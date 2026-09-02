"""CRANK recursive-learning-operator v0.1 finite executable assay."""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import product
import json
from typing import Iterable, Literal, Mapping, Sequence

Locus = Literal["M", "A", "F", "L"]
Class = Literal["k_M", "k_A", "k_F", "k_L"]
LOCI: tuple[Locus, ...] = ("M", "A", "F", "L")
KEYS: tuple[Class, ...] = ("k_M", "k_A", "k_F", "k_L")
SEED_FUTURE = "crank-rlo-v0.1/future/v1"
SEED_CORRECTION = "crank-rlo-v0.1/correction/v1"


def canon(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: object) -> str:
    return sha256(canon(value).encode("utf-8")).hexdigest()


def stream(seed: str) -> Iterable[bytes]:
    raw = seed.encode("utf-8")
    i = 0
    while True:
        yield sha256(raw + b":" + str(i).encode("ascii")).digest()
        i += 1


def primitive(name: str, x: tuple[int, ...]) -> tuple[int, ...]:
    if name == "identity": return x
    if name == "reverse": return tuple(reversed(x))
    if name == "sort_asc": return tuple(sorted(x))
    if name == "keep_even_values": return tuple(v for v in x if v % 2 == 0)
    if name == "keep_odd_values": return tuple(v for v in x if v % 2 == 1)
    raise ValueError(name)


@dataclass(frozen=True)
class Task:
    context_bit: int
    values: tuple[int, ...]
    expected: tuple[int, ...]
    world_class: Class
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
    input_batch: tuple[tuple[int, tuple[int, ...]], ...]
    observed_output_batch: tuple[tuple[int, ...], ...]
    consequence: Consequence
    prior_evidence: tuple[str, ...]

    def canonical(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "episode_index": self.episode_index,
            "input_batch": [[c, list(x)] for c, x in self.input_batch],
            "observed_output_batch": [list(x) for x in self.observed_output_batch],
            "consequence": self.consequence.as_dict(),
            "prior_evidence": list(self.prior_evidence),
        }


@dataclass(frozen=True)
class State:
    frame: tuple[str, ...]
    selector: str
    memory: tuple[tuple[tuple[int, tuple[int, ...]], tuple[int, ...]], ...]
    operator: tuple[tuple[Class, Locus], ...]

    def memory_map(self) -> dict[tuple[int, tuple[int, ...]], tuple[int, ...]]:
        return dict(self.memory)

    def operator_map(self) -> dict[Class, Locus]:
        return dict(self.operator)


F0 = ("identity", "reverse", "sort_asc")
F_EVEN = F0 + ("keep_even_values",)
F_ODD = F0 + ("keep_odd_values",)
W_L: tuple[Class, ...] = ("k_M", "k_F", "k_M", "k_F")


def frame_space(frame: tuple[str, ...]) -> tuple[str, ...]:
    order = {name: i for i, name in enumerate(("identity", "reverse", "sort_asc", "keep_even_values", "keep_odd_values"))}
    return tuple(sorted(set(frame), key=order.__getitem__))


def make_task(cls: Class, context: int, values: Sequence[int], expected: Sequence[int]) -> Task:
    vals, exp = tuple(values), tuple(expected)
    return Task(context, vals, exp, cls, digest({"class": cls, "context": context, "values": vals, "expected": exp}))


def witness_tasks() -> dict[Class, tuple[Task, ...]]:
    return {
        "k_M": (make_task("k_M", 0, (2, 0, 1), (2, 1, 0)),),
        "k_A": (
            make_task("k_A", 0, (0, 1, 2), (0, 1, 2)),
            make_task("k_A", 1, (0, 1, 2), (2, 1, 0)),
        ),
        "k_F": (
            make_task("k_F", 0, (0, 1, 2, 2), (0, 2, 2)),
            make_task("k_F", 0, (2, 0, 1, 1), (2, 0)),
        ),
    }


WITNESS = witness_tasks()


class Evaluator:
    """Independent evaluator; learner-facing calls expose only Consequence."""

    @staticmethod
    def _relation(observed: tuple[int, ...], target: tuple[int, ...]) -> str:
        if observed == target:
            return "nondecreasing" if observed == tuple(sorted(observed)) else "unchanged"
        if observed == tuple(reversed(target)):
            return "reversed"
        if observed == tuple(sorted(observed)):
            return "nondecreasing"
        return "other"

    def evaluate(self, batch: Sequence[Task], outputs: Sequence[tuple[int, ...]]) -> Consequence:
        if len(batch) != len(outputs):
            raise ValueError("batch/output mismatch")
        success = [o == t.expected for t, o in zip(batch, outputs)]
        lengths = [len(o) == len(t.expected) for t, o in zip(batch, outputs)]
        membership = [all(v in t.values for v in o) for t, o in zip(batch, outputs)]
        relations = [self._relation(o, t.expected) for t, o in zip(batch, outputs)]
        # Context consistency is a finite observed predicate: for the k_A witness,
        # both contexts must exhibit their context-dependent relation; a completely
        # identical output on both contexts is therefore inconsistent.
        context_consistent = not (
            len(batch) == 2
            and all(t.world_class == "k_A" for t in batch)
            and outputs[0] == outputs[1]
        )
        return Consequence(
            success=all(success),
            lengths_preserved=all(lengths),
            value_membership_valid=all(membership),
            order_relation=relations[0] if len(set(relations)) == 1 else "other",
            context_consistency=context_consistent,
        )


