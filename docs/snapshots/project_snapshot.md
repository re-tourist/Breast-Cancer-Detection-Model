# project_snapshot

## 1. Repository Overview

- repository type: single-package coursework / prototype repo
- apparent purpose: breast-level malignant probability prediction from mammography images
- current execution stage: Stage 2 closed with documented limitations on a clean strict paired CC/MLO baseline
- primary language(s): Python
- main framework(s): PyTorch, torchvision, scikit-learn, Pillow, NumPy
- monorepo or not: no
- current documentation quality: good for active execution; Stage 2 contract and review docs are now part of the main path

## 2. Top-Level Structure

- `.agents/`
  - local skills for repo snapshot, planning, and milestone review
- `.codex/`
  - project-scoped Codex config and subagent definitions
- `.github/`
  - pull request template
- `configs/`
  - project configuration files; contents not inspected in depth
- `data/`
  - raw dataset, generated metadata, split artifacts, and data README
- `docs/`
  - task definition, plan docs, handoff docs, workflow docs, context docs, snapshots, and review/contract templates
- `outputs/`
  - generated runs, smoke artifacts, and temporary outputs
- `prompts/`
  - prompt templates for generating project docs and reviews
- `scripts/`
  - runnable Stage 1 and Stage 2 entry points
- `src/`
  - implementation packages for data, models, training, and evaluation
- `templates/`
  - reusable PR / task / milestone templates
- `tests/`
  - `unittest`-based validation suite

High-frequency code areas:

- `src/data/`
- `src/train/`
- `src/eval/`
- `scripts/`
- `tests/`

High-frequency documentation areas:

- `README.md`
- `data/README.md`
- `docs/task_definition.md`
- `docs/ai/`
- `docs/plan/`
- `docs/contracts/`
- `docs/review/`
- `docs/handoff/`

Stable / sensitive areas:

- `data/raw/primary/`
- `data/processed/`
- `outputs/`
- `docs/task_definition.md`
- `docs/contracts/contract_freeze_stage2.md`

## 3. Key Entry Points

### Training / Experiment entrypoints

- `scripts/train_baseline.py`
  - `--dataset single` keeps the Stage 1 fallback path
  - `--dataset paired` runs the Stage 2 paired baseline
- `scripts/run_stage1_smoke.py`
- `scripts/run_stage2_smoke.py`

### Inference / Evaluation entrypoints

- `scripts/run_eval.py`
  - `--dataset single` writes image-level plus breast-level artifacts
  - `--dataset paired` writes breast-level predictions, metrics, and eval context artifacts
- `src/eval/pipeline.py`
- `src/eval/aggregation.py`

### Data / preprocessing entrypoints

- `scripts/inspect_dataset.py`
- `scripts/build_dataset_index.py`
- `scripts/build_splits.py`
- `scripts/check_dataset_loading.py`

### Main configs / docs

- `README.md`
- `AGENTS.md`
- `data/README.md`
- `docs/ai/WORKFLOW_GUIDE.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/contracts/contract_freeze_stage2.md`
- `docs/plan/plan_stage2.md`
- `docs/plan/issue_stage2.md`
- `docs/review/code_review.md`
- `docs/handoff/stage2_closeout.md`

## 4. Tooling Signals

### Dependency / package manager

- signal: lightweight pip-style dependency list only
- file(s): `requirements.txt` lists `numpy`, `Pillow`, `scikit-learn`, `torch`, `torchvision`

### Build system

- signal: none clearly discoverable

### Lint / format

- signal: none clearly discoverable

### Type checking

- signal: none clearly discoverable

### Test framework

- signal: Python `unittest`
- file(s): `tests/test_*.py`, `python -m unittest`

### CI / GitHub Actions

- signal: no GitHub Actions workflow file discovered in the scanned repo
- file(s): `.github/pull_request_template.md` only

## 5. Validation Signals

### Run

- `python scripts/inspect_dataset.py`
- `python scripts/build_dataset_index.py`
- `python scripts/build_splits.py`
- `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1`
- `python scripts/train_baseline.py --dataset single --epochs 1 --batch-size 8 --image-size 512`
- `python scripts/train_baseline.py --dataset paired --image-size 1024 --epochs 10 --output-dir outputs/m2_baseline`
- `python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline/best_model.pt --image-size 1024`
- Linux server run A:
  - `python scripts/train_baseline.py --dataset paired --image-size 1024 --batch-size 1 --epochs 10 --lr 1e-3 --output-dir outputs/m2_baseline_20260330_021213`
  - `python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline_20260330_021213/best_model.pt --image-size 1024 --batch-size 1 --output-dir outputs/m2_baseline_20260330_021213/eval`
