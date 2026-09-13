#!/usr/bin/env python3
"""Validate the v5 professional scenario benchmark and its novelty."""

from __future__ import annotations

import argparse
from collections import Counter
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import sys


KEYED_FIELDS = {
    "id",
    "jurisdiction",
    "domain",
    "professional_role",
    "scenario_type",
    "case_ref",
    "event_ids",
    "source_family_ids",
    "applicable_date",
    "angle",
    "question",
    "correct_answer",
    "key_points",
    "source_binding",
    "expected_release_state",
    "critical_error_traps",
}
BLIND_FIELDS = {
    "id",
    "jurisdiction",
    "domain",
    "professional_role",
    "scenario_type",
    "case_ref",
    "event_ids",
    "source_family_ids",
    "applicable_date",
    "angle",
    "question",
    "source_binding",
}
REQUIRED_JURISDICTIONS = {
    "National/Cross-jurisdiction",
    "ACT",
    "NSW",
    "NT",
    "QLD",
    "SA",
    "TAS",
    "VIC",
    "WA",
}
ALLOWED_RELEASE_STATES = {
    "ready-for-grounded-drafting",
    "historical-only",
    "needs-live-verification",
    "coverage-gap",
    "insufficient-evidence",
    "procedural-status-conflict",
}
FAIL_CLOSED_STATES = ALLOWED_RELEASE_STATES - {"ready-for-grounded-drafting"}
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
WORD_RE = re.compile(r"[a-z0-9]+")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: JSONL row is not an object")
        rows.append(value)
    return rows


def normalized(text: str) -> str:
    return " ".join(WORD_RE.findall(text.lower()))


