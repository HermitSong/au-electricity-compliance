"""Independent source replay and adversarial tests; no staged implementation writes."""

import copy
from datetime import date
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))

from reviewed_bindings import digest, live_review_errors, reviewed_binding
from packet_contract import (INPUT_PATHS, canonical_span_errors, current_release_errors,
                             seal_packet, validate_packet)
from route_applicability import KNOWLEDGE_BASELINE, route_question


class ReviewDate(date):
    @classmethod
    def today(cls):
        return cls(2026, 9, 13)


class ReviewedBindingsAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'data').mkdir()
        (self.root / 'official-snapshots').mkdir()
        self.clock = patch('reviewed_bindings.date', ReviewDate)
        self.clock.start()
        self.addCleanup(self.clock.stop)
        self.source = self.root / 'official-snapshots/fixture.txt'
        self.source.write_text('Obligation.\nException.\n', encoding='utf-8')
        self.source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.provision = {
            'provision_id': 'TEST-REVIEWED', 'status': 'current-at-baseline',
            'official_url': 'https://www.aemc.gov.au/review-fixture',
            'valid_from': '2026-09-04', 'valid_to': None,
        }
        self.chunks = [{
            'chunk_id': str(index), 'canonical_url': self.provision['official_url'],
            'parent_canonical_url': None, 'snapshot_path': 'official-snapshots/fixture.txt',
            'source_sha256': self.source_hash, 'text': text,
            'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'locator': 'document-text', 'character_start': start, 'character_end': end,
        } for index, text, start, end in [(1, 'Obligation.', 0, 11), (2, 'Exception.', 12, 22)]]
        self.candidate = {
            'provision_id': self.provision['provision_id'],
            'provision_sha256': digest(self.provision),
            'prepared_by': 'synthetic-preparer', 'verified_as_of': '2026-09-13',
            'operative_from': '2026-09-04', 'official_url': self.provision['official_url'],
            'clause_scope': 'Obligation and exception',
            'applicability_limit': 'Synthetic test only; never operational authority.',
            'source_span_ids': ['source-span:1', 'source-span:2'],
            'source_sha256_values': [self.source_hash],
            'span_record_sha256': digest(self.chunks),
        }
        self.approval = {
            'candidate_sha256': digest(self.candidate),
            'reviewer_id': 'synthetic-independent-reviewer', 'reviewed_at': '2026-09-13',
            'result': 'approved-for-scoped-drafting',
            'review_note': 'Synthetic review fixture, not an approval of any real source.',
        }
        self.persist()

    def write_json(self, relative, value):
        (self.root / relative).write_text(json.dumps(value), encoding='utf-8')

    def persist(self):
        self.write_json('data/clause-binding-candidates.json', {'candidates': [self.candidate]})
        self.write_json('data/clause-binding-approvals.json', {'approvals': [self.approval]})
        self.write_json('data/provision-version-register.json', {'provisions': [self.provision]})
        (self.root / 'data/source-text-chunks.jsonl').write_text(
            ''.join(json.dumps(row) + '\n' for row in self.chunks), encoding='utf-8')

    def binding(self):
        return reviewed_binding(self.root, self.provision, self.chunks)

    def publish_binding(self):
        binding = self.binding()
        self.assertIsNotNone(binding)
        self.write_json('data/provision-source-bindings.json', {'bindings': [binding]})
        return binding

    def span(self, row):
        fields = {'text': 'text', 'official_url': 'canonical_url',
                  'related_official_url': 'parent_canonical_url', 'source_path': 'snapshot_path',
                  'source_locator': 'locator', 'source_text_sha256': 'text_sha256',
                  'source_snapshot_sha256': 'source_sha256'}
        return {'evidence_id': 'source-span:' + row['chunk_id'],
                'doc_type': 'official-source-span',
                **{key: row.get(source_key) for key, source_key in fields.items()}}

    def packet(self):
        binding = self.publish_binding()
        artifact = {
            'record_type': 'local-official-snapshot', 'snapshot_status': 'captured-immutable-copy',
            'canonical_url': self.provision['official_url'], 'artifact_id': 'fixture-artifact',
            'sha256': self.source_hash, 'snapshot_path': 'official-snapshots/fixture.txt',
        }
        (self.root / 'data/source-artifact-ledger.jsonl').write_text(
            json.dumps(artifact) + '\n', encoding='utf-8')
        return {
            'answer_as_of': '2026-09-13',
            'applicability': {'provision_route_ids': [self.provision['provision_id']]},
            'evidence': [{
                'evidence_id': 'provision:' + self.provision['provision_id'],
                'status': self.provision['status'], 'official_url': self.provision['official_url'],
                'provision_source_binding': binding,
                'source_artifact': {'artifact_id': artifact['artifact_id'],
                                    'source_sha256': self.source_hash,
                                    'snapshot_path': artifact['snapshot_path']},
            }] + [self.span(row) for row in self.chunks],
        }

    def test_valid_review_is_scoped_and_never_execution(self):
        binding = self.binding()
        self.assertTrue(binding['supports_current_law_drafting'])
        self.assertIs(binding['supports_operational_execution'], False)
        self.assertIn('not-professional-certification', binding['review_status'])

    def test_changed_candidate_invalidates_approval(self):
        for key in ('clause_scope', 'applicability_limit', 'verified_as_of', 'official_url'):
            with self.subTest(field=key):
                candidate = dict(self.candidate, **{key: 'changed'})
                self.write_json('data/clause-binding-candidates.json', {'candidates': [candidate]})
                self.assertIsNone(self.binding())

    def test_changed_provision_invalidates_approval(self):
        self.provision['valid_to'] = '2026-09-12'
        self.assertIsNone(self.binding())

    def test_changed_quote_with_recomputed_text_hash_is_rejected(self):
        self.chunks[1]['text'] = 'No exception.'
        self.chunks[1]['text_sha256'] = hashlib.sha256(b'No exception.').hexdigest()
        self.assertIsNone(self.binding())

    def test_changed_source_bytes_are_rejected(self):
        self.source.write_bytes(b'Changed source.')
        self.assertIsNone(self.binding())

    def test_changed_locator_is_rejected(self):
        self.chunks[1]['character_start'] = 1
        self.assertIsNone(self.binding())

    def test_missing_approval_is_rejected(self):
        self.write_json('data/clause-binding-approvals.json', {'approvals': []})
        self.assertIsNone(self.binding())

    def test_duplicate_approval_is_rejected(self):
        self.write_json('data/clause-binding-approvals.json',
                        {'approvals': [self.approval, self.approval]})
        self.assertIsNone(self.binding())

    def test_duplicate_candidate_is_rejected(self):
        self.write_json('data/clause-binding-candidates.json',
                        {'candidates': [self.candidate, self.candidate]})
        self.assertIsNone(self.binding())

    def test_preparer_cannot_be_reviewer(self):
        self.approval['reviewer_id'] = self.candidate['prepared_by']
        self.persist()
        self.assertIsNone(self.binding())

    def test_invalid_review_dates_are_rejected(self):
        for value in ('2026-09-12', '2026-09-14', 'not-a-date'):
            with self.subTest(value=value):
                self.approval['reviewed_at'] = value
                self.persist()
                self.assertIsNone(self.binding())

    def test_future_verification_and_operative_dates_are_rejected(self):
        for key in ('verified_as_of', 'operative_from'):
            with self.subTest(field=key):
                candidate = dict(self.candidate, **{key: '2026-09-14'})
                approval = dict(self.approval, candidate_sha256=digest(candidate))
                self.write_json('data/clause-binding-candidates.json', {'candidates': [candidate]})
                self.write_json('data/clause-binding-approvals.json', {'approvals': [approval]})
                self.assertIsNone(self.binding())

    def test_out_of_root_source_path_is_rejected_even_with_updated_hashes(self):
        self.chunks[0]['snapshot_path'] = '../outside-source.txt'
        self.candidate['span_record_sha256'] = digest(self.chunks)
        self.approval['candidate_sha256'] = digest(self.candidate)
        self.persist()
        self.assertIsNone(self.binding())

    def test_exact_review_date_is_required(self):
        self.publish_binding()
        ids = [self.provision['provision_id']]
        self.assertEqual(live_review_errors(self.root, ids, '2026-09-13'), [])
        for value in ('2026-09-12', '2026-09-14'):
            with self.subTest(date=value):
                self.assertTrue(live_review_errors(self.root, ids, value))

    def test_revoked_approval_rejects_old_materialized_binding(self):
        self.publish_binding()
        self.write_json('data/clause-binding-approvals.json', {'approvals': []})
        self.assertTrue(live_review_errors(self.root, [self.provision['provision_id']], '2026-09-13'))

    def test_tampered_materialized_binding_is_rejected(self):
        binding = self.publish_binding()
        binding['supports_operational_execution'] = True
        self.write_json('data/provision-source-bindings.json', {'bindings': [binding]})
        self.assertTrue(live_review_errors(self.root, [self.provision['provision_id']], '2026-09-13'))

    def test_no_routes_cannot_assert_live_review(self):
        self.publish_binding()
        self.assertTrue(live_review_errors(self.root, [], '2026-09-13'))

    def test_resealed_packet_cannot_tamper_with_a_quote(self):
        packet = self.packet()
        packet['evidence'][-1]['text'] = 'No exception.'
        packet['evidence'][-1]['source_text_sha256'] = hashlib.sha256(b'No exception.').hexdigest()
        seal_packet(packet, self.root)
        self.assertTrue(canonical_span_errors(packet, self.root))

    def test_all_bound_spans_are_required_in_release_packet(self):
        packet = self.packet()
        self.assertEqual(current_release_errors(packet, self.root), [])
        packet['evidence'].pop()  # Omit the exception but retain the obligation.
        seal_packet(packet, self.root)
        self.assertTrue(current_release_errors(packet, self.root),
                        'A packet with the exception span removed was accepted.')

    def test_full_validator_rejects_resealed_exception_omission(self):
        question = 'Explain NEM battery dispatch responsibilities.'
        inputs = {'jurisdiction': 'National Electricity Market', 'actor': 'battery',
                  'activity': 'dispatch', 'as_of': '2026-09-13'}
        applicability = route_question(question, **inputs)
        self.assertEqual(len(applicability['provision_route_ids']), 1)
        self.provision['provision_id'] = applicability['provision_route_ids'][0]
        self.candidate.update(provision_id=self.provision['provision_id'],
                              provision_sha256=digest(self.provision))
        self.approval['candidate_sha256'] = digest(self.candidate)
        self.persist()
        packet = self.packet()
        packet.update(question=question, routing_inputs=inputs, applicability=applicability,
                      knowledge_baseline=KNOWLEDGE_BASELINE,
                      jurisdiction=inputs['jurisdiction'], actor=inputs['actor'],
                      activity=inputs['activity'], release_state='ready-for-grounded-drafting')
        # Complete the hash manifest within the isolated fixture; production code is imported above.
        for relative in INPUT_PATHS.values():
            path = self.root / relative
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{}', encoding='utf-8')
        draft = {'question': question, 'answer_as_of': inputs['as_of']}
        seal_packet(packet, self.root)
        self.assertEqual(validate_packet(packet, self.root, draft), [])
        packet['evidence'].pop()
        seal_packet(packet, self.root)
        self.assertTrue(validate_packet(packet, self.root, draft),
                        'Full validator accepted a resealed packet omitting the bound exception.')

    def test_baseline_date_cannot_reuse_a_later_review_or_revoked_approval(self):
        packet = self.packet()
        packet['answer_as_of'] = '2026-08-29'
        self.write_json('data/clause-binding-approvals.json', {'approvals': []})
        self.assertTrue(current_release_errors(packet, self.root),
                        'Release prerequisite checks skipped review replay at the old baseline.')

    def test_whitespace_reviewer_and_note_are_rejected(self):
        self.approval.update(reviewer_id='   ', review_note='\n\t ')
        self.persist()
        self.assertIsNone(self.binding())

    def test_duplicate_source_identity_is_rejected(self):
        self.chunks.insert(0, copy.deepcopy(self.chunks[0]))
        self.assertIsNone(self.binding())

    def test_malformed_chunk_fails_closed_without_exception(self):
        self.publish_binding()
        (self.root / 'data/source-text-chunks.jsonl').write_text('null\n', encoding='utf-8')
        self.assertTrue(live_review_errors(self.root, [self.provision['provision_id']], '2026-09-13'))


