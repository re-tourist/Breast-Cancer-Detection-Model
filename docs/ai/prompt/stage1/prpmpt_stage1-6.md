你现在继续为乳腺癌检测课程项目实现 Milestone 1 的 Issue 1.6。

当前唯一权威的 issue 定义来源是：
- docs/gitflow/issue/issue_stage1.md
请先阅读并严格遵守其中对 Issue 1.6 的定义，不要自行改写 issue 目标。

你还必须结合以下现有实现：
1. docs/plan/minimal_system_design.md
2. docs/gitflow/issue/issue_stage1.md 中 Issue 1.6 的原始要求
3. 已完成的 Issue 1.1–1.5 相关代码与脚本
4. data/processed/metadata/ 下的 index artifacts
5. data/processed/splits/ 下的 split / fold artifacts
6. outputs/m1_baseline/ 下当前训练产物
7. outputs/m1_baseline/eval/ 下当前评估产物

如果仓库实际路径与文档不一致，不要臆造，基于仓库现状做最小合理适配，并在最终汇报中明确指出差异。

================================
一、严格按原 issue 定义执行
================================

Issue 1.6 的原始定义是：

Title:
Run One End-to-End Smoke Test and Record Sanity Findings

Goal:
基于当前最小管线完成一次端到端 smoke test，并形成可复查的 sanity 记录。

Scope:
- 选定一个最小可运行配置
- 跑通至少 1 fold 或一个小规模 train/val 实验
- 保存基本日志与结果
- 记录基础异常与观察结论

Deliverables:
- smoke test 运行脚本
- 一份简短的 sanity report（md）
- 运行日志、指标与必要输出文件路径

Acceptance Criteria:
- 能完整跑通数据读取、训练、验证、评估闭环
- 生成 breast-level AUROC 或至少完成该指标计算流程
- 有明确的 sanity 结论，而不是只说“跑过了”
- 能指出是否存在基础问题（标签错、loss 异常、输出塌缩、明显过拟合等）

你必须以这些要求为准，不要把本 issue 扩展成正式 benchmark 或复杂实验系统。

================================
二、本次允许做的内容
================================

1. 新增一个端到端 smoke test 运行脚本，串起：
   - split 读取
   - train baseline
   - eval pipeline
2. 选择一个最小可运行配置（例如 1 epoch、小 batch、CPU 友好参数）
3. 保存训练日志、评估产物和必要路径信息
4. 写一份简短但有判断力的 sanity report（markdown）
5. 如有必要，可补一个非常轻量的工具函数/脚本包装，但不要重构 trainer 或 eval 框架
6. 补充最小测试，验证 smoke 脚本至少能调起闭环中的关键步骤

================================
三、本次不允许做的内容
================================

1. 不做正式多折实验框架
2. 不做超参数搜索
3. 不做模型结构升级
4. 不进入 paired 双分支训练
5. 不做大规模文档整理（那是 Issue 1.7）
6. 不把本 issue 变成“为了好看指标而调参”

================================
四、实现要求
================================

请优先做一个最小、清晰、可复查的 smoke 方案。

建议但不强制的实现方向：
- scripts/run_stage1_smoke.py
- outputs/m1_smoke/ 或 outputs/m1_baseline/smoke/
- docs/reports/stage1_smoke_report.md 或等价路径

这个脚本应尽量串起已有最小闭环，而不是重新发明一套流程。
优先复用已有：
- train_baseline.py
- run_eval.py
- 现有 split artifacts
- 现有 output 结构

如需通过 subprocess 调用已有脚本可以接受；
如你认为直接调用 Python 接口更稳，也可以，但不要为此重构已有代码。

================================
五、sanity report 的最低要求
================================

请写一份简短 markdown 报告，至少包含：

1. 本次 smoke test 使用的最小配置
   - 数据 split
   - epoch
   - batch size
   - image size
   - device
   - checkpoint / output dir

2. 跑通了哪些环节
   - 数据读取
   - 训练
   - 验证
   - breast-level 聚合评估

3. 关键产物路径
   - config / summary / checkpoint
   - image-level predictions
   - breast-level predictions
   - breast-level metrics

4. 关键观察
   至少回答：
   - 标签是否看起来对齐
   - loss 是否能正常计算、是否有明显异常
   - 输出是否有塌缩迹象（例如几乎常数）
   - 评估脚本是否成功产出 breast-level AUROC
   - 当前结果更像“能跑通”还是“已有合理效果”

5. 明确 sanity 结论
   不能只写“已成功运行”，必须给出判断：
   - 当前闭环是否成立
   - 当前最主要的限制是什么
   - 进入 M2 前最值得注意的风险是什么

================================
六、最小验收标准
================================

你的实现必须满足：

1. 能完整跑通数据读取、训练、验证、评估闭环
2. 至少产出一次 breast-level AUROC 或完成该计算流程
3. 有单独的 smoke test 运行脚本
4. 有一份简短但有判断力的 sanity report
5. 报告里能指出至少一种当前存在或潜在的基础问题/限制
6. 不越界到 Issue 1.7 的大规模文档整理

================================
七、测试要求
================================

请补充最小测试或验证方式，至少覆盖其一：
1. smoke 脚本在测试模式/超小配置下可启动并完成关键阶段
2. smoke 脚本正确汇总并输出关键产物路径
3. sanity report 成功生成

测试保持最小即可，不要为了测试重写工程结构。

================================
八、最终汇报格式
================================

请按以下格式返回：

1. 修改了哪些文件
2. 每个文件的作用
3. smoke test 采用了什么最小配置
4. 端到端串起了哪些已有模块
5. 输出了哪些日志/产物，保存到哪里
6. sanity report 包含哪些结论
7. 给出一次最小运行方式
8. 给出一段实际运行输出示例
9. 补了哪些测试或验证步骤
10. 明确说明这次实现如何对应 issue_stage1.md 中 Issue 1.6 的 Goal / Scope / Deliverables / Acceptance Criteria

如果你发现现有脚本之间的接口不够顺滑，请做最小合理胶水层，不要借机重构整个训练/评估系统。当前任务是完成 M1 的端到端 smoke 与 sanity 记录。