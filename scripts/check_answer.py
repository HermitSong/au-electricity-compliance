#!/usr/bin/env python3
"""Deterministically check a claim-addressable draft against indexed evidence."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path

from packet_contract import POLICY_VERSION, validate_packet


FINAL_LANGUAGE = re.compile(r"\b(contravened|breached|liable|found guilty|court found|was fined|penalty was imposed)\b", re.I)
CURRENT_LANGUAGE = re.compile(r"\b(current|currently|now|must|required|prohibited|as at|as of)\b", re.I)
JUDICIAL_FINAL_STATUS = re.compile(r"final-court|final-conviction|final-on-appeal|final-sentence|conviction", re.I)
CURRENT_SUPPORT_STATUSES = {
    "current-at-baseline",
    "current-at-baseline-appellate-control",
}
LOCAL_SNAPSHOT_STATUSES = {"bundled-immutable-copy", "captured-immutable-copy"}


def resolve_claim_type(claim: dict) -> str:
    return claim.get('claim_type') or ('current-law' if CURRENT_LANGUAGE.search(str(claim.get('text', ''))) else 'historical-fact')


def get_evidence(connection: sqlite3.Connection, evidence_id: str) -> dict | None:
    connection.row_factory = sqlite3.Row
    row = connection.execute("SELECT * FROM documents WHERE evidence_id = ?", (evidence_id,)).fetchone()
    return dict(row) if row else None


def check_draft(root: Path, draft: dict, packet: dict | None = None, database: Path | None = None) -> dict:
    database = database or root / "data" / "search-index.sqlite3"
    packet_ids = {item["evidence_id"]: item for item in packet.get("evidence", [])} if packet else None
    errors = []
    warnings = []
    reports = []
    claims = draft.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("Draft must contain a non-empty claims array.")
        claims = []

    current_claims = any(resolve_claim_type(claim) == 'current-law' for claim in claims)
    packet_errors = validate_packet(packet, root, draft) if current_claims else []
    binding_path = root / 'data/provision-source-bindings.json'
    bindings = {row['provision_id']: row for row in json.loads(binding_path.read_text(encoding='utf-8-sig'))['bindings']} if binding_path.exists() else {}
    connection = sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)
    try:
        for index, claim in enumerate(claims, 1):
            claim_id = claim.get("claim_id") or f"claim-{index}"
            text = str(claim.get("text", "")).strip()
            claim_type = resolve_claim_type(claim)
            evidence_ids = claim.get("evidence_ids") or []
            claim_errors = list(packet_errors) if claim_type == 'current-law' else []
            claim_warnings = []
            if not text:
                claim_errors.append("Claim text is empty.")
            if not evidence_ids:
                claim_errors.append("Material claim has no evidence IDs.")
            evidence = []
            for evidence_id in evidence_ids:
                row = get_evidence(connection, evidence_id)
                if row is None:
                    claim_errors.append(f"Unknown evidence ID: {evidence_id}")
                    continue
                evidence.append(row)
                if packet_ids is not None:
                    if evidence_id not in packet_ids:
                        claim_errors.append(f"Evidence was not present in the frozen packet: {evidence_id}")
                    elif packet_ids[evidence_id]["sha256"] != row["sha256"]:
                        claim_errors.append(f"Evidence checksum changed after packet creation: {evidence_id}")
                if row["doc_type"] in {"enforcement-event", "technical-event", "provision-version", "official-source-span"}:
                    if not row["official_url"] or not row["official_url"].startswith("https://"):
                        claim_errors.append(f"Controlling evidence lacks an HTTPS official URL: {evidence_id}")

            if claim_type == "current-law":
                current_provisions = [
                    row for row in evidence
                    if row["doc_type"] == "provision-version"
                    and row["status"] in CURRENT_SUPPORT_STATUSES
                ]
                if not current_provisions:
                    claim_errors.append(
                        "Current-law claim lacks a provision-version citation approved for current-law support; "
                        "version-check, transition-check and comparator-only records require live review."
                    )
                for provision in current_provisions:
                    canonical_binding = bindings.get(provision['evidence_id'].removeprefix('provision:'), {})
                    if not canonical_binding.get('supports_current_law_drafting', False):
                        claim_errors.append(f"Canonical provision binding is not approved for current-law drafting: {provision['evidence_id']}")
                    supplied_binding = (packet_ids or {}).get(provision['evidence_id'], {}).get('provision_source_binding')
                    if supplied_binding != canonical_binding:
                        claim_errors.append(f"Packet binding differs from the canonical reviewed binding: {provision['evidence_id']}")
                if packet is not None and packet.get("release_state") != "ready-for-grounded-drafting":
                    claim_errors.append(
                        f"Current-law claim uses a packet with non-release state: {packet.get('release_state')}."
                    )
                if packet is not None:
                    routed_ids = {
                        f"provision:{provision_id}"
                        for provision_id in packet.get("applicability", {}).get("provision_route_ids", [])
                    }
                    unrelated = sorted(
                        row["evidence_id"] for row in current_provisions
                        if row["evidence_id"] not in routed_ids
                    )
                    if unrelated:
                        claim_errors.append(
                            "Current-law claim cites a provision outside the deterministic applicability route: "
                            + ", ".join(unrelated)
                        )
                source_span_urls = {url for row in evidence if row['doc_type'] == 'official-source-span'
                                    for url in (row['related_official_url'], row['official_url']) if url}
                missing_source_spans = sorted({row["official_url"] for row in current_provisions} - source_span_urls)
                if missing_source_spans:
                    claim_errors.append(
                        "Current-law claim lacks an addressable official-source span for: "
                        + ", ".join(missing_source_spans)
                    )
                if packet_ids is not None:
                    cited_source_span_ids = {
                        row["evidence_id"] for row in evidence if row["doc_type"] == "official-source-span"
                    }
                    for row in current_provisions:
                        packet_item = packet_ids.get(row["evidence_id"], {})
                        artifact = packet_item.get("source_artifact", {})
                        if artifact.get("snapshot_status") not in LOCAL_SNAPSHOT_STATUSES:
                            claim_errors.append(
                                f"Current-law source is not bound to an immutable local snapshot: {row['evidence_id']}"
                            )
                        if packet_item.get("temporal_link_candidate_only"):
                            claim_errors.append(
                                f"Current-law support was added only by an unapproved candidate temporal link: {row['evidence_id']}"
                            )
                        binding = packet_item.get("provision_source_binding", {})
                        if not binding.get("supports_current_law_drafting", False):
                            claim_errors.append(
                                f"Current-law provision lacks a verified clause-level source binding: {row['evidence_id']}"
                            )
                        elif not cited_source_span_ids.intersection(binding.get("source_span_ids", [])):
                            claim_errors.append(
                                f"Current-law claim does not cite a source span bound to: {row['evidence_id']}"
                            )
                if any(row["status"] == "future-at-baseline" for row in evidence):
                    claim_errors.append("Current-law claim cites a future provision version.")
                if any(row["temporal_classification"] == "quashed-or-overturned" for row in evidence):
                    claim_errors.append("Current-law claim cites a quashed or overturned proposition.")

            judicial_text = text
            if claim_type == 'current-law' and not claim_errors:
                generic_roles = re.compile(
                    r'\b(?:the\s+)?intermediary\s+and\s+(?:the\s+)?applicant\s+(?:are|will\s+be)\s+'
                    r'jointly\s+and\s+severally\s+liable\b', re.I)
                has_statutory_text = any(
                    row['doc_type'] == 'official-source-span'
                    and 'jointly and severally liable' in ' '.join(row['body'].lower().split())
                    for row in evidence)
                if has_statutory_text:
                    # A source-bound allocation between generic legal roles is
                    # not a finding that a named party committed a breach.
                    judicial_text = generic_roles.sub('the stated statutory allocation applies', judicial_text)
            if FINAL_LANGUAGE.search(judicial_text):
                judicial_support = [
                    row for row in evidence
                    if JUDICIAL_FINAL_STATUS.search(row["status"] or "")
                    and row["temporal_classification"] not in {
                        "technical-not-authority", "pending-or-non-final", "quashed-or-overturned"
                    }
                ]
                if not judicial_support:
                    claim_errors.append(
                        "Judicial liability language is unsupported. Notices, undertakings, suspensions, "
                        "investigations and technical events are not court findings or admissions."
                    )

            if any(row["temporal_classification"] == "superseded-or-old-rule" for row in evidence):
                claim_warnings.append("Historical old-rule evidence is cited; state the historical date and current comparator explicitly.")
            if any(row["coverage_status"] == "archive-gap" for row in evidence):
                claim_warnings.append("Cited source family has a disclosed archive gap; do not claim corpus completeness.")

            errors.extend(f"{claim_id}: {item}" for item in claim_errors)
            warnings.extend(f"{claim_id}: {item}" for item in claim_warnings)
            reports.append({
                "claim_id": claim_id,
                "claim_type": claim_type,
                "evidence_ids": evidence_ids,
                "passed": not claim_errors,
                "errors": claim_errors,
                "warnings": claim_warnings,
            })
    finally:
        connection.close()

    report = {
        "schema_version": "1.0",
        "validation_policy": POLICY_VERSION,
        "passed": not errors,
        "blocking_error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "claim_reports": reports,
        "human_review_required": "This checker validates deterministic invariants, not semantic entailment. An independent reviewer must compare every claim with the cited text and repeat the search.",
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft", type=Path, help="JSON file with question and claims[].")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--database", type=Path)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    draft = json.loads(args.draft.read_text(encoding='utf-8-sig'))
    packet = json.loads(args.packet.read_text(encoding='utf-8-sig')) if args.packet else None
    report = check_draft(args.root.resolve(), draft, packet, args.database)
    report.update(draft=str(args.draft), packet=str(args.packet) if args.packet else None)
    rendered = json.dumps(report, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote check report to {args.output}")
        print(f"Passed: {report['passed']}")
    else:
        print(rendered, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
