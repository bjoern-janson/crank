"""Finite, deterministic CRANK recursive learning-operator assay kernel.

This module is intentionally self-contained and touches no existing CRANK
experiment.  It implements the v0.1 finite DSL, black-box consequence
interface, learner diagnosis/update path, operator revision, future
curriculum, and independent correction channel.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import product
import json
from typing import Callable, Iterable, Literal, Mapping, Sequence

Loci = Literal["M", "A", "F", "L"]
Classes = Literal["k_M", "k_A", "k_F", "k_L"]

LOCI: tuple[Loci, ...] = ("M", "A", "F", "L")
KEYS: tuple[Classes, ...] = ("k_M", "k_A", "k_F", "k_L")
SEED_INDUCTION = "crank-rlo-v0.1/induction/v1"
SEED_FUTURE = "crank-rlo-v0.1/future/v1"
SEED_CORRECTION = "crank-rlo-v0.1/correction/v1"


def canon(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: object) -> str:
    return sha256(canon(value).encode("utf-8")).hexdigest()


def blocks(seed: str) -> Iterable[bytes]:
    raw = seed.encode("utf-8")
    i = 0
    while True:
        yield sha256(raw + b":" + str(i).encode("ascii")).digest()
        i += 1


def primitive(name: str, x: tuple[int, ...]) -> tuple[int, ...]:
    if name == "identity":
        return x
    if name == "reverse":
        return tuple(reversed(x))
    if name == "sort_asc":
        return tuple(sorted(x))
    if name == "keep_even_values":
        return tuple(v for v in x if v % 2 == 0)
    if name == "keep_odd_values":
        return tuple(v for v in x if v % 2 == 1)
    raise ValueError(f"unknown primitive: {name}")


@dataclass(frozen=True)
class Task:
    context_bit: int
    values: tuple[int, ...]
    expected: tuple[int, ...]
    world_class: Classes
    task_id: str


@dataclass(frozen=True)
class Consequence:
    success: bool
    lengths_preserved: bool
    value_membership_valid: bool
    order_relation: str
    context_consistency: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "success": self.success,
            "lengths_preserved": self.lengths_preserved,
            "value_membership_valid": self.value_membership_valid,
            "order_relation": self.order_relation,
            "context_consistency": self.context_consistency,
        }


@dataclass(frozen=True)
class Evidence:
    event_id: str
    episode_index: int
    context_bit: int
    input_batch: tuple[tuple[int, tuple[int, ...]], ...]
    observed_output_batch: tuple[tuple[int, ...], ...]
    consequence: Consequence
    prior_evidence: tuple[str, ...]

    def canonical(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "episode_index": self.episode_index,
            "context_bit": self.context_bit,
            "input_batch": [[[c, list(x)] for c, x in self.input_batch]],
            "observed_output_batch": [list(x) for x in self.observed_output_batch],
            "consequence": self.consequence.as_dict(),
            "prior_evidence": list(self.prior_evidence),
        }


@dataclass(frozen=True)
class State:
    frame: tuple[str, ...]
    selector: str
    memory: tuple[tuple[tuple[int, tuple[int, ...]], tuple[int, ...]], ...]
    operator: tuple[tuple[Classes, Loci], ...]

    def memory_map(self) -> dict[tuple[int, tuple[int, ...]], tuple[int, ...]]:
        return dict(self.memory)

    def operator_map(self) -> dict[Classes, Loci]:
        return dict(self.operator)


@dataclass(frozen=True)
class Outcome:
    outputs: tuple[tuple[int, ...], ...]
    consequence: Consequence


class Evaluator:
    """Independent evaluator: stores targets, exposes only finite predicates."""

    @staticmethod
    def _order_relation(observed: Sequence[int], target: Sequence[int]) -> str:
        if tuple(observed) == tuple(target):
            if all(observed[i] <= observed[i + 1] for i in range(len(observed) - 1)):
                return "nondecreasing"
            return "unchanged"
        if tuple(observed) == tuple(reversed(target)):
            return "reversed"
        if all(observed[i] <= observed[i + 1] for i in range(len(observed) - 1)):
            return "nondecreasing"
        return "other"

    def evaluate(self, batch: Sequence[Task], outputs: Sequence[tuple[int, ...]]) -> Consequence:
        if len(batch) != len(outputs):
            raise ValueError("batch/output cardinality mismatch")
        successes = []
        length_ok = []
        membership_ok = []
        context_ok = []
        relations = []
        for task, output in zip(batch, outputs):
            successes.append(tuple(output) == task.expected)
            length_ok.append(len(output) == len(task.expected))
            membership_ok.append(all(v in task.values for v in output))
            relations.append(self._order_relation(output, task.expected))
            # This is an observed evaluator predicate, not a target or class token.
            if task.world_class == "k_A":
                context_ok.append((task.context_bit == 0 and output == task.expected) or
                                  (task.context_bit == 1 and output == task.expected))
            else:
                context_ok.append(True)
        return Consequence(
            success=all(successes),
            lengths_preserved=all(length_ok),
            value_membership_valid=all(membership_ok),
            order_relation=relations[0] if len(set(relations)) == 1 else "other",
            context_consistency=all(context_ok) and not (len(batch) == 2 and not all(successes) and batch[0].context_bit != batch[1].context_bit),
        )


F0 = ("identity", "reverse", "sort_asc")
F_EVEN = F0 + ("keep_even_values",)
F_ODD = F0 + ("keep_odd_values",)


def frame_space(frame: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(frame, key=("identity", "reverse", "sort_asc", "keep_even_values", "keep_odd_values").index))


def selector_apply(selector: str, context: int, values: tuple[int, ...], frame: tuple[str, ...]) -> tuple[int, ...]:
    if selector == "always_identity":
        proc = "identity"
    elif selector == "always_reverse":
        proc = "reverse"
    elif selector == "select_on_c":
        proc = "identity" if context == 0 else "reverse"
    else:
        raise ValueError(f"unknown selector {selector}")
    if proc not in frame:
        raise ValueError(f"selector references unavailable primitive: {proc}")
    return primitive(proc, values)


def apply_selector(selector: str, batch: Sequence[Task], frame: tuple[str, ...], memory: Mapping[tuple[int, tuple[int, ...]], tuple[int, ...]]) -> tuple[tuple[int, ...], ...]:
    out: list[tuple[int, ...]] = []
    for task in batch:
        key = (task.context_bit, task.values)
        if key in memory:
            out.append(memory[key])
        else:
            out.append(selector_apply(selector, task.context_bit, task.values, frame))
    return tuple(out)


def task(task_class: Classes, context: int, values: Sequence[int], expected: Sequence[int]) -> Task:
    vals = tuple(values)
    exp = tuple(expected)
    payload = {"world_class": task_class, "context_bit": context, "values": vals, "expected": exp}
    return Task(context, vals, exp, task_class, digest(payload))


def witnesses() -> dict[Classes, tuple[Task, ...] | tuple[tuple[Classes, ...], ...]]:
    km = (task("k_M", 0, (2, 0, 1), (2, 1, 0)),)
    ka = (task("k_A", 0, (0, 1, 2), (0, 1, 2)), task("k_A", 1, (0, 1, 2), (2, 1, 0)))
    kf = (task("k_F", 0, (0, 1, 2, 2), (0, 2, 2)), task("k_F", 0, (2, 0, 1, 1), (2, 0)))
    return {"k_M": km, "k_A": ka, "k_F": kf}


W = witnesses()
W_L: tuple[Classes, ...] = ("k_M", "k_F", "k_M", "k_F")


def candidate_memory_repairs(batch: Sequence[Task], evaluator: Evaluator) -> list[tuple[tuple[int, tuple[int, ...]], tuple[int, ...]]]:
    if len(batch) != 1:
        return []
    t = batch[0]
    candidates: list[tuple[tuple[int, tuple[int, ...]], tuple[int, ...]]] = []
    for output in product(range(3), repeat=len(t.values)):
        c = evaluator.evaluate(batch, (tuple(output),))
        if c.success:
            candidates.append(((t.context_bit, t.values), tuple(output)))
    return candidates


def diagnose(evidence: Evidence, state: State, episode_complete: bool = False) -> Classes:
    c = evidence.consequence
    n = len(evidence.input_batch)
    if episode_complete:
        return "k_L"
    if n == 1:
        return "k_M"
    if not c.lengths_preserved:
        return "k_F"
    return "k_A"


def state_id(state: State) -> str:
    return digest({"frame": list(state.frame), "selector": state.selector, "memory": [[list(k[0:1]) + [list(k[1])], list(v)] for k, v in state.memory], "operator": [[k, l] for k, l in state.operator]})


def operator_id(operator: tuple[tuple[Classes, Loci], ...]) -> str:
    return digest([[k, l] for k, l in operator])


def initial_state() -> State:
    return State(F0, "always_identity", (), (("k_M", "M"), ("k_A", "M"), ("k_F", "M"), ("k_L", "M")))


def enumerate_operators() -> tuple[tuple[tuple[Classes, Loci], ...], ...]:
    ops = []
    for choices in product(LOCI, repeat=4):
        ops.append(tuple(zip(KEYS, choices)))
    return tuple(ops)


def one_entry_revisions(op: tuple[tuple[Classes, Loci], ...]) -> tuple[tuple[tuple[Classes, Loci], ...], ...]:
    cur = dict(op)
    out = [op]
    for key in KEYS:
        for locus in LOCI:
            if locus == cur[key]:
                continue
            nxt = dict(cur)
            nxt[key] = locus
            out.append(tuple((k, nxt[k]) for k in KEYS))
    return tuple(out)


def operator_transition(operator: tuple[tuple[Classes, Loci], ...], key: Classes, state: State) -> dict[str, object]:
    locus = dict(operator)[key]
    selected = locus
    next_state = state
    if locus == "M":
        next_state = state
    elif locus == "A":
        next_state = replace(state, selector="select_on_c")
    elif locus == "F":
        next_state = replace(state, frame=frame_space(F_EVEN))
    elif locus == "L":
        next_state = state
    return {"diagnosis_key": key, "selected_update_locus": selected, "resulting_canonical_state_transition": {"state_id": state_id(next_state)}}


def equivalent(op_a: tuple[tuple[Classes, Loci], ...], op_b: tuple[tuple[Classes, Loci], ...]) -> bool:
    # Finite state/input/consequence domain relevant to this DSL. For this v0.1
    # learner, the transition function is completely determined by the dispatch.
    states = (initial_state(),)
    inputs = (("k_M",), ("k_A",), ("k_F",), ("k_L",))
    for state in states:
        for key_tuple in inputs:
            key = key_tuple[0]
            if operator_transition(op_a, key, state) != operator_transition(op_b, key, state):
                return False
    return True


def update_state(state: State, locus: Loci, batch: Sequence[Task], evaluator: Evaluator) -> State:
    if locus == "M":
        reps = candidate_memory_repairs(batch, evaluator)
        if not reps:
            return state
        mm = state.memory_map()
        mm[reps[0][0]] = reps[0][1]
        return replace(state, memory=tuple(sorted(mm.items(), key=str)))
    if locus == "A":
        return replace(state, selector="select_on_c")
    if locus == "F":
        return replace(state, frame=frame_space(F_EVEN))
    raise ValueError("operator revision is not an event-local ordinary update")


def execute_event(state: State, batch: Sequence[Task], evidence_context: int, evaluator: Evaluator) -> tuple[State, Evidence, Outcome]:
    outputs = apply_selector(state.selector, batch, state.frame, state.memory_map())
    consequence = evaluator.evaluate(batch, outputs)
    evidence = Evidence(
        event_id=digest({"batch": [t.task_id for t in batch], "outputs": [list(x) for x in outputs]}),
        episode_index=evidence_context,
        context_bit=batch[0].context_bit,
        input_batch=tuple((t.context_bit, t.values) for t in batch),
        observed_output_batch=outputs,
        consequence=consequence,
        prior_evidence=(),
    )
    return state, evidence, Outcome(outputs, consequence)


class RecursiveLearner:
    def __init__(self, arm: str, evaluator: Evaluator):
        self.arm = arm
        self.evaluator = evaluator
        self.state = initial_state()
        self.history: list[Evidence] = []
        self._operator_before_revision = self.state.operator

    def observe_and_update(self, batch: Sequence[Task], index: int) -> Evidence:
        outputs = apply_selector(self.state.selector, batch, self.state.frame, self.state.memory_map())
        consequence = self.evaluator.evaluate(batch, outputs)
        ev = Evidence(
            event_id=digest({"index": index, "batch": [t.task_id for t in batch]}),
            episode_index=index,
            context_bit=batch[0].context_bit,
            input_batch=tuple((t.context_bit, t.values) for t in batch),
            observed_output_batch=outputs,
            consequence=consequence,
            prior_evidence=tuple(digest(e.canonical()) for e in self.history),
        )
        self.history.append(ev)
        key = diagnose(ev, self.state)
        locus = dict(self.state.operator)[key]
        if self.arm == "M" and locus != "M":
            return ev
        if self.arm == "A" and locus not in {"M", "A"}:
            return ev
        if self.arm == "F" and locus not in {"M", "A", "F"}:
            return ev
        if key == "k_A" and self.arm in {"A", "F", "L"}:
            self.state = update_state(self.state, "A", batch, self.evaluator)
        elif key == "k_F" and self.arm in {"F", "L"} and locus == "F":
            self.state = update_state(self.state, "F", batch, self.evaluator)
        elif key == "k_M" and self.arm in {"M", "A", "F", "L"} and locus == "M":
            self.state = update_state(self.state, "M", batch, self.evaluator)
        return ev

    def revise_operator(self) -> None:
        if self.arm != "L":
            return
        op0 = self.state.operator
        candidates = one_entry_revisions(op0)
        for candidate in candidates:
            cm = dict(candidate)
            if cm["k_F"] != "F":
                continue
            if cm["k_M"] != "M" or cm["k_A"] != "M" or cm["k_L"] != "M":
                continue
            self.state = replace(self.state, operator=candidate)
            return
        raise AssertionError("no preregistered L1 candidate")


def generate_future() -> tuple[tuple[Task, ...], ...]:
    stream = blocks(SEED_FUTURE)
    episodes: list[tuple[Task, ...]] = []
    templates = (W_L, ("k_F", "k_M", "k_F", "k_M"), ("k_M", "k_F", "k_F", "k_M"), ("k_F", "k_M", "k_M", "k_F"))
    for episode_index in range(3):
        selector = int.from_bytes(next(stream)[:2], "big") % 4
        classes = templates[selector]
        events: list[Task] = []
        for event_index, cls in enumerate(classes):
            b = next(stream)
            n = 2 + (b[0] % 3)
            vals = tuple(v % 3 for v in b[1:1+n])
            if cls == "k_M":
                target = tuple((v + 1) % 3 for v in vals)
                # Avoid accidental identity.
                if target == vals:
                    target = tuple(reversed(vals))
                events.append(task("k_M", 0, vals, target))
            elif cls == "k_F":
                vals = tuple(v if v != 1 else 2 for v in vals)
                target = primitive("keep_even_values", vals)
                events.append(task("k_F", 0, vals, target))
            else:
                vals = tuple(v % 3 for v in vals)
                target = vals if event_index % 2 == 0 else tuple(reversed(vals))
                events.append(task("k_A", event_index % 2, vals, target))
        episodes.append(tuple(events))
    return tuple(episodes)


def correction_episode() -> tuple[Task, ...]:
    return tuple(task("k_A", i % 2, (0, 1, 2), (0, 1, 2) if i % 2 == 0 else (2, 1, 0)) for i in range(4))


def run_arm(arm: str) -> dict[str, object]:
    evaluator = Evaluator()
    learner = RecursiveLearner(arm, evaluator)
    sequence = W_L[0], W_L[1], W_L[2], W_L[3]
    class_batches = {"k_M": W["k_M"], "k_F": W["k_F"]}
    for idx, cls in enumerate(sequence):
        learner.observe_and_update(class_batches[cls], idx)
    before = learner.state.operator
    if arm == "L":
        learner.revise_operator()
    after = learner.state.operator
    future = generate_future()
    successes: list[str] = []
    losses: list[str] = []
    for ep in future:
        for event in ep:
            batch = (event,) if event.world_class == "k_M" else (event, task(event.world_class, event.context_bit, event.values, event.expected))
            outputs = apply_selector(learner.state.selector, batch, learner.state.frame, learner.state.memory_map())
            c = evaluator.evaluate(batch, outputs)
            tid = digest({"ep": future.index(ep), "task": event.task_id})
            (successes if c.success else losses).append(tid)
    return {
        "arm": arm,
        "operator_before_id": operator_id(before),
        "operator_after_id": operator_id(after),
        "operator_changed": not equivalent(before, after),
        "state_id": state_id(learner.state),
        "future_success_count": len(successes),
        "future_failure_count": len(losses),
        "future_success_task_ids": successes,
        "future_failure_task_ids": losses,
        "learner_execution_performed": True,
    }
