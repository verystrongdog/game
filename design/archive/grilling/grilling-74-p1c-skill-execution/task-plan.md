# Grilling #74 P1c 技能执行引擎 — 实施任务计划

> Grilling #74 (GitHub #74) 结论：落地技能执行引擎（#70 D3 混合注入裁决 + P1a/P1b 设计的执行端）。5 项共识：cortical_nodes=组内端点 fid / base=组内节点均值（role 公式形态）/ 结算前注入 + Δ_skill×mean(m) / A6 立即闭环 / 通道全表 + 4 类效果。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [SkillDefinition 数据结构](#三skilldefinition-数据结构)
4. [通道映射](#四通道映射)
5. [技能结算流程](#五技能结算流程)
6. [A6 事件](#六a6-事件)
7. [任务分解](#七任务分解)
8. [文件清单](#八文件清单)
9. [数据契约与校验](#九数据契约与校验)
10. [验收标准](#十验收标准)
11. [推迟清单](#十一推迟清单)

---

## 一、背景与动机

#70 D3 裁决 skill.cortical_nodes 激活机制 = C 混合注入+传播（运行时 §4.5 延迟项闭合）：核心节点直接注入 Δ_skill + W·a 网络传播。P1a 产出技能候选池（context ≥2 边），P1b 产出 LinkState/FocusSet。P1c 落地执行端：SkillDefinition 数据 + 注入 + base×gate 结算 + A6 事件——阻塞 P3 NPC 全量（NpcSalience 需技能候选集）与平衡工具 T1（scale_mental/θ_mem 校准需技能执行）。

**引擎现状**：`CombatAction` = M1/Broca 双通道 `ActionSlot`（ActionKind: PhysicalAttack/MentalAttack/Defend，CombatAction.cs:6-28）；技能动作待扩展。正典 base 公式（运行时 §八）+ A6（§5.5）+ tone_bias 权重表（NPC AI §3.3）。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | `cortical_nodes` = **组内边端点 functional_id 去重集合**（P1a 双视图供给）；命名属构建层/UI 后置 | 数据 |
| D2 | `skill_base_effect` = **组内节点 a(t) 均值**（公式形态按 role：乘 scale_mental / 加 w_execution / σ−θ_mem）——技能数值与自身组内边状态绑定（"调链路改技能数值" D3 意图） | 规则 |
| D3 | 注入 = **结算前**（同回合生效）+ **Δ_skill × mean(m of 组内边)**；Δ_skill 初始 0.1 [NEW] 待 #35 校准；聚焦已经 W ×2.0 反映，注入不乘 focus（防双算） | 规则 |
| D4 | A6 = **立即闭环**：技能使用成功 emit，δ = sign(tone_bias[role]) 代码常量（NPC AI §3.3 推导，与 Gurney 权重表同惯例），m=1.0，α=0 | 事件 |
| D5 | 执行集成 = **通道全表 + 4 类效果**（物理/精神/防御/记忆检索），flee/approach/perceive/disrupt 接口预留 | 范围 |

## 三、SkillDefinition 数据结构

```csharp
// Types/SkillDefinition.cs（不可变——构建层技能目录数据）
public sealed record SkillDefinition
{
    public string Id { get; init; }            // 涌现命名后置——P1c 用占位 id（network_role 组合）
    public string Network { get; init; }       // 主导网络（kroell14 name）
    public string Role { get; init; }          // 8 行为角色（P1a primary_role）
    public IReadOnlyList<string> EdgeIds { get; init; }   // cc:NNN / pp:NNN（P1a context 内边）
    public IReadOnlyList<string> CorticalNodes { get; init; }  // 组内边端点 fid 去重（D1）
}

// Data/SkillCatalog.cs —— 从 P1a link_contexts_tripartite.json 构建
//   候选技能 = context(edge_count ≥ 2) → SkillDefinition
//   依赖 P1a 产物；P1a 未实施时由 domain_role_map + tripartite 临时构建（T1 兼容）
```

**CorticalNodes 推导**：`∪ {fid : fid ∈ functional_ids(dk(edge.source)) ∪ functional_ids(dk(edge.target)) for edge in EdgeIds}`（dk→fid 经 tripartite graph_nodes）。

## 四、通道映射

| role | 通道 | 说明 |
|------|------|------|
| attack_physical | M1 | 物理动作 |
| defend | M1 | 与基础防御同通道 |
| approach | M1 | 趋近/移动（接口预留，P3/P4 补） |
| flee | M1 | 逃跑（接口预留，P4a 补） |
| attack_mental | Broca | 语言/认知攻击 |
| disrupt | Broca | 社会干扰（接口预留） |
| support | Broca | 记忆检索/安抚（P1c 实现记忆检索） |
| perceive | 无通道（响应型预留） | 输入型，gate bypass（运行时 §6.5） |

**CombatAction 扩展**：

```csharp
public enum ActionKind { PhysicalAttack, MentalAttack, Defend, Skill }  // +Skill
public sealed record ActionSlot
{
    // 既有字段不变；Skill 动作时:
    //   Kind = Skill; Payload = skillId
}
// 校验: Skill 动作的通道必须匹配 role 映射（D5）；perceive 不允许作行动窗口动作
```

## 五、技能结算流程

```
Phase 4 行动窗口 — SkillAction 结算（ActionResolver 扩展）:

1. 查 SkillCatalog → SkillDefinition（含 CorticalNodes）
2. 注入（D3，结算前）:
     Δ_inj = Δ_skill × mean(m of EdgeIds)      // Δ_skill = CalibrationConfig.SkillDeltaSkill（初始 0.1）
     for j ∈ CorticalNodes: a_j ← clip(a_j + Δ_inj, 0, 1)
3. base（D2，组内节点）:
     attack_physical: base = base_fixed + mean(a of CorticalNodes) × w_execution
                       （base_fixed/w_execution [NEW] 待 #35——demo 用 4 / 1.0 对齐基础行动）
     attack_mental:   base = mean(a of CorticalNodes) × scale_mental
     defend:          base = 防御减伤提升（× (1 + mean(a of CorticalNodes) × k_defend)）[NEW]
     support(记忆):   success = σ(mean(a of MTL ∩ CorticalNodes) − θ_mem)
4. effect = base × gate_bonus(role)              // 运行时 §6.5
5. 效果事件（复用 DamageCalculator）:
     物理伤害 → PhysicalDamageEvent（命中判定同基础行动）
     精神伤害 → MentalDamageEvent（永远命中，忍耐减免，低 SAN 穿透）
     防御 → 防御增强状态
     记忆检索 → 成功则 HealEvent/状态增益（细节随 support 技能设计）
6. A6 emit（§六）——对技能使用者
```

**确定性**：注入修改的是战斗内 a(t)（WcState），非 LinkState——战斗内注入在 Phase 1 更新后、结算前即时生效，下回合 Phase 1 自然衰减/传播（W·a）。

## 六、A6 事件

```
触发: 技能结算成功（每技能执行一次）→ emit A6（仅技能使用者，α=0 不产生 s）
δ = sign(tone_bias[role]) —— 代码常量（NPC AI §3.3 权重表推导，注释带正典引用）:
  perceive      ( +, 0, 0, 0 )
  attack_physical ( 0, +, +, − )
  attack_mental ( 0, +, 0, − )
  defend        ( +, −, 0, + )
  approach      ( 0, +, +, − )
  flee          ( +, −, 0, − )
  disrupt       ( 0, +, 0, − )
  support       ( 0, 0, 0, + )
m = 1.0（与 A7/C1/D1/D2 同类：事件固定最大）；经 EventProcessor δ 实时注入（与既有 A 类事件同路径）
```

## 七、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | `SkillDefinition` + `SkillCatalog`（P1a 候选池 → 技能目录；P1a 未就绪时 domain_role_map 临时构建兼容） | 代码 | `Types/SkillDefinition.cs` + `Data/SkillCatalog.cs` | P1a 产物 |
| T2 | `CombatAction` 扩展（ActionKind.Skill + skillId + 通道映射校验） | 代码 | `Types/CombatAction.cs` + `Types/Enums.cs` | D5 |
| T3 | 技能结算器：注入（Δ_skill×mean(m)）→ base（组内节点×role 公式）→ gate → 4 类效果事件 + A6 emit | 代码 | `Engine/SkillResolver.cs` | T1/T2 |
| T4 | `ActionResolver` 集成（SkillAction dispatch 进 Phase 4） | 代码 | `Flow/ActionResolver.cs` | T3 |
| T5 | Console demo 接线（快捷槽技能选择/执行/注入后 a(t) 变化显示/效果/A6 日志） | 代码 | `YouAreNotTheFish.Console` | T4 |
| T6 | 测试（注入 clip/mean(m) 调制/base 组内节点/gate 乘算/A6 sign 8 角色/通道校验）+ 文档同步 | 测试+文档 | 测试绿 + 决策树/六维状态/memory | T1-T5 |

## 八、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `code/src/YouAreNotTheFish.Core/Types/SkillDefinition.cs` | 新建 | 代码 |
| `code/src/YouAreNotTheFish.Core/Data/SkillCatalog.cs` | 新建 | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/SkillResolver.cs` | 新建 | 代码 |
| `code/src/YouAreNotTheFish.Core/Types/CombatAction.cs` + `Enums.cs` | 改写（+Skill） | 代码 |
| `code/src/YouAreNotTheFish.Core/Flow/ActionResolver.cs` | 改写（dispatch） | 代码 |
| `code/src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` | 改写（+SkillDeltaSkill 等 [NEW]） | 代码 |
| `code/src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `code/src/YouAreNotTheFish.Console/` | 改写 | 代码 |
| `data/connectivity/link_contexts_tripartite.json`（P1a 产物） | 依赖 | 数据 |
| `design/decisions/` / `design/framework/six-dimensions.md` / memory | 追加 | 文档 |

## 九、数据契约与校验

### 不变量

- SkillDefinition.EdgeIds ⊆ CC+PP 888 边键；CorticalNodes 为端点 fid 去重（与 P1a 双视图一致）
- 注入后 a_j ∈ (0,1)（clip 保证）；注入只改战斗内 WcState，不改 LinkState
- 效果 = base × gate_bonus（运行时 §6.5）；A6 δ = sign 常量表（8 角色全）
- 确定性：SkillCatalog 构建纯函数，同输入同输出

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test code/src/YouAreNotTheFish.Core.Tests` |
| 通道校验 | Skill 动作 role→通道 映射单测（非法通道抛错） |
| A6 sign | 8 角色 × 4 tone 逐项断言 |
| 注入效果 | demo：技能执行后 CorticalNodes a(t) 提升 + base 变化可见 |
| 交叉引用 | `python3 code/tools/validate_cross_refs.py` |

## 十、验收标准

- [ ] SkillCatalog 从 P1a 候选池构建（context ≥2 边 → SkillDefinition），CorticalNodes 端点 fid 去重
- [ ] CombatAction.Skill 动作可用，通道映射校验生效（perceive 禁作行动窗口动作）
- [ ] 技能结算：结算前注入（Δ_skill×mean(m)）→ base（组内节点）→ gate → 4 类效果事件
- [ ] A6 emit：8 角色 sign 常量表正确，m=1.0，α=0
- [ ] Console demo 可执行技能并显示注入/a(t)/效果/A6 日志
- [ ] 测试绿；决策树 #74 / 六维状态 / memory 落位

## 十一、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 技能命名（涌现触发命名） | 构建层/UI 语义 | 技能系统 grilling（P1c 后） |
| flee/approach/disrupt 效果 | P4a 逃跑/P3 NPC 未实现 | 各自批次补 |
| perceive 技能执行语义（响应型） | 响应窗口 L1/L3/L5 交互未实现 | P4c |
| base_fixed/w_execution/k_defend 数值 | 无正典值 | #35 校准 |
| support 技能细分（安抚/记忆检索） | 效果集待设计 | support 技能 grilling |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](../grilling-70-engine-roadmap/task-plan.md), [Grilling #72 P1a task-plan](../grilling-72-p1a-skill-context/task-plan.md), [Grilling #73 P1b task-plan](../grilling-73-p1b-linkstate/task-plan.md), [运行时状态模型](../../../rules/skill-tree/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md), [技能生成机制](../../../rules/skill-tree/%E6%8A%80%E8%83%BD%E7%94%9F%E6%88%90%E6%9C%BA%E5%88%B6.md), [NPC AI 行为模型](../../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md), [数学语言书写规范](../../../conventions/agents/math-language-writing.md)*
