# project_snapshot

## 1. Repository Overview

- repository type: single-package coursework / prototype repo
- apparent purpose: Stage 1 minimal runnable pipeline for breast-level malignant probability prediction from mammography images
- primary language(s): Python
- main framework(s): PyTorch, scikit-learn, Pillow, NumPy
- monorepo or not: no
- current documentation quality: usable, but with legacy/duplicate workflow docs that should be treated carefully

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
  - runnable Stage 1 entry points
- `src/`
  - implementation packages for data, models, training, and evaluation
- `templates/`
  - reusable PR / task / milestone templates
- `tests/`
  - `unittest`-based validation suite

High-frequency code areas:

- `src/`
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
- `docs/handoff/stage1_closeout.md`
- `.codex/`

## 3. Key Entry Points

### Runtime / App entrypoints

- none discovered; this is a scripts-driven repo

### Training / Experiment entrypoints

- `scripts/train_baseline.py`
- `scripts/run_stage1_smoke.py`

### Inference / Evaluation entrypoints

- `scripts/run_eval.py`
- `src/eval/pipeline.py`
- `src/eval/aggregation.py`

### Data / preprocessing entrypoints

- `scripts/inspect_dataset.py`
- `scripts/build_dataset_index.py`
- `scripts/build_splits.py`
- `scripts/check_dataset_loading.py`

### Main configs

- `.codex/config.toml`
- `.codex/agents/implementer.toml`
- `.codex/agents/reviewer.toml`
- `data/README.md`

### Main docs

- `README.md`
- `data/README.md`
- `docs/task_definition.md`
- `docs/plan/minimal_system_design.md`
- `docs/handoff/stage1_handoff.md`
- `docs/handoff/stage1_closeout.md`
- `docs/ai/WORKFLOW_GUIDE.md`

## 4. Tooling Signals

### Dependency / package manager

- signal: no curated package manager discovered
- file(s): `requirements.txt` exists but is empty

### Build system

- signal: none clearly discoverable
- file(s): not clearly discoverable

### Lint / format

- signal: none clearly discoverable
- file(s): not clearly discoverable

### Type checking

- signal: none clearly discoverable
- file(s): not clearly discoverable

### Test framework

- signal: Python `unittest`
- file(s): `tests/test_*.py`, `python -m unittest`

### CI / GitHub Actions

- signal: no GitHub Actions workflow file discovered in the scanned repo
- file(s): `.github/pull_request_template.md` only

### Docker / environment / devcontainer

- signal: none discovered
- file(s): not clearly discoverable

## 5. Validation Signals

### Install

- not clearly discoverable

### Run

- `python scripts/inspect_dataset.py`
- `python scripts/build_dataset_index.py`
- `python scripts/build_splits.py`
- `python scripts/train_baseline.py --epochs 1 --batch-size 8 --image-size 512`
- `python scripts/run_eval.py --checkpoint outputs/m1_baseline/best_model.pt --image-size 512 --output-dir outputs/m1_baseline/eval`
- `python scripts/run_stage1_smoke.py`

### Test

- `python -m unittest`
- `python -m unittest tests.test_index_builder`
- `python -m unittest tests.test_datasets`
- `python -m unittest tests.test_splits`
- `python -m unittest tests.test_split_fold_assignment`
- `python -m unittest tests.test_eval`
- `python -m unittest tests.test_training_smoke`
- `python -m unittest tests.test_stage1_smoke`

### Lint

- not clearly discoverable

### Build

- not clearly discoverable

### Focused / local checks

- `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1 --save-preview`
- `python scripts/inspect_dataset.py`
- `python scripts/build_dataset_index.py`
- `python scripts/build_splits.py`

## 6. Risk Zones

### Sensitive directories/files

- `data/raw/primary/`
- `data/processed/`
- `outputs/`
- `src/data/`
- `src/eval/`
- `.codex/`
- `.agents/`

### Potentially generated files

- `data/processed/metadata/*.csv`
- `data/processed/splits/*.csv`
- `data/processed/splits/*.json`
- `outputs/*`
- `*.pt`
- `*.ckpt`

### Infra / deployment / secrets-related areas

- none clearly discovered

### Public interfaces / schemas / stable outputs

- `data/README.md`
- `docs/task_definition.md`
- `scripts/*.py` CLI flags and artifact locations
- `outputs/m1_baseline/*`
- `outputs/m1_smoke/*`
- `data/processed/metadata/*`
- `data/processed/splits/*`

### Places where small edits could have repo-wide impact

- `src/data/splits.py`
- `src/data/index_builder.py`
- `src/eval/pipeline.py`
- `scripts/train_baseline.py`
- `scripts/run_eval.py`

## 7. Documentation State

### Existing docs

- `README.md`: current stage summary and run commands
- `AGENTS.md`: repo operating manual
- `data/README.md`: data layout and intake rules
- `docs/task_definition.md`: breast-level task definition
- `docs/plan/minimal_system_design.md`: design reference for the minimal system
- `docs/handoff/stage1_handoff.md`: Stage 1 handoff
- `docs/handoff/stage1_closeout.md`: Stage 1 closeout
- `docs/ai/WORKFLOW_GUIDE.md`: starter-kit workflow guide
- `docs/ai/PROJECT_CONTEXT.md`: project context for agents
- `docs/plan/plan_stage2.md`: Stage 2 plan
- `docs/plan/issue_stage0.md`: Stage 0 bootstrap issues
- `docs/plan/issue_stage1.md`: Stage 1 minimal pipeline issues
- `docs/plan/issue_stage2.md`: Stage 2 issue breakdown
- `docs/contracts/contract_freeze_stage2.md`: Stage 2 contract freeze
- `docs/review/code_review.md`: review expectations

### Likely missing docs

- [ ] AGENTS.md
- [ ] PROJECT_CONTEXT.md
- [ ] stage plan
- [ ] issue breakdown
- [ ] review checklist
- [ ] contract freeze
- [ ] closeout doc

### Suspected stale docs

- Legacy branch-policy notes were retired from the active docs and no longer part of the workflow path
- `docs/plan/stage/plan_stage0.md`
- `docs/plan/plan_milestone.md`
- `templates/PR_TEMPLATE.md` and `.github/pull_request_template.md` overlap

## 8. Working Recommendations

### Read first

- `AGENTS.md`
- `docs/ai/WORKFLOW_GUIDE.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/plan/issue_stage0.md`
- `docs/plan/issue_stage1.md`
- `docs/snapshots/project_snapshot.md`
- `docs/plan/plan_stage2.md`
- `docs/plan/issue_stage2.md`
- `docs/contracts/contract_freeze_stage2.md`

### Avoid touching casually

- `data/raw/primary/`
- `data/processed/`
- `outputs/`
- `docs/task_definition.md`
- `src/data/splits.py`
- `src/eval/pipeline.py`

### Validate first

- `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1 --save-preview`
- `python -m unittest tests.test_datasets`
- `python -m unittest tests.test_splits`
- `python -m unittest tests.test_eval`

### Document before coding if missing

- project context
- repo snapshot
- stage plan
- issue breakdown
- contract freeze

## 9. Open Uncertainties

- exact contents of `configs/` were not inspected in depth
- no CI workflow file was found during the scan, but that may change later
- Legacy workflow material is retired and no longer part of the active workflow
- install/bootstrap instructions are not clearly discoverable beyond the runtime notes in `README.md`
