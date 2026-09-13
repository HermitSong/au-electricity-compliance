"""Check the tracked release boundary; this is a heuristic, not a security audit."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DENIED_PARTS = {'source-originals', 'official-snapshots', 'backups', 'source-recovery',
                'enterprise-private', 'private-operations', 'operations-runs',
                '__pycache__', '.venv', 'node_modules', 'ocr-gap-recovery'}
DENIED_SUFFIXES = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.sqlite3', '.zip', '.pem', '.key', '.log'}
PATTERNS = {
    'private-key': re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
    'github-token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'api-token': re.compile(r'(?<![\w-])sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{35,}\b'),
    'local-user-path': re.compile(r'(?i)[A-Z]:(?:\\+|/)Users(?:\\+|/)(?!Public\b|<|USER\b|example\b)[A-Za-z0-9_.-]+'),
}


def approved_assets(root):
    manifest_path = root / 'evidence/manifest.json'
    if not manifest_path.exists():
        return {}
    manifest = json.loads(manifest_path.read_text('utf-8'))
    if manifest.get('project_licence_applies') is not False or manifest.get('current_law_release') is not False:
        raise ValueError('Source attachment rights and current-law gates must stay separate')
    assets = {}
    for item in manifest['assets']:
        relative = item['path']
        parts = PurePosixPath(relative)
        if (relative != parts.as_posix() or '\\' in relative or '..' in parts.parts
                or len(parts.parts) != 3 or parts.parts[0] != 'evidence'
                or parts.parts[1] not in {'originals', 'renders'}
                or parts.suffix not in {'.pdf', '.png'}):
            raise ValueError('Invalid source attachment path')
        if relative.casefold() in {name.casefold() for name in assets}:
            raise ValueError('Duplicate source attachment')
        path = root / relative
        if any(p.is_symlink() for p in (path, path.parent, path.parent.parent)):
            raise ValueError('Source attachment symlink')
        path.resolve().relative_to(root.resolve())
        for field in ('official_url', 'permission_url', 'licence_basis', 'attribution',
                      'permission_reviewed_on', 'privacy_review', 'temporal_limit', 'transformation'):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError('Missing attachment provenance: ' + field)
        if (item.get('redistribution_status') != 'reviewed-for-this-release'
                or item.get('current_law_release') is not False):
            raise ValueError('Unreviewed or legally promoted attachment')
        raw = path.read_bytes()
        expected_magic = b'%PDF-' if parts.suffix == '.pdf' else b'\x89PNG\r\n\x1a\n'
        if (not raw.startswith(expected_magic) or len(raw) != item['size_bytes']
                or hashlib.sha256(raw).hexdigest() != item['sha256']):
            raise ValueError('Source attachment bytes differ from reviewed manifest')
        assets[relative] = item
    return assets


def main():
    result = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, check=True, capture_output=True)
    paths = [p for p in result.stdout.decode('utf-8').split('\0') if p]
    if not paths:
        raise ValueError('No tracked files to inspect')
    findings = []
    try:
        assets = approved_assets(ROOT)
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({'findings': [{'kind': 'invalid-evidence-manifest', 'detail': str(exc)}]}))
        return 1
    for relative in set(assets) - set(paths):
        findings.append({'file': relative, 'kind': 'manifest-asset-not-tracked'})
    for relative in paths:
        path = ROOT / relative
        if relative in assets:
            continue
        if relative.startswith(('evidence/originals/', 'evidence/renders/')):
            findings.append({'file': relative, 'kind': 'unreviewed-evidence-asset'})
        if (set(path.relative_to(ROOT).parts) & DENIED_PARTS or path.suffix.lower() in DENIED_SUFFIXES
                or path.name == '.env' or path.name.startswith('.env.') and path.name != '.env.example'):
            findings.append({'file': relative, 'kind': 'excluded-file'})
        if path.is_symlink():
            findings.append({'file': relative, 'kind': 'symlink'})
            continue
        raw = path.read_bytes()
        if b'\0' in raw:
            findings.append({'file': relative, 'kind': 'unexpected-binary'})
            continue
        text = raw.decode('utf-8-sig')
        if relative == 'data/source-text-chunks.jsonl' and text.strip():
            findings.append({'file': relative, 'kind': 'nonempty-source-text-placeholder'})
        for kind, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append({'file': relative, 'kind': kind})
    print(json.dumps({'tracked_files': len(paths), 'findings': findings,
                      'scope': 'Tracked working-file paths, text patterns and public source-text boundary only; no universal secret, privacy or rights assurance.'}, indent=2))
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())
