# Stage 2 Issue Plan — M2: Simple CNN Baseline

> Milestone: M2 — Simple CNN Baseline  
> Goal: 基于标准 CNN 或预训练模型建立第一个可信 baseline。  
> Design reference: `docs/plan/minimal_system_design.md`

---

## Issue 2.1 — Freeze Baseline Configuration for the First Credible CNN Run

### Background
`docs/plan/minimal_system_design.md` 已经完成了最小系统的设计拍板：  
主线是“单图编码器预训练 + 双视图晚融合的 breast-level 二分类系统”，保底方案是“单图分类 + breast-level 聚合”。

但 M2 的目标不是一次性把所有设计都做满，而是先建立**第一个可信 baseline**。  
因此，在正式训练前，需要先冻结一版 baseline 配置，避免训练过程中不断改 backbone、输入尺寸、损失函数和聚合规则，导致结果不可比较。

### Suggested Branch
`feat/model`

### Goal
确定 M2 第一版 baseline 的正式配置，形成后续训练、评估和记录的一致标准。

### Scope
- 明确 M2 是先做保底单图 baseline，还是直接进入双视图 baseline
- 冻结 backbone、输入尺寸、损失函数、优化器、epoch 数等关键配置
- 冻结输出记录规范
- 明确本轮 baseline 的目标是“可信”而非“最优”

### Deliverables
- 一份 baseline config
- 一份简短的 baseline freeze note（可写入 docs 或 config 注释）

### Acceptance Criteria
- 至少有一套明确且可复现的 baseline 配置
- 关键训练参数不再散落在脚本里临时修改
- 后续 issue 可直接引用该配置开展实现与训练

---

## Issue 2.2 — Implement the First Single-image CNN Baseline

### Background
根据 `minimal_system_design.md`，单图分类 + breast-level 聚合是当前项目的**保底方案**，也是整个系统的安全网。  
因此，M2 的第一件正式 baseline 工作，应当是把这个保底方案做成一个完整、可信、可复现实验。

这一步的意义不是说单图一定是最终最佳路线，而是：

- 它实现最稳
- 它可以验证数据、预处理、训练框架和评估链路是否一致
- 它也可以为后续双视图主线提供编码器初始化或比较基线

### Suggested Branch
`feat/model`

### Goal
完成一个标准预训练 CNN 的单图 baseline，并能输出 breast-level 结果。

### Scope
- 选择一个简单且成熟的 backbone（如 ResNet18 / EfficientNet-B0 / EfficientNet-B2 中的一种）
- 接入 M1 的训练与评估骨架
- 完成单图训练
- 完成基于 `breast_id` 的聚合与验证
- 输出 baseline 指标

### Deliverables
- 单图 baseline 模型实现
- 对应训练配置
- 一轮正式 baseline 结果

### Acceptance Criteria
- baseline 能在正式 fold 设置下训练和验证
- 能输出 OOF 或至少 fold-level breast-level AUROC
- 结果记录完整，可复查
- 可作为后续所有增强实验的比较基线

---

## Issue 2.3 — Add Checkpointing, Logging, and Result Artifact Saving

### Background
M2 已经不是“只求跑通”的阶段，而是“建立第一个可信 baseline”的阶段。  
因此，训练产物必须具备最基本的实验管理能力：

- 模型 checkpoint
- 配置留档
- 日志记录
- 验证结果保存
- 关键图表或 summary 输出

否则即使跑出了一个不错的结果，也很难复现、比较和复盘。

### Suggested Branch
`feat/train`

### Goal
为 baseline 训练补齐最小但规范的实验产物管理能力。

### Scope
- 保存 best / last checkpoint
- 保存训练配置副本
- 保存训练日志
- 保存验证预测结果
- 保存关键指标 summary

### Deliverables
- checkpoint 保存逻辑
- 日志与结果目录规范
- baseline 结果产物样例

### Acceptance Criteria
- 一次 baseline 运行结束后，关键产物可完整留存
- 能清楚知道某个结果对应哪组配置
- 后续可以基于这些产物做结果对比和复盘

---

## Issue 2.4 — Run the First Formal Baseline Experiment

