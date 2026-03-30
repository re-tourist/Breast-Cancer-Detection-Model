# Stage 2 Linux Run Order

```bash
# 进入项目目录
cd /path/to/Breast-Cancer-Detection-Model

# 拉取远端最新分支信息
git fetch origin

# 切到 Stage 2 实现分支，优先复用本地分支，没有就跟踪远端创建
git checkout codex/feat-model-stage2 || git checkout -t origin/codex/feat-model-stage2

# 如果本地已经有这个分支就快进更新
git pull --ff-only

# 安装当前仓库最小运行时依赖
python -m pip install -r requirements.txt

# 为本次正式 run 生成唯一输出目录，避免覆盖旧结果
RUN_ID=$(date +%Y%m%d_%H%M%S)

# 定义本次 run 的输出根目录
RUN_DIR=outputs/m2_baseline_${RUN_ID}

# 先确认 paired 数据加载正常
python scripts/check_dataset_loading.py --dataset paired --batch-size 2 --num-batches 1

# 可选：先跑一个轻量 Stage 2 smoke，确认训练/eval/plumbing 正常
python scripts/run_stage2_smoke.py --image-size 256 --batch-size 2 --epochs 1 --output-dir outputs/m2_smoke

# 正式训练 Stage 2 paired baseline，固定 1024 输入；这里先从 batch_size=1 开始，如果连 1 都 OOM 就停止
python scripts/train_baseline.py --dataset paired --image-size 1024 --batch-size 1 --epochs 10 --output-dir "$RUN_DIR"

# 用最佳 checkpoint 跑正式 paired eval
python scripts/run_eval.py --dataset paired --checkpoint "$RUN_DIR/best_model.pt" --image-size 1024 --batch-size 1 --output-dir "$RUN_DIR/eval"

# 查看最终 breast-level metrics
cat "$RUN_DIR/eval/breast_level_metrics.json"
```
