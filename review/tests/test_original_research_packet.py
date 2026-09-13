import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from answer_kb import packet_state, research_originals_section
from packet_contract import canonical_span_errors, packet_digest, research_original_errors, seal_packet


class OriginalResearchPacketTests(unittest.TestCase):
    def section(self, status='ok', results=None):
        with patch('answer_kb.search_research_originals', return_value={
                'query': 'ENGIE complaints', 'status': status,
                'results': [] if results is None else results,
                'warnings': [], 'use_limit': 'Research only.'}):
            return research_originals_section(ROOT, 'ENGIE complaints', {'route_state': 'routed'}, 6)

    def packet(self):
        return {'question': 'ENGIE complaints', 'applicability': {'route_state': 'routed'},
                'evidence': [], 'research_originals': self.section()}

    def test_originals_are_separate_and_not_approval(self):
        result = self.section()
        self.assertFalse(result['supports_current_law_drafting'])
        self.assertFalse(result['may_execute'])
        self.assertIn('label alone does not establish', result['applicability_use_limit'])
        self.assertIn('source-stated compliance observations', result['applicability_use_limit'])
        self.assertIn('not publication', result['date_use_limit'])

    def test_ambiguous_context_does_not_run_archive_search(self):
        with patch('answer_kb.search_research_originals') as search:
            result = research_originals_section(ROOT, 'Can we do this?', {'route_state': 'needs-applicability-input'}, 6)
        search.assert_not_called()
        self.assertEqual(result['status'], 'not-run-applicability-unresolved')
        self.assertEqual(result['results'], [])

    def test_archive_absence_is_disclosed_not_no_matches(self):
        self.assertEqual(self.section('archive-unavailable')['status'], 'archive-unavailable')

    def test_archive_retrieval_does_not_change_empty_canonical_packet_state(self):
        self.section(results=[{'research_id': 'original:test'}])
        self.assertEqual(packet_state([], [], False)[0], 'insufficient-evidence')

    def test_research_metadata_is_part_of_packet_identity(self):
        packet = self.packet()
        seal_packet(packet, ROOT)
        changed = copy.deepcopy(packet)
        changed['research_originals']['results'].append({'research_id': 'original:changed'})
        self.assertNotEqual(packet['packet_id'], packet_digest(changed))

    def test_resealed_promotion_still_fails(self):
        packet = self.packet()
        packet['research_originals']['supports_current_law_drafting'] = True
        seal_packet(packet, ROOT)
        self.assertTrue(any('promote' in error for error in research_original_errors(packet, ROOT)))

    def test_archive_evidence_cannot_be_moved_into_controlling_lane(self):
        packet = self.packet()
        packet['evidence'] = [{'evidence_id': 'original:hash', 'doc_type': 'official-source-span'}]
        self.assertTrue(any('controlling evidence' in error for error in research_original_errors(packet, ROOT)))

    def test_relabelled_original_retains_a_provenance_guard(self):
        for origin in ({'research_id': 'original:hash'}, {'source_path': 'source-originals/objects/a.json'},
                       {'source_artifact': {'snapshot_path': 'source-originals\\objects\\a.html'}}):
            with self.subTest(origin=origin):
                packet = self.packet()
                packet['evidence'] = [{'evidence_id': 'source-span:made-up', 'doc_type': 'official-source-span', **origin}]
                self.assertTrue(any('controlling evidence' in error for error in research_original_errors(packet, ROOT)))

    def test_erased_origin_cannot_manufacture_a_canonical_span(self):
        packet = self.packet()
        packet['evidence'] = [{'evidence_id': 'source-span:made-up', 'doc_type': 'official-source-span'}]
        self.assertTrue(canonical_span_errors(packet, ROOT))

    def test_real_canonical_span_requires_unchanged_text_and_provenance(self):
        chunk = json.loads((ROOT / 'data/source-text-chunks.jsonl').read_text(encoding='utf-8-sig').splitlines()[0])
        fields = {'text': 'text', 'official_url': 'canonical_url', 'related_official_url': 'parent_canonical_url',
                  'source_path': 'snapshot_path', 'source_locator': 'locator',
                  'source_text_sha256': 'text_sha256', 'source_snapshot_sha256': 'source_sha256'}
        item = {'evidence_id': 'source-span:' + chunk['chunk_id'], 'doc_type': 'official-source-span',
                **{key: chunk.get(source_key) for key, source_key in fields.items()}}
        self.assertEqual(canonical_span_errors({'evidence': [item]}, ROOT), [])
        for key in fields:
            with self.subTest(key=key):
                self.assertTrue(canonical_span_errors({'evidence': [{**item, key: 'Altered'}]}, ROOT))

    def test_resealing_cannot_remove_or_reverse_canonical_use_limits(self):
        for key in ('date_use_limit', 'applicability_use_limit', 'use_limit'):
            for replacement in (None, 'This is approved current law.'):
                with self.subTest(key=key, replacement=replacement):
                    packet = self.packet()
                    packet['research_originals'][key] = replacement
                    seal_packet(packet, ROOT)
                    self.assertTrue(any('use limit' in error for error in research_original_errors(packet, ROOT)))

    def test_entry_points_do_not_require_acquisition_site_packages(self):
        script = ('import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); '
                  'import answer_kb, packet_contract, build_operational_brief; '
                  'result=answer_kb.research_originals_section(Path(sys.argv[2]), "billing", {"route_state":"routed"}, 6); '
                  'assert result["status"]=="archive-unavailable"; print("stdlib entry points passed")')
        with tempfile.TemporaryDirectory() as temporary:
            completed = subprocess.run([sys.executable, '-B', '-S', '-c', script, str(ROOT / 'scripts'), temporary],
                                       capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_query_mismatch_is_detected_after_resealing(self):
        packet = self.packet()
        packet['research_originals']['query'] = 'Different issue'
        seal_packet(packet, ROOT)
        self.assertTrue(any('question' in error for error in research_original_errors(packet, ROOT)))

    def test_source_validator_is_called_for_resealed_results(self):
        packet = self.packet()
        packet['research_originals']['results'] = [{'research_id': 'original:forged'}]
        with patch('packet_contract.validate_research_results', return_value=['Forged source text.']) as validate:
            errors = research_original_errors(packet, ROOT)
        validate.assert_called_once_with(ROOT, packet['research_originals']['results'])
        self.assertIn('Forged source text.', errors)

    def test_false_status_and_invalid_limit_are_rejected(self):
        packet = self.packet()
        packet['research_originals'].update(status='no-matches', requested_limit=True,
                                           results=[{'research_id': 'original:forged'}])
        with patch('packet_contract.validate_research_results', return_value=[]):
            errors = research_original_errors(packet, ROOT)
        self.assertTrue(any('contradicts' in error for error in errors))
        self.assertTrue(any('limit is invalid' in error for error in errors))

    def test_brief_keeps_research_chain_and_rejects_a_stale_ready_label(self):
        packet = json.loads((ROOT / 'review/results/centrepay-answer-packet-2026-09-06.json').read_text(encoding='utf-8'))
        packet['release_state'] = 'ready-for-grounded-drafting'
        packet['research_originals'] = self.section('archive-unavailable')
        packet['research_originals']['query'] = packet['question']
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'packet.json'
            path.write_text(json.dumps(packet), encoding='utf-8')
            completed = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build_operational_brief.py'),
                                        '--root', str(ROOT), '--packet', str(path)],
                                       capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 2, completed.stderr)
        brief = json.loads(completed.stdout)
        self.assertFalse(brief['may_execute'])
        self.assertEqual(brief['operational_release_state'], 'blocked')
        self.assertEqual(brief['research_case_chains'], packet['research_case_chains'])
        self.assertEqual(brief['research_originals'], packet['research_originals'])
        self.assertTrue(any('identity' in error or 'canonical input' in error for error in brief['blockers']))

    def test_brief_quarantines_renamed_originals_and_reversed_warnings(self):
        packet = json.loads((ROOT / 'review/results/centrepay-answer-packet-2026-09-06.json').read_text(encoding='utf-8'))
        packet['research_originals'] = self.section('archive-unavailable')
        packet['research_originals']['use_limit'] = 'This is approved current law.'
        packet['evidence'].append({
            'evidence_id': 'source-span:made-up', 'doc_type': 'official-source-span',
            'official_url': 'https://example.invalid/original', 'source_path': 'source-originals/objects/test.json',
        })
        seal_packet(packet, ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'packet.json'
            path.write_text(json.dumps(packet), encoding='utf-8')
            completed = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/build_operational_brief.py'),
                                        '--root', str(ROOT), '--packet', str(path)],
                                       capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 2, completed.stderr)
        brief = json.loads(completed.stdout)
        self.assertEqual(brief['official_source_spans'], [])
        self.assertIsNone(brief['research_originals'])
        self.assertTrue(brief['quarantined_evidence']['rejected_source_spans'])
        self.assertTrue(brief['quarantined_evidence']['rejected_research_originals'])
        self.assertFalse(brief['may_execute'])


if __name__ == '__main__':
    unittest.main()
