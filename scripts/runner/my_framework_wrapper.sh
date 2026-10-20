#!/usr/bin/env bash
# ============================================================================
# my_framework_wrapper.sh — generic full-run runner template
#
# Copy per framework per topic as  scripts/runner/<id>_<framework>_<topic>_fullrun.sh
# and fill the TODO blocks below. The runner:
#   • creates a fresh physical run workspace (never reuses or mutates templates)
#   • mounts contract + dataset read-only
#   • injects the organizer-provided model env (OPENAI_*) and the FRAMEWORK_*
#     wrapper-contract variables
#   • runs your framework's native entrypoint and captures logs/e2e.log
# The framework itself must own planning, experiments, comparison, selection,
# and final artifact delivery (rules §7.2). The runner contains no evaluation
# logic.
# ============================================================================
set -euo pipefail

# --- TODO(replace-me): fill in ---
FRAMEWORK_ID="NN"                          # your registered two-digit id
FRAMEWORK_NAME="replace-me-framework"
TOPIC="replace-me-topic"                   # tdc_admet_tox | psydefdetect | arc_wbe_2026
CONTRACT_FILE="contracts/replace_me_contract.md"   # path inside this repo
DATASET_ENV_NAME="REPLACE_ME_DATASET_ROOT"         # env var with the dataset root
ENTRYPOINT="${FRAMEWORK_ENTRYPOINT:-}"             # may also be injected
RUN_ROOT="${RUN_ROOT:-$PWD/runs}"

# --- wrapper-contract interface (public contract) ---
export FRAMEWORK_RUNTIME_KIND="native"     # launching the framework's own pipeline
export FRAMEWORK_ENTRY_PATHS="${FRAMEWORK_ENTRY_PATHS:-$ENTRYPOINT}"
export FRAMEWORK_PROVIDER_INJECTION="env"  # OPENAI_BASE_URL/OPENAI_API_KEY/OPENAI_MODEL
export FRAMEWORK_NATIVE_LOG_MARKER="${FRAMEWORK_NATIVE_LOG_MARKER:-MYFRAMEWORK_NATIVE}"

# --- model env (rules §4) — yours during self-testing, the organizer's at
# official evaluation; the framework code never hardcodes an endpoint/id ---
: "${OPENAI_BASE_URL:?set your own values for self-testing; the organizer injects at official evaluation (rules §4)}"
: "${OPENAI_API_KEY:?set your own values for self-testing; the organizer injects at official evaluation (rules §4)}"
: "${OPENAI_MODEL:?set your own values for self-testing; the organizer injects at official evaluation (rules §4)}"

RUN_ID="${FRAMEWORK_ID}-${FRAMEWORK_NAME}-${TOPIC}-$(date +%Y%m%dT%H%M%S)"
WS="$RUN_ROOT/$RUN_ID/workspace"
mkdir -p "$WS/input" "$RUN_ROOT/$RUN_ID/logs"

# --- mount contract read-only ---
cp "$CONTRACT_FILE" "$WS/input/contract.md"
chmod -R a-w "$WS/input"

# --- dataset (read-only) ---
: "${!DATASET_ENV_NAME:?$DATASET_ENV_NAME must point at the dataset root}"
export DATASET_ROOT="${!DATASET_ENV_NAME}"

echo "[runner] run id: $RUN_ID"
echo "[runner] topic:  $TOPIC"
echo "[runner] the framework must print $FRAMEWORK_NATIVE_LOG_MARKER from inside its own execution"

# --- run the framework's native pipeline, capturing the raw log stream ---
{
  # TODO(replace-me): invoke your framework through its documented native
  # entrypoint (no generic driver loops; rules §5.4).
  eval "${FRAMEWORK_ENTRY_PATHS:?nothing to run — fill ENTRYPOINT or set FRAMEWORK_ENTRY_PATHS}"
} 2>&1 | tee "$RUN_ROOT/$RUN_ID/logs/e2e.log"

echo "[runner] artifacts must be in $WS (research_idea.json / experiment_trace.json / final_report.md / topic payload)"
echo "[runner] finished: $RUN_ROOT/$RUN_ID"