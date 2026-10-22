#!/usr/bin/env bash
# ============================================================================
# selfcheck_tdc.sh — one-command TDC-ADMET-Tox self-check
#
# 1. Audits the golden run (needs nothing but this repo).
# 2. If TDC_ADMET_TOX_DATASET_ROOT is set AND the reference baseline's
#    dependencies are installed, runs the baseline into a temp run root and
#    audits its output with the same validator (exercises the full path).
#
# Any failing step stops the selfcheck. Exit codes per the CLI conventions
# (docs/scorer-contracts.md).
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="${PYTHON:-python3}"
VALIDATOR="scoring/validate_tdc_admet_tox_run.py"
GOLDEN="templates/submission/golden_tdc_admet_tox"

echo "[selfcheck] 1/2 audit the golden run (run-root layout, logs at root)"
"$PY" "$VALIDATOR" --run-root "$GOLDEN" --stage framework >/dev/null
echo "[selfcheck] golden audit: PASS"

if [ -n "${TDC_ADMET_TOX_DATASET_ROOT:-}" ]; then
  echo "[selfcheck] 2/2 TDC_ADMET_TOX_DATASET_ROOT is set: running the reference baseline"
  OUT="$(mktemp -d)"
  trap 'rm -rf "$OUT"' EXIT
  "$PY" scoring/run_tdc_admet_tox_reference_baseline.py \
    --public-dataset-root "$TDC_ADMET_TOX_DATASET_ROOT" \
    --output-root "$OUT"
  "$PY" "$VALIDATOR" --run-root "$OUT" --stage framework >/dev/null
  echo "[selfcheck] baseline run audit: PASS"
else
  echo "[selfcheck] 2/2 skipped (TDC_ADMET_TOX_DATASET_ROOT unset) — export it and"
  echo "          re-run to exercise the reference-baseline round trip."
fi

echo "[selfcheck] TDC-ADMET-Tox selfcheck: PASS"