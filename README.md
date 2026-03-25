# Breast Cancer Detection Model

## Project Overview

This repository is a course project for breast cancer detection from mammography images.

The repository is currently in Stage 0: bootstrap the project, make the dataset layout explicit, inspect the provided data, and define the initial task and evaluation protocol.

Current status:
- dataset archives, labels, and the submission template are present under `data/raw/primary/`
- repository directories exist
- task and data conventions are documented
- no training pipeline or baseline model is implemented yet

## Current Stage and Scope

In scope for the current stage:
- repository structure and developer-facing documentation
- data directory conventions
- lightweight dataset inspection utilities
- task definition and evaluation protocol

Out of scope for the current stage:
- large-scale training
- complex preprocessing pipelines
- aggressive optimization
- external dataset integration beyond storage conventions

## Repository Structure

- `configs/`: placeholder for future configuration files
- `data/`: raw, interim, and processed data layout plus data conventions
- `docs/`: planning material and project documentation
- `outputs/`: generated artifacts such as figures, logs, and checkpoints
- `scripts/`: lightweight runnable utilities
- `src/`: placeholders for future `models`, `train`, and `eval` code
- `requirements.txt`: placeholder for later stages; Stage 0 utilities use the Python standard library only

## Data Organization

The primary course dataset currently lives under `data/raw/primary/`.

Expected files:
- `train.csv`
- `train_img.zip`
- `test_img.zip`
- `name_sid_submission.csv`
- the course dataset note DOCX

Observed dataset facts from the current intake:
- `train.csv` contains 1,300 labeled image rows for 650 `breast_id` studies
- each `breast_id` has exactly two views: one `CC` image and one `MLO` image
- the submission template expects one malignant probability per `breast_id`

See `data/README.md` for directory rules and the current intake summary.

## Environment and Setup

Recommended:
- Python 3.10 or newer

Stage 0 setup:
1. Clone the repository.
2. Keep the provided raw dataset files under `data/raw/primary/`.
3. Do not modify raw files in place.
4. If you extract image archives locally, place extracted files under `data/interim/primary/`.

No third-party dependencies are required for the current inspection utility.

## Minimal Usage

Review the current Stage 0 materials:

1. Read the stage planning docs in `docs/plan/` and `docs/gitflow/issue/`.
2. Inspect the dataset with:

```bash
python scripts/inspect_dataset.py
```

3. Read the task and evaluation protocol in `docs/task_definition.md`.
4. Read the data layout conventions in `data/README.md`.

There is no training entry point yet. Stage 1 is expected to add the first minimal runnable baseline pipeline.

## Current Progress

- repository bootstrap structure is in place
- raw primary dataset files are stored in the repository data layout
- breast-level prediction target is documented
- evaluation is defined around AUROC, matching the course submission requirement
- a reproducible inspection script is available for verifying the current dataset assumptions

## Next Steps

- create breast-level train/validation splits keyed by `breast_id`
- define the first minimal baseline data loading path
- implement a simple baseline that consumes paired `CC` and `MLO` views
- add validation reporting around the documented task definition
