"""Exercise actual indexed cases and legacy claims without rewriting benchmark history."""
import argparse
import json
from pathlib import Path
import sqlite3

from check_answer import check_draft, resolve_claim_type


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    events = read_jsonl(root / 'data/enforcement-events-full.jsonl')
    event = next(row for row in events if row['event_id'].startswith('vic-2025-12-24-shantey-'))
    evidence_id = 'event:' + event['event_id']
    with sqlite3.connect((root / 'data/search-index.sqlite3').as_uri() + '?mode=ro', uri=True) as connection:
        indexed = connection.execute('SELECT status, temporal_classification FROM documents WHERE evidence_id=?', (evidence_id,)).fetchone()
    draft = {'question': 'What procedural status does the preserved Shantey register entry describe?',
             'claims': [{'claim_id': 'shantey-procedure', 'claim_type': 'procedural-status',
                         'text': 'The register describes a conditional temporary VCAT stay pending final hearing.',
                         'evidence_ids': [evidence_id]}]}
    historical = check_draft(root, draft)
    incorrect = check_draft(root, {**draft, 'claims': [{**draft['claims'][0], 'text': 'The court found Shantey liable.'}]})
    missing = check_draft(root, {'question': 'Can a Victorian retailer disconnect a life-support customer now?',
                               'claims': [{'claim_id': 'missing-packet', 'text': 'The retailer must comply now.', 'evidence_ids': [evidence_id]}]})
    packets = {row['id']: row for row in read_jsonl(root / 'review/results/case-loop-v5-evidence-packets.jsonl')}
    legacy_checks = []
    for answer in read_jsonl(root / 'review/results/case-loop-v5-answers.jsonl'):
        claims = [claim for claim in answer['claims'] if resolve_claim_type(claim) == 'current-law']
        if claims:
            packet = packets[answer['id']]
            checked = check_draft(root, {**answer, 'question': answer.get('question') or packet['question'], 'claims': claims}, packet)
            legacy_checks.append({'id': answer['id'], 'report': checked})
    checks = {
        'canonical_status_preserved_in_index': indexed == ('review-pending-conditional-stay', 'pending-or-non-final'),
        'historical_procedural_query_remains_usable': historical['passed'],
        'unsupported_final_judicial_finding_blocked': not incorrect['passed'],
        'implicit_current_law_without_packet_blocked': not missing['passed'],
        'legacy_current_law_claims_not_promoted': bool(legacy_checks) and all(not row['report']['passed'] for row in legacy_checks),
    }
    report = {'purpose': 'Targeted real-index contract regression checks; not a new benchmark or semantic legal accuracy score.',
              'passed': all(checks.values()), 'checks': checks,
              'historical_procedure_report': historical, 'unsupported_finding_report': incorrect,
              'missing_packet_report': missing, 'legacy_current_claim_rechecks': legacy_checks}
    output = root / 'review/results/delivery-regression-verification.json'
    output.write_text(json.dumps(report, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'checks': checks, 'legacy_question_count': len(legacy_checks), 'output': str(output)}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
