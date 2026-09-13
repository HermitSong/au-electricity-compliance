#!/usr/bin/env python3
"""Build frozen double-search packets and retrieval metrics for the v5 benchmark."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from answer_kb import LOCAL_SNAPSHOT_STATUSES, expand_temporal_comparators, relevant_gaps, source_artifact_lookup
from double_search_kb import double_search
from kb_search import compact_result


JURISDICTION_FILTERS = {
    "ACT": "Australian Capital Territory",
    "NSW": "New South Wales",
    "NT": "Northern Territory",
    "QLD": "Queensland",
    "SA": "South Australia",
    "TAS": "Tasmania",
    "VIC": "Victoria",
    "WA": "Western Australia",
    "National/Cross-jurisdiction": None,
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def route_mode(row: dict) -> str:
    angle = str(row.get("angle", "")).lower()
    exact_modes = {
        "coverage-gap": {
            "bot-protected-archive-gap", "protected-information-aggregate-only",
            "documented-four-year-gap", "pdf-extraction-backlog", "six-year-rolling-window",
        },
        "insufficient-evidence": {
            "official-source-insufficient", "investigation-no-outcome-amount",
        },
        "procedural-status-conflict": {
            "proceedings-allegations-only", "stay-and-discontinued-challenges",
            "private-disputes-aggregate-only", "incident-to-undertaking-chronology",
            "paired-undertakings-no-conviction", "accepted-undertaking-with-variations",
            "unnamed-technical-event", "outside-control-technical-finding",
            "technical-cause-not-prosecution", "tree-failure-no-breach-finding",
            "portfolio-technical-report", "determination-disputed-review-board",
        },
        "needs-live-verification": {
            "historical-control-current-law", "historical-case-current-authorisation",
            "legacy-undertaking-current-claims", "appeal-controls-repealed-law",
            "former-statute-current-control", "historical-clause-current-process",
            "active-public-register-order", "warning-not-conviction-current-status",
            "historical-environment-law-current-controls", "historical-audit-current-obligation",
        },
        "historical-only": {
            "repealed-order-not-erased-history", "old-regulation-current-control",
            "company-and-director-separate-charges", "no-customers-not-a-defence",
        },
    }
    for mode, angles in exact_modes.items():
        if angle in angles:
            return mode
    text = " ".join(
        str(row.get(field, "")) for field in ("scenario_type", "angle", "question")
    ).lower()
    if re.search(r"\b(exhaustive|archive gap|all public records)\b", text):
        return "corpus-completeness"
    if any(term in text for term in ("technical report", "technical event")):
        return "technical-status"
    if any(term in text for term in ("proceeding", "allegation", "no admission", "undertaking", "quashed", "appeal")):
        return "procedural-status"
    if re.search(r"\b(old-rule|superseded|current rule|today|current law|now)\b", text):
        return "current-law"
    return "mixed-professional-advice"


def release_state(mode: str, evidence: list[dict], gaps: list[dict]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if not evidence:
        return "insufficient-evidence", ["No indexed evidence was retrieved."]
    if mode in {
        "coverage-gap", "insufficient-evidence", "procedural-status-conflict",
        "needs-live-verification", "historical-only"
    }:
        return mode, [f"Question metadata routes this scenario to {mode}; the answer must satisfy that release gate."]
    if mode == "corpus-completeness" and gaps:
        return "coverage-gap", ["Relevant registered public source families have unresolved archive gaps."]
    if gaps:
        reasons.append("Archive gaps are disclosed; the answer must not claim corpus completeness.")

    events = [item for item in evidence if item["doc_type"] in {"enforcement-event", "technical-event"}]
    provisions = [item for item in evidence if item["doc_type"] == "provision-version"]
    current_provisions = [
        item for item in provisions
        if item["status"] in {"current-at-baseline", "current-at-baseline-appellate-control"}
        and not item.get("temporal_link_candidate_only", False)
    ]
    if mode == "current-law" and not current_provisions:
        return "needs-live-verification", reasons + ["No independently retrieved provision approved for current-law support was retrieved."]
    if mode == "current-law" and all(
        item.get("source_artifact", {}).get("snapshot_status") not in LOCAL_SNAPSHOT_STATUSES
        for item in current_provisions
    ):
        return "needs-live-verification", reasons + [
            "The controlling provision records are bound only to remote official URLs and require live source verification."
        ]
    if mode == "procedural-status" and not events:
        return "insufficient-evidence", reasons + ["No event record was retrieved for the requested procedural classification."]
    if mode == "technical-status" and not any(item["doc_type"] == "technical-event" for item in evidence):
        return "insufficient-evidence", reasons + ["No technical-event record was retrieved."]
    if mode == "current-law" and events and all(
        item["temporal_classification"] in {"superseded-or-old-rule", "quashed-or-overturned"}
        for item in events
    ):
        return "historical-only", reasons + ["Retrieved events are historical or displaced; only the provision comparator can support present guidance."]
    return "ready-for-grounded-drafting", reasons


def select_role_balanced_results(results: list[dict], limit: int, mode: str) -> list[dict]:
    """Keep ranked results while preserving evidence needed for coverage claims."""
    selected = list(results[:limit])
    selected_ids = {item["evidence_id"] for item in selected}
    if mode in {"coverage-gap", "corpus-completeness"}:
        for item in results:
            if item["doc_type"] != "source-family" or item["evidence_id"] in selected_ids:
                continue
            selected.append(item)
            selected_ids.add(item["evidence_id"])
            if sum(candidate["doc_type"] == "source-family" for candidate in selected) >= 2:
                break
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--blind", type=Path)
    parser.add_argument("--keyed", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--as-of", default="2026-08-29")
    parser.add_argument("--limit", type=int, default=18)
    args = parser.parse_args()
    root = args.root.resolve()
    blind_path = args.blind or root / "review" / "questions" / "case-question-bank-v5-blind.jsonl"
    keyed_path = args.keyed or root / "review" / "questions" / "case-question-bank-v5.jsonl"
    output_path = args.output or root / "review" / "results" / "case-loop-v5-evidence-packets.jsonl"
    report_path = args.report or root / "review" / "results" / "case-loop-v5-retrieval-report.json"
    database = root / "data" / "search-index.sqlite3"

    blind = read_jsonl(blind_path)
    keyed_by_id = {row["id"]: row for row in read_jsonl(keyed_path)}
    packets: list[dict] = []
    missing_any: list[str] = []
    missing_all: list[str] = []
    scored_question_count = 0
    state_counts: Counter[str] = Counter()
    top_rank_counts: Counter[int] = Counter()
    artifacts = source_artifact_lookup(root)

    for row in blind:
        row_id = row["id"]
        jurisdiction_filter = JURISDICTION_FILTERS.get(row["jurisdiction"], row["jurisdiction"])
        mode = route_mode(row)
        query_b, candidate_results, raw = double_search(
            database,
            row["question"],
            jurisdiction=jurisdiction_filter,
            as_of=args.as_of,
            limit=max(args.limit, 40),
        )
        merged = select_role_balanced_results(candidate_results, args.limit, mode)
        merged = expand_temporal_comparators(root, database, merged, args.as_of)
        evidence = []
        for result in merged:
            item = compact_result(result)
            item["rrf_rank"] = result["rrf_rank"]
            item["rrf_score"] = result["rrf_score"]
            item["retrieval_provenance"] = result["retrieval_provenance"]
            if result.get("temporal_link_role"):
                item["temporal_link_role"] = result["temporal_link_role"]
                item["linked_from_event_ids"] = result["linked_from_event_ids"]
                item["temporal_link_candidate_only"] = result["temporal_link_candidate_only"]
                item["temporal_link_metadata"] = result["temporal_link_metadata"]
            item["source_artifact"] = artifacts.get(result.get("official_url"), {
                "snapshot_status": "not-recorded-in-source-artifact-ledger",
                "provenance_status": "unverified",
            })
            evidence.append(item)
        gaps = relevant_gaps(root, jurisdiction_filter, include_all=mode == "corpus-completeness")
        state, reasons = release_state(mode, evidence, gaps)
        state_counts[state] += 1
        identity = json.dumps(
            {
                "id": row_id,
                "question": row["question"],
                "as_of": args.as_of,
                "evidence": [(item["evidence_id"], item["sha256"]) for item in evidence],
            },
            sort_keys=True,
        )
        retrieved_ids = [item["evidence_id"] for item in evidence]
        expected_event_ids = [f"event:{event_id}" for event_id in keyed_by_id[row_id]["event_ids"]]
        matched_ranks = [retrieved_ids.index(event_id) + 1 for event_id in expected_event_ids if event_id in retrieved_ids]
        if expected_event_ids:
            scored_question_count += 1
            if not matched_ranks:
                missing_any.append(row_id)
            if len(matched_ranks) != len(expected_event_ids):
                missing_all.append(row_id)
        for rank in matched_ranks:
            top_rank_counts[rank] += 1
        packets.append({
            "schema_version": "1.0",
            "id": row_id,
            "packet_id": hashlib.sha256(identity.encode("utf-8")).hexdigest(),
            "question": row["question"],
            "jurisdiction": row["jurisdiction"],
            "jurisdiction_filter": jurisdiction_filter,
            "scenario_date": row["applicable_date"],
            "answer_as_of": args.as_of,
            "answer_mode": mode,
            "release_state": state,
            "release_reasons": reasons,
            "query_a": row["question"],
            "query_b": query_b,
            "raw_result_counts": [len(result_set) for result_set in raw],
            "coverage_warnings": gaps,
            "evidence": evidence,
        })

    write_jsonl(output_path, packets)
    question_count = len(blind)
    report = {
        "schema_version": "1.0",
        "answer_as_of": args.as_of,
        "question_count": question_count,
        "retrieval_limit": args.limit,
        "questions_with_named_gold_events": scored_question_count,
        "questions_with_any_gold_event_retrieved": scored_question_count - len(missing_any),
        "any_gold_event_recall_rate": (scored_question_count - len(missing_any)) / scored_question_count if scored_question_count else 0,
        "questions_with_all_gold_events_retrieved": scored_question_count - len(missing_all),
        "all_gold_events_recall_rate": (scored_question_count - len(missing_all)) / scored_question_count if scored_question_count else 0,
        "missing_any_gold_event_question_ids": missing_any,
        "missing_one_or_more_gold_event_question_ids": missing_all,
        "release_state_counts": dict(sorted(state_counts.items())),
        "matched_gold_event_rank_histogram": {str(key): value for key, value in sorted(top_rank_counts.items())},
        "method": "SQLite FTS5 and an independent canonical-file scan are merged by reciprocal rank fusion, then role-balanced for coverage evidence; gold event IDs are used only for offline recall scoring.",
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(packets)} frozen evidence packets to {output_path}")
    print(f"Any-gold-event recall: {report['questions_with_any_gold_event_retrieved']}/{scored_question_count}")
    print(f"All-gold-events recall: {report['questions_with_all_gold_events_retrieved']}/{scored_question_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
