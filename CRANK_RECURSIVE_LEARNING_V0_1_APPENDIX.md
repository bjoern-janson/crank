# CRANK — Recursive Learning-Operator Revision
## Minimal Finite Assay v0.1 — Mechanical Appendix

**Status:** prospective specification. No implementation result is implied.

This appendix closes the finite mechanical definitions required by the scientific preregistration. It does not modify CRANK-IL, CRANK-DEL, the existing corrective-buffer experiments, or the Layer-0 assay.

---

## 1. Frozen question

\[
\boxed{\textbf{Can consequence change the rule that determines how future consequence changes the system?}}
\]

The target transition is:

\[
\boxed{\mathcal L_t\xrightarrow{e_t}\mathcal L_{t+1}}
\]

where the ordinary state transition and operator-revision transition remain separate:

\[
S_{t+1}=\mathcal L_t(S_t,x_t,o_t)
\]

\[
\mathcal L_{t+1}=\mathcal R(\mathcal L_t,S_t,S_{t+1},e_t).
\]

The assay distinguishes four update loci:

\[
\boxed{\Delta M,\quad\Delta A,\quad\Delta F,\quad\Delta\mathcal L}
\]

and four causal interpretation boundaries:

```text
decoding → update selection → update execution → operator revision
```

A positive recursive result additionally requires future consequence and a live correction route.

---

## 2. Finite base world

A task input is:

```text
TaskInput = (context_bit, values)
```

with:

\[
context\_bit\in\{0,1\}
\]

and:

\[
values\in\{0,1,2\}^n,\qquad 1\le n\le4.
\]

Thus the complete key domain is finite:

\[
D=\{0,1\}\times\bigcup_{n=1}^{4}\{0,1,2\}^n.
\]

There are:

\[
|D|=2(3+9+27+81)=240
\]

possible task-input keys.

Outputs are sequences over the same alphabet and the same length as the corresponding input.

---

## 3. Frozen initial frame and procedure state

The initial constructive frame is:

```text
F0 = {
    identity,
    reverse,
    sort_asc,
}
```

Primitive semantics:

```text
identity(x)         = x
reverse(x)          = x in reverse order
sort_asc(x)         = x sorted in nondecreasing order
keep_even_values(x) = every element v with v mod 2 == 0, preserving order
keep_odd_values(x)  = every element v with v mod 2 == 1, preserving order
```

`keep_even_values` and `keep_odd_values` are not members of `F0`.

The initial executable selector is:

```text
A0 = always_identity
```

The current procedure-selection language is finite and contains exactly:

\[
\boxed{
\mathcal H_A=
\{
\texttt{always_identity},
\texttt{always_reverse},
\texttt{select_on_c}
\}
}
\]

with:

```text
always_identity(x,c) = identity(x)
always_reverse(x,c)   = reverse(x)
select_on_c(x,c)      = identity(x) when c=0; reverse(x) when c=1
```

No selector may introduce a procedure absent from the current frame.

---

## 4. Finite memory grammar

Memory is deliberately narrow so that exhaustive enumeration is possible and so that memory cannot silently contain a general selector or a new primitive.

A memory state is a partial exact-override map with at most one entry:

```text
M = {} | {(TaskInputKey, OutputSequence)}
```

where:

```text
TaskInputKey = (context_bit, values)
```

and the output sequence must have the same length as `values`.

The memory hypothesis space is therefore:

\[
\boxed{
\mathcal H_M
=
\{\varnothing\}
\cup
\{\operatorname{override}(d,y):d\in D,\ y\in Y_d\}
}
\]

where \(Y_d\) is the finite output set associated with input key \(d\).

Its exact cardinality is:

\[
|\mathcal H_M|
=
1+2\sum_{n=1}^{4}3^n3^n
=
1+2(9+81+729+6561)
=
14{,}761.
\]

One event may add or replace at most one memory entry because:

\[
\boxed{B_{update}=1.}
\]

Memory cannot:

- alter the primitive set;
- alter procedure-selection semantics;
- alter operator dispatch;
- alter \(Q_t\);
- contain more than one entry.

