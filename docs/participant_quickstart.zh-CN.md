# 参赛快速上手

[English](participant_quickstart.md)。本指南说明框架接入与自测流程。规则以 `docs/rules.md` 为准；逐任务要求以 `contracts/*.md` 为准。

三个公开任务仅供开发与自测。正式测评采用其他任务，由主办方统一运行和评分；自测成绩不计入最终排名。

## 0. 流程概览

1. 报名并获取两位数框架 ID。
2. 下载三个自测数据集并校验 SHA-256。
3. 阅读对应任务契约。
4. 配置声明框架启动方式的适配器。
5. 使用官方 runner 模板完成自测。
6. 按规则提交开源框架仓库与运行产物，供主办方正式测评。

研究规划、实验设计、执行、结果比较、方案选择和报告撰写均由框架完成。适配器负责接入与启动，不预先指定研究方法。

## 1. 数据集

```bash
bash scripts/setup_datasets.sh --dataset tdc_admet_tox   # ~1.4 MB
bash scripts/setup_datasets.sh --dataset psydefdetect    # ~5.4 MB
bash scripts/setup_datasets.sh --dataset arc_wbe_2026    # ~907 MB
```

脚本从原始发布处下载并核对固定的 SHA-256，不匹配的数据不予接受。随后配置数据集路径：

```bash
export TDC_ADMET_TOX_DATASET_ROOT=$PWD/data/tdc_admet_tox/public
export PSYDEFDETECT_DATASET_ROOT=$PWD/data/psydefdetect
export ARC_WBE_2026_DATASET_ROOT=$PWD/data/arc_white_box_estimation_2026
```

若无法直接访问 `huggingface.co`，可设置 `HF_ENDPOINT=https://hf-mirror.com`。脚本仅在直连失败后启用镜像回退。

PsyDefDetect 数据采用 `cc-by-nc-4.0`。本竞赛按非商业用途举办，数据使用须符合该许可。

## 2. 任务契约

三个自测任务分别规定数据可见性、指标、实验预算与输出要求：

- `contracts/arc_wbe_2026_contract.md`：100 个 MLP 中的 10 个作为可见验证集并提供真值，其余 90 个用于主办方评分，不挂载到框架容器。见规则 §3.4。
- `contracts/psydefdetect_contract.md`：指标为正类 1–8 的 macro-F1。使用仓库根目录的 `psydefdetect_split.canonical.json` 对话级切分，SHA-256 见规则 §3.3。本地自评命令如下：

  ```bash
  python3 scoring/run_psydefdetect_local_score.py \
    --dataset-root "$PSYDEFDETECT_DATASET_ROOT" \
    --predictions predictions.jsonl \
    --output-score score.json
  ```

- `contracts/tdc_admet_tox_contract.md`：AMES、hERG、DILI 的 AUROC 等权平均。`sample_id` 须直接取自数据文件，`hERG` 对应前缀 `HERG_`，详见规则 §5.6。可运行 `bash scripts/selfcheck_tdc.sh` 校验 golden run；配置 `TDC_ADMET_TOX_DATASET_ROOT` 后，还会执行参照实现的评分与验证。

本地自评文件仅用于调试，不作为正式评分文件提交。各任务共同要求：

- 首次实验前确定并锁定 `research_idea.json`。
- 完成 2–4 条具有实质性区别的策略线。同一策略线内的重试、仅换种子与小幅调参不增加计数；须完成至少一个完整实验方可计为一条。比较后提交选定结果，不得开展第 5 条。见规则 §5.8。
- 在 `experiment_trace.json` 中记录每次实验。

## 3. 适配器与运行器

复制适配器示例：

```bash
cp -r templates/example-adapter/ myframework/
```

`manifest.json` 声明框架 ID、名称、上游仓库、许可、原生入口、必需环境变量、镜像与补丁。完成占位内容后，对照 `schemas/adapter.schema.json` 校验：

```bash
python3 scripts/validate_schemas.py --manifest myframework/manifest.json
```

Fullrun wrapper 须遵循 `scripts/runner/` 中的模板。Runner 只读挂载契约与数据，通过 `OPENAI_BASE_URL`、`OPENAI_API_KEY`、`OPENAI_MODEL` 注入模型配置，导出 `WORKSPACE` 与 `DATASET_ROOT`，生成 `input/prompt.txt`，在独立工作目录中启动框架并收集产物。工作路径须从 `WORKSPACE` 读取，不得硬编码。

