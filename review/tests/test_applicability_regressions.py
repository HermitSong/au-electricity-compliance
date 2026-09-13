"""Algorithm regressions for intake routing, not legal applicability findings."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from route_applicability import route_question


class ApplicabilityRegressionTests(unittest.TestCase):
    def route(self, question, **kwargs):
        return route_question(question, as_of="2026-09-06", **kwargs)

    def test_public_return_fields_remain_available(self):
        result = self.route("Can a Victorian retailer disconnect a customer tomorrow?")
        expected_fields = {
            "route_state", "answer_as_of", "knowledge_baseline", "temporal_intent",
            "jurisdiction_candidates", "actor_candidates", "activity_candidates",
            "provision_route_ids", "provision_route_status", "missing_material_inputs",
            "requires_live_version_check", "reasons",
        }
        self.assertTrue(expected_fields <= result.keys())
        self.assertEqual(result["answer_as_of"], "2026-09-06")
        self.assertEqual(result["knowledge_baseline"], "2026-08-29")
        self.assertEqual(result["temporal_intent"], "current-or-prospective-advice")
        self.assertTrue(result["requires_live_version_check"])

    def test_victoria_life_support_disconnection_routes(self):
        for question, context in (
            ("Can a Victorian retailer disconnect a life-support customer tomorrow?", {}),
            ("Can we disconnect a life-support customer tomorrow?",
             {"jurisdiction": "Victoria", "actor": "retailer"}),
        ):
            with self.subTest(question=question):
                result = self.route(question, **context)
                self.assertEqual(result["route_state"], "routed")
                self.assertEqual(result["jurisdiction_candidates"], ["Victoria"])
                self.assertEqual(result["provision_route_ids"], [
                    "VIC-ERCP-V6-LIFE-SUPPORT-2026-08-29",
                    "VIC-ERCP-V6-DISCONNECTION-2026-08-29",
                ])
                self.assertEqual(result["missing_material_inputs"], [])

    def test_statute_word_act_does_not_add_a_territory(self):
        for statute_word in ("Act", "act"):
            with self.subTest(statute_word=statute_word):
                result = self.route(
                    f"Under the Electricity Industry {statute_word}, "
                    "must a Victorian retailer refund a customer?"
                )
                self.assertEqual(result["jurisdiction_candidates"], ["Victoria"])
                self.assertEqual(result["route_state"], "routed")
                self.assertEqual(result["provision_route_ids"], ["VIC-ERCP-V6-2026-08-29"])

    def test_statute_word_act_does_not_resolve_unknown_jurisdiction(self):
        result = self.route("Under the Electricity Act, may a retailer disconnect a customer?")
        self.assertEqual(result["jurisdiction_candidates"], [])
        self.assertEqual(result["route_state"], "needs-applicability-input")
        self.assertIn("jurisdiction", result["missing_material_inputs"])
        self.assertEqual(result["provision_route_ids"], [])

    def test_uppercase_act_and_full_territory_name_are_detected(self):
        for territory in ("ACT", "Australian Capital Territory", "australian capital territory"):
            with self.subTest(territory=territory):
                result = self.route(
                    f"Can a retailer in {territory} disconnect a life-support customer tomorrow?"
                )
                self.assertEqual(result["jurisdiction_candidates"], ["Australian Capital Territory"])
                self.assertEqual(result["route_state"], "routed")
                self.assertEqual(result["provision_route_ids"], [
                    "NERR-LIFE-SUPPORT-CURRENT-2026-08-29",
                    "NERR-DISCONNECTION-CURRENT-2026-08-29",
                ])

    def test_unresolved_multiple_regimes_remain_blocked(self):
        for context in ("Victoria and ACT", "Victoria and NSW", "Victoria under NEM rules"):
            with self.subTest(context=context):
                result = self.route(f"Can a retailer in {context} disconnect a customer tomorrow?")
                self.assertEqual(result["route_state"], "needs-applicability-input")
                self.assertIn(
                    "single applicable jurisdiction or an explicit cross-jurisdiction comparison",
                    result["missing_material_inputs"],
                )
                self.assertEqual(result["provision_route_ids"], [])
                self.assertTrue(result["requires_live_version_check"])

    def test_mixed_temporal_intent_keeps_current_advice_and_live_gate(self):
        historical_questions = (
            "What happened in the 2024 Victorian disconnection case?",
            "Describe the case outcome for a Victorian retailer.",
            "Describe the penalty imposed on a Victorian retailer.",
            "A Victorian retailer was fined for disconnecting a customer.",
            "Describe the historical case involving a Victorian retailer.",
            "Describe the Victorian retailer's case on appeal.",
        )
        current_question = "Can a Victorian retailer disconnect a life-support customer tomorrow?"
        for historical in historical_questions:
            for question in (f"{historical} {current_question}", f"{current_question} {historical}"):
                with self.subTest(question=question):
                    result = self.route(question)
                    self.assertEqual(result["temporal_intent"], "current-or-prospective-advice")
                    self.assertTrue(result["requires_live_version_check"])
                    self.assertEqual(result["route_state"], "routed")
                    self.assertEqual(result["provision_route_ids"], [
                        "VIC-ERCP-V6-LIFE-SUPPORT-2026-08-29",
                        "VIC-ERCP-V6-DISCONNECTION-2026-08-29",
                    ])
                    self.assertEqual(result["temporal_sub_intents"], {
                        "historical": True, "current_or_prospective": True,
                    })

    def test_mixed_intent_in_one_sentence_keeps_live_gate(self):
        result = self.route(
            "What happened when a Victorian retailer was fined for disconnection, "
            "and can a Victorian retailer disconnect a customer tomorrow?"
        )
        self.assertEqual(result["temporal_intent"], "current-or-prospective-advice")
        self.assertTrue(result["requires_live_version_check"])

    def test_mixed_intent_still_requires_missing_operational_inputs(self):
        for question, missing in (
            ("What happened in the historical case, and can a retailer disconnect tomorrow?",
             ["jurisdiction"]),
            ("Describe the historical case in Victoria. Can we disconnect tomorrow?",
             ["regulated actor role"]),
            ("Describe the historical case in Victoria. Can a retailer proceed tomorrow?",
             ["regulated activity"]),
        ):
            with self.subTest(question=question):
                result = self.route(question)
                self.assertEqual(result["route_state"], "needs-applicability-input")
                self.assertEqual(result["missing_material_inputs"], missing)
                self.assertEqual(result["provision_route_ids"], [])
                self.assertTrue(result["requires_live_version_check"])

    def test_past_only_questions_do_not_require_live_version_check(self):
        for question in (
            "What happened in the 2024 Victorian retailer disconnection case?",
            "Describe the case outcome for a Victorian retailer in 2024.",
            "Describe the penalty imposed on a Victorian retailer in 2024.",
            "Why was a Victorian retailer fined in the historical case?",
            "A Victorian retailer was fined for disconnecting a customer in 2024.",
            "Describe the Victorian retailer's case on appeal in 2024.",
        ):
            with self.subTest(question=question):
                result = self.route(question)
                self.assertEqual(result["temporal_intent"], "historical-or-descriptive")
                self.assertFalse(result["requires_live_version_check"])
                self.assertEqual(result["temporal_sub_intents"], {
                    "historical": True, "current_or_prospective": False,
                })

    def test_mixed_intent_live_gate_respects_answer_date_and_baseline(self):
        question = (
            "What happened in the historical case, "
            "and can a Victorian retailer disconnect a customer tomorrow?"
        )
        for as_of, baseline, expected in (
            ("2026-08-28", "2026-08-29", False),
            ("2026-08-29", "2026-08-29", False),
            ("2026-09-06", "2026-08-29", True),
            ("2026-09-06", "2026-09-06", False),
        ):
            with self.subTest(as_of=as_of, baseline=baseline):
                result = route_question(question, as_of=as_of, knowledge_baseline=baseline)
                self.assertEqual(result["temporal_intent"], "current-or-prospective-advice")
                self.assertEqual(result["requires_live_version_check"], expected)

    def test_fcas_and_pasa_keep_specific_activity_and_route(self):
        for activity, route in (
            ("FCAS", "NER-FCAS-CURRENT-2026-08-29"),
            ("PASA", "NER-PASA-AVAILABILITY-CURRENT-2026-08-29"),
        ):
            for token in (activity, activity.lower()):
                with self.subTest(token=token):
                    result = self.route(f"What must a NEM generator do for {token} today?")
                    self.assertEqual(result["route_state"], "routed")
                    self.assertEqual(result["activity_candidates"], [activity])
                    self.assertEqual(result["provision_route_ids"], [route])
                    self.assertTrue(result["requires_live_version_check"])

    def test_fcas_and_pasa_routes_coexist_with_explicit_bidding_and_dispatch(self):
        result = self.route("What must a NEM generator do for FCAS, PASA, bidding and dispatch today?")
        self.assertCountEqual(result["activity_candidates"], ["bidding and dispatch", "FCAS", "PASA"])
        self.assertEqual(result["provision_route_ids"], [
            "NER-BIDDING-V254-2026-09-04",
            "NER-DISPATCH-V254-2026-09-04",
            "NER-FCAS-CURRENT-2026-08-29",
            "NER-PASA-AVAILABILITY-CURRENT-2026-08-29",
        ])

    def test_fcas_and_pasa_together_do_not_imply_bidding_and_dispatch(self):
        result = self.route("What must a NEM generator do for FCAS and PASA today?")
        self.assertCountEqual(result["activity_candidates"], ["FCAS", "PASA"])
        self.assertEqual(result["provision_route_ids"], [
            "NER-FCAS-CURRENT-2026-08-29", "NER-PASA-AVAILABILITY-CURRENT-2026-08-29",
        ])

    def test_explicit_fcas_and_pasa_activity_remains_supported(self):
        for activity, route in (
            ("FCAS", "NER-FCAS-CURRENT-2026-08-29"),
            ("PASA", "NER-PASA-AVAILABILITY-CURRENT-2026-08-29"),
        ):
            with self.subTest(activity=activity):
                result = self.route(
                    "What must we do today?", jurisdiction="National Electricity Market",
                    actor="generator", activity=activity,
                )
                self.assertEqual(result["route_state"], "routed")
                self.assertEqual(result["activity_candidates"], [activity])
                self.assertEqual(result["provision_route_ids"], [route])

    def test_unknown_jurisdiction_remains_unresolved(self):
        for question in (
            "A retailer plans to disconnect a life-support customer tomorrow. Can it proceed?",
            "What must a generator do for FCAS today?",
            "What must a generator do for PASA today?",
        ):
            with self.subTest(question=question):
                result = self.route(question)
                self.assertEqual(result["jurisdiction_candidates"], [])
                self.assertEqual(result["route_state"], "needs-applicability-input")
                self.assertIn("jurisdiction", result["missing_material_inputs"])
                self.assertEqual(result["provision_route_ids"], [])
                self.assertTrue(result["requires_live_version_check"])


if __name__ == "__main__":
    unittest.main()
