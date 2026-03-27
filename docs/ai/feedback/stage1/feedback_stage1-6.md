1. 修改了哪些文件

修改了 [run_stage1_smoke.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/run_stage1_smoke.py) 和 [test_stage1_smoke.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_stage1_smoke.py)。

本次实际生成的 smoke 产物在 [outputs/m1_smoke](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke)：
[stage1_smoke_report.md](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/stage1_smoke_report.md)、[metrics_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/train/metrics_summary.json)、[best_model.pt](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/train/best_model.pt)、[image_level_predictions.csv](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/eval/image_level_predictions.csv)、[breast_level_predictions.csv](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/eval/breast_level_predictions.csv)、[breast_level_metrics.json](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/eval/breast_level_metrics.json)。

2. 每个文件的作用

[scripts/run_stage1_smoke.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/run_stage1_smoke.py) 是 Issue 1.6 的最小端到端 smoke 脚本。它复用已有 `train_baseline.py` 和 `run_eval.py`，顺序跑训练与评估，保存 stdout/stderr 日志，读取产物并生成一份 sanity report。

[tests/test_stage1_smoke.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_stage1_smoke.py) 是最小集成测试。它用合成 split 和 zip 图像调起 smoke 脚本，验证 report、train summary、eval metrics 和 prediction artifact 都能生成。

3. smoke test 采用了什么最小配置

这次实际 smoke 配置是：

- train split: [primary_single_image_split_train.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_single_image_split_train.csv)
- val split: [primary_single_image_split_val.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_single_image_split_val.csv)
- split context: [primary_split_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_split_summary.json)，其中 `val_fold=0`
- epochs: `1`
- batch size: `8`
- image size: `512`
- device: `cpu`
- selection metric: `auto`
- aggregation: `mean`
- output dir: [outputs/m1_smoke](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke)

4. 端到端串起了哪些已有模块

这次没有重发明流程，只做了薄胶水层：

- 复用 Issue 1.3 的 single-image split artifacts
- 复用 Issue 1.2 的 `SingleImageDataset` 和 transforms
- 复用 Issue 1.4 / 1.4.x 的 [train_baseline.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/train_baseline.py) 与 `trainer.py`
- 复用 Issue 1.5 的 [run_eval.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/run_eval.py) 和 `src/eval/`
- 新脚本只负责串联、记录日志、汇总关键路径、写 sanity report

5. 输出了哪些日志/产物，保存到哪里

都保存在 [outputs/m1_smoke](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke)：

- 训练日志: [train_stdout.log](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/train_stdout.log), [train_stderr.log](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/train_stderr.log)
- 评估日志: [eval_stdout.log](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/eval_stdout.log), [eval_stderr.log](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/eval_stderr.log)
- 训练产物: [config.json](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/train/config.json), [metrics_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/train/metrics_summary.json), [best_model.pt](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/train/best_model.pt)
- 评估产物: [image_level_predictions.csv](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/eval/image_level_predictions.csv), [breast_level_predictions.csv](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/eval/breast_level_predictions.csv), [breast_level_metrics.json](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/eval/breast_level_metrics.json)
- sanity report: [stage1_smoke_report.md](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/stage1_smoke_report.md)

6. sanity report 包含哪些结论

报告在 [stage1_smoke_report.md](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/stage1_smoke_report.md)，核心结论是：

- 标签对齐看起来正常：val split 的 breast-level 标签分布 `{'0': 98, '1': 32}` 与评估输出一致
- loss 能正常计算且保持 finite，没有 NaN / inf
- 预测有明显塌缩风险：breast-level prediction `min=0.5655`, `max=0.5922`, `std=0.0049`
- breast-level AUROC 计算流程跑通，实际得到 `0.4225`
- 这次结果更像“闭环已成立”的 sanity run，不像“已有合理效果”的 baseline

报告里明确写了：
- 当前闭环成立
- 当前主要限制是近似常数输出
- 进入 M2 前的主要风险是带着结构正确但很弱的单图 baseline 继续推进

7. 给出一次最小运行方式

```bash
python scripts/run_stage1_smoke.py
```

测试模式最小验证：

```bash
python -m unittest tests.test_stage1_smoke
```

8. 给出一段实际运行输出示例

```text
Stage 1 smoke test finished successfully
- output dir: D:\MyProject\Breast-Cancer-Detection-Model\outputs\m1_smoke
- report: D:\MyProject\Breast-Cancer-Detection-Model\outputs\m1_smoke\stage1_smoke_report.md
- train metrics: D:\MyProject\Breast-Cancer-Detection-Model\outputs\m1_smoke\train\metrics_summary.json
- eval metrics: D:\MyProject\Breast-Cancer-Detection-Model\outputs\m1_smoke\eval\breast_level_metrics.json
- breast auroc: 0.4225
- collapse suspected: True
```

9. 补了哪些测试或验证步骤

新增了 [tests/test_stage1_smoke.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_stage1_smoke.py)，覆盖：

- smoke 脚本能在超小配置下启动并完成 train + eval
- `stage1_smoke_report.md` 成功生成
- train/eval 关键 artifact 成功生成
- report 中能看到关键产物路径和 sanity 结论字段

实际已验证：

```bash
python -m unittest tests.test_stage1_smoke
python -m unittest tests.test_index_builder tests.test_datasets tests.test_splits tests.test_split_fold_assignment tests.test_training_smoke tests.test_eval tests.test_stage1_smoke
python scripts/run_stage1_smoke.py
```

10. 明确说明这次实现如何对应 issue_stage1.md 中 Issue 1.6 的 Goal / Scope / Deliverables / Acceptance Criteria

对应关系是直接对齐的：

- Goal：新增 [run_stage1_smoke.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/run_stage1_smoke.py)，并实际跑出 [stage1_smoke_report.md](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke/stage1_smoke_report.md)
- Scope：选了一个 CPU 友好的最小配置，串起数据读取、训练、验证、breast-level 聚合评估，保存日志与结果，并记录异常观察
- Deliverables：已有 smoke 脚本、sanity report、日志、metrics、checkpoint、prediction artifact
- Acceptance Criteria：闭环已完整跑通；breast-level AUROC 已实际生成；报告里给了明确 sanity 判断，而不是只写“跑过了”；也明确指出了当前的基础问题是输出接近常数、效果不可信

路径适配说明：
- 本次权威 issue 文档实际使用的是 [docs/plan/issue_stage1.md](D:/MyProject/Breast-Cancer-Detection-Model/docs/plan/issue_stage1.md)
- sanity report 放在 `outputs/m1_smoke/` 而不是 `docs/reports/`，这是有意保持它作为一次运行产物，和现有 `outputs/m1_baseline/` 风格一致
- 本次没有重构 trainer 或 eval 框架，只加了最小胶水层，未越界到 Issue 1.7 的文档整理工作
