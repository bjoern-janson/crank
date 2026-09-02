"""Deterministic tabular mechanism with explicitly revisable experience state."""
from dataclasses import dataclass
from typing import Tuple
from authority_adapter import AdmissibleSpace

FAILURE = "attempt_failed"
SUCCESS = "fallback_completed"

@dataclass(frozen=True, order=True)
class Experience:
    action: str
    consequence_code: str

@dataclass(frozen=True, order=True)
class RevisableState:
    scores: Tuple[Tuple[str, int], ...]
    @classmethod
    def initial(cls, actions): return cls(tuple((a,0) for a in actions))
    def score_for(self, action): return dict(self.scores)[action]
    def update(self, experience: Experience):
        scores=dict(self.scores)
        if experience.action not in scores: raise ValueError(f"unknown action {experience.action}")
        if experience.consequence_code == FAILURE:
            scores[experience.action] += 1
        elif experience.consequence_code == SUCCESS:
            scores[experience.action] = max(0, scores[experience.action] - 1)
        else:
            raise ValueError(f"unknown consequence {experience.consequence_code}")
        return RevisableState(tuple(scores.items()))

@dataclass(frozen=True)
class RevisableMechanism:
    priority: Tuple[str,...] = ("a_tool","z_fallback")
    def choose(self, admissible: AdmissibleSpace, state: RevisableState):
        if not admissible.allowed_actions: raise ValueError('empty admissible space')
        p={a:i for i,a in enumerate(self.priority)}
        return min(admissible.allowed_actions,key=lambda a:(state.score_for(a),p.get(a,len(p)),a))
