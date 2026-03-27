# Stage 2 Closeout

## Milestone Info

- Milestone ID: Stage 2
- Milestone name: strict paired CC/MLO breast-level baseline
- Status:
  - [ ] complete
  - [x] partially complete
  - [ ] blocked
  - [x] handed off with risks
- Date: 2026-03-27
- Related stage / branch:
  - `codex/docs-stage2-freeze`
  - `codex/feat-model-stage2`
- Related plan doc:
  - `docs/plan/plan_stage2.md`
- Related issue doc:
  - `docs/plan/issue_stage2.md`

---

## 1. Executive Summary

Stage 2 was meant to move the repository from the Stage 1 single-image fallback toward the first real paired breast-level baseline.

That implementation work is now in place:
- strict paired `(CC, MLO)` loading is enforced
- a shared-backbone EfficientNet-B2 paired baseline is implemented
- training and evaluation entrypoints now support `--dataset {single,paired}`
- paired evaluation exports only breast-level predictions and metrics
- a dedicated Stage 2 smoke script and regression tests were added

What is still missing is the formal real-data Stage 2 baseline run on the Linux training environment at `1024` resolution.

So Stage 2 engineering implementation is ready, but Stage 2 should not be treated as fully closed from a modeling / evidence perspective yet.

---

## 2. What Was Completed

- [x] Stage 2 contract freeze was synced to the repo docs
  - 对应代码/文档位置：
    - `docs/contracts/contract_freeze_stage2.md`
    - `docs/plan/plan_stage2.md`
    - `docs/plan/issue_stage2.md`
    - `docs/review/code_review.md`
  - 如何验证：
    - manual doc review against the frozen paired contract
  - 是否已经达到预期：
    - yes; the strict pair, fixed order, and probability-export rules are now explicit

- [x] Paired model, train loop, and checkpoint-selection path were implemented
  - 对应代码/文档位置：
    - `src/models/baseline.py`
    - `src/train/trainer.py`
    - `scripts/train_baseline.py`
  - 如何验证：
    - `python -m unittest tests.test_training_smoke`
    - `python -m unittest tests.test_stage2_smoke`
  - 是否已经达到预期：
    - yes for local engineering scope; the paired path trains and selects checkpoints by `breast_auroc`

- [x] Paired evaluation path and artifact contract were implemented
  - 对应代码/文档位置：
    - `src/eval/pipeline.py`
    - `src/eval/__init__.py`
    - `scripts/run_eval.py`
  - 如何验证：
    - `python -m unittest tests.test_eval`
    - `python -m unittest tests.test_stage2_smoke`
  - 是否已经达到预期：
    - yes; paired eval writes only `breast_level_predictions.csv` and `breast_level_metrics.json`

- [x] Strict paired dataset validation and view-order checks were implemented
  - 对应代码/文档位置：
    - `src/data/datasets.py`
    - `tests/test_datasets.py`
  - 如何验证：
    - `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1`
    - `python -m unittest tests.test_datasets`
  - 是否已经达到预期：
    - yes; incomplete pairs, duplicate views, and swapped `CC` / `MLO` semantics are rejected

- [x] Stage 2 smoke script and smoke regression test were added
  - 对应代码/文档位置：
    - `scripts/run_stage2_smoke.py`
    - `tests/test_stage2_smoke.py`
  - 如何验证：
    - `python -m unittest tests.test_stage2_smoke`
  - 是否已经达到预期：
    - yes for local synthetic smoke; not yet for the formal full-data server run

---

## 3. What Was Not Completed

- [x] Formal Linux server baseline run at `1024` resolution
  - 为什么没完成：
    - this workspace was used for implementation and light validation only; the user explicitly asked to hand off heavier training to the Linux server
  - 是否应该进入下一个 milestone：
    - yes; this is the immediate next action before Stage 2 can be cleanly closed

- [x] Formal Stage 2 performance interpretation
  - 为什么没完成：
    - no real baseline artifact under `outputs/m2_baseline/` exists yet from the frozen server configuration
  - 是否应该进入下一个 milestone：
    - yes; the result quality, collapse risk, and memory behavior must be reviewed after the server run

- [x] PR creation / remote review handoff
  - 为什么没完成：
    - implementation and local validation were completed, but no push / PR was opened from this workspace
  - 是否应该进入下一个 milestone：
    - yes if you want GitHub review before merge

---

## 4. Key Files and Changes

### Code
- `src/models/baseline.py`
  - 作用：single fallback model plus paired EfficientNet-B2 model definitions
  - 在本 milestone 中承担什么责任：
    - added `PairedEfficientNetB2Baseline` with fixed `(CC, MLO)` late fusion

- `src/train/trainer.py`
  - 作用：train / validate / checkpoint-selection utilities
  - 在本 milestone 中承担什么责任：
    - added paired loaders, paired train / validate loops, and `breast_auroc`-first checkpoint selection

- `src/data/datasets.py`
  - 作用：single and paired dataset loading
  - 在本 milestone 中承担什么责任：
    - enforced strict complete paired rows and fixed `(CC, MLO)` semantics

