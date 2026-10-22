# Golden TDC-ADMET-Tox Run

A **frozen, complete, legal** TDC-ADMET-Tox handoff (framework stage, no
`score.json`), used as the canonical worked example and the regression
fixture for the official audit.

## Layout

This directory is the **run root** — the same shape the runner produces
(`docs/rules.md` §5.2):

```
golden_tdc_admet_tox/
├── PROVENANCE.json           # self-reported submission ledger (per template)
├── logs/e2e.log              # raw stdout/stderr of the run (run root, NOT inside workspace)
└── workspace/                # the `WORKSPACE` the runner injects
    ├── predictions.csv       # root-level topic payload
    ├── experiment_trace.json # trace: experiments, claims, resource_budget, reproduction
    ├── environment.json      # 6 required fields (validator `validate_environment`)
    ├── research_idea.json
    ├── final_report.md
    ├── paper.md              # every displayed number carries a claim marker
    ├── reproduce.sh          # reproduction entrypoint referenced by the trace
    └── experiment_001/…002/  # config / predictions / metrics / train log per experiment
```

## How to use it

Audit it — it must pass, and staying passing is a CI regression:

```bash
python3 scoring/validate_tdc_admet_tox_run.py \
  --run-root templates/submission/golden_tdc_admet_tox \
  --stage framework
```

Study it — every requirement the audit enforces is demonstrated here:
trace field-for-field, the byte-equal `resource_budget` dict (values come
from `scoring/resource_budget.anchors.json`), metrics-file ↔ trace metric
exact equality, claim values at 1e-12, and claim markers on every displayed
paper number.

## Where it comes from

The canonical baseline (`scoring/run_tdc_admet_tox_reference_baseline.py`)
produces a run with this same shape against the real dataset; this frozen
copy substitutes fixed placeholder data so the example needs no downloads
and no learned dependencies. Treat it as the shape contract: if the
validator is changed, this tree is the first thing that must still pass.

`model`, `dataset_sha256`/`split_sha256`/`prompt_sha256`/`contract_sha256`,
and the run id are fill-in values — replace them with your own run's values
before submitting (see the PROVENANCE template).