1. 修改了哪些文件
- [src/eval/aggregation.py](d:/MyProject/Breast-Cancer-Detection-Model/src/eval/aggregation.py)
- [src/eval/metrics.py](d:/MyProject/Breast-Cancer-Detection-Model/src/eval/metrics.py)
- [src/eval/pipeline.py](d:/MyProject/Breast-Cancer-Detection-Model/src/eval/pipeline.py)
- [src/eval/__init__.py](d:/MyProject/Breast-Cancer-Detection-Model/src/eval/__init__.py)
- [scripts/run_eval.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/run_eval.py)
- [tests/test_eval.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_eval.py)

2. 每个文件的作用
- [aggregation.py](d:/MyProject/Breast-Cancer-Detection-Model/src/eval/aggregation.py)：对一份 prediction rows 按 `breast_id` 聚合，支持 `mean` 和 `max`。
- [metrics.py](d:/MyProject/Breast-Cancer-Detection-Model/src/eval/metrics.py)：计算 breast-level AUROC，并处理单类安全退化。
- [pipeline.py](d:/MyProject/Breast-Cancer-Detection-Model/src/eval/pipeline.py)：收集 single-image validation predictions、构建 evaluation 结果、写出 artifact。
- [__init__.py](d:/MyProject/Breast-Cancer-Detection-Model/src/eval/__init__.py)：导出最小评估接口。
- [run_eval.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/run_eval.py)：最小评估入口，读取 checkpoint + val split，输出 image-level 和 breast-level artifact。
- [test_eval.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_eval.py)：覆盖 mean/max、target 一致性、单类 AUROC、artifact 落盘。

3. aggregation 接口支持哪些输入与聚合方式
- 核心接口是 `aggregate_prediction_rows(...)`，输入是一份 prediction table，不写死为 single-image。
- 只要求输入行里至少有：
- `breast_id`
- `target`
- `prediction`
- 可选 `image_id` 或其他 item id，用于导出可追踪引用。
- 当前支持：
- `mean`
- `max`
- 输出行至少包含：
- `breast_id`
- `target`
- `prediction`
- `num_items_aggregated`
- `item_ids`

4. AUROC 如何计算，单类时如何处理
- 用 `sklearn.metrics.roc_auc_score` 计算二分类 AUROC。
- 如果 breast-level `target` 只有一个类别，返回 `None`，不报错中断。
- `breast_level_metrics.json` 会同时写：
- `breast_auroc`
- `auroc_available`
- `auroc_reason`

5. 输出了哪些结果文件，保存到哪里
- 默认评估输出目录是 [outputs/m1_baseline/eval](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline/eval)
- 产物包括：
- [image_level_predictions.csv](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline/eval/image_level_predictions.csv)
- [breast_level_predictions.csv](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline/eval/breast_level_predictions.csv)
- [breast_level_metrics.json](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline/eval/breast_level_metrics.json)

6. 简单评估入口脚本如何运行
- 脚本是 [run_eval.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/run_eval.py)
- 它会：
- 读取 `best_model.pt`
- 读取 val split
- 生成 image-level prediction rows
- 聚合成 breast-level prediction
- 输出 breast-level AUROC 和 artifact

7. 给出一次最小运行示例
```bash
python scripts/run_eval.py --checkpoint outputs/m1_baseline/best_model.pt --image-size 512 --output-dir outputs/m1_baseline/eval
```

8. 给出一段实际输出示例
```text
Evaluation finished successfully
- checkpoint: outputs\m1_baseline\best_model.pt
- aggregation: mean
- image predictions: 260
- breast predictions: 130
- breast auroc: 0.4225
- auroc available: True
```

`breast_level_predictions.csv` 示例：
```text
breast_id,target,prediction,num_items_aggregated,item_ids
00668_R,1,0.5715279579162598,2,00668_R_CC|00668_R_MLO
01041_R,0,0.5786077082157135,2,01041_R_CC|01041_R_MLO
02930_R,1,0.580634742975235,2,02930_R_CC|02930_R_MLO
```

9. 补了哪些测试
- `mean` 聚合正确
- `max` 聚合正确
- 同一 `breast_id` 内 `target` 不一致时报错
- 单类 AUROC 返回 `None`
- `image_level_predictions.csv` / `breast_level_predictions.csv` / `breast_level_metrics.json` 成功生成
- 实际跑过：
```bash
python -m unittest tests.test_eval
python -m unittest tests.test_index_builder tests.test_datasets tests.test_splits tests.test_split_fold_assignment tests.test_training_smoke tests.test_eval
python scripts/run_eval.py --checkpoint outputs/m1_baseline/best_model.pt --image-size 512 --output-dir outputs/m1_baseline/eval
```

10. 明确说明这次实现如何对应 `issue_stage1.md` 中 Issue 1.5 的原始 Goal / Scope / Deliverables / Acceptance Criteria
- Goal：
  - 已建立最小评估脚本框架 [run_eval.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/run_eval.py)，支持从验证预测输出中完成 breast-level 聚合和 AUROC 计算。
- Scope：
  - 支持收集 image-level predictions
  - 支持基于 `breast_id` 的聚合接口
  - 支持 `mean` / `max`
  - 支持 AUROC 与单类安全退化
  - 支持保存验证结果表
- Deliverables：
  - `src/eval/` 最小评估模块已补齐
  - AUROC 逻辑已独立实现
  - breast-level prediction CSV 已导出
  - 简单评估入口脚本已提供
- Acceptance Criteria：
  - 可以对 prediction table 正确做 `breast_id` 聚合
  - 可以输出 breast-level AUROC
  - 结果文件包含 `breast_id / target / prediction`
  - 逻辑是独立模块，可直接给 M2 复用
- 路径差异说明：
  - 仓库里没有 `docs/plan/issue_stage1.md`，本次按你的要求使用了等价文档 [docs/gitflow/issue/issue_stage1.md](d:/MyProject/Breast-Cancer-Detection-Model/docs/gitflow/issue/issue_stage1.md)
- 范围控制说明：
  - 没有重构整个 trainer
  - 没有引入复杂 evaluator framework
  - 没有开始 paired 双分支训练
  - 没有越界到 Milestone 2