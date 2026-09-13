#!/usr/bin/env python3
"""Repeat retrieval against a draft and detect unaddressed temporal authority conflicts."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from double_search_kb import double_search
from check_answer import check_draft, resolve_claim_type
from reviewed_bindings import live_review_errors
from route_applicability import KNOWLEDGE_BASELINE


CURRENT_SUPPORT_STATUSES = {
    "current-at-baseline",
    "current-at-baseline-appellate-control",
}
TEMPORAL_CONTROL_CLASSES = {
    "appellate-control",
    "quashed-or-overturned",
}


def evidence_rows(connection: sqlite3.Connection, evidence_ids: list[str]) -> list[dict]:
    connection.row_factory = sqlite3.Row
    rows = []
    for evidence_id in evidence_ids:
        row = connection.execute(
            "SELECT * FROM documents WHERE evidence_id = ?", (evidence_id,)
        ).fetchone()
        if row is not None:
            rows.append(dict(row))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--database", type=Path)
    parser.add_argument("--as-of", default="2026-08-29")
    parser.add_argument("--limit", type=int, default=24)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--packet", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    database = args.database or root / "data" / "search-index.sqlite3"
    draft = json.loads(args.draft.read_text(encoding="utf-8-sig"))
    claims = draft.get("claims") or []
    reports = []
    errors = []
    warnings = []
    current_claims = [claim for claim in claims if resolve_claim_type(claim) == 'current-law']
    shared_reports = {}
    if current_claims:
        packet = json.loads(args.packet.read_text(encoding='utf-8-sig')) if args.packet else None
        shared = check_draft(root, {**draft, 'claims': current_claims}, packet, database)
        shared_reports = {id(claim): result for claim, result in zip(current_claims, shared['claim_reports'])}

    connection = sqlite3.connect(database)
    try:
        for index, claim in enumerate(claims, 1):
            claim_id = claim.get("claim_id") or f"claim-{index}"
            text = str(claim.get("text", "")).strip()
            claim_type = resolve_claim_type(claim)
            cited_ids = list(dict.fromkeys(claim.get("evidence_ids") or []))
            cited_rows = evidence_rows(connection, cited_ids)
            issue_families = {
                row["issue_family"] for row in cited_rows if row.get("issue_family")
            }
            issue_filter = next(iter(issue_families)) if len(issue_families) == 1 else None
            query_b, merged, _ = double_search(
                database,
                text,
                issue_family=issue_filter,
                as_of=args.as_of,
                limit=args.limit,
            )
            provision_query_b = None
            provision_rows = []
            if claim_type == 'current-law':
                # A complete instrument can crowd every provision out of a mixed
                # top-k window. Independently search that evidence type as well.
                provision_query_b, provision_rows, _ = double_search(
                    database, text, issue_family=issue_filter,
                    doc_type='provision-version', as_of=args.as_of, limit=args.limit,
                )
                present = {row['evidence_id'] for row in merged}
                merged.extend(row for row in provision_rows if row['evidence_id'] not in present)
            retrieved_ids = {row["evidence_id"] for row in merged}
            claim_errors = ['Shared current-law contract: ' + message for message in shared_reports.get(id(claim), {}).get('errors', [])]
            claim_warnings = []

            if cited_ids and not retrieved_ids.intersection(cited_ids):
                claim_warnings.append(
                    "The independent search did not recover any cited evidence in its result window."
                )

            controlling = [
                row for row in merged
                if row["temporal_classification"] in TEMPORAL_CONTROL_CLASSES
                and (not issue_families or row["issue_family"] in issue_families)
            ]
            unaddressed_controls = [
                row["evidence_id"] for row in controlling if row["evidence_id"] not in cited_ids
            ]
            if claim_type == "current-law" and unaddressed_controls:
                claim_errors.append(
                    "Independent search found unaddressed appellate or displaced authority: "
                    + ", ".join(unaddressed_controls[:6])
                )

            if claim_type == "current-law":
                current_provisions = [
                    row for row in merged
                    if row["doc_type"] == "provision-version"
                    and row["status"] in CURRENT_SUPPORT_STATUSES
                    and (not issue_families or row["issue_family"] in issue_families)
                    and (args.as_of <= KNOWLEDGE_BASELINE or not live_review_errors(
                        root, [row['evidence_id'].removeprefix('provision:')], args.as_of))
                ]
                if not current_provisions:
                    claim_errors.append(
                        "Independent search did not recover a provision approved for current-law support."
                    )
                elif not any(row['evidence_id'] in cited_ids for row in current_provisions):
                    claim_errors.append(
                        "Independent search did not recover a cited provision approved for current-law support."
                    )
                uncited_current = [
                    row["evidence_id"] for row in current_provisions
                    if row["evidence_id"] not in cited_ids
                ]
                if uncited_current:
                    claim_warnings.append(
                        "Independent search found an uncited current provision comparator for semantic review; "
                        "retrieval alone does not establish a contradiction: "
                        + ", ".join(uncited_current[:4])
                    )

            errors.extend(f"{claim_id}: {item}" for item in claim_errors)
            warnings.extend(f"{claim_id}: {item}" for item in claim_warnings)
            reports.append({
                "claim_id": claim_id,
                "query_a": text,
                "query_b": query_b,
                "provision_query_b": provision_query_b,
                "provision_search_evidence_ids": [row['evidence_id'] for row in provision_rows],
                "issue_family_filter": issue_filter,
                "retrieved_evidence_ids": [row["evidence_id"] for row in merged],
                "unaddressed_temporal_controls": unaddressed_controls,
                "passed": not claim_errors,
                "errors": claim_errors,
                "warnings": claim_warnings,
            })
    finally:
        connection.close()

    report = {
        "schema_version": "1.0",
        "draft": str(args.draft),
        "answer_as_of": args.as_of,
        "method": "independent-double-search-temporal-conflict-check",
        "passed": not errors,
        "blocking_error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "claim_reports": reports,
        "semantic_review_required": (
            "This second checker re-runs retrieval and temporal conflict tests. It does not prove "
            "semantic entailment; an independent reviewer must still compare claim text with exact source spans."
        ),
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote independent check report to {args.output}")
        print(f"Passed: {report['passed']}")
    else:
        print(rendered, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
