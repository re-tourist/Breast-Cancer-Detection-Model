1. 修改了哪些文件

- [src/data/splits.py](d:/MyProject/Breast-Cancer-Detection-Model/src/data/splits.py)
- [src/data/__init__.py](d:/MyProject/Breast-Cancer-Detection-Model/src/data/__init__.py)
- [scripts/build_splits.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/build_splits.py)
- [tests/test_splits.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_splits.py)
- [primary_paired_breast_split_train.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_paired_breast_split_train.csv)
- [primary_paired_breast_split_val.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_paired_breast_split_val.csv)
- [primary_single_image_split_train.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_single_image_split_train.csv)
- [primary_single_image_split_val.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_single_image_split_val.csv)
- [primary_split_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_split_summary.json)

2. 每个文件的作用

- [splits.py](d:/MyProject/Breast-Cancer-Detection-Model/src/data/splits.py)：实现 `breast_id` 分组 holdout、paired/single 映射、泄漏检查、summary 构建和 split 落盘。
- [__init__.py](d:/MyProject/Breast-Cancer-Detection-Model/src/data/__init__.py)：导出 Issue 1.3 的 split 接口，保持 `src.data` 统一入口。
- [build_splits.py](d:/MyProject/Breast-Cancer-Detection-Model/scripts/build_splits.py)：最小 CLI，重复生成 split 文件并打印统计。
- [test_splits.py](d:/MyProject/Breast-Cancer-Detection-Model/tests/test_splits.py)：覆盖可复现性、无 leakage、schema 保持、fallback、错误输入。
- [primary_paired_breast_split_train.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_paired_breast_split_train.csv) / [primary_paired_breast_split_val.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_paired_breast_split_val.csv)：可直接给 `PairedBreastDataset` 使用的 train/val split。
- [primary_single_image_split_train.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_single_image_split_train.csv) / [primary_single_image_split_val.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_single_image_split_val.csv)：由 paired split 映射得到、可直接给 `SingleImageDataset` 使用的 train/val split。
- [primary_split_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_split_summary.json)：保存 split 策略、统计和检查结果。

3. split 的分组单位是什么

- 固定是 `breast_id`。
- split 构建只在 paired breast-level index 上做一次，再把同一批 `breast_id` 映射到 single-image index。

4. split 是如何保证 paired / single 边界一致的

- 先在 [primary_paired_breast_index.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_paired_breast_index.csv) 上生成 train/val 的 `breast_id` 集合。
- 再按这两个 `breast_id` 集合过滤 [primary_single_image_index.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_single_image_index.csv)。
- single 侧不做任何独立随机。
- 输出 split CSV 保留原索引 schema，所以当前 [datasets.py](d:/MyProject/Breast-Cancer-Detection-Model/src/data/datasets.py) 可以直接读取。

5. 输出了哪些 split 文件，保存到哪里

保存在 [data/processed/splits](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits)：

- [primary_paired_breast_split_train.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_paired_breast_split_train.csv)
- [primary_paired_breast_split_val.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_paired_breast_split_val.csv)
- [primary_single_image_split_train.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_single_image_split_train.csv)
- [primary_single_image_split_val.csv](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_single_image_split_val.csv)
- [primary_split_summary.json](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits/primary_split_summary.json)

6. 做了哪些 leakage 检查

- train 和 val 的 `breast_id` 集合是否完全不相交
- paired split 是否完整覆盖原 paired index，且无重复、无遗漏
- single split 是否严格由 paired split 的 `breast_id` 映射得到
- single / paired 两边是否共享完全一致的 `breast_id` 边界
- paired split 后每行的 `image_id_cc`、`image_id_mlo`、`image_path_cc`、`image_path_mlo` 是否非空
- train / val 是否都非空
- summary 中还记录了是否触发 stratified fallback，以及原因

7. train / val 的 breast 数、image 数、标签分布统计

本次实际运行 `python scripts/build_splits.py` 得到：

- paired train：520 breasts，520 rows，`0=395, 1=125`
- paired val：130 breasts，130 rows，`0=98, 1=32`
- single train：520 breasts，1040 images，`0=790, 1=250`
- single val：130 breasts，260 images，`0=196, 1=64`
- leakage overlap：0

8. 给出最小运行方式

```bash
python scripts/build_splits.py
python -m unittest tests.test_splits
```

我实际还验证了 split 文件可直接被现有 loader 读取：

```bash
python scripts/check_dataset_loading.py --dataset single --single-index data/processed/splits/primary_single_image_split_train.csv --batch-size 2 --num-batches 1
python scripts/check_dataset_loading.py --dataset paired --paired-index data/processed/splits/primary_paired_breast_split_train.csv --batch-size 2 --num-batches 1
```

9. 给出一次实际输出示例

```text
Split artifacts built successfully
- split strategy: stratified_group_holdout
- random_state: 42
- val_ratio: 0.2
- paired train: 520 breasts, 520 rows, labels 0=395, 1=125
- paired val: 130 breasts, 130 rows, labels 0=98, 1=32
- single train: 520 breasts, 1040 images, labels 0=790, 1=250
- single val: 130 breasts, 260 images, labels 0=196, 1=64
- leakage check: overlap_count=0
- fallback: used=False reason=''
```

10. 明确说明有哪些假设、限制或待确认点

- `docs/plan/issue_stage1.md` 已存在；本次按你的要求使用了 [docs/plan/issue_stage1.md](D:/MyProject/Breast-Cancer-Detection-Model/docs/plan/issue_stage1.md)。
- 默认策略是 `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` 取首个 fold 作为 val；这是单次 holdout 产物，不是 k-fold 框架。
- 只有当 `val_ratio` 不适合该 stratified 方案，或类别样本不足时，才明确回退到 `GroupShuffleSplit`，并把原因写进 summary。
- split CSV 没有新增 `split` 列，而是靠文件名区分 train / val；这是有意保持 schema 与 Issue 1.1 索引一致，便于直接复用现有 dataset loader。
- 没有实现 Issue 1.4 / 1.5 的训练、评估、AUROC 或实验管理。
- 实际验证已通过：
  - `python -m unittest tests.test_index_builder tests.test_datasets tests.test_splits`
  - `python scripts/build_splits.py`
  - 用 split CSV 跑 `check_dataset_loading.py` 的 single / paired smoke test 均通过。
