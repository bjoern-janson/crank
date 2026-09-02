from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from .hypothesis_space import HypothesisSpace
from .procedure import Procedure, execute


@dataclass(frozen=True)
class TrainingExample:
    example_id: str
    input_value: Tuple[int, ...]
    expected_output: Tuple[int, ...]

    def __init__(self, example_id: str, input_value: Iterable[int], expected_output: Iterable[int]) -> None:
        if not example_id:
            raise ValueError("example_id must be non-empty")
        object.__setattr__(self, "example_id", example_id)
        object.__setattr__(self, "input_value", tuple(int(x) for x in input_value))
        object.__setattr__(self, "expected_output", tuple(int(x) for x in expected_output))


@dataclass(frozen=True)
class InductionResult:
    candidate: Optional[Procedure]
    evidence: Tuple[TrainingExample, ...]
    tested_hypotheses: int


@dataclass(frozen=True)
class ProcedureInducer:
    """Deterministic exhaustive inducer over a declared finite space.

    The inducer has no expressive power beyond HypothesisSpace.enumerate().
    Candidate selection is the first exact-training-fit in canonical
    enumeration order, making the result reproducible and auditable.
    """

    hypothesis_space: HypothesisSpace

    def induce(self, evidence: Iterable[TrainingExample]) -> InductionResult:
        examples = tuple(evidence)
        tested = 0
        for candidate in self.hypothesis_space.enumerate():
            tested += 1
            if all(
                execute(candidate, example.input_value).output_value == example.expected_output
                for example in examples
            ):
                return InductionResult(candidate, examples, tested)
        return InductionResult(None, examples, tested)
