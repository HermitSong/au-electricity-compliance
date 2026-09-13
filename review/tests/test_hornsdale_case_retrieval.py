from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from answer_kb import expand_case_chains
from case_chains import selected_research_chains


class HornsdaleCaseRetrievalTests(unittest.TestCase):
    def test_explicit_named_battery_case_includes_lifecycle_and_court_orders(self):
        chain = selected_research_chains(ROOT, [], 'Review Hornsdale Power Reserve FCAS.')
        self.assertIn('hornsdale-power-reserve-fcas', chain)
        rows = expand_case_chains(ROOT, ROOT / 'data/search-index.sqlite3', [], 'Review Hornsdale Power Reserve FCAS.')
        ids = {row['evidence_id'] for row in rows}
        self.assertTrue({'event:' + event for event in chain['hornsdale-power-reserve-fcas']['event_ids']} <= ids)
        self.assertTrue(set(chain['hornsdale-power-reserve-fcas']['source_evidence_ids']) <= ids)
        self.assertTrue(any('final-court' in row['status'] for row in rows))
        self.assertTrue(any('allegations' in row['status'] for row in rows))

    def test_wind_farm_is_not_alias_of_battery_case(self):
        self.assertNotIn('hornsdale-power-reserve-fcas', selected_research_chains(ROOT, [], 'HWF 1 Hornsdale wind farm protection settings.'))

    def test_unqualified_acronym_is_not_an_alias(self):
        self.assertNotIn('hornsdale-power-reserve-fcas', selected_research_chains(ROOT, [], 'What is the HPR registration fee?'))

    def test_case_chain_never_grants_current_authority(self):
        chain = selected_research_chains(ROOT, [], '2022 FCA 738')['hornsdale-power-reserve-fcas']
        self.assertIs(chain['current_law_release'], False)
        self.assertIs(chain['operational_bindings_approved'], False)


if __name__ == '__main__':
    unittest.main()
