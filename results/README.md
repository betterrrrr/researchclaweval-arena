# Results

This directory is empty **until the submission window closes**.

The competition leaderboard contains official objective scores from the
organizer's evaluation on topics other than the three public self-test topics,
with an overall championship and per-topic rankings. Self-test scores do not
count toward final rankings. Publishing policy:

- Only host-scored official values enter the board (no self-reported numbers).
- Publish each official topic's raw score, normalized 0–100 score, outcome
  status, and rank, plus the equal-weight mean total and first-place count.
  Use reference values fixed and published before official evaluation.
- Compare totals rounded half up to six decimal places. The highest total
  wins; tied totals are resolved by topic first-place count, then a shared
  rank. Topic first places use valid raw scores, not clipped normalized
  scores; each tied first-place framework receives one first-place count.
- Failed or missing valid results contribute 0 while remaining in the fixed
  topic count; retain `null` as the raw score and show the failure status.
  At least one valid official result is required for the overall board;
  disqualified frameworks are excluded. See `docs/rules.md` §6.3.
- Every number passes the contamination discipline (placeholder values /
  non-official metrics / substitute datasets are rejected and registered).
- Anchors cited alongside `b0`/`bT`-style normalized numbers are a
  convention, not an authoritative baseline — any such citation carries that
  caveat (see `docs/metric-system.md` §3).
- The long-term community leaderboard (12-dimension, judge-based) is a
  separate surface; timing and granularity are decided separately.

Untracked content in this directory is ignored by `.gitignore` until
publishing is authorized.