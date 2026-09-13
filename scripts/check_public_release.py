"""Scan a references-only release, not copyright ownership or legal clearance.

By default inspect existing tracked working files; report unstaged deletions.
--staged inspects every stage-zero index blob by object ID, without checkout,
filters, or consulting working-file contents. Neither mode scans history,
untracked files, remote content, or proves that apparently original prose is
original. Path, format and export-shape checks are deliberately heuristic;
renamed unmarked plain-text copies and encoded payloads need human review.
Run against a stable checkout/index; concurrent filesystem changes are outside
this check's assurance. No manifest record grants a file exemption.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'evidence/manifest.json'
SOURCE_TEXT = 'data/source-text-chunks.jsonl'
DENIED_PARTS = {
    '.git', 'source-originals', 'official-snapshots', 'backups', 'source-recovery',
    'enterprise-private', 'private-operations', 'operations-runs', 'private-runs',
    'runs', '--pycache--', '.venv', 'node-modules', 'ocr-gap-recovery',
    'office-recovery', 'offline-recovery', 'staging-full', 'source-archives',
    'originals', 'renders', 'screenshots', 'ocr', 'fulltext', 'full-text',
    'extracted-text', 'source-text',
}
DENIED_SUFFIXES = {
    '.pdf', '.doc', '.docx', '.docm', '.dot', '.dotx', '.dotm', '.rtf',
    '.xls', '.xlsx', '.xlsm', '.xlsb', '.xlt', '.xltx', '.xltm',
    '.ppt', '.pptx', '.pptm', '.pot', '.potx', '.pps', '.ppsx', '.one',
    '.odt', '.ods', '.odp', '.png', '.jpg', '.jpeg', '.gif', '.webp',
    '.bmp', '.tif', '.tiff', '.heic', '.avif', '.svg', '.ico',
    '.zip', '.tar', '.tgz', '.gz', '.bz2', '.xz', '.7z', '.rar', '.zst',
    '.cab', '.iso', '.epub', '.jar', '.war', '.mhtml', '.mht',
    '.sqlite3', '.sqlite', '.db', '.bin', '.exe', '.dll', '.so',
    '.pyc', '.pyo', '.class', '.wasm', '.mp3', '.mp4', '.wav',
    '.pem', '.key', '.log',
}
EXPORT_NAME = re.compile(
    r'(?:^|[-_.])(?:full[-_]?text|source[-_]text|extracted[-_]text|ocr'
    r'|screenshots?|page[-_]renders?|source[-_]originals?'
    r'|source[-_]browser|source[-_]recovery)(?:$|[-_.])', re.I)
CODE_SUFFIXES = {'.py', '.ps1', '.js', '.cjs', '.mjs', '.ts', '.tsx', '.jsx', '.sh'}
FULLTEXT_KEYS = {
    'fulltext', 'full_text', 'source_text', 'extracted_text', 'ocr_text',
    'raw_html', 'html_content', 'page_text', 'document_text',
}
PATTERNS = {
    'private-key': re.compile(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),
    'github-token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'api-token': re.compile(r'(?<![\w-])sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{35,}\b'),
    'local-user-path': re.compile(r'(?i)[A-Z]:(?:\\+|/)Users(?:\\+|/)(?!Public\b|<|USER\b|example\b)[A-Za-z0-9_.-]+'),
}
SCOPE = (
    'Heuristic path, byte-format, export-shape and secret-pattern checks only; '
    'not legal clearance, proof of authorship, or universal privacy/security assurance. '
    'Unmarked plain-text copies and encoded payloads may evade detection. '
    'Excludes untracked files, Git history and remote content. '
    'Working-tree mode ignores absent tracked files and does not approve the index; '
    '--staged checks every indexed blob, not unstaged edits. Use a stable checkout/index.'
)


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Duplicate JSON key: ' + key)
        value[key] = item
    return value


def _invalid_constant(value):
    raise ValueError('Non-JSON constant: ' + value)


def _load_json(text):
    return json.loads(text, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)


def _objects(value):
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            yield item
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)


def validate_manifest(raw):
    """Validate metadata bytes from the same tree being scanned; grant no exemptions."""
    manifest = _load_json(raw.decode('utf-8-sig'))
    if not isinstance(manifest, dict):
        raise ValueError('Manifest must be a JSON object')
    if (manifest.get('schema_version') != '2.0'
            or manifest.get('distribution_mode') != 'references-only'
            or manifest.get('assets') != []
            or manifest.get('project_licence_applies') is not False
            or manifest.get('current_law_release') is not False):
        raise ValueError('Require schema 2.0, references-only, assets [], and both licence/current-law gates false')
    sources = manifest.get('sources')
    if not isinstance(sources, list) or not sources:
        raise ValueError('Require nonempty reference-only source metadata')
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError('Each source must be reference metadata')
        for field in ('title', 'issuer', 'official_url'):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise ValueError('Missing source metadata: ' + field)
        url = urlsplit(source['official_url'])
        if url.scheme not in {'https', 'http'} or not url.hostname or url.username or url.password:
            raise ValueError('Source official_url must be an HTTP(S) reference without credentials')
    for item in _objects(manifest):
        for key, value in item.items():
            field = key.casefold().replace('-', '_')
            if field in {'current_law_release', 'project_licence_applies',
                         'attachments_allowed', 'redistribution_allowed',
                         'attachment_included', 'distributed'} and value is not False:
                raise ValueError('Reference metadata cannot enable ' + key)
            if field == 'distribution_mode' and value != 'references-only':
                raise ValueError('Reference metadata cannot change distribution mode')
            if field == 'reference_only' and value is not True:
                raise ValueError('Source must remain reference-only')
            if field in {'redistribution_status', 'distribution_status'} and (
                    not isinstance(value, str) or value not in {
                        'reference-only', 'references-only', 'reference-only-no-attachment',
                        'not-distributed'}):
                raise ValueError('Reference metadata cannot approve redistribution')
            if field == 'assets' and value != []:
                raise ValueError('Source assets must be empty')
            if field in FULLTEXT_KEYS | {'path', 'local_path', 'snapshot_path', 'text_path',
                                        'attachments', 'attachment', 'files', 'content',
                                        'text', 'pages', 'payload', 'base64', 'data_uri'}:
                raise ValueError('Attachment or text payload field in manifest: ' + key)
    return manifest


def _relative_path(relative):
    path = PurePosixPath(relative)
    if (not relative or path.is_absolute() or path.as_posix() != relative
            or '\\' in relative or ':' in relative
            or any(part in {'.', '..'} or part.endswith((' ', '.')) for part in path.parts)
            or any(ord(char) < 32 or ord(char) == 127 for char in relative)):
        raise ValueError('Invalid or non-portable tracked path')
    return path


def _working_bytes(root, relative):
    path = root
    # Check every ancestor before reading; Windows junctions are reparse points.
    for part in _relative_path(relative).parts:
        path = path / part
        try:
            info = path.lstat()
        except FileNotFoundError:
            return None
        if (stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0)
                & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)):
            raise ValueError('Symlink or reparse point in tracked path')
    path.resolve().relative_to(root)
    if not stat.S_ISREG(info.st_mode):
        raise ValueError('Tracked path is not a regular file')
    return path.read_bytes()


def _excluded_path(relative):
    path = PurePosixPath(relative)
    parts = {part.casefold().replace('_', '-') for part in path.parts}
    name = path.name.casefold()
    if (parts & DENIED_PARTS or {s.casefold() for s in path.suffixes} & DENIED_SUFFIXES
            or name == 'permissions.local.json'
            or name == '.env' or name.startswith('.env.') and name != '.env.example'):
        return True
    if relative == SOURCE_TEXT:
        return False
    if path.suffix.casefold() not in CODE_SUFFIXES and EXPORT_NAME.search(name):
        return True
    return (path.suffix.casefold() in {'.html', '.htm', '.xml'}
            and path.parts[0].casefold() in {'evidence', 'official-documents', 'data'})


def _binary_format(raw):
    prefix = raw.removeprefix(b'\xef\xbb\xbf').lstrip(b' \t\r\n')
    signatures = (
        b'%PDF-', b'\x89PNG\r\n\x1a\n', b'\xff\xd8\xff', b'GIF87a', b'GIF89a',
        b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08', b'\xd0\xcf\x11\xe0',
        b'\x1f\x8b', b'BZh', b'\xfd7zXZ\x00', b'7z\xbc\xaf\x27\x1c', b'Rar!',
        b'SQLite format 3', b'\x7fELF', b'\x00asm', b'{\\rtf', b'RIFF',
    )
    return (prefix.startswith(signatures) or raw[257:262] == b'ustar'
            or re.search(br'(?m)^[ \t]*%PDF-', raw[:1024]) is not None
            or re.match(br'(?is)(?:<\?xml[^>]*>\s*)?<svg\b', prefix) is not None)


def _source_export(value):
    for item in _objects(value):
        fields = {key.casefold().replace('-', '_'): v for key, v in item.items()}
        if any(fields.get(field) for field in FULLTEXT_KEYS):
            return True
        # Match captured text records, not generic text/quote/locator metadata.
        if fields.get('text') and (
                fields.get('doc_type') == 'official-source-span'
                or {'source_sha256', 'text_sha256', 'locator'} <= fields.keys()
                or {'chunk_id', 'canonical_url', 'locator'} <= fields.keys()):
            return True
    return False


def inspect_bytes(relative, raw):
    """Return findings for a file without reading outside the supplied bytes."""
    findings = []
    if _excluded_path(relative):
        findings.append({'file': relative, 'kind': 'excluded-file'})
    if _binary_format(raw) or re.search(br'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', raw):
        findings.append({'file': relative, 'kind': 'unexpected-binary'})
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        findings.append({'file': relative, 'kind': 'non-utf8'})
        return findings
    if relative == SOURCE_TEXT and text.strip():
        findings.append({'file': relative, 'kind': 'nonempty-source-text-placeholder'})
    for kind, pattern in PATTERNS.items():
        if pattern.search(text):
            findings.append({'file': relative, 'kind': kind})
    path = PurePosixPath(relative)
    if path.suffix.casefold() not in CODE_SUFFIXES:
        try:
            records = [_load_json(text)]
        except (ValueError, RecursionError):
            records = []
            for line in text.splitlines():
                try:
                    records.append(_load_json(line))
                except (ValueError, RecursionError):
                    continue
        if any(_source_export(record) for record in records):
            findings.append({'file': relative, 'kind': 'source-text-export'})
    return findings


def _git(root, *args):
    result = subprocess.run(
        ['git', '-c', 'safe.directory=' + root.as_posix(), *args],
        cwd=root, check=True, capture_output=True,
        env={**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_NO_REPLACE_OBJECTS': '1',
             'GIT_OPTIONAL_LOCKS': '0'})
    return result.stdout


def _staged_bytes(root, oid):
    raw = _git(root, 'cat-file', 'blob', oid)
    algorithm = 'sha1' if len(oid) == 40 else 'sha256'
    digest = hashlib.new(algorithm, b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw)
    if digest.hexdigest() != oid:
        raise ValueError('Staged bytes do not match the indexed Git object ID')
    return raw


def _index_entries(root):
    actual_root = Path(_git(root, 'rev-parse', '--show-toplevel').decode('utf-8').strip()).resolve()
    if actual_root != root:
        raise ValueError('Scan root must be the Git repository root')
    entries = []
    for record in _git(root, 'ls-files', '--stage', '-z').split(b'\0'):
        if not record:
            continue
        metadata, relative = record.split(b'\t', 1)
        mode, oid, stage = metadata.decode('ascii').split()
        if not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', oid):
            raise ValueError('Invalid Git object ID')
        entries.append((relative.decode('utf-8'), mode, oid, stage))
    return entries


def scan_release(root=ROOT, staged=False):
    """Inspect current tracked files or the complete index, without mutating Git."""
    root = Path(root).resolve()
    report = {'mode': 'staged' if staged else 'working-tree', 'tracked_files': 0,
              'scanned_files': 0, 'missing_working_files': [], 'findings': [], 'scope': SCOPE}
    findings = report['findings']
    try:
        entries = _index_entries(root)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        findings.append({'kind': 'git-inspection-failed', 'detail': str(exc)})
        return report
    report['tracked_files'] = len(entries)
    if not entries:
        findings.append({'kind': 'no-tracked-files'})
    required = {}
    seen = set()
    for relative, mode, oid, stage in entries:
        try:
            _relative_path(relative)
            if relative.casefold() in seen:
                raise ValueError('Duplicate or case-colliding tracked path')
            seen.add(relative.casefold())
        except ValueError as exc:
            findings.append({'file': relative, 'kind': 'invalid-path', 'detail': str(exc)})
            continue
        if stage != '0':
            findings.append({'file': relative, 'kind': 'unmerged-index'})
            continue
        if mode not in {'100644', '100755'}:
            findings.append({'file': relative, 'kind': 'unsupported-git-mode', 'mode': mode})
            continue
        try:
            raw = _staged_bytes(root, oid) if staged else _working_bytes(root, relative)
        except (OSError, ValueError, subprocess.CalledProcessError) as exc:
            findings.append({'file': relative, 'kind': 'unreadable-or-unsafe-file', 'detail': str(exc)})
            continue
        if raw is None:
            report['missing_working_files'].append(relative)
            continue
        report['scanned_files'] += 1
        findings.extend(inspect_bytes(relative, raw))
        if relative in {MANIFEST, SOURCE_TEXT}:
            required[relative] = raw
    if MANIFEST not in required:
        findings.append({'file': MANIFEST, 'kind': 'invalid-evidence-manifest',
                         'detail': 'Manifest must exist as a tracked regular file in the scanned tree'})
    else:
        try:
            validate_manifest(required[MANIFEST])
        except (ValueError, RecursionError) as exc:
            findings.append({'file': MANIFEST, 'kind': 'invalid-evidence-manifest', 'detail': str(exc)})
    if SOURCE_TEXT not in required:
        findings.append({'file': SOURCE_TEXT, 'kind': 'missing-source-text-placeholder'})
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Git repository root to inspect')
    parser.add_argument('--staged', action='store_true', help='Inspect all exact index blobs instead of working files')
    args = parser.parse_args(argv)
    report = scan_release(args.root, staged=args.staged)
    print(json.dumps(report, indent=2))
    return 1 if report['findings'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
