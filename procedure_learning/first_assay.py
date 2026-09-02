"""First CRANK-IL causal procedure-learning assay.

This is an experiment runner, not a new learning architecture.  It compares a
frozen same-evidence procedural shadow against an induced treatment under one
fixed frame and one fixed execution contract.
"""

from dataclasses import dataclass
import hashlib
from typing import Iterable, Tuple

from .frame_spec import FrameSpec, Primitive
from .hypothesis_space import HypothesisSpace
from .procedure import Procedure, ExecutionTrace, execute
from .procedure_inducer import ProcedureInducer, TrainingExample
from .procedure_shadow import SameEvidenceShadow
from .procedure_test import ExecutionContract, ProcedureTest, TestResult, ReachCertificate


FRAME = FrameSpec(
    "crank-il-first-assay-f0",
    (Primitive.IDENTITY, Primitive.REVERSE, Primitive.SORT_ASC),
    1,
)
SPACE = HypothesisSpace(FRAME)
BASE_PROCEDURE = Procedure((Primitive.REVERSE,))
CONTRACT = ExecutionContract(
    "crank-il-sequence-v1",
    "theta-frozen-v1",
    "budget-small-v1",
)
EVIDENCE = (
    TrainingExample("h1", (3, 1, 2), (1, 2, 3)),
    TrainingExample("h2", (8, 5, 7), (5, 7, 8)),
)
HELDOUT_SEED = "crank-il-first-assay-heldout-v1"
HELDOUT_COUNT = 6


@dataclass(frozen=True)
class HeldOutTask:
    task_id: str
    input_value: Tuple[int, ...]
    expected_output: Tuple[int, ...]


def _bytes(seed: str) -> bytes:
    return hashlib.sha256(seed.encode("utf-8")).digest()


def generate_heldout_tasks(seed: str = HELDOUT_SEED, count: int = HELDOUT_COUNT) -> Tuple[HeldOutTask, ...]:
    """Generate T* independently from induction state and after induction.

    The generator is independent of the inducer and candidate procedure.  It
    produces length-5 inputs with values in 10..99, disjoint from H's values.
    Monotone/reverse-monotone inputs are rejected so reverse cannot accidentally
    coincide with the sorting target.
    """
    tasks = []
    nonce = 0
    while len(tasks) < count:
        digest = _bytes(f"{seed}:{nonce}")
        values = tuple(10 + (digest[i] % 90) for i in range(5))
        if len(set(values)) < 5:
            nonce += 1
            continue
        expected = tuple(sorted(values))
        if tuple(reversed(values)) == expected:
            nonce += 1
            continue
        task_id = hashlib.sha256(
            f"{seed}:task:{nonce}:{','.join(map(str, values))}".encode("utf-8")
        ).hexdigest()[:16]
        tasks.append(HeldOutTask(task_id, values, expected))
        nonce += 1
    return tuple(tasks)


def memorization_template(evidence: Iterable[TrainingExample], value: Tuple[int, ...]) -> Tuple[int, ...] | None:
    """Exact-example memorization control; no interpolation is permitted."""
    for example in evidence:
        if tuple(value) == example.input_value:
            return example.expected_output
    return None


def exhaustive_search_control(
    space: HypothesisSpace, evidence: Iterable[TrainingExample]
) -> Procedure | None:
    """Existing-search comparator: synthesize once from H without a base-state update."""
    examples = tuple(evidence)
    for candidate in space.enumerate():
        if all(execute(candidate, e.input_value).output_value == e.expected_output for e in examples):
            return candidate
    return None


