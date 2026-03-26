你现在对 Milestone 1 的 Issue 1.3 做一次轻量级修补（Issue 1.3.x）。

⚠️ 本次不是重做 split，也不是重构代码，而是补齐原 issue 文档中“fold assignment artifact”的要求。

================================
一、背景（必须理解）
================================

当前状态：
- Issue 1.3 已经实现：
  - 基于 breast_id 的 group-aware train/val split
  - paired 与 single 一致边界
  - leakage 检查
  - 使用 StratifiedGroupKFold 生成划分
  - 输出 train.csv / val.csv / summary.json

问题：
- 当前产物更像“单次 train/val 划分”
- 但 issue_stage1.md 原始要求是：
  - 优先支持 5-fold
  - 输出 fold assignment 文件

因此，本次修补目标是：

👉 在不破坏现有 train/val split 的前提下  
👉 补充一个标准的 fold assignment artifact  
👉 让实现完全对齐 issue 文档

================================
二、本次允许做的事情（严格限制）
================================

只允许：

1. 在现有 split 逻辑基础上，导出 fold assignment
2. 增加一个 fold-level summary
3. 补充最小测试验证 fold assignment 正确性
4. 如有必要，增加极小的辅助函数

禁止：

- 不重写 split 逻辑
- 不改变 train.csv / val.csv 结构
- 不修改 dataset / trainer / dataloader
- 不扩展为完整 cross-validation 框架
- 不影响 Issue 1.4 及之后流程

================================
三、你必须实现的内容
================================

## 1️⃣ fold assignment 文件

请生成一个新的 artifact，例如：

data/processed/splits/fold_assignment.csv

每一行必须对应一个 breast_id，至少包含：

- breast_id
- fold  （0 ~ K-1，例如 0~4）
- target（is_malignant）
- （可选）num_images 或其他已有字段

要求：

- fold assignment 必须来自现有 StratifiedGroupKFold
- 不允许重新随机划分
- 每个 breast_id 只出现一次
- fold 值连续且完整

⚠️ 注意：
不要只导出 train/val，要导出完整 fold mapping。

---

## 2️⃣ fold-level summary

请额外生成：

fold_summary.json 或 fold_summary.csv

至少包含：

对每个 fold：
- breast_count
- image_count（可选）
- malignant_count
- non_malignant_count
- malignant_ratio

以及：
- 总 breast 数
- fold 数
- 是否 stratified（true/false）
- 是否 fallback（true/false）

---

## 3️⃣ 与现有 train/val 的关系（必须说明）

你必须保证并在代码中明确：

- 当前 train.csv / val.csv 是从 fold assignment 派生的
  （例如 fold 0 作为 val，其余为 train）

如果当前实现不是这样，也不要推翻现有逻辑，而是：

- 在 summary 中明确记录当前 train/val 对应的是哪一个 fold

---

## 4️⃣ 一致性检查（必须做）

请显式检查：

1. fold assignment 中：
   - 每个 breast_id 只出现一次
   - fold 分布合理（无空 fold）

2. train/val split：
   - 与 fold assignment 一致
   - train 与 val 无 overlap

3. label 分布：
   - 每个 fold 都有合理的 malignant / non-malignant 分布
   - 若极端失衡，需记录 warning（不要报错）

---

## 5️⃣ 测试（最小但必须）

请至少添加一个测试文件，例如：

tests/test_split_fold_assignment.py

覆盖：

1. fold assignment 中无重复 breast_id
2. fold 数量正确（例如 5 fold）
3. train/val 与 fold assignment 一致
4. fold 内 target 不为空

测试必须小而直接，不要复杂化。

---

================================
四、实现风格要求
================================

1. 不要重构现有 split 代码，只做“旁路增强”
2. fold assignment 生成逻辑尽量复用已有结果
3. 避免重复计算
4. 文件命名清晰、路径统一
5. 让这个 artifact 后续能直接用于：
   - cross-validation
   - reproducibility
   - debug

================================
五、最小验收标准
================================

你的实现必须满足：

1. 新增 fold_assignment.csv
2. 每个 breast_id 恰好一行
3. fold ∈ [0, K-1]
4. fold 分布合理
5. train/val split 可从 fold assignment 解释
6. 有 fold-level summary
7. 有最小测试
8. 不影响现有训练流程

================================
六、最终汇报格式
================================

请按以下格式返回：

1. 修改了哪些文件
2. 每个文件的作用
3. fold assignment 文件结构（字段说明）
4. fold summary 包含哪些统计信息
5. train/val 与 fold 的关系
6. 做了哪些一致性检查
7. 补了哪些测试
8. 给出最小运行方式
9. 给出一段 fold_assignment.csv 示例
10. 明确说明本次修改没有破坏 Issue 1.3 / 1.4 的现有逻辑