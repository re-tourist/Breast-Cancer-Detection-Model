你现在继续为乳腺癌检测课程项目实现 Milestone 1 的 Issue 1.4。

当前项目上下文：
- Milestone: M1 — Minimal Runnable Pipeline
- 已完成：
  - Issue 1.1：dataset index 与 paired breast-level samples
  - Issue 1.2：minimal preprocessing、dataset loading、dataloader smoke test
  - Issue 1.3：breast_id-grouped train/val split and reusable split artifacts
- 当前要做：
  - Issue 1.4：Implement minimal train/val loop for a runnable baseline

开始前你必须先阅读并遵守以下内容：
1. docs/plan/minimal_system_design.md
 2. docs/plan/issue_stage1.md
3. src/data/index_builder.py、src/data/datasets.py、src/data/transforms.py、src/data/splits.py
4. data/processed/splits/ 下的 split artifacts
5. 现有 scripts/ 下与数据检查相关的脚本，避免重复造轮子

如果仓库实际路径与文档不一致，不要臆造，基于仓库现状做最小合理适配，并在最终汇报中明确指出差异。

================================
一、任务背景与冻结约束
================================

当前主任务是 mammography breast-level malignant probability prediction。

冻结约束如下：
- pathology == "M" -> is_malignant = 1
- pathology in {"B", "N"} -> is_malignant = 0
- 主线预测单位最终是 breast-level
- 但 Milestone 1 的保底可运行路线允许先做 single-image baseline
- 数据划分必须复用 Issue 1.3 的 breast_id-grouped split
- 当前阶段目标是建立最小可运行训练/验证闭环，不追求最优模型与最优结果

Issue 1.4 的目标是：
基于已有 split 和 dataset，实现一个最小、稳定、可复现的 train/val baseline，使项目第一次具备完整的“训练—验证”运行能力。

================================
二、本次只允许做的内容
================================

本次允许做的事情：
1. 实现一个最小 baseline 模型
2. 实现 train loop 与 val loop
3. 从已有 split 文件构建 dataloader
4. 计算最小基础指标
5. 保存最小训练输出与结果摘要
6. 提供一个可直接运行的训练脚本
7. 提供最小 smoke test 或 sanity check

本次不允许做的事情：
- 不实现复杂 backbone 搜索
- 不引入大规模实验管理系统
- 不引入复杂超参数搜索
- 不做 cross-validation 框架
- 不做 detection / segmentation / ROI 分支
- 不提前扩展到完整 paper-style pipeline
- 不大改 Issue 1.1 / 1.2 / 1.3 已有实现

================================
三、baseline 设计原则（必须遵守）
================================

Milestone 1 当前优先目标是“先跑通”，不是“先做强”。

请优先实现一个最小且稳定的 single-image classification baseline：
- 输入：SingleImageDataset
- 标签：is_malignant
- 输出：binary logit / probability
- loss：标准二分类损失（如 BCEWithLogitsLoss）
- metric：至少包含 val loss 与一个基础分类指标

模型选择原则：
- 优先简单、稳定、依赖少
- 不要一上来接很重的预训练大模型
- 可以使用一个很小的 CNN，或极轻量 torchvision backbone（若仓库依赖允许且实现更稳）
- 关键是可运行、可验证、结构清晰

================================
四、关于验证与指标的要求
================================

当前阶段至少要有：
1. train loss
2. val loss
3. 一个基础二分类指标，例如 accuracy
4. 最好再加 AUROC；若当前依赖或样本情况不稳定，可先不强制，但要说明

注意：
- 当前 split 是 breast_id-grouped 的，所以 image-level val 指标至少不会有明显 leakage
- 但当前 baseline 如果是 single-image classifier，那么它本质上仍是 image-level prediction
- 你可以先实现 image-level 验证闭环
- 若实现成本不高，欢迎顺手补一个基于 breast_id 的 mean aggregation 验证函数，把同一 breast 的两张图概率做平均后再算 breast-level metric；但这不是强制项，不能因此拖慢主线

================================
五、推荐实现目标
================================

建议但不强制的文件结构：
- src/models/baseline.py 或 src/models/classifier.py
- src/engine/trainer.py 或 src/training/train_loop.py
- scripts/train_baseline.py
- tests/test_training_smoke.py
- outputs/m1_baseline/ 或 runs/m1_baseline/ 下保存结果

训练脚本至少应支持：
- 指定 train split csv
- 指定 val split csv
- batch size
- epochs
- image size（若当前数据 pipeline 已固定，可不暴露太多参数）
- random seed
- output dir

结果产物建议至少包括：
- config / args 保存
- 最后一轮或最佳轮的 metrics summary
- 简单日志
- 可选：best model checkpoint

================================
六、最小验收标准
================================

你提交的实现必须满足：

1. 能基于 Issue 1.3 的 split 文件正常构建 train/val dataloader
2. 能完整跑通至少 1 个 epoch 的训练与验证
3. 能输出 train loss、val loss 和至少一个基础指标
4. 结果文件有明确保存位置
5. 有最小脚本和测试 / smoke test
6. 不越界实现 Issue 1.5 或更后面的复杂内容

================================
七、实现风格要求
================================

1. 先追求稳定和清晰，不追求复杂和“高级感”
2. train loop、val loop、metric 计算尽量分层清楚
3. 不要把数据加载、模型定义、训练逻辑、CLI 全部糊在一个文件里
4. 保持后续 Issue 1.5 可以平滑接入 breast-level aggregation / evaluation
5. 如果你顺手实现了 breast-level mean aggregation metric，请保持它是轻量附加能力，而不是把整个 issue 重心带偏

================================
八、你最终需要返回给我的内容
================================

请按以下格式汇报：

1. 修改了哪些文件
2. 每个文件的作用
3. baseline 模型是什么，为什么这样选
4. train/val loop 做了什么
5. 使用了哪些指标
6. 如何运行最小训练
7. 给出一次实际运行输出示例
8. 输出结果保存到哪里
9. 做了哪些 smoke test / 单元测试
10. 明确说明有哪些假设、限制或待确认点

如果你判断当前阶段加入 breast-level mean aggregation 验证非常低成本且有益，可以实现；但请把它作为“轻量附加项”，不要因此引入复杂 evaluator 框架。当前主任务仍然是先建立最小训练/验证闭环。
