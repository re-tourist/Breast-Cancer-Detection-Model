# contract_freeze

## Contract Title

- Contract ID: M2-paired-baseline-freeze-001
- Related stage / milestone: M2 / first credible breast-level baseline
- Status:
  - [ ] proposed
  - [x] frozen
  - [ ] revised
  - [ ] retired
- Owner: human project owner
- Last updated: 2026-03-27

## 1. Purpose

This contract freeze exists to lock the current working boundary for Stage 2.

Its purpose is to prevent:

- silent scope drift
- accidental interface changes
- semantic changes hidden inside “small implementation tweaks”
- repeated redesign during an execution phase

This document is not a full design spec.
It is a boundary document.

---

## 2. What This Contract Covers

Current contract scope:

- the Stage 2 paired breast-level baseline
- `breast_id`-grouped train / validation usage
- stage artifact locations and output meaning
- evaluation meaning centered on breast-level AUROC
- the current fallback relationship between the single-image path and the paired mainline

## 3. Frozen Objectives

The following goals are fixed for this stage:

- build the first credible breast-level baseline on paired CC/MLO views
- preserve leakage-safe validation grouped by `breast_id`
- produce reproducible training and evaluation artifacts that can be reviewed later

These objectives must not be reinterpreted during normal implementation work.

If execution reveals they are no longer valid, stop and report instead of redefining them silently.

---

## 4. Frozen Inputs / Outputs

Define the stable meaning of inputs and outputs in this stage.

### Inputs

- Input A:
  - source: `data/raw/primary/` through generated indexes and split artifacts
  - expected form: strict paired CC/MLO examples keyed by `breast_id`
  - meaning: one breast-level training example
- Input B:
  - source: `data/processed/metadata/*` and `data/processed/splits/*`
  - expected form: generated index and split artifacts
  - meaning: reproducible dataset and validation layout

Paired-input contract:

- paired mode accepts only complete two-view samples with one `CC` image and one `MLO` image for the same `breast_id`
- incomplete samples must not be silently repaired by copying a view, fabricating a pair, or choosing an arbitrary second image
- invalid paired candidates must be filtered during index/data-build time and their counts must be reported explicitly
- paired view order is frozen as `(CC, MLO)` and must remain stable through dataset loading, model forward, evaluation, and artifact export

### Outputs

- Output A:
  - location / API / artifact: `outputs/m2_baseline/`
  - expected form: config snapshot, checkpoint, logs, and metrics summary
  - meaning: reproducible baseline run artifacts
- Output B:
  - location / API / artifact: `outputs/m2_baseline/eval/`
  - expected form: breast-level predictions and breast-level metrics for paired mode; image-level predictions remain single-path-only artifacts
  - meaning: reviewable evaluation output for the Stage 2 baseline
- Output C:
  - location / API / artifact: `outputs/m2_smoke/`
  - expected form: smoke-run logs and sanity report
  - meaning: narrow end-to-end evidence for the stage

If an implementation needs to change any of the above, it must trigger a freeze review.

---

## 5. Frozen Interfaces

List interfaces that must remain stable during this stage.

Frozen interfaces:

- `breast_id` remains the grouping key for validation and reporting
- breast-level output semantics remain the primary evaluation meaning
- output artifacts remain repository-relative and human reviewable
- evaluation output columns remain compatible with `breast_id` and predicted score semantics
- any CLI/config switches that select the paired baseline must preserve the documented meaning of the run
- paired-mode `prediction` exports represent sigmoid probabilities in `[0, 1]`, not raw logits
- paired-mode breast-level export rows preserve `CC` first and `MLO` second in all paired identifiers and image paths

Allowed tolerance:

- minor internal refactor that preserves interface meaning
- doc clarification without semantic change
- non-breaking validation additions

Not allowed:

- renaming without approval
- silent semantic drift
- hidden behavior changes behind the same interface
- exporting logits under the `prediction` column name
- swapping `CC` and `MLO` semantics in any intermediate layer while keeping the same field names

---

## 6. Allowed Change Window

The following changes are allowed within this frozen stage:

