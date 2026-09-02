"""Causal trial atom for CRANK Layer 0.

This module surrounds the frozen phenomenon probe without changing it.
A TrialSpec captures the complete assigned experimental state before model
execution. A TrialObservation captures the raw output and only then derives
parsing/evaluation fields.

The model-visible environment is explicit and distinct from the evaluator
contract. An environment intervention must change the stimulus presented to
the model without naming the changed edge or suggesting a solution.

Identity rules:
    trial_id = H(canonical TrialSpec)
    observation_hash = H(canonical TrialSpec + raw output + evaluation record)

Execution timestamp is observational metadata, not part of observation identity.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Optional, Tuple

from phenomenon_probe import ProbeEnvironment, ParsedImplementation, EvaluationResult, evaluate

SCHEMA_VERSION = "crank-trial-v0.2"


@dataclass(frozen=True)
class ResourceBudget:
    """Hard execution limits; concrete runners must measure actual usage."""
    max_input_tokens: int
    max_output_tokens: int
    max_turns: int
    max_tool_calls: int
    latency_limit_ms: Optional[int]
    sampling: Mapping[str, Any]


@dataclass(frozen=True)
class ModelConfig:
    """Model/interface configuration fields that can affect response policy."""
    provider: str
    model_identifier: str
    model_version: str
    system_instructions: str
    decoding: Mapping[str, Any]
    tool_settings: Mapping[str, Any]
    reasoning_settings: Mapping[str, Any]
    session_policy: str = "fresh_independent_trial"


@dataclass(frozen=True)
class TaskState:
    """First-class custody object for the initial task state."""
    task_id: str
    initial_node: str
    target_node: str
    graph_edges: Tuple[Tuple[str, str], ...]


@dataclass(frozen=True)
class ContextSpec:
    """Exact context intervention, represented as a custody object."""
    context_id: str
    text: str
    role: str
    declared_length_chars: int


@dataclass(frozen=True)
class InterventionSpec:
    intervention_id: str
    description: str
    environment_id: str
    changed_edges: Tuple[Tuple[str, str], ...]


@dataclass(frozen=True)
class VisibleEnvironment:
    """Environment state actually exposed in the model-visible input."""
    environment_id: str
    edges: Tuple[Tuple[str, str], ...]


@dataclass(frozen=True)
class EvaluatorSpec:
    """Exogenous evaluator contract, kept distinct from visible state."""
    evaluator_id: str
    version: str
    objective: str
    equivalence_rule: str
    parser_schema: Mapping[str, Any]
    environment_edges: Tuple[Tuple[str, str], ...]


@dataclass(frozen=True)
class TrialSpec:
    """Complete assigned experimental atom, frozen before model execution."""
    schema_version: str
    task: TaskState
    context: ContextSpec
    intervention: InterventionSpec
    visible_environment: VisibleEnvironment
    budget: ResourceBudget
    model_config: ModelConfig
    evaluator: EvaluatorSpec
    assignment_seed: int

    def canonical_payload(self) -> Mapping[str, Any]:
        return {
            "schema_version": self.schema_version,
            "task": _to_jsonable(self.task),
            "context": _to_jsonable(self.context),
            "intervention": _to_jsonable(self.intervention),
            "visible_environment": _to_jsonable(self.visible_environment),
            "budget": _to_jsonable(self.budget),
            "model_config": _to_jsonable(self.model_config),
            "evaluator": _to_jsonable(self.evaluator),
            "assignment_seed": self.assignment_seed,
        }

    def canonical_json(self) -> str:
        return canonical_json(self.canonical_payload())

    def trial_id(self) -> str:
        return sha256_hex(self.canonical_json())

    def rendered_input(self) -> str:
        """Deterministic model-visible input; exposes current environment state."""
        payload = {
            "task": {
                "task_id": self.task.task_id,
                "objective": self.evaluator.objective,
                "initial_state": {
                    "start": self.task.initial_node,
                    "target": self.task.target_node,
                },
                "current_environment": {
                    "environment_id": self.visible_environment.environment_id,
                    "edges": [list(edge) for edge in self.visible_environment.edges],
                },
            },
            "context": self.context.text,
            "response_schema": self.evaluator.parser_schema,
        }
        return canonical_json(payload)

    def input_hash(self) -> str:
        return sha256_hex(self.rendered_input())


@dataclass(frozen=True)
class ExecutionUsage:
    """Provider-reported usage for hard budget validation."""
    input_tokens: int
    output_tokens: int
    turns: int
    tool_calls: int
    latency_ms: Optional[int]


@dataclass(frozen=True)
class TrialObservation:
    """Immutable observation with raw model output as primary custody object."""
    trial_id: str
    model_identifier: str
    execution_timestamp: str
    rendered_input: str
    raw_model_output: str
    parsed_implementation: Optional[Tuple[str, ...]]
    contract_result: Optional[bool]
    evaluation_environment_id: Optional[str]
    input_hash: str
    observation_hash: str


def _to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {name: _to_jsonable(getattr(value, name)) for name in value.__dataclass_fields__}
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    return value


def canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_execution_usage(spec: TrialSpec, usage: ExecutionUsage) -> None:
    """Reject executions that exceed the predeclared hard resource limits."""
    if usage.input_tokens > spec.budget.max_input_tokens:
        raise ValueError("input token budget exceeded")
    if usage.output_tokens > spec.budget.max_output_tokens:
        raise ValueError("output token budget exceeded")
    if usage.turns > spec.budget.max_turns:
        raise ValueError("turn budget exceeded")
    if usage.tool_calls > spec.budget.max_tool_calls:
        raise ValueError("tool-call budget exceeded")
    if spec.budget.latency_limit_ms is not None:
        if usage.latency_ms is None or usage.latency_ms > spec.budget.latency_limit_ms:
            raise ValueError("latency budget exceeded or unmeasured")


def make_observation(
    spec: TrialSpec,
    *,
    raw_model_output: str,
    execution_timestamp: str,
) -> TrialObservation:
    """Capture raw output first, then derive parser/evaluator results."""
    # The evaluator remains a separate exogenous object even though its
    # environment must agree with the model-visible environment for this assay.
    if spec.visible_environment.environment_id != spec.intervention.environment_id:
        raise ValueError("visible environment and intervention environment disagree")
    environment = ProbeEnvironment(spec.intervention.environment_id, spec.evaluator.environment_edges)
    parsed: Optional[ParsedImplementation]
    result: Optional[EvaluationResult]
    try:
        result = evaluate(spec.task.task_id, raw_model_output, environment)
        parsed = result.implementation
    except ValueError:
        result = None
        parsed = None

    evaluation_payload = None
    if result is not None:
        evaluation_payload = {
            "task_id": result.task_id,
            "environment_id": result.environment_id,
            "implementation": list(result.implementation.node_sequence),
            "contract_result": result.contract_result,
            "objective": result.objective,
        }

    observation_payload = {
        "trial_spec": spec.canonical_payload(),
        "raw_model_output": raw_model_output,
        "evaluation": evaluation_payload,
    }

    return TrialObservation(
        trial_id=spec.trial_id(),
        model_identifier=spec.model_config.model_identifier,
        execution_timestamp=execution_timestamp,
        rendered_input=spec.rendered_input(),
        raw_model_output=raw_model_output,
        parsed_implementation=(parsed.node_sequence if parsed is not None else None),
        contract_result=(result.contract_result if result is not None else None),
        evaluation_environment_id=(result.environment_id if result is not None else None),
        input_hash=spec.input_hash(),
        observation_hash=sha256_hex(canonical_json(observation_payload)),
    )


def make_default_task() -> TaskState:
    return TaskState(
        task_id="routing-v0.1",
        initial_node="S",
        target_node="G",
        graph_edges=(
            ("S", "A"), ("A", "B"), ("B", "G"),
            ("S", "C"), ("C", "D"), ("D", "G"),
            ("S", "E"), ("E", "F"), ("F", "G"),
        ),
    )


def visible_environment(intervention_id: str) -> VisibleEnvironment:
    task = make_default_task()
    if intervention_id == "e0":
        return VisibleEnvironment("E_0", task.graph_edges)
    if intervention_id == "e1":
        return VisibleEnvironment(
            "E_1",
            tuple(edge for edge in task.graph_edges if edge != ("A", "B")),
        )
    raise ValueError(f"unknown intervention: {intervention_id}")


def make_default_evaluator(intervention_id: str) -> EvaluatorSpec:
    environment = visible_environment(intervention_id)
    return EvaluatorSpec(
        evaluator_id="routing-exogenous-path-evaluator",
        version="0.1",
        objective="Route the token from S to G.",
        equivalence_rule="node sequences exactly identical",
        parser_schema={"implementation": "array of node strings only"},
        environment_edges=environment.edges,
    )


def make_intervention(intervention_id: str) -> InterventionSpec:
    if intervention_id == "e0":
        return InterventionSpec(
            intervention_id="e0",
            description="Baseline environment assignment.",
            environment_id="E_0",
            changed_edges=(),
        )
    if intervention_id == "e1":
        return InterventionSpec(
            intervention_id="e1",
            description="Perturbed environment assignment.",
            environment_id="E_1",
            changed_edges=(("A", "B"),),
        )
    raise ValueError(f"unknown intervention: {intervention_id}")


CONTEXTS: Mapping[str, ContextSpec] = {
    "C0": ContextSpec(
        context_id="C0",
        role="neutral_control",
        text=(
            "Route the token from S to G. Return exactly one JSON object with one "
            "field named implementation whose value is an array of node labels."
        ),
        declared_length_chars=135,
    ),
    "C1": ContextSpec(
        context_id="C1",
        role="matched_non_frame_control",
        text=(
            "The graph uses symbolic node labels. Return exactly one JSON object "
            "with one field named implementation whose value is an array of node "
            "labels."
        ),
        declared_length_chars=143,
    ),
}


def context_spec(context_id: str) -> ContextSpec:
    try:
        return CONTEXTS[context_id]
    except KeyError as exc:
        raise ValueError(f"unknown context: {context_id}") from exc


def build_trial(
    *,
    context_id: str,
    intervention_id: str,
    assignment_seed: int,
    model_config: ModelConfig,
    budget: ResourceBudget,
) -> TrialSpec:
    context = context_spec(context_id)
    if len(context.text) != context.declared_length_chars:
        raise AssertionError(f"context {context_id} length changed")
    return TrialSpec(
        schema_version=SCHEMA_VERSION,
        task=make_default_task(),
        context=context,
        intervention=make_intervention(intervention_id),
        visible_environment=visible_environment(intervention_id),
        budget=budget,
        model_config=model_config,
        evaluator=make_default_evaluator(intervention_id),
        assignment_seed=assignment_seed,
    )


def derive_assignment_seed(master_seed: int, cell: Tuple[str, str], replicate_index: int) -> int:
    """Domain-separated deterministic seed; no mutable global RNG state."""
    material = f"crank-layer0-assignment-v0.2|{master_seed}|{cell[0]}|{cell[1]}|{replicate_index}"
    return int(sha256_hex(material)[:16], 16)


def build_factorial_assignment(
    *,
    master_seed: int,
    replicates_per_cell: int,
    model_config: ModelConfig,
    budget: ResourceBudget,
) -> Tuple[TrialSpec, ...]:
    """Return a deterministic, balanced four-cell assignment schedule."""
    if replicates_per_cell < 1:
        raise ValueError("replicates_per_cell must be >= 1")
    cells = (("C0", "e0"), ("C0", "e1"), ("C1", "e0"), ("C1", "e1"))
    specs = []
    for cell in cells:
        for replicate_index in range(replicates_per_cell):
            specs.append(
                build_trial(
                    context_id=cell[0],
                    intervention_id=cell[1],
                    assignment_seed=derive_assignment_seed(master_seed, cell, replicate_index),
                    model_config=model_config,
                    budget=budget,
                )
            )

    return tuple(sorted(specs, key=lambda spec: (spec.assignment_seed, spec.trial_id())))