- `src/eval/pipeline.py`
  - 作用：prediction collection and artifact writing
  - 在本 milestone 中承担什么责任：
    - added paired breast-level prediction collection and breast-level-only export behavior

### Docs
- `docs/contracts/contract_freeze_stage2.md`
  - 作用：Stage 2 frozen interface / semantics
  - 是否已与实现同步：
    - yes

- `README.md`
  - 作用：top-level current-state description
  - 是否已与实现同步：
    - yes; now reflects Stage 2 active state and paired commands

- `docs/snapshots/project_snapshot.md`
  - 作用：repo snapshot for future agents
  - 是否已与实现同步：
    - yes; now reflects Stage 2 active entrypoints

### Config / Scripts / Assets
- `scripts/train_baseline.py`
  - 作用：public training entrypoint
  - 当前是否可直接复用：
    - yes; supports both `single` and `paired`

- `scripts/run_eval.py`
  - 作用：public evaluation entrypoint
  - 当前是否可直接复用：
    - yes; paired mode writes breast-level-only artifacts

- `scripts/run_stage2_smoke.py`
  - 作用：paired end-to-end smoke run and contract report
  - 当前是否可直接复用：
    - yes for plumbing checks; not a substitute for the formal baseline run

---

## 5. Validation Summary

### Validation Run
- `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1`
- `python -m unittest tests.test_datasets tests.test_eval tests.test_training_smoke tests.test_stage1_smoke tests.test_stage2_smoke`

### What These Checks Actually Prove
- 证明了什么：
  - the real paired split still loads after the stricter paired validation was added
  - single fallback behavior still passes its smoke regression
  - paired training / evaluation plumbing works end to end on synthetic smoke data
  - paired exports preserve probability range and do not generate image-level CSVs
  - swapped or malformed paired rows are rejected
- 没证明什么：
  - no real Stage 2 baseline quality claim
  - no evidence yet that the `1024` paired run fits the target Linux GPU memory budget
  - no evidence yet that the paired baseline avoids collapse on the real validation split

### Missing or Weak Validation
- 缺失验证 1:
  - formal real-data paired run at `1024` resolution with the frozen config
- 缺失验证 2:
  - human review of final training outputs and whether Stage 2 is good enough to close

---

## 6. Risks and Known Limitations

### P0 / blocking
- none found in the local implementation path after regression testing

### P1 / serious but not blocking
- Stage 2 still lacks the formal real-data baseline run, so no trustworthy modeling conclusion exists yet
- paired training currently depends on torchvision pretrained EfficientNet-B2 weights being available in the runtime environment

### P2 / should improve later
- there is still no mainline full-CV paired runner
- smoke checks prove contract correctness, but not final performance quality

---

## 7. Contract / Scope Notes

- [x] 完全在冻结 contract 内执行
- [ ] 有小范围偏离，但已说明
- [ ] 出现了 contract 级别问题
- [ ] 发生了实际 scope 漂移
- [ ] 没有正式 contract freeze

补充说明：
- public CLI expansion was limited to the planned `--dataset {single,paired}` switch
- Stage 1 single-image fallback behavior was preserved
- paired mode now enforces the frozen rules:
  - strict complete `(CC, MLO)` samples only
  - fixed `(CC, MLO)` ordering across dataset / model / eval / export
  - `prediction` exported as sigmoid probability

---

## 8. Recommended Next Entry Point

### Recommended first task
- Run the formal Stage 2 paired baseline on the Linux training environment with the frozen config.

### Recommended first files to read
- `docs/contracts/contract_freeze_stage2.md`
- `scripts/train_baseline.py`
- `scripts/run_eval.py`
- `scripts/run_stage2_smoke.py`
- `docs/handoff/stage2_closeout.md`

### Recommended first checks
- `python scripts/train_baseline.py --dataset paired --image-size 1024 --epochs 10 --batch-size <fit-on-server> --output-dir outputs/m2_baseline`
- `python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline/best_model.pt --image-size 1024 --output-dir outputs/m2_baseline/eval`
- review `outputs/m2_baseline/eval/breast_level_predictions.csv` and `outputs/m2_baseline/eval/breast_level_metrics.json`

### Recommended decision to make before coding
- decide whether Stage 2 should be closed after the formal server run or extended for another paired-baseline iteration
- decide whether a GitHub PR review is required before merging into the long-lived feature branches

---

## 9. Handoff Guidance

- Do not treat the local smoke pass as evidence of a strong baseline.
- Do not relax the strict paired contract to “make the run work”.
- If the `1024` paired run cannot fit even with batch size `1`, stop and ask the user instead of silently changing the contract.
- If any future change touches task meaning, split protocol, or the frozen paired export semantics, re-freeze before implementation.

---

## 10. Final Verdict

- [ ] milestone can be cleanly closed
- [ ] milestone can be closed with documented limitations
- [x] milestone should remain open pending one last validation
- [ ] milestone should not be closed because the result is not yet reliable

最后一句总结：
- 当前结论：Stage 2 implementation is ready for the formal server run, but Stage 2 should remain open until that real paired baseline is executed and reviewed.
