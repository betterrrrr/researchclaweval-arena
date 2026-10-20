# Example adapter (anonymized skeleton)

This is a **placeholder skeleton** — every value is a `replace-me` placeholder
or a plain example. It shows the integration surface a participant fills in;
it is not a real framework and contains no framework code.

## What an adapter is

One directory in your team's repository that declares **how to launch your
framework**. It contains no evaluation logic: topic selection, hypothesis,
experiment design, execution, comparison, selection, and final report are all
owned by your framework during the run (rules §7.2).

## TODO list (5 places)

1. `manifest.json` — `framework_id` (`NN`), `name`, `upstream_url`,
   `upstream_commit`, `license_spdx`, `native_entrypoint` (+ source file),
   `required_images` (or remove if none), `patches` (or `[]`).
   Validated against `schemas/adapter.schema.json`.
2. `entrypoint.example.py` — replace with a pointer to (or a thin launcher
   of) your framework's real native entrypoint. The launched process, not the
   wrapper, must own the whole research flow.
3. Print the native marker **from inside your framework's execution**:
   ```
   FRAMEWORK_NATIVE_LOG_MARKER
   ```
   as early as possible in the run; without it in `logs/e2e.log` the run is
   non-native and does not score (rules §5.5).
4. Respect the injected model env (`OPENAI_BASE_URL` / `OPENAI_API_KEY` /
   `OPENAI_MODEL`). Never hardcode an endpoint or a model id — that is a
   rejection (rules §4).
5. Deliver the per-topic payload into the workspace root of the run
   (`templates/submission/` shows the artifact layout):
   - tdc: `predictions.csv` (`sample_id,endpoint,probability`)
   - psydef: `predictions.jsonl` (one `{"id":…,"predicted_label":…}` per line)
   - arc: `estimator.py` with `predict(self, mlp)` returning `(32, 256)`

## Runner

`scripts/runner/my_framework_wrapper.sh` is the generic runner template:
it mounts contract + dataset read-only, injects the provider env, runs your
entrypoint in a fresh workspace, and collects `logs/e2e.log`. Copy it per
topic as `<id>_<framework>_<topic>_fullrun.sh` and fill the topic parameters
(contract path, dataset env, budget, payload expectations).

See `docs/participant_quickstart.md` for the end-to-end walkthrough.