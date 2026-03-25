# 📄 `issue_stage1.md`

```markdown
# Stage 1 (M0) — Issue Breakdown
Project Bootstrap & Lightweight Research

---

## Issue 0.1 — Initialize Project Structure

### Goal
建立项目基础目录结构，确保后续模块开发有统一入口。

### Scope
- 创建标准目录结构（src / data / scripts / configs / docs / outputs）
- 初始化 README.md
- 添加 .gitignore（忽略 data、outputs 等）

### Suggested Structure

```

project_root/
├── src/
│   ├── data/
│   ├── models/
│   ├── train/
│   └── eval/
├── data/
├── scripts/
├── configs/
├── outputs/
├── docs/
└── README.md

```

### Deliverables
- 完整目录结构
- README 初始说明

### Acceptance Criteria
- 项目结构清晰
- 无 import 路径错误
- 可扩展性良好

### Suggested Branch
feat/scripts

---

## Issue 0.2 — Design Data Directory Structure

### Goal
建立统一的数据目录规范，支持课程数据 + 外部数据扩展。

### Scope
- 设计 data/ 目录结构
- 区分 raw / interim / processed
- 区分 primary / external 数据来源
- 编写 data/README.md 说明规范

### Expected Structure

```

data/
├── raw/
│   ├── primary/
│   └── external/
├── interim/
│   ├── primary/
│   └── external/
├── processed/
│   ├── metadata/
│   ├── splits/
│   └── cache/
└── README.md

```

### Deliverables
- data 目录创建
- README 说明数据层语义

### Acceptance Criteria
- 结构清晰表达数据生命周期
- 可支持多数据集扩展
- 无硬编码路径设计

### Suggested Branch
feat/data

---

## Issue 0.3 — Dataset Intake and Inspection

### Goal
完成课程数据集接入与初步分析。

### Scope
- 放置原始数据到 raw/primary/
- 解压 train/test 图像到 interim/primary/
- 解析 train.csv
- 可视化样本（随机几张图 + 标签）

### Deliverables
- 数据成功加载
- 基本统计信息（类别分布）
- 样本可视化结果

### Acceptance Criteria
- 能正确读取图像与标签
- 数据路径明确
- 无数据缺失或异常

### Suggested Branch
feat/data

---

## Issue 0.4 — Define Task and Evaluation Protocol

### Goal
明确问题定义，为后续模型训练提供统一接口。

### Scope
- 确定任务类型（classification）
- 定义输入输出格式
- 选择评价指标（accuracy / precision / recall / AUC）

### Deliverables
- docs/task_definition.md

### Acceptance Criteria
- 输入输出形式清晰
- metric 明确
- 可直接用于训练模块设计

### Suggested Branch
docs

---

## Issue 0.5 — Minimal Research Notes for Baseline

### Goal
进行最小必要调研，仅支撑 baseline 构建。

### Scope
- 调研 2–3 种常见方法（CNN / transfer learning）
- 简要记录优缺点
- 不做深入论文推导

### Deliverables
- docs/research_notes.md

### Acceptance Criteria
- 至少 2 种可实现 baseline 方案
- 有清晰对比
- 能指导模型选择

### Suggested Branch
docs

---

## Issue 0.6 — Setup Basic Dev Workflow

### Goal
建立基础开发与协作流程。

### Scope
- 确认 dev 为集成分支
- feature 分支规范（feat/*）
- commit message 规范

### Deliverables
- docs/workflow.md

### Acceptance Criteria
- 分支策略清晰
- 所有 feature 分支可合并 dev
- 无冲突流程问题

### Suggested Branch
dev

---

## Stage 1 Completion Criteria

完成以下内容即视为 Stage 1 完成：

- 项目结构初始化完成
- data 目录规范建立
- 数据成功接入并验证
- 任务定义明确
- baseline 方案已确定
- 开发流程可用

---

## Notes

Stage 1 严格限制：

- ❌ 不进行模型训练优化
- ❌ 不引入复杂 pipeline
- ❌ 不做高级特征工程

核心目标只有一个：

👉 为 Stage 2 提供“可运行的最小输入条件”
```

