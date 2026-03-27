1. 修改了哪些文档/文件

修改了 [README.md](d:/MyProject/Breast-Cancer-Detection-Model/README.md)、[data/README.md](d:/MyProject/Breast-Cancer-Detection-Model/data/README.md)，新增了 [docs/handoff/stage1_handoff.md](d:/MyProject/Breast-Cancer-Detection-Model/docs/handoff/stage1_handoff.md)。

2. 每个文件的作用

[README.md](d:/MyProject/Breast-Cancer-Detection-Model/README.md) 现在负责给出 Stage 1 的最小运行入口、当前范围和边界。  
[data/README.md](d:/MyProject/Breast-Cancer-Detection-Model/data/README.md) 现在补齐了 Stage 1 已生成的 metadata / split / fold artifact。  
[stage1_handoff.md](d:/MyProject/Breast-Cancer-Detection-Model/docs/handoff/stage1_handoff.md) 是给未来自己/新成员的工程交接文档，重点回答“怎么跑、产物在哪、当前到哪一步、主要风险是什么”。

3. README 更新了什么

README 从原来的 Stage 0 状态改成了 Stage 1 状态，主要补了这些内容：

- 当前已经有最小可运行 pipeline，而不是“尚未实现训练入口”
- 最小运行命令：`build_dataset_index`、`build_splits`、`train_baseline`、`run_eval`、`run_stage1_smoke`
- 当前仓库结构里和 M1 直接相关的目录与脚本
- 当前边界：训练仍是 single-image fallback，不是正式 paired baseline
- 当前限制：smoke 结果只能说明闭环成立，不说明 baseline 已经有效

4. Stage 1 handoff / summary 文档包含哪些部分

[stage1_handoff.md](d:/MyProject/Breast-Cancer-Detection-Model/docs/handoff/stage1_handoff.md) 包含：

- Stage 1 已完成内容
- 当前任务定义与边界
- 关键代码目录、脚本和 artifact 路径
- 最小 runbook
- 每个入口脚本会产出什么
- 当前 smoke 的已知发现
- 已知问题与进入 M2 前的注意事项
- 对未来工作的几个实用提醒

5. 文档里如何说明最小运行入口

README 和 handoff 都明确给了这几条命令：

```bash
python scripts/build_dataset_index.py
python scripts/build_splits.py
python scripts/train_baseline.py --epochs 1 --batch-size 8 --image-size 512
python scripts/run_eval.py --checkpoint outputs/m1_baseline/best_model.pt --image-size 512 --output-dir outputs/m1_baseline/eval
python scripts/run_stage1_smoke.py
```

同时 handoff 里还把关键输入和输出目录写清楚了：
- [data/processed/metadata](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/metadata)
- [data/processed/splits](d:/MyProject/Breast-Cancer-Detection-Model/data/processed/splits)
- [outputs/m1_baseline](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_baseline)
- [outputs/m1_smoke](d:/MyProject/Breast-Cancer-Detection-Model/outputs/m1_smoke)

6. 文档里如何说明 M1 已完成与未完成范围

文档明确写了：

已完成：
- single-image / paired breast-level index
- dataset / transforms
- `breast_id`-grouped split 和 fold assignment
- minimal single-image baseline train/val
- minimal eval + breast-level aggregation
- end-to-end smoke test

未完成：
- paired dual-branch breast-level training 主线
- multi-fold training orchestration
- M2 的正式 baseline 提升
- benchmark / tuning / complex experiment management

7. 文档里记录了哪些已知问题与后续注意事项

文档明确记录了这些问题和注意事项：

- 当前主训练路径仍是 single-image fallback，而最终任务是 breast-level multi-view
- 当前 smoke 暴露出 prediction collapse 风险，预测分布过窄
- 当前结果只能说明闭环成立，不能说明 baseline 已经有效
- 进入 M2 前最值得优先处理的是更强的 breast-level 建模和塌缩问题诊断
- `requirements.txt` 仍未整理，这是工程交接时的已知短板

8. 给出一段文档示例

来自 [stage1_handoff.md](d:/MyProject/Breast-Cancer-Detection-Model/docs/handoff/stage1_handoff.md)：

```md
The frozen project task is still breast-level malignant probability prediction.

Current Stage 1 training path:
- train a single-image classifier on the grouped single-image split
- aggregate validation predictions back to `breast_id` during evaluation

Interpretation:
- this is a runnable fallback path, not the intended final breast-level baseline
- Stage 1 proves the pipeline is structurally correct enough to load data, train, validate, aggregate, and report breast-level metrics
- Stage 1 does not prove that the current baseline is strong
```

9. 明确说明这次实现如何对应 issue_stage1.md 中 Issue 1.7 的 Goal / Scope / Deliverables / Acceptance Criteria

这次实现是直接对齐 Issue 1.7 的：

- Goal：把 Stage 1 的工程文档和运行说明同步到当前真实代码状态
- Scope：更新了 README、补了 handoff 文档、补了关键目录/脚本说明、记录了已知问题和后续注意事项
- Deliverables：已经有文档更新和 Stage 1 handoff 文档
- Acceptance Criteria：现在新成员或未来自己可以根据文档快速找到 M1 产物、知道怎么跑最小 pipeline、知道 M1 做到了什么和没做到什么，而且文档内容已经从原先的 Stage 0 状态修正为和当前代码/产物一致

路径差异说明：
- 本次权威 issue 文档使用的是 [docs/plan/issue_stage1.md](D:/MyProject/Breast-Cancer-Detection-Model/docs/plan/issue_stage1.md)
- 之前 README 停留在 Stage 0，这次已经按实际代码状态修正
- 这次没有越界到 M2 方案设计，也没有改训练/评估逻辑，只做了文档同步和交接说明
