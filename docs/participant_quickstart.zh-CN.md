# 参赛快速上手(中文)

> 本文是英文版 [`participant_quickstart.md`](participant_quickstart.md) 的配套翻译。若与中文规则(`docs/rules.md`)冲突,以规则为准;若规则与契约(`contracts/*.md`)冲突,以契约为准。

## 0. 你要做的事

1. 报名并拿到 framework id(两位数)。
2. 配好三个数据集(自己下载 + 自己校验 sha256)。
3. 读三份契约。
4. 只写一个 adapter:声明**怎么启动**你的框架。
5. 用官方 runner 模板跑通。
6. 提交:开源框架仓库 + 每个 topic 一份产物。

**规划、实验设计、执行、比较、选择、成稿全部由你的框架负责**——adapter 里不含任何评测逻辑。

---

## 1. 数据集

```bash
bash scripts/setup_datasets.sh --dataset tdc_admet_tox   # ~1.4 MB
bash scripts/setup_datasets.sh --dataset psydefdetect    # ~5.4 MB
bash scripts/setup_datasets.sh --dataset arc_wbe_2026    # ~907 MB
```

脚本从原始公开发布处下载,sha256 与冻结值不符的一律拒绝(见 `docs/rules.md` §3.2)。然后导出数据集根路径:

```bash
export TDC_ADMET_TOX_DATASET_ROOT=$PWD/data/tdc_admet_tox/public
export PSYDEFDETECT_DATASET_ROOT=$PWD/data/psydefdetect
export ARC_WBE_2026_DATASET_ROOT=$PWD/data/arc_white_box_estimation_2026
```

网络下 `huggingface.co` 不可达时,设 `HF_ENDPOINT=https://hf-mirror.com`(脚本只在直连失败后才回退到镜像)。

> ⚠️ `psydefdetect` 授权为 `cc-by-nc-4.0`。本竞赛按**非商业**用途举办;下载前请确认你的个人用途合规。

## 2. 契约

读这三份:

- `contracts/arc_wbe_2026_contract.md` —— 注意**可见验证集**(规则 §3.4):100 个 MLP 中有 10 个连真值一起给你,可用官方指标自评;其余 90 个是评分集,永远不会挂进你的容器。
- `contracts/psydefdetect_contract.md` —— 正类 1–8 上的 macro-F1;对话级切分已冻结(仓库根 `psydefdetect_split.canonical.json`;canonical sha256 在 `docs/rules.md` §3.3)。可以立即自评分:

  ```bash
  python3 scoring/run_psydefdetect_local_score.py \
    --dataset-root "$PSYDEFDETECT_DATASET_ROOT" \
    --predictions predictions.jsonl \
    --output-score score.json
  ```
- `contracts/tdc_admet_tox_contract.md` —— AMES / hERG / DILI 的 AUROC 取宏平均。写代码**之前**先读规则 §5.6 关于 `sample_id` 的要求(`hERG` endpoint 对应 `HERG_` 前缀)。每天自检一次:`bash scripts/selfcheck_tdc.sh`(先验 golden run,设了 `TDC_ADMET_TOX_DATASET_ROOT` 时再跑参照实现的返回环)。

三份契约共享同一骨架:

- 第一次实验**之前**写好并锁定 `research_idea.json`
- 跑 **2–4 次实质性不同**的实验——按**策略线**计数:一条线内的重试、仅换种子不算,一条线只有完成了一个完整实验才算确立(规则 §5.8)——然后立刻晋升选中结果(绝不开第 5 条)
- 每个实验都记进 `experiment_trace.json`

## 3. Adapter

复制骨架:

```bash
cp -r templates/example-adapter/ myframework/
```

manifest(`manifest.json`)声明:framework id、名称、上游仓库、许可、原生入口、必需环境变量、必需镜像、补丁。把每个 TODO 填了——本地对照 `schemas/adapter.schema.json` 校验:

```bash
python3 scripts/validate_schemas.py --manifest myframework/manifest.json
```

你的 fullrun wrapper 遵循 `scripts/runner/` 里的 runner 模板:只读挂载契约与数据集到全新 workspace、经环境变量注入模型 endpoint(`OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_MODEL`)、导出 `WORKSPACE`(新 workspace 路径)与 `DATASET_ROOT`、在 `input/prompt.txt` 合成任务输入(见 §4)、原生运行你的框架、收集产物。通过 `WORKSPACE` 环境变量定位你的 workspace——**永远不要硬编码路径**。

**模型策略(规则 §4):** 自测阶段用自己的模型——主办方不限制(推荐的自测模型在规则 §4 点名;也可以用自己的)。正式测评阶段主办方经同样三个环境变量注入模型;无论哪个阶段,代码里都不得硬编码 endpoint 或模型 id。

