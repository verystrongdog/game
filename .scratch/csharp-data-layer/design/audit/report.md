# 审计报告: C# Data Layer 实现规格

> 审计日期: 2026-08-12 | 审计方法: workflow 3 专家 agent（数据结构 + 交叉引用 + 完整性）→ 综合 | spec 版本: v1.0

## Trace Table

### AC 追踪（7 项，3 ❌ + 1 ❌数据 + 1 ⚠️ + 2 ✅）

| AC | 覆盖项 | 判定 | 依据 |
|----|--------|------|------|
| AC-1 | §2.2 WsensoryMatrix + LoadWsensory | ❌ | `matrix_2d` 值为 int 0/1，`bool[][]` 反序列化抛 `JsonException`（.NET 8 实测） |
| AC-2 | §五 约束1（rows key ∈ regions） | ✅ | 69/69 双向双射，无缺失 |
| AC-3 | §2.2 SituationPrimitives + LoadSituationPrimitives | ❌ | 根 key 为 `situation_archetypes`，spec 属性 `Archetypes` 无 `[JsonPropertyName]`，反序列化得 0 个 |
| AC-4 | §五 约束3（key_brain_regions ∈ regions） | ❌ | 39 引用中 3 个悬挂：ReflexEscape、SeptalRegion、Habenula（连模糊匹配都不存在） |
| AC-5 | §2.2 SignalTypesCatalog + LoadSignalTypes | ❌ | 根 key 为 `_categories`（下划线前缀），spec 无属性声明 → 0 categories；且声称 19 子类，实际 18 |
| AC-6 | §2.1 已有代码一致性 | ⚠️ 内容为真但不可自动化 | 100 字段全部 ✅，但 JSON 新增 key 会被静默忽略，测试全绿也发现不了 |
| AC-7 | build + 测试 | ✅ | 当前 build 0 错误 0 警告，10 测试全绿 |

### §2.1 已实现 Records（100 字段 — 全部 ✅）

| Record | 字段数 | 判定 |
|--------|--------|------|
| FunctionProfile | 11 | ✅ enum/nullable/映射全部正确 |
| BrainRegion | 16 | ✅ 含 hemisphere 仅 2 区出现 |
| BrainRegionsData | 1 | ✅ |
| FunctionLabel | 4 | ✅ signal_type 18 词表全覆盖 |
| GraphNode | 13 | ✅ |
| NodeProfile | 7 | ✅ |
| CorticocorticalEdge | 11 | ✅ |
| BrainstemProjection | 11 | ✅ |
| CstcEdge | 10 | ✅ |
| PrivilegedPathway | 11 | ✅ |
| TripartiteModel | 6 | ✅ 51/51/776/114/47/112 计数正确 |

**结论：`/home/dog/game/src/YouAreNotTheFish.Core/Data/` 无需任何改动。**

### §2.2 待实现 Records（33 字段：18 ❌ 映射失配 + 1 ❌ 类型错误 + 2 ⚠️ 值域错误）

**根因**：`PropertyNameCaseInsensitive = true` 只忽略大小写，**不忽略下划线**。§2.2 所有代码块无一处 `[JsonPropertyName]`→ snake_case 字段静默反序列化为默认值，不抛错、数据全丢。

关键错误字段：

| 字段 | JSON key | 问题 |
|------|----------|------|
| `Matrix` | matrix_2d | 无属性失配 + int 0/1 → `bool[][]` 抛 JsonException |
| `Archetypes` | situation_archetypes | 无属性失配（AC-3 必挂） |
| `Categories` | _categories | 无属性失配（AC-5 必挂） |
| `Description` | _description | 无属性失配 |
| `DisplayName` 等 12 字段 | snake_case | 无属性失配，静默丢数据 |
| `Agency` | agency | 值域错误：spec "environment" → 实际 `circumstance` |
| `Valence` | valence | 值域错误：spec "neutral" → 实际 `ambiguous` |

### signal_types 词表内容级错误（spec vs 实际 JSON）

| 类目 | spec 声称 | 实际 JSON |
|------|----------|-----------|
| excitation | 5 子类（含 learning_signal） | 6 子类（+emotional_salience, +social_intention） |
| gating | 5 子类 | 4 子类（go_direct/nogo_indirect/stop_hyperdirect/disinhibition_thalamic） |
| modulation | 5 子类 | 5 子类（motor_DA/pain_opioid 替代 punishment_da/stress_cortisol） |
| plasticity | 4 子类 | 3 子类（ltp_consolidation/ltd_depression 替代 prediction_error 等） |
| **合计** | **19** | **18**（6+4+5+3） |

