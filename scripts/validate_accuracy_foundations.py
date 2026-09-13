#!/usr/bin/env python3
"""Validate provenance, obligation, temporal-routing and applicability foundations."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

from build_source_artifact_ledger import collect_canonical_urls
from double_search_kb import double_search
from route_applicability import route_question


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    ledger = read_jsonl(root / "data" / "source-artifact-ledger.jsonl")
    ledger_ids = [row["artifact_id"] for row in ledger]
    if len(ledger_ids) != len(set(ledger_ids)):
        failures.append("Source-artifact ledger contains duplicate artifact IDs.")
    references, _ = collect_canonical_urls(root)
    ledger_urls = {row["canonical_url"] for row in ledger if row["canonical_url"]}
    missing_urls = sorted(set(references) - ledger_urls)
    if missing_urls:
        failures.append(f"Source-artifact ledger omits {len(missing_urls)} canonical URLs.")
    local_paths: set[str] = set()
    for row in ledger:
        if row["record_type"] != "local-official-snapshot":
            if row["snapshot_status"] != "remote-only-no-snapshot" or row["sha256"] is not None:
                failures.append(f"Remote-only source has invalid snapshot metadata: {row['artifact_id']}")
            continue
        relative = row["snapshot_path"]
        if relative in local_paths:
            failures.append(f"Duplicate local snapshot path: {relative}")
        local_paths.add(relative)
        path = root / relative
        if not path.is_file():
            failures.append(f"Ledger snapshot is missing: {relative}")
        elif file_sha256(path) != row["sha256"]:
            failures.append(f"Ledger snapshot hash mismatch: {relative}")
    expected_local = {
        path.relative_to(root).as_posix()
        for path in (root / "official-documents").rglob("*")
        if path.is_file() and path.name != "SOURCES.md"
    }
    capture_manifest = root / "official-snapshots" / "manifest.jsonl"
    if capture_manifest.exists():
        expected_local.update(
            row["snapshot_path"]
            for row in read_jsonl(capture_manifest)
            if row.get("capture_status") == "captured" and (root / row["snapshot_path"]).is_file()
        )
    if expected_local != local_paths:
        failures.append("Source-artifact ledger does not cover exactly the bundled official documents.")

    provisions = read_json(root / "data" / "provision-version-register.json")
    obligations = read_json(root / "data" / "obligation-register.json")
    bindings = read_json(root / "data" / "provision-source-bindings.json")
    provision_ids = {row["provision_id"] for row in provisions["provisions"]}
    obligation_provision_ids = {row["provision_id"] for row in obligations["obligations"]}
    if provision_ids != obligation_provision_ids:
        failures.append("Obligation register is not in one-to-one parity with the provision register.")
    if obligations["obligation_count"] != len(obligations["obligations"]):
        failures.append("Obligation register count is incorrect.")
    if bindings["binding_count"] != len(provisions["provisions"]):
        failures.append("Provision-source binding register is not in parity with the provision register.")
    for obligation in obligations["obligations"]:
        if not obligation["applicability"]["required_inputs"] or not obligation["minimum_control_evidence"]:
            failures.append(f"Obligation lacks applicability or control evidence: {obligation['obligation_id']}")

    source_chunks = read_jsonl(root / "data" / "source-text-chunks.jsonl")
    source_chunks_by_id = {f"source-span:{chunk['chunk_id']}": chunk for chunk in source_chunks}
    for chunk in source_chunks:
        snapshot = root / chunk["snapshot_path"]
        if not snapshot.is_file() or file_sha256(snapshot) != chunk["source_sha256"]:
            failures.append(f"Source-text chunk is not bound to the captured source bytes: {chunk['chunk_id']}")
        if hashlib.sha256(chunk["text"].encode("utf-8")).hexdigest() != chunk["text_sha256"]:
            failures.append(f"Source-text chunk hash mismatch: {chunk['chunk_id']}")
    for binding in bindings["bindings"]:
        if not binding["supports_current_law_drafting"]:
            continue
        if not binding["source_span_ids"]:
            failures.append(f"Drafting-approved binding has no source spans: {binding['provision_id']}")
        for evidence_id in binding["source_span_ids"]:
            if evidence_id not in source_chunks_by_id:
                failures.append(f"Provision binding references a missing source span: {evidence_id}")
        if binding["professional_legal_review_status"] != "required-before-execution":
            failures.append(f"Provision binding bypasses professional execution review: {binding['provision_id']}")
    connection = sqlite3.connect(root / "data" / "search-index.sqlite3")
    try:
        indexed_source_spans = connection.execute(
            "SELECT COUNT(*) FROM documents WHERE doc_type = 'official-source-span'"
        ).fetchone()[0]
    finally:
        connection.close()
    if indexed_source_spans != len(source_chunks):
        failures.append("Search index official-source-span count does not match extracted source chunks.")

    events = {
        row["event_id"]: row
        for filename in ("enforcement-events-full.jsonl", "technical-events-full.jsonl")
        for row in read_jsonl(root / "data" / filename)
    }
    links = read_jsonl(root / "data" / "event-provision-links.jsonl")
    for link in links:
        event = events[link["event_id"]]
        comparators = link["current_comparator_ids"]
        if link.get("mapping_method") != "deterministic-keyword-and-source-rules-v2":
            failures.append(f"Temporal link lacks the current mapping method: {link['event_id']}")
        if link.get("review_status") != "candidate-auto-mapped":
            failures.append(f"Auto-generated temporal link is not marked as a candidate: {link['event_id']}")
        if link.get("reviewed_by") is not None or link.get("reviewed_at") is not None:
            failures.append(f"Auto-generated temporal link falsely claims completed review: {link['event_id']}")
        is_wa = event["jurisdiction"] == "Western Australia" or event["source_family_id"].startswith("WA-")
        if is_wa and any(item.startswith(("NER-", "NERR-", "NERL-")) for item in comparators):
            failures.append(f"WA event is routed to a national energy rule comparator: {link['event_id']}")
        if "victorian-energy-upgrades" in link["issue_families"] and "VIC-ERCP-V6-2026-08-29" in comparators:
            failures.append(f"VEU event is routed to the retail code: {link['event_id']}")
        if "WEM-RULES-CURRENT-2026-08-29" in comparators and not is_wa:
            failures.append(f"Non-WA event is routed to WEM rules: {link['event_id']}")

    ambiguous = route_question(
        "A retailer plans to disconnect a life-support customer tomorrow. Can it proceed?",
        as_of="2026-08-29",
    )
    if ambiguous["route_state"] != "needs-applicability-input" or "jurisdiction" not in ambiguous["missing_material_inputs"]:
        failures.append("Applicability router does not block an ambiguous life-support disconnection question.")
    routed = route_question(
        "Can a Victorian retailer disconnect a life-support customer tomorrow?",
        as_of="2026-08-29",
    )
    if routed["route_state"] != "routed" or routed["jurisdiction_candidates"] != ["Victoria"]:
        failures.append("Applicability router does not route an explicit Victorian retail question.")
    expected_victorian_routes = [
        "VIC-ERCP-V6-LIFE-SUPPORT-2026-08-29",
        "VIC-ERCP-V6-DISCONNECTION-2026-08-29",
    ]
    if routed["provision_route_ids"] != expected_victorian_routes:
        failures.append("Applicability router does not select the Victorian clause-family routes.")
    stale = route_question(
        "Can a Victorian retailer disconnect a life-support customer tomorrow?",
        as_of="2026-09-04",
    )
    if not stale["requires_live_version_check"]:
        failures.append("Applicability router does not require a live check after the knowledge baseline.")

    _, _, raw_results = double_search(
        root / "data" / "search-index.sqlite3",
        "ENGIE Victoria family violence reporting failures",
        jurisdiction="Victoria",
        as_of="2026-08-29",
        limit=5,
    )
    engines = {row.get("retrieval_engine") for result_set in raw_results for row in result_set}
    if engines != {"sqlite-fts5", "canonical-json-memory-scan"}:
        failures.append(f"Double search is not using two independent retrieval engines: {sorted(engines)}")

    brief_path = root / "review" / "results" / "victoria-disconnection-operational-brief.json"
    if brief_path.exists():
        brief = read_json(brief_path)
        if brief["operational_release_state"] != "pending-human-control-approval" or brief["may_execute"] is not False:
            failures.append("Operational brief does not preserve the accountable human approval gate.")
        if not brief["controls"] or not brief["official_source_spans"] or not brief["historical_case_examples"]:
            failures.append("Operational brief lacks controls, official source spans or historical case examples.")

    freshness = read_json(root / "data" / "source-freshness-report.json")
    if freshness["provision_source_count"] != len([p for p in provisions["provisions"] if p["status"] != "future-at-baseline"]):
        failures.append("Source-freshness report does not cover every non-future provision route.")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    failures = validate(root)
    if failures:
        print(f"Accuracy-foundation validation failed with {len(failures)} issue(s):")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("Accuracy-foundation validation passed.")
    print("Verified source bytes, canonical URL coverage, obligation parity, temporal routing and fail-closed applicability.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
