import unittest

import recursive_learning_operator as rlo


class TestFiniteContract(unittest.TestCase):
    def test_operator_space(self):
        self.assertEqual(len(rlo.enumerate_operators()), 256)
        self.assertEqual(len(rlo.one_entry_revisions(rlo.initial_state().operator)), 13)

    def test_witness_domains(self):
        self.assertEqual(rlo.W_L, ("k_M", "k_F", "k_M", "k_F"))
        self.assertEqual(len(rlo.WITNESS["k_M"]), 1)
        self.assertEqual(len(rlo.WITNESS["k_A"]), 2)
        self.assertEqual(len(rlo.WITNESS["k_F"]), 2)

    def test_evidence_excludes_target_and_world_class(self):
        ev = rlo.make_evidence(rlo.initial_state(), rlo.WITNESS["k_M"], 0, rlo.Evaluator(), ())
        text = rlo.canon(ev.canonical())
        self.assertNotIn("expected", text)
        self.assertNotIn("world_class", text)
        self.assertNotIn("k_F", text)

    def test_frame_only_update_keeps_selector(self):
        state = rlo.initial_state()
        updated = rlo.update(state, "F", rlo.WITNESS["k_F"], rlo.Evaluator())
        self.assertEqual(updated.frame, rlo.F_EVEN)
        self.assertEqual(updated.selector, state.selector)

    def test_operator_change_is_not_equivalent(self):
        op0 = rlo.initial_state().operator
        changed = dict(op0)
        changed["k_F"] = "F"
        op1 = tuple((k, changed[k]) for k in rlo.KEYS)
        self.assertFalse(rlo.equivalent(op0, op1))
        self.assertTrue(rlo.equivalent(op0, op0))


class TestAssayPath(unittest.TestCase):
    def _run(self, arm):
        learner = rlo.Learner(arm, rlo.Evaluator())
        for idx, cls in enumerate(rlo.W_L):
            learner.induction_event(rlo.WITNESS[cls], idx)
        if arm == "L":
            learner.revise_operator()
        return learner

    def test_same_evidence_across_arms(self):
        histories = [
            [rlo.canon(e.canonical()) for e in self._run(a).history]
            for a in ("M", "A", "F", "L")
        ]
        self.assertTrue(all(h == histories[0] for h in histories[1:]))

    def test_recursive_operator_revision(self):
        learner = self._run("L")
        self.assertEqual(learner.state.operator_map()["k_F"], "F")
        self.assertFalse(rlo.equivalent(learner.pre_revision_operator, learner.state.operator))

    def test_controls_keep_operator_frozen(self):
        for arm in ("M", "A", "F"):
            learner = self._run(arm)
            self.assertTrue(rlo.equivalent(learner.pre_revision_operator, learner.state.operator))

    def test_correction_candidate_changes_operator(self):
        learner = self._run("L")
        corrected = rlo.correction_candidate(learner.state.operator)
        self.assertEqual(dict(corrected)["k_A"], "A")
        self.assertFalse(rlo.equivalent(learner.state.operator, corrected))

    def test_future_generator_is_stable(self):
        first = rlo.generate_future()
        self.assertEqual(first, rlo.generate_future())
        self.assertEqual(sum(len(ep) for ep in first), 12)


if __name__ == "__main__":
    unittest.main()
