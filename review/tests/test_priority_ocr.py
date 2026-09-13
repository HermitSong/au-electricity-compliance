import sys
from pathlib import Path
import unittest
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from prepare_priority_ocr import priority, select, low_confidence_words


def row(name, pages=1):
    return {"canonical_url": "https://www.esc.vic.gov.au/" + name, "sha256": name,
            "page_count": pages, "recovery_status": "failed", "source_family_ids": ["VIC-ESC-PENALTIES"]}


class PriorityOcrTests(unittest.TestCase):
    def test_tesseract_tsv_with_and_without_header_keeps_confidence_and_coordinates(self):
        body = "5\t1\t1\t1\t1\t1\t10\t20\t30\t40\t72.5\t$200\n5\t1\t1\t1\t1\t2\t50\t20\t30\t40\t96\tnotice\n"
        header = "level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
        for tsv in (body, header + body):
            words = low_confidence_words(tsv)
            self.assertEqual(len(words), 1)
            self.assertEqual(words[0]["text"], "$200")
            self.assertEqual(words[0]["left"], "10")
            self.assertEqual(words[0]["conf"], "72.5")

    def test_shortest_first_and_both_limits(self):
        result, _ = select([row("penalty-z.pdf", 9), row("undertaking-b.pdf", 3), row("penalty-a.pdf", 1)], 2, 5)
        self.assertEqual([r[0]["page_count"] for r in result], [1, 3])

    def test_submissions_and_clearing_excluded(self):
        for name in ("penalty-policy-submission.pdf", "environmental-enforcement-penalty.pdf", "VCN-CPS-penalty.pdf"):
            self.assertIsNone(priority(row(name))[0])

    def test_non_electricity_and_already_recovered_excluded(self):
        candidate = row("penalty.pdf")
        candidate.update(canonical_url="https://www.acma.gov.au/penalty.pdf", source_family_ids=["ACMA"])
        self.assertIsNone(priority(candidate)[0])
        candidate = row("penalty.pdf")
        candidate["recovery_status"] = "captured"
        self.assertEqual(select([candidate])[0], [])

    def test_unknown_pages_duplicates_and_hard_caps(self):
        self.assertEqual(len(select([row("penalty.pdf"), row("penalty.pdf")])[0]), 1)
        self.assertEqual(select([row("penalty.pdf", None)])[0], [])
        for docs, pages in ((31, 100), (30, 101), (0, 100)):
            with self.assertRaises(ValueError):
                select([], docs, pages)


if __name__ == "__main__":
    unittest.main()
