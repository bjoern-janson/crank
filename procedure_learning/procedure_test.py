from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Tuple

from .procedure import Procedure, execute


def _canonical(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _canonical(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"unsupported canonical value: {type(value)!r}")


def _hash(value: Any) -> str:
    payload = json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ExecutionContract:
    """Frozen interface/resource identity used for procedure evaluation."""

    interface_id: str
    theta_id: str
    budget_id: str

    def __post_init__(self) -> None:
        if not self.interface_id or not self.theta_id or not self.budget_id:
            raise ValueError("execution contract identifiers must be non-empty")

    @property
    def contract_id(self) -> str:
        return _hash(("crank-execution-contract-v1", self.interface_id, self.theta_id, self.budget_id))


@dataclass(frozen=True)
class TestResult:
    procedure_id: str
    task_id: str
    passed: bool
    output_value: Tuple[int, ...]
    expected_output: Tuple[int, ...]
    trace_id: str
    execution_contract_id: str


@dataclass(frozen=True)
class ReachCertificate:
    procedure_id: str
    task_set_hash: str
    execution_contract_id: str
    reachable_task_ids: Tuple[str, ...]
    certificate_id: str


@dataclass(frozen=True)
class ProcedureTest:
    contract: ExecutionContract

    def run(self, procedure: Procedure, tasks: Iterable[Tuple[str, Iterable[int], Iterable[int]]]) -> Tuple[TestResult, ...]:
        results = []
        for task_id, input_value, expected_output in tasks:
            expected = tuple(int(x) for x in expected_output)
            trace = execute(procedure, input_value)
            results.append(
                TestResult(
                    procedure_id=procedure.procedure_id,
                    task_id=str(task_id),
                    passed=trace.output_value == expected,
                    output_value=trace.output_value,
                    expected_output=expected,
                    trace_id=trace.trace_id,
                    execution_contract_id=self.contract.contract_id,
                )
            )
        return tuple(results)

    def retain(self, results: Iterable[TestResult]) -> bool:
        """Return true only when every declared prospective test passed."""
        ordered = tuple(results)
        return bool(ordered) and all(
            result.passed and result.execution_contract_id == self.contract.contract_id
            for result in ordered
        )

    def certificate(self, procedure: Procedure, results: Iterable[TestResult]) -> ReachCertificate:
        ordered = tuple(sorted(results, key=lambda r: r.task_id))
        task_set_hash = _hash(
            (
                "crank-task-set-v1",
                tuple((r.task_id, r.expected_output) for r in ordered),
            )
        )
        reachable = tuple(r.task_id for r in ordered if r.passed)
        certificate_id = _hash(
            (
                "crank-reach-certificate-v1",
                procedure.procedure_id,
                task_set_hash,
                self.contract.contract_id,
                reachable,
            )
        )
        return ReachCertificate(
            procedure_id=procedure.procedure_id,
            task_set_hash=task_set_hash,
            execution_contract_id=self.contract.contract_id,
            reachable_task_ids=reachable,
            certificate_id=certificate_id,
        )
