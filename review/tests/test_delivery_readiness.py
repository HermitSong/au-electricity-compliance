"""Focused audit regressions. All fixture writes stay in delivery review/results."""

from contextlib import redirect_stderr, redirect_stdout
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_delivery_readiness import audit, canonical_url, family_scope, main, select_manifest


# URLs and family names already present in the delivery; contents below are test fixtures.
URL = "https://www.aer.gov.au/publications/reports/compliance"
OTHER = "https://www.aer.gov.au/news/articles/news-releases/20000-penalty-imposed-agl-hydro"
OLD = "https://www.esc.vic.gov.au/node/3052"
NEW = "https://www.esc.vic.gov.au/register"
FAMILY = "AU-AER-COMPLIANCE"
SECOND = "AU-ACCC-ENFORCEMENT"


class DeliveryReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="delivery-test-", dir=ROOT / "review" / "results")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "archive"
        self.inventory = [{"canonical_url": URL, "source_family_ids": [FAMILY],
                           "has_research_text": True, "latest_extraction_status": "extracted-unreviewed"}]
        self.families = [{"id": FAMILY, "url": URL}]
        self.reviews = [{"source_family_id": FAMILY, "source_url": URL,
                         "public_date_scope": "2006-01-01 to 2026-08-29", "checked_at": "2026-08-29",
                         "pages_or_years_checked": "Fixture public index", "gap_periods": [],
                         "extraction_status": "complete-case-indexed", "public_record_count": 1}]
        self.events = [{"event_id": "fixture-event", "status": "final", "source_family_id": FAMILY,
                        "official_source_url": URL, "outcome": "Fixture final outcome."}]
        self.links = [{"event_id": "fixture-event", "historical_status": "final",
                       "current_comparator_ids": ["fixture-provision"], "review_status": "candidate-auto-mapped",
                       "reviewed_by": None, "reviewed_at": None, "review_evidence_ids": []}]
        self.aliases = []
        self.resolutions = []
        self.manifest = [self.capture(URL)]

    def write(self, relative, value, root=None, jsonl=False):
        path = (root or self.root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if jsonl:
            content = "".join(json.dumps(row) + "\n" for row in value)
        elif isinstance(value, str):
            content = value
        else:
            content = json.dumps(value)
        path.write_text(content, encoding="ascii")
        return path

    def capture(self, url, text="Fixture source text.", status="extracted-unreviewed", **fields):
        units = [{"locator": "page:1", "text": text}]
        raw = json.dumps(units).encode("ascii")
        digest = hashlib.sha256(raw).hexdigest()
        path = f"source-originals/objects/{digest}.json"
        self.write(path, raw.decode("ascii"), self.archive)
        return {"canonical_url": url, "text_path": path, "text_sha256": digest,
                "extraction_status": status, "capture_status": "bytes-preserved",
                "legal_review_status": "not-reviewed", "current_law_release": False, **fields}

    def save(self):
        self.write("README.md", "Fixture research-only delivery.\n")
        self.write("ORIGINAL-SOURCE-SCOPE.md", "Fixture scope: source universe is unknown.\n")
        self.write("data/enforcement-source-register.json", {"sources": self.families})
        self.write("data/source-coverage-ledger.json", {"source_family_count": len(self.reviews),
                                                       "source_reviews": self.reviews})
        self.write("data/source-original-inventory.jsonl", self.inventory, jsonl=True)
        self.write("data/source-original-summary.json", {"inventory_url_count": len(self.inventory),
                                                         "research_text_url_count": len(self.inventory)})
        self.write("source-originals/manifest.jsonl", self.manifest, self.archive, jsonl=True)
        self.write("data/enforcement-events-full.jsonl", self.events, jsonl=True)
        self.write("data/technical-events-full.jsonl", [], jsonl=True)
        self.write("data/event-provision-links.jsonl", self.links, jsonl=True)
        self.write("data/provision-version-register.json", {"provisions": [{"provision_id": "fixture-provision", "official_url": URL}]})
        self.write("data/provision-source-bindings.json", {"bindings": []})
        self.write("data/selected-source-aliases.json", {"aliases": self.aliases})
        self.write("data/source-recovery-resolution.jsonl", self.resolutions, jsonl=True)

    def run_audit(self, archive=True):
        self.save()
        return audit(self.root, self.archive if archive else None)

    def test_unique_global_urls_allow_cross_family_membership(self):
        self.families.append({"id": SECOND, "url": URL})
        self.reviews.append({**self.reviews[0], "source_family_id": SECOND})
        self.inventory[0]["source_family_ids"].append(SECOND)
        self.inventory.append(copy.deepcopy(self.inventory[0]))
        report = self.run_audit()
        self.assertEqual(report["counts"]["known_url_count"], 1)
        self.assertEqual(report["counts"]["text_url_count"], 1)
        self.assertEqual(report["counts"]["family_membership_url_count"], 2)
        self.assertEqual(report["counts"]["cross_family_url_count"], 1)
        self.assertTrue(all(row["known_url_count"] == row["text_url_count"] == 1 for row in report["families"]))
        self.assertTrue(all(row["task_counts"]["enumerate-full-source-family"] == 1 for row in report["families"]))
        self.assertTrue(all(row["task_counts"]["review-extraction-completeness"] == 1 for row in report["families"]))

    def test_explicit_register_urls_and_unassigned_urls_are_not_lost(self):
        self.families[0]["url"] = OTHER
        self.inventory.append({"canonical_url": NEW, "source_family_ids": [], "has_research_text": False})
        report = self.run_audit()
        self.assertEqual(report["counts"]["known_url_count"], 3)
        self.assertEqual(report["counts"]["missing_text_url_count"], 2)
        self.assertEqual(report["counts"]["unassigned_family_url_count"], 1)
        self.assertEqual(report["families"][0]["known_url_count"], 2)
        self.assertTrue(any(row["task"] == "review-source-family-membership" and row["subject"] == NEW for row in report["tasks"]))

    def test_unknown_and_aggregate_zero_are_not_verified_zero(self):
        row = {**self.reviews[0], "public_record_count": 0}
        for status in ("unknown", "archive-gap", "aggregate-only"):
            with self.subTest(status=status):
                result = family_scope({**row, "extraction_status": status}, 0)
                self.assertNotEqual(result["zero_record_interpretation"], "verified-zero-in-ledger-scope")
                self.assertEqual(result["full_source_family_enumeration"], "unknown")
        self.assertEqual(family_scope(row, 0)["zero_record_interpretation"], "verified-zero-in-ledger-scope")

    def test_verified_zero_requires_scope_evidence_no_gaps_and_no_events(self):
        row = {**self.reviews[0], "public_record_count": 0}
        for changes in ({"checked_at": None}, {"gap_periods": ["Unenumerated archive"]}, {"public_record_count": False}):
            self.assertNotEqual(family_scope({**row, **changes}, 0)["zero_record_interpretation"], "verified-zero-in-ledger-scope")
        self.assertNotEqual(family_scope(row, 1)["zero_record_interpretation"], "verified-zero-in-ledger-scope")

    def test_complete_known_queue_cannot_promote_universe_legal_or_release(self):
        report = self.run_audit()
        self.assertEqual(report["gates"]["known_url_text_coverage"]["status"], "complete-known-queue")
        self.assertEqual(report["gates"]["full_source_family_enumeration"]["status"], "unknown")
        for gate in ("extraction_completeness", "legal_verification", "operational_release"):
            self.assertEqual(report["gates"][gate]["status"], "not-established")
        self.assertFalse(report["delivery_ready"])
        self.assertEqual(report["delivery_ready"], not report["blocking_gates"])

    def test_partial_text_and_ocr_are_counted_separately(self):
        self.manifest = [self.capture(URL, page_count=3, pages_without_text=[2], status="needs-ocr-or-blank-page-review")]
        report = self.run_audit()
        self.assertEqual(report["counts"]["text_url_count"], 1)
        self.assertEqual(report["counts"]["missing_text_url_count"], 0)
        self.assertEqual(report["counts"]["needs_ocr_url_count"], 1)
        self.assertEqual(report["urls"][0]["pages_without_text"], [2, 3])
        self.assertIn("ocr-or-blank-page-review", report["task_counts"])

    def test_ocr_extracted_still_needs_visual_review(self):
        self.manifest = [self.capture(URL, status="ocr-extracted-unreviewed", page_count=1)]
        report = self.run_audit()
        self.assertEqual(report["counts"]["needs_ocr_url_count"], 1)
        self.assertNotEqual(report["gates"]["extraction_completeness"]["status"], "complete")

    def test_missing_archive_uses_labelled_inventory_claims(self):
        report = self.run_audit(archive=False)
        self.assertEqual(report["counts"]["text_url_count"], 1)
        self.assertEqual(report["counts"]["archive_verified_text_url_count"], 0)
        self.assertEqual(report["urls"][0]["text_evidence_basis"], "inventory-claim-only")
        self.assertIn("input_evidence", report["blocking_gates"])

    def test_corrupt_or_escaping_text_is_not_coverage(self):
        self.manifest[0]["text_sha256"] = "0" * 64
        report = self.run_audit()
        self.assertEqual(report["counts"]["text_url_count"], 0)
        self.assertIn("unusable-text-object", [row["code"] for row in report["input_defects"]])
        self.manifest[0]["text_path"] = "../outside.json"
        self.assertEqual(self.run_audit()["counts"]["text_url_count"], 0)

    def test_retry_preserves_text_until_explicit_invalidation(self):
        self.manifest.append({"canonical_url": URL, "capture_status": "failed"})
        self.assertEqual(self.run_audit()["counts"]["text_url_count"], 1)
        self.manifest[-1]["invalidates_prior_text"] = True
        self.assertEqual(self.run_audit()["counts"]["text_url_count"], 0)

    def test_error_pages_are_not_text(self):
        self.manifest[0]["extraction_status"] = "blocked-or-error-page"
        self.assertEqual(self.run_audit()["counts"]["text_url_count"], 0)

    def test_fragments_alias_but_query_versions_do_not(self):
        self.assertEqual(canonical_url(URL.upper().replace("/PUBLICATIONS/REPORTS/COMPLIANCE", "/publications/reports/compliance") + "#part"), URL)
        self.assertNotEqual(canonical_url(URL + "?version=1"), canonical_url(URL + "?version=2"))
        self.inventory[0]["canonical_url"] += "#part"
        report = self.run_audit()
        self.assertEqual(report["counts"]["known_url_count"], 1)
        self.assertEqual(report["counts"]["text_url_count"], 1)

    def test_event_alias_does_not_transfer_source_text_or_duplicate_events(self):
        self.aliases = [{"alias_url": OTHER, "canonical_event_ids": ["fixture-event"]}]
        report = self.run_audit()
        self.assertEqual(report["counts"]["event_count"], 1)
        self.assertEqual(report["counts"]["known_url_count"], 2)
        self.assertEqual(report["counts"]["missing_text_url_count"], 1)
        self.assertEqual(report["families"][0]["known_url_count"], 2)

    def test_replacement_same_event_does_not_close_original_gap(self):
        self.inventory.append({"canonical_url": OLD, "source_family_ids": [FAMILY], "has_research_text": False})
        relation = {"kind": "public-register-counterpart", "event_identity_verified": True, "historical_identity_verified": False}
        self.resolutions = [{"canonical_url": OLD, "response_url": NEW, "status": "alternative-official-source-only", "source_relation": relation}]
        self.manifest.append(self.capture(NEW, recovery_for_url=OLD, response_url=NEW, source_relation=relation))
        report = self.run_audit()
        rows = {row["canonical_url"]: row for row in report["urls"]}
        self.assertFalse(rows[OLD]["has_research_text"])
        self.assertTrue(rows[NEW]["has_research_text"])
        self.assertFalse(report["replacement_sources"][0]["closes_original_gap"])
        self.assertEqual(rows[NEW]["source_family_ids"], [])

    def test_misfiled_alternative_not_original_but_relocation_is_preserved(self):
        row = self.capture(OLD, response_url=NEW, source_relation={"kind": "current-policy-successor"})
        self.assertNotIn(OLD, select_manifest([row])[1])
        row["source_relation"] = {"kind": "official-relocated-document", "evidence": "Fixture same-report identity evidence."}
        self.assertIn(OLD, select_manifest([row])[1])

    def test_candidate_links_remain_unreviewed_even_with_reviewer_fields(self):
        self.links[0].update(reviewed_by="fixture-reviewer", reviewed_at="2026-08-29", review_evidence_ids=["fixture-evidence"])
        report = self.run_audit()
        self.assertEqual(report["counts"]["reviewed_association_count"], 0)
        self.assertIn("case_provision_association_review", report["blocking_gates"])
        self.assertIn("review-case-provision-association", report["task_counts"])

    def test_approval_label_without_review_evidence_is_incomplete(self):
        self.links[0]["review_status"] = "independently-approved"
        self.assertEqual(self.run_audit()["counts"]["reviewed_association_count"], 0)

    def test_missing_duplicate_and_orphan_links_block_association_review(self):
        for links in ([], [self.links[0], self.links[0]], [{**self.links[0], "event_id": "absent-fixture-event"}]):
            with self.subTest(links=len(links)):
                self.links = links
                report = self.run_audit()
                self.assertEqual(report["counts"]["reviewed_association_count"], 0)
                self.assertEqual(report["gates"]["case_provision_association_review"]["status"], "not-established")

    def test_status_conflicts_are_candidates_without_reclassification(self):
        self.events[0]["case_status_note"] = "Fixture decision stayed pending review; later disposition requires checking."
        self.links[0]["historical_status"] = "proceedings-pending"
        self.manifest = [self.capture(URL, text="Fixture appeal pending; this may be historical.")]
        before = copy.deepcopy(self.events)
        report = self.run_audit()
        codes = {row["code"] for row in report["review_candidates"]}
        self.assertIn("event-link-status-mismatch", codes)
        self.assertIn("final-status-pending-or-stay-language", codes)
        self.assertIn("final-status-source-pending-or-stay-language", codes)
        self.assertEqual(self.events, before)
        self.assertTrue(all(row["disposition"] == "review-candidate" and not row["automatic_legal_reclassification"] for row in report["review_candidates"]))

    def test_right_to_appeal_alone_is_not_pending_language(self):
        self.events[0]["case_status_note"] = "Fixture source states a right to appeal; no appeal outcome published."
        self.assertEqual(self.run_audit()["review_candidates"], [])

    def test_bad_json_input_reports_defect_and_stays_not_ready(self):
        self.save()
        self.write("data/event-provision-links.jsonl", "{invalid}\n")
        report = audit(self.root, self.archive)
        self.assertFalse(report["delivery_ready"])
        self.assertIn("invalid-jsonl-record", [row["code"] for row in report["input_defects"]])

    def test_deterministic_reports_and_read_only_inputs(self):
        self.save()
        before = {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in self.root.rglob("*") if path.is_file()}
        first = audit(self.root, self.archive)
        self.assertEqual(first, audit(self.root, self.archive))
        after = {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_cli_report_success_require_ready_failure_and_ascii_outputs(self):
        self.save()
        output = self.root / "review" / "results" / "delivery-cli"
        args = ["--root", str(self.root), "--output-dir", str(output)]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(args), 0)
            first = (output / "delivery-readiness.json").read_bytes()
            self.assertEqual(main(args + ["--require-ready"]), 1)
        self.assertEqual(first, (output / "delivery-readiness.json").read_bytes())
        self.assertEqual(len(list(output.iterdir())), 4)
        for path in output.iterdir():
            path.read_bytes().decode("ascii")

    def test_cli_rejects_output_outside_results(self):
        self.save()
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as failure:
            main(["--root", str(self.root), "--output-dir", str(self.archive)])
        self.assertEqual(failure.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
