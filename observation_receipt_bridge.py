"""Validated observational output -> buffer-compatible evidence receipt.

The model contributes raw output only. Empirical authority is minted only after
the exogenous probe evaluator has produced a successful contract evaluation.
"""

from dataclasses import dataclass, field
from corrigible_buffer_v1 import AuthorizedReceipt, ReceiptAuthority
from phenomenon_probe import ProbeObservation

@dataclass(frozen=True)
class ValidatedObservation:
    evaluator_receipt_id: str
    task_id: str
    environment_id: str
    raw_model_output: str
    implementation: tuple[str, ...]
    contract_result: bool
    _issuer_token: object = field(repr=False, compare=False, default=None)
    def is_validated_by(self, token: object) -> bool:
        return self._issuer_token is token and self.contract_result is True

class ExogenousEvaluator:
    """Trusted evaluator-side receipt issuer, not model-owned authority."""
    def __init__(self):
        self.__issuer_token = object()
        self.__receipt_ids: set[str] = set()
    def validate(self, receipt_id: str, observation: ProbeObservation) -> ValidatedObservation:
        if receipt_id in self.__receipt_ids:
            raise ValueError(f"duplicate evaluator receipt id: {receipt_id}")
        if observation.evaluation is None or observation.parsed_implementation is None:
            raise ValueError("cannot validate an unevaluated observation")
        if observation.evaluation.contract_result is not True:
            raise ValueError("only successful external evaluations can produce evidence")
        self.__receipt_ids.add(receipt_id)
        return ValidatedObservation(
            evaluator_receipt_id=receipt_id,
            task_id=observation.task_id,
            environment_id=observation.evaluation.environment_id,
            raw_model_output=observation.raw_model_output,
            implementation=observation.parsed_implementation.node_sequence,
            contract_result=True,
            _issuer_token=self.__issuer_token,
        )
    def to_buffer_receipt(self, observation: ValidatedObservation, authority: ReceiptAuthority, validates_claim_id: str) -> AuthorizedReceipt:
        if not observation.is_validated_by(self.__issuer_token):
            raise ValueError("observation was not issued by this evaluator")
        return authority.authorize_success(
            receipt_id=observation.evaluator_receipt_id,
            tool_name="phenomenon_probe_evaluator",
            input_args=f"task={observation.task_id};environment={observation.environment_id}",
            output_summary=observation.raw_model_output,
            validates_claim_id=validates_claim_id,
        )
