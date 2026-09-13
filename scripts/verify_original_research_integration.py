"""Exercise research handover against real local data without granting legal release."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from packet_contract import canonical_span_errors, input_digests, packet_digest, research_original_errors


SCENARIOS = [
    ('centrepay', 'For a South Australian electricity retailer, how does the AGL Centrepay appeal affect current handling of closed-account payments?',
     'South Australia', 'billing'),
    ('engie', 'For a Victorian electricity retailer, what can the ENGIE complaint-handling cases teach our complaints team about referral delays and unresolved complaints?',
     'Victoria', 'complaints'),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    output = root / 'review/results'
    manifest = root / 'source-originals/manifest.jsonl'
    before = hashlib.sha256(manifest.read_bytes()).hexdigest()
    scenarios = []
    for name, question, jurisdiction, activity in SCENARIOS:
        packet_path = output / f'original-research-{name}-packet-2026-09-06.json'
        brief_path = output / f'original-research-{name}-brief-2026-09-06.json'
        packet_run = subprocess.run([sys.executable, '-B', str(root / 'scripts/answer_kb.py'), question,
                                     '--root', str(root), '--jurisdiction', jurisdiction, '--actor', 'retailer',
                                     '--activity', activity, '--as-of', '2026-09-06', '--output', str(packet_path)],
                                    capture_output=True, text=True, check=False)
        if packet_run.returncode not in (0, 2):
            raise RuntimeError(packet_run.stderr)
        packet = json.loads(packet_path.read_text(encoding='utf-8'))
        brief_run = subprocess.run([sys.executable, '-B', str(root / 'scripts/build_operational_brief.py'),
                                    '--root', str(root), '--packet', str(packet_path), '--output', str(brief_path)],
                                   capture_output=True, text=True, check=False)
        if brief_run.returncode not in (0, 2):
            raise RuntimeError(brief_run.stderr)
        brief = json.loads(brief_path.read_text(encoding='utf-8'))
        checks = {
            'packet_identity_current': packet['packet_id'] == packet_digest(packet),
            'canonical_inputs_current': packet['canonical_register_sha256'] == input_digests(root),
            'applicability_routed': packet['applicability']['route_state'] == 'routed',
            'research_candidates_available': packet['research_originals']['status'] == 'ok'
                                             and 0 < len(packet['research_originals']['results']) <= 6,
            'research_and_spans_valid': not (research_original_errors(packet, root) + canonical_span_errors(packet, root)),
            'live_version_gate_retained': packet['release_state'] == 'needs-live-verification',
            'brief_nonexecuting': brief['may_execute'] is False and brief['operational_release_state'] == 'blocked',
            'research_handover_preserved': brief['research_originals'] == packet['research_originals'],
            'case_chains_preserved': brief['research_case_chains'] == packet['research_case_chains'],
        }
        if name == 'centrepay':
            checks['centrepay_chain_present'] = 'agl-centrepay-rule31' in packet['research_case_chains']
        scenarios.append({'name': name, 'question': question, 'checks': checks,
                          'research_urls': [item['url'] for item in packet['research_originals']['results']],
                          'packet': packet_path.relative_to(root).as_posix(),
                          'brief': brief_path.relative_to(root).as_posix()})
    unchanged = before == hashlib.sha256(manifest.read_bytes()).hexdigest()
    report = {'passed': unchanged and all(all(row['checks'].values()) for row in scenarios),
              'archive_manifest_unchanged': unchanged, 'archive_manifest_sha256': before,
              'scope': 'Real-data integration and release-boundary checks, not legal accuracy or operational approval.',
              'scenarios': scenarios}
    (output / 'original-research-integration-verification.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
