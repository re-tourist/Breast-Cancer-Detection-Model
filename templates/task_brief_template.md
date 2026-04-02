# task_brief

## Task Identity

- Task title:
- Task type:
  - [ ] issue implementation
  - [ ] milestone execution
  - [ ] review
  - [ ] documentation
  - [ ] refactor
  - [ ] debugging
  - [ ] investigation
- Related stage / milestone:
- Related issue:
- Suggested branch:
- Requested by:

---

## 1. Goal

请用 2–5 句话说明本任务要达成什么。

只写这次任务的直接目标，不要展开整个项目背景。

建议回答：
- 这次要交付什么
- 这次不需要解决什么
- 这次完成后，项目会前进一步到哪里

---

## 2. Primary Context

本任务优先参考的文档和文件：

### Must read first
- `AGENTS.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `...`

### Task-specific docs
- `docs/plan/...`
- `docs/contracts/...`
- `docs/review/...`

### Code / config entrypoints
- `...`
- `...`

如果某个文档不存在，请明确写：
- missing / needs creation

---

## 3. Scope

### In scope
- [ ] item 1
- [ ] item 2
- [ ] item 3

### Out of scope
- [ ] item 1
- [ ] item 2
- [ ] item 3

这部分必须明确，避免 agent 顺手扩 scope。

---

## 4. Constraints

本任务必须遵守的硬约束：

- Constraint 1:
- Constraint 2:
- Constraint 3:

常见例子：
- 不改 public API
- 不改 stable file layout
- 不加依赖
- 不改 evaluation semantics
- 不做大重构
- 只在指定目录改动

---

## 5. Expected Deliverables

本任务交付物包括：

- [ ] code
- [ ] docs
- [ ] config
- [ ] tests
- [ ] validation evidence
- [ ] review note
- [ ] handoff note

具体说明：
- Deliverable 1:
- Deliverable 2:

---

## 6. Validation Requirements

本任务最低验证要求：

### Narrow checks
- command / check 1:
- command / check 2:

### Manual sanity checks
- check 1:
- check 2:

### Optional broader checks
- check 1:
- check 2:

如果验证无法完成，请在最终汇报中明确说明。

---

## 7. Stop Conditions

出现以下任一情况时，不要继续推进，请停止并汇报：

- stop condition 1:
- stop condition 2:
- stop condition 3:

常见例子：
- 需要改 frozen contract
- 需要加依赖
- 需要扩大 milestone scope
- 现有验证与目标语义冲突
- 找不到关键入口文件或关键配置

---

## 8. Final Report Format

任务完成后，请按以下格式汇报：

1. Files changed
2. What changed in each file
3. Validation run
4. Risks / uncertainties
5. Whether scope stayed intact
6. Suggested next step

---

## 9. Human Decision Needed After Completion

本任务完成后，是否需要人工做以下判断：

- [ ] 是否进入下一个 issue
- [ ] 是否更新 contract freeze
- [ ] 是否接受当前验证为足够
- [ ] 是否改变 milestone 优先级
- [ ] 是否继续推进到下个阶段

补充说明：
- decision 1:
- decision 2:
