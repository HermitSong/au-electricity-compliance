"""Evidence-located operating-record screening, not legal adjudication."""
from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
import re

VERSION = '0.1.0'
MAX_BYTES = 5_000_000
MAX_CHARACTERS = 1_000_000
MAX_CANDIDATE_SPANS = 1000
MAX_REPORT_BYTES = 64_000_000
WINDOW = 1800
OVERLAP = 300
JURISDICTIONS = {'SA', 'NSW', 'QLD', 'ACT', 'TAS', 'VIC', 'WA', 'NT', 'unknown'}
JURISDICTION_NAMES = {'SA': 'South Australia', 'NSW': 'New South Wales', 'QLD': 'Queensland',
                      'ACT': 'Australian Capital Territory', 'TAS': 'Tasmania', 'VIC': 'Victoria',
                      'WA': 'Western Australia', 'NT': 'Northern Territory', 'unknown': 'unknown'}
OAIC = 'https://www.oaic.gov.au/privacy/notifiable-data-breaches/preventing-preparing-for-and-responding-to-data-breaches/data-breach-preparation-and-response/part-4-notifiable-data-breach-ndb-scheme'
NERL = 'https://www.legislation.sa.gov.au/_legislation-documents/lz/c/a/national-energy-retail-law-south-australia-act-2011/current/2011.6.auth.pdf'
ENGIE = 'https://www.esc.vic.gov.au/media-centre/engie-fined-12-million-after-becoming-victorias-most-complained-about-energy-retailer'

# These are discovery questions and review prompts, never encoded legal holdings.
CATEGORIES = {
    'privacy-disclosure': {
        'label': 'Possible personal-information disclosure or security incident',
        'patterns': [r'data breach|data leak|personal information|customer (?:data|information|list)|wrong recipient|unauthori[sz]ed access',
                     '\u5ba2\u6237\u4fe1\u606f|\u5ba2\u6237\u8d44\u6599|\u4e2a\u4eba\u4fe1\u606f|\u6570\u636e\u6cc4\u9732|\u9519\u8bef\u6536\u4ef6\u4eba'],
        'priority': 'prompt-sensitive-data-review', 'activity': 'safety and incident response',
        'question': 'What current duties concern personal information disclosure, suspected eligible data breach assessment and notification for an electricity retailer?',
        'missing': ['Privacy Act and any CDR applicability', 'Exact data fields and affected people, including vulnerability',
                    'Authorised recipients, actual access and security logs', 'Earliest organisational awareness and evidence for it',
                    'Serious-harm assessment and verified effectiveness of remediation'],
        'actions': ['Assign the privacy/security incident owner promptly.', 'Consider containment without destroying audit evidence.',
                    'Assess each applicable reporting regime; do not wait for the next meeting.'],
        'sources': [OAIC], 'case_hints': [],
    },
    'complaints-backlog': {
        'label': 'Customer correspondence, complaints or bill-review backlog',
        'patterns': [r'complaint|bill review|billing dispute|unanswered|unreplied|email backlog|mail backlog',
                     '\u6295\u8bc9|\u8d26\u5355\u5f02\u8bae|\u8d26\u5355\u590d\u6838|\u672a\u56de\u590d|\u6ca1\u6709\u53ca\u65f6\u56de\u590d|\u90ae\u4ef6\u79ef\u538b'],
        'priority': 'prompt-customer-service-review', 'activity': 'billing and payment',
        'question': 'What current complaint handling and bill review duties apply to an electricity retailer, including its published complaints policy time limits and relevant enforcement cases?',
        'missing': ['Customer jurisdiction and class for each item', 'Original correspondence and receipt timestamps',
                    'Whether each item is an enquiry, complaint, bill review or other request',
                    'Company complaints policy and effective version', 'Acknowledgements, substantive replies and any valid agreed extension',
                    'Concurrent hardship, family violence, life support, debt recovery or disconnection'],
        'actions': ['Triage individual items by harm and applicable deadlines, not inbox age alone.',
                    'Assign an owner and obtain actual case records; staffing shortage is not a clearance.'],
        'sources': [NERL],
        'case_hints': [{'entity': 'ENGIE', 'jurisdiction': 'Victoria', 'event_year': 2025,
                        'status': 'infringement-alleged-breaches', 'official_url': ENGIE,
                        'use_limit': 'Complaint/bill-review delay comparator. Verify the notice and applicable historical rules. Not a court judgment or a national response-time rule.'}],
    },
    'hardship-collection': {
        'label': 'Payment difficulty, hardship or debt-collection interaction',
        'patterns': [r'hardship|cannot afford|can.t afford|payment difficult|debt collect|payment plan',
                     '\u4ed8\u4e0d\u8d77|\u652f\u4ed8\u56f0\u96be|\u56f0\u96be\u63f4\u52a9|\u50ac\u6536|\u5206\u671f\u4ed8\u6b3e'],
        'priority': 'prompt-customer-harm-review', 'activity': 'payment difficulty and hardship',
        'question': 'What current hardship, capacity to pay, payment plan and debt recovery protections apply to residential electricity customers and what enforcement cases explain them?',
        'small_business_question': 'What current payment difficulty, payment arrangement and debt recovery duties apply to small business electricity customers, and which residential hardship protections do not apply?',
        'missing': ['Actual customer communication and payment capacity', 'Hardship policy version and assistance already offered',
                    'Payment-plan status, collection activity and applicable exceptions'],
        'actions': ['Escalate a possible assistance/collection conflict to the responsible customer-protection owner.'],
        'sources': [NERL], 'case_hints': [],
    },
    'life-support': {
        'label': 'Life-support or medically dependent customer signal',
        'patterns': [r'life.support|oxygen concentrator|medical dependence', '\u751f\u547d\u652f\u6301|\u5236\u6c27\u673a|\u547c\u5438\u673a'],
        'priority': 'immediate-human-triage-if-live', 'activity': 'life-support protection',
        'question': 'What current life support registration, customer notification and disconnection protections apply to an electricity retailer?',
        'missing': ['Whether this is a live customer rather than a hypothetical or training example',
                    'Registration, medical confirmation and contact records', 'Actual supply or disconnection status'],
        'actions': ['If a live safety threat is present, use the established emergency process immediately.'],
        'sources': [], 'case_hints': [],
    },
    'family-violence': {
        'label': 'Family-violence and protected-contact signal',
        'patterns': [r'family violence|domestic violence|abusive partner|safe contact', '\u5bb6\u5ead\u66b4\u529b|\u5bb6\u66b4|\u5b89\u5168\u8054\u7cfb'],
        'priority': 'immediate-human-triage-if-live', 'activity': 'family violence assistance',
        'question': 'What current family violence, safe contact, account access and debt handling obligations apply to electricity retailers, and what official enforcement cases are relevant?',
        'missing': ['Jurisdiction and applicable commencement dates', 'Protected contact and access instructions',
                    'Actual account access, disclosures and customer safety needs'],
        'actions': ['Route to trained staff using verified safe-contact instructions.'],
        'sources': [], 'case_hints': [],
    },
    'control-follow-up': {
        'label': 'Unresolved action, resourcing or repeat-control signal',
        'patterns': [r'not enough staff|staff shortage|understaff|still unresolved|last meeting|overdue action',
                     '\u4eba\u624b\u4e0d\u8db3|\u4eba\u5458\u6709\u9650|\u4e0a\u6b21\u4f1a\u8bae|\u4ecd\u672a\u5904\u7406'],
        'priority': 'management-control-review', 'activity': 'retail',
        'question': 'What current operational evidence and complaint handling controls are required of an electricity retailer when customer matters remain unresolved?',
        'missing': ['Underlying issue and actual obligations', 'Previous action owner, due date and completion evidence',
                    'Whether delay has caused an independently identifiable customer or reporting failure'],
        'actions': ['Reconcile the prior action register and verify completion; a verbal assurance is not proof.'],
        'sources': [], 'case_hints': [],
    },
    'other': {
        'label': 'Additional externally identified issue outside the seed detector',
        'patterns': [], 'priority': 'unclassified-review', 'activity': None, 'question': None,
        'missing': ['Issue classification, facts and applicable authority require independent review'],
        'actions': ['Review the cited passage and formulate an authorised non-personal research question separately.'],
        'sources': [], 'case_hints': [],
    },
}
QUALIFIERS = {
    'uncertainty-language': r'\b(?:may|might|possibly|suspect|uncertain)\b|\u53ef\u80fd|\u6000\u7591|\u4e0d\u786e\u5b9a',
    'hypothetical-language': r'\b(?:if|suppose|hypothetical|training|example)\b|\u5047\u8bbe|\u5982\u679c|\u6f14\u7ec3',
    'negation-language': r'\b(?:no|not|never|denied|false alarm)\b|\u6ca1\u6709|\u672a\u53d1\u751f|\u5426\u8ba4',
    'remediation-language': r'\b(?:resolved|deleted|contained|recalled|remediated)\b|\u5df2\u89e3\u51b3|\u5df2\u5220\u9664|\u5df2\u64a4\u56de|\u5df2\u6b62\u635f',
}
LIMITS = [
    'Candidate screening only; neither a finding of contravention nor a compliance clearance.',
    'No-match means only that the bounded detector and supplied proposals found no candidate.',
    'Hash and quote checks prove correspondence to supplied text, not the truth or completeness of that text.',
    'No integrated speech recognition, semantic AI reviewer, live business-system checks or ongoing monitoring.',
    'Six lexical seed families in English and Chinese are not a complete Australian compliance taxonomy.',
    'Meeting date, upload date and assessment date do not establish the legal clock-start event.',
    'Company policies, contracts, actual records and operative source versions require separate verification.',
    'Reports contain private source excerpts; keep them out of public repositories and external search prompts.',
]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False).encode('ascii')


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def read_limited(path: Path, limit: int = MAX_BYTES) -> bytes:
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError('Input exceeds size limit; nothing was silently truncated')
    return raw


