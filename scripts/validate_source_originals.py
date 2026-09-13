#!/usr/bin/env python3
"""Validate original byte provenance; never certify legal completeness."""

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3

from collect_source_originals import select_manifest_rows


ARTIFACTS = (("snapshot_path", "sha256"), ("text_path", "text_sha256"),
             ("screenshot_path", "screenshot_sha256"), ("raw_response_path", "raw_response_sha256"),
             ("embedded_record_path", "embedded_record_sha256"), ("ocr_pages_path", "ocr_pages_sha256"),
             ("alternative_text_path", "alternative_text_sha256"), ("ocr_comparison_path", "ocr_comparison_sha256"),
             ("image_path", "image_sha256"), ("tesseract_word_boxes_path", "tesseract_word_boxes_sha256"))


def check_artifacts(root, row, checked, errors):
    for path_key, hash_key in ARTIFACTS:
        if path_key not in row and hash_key not in row:
            continue
        relative, digest = row.get(path_key), row.get(hash_key)
        if not relative or not digest:
            errors.append(f"Missing artifact provenance: {path_key}")
            continue
        path = (root / relative).resolve()
        if not path.is_relative_to((root / 'source-originals/objects').resolve()):
            errors.append(f"Object path escapes original archive: {relative}")
            continue
        if (relative, digest) in checked:
            continue
        checked.add((relative, digest))
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            errors.append(f"Missing or corrupt source object: {relative}")
            continue
        if path_key in {'text_path', 'alternative_text_path', 'ocr_pages_path', 'ocr_comparison_path'}:
            try:
                content = json.loads(path.read_bytes())
                if not isinstance(content, list):
                    raise ValueError('Expected list')
                if path_key in {'text_path', 'alternative_text_path'}:
                    if not all(isinstance(unit, dict) and isinstance(unit.get('text'), str) and unit.get('locator') for unit in content):
                        raise ValueError('Invalid text/locator representation')
                    if len({u['locator'] for u in content}) != len(content):
                        raise ValueError('Duplicate text locators')
                else:
                    if [page['page'] for page in content] != list(range(1, row['page_count'] + 1)):
                        raise ValueError('OCR evidence does not cover every page in sequence')
                    for page in content:
                        check_artifacts(root, page, checked, errors)
            except (ValueError, KeyError, TypeError) as exc:
                errors.append(f"Invalid structured evidence: {relative}: {exc}")


def validate(root: Path) -> dict:
    errors = []
    checked = set()
    manifest = root / "source-originals" / "manifest.jsonl"
    rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    _, preserved = select_manifest_rows(rows)
    for row in rows:
        if row.get("current_law_release") is not False or row.get("legal_review_status") != "not-reviewed":
            errors.append("Acquisition records must not silently grant current-law release")
        if row.get("capture_status") not in {"bytes-preserved", "browser-text-preserved"}:
            continue
        if not row.get('snapshot_path') or not row.get('sha256'):
            errors.append(f"Missing primary artifact: {row['canonical_url']}")
        check_artifacts(root, row, checked, errors)
    # Include retained alternate and superseded captures, not just the preferred index copy.
    recovery_count = 0
    for log in (root / 'source-originals').glob('recovery-*.jsonl'):
        for line in log.read_text(encoding='utf-8-sig').splitlines():
            if line.strip():
                check_artifacts(root, json.loads(line), checked, errors)
                recovery_count += 1
    expected = {}
    if not errors:
        for url, row in preserved.items():
            for unit in json.loads((root / row["text_path"]).read_bytes()):
                key = (url, unit["locator"])
                expected[key] = (hashlib.sha256(unit["text"].encode("utf-8")).hexdigest(), row["sha256"],
                                 row["snapshot_path"], row["text_path"], row["text_sha256"])
    database = root / "source-originals" / "search.sqlite3"
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            errors.append(f"Original search database integrity: {integrity}")
        units = connection.execute("SELECT COUNT(*) FROM originals").fetchone()[0]
        unsafe = connection.execute("SELECT COUNT(*) FROM originals WHERE review_status != ?", ("research-only; not legal clearance",)).fetchone()[0]
        if unsafe:
            errors.append("Original search contains records without the research-only boundary")
        if not errors:
            for url, locator, text, digest, source_path, text_path, text_digest in connection.execute(
                    "SELECT url,locator,text,sha256,snapshot_path,text_path,text_sha256 FROM originals"):
                actual = (hashlib.sha256(text.encode("utf-8")).hexdigest(), digest, source_path, text_path, text_digest)
                if expected.pop((url, locator), None) != actual:
                    errors.append(f"Search text/provenance does not match preserved source extraction: {url} {locator}")
            if expected:
                errors.append(f"Search index omits {len(expected)} preserved text units")
    return {"passed": not errors, "manifest_outcomes_checked": len(rows), "recovery_outcomes_checked": recovery_count, "distinct_objects_checked": len(checked),
            "search_units_checked": units, "errors": errors,
            "scope": "Byte identity, path containment, text locators, search-to-extraction fidelity and research-only boundary. Not legal accuracy or corpus completeness."}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(args.root.resolve())
    rendered = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
