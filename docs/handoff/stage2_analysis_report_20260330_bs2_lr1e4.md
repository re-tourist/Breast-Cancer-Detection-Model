# Stage 2 Analysis Report

## Scope

This report analyzes the new Stage 2 training run executed with:

- dataset: `paired`
- image size: `1024`
- batch size: `2`
- epochs: `10`
- learning rate: `1e-4`

It also explains why the subsequent evaluation output first looked inconsistent, and what was later confirmed after the user shared the full `outputs/m2_baseline/` directory.

---

## 1. Executive Summary

The new training log is strongly improved compared with the previous `batch_size=1`, `lr=1e-3` experiment.

The optimization behavior now looks healthy:

- validation loss stays in a reasonable range
- validation AUROC climbs quickly above `0.88`
- the best training-side validation `breast_auroc` reaches `0.9668` at epoch `9`

However, that first interpretation was incomplete. After the full `outputs/m2_baseline/` directory was returned, it became clear that the server-side evaluation did use the new checkpoint, but it was executed with an older copy of `run_eval.py` that still defaulted paired eval outputs to `outputs/m2_baseline/eval`.

So the correct conclusion is:

- the new hyperparameter choice looks very promising from the training log
- the new checkpoint already has evidence of strong eval performance
- a clean rerun on the updated eval script is still needed so the artifact path and eval log match the actual checkpoint lineage

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

### What the later evidence showed

The user later provided this evaluation log:

- checkpoint: `outputs/m2_baseline_bs2_lr1e4/best_model.pt`
- breast auroc: `0.9665`
- wrote:
  - `/home/.../outputs/m2_baseline/eval/breast_level_predictions.csv`
  - `/home/.../outputs/m2_baseline/eval/breast_level_metrics.json`

That combination is inconsistent with the current local `run_eval.py` implementation. The current script would:

- print a `Starting evaluation` header with device and output dir
- default the output dir to `checkpoint_parent/eval` when `--checkpoint` is passed explicitly

The absence of those startup lines and the legacy output path together imply that the Linux server evaluated the correct new checkpoint with an older script revision.

So the metric itself is strong evidence for run B, but the artifact landed in the legacy `outputs/m2_baseline/eval/` directory instead of the checkpoint-matched `outputs/m2_baseline_bs2_lr1e4/eval/`.

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

The current best explanation is stale server code, not shell-variable reuse.

Evidence:

- the eval log printed the new checkpoint path correctly
- the eval log did not include the startup lines added in the newer local script
- the output still defaulted to the legacy paired path `outputs/m2_baseline/eval`

This means the server very likely ran an older `run_eval.py` that still had the old default output-dir behavior.

---

## 5. Repository Fixes Applied

To reduce this class of mistakes, the repository has been updated as follows:

- `scripts/run_eval.py`
  - now prints a clear startup summary before evaluation
  - prints dataset, device, checkpoint, validation split, and actual output directory
  - preserves prior non-empty evaluation output directories instead of overwriting them
  - when a checkpoint is explicitly provided and no output directory is passed, it now defaults to `checkpoint_parent/eval`
  - writes `eval_config.json` so the actual checkpoint and output directory are preserved in the artifact set itself
- `run_order.md`
  - rewritten with a safer Linux workflow
  - now emphasizes keeping train and eval on the same explicit run directory
- `tests/test_eval.py`
  - extended with regression coverage for the new eval output-directory behavior and eval config capture

These changes do not guess user intent, but they make the actual checkpoint/output choice visible and avoid silent eval artifact overwrites.

---

## 6. Correct Next Action

First, pull the latest branch on the Linux server so the updated `run_eval.py` is actually the one being executed.

Then run evaluation again against the new checkpoint:

```bash
git pull --ff-only

python scripts/run_eval.py \
  --dataset paired \
  --checkpoint outputs/m2_baseline_bs2_lr1e4/best_model.pt \
  --image-size 1024 \
  --batch-size 1
```

This will now default to writing under:

- `outputs/m2_baseline_bs2_lr1e4/eval`

without needing a separate `--output-dir`, and it will also write `eval_config.json`.

---

## 7. Interim Judgment

### What can already be said

- the new hyperparameter regime is much better
- the earlier diagnosis about unstable optimization was correct
- `batch_size=2` and `lr=1e-4` appear to move the model into a stable and high-performing validation regime
- the returned eval metric under the new checkpoint path is already very strong: `breast_auroc=0.9665`

### What cannot yet be claimed

- a clean artifact lineage under `outputs/m2_baseline_bs2_lr1e4/eval/`
- the final prediction-distribution interpretation for the clean rerun
- the final false-positive / false-negative pattern for the clean rerun

Those still depend on rerunning evaluation with the correct checkpoint.

---

## 8. Final Verdict

The new training result is highly encouraging, and the returned eval metric strongly suggests the optimization failure has been fixed.

But the current artifact lineage is still messy because the server used an older eval script and wrote the result into the legacy `outputs/m2_baseline/eval/` directory. The next step is not another retraining run. The next step is a clean re-evaluation of `outputs/m2_baseline_bs2_lr1e4/best_model.pt` after pulling the updated branch.
