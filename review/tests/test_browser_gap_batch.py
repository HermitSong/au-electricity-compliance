import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from prepare_browser_gap_batch import prepare
from finalize_browser_gap_batch import redirect_relation
from collect_observed_attachments import collect


class BrowserGapTests(unittest.TestCase):
    def test_identical_url_is_not_a_redirect(self):
        self.assertIsNone(redirect_relation({'canonical_url': 'https://www.aer.gov.au/a',
                                             'response_url': 'https://www.aer.gov.au/a'}))

    def test_query_or_destination_change_requires_review(self):
        for suffix in ('?v=2', '/historical'):
            relation = redirect_relation({'canonical_url': 'https://www.aer.gov.au/a',
                                           'response_url': 'https://www.aer.gov.au/a' + suffix})
            self.assertFalse(relation['current_law_identity_verified'])
            self.assertEqual(relation['equivalence_status'], 'not-established')

    def test_cohort_excludes_existing_text_denials_and_malformed_urls(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root, output = base / 'archive', base / 'delta'
            (root / 'data').mkdir(parents=True)
            (root / 'review/results').mkdir(parents=True)
            urls = ['https://www.aer.gov.au/' + n for n in ('new', 'render', 'existing', 'denied', 'bad)**')]
            inventory = [{'canonical_url': u} for u in urls]
            states = [
                {'capture_status': 'not-attempted'},
                {'capture_status': 'bytes-preserved', 'extraction_status': 'needs-browser-rendering-or-content-review'},
                {'has_research_text': True}, {'capture_status': 'failed', 'reason': 'http-403'},
                {'capture_status': 'not-attempted'}]
            (root / 'data/source-original-inventory.jsonl').write_text(
                ''.join(json.dumps(r) + '\n' for r in inventory), encoding='utf-8')
            (root / 'review/results/delivery-readiness.json').write_text(json.dumps({'urls': [
                {'canonical_url': u, 'has_research_text': False, **s} for u, s in zip(urls, states)]}), encoding='utf-8')
            result = prepare(root, output)
            self.assertEqual(result['urls'], urls[:2])
            self.assertEqual(len(result['excluded']), 1)
            with self.assertRaises(FileExistsError):
                prepare(root, output)

    def test_rejects_output_inside_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                prepare(Path(temp), Path(temp) / 'delta')

    def attachment_fixture(self, base):
        evidence, output = base / 'evidence', base / 'delta'
        path = evidence / 'source-originals/objects/page.html'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'<main>Attachment links</main>')
        candidates = [{'canonical_url': 'https://www.aer.gov.au/system/files/' + name,
                       'source_index_evidence': [{'snapshot_path': 'source-originals/objects/page.html',
                           'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}]}
                      for name in ('a.pdf', 'b.pdf')]
        enumeration = evidence / 'enumeration.jsonl'
        enumeration.write_text(''.join(json.dumps(r) + '\n' for r in candidates), encoding='utf-8')
        return evidence, output, enumeration, candidates

    def test_site_denial_stops_host_and_cannot_be_retried_as_local_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            evidence, output, enumeration, _ = self.attachment_fixture(Path(temp))
            with patch('collect_observed_attachments.Fetcher') as factory:
                factory.return_value.fetch.side_effect = lambda row, root: {
                    **row, 'capture_status': 'failed', 'reason': 'http-403',
                    'legal_review_status': 'not-reviewed', 'current_law_release': False}
                outcomes = collect(enumeration, evidence, output)
                self.assertEqual(factory.return_value.fetch.call_count, 1)
                self.assertEqual(outcomes[1]['capture_status'], 'deferred')
                self.assertEqual(collect(enumeration, evidence, output, True), [])
                self.assertEqual(factory.return_value.fetch.call_count, 1)

    def test_local_failure_retry_keeps_previous_outcomes(self):
        with tempfile.TemporaryDirectory() as temp:
            evidence, output, enumeration, candidates = self.attachment_fixture(Path(temp))
            log = output / 'source-originals/recovery-attachments.jsonl'
            log.parent.mkdir(parents=True)
            log.write_text(''.join(json.dumps({**r, 'reason': 'robots-check-failed:URLError'}) + '\n'
                                   for r in candidates), encoding='utf-8')
            with patch('collect_observed_attachments.Fetcher') as factory:
                factory.return_value.fetch.side_effect = lambda row, root: {**row, 'capture_status': 'bytes-preserved'}
                self.assertEqual(collect(enumeration, evidence, output), [])
                self.assertEqual(len(collect(enumeration, evidence, output, True)), 2)
                self.assertEqual(len(log.read_text(encoding='utf-8').splitlines()), 4)

    def test_changed_link_provenance_is_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as temp:
            evidence, output, enumeration, _ = self.attachment_fixture(Path(temp))
            (evidence / 'source-originals/objects/page.html').write_bytes(b'changed')
            with patch('collect_observed_attachments.Fetcher') as factory:
                with self.assertRaises(ValueError):
                    collect(enumeration, evidence, output)
                factory.assert_not_called()


if __name__ == '__main__':
    unittest.main()
