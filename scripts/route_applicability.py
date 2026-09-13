#!/usr/bin/env python3
"""Deterministic intake gate for jurisdiction, actor, activity and answer date."""

from __future__ import annotations

import argparse
from datetime import date
import json
import re


KNOWLEDGE_BASELINE = "2026-08-29"

JURISDICTION_PATTERNS = [
    # Only the territory abbreviation is case-sensitive; "Act" is a statute word.
    ("Australian Capital Territory", r"(?-i:\bACT\b)|Australian Capital Territory"),
    ("New South Wales", r"\bNSW\b|New South Wales"),
    ("Northern Territory", r"\bNT\b|Northern Territory"),
    ("Queensland", r"\bQLD\b|Queensland"),
    ("South Australia", r"\bSA\b|South Australia"),
    ("Tasmania", r"\bTAS\b|Tasmania"),
    ("Victoria", r"\bVIC\b|Victoria(?:n)?"),
    ("Western Australia", r"\bWA\b|Western Australia|\bWEM\b"),
    ("National Electricity Market", r"National Electricity Market|\bNEM\b|National Electricity Rules|\bNER\b|AEMO"),
    ("NECF jurisdictions", r"\bNECF\b|National Energy Retail (?:Law|Rules)|\bNERL\b|\bNERR\b"),
    ("Commonwealth", r"Commonwealth|Australian Consumer Law|\bACL\b|Clean Energy Regulator|\bCER\b|ACCC|ACMA"),
]

ACTOR_PATTERNS = [
    ("retailer", r"\bretailer\b|energy seller|retail business"),
    ("distributor or network service provider", r"\bdistributor\b|network service provider|\bDNSP\b|\bTNSP\b|network operator"),
    ("generator or integrated resource provider", r"\bgenerator\b|generating system|integrated resource provider|power station|solar farm|wind farm"),
    ("battery or BESS operator", r"\bBESS\b|\bBDU\b|\bbatter(?:y|ies)\b|energy storage"),
    ("electrical contractor or worker", r"electrician|electrical contractor|installer|electrical worker"),
    ("embedded network operator or exempt seller", r"embedded network|exempt seller|on-seller"),
    ("customer", r"\bcustomer\b|consumer|pensioner|account holder"),
    ("WEM participant", r"WEM participant|market participant.*WEM"),
]

ACTIVITY_PATTERNS = [
    ("disconnection", r"disconnect|de-energ"),
    ("life-support protection", r"life[ -]?support|medical equipment"),
    ("payment difficulty and hardship", r"hardship|payment difficult|financial difficult|arrears|payment plan"),
    ("family violence assistance", r"family violence|domestic violence|affected customer"),
    ("billing and payment", r"bill|charge|refund|payment|debt collect|centrepay"),
    ("marketing and consent", r"market|advertis|represent|consent|telemarket|spam|transfer"),
    ("metering", r"meter|metrology|NMI"),
    ("bidding and dispatch", r"bid|rebid|dispatch"),
    ("FCAS", r"\bFCAS\b"),
    ("PASA", r"\bPASA\b"),
    ("connection and registration", r"connect|registration|authorisation|licen[cs]e|exemption"),
    ("registration fees", r"registration.{0,20}\bfees?\b|AEMO.{0,20}\bfees?\b|\bFY27\b"),
    ("market settlement", r"\bsettlement\b|\btrading amount\b|\bspot revenue\b"),
    ("safety and incident response", r"safety|incident|shock|electrocut|energised|fire|WHS"),
    ("reporting and records", r"report|record|notify|notification"),
    ("VEU certificate activity", r"\bVEU\b|\bVEET\b|Victorian Energy Upgrades|energy efficiency certificate"),
]

CURRENT_ADVICE = re.compile(
    r"\b(can|may|must|should|required|allowed|compliant|proceed|plan(?:s|ned)?|proposed|tomorrow|today|now|current|go-live|before we)\b",
    re.I,
)
HISTORICAL_INTENT = re.compile(r"\b(what happened|case outcome|penalty imposed|was fined|historical case|on appeal)\b", re.I)
JURISDICTION_SENSITIVE = re.compile(
    r"disconnect|life[ -]?support|hardship|family violence|bill|meter|licen[cs]e|exemption|electrical|safety|environment|connection|retail|customer|ombudsman|VEU|VEET|\bFCAS\b|\bPASA\b",
    re.I,
)


def unique_matches(text: str, patterns: list[tuple[str, str]]) -> list[str]:
    return [label for label, pattern in patterns if re.search(pattern, text, re.I)]


