# Security Policy

## Reporting a vulnerability

This repository is a public evaluation-protocol artifact. Reports that matter
to us:

- A committed secret (token, key, credential) anywhere in the tree.
- Code in `scoring/` or `judge/` that would let a submitted artifact read
  hidden test labels or another participant's data.
- A bypass of the fail-closed behavior in the official-scorer glue.

To report:

1. Open a private vulnerability advisory
   (GitHub: Security → Report a vulnerability) — preferred.
2. If the issue is a leaked credential, also contact the maintainer directly
   *before* opening anything public: rotating the secret comes first.

## Design posture

- No secrets live in the source; the judge reads `JUDGE_API_KEY` /
  `JUDGE_MODEL` / `JUDGE_BASE_URL` from the environment only.
- The release gate (`scripts/check-release.sh`) and gitleaks run on every
  change (`.github/workflows/release-gate.yml`) precisely so a credential
  cannot enter the public tree unnoticed.
- Dataset files, run artifacts, and result tables are never committed
  (see `.gitignore` and `scripts/check-release.sh` file-name checks).