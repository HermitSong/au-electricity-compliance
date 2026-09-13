"""Report stale or changed scoped clause reviews without granting new approval."""
import argparse
from datetime import date
import json
from pathlib import Path

from reviewed_bindings import CANDIDATES, records, live_review_errors


def audit(root, as_of):
    date.fromisoformat(as_of)
    dependencies = {row['provision_id']: row['knowledge_paths'] for row in
                    records(root, 'data/rule-dependencies.json', 'dependencies')}
    results = []
    for candidate in records(root, CANDIDATES, 'candidates'):
        provision_id = candidate['provision_id']
        errors = live_review_errors(root, [provision_id], as_of)
        results.append({'provision_id': provision_id, 'as_of': as_of,
                        'status': 'requires-review' if errors else 'scoped-review-replayed',
                        'reasons': errors, 'declared_affected_knowledge_paths': dependencies.get(provision_id, [])})
    return {'as_of': as_of, 'reviews': results, 'requires_review_count': sum(bool(row['reasons']) for row in results),
            'may_execute': False,
            'limit': 'Offline change/expiry audit of declared dependencies. This does not fetch new law, enumerate all dependencies, authenticate reviewers or grant a new approval.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--as-of', default=date.today().isoformat())
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = audit(args.root.resolve(), args.as_of)
    rendered = json.dumps(report, indent=2, ensure_ascii=True) + '\n'
    if args.output:
        if args.output.exists():
            parser.error('Output exists; preserve prior review reports')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding='utf-8')
    else:
        print(rendered, end='')
    return 2 if report['requires_review_count'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
