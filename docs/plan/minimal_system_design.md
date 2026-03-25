# Minimal System Design — Breast Cancer Detection

## 1. Document Purpose

本文档用于对当前项目的“最小闭环系统”进行正式拍板，明确：

- 当前阶段要解决的任务是什么
- 为什么选择该方案，而不是其他候选方案
- 最小系统的输入、输出、评价、训练与验证协议
- 当前阶段明确不做什么
- 后续迭代应沿什么方向推进

本文档的目标不是给出最终最优方案，而是为 Stage 1 / M1 提供**稳定、可执行、边界清晰**的工程输入。

本文档是当前最小系统设计的决策基线。后续若出现重大调整，应以补充文档或修订记录的形式更新，而不是在实现阶段隐式漂移。

---

## 2. Project Context and Decision Principle

根据当前项目规划，Stage 0 的目标是在不引入复杂模型设计的前提下，完成项目初始化、最小问题定义以及仅支撑 baseline 构建的轻量调研，为 Stage 1 提供稳定输入。整体 milestone 也采用“先验证可行性，再逐步工程化”的推进方式。  
因此，本阶段的核心原则不是“追求最强模型”，而是：

- 先构建一个可信、可提交、可复现的最小闭环
- 在有限时间和有限提交次数下，优先降低方向性错误
- 参考已有强经验，但避免将竞赛重工程方案直接搬入课程项目
- 将复杂设计留到后续 milestone，而不是在最小系统阶段过早展开

本项目最终提交受真实评测约束，且提交机会有限，因此最小系统需要兼顾：
- 工程可实现性
- 指标导向的一致性
- 方案风险可控
- 后续可扩展性

---

## 3. Task Definition

### 3.1 Official Task

根据教师提供的任务说明：

- 输入数据为乳腺 X 线图像
- 每个 `breast_id` 对应 2 张图像
- 两张图像分别来自 CC 与 MLO 两个视图
- 目标是为每一个 `breast_id` 输出一个属于恶性癌症（Malignant）的概率
- 最终提交为图像级分类 prediction，不要求输出检测框
- 评分指标为 AUROC
- 训练集需自行划分 train/dev，且由于数据量较小，明确建议考虑多折交叉验证  
  :contentReference[oaicite:2]{index=2}

因此，本项目当前阶段的正式任务定义为：

> **Breast-level binary classification on paired mammography views**  
> 输入为同一 `breast_id` 的两张乳腺 X 线图像（CC + MLO），输出为该乳房属于恶性类别（Malignant）的概率。

### 3.2 Label Definition

原始 `pathology` 字段包括：

- `M`: Malignant
- `B`: Benign
- `N`: Normal  
  :contentReference[oaicite:3]{index=3}

最小系统阶段采用如下二分类定义：

- `y = 1`：`pathology == M`
- `y = 0`：`pathology in {B, N}`

即主任务定义为：

> **M vs (B + N)**

原因如下：

1. 教师最终评分只关心是否为 Malignant，和主指标 AUROC 直接对应。:contentReference[oaicite:4]{index=4}
2. 在最小系统阶段，三分类会增加任务复杂度，但不会直接提高主目标对齐程度。
3. 将良性 B 视作负类，但在训练策略上需要将其视为更重要的 hard negative，而不是与正常 N 完全等价对待。

### 3.3 Task Boundary

本阶段任务边界明确如下：

- **主线任务是分类，不是检测**
- 可以利用 annotation 信息做辅助分析或后续扩展
- 但最小系统不以目标检测器或分割器为主线路径  
  :contentReference[oaicite:5]{index=5}

---

## 4. Dataset Understanding and Constraints

### 4.1 Provided Dataset

教师提供的数据说明中已明确：

- 训练集包含 650 个乳房、1300 张图像
- 每个 `breast_id` 有 2 张图
- 测试集无标签
- 训练样本较少，可能需要多折交叉验证
- 也可能需要考虑额外公开数据集  
  :contentReference[oaicite:6]{index=6}

