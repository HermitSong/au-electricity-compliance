#!/usr/bin/env python3
"""Create a routed, status-aware evidence packet for a separate answer model."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import sqlite3

from double_search_kb import double_search
from case_chains import selected_research_chains
from kb_search import compact_result
from route_applicability import KNOWLEDGE_BASELINE, route_question
from packet_contract import seal_packet, effective_jurisdiction as resolve_effective_jurisdiction, current_release_errors
from search_source_originals import (search_research_originals, AUTHORITY_ROLE, USE_LIMIT,
                                    UNRESOLVED_USE_LIMIT, DATE_USE_LIMIT, APPLICABILITY_USE_LIMIT)
from read_source_originals import expand_research_results
from reviewed_bindings import live_review_errors


CURRENT_SUPPORT_STATUSES = {
    "current-at-baseline",
    "current-at-baseline-appellate-control",
}
LOCAL_SNAPSHOT_STATUSES = {"bundled-immutable-copy", "captured-immutable-copy"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def source_artifact_lookup(root: Path) -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    path = root / "data" / "source-artifact-ledger.jsonl"
    if not path.exists():
        return lookup
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        url = row.get("canonical_url")
        if not url:
            continue
        current = lookup.get(url)
        row_is_local = row["record_type"] == "local-official-snapshot"
        current_is_local = current and current.get("snapshot_status") in LOCAL_SNAPSHOT_STATUSES
        row_retrieved = row.get("retrieved_at") or ""
        current_retrieved = current.get("retrieved_at") if current else ""
        if current is None or (row_is_local and not current_is_local) or (row_is_local and row_retrieved > (current_retrieved or "")):
            lookup[url] = {
                "artifact_id": row["artifact_id"],
                "snapshot_status": row["snapshot_status"],
                "snapshot_path": row["snapshot_path"],
                "source_sha256": row["sha256"],
                "retrieved_at": row["retrieved_at"],
                "provenance_status": row["provenance_status"],
                "provenance_limitations": row["provenance_limitations"],
            }
    return lookup


def provision_binding_lookup(root: Path) -> dict[str, dict]:
    path = root / "data" / "provision-source-bindings.json"
    if not path.exists():
        return {}
    return {item["provision_id"]: item for item in load_json(path)["bindings"]}


def relevant_gaps(root: Path, jurisdiction: str | None, include_all: bool = False) -> list[dict]:
    if not jurisdiction and not include_all:
        return []
    register = load_json(root / "data" / "enforcement-source-register.json")
    source_jurisdiction = {item["id"]: item["jurisdiction"] for item in register["sources"]}
    ledger = load_json(root / "data" / "source-coverage-ledger.json")
    gaps = []
    for review in ledger["source_reviews"]:
        source_id = review["source_family_id"]
        source_location = source_jurisdiction[source_id]
        if jurisdiction and jurisdiction.lower() not in source_location.lower():
            continue
        if review["extraction_status"] == "archive-gap":
            gaps.append({
                "source_family_id": source_id,
                "gap_periods": review["gap_periods"],
                "gap_reason": review["gap_reason"],
            })
    return gaps


def expand_temporal_comparators(
    root: Path,
    database: Path,
    rows: list[dict],
    as_of: str | None,
) -> list[dict]:
    """Append candidate comparators while preserving whether search found them independently."""
    links = {
        row["event_id"]: row
        for row in (
            json.loads(line)
            for line in (root / "data" / "event-provision-links.jsonl").read_text(encoding="utf-8-sig").splitlines()
            if line.strip()
        )
    }
    requested: dict[str, list[str]] = {}
    link_metadata: dict[str, list[dict]] = {}
    for row in rows:
        if row["doc_type"] not in {"enforcement-event", "technical-event"}:
            continue
        event_id = row["evidence_id"].removeprefix("event:")
        link = links.get(event_id)
        if not link:
            continue
        for provision_id in link.get("current_comparator_ids", []):
            evidence_id = f"provision:{provision_id}"
            requested.setdefault(evidence_id, []).append(event_id)
            link_metadata.setdefault(evidence_id, []).append({
                "event_id": event_id,
                "mapping_method": link.get("mapping_method"),
                "review_status": link.get("review_status", "legacy-review-status-unknown"),
            })
    expanded = [dict(row) for row in rows]
    for row in expanded:
        evidence_id = row["evidence_id"]
        if evidence_id in requested:
            row["temporal_link_role"] = "current-comparator-also-independently-retrieved"
            row["linked_from_event_ids"] = sorted(set(requested[evidence_id]))
            row["temporal_link_candidate_only"] = False
            row["temporal_link_metadata"] = link_metadata[evidence_id]
    existing = {row["evidence_id"] for row in expanded}
    missing = [evidence_id for evidence_id in requested if evidence_id not in existing]
    if not missing:
        return expanded

    placeholders = ",".join("?" for _ in missing)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        found = {
            row["evidence_id"]: dict(row)
            for row in connection.execute(
                f"SELECT * FROM documents WHERE evidence_id IN ({placeholders})",
                missing,
            )
        }
    finally:
        connection.close()

    for evidence_id in missing:
        row = found.get(evidence_id)
        if not row:
            continue
        if as_of and row["effective_from"] and row["effective_from"] > as_of:
            continue
        if as_of and row["effective_to"] and row["effective_to"] < as_of:
            continue
        row["issue_families"] = json.loads(row.pop("issue_families_json"))
        row["metadata"] = json.loads(row.pop("metadata_json"))
        row["lexical_score"] = None
        row["rrf_rank"] = len(expanded) + 1
        row["rrf_score"] = 0.0
        row["retrieval_provenance"] = [{
            "search": "candidate-temporal-link",
            "rank": row["rrf_rank"],
            "query": "current comparator",
        }]
        row["temporal_link_role"] = "current-comparator"
        row["linked_from_event_ids"] = sorted(set(requested[evidence_id]))
        row["temporal_link_candidate_only"] = True
        row["temporal_link_metadata"] = link_metadata[evidence_id]
        expanded.append(row)
    return expanded


def expand_applicability_routes(database: Path, rows: list[dict], provision_ids: list[str], as_of: str | None) -> list[dict]:
    if not provision_ids:
        return rows
    requested = {f"provision:{provision_id}" for provision_id in provision_ids}
    expanded = [dict(row) for row in rows]
    existing = {row["evidence_id"] for row in expanded}
    for row in expanded:
        if row["evidence_id"] in requested:
            row["applicability_route_role"] = "deterministic-regime-route"
    missing = sorted(requested - existing)
    if not missing:
        return expanded
    placeholders = ",".join("?" for _ in missing)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        found = {
            row["evidence_id"]: dict(row)
            for row in connection.execute(
                f"SELECT * FROM documents WHERE evidence_id IN ({placeholders})",
                missing,
            )
        }
    finally:
        connection.close()
    for evidence_id in missing:
        row = found.get(evidence_id)
        if not row:
            continue
        if as_of and row["effective_from"] and row["effective_from"] > as_of:
            continue
        if as_of and row["effective_to"] and row["effective_to"] < as_of:
            continue
        row["issue_families"] = json.loads(row.pop("issue_families_json"))
        row["metadata"] = json.loads(row.pop("metadata_json"))
        row["lexical_score"] = None
        row["rrf_rank"] = len(expanded) + 1
        row["rrf_score"] = 0.0
        row["retrieval_provenance"] = [{
            "search": "applicability-router",
            "engine": "deterministic-applicability-router",
            "rank": row["rrf_rank"],
            "query": "resolved jurisdiction, actor and activity",
        }]
        row["applicability_route_role"] = "deterministic-regime-route"
        expanded.append(row)
    return expanded


def expand_verified_source_bindings(root: Path, database: Path, rows: list[dict]) -> list[dict]:
    """Attach exact binding metadata and its immutable source spans."""
    bindings = provision_binding_lookup(root)
    expanded = [dict(row) for row in rows]
    requested_spans: dict[str, list[str]] = {}
    for row in expanded:
        if row["doc_type"] != "provision-version":
            continue
        provision_id = row["evidence_id"].removeprefix("provision:")
        binding = bindings.get(provision_id)
        if not binding:
            continue
        row["provision_source_binding"] = binding
        if row.get("temporal_link_candidate_only") or not binding["supports_current_law_drafting"]:
            continue
        for evidence_id in binding["source_span_ids"]:
            requested_spans.setdefault(evidence_id, []).append(provision_id)
    existing = {row["evidence_id"] for row in expanded}
    missing = sorted(set(requested_spans) - existing)
    if not missing:
        return expanded
    placeholders = ",".join("?" for _ in missing)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        found = {
            row["evidence_id"]: dict(row)
            for row in connection.execute(
                f"SELECT * FROM documents WHERE evidence_id IN ({placeholders})",
                missing,
            )
        }
    finally:
        connection.close()
    for evidence_id in missing:
        row = found.get(evidence_id)
        if not row:
            continue
        row["issue_families"] = json.loads(row.pop("issue_families_json"))
        row["metadata"] = json.loads(row.pop("metadata_json"))
        row["lexical_score"] = None
        row["rrf_rank"] = len(expanded) + 1
        row["rrf_score"] = 0.0
        row["retrieval_provenance"] = [{
            "search": "verified-provision-source-binding",
            "engine": "deterministic-clause-binding",
            "rank": row["rrf_rank"],
            "query": "exact official clause range",
        }]
        row["provision_source_binding_role"] = "exact-official-clause-range"
        row["bound_provision_ids"] = sorted(set(requested_spans[evidence_id]))
        expanded.append(row)
    return expanded


def expand_case_chains(root: Path, database: Path, rows: list[dict], question: str) -> list[dict]:
    chains = selected_research_chains(root, rows, question)
    requested = {'event:' + event_id for chain in chains.values() for event_id in chain['event_ids']}
    for chain in chains.values():
        source_ids = chain.get('source_evidence_ids', [])
        if (not isinstance(source_ids, list) or any(not isinstance(identity, str)
                or not identity.startswith('source-span:') for identity in source_ids)):
            raise ValueError('Case source links must be canonical official source-span identifiers')
        requested.update(source_ids)
    expanded = [dict(row) for row in rows]
    missing = sorted(requested - {row['evidence_id'] for row in expanded})
    if not missing:
        return expanded
    connection = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    try:
        placeholders = ','.join('?' for _ in missing)
        found = {row['evidence_id']: dict(row) for row in connection.execute(
            f'SELECT * FROM documents WHERE evidence_id IN ({placeholders})', missing)}
    finally:
        connection.close()
    if set(found) != set(missing):
        raise ValueError('Case chain references missing canonical event evidence; rebuild or reconcile the index')
    for identity in missing:
        row = found[identity]
        row['issue_families'] = json.loads(row.pop('issue_families_json'))
        row['metadata'] = json.loads(row.pop('metadata_json'))
        row['lexical_score'] = None
        row['rrf_rank'] = len(expanded) + 1
        row['rrf_score'] = 0.0
        row['retrieval_provenance'] = [{'search': 'research-case-chain', 'rank': row['rrf_rank'],
                                      'query': 'explicit named case or linked canonical event'}]
        expanded.append(row)
    return expanded


def packet_state(rows: list[dict], gaps: list[dict], require_complete_public_sources: bool) -> tuple[str, list[str]]:
    reasons = []
    if not rows:
        return "insufficient-evidence", ["No evidence was retrieved."]
    if require_complete_public_sources and gaps:
        return "coverage-gap", ["A relevant registered source family has an unresolved public archive gap."]
    if gaps:
        reasons.append("Relevant public-source archive gaps are disclosed in coverage_warnings; do not make a corpus-completeness claim.")
    provision_rows = [row for row in rows if row["doc_type"] == "provision-version"]
    if not provision_rows:
        reasons.append("No reviewed provision-version record is in the packet; current-law conclusions require live verification.")
        return "needs-live-verification", reasons
    applicable_current = [
        row for row in provision_rows
        if row["status"] in CURRENT_SUPPORT_STATUSES and not row.get("temporal_link_candidate_only", False)
    ]
    if not applicable_current:
        statuses = sorted({row["status"] for row in provision_rows})
        reasons.append(
            "No independently retrieved provision record is approved to support a current-law conclusion without an additional live version, "
            f"transition or jurisdiction check. Retrieved statuses: {', '.join(statuses)}."
        )
        return "needs-live-verification", reasons
    if all(row["temporal_classification"] in {"superseded-or-old-rule", "quashed-or-overturned", "pending-or-non-final", "technical-not-authority"} for row in rows if row["doc_type"].endswith("event")) and not provision_rows:
        return "historical-only", ["Retrieved events cannot establish the current legal position."]
    return "ready-for-grounded-drafting", reasons


def research_originals_section(root: Path, question: str, applicability: dict, limit: int) -> dict:
    """Attach discovery evidence without changing the controlling-evidence lane."""
    if applicability.get('route_state') != 'routed':
        result = {
            'query': question, 'status': 'not-run-applicability-unresolved', 'results': [],
            'warnings': ['Resolve applicability before searching potentially incompatible regimes.'],
            'use_limit': UNRESOLVED_USE_LIMIT,
        }
    else:
        result = search_research_originals(root, question, limit=limit)
    return {
        **result,
        'requested_limit': limit,
        'authority_role': AUTHORITY_ROLE,
        'supports_current_law_drafting': False,
        'may_execute': False,
        'use_limit': USE_LIMIT if applicability.get('route_state') == 'routed' else UNRESOLVED_USE_LIMIT,
        'date_use_limit': DATE_USE_LIMIT,
        'applicability_use_limit': APPLICABILITY_USE_LIMIT,
    }


def research_readings_section(root: Path, question: str, applicability: dict, originals: dict, depth: str) -> dict:
    enabled = depth == 'expanded' and applicability.get('route_state') == 'routed'
    seeds = originals.get('results', []) if enabled else []
    result = expand_research_results(root, question, seeds)
    if not enabled:
        result['status'] = ('not-run-applicability-unresolved' if applicability.get('route_state') != 'routed'
                            else 'not-requested')
    elif originals.get('status') in {'integrity-error', 'archive-unavailable', 'invalid-query'}:
        result['status'] = 'integrity-error'
        result['validation_errors'].append('Source discovery was incomplete or failed: ' + originals['status'])
        result['warnings'].append('Source discovery was incomplete or failed: ' + originals['status'])
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--database", type=Path)
    parser.add_argument("--jurisdiction")
    parser.add_argument("--actor")
    parser.add_argument("--activity")
    parser.add_argument("--asset-type")
    parser.add_argument("--issue-family")
    parser.add_argument("--as-of")
    parser.add_argument("--limit", type=int, default=18)
    parser.add_argument("--originals-limit", type=int, default=6)
    parser.add_argument('--research-depth', choices=('excerpts', 'expanded'), default='expanded',
                        help='Expand discovered local originals; excerpts retains the prior retrieval baseline.')
    parser.add_argument("--require-complete-public-sources", action="store_true")
    parser.add_argument("--allow-ambiguous-routing", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.originals_limit <= 12:
        parser.error('--originals-limit must be between 1 and 12')
    root = args.root.resolve()
    answer_as_of = args.as_of or date.today().isoformat()
    applicability = route_question(
        args.question,
        jurisdiction=args.jurisdiction,
        actor=args.actor,
        activity=args.activity,
        as_of=answer_as_of,
        knowledge_baseline=KNOWLEDGE_BASELINE,
    )
    effective_jurisdiction = resolve_effective_jurisdiction(applicability, args.jurisdiction)
    database = args.database or root / "data" / "search-index.sqlite3"
    if applicability["route_state"] == "needs-applicability-input" and not args.allow_ambiguous_routing:
        query_b = None
        rows = []
        gaps = []
        state = "needs-applicability-input"
        reasons = applicability["reasons"] + [
            "Retrieval was not run because unresolved applicability could mix incompatible legal regimes."
        ]
    else:
        query_b, rows, _ = double_search(
            database, args.question, jurisdiction=effective_jurisdiction,
            issue_family=args.issue_family, as_of=answer_as_of, limit=args.limit,
        )
        rows = expand_applicability_routes(
            database, rows, applicability["provision_route_ids"], answer_as_of,
        )
        rows = expand_case_chains(root, database.resolve(), rows, args.question)
        rows = expand_temporal_comparators(root, database, rows, answer_as_of)
        rows = expand_verified_source_bindings(root, database, rows)
        gaps = relevant_gaps(root, effective_jurisdiction, include_all=args.require_complete_public_sources)
        state, reasons = packet_state(rows, gaps, args.require_complete_public_sources)
        if (applicability["requires_live_version_check"] and state == "ready-for-grounded-drafting"
                and live_review_errors(root, applicability['provision_route_ids'], answer_as_of)):
            state = "needs-live-verification"
            reasons.append(
                f"The answer date {answer_as_of} is later than the verified knowledge baseline {KNOWLEDGE_BASELINE}."
            )
    evidence = []
    artifacts = source_artifact_lookup(root)
    for row in rows:
        item = compact_result(row)
        item["rrf_rank"] = row["rrf_rank"]
        item["rrf_score"] = row["rrf_score"]
        item["retrieval_provenance"] = row["retrieval_provenance"]
        if row.get("temporal_link_role"):
            item["temporal_link_role"] = row["temporal_link_role"]
            item["linked_from_event_ids"] = row["linked_from_event_ids"]
            item["temporal_link_candidate_only"] = row["temporal_link_candidate_only"]
            item["temporal_link_metadata"] = row["temporal_link_metadata"]
        if row.get("applicability_route_role"):
            item["applicability_route_role"] = row["applicability_route_role"]
        if row.get("provision_source_binding"):
            item["provision_source_binding"] = row["provision_source_binding"]
        if row.get("provision_source_binding_role"):
            item["provision_source_binding_role"] = row["provision_source_binding_role"]
            item["bound_provision_ids"] = row["bound_provision_ids"]
        item["source_artifact"] = artifacts.get(row.get("official_url"), {
            "snapshot_status": "not-recorded-in-source-artifact-ledger",
            "provenance_status": "unverified",
        })
        evidence.append(item)
    if state == "ready-for-grounded-drafting" and applicability["temporal_intent"] == "current-or-prospective-advice":
        routed_evidence_ids = {
            f"provision:{provision_id}" for provision_id in applicability["provision_route_ids"]
        }
        controlling = [
            item for item in evidence
            if item["doc_type"] == "provision-version" and item["status"] in CURRENT_SUPPORT_STATUSES
            and not item.get("temporal_link_candidate_only", False)
            and item["evidence_id"] in routed_evidence_ids
        ]
        if not routed_evidence_ids or not controlling:
            state = "needs-live-verification"
            reasons.append(
                "No approved deterministic provision route was resolved for the current operational question."
            )
        if controlling and any(
            item["source_artifact"].get("snapshot_status") not in LOCAL_SNAPSHOT_STATUSES
            for item in controlling
        ):
            state = "needs-live-verification"
            reasons.append(
                "At least one controlling provision lacks an immutable local source; verify and snapshot its operative text before release."
            )
        missing_bindings = [
            item["evidence_id"] for item in controlling
            if not item.get("provision_source_binding", {}).get("supports_current_law_drafting", False)
        ]
        if state == "ready-for-grounded-drafting" and missing_bindings:
            state = "needs-live-verification"
            reasons.append(
                "No verified clause-level official-text binding is available for: " + ", ".join(missing_bindings)
            )
        controlling_urls = {item["official_url"] for item in controlling}
        addressable_urls = {url for item in evidence if item['doc_type'] == 'official-source-span'
                            for url in (item.get('related_official_url'), item['official_url']) if url}
        missing_source_text = sorted(controlling_urls - addressable_urls)
        if state == "ready-for-grounded-drafting" and missing_source_text:
            state = "needs-live-verification"
            reasons.append(
                "No addressable official-source text span was retrieved for: " + ", ".join(missing_source_text)
            )
    originals = research_originals_section(root, args.question, applicability, args.originals_limit)
    readings = research_readings_section(root, args.question, applicability, originals, args.research_depth)
    packet = {
        "schema_version": "1.1",
        "question": args.question,
        "jurisdiction": effective_jurisdiction,
        "actor": args.actor,
        "activity": args.activity,
        "asset_type": args.asset_type,
        "issue_family": args.issue_family,
        "requires_complete_public_sources": args.require_complete_public_sources,
        "answer_as_of": answer_as_of,
        "knowledge_baseline": KNOWLEDGE_BASELINE,
        "applicability": applicability,
        "routing_inputs": {"jurisdiction": args.jurisdiction, "actor": args.actor,
                           "activity": args.activity, "as_of": answer_as_of},
        "release_state": state,
        "release_reasons": reasons,
        "query_a": args.question,
        "query_b": query_b,
        "coverage_warnings": gaps,
        "answer_contract": {
            "material_claims_require_evidence_ids": True,
            "current_law_claims_require_applicable_provision_version": True,
            "current_law_claims_require_verified_clause_binding": True,
            "current_law_claims_must_cite_bound_source_spans": True,
            "proceedings_are_allegations_only": True,
            "technical_events_are_not_contravention_findings": True,
            "quashed_propositions_are_not_current_authority": True,
            "candidate_temporal_links_do_not_establish_current_law": True,
            "unresolved_applicability_fails_closed": True,
            "research_originals_are_unreviewed_discovery_only": True,
        },
        "evidence": evidence,
        "research_originals": originals,
        "research_readings": readings,
        "research_depth": args.research_depth,
        "research_case_chains": selected_research_chains(root, evidence, args.question),
        "case_chain_use_limit": "Read linked subsequent treatment before applying an earlier case. Chain expansion includes later procedural history: do not present it as known on an earlier answer date or as proof of jurisdictional applicability. Research chronology and unresolved docket activity do not approve current-law use or prove finality.",
    }
    if applicability['temporal_intent'] == 'current-or-prospective-advice' and state == 'ready-for-grounded-drafting':
        eligibility_errors = current_release_errors(packet, root)
        if eligibility_errors:
            state = packet['release_state'] = 'needs-live-verification'
            packet['release_reasons'].extend(eligibility_errors)
    seal_packet(packet, root)
    rendered = json.dumps(packet, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote evidence packet {packet['packet_id']} to {args.output}")
        print(f"Release state: {state}")
    else:
        print(rendered, end="")
    return 0 if state == "ready-for-grounded-drafting" else 2


if __name__ == "__main__":
    raise SystemExit(main())
