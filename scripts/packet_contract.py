"""Shared integrity and release checks for frozen decision evidence packets."""
import hashlib
import json
from pathlib import Path
from datetime import date

from route_applicability import KNOWLEDGE_BASELINE, route_question
from case_chains import selected_research_chains
from search_source_originals import (validate_research_results, AUTHORITY_ROLE, USE_LIMIT,
                                    UNRESOLVED_USE_LIMIT, DATE_USE_LIMIT, APPLICABILITY_USE_LIMIT)
from read_source_originals import validate_reading_section
from reviewed_bindings import live_review_errors


POLICY_VERSION = 'evidence-release-v2'
INPUT_PATHS = {
    'clause_binding_candidates': 'data/clause-binding-candidates.json',
    'clause_binding_approvals': 'data/clause-binding-approvals.json',
    'reviewed_binding_policy_code': 'scripts/reviewed_bindings.py',
    'source_artifact_ledger': 'data/source-artifact-ledger.jsonl',
    'source_text_chunks': 'data/source-text-chunks.jsonl',
    'obligation_register': 'data/obligation-register.json',
    'provision_version_register': 'data/provision-version-register.json',
    'event_provision_links': 'data/event-provision-links.jsonl',
    'provision_source_bindings': 'data/provision-source-bindings.json',
    'source_coverage_ledger': 'data/source-coverage-ledger.json',
    'source_register': 'data/enforcement-source-register.json',
    'enforcement_events': 'data/enforcement-events-full.jsonl',
    'technical_events': 'data/technical-events-full.jsonl',
    'freshness_policy': 'data/source-refresh-policy.json',
    'routing_policy_code': 'scripts/route_applicability.py',
    'packet_policy_code': 'scripts/packet_contract.py',
    'claim_checker_code': 'scripts/check_answer.py',
    'independent_claim_checker_code': 'scripts/double_check_answer.py',
    'packet_builder_code': 'scripts/answer_kb.py',
    'case_chain_loader_code': 'scripts/case_chains.py',
    'original_research_code': 'scripts/search_source_originals.py',
    'original_reading_code': 'scripts/read_source_originals.py',
    'original_manifest_policy_code': 'scripts/source_manifest.py',
    'original_query_token_policy_code': 'scripts/kb_search.py',
}

STATE_JURISDICTIONS = {'Australian Capital Territory', 'New South Wales', 'Northern Territory', 'Queensland',
                       'South Australia', 'Tasmania', 'Victoria', 'Western Australia'}
CURRENT_SUPPORT_STATUSES = {'current-at-baseline', 'current-at-baseline-appellate-control'}
LOCAL_SNAPSHOT_STATUSES = {'bundled-immutable-copy', 'captured-immutable-copy'}


def effective_jurisdiction(applicability: dict, explicit: str | None) -> str | None:
    detected = applicability.get('jurisdiction_candidates', [])
    return explicit or (detected[0] if len(detected) == 1 and detected[0] in STATE_JURISDICTIONS else None)


