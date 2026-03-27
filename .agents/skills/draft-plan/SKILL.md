---
name: draft-plan
description: Draft a stage or milestone plan document from project context, repository snapshot, and current task goals.
---

# draft-plan

## Purpose

Use this skill to draft `docs/plan/plan_stageX.md`.

This skill is useful when:
- the project has high-level intent but no executable stage plan
- a new milestone is about to begin
- a human wants the stage written in a Codex-friendly format
- planning should be converted into issue-ready structure

This skill writes planning documents.
It does not decide the overall project direction.

---

## Inputs

Prefer these inputs:

1. `docs/ai/PROJECT_CONTEXT.md`
2. `docs/snapshots/project_snapshot.md`
3. README and top-level docs
4. existing stage / milestone docs
5. `prompts/generate_plan.prompt.md`
6. explicit human milestone goal, if provided

If project intent is unclear, mark the uncertainty instead of inventing a stage goal.

---

## Required behavior

You must:
- keep the stage centered on one coherent objective
- define in-scope and out-of-scope explicitly
- provide deliverables and acceptance criteria
- include validation planning
- include stop conditions
- keep the stage small enough to be meaningfully reviewed

You must not:
- merge multiple large directions into one vague milestone
- leave scope boundaries implicit
- omit out-of-scope just to sound flexible
- claim that a stage is ready for execution if critical inputs are missing

---

## Output target

Primary output:
- `docs/plan/plan_stageX.md`

Optional support notes:
- missing dependencies
- boundary questions needing human confirmation
- issue split suggestions

---

## Suggested workflow

1. read `PROJECT_CONTEXT.md`
2. read `project_snapshot.md`
3. inspect current repository maturity
4. read `prompts/generate_plan.prompt.md`
5. identify one stage objective
6. define:
   - scope
   - out-of-scope
   - dependencies
   - deliverables
   - acceptance
   - risks
   - stop conditions
7. produce the stage plan
8. list the top items that still need human confirmation

---

## Quality bar

A good stage plan should:
- be executable by issue-sized chunks
- make scope boundaries obvious
- support contract freezing later
- be specific enough for implementer and reviewer use

A weak stage plan will usually:
- be too broad
- avoid concrete acceptance
- hide risk behind vague language
- fail to define what not to do
