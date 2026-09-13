#!/usr/bin/env python3
"""Convert an evidence packet into a non-executing enterprise control brief."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from packet_contract import validate_packet, canonical_span_errors, research_original_errors


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    packet = read_json(args.packet)
    rejected_span_errors = canonical_span_errors(packet, root)
    rejected_research_errors = research_original_errors(packet, root)
    register = read_json(root / "data" / "obligation-register.json")
    obligations_by_provision = {item["provision_id"]: item for item in register["obligations"]}
    obligations_by_id = {item["obligation_id"]: item for item in register["obligations"]}
    routed_provision_ids = set(packet.get("applicability", {}).get("provision_route_ids", []))
    selected: dict[str, dict] = {}
    cases = []
    source_spans = []
    for evidence in packet.get("evidence", []):
        evidence_id = evidence["evidence_id"]
        if evidence_id.startswith("provision:"):
            provision_id = evidence_id.removeprefix("provision:")
            obligation = obligations_by_provision.get(provision_id)
            if obligation and provision_id in routed_provision_ids:
                selected[obligation["obligation_id"]] = obligation
        elif evidence_id.startswith("obligation:OBL-"):
            obligation_id = evidence_id.removeprefix("obligation:")
            obligation = obligations_by_id.get(obligation_id)
            if obligation and obligation["provision_id"] in routed_provision_ids:
                selected[obligation_id] = obligation
        elif evidence["doc_type"] in {"enforcement-event", "technical-event"}:
            cases.append({
                "evidence_id": evidence_id,
                "title": evidence["title"],
                "entity": evidence["entity"],
                "event_date": evidence["event_date"],
                "jurisdiction": evidence["jurisdiction"],
                "status": evidence["status"],
                "temporal_classification": evidence["temporal_classification"],
                "official_url": evidence["official_url"],
                "related_official_url": evidence.get("related_official_url"),
                "source_artifact": evidence.get("source_artifact"),
                "use_limit": "Historical example only; verify the current rule and do not overstate procedural status.",
            })
        elif evidence["doc_type"] == "official-source-span":
            source_spans.append({
                "evidence_id": evidence_id,
                "official_url": evidence["official_url"],
                "related_official_url": evidence.get("related_official_url"),
                "locator": evidence.get("source_locator"),
                "snapshot_path": evidence["source_path"],
                "text_sha256": evidence.get("source_text_sha256"),
                "source_snapshot_sha256": evidence.get("source_snapshot_sha256"),
                "binding_role": evidence.get("provision_source_binding_role"),
                "bound_provision_ids": evidence.get("bound_provision_ids", []),
            })

    controls = []
    for obligation in sorted(selected.values(), key=lambda item: item["obligation_id"]):
        controls.append({
            "obligation_id": obligation["obligation_id"],
            "provision_id": obligation["provision_id"],
            "jurisdiction": obligation["jurisdiction"],
            "actor_class": obligation["applicability"]["actor_class"],
            "regulated_activity": obligation["applicability"]["regulated_activity"],
            "control_objective": obligation["control_objective"],
            "minimum_evidence_required": obligation["minimum_control_evidence"],
            "control_owner": None,
            "evidence_provided": [],
            "evidence_status": "not-assessed",
            "professional_approval_status": "not-approved",
            "provision_source_binding": next((
                evidence.get("provision_source_binding")
                for evidence in packet.get("evidence", [])
                if evidence["evidence_id"] == f"provision:{obligation['provision_id']}"
            ), None),
        })

    packet_state = packet["release_state"]
    prerequisites = [
        "Confirm the legal entity, regulated role, jurisdiction, activity, customer or asset class and decision date.",
        "Verify each controlling provision against an addressable official source span current at the decision date.",
        "Assign a control owner and attach the minimum operational evidence for every applicable obligation.",
        "Obtain accountable legal or compliance approval for applicability and any exception before execution.",
        "Retain the approved brief, source hashes, evidence and resulting action in the audit record.",
    ]
    blockers = [] if packet_state == "ready-for-grounded-drafting" else list(packet.get("release_reasons", []))
    blockers.extend('Evidence packet validation: ' + error for error in
                    validate_packet(packet, root, {'question': packet.get('question')}))
    warnings = list(packet.get("release_reasons", [])) if packet_state == "ready-for-grounded-drafting" else []
    if not controls:
        blockers.append("No machine-readable obligation and control route was established from the evidence packet.")
    if not source_spans and packet.get("applicability", {}).get("temporal_intent") == "current-or-prospective-advice":
        blockers.append("No addressable official-source span was retrieved for the proposed current action.")
    operational_state = "pending-human-control-approval" if packet_state == "ready-for-grounded-drafting" and not blockers else "blocked"
    brief = {
        "schema_version": "1.0",
        "brief_id": f"operational:{packet['packet_id']}",
        "question": packet["question"],
        "answer_as_of": packet["answer_as_of"],
        "applicability": packet.get("applicability"),
        "evidence_packet_id": packet["packet_id"],
        "evidence_packet_release_state": packet_state,
        "operational_release_state": operational_state,
        "may_execute": False,
        "blockers": blockers,
        "warnings": warnings,
        "mandatory_prerequisites": prerequisites,
        "controls": controls,
        "historical_case_examples": cases,
        "research_case_chains": packet.get('research_case_chains', {}),
        "case_chain_use_limit": packet.get('case_chain_use_limit'),
        "research_originals": None if rejected_research_errors else packet.get('research_originals'),
        "research_readings": None if rejected_research_errors else packet.get('research_readings'),
        "official_source_spans": [] if rejected_span_errors else source_spans,
        "quarantined_evidence": {
            "rejected_source_spans": source_spans if rejected_span_errors else [],
            "rejected_research_originals": packet.get('research_originals') if rejected_research_errors else None,
            "rejected_research_readings": packet.get('research_readings') if rejected_research_errors else None,
            "reasons": rejected_span_errors + rejected_research_errors,
            "use_limit": "Rejected input retained for inspection only; not admitted source evidence.",
        },
        "decision_record": {
            "accountable_owner": None,
            "legal_or_compliance_approver": None,
            "decision": None,
            "decision_time": None,
            "conditions_or_exceptions": [],
        },
    }
    rendered = json.dumps(brief, indent=2, ensure_ascii=True) + "\n"
    output = args.output
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"Wrote operational brief to {output}")
        print(f"Operational release state: {operational_state}")
    else:
        print(rendered, end="")
    return 0 if operational_state == "pending-human-control-approval" else 2


if __name__ == "__main__":
    raise SystemExit(main())