def provision_routes(jurisdictions: list[str], actors: list[str], activities: list[str], as_of: str = KNOWLEDGE_BASELINE) -> list[str]:
    routes: list[str] = []
    actor_text = " ".join(actors).lower()
    activity_text = " ".join(activities).lower()
    jurisdiction_set = set(jurisdictions)
    retail_actor = any(term in actor_text for term in ("retailer", "distributor", "network service", "exempt seller"))
    if "Victoria" in jurisdiction_set and retail_actor:
        victoria_routes = (
            ("payment difficulty", "VIC-ERCP-V6-PAYMENT-DIFFICULTY-2026-08-29"),
            ("family violence", "VIC-ERCP-V6-FAMILY-VIOLENCE-2026-08-29"),
            ("life-support", "VIC-ERCP-V6-LIFE-SUPPORT-2026-08-29"),
            ("disconnection", "VIC-ERCP-V6-DISCONNECTION-2026-08-29"),
        )
        routes.extend(route for marker, route in victoria_routes if marker in activity_text)
        if not routes and any(term in activity_text for term in ("billing", "marketing", "metering")):
            routes.append("VIC-ERCP-V6-2026-08-29")
    necf_states = {
        "Australian Capital Territory", "New South Wales", "Queensland", "South Australia", "Tasmania",
        "NECF jurisdictions",
    }
    if jurisdiction_set & necf_states and retail_actor:
        activity_routes = (
            ("life-support", "NERR-LIFE-SUPPORT-CURRENT-2026-08-29"),
            ("disconnection", "NERR-DISCONNECTION-CURRENT-2026-08-29"),
            ("billing", "NERR-BILLING-CURRENT-2026-08-29"),
            ("marketing", "NERL-EIC-CURRENT-2026-08-29"),
        )
        routes.extend(route for marker, route in activity_routes if marker in activity_text)
    if "National Electricity Market" in jurisdiction_set:
        market_routes = (
            ("bidding", "NER-REBIDDING-CURRENT-2026-08-29"),
            ("dispatch", "NER-DISPATCH-CURRENT-2026-08-29"),
            ("fcas", "NER-FCAS-CURRENT-2026-08-29"),
            ("pasa", "NER-PASA-AVAILABILITY-CURRENT-2026-08-29"),
            ("metering", "NER-METERING-CURRENT-2026-08-29"),
        )
        routes.extend(route for marker, route in market_routes if marker in activity_text)
        if as_of >= '2026-09-04':
            replacements = {
                'NER-REBIDDING-CURRENT-2026-08-29': 'NER-BIDDING-V254-2026-09-04',
                'NER-DISPATCH-CURRENT-2026-08-29': 'NER-DISPATCH-V254-2026-09-04',
            }
            routes = [replacements.get(route, route) for route in routes]
            battery_actor = any(term in actor_text for term in ('battery', 'bess', 'bidirectional'))
            if battery_actor and 'connection and registration' in activity_text:
                routes.append('NER-BDU-REGISTRATION-V254-2026-09-04')
            if 'settlement' in activity_text:
                routes.append('NER-SETTLEMENT-V254-2026-09-04')
            if 'registration fees' in activity_text:
                routes.extend(('AEMO-REGISTRATION-FEES-FY27', 'AEMO-REGISTRATION-INVOICING-FY27'))
    return list(dict.fromkeys(routes))


def route_question(
    question: str,
    *,
    jurisdiction: str | None = None,
    actor: str | None = None,
    activity: str | None = None,
    as_of: str | None = None,
    knowledge_baseline: str = KNOWLEDGE_BASELINE,
) -> dict:
    as_of = as_of or date.today().isoformat()
    jurisdictions = [jurisdiction] if jurisdiction else unique_matches(question, JURISDICTION_PATTERNS)
    actors = [actor] if actor else unique_matches(question, ACTOR_PATTERNS)
    activities = [activity] if activity else unique_matches(question, ACTIVITY_PATTERNS)
    # Historical context must not disable gates for a simultaneous operational request.
    current_advice = bool(CURRENT_ADVICE.search(question))
    historical_intent = bool(HISTORICAL_INTENT.search(question))
    missing: list[str] = []
    reasons: list[str] = []

    if current_advice and JURISDICTION_SENSITIVE.search(question) and not jurisdictions:
        missing.append("jurisdiction")
        reasons.append("The requested operational answer changes between the NEM/NECF and state or territory regimes.")
    if len(jurisdictions) > 1:
        missing.append("single applicable jurisdiction or an explicit cross-jurisdiction comparison")
        reasons.append("Multiple legal regimes were detected and cannot be collapsed into one operative rule.")
    if current_advice and not actors:
        missing.append("regulated actor role")
        reasons.append("The duty may attach to a retailer, distributor, generator, contractor, exempt seller or another role.")
    if current_advice and not activities:
        missing.append("regulated activity")
        reasons.append("An operative obligation cannot be selected without the proposed or completed activity.")

    state = "needs-applicability-input" if missing else "routed"
    routes = provision_routes(jurisdictions, actors, activities, as_of=as_of) if state == "routed" else []
    return {
        "route_state": state,
        "answer_as_of": as_of,
        "knowledge_baseline": knowledge_baseline,
        "temporal_intent": "current-or-prospective-advice" if current_advice else "historical-or-descriptive",
        "temporal_sub_intents": {
            "historical": historical_intent,
            "current_or_prospective": current_advice,
        },
        "jurisdiction_candidates": jurisdictions,
        "actor_candidates": actors,
        "activity_candidates": activities,
        "provision_route_ids": routes,
        "provision_route_status": "clause-family-route-exact-subclause-facts-required" if routes else "no-deterministic-provision-route",
        "missing_material_inputs": missing,
        "requires_live_version_check": as_of > knowledge_baseline and current_advice,
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--jurisdiction")
    parser.add_argument("--actor")
    parser.add_argument("--activity")
    parser.add_argument("--as-of")
    args = parser.parse_args()
    result = route_question(
        args.question,
        jurisdiction=args.jurisdiction,
        actor=args.actor,
        activity=args.activity,
        as_of=args.as_of,
    )
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result["route_state"] == "routed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
