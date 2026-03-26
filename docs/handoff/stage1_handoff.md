# Stage 1 Handoff

## Purpose

This document is the Stage 1 engineering handoff for the minimal runnable pipeline.

Use it to answer four questions quickly:
- what Stage 1 already implements
- how to run the minimal pipeline
- where the generated artifacts live
- what limitations and risks still block a stronger baseline

## Stage 1 Status

Stage 1 is complete as a minimal runnable pipeline.

Implemented now:
- dataset indexes for single-image and paired breast-level views
- minimal preprocessing and dataset loading
- `breast_id`-grouped train/val split plus 5-fold assignment artifacts
- minimal single-image baseline training and validation
- breast-level aggregation and AUROC evaluation artifacts
- one end-to-end smoke test with a sanity report

Not implemented yet:
- paired dual-branch breast-level training as the main training path
- multi-fold training orchestration
- stronger baseline engineering for M2
- benchmark-oriented tuning or experiment management

## Task Definition and Current Boundary

The frozen project task is still breast-level malignant probability prediction.

Current Stage 1 training path:
- train a single-image classifier on the grouped single-image split
- aggregate validation predictions back to `breast_id` during evaluation

Interpretation:
- this is a runnable fallback path, not the intended final breast-level baseline
- Stage 1 proves the pipeline is structurally correct enough to load data, train, validate, aggregate, and report breast-level metrics
- Stage 1 does not prove that the current baseline is strong

## Key Paths

Core code:
- `src/data/`: index building, datasets, transforms, split generation
- `src/eval/`: aggregation, AUROC, evaluation artifact writing
- `src/models/`: minimal CNN baseline
- `src/train/`: train/val loop and checkpoint-selection logic

Main runnable scripts:
- `scripts/build_dataset_index.py`: build Stage 1 metadata indexes
- `scripts/build_splits.py`: build grouped train/val splits and fold assignment
- `scripts/check_dataset_loading.py`: dataset-loading smoke and preview helper
- `scripts/train_baseline.py`: minimal single-image baseline training
- `scripts/run_eval.py`: breast-level evaluation from a validation split and checkpoint
- `scripts/run_stage1_smoke.py`: end-to-end Stage 1 smoke run and sanity report

Generated metadata and split artifacts:
- `data/processed/metadata/primary_single_image_index.csv`
- `data/processed/metadata/primary_paired_breast_index.csv`
- `data/processed/metadata/primary_index_report.json`
- `data/processed/splits/primary_single_image_split_train.csv`
- `data/processed/splits/primary_single_image_split_val.csv`
- `data/processed/splits/primary_paired_breast_split_train.csv`
- `data/processed/splits/primary_paired_breast_split_val.csv`
- `data/processed/splits/primary_fold_assignment.csv`
- `data/processed/splits/primary_fold_summary.json`
- `data/processed/splits/primary_split_summary.json`

Generated training and evaluation outputs:
- `outputs/m1_baseline/config.json`
- `outputs/m1_baseline/metrics_summary.json`
- `outputs/m1_baseline/best_model.pt`
- `outputs/m1_baseline/eval/image_level_predictions.csv`
- `outputs/m1_baseline/eval/breast_level_predictions.csv`
- `outputs/m1_baseline/eval/breast_level_metrics.json`

Generated smoke outputs:
- `outputs/m1_smoke/train/`
- `outputs/m1_smoke/eval/`
- `outputs/m1_smoke/train_stdout.log`
- `outputs/m1_smoke/train_stderr.log`
- `outputs/m1_smoke/eval_stdout.log`
- `outputs/m1_smoke/eval_stderr.log`
- `outputs/m1_smoke/stage1_smoke_report.md`

## Minimal Runbook

If Stage 1 processed artifacts do not exist yet:

```bash
python scripts/build_dataset_index.py
python scripts/build_splits.py
```

Minimal baseline training:

```bash
python scripts/train_baseline.py --epochs 1 --batch-size 8 --image-size 512
```

Minimal evaluation from the validation split:

```bash
python scripts/run_eval.py --checkpoint outputs/m1_baseline/best_model.pt --image-size 512 --output-dir outputs/m1_baseline/eval
```

End-to-end smoke run:

```bash
python scripts/run_stage1_smoke.py
```

Optional dataset-loading check:

```bash
python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1 --save-preview
```

## What To Expect From Each Entry Point

`build_dataset_index.py`
- reads `data/raw/primary/train.csv` and `train_img.zip`
- writes dataset indexes and an index report to `data/processed/metadata/`

`build_splits.py`
- reads the Stage 1 indexes
- writes grouped train/val splits, fold assignment, and split summaries to `data/processed/splits/`

`train_baseline.py`
- trains the minimal single-image CNN on the grouped single-image split
- writes config, metric summary, and the best checkpoint to `outputs/m1_baseline/`

`run_eval.py`
- loads the validation split and checkpoint
- writes image-level predictions, breast-level predictions, and breast-level metrics to `outputs/m1_baseline/eval/`

`run_stage1_smoke.py`
- reruns training and evaluation end to end under `outputs/m1_smoke/`
- writes logs plus a markdown sanity report

## Current Known Findings

The current Stage 1 smoke run already highlights an important limitation.

From `outputs/m1_smoke/stage1_smoke_report.md`:
- the grouped validation breast labels match the evaluation artifact labels, so the pipeline looks structurally aligned
- train and validation loss remain finite
- breast-level AUROC is produced successfully: `0.4225`
- predictions are tightly clustered, with breast-level prediction spread roughly `0.5655` to `0.5922` and `std=0.0049`

Interpretation:
- Stage 1 succeeds as a runnable sanity pipeline
- Stage 1 does not yet succeed as a useful baseline
- the current model shows near-constant output behavior and weak discrimination

## Known Issues and M2 Attention Points

Known issues now:
- the main training path is still single-image, while the official task is breast-level and naturally multi-view
- current smoke outputs show prediction-collapse risk and weak AUROC
- `requirements.txt` is still not curated, so environment portability is weaker than the code path itself

Priority attention before or during M2:
- move from the single-image fallback path toward a stronger breast-level baseline
- diagnose why predictions remain tightly clustered before trusting validation metrics
- keep evaluation centered on breast-level metrics, even if image-level training is still used as a stepping stone
- treat fold artifacts as the reproducibility anchor if multi-fold training is added later

## Practical Notes For Future Work

- Use the generated fold assignment to keep future experiments group-aware and reproducible.
- Do not interpret the current Stage 1 numbers as benchmark-quality results.
- If README and older planning notes differ from actual artifact names, trust the current scripts and paths listed in this document.
- `data/README.md` is the quick reference for data layout; this handoff document is the quick reference for Stage 1 runtime and outputs.
