import hashlib
import io
import json
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

from collect_source_originals import read_jsonl, save_object
from merge_source_recovery import acceptable, fingerprint, verified_bytes
from validate_source_originals import check_artifacts
import recover_preserved_pdf_text as recovery


TEXT = "The retailer must retain source evidence and review each applicable requirement before any operational release."


def pdf_bytes(pages):
    buffer = io.BytesIO()
    writer = canvas.Canvas(buffer, invariant=1)
    for text in pages:
        if text:
            writer.drawString(30, 700, text)
        writer.showPage()
    writer.save()
    return buffer.getvalue()


class PreservedPdfRecoveryTests(unittest.TestCase):
    def setUp(self):
        recovery.OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="test-preserved-pdf-", dir=recovery.OUTPUT_BASE)
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "source"
        self.output = Path(self.temp.name) / "output"
        self.source.mkdir()
        self.addCleanup(patch.stopall)
        patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")).start()
        patch.object(socket, "create_connection", side_effect=AssertionError("Network forbidden")).start()

    def prior(self, data, url="https://example.gov.au/source.pdf", **overrides):
        relative, digest = save_object(self.source, data, ".pdf")
        return {"canonical_url": url, "response_url": url, "snapshot_path": relative,
                "sha256": digest, "capture_status": "bytes-preserved", "content_type": "application/pdf",
                "extraction_status": "needs-ocr-or-blank-page-review", "acquisition_method": "https-original-bytes",
                "retrieved_at": "2025-01-01T00:00:00Z", "attempted_at": "2025-01-01T00:00:00Z",
                "references": ["original-reference"], "source_family_ids": ["test-family"],
                "response_headers": {"etag": "original"}, "source_time_version": "historical-unreviewed",
                "legal_review_status": "not-reviewed", "current_law_release": False, **overrides}

    def recover(self, prior):
        return recovery.recover_one(self.source, self.output, prior, pdfium, {"archive_root": str(self.source)})

    def inputs(self, rows, missing=None):
        raw = "".join(json.dumps(row) + "\n" for row in rows).encode()
        manifest = self.source / "source-originals/manifest.jsonl"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_bytes(raw)
        report = {"archive_available": True, "inputs": [{"role": "archive", "path": "source-originals/manifest.jsonl",
                                                         "sha256": hashlib.sha256(raw).hexdigest()}],
                  "urls": [{"canonical_url": row["canonical_url"], "has_research_text": False,
                            "extraction_status": row.get("extraction_status")} for row in (missing or rows)]}
        path = self.source / "review/results/delivery-readiness.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(report), encoding="utf-8")
        return manifest, path

    def test_original_bytes_paths_and_metadata_unchanged_and_merge_compatible(self):
        prior = self.prior(pdf_bytes([TEXT, TEXT]))
        path = self.source / prior["snapshot_path"]
        before = (path.read_bytes(), path.stat().st_mtime_ns)
        original_row = json.dumps(prior, sort_keys=True)
        row = self.recover(prior)
        self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)
        self.assertEqual(json.dumps(prior, sort_keys=True), original_row)
        self.assertEqual(verified_bytes(self.output, row), before[0])
        self.assertEqual(row["snapshot_path"], prior["snapshot_path"])
        for key in ("acquisition_method", "retrieved_at", "attempted_at", "references", "source_family_ids",
                    "response_headers", "response_url", "source_time_version"):
            self.assertEqual(row[key], prior[key])
        self.assertEqual(row["preserved_source_provenance"]["source_record"], prior)
        self.assertTrue(acceptable(row))
        errors = []
        check_artifacts(self.output, row, set(), errors)
        self.assertEqual(errors, [])
        units = json.loads((self.output / row["text_path"]).read_bytes())
        self.assertEqual([unit["locator"] for unit in units], ["page:1", "page:2"])
        self.assertTrue(all(unit["text"].strip() for unit in units))

    def test_hash_mismatch_is_failure_before_pdfium_or_copy(self):
        prior = self.prior(pdf_bytes([TEXT]), sha256="0" * 64)
        with patch.object(pdfium, "PdfDocument", side_effect=AssertionError("Must validate first")):
            row = self.recover(prior)
        self.assertEqual(row["reason_code"], "original-hash-mismatch")
        self.assertFalse(row["original_copied"])
        self.assertFalse(self.output.exists())
        self.assertNotIn("text_path", row)

    def test_input_path_containment(self):
        prior = self.prior(pdf_bytes([TEXT]))
        for bad in ("../escape.pdf", str(self.source / prior["snapshot_path"]),
                    "source-originals/objects/../../../escape.pdf", "C:escape.pdf"):
            with self.subTest(path=bad):
                row = self.recover({**prior, "snapshot_path": bad})
                self.assertEqual(row["reason_code"], "path-containment")
                self.assertFalse(row["original_copied"])

    def test_output_cannot_overlap_archive_or_escape_stage(self):
        for bad in (self.source, self.source / "out", self.source.parent,
                    recovery.OUTPUT_BASE.parent / "not-authorized"):
            with self.subTest(path=bad), self.assertRaises(recovery.RecoveryError):
                recovery.validate_output_root(self.source, bad)

    def test_empty_whitespace_and_punctuation_are_not_text(self):
        for pages in ([""], ["  \t\r\n\x00\u200b"], [". " * 120]):
            with self.subTest(pages=pages):
                prior = self.prior(pdf_bytes([""]))
                with patch.object(pdfium.PdfTextPage, "get_text_range", return_value=pages[0]):
                    row = self.recover(prior)
                self.assertEqual(row["recovery_status"], "failed")
                self.assertEqual(row["substantive_character_count"], 0)
                self.assertEqual(row["pages_without_text"], [1])
                self.assertNotIn("text_path", row)

    def test_threshold_is_across_document_and_excludes_spaces(self):
        for total in (79, 80):
            with self.subTest(total=total):
                texts = ["a " * 40, "b " * (total - 40)]
                with patch.object(pdfium.PdfTextPage, "get_text_range", side_effect=texts):
                    row = self.recover(self.prior(pdf_bytes(["", ""])))
                self.assertEqual(row["substantive_character_count"], total)
                self.assertEqual(row["recovery_status"], "captured" if total == 80 else "failed")
                self.assertEqual(row["pages_attempted"], 2)

    def test_partial_pages_remain_incomplete_and_no_empty_units(self):
        row = self.recover(self.prior(pdf_bytes([TEXT, "", TEXT])))
        self.assertEqual(row["recovery_status"], "captured")
        self.assertEqual(row["extraction_status"], "needs-ocr-or-blank-page-review")
        self.assertEqual(row["extraction_completeness"], "incomplete")
        self.assertEqual(row["pages_without_text"], [2])
        self.assertEqual(row["pages_attempted"], 3)
        self.assertFalse(row["native_text_all_pages_present"])
        units = json.loads((self.output / row["text_path"]).read_bytes())
        self.assertEqual([unit["locator"] for unit in units], ["page:1", "page:3"])

    def test_page_error_does_not_prevent_remaining_pages(self):
        with patch.object(pdfium.PdfTextPage, "get_text_range", side_effect=[TEXT, ValueError("bad page"), TEXT]):
            row = self.recover(self.prior(pdf_bytes(["", "", ""])))
        self.assertTrue(row["all_pages_attempted"])
        self.assertEqual(row["pages_attempted"], 3)
        self.assertEqual(row["page_errors"][0]["locator"], "page:2")
        self.assertEqual(row["recovered_page_count"], 2)
        self.assertEqual(row["extraction_completeness"], "incomplete")

    def test_native_success_never_grants_legal_or_completeness_approval(self):
        prior = self.prior(pdf_bytes([TEXT]), legal_review_status="approved", current_law_release=True,
                           redistribution_status="cleared", extraction_error="old error")
        row = self.recover(prior)
        self.assertEqual(row["legal_review_status"], "not-reviewed")
        self.assertFalse(row["current_law_release"])
        self.assertEqual(row["redistribution_status"], "not-cleared")
        self.assertEqual(row["extraction_completeness"], "completeness-unreviewed")
        self.assertEqual(row["review_status"], recovery.BOUNDARY)
        self.assertNotIn("extraction_error", row)
        self.assertEqual(row["preserved_source_provenance"]["source_record"]["extraction_error"], "old error")
        for key in ("new_download", "network_used", "ocr_used", "password_attempted"):
            self.assertFalse(row["extractor_provenance"][key])

    def test_password_protected_and_unreadable_pdfs_recorded(self):
        writer = PdfWriter()
        writer.append(PdfReader(io.BytesIO(pdf_bytes([TEXT]))))
        writer.encrypt("test-password")
        stream = io.BytesIO()
        writer.write(stream)
        for data, code in ((stream.getvalue(), "encrypted-pdf"), (b"%PDF-1.4\nbroken", "unreadable-pdf")):
            with self.subTest(code=code):
                row = self.recover(self.prior(data))
                self.assertEqual(row["reason_code"], code)
                self.assertEqual(row["recovery_status"], "failed")
                self.assertTrue(row["original_copied"])
                self.assertNotIn("text_path", row)

    def test_rerun_deduplicates_successes_failures_and_objects(self):
        rows = [self.prior(pdf_bytes([TEXT])), self.prior(pdf_bytes([""]), url="https://example.gov.au/blank.pdf")]
        inputs = self.inputs(rows)
        before_source = {str(path): path.read_bytes() for path in self.source.rglob("*") if path.is_file()}
        first = recovery.run(self.source, self.output)
        before_output = {str(path): (path.read_bytes(), path.stat().st_mtime_ns)
                         for path in self.output.rglob("*") if path.is_file()}
        second = recovery.run(self.source, self.output)
        after_output = {str(path): (path.read_bytes(), path.stat().st_mtime_ns)
                        for path in self.output.rglob("*") if path.is_file()}
        self.assertEqual(before_output, after_output)
        self.assertEqual(before_source, {str(path): path.read_bytes() for path in self.source.rglob("*") if path.is_file()})
        self.assertTrue(all(path.exists() for path in inputs))
        self.assertEqual(first["success_rows_appended_this_run"], 1)
        self.assertEqual(first["failure_rows_appended_this_run"], 1)
        self.assertEqual(second["success_rows_appended_this_run"], 0)
        self.assertEqual(second["failure_rows_appended_this_run"], 0)
        successes = read_jsonl(self.output / recovery.SUCCESS_LOG)
        self.assertEqual(len(successes), 1)
        self.assertEqual(successes[0]["recovery_fingerprint"], fingerprint(successes[0]))

    def test_corrupt_existing_output_is_not_overwritten(self):
        prior = self.prior(pdf_bytes([TEXT]))
        row = self.recover(prior)
        path = self.output / row["snapshot_path"]
        path.write_bytes(b"corrupt")
        with self.assertRaises(ValueError):
            self.recover(prior)
        self.assertEqual(path.read_bytes(), b"corrupt")

    def test_missing_only_selection_retains_original_after_failed_retry(self):
        prior = self.prior(pdf_bytes([TEXT]))
        other = self.prior(pdf_bytes([TEXT]), url="https://example.gov.au/already.pdf")
        nonpdf = {**prior, "canonical_url": "https://example.gov.au/data.txt", "content_type": "text/plain"}
        nonpdf["snapshot_path"], nonpdf["sha256"] = save_object(self.source, b"plain data", ".txt")
        retry = {"canonical_url": prior["canonical_url"], "capture_status": "failed"}
        report = {"urls": [{"canonical_url": prior["canonical_url"], "has_research_text": False},
                           {"canonical_url": other["canonical_url"], "has_research_text": True},
                           {"canonical_url": nonpdf["canonical_url"], "has_research_text": False}]}
        targets, excluded = recovery.targets_from_report(self.source, [prior, other, nonpdf, retry], report)
        self.assertEqual(targets, [(1, prior)])
        self.assertEqual(excluded[0]["reason_code"], "preserved-non-pdf")

    def test_stale_readiness_report_rejected_before_writes(self):
        row = self.prior(pdf_bytes([TEXT]))
        manifest, _ = self.inputs([row])
        with manifest.open("ab") as handle:
            handle.write(b"\n")
        with self.assertRaisesRegex(recovery.RecoveryError, "exact source manifest"):
            recovery.run(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_cli_network_guard_rejects_network_events(self):
        for event in ("socket.connect", "socket.getaddrinfo", "socket.sendto"):
            with self.subTest(event=event), self.assertRaisesRegex(RuntimeError, "Network is disabled"):
                recovery.deny_network(event, ())


if __name__ == "__main__":
    unittest.main()
