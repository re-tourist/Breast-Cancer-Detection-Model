# issue_stage1

This file captures the Stage 1 minimal runnable pipeline plan that used to live under `docs/gitflow/issue/`.
It now sits under `docs/plan/` with the rest of the active planning docs.

---

## Issue 1.1 - Build Dataset Index and Paired Breast-level Samples

- Goal: build a stable dataset index for both single-image and paired breast-level views
- Deliverables: dataset index generation code and structured metadata / sample tables
- Acceptance: single-image and paired views can be built consistently

## Issue 1.2 - Implement Minimal Preprocessing and Dataset Loading

- Goal: make the minimal image loading and preprocessing path runnable
- Deliverables: dataset and transform modules plus a lightweight loading smoke test
- Acceptance: tensors have stable shapes and preprocessing is reproducible

## Issue 1.3 - Implement Group-aware Train/Validation Split

- Goal: create a leakage-safe split strategy based on `breast_id`
- Deliverables: split generation script or module and fold assignment artifacts
- Acceptance: the same `breast_id` never leaks across train and validation

## Issue 1.4 - Create Minimal Training Script Skeleton

- Goal: establish the smallest train / validate loop that can be extended later
- Deliverables: minimal training entrypoint and train loop skeleton
- Acceptance: one epoch can run end to end on a small configuration

## Issue 1.5 - Create Minimal Evaluation and Breast-level Aggregation Skeleton

- Goal: make evaluation breast-level instead of image-level
- Deliverables: evaluation module and breast-level prediction artifacts
- Acceptance: aggregated metrics can be computed from validation predictions

## Issue 1.6 - Run One End-to-End Smoke Test and Record Sanity Findings

- Goal: run the full minimal pipeline once and write down the findings
- Deliverables: smoke-test script and a sanity report
- Acceptance: the pipeline is runnable as a whole and the report states what worked and what did not

## Issue 1.7 - Sync Stage-1 Documentation and Usage Notes

- Goal: keep the Stage 1 docs aligned with the actual runnable state
- Deliverables: documentation updates and a Stage 1 summary or handoff note
- Acceptance: the current runnable pipeline is understandable from the docs

## Stage 1 Completion Criteria

- dataset indexing works
- grouped splits exist
- the minimal training loop runs
- breast-level evaluation exists
- one smoke run has been recorded
