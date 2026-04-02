# generate_issue.prompt

你现在要根据已有 stage plan，为当前项目起草 `issue_stageX.md`。

目标：
把 stage 拆成若干个可执行、可验证、可 review 的 issue。

---

## 输入优先级

优先使用：
- `docs/plan/plan_stageX.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/snapshots/project_snapshot.md`
- README.md
- 当前仓库目录结构与入口文件

---

## 每个 issue 必须包含

1. Background
2. Suggested Branch
3. Goal
4. In Scope
5. Out of Scope
6. Relevant Files / Paths
7. Constraints
8. Suggested Workflow
9. Done When
10. Required Validation
11. Report Format
12. Stop and Report If

---

## 拆分原则

- issue 应该尽量独立闭环
- 不要把多个方向混进一个 issue
- 优先按模块、职责、验证闭环拆
- 一个 issue 的改动范围要尽量清晰
- issue 之间最好有自然顺序，但不要过度耦合
- 必须明确哪些内容不在本 issue 里

---

## 输出格式

1. 先给 issue 划分理由
2. 再输出完整 `issue_stageX.md` 初稿
3. 最后列出哪些 issue 需要人类先确认再交给 Codex 执行
