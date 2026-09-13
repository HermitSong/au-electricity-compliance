"""Public event metadata curation invariants, not legal clearance."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
CURATION_NOTE = (
    "Case metadata independently curated from existing public records; "
    "no new source acquisition or substantive legal determination."
)
GAP = "public-details-require-source-review"
MUTABLE_FIELDS = {
    "issue", "outcome", "instrument_or_rule", "public_distribution_note",
    "public_curation_gaps", "public_curation_basis",
    "public_curation_basis_event_ids",
}


def read_jsonl(name):
    return [
        json.loads(line)
        for line in (ROOT / "data" / name).read_text("utf-8").splitlines()
    ]


def digest(value):
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class PublicEventCurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events = read_jsonl("enforcement-events-full.jsonl")
        cls.by_id = {event["event_id"]: event for event in cls.events}
        cls.curated = [
            event for event in cls.events
            if event.get("public_distribution_note") == CURATION_NOTE
        ]
        cls.links = read_jsonl("event-provision-links.jsonl")

    def event(self, number):
        return self.events[number - 1]

    def test_audited_inventory_is_complete(self):
        # Fixed audit inventory: 280 narrative cases and 42 parser/navigation cases.
        self.assertEqual(len(self.events), 824)
        self.assertEqual(len(self.by_id), 824)
        self.assertEqual(len(self.curated), 322)
        self.assertEqual(
            digest(sorted(event["event_id"] for event in self.curated)),
            "337aeffd9862f6aa5565b2ac3bf6781da2aa7b717dea3a00e72c13c0583340ca",
        )

    def test_identity_dates_status_and_temporal_notes_preserved(self):
        # Fingerprint captured before curation; only the explicitly mutable
        # narrative/curation fields are excluded, including for untouched rows.
        protected = [
            {key: value for key, value in event.items()
             if key not in MUTABLE_FIELDS}
            for event in self.events
        ]
        self.assertEqual(
            digest(protected),
            "ac54a911acf0286650e3415d343527a35467e5c96c9ec1dee646c47f922a6b05",
        )

    def test_corresponding_historical_links_match_exactly(self):
        curated_ids = {event["event_id"] for event in self.curated}
        found = set()
        for link in self.links:
            if link["event_id"] in curated_ids:
                found.add(link["event_id"])
                self.assertEqual(
                    link["historical_instrument_or_rule"],
                    self.by_id[link["event_id"]]["instrument_or_rule"],
                    link["event_id"],
                )
        self.assertEqual(found, curated_ids)

    def test_parser_and_publisher_boilerplate_do_not_return(self):
        # Specific contamination signatures, not a length-based copyright rule.
        residue = re.compile(
            r"Home WA Government Announcements|"
            r"Disciplinary Action (?:summary|outcome)|"
            r"Obligations? contravened\s*:|More information|"
            r"Sentencing Remarks|In mitigation, the Court|"
            r"Compliance Rating Scale|We issued 2 penalty",
            re.IGNORECASE,
        )
        for event in self.curated:
            for field in ("issue", "outcome", "instrument_or_rule"):
                with self.subTest(event=event["event_id"], field=field):
                    self.assertIsNone(residue.search(event[field]))
            self.assertIsNone(re.search(
                r"(?:^|;\s*)s\s+[a-z]",
                event["instrument_or_rule"],
            ))

    def test_missing_instruments_have_separate_explicit_gaps(self):
        empty = [event for event in self.curated
                 if not event["instrument_or_rule"]]
        self.assertEqual(len(empty), 69)
        for event in self.curated:
            rule = event["instrument_or_rule"]
            self.assertNotEqual(rule, event["case_status_note"])
            self.assertNotIn(GAP, rule)
            gaps = event.get("public_curation_gaps", [])
            for gap in gaps:
                self.assertEqual(gap["status"], GAP)
                self.assertIn(gap["field"],
                              ("issue", "outcome", "instrument_or_rule"))
                self.assertTrue(gap["detail"])
            if not rule:
                self.assertTrue(any(
                    gap["field"] == "instrument_or_rule" for gap in gaps
                ), event["event_id"])
            for field in ("issue", "outcome"):
                if GAP in event[field]:
                    self.assertTrue(any(gap["field"] == field for gap in gaps))

    def test_amounts_and_counterfactuals_remain_distinct(self):
        for number, amounts in {
            67: ("$1.1 million",),
            74: ("$125,000", "$145,000"),
            111: ("$2 million", "$325,000"),
            113: ("$700,000", "$780,000", "23,000"),
            206: ("$20,000", "$60,000", "$80,000"),
            434: ("$35,000", GAP),
            517: ("$11,000", GAP),
            587: ("$3,000", "$553", GAP),
            714: ("$577", GAP),
            817: ("$40,000", "$2,268", "counterfactual", "$80,000"),
        }.items():
            for amount in amounts:
                self.assertIn(amount, self.event(number)["outcome"])
        splendor = self.event(584)["outcome"]
        self.assertIn("counterfactual", splendor)
        self.assertIn("actual sentence is " + GAP, splendor)
        for number, fine, other in ((697, "$580,000", "$30,000"),
                                    (698, "$300,000", "$20,000")):
            event = self.event(number)
            self.assertIn(fine, event["outcome"])
            self.assertIn(other, event["outcome"])
            self.assertEqual(event["public_curation_basis_event_ids"],
                             [self.event(696)["event_id"]])

    def test_review_stays_and_historical_code_boundaries_survive(self):
        stayed = self.event(768)
        for identifier in ("15A(i)(a)", "15A(i)(b)(i)"):
            self.assertIn(identifier, stayed["instrument_or_rule"])
        self.assertTrue(any(
            "source-recorded" in gap["detail"] and "unverified" in gap["detail"]
            for gap in stayed["public_curation_gaps"]
        ))
        self.assertIn("15a(1)(b)(i)", self.event(735)["instrument_or_rule"])
        for detail in ("24 December 2025", "26 March 2026", "5 June 2026",
                       "Not a final tribunal determination",
                       "do not infer that all certificate decisions were stayed"):
            self.assertIn(detail, stayed["case_status_note"])
        for number, date in ((695, "24 September 2025"),
                             (718, "15 October 2025"),
                             (754, "9 February 2026")):
            self.assertIn(date, self.event(number)["issue"])
        self.assertIn("clause 30(1)", self.event(708)["instrument_or_rule"])
        self.assertNotIn("clause 30(1)", self.event(747)["instrument_or_rule"])
        self.assertIn("$40.424 million", self.event(747)["outcome"])
        self.assertIn("$3.584 million", self.event(747)["outcome"])
        self.assertIn("not a new contravention", self.event(803)["issue"])
        self.assertIn("12 June 2025", self.event(593)["outcome"])
        self.assertIn("12 months and until", self.event(688)["outcome"])
        self.assertIn("12 months", self.event(807)["outcome"])

    def test_unrecoverable_narratives_do_not_become_positive_findings(self):
        for number, field in ((406, "outcome"), (478, "outcome"),
                              (492, "outcome"), (711, "issue"),
                              (741, "issue"), (801, "outcome"),
                              (811, "outcome")):
            self.assertIn(GAP, self.event(number)[field])
        self.assertIn("no breach finding", self.event(34)["outcome"])
        self.assertIn("not findings", self.event(516)["outcome"])


if __name__ == "__main__":
    unittest.main()
