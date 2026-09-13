import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from collect_source_originals import discover, read_jsonl, save_object
from enumerate_source_indexes import enumerate_links
from merge_evidence_batch import merge, prepare
from collect_enumerated_sources import access_stop_reason


class EnumerationTests(unittest.TestCase):
    def test_access_pause_survives_resume(self):
        self.assertEqual(access_stop_reason([{'reason': 'http-403'}, {'capture_status': 'bytes-preserved'}]), 'http-403')
        self.assertEqual(access_stop_reason([{'reason': 'http-429'}]), 'http-429')
        self.assertIsNone(access_stop_reason([{'reason': 'http-404'}, {'reason': None}]))
    def capture(self, links):
        return {'canonical_url': 'https://www.aemo.com.au/reports', 'links': links,
                'source_family_ids': ['AEMO'], 'snapshot_path': 'capture.html',
                'sha256': 'abc', 'retrieved_at': '2026-09-06'}

    def test_keeps_versions_not_events(self):
        capture = self.capture([{'url': 'https://www.aemo.com.au/file.pdf?rev=2', 'text': 'Report'},
                                {'url': 'https://www.aemo.com.au/file.pdf?rev=1', 'text': 'Report'},
                                {'url': 'https://www.aemo.com.au/file.pdf?rev=2#page=3', 'text': 'Report'}])
        rows = enumerate_links([capture], {'https://www.aemo.com.au/file.pdf?rev=1'})
        self.assertEqual(len(rows), 2)
        self.assertEqual(sum(r['known_exact_url'] for r in rows), 1)
        self.assertEqual(rows[1]['same_path_other_urls'], ['https://www.aemo.com.au/file.pdf?rev=1'])
        self.assertIs(rows[1]['current_law_release'], False)

    def test_scope_and_detail_pages(self):
        links = [{'url': url, 'label': 'Report'} for url in (
            'https://www.aemo.com.au/reports/detail', 'https://www.aemo.com.au/about',
            'https://example.com/report.pdf', 'http://www.aemo.com.au/report.pdf')]
        rows = enumerate_links([self.capture(links)], set())
        self.assertEqual([r['document_role'] for r in rows], ['report-detail-page'])

    def test_browser_link_text_supported(self):
        for key in ('label', 'text'):
            row = {'canonical_url': 'https://www.aemo.com.au/reports', 'discovery_depth': 0,
                   'extraction_status': 'extracted-unreviewed', 'source_family_ids': ['AEMO'],
                   'links': [{'url': 'https://www.aemo.com.au/report.pdf', key: 'Electricity report'}]}
            self.assertEqual(discover(row, {'aemo.com.au'}, 2)[0]['link_label'], 'Electricity report')


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'archive'
        self.batch = Path(self.temp.name) / 'delta'
        for path in (self.root / 'data', self.root / 'source-originals', self.root / 'review/results',
                     self.batch / 'source-originals'):
            path.mkdir(parents=True)
        (self.root / 'source-originals/manifest.jsonl').write_text('', encoding='utf-8')
        (self.root / 'data/source-original-inventory.jsonl').write_text('', encoding='utf-8')
        (self.root / 'data/source-original-summary.json').write_text('{"initial_seed_url_count":0}', encoding='utf-8')
        path, sha = save_object(self.batch, b'<main>Original report</main>', '.html')
        text, text_sha = save_object(self.batch, b'[{"locator":"paragraph:1","text":"Original report"}]', '.json')
        self.row = {'canonical_url': 'https://www.aemo.com.au/report', 'references': [],
                    'source_family_ids': ['AEMO'], 'discovery_depth': 1, 'discovered_from': [],
                    'snapshot_path': path, 'sha256': sha, 'text_path': text, 'text_sha256': text_sha,
                    'capture_status': 'bytes-preserved', 'extraction_status': 'extracted-unreviewed',
                    'legal_review_status': 'not-reviewed', 'current_law_release': False}
        self.write_batch()

    def write_batch(self):
        (self.batch / 'source-originals/manifest.jsonl').write_text(json.dumps(self.row) + '\n', encoding='utf-8')

    def test_corrupt_delta_does_not_change_destination(self):
        (self.batch / self.row['text_path']).write_bytes(b'corrupt')
        with self.assertRaises(ValueError):
            merge(self.root, [self.batch], [], None)
        self.assertEqual((self.root / 'source-originals/manifest.jsonl').read_text(), '')
        self.assertFalse((self.root / 'source-originals/objects').exists())

    def test_path_escape_rejected(self):
        self.row['snapshot_path'] = '../outside.html'
        self.write_batch()
        with self.assertRaises(ValueError):
            prepare(self.root, [self.batch], [])

    def test_release_promotion_rejected(self):
        self.row['current_law_release'] = True
        self.write_batch()
        with self.assertRaises(ValueError):
            prepare(self.root, [self.batch], [])

    def test_existing_corrupt_object_not_overwritten(self):
        target = self.root / self.row['snapshot_path']
        target.parent.mkdir(parents=True)
        target.write_bytes(b'old corrupt bytes')
        with self.assertRaises(ValueError):
            prepare(self.root, [self.batch], [])
        self.assertEqual(target.read_bytes(), b'old corrupt bytes')

    def test_unattempted_urls_stay_in_denominator_and_rerun_deduplicates(self):
        pending = {'canonical_url': 'https://www.aemo.com.au/other.pdf?rev=2',
                   'source_family_ids': ['AEMO'], 'references': [], 'discovered_from': [], 'discovery_depth': 1}
        first = merge(self.root, [self.batch], [pending], None)
        second = merge(self.root, [self.batch], [pending], None)
        self.assertEqual(first['inventory_urls_after'], 2)
        self.assertEqual(first['newly_enumerated_urls_without_text'], 1)
        self.assertEqual(second['manifest_rows_to_append'], 0)
        self.assertEqual(len(read_jsonl(self.root / 'source-originals/manifest.jsonl')), 1)

    def test_failed_rebuild_restores_manifest_and_inventory(self):
        with patch('merge_evidence_batch.rebuild_outputs', side_effect=RuntimeError('index failed')):
            with self.assertRaises(RuntimeError):
                merge(self.root, [self.batch], [], None)
        self.assertEqual((self.root / 'source-originals/manifest.jsonl').read_text(), '')
        self.assertEqual((self.root / 'data/source-original-inventory.jsonl').read_text(), '')

    def test_missing_enumeration_evidence_rejected(self):
        entry = {**self.row, 'source_index_evidence': [{'snapshot_path': self.row['snapshot_path'], 'sha256': '0' * 64}]}
        with self.assertRaises(ValueError):
            prepare(self.root, [self.batch], [entry])

    def test_completed_ocr_handoff_wins_over_earlier_engine_logs(self):
        final = {**self.row, 'extraction_method': 'tesseract-with-rapidocr-comparison'}
        (self.batch / 'source-originals/recovery-priority-ocr.jsonl').write_text(json.dumps(final) + '\n', encoding='utf-8')
        _, pending, _, _ = prepare(self.root, [self.batch], [])
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]['extraction_method'], final['extraction_method'])


if __name__ == '__main__':
    unittest.main()
