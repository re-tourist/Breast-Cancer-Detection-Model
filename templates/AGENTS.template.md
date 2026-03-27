# AGENTS.md

## Purpose

This file is the repository-level operating manual for AI coding agents.

It defines durable working rules for normal development work in this repository.
It is not a product README and not a task-specific prompt.

Agents should use this file together with:

- `docs/ai/PROJECT_CONTEXT.md`
- `docs/plan/*`
- `docs/contracts/*`
- `docs/review/*`
- any nested `AGENTS.md` closer to the working directory

---

## Repository Summary

- Repository purpose:
- Primary language / stack:
- Repository type:
  - [ ] application
  - [ ] library
  - [ ] research repo
  - [ ] coursework repo
  - [ ] monorepo
  - [ ] tooling / infra
- Main entrypoints:
  - `...`
  - `...`

---

## Default Working Order

Follow this order unless a task explicitly requires otherwise:

1. read the relevant docs and entry files first
2. confirm the scope and affected files
3. make the smallest reasonable change
4. run the narrowest useful validation first
5. update docs/config/tests if behavior changed
6. summarize what changed, what was verified, and what remains uncertain

For multi-file, architecture-affecting, or ambiguous tasks:
- plan first
- then implement
- then review

---

## Repository Expectations

Always try to:

- preserve existing structure unless a task explicitly allows refactoring
- prefer small, reviewable diffs
- reuse existing patterns before introducing new abstractions
- keep behavior, config, and docs in sync
- report uncertainty instead of silently guessing

Do not:

- rewrite large areas without clear justification
- introduce unrelated cleanup into feature work
- silently change public behavior, contracts, or file layout
- assume missing project facts are true

---

## Key Directories and Responsibilities

### Core code
- `src/`:
- `app/`:
- `backend/`:
- `services/`:

### Docs
- `docs/ai/`:
- `docs/plan/`:
- `docs/contracts/`:
- `docs/review/`:
- `docs/handoff/`:

### Tests / validation
- `tests/`:
- `scripts/`:

### Sensitive or stable areas
- `...`
- `...`

---

## Entry Files to Read First

When entering an unfamiliar task, read these first if relevant:

- `README.md`
- `AGENTS.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `...`
- `...`

Task-specific high-value files:
- `...`
- `...`

---

## Development and Validation Commands

### Install
```bash
# fill in
