"""Layer-0 Minimal Phenomenon Probe for the CRANK stack.

Primitive:
    I ~ pi(I | X, C, e, B)
    Y = A(I, E)

The probe is an observational front end. It captures the raw model output,
then parses and evaluates it exogenously. It does not infer a mechanism,
frame, learning, representation change, capability, or improvement.
"""

from dataclasses import dataclass
import json
from typing import Iterable, Mapping, Optional, Tuple

TASK_ID = "routing-v0.1"
OBJECTIVE = "Route the token from S to G."

BASELINE_EDGES: Tuple[Tuple[str, str], ...] = (
    ("S", "A"), ("A", "B"), ("B", "G"),
    ("S", "C"), ("C", "D"), ("D", "G"),
    ("S", "E"), ("E", "F"), ("F", "G"),
)
PERTURBED_REMOVAL = ("A", "B")


class ParseError(ValueError):
    """Raw model output cannot be parsed as the frozen probe schema."""


class ContractMismatch(ValueError):
    """The preregistered task identification conditions do not hold."""


@dataclass(frozen=True)
class ProbeEnvironment:
    environment_id: str
    edges: Tuple[Tuple[str, str], ...]

    @classmethod
    def baseline(cls) -> "ProbeEnvironment":
        return cls("E_0", BASELINE_EDGES)

    @classmethod
    def perturbed(cls) -> "ProbeEnvironment":
        return cls(
            "E_1",
            tuple(edge for edge in BASELINE_EDGES if edge != PERTURBED_REMOVAL),
        )


@dataclass(frozen=True)
class ParsedImplementation:
    node_sequence: Tuple[str, ...]


@dataclass(frozen=True)
class EvaluationResult:
    task_id: str
    environment_id: str
    implementation: ParsedImplementation
    contract_result: bool
    objective: str


@dataclass(frozen=True)
class ProbeObservation:
    """Raw-output custody object plus fields derived afterward."""

    context_id: str
    intervention_id: str
    task_id: str
    raw_model_output: str
    parsed_implementation: Optional[ParsedImplementation]
    evaluation: Optional[EvaluationResult]


def parse_implementation(raw_model_output: str) -> ParsedImplementation:
    """Parse exactly one model-owned field: the proposed implementation."""
    try:
        payload = json.loads(raw_model_output)
    except json.JSONDecodeError as exc:
        raise ParseError("model output is not valid JSON") from exc

    if not isinstance(payload, dict) or set(payload) != {"implementation"}:
        raise ParseError("model output must contain exactly 'implementation'")

    implementation = payload["implementation"]
    if not isinstance(implementation, list) or not implementation:
        raise ParseError("implementation must be a non-empty list")
    if not all(isinstance(node, str) for node in implementation):
        raise ParseError("implementation nodes must all be strings")

    return ParsedImplementation(tuple(implementation))


def is_valid_path(
    implementation: ParsedImplementation,
    environment: ProbeEnvironment,
) -> bool:
    nodes = implementation.node_sequence
    if len(nodes) < 2 or nodes[0] != "S" or nodes[-1] != "G":
        return False
    available = set(environment.edges)
    return all((a, b) in available for a, b in zip(nodes, nodes[1:]))


def evaluate(
    task_id: str,
    raw_model_output: str,
    environment: ProbeEnvironment,
) -> EvaluationResult:
    """Parse and evaluate after raw-output capture; evaluator is exogenous."""
    implementation = parse_implementation(raw_model_output)
    return EvaluationResult(
        task_id=task_id,
        environment_id=environment.environment_id,
        implementation=implementation,
        contract_result=is_valid_path(implementation, environment),
        objective=OBJECTIVE,
    )


def observe(
    *,
    context_id: str,
    intervention_id: str,
    task_id: str,
    raw_model_output: str,
    environment: ProbeEnvironment,
) -> ProbeObservation:
    """Capture raw output first, then derive parse/evaluation records."""
    try:
        result = evaluate(task_id, raw_model_output, environment)
    except ParseError:
        return ProbeObservation(
            context_id=context_id,
            intervention_id=intervention_id,
            task_id=task_id,
            raw_model_output=raw_model_output,
            parsed_implementation=None,
            evaluation=None,
        )

    return ProbeObservation(
        context_id=context_id,
        intervention_id=intervention_id,
        task_id=task_id,
        raw_model_output=raw_model_output,
        parsed_implementation=result.implementation,
        evaluation=result,
    )


def summarize_distribution(
    observations: Iterable[ProbeObservation],
) -> Mapping[Tuple[str, str, Tuple[str, ...]], int]:
    """Secondary descriptive distribution; observations are never rewritten."""
    counts = {}
    for observation in observations:
        implementation = (
            observation.parsed_implementation.node_sequence
            if observation.parsed_implementation is not None
            else ("<PARSE_ERROR>",)
        )
        key = (observation.context_id, observation.intervention_id, implementation)
        counts[key] = counts.get(key, 0) + 1
    return counts


def validate_probe_contract() -> None:
    """Assert the preregistered identification conditions."""
    e0 = ProbeEnvironment.baseline()
    e1 = ProbeEnvironment.perturbed()
    i0 = ParsedImplementation(("S", "A", "B", "G"))
    ia = ParsedImplementation(("S", "C", "D", "G"))
    ib = ParsedImplementation(("S", "E", "F", "G"))

    if not is_valid_path(i0, e0):
        raise ContractMismatch("A(I0,E0)=1 failed")
    if is_valid_path(i0, e1):
        raise ContractMismatch("A(I0,E1)=0 failed")
    if not is_valid_path(ia, e1) or not is_valid_path(ib, e1):
        raise ContractMismatch("valid alternatives under E1 failed")
    if ia.node_sequence == ib.node_sequence:
        raise ContractMismatch("alternatives are not distinct")
