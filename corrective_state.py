from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True, order=True)
class CanonicalClaim:
    id: str
    content: str
    authority: str
    dependencies: Tuple[str, ...]
    invalidated_by: Tuple[str, ...] = ()

@dataclass(frozen=True, order=True)
class CanonicalAnomaly:
    id: str
    tool_name: str
    input_args: str
    error_trace: str
    related_claim_id: str

@dataclass(frozen=True, order=True)
class CanonicalCorrection:
    id: str
    observation_id: str
    target_claim_id: str
    constraint_key: str
    negative_invariant: str
    rationale: str

@dataclass(frozen=True)
class CorrectiveState:
    active_claims: Tuple[CanonicalClaim, ...]
    invalidated_claims: Tuple[CanonicalClaim, ...]
    anomalies: Tuple[CanonicalAnomaly, ...]
    corrections: Tuple[CanonicalCorrection, ...]
