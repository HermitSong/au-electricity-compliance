"""Expose historical grade dimensions without inventing a new accuracy score."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    values = [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    result = {row['id']: row for row in values}
    if len(result) != len(values):
        raise ValueError('Duplicate IDs: ' + str(path))
    return result


def build(root, archive):
    expected = {f'CASE100-{n:03d}' for n in range(1, 101)}
    inputs = {name: archive / 'results' / filename for name, filename in {
        'keyed': 'active-keyed.jsonl', 'answers': 'active-answers.jsonl',
        'grades': 'active-grades.jsonl', 'scored': 'scored-items.jsonl',
    }.items()}
    banks = {name: rows(path) for name, path in inputs.items()}
    if any(set(bank) != expected for bank in banks.values()):
        raise ValueError('Each input must contain exactly the frozen 100 IDs')
    manifest_path = archive / 'revision-manifest.json'
    replacements = {row['id']: row for row in json.loads(manifest_path.read_text())['replacements']}
    inputs['revisions'] = manifest_path
    checked_sources, output = {}, []
    for qid in sorted(expected):
        gold, answer, grade, scored = [banks[name][qid] for name in ('keyed', 'answers', 'grades', 'scored')]
        target_urls = {source['url'] for source in gold['sources']}
        if not target_urls or not grade['gold_valid']:
            raise ValueError('A real case and valid reference review are required: ' + qid)
        for source in gold['sources']:
            for key, digest_key in [('snapshot_path', 'sha256'), ('text_path', 'text_sha256')]:
                path = (root / source[key]).resolve()
                if not path.is_relative_to(root):
                    raise ValueError('Source path escapes KB root')
                if path not in checked_sources:
                    checked_sources[path] = sha(path)
                if checked_sources[path] != source[digest_key]:
                    raise ValueError('Reference source changed: ' + qid)
        part = 'abcd'[(int(qid[-3:]) - 1) // 25]
        packet_path = archive / 'blind' / part / 'packets' / (qid + '.json')
        if qid in replacements:
            packet_path = (archive / replacements[qid]['packet_path']).resolve()
            if not packet_path.is_relative_to(archive) or sha(packet_path) != replacements[qid]['packet_sha256']:
                raise ValueError('Replacement packet path/hash mismatch: ' + qid)
        inputs['packet-' + qid] = packet_path
        packet = json.loads(packet_path.read_text())
        if packet['question'] != gold['question']:
            raise ValueError('Packet and question differ: ' + qid)
        urls_by_id = {item['evidence_id']: item.get('official_url') for item in packet.get('evidence', [])}
        urls_by_id.update({item['research_id']: item.get('url') for item in packet.get('research_originals', {}).get('results', [])})
        cited = {eid for claim in answer['claims'] for eid in claim['evidence_ids']}
        matched = sorted(eid for eid in cited if urls_by_id.get(eid) in target_urls)
        verdicts = Counter(item['verdict'] for item in grade['criterion_results'])
        if set(verdicts) - {'met', 'partial', 'not-met', 'unsupported'}:
            raise ValueError('Unknown legacy grade verdict: ' + qid)
        if [item['id'] for item in grade['criterion_results']] != ['C1', 'C2', 'C3', 'C4']:
            raise ValueError('Criterion population differs: ' + qid)
        if scored['supported_points'] != verdicts['met'] or scored['grade_support_errors']:
            raise ValueError('Legacy mechanical grade needs separate adjudication: ' + qid)
        if not cited:
            diagnostic = 'no-structured-citations-recorded'
        elif matched:
            diagnostic = 'designated-case-source-cited'
        else:
            diagnostic = 'other-citations-need-relevance-review'
        output.append({
            'id': qid,
            'historical_complete_and_supported': scored['strict_pass'],
            'official_rule_correctness': 'not-separately-assessed',
            'legacy_criterion_counts': dict(verdicts),
            'legacy_criterion_results': grade['criterion_results'],
            'case_citation_required': True,
            'case_requirement_basis': {'case_name': gold['case_name'], 'verified_source_urls': sorted(target_urls)},
            'case_citation_diagnostic': diagnostic,
            'matched_designated_case_citation_ids': matched,
            'case_citation_compliance': 'not-separately-adjudicated',
            'legacy_critical_errors_found': grade['critical_errors_found'],
            'legacy_unsupported_material_claims': grade['unsupported_material_claims'],
            'meaning': 'A legacy non-pass is not an incorrectness finding. No new rule-truth or case-citation review is inferred.',
        })
    criteria = Counter()
    for item in output:
        criteria.update(item['legacy_criterion_counts'])
    summary = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'mode': 'historical-record-reclassification-not-new-model-test',
        'questions': len(output), 'criterion_counts': dict(criteria),
        'historical_complete_and_supported_questions': sum(item['historical_complete_and_supported'] for item in output),
        'not_established_as_complete_under_old_rubric': sum(not item['historical_complete_and_supported'] for item in output),
        'official_rule_correctness_rate': None,
        'official_rule_correctness_not_separately_assessed': len(output),
        'known_relevant_case_questions': len(output),
        'citation_diagnostics': dict(Counter(item['case_citation_diagnostic'] for item in output)),
        'legacy_recorded_critical_error_questions': sum(bool(item['legacy_critical_errors_found']) for item in output),
        'legacy_recorded_unsupported_material_claim_questions': sum(bool(item['legacy_unsupported_material_claims']) for item in output),
        'source_objects_hash_verified': len(checked_sources),
        'input_hashes': {str(path.relative_to(archive)): sha(path) for path in inputs.values()},
        'limits': [
            'No answer, original key, grade, packet or original score was changed.',
            'No separate current-rule correctness review or new blind model run occurred.',
            'Citation presence is not a complete citation-quality finding.',
            'No recorded critical error does not establish 100 percent correctness.',
            'These historical questions do not directly measure all operational compliance decisions.',
        ],
    }
    return output, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, archive = args.root.resolve(), args.archive.resolve()
    if args.output.resolve().is_relative_to(archive):
        raise ValueError('Write reclassification outside the frozen examination archive')
    output, summary = build(root, archive)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / 'reclassified-items.jsonl').open('x', encoding='utf-8') as handle:
        for item in output:
            handle.write(json.dumps(item, ensure_ascii=True) + '\n')
    with (args.output / 'summary.json').open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(summary, indent=2, ensure_ascii=True) + '\n')
    counts = summary['criterion_counts']
    text = f'''# Scoring Clarification: Historical 100-Question Examination

Date: 8 September 2026. This is a reclassification, not a new model test.

## Correct Interpretation

The preserved result of **{summary['historical_complete_and_supported_questions']}/100** measures complete-and-supported historical-question attainment. It is not an answer accuracy rate. The other **{summary['not_established_as_complete_under_old_rubric']}** questions were not established as complete under the original combined rubric; they are not automatically incorrect.

The original criterion verdicts are **{counts.get('met', 0)} met**, **{counts.get('partial', 0)} partial**, **{counts.get('not-met', 0)} not met** and **{counts.get('unsupported', 0)} unsupported**. A zero binary point can mean omitted information or an incomplete answer, not a false statement.

The original review records contain {summary['legacy_recorded_critical_error_questions']} questions with detected critical errors and {summary['legacy_recorded_unsupported_material_claim_questions']} with flagged unsupported material claims. These are recorded findings, not proof that every answer is correct.

**A new official-rule correctness percentage is not available.** All 100 questions retain `not-separately-assessed` for that dimension. The original exercise tested historical case facts and bounded audit reasoning. Correct present-rule advice cannot supply historical facts specifically requested by a question, and an old-case answer cannot by itself establish today's applicable rules.

## Owner's Scoring Policy

1. Correctness is judged against applicable official rules and authoritative source facts. An omitted answer citation is not an error in the conclusion by itself. Evaluators may verify the answer using separately recorded official-source review outside the original packet.
2. Completeness is separate. Partial answers and abstentions do not become incorrect statements, but do not count as completed answers either.
3. Materially relevant real cases must be cited when known. Missing or defective case citations are reported separately from conclusion correctness. A documented scoped search with no relevant result does not require inventing a precedent.

All 100 questions in this particular examination have identified real-case sources, so the case-citation requirement applies to all 100. Citation-presence diagnostics: `{json.dumps(summary['citation_diagnostics'], sort_keys=True)}`. Presence is not a fresh assessment of relevance, temporal treatment or full citation compliance.

## Integrity and Next Assessment

Reclassification checked the hashes of {summary['source_objects_hash_verified']} preserved original/text objects and retained per-input hashes. Original answers, keys, grades, packets and reports remain unchanged. No production retrieval, legal-release rule or operational permission was weakened.

Future operational examinations should ask for the decision, applicable obligations, material qualifications and actions; case details belong in the supporting evidence. Avoid allowing incidental historical detail to dominate a decision-support accuracy score unless that detail is the task.

A new substantive accuracy score requires separate official-source review of every material conclusion, including uncited conclusions, with correct/incorrect/unverified/unanswered populations disclosed. It must not be derived by simply removing citation penalties or awarding abstentions a pass.

- [Answer Quality Rubric](../../architecture/ANSWER-QUALITY-RUBRIC.md)
- [Original Frozen Report](../source-recovery/case-exam-100-2026-09-07/delivery/REPORT.md)
- [Original Answers and Criterion Reviews](../source-recovery/case-exam-100-2026-09-07/delivery/ITEM-RESULTS.md)
- [Per-Question Reclassification](../source-recovery/case-exam-scoring-2026-09-08/reclassified-items.jsonl)
'''
    with (args.output / 'REPORT.md').open('x', encoding='utf-8') as handle:
        handle.write(text)
    print(json.dumps({key: value for key, value in summary.items() if key != 'input_hashes'}, indent=2))


if __name__ == '__main__':
    main()
