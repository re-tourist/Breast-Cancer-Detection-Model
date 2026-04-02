你现在继续为乳腺癌检测课程项目实现 Milestone 1 的 Issue 1.3。

当前项目上下文：
- Milestone: M1 — Minimal Runnable Pipeline
- 已完成：
  - Issue 1.1：dataset index 与 paired breast-level samples
  - Issue 1.2：minimal preprocessing、dataset loading、dataloader smoke test
- 当前要做：
  - Issue 1.3：Implement breast_id-grouped train/val split and reusable split artifacts

开始前你必须先阅读并遵守以下内容：
1. docs/plan/minimal_system_design.md
 2. docs/plan/issue_stage1.md
3. src/data/index_builder.py 及 Issue 1.1 生成的索引文件
4. src/data/datasets.py 与 transforms.py，理解当前 single / paired dataset 的输入字段
5. data/processed/metadata/ 下的 primary_single_image_index.csv 与 primary_paired_breast_index.csv

如果仓库实际路径与文档不一致，不要臆造，基于仓库现状做最小合理适配，并在最终汇报中明确指出差异。

================================
一、任务背景与冻结约束
================================

当前主任务是 mammography breast-level malignant probability prediction。

冻结约束如下：
- pathology == "M" -> is_malignant = 1
- pathology in {"B", "N"} -> is_malignant = 0
- 同一 breast_id 下有两张图（CC + MLO）
- 所有训练/验证划分必须以 breast_id 为 group
- 绝对不能出现同一个 breast_id 同时出现在 train 和 val 中
- Milestone 1 的目标是建立最小可运行闭环，不做复杂多折实验框架

Issue 1.3 的目标是：
基于 Issue 1.1 的 paired breast-level index，实现可复用、可检查、可落盘的 train/val split 机制，并让 single-image 与 paired 两种视图都能共享这一 split。

================================
二、本次只允许做的内容
================================

本次允许做的事情：
1. 基于 paired breast-level index 生成 breast_id 级别的 train/val split
2. 保证 train/val 之间 breast_id 严格不泄漏
3. 生成 paired 视图可直接使用的 split 文件
4. 生成 single-image 视图可直接使用的 split 文件（基于同一 breast_id 划分映射）
5. 输出 split 统计信息与检查报告
6. 提供一个最小脚本，方便重复生成 split
7. 提供最小测试，验证没有 leakage、样本数合理、标签分布可检查

本次不允许做的事情：
- 不实现训练脚本
- 不实现 AUROC / accuracy 评估
- 不实现 k-fold / cross-validation 大框架
- 不引入复杂实验管理系统
- 不修改 Issue 1.1 / 1.2 的主体逻辑，除非是完成本 issue 所必需的小修补

================================
三、split 设计原则（必须遵守）
================================

1. split 的基本分组单位必须是 breast_id
2. single-image split 不能自己重新随机划分，必须从 breast-level split 映射得到
3. paired 与 single 两种视图必须共享同一套 train/val 边界
4. 必须显式检查 leakage
5. 必须输出基础统计，便于人工确认 split 是否合理

你可以使用简单的 holdout 方案，例如：
- train / val = 80 / 20
或文档/仓库已有约定的比例

如无强制文档要求，优先使用一个简单、稳定、可复现的随机种子方案。

================================
四、推荐实现目标
================================

建议在 src/data/ 或 scripts/ 下实现最小 split 机制。

建议但不强制的产物结构：
- src/data/splits.py
- scripts/build_splits.py
- tests/test_splits.py
- data/processed/splits/ 下保存生成的 split 文件
- outputs/reports/ 或 data/processed/metadata/ 下保存 split summary

建议至少生成以下产物：

A. paired_breast_split_train.csv
B. paired_breast_split_val.csv
C. single_image_split_train.csv
D. single_image_split_val.csv
E. split_summary.json 或 split_report.json

文件命名可按仓库风格调整，但必须清晰可复用。

================================
五、必须做的检查
================================

请显式检查并汇报：

1. train 和 val 的 breast_id 集合是否完全不相交
2. single-image train/val 是否由 paired split 映射而来，而不是单独随机
3. paired split 后每个样本是否仍保持 CC/MLO 完整
4. train / val 的 malignant vs non-malignant 分布
5. train / val 的 image 数、breast 数
6. 是否存在空 split、极端失衡或异常情况

如果你能在不复杂化实现的前提下做简单的 stratified group split，可以做；
如果当前阶段不方便稳定实现，也可以先做普通 group split，但必须明确说明标签分布结果。

================================
六、最小验收标准
================================

你提交的实现必须满足：

1. train/val split 严格按 breast_id 分组
2. 没有任何 breast_id leakage
3. paired 与 single 视图共享同一 train/val 边界
4. 输出可复用的 split 文件
5. 有基础统计和检查结果
6. 有最小脚本和测试
7. 不越界实现 Issue 1.4 / 1.5

================================
七、对前面 issue 的允许小修补
================================

如果为了完成 Issue 1.3，必须对 Issue 1.1 / 1.2 做极小修补，可以做，但仅限：
- 补充字段常量导出
- 增加索引读取辅助函数
- 修正明显影响 split 构建的小问题

不要借机重构 datasets / transforms / index builder。

================================
八、你最终需要返回给我的内容
================================

请按以下格式汇报：

1. 修改了哪些文件
2. 每个文件的作用
3. split 的分组单位是什么
4. split 是如何保证 paired / single 边界一致的
5. 输出了哪些 split 文件，保存到哪里
6. 做了哪些 leakage 检查
7. train / val 的 breast 数、image 数、标签分布统计
8. 给出最小运行方式
9. 给出一次实际输出示例
10. 明确说明有哪些假设、限制或待确认点

如果你发现仓库中的标签分布太不均衡，导致简单 holdout 结果不理想，请不要直接扩展成复杂实验框架。请先保持 M1 最小实现，只需在汇报中明确说明当前 split 的性质与局限。
