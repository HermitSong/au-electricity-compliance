"""Load research-only case chronology for case lookup and frozen answer packets."""
import hashlib
import json
import re
from pathlib import Path


def load_research_chains(root: Path) -> tuple[dict, dict]:
    chains, by_event = {}, {}
    for path in sorted((root / 'data/reviewed-case-chains').glob('*.json')):
        raw = path.read_bytes()
        chain = json.loads(raw)
        if chain.get('current_law_release') is not False or chain.get('operational_bindings_approved') is not False:
            raise ValueError('Research case chains cannot grant operational release')
        identity = chain['chain_id']
        if identity in chains:
            raise ValueError('Duplicate research case chain identity')
        chains[identity] = {**chain, 'research_artifact_path': path.relative_to(root).as_posix(),
                            'research_artifact_sha256': hashlib.sha256(raw).hexdigest()}
        for event_id in chain.get('event_ids', [chain['canonical_event_id']]):
            by_event.setdefault(event_id, []).append(identity)
    return chains, by_event


def selected_research_chains(root: Path, evidence: list[dict], question: str = '') -> dict:
    chains, by_event = load_research_chains(root)
    selected = {identity for row in evidence
                for identity in by_event.get(row.get('evidence_id', '').removeprefix('event:'), [])}
    query = ' ' + ' '.join(re.findall(r'[a-z0-9]+', question.lower())) + ' '
    for identity, chain in chains.items():
        if any(' ' + ' '.join(re.findall(r'[a-z0-9]+', alias.lower())) + ' ' in query
               for alias in chain.get('retrieval_aliases', []) if alias.strip()):
            selected.add(identity)
    return {identity: chains[identity] for identity in sorted(selected)}