自测阶段由参赛者提供模型，正式测评由主办方通过相同环境变量配置。两阶段均不得在代码中硬编码模型 ID 或 endpoint。推荐自测模型见规则 §4。

`FRAMEWORK_NATIVE_LOG_MARKER` 须由框架自身在运行早期输出。退出码为 0 但 `logs/e2e.log` 缺少标记时，仍判为非原生执行。检查命令：`bash scripts/check_native_marker.sh logs/e2e.log`；也可传入运行根目录，并通过第二个参数指定自定义标记。

## 4. 任务输入

Runner 根据契约、执行预算与任务摘要生成 `prompt.txt`，挂载至工作目录的 `input/prompt.txt`。自测时通过 `PROMPT_TASK_SUMMARY` 或模板提供摘要；正式测评时由主办方提供。

适配器负责将输入转换为框架支持的形式。输入不得预设算法族、特征表示、模型架构、超参数、实验顺序或最终方法。

提交的 `prompt.txt` 须为挂载原件，`PROVENANCE.json` 中的 `prompt_sha256` 按该原件计算。

## 5. 提交与运行记录

每个任务保留一份运行产物，任务特有载荷以对应契约为准：

```
<framework>-<topic>-<YYYYMMDDTHHMMSS>/
├── PROVENANCE.json          # framework_commit / model / dataset_sha256 / split_sha256
├── workspace/
│   ├── research_idea.json
│   ├── experiment_trace.json
│   ├── environment.json     # 运行环境，六个必需字段，见下文
│   ├── final_report.md
│   └── <topic 载荷>          # predictions.csv | predictions.jsonl | estimator.py
├── logs/e2e.log             # 运行时的原始 stdout/stderr
├── prompt.txt               # 任务输入原文，runner 挂载于 workspace/input/prompt.txt（§4）
└── source/                  # 可选:框架生成的研究代码
```

三个公开自测任务的载荷格式如下：

| 任务 | 载荷 | 格式 |
|---|---|---|
| `tdc_admet_tox` | `predictions.csv` | `sample_id,endpoint,probability` |
| `psydefdetect` | `predictions.jsonl` | 每行 `{"id":…, "predicted_label":…}` |
| `arc_wbe_2026` | `estimator.py` | `predict(mlp)` 返回 `(32,256)` 数组 |

`environment.json` 包含 `python_version`、`platform`、`device`、`seeds`、`packages`、`created_at` 六个必需字段。Trace 的 `reproduction` 块声明复现选定实验的入口、命令和种子；环境记录示例见 `templates/submission/environment.json.template`。

`dataset_sha256` 与 `split_sha256` 须与公布值一致。日志保存为 `logs/e2e.log`；社区榜评审依次查找 `logs/e2e.log`、`logs/native.log`、`logs/native_stdout.log`，不读取根目录 `run.log`。

`PROVENANCE.json` 记录提交与运行信息，可用 `python3 scripts/validate_schemas.py --provenance <provenance-path>` 校验格式。`model` 须填写实际使用的模型 ID，不能填写环境变量名称。格式校验不证明内容真实性；正式模型还须与 `experiment_trace.json` 中的 `framework_internal_model` 及主办方配置一致。

## 6. 常见验证问题

| 问题 | 检查项 |
|---|---|
| 占位符或常量结果被拒 | 是否生成真实预测与实验产物；有效的原始低分不等同于占位结果 |
| TDC 样本标识不匹配 | `sample_id` 是否直接取自 `test.csv`，是否保留 `hERG` 与 `HERG_` 的大小写区别 |
| ARC 估计器被拒 | `predict()` 是否接收 `mlp`，输出形状与数值是否符合契约 |
| ARC 缺少 `b0`、`bT` | 是否记录数值化的 `framework_visible_validation`；见规则 §3.4 |
| 运行被判非原生 | 标记是否存在，是否由框架自身输出 |
| 网络中断 | 墙钟预算不暂停；检查连接、检查点、恢复与客户端重试配置 |
| 切分校验失败 | 是否使用固定 canonical 切分，SHA-256 是否与规则 §3.3 一致 |

## 7. 时间安排

第 1 周报名与环境接入，第 2–3 周开发与自测，第 4 周提交。主办方完成正式测评后公布结果。赛前须完成契约、数据下载、评分工具和文档验证。

问题反馈通过 issue 提交，常见问题见 [FAQ](FAQ.zh-CN.md)。
