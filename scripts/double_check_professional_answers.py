#!/usr/bin/env python3
"""Batch deterministic and independent-search checks for v5 answers."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sqlite3

from double_search_kb import double_search
from check_answer import check_draft, resolve_claim_type


CURRENT_SUPPORT_STATUSES = {"current-at-baseline", "current-at-baseline-appellate-control"}
CONCLUSIVE_LANGUAGE = re.compile(r"\b(contravened|breached|liable|found guilty|convicted|court found)\b", re.I)
COURT_LANGUAGE = re.compile(r"\b(found guilty|convicted|court found|court held|liable)\b", re.I)
AFFIRMATIVE_COMPLETENESS = re.compile(
    r"\b(corpus|archive|register|source|record|history|coverage)\b.{0,100}"
    r"\b(is complete|is comprehensive|is exhaustive|contains all|contains every|covers all|covers every|includes all|includes every|no other)\b",
    re.I,
)
ALLEGATION_LANGUAGE = re.compile(r"\b(allege|alleges|alleged|alleging|proceedings|claim by the regulator)\b", re.I)
NON_FINAL_STATUS = re.compile(r"proceeding|allegation|pending|investigation|reported-breach", re.I)
JUDICIAL_STATUS = re.compile(r"^(?:final(?:$|-)|.*(?:conviction|found-guilty|court-order|judgment).*)", re.I)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--answers", type=Path)
    parser.add_argument("--packets", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--as-of", default="2026-08-29")
    args = parser.parse_args()
    root = args.root.resolve()
    answers_path = args.answers or root / "review" / "results" / "case-loop-v5-answers.jsonl"
    packets_path = args.packets or root / "review" / "results" / "case-loop-v5-evidence-packets.jsonl"
    output_path = args.output or root / "review" / "results" / "case-loop-v5-double-checks.jsonl"
    summary_path = args.summary or root / "review" / "results" / "case-loop-v5-double-check-summary.json"
    answers = read_jsonl(answers_path)
    packets = {row["id"]: row for row in read_jsonl(packets_path)}
    database_path = root / "data" / "search-index.sqlite3"

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        indexed = {row["evidence_id"]: dict(row) for row in connection.execute("SELECT * FROM documents")}
    finally:
        connection.close()

    results = []
    for answer in answers:
        row_id = answer["id"]
        packet = packets[row_id]
        packet_ids = {item["evidence_id"] for item in packet["evidence"]}
        packet_ids.update(
            f"source-family:{item['source_family_id']}"
            for item in packet.get("coverage_warnings", [])
            if item.get("source_family_id")
        )
        question_errors: list[str] = []
        question_warnings: list[str] = []
        claim_reports = []
        current_claims = [claim for claim in answer.get('claims', []) if resolve_claim_type(claim) == 'current-law']
        current_checks = check_draft(root, {**answer, 'question': answer.get('question') or packet['question'], 'claims': current_claims}, packet, database_path) if current_claims else None
        shared_reports = {id(claim): result for claim, result in zip(current_claims, current_checks['claim_reports'])} if current_checks else {}
        for claim in answer.get("claims", []):
            claim_id = claim.get("claim_id", "missing-claim-id")
            text = str(claim.get("text", ""))
            evidence_ids = list(dict.fromkeys(claim.get("evidence_ids") or []))
            errors: list[str] = []
            warnings: list[str] = []
            evidence = []
            errors.extend('Shared current-law contract: ' + message for message in shared_reports.get(id(claim), {}).get('errors', []))
            for evidence_id in evidence_ids:
                row = indexed.get(evidence_id)
                if row is None:
                    errors.append(f"Unknown evidence ID: {evidence_id}")
                    continue
                evidence.append(row)
                if evidence_id not in packet_ids:
                    errors.append(f"Evidence was outside the frozen packet: {evidence_id}")
                if row["doc_type"] in {"enforcement-event", "technical-event", "provision-version"}:
                    if not row["official_url"] or not row["official_url"].startswith("https://"):
                        errors.append(f"Controlling evidence lacks an official HTTPS URL: {evidence_id}")

            if resolve_claim_type(claim) == "current-law":
                if not any(
                    row["doc_type"] == "provision-version" and row["status"] in CURRENT_SUPPORT_STATUSES
                    for row in evidence
                ):
                    errors.append("Current-law claim lacks an approved current provision in its citations.")
                if any(row["temporal_classification"] in {"quashed-or-overturned", "superseded-or-old-rule"} for row in evidence):
                    errors.append("Current-law claim cites displaced or old-rule evidence without a controlling current comparator.")

            if (
                CONCLUSIVE_LANGUAGE.search(text)
                and not ALLEGATION_LANGUAGE.search(text)
                and any(NON_FINAL_STATUS.search(row["status"] or "") for row in evidence)
            ):
                errors.append("Conclusive liability language is paired with non-final evidence.")
            if COURT_LANGUAGE.search(text) and not any(JUDICIAL_STATUS.search(row["status"] or "") for row in evidence):
                errors.append("Court or liability language lacks a final judicial-status source.")
            if (
                any(row["doc_type"] == "technical-event" for row in evidence)
                and CONCLUSIVE_LANGUAGE.search(text)
                and not re.search(r"\b(no|not|without|does not|cannot|do not)\b.{0,40}\b(contravention|breach|liable|guilty|finding)\b", text, re.I)
            ):
                errors.append("Technical-event evidence is used for an affirmative contravention or liability claim.")
            if (
                claim.get("claim_type") != "coverage-limit"
                and AFFIRMATIVE_COMPLETENESS.search(text)
                and any(row["coverage_status"] == "archive-gap" for row in evidence)
            ):
                errors.append("Completeness language is unsupported because cited source coverage has an archive gap.")

            issue_families = {row["issue_family"] for row in evidence if row.get("issue_family")}
            issue_filter = next(iter(issue_families)) if len(issue_families) == 1 else None
            try:
                independent_query = f"{packet['question']} {text}"
                query_b, merged, _ = double_search(
                    database_path,
                    independent_query,
                    jurisdiction=packet.get("jurisdiction_filter"),
                    issue_family=issue_filter,
                    as_of=args.as_of,
                    limit=24,
                )
                retrieved_ids = [row["evidence_id"] for row in merged]
                if claim.get("claim_type") == "coverage-limit" and not set(evidence_ids).intersection(retrieved_ids):
                    missing_types = {
                        indexed[evidence_id]["doc_type"]
                        for evidence_id in evidence_ids if evidence_id in indexed
                    }
                    for doc_type in sorted(missing_types):
                        focused_jurisdiction = (
                            None if doc_type in {"provision-version", "obligation-control"}
                            else packet.get("jurisdiction_filter")
                        )
                        _, coverage_rows, _ = double_search(
                            database_path,
                            independent_query,
                            jurisdiction=focused_jurisdiction,
                            doc_type=doc_type,
                            as_of=args.as_of,
                            limit=24,
                        )
                        retrieved_ids.extend(row["evidence_id"] for row in coverage_rows)
            except ValueError as exc:
                independent_query = f"{packet['question']} {text}"
                query_b = independent_query
                retrieved_ids = []
                errors.append(f"Independent search could not form a valid query: {exc}")
            if evidence_ids and not set(evidence_ids).intersection(retrieved_ids):
                warnings.append("Independent search did not recover a cited evidence ID in Top 24.")

            question_errors.extend(f"{claim_id}: {message}" for message in errors)
            question_warnings.extend(f"{claim_id}: {message}" for message in warnings)
            claim_reports.append({
                "claim_id": claim_id,
                "claim_type": claim.get("claim_type"),
                "evidence_ids": evidence_ids,
                "independent_query_b": query_b,
                "independent_top24_evidence_ids": retrieved_ids,
                "passed": not errors,
                "errors": errors,
                "warnings": warnings,
            })

        results.append({
            "id": row_id,
            "passed": not question_errors,
            "blocking_error_count": len(question_errors),
            "warning_count": len(question_warnings),
            "errors": question_errors,
            "warnings": question_warnings,
            "claim_reports": claim_reports,
            "semantic_review_required": True,
        })

    write_jsonl(output_path, results)
    failed = [row["id"] for row in results if not row["passed"]]
    summary = {
        "schema_version": "1.0",
        "answer_as_of": args.as_of,
        "question_count": len(results),
        "passed_question_count": len(results) - len(failed),
        "failed_question_count": len(failed),
        "failed_question_ids": failed,
        "blocking_error_count": sum(row["blocking_error_count"] for row in results),
        "warning_count": sum(row["warning_count"] for row in results),
        "claim_type_counts": dict(sorted(Counter(
            claim.get("claim_type", "") for answer in answers for claim in answer.get("claims", [])
        ).items())),
        "method": "Frozen-packet invariant checks plus an independent double search for every material claim.",
        "semantic_review_required": "An independent reviewer must still compare each claim with the exact cited text and score the five professional dimensions.",
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(results)} question checks to {output_path}")
    print(f"Passed: {summary['passed_question_count']}/{summary['question_count']}")
    print(f"Blocking errors: {summary['blocking_error_count']}")
    print(f"Warnings: {summary['warning_count']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
