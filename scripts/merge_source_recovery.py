"""Merge preserved acquisitions without confusing replacements with historical originals."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from collect_source_originals import attach_extraction, normalise_url, now, read_jsonl, rebuild_outputs, select_manifest_rows


LOGS = ['recovery-browser.jsonl', 'recovery-ocr.jsonl', 'recovery-ocr-double.jsonl',
        'recovery-embedded.jsonl', 'recovery-inapp.jsonl', 'recovery-downloads.jsonl', 'recovery-attachments.jsonl']
METADATA = ('canonical_url', 'references', 'source_family_ids', 'discovery_depth', 'discovered_from')
FALLBACKS = {'corrected-official-directory', 'current-policy-successor', 'current-agency-successor', 'public-register-counterpart'}


def acceptable(row):
    if row.get('browser_capture_provenance', {}).get('selector') == '.layout-col':
        return False  # These three AEMO sidebar captures were subsequently corrected.
    return bool(row.get('text_path') and row.get('extraction_status') != 'blocked-or-error-page')


def is_fallback(row):
    return row.get('source_relation', {}).get('kind') in FALLBACKS


def fingerprint(row):
    fields = ('canonical_url', 'sha256', 'text_sha256', 'acquisition_method', 'extraction_method',
              'source_relation', 'ocr_comparison_sha256', 'extraction_revision', 'recovery_for_url', 'invalidates_prior_text')
    return hashlib.sha256(json.dumps({k: row.get(k) for k in fields}, sort_keys=True).encode()).hexdigest()


def verified_bytes(root, row):
    path = (root / row['snapshot_path']).resolve()
    if not path.is_relative_to((root / 'source-originals/objects').resolve()):
        raise ValueError('Source object path escapes archive')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != row['sha256']:
        raise ValueError('Source bytes have changed')
    return data


def merge(root, legacy_root):
    archive = root / 'source-originals'
    rows = read_jsonl(archive / 'manifest.jsonl')
    latest, preserved = select_manifest_rows(rows)
    baseline = json.loads((root / 'data/source-original-summary.json').read_text())
    pending, corrections, candidates = [], [], {}
    for prior in latest.values():
        mime = prior.get('content_type', '')
        if 'officedocument' not in mime or prior.get('extraction_revision') == 4 or not prior.get('snapshot_path'):
            continue
        corrected = attach_extraction(dict(prior), verified_bytes(root, prior), root)
        corrected.update(invalidates_prior_text=True, extraction_refreshed_at=now(),
                         extraction_correction='Office packages must not be decoded as UTF-8 text')
        pending.append(corrected)
        corrections.append({'canonical_url': prior['canonical_url'], 'old_text_sha256': prior.get('text_sha256'),
                            'new_text_sha256': corrected.get('text_sha256'), 'status': corrected['extraction_status']})
    for name in LOGS:
        for row in read_jsonl(archive / name):
            row = dict(row)
            if 'officedocument' in row.get('content_type', '') and row.get('snapshot_path'):
                row = attach_extraction(row, verified_bytes(root, row), root)
            if not acceptable(row):
                continue
            row['recovery_log'] = name
            candidates[row['canonical_url']] = row
    for old, row in candidates.items():
        row = dict(row)
        if is_fallback(row):
            row['recovery_for_url'] = old
            row['canonical_url'] = normalise_url(row['response_url'])
            row['references'] = sorted(set(row.get('references', [])) | {f'reference-repair:{old}'})
            # A single register row must not replace the full register in the FTS index.
            existing = preserved.get(row['canonical_url'])
            if row['source_relation']['kind'] == 'public-register-counterpart' and existing:
                continue
        pending.append(row)
    seen = {fingerprint(row) for row in rows}
    appended = 0
    with (archive / 'manifest.jsonl').open('a', encoding='utf-8', newline='\n') as handle:
        for row in pending:
            identity = fingerprint(row)
            if identity in seen:
                continue
            row['recovery_import_id'] = identity
            row['recovery_imported_at'] = now()
            handle.write(json.dumps(row, ensure_ascii=True) + '\n')
            rows.append(row)
            seen.add(identity)
            appended += 1
    entries = {row['canonical_url']: {k: v for k, v in row.items() if not k.startswith('latest_') and k != 'has_research_text'}
               for row in read_jsonl(root / 'data/source-original-inventory.jsonl')}
    for row in rows:
        entries.setdefault(row['canonical_url'], {key: row.get(key, [] if key not in ('canonical_url', 'discovery_depth') else 0) for key in METADATA})
    summary = rebuild_outputs(root, entries, baseline['initial_seed_url_count'], now(), legacy_root)
    _, preserved = select_manifest_rows(rows)
    targets = json.loads((root / 'data/source-recovery-targets.json').read_text())['targets']
    resolution = []
    for target in targets:
        url = target['canonical_url']
        row = candidates.get(url, {})
        status = ('alternative-official-source-only' if is_fallback(row) else
                  'recovered-original-source-text' if url in preserved else 'original-unavailable')
        resolution.append({'canonical_url': url, 'status': status,
                           **{k: row[k] for k in ('response_url', 'source_relation', 'snapshot_path', 'sha256', 'text_path', 'text_sha256', 'recovery_log') if k in row},
                           'legal_review_status': 'not-reviewed', 'current_law_release': False})
    (root / 'data/source-recovery-resolution.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=True) + '\n' for r in resolution), encoding='utf-8')
    correction_path = root / 'review/results/source-office-extraction-corrections.json'
    previous_corrections = json.loads(correction_path.read_text()) if correction_path.exists() else []
    by_url = {r['canonical_url']: r for r in previous_corrections}
    for corrected in corrections:
        previous = by_url.get(corrected['canonical_url'], {})
        by_url[corrected['canonical_url']] = {**corrected, 'old_text_sha256': previous.get('old_text_sha256', corrected['old_text_sha256'])}
    correction_path.write_text(json.dumps(list(by_url.values()), indent=2) + '\n', encoding='utf-8')
    report = {'generated_at': now(), 'canonical_target_count': len(targets), 'resolution_counts': dict(Counter(r['status'] for r in resolution)),
              'legacy_url_count': summary['legacy_remote_url_count'], 'legacy_urls_with_source_text': summary['legacy_remote_urls_with_research_text'],
              'legacy_urls_without_original_text': summary['legacy_remote_urls_still_without_research_text'],
              'fragment_aliases_not_new_documents': summary['legacy_fragment_aliases_with_research_text'],
              'office_sources_corrected': len(json.loads(correction_path.read_text())),
              'independent_ocr_documents': len(read_jsonl(archive / 'recovery-ocr-double.jsonl')),
              'limitations': ['Recovered current representations are not proof of unchanged historical bytes.',
                              'Alternative official sources do not establish missing historical originals.',
                              'OCR differences and publication/commencement dates require legal review.',
                              'This finite legacy cohort is not all Australian electricity compliance material.']}
    (root / 'review/results/source-recovery-summary.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return {**report, 'manifest_rows_appended_this_run': appended}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--legacy-root', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(merge(args.root.resolve(), args.legacy_root.resolve()), indent=2))


if __name__ == '__main__':
    main()
