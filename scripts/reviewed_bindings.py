"""Replay maintainer-held clause reviews; model answer output cannot grant approval."""
from datetime import date
import hashlib
import json
from pathlib import Path

CANDIDATES = 'data/clause-binding-candidates.json'
APPROVALS = 'data/clause-binding-approvals.json'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def records(root, relative, key):
    path = root / relative
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError('Canonical clause-review file must be an object')
    rows = value.get(key, [])
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError('Invalid canonical clause-review records')
    return rows


def reviewed_binding(root, provision, chunks):
    """Return a reproducible approved binding, or None; malformed reviews fail closed."""
    try:
        candidates = [row for row in records(root, CANDIDATES, 'candidates') if row.get('provision_id') == provision['provision_id']]
        if len(candidates) != 1:
            return None
        candidate = candidates[0]
        approvals = [row for row in records(root, APPROVALS, 'approvals') if row.get('candidate_sha256') == digest(candidate)]
        if len(approvals) != 1:
            return None
        approval = approvals[0]
        preparer = candidate.get('prepared_by')
        reviewer = approval.get('reviewer_id')
        note = approval.get('review_note')
        if (approval.get('result') != 'approved-for-scoped-drafting'
                or not isinstance(reviewer, str) or not reviewer.strip()
                or not isinstance(preparer, str) or not preparer.strip()
                or reviewer.strip().casefold() == preparer.strip().casefold()
                or not isinstance(note, str) or not note.strip()
                or candidate.get('provision_sha256') != digest(provision)
                or candidate.get('official_url') != provision.get('official_url')
                or not candidate.get('clause_scope') or not candidate.get('applicability_limit')):
            return None
        checked = date.fromisoformat(candidate['verified_as_of'])
        operative = date.fromisoformat(candidate['operative_from'])
        reviewed = date.fromisoformat(approval['reviewed_at'])
        if checked > date.today() or operative > checked or reviewed < checked or reviewed > date.today():
            return None
        ids = candidate['source_span_ids']
        if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
            return None
        by_id = {'source-span:' + row['chunk_id']: row for row in chunks}
        if len(by_id) != len(chunks):
            return None
        selected = [by_id[span_id] for span_id in ids]
        source_hashes = sorted({row['source_sha256'] for row in selected})
        if source_hashes != candidate['source_sha256_values']:
            return None
        for row in selected:
            path = (root / row['snapshot_path']).resolve()
            if (row['canonical_url'] != candidate['official_url'] or not path.is_relative_to(root.resolve())
                    or hashlib.sha256(path.read_bytes()).hexdigest() != row['source_sha256']
                    or hashlib.sha256(row['text'].encode()).hexdigest() != row['text_sha256']
                    or not row.get('text', '').strip() or not row.get('locator')):
                return None
        if candidate['span_record_sha256'] != digest(selected):
            return None
        return {
            'provision_id': provision['provision_id'], 'authority_status': provision['status'],
            'official_url': provision['official_url'], 'clause_scope': candidate['clause_scope'],
            'binding_status': 'reviewed-exact-clause-range',
            'review_status': 'independent-ai-source-review-not-professional-certification',
            'supports_current_law_drafting': True, 'supports_operational_execution': False,
            'professional_legal_review_status': 'material-action-approval-remains-separate',
            'source_span_ids': ids, 'source_locators': [row['locator'] for row in selected],
            'source_sha256_values': source_hashes,
            'review_candidate_sha256': digest(candidate), 'approval_sha256': digest(approval),
            'operative_from': candidate['operative_from'], 'verified_as_of': candidate['verified_as_of'],
            'limitation': candidate['applicability_limit'],
        }
    except (OSError, ValueError, KeyError, TypeError):
        return None


def live_review_errors(root, provision_ids, as_of):
    """Only the exact reviewed date is admitted; no global baseline is advanced."""
    errors = []
    try:
        answer_date = date.fromisoformat(as_of)
        provisions = {row['provision_id']: row for row in records(root, 'data/provision-version-register.json', 'provisions')}
        bindings = {row['provision_id']: row for row in records(root, 'data/provision-source-bindings.json', 'bindings')}
        chunks = [json.loads(line) for line in (root / 'data/source-text-chunks.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
        if not provision_ids:
            return ['A scoped live version check requires controlling provision routes.']
        for provision_id in provision_ids:
            approved = reviewed_binding(root, provisions.get(provision_id, {}), chunks)
            if not approved or approved != bindings.get(provision_id):
                errors.append('Missing or changed independently reviewed binding: ' + provision_id)
            elif answer_date != date.fromisoformat(approved['verified_as_of']):
                errors.append('A new live version check is required for the requested date: ' + provision_id)
        return errors
    except (OSError, ValueError, KeyError, TypeError):
        return ['Scoped live version checks could not be replayed.']
