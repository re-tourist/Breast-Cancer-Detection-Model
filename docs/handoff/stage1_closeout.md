# Stage 1 Closeout

## Milestone 1 Objective

Stage 1 was meant to establish a minimal runnable pipeline for the breast-level malignant probability task.

For closeout purposes, that objective is considered met only if the repository can:
- build dataset indexes from the provided raw metadata
- build `breast_id`-grouped splits and fold assignment artifacts
- train a minimal baseline without data leakage across grouped boundaries
- aggregate validation predictions back to `breast_id`
- produce breast-level evaluation artifacts and a smoke-test sanity record

## What Was Completed In M1

Stage 1 now includes:
- dataset index artifacts for single-image and paired breast-level views
- minimal preprocessing and dataset loading
- grouped train/val split artifacts plus 5-fold assignment artifacts
- a minimal single-image baseline train/val loop
- breast-level aggregation and AUROC evaluation artifacts
- one end-to-end smoke test with logs and a markdown sanity report
- Stage 1 runtime and artifact documentation

This means M1 achieved a full engineering loop from raw metadata and image archive access through to breast-level evaluation.

## What Remains Out Of Scope For M1

The following are still outside the Stage 1 boundary:
- paired dual-branch breast-level training as the main baseline
- multi-fold training orchestration built on top of the fold artifacts
- stronger baseline engineering aimed at competitive validation performance
- hyperparameter search, experiment management, or benchmark-style reporting
- Milestone 2 model design and improvement work

M1 should therefore be read as a runnable fallback foundation, not as a validated final baseline.

## Current Runnable Path

The current minimal runnable path is:

```bash
python scripts/build_dataset_index.py
python scripts/build_splits.py
python scripts/train_baseline.py --epochs 1 --batch-size 8 --image-size 512
python scripts/run_eval.py --checkpoint outputs/m1_baseline/best_model.pt --image-size 512 --output-dir outputs/m1_baseline/eval
python scripts/run_stage1_smoke.py
```

Interpretation of that path:
- training is still single-image
- validation reporting is breast-level through `breast_id` aggregation
- the smoke script is the quickest way to confirm that the whole loop still runs end to end

## Current Artifacts And Where To Find Them

Stage 1 metadata artifacts:
- `data/processed/metadata/primary_single_image_index.csv`
- `data/processed/metadata/primary_paired_breast_index.csv`
- `data/processed/metadata/primary_index_report.json`

Stage 1 split artifacts:
- `data/processed/splits/primary_single_image_split_train.csv`
- `data/processed/splits/primary_single_image_split_val.csv`
- `data/processed/splits/primary_paired_breast_split_train.csv`
- `data/processed/splits/primary_paired_breast_split_val.csv`
- `data/processed/splits/primary_fold_assignment.csv`
- `data/processed/splits/primary_fold_summary.json`
- `data/processed/splits/primary_split_summary.json`

Current baseline outputs:
- `outputs/m1_baseline/config.json`
- `outputs/m1_baseline/metrics_summary.json`
- `outputs/m1_baseline/best_model.pt`
- `outputs/m1_baseline/eval/image_level_predictions.csv`
- `outputs/m1_baseline/eval/breast_level_predictions.csv`
- `outputs/m1_baseline/eval/breast_level_metrics.json`

Current smoke outputs:
- `outputs/m1_smoke/train/`
- `outputs/m1_smoke/eval/`
- `outputs/m1_smoke/train_stdout.log`
- `outputs/m1_smoke/train_stderr.log`
- `outputs/m1_smoke/eval_stdout.log`
- `outputs/m1_smoke/eval_stderr.log`
- `outputs/m1_smoke/stage1_smoke_report.md`

## Main Sanity Findings From The Smoke Test

The current smoke run shows that the pipeline is structurally working, but not yet producing a convincing baseline.

Observed from `outputs/m1_smoke/stage1_smoke_report.md`:
- grouped validation labels and breast-level evaluation labels are aligned
- train and validation loss are finite
- breast-level AUROC is produced successfully: `0.4225`
- breast-level predictions are tightly clustered, approximately `0.5655` to `0.5922`, with `std=0.0049`

Practical reading:
- the end-to-end loop is real and reusable
- the current baseline remains weak
- there is already a clear prediction-collapse risk signal

## Known Limitations And Risks

The main limitations at closeout are:
- the active training route is still a single-image fallback, while the task definition is breast-level and naturally multi-view
- current validation outputs are weak and tightly clustered, so the pipeline is not yet evidence of an effective baseline
- fold artifacts exist, but the repository does not yet run multi-fold training or OOF evaluation as a baseline workflow
- dependency packaging remains lightweight, so reproducibility across environments is weaker than the code path itself

The main risk entering M2 is mistaking structural completeness for modeling readiness.

## Recommended First Priorities For M2

1. Replace the single-image fallback emphasis with a stronger breast-level training path, ideally centered on paired CC/MLO inputs.
2. Diagnose and reduce the current near-constant prediction behavior before treating validation metrics as informative.
3. Build the next baseline around the existing grouped split and fold artifacts so future results remain leakage-safe and reproducible.

## Closeout Statement

Milestone 1 should be closed as complete for infrastructure and runnable-path purposes.

It should not be closed as a successful modeling baseline.

The repository is now ready for Milestone 2 work because the core questions of data intake, grouped splitting, minimal training, breast-level aggregation, evaluation output, and end-to-end smoke execution have all been answered in code.