- Linux server run B training:
  - `python scripts/train_baseline.py --dataset paired --image-size 1024 --batch-size 2 --epochs 10 --lr 1e-4 --output-dir outputs/m2_baseline_bs2_lr1e4`
- Linux server run B clean eval:
  - `python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline_bs2_lr1e4/best_model.pt --image-size 1024 --batch-size 1`
- `python scripts/run_stage1_smoke.py`
- `python scripts/run_stage2_smoke.py`

### Test

- `python -m unittest`
- `python -m unittest tests.test_index_builder`
- `python -m unittest tests.test_datasets`
- `python -m unittest tests.test_splits`
- `python -m unittest tests.test_split_fold_assignment`
- `python -m unittest tests.test_eval`
- `python -m unittest tests.test_training_smoke`
- `python -m unittest tests.test_stage1_smoke`
- `python -m unittest tests.test_stage2_smoke`

## 6. Risk Zones

### Sensitive directories/files

- `data/raw/primary/`
- `data/processed/`
- `outputs/`
- `src/data/`
- `src/eval/`
- `scripts/train_baseline.py`
- `scripts/run_eval.py`

### Public interfaces / schemas / stable outputs

- `docs/task_definition.md`
- `docs/contracts/contract_freeze_stage2.md`
- `scripts/train_baseline.py` CLI flags and output directories
- `scripts/run_eval.py` CLI flags and output artifacts
- `outputs/m1_baseline/*`
- `outputs/m2_baseline/*`
- `outputs/m1_smoke/*`
- `outputs/m2_smoke/*`
- `data/processed/metadata/*`
- `data/processed/splits/*`

### Places where small edits could have repo-wide impact

- `src/data/index_builder.py`
- `src/data/datasets.py`
- `src/train/trainer.py`
- `src/eval/pipeline.py`
- `scripts/train_baseline.py`
- `scripts/run_eval.py`

## 7. Documentation State

### Existing docs

- `README.md`: current Stage 2 summary and run commands
- `AGENTS.md`: repo operating manual
- `data/README.md`: data layout and intake rules
- `docs/task_definition.md`: breast-level task definition
- `docs/handoff/stage1_handoff.md`: Stage 1 handoff
- `docs/handoff/stage1_closeout.md`: Stage 1 closeout
- `docs/handoff/stage2_closeout.md`: final Stage 2 closeout and next-step recommendation
- `docs/handoff/stage2_problem_report_20260330.md`: first failed server run diagnosis
- `docs/handoff/stage2_analysis_report_20260330_bs2_lr1e4.md`: second server training run analysis and eval mismatch note
- `docs/ai/WORKFLOW_GUIDE.md`: canonical repo workflow
- `docs/ai/PROJECT_CONTEXT.md`: project context for agents
- `docs/plan/plan_stage2.md`: Stage 2 plan
- `docs/plan/issue_stage2.md`: Stage 2 issue breakdown
- `docs/contracts/contract_freeze_stage2.md`: Stage 2 contract freeze
- `docs/review/code_review.md`: review expectations

### Suspected stale docs

- `docs/plan/plan_stage0.md`
- `docs/plan/plan_milestone.md`
- duplicated PR templates under `templates/` and `.github/`

## 8. Working Recommendations

### Read first

- `AGENTS.md`
- `README.md`
- `docs/ai/WORKFLOW_GUIDE.md`
- `data/README.md`
- `docs/task_definition.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/snapshots/project_snapshot.md`
- `docs/plan/plan_stage2.md`
- `docs/plan/issue_stage2.md`
- `docs/contracts/contract_freeze_stage2.md`
- `docs/review/code_review.md`
- `docs/handoff/stage2_closeout.md`

### Avoid touching casually

- `data/raw/primary/`
- `data/processed/`
- `outputs/`
- `docs/task_definition.md`
- `docs/contracts/contract_freeze_stage2.md`

### Validate first

- `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1`
- `python -m unittest tests.test_datasets`
- `python -m unittest tests.test_eval`
- `python -m unittest tests.test_training_smoke`
- `python -m unittest tests.test_stage2_smoke`

## 9. Open Uncertainties

- the final Stage 2 result is still based on one grouped holdout split rather than full CV
- exact contents of `configs/` were not inspected in depth
- no CI workflow file was found during the scan, but that may change later
- install/bootstrap instructions are still intentionally lightweight beyond runtime notes in `README.md`
