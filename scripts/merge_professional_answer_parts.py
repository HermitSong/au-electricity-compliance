#!/usr/bin/env python3
"""Merge four independently written v5 blind-answer shards."""

from __future__ import annotations

import json
from pathlib import Path
import re


CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result_dir = root / "review" / "results"
    rows = []
    for part in range(1, 5):
        path = result_dir / f"case-loop-v5-answers-part{part}.jsonl"
        part_rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        if len(part_rows) != 25:
            raise ValueError(f"{path.name} must contain exactly 25 rows, found {len(part_rows)}")
        rows.extend(part_rows)
    expected_ids = [f"AUPRO-{number:03d}" for number in range(1, 101)]
    actual_ids = [str(row.get("id", "")) for row in rows]
    if actual_ids != expected_ids:
        raise ValueError("Merged answer IDs are not exactly AUPRO-001 through AUPRO-100 in order")
    rendered = "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows)
    if CJK_RE.search(rendered):
        raise ValueError("Merged answers contain Han characters")
    output = result_dir / "case-loop-v5-answers.jsonl"
    output.write_text(rendered, encoding="utf-8")
    print(f"Merged {len(rows)} blind answers into {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
