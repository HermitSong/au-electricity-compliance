"""Compare exact question bytes and archive state, not legal answer accuracy."""
import argparse
import json
from pathlib import Path
from statistics import median


def compare(before, after):
    for key in ('question_bank_sha256', 'archive_manifest_sha256', 'archive_root'):
        if not before.get(key) or before[key] != after.get(key):
            raise ValueError('Cannot compare unmatched evaluation evidence: ' + key)
    if before['summary']['top_k_distinct_sources'] != after['summary']['top_k_distinct_sources']:
        raise ValueError('Top-k limits differ')
    old = {r['id']: r for r in before['results']}
    new = {r['id']: r for r in after['results']}
    if not old or old.keys() != new.keys():
        raise ValueError('Question IDs differ or are empty')
    for key in old:
        for field in ('question', 'expected_source_urls'):
            if old[key][field] != new[key][field]:
                raise ValueError('Question or target changed: ' + key)
    gains = [key for key in old if not old[key]['target_hit'] and new[key]['target_hit']]
    regressions = [key for key in old if old[key]['target_hit'] and not new[key]['target_hit']]
    return {
        'scope': 'Paired designated-source retrieval check; not legal-answer accuracy or source completeness.',
        'question_bank_sha256': before['question_bank_sha256'],
        'archive_manifest_sha256': before['archive_manifest_sha256'],
        'question_count': len(old), 'top_k_distinct_sources': before['summary']['top_k_distinct_sources'],
        'prior_search_code_sha256': before['search_code_sha256'],
        'new_search_code_sha256': after['search_code_sha256'],
        'before': before['summary'], 'after': after['summary'],
        'gained_question_ids': gains, 'regressed_question_ids': regressions,
        'still_missing_question_ids': [key for key in new if not new[key]['target_hit']],
        'median_seconds_before': round(median(r['elapsed_seconds'] for r in old.values()), 3),
        'median_seconds_after': round(median(r['elapsed_seconds'] for r in new.values()), 3),
        'limitations': ['Any designated target in top-k counts as a hit; precision and complete issue coverage are not measured.',
                        'Both runs share the same archive and verification dependencies; this is not independent legal review.',
                        'Runtime timings are local observations, not controlled performance estimates.'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = compare(json.loads(args.before.read_text(encoding='utf-8')),
                     json.loads(args.after.read_text(encoding='utf-8')))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(report, indent=2, ensure_ascii=True) + '\n')
    print(json.dumps(report, indent=2, ensure_ascii=True))
