"""Tests for the CRANK Layer-0 experimental atom."""

import unittest

from phenomenon_probe import ProbeEnvironment, is_valid_path
from trial_contract import (
    ExecutionUsage,
    ModelConfig,
    ResourceBudget,
    build_factorial_assignment,
    build_trial,
    context_spec,
    make_observation,
    make_default_task,
    validate_execution_usage,
)


class TrialContractTests(unittest.TestCase):
    def setUp(self):
        self.model = ModelConfig(
            provider="test-provider",
            model_identifier="test-model",
            model_version="test-version",
            system_instructions="fixed-system-v0.1",
            decoding={"temperature": 0.0, "top_p": 1.0},
            tool_settings={"tools_enabled": False},
            reasoning_settings={"budget": "fixed"},
            session_policy="fresh_independent_trial",
        )
        self.budget = ResourceBudget(
            max_input_tokens=512,
            max_output_tokens=64,
            max_turns=1,
            max_tool_calls=0,
            latency_limit_ms=30000,
            sampling={"n": 1, "seed": "external-assignment"},
        )
        self.usage = ExecutionUsage(100, 20, 1, 0, 1000)

    def test_contexts_are_first_class_and_not_procedural(self):
        c0 = context_spec("C0")
        c1 = context_spec("C1")
        self.assertEqual(len(c0.text), c0.declared_length_chars)
        self.assertEqual(len(c1.text), c1.declared_length_chars)
        self.assertNotIn("check format", c0.text.lower())
        self.assertNotIn("A->B", c1.text)
        self.assertNotIn("S,C,D,G", c1.text)
        self.assertNotIn("S,E,F,G", c1.text)
        self.assertNotIn("alternative", c1.text.lower())

    def test_task_state_is_explicit(self):
        task = make_default_task()
        self.assertEqual(task.task_id, "routing-v0.1")
        self.assertEqual(task.initial_node, "S")
        self.assertEqual(task.target_node, "G")
        self.assertIn(("A", "B"), task.graph_edges)

    def test_intervention_changes_model_visible_environment(self):
        e0 = build_trial(context_id="C0", intervention_id="e0", assignment_seed=1, model_config=self.model, budget=self.budget)
        e1 = build_trial(context_id="C0", intervention_id="e1", assignment_seed=1, model_config=self.model, budget=self.budget)
        self.assertNotEqual(e0.visible_environment.edges, e1.visible_environment.edges)
        self.assertNotEqual(e0.rendered_input(), e1.rendered_input())
        self.assertNotEqual(e0.input_hash(), e1.input_hash())
        self.assertEqual(e0.visible_environment.edges, e0.evaluator.environment_edges)
        self.assertEqual(e1.visible_environment.edges, e1.evaluator.environment_edges)
        rendered = e1.rendered_input()
        self.assertIn("current_environment", rendered)
        self.assertNotIn("A-to-B", rendered)
        self.assertNotIn("The A-to-B transition is unavailable", rendered)
        self.assertNotIn("S,C,D,G", rendered)
        self.assertNotIn("S,E,F,G", rendered)

    def test_intervention_is_not_an_edge_specific_textual_cue(self):
        trial = build_trial(
            context_id="C0",
            intervention_id="e1",
            assignment_seed=1,
            model_config=self.model,
            budget=self.budget,
        )
        rendered = trial.rendered_input()
        self.assertNotIn("changed_edges", rendered)
        self.assertNotIn('"intervention_id"', rendered)
        self.assertNotIn("unavailable", rendered.lower())

    def test_same_trial_spec_has_same_ids_and_input(self):
        a = build_trial(context_id="C0", intervention_id="e0", assignment_seed=77, model_config=self.model, budget=self.budget)
        b = build_trial(context_id="C0", intervention_id="e0", assignment_seed=77, model_config=self.model, budget=self.budget)
        self.assertEqual(a.trial_id(), b.trial_id())
        self.assertEqual(a.rendered_input(), b.rendered_input())
        self.assertEqual(a.input_hash(), b.input_hash())

    def test_trial_identity_changes_when_assignment_changes_but_not_with_outcome(self):
        a = build_trial(context_id="C0", intervention_id="e0", assignment_seed=77, model_config=self.model, budget=self.budget)
        b = build_trial(context_id="C0", intervention_id="e0", assignment_seed=78, model_config=self.model, budget=self.budget)
        self.assertNotEqual(a.trial_id(), b.trial_id())
        good = make_observation(a, raw_model_output='{"implementation":["S","A","B","G"]}', execution_timestamp="2026-01-01T00:00:00Z", execution_usage=self.usage)
        bad = make_observation(a, raw_model_output='{"implementation":["S","C","D","G"]}', execution_timestamp="2026-01-01T00:00:00Z", execution_usage=self.usage)
        self.assertEqual(good.trial_id, bad.trial_id)
        self.assertNotEqual(good.observation_hash, bad.observation_hash)

    def test_execution_usage_is_custodied_and_hash_bound(self):
        trial = build_trial(context_id="C1", intervention_id="e0", assignment_seed=8, model_config=self.model, budget=self.budget)
        a = make_observation(trial, raw_model_output='{"implementation":["S","A","B","G"]}', execution_timestamp="2026-01-01T00:00:00Z", execution_usage=self.usage)
        self.assertEqual(a.execution_usage, self.usage)
        altered = ExecutionUsage(101, 20, 1, 0, 1000)
        b = make_observation(trial, raw_model_output='{"implementation":["S","A","B","G"]}', execution_timestamp="2026-01-01T00:00:00Z", execution_usage=altered)
        self.assertNotEqual(a.observation_hash, b.observation_hash)

    def test_execution_timestamp_is_metadata_only_for_observation_identity(self):
        trial = build_trial(context_id="C1", intervention_id="e0", assignment_seed=8, model_config=self.model, budget=self.budget)
        a = make_observation(trial, raw_model_output='{"implementation":["S","A","B","G"]}', execution_timestamp="2026-01-01T00:00:00Z", execution_usage=self.usage)
        b = make_observation(trial, raw_model_output='{"implementation":["S","A","B","G"]}', execution_timestamp="2026-01-01T00:01:00Z", execution_usage=self.usage)
        self.assertEqual(a.observation_hash, b.observation_hash)
        self.assertNotEqual(a.execution_timestamp, b.execution_timestamp)

    def test_raw_output_is_preserved_verbatim(self):
        trial = build_trial(context_id="C1", intervention_id="e0", assignment_seed=8, model_config=self.model, budget=self.budget)
        raw = '{"implementation":["S","A","B","G"]}\n'
        observation = make_observation(trial, raw_model_output=raw, execution_timestamp="2026-01-01T00:00:00Z", execution_usage=self.usage)
        self.assertEqual(observation.raw_model_output, raw)
        self.assertEqual(observation.rendered_input, trial.rendered_input())
        self.assertEqual(observation.parsed_implementation, ("S", "A", "B", "G"))
        self.assertTrue(observation.contract_result)
        self.assertEqual(observation.input_hash, trial.input_hash())

    def test_parse_or_evaluation_failure_does_not_rewrite_raw_observation(self):
        trial = build_trial(context_id="C0", intervention_id="e0", assignment_seed=9, model_config=self.model, budget=self.budget)
        raw = "not-json"
        observation = make_observation(trial, raw_model_output=raw, execution_timestamp="2026-01-01T00:00:00Z", execution_usage=self.usage)
        self.assertEqual(observation.raw_model_output, raw)
        self.assertIsNone(observation.parsed_implementation)
        self.assertIsNone(observation.contract_result)

    def test_over_budget_execution_cannot_become_observation(self):
        trial = build_trial(context_id="C0", intervention_id="e0", assignment_seed=10, model_config=self.model, budget=self.budget)
        with self.assertRaises(ValueError):
            make_observation(
                trial,
                raw_model_output='{"implementation":["S","A","B","G"]}',
                execution_timestamp="2026-01-01T00:00:00Z",
                execution_usage=ExecutionUsage(513, 20, 1, 0, 1000),
            )

    def test_fresh_session_policy_is_explicit(self):
        self.assertEqual(self.model.session_policy, "fresh_independent_trial")

    def test_budget_is_hard_validated(self):
        trial = build_trial(context_id="C0", intervention_id="e0", assignment_seed=5, model_config=self.model, budget=self.budget)
        validate_execution_usage(trial, ExecutionUsage(100, 20, 1, 0, 1000))
        with self.assertRaises(ValueError):
            validate_execution_usage(trial, ExecutionUsage(513, 20, 1, 0, 1000))
        with self.assertRaises(ValueError):
            validate_execution_usage(trial, ExecutionUsage(100, 65, 1, 0, 1000))
        with self.assertRaises(ValueError):
            validate_execution_usage(trial, ExecutionUsage(100, 20, 2, 0, 1000))
        with self.assertRaises(ValueError):
            validate_execution_usage(trial, ExecutionUsage(100, 20, 1, 1, 1000))

    def test_factorial_assignment_is_balanced_and_deterministic(self):
        a = build_factorial_assignment(master_seed=1234, replicates_per_cell=3, model_config=self.model, budget=self.budget)
        b = build_factorial_assignment(master_seed=1234, replicates_per_cell=3, model_config=self.model, budget=self.budget)
        self.assertEqual([x.trial_id() for x in a], [x.trial_id() for x in b])
        counts = {("C0", "e0"): 0, ("C0", "e1"): 0, ("C1", "e0"): 0, ("C1", "e1"): 0}
        for spec in a:
            counts[(spec.context.context_id, spec.intervention.intervention_id)] += 1
        self.assertEqual(set(counts.values()), {3})

    def test_frozen_evaluator_conditions_still_hold(self):
        e0 = ProbeEnvironment.baseline()
        e1 = ProbeEnvironment.perturbed()
        self.assertTrue(is_valid_path(type("I", (), {"node_sequence": ("S", "A", "B", "G")})(), e0))
        self.assertFalse(is_valid_path(type("I", (), {"node_sequence": ("S", "A", "B", "G")})(), e1))


if __name__ == "__main__":
    unittest.main()
