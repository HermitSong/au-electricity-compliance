"""Import explicitly identified official browser downloads, never arbitrary Downloads files."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from collect_source_originals import attach_extraction, now, read_jsonl, save_object


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--downloads', type=Path, required=True)
    parser.add_argument('--mapping', type=Path, required=True)
    args = parser.parse_args()
    root, downloads = args.root.resolve(), args.downloads.resolve()
    targets = {r['canonical_url']: r['prior'] for r in json.loads((root / 'data/source-recovery-targets.json').read_bytes())['targets']}
    log = root / 'source-originals/recovery-downloads.jsonl'
    done = {(r['canonical_url'], r.get('sha256')) for r in read_jsonl(log)}
    with log.open('a', encoding='utf-8', newline='\n') as handle:
        for item in json.loads(args.mapping.read_bytes())['downloads']:
            path = (downloads / item['filename']).resolve()
            if not path.is_relative_to(downloads) or path.name != item['filename']:
                raise ValueError('Download path must be an explicitly named direct child')
            data = path.read_bytes()
            if len(data) != item['observed_size_bytes']:
                raise ValueError(f'Download size changed: {path.name}')
            if not data.startswith(b'%PDF-'):
                raise ValueError('This importer accepts original PDF bytes only')
            stored, digest = save_object(root, data, '.pdf')
            url = item['canonical_url']
            if (url, digest) in done:
                continue
            parent = item.get('parent_url', url)
            prior = targets.get(url, targets.get(parent))
            if prior is None:
                raise ValueError('Download must be in the recovery cohort or its documented attachment')
            row = {k: prior[k] for k in ('references', 'source_family_ids', 'discovery_depth', 'discovered_from')}
            row.update({'canonical_url': url, 'capture_status': 'bytes-preserved', 'recovery_status': 'captured',
                        'acquisition_method': 'official-link-inapp-browser-download', 'representation': 'original-pdf-bytes',
                        'response_url': item['download_url'], 'snapshot_path': stored, 'sha256': digest,
                        'size_bytes': len(data), 'content_type': 'application/pdf', 'imported_at': now(),
                        'legal_review_status': 'not-reviewed', 'current_law_release': False,
                        'redistribution_status': 'not-cleared', 'source_time_version': 'not-established',
                        'download_provenance': {'official_link_page': parent, 'link_url': item['download_url'],
                            'observation_date': '2026-09-05', 'file_modified_at': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                            'note': 'Downloaded by the in-app browser from an observed official link. HTTP headers and exact response time were not exposed; file time is not publication time.'}})
            if item.get('source_relation'):
                row['source_relation'] = item['source_relation']
            attach_extraction(row, data, root)
            text = '\n'.join(u['text'] for u in json.loads((root / row['text_path']).read_bytes())) if row.get('text_path') else ''
            if any(term.casefold() not in text.casefold() for term in item['identity_terms']):
                raise ValueError(f'Document identity check failed: {path.name}')
            row['document_identity_check'] = {'required_terms': item['identity_terms'], 'passed': True,
                'limitation': 'Title/period/content identity only; not proof of unchanged historical bytes or legal accuracy.'}
            handle.write(json.dumps(row, ensure_ascii=True) + '\n')
            handle.flush()
            print(json.dumps({'url': url, 'pages': row.get('page_count'), 'characters': row['text_character_count'], 'sha256': digest}), flush=True)


if __name__ == '__main__':
    main()
