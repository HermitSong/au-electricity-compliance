#!/usr/bin/env python3
"""Search the local canonical-derived FTS index and emit an evidence list."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_search import compact_result, search


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--database", type=Path)
    parser.add_argument("--jurisdiction")
    parser.add_argument("--issue-family")
    parser.add_argument("--doc-type")
    parser.add_argument("--as-of")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args()
    database = args.database or args.root / "data" / "search-index.sqlite3"
    rows = search(
        database, args.query, jurisdiction=args.jurisdiction, issue_family=args.issue_family,
        doc_type=args.doc_type, as_of=args.as_of, limit=args.limit,
    )
    print(json.dumps({
        "query": args.query,
        "as_of": args.as_of,
        "filters": {"jurisdiction": args.jurisdiction, "issue_family": args.issue_family, "doc_type": args.doc_type},
        "result_count": len(rows),
        "results": [compact_result(row) for row in rows],
    }, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
