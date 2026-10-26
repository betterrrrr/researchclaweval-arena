# ResearchClawEval 科研 Agent 框架竞赛

我们想比较的是：收到一个研究任务后，不同的科研 Agent 框架能不能自己做计划、写代码、跑实验、比较结果，最后交出报告。

你提交开源框架，主办方统一运行和评分。报名开放，赛期一个月。

**仓库公开的三个 topic 供参赛者自测。最终评分会使用其他 topic，自测成绩不计入最终排名。**

## 一、为什么办这个比赛

不同框架的演示通常使用不同任务、模型和运行预算，很难直接比较。这次比赛让参赛框架在相同的任务要求和运行条件下接受测评，研究方法和实验方案由框架自己决定。

## 二、自测和正式测评怎么分

| 阶段 | 任务 | 模型 | 用途 |
|---|---|---|---|
| 开发与自测 | 仓库里的三个公开 topic | 参赛者自己提供 | 检查接入、实验流程和输出格式，可以反复调试 |
| 正式测评 | 其他 topic | 主办方统一提供 | 主办方统一运行、评分，计算最终排名 |

正式测评时，各框架使用相同的任务要求、数据划分、模型和运行预算。具体要求见[比赛规则](rules.md)。

## 三、三个公开自测任务

| 自测任务 | 要做什么 | 指标 | 数据大小 |
|---|---|---|---|
| [TDC-ADMET-Tox](../contracts/tdc_admet_tox_contract.md) | 根据分子结构预测三种毒性（AMES / hERG / DILI） | macro-AUROC，越高越好 | 1.4 MB |
| [PsyDefDetect](../contracts/psydefdetect_contract.md) | 识别支持性对话中的心理防御机制 | macro-F1，越高越好 | 5.4 MB |
| [ARC-WBE-2026](../contracts/arc_wbe_2026_contract.md) | 根据 Transformer 权重矩阵估计各层激活 | 调整后的末层得分，越低越好 | 907 MB |

数据从原始发布处下载，脚本会校验文件，主办方不重新分发数据集。

```bash
bash scripts/setup_datasets.sh --dataset tdc_admet_tox
bash scripts/setup_datasets.sh --dataset psydefdetect
bash scripts/setup_datasets.sh --dataset arc_wbe_2026
```

各任务可见的数据和自评方式见对应任务说明。这些任务用来熟悉流程，不是最终评分题目。

## 四、参赛需要准备什么

提供开源框架，并从 `templates/example-adapter/` 复制适配器示例，配置框架入口、容器镜像和任务输入方式。适配器负责启动和传递任务；研究计划、实验设计、执行、比较和报告撰写都由框架完成。

按文档配置 runner 后运行自测：

```bash
export RUN_ROOT=/tmp/my-run
bash scripts/runner/<your-id>_<your-framework>_<topic>_fullrun.sh
```

完整步骤见[中文快速上手](participant_quickstart.zh-CN.md) / [English](participant_quickstart.md)。

## 五、提交什么

提交开源框架仓库与运行产物。每次运行需要保留：

```text
workspace/
  research_idea.json       第一次实验前确定的研究计划
  experiment_trace.json    实验配置、过程和结果
  environment.json         运行环境与复现信息
  final_report.md          最终报告
  <topic 载荷>             任务要求的预测文件或程序
logs/e2e.log               完整执行日志
prompt.txt                 任务输入原文
PROVENANCE.json            框架版本、模型和数据校验信息
```

具体字段和逐任务要求见[规则 §5](rules.md#5-提交物)。自测产物用于检查流程，最终成绩来自主办方在其他 topic 上的正式运行。

## 六、怎么评分

### 6.1 成绩来源

主办方按正式测评 topic 的评分标准计算客观分。不接受参赛者自报分数，三个公开自测任务的成绩不计入最终排名。赛后社区榜使用的 LLM 评审维度不进入比赛排名。

### 6.2 怎么排名

比赛设总分冠军，也公布各 topic 的单项排名。每个正式 topic 的原始成绩先按赛前固定的参考值换算成 0–100 分，再等权平均。总分最高者夺冠。失败或缺少有效结果的任务按 0 分计入，不能从平均分中去掉。具体公式见[规则 §6.3](rules.md#63-排名)。

### 6.3 并列怎么处理

总分统一四舍五入到小数点后六位后比较。总分相同时，单项第一数量更多者优先；数量仍相同则并列。单项第一依据有效原始成绩判定，单项并列第一时各计一个第一。

## 七、运行要求

提交后固定框架版本。正式测评的模型通过环境变量注入，代码不得写死模型或 API 地址。任务输入只描述问题和限制，不能替框架指定研究方法。

请使用官方 runner 保存完整日志。框架需要在自己的执行过程中打印原生执行标记；缺少标记、日志或规定产物的运行不予受理。详细要求见[比赛规则](rules.md)。

## 八、时间安排

赛期一个月：第 1 周报名并接入环境，第 2–3 周开发和自测，第 4 周提交，由主办方正式测评后公布结果。

比赛规则与具体时间以官方发布为准。
