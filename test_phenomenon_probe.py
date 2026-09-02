import unittest

from corrigible_buffer_v1 import ReceiptAuthority
from observation_receipt_bridge import ExogenousEvaluator
from phenomenon_probe import (
    BASELINE_EDGES,
    PERTURBED_REMOVAL,
    ParsedImplementation,
    ProbeEnvironment,
    is_valid_path,
    observe,
    summarize_distribution,
    validate_probe_contract,
)
from trial_contract import ExecutionUsage


class IdentificationTests(unittest.TestCase):
    def test_preregistered_identification_conditions(self):
        validate_probe_contract()
        self.assertIn(PERTURBED_REMOVAL, BASELINE_EDGES)

    def test_two_valid_perturbed_implementations_are_distinct(self):
        e1 = ProbeEnvironment.perturbed()
        ia = ParsedImplementation(("S", "C", "D", "G"))
        ib = ParsedImplementation(("S", "E", "F", "G"))
        self.assertTrue(is_valid_path(ia, e1))
        self.assertTrue(is_valid_path(ib, e1))
        self.assertNotEqual(ia.node_sequence, ib.node_sequence)


class CustodyTests(unittest.TestCase):
    def test_raw_model_output_is_primary_custody_object(self):
        raw = '{"implementation":["S","C","D","G"]}\n'
        obs = observe(context_id="C0", intervention_id="e1", task_id="routing-v0.1", raw_model_output=raw, environment=ProbeEnvironment.perturbed())
        self.assertEqual(obs.raw_model_output, raw)
        self.assertEqual(obs.parsed_implementation.node_sequence, ("S", "C", "D", "G"))
        self.assertTrue(obs.evaluation.contract_result)

    def test_parse_failure_retains_raw_output_without_evaluation(self):
        raw = "not-json"
        obs = observe(context_id="C1", intervention_id="e0", task_id="routing-v0.1", raw_model_output=raw, environment=ProbeEnvironment.baseline())
        self.assertEqual(obs.raw_model_output, raw)
        self.assertIsNone(obs.parsed_implementation)
        self.assertIsNone(obs.evaluation)

    def test_distribution_summary_is_derived_after_observation(self):
        observations = [
            observe(context_id="C0", intervention_id="e1", task_id="routing-v0.1", raw_model_output='{"implementation":["S","C","D","G"]}', environment=ProbeEnvironment.perturbed()),
            observe(context_id="C0", intervention_id="e1", task_id="routing-v0.1", raw_model_output='{"implementation":["S","E","F","G"]}', environment=ProbeEnvironment.perturbed()),
        ]
        counts = summarize_distribution(observations)
        self.assertEqual(sum(counts.values()), 2)
        self.assertEqual(len(counts), 2)


class EvidenceBridgeTests(unittest.TestCase):
    def _observation(self, raw):
        return observe(
            context_id="C0",
            intervention_id="e1",
            task_id="routing-v0.1",
            raw_model_output=raw,
            environment=ProbeEnvironment.perturbed(),
        )

    def test_validated_output_can_become_buffer_compatible_receipt(self):
        raw = '{"implementation":["S","C","D","G"]}'
        obs = self._observation(raw)
        evaluator = ExogenousEvaluator(ProbeEnvironment.perturbed())
        validated = evaluator.validate("obs-r1", obs)
        authority = ReceiptAuthority()
        receipt = evaluator.to_buffer_receipt(validated, authority, "c1")
        self.assertEqual(receipt.validates_claim_id, "c1")
        self.assertEqual(receipt.tool_name, "phenomenon_probe_evaluator")
        self.assertEqual(receipt.output_summary, raw)

    def test_invalid_external_evaluation_cannot_become_receipt(self):
        obs = self._observation('{"implementation":["S","A","B","G"]}')
        self.assertFalse(obs.evaluation.contract_result)
        with self.assertRaises(ValueError):
            ExogenousEvaluator(ProbeEnvironment.perturbed()).validate("obs-r2", obs)

    def test_recomputation_ignores_forged_success_fields(self):
        obs = self._observation('{"implementation":["S","A","B","G"]}')
        forged = type(obs)(
            context_id=obs.context_id,
            intervention_id=obs.intervention_id,
            task_id=obs.task_id,
            raw_model_output=obs.raw_model_output,
            parsed_implementation=ParsedImplementation(("S", "C", "D", "G")),
            evaluation=type("ForgedEval", (), {
                "task_id": obs.task_id,
                "environment_id": "E_1",
                "implementation": ParsedImplementation(("S", "C", "D", "G")),
                "contract_result": True,
                "objective": "forged",
            })(),
        )
        with self.assertRaises(ValueError):
            ExogenousEvaluator(ProbeEnvironment.perturbed()).validate("obs-r-forged", forged)

    def test_second_evaluator_cannot_substitute_for_first(self):
        obs = self._observation('{"implementation":["S","C","D","G"]}')
        evaluator_a = ExogenousEvaluator(ProbeEnvironment.perturbed())
        evaluator_b = ExogenousEvaluator(ProbeEnvironment.perturbed())
        validated = evaluator_a.validate("obs-r3", obs)
        authority = ReceiptAuthority()
        with self.assertRaises(ValueError):
            evaluator_b.to_buffer_receipt(validated, authority, "c1")


if __name__ == "__main__":
    unittest.main()
