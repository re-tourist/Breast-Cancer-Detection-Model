# Stage 2 Linux Run Order

```bash
# 进入项目目录
cd /path/to/Breast-Cancer-Detection-Model

# 拉取远端最新分支信息
git fetch origin

# 切到 Stage 2 实现分支，没有本地分支就跟踪远端创建
git checkout codex/feat-model-stage2 || git checkout -t origin/codex/feat-model-stage2

# 快进更新本地分支
git pull --ff-only

# 安装当前仓库最小运行时依赖
python -m pip install -r requirements.txt

# 先确认 paired 数据加载正常
python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1

# 可选：先跑一个轻量 Stage 2 smoke，确认 train/eval/plumbing 正常
python scripts/run_stage2_smoke.py --image-size 256 --batch-size 2 --epochs 1 --output-dir outputs/m2_smoke

# 为本次正式训练定义唯一输出目录，避免覆盖旧结果
RUN_DIR=outputs/m2_baseline_$(date +%Y%m%d_%H%M%S)

# 正式训练 Stage 2 paired baseline，按当前实验参数执行
python scripts/train_baseline.py --dataset paired --image-size 1024 --batch-size 2 --epochs 10 --lr 1e-4 --output-dir "$RUN_DIR"

# 用同一个 RUN_DIR 下的 best checkpoint 跑 paired eval，不再单独手写其他目录
python scripts/run_eval.py --dataset paired --checkpoint "$RUN_DIR/best_model.pt" --image-size 1024 --batch-size 1

# 查看最终 breast-level metrics
cat "$RUN_DIR/eval/breast_level_metrics.json"

# 查看本次 eval 的上下文，确认 checkpoint 和 output dir 没有跑偏
cat "$RUN_DIR/eval/eval_config.json"
```

## Important Notes

```bash
# 每次新实验前都重新定义 RUN_DIR，不要复用旧 shell 里的 RUN_DIR
RUN_DIR=outputs/m2_baseline_$(date +%Y%m%d_%H%M%S)

# 如果训练命令里显式写了 --output-dir，就在 eval 命令里使用同一个目录，不要混用旧的 RUN_DIR
python scripts/train_baseline.py ... --output-dir outputs/m2_baseline_bs2_lr1e4
python scripts/run_eval.py --dataset paired --checkpoint outputs/m2_baseline_bs2_lr1e4/best_model.pt --image-size 1024 --batch-size 1

# 在服务器上做评估前先 git pull，避免跑到旧版 run_eval.py
git pull --ff-only
```
