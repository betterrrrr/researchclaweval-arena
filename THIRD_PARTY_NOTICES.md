# Third-Party Notices

This repository redistributes **no code from third parties as vendored
sources** — scorer glue is written here and calls officially installed
packages. The following are used or referenced; verify each license on its
own page before commercial distribution of anything you build.

## Datasets (referenced, not redistributed)

| Asset | Source | License |
|---|---|---|
| `admet_group.zip` (TDC-ADMET-Tox, V105) | Harvard Dataverse `doi:10.7910/DVN/21LKWG` | Dataverse terms |
| `PsyDefConv.json` (PsyDefDetect) | HuggingFace `AIMH/PsyDefConv` | `cc-by-nc-4.0` — the competition is run for **non-commercial** purposes |
| `arc-whestbench-public-2026` | HuggingFace `aicrowd/arc-whestbench-public-2026` | `cc-by-4.0` |

## Tooling (installed by the user, referenced by scripts)

| Tool | Purpose | Notes |
|---|---|---|
| `whestbench` | official ARC White-Box Estimation scorer + benchmark | installed per its own docs; this repo provides glue only |
| `datasets` / `huggingface-hub` | dataset download used by `setup_datasets.sh` for ARC | Apache-2.0 |
| numpy / pandas | scorer glue runtime | BSD / BSD-3-Clause |
| `gitleaks` | release-gate secret scan (CI only) | MIT — used as a pinned binary download, not an action |

## Released derivative notice

Portions of this repository derive from the Apache-2.0-licensed
`researchclaweval-public` project and are relicensed to MIT by the same
copyright holder; see `NOTICE.md`.