结合对 `train.csv` 的实际检查，当前数据在工程上具有以下关键结构约束：

1. 每个 `breast_id` 恰好对应两张图像
2. 两张图像恰好对应两个视图：CC 和 MLO
3. 同一个 `breast_id` 内部标签一致
4. 任务天然是 **breast-level**，而不是单张 image-level 独立分类任务

这意味着最关键的工程要求不是“单图精度最高”，而是：

> **不能让同一 `breast_id` 的两张图落入不同的数据划分中。**

否则将产生严重泄漏。

### 4.2 Why Multi-view Matters

乳腺 X 线筛查在临床上本就依赖多视图观察。公开研究也强调：

- 标准乳腺摄影通常包含 CC 与 MLO 两个视图
- 一个可疑结构通常需要在两个视图中共同出现，才能更可信地判断为真实病灶而非组织重叠
- 多视图建模通常比单视图分析更符合临床使用方式，也往往优于纯单视图方案 :contentReference[oaicite:7]{index=7}

因此，虽然最小系统可以从单图训练起步，但最终的主提交方案不应长期停留在“完全忽略多视图关系”的形式。

---

## 5. Lightweight Research Summary and Engineering Interpretation

### 5.1 Why Reference Competition Solutions

对于乳腺癌检测任务，尤其是 mammography 场景，通用图像分类经验并不总是可靠。你已经收集的参考资料中，高质量竞赛复盘和方案解析具有很高的工程价值，因为它们往往沉淀了：

- 图像尺寸与 resize 的经验
- 多图聚合方式
- 预处理与裁剪细节
- 类别不平衡的实际处理方式
- 多视图 / CAM / ROI 的使用边界  
  :contentReference[oaicite:8]{index=8}

但这些资料的正确使用方式不是“照搬金牌方案”，而是：

> 将其中**低复杂度、高迁移性、与当前任务一致**的经验提炼出来，作为最小闭环的决策依据。

### 5.2 Why Not Copy Full RSNA Gold Pipelines

RSNA Screening Mammography Breast Cancer Detection AI Challenge 是一个大规模真实竞赛任务，吸引了 2000+ 参赛者，目标也是通过筛查性乳腺 X 线检测乳腺癌。它非常适合作为经验参考。:contentReference[oaicite:9]{index=9}

但是，RSNA 类方案通常包含大量不适合当前最小系统阶段直接引入的重工程元素，例如：

- 多模型集成
- 大规模外部数据混合
- 重 TTA
- 检测 + 分类两阶段系统
- 更复杂的阈值与 leaderboard probing 策略

当前课程项目具有完全不同的约束：

- 数据规模更小
- 提交次数更少
- 目标是建立一个可复现、可解释、能稳定提交的最小系统
- 最终指标是 AUROC，而不是围绕特定阈值优化的比赛型指标  
  :contentReference[oaicite:10]{index=10}

因此，最小系统阶段只吸收以下类型的经验：

- 多视图优先于纯单视图
- 尽量避免过小输入分辨率
- 数据划分必须围绕检查级 / breast-level 单位
- 从单图 baseline 向轻量多视图融合过渡是合理路径
- ROI / CAM 可作为后续增强方向，而不是 V1 主线

---

## 6. Candidate Solution Comparison

### 6.1 Candidate A — Random Small CNN / Plain ResNet Baseline

**描述：**
直接使用普通图像分类套路，例如 ResNet18 + 单图训练 + 简单平均融合。

**优点：**
- 工程最快
- 实现风险低
- 易于快速验证训练流程

**缺点：**
- 对 mammography 的任务结构利用不足
- 输入分辨率和细粒度病灶敏感性可能不够
- 容易得到“能跑但不可信”的 baseline
- 对有限提交次数不够友好，因为方向性错误较多

**结论：**
可作为保底实验思路，但不应作为正式拍板主线。

---

### 6.2 Candidate B — Single-image Classifier + Breast-level Aggregation

