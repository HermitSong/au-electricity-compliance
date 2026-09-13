import hashlib
import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from evaluate_original_retrieval import evaluation_provenance
from compare_research_retrieval import compare


class RetrievalEvaluationProvenanceTests(unittest.TestCase):
    def test_comparison_rejects_changed_archive_bank_or_targets(self):
        report = {'question_bank_sha256': 'bank', 'archive_manifest_sha256': 'manifest',
                  'archive_root': 'archive', 'search_code_sha256': 'code',
                  'summary': {'top_k_distinct_sources': 6},
                  'results': [{'id': 'test', 'question': 'question', 'expected_source_urls': ['url'],
                               'target_hit': False, 'elapsed_seconds': 1.0}]}
        improved = copy.deepcopy(report)
        improved['results'][0]['target_hit'] = True
        self.assertEqual(compare(report, improved)['gained_question_ids'], ['test'])
        self.assertEqual(compare(improved, report)['regressed_question_ids'], ['test'])
        for key in ('question_bank_sha256', 'archive_manifest_sha256', 'archive_root'):
            changed = copy.deepcopy(report)
            changed[key] = 'changed'
            with self.assertRaises(ValueError):
                compare(report, changed)
        for field in ('question', 'expected_source_urls'):
            changed = copy.deepcopy(report)
            changed['results'][0][field] = 'changed'
            with self.assertRaises(ValueError):
                compare(report, changed)

    def test_hashes_loaded_search_code_not_archive_root_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source-originals').mkdir()
            (root / 'source-originals/manifest.jsonl').write_bytes(b'[]\n')
            (root / 'scripts').mkdir()
            (root / 'scripts/search_source_originals.py').write_bytes(b'unrelated placeholder')
            actual = evaluation_provenance(root)
            expected = hashlib.sha256(Path(sys.modules['search_source_originals'].__file__).read_bytes()).hexdigest()
            self.assertEqual(actual['search_code_sha256'], expected)
            self.assertEqual(actual['archive_manifest_sha256'], hashlib.sha256(b'[]\n').hexdigest())
            self.assertEqual(set(actual['runtime_sha256']), {'search_source_originals', 'source_manifest', 'kb_search'})

    def test_changed_or_absent_manifest_cannot_keep_same_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source-originals').mkdir()
            manifest = root / 'source-originals/manifest.jsonl'
            manifest.write_bytes(b'first')
            before = evaluation_provenance(root)
            manifest.write_bytes(b'second')
            self.assertNotEqual(before, evaluation_provenance(root))
            manifest.unlink()
            with self.assertRaises(FileNotFoundError):
                evaluation_provenance(root)


if __name__ == '__main__':
    unittest.main()
