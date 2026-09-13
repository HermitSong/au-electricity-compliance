"""Synthetic release-gate regressions; these fixtures are not legal approvals."""

import contextlib
import copy
from datetime import date, timedelta
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import double_check_professional_answers as batch_checker
from packet_contract import INPUT_PATHS, seal_packet, validate_packet
from route_applicability import KNOWLEDGE_BASELINE, route_question


class ReleaseBypassRegressionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for relative in INPUT_PATHS.values():
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{}\n", encoding="utf-8")

        self.question = "Can a Victorian retailer manage life-support protection?"
        self.post_baseline = (
            date.fromisoformat(KNOWLEDGE_BASELINE) + timedelta(days=1)
        ).isoformat()
        self.source_family_id = "SYNTHETIC-VIC-REVIEW"
        self.write_json("data/enforcement-source-register.json", {
            "sources": [{"id": self.source_family_id, "jurisdiction": "Victoria"}],
        })
        self.write_json("data/source-coverage-ledger.json", {"source_reviews": []})

        provision_id = "VIC-ERCP-V6-LIFE-SUPPORT-2026-08-29"
        evidence_id = "provision:" + provision_id
        span_id = "source-span:synthetic-release-review"
        official_url = "https://example.invalid/synthetic-victoria-code"
        snapshot_path = "data/synthetic-source.txt"
        snapshot = b"Synthetic source text for release-gate tests only."
        (self.root / snapshot_path).write_bytes(snapshot)
        source_hash = hashlib.sha256(snapshot).hexdigest()
        self.write_json('data/source-text-chunks.jsonl', {
            'chunk_id': span_id.removeprefix('source-span:'), 'canonical_url': official_url,
            'parent_canonical_url': None, 'snapshot_path': snapshot_path,
            'locator': 'synthetic:source', 'text': snapshot.decode('utf-8'),
            'text_sha256': source_hash, 'source_sha256': source_hash,
        })
        artifact = {
            "artifact_id": "synthetic-release-artifact",
            "snapshot_status": "captured-immutable-copy",
            "snapshot_path": snapshot_path,
            "source_sha256": source_hash,
            "retrieved_at": KNOWLEDGE_BASELINE + "T00:00:00Z",
            "provenance_status": "synthetic-test-fixture",
            "provenance_limitations": "Not a real source or review receipt.",
        }
        self.write_json("data/source-artifact-ledger.jsonl", {
            **artifact,
            "record_type": "local-official-snapshot",
            "canonical_url": official_url,
            "sha256": source_hash,
        })
        binding = {
            "provision_id": provision_id,
            "authority_status": "current-at-baseline",
            "official_url": official_url,
            "supports_current_law_drafting": True,
            "supports_operational_execution": False,
            "source_span_ids": [span_id],
            "source_sha256_values": [source_hash],
        }
        self.write_json("data/provision-source-bindings.json", {"bindings": [binding]})
        self.write_json("data/provision-version-register.json", {
            "baseline_date": KNOWLEDGE_BASELINE,
            "provisions": [{
                "provision_id": provision_id,
                "official_url": official_url,
                "status": "current-at-baseline",
                "jurisdiction": "Victoria",
            }],
        })
        provision = {
            "evidence_id": evidence_id,
            "doc_type": "provision-version",
            "status": "current-at-baseline",
            "official_url": official_url,
            "related_official_url": None,
            "sha256": source_hash,
            "temporal_classification": "current-rule",
            "coverage_status": "",
            "issue_family": "life-support",
            "source_artifact": artifact,
            "provision_source_binding": binding,
            "temporal_link_candidate_only": False,
        }
        span = {
            "evidence_id": span_id,
            "doc_type": "official-source-span",
            "status": "captured-official-source-text",
            "official_url": official_url,
            "related_official_url": None,
            "sha256": source_hash,
            "temporal_classification": "official-source-snapshot",
            "coverage_status": "",
            "issue_family": "life-support",
            "source_artifact": artifact,
            'source_path': snapshot_path,
            'source_locator': 'synthetic:source',
            'text': snapshot.decode('utf-8'),
            'source_text_sha256': source_hash,
            'source_snapshot_sha256': source_hash,
        }
        self.evidence = [provision, span]
        self.packet = self.make_packet()
        self.draft = {
            "question": self.question,
            "answer_as_of": KNOWLEDGE_BASELINE,
            "claims": [{
                "claim_id": "SYNTHETIC-C1",
                "claim_type": "current-law",
                "text": "Current synthetic test obligation.",
                "evidence_ids": [evidence_id, span_id],
            }],
        }

    def write_json(self, relative, value):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def make_packet(self, question=None, as_of=KNOWLEDGE_BASELINE):
        question = question or self.question
        context = {
            "jurisdiction": "Victoria",
            "actor": "retailer",
            "activity": "life-support protection",
            "as_of": as_of,
        }
        packet = {
            "id": "SYNTHETIC-ANSWER",
            "question": question,
            "answer_as_of": as_of,
            "knowledge_baseline": KNOWLEDGE_BASELINE,
            "jurisdiction": context["jurisdiction"],
            "actor": context["actor"],
            "activity": context["activity"],
            "routing_inputs": context,
            "applicability": route_question(question, **context),
            "requires_complete_public_sources": False,
            "release_state": "ready-for-grounded-drafting",
            "coverage_warnings": [],
            "evidence": copy.deepcopy(self.evidence),
        }
        return seal_packet(packet, self.root)

    def test_batch_forwards_answer_date_to_shared_checker(self):
        answer = {**self.draft, "id": self.packet["id"], "answer_as_of": self.post_baseline}
        date_error = "Draft answer date differs from the packet answer date."
        shared_report = {
            "passed": False,
            "errors": [date_error],
            "claim_reports": [{
                "claim_id": "SYNTHETIC-C1",
                "passed": False,
                "errors": [date_error],
                "warnings": [],
            }],
        }
        with (
            patch.object(sys, "argv", ["batch-checker", "--root", str(self.root)]),
            patch.object(batch_checker, "read_jsonl", side_effect=[[answer], [self.packet]]),
            patch.object(batch_checker.sqlite3, "connect") as connect,
            patch.object(batch_checker, "check_draft", return_value=shared_report) as check,
            patch.object(batch_checker, "double_search", return_value=("synthetic query", self.evidence, [])),
            patch.object(batch_checker, "write_jsonl") as write_report,
            patch.object(Path, "write_text", return_value=0),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            connect.return_value.execute.return_value = self.evidence
            exit_code = batch_checker.main()

        check.assert_called_once()
        forwarded = check.call_args.args[1]
        self.assertEqual(forwarded.get("answer_as_of"), self.post_baseline)
        self.assertNotEqual(forwarded["answer_as_of"], self.packet["answer_as_of"])
        self.assertEqual(forwarded["claims"], answer["claims"])
        self.assertEqual(exit_code, 1)
        reports = write_report.call_args.args[1]
        self.assertEqual(len(reports), 1)
        self.assertFalse(reports[0]["passed"])

    def test_historical_question_current_law_claim_requires_live_version(self):
        self.assertEqual(validate_packet(self.packet, self.root, self.draft), [])
        question = "Describe the historical life-support case involving a Victorian retailer."
        packet = self.make_packet(question, self.post_baseline)
        draft = {**self.draft, "question": question, "answer_as_of": self.post_baseline}
        self.assertEqual(packet["applicability"]["temporal_intent"], "historical-or-descriptive")
        self.assertFalse(packet["applicability"]["requires_live_version_check"])
        errors = validate_packet(packet, self.root, draft)
        self.assertTrue(
            any("live version" in error.lower().replace("-", " ") for error in errors),
            errors,
        )

    def test_require_complete_public_sources_survives_rehash_with_canonical_gap(self):
        self.assertEqual(validate_packet(self.packet, self.root, self.draft), [])
        gap = {
            "source_family_id": self.source_family_id,
            "extraction_status": "archive-gap",
            "gap_periods": ["2024"],
            "gap_reason": "Synthetic missing archive period.",
        }
        self.write_json("data/source-coverage-ledger.json", {"source_reviews": [gap]})
        packet = copy.deepcopy(self.packet)
        packet.update(
            requires_complete_public_sources=True,
            release_state="coverage-gap",
            coverage_warnings=[gap],
        )
        seal_packet(packet, self.root)
        self.assertTrue(validate_packet(packet, self.root, self.draft))

        # Removing the packet warning must not hide the pinned canonical gap.
        packet.update(release_state="ready-for-grounded-drafting", coverage_warnings=[])
        seal_packet(packet, self.root)
        errors = validate_packet(packet, self.root, self.draft)
        self.assertTrue(any("coverage" in error.lower() for error in errors), errors)

    def test_rehashed_top_level_context_must_match_routing_inputs(self):
        self.assertEqual(validate_packet(self.packet, self.root, self.draft), [])
        for field, value in (
            ("actor", "customer"),
            ("activity", "billing and payment"),
            ("jurisdiction", "New South Wales"),
        ):
            with self.subTest(field=field):
                packet = copy.deepcopy(self.packet)
                packet[field] = value
                seal_packet(packet, self.root)
                self.assertEqual(packet["routing_inputs"], self.packet["routing_inputs"])
                self.assertEqual(packet["applicability"], self.packet["applicability"])
                errors = validate_packet(packet, self.root, self.draft)
                self.assertTrue(errors, f"Contradictory {field} was accepted after rehashing.")
                self.assertTrue(
                    any(field in error.lower() or "context" in error.lower() for error in errors),
                    errors,
                )


if __name__ == "__main__":
    unittest.main()
