# Stage 2 Problem Report

## Run Info

- Date: 2026-03-30
- Run directory: `outputs/m2_baseline_20260330_021213`
- Train config:
  - dataset: `paired`
  - model: `PairedEfficientNetB2Baseline`
  - image size: `1024`
  - batch size: `1`
  - epochs: `10`
  - learning rate: `1e-3`
  - device: `gpu (cuda:0, NVIDIA GeForce RTX 4090)`
- Eval config:
  - dataset: `paired`
  - aggregation: `paired_direct`
  - output files:
    - `outputs/m2_baseline_20260330_021213/eval/breast_level_predictions.csv`
    - `outputs/m2_baseline_20260330_021213/eval/breast_level_metrics.json`

---

## 1. Executive Summary

The formal Stage 2 paired baseline run completed on the Linux GPU server, so the engineering path and runtime environment are now confirmed.

The modeling result is not good enough to close Stage 2:
- best validation `breast_auroc` is only `0.5389`
- best validation `breast_accuracy` is `0.7462`
- the validation majority-class baseline is `98 / 130 = 0.7538`

This means the model learned only a weak ranking signal and did not produce a useful breast-level classifier. The result is not a contract failure or a GPU/runtime failure. It is a training-quality failure under the current optimization setup.

The strongest evidence points to unstable optimization and severe negative-class bias under `1024` resolution, `batch_size=1`, and `lr=1e-3`.

---

## 2. Key Evidence

### Main metrics

- validation breasts: `130`
  - negatives: `98`
  - positives: `32`
- best epoch: `4`
- best `breast_auroc`: `0.5389`
- best `breast_accuracy`: `0.7462`
- majority-negative baseline accuracy: `0.7538`

### Training instability

The training history is unstable instead of steadily improving:

- epoch 1: `val_loss=3.47`, `breast_auroc=0.5045`
- epoch 2: `val_loss=1.61`, `breast_auroc=0.5255`
- epoch 3: `val_loss=26.58`, `breast_auroc=0.5365`
- epoch 4: `val_loss=13.04`, `breast_auroc=0.5389`
- epoch 8: `val_loss=151.88`, `breast_auroc=0.4120`
- epoch 10: `val_loss=6.30`, `breast_auroc=0.3268`

This is not the pattern of a stable pretrained fine-tune. The validation objective explodes and the ranking metric collapses after the early peak.

### Prediction distribution

The paired eval export shows strong collapse toward the negative side:

- prediction min: `3.08e-16`
- prediction max: `0.5392`
- prediction mean: `0.0276`
- prediction std: `0.0725`
- predictions `>= 0.5`: `1 / 130`
- predictions `< 0.5`: `129 / 130`

Class-wise prediction means:

- negatives mean prediction: `0.0248`
- positives mean prediction: `0.0361`

The gap is real but very small. The model is barely separating the classes.

### Hard failure examples

- highest prediction in the full validation set is a negative:
  - `breast_id=14084_R`, `target=0`, `prediction=0.5392`
- highest positive prediction is only:
  - `breast_id=02930_R`, `target=1`, `prediction=0.2044`
- some positives are predicted almost exactly zero:
  - `breast_id=72545_R`, `target=1`, `prediction=3.08e-16`
  - `breast_id=93384_L`, `target=1`, `prediction=9.21e-14`

This is not just a threshold-calibration issue. Positive cases are not being ranked strongly enough.

---

## 3. What This Run Proves

### Confirmed

- the formal Stage 2 paired path runs end to end on the Linux GPU server
- the strict paired `(CC, MLO)` contract is still executable at `1024`
- checkpoint selection by `breast_auroc` works as designed
- paired eval export semantics are correct:
  - one row per `breast_id`
  - probability-valued `prediction`
  - no paired `image_level_predictions.csv`

### Not confirmed

- a reliable Stage 2 baseline
- useful positive-class separation
- stable optimization under the current train setup

---

## 4. Root Cause Assessment

### Primary cause: optimization is too aggressive

The most likely primary cause is that `lr=1e-3` is too high for this setup:

