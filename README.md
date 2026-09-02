# CRANK

A causally separated experimental framework for studying context-sensitive
model behavior, corrective state, authority-preserving admissibility,
downstream behavior, environmental consequence, and temporal experience.

## Layer-0 phenomenon assay

The frozen primitive is:

```text
(X, C, E_tilde, e, B, Theta) -> raw implementation I -> exogenous evaluator A(I,E_eval)
```

`E_tilde` is the model-visible current environment state. `E_eval` is the
exogenous evaluator environment. For the environment-intervention assay,
e0/e1 must change `E_tilde` as well as the evaluator contract. The model sees
the current graph/state, not a textual description of the removed edge.

`raw_model_output` is the primary outcome custody object. Parsing and
exogenous evaluation happen only after capture. The probe does not claim a
mechanism, frame, learning effect, representation change, capability
expansion, or improvement merely from an observed distributional difference.

## Experimental atom

Every executed trial is represented by a `TrialSpec` in `trial_contract.py`:

```text
tau = (X0, C, E_tilde, e, B, Theta, E_eval_spec) -> I -> A(I,E_eval)
```

The atom explicitly binds:

- `X`: first-class initial task state
- `C`: exact context custody object
- `E_tilde`: model-visible current environment state
- `e`: intervention assignment
- `B`: hard resource budget
- `Theta`: model/interface configuration and session policy
- `E_eval_spec`: exogenous evaluator contract
- assignment seed

The exact rendered model-visible input is preserved. `trial_id` is the
SHA-256 of the canonical pre-execution TrialSpec and therefore does not depend
on the model outcome. `input_hash` binds the rendered input. After capture,
`observation_hash` binds the trial specification, raw output, and derived
evaluation record. Execution timestamp is explicitly non-custodial metadata.

## Four-cell Layer-0 design

```text
             e0             e1
C0        baseline       perturbation
C1        baseline       perturbation
```

The intervention is now observable through the current environment state:

```text
E0: S->A->B->G, S->C->D->G, S->E->F->G
E1: S->A   B->G, S->C->D->G, S->E->F->G
```

The rendered input must differ between e0 and e1 while containing no textual
instruction naming the changed edge and no supplied alternative path.

`C0` is the neutral control. `C1` is a matched non-frame semantic placebo;
it contains neutral graph-label context rather than a procedural instruction
such as `check format first`. Character count is recorded, but exact token
equality must be measured with the concrete model/tokenizer.

The deterministic assignment helper uses domain-separated SHA-256 seeds and
balanced replication across all four cells. It has no dependence on model
outputs or a mutable global RNG.

## Execution controls

Every trial declares `session_policy=fresh_independent_trial`; a concrete
runner must start without prior conversation history. `ResourceBudget` is a
hard execution contract, and provider-reported usage must satisfy its limits.
Model identity includes provider, model, version, system instructions,
decoding, tool settings, reasoning settings, and session policy.

## Observation and analysis custody

The execution boundary is:

```text
TrialSpec
  -> rendered_input with E_tilde
  -> raw_model_output
  -> post-hoc parse
  -> frozen exogenous evaluation against E_eval
  -> immutable observation
```

Raw observations are never rewritten. Derived analyses consume the recorded
observations; they do not change their custody objects. Layer-0 results must be
frozen before being supplied to downstream CRANK components.

## Possible, licensed, and realized transitions

CRANK distinguishes three relations that must not be inferred from one
another merely from observed behavior:

```text
G_possible  -> transitions available from the current environment/task
G_auth      -> transitions admissible under the applicable authority/constraints
G_realized  -> transitions actually selected/executed by the downstream system
```

As an organizing decomposition:

```math
G_realized subseteq G_possible ∩ G_auth
```

subject to the current state and other execution conditions. An observed
increase in realized behavior therefore does not by itself establish a change
in capability, possible transitions, or authorization. In particular,
behavioral revision can occur while authorization remains fixed.

The current `AuthorityAdapter` is a restricted projection of this richer
conditional authorization relation: `CorrectiveState -> constraint keys ->
AdmissibleSpace`. It is not a general-purpose governance engine.

The corresponding governance abstraction is:

```math
G_auth subseteq S × C × A × S
```

where an authorization licenses a scoped transition only under specified
conditions. The abstraction is descriptive of the existing seams; it does not
add a new subsystem.

The current corrigibility interpretation is likewise descriptive:

```math
G_auth^t -> G_auth^(t+1)
```

where a warranted correction may revise previously admissible transitions
while retaining provenance for the revision. This should not be conflated
with temporal experience state, which can change action selection while the
authorization relation remains constant.

The organizing primitives are:

```text
Governance:
  control over the conditional admissibility of transitions.

Corrigibility:
  revisable transition authorization with persistent provenance.
```

A core anti-credit-leakage invariant is therefore:

```text
produced(x) does not imply authorized(x -> y)
```

and, more generally, no transition should acquire binding force merely because
the process that produced its input also claims authority over that transition.

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
Observable-intervention contract: established.
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
