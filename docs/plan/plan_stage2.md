# plan_stage2

## Stage Title

- Stage ID: M2
- Stage name: First credible breast-level baseline
- Suggested branch family: `feat/model`
- Status:
  - [ ] draft
  - [x] active
  - [x] frozen
  - [ ] complete

---

## 1. Background

Stage 1 already proved the repository can:

- index the primary dataset
- build `breast_id`-grouped splits and fold artifacts
- train a minimal fallback baseline
- aggregate predictions back to breast level
- write evaluation and smoke-test artifacts

What remains is the modeling gap:

- the current runnable path is still a single-image fallback
- the smoke outputs show weak and tightly clustered predictions
- the task definition and design doc both point to breast-level classification on paired CC/MLO views

Stage 2 exists to move from structural proof to the first credible breast-level baseline.

---

## 2. Goal

Build a reproducible, leakage-safe, breast-level baseline using paired mammography views.

Primary target:

- paired CC/MLO inputs for the same `breast_id`
- a lightweight but credible CNN backbone, frozen around the design reference
- breast-level output and breast-level AUROC reporting
- strict paired-sample semantics with no runtime auto-repair for missing views

The stage is successful if the repository can run a complete baseline path with stable artifacts and a clear handoff to the next milestone.

---

## 3. In Scope

- [ ] freeze the Stage 2 baseline contract and artifact layout
- [ ] implement the paired CC/MLO breast-level modeling path
- [ ] keep the single-image fallback available as a diagnostic or smoke path
- [ ] add checkpointing, logging, and result artifact saving for the baseline run
- [ ] run one formal baseline experiment and record the outcome
- [ ] sync docs and closeout notes with the actual behavior
- [ ] preserve frozen `(CC, MLO)` ordering and probability-typed paired exports end to end

Use concrete deliverables, not vague ambitions.

---

## 4. Out of Scope

- [ ] detection / segmentation as the main line of work
- [ ] ROI-supervised or CAM-driven redesign as the default path
- [ ] external data mixing or augmentation from new datasets without approval
- [ ] hyperparameter search, benchmark tuning, or experiment-manager adoption
- [ ] changing label semantics, task definition, or split protocol
- [ ] multi-model ensembles or large-scale ablation campaigns

This section is mandatory.
It protects the stage from uncontrolled expansion.

---

## 5. Inputs and Dependencies

Required upstream inputs:

- docs:
  - `README.md`
  - `data/README.md`
  - `docs/task_definition.md`
  - `docs/plan/minimal_system_design.md`
  - `docs/handoff/stage1_handoff.md`
  - `docs/handoff/stage1_closeout.md`
  - `docs/ai/PROJECT_CONTEXT.md`
  - `docs/snapshots/project_snapshot.md`
- configs:
  - `.codex/config.toml`
  - `.codex/agents/implementer.toml`
  - `.codex/agents/reviewer.toml`
- code modules:
  - `src/data/`
  - `src/models/`
  - `src/train/`
  - `src/eval/`
  - `scripts/*.py`
- datasets / assets:
  - `data/raw/primary/train.csv`
  - `data/raw/primary/train_img.zip`
  - `data/raw/primary/test_img.zip`
  - `data/raw/primary/name_sid_submission.csv`
  - `data/processed/metadata/*`
  - `data/processed/splits/*`
- previous milestone outputs:
  - `outputs/m1_baseline/*`
  - `outputs/m1_smoke/*`

Blocking dependencies:

- agreement on the Stage 2 contract freeze
- enough compute to run the paired baseline at the chosen input size
- stable artifact paths for baseline runs and smoke runs
- ability to keep paired sample construction strict without inventing synthetic view completion

---

## 6. Proposed Issue Breakdown

### Issue 2.1

- Title: Freeze the Stage 2 paired-baseline contract
- Goal: lock the Stage 2 objective, interfaces, artifact layout, and validation expectations before code changes begin
- Main files / directories:
  - `docs/ai/PROJECT_CONTEXT.md`
  - `docs/contracts/contract_freeze_stage2.md`
  - `docs/plan/plan_stage2.md`
  - `docs/plan/issue_stage2.md`
- Expected output: a stable working boundary for the paired baseline

### Issue 2.2

- Title: Implement the paired CC/MLO breast-level baseline
- Goal: add the main Stage 2 training path that consumes paired views for the same `breast_id`
- Main files / directories:
  - `src/data/`
  - `src/models/`
  - `src/train/`
  - `scripts/train_baseline.py`
- Expected output: a trainable paired baseline with breast-level outputs and strict paired-sample handling

### Issue 2.3

