#!/usr/bin/env bash
# ============================================================================
# check_native_marker.sh — verify your logs/e2e.log carries the native marker
#
# Usage:
#   bash scripts/check_native_marker.sh <log-or-run-root> [MARKER]
#
# The default marker is the runner template's MYFRAMEWORK_NATIVE; pass your
# own when you changed FRAMEWORK_NATIVE_LOG_MARKER. If the argument is a
# directory, logs/e2e.log is looked up inside it (run-root layout).
# Exit 0 = PASS, 1 = FAIL (rules §5.5).
# ============================================================================
set -euo pipefail

TARGET="${1:?usage: check_native_marker.sh <log-or-run-root> [MARKER]}"
MARKER="${2:-MYFRAMEWORK_NATIVE}"

if [ -d "$TARGET" ]; then
  LOG="$TARGET/logs/e2e.log"
else
  LOG="${TARGET%/}"
fi

if [ ! -f "$LOG" ]; then
  echo "FAIL: log file not found: $LOG" >&2
  exit 1
fi

if grep -qF -- "$MARKER" "$LOG"; then
  echo "PASS: native marker '$MARKER' found in ${LOG#./}"
  echo "The run is attributable as framework-native execution (rules §5.5)."
  exit 0
fi

echo "FAIL: native marker '$MARKER' not found in ${LOG#./}" >&2
echo "The framework must print the marker from inside its own execution," >&2
echo "as early as possible (rules §5.5). A wrapper printing it on the" >&2
echo "framework's behalf is judged non-native. It should appear near the" >&2
echo "top of e2e.log." >&2
exit 1