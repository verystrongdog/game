# Grilling #83 P5-2 消耗品进引擎 — 实施任务计划

> Grilling #83 (GitHub #83) 结论：消耗品系统（17 药物）落地引擎。4 项共识：drugs.json+上下文映射（§3.15 缺口填充）/ EffectiveM+W 重算 / UseItem 占 M1（杂项动作）/ 过量战斗内+依赖戒断耐药接口+禁止组合校验。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [药物数据与映射](#三药物数据与映射)
4. [调制生效机制](#四调制生效机制)
5. [使用流程](#五使用流程)
6. [风险模型与禁止组合](#六风险模型与禁止组合)
7. [任务分解](#七任务分解)
8. [文件清单](#八文件清单)
9. [数据契约与校验](#九数据契约与校验)
10. [验收标准](#十验收标准)
11. [推迟清单](#十一推迟清单)

---

## 一、背景与动机

消耗品系统.md 正典完整（17 药物/调制模型/风险/禁止组合），但 §3.15 明确"具体药物-链路映射表待内容填充"（13 功能域废弃后）——数据缺口。调制影响有效 m 值（P1b LinkState 衔接），战斗中使用（占 1 动作）。P5-2 落地：drugs.json + 调制生效 + 使用流程 + 风险。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | `drugs.json` [NEW] 17 药 + **上下文级调制目标**（P1a 衔接——§3.15 域表 → gameplay_domain → P1a 上下文桥接）；首批 3-4 药完整映射，其余按域批量生成 | 数据 |
| D2 | 调制生效 = `CombatState.EffectiveM[edgeId] = clamp(LinkState.M + Σ偏移, 0, 1)`（拮抗天花板：药物+组件偏移总和 ≤ 1.4，冲突取绝对值最大——决策树 #4）+ **W 脏标记下回合重算** + 钳制 ↕ = 有效 m 锁定区间 | 机制 |
| D3 | 使用 = `ActionKind.UseItem`（M1 通道——**杂项动作**，同环境交互 §10.13）+ 每回合 1 种 + 同域叠加后药降级（§八） | 动作 |
| D4 | 风险 = 过量战斗内落地（单场 ≥2 窄治疗窗 → 调制翻倍+负面）+ 依赖/戒断/耐药跨战斗计数器**接口预留**（N/K/M [NEW] 待 #35）+ 禁止组合（致死阻止/危险警告标志） | 范围 |

## 三、药物数据与映射

### 3.1 `data/drugs.json`（新建）

```json
{
  "schema": "drugs", "version": 1,
  "drugs": [
    {"id": "diazepam", "name": "地西泮", "rarity": "uncommon",
     "modulations": [
       {"target_context": "threat_defense/defend", "type": "inhibit", "strength": "med"},
       {"target_context": "arousal_modulation/perceive", "type": "inhibit", "strength": "med"}
     ],
     "risk": "dependence", "special_effect": "SAN 承受力↑（威胁被压制）、速度↓"},
    {"id": "haloperidol", "name": "氟哌啶醇", "rarity": "very_rare",
     "modulations": [{"target_context": "reward_learning/approach", "type": "inhibit", "strength": "strong"}],
     "risk": "tolerance", "special_effect": "清除幻觉/妄想 + 概率动作失败（僵硬）"},
    {"id": "clozapine", "name": "氯氮平", "rarity": "very_rare",
     "modulations": [
       {"target_context": "reward_learning/approach", "type": "inhibit", "strength": "weak"},
       {"target_context": "cognitive_control/support", "type": "enhance", "strength": "med"},
       {"target_context": "memory_consolidation/support", "type": "clamp", "strength": "med"}
     ],
     "risk": "tolerance", "special_effect": "SAN 大幅恢复 + 清除精神异常"}
  ]
}
```

- 调制目标 = P1a 上下文（`network/role` 键）——§3.15 域映射表翻译：防御域 → `threat_defense/defend` 等（gameplay_domain → P1a 上下文桥接）
- 首批完整映射 3-4 药（地西泮/氟哌啶醇/哌甲酯/氯氮平——代表 4 类调制），其余 13 药按 §3.15 域表批量生成（映射表可后续调整——#35/内容填充）

### 3.2 携带与使用数据

- 携带上限 6 → 9 → 12（叙事扩容——构建层，demo 用 6）
- 同种 2 片/槽；物品栏独立于技能槽

## 四、调制生效机制

```
CombatState.EffectiveM[edgeId]:
  base = LinkState.M[edgeId]
  mods = Σ 药物调制偏移（↓ = −Δ / ↑ = +Δ / ↕ = 钳制区间）
  拮抗检查: Σ(药物+组件) 偏移 ≤ 1.4（超限拒绝/截断）；药物抑制 + 组件增强同边 → 取绝对值最大者
  EffectiveM = clamp(base + 净偏移, 0, 1)
  钳制 ↕: EffectiveM 锁定在 [lo, hi]（如碳酸锂 SAN 地板——clamp 区间）

W 重算: 药物使用 → EffectiveM 变化 → W 脏标记 → 下回合 Phase 1 前 WMatrixBuilder 重算（69×69 一次性）
```

- 调制强度映射（§2.2）：弱 ±0.1-0.2 / 中 ±0.2-0.4 / 强 ±0.4-0.6
- 持续时间：整场战斗（战斗结束重置——EffectiveM 归 LinkState.M）

## 五、使用流程

```
ActionKind.UseItem（M1 通道——杂项动作，与环境交互同款 §10.13）+ itemId payload
  校验: 携带量 > 0 / 每回合 1 种（CombatState 记录本回合已用药物）/ 禁止组合（§六）
  结算: 应用调制（更新 EffectiveM → W 脏）→ 消耗 1 片
  每回合限制: 1 种（CombatState.UsedDrugThisRound）
  同域叠加: 两种药物调制同一上下文 → 后药强度 −1 级（§八——强→中→弱→无效）
```

## 六、风险模型与禁止组合

```
过量（战斗内落地）:
  CombatState.DrugUseCount[drugId] —— 单场同种 ≥ 2（窄治疗窗: 碳酸锂/阿米替林）
  → 调制翻倍 + 附加负面（碳酸锂: SAN 暴跌+运动失灵 / 阿米替林: 速度↓↓+概率跳过）

依赖/戒断/耐药（跨战斗计数器——接口预留）:
  DrugPersistentState（构建层持久）: DependenceCount / ToleranceCount / 戒断窗口
  N/K/M 阈值 [NEW] 待 #35 数值模拟——demo 不触发（字段与校验接口就位）

禁止组合:
  致死（苯二氮䓬+酒精 / SSRI+MDMA）→ 使用校验直接阻止
  危险（氯胺酮+酒精 / 碳酸锂+布洛芬）→ 警告标志——demo 允许强行 + 触发负面（跳过 2 回合等）
```

## 七、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | `drugs.json`（17 药 + 上下文调制映射——首批 3-4 完整 + 其余按域批量） | 数据 | `data/drugs.json` | D1 |
| T2 | 药物数据 + `ActionKind.UseItem`（M1 杂项）+ 携带量/物品栏 | 代码 | `Types/Enums.cs` + `Types/Drug.cs` | T1 |
| T3 | `EffectiveM` 表 + W 脏标记重算 + 拮抗天花板 + 钳制区间 | 代码 | `Entity/CombatState.cs` + `Engine/WMatrixBuilder.cs`（重算入口） | T2 + P1b |
| T4 | 使用结算（调制应用 + 每回合 1 种 + 同域降级 + 消耗） | 代码 | `Flow/ActionResolver.cs` | T3 |
| T5 | 风险：过量计数 + 依赖戒断耐药接口（DrugPersistentState）+ 禁止组合校验 | 代码 | `Entity/DrugPersistentState.cs` + `ActionResolver.cs` | T4 |
| T6 | Console demo：`use <药物>` 命令 + EffectiveM 显示 + 效果/风险日志 | 代码 | `YouAreNotTheFish.Console` | T4/T5 |
| T7 | 测试（调制叠加/拮抗/钳制/同域降级/过量/禁止组合）+ 文档同步 | 测试+文档 | 测试绿 + 决策树/六维状态/memory | T1-T6 |

## 八、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `data/drugs.json` | 新建 | 数据 |
| `code/src/YouAreNotTheFish.Core/Types/Drug.cs` | 新建 | 代码 |
| `code/src/YouAreNotTheFish.Core/Entity/CombatState.cs` | 改写（EffectiveM/计数） | 代码 |
| `code/src/YouAreNotTheFish.Core/Entity/DrugPersistentState.cs` | 新建（跨战斗接口） | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/WMatrixBuilder.cs` | 改写（EffectiveM 消费/重算入口） | 代码 |
| `code/src/YouAreNotTheFish.Core/Flow/ActionResolver.cs` | 改写（UseItem） | 代码 |
| `code/src/YouAreNotTheFish.Core/Types/Enums.cs`（UseItem/钳制） | 改写 | 代码 |
| `code/src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `code/src/YouAreNotTheFish.Console/` | 改写 | 代码 |
| `design/decisions/` / `design/framework/six-dimensions.md` / memory | 追加 | 文档 |

## 九、数据契约与校验

### 不变量

- drugs.json 17 药全；调制目标为 P1a 上下文键（与 link_contexts_tripartite 一致）
- EffectiveM = clamp(base + 净偏移, 0, 1)；拮抗天花板 Σ ≤ 1.4；冲突取绝对值最大
- 钳制 = 区间锁定；战斗结束 EffectiveM 归 LinkState.M（构建层不污染）
- 每回合 1 种；同域叠加后药降级；过量单场 ≥2 触发
- 致死组合直接阻止；危险组合警告标志
- 确定性：EffectiveM/W 重算纯函数，同输入同输出

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test code/src/YouAreNotTheFish.Core.Tests` |
| 调制叠加 | 单药/双药/拮抗超限 单测 |
| 钳制 | 区间锁定 单测 |
| 同域降级 | 后药强度降级 单测 |
| 过量 | 单场 2 次触发 单测 |
| 禁止组合 | 致死阻止/危险警告 单测 |
| 交叉引用 | `python3 code/tools/validate_cross_refs.py` |

## 十、验收标准

- [ ] drugs.json 17 药 + 上下文映射（首批 3-4 完整）
- [ ] UseItem 动作（M1 杂项）+ 携带量 + 每回合 1 种 + 同域降级
- [ ] EffectiveM + W 重算 + 拮抗天花板 + 钳制区间生效
- [ ] 过量触发；依赖/戒断/耐药接口预留（N/K/M [NEW]）
- [ ] 禁止组合校验（致死阻止/危险警告）
- [ ] Console demo `use` 命令 + EffectiveM 显示
- [ ] 测试绿；决策树 #83 / 六维状态 / memory 落位

## 十一、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 药物-上下文映射全量精调 | 首批 3-4 完整 + 其余批量 | 内容填充批次 |
| 依赖/戒断/耐药数值（N/K/M） | 待数值模拟 | #35 |
| 非战斗使用（SSRI 休息增益/尼古丁社交货币） | 休息/社交系统未进引擎 | 休息系统批次 |
| 敌我同构敌人用药 | P3 NPC 行动候选集扩展（UseItem） | NPC 精细化批次 |
| 涌现效果细节（SAN 承受力/速度变化——下游涌现） | 部分依赖情境/状态系统 | 状态系统扩展批次 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](../grilling-70-engine-roadmap/task-plan.md), [消耗品系统](../../../entities/%E6%B6%88%E8%80%97%E5%93%81%E7%B3%BB%E7%BB%9F.md), [Grilling #72 P1a task-plan](../grilling-72-p1a-skill-context/task-plan.md), [Grilling #73 P1b task-plan](../grilling-73-p1b-linkstate/task-plan.md), [数学语言书写规范](../../../conventions/agents/math-language-writing.md)*
