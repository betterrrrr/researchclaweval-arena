# Golden Run — Final Report

## What was done

Two materially different configurations were designed and locked before the
first evaluation began, following the experiment-budget rules in the
execution budget.

## What was compared

Configuration exp_001 used a compact fingerprint with an unweighted
regularized linear head. Configuration exp_002 used a wider fingerprint
with balanced class weighting. Both were evaluated on the fixed validation
split with the official metric. Each configuration ran exactly one
candidate.

## What was selected

exp_002 achieved the best validation macro AUROC and was promoted to
produce the final predictions. The full reproducible command is
`bash reproduce.sh`.

## Artifacts

The experiment trace, environment record, per-experiment predictions and
metrics, and this report live next to the payload at the workspace root, per
the submission spec layout.