def run_assay() -> dict:
    """Run the predeclared assay in causal order."""
    inducer = ProcedureInducer(SPACE)
    induction = inducer.induce(BASE_PROCEDURE, EVIDENCE)
    if induction.candidate is None:
        raise AssertionError("predeclared curriculum must induce a candidate")

    # T* is generated only after induction and via an independent mechanism.
    heldout = generate_heldout_tasks()
    shadow = SameEvidenceShadow(BASE_PROCEDURE)
    shadow_obs = shadow.run(EVIDENCE, (task.input_value for task in heldout))

    tester = ProcedureTest(CONTRACT)
    treatment_results = tester.run(
        induction.candidate,
        ((t.task_id, t.input_value, t.expected_output) for t in heldout),
    )
    shadow_results = tester.run(
        BASE_PROCEDURE,
        ((t.task_id, t.input_value, t.expected_output) for t in heldout),
    )
    r0 = tuple(r.task_id for r in shadow_results if r.passed)
    r1 = tuple(r.task_id for r in treatment_results if r.passed)
    delta_plus = tuple(sorted(set(r1) - set(r0)))
    delta_minus = tuple(sorted(set(r0) - set(r1)))

    search_candidate = exhaustive_search_control(SPACE, EVIDENCE)
    search_results = tester.run(
        search_candidate,
        ((t.task_id, t.input_value, t.expected_output) for t in heldout),
    ) if search_candidate is not None else ()
    memo_reach = tuple(
        t.task_id
        for t in heldout
        if memorization_template(EVIDENCE, t.input_value) == t.expected_output
    )

    reach_certificate: ReachCertificate = tester.certificate(induction.candidate, treatment_results)
    exclusion = {
        "kind": "singleton_frozen_shadow",
        "old_space_procedure_ids": [BASE_PROCEDURE.procedure_id],
        "heldout_task_ids": [t.task_id for t in heldout],
        "all_old_space_members_fail": all(not r.passed for r in shadow_results),
    }

    traces = []
    for task in heldout:
        trace0: ExecutionTrace = execute(BASE_PROCEDURE, task.input_value)
        trace1: ExecutionTrace = execute(induction.candidate, task.input_value)
        traces.append(
            {
                "task_id": task.task_id,
                "shadow": {
                    "procedure_id": trace0.procedure_id,
                    "trace_id": trace0.trace_id,
                    "input": list(trace0.input_value),
                    "steps": [[name, list(value)] for name, value in trace0.steps],
                    "output": list(trace0.output_value),
                },
                "treatment": {
                    "procedure_id": trace1.procedure_id,
                    "trace_id": trace1.trace_id,
                    "input": list(trace1.input_value),
                    "steps": [[name, list(value)] for name, value in trace1.steps],
                    "output": list(trace1.output_value),
                },
            }
        )

    return {
        "experiment": "crank-il-first-assay-v1",
        "frame": {
            "frame_id": FRAME.frame_id,
            "allowed_primitives": [p.value for p in FRAME.allowed_primitives],
            "max_program_length": FRAME.max_program_length,
            "hypothesis_count": len(SPACE),
        },
        "causal_intervention": {
            "evidence": [[e.example_id, list(e.input_value), list(e.expected_output)] for e in EVIDENCE],
            "theta_id": CONTRACT.theta_id,
            "budget_id": CONTRACT.budget_id,
            "test_family_seed": HELDOUT_SEED,
            "heldout_generated_after_induction": True,
            "only_procedural_update_permission_differs": True,
        },
        "base": {
            "program": list(BASE_PROCEDURE.canonical_program()),
            "procedure_id": BASE_PROCEDURE.procedure_id,
        },
        "induction": {
            "base_procedure_id": induction.base_procedure_id,
            "candidate_program": list(induction.candidate.canonical_program()),
            "candidate_procedure_id": induction.candidate.procedure_id,
            "tested_hypotheses": induction.tested_hypotheses,
        },
        "heldout_tasks": [
            {"task_id": t.task_id, "input": list(t.input_value), "expected": list(t.expected_output)}
            for t in heldout
        ],
        "results": {
            "R0": list(r0),
            "R1": list(r1),
            "delta_R_plus": list(delta_plus),
            "delta_R_minus": list(delta_minus),
        },
        "identities": {
            "shadow_observation_trace_ids": list(shadow_obs.trace_ids),
            "treatment_reach_certificate_id": reach_certificate.certificate_id,
            "treatment_trace_ids": [r.trace_id for r in treatment_results],
            "treatment_test_contract_id": CONTRACT.contract_id,
        },
        "old_space_exclusion": exclusion,
        "controls": {
            "memorization_template_R": list(memo_reach),
            "exhaustive_search_procedure_id": search_candidate.procedure_id if search_candidate else None,
            "exhaustive_search_R": [r.task_id for r in search_results if r.passed],
        },
        "programs_and_traces": traces,
        "success_criterion": "delta_R_plus_nonempty",
        "observed_success": bool(delta_plus),
    }
