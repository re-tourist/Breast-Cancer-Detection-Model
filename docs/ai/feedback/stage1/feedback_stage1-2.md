1. 修改了哪些文件

- [src/data/transforms.py](D:/MyProject/Breast-Cancer-Detection-Model/src/data/transforms.py)
- [src/data/datasets.py](D:/MyProject/Breast-Cancer-Detection-Model/src/data/datasets.py)
- [src/data/__init__.py](D:/MyProject/Breast-Cancer-Detection-Model/src/data/__init__.py)
- [scripts/check_dataset_loading.py](D:/MyProject/Breast-Cancer-Detection-Model/scripts/check_dataset_loading.py)
- [tests/test_datasets.py](D:/MyProject/Breast-Cancer-Detection-Model/tests/test_datasets.py)

2. 每个文件的作用

- [transforms.py](D:/MyProject/Breast-Cancer-Detection-Model/src/data/transforms.py)：实现最小预处理流水线和 `build_train_transform` / `build_eval_transform`。
- [datasets.py](D:/MyProject/Breast-Cancer-Detection-Model/src/data/datasets.py)：实现 zip/文件系统双路径读图、`SingleImageDataset`、`PairedBreastDataset`。
- [__init__.py](D:/MyProject/Breast-Cancer-Detection-Model/src/data/__init__.py)：把 Issue 1.1 的索引接口和 Issue 1.2 的 dataset/transform 接口统一导出。
- [check_dataset_loading.py](D:/MyProject/Breast-Cancer-Detection-Model/scripts/check_dataset_loading.py)：做 dataloader smoke test，并可保存预处理 preview 图。
- [test_datasets.py](D:/MyProject/Breast-Cancer-Detection-Model/tests/test_datasets.py)：覆盖 transform、single dataset、paired dataset、dataloader batch 行为。

3. single-image dataset 的输入与输出定义

输入：
- `index_csv_path`：默认用 [primary_single_image_index.csv](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_single_image_index.csv)
- `archive_path`：默认用 `data/raw/primary/train_img.zip`
- `transform`
- `image_root=None`：若提供且 `image_root / image_path` 存在，则优先走解压目录

输出 dict：
- `image`: `torch.float32`，默认 shape `[3, 1024, 1024]`
- `target`: `torch.float32` 标量
- `image_id`
- `breast_id`
- `view`
- `image_path`
- `laterality`

4. paired dataset 的输入与输出定义

输入：
- `index_csv_path`：默认用 [primary_paired_breast_index.csv](D:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata/primary_paired_breast_index.csv)
- `archive_path`
- `transform`
- `image_root=None`

输出 dict：
- `x_cc`: `torch.float32`，默认 shape `[3, 1024, 1024]`
- `x_mlo`: `torch.float32`，默认 shape `[3, 1024, 1024]`
- `target`: `torch.float32` 标量
- `breast_id`
- `image_path_cc`
- `image_path_mlo`
- `image_id_cc`
- `image_id_mlo`
- `laterality`

5. 预处理流水线具体做了什么

- 把原始 JPEG 转成单通道灰度
- 用像素阈值 `> 5` 做前景 bbox，裁掉背景/黑边；如果找不到前景则回退原图
- 若 `laterality == "R"`，做水平翻转统一朝向
- 保持长宽比 resize
- 用 0 padding 到固定正方形尺寸，默认 `1024 x 1024`
- 转成 `[0, 1]` 的 `torch.float32`
- 默认复制灰度到 3 通道；也支持切成 1 通道
- train/eval 预处理主流程一致；当前 train 默认不启用随机增强，避免 M1 越界和引入不必要不稳定性

6. 图像读取方案如何实现

- 优先读 `image_root / image_path`
- 若不存在，则回退到 `train_img.zip` 中按 `image_path` 直接读取 member
- zip handle 在 dataset 内部懒打开，不在初始化时提前持有
- 这保证了当前仓库“只有 zip、没有解压目录”时也能稳定工作

7. smoke test / 可视化检查怎么运行

运行：
```bash
python scripts/check_dataset_loading.py --dataset single --batch-size 2 --num-batches 1
python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1 --save-preview
python -m unittest tests.test_index_builder tests.test_datasets
```

可视化输出默认保存到：
- [outputs/dataset_loading_preview](D:/MyProject/Breast-Cancer-Detection-Model/outputs/dataset_loading_preview)

实际已生成示例：
- [paired_0_00406_L.png](D:/MyProject/Breast-Cancer-Detection-Model/outputs/dataset_loading_preview/paired_0_00406_L.png)
- [paired_1_00406_R.png](D:/MyProject/Breast-Cancer-Detection-Model/outputs/dataset_loading_preview/paired_1_00406_R.png)

8. 一段最小运行方式

```bash
python scripts/check_dataset_loading.py --dataset single --batch-size 2 --num-batches 1
python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1 --save-preview
```

9. 一次实际输出示例

single-image smoke：
```text
Dataset: single
Mode: eval
Length: 1300
Batch 0
- keys: ['image', 'target', 'image_id', 'breast_id', 'view', 'image_path', 'laterality']
- image: shape=(2, 3, 1024, 1024) dtype=torch.float32 min=0.0000 max=1.0000
- target: shape=(2,) dtype=torch.float32 min=0.0000 max=0.0000
- image_id sample: ['00406_L_CC', '00406_L_MLO']
```

paired smoke：
```text
Dataset: paired
Mode: eval
Length: 650
Batch 0
- keys: ['x_cc', 'x_mlo', 'target', 'breast_id', 'image_path_cc', 'image_path_mlo', 'image_id_cc', 'image_id_mlo', 'laterality']
- x_cc: shape=(2, 3, 1024, 1024) dtype=torch.float32 min=0.0000 max=1.0000
- x_mlo: shape=(2, 3, 1024, 1024) dtype=torch.float32 min=0.0000 max=1.0000
- target: shape=(2,) dtype=torch.float32 min=0.0000 max=0.0000
- breast_id sample: ['00406_L', '00406_R']
```

10. 假设、限制或待确认点

- `docs/plan/issue_stage1.md` 仍不存在；本次按你的规则使用了等价文档 [docs/gitflow/issue/issue_stage1.md](D:/MyProject/Breast-Cancer-Detection-Model/docs/gitflow/issue/issue_stage1.md)。
- 当前仓库没有 `data/interim/primary/train_img/...` 解压图目录，所以主读图路径是 zip；`image_root` 只是后续速度优化接口。
- 方向统一没有用启发式图像规则，而是严格基于 Issue 1.1 索引中的 `laterality` 字段：只有 `R` 才水平翻转。
- 原始 JPEG 文件是 RGB 存储，但采样检查三个通道数值一致，所以本实现先灰度化，再按需复制到 3 通道。
- train/eval 已区分工厂函数，但当前默认都不启用随机增强；这是有意保持 M1 稳定和可检查。
- 没有实现 Issue 1.3 / 1.4 / 1.5 的 split、train loop、AUROC 或评估逻辑。
- 验证已实际通过：
  - `python -m unittest tests.test_index_builder tests.test_datasets`
  - `python scripts/check_dataset_loading.py --dataset single --batch-size 2 --num-batches 1`
  - `python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1 --save-preview`