"""Validated observational output -> buffer-compatible evidence receipt.

The model contributes raw output only. Empirical authority is minted only after
the exogenous evaluator recomputes the frozen contract from raw observation
custody. Caller-supplied parsed/evaluation fields are never trusted as the
source of validity.
"""

from dataclasses import dataclass, field
from corrigible_buffer_v1 import AuthorizedReceipt, ReceiptAuthority
from phenomenon_probe import ProbeEnvironment, ProbeObservation, evaluate

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
    def __init__(self, environment: ProbeEnvironment):
        self.__issuer_token = object()
        self.__receipt_ids: set[str] = set()
        self.__environment = environment

    def validate(self, receipt_id: str, observation: ProbeObservation) -> ValidatedObservation:
        if receipt_id in self.__receipt_ids:
            raise ValueError(f"duplicate evaluator receipt id: {receipt_id}")

        try:
            result = evaluate(
                observation.task_id,
                observation.raw_model_output,
                self.__environment,
            )
        except ValueError as exc:
            raise ValueError("cannot validate observation against evaluator contract") from exc

        if result.contract_result is not True:
            raise ValueError("only successful external evaluations can produce evidence")

        self.__receipt_ids.add(receipt_id)
        return ValidatedObservation(
            evaluator_receipt_id=receipt_id,
            task_id=result.task_id,
            environment_id=result.environment_id,
            raw_model_output=observation.raw_model_output,
            implementation=result.implementation.node_sequence,
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