### Background
M2 的核心不是“有 baseline 代码”，而是“真的产出第一个可信 baseline 结果”。  
因此，需要有一个独立 issue 专门承担正式运行，而不是把“训练脚本存在”误当成 baseline 已完成。

### Suggested Branch
`feat/scripts`

### Goal
使用冻结配置完成第一轮正式 baseline 实验，并产出可比较的主指标结果。

### Scope
- 按既定配置运行 baseline
- 至少完成一个正式 fold，理想情况下完成完整 CV
- 输出主指标 AUROC
- 记录训练资源、时间和基础观察

### Deliverables
- baseline run 记录
- 指标结果
- 预测文件与必要日志

### Acceptance Criteria
- 至少有一轮正式 baseline 结果，不再只是 smoke test
- 主指标为 breast-level AUROC
- 运行过程和产物可复查
- 可明确判断该 baseline 是否具备继续优化的价值

---

## Issue 2.5 — Analyze Baseline Quality and Decide Whether to Move Forward

### Background
M2 milestone 的最后一项明确写着：  
“分析 baseline 是否具备继续优化的价值。”

这说明 Stage 2 的终点不只是“跑一个数”，而是要进行一次**最小研究判断**：

- baseline 有没有明显工程问题
- baseline 的结果是否可信
- 当前路线是否值得继续
- 下一阶段应优先优化什么

这个判断对于整个项目节奏很重要，因为它决定后续是进入双视图主线、优化预处理，还是先修补基础问题。

### Suggested Branch
`feat/eval`

### Goal
对第一版 baseline 进行结构化分析，给出是否继续沿当前路线推进的明确结论。

### Scope
- 分析主指标与 fold 波动
- 分析训练/验证 loss 走势
- 分析恶性与非恶性样本上的基本表现
- 检查是否存在明显过拟合、预测塌缩或数据问题
- 给出下一阶段建议

### Deliverables
- 一份 baseline analysis report（md）
- 简要结论：继续 / 调整 / 回退

### Acceptance Criteria
- 报告不是简单罗列数字，而是有判断
- 能说明 baseline 的可信度和局限
- 能明确后续优化方向，而不是笼统说“继续调参”

---

## Issue 2.6 — Prepare the Transition from Backup Baseline to Mainline Multi-view Baseline

### Background
根据 `minimal_system_design.md`，单图 baseline 只是保底方案；项目最终主线仍然是：

> 单图编码器预训练 + 双视图晚融合的 breast-level 二分类系统

因此，M2 如果顺利完成单图 baseline，就应该开始为下一阶段切向主线做准备。  
但此时仍不建议直接在同一 issue 中展开复杂主线开发，而应先完成“过渡准备”。

### Suggested Branch
`feat/model`

### Goal
整理从单图 baseline 过渡到双视图主线所需的接口、依赖和最小设计准备。

### Scope
- 识别单图 backbone 可复用部分
- 明确双视图输入与融合 head 的接口要求
- 确定后续主线实现的最小改造范围
- 记录需要新增的配置项与数据接口

### Deliverables
- 一份 mainline transition note
- 必要的代码接口整理（如适合）

### Acceptance Criteria
- 后续进入主线多视图实现时，不需要从头重构 M2 baseline
- 单图 baseline 与主线之间的关系清晰
- 过渡边界明确，不混入正式主线开发

---

## Issue 2.7 — Sync Baseline Documentation and Experiment Summary

### Background
M2 完成后，项目应当从“最小可运行”进入“已有第一个可信 baseline”的状态。  
这意味着仓库文档需要同步更新，至少明确：

- 当前 baseline 是什么
- 它的配置和结论是什么
- 当前主线与保底方案分别处于什么状态
- 下一阶段准备做什么

### Suggested Branch
`docs`

### Goal
同步 baseline 结果与阶段总结，确保项目文档和实验状态一致。

### Scope
- 更新 README 或实验文档
- 记录 baseline 配置与结果
- 记录当前结论与后续方向
- 形成 M2 handoff 文档

### Deliverables
- 文档更新
- M2 summary / handoff 文档

### Acceptance Criteria
- 仓库文档能反映 M2 的真实状态
- 未来自己或协作者能快速理解当前 baseline 结论
- 文档与代码、结果目录一致