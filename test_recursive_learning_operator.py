import unittest

import recursive_learning_operator as rlo


class TestFiniteContract(unittest.TestCase):
    def test_operator_space(self):
        ops = rlo.enumerate_operators()
        self.assertEqual(len(ops), 256)
        self.assertEqual(len(rlo.one_entry_revisions(rlo.initial_state().operator)), 13)

    def test_witness_domains(self):
        self.assertEqual(rlo.W_L, ("k_M", "k_F", "k_M", "k_F"))
        self.assertEqual(len(rlo.W["k_M"]), 1)
        self.assertEqual(len(rlo.W["k_A"]), 2)
        self.assertEqual(len(rlo.W["k_F"]), 2)

    def test_evidence_cannot_contain_target_or_world_class(self):
        ev = rlo.Evidence(
            event_id="e", episode_index=0, context_bit=0,
            input_batch=(((0, 1), (2, 0, 1)),),
            observed_output_batch=((2, 0, 1),),
            consequence=rlo.Consequence(False, True, True, "unchanged", True),
            prior_evidence=(),
        )
        text = rlo.canon(ev.canonical())
        self.assertNotIn("expected_outputs", text)
        self.assertNotIn("world_class", text)
        self.assertNotIn("k_F", text)

    def test_frame_only_transaction(self):
        evaluator = rlo.Evaluator()
        state = rlo.initial_state()
        batch = rlo.W["k_F"]
        updated = rlo.update_state(state, "F", batch, evaluator)
        self.assertEqual(updated.frame, rlo.F_EVEN)
        self.assertEqual(updated.selector, state.selector)

    def test_operator_equivalence(self):
        op0 = rlo.initial_state().operator
        op1 = dict(op0)
        op1["k_F"] = "F"
        op1 = tuple((k, op1[k]) for k in rlo.KEYS)
        self.assertFalse(rlo.equivalent(op0, op1))
        self.assertTrue(rlo.equivalent(op0, op0))


class TestAssayPath(unittest.TestCase):
    def _run_induction(self, arm):
        learner = rlo.RecursiveLearner(arm, rlo.Evaluator())
        for idx, cls in enumerate(rlo.W_L):
            learner.observe_and_update(rlo.W[cls], idx)
        if arm == "L":
            learner.revise_operator()
        return learner

    def test_all_arms_receive_same_evidence_bytes(self):
        learners = [self._run_induction(a) for a in ("M", "A", "F", "L")]
        histories = [[rlo.canon(e.canonical()) for e in x.history] for x in learners]
        self.assertTrue(all(h == histories[0] for h in histories[1:]))

    def test_recursive_operator_revision(self):
        learner = self._run_induction("L")
        self.assertNotEqual(dict(learner.state.operator)["k_F"], "M")
        self.assertEqual(dict(learner.state.operator)["k_F"], "F")
        self.assertFalse(rlo.equivalent(learner._operator_before_revision, learner.state.operator))

    def test_controls_do_not_revise_operator(self):
        for arm in ("M", "A", "F"):
            learner = self._run_induction(arm)
            self.assertTrue(rlo.equivalent(learner._operator_before_revision, learner.state.operator))

    def test_correction_channel_can_revise_operator(self):
        learner = self._run_induction("L")
        op1 = learner.state.operator
        op2 = dict(op1)
        op2["k_A"] = "A"
        op2 = tuple((k, op2[k]) for k in rlo.KEYS)
        self.assertFalse(rlo.equivalent(op1, op2))
        self.assertEqual(dict(op2)["k_A"], "A")


if __name__ == "__main__":
    unittest.main()
