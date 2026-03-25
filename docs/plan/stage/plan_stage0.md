# Stage 0 Plan — Project Bootstrap & Lightweight Research

## Objective

在不引入复杂模型设计的前提下，完成：
- 项目工程初始化
- 最小问题定义（task / dataset / metric）

为 Stage 1（Minimal Pipeline）提供稳定输入。

---

## Branch Strategy

使用模块化分支（避免 stage-based 分支）：

- feat/data
- feat/scripts
- docs
- dev（集成分支）

---

## Issue Breakdown

---

## Issue 0.1 — Initialize Repository Structure

### Goal
建立基础项目结构，支撑后续开发。

### Scope
- 创建目录结构
- 初始化 README
- 创建 .gitignore

### Suggested Structure
```
project-root/
├── data/
├── docs/
├── models/
├── scripts/
├── tests/
├── .gitignore
├── README.md
```
### Deliverables
- 完整目录结构
- 初始 README

### Acceptance Criteria
- 项目可运行（无 import error）
- 结构清晰可扩展

### Suggested Branch
feat/scripts

---

## Issue 0.2 — Dataset Selection and Inspection

### Goal
确定数据集，并完成基础分析。

### Scope
- 选择乳腺癌数据集（Kaggle）
- 分析数据格式（image / label）
- 统计类别分布

### Deliverables
- dataset summary 文档
- 数据示例可视化

### Acceptance Criteria
- 明确数据路径
- 明确标签形式
- 确认是否存在类别不平衡

### Suggested Branch
feat/data

---

## Issue 0.3 — Define Task and Evaluation Metric

### Goal
明确问题定义（Problem Definition）。

### Scope
- 确定任务类型（classification）
- 定义输入输出格式
- 选择评价指标

### Deliverables
- task_definition.md

### Acceptance Criteria
- 输入输出形式明确
- metric 明确（accuracy / AUC）

### Suggested Branch
docs

---

## Issue 0.4 — Minimal Research Documentation

### Goal
完成轻量调研，仅支撑 baseline 构建。

### Scope
- 查找2-3种常见方法（CNN / transfer learning）
- 不深入推导，只记录可用方案

### Deliverables
- research_notes.md

### Acceptance Criteria
- 至少 2 种 baseline 方案
- 有简单优缺点分析

### Suggested Branch
docs

---

## Issue 0.5 — Setup Basic Dev Workflow

### Goal
建立基本开发流程。

### Scope
- 建立 dev 分支
- 定义合并策略
- 确定 commit 规范

### Deliverables
- workflow 文档

### Acceptance Criteria
- 所有 feature 分支可合并到 dev
- 无冲突问题

### Suggested Branch
dev

---

## Stage 0 Completion Criteria

Stage 0 完成标志：

- 已确定任务（classification）
- 已选定数据集
- 已完成数据初步分析
- 已明确评价指标
- 项目结构已建立
- 分支策略可用

---

## Notes

Stage 0 不允许：
- 引入复杂模型
- 进行训练优化
- 设计高级 pipeline

目标只有一个：

👉 为 Stage 1 提供“可执行的最小输入条件”