- pretrained EfficientNet-B2 backbone
- paired late-fusion head
- `1024` resolution
- `batch_size=1`
- full fine-tuning

Evidence:

- `val_loss` swings from `1.58` to `151.88`
- `breast_auroc` peaks early and then degrades badly
- the final epochs are worse than near-random

This is consistent with unstable updates and poor fine-tuning dynamics.

### Secondary cause: strong negative bias under class imbalance

The model outputs almost all probabilities near zero. That means the current setup is not recovering enough positive signal even though `pos_weight=3.16` is present.

Evidence:

- only `1` prediction exceeds `0.5`
- positive mean prediction is only `0.0361`
- many positive samples are effectively assigned zero risk

So the problem is not that the threshold is too strict. The logits themselves are mostly pushing toward the negative class.

### What does not look like the main cause

- not a CPU/GPU mismatch: this run used CUDA on an RTX 4090
- not a split leak issue: grouped split checks are already clean
- not a paired contract issue: paired sample counts and eval behavior are consistent
- not an export bug: predictions are valid probabilities in `[0, 1]`

---

## 5. Recommended Fix Strategy

## First rerun: minimal change only

Keep all Stage 2 contracts fixed and change only optimization stability.

Recommended first rerun:

- keep dataset: `paired`
- keep image size: `1024`
- keep batch size: `1`
- keep epochs: `10`
- keep split and eval contract unchanged
- change learning rate from `1e-3` to `1e-4`

Reason:

- this isolates the most likely failure mode first
- it preserves comparability with the current run
- it avoids mixing optimization changes with task or data changes

## Second rerun only if needed

If the `1e-4` rerun is still unstable or still collapses toward negatives, the next minimal step should be staged optimization, not data-contract relaxation.

Recommended second step:

- freeze the EfficientNet backbone for the first `1-2` epochs
- train only the fusion head first
- then unfreeze and continue at a low learning rate

Reason:

- batch size `1` makes full-backbone updates noisy
- the fusion head may need to stabilize before backbone adaptation

## Third step if the second still fails

Consider increasing effective batch size without changing the frozen contract:

- keep physical batch size `1`
- add gradient accumulation to reach an effective batch size of `4` or `8`

This is preferable to changing split protocol, changing task definition, or silently lowering image size for the formal baseline.

---

## 6. What Not To Do Next

- do not change the task definition
- do not change the grouped split protocol
- do not relax the strict paired `(CC, MLO)` contract
- do not treat threshold tuning as the main fix
- do not claim this run as a meaningful Stage 2 baseline
- do not change multiple major variables at once

The current evidence is strong enough that the next experiment should be a controlled optimization fix, not a broad redesign.

---

## 7. Recommended Next Experiment

### Goal

Test whether the poor result is mainly caused by unstable fine-tuning rather than by an invalid paired baseline design.

### Proposed command shape

Training:

```bash
python scripts/train_baseline.py \
  --dataset paired \
  --image-size 1024 \
  --batch-size 1 \
  --epochs 10 \
  --lr 1e-4 \
  --output-dir outputs/m2_baseline_lr1e4
```

Evaluation:

```bash
python scripts/run_eval.py \
  --dataset paired \
  --checkpoint outputs/m2_baseline_lr1e4/best_model.pt \
  --image-size 1024 \
  --batch-size 1 \
  --output-dir outputs/m2_baseline_lr1e4/eval
```

### Success criteria for the rerun

At minimum, the rerun should show both:

- a more stable validation curve without extreme `val_loss` explosion
- a clear improvement over the current `0.5389` AUROC

If accuracy remains near the majority baseline but AUROC improves materially, that still counts as progress. If AUROC stays near `0.54` and predictions remain compressed near zero, then the next step should move to staged freezing or gradient accumulation.

---

## 8. Final Verdict

- the formal server run is complete
- the current Stage 2 implementation is operational
- the current Stage 2 baseline result is not reliable enough to close the milestone

Current conclusion:

Stage 2 should remain open. The next action should be a controlled rerun with a lower learning rate, followed by another prediction-distribution review before any larger model or workflow change is approved.
