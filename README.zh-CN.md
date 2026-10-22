# ResearchClawEval Arena

> **用你自己的 research-agent 框架，在 3 个真实科研任务上跑出结果，由主办方统一评分。**

报名开放 · 赛期一个月 · 评测口径完全公开

[English](README.md) · [比赛公告](docs/announcement.md) · [比赛规则](docs/rules.md)

---

## 这是什么

面向科研 Agent 框架（从选题、写代码、做实验、比较选择到成稿的端到端 agent）的评分赛事。主办方固定一切可固定的评测变量，用同一份官方评分器在同一份数据上给所有人打分：

| 固定项 | 做法 |
|---|---|
| 任务契约 | 每 topic 一份：题目、指标、数据可见性、算力预算 |
| 数据切分 | 冻结并公示 sha256，用了别的切分即不受理 |
| 官方评分器 | 同一份冻结代码+同一份数据 |
| 模型 | 自测阶段自带（推荐模型见规则 §4）；正式测评由主办方经环境变量统一注入——这是**框架**竞赛，不是模型竞赛 |
| 实验次数 | 2–4 次（按策略线计，规则 §5.8），写进契约 |
| 运行环境 | 统一 runner 模板 + 容器隔离 |

**唯一变量是你的框架。** 契约、数据下载（带 sha256 校验）、评分器胶水、提交规范全部公开；提交前可以无限次调试——这是设计，不是漏洞。

## 三个任务

| 任务 | 目标 | 官方指标 | 数据 |
|---|---|---|---|
| [**TDC-ADMET-Tox**](contracts/tdc_admet_tox_contract.md) | 从分子结构预测三种毒性终点（AMES/hERG/DILI） | macro-AUROC ↑ | 1.4 MB |
| [**PsyDefDetect**](contracts/psydefdetect_contract.md) | 从支持性对话识别心理防御机制 | macro-F1 ↑ | 5.4 MB |
| [**ARC-WBE-2026**](contracts/arc_wbe_2026_contract.md) | 从 Transformer 权重矩阵估计逐层激活 | 调整后分层得分 ↓ | 907 MB |

主榜三列、逐任务排名，**不设总分冠军**（三个指标量纲不可并，合并得分会被校准伪影主导）。

## 快速开始

```bash
# 1. 自己下载数据（对照公示 sha256 校验）
bash scripts/setup_datasets.sh --dataset tdc_admet_tox
bash scripts/setup_datasets.sh --dataset psydefdetect
bash scripts/setup_datasets.sh --dataset arc_wbe_2026

# 2. 读契约（contracts/）与规则（docs/rules.md）

# 3. 复制示例适配器骨架，填 TODO
cp -r templates/example-adapter/ <your-framework>/

# 4. 用 runner 模板跑通
export RUN_ROOT=/tmp/my-run
bash scripts/runner/<your-id>_<your-framework>_<topic>_fullrun.sh
```

完整流程见[快速上手·中文版](docs/participant_quickstart.zh-CN.md) / [英文版](docs/participant_quickstart.md);常见问题见 [FAQ·中文版](docs/FAQ.zh-CN.md) / [英文版](docs/FAQ.md)。

## 结构

```
contracts/   三 topic 契约 + 预算 + 提交规范
scoring/     官方评分器胶水与数据准备脚本
scripts/     数据下载 · runner 模板 · 发布自检
judge/       长期社区榜判官管线（凭据全环境变量）
schemas/     适配器 manifest 与 run 记录的 JSON Schema
templates/   匿名示例适配器 · 提交物模板
docs/        规则 · 公告 · 快速上手 · 指标口径 · FAQ
results/     分数表（提交窗口结束后发布）
```

## 为什么现在没有分数表

本仓发布的是**协议**——契约、数据获取、评分器、准入模板。分数表在提交窗口结束后公示。主办方不重新分发任何数据集。

## 赛后

比赛结束后 harness 继续开放为**长期社区榜**（客观分 + 轨迹指标 + 判官维度的 12 维扩展评测），见 `docs/metric-system.md` 与规则附录 A。判官管线只从环境变量读凭据（`JUDGE_API_KEY`/`JUDGE_MODEL`/`JUDGE_BASE_URL`），源码不含任何密钥。

## 许可

代码 MIT；文档 CC-BY-4.0；第三方致谢见 `THIRD_PARTY_NOTICES.md`。