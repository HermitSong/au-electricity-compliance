#!/usr/bin/env python3
"""Independent in-memory search over canonical files, without the SQLite index."""

from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path

from build_search_index import build_documents
from kb_search import applicable_as_of, compact_result, tokenize


@lru_cache(maxsize=4)
def canonical_documents(root_text: str) -> tuple[dict, ...]:
    root = Path(root_text)
    rows = []
    for item in build_documents(root):
        row = dict(item)
        metadata_json = json.dumps(row["metadata"], ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        row["sha256"] = hashlib.sha256("\n".join((row["title"], row["body"], metadata_json)).encode("utf-8")).hexdigest()
        rows.append(row)
    return tuple(rows)


def score(row: dict, query: str, tokens: list[str]) -> float:
    phrase = query.lower().strip()
    fields = (
        (str(row["title"]).lower(), 5.0),
        (str(row["entity"]).lower(), 5.0),
        (str(row["instrument"]).lower(), 3.5),
        (str(row["issue_family"]).lower(), 3.0),
        (str(row["evidence_id"]).lower(), 2.5),
        (str(row["body"]).lower(), 1.0),
    )
    value = 0.0
    if phrase and len(phrase) > 3:
        for text, weight in fields:
            if phrase in text:
                value += 10.0 * weight
    matched = set()
    for token in tokens:
        token_total = 0.0
        for text, weight in fields:
            count = min(text.count(token), 5)
            token_total += count * weight
        if token_total:
            matched.add(token)
            value += token_total
    if tokens:
        value += 15.0 * len(matched) / len(tokens)
    value += row["authority_rank"] / 1000.0
    return value


def search_canonical(
    root: Path,
    query: str,
    *,
    jurisdiction: str | None = None,
    issue_family: str | None = None,
    doc_type: str | None = None,
    as_of: str | None = None,
    limit: int = 40,
) -> list[dict]:
    tokens = tokenize(query)
    if not tokens:
        raise ValueError("Query has no searchable terms")
    scored = []
    for source in canonical_documents(str(root.resolve())):
        row = dict(source)
        if jurisdiction and jurisdiction.lower() not in row["jurisdiction"].lower():
            continue
        if issue_family and issue_family not in row["issue_families"]:
            continue
        if doc_type and row["doc_type"] != doc_type:
            continue
        if not applicable_as_of(row, as_of):
            continue
        value = score(row, query, tokens)
        if value <= row["authority_rank"] / 1000.0:
            continue
        row["lexical_score"] = -value
        row["retrieval_query"] = query
        row["retrieval_expression"] = "canonical-token-and-phrase-scan"
        row["retrieval_engine"] = "canonical-json-memory-scan"
        scored.append(row)
    scored.sort(key=lambda item: (item["lexical_score"], -item["authority_rank"], item["evidence_id"]))
    return scored[:limit]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--jurisdiction")
    parser.add_argument("--issue-family")
    parser.add_argument("--doc-type")
    parser.add_argument("--as-of")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    rows = search_canonical(
        args.root.resolve(), args.query, jurisdiction=args.jurisdiction,
        issue_family=args.issue_family, doc_type=args.doc_type, as_of=args.as_of, limit=args.limit,
    )
    print(json.dumps({
        "method": "canonical-json-memory-scan",
        "query": args.query,
        "result_count": len(rows),
        "results": [compact_result(row) for row in rows],
    }, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
