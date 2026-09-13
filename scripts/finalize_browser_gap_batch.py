"""Validate a browser cohort and enumerate its observed supporting attachments."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from collect_source_originals import discover, now, normalise_url, read_jsonl
from validate_source_originals import check_artifacts


def redirect_relation(row):
    if normalise_url(row['canonical_url']) == normalise_url(row['response_url']):
        return None
    return {'kind': 'observed-browser-redirect', 'requested_url': row['canonical_url'],
            'destination_url': row['response_url'], 'equivalence_status': 'not-established',
            'current_law_identity_verified': False}


def finalize(root, archive_root, report_root):
    root, archive_root, report_root = root.resolve(), archive_root.resolve(), report_root.resolve()
    if (root == archive_root or root.is_relative_to(archive_root)
            or report_root == archive_root or report_root.is_relative_to(archive_root)):
        raise ValueError('Output must remain outside the canonical archive')
    cohort = json.loads((root / 'data/source-recovery-targets.json').read_text(encoding='utf-8'))
    expected = {r['canonical_url'] for r in cohort['targets']}
    rows = read_jsonl(root / 'source-originals/recovery-inapp.jsonl')
    inventory = {r['canonical_url'] for r in read_jsonl(archive_root / 'data/source-original-inventory.jsonl')}
    selected = {r['canonical_url']: r for r in rows}
    errors, checked, outcomes, redirects, attachments = [], set(), [], [], {}
    for url, row in selected.items():
        check_artifacts(root, row, checked, errors)
        if url not in expected:
            errors.append('Capture outside the explicit cohort: ' + url)
        if (row.get('current_law_release') is not False or row.get('legal_review_status') != 'not-reviewed'
                or urlparse(row['response_url']).hostname != 'www.aer.gov.au'):
            errors.append('Unexpected source authority or review promotion: ' + url)
        relation = redirect_relation(row)
        if relation:
            redirects.append({**row, 'source_relation': relation})
        outcomes.append({'canonical_url': url, 'response_url': row['response_url'], 'title': row['title'],
                         'characters': row['text_character_count'], 'sha256': row['sha256'],
                         'text_sha256': row['text_sha256'], 'redirect_review_required': bool(relation),
                         'page_scope': 'Rendered main element only; attachments and pagination are separate sources'})
        for child in discover(row, {'aemo.com.au', 'aemc.gov.au'}, 100):
            child['canonical_url'] = normalise_url(child['canonical_url'])
            child['source_family_ids'] = []
            child['document_role'] = 'linked-original-needs-review'
            child['legal_review_status'], child['current_law_release'] = 'not-reviewed', False
            child['source_index_evidence'] = [{'index_url': url, 'snapshot_path': row['snapshot_path'],
                'sha256': row['sha256'], 'retrieved_at': row['retrieved_at'],
                'locator': 'main a[href]', 'link_label': child.get('link_label', '')}]
            item = attachments.setdefault(child['canonical_url'], child)
            if item is not child:
                for key in ('references', 'discovered_from', 'source_index_evidence'):
                    item[key].extend(v for v in child[key] if v not in item[key])
    if errors:
        raise ValueError('; '.join(errors))
    enumeration = root / 'data/browser-attachment-enumeration.jsonl'
    enumeration.write_text(''.join(json.dumps(r, ensure_ascii=True) + '\n' for r in attachments.values()), encoding='utf-8')
    (root / 'source-originals/recovery-z-inapp-redirects.jsonl').write_text(
        ''.join(json.dumps(r, ensure_ascii=True) + '\n' for r in redirects), encoding='utf-8')
    report = {'generated_at': now(), 'target_count': len(expected), 'captured_urls': len(selected),
              'uncaptured_urls': sorted(expected - selected.keys()), 'excluded': cohort['excluded'],
              'distinct_objects_validated': len(checked), 'integrity_errors': errors,
              'redirects_requiring_identity_review': [r['source_relation'] for r in redirects],
              'observed_attachment_urls': len(attachments),
              'new_attachment_urls': sorted(attachments.keys() - inventory),
              'legal_review_status': 'not-reviewed', 'current_law_release': False,
              'boundaries': ['Browser-rendered research text is not court-approved or legally verified evidence.',
                             'A register page capture is not full register enumeration.',
                             'A guideline landing page is not the text of its attached instrument.',
                             'Redirects do not prove document or version equivalence.',
                             'Only observed attachment links are enumerated in this batch.'],
              'outcomes': outcomes}
    report_root.mkdir(parents=True, exist_ok=True)
    (report_root / 'browser-gap-recovery-2026-09-07.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    lines = ['# Browser Gap Recovery - 7 September 2026', '',
             f'- Captured {len(selected)} of {len(expected)} explicitly selected AER URL gaps.',
             f'- Validated {len(checked)} immutable HTML and text objects.',
             f'- Redirects requiring identity review: {len(redirects)}.',
             f'- Observed attachment URLs: {len(attachments)}; new to inventory: {len(attachments.keys() - inventory)}.',
             '- All captures remain unreviewed, research-only and not cleared for redistribution.', '',
             '## Boundaries', '', *['- ' + s for s in report['boundaries']], '', '## Captures', '',
             '| Page | Text characters | Redirect review |', '|---|---:|---|']
    lines.extend(f"| [{r['title'].replace('|', '/')}](<{r['canonical_url']}>) | {r['characters']} | {r['redirect_review_required']} |" for r in outcomes)
    (report_root / 'browser-gap-recovery-2026-09-07.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return {k: v for k, v in report.items() if k != 'outcomes'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--archive-root', type=Path, required=True)
    parser.add_argument('--report-root', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(finalize(args.root, args.archive_root, args.report_root), indent=2))