---

## 5. Finite frame grammar

A frame update may add at most one declared optional primitive.

The optional primitive set is:

```text
Poptional = {
    keep_even_values,
    keep_odd_values,
}
```

The complete frame-update hypothesis space is:

\[
\boxed{
\mathcal H_F=
\{F_0,
F_0\cup\{\texttt{keep\_even\_values}\},
F_0\cup\{\texttt{keep\_odd\_values}\}
\}
}
\]

Thus:

\[
|\mathcal H_F|=3.
\]

A frame update cannot alter learning-operator dispatch.

---

## 6. Procedure spaces induced by a frame

For any frame \(F\), the executable procedure space is every single primitive program drawn from that frame, including the empty/identity program only once under canonical naming.

For \(F_0\):

\[
\boxed{
\mathcal P(F_0)=
\{\texttt{identity},\texttt{reverse},\texttt{sort\_asc}\}
}
\]

For:

```text
F_even = F0 ∪ {keep_even_values}
```

\[
\mathcal P(F_{even})
=
\mathcal P(F_0)\cup\{\texttt{keep\_even\_values}\}.
\]

For:

```text
F_odd = F0 ∪ {keep_odd_values}
```

\[
\mathcal P(F_{odd})
=
\mathcal P(F_0)\cup\{\texttt{keep\_odd\_values}\}.
\]

No composition is available in v0.1. This keeps frame closure finite and makes the `k_F` certificate exhaustive by direct enumeration.

---

## 7. Contract-relative minimal-fix ordering

Minimality is relative to the frozen update grammar and budget.

The causal-depth ordering is fixed as:

\[
\boxed{
\operatorname{depth}(M)=0,
\quad
\operatorname{depth}(A)=1,
\quad
\operatorname{depth}(F)=2,
\quad
\operatorname{depth}(\mathcal L)=3.
}
\]

For a failure class \(k\), a candidate at locus \(L\) is valid iff it is contract-valid over the complete declared witness for \(k\).

Then:

\[
\boxed{
\operatorname{MinFix}_{(\mathcal G,B)}(k)
=
\arg\min_{L\in\{M,A,F,\mathcal L\}}
\operatorname{depth}(L)
}
\]

among valid candidates.

If two candidates share the same depth they are both retained in the certificate; no such tie is expected for the four preregistered witnesses.

Thus “minimal” is neither a semantic assertion nor a claim about all possible programs. It is a finite, contract-relative property.

---

## 8. Finite learning-operator domain

The event-level failure-class domain is:

\[
\boxed{K_{event}=\{k_M,k_A,k_F\}.}
\]

The episode-level recursive diagnosis is:

\[
\boxed{k_{\mathcal L}}
\]

and belongs to the operator-revision diagnosis domain but is not an ordinary single-event failure class.

The complete operator-dispatch domain is therefore:

\[
\boxed{K=\{k_M,k_A,k_F,k_{\mathcal L}\}.}
\]

For every \(k\in K\):

\[
\mathcal L(k)\in\{M,A,F,\mathcal L\}.
\]

The complete operator hypothesis space is:

\[
\boxed{|\mathcal H_{\mathcal L}|=4^4=256.}
\]

The initial operator is:

\[
\boxed{
\mathcal L_0:
\begin{cases}
k_M\mapsto M\\
k_A\mapsto M\\
k_F\mapsto M\\
k_{\mathcal L}\mapsto M
\end{cases}}
\]

The recursive revision neighborhood is restricted to at most one dispatch-entry mutation:

\[
\boxed{
\mathcal H_{\mathcal L}^{(1)}(\mathcal L)
=
\{L'\in\mathcal H_{\mathcal L}:d_H(L',\mathcal L)\le1\}
}
\]

where \(d_H\) is Hamming distance over the four dispatch entries.

Thus:

\[
|\mathcal H_{\mathcal L}^{(1)}|=1+4(4-1)=13.
\]

No operator candidate may add a new class or update primitive.

---

## 9. State bounds

The finite state contract is:

