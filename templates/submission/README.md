# Submission templates

Per topic, one artifact set named
`<framework>-<topic>-<YYYYMMDDTHHMMSS>/`:

```
PROVENANCE.json       # edit from PROVENANCE.json.template
workspace/
  research_idea.json    # written and locked BEFORE the first experiment
  experiment_trace.json # every experiment and its results
  environment.json      # run env — six required fields (see template)
  final_report.md       # framework-authored
  <topic payload>       # predictions.csv | predictions.jsonl | estimator.py
logs/
  e2e.log               # raw stdout/stderr of the run (required)
prompt.txt              # the exact task input the runner mounted (input/prompt.txt)
source/                 # optional: research code the framework generated
```

A complete worked example (audit-passing) lives in
`golden_tdc_admet_tox/`; `environment.json.template` mirrors its
environment record.

Validation rules (rules §5, §8, contracts/):

- `dataset_sha256` and `split_sha256` must match the published values
  byte-for-byte; a mismatch is rejected without scoring.
- `logs/e2e.log` is the primary record. The judge reads
  `logs/e2e.log` → `logs/native.log` → `logs/native_stdout.log`; a
  root-level `run.log` is not consulted.
- The root-level `score.json` is written only by the host-side official
  scorer after the framework exits (e.g. `scoring/run_tdc_admet_tox_host_score.py`).
  Never create or modify it yourself.
- ARC payload: `estimator.py` exposing `predict(self, mlp)` returning a real
  `(32, 256)` array (see `contracts/arc_wbe_2026_contract.md` and
  `scoring/arc_wbe_2026_official_adapter.py` for the fail-closed checks).