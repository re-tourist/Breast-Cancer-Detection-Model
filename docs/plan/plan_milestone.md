# Milestone Plan

## Overview

本项目为乳腺癌检测任务，采用“先验证可行性 → 再逐步工程化”的策略推进。

整体原则：

- 先跑通最小闭环，再优化
- 每个 Mileston**e 必须有明确完成判据**
- **前期 Milestone 属于探索型，不固化技术路**线

***

## M0: Project Bootstrap and Lightweight Research

### Goal

完成项目初始化，并明确最小可行问题定义（Problem Definition）。

### Scope

- 建立项目仓库与基础结构
- 进行轻量调研（仅支撑最小系统）
- 明确任务形式与数据来源

### Deliverables

- GitHub repository 初始化
- 基础目录结构
- 轻量调研文档（dataset / task / metric）
- 分支策略建立

### Acceptance Criteria

- 已确定任务类型（classification）
- 已选定数据集
- 已明确输入输出形式
- 已确定评价指标（如 accuracy / AUC）
- 项目结构初始化完成

***

## M1: Minimal Runnable Pipeline

### Goal

构建端到端最小可运行流程（不追求效果，只验证流程）。

### Scope

- 数据加载
- 数据划分
- 最小训练循环
- 基本评估逻辑

### Deliverables

- dataset loader
- train loop
- eval script
- baseline run log

### Acceptance Criteria

- 能完成至少 1 epoch 训练
- loss 正常变化
- 能输出验证指标
- 无阻塞性 bug

***

## M2: Simple CNN Baseline

### Goal

建立第一个可信的 CNN baseline。

### Scope

- 使用标准模型（ResNet18 等）
- 完整训练流程
- 结果记录与分析

### Deliverables

- baseline model
- training logs
- evaluation metrics
- result visualization

### Acceptance Criteria

- baseline 可复现
- 有完整训练记录
- 指标稳定（非随机）
- 有初步误差分析

***

## M3: Baseline Improvement and Controlled Experiments

### Goal

在 baseline 基础上进行小步优化与对比实验。

### Scope

- 数据增强
- 类别不平衡处理
- 超参数调整
- backbone 对比

### Deliverables

- 实验记录
- 对比结果
- 消融分析

### Acceptance Criteria

- 至少 2 组对比实验
- 指标有可解释变化
- 有结论总结

***

## M4: Report and Final Packaging

### Goal

完成最终项目交付。

### Scope

- 整理实验结果
- 可视化
- 撰写报告

### Deliverables

- report.md
- figures
- final code

### Acceptance Criteria

- 报告完整
- 实验结果清晰
- 项目可复现

