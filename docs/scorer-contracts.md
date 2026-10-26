# Scoring Interfaces and Contracts

This document describes scoring and validation for the three public
self-test topics. Final competition evaluation uses other topics and their
corresponding scoring contracts.

`scoring/` contains the TDC and PsyDefDetect scoring implementations, artifact
validators, data preparation scripts, and adapters for the external ARC
toolkit. The ARC toolkit itself is not included in this repository.

## Installation

TDC and PsyDefDetect scoring and artifact validation use the Python standard
library. ARC tools also require `whestbench`, `datasets`, and `pyarrow` from
`scoring/requirements.txt`. Install ARC dependencies in a dedicated environment:

```bash
uv venv
uv pip install -r scoring/requirements.txt
```

Release bundles should pin the ARC toolkit versions used for evaluation.
The dependency file currently lists packages without version pins.

## Command-line interfaces

Python entry points use `argparse`. Successful commands exit 0; validation
or scoring failures generally exit 1, and argument errors exit 2. Output
formats differ by entry point as specified below.

| Entry point | Arguments | Success | Failure |
|---|---|---|---|
| `validate_tdc_admet_tox_run.py` | `--run-root` `--stage` [`--public-dataset-root`] | Audit JSON on stdout, exit 0 | `{"status":"failed","error":…}` JSON on stdout, exit 1 |
| `run_tdc_admet_tox_validation_score.py` | `--validation` `--predictions` `--output-metrics` | Metrics JSON on stdout and in the output file, exit 0 | Plain-text error, exit 1 |
| `run_tdc_admet_tox_host_score.py` | `--public-dataset-root` `--hidden-labels` `--predictions` `--output-score` | Score JSON in the output file; no success JSON on stdout, exit 0 | Plain-text error, exit 1 |
| `scripts/check-release.sh` | `--path DIR` | `check-release.sh: PASS` on stdout, exit 0 | `FINDING: …` on stderr, exit 1; usage errors also exit 1 |
| `scripts/check_native_marker.sh` | `<log-or-run-root>` `[MARKER]` | `PASS:` on stdout, exit 0 | `FAIL:` on stderr, exit 1 |
| `scripts/validate_schemas.py` | `--manifest FILE`, `--provenance FILE`, `--trace FILE`, `--environment FILE`, or `--all-repo` | `{"status":"passed",…}` JSON, exit 0 | `{"status":"failed","errors":…}` JSON, exit 1 |
| `scripts/selfcheck_tdc.sh` | None | `[selfcheck] TDC-ADMET-Tox selfcheck: PASS`, exit 0 | Stops at the first failed step with a nonzero exit status |

The validation scorer's `--output-metrics` writes validation metrics. The
host scorer's `--output-score` writes the official score. Both files are
JSON, but their purposes and payloads differ. Shell entry points use text
output; callers should check their exit status.

## TDC-ADMET-Tox: `macro_average_auroc`

The main score is the equal-weight mean AUROC for AMES, hERG, and DILI.
AUPRC, calibration, runtime, and reproducibility are secondary diagnostics
and do not enter the main score.

| Script | Role |
|---|---|
| `run_tdc_admet_tox_host_score.py` | Organizer-side scorer using hidden test labels (`TDC_ADMET_TOX_HIDDEN_LABELS_ROOT`). Labels are not mounted into framework containers. Writes `score.json` after the framework exits. |
| `validate_tdc_admet_tox_run.py` | Artifact validation at `--stage framework` before scoring and `--stage final` after scoring. Rejects other-topic markers and hidden-label references in framework artifacts. |
| `run_tdc_admet_tox_reference_baseline.py` | Builds and scores a reference baseline with a `reproduce.py` entry point. |
| `export_tdc_admet_tox_official_splits.py` | Exports the fixed endpoint splits from the source archive. |
| `prepare_tdc_admet_tox_from_archive.py` | Creates `public/{train,validation,test}.csv` from `admet_group.zip`, as used by `scripts/setup_datasets.sh`. |
| `scripts/selfcheck_tdc.sh` | Validates the golden run and, when `TDC_ADMET_TOX_DATASET_ROOT` is set, runs and validates the reference baseline. |

Data originates from Harvard Dataverse `doi:10.7910/DVN/21LKWG` under its
applicable terms. Download checksums are listed in `docs/rules.md` §3.2.

## PsyDefDetect: macro-F1 over positive classes 1–8

The official macro-F1 excludes class `0` (No Defense).

| Script | Role |
|---|---|
| `run_psydefdetect_local_score.py` | Local self-evaluation on the standardized split. Uses `PSYDEFDETECT_DATASET_ROOT` and the fixed canonical split; checksum in `docs/rules.md` §3.3. |

PsyDefConv uses `cc-by-nc-4.0`. The competition is non-commercial, and data
use must comply with that license.

## ARC-WBE-2026: `adjusted_final_layer_score`

Lower scores are better. The metric compares estimated and true activations.
Frameworks receive a visible validation set of 10 MLPs with ground truth;
the disjoint 90-MLP scoring set is evaluated by the organizer.

| Script | Role |
|---|---|
| `run_arc_wbe_2026_local_score.py` | Local evaluation on the visible validation set. |
| `arc_wbe_2026_official_adapter.py` | Checks the estimator load contract and renders an adapter for the official scorer. `predict(mlp)` returns `(32,256)` predictions. Missing, malformed, non-finite, wrong-shape, constant, scalar, and placeholder outputs are rejected. Optional two-digit `framework_hint` selects estimator-shape routing. |
| `bake_arc_wbe_2026_dataset_with_whestbench.py` | Prepares the dataset format used by the official toolkit. |
| `prepare_arc_wbe_2026_dataset.py` | Downloads and prepares ARC data for `setup_datasets.sh`. |
| `make_arc_wbe_2026_visible_validation.py` | Creates disjoint 10-MLP validation and 90-MLP scoring sets and writes `split_manifest.json` with per-set checksums. |

Install the official `whestbench` toolkit and data using the
[ARC dataset documentation](https://huggingface.co/datasets/aicrowd/arc-whestbench-public-2026).
The external toolkit's license applies separately.

## Shared requirements

- Formal score files are produced by the organizer-side scorer. Frameworks
  must not create or modify the official `score.json`. Local self-evaluation
  outputs are separate from formal score records.
- Dataset and split checksums must match the published values.
- Framework containers must not receive hidden labels. The repository root
  must not serve as a writable framework workspace.
