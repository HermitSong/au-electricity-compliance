"""Release metadata consistency, not legal interpretation or clearance."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_public_release import validate_manifest


def reference_manifest():
    return {
        'schema_version': '2.0', 'distribution_mode': 'references-only',
        'project_licence_applies': False, 'current_law_release': False, 'assets': [],
        'sources': [{'title': 'Synthetic source reference', 'issuer': 'Example issuer',
                     'official_url': 'https://example.org/reference.pdf',
                     'redistribution_status': 'reference-only', 'current_law_release': False}],
    }


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

    def test_actual_release_has_two_references_and_no_asset_exemptions(self):
        manifest = validate_manifest((ROOT / 'evidence/manifest.json').read_bytes())
        self.assertEqual(manifest['assets'], [])
        self.assertEqual(len(manifest['sources']), 2)
        self.assertFalse(manifest['project_licence_applies'])
        self.assertFalse(manifest['current_law_release'])

    def test_valid_reference_metadata(self):
        manifest = reference_manifest()
        self.assertEqual(validate_manifest(json.dumps(manifest).encode()), manifest)

    def test_policy_switches_fail_closed(self):
        for field, value in [
                ('schema_version', '1.0'), ('distribution_mode', 'attachments'),
                ('assets', [{'path': 'evidence/originals/reintroduced.pdf'}]),
                ('assets', None), ('assets', {}), ('project_licence_applies', True),
                ('project_licence_applies', 0), ('current_law_release', True),
                ('current_law_release', 'false'), ('sources', []), ('sources', {}),
                ('sources', [None])]:
            with self.subTest(field=field, value=value):
                manifest = reference_manifest()
                manifest[field] = value
                with self.assertRaises(ValueError):
                    validate_manifest(json.dumps(manifest).encode())

    def test_missing_required_fields_fail_closed(self):
        manifest = reference_manifest()
        for field in manifest:
            with self.subTest(field=field):
                changed = copy.deepcopy(manifest)
                del changed[field]
                with self.assertRaises(ValueError):
                    validate_manifest(json.dumps(changed).encode())

    def test_source_record_cannot_reenable_attachments_or_payloads(self):
        for field, value in [
                ('path', 'evidence/originals/source.pdf'), ('path', '../outside.txt'),
                ('attachments', []), ('assets', [{'path': 'source.pdf'}]),
                ('redistribution_status', 'reviewed-for-this-release'),
                ('redistribution_status', []),
                ('current_law_release', True), ('project_licence_applies', True),
                ('distribution_mode', 'attachments'), ('attachments_allowed', True),
                ('full_text', 'Copied source body'), ('content', {'base64': 'payload'}),
                ('official_url', 'file:///private/source.pdf'), ('title', '')]:
            with self.subTest(field=field):
                manifest = reference_manifest()
                manifest['sources'][0][field] = value
                with self.assertRaises(ValueError):
                    validate_manifest(json.dumps(manifest).encode())

    def test_malformed_manifest_fails_closed(self):
        valid = json.dumps(reference_manifest()).encode()
        cases = [b'', b'{', b'[]', b'null', b'false', b'\xff',
                 valid[:-1] + b', "assets": []}',
                 valid[:-1] + b', "unexpected": NaN}']
        for raw in cases:
            with self.subTest(raw=raw[:25]), self.assertRaises(ValueError):
                validate_manifest(raw)


if __name__ == '__main__':
    unittest.main()
