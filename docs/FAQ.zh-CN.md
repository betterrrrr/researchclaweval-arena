# 常见问题

[English](FAQ.md)。本页为参赛与自测说明，规则以 `docs/rules.md` 为准。

## 比赛

**公开的三个任务是否用于最终评分？**

三个公开任务仅供开发与自测，可重复运行和调试。正式测评采用其他任务，由主办方统一运行和评分；自测成绩不计入最终排名。见规则 §0、§2。

**总分与冠军如何确定？**

各正式任务按测评前固定的参考值归一化至 0–100 分，再等权平均。总分最高者获得总分冠军；总分相同时，单项第一数量较多者优先，仍相同则并列。单项排名同时公布。计算公式与精度见规则 §6.3。

**失败或缺少有效结果的任务如何处理？**

该任务对总分贡献为 0，仍计入固定任务总数。原始分记为 `null` 并保留状态，不得仅对成功任务计算平均分。至少有一个有效正式测评结果方可进入总榜；取消资格的框架不参与评奖。

**模型由谁提供？**

自测阶段由参赛者提供，推荐使用 `deepseek-v4.1-flash`，不作强制要求。正式测评由主办方通过 `OPENAI_BASE_URL`、`OPENAI_API_KEY`、`OPENAI_MODEL` 统一注入，不允许另行指定模型或 endpoint。两阶段均不得在代码中硬编码模型 ID 或地址。

**LLM 评审是否参与比赛排名？**

比赛仅依据正式任务的客观评分。七维 LLM 评审与 ED 属于社区榜，受调用成本、评分波动及证据来源限制，不参与比赛排名。见规则 §6.2 和附录 A。

## 数据

**如何获取数据？**

运行 `scripts/setup_datasets.sh` 从原始发布处下载并校验 SHA-256。主办方不重新分发数据。无法直接访问 `huggingface.co` 时，可设置 `HF_ENDPOINT=https://hf-mirror.com`。见规则 §3.2。

**PsyDefDetect 的许可要求是什么？**

数据采用 `cc-by-nc-4.0`。本竞赛按非商业用途举办，参赛者的数据使用须符合该许可。

**应使用哪份数据切分？**

使用固定的 canonical 切分，`split_sha256` 须与公布值完全一致。PsyDefDetect 使用对话级切分，与数据集自带的记录级切分不同。见规则 §3.3。

## 评分与验证

**TDC 预测因样本标识不匹配被拒绝，应如何处理？**

直接使用 `public/test.csv` 中的 `sample_id`，不得自行重建。`hERG` 对应 ID 前缀为 `HERG_`。预测记录的 ID 与 endpoint 集合必须与测试文件一致，否则校验或评分程序会拒绝该结果。此类错误不产生有效的原始 0 分。见规则 §5.6。

**ARC 估计器的输出要求是什么？**

`predict(mlp)` 须返回符合契约的 `(32, 256)` 数值数组。适配器支持带或不带 `budget` 参数的实现，并拒绝错误形状、非有限值、常量、全零、广播、标量及占位符结果。详见 ARC 契约的 Required Outputs。

**ARC 的 `b0`、`bT` 缺失时应检查哪些记录？**

检查 `experiment_trace.json` 中是否包含数值化的 `framework_visible_validation` 自评记录。ARC 为可见验证集提供真值，评分集真值仅供主办方使用。缺少数值记录时，无法据此计算 `b0`、`bT`，扩展评测使用评审工具的序数路径。见规则 §3.4。

**退出码为 0 是否代表运行有效？**

退出码不替代产物与原生执行校验。`FRAMEWORK_NATIVE_LOG_MARKER` 须由框架自身在运行早期输出至日志，外层 wrapper 不得代为输出。检查命令：`bash scripts/check_native_marker.sh logs/e2e.log`。见规则 §5.5。

**2–4 次实验如何计数？**

按策略线计数：算法族、特征表示、模型架构或超参数搜索空间的整体设定须存在实质性区别。同一策略线内的重试、仅换种子和小幅调参不增加计数；未完成训练或评估的配置尝试仅记入日志。已完成评估后崩溃或超时的配置仍归入所属策略线。见规则 §5.8。

**是否接受参赛者自行计算的成绩？**

自评分仅用于开发与调试，不作为入榜成绩。正式成绩由主办方按官方指标与固定切分计算。见规则 §6.1、§8。

## 工具与运行

**是否提供发布包？**

GitHub Releases 提供 `researchclaweval-arena-<version>.zip` 和 `.tar.gz`，内容对应发布标签，校验值见发布说明。解压后按 `docs/participant_quickstart.zh-CN.md` 配置环境。数据集不包含在发布包中，须通过下载脚本另行获取。

**Runner 的职责是什么？**

`scripts/runner/` 中的模板负责只读挂载契约和数据、注入模型环境变量、导出 `WORKSPACE` 与 `DATASET_ROOT`、生成 `input/prompt.txt`、在独立工作目录中启动框架，并收集 `logs/e2e.log` 和运行产物。运行须使用官方模板。见规则 §5.4、§5.7。

**适配器 manifest 需要哪些内容？**

`templates/example-adapter/manifest.json` 声明框架 ID、名称、上游仓库、许可、原生入口、必需环境变量、镜像和补丁。完成占位内容后，使用 `python3 scripts/validate_schemas.py --manifest <manifest-path>` 对照 `schemas/adapter.schema.json` 校验。

**`resource_budget` 应如何填写？**

使用契约规定的完整预算对象。TDC 的定义与示例见 `contracts/tdc_admet_tox_compute_budget.md`，机器可读值见 `scoring/resource_budget.anchors.json`；其中包括 `network_policy: "injected_llm_relay_only"`。校验要求完整匹配，不应从错误消息推断配置。

**网络中断是否暂停预算计时？**

不暂停任务契约规定的墙钟计时，也不补时。建议自测前验证连接，定期保存检查点，并在框架客户端配置重试、退避与恢复。注入的 relay 不提供统一重试配置，社区榜评审工具另有重试机制。见规则 §5.4。

**评审工具的凭据由谁配置？**

评审工具由主办方运行，通过 `JUDGE_API_KEY`、`JUDGE_MODEL`、`JUDGE_BASE_URL` 读取配置。源码不包含凭据或默认模型 ID。

**如何报告评分工具问题？**

提交 issue，注明任务、脚本名称和最小复现步骤。复现材料不得包含原始数据集或密钥。
