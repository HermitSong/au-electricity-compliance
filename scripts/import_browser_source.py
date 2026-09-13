#!/usr/bin/env python3
"""Import a checked browser text transfer without claiming original HTTP bytes."""

import argparse
import json
from pathlib import Path

from collect_source_originals import now, read_jsonl, save_object


def transfer_fingerprint(text: str) -> tuple[int, str]:
    data = text.encode("utf-16-le")
    value = 2166136261
    for index in range(0, len(data), 2):
        unit = data[index] | data[index + 1] << 8
        value = ((value ^ unit) * 16777619) & 0xffffffff
    return len(data) // 2, f"{value:08x}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("descriptor", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    descriptor = json.loads(args.descriptor.read_text(encoding="utf-8"))
    text_path = (args.descriptor.parent / descriptor["text_file"]).resolve()
    if not text_path.is_relative_to(args.descriptor.parent.resolve()):
        raise ValueError("Browser transfer path must stay inside its input directory")
    text = text_path.read_text(encoding="utf-8").rstrip("\n")
    length, fingerprint = transfer_fingerprint(text)
    if (length, fingerprint) != (descriptor["character_count"], descriptor["transfer_fnv1a32"]):
        raise ValueError(f"Browser transfer mismatch: length={length}, fingerprint={fingerprint}")
    if args.check_only:
        print(json.dumps({"transfer_checked": True, "character_count": length, "fnv1a32": fingerprint}))
        return 0
    root = args.root.resolve()
    existing = read_jsonl(root / "source-originals" / "manifest.jsonl")
    if any(row.get("browser_capture_time") == descriptor["captured_at"] and row["canonical_url"] == descriptor["canonical_url"] for row in existing):
        print("Browser capture already imported")
        return 0
    previous = next((row for row in reversed(existing) if row["canonical_url"] == descriptor["canonical_url"]), None)
    if not previous:
        raise ValueError("Browser source must already be registered in the acquisition manifest")
    snapshot_path, digest = save_object(root, text.encode("utf-8"), ".txt")
    units = [{"locator": "browser:" + descriptor["selector"], "text": text}]
    derived_path, derived_digest = save_object(root, (json.dumps(units, ensure_ascii=True, indent=2) + "\n").encode("utf-8"), ".json")
    row = {key: previous[key] for key in ("canonical_url", "references", "source_family_ids", "discovery_depth", "discovered_from")}
    row.update({"capture_status": "browser-text-preserved", "acquisition_method": "browser-rendered-main-text",
                "representation": descriptor["representation"], "title": descriptor["title"],
                "attempted_at": descriptor["captured_at"], "retrieved_at": descriptor["captured_at"],
                "browser_capture_time": descriptor["captured_at"], "imported_at": now(),
                "snapshot_path": snapshot_path, "sha256": digest, "size_bytes": len(text.encode("utf-8")),
                "content_type": "text/plain; charset=utf-8", "text_path": derived_path,
                "text_sha256": derived_digest, "text_character_count": length,
                "extraction_status": "extracted-unreviewed", "content_class": "browser-rendered-main-text",
                "browser_capture_provenance": descriptor, "legal_review_status": "not-reviewed",
                "current_law_release": False, "redistribution_status": "not-cleared", "links": []})
    with (root / "source-originals" / "manifest.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(json.dumps({"imported": True, "canonical_url": row["canonical_url"], "representation": row["representation"], "sha256": digest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
