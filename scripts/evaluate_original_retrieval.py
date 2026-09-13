"""Measure fixed-target research retrieval, never legal-answer correctness."""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
from time import perf_counter

from search_source_originals import search_research_originals, validate_research_results


def evaluation_provenance(archive: Path) -> dict:
    runtime = {name: hashlib.sha256(Path(sys.modules[name].__file__).read_bytes()).hexdigest()
               for name in ('search_source_originals', 'source_manifest', 'kb_search')}
    manifest = archive / 'source-originals/manifest.jsonl'
    with manifest.open('rb') as handle:
        manifest_hash = hashlib.file_digest(handle, 'sha256').hexdigest()
    return {'search_code_sha256': runtime['search_source_originals'],
            'runtime_sha256': runtime, 'archive_manifest_sha256': manifest_hash}


def strict_question_baseline(root: Path, question: str, limit: int) -> list[str]:
    tokens = re.findall(r'[A-Za-z0-9]+', question)
    if not tokens:
        return []
    database = root.resolve() / 'source-originals/search.sqlite3'
    with closing(sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)) as connection:
        return [row[0] for row in connection.execute(
            'SELECT url FROM originals WHERE originals MATCH ? ORDER BY rank LIMIT ?',
            (' AND '.join('"' + token + '"' for token in tokens), limit))]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--archive-root', type=Path)
    parser.add_argument('--questions', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=6)
    args = parser.parse_args()
    if not 1 <= args.limit <= 12:
        parser.error('--limit must be between 1 and 12')
    root = args.root.resolve()
    archive = (args.archive_root or root).resolve()
    questions = args.questions or root / 'review/questions/research-original-retrieval-v1.jsonl'
    bank_bytes = questions.read_bytes()
    rows = [json.loads(line) for line in bank_bytes.decode('utf-8-sig').splitlines() if line.strip()]
    if not rows or len({row['id'] for row in rows}) != len(rows):
        parser.error('Question bank must be nonempty and have unique IDs')
    provenance = evaluation_provenance(archive)
    reports = []
    for row in rows:
        expected = set(row['expected_source_urls'])
        if not expected:
            raise ValueError('Positive retrieval questions require explicit target URLs: ' + row['id'])
        start = perf_counter()
        research = search_research_originals(archive, row['question'], args.limit)
        integrity_errors = validate_research_results(archive, research['results'])
        elapsed = round(perf_counter() - start, 3)
        found = {item['url'] for item in research['results']}
        baseline = set(strict_question_baseline(archive, row['question'], args.limit))
        reports.append({
            'id': row['id'], 'question': row['question'], 'expected_source_urls': sorted(expected),
            'target_hit': bool(expected & found), 'matched_target_urls': sorted(expected & found),
            'baseline_target_hit': bool(expected & baseline),
            'baseline_returned_urls': sorted(baseline), 'research': research,
            'result_integrity_errors': integrity_errors, 'elapsed_seconds': elapsed,
            'expected_source_role': row['expected_source_role'],
            'critical_misstatement_to_avoid': row['critical_misstatement_to_avoid'],
        })
        print(row['id'] + ': target_hit=' + str(bool(expected & found)) + ', status=' + research['status'], flush=True)
    summary = {
        'question_count': len(rows), 'top_k_distinct_sources': args.limit,
        'target_hit_questions': sum(row['target_hit'] for row in reports),
        'strict_full_question_baseline_hits': sum(row['baseline_target_hit'] for row in reports),
        'integrity_error_count': sum(len(row['result_integrity_errors']) for row in reports),
        'search_integrity_error_questions': sum(row['research']['status'] == 'integrity-error' for row in reports),
        'missing_target_question_ids': [row['id'] for row in reports if not row['target_hit']],
    }
    if evaluation_provenance(archive) != provenance:
        raise ValueError('Archive manifest or loaded runtime files changed during evaluation')
    report = {
        'benchmark_type': 'finite-source-retrieval-acceptance-not-legal-answer-evaluation',
        'question_bank_sha256': hashlib.sha256(bank_bytes).hexdigest(),
        **provenance,
        'archive_root': str(archive), 'summary': summary,
        'limitations': [
            'Targets are independently selected local-source retrieval examples, not independently approved legal answers.',
            'Any target in the first k distinct sources counts as a hit. Unlisted sources may still be relevant; precision is not measured.',
            'The strict-AND baseline feeds the full business question to the former keyword-query interface; it is not an optimally reformulated human query.',
            'No claim is made about current law, semantic answer accuracy, professional superiority, operational permission or nationwide completeness.',
            'Record any tuning after observing this bank; a rerun after tuning is not an untouched holdout.',
        ],
        'results': reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    return 1 if summary['integrity_error_count'] or summary['search_integrity_error_questions'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
