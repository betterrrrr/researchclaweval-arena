# Scorer Contracts

How the official scores for the three topics are computed and what the
scripts in `scoring/` do. All scripts are glue around the official scorers —
the scoring code is not vendored here; install the official packages as
described below, and run the glue.

## TDC-ADMET-Tox — `macro_average_auroc`

Three endpoints (AMES / hERG / DILI); the main score is the unweighted mean
of the three endpoint AUROCs. AUPRC, calibration, runtime, reproducibility
are secondary diagnostics and never enter the score.

| script | role |
|---|---|
| `run_tdc_admet_tox_host_score.py` | **host-side official scorer.** Needs the hidden test labels (`TDC_ADMET_TOX_HIDDEN_LABELS_ROOT`); never mounted into framework containers. Writes `score.json` after the framework exits. |
| `validate_tdc_admet_tox_run.py` | artifact validator, `--stage framework` (before scoring) and `--stage final` (after). Rejects, among other things, framework outputs carrying other-topic markers or hidden-label references. |
| `run_tdc_admet_tox_reference_baseline.py` | builds and scores a reference baseline run (`reproduce.py` reproduces it) — the reference implementation teams can start from. |
| `export_tdc_admet_tox_official_splits.py` | (re)exports the frozen endpoint splits from the archive. |
| `prepare_tdc_admet_tox_from_archive.py` | materializes `public/{train,validation,test}.csv` from `admet_group.zip`; used by `scripts/setup_datasets.sh`. |

**Dataset licensing:** TDC-ADMET-Tox data comes from Harvard Dataverse
(`doi:10.7910/DVN/21LKWG`), used under Dataverse terms; see
`docs/rules.md` §3.1 for the sha256 you must match after downloading.

## PsyDefDetect — macro-F1 over positive classes 1–8

Class `0` (No Defense) is excluded from the official macro-F1.

| script | role |
|---|---|
| `run_psydefdetect_local_score.py` | the local scorer on the standardized split; framework can run it for self-evaluation. Reads `PSYDEFDETECT_DATASET_ROOT` and the frozen canonical split (split sha256 published in `docs/rules.md` §3.3). |

**Data licensing:** `PsyDefConv` is `cc-by-nc-4.0`; the competition is
**non-commercial** — verify your own use complies before downloading.

## ARC-WBE-2026 — `adjusted_final_layer_score` (lower is better)

ARC differs from the other two topics: the official metric compares against
true activations, which are host-only. Frameworks receive a **visible
validation set** (10 MLPs with ground truth, disjoint from the 90-MLP scoring
set) for self-evaluation; the host scores the rest.

| script | role |
|---|---|
| `run_arc_wbe_2026_local_score.py` | local scorer over the visible validation set (framework-side self-evaluation). |
| `arc_wbe_2026_official_adapter.py` | scans the framework's `estimator.py`, verifies it satisfies the load contract (`predict(mlp)` returning `(32,256)`; no constants, scalars, or placeholder logic), and renders the official adapter the host feeds to the official scorer. It fails closed on missing/malformed/non-finite/shape-mismatched predictions. Accepts a `framework_hint` — a two-digit framework id — for estimator-shape routing. |
| `bake_arc_wbe_2026_dataset_with_whestbench.py` | bakes the dataset format required by the official scorer (whest). |
| `prepare_arc_wbe_2026_dataset.py` | downloads + prepares the dataset (called by `setup_datasets.sh`). |
| `make_arc_wbe_2026_visible_validation.py` | splits the dataset into visible-validation (10 MLPs) and scoring (90 MLPs) sets, writing `split_manifest.json` with per-set sha256. |

**Official scorer installation:** the official ARC estimator benchmark is
`whestbench` (ARC White-Box Estimation toolkit); install the official package
and dataset per its own documentation (`https://huggingface.co/datasets/aicrowd/arc-whestbench-public-2026`).
We provide glue, not the vendored toolkit; verify the toolkit's license on
its own page.

## Common invariants

- Only `score.json` written by the host-side scorer counts. A framework must
  never create, backfill, or edit `score.json`.
- `dataset_sha256` / `split_sha256` mismatches are rejected without scoring.
- Framework containers never see hidden labels, and the repository root is
  never mounted as a writable framework workspace.