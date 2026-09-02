# Layer-0 four-cell dataset scaffold

This directory is the execution-data boundary for the frozen Layer-0 phenomenon assay.

No model output is included yet. The repository intentionally contains only the immutable dataset schema and an execution manifest until the experiment is actually run.

Required custody fields per trial:

- `trial_id`
- `context_id`
- `intervention_id`
- `task_id`
- `raw_model_output`
- `parsed_implementation`
- `contract_result`
- `model_identifier` (metadata)
- `execution_timestamp` (metadata)

The four preregistered cells are:

```text
(C0,e0)  (C0,e1)
(C1,e0)  (C1,e1)
```

Do not add model-produced validity declarations to the analytical fields. Parsing and contract evaluation are post-hoc and exogenous.

The dataset should be committed only after actual execution. A later results commit should contain the frozen raw observations and preregistered analysis output unchanged.