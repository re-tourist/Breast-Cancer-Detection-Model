# Git Workflow

## Purpose

This document defines the current Git workflow for this repository during Stage 0 and the early baseline stage.

It focuses on:
- branch responsibilities
- branch naming and usage rules
- commit message conventions
- merge rules into `dev`
- the preferred issue description format used in this project

Out of scope:
- release automation
- semantic versioning
- complex GitFlow release or hotfix branches

## Branch Roles

Current branch layout:

- `main`: stable snapshot branch; update only after `dev` reaches a clean milestone
- `dev`: integration branch; all issue-level work is merged here first
- `docs`: documentation branch for README, plans, task definitions, workflow notes, and other doc-only changes
- `feat/scripts`: lightweight scripts and repository bootstrap utilities
- `feat/data`: data intake, data rules, manifests, and inspection-related work
- `feat/model`: model structure or baseline model code when Stage 1 begins
- `feat/eval`: evaluation code, metrics, and reporting utilities
- `feat/train`: training entrypoints and training-loop-related code

Current merge direction:

- `docs` -> `dev`
- `feat/scripts` -> `dev`
- `feat/data` -> `dev`
- `feat/model` -> `dev`
- `feat/eval` -> `dev`
- `feat/train` -> `dev`
- `dev` -> `main` only when a stage milestone is considered stable

## Branch Selection Rules

Use the branch that best matches the dominant scope of the issue:

- documentation-only changes: `docs`
- dataset layout, manifests, or inspection changes: `feat/data`
- utility scripts or repo bootstrap changes: `feat/scripts`
- model implementation work: `feat/model`
- evaluation or metrics work: `feat/eval`
- training entrypoints or loops: `feat/train`
- integration work across completed issue branches: `dev`

If one issue touches code and docs together, prefer the branch that owns the code and include the necessary doc update in the same change.

## Naming Rules

The repository currently uses fixed long-lived working branches instead of creating a new branch for every issue.

Rules:

- keep branch names short and module-oriented
- prefer `feat/<area>` for code branches
- keep `docs` as a dedicated documentation branch
- do not create nested branches under an existing non-prefix branch

Important Git note:

- do not create `docs/*` while `docs` already exists
- a branch like `docs/update` blocks creation or reuse of `docs` because Git stores refs as paths

Examples:

- valid: `docs`
- valid: `feat/data`
- valid: `feat/scripts`
- invalid in this repo: `docs/update`

## Standard Workflow

Recommended issue workflow:

1. update the integration branch
2. switch to the branch that owns the issue
3. sync that branch from `dev`
4. make one focused issue-sized change
5. merge the branch back into `dev`

Example for a documentation issue:

```bash
git switch dev
git pull
git switch docs
git merge dev

# make changes
git add docs/gitflow/workflow.md README.md
git commit -m "docs(workflow): define Stage 0 issue 0.6 basic dev workflow"

git switch dev
git merge docs
```

If the branch has several temporary commits for one issue, a squash merge into `dev` is preferred to keep the integration history readable.

## Commit Message Convention

Use this format:

```text
<branch>(<scope>): <action> <stage/issue> <summary>
```

Guidelines:

- use the receiving branch name as the prefix
- keep `<scope>` short and concrete
- start the summary with a verb
- mention the stage or issue number when it adds useful context
- keep one logical change per commit

Examples:

- `docs(workflow): define Stage 0 issue 0.6 basic dev workflow`
- `feat/data(intake): inspect Stage 0 issue 0.2 dataset layout`
- `feat/scripts(bootstrap): add dataset inspection entrypoint`
- `dev(merge): integrate docs workflow for Stage 0 issue 0.6`

## Merge Rules

- all working branches merge into `dev` before anything reaches `main`
- do not merge `docs` or `feat/*` directly into `main`
- keep each merge focused on one issue or one tightly related issue group
- resolve conflicts on the source branch before merging into `dev`
- update related docs in the same change when the workflow or structure changes

At the current project stage, simplicity is preferred over a complex release model.

## Issue Description Template

When opening or documenting an issue result, use a compact title plus `what` and `why`.

Recommended title format:

```text
<branch>(<scope>): <action> <stage/issue> <summary>
```

Recommended body format:

```text
what:
- concrete deliverable 1
- concrete deliverable 2

why:
- reason 1 tied to the current stage
- reason 2 tied to reproducibility, clarity, or integration
```

Example:

```text
docs(workflow): define Stage 0 issue 0.6 basic dev workflow

what:
- add docs/gitflow/workflow.md to document branch roles, merge path, and commit rules
- align README and issue notes with the new workflow document

why:
- make the collaboration process explicit before Stage 1 code work starts
- reduce branch confusion and avoid repeat ref conflicts such as docs vs docs/*
```

## Project-Specific Conventions

The current repository conventions are:

- `dev` is the integration branch
- `docs` is a real working branch, not a branch prefix
- `feat/*` branches are organized by responsibility, not by temporary ticket number
- issue-level changes should stay small and reviewable
- documentation should be updated whenever a workflow rule becomes stable
- branch and commit names should describe the actual repository state, not future plans

These rules are intentionally simple so Stage 0 and Stage 1 work can move forward without extra process overhead.
