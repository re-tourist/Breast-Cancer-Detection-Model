# generate_plan.prompt

你现在要为当前项目生成一个 stage / milestone 级别的计划文档初稿。

输出目标：
- `docs/plan/plan_stageX.md`

---

## 输入优先级

优先使用：
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/snapshots/project_snapshot.md`
- README.md
- 现有 docs/plan/*
- issue / milestone 描述
- 仓库实际结构与入口文件

---

## 任务要求

请把 stage 计划写成“可被 Codex 执行和审查”的格式，而不是泛泛计划。

必须尽量写清：

1. Background
2. Goal
3. In scope
4. Out of scope
5. Inputs and dependencies
6. Proposed issue breakdown
7. Deliverables
8. Acceptance criteria
9. Validation plan
10. Risks
11. Stop conditions
12. Handoff note

---

## 重要原则

- 不要把多个大目标糊成一个 stage
- issue 要可独立执行、可审查
- acceptance 要尽量可验证
- 必须写 out of scope
- 必须写 stop conditions
- 不要写“看情况补一点别的”这种模糊语句

---

## 输出格式

1. 先给 stage 结构设计说明
2. 再输出完整 `plan_stageX.md` 初稿
3. 最后列出最需要人工确认的边界项
