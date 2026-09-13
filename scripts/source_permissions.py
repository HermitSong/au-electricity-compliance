"""Operator-recorded acquisition scope, not a publisher licence or legal opinion."""
from datetime import date, datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import stat
from urllib.parse import parse_qsl, quote, urldefrag, urlparse, urlunparse


PUBLIC_ROOT = Path(__file__).resolve().parents[1]
ACTIONS = {'download', 'local-store', 'extract-text'}


def linked_path(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return bool(stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0)
                & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400))


def private_path(path, *excluded_roots):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if linked_path(part):
            raise ValueError('Private paths must not traverse symlinks or junctions')
        if (part / '.git').exists():
            raise ValueError('Acquisition files must stay outside Git worktrees')
    resolved = path.resolve()
    for root in (PUBLIC_ROOT, *excluded_roots):
        root = Path(root).resolve()
        if resolved.is_relative_to(root) or root.is_relative_to(resolved):
            raise ValueError('Private output must be disjoint from the knowledge repository')
    return resolved


def private_archive(path, *excluded_roots):
    root = private_path(path, *excluded_roots)
    for relative in ('source-originals/objects', 'source-originals/manifest.jsonl',
                     'source-originals/search.sqlite3', 'source-originals/search.sqlite3-journal',
                     'source-originals/search.sqlite3-wal', 'source-originals/search.sqlite3-shm',
                     'data/source-original-inventory.jsonl', 'data/source-original-gap-queue.jsonl',
                     'data/source-original-summary.json', 'review/results/original-source-collection-report.md'):
        private_path(root / relative, *excluded_roots)
    return root


def source_url(value):
    if not isinstance(value, str) or any(ord(c) < 32 for c in value) or '\\' in value:
        raise ValueError('Invalid source URL')
    parsed = urlparse(urldefrag(value.strip())[0])
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
            or parsed.password or parsed.port not in (None, 443)
            or '*' in value or parsed.hostname.endswith(('.local', '.localhost'))
            or '.' not in parsed.hostname):
        raise ValueError('Only explicitly reviewed public HTTPS URLs are supported')
    try:
        ipaddress.ip_address(parsed.hostname)
    except ValueError:
        pass
    else:
        raise ValueError('IP-address destinations are not supported')
    if any(key.lower().replace('-', '_') in {'token', 'access_token', 'api_key', 'apikey',
                                           'authorization', 'password', 'session', 'sessionid', 'signature',
                                           'sig', 'x_amz_credential', 'x_amz_signature', 'x_amz_security_token',
                                           'x_goog_credential', 'x_goog_signature', 'googleaccessid', 'awsaccesskeyid'}
           for key, _ in parse_qsl(parsed.query)):
        raise ValueError('Credential or signed-session URLs are not public acquisition targets')
    return urlunparse(parsed._replace(
        scheme='https', netloc=parsed.hostname.lower(),
        path=quote(parsed.path or '/', safe="/%:@!$&'()*+,;=-._~"),
        query=quote(parsed.query, safe="/?%:@!$&'()*+,;=-._~")))


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate permission field')
        result[key] = value
    return result


class PermissionPolicy:
    def __init__(self, document):
        if not isinstance(document, dict) or document.get('schema_version') != '1.0':
            raise ValueError('Unsupported acquisition permission schema')
        if not isinstance(document.get('permissions'), list):
            raise ValueError('permissions must be a list; an empty list grants nothing')
        self.entries = {}
        for entry in document['permissions']:
            if not isinstance(entry, dict):
                raise ValueError('Invalid acquisition permission record')
            for field in ('id', 'purpose', 'basis_reference', 'reviewed_by'):
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    raise ValueError('Missing permission field: ' + field)
            if entry.get('basis_type') not in {'publisher-licence', 'written-permission', 'reviewed-statutory-exception'}:
                raise ValueError('A specific acquisition and local-use basis is required')
            if entry.get('access_review') != 'automated-access-permitted':
                raise ValueError('Automated access must be reviewed separately')
            if entry.get('privacy_review') not in {'no-personal-information-expected', 'reviewed-lawful-handling'}:
                raise ValueError('Privacy review is required')
            if set(entry.get('actions', [])) != ACTIONS:
                raise ValueError('Download, local storage and extraction must all be covered')
            reviewed = date.fromisoformat(entry['reviewed_on'])
            expiry = date.fromisoformat(entry['valid_until'])
            if reviewed > expiry:
                raise ValueError('Invalid permission review interval')
            if not isinstance(entry.get('urls'), list) or not entry['urls']:
                raise ValueError('Exact URLs are required; domain-wide grants are unsupported')
            for value in entry['urls']:
                url = source_url(value)
                if url in self.entries:
                    raise ValueError('Duplicate acquisition URL')
                self.entries[url] = entry
        self.sha256 = hashlib.sha256(json.dumps(document, sort_keys=True, ensure_ascii=True).encode()).hexdigest()

    @classmethod
    def load(cls, path):
        path = private_path(path)
        if path.stat().st_size > 2_000_000:
            raise ValueError('Permission file exceeds the bounded review size')
        return cls(json.loads(path.read_text('utf-8-sig'), object_pairs_hook=unique_object))

    def require(self, url):
        entry = self.entries.get(source_url(url))
        today = datetime.now(timezone.utc).date()
        if not entry or not date.fromisoformat(entry['reviewed_on']) <= today <= date.fromisoformat(entry['valid_until']):
            raise ValueError('acquisition-permission-required-or-expired')
        return {'permission_id': entry['id'], 'permission_policy_sha256': self.sha256,
                'permission_valid_until': entry['valid_until'],
                'permission_status': 'operator-recorded-scope-not-independently-certified'}

    def require_transport(self, url):
        normal = source_url(url)
        parsed = urlparse(normal)
        if parsed.path == '/robots.txt' and not parsed.query:
            for target in self.entries:
                if urlparse(target).netloc == parsed.netloc:
                    try:
                        return self.require(target)
                    except ValueError:
                        continue
        return self.require(normal)
