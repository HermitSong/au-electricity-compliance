"""Read published WorkSafe record payloads from preserved HTML, without executing scripts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from lxml import html
from collect_source_originals import now, read_jsonl, save_object


def record_payload(data, expected_id):
    if not isinstance(data, list):
        raise ValueError('Expected a Nuxt reference table')

    def resolve(index, ancestors=()):
        if not isinstance(index, int) or index < 0:
            return None
        if index >= len(data) or index in ancestors or len(ancestors) > 40:
            raise ValueError('Invalid or cyclic record reference')
        value = data[index]
        if isinstance(value, dict):
            return {key: resolve(ref, (*ancestors, index)) for key, ref in value.items()}
        if isinstance(value, list):
            return [resolve(ref, (*ancestors, index)) for ref in value]
        return value

    candidates = [index for index, value in enumerate(data) if isinstance(value, dict)
                  and 'field_body' in value and 'drupal_internal__id' in value]
    matches = [resolve(index) for index in candidates if data[data[index]['drupal_internal__id']] == expected_id]
    if len(matches) != 1 or not matches[0].get('field_body', {}).get('value'):
        raise ValueError('No unique, non-empty published record for the requested record id')
    return matches[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    targets = json.loads((root / 'data/source-recovery-targets.json').read_text(encoding='utf-8'))['targets']
    log = root / 'source-originals/recovery-embedded.jsonl'
    done = {r['canonical_url'] for r in read_jsonl(log)}
    with log.open('a', encoding='utf-8', newline='\n') as handle:
        for target in targets:
            match = re.fullmatch(r'https://www\.worksafe\.vic\.gov\.au/record/(\d+)', target['canonical_url'])
            if not match or target['canonical_url'] in done:
                continue
            prior = target['prior']
            try:
                raw = (root / prior['snapshot_path']).read_bytes()
                if hashlib.sha256(raw).hexdigest() != prior['sha256']:
                    raise ValueError('Preserved HTML hash mismatch')
                tree = html.fromstring(raw)
                scripts = tree.xpath('//script[@id="__NUXT_DATA__"]/text()')
                if len(scripts) != 1:
                    raise ValueError('No unique Nuxt source payload')
                record = record_payload(json.loads(scripts[0]), int(match[1]))
                exact_path, exact_hash = save_object(root, (json.dumps(record, ensure_ascii=True, indent=2) + '\n').encode(), '.json')
                body = html.fromstring(record['field_body']['value']).text_content().strip()
                units = [{'locator': 'html:script#__NUXT_DATA__:record.title', 'text': record['title']},
                         {'locator': 'html:script#__NUXT_DATA__:record.field_body.value', 'text': body}]
                for field in ('field_prs_acn', 'field_prs_dateoffence', 'field_prs_dateoutcome', 'field_prs_datepublished', 'prs'):
                    if record.get(field) is not None:
                        units.append({'locator': f'html:script#__NUXT_DATA__:record.{field}',
                                      'text': field + ': ' + json.dumps(record[field], ensure_ascii=True)})
                text_path, text_hash = save_object(root, (json.dumps(units, ensure_ascii=True, indent=2) + '\n').encode(), '.json')
                row = {**prior, 'recovery_status': 'captured', 'extraction_status': 'extracted-unreviewed',
                       'extraction_refreshed_at': now(), 'extraction_method': 'published-nuxt-record-json-reference-resolution',
                       'title': record['title'], 'text_path': text_path, 'text_sha256': text_hash,
                       'text_character_count': sum(len(unit['text']) for unit in units),
                       'embedded_record_path': exact_path, 'embedded_record_sha256': exact_hash,
                       'content_class': 'official-record-embedded-in-original-html', 'record_id_verified': int(match[1]),
                       'source_date_fields_note': 'Field labels and values copied as published; conduct-date and legal-status interpretation still require review.',
                       'legal_review_status': 'not-reviewed', 'current_law_release': False}
                row.pop('reason', None)
            except Exception as exc:
                row = {'canonical_url': target['canonical_url'], 'recovery_status': 'failed', 'reason': f'{type(exc).__name__}: {exc}'}
            handle.write(json.dumps(row, ensure_ascii=True) + '\n')
            handle.flush()
            print(json.dumps({'url': row['canonical_url'], 'status': row['recovery_status'], 'reason': row.get('reason')}), flush=True)


if __name__ == '__main__':
    main()
