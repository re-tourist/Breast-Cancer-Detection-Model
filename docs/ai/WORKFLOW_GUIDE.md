# WORKFLOW_GUIDE

## Purpose

This is the canonical workflow for this repository.

Use it together with:

- `AGENTS.md` for repo-level operating rules
- `docs/ai/PROJECT_CONTEXT.md` for project intent and stage boundaries
- `docs/plan/*`, `docs/contracts/*`, `docs/review/*`, and `docs/handoff/*` for stage execution

If another workflow doc conflicts with this one, this one wins.

Older branch notes were retired from the active docs and should not be used as workflow source.

---

## Canonical Sources

Agents should treat the repository as the source of truth. Do not rely on chat history or repeated manual prompt rewriting.

Use these docs in order when starting non-trivial work:

1. `README.md`
2. `AGENTS.md`
3. `docs/ai/WORKFLOW_GUIDE.md`
4. `docs/ai/PROJECT_CONTEXT.md`
5. `docs/snapshots/project_snapshot.md`
6. stage plan and issue docs
7. contract freeze docs
8. review docs
9. handoff / closeout docs

---

## Role Split

### Human owns

- project goal
- milestone design
- issue acceptance
- contract freeze
- evaluation meaning
- research / product direction
- final go / no-go decisions

### Implementer owns

- scoped implementation
- narrow validation
- docs / config / test sync
- structured execution report

### Reviewer owns

- scope review
- contract review
- validation review
- semantic risk review
- structured approve / revise / stop recommendation

---

## Branching and Merge Policy

This repository uses a small set of long-lived working branches:

- `main`: stable snapshot branch
- `dev`: integration branch
- `docs`: documentation branch
- `feat/*`: feature branches for focused code work

Branch selection rules:

- documentation-only work: `docs`
- dataset, manifests, or inspection work: `feat/data`
- scripts and bootstrap work: `feat/scripts`
- model work: `feat/model`
- evaluation work: `feat/eval`
- training work: `feat/train`
- integration work across completed issues: `dev`

Merge policy:

- merge working branches into `dev` first
- merge `dev` into `main` only after a milestone is stable
- keep each merge focused on one issue or a tightly related group
- resolve conflicts on the source branch before merging

Naming and commit conventions:

- keep branch names short and module-oriented
- use `feat/<area>` for code branches
- keep `docs` as the documentation branch
- avoid nested `docs/*` branch names when `docs` is the real branch name
- use commit messages of the form `<branch>(<scope>): <action> <stage/issue> <summary>`

---

## Standard Lifecycle

### Discover

Before changing anything, read the relevant repo docs and entrypoints.

Minimum order:

1. `AGENTS.md`
2. `docs/ai/PROJECT_CONTEXT.md`
3. `docs/snapshots/project_snapshot.md`
4. the relevant stage / issue / contract docs
5. the relevant `scripts/*.py` entrypoint
6. the backing `src/*` modules

### Plan

Before coding a new stage or issue:

1. write or update `docs/plan/plan_stageX.md`
2. split the stage into `docs/plan/issue_stageX.md`
3. confirm scope, ordering, deliverables, and stop conditions

### Freeze

Before active execution begins:

1. create or update `docs/contracts/contract_freeze_*.md`
2. lock the stage objective, inputs, outputs, interfaces, and validation expectations
3. stop if the work would need to change the frozen boundary

### Execute

For each issue:

1. make the smallest viable change
2. keep the change local to the issue scope
3. run narrow validation first
4. sync docs/tests/config if behavior changed
5. write a structured issue report or PR description

### Review

Review should check:

- scope drift
- contract violations
- validation adequacy
- docs/config mismatch
- semantic correctness risk

Review output should be one of:

- approve
- revise
- stop

### Closeout

When a milestone is done or paused:

1. update `docs/handoff/milestone_closeout*.md`
2. record completed work, missing work, risks, and the next entry point
3. decide whether the milestone can be closed cleanly

---

## PR / Issue / Milestone Artifacts

Use the repo templates and docs to keep reports consistent:

- PRs should use the GitHub default template in `.github/pull_request_template.md`
- `templates/PR_TEMPLATE.md` is a reusable reference copy, not the canonical PR entrypoint
- issue-level execution should be summarized with changed files, validation, risks, and next step
- milestone closeout should state what was completed, what remains, and whether the next stage can start cleanly

If workflow behavior changes, update the canonical workflow docs in the same change.

---

## Failure Signs

The workflow is not working well if:

- humans still rewrite long prompts every time
- agents ignore `AGENTS.md`
- reviewer only repeats the implementer summary
- scope drift happens frequently
- contract docs exist but do not affect behavior
- docs are present but never referenced during execution

---

## How to Evolve

Only add new workflow rules after repeated real use shows a need.

Good candidates for later expansion:

- more reusable skills
- nested `AGENTS.md`
- CI-triggered reviews
- project-type specializations
- richer repo snapshot automation
- plan / issue drafting skills
- milestone review automation

Do not expand just because it sounds useful. Expand after repeated friction shows what is actually reusable.
