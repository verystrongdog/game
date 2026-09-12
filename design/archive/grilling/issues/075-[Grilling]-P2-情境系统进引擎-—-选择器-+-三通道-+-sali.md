# #75 [Grilling] P2 情境系统进引擎 — 选择器 + 三通道 + salience

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/75

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #70 路线图 P2：情境系统进引擎——α_patterns 数据化（#69 D9 落地）+ 27 原型选择器 + s_env/m_field 三通道输入 + 情境 salience 接口（供 P3 NPC 全量）。

## 六维定位

- **维度**: 规则（情境选择/环境基调语义）+ 管线（引擎实现）
- **依赖**: #69 三通道语义（s_事件/s_env/m_field，task-plan 已定 schema）+ situation_primitives.json（27 原型，key_brain_regions/rdoc_profile 已核查）+ EventProcessor 现状（α pattern 硬编码 6 元素定长）+ 运行时状态模型 §4.5（s = W_sensory × α）+ 核心机制 §6.2（情境生成流程：空间类型→观察向量→原型→扰动）
- **阻塞**: P3 NPC Affordance 全量（情境 salience 输入）+ #69 延迟项落地（s_env/m_field 通道）
- **关联**: #38 月光场重建（m_field 参数集待定，本批占位）

## 当前状态

- EventProcessor.cs：14 事件 α pattern 硬编码为 new[]{1,0,1,0,0,0}（6 模态定长）——#69 D9 要迁到 alpha_patterns.json（8 模态）
- situation_primitives.json：27 原型（name/rdoc_profile/appraisal_profile/primary_networks/key_brain_regions/levels_involved/typical_game_scenario）；auto_activated_links 为 legacy 字段（已废弃 364 链路）
- 核心机制 §6.2：空间类型 → 医院观察向量 → 主导情境原型 → RDoC 权重偏置 → 个体扰动（SAN/L1/L3）→ 网络激活
- W_sensory 当前 69×6（#69 已定扩至 69×8，未实施）

## 关键待决

1. α_patterns 数据化实施边界（#69 D9 已定 schema——确认直接实施 + 8 模态数据生成）
2. 情境选择器算法：空间类型→27 原型映射 + SAN 调制 + 刷新时机
3. s_env/m_field 数据源与落点：环境基调表（空间→α_env）+ m_field 占位实现
4. 情境 salience 接口形态：显式（原型 id+偏置输出供 P3）vs 隐式（仅 s(t) 通道自然涌现）

## 预期产出

- `.scratch/grilling-75-p2-situation/task-plan.md`（选择器算法/三通道落点/salience 接口/实现步骤）
- 决策树追加 + 六维状态更新 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #75 关闭总结

### 决策表（4 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | 事件/持续场分离：alpha_patterns.json（14 事件）+ env_tones.json（α_env） | T2/T3 |
| D2 | 情境选择器：映射表 + 低 SAN 概率偏移 + key_brain_regions 直接节点注入 | T5 |
| D3 | 三通道并入 s 数组（s_total），m_field 占位 0 | T6 |
| D4 | 隐式涌现 + 只读 SituationState 接口 | T6 |

### 数据现状核查

- EventProcessor.cs:123 硬编码 6 元素 α pattern；27 原型 key_brain_regions 混合 fid/dk 名；W_sensory 69×6

### 受影响文件

- `.scratch/grilling-75-p2-situation/task-plan.md`（新建：schema/选择器/落点/T1-T7/验收）
- `docs/决策树.md`（#75 条目）、`docs/设计框架-六维状态.md`（P2 ✅）、memory
- 实施后：W_sensory 69×8 / alpha_patterns.json / env_tones.json + EventProcessor/SituationSelector/CombatState/CalibrationConfig/Console/Tests

### 推迟清单

- m_field 参数 → #38；env_tones 全表 → 空间内容；SAN 偏移分组 → 内容填充；强度系数 → #35

### 质量门禁

- 4 决策全落位；不变量：α pattern 前 6 位迁移一致/W_sensory 行序 canonical 69/s_total 范围/确定性延续
- 后续：T1-T7 实施（T1 先行——W_sensory 69×8 是 #69 与 P2 的共同前置）

---
*导出: 2026-09-12 | 来源: GitHub issue*
