# ResearchClawEval Arena

这是一个科研 Agent 框架比赛。你提交自己的框架，由主办方统一运行和评分，看看它能否独立完成研究计划、写代码、做实验、比较结果和撰写报告。

**仓库里的三个 topic 是给参赛者自测用的。最终评分会使用其他 topic，自测成绩不计入最终排名。**

报名开放，赛期一个月。

[English](README.md) · [比赛公告](docs/announcement.md) · [比赛规则](docs/rules.md)

## 怎么参加

你需要提供一个开源框架，以及启动它的适配器（adapter）。适配器负责把任务交给框架，研究思路和实验过程由框架自己决定。

比赛分两步：

1. **开发与自测**：用下面三个公开任务检查框架能否接收任务、跑完实验、保存日志并输出规定格式的结果。可以反复调试，模型由你自己提供。
2. **正式测评**：提交框架后，主办方在其他 topic 上统一运行，提供模型，并按各任务的评分标准计算最终成绩。

正式测评时，各参赛框架使用相同的任务要求、数据划分、模型和运行预算。框架需要自行设计并比较实验方案，实验次数按规则中的“策略线”计数，具体见[比赛规则 §5.8](docs/rules.md#58-实验计数策略线)。

## 三个自测任务

这三个任务的说明、数据下载脚本和评分工具都在仓库里，用来熟悉接入和运行流程。它们不是最终评分的题目。

| 自测任务 | 要做什么 | 评分指标 | 数据大小 |
|---|---|---|---|
| [TDC-ADMET-Tox](contracts/tdc_admet_tox_contract.md) | 根据分子结构预测三种毒性（AMES / hERG / DILI） | macro-AUROC，越高越好 | 1.4 MB |
| [PsyDefDetect](contracts/psydefdetect_contract.md) | 识别支持性对话中的心理防御机制 | macro-F1，越高越好 | 5.4 MB |
| [ARC-WBE-2026](contracts/arc_wbe_2026_contract.md) | 根据 Transformer 的权重矩阵估计各层激活 | 调整后的末层得分，越低越好 | 907 MB |

数据从原始发布处下载，脚本会校验文件；仓库不存放数据集。各任务可见的数据和本地自评方式见对应任务说明。

## 开始自测

```bash
# 1. 下载自测数据并校验
bash scripts/setup_datasets.sh --dataset tdc_admet_tox
bash scripts/setup_datasets.sh --dataset psydefdetect
bash scripts/setup_datasets.sh --dataset arc_wbe_2026

# 2. 阅读 contracts/ 中的任务说明和 docs/rules.md

# 3. 复制适配器示例，填好框架的启动方式
cp -r templates/example-adapter/ <your-framework>/

# 4. 按文档配置 runner，运行一个自测任务
export RUN_ROOT=/tmp/my-run
bash scripts/runner/<your-id>_<your-framework>_<topic>_fullrun.sh
```

详细步骤：[中文快速上手](docs/participant_quickstart.zh-CN.md) / [English](docs/participant_quickstart.md)。遇到问题可以先看 [FAQ](docs/FAQ.zh-CN.md)。

## 提交与评分

提交内容包括开源框架仓库和运行产物。运行产物需要保留研究计划、实验记录、最终报告、完整日志，以及任务要求的预测文件或程序，格式见[比赛规则 §5](docs/rules.md#5-提交物)。

最终排名以主办方在其他 topic 上的正式测评结果为准，不接受参赛者自报分数。比赛设**总分冠军**，也保留各 topic 的单项排名：

- 每个正式 topic 的成绩先换算成 0–100 分，再等权平均，得到总分。
- 总分最高者夺冠；总分相同时，单项第一数量更多者优先；仍相同则并列。
- 换算使用正式测评开始前公布并固定的参考值，不随参赛队伍的成绩变化。失败或缺少有效结果的任务计 0 分，仍计入平均分的任务总数。

具体公式和并列规则见[比赛规则 §6.3](docs/rules.md#63-排名)。

分数表会在提交窗口结束、正式评分完成后发布到 `results/`。

## 仓库里有什么

```text
contracts/   自测任务说明、预算和输出要求
scoring/     评分工具和数据准备脚本
scripts/     数据下载、运行模板和发布检查
templates/   适配器和提交物示例
schemas/     适配器与运行记录的格式定义
docs/        比赛规则、公告、上手指南和 FAQ
results/     正式测评结果
judge/       赛后社区榜使用的评审工具
```

比赛结束后，项目会继续维护社区榜，加入实验过程和报告质量等评测。具体见[指标说明](docs/metric-system.md)和[规则附录 A](docs/rules.md#附录-a长期社区榜12-维)。

代码使用 MIT 许可，文档使用 CC-BY-4.0。第三方内容见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
