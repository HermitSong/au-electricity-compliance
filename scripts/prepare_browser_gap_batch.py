"""Prepare an explicit, read-only-source cohort for normal browser recovery."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


def prepare(archive_root, output_root):
    archive_root, output_root = archive_root.resolve(), output_root.resolve()
    if (output_root == archive_root or output_root.is_relative_to(archive_root)
            or archive_root.is_relative_to(output_root)):
        raise ValueError('Source and delta roots must be disjoint')
    inventory = [json.loads(line) for line in
                 (archive_root / 'data/source-original-inventory.jsonl').read_text(encoding='utf-8').splitlines()
                 if line.strip()]
    report = json.loads((archive_root / 'review/results/delivery-readiness.json').read_text(encoding='utf-8'))
    missing = {r['canonical_url']: r for r in report['urls'] if not r['has_research_text']}
    targets, excluded = [], []
    for row in inventory:
        url = row['canonical_url']
        if url not in missing or urlparse(url).hostname != 'www.aer.gov.au':
            continue
        status = missing[url]
        if (status.get('extraction_status') != 'needs-browser-rendering-or-content-review'
                and status.get('capture_status') != 'not-attempted'):
            continue
        if url.endswith(')**'):
            excluded.append({'canonical_url': url, 'reason': 'Malformed markdown suffix; not silently aliased'})
            continue
        prior = {k: row.get(k, [] if k != 'discovery_depth' else 0) for k in
                 ('references', 'source_family_ids', 'discovery_depth', 'discovered_from')}
        targets.append({'canonical_url': url, 'prior': {'canonical_url': url, **prior},
                        'prior_gap': status})
    (output_root / 'data').mkdir(parents=True, exist_ok=True)
    (output_root / 'source-originals').mkdir(parents=True, exist_ok=True)
    payload = {'scope': 'Known missing AER public pages, ordinary browser access only',
               'legal_review_status': 'not-reviewed', 'current_law_release': False,
               'targets': targets, 'excluded': excluded}
    destination = output_root / 'data/source-recovery-targets.json'
    if destination.exists():
        raise FileExistsError('Refusing to replace an existing cohort')
    destination.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    return {'target_count': len(targets), 'excluded': excluded,
            'urls': [r['canonical_url'] for r in targets]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-root', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.archive_root, args.output_root), indent=2))