**描述：**
先将每张图作为独立训练样本训练分类器，推理时再将同一 `breast_id` 的两张图分数聚合成 breast-level 结果。

**优点：**
- 工程简单
- 与现有图像分类代码兼容性高
- 适合做最小 runnable baseline
- 可作为后续多视图模型初始化来源

**缺点：**
- 训练时没有显式建模 CC/MLO 关系
- 聚合策略较粗糙
- 与任务的最终输入结构并不完全一致

**结论：**
这是非常重要的**保底方案**，但不是最终拍板主线。

---

### 6.3 Candidate C — Paired Multi-view Breast-level Classifier

**描述：**
输入同一 `breast_id` 的 CC 与 MLO 两张图，使用共享 backbone 分别提特征，再做轻量融合，直接输出 breast-level malignant probability。

**优点：**
- 与任务定义一致
- 与临床使用方式一致
- 比单图聚合更能利用视图互补信息
- 相比重型多视图 Transformer / graph 方案，轻量晚融合工程风险较低

**缺点：**
- 数据组织和 loader 复杂度高于单图方案
- 对实现规范要求更高
- 需要保证视图配对逻辑严格正确

**结论：**
这是当前最符合“最小但合理”的主线方案。

---

### 6.4 Candidate D — Detection / ROI-supervised Pipeline

**描述：**
利用 annotation 构建目标检测或 ROI 裁剪系统，再进行分类。

**优点：**
- 有可能更聚焦病灶区域
- 有潜力提升局部病灶可见性利用

**缺点：**
- 实现复杂度显著上升
- 对数据清洗、标注解析、训练流程要求更高
- 很容易超出最小系统阶段边界
- 与当前“先闭环后增强”的路线不一致

**结论：**
明确列入后续增强候选，不纳入当前最小系统主线。

---

## 7. Final Decision

### 7.1 Mainline Decision

当前最小系统正式拍板为：

> **单图编码器预训练 + 双视图晚融合的 breast-level 二分类系统**

更具体地说：

1. 先训练一个**单图分类器**，用于学习基本视觉表征
2. 再将该单图 backbone 用作初始化
3. 构建一个**双视图配对输入**的多视图分类器
4. 共享 backbone 分别抽取 CC 与 MLO 特征
5. 采用**轻量晚融合**方式，输出 breast-level malignant probability

这一路线兼顾了：

- 最小闭环可实现性
- 与任务定义一致
- 多视图利用
- 后续扩展空间
- 相对较低的工程风险

### 7.2 Backup Decision

若主线多视图模型在 M1 / M2 阶段出现明显阻塞，则回退到以下保底方案：

> **单图分类 + breast-level 分数聚合**

聚合策略优先比较：

- `mean`
- `max`

保底方案必须始终保持可运行状态，作为整个项目的安全网。

---

## 8. Model and Training Protocol

### 8.1 Input Unit

主线模型的训练与推理基本单位为：

- 一个 `breast_id`
- 对应两张图像：`CC` 与 `MLO`

单图预训练阶段的样本单位为单张图像，但必须保留 `breast_id` 元信息，以支撑后续严格划分与聚合。

### 8.2 Preprocessing

最小系统阶段采用以下预处理原则：

1. 背景/黑边裁剪
2. 统一方向处理（例如右乳翻转到统一朝向）
3. 保持长宽比 resize
4. padding 到固定输入尺寸
5. 保留灰度结构信息，不进行过强颜色化处理

工程解释：

- mammography 中细粒度病灶往往较小
- 粗暴拉伸或过小输入尺寸可能损伤可见性
- 方向不统一会增加模型额外学习负担
- 背景区域过大可能稀释有效区域占比

### 8.3 Input Resolution

最小系统主线建议采用 **1024 级别输入** 作为默认配置。

原因：

- 乳腺 X 线中病灶可能较小
- 224 / 384 这类典型自然图像输入对该任务可能过小
- 1024 在“细节保留”和“工程可训练性”之间是相对稳健的折中

