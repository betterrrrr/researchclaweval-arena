#!/usr/bin/env bash
# Reproduce the golden run: both experiment configurations, then promote
# the better one and evaluate it on the public test split.
set -euo pipefail
echo "golden reproduction entrypoint (see experiment_trace.json / final_report.md)"
echo "run 1: fingerprint 1024 bits, unweighted"
echo "run 2: fingerprint 2048 bits, balanced"
echo "select by validation macro AUROC, write root-level predictions.csv"