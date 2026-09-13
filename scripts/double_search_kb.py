#!/usr/bin/env python3
"""Run SQLite FTS and an independent canonical-file scan, then merge with RRF."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from canonical_search import search_canonical
from kb_search import compact_result, search, tokenize


EXPANSIONS = [
    (r"hardship|financial difficulty|payment plan", "hardship payment difficulty capacity to pay NERL NERR"),
    (r"life support|medical equipment", "life support registration distributor notification information pack deregistration"),
    (r"disconnect|de-energ", "disconnection de-energisation hardship notice protected customer"),
    (r"consent|switch|transfer", "explicit informed consent EIC customer transfer NERL"),
    (r"centrepay|overcharg|closed account", "Centrepay billing overcharging rule 31 AGL Full Court quashed appeal"),
    (r"family violence|domestic violence", "family violence protected information safe contact debt collection"),
    (r"bid|rebid|good faith", "bidding rebidding false misleading 3.8.22 3.8.22A superseded"),
    (r"dispatch", "dispatch instruction 4.9.8 AEMO participant"),
    (r"fcas|frequency", "FCAS ancillary service enablement capability dispatch"),
    (r"performance standard|protection setting|ride.through", "generator performance standards GPS 4.15 Schedule 5.2 approved settings"),
    (r"availability|pasa|capacity", "PASA availability information 3.7.3 3.13.2"),
    (r"meter", "metering metrology NMI Chapter 7 smart meter"),
    (r"electrical[- ]safety|electrocution|electrician|wiring rules", "electrical safety Electrical Safety Act 2002"),
    (r"appeal|first.instance|first instance", "appeal first instance final penalty controlling outcome"),
    (r"telemarket|spam|do not call", "Do Not Call Register Spam Act telemarketing consent unsubscribe"),
    (r"victoria|\bvic\b|esc", "Victoria ESC Energy Retail Code of Practice payment difficulty"),
    (r"western australia|\bwa\b|wem", "Western Australia WEM ERA Wholesale Electricity Market Rules"),
    (r"work health|worksafe|workplace|worker", "WHS OHS prosecution electrical hazard workplace"),
]


def expanded_query(query: str) -> str:
    additions = []
    for pattern, expansion in EXPANSIONS:
        if re.search(pattern, query, re.I):
            additions.append(expansion)
    # Search B is deliberately issue-oriented and does not copy the full Search A phrase.
    core = " ".join(re.findall(r"\b(?:19|20)\d{2}\b|\b[A-Z][A-Za-z0-9&.-]{2,}\b", query))
    value = " ".join([core, *additions]).strip()
    return value if value and tokenize(value) else query


def reciprocal_rank_fusion(result_sets: list[list[dict]], limit: int, rank_constant: int = 60) -> list[dict]:
    scores: dict[str, float] = {}
    rows: dict[str, dict] = {}
    provenance: dict[str, list[dict]] = {}
    for search_index, result_set in enumerate(result_sets, 1):
        for rank, row in enumerate(result_set, 1):
            evidence_id = row["evidence_id"]
            scores[evidence_id] = scores.get(evidence_id, 0.0) + 1.0 / (rank_constant + rank)
            rows[evidence_id] = row
            provenance.setdefault(evidence_id, []).append({
                "search": search_index,
                "engine": row.get("retrieval_engine", "sqlite-fts5"),
                "rank": rank,
                "query": row["retrieval_query"],
            })
    ordered = sorted(scores, key=lambda item: (-scores[item], -rows[item]["authority_rank"], item))[:limit]
    merged = []
    for rank, evidence_id in enumerate(ordered, 1):
        row = dict(rows[evidence_id])
        row["rrf_score"] = scores[evidence_id]
        row["rrf_rank"] = rank
        row["retrieval_provenance"] = provenance[evidence_id]
        merged.append(row)
    return merged


def double_search(
    database: Path,
    query: str,
    *,
    jurisdiction: str | None = None,
    issue_family: str | None = None,
    doc_type: str | None = None,
    as_of: str | None = None,
    limit: int = 15,
) -> tuple[str, list[dict], list[list[dict]]]:
    query_b = expanded_query(query)
    # Keep the candidate pool stable for normal answer and audit result sizes.
    # A limit-dependent shallow pool can make an item move into the top results
    # merely because the caller asked for more output.
    window = max(limit * 4, 160)
    result_a = search(
        database, query, jurisdiction=jurisdiction, issue_family=issue_family,
        doc_type=doc_type, as_of=as_of, limit=window,
    )
    for row in result_a:
        row["retrieval_engine"] = "sqlite-fts5"
    root = database.resolve().parent.parent
    result_b = search_canonical(
        root, f"{query} {query_b}", jurisdiction=jurisdiction,
        issue_family=issue_family, doc_type=doc_type, as_of=as_of, limit=window,
    )
    return query_b, reciprocal_rank_fusion([result_a, result_b], limit), [result_a, result_b]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--database", type=Path)
    parser.add_argument("--jurisdiction")
    parser.add_argument("--issue-family")
    parser.add_argument("--doc-type")
    parser.add_argument("--as-of", default="2026-08-29")
    parser.add_argument("--limit", type=int, default=15)
    args = parser.parse_args()
    database = args.database or args.root / "data" / "search-index.sqlite3"
    query_b, merged, raw = double_search(
        database, args.query, jurisdiction=args.jurisdiction,
        issue_family=args.issue_family, doc_type=args.doc_type, as_of=args.as_of, limit=args.limit,
    )
    print(json.dumps({
        "method": "sqlite-fts5-plus-independent-canonical-scan-with-reciprocal-rank-fusion",
        "query_a": args.query,
        "query_b": query_b,
        "as_of": args.as_of,
        "raw_result_counts": [len(item) for item in raw],
        "result_count": len(merged),
        "results": [{**compact_result(row), "rrf_score": row["rrf_score"], "rrf_rank": row["rrf_rank"], "retrieval_provenance": row["retrieval_provenance"]} for row in merged],
    }, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
