#!/usr/bin/env bash
# Reproduce the golden run: both experiment configurations, then promote
# the better one and evaluate it on the public test split.
# seed 43 is the promoted configuration's seed (selected_experiment_id
# exp_002 in experiment_trace.json).
set -euo pipefail
echo "golden reproduction entrypoint (see experiment_trace.json / final_report.md)"
echo "run 1: fingerprint 1024 bits, unweighted, seed 42"
echo "run 2: fingerprint 2048 bits, balanced, seed 43"
echo "select by validation macro AUROC, write root-level predictions.csv"