- implementation detail improvements that do not change semantics
- focused bug fixes that restore intended behavior
- additional tests / validation
- documentation sync
- narrow refactors that preserve interfaces and outputs

Project-specific allowed changes:

- improve paired-view model internals without changing the breast-level output meaning
- refine logging or checkpoint cadence without changing artifact semantics
- add explicit reporting for filtered invalid paired samples without relaxing the strict paired-sample contract

This section is important:
it tells agents where they still have execution freedom.

---

## 7. Explicitly Forbidden Changes

The following changes must not be made during this stage without explicit approval:

- changing the task from breast-level classification to detection / segmentation
- changing label semantics away from `M` vs `B + N`
- introducing image-level train/validation leakage
- changing the stable output meaning or artifact layout without review
- adding major dependencies
- silently repairing incomplete paired samples at runtime
- reordering paired view semantics away from frozen `(CC, MLO)` order
- reinterpreting the milestone goal as “just get something running”

Common examples:

- redesigning architecture mid-stage
- changing output meaning
- changing evaluation criteria
- changing stable config semantics
- moving major directories
- adding major dependencies
- reinterpreting milestone goals

---

## 8. Validation Contract

The following validation expectations are frozen for this stage:

- required local checks:
  - `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1 --save-preview`
  - `python scripts/build_dataset_index.py`
  - `python scripts/build_splits.py`
- required focused tests:
  - `python -m unittest tests.test_datasets`
  - `python -m unittest tests.test_splits`
  - `python -m unittest tests.test_split_fold_assignment`
  - `python -m unittest tests.test_eval`
  - `python -m unittest tests.test_training_smoke`
- required manual sanity checks:
  - confirm paired CC/MLO alignment for the same `breast_id`
  - confirm invalid paired candidates are filtered or rejected explicitly rather than silently repaired
  - confirm paired export rows preserve `CC`/`MLO` order in identifiers and image paths
  - inspect prediction spread and label alignment
  - confirm breast-level evaluation output is not collapsed into a meaningless constant
  - confirm exported `prediction` values are sigmoid probabilities in `[0, 1]`
- optional broader checks:
  - `python -m unittest`

A task cannot be called complete if it violates these minimum validation expectations.

---

## 9. Stop Conditions

If any of the following happen, stop and report:

- the implementation cannot proceed without changing a frozen interface
- validation evidence contradicts the frozen objective
- the requested task implies scope expansion beyond this contract
- missing upstream dependency makes the contract impossible to honor
- semantic correctness becomes uncertain in a way that tests do not catch

Project-specific stop conditions:

- Stop condition 1: paired data cannot be used without leakage-safe grouping
- Stop condition 2: the stage would need a task-definition or label-semantic change
- Stop condition 3: the paired pipeline cannot preserve the frozen `(CC, MLO)` ordering contract end to end
- Stop condition 4: evaluation artifacts would need to blur probability-vs-logit semantics

---

## 10. Change Control

If someone believes this contract must change, do not silently edit code first.

Use this process:

1. identify the exact frozen item that is no longer viable
2. explain why it blocks execution or correctness
3. propose the smallest necessary revision
4. obtain human approval
5. update this contract explicitly before continuing

Normal implementation work must not bypass this process.

---

## 11. Linked Documents

Relevant docs:

- `docs/ai/PROJECT_CONTEXT.md`
- `docs/plan/plan_stage2.md`
- `docs/review/code_review.md`
- `docs/handoff/stage1_handoff.md`
- `docs/handoff/stage1_closeout.md`

Project-specific links:

- `README.md`
- `data/README.md`
- `docs/task_definition.md`
- `docs/plan/minimal_system_design.md`

---

## 12. Freeze Review Notes

Use this section to track boundary decisions over time.

### Review entry

- date: 2026-03-27
- requested by: repository bootstrap / Stage 2 planning
- issue: define the first paired breast-level baseline without drifting away from the breast-level task
- proposed change: freeze the paired baseline, artifact layout, and validation contract
- decision: frozen
- rationale: Stage 2 implementation proceeds only with strict paired samples, fixed `(CC, MLO)` ordering, and probability-typed paired exports

Add one entry per boundary-level change request.
