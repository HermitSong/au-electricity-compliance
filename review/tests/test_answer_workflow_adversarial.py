"""Independent contract probes; provider stubs are not model integration.

Known defects intentionally fail rejection assertions until implementation fixes.
Real-KB probes use read-only stage inputs and disposable output directories.
"""
from copy import deepcopy
from contextlib import redirect_stdout
from pathlib import Path
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import answer_workflow as aw


def request(question='Describe scheduled battery registration in the NEM.'):
    return {
        'schema_version': '1.0', 'question': question,
        'context': {'jurisdiction': 'NEM', 'actor': 'battery operator',
                    'activity': 'registration', 'as_of': '2026-09-13'},
        'requirements': [{'requirement_id': 'topic', 'question': 'What requirements apply?',
                          'kind': 'current-law', 'intake_keys': []}],
        'intake': [], 'known_cases': [],
    }


def providers():
    return {
        'schema_version': '1.0', 'trusted_commands': True,
        **{role: {'id': role + '-stub', 'model_identity': role + '-stub',
                  'argv': [sys.executable, str(Path(__file__).resolve()), '--unused', role],
                  'timeout_seconds': 5, 'max_output_bytes': 200000}
           for role in ('answer', 'reviewer')},
    }


def accept(payload):
    """Explicitly fallible reviewer response, not a semantic-quality assertion."""
    draft = payload['draft']
    return {
        'schema_version': '1.1', 'binding': payload['binding'], 'verdict': 'accept',
        'requirements': [{'requirement_id': s['requirement_id'],
                          'verdict': 'satisfied' if s['status'] == 'answered' else 'bounded',
                          'rationale': 'The fixture accepts the declared section status.'}
                         for s in draft['sections']],
        'claims': [{'claim_id': c['claim_id'], 'claim_type': c['claim_type'],
                    'verdict': 'supported', 'rationale': 'The fixture accepts this claim.'}
                   for c in draft['claims']],
        'scope': [{'field': key, 'verdict': 'consistent',
                   'rationale': 'The fixture accepts the declared scope.'}
                  for key in sorted(aw.CONTEXT_FIELDS)],
        'known_cases': [],
        'counter_searches': [{'search_id': s['search_id'], 'verdict': 'addressed',
                             'counter_evidence_ids': [], 'claim_ids': [],
                             'rationale': 'No contrary item is selected in this fixture.'}
                            for s in payload['searches'] if s['kind'] != 'initial'],
        'checker_warnings': [{'warning_id': w['warning_id'], 'verdict': 'addressed',
                             'claim_ids': [w['claim_id']],
                             'rationale': 'The fixture separately accepts this warning disposition.'}
                            for w in payload['checker_warnings']],
        'english': {'verdict': 'english', 'rationale': 'The prose is English.'},
        'search_requests': [],
    }


def unanswered(payload, limitation):
    return {
        'schema_version': '1.0', 'binding': payload['binding'], 'language': 'en',
        'sections': [{'requirement_id': 'topic', 'status': 'unanswered',
                      'claim_ids': [], 'limitation': limitation}],
        'claims': [],
    }


class RealKBBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def limitation_workflow(self, limitation):
        captured = {}

        def provider(config, role, payload, output):
            captured[role] = deepcopy(payload)
            if role == 'answer':
                self.assertEqual(payload['known_cases'], {})
                return unanswered(payload, limitation)
            return accept(payload)

        # Retrieval, both packet gates, draft/review validation and rendering are real.
        with patch.object(aw, 'provider_call', side_effect=provider):
            result = aw.workflow(request(), providers(), ROOT, self.base / 'out', 0)
        return result, captured

    def test_uncited_current_obligation_in_limitation_is_rejected(self):
        obligation = 'The operator must pay a $42 registration fee today.'
        try:
            result, captured = self.limitation_workflow(obligation)
        except ValueError:
            return
        self.assertTrue(all(not g['current_law_eligible']
                            for g in result['packet_gates'].values()))
        self.assertEqual(captured['reviewer']['checks']['errors'], [])
        self.assertEqual(captured['reviewer']['checks']['reports'], [])
        self.assertNotIn(obligation, (self.base / 'out' / 'answer.md').read_text('utf-8'),
                         'Uncited current-law prose escaped every claim and authority gate via limitation')

    def test_honest_unanswered_limitation_remains_available(self):
        limitation = 'The operative requirements have not been established from this evidence.'
        result, captured = self.limitation_workflow(limitation)
        self.assertEqual(result['final_status'], 'reviewed-partial-research-answer')
        self.assertEqual(captured['reviewer']['checks']['errors'], [])
        self.assertIs(result['action_permission'], False)
        self.assertIs(result['current_legal_release'], False)
        self.assertIs(result['professional_certification'], False)
        self.assertIs(result['independence_verified'], False)

    def test_spelled_out_current_fee_cannot_escape_through_limitation(self):
        obligation = 'The current registration fee is forty-two dollars.'
        try:
            result, captured = self.limitation_workflow(obligation)
        except ValueError:
            return
        self.assertTrue(all(not g['current_law_eligible']
                            for g in result['packet_gates'].values()))
        self.assertEqual(captured['reviewer']['checks']['errors'], [])
        self.assertNotIn(obligation, (self.base / 'out' / 'answer.md').read_text('utf-8'),
                         'Material current-law fee escaped the limitation keyword filter')

    def test_registration_exemption_cannot_escape_through_limitation(self):
        assertion = 'The operator is exempt from registration.'
        try:
            result, _ = self.limitation_workflow(assertion)
        except ValueError:
            return
        self.assertTrue(all(not g['current_law_eligible']
                            for g in result['packet_gates'].values()))
        self.assertNotIn(assertion, (self.base / 'out' / 'answer.md').read_text('utf-8'),
                         'Uncited registration exemption escaped the limitation channel')

    def test_relative_payment_deadline_cannot_escape_through_limitation(self):
        assertion = 'The applicable payment deadline is the next business day.'
        try:
            result, _ = self.limitation_workflow(assertion)
        except ValueError:
            return
        self.assertTrue(all(not g['current_law_eligible']
                            for g in result['packet_gates'].values()))
        self.assertNotIn(assertion, (self.base / 'out' / 'answer.md').read_text('utf-8'),
                         'Uncited operative deadline escaped the limitation channel')

    def assert_fixed_public_limitation(self, private_note):
        result, captured = self.limitation_workflow(private_note)
        output = self.base / 'out'
        self.assertEqual(captured['reviewer']['draft']['sections'][0]['limitation'], private_note)
        self.assertEqual(aw.load_json(output / 'draft-00.json')['sections'][0]['limitation'], private_note)
        self.assertEqual(aw.load_json(output / 'result.json'), result)
        self.assertEqual(result['research_answer']['sections'][0]['limitation'], aw.COVERAGE_WORDING['unanswered'])
        self.assertEqual(result['final_status'], 'reviewed-partial-research-answer')
        self.assertNotIn(private_note, json.dumps(result))
        self.assertNotIn(private_note, (output / 'answer.md').read_text('utf-8'))
        for field in ('action_permission', 'current_legal_release', 'professional_certification'):
            self.assertIs(result[field], False)

    def test_exemption_is_not_published_even_if_keyword_detection_fails(self):
        # Fault injection proves release projection is independent of the heuristic.
        with patch.object(aw, 'limitation_has_obligation', return_value=False):
            self.assert_fixed_public_limitation('The operator is exempt from registration.')

    def test_relative_deadline_is_not_published_even_if_keyword_detection_fails(self):
        with patch.object(aw, 'limitation_has_obligation', return_value=False):
            self.assert_fixed_public_limitation('The applicable payment deadline is the next business day.')

    def test_benign_private_note_is_also_replaced_in_json_and_markdown(self):
        self.assert_fixed_public_limitation('Independent audit marker: evidence coverage remains uncertain.')

    def event_packet(self):
        req = request('What happened in the Pelican Point proceedings?')
        req['context'].update(jurisdiction=None, actor=None, activity=None)
        req['requirements'][0]['kind'] = 'research'
        out = self.base / 'event'
        out.mkdir()
        packets, gates, searches = [], {}, []
        aw.retrieve(req, req['question'], 'initial', ROOT, out, packets, gates, searches)
        return req, packets[0], out

    def test_resealed_forged_event_quote_is_rejected_against_canonical_body(self):
        req, packet, out = self.event_packet()
        row = next(r for r in packet['evidence']
                   if r['evidence_id'] == 'event:au-aer-2024-03-27-pelican-point-final-penalty')
        self.assertIn('$900,000', row['text'])
        saved_sha = row['sha256']
        row['text'] = 'The historical Pelican Point penalty total was $42.'
        packet['packet_id'] = aw.packet_digest(packet)
        try:
            gate = aw.packet_gate(packet, ROOT, req['question'], req['context'])
        except ValueError:
            return
        self.assertEqual(row['sha256'], saved_sha)
        aw.write_new(out / 'forged.json', packet)
        binding = {'fixture': 'resealed-canonical-forgery'}
        draft = single_claim(req, packet, binding, row['evidence_id'], row['text'], row['text'])
        checks = aw.deterministic_checks(
            req, [packet], {packet['packet_id']: gate},
            [{'packet_id': packet['packet_id'], 'packet_file': 'forged.json'}],
            draft, binding, ROOT, out, 0)
        self.assertEqual([r['script'] for r in checks['reports']],
                         ['check_answer.py', 'double_check_answer.py'])
        self.assertFalse(checks['passed'],
                         'Forged canonical text passed packet integrity and both actual checker subprocesses')

    def test_unsealed_event_tampering_is_rejected(self):
        req, packet, _ = self.event_packet()
        packet['evidence'][0]['text'] = 'Changed without resealing.'
        with self.assertRaisesRegex(ValueError, 'integrity'):
            aw.packet_gate(packet, ROOT, req['question'], req['context'])

    def test_resealed_official_span_tampering_is_rejected(self):
        req, packet, _ = self.event_packet()
        row = next(r for r in packet['evidence'] if r['evidence_id'].startswith('source-span:'))
        row['text'] = 'Changed official source text.'
        packet['packet_id'] = aw.packet_digest(packet)
        with self.assertRaisesRegex(ValueError, 'integrity'):
            aw.packet_gate(packet, ROOT, req['question'], req['context'])

    def test_every_nonspan_canonical_type_rejects_resealed_forged_body(self):
        from kb_search import compact_result
        req, original, _ = self.event_packet()
        database = ROOT / 'data/search-index.sqlite3'
        connection = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
        self.addCleanup(connection.close)
        connection.row_factory = sqlite3.Row
        kinds = {'enforcement-event', 'technical-event', 'knowledge-chunk',
                 'obligation-control', 'provision-version', 'source-family'}
        for kind in sorted(kinds):
            with self.subTest(doc_type=kind):
                row = dict(connection.execute(
                    'SELECT * FROM documents WHERE doc_type = ? ORDER BY evidence_id LIMIT 1',
                    (kind,)).fetchone())
                if isinstance(row.get('metadata'), str):
                    row['metadata'] = json.loads(row['metadata'])
                evidence = compact_result(row)
                packet = deepcopy(original)
                packet['evidence'] = [r for r in packet['evidence']
                                      if r['evidence_id'] != evidence['evidence_id']] + [evidence]
                packet['research_case_chains'] = aw.selected_research_chains(
                    ROOT, packet['evidence'], req['question'])
                packet['packet_id'] = aw.packet_digest(packet)
                # First prove this canonical projection is intact, before forging it.
                aw.packet_gate(packet, ROOT, req['question'], req['context'])
                evidence['text'] = 'Deliberately fabricated historical evidence for integrity testing.'
                packet['packet_id'] = aw.packet_digest(packet)
                with self.assertRaises(ValueError):
                    aw.packet_gate(packet, ROOT, req['question'], req['context'])

    def test_actual_legacy_checker_warning_is_preserved_in_registry(self):
        req = request('AGL Hydro McKay1 2006 infringement notice')
        req['context'].update(jurisdiction=None, actor=None, activity=None)
        req['requirements'][0]['kind'] = 'research'
        out = self.base / 'actual-warnings'
        out.mkdir()
        packets, gates, searches = [], {}, []
        aw.retrieve(req, req['question'], 'initial', ROOT, out, packets, gates, searches)
        packet = packets[0]
        source = next(r for r in packet['evidence']
                      if r['evidence_id'] == 'event:au-aer-2006-08-31-agl-hydro-mckay1-infringement')
        binding = {'fixture': 'actual-checker-warning'}
        draft = single_claim(req, packet, binding, source['evidence_id'], source['text'],
                             'The historical AGL Hydro McKay1 record describes a paid infringement notice, '
                             'not a court finding.')
        checks = aw.deterministic_checks(req, packets, gates, searches, draft, binding, ROOT, out, 0)
        self.assertTrue(checks['passed'], checks['errors'])
        self.assertEqual([r['script'] for r in checks['reports']],
                         ['check_answer.py', 'double_check_answer.py'])
        self.assertTrue(checks['checker_warnings'])
        self.assertTrue(any('old-rule' in w['message'] for w in checks['checker_warnings']))
        for warning in checks['checker_warnings']:
            raw = next(r['report'] for r in checks['reports'] if r['script'] == warning['script'])
            claim = next(c for c in raw['claim_reports'] if c['claim_id'] == warning['claim_id'])
            self.assertIn(warning['message'], claim['warnings'])
            self.assertIn(warning['claim_id'] + ': ' + warning['message'], raw['warnings'])
            identity = {key: warning[key] for key in ('script', 'packet_id', 'claim_id', 'message')}
            self.assertEqual(warning['warning_id'], 'warning:' + aw.sha(aw.canonical(identity)))


