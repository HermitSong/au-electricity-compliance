#!/usr/bin/env python3
"""Merge and validate four independent v5 audit shards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SCORECARD_FIELDS = {
    "jurisdiction_and_scope",
    "temporal_applicability",
    "legal_and_procedural_status",
    "operational_control",
    "evidence_and_uncertainty",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", default="round1", help="Grade shard label, for example round1, round2 or final")
    parser.add_argument("--output", type=Path, help="Optional merged JSONL output path")
    args = parser.parse_args()
    if not args.round.replace("-", "").replace("_", "").isalnum():
        raise ValueError("--round must be an alphanumeric label")
    root = Path(__file__).resolve().parents[1]
    result_dir = root / "review" / "results"
    rows = []
    for part in range(1, 5):
        path = result_dir / f"case-loop-v5-grades-{args.round}-part{part}.jsonl"
        part_rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        if len(part_rows) != 25:
            raise ValueError(f"{path.name} must contain exactly 25 rows, found {len(part_rows)}")
        rows.extend(part_rows)
    expected_ids = [f"AUPRO-{number:03d}" for number in range(1, 101)]
    if [str(row.get("id", "")) for row in rows] != expected_ids:
        raise ValueError("Merged grade IDs are not exactly AUPRO-001 through AUPRO-100 in order")
    for row in rows:
        scorecard = row.get("scorecard")
        if not isinstance(scorecard, dict) or set(scorecard) != SCORECARD_FIELDS:
            raise ValueError(f"{row['id']}: malformed five-dimension scorecard")
        points = sum(value is True for value in scorecard.values())
        if row.get("points_total") != 5 or row.get("points_hit") != points:
            raise ValueError(f"{row['id']}: points do not match scorecard")
        expected_grade = "pass" if points == 5 and not row.get("critical_error") else ("fail" if row.get("critical_error") else "partial")
        if row.get("grade") != expected_grade:
            raise ValueError(f"{row['id']}: grade must be {expected_grade}")
    output = args.output or result_dir / f"case-loop-v5-grades-{args.round}.jsonl"
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )
    print(f"Merged {len(rows)} {args.round} grades into {output}")
    print(f"Pass: {sum(row['grade'] == 'pass' for row in rows)}")
    print(f"Partial: {sum(row['grade'] == 'partial' for row in rows)}")
    print(f"Fail: {sum(row['grade'] == 'fail' for row in rows)}")
    print(f"Points: {sum(row['points_hit'] for row in rows)}/500")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
