from dataclasses import dataclass
from typing import Iterable, Mapping, Tuple
from corrective_state import CorrectiveState

@dataclass(frozen=True)
class AdmissibleSpace:
    allowed_actions: Tuple[str, ...]
    applied_constraints: Tuple[str, ...]

@dataclass(frozen=True)
class AuthorityAdapter:
    _base_actions: Tuple[str, ...]
    _deny_rules: Tuple[Tuple[str, Tuple[str, ...]], ...]

    def __init__(self, base_actions: Iterable[str], deny_rules: Mapping[str, Iterable[str]]):
        object.__setattr__(self, '_base_actions', tuple(sorted(set(base_actions))))
        object.__setattr__(self, '_deny_rules', tuple(sorted((k, tuple(sorted(set(v)))) for k,v in deny_rules.items())))

    def admissible(self, state: CorrectiveState) -> AdmissibleSpace:
        rules = dict(self._deny_rules)
        keys = tuple(sorted({c.constraint_key for c in state.corrections if c.constraint_key in rules}))
        denied = set()
        for key in keys:
            denied.update(rules[key])
        return AdmissibleSpace(tuple(a for a in self._base_actions if a not in denied), keys)
