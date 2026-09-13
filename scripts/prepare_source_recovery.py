"""Freeze the legacy missing-text cohort before browser/OCR recovery."""
import argparse
import json
from pathlib import Path
from collect_source_originals import read_jsonl, now
from source_permissions import private_path


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
        row = latest.get(item['canonical_url'], {})
        stopped = (not row.get('permission_id') or row.get('reason', '').startswith(
            ('robots-', 'http-401', 'http-403', 'http-429', 'host-paused', 'acquisition-permission')))
        targets.append({'canonical_url': item['canonical_url'], 'prior': row,
                        'route': 'permission-or-access-review' if stopped else
                        'pdf-ocr' if row.get('extraction_status') == 'needs-ocr-or-blank-page-review' else 'manual-browser-review'})
    destination = private_path(private_path(args.output_root) / 'data/source-recovery-targets.json')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({'created_at': now(), 'target_count': len(targets), 'targets': targets},
                                     indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(json.dumps({'targets': len(targets), 'manual_browser_review': sum(r['route'] == 'manual-browser-review' for r in targets),
                      'permission_or_access_review': sum(r['route'] == 'permission-or-access-review' for r in targets),
                      'pdf_ocr': sum(r['route'] == 'pdf-ocr' for r in targets)}))


if __name__ == '__main__':
    main()
