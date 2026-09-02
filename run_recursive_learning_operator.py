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


def main() -> None:
    require_pre_certificates()
    results = {
        "manifest": "CRANK_RLO_EXECUTION_v0.1",
        "pre_execution_gate": "PASS",
        "arms": [rlo.run_arm(a) for a in ("M", "A", "F", "L")],
    }
    # Deliberately record, but do not post-process, the independent correction path.
    op1 = dict(rlo.initial_state().operator)
    op1["k_F"] = "F"
    op1 = tuple((k, op1[k]) for k in rlo.KEYS)
    op2 = dict(op1)
    op2["k_A"] = "A"
    op2 = tuple((k, op2[k]) for k in rlo.KEYS)
    results["correction"] = {
        "challenge_seed": rlo.SEED_CORRECTION,
        "pre_operator_id": rlo.operator_id(op1),
        "corrected_operator_id": rlo.operator_id(op2),
        "operator_changed": not rlo.equivalent(op1, op2),
        "corr_reach": not rlo.equivalent(op1, op2),
    }
    Path("RLO_EXECUTION_RESULTS.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
