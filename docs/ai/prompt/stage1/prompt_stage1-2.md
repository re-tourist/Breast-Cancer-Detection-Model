你现在继续为乳腺癌检测课程项目实现 Milestone 1 的 Issue 1.2。

当前项目上下文：
- Milestone: M1 — Minimal Runnable Pipeline
- 当前已完成：Issue 1.1（dataset index 与 paired breast-level samples）
- 当前要做：Issue 1.2 — Implement Minimal Preprocessing and Dataset Loading

开始前你必须先阅读并遵守以下文档：
1. docs/plan/minimal_system_design.md
 2. docs/plan/issue_stage1.md
3. src/data/index_builder.py 及其导出的字段定义
4. data/processed/metadata/ 下由 Issue 1.1 生成的索引文件

如果发现仓库实际路径与文档不一致，不要臆造，基于仓库现状做最小合理适配，并在最终汇报中明确指出。

================================
一、任务背景与冻结约束
================================

当前任务不是普通自然图像分类，而是 mammography breast-level malignant probability prediction。

冻结约束如下：
- 主任务标签：pathology == "M" 为 1；pathology in {"B", "N"} 为 0
- 主线输入单位：同一 breast_id 下的两张图（CC + MLO）
- 保底路线：single-image classification + breast-level aggregation
- 所有训练/验证划分后续必须以 breast_id 为 group
- Milestone 1 当前优先目标是打通最小可运行链路，而不是追求最优效果

Issue 1.2 的目标是：
在已经完成的索引基础上，实现最小可运行的读图、轻量预处理、single-image dataset、paired breast-level dataset，以及最小 dataloader smoke test。

================================
二、本次只允许做的内容
================================

请只实现 Issue 1.2 范围内内容，不要提前做 Issue 1.3 / 1.4 / 1.5。

本次允许做的事情：
1. 实现基础图像读取逻辑
2. 实现最小预处理流水线
3. 支持 single-image dataset
4. 支持 paired breast-level dataset
5. 支持训练/验证模式下最小 transform 切换
6. 提供简单可视化或检查脚本，用于人工抽样确认预处理是否基本合理
7. 提供 dataloader smoke test

本次不允许做的事情：
- 不实现 group split
- 不实现训练脚本
- 不实现 AUROC 评估
- 不引入重增强
- 不引入 detection / ROI 主线
- 不引入复杂配置系统
- 不大规模重构 Issue 1.1 的索引逻辑，除非是实现 1.2 所必需的小修补

================================
三、预处理原则（必须遵守）
================================

Milestone 1 只做轻量、合理、可运行的预处理，不做重型增强。

最小预处理原则：
1. 背景/黑边裁剪
2. 方向统一（例如右乳翻转到统一朝向）
3. 保持长宽比 resize
4. padding 到固定尺寸
5. 保留灰度结构
6. 不引入过重增强

请优先实现“稳定、可检查”的版本，而不是追求复杂或强增强版本。

================================
四、推荐实现目标
================================

建议优先在 src/data/ 下实现，保持清晰分层。

建议但不强制的文件结构：
- src/data/transforms.py
- src/data/datasets.py
- scripts/check_dataset_loading.py 或 scripts/preview_preprocessing.py
- tests/test_datasets.py 或等价测试文件

请尽量复用 Issue 1.1 生成的索引，不要重新发明一套字段系统。

建议实现两个 dataset：
A. SingleImageDataset
- 输入：single-image index
- 输出至少包含：
  - image tensor
  - target / is_malignant
  - image_id
  - breast_id
  - view
  - image_path

B. PairedBreastDataset
- 输入：paired breast-level index
- 输出至少包含：
  - x_cc
  - x_mlo
  - target / is_malignant
  - breast_id
  - image_path_cc
  - image_path_mlo

请保持输出结构后续容易接到 train loop 中。

================================
五、关于图像读取的要求
================================

请基于仓库当前数据实际形式做最小合理实现：
- 若图像来自 zip 内路径，则给出稳定可用的读取方案
- 若需要为后续速度优化预留接口，可以留简洁钩子，但不要现在过度设计缓存系统

请不要为了“优雅”而把读图系统复杂化。
当前目标是少量样本也能稳定迭代。

================================
六、关于 transform 的要求
================================

请区分：
- train transform
- eval transform

但当前差异应保持最小。
可以先做到：
- train/eval 共用主预处理
- train 仅允许非常轻量、低风险的增强，若你判断当前阶段不应加增强，也可以先不加，并说明理由

预处理后应保证：
- 输出尺寸统一
- tensor dtype 合理
- 通道形式明确（例如单通道或转成 3 通道时要说明）
- paired dataset 的 CC/MLO 预处理行为一致

================================
七、最小验收标准
================================

你提交的实现必须满足：

1. single-image dataset 能正确返回图像张量、标签和元信息
2. paired breast-level dataset 能正确返回 (x_cc, x_mlo)、标签和 breast_id
3. 预处理后图像尺寸统一
4. 方向统一逻辑能运行且无明显错误
5. dataloader 能在少量样本上稳定迭代
6. 至少有一次人工抽样检查或可视化检查
7. 不越界实现 Issue 1.3 / 1.4 / 1.5

================================
八、对 Issue 1.1 的允许小修补
================================

如果为了完成 Issue 1.2，必须对 Issue 1.1 做极小修补，可以做，但仅限以下类型：
- 补充稳定的字段常量导出
- 固定列顺序
- 提供更直接的索引读取辅助函数
- 修正明显影响 dataset 读取的小问题

不要借机大改 index builder。

================================
九、你最终需要返回给我的内容
================================

请按以下格式汇报：

1. 修改了哪些文件
2. 每个文件的作用
3. single-image dataset 的输入与输出定义
4. paired dataset 的输入与输出定义
5. 预处理流水线具体做了什么
6. 图像读取方案如何实现
7. smoke test / 可视化检查怎么运行
8. 给出一段最小运行方式
9. 给出一次实际输出示例（shape、dtype、keys 等）
10. 明确说明有哪些假设、限制或待确认点

如果你发现实际仓库数据组织让“方向统一”无法可靠判断，请不要瞎写启发式规则。请明确汇报你基于哪个字段或约定来做方向统一；若暂时无法严格实现，就给出最小保守版本并明确说明。