def single_claim(req, packet, binding, evidence_id, quote, claim_text, start=0):
    return {
        'schema_version': '1.0', 'binding': binding, 'language': 'en',
        'sections': [{'requirement_id': 'topic', 'status': 'answered',
                      'claim_ids': ['claim-1'], 'limitation': ''}],
        'claims': [{'claim_id': 'claim-1', 'requirement_ids': ['topic'],
                    'packet_id': packet['packet_id'], 'claim_type': 'historical-fact',
                    'text': claim_text, 'citations': [{'evidence_id': evidence_id, 'quote': quote,
                                                     'span': {'start': start, 'end': start + len(quote)}}]}],
    }


class DraftReviewContractTests(unittest.TestCase):
    def setUp(self):
        self.req = request()
        self.req['requirements'][0]['kind'] = 'research'
        self.binding = {'fixture': 'contract-only'}
        self.packet = {'packet_id': 'packet-initial', 'evidence': [
            {'evidence_id': 'event:fixture', 'text': 'The first historical notice.'}],
            'research_case_chains': {}}
        self.draft = single_claim(self.req, self.packet, self.binding, 'event:fixture',
                                  'The first historical notice.', 'The historical notice was published.')

    def test_whitespace_only_exact_citation_is_rejected(self):
        self.draft['claims'][0]['citations'][0].update(quote=' ', span={'start': 3, 'end': 4})
        try:
            errors = aw.validate_draft(self.draft, self.req, [self.packet], self.binding)
        except ValueError:
            return
        self.assertTrue(errors, 'One space is accepted as the only exact quote for a material claim')

    def test_material_exact_citation_is_accepted(self):
        self.assertEqual(aw.validate_draft(self.draft, self.req, [self.packet], self.binding), [])

    def test_tampered_quote_is_rejected(self):
        self.draft['claims'][0]['citations'][0]['quote'] = 'A different historical notice.'
        with self.assertRaisesRegex(ValueError, 'quote'):
            aw.validate_draft(self.draft, self.req, [self.packet], self.binding)

    def test_missing_requirement_is_rejected(self):
        self.req['requirements'].append({'requirement_id': 'missing', 'question': 'What else?',
                                         'kind': 'research', 'intake_keys': []})
        with self.assertRaisesRegex(ValueError, 'every required subquestion'):
            aw.validate_draft(self.draft, self.req, [self.packet], self.binding)

    def test_stale_draft_binding_is_rejected(self):
        self.draft['binding'] = {'fixture': 'stale'}
        with self.assertRaisesRegex(ValueError, 'Stale draft'):
            aw.validate_draft(self.draft, self.req, [self.packet], self.binding)

    def test_same_model_identity_with_whitespace_padding_is_rejected(self):
        config = providers()
        config['answer']['model_identity'] = 'same-model'
        config['reviewer']['model_identity'] = ' SAME-MODEL '
        with self.assertRaises(ValueError):
            aw.validate_providers(config)

    def test_same_model_identity_with_case_difference_is_rejected(self):
        config = providers()
        config['answer']['model_identity'] = 'same-model'
        config['reviewer']['model_identity'] = 'SAME-MODEL'
        with self.assertRaises(ValueError):
            aw.validate_providers(config)

    def test_explicit_denial_of_operational_permission_is_allowed(self):
        aw.english('This answer does not grant permission to act.')

    def test_positive_operational_permission_remains_rejected(self):
        with self.assertRaises(ValueError):
            aw.english('This answer grants permission to act.')

    def test_every_section_status_has_fixed_public_wording_without_mutating_audit(self):
        for status in ('answered', 'partial', 'unanswered'):
            with self.subTest(status=status):
                draft = deepcopy(self.draft)
                private_note = 'Private audit marker: the operator is exempt from registration.'
                draft['sections'][0].update(status=status, limitation=private_note)
                if status == 'unanswered':
                    draft['sections'][0]['claim_ids'] = []
                    draft['claims'] = []
                original = deepcopy(draft)
                public = aw.release_projection(draft)
                rendered = aw.render_answer(self.req, draft, [self.packet], 'reviewed-partial-research-answer')
                self.assertEqual(public['sections'][0]['limitation'], aw.COVERAGE_WORDING[status])
                self.assertNotIn(private_note, json.dumps(public))
                self.assertNotIn(private_note, rendered)
                self.assertEqual(public['claims'], draft['claims'])
                self.assertEqual(draft, original)


