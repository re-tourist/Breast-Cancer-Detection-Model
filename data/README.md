# Data Directory Guide

## Purpose

This file defines the Stage 0 data layout and records the current intake status of the primary course dataset.

In scope:
- directory conventions
- storage rules for raw, interim, and processed data
- the observed dataset summary needed to unblock a minimal baseline

Out of scope:
- final preprocessing design
- external dataset integration details
- heavy feature engineering

## Directory Layout

- `raw/primary/`: original course-provided files kept as close to the source delivery as possible
- `raw/external/`: optional external datasets downloaded for later comparison or augmentation
- `interim/primary/`: extracted or lightly reorganized versions of the primary dataset used for inspection or loading
- `interim/external/`: extracted or lightly reorganized external datasets
- `processed/metadata/`: derived small metadata tables such as breast-level labels or manifests
- `processed/splits/`: train/validation split files keyed by `breast_id`
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

Current Stage 0 summary:
- breast-level pathology counts: `N=412`, `B=81`, `M=157`
- image-level pathology counts: `N=824`, `B=162`, `M=314`
- annotated image rows: `476 / 1300`
- lesion metadata is sparse for normal cases, with `lesion_type` empty on 824 image rows

These counts can be regenerated with:

```bash
python scripts/inspect_dataset.py
```

## Usage Rules

- do not edit files inside `raw/primary/` in place
- keep raw filenames and relative paths stable unless there is a documented reason to change them
- extract archives into `interim/primary/` rather than next to the raw zip files
- store derived breast-level manifests under `processed/metadata/`
- store train/validation split definitions under `processed/splits/`
- keep all file references repository-relative
- document any new external dataset before using it in code
