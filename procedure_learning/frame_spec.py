from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Tuple


class Primitive(str, Enum):
    IDENTITY = "identity"
    REVERSE = "reverse"
    SORT_ASC = "sort_asc"
    SORT_DESC = "sort_desc"
    KEEP_EVEN = "keep_even"
    KEEP_ODD = "keep_odd"
    DROP_FIRST = "drop_first"
    DROP_LAST = "drop_last"


@dataclass(frozen=True)
class FrameSpec:
    """Declares the constructive language available to procedure induction.

    The frame does not itself define a procedure.  It only fixes the allowed
    primitive vocabulary and the maximum program length, making the induced
    hypothesis space finite and auditable.
    """

    frame_id: str
    allowed_primitives: Tuple[Primitive, ...]
    max_program_length: int

    def __init__(
        self,
        frame_id: str,
        allowed_primitives: Iterable[Primitive],
        max_program_length: int,
    ) -> None:
        if not frame_id:
            raise ValueError("frame_id must be non-empty")
        primitives = tuple(dict.fromkeys(Primitive(p) for p in allowed_primitives))
        if not primitives:
            raise ValueError("allowed_primitives must be non-empty")
        if max_program_length < 0:
            raise ValueError("max_program_length must be non-negative")
        object.__setattr__(self, "frame_id", frame_id)
        object.__setattr__(self, "allowed_primitives", primitives)
        object.__setattr__(self, "max_program_length", max_program_length)

    def canonical(self) -> tuple:
        return (
            self.frame_id,
            tuple(p.value for p in self.allowed_primitives),
            self.max_program_length,
        )
