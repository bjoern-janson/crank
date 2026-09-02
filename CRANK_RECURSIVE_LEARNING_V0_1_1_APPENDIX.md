# CRANK — Recursive Learning-Operator Revision
## Minimal Finite Assay v0.1.1 — Mechanical Appendix Revision

**Status:** prospective specification. This file supersedes the mechanical definitions in `CRANK_RECURSIVE_LEARNING_V0_1_APPENDIX.md` wherever they conflict with this revision. No learner execution is authorized until the pre-execution certificates generated from this contract pass.

This revision changes only mechanical definitions. The scientific question, four update loci, four-class structure, recurrence witness, same-evidence design, held-out evaluation, and correction requirement remain frozen.

---

## 1. Frozen scientific object

\[
\boxed{\mathcal L_t:(S_t,x_t,o_t)\rightarrow S_{t+1}}
\]

\[
\boxed{\mathcal L_{t+1}=\mathcal R(\mathcal L_t,S_t,S_{t+1},e_t)}
\]

The four update loci remain:

\[
\boxed{\Delta M,\quad\Delta A,\quad\Delta F,\quad\Delta\mathcal L}
\]

The experiment asks:

\[
\boxed{\textbf{Can consequence change the rule that determines how future consequence changes the system?}}
\]

---

## 2. Finite world

A task input is:

```text
TaskInput = (context_bit, values)
```

where:

\[
context\_bit\in\{0,1\}
\]

and:

\[
values\in\{0,1,2\}^n,\qquad1\le n\le4.
\]

The complete input-key domain is:

\[
D=\{0,1\}\times\bigcup_{n=1}^{4}\{0,1,2\}^n
\]

with:

\[
|D|=240.
\]

Outputs are finite sequences over `{0,1,2}` with length bounded by four.

---

## 3. Initial frame and finite procedure language

The initial frame is:

```text
F0 = {
    identity,
    reverse,
    sort_asc,
}
```

Primitive semantics are exactly:

```text
identity(x)          = x
reverse(x)           = reverse(x)
sort_asc(x)          = nondecreasing sort(x)
keep_even_values(x)  = subsequence of values v with v mod 2 == 0
keep_odd_values(x)   = subsequence of values v with v mod 2 == 1
```

`keep_even_values` and `keep_odd_values` are not members of `F0`.

The procedure-selector hypothesis space is:

\[
\boxed{
\mathcal H_A=
\{\texttt{always_identity},\texttt{always_reverse},\texttt{select_on_c}\}
}
\]

with:

```text
always_identity(x,c) = identity(x)
always_reverse(x,c)   = reverse(x)
select_on_c(x,c)      = identity(x) if c=0 else reverse(x)
```

A selector may reference only primitives present in the current frame.

---

## 4. Finite memory grammar

A memory state contains zero or one exact override:

```text
M = {} | {(TaskInput, OutputSequence)}
```

The complete memory hypothesis space is:

\[
\boxed{
\mathcal H_M
=\{\varnothing\}\cup\{\operatorname{override}(d,y):d\in D,\ y\in Y_d\}
}
\]

where `Y_d` is the finite output space for input key `d`.

Therefore:

\[
|\mathcal H_M|=1+2\sum_{n=1}^4 3^{2n}=14{,}761.
\]

A memory update can add or replace only one entry.

Memory cannot encode a selector, add a primitive, modify frame membership, or modify operator dispatch.

---

## 5. Finite frame grammar and construction semantics

The optional primitive set is:

```text
Poptional = {
    keep_even_values,
    keep_odd_values,
}
```

The frame-update hypothesis space is:

\[
\boxed{
\mathcal H_F=
\{F_0,F_{even},F_{odd}\}
}
\]

where:

```text
F_even = F0 ∪ {keep_even_values}
F_odd  = F0 ∪ {keep_odd_values}
```

A frame update is constructive, not merely declarative.

For a frame `F`, the canonical construction space is the set of one-step executable procedures whose primitive is a member of `F`:

\[
\mathcal H(F)=\{\text{canonical one-primitive procedures using primitives in }F\}.
\]

The construction operation induced by `F_even` deterministically exposes:

```text
keep_even_values
```

as an executable procedure in `H(F_even)` within the same update event.

Likewise `F_odd` exposes `keep_odd_values`.

No separate `A` mutation is credited for this exposure. The current procedure selector is recomputed from the frozen construction semantics after a frame update; this recomputation is not an independent update event and carries no `A` credit.

Thus:

\[
\boxed{
\Delta F\Rightarrow\text{new constructible procedure}
}
\]

