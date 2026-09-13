"""Release text/asset consistency checks, not legal interpretation or clearance."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_public_release import approved_assets


class ReleaseLicensingTests(unittest.TestCase):
    def test_release_documents_point_to_custom_licence(self):
        licence = (ROOT / 'LICENSE').read_text('utf-8')
        self.assertTrue(licence.startswith('Australian Electricity Compliance Source-Available Licence 1.0'))
        self.assertIn('valid earlier MIT or Creative Commons permissions', licence)
        self.assertIn('Internal Use, including production deployment', licence)
        self.assertIn('white-label or rebranded commercial version', licence)
        readme = (ROOT / 'README.md').read_text('utf-8')
        self.assertIn('not OSI-approved open source', readme)
        self.assertNotIn('[MIT](LICENSE)', readme)
        self.assertNotIn('[CC BY 4.0](LICENSE-CONTENT.md)', readme)

    def test_contribution_grant_requires_explicit_acknowledgement(self):
        contribution = (ROOT / 'CONTRIBUTING.md').read_text('utf-8')
        self.assertIn('Do not infer this grant from a fork', contribution)
        self.assertIn('I retain ownership', contribution)
        self.assertIn('third-party material', contribution)
        self.assertIn('An unchecked box is not consent', (ROOT / '.github/pull_request_template.md').read_text('utf-8'))

    def test_actual_assets_are_separate_from_current_law_and_project_licence(self):
        assets = approved_assets(ROOT)
        self.assertEqual(len(assets), 4)
        self.assertEqual(sum(path.endswith('.pdf') for path in assets), 2)
        for asset in assets.values():
            self.assertFalse(asset['current_law_release'])
            self.assertIsNone(asset['retrieved_at'])

    def fixture(self, folder):
        root = Path(folder)
        manifest = json.loads((ROOT / 'evidence/manifest.json').read_text('utf-8'))
        manifest['assets'] = [manifest['assets'][0]]
        path = root / manifest['assets'][0]['path']
        path.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / manifest['assets'][0]['path'], path)
        return root, manifest, path

    def write_manifest(self, root, manifest):
        (root / 'evidence/manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def test_tampered_bytes_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root, manifest, path = self.fixture(folder)
            self.write_manifest(root, manifest)
            path.write_bytes(path.read_bytes() + b'changed')
            with self.assertRaises(ValueError):
                approved_assets(root)

    def test_unreviewed_or_promoted_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root, manifest, _ = self.fixture(folder)
            for field, value in [('redistribution_status', 'not-cleared'),
                                 ('current_law_release', True), ('attribution', '')]:
                with self.subTest(field=field):
                    changed = copy.deepcopy(manifest)
                    changed['assets'][0][field] = value
                    self.write_manifest(root, changed)
                    with self.assertRaises(ValueError):
                        approved_assets(root)
            manifest['project_licence_applies'] = True
            self.write_manifest(root, manifest)
            with self.assertRaises(ValueError):
                approved_assets(root)

    def test_out_of_scope_paths_and_duplicates_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root, manifest, _ = self.fixture(folder)
            for path in ['../secret.pdf', '/evidence/originals/a.pdf',
                         'evidence/originals/../../a.pdf', 'evidence/originals/a.html',
                         'evidence\\originals\\a.pdf']:
                with self.subTest(path=path):
                    changed = copy.deepcopy(manifest)
                    changed['assets'][0]['path'] = path
                    self.write_manifest(root, changed)
                    with self.assertRaises(ValueError):
                        approved_assets(root)
            manifest['assets'].append(copy.deepcopy(manifest['assets'][0]))
            self.write_manifest(root, manifest)
            with self.assertRaises(ValueError):
                approved_assets(root)

    def test_arbitrary_binary_is_not_approved_by_matching_hash(self):
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            root, manifest, path = self.fixture(folder)
            raw = b'Not a PDF'
            path.write_bytes(raw)
            manifest['assets'][0].update(size_bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
            self.write_manifest(root, manifest)
            with self.assertRaises(ValueError):
                approved_assets(root)


if __name__ == '__main__':
    unittest.main()
