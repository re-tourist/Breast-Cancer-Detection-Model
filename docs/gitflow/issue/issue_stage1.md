# Stage 1 Issue Plan — M1: Minimal Runnable Pipeline

> Milestone: M1 — Minimal Runnable Pipeline  
> Goal: 搭建一个端到端最小可运行流程，不追求效果，只追求跑通。  
> Design reference: `docs/plan/minimal_system_design.md`

---

## Issue 1.1 — Build Dataset Index and Paired Breast-level Samples

### Background
根据 `docs/plan/minimal_system_design.md`，当前任务不是普通单图分类，而是 **breast-level malignant probability prediction**。  
每个 `breast_id` 对应两张图像（CC + MLO），最终预测单位也是 `breast_id`。因此，项目最早期必须先把数据组织层做对，否则后续训练、验证和聚合都会建立在错误输入之上。

M1 阶段的首要任务不是追求复杂预处理，而是建立一套**清晰、稳定、可检查**的数据索引机制，至少支持两类样本视图：

1. **single-image view**：用于后续单图 baseline 或编码器预训练
2. **paired breast-level view**：用于后续双视图主线模型

这一层同时需要明确保留关键元信息，例如：

- `image_id`
- `breast_id`
- `view`（CC / MLO）
- `pathology`
- 二分类标签 `is_malignant`
- 图像路径

### Suggested Branch
`feat/data`

### Goal
建立项目统一的数据索引与样本组织入口，支持后续单图与双视图两种读取方式。

### Scope
- 解析教师提供的数据说明与 `train.csv`
- 统一生成结构化样本索引
- 检查每个 `breast_id` 是否确实对应两张图、且视图为 CC + MLO
- 提供单图样本表和双视图样本表
- 输出基本数据统计信息，便于人工核查

### Deliverables
- `src/data/` 下的数据索引与样本构建代码
- 可复用的数据清单文件（如 csv/json）
- 一份简短的数据检查输出或报告
- 支撑后续 dataloader 的统一字段定义

### Acceptance Criteria
- 能从原始数据稳定构建 single-image 样本索引
- 能从原始数据稳定构建 paired breast-level 样本索引
- 每个 paired sample 都能正确对应 CC 与 MLO
- 标签字段统一为 `is_malignant = 1(pathology == M)`
- 数据统计结果与原始说明基本一致
- 无明显缺失配对、重复配对或标签冲突问题

---

## Issue 1.2 — Implement Minimal Preprocessing and Dataset Loading

### Background
`minimal_system_design.md` 已明确，最小系统阶段需要采用**轻量但任务合理**的预处理，而不是自然图像任务中的默认处理。  
当前阶段不追求最优图像增强，而是要先打通“读图 → 预处理 → 张量输出”的最小链路，并尽可能贴近后续 baseline 设定。

最小预处理原则包括：

- 背景/黑边裁剪
- 方向统一（如右乳翻转到统一朝向）
- 保持长宽比 resize
- padding 到固定尺寸
- 保留灰度结构

M1 中的重点不是做很多增强，而是让 dataloader 输出稳定、可检查、可复现。

### Suggested Branch
`feat/data`

### Goal
实现最小可运行的数据集读取与预处理流程，确保单图和双视图输入都能稳定送入模型。

### Scope
- 实现基础图像读取逻辑
- 实现最小预处理流水线
- 支持 single-image dataset
- 支持 paired breast-level dataset
- 支持训练/验证模式下的基础 transform 切换
- 为后续高分辨率训练保留接口，但当前优先保证流程正确

### Deliverables
- `src/data/datasets.py` 或等效模块
- `src/data/transforms.py` 或等效模块
- 一段简单的可视化/检查脚本，用于确认预处理结果
- 最小 dataloader smoke test

### Acceptance Criteria
- 单图 dataset 能正确返回图像张量、标签和元信息
- 双视图 dataset 能正确返回 `(x_cc, x_mlo)`、标签和 `breast_id`
- 预处理后图像尺寸统一
- 方向统一逻辑能运行且无明显错误
- 数据读取流程可在少量样本上稳定迭代
- 至少完成一次人工抽样检查，确认预处理结果基本合理

---

## Issue 1.3 — Implement Group-aware Train/Validation Split

### Background
该任务最关键的工程约束之一是：**不能让同一 `breast_id` 的两张图分到不同 fold 或 train/val 两侧**。  
`minimal_system_design.md` 已明确将验证协议冻结为 **breast_id 级别的 group split**，并优先采用 `StratifiedGroupKFold`。

因此，M1 必须优先建立**可复用、可检查、不会泄漏**的划分逻辑。这一层若做错，后续所有指标都不可信。

### Suggested Branch
`feat/data`

### Goal
实现基于 `breast_id` 的严格划分逻辑，为后续训练与评估提供可信 fold 信息。

### Scope
- 以 `breast_id` 为 group 进行划分
- 以 breast-level 二分类标签进行分层
- 优先支持 5-fold 划分
- 输出 fold assignment 文件
- 增加必要检查，防止泄漏

### Deliverables
- fold 生成脚本或模块
- fold 分配结果文件
- 一份简单的 fold 分布统计输出

