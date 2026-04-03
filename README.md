# Breast Cancer Detection Model

## Project Overview

This repository is a course project for breast cancer detection from mammography images.

The repository has completed Stage 2 for the breast-level malignant probability task and is ready for the next milestone.

Current status:
- Stage 1 data indexing, grouped split, evaluation, and smoke-test infrastructure remain in place
- Stage 1 single-image training remains available as a fallback path
- Stage 2 paired CC/MLO training, direct breast-level evaluation, and a dedicated Stage 2 smoke script are implemented
- the paired contract is frozen to strict complete `(CC, MLO)` samples, fixed `(CC, MLO)` ordering, and probability-valued `prediction` exports
- formal Linux server experimentation completed for the Stage 2 baseline:
  - run A at `batch_size=1`, `lr=1e-3` exposed unstable optimization and weak paired performance
  - run B at `batch_size=2`, `lr=1e-4` produced a much stronger training-side validation curve
  - the clean checkpoint-matched eval under `outputs/m2_baseline_bs2_lr1e4/eval/` reported `breast_auroc=0.9665`

## Current Stage and Scope

In scope for the current repository state:
- reproducible data indexing and strict paired breast-level sample definitions
- lightweight preprocessing and dataset loading
- `breast_id`-grouped split artifacts and fold assignment
- Stage 1 single-image fallback training and aggregated evaluation
- Stage 2 paired CC/MLO breast-level training and direct breast-level evaluation
- Stage 1 and Stage 2 smoke-test scripts and sanity reports

Out of scope for the current stage:
- changing the task definition, split protocol, or Stage 2 frozen contract
- full cross-validation training orchestration
- hyperparameter search and benchmark tuning
- heavy evaluator or experiment-management frameworks
- claiming broader robustness than the current grouped holdout evidence supports

## Repository Structure

- `src/data/`: dataset index building, transforms, datasets, and grouped split utilities
- `src/models/`: single-image fallback model and paired Stage 2 baseline model
- `src/train/`: train/val loop, checkpoint selection, and metric summary logic
- `src/eval/`: breast-level aggregation, AUROC calculation, paired prediction collection, and evaluation artifact writing
- `scripts/`: runnable Stage 1 and Stage 2 entry points
- `data/processed/metadata/`: generated dataset index artifacts
- `data/processed/splits/`: generated split and fold assignment artifacts
- `outputs/m1_baseline/`: single-image fallback outputs and evaluation artifacts
- `outputs/m2_baseline/`: paired Stage 2 baseline outputs and evaluation artifacts
- `outputs/m1_smoke/`: Stage 1 smoke logs, outputs, and sanity report
- `outputs/m2_smoke/`: Stage 2 smoke logs, outputs, and sanity report

## Data Organization

The primary course dataset is expected under `data/raw/primary/`.

Required raw inputs:
- `train.csv`
- `train_img.zip`
- `test_img.zip`
- `name_sid_submission.csv`

Generated artifacts live under:
- `data/processed/metadata/`
- `data/processed/splits/`
- `outputs/m1_baseline/`
- `outputs/m2_baseline/`
- `outputs/m1_smoke/`
- `outputs/m2_smoke/`

See `data/README.md` for the data layout rules, `docs/handoff/stage1_handoff.md` for the Stage 1 artifact map, and `docs/handoff/stage2_closeout.md` for the current Stage 2 execution status.

## Environment and Setup

Recommended:
- Python 3.10 or newer

Current scripts require the runtime environment to provide:
- `numpy`
- `Pillow`
- `torch`
- `torchvision`
- `scikit-learn`

Notes:
- keep the provided raw dataset files under `data/raw/primary/`
- do not edit raw files in place
- `requirements.txt` now lists the minimal runtime dependencies, but version locking remains a follow-up item

## Workflow

The canonical workflow for this repository lives in [docs/ai/WORKFLOW_GUIDE.md](docs/ai/WORKFLOW_GUIDE.md).
Use [AGENTS.md](AGENTS.md) for repo-level operating rules and [docs/ai/PROJECT_CONTEXT.md](docs/ai/PROJECT_CONTEXT.md) for current project intent and stage boundaries.

When these docs conflict, follow the canonical workflow and the current project context.

## Minimal Usage

If the processed artifacts already exist, you can start from training, evaluation, or smoke. Otherwise, the minimal repository flow is:

1. Build dataset indexes:

```bash
python scripts/build_dataset_index.py
```

2. Build grouped splits and fold assignment:

```bash
python scripts/build_splits.py
```

3. Check paired dataset loading:

```bash
python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1
```

4. Train the Stage 1 single-image fallback:

```bash
python scripts/train_baseline.py --dataset single --epochs 1 --batch-size 8 --image-size 512
```

5. Train the Stage 2 paired baseline:

```bash
python scripts/train_baseline.py --dataset paired --image-size 1024 --batch-size 2 --epochs 10 --lr 1e-4 --output-dir outputs/m2_baseline
```

6. Run evaluation from a checkpoint:

```bash
python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline/best_model.pt --image-size 1024 --batch-size 1
```

This writes:

- `breast_level_predictions.csv`
- `breast_level_metrics.json`
- `eval_config.json`

7. Run the dedicated smoke scripts:

```bash
python scripts/run_stage1_smoke.py
python scripts/run_stage2_smoke.py
```

For a fuller Stage 1 runbook and artifact map, read `docs/handoff/stage1_handoff.md`.
For the Stage 1 foundation closeout, read `docs/handoff/stage1_closeout.md`.
For the final Stage 2 closeout and remaining limitations, read `docs/handoff/stage2_closeout.md`.
For the failed first server run diagnosis, read `docs/handoff/stage2_problem_report_20260330.md`.
For the current best-known rerun analysis and eval mismatch note, read `docs/handoff/stage2_analysis_report_20260330_bs2_lr1e4.md`.

## Current Progress

- dataset indexes exist for both single-image and paired breast-level views
- grouped train/val splits and 5-fold assignment artifacts are generated by `breast_id`
- a single-image fallback training loop and checkpoint selection flow remain available
- a paired EfficientNet-B2 baseline now trains one `breast_id` sample at a time from fixed `(CC, MLO)` inputs
- single-image evaluation still writes image-level and breast-level artifacts
- paired evaluation writes `breast_level_predictions.csv`, `breast_level_metrics.json`, and `eval_config.json`
- Stage 1 and Stage 2 smoke scripts both produce logs and markdown sanity reports

## Current Limitations

- the Stage 2 result is still based on one grouped holdout split rather than full cross-validation
- local smoke and unit tests only prove plumbing and contract correctness; they do not prove final model quality
- full cross-validation training is still not implemented as a mainline runner
- dependency packaging remains lightweight and not yet cleaned up for broader handoff

## Next Steps

1. Treat `outputs/m2_baseline_bs2_lr1e4/` as the canonical Stage 2 baseline artifact root.
2. Decide whether the next milestone should focus on broader evidence, such as full CV or repeated seeds, or on the next model improvement step.
3. Preserve checkpoint-matched eval artifacts and `eval_config.json` for all future runs.
