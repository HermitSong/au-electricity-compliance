#!/usr/bin/env python3
"""Validate v5 blind answers and the independent five-dimension audit."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sqlite3
import sys


ANSWER_FIELDS = {
    "id",
    "disposition",
    "answer_as_of",
    "answer",
    "immediate_actions",
    "jurisdiction_qualification",
    "temporal_qualification",
    "legal_status_qualification",
    "uncertainty_and_escalation",
    "confidence",
    "claims",
    "kb_sources",
}
GRADE_FIELDS = {
    "id",
    "grade",
    "scorecard",
    "points_hit",
    "points_total",
    "critical_error",
    "defect_type",
    "finding",
    "required_remediation",
}
SCORECARD_FIELDS = {
    "jurisdiction_and_scope",
    "temporal_applicability",
    "legal_and_procedural_status",
    "operational_control",
    "evidence_and_uncertainty",
}
ALLOWED_DISPOSITIONS = {
    "ready-for-grounded-drafting",
    "historical-only",
    "needs-live-verification",
    "coverage-gap",
    "insufficient-evidence",
    "procedural-status-conflict",
}
CURRENT_SUPPORT_STATUSES = {"current-at-baseline", "current-at-baseline-appellate-control"}
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--answers", type=Path)
    parser.add_argument("--grades", type=Path)
    parser.add_argument("--require-perfect", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    answers_path = args.answers or root / "review" / "results" / "case-loop-v5-answers.jsonl"
    grades_path = args.grades or root / "review" / "results" / "case-loop-v5-grades-final.jsonl"
    keyed_path = root / "review" / "questions" / "case-question-bank-v5.jsonl"
    packets_path = root / "review" / "results" / "case-loop-v5-evidence-packets.jsonl"
    required_paths = [answers_path, grades_path, keyed_path, packets_path]
    failures = [f"Missing result file: {path.relative_to(root)}" for path in required_paths if not path.is_file()]
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    try:
        answers = read_jsonl(answers_path)
        grades = read_jsonl(grades_path)
        keyed = read_jsonl(keyed_path)
        packets = read_jsonl(packets_path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    expected_ids = [f"AUPRO-{number:03d}" for number in range(1, 101)]
    keyed_by_id = {row["id"]: row for row in keyed}
    packet_by_id = {row["id"]: row for row in packets}
    answer_ids = [str(row.get("id", "")) for row in answers]
    grade_ids = [str(row.get("id", "")) for row in grades]
    if answer_ids != expected_ids:
        failures.append("Answer IDs are not exactly AUPRO-001 through AUPRO-100 in order")
    if grade_ids != expected_ids:
        failures.append("Grade IDs are not exactly AUPRO-001 through AUPRO-100 in order")

    database = sqlite3.connect(root / "data" / "search-index.sqlite3")
    database.row_factory = sqlite3.Row
    try:
        indexed = {
            row["evidence_id"]: dict(row)
            for row in database.execute(
                "SELECT evidence_id, doc_type, status, temporal_classification, source_path FROM documents"
            )
        }
    finally:
        database.close()

    for row in answers:
        row_id = str(row.get("id", "<missing-id>"))
        fields = set(row)
        if fields != ANSWER_FIELDS:
            failures.append(
                f"{row_id}: answer fields differ; missing={sorted(ANSWER_FIELDS-fields)}, extra={sorted(fields-ANSWER_FIELDS)}"
            )
        if CJK_RE.search(json.dumps(row, ensure_ascii=False)):
            failures.append(f"{row_id}: answer contains Han characters")
        expected = keyed_by_id.get(row_id, {}).get("expected_release_state")
        disposition = row.get("disposition")
        if disposition not in ALLOWED_DISPOSITIONS:
            failures.append(f"{row_id}: invalid disposition {disposition}")
        if expected and disposition != expected:
            failures.append(f"{row_id}: disposition {disposition} does not match keyed state {expected}")
        if row.get("answer_as_of") != "2026-08-29":
            failures.append(f"{row_id}: answer_as_of must be 2026-08-29")
        if not isinstance(row.get("immediate_actions"), list) or len(row.get("immediate_actions", [])) < 2:
            failures.append(f"{row_id}: immediate_actions must contain at least two actions")
        if row.get("confidence") not in {"high", "medium", "low"}:
            failures.append(f"{row_id}: invalid confidence")
        packet = packet_by_id.get(row_id, {})
        packet_ids = {item["evidence_id"] for item in packet.get("evidence", [])}
        packet_ids.update(
            f"source-family:{item['source_family_id']}"
            for item in packet.get("coverage_warnings", [])
            if item.get("source_family_id")
        )
        claims = row.get("claims")
        if not isinstance(claims, list) or not claims:
            failures.append(f"{row_id}: claims must be a non-empty array")
            claims = []
        for index, claim in enumerate(claims, 1):
            claim_id = claim.get("claim_id", f"claim-{index}") if isinstance(claim, dict) else f"claim-{index}"
            if not isinstance(claim, dict) or set(claim) != {"claim_id", "text", "claim_type", "evidence_ids"}:
                failures.append(f"{row_id}/{claim_id}: malformed claim")
                continue
            evidence_ids = claim.get("evidence_ids")
            if not isinstance(evidence_ids, list) or not evidence_ids:
                failures.append(f"{row_id}/{claim_id}: claim has no evidence IDs")
                continue
            rows = []
            for evidence_id in evidence_ids:
                if evidence_id not in indexed:
                    failures.append(f"{row_id}/{claim_id}: unknown evidence ID {evidence_id}")
                    continue
                rows.append(indexed[evidence_id])
                if evidence_id not in packet_ids:
                    failures.append(f"{row_id}/{claim_id}: evidence ID was not in the frozen packet: {evidence_id}")
            if claim.get("claim_type") == "current-law" and not any(
                item["doc_type"] == "provision-version" and item["status"] in CURRENT_SUPPORT_STATUSES
                for item in rows
            ):
                failures.append(f"{row_id}/{claim_id}: current-law claim lacks an approved current provision")
            if claim.get("claim_type") not in {
                "current-law", "historical-fact", "procedural-status", "technical-finding", "control-recommendation", "coverage-limit"
            }:
                failures.append(f"{row_id}/{claim_id}: invalid claim_type {claim.get('claim_type')}")
        sources = row.get("kb_sources")
        if not isinstance(sources, list) or not sources:
            failures.append(f"{row_id}: kb_sources must be a non-empty array")
        else:
            for source in sources:
                if not (root / str(source)).is_file():
                    failures.append(f"{row_id}: missing KB source path {source}")

    total_points = 0
    pass_count = 0
    critical_count = 0
    for row in grades:
        row_id = str(row.get("id", "<missing-id>"))
        fields = set(row)
        if fields != GRADE_FIELDS:
            failures.append(
                f"{row_id}: grade fields differ; missing={sorted(GRADE_FIELDS-fields)}, extra={sorted(fields-GRADE_FIELDS)}"
            )
        if CJK_RE.search(json.dumps(row, ensure_ascii=False)):
            failures.append(f"{row_id}: grade contains Han characters")
        scorecard = row.get("scorecard")
        if not isinstance(scorecard, dict) or set(scorecard) != SCORECARD_FIELDS:
            failures.append(f"{row_id}: scorecard must contain exactly the five professional dimensions")
            continue
        if any(value not in {True, False} for value in scorecard.values()):
            failures.append(f"{row_id}: scorecard values must be booleans")
        computed_points = sum(value is True for value in scorecard.values())
        if row.get("points_total") != 5 or row.get("points_hit") != computed_points:
            failures.append(f"{row_id}: points do not match scorecard")
        critical = row.get("critical_error") is True
        expected_grade = "pass" if computed_points == 5 and not critical else ("fail" if critical else "partial")
        if row.get("grade") != expected_grade:
            failures.append(f"{row_id}: grade {row.get('grade')} should be {expected_grade}")
        total_points += computed_points
        pass_count += row.get("grade") == "pass"
        critical_count += critical

    if args.require_perfect and (pass_count != 100 or total_points != 500 or critical_count):
        failures.append(
            f"Final professional gate is not perfect: pass={pass_count}/100, points={total_points}/500, critical={critical_count}"
        )
    if failures:
        print(f"Professional result validation failed with {len(failures)} issue(s):", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("Professional result validation passed.")
    print(f"Answers: {len(answers)}")
    print(f"Pass: {pass_count}/100")
    print(f"Points: {total_points}/500")
    print(f"Critical errors: {critical_count}")
    print("Grade distribution:", dict(sorted(Counter(row["grade"] for row in grades).items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
