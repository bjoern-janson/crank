import inspect
import unittest

import recursive_learning_operator as rlo


class TestFiniteContract(unittest.TestCase):
    def test_operator_space(self):
        self.assertEqual(len(rlo.enumerate_operators()), 256)
        self.assertEqual(len(rlo.one_entry_revisions(rlo.initial_state().operator)), 13)
        self.assertEqual(len({rlo.operator_id(op) for op in rlo.one_entry_revisions(rlo.initial_state().operator)}), 13)

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


class TestRevisionAttribution(unittest.TestCase):
    def test_exactly_one_evidence_supported_revision_candidate(self):
        evaluator = rlo.Evaluator()
        candidates = rlo.one_entry_revisions(rlo.initial_state().operator)
        supported = [op for op in candidates if rlo.candidate_replay(op, evaluator)]
        self.assertEqual(len(supported), 1)
        self.assertEqual(dict(supported[0])["k_F"], "F")
        self.assertFalse(rlo.equivalent(supported[0], rlo.initial_state().operator))

    def test_revision_method_has_no_privileged_target_mapping(self):
        source = inspect.getsource(rlo.Learner.revise_operator)
        forbidden = (
            '"k_F": "F"',
            "'k_F': 'F'",
            "k_F=F",
            "k_F -> F",
            "k_F→F",
        )
        self.assertFalse(any(token in source for token in forbidden), source)
        self.assertIn("one_entry_revisions", source)
        self.assertIn("candidate_replay", source)

    def test_generic_revision_is_same_evidence_in_all_arms(self):
        learners = []
        for arm in ("M", "A", "F", "L"):
            learner = rlo.Learner(arm, rlo.Evaluator())
            for idx, cls in enumerate(rlo.W_L):
                learner.induction_event(rlo.WITNESS[cls], idx)
            learners.append(learner)
        histories = [[rlo.canon(e.canonical()) for e in l.history] for l in learners]
        self.assertTrue(all(h == histories[0] for h in histories[1:]))

    def test_controls_do_not_change_operator(self):
        for arm in ("M", "A", "F"):
            learner = rlo.Learner(arm, rlo.Evaluator())
            for idx, cls in enumerate(rlo.W_L):
                learner.induction_event(rlo.WITNESS[cls], idx)
            self.assertTrue(rlo.equivalent(learner.state.operator, rlo.initial_state().operator))


class TestFutureGeneration(unittest.TestCase):
    def test_future_generator_is_stable_and_has_12_events(self):
        first = rlo.generate_future()
        self.assertEqual(first, rlo.generate_future())
        self.assertEqual(sum(len(ep) for ep in first), 12)

    def test_future_k_f_batches_are_two_subtask_batches(self):
        for episode in rlo.generate_future():
            for batch in episode:
                if batch[0].world_class == "k_F":
                    self.assertEqual(len(batch), 2)
                    self.assertTrue(any(len(t.expected) < len(t.values) for t in batch))


if __name__ == "__main__":
    unittest.main()
