# Metric System (long-term community leaderboard)

The competition leaderboard uses **objective official scores only** (see
`docs/rules.md` §6). This document describes the extended 12-dimension metric
system used by the long-term community leaderboard that runs after the
competition on the same harness, the same topics, and the same frozen splits.

The 12 dimensions: `b0 / bT / AUP / UR / ED` plus seven LLM-judge dimensions
`PQ / PEA / ER / OU / ECC / SC / CC`.

## 1. Trajectory metrics (deterministic arithmetic, no LLM)

Extracted from the run's `experiment_trace.json`. All four are computed by
plain arithmetic over the recorded trace — no model in the loop:

| Dim | What | Notes |
|---|---|---|
| `b0` | baseline-normalized first-experiment score | anchor-relative, see §3 |
| `bT` | baseline-normalized final/selected-experiment score | anchor-relative |
| `AUP` | area-under-progress of improvements across experiments | has a `1/N` floor — never averaged across topics; report N alongside any AUP |
| `UR` | utilization of the allowed experiment budget | |

Missing values are recorded as `null`, never filled with `0` — an anchor
value of 0 has real semantics (random-level), so filling would fabricate a
meaningful-looking score.

## 2. ED (experiment-design diversity)

`ED` measures how *methodologically* different the recorded experiments are.
It is computed by clustering the experiment descriptions: a run whose
experiments keep re-using one configuration family scores low; a run that
explored genuinely different approaches scores high.

**Data limitation:** `ED` requires the run to *record* its method choices.
Runs whose traces carry no per-experiment method descriptions cannot be
scored — those cells are `null`, not `0`.

## 3. Anchors

`b0`/`bT` normalize the raw score against fixed anchors
(`scoring/metric_anchors.json`) so that 0 has a clear meaning
(random-level) and topic scales are comparable:

| topic | worst (anchor=0) | best (anchor=1) | scale |
|---|---|---|---|
| `tdc_admet_tox` | 0.5 (random AUROC) | 1.0 (perfect AUROC) | linear |
| `psydefdetect` | 0.125 (random over 8 positive classes) | 1.0 (perfect macro-F1) | linear |
| `arc_wbe_2026` | 0.075 (random-level estimator) | 1e-06 (near-perfect est.) | log |

> The anchors are a **convention calibrated by the organizer, not an
> authoritative baseline**. Any citation of these values must carry that
> caveat.

## 4. The seven judge dimensions

For subjective/process dimensions, a unified LLM judge reads the run's
execution artifacts (logs, trace, report) and scores on frozen rubrics:

| Dim | Dimension | Judge sees |
|---|---|---|
| `PQ` | planning quality / idea quality | `research_idea.json`, log |
| `PEA` | experimental adequacy (do the experiments test the hypothesis) | trace, logs |
| `ER` | execution robustness (does the run actually do what it claims) | `e2e.log` |
| `OU` | output usage (does the report cite what the experiments actually produced) | report + trace |
| `ECC` | evidence-claim consistency | report + trace + logs |
| `SC` | state consistency (the run's stage/duty bookkeeping stays coherent) | trace |
| `CC` | completeness against the framework's own duty list | trace |

Operational rules:

- The judge runs on one unified model for the whole period; the model id is
  **frozen and published** at leaderboard start.
- Credentials are read exclusively from environment variables
  (`JUDGE_API_KEY` / `JUDGE_MODEL` / `JUDGE_BASE_URL`). The source contains
  no secrets and no default model id.
- The judge trusts `logs/e2e.log` (the run's raw output stream) above
  framework-written reports when they conflict.

### Known limitations (deliberate, not bugs)

- **Noise:** the single-call judge path measures a mean absolute difference
  around 0.052 with ~84% agreement on re-scored samples. Rank differences
  below the calibrated tie threshold are reported as ties.
- **Cost:** the container-agent paths (ER/SC/CC) cost on the order of
  47K tokens per run. This is a real per-run cost; the competition
  leaderboard deliberately does not include judge dimensions.
- **`CC` is framework-relative:** the judge derives the duty list from the
  run itself, so `CC` is comparable *within* a framework family, not across
  frameworks. Either a fixed stage contract is issued by the organizer, or
  `CC` is demoted to a display-only column.
- **Submitted-evidence caveat:** when *participants* run the harness
  themselves and submit artifacts (as in this competition), the log is the
  runner wrapper's live-tee of the framework's own stdout/stderr, submitted
  alongside the artifacts — faithful, but written by participant-owned code,
  not by the host. ER/SC/CC then measure the *quality of the submitted
  evidence*, not the execution itself. The community leaderboard's judge
  runs are host-captured again; this caveat applies only to fan-made
  submissions and should be stated whenever such numbers are cited.

## 5. What is and is not comparable

- Official scores from the competition are objective-scorer numbers on the
  frozen split. They are comparable to each other.
- Judge-dimension numbers are not comparable to official scores in any
  arithmetic sense.
- AUP is not averaged across topics (`1/N` floor).
- No missing cell is ever imputed with 0.