若资源受限，可在早期 sanity check 中使用更小尺寸验证流程，但正式 baseline 不应长期停留在 224 级别。

### 8.4 Backbone Choice

最小系统主线默认 backbone 拍板为：

> **EfficientNet-B2 级别的预训练 CNN backbone**

理由：

- 比随意的浅层 ResNet 更适合作为较强但仍轻量的起点
- 对中高分辨率输入较友好
- 迁移学习路径成熟
- 工程实现难度和资源压力相对可控

注意：

- 这不是最终“理论最优”选择
- 这是在当前阶段对工程收益/风险比的拍板选择

### 8.5 Fusion Head

双视图模型采用**共享 backbone + 轻量晚融合**：

- `f_cc = encoder(x_cc)`
- `f_mlo = encoder(x_mlo)`
- 融合特征可采用：
  - `concat(f_cc, f_mlo, |f_cc - f_mlo|)`
- 融合后接小型 MLP / linear head 输出 logit

该设计的目的不是追求多视图建模的最先进形式，而是：

- 比简单分数平均更充分利用视图信息
- 比 cross-attention / graph / transformer 方案更稳、更简单

### 8.6 Loss Function

主线默认使用：

> **BCEWithLogitsLoss + 正类权重（pos_weight）**

理由：

- 与二分类 AUROC 任务一致
- 实现简单稳定
- 便于后续对不平衡做基础修正

注意：

- 良性 B 虽然属于负类，但在采样和分析上需要额外关注
- 后续如有需要，可在 M3 再比较 focal loss 等改进项

### 8.7 Augmentation Policy

V1 只使用**轻量数据增强**，例如：

- 小幅旋转
- 小幅平移/缩放
- 轻微亮度/对比度调整
- 轻微噪声

V1 明确不使用：

- mixup
- cutmix
- 强 cutout
- 重度几何扰动

理由：

- 病灶可能很小
- 强增强可能直接破坏关键信号
- 最小系统阶段优先保证信号保真和训练稳定性

---

## 9. Data Split and Validation Protocol

### 9.1 Split Unit

数据划分单位必须是：

> **`breast_id` 级别的 group split**

严禁按单张图像随机划分。

### 9.2 Validation Strategy

采用：

> **StratifiedGroupKFold（5-fold）**

分层标签使用 breast-level 的二分类标签（M vs 非M），group 使用 `breast_id`。

理由：

- 教师已明确提示数据量较小，可能需要多折交叉验证。:contentReference[oaicite:11]{index=11}
- 该任务天然存在一对图像对应一个标签的结构约束
- 多折验证比单次随机切分更稳，更适合小样本项目

### 9.3 Primary Metric

主指标拍板为：

> **OOF breast-level AUROC**

理由：

- 与教师最终评测完全一致。:contentReference[oaicite:12]{index=12}
- 可直接反映真实提交方向
- 不依赖额外阈值选择

### 9.4 Secondary Monitoring Metrics

在训练日志中可同时记录：

- train loss
- val loss
- image-level AUROC（仅作辅助）
- breast-level AUROC（主指标）
- class-wise confusion summary（仅开发阶段分析）

但项目正式比较与方案拍板均以 **breast-level OOF AUROC** 为准。

---

## 10. What Is Explicitly Out of Scope for V1

以下内容在当前最小系统阶段**明确不做**：

1. 目标检测器主线
2. 分割器主线
3. CAM 引导主线
4. 多模型 ensemble
5. 外部数据强依赖混训
6. 复杂 TTA
7. 三分类主线
8. 复杂多任务学习
9. 大规模超参数搜索
10. 重度竞赛技巧迁移

这些内容不是“永远不做”，而是：

> **不属于最小系统阶段的冻结范围。**

---

## 11. External Data Policy

教师说明中提到，当前数据量不多，可能需要外部公开数据。:contentReference[oaicite:13]{index=13}

但最小系统阶段的策略拍板为：

