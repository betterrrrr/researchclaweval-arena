# Frequently Asked Questions

[中文](FAQ.zh-CN.md). This page explains participation and self-testing.
The rules in `docs/rules.md` take precedence.

## Competition

**Are the three public topics used for final scoring?**

The public topics are for development and self-testing and may be run
repeatedly. Official evaluation uses other topics, run and scored by the
organizer. Self-test scores do not count toward final rankings. See rules
§0 and §2.

**How are the overall score and champion determined?**

Normalize each official topic score to 0–100 using reference values fixed
before evaluation, then take the equal-weight mean. The highest total wins.
Tied totals are resolved by topic first-place count; if that also ties, the
rank is shared. Per-topic rankings are also published. See rules §6.3 for
the formula and comparison precision.

**How are failed or missing results handled?**

The topic contributes 0 to the total and remains in the fixed topic count.
Record the raw score as `null` and retain the outcome status. Do not average
only successful topics. At least one valid official result is required for
the overall board; disqualified frameworks are excluded.

**Who provides the model?**

Participants provide their model for self-testing; the recommendation in
rules §4 is optional. For official evaluation, the organizer supplies
`OPENAI_BASE_URL`, `OPENAI_API_KEY`, and `OPENAI_MODEL`. An alternative model
or endpoint is not permitted at that stage. Neither stage permits model IDs
or endpoints to be hardcoded in framework code.

**Do LLM-judge scores affect competition rankings?**

Competition rankings use official objective scores. The seven LLM-judge
dimensions and ED belong to the community leaderboard. Their use is subject
to evaluation cost, scoring variability, and evidence provenance. See rules
§6.2 and Appendix A.

## Data

**How are datasets obtained?**

Use `scripts/setup_datasets.sh` to download from the original sources and
verify SHA-256. The organizer does not redistribute datasets. If
`huggingface.co` is unreachable, set `HF_ENDPOINT=https://hf-mirror.com`.
See rules §3.2.

**What license applies to PsyDefDetect?**

The data uses `cc-by-nc-4.0`. The competition is non-commercial, and
participants' data use must comply with the license.

**Which data split is required?**

Use the frozen canonical split. `split_sha256` must match the published
value exactly. PsyDefDetect uses a dialogue-level split, distinct from the
dataset's record-level split. See rules §3.3.

## Scoring and validation

**How should a TDC sample-ID mismatch be resolved?**

Use `sample_id` directly from `public/test.csv`; do not reconstruct it.
The `hERG` endpoint uses the `HERG_` ID prefix. The prediction ID and endpoint
keys must match the test file exactly. A mismatch is rejected by validation
or scoring and does not produce a valid raw score of 0. See rules §5.6.

**What output must an ARC estimator produce?**

`predict(mlp)` must return a `(32, 256)` numeric array satisfying the
contract. The adapter supports implementations with or without a `budget`
parameter. It rejects incorrect shapes, non-finite values, constants,
zero-filled, broadcast, scalar, and placeholder outputs. See the ARC
contract's Required Outputs.

**What should be checked when ARC `b0` or `bT` is missing?**

Check for numeric `framework_visible_validation` records in
`experiment_trace.json`. ARC provides ground truth for visible validation;
scoring-set ground truth remains organizer-side. Without numeric records,
`b0` and `bT` cannot be computed from those records, and extended evaluation
uses the judge's ordinal path. See rules §3.4.

**Does exit code 0 establish a valid run?**

Exit status does not replace artifact and native-execution validation.
`FRAMEWORK_NATIVE_LOG_MARKER` must be emitted early by the framework itself,
not by its outer wrapper. Check with
`bash scripts/check_native_marker.sh logs/e2e.log`. See rules §5.5.

**How are the 2–4 experiments counted?**

Count strategy lines that differ materially in algorithm family, feature
representation, architecture, or overall hyperparameter-search design.
Retries, seed-only repeats, and minor tuning within a line do not add a
line. Setup attempts without training or evaluation are logged only.
Configurations evaluated before a crash or timeout still count within their
line. See rules §5.8.

**Are participant-computed scores accepted?**

Self-scores support development and debugging only. The organizer computes
official results using the required metrics and fixed splits. See rules
§6.1 and §8.

## Tools and execution

**Are release bundles available?**

GitHub Releases provides `researchclaweval-arena-<version>.zip` and `.tar.gz`
for the tagged source tree, with checksums in the release notes. Extract a
bundle and follow `docs/participant_quickstart.md`. Datasets are not bundled
and must be obtained through the download scripts.

**What does the runner do?**

Templates in `scripts/runner/` mount contracts and datasets read-only,
inject model configuration, export `WORKSPACE` and `DATASET_ROOT`, compose
`input/prompt.txt`, launch the framework in a fresh workspace, and collect
`logs/e2e.log` and artifacts. Runs must use the official template. See rules
§5.4 and §5.7.

**What belongs in the adapter manifest?**

`templates/example-adapter/manifest.json` declares the framework ID, name,
upstream repository, license, native entrypoint, required environment
variables, images, and patches. Replace the placeholders and validate with
`python3 scripts/validate_schemas.py --manifest <manifest-path>` against
`schemas/adapter.schema.json`.

**How should trace `resource_budget` be populated?**

Use the complete budget object specified by the contract. For TDC, the
requirements and example are in `contracts/tdc_admet_tox_compute_budget.md`;
the machine-readable value is in `scoring/resource_budget.anchors.json`.
It includes `network_policy: "injected_llm_relay_only"`. Validation requires
an exact match; error messages should not be used to reconstruct the object.

**Does a network interruption pause the budget?**

Contract wall-clock limits continue to apply, without extra time. Verify
connectivity before self-testing, save checkpoints, and configure retries,
backoff, and recovery in the framework client. The injected relay has no
shared retry setting; the community judge has its own retry mechanism.
See rules §5.4.

**Who configures judge credentials?**

The organizer runs the judge with `JUDGE_API_KEY`, `JUDGE_MODEL`, and
`JUDGE_BASE_URL`. Source files contain no credentials or default model ID.

**How should a scoring-tool issue be reported?**

Open an issue with the topic, script name, and minimal reproduction steps.
Do not include raw datasets or credentials in reproduction material.
