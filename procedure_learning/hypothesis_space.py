from dataclasses import dataclass
from itertools import product
from typing import Iterable, Iterator, Tuple

from .frame_spec import FrameSpec, Primitive
from .procedure import Procedure


@dataclass(frozen=True)
class HypothesisSpace:
    """Finite executable hypothesis space induced by a FrameSpec."""

    frame: FrameSpec

    def contains(self, procedure: Procedure) -> bool:
        program = procedure.program
        return (
            len(program) <= self.frame.max_program_length
            and all(p in self.frame.allowed_primitives for p in program)
        )

    def __len__(self) -> int:
        return sum(len(self.frame.allowed_primitives) ** n for n in range(self.frame.max_program_length + 1))

    def enumerate(self) -> Iterator[Procedure]:
        primitives: Tuple[Primitive, ...] = self.frame.allowed_primitives
        yield Procedure(())
        for length in range(1, self.frame.max_program_length + 1):
            for program in product(primitives, repeat=length):
                yield Procedure(program)

    def canonical(self) -> tuple:
        return ("crank-hypothesis-space-v1", self.frame.canonical())
