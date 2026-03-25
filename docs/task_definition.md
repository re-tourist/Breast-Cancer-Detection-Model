# Task Definition

## Purpose

This document defines the Stage 0 problem setup for the primary course dataset.

It is intentionally limited to the minimum decisions needed to support a first baseline:
- what one training example means
- what the model should predict
- how validation should be done
- which metrics matter most

## Dataset Basis

The definition below is based on the current contents of `data/raw/primary/` and the course dataset note stored there.

Observed facts:
- training labels are stored in `train.csv`
- the training table has 1,300 image rows for 650 breasts
- each `breast_id` has exactly two images: one `CC` view and one `MLO` view
- the submission template expects one score per `breast_id`
- `pathology` is consistent across the two views of each breast

## Task Type

Primary task: breast-level binary classification for malignancy.

Target definition:
- positive class: `pathology == M`
- negative class: `pathology in {B, N}`

This aligns with the course requirement to predict a malignant probability for each `breast_id`.

The raw table is image-level, but the project target is breast-level.
If a future baseline trains on single images, validation and submission still need to aggregate predictions back to the breast level.

## Input Format

Each breast-level example consists of:
- one `CC` mammography image
- one `MLO` mammography image
- a shared `breast_id`

Available metadata in `train.csv` includes:
- `l_r`
- `device`
- `lesion_type`
- `birads`
- `pathology`
- `difficult`
- `annotations`

Stage 0 assumes the baseline input interface should work without requiring metadata or ROI annotations.

## Target and Output Format

Training label:
- derive a breast-level binary label from `pathology`
- use `1` for malignant and `0` for non-malignant

Submission output:
- one row per `breast_id`
- one probability score in `[0, 1]`

Submission columns:
- `breast_id`
- `pred_score`

`pred_score` should represent the model confidence that the breast belongs to the malignant class.

## Split and Validation Protocol

Validation must split by `breast_id`, not by image path.

Reason:
- each breast has two related images
- splitting at the image level would leak information between train and validation

Recommended Stage 0 protocol:
- start with a stratified breast-level train/validation split
- treat cross-validation as the likely next step because the labeled dataset is small
- store any derived split files under `data/processed/splits/`

## Evaluation Metrics

### Primary Metric: AUROC

AUROC is the primary metric for this project at the current stage.

Why:
- the course submission process uses AUROC
- the required output is a probability score rather than a hard class label
- the dataset is imbalanced at the breast level: `M=157` vs `B+N=493`
- AUROC evaluates ranking quality across thresholds before a deployment threshold is fixed

### Secondary Metrics

Secondary metrics to report on internal validation:
- sensitivity (recall) for the malignant class
- specificity at the chosen threshold
- PR AUC
- confusion matrix at a documented threshold

Accuracy may be reported, but it is not a primary decision metric for this repository because it can hide poor malignant-case recall under class imbalance.

## Known Caveats

- the provided labels are image rows, but the official prediction target is breast-level
- ROI annotations are available for many abnormal cases, but Stage 0 does not require detection or segmentation
- the labeled dataset is small, so split variance should be expected
- `birads` and related metadata may be useful later, but they should be treated carefully to avoid shortcut-heavy baselines
