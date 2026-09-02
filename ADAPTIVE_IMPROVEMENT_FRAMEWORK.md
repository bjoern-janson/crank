# Adaptive Improvement as Feedback-Conditioned Change in Future Reach Under Revisable Authorization

**STATUS: prospective design / admission framework**

This document specifies what a future CRANK experiment would have to establish
before CRANK should admit the label **adaptive improvement**.

It is **not** a runtime subsystem, a new causal component, a replacement for a
frozen experiment, or an empirical claim that adaptive improvement has already
been demonstrated. It adds no execution mechanism.

The current empirical machinery remains the evidentiary base:

```text
Phenomenon probe
    -> raw implementation I
    -> exogenous evaluation
    -> evidence / warrant
    -> Corrective Buffer
    -> canonical corrective state S_B
    -> Authority-Preserving Adapter
    -> admissible space
    -> downstream mechanism
    -> behavior
    -> environment / outcome
    -> temporal experience state
```

The present repository establishes experimental and architectural seams around
those layers; the future framework described here defines the admission burden
for a stronger claim.

## 1. Central distinction

CRANK should not collapse the following concepts:

```text
G_possible  = transitions available under specified execution conditions
G_auth      = transitions licensed under the applicable authority/constraints
G_realized  = transitions actually selected/executed
```

The basic relation is:

```math
G_{realized} \subseteq G_{possible} \cap G_{auth}
```

subject to the current state and execution conditions.

These are logical relations, not a required temporal pipeline. A transition can
be realized without establishing a general reachability claim, while a
reachability claim can be estimated from repeated controlled realizations.
Likewise, an observed behavioral change does not by itself establish that
possible transitions or authorization changed.

A useful richer representation of conditional authorization is:

```math
G_{auth} \subseteq S \times C \times A \times S
```

where authorization licenses an action or transition only under specified
state, context, action, and resulting-state conditions.

The existing `AuthorityAdapter` is only a restricted projection of this richer
relation. It maps canonical corrective state to constraint keys and then to an
admissible action space. This document does not propose replacing it with a
general governance engine.

## 2. What “adaptive improvement” would have to mean here

The intended future claim is not simply:

```text
behavior changed after feedback
```

and not merely:

```text
performance improved on the observed task
```

The candidate claim is narrower:

> **Adaptive improvement** is a feedback-conditioned revision that causally
> changes validated future reach while preserving access to corrective
> revision at the next time step.

For this framework, the key object is therefore a validated change in future
reachable consequences, not a direct assertion about an internal capability
latent.

A useful conceptual chain is:

```math
\boxed{
G_{possible} \rightarrow G_{auth} \rightarrow G_{realized}
}
```

followed, as a separate evidentiary layer, by:

```math
\boxed{
G_{realized}
\xrightarrow{controlled\ evaluation}
\Delta \mathcal R_{validated}
\xrightarrow{causal\ controls}
Cause(\Delta \mathcal R)
}
```

and finally by preservation of corrective access:

```math
\boxed{
Cause(\Delta\mathcal R)
\land
CorrAccess_{t+1}
\rightarrow
Admit_{CRANK}
}
```

Here `Admit_CRANK` is deliberately named for the framework rather than
`safe self-improvement`. The latter would presuppose a global safety result that
this experimental design does not establish.

## 3. Capability, reachability, authorization, and realization

A future experiment may need to distinguish at least four explanatory levels.

### 3.1 Intrinsic capability

Let `K` denote whatever latent capability construct a future study explicitly
defines and validates.

This document does not assume that such a latent is directly observable, nor
that a change in behavior is evidence of a change in `K`.

### 3.2 Possible transitions / future reach

Let `R(C,E,B,Theta)` denote the set of consequences or transition outcomes that
are operationally available under specified context, environment, resource,
and execution conditions.

The important point is that reach is an operational construct. It should not be
defined as everything that is physically conceivable, nor should it be inferred
from one successful execution.

A failed transition under one condition therefore does not establish permanent
foreclosure:

```math
x \notin \mathcal R(C,E,B)
\not\Rightarrow
x \notin \mathcal R(C',E',B')
```