def current_release_errors(packet: dict, root: Path) -> list[str]:
    """Recompute release prerequisites; a supplied ready label is not authorization."""
    errors = []
    if (packet.get('answer_as_of', '') > KNOWLEDGE_BASELINE
            and live_review_errors(root, packet.get('applicability', {}).get('provision_route_ids', []), packet.get('answer_as_of', ''))):
        errors.append('Current-law claims require a live version check beyond the verified knowledge baseline, regardless of question wording.')
    if packet.get('requires_complete_public_sources') is True:
        ledger = json.loads((root / INPUT_PATHS['source_coverage_ledger']).read_text(encoding='utf-8-sig'))
        register = json.loads((root / INPUT_PATHS['source_register']).read_text(encoding='utf-8-sig'))
        sources = {row['id']: row for row in register.get('sources', [])}
        jurisdiction = packet.get('jurisdiction')
        relevant = [row for row in ledger.get('source_reviews', [])
                    if not jurisdiction or jurisdiction.lower() in sources.get(row.get('source_family_id'), {}).get('jurisdiction', '').lower()]
        if (not relevant or any(row.get('extraction_status') not in {'complete-case-indexed', 'complete-series-indexed'}
                                or row.get('gap_periods') for row in relevant)):
            errors.append('Complete public-source coverage is required but canonical coverage remains incomplete or unknown.')
    evidence = {row.get('evidence_id'): row for row in packet.get('evidence', []) if isinstance(row, dict)}
    route_ids = packet.get('applicability', {}).get('provision_route_ids', [])
    if not route_ids:
        errors.append('Current-law release requires a resolved controlling provision route.')
    bindings = {row['provision_id']: row for row in json.loads((root / INPUT_PATHS['provision_source_bindings']).read_text(encoding='utf-8-sig')).get('bindings', [])}
    reviewed_routes = [provision_id for provision_id in route_ids
                       if bindings.get(provision_id, {}).get('binding_status') == 'reviewed-exact-clause-range']
    if reviewed_routes:
        errors.extend(live_review_errors(root, reviewed_routes, packet.get('answer_as_of', '')))
    artifacts = [json.loads(line) for line in (root / INPUT_PATHS['source_artifact_ledger']).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    for provision_id in route_ids:
        item = evidence.get('provision:' + provision_id, {})
        if item.get('status') not in CURRENT_SUPPORT_STATUSES or item.get('temporal_link_candidate_only'):
            errors.append(f'Release prerequisites lack controlling current evidence: {provision_id}')
        binding = bindings.get(provision_id, {})
        if not binding.get('supports_current_law_drafting') or item.get('provision_source_binding') != binding:
            errors.append(f'Release prerequisites lack a canonical reviewed source binding: {provision_id}')
        required_spans = binding.get('source_span_ids', [])
        if (not required_spans or not all(evidence.get(span_id, {}).get('doc_type') == 'official-source-span'
                                         for span_id in required_spans)):
            errors.append(f'Release prerequisites lack a bound official text span: {provision_id}')
        supplied = item.get('source_artifact', {})
        matches = [row for row in artifacts if row.get('record_type') == 'local-official-snapshot'
                   and row.get('snapshot_status') in LOCAL_SNAPSHOT_STATUSES
                   and row.get('canonical_url') == item.get('official_url')
                   and row.get('artifact_id') == supplied.get('artifact_id')
                   and row.get('sha256') == supplied.get('source_sha256')
                   and row.get('snapshot_path') == supplied.get('snapshot_path')]
        verified = False
        for artifact in matches:
            path = (root / artifact['snapshot_path']).resolve()
            if path.is_relative_to(root.resolve()) and path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == artifact['sha256']:
                verified = True
                break
        if not verified:
            errors.append(f'Release prerequisites lack verified local source bytes: {provision_id}')
    return errors


def input_digests(root: Path) -> dict:
    hashes = {key: hashlib.sha256((root / relative).read_bytes()).hexdigest()
              if (root / relative).is_file() else None for key, relative in INPUT_PATHS.items()}
    chain_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in sorted((root / 'data/reviewed-case-chains').glob('*.json'))}
    hashes['research_case_chain_set'] = hashlib.sha256(json.dumps(chain_hashes, sort_keys=True).encode()).hexdigest()
    return hashes


def packet_digest(packet: dict) -> str:
    content = {key: value for key, value in packet.items() if key != 'packet_id'}
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def seal_packet(packet: dict, root: Path) -> dict:
    packet['schema_version'] = '1.2'
    packet['validation_policy'] = POLICY_VERSION
    packet['canonical_register_sha256'] = input_digests(root)
    packet['packet_id'] = packet_digest(packet)
    return packet


