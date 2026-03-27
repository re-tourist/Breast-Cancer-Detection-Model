# issue_stage2

This file lists the issues for a single stage.
Each issue should be independently executable, reviewable, and closable.

---

# Issue 2.1 — Freeze the Stage 2 paired-baseline contract

## Background

Stage 1 already proved the pipeline can run end to end, but the current baseline is still the single-image fallback and its predictions are weak and tightly clustered. Stage 2 needs a frozen boundary before code work starts so the paired baseline does not drift into a new task definition or a new output meaning.

## Suggested Branch

- `docs`

## Goal

Write the Stage 2 contract and make the project context explicit so the paired baseline can be implemented, reviewed, and closed out without reinterpreting the task midstream.

## In Scope

- [ ] fill `docs/ai/PROJECT_CONTEXT.md`
- [ ] create `docs/contracts/contract_freeze_stage2.md`
- [ ] align `docs/plan/plan_stage2.md` with the frozen objective and artifact layout
- [ ] record the validation expectations and stop conditions
- [ ] freeze strict paired-sample, fixed `(CC, MLO)` ordering, and probability-export semantics

## Out of Scope

- [ ] model code changes
- [ ] training loop changes
- [ ] evaluation logic changes

## Relevant Files / Paths

- `README.md`
- `data/README.md`
- `docs/task_definition.md`
- `docs/plan/minimal_system_design.md`
- `docs/handoff/stage1_closeout.md`
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/contracts/contract_freeze_stage2.md`

## Constraints

- do not change the breast-level task definition
- do not change split semantics
- do not introduce new dependencies
- keep the contract readable enough for later review
- do not leave paired missing-view behavior implicit

## Suggested Workflow

1. read the task definition and the Stage 1 closeout
2. identify the frozen objective and the frozen interfaces
3. write the contract around the paired breast-level baseline
4. cross-check the stage plan for contradictions
5. record the stop conditions and validation contract

## Done When

- [ ] the project context is explicit about Stage 2
- [ ] the contract freeze covers inputs, outputs, interfaces, and validation
- [ ] the stage plan and the contract agree on the paired breast-level baseline
- [ ] the contract makes strict pair completeness, fixed view order, and probability export semantics explicit

## Required Validation

- command / check 1: manual consistency check against `README.md`, `docs/task_definition.md`, `docs/plan/minimal_system_design.md`, and `docs/handoff/stage1_closeout.md`
- command / check 2: verify the contract does not redefine the task or relax leakage safety
- manual sanity check: confirm the stage boundary points to a paired breast-level baseline, not a detection task
- manual sanity check: confirm the freeze forbids silent pair repair, view-order swaps, and logit/probability ambiguity
- optional broader check: have the reviewer subagent read the contract and stage plan together

## Report Format

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- the contract would need to redefine the task or the split protocol
- the freeze would need a new dependency or a major architecture change
- the implementation boundary cannot be expressed clearly in writing

---

# Issue 2.2 — Implement the paired CC/MLO breast-level baseline

## Background

The design reference already says the main line should be a paired CC/MLO breast-level classifier with a lightweight pretrained CNN backbone. Stage 1 kept a single-image fallback as the runnable safety net; Stage 2 needs the mainline paired path.

## Suggested Branch

- `feat/model`

## Goal

Implement the main paired breast-level modeling path so the repository can train on `CC + MLO` inputs for the same `breast_id` and emit breast-level predictions.

## In Scope

- [ ] paired data loading for the same breast
- [ ] a shared-backbone or equivalent paired-view model path
- [ ] minimal config support for the paired baseline
- [ ] keep the single-image fallback available for smoke or diagnostic use

## Out of Scope

- [ ] detection / segmentation
- [ ] external data
- [ ] experiment orchestration frameworks

## Relevant Files / Paths

- `src/data/datasets.py`
- `src/data/transforms.py`
- `src/models/baseline.py`
- `src/train/trainer.py`
- `scripts/train_baseline.py`
- `data/processed/metadata/*`
- `data/processed/splits/*`

## Constraints

- do not break `breast_id` grouping
- do not leak images across train and validation
- do not rename stable output meanings without approval
- keep the model simple enough to review
- preserve the frozen `(CC, MLO)` ordering end to end
- do not repair incomplete pairs at runtime

## Suggested Workflow

1. inspect the existing single-image path and the paired index artifacts
2. add the paired-view data path with the smallest viable change
3. wire the paired model into the training loop
4. verify shapes, labels, and breast grouping
5. run a narrow smoke check before broadening validation

## Done When

- [ ] the training path consumes paired CC/MLO inputs for the same breast
- [ ] the model produces breast-level outputs
- [ ] the paired path can be validated on a narrow smoke-sized run
- [ ] paired rows with invalid or missing view semantics fail explicitly instead of being auto-repaired

## Required Validation

- command / check 1: `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1 --save-preview`
- command / check 2: `python -m unittest tests.test_datasets`
- manual sanity check: confirm paired samples align on `breast_id` and views are not mixed across splits
- manual sanity check: confirm the model receives `CC` first and `MLO` second consistently
- optional broader check: `python -m unittest tests.test_splits`

## Report Format

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- paired inputs cannot be implemented without leakage
- the implementation would require a task-definition change
- the model path cannot remain reviewable and minimal

---

# Issue 2.3 — Add checkpointing, logging, and artifact saving

## Background

Stage 2 baseline results must be reproducible and reviewable. The repository already has a fallback baseline output layout, but the paired baseline needs the same level of artifact discipline.

## Suggested Branch

- `feat/train`

## Goal

Make the Stage 2 baseline save the config, checkpoint, logs, and result artifacts needed for later review and handoff.

## In Scope

- [ ] checkpoint writing
- [ ] metrics summary writing
- [ ] config snapshotting
- [ ] log output capture
- [ ] stable output directory layout for the Stage 2 baseline

## Out of Scope

- [ ] new metrics that do not support the stage goal
- [ ] experiment-manager adoption
- [ ] unrelated training refactors

## Relevant Files / Paths

- `src/train/trainer.py`
- `scripts/train_baseline.py`
- `outputs/m2_baseline/`

## Constraints

- preserve existing semantics where possible
- keep output layout repository-relative
- do not hide validation failures behind logging changes
- keep paired metrics and checkpoints keyed to breast-level metrics only

## Suggested Workflow

1. identify the minimum artifact set needed for review
2. add or adapt checkpoint and logging code
3. write config and summary artifacts in a stable layout
4. run a short train smoke to verify outputs

## Done When

- [ ] the baseline run emits a config snapshot and a checkpoint
- [ ] the run writes a summary that can be reviewed later
- [ ] the output layout is stable enough for the next milestone to reuse
- [ ] the summary makes it clear whether pretrained weights and strict paired data contracts were actually used

## Required Validation

- command / check 1: `python -m unittest tests.test_training_smoke`
- command / check 2: a short paired-baseline training run that writes all expected artifacts
- manual sanity check: inspect the saved files and confirm they match the documented layout
- optional broader check: rerun the smoke with a different seed or batch size if needed

## Report Format

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- the artifact layout would need to change mid-issue
- the run cannot save the expected files without semantic drift
- the change would require a broad training refactor

---

# Issue 2.4 — Extend evaluation to paired baseline outputs

## Background

The task metric is breast-level AUROC, so the evaluation path has to emit breast-level predictions and write a result set that is easy to inspect.

## Suggested Branch

- `feat/eval`

## Goal

Make the evaluation pipeline collect predictions, preserve paired-view semantics, and write the baseline metrics in a stable artifact format.

## In Scope

- [ ] breast-level prediction collection
- [ ] AUROC reporting
- [ ] prediction artifact writing
- [ ] evaluation summary output
- [ ] paired-mode breast-level-only export semantics

## Out of Scope

- [ ] threshold optimization
- [ ] complex experiment dashboards
- [ ] detection / segmentation metrics

## Relevant Files / Paths

- `src/eval/aggregation.py`
- `src/eval/metrics.py`
- `src/eval/pipeline.py`
- `scripts/run_eval.py`

## Constraints

- keep the evaluation meaning breast-level
- keep output columns stable unless a contract revision is approved
- do not introduce image-level leakage or hidden averaging tricks
- export paired `prediction` values as sigmoid probabilities, not raw logits
- preserve `(CC, MLO)` order in all paired identifiers and paths

## Suggested Workflow

1. inspect the current evaluation pipeline and outputs
2. adapt the paired prediction collector and output writer as needed
3. verify breast-level labels and predictions line up
4. confirm the report is written in a reviewable format

## Done When

- [ ] evaluation emits breast-level predictions and metrics
- [ ] the artifact layout is stable and documented
- [ ] the report can be used in a milestone review without re-running the full experiment
- [ ] paired mode does not emit `image_level_predictions.csv`

## Required Validation

- command / check 1: `python -m unittest tests.test_eval`
- command / check 2: `python scripts/run_eval.py --checkpoint ... --image-size ... --output-dir ...`
- manual sanity check: inspect `breast_level_predictions.csv` and `breast_level_metrics.json`
- manual sanity check: confirm paired `prediction` values are in `[0, 1]` and paired row fields keep `CC` before `MLO`
- optional broader check: compare the breast-level labels against the split artifacts

## Report Format

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- the evaluation semantics would have to change to make the code work
- the output meaning no longer matches breast-level classification
- the change would require a larger train/eval redesign

---

# Issue 2.5 — Run the formal baseline and write closeout notes

## Background

The stage is not complete until there is a real run, an honest readout, and a handoff document. Stage 1 already has smoke evidence; Stage 2 should add a formal baseline result and a decision on the next step.

## Suggested Branch

- `feat/scripts`

## Goal

Execute the Stage 2 baseline, inspect the result honestly, and write the milestone closeout so the next milestone can start without rediscovering the current state.

## In Scope

- [ ] run the formal baseline
- [ ] capture the key metrics and output files
- [ ] write the closeout summary
- [ ] identify open risks and the next entry point

## Out of Scope

- [ ] major model redesign
- [ ] large hyperparameter search
- [ ] changing the milestone objective during closeout

## Relevant Files / Paths

- `scripts/run_stage1_smoke.py` or a Stage 2 smoke/run wrapper if introduced
- `docs/handoff/milestone_closeout.template.md`
- `docs/handoff/stage2_closeout.md` if created later
- `outputs/m2_baseline/`

## Constraints

- report the actual result, not the desired result
- do not claim success if the baseline is still collapsing
- keep the handoff readable for the next person
- report whether strict paired-sample filtering and fixed `(CC, MLO)` ordering held in the formal run

## Suggested Workflow

1. run the formal baseline using the frozen config
2. inspect outputs, metrics, and prediction spread
3. record the limitations honestly
4. write or update the closeout note
5. recommend the next issue or milestone entry point

## Done When

- [ ] the formal baseline result is captured
- [ ] the stage closeout notes the actual risks and limitations
- [ ] the next milestone entry point is obvious

## Required Validation

- command / check 1: the formal baseline run itself
- command / check 2: a review of the generated result artifacts
- manual sanity check: inspect whether predictions are still collapsed or meaningfully separated
- optional broader check: run the reviewer subagent on the closeout summary

## Report Format

1. changed files
2. what changed in each file
3. validation run
4. known risks / limitations
5. suggested next issue

## Stop and Report If

- the run cannot be interpreted honestly
- the closeout would need to change the milestone objective
- the result evidence is too weak to support a next-step recommendation
