# Run Order

说明：
- 统一采用“一行注释，一行命令”的格式。
- 新增命令组时先写时间戳标题，方便区分不同批次。
- 默认面向 Linux 服务器执行重计算任务；本地只负责准备命令、轻量验证和结果分析。

## [2026-04-03 服务器同步与环境准备]

```bash
# 进入项目目录
cd /path/to/Breast-Cancer-Detection-Model

# 拉取远端最新代码
git fetch origin

# 切到当前 Stage 2 工作分支；如果本地没有该分支则跟踪远端创建
git checkout codex/feat-model-stage2 || git checkout -t origin/codex/feat-model-stage2

# 快进更新本地分支
git pull --ff-only

# 安装当前仓库最小运行依赖
python -m pip install -r requirements.txt
```

## [2026-04-03 数据与轻量检查]

```bash
# 检查 paired 数据加载是否正常
python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1

# 可选：先跑一个轻量 Stage 2 smoke，确认 train/eval/plumbing 正常
python scripts/run_stage2_smoke.py --image-size 256 --batch-size 2 --epochs 1 --output-dir outputs/m2_smoke
```

## [2026-04-03 Stage 2 正式训练与评估]

```bash
# 为本次正式实验定义唯一输出目录，避免覆盖旧结果
RUN_DIR=outputs/m2_baseline_$(date +%Y%m%d_%H%M%S)

# 正式训练 Stage 2 paired baseline，使用当前验证通过的超参数
python scripts/train_baseline.py --dataset paired --image-size 1024 --batch-size 2 --epochs 10 --lr 1e-4 --output-dir "$RUN_DIR"

# 使用同一 RUN_DIR 下的最佳 checkpoint 做 paired eval
python scripts/run_eval.py --dataset paired --checkpoint "$RUN_DIR/best_model.pt" --image-size 1024 --batch-size 1

# 查看本次评估指标
cat "$RUN_DIR/eval/breast_level_metrics.json"

# 查看本次评估上下文，确认 checkpoint 和 output dir 匹配
cat "$RUN_DIR/eval/eval_config.json"
```

## [2026-04-03 测试集提交文件生成]

```bash
# 使用当前 canonical checkpoint 生成测试集 submission
python scripts/run_test_submission.py --checkpoint outputs/m2_baseline_bs2_lr1e4/best_model.pt --image-size 1024 --batch-size 1

# 查看 submission 上下文，确认 checkpoint 和 output dir 匹配
cat outputs/m2_baseline_bs2_lr1e4/submission/submission_config.json

# 查看最终可提交 CSV 的前几行
head -n 5 outputs/m2_baseline_bs2_lr1e4/submission/name_sid_submission.csv
```

## [2026-04-03 使用约束]

```bash
# 每次新实验前都重新定义 RUN_DIR，不要复用旧 shell 里的变量
RUN_DIR=outputs/m2_baseline_$(date +%Y%m%d_%H%M%S)

# 如果训练命令显式写了 --output-dir，评估命令也必须使用同一实验目录下的 checkpoint
python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline_bs2_lr1e4/best_model.pt --image-size 1024 --batch-size 1

# 在服务器上做正式评估或 submission 之前先拉最新代码，避免跑到旧脚本
git pull --ff-only
```
