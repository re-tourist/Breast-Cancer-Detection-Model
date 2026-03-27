# generate_project_context.prompt

你现在要为当前项目生成一份 `docs/ai/PROJECT_CONTEXT.md` 初稿。

目标：
把“项目高层意图”和“agent 执行边界”写清楚，供后续 Codex 执行时长期参考。

---

## 你的任务

请根据以下信息源尽可能生成初稿：

- README.md
- docs/*
- 现有计划文档
- issue / milestone 描述
- 仓库结构
- 若有 project_snapshot.md，也要使用

如果某些高层意图无法从仓库确认，请明确标为：
- needs human confirmation

---

## 重点要写清楚的内容

1. 项目是什么
2. 当前阶段是什么
3. 这一阶段想证明或交付什么
4. 什么由人类负责，不应由 agent 擅自决定
5. 什么由 agent 执行
6. 有哪些长期约束
7. 当前阶段的成功标准
8. 哪些情况必须 stop and report
9. 重要文档和重要文件入口
10. 推荐的汇报偏好

---

## 风格要求

- 比 README 更偏执行边界
- 比 AGENTS.md 更偏项目语义
- 不要写泛泛背景介绍
- 对不确定内容要诚实标注
- 尽量用结构化模板输出

---

## 输出格式

1. 先给“可确认信息”和“需要人工确认的信息”
2. 再输出完整的 `PROJECT_CONTEXT.md` 初稿
3. 最后列出 3–8 个最值得人工补充的问题