def research_original_errors(packet: dict, root: Path) -> list[str]:
    errors = []
    for item in packet.get('evidence', []):
        if not isinstance(item, dict):
            continue
        paths = [item.get(key, '') for key in ('source_path', 'snapshot_path', 'text_path')]
        artifact = item.get('source_artifact')
        if isinstance(artifact, dict):
            paths.append(artifact.get('snapshot_path', ''))
        elif artifact is not None:
            errors.append('Controlling evidence has malformed source-artifact metadata.')
        if (str(item.get('evidence_id', '')).startswith('original:')
                or str(item.get('evidence_id', '')).startswith('reading:')
                or str(item.get('reading_id', '')).startswith('reading:')
                or str(item.get('research_id', '')).startswith('original:')
                or item.get('doc_type') == 'research-original'
                or any('source-originals/' in str(path).replace('\\', '/').lower() for path in paths)):
            errors.append('Unreviewed research originals cannot be promoted into controlling evidence.')
    section = packet.get('research_originals')
    if section is None:
        if packet.get('research_readings') is not None or 'research_depth' in packet:
            errors.append('Research readings require the original discovery section.')
        return errors
    if not isinstance(section, dict):
        return errors + ['Research-original section must be an object.']
    if (section.get('authority_role') != AUTHORITY_ROLE
            or section.get('supports_current_law_drafting') is not False
            or section.get('may_execute') is not False):
        errors.append('Research-original section attempts to promote unreviewed sources to legal or operational authority.')
    expected_limit = (UNRESOLVED_USE_LIMIT if section.get('status') == 'not-run-applicability-unresolved'
                      else USE_LIMIT)
    for key, expected in (('date_use_limit', DATE_USE_LIMIT), ('applicability_use_limit', APPLICABILITY_USE_LIMIT),
                          ('use_limit', expected_limit)):
        if section.get(key) != expected:
            errors.append('Research-original canonical use limit is missing or changed: ' + key)
    if section.get('query') != packet.get('question'):
        errors.append('Research-original query differs from the frozen decision question.')
    limit = section.get('requested_limit')
    results = section.get('results')
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 12:
        errors.append('Research-original result limit is invalid.')
    if not isinstance(results, list):
        return errors + ['Research-original results must be a list.']
    if isinstance(limit, int) and len(results) > limit:
        errors.append('Research-original results exceed the recorded limit.')
    status = section.get('status')
    if status not in {'ok', 'no-matches', 'archive-unavailable', 'invalid-query', 'integrity-error',
                      'not-run-applicability-unresolved'}:
        errors.append('Research-original search status is unsupported.')
    if results and status not in {'ok', 'integrity-error'}:
        errors.append('Research-original search status contradicts supplied results.')
    if packet.get('applicability', {}).get('route_state') != 'routed' and results:
        errors.append('Research-original retrieval must not bypass unresolved applicability.')
    try:
        errors.extend(validate_research_results(root, results))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        errors.append('Research-original source identities and bytes could not be validated.')
    readings = packet.get('research_readings')
    if 'research_depth' in packet and readings is None:
        errors.append('An explicit research reading mode requires its reading section.')
    if readings is not None:
        try:
            errors.extend(validate_reading_section(root, readings, query=packet.get('question'), seeds=results,
                                                  discovery_status=section.get('status')))
            if packet.get('research_depth') not in {'excerpts', 'expanded'}:
                errors.append('Research reading depth is invalid.')
            expected_disabled = ('not-run-applicability-unresolved'
                                 if packet.get('applicability', {}).get('route_state') != 'routed'
                                 else 'not-requested' if packet.get('research_depth') == 'excerpts' else None)
            if expected_disabled and readings.get('status') != expected_disabled:
                errors.append('Research reading status contradicts the disabled mode or unresolved applicability.')
            if not expected_disabled and readings.get('status') in {'not-requested', 'not-run-applicability-unresolved'}:
                errors.append('Expanded routed research cannot be resealed as a disabled reading.')
            if packet.get('applicability', {}).get('route_state') != 'routed' and readings.get('results'):
                errors.append('Expanded reading must not bypass unresolved applicability.')
            if packet.get('research_depth') == 'excerpts' and readings.get('results'):
                errors.append('Excerpts-only mode cannot silently contain expanded readings.')
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            errors.append('Expanded research text could not be validated.')
    return errors


