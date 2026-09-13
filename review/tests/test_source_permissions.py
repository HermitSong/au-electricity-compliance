"""Synthetic offline checks of acquisition boundaries, not a rights opinion."""
import copy
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from collect_source_originals import Fetcher, SafeRedirect, main, save_object, seeds
from source_permissions import PermissionPolicy, linked_path, private_archive, private_path, source_url

URL = 'https://www.aer.gov.au/synthetic-source-not-a-real-document'


def permission_document(*urls):
    today = datetime.now(timezone.utc).date()
    return {'schema_version': '1.0', 'permissions': [{
        'id': 'synthetic-test-only', 'urls': list(urls or [URL]),
        'purpose': 'Offline synthetic tests; not real collection permission',
        'basis_type': 'written-permission', 'basis_reference': 'Synthetic fixture only',
        'reviewed_by': 'Synthetic test actor', 'reviewed_on': today.isoformat(),
        'valid_until': (today + timedelta(days=1)).isoformat(),
        'actions': ['download', 'local-store', 'extract-text'],
        'access_review': 'automated-access-permitted',
        'privacy_review': 'no-personal-information-expected'}]}


def item(url=URL):
    return {'canonical_url': url, 'references': [], 'source_family_ids': [],
            'discovery_depth': 0, 'discovered_from': []}