The environment, resources, task, authorization, or other controlled
conditions may differ.

### 3.3 Authorization / licensed transition

Authorization determines which otherwise possible transitions are admissible
under the governing constraints.

The core anti-credit-leakage invariant is:

```text
produced(x) does not imply authorized(x -> y)
```

A component that generates an observation, candidate action, correction, or
proposal does not thereby acquire authority over the downstream transition.

### 3.4 Realization

A realization is an empirical execution of a selected transition under a
specified trial condition.

Realization is therefore evidence about what occurred. It is not itself proof
that the transition was generally reachable, intrinsically supported, or
properly authorized.

## 4. The non-implication ladder

The following shortcuts are explicitly denied:

```math
\Delta P(I_{raw})
\not\Rightarrow
\Delta\mathcal R
\not\Rightarrow
\Delta\mathcal R_{mechanism}
\not\Rightarrow
\Delta\mathcal K_{intrinsic}
```

The arrows here are **not** a proposed ordering of runtime events. They mark
claims that cannot be substituted for one another without additional evidence.

In particular:

```text
behavioral change        does not imply cause
production                does not imply authorization
failure                   does not imply foreclosure
observed anomaly          does not imply mechanism
realized transition      does not imply general reachability
reachability increase    does not imply intrinsic capability increase
```

These are protection rules for experimental attribution, authority, and
correction.

## 5. Raw observation remains primary custody

A future adaptive-improvement study must retain the same custody discipline
already used at Layer 0.

The primitive observation remains the raw implementation distribution, for
example:

```math
P(I_{raw}\mid X,C,\widetilde E,e,B,\Theta)
```

with the exact trial inputs, model/interface configuration, resource budget,
intervention assignment, raw output, and exogenous evaluation preserved.

Changes in this raw distribution can motivate downstream hypotheses, but they
must not silently become reach, mechanism, or capability claims.

The evidentiary order is:

```text
raw observation
    -> controlled evaluation
    -> supported transition facts
    -> reachability analysis
    -> causal attribution
```

The framework therefore keeps implementation-distribution evidence separate
from the stronger claim of future reach expansion.

## 6. Feedback-conditioned authorization revision

A future corrective experiment may establish a warranted authorization update
of the form:

```math
G_{auth}^{t} \rightarrow G_{auth}^{t+1}
```

provided that the revision follows the framework's external evidentiary path,
retains provenance, and does not self-certify its own authority.

The relevant causal route is conceptually:

```text
exogenous observation
    -> evaluation
    -> evidence / warrant
    -> corrective state
    -> authority-preserving admissibility update
    -> downstream execution
```

This preserves the existing causal separation. A mechanism may respond to an
admissible-space change, but the mechanism is not credited for authorizing the
change merely because it acts after it.

## 7. Future reach must be tested prospectively

A future experiment should define a held-out task family or other controlled
future test set before observing the relevant outcomes.

Conceptually, let:

```math
\mathcal R_t = \mathcal R(C_t,E_t,B_t,\Theta_t,G_{auth}^t)
```

and let the future evaluation target be a preregistered held-out condition
rather than a task chosen after the feedback is observed.

The object of interest is then something like:

```math
\Delta\mathcal R_{validated}
=
\mathcal R_{t+1,heldout}
-
\mathcal R_{t,heldout}
```

with the actual operational definition supplied by the future experiment.

This notation is prospective. The current repository does not instantiate a
`t_frozen` future-reach object or claim such a quantity has already been
measured.

## 8. Causal attribution burden

A future reach change should not be credited to feedback-conditioned revision
just because the change occurred after feedback.

The future study must distinguish at least:

```text
feedback exposure
revision mechanism
authorization state
alternative explanations
held-out future realization
```

A candidate result therefore requires a causal control structure capable of
supporting:

```math
Cause(\Delta\mathcal R,\text{feedback-conditioned revision})
```

rather than merely:

```math
\Delta\mathcal R \text{ observed after feedback}
```

This is the same causal discipline already used elsewhere in CRANK: no
component receives credit for a transition it does not itself implement and
experimentally identify.

## 9. Corrective access is part of the admission criterion

