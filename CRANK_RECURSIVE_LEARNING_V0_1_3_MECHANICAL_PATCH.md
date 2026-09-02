# CRANK — Recursive Learning-Operator Revision
## v0.1.3 Mechanical Patch

**Supersedes only conflicting mechanical details in v0.1.2. Scientific design is unchanged.**

### 1. Frame transaction is authoritative

For a frame update on `k_F`, the update transaction is exactly:

```text
pre:  F_t
post: F_t ∪ {keep_even_values}
exec: keep_even_values(current_kF_batch)
```

The constructed procedure is an execution artifact of the frame transaction. `A_t` is unchanged and no `ΔA` credit is recorded.

### 2. Witness-relative memory state quotient

For the lower-level recursive certificate, memory states are quotiented by their observable behavior on the finite witness input keys:

```text
q(M) = M restricted to the distinct TaskInput keys occurring in W_L,
       with all non-witness keys mapped to one canonical ⊥ state.
```

Two memory states are equivalent iff they produce identical outputs for every witness subtask under the current procedure semantics.

This quotient is exact for `W_L` because no witness execution can inspect a memory entry whose key does not occur in the witness.

The witness contains three distinct input keys:

```text
m0 = (0, [2,0,1])
f0 = (0, [0,1,2,2])
f1 = (0, [2,0,1,1])
```

The quotient state space is therefore finite:

```text
empty
27 possible overrides on m0
81 possible overrides on f0
81 possible overrides on f1
```

for a total of:

\[
|Q_M|=1+27+81+81=190.
\]

The lower-level certificate must exhaustively enumerate the quotient transition graph over exactly four witness events, not enumerate behaviorally duplicate full-memory traces.

This is an exact finite-state reduction, not a heuristic pruning rule.

### 3. Lower-level recursive exclusion

With `L0` frozen:

```text
L0(k_M) = M
L0(k_F) = M
```

and `W_L=(k_M,k_F,k_M,k_F)`, every lower-level event routes to memory.

At most one quotient-memory entry can be changed per event.

The certificate checks every reachable quotient-memory state at every event index and records whether the complete prefix and complete four-event witness are contract-valid.

The required result remains:

\[
\boxed{
\forall q\in Q_M^{(B,W_L)},
\quad
q\not\models W_L^{future\_repair}.
}
\]

The quotient is complete for the witness, so passing this certificate is equivalent to exhausting the full lower-level memory behavior relevant to `W_L`.

### 4. Pre-execution gate

Learner execution remains forbidden until:

```text
MinFix(k_M) = M
MinFix(k_A) = A
MinFix(k_F) = F
lower-level recursive exclusion = PASS
```
