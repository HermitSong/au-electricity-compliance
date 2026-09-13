import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import run_gap_ocr_batch as batch
from validate_source_originals import check_artifacts
from merge_evidence_batch import prepare as prepare_merge


def source(name="electricity-wholesale-licence.pdf", pages=2, host="www.esc.vic.gov.au"):
    return {"canonical_url": "https://" + host + "/" + name, "sha256": "a" * 64,
            "page_count": pages, "has_research_text": False, "capture_status": "bytes-preserved",
            "extraction_status": "needs-ocr-or-blank-page-review", "source_family_ids": ["VIC-ESC-PENALTIES"]}


class GapOcrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root_patch = patch.object(batch, "ROOT", Path(cls.temporary.name) / "batch")
        cls.root_patch.start()
        (batch.ROOT / "tmp").mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        cls.root_patch.stop()
        cls.temporary.cleanup()

    def test_current_cohort_and_recovered_exclusion_preserve_metadata(self):
        row = source()
        row["references"] = ["attachment:prior"]
        chosen, excluded = batch.select([row], [row["canonical_url"]])
        self.assertEqual(chosen, [])
        self.assertEqual(excluded[0]["source_record"]["references"], row["references"])
        row["has_research_text"] = True
        self.assertEqual(batch.select([row])[0], [])

    def test_scope_and_procedure_not_mistaken_for_submission(self):
        for row in (source("VCN-CPS-1.pdf"), source("Gas Retail Licence.pdf"),
                    source("warning.pdf", host="www.acma.gov.au")):
            self.assertIsNone(batch.priority(row)[0])
        self.assertEqual(batch.priority(source("Practice-note-utility.pdf", host="www.acat.act.gov.au"))[0], 0)

    def test_caps_and_shortest_priority(self):
        chosen, excluded = batch.select([source("electricity-licence-long.pdf", 5), source("electricity-licence-short.pdf", 1)], max_pages=4)
        self.assertEqual([r["page_count"] for r in chosen], [1])
        self.assertEqual(excluded[0]["reason"], "document-or-page-budget")
        for docs, pages in ((41, 240), (40, 241), (0, 1)):
            with self.assertRaises(ValueError):
                batch.select([], max_docs=docs, max_pages=pages)
        with self.assertRaises(ValueError):
            batch.run_batch(1201)

    def test_installed_runner_rejects_canonical_output_root(self):
        with patch.object(batch, "ROOT", batch.SOURCE / "ocr-gap-recovery"):
            with self.assertRaisesRegex(ValueError, "disjoint"):
                batch.guard_writes()

    def test_closed_batch_cannot_start_another_worker(self):
        with tempfile.TemporaryDirectory(dir=batch.ROOT / "tmp") as directory, patch.object(batch, "ROOT", Path(directory)):
            batch.dump("selection.json", {"selected_documents": 1, "selected_pages": 1})
            batch.dump("execution.json", {"closed": True, "phases": []})
            with self.assertRaisesRegex(ValueError, "finalized"):
                batch.run_batch(1)
            with self.assertRaisesRegex(ValueError, "reservation"):
                batch.run_worker()

    def test_checkpoint_retries_transient_windows_sharing_failure(self):
        with tempfile.TemporaryDirectory(dir=batch.ROOT / "tmp") as directory, patch.object(batch, "ROOT", Path(directory)):
            replace = batch.os.replace
            calls = []
            def transient(source, destination):
                calls.append(1)
                if len(calls) == 1:
                    raise PermissionError("sharing violation")
                replace(source, destination)
            with patch.object(batch.os, "replace", side_effect=transient):
                batch.dump("checkpoint.json", {"status": "completed"})
            self.assertEqual(json.loads((batch.ROOT / "checkpoint.json").read_bytes())["status"], "completed")
            self.assertEqual(len(calls), 2)

    def test_numeric_and_negation_disagreement(self):
        comparison = batch.comparison("must not pay $120 by 1/2/2024", "must pay $720 by 1/2/2024")
        self.assertTrue(comparison["critical_token_disagreement"])
        self.assertEqual(comparison["modal_counts_only_in_first"], {"not": 1})
        self.assertIn("$120", comparison["tokens_only_in_first"])

    def test_dual_outputs_nested_refs_and_partial_state(self):
        with tempfile.TemporaryDirectory(dir=batch.ROOT / "tmp") as directory, patch.object(batch, "ROOT", Path(directory)):
            original, digest = batch.save_object(batch.ROOT, b"%PDF-example", ".pdf")
            image, image_hash = batch.save_object(batch.ROOT, b"image-fixture", ".png")
            first, first_hash = batch.object_json([{"locator": "page:1", "text": "must not " + "electricity licence " * 15}])
            second, second_hash = batch.object_json([{"locator": "page:1", "text": "must " + "electricity licence " * 15}])
            target = {"id": "doc-001", "prior": source(pages=1), "page_count": 1,
                      "snapshot_path": original, "sha256": digest, "selection_reason": "test"}
            page = {"page": 1, "locator": "page:1", "render_status": "completed", "first_status": "completed", "second_status": "completed",
                    "image_path": image, "image_sha256": image_hash, "first_text_path": first, "first_text_sha256": first_hash,
                    "second_text_path": second, "second_text_sha256": second_hash}
            result, _, _ = batch.assemble(target, {"pages": [page]})
            checked, errors = set(), []
            check_artifacts(batch.ROOT, result, checked, errors)
            self.assertEqual(errors, [])
            self.assertTrue({(first, first_hash), (second, second_hash), (image, image_hash)} <= checked)
            self.assertIn((result["second_engine_text_path"], result["second_engine_text_sha256"]), checked)
            self.assertEqual(result["recovery_status"], "captured")
            (batch.ROOT / batch.FINAL_LOG).write_text(json.dumps(result) + "\n", encoding="utf-8")
            bad_earlier = {**result, "text_sha256": "0" * 64}
            (batch.ROOT / "source-originals/recovery-ocr.jsonl").write_text(json.dumps(bad_earlier) + "\n", encoding="utf-8")
            _, pending, _, objects = prepare_merge(batch.ROOT / "destination", [batch.ROOT], [])
            self.assertEqual(len(pending), 1)
            self.assertEqual(pending[0]["ocr_comparison_sha256"], result["ocr_comparison_sha256"])
            self.assertTrue({first, second, image} <= set(objects))
            (batch.ROOT / image).write_bytes(b"corrupt-fixture")
            with self.assertRaisesRegex(ValueError, "corrupt"):
                prepare_merge(batch.ROOT / "destination", [batch.ROOT], [])
            page.update(second_status="running")
            page.pop("second_text_path")
            page.pop("second_text_sha256")
            result, pages, comparisons = batch.assemble(target, {"pages": [page]})
            self.assertEqual(result["recovery_status"], "partial")
            self.assertEqual(result["pages_without_dual_ocr"], [1])
            self.assertEqual(pages[0]["second_status"], "interrupted")
            self.assertFalse(comparisons[0]["critical_token_disagreement"])
            self.assertFalse(result["handoff_eligible"])

    def test_blank_page_keeps_partial_state_without_discarding_recovered_document(self):
        with tempfile.TemporaryDirectory(dir=batch.ROOT / "tmp") as directory, patch.object(batch, "ROOT", Path(directory)):
            path, digest = batch.object_json([{"locator": "page:1", "text": "electricity licence " * 20}])
            page = {"page": 1, "locator": "page:1", "render_status": "completed", "first_status": "completed", "second_status": "completed",
                    "first_text_path": path, "first_text_sha256": digest, "second_text_path": path, "second_text_sha256": digest}
            blank = {"page": 2, "locator": "page:2", "render_status": "completed", "first_status": "completed", "second_status": "completed"}
            result, _, _ = batch.assemble({"id": "doc-001", "prior": source(), "page_count": 2, "selection_reason": "test"}, {"pages": [page, blank]})
            self.assertEqual(result["recovery_status"], "partial")
            self.assertTrue(result["handoff_eligible"])
            self.assertEqual(result["pages_without_text"], [2])
            self.assertEqual(result["pages_without_dual_ocr"], [])

    def test_one_corrupt_document_does_not_discard_successful_handoff(self):
        with tempfile.TemporaryDirectory(dir=batch.ROOT / "tmp") as directory:
            parent = Path(directory)
            with patch.multiple(batch, ROOT=parent / "batch", SOURCE=parent / "canonical", REPORT=parent / "report.json"), patch.object(batch, "source_inventory", return_value={}):
                targets = []
                for index in (1, 2):
                    raw = b"%PDF-fixture-" + str(index).encode()
                    original, digest = batch.save_object(batch.SOURCE, raw, ".pdf")
                    batch.save_object(batch.ROOT, raw, ".pdf")
                    text_path, text_hash = batch.object_json([{"locator": "page:1", "text": "electricity licence " * 20}])
                    prior = {**source(name=f"electricity-licence-{index}.pdf", pages=1), "snapshot_path": original, "sha256": digest}
                    target = {"id": f"doc-{index:03}", "prior": prior, "canonical_url": prior["canonical_url"],
                              "page_count": 1, "snapshot_path": original, "sha256": digest, "selection_reason": "test"}
                    targets.append(target)
                    batch.dump("documents/" + target["id"] + ".json", {"status": "completed", "pages": [{
                        "page": 1, "locator": "page:1", "render_status": "completed", "first_status": "completed", "second_status": "completed",
                        "first_text_path": text_path, "first_text_sha256": text_hash, "second_text_path": text_path, "second_text_sha256": text_hash}]})
                (batch.ROOT / targets[1]["snapshot_path"]).write_bytes(b"damaged-stage-copy")
                batch.dump("selection.json", {"targets": targets, "canonical_control_hashes": {}, "input_missing_urls": 2, "excluded": []})
                batch.dump("canonical-before.json", {})
                result = batch.quality_report()
                self.assertEqual(result["counts"]["recovered_documents"], 1)
                self.assertEqual(result["counts"]["invalid_documents_excluded_from_handoff"], 1)
                self.assertEqual(batch.read_jsonl(batch.ROOT / batch.FINAL_LOG)[0]["id"], "doc-001")


if __name__ == "__main__":
    unittest.main()
