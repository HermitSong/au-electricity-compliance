import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from build_provision_source_bindings import build, ERCP_PARENT_URL
from check_answer import check_draft, resolve_claim_type
from packet_contract import INPUT_PATHS, effective_jurisdiction, packet_digest, seal_packet, validate_packet
from route_applicability import KNOWLEDGE_BASELINE, route_question
from build_temporal_links import temporal_classification


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for path in INPUT_PATHS.values():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('{}', encoding='utf-8')
        self.question = 'Can a Victorian retailer disconnect a life-support customer?'
        self.packet = {'question': self.question, 'answer_as_of': KNOWLEDGE_BASELINE,
                       'knowledge_baseline': KNOWLEDGE_BASELINE,
                       'routing_inputs': {'jurisdiction': None, 'actor': None, 'activity': None, 'as_of': KNOWLEDGE_BASELINE},
                       'applicability': route_question(self.question, as_of=KNOWLEDGE_BASELINE),
                       'release_state': 'ready-for-grounded-drafting', 'evidence': []}
        seal_packet(self.packet, self.root)
        self.packet['jurisdiction'] = effective_jurisdiction(self.packet['applicability'], None)
        seal_packet(self.packet, self.root)
        self.draft = {'question': self.question, 'claims': [{'claim_id': 'C1', 'text': 'Current test obligation.', 'claim_type': 'current-law', 'evidence_ids': []}]}

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_packet_integrity_is_not_legal_certification(self):
        errors = validate_packet(self.packet, self.root, self.draft)
        self.assertFalse(any('identity' in error or 'canonical input' in error for error in errors))
        self.assertTrue(any('Release prerequisites' in error for error in errors))

    def test_missing_packet_rejected(self):
        self.assertTrue(validate_packet(None, self.root, self.draft))

    def test_each_material_context_field_is_hashed(self):
        for field in ('answer_as_of', 'actor', 'activity', 'release_state', 'coverage_warnings', 'evidence', 'answer_contract'):
            changed = copy.deepcopy(self.packet)
            changed[field] = 'tampered'
            self.assertNotEqual(packet_digest(changed), self.packet['packet_id'])

    def test_rehashed_false_route_rejected(self):
        changed = copy.deepcopy(self.packet)
        changed['applicability']['provision_route_ids'] = ['unrelated-provision']
        seal_packet(changed, self.root)
        self.assertTrue(any('routing policy' in e for e in validate_packet(changed, self.root, self.draft)))

    def test_changed_canonical_data_invalidates_packet(self):
        (self.root / INPUT_PATHS['source_coverage_ledger']).write_text('{"changed":true}')
        self.assertTrue(any('source_coverage_ledger' in e for e in validate_packet(self.packet, self.root, self.draft)))

    def test_question_mismatch_rejected(self):
        self.assertTrue(validate_packet(self.packet, self.root, {**self.draft, 'question': 'Another customer'}))

    def test_blocked_packet_cannot_be_released_by_hashing(self):
        self.packet['release_state'] = 'needs-live-verification'
        seal_packet(self.packet, self.root)
        self.assertTrue(any('non-release' in e for e in validate_packet(self.packet, self.root, self.draft)))

    def test_future_date_cannot_clear_live_version_gate(self):
        self.packet['answer_as_of'] = '2026-09-06'
        self.packet['routing_inputs']['as_of'] = '2026-09-06'
        self.packet['applicability'] = route_question(self.question, as_of='2026-09-06')
        seal_packet(self.packet, self.root)
        self.assertTrue(any('live version' in e for e in validate_packet(self.packet, self.root, self.draft)))

    def test_wrong_document_page_numbers_never_approve_a_binding(self):
        provision = {'provision_id': 'VIC-ERCP-V6-LIFE-SUPPORT-2026-08-29', 'official_url': ERCP_PARENT_URL, 'status': 'current-at-baseline'}
        (self.root / 'data/provision-version-register.json').write_text(json.dumps({'baseline_date': KNOWLEDGE_BASELINE, 'provisions': [provision]}))
        chunks = [{'canonical_url': 'https://www.esc.vic.gov.au/wrong.pdf', 'parent_canonical_url': ERCP_PARENT_URL,
                   'locator': f'page:{n}', 'chunk_id': str(n), 'source_sha256': '0' * 64, 'text': 'Unrelated document.'} for n in range(113, 129)]
        (self.root / 'data/source-text-chunks.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in chunks))
        binding = build(self.root)['bindings'][0]
        self.assertFalse(binding['supports_current_law_drafting'])
        self.assertEqual(binding['binding_status'], 'candidate-page-range-located')

    def test_shared_checker_requires_packet_even_with_cited_current_provision(self):
        (self.root / 'data/provision-source-bindings.json').write_text('{"bindings": []}')
        db = self.root / 'data/search-index.sqlite3'
        connection = sqlite3.connect(db)
        connection.execute('CREATE TABLE documents (evidence_id TEXT)')
        connection.close()
        report = check_draft(self.root, self.draft)
        self.assertFalse(report['passed'])
        self.assertTrue(any('require a frozen' in error for error in report['errors']))
        self.assertFalse(report['claim_reports'][0]['passed'])

    def test_missing_claim_type_cannot_skip_current_law_checks(self):
        self.assertEqual(resolve_claim_type({'text': 'The retailer must comply now.'}), 'current-law')
        self.assertEqual(resolve_claim_type({'text': 'The regulator issued notices in 2024.'}), 'historical-fact')

    def test_stayed_review_is_not_final_authority(self):
        event = {'status': 'review-pending-conditional-stay', 'event_type': 'licence-or-accreditation-action',
                 'case_status_note': 'Conditional stay pending final hearing', 'event_date': '2025-12-24'}
        self.assertEqual(temporal_classification(event, [])[0], 'pending-or-non-final')


if __name__ == '__main__':
    unittest.main()
