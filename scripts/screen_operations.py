"""Screen authorised private UTF-8 operating records and optionally retrieve KB packets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from operations_screening import (MAX_REPORT_BYTES, build_screening, canonical, load_json, parse_json, read_limited,
                                  research_requests, sha, validate_screening)


def safe_output_dir(path: Path, protected_roots: list[Path]) -> Path:
    resolved = path.resolve()
    if any(resolved == root.resolve() or resolved.is_relative_to(root.resolve()) for root in protected_roots):
        raise ValueError('Private output must be outside the public knowledge base and code tree')
    if path.exists() or path.is_symlink():
        raise ValueError('Output directory must be new; existing records are never overwritten')
    return resolved


def write_new(path: Path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True, allow_nan=False)
        stream.write('\n')


def retrieval_command(request: dict, kb_root: Path, output: Path) -> list[str]:
    # Only fixed category templates and validated enum/date context enter this call.
    return [sys.executable, '-B', str(kb_root / 'scripts/answer_kb.py'), request['question'],
            '--root', str(kb_root), '--jurisdiction', request['jurisdiction'],
            '--actor', request['actor'], '--activity', request['activity'],
            '--as-of', request['as_of'], '--output', str(output)]


def retrieve_packets(requests: list[dict], kb_root: Path, output_dir: Path) -> list[dict]:
    results = []
    for request in requests:
        row = {'category_id': request['category_id'], 'request': request,
               'state': request['state'], 'may_execute': False, 'legal_clearance': False}
        if request['state'] != 'local-research-only':
            results.append(row)
            continue
        path = output_dir / (request['category_id'] + '-packet.json')
        try:
            result = subprocess.run(retrieval_command(request, kb_root, path),
                                    capture_output=True, timeout=180, check=False)
            row['process_exit_code'] = result.returncode
            if result.returncode not in (0, 2) or not path.is_file():
                row['state'] = 'retrieval-failed'
            else:
                # The existing checker validates canonical sources and release semantics.
                from packet_contract import validate_packet
                raw_packet = read_limited(path, MAX_REPORT_BYTES)
                packet = parse_json(raw_packet)
                if not isinstance(packet, dict):
                    raise ValueError('Packet must be a JSON object')
                errors = validate_packet(packet, kb_root, {'question': request['question']})
                expected = {'jurisdiction': request['jurisdiction'], 'actor': request['actor'],
                            'activity': request['activity'], 'as_of': request['as_of']}
                if packet.get('question') != request['question'] or packet.get('routing_inputs') != expected:
                    errors.append('Packet does not match the fixed research request')
                row.update({'state': 'packet-requires-review' if not errors else 'packet-not-admitted',
                            'packet_path': path.name, 'packet_sha256': sha(raw_packet),
                            'packet_id': packet.get('packet_id'), 'packet_release_state': packet.get('release_state'),
                            'packet_release_reasons': packet.get('release_reasons'), 'validation_errors': errors})
        except (subprocess.TimeoutExpired, OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError, ImportError):
            row['state'] = 'retrieval-failed-or-invalid'
        row['use_limit'] = 'Research about a general issue, not adjudication of private facts. Preserve all KB release blockers and independently review relevance.'
        results.append(row)
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transcript', type=Path, required=True)
    parser.add_argument('--context', type=Path, required=True)
    parser.add_argument('--proposals', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--kb-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--retrieve-kb', action='store_true')
    args = parser.parse_args(argv)
    try:
        kb_root = args.kb_root.resolve()
        output = safe_output_dir(args.output_dir, [kb_root, Path(__file__).resolve().parents[1]])
        raw = read_limited(args.transcript)
        context = load_json(args.context)
        proposals = load_json(args.proposals) if args.proposals else None
        report = build_screening(raw, context, proposals)
        if validate_screening(report, raw, context, proposals):
            raise ValueError('Internal replay failed')
        requests = research_requests(report)
        if args.retrieve_kb and not (kb_root / 'scripts/answer_kb.py').is_file():
            raise ValueError('KB root lacks the existing answer workflow')
        output.mkdir(parents=True, exist_ok=False)
        write_new(output / 'screening.json', report)
        write_new(output / 'research-requests.json', requests)
        results = []
        if args.retrieve_kb:
            sys.path.insert(0, str(kb_root / 'scripts'))
            results = retrieve_packets(requests, kb_root, output)
        write_new(output / 'research-results.json', results)
        manifest = {'schema_version': '1.0', 'report_id': report['report_id'],
                    'retrieval_attempted': args.retrieve_kb, 'may_execute': False, 'may_notify': False,
                    'legal_clearance': False, 'confidentiality': 'private-operational-material',
                    'files': {p.name: sha(p.read_bytes()) for p in sorted(output.iterdir()) if p.is_file()}}
        manifest['manifest_sha256'] = sha(canonical(manifest))
        write_new(output / 'manifest.json', manifest)
        print(json.dumps({'state': report['screening_state'], 'candidate_categories': len(report['findings']),
                          'retrieval_attempted': args.retrieve_kb, 'may_execute': False,
                          'notice': 'Private report created. Screening and software integrity are not legal clearance.'}))
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        # Error logs must not echo excerpts, personal identifiers or arbitrary JSON input.
        print('Screening failed: check input schema, size, authorisation and private output location. No clearance issued.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