- Title: Add checkpointing, logging, and artifact saving
- Goal: make the Stage 2 baseline run reproducible and reviewable
- Main files / directories:
  - `src/train/trainer.py`
  - `scripts/train_baseline.py`
  - `outputs/m2_baseline/`
- Expected output: config, logs, checkpoint, and summary artifacts for the baseline run

### Issue 2.4

- Title: Extend evaluation to paired baseline outputs
- Goal: collect predictions, preserve paired-view semantics, and write the baseline metrics in a stable artifact format
- Main files / directories:
  - `src/eval/`
  - `scripts/run_eval.py`
- Expected output: breast-level predictions and metrics artifacts for Stage 2

### Issue 2.5

- Title: Run the formal baseline and write closeout notes
- Goal: execute the formal Stage 2 run, inspect the results honestly, and write the handoff so the next milestone can start without rediscovering the current state
- Main files / directories:
  - `scripts/run_stage1_smoke.py` or a Stage 2 smoke/run wrapper if introduced
  - `docs/handoff/milestone_closeout.template.md`
  - `docs/handoff/stage2_closeout.md` if created later
- Expected output: a milestone closeout note and a clear next-step recommendation

Add or remove issues as needed, but keep them independently reviewable.

---

## 7. Deliverables

At the end of this stage, the repository should contain:

- [ ] a paired breast-level baseline implementation
- [ ] reproducible training and evaluation artifacts for the baseline
- [ ] a recorded run outcome and a handoff note for the next milestone
- [ ] explicit reporting of paired-sample validity and no silent sample repair

Possible deliverables:

- runnable code
- config file
- test / validation script
- benchmark report
- doc update
- closeout note

---

## 8. Acceptance Criteria

This stage is accepted only if:

- [ ] the paired baseline can run end to end with `breast_id`-grouped validation
- [ ] breast-level AUROC and the supporting prediction artifacts are reported
- [ ] the final docs and contract remain aligned with the implementation
- [ ] paired exports preserve frozen `(CC, MLO)` ordering and probability semantics

Each acceptance criterion should be externally checkable.

Bad:

- “looks good”
- “more complete”

Good:

- “script X runs successfully”
- “doc Y matches current behavior”
- “metric Z is reported with command and source”

---

## 9. Validation Plan

Minimum validation for this stage:

- local checks:
  - `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1 --save-preview`
  - `python scripts/build_dataset_index.py`
  - `python scripts/build_splits.py`
- focused tests:
  - `python -m unittest tests.test_datasets`
  - `python -m unittest tests.test_splits`
  - `python -m unittest tests.test_split_fold_assignment`
  - `python -m unittest tests.test_eval`
  - `python -m unittest tests.test_training_smoke`
- manual sanity checks:
  - inspect paired sample alignment for `CC` and `MLO`
  - inspect that incomplete paired candidates are rejected or filtered explicitly, not silently repaired
  - inspect breast-level prediction spread and ensure outputs are not trivially collapsed
  - confirm validation examples remain grouped by `breast_id`
  - confirm paired `breast_level_predictions.csv` exports probabilities in `[0, 1]`
- optional full-suite checks:
  - `python -m unittest`

For each deliverable, specify what evidence will count as validation.

---

## 10. Risks

Main risks in this stage:

- Risk 1: the paired baseline may remain slow or unstable at the design input size
- Risk 2: the model may still collapse to nearly constant predictions
- Risk 3: the implementation may drift from the intended breast-level semantics if the contract is not frozen early
- Risk 4: paired view order could drift between dataset, model, and export layers if not locked explicitly
- Risk 5: probability-vs-logit semantics could be blurred in exported artifacts if not frozen

For each risk, optionally note:

- trigger: running paired training at full resolution
- likely impact: weak or misleading validation results
- mitigation: keep a narrow smoke path and inspect prediction spread early

---

## 11. Stop Conditions

If any of these happen, stop and report:

- the requested change would require changing task definition, label semantics, or split protocol
- implementation would introduce image-level leakage across `breast_id`
- validation evidence conflicts with the intended breast-level semantics
- required dependencies or compute are missing
- scope expansion becomes unavoidable
- paired mode would need runtime auto-repair for incomplete two-view samples
- paired export semantics would no longer clearly distinguish probability from logit

Examples:

- required dependency is missing
- implementation would violate frozen interface
- validation evidence conflicts with intended semantics
- scope expansion becomes unavoidable

---

## 12. Handoff Note

At stage close, produce or update:

- closeout summary: Stage 2 result, what worked, and what did not
- key changed files: model, train, eval, docs, and contract files
- open problems: performance limits, collapse risk, or remaining ambiguity
- suggested next stage entry point: controlled improvement on top of the first credible paired baseline
- explicit note on whether strict paired-sample filtering and frozen `(CC, MLO)` ordering held in the final run
