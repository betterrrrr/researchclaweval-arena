# Validation Semantics (TDC-ADMET-Tox)

> The audit (`scoring/validate_tdc_admet_tox_run.py`) is the authoritative
> implementation of these semantics. If this document and the audit ever
> disagree, the audit wins and this document is a bug — report it.

This page exists because the audit is deliberately strict, and the strictness
is easy to discover only by reading its source. Worked examples live in
`templates/submission/golden_tdc_admet_tox/`.

## 1. Metrics must be copied, not recomputed

`experiment_trace.json` carries `validation_metrics` per experiment, and each
experiment also points at its `metrics_file`. The audit requires the two to
match **bit for bit** (`metric_values_match`): every numeric field the trace
declares for `macro_average_auroc` and for each endpoint's `per_endpoint`
row must be **exactly equal** to the same field in the metrics file — not
equal within a tolerance.

Consequences:

- Write both from the same source of truth (e.g. the scorer output), or copy
  the numbers verbatim.
- Do not round a metric in the trace ("0.75232" → "0.752"); do not recompute
  it in another precision. JSON round-tripping of the same float is fine;
  a different computation is not.
- The metrics file must be on the **validation** split and must not contain
  any test/hidden-test metric (any key or value that reads like a test
  split), and `validation_metrics` must provide per-endpoint AUROC for all
  three endpoints (AMES / hERG / DILI).

## 2. Claims: values tie to source metrics at 1e-12

Every claim in `trace.claims` must reference a complete source experiment
(id + the exact same `prediction_file` / `config_file` / `log_file` paths),
and its `value` must equal the metric it names (**= auroc | auprc |
average_precision | brier | brier_score | ece | ece_10_bin | runtime_seconds**,
with the alias table in the audit) from that experiment's metrics file,
compared with `isclose(rel_tol=0.0, abs_tol=1e-12)`.

Practical reading: a claim value is the **same number** as the metrics file
field, to twelve decimal places. `runtime_seconds` claims compare against the
experiment's declared runtime. Copy values; don't recompute or reformat.

## 3. Score checks at 1e-12

Two more exact comparisons (both offset only by the audit's strictness):

- `score.json` `main_score` must equal the mean of the per-endpoint AUROC
  values in the same file, to 1e-12.
- `selected_experiment_id` must be the experiment with the maximum
  validation `macro_average_auroc` (a tie within 1e-12 is a pass).

## 4. Paper numbers: every displayed number carries a claim marker

The paper (`paper.md`, or `paper.pdf` + `paper_claims.md`) must reference
**every** trace claim, must not reference unknown claim ids, and every
*displayed* number in a table cell or in quantitative prose (prose containing
an empirical term such as auroc / auprc / score / runtime / improvement)
must sit in the same cell/line as an `<!-- claim:... -->` marker whose claim
value matches it.

The match is not at 1e-12 — it honors the number's own display resolution:

```
tolerance = 0.5 * 10^(-displayed decimals)        # "0.752" → ±0.0005
percentages divide tolerance (and the value) by 100
```

So "0.752" matches a claim of 0.7520 but not 0.7521; "75.20%" matches 0.7520.
You may round *for display* — the marker's claim value is the exact one.

## 5. Golden run

`templates/submission/golden_tdc_admet_tox/` is a complete legal handoff
(2 experiments, 3 claims, marked paper, full environment/reproduction
records) that the audit must accept:

```bash
python3 scoring/validate_tdc_admet_tox_run.py \
  --run-root templates/submission/golden_tdc_admet_tox \
  --stage framework
```

It is also the regression fixture: the audit keeps passing on it after every
change (`tests/test_validate_golden.py`).