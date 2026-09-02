"""Causal trial atom for CRANK Layer 0.

This module surrounds the frozen phenomenon probe without changing it.
A TrialSpec captures the complete assigned experimental state before model
execution. A TrialObservation captures the raw output and only then derives
parsing/evaluation fields.

Identity rules:
    trial_id = H(canonical TrialSpec)
    observation_hash = H(canonical TrialSpec + raw output + evaluation record)

The trial identifier is therefore outcome-independent.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Optional, Tuple

from phenomenon_probe import ProbeEnvironment, ParsedImplementation, EvaluationResult, evaluate

SCHEMA_VERSION = "crank-trial-v0.1"


@dataclass(frozen=True)
class ResourceBudget:
    """Predeclared execution budget; values are metadata, not outcomes."""
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


@dataclass(frozen=True)
class TaskState:
    """First-class custody object for the model-visible initial task state."""
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
class EvaluatorSpec:
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
        """Deterministic model-visible input; no outcome fields are included."""
        payload = {
            "task": {
                "task_id": self.task.task_id,
                "objective": self.evaluator.objective,
                "initial_state": {
                    "start": self.task.initial_node,
                    "target": self.task.target_node,
                    "edges": [list(edge) for edge in self.task.graph_edges],
                },
            },
            "context": self.context.text,
            "intervention": self.intervention.description,
            "response_schema": self.evaluator.parser_schema,
        }
        return canonical_json(payload)

    def input_hash(self) -> str:
        return sha256_hex(self.rendered_input())


@dataclass(frozen=True)
class TrialObservation:
    """Immutable observation with raw model output as primary custody object."""
    trial_id: str
    model_identifier: str
    execution_timestamp: str
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


def make_observation(
    spec: TrialSpec,
    *,
    raw_model_output: str,
    execution_timestamp: str,
) -> TrialObservation:
    """Capture raw output first, then derive parser/evaluator results."""
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


def make_default_evaluator(intervention_id: str) -> EvaluatorSpec:
    task = make_default_task()
    if intervention_id == "e0":
        edges = task.graph_edges
    elif intervention_id == "e1":
        edges = tuple(edge for edge in task.graph_edges if edge != ("A", "B"))
    else:
        raise ValueError(f"unknown intervention: {intervention_id}")
    return EvaluatorSpec(
        evaluator_id="routing-exogenous-path-evaluator",
        version="0.1",
        objective="Route the token from S to G.",
        equivalence_rule="node sequences exactly identical",
        parser_schema={"implementation": "array of node strings only"},
        environment_edges=edges,
    )


def make_intervention(intervention_id: str) -> InterventionSpec:
    if intervention_id == "e0":
        return InterventionSpec(
            intervention_id="e0",
            description="No environmental change; use the baseline routing environment.",
            environment_id="E_0",
            changed_edges=(),
        )
    if intervention_id == "e1":
        return InterventionSpec(
            intervention_id="e1",
            description="The routing environment has changed; the A-to-B transition is unavailable.",
            environment_id="E_1",
            changed_edges=(("A", "B"),),
        )
    raise ValueError(f"unknown intervention: {intervention_id}")


# The v0.1 contexts are deliberately equal in character footprint. Exact token
# equality remains model/tokenizer dependent and is recorded separately by an
# execution harness once a concrete model interface is selected.
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
            "Route the token from S to G. Check format first; return exactly one "
            "JSON object with one field named implementation whose value is an "
            "array of node labels."
        ),
        declared_length_chars=135,
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
        budget=budget,
        model_config=model_config,
        evaluator=make_default_evaluator(intervention_id),
        assignment_seed=assignment_seed,
    )
