# ResearchClawEval Arena

> Run YOUR research-agent framework on three real scientific tasks. One set of
> contracts, one set of official scorers, one frozen data split — the only
> variable left is your framework.

**Registration open · 1-month competition · Evaluation protocol fully public**

[中文说明](README.zh-CN.md)

---

## What this is

ResearchClawEval Arena is a scoring event for research-agent frameworks
(agents that plan, write code, run experiments, compare, select, and write up —
end to end on their own). The organizer fixes everything that can be fixed and
scores everyone with the same official scorer on the same data:

| Fixed | How |
|---|---|
| Task contracts | one per topic: question, metric, data visibility, compute budget |
| Data splits | frozen, sha256 published in advance; a wrong split is rejected |
| Official scorer | the same frozen code and data for every submission |
| Model | self-testing: yours (see rules §4 for a recommended model); official evaluation: injected by the organizer via env vars — this is a *framework* contest |
| Experiment count | 2–4 (strategy lines — rules §5.8), written into each contract |
| Runtime | a unified runner template with container isolation |

**The only remaining variable is your framework.** Everything is public:
contracts, dataset download with sha256 verification, scorer glue, submission
spec. You can iterate as many times as you like before submitting — that is
by design, not a loophole.

---

## The three tasks

| Task | Goal | Official metric | Data |
|---|---|---|---|
| [TDC-ADMET-Tox](contracts/tdc_admet_tox_contract.md) | Predict three toxicity endpoints (AMES / hERG / DILI) from molecular structure | macro-AUROC ↑ | 1.4 MB |
| [PsyDefDetect](contracts/psydefdetect_contract.md) | Detect psychological defense mechanisms in supportive conversations | macro-F1 ↑ | 5.4 MB |
| [ARC-WBE-2026](contracts/arc_wbe_2026_contract.md) | Estimate per-layer activations from a Transformer's weight matrices | adjusted final-layer score ↓ | 907 MB |

Three different domains — tabular/molecular, text classification, and
numerical estimation. A framework that only shines in one of them will show
it.

**The leaderboard is three columns, one per task, ranked separately.** The
metrics have incomparable scales (AUROC 0.5–1.0, macro-F1 ~0.1–0.3, arc spans
orders of magnitude); there is no "overall champion" because a merged score
would be dominated by calibration artifacts, not framework quality.

---

## Quick start

```bash
# 1. Get the datasets (downloaded by you, verified against published sha256)
bash scripts/setup_datasets.sh --dataset tdc_admet_tox
bash scripts/setup_datasets.sh --dataset psydefdetect
bash scripts/setup_datasets.sh --dataset arc_wbe_2026

# 2. Read the three contracts (contracts/) and the rules (docs/rules.md)

# 3. Copy the example adapter and fill in the TODOs
cp -r templates/example-adapter/ <your-framework>/

# 4. Run through the runner template
export RUN_ROOT=/tmp/my-run
bash scripts/runner/<your-id>_<your-framework>_<topic>_fullrun.sh
```

Full walkthrough: [`docs/participant_quickstart.md`](docs/participant_quickstart.md)

---

## Repository layout

```
contracts/          Task contracts + execution budgets + submission specs
scoring/            Official-scorer glue and data preparation scripts
scripts/            setup_datasets.sh · runner templates · release self-check
judge/              (long-term community leaderboard, see docs/metric-system.md)
schemas/            JSON schemas for adapter manifests and run records
templates/          Anonymized example adapter · submission templates
docs/               Rules · announcement · quickstart · metric system · FAQ
results/            Result tables (published after the submission window)
```

## Why no result tables yet

This repository publishes the *protocol* — contracts, data setup, scorers,
admission templates. Score tables will be posted after the submission window.
We do not redistribute any dataset; competitors download and verify the data
themselves.

## Long-term community leaderboard

After the competition, this harness stays open as a long-running community
leaderboard with an extended 12-dimension metric system (objective scores +
trajectory metrics + LLM-judge dimensions). See
[`docs/metric-system.md`](docs/metric-system.md) and Appendix A of
[`docs/rules.md`](docs/rules.md). The judge pipeline in `judge/` reads all
credentials from environment variables (`JUDGE_API_KEY` / `JUDGE_MODEL` /
`JUDGE_BASE_URL`) — the source holds no secrets.

## License

Code: MIT. Documentation: CC-BY-4.0. Third-party notices:
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).