1. 修改了哪些文件
- [src/train/trainer.py](d:/MyProject/Breast-Cancer-Detection-Model/src/train/trainer.py)
- [scripts/train_baseline.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/train_baseline.py)
- [src/train/__init__.py](d:/MyProject/Breast-Cancer-Detection-Model/src/train/__init__.py)
- [tests/test_training_smoke.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_training_smoke.py)

2. 每个修改的作用
- [trainer.py](d:/MyProject/Breast-Cancer-Detection-Model/src/train/trainer.py)：新增 `resolve_selection_metric` 和 `is_better_selection`，把 best checkpoint 选择从固定 `val_loss` 改成可配置 selection metric。
- [train_baseline.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/train_baseline.py)：新增 `--selection-metric`，并把 selection 信息写入 `config.json` 和 `metrics_summary.json`。
- [__init__.py](d:/MyProject/Breast-Cancer-Detection-Model/src/train/__init__.py)：导出新的 selection 相关接口。
- [test_training_smoke.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_training_smoke.py)：补 selection/fallback/summary 的最小测试。

3. best checkpoint 选择逻辑现在是什么
- `auto` 模式下按优先级选本 epoch 的选择指标：
- `breast_mean_auroc` 可用时用它，越大越好。
- 否则回退到 `image_auroc`，越大越好。
- 再否则回退到 `val_loss`，越小越好。
- 不同 epoch 之间先比 `priority_rank`，再比指标值，所以更高优先级的指标永远覆盖更低优先级指标。

4. 默认 selection metric 是什么，为什么
- 默认是 `--selection-metric auto`。
- 这是因为项目冻结主任务是 breast-level malignant probability prediction，所以优先用 `breast_mean_auroc`；只有它不可算时才向下回退。

5. fallback 机制是什么
- `auto` 模式会自动回退：`breast_mean_auroc -> image_auroc -> val_loss`。
- `explicit` 模式不会跨指标回退。
- 显式指定 `breast_mean_auroc` 或 `image_auroc` 时，如果某个 epoch 该指标是 `None`，该 epoch 不参与 best 更新。
- 如果整个训练过程中显式指标始终不可用，会直接报错，提示改用 `auto` 或 `val_loss`。

6. `metrics_summary.json` 新增了哪些字段
- 顶层新增：
- `primary_selection_metric`
- `selection_mode`
- `best_metric_name`
- `best_metric_value`
- `fallback_used`
- `fallback_reason`
- 每个 epoch 的 `history` 新增：
- `selection_metric_name`
- `selection_metric_value`
- `selection_fallback_used`
- `selection_fallback_reason`

7. 补了哪些测试
- `auto` 优先选择 `breast_mean_auroc`
- `auto` 回退到 `image_auroc`
- `auto` 回退到 `val_loss`
- 高优先级 selection 胜过低优先级 selection
- 显式 `image_auroc` 在整个训练都不可用时抛出清晰错误
- 端到端脚本 smoke test 现在额外校验 `metrics_summary.json` 的 selection 字段

8. 给出一次最小运行方式
```bash
python -m unittest tests.test_training_smoke
python scripts/train_baseline.py --epochs 1 --batch-size 8 --image-size 512 --output-dir outputs/m1_baseline
```

9. 给出一段新的 summary 输出示例
```text
Epoch 1/1 train_loss=1.0648 val_loss=1.0770 image_acc=0.2462 image_auroc=0.4482 breast_mean_acc=0.2462 breast_mean_auroc=0.4225 selection=breast_mean_auroc:0.4225
Training finished successfully
- primary selection metric: breast_mean_auroc
- best epoch: 1
- best metric: breast_mean_auroc=0.4225
- fallback used: False
- fallback reason: None
```

10. 明确说明这次修补没有越界到 Issue 1.5
- 这次只改了训练阶段的 checkpoint 选择和 summary 记录，没有新建 evaluator framework。
- 没有新增 breast-level prediction CSV/JSON artifact。
- 没有改模型、dataset、split、transform 主体逻辑。
- `docs/plan/issue_stage1.md` 仍不存在，本次继续按要求使用 [docs/gitflow/issue/issue_stage1.md](d:/MyProject/Breast-Cancer-Detection-Model/docs/gitflow/issue/issue_stage1.md) 作为等价文档。
- 已实际验证：
- `python -m unittest tests.test_index_builder tests.test_datasets tests.test_splits tests.test_training_smoke`
- `python scripts/train_baseline.py --epochs 1 --batch-size 8 --image-size 512 --output-dir outputs/m1_baseline`