def parse_json(raw: bytes):
    try:
        return json.loads(raw.decode('utf-8-sig'), object_pairs_hook=_unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite JSON number')))
    except RecursionError as error:
        raise ValueError('JSON nesting exceeds supported depth') from error


def load_json(path: Path, limit: int = MAX_BYTES):
    return parse_json(read_limited(path, limit))


def decode_source(raw: bytes) -> str:
    text = raw.decode('utf-8-sig')
    if not text.strip() or '\x00' in text or len(text) > MAX_CHARACTERS:
        raise ValueError('Expected nonempty UTF-8 text within the character limit')
    return text


def validate_context(context: dict):
    fields = {'schema_version', 'legal_entity_ref', 'jurisdiction', 'actor', 'customer_class',
              'record_date', 'assessment_date', 'source_kind', 'language', 'processing_authorised'}
    if not isinstance(context, dict) or set(context) != fields:
        raise ValueError('Context fields do not match the documented schema')
    choices = {'schema_version': {'1.0'}, 'jurisdiction': JURISDICTIONS,
               'actor': {'retailer', 'unknown'}, 'customer_class': {'residential', 'small-business', 'mixed', 'unknown'},
               'source_kind': {'transcript', 'summary', 'email-log'}, 'language': {'en', 'zh', 'mixed', 'other'}}
    for key, values in choices.items():
        if not isinstance(context[key], str) or context[key] not in values:
            raise ValueError('Invalid context choice: ' + key)
    if context['processing_authorised'] is not True:
        raise ValueError('Authorised private processing must be confirmed before screening')
    if not isinstance(context['legal_entity_ref'], str) or not 1 <= len(context['legal_entity_ref']) <= 200:
        raise ValueError('Provide a private legal entity reference, or unknown')
    for key in ('record_date', 'assessment_date'):
        value = context[key]
        if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
            raise ValueError('Dates must be explicit ISO dates')
        date.fromisoformat(value)
    if context['record_date'] > context['assessment_date']:
        raise ValueError('Record date cannot follow assessment date')


def source_windows(text: str):
    # Every character is scanned; overlap retains local context across boundaries.
    start = 0
    while start < len(text):
        end = min(start + WINDOW, len(text))
        yield start, end
        if end == len(text):
            break
        start = end - OVERLAP


def proposal_spans(proposals, text: str):
    if proposals is None:
        return []
    if not isinstance(proposals, dict) or set(proposals) != {'schema_version', 'source_text_sha256', 'candidates'}:
        raise ValueError('Invalid external proposal envelope')
    if proposals['schema_version'] != '1.0' or proposals['source_text_sha256'] != sha(text.encode('utf-8')):
        raise ValueError('External proposals are not pinned to this exact text')
    rows = proposals['candidates']
    if not isinstance(rows, list) or len(rows) > 1000:
        raise ValueError('External proposal count is invalid')
    result = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'category_id', 'start', 'end', 'quote'}:
            raise ValueError('External proposal fields are invalid; commands and legal conclusions are not accepted')
        start, end = row['start'], row['end']
        if not isinstance(row['category_id'], str) or row['category_id'] not in CATEGORIES:
            raise ValueError('Unrecognised proposal category')
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text) or end - start > 8000:
            raise ValueError('External proposal offsets are invalid')
        if not isinstance(row['quote'], str) or text[start:end] != row['quote'] or not row['quote'].strip():
            raise ValueError('External proposal does not match its exact source quote')
        result.append((row['category_id'], start, end, 'external-proposal-unverified'))
    return result


def build_screening(raw: bytes, context: dict, proposals=None) -> dict:
    validate_context(context)
    text = decode_source(raw)
    text_hash = sha(text.encode('utf-8'))
    candidates = set(proposal_spans(proposals, text))
    windows = list(source_windows(text))
    for start, end in windows:
        for category_id, spec in CATEGORIES.items():
            for pattern in spec['patterns']:
                for match in re.finditer(pattern, text[start:end], re.IGNORECASE):
                    hit_start, hit_end = start + match.start(), start + match.end()
                    # Keep negations, uncertainty and neighbouring lines, not only the trigger.
                    quote_start = max(0, hit_start - 220)
                    quote_end = min(len(text), hit_end + 320)
                    candidates.add((category_id, quote_start, quote_end, 'lexical-seed-unverified'))
                    if len(candidates) > MAX_CANDIDATE_SPANS:
                        raise ValueError('Too many candidate spans; split the record with provenance retained, not silent truncation')
    findings = []
    for category_id in CATEGORIES:
        spans = []
        for _, start, end, origin in sorted(c for c in candidates if c[0] == category_id):
            quote = text[start:end]
            spans.append({'start': start, 'end': end, 'line_start': text.count('\n', 0, start) + 1,
                          'line_end': text.count('\n', 0, end - 1) + 1, 'quote': quote,
                          'source_text_sha256': text_hash, 'origin': origin,
                          'qualifier_signals': [key for key, pattern in QUALIFIERS.items() if re.search(pattern, quote, re.IGNORECASE)]})
        if not spans:
            continue
        spec = CATEGORIES[category_id]
        findings.append({
            'finding_id': 'candidate:' + category_id, 'category_id': category_id, 'title': spec['label'],
            'triage_priority': spec['priority'], 'status': 'candidate-needs-fact-and-law-review',
            'fact_status': 'record-statement-not-independently-verified', 'duty_status': 'not-determined',
            'contravention_status': 'not-determined', 'source_spans': spans,
            'missing_facts': spec['missing'], 'suggested_review_actions': spec['actions'],
            'deadline': {'due_at': None, 'clock_start': None, 'state': 'not-calculated',
                         'reason': 'Verify the actual awareness/receipt event, applicable rule or policy, calendar and exceptions.'},
            'owner': None, 'resolution': {'status': 'not-verified', 'evidence_refs': []},
            'legal_evidence_ids': [], 'source_discovery_hints': spec['sources'],
            'historical_case_discovery_hints': spec['case_hints'],
            'hint_use_limit': 'Discovery only; not verified current authority or a finding about this company.',
        })
    warnings = list(LIMITS)
    if context['source_kind'] == 'summary':
        warnings.append('SUMMARY ONLY: omitted details cannot be recovered. Obtain the authorised transcript and original records.')
    if context['language'] == 'other':
        warnings.append('Language outside the English/Chinese seed vocabulary; semantic review is required.')
    if context['jurisdiction'] == 'unknown' or context['actor'] == 'unknown' or context['customer_class'] == 'unknown':
        warnings.append('Applicability is unresolved; a candidate must not be used for current-law release.')
    report = {'schema_version': '1.0', 'screening_version': VERSION,
              'engine_sha256': sha(Path(__file__).read_bytes()), 'context': context,
              'source_raw_sha256': sha(raw), 'source_text_sha256': text_hash,
              'proposal_sha256': sha(canonical(proposals)),
              'offset_convention': 'Python Unicode code points, zero-based half-open; UTF-8 BOM removed, newlines preserved',
              'screening_state': 'candidates-for-review' if findings else 'no-candidates-not-clearance',
              'may_execute': False, 'may_notify': False, 'legal_clearance': False,
              'findings': findings, 'warnings': warnings,
              'coverage': {'input_characters': len(text), 'scanned_characters': len(text),
                           'windows': len(windows), 'truncated': False,
                           'external_proposal_count': len(proposals['candidates']) if proposals else 0,
                           'seed_categories': [key for key in CATEGORIES if key != 'other'],
                           'full_semantic_review': False, 'all_compliance_issues_assessed': False}}
    report['report_id'] = 'screening:' + sha(canonical(report))
    return report


def validate_screening(report: dict, raw: bytes, context: dict, proposals=None) -> list[str]:
    expected = build_screening(raw, context, proposals)
    return [] if canonical(report) == canonical(expected) else ['Screening differs from exact input-and-engine replay; not valid for handover.']


def research_requests(report: dict) -> list[dict]:
    context = report['context']
    requests = []
    for finding in report['findings']:
        spec = CATEGORIES[finding['category_id']]
        question = (spec.get('small_business_question', spec['question'])
                    if context['customer_class'] == 'small-business' else spec['question'])
        request = {'category_id': finding['category_id'], 'question': question,
                   'jurisdiction': JURISDICTION_NAMES[context['jurisdiction']], 'actor': context['actor'],
                   'activity': spec['activity'], 'as_of': context['assessment_date'], 'customer_class': context['customer_class']}
        request['state'] = ('blocked-unresolved-context' if any(context[key] == 'unknown' for key in ('jurisdiction', 'actor', 'customer_class'))
                            else 'manual-scope-review' if spec['question'] is None or context['customer_class'] == 'mixed' else 'local-research-only')
        requests.append(request)
    return requests