> **V1 不依赖外部数据。**

原因：

1. 先验证当前给定数据上的闭环是否稳定
2. 先建立本地 5-fold OOF 评估基线
3. 避免在最小系统阶段引入额外域差与数据清洗负担

若后续需要外部数据，优先级建议如下：

### 11.1 First Priority — VinDr-Mammo

VinDr-Mammo 是公开的大规模数字乳腺摄影数据集，包含 5000 个标准四视图检查、breast-level assessment 以及 lesion-level annotation，任务形态与当前项目更接近。:contentReference[oaicite:14]{index=14}

### 11.2 Second Priority — INBreast

INBreast 规模较小，但标注质量高，适合作为辅助验证或 ROI 分析用数据集。  
（注：本阶段不强制纳入实现范围。）

### 11.3 Third Priority — CBIS-DDSM

CBIS-DDSM 是非常经典的公开乳腺 X 线数据集，包含正常、良性、恶性以及验证病理信息，且经过较好整理。:contentReference[oaicite:15]{index=15}

但需要注意：

- 其成像域与现代数字乳腺摄影存在差异
- 作为 V1 主体混训数据并不稳妥
- 更适合在后续阶段做扩展验证，而不是最小系统的第一依赖

---

## 12. Risks and Fallback Logic

### 12.1 Main Risks

当前最小系统的主要风险包括：

1. 数据量小导致 fold 波动较大
2. 多视图 loader / 配对逻辑实现错误
3. 输入尺寸较高导致资源压力
4. 预处理不当损伤病灶细节
5. 负类内部（B 与 N）差异导致模型出现“恶性 vs 正常”偏置，而对良性病灶区分不足

### 12.2 Fallback Order

若开发过程中出现阻塞，回退顺序如下：

1. **先保证单图 baseline 全流程可用**
2. 再切换到双视图晚融合
3. 若 1024 输入无法稳定训练，先用较小尺寸做流程验证，再回升分辨率
4. 若 backbone 过重导致阻塞，可临时退到更轻 backbone 做流程检查
5. 绝不在主线未稳定前引入 ROI / 检测 / 外部数据混训

---

## 13. Stage-1-Oriented Engineering Requirements

为了让本文档能直接支撑后续实现，Stage 1 需要满足以下工程要求：

1. 能正确读取单图与双视图样本
2. 能基于 `breast_id` 生成严格的 group split
3. 能训练至少 1 fold 跑通 end-to-end
4. 能输出 breast-level AUROC
5. 能保存 OOF 预测与 per-breast 结果
6. 能比较保底方案与主线方案
7. 训练日志、配置文件、结果文件路径清晰

也就是说，Stage 1 的“最小 runnable”不是只要 loss 能下降，而是要具备：

> **从数据组织到 breast-level 评估的完整闭环。**

---

## 14. Final Frozen Decision

当前最小系统设计最终冻结为：

### Mainline
- 任务：breast-level malignant probability prediction
- 标签：M vs (B + N)
- 输入：同一 `breast_id` 的 CC + MLO 双视图
- 模型：单图预训练 backbone + 双视图晚融合分类器
- backbone：EfficientNet-B2 级别预训练 CNN
- 输入尺寸：默认 1024 级别
- 验证：5-fold StratifiedGroupKFold
- 主指标：OOF breast-level AUROC

### Backup
- 单图分类器
- breast-level `mean` / `max` 聚合

### Out of Scope for V1
- detection / ROI 主线
- segmentation 主线
- ensemble
- external-data-dependent training
- heavy TTA
- 复杂多任务设计

---

## 15. Revision Policy

若后续需要修改本文档中的核心决策，至少应满足以下条件之一：

- 当前主线在工程上不可稳定实现
- 当前主线在本地 OOF 上明显劣于保底方案
- 有新增证据表明某项冻结决策不合理
- M2/M3 阶段进入受控增强实验，需要正式扩展边界

在未满足上述条件前，实现层面不得擅自偏离本文档的冻结范围。