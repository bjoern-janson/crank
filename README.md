# CRANK

A causally separated experimental framework for studying context-sensitive
model behavior, corrective state, authority-preserving admissibility,
downstream behavior, environmental consequence, and temporal experience.

## Layer-0 phenomenon assay

The frozen primitive is:

```text
(X, C, e, B, Theta) -> raw implementation I -> exogenous evaluator A(I,E)
```

`raw_model_output` is the primary outcome custody object. Parsing and
exogenous evaluation happen only after capture. The probe does not claim a
mechanism, frame, learning effect, representation change, capability
expansion, or improvement merely from an observed distributional difference.

## Experimental atom

Every executed trial is represented by a `TrialSpec` in `trial_contract.py`:

```text
tau = (X0, C, e, B, Theta, E_spec) -> I -> A(I,E)
```

The atom explicitly binds:

- `X`: first-class initial task state
- `C`: exact context custody object
- `e`: intervention assignment
- `B`: resource budget
- `Theta`: model/interface configuration
- `E_spec`: evaluator contract
- assignment seed

The exact rendered model-visible input is preserved. `trial_id` is the
SHA-256 of the canonical pre-execution TrialSpec and therefore does not depend
on the model outcome. `input_hash` binds the rendered input. After capture,
`observation_hash` binds the trial specification, raw output, and derived
evaluation record.

## Four-cell Layer-0 design

```text
             e0             e1
C0        baseline       perturbation
C1        baseline       perturbation
```

`e1` is an exogenous evaluator/environment change. Its edge-specific content
is deliberately absent from the model-visible prompt so the intervention does
not become an unintended textual cue.

`C0` and `C1` are concrete custody objects with equal character footprint in
v0.1. Exact token equality is measured at execution with the selected
model/tokenizer and is recorded as metadata rather than assumed from text
length.

The deterministic assignment helper uses domain-separated SHA-256 seeds and
balanced replication across all four cells. It has no dependence on model
outputs or a mutable global RNG.

## Observation and analysis custody

The execution boundary is:

```text
TrialSpec
  -> rendered_input
  -> raw_model_output
  -> post-hoc parse
  -> frozen exogenous evaluation
  -> immutable observation
```

Raw observations are never rewritten. Derived analyses consume the recorded
observations; they do not change their custody objects.

`PHENOMENON_PROBE_PREREGISTRATION.json` is synchronized with the executable
trial contract. `LAYER0_TRIAL_SCHEMA.json` defines the machine-readable trial
and observation envelope. `LAYER0_EXECUTION_MANIFEST.template.json` is a
pre-execution manifest template; it is not empirical data.

## Full causal stack

```text
Phenomenon probe
    -> raw I
    -> exogenous evaluation
    -> evidence / warrant
    -> Corrective Buffer
    -> canonical S_B
    -> Authority-Preserving Adapter
    -> admissible space A
    -> downstream mechanism
    -> behavior
    -> environment / outcome
    -> experience
    -> explicit temporal state
```

The anti-credit-leakage rule is:

```text
No component receives credit for a causal transition it does not itself
implement and experimentally identify.
```

## Frozen boundary

Existing temporal-revisability, corrective-buffer, adapter, and environment
artifacts are retained as frozen baselines. The Layer-0 trial contract is an
execution/custody layer around the phenomenon probe; it does not rewrite the
frozen causal components.

## Current claim ceiling

```text
Infrastructure: established.
Layer-0 phenomenon effect: untested.
```

No model-generated dataset is committed by this repository state.

## Verification

Run:

```bash
python -m unittest discover -v
```

The Layer-0 specification is frozen in
`PHENOMENON_PROBE_PREREGISTRATION.json` and the trial contract in
`TRIAL_CONTRACT_PREREGISTRATION.json`.
