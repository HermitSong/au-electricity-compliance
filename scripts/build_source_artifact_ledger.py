#!/usr/bin/env python3
"""Build a truthful provenance ledger for local snapshots and remote-only sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
from collections import defaultdict
from pathlib import Path


BASELINE_DATE = "2026-08-29"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def sha256_bytes(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}:{hashlib.sha256(value.encode('utf-8')).hexdigest()[:24]}"


def parse_snapshot_manifest(root: Path) -> dict[str, str]:
    manifest = root / "official-documents" / "SOURCES.md"
    mappings: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^\|\s*`([^`]+)`\s*\|\s*(https://[^|\s]+)\s*\|", line)
        if match:
            mappings[match.group(1)] = match.group(2)
    return mappings


def read_capture_manifest(root: Path) -> list[dict]:
    path = root / "official-snapshots" / "manifest.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def collect_canonical_urls(root: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    references: dict[str, set[str]] = defaultdict(set)
    source_families: dict[str, set[str]] = defaultdict(set)

    for filename in ("enforcement-events-full.jsonl", "technical-events-full.jsonl"):
        for event in read_jsonl(root / "data" / filename):
            url = event["official_source_url"]
            references[url].add(f"event:{event['event_id']}")
            source_families[url].add(event["source_family_id"])

    source_register = read_json(root / "data" / "enforcement-source-register.json")
    for source in source_register["sources"]:
        url = source["url"]
        references[url].add(f"source-family:{source['id']}")
        source_families[url].add(source["id"])

    coverage = read_json(root / "data" / "source-coverage-ledger.json")
    for review in coverage["source_reviews"]:
        url = review["source_url"]
        references[url].add(f"coverage-review:{review['source_family_id']}")
        source_families[url].add(review["source_family_id"])

    provisions = read_json(root / "data" / "provision-version-register.json")
    for provision in provisions["provisions"]:
        url = provision["official_url"]
        references[url].add(f"provision:{provision['provision_id']}")

    return references, source_families


def build_ledger(root: Path) -> tuple[list[dict], dict]:
    manifest_urls = parse_snapshot_manifest(root)
    references, source_families = collect_canonical_urls(root)
    rows: list[dict] = []
    snapshotted_urls: set[str] = set()
    documents_root = root / "official-documents"

    for path in sorted(item for item in documents_root.rglob("*") if item.is_file() and item.name != "SOURCES.md"):
        relative = path.relative_to(root).as_posix()
        url = manifest_urls.get(path.name)
        if url:
            snapshotted_urls.add(url)
        retrieved_at = "2026-08" if relative.startswith("official-documents/domain-documents/") else None
        metadata_complete = bool(url and retrieved_at)
        rows.append({
            "artifact_id": stable_id("artifact", relative),
            "record_type": "local-official-snapshot",
            "canonical_url": url,
            "snapshot_path": relative,
            "snapshot_status": "bundled-immutable-copy",
            "sha256": sha256_bytes(path),
            "size_bytes": path.stat().st_size,
            "mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            "retrieved_at": retrieved_at,
            "retrieval_time_precision": "month" if retrieved_at else None,
            "source_family_ids": sorted(source_families.get(url, set())) if url else [],
            "canonical_record_references": sorted(references.get(url, set())) if url else [],
            "provenance_status": "byte-verified-metadata-complete" if metadata_complete else "byte-verified-metadata-incomplete",
            "provenance_limitations": [] if metadata_complete else [
                item for item, present in (
                    ("Canonical source URL was not recorded when the file was acquired.", bool(url)),
                    ("Exact retrieval timestamp was not recorded when the file was acquired.", bool(retrieved_at)),
                ) if not present
            ],
            "ledger_baseline": BASELINE_DATE,
        })

    for capture in read_capture_manifest(root):
        if capture.get("capture_status") != "captured":
            continue
        path = root / capture["snapshot_path"]
        if not path.is_file():
            continue
        url = capture["canonical_url"]
        snapshotted_urls.add(url)
        rows.append({
            "artifact_id": capture["capture_id"],
            "record_type": "local-official-snapshot",
            "canonical_url": url,
            "snapshot_path": capture["snapshot_path"],
            "snapshot_status": "captured-immutable-copy",
            "sha256": capture["sha256"],
            "size_bytes": capture["size_bytes"],
            "mime_type": capture["content_type"].split(";", 1)[0],
            "retrieved_at": capture["retrieved_at"],
            "retrieval_time_precision": "timestamp",
            "response_url": capture["response_url"],
            "response_status_code": capture["status_code"],
            "response_headers": capture["response_headers"],
            "source_family_ids": sorted(source_families.get(url, set())),
            "canonical_record_references": sorted(references.get(url, set())),
            "provenance_status": "byte-verified-metadata-complete",
            "provenance_limitations": [],
            "ledger_baseline": BASELINE_DATE,
        })

    for url in sorted(references):
        if url in snapshotted_urls:
            continue
        rows.append({
            "artifact_id": stable_id("remote", url),
            "record_type": "remote-official-source",
            "canonical_url": url,
            "snapshot_path": None,
            "snapshot_status": "remote-only-no-snapshot",
            "sha256": None,
            "size_bytes": None,
            "mime_type": None,
            "retrieved_at": None,
            "retrieval_time_precision": None,
            "source_family_ids": sorted(source_families.get(url, set())),
            "canonical_record_references": sorted(references[url]),
            "provenance_status": "not-locally-reproducible",
            "provenance_limitations": [
                "No immutable local source snapshot is bound to this URL.",
                "The live page may change or disappear after the canonical record was created.",
            ],
            "ledger_baseline": BASELINE_DATE,
        })

    rows.sort(key=lambda item: (item["record_type"], item["snapshot_path"] or item["canonical_url"] or ""))
    summary = {
        "schema_version": "1.0",
        "baseline_date": BASELINE_DATE,
        "artifact_count": len(rows),
        "local_snapshot_count": sum(row["record_type"] == "local-official-snapshot" for row in rows),
        "local_snapshot_with_url_count": sum(
            row["record_type"] == "local-official-snapshot" and bool(row["canonical_url"])
            for row in rows
        ),
        "metadata_incomplete_snapshot_count": sum(
            row["record_type"] == "local-official-snapshot" and row["provenance_status"].endswith("metadata-incomplete")
            for row in rows
        ),
        "remote_only_source_count": sum(row["record_type"] == "remote-official-source" for row in rows),
        "canonical_url_count": len(references),
        "canonical_url_ledger_coverage_count": len({row["canonical_url"] for row in rows if row["canonical_url"] in references}),
        "reproducibility_status": "partial-local-snapshots-remote-only-sources-remain",
        "interpretation": "A URL or generated search-index hash is not an immutable official-source snapshot. Remote-only records require live verification or later source capture.",
    }
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "data" / "source-artifact-ledger.jsonl"
    summary_path = args.summary or root / "data" / "source-artifact-summary.json"
    rows, summary = build_ledger(root)
    output.write_text(
        "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} source-artifact records to {output}")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
