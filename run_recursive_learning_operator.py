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
    before = learner.state.operator
    revision_candidate_count = None
    supported_candidate_count = None
    if arm == "L":
        candidates = rlo.one_entry_revisions(before)
        supported = [c for c in candidates if rlo.candidate_replay(c, rlo.Evaluator())]
        revision_candidate_count = len(candidates)
        supported_candidate_count = len(supported)
        learner.revise_operator()
        if supported_candidate_count != 1:
            raise AssertionError(f"operator revision is not unique: {supported_candidate_count}")
    after = learner.state.operator
    success_ids: list[str] = []
    failure_ids: list[str] = []
    for episode_index, episode in enumerate(rlo.generate_future()):
        for event_index, batch in enumerate(episode):
            ok, _ = learner.future_event(batch, episode_index * 4 + event_index)
            task_id = rlo.digest({"future_index": episode_index * 4 + event_index, "task_ids": [t.task_id for t in batch]})
            (success_ids if ok else failure_ids).append(task_id)
    result = {
        "arm": arm,
        "operator_before_id": rlo.operator_id(before),
        "operator_after_id": rlo.operator_id(after),
        "operator_changed": not rlo.equivalent(before, after),
        "future_success_count": len(success_ids),
        "future_failure_count": len(failure_ids),
        "future_success_task_ids": success_ids,
        "future_failure_task_ids": failure_ids,
    }
    if arm == "L":
        result["revision_candidate_count"] = revision_candidate_count
        result["supported_candidate_count"] = supported_candidate_count
    return result


def main() -> None:
    require_pre_certificates()
    arms = [run_arm(arm) for arm in ("M", "A", "F", "L")]
    recursive = next(item for item in arms if item["arm"] == "L")
    frame = next(item for item in arms if item["arm"] == "F")
    results = {
        "manifest": "CRANK_RLO_EXECUTION_v0.2",
        "pre_execution_gate": "PASS",
        "arms": arms,
        "primary": {
            "operator_revision": bool(recursive["operator_changed"]),
            "operator_revision_unique": recursive.get("supported_candidate_count") == 1,
            "frame_control_future_success_count": frame["future_success_count"],
            "recursive_future_success_count": recursive["future_success_count"],
            "recursive_vs_frame_future_success_delta": recursive["future_success_count"] - frame["future_success_count"],
        },
        "correction": {
            "challenge_seed": rlo.SEED_CORRECTION,
            "executed": False,
            "corrigibility_claim_status": "UNTESTED",
        },
        "learner_execution_performed": True,
    }
    Path("RLO_EXECUTION_RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