spec 引用了 Grilling #26 时代的旧词表，数据文件已更新但 spec 未同步。

### 交叉引用约束追踪

| 约束 | 实测 | 判定 |
|------|------|------|
| §五 约束1 W_sensory rows ∈ regions | 69/69 双向双射 | ✅ |
| §五 约束2 matrix_2d 行序 = rows key 序 | 0 mismatch | ⚠️ 验证方式只查行数不查行序 |
| §五 约束3 key_brain_regions ∈ regions | 3/39 悬挂 | ❌ AC-4 必挂 |
| §五 约束4 levels_involved ∈ L0..L5 | 27/27 合法 | ⚠️ 无 AC 覆盖 |
| §五 约束5 signal_type 格式 | 18/18 全覆盖 | ⚠️ 格式校验挡不住拼写错误 |
| **遗漏1** input_types/output_types ∈ 词表 | 0 缺失 | data 通过，spec 未记录 |
| **遗漏2** function_label 内部一致性 | 0 不一致 | data 通过，spec 未约束 |
| **遗漏3** tripartite 边 source/target | 1049 条 0 坏引用 | **最大引用面零约束** |
| **遗漏4** mirror_of ∈ regions | 2 条合法 | data 通过，spec 未约束 |
| **遗漏5** primary_networks 注册表 | 2 值近失配 | 需设计决策 |
| **遗漏6** auto_activated_links | 105 条旧链路名 | ⚠️ 指向已废弃 364 链路模型，按垃圾桶隔离原则必须显式处理 |

## 缺口汇总

### Error 级（6 项 — 阻断性，spec 必须修复后才能实现）

| # | 缺口 | 影响 |
|----|------|------|
| E1 | §2.2 全部代码块缺 `[JsonPropertyName]`（18 字段失配） | 静默数据全丢；AC-3/AC-5 必挂 |
| E2 | `Matrix` 声明 `bool[][]` ← JSON int 0/1 | 运行时抛 JsonException；AC-1 必挂 |
| E3 | signal_types 词表过时（19→18，10 个 subtype 名不存在） | AC-5 必挂；实现者按 spec 造数据污染词表 |
| E4 | RdocProfile 3 域 vs 数据 6 域（缺 positive_valence/arousal_regulatory/sensorimotor） | 静默丢 3 域数据 |
| E5 | AC-4 数据悬挂：3 个 region 引用无对应脑区（ReflexEscape/SeptalRegion/Habenula） | AC-4 必失败；需上游决策 |
| E6 | agency/valence 值域文档错误 | 按 spec 写校验误报 |

### Warning 级（10 项）

| # | 缺口 |
|----|------|
| W1 | RegionIds 填充方案未说明，无 AC 测它 |
| W2 | SignalSubtype 异构字段（neurotransmitter/pathway/mechanism 等）静默丢弃 |
| W3 | 三体边 `type` key + 根对象 `_` 前缀 key 未声明有意不映射 |
| W4 | W_sensory.json 3 个未建模顶层 key（modality_nodes 等） |
| W5 | §五 约束2 验证方式太弱（只查行数）；约束5 应升级为 membership 校验 |
| W6 | §五 约束2/4/5 + loader 异常分支无 AC 覆盖 |
| W7 | AC-6 不可自动化（建议降级为一次性审计产物） |
| W8 | 遗漏约束 5/6 需设计决策后方可补入 |
| W9 | §七自检清单与新类型脱节（"枚举字段解析"不适用） |
| W10 | Modalities 等无下划线字段靠 case-insensitive 碰巧匹配 |

## 审计结论

**❌ 退回修改（有 error）**

三个 AC（AC-1/3/5）按 spec 原样实现必失败，且失败原因是 spec 自身错误而非实现错误。§2.2 待实现部分 18 处映射失配将导致静默数据全丢。AC-4 因数据悬挂必失败。

**§2.1 已实现部分 100 字段全部正确，`src/YouAreNotTheFish.Core/Data/` 无需改动。**

### 必须修复（E1-E6，全改 spec 不改数据文件）

1. §2.2 全部代码块补 `[JsonPropertyName]`（19 处）
2. `Matrix` 改 `int[][]`（与 `Rows` 的 `Dictionary<string,int>` 自洽）
3. signal_types 词表更新为实际 18 子类，AC-5 改为 "4 categories × 18 subtypes"
4. RdocProfile 扩为 6 域（+positive_valence/arousal_regulatory/sensorimotor）
5. agency 值域改 `{circumstance, other, self}`；valence 改 `{ambiguous, negative, positive}`
6. AC-4 设计决策：补 3 个 region 到 `brain_regions.json` 或加豁免名单

## 半径扩张

| 修复点 | 受影响消费者 | 复查状态 |
|--------|------------|---------|
| spec.md §2.2 全部代码块 | 3 个新 Loader 方法 + 7 个新 record | 待修复后重审 |
| AC-1/3/5 描述 | 对应测试 | 待修复后重审 |
| AC-4 设计决策 | brain_regions.json（如补 region）/ spec（如豁免） | **需人类决策** |
| auto_activated_links 废弃引用 | 364 链路模型 → CSTC 词表 | **需人类决策** |
| primary_networks 对齐 | functional_networks.networks 注册表 | 待修复后复查 |

---

# Δ审计报告（v1.1 → v1.2）

> 审计日期: 2026-08-12 | 审计方法: workflow 3 专家 agent（数据结构Δ + 交叉引用Δ + 完整性Δ）→ 综合 | spec 版本: v1.1 → v1.2

## 审计结论

**⚠️ 有条件通过**（v1.2 已满足条件，数据侧免重审）

### 数据侧：完全通过

三路独立实测一致：
- E1-E6 修复全部实测确认（41 个 `[JsonPropertyName]` 逐字段吻合、69×6 int 矩阵、18 子类词表、RdocProfile 6 域、0 悬挂引用、agency/valence 值域吻合）
- §五 11 条约束 11/11 通过：C1 69/69 双向双射、C2 逐行逐模态 0 mismatch、C3 201 引用 0 悬挂、C5 588/588 ∈ 词表、C7 拼接 0 不一致、C9 1049 条边 0 坏引用、C10 88 引用 0 失配

### 规格侧：2 个 AC 覆盖缺口（已在 v1.2 修复）

| # | 缺口 | v1.2 处置 |
|---|------|-----------|
| E-Δ1 | 约束8（mirror_of）无 AC | ✅ AC-13 新增 |
| E-Δ2 | 约束9（1049 三体边，最大引用面）无 AC——v1.0 核心问题只修复一半 | ✅ AC-14 新增（显式覆盖 brainstem target + privileged_pathways） |

### 文本修正（v1.2 同批）

- 变更日志 ×19→×41；「词表最大消费方」备注移至约束5（588 vs 283）；约束8 来源列注明 `function_profile.mirror_of`；§三 异常行为时态修正（AC-11 测试）；约束9 交集语义注明
- auto_activated_links 豁免在 AC 层注明（§六 表下注）

### Warning 级（非阻断，进结转清单）

| # | 发现 | 处置 |
|---|------|------|
| W-6 | Matrix 行序依赖 Dictionary 反序列化保序（实践行为非语言保证），loader 后处理 `Rows.Keys.ToArray()` 依赖此序 | 工作issue 测试加显式断言（Matrix 行序 == Rows.Keys 序） |
| W-7 | agency/valence 值域仅注释声明，无 AC 强制（已记录设计决定：保持 string） | 接受风险 |
| W-8 | rdoc_profile 各 archetype 仅 3-4 域子集，无全 6 域者——nullable 设计正确 | 信息项 |

### 半径扩张（工作issue 创建时的硬性前置）

1. 测试 issue 的 scope 必须显式包含：brainstem target + privileged_pathways source/target membership（约束9 未覆盖面）
2. AC-12 测试需另读原始 JSON 获取 functional_networks 注册表（SituationPrimitives 未映射该 key）
3. AC-11 异常三分支测试须进测试 issue 范围（当前 0 异常测试）
4. 现有测试扩展：`EnumFieldsAreParsedCorrectly` 追加 mirror_of membership 断言；`PrivilegedPathwayFieldsExist` 扩展为 membership 校验

---
*创建: 2026-08-12 | 更新: 2026-08-12*
*关联: [spec.md](../spec.md) v1.2, [任务issue 01](../issues/01-data-layer-spec.md)*