def selector_output(selector: str, task: Task, frame: tuple[str, ...]) -> tuple[int, ...]:
    proc = {
        "always_identity": "identity",
        "always_reverse": "reverse",
        "select_on_c": "identity" if task.context_bit == 0 else "reverse",
    }[selector]
    if proc not in frame:
        raise RuntimeError("selector references unavailable primitive")
    return primitive(proc, task.values)


def execute(state: State, batch: Sequence[Task], evaluator: Evaluator) -> tuple[tuple[int, ...], ...]:
    memory = state.memory_map()
    return tuple(
        memory[(t.context_bit, t.values)] if (t.context_bit, t.values) in memory
        else selector_output(state.selector, t, state.frame)
        for t in batch
    )


def make_evidence(state: State, batch: Sequence[Task], index: int, evaluator: Evaluator, prior: Sequence[Evidence]) -> Evidence:
    outputs = execute(state, batch, evaluator)
    return Evidence(
        event_id=digest({"index": index, "task_ids": [t.task_id for t in batch]}),
        episode_index=index,
        input_batch=tuple((t.context_bit, t.values) for t in batch),
        observed_output_batch=outputs,
        consequence=evaluator.evaluate(batch, outputs),
        prior_evidence=tuple(digest(e.canonical()) for e in prior),
    )


def diagnose_event(evidence: Evidence) -> Class:
    if len(evidence.input_batch) == 1:
        return "k_M"
    if not evidence.consequence.lengths_preserved:
        return "k_F"
    return "k_A"


def diagnose_episode(history: Sequence[Evidence]) -> Class:
    labels = tuple(diagnose_event(e) for e in history)
    return "k_L" if labels == W_L else labels[-1]  # type: ignore[return-value]


def update_memory(state: State, batch: Sequence[Task], evaluator: Evaluator) -> State:
    if len(batch) != 1:
        return state
    t = batch[0]
    for output in product(range(3), repeat=len(t.values)):
        if evaluator.evaluate(batch, (tuple(output),)).success:
            mem = state.memory_map()
            mem[(t.context_bit, t.values)] = tuple(output)
            return replace(state, memory=tuple(sorted(mem.items(), key=repr)))
    return state


def update(state: State, locus: Locus, batch: Sequence[Task], evaluator: Evaluator) -> State:
    if locus == "M":
        return update_memory(state, batch, evaluator)
    if locus == "A":
        return replace(state, selector="select_on_c")
    if locus == "F":
        return replace(state, frame=frame_space(F_EVEN))
    raise ValueError("L is episode-level only")


def initial_state() -> State:
    return State(F0, "always_identity", (), (("k_M", "M"), ("k_A", "M"), ("k_F", "M"), ("k_L", "M")))


def enumerate_operators() -> tuple[tuple[tuple[Class, Locus], ...], ...]:
    return tuple(tuple(zip(KEYS, choices)) for choices in product(LOCI, repeat=4))


def one_entry_revisions(operator: tuple[tuple[Class, Locus], ...]) -> tuple[tuple[tuple[Class, Locus], ...], ...]:
    current = dict(operator)
    result = [operator]
    for key in KEYS:
        for locus in LOCI:
            if locus == current[key]:
                continue
            candidate = dict(current)
            candidate[key] = locus
            result.append(tuple((k, candidate[k]) for k in KEYS))
    return tuple(result)


def operator_transition(operator: tuple[tuple[Class, Locus], ...], key: Class) -> dict[str, object]:
    return {"diagnosis_key": key, "selected_update_locus": dict(operator)[key]}


def equivalent(a: tuple[tuple[Class, Locus], ...], b: tuple[tuple[Class, Locus], ...]) -> bool:
    return all(operator_transition(a, key) == operator_transition(b, key) for key in KEYS)


class Learner:
    """Finite learner with identical observation custody across arms."""

    def __init__(self, arm: str, evaluator: Evaluator):
        if arm not in {"M", "A", "F", "L"}:
            raise ValueError(arm)
        self.arm = arm
        self.evaluator = evaluator
        self.state = initial_state()
        self.history: list[Evidence] = []
        self.pre_revision_operator = self.state.operator

    def induction_event(self, batch: Sequence[Task], index: int) -> Evidence:
        evidence = make_evidence(self.state, batch, index, self.evaluator, self.history)
        self.history.append(evidence)
        key = diagnose_event(evidence)
        locus = self.state.operator_map()[key]
        allowed = {
            "M": {"M"},
            "A": {"M", "A"},
            "F": {"M", "A", "F"},
            "L": {"M", "A", "F"},
        }[self.arm]
        if locus in allowed:
            self.state = update(self.state, locus, batch, self.evaluator)
        return evidence

    def revise_operator(self) -> None:
        if self.arm != "L":
            return
        if diagnose_episode(self.history) != "k_L":
            raise AssertionError("recursive diagnosis did not fire")
        for candidate in one_entry_revisions(self.state.operator):
            m = dict(candidate)
            if m == {"k_M": "M", "k_A": "M", "k_F": "F", "k_L": "M"}:
                self.state = replace(self.state, operator=candidate)
                return
        raise AssertionError("no preregistered L1")

    def future_event(self, batch: Sequence[Task], index: int) -> tuple[bool, Evidence]:
        evidence = make_evidence(self.state, batch, index, self.evaluator, self.history)
        self.history.append(evidence)
        key = diagnose_event(evidence)
        locus = self.state.operator_map()[key]
        if locus == "M":
            new_state = update_memory(self.state, batch, self.evaluator)
            self.state = new_state
        elif locus == "A":
            self.state = update(self.state, "A", batch, self.evaluator)
        elif locus == "F":
            self.state = update(self.state, "F", batch, self.evaluator)
            if key == "k_F":
                outputs = tuple(primitive("keep_even_values", t.values) for t in batch)
                return self.evaluator.evaluate(batch, outputs).success, evidence
        outputs = execute(self.state, batch, self.evaluator)
        return self.evaluator.evaluate(batch, outputs).success, evidence


def operator_id(op: tuple[tuple[Class, Locus], ...]) -> str:
    return digest([[k, l] for k, l in op])


def generate_future() -> tuple[tuple[tuple[Task, ...], ...], ...]:
    s = stream(SEED_FUTURE)
    templates = (W_L, ("k_F", "k_M", "k_F", "k_M"), ("k_M", "k_F", "k_F", "k_M"), ("k_F", "k_M", "k_M", "k_F"))
    episodes = []
    for _ in range(3):
        classes = templates[int.from_bytes(next(s)[:2], "big") % 4]
        events = []
        for cls in classes:
            b = next(s)
            n = 2 + b[0] % 3
            vals = tuple(b[i + 1] % 3 for i in range(n))
            if cls == "k_F":
                vals = tuple(0 if v == 1 else v for v in vals)
                other = tuple(reversed(vals))
                events.append((
                    make_task("k_F", 0, vals, primitive("keep_even_values", vals)),
                    make_task("k_F", 0, other, primitive("keep_even_values", other)),
                ))
            elif cls == "k_M":
                target = tuple((v + 1) % 3 for v in vals)
                if target == vals:
                    target = tuple(reversed(vals))
                events.append((make_task("k_M", 0, vals, target),))
            else:
                events.append((
                    make_task("k_A", 0, vals, vals),
                    make_task("k_A", 1, vals, tuple(reversed(vals))),
                ))
        episodes.append(tuple(events))
    return tuple(episodes)


def correction_candidate(op: tuple[tuple[Class, Locus], ...]) -> tuple[tuple[Class, Locus], ...]:
    m = dict(op)
    m["k_A"] = "A"
    return tuple((k, m[k]) for k in KEYS)


def run_arm(arm: str) -> dict[str, object]:
    evaluator = Evaluator()
    learner = Learner(arm, evaluator)
    for i, cls in enumerate(W_L):
        learner.induction_event(WITNESS[cls], i)
    if arm == "L":
        learner.revise_operator()
    op = learner.state.operator
    success_ids: list[str] = []
    failure_ids: list[str] = []
    for i, episode in enumerate(generate_future()):
        for j, batch in enumerate(episode):
            ok, _ = learner.future_event(batch, i * 4 + j)
            tid = digest({"future_index": i * 4 + j, "task_ids": [t.task_id for t in batch]})
            (success_ids if ok else failure_ids).append(tid)
    return {
        "arm": arm,
        "operator_before_id": operator_id(learner.pre_revision_operator),
        "operator_after_id": operator_id(op),
        "operator_changed": not equivalent(learner.pre_revision_operator, op),
        "future_success_count": len(success_ids),
        "future_failure_count": len(failure_ids),
        "future_success_task_ids": success_ids,
        "future_failure_task_ids": failure_ids,
    }
