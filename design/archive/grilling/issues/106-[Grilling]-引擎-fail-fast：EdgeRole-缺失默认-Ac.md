# #106 [Grilling] 引擎 fail-fast：EdgeRole 缺失默认 Active(0) 静默失败（#91 ③ 后置项）

> 状态：关闭 · 创建 2026-08-30 · 关闭 2026-08-30
> 标签：维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/106

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

引擎层 fail-fast 防御：三体模型边数据缺失 `role` 字段时，C# 反序列化静默回退 `EdgeRole.Active(0)`，导致权重语义静默改变（brainstem 边 modulating(0.5)→active(1.0)）。这是 Grilling #91 Q5 的后置项 ③（决策树 §Q5 → 推迟）。

## 六维定位

- 维度: 管线（引擎数据完整性防御）
- 依赖: #91（已闭合）、data-layer spec（EdgeRole 非可空）、tools/validate_tripartite_annotations.py（管线侧校验已实现）
- 阻塞: 无（独立决策；建议 #105 启动前定夺，实现可并入 #105 或独立任务）

## 当前状态

- 校验脚本 `tools/validate_tripartite_annotations.py`（只读 fail-fast）**已能发现**缺失（REQUIRED_FIELDS 检查，2026-08-30 commit 373c2a0）——管线侧防御 ✅
- 引擎侧（C#）**未防御**：`EdgeRole` 默认值 = Active(0)（BrainEnums.cs:61）；`Role` 属性非可空（TripartiteEdges.cs）；`SnakeCaseEnumConverter.Read` 仅在字段存在时触发（缺失 → 属性保持默认值，converter 不介入）；反序列化后无法区分「JSON 缺失」与「显式 active」。
- 消费者现状：`CorticalBias.Compute` 对 brainstem 边做 Silent → InvalidDataException（BrainEnums.cs + CorticalBias.cs:60-64），但缺失字段静默成为 Active 无法被消费者检测。

## 决策目标

定夺引擎层 fail-fast 的实现机制、范围、时机与归属（#105 并入 or 独立任务），并在决策树/六维状态落位。

---

## 评论（1 条）

### verystrongdog · 2026-08-30

## ✅ Grilling #106 关闭总结

### 决策表（Q1-Q7）

| # | 决策 | 内容 |
|---|------|------|
| Q1 | 机制 | `[JsonRequired]`（net8.0 原生）——4 类边 record 的 `Role` 加 `[JsonRequired]`，缺失 → 反序列化边界抛 `JsonException`；实测确认缺失/null/active/大小写/数组元素全部行为 |
| Q2 | 范围 | 仅 `Role`（真实类名 `BrainstemProjection`/`CstcEdge`/`CorticocorticalEdge`/`PrivilegedPathway`）；拒绝全局 required（混淆合法省略）与只保护 brainstem（留不一致契约） |
| Q3 | 测试 | 四类缺 role 回归 + null 失败断言 + active 正例；验收语义：缺失 → JsonException；显式 active → 正常通过 |
| Q4 | 归属 | 独立 implementation issue **#107** 入串行队列；不并入 #105、不回写 #91 |
| Q5 | Console | `catch (JsonException)` → stderr「数据校验失败」+ exit 1；锁 stderr 内容而非仅 exit code |
| Q6 | 延迟项 | 其余枚举字段「缺失→默认 0」风险延迟；触发标准 ①引擎消费者 ②静默错误语义 ③校验未覆盖 三项同时满足 → 独立评估 |
| Q7 | 收尾 | Step 4 落盘完成 |

### 受影响文件

- `docs/决策树.md`（#106 条目 + #91 推迟项加「→ 见 #106」）——commit fdae389
- `docs/设计框架-六维状态.md`（管线 ✅ 条目，22→23）——commit fdae389
- `.scratch/csharp-data-layer/design/spec.md`（§四 EdgeRole 行 + v1.4）——commit fdae389
- `.scratch/csharp-console/design/spec.md`（AC-12 + v1.3）——commit fdae389
- memory（`引擎fail-fast-grilling-106.md`）
- GitHub：**#107**（implementation issue，排队中）

### 写入验证表

| 决策 | 写入文件 | 位置 | 验证 |
|------|---------|------|------|
| Q1 机制 | 决策树 | §Grilling #106 Q1 | ✅ 已验证 |
| Q2 范围 | 决策树 | §Grilling #106 Q2 | ✅ 已验证 |
| Q3 测试 | 决策树 + #107 body | §Grilling #106 Q3 + 验收标准 | ✅ 已验证 |
| Q4 归属 | 决策树 + #107 | §Grilling #106 Q4 + issue | ✅ 已验证 |
| Q5 Console | 决策树 + console spec AC-12 | §Grilling #106 Q5 + v1.3 | ✅ 已验证 |
| Q6 延迟项 | 决策树 | §Grilling #106 Q6 + 推迟 | ✅ 已验证 |
| Q7 落盘 | 全部 | — | ✅ 已验证 |

### 校验结果（质量门禁）

- 一致性清扫：`CstcProjection` 等错误类名仅存于决策树（刻意记录「注意不是…」，属决策历史）；`垃圾桶` 引用全部在决策历史或 ⚠️ 已废弃段；无路径断裂 ✅
- 交叉引用：决策树 #91→#106 锚点、六维状态→决策树锚点、#107 引用均有效 ✅
- 注册表：无新术语入库（EdgeRole 8 字符不触发 ≤4 规则；fail-fast 语义已由 calibration_status 条目覆盖）✅

### 推迟清单

- 其余枚举字段静默默认风险 → 触发标准 ①+②+③ 同时满足时独立评估
- 引擎层防御实施 → **#107**（串行队列，待排期）

---
*导出: 2026-09-12 | 来源: GitHub issue*
