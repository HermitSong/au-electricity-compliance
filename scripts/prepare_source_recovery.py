"""Freeze the legacy missing-text cohort before browser/OCR recovery."""
import argparse
import json
from pathlib import Path
from collect_source_originals import read_jsonl, now


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    remote = {r['canonical_url'] for r in read_jsonl(args.root / 'data/source-artifact-ledger.jsonl')
              if r.get('snapshot_status') == 'remote-only-no-snapshot'}
    inventory = read_jsonl(args.root / 'data/source-original-inventory.jsonl')
    latest = {r['canonical_url']: r for r in read_jsonl(args.root / 'source-originals/manifest.jsonl')}
    targets = []
    for item in inventory:
        if item['canonical_url'] not in remote or item['has_research_text']:
            continue
        row = latest[item['canonical_url']]
        targets.append({'canonical_url': item['canonical_url'], 'prior': row,
                        'route': 'pdf-ocr' if row.get('extraction_status') == 'needs-ocr-or-blank-page-review' else 'browser'})
    destination = args.output_root / 'data/source-recovery-targets.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({'created_at': now(), 'target_count': len(targets), 'targets': targets},
                                     indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(json.dumps({'targets': len(targets), 'browser': sum(r['route'] == 'browser' for r in targets),
                      'pdf_ocr': sum(r['route'] == 'pdf-ocr' for r in targets)}))


if __name__ == '__main__':
    main()
