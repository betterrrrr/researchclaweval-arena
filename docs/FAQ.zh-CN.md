# FAQ(中文)

> 本文是英文版 [`FAQ.md`](FAQ.md) 的配套翻译。若与中文规则(`docs/rules.md`)冲突,以规则为准;英文版与中文版同为正式口径。

## 比赛

**问:任务是隐藏的吗?**

不是。三个任务全部是公开 benchmark,完全披露。提交前可以无限次迭代;没有隐藏集、没有秘密切分。这是刻意设计——见 `docs/rules.md` §0 与 §2。

**问:榜单是合并总分吗?**

不是。主榜三列、每任务各排各的。三个指标(0.5–1.0 的 AUROC、约 0.1–0.3 的 macro-F1、跨数量级的 arc 得分)无法合并——任何归一化相加都会被校准伪影主导,而不是被框架质量主导。见 `docs/rules.md` §6.3「排名」与 `docs/announcement.md` §6.3。

**问:模型由谁提供?**

分两阶段。**自测阶段**(提交前):用你自己的模型——主办方不限制(主办方推荐的自测模型在规则 §4 点名)。**正式测评**(提交后评分):主办方经 `OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_MODEL` 统一注入;该阶段自带模型或自带 endpoint 即不受理。这是**框架**竞赛,不是模型竞赛(规则 §4)。

**问:为什么榜上不用判官/LLM 评分?**

比赛榜只用客观官方分。七维 LLM 判官与 ED 属于长期社区榜:它们有噪声、有成本,而且在"提交产物"的交付模式下测的是证据质量而非执行本身(规则 §6.2 与附录 A)。

## 数据

**问:数据从哪来?**

自己下载、自己校验 sha256——`scripts/setup_datasets.sh`。主办方不重新分发数据集(规则 §3.2)。若 `huggingface.co` 不可达,设 `HF_ENDPOINT=https://hf-mirror.com`。

**问:PsyDefDetect 真的能用吗?**

能,授权为 `cc-by-nc-4.0`。本竞赛按**非商业用途**举办;下载前请确认你自己的用途合规。

**问:必须用哪个切分?**

冻结的 canonical 切分。`split_sha256` 必须逐字节匹配;任何重新划分都不受理。PsyDefDetect 的 canonical 切分是对话级、无泄漏的切分,与数据集自带的记录级官方切分不同(规则 §3.3)。

## 评分

**问:我的 TDC 分数恰好是 0。**

检查 `predictions.csv` 的 `sample_id` 是否逐字取自 `public/test.csv`——永远不要自己拼(`hERG` endpoint 对应 `HERG_` 前缀)。一个 id 对不上 → 全部匹配失败、分数为 0(规则 §5.6)。

**问:我的 ARC 估计器被拒了。**

官方适配器 fail-closed:`predict(self, mlp)` 必须返回真实的 `(32, 256)` 浮点数组。常量、广播、标量、全零、占位符或粘贴的日志输出都不受理(ARC 契约 "Required Outputs")。也检查签名——有些估计器省略 `budget` 参数;适配器会探测签名,两种都支持。

**问:为什么我的 ARC run 没有 `b0`/`bT`?**

ARC 是唯一不给框架真值的 topic。需要 `experiment_trace.json` 里有数字化的 `framework_visible_validation` 自评记录才能算(规则 §3.4);没有的话扩展维度退回到判官的序数路径。

**问:我的 run 退出码 0 却没分。**

多半是缺原生标记:`FRAMEWORK_NATIVE_LOG_MARKER` 必须由**框架自己的执行**打印进运行日志,且在运行**尽量靠前**的位置(规则 §5.5)。由 wrapper 代打会被判非原生。自测:`bash scripts/check_native_marker.sh logs/e2e.log`。

**问:2–4 次实验怎么计数?**

实验按**策略线**计:一套实质性不同的配置簇(在算法族 / 特征 / 架构 / 超参搜索空间整体设计上有别)。一条线内的重试、仅换种子、小调参不算;失败的 setup 尝试永远不算;已评估后崩溃或超时的配置按其所属策略线计为一个完整配置(规则 §5.8 与各契约的执行预算)。

**问:可以提交自算分数吗?**

不行。自报分数永不入榜——占位符分数、自实现指标、错误切分都是不受理事由(规则 §6.1、§8)。

## 工具

**问:有参赛用下载包吗?**

有——GitHub Releases 发布 `researchclaweval-arena-<version>.zip` / `.tar.gz`(打标树的精确副本,release 说明里有校验 sha256)。解压到任意位置,跑 `bash scripts/setup_datasets.sh`,按 `docs/participant_quickstart.md` 走。数据从不打包——自己下载、自己校验。

**问:runner 是什么?**

`scripts/runner/` 下的模板包装:只读挂载契约与数据集、注入模型环境、导出 `WORKSPACE` / `DATASET_ROOT`、在 `input/prompt.txt` 合成任务输入(契约 + 执行预算 + 任务摘要;规则 §5.7)、在新 workspace 里原生运行你的框架、收集 `logs/e2e.log` 与产物。必须用它而不是自己写临时编排,这样产物才可归因(规则 §5.4)。

**问:adapter 的 manifest 里填什么?**

`templates/example-adapter/manifest.json`——对照 `schemas/adapter.schema.json` 校验(framework id、名称、上游仓库、许可、原生入口、必需环境变量/镜像、补丁)。把每个 TODO 都填了,那就是全部接入面。本地自测:`python3 scripts/validate_schemas.py --manifest <你的 manifest.json>`。

**问:运行中网关抖动会怎样?**

契约里的墙钟预算照常走表——网关抖动**不是豁免理由**。自测建议:先用一个小实验验证链路,定期 checkpoint 并从断点续跑,重试/退避在你自己客户端侧配置(注入的 relay 没有官方旋钮;社区榜判官侧自带重试,规则 §5.4)。

**问:判官管线需要我的 key 吗?**

判官跑在主办方侧。代码从环境变量读 `JUDGE_API_KEY` / `JUDGE_MODEL` / `JUDGE_BASE_URL`;源码里没有密钥、没有默认模型 id。

**问:发现评分器胶水脚本的 bug?**

开 issue,附 topic、脚本名与最小复现。不要用邮件发原始数据集或任何密钥给任何人。