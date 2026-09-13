#!/usr/bin/env python3
"""Build deterministic candidate rule links and temporal warnings for every event."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


BASELINE_DATE = "2026-08-29"

ISSUE_RULES = [
    ("victorian-energy-upgrades", r"\bveu\b|\bveet\b|victorian energy upgrades|victorian energy efficiency certificate"),
    ("life-support", r"life[ -]?support|medical equipment"),
    ("family-violence", r"family violence|domestic violence"),
    ("hardship-payment-difficulty", r"hardship|payment difficulty|payment plan|capacity to pay|financial difficulty"),
    ("disconnection", r"disconnect|de-energ|re-energ|interruption notice"),
    ("explicit-informed-consent", r"explicit informed consent|\beic\b|without consent|customer transfer"),
    ("billing-overcharging-centrepay", r"centrepay|overcharg|billing|\bbill\b|refund|credit balance|pay(?:ment)? credit|feed.in credit|late.payment fee|processing fee|prohibited fee|notified price|charged price|daily supply charge|undercharg"),
    ("telemarketing-spam", r"telemarket|do not call|spam act|commercial electronic message|unsolicited call"),
    ("renewable-energy-certificates", r"renewable energy \(electricity\) (?:act|regulations)|small.scale technology certificate|\bstcs?\b|\bsres\b|large.scale generation certificate|\blgcs?\b|rec registry|improper creation of certificates|registered agent"),
    ("marketing-pricing-representations", r"mislead|representation|advertis|price information|best offer|default market offer|greenpower|renewable energy certificate|discount claim|electricity retail code|price cap|solar sharer"),
    ("contract-notices", r"contract end|fixed term|benefit change|rule 48\b"),
    ("wholesale-bidding-rebidding", r"\brebid|\bbidding|bid reason|good faith|false or misleading bid|offer price"),
    ("dispatch-instructions", r"dispatch instruction|failed to follow dispatch|dispatch compliance|generation dispatch offer|offer capability"),
    ("fcas", r"\bfcas\b|frequency control ancillary|ancillary service"),
    ("generator-performance-standards", r"performance standard|protection setting|ride.through|lvrt|registered performance|generating system model"),
    ("availability-information", r"\bpasa\b|available capacity|availability information|availability submission|capability offer"),
    ("metering", r"metering|meter data|smart meter|metrology|nmi|estimated read"),
    ("ring-fencing", r"ring.fenc"),
    ("wem-market-conduct", r"wholesale electricity market rules|\bwem\b|trading interval|short term energy market|stem"),
    ("ombudsman-membership", r"ombudsman.+member|member of the energy and water ombudsman|section 112\(2\)"),
    ("authorisation-exemption", r"authorisation|authorization|licen[cs]e|exemption|unlicensed|registration|registered with|exempted"),
    ("reporting-recordkeeping", r"reporting|reportable|record.keep|notification failure|late notification|information requirement|failed to provide information|market performance data|auditor approval|audit approval|auditor.general|audited its"),
    ("electrical-safety-licensing", r"electric shock|electrocut|electrical work|electrical safety|electrician|live conductor|energised conductor|unsafe energisation|powerline|power line|electrical licence"),
    ("work-health-safety", r"work health and safety|occupational safety|occupational health|safe work|worksafe|workplace|employee|worker|fall from|crane"),
    ("environmental", r"environment|pollution|contaminat|emission|planning approval|vegetation clear|bushfire|fire prevention"),
    ("privacy-cyber", r"privacy|personal information|cyber|security incident|data breach|critical infrastructure"),
    ("jurisdictional-wholesale-pricing", r"wholesale contract regulatory instrument|regulated weekly wholesale|wholesale pricing|wholesale confirmations"),
    ("power-system-security", r"system black|power system|market suspension|transmission fault|interconnector trip|tower outage|network reliability|supply emergency"),
]

COMPARATORS = {
    "victorian-energy-upgrades": ["VIC-VEU-CURRENT-2026-08-29"],
    "life-support": ["NERR-LIFE-SUPPORT-CURRENT-2026-08-29"],
    "family-violence": ["NERR-HARDSHIP-CURRENT-2026-08-29"],
    "hardship-payment-difficulty": ["NERR-HARDSHIP-CURRENT-2026-08-29"],
    "disconnection": ["NERR-DISCONNECTION-CURRENT-2026-08-29"],
    "explicit-informed-consent": ["NERL-EIC-CURRENT-2026-08-29"],
    "billing-overcharging-centrepay": ["NERR-BILLING-CURRENT-2026-08-29"],
    "telemarketing-spam": ["DNCR-SPAM-CURRENT-2026-08-29"],
    "renewable-energy-certificates": ["CER-RET-CURRENT-2026-08-29"],
    "marketing-pricing-representations": ["ACL-ENERGY-MARKETING-CURRENT-2026-08-29"],
    "contract-notices": ["NERR-CONTRACT-NOTICES-CURRENT-2026-08-29"],
    "wholesale-bidding-rebidding": ["NER-REBIDDING-CURRENT-2026-08-29"],
    "dispatch-instructions": ["NER-DISPATCH-CURRENT-2026-08-29"],
    "fcas": ["NER-FCAS-CURRENT-2026-08-29"],
    "generator-performance-standards": ["NER-GPS-CURRENT-2026-08-29"],
    "availability-information": ["NER-PASA-AVAILABILITY-CURRENT-2026-08-29"],
    "metering": ["NER-METERING-CURRENT-2026-08-29"],
    "ring-fencing": ["AER-RING-FENCING-CURRENT-2026-08-29"],
    "wem-market-conduct": ["WEM-RULES-CURRENT-2026-08-29"],
    "authorisation-exemption": ["ENERGY-LICENSING-CURRENT-2026-08-29"],
    "ombudsman-membership": ["NERL-OMBUDSMAN-MEMBERSHIP-CURRENT-2026-08-29"],
    "reporting-recordkeeping": ["REPORTING-RECORDKEEPING-CURRENT-2026-08-29"],
    "electrical-safety-licensing": ["JURISDICTION-ELECTRICAL-SAFETY-CURRENT-2026-08-29"],
    "work-health-safety": ["JURISDICTION-WHS-CURRENT-2026-08-29"],
    "environmental": ["JURISDICTION-ENVIRONMENT-CURRENT-2026-08-29"],
    "privacy-cyber": [],
    "jurisdictional-wholesale-pricing": ["JURISDICTION-WHOLESALE-RULES-CURRENT-2026-08-29"],
    "power-system-security": ["POWER-SYSTEM-SECURITY-CURRENT-2026-08-29"],
    "other": [],
}

NON_FINAL_STATUSES = {
    "proceedings-allegations-only",
    "ongoing-non-final",
    "active-action",
    "non-final",
}


def read_jsonl(path: Path) -> list[dict]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return records


def classify_issue_families(event: dict) -> list[str]:
    text = " ".join(
        str(event.get(field, ""))
        for field in (
            "issue",
            "outcome",
            "instrument_or_rule",
            "case_status_note",
            "electricity_relevance",
        )
    ).lower()
    families = [family for family, pattern in ISSUE_RULES if re.search(pattern, text, re.I)]
    source = str(event.get("source_family_id", ""))
    jurisdiction = str(event.get("jurisdiction", "")).lower()
    is_wa = "western australia" in jurisdiction or source.startswith("WA-")
    is_veu = bool(re.search(r"\bveu\b|\bveet\b|victorian energy upgrades|victorian energy efficiency certificate", text, re.I))

    # Market names, ordinary English and safety facts share dangerous keywords.
    # Apply jurisdiction and source constraints before creating legal edges.
    if not is_wa:
        families = [family for family in families if family != "wem-market-conduct"]
    elif "wem-market-conduct" in families and not (
        source in {"WA-ERA-WEM-REGISTERS", "WA-AEMO-WEM-SYSTEM-MANAGEMENT"}
        or re.search(r"wholesale electricity market|electricity system and market rules|\bwem\b|short term energy market|\bstem\b", text, re.I)
    ):
        families = [family for family in families if family != "wem-market-conduct"]
    safety_source = any(token in source for token in ("WORKSAFE", "SAFEWORK", "OWHSP", "ENERGY-SAFE"))
    retail_context = bool(re.search(
        r"customer|retailer|retail account|nerr|nerl|life.support|payment plan|bill|premises disconnection",
        text,
        re.I,
    ))
    if safety_source and not retail_context:
        families = [family for family in families if family not in {
            "hardship-payment-difficulty", "disconnection", "authorisation-exemption",
            "marketing-pricing-representations",
        }]
    if "disconnection" in families and not retail_context and any(
        family in families for family in ("electrical-safety-licensing", "work-health-safety")
    ):
        families = [family for family in families if family != "disconnection"]
    if source == "NT-UC-ANNUAL-COMPLIANCE":
        families = [family for family in families if family != "wem-market-conduct"]
    if source == "AU-AER-COMPLIANCE" and retail_context and not re.search(
        r"electric shock|electrocut|electrical work|electrical safety|live conductor|energised conductor|unsafe energisation",
        text,
        re.I,
    ):
        families = [family for family in families if family != "electrical-safety-licensing"]
    if is_veu:
        families = [family for family in families if family not in {
            "victorian-retail-customer-protection", "life-support", "family-violence",
            "hardship-payment-difficulty", "disconnection", "billing-overcharging-centrepay",
            "explicit-informed-consent",
        }]
        if "victorian-energy-upgrades" not in families:
            families.insert(0, "victorian-energy-upgrades")
    if event.get("event_type") == "technical-event":
        allowed = {
            "power-system-security", "generator-performance-standards", "fcas",
            "dispatch-instructions", "availability-information", "reporting-recordkeeping",
        }
        if is_wa and (
            source in {"WA-ERA-WEM-REGISTERS", "WA-AEMO-WEM-SYSTEM-MANAGEMENT"}
            or re.search(r"wholesale electricity market|electricity system and market rules|\bwem\b", text, re.I)
        ):
            allowed.add("wem-market-conduct")
        if re.search(r"environmental regulator|environmental protection|pollution offence|contaminated land", text, re.I):
            allowed.add("environmental")
        families = [family for family in families if family in allowed]
        if "power-system-security" not in families:
            families.append("power-system-security")
    if source == "AU-CER-COMPLIANCE" and "renewable-energy-certificates" in families:
        families = [family for family in families if family in {"renewable-energy-certificates", "reporting-recordkeeping"}]
    if not families or families == ["other"]:
        if source in {"VIC-ENERGY-SAFE-PROSECUTIONS", "WA-BUILDING-ENERGY-STATEMENTS"}:
            families = ["electrical-safety-licensing"]
        elif source == "QLD-EWOQ-ANNUAL":
            families = ["billing-overcharging-centrepay"]
        elif event.get("event_type") == "technical-event":
            families = ["power-system-security"]
    return families or ["other"]


def temporal_classification(event: dict, families: list[str]) -> tuple[str, str | None, str]:
    status = str(event.get("status", "")).lower()
    note = str(event.get("case_status_note", "")).lower()
    source = str(event.get("source_family_id", ""))
    event_date = str(event.get("event_date", ""))
    text = " ".join((note, str(event.get("instrument_or_rule", "")).lower(), str(event.get("issue", "")).lower()))

    if event.get("event_type") == "technical-event" or "technical event" in note or "technical report" in status:
        return "technical-not-authority", "technical-event-not-contravention", "Technical evidence may explain controls but cannot establish a contravention without a separate official finding."
    if status == "appeal-allowed":
        return "appellate-control", "displaces-earlier-outcome", "This record describes an allowed appeal, not an appellate judgment itself set aside. Consult the dated case chain for later activity; current applicability and finality still require verification."
    if (
        status == "quashed-on-appeal"
        and "controlling appellate" in note
        and "first-instance outcome displaced" not in note
    ):
        return "appellate-control", "displaces-earlier-outcome", "This appellate event is the current controlling treatment of the earlier outcome at the baseline; the earlier first-instance proposition is displaced."
    if status == "quashed-on-appeal" or "quashed" in note or "overturned" in note:
        return "quashed-or-overturned", "appellate-displacement", "The displaced first-instance proposition must not be used as current authority; use the later appellate outcome."
    if status in NON_FINAL_STATUSES or re.search(r"proceeding|allegation|pending|investigation", status):
        return "pending-or-non-final", "non-final-proceeding", "Allegations and requested orders are not findings of contravention."
    if "expired" in status:
        return "superseded-or-old-rule", "expired-administrative-action", "The administrative action has expired; verify current eligibility, registration and the current governing provisions separately."
    if "old-rule" in text or "supersed" in text or "replaced by" in text:
        return "superseded-or-old-rule", "historical-rule-conflict", "The event remains historical evidence, but present guidance must use the current comparator and any transition rule."
    if "wholesale-bidding-rebidding" in families and event_date < "2016-07-01":
        return "superseded-or-old-rule", "historical-rule-conflict", "The pre-1 July 2016 bidding-in-good-faith framework is not the current objective bidding and rebidding test."
    if source == "WA-WORKSAFE-PROSECUTIONS" and event_date < "2022-03-31":
        return "superseded-or-old-rule", "historical-rule-conflict", "The event applies the former WA occupational safety framework; current WA WHS legislation commenced on 31 March 2022."
    if source == "VIC-ESC-PENALTIES" and event_date < "2022-03-01":
        return "superseded-or-old-rule", "historical-rule-conflict", "The event predates the remade Victorian Energy Retail Code of Practice and requires a current-code comparator."
    if re.search(r"\brees\b", text) and event_date < "2021-01-01":
        return "superseded-or-old-rule", "historical-rule-conflict", "The South Australian REES framework was replaced by REPS after 2020."
    return "historical-event-current-comparator-required", None, "Use the event's historical instrument for what occurred, then verify the separately linked current comparator for present guidance."


def comparator_ids(event: dict, families: list[str]) -> list[str]:
    ids: list[str] = []
    source = str(event.get("source_family_id", ""))
    jurisdiction = str(event.get("jurisdiction", "")).lower()
    is_wa = "western australia" in jurisdiction or source.startswith("WA-")
    is_veu = "victorian-energy-upgrades" in families
    is_victoria_retail = not is_veu and (
        source == "VIC-ESC-PENALTIES"
        and any(f in families for f in {
            "life-support", "family-violence", "hardship-payment-difficulty", "disconnection",
            "explicit-informed-consent", "billing-overcharging-centrepay", "marketing-pricing-representations"
        })
    )
    is_necf_retail = any(name in jurisdiction for name in (
        "australian capital territory", "new south wales", "queensland",
        "south australia", "tasmania", "national energy laws", "necf",
    ))
    for family in families:
        for provision_id in COMPARATORS.get(family, []):
            if is_wa and provision_id.startswith(("NER-", "NERR-", "NERL-")):
                continue
            if is_wa and family == "metering":
                provision_id = "WA-METERING-CODE-CURRENT-2026-08-29"
            if is_victoria_retail and provision_id.startswith(("NERR-", "NERL-")):
                continue
            if not is_necf_retail and not is_victoria_retail and provision_id.startswith(("NERR-", "NERL-")):
                continue
            if provision_id not in ids:
                ids.append(provision_id)
    if is_victoria_retail:
        victoria_comparators = {
            "hardship-payment-difficulty": "VIC-ERCP-V6-PAYMENT-DIFFICULTY-2026-08-29",
            "family-violence": "VIC-ERCP-V6-FAMILY-VIOLENCE-2026-08-29",
            "life-support": "VIC-ERCP-V6-LIFE-SUPPORT-2026-08-29",
            "disconnection": "VIC-ERCP-V6-DISCONNECTION-2026-08-29",
        }
        specific = [victoria_comparators[family] for family in families if family in victoria_comparators]
        for provision_id in reversed(specific or ["VIC-ERCP-V6-2026-08-29"]):
            if provision_id not in ids:
                ids.insert(0, provision_id)
    if event.get("source_family_id") == "QLD-QCA-ENERGY-REPORTING" and "QLD-RETAIL-PRICING-CURRENT-2026-08-29" not in ids:
        ids.insert(0, "QLD-RETAIL-PRICING-CURRENT-2026-08-29")
    return ids


def mapping_status(classification: str, comparator_count: int) -> str:
    if classification == "technical-not-authority":
        return "not-applicable-technical-evidence"
    if classification == "quashed-or-overturned":
        return "historical-only-do-not-use-displaced-proposition"
    if classification == "appellate-control":
        return "appellate-control-current-at-baseline"
    if classification == "pending-or-non-final":
        return "not-applicable-no-final-liability"
    if not comparator_count:
        return "needs-reviewed-current-clause-mapping"
    if classification == "superseded-or-old-rule":
        return "historical-only-candidate-comparator-linked"
    return "candidate-comparator-linked-independent-review-required"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "data" / "event-provision-links.jsonl"

    provision_path = root / "data" / "provision-version-register.json"
    provision_data = json.loads(provision_path.read_text(encoding="utf-8-sig"))
    valid_ids = {item["provision_id"] for item in provision_data["provisions"]}

    events = read_jsonl(root / "data" / "enforcement-events-full.jsonl")
    events += read_jsonl(root / "data" / "technical-events-full.jsonl")
    links = []
    for event in events:
        families = classify_issue_families(event)
        classification, conflict, note = temporal_classification(event, families)
        comparators = comparator_ids(event, families)
        unknown = sorted(set(comparators) - valid_ids)
        if unknown:
            raise ValueError(f"Unknown provision comparator(s) for {event['event_id']}: {unknown}")
        links.append({
            "event_id": event["event_id"],
            "event_date": event["event_date"],
            "jurisdiction": event["jurisdiction"],
            "issue_family": families[0],
            "issue_families": families,
            "historical_instrument_or_rule": event["instrument_or_rule"],
            "historical_status": event["status"],
            "temporal_classification": classification,
            "conflict_flag": conflict,
            "current_comparator_ids": comparators,
            "current_mapping_status": mapping_status(classification, len(comparators)),
            "current_authority_note": note,
            "baseline_date": BASELINE_DATE,
            "mapping_method": "deterministic-keyword-and-source-rules-v2",
            "review_status": "candidate-auto-mapped",
            "reviewed_by": None,
            "reviewed_at": None,
            "review_evidence_ids": [],
        })

    links.sort(key=lambda item: (item["event_date"], item["event_id"]))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(item, ensure_ascii=True, separators=(",", ":")) + "\n" for item in links), encoding="utf-8")
    print(f"Wrote {len(links)} event-provision links to {output}")
    print(f"Temporal warnings: {sum(bool(item['conflict_flag']) for item in links)}")
    print(f"Unmapped current comparators: {sum(not item['current_comparator_ids'] for item in links)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