def tokens(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


def jaccard(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def near_duplicate(left: str, right: str) -> tuple[bool, float, float]:
    norm_left, norm_right = normalized(left), normalized(right)
    sequence = SequenceMatcher(None, norm_left, norm_right).ratio()
    token_score = jaccard(norm_left, norm_right)
    duplicate = norm_left == norm_right or sequence >= 0.86 or token_score >= 0.68
    return duplicate, sequence, token_score


def corpus_ids(root: Path) -> tuple[set[str], set[str]]:
    event_ids: set[str] = set()
    for name in ("enforcement-events-full.jsonl", "technical-events-full.jsonl"):
        event_ids.update(row["event_id"] for row in read_jsonl(root / "data" / name))
    register = json.loads((root / "data" / "enforcement-source-register.json").read_text(encoding="utf-8-sig"))
    source_ids = {item["id"] for item in register["sources"]}
    return event_ids, source_ids


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    question_dir = root / "review" / "questions"
    keyed_path = question_dir / "case-question-bank-v5.jsonl"
    blind_path = question_dir / "case-question-bank-v5-blind.jsonl"
    packets_path = root / "review" / "results" / "case-loop-v5-evidence-packets.jsonl"
    retrieval_report_path = root / "review" / "results" / "case-loop-v5-retrieval-report.json"
    prior_paths = [
        question_dir / "case-question-bank-v3.jsonl",
        question_dir / "case-question-bank-v4.jsonl",
    ]
    for path in [keyed_path, blind_path, packets_path, retrieval_report_path, *prior_paths]:
        if not path.is_file():
            failures.append(f"Missing benchmark file: {path.relative_to(root)}")
    if failures:
        return failures

    try:
        keyed = read_jsonl(keyed_path)
        blind = read_jsonl(blind_path)
        packets = read_jsonl(packets_path)
        retrieval_report = json.loads(retrieval_report_path.read_text(encoding="utf-8-sig"))
        prior = [row for path in prior_paths for row in read_jsonl(path)]
        valid_event_ids, valid_source_ids = corpus_ids(root)
        temporal_links = {
            row["event_id"]: row
            for row in read_jsonl(root / "data" / "event-provision-links.jsonl")
        }
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        return [str(exc)]

    if len(keyed) != 100:
        failures.append(f"Expected 100 keyed v5 questions, found {len(keyed)}")
    if len(blind) != 100:
        failures.append(f"Expected 100 blind v5 questions, found {len(blind)}")
    expected_ids = [f"AUPRO-{number:03d}" for number in range(1, 101)]
    keyed_ids = [str(row.get("id", "")) for row in keyed]
    blind_ids = [str(row.get("id", "")) for row in blind]
    if keyed_ids != expected_ids:
        failures.append("Keyed v5 IDs are not exactly AUPRO-001 through AUPRO-100 in order")
    if blind_ids != expected_ids:
        failures.append("Blind v5 IDs are not exactly AUPRO-001 through AUPRO-100 in order")

    packet_ids = [str(row.get("id", "")) for row in packets]
    if packet_ids != expected_ids:
        failures.append("Evidence-packet IDs are not exactly AUPRO-001 through AUPRO-100 in order")
    packet_by_id = {str(row.get("id", "")): row for row in packets}

    blind_by_id = {str(row.get("id", "")): row for row in blind}
    scenario_signatures: set[tuple] = set()
    for row in keyed:
        row_id = str(row.get("id", "<missing-id>"))
        fields = set(row)
        if fields != KEYED_FIELDS:
            failures.append(
                f"{row_id}: keyed fields differ; missing={sorted(KEYED_FIELDS - fields)}, extra={sorted(fields - KEYED_FIELDS)}"
            )
        if CJK_RE.search(json.dumps(row, ensure_ascii=False)):
            failures.append(f"{row_id}: contains Han characters")
        question = str(row.get("question", ""))
        if len(question.split()) < 18:
            failures.append(f"{row_id}: question is too short to establish a professional scenario")
        if not isinstance(row.get("key_points"), list) or len(row.get("key_points", [])) != 5:
            failures.append(f"{row_id}: key_points must contain exactly five items")
        if not isinstance(row.get("critical_error_traps"), list) or not row.get("critical_error_traps"):
            failures.append(f"{row_id}: critical_error_traps must be a non-empty array")
        event_ids = row.get("event_ids")
        if not isinstance(event_ids, list):
            failures.append(f"{row_id}: event_ids must be an array")
            event_ids = []
        if not event_ids and row.get("expected_release_state") not in {
            "coverage-gap", "insufficient-evidence", "procedural-status-conflict"
        }:
            failures.append(
                f"{row_id}: event_ids may be empty only for a source-level coverage, evidence or procedural-status scenario"
            )
        for event_id in event_ids:
            if event_id not in valid_event_ids:
                failures.append(f"{row_id}: unknown event_id {event_id}")
        source_ids = row.get("source_family_ids")
        if not isinstance(source_ids, list) or not source_ids:
            failures.append(f"{row_id}: source_family_ids must be a non-empty array")
            source_ids = []
        for source_id in source_ids:
            if source_id not in valid_source_ids:
                failures.append(f"{row_id}: unknown source_family_id {source_id}")
        if row.get("expected_release_state") not in ALLOWED_RELEASE_STATES:
            failures.append(f"{row_id}: invalid expected_release_state {row.get('expected_release_state')}")
        if not re.fullmatch(r"\d{4}(?:-\d{2}(?:-\d{2})?)?", str(row.get("applicable_date", ""))):
            failures.append(f"{row_id}: applicable_date must be YYYY, YYYY-MM or YYYY-MM-DD")
        signature = (
            tuple(sorted(event_ids)),
            normalized(str(row.get("professional_role", ""))),
            normalized(str(row.get("angle", ""))),
        )
        if signature in scenario_signatures:
            failures.append(f"{row_id}: repeats an event-role-angle scenario signature within v5")
        scenario_signatures.add(signature)

        blind_row = blind_by_id.get(row_id)
        if blind_row is None:
            failures.append(f"{row_id}: missing blind record")
        else:
            blind_fields = set(blind_row)
            if blind_fields != BLIND_FIELDS:
                failures.append(
                    f"{row_id}: blind fields differ; missing={sorted(BLIND_FIELDS - blind_fields)}, extra={sorted(blind_fields - BLIND_FIELDS)}"
                )
            for field in BLIND_FIELDS:
                if blind_row.get(field) != row.get(field):
                    failures.append(f"{row_id}: blind field does not match keyed record: {field}")

        packet = packet_by_id.get(row_id)
        if packet is None:
            failures.append(f"{row_id}: missing frozen evidence packet")
        else:
            if packet.get("release_state") != row.get("expected_release_state"):
                failures.append(
                    f"{row_id}: packet state {packet.get('release_state')} does not match keyed state "
                    f"{row.get('expected_release_state')}"
                )
            packet_evidence = packet.get("evidence")
            if not isinstance(packet_evidence, list) or not packet_evidence:
                failures.append(f"{row_id}: frozen evidence packet is empty")
                packet_evidence = []
            evidence_ids = {str(item.get("evidence_id", "")) for item in packet_evidence}
            for event_id in event_ids:
                if f"event:{event_id}" not in evidence_ids:
                    failures.append(f"{row_id}: named gold event is absent from the frozen packet: {event_id}")
            for item in packet_evidence:
                if item.get("doc_type") not in {"enforcement-event", "technical-event"}:
                    continue
                event_id = str(item.get("evidence_id", "")).removeprefix("event:")
                link = temporal_links.get(event_id)
                if link is None:
                    failures.append(f"{row_id}: packet event lacks a reviewed temporal link: {event_id}")
                    continue
                for provision_id in link.get("current_comparator_ids", []):
                    if f"provision:{provision_id}" not in evidence_ids:
                        failures.append(
                            f"{row_id}: packet omits the reviewed current comparator for {event_id}: {provision_id}"
                        )

    all_candidates = [(str(row.get("id", "")), str(row.get("question", ""))) for row in keyed]
    prior_candidates = [(str(row.get("id", "")), str(row.get("question", ""))) for row in prior]
    for index, (row_id, question) in enumerate(all_candidates):
        comparisons = prior_candidates + all_candidates[:index]
        for other_id, other_question in comparisons:
            duplicate, sequence, token_score = near_duplicate(question, other_question)
            if duplicate:
                failures.append(
                    f"{row_id}: possible semantic duplicate of {other_id} "
                    f"(sequence={sequence:.3f}, token_jaccard={token_score:.3f})"
                )

    jurisdiction_counts = Counter(str(row.get("jurisdiction", "")) for row in keyed)
    for jurisdiction in sorted(REQUIRED_JURISDICTIONS):
        if jurisdiction_counts[jurisdiction] < 5:
            failures.append(f"v5 has fewer than five questions for {jurisdiction}: {jurisdiction_counts[jurisdiction]}")
    if jurisdiction_counts["National/Cross-jurisdiction"] < 15:
        failures.append(
            "v5 has fewer than 15 National/Cross-jurisdiction questions: "
            f"{jurisdiction_counts['National/Cross-jurisdiction']}"
        )
    role_count = len({normalized(str(row.get("professional_role", ""))) for row in keyed})
    domain_count = len({normalized(str(row.get("domain", ""))) for row in keyed})
    if role_count < 8:
        failures.append(f"v5 has fewer than eight professional roles: {role_count}")
    if domain_count < 12:
        failures.append(f"v5 has fewer than 12 domains: {domain_count}")
    fail_closed_count = sum(row.get("expected_release_state") in FAIL_CLOSED_STATES for row in keyed)
    if fail_closed_count < 15:
        failures.append(f"v5 has fewer than 15 fail-closed scenarios: {fail_closed_count}")
    if retrieval_report.get("questions_with_named_gold_events") != 94:
        failures.append("v5 retrieval report does not contain the expected 94 named-event scenarios")
    if retrieval_report.get("questions_with_all_gold_events_retrieved") != 94:
        failures.append("v5 retrieval report is below 94/94 all-gold-event recall")
    if retrieval_report.get("missing_one_or_more_gold_event_question_ids"):
        failures.append("v5 retrieval report contains named-event retrieval misses")

    if not failures:
        print("Professional benchmark validation passed.")
        print(f"Questions: {len(keyed)}")
        print(f"Prior questions compared for novelty: {len(prior)}")
        print(f"Jurisdictions: {len(jurisdiction_counts)}")
        print(f"Professional roles: {role_count}")
        print(f"Domains: {domain_count}")
        print(f"Fail-closed scenarios: {fail_closed_count}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    failures = validate(args.root.resolve())
    if failures:
        print(f"Professional benchmark validation failed with {len(failures)} issue(s):", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
