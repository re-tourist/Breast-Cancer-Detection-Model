---
name: draft-agents-md
description: Draft or rewrite a repository-level AGENTS.md by combining repository evidence, existing docs, project snapshot, and the stored AGENTS meta prompt.
---

# draft-agents-md

## Purpose

Use this skill to draft or improve a project-level `AGENTS.md`.

This skill is appropriate when:
- a repository does not have an AGENTS.md
- the existing AGENTS.md is stale, vague, or too task-specific
- a project has been scanned and now needs durable agent rules
- a human wants to reduce repeated prompt-based orchestration

This skill produces a repository operating guide, not a project README.

---

## Inputs

Prefer these inputs, in order:

1. repository structure and key files
2. `docs/snapshots/project_snapshot.md`
3. `README.md`
4. existing `AGENTS.md` or similar rule files
5. docs under `docs/`
6. `prompts/generate_agents_md.prompt.md`

If some inputs are missing, proceed conservatively.

---

## Required behavior

You must:
- ground the output in repository evidence
- avoid invented commands or policies
- keep the result short, durable, and execution-oriented
- prefer practical instructions over generic advice
- clearly separate confirmed facts from uncertain recommendations

You must not:
- turn AGENTS.md into a task-specific implementation plan
- duplicate large portions of README
- include speculative repo facts as if they were confirmed

---

## Output target

Primary output:
- root `AGENTS.md`

Optional supporting output:
- short notes about missing docs or places where nested AGENTS.md may be useful

---

## Preferred structure of the generated AGENTS.md

The generated file should usually cover:

1. purpose
2. default working order
3. repo expectations
4. always allowed / ask first / never do
5. validation strategy
6. done definition
7. documentation sync rules
8. reporting format
9. ambiguity handling
10. where to move more specialized rules later

Keep it concise.

---

## Suggested workflow

1. read `project_snapshot.md` if present
2. inspect README and top-level docs
3. inspect build/test/lint/config signals
4. identify stable areas, risky areas, and likely entrypoints
5. read `prompts/generate_agents_md.prompt.md`
6. draft `AGENTS.md`
7. make sure the draft is:
   - repo-grounded
   - compact
   - useful for future execution
8. report what remains uncertain

---

## Quality bar

A good result should:
- reduce future manual context rewriting
- help implementer and reviewer behave consistently
- reflect the repository as it actually is
- remain useful across many tasks

A bad result will usually:
- be too long
- be too generic
- be too promotional
- contain commands or rules not supported by repository evidence
