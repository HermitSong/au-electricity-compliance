import copy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from collect_source_originals import rebuild_outputs, save_object
from search_source_originals import (
    MAX_CANDIDATES, MAX_EXCERPT_CHARS, MAX_TOKENS, MAX_QUERY_ANCHORS, REVIEW_STATUS,
    _query_anchors, search_research_originals, validate_research_results,
)


class ResearchOriginalSearchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.rows = []
        self.add_source()
        self.rebuild()

    def add_source(self, url="https://www.aer.gov.au/billing", units=None, **overrides):
        units = units or [{"locator": "page:1", "text": "Retailer billing obligations. Exact source text.\nSecond line."}]
        source_path, source_hash = save_object(self.root, ("Preserved bytes: " + url).encode(), ".bin")
        text_path, text_hash = save_object(self.root, json.dumps(units).encode(), ".json")
        row = {
            "canonical_url": url, "references": [], "source_family_ids": [],
            "discovery_depth": 0, "discovered_from": [], "title": "Billing source",
            "capture_status": "bytes-preserved", "snapshot_path": source_path,
            "sha256": source_hash, "text_path": text_path, "text_sha256": text_hash,
            "extraction_status": "extracted-unreviewed", "legal_review_status": "not-reviewed",
            "current_law_release": False, "retrieved_at": "2026-09-05T00:00:00Z",
            "page_count": 2, "pages_without_text": [2], **overrides,
        }
        self.rows.append(row)
        return row

    def write_manifest(self):
        (self.root / "source-originals/manifest.jsonl").write_text(
            "".join(json.dumps(row) + "\n" for row in self.rows), encoding="utf-8")

    def rebuild(self):
        self.write_manifest()
        rebuild_outputs(self.root, {row["canonical_url"]: row for row in self.rows}, len(self.rows), "test")

    def sql(self, statement, values=()):
        with closing(sqlite3.connect(self.root / "source-originals/search.sqlite3")) as connection, connection:
            connection.execute(statement, values)

    def search(self, query="retailer billing", limit=6):
        return search_research_originals(self.root, query, limit)

    def assert_integrity_error(self, response):
        self.assertEqual(response["status"], "integrity-error", response)
        self.assertTrue(response["validation_errors"])
        self.assertTrue(response["warnings"])

    def test_clean_exact_canonical_excerpt_and_stable_identity(self):
        response = self.search()
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response['sql_budget_seconds'], 15.0)
        self.assertEqual(len(response["results"]), 1)
        hit = response["results"][0]
        unit = json.loads((self.root / hit["text_path"]).read_bytes())[0]
        self.assertEqual(hit["excerpt"], unit["text"])
        self.assertTrue(hit["research_id"].startswith("original:"))
        self.assertEqual(hit["review_status"], REVIEW_STATUS)
        self.assertEqual(hit["pages_without_text"], [2])
        self.assertEqual(validate_research_results(self.root, response["results"]), [])
        self.assertEqual(response, self.search())
        self.assertNotIn("evidence", response)
        self.assertIn("not exhaustive", response["use_limit"])

    def test_preserved_archive_search_works_without_acquisition_packages(self):
        script = ('import sys,json; from pathlib import Path; sys.path.insert(0, sys.argv[1]); '
                  'from search_source_originals import search_research_originals; '
                  'print(json.dumps(search_research_originals(Path(sys.argv[2]), "retailer billing")))')
        scripts = Path(__file__).resolve().parents[2] / 'scripts'
        completed = subprocess.run([sys.executable, '-B', '-S', '-c', script, str(scripts), str(self.root)],
                                   capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)['status'], 'ok')

    def test_long_excerpt_is_an_exact_substring_near_match(self):
        text = "Introduction. " * 300 + "Retailer billing obligations. " + "Context. " * 300
        self.add_source(units=[{"locator": "html:main", "text": text}])
        self.rebuild()
        hit = self.search()["results"][0]
        self.assertIn(hit["excerpt"], text)
        self.assertIn("Retailer billing", hit["excerpt"])
        self.assertEqual(len(hit["excerpt"]), MAX_EXCERPT_CHARS)
        self.assertEqual(validate_research_results(self.root, [hit]), [])

    def test_late_business_issue_survives_a_long_question_setup(self):
        query = ('Our operations team is preparing a cross functional customer risk review '
                 'after several process changes involving multiple vendors and regional departments. '
                 'Locate retailer billing obligations.')
        response = self.search(query)
        self.assertEqual(response['status'], 'ok')
        self.assertIn('"billing"', response['queries_used'][0])
        self.assertEqual(response['results'][0]['url'], self.rows[0]['canonical_url'])

    def test_snapshot_and_text_byte_tampering(self):
        for field in ("snapshot_path", "text_path"):
            with self.subTest(field=field):
                path = self.root / self.rows[0][field]
                original = path.read_bytes()
                hit = self.search()["results"][0]
                path.write_bytes(original + b" ")
                response = self.search()
                self.assert_integrity_error(response)
                self.assertEqual(response["results"], [])
                self.assertTrue(validate_research_results(self.root, [hit]))
                path.write_bytes(original)

    def test_fts_text_url_locator_and_metadata_tampering(self):
        changes = {
            "text": "Retailer billing fabricated quotation", "url": "https://www.aer.gov.au/invented",
            "locator": "page:99", "title": "Invented title", "sha256": "0" * 64,
            "snapshot_path": "source-originals/objects/invented.bin", "text_path": "source-originals/objects/invented.json",
            "text_sha256": "0" * 64, "retrieved_at": "2026-09-06T00:00:00Z",
            "acquisition_method": "official-certified", "extraction_status": "verified",
            "page_count": 99, "pages_without_text": "[]", "review_status": "approved",
        }
        for field, value in changes.items():
            with self.subTest(field=field):
                self.rebuild()
                self.sql(f"UPDATE originals SET {field}=?", (value,))
                response = self.search()
                self.assert_integrity_error(response)
                self.assertFalse(response["results"])

    def test_matching_shadow_content_poison_is_rejected(self):
        self.sql("UPDATE originals_content SET c3=?", ("Retailer billing forged in shadow content",))
        self.assert_integrity_error(self.search())

    def test_self_consistent_fts_objects_need_manifest_authorization(self):
        path, digest = save_object(self.root, json.dumps([{"locator": "page:1", "text": "Retailer billing invented."}]).encode(), ".json")
        self.sql("UPDATE originals SET text=?,text_path=?,text_sha256=?", ("Retailer billing invented.", path, digest))
        self.assert_integrity_error(self.search())

    def test_escaped_snapshot_and_text_paths_even_with_matching_hashes(self):
        for field in ("snapshot_path", "text_path"):
            original = self.rows[0][field]
            data = (self.root / original).read_bytes()
            outside = self.root / ("outside-" + field)
            outside.write_bytes(data)
            paths = (outside.name, "source-originals/objects/../../" + outside.name, str(outside.resolve()))
            for escaped in paths:
                with self.subTest(field=field, path=escaped):
                    self.rows[0][field] = escaped
                    self.write_manifest()
                    self.sql(f"UPDATE originals SET {field}=?", (escaped,))
                    self.assert_integrity_error(self.search())
            self.rows[0][field] = original
            self.rebuild()

    def test_symlink_escape_when_platform_allows(self):
        outside = self.root / "outside.bin"
        outside.write_bytes((self.root / self.rows[0]["snapshot_path"]).read_bytes())
        link = self.root / "source-originals/objects/link.bin"
        try:
            link.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"Symlink creation unavailable: {exc}")
        self.rows[0]["snapshot_path"] = "source-originals/objects/link.bin"
        self.write_manifest()
        self.sql("UPDATE originals SET snapshot_path=?", (self.rows[0]["snapshot_path"],))
        self.assert_integrity_error(self.search())

    def test_missing_optional_archive_does_not_create_database(self):
        absent = self.root / "no-archive"
        response = search_research_originals(absent, "billing")
        self.assertEqual(response["status"], "archive-unavailable")
        self.assertEqual(response["results"], [])
        self.assertFalse(absent.exists())
        self.assertEqual(validate_research_results(absent, []), [])

    def test_incomplete_or_corrupt_archive_is_not_no_matches(self):
        manifest = self.root / "source-originals/manifest.jsonl"
        manifest.unlink()
        self.assert_integrity_error(self.search("nonexistentkeyword"))
        self.write_manifest()
        database = self.root / "source-originals/search.sqlite3"
        database.unlink()
        self.assert_integrity_error(self.search())
        self.assertFalse(database.exists())
        database.write_bytes(b"This is not SQLite")
        self.assert_integrity_error(self.search("nonexistentkeyword"))

    def test_malformed_manifest_and_text_json_are_validation_errors(self):
        manifest = self.root / "source-originals/manifest.jsonl"
        for malformed in ("not-json", "[]\n", '{"canonical_url": null}'):
            manifest.write_text(malformed, encoding="utf-8")
            self.assert_integrity_error(self.search())
        for raw in (b"{}", b"not-json", b'[{"locator":"page:1","text":false}]',
                    b'[{"locator":"page:1","text":"billing"},{"locator":"page:1","text":"billing"}]'):
            path, digest = save_object(self.root, raw, ".json")
            self.rows[0].update(text_path=path, text_sha256=digest)
            self.write_manifest()
            self.sql("UPDATE originals SET text_path=?,text_sha256=?", (path, digest))
            self.assert_integrity_error(self.search())

    def test_stopword_heavy_business_question_and_literal_fts(self):
        response = self.search("Could you please tell me what we should do about retailer billing?")
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["queries_used"][0], '"retailer" AND "billing"')
        response = self.search('billing" OR * NOT ("retailer) --')
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["queries_used"][0], '"billing" AND "retailer"')

    def test_partial_term_fallback_is_visible(self):
        response = self.search("billing unmatchedword")
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["queries_used"], ['"billing" AND "unmatchedword"', '"billing" OR "unmatchedword"'])
        self.assertTrue(any("fallback" in warning for warning in response["warnings"]))

    def test_explicit_acronym_survives_unmatched_business_context(self):
        target = self.add_source(url='https://www.aer.gov.au/protocol', title='',
                                 units=[{'locator': 'page:1', 'text': 'NMI identification and customer records.'}])
        self.add_source(url='https://www.aer.gov.au/other', title='Retailer billing guide',
                        units=[{'locator': 'page:1', 'text': 'Retailer billing customer records and team process.'}])
        self.rebuild()
        response = self.search('Our retailer billing team has a question about NMI records and unfamiliarword.', limit=1)
        self.assertEqual(response['status'], 'ok')
        self.assertEqual(response['results'][0]['url'], target['canonical_url'])
        self.assertEqual(response['query_anchors'], ['"nmi"'])
        self.assertIn('"nmi"', response['queries_used'][1])
        self.assertEqual(validate_research_results(self.root, response['results']), [])

    def test_quoted_phrase_priority_keeps_word_order_and_visible_broad_fallback(self):
        target = self.add_source(url='https://www.aer.gov.au/target', title='',
                                 units=[{'locator': 'page:1', 'text': 'Life support registration.'}])
        self.add_source(url='https://www.aer.gov.au/other', title='',
                        units=[{'locator': 'page:1', 'text': 'Support your daily life through retailer billing.'}])
        self.rebuild()
        response = self.search('Find "life support" material for an unfamiliarworkflow.', limit=3)
        self.assertEqual(response['results'][0]['url'], target['canonical_url'])
        self.assertEqual(response['query_anchors'], ['"life support"'])
        self.assertTrue(any('Any-term fallback' in warning for warning in response['warnings']))

    def test_missing_acronym_does_not_suppress_available_broad_results(self):
        response = self.search('ZZZX retailer billing unmatchedword')
        self.assertEqual(response['status'], 'ok')
        self.assertEqual(response['results'][0]['url'], self.rows[0]['canonical_url'])
        self.assertEqual(len(response['queries_used']), 2)
        self.assertFalse(response['anchor_probes'][0]['used'])

    def test_common_acronym_does_not_displace_issue_specific_broad_results(self):
        for number in range(3):
            self.add_source(url=f'https://www.aer.gov.au/common-{number}', title='',
                            units=[{'locator': 'page:1', 'text': 'REG technical background.'}])
        self.rebuild()
        with patch('search_source_originals.MAX_ANCHOR_SOURCES', 2):
            response = self.search('REG retailer billing unfamiliarword')
        self.assertEqual(response['status'], 'ok')
        self.assertFalse(response['anchor_probes'][0]['used'])
        self.assertTrue(response['anchor_probes'][0]['count_capped'])
        self.assertEqual(response['anchor_probes'][0]['distinct_sources_observed'], 3)
        self.assertEqual(len(response['queries_used']), 2)

    def test_acronym_selectivity_counts_sources_not_pages(self):
        self.add_source(url='https://www.aer.gov.au/nmi', title='',
                        units=[{'locator': f'page:{n}', 'text': 'NMI information.'} for n in range(100)])
        self.rebuild()
        with patch('search_source_originals.MAX_ANCHOR_SOURCES', 2):
            response = self.search('NMI billing unfamiliarword')
        self.assertTrue(response['anchor_probes'][0]['used'])
        self.assertEqual(response['anchor_probes'][0]['distinct_sources_observed'], 1)

    def test_only_explicit_bounded_anchors_are_used(self):
        self.assertEqual(_query_anchors('Retailer billing in Victoria', ['retailer', 'billing', 'victoria']), [])
        self.assertEqual(_query_anchors('WE OR NOT BILLING', ['billing']), ['"billing"'])
        self.assertEqual(_query_anchors('NMI "life support"', ['billing']), [])
        query = ' '.join('ACR' + str(n) for n in range(20))
        self.assertEqual(len(_query_anchors(query, query.lower().split())), MAX_QUERY_ANCHORS)
        response = self.search('billing ' + ' '.join(f'term{n}' for n in range(MAX_TOKENS)) + ' NMI')
        self.assertEqual(response['query_anchors'], [])

    def test_anchor_cannot_bypass_manifest_integrity(self):
        self.add_source(url='https://www.aer.gov.au/nmi', title='',
                        units=[{'locator': 'page:1', 'text': 'NMI information.'}])
        self.rebuild()
        (self.root / self.rows[-1]['snapshot_path']).write_bytes(b'tampered')
        response = self.search('NMI billing unfamiliarword')
        self.assert_integrity_error(response)
        self.assertNotIn(self.rows[-1]['canonical_url'], [r['url'] for r in response['results']])

    def test_empty_invalid_and_stopword_only_queries(self):
        for query in ("", "  ", "?!()", None, 12, "the and can we please", "\x00billing", "x" * 4097):
            with self.subTest(query=repr(query)[:50]):
                response = self.search(query)
                self.assertEqual(response["status"], "invalid-query")
                self.assertFalse(response["queries_used"])
        for limit in (0, -1, 101, True, 1.5, "6", None):
            self.assertEqual(self.search(limit=limit)["status"], "invalid-query")

    def test_genuine_no_matches(self):
        response = self.search("unmatchedword")
        self.assertEqual(response["status"], "no-matches")
        self.assertEqual(response["results"], [])
        self.assertFalse(response["validation_errors"])

    def test_query_tokens_and_candidate_scan_are_bounded(self):
        response = self.search("billing " + " ".join(f"term{n}" for n in range(MAX_TOKENS + 10)), limit=100)
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["queries_used"][0].count('"') // 2, MAX_TOKENS)
        self.assertLessEqual(response["candidate_limit"], MAX_CANDIDATES)
        for number in range(5):
            self.sql("INSERT INTO originals SELECT ?,title,locator,text,sha256,snapshot_path,review_status,retrieved_at,acquisition_method,extraction_status,page_count,pages_without_text,text_path,text_sha256 FROM originals LIMIT 1",
                     (f"https://www.aer.gov.au/poison-{number}",))
        with patch("search_source_originals.MAX_CANDIDATES", 3):
            response = self.search()
        self.assert_integrity_error(response)
        self.assertEqual(response["candidates_scanned"], 3)
        self.assertTrue(any("scan limit reached" in warning for warning in response["warnings"]))

    def test_url_diversity_despite_many_high_ranked_pages(self):
        self.add_source(units=[{"locator": f"page:{n}", "text": "Retailer billing."} for n in range(1, 301)])
        for number in range(4):
            self.add_source(url=f"https://www.aer.gov.au/other-{number}",
                            units=[{"locator": "page:1", "text": "Retailer billing and " + "more context " * 100}])
        self.rebuild()
        response = self.search(limit=4)
        self.assertEqual(response["status"], "ok")
        self.assertEqual(len(response["results"]), 4)
        self.assertEqual(len({hit["url"] for hit in response["results"]}), 4)
        self.assertEqual(response["candidates_scanned"], 4)

    def test_good_results_survive_other_candidate_failures_with_error_status(self):
        self.add_source(url="https://www.aer.gov.au/other")
        self.rebuild()
        (self.root / self.rows[0]["snapshot_path"]).write_bytes(b"tampered")
        response = self.search()
        self.assert_integrity_error(response)
        self.assertEqual(len(response["results"]), 1)
        self.assertEqual(validate_research_results(self.root, response["results"]), [])

    def test_recovery_append_order_failed_retry_and_invalidation(self):
        prior_hit = self.search()["results"][0]
        self.rows.append({"canonical_url": self.rows[0]["canonical_url"], "capture_status": "failed"})
        self.write_manifest()
        self.assertEqual(self.search()["status"], "ok")
        self.add_source(units=[{"locator": "page:1", "text": "Recovered retailer billing text."}],
                        recovery_log="recovery-browser.jsonl", retrieved_at="2020-01-01T00:00:00Z")
        self.write_manifest()
        self.assert_integrity_error(self.search())
        self.assertTrue(validate_research_results(self.root, [prior_hit]))
        self.rebuild()
        self.assertEqual(self.search()["results"][0]["excerpt"], "Recovered retailer billing text.")
        self.rows.append({"canonical_url": self.rows[0]["canonical_url"], "invalidates_prior_text": True})
        self.write_manifest()
        self.assert_integrity_error(self.search())

    def test_unmerged_recovery_log_does_not_authorize_poison(self):
        recovery = {**self.rows[0], "title": "Unmerged recovery title"}
        (self.root / "source-originals/recovery-browser.jsonl").write_text(json.dumps(recovery), encoding="utf-8")
        self.sql("UPDATE originals SET title=?", (recovery["title"],))
        self.assert_integrity_error(self.search())

    def test_packet_metadata_excerpt_and_id_cannot_be_resealed(self):
        hit = self.search()["results"][0]
        changes = {"research_id": "original:invented", "excerpt": "A finding invented by the packet.",
                   "url": "https://www.aer.gov.au/fake", "locator": "page:2", "title": "Fake title",
                   "sha256": "0" * 64, "text_sha256": "0" * 64, "snapshot_path": "outside.bin",
                   "text_path": "outside.json", "retrieved_at": "future", "acquisition_method": "certified",
                   "extraction_status": "approved", "review_status": "legal clearance",
                   "page_count": 1, "pages_without_text": [], "current_law_release": True}
        for key, value in changes.items():
            with self.subTest(field=key):
                forged = {**hit, key: value}
                self.assertTrue(validate_research_results(self.root, [forged]))
        self.assertTrue(validate_research_results(self.root, [hit, copy.deepcopy(hit)]))
        self.assertTrue(validate_research_results(self.root, [{"excerpt": hit["excerpt"]}]))
        self.assertTrue(validate_research_results(self.root, [None]))
        self.assertTrue(validate_research_results(self.root, {}))

    def test_packet_validation_does_not_rerun_search(self):
        hit = self.search()["results"][0]
        with patch("search_source_originals.sqlite3.connect", side_effect=AssertionError("Must not search")):
            self.assertEqual(validate_research_results(self.root, [hit]), [])
        (self.root / "source-originals/search.sqlite3").unlink()
        self.assertEqual(validate_research_results(self.root, [hit]), [])

    def test_sql_budget_failure_is_not_no_matches(self):
        with patch("search_source_originals.SQL_SECONDS", -1):
            self.add_source(units=[{"locator": f"page:{n}", "text": "Retailer billing."} for n in range(3000)])
            self.rebuild()
            response = self.search()
        self.assert_integrity_error(response)


if __name__ == "__main__":
    unittest.main()
