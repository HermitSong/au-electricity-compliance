import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from collect_source_originals import extract, generic_reextract_allowed, save_object, select_manifest_rows
from merge_source_recovery import acceptable, fingerprint, is_fallback
from recover_embedded_sources import record_payload
from validate_source_originals import check_artifacts


class RecoveryTests(unittest.TestCase):
    def test_generic_reextract_preserves_specialist_extraction(self):
        row = {'capture_status': 'bytes-preserved'}
        self.assertTrue(generic_reextract_allowed(row))
        for key in ('ocr_pages_path', 'embedded_record_path', 'browser_capture_provenance'):
            self.assertFalse(generic_reextract_allowed({**row, key: 'evidence'}))

    def test_docx_text_and_locator(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as package:
            package.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Section 31: $25 million</w:t></w:r></w:p></w:body></w:document>')
        result = extract(stream.getvalue(), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'https://www.aer.gov.au/test.docx')
        self.assertEqual(result['units'], [{'locator': 'docx:word/document.xml:paragraph:1', 'text': 'Section 31: $25 million'}])

    def test_xlsx_empty_leading_cells_and_formulas(self):
        from openpyxl import Workbook
        book, stream = Workbook(), io.BytesIO()
        book.active['B2'] = 'Penalty'
        book.active['C2'] = '=2+3'
        book.save(stream)
        book.close()
        result = extract(stream.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'https://www.aer.gov.au/test.xlsx')
        self.assertEqual(result['units'], [{'locator': 'xlsx:Sheet:row:2', 'text': 'B2: Penalty\nC2: =2+3'}])
        self.assertIn('unevaluated', result['content_class'])

    def test_unknown_zip_not_binary_text(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w') as package:
            package.writestr('test', 'not a Word document')
        result = extract(stream.getvalue(), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'https://www.aer.gov.au/test')
        self.assertFalse(result['units'])
        self.assertEqual(result['extraction_status'], 'unsupported-format')

    def test_explicit_invalidation_removes_old_garbage(self):
        old = {'canonical_url': 'https://www.aer.gov.au/test', 'text_path': 'old'}
        failed = {'canonical_url': old['canonical_url'], 'capture_status': 'failed'}
        self.assertIn(old['canonical_url'], select_manifest_rows([old, failed])[1])
        self.assertNotIn(old['canonical_url'], select_manifest_rows([old, {**failed, 'invalidates_prior_text': True}])[1])

    def test_sidebar_excluded_but_corrected_main_kept(self):
        row = {'text_path': 'text', 'extraction_status': 'extracted-unreviewed', 'browser_capture_provenance': {'selector': '.layout-col'}}
        self.assertFalse(acceptable(row))
        row['browser_capture_provenance']['selector'] = '.layout-col:has(h1)'
        self.assertTrue(acceptable(row))

    def test_counterpart_is_not_original(self):
        self.assertTrue(is_fallback({'source_relation': {'kind': 'public-register-counterpart'}}))
        self.assertFalse(is_fallback({'source_relation': {'kind': 'official-relocated-document'}}))

    def test_import_fingerprint_ignores_bookkeeping_not_content(self):
        row = {'canonical_url': 'https://www.aer.gov.au/a', 'sha256': 'a', 'text_sha256': 'b'}
        self.assertEqual(fingerprint(row), fingerprint({**row, 'recovery_imported_at': 'later'}))
        self.assertNotEqual(fingerprint(row), fingerprint({**row, 'text_sha256': 'c'}))

    def test_record_id_and_nonempty_body(self):
        data = [{'drupal_internal__id': 1, 'field_body': 2}, 123, {'value': 3}, '<p>Full case text</p>']
        self.assertEqual(record_payload(data, 123)['field_body']['value'], '<p>Full case text</p>')
        with self.assertRaises(ValueError):
            record_payload(data, 124)
        with self.assertRaises(ValueError):
            record_payload([data[0], 123, {'value': 2}], 123)

    def test_nested_ocr_evidence_and_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image_path, image_hash = save_object(root, b'page image', '.png')
            pages_path, pages_hash = save_object(root, json.dumps([{'page': 1, 'image_path': image_path, 'image_sha256': image_hash}]).encode(), '.json')
            row = {'page_count': 1, 'ocr_pages_path': pages_path, 'ocr_pages_sha256': pages_hash}
            errors = []
            check_artifacts(root, row, set(), errors)
            self.assertFalse(errors)
            (root / image_path).write_bytes(b'changed')
            check_artifacts(root, row, set(), errors)
            self.assertTrue(errors)

    def test_nested_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pages_path, pages_hash = save_object(root, json.dumps([{'page': 1, 'image_path': '../outside.png', 'image_sha256': 'x'}]).encode(), '.json')
            errors = []
            check_artifacts(root, {'page_count': 1, 'ocr_pages_path': pages_path, 'ocr_pages_sha256': pages_hash}, set(), errors)
            self.assertTrue(any('escapes' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
