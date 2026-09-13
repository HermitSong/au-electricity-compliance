import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from answer_kb import research_originals_section, research_readings_section
from packet_contract import research_original_errors, seal_packet, packet_digest
from read_source_originals import expand_research_results, read_original, validate_reading_section, MAX_TOTAL_CHARS
from search_source_originals import _source_metadata, _research_id


class SourceReadingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'source-originals/objects').mkdir(parents=True)
        self.rows = []
        self.units = [
            {'locator': 'page:1', 'text': 'Example Energy. Court decision. Cover page only.'},
            {'locator': 'page:2', 'text': 'Procedural introduction. Counsel and hearing history.'},
            {'locator': 'page:3', 'text': 'Billing notification handoff failed. A team left amended bills in an unmonitored inbox.\nThe notification workflow was later changed.'},
            {'locator': 'page:4', 'text': 'Historical exceptions and conditions. These findings do not identify present law.'},
        ]
        self.seed = self.source('https://www.regulator.gov.au/example', self.units)
        self.query = 'What billing notification handoff failed at Example Energy?'

    def source(self, url, units):
        binary = ('Preserved synthetic original: ' + url).encode()
        text = json.dumps(units).encode()
        sh, th = hashlib.sha256(binary).hexdigest(), hashlib.sha256(text).hexdigest()
        sp, tp = 'source-originals/objects/' + sh + '.bin', 'source-originals/objects/' + th + '.json'
        (self.root / sp).write_bytes(binary)
        (self.root / tp).write_bytes(text)
        row = {'canonical_url': url, 'capture_status': 'bytes-preserved', 'snapshot_path': sp, 'sha256': sh,
               'text_path': tp, 'text_sha256': th, 'title': 'Example source', 'retrieved_at': '2026-09-09',
               'extraction_status': 'extracted-unreviewed', 'legal_review_status': 'not-reviewed',
               'current_law_release': False, 'page_count': len(units), 'pages_without_text': []}
        self.rows.append(row)
        (self.root / 'source-originals/manifest.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in self.rows))
        seed = dict(_source_metadata(row), locator=units[0]['locator'], excerpt=units[0]['text'][:1600])
        seed['research_id'] = _research_id(seed)
        return seed

    def expanded(self, **kwargs):
        return expand_research_results(self.root, self.query, [self.seed], **kwargs)

    def test_cover_seed_opens_relevant_body_without_target_locator(self):
        result = self.expanded(passages_per_source=1)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['results'][0]['locator'], 'page:3')
        self.assertIn('unmonitored inbox', result['results'][0]['text'])
        self.assertFalse(result['supports_current_law_drafting'])
        self.assertFalse(result['may_execute'])
        self.assertEqual(validate_reading_section(self.root, result, query=self.query, seeds=[self.seed]), [])

    def test_deterministic_exact_ranges_and_offsets(self):
        before = self.expanded()
        self.assertEqual(before, self.expanded())
        units = {row['locator']: row['text'] for row in self.units}
        for row in before['results']:
            self.assertEqual(row['text'], units[row['locator']][row['start_char']:row['end_char']])
            self.assertTrue(row['reading_id'].startswith('reading:'))

    def test_reader_exposes_neighbor_context(self):
        result = read_original(self.root, self.seed['url'], 'page:3')
        self.assertEqual(result['result']['previous_locator'], 'page:2')
        self.assertEqual(result['result']['next_locator'], 'page:4')
        continuation = result['continuation']
        self.assertEqual(continuation['locator'], 'page:4')
        next_read = read_original(self.root, **continuation)
        self.assertIn('exceptions', next_read['result']['text'])

    def test_long_unit_continuation_reconstructs_original_without_gaps(self):
        text = ('Exact billing narrative with multiple paragraphs.\n' * 200)
        seed = self.source('https://www.regulator.gov.au/long', [{'locator': 'html:main', 'text': text}])
        request = {'url': seed['url'], 'locator': 'html:main', 'offset': 0}
        actual = ''
        while request:
            result = read_original(self.root, **request, max_chars=113)
            actual += result['result']['text']
            request = result['continuation']
        self.assertEqual(actual, text)

    def test_hash_pin_rejects_changed_extraction(self):
        with self.assertRaisesRegex(ValueError, 'changed'):
            read_original(self.root, self.seed['url'], 'page:3', expected_text_sha256='0' * 64)

    def test_invalid_ranges_do_not_become_empty_success(self):
        for offset in (-1, True, 1.2, 100000000):
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                read_original(self.root, self.seed['url'], 'page:3', offset=offset)
        with self.assertRaises(ValueError):
            read_original(self.root, self.seed['url'], 'page:3', offset=len(self.units[2]['text']))

    def test_no_matches_and_empty_candidates_are_distinct(self):
        result = expand_research_results(self.root, 'unmatchedword', [self.seed])
        self.assertEqual(result['status'], 'no-matches')
        self.assertEqual(expand_research_results(self.root, self.query, [])['status'], 'no-source-candidates')
        self.assertEqual(expand_research_results(self.root, '', [self.seed])['status'], 'invalid-query')

    def test_empty_unit_is_not_substantive_text(self):
        seed = self.source('https://www.regulator.gov.au/blank', [
            {'locator': 'page:1', 'text': 'Title'}, {'locator': 'page:2', 'text': ''}])
        result = read_original(self.root, seed['url'], 'page:2')
        self.assertEqual(result['status'], 'empty-text-unit')
        self.assertEqual(result['result']['text'], '')

    def test_multiple_sources_keep_individual_budgets_and_provenance(self):
        long_text = 'Billing notification handoff. ' * 5000
        seeds = [self.source('https://www.regulator.gov.au/source-' + str(i),
                             [{'locator': 'html:main', 'text': long_text}]) for i in range(4)]
        result = expand_research_results(self.root, self.query, seeds)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual({row['url'] for row in result['results']}, {row['url'] for row in seeds})
        self.assertLessEqual(result['total_chars'], MAX_TOTAL_CHARS)
        self.assertEqual(validate_reading_section(self.root, result, query=self.query, seeds=seeds), [])

    def test_packet_expansion_identity_and_tampering(self):
        with patch('answer_kb.search_research_originals', return_value={
                'query': self.query, 'status': 'ok', 'results': [self.seed], 'warnings': []}):
            originals = research_originals_section(self.root, self.query, {'route_state': 'routed'}, 6)
        readings = research_readings_section(self.root, self.query, {'route_state': 'routed'}, originals, 'expanded')
        packet = {'question': self.query, 'applicability': {'route_state': 'routed'}, 'evidence': [],
                  'research_originals': originals, 'research_readings': readings, 'research_depth': 'expanded'}
        self.assertEqual(research_original_errors(packet, self.root), [])
        seal_packet(packet, self.root)
        changed = copy.deepcopy(packet)
        changed['research_readings']['results'][0]['text'] = 'Fabricated approval.'
        self.assertNotEqual(packet_digest(changed), packet['packet_id'])
        seal_packet(changed, self.root)
        self.assertTrue(research_original_errors(changed, self.root))

    def test_unresolved_or_excerpts_mode_does_not_open_source_text(self):
        for route, depth, expected in [('needs-applicability-input', 'expanded', 'not-run-applicability-unresolved'),
                                       ('routed', 'excerpts', 'not-requested')]:
            with self.subTest(route=route), patch('read_source_originals._source') as read:
                result = research_readings_section(self.root, self.query, {'route_state': route},
                                                   {'results': [self.seed], 'status': 'ok'}, depth)
            read.assert_not_called()
            self.assertEqual(result['status'], expected)
            self.assertFalse(result['results'])

    def test_standalone_reader_has_no_acquisition_dependency(self):
        result = subprocess.run([sys.executable, '-B', '-S', str(ROOT / 'scripts/read_source_originals.py'),
                                 self.seed['url'], '--root', str(self.root), '--locator', 'page:3'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('unmonitored inbox', json.loads(result.stdout)['result']['text'])


if __name__ == '__main__':
    unittest.main()
