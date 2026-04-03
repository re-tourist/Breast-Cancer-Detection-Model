# AGENTS.md

## Purpose

- Repo-level operating manual for AI coding agents working in this repository.
- This is a single-package Python project for breast cancer detection work: Stage 1 established a minimal runnable pipeline, and Stage 2 has now closed on a stricter paired breast-level baseline.
- Use this file for durable execution rules. Use `README.md` and `docs/` for human-oriented project context.

## Current Boundary

- Treat the repository as a Stage 1 foundation with a completed Stage 2 paired-baseline boundary:
  - dataset inspection and indexing
  - `breast_id`-grouped split generation
  - the current single-image fallback path
  - breast-level aggregation and evaluation
  - smoke-tested artifact generation
  - the strict paired CC/MLO Stage 2 baseline path
- For M2-style paired-baseline work or follow-up changes, follow the Stage 2 plan, issue breakdown, contract freeze, and closeout instead of improvising.

## Read First

Read in this order before non-trivial changes:

1. `README.md`
2. `docs/ai/WORKFLOW_GUIDE.md`
3. `data/README.md`
4. `docs/task_definition.md`
5. `docs/handoff/stage1_handoff.md`
6. `docs/ai/PROJECT_CONTEXT.md`
7. `docs/snapshots/project_snapshot.md`
8. `docs/plan/plan_stageX.md`
9. `docs/plan/issue_stageX.md`
10. `docs/contracts/contract_freeze*.md`
11. `docs/review/code_review.md`
12. `docs/handoff/milestone_closeout*.md`
13. The relevant `scripts/*.py` entrypoint
14. The backing `src/*` module(s)
15. The affected `tests/test_*.py`

- If the task touches branching or merge policy, read `docs/ai/WORKFLOW_GUIDE.md` first.
- If older planning notes conflict with live code, trust `README.md`, `data/README.md`, `docs/ai/PROJECT_CONTEXT.md`, `docs/snapshots/project_snapshot.md`, `docs/plan/*.md`, `docs/contracts/*.md`, `docs/handoff/*.md`, and the current scripts first.

## Repo Map

- `src/data/`: dataset indexing, normalized CSV schemas, loaders, transforms, grouped split logic
- `src/models/`: minimal baseline model
- `src/train/`: training loop, metric selection, checkpoint writing
- `src/eval/`: prediction collection, breast-level aggregation, evaluation artifacts
- `scripts/`: runnable Stage 1 entrypoints
- `docs/ai/`: project context and workflow guidance
- `docs/snapshots/`: repository snapshot documents
- `docs/plan/`: stage plans and issue breakdowns
- `docs/contracts/`: frozen stage boundaries
- `docs/review/`: review expectations and checklists
- `tests/`: current validation suite; uses `unittest`
- `data/raw/primary/`: course raw dataset; treat as read-only
- `data/processed/`: reproducible metadata and split artifacts; regenerate instead of hand-editing
- `outputs/`: generated runs, previews, and test temp files; not source code
- `docs/handoff/`: current runtime and artifact state

High-frequency entrypoints:

- `scripts/inspect_dataset.py`
- `scripts/build_dataset_index.py`
- `scripts/build_splits.py`
- `scripts/check_dataset_loading.py`
- `scripts/train_baseline.py`
- `scripts/run_eval.py`
- `scripts/run_stage1_smoke.py`
- `scripts/run_stage2_smoke.py`

## Environment And Commands

- Observed locally during validation: `Python 3.12.8`
- `README.md` currently names these runtime dependencies: `numpy`, `Pillow`, `torch`, `torchvision`, `scikit-learn`
- `requirements.txt` currently lists the minimal runtime dependencies. It is not version-locked and should not be treated as a fully curated environment manifest.

```bash
# inspect current raw dataset assumptions
python scripts/inspect_dataset.py

# rebuild normalized indexes
python scripts/build_dataset_index.py

# rebuild grouped split artifacts
python scripts/build_splits.py

# smoke-test dataset loading and optionally save previews
python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1 --save-preview

# run minimal Stage 1 training
python scripts/train_baseline.py --epochs 1 --batch-size 8 --image-size 512

# run breast-level evaluation from a checkpoint
python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline/best_model.pt --image-size 1024 --batch-size 1

# run the end-to-end Stage 1 smoke flow
python scripts/run_stage1_smoke.py

# run the end-to-end Stage 2 paired smoke flow
python scripts/run_stage2_smoke.py

# targeted tests
python -m unittest tests.test_index_builder
python -m unittest tests.test_datasets
python -m unittest tests.test_splits
python -m unittest tests.test_split_fold_assignment
python -m unittest tests.test_eval
python -m unittest tests.test_training_smoke
python -m unittest tests.test_stage1_smoke
python -m unittest tests.test_stage2_smoke

# full regression
python -m unittest
```

