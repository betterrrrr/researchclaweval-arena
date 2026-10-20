#!/usr/bin/env bash
# ============================================================================
# check-release.sh — release safety gate for researchclaweval-arena
#
# Two engines:
#   1. allowlist: every git-tracked file must appear in scripts/allowlist.txt
#      and vice versa (bi-directional diff is empty).
#   2. pattern scan: forbidden strings, hosts, file names, oversized files,
#      and symlinks across the tree.
#
# Usage:
#   bash scripts/check-release.sh              # full gate (inside a git worktree)
#   bash scripts/check-release.sh --path DIR   # pattern scan only on DIR
#
# Exits non-zero on any finding. The script itself and the shared rule files
# necessarily contain pattern text and are exempted from their own scan.
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="full"
TARGET="$ROOT"
if [[ "${1:-}" == "--path" ]]; then
  MODE="path"
  TARGET="${2:?--path requires a directory}"
fi

failed=0

# Files that carry pattern text by construction:
EXEMPT=(
  "scripts/check-release.sh"
  "scripts/gitleaks.toml"
  "scripts/forbidden-hosts.txt"
  "scripts/allowlist.txt"
  "tests/test_release_safety.py"
)

list_files() {
  if [[ "$MODE" == "full" ]]; then
    git ls-files
  else
    find "$TARGET" -type f -not -path '*/.git/*'
  fi
}

is_exempt() {
  local rel="$1"
  local e
  for e in "${EXEMPT[@]}"; do
    [[ "$rel" == "$e" ]] && return 0
  done
  return 1
}

# ---- allowlist engine (full mode only) -------------------------------------
if [[ "$MODE" == "full" ]]; then
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "error: full mode requires a git worktree" >&2
    exit 2
  fi
  local_allow="$TARGET/scripts/allowlist.txt"   # unused: allowlist is repo-relative
  git ls-files | sort > /tmp/rce-tracked.txt
  sort "$TARGET/scripts/allowlist.txt" > /tmp/rce-allow.txt
  if ! comm -23 /tmp/rce-tracked.txt /tmp/rce-allow.txt > /tmp/rce-t-not-a.txt; then :; fi
  if [[ -s /tmp/rce-t-not-a.txt ]]; then
    echo "FINDING: tracked but NOT in allowlist:" >&2
    cat /tmp/rce-t-not-a.txt >&2
    failed=1
  fi
  if ! comm -13 /tmp/rce-tracked.txt /tmp/rce-allow.txt > /tmp/rce-a-not-t.txt; then :; fi
  if [[ -s /tmp/rce-a-not-t.txt ]]; then
    echo "FINDING: in allowlist but NOT tracked (stale entry):" >&2
    cat /tmp/rce-a-not-t.txt >&2
    failed=1
  fi
fi

# ---- pattern scan engine ----------------------------------------------------
declare -a P
P=(
  # G1 — token shapes
  'sk-[A-Za-z0-9_-]{20,}'
  'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}'
  'AIza[0-9A-Za-z_-]{20,}|AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'glpat-[A-Za-z0-9_-]{20,}'
  '-----BEGIN (RSA |OPENSSH |EC |DSA |ENCRYPTED )?PRIVATE KEY-----'
  'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}'
  "(api[_-]?key|token|secret|password|bearer)[[:space:]]*[:=][[:space:]]*[\"'][^\"']{12,}[\"']"
  # G4 — absolute machine paths and identities (/workspace is a legal
  # container path in the contracts, so it is deliberately not matched)
  '(^|[[:space:]"])/(home|Users|root|mnt|opt|data)/[A-Za-z0-9_./-]+'
  'jianbiao|guanghao|betterrrrr'
  # G5 — names (word-bounded)
  '\b(babylm|BabyLM|mountaincar|MountainCar|topic2|Topic2|gave2|GAVE2|Task2)\b'
  '\b(AI-?Researcher|AI-?Scientist|AutoResearchClaw|DeepScientist|dr-?claw|EvoScientist)\b'
  '(^|[^A-Za-z0-9])aris($|[^A-Za-z0-9])'
  '\b(HKUDS|SakanaAI|aiming-lab|wanshuiyin)\b'
  # G5 — organizer-internal model lineage (gpt-5/6 · deepseek · kimi · luna);
  # generic public product names (claude, codex, llama, qwen, ...) are NOT
  # banned — they legitimately appear in tool dirs and participant docs.
  '\b(gpt-?5|gpt-?6|kimi|luna)\b'
  '\b(fullpipe|intake_0102|judge_0102|admission_probe|candidate-run)\b'
  # domains / endpoints
  '\bparatera\b|\bbianxie\b|\bmoonshot\b|\bhost\.docker\.internal\b|\bresearchclaweval\.dev\b'
  # internal result/run vocabulary
  '\b(140 ?格|140 ?cell|1574|1680|1542)\b'
)
# Patterns that legitimately appear only in the docs they describe:
declare -a P_DOC_EXEMPT
P_DOC_EXEMPT=()
# 'codex' appears only inside docs/rules.md §8 (the forbidden-entrypoint token
# rule text). Scan for it everywhere else.
COOEX_TARGET=docs/rules.md
CODEX_EXEMPT=("docs/rules.md")

scan_text() {
  local pattern="$1"; shift
  local found=0
  local f rel
  while IFS= read -r f; do
    [[ -n "$f" ]] || continue
    rel="${f#$TARGET/}"; [[ "$MODE" == "path" ]] && rel="$f"
    if is_exempt "$rel"; then continue; fi
    if grep -qP "$pattern" "$f" 2>/dev/null; then
      echo "  $rel" >&2
      found=1
    fi
  done
  if [[ "$found" == "1" ]]; then
    echo "FINDING: pattern /$pattern/" >&2
    failed=1
  fi
}

pipeline_files() { list_files; }

for p in "${P[@]}"; do
  scan_text "$p" < <(pipeline_files)
done

# codex — everywhere except the rules document that must quote it, and
# .gitignore where '.codex/' is a legitimate local-tool dir rule
for f in $(list_files); do
  [[ -n "$f" ]] || continue
  rel="${f#$TARGET/}"
  if is_exempt "$rel"; then continue; fi
  case "$rel" in docs/rules.md|.gitignore) continue ;; esac
  if grep -q 'codex' "$f" 2>/dev/null; then echo "  $rel"; fi
done | tee /tmp/rce-codex-hits.txt
if [[ -s /tmp/rce-codex-hits.txt ]]; then
  echo "FINDING: 'codex' outside docs/rules.md and .gitignore:" >&2
  cat /tmp/rce-codex-hits.txt >&2
  failed=1
fi

# deepseek — allowed ONLY in docs/rules.md (the published self-test model
# recommendation in §4); rejected everywhere else
found_ds=$(list_files | while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  rel="${f#$TARGET/}"
  if is_exempt "$rel"; then continue; fi
  case "$rel" in docs/rules.md) continue ;; esac
  if grep -qi 'deepseek' "$f" 2>/dev/null; then echo "  $rel"; fi
done)
if [[ -n "$found_ds" ]]; then
  echo "FINDING: 'deepseek' outside docs/rules.md:" >&2
  echo "$found_ds" >&2
  failed=1
fi

# forbidden hosts (case-insensitive substring, from the shared list)
if [[ -f "$TARGET/scripts/forbidden-hosts.txt" ]]; then
  while IFS= read -r host; do
    [[ -n "$host" ]] || continue
    hits=$(list_files | while IFS= read -r f; do
      [[ -n "$f" ]] || continue
      rel="${f#$TARGET/}"
      if is_exempt "$rel"; then continue; fi
      if grep -qi "$host" "$f" 2>/dev/null; then echo "  $rel"; fi
    done)
    if [[ -n "$hits" ]]; then
      echo "FINDING: forbidden host marker '$host':" >&2
      echo "$hits" >&2
      failed=1
    fi
  done < "$TARGET/scripts/forbidden-hosts.txt"
fi

# judge/ directory — the judge pipeline must not name any provider API var
if [[ -d "$TARGET/judge" ]]; then
  jhits=$(find "$TARGET/judge" -name '*.py' -type f 2>/dev/null | while IFS= read -r f; do
    [[ -n "$f" ]] || continue
    if grep -qE 'OPENAI_API_KEY|OPENAI_MODEL|OPENAI_BASE_URL|ANTHROPIC_API_KEY|ANTHROPIC_MODEL' "$f" 2>/dev/null; then echo "  $f"; fi
  done)
  if [[ -n "$jhits" ]]; then
    echo "FINDING: judge/ must use JUDGE_* env naming only:" >&2
    echo "$jhits" >&2
    failed=1
  fi
fi

# ---- file-name checks (results artifacts must not be tracked) ---------------
name_hits=$(list_files | grep -E '(^|/)(score|results)\.json$|run[-_][0-9]|tracked_run|score_exclusions' || true)
if [[ -n "$name_hits" ]]; then
  echo "FINDING: result/run artifacts tracked in the tree:" >&2
  echo "$name_hits" >&2
  failed=1
fi

# ---- size / symlink checks --------------------------------------------------
big=$(list_files | while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  if [[ -f "$f" ]] && (( $(stat -c%s "$f") > 5242880 )); then echo "  $f"; fi
done)
if [[ -n "$big" ]]; then
  echo "FINDING: tracked file exceeds 5 MiB:" >&2
  echo "$big" >&2
  failed=1
fi

syms=$(list_files | while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  if [[ -L "$f" ]]; then echo "  $f"; fi
done)
if [[ -n "$syms" ]]; then
  echo "FINDING: tracked symlinks must not be published:" >&2
  echo "$syms" >&2
  failed=1
fi

if [[ "$failed" == "0" ]]; then
  echo "check-release.sh: PASS"
  exit 0
fi
echo "check-release.sh: FAIL" >&2
exit 1