# Stage 2 Closeout

## Milestone Info

- Milestone ID: Stage 2
- Milestone name: strict paired CC/MLO breast-level baseline
- Status:
  - [ ] complete
  - [x] partially complete
  - [ ] blocked
  - [x] handed off with risks
- Date: 2026-04-02
- Related stage / branch:
  - `codex/docs-stage2-freeze`
  - `codex/feat-model-stage2`
- Related plan doc:
  - `docs/plan/plan_stage2.md`
- Related issue doc:
  - `docs/plan/issue_stage2.md`

---

## 1. Executive Summary

Stage 2 was supposed to move the repository from the Stage 1 single-image fallback to the first strict paired breast-level baseline.

That engineering work is complete:
- strict paired `(CC, MLO)` loading is enforced
- the shared-backbone EfficientNet-B2 paired model is implemented
- training and evaluation entrypoints support `--dataset {single,paired}`
- paired evaluation writes only breast-level artifacts
- a dedicated Stage 2 smoke path and regression coverage exist

Formal Linux server experimentation has also started:
- run A (`batch_size=1`, `lr=1e-3`) completed on GPU but failed as a useful baseline, with `breast_auroc=0.5389` and strong negative-side collapse
- run B (`batch_size=2`, `lr=1e-4`) showed a much healthier training curve and a best training-side validation `breast_auroc=0.9668`
- the evaluation command after run B accidentally pointed to the older run A checkpoint, so the new run still needs one clean checkpoint-matched evaluation pass

The Stage 2 implementation is operational and the latest optimization regime looks promising, but the milestone should remain open until `outputs/m2_baseline_bs2_lr1e4/best_model.pt` is evaluated cleanly.

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
    - paired eval writes only `breast_level_predictions.csv` and `breast_level_metrics.json`

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

- [x] Follow-up training run B and evaluation workflow hardening
  - Corresponding files / docs:
    - `scripts/run_eval.py`
    - `tests/test_eval.py`
    - `run_order.md`
    - `docs/handoff/stage2_analysis_report_20260330_bs2_lr1e4.md`
  - Validation:
    - `python -m unittest tests.test_eval`
    - manual review of the run B training log
  - Result:
    - evaluation now prints the actual checkpoint/device/output dir, defaults to checkpoint-matched eval directories, and preserves non-empty eval outputs instead of overwriting them

---

## 3. What Was Not Completed

- [x] Clean evaluation of the new `batch_size=2`, `lr=1e-4` checkpoint
  - Why not completed:
    - the eval command after run B reused an older shell `RUN_DIR` and targeted run A's checkpoint instead of `outputs/m2_baseline_bs2_lr1e4/best_model.pt`
  - Should this roll into the next step:
    - yes; this is the immediate next action

- [x] Final Stage 2 close decision
  - Why not completed:
    - the most promising run still lacks a clean evaluation artifact set
  - Should this roll into the next step:
    - yes; close/no-close depends on the checkpoint-matched eval result

- [x] Final prediction-distribution review for run B
  - Why not completed:
    - no clean `breast_level_predictions.csv` exists yet for the new checkpoint
  - Should this roll into the next step:
    - yes; inspect the new prediction spread immediately after the clean eval

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
    - records the interpretation of run B training and the mistaken old-checkpoint evaluation
  - Sync state:
    - yes; describes the current outstanding validation gap

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
    - yes; now safer for repeated server experimentation

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
- server run B training:
  - `python scripts/train_baseline.py --dataset paired --image-size 1024 --batch-size 2 --epochs 10 --lr 1e-4 --output-dir outputs/m2_baseline_bs2_lr1e4`
- latest local regression after eval hardening:
  - `python -m unittest tests.test_eval`

### What These Checks Actually Prove

- Proved:
  - the real paired split loads under the strict paired rules
  - single fallback behavior still passes smoke
  - paired training / evaluation plumbing works end to end on local smoke-sized data
  - run A was a real GPU run and exposed a weak collapsed baseline
  - run B training is far more stable than run A
  - eval artifact writing is now guarded against silent overwrite on repeated runs

- Not proved:
  - that run B already has a final accepted evaluation result
  - that the latest paired baseline can be closed as the official Stage 2 outcome
  - that no further optimization iteration is needed after the clean run B eval

### Missing or Weak Validation

- Missing validation 1:
  - clean eval of `outputs/m2_baseline_bs2_lr1e4/best_model.pt`
- Missing validation 2:
  - prediction-distribution and hardest-error review for the clean run B eval artifacts

---

## 6. Risks and Known Limitations

### P0 / blocking

- Stage 2 still lacks a clean checkpoint-matched eval artifact set for the most promising server run

### P1 / serious but not blocking

- run A proved the baseline can still collapse badly under unstable optimization settings
- repeated shell use on the server can still confuse train/eval pairing if commands are edited carelessly
- paired training still depends on torchvision pretrained EfficientNet-B2 weights being available in the runtime environment

### P2 / should improve later

- there is still no mainline full-CV paired runner
- smoke checks prove contract correctness, not final quality

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
- the eval hardening change improved workflow safety without changing the paired artifact contract

---

## 8. Recommended Next Entry Point

### Recommended first task

- run a clean evaluation against `outputs/m2_baseline_bs2_lr1e4/best_model.pt`

### Recommended first files to read

- `docs/contracts/contract_freeze_stage2.md`
- `docs/handoff/stage2_problem_report_20260330.md`
- `docs/handoff/stage2_analysis_report_20260330_bs2_lr1e4.md`
- `scripts/run_eval.py`
- `run_order.md`

### Recommended first checks

- `python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline_bs2_lr1e4/best_model.pt --image-size 1024 --batch-size 1`
- review `outputs/m2_baseline_bs2_lr1e4/eval/breast_level_predictions.csv`
- review `outputs/m2_baseline_bs2_lr1e4/eval/breast_level_metrics.json`

### Recommended decision to make before coding

- decide whether the clean run B eval is strong enough to close Stage 2
- if not, decide whether the next iteration should prioritize staged freezing or gradient accumulation

---

## 9. Handoff Guidance

- Do not treat run A as the current best baseline; it is the diagnosed failure case.
- Do not treat run B training-side AUROC as final evidence until the clean eval artifacts exist.
- Do not relax the strict paired contract to make experiments easier.
- When using explicit `--output-dir` during training, use the matching checkpoint path during eval instead of relying on an old shell `RUN_DIR`.
- If any future change touches task meaning, split protocol, or the frozen paired export semantics, re-freeze before implementation.

---

## 10. Final Verdict

- [ ] milestone can be cleanly closed
- [ ] milestone can be closed with documented limitations
- [x] milestone should remain open pending one last validation
- [ ] milestone should not be closed because the result is not yet reliable

Current conclusion:

Stage 2 implementation is complete and current optimization evidence is encouraging, but Stage 2 should remain open until `outputs/m2_baseline_bs2_lr1e4/best_model.pt` is evaluated cleanly and the resulting artifacts are reviewed.
