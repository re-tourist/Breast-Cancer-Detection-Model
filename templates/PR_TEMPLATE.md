﻿# Pull Request

## 1. Summary

简要说明本次 PR 解决了什么问题。

- 对应阶段 / milestone：
- 对应 issue：
- 本次 PR 的核心目标：

---

## 2. Why This Change Exists

说明为什么需要这次改动。

请回答：
- 这个改动补的是哪个缺口？
- 它在当前阶段里的作用是什么？
- 为什么现在做，而不是以后做？

---

## 3. Files Changed

按文件或目录列出本次主要改动。

示例格式：

- `path/to/file_a.py`
  - 做了什么
  - 为什么改
- `path/to/file_b.md`
  - 做了什么
  - 为什么改

请不要只列文件名，不解释改动意义。

---

## 4. Scope Check

请明确说明本次改动是否严格在 scope 内。

- [ ] 完全在当前 issue / milestone scope 内
- [ ] 有少量超出 scope 的改动，但已说明理由
- [ ] 存在明显超出 scope 的改动，需要人工确认

若存在超出 scope 的改动，请说明：
- 超出了什么
- 为什么不可避免
- 带来了什么风险

---

## 5. Validation

请列出你实际运行过的验证，而不是理论上可以运行的验证。

### Commands Run

```bash
# command 1
# command 2
# command 3
```

### Validation Result

- 检查 1：
- 检查 2：
- 手工 sanity check：
- 未运行但本来可能相关的检查：

如果没有运行某项检查，请明确说明原因。

------

## 6. Documentation / Config Sync

请检查以下内容是否需要同步：

-  README
-  docs/ai
-  docs/plan
-  docs/review
-  docs/contracts
-  examples / scripts / config comments
-  无需同步文档

说明：

- 更新了哪些文档：
- 为什么这些文档需要更新：
- 如果没更新，为什么可以不更新：

------

## 7. Risks / Limitations

请诚实列出当前已知风险。

包括但不限于：

- 尚未验证的路径
- 潜在兼容性问题
- 暂时保留的技术债
- 可能影响后续 issue 的地方
- 语义上仍有不确定性的地方

请不要写“无”除非你非常确定。

------

## 8. Contract / Interface Check

请说明本次改动是否触及以下边界：

-  public API
-  config semantics
-  stable file layout
-  data flow / output meaning
-  evaluation logic
-  frozen contract
-  none of the above

若触及，请说明：

- 改了什么
- 是否在允许范围内
- 需要谁确认

------

## 9. Stop Condition Check

请说明是否遇到任何本应“停止并汇报”的情况：

-  没有遇到
-  遇到了，但已在本 PR 中说明
-  遇到了，当前 PR 不应继续推进

说明：

- stop condition 是什么：
- 发生在哪：
- 当前如何处理：

------

## 10. Reviewer Focus

请告诉 reviewer 这次最值得重点检查的地方。

例如：

- 某个核心模块是否越界修改
- 某个验证是否充分
- 某个语义是否可能“指标正确但逻辑不对”
- 某处 contract 是否有潜在冲突

建议 reviewer 重点关注：
 1.
 2.
 3.

------

## 11. Recommended Next Step

请给出最自然的下一步，而不是泛泛而谈。

例如：

- 进入 issue X.2
- 补一项 focused validation
- 先冻结当前接口
- 先人工确认某个实验结果再继续
