"""Finite, deterministic CRANK recursive-learning-operator assay kernel."""
from __future__ import annotations
from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import product
import json
from typing import Iterable, Literal, Sequence

Locus = Literal["M", "A", "F", "L"]
Class = Literal["k_M", "k_A", "k_F", "k_L"]
LOCI = ("M", "A", "F", "L")
KEYS = ("k_M", "k_A", "k_F", "k_L")
SEED_FUTURE = "crank-rlo-v0.1/future/v1"
SEED_CORRECTION = "crank-rlo-v0.1/correction/v1"
F0 = ("identity", "reverse", "sort_asc")
F_EVEN = F0 + ("keep_even_values",)
W_L = ("k_M", "k_F", "k_M", "k_F")


def canon(v: object) -> str:
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(v: object) -> str:
    return sha256(canon(v).encode()).hexdigest()


def primitive(name: str, x: tuple[int, ...]) -> tuple[int, ...]:
    if name == "identity": return x
    if name == "reverse": return tuple(reversed(x))
    if name == "sort_asc": return tuple(sorted(x))
    if name == "keep_even_values": return tuple(v for v in x if v % 2 == 0)
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

    def as_dict(self):
        return {"success": self.success, "lengths_preserved": self.lengths_preserved,
                "value_membership_valid": self.value_membership_valid,
                "order_relation": self.order_relation,
                "context_consistency": self.context_consistency}


@dataclass(frozen=True)
class Evidence:
    event_id: str
    episode_index: int
    input_batch: tuple[tuple[int, tuple[int, ...]], ...]
    observed_output_batch: tuple[tuple[int, ...], ...]
    consequence: Consequence
    prior_evidence: tuple[str, ...]

    def canonical(self):
        return {"event_id": self.event_id, "episode_index": self.episode_index,
                "input_batch": [[c, list(x)] for c, x in self.input_batch],
                "observed_output_batch": [list(x) for x in self.observed_output_batch],
                "consequence": self.consequence.as_dict(), "prior_evidence": list(self.prior_evidence)}


@dataclass(frozen=True)
class State:
    frame: tuple[str, ...]
    selector: str
    memory: tuple[tuple[tuple[int, tuple[int, ...]], tuple[int, ...]], ...]
    operator: tuple[tuple[Class, Locus], ...]

    def memory_map(self): return dict(self.memory)
    def operator_map(self): return dict(self.operator)


def make_task(cls, context, values, expected):
    v, e = tuple(values), tuple(expected)
    return Task(context, v, e, cls, digest({"class": cls, "context": context, "values": v, "expected": e}))


def witness_tasks():
    return {
        "k_M": (make_task("k_M", 0, (2,0,1), (2,1,0)),),
        "k_A": (make_task("k_A", 0, (0,1,2), (0,1,2)), make_task("k_A", 1, (0,1,2), (2,1,0))),
        "k_F": (make_task("k_F", 0, (0,1,2,2), (0,2,2)), make_task("k_F", 0, (2,0,1,1), (2,0))),
    }


WITNESS = witness_tasks()


class Evaluator:
    """Private custody evaluator; learner-facing evidence exposes only predicates."""
    def evaluate(self, batch: Sequence[Task], outputs: Sequence[tuple[int, ...]]) -> Consequence:
        ok = [o == t.expected for t, o in zip(batch, outputs)]
        lens = [len(o) == len(t.expected) for t, o in zip(batch, outputs)]
        members = [all(v in t.values for v in o) for t, o in zip(batch, outputs)]
        rels = []
        for t, o in zip(batch, outputs):
            if o == t.expected: rels.append("nondecreasing" if o == tuple(sorted(o)) else "unchanged")
            elif o == tuple(reversed(t.expected)): rels.append("reversed")
            elif o == tuple(sorted(o)): rels.append("nondecreasing")
            else: rels.append("other")
        context_ok = not (len(batch) == 2 and all(t.world_class == "k_A" for t in batch) and outputs[0] == outputs[1])
        return Consequence(all(ok), all(lens), all(members), rels[0] if len(set(rels)) == 1 else "other", context_ok)

    def valid(self, batch, outputs):
        return self.evaluate(batch, outputs).success


def frame_space(frame):
    order = {n:i for i,n in enumerate(("identity","reverse","sort_asc","keep_even_values"))}
    return tuple(sorted(set(frame), key=order.__getitem__))


def selector_output(selector, t, frame):
    proc = {"always_identity":"identity", "always_reverse":"reverse",
            "select_on_c":"identity" if t.context_bit == 0 else "reverse"}[selector]
    if proc not in frame: raise RuntimeError("selector references unavailable primitive")
    return primitive(proc, t.values)


def execute(state, batch):
    mem = state.memory_map()
    return tuple(mem[(t.context_bit,t.values)] if (t.context_bit,t.values) in mem else selector_output(state.selector,t,state.frame) for t in batch)


def make_evidence(state, batch, index, evaluator, prior=()):
    out = execute(state, batch)
    return Evidence(digest({"index":index,"task_ids":[t.task_id for t in batch]}), index,
                    tuple((t.context_bit,t.values) for t in batch), out,
                    evaluator.evaluate(batch,out), tuple(digest(e.canonical()) for e in prior))


