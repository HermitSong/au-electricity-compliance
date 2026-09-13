"""Enumerate source-backed report links without merging versions or declaring a census complete."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse, urlunparse

from collect_source_originals import ATTACHMENT, normalise_url, read_jsonl


def path_identity(url):
    return urlunparse(urlparse(url)._replace(query='', fragment=''))


def enumerate_links(captures, known_urls):
    by_path = {}
    for url in known_urls:
        by_path.setdefault(path_identity(url), []).append(url)
    entries = {}
    for capture in captures:
        parent = capture['canonical_url']
        for link in capture.get('links', []):
            url = normalise_url(link['url'])
            parsed = urlparse(url)
            if parsed.scheme != 'https' or parsed.hostname != urlparse(parent).hostname:
                continue
            attachment = bool(ATTACHMENT.search(url))
            detail = parsed.path.startswith(urlparse(parent).path.rstrip('/') + '/')
            if not attachment and not detail:
                continue
            label = link.get('label') or link.get('text') or ''
            row = entries.setdefault(url, {'canonical_url': url, 'source_family_ids': [], 'references': [],
                                           'discovered_from': [], 'discovery_depth': 1, 'source_index_evidence': [],
                                           'link_label': label, 'document_role': 'linked-original' if attachment else 'report-detail-page',
                                           'known_exact_url': url in known_urls,
                                           'same_path_other_urls': sorted(set(by_path.get(path_identity(url), [])) - {url}),
                                           'version_identity_status': 'not-equated; query parameters preserved',
                                           'relevance_status': 'official-electricity-report-index-candidate',
                                           'legal_review_status': 'not-reviewed', 'current_law_release': False})
            for key, values in (('source_family_ids', capture['source_family_ids']),
                                ('references', ['source-index:' + parent]), ('discovered_from', [parent])):
                row[key] = sorted(set(row[key]) | set(values))
            evidence = {'index_url': parent, 'snapshot_path': capture['snapshot_path'], 'sha256': capture['sha256'],
                        'retrieved_at': capture['retrieved_at'], 'locator': 'a[href]', 'link_label': label}
            if evidence not in row['source_index_evidence']:
                row['source_index_evidence'].append(evidence)
    return [entries[url] for url in sorted(entries)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--capture-root', type=Path, required=True)
    args = parser.parse_args()
    root, captures_root = args.root.resolve(), args.capture_root.resolve()
    captures = read_jsonl(captures_root / 'source-originals/recovery-inapp.jsonl')
    for row in captures:
        path = (captures_root / row['snapshot_path']).resolve()
        if not path.is_relative_to((captures_root / 'source-originals/objects').resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Index snapshot failed containment or hash validation')
    known = {row['canonical_url'] for row in read_jsonl(root / 'data/source-original-inventory.jsonl')}
    entries = enumerate_links(captures, known)
    output = root / 'data/source-index-enumeration.jsonl'
    output.write_text(''.join(json.dumps(row, ensure_ascii=True) + '\n' for row in entries), encoding='utf-8')
    report = {'scope': 'Two captured AEMO NEM report indexes; not all Australian source families.',
              'index_enumeration_status': 'captured-index-links-enumerated-only', 'full_source_family_enumeration': 'not-established',
              'captured_indexes': [{'url': row['canonical_url'], 'sha256': row['sha256'], 'retrieved_at': row['retrieved_at']} for row in captures],
              'unique_linked_url_count': len(entries), 'already_known_exact_url_count': sum(row['known_exact_url'] for row in entries),
              'same_path_other_url_candidate_count': sum(bool(row['same_path_other_urls']) for row in entries),
              'role_counts': dict(Counter(row['document_role'] for row in entries)),
              'boundaries': ['A report link is not a recovered original or a separate event.',
                             'Technical incidents, directions and compensation reports are not contravention findings.',
                             'Query-string variants remain separate until byte and version identity is reviewed.',
                             'Collapsed DOM lists are captured; visual and attachment completeness are not certified.',
                             'Operating-incident index says older archived reports are available from AEMO Support Hub.']}
    (root / 'review/results/source-index-enumeration-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
