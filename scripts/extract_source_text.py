#!/usr/bin/env python3
"""Extract addressable text chunks from the latest captured official sources."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import hashlib
import io
import json
from pathlib import Path
import re

from pypdf import PdfReader


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)


def read_manifest(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def latest_captures(rows: list[dict]) -> list[dict]:
    latest: dict[str, dict] = {}
    for row in rows:
        if row.get("capture_status") != "captured":
            continue
        current = latest.get(row["canonical_url"])
        if current is None or row["retrieved_at"] > current["retrieved_at"]:
            latest[row["canonical_url"]] = row
    return [latest[url] for url in sorted(latest)]


def normalise(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[\t\r\f\v]+", " ", text)
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def split_text(text: str, chunk_size: int = 5000, overlap: int = 500) -> list[tuple[int, int, str]]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        if end < len(text):
            boundary = max(text.rfind("\n", start + chunk_size // 2, end), text.rfind(". ", start + chunk_size // 2, end))
            if boundary > start:
                end = boundary + 1
        value = text[start:end].strip()
        if value:
            chunks.append((start, end, value))
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def extracted_units(path: Path, content_type: str) -> tuple[list[tuple[str, str]], str | None]:
    base_type = content_type.split(";", 1)[0].lower()
    data = path.read_bytes()
    if base_type == "application/pdf" or path.suffix.lower() == ".pdf":
        reader = PdfReader(io.BytesIO(data))
        units = []
        for page_number, page in enumerate(reader.pages, 1):
            text = normalise(page.extract_text() or "")
            if text:
                units.append((f"page:{page_number}", text))
        return units, None if units else "PDF contains no extractable text; OCR or a replacement source is required."
    if base_type in {"text/html", "application/xhtml+xml"} or path.suffix.lower() in {".html", ".htm"}:
        parser = VisibleTextParser()
        parser.feed(data.decode("utf-8", errors="replace"))
        text = normalise("\n".join(parser.parts))
        return ([('html-visible-text', text)] if text else []), (None if text else "HTML contains no visible text.")
    if base_type.startswith("text/") or base_type == "application/json" or path.suffix.lower() in {".txt", ".json"}:
        text = normalise(data.decode("utf-8", errors="replace"))
        return ([('document-text', text)] if text else []), (None if text else "Document contains no extractable text.")
    return [], f"Unsupported content type: {content_type}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = root / "official-snapshots" / "manifest.jsonl"
    output = args.output or root / "data" / "source-text-chunks.jsonl"
    rows = []
    failures = []
    for capture in latest_captures(read_manifest(manifest)):
        path = root / capture["snapshot_path"]
        try:
            units, error = extracted_units(path, capture["content_type"])
        except Exception as exc:
            units, error = [], f"{type(exc).__name__}: {exc}"
        if error:
            failures.append({"canonical_url": capture["canonical_url"], "snapshot_path": capture["snapshot_path"], "error": error})
        for locator, text in units:
            for index, (start, end, value) in enumerate(split_text(text), 1):
                identity = f"{capture['sha256']}|{locator}|{start}|{end}"
                rows.append({
                    "chunk_id": hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32],
                    "artifact_id": capture["capture_id"],
                    "canonical_url": capture["canonical_url"],
                    "parent_canonical_url": capture.get("parent_canonical_url"),
                    "snapshot_path": capture["snapshot_path"],
                    "source_sha256": capture["sha256"],
                    "retrieved_at": capture["retrieved_at"],
                    "content_type": capture["content_type"],
                    "locator": locator,
                    "chunk_index": index,
                    "character_start": start,
                    "character_end": end,
                    "text_sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
                    "text": value,
                })
    output.write_text(
        "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    summary = {
        "schema_version": "1.0",
        "captured_source_count": len(latest_captures(read_manifest(manifest))),
        "source_with_extracted_text_count": len({row["canonical_url"] for row in rows}),
        "chunk_count": len(rows),
        "extraction_failure_count": len(failures),
        "failures": failures,
    }
    (root / "data" / "source-text-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
