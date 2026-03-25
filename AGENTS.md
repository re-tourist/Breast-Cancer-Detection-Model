# AGENTS.md

## Project Overview
This repository is a course project for breast cancer detection using deep learning.

Current focus:
- bootstrap the repository
- define data conventions
- inspect the dataset
- define task and evaluation protocol
- prepare for a minimal baseline

At the current stage, prioritize clarity, extensibility, and reproducibility over model complexity.

---

## Current Stage Boundary

This repository is currently in an early project-bootstrap stage.

Allowed:
- create and refine project structure
- define data directory conventions
- write project documentation
- implement lightweight dataset inspection utilities
- clarify task definition and evaluation protocol
- improve README, .gitignore, and developer workflow docs

Not allowed unless explicitly requested:
- large-scale model training
- aggressive optimization
- complicated pipeline design
- premature abstraction for future stages
- introducing many dependencies without a clear need

When uncertain, prefer the smallest clean solution that keeps the next stage unblocked.

---

## Primary Goals at This Stage

The agent should help the repository reach these outcomes:

1. clear repository structure
2. clean data directory design
3. successful dataset intake and basic inspection
4. explicit task definition
5. explicit evaluation protocol
6. readable README and maintainable dev workflow

Do not drift into later-stage modeling work unless the user explicitly asks for it.

---

## Instruction Priority

When working in this repo, use this priority order:

1. direct user request
2. this AGENTS.md
3. stage planning documents in `docs/` or project root
4. existing code conventions
5. default framework conventions

If instructions conflict, do not guess silently. State the conflict clearly.

---

## How to Read the Repository Before Editing

Before making non-trivial changes:

1. read `README.md` if present
2. read stage planning documents relevant to the task
3. inspect the target directory before creating new files
4. reuse existing naming and layout whenever possible

Do not create parallel structures without a strong reason.

Examples of bad behavior:
- creating a new directory tree when an existing one already fits
- duplicating task definitions in multiple files
- adding scripts that hardcode personal paths

---

## Repository Design Principles

### 1. Prefer simple and conventional structure
Use a minimal structure that is easy to understand and easy to extend.

### 2. Separate concerns clearly
Keep data rules, task definition, model code, training code, and evaluation code logically separated.

### 3. Reproducibility first
Any script that inspects or prepares data should be rerunnable and should avoid hidden assumptions.

### 4. Avoid hardcoded paths
Use repository-relative paths, config files, or clearly defined constants.

### 5. Document decisions
If a design choice affects future work, record it in Markdown rather than leaving it implicit in code.

---

## Directory Guidance

Typical expected top-level layout may include:

- `src/` or `models/` for source code
- `data/` for dataset storage conventions
- `scripts/` for runnable utilities
- `configs/` for configuration files
- `docs/` for planning, task definition, workflow, and research notes
- `outputs/` for generated artifacts
- `tests/` for lightweight validation where appropriate

The agent should not force a large architecture too early.
If only a minimal structure is needed for the current stage, keep it minimal.

---

## Data Handling Rules

Data organization must be explicit and extensible.

Preferred principles:
- separate raw / interim / processed data when relevant
- distinguish official/course data from external data when relevant
- keep metadata, splits, and cache conceptually separate
- never commit large raw datasets unless explicitly intended
- document expected file locations in Markdown

If the dataset is first being integrated:
- inspect actual filenames and label files before defining loaders
- summarize image format, labels, class balance, and anomalies
- do not assume binary/multiclass details without checking

---

## Documentation Rules

When writing documentation:

- explain what the file is for
- explain what is in scope and out of scope
- prefer concrete bullets/checklists over vague prose
- keep terminology consistent across README, docs, and scripts
- update docs when code structure changes

Important:
- README should explain what the project does now, not what it may do one month later
- avoid fake completeness
- mark placeholders clearly if something is intentionally unfinished

---

## README Expectations

A good README at this stage should cover:

1. project purpose
2. current stage and scope
3. repository structure
4. data organization
5. setup instructions
6. minimal usage instructions
7. current progress
8. next planned steps

README should be honest about what is already implemented and what is not yet implemented.

---

## .gitignore Expectations

At minimum, ignore:
- Python cache files
- virtual environments
- notebook checkpoints
- OS/editor junk
- large data directories when appropriate
- generated outputs
- model checkpoints
- experiment logs

Do not ignore source code, configs, or essential small documentation files.

---

## Coding Rules

For Python code:
- prefer readable, explicit code
- add short docstrings for non-trivial functions
- avoid overengineering
- keep functions small and testable
- use clear naming
- avoid magic numbers when a named constant is clearer

For scripts:
- make inputs/outputs explicit
- print concise summaries of what the script did
- fail loudly on missing required files
- do not silently swallow exceptions

---

## Evaluation and Task Definition Rules

When working on task definition or evaluation documents:

- explicitly define the task type
- explicitly define input format
- explicitly define label format
- explicitly define train/val/test assumptions if known
- explicitly define primary metrics
- mention secondary metrics if useful
- explain why the chosen metrics are appropriate

Do not list metrics mechanically.
Tie metrics to the task and dataset characteristics.

---

## Git and Change Discipline

Prefer small, focused changes.

When making edits:
- do not mix unrelated refactors into a task
- preserve existing user work
- do not rename files casually
- do not rewrite structure unless necessary

If a task touches multiple files, keep the change logically coherent.

Suggested branch intent from current planning:
- data-related work -> `feat/data`
- structure/scripts/bootstrap work -> `feat/scripts`
- documentation-heavy work -> `docs`
- integration happens on `dev`

If the current checked-out branch does not match the task, warn before making broad changes.

---

## When the Agent Should Ask for Clarification

Ask before proceeding when:
- the real dataset layout conflicts with documented assumptions
- there are multiple equally plausible repository structures
- a request would introduce major new dependencies
- a request crosses the current stage boundary significantly
- the intended source directory (`src/` vs `models/`) is ambiguous and would affect many files

Do not ask for clarification on minor naming choices if the planning docs already imply a reasonable answer.

---

## What “Good Output” Looks Like in This Repo

A good contribution in this repository usually has these traits:

- aligned with the current stage
- small but complete
- documented
- reproducible
- easy to review
- leaves the repo cleaner than before

---

## Preferred Working Style for This Repo

When given a task:
1. restate the concrete goal briefly
2. inspect existing relevant files
3. make the minimum high-confidence changes
4. summarize what changed
5. mention any assumptions or follow-up risks

Do not pretend something was verified if it was not actually verified.

---

## If You Update This File

Update this AGENTS.md when:
- the same mistake happens more than once
- a repo convention becomes stable
- a directory needs local rules
- stage focus changes materially