**原生执行标记。** 框架必须从**自己的执行内部**打印 `FRAMEWORK_NATIVE_LOG_MARKER`,越早越好。退出码 0 但 `logs/e2e.log` 里没有这个标记 → 判非原生,不计分。自测:`bash scripts/check_native_marker.sh logs/e2e.log`(也可传 run 根目录,或用第二个参数传自定义标记)。

## 4. prompt.txt

每个 topic 一份统一任务输入(契约 + 预算 + 任务摘要),名为 `prompt.txt`。runner 模板把它合成到新 workspace 的 `input/prompt.txt`:由契约、执行预算、以及你自测时设置的任务摘要(导出 `PROMPT_TASK_SUMMARY` 或在模板里填)或正式测评时主办方提供的任务摘要组成。**怎么把它翻译成自己框架能吃的形态,由你负责**——这正是 adapter 的含义。prompt **不得规定任何方法**——算法族、特征表示、架构、超参、实验顺序、选定方法全部由你的框架自己定。

提交物里的 `prompt.txt` 就是 runner 挂载的那份原件,`PROVENANCE.json` 的 `prompt_sha256` 对它计算——自测什么、就交什么。

## 5. 提交

每个 topic 一份产物:

```
<framework>-<topic>-<YYYYMMDDTHHMMSS>/
├── PROVENANCE.json          # framework_commit / model / dataset_sha256 / split_sha256
├── workspace/
│   ├── research_idea.json
│   ├── experiment_trace.json
│   ├── environment.json     # 运行环境——六个必填字段,见下
│   ├── final_report.md
│   └── <topic 载荷>          # predictions.csv | predictions.jsonl | estimator.py
├── logs/e2e.log             # 运行时的原始 stdout/stderr
├── prompt.txt               # 喂给框架的任务输入原文（runner 挂载于 workspace/input/prompt.txt，提交原件，§4）
└── source/                  # 可选:框架生成的研究代码
```

载荷格式(规则 §5.3):

| topic | 载荷 | 格式 |
|---|---|---|
| `tdc_admet_tox` | `predictions.csv` | `sample_id,endpoint,probability` |
| `psydefdetect` | `predictions.jsonl` | 每行一个 `{"id":…, "predicted_label":…}` |
| `arc_wbe_2026` | `estimator.py` | `predict(mlp)` 返回 `(32,256)` 数组 |

`environment.json` 记录运行环境——审计检查六个字段(`python_version`、`platform`、`device`、`seeds`、`packages`、`created_at`);trace 的 `reproduction` 块声明重跑选中实验的确切入口、命令与种子。从 `templates/submission/environment.json.template` 起步。

`dataset_sha256` 与 `split_sha256` 必须与公示值逐字节一致,不一致直接不受理、不评分。`logs/e2e.log` 是主记录——判官管线只认 `logs/e2e.log` → `logs/native.log` → `logs/native_stdout.log`,**不读根目录的 `run.log`**。

`PROVENANCE.json` 是自行填写的提交清单(当前没有任何代码校验它)——导出时把 `model` 填成该次运行**实际使用的模型 id**,永远不要留环境变量名。真正被机器核验的模型值是 `experiment_trace.json` 里的 `framework_internal_model`,正式测评时它必须与公示的官方模型一致(规则 §4)。

## 6. 常见失败模式

| 症状 | 可能原因 |
|---|---|
| 全零 / 常数分数 | 占位符或常数预测(规则 §8) |
| TDC 分数恰好为 0 | `sample_id` 自己拼的,没从 `test.csv` 逐字取(`hERG` vs `HERG`) |
| ARC 估计器被拒 | `predict()` 缺 `mlp` 参数、形状错、或含非有限值——官方适配器 fail-closed |
| trace 里没有 `b0`/`bT` | ARC:没有数字化 `framework_visible_validation` 自评记录(契约 §3.4) |
| 运行被判非原生 | `FRAMEWORK_NATIVE_LOG_MARKER` 缺失,或由 wrapper 代打而非框架自己打印 |
| 运行中网关抖动 | 墙钟预算照常走表(规则 §5.4);先跑小探针、checkpoint、断点续跑、客户端重试/退避 |
| 切分被拒 | 数据集被重新划分;用冻结的 canonical 切分(sha256 见规则 §3.3) |

## 7. 时间线

```
赛前        契约冻结 · 数据可下 · 评分器跑通 · 文档就绪
第 1 周      报名 + 环境接入
第 2–3 周    开发与自测
第 4 周      提交窗口 → 主办方评分 → 结果公布
```

有问题?开 issue,或先读 `docs/FAQ.zh-CN.md`。