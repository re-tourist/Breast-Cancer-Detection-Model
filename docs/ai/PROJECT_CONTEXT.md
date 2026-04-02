# PROJECT_CONTEXT

## 1. Project Summary

- Project name: Breast Cancer Detection Model
- Project type:
  - [ ] research
  - [ ] product
  - [x] coursework
  - [x] prototype
  - [ ] infrastructure
- One-sentence description: Stage 1 minimal runnable pipeline for breast-level malignant probability prediction from mammography images.
- Primary language / stack: Python, PyTorch, NumPy, Pillow, scikit-learn

## 2. Current Phase

- Current milestone / stage: Milestone 2 active execution for the first paired baseline
- Why this stage exists: Stage 1 proved the pipeline can ingest data, split by `breast_id`, train, evaluate, and smoke-test end to end; Stage 2 should move from structural proof to the first credible breast-level baseline.
- What this stage should prove or deliver: a leakage-safe paired CC/MLO baseline, reproducible training/evaluation artifacts, and a clear handoff to the next milestone.
- What is explicitly out of scope in this stage:
  - detection / segmentation as the main task
  - external data mixing without approval
  - heavy experiment-management frameworks
  - long hyperparameter search or benchmark tuning
  - changing the task definition or split protocol

## 3. High-Level Goal

The project goal is breast-level binary classification for malignancy from mammography images.

What matters most at this stage:

- preserve breast-level semantics end to end
- keep `breast_id` grouping leakage-safe
- produce reproducible artifacts and validation evidence
- move toward a stronger paired-view baseline instead of polishing the weak single-image fallback
- keep paired inputs strict: no fake view completion, no silent sample repair
- preserve frozen `(CC, MLO)` ordering through dataset, model, eval, and exports
- keep exported paired predictions interpretable as malignant probabilities

The project is not trying to become a full research platform yet. The current priority is correctness, reproducibility, and a handoff-friendly baseline that can be reviewed and extended safely.

## 4. Human-Owned Decisions

These areas are owned by the human and should not be changed by agents without approval:

- research / product direction: whether the project continues as breast-level malignant probability prediction and what future baseline family is prioritized
- milestone boundaries: what is considered Stage 2 complete versus deferred
- contract freeze: which interfaces, artifacts, and semantics are frozen for the active stage
- evaluation criteria: which metrics and checks count as acceptable evidence
- release / submission decisions: when a result is meaningful enough to treat as a real baseline
- public API / external commitments: CLI behavior, file layout, and output schema

## 5. Agent-Owned Execution Scope

Agents are expected to help with:

- code implementation
- refactor within approved scope
- tests / validation
- local documentation sync
- issue-level execution
- milestone-level closeout drafting

Agents are not expected to decide:

- whether the overall direction is correct
- whether a failed result invalidates the project hypothesis
- whether to expand scope
- whether to change the meaning of success

## 6. Project Constraints

Project-specific constraints:

- keep `breast_id`-grouped splits and fold assignment leakage-safe
- do not modify `data/raw/primary/` in place
- keep generated metadata and split artifacts under `data/processed/`
- keep outputs repository-relative under `outputs/`
- prefer minimal viable implementation before optimization
- avoid adding dependencies or large frameworks unless explicitly approved
- preserve breast-level evaluation semantics even if a single-image fallback remains available for diagnostics
- paired mode accepts only strict complete `(CC, MLO)` samples
- invalid paired candidates must be filtered or rejected explicitly, never silently repaired
- paired artifact exports must preserve `(CC, MLO)` order and probability semantics

## 7. Success Criteria for This Phase

A phase is considered successful when:

- [ ] a paired breast-level baseline can train and evaluate without changing the task definition
- [ ] breast-level predictions and metrics are written to reproducible artifacts
- [ ] leakage-safety is preserved by `breast_id`-grouped validation
- [ ] paired-mode exports preserve frozen `(CC, MLO)` order and `prediction` means sigmoid probability

Optional quantitative gates:

- metric / threshold: breast-level AUROC is reported on grouped validation; no fixed target threshold has been frozen yet
- runtime / cost budget: keep a narrow smoke-sized validation path available
- reproducibility requirement: the same split and config inputs produce the same artifact layout and comparable outputs

## 8. Stop Conditions

If any of these happen, the agent should stop and report instead of pushing forward:

- required files, configs, or data artifacts are missing
- the requested change would violate a frozen contract or require changing task meaning
- paired-view implementation would introduce image-level leakage
- the solution requires unapproved dependencies or a major architecture rewrite
- validation results contradict the task definition or evaluation semantics
- paired mode would require runtime auto-repair for incomplete paired samples
- exported paired predictions can no longer be stated honestly as probabilities

## 9. Important Files and Docs

Core files:

- `README.md`
- `data/README.md`
- `docs/ai/WORKFLOW_GUIDE.md`
- `docs/task_definition.md`
- `docs/plan/minimal_system_design.md`
- `docs/handoff/stage1_handoff.md`
- `docs/handoff/stage1_closeout.md`
- `scripts/build_dataset_index.py`
- `scripts/build_splits.py`
- `scripts/check_dataset_loading.py`
- `scripts/train_baseline.py`
- `scripts/run_eval.py`
- `scripts/run_stage1_smoke.py`
- `scripts/run_stage2_smoke.py` if introduced during Stage 2 execution

Planning docs:

- `docs/snapshots/project_snapshot.md`
- `docs/plan/plan_stage2.md`
- `docs/plan/issue_stage2.md`

Contracts / review docs:

- `docs/contracts/contract_freeze_stage2.md`
- `docs/review/code_review.md`

## 10. Reporting Preference

When reporting progress, prefer this style:

- concise factual summary
- changed files first
- validation second
- open risks last
- do not overclaim certainty
