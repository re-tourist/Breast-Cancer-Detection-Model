1. 修改了哪些文件
- [src/data/index_builder.py](D:/MyProject/Breast-Cancer-Detection-Model/src/data/index_builder.py)
- [src/data/__init__.py](D:/MyProject/Breast-Cancer-Detection-Model/src/data/__init__.py)
- [scripts/build_dataset_index.py](D:/MyProject/Breast-Cancer-Detection-Model/scripts/build_dataset_index.py)
- [tests/__init__.py](D:/MyProject/Breast-Cancer-Detection-Model/tests/__init__.py)
- [tests/test_index_builder.py](D:/MyProject/Breast-Cancer-Detection-Model/tests/test_index_builder.py)
- [data/processed/metadata/primary_single_image_index.csv](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_single_image_index.csv)
- [data/processed/metadata/primary_paired_breast_index.csv](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_paired_breast_index.csv)
- [data/processed/metadata/primary_index_report.json](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_index_report.json)

2. 每个文件的作用
- [src/data/index_builder.py](D:/MyProject/Breast-Cancer-Detection-Model/src/data/index_builder.py): 定义字段常量、严格校验逻辑、single-image index 构建、paired breast-level index 构建、统计报告生成、CSV/JSON 写出辅助函数。
- [src/data/__init__.py](D:/MyProject/Breast-Cancer-Detection-Model/src/data/__init__.py): 暴露后续可复用的公开接口和字段常量。
- [scripts/build_dataset_index.py](D:/MyProject/Breast-Cancer-Detection-Model/scripts/build_dataset_index.py): 最小 CLI 入口，默认读取 `train.csv` 和 `train_img.zip`，严格模式下构建并落盘索引与报告。
- [tests/__init__.py](D:/MyProject/Breast-Cancer-Detection-Model/tests/__init__.py): 让 `python -m unittest tests.test_index_builder` 稳定导入。
- [tests/test_index_builder.py](D:/MyProject/Breast-Cancer-Detection-Model/tests/test_index_builder.py): 覆盖成功构建、重复 `image_id`、错误 view 集合、breast 内 pathology 冲突、缺失 zip 成员、paired 缺失配对这 6 条路径。
- [data/processed/metadata/primary_single_image_index.csv](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_single_image_index.csv): 生成后的 single-image 样本索引。
- [data/processed/metadata/primary_paired_breast_index.csv](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_paired_breast_index.csv): 生成后的 paired breast-level 样本索引。
- [data/processed/metadata/primary_index_report.json](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_index_report.json): 统计摘要、异常计数、详细校验结果。

3. single-image index 的字段定义
- `image_id`: 由 `Path(image_path).stem` 派生。
- `breast_id`: 原始 `breast_id`。
- `view`: 由原始 `cc_mlo` 显式映射。
- `pathology`: 原始病理标签。
- `is_malignant`: `int(pathology == "M")`。
- `image_path`: 保留 `train.csv` 中的 archive-relative 路径。
- `laterality`: 由原始 `l_r` 映射。
- `device`: 原始设备字段。
- `lesion_type`: 原始病灶类型字段。
- `birads`: 原始 `birads`。
- `difficult`: 原始 `difficult`。
- `annotations`: 原始 `annotations`。

4. paired breast-level index 的字段定义
- `breast_id`
- `pathology`
- `is_malignant`
- `image_id_cc`
- `image_id_mlo`
- `image_path_cc`
- `image_path_mlo`
- `laterality`
- `device`
- `birads`

5. 做了哪些一致性检查
- 必需列是否存在：`image_path`, `breast_id`, `cc_mlo`, `pathology`
- `pathology` 是否只来自 `{M, B, N}`
- 是否存在重复 `image_id`
- 每个 `breast_id` 是否恰好 2 条记录
- 每个 `breast_id` 的视图是否恰好为 `CC` 和 `MLO`
- 同一 `breast_id` 内 `pathology` 是否一致
- `train.csv` 中的每个 `image_path` 是否存在于 `train_img.zip`
- paired 构建后是否存在缺失配对、重复配对、空的 `cc/mlo` 核心字段
- 额外做了 paired 元数据一致性检查：`pathology`、`is_malignant`、`laterality`、`device`、`birads` 在同一 `breast_id` 内必须一致

默认行为是严格模式：
- 任一核心校验失败会抛出 `DatasetIndexError`
- CLI 退出码为 `1`
- 不写出索引文件

6. 输出文件保存到哪里
- [primary_single_image_index.csv](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_single_image_index.csv)
- [primary_paired_breast_index.csv](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_paired_breast_index.csv)
- [primary_index_report.json](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_index_report.json)

7. 一段最小运行方式
```bash
python scripts/build_dataset_index.py
python -m unittest tests.test_index_builder
```

8. 一次示例统计输出
```text
Dataset indexes built successfully
- single-image rows: 1300
- paired breast rows: 650
- image-level pathology: B=162, M=314, N=824
- breast-level pathology: B=81, M=157, N=412
- image-level is_malignant: 0=986, 1=314
- breast-level is_malignant: 0=493, 1=157
- anomaly counts: {'missing_required_columns': 0, 'invalid_pathology_values': 0, 'duplicate_image_ids': 0, 'invalid_breast_image_count': 0, 'invalid_breast_view_pairs': 0, 'inconsistent_breast_pathology': 0, 'missing_archive_paths': 0, 'invalid_paired_samples': 0, 'duplicate_paired_breast_ids': 0, 'empty_paired_fields': 0, 'inconsistent_paired_metadata': 0}
```

9. 假设、限制或待确认点
- `docs/plan/minimal_system_design.md` 存在并已遵守。
- `docs/plan/issue_stage1.md` 已存在；按你的规则改读了 [docs/plan/issue_stage1.md](D:/MyProject/Breast-Cancer-Detection-Model/docs/plan/issue_stage1.md)。
- 文档假设 vs 实际仓库有一处差异：实际原始字段名是 `cc_mlo`、`l_r`，且没有独立 `image_id` 列，所以实现里做了显式字段映射并由 `image_path` 派生 `image_id`。
- 当前仓库没有已解压的 `train_img/` 目录，所以“路径存在性”检查按 `train_img.zip` 成员表完成，没有把文件系统解压路径设成当前 issue 的前提。
- `lesion_type`、`difficult`、`annotations` 在同一 `breast_id` 内并不总是稳定，所以只保留在 single-image index，没有升格到 paired index。
- 本次没有实现 Issue 1.2/1.3/1.4 内容，没有做预处理、Dataset/DataLoader、split、训练或评估脚本。
- 已验证 `python scripts/build_dataset_index.py` 和 `python -m unittest tests.test_index_builder` 均通过。