def canonical_span_errors(packet: dict, root: Path) -> list[str]:
    """Renaming a research result must not manufacture a canonical source span."""
    spans = [item for item in packet.get('evidence', []) if isinstance(item, dict)
             and (item.get('doc_type') == 'official-source-span'
                  or str(item.get('evidence_id', '')).startswith('source-span:'))]
    if not spans:
        return []
    try:
        chunks = {row['chunk_id']: row for row in (json.loads(line) for line in
                  (root / INPUT_PATHS['source_text_chunks']).read_text(encoding='utf-8-sig').splitlines() if line.strip())}
    except (OSError, ValueError, KeyError, TypeError):
        return ['Canonical official source spans could not be loaded.']
    errors = []
    fields = {'text': 'text', 'official_url': 'canonical_url', 'related_official_url': 'parent_canonical_url',
              'source_path': 'snapshot_path', 'source_locator': 'locator',
              'source_text_sha256': 'text_sha256', 'source_snapshot_sha256': 'source_sha256'}
    for item in spans:
        chunk = chunks.get(str(item.get('evidence_id', '')).removeprefix('source-span:'))
        if (not chunk or item.get('doc_type') != 'official-source-span'
                or any(item.get(key) != chunk.get(source_key) for key, source_key in fields.items())):
            errors.append('Official source span differs from canonical text and provenance: ' + str(item.get('evidence_id')))
    return errors


def validate_packet(packet: dict | None, root: Path, draft: dict) -> list[str]:
    if not isinstance(packet, dict):
        return ['Current-law claims require a frozen evidence packet; omission cannot bypass release checks.']
    errors = []
    if packet.get('validation_policy') != POLICY_VERSION or packet.get('schema_version') != '1.2':
        errors.append('Legacy or unsupported packet contract; regenerate with the current packet builder.')
    if packet.get('packet_id') != packet_digest(packet):
        errors.append('Packet identity does not match its complete decision context and evidence.')
    if not draft.get('question') or draft.get('question') != packet.get('question'):
        errors.append('Draft question does not match the frozen packet question.')
    if draft.get('answer_as_of') and draft['answer_as_of'] != packet.get('answer_as_of'):
        errors.append('Draft answer date differs from the packet answer date.')
    observed = input_digests(root)
    pinned = packet.get('canonical_register_sha256', {})
    for key, value in observed.items():
        if value is None or pinned.get(key) != value:
            errors.append(f'Packet canonical input is missing or changed: {key}')
    try:
        if packet.get('research_case_chains', {}) != selected_research_chains(root, packet.get('evidence', []), packet.get('question', '')):
            errors.append('Packet omits or changes the canonical research case chain for retrieved events.')
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        errors.append('Canonical research case chain could not be validated.')
    errors.extend(research_original_errors(packet, root))
    errors.extend(canonical_span_errors(packet, root))
    applicability = packet.get('applicability', {})
    routing_inputs = packet.get('routing_inputs')
    try:
        date.fromisoformat(packet['answer_as_of'])
        if not isinstance(routing_inputs, dict) or routing_inputs.get('as_of') != packet['answer_as_of']:
            raise ValueError('Missing or inconsistent routing inputs')
        expected = route_question(packet['question'], jurisdiction=routing_inputs.get('jurisdiction'),
                                  actor=routing_inputs.get('actor'), activity=routing_inputs.get('activity'),
                                  as_of=packet['answer_as_of'])
        if expected != applicability or packet.get('knowledge_baseline') != KNOWLEDGE_BASELINE:
            errors.append('Packet applicability differs from the current deterministic routing policy.')
        if (packet.get('jurisdiction') != effective_jurisdiction(expected, routing_inputs.get('jurisdiction'))
                or packet.get('actor') != routing_inputs.get('actor')
                or packet.get('activity') != routing_inputs.get('activity')):
            errors.append('Packet top-level context contradicts its authoritative routing inputs.')
    except (KeyError, ValueError, TypeError):
        errors.append('Packet lacks a valid answer date and complete routing inputs.')
    if applicability.get('route_state') != 'routed':
        errors.append('Packet applicability is unresolved.')
    if (applicability.get('requires_live_version_check')
            and live_review_errors(root, applicability.get('provision_route_ids', []), packet.get('answer_as_of', ''))):
        errors.append('Packet requires a live version check before current-law release.')
    if packet.get('release_state') != 'ready-for-grounded-drafting':
        errors.append(f"Current-law packet has non-release state: {packet.get('release_state')}")
    try:
        errors.extend(current_release_errors(packet, root))
    except (OSError, ValueError, KeyError, TypeError):
        errors.append('Canonical release prerequisites could not be validated.')
    return errors
