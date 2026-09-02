# CRANK-IL: isolated procedure induction layer

This package is an additive experimental layer. Existing CRANK buffer,
adapter, temporal, Layer-0, and environment artifacts are not modified here.

## Causal boundary

```text
same H, Theta, B, T*, E_eval
        |
        +--> frozen A0[H]  (shadow)
        |
        +--> Induce(A0, H) -> candidate A1
                         |
                         v
                 prospective Test
                  /      |      \
               reject  reopen  retain
                         |
                         v
                       Reach
```

The package distinguishes:

```text
Frame != hypothesis space != procedure != execution trace != reach certificate
```

`FrameSpec` declares the primitive vocabulary and depth bound. `HypothesisSpace`
enforces frame membership and provides deterministic finite enumeration.
`Procedure` defines executable semantics and a canonical procedure identity.
`ExecutionTrace` records execution and has a separate trace identity.
`ProcedureTest` binds results and reach certificates to a frozen execution
contract.

## Initial weak DSL

The first implementation uses only sequence transformations:

`identity`, `reverse`, `sort_asc`, `sort_desc`, `keep_even`, `keep_odd`,
`drop_first`, `drop_last`.

A frame selects a subset of these primitives and a maximum program length.
No callables, dynamic code generation, or hidden operators are admitted.

## Claim ceiling

The implementation establishes only machinery for an induction experiment.
It does not establish that algorithmic learning, structural transfer,
constructive Reach expansion, or intrinsic capability has occurred.

Those claims require prospective evaluation under an identical
same-evidence shadow and a fixed execution contract.
