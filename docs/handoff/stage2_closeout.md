# Stage 2 Closeout

## Milestone Info

- Milestone ID: Stage 2
- Milestone name: strict paired CC/MLO breast-level baseline
- Status:
  - [x] complete
  - [ ] partially complete
  - [ ] blocked
  - [x] handed off with risks
- Date: 2026-04-03
- Related stage / branch:
  - `codex/docs-stage2-freeze`
  - `codex/feat-model-stage2`
- Related plan doc:
  - `docs/plan/plan_stage2.md`
- Related issue doc:
  - `docs/plan/issue_stage2.md`

---

## 1. Executive Summary

Stage 2 was meant to move the repository from the Stage 1 single-image fallback to the first strict paired breast-level baseline.

That milestone is now complete.

What was delivered:
- strict paired `(CC, MLO)` loading and validation
- a shared-backbone EfficientNet-B2 paired baseline
- paired training and direct breast-level evaluation under `--dataset paired`
- checkpoint selection by `breast_auroc`
- clean checkpoint-matched eval artifacts with `eval_config.json`

The final canonical Stage 2 run is:
- training root: `outputs/m2_baseline_bs2_lr1e4/`
- eval root: `outputs/m2_baseline_bs2_lr1e4/eval/`
- final paired eval AUROC: `0.9665`

Stage 2 should be closed with documented limitations, not treated as an unlimited-quality final research result. The baseline is now credible, reproducible, and strong enough to hand off to the next milestone.

---

## 2. What Was Completed

- [x] Stage 2 contract freeze and documentation sync
  - Corresponding files:
    - `docs/contracts/contract_freeze_stage2.md`
    - `docs/plan/plan_stage2.md`
    - `docs/plan/issue_stage2.md`
    - `docs/review/code_review.md`
  - Validation:
    - manual consistency review against the frozen paired contract
  - Result:
    - the strict pair, fixed order, and probability-export rules are explicit and enforced

- [x] Paired model, training path, and checkpoint-selection path
  - Corresponding files:
    - `src/models/baseline.py`
    - `src/train/trainer.py`
    - `scripts/train_baseline.py`
  - Validation:
    - `python -m unittest tests.test_training_smoke`
    - `python -m unittest tests.test_stage2_smoke`
  - Result:
    - the paired path trains and selects checkpoints by `breast_auroc`

- [x] Paired evaluation path and artifact contract
  - Corresponding files:
    - `src/eval/pipeline.py`
    - `src/eval/__init__.py`
    - `scripts/run_eval.py`
  - Validation:
    - `python -m unittest tests.test_eval`
    - `python -m unittest tests.test_stage2_smoke`
  - Result:
    - paired eval writes only `breast_level_predictions.csv`, `breast_level_metrics.json`, and `eval_config.json`

- [x] Strict paired dataset validation and view-order checks
  - Corresponding files:
    - `src/data/datasets.py`
    - `tests/test_datasets.py`
  - Validation:
    - `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1`
    - `python -m unittest tests.test_datasets`
  - Result:
    - incomplete pairs, duplicate views, and swapped `CC` / `MLO` semantics are rejected

- [x] Formal Linux server run A and failure diagnosis
  - Corresponding artifacts / docs:
    - `outputs/m2_baseline_20260330_021213/metrics_summary.json`
    - `outputs/m2_baseline_20260330_021213/eval/breast_level_predictions.csv`
    - `outputs/m2_baseline_20260330_021213/eval/breast_level_metrics.json`
    - `docs/handoff/stage2_problem_report_20260330.md`
  - Validation:
    - manual metric review and prediction-distribution analysis
  - Result:
    - the first server run was judged an optimization failure, not a contract or runtime failure

- [x] Formal Linux server run B, clean eval, and artifact hardening
  - Corresponding artifacts / docs:
    - `outputs/m2_baseline_bs2_lr1e4/metrics_summary.json`
    - `outputs/m2_baseline_bs2_lr1e4/eval/eval_config.json`
    - `outputs/m2_baseline_bs2_lr1e4/eval/breast_level_predictions.csv`
    - `outputs/m2_baseline_bs2_lr1e4/eval/breast_level_metrics.json`
    - `docs/handoff/stage2_analysis_report_20260330_bs2_lr1e4.md`
  - Validation:
    - `python -m unittest tests.test_eval`
    - manual review of the final run B training and eval artifacts
  - Result:
    - the new hyperparameter regime produced a strong, clean, checkpoint-matched baseline artifact set

