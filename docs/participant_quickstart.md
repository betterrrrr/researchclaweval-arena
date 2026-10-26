# Participant Quickstart

[中文](participant_quickstart.zh-CN.md). This guide covers framework integration
and self-testing. `docs/rules.md` defines competition rules; `contracts/*.md`
defines task-specific requirements.

The three public topics are for development and self-testing. Official
evaluation uses other topics, run and scored by the organizer. Self-test
scores do not count toward final rankings.

## 0. Workflow

1. Register and obtain a two-digit framework ID.
2. Download the three self-test datasets and verify SHA-256.
3. Read the task contracts.
4. Configure an adapter declaring the framework launch procedure.
5. Complete self-testing with the official runner template.
6. Submit the open-source framework repository and run artifacts for official
   evaluation as specified by the rules.

The framework owns research planning, experiment design, execution,
comparison, selection, and report preparation. The adapter handles
integration and launch without prescribing research methods.

## 1. Datasets

```bash
bash scripts/setup_datasets.sh --dataset tdc_admet_tox   # ~1.4 MB
bash scripts/setup_datasets.sh --dataset psydefdetect    # ~5.4 MB
bash scripts/setup_datasets.sh --dataset arc_wbe_2026    # ~907 MB
```

The script downloads from the original sources and checks the frozen
SHA-256 values. Configure dataset paths after download:

```bash
export TDC_ADMET_TOX_DATASET_ROOT=$PWD/data/tdc_admet_tox/public
export PSYDEFDETECT_DATASET_ROOT=$PWD/data/psydefdetect
export ARC_WBE_2026_DATASET_ROOT=$PWD/data/arc_white_box_estimation_2026
```

If direct access to `huggingface.co` fails, set
`HF_ENDPOINT=https://hf-mirror.com`. Mirror fallback is used only after
direct access fails.

PsyDefDetect uses `cc-by-nc-4.0`. The competition is non-commercial, and data
use must comply with that license.

## 2. Task contracts

The three self-test contracts specify data visibility, metrics, experiment
budgets, and required outputs:

- `contracts/arc_wbe_2026_contract.md`: 10 of 100 MLPs form the visible
  validation set and include ground truth. The remaining 90 are scored by
  the organizer and are not mounted into framework containers. See rules §3.4.
- `contracts/psydefdetect_contract.md`: macro-F1 over positive classes 1–8,
  using the dialogue-level split in `psydefdetect_split.canonical.json`.
  The checksum is in rules §3.3. Local self-evaluation:

  ```bash
  python3 scoring/run_psydefdetect_local_score.py \
    --dataset-root "$PSYDEFDETECT_DATASET_ROOT" \
    --predictions predictions.jsonl \
    --output-score score.json
  ```

- `contracts/tdc_admet_tox_contract.md`: equal-weight mean AUROC for AMES,
  hERG, and DILI. Use sample IDs from the data files; `hERG` uses the `HERG_`
  prefix (rules §5.6). `bash scripts/selfcheck_tdc.sh` validates the golden
  run and, when `TDC_ADMET_TOX_DATASET_ROOT` is set, evaluates and validates
  the reference baseline.

Local self-evaluation files are for debugging and are not submitted as
official scores. Shared requirements:

- Write and lock `research_idea.json` before the first experiment.
- Complete 2–4 materially different strategy lines. Retries, seed-only
  repeats, and minor tuning within a line do not add a line. A line requires
  at least one complete experiment. Compare results and submit the selected
  result without starting a fifth line. See rules §5.8.
- Record every experiment in `experiment_trace.json`.

## 3. Adapter and runner

Copy the adapter example:

```bash
cp -r templates/example-adapter/ myframework/
```

`manifest.json` declares the framework ID, name, upstream repository,
license, native entrypoint, required environment variables, images, and
patches. Replace placeholders and validate against `schemas/adapter.schema.json`
with `python3 scripts/validate_schemas.py --manifest myframework/manifest.json`.

The fullrun wrapper must follow `scripts/runner/` templates. The runner
mounts contracts and data read-only, supplies `OPENAI_BASE_URL`,
`OPENAI_API_KEY`, and `OPENAI_MODEL`, exports `WORKSPACE` and `DATASET_ROOT`,
composes `input/prompt.txt`, launches the framework in a fresh workspace,
and collects artifacts. Read the workspace path from `WORKSPACE`; do not
hardcode it.

Participants provide the self-test model; `deepseek-v4.1-flash` is recommended
but not required. The organizer provides the official model through the same
environment variables. Neither stage permits hardcoded model IDs or endpoints.
See rules §4.

`FRAMEWORK_NATIVE_LOG_MARKER` must be emitted early by the framework itself.
Exit code 0 without the marker in `logs/e2e.log` is still non-native.
Check with `bash scripts/check_native_marker.sh logs/e2e.log`; a run root is
also accepted, and the second argument can specify a custom marker.

## 4. Task input

The runner composes `prompt.txt` from the contract, execution budget, and
task summary and mounts it at `input/prompt.txt`. For self-testing, set
`PROMPT_TASK_SUMMARY` or the template field. The organizer supplies the
summary during official evaluation.

The adapter converts the input into the framework's supported format. The
input must not prescribe an algorithm family, feature representation,
architecture, hyperparameters, experiment order, or selected method.

Submit the exact mounted `prompt.txt` and calculate `PROVENANCE.json`
`prompt_sha256` from that file.

## 5. Submission and run records

Retain one artifact set per topic. Task-specific payloads follow the
corresponding contract:

```
<framework>-<topic>-<YYYYMMDDTHHMMSS>/
├── PROVENANCE.json          # framework_commit / model / dataset_sha256 / split_sha256
├── workspace/
│   ├── research_idea.json
│   ├── experiment_trace.json
│   ├── environment.json     # run env — six required fields, see below
│   ├── final_report.md
│   └── <topic payload>      # predictions.csv | predictions.jsonl | estimator.py
├── logs/e2e.log             # raw stdout/stderr of the run
├── prompt.txt               # the exact mounted task input (runner writes it at workspace/input/prompt.txt, §4)
└── source/                  # optional: research code produced by the framework
```

The three public self-test payload formats are:

| Topic | Payload | Format |
|---|---|---|
| `tdc_admet_tox` | `predictions.csv` | `sample_id,endpoint,probability` |
| `psydefdetect` | `predictions.jsonl` | one `{"id":…,"predicted_label":…}` per line |
| `arc_wbe_2026` | `estimator.py` | `predict(mlp)` returning a `(32,256)` array |

`environment.json` requires `python_version`, `platform`, `device`, `seeds`,
`packages`, and `created_at`. The trace's `reproduction` block declares the
entrypoint, command, and seed needed to reproduce the selected experiment.
Use `templates/submission/environment.json.template` as a reference.

`dataset_sha256` and `split_sha256` must match the published values. Store
logs at `logs/e2e.log`. The community judge searches `logs/e2e.log`,
`logs/native.log`, and `logs/native_stdout.log` in that order; it does not
read a root-level `run.log`.

`PROVENANCE.json` records submission and run information. Validate its
format with `python3 scripts/validate_schemas.py --provenance <provenance-path>`.
Populate `model` with the actual model ID, not an environment variable name.
Schema validation does not establish factual accuracy. The official model
must also match trace `framework_internal_model` and organizer configuration.

## 6. Common validation issues

| Issue | Checks |
|---|---|
| Placeholder or constant outputs rejected | Confirm that real predictions and experiment artifacts were produced; a valid low raw score is not itself a placeholder |
| TDC sample-ID mismatch | Use `sample_id` from `test.csv` and preserve the `hERG` / `HERG_` distinction |
| ARC estimator rejected | Check the `mlp` parameter, output shape, and finite values |
| ARC `b0` or `bT` missing | Check numeric `framework_visible_validation` records; see rules §3.4 |
| Run classified as non-native | Check that the framework itself emitted the marker |
| Network interruption | Wall-clock limits continue; check connectivity, checkpoints, recovery, and client retries |
| Split validation failed | Use the frozen canonical split and checksum in rules §3.3 |

## 7. Schedule

Week 1 covers registration and environment setup, weeks 2–3 development and
self-testing, and week 4 submission. Results are published after official
evaluation. Contracts, dataset download, scorers, and documentation must be
validated before the competition opens.

Report issues through the repository issue tracker. See [FAQ](FAQ.md) for
common questions.
