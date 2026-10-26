# Community Leaderboard Metric System

This document defines the 12-dimension metric system for the community
leaderboard maintained after the competition. Community topics and splits
are specified separately. The three public self-test topics are not the
final competition evaluation topics.

Competition rankings use official objective scores normalized to 0–100 and
averaged with equal weights. Tied totals are resolved by topic first-place
count, then a shared rank. Competition reference values are specified
separately from the community anchors below. See `docs/rules.md` §6.3.

The community dimensions are `b0 / bT / AUP / UR / ED` and
`PQ / PEA / ER / OU / ECC / SC / CC`.

## 1. Trajectory metrics

The following metrics are calculated from `experiment_trace.json` without
LLM scoring:

| Metric | Definition | Reporting requirement |
|---|---|---|
| `b0` | Anchor-normalized first-experiment score | Use the reference values in §3 |
| `bT` | Anchor-normalized final or selected-experiment score | Use the reference values in §3 |
| `AUP` | Area under experimental progress | Has a `1/N` lower bound; report N and do not average across topics |
| `UR` | Utilization of the permitted experiment budget | Use the task's declared budget |

Missing community metric values are recorded as `null`. An anchor score of
0 represents random-level performance and must not substitute for missing
evidence. This differs from the competition rule assigning a failed topic
0 contribution to the total while retaining a `null` raw score.

## 2. Experiment-design diversity

`ED` evaluates methodological differences between recorded experiments.
It groups experiment descriptions by method, distinguishing repeated
configurations from different approaches. Runs without method descriptions
cannot be evaluated for this dimension; record `null`.

## 3. Normalization anchors

`b0` and `bT` use fixed anchors in `scoring/metric_anchors.json`:

| Topic | Reference at 0 | Reference at 1 | Scale |
|---|---|---|---|
| `tdc_admet_tox` | 0.5, random AUROC | 1.0, perfect AUROC | Linear |
| `psydefdetect` | 0.125, uniform random over 8 positive classes | 1.0, perfect macro-F1 | Linear |
| `arc_wbe_2026` | 0.075, random-level estimator | 1e-06, near-perfect estimator | Logarithmic |

These are organizer-defined calibration references, not authoritative
benchmark baselines. Publications citing them must state this limitation.
They do not define the reference values for formal competition topics.

## 4. LLM-judge dimensions

A single judge model evaluates execution artifacts against fixed rubrics:

| Metric | Dimension | Evidence |
|---|---|---|
| `PQ` | Research planning and idea quality | `research_idea.json`, logs |
| `PEA` | Adequacy of experiments for testing the hypothesis | Trace, logs |
| `ER` | Execution robustness | `e2e.log` |
| `OU` | Use of experimental outputs in the report | Report, trace |
| `ECC` | Consistency between evidence and claims | Report, trace, logs |
| `SC` | Consistency of recorded workflow state | Trace |
| `CC` | Completion of the framework's declared obligations | Trace |

The judge model ID is fixed and published for each evaluation period.
Credentials and configuration are read from `JUDGE_API_KEY`, `JUDGE_MODEL`,
and `JUDGE_BASE_URL`; source files contain no credentials or default model ID.
When execution logs conflict with reports or plans, logs take precedence.

### Evaluation limitations

- LLM scoring has additional execution cost and variability. Differences
  below the calibrated tie threshold are reported as ties. Judge dimensions
  do not affect competition rankings.
- `CC` is relative to obligations inferred from a framework's own run.
  Cross-framework comparison requires a common stage contract; otherwise,
  report `CC` as a descriptive column only.
- For participant-run submissions, the participant controls the submitted
  logs even when the runner records stdout/stderr in real time. `ER`, `SC`,
  and `CC` therefore reflect the submitted evidence and do not establish
  independently observed execution. Distinguish these submissions from
  organizer-run evaluations with host-captured logs.

## 5. Comparability and missing values

- Compare official raw scores within the same topic and fixed data split.
  Competition totals combine scores only through the normalization defined
  in the competition rules.
- Do not combine judge scores arithmetically with official task scores.
- Do not average `AUP` across topics; its lower bound depends on N.
- Record missing community metric values as `null`, not 0.
