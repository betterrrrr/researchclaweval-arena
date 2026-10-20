# Contributing

Thanks for helping with ResearchClawEval Arena. The repository is small by
design: contracts, official-scorer glue, templates, and documentation.

## Ground rules

- **No sensitive content.** This repo is public and intentionally free of
  credentials, datasets, run artifacts, and results. If your change mentions
  a secret, a raw path, a private endpoint, or an undeclared dataset — fix
  it locally first.
- **Run the gate.** Every PR runs `.github/workflows/release-gate.yml`:
  `scripts/check-release.sh` (allowlist + pattern scan), gitleaks, and a
  smoke pass. If you added a file, add it to `scripts/allowlist.txt` in the
  same PR — the gate fails otherwise, by design.
- **Keep contracts authoritative.** Changes to `contracts/` or `docs/rules.md`
  affect every participant; they are the product, not the appendage.

## Style

- Shell: `bash -n` clean, `set -euo pipefail` where applicable, POSIX-sh
  friendly where easy.
- Python: `python3 -m py_compile` clean; no third-party runtime dependencies
  for the glue (scoring scripts may import numpy / pandas / whest when
  installed by the user, per `docs/scorer-contracts.md`).
- Docs: plain English or Chinese where the surrounding file uses it; no
  internal vocabulary from competitor-facing text (see `docs/FAQ.md`).

## Process

1. Open an issue for anything beyond a typo.
2. Branch, change, add `scripts/allowlist.txt` lines, run
   `bash scripts/check-release.sh` locally until PASS.
3. PR against `main`; the release gate runs automatically.

## Licensing

By contributing you agree your contribution is licensed under the repository
terms (code: MIT; docs: CC-BY-4.0 — see `LICENSE` and `NOTICE.md`).