---

## 3. What Was Not Completed

- [x] Full cross-validation or repeated-seed robustness validation
  - Why not completed:
    - Stage 2 was frozen around one grouped holdout baseline, not a broader robustness milestone
  - Should this roll into the next step:
    - yes; this is a natural next-stage extension if more evidence is required

- [x] Deep error analysis beyond the current artifact review
  - Why not completed:
    - the milestone goal was to establish a credible baseline, not to exhaustively analyze all false positives / false negatives
  - Should this roll into the next step:
    - yes; this belongs to follow-up improvement work rather than Stage 2 closure

- [x] Full-CV runner or orchestration tooling
  - Why not completed:
    - explicitly out of scope for the Stage 2 contract
  - Should this roll into the next step:
    - yes if the next milestone needs stronger evidence or broader benchmarking

---

## 4. Key Files and Changes

### Code

- `src/models/baseline.py`
  - Role:
    - single fallback model plus paired EfficientNet-B2 model definitions
  - Stage 2 responsibility:
    - provides `PairedEfficientNetB2Baseline` with fixed `(CC, MLO)` late fusion

- `src/train/trainer.py`
  - Role:
    - train / validate / checkpoint-selection utilities
  - Stage 2 responsibility:
    - provides paired loaders, paired train / validate loops, and `breast_auroc`-first checkpoint selection

- `src/data/datasets.py`
  - Role:
    - single and paired dataset loading
  - Stage 2 responsibility:
    - enforces strict complete paired rows and fixed `(CC, MLO)` semantics

- `src/eval/pipeline.py`
  - Role:
    - prediction collection and artifact writing
  - Stage 2 responsibility:
    - collects paired breast-level predictions and writes breast-level-only paired outputs

### Docs

- `docs/contracts/contract_freeze_stage2.md`
  - Role:
    - frozen Stage 2 interface and semantics
  - Sync state:
    - yes; still matches the implementation

- `docs/handoff/stage2_problem_report_20260330.md`
  - Role:
    - documents why run A failed and why the failure was attributed to optimization instability
  - Sync state:
    - yes; grounded in real server artifacts

- `docs/handoff/stage2_analysis_report_20260330_bs2_lr1e4.md`
  - Role:
    - records the interpretation of run B training, the later eval clarification, and the evolution of the eval workflow hardening
  - Sync state:
    - yes; now historical context rather than an open blocker

### Config / Scripts / Assets

- `scripts/train_baseline.py`
  - Role:
    - public training entrypoint
  - Reuse state:
    - yes; supports both `single` and `paired`

- `scripts/run_eval.py`
  - Role:
    - public evaluation entrypoint
  - Reuse state:
    - yes; now writes `eval_config.json` and avoids silent eval artifact overwrite

- `run_order.md`
  - Role:
    - Linux server runbook
  - Reuse state:
    - yes; updated to reduce shell-variable misuse and output-directory confusion

---

## 5. Validation Summary

### Validation Run

- `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1`
- `python -m unittest tests.test_datasets tests.test_eval tests.test_training_smoke tests.test_stage1_smoke tests.test_stage2_smoke`
- server run A:
  - `python scripts/train_baseline.py --dataset paired --image-size 1024 --batch-size 1 --epochs 10 --lr 1e-3 --output-dir outputs/m2_baseline_20260330_021213`
  - `python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline_20260330_021213/best_model.pt --image-size 1024 --batch-size 1 --output-dir outputs/m2_baseline_20260330_021213/eval`
- server run B:
  - `python scripts/train_baseline.py --dataset paired --image-size 1024 --batch-size 2 --epochs 10 --lr 1e-4 --output-dir outputs/m2_baseline_bs2_lr1e4`
  - `python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline_bs2_lr1e4/best_model.pt --image-size 1024 --batch-size 1`
- latest local regression after eval hardening:
  - `python -m unittest tests.test_eval`

### What These Checks Actually Prove

- Proved:
  - the real paired split loads under the strict paired rules
  - single fallback behavior still passes smoke
  - paired training / evaluation plumbing works end to end on local smoke-sized data
  - run A was a real GPU run and exposed a weak collapsed baseline
  - run B training is far more stable than run A
  - run B checkpoint produced `breast_auroc=0.9665` on clean paired eval
  - the clean eval artifacts confirm:
    - `checkpoint = outputs/m2_baseline_bs2_lr1e4/best_model.pt`
    - `output_dir = outputs/m2_baseline_bs2_lr1e4/eval`
    - `device = cuda`
  - prediction spread is no longer collapsed:
    - positive mean probability: `0.7081`
    - negative mean probability: `0.0280`
    - threshold-0.5 confusion summary: `TP=23`, `TN=96`, `FP=2`, `FN=9`

- Not proved:
  - generalization beyond the current grouped holdout split
  - robustness under broader seeds, folds, or alternative training schedules
  - whether the next milestone should prioritize staged freezing, gradient accumulation, or broader validation

### Missing or Weak Validation

- Missing validation 1:
  - full cross-validation or repeated-seed robustness evidence
- Missing validation 2:
  - deeper medical or image-level inspection of hardest false positives / false negatives

---

## 6. Risks and Known Limitations

### P0 / blocking

- none for Stage 2 closeout

### P1 / serious but not blocking

- the final baseline result is still based on one grouped holdout split rather than full CV
- paired training still depends on torchvision pretrained EfficientNet-B2 weights being available in the runtime environment

### P2 / should improve later

- there is still no mainline full-CV paired runner
- smoke checks prove contract correctness, not final quality
- the current holdout still contains a few hard errors, including high-confidence false positives and low-confidence false negatives

---

## 7. Contract / Scope Notes

- [x] completely executed inside the frozen contract
- [ ] minor scope drift occurred but was documented
- [ ] contract-level problem occurred
- [ ] actual milestone scope drift occurred
- [ ] no formal contract freeze existed

Additional notes:

- public CLI expansion remained limited to `--dataset {single,paired}`
- Stage 1 single-image fallback behavior was preserved
- paired mode still enforces:
  - strict complete `(CC, MLO)` samples only
  - fixed `(CC, MLO)` ordering across dataset / model / eval / export
  - `prediction` exported as sigmoid probability
- `eval_config.json` is now part of the expected eval evidence set for artifact traceability

---

## 8. Recommended Next Entry Point

### Recommended first task

- start the next milestone from the clean Stage 2 baseline artifacts rather than reimplementing Stage 2

### Recommended first files to read

- `docs/handoff/stage2_closeout.md`
- `docs/handoff/stage2_problem_report_20260330.md`
- `docs/handoff/stage2_analysis_report_20260330_bs2_lr1e4.md`
- `outputs/m2_baseline_bs2_lr1e4/metrics_summary.json`
- `outputs/m2_baseline_bs2_lr1e4/eval/eval_config.json`

### Recommended first checks

- review `outputs/m2_baseline_bs2_lr1e4/eval/breast_level_predictions.csv`
- review `outputs/m2_baseline_bs2_lr1e4/eval/breast_level_metrics.json`
- decide whether to expand evidence with full CV, repeated seeds, or error-focused analysis

### Recommended decision to make before coding

- decide what the next milestone is actually for:
  - stronger evidence on the same baseline
  - broader robustness validation
  - or the next model improvement step

---

## 9. Handoff Guidance

- Do not treat run A as the current best baseline; it is the diagnosed failure case.
- Treat `outputs/m2_baseline_bs2_lr1e4/` as the canonical Stage 2 baseline artifact root.
- Do not relax the strict paired contract to make experiments easier.
- Preserve `eval_config.json` with every future eval so checkpoint lineage remains auditable.
- If any future change touches task meaning, split protocol, or the frozen paired export semantics, re-freeze before implementation.

---

## 10. Final Verdict

- [ ] milestone can be cleanly closed
- [x] milestone can be closed with documented limitations
- [ ] milestone should remain open pending one last validation
- [ ] milestone should not be closed because the result is not yet reliable

Current conclusion:

Stage 2 is complete and can be closed with documented limitations. The final canonical baseline is `outputs/m2_baseline_bs2_lr1e4/`, with clean checkpoint-matched eval artifacts under `outputs/m2_baseline_bs2_lr1e4/eval/` and a final breast-level AUROC of `0.9665` on the grouped validation split.