def diagnose_event(e):
    if len(e.input_batch) == 1: return "k_M"
    if not e.consequence.lengths_preserved: return "k_F"
    return "k_A"


def initial_state():
    return State(F0, "always_identity", (), (("k_M","M"),("k_A","M"),("k_F","M"),("k_L","M")))


def update_memory(state, batch, evaluator):
    if len(batch) != 1: return state
    t = batch[0]
    for out in product(range(3), repeat=len(t.values)):
        if evaluator.valid(batch, (tuple(out),)):
            m = state.memory_map(); m[(t.context_bit,t.values)] = tuple(out)
            return replace(state, memory=tuple(sorted(m.items(), key=repr)))
    return state


def update(state, locus, batch, evaluator):
    if locus == "M": return update_memory(state,batch,evaluator)
    if locus == "A": return replace(state, selector="select_on_c")
    if locus == "F": return replace(state, frame=frame_space(F_EVEN))
    raise ValueError("L is episode-level only")


def operator_id(op): return digest([[k,v] for k,v in op])


def enumerate_operators(): return tuple(tuple(zip(KEYS,c)) for c in product(LOCI, repeat=4))


def one_entry_revisions(op):
    base = dict(op); out = [op]
    for key in KEYS:
        for locus in LOCI:
            if locus == base[key]: continue
            n = dict(base); n[key] = locus
            out.append(tuple((k,n[k]) for k in KEYS))
    return tuple(out)


def candidate_replay(operator, history, evaluator):
    """Privately evaluate one candidate over the exact frozen induction witness."""
    state = initial_state()
    state = replace(state, operator=operator)
    for index, batch in enumerate((WITNESS["k_M"],WITNESS["k_F"],WITNESS["k_M"],WITNESS["k_F"])):
        key = ("k_M","k_F","k_M","k_F")[index]
        locus = dict(operator)[key]
        if locus == "M": state = update_memory(state,batch,evaluator)
        elif locus == "A": state = update(state,"A",batch,evaluator)
        elif locus == "F":
            state = update(state,"F",batch,evaluator)
            return False if not evaluator.valid(batch, tuple(primitive("keep_even_values",t.values) for t in batch)) else (index == 3 and all(evaluator.valid(WITNESS["k_M"], execute(state,WITNESS["k_M"])))) if index == 3 else True
        else: return False
        if not evaluator.valid(batch, execute(state,batch)):
            return False
    return True


class Learner:
    def __init__(self, arm, evaluator):
        if arm not in {"M","A","F","L"}: raise ValueError(arm)
        self.arm, self.evaluator = arm, evaluator
        self.state, self.history = initial_state(), []

    def induction_event(self, batch, index):
        e = make_evidence(self.state,batch,index,self.evaluator,self.history); self.history.append(e)
        key = diagnose_event(e); locus = self.state.operator_map()[key]
        allowed = {"M":{"M"},"A":{"M","A"},"F":{"M","A","F"},"L":{"M","A","F"}}[self.arm]
        if locus in allowed: self.state = update(self.state,locus,batch,self.evaluator)
        return e

    def revise_operator(self):
        if self.arm != "L": return
        if tuple(diagnose_event(e) for e in self.history) != W_L: raise AssertionError("recursive diagnosis did not fire")
        candidates = one_entry_revisions(self.state.operator)
        scored = [(candidate_replay(c, self.history, self.evaluator), c) for c in candidates]
        winners = [c for ok,c in scored if ok]
        if not winners: raise AssertionError("no evidence-supported operator candidate")
        self.state = replace(self.state, operator=winners[0])

    def future_event(self,batch,index):
        e = make_evidence(self.state,batch,index,self.evaluator,self.history); self.history.append(e)
        key = diagnose_event(e); locus = self.state.operator_map()[key]
        self.state = update(self.state,locus,batch,self.evaluator)
        return self.evaluator.valid(batch, execute(self.state,batch)), e


def generate_future():
    s = stream(SEED_FUTURE); templates=(W_L,("k_F","k_M","k_F","k_M"),("k_M","k_F","k_F","k_M"),("k_F","k_M","k_M","k_F")); episodes=[]
    for _ in range(3):
        classes=templates[int.from_bytes(next(s)[:2],"big")%4]; events=[]
        for cls in classes:
            b=next(s); n=2+b[0]%3; vals=tuple(b[i+1]%3 for i in range(n))
            if cls=="k_F":
                if all(v%2==0 for v in vals): vals=vals[:-1]+(1,)
                other=tuple(reversed(vals))
                events.append((make_task("k_F",0,vals,primitive("keep_even_values",vals)),make_task("k_F",0,other,primitive("keep_even_values",other))))
            else:
                events.append((make_task(cls,0,vals,vals if cls=="k_A" else tuple((v+1)%3 for v in vals)),) if cls=="k_M" else (make_task("k_A",0,vals,vals),make_task("k_A",1,vals,tuple(reversed(vals)))))
        episodes.append(tuple(events))
    return tuple(episodes)
