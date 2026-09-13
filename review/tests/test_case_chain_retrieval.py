import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_temporal_links import temporal_classification
from case_lookup import load_research_chains
from case_chains import selected_research_chains
from packet_contract import input_digests, seal_packet, validate_packet


class CaseChainTests(unittest.TestCase):
    def test_answer_packet_selects_case_chain_by_event_identity(self):
        evidence = [{'evidence_id': 'event:au-fcafc-2026-08-19-agl-centrepay-appeal'}]
        self.assertEqual(list(selected_research_chains(ROOT, evidence)), ['agl-centrepay-rule31'])
        self.assertEqual(selected_research_chains(ROOT, [{'evidence_id': 'event:unrelated'}]), {})

    def test_explicit_named_case_does_not_depend_on_lexical_search(self):
        self.assertIn('agl-centrepay-rule31', selected_research_chains(ROOT, [], 'How does the AGL Centrepay appeal affect refunds?'))
        self.assertIn('agl-centrepay-rule31', selected_research_chains(ROOT, [], 'Explain [2026] FCAFC 106.'))
        self.assertEqual(selected_research_chains(ROOT, [], 'AGL disconnection hardship'), {})

    def test_resealed_packet_cannot_omit_case_chain(self):
        packet = {'question': 'AGL Centrepay appeal', 'evidence': [
            {'evidence_id': 'event:au-fcafc-2026-08-19-agl-centrepay-appeal'}]}
        seal_packet(packet, ROOT)
        errors = validate_packet(packet, ROOT, {'question': packet['question']})
        self.assertTrue(any('omits or changes' in error for error in errors))

    def test_chain_deletion_invalidates_input_set(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root / 'data/reviewed-case-chains'
            directory.mkdir(parents=True)
            before = input_digests(root)['research_case_chain_set']
            path = directory / 'chain.json'
            path.write_text('{}', encoding='utf-8')
            self.assertNotEqual(input_digests(root)['research_case_chain_set'], before)
            path.unlink()
            self.assertEqual(input_digests(root)['research_case_chain_set'], before)
    def test_appeal_allowed_is_not_itself_quashed(self):
        event = {'event_type': 'appeal-judgment', 'status': 'appeal-allowed',
                 'case_status_note': 'The earlier penalty was quashed.'}
        self.assertEqual(temporal_classification(event, [])[0], 'appellate-control')

    def test_historical_relief_remains_displaced(self):
        self.assertEqual(temporal_classification({'status': 'quashed-on-appeal'}, [])[0], 'quashed-or-overturned')

    def test_chain_connects_all_three_existing_events_without_approval(self):
        chains, events = load_research_chains(ROOT)
        chain = chains['agl-centrepay-rule31']
        self.assertEqual(len(chain['event_ids']), 3)
        self.assertFalse(chain['current_law_release'])
        self.assertFalse(chain['supports_current_law_drafting'])
        self.assertFalse(chain['later_status']['no_further_appeal_claim'])
        self.assertTrue(chain['later_status']['later_activity_observed'])
        self.assertEqual(len(chain['research_artifact_sha256']), 64)
        for event in chain['event_ids']:
            self.assertIn(chain['chain_id'], events[event])

    def test_chain_cannot_silently_promote_release(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            directory = root / 'data/reviewed-case-chains'
            directory.mkdir(parents=True)
            (directory / 'bad.json').write_text(json.dumps({'chain_id': 'bad', 'current_law_release': True}), encoding='utf-8')
            with self.assertRaises(ValueError):
                load_research_chains(root)

    def test_canonical_status_subject_and_event_time_posture(self):
        events = {r['event_id']: r for r in (json.loads(line) for line in
                  (ROOT / 'data/enforcement-events-full.jsonl').read_text(encoding='utf-8-sig').splitlines())}
        self.assertEqual(events['au-fcafc-2026-08-19-agl-centrepay-appeal']['status'], 'appeal-allowed')
        start = events['au-aer-2022-12-16-agl-alleged-breaches-overcharging-obligations']
        self.assertEqual(start['status'], 'proceedings-allegations-only')
        self.assertIn('dismissed', start['case_status_note'])


if __name__ == '__main__':
    unittest.main()
