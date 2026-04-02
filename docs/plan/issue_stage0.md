# issue_stage0

This file captures the Stage 0 bootstrap plan that used to live under `docs/gitflow/issue/`.
It is kept under `docs/plan/` so the project has one active planning namespace.

---

## Issue 0.1 - Initialize Project Structure

- Goal: create the base repository layout for `src/`, `data/`, `scripts/`, `configs/`, `docs/`, and `outputs/`
- Deliverables: stable top-level directory layout and initial project overview in `README.md`
- Acceptance: the repo structure is clear and extendable

## Issue 0.2 - Design Data Directory Structure

- Goal: establish a consistent `data/` layout for primary and external data
- Deliverables: `data/` directory layout and `data/README.md`
- Acceptance: the data lifecycle is easy to understand and extend

## Issue 0.3 - Dataset Intake and Inspection

- Goal: verify that the course dataset can be read and inspected
- Deliverables: successful dataset load, basic stats, and a small visual inspection record
- Acceptance: images and labels can be read correctly

## Issue 0.4 - Define Task and Evaluation Protocol

- Goal: make the problem definition explicit before modeling starts
- Deliverables: `docs/task_definition.md`
- Acceptance: the task meaning and metric choice are clear

## Issue 0.5 - Minimal Research Notes for Baseline

- Goal: collect only the minimum baseline research needed to start implementation
- Deliverables: `docs/research_notes.md`
- Acceptance: the notes are enough to choose a first baseline direction

## Issue 0.6 - Setup Basic Dev Workflow

- Goal: establish the repository workflow rules for future work
- Deliverables: `docs/ai/WORKFLOW_GUIDE.md` and `AGENTS.md`
- Acceptance: the active workflow is documented in one place and does not depend on deleted gitflow paths

## Stage 0 Completion Criteria

- project structure is initialized
- data directory rules exist
- raw data can be inspected
- task definition is documented
- a baseline direction is recorded
- the repository workflow is usable