```text
R_t       : one TaskInput currently under evaluation
F_t       : one member of H_F
A_t       : one member of H_A
M_t       : zero or one exact override entries
C_t       : immutable evidence history for the current episode
Q_t       : fixed protected adjudication boundary
```

The evidence history contains at most four event records for the recursive induction episode.

No unbounded hidden carry-forward state is permitted.

No timestamp, wall-clock value, global RNG, hidden seed, or external mutable state may affect the canonical state transition.

---

## 10. Canonical representation

All canonical objects are serialized as UTF-8 JSON using exactly:

```python
json.dumps(
    value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)
```

Tuple-like values are represented as JSON arrays. Enum-like labels are represented as their fixed ASCII names. No timestamps are included in canonical identities.

The canonical digest is:

\[
\boxed{
H(v)=\operatorname{SHA256}(\operatorname{UTF8}(\operatorname{canonical\_json}(v)))
}
\]

encoded as lowercase hexadecimal.

The identity fields are:

```text
operator_id = H(canonical(operator))
frame_id    = H(canonical(frame))
procedure_id= H(canonical(procedure))
trace_id    = H(canonical(trace))
task_id     = H(canonical(task))
```

A syntactic rewrite that canonicalizes to the same value is not a state or operator change.

---

## 11. Learner-visible evidence object `e_t`

The evaluator retains latent truth:

```text
world_class
```

but the learner never receives it.

The exact learner-visible evidence object is:

```text
Evidence = {
    "event_id": str,
    "episode_index": int,
    "context_bit": 0 | 1,
    "inputs": tuple[TaskInput, ...],
    "observed_outputs": tuple[Sequence, ...],
    "expected_outputs": tuple[Sequence, ...],
    "prior_evidence": tuple[EvidenceDigest, ...],
}
```

`expected_outputs` are part of the externally evaluated task consequence, not a class label. No field named `k_M`, `k_A`, `k_F`, or `k_L` is present in the learner-facing object.

The evaluator additionally retains:

```text
world_class
required_minimal_locus
lower_level_exclusion_certificate
```

These are evaluator custody objects and are not learner inputs.

The same `Evidence` bytes are supplied to every experimental arm:

\[
\boxed{e_t^{(M)}=e_t^{(A)}=e_t^{(F)}=e_t^{(L)}}
\]

The only additional treatment permission is:

\[
\boxed{\operatorname{PermitOperatorRevision}=1}
\]

for Arm L.

---

## 12. Diagnosis

Diagnosis is deterministic and exhaustive over the finite update languages.

The learner computes:

\[
\boxed{\hat k_t=\operatorname{Diagnose}(e_t,S_t)}
\]

without receiving `world_class`.

For a single event, diagnosis evaluates the current evidence against the finite candidate spaces in depth order:

```text
M → A → F
```

and returns the first locus whose candidate set contains a contract-valid repair of the event witness.

This is a finite computation because:

\[
|\mathcal H_M|<\infty,
\qquad
|\mathcal H_A|<\infty,
\qquad
|\mathcal H_F|<\infty.
\]

For the recursive episode, after all four witness events have been observed, diagnosis additionally evaluates the fixed recurrence condition defined in Section 16. If that condition holds, the episode receives:

```text
k_L = k_𝓛
```

as an episode-level diagnosis for operator revision.

The learner logs both:

```text
k_world
k_hat
```

but only the evaluator may access `k_world` for scoring.

---

## 13. Failure class `k_M`

The `k_M` witness is a single event containing exactly one subtask:

```text
context_bit = 0
input  = [2,0,1]
output = [2,1,0]
```

The current procedure is `identity`, while the required output is individually memorisable by one exact override.

A one-entry memory hypothesis exists that passes the event contract.

The witness does not require frame expansion.

Therefore:

\[
\boxed{
\operatorname{MinFix}_{(\mathcal G,B)}(k_M)=M.
}
\]

This is a contract-relative statement over the frozen finite grammar and budget.

---

## 14. Failure class `k_A`

The `k_A` witness is one context-conditioned batch containing two subtasks:

```text
(c=0, [0,1,2]) → [0,1,2]
(c=1, [0,1,2]) → [2,1,0]
```

The frame already contains both `identity` and `reverse`.

`select_on_c` solves the entire batch.

The memory grammar has capacity for only one exact override and therefore cannot solve both subtasks within one update event.

No frame expansion is required.

Thus:

\[
\boxed{
\operatorname{MinFix}_{(\mathcal G,B)}(k_A)=A.
}
\]

The minimality certificate exhausts `H_M` and verifies that no one-entry memory candidate solves the full batch, while `select_on_c` passes.

---

## 15. Failure class `k_F`

The `k_F` witness is one batch containing two subtasks:

```text
[0,1,2,2]   → [0,2,2]
[2,0,1,1]   → [2,0]
```

The required transformation is:

```text
keep_even_values
```

Exhaustive evaluation over the initial procedure space establishes:

\[
\boxed{
\forall A\in\mathcal P(F_0),
\exists\text{ witness subtask }x:
A(x)\ne\texttt{keep\_even\_values}(x).
}
\]

The one-entry memory space is also insufficient to solve both subtasks within the one-event update budget.

Adding `keep_even_values` makes the task reachable:

\[
F_{even}=F_0\cup\{\texttt{keep\_even\_values}\}.
\]

Therefore:

\[
\boxed{
\operatorname{MinFix}_{(\mathcal G,B)}(k_F)=F.
}
\]

The frame certificate records the complete old-space closure and at least one newly reachable witness in the expanded frame.

---

## 16. Recursive witness `W_L`

The exact recurrent witness is:

\[
\boxed{
W_{\mathcal L}=(k_M,k_F,k_M,k_F).
}
\]

Exactly four events occur.

The event-level class labels are evaluator metadata used only for scoring and validation. The learner reconstructs its own `k_hat` from evidence.

The recursive diagnosis condition is:

1. both occurrences of `k_M` are correctly repairable by `M`;
2. both occurrences of `k_F` are certified as requiring `F` under the lower-level finite search;
3. `L0` routes both `k_F` occurrences to `M`;
4. the same inappropriate routing recurs after the first `k_F` consequence;
5. no lower-level update may directly alter the dispatch table.

When all five conditions hold, the episode receives:

\[
\boxed{k_{\mathcal L}}.
\]

This is a recurrence diagnosis, not a hidden class token supplied by the evaluator.

---

## 17. Lower-level exclusion certificate for the recursive witness

The decisive pre-execution certificate is an exhaustive simulation over all lower-level update histories permitted by the frozen grammar and budget.

Define:

\[
\mathcal H_{M,A,F}^{(B,W_{\mathcal L})}
\]

as every four-event execution trace generated by:

- an immutable operator `L0`;
- exactly the declared `M`, `A`, and `F` update languages;
- the one-update-per-event budget;
- the fixed witness `W_L`;
- the bounded state contract;
- no operator-dispatch mutation.

The certificate must establish the stronger behavioral exclusion:

\[
\boxed{
\forall h\in\mathcal H_{M,A,F}^{(B,W_{\mathcal L})},
\quad
h\not\models W_{\mathcal L}^{\rm future\_repair}.
}
\]

Here `models` means that the four-event trace produces contract-valid outputs for **both** `k_F` batches while preserving the required `k_M` behavior at the two `k_M` positions.

The certificate therefore asks whether any lower-level history can repair the recurrent problem without changing the operator. It does not use operator immutability itself as the reason for failure; it measures whether the remaining finite machinery can nevertheless solve the recurrent witness.

Because `L0` routes each `k_F` event to `M`, and the memory state contains at most one exact override, a lower-level trace cannot store enough independent overrides to solve both two-subtask `k_F` batches. `A` cannot introduce `keep_even_values`, and `F` cannot be selected while the immutable `L0` dispatch remains in force.

The certificate must nevertheless enumerate the full finite lower-level space and record every successful partial repair, if any.

The certificate must be generated **before** execution of the recursive treatment.

---

## 18. Operator revision rule