class CheckerWarningReviewTests(unittest.TestCase):
    """Raw report normalization and reviewer-only schema 1.1 boundary probes."""
    def setUp(self):
        self.req = request()
        self.req['requirements'][0]['kind'] = 'research'
        self.binding = {'fixture': 'warning-review'}
        self.packet = {'packet_id': 'packet-warning', 'evidence': [
            {'evidence_id': 'event:fixture', 'text': 'The historical notice.'}],
            'research_case_chains': {}}
        self.draft = single_claim(self.req, self.packet, self.binding, 'event:fixture',
                                  'The historical notice.', 'The historical notice was published.')
        other = deepcopy(self.draft['claims'][0])
        other['claim_id'] = 'claim-2'
        self.draft['claims'].append(other)
        self.draft['sections'][0]['claim_ids'].append('claim-2')
        self.searches = [{'search_id': 'initial', 'kind': 'initial', 'packet_id': self.packet['packet_id']},
                         {'search_id': 'counter', 'kind': 'counter', 'packet_id': self.packet['packet_id']}]
        self.message = '  A comparator needs separate review.  '
        reports = []
        for script in ('check_answer.py', 'double_check_answer.py'):
            reports.append({'script': script, 'packet_id': self.packet['packet_id'], 'report': {
                'passed': True, 'errors': [], 'warning_count': 1,
                'warnings': ['claim-1: ' + self.message],
                'claim_reports': [
                    {'claim_id': 'claim-1', 'passed': True, 'errors': [], 'warnings': [self.message]},
                    {'claim_id': 'claim-2', 'passed': True, 'errors': [], 'warnings': []}]}})
        self.checks = {'passed': True, 'errors': [], 'reports': reports,
                       'checker_warnings': aw.checker_warning_catalog(reports, self.draft)}
        self.review = accept(self.payload())

    def payload(self):
        return {'binding': self.binding, 'draft': self.draft, 'searches': self.searches,
                'checker_warnings': self.checks['checker_warnings']}

    def validate(self):
        return aw.validate_review(self.review, self.req, [self.packet], self.searches,
                                  self.draft, self.checks, self.binding)

    def test_all_separately_addressed_warnings_allow_acceptance(self):
        self.assertEqual(self.validate(), [])
        self.assertEqual(len(self.review['checker_warnings']), 2)
        self.assertEqual(self.draft['schema_version'], '1.0')
        self.assertEqual(self.req['schema_version'], '1.0')
        self.assertEqual(self.review['schema_version'], '1.1')

    def test_ids_bind_script_packet_claim_and_unmodified_message(self):
        registry = self.checks['checker_warnings']
        self.assertEqual(len(registry), 2)
        self.assertEqual({w['script'] for w in registry}, {'check_answer.py', 'double_check_answer.py'})
        for warning in registry:
            identity = {key: warning[key] for key in ('script', 'packet_id', 'claim_id', 'message')}
            self.assertEqual(warning['message'], self.message)
            self.assertEqual(warning['warning_id'], 'warning:' + aw.sha(aw.canonical(identity)))

    def test_missing_warning_field_is_rejected(self):
        del self.review['checker_warnings']
        with self.assertRaises(ValueError):
            self.validate()

    def test_old_reviewer_schema_is_rejected(self):
        self.review['schema_version'] = '1.0'
        with self.assertRaises(ValueError):
            self.validate()

    def test_empty_dispositions_cannot_hide_nonempty_warnings(self):
        self.review['checker_warnings'] = []
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.validate()

    def test_one_omitted_warning_is_rejected(self):
        self.review['checker_warnings'].pop()
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.validate()

    def test_duplicate_warning_disposition_is_rejected(self):
        self.review['checker_warnings'].append(deepcopy(self.review['checker_warnings'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.validate()

    def test_unknown_warning_identity_is_rejected(self):
        self.review['checker_warnings'][0]['warning_id'] = 'warning:' + '0' * 64
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.validate()

    def test_wrong_claim_or_no_claim_cannot_dispose_warning(self):
        for references in ([], ['claim-2']):
            with self.subTest(claim_ids=references):
                self.review['checker_warnings'][0]['claim_ids'] = references
                with self.assertRaisesRegex(ValueError, 'warned claim'):
                    self.validate()

    def test_blank_nonenglish_or_authorizing_rationale_is_rejected(self):
        for rationale in (' ', '\u4e2d\u6587', 'This review grants permission to act.'):
            with self.subTest(rationale=rationale):
                self.review['checker_warnings'][0]['rationale'] = rationale
                with self.assertRaises(ValueError):
                    self.validate()

    def test_missing_warning_cannot_coexist_with_accept(self):
        self.review['checker_warnings'][0]['verdict'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'contradicts'):
            self.validate()

    def test_missing_warning_allows_revision_and_targeted_research(self):
        self.review['checker_warnings'][0]['verdict'] = 'missing'
        self.review['verdict'] = 'revise'
        self.review['search_requests'] = [{
            'requirement_ids': [], 'claim_ids': ['claim-1'], 'known_case_ids': [],
            'query': 'Retrieve the warned comparator and its limits.',
            'reason': 'Its effect on the claim has not been established.'}]
        self.assertTrue(any('checker_warnings:' in f for f in self.validate()))

    def test_tampered_normalized_catalog_is_rejected_against_raw_reports(self):
        self.checks['checker_warnings'][0]['message'] = 'Changed normalized message.'
        with self.assertRaisesRegex(ValueError, 'catalog'):
            self.validate()

    def test_stale_disposition_after_raw_message_change_is_rejected(self):
        report = self.checks['reports'][0]['report']
        report['claim_reports'][0]['warnings'] = ['A different warning.']
        report['warnings'] = ['claim-1: A different warning.']
        self.checks['checker_warnings'] = aw.checker_warning_catalog(self.checks['reports'], self.draft)
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.validate()

    def test_aggregate_only_warning_cannot_be_dropped(self):
        report = self.checks['reports'][0]['report']
        report['claim_reports'][0]['warnings'] = []
        with self.assertRaisesRegex(ValueError, 'aggregate'):
            self.validate()

    def test_per_claim_warning_cannot_disappear_from_aggregate(self):
        report = self.checks['reports'][0]['report']
        report['warnings'] = []
        report['warning_count'] = 0
        with self.assertRaisesRegex(ValueError, 'aggregate'):
            self.validate()

    def test_invalid_warning_counts_are_rejected(self):
        for count in (0, 2, True, '1'):
            with self.subTest(count=count):
                self.checks['reports'][0]['report']['warning_count'] = count
                with self.assertRaisesRegex(ValueError, 'aggregate'):
                    self.validate()

    def test_duplicate_or_missing_checker_reports_are_rejected(self):
        for reports in ([self.checks['reports'][0]], self.checks['reports'] + [self.checks['reports'][0]]):
            with self.subTest(count=len(reports)):
                with self.assertRaises(ValueError):
                    aw.checker_warning_catalog(reports, self.draft)

    def test_identical_four_part_warnings_share_one_id_but_counts_reconcile(self):
        report = self.checks['reports'][0]['report']
        report['claim_reports'][0]['warnings'].append(self.message)
        report['warnings'].append('claim-1: ' + self.message)
        report['warning_count'] = 2
        self.assertEqual(aw.checker_warning_catalog(self.checks['reports'], self.draft),
                         self.checks['checker_warnings'])
        self.assertEqual(self.validate(), [])

    def test_distinct_claims_with_same_message_need_distinct_dispositions(self):
        report = self.checks['reports'][0]['report']
        report['claim_reports'][1]['warnings'] = [self.message]
        report['warnings'].append('claim-2: ' + self.message)
        report['warning_count'] = 2
        self.checks['checker_warnings'] = aw.checker_warning_catalog(self.checks['reports'], self.draft)
        self.assertEqual(len(self.checks['checker_warnings']), 3)
        with self.assertRaisesRegex(ValueError, 'coverage'):
            self.validate()

    def test_empty_warning_list_is_mandatory_even_when_no_warnings_exist(self):
        for wrapper in self.checks['reports']:
            wrapper['report'].update(warnings=[], warning_count=0)
            for claim in wrapper['report']['claim_reports']:
                claim['warnings'] = []
        self.checks['checker_warnings'] = []
        self.review = accept(self.payload())
        self.assertEqual(self.validate(), [])
        del self.review['checker_warnings']
        with self.assertRaises(ValueError):
            self.validate()


class CurrentNERRegressionTests(unittest.TestCase):
    """Independent diagnostic sentences, not blind-bank questions or gold answers."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)
        self.req = request('What are the BDU registration obligations for integrated resource '
                           'providers in the National Electricity Market?')
        self.req['context'].update(jurisdiction='National Electricity Market',
                                   actor='battery or BESS operator',
                                   activity='connection and registration')
        packets, gates, searches = [], {}, []
        aw.retrieve(self.req, self.req['question'], 'initial', ROOT, self.out,
                    packets, gates, searches)
        self.packet = packets[0]
        self.assertTrue(gates[self.packet['packet_id']]['current_law_eligible'], gates)
        self.provision = next(r for r in self.packet['evidence']
                              if r['evidence_id'] == 'provision:NER-BDU-REGISTRATION-V254-2026-09-04')
        self.evidence_ids = [self.provision['evidence_id']] + self.provision[
            'provision_source_binding']['source_span_ids']

    def draft(self, text):
        return {'question': self.req['question'], 'answer_as_of': self.req['context']['as_of'],
                'claims': [{'claim_id': 'registration-rule', 'claim_type': 'current-law',
                            'text': text, 'evidence_ids': self.evidence_ids}]}

    def test_reviewed_provision_not_lost_when_full_ner_pages_fill_general_search(self):
        from check_answer import check_draft
        draft = self.draft('The NER registration provisions cover Integrated Resource Providers, '
                           'integrated resource systems, bidirectional units, and scheduled bidirectional units.')
        shared = check_draft(ROOT, draft, self.packet)
        self.assertTrue(shared['passed'], shared['errors'])
        aw.write_new(self.out / 'current-draft.json', draft)
        result = aw.run_json(
            [sys.executable, '-B', str(ROOT / 'scripts/double_check_answer.py'),
             str(self.out / 'current-draft.json'), '--root', str(ROOT),
             '--packet', str(self.out / 'packet-01.json'), '--as-of', '2026-09-13'],
            None, self.out, allowed=(0, 1))
        self.assertTrue(result['passed'], result['errors'])

    def test_statutory_joint_liability_does_not_require_a_court_finding(self):
        from check_answer import check_draft
        self.assertTrue(any('jointly and severally liable' in r['text']
                            for r in self.packet['evidence'] if r['evidence_id'] in self.evidence_ids))
        draft = self.draft('Under NER clause 2.9.3(d)(5), the intermediary and applicant will be '
                           'jointly and severally liable for the acts, omissions, statements, '
                           'representations and notices of the intermediary in its capacity as a '
                           'Registered Participant, subject to the appointment and revocation '
                           'provisions in clause 2.9.3.')
        result = check_draft(ROOT, draft, self.packet)
        self.assertTrue(result['passed'], result['errors'])

    def test_current_law_label_and_statutory_cites_do_not_license_court_findings(self):
        from check_answer import check_draft
        draft = self.draft('The court found that the applicant breached the Rules and was '
                           'jointly and severally liable.')
        result = check_draft(ROOT, draft, self.packet)
        self.assertFalse(result['passed'])
        self.assertTrue(any('Judicial liability language is unsupported' in e for e in result['errors']),
                        result['errors'])

    def test_stale_independent_checker_hash_is_rejected(self):
        key = 'independent_claim_checker_code'
        self.assertEqual(self.packet['canonical_register_sha256'][key],
                         aw.sha((ROOT / 'scripts/double_check_answer.py').read_bytes()))
        self.packet['canonical_register_sha256'][key] = '0' * 64
        self.packet['packet_id'] = aw.packet_digest(self.packet)
        with self.assertRaisesRegex(ValueError, 'integrity'):
            aw.packet_gate(self.packet, ROOT, self.req['question'], self.req['context'])

    def test_statutory_exception_does_not_cover_past_named_or_judicial_findings(self):
        from check_answer import check_draft
        for text in (
                'The intermediary and applicant were jointly and severally liable.',
                'ExampleCo and OtherCo will be jointly and severally liable.',
                'The court found that the intermediary and applicant are jointly and severally liable.',
                'The intermediary and applicant will be jointly and severally liable. A penalty was imposed.'):
            with self.subTest(text=text):
                result = check_draft(ROOT, self.draft(text), self.packet)
                self.assertFalse(result['passed'])
                self.assertTrue(any('Judicial liability language is unsupported' in e for e in result['errors']),
                                result['errors'])


    def test_pending_engie_allegations_still_cannot_be_reported_as_findings(self):
        from check_answer import check_draft
        draft = {'question': 'Describe the historical ENGIE customer-support proceeding.',
                 'answer_as_of': '2026-09-13', 'claims': [{
                     'claim_id': 'pending-event', 'claim_type': 'historical-fact',
                     'text': 'ENGIE breached its customer-support obligations.',
                     'evidence_ids': ['event:vic-esc-2026-03-20-engie-customer-support-proceedings']}]}
        result = check_draft(ROOT, draft)
        self.assertFalse(result['passed'])
        self.assertTrue(any('Judicial liability language is unsupported' in e for e in result['errors']),
                        result['errors'])


class IndependentCheckerPolicyTests(unittest.TestCase):
    """Isolated search-policy tests: fixture retrieval and shared gate, not integration."""
    @staticmethod
    def row(identity, doc_type='provision-version', temporal='provision-version'):
        return {'evidence_id': identity, 'doc_type': doc_type, 'status': 'current-at-baseline',
                'issue_family': 'fixture-family', 'temporal_classification': temporal}

    def run_policy(self, general, provisions, rejected_reviews=()):
        import double_check_answer as checker
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            database = out / 'fixture.sqlite3'
            sqlite3.connect(database).close()
            draft = {'question': 'Independent policy fixture.', 'answer_as_of': '2026-09-13',
                     'claims': [{'claim_id': 'policy-claim', 'claim_type': 'current-law',
                                 'text': 'The governing provision establishes this fixture requirement.',
                                 'evidence_ids': ['provision:fixture-governing']}]}
            aw.write_new(out / 'draft.json', draft)
            aw.write_new(out / 'packet.json', {})
            calls = []

            def search(*args, **kwargs):
                calls.append(kwargs)
                result = provisions if kwargs.get('doc_type') == 'provision-version' else general
                return 'independent fixture query', deepcopy(result), {}

            def reviews(root, identities, as_of):
                return ['Fixture record has no live review.'] if set(identities) & set(rejected_reviews) else []

            shared = {'claim_reports': [{'claim_id': 'policy-claim', 'errors': []}]}
            stream = io.StringIO()
            argv = ['double_check_answer.py', str(out / 'draft.json'), '--root', str(out),
                    '--database', str(database), '--packet', str(out / 'packet.json'),
                    '--as-of', '2026-09-13']
            with patch.object(sys, 'argv', argv), patch.object(checker, 'double_search', side_effect=search), \
                    patch.object(checker, 'check_draft', return_value=shared), \
                    patch.object(checker, 'evidence_rows', return_value=[self.row('provision:fixture-governing')]), \
                    patch.object(checker, 'live_review_errors', side_effect=reviews), redirect_stdout(stream):
                exit_code = checker.main()
            return exit_code, json.loads(stream.getvalue()), calls

    def test_uncited_comparator_is_explicit_warning_not_contradiction_proof(self):
        governing = self.row('provision:fixture-governing')
        comparator = self.row('provision:fixture-comparator')
        code, report, calls = self.run_policy([governing], [governing, comparator])
        self.assertEqual(code, 0)
        self.assertTrue(report['passed'])
        self.assertEqual(report['errors'], [])
        self.assertTrue(any('semantic review' in w and 'provision:fixture-comparator' in w
                            for w in report['warnings']))
        self.assertEqual([c.get('doc_type') for c in calls], [None, 'provision-version'])
        self.assertIn('provision:fixture-comparator', report['claim_reports'][0]['provision_search_evidence_ids'])

    def test_unaddressed_appellate_control_remains_blocking(self):
        governing = self.row('provision:fixture-governing')
        appellate = self.row('event:fixture-appeal', 'enforcement-event', 'appellate-control')
        code, report, _ = self.run_policy([governing, appellate], [governing])
        self.assertEqual(code, 1)
        self.assertFalse(report['passed'])
        self.assertTrue(any('unaddressed appellate' in e for e in report['errors']))

    def test_only_uncited_approved_comparator_cannot_satisfy_cited_provision_recovery(self):
        comparator = self.row('provision:fixture-comparator')
        code, report, _ = self.run_policy([], [comparator])
        self.assertEqual(code, 1)
        self.assertFalse(report['passed'])
        self.assertTrue(any('did not recover a cited provision' in e for e in report['errors']),
                        report['errors'])
        self.assertTrue(any('semantic review' in w for w in report['warnings']))

    def test_no_independently_recovered_current_provision_remains_blocking(self):
        source = self.row('source-span:fixture', 'official-source-span', 'official-source-snapshot')
        code, report, _ = self.run_policy([source], [])
        self.assertEqual(code, 1)
        self.assertFalse(report['passed'])
        self.assertTrue(any('did not recover a provision' in e for e in report['errors']))

    def test_postbaseline_unreviewed_record_does_not_count_as_current_recovery(self):
        old = self.row('provision:fixture-old')
        code, report, _ = self.run_policy([old], [old], rejected_reviews={'fixture-old'})
        self.assertEqual(code, 1)
        self.assertFalse(report['passed'])
        self.assertTrue(any('did not recover a provision' in e for e in report['errors']))

if __name__ == '__main__':
    unittest.main()
