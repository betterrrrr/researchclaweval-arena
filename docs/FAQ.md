# FAQ

## The competition

**Q: Are the three public topics used for final scoring?**
No. They are for participant self-testing, and you can run and debug them
as often as needed. Final scoring uses other topics, run and scored by the
organizer. Self-test scores do not count toward final rankings. See
`docs/rules.md` §0 and §2.

**Q: Is the leaderboard a single merged score?**
No. Official evaluation has a separate ranking for each topic. Different
task metrics are not added together, and there is no overall champion.
Public self-test scores do not enter the final rankings. See `docs/rules.md`
§6.3 and `docs/announcement.md` §6.2.

**Q: Who provides the model?**
Two stages. Self-testing (before submission): you bring your own model —
the organizer does not restrict it (the organizer's recommended self-test
model is named in rules §4). Official evaluation (submission
scoring): the organizer injects the model via `OPENAI_BASE_URL` /
`OPENAI_API_KEY` / `OPENAI_MODEL`; bringing your own model or endpoint at
that stage is grounds for rejection. This is a framework contest, not a
model contest (rules §4).

**Q: Why is there no judge/LLM-scoring on the board?**
The competition board uses objective official scores only. The 7-dimension
LLM judge and ED belong to the long-term community leaderboard: they are
noisy, expensive, and in a submit-artifacts mode they would measure evidence
quality rather than execution (rules §6.2, appendix A).

## Data

**Q: Where do I get the data?**
You download it yourself and verify sha256 — `scripts/setup_datasets.sh`.
The organizer does not redistribute datasets (rules §3.2). If
`huggingface.co` is unreachable, set `HF_ENDPOINT=https://hf-mirror.com`.

**Q: Is PsyDefDetect really usable?**
Yes, under `cc-by-nc-4.0`. The competition is organized for non-commercial
purposes; make sure your own use complies before downloading.

**Q: What split do I have to use?**
The frozen canonical splits. `split_sha256` must match byte for byte; any
re-splitting is a rejection. For PsyDefDetect the canonical split is a
dialogue-level, leakage-free split distinct from the dataset's official
record-level one (rules §3.3).

## Scoring

**Q: My TDC score is exactly 0.**
Check `predictions.csv` `sample_id` values against `public/test.csv` —
`sample_id` must be taken verbatim from that file, never re-built
(`hERG` endpoint → `HERG_` prefix). One mismatched id → zero matches and a
zero score (rules §5.6).

**Q: My ARC estimator was rejected.**
The official adapter fails closed: `predict(self, mlp)` must return a real
`(32, 256)` float array. Constants, broadcast, scalar, zero-filled,
placeholder, or pasted log outputs are inadmissible (ARC contract,
"Required Outputs"). Also check the signature — some estimators omit the `budget`
parameter; the adapter probes the signature and supports both.

**Q: Why doesn't my ARC run have `b0`/`bT`?**
ARC is the one topic without a truth value for the framework. Numeric
`framework_visible_validation` self-evaluation records in
`experiment_trace.json` are required to compute those (rules §3.4); without
them the extended dimensions fall back to the judge's ordinal path.

**Q: My run exited 0 but scored nothing.**
Most likely the native marker is missing: `FRAMEWORK_NATIVE_LOG_MARKER` must
be printed by *your framework's own execution* into the run log, early in the
run (rules §5.5). A wrapper printing it on the framework's behalf is judged
non-native. Self-check with `bash scripts/check_native_marker.sh logs/e2e.log`.

**Q: What counts as the 2–4 experiments?**
Experiments are counted as *strategy lines*: a materially different
configuration cluster (differing in algorithm family / features /
architecture / overall hyperparameter-search design). Retries, seed-only
repeats, and small tuning inside one line do not count; failed setup
attempts never count; a configuration that was evaluated and then crashed or
timed out still counts for its line (rules §5.8, contracts' execution
budgets).

**Q: Can I submit a self-computed score?**
No. Self-reported scores never enter the board — placeholder values,
self-implemented metrics, and wrong splits are all rejection grounds
(rules §6.1, §8).

## Tooling

**Q: Is there a download bundle for participants?**
Yes — the GitHub releases carry `researchclaweval-arena-<version>.zip` /
`.tar.gz` (exact copies of the tagged tree, verified sha256 in the release
notes). Unzip anywhere, run `bash scripts/setup_datasets.sh`, and follow
`docs/participant_quickstart.md`. Datasets are never bundled — you download
and verify them yourself.

**Q: What is the runner?**
A template wrapper (`scripts/runner/`) that mounts contract + dataset
read-only, injects the model env, exports `WORKSPACE` / `DATASET_ROOT`,
composes the task input at `input/prompt.txt` (contract + execution budget +
task summary; rules §5.7), runs your framework natively in a fresh
workspace, and collects `logs/e2e.log` and the artifacts. You must use it
rather than your own ad-hoc orchestration so the artifacts are attributable
(rules §5.4).

**Q: What goes into the adapter manifest?**
`templates/example-adapter/manifest.json` — validated against
`schemas/adapter.schema.json` (framework id, name, upstream repo, license,
native entrypoint, required env/images, patches). Fill every TODO, that's
the entire integration surface. Validate locally with
`python3 scripts/validate_schemas.py --manifest <your-manifest.json>`.

**Q: What exactly is `resource_budget` in my trace?**
The declared compute budget, recorded verbatim: the audit compares it byte
for byte. The canonical dict is documented in
`contracts/tdc_admet_tox_compute_budget.md` (with a copyable JSON example)
and machine-readable in `scoring/resource_budget.anchors.json` — copy the
value from there, never from decoded error messages. It includes
`network_policy: "injected_llm_relay_only"` (rules §5.4).

**Q: What if the network flaps mid-run?**
The wall-clock budgets in the contracts keep running — a gateway blip is
not an exemption. Self-testing advice: prove the link with a tiny
experiment first, checkpoint your state, and resume from checkpoints;
configure client-side retries/backoff on your side (there is no official
knob on the injected relay; the community-board judge has its own retries,
rules §5.4).

**Q: Does the judge pipeline need a key from me?**
The judge runs organizer-side. The code reads `JUDGE_API_KEY` /
`JUDGE_MODEL` / `JUDGE_BASE_URL` from the environment; there are no secrets
and no default model id in the source.

**Q: I found a bug in a scorer glue script.**
Open an issue with the topic, the script name, and a minimal reproduction.
Do not email raw dataset files or keys to anyone.