An improvement claim is incomplete if the system can improve once but can no
longer accept warranted correction afterward.

The future framework therefore requires preserved corrective access:

```math
CorrAccess_{t+1}
```

meaning that the post-revision system remains reachable through the intended
correction path and retains the provenance needed to revise the resulting
authorization when warranted.

This is not a claim of global corrigibility. It is a testable preservation
condition for the specific correction channel under study.

## 10. Anti-wireheading boundary

Improvement must be defined over an exogenous or independently adjudicated
outcome, not over a scalar that the mechanism can directly rewrite to make
itself look better.

The evaluator and metric therefore remain outside the mechanism being credited
with adaptive change.

Conceptually:

```text
mechanism output
    -> environment
    -> exogenous observation
    -> predeclared metric / evaluation
```

not:

```text
mechanism output
    -> mechanism-controlled score
    -> declared improvement
```

This preserves the distinction between achieving a consequence and altering the
measurement of that consequence.

## 11. Three protection layers

The framework can be summarized by three independent forms of epistemic
protection.

### Attribution protection

```math
\boxed{\text{behavior} \not\Rightarrow \text{cause}}
```

Behavioral change requires an experimental attribution argument.

### Authority protection

```math
\boxed{\text{production} \not\Rightarrow \text{authorization}}
```

Producing an artifact, candidate transition, or observation cannot by itself
mint authority over what happens next.

### Correction protection

```math
\boxed{\text{failure} \not\Rightarrow \text{foreclosure}}
```

A failed transition is evidence under its tested conditions, not automatic
proof that the corresponding outcome is globally impossible.

## 12. Prospective admission rule

For a future result, a useful conceptual admission predicate is:

```math
Admit_{CRANK}
=
\Delta\mathcal R_{validated}
\land
Cause(\Delta\mathcal R,\text{feedback-conditioned revision})
\land
CorrAccess_{t+1}
```

The notation means that all three burdens must be met:

1. **validated reach change** — the future evaluation establishes a preregistered
   change in operationally defined reach;
2. **causal attribution** — controlled evidence identifies feedback-conditioned
   revision as the cause of that change, rather than merely its temporal
   predecessor;
3. **corrective access preserved** — the resulting system retains the intended
   correction path and provenance.

The corresponding conceptual definition is:

```math
\boxed{
\text{adaptive improvement}
=
\text{validated reach change}
+
\text{warranted causal attribution}
+
\text{preserved corrective access}
}
```

The plus signs are logical conjunction, not a numeric score.

## 13. What this framework does not establish

This document does **not** establish any of the following in the present
repository state:

```text
- adaptive improvement
- general capability growth
- intrinsic capability increase
- mechanism-specific reach expansion
- globally safe self-improvement
- universal corrigibility
- unrestricted governance
- alignment in the broad sense
```

It also does not authorize changing the frozen Layer-0 preregistration,
temporal experiment, corrective-buffer baseline, adapter baseline, or existing
environment artifacts.

## 14. Intended experimental progression

The intended future progression is therefore:

```text
Layer 0:
  raw implementation distribution under controlled intervention

Temporal revision:
  behavior changes through explicit, revisable experience state

Future adaptive-improvement assay:
  feedback-conditioned revision
      -> validated held-out future reach change
      -> causal attribution
      -> corrective access preserved
      -> Admit_CRANK
```

The transitions between these stages are evidentiary transitions, not automatic
consequences of architectural proximity.

## 15. Final claim ceiling

Until a future experiment satisfies the admission rule above, CRANK should say
only that it has established the relevant infrastructure, causal separations,
correction pathways, execution custody, and temporal revision mechanisms that
make the stronger test possible.

The intended discipline is simple:

```text
Do not call a behavior change adaptive improvement.
Do not call a reach change capability growth.
Do not call production authorization.
Do not call failure permanent foreclosure.
Do not call an observed anomaly its mechanism.
```

The future experiment earns the stronger label only by satisfying its own
precommitted evidentiary burden.

---

**Scope note:** This is a prospective design specification. It intentionally
adds no runtime mechanism and makes no empirical adaptive-improvement claim
about the current CRANK repository.
