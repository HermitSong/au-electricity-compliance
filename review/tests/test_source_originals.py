import hashlib
from collections import deque
import json
from contextlib import closing
from pathlib import Path
import sys
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from collect_source_originals import Fetcher, allowed_url, discover, extract, normalise_url, rebuild_outputs, save_object, take_available_host, transport_url
from import_browser_source import transfer_fingerprint
from validate_source_originals import validate


class SourceOriginalTests(unittest.TestCase):
    def test_url_safety(self):
        self.assertTrue(allowed_url("https://www.aer.gov.au/test", set()))
        for url in ("http://www.aer.gov.au/test", "https://user:pass@www.aer.gov.au/",
                    "https://www.aer.gov.au.evil.invalid/", "https://127.0.0.1/", "https://www.aer.gov.au:8888/"):
            self.assertFalse(allowed_url(url, set()))

    def test_fragment_removed_query_preserved(self):
        self.assertEqual(normalise_url("https://www.aer.gov.au/a?version=3#x"), "https://www.aer.gov.au/a?version=3")

    def test_transport_encoding_preserves_existing_escapes_and_query(self):
        original = "https://www.aer.gov.au/Guideline - version%201.pdf?q=a b&version=2"
        self.assertEqual(transport_url(original), "https://www.aer.gov.au/Guideline%20-%20version%201.pdf?q=a%20b&version=2")
        self.assertEqual(normalise_url(original), original)

    def test_challenge_is_not_document_text(self):
        result = extract(b"<html><title>Just a moment</title><body>Verify</body></html>", "text/html", "https://www.aer.gov.au/a")
        self.assertEqual(result["extraction_status"], "blocked-or-error-page")
        self.assertFalse(result["units"])

    def test_main_text_and_links(self):
        document = ("<html><title>A decision</title><nav>MENU</nav><main><p>" + "Recorded facts. " * 30
                    + "</p><a href='/decision.pdf'>Decision</a><script>BAD</script></main></html>").encode()
        result = extract(document, "text/html", "https://www.aer.gov.au/a")
        self.assertNotIn("MENU", result["units"][0]["text"])
        self.assertNotIn("BAD", result["units"][0]["text"])
        self.assertEqual(result["links"][0]["url"], "https://www.aer.gov.au/decision.pdf")
        self.assertEqual(result["extraction_status"], "extracted-unreviewed")

    def test_objects_cannot_silently_change(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            relative, digest = save_object(root, b"source", ".bin")
            self.assertEqual(digest, hashlib.sha256(b"source").hexdigest())
            self.assertEqual(save_object(root, b"source", ".bin"), (relative, digest))
            (root / relative).write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                save_object(root, b"source", ".bin")

    def test_attachment_depth_and_authority(self):
        row = {"canonical_url": "https://www.aer.gov.au/a", "source_family_ids": [],
               "discovery_depth": 0, "extraction_status": "extracted-unreviewed", "links": [
                   {"url": "https://www.aer.gov.au/decision.pdf", "label": "Decision"},
                   {"url": "https://evil.invalid/a.pdf", "label": "Decision"},
               ]}
        self.assertEqual(len(discover(row, set(), 1)), 1)
        self.assertFalse(discover(row, set(), 0))

    def test_largest_main_and_article_header_preserved(self):
        document = ("<html><main>Menu</main><article><header>Decision on 5 September 2026</header><p>"
                    + "Relevant case facts. " * 20 + "</p></article></html>").encode()
        result = extract(document, "text/html", "https://www.aer.gov.au/a")
        self.assertIn("Decision on 5 September 2026", result["units"][0]["text"])

    def test_robots_denial_stops_source_request(self):
        fetcher = Fetcher(set(), 5, 1024, 0, permissions=SimpleNamespace(require=lambda url: {}))
        item = {"canonical_url": "https://www.aer.gov.au/private/case", "references": [],
                "source_family_ids": [], "discovery_depth": 0, "discovered_from": []}
        with tempfile.TemporaryDirectory() as folder, patch.object(fetcher, "request", return_value=(
                b"User-agent: *\nDisallow: /private/", {}, "https://www.aer.gov.au/robots.txt", 200)) as request:
            row = fetcher.fetch(item, Path(folder))
        self.assertEqual(row["reason"], "robots-disallowed")
        self.assertEqual(request.call_count, 1)
        self.assertIs(row["current_law_release"], False)

    def test_login_page_is_not_source_text(self):
        result = extract(b"<html><title>Sign in</title><body>Account needed</body></html>", "text/html", "https://www.aer.gov.au/a")
        self.assertEqual(result["extraction_status"], "blocked-or-error-page")

    def test_first_access_denial_pauses_host_for_review(self):
        fetcher = Fetcher(set(), 5, 1024, 0, permissions=SimpleNamespace(require=lambda url: {}))
        item = {"canonical_url": "https://www.aer.gov.au/restricted", "references": [],
                "source_family_ids": [], "discovery_depth": 0, "discovered_from": []}
        with tempfile.TemporaryDirectory() as folder, patch.object(fetcher, "permission", return_value=(True, "robots-allowed")), \
                patch.object(fetcher, "request", side_effect=HTTPError(item["canonical_url"], 403, "Forbidden", {}, None)):
            fetcher.robots["www.aer.gov.au"] = (None, None)
            row = fetcher.fetch(item, Path(folder))
        self.assertEqual(row["reason"], "http-403")
        self.assertIn("www.aer.gov.au", fetcher.paused)

    def test_slow_host_does_not_occupy_all_workers(self):
        queued = deque([{"canonical_url": "https://www.aer.gov.au/a"},
                        {"canonical_url": "https://www.aer.gov.au/b"},
                        {"canonical_url": "https://www.esc.vic.gov.au/a"}])
        item = take_available_host(queued, [{"canonical_url": "https://www.aer.gov.au/running"}])
        self.assertEqual(item["canonical_url"], "https://www.esc.vic.gov.au/a")
        self.assertEqual(len(queued), 2)
        self.assertIsNone(take_available_host(queued, [{"canonical_url": "https://www.aer.gov.au/running"}]))

    def test_browser_transfer_fingerprint(self):
        self.assertEqual(transfer_fingerprint("hello"), (5, "4f9f2cab"))
        self.assertEqual(transfer_fingerprint("\U0001f600")[0], 2)

    def test_archive_index_and_corruption_detection(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source_path, source_hash = save_object(root, b"Original test source", ".bin")
            text_path, text_hash = save_object(root, json.dumps([{"locator": "page:1", "text": "Test source evidence"}]).encode(), ".json")
            item = {"canonical_url": "https://www.aer.gov.au/test", "references": [],
                    "source_family_ids": [], "discovery_depth": 0, "discovered_from": []}
            row = {**item, "capture_status": "bytes-preserved", "snapshot_path": source_path,
                   "sha256": source_hash, "text_path": text_path, "text_sha256": text_hash,
                   "extraction_status": "extracted-unreviewed", "legal_review_status": "not-reviewed",
                   "current_law_release": False, "retrieved_at": "2026-09-05T00:00:00Z"}
            (root / "source-originals" / "manifest.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
            summary = rebuild_outputs(root, {item["canonical_url"]: item}, 1, "test")
            self.assertEqual(summary["research_text_url_count"], 1)
            self.assertEqual(summary["legally_verified_full_text_url_count"], 0)
            self.assertTrue(validate(root)["passed"])
            with closing(sqlite3.connect(root / "source-originals" / "search.sqlite3")) as connection:
                result = connection.execute("SELECT acquisition_method,extraction_status,pages_without_text,text_sha256 FROM originals").fetchone()
            self.assertEqual(result, ("https-original-bytes", "extracted-unreviewed", "[]", text_hash))
            with closing(sqlite3.connect(root / "source-originals" / "search.sqlite3")) as connection, connection:
                connection.execute("UPDATE originals SET text = 'Invented source text'")
            self.assertFalse(validate(root)["passed"])
            rebuild_outputs(root, {item["canonical_url"]: item}, 1, "test")
            (root / source_path).write_bytes(b"Changed")
            self.assertFalse(validate(root)["passed"])


if __name__ == "__main__":
    unittest.main()
