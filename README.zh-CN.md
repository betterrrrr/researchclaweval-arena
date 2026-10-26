# ResearchClawEval Arena

ResearchClawEval Arena 是面向科研 Agent 框架的公开竞赛，评估框架在统一条件下完成研究规划、代码实现、实验执行、结果分析与报告撰写的能力。参赛框架由主办方统一运行和评分。

**本仓库公开的三个任务仅用于开发与自测。正式测评采用其他任务，自测成绩不计入最终排名。**

报名开放，赛期一个月。

[English](README.md) · [比赛公告](docs/announcement.md) · [比赛规则](docs/rules.md)

## 参赛流程

参赛者需提交开源框架及其适配器（adapter）。适配器负责接收任务并启动框架，研究方法与实验方案由框架自主确定。

| 阶段 | 任务与要求 |
|---|---|
| 开发与自测 | 使用三个公开任务验证框架接入、实验流程、日志记录和输出格式；模型由参赛者提供，推荐使用 `deepseek-v4.1-flash`（非强制），可重复调试 |
| 正式测评 | 提交框架后，由主办方在其他任务上统一运行，提供模型并计算成绩 |

正式测评统一任务要求、数据划分、模型和运行预算。实验次数按“策略线”计数，具体见[比赛规则 §5.8](docs/rules.md#58-实验计数策略线)。

## 公开自测任务

仓库提供以下任务的说明、数据下载脚本和评分工具，供参赛者验证接入与运行流程。

| 自测任务 | 任务目标 | 评分指标 | 数据大小 |
|---|---|---|---|
| [TDC-ADMET-Tox](contracts/tdc_admet_tox_contract.md) | 根据分子结构预测三种毒性终点（AMES / hERG / DILI） | macro-AUROC ↑ | 1.4 MB |
| [PsyDefDetect](contracts/psydefdetect_contract.md) | 识别支持性对话中的心理防御机制 | macro-F1 ↑ | 5.4 MB |
| [ARC-WBE-2026](contracts/arc_wbe_2026_contract.md) | 根据 Transformer 权重矩阵估计各层激活 | 调整后的末层得分 ↓ | 907 MB |

数据从原始发布处下载，由脚本执行校验；本仓库不存储或重新分发数据集。数据可见性与本地自评方式见各任务说明。

## 快速开始

```bash
# 1. 下载并校验自测数据
bash scripts/setup_datasets.sh --dataset tdc_admet_tox
bash scripts/setup_datasets.sh --dataset psydefdetect
bash scripts/setup_datasets.sh --dataset arc_wbe_2026

# 2. 阅读 contracts/ 中的任务说明和 docs/rules.md

# 3. 复制适配器示例，配置框架启动方式
cp -r templates/example-adapter/ <your-framework>/

# 4. 按文档配置 runner，执行自测
export RUN_ROOT=/tmp/my-run
bash scripts/runner/<your-id>_<your-framework>_<topic>_fullrun.sh
```

完整流程见[中文快速上手](docs/participant_quickstart.zh-CN.md) / [English](docs/participant_quickstart.md)，常见问题见 [FAQ](docs/FAQ.zh-CN.md)。

## 提交与评分

提交内容包括开源框架仓库和运行产物。每次运行需保留研究计划、实验记录、最终报告、完整日志，以及任务要求的预测文件或程序。格式要求见[比赛规则 §5](docs/rules.md#5-提交物)。

最终排名依据主办方的正式测评结果，不接受参赛者自报分数。比赛设**总分冠军**，同时公布单项排名：

- 各正式任务的成绩按测评前公布并固定的参考值归一化至 0–100 分，再等权平均计算总分。
- 总分最高者获得总分冠军；总分相同时，单项第一数量较多者优先；仍相同则并列。
- 失败或缺少有效结果的任务对总分贡献为 0 分，仍计入平均分的任务总数。

具体公式与并列规则见[比赛规则 §6.3](docs/rules.md#63-排名)。提交窗口结束并完成正式评分后，结果发布至 `results/`。

## 仓库结构

```text
contracts/   自测任务说明、预算与输出要求
scoring/     评分工具与数据准备脚本
scripts/     数据下载、运行模板与发布检查
templates/   适配器与提交物示例
schemas/     适配器与运行记录的格式定义
docs/        比赛规则、公告、上手指南与 FAQ
results/     正式测评结果
judge/       赛后社区榜评审工具
```

赛后将继续维护社区榜，扩展实验过程与报告质量等评测维度。详见[指标说明](docs/metric-system.md)和[规则附录 A](docs/rules.md#附录-a长期社区榜12-维)。

代码采用 MIT 许可，文档采用 CC-BY-4.0。第三方内容见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
