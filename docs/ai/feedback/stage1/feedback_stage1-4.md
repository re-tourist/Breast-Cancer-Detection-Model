1. 修改了哪些文件

- [src/models/baseline.py](d:/MyProject/Breast-Cancer-Detection-Model/src/models/baseline.py)
- [src/models/__init__.py](d:/MyProject/Breast-Cancer-Detection-Model/src/models/__init__.py)
- [src/train/trainer.py](d:/MyProject/Breast-Cancer-Detection-Model/src/train/trainer.py)
- [src/train/__init__.py](d:/MyProject/Breast-Cancer-Detection-Model/src/train/__init__.py)
- [scripts/train_baseline.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/train_baseline.py)
- [tests/test_training_smoke.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_training_smoke.py)

实际运行生成了：
- [config.json](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline/config.json)
- [metrics_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline/metrics_summary.json)
- [best_model.pt](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline/best_model.pt)

2. 每个文件的作用

- [baseline.py](d:/MyProject/Breast-Cancer-Detection-Model/src/models/baseline.py)：定义最小单图 CNN baseline。
- [trainer.py](d:/MyProject/Breast-Cancer-Detection-Model/src/train/trainer.py)：实现 dataloader 构建、`pos_weight` 计算、train loop、val loop、image-level 指标和轻量 breast mean aggregation 指标。
- [train_baseline.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/train_baseline.py)：最小训练入口，读取 Issue 1.3 的 split CSV，训练 1 个单图 baseline，并保存 config、summary、checkpoint。
- [test_training_smoke.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_training_smoke.py)：覆盖 CLI 端到端 smoke 和单类验证集 AUROC 安全退化。
- 两个 `__init__.py`：只做最小导出，方便后续复用。

3. baseline 模型是什么，为什么这样选

模型是一个自定义 `MinimalSingleImageCNN`，结构是 4 个下采样卷积块，通道数固定 `16 -> 32 -> 64 -> 128`，最后接全局平均池化和线性分类头，输出单个 binary logit。

这样选的原因是：
- 当前环境实际是 CPU，先保证稳定可跑
- 不依赖重型预训练 backbone
- 和当前 `SingleImageDataset`、3 通道灰度复制输入完全兼容
- 结构足够清楚，后续 Issue 1.5 / 更后面的 paired 主线可以平滑替换模型而不动训练骨架

4. train/val loop 做了什么

- train loop：
  - 从 Issue 1.3 的 single-image split CSV 构建 train dataloader
  - 前向、`BCEWithLogitsLoss`、反向传播、Adam 更新
  - 按 epoch 汇总 `train_loss`
- val loop：
  - 读取 val split
  - 计算 `val_loss`
  - 计算 image-level `accuracy` 和 `AUROC`
  - 收集 `breast_id`，把同一 breast 的两张图概率取平均
  - 额外计算 `breast_mean_accuracy` 和 `breast_mean_auroc`
- checkpoint：
  - 按 `val_loss` 选 best
  - 保存 `best_model.pt`

5. 使用了哪些指标

- `train_loss`
- `val_loss`
- `image_accuracy`
- `image_auroc`
- 轻量附加项：
  - `breast_mean_accuracy`
  - `breast_mean_auroc`

如果某次验证集只有单类，AUROC 会返回 `None`，不会中断训练。

6. 如何运行最小训练

真实数据 smoke 建议这样跑：

```bash
python scripts/train_baseline.py --epochs 1 --batch-size 8 --image-size 512
```

默认接口仍保留：
- `--train-split`
- `--val-split`
- `--archive-path`
- `--image-root`
- `--image-size`
- `--batch-size`
- `--epochs`
- `--lr`
- `--seed`
- `--num-workers`
- `--output-dir`

7. 给出一次实际运行输出示例

```text
Epoch 1/1 train_loss=1.0648 val_loss=1.0770 image_acc=0.2462 image_auroc=0.4482 breast_mean_acc=0.2462 breast_mean_auroc=0.4225
Training finished successfully
- best epoch: 1
- best val loss: 1.0770
- wrote: D:\MyProject\Breast-Cancer-Detection-Model\outputs\m1_baseline\config.json
- wrote: D:\MyProject\Breast-Cancer-Detection-Model\outputs\m1_baseline\metrics_summary.json
- wrote: D:\MyProject\Breast-Cancer-Detection-Model\outputs\m1_baseline\best_model.pt
```

8. 输出结果保存到哪里

默认保存到 [outputs/m1_baseline](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline)：

- [config.json](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline/config.json)
- [metrics_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline/metrics_summary.json)
- [best_model.pt](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline/best_model.pt)

9. 做了哪些 smoke test / 单元测试

已实际通过：

```bash
python -m unittest tests.test_index_builder tests.test_datasets tests.test_splits tests.test_training_smoke
```

新增的训练相关测试覆盖了：
- `train_baseline.py` CLI 端到端 1 epoch smoke
- 配置、summary、checkpoint 落盘
- 单类验证集时 `image_auroc` / `breast_mean_auroc` 返回 `None`

还实际跑通了真实数据 smoke：

```bash
python scripts/train_baseline.py --epochs 1 --batch-size 8 --image-size 512
```

10. 明确说明有哪些假设、限制或待确认点

- `docs/plan/issue_stage1.md` 仍不存在；这次继续按你的规则使用了 [issue_stage1.md](d:/MyProject/Breast-Cancer-Detection-Model/docs/gitflow/issue/issue_stage1.md)。
- 当前环境实际只有 CPU，所以真实 smoke 用了 `--image-size 512`；代码默认值仍保留 `1024`，但在 CPU 上会更慢。
- 当前 baseline 是 single-image image-level 训练闭环，不是 paired breast-level 主线训练。
- 我补了轻量的 `breast_id` mean aggregation 验证指标，但没有引入完整 evaluator 框架，没有越界到 Issue 1.5。
- 真实 smoke 的指标现在只是“能跑通”的基线，不代表效果已经合理；当前任务重点是训练-验证闭环首次成立。

如果你下一步要按 issue 粒度提交，我也可以继续给你补一份 Issue 1.4 对应的 `git add` 命令和标准三段 commit 信息。