After `k_L` diagnosis, Arm L may enumerate:

\[
\mathcal H_{\mathcal L}^{(1)}(\mathcal L_0).
\]

The revision mechanism is deterministic:

1. identify the dispatch key whose evaluator-certified lower-level minimum repeatedly conflicts with `L0`;
2. enumerate all one-entry replacements in canonical operator order;
3. emit the first candidate satisfying the externally supplied retention test.

For the preregistered witness, the intended candidate is:

\[
\boxed{\mathcal L_1(k_F)=F}
\]

with every other `L0` dispatch entry unchanged.

Thus:

\[
\boxed{
\mathcal L_1:
\begin{cases}
k_M\mapsto M\\
k_A\mapsto M\\
k_F\mapsto F\\
k_{\mathcal L}\mapsto M
\end{cases}}
\]

The intended candidate is not authoritative merely because it was generated.

---

## 19. Operator equivalence

For a finite operator domain, two operators are equivalent iff their complete canonical transitions agree:

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

Here each operator transition record contains at least:

```text
diagnosis key
selected update locus
resulting canonical state transition
```

The complete finite domain is:

\[
\mathcal D_{op}=K\times\mathcal S_{bounded}\times\mathcal X\times\mathcal O
\]

where every component ranges over the declared finite domains in this appendix.

Operator equivalence is therefore established by exhaustive enumeration, not by source-code comparison or semantic inspection.

The primary mechanism result requires:

\[
\boxed{\mathcal L_1\not\equiv\mathcal L_0.}
\]

---

## 20. Experimental arms

All arms use exactly the same:

```text
H
Theta
B
E_eval
Evidence
chronology
future generator
correction generator
```

### Arm M

Permits `M` updates only. `A`, `F`, and `L` remain frozen.

### Arm A

Permits `M` and `A` updates. `F` and `L` remain frozen.

### Arm F

Permits `M`, `A`, and `F` updates. `L` remains frozen.

### Arm L

Permits `M`, `A`, `F`, and operator revision.

The only extra causal permission is:

```text
PermitOperatorRevision = 1
```

No arm receives richer learner-visible evidence.

---

## 21. Same-evidence invariant

For every induction event:

\[
\boxed{ e_t^{(M)}=e_t^{(A)}=e_t^{(F)}=e_t^{(L)} }
\]

as exact canonical byte sequences.

The world class is evaluator custody only:

\[
\boxed{ k_t^{world}\notin e_t }
\]

This prevents the recursive arm from receiving a diagnosis advantage.

---

## 22. Induction chronology

The exact sequence is:

```text
1. Construct frozen task world.
2. Construct frozen finite grammars and enumerators.
3. Generate the lower-level certificates.
4. Construct L0.
5. Start a fresh episode with empty mutable state.
6. Present the four-event W_L sequence.
7. Capture identical evidence for all arms.
8. Diagnose from evidence only.
9. Apply the arm-permitted single update.
10. For Arm L, after the recurrent diagnosis, generate a candidate L1.
11. Pass the candidate through independent external retention evaluation.
12. Freeze L1 and all post-induction state.
13. Only now generate H*.
14. Evaluate all arms on the identical H*.
15. Apply the independent correction challenge to the frozen recursive successor.
```

No future task, seed output, treatment result, or correction result may be available during steps 1–11.

---

## 23. Held-out future curriculum generator

The held-out seed is exactly:

```text
crank-rlo-v0.1/future/v1
```

Its UTF-8 bytes are the seed material.

For integer counter \(i=0,1,2,\ldots\), define:

```text
block_i = SHA256(seed_utf8 || b":" || decimal(i).encode("ascii"))
```

The counter stream is deterministic and domain-separated from induction and correction.

The generator emits a task only after all of the following are satisfied:

- input length is between 2 and 4;
- values are in `{0,1,2}`;
- the resulting task is not byte-identical to an induction subtask;
- at least two distinct future `k_F` subtasks are generated;
- no future task is selected using treatment output.

The future curriculum contains exactly 12 events arranged into three four-event episodes.

