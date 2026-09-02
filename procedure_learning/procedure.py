from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Tuple

from .frame_spec import Primitive


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _canonical(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    if isinstance(value, Primitive):
        return value.value
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"unsupported canonical value: {type(value)!r}")


def _sha256(value: Any) -> str:
    payload = json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Procedure:
    """Executable program represented only by primitive operations.

    This object defines execution semantics.  Membership in a particular
    frame/hypothesis space is deliberately checked elsewhere.
    """

    program: Tuple[Primitive, ...]

    def __init__(self, program: Iterable[Primitive]) -> None:
        object.__setattr__(self, "program", tuple(Primitive(p) for p in program))

    @property
    def procedure_id(self) -> str:
        return _sha256(("crank-procedure-v1", tuple(p.value for p in self.program)))

    def canonical_program(self) -> tuple:
        return tuple(p.value for p in self.program)


@dataclass(frozen=True)
class ExecutionTrace:
    procedure_id: str
    input_value: tuple
    steps: Tuple[Tuple[str, tuple], ...]
    output_value: tuple

    @property
    def trace_id(self) -> str:
        return _sha256(
            (
                "crank-trace-v1",
                self.procedure_id,
                self.input_value,
                self.steps,
                self.output_value,
            )
        )


def _apply(primitive: Primitive, value: tuple) -> tuple:
    if primitive is Primitive.IDENTITY:
        return value
    if primitive is Primitive.REVERSE:
        return tuple(reversed(value))
    if primitive is Primitive.SORT_ASC:
        return tuple(sorted(value))
    if primitive is Primitive.SORT_DESC:
        return tuple(sorted(value, reverse=True))
    if primitive is Primitive.KEEP_EVEN:
        return tuple(x for x in value if x % 2 == 0)
    if primitive is Primitive.KEEP_ODD:
        return tuple(x for x in value if x % 2 != 0)
    if primitive is Primitive.DROP_FIRST:
        return value[1:]
    if primitive is Primitive.DROP_LAST:
        return value[:-1]
    raise ValueError(f"unsupported primitive: {primitive!r}")


def execute(procedure: Procedure, input_value: Iterable[int]) -> ExecutionTrace:
    current = tuple(int(x) for x in input_value)
    steps = []
    for primitive in procedure.program:
        current = _apply(primitive, current)
        steps.append((primitive.value, current))
    return ExecutionTrace(
        procedure_id=procedure.procedure_id,
        input_value=tuple(int(x) for x in input_value),
        steps=tuple(steps),
        output_value=current,
    )