class StagedSourceReplayTests(unittest.TestCase):
    def test_each_staged_candidate_replays_exact_pdf_spans(self):
        from pypdf import PdfReader
        from extract_source_text import normalise

        candidates = json.loads((ROOT / 'data/clause-binding-candidates.json').read_text(
            encoding='utf-8-sig'))['candidates']
        provisions = json.loads((ROOT / 'data/provision-version-register.json').read_text(
            encoding='utf-8-sig'))['provisions']
        rows = [json.loads(line) for line in (ROOT / 'data/source-text-chunks.jsonl').read_text(
            encoding='utf-8-sig').splitlines() if line.strip()]
        readers, pages = {}, {}
        for candidate in candidates:
            with self.subTest(provision=candidate['provision_id']):
                matching = [p for p in provisions if p['provision_id'] == candidate['provision_id']]
                self.assertEqual(len(matching), 1)
                self.assertEqual(candidate['provision_sha256'], digest(matching[0]))
                self.assertEqual(candidate['verified_as_of'], '2026-09-13')
                self.assertEqual(candidate['operative_from'], matching[0]['valid_from'])
                selected = []
                for span_id in candidate['source_span_ids']:
                    matches = [r for r in rows if 'source-span:' + r['chunk_id'] == span_id]
                    self.assertEqual(len(matches), 1, span_id)
                    row = matches[0]
                    selected.append(row)
                    path = (ROOT / row['snapshot_path']).resolve()
                    self.assertTrue(path.is_relative_to(ROOT))
                    if path not in readers:
                        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row['source_sha256'])
                        readers[path] = PdfReader(path)
                    page_number = int(row['locator'].removeprefix('page:'))
                    key = (path, page_number)
                    if key not in pages:
                        pages[key] = normalise(readers[path].pages[page_number - 1].extract_text() or '')
                    start, end = row['character_start'], row['character_end']
                    self.assertTrue(0 <= start < end <= len(pages[key]))
                    self.assertEqual(pages[key][start:end].strip(), row['text'], span_id)
                    self.assertEqual(hashlib.sha256(row['text'].encode()).hexdigest(), row['text_sha256'])
                    self.assertEqual(row['canonical_url'], candidate['official_url'])
                self.assertEqual(digest(selected), candidate['span_record_sha256'])
                self.assertEqual(sorted({r['source_sha256'] for r in selected}), candidate['source_sha256_values'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