Episode class schedules are generated from the fixed cyclic template set:

```text
(M,F,M,F)
(F,M,F,M)
(M,F,F,M)
(F,M,M,F)
```

The SHA-256 stream selects one template per episode by the first two digest bytes modulo 4.

The task payload for each event is independently generated from subsequent digest blocks.

The future curriculum is generated only after `L1` and all post-induction state are frozen.

---

## 24. Future reach definition

For a frozen arm state and frozen future curriculum, define:

\[
\mathcal R_{future}
\]

as the set of future task IDs for which the complete task contract is satisfied at the end of the event under the declared resource and update budget.

For recursive treatment versus the same-evidence frozen shadow:

\[
\boxed{
\Delta\mathcal R^+_{\mathcal L}
=
\mathcal R_{future}(\mathcal L_1,H^*)
\setminus
\mathcal R_{future}(\mathcal L_0[H],H^*)
}
\]

and:

\[
\boxed{
\Delta\mathcal R^-_{\mathcal L}
=
\mathcal R_{future}(\mathcal L_0[H],H^*)
\setminus
\mathcal R_{future}(\mathcal L_1,H^*)
}
\]

Primary future criterion:

\[
\boxed{\Delta\mathcal R^+_{\mathcal L}\ne\varnothing.}
\]

---

## 25. Mechanism and future-benefit separation

The experiment records the following separately:

```text
operator_changed
operator_future_consequence
corrigible_after_change
```

The order of adjudication is fixed:

\[
\boxed{
\text{operator revision}
\rightarrow
\text{future consequence}
\rightarrow
\text{correction test}
}
\]

A later positive outcome cannot retroactively establish an earlier mechanism.

---

## 26. Independent correction challenge

After `L1` and the future evaluation are frozen, the recursive successor receives an independent correction episode.

The correction seed is exactly:

```text
crank-rlo-v0.1/correction/v1
```

The challenge uses the same finite evidence contract but a fresh class schedule:

```text
(k_A, k_A, k_A, k_A)
```

The external evaluator independently certifies the minimal lower-level locus for this new recurrence as `A`.

The currently retained operator routes:

```text
k_A -> M
```

so the correction episode produces a repeated externally adjudicated conflict between observed lower-level minimum and current operator routing.

The correction mechanism may propose the one-entry revision:

\[
\mathcal L_2(k_A)=A.
\]

Retention of `L2` is not required for the primary C5 claim; the primary correction criterion is whether an independently adjudicated path exists from adverse evidence to consequential operator revision:

\[
\boxed{
 e_{correction}\rightsquigarrow\Delta\mathcal L.
}
\]

Operationally:

\[
\boxed{
\operatorname{CorrReach}(\mathcal L_1,Q)>0
}
\]

iff the frozen recursive successor can be driven, by the independent correction episode and evaluator, to an operator transition `L1 -> L2` that changes at least one dispatch entry.

If this fails while operator revision and future consequence are positive, the result is classified as recursive self-modification without demonstrated corrigible recursive learning.

---

## 27. Pre-execution certificates

The following artifacts must exist before learner execution:

```text
MINFIX_KM_CERTIFICATE.json
MINFIX_KA_CERTIFICATE.json
MINFIX_KF_CERTIFICATE.json
MINFIX_KL_LOWER_EXCLUSION.json
OPERATOR_DOMAIN_MANIFEST.json
CANONICALIZATION_SPEC.json
```

The certificates record:

- exact hypothesis-space cardinality;
- canonical enumerator identity;
- task witness IDs;
- complete tested candidate hashes;
- pass/fail result for every candidate;
- winning candidate(s), if any;
- lower-level exclusion result;
- task-set hash;
- certificate hash.

No learner result may be used to generate or modify these certificates.

---

## 28. Required execution records

Every event records:

```text
event_id
arm_id
world_class                 # evaluator custody only in scoring layer
learner_hat_class
input_hash
output_hash
evidence_hash
selected_update_locus
pre_state_hash
post_state_hash
trace_id
```

Every operator state records:

```text
operator_id
canonical_dispatch
revision_parent_id
revision_reason_hash
retention_result
```

Every future evaluation records:

```text
task_id
arm_id
operator_id
state_id
success
trace_id
```

All result artifacts are immutable after commitment.

---

## 29. Interpretation taxonomy

The frozen interpretation rules are:

\[
\boxed{
\hat k\ne k^{world}
\Rightarrow
\text{decoding failure}
}
\]

\[
\boxed{
\hat k=k^{world},\quad
\mathcal L(\hat k)\ne L^*
\Rightarrow
\text{selection failure}
}
\]

\[
\boxed{
\mathcal L(\hat k)=L^*,\quad
S'\text{ fails}
\Rightarrow
\text{execution failure}
}
\]

\[
\boxed{
S'\text{ succeeds},\quad
\mathcal L'\equiv\mathcal L
\Rightarrow
\text{non-recursive adaptation}
}
\]

\[
\boxed{
\mathcal L'\not\equiv\mathcal L
\Rightarrow
\text{operator revision}
}
\]

\[
\boxed{
\mathcal L'\not\equiv\mathcal L,
\quad
\Delta\mathcal R^+\ne\varnothing
\Rightarrow
\text{recursive consequence}
}
\]

\[
\boxed{
\text{previous conditions}
\land
\operatorname{CorrReach}>0
\Rightarrow
\text{corrigible recursive learning}
}
\]

A null result terminates at the earliest unsupported transition and is not collapsed into “learning failed.”

---

## 30. Primary claim ladder

### C0 — state adaptation

\[
S_1\ne S_0.
\]

### C1 — procedure adaptation

\[
A_1\ne A_0.
\]

### C2 — frame/construction adaptation

\[
\mathcal H(F_1)\ne\mathcal H(F_0).
\]

### C3 — learning-operator modification

\[
\boxed{\mathcal L_1\not\equiv\mathcal L_0.}
\]

### C4 — recursive consequence

\[
\boxed{\Delta\mathcal R^+_{\mathcal L}\ne\varnothing.}
\]

### C5 — corrigible recursive learning

\[
\boxed{
C3\land C4\land\operatorname{CorrReach}(\mathcal L_1,Q)>0.
}
\]

---

## 31. Explicit non-claims

This assay does not establish:

```text
general intelligence
open-endedness
unrestricted self-improvement
general-purpose meta-learning
general-purpose transfer
intrinsic capability increase
```

A positive result establishes only the bounded causal transition actually demonstrated by the frozen contract and certificates.

---

## 32. Frozen seeds and generators

The only string seeds permitted by v0.1 are:

```text
crank-rlo-v0.1/induction/v1
crank-rlo-v0.1/future/v1
crank-rlo-v0.1/correction/v1
```

Induction witness instances are fixed directly by this appendix.

Future and correction task payloads are generated only by the SHA-256 counter-stream rule in this document.

No ambient random source is permitted.

---

## 33. Isolation boundary

This appendix introduces no changes to:

```text
CRANK-IL
CRANK-DEL
corrigible_buffer.py
AuthorityAdapter
MinimalMechanism
revisable_adaptive_mechanism.py
Layer-0 trial contract
```

The recursive assay is an isolated experimental branch.

Its implementation may depend on shared canonicalization or utility conventions only where those dependencies are explicitly imported and version-pinned. No existing experiment may be rewritten to accommodate the recursive assay.

---

## 34. Execution boundary

The implementation phase begins only after this appendix is committed unchanged and the pre-execution certificates have been generated from the exact frozen definitions above.

The intended execution sequence is:

```text
freeze appendix
    ↓
enumerate spaces
    ↓
certify MinFix(M/A/F/L)
    ↓
execute controls + recursive arm
    ↓
externally retain/reject candidate operator
    ↓
freeze post-induction state
    ↓
generate H*
    ↓
evaluate future reach
    ↓
apply correction challenge
    ↓
interpret at the first failed causal boundary
```

The next scientifically interesting object after this appendix is therefore an execution log, not an additional conceptual layer.
