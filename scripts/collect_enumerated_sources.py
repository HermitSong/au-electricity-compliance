"""Acquire enumerated public originals using the existing permission-aware fetcher."""
import argparse
from collections import Counter, deque
import json
from pathlib import Path
import time

from collect_source_originals import Fetcher, discover, host_key, now, read_jsonl, select_manifest_rows
from enumerate_source_indexes import path_identity
from source_permissions import PermissionPolicy, private_path


def access_stop_reason(rows):
    for row in reversed(rows):
        reason = row.get('reason') or ''
        if reason.startswith(('robots-', 'http-401', 'http-403', 'http-429')):
            return reason
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--archive-root', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--permissions', type=Path, required=True)
    parser.add_argument('--max-requests', type=int, default=1000)
    parser.add_argument('--max-seconds', type=int, default=900)
    args = parser.parse_args()
    root, archive = args.root.resolve(), args.archive_root.resolve()
    output = private_path(args.output_root, root)
    permissions = PermissionPolicy.load(args.permissions)
    candidates = read_jsonl(root / 'data/source-index-enumeration.jsonl')
    prior, preserved = select_manifest_rows(read_jsonl(archive / 'source-originals/manifest.jsonl'))
    denied_paths = {path_identity(url) for url, row in prior.items()
                    if row.get('reason') in {'http-401', 'http-403', 'robots-disallowed'}}
    log = private_path(output / 'source-originals/manifest.jsonl')
    summary_path = private_path(output / 'batch-summary.json')
    log.parent.mkdir(parents=True, exist_ok=True)
    previous = read_jsonl(log)
    previous_stop = access_stop_reason(previous)
    if previous_stop:
        print(json.dumps({'new_attempt_count': 0, 'access_review_required': previous_stop,
                          'message': 'Prior batch access stop remains active; no automatic retries or alternative URL paths.'}))
        return
    done = {row['canonical_url'] for row in previous}
    entries = {row['canonical_url']: row for row in candidates}
    for row in previous:
        for child in discover(row, {'aemo.com.au'}, 2):
            entries.setdefault(child['canonical_url'], child)
    queue = deque(row for url, row in entries.items() if url not in done and url not in preserved and path_identity(url) not in denied_paths)
    fetcher = Fetcher({'aemo.com.au'}, 20, 40 * 1024 * 1024, 1.0, permissions)
    deadline = time.monotonic() + args.max_seconds
    count = 0
    with log.open('a', encoding='utf-8', newline='\n') as handle:
        while queue and count < args.max_requests and time.monotonic() < deadline:
            item = queue.popleft()
            row = fetcher.fetch(item, output)
            row['batch_id'] = 'source-index-expansion-2026-09-06'
            handle.write(json.dumps(row, ensure_ascii=True) + '\n')
            handle.flush()
            count += 1
            for child in discover(row, {'aemo.com.au'}, 2):
                url = child['canonical_url']
                if url not in entries:
                    entries[url] = child
                    if url not in preserved and path_identity(url) not in denied_paths:
                        queue.append(child)
            print(json.dumps({'completed': count, 'status': row['capture_status'], 'reason': row.get('reason'), 'url': row['canonical_url']}), flush=True)
            if access_stop_reason([row]):
                print('Stopped this single-host batch for access review; no URL variants will bypass the denial.', flush=True)
                break
    rows = read_jsonl(log)
    report = {'generated_at': now(), 'new_attempt_count': count, 'total_batch_url_count': len(rows),
              'capture_status_counts': dict(Counter(row['capture_status'] for row in rows)),
              'text_url_count': sum(bool(row.get('text_path')) for row in rows),
              'remaining_queue_count': len(queue), 'legal_review_status': 'not-reviewed'}
    summary_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
