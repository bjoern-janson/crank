from dataclasses import dataclass
from typing import Mapping, Tuple
@dataclass(frozen=True)
class EnvironmentalConsequence: code: str
@dataclass(frozen=True)
class DeterministicEnvironment:
    _map: Tuple[Tuple[str,str],...]
    def __init__(self, transitions: Mapping[str,str]): object.__setattr__(self,'_map',tuple(sorted((str(k),str(v)) for k,v in transitions.items())))
    def consequence(self, behavior): return EnvironmentalConsequence(dict(self._map)[behavior])
@dataclass(frozen=True)
class PredeclaredScalarMetric:
    _scores: Tuple[Tuple[str,float],...]
    def __init__(self,scores: Mapping[str,float]): object.__setattr__(self,'_scores',tuple(sorted((str(k),float(v)) for k,v in scores.items())))
    def score(self,c): return dict(self._scores)[c.code]
