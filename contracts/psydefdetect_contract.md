# PsyDefDetect Runtime Contract

## Topic
- Topic id: `psydefdetect`
- Topic label: `PsyDefDetect`
- Dataset root: `data/psydefdetect`
- Dataset env: `PSYDEFDETECT_DATASET_ROOT`
- Contract file: `contracts/psydefdetect_contract.md`

## Objective
Build methods for the PsyDefDetect shared task: detecting levels of psychological defense mechanisms in supportive conversations.

## Shared inputs
- `contracts/psydefdetect_execution_budget.md`
- `scoring/run_psydefdetect_local_score.py`
- the standardized split: `psydefdetect_split.canonical.json`（仓库根；sha256 公示见 `docs/rules.md` §3.3）

## Task Definition
Given a target help-seeker utterance and the preceding supportive conversation context, predict one of nine labels:

- `0`: No Defense
- `1`: Action Defenses
- `2`: Major Image-Distorting
- `3`: Disavowal
- `4`: Minor Image-Distorting
- `5`: Neurotic
- `6`: Obsessional
- `7`: High-Adaptive
- `8`: Needs More Information

## Metric
The primary score is macro-F1 over positive classes `1-8`. Class `0` is excluded from the official macro-F1 calculation.

## Required Outputs
- A prediction artifact for the standardized evaluation split, preferably `predictions.jsonl` or `submission.csv`
- A concrete `score.json` artifact produced by running the provided local scorer on the standardized split
- An `experiment_trace.json` artifact proving at least 2 materially different experiments were run and compared
- `final_report.md`
- Logs and workspace traces

## Experiment Contract
- Use the standardized split whose canonical sha256 is published in `docs/rules.md` ("Split Freeze").
- Run exactly 2 to 4 materially different experiments before selecting a final approach. Never start a fifth experiment.
- Follow `contracts/psydefdetect_execution_budget.md`: record compact experiment results, only use experiments 3-4 for a specific improvement over the current best result, and finalize immediately after the last experiment.
- Record those experiments in `experiment_trace.json`.
- Use the framework's own orchestration flow as much as possible for planning, experiment execution, comparison, and finalization.
- Do not satisfy this task by only dropping ad-hoc one-off scripts or scattered per-experiment folders without a framework-level final selection and handoff.
- Do not rely on runtime downloads of new Hugging Face models or other large external model assets.
- Any framework-internal API experiment must use the injected `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and `OPENAI_MODEL` environment variables. `OPENAI_MODEL` must equal the evaluation target model; do not hardcode `api.openai.com` or another public provider endpoint.
- If a stronger second experiment is needed, prefer:
  - the configured remote API model path already available in the framework runtime
  - container-local dependencies or models that are already present
  - non-download alternatives such as prompting, reranking, self-consistency, or retrieval-style comparisons
- `experiment_trace.json` must include:
  - `framework_native_execution: true`
  - `consumed_topic_input: true`
  - `workspace_trace_root`
  - `experiments` with length 2-4
  - `selected_experiment_id`
  - `prediction_artifact`
  - `score_artifact`
  - `framework_internal_model` equal to the evaluation target model
  - `framework_internal_api_base_url` populated from the injected environment
- Before exit, the framework must promote the selected final artifacts to `/workspace/predictions.jsonl` or `/workspace/submission.csv`, `/workspace/score.json`, `/workspace/experiment_trace.json`, and `/workspace/final_report.md`.
- If the framework cannot complete that finalization step inside its own flow, it should stop with a concrete blocker rather than silently leave partial experiment outputs.
- A single lightweight baseline without comparative experimentation does not satisfy this contract.

## Scope Guard
- Do not route this topic to any other topic's wrappers, scorers, contracts, datasets, or workspaces.
- Do not reuse another topic's fixed workspace as a writable or template workspace.
- Use fresh physical run workspaces under the current `RUN_ROOT` for evaluation runs.
