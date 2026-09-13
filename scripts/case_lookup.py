#!/usr/bin/env python3
"""Filter and cite historical electricity compliance cases from canonical records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from answer_kb import source_artifact_lookup
from case_chains import load_research_chains


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def contains(value: str, needle: str | None) -> bool:
    return not needle or needle.lower() in value.lower()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--query")
    parser.add_argument("--entity")
    parser.add_argument("--jurisdiction")
    parser.add_argument("--issue-family")
    parser.add_argument("--source-family")
    parser.add_argument("--status")
    parser.add_argument("--from-date")
    parser.add_argument("--to-date")
    parser.add_argument("--current-comparator")
    parser.add_argument("--oldest-first", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    links = {row["event_id"]: row for row in read_jsonl(root / "data" / "event-provision-links.jsonl")}
    artifacts = source_artifact_lookup(root)
    chains, chains_by_event = load_research_chains(root)
    events = []
    for filename in ("enforcement-events-full.jsonl", "technical-events-full.jsonl"):
        events.extend(read_jsonl(root / "data" / filename))
    results = []
    for event in events:
        link = links[event["event_id"]]
        searchable = " ".join(str(event.get(field, "")) for field in (
            "event_id", "entity", "issue", "outcome", "instrument_or_rule", "source_title",
        ))
        if not contains(searchable, args.query):
            continue
        if not contains(event["entity"], args.entity):
            continue
        if not contains(event["jurisdiction"], args.jurisdiction):
            continue
        if args.issue_family and args.issue_family not in link["issue_families"]:
            continue
        if args.source_family and event["source_family_id"] != args.source_family:
            continue
        if not contains(event["status"], args.status):
            continue
        if args.from_date and event["event_date"] < args.from_date:
            continue
        if args.to_date and event["event_date"] > args.to_date:
            continue
        if args.current_comparator and args.current_comparator not in link["current_comparator_ids"]:
            continue
        results.append({
            "event_id": event["event_id"],
            "event_date": event["event_date"],
            "publication_date": event["publication_date"],
            "entity": event["entity"],
            "jurisdiction": event["jurisdiction"],
            "event_type": event["event_type"],
            "status": event["status"],
            "issue": event["issue"],
            "outcome": event["outcome"],
            "historical_instrument_or_rule": event["instrument_or_rule"],
            "case_status_note": event["case_status_note"],
            "official_source_url": event["official_source_url"],
            "source_artifact": artifacts.get(event["official_source_url"], {
                "snapshot_status": "not-recorded-in-source-artifact-ledger",
                "provenance_status": "unverified",
            }),
            "issue_families": link["issue_families"],
            "temporal_classification": link["temporal_classification"],
            "conflict_flag": link["conflict_flag"],
            "current_comparator_ids": link["current_comparator_ids"],
            "current_mapping_status": link["current_mapping_status"],
            "temporal_link_review_status": link["review_status"],
            "research_case_chain_ids": chains_by_event.get(event["event_id"], []),
        })
    results.sort(key=lambda item: (item["event_date"], item["event_id"]), reverse=not args.oldest_first)
    results = results[: args.limit]
    payload = {
        "schema_version": "1.0",
        "filters": {
            "query": args.query, "entity": args.entity, "jurisdiction": args.jurisdiction,
            "issue_family": args.issue_family, "source_family": args.source_family,
            "status": args.status, "from_date": args.from_date, "to_date": args.to_date,
            "current_comparator": args.current_comparator,
        },
        "result_count": len(results),
        "temporal_warning": "Historical cases describe the source-time position. Candidate current-comparator links do not establish present law.",
        "results": results,
        "research_case_chains": {identity: chains[identity] for identity in sorted({
            identity for result in results for identity in result['research_case_chain_ids']})},
        "case_chain_use_limit": "Evidence-bound research chronology, not an approved current-law answer. Event-time posture differs from later case disposition; unresolved filings and source conflicts remain open.",
    }
    rendered = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {len(results)} cases to {args.output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
