from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from snapshot_official_sources import known_access_interstitial


class ContentAdmissionTests(unittest.TestCase):
    def test_observed_aer_challenge_is_not_source_text(self):
        sample = b'<script>function triggerInterstitialChallenge(){xhr.open("POST", "/_sec/verify?provider=interstitial")}</script>'
        self.assertTrue(known_access_interstitial(sample, 'text/html; charset=utf-8'))

    def test_genuine_article_mentions_are_not_the_signature(self):
        self.assertFalse(known_access_interstitial(b'<html>The court considered access denied messages.</html>', 'text/html'))

    def test_non_html_bytes_are_not_classified_as_html(self):
        self.assertFalse(known_access_interstitial(b'%PDF-1.7', 'application/pdf'))


if __name__ == '__main__':
    unittest.main()
