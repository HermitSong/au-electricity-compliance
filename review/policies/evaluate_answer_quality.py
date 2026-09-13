"""Validate separately reviewed correctness, completeness and case citation."""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
from urllib.parse import urlsplit


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must be non-empty text')


def require_urls(value, label):
    if not isinstance(value, list) or not value:
        raise ValueError(label + ' must contain source URLs')
    for url in value:
        if not isinstance(url, str) or urlsplit(url).scheme != 'https' or not urlsplit(url).netloc:
            raise ValueError(label + ' contains an invalid HTTPS URL')


def assess(review):
    """Require explicit adjudication; never infer truth from missing citations."""
    correctness = review.get('correctness')
    completeness = review.get('completeness')
    case_search = review.get('case_search')
    citation = review.get('case_citation')
    if correctness not in {'correct', 'incorrect', 'unverified', 'not-answered'}:
        raise ValueError('Unknown correctness status')
    if completeness not in {'complete', 'partial', 'not-answered'}:
        raise ValueError('Unknown completeness status')
    if case_search not in {'known-relevant', 'none-found-in-documented-search', 'not-assessed'}:
        raise ValueError('Unknown case search status')
    if citation not in {'compliant', 'missing', 'defective', 'not-assessed', 'not-required'}:
        raise ValueError('Unknown case citation status')
    require_text(review.get('id'), 'Review ID')
    if (correctness == 'not-answered') != (completeness == 'not-answered'):
        raise ValueError('Not-answered status must be consistent across dimensions')

    if correctness in {'correct', 'incorrect'}:
        record = review.get('official_verification', {})
        require_urls(record.get('source_urls'), 'Evaluator source URLs')
        for field in ('jurisdiction', 'reason', 'assessed_scope'):
            require_text(record.get(field), 'Official verification ' + field)
        date.fromisoformat(record.get('as_of', ''))
        if record.get('reviewed_against_official_sources') is not True:
            raise ValueError('A correctness finding needs an explicit official-source review')
        if correctness == 'incorrect':
            require_text(record.get('contradicted_answer_claim'), 'Contradicted answer claim')
            require_text(record.get('official_conflict'), 'Official conflict')

    if case_search == 'known-relevant':
        if citation == 'not-required':
            raise ValueError('A known relevant case cannot waive the citation requirement')
        if citation == 'compliant':
            record = review.get('case_review', {})
            require_urls(record.get('cited_case_urls'), 'Cited case URLs')
            require_text(record.get('relevance_and_support'), 'Case relevance and support')
            if record.get('procedural_status_reviewed') is not True or record.get('temporal_treatment_reviewed') is not True:
                raise ValueError('Case citation needs procedural and temporal review')
    elif case_search == 'none-found-in-documented-search':
        if citation != 'not-required':
            raise ValueError('No identified case uses a scoped not-required citation status')
        record = review.get('case_search_record', {})
        require_urls(record.get('sources_checked'), 'Searched official repositories')
        if not isinstance(record.get('queries'), list) or not record['queries']:
            raise ValueError('No-case-found finding requires recorded queries')
        for query in record['queries']:
            require_text(query, 'Search query')
        require_text(record.get('scope'), 'Case search scope')
        date.fromisoformat(record.get('as_of', ''))
    elif citation != 'not-assessed':
        raise ValueError('An unassessed search cannot decide the case requirement')

    if correctness == 'incorrect':
        outcome = 'incorrect'
    elif correctness == 'unverified':
        outcome = 'needs-review'
    elif correctness == 'not-answered':
        outcome = 'unanswered'
    elif completeness == 'partial':
        outcome = 'correct-but-incomplete'
    elif citation in {'missing', 'defective'}:
        outcome = 'correct-with-case-citation-deficiency'
    elif citation == 'not-assessed':
        outcome = 'correct-with-case-review-pending'
    else:
        outcome = 'complete-within-assessed-scope'
    return {
        'id': review['id'], 'correctness': correctness, 'completeness': completeness,
        'case_search': case_search, 'case_citation': citation, 'outcome': outcome,
        'may_execute': False, 'current_law_release': False,
        'limit': 'Validates reviewer declarations, not source authenticity or legal truth.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reviews', type=Path, help='JSONL with independently adjudicated dimensions')
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.reviews.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    if len({row['id'] for row in rows}) != len(rows):
        raise ValueError('Duplicate review IDs')
    for row in rows:
        print(json.dumps(assess(row), ensure_ascii=True))


if __name__ == '__main__':
    main()
