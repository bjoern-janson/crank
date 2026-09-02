import unittest

from .frame_spec import FrameSpec, Primitive
from .hypothesis_space import HypothesisSpace
from .procedure import Procedure, execute
from .procedure_inducer import ProcedureInducer, TrainingExample
from .procedure_shadow import SameEvidenceShadow
from .procedure_test import ExecutionContract, ProcedureTest


FRAME = FrameSpec(
    "toy-sequence-v1",
    (Primitive.IDENTITY, Primitive.REVERSE, Primitive.SORT_ASC),
    2,
)
SPACE = HypothesisSpace(FRAME)
CONTRACT = ExecutionContract("toy-interface-v1", "theta-test", "budget-small")


class FrameAndSpaceTests(unittest.TestCase):
    def test_space_is_finite_and_frame_bounded(self):
        self.assertEqual(len(SPACE), 1 + 3 + 9)
        self.assertTrue(SPACE.contains(Procedure((Primitive.REVERSE, Primitive.SORT_ASC))))
        self.assertFalse(SPACE.contains(Procedure((Primitive.REVERSE,) * 3)))
        self.assertFalse(SPACE.contains(Procedure((Primitive.KEEP_EVEN,))))
        self.assertEqual(sum(1 for _ in SPACE.enumerate()), len(SPACE))


class ProcedureIdentityTests(unittest.TestCase):
    def test_canonical_procedure_id_is_stable(self):
        a = Procedure((Primitive.REVERSE, Primitive.SORT_ASC))
        b = Procedure((Primitive.REVERSE, Primitive.SORT_ASC))
        self.assertEqual(a.procedure_id, b.procedure_id)
        self.assertNotEqual(a.procedure_id, Procedure((Primitive.SORT_ASC, Primitive.REVERSE)).procedure_id)

    def test_trace_identity_is_separate_from_procedure_identity(self):
        p = Procedure((Primitive.REVERSE,))
        trace = execute(p, (1, 2, 3))
        self.assertEqual(trace.procedure_id, p.procedure_id)
        self.assertNotEqual(trace.trace_id, p.procedure_id)

    def test_execution_preserves_input_for_trace(self):
        values = (3, 1, 2)
        trace = execute(Procedure((Primitive.SORT_ASC,)), values)
        self.assertEqual(trace.input_value, values)
        self.assertEqual(trace.output_value, (1, 2, 3))


class InductionTests(unittest.TestCase):
    def test_exhaustive_induction_finds_exact_fit(self):
        evidence = (
            TrainingExample("e1", (3, 1, 2), (1, 2, 3)),
            TrainingExample("e2", (5, 4), (4, 5)),
        )
        result = ProcedureInducer(SPACE).induce(evidence)
        self.assertIsNotNone(result.candidate)
        self.assertEqual(result.candidate.program, (Primitive.SORT_ASC,))
        self.assertLessEqual(result.tested_hypotheses, len(SPACE))

    def test_no_fit_is_explicit(self):
        evidence = (TrainingExample("e1", (1, 2), (9, 9)),)
        result = ProcedureInducer(SPACE).induce(evidence)
        self.assertIsNone(result.candidate)
        self.assertEqual(result.tested_hypotheses, len(SPACE))


class ShadowTests(unittest.TestCase):
    def test_same_evidence_shadow_does_not_revise(self):
        shadow = SameEvidenceShadow(Procedure((Primitive.REVERSE,)))
        evidence = (TrainingExample("e1", (1, 2), (2, 1)),)
        observed = shadow.run(evidence, ((1, 2),))
        self.assertEqual(observed.procedure_id, shadow.procedure.procedure_id)
        with self.assertRaises(RuntimeError):
            shadow.revised(evidence)


class TestAndReachTests(unittest.TestCase):
    def test_retain_requires_all_declared_tests_to_pass(self):
        tester = ProcedureTest(CONTRACT)
        p = Procedure((Primitive.SORT_ASC,))
        passing = tester.run(p, (("t1", (3, 1), (1, 3)), ("t2", (2, 1), (1, 2))))
        failing = tester.run(p, (("t1", (3, 1), (1, 3)), ("t3", (2, 1), (9, 9))))
        self.assertTrue(tester.retain(passing))
        self.assertFalse(tester.retain(failing))

    def test_reach_certificate_binds_task_set_and_contract(self):
        tester = ProcedureTest(CONTRACT)
        p = Procedure((Primitive.SORT_ASC,))
        results = tester.run(p, (("t1", (3, 1), (1, 3)), ("t2", (2, 5), (2, 5))))
        certificate = tester.certificate(p, results)
        self.assertEqual(certificate.reachable_task_ids, ("t1", "t2"))
        self.assertEqual(certificate.procedure_id, p.procedure_id)
        self.assertEqual(certificate.execution_contract_id, CONTRACT.contract_id)
        self.assertTrue(certificate.certificate_id)

    def test_same_procedure_and_tasks_have_same_reach_identity(self):
        tester = ProcedureTest(CONTRACT)
        p1 = Procedure((Primitive.SORT_ASC,))
        p2 = Procedure((Primitive.SORT_ASC,))
        tasks = (("t1", (3, 1), (1, 3)),)
        self.assertEqual(tester.certificate(p1, tester.run(p1, tasks)), tester.certificate(p2, tester.run(p2, tasks)))


if __name__ == "__main__":
    unittest.main()
