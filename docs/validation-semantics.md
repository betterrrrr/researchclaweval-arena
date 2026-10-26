# TDC-ADMET-Tox Validation Semantics

`scoring/validate_tdc_admet_tox_run.py` implements the checks described here.
If the document differs from the validator, use the implementation and report
the discrepancy. A complete example is provided in
`templates/submission/golden_tdc_admet_tox/`.

## 1. Trace metrics and metric files

Each experiment in `experiment_trace.json` contains `validation_metrics`
and a reference to `metrics_file`. `metric_values_match` requires exact
numeric equality between corresponding `macro_average_auroc` and
`per_endpoint` fields. This is numeric equality, not a byte comparison of
serialized JSON, and no tolerance is applied.

Generate both records from the same scorer output or copy the metric
values without rounding. Re-serializing the same values as JSON is valid;
recomputing at different precision may change the values and fail validation.

Metric files must describe the validation split and must not contain test
or hidden-test metrics. `validation_metrics` must include AUROC values for
all three endpoints: AMES, hERG, and DILI.

## 2. Claim values and source records

Each entry in `trace.claims` must reference a complete source experiment,
including its ID and the same `prediction_file`, `config_file`, and
`log_file` paths. Its `value` must match the named source metric under
`isclose(rel_tol=0.0, abs_tol=1e-12)`.

Supported names include `auroc`, `auprc`, `average_precision`, `brier`,
`brier_score`, `ece`, `ece_10_bin`, and `runtime_seconds`; aliases are defined
in the validator. Runtime claims are compared with the experiment's declared
runtime. The tolerance is an absolute difference of 1e-12, not a rule for
rounding claim values to twelve decimal places.

## 3. Official score and experiment selection

The validator also checks:

- `score.json` `main_score` equals the mean of the file's per-endpoint AUROC
  values, with absolute tolerance 1e-12.
- `selected_experiment_id` identifies an experiment with the maximum
  validation `macro_average_auroc`. A difference within 1e-12 is accepted
  as a tie.

## 4. Quantitative statements in the paper

`paper.md`, or `paper.pdf` with `paper_claims.md`, must reference every trace
claim and must not refer to unknown claim IDs. Each displayed number in a
table cell or quantitative prose line requires an `<!-- claim:... -->`
marker in that cell or line. The marker's claim value must support the
number. Quantitative prose is detected using empirical terms such as AUROC,
AUPRC, score, runtime, and improvement.

The displayed number is compared at its display resolution:

```text
tolerance = 0.5 * 10^(-displayed decimals)        # "0.752" → ±0.0005
percentages divide tolerance (and the value) by 100
```

For example, `0.752` matches source values `0.7520` and `0.7521`, but not
`0.7526`. `75.20%` matches `0.7520`. Rounding is permitted for display; trace
claims retain the source metric values.

## 5. Reference submission

`templates/submission/golden_tdc_admet_tox/` contains two experiments,
three claims, a marked paper, and environment and reproduction records.
Validate it with:

```bash
python3 scoring/validate_tdc_admet_tox_run.py \
  --run-root templates/submission/golden_tdc_admet_tox \
  --stage framework
```

`tests/test_validate_golden.py` checks that the reference submission remains
accepted by the validator.