without implying:

\[
\Delta F+\Delta A.
\]

The procedure space is:

\[
\mathcal H(F_0)=\{identity,reverse,sort\_asc\}
\]

\[
\mathcal H(F_{even})=\mathcal H(F_0)\cup\{keep\_even\_values\}
\]

\[
\mathcal H(F_{odd})=\mathcal H(F_0)\cup\{keep\_odd\_values\}.
\]

No composition is available.

---

## 6. Contract-relative minimality

The frozen depth ordering is:

\[
\operatorname{depth}(M)=0,
\quad
\operatorname{depth}(A)=1,
\quad
\operatorname{depth}(F)=2,
\quad
\operatorname{depth}(\mathcal L)=3.
\]

For a witness `W` and finite grammar/budget pair `(G,B)`,

\[
\operatorname{MinFix}_{(G,B)}(W)
\]

is the minimum-depth update locus for which an element of the finite hypothesis space produces a contract-valid result over the complete witness.

All competing finite candidate spaces are enumerated before learner execution.

---

## 7. Finite operator language

The operator domain is:

\[
K=\{k_M,k_A,k_F,k_{\mathcal L}\}.
\]

Operators map each key to one locus:

\[
\mathcal L(k)\in\{M,A,F,\mathcal L\}.
\]

Thus:

\[
|\mathcal H_{\mathcal L}|=4^4=256.
\]

The initial operator is:

\[
\boxed{
\mathcal L_0:
(k_M\mapsto M,\ k_A\mapsto M,\ k_F\mapsto M,\ k_{\mathcal L}\mapsto M)
}
\]

An operator revision may mutate at most one dispatch entry:

\[
|\mathcal H_{\mathcal L}^{(1)}(\mathcal L)|=13.
\]

No revision may add a new class or update primitive.

---

## 8. Bounded state and update budget

```text
R_t : one current task input
F_t : one finite frame
A_t : one finite procedure selector
M_t : zero or one exact override
C_t : immutable evidence history, at most four records
Q_t : fixed protected adjudication boundary
```

The per-event update budget is:

\[
\boxed{B_{update}=1.}
\]

Exactly one primary update locus can be credited for each failure event.

No hidden state, wall-clock value, ambient RNG, hidden seed, or external mutable state may affect canonical transitions.

---

## 9. Exact learner-visible evidence

The learner-visible evidence is **not** the target output.

For each event, the exact learner-visible object is:

```text
Evidence = {
    "event_id": str,
    "episode_index": int,
    "context_bit": 0 | 1,
    "input_batch": tuple[TaskInput, ...],
    "observed_output_batch": tuple[OutputSequence, ...],
    "consequence": ConsequenceRecord,
    "prior_evidence": tuple[EvidenceDigest, ...],
}
```

`ConsequenceRecord` is finite and contains only evaluator-observed predicates:

```text
ConsequenceRecord = {
    "success": bool,
    "lengths_preserved": bool,
    "value_membership_valid": bool,
    "order_relation": one of {"unchanged", "reversed", "nondecreasing", "other"},
    "context_consistency": bool,
}
```

These predicates are computed from the environment's declared consequence relation and the observed output. They never contain:

```text
expected_outputs
world_class
required_minimal_locus
class token
operator target
```

The evaluator may retain:

```text
expected_outputs
world_class
required_minimal_locus
lower_level_exclusion_certificate
```

as private custody objects for scoring and certification.

The exact target output therefore cannot be recovered directly from a learner-facing field.

All arms receive byte-identical evidence:

\[
\boxed{e_t^{(M)}=e_t^{(A)}=e_t^{(F)}=e_t^{(L)}}.
\]

The only additional Arm-L permission is:

```text
PermitOperatorRevision = 1
```

---

## 10. Learner diagnosis

The learner computes:

\[
\boxed{\hat k_t=\operatorname{Diagnose}(e_t,S_t)}.
\]

The evaluator-side `world_class` is never passed to diagnosis.

Diagnosis uses the finite candidate languages and the learner-visible consequence predicates.

For a single-event witness, a candidate locus is diagnostically admissible when the current evidence is consistent with at least one contract-valid repair in that locus's finite candidate language.

For the recurrent episode, the diagnosis is computed only after the complete four-event sequence has been observed.

The learner records both:

```text
k_hat
```

and a digest of the evidence used for diagnosis.

The evaluator separately records:

```text
k_world
```

for post hoc scoring.

---

## 11. Witness `k_M`

The single-event witness is:

```text
context_bit = 0
input        = [2,0,1]
required     = [2,1,0]       # evaluator custody only
```

The current procedure is `identity`.

One exact memory override solves the witness under the frozen contract.

Therefore the pre-certificate must establish:

\[
\boxed{\operatorname{MinFix}_{(G,B)}(k_M)=M.}
\]

---

## 12. Witness `k_A`

The single-event witness is a two-subtask context-conditioned batch:

```text
(c=0, [0,1,2]) → [0,1,2]
(c=1, [0,1,2]) → [2,1,0]   # evaluator custody only
```

Both identity and reverse are already available in `F0`.

`select_on_c` solves the complete batch.

A memory state contains only one exact override and therefore cannot solve both subtasks in one update event.

The pre-certificate must establish:

\[
\boxed{\operatorname{MinFix}_{(G,B)}(k_A)=A.}
\]

---

## 13. Witness `k_F`

The single-event witness is:

```text
[0,1,2,2] → [0,2,2]
[2,0,1,1] → [2,0]       # evaluator custody only
```

The target transformation is `keep_even_values`.

Before the update:

\[
\boxed{
\forall P\in\mathcal H(F_0),
\exists x\text{ in the witness}:P(x)\ne keep\_even\_values(x).
}
\]

The one-entry memory language is insufficient for the two-subtask batch.

After a frame update:

\[
F_{even}=F_0\cup\{keep\_even\_values\}
\]

and the construction semantics expose the new procedure immediately:

\[
\boxed{keep\_even\_values\in\mathcal H(F_{even}).}
\]

The pre-certificate must therefore establish:

\[
\boxed{\operatorname{MinFix}_{(G,B)}(k_F)=F.}
\]

---

## 14. Recursive witness

The exact four-event witness is:

\[
\boxed{W_{\mathcal L}=(k_M,k_F,k_M,k_F).}
\]

Exactly four events occur.

The initial dispatch routes both ordinary classes to memory:

\[
\mathcal L_0(k_M)=M,
\qquad
\mathcal L_0(k_F)=M.
\]

The `k_F` lower-level minimum is `F`.

Because the memory grammar contains at most one override and the two `k_F` events each contain two subtasks, no lower-level trace can solve the complete four-event witness while preserving both `k_M` events under the one-update budget.

The recursive hypothesis is therefore that the repeated conflict is a property of dispatch rather than another missing memory entry.

The operator revision candidate is:

\[
\boxed{
\mathcal L_1(k_M)=M,
\quad
\mathcal L_1(k_A)=M,
\quad
\mathcal L_1(k_F)=F,
\quad
\mathcal L_1(k_{\mathcal L})=M.
}
\]

---

## 15. Lower-level exhaustive exclusion

Define:

\[
\mathcal H_{M,A,F}^{(B,W_{\mathcal L})}
\]

as every four-event execution trace generated by the finite memory, procedure, and frame languages under:

- frozen `L0` dispatch;
- the exact four-event witness;
- one primary update per event;
- bounded state;
- no operator mutation.

The required certificate is:

\[
\boxed{
\forall h\in\mathcal H_{M,A,F}^{(B,W_{\mathcal L})},
\quad
h\not\models W_{\mathcal L}^{future\_repair}.
}
\]

Here `models` means that all four witness events are contract-valid, including both `k_M` batches and both two-subtask `k_F` batches.

The certificate must enumerate all distinct canonical lower-level traces; duplicate traces after canonicalization are counted once.

The certificate must record any maximal partial repairs encountered.

The lower-level exclusion is a pre-execution artifact and cannot be changed after observing learner behavior.

---

## 16. Canonicalization and exhaustive operator equivalence

Canonical serialization is UTF-8 JSON with:

```python
json.dumps(
    value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)
```

SHA-256 over canonical UTF-8 bytes is the identity digest.

Two operators are equivalent iff their complete canonical transitions agree over the finite operator domain:

\[
\boxed{
\mathcal L_i\equiv\mathcal L_j
\iff
\forall d\in\mathcal D_{op},
\operatorname{canon}(\mathcal L_i(d))
=
\operatorname{canon}(\mathcal L_j(d)).
}
\]

Each canonical transition contains at least:

```text
diagnosis key
selected update locus
resulting canonical state transition
```

The positive mechanism criterion is:

\[
\boxed{\mathcal L_1\not\equiv\mathcal L_0.}
\]

---

## 17. Experimental arms and evidence invariance

The four arms remain:

```text
M: permits M only
A: permits M + A
F: permits M + A + F
L: permits M + A + F + operator revision
```

All arms receive identical:

```text
Evidence
Theta
B
E_eval
chronology
future generator
correction generator
```

Only Arm L has:

```text
PermitOperatorRevision = 1
```

No recursive-arm diagnostic advantage is permitted.

---

## 18. Post-induction freeze and future curriculum

After induction, the recursive successor and all post-induction ordinary state are frozen.

Only after this freeze is the future curriculum generated.

The fixed future seed is:

```text
crank-rlo-v0.1/future/v1
```

The deterministic SHA-256 counter stream is:

```text
block_i = SHA256(seed_utf8 || b":" || decimal(i).encode("ascii"))
```

The future curriculum contains exactly 12 events in three four-event episodes.

No treatment output is accessible to the future generator.

---

## 19. Future reach

For each frozen arm define:

\[
\mathcal R_{future}(arm,H^*)
\]

as the set of task IDs whose complete contract is satisfied.

The recursive positive difference is:

\[
\boxed{
\Delta\mathcal R^+_{\mathcal L}
=
\mathcal R_{future}(L,H^*)
\setminus
\mathcal R_{future}(L_0[H],H^*)
}
\]

with directional loss recorded separately.

The primary future criterion is:

\[
\boxed{\Delta\mathcal R^+_{\mathcal L}\ne\varnothing.}
\]

---

## 20. Correction challenge

After future evaluation is frozen, the recursive successor receives an independent correction challenge.

The fixed correction seed is:

```text
crank-rlo-v0.1/correction/v1
```

The correction schedule is:

```text
(k_A, k_A, k_A, k_A)
```

The external evaluator independently certifies the lower-level minimum for this recurrence as `A`.

The retained `L1` routes `k_A -> M` and therefore faces an externally adjudicated repeated conflict.

A successful correction path must produce:

\[
\boxed{\mathcal L_2(k_A)=A}
\]

through the independently adjudicated route.

The correction criterion is:

\[
\boxed{\operatorname{CorrReach}(\mathcal L_1,Q)>0.}
\]

---

## 21. Required pre-execution certificates

Before any learner execution, the following must exist:

```text
MINFIX_KM_CERTIFICATE.json
MINFIX_KA_CERTIFICATE.json
MINFIX_KF_CERTIFICATE.json
MINFIX_KL_LOWER_EXCLUSION.json
OPERATOR_DOMAIN_MANIFEST.json
CANONICALIZATION_SPEC.json
```

Each certificate must include:

- finite hypothesis-space cardinality;
- enumerator identity;
- complete candidate hashes;
- complete pass/fail outcomes;
- witness hashes;
- lower-level exclusion result where applicable;
- certificate hash.

No learner output may influence these artifacts.

---

## 22. Interpretation taxonomy

The frozen interpretation rules remain:

\[
\hat k\ne k^{world}\Rightarrow\text{decoding failure}
\]

\[
\hat k=k^{world}\land\mathcal L(\hat k)\ne L^*\Rightarrow\text{selection failure}
\]

\[
\mathcal L(\hat k)=L^*\land S'\text{ fails}\Rightarrow\text{execution failure}
\]

\[
S'\text{ succeeds}\land\mathcal L'\equiv\mathcal L\Rightarrow\text{non-recursive adaptation}
\]

\[
\mathcal L'\not\equiv\mathcal L\Rightarrow\text{operator revision}
\]

\[
\mathcal L'\not\equiv\mathcal L\land\Delta\mathcal R^+\ne\varnothing\Rightarrow\text{recursive consequence}
\]

\[
\text{previous conditions}\land\operatorname{CorrReach}>0\Rightarrow\text{corrigible recursive learning}
\]

A null result terminates at the earliest unsupported causal transition.

---

## 23. Explicit non-claims

No positive result establishes:

```text
general intelligence
open-endedness
unrestricted self-improvement
general-purpose meta-learning
general-purpose transfer
intrinsic capability increase
```

---

## 24. No learner execution authorization

This appendix does not authorize learner execution by itself.

Execution is authorized only if all pre-execution certificates pass against this exact appendix revision.

The experimental order is:

```text
freeze mechanical appendix
    ↓
enumerate finite spaces
    ↓
generate and verify pre-execution certificates
    ↓
if and only if all pass:
    execute controls + recursive treatment
    ↓
externally retain/reject candidate operator
    ↓
freeze
    ↓
generate H*
    ↓
evaluate future reach
    ↓
correction challenge
    ↓
interpret earliest failed causal boundary
```
