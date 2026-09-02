# CRANK — Recursive Learning-Operator Revision
## v0.1.2 Mechanical Patch

**Supersedes only the conflicting mechanical definitions in `CRANK_RECURSIVE_LEARNING_V0_1.1_APPENDIX.md`. The scientific design is unchanged.**

### 1. Evidence boundary

The learner-visible evidence object contains:

```text
(event_id, episode_index, context_bit,
 input_batch, observed_output_batch,
 consequence, prior_evidence)
```

It does **not** contain `expected_outputs`, `world_class`, `required_minimal_locus`, or any failure-class token.

Evaluator custody may retain those values for scoring and certification.

The consequence record is the finite observation:

```text
(success,
 lengths_preserved,
 value_membership_valid,
 order_relation,
 context_consistency)
```

These fields describe the observed consequence and contain no target output.

### 2. Frame-only construction/execution transaction

A frame update is a single atomic update transaction. It may add one optional primitive and, in the same transaction, construct and execute the corresponding one-primitive procedure for the current witness.

For `k_F`:

```text
F0 = {identity, reverse, sort_asc}
F1 = F0 ∪ {keep_even_values}
```

The transaction then constructs:

```text
P_even = keep_even_values
```

and executes `P_even` immediately against the current `k_F` witness.

This constructed procedure is a **derived execution artifact of the frame update**, not an independent `A` update.

Therefore the transaction has:

```text
ΔF = 1
ΔA = 0
```

for causal credit purposes.

The pre-update selector `A_t` is not mutated by this transaction. No subsequent selector search is required to execute the newly constructed procedure.

This is the formal meaning of:

\[
\boxed{\Delta F\Rightarrow\text{new constructible procedure and same-event execution}}
\]

without implying:

\[
\Delta F+\Delta A.
\]

### 3. Contract-relative `k_F` certificate

The `k_F` witness remains:

```text
[0,1,2,2] → [0,2,2]
[2,0,1,1] → [2,0]
```

The required transformation is `keep_even_values`.

The complete pre-update procedure space is:

```text
H(F0) = {identity, reverse, sort_asc}
```

and the complete post-update construction space relevant to this witness is:

```text
H(F1) = {identity, reverse, sort_asc, keep_even_values}
```

The certificate checks:

```text
∀ P ∈ H(F0), P does not solve both k_F subtasks
```

and:

```text
keep_even_values solves both k_F subtasks.
```

Memory is also exhaustively checked and cannot solve both subtasks with one entry.

Therefore:

\[
\boxed{\operatorname{MinFix}_{(G,B)}(k_F)=F.}
\]

### 4. Recursive lower-level exclusion

The exact witness is:

\[
\boxed{W_L=(k_M,k_F,k_M,k_F).}
\]

`L0` routes both event classes to `M`:

```text
L0(k_M) = M
L0(k_F) = M
```

Therefore, under frozen `L0`, the lower-level arm can select only memory updates on this witness.

The memory state contains at most one exact override and each `k_F` event contains two subtasks. A complete witness requires both subtasks of each `k_F` event to succeed and both `k_M` events to succeed.

The exhaustive search enumerates every four-event memory trace under:

```text
empty memory at t0
one-entry state bound
one memory update per event
replacement permitted
```

No such trace can simultaneously preserve both `k_M` events and solve both two-subtask `k_F` events.

Thus the required exclusion is:

\[
\boxed{
\forall h\in H_{M,A,F}^{(B,W_L)},
\quad h\not\models W_L^{future\_repair}.
}
\]

### 5. Operator-revision semantics

The recursive candidate remains the one-entry mutation:

\[
\boxed{
L1(k_M)=M,
\quad L1(k_A)=M,
\quad L1(k_F)=F,
\quad L1(k_L)=M.
}
\]

Operator revision remains distinct from ordinary state update.

### 6. Pre-execution gate

The learner may not execute until all four certificates have passed:

```text
MINFIX_KM_CERTIFICATE
MINFIX_KA_CERTIFICATE
MINFIX_KF_CERTIFICATE
MINFIX_KL_LOWER_EXCLUSION
```

A certificate failure is a hard stop and requires another mechanical specification revision.
