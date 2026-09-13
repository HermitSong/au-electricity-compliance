#!/usr/bin/env python3
"""Synchronise reviewed coverage gaps into staging coverage and the source register."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> int:
    overrides = load(ROOT / "data" / "source-coverage-status-overrides.json")["overrides"]
    reviews: dict[str, dict] = {}
    changed_files = []
    for coverage_path in sorted((ROOT / "staging-full").glob("*/coverage.json")):
        document = load(coverage_path)
        changed = False
        for review in document["source_reviews"]:
            source_id = review["source_family_id"]
            reviews[source_id] = review
            if source_id in overrides:
                for field, value in overrides[source_id].items():
                    if review.get(field) != value:
                        review[field] = value
                        changed = True
        if changed:
            write(coverage_path, document)
            changed_files.append(str(coverage_path.relative_to(ROOT)))

    missing = sorted(set(overrides) - set(reviews))
    if missing:
        raise ValueError(f"Coverage overrides reference unknown reviews: {missing}")

    register_path = ROOT / "data" / "enforcement-source-register.json"
    register = load(register_path)
    for source in register["sources"]:
        review = reviews.get(source["id"])
        if not review:
            continue
        source["gap_periods"] = review["gap_periods"]
        if source["id"] in overrides:
            source["completeness_level"] = "archive-gap"
            source["limitation"] = review["gap_reason"]
    register["baseline_date"] = "2026-08-29"
    write(register_path, register)
    changed_files.append(str(register_path.relative_to(ROOT)))
    print(json.dumps({"changed_files": changed_files, "overridden_sources": sorted(overrides)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
