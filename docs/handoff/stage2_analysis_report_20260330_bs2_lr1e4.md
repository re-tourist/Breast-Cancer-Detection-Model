# Stage 2 Analysis Report

## Scope

This report analyzes the new Stage 2 training run executed with:

- dataset: `paired`
- image size: `1024`
- batch size: `2`
- epochs: `10`
- learning rate: `1e-4`

It also explains why the subsequent evaluation output should not be treated as the evaluation result for that new run.

---

## 1. Executive Summary

The new training log is strongly improved compared with the previous `batch_size=1`, `lr=1e-3` experiment.

The optimization behavior now looks healthy:

- validation loss stays in a reasonable range
- validation AUROC climbs quickly above `0.88`
- the best training-side validation `breast_auroc` reaches `0.9668` at epoch `9`

However, the evaluation command that followed did not evaluate this new checkpoint. It evaluated the older checkpoint under `outputs/m2_baseline_20260330_021213/best_model.pt`, which is the weak earlier run with `breast_auroc=0.5389`.

So the correct conclusion is:

- the new hyperparameter choice looks very promising from the training log
- the new run still needs a clean evaluation pass against the actual new checkpoint before it can be accepted as the latest Stage 2 result

---

## 2. What Happened

### New training command

The training command used:

```bash
python scripts/train_baseline.py \
  --dataset paired \
  --image-size 1024 \
  --batch-size 2 \
  --epochs 10 \
  --lr 1e-4 \
  --output-dir outputs/m2_baseline_bs2_lr1e4
```

This produced:

- output dir: `outputs/m2_baseline_bs2_lr1e4`
- best epoch: `9`
- best metric: `breast_auroc=0.9668`
- best checkpoint: `outputs/m2_baseline_bs2_lr1e4/best_model.pt`

### Evaluation command actually used an older checkpoint

The later evaluation log printed:

- checkpoint: `outputs/m2_baseline_20260330_021213/best_model.pt`
- breast auroc: `0.5389`

That checkpoint path belongs to the older run, not the new `outputs/m2_baseline_bs2_lr1e4` run.

Therefore the evaluation result is valid for the old run only. It does not measure the new model.

---

## 3. Training Log Analysis

### Why the new training run looks much better

Training-side validation metrics:

- epoch 1: `val_loss=1.0551`, `breast_auroc=0.6575`
- epoch 2: `val_loss=0.7932`, `breast_auroc=0.8862`
- epoch 3: `val_loss=0.7946`, `breast_auroc=0.8702`
- epoch 4: `val_loss=0.8275`, `breast_auroc=0.8881`
- epoch 5: `val_loss=0.4116`, `breast_auroc=0.9659`
- epoch 6: `val_loss=0.5125`, `breast_auroc=0.9353`
- epoch 7: `val_loss=0.4306`, `breast_auroc=0.9592`
- epoch 8: `val_loss=0.8610`, `breast_auroc=0.9464`
- epoch 9: `val_loss=0.7304`, `breast_auroc=0.9668`
- epoch 10: `val_loss=0.8340`, `breast_auroc=0.9617`

These signals are qualitatively different from the failed earlier run:

- no massive `val_loss` explosion to double- or triple-digit values
- no collapse of AUROC after a brief early peak
- no sign of the previous severe instability pattern

### What changed

Compared with the failed run, two important optimization changes were made:

- `batch_size: 1 -> 2`
- `lr: 1e-3 -> 1e-4`

This is fully consistent with the previous diagnosis that the earlier setup was too noisy and too aggressive.

### What this implies

The poor earlier result was likely not a fundamental failure of the paired Stage 2 design. It was much more likely an optimization failure caused by a bad hyperparameter regime.

That is an important distinction:

- if the design were fundamentally broken, this kind of immediate training-curve improvement would be unlikely
- instead, the new run suggests the paired baseline is viable and was previously being trained under unstable settings

---

## 4. Why The Eval Result Is Mixed Up

The likely cause is shell-variable reuse.

The new training command wrote to:

- `outputs/m2_baseline_bs2_lr1e4`

But the evaluation command used:

- `--checkpoint "$RUN_DIR/best_model.pt"`
- `--output-dir "$RUN_DIR/eval"`

and the resulting log shows that `RUN_DIR` still pointed to:

- `outputs/m2_baseline_20260330_021213`

So the shell variable did not match the explicit training output directory used in the new train command.

This is a workflow bug, not a model bug.

---

## 5. Repository Fixes Applied

To reduce this class of mistakes, the repository has been updated as follows:

- `scripts/run_eval.py`
  - now prints a clear startup summary before evaluation
  - prints dataset, device, checkpoint, validation split, and actual output directory
  - preserves prior non-empty evaluation output directories instead of overwriting them
  - when a checkpoint is explicitly provided and no output directory is passed, it now defaults to `checkpoint_parent/eval`
- `run_order.md`
  - rewritten with a safer Linux workflow
  - now emphasizes keeping train and eval on the same explicit run directory
- `tests/test_eval.py`
  - extended with regression coverage for the new eval output-directory behavior

These changes do not guess user intent, but they make the actual checkpoint/output choice visible and avoid silent eval artifact overwrites.

---

## 6. Correct Next Action

Run evaluation again against the new checkpoint:

```bash
python scripts/run_eval.py \
  --dataset paired \
  --checkpoint outputs/m2_baseline_bs2_lr1e4/best_model.pt \
  --image-size 1024 \
  --batch-size 1
```

This will now default to writing under:

- `outputs/m2_baseline_bs2_lr1e4/eval`

without needing a separate `--output-dir`.

---

## 7. Interim Judgment

### What can already be said

- the new hyperparameter regime is much better
- the earlier diagnosis about unstable optimization was correct
- `batch_size=2` and `lr=1e-4` appear to move the model into a stable and high-performing validation regime

### What cannot yet be claimed

- the official latest Stage 2 eval number for the new run
- the final prediction distribution for the new run
- the final false-positive / false-negative pattern for the new run

Those still depend on rerunning evaluation with the correct checkpoint.

---

## 8. Final Verdict

The new training result is highly encouraging and likely represents a real fix to the previous optimization failure.

But the evaluation evidence is currently mixed because the eval command targeted the wrong checkpoint. The next step is not another retraining run. The next step is a clean re-evaluation of `outputs/m2_baseline_bs2_lr1e4/best_model.pt`.
