# NOTICE

## Derived content

Portions of this repository (task contracts, scorer glue, schemas, and
templates) are derived from the `researchclaweval-public` project, which is
licensed under the Apache License 2.0. Both projects are authored by the same
single copyright holder, who relicenses those portions under the MIT License
(see `LICENSE`) for this repository.

## Documentation license

Documentation in `docs/`, the READMEs, and the contracts are licensed under
the Creative Commons Attribution 4.0 International (CC-BY-4.0). You are free
to share and adapt them with attribution.

## Secrets policy

- The LLM-judge pipeline (`judge/`) reads all credentials exclusively from
  environment variables (`JUDGE_API_KEY` / `JUDGE_MODEL` / `JUDGE_BASE_URL`).
  The source contains no secrets and no default credential values, and the
  release gate (`scripts/check-release.sh`) scans for credential patterns on
  every change.
- The competition model endpoint is injected at run time via
  `OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_MODEL`; no real values are
  stored anywhere in this repository.

## Data

This repository does not redistribute any dataset. Competitors download and
verify the public datasets themselves (`scripts/setup_datasets.sh`); see
`docs/rules.md` §3 for licenses and sha256 values. Third-party data and
tooling notices: `THIRD_PARTY_NOTICES.md`.