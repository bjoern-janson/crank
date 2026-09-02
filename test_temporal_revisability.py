import json, hashlib
from pathlib import Path
import unittest
from authority_adapter import AdmissibleSpace
from revisable_adaptive_mechanism import RevisableMechanism, RevisableState, Experience
from sequence_environment import SequencedEnvironment

ROOT=Path(__file__).resolve().parent
PREREG='TEMPORAL_REVISABILITY_PREREGISTRATION.json'
SNAP='FROZEN_TEMPORAL_CORE_SNAPSHOT_SHA256.txt'
RESULT='TEMPORAL_REVISABILITY_RESULTS.json'


class FrozenBaselineTests(unittest.TestCase):
    def test_snapshot_matches(self):
        expected={}
        for line in (ROOT/SNAP).read_text().splitlines():
            if line.strip():
                d,n=line.split('  ',1); expected[n]=d
        for n,d in expected.items():
            self.assertEqual(hashlib.sha256((ROOT/n).read_bytes()).hexdigest(),d,n)


class PreregTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.spec=json.loads((ROOT/PREREG).read_text())
    def test_sequence_and_rule(self):
        self.assertEqual(self.spec['priority'],['a_tool','z_fallback'])
        self.assertEqual(self.spec['initial_state'],{'a_tool':0,'z_fallback':0})
        self.assertEqual(self.spec['experience_sequence'],[
            ['a_tool','attempt_failed'],
            ['z_fallback','attempt_failed'],
            ['a_tool','fallback_completed']])
    def test_fixed_admissibility(self):
        self.assertEqual(self.spec['admissible_actions'],['a_tool','z_fallback'])


class RevisabilityTests(unittest.TestCase):
    def test_conflicting_sequence_is_revisable(self):
        mech=RevisableMechanism(); A=AdmissibleSpace(('a_tool','z_fallback'),())
        env=SequencedEnvironment({0:{'a_tool':'attempt_failed','z_fallback':'fallback_completed'},
                                  1:{'a_tool':'attempt_failed','z_fallback':'attempt_failed'},
                                  2:{'a_tool':'fallback_completed','z_fallback':'attempt_failed'}})
        q0=RevisableState.initial(('a_tool','z_fallback'))
        b0=mech.choose(A,q0); e0=env.consequence(0,b0); q1=q0.update(Experience(b0,e0))
        b1=mech.choose(A,q1); e1=env.consequence(1,b1); q2=q1.update(Experience(b1,e1))
        b2=mech.choose(A,q2); e2=env.consequence(2,b2); q3=q2.update(Experience(b2,e2))
        self.assertEqual((b0,e0),('a_tool','attempt_failed'))
        self.assertEqual((b1,e1),('z_fallback','attempt_failed'))
        self.assertEqual((b2,e2),('a_tool','fallback_completed'))
        self.assertEqual(q1.scores,(('a_tool',1),('z_fallback',0)))
        self.assertEqual(q2.scores,(('a_tool',1),('z_fallback',1)))
        self.assertEqual(q3.scores,(('a_tool',0),('z_fallback',1)))
        self.assertEqual(q3.score_for('a_tool'),0)
        self.assertEqual(q0.score_for('a_tool'),0)

    def test_frozen_result_artifact_matches_observed_sequence(self):
        expected = {
            'sequence': [
                {'t':0,'behavior':'a_tool','experience':'attempt_failed','state':[['a_tool',0],['z_fallback',0]]},
                {'t':1,'behavior':'z_fallback','experience':'attempt_failed','state':[['a_tool',1],['z_fallback',0]]},
                {'t':2,'behavior':'a_tool','experience':'fallback_completed','state':[['a_tool',1],['z_fallback',1]]},
                {'t':3,'behavior':'a_tool','state':[['a_tool',0],['z_fallback',1]]},
            ],
            'admissibility_constant': True,
        }
        self.assertEqual(json.loads((ROOT/RESULT).read_text()), expected)

    def test_same_admissibility_different_state_different_behavior(self):
        mech=RevisableMechanism(); A=AdmissibleSpace(('a_tool','z_fallback'),())
        q_clean=RevisableState.initial(('a_tool','z_fallback'))
        q_after_failure=q_clean.update(Experience('a_tool','attempt_failed'))
        q_after_both=q_after_failure.update(Experience('z_fallback','attempt_failed'))
        self.assertEqual(A,A)
        self.assertNotEqual(q_clean,q_after_failure)
        self.assertNotEqual(q_after_failure,q_after_both)
        self.assertEqual(mech.choose(A,q_clean),'a_tool')
        self.assertEqual(mech.choose(A,q_after_failure),'z_fallback')
        self.assertEqual(mech.choose(A,q_after_both),'a_tool')

    def test_reset_restores_initial_behavior(self):
        mech=RevisableMechanism(); A=AdmissibleSpace(('a_tool','z_fallback'),())
        q0=RevisableState.initial(('a_tool','z_fallback'))
        q1=q0.update(Experience('a_tool','attempt_failed'))
        q2=q1.update(Experience('a_tool','fallback_completed'))
        self.assertNotEqual(mech.choose(A,q0),mech.choose(A,q1))
        self.assertEqual(q2,q0)
        self.assertEqual(mech.choose(A,q2),mech.choose(A,q0))

    def test_zero_or_unknown_evidence_does_not_silently_revise(self):
        mech=RevisableMechanism(); A=AdmissibleSpace(('a_tool','z_fallback'),())
        q0=RevisableState.initial(('a_tool','z_fallback'))
        with self.assertRaises(ValueError): q0.update(Experience('a_tool','unknown'))
        self.assertEqual(q0,RevisableState.initial(('a_tool','z_fallback')))


if __name__=='__main__':
    unittest.main()