class SourcePermissionTests(unittest.TestCase):
    def test_missing_permission_makes_no_network_or_source_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            fetcher = Fetcher(set(), 5, 1024, 0)
            with patch.object(fetcher, 'request') as request:
                result = fetcher.fetch(item(), Path(tmp))
                request.assert_not_called()
            self.assertEqual(result['capture_status'], 'deferred')
            self.assertEqual(result['reason'], 'acquisition-permission-required')
            self.assertFalse(list(Path(tmp).iterdir()))
            with patch('collect_source_originals.build_opener') as opener:
                with self.assertRaises(ValueError):
                    fetcher.request(URL, 100)
                opener.assert_not_called()

    def test_exact_scope_does_not_extend_to_child_query_or_host(self):
        policy = PermissionPolicy(permission_document())
        policy.require(URL)
        policy.require(URL + '#page=2')
        for url in (URL + '/child.pdf', URL + '?version=2', URL.replace('www.aer', 'aer')):
            with self.subTest(url=url), self.assertRaises(ValueError):
                policy.require(url)

    def test_empty_expired_and_future_permissions_grant_nothing(self):
        with self.assertRaises(ValueError):
            PermissionPolicy({'schema_version': '1.0', 'permissions': []}).require(URL)
        today = datetime.now(timezone.utc).date()
        for start, end in ((-3, -1), (1, 2)):
            document = permission_document()
            document['permissions'][0]['reviewed_on'] = (today + timedelta(days=start)).isoformat()
            document['permissions'][0]['valid_until'] = (today + timedelta(days=end)).isoformat()
            with self.assertRaises(ValueError):
                PermissionPolicy(document).require(URL)

    def test_missing_review_or_actions_fail_before_network(self):
        for key, value in [('actions', ['download']), ('access_review', 'not-reviewed'),
                           ('privacy_review', 'unknown'), ('reviewed_by', ''),
                           ('basis_type', 'public-url'), ('urls', [])]:
            document = permission_document()
            document['permissions'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                PermissionPolicy(document)

    def test_duplicate_keys_and_urls_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'permissions.local.json'
            path.write_text('{"schema_version":"1.0","permissions":[],"permissions":[]}', encoding='utf-8')
            with self.assertRaises(ValueError):
                PermissionPolicy.load(path)
        document = permission_document()
        document['permissions'].append(copy.deepcopy(document['permissions'][0]))
        with self.assertRaises(ValueError):
            PermissionPolicy(document)

    def test_bad_destinations_rejected(self):
        for url in ('http://www.aer.gov.au/x', 'https://user:pass@www.aer.gov.au/x',
                    'https://127.0.0.1/x', 'https://localhost/x', 'https://host.local/x',
                    'https://www.aer.gov.au:444/x', 'https://*.gov.au/x',
                    URL + '?access_token=synthetic', URL + '?signature=synthetic',
                    URL + '?X-Amz-Credential=synthetic', URL + '?X-Amz-Signature=synthetic',
                    URL + '?sig=synthetic', URL + '?X-Goog-Credential=synthetic',
                    'https://www.aer.gov.au/\nheader', 'https://www.aer.gov.au\\@other.test/x'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                source_url(url)

    def test_robots_transport_does_not_grant_document_rights(self):
        policy = PermissionPolicy(permission_document())
        policy.require_transport('https://www.aer.gov.au/robots.txt')
        for url in ('https://other.gov.au/robots.txt', URL + '/other'):
            with self.assertRaises(ValueError):
                policy.require_transport(url)
        with self.assertRaises(ValueError):
            policy.require('https://www.aer.gov.au/robots.txt')

    def test_redirects_never_dispatch_even_to_an_approved_target(self):
        handler = SafeRedirect()
        request = Request(URL)
        for target in (URL + '/unreviewed', URL + '/approved', 'https://www.aemo.com.au/synthetic'):
            with self.subTest(target=target), self.assertRaises(ValueError):
                handler.redirect_request(request, None, 302, '', {}, target)

    def test_default_https_port_does_not_bypass_host_pause(self):
        fetcher = Fetcher(set(), 5, 1024, 0, PermissionPolicy(permission_document()))
        fetcher.robots['www.aer.gov.au'] = (None, None)
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(fetcher, 'request', side_effect=HTTPError(URL, 403, 'Synthetic denial', {}, None)) as request:
            self.assertEqual(fetcher.fetch(item(), Path(tmp))['reason'], 'http-403')
            alias = URL.replace('www.aer.gov.au/', 'WWW.AER.GOV.AU:443/')
            result = fetcher.fetch(item(alias), Path(tmp))
            self.assertIn('host-paused', result['reason'])
            self.assertEqual(request.call_count, 1)

    def test_nested_git_destinations_fail_before_network_or_writes(self):
        for relative in ('data', 'source-originals', 'review/results'):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                nested = root / relative
                nested.mkdir(parents=True)
                (nested / '.git').mkdir()
                fetcher = Fetcher(set(), 5, 1024, 0, PermissionPolicy(permission_document()))
                with patch.object(fetcher, 'request') as request:
                    result = fetcher.fetch(item(), root)
                    self.assertEqual(result['capture_status'], 'failed')
                    request.assert_not_called()
                with self.assertRaises(ValueError):
                    private_archive(root)
                self.assertEqual(list(nested.iterdir()), [nested / '.git'])

    def test_private_network_objects_cannot_enter_a_nested_git_shard(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = b'Synthetic object, not a publisher document.'
            shard = root / 'source-originals/objects' / hashlib.sha256(data).hexdigest()[:2]
            shard.mkdir(parents=True)
            (shard / '.git').mkdir()
            with self.assertRaises(ValueError):
                save_object(root, data, '.txt', require_private=True)
            self.assertEqual(list(shard.iterdir()), [shard / '.git'])

    def test_nested_junction_and_unresolved_specialist_outputs_are_rejected(self):
        from collect_observed_attachments import collect
        import collect_enumerated_sources
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'archive'
            linked = root / 'data'
            with patch('source_permissions.linked_path', side_effect=lambda p: p == linked):
                with self.assertRaises(ValueError):
                    private_archive(root)
            # Simulated reparse point is checked before resolve can hide it.
            with patch('source_permissions.linked_path', side_effect=lambda p: p == root):
                with self.assertRaises(ValueError):
                    collect(Path(tmp) / 'missing.jsonl', Path(tmp) / 'evidence', root)
                with patch.object(sys, 'argv', ['collector', '--root', str(ROOT), '--archive-root', tmp,
                                             '--output-root', str(root), '--permissions', str(Path(tmp) / 'missing.json')]):
                    with self.assertRaises(ValueError):
                        collect_enumerated_sources.main()

    def test_reparse_attribute_is_detected_without_path_is_junction(self):
        from types import SimpleNamespace
        import stat
        with patch.object(Path, 'lstat', return_value=SimpleNamespace(st_mode=stat.S_IFDIR,
                                                                   st_file_attributes=0x400)):
            self.assertTrue(linked_path(Path('synthetic-junction')))

    def test_repo_ancestor_worktree_and_symlink_outputs_rejected(self):
        for path in (ROOT, ROOT / 'ignored-private', ROOT.parent):
            with self.assertRaises(ValueError):
                private_path(path)
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / 'another-checkout'
            repo.mkdir()
            (repo / '.git').write_text('gitdir: external', encoding='utf-8')
            with self.assertRaises(ValueError):
                private_path(repo / 'private')
            self.assertEqual(private_path(base / 'private'), base / 'private')
            target = base / 'target'
            target.mkdir()
            link = base / 'link'
            try:
                link.symlink_to(target, target_is_directory=True)
            except OSError:
                self.skipTest('Symlink creation unavailable: Windows privilege requirement.')
            with self.assertRaises(ValueError):
                private_path(link / 'objects')

    def test_storage_rejects_symlink_below_private_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root, target = base / 'archive', base / 'elsewhere'
            root.mkdir()
            target.mkdir()
            try:
                (root / 'source-originals').symlink_to(target, target_is_directory=True)
            except OSError:
                self.skipTest('Symlink creation unavailable: Windows privilege requirement.')
            with self.assertRaises(ValueError):
                save_object(root, b'synthetic', '.txt')
            self.assertEqual(list(target.iterdir()), [])

    def test_permitted_synthetic_capture_remains_research_only(self):
        policy = PermissionPolicy(permission_document())
        fetcher = Fetcher(set(), 5, 1024, 0, policy)
        fetcher.robots['www.aer.gov.au'] = (None, None)
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(fetcher, 'permission', return_value=(True, 'robots-not-published')), \
                patch.object(fetcher, 'request', return_value=(b'Synthetic source.', {'content-type': 'text/plain'}, URL, 200)):
            result = fetcher.fetch(item(), Path(tmp))
            self.assertEqual(result['capture_status'], 'bytes-preserved')
            self.assertEqual(result['permission_policy_sha256'], policy.sha256)
            self.assertFalse(result['current_law_release'])
            self.assertEqual(result['redistribution_status'], 'not-cleared')
            self.assertEqual(result['legal_review_status'], 'not-reviewed')

    def test_inventory_cli_default_does_not_request_network(self):
        with tempfile.TemporaryDirectory() as tmp, patch('collect_source_originals.Fetcher.request') as request:
            with patch.object(sys, 'argv', ['collect_source_originals.py', '--root', str(ROOT), '--output-root', tmp]), \
                    patch('sys.stdout', new_callable=io.StringIO):
                self.assertEqual(main(), 0)
            request.assert_not_called()
            summary = json.loads((Path(tmp) / 'data/source-original-summary.json').read_text('utf-8'))
            self.assertGreater(summary['inventory_url_count'], 0)
            self.assertEqual(summary['response_bytes_preserved_url_count'], 0)
            gaps = (Path(tmp) / 'data/source-original-gap-queue.jsonl').read_text('utf-8')
            self.assertIn('acquisition-and-local-use-permission-review', gaps)

    def test_download_cli_requires_explicit_permission_file(self):
        with tempfile.TemporaryDirectory() as tmp, patch('collect_source_originals.Fetcher.request') as request:
            with patch.object(sys, 'argv', ['collector', '--download', '--output-root', tmp]), \
                    patch('sys.stderr', new_callable=io.StringIO), self.assertRaises(SystemExit) as exc:
                main()
            self.assertEqual(exc.exception.code, 2)
            request.assert_not_called()

    def test_public_checkout_seed_inventory_needs_no_original_directory(self):
        entries, _ = seeds(ROOT)
        self.assertGreater(len(entries), 800)

    def test_retired_snapshot_command_cannot_fetch(self):
        import snapshot_official_sources
        with self.assertRaises(ValueError):
            snapshot_official_sources.capture(URL, ROOT, 1, 100)
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/snapshot_official_sources.py')], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b'disabled', result.stderr)


if __name__ == '__main__':
    unittest.main()
