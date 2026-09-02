from dataclasses import dataclass
from typing import Iterable, Tuple

from .procedure import ExecutionTrace, Procedure, execute


@dataclass(frozen=True)
class ShadowObservation:
    procedure_id: str
    evidence_ids: Tuple[str, ...]
    trace_ids: Tuple[str, ...]


@dataclass(frozen=True)
class SameEvidenceShadow:
    """Frozen procedural control receiving the same evidence interface.

    Evidence is recorded for custody but cannot alter the frozen procedure.
    """

    procedure: Procedure

    def run(self, evidence: Iterable[object], inputs: Iterable[Iterable[int]]) -> ShadowObservation:
        evidence_tuple = tuple(evidence)
        traces = tuple(execute(self.procedure, values) for values in inputs)
        ids = tuple(getattr(item, "example_id", str(i)) for i, item in enumerate(evidence_tuple))
        return ShadowObservation(
            procedure_id=self.procedure.procedure_id,
            evidence_ids=ids,
            trace_ids=tuple(trace.trace_id for trace in traces),
        )

    def revised(self, *_: object) -> "SameEvidenceShadow":
        raise RuntimeError("same-evidence shadow is frozen and cannot be revised")
