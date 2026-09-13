"""Fetch a bounded, provenance-pinned attachment cohort without crawling further."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from collect_source_originals import Fetcher, now, read_jsonl


def collect(enumeration, evidence_root, output_root, resume_local_network_failure=False):
    evidence_root, output_root = evidence_root.resolve(), output_root.resolve()
    if (evidence_root == output_root or output_root.is_relative_to(evidence_root)
            or evidence_root.is_relative_to(output_root)):
        raise ValueError('Evidence and output roots must be disjoint')
    candidates = read_jsonl(enumeration)
    if len(candidates) > 30:
        raise ValueError('This attachment batch is bounded at 30 URLs')
    for row in candidates:
        if urlparse(row['canonical_url']).hostname not in {'www.aer.gov.au', 'www.aemc.gov.au'}:
            raise ValueError('Attachment outside the explicit AER/AEMC cohort')
        if not row.get('source_index_evidence'):
            raise ValueError('Missing link provenance')
        for evidence in row['source_index_evidence']:
            path = (evidence_root / evidence['snapshot_path']).resolve()
            if (not path.is_relative_to((evidence_root / 'source-originals/objects').resolve())
                    or hashlib.sha256(path.read_bytes()).hexdigest() != evidence['sha256']):
                raise ValueError('Missing or changed link evidence')
    log = output_root / 'source-originals/recovery-attachments.jsonl'
    previous = read_jsonl(log)
    latest = {r['canonical_url']: r for r in previous}
    retry_reasons = {'robots-check-failed:URLError',
                     'host-paused-after-access-stop:robots-check-failed:URLError'}
    retriable = {u for u, r in latest.items() if resume_local_network_failure and r.get('reason') in retry_reasons}
    attempted = latest.keys() - retriable
    stopped = {urlparse(r['canonical_url']).hostname: r.get('reason', '') for r in latest.values()
               if r['canonical_url'] not in retriable
               if r.get('reason', '').startswith(('robots-', 'http-401', 'http-403', 'http-429', 'host-paused'))}
    fetcher = Fetcher({'aer.gov.au', 'aemc.gov.au'}, timeout=20, max_bytes=40_000_000, delay=1)
    log.parent.mkdir(parents=True, exist_ok=True)
    outcomes = []
    for row in candidates:
        if row['canonical_url'] in attempted:
            continue
        host = urlparse(row['canonical_url']).hostname
        if host in stopped:
            result = {**row, 'capture_status': 'deferred', 'attempted_at': now(),
                      'reason': 'host-paused-after-access-stop:' + stopped[host],
                      'legal_review_status': 'not-reviewed', 'current_law_release': False}
        else:
            result = fetcher.fetch(row, output_root)
            if row['canonical_url'] in retriable:
                result['recovery_reason'] = 'Retry after independently confirmed local socket permission failure; robots and site access checks still enforced'
            if result.get('reason', '').startswith(('robots-', 'http-401', 'http-403', 'http-429')):
                stopped[host] = result['reason']
        with log.open('a', encoding='utf-8', newline='\n') as handle:
            handle.write(json.dumps(result, ensure_ascii=True) + '\n')
        summary = {k: result.get(k) for k in ('canonical_url', 'capture_status', 'extraction_status', 'text_character_count', 'reason')}
        outcomes.append(summary)
        print(json.dumps(summary), flush=True)
    return outcomes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enumeration', type=Path, required=True)
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--resume-local-network-failure', action='store_true',
                        help='Only after independently confirming a local socket-permission failure, never a site access denial')
    args = parser.parse_args()
    collect(args.enumeration, args.evidence_root, args.output_root, args.resume_local_network_failure)