### Acceptance Criteria
- 同一 `breast_id` 不会同时出现在 train/val 两侧
- fold 数量和样本数量正确
- 每个 fold 的正负样本分布基本合理
- 可重复生成一致的划分结果（在固定随机种子下）
- 划分结果可直接被后续训练脚本读取

---

## Issue 1.4 — Create Minimal Training Script Skeleton

### Background
M1 的目标不是正式 baseline 训练，而是先构建一个**最小训练闭环骨架**。  
这意味着训练脚本需要优先满足：

- 可读配置
- 可跑通一个 epoch
- 可输出基本日志
- 可保存最小结果

而不是一开始就追求完整实验管理或复杂训练策略。

该骨架后续会被 M2 复用，因此需要做到“简洁但不临时”。

### Suggested Branch
`feat/train`

### Goal
建立最小训练脚本框架，支持从 dataloader 读取样本并完成单轮训练/验证流程。

### Scope
- 配置读取
- 数据集与 dataloader 接入
- 模型初始化接口
- loss 计算
- optimizer 基础逻辑
- train/val loop
- 基础日志打印
- checkpoint/结果保存接口预留

### Deliverables
- `train.py` 或等效最小训练入口
- 训练配置样例
- 训练循环骨架代码

### Acceptance Criteria
- 能在 1 fold 或一个小子集上完整跑通 train/val
- 能打印基本 loss 日志
- 训练过程中无 shape/label/device 基础错误
- 代码结构可被 M2 继续扩展，而非一次性脚本

---

## Issue 1.5 — Create Minimal Evaluation and Breast-level Aggregation Skeleton

### Background
当前任务最终评价单位是 **breast-level AUROC**，而不是单图 accuracy。  
因此，即使在 M1 阶段还未正式做 baseline，也必须先把评估骨架搭对：

- 能收集验证预测
- 能按 `breast_id` 聚合
- 能计算 breast-level 指标
- 能输出可追踪的结果文件

如果评估框架晚于训练脚本建立，很容易导致训练逻辑先按 image-level 习惯固化，后面再改成本更高。

### Suggested Branch
`feat/eval`

### Goal
建立最小评估脚本框架，支持从验证输出中完成 breast-level 聚合与 AUROC 计算。

### Scope
- 收集 image-level 或 pair-level 预测结果
- 实现基于 `breast_id` 的聚合接口
- 支持 `mean` / `max` 等基本聚合方式
- 计算 AUROC
- 保存验证结果表

### Deliverables
- `src/eval/` 下的最小评估模块
- AUROC 计算逻辑
- breast-level prediction 导出文件
- 简单的评估入口脚本

### Acceptance Criteria
- 能对一份预测结果表正确完成 `breast_id` 聚合
- 能输出 breast-level AUROC
- 结果文件中包含 `breast_id`, target, prediction 等关键字段
- 评估逻辑可被 M2 正式 baseline 直接复用

---

## Issue 1.6 — Run One End-to-End Smoke Test and Record Sanity Findings

### Background
M1 的 milestone 定义已经明确：要跑通一轮最小训练与验证，并记录是否存在数据、标签、loss、过拟合等基础问题。  
因此，M1 最后必须有一个“端到端 smoke test” issue，把前面数据、训练、评估链路真正串起来。

这个 issue 的目标不是追求漂亮指标，而是回答几个关键问题：

- 数据能不能正确读到训练里
- 标签有没有错位
- loss 能不能正常下降
- 评估脚本是不是能产出结果
- 有没有明显泄漏、塌陷、全常数输出等基础异常

### Suggested Branch
`feat/scripts`

### Goal
基于当前最小管线完成一次端到端 smoke test，并形成可复查的 sanity 记录。

### Scope
- 选定一个最小可运行配置
- 跑通至少 1 fold 或一个小规模 train/val 实验
- 保存基本日志与结果
- 记录基础异常与观察结论

### Deliverables
- smoke test 运行脚本
- 一份简短的 sanity report（md）
- 运行日志、指标与必要输出文件路径

### Acceptance Criteria
- 能完整跑通数据读取、训练、验证、评估闭环
- 生成 breast-level AUROC 或至少完成该指标计算流程
- 有明确的 sanity 结论，而不是只说“跑过了”
- 能指出是否存在基础问题（标签错、loss 异常、输出塌缩、明显过拟合等）

---

## Issue 1.7 — Sync Stage-1 Documentation and Usage Notes

### Background
M1 结束后，项目应当从“零散代码尝试”进入“有组织的最小闭环状态”。  
因此需要把 Stage 1 的使用方式、目录结构、运行入口和当前已知限制同步到文档中，否则后续 M2 很容易在不清楚前提的情况下继续扩展。

### Suggested Branch
`docs`

### Goal
同步 Stage 1 的工程文档与运行说明，为后续 baseline 正式训练提供清晰入口。

### Scope
- 更新 README 中的最小运行说明（如适用）
- 记录 Stage 1 的产物与当前边界
- 补充必要的目录/脚本说明
- 记录当前已知问题与后续注意事项

### Deliverables
- 文档更新
- Stage 1 handoff 或 summary 文档

### Acceptance Criteria
- 新成员或未来自己能根据文档定位 M1 产物
- 能知道最小 pipeline 如何运行
- 能知道 M1 已完成什么、未完成什么
- 文档内容与实际代码状态一致