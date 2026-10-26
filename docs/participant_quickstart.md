# Participant Quickstart

> If the docs disagree with the rules (`docs/rules.md`), the rules win.
> If the rules disagree with a contract (`contracts/*.md`), the contract wins.

This guide uses the three public topics for integration and self-testing.
**Final scoring uses other topics, run and scored by the organizer.
Scores on these self-test topics do not count toward final rankings.**

## 0. What you will do

1. Register and receive a framework id (a two-digit number).
2. Set up the three datasets (download + sha256 verify yourself).
3. Read the three contracts.
4. Write exactly one adapter: how to *launch* your framework.
5. Run through the official runner template.
6. Submit the open-source framework repo and run artifacts as required by the
   rules; the organizer evaluates the framework on other topics.

Your framework must own **planning, experiment design, execution, comparison,
selection, and final delivery** — the adapter contains no evaluation logic.

---

## 1. Datasets

```bash
bash scripts/setup_datasets.sh --dataset tdc_admet_tox   # ~1.4 MB
bash scripts/setup_datasets.sh --dataset psydefdetect    # ~5.4 MB
bash scripts/setup_datasets.sh --dataset arc_wbe_2026    # ~907 MB
```

The script downloads from the original public sources and refuses anything
whose sha256 does not match the frozen value (see `docs/rules.md` §3.2).
Then export the dataset roots:

```bash
export TDC_ADMET_TOX_DATASET_ROOT=$PWD/data/tdc_admet_tox/public
export PSYDEFDETECT_DATASET_ROOT=$PWD/data/psydefdetect
export ARC_WBE_2026_DATASET_ROOT=$PWD/data/arc_white_box_estimation_2026
```

If `huggingface.co` is unreachable in your network, set
`HF_ENDPOINT=https://hf-mirror.com` (the script falls back to the mirror only
after direct access fails).

> ⚠️ `psydefdetect` is `cc-by-nc-4.0`. The competition is held for
> **non-commercial** purposes; make sure your individual use is compliant
> with the license before downloading.

## 2. Contracts

Read these three:

- `contracts/arc_wbe_2026_contract.md` — pay attention to the **visible
  validation set** (§3.4 of the rules): 10 of 100 MLPs are given to you with
  ground truth so you can self-evaluate with the official metric. The other
  90 are the scoring set and are never mounted into your container.
- `contracts/psydefdetect_contract.md` — macro-F1 over positive classes 1–8;
  the dialogue-level split is frozen (file `psydefdetect_split.canonical.json`
  in the repo root; canonical sha256 in `docs/rules.md` §3.3). You can
  self-score immediately:

  ```bash
  python3 scoring/run_psydefdetect_local_score.py \
    --dataset-root "$PSYDEFDETECT_DATASET_ROOT" \
    --predictions predictions.jsonl \
    --output-score score.json
  ```
- `contracts/tdc_admet_tox_contract.md` — macro average of AMES / hERG / DILI
  AUROC. Read §5.6 of the rules about `sample_id` **before** writing code
  (`hERG` endpoint → `HERG_` id prefix). Self-check once a day with
  `bash scripts/selfcheck_tdc.sh` (audits the golden run, then the optional
  reference-baseline round trip when `TDC_ADMET_TOX_DATASET_ROOT` is set).

All contracts share the same spine:

- write and lock `research_idea.json` **before** your first experiment
- run **2–4 materially different** experiments — counted as **strategy lines**:
  retries and seed-only repeats inside one line don't count, and a line is
  established only by a complete experiment (rules §5.8) — then immediately
  promote the selected result (never a 5th)
- record every experiment in `experiment_trace.json`

## 3. The adapter

Copy the skeleton:

```bash
cp -r templates/example-adapter/ myframework/
```

The manifest (`manifest.json`) declares: framework id, name, upstream
repository, license, native entrypoint, required env, required images, and
patches. Fill every TODO — validate locally against
`schemas/adapter.schema.json` with
`python3 scripts/validate_schemas.py --manifest myframework/manifest.json`.