- There is no confirmed repo-wide `lint`, `format`, or `type-check` command. Do not claim those checks were run unless such tooling is added later.

## Default Working Style

- Start from the relevant entry script or module, then trace the backing `src/*` code.
- For non-trivial milestone work, read the project context, repository snapshot, plan, issue breakdown, and any active contract freeze before editing.
- Keep changes small and local to the affected subsystem.
- Preserve existing artifact names, CLI flags, and file layouts unless the task explicitly changes them.
- Prefer regenerating script-owned artifacts over manually editing generated CSV or JSON files.
- Validate the closest test or script first, then broaden only as needed.
- Update docs when changing paths, artifact names, task definition, evaluation behavior, or CLI behavior.
- For repeated server evaluation work, prefer checkpoint-matched output directories and avoid reusing stale shell variables from older runs.

## Engineering Rules

- The project task is breast-level malignant probability prediction.
- The current training path is single-image, but validation and reporting are breast-level. Preserve that distinction unless the task explicitly changes it.
- The current repository also contains a Stage 2 paired breast-level path. In paired mode, keep strict complete `(CC, MLO)` semantics, fixed `(CC, MLO)` ordering, and probability-valued exports.
- Splits must remain `breast_id`-grouped. Never introduce image-level leakage between train and validation.
- Keep all dataset and artifact paths repo-relative. Do not hardcode personal filesystem paths.
- `data/processed/` and `outputs/` are script-owned outputs. If filenames or schemas change, update every reader, writer, and affected test in the same change.
- Keep `tests/` on `unittest` conventions unless the repository explicitly migrates.
- Avoid heavy frameworks, experiment managers, or dependency expansion during Stage 1 maintenance.

## Boundaries

### Always Allowed

- Edit docs, code, and tests within the current Stage 1 scope
- Run affected `unittest` modules
- Run reproducible scripts that write under `data/processed/` or `outputs/`
- Improve clarity, reproducibility, and consistency of current entrypoints

### Ask First

- Add or upgrade dependencies
- Change the task definition, label semantics, split protocol, or artifact layout
- Reorganize raw data or make external data part of the mainline flow
- Launch long GPU jobs or multi-hour training runs
- Delete artifacts or outputs you did not create
- Change `docs/ai/WORKFLOW_GUIDE.md`, branch policy, or push/merge workflow
- Perform broad refactors across `src/data/`, `src/train/`, and `src/eval/` at once

### Never Do

- Modify files in `data/raw/primary/` in place
- Treat `data/processed/*.csv` or `*.json` as hand-maintained source of truth
- Commit large raw data, extracted images, checkpoints, or generated `outputs/`
- Introduce image-level train/val leakage
- Present current smoke-test metrics as evidence of a strong baseline
- Claim lint, format, or type-check coverage that the repo does not define

## Done Definition

A change is done only when all applicable items below are true:

- The affected code path works, or the doc change is internally consistent.
- The nearest relevant verification has been run:
  - data indexing or split changes: `tests.test_index_builder`, `tests.test_splits`, or `tests.test_split_fold_assignment`
  - dataset or transform changes: `tests.test_datasets` and/or `scripts/check_dataset_loading.py`
  - evaluation changes: `tests.test_eval`
  - training loop changes: `tests.test_training_smoke`
  - end-to-end train/eval script changes: `tests.test_stage1_smoke` and/or `tests.test_stage2_smoke`
  - broad or cross-cutting changes: `python -m unittest`
- If paths, artifact names, task definition, or data conventions changed, the related docs were updated in the same change.
- The final report states exactly what changed, what was run, and what remains unverified.

## Delivery Expectations

When handing work back, report:

- files changed
- why the change was needed
- commands or tests actually run
- artifacts or interfaces affected
- remaining risks, TODOs, or manual follow-up
- any items not verified

## Keep This File Small

- Do not turn the root `AGENTS.md` into a long SOP library.
- Add a local `AGENTS.md` only when one subsystem becomes complex enough to need its own rules.
- Prefer dedicated docs or skills for repeatable flows such as dataset artifact rebuilds or smoke-report interpretation.
