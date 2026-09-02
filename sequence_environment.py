from dataclasses import dataclass
from typing import Mapping, Tuple

@dataclass(frozen=True)
class SequencedEnvironment:
    """Deterministic time-indexed consequence mapping."""
    _steps: Tuple[Tuple[str, Tuple[Tuple[str,str],...]], ...]
    def __init__(self, steps: Mapping[int, Mapping[str,str]]):
        object.__setattr__(self, '_steps', tuple(sorted((int(t), tuple(sorted((str(a),str(c)) for a,c in m.items()))) for t,m in steps.items())))
    def consequence(self, t: int, action: str) -> str:
        return dict(dict(self._steps)[int(t)])[action]
