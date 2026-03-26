你现在继续为乳腺癌检测课程项目实现 Milestone 1 的 Issue 1.5。

当前唯一权威的 issue 定义来源是：
- Stage 1 Issue Plan / issue_stage1.md

请先阅读并严格遵守其中对 Issue 1.5 的定义，不要自行改写 issue 目标。你还必须结合以下文档与现有实现：
1. docs/plan/minimal_system_design.md
2. issue_stage1.md 中 Issue 1.5 的原始要求
3. 当前已完成的 Issue 1.1–1.4 / 1.4.x 相关实现
4. Issue 1.3 的 split artifacts
5. 当前 train/val 输出结构与 checkpoint / metrics summary 结构

如果仓库实际路径与文档不一致，不要臆造，基于仓库现状做最小合理适配，并在最终汇报中明确指出差异。

================================
一、严格按原 issue 定义执行
================================

Issue 1.5 的原始定义是：

Title:
Create Minimal Evaluation and Breast-level Aggregation Skeleton

Goal:
建立最小评估脚本框架，支持从验证输出中完成 breast-level 聚合与 AUROC 计算。

Scope:
- 收集 image-level 或 pair-level 预测结果
- 实现基于 breast_id 的聚合接口
- 支持 mean / max 等基本聚合方式
- 计算 AUROC
- 保存验证结果表

Deliverables:
- src/eval/ 下的最小评估模块
- AUROC 计算逻辑
- breast-level prediction 导出文件
- 简单的评估入口脚本

Acceptance Criteria:
- 能对一份预测结果表正确完成 breast_id 聚合
- 能输出 breast-level AUROC
- 结果文件中包含 breast_id, target, prediction 等关键字段
- 评估逻辑可被 M2 正式 baseline 直接复用

你必须以这些要求为准，不要把本 issue 扩展成复杂实验平台。

================================
二、本次允许做的内容
================================

1. 从当前验证输出中收集预测结果
2. 实现独立、清晰的 breast-level aggregation 接口
3. 至少支持 mean 聚合，并尽量顺手支持 max 聚合
4. 实现 AUROC 计算与单类安全退化
5. 导出 breast-level prediction 文件
6. 提供一个最小 evaluation 入口脚本
7. 提供最小测试，验证聚合和 AUROC 逻辑

================================
三、本次不允许做的内容
================================

1. 不重构整个训练框架
2. 不扩展成复杂 evaluator framework
3. 不开始 paired 双分支训练
4. 不进入 Milestone 2 的正式 baseline 工程
5. 不大改 Issue 1.4 的训练主骨架
6. 不引入多种复杂 aggregation 策略搜索

================================
四、实现要求
================================

请尽量在 src/eval/ 下组织最小评估模块，保持与原 issue deliverables 一致。

建议但不强制的实现方向：
- src/eval/aggregation.py
- src/eval/metrics.py
- scripts/run_eval.py 或等价入口
- 输出 breast_level_predictions.csv
- 输出 breast_level_metrics.json

聚合输入不要被写死为 single-image only。
当前主来源可以是 image-level prediction，但接口层面应允许“对一份预测结果表”进行聚合，这样后续更容易复用到 pair-level 输出。

聚合要求：
- 按 breast_id 分组
- target 在同组内必须一致，否则报错
- 至少支持 aggregation = mean
- 最好支持 aggregation = max
- 输出中至少包含：
  - breast_id
  - target
  - prediction
  - num_items_aggregated

指标要求：
- 计算 breast-level AUROC
- 若 target 只有单类，必须安全退化并明确记录

================================
五、最小验收标准
================================

你的实现必须满足：

1. 能对一份预测结果表正确完成 breast_id 聚合
2. 能输出 breast-level AUROC
3. 结果文件中包含 breast_id、target、prediction 等关键字段
4. 有独立、清晰、可复用的最小评估模块
5. 有简单评估入口脚本
6. 评估逻辑可被 M2 正式 baseline 直接复用
7. 不越界扩展到复杂评估平台

================================
六、测试要求
================================

请补充最小测试，至少覆盖：
1. mean 聚合正确
2. max 聚合正确（如果你实现了）
3. 同一 breast_id 内 target 不一致时报错
4. AUROC 单类时安全退化
5. 评估 artifact 成功生成

================================
七、最终汇报格式
================================

请按以下格式返回：

1. 修改了哪些文件
2. 每个文件的作用
3. aggregation 接口支持哪些输入与聚合方式
4. AUROC 如何计算，单类时如何处理
5. 输出了哪些结果文件，保存到哪里
6. 简单评估入口脚本如何运行
7. 给出一次最小运行示例
8. 给出一段实际输出示例
9. 补了哪些测试
10. 明确说明这次实现如何对应 issue_stage1.md 中 Issue 1.5 的原始 Goal / Scope / Deliverables / Acceptance Criteria