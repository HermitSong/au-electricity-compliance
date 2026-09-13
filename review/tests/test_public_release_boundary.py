"""Functional boundary tests using temporary files and a read-only fake Git index."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_public_release as boundary
from test_release_licensing import reference_manifest


class PublicReleaseBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve() / 'repo'
        self.root.mkdir()
        self.entries = {}
        self.blobs = {}
        self.calls = []
        self.add(boundary.MANIFEST, json.dumps(reference_manifest()).encode())
        self.add(boundary.SOURCE_TEXT, b'')
        self.git_patch = patch.object(boundary, '_git', side_effect=self.git)
        self.git_patch.start()
        self.addCleanup(self.git_patch.stop)

    def add(self, relative, raw, mode='100644', stage='0', working=True):
        oid = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        self.entries[relative] = (mode, oid, stage)
        self.blobs[oid] = raw
        if working:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        return oid

    def git(self, root, *args):
        self.assertEqual(root, self.root)
        self.calls.append(args)
        if args == ('rev-parse', '--show-toplevel'):
            return str(self.root).encode() + b'\n'
        if args == ('ls-files', '--stage', '-z'):
            return b''.join(f'{mode} {oid} {stage}\t{path}'.encode() + b'\0'
                            for path, (mode, oid, stage) in self.entries.items())
        if args[:2] == ('cat-file', 'blob'):
            return self.blobs[args[2]]
        self.fail('Unexpected Git command: ' + repr(args))

    def scan(self, staged=False):
        return boundary.scan_release(self.root, staged=staged)

    def kinds(self, report, relative=None):
        return {row['kind'] for row in report['findings']
                if relative is None or row.get('file') == relative}

    def test_original_prose_code_metadata_and_synthetic_quotes_pass(self):
        self.add('knowledge-base/original.md', b'# Original analysis\nOrdinary English analysis with source links.\n')
        self.add('data/case.json', json.dumps({
            'status': 'proceedings', 'source_url': 'https://example.org/decision',
            'source_locator': {'locator': 'page:2', 'quote': 'A short binding locator'},
            'snapshot_path': 'source-originals/objects/historical.pdf',
        }).encode())
        self.add('review/fixtures/example.json', b'{"synthetic": true, "text": "Example meeting", "quote": "Synthetic wording"}')
        self.add('scripts/extract_source_text.py', b'fixture = {"full_text": "Synthetic text"}\n')
        self.add('.env.example', b'EXAMPLE_TOKEN=\n')
        self.assertEqual(self.scan()['findings'], [])
        self.assertEqual(self.scan(staged=True)['findings'], [])

    def test_acquisition_materials_and_new_tests_pass_the_same_byte_checks(self):
        for relative in (
                'scripts/source_permissions.py',
                'SOURCE-ACQUISITION.md',
                'skills/au-lawful-source-acquisition/SKILL.md',
                'review/tests/test_public_release_boundary.py',
                'review/tests/test_release_licensing.py'):
            with self.subTest(relative=relative):
                self.assertEqual(boundary.inspect_bytes(relative, (ROOT / relative).read_bytes()), [])

    def test_excluded_formats_and_archive_private_paths(self):
        paths = ['source-originals/item.txt', 'OFFICIAL-SNAPSHOTS/item.md',
                 'review/runs/result.json', 'private-operations/meeting.txt',
                 'operations-runs/result.txt', 'evidence/originals/renamed.txt',
                 'evidence/renders/page.txt', 'office-recovery/result.txt',
                 'screenshots/page.md', 'OCR/output.txt', 'source_archives/archive.txt',
                 'misc/notes.PDF', 'misc/source.pdf.txt', 'misc/file.docm',
                 'misc/file.xlsx', 'misc/file.pptx', 'misc/file.odt', 'misc/file.rtf',
                 'misc/page.PNG', 'misc/page.svg', 'misc/archive.tar.gz',
                 'misc/archive.7z', 'misc/archive.zip', 'misc/cache.sqlite3',
                 'misc/archive.epub', '.env.production', 'misc/fulltext.md',
                 'misc/source-text-export.jsonl', 'official-documents/copy.html',
                 'permissions.local.json', 'misc/__pycache__/cache.txt']
        for relative in paths:
            self.add(relative, b'{}')
        report = self.scan()
        for relative in paths:
            with self.subTest(relative=relative):
                self.assertIn('excluded-file', self.kinds(report, relative))

    def test_renamed_source_bytes_and_non_utf8_fail_without_crashing(self):
        samples = [b'%PDF-1.7\nOriginal source', b' \n%PDF-1.4\nASCII only',
                   b'\x89PNG\r\n\x1a\nimage', b'PK\x03\x04archive',
                   b'\xd0\xcf\x11\xe0office', b'GIF89aimage', b'{\\rtf1 source}',
                   b'<svg xmlns="http://www.w3.org/2000/svg"></svg>',
                   b'\x00opaque', b'control\x01', b'\xff\xfe', b'latin-1 \xe9']
        for index, raw in enumerate(samples):
            self.add(f'misc/renamed-{index}.md', raw)
        for staged in (False, True):
            report = self.scan(staged)
            for index in range(len(samples)):
                with self.subTest(staged=staged, index=index):
                    self.assertTrue(self.kinds(report, f'misc/renamed-{index}.md') &
                                    {'unexpected-binary', 'non-utf8'})

    def test_renamed_fulltext_exports_fail_but_quote_fields_are_not_banned(self):
        records = [{'full_text': 'Source body'}, {'nested': [{'ocr_text': 'Source page'}]},
                   {'text': 'Source body', 'chunk_id': '1', 'canonical_url': 'https://example.org', 'locator': 'page:1'},
                   {'doc_type': 'official-source-span', 'text': 'Source span'}]
        for index, value in enumerate(records):
            self.add(f'misc/reference-{index}.txt', json.dumps(value).encode())
        self.add('misc/records.md', b'{"id": 1}\n{"extracted_text": "Source body"}\n')
        report = self.scan()
        for relative in [f'misc/reference-{i}.txt' for i in range(len(records))] + ['misc/records.md']:
            self.assertIn('source-text-export', self.kinds(report, relative))

    def test_source_text_placeholder_is_required_tracked_and_empty(self):
        for raw in (b'', b'\n', b' \t\r\n', b'\xef\xbb\xbf\n'):
            self.add(boundary.SOURCE_TEXT, raw)
            self.assertEqual(self.scan()['findings'], [])
        self.add(boundary.SOURCE_TEXT, b'{"quote": "Even a small source payload"}\n')
        self.assertIn('nonempty-source-text-placeholder', self.kinds(self.scan()))
        del self.entries[boundary.SOURCE_TEXT]
        self.assertIn('missing-source-text-placeholder', self.kinds(self.scan()))

    def test_missing_untracked_malformed_and_reenabled_manifest_fail_closed(self):
        for raw in (b'[]', b'{', b'\xff', b'{"assets": []}'):
            self.add(boundary.MANIFEST, raw)
            self.assertIn('invalid-evidence-manifest', self.kinds(self.scan()))
        manifest = reference_manifest()
        manifest['assets'] = [{'path': 'misc/exempt.md', 'sha256': '0' * 64}]
        self.add(boundary.MANIFEST, json.dumps(manifest).encode())
        self.add('misc/exempt.md', b'%PDF-1.4')
        report = self.scan()
        self.assertIn('invalid-evidence-manifest', self.kinds(report))
        self.assertIn('unexpected-binary', self.kinds(report, 'misc/exempt.md'))
        self.add(boundary.MANIFEST, json.dumps(reference_manifest()).encode())
        del self.entries[boundary.MANIFEST]
        self.assertIn('invalid-evidence-manifest', self.kinds(self.scan()))

    def test_paths_cannot_escape_in_either_mode(self):
        paths = ['../outside.md', '/outside.md', 'C:/outside.md',
                 'evidence/../../outside.md', 'data\\outside.md',
                 'data//outside.md', './outside.md', 'data/./outside.md',
                 'data/file.md:stream', 'data/../outside.md', 'data./outside.md']
        for relative in paths:
            self.add(relative, b'outside', working=False)
        for staged in (False, True):
            report = self.scan(staged)
            for relative in paths:
                with self.subTest(relative=relative, staged=staged):
                    self.assertIn('invalid-path', self.kinds(report, relative))

    def test_index_symlinks_submodules_and_unmerged_entries_fail_closed(self):
        for mode in ('120000', '160000', '100600'):
            self.add(f'misc/mode-{mode}', b'../outside', mode=mode, working=False)
        self.add('misc/conflict.md', b'conflict', stage='2')
        for staged in (False, True):
            report = self.scan(staged)
            self.assertIn('unmerged-index', self.kinds(report, 'misc/conflict.md'))
            for mode in ('120000', '160000', '100600'):
                self.assertIn('unsupported-git-mode', self.kinds(report, f'misc/mode-{mode}'))

    def test_working_symlink_and_symlink_ancestor_are_not_followed(self):
        outside = self.root.parent / 'outside'
        outside.mkdir()
        (outside / 'source.md').write_bytes(b'%PDF-1.4')
        try:
            (self.root / 'link.md').symlink_to(outside / 'source.md')
            (self.root / 'linked-dir').symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest('Symlink creation unavailable: ' + str(exc))
        self.add('link.md', b'safe staged text', working=False)
        self.add('linked-dir/source.md', b'safe staged text', working=False)
        report = self.scan()
        for relative in ('link.md', 'linked-dir/source.md'):
            self.assertIn('unreadable-or-unsafe-file', self.kinds(report, relative))
        self.assertEqual(self.scan(staged=True)['findings'], [])

    def test_reparse_point_is_rejected_even_without_symlink_privilege(self):
        self.add('misc/source.md', b'original')
        real_lstat = Path.lstat

        def lstat(path):
            if path == self.root / 'misc':
                class ReparsePoint:
                    st_mode = stat.S_IFDIR
                    st_file_attributes = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)
                return ReparsePoint()
            return real_lstat(path)

        with patch.object(Path, 'lstat', lstat):
            self.assertIn('unreadable-or-unsafe-file', self.kinds(self.scan(), 'misc/source.md'))

    def test_staged_source_bytes_cannot_be_hidden_by_safe_working_copy(self):
        oid = self.add('misc/original.md', b'%PDF-1.7\nSource original')
        (self.root / 'misc/original.md').write_bytes(b'Original project commentary\n')
        self.assertEqual(self.scan()['findings'], [])
        report = self.scan(staged=True)
        self.assertIn('unexpected-binary', self.kinds(report, 'misc/original.md'))
        self.assertIn(('cat-file', 'blob', oid), self.calls)

    def test_blob_substitution_cannot_approve_different_staged_bytes(self):
        oid = self.add('misc/original.md', b'%PDF-1.7\nSource original')
        self.blobs[oid] = b'Harmless replacement text'
        self.assertIn('unreadable-or-unsafe-file', self.kinds(self.scan(staged=True), 'misc/original.md'))

    def test_sha256_git_object_ids_are_supported(self):
        raw = b'Original analysis\n'
        oid = hashlib.sha256(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        self.entries['misc/original.md'] = ('100644', oid, '0')
        self.blobs[oid] = raw
        self.assertEqual(self.scan(staged=True)['findings'], [])

    def test_staged_safe_copy_does_not_hide_unsafe_working_copy(self):
        self.add('misc/original.md', b'Original commentary\n')
        (self.root / 'misc/original.md').write_bytes(b'%PDF-1.4')
        self.assertIn('unexpected-binary', self.kinds(self.scan(), 'misc/original.md'))
        self.assertEqual(self.scan(staged=True)['findings'], [])

    def test_unstaged_removal_is_reported_but_staged_blob_is_still_rejected(self):
        self.add('evidence/originals/removed.pdf', b'%PDF-1.4', working=False)
        report = self.scan()
        self.assertEqual(report['findings'], [])
        self.assertEqual(report['missing_working_files'], ['evidence/originals/removed.pdf'])
        self.assertIn('excluded-file', self.kinds(self.scan(staged=True), 'evidence/originals/removed.pdf'))

    def test_manifest_and_placeholder_are_checked_from_the_selected_tree(self):
        self.add(boundary.MANIFEST, b'{"schema_version": "1.0", "assets": []}')
        (self.root / boundary.MANIFEST).write_bytes(json.dumps(reference_manifest()).encode())
        self.add(boundary.SOURCE_TEXT, b'{"text": "Source text"}\n')
        (self.root / boundary.SOURCE_TEXT).write_bytes(b'')
        self.assertEqual(self.scan()['findings'], [])
        kinds = self.kinds(self.scan(staged=True))
        self.assertIn('invalid-evidence-manifest', kinds)
        self.assertIn('nonempty-source-text-placeholder', kinds)
        (self.root / boundary.MANIFEST).unlink()
        (self.root / boundary.SOURCE_TEXT).unlink()
        kinds = self.kinds(self.scan())
        self.assertIn('invalid-evidence-manifest', kinds)
        self.assertIn('missing-source-text-placeholder', kinds)

    def test_failed_git_or_blob_read_returns_findings(self):
        with patch.object(boundary, '_git', side_effect=subprocess.CalledProcessError(1, ['git'])):
            self.assertIn('git-inspection-failed', self.kinds(self.scan()))

        def fail_blob(root, *args):
            if args[0] == 'cat-file':
                raise OSError('Missing blob')
            return self.git(root, *args)

        with patch.object(boundary, '_git', side_effect=fail_blob):
            self.assertIn('unreadable-or-unsafe-file', self.kinds(self.scan(staged=True)))

    def test_cli_returns_json_and_nonzero_for_failure(self):
        self.add('misc/renamed.txt', b'%PDF-1.4')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = boundary.main(['--root', str(self.root), '--staged'])
        self.assertEqual(status, 1)
        report = json.loads(output.getvalue())
        self.assertEqual(report['mode'], 'staged')
        self.assertIn('unexpected-binary', self.kinds(report))


if __name__ == '__main__':
    unittest.main()
