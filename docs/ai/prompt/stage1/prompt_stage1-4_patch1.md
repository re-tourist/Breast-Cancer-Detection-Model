你现在不要进入下一个大 issue，先对 Milestone 1 的 Issue 1.4 做一次小修补（Issue 1.4.x）。

当前状态：
- Issue 1.4 已经实现了最小 single-image baseline、train/val loop、image-level metric，以及轻量 breast mean aggregation metric
- 当前 best checkpoint 是按 val_loss 选择的
- 但项目冻结主任务是 breast-level malignant probability prediction
- 已经有 breast_mean_accuracy / breast_mean_auroc，因此当前 model selection 与主任务目标还不够对齐

本次修补目标：
在不重构训练框架、不扩展到完整 evaluator 框架的前提下，补齐一个“与主任务更对齐”的 checkpoint 选择与 summary 记录机制。

================================
一、修补范围
================================

只允许做以下小修补：
1. 给训练逻辑增加显式的 selection metric 机制
2. 调整 best checkpoint 选择逻辑
3. 增强 metrics_summary.json 的结构化记录
4. 补充最小测试，覆盖 selection metric/fallback 行为
5. 如有必要，增加非常小的 CLI 参数（例如 --selection-metric）

不要做以下事情：
- 不重构整个 trainer
- 不扩展成复杂 evaluator 框架
- 不改模型结构
- 不改 dataset / split / transforms 主体逻辑
- 不进入 Issue 1.5 的正式 breast-level evaluator 开发

================================
二、你必须实现的选择逻辑
================================

请实现一个清晰的 model selection 机制，推荐默认规则如下：

优先级：
1. 如果 breast_mean_auroc 可用（不是 None），则默认用它作为 best checkpoint 选择指标，方向是越大越好
2. 如果 breast_mean_auroc 不可用，则回退到 image_auroc，方向越大越好
3. 如果 image_auroc 也不可用，则回退到 val_loss，方向越小越好

你可以把这个逻辑封装成独立函数，避免散落在 train loop 里。

如你认为更合适，也可以支持 CLI 参数：
- --selection-metric auto
- --selection-metric breast_mean_auroc
- --selection-metric image_auroc
- --selection-metric val_loss

但默认必须是一个合理的 auto 模式，而且要和上述优先级一致。

================================
三、metrics summary 的增强要求
================================

请确保输出的 metrics_summary.json 至少清楚记录：

1. primary_selection_metric
2. selection_mode（如 auto / explicit）
3. best_epoch
4. best_metric_name
5. best_metric_value
6. 若发生 fallback，记录 fallback_used=true/false
7. 若发生 fallback，记录 fallback_reason
8. 每个 epoch 的：
   - train_loss
   - val_loss
   - image_accuracy
   - image_auroc
   - breast_mean_accuracy
   - breast_mean_auroc

不要只保存最终一行 summary，要保证后续人工复查时能看出 best checkpoint 是怎么选出来的。

================================
四、测试要求
================================

请至少补充以下测试之一或多项：

1. 当 breast_mean_auroc 存在时，best checkpoint 按 breast_mean_auroc 选择
2. 当 breast_mean_auroc 为 None、image_auroc 存在时，自动回退到 image_auroc
3. 当两个 AUROC 都不可用时，自动回退到 val_loss
4. metrics_summary.json 中正确记录了 primary_selection_metric 与 fallback 信息

测试尽量保持小而直接，不要引入复杂测试夹具。

================================
五、你最终需要返回给我的内容
================================

请按以下格式汇报：

1. 修改了哪些文件
2. 每个修改的作用
3. best checkpoint 选择逻辑现在是什么
4. 默认 selection metric 是什么，为什么
5. fallback 机制是什么
6. metrics_summary.json 新增了哪些字段
7. 补了哪些测试
8. 给出一次最小运行方式
9. 给出一段新的 summary 输出示例
10. 明确说明这次修补没有越界到 Issue 1.5

如果你发现现有 trainer 结构里很难优雅地加入这个逻辑，请做最小合理改动，不要为了“优雅”而扩大改动范围。当前任务就是一个轻量修补。