1. 修改了哪些文件
- [src/data/splits.py](d:/MyProject/Breast-Cancer-Detection-Model/src/data/splits.py)
- [src/data/__init__.py](d:/MyProject/Breast-Cancer-Detection-Model/src/data/__init__.py)
- [scripts/build_splits.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/build_splits.py)
- [tests/test_split_fold_assignment.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_split_fold_assignment.py)
- [primary_fold_assignment.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_fold_assignment.csv)
- [primary_fold_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_fold_summary.json)
- [primary_split_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_split_summary.json)

2. 每个文件的作用
- [splits.py](d:/MyProject/Breast-Cancer-Detection-Model/src/data/splits.py)：在现有 holdout split 逻辑上补充完整 fold assignment、fold summary，以及 train/val 与 fold 的一致性检查。
- [__init__.py](d:/MyProject/Breast-Cancer-Detection-Model/src/data/__init__.py)：导出 `FOLD_ASSIGNMENT_FIELDS`，避免后续脚本和测试硬编码字段。
- [build_splits.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/build_splits.py)：生成 split 时额外落盘 `fold_assignment.csv` 和 `fold_summary.json`，并打印 fold 信息。
- [test_split_fold_assignment.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_split_fold_assignment.py)：最小测试，验证 fold 数量、唯一性、train/val 与 fold 对应关系。
- [primary_fold_assignment.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_fold_assignment.csv)：每个 `breast_id` 对应的完整 fold mapping。
- [primary_fold_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_fold_summary.json)：每个 fold 的统计、warning、以及 train/val 来源说明。
- [primary_split_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_split_summary.json)：在原 summary 基础上补充 fold assignment 与 fold summary 信息。

3. fold assignment 文件结构
- 文件：[primary_fold_assignment.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_fold_assignment.csv)
- 字段：
- `breast_id`：breast 级唯一 id
- `fold`：fold 编号，当前为 `0~4`
- `target`：`is_malignant`
- `num_images`：该 `breast_id` 对应的图像数，当前实际都是 `2`

4. fold summary 包含哪些统计信息
- 文件：[primary_fold_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_fold_summary.json)
- 顶层包含：
- `total_breasts`
- `fold_count`
- `is_stratified`
- `used_fallback`
- `fallback_reason`
- `val_fold`
- `train_folds`
- `train_val_derived_from_fold_assignment`
- `warnings`
- `folds`
- 每个 `folds[i]` 包含：
- `fold`
- `breast_count`
- `image_count`
- `malignant_count`
- `non_malignant_count`
- `malignant_ratio`
- `warnings`

5. train/val 与 fold 的关系
- 当前 `train/val` 不是单独随机出来的。
- 在 stratified 成功路径下，我把完整 `StratifiedGroupKFold` materialize 成 5-fold mapping，再明确规定：
- `fold 0 -> val`
- `fold 1,2,3,4 -> train`
- 这层关系已经写进：
- [primary_split_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_split_summary.json)
- [primary_fold_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_fold_summary.json)

6. 做了哪些一致性检查
- `fold_assignment` 中每个 `breast_id` 只出现一次
- `fold` 是否连续完整，当前应为 `[0,1,2,3,4]`
- `train` 和 `val` 的 `breast_id` 是否无 overlap
- `train/val` 是否与 `fold_assignment` 一致，当前 `val` 必须等于 `fold 0`
- paired/single 原有 coverage 与 leakage 检查保持不变
- 每个 fold 的标签分布是否存在极端失衡
- 极端失衡只记 `warning`，不报错

7. 补了哪些测试
- 新增 [tests/test_split_fold_assignment.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_split_fold_assignment.py)
- 覆盖：
- `fold_assignment` 中 `breast_id` 无重复
- fold 数量正确且为 `0~4`
- `target` 非空，`num_images` 正确
- `train/val` 与 `fold 0` 对应关系一致
- 新 artifact 文件可成功落盘
- 实际跑过：
```bash
python -m unittest tests.test_splits tests.test_split_fold_assignment
python -m unittest tests.test_index_builder tests.test_datasets tests.test_splits tests.test_split_fold_assignment tests.test_training_smoke
```

8. 给出最小运行方式
```bash
python scripts/build_splits.py
python -m unittest tests.test_split_fold_assignment
```

9. 给出一段 `fold_assignment.csv` 示例
```text
breast_id,fold,target,num_images
00406_L,1,0,2
00406_R,3,0,2
00668_R,0,1,2
00798_R,4,1,2
01041_R,0,0,2
01134_R,2,0,2
```

10. 明确说明本次修改没有破坏 Issue 1.3 / 1.4 的现有逻辑
- 没有重写 split 逻辑，只是在现有 stratified holdout 上补了完整 fold mapping。
- 原有 train/val CSV 结构和文件名没变，`SingleImageDataset`、`PairedBreastDataset`、`train_baseline.py` 不需要改。
- 现有 train/val 统计仍然是：
- paired train `520` / val `130`
- single train `1040` / val `260`
- 只是在此基础上补充了 650 行完整 fold assignment 和 5-fold summary。
- 这次没有改 dataset / trainer / dataloader，没有扩展成 cross-validation 训练框架。
- `docs/plan/issue_stage1.md` 仍不存在，本次继续按要求使用 [docs/gitflow/issue/issue_stage1.md](d:/MyProject/Breast-Cancer-Detection-Model/docs/gitflow/issue/issue_stage1.md) 作为等价文档。