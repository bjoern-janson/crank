"""Isolated CRANK inductive-procedure learning layer.

This package is intentionally additive. It does not modify the existing
corrective buffer, authority adapter, temporal mechanism, Layer-0 contract,
or Reach machinery.
"""

from .frame_spec import FrameSpec, Primitive
from .procedure import Procedure, ExecutionTrace, execute
from .hypothesis_space import HypothesisSpace
from .procedure_inducer import TrainingExample, InductionResult, ProcedureInducer
from .procedure_shadow import SameEvidenceShadow, ShadowObservation
from .procedure_test import ExecutionContract, ProcedureTest, TestResult, ReachCertificate

__all__ = [
    "FrameSpec",
    "Primitive",
    "Procedure",
    "ExecutionTrace",
    "execute",
    "HypothesisSpace",
    "TrainingExample",
    "InductionResult",
    "ProcedureInducer",
    "SameEvidenceShadow",
    "ShadowObservation",
    "ExecutionContract",
    "ProcedureTest",
    "TestResult",
    "ReachCertificate",
]
