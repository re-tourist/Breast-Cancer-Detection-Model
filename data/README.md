# Data Directory Guide

## Purpose

This file defines the repository data layout and records the current intake status of the primary course dataset.

In scope:
- directory conventions
- storage rules for raw, interim, and processed data
- the current Stage 1 generated metadata and split artifacts

Out of scope:
- detailed preprocessing design
- external dataset integration details
- model-training logic

## Directory Layout

- `raw/primary/`: original course-provided files kept as close to the source delivery as possible
- `raw/external/`: optional external datasets downloaded for later comparison or augmentation
- `interim/primary/`: extracted or lightly reorganized versions of the primary dataset used for inspection or loading
- `interim/external/`: extracted or lightly reorganized external datasets
- `processed/metadata/`: derived small metadata tables such as dataset indexes and validation reports
- `processed/splits/`: train/validation split files and fold assignment artifacts keyed by `breast_id`
- `processed/cache/`: optional generated caches; create only when needed

## Current Primary Dataset Intake

Files currently observed in `raw/primary/`:
- `train.csv`
- `train_img.zip`
- `test_img.zip`
- `name_sid_submission.csv`
- one course dataset note DOCX

Observed dataset structure:
- `train.csv` contains 1,300 image rows representing 650 breasts
- each `breast_id` has exactly two images: one `CC` view and one `MLO` view
- image paths in `train.csv` point to JPEG files inside `train_img.zip`
- the test archive contains 1,300 JPEG images and the submission template contains 650 `breast_id` rows
- `pathology` is consistent across the two views of each breast, so a breast-level target can be derived safely
- `annotations` are empty for normal cases and contain polygon ROI strings for abnormal cases

Current dataset summary:
- breast-level pathology counts: `N=412`, `B=81`, `M=157`
- image-level pathology counts: `N=824`, `B=162`, `M=314`
- annotated image rows: `476 / 1300`
- lesion metadata is sparse for normal cases, with `lesion_type` empty on 824 image rows

These counts can be regenerated with:

```bash
python scripts/inspect_dataset.py
```

## Current Stage 1 Generated Artifacts

Current index artifacts under `processed/metadata/`:
- `primary_single_image_index.csv`
- `primary_paired_breast_index.csv`
- `primary_index_report.json`

Current split artifacts under `processed/splits/`:
- `primary_single_image_split_train.csv`
- `primary_single_image_split_val.csv`
- `primary_paired_breast_split_train.csv`
- `primary_paired_breast_split_val.csv`
- `primary_fold_assignment.csv`
- `primary_fold_summary.json`
- `primary_split_summary.json`

These files are small, reproducible project artifacts that describe how Stage 1 reads and splits the dataset.

## Usage Rules

- do not edit files inside `raw/primary/` in place
- keep raw filenames and relative paths stable unless there is a documented reason to change them
- extract archives into `interim/primary/` rather than next to the raw zip files
- store derived dataset indexes under `processed/metadata/`
- store train/validation split definitions and fold assignment under `processed/splits/`
- keep all file references repository-relative
- document any new external dataset before using it in code
