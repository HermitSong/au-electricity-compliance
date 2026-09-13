import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import answer_workflow as workflow
from answer_kb import expand_case_chains
from case_chains import selected_research_chains
from reviewed_bindings import live_review_errors


class PublicDistributionTests(unittest.TestCase):
    def test_empty_source_contract_has_no_distributed_official_text(self):
        self.assertFalse((ROOT / 'data/source-text-chunks.jsonl').read_text('utf-8').strip())

    def test_historical_receipts_do_not_approve_missing_originals(self):
        data = json.loads((ROOT / 'data/clause-binding-candidates.json').read_text('utf-8-sig'))
        for row in data['candidates']:
            with self.subTest(provision=row['provision_id']):
                self.assertTrue(live_review_errors(ROOT, [row['provision_id']], '2026-09-13'))

    def test_hpr_public_events_retain_missing_source_boundary(self):
        chain = selected_research_chains(ROOT, [], 'Hornsdale Power Reserve FCAS')['hornsdale-power-reserve-fcas']
        self.assertFalse(chain['source_evidence_ids'])
        self.assertEqual(len(chain['undistributed_source_evidence_ids']), 2)
        rows = expand_case_chains(ROOT, ROOT / 'data/search-index.sqlite3', [], 'Hornsdale Power Reserve FCAS')
        self.assertTrue({'event:' + value for value in chain['event_ids']} <= {r['evidence_id'] for r in rows})
        self.assertFalse(any(r['doc_type'] == 'official-source-span' for r in rows))
        self.assertFalse(chain['current_law_release'])

    def test_public_handoff_searches_without_granting_current_authority(self):
        from test_answer_workflow import request
        item = request()
        item['question'] = 'What battery registration obligations apply to an integrated resource provider?'
        item['context'].update(jurisdiction='National Electricity Market', actor='battery or BESS operator', activity='connection and registration', as_of='2026-09-13')
        item['known_cases'] = []
        with tempfile.TemporaryDirectory() as folder:
            result = workflow.workflow(item, None, ROOT, Path(folder) / 'handoff')
        self.assertEqual(result['final_status'], 'handoff-not-integrated-model')
        self.assertFalse(result['action_permission'])
        self.assertFalse(result['current_legal_release'])
        self.assertTrue(result['packet_gates'])
        self.assertTrue(all(not gate['current_law_eligible'] for gate in result['packet_gates'].values()))


if __name__ == '__main__':
    unittest.main()
