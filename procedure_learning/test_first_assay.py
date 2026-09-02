import json
import unittest

from .first_assay import (
    BASE_PROCEDURE,
    EVIDENCE,
    FRAME,
    HELDOUT_COUNT,
    SPACE,
    generate_heldout_tasks,
    run_assay,
)
from .procedure import execute, Procedure
from .procedure_inducer import ProcedureInducer


class FirstAssayTests(unittest.TestCase):
    def test_declared_contract_is_exact(self):
        self.assertEqual(FRAME.frame_id, "crank-il-first-assay-f0")
        self.assertEqual(tuple(p.value for p in FRAME.allowed_primitives), ("identity", "reverse", "sort_asc"))
        self.assertEqual(FRAME.max_program_length, 1)
        self.assertEqual(len(SPACE), 4)
        self.assertEqual(BASE_PROCEDURE.canonical_program(), ("reverse",))
        self.assertEqual(len(EVIDENCE), 2)

    def test_induction_precedes_independent_heldout_generation(self):
        result = ProcedureInducer(SPACE).induce(BASE_PROCEDURE, EVIDENCE)
        self.assertIsNotNone(result.candidate)
        self.assertEqual(result.candidate.canonical_program(), ("sort_asc",))
        tasks = generate_heldout_tasks()
        self.assertEqual(len(tasks), HELDOUT_COUNT)
        self.assertTrue(all(len(t.input_value) == 5 for t in tasks))
        self.assertTrue(all(all(10 <= x <= 99 for x in t.input_value) for t in tasks))
        self.assertTrue(all(t.expected_output == tuple(sorted(t.input_value)) for t in tasks))
        self.assertTrue(all(tuple(reversed(t.input_value)) != t.expected_output for t in tasks))

    def test_assay_success_criterion_and_controls(self):
        result = run_assay()
        self.assertTrue(result["observed_success"])
        self.assertNotEqual(result["base"]["procedure_id"], result["induction"]["candidate_procedure_id"])
        self.assertEqual(result["results"]["delta_R_minus"], [])
        self.assertEqual(set(result["results"]["delta_R_plus"]), set(result["results"]["R1"]))
        self.assertEqual(result["controls"]["memorization_template_R"], [])
        self.assertEqual(result["controls"]["exhaustive_search_R"], result["results"]["R1"])
        self.assertTrue(result["old_space_exclusion"]["all_old_space_members_fail"])
        self.assertEqual(len(result["programs_and_traces"]), HELDOUT_COUNT)
        self.assertTrue(all(item["shadow"]["trace_id"] != item["treatment"]["trace_id"] for item in result["programs_and_traces"]))

    def test_shadow_is_frozen_and_old_space_is_singleton(self):
        result = run_assay()
        self.assertEqual(result["old_space_exclusion"]["old_space_procedure_ids"], [BASE_PROCEDURE.procedure_id])
        self.assertEqual(result["old_space_exclusion"]["heldout_task_ids"], [t.task_id for t in generate_heldout_tasks()])


if __name__ == "__main__":
    unittest.main()
