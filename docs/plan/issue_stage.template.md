# issue_stageX

This file lists the issues for a single stage.
Each issue should be independently executable, reviewable, and closable.

---

# Issue X.1 — <title>

## Background

Briefly explain:
- what upstream context this issue depends on
- why this issue exists in the stage
- what gap it closes

## Suggested Branch

- `feat/...` or `docs/...` or `fix/...`

## Goal

State the concrete goal in one paragraph.

Good examples:
- add the minimum runnable training entry point
- implement the dataset scanning layer
- freeze config loading behavior for the baseline
- update closeout docs for milestone transition

## In Scope

- [ ] item 1
- [ ] item 2
- [ ] item 3

## Out of Scope

- [ ] item 1
- [ ] item 2

## Relevant Files / Paths

- `...`
- `...`
- `...`

## Constraints

List hard constraints for this issue.

Examples:
- do not redesign architecture
- do not rename public entrypoints
- preserve config compatibility
- no new dependency without approval
- keep docs in sync if behavior changes

Project-specific constraints:
- Constraint 1:
- Constraint 2:

## Suggested Workflow

Recommended execution order:

1. read the relevant docs and entry files
2. inspect affected modules
3. make the smallest viable change
4. run narrow validation
5. update docs/tests if needed
6. summarize changes and risks

## Done When

This issue is done when all are true:

- [ ] result 1
- [ ] result 2
- [ ] result 3

## Required Validation

Minimum evidence required:

- command / check 1:
- command / check 2:
- manual sanity check:
- optional broader check:

## Report Format

Final report should include:

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- stop condition 1
- stop condition 2
- stop condition 3

---

# Issue X.2 — <title>

## Background

...

## Suggested Branch

- `feat/...`

## Goal

...

## In Scope

- [ ] ...
- [ ] ...

## Out of Scope

- [ ] ...
- [ ] ...

## Relevant Files / Paths

- `...`

## Constraints

- ...

## Suggested Workflow

1. ...
2. ...

## Done When

- [ ] ...

## Required Validation

- ...

## Report Format

1. ...
2. ...

## Stop and Report If

- ...
