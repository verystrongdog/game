# #74 [Grilling] P1c 技能执行引擎 — 混合注入 + 效果结算 + A6

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/74

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #70 D3（skill.cortical_nodes 激活机制 = C 混合注入+传播）与 P1a/P1b 设计，落地技能执行引擎：技能数据结构 + Δ_skill 混合注入实现 + skill_base_effect × gate_bonus 结算 + A6 事件闭环。

## 六维定位

- **维度**: 规则（技能执行语义/效果公式）+ 管线（引擎实现）
- **依赖**: #70 D3（混合注入裁决）+ P1a（技能候选池 link_contexts_tripartite.json）+ P1b（LinkState/FocusSet）+ 运行时状态模型 §4.5（延迟项闭合）/§五.5（A6）/§八（base 公式）+ 技能生成机制 §五（skill_effect = base × gate）+ NPC AI §3.3（tone_bias 权重表）+ CombatAction 现状（M1/Broca ActionSlot 已核查）
- **阻塞**: P3 NPC Affordance 全量（NpcSalience 正式化需技能候选集）+ 数值平衡工具 T1（scale_mental/θ_mem 校准需技能执行存在）

## 当前状态

- 引擎：CombatAction = M1/Broca 双通道 ActionSlot（ActionKind: PhysicalAttack/MentalAttack/Defend），技能动作待扩展
- 正典：skill_effect = skill_base_effect × gate_bonus(role)；base 从 a(t) 派生（精神攻击 = mean(a of cognitive nodes)×scale_mental、物理技能 = 固定值 + a(Precentral)×w_execution、记忆检索 = σ(mean(a of MTL)−θ_mem)）；A6 δ = sign(tone_bias[skill.role])、α=0
- #70 D3 裁决：核心节点直接注入 Δ_skill（a_j ← clip(a_j+Δ_skill, 0, 1)）+ W·a 网络传播

## 关键待决

1. 技能数据结构：cortical_nodes 来源（组内边端点节点？）+ base_effect 参数
2. skill_base_effect 节点集：组内 nodes vs role 模板节点
3. Δ_skill 注入时序与量（结算前/后？与 m 的关系？）
4. A6 事件 sign 语义确认 + 引擎实现
5. 执行集成：CombatAction 扩展 + ActionResolver 结算流程

## 预期产出

- `.scratch/grilling-74-p1c-skill-execution/task-plan.md`（数据结构/注入时序/结算流程/实现步骤）
- 决策树追加 + 六维状态更新 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #74 关闭总结

### 决策表（5 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | cortical_nodes = 组内边端点 fid 去重集合 | SkillDefinition |
| D2 | base = 组内节点 a(t) 均值（role 公式形态） | SkillResolver |
| D3 | 结算前注入 + Δ_skill×mean(m)，Δ_skill 初始 0.1 [NEW] | SkillResolver |
| D4 | A6 立即闭环：δ = sign(权重表) 代码常量，m=1.0，α=0 | EventProcessor |
| D5 | 通道全表 + 4 类效果；flee/approach/disrupt/perceive 预留 | CombatAction/ActionResolver |

### 引擎现状核查

- CombatAction = M1/Broca ActionSlot（3 ActionKind）→ 扩展 Skill + skillId + 通道校验

### 受影响文件

- `.scratch/grilling-74-p1c-skill-execution/task-plan.md`（新建：数据结构/通道映射/结算流程/A6/T1-T6/验收）
- `docs/决策树.md`（#74 条目）、`docs/设计框架-六维状态.md`（P1c ✅）、memory
- 实施后：SkillDefinition.cs/SkillCatalog.cs/SkillResolver.cs（新建）+ CombatAction/Enums/ActionResolver/CalibrationConfig/Console/Tests（改写）

### 推迟清单

- 技能命名 / flee·approach·disrupt 效果 / perceive 执行 / base 数值（#35）/ support 细分

### 质量门禁

- 5 决策全落位；不变量：EdgeIds ⊆ 888 边/CorticalNodes 去重/a_j∈(0,1)/A6 sign 8 角色全/确定性延续
- 后续：T1-T6 实施（依赖 P1a 产物 link_contexts_tripartite.json）

---
*导出: 2026-09-12 | 来源: GitHub issue*
