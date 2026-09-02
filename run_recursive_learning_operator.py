from __future__ import annotations

import json
from pathlib import Path

import recursive_learning_operator as rlo

CERTS = (
    "MINFIX_KM_CERTIFICATE.json",
    "MINFIX_KA_CERTIFICATE.json",
    "MINFIX_KF_CERTIFICATE.json",
    "MINFIX_KL_LOWER_EXCLUSION.json",
)


def require_pre_certificates() -> None:
    root = Path(__file__).resolve().parent
    for name in CERTS:
        data = json.loads((root / name).read_text(encoding="utf-8"))
        if data.get("status") != "PASS":
            raise RuntimeError(f"pre-execution gate failed: {name}")
        if data.get("learner_execution_performed") is not False:
            raise RuntimeError(f"invalid pre-certificate custody field: {name}")


def run_arm(arm: str) -> dict[str, object]:
    learner = rlo.Learner(arm, rlo.Evaluator())
    for index, cls in enumerate(rlo.W_L):
        learner.induction_event(rlo.WITNESS[cls], index)
    induction_operator_id = rlo.operator_id(learner.pre_revision_operator)
    if arm == "L":
        learner.revise_operator()
    post_operator_id = rlo.operator_id(learner.state.operator)
    success_ids: list[str] = []
    failure_ids: list[str] = []
    for episode_index, episode in enumerate(rlo.generate_future()):
        for event_index, batch in enumerate(episode):
            ok, _ = learner.future_event(batch, episode_index * 4 + event_index)
            task_id = rlo.digest({"future_index": episode_index * 4 + event_index, "task_ids": [t.task_id for t in batch]})
            (success_ids if ok else failure_ids).append(task_id)
    return {
        "arm": arm,
        "operator_before_id": induction_operator_id,
        "operator_after_id": post_operator_id,
        "operator_changed": not rlo.equivalent(learner.pre_revision_operator, learner.state.operator),
        "future_success_count": len(success_ids),
        "future_failure_count": len(failure_ids),
        "future_success_task_ids": success_ids,
        "future_failure_task_ids": failure_ids,
    }


def main() -> None:
    require_pre_certificates()
    arms = [run_arm(arm) for arm in ("M", "A", "F", "L")]
    recursive = next(item for item in arms if item["arm"] == "L")
    shadow = next(item for item in arms if item["arm"] == "F")
    op1 = tuple((k, "F" if k == "k_F" else "M") for k in rlo.KEYS)
    op2 = rlo.correction_candidate(op1)
    results = {
        "manifest": "CRANK_RLO_EXECUTION_v0.1",
        "pre_execution_gate": "PASS",
        "arms": arms,
        "primary": {
            "operator_revision": bool(recursive["operator_changed"]),
            "operator_not_revised_shadow": not bool(shadow["operator_changed"]),
            "recursive_future_success_count": recursive["future_success_count"],
            "shadow_future_success_count": shadow["future_success_count"],
        },
        "correction": {
            "challenge_seed": rlo.SEED_CORRECTION,
            "pre_operator_id": rlo.operator_id(op1),
            "corrected_operator_id": rlo.operator_id(op2),
            "operator_changed": not rlo.equivalent(op1, op2),
            "corr_reach": not rlo.equivalent(op1, op2),
        },
        "learner_execution_performed": True,
    }
    Path("RLO_EXECUTION_RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
