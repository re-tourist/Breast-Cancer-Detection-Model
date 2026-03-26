你现在在为一个课程项目实现 Milestone 1 的 Issue 1.1。

项目名称：乳腺癌检测项目——最小可运行闭环系统
当前 Issue：Issue 1.1 — Build Dataset Index and Paired Breast-level Samples

在开始改代码前，你必须先阅读并遵守以下文档约束：
1. docs/plan/minimal_system_design.md
2. docs/plan/issue_stage1.md
如果仓库中这些路径不存在，请先在现有文件中查找同名或等价文档；若仍找不到，不要臆造，直接在最终汇报中说明缺失。

================================
一、你必须遵守的任务背景
================================

当前任务不是普通单图分类，而是 breast-level malignant probability prediction。

冻结约束如下：
- 输入单位：同一 breast_id 下两张图像（CC + MLO）
- 输出单位：breast-level malignant probability
- 标签定义：
  - pathology == M -> is_malignant = 1
  - pathology in {B, N} -> is_malignant = 0
- 所有后续训练/验证划分都必须以 breast_id 为 group
- Milestone 1 当前只做最小可运行闭环，不做复杂扩展

Issue 1.1 的唯一目标是：
建立统一、稳定、可检查的数据索引机制，至少支持两类样本视图：
1. single-image view
2. paired breast-level view

================================
二、本次只允许完成的内容
================================

请只实现 Issue 1.1 范围内的内容，不要提前做 Issue 1.2 / 1.3 / 1.4 的工作。

本次允许做的事情：
1. 解析原始训练元数据（例如 train.csv 及其对应图像路径）
2. 定义统一字段规范
3. 构建 single-image sample index
4. 构建 paired breast-level sample index
5. 对 breast-level 配对一致性做检查
6. 输出基础数据统计与检查结果
7. 提供后续模块可复用的索引构建接口

本次不允许做的事情：
- 不实现图像预处理
- 不实现 Dataset / DataLoader
- 不实现 fold split
- 不实现训练或评估脚本
- 不引入复杂配置系统
- 不过度设计通用数据框架
- 不修改与本 issue 无关的大量文件

================================
三、推荐的实现目标
================================

请优先在 src/data/ 下组织实现，保持最小、清晰、可复用。

建议但不强制的产物结构示例：
- src/data/index_builder.py
- src/data/schema.py 或在模块内部清晰定义字段
- scripts/build_dataset_index.py 或等价脚本
- outputs/indexes/ 或 data/processed/ 下保存生成的索引文件
- 如有必要，可增加一个很小的 utils 模块，但不要扩展过度

你需要构建两份核心索引表：

A. single-image index
每条记录至少包含以下字段：
- image_id
- breast_id
- view
- pathology
- is_malignant
- image_path

如原始数据还有 side / laterality / patient_id 等字段，可以保留，但不要把它们变成当前 issue 的强依赖。

B. paired breast-level index
每条记录代表一个 breast sample，至少包含：
- breast_id
- pathology
- is_malignant
- image_id_cc
- image_id_mlo
- image_path_cc
- image_path_mlo

如果原始数据里有可保留的额外字段，也可以保留，但必须保证核心字段清晰、稳定。

================================
四、你必须做的数据一致性检查
================================

请在实现中显式检查并汇报以下问题：

1. 每个 breast_id 是否恰好对应两张图
2. 两张图的 view 是否为一张 CC、一张 MLO
3. 同一 breast_id 内 pathology 是否一致
4. 是否存在重复 image_id
5. 图像路径是否存在（若仓库环境能检查）
6. paired 样本构建后是否有缺失配对或重复配对

请不要把异常静默吞掉。
对于不满足假设的样本：
- 要么明确报错并停止
- 要么以“严格模式/非严格模式”处理，但默认建议严格
无论哪种方式，都必须在最终汇报中说明。

================================
五、实现风格要求
================================

1. 代码以“最小可运行、后续可复用”为目标，不要过度工程化
2. 函数命名与字段命名必须直观
3. 尽量让 single-image index 和 paired index 的生成逻辑清楚分层
4. 不要把业务规则散落在脚本各处，核心标签映射和配对逻辑应集中定义
5. 保持 I/O 和核心逻辑适度分离
6. 若某些原始字段名与项目约定不一致，应在代码中显式映射，而不是靠注释含混处理

================================
六、最小验收标准
================================

你提交的实现必须满足：

1. 能从原始训练元数据稳定生成 single-image 样本索引
2. 能稳定生成 paired breast-level 样本索引
3. 每个 paired sample 正确对应 CC 与 MLO
4. 标签统一映射为 is_malignant = int(pathology == "M")
5. 有基础统计输出，例如：
   - 总 image 数
   - 总 breast 数
   - pathology 分布
   - is_malignant 分布
   - 配对成功数
   - 异常样本数
6. 输出的索引文件可直接供后续 Issue 1.2 / 1.3 复用
7. 没有偷偷实现后续 issue 的内容

================================
七、你最终需要返回给我的内容
================================

请按下面格式汇报：

1. 修改了哪些文件
2. 每个文件的作用
3. single-image index 的字段定义
4. paired breast-level index 的字段定义
5. 做了哪些一致性检查
6. 输出文件保存到哪里
7. 给出一段最小运行方式
8. 给出一次示例统计输出
9. 明确说明有哪些假设、限制或待确认点

如果你发现仓库实际数据字段、目录结构、文件命名与文档假设不一致：
- 不要擅自脑补
- 基于仓库实际情况做最小合理适配
- 并在最终汇报里明确指出“文档假设 vs 实际仓库”的差异