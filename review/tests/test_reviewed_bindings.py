"""Synthetic checks of scoped review admission, not legal accuracy measurements."""
import copy
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from reviewed_bindings import digest, reviewed_binding, live_review_errors
from route_applicability import provision_routes


class ReviewedBindingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.today = date.today().isoformat()
        self.provision = {'provision_id': 'SYNTHETIC-ONLY', 'status': 'current-at-baseline',
                          'official_url': 'https://example.invalid/synthetic-source.txt'}
        source = b'Synthetic exact provision with an exception.'
        self.write('official-snapshots/source.txt', source)
        source_hash = hashlib.sha256(source).hexdigest()
        self.chunk = {'chunk_id': 'synthetic', 'canonical_url': self.provision['official_url'],
                      'snapshot_path': 'official-snapshots/source.txt', 'source_sha256': source_hash,
                      'locator': 'synthetic:1', 'text': source.decode(), 'text_sha256': source_hash}
        self.candidate = {'provision_id': self.provision['provision_id'], 'provision_sha256': digest(self.provision),
                          'prepared_by': 'fixture-author', 'verified_as_of': self.today, 'operative_from': self.today,
                          'official_url': self.provision['official_url'], 'clause_scope': 'Synthetic clause only',
                          'source_span_ids': ['source-span:synthetic'], 'source_sha256_values': [source_hash],
                          'span_record_sha256': digest([self.chunk]), 'applicability_limit': 'Synthetic only; not real law.'}
        self.approval = {'candidate_sha256': digest(self.candidate), 'reviewer_id': 'fixture-reviewer',
                         'reviewed_at': self.today, 'result': 'approved-for-scoped-drafting',
                         'review_note': 'Synthetic test receipt; no actual source verification.'}
        self.save()

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value if isinstance(value, bytes) else json.dumps(value).encode())

    def save(self):
        self.write('data/clause-binding-candidates.json', {'candidates': [self.candidate]})
        self.write('data/clause-binding-approvals.json', {'approvals': [self.approval]})
        self.write('data/provision-version-register.json', {'provisions': [self.provision]})
        self.write('data/source-text-chunks.jsonl', self.chunk)
        binding = reviewed_binding(self.root, self.provision, [self.chunk])
        self.write('data/provision-source-bindings.json', {'bindings': [binding] if binding else []})
        return binding

    def test_complete_receipt_allows_only_scoped_drafting(self):
        binding = self.save()
        self.assertTrue(binding['supports_current_law_drafting'])
        self.assertFalse(binding['supports_operational_execution'])
        self.assertEqual(live_review_errors(self.root, ['SYNTHETIC-ONLY'], self.today), [])

    def test_missing_receipt_does_not_approve_text(self):
        self.write('data/clause-binding-approvals.json', {'approvals': []})
        self.assertIsNone(reviewed_binding(self.root, self.provision, [self.chunk]))

    def test_preparer_cannot_self_approve(self):
        self.approval['reviewer_id'] = self.candidate['prepared_by']
        self.assertIsNone(self.save())

    def test_other_dates_require_new_review(self):
        for delta in (-1, 1):
            self.assertTrue(live_review_errors(self.root, ['SYNTHETIC-ONLY'], (date.today() + timedelta(days=delta)).isoformat()))

    def test_future_review_date_rejected(self):
        self.approval['reviewed_at'] = (date.today() + timedelta(days=1)).isoformat()
        self.assertIsNone(self.save())

    def test_provision_edit_invalidates_approval(self):
        self.provision['scope'] = 'Changed applicability'
        self.assertIsNone(self.save())

    def test_source_edit_invalidates_approval(self):
        self.write('official-snapshots/source.txt', b'Changed source')
        self.assertIsNone(reviewed_binding(self.root, self.provision, [self.chunk]))

    def test_quote_edit_and_rehash_does_not_reuse_receipt(self):
        self.chunk['text'] = 'An invented obligation.'
        self.chunk['text_sha256'] = hashlib.sha256(self.chunk['text'].encode()).hexdigest()
        self.candidate['span_record_sha256'] = digest([self.chunk])
        self.assertIsNone(self.save())

    def test_bound_scope_change_invalidates_receipt(self):
        self.candidate['applicability_limit'] = 'Every enterprise may execute'
        self.assertIsNone(self.save())

    def test_duplicate_approval_is_ambiguous(self):
        self.write('data/clause-binding-approvals.json', {'approvals': [self.approval, self.approval]})
        self.assertIsNone(reviewed_binding(self.root, self.provision, [self.chunk]))

    def test_changed_binding_flag_fails_runtime_replay(self):
        binding = self.save()
        binding['supports_operational_execution'] = True
        self.write('data/provision-source-bindings.json', {'bindings': [binding]})
        self.assertTrue(live_review_errors(self.root, ['SYNTHETIC-ONLY'], self.today))

    def test_every_route_must_have_its_own_review(self):
        self.assertTrue(live_review_errors(self.root, ['SYNTHETIC-ONLY', 'UNREVIEWED'], self.today))
        self.assertTrue(live_review_errors(self.root, [], self.today))

    def test_malformed_canonical_file_fails_closed(self):
        self.write('data/clause-binding-candidates.json', [])
        self.assertIsNone(reviewed_binding(self.root, self.provision, [self.chunk]))

    def test_historical_route_does_not_use_later_ner_version(self):
        args = (['National Electricity Market'], ['battery or BESS operator'], ['bidding and dispatch'])
        self.assertEqual(provision_routes(*args, as_of='2026-09-03'),
                         ['NER-REBIDDING-CURRENT-2026-08-29', 'NER-DISPATCH-CURRENT-2026-08-29'])
        self.assertEqual(provision_routes(*args, as_of='2026-09-04'),
                         ['NER-BIDDING-V254-2026-09-04', 'NER-DISPATCH-V254-2026-09-04'])

    def test_wa_battery_does_not_get_nem_registration_route(self):
        self.assertEqual(provision_routes(['Western Australia'], ['battery or BESS operator'], ['connection and registration'], self.today), [])


if __name__ == '__main__':
    unittest.main()
