# ResearchClawEval Arena

Submit your research-agent framework for the organizer to run and score.
The framework should plan the research, write code, run and compare experiments,
and produce a final report.

**The three topics in this repository are for participant self-testing.
Final scoring will use other topics. Self-test scores do not count toward
final rankings.**

Registration open · 1-month competition

[中文说明](README.zh-CN.md) · [比赛公告](docs/announcement.md) · [Rules](docs/rules.md)

---

## What this is

ResearchClawEval Arena is a competition for research-agent frameworks.
Use the public self-test topics to develop your adapter and check the full
workflow. After submission, the organizer runs your framework on other topics
and calculates the final scores. All participants in official evaluation use
the same task requirements, model, data splits, and budgets:

| Fixed | How |
|---|---|
| Task contracts | one per topic: question, metric, data visibility, compute budget |
| Data splits | frozen, sha256 published in advance; a wrong split is rejected |
| Official scorer | the same frozen code and data for every submission |
| Model | Self-testing: participant-provided; `deepseek-v4.1-flash` is recommended, not required. Official evaluation: supplied by the organizer via environment variables (rules §4). |
| Experiment count | 2–4 (strategy lines — rules §5.8), written into each contract |
| Runtime | a unified runner template with container isolation |

The self-test contracts, dataset download scripts, scoring tools, and
submission formats are public. You can repeat self-tests as often as needed
before submitting. Official evaluation uses other topics.

---

## Three self-test tasks

These topics help you test your integration. They are not the topics used
for final scoring.

| Task | Goal | Official metric | Data |
|---|---|---|---|
| [TDC-ADMET-Tox](contracts/tdc_admet_tox_contract.md) | Predict three toxicity endpoints (AMES / hERG / DILI) from molecular structure | macro-AUROC ↑ | 1.4 MB |
| [PsyDefDetect](contracts/psydefdetect_contract.md) | Detect psychological defense mechanisms in supportive conversations | macro-F1 ↑ | 5.4 MB |
| [ARC-WBE-2026](contracts/arc_wbe_2026_contract.md) | Estimate per-layer activations from a Transformer's weight matrices | adjusted final-layer score ↓ | 907 MB |

Final rankings use the organizer's scores on other topics. The competition
awards an **overall champion** and also publishes per-topic rankings:

- Normalize each official topic score to 0–100 using reference values fixed
  and published before official evaluation, then take the equal-weight mean.
- The highest total wins. Tied totals are resolved by the number of topic
  first places; if that also ties, the overall rank is shared.
- Failed or missing valid results contribute 0 and remain in the fixed topic
  count. Reference values do not depend on competitors' scores.

See [rules §6.3](docs/rules.md#63-排名) for the formula and tie rules.

---

## Quick start

```bash
# 1. Get the self-test datasets (verified against published sha256)
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
contracts/          Self-test task contracts + execution budgets + submission specs
scoring/            Official-scorer glue and data preparation scripts
scripts/            setup_datasets.sh · runner templates · release self-check
judge/              (long-term community leaderboard, see docs/metric-system.md)
schemas/            JSON schemas for adapter manifests and run records
templates/          Anonymized example adapter · submission templates
docs/               Rules · announcement · quickstart · metric system · FAQ
results/            Result tables (published after the submission window)
```

## Why no result tables yet

This repository provides materials for self-testing and integration.
Final score tables will be posted after the submission window and official
evaluation on other topics.
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