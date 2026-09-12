# #76 [Grilling] P3 NPC Affordance 全量 — 7 参数化 + salience 正式化

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/76

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #70 路线图 P3：NpcSalience 从 demo 占位（3 行动硬编码 + FirstEnemy）升级为正式 Affordance Competition——7 参数化性格（4 tone baseline + 3 CSTC bias）+ 6 标签映射 + 技能候选集 + T_SAN + 目标选择接口（E-4 闭合）。

## 六维定位

- **维度**: 规则（NPC 决策语义）+ 管线（引擎实现）
- **依赖**: NPC AI 行为模型 §三/§四（正典已完整定义：Salience 公式/tone_bias 权重表/T_SAN/7 参数/6 标签映射表）+ P1a（技能候选集）+ P1b（LinkState——NPC 静态 m 模板）+ P1c（技能执行/通道映射）+ P2（情境只读状态）
- **阻塞**: P4e 多敌方（目标选择多目标）+ 平衡工具 T1（NPC 校准）
- **承接**: #70 路线图 P3（E-4 闭合）

## 当前状态

- NPC AI 正典完整：Salience = mean(a_j ∈ skill.cortical_nodes) × gate_bonus(role) × (1+tone_bias)；tone_bias 8 角色权重表；T = T_base(0.15) + T_SAN(0/+0.10/+0.30/∞)；Boss argmax/杂兵 Softmax；7 参数（4 baseline + 3 bias，bias 生效 = gate_loop_effective = clamp(gate+bias, 0, 1)）；6 标签→7 参数映射表（§4.2，±0.1~0.2/±0.15）；目标选择（§7.2 目标 salience = 节点群均值×gate×tone_bias）
- 引擎 NpcSalience.cs：demo 3 行动硬编码（PhysicalNodes/MentalNodes/DefendNodes + FirstEnemy + 硬编码 baseline/tone_bias）——E-4 闭合对象

## 关键待决

1. 7 参数数据结构 + 标签映射表落点（数据文件 vs 代码常量）
2. NPC 行动候选集构成（基础行动 + 浮现技能；NPC LinkState 静态模板）
3. 选择规则细节（Boss/杂兵/T_SAN/恐慌配置 §9.1）+ 目标选择接口（单目标 demo / 多目标预留）
4. E-4 闭合范围 + Console demo 接线（标签→NPC 模板）

## 预期产出

- `.scratch/grilling-76-p3-npc-affordance/task-plan.md`（数据结构/候选集/选择规则/实现步骤）
- 决策树追加 + 六维状态更新 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #76 关闭总结

### 决策表（4 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | personality_tags.json + NpcPersonality + per-participant baseline | T1/T2 |
| D2 | 候选集 = 3 基础行动（节点模板正式化）+ 已浮现技能（静态 LinkState） | T3 |
| D3 | Boss argmax/杂兵 Softmax + T_SAN + 恐慌配置占位 + 目标选择框架 | T4 |
| D4 | E-4 全闭合：RoleToneWeights 与 A6 sign 同源 + Console 双模板 | T5/T6 |

### 引擎现状核查

- NpcSalience.cs 3 行动硬编码 + FirstEnemy + 硬编码 baseline/tone_bias（plan §4.8 [NEW]）

### 受影响文件

- `.scratch/grilling-76-p3-npc-affordance/task-plan.md`（新建：数据结构/候选集/选择规则/E-4 清单/T1-T7/验收）
- `docs/决策树.md`（#76 条目）、`docs/设计框架-六维状态.md`（P3 ✅）、memory
- 实施后：NpcPersonality.cs/RoleToneWeights.cs/personality_tags.json（新建）+ NpcSalience 重写 + ParticipantState/ToneUpdater/CandidateSetBuilder/Console/Tests

### 推迟清单

- 目标四节点群 → P4e；恐慌配置数值 → #35；NPC 持久髓鞘化 → Boss 批次；多标签样例 → 敌人 Stat 批次

### 质量门禁

- 4 决策全落位；不变量：tags 偏移 ∈ §4.2/RoleToneWeights 与正典逐值一致/A6Sign 单源/确定性延续
- 后续：T1-T7 实施（依赖 P1a 候选池 + P1b NPC 静态 LinkState + P1c 通道映射 + P2 情境只读状态）

---
*导出: 2026-09-12 | 来源: GitHub issue*