Your fullrun wrapper follows the runner template in `scripts/runner/`:
it mounts the contract and dataset read-only into a fresh workspace, injects
the model endpoint via env (`OPENAI_BASE_URL` / `OPENAI_API_KEY` /
`OPENAI_MODEL`), exports `WORKSPACE` (the fresh workspace path) and
`DATASET_ROOT`, composes the task input at `input/prompt.txt` (see §4), runs
your framework natively, and collects the artifacts. Locate your workspace
through the `WORKSPACE` env var — never hardcode the path.

**Model policy (rules §4):** self-testing uses your own model — the
organizer does not restrict you (the recommended self-test model is named in
rules §4). Official evaluation injects the
organizer's model over the same three env vars; never hardcode an endpoint
or a model id in your code either way.

**Native execution marker.** Your framework must print
`FRAMEWORK_NATIVE_LOG_MARKER` from inside its own execution, as early as
possible. A run that exits 0 without this marker in `logs/e2e.log` is judged
non-native and does not score. Self-check with
`bash scripts/check_native_marker.sh logs/e2e.log` (pass the run root, or
your custom marker as a second argument).

## 4. Prompt.txt

The organizer provides a unified task input per topic (contract + budget +
task summary) named `prompt.txt`. The runner template composes it into the
fresh workspace at `input/prompt.txt` from the contract, the execution
budget, and a task summary you set during self-testing (export
`PROMPT_TASK_SUMMARY` or fill it in the template) or the organizer provides
at official evaluation. Translating it into a form your framework can
consume is the adapter's job. The prompt must **not prescribe any method** —
algorithm family, feature representation, architecture, hyperparameters,
experiment order, selected method are all decided by your framework.

The submitted `prompt.txt` is the exact file the runner mounted, and
`PROVENANCE.json` `prompt_sha256` is its sha256 — self-test what you submit.

## 5. Submission

Per topic, one artifact set:

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

Payload formats (rules §5.3):

| topic | payload | format |
|---|---|---|
| `tdc_admet_tox` | `predictions.csv` | `sample_id,endpoint,probability` |
| `psydefdetect` | `predictions.jsonl` | one `{"id":…,"predicted_label":…}` per line |
| `arc_wbe_2026` | `estimator.py` | `predict(mlp)` returning a `(32,256)` array |

`environment.json` records the run environment — the audit checks six fields
(`python_version`, `platform`, `device`, `seeds`, `packages`, `created_at`);
the trace's `reproduction` block declares the exact entrypoint, command, and
seed that rerun the promoted experiment. Start from
`templates/submission/environment.json.template`.

`dataset_sha256` and `split_sha256` must match the published values byte for
byte; a mismatch is rejected without scoring. `logs/e2e.log` is the primary
record — the judge pipeline reads `logs/e2e.log` → `logs/native.log` →
`logs/native_stdout.log`, never a root-level `run.log`.

`PROVENANCE.json` is your self-reported submission ledger (no code validates
it today) — fill `model` with the model id actually used for that run at
export time, never an env var name. The model value that *is* machine-checked
is `experiment_trace.json` `framework_internal_model`, which must equal the
published official model at official evaluation (rules §4).

## 6. Common failure modes

| Symptom | Likely cause |
|---|---|
| All-zero / constant score | placeholder or constant predictions (§8 of the rules) |
| TDC score of exactly 0 | `sample_id` built by hand, not taken from `test.csv` (`hERG` vs `HERG`) |
| ARC estimator rejected | `predict()` missing `mlp` param, wrong shape, or non-finite values — the official adapter fails closed |
| `b0`/`bT` missing in your trace | ARC: no numeric `framework_visible_validation` record (contract §3.4) |
| Run judged non-native | `FRAMEWORK_NATIVE_LOG_MARKER` missing or printed by the wrapper instead of the framework |
| Gateway blips mid-run | wall-clock budgets still tick (rules §5.4); run tiny probes first, checkpoint, resume, client-side retry/backoff |
| Rejected split | your dataset was re-split; use the frozen canonical split (sha256 in rules §3.3) |

## 7. Timeline

```
Before      contracts frozen · data downloadable · scorers run · docs ready
Week 1      registration + environment setup
Weeks 2–3   development and self-testing
Week 4      submission window → organizer scoring → results published
```

Questions? Open an issue, or read `docs/FAQ.md` first.