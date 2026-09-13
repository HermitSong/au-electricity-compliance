"""Scoring-policy tests; synthetic declarations are not legal review evidence."""
import copy
import unittest

from evaluate_answer_quality import assess


def reviewed():
    return {
        'id': 'SYNTHETIC-001', 'correctness': 'correct', 'completeness': 'complete',
        'case_search': 'known-relevant', 'case_citation': 'missing',
        'official_verification': {
            'source_urls': ['https://example.invalid/official-rule-fixture'],
            'jurisdiction': 'Synthetic jurisdiction', 'as_of': '2026-09-08',
            'reason': 'Synthetic reviewer declaration for a unit test.',
            'assessed_scope': 'Fixture claim, not a real compliance answer.',
            'reviewed_against_official_sources': True,
        },
    }


class QualityTests(unittest.TestCase):
    def test_correct_without_answer_citation_is_not_wrong(self):
        result = assess(reviewed())
        self.assertEqual(result['correctness'], 'correct')
        self.assertEqual(result['outcome'], 'correct-with-case-citation-deficiency')
        self.assertFalse(result['current_law_release'])
        self.assertFalse(result['may_execute'])

    def test_unverified_is_neither_correct_nor_wrong(self):
        row = reviewed()
        row['correctness'] = 'unverified'
        row.pop('official_verification')
        self.assertEqual(assess(row)['outcome'], 'needs-review')

    def test_unknown_case_search_is_pending(self):
        row = reviewed()
        row.update(case_search='not-assessed', case_citation='not-assessed')
        self.assertEqual(assess(row)['outcome'], 'correct-with-case-review-pending')

    def test_missing_evidence_cannot_establish_incorrectness(self):
        row = reviewed()
        row['correctness'] = 'incorrect'
        with self.assertRaises(ValueError):
            assess(row)

    def test_actual_official_conflict_can_be_incorrect(self):
        row = reviewed()
        row['correctness'] = 'incorrect'
        row['official_verification'].update(contradicted_answer_claim='Fixture claim X', official_conflict='Fixture source contradicts X')
        self.assertEqual(assess(row)['outcome'], 'incorrect')

    def test_completeness_is_separate(self):
        row = reviewed()
        row['completeness'] = 'partial'
        result = assess(row)
        self.assertEqual(result['outcome'], 'correct-but-incomplete')
        self.assertEqual(result['case_citation'], 'missing')

    def test_abstention_is_not_automatically_correct(self):
        row = reviewed()
        row.update(correctness='not-answered', completeness='not-answered')
        self.assertEqual(assess(row)['outcome'], 'unanswered')

    def test_case_with_relevance_and_time_review_can_pass(self):
        row = reviewed()
        row.update(case_citation='compliant', case_review={
            'cited_case_urls': ['https://example.invalid/case-fixture'],
            'relevance_and_support': 'Fixture case supports the fixture proposition.',
            'procedural_status_reviewed': True, 'temporal_treatment_reviewed': True,
        })
        self.assertEqual(assess(row)['outcome'], 'complete-within-assessed-scope')
        for field in ('procedural_status_reviewed', 'temporal_treatment_reviewed', 'relevance_and_support'):
            changed = copy.deepcopy(row)
            changed['case_review'].pop(field)
            with self.assertRaises(ValueError):
                assess(changed)

    def test_known_case_cannot_be_waived(self):
        row = reviewed()
        row['case_citation'] = 'not-required'
        with self.assertRaises(ValueError):
            assess(row)

    def test_no_case_found_requires_documented_search(self):
        row = reviewed()
        row.update(case_search='none-found-in-documented-search', case_citation='not-required')
        with self.assertRaises(ValueError):
            assess(row)
        row['case_search_record'] = {
            'queries': ['synthetic search'], 'sources_checked': ['https://example.invalid/register'],
            'as_of': '2026-09-08', 'scope': 'Synthetic, bounded repository search.',
        }
        self.assertEqual(assess(row)['outcome'], 'complete-within-assessed-scope')

    def test_correct_finding_requires_evaluator_verification_not_answer_citations(self):
        row = reviewed()
        row.pop('official_verification')
        with self.assertRaises(ValueError):
            assess(row)

    def test_inconsistent_unanswered_status_fails(self):
        row = reviewed()
        row['completeness'] = 'not-answered'
        with self.assertRaises(ValueError):
            assess(row)


if __name__ == '__main__':
    unittest.main()
