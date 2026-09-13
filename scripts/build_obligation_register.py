#!/usr/bin/env python3
"""Build a machine-readable obligation and minimum-control register."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CONTROL_CATALOG = {
    "wholesale-bidding-rebidding": ("registered participant", "offers, bids and rebids", "Prevent false, misleading or unsupported bid and rebid submissions.", ["immutable bid history", "reason and decision log", "input validation and escalation record"]),
    "dispatch-instructions": ("scheduled or semi-scheduled participant", "dispatch and directions", "Identify and comply with the applicable instruction or document a valid exception.", ["dispatch target and telemetry", "acknowledgement", "exception and incident record"]),
    "availability-information": ("scheduled participant", "PASA and availability submissions", "Keep availability information accurate, timely and traceable to plant capability.", ["capability record", "outage approval", "submission and change log"]),
    "fcas": ("market ancillary service provider", "FCAS offer and delivery", "Offer and deliver only validated ancillary-service capability.", ["MASS evidence", "enablement and response data", "commissioning record"]),
    "generator-performance-standards": ("generator or integrated resource provider", "connection and plant operation", "Operate to approved performance standards and settings.", ["registered performance standard", "settings register", "model validation and change approval"]),
    "hardship-payment-difficulty": ("retailer", "payment difficulty and hardship", "Identify eligible customers and provide the protections and assistance required by the routed regime.", ["customer status", "capacity assessment", "offer, acceptance and review record"]),
    "family-violence": ("retailer", "family violence assistance", "Protect affected-customer safety, privacy and access to flexible assistance across every customer interaction.", ["safe contact preference", "account access controls", "debt and assistance decision record", "training and disclosure audit trail"]),
    "life-support": ("retailer or distributor", "life-support registration and supply protection", "Reconcile registration and prevent prohibited de-energisation of protected premises.", ["retailer-distributor reconciliation", "customer contact attempts", "protected-site work-order block"]),
    "explicit-informed-consent": ("retailer or sales agent", "customer transfer and contract formation", "Obtain and retain valid explicit informed consent for each regulated transaction.", ["consent record", "identity and authority checks", "transaction-specific disclosure"]),
    "disconnection": ("retailer or distributor", "disconnection and reconnection", "Block disconnection until every routed prerequisite and vulnerability check passes.", ["decision-rules output", "notices", "payment, vulnerability and protected-period checks", "work-order status"]),
    "billing-overcharging-centrepay": ("retailer", "pricing and billing", "Calculate, notify, reconcile and remediate charges under the applicable tariff and customer regime.", ["tariff version", "bill calculation", "change notice", "refund and exception record"]),
    "victorian-retail-customer-protection": ("Victorian retailer or distributor", "Victorian retail customer protection", "Apply the operative Victorian code version and issue-specific clause before action.", ["customer and premises classification", "operative code version", "issue-specific decision evidence"]),
    "marketing-pricing-representations": ("energy business or sales agent", "marketing and pricing representations", "Substantiate every material representation and apply the correct sales-channel controls.", ["approved claim and substantiation", "script or creative version", "consent and channel record"]),
    "telemarketing-spam": ("caller, sender or contracting principal", "telemarketing and electronic messages", "Verify consent, register status, sender identity, calling time and unsubscribe controls.", ["consent evidence", "register wash", "campaign and suppression logs", "contractor audit"]),
    "wem-market-conduct": ("WEM market participant", "WEM offers and trading conduct", "Apply the current WEM rule and procedure to the relevant facility, interval and conduct.", ["offer construction inputs", "trading decision log", "market submission record"]),
    "electrical-safety-licensing": ("electrical duty holder", "electrical work and energisation", "Use licensed workers, approved equipment and verified test and inspection gates.", ["worker licence", "test and inspection record", "certificate", "energisation approval"]),
    "work-health-safety": ("PCBU, employer or officer", "work health and safety", "Eliminate or minimise risk and evidence consultation, competence and due diligence.", ["risk assessment", "SWMS", "competence record", "consultation and verification"]),
    "environmental": ("project owner or operator", "planning and environmental compliance", "Map approvals and prevent work outside conditions or reporting limits.", ["approval pathway", "conditions register", "monitoring and regulator reports"]),
    "authorisation-exemption": ("energy business", "market entry and licensed activity", "Confirm the legal entity, activity and jurisdiction are covered by a current authority or exemption.", ["entity and activity map", "register extract", "conditions register", "renewal calendar"]),
    "metering": ("metering role holder", "metering and market data", "Perform only authorised metering roles and preserve accurate, correctable data lineage.", ["role accreditation", "metrology test", "data lineage", "access and correction log"]),
    "ring-fencing": ("network service provider", "ring-fencing and access", "Prevent discrimination, prohibited information flows and unsupported cost allocation.", ["ring-fencing register", "access controls", "cost allocation", "waiver and annual report"]),
    "reporting-recordkeeping": ("regulated entity", "records and regulator reporting", "Route each report to its exact instrument, period, owner and evidence lineage.", ["source-to-report lineage", "approval", "submission receipt", "retention and correction log"]),
    "contract-notices": ("retailer", "contract and benefit notices", "Send the operative notice with correct timing, content and customer route.", ["contract version", "notice content", "delivery timestamp", "exception record"]),
    "ombudsman-membership": ("retailer, distributor or exempt seller", "ombudsman membership and cooperation", "Maintain required scheme membership and cooperate under the routed law or exemption condition.", ["membership confirmation", "entity and activity scope", "complaint referral record"]),
    "jurisdictional-wholesale-pricing": ("jurisdictional wholesale counterparty", "state wholesale pricing or contracts", "Select and apply the exact local instrument instead of importing NEM bidding rules.", ["jurisdiction route", "operative instrument", "contract and price calculation"]),
    "power-system-security": ("system or market participant", "system security and emergency operations", "Classify the event and comply with the current national or local operating instrument.", ["event chronology", "instruction and response log", "technical data", "incident report"]),
    "renewable-energy-certificates": ("registered person, liable entity or accredited power station", "renewable certificate creation and surrender", "Create, transfer and surrender certificates only from verified eligible activity and data.", ["registration or accreditation", "generation or installation data", "certificate ledger", "claims approval"]),
    "victorian-energy-upgrades": ("VEU accredited person or scheme participant", "VEU activities and certificate creation", "Perform eligible activities and create certificates only from authentic, compliant evidence.", ["accreditation and activity eligibility", "consumer consent and co-payment", "installation evidence", "certificate claim and audit trail"]),
}


def review_status(provision: dict) -> str:
    status = provision["status"]
    if status == "future-at-baseline":
        return "future-not-operative-at-baseline"
    if status in {"current-at-baseline", "current-at-baseline-appellate-control"}:
        return "approved-current-route-at-baseline"
    return "route-only-exact-source-required"


def build_register(root: Path) -> dict:
    provisions = json.loads((root / "data" / "provision-version-register.json").read_text(encoding="utf-8-sig"))
    obligations = []
    for provision in provisions["provisions"]:
        family = provision["issue_family"]
        actor, activity, objective, evidence = CONTROL_CATALOG.get(
            family,
            ("regulated entity", family, "Determine and comply with the exact routed obligation.", ["applicability decision", "operative source text", "execution evidence"]),
        )
        obligations.append({
            "obligation_id": f"OBL-{provision['provision_id']}",
            "provision_id": provision["provision_id"],
            "issue_family": family,
            "instrument": provision["instrument"],
            "provisions": provision["provisions"],
            "jurisdiction": provision["jurisdiction"],
            "valid_from": provision["valid_from"],
            "valid_to": provision["valid_to"],
            "authority_status": provision["status"],
            "review_status": review_status(provision),
            "applicability": {
                "actor_class": actor,
                "regulated_activity": activity,
                "required_inputs": ["legal entity", "actor role", "jurisdiction", "activity", "event or decision date"],
                "decision_rule": "Do not apply this route until all material applicability inputs are resolved against the operative source.",
            },
            "control_objective": objective,
            "minimum_control_evidence": evidence,
            "official_source": provision["official_url"],
            "version_note": provision["version_note"],
        })
    counts: dict[str, int] = {}
    for item in obligations:
        counts[item["review_status"]] = counts.get(item["review_status"], 0) + 1
    return {
        "schema_version": "1.0",
        "baseline_date": provisions["baseline_date"],
        "purpose": "Machine-readable routing from current provision versions to applicability inputs, control objectives and minimum evidence.",
        "release_rule": "Only approved-current-route-at-baseline may support a baseline current-law proposition, and only after applicability is resolved. Later answer dates require live version verification.",
        "obligation_count": len(obligations),
        "review_status_counts": counts,
        "obligations": obligations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "data" / "obligation-register.json"
    data = build_register(root)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Wrote {data['obligation_count']} obligations to {output}")
    print(json.dumps(data["review_status_counts"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
