# Grilling #78 P4a 逃跑/投降进引擎 — 实施任务计划

> Grilling #78 (GitHub #78) 结论：逃跑/投降规则（回合战斗流程 §8 正典）落地引擎 + 补 [NEW] 数值。4 项共识：逃跑默认成功 / FleeSanRestore +10 + Δm 跳过 + A7 闭环 / 投降简化判定（理性类型+SAN≥30%）/ ExitStatus 四态 + IsOver 扩展。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [规则补全（[NEW]）](#三规则补全new)
4. [ExitStatus 与动作扩展](#四exitstatus-与动作扩展)
5. [逃跑流程](#五逃跑流程)
6. [投降流程](#六投降流程)
7. [战斗结束条件扩展](#七战斗结束条件扩展)
8. [任务分解](#八任务分解)
9. [文件清单](#九文件清单)
10. [数据契约与校验](#十数据契约与校验)
11. [验收标准](#十一验收标准)
12. [推迟清单](#十二推迟清单)

---

## 一、背景与动机

正典已定义（回合战斗流程 §8.2/§8.3：逃跑 = M1 通道宣布→成功退出、失败例外 = L5 控制压制回避；惩罚 = SAN 部分恢复 + 无髓鞘化增长；投降 = Broca 通道、理性敌方查表接受/拒绝、精神病人/造物无效；全部敌方逃跑/投降 → 战斗结束），但引擎无逃跑/投降动作，IsOver 只查 HP/SAN。A7 事件（δ (1,−1,0,0) + α 视觉+躯体）未接线（E-2 缺口）。本批落地 + 补 [NEW] 数值。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | 逃跑默认成功（无成功率判定——正典无此规则）；L5 控制压制回避 = 接口预留；软边界自动逃跑 P4e 接入 | 规则 |
| D2 | 逃跑惩罚 = `FleeSanRestore [NEW] = +10`（待 #35）+ Δm 结算跳过（逃跑者标记未完成）+ **A7 事件闭环**（E-2） | 规则 |
| D3 | 投降简化判定 = 敌方类型 ∈ {医疗人员, 拜月教徒} 且 敌方 SAN ≥ 30%（"有理性残余" [NEW]，与恐慌阈值对齐）；demo 默认接受；拒绝细节 [NEW] 待 P3 性格 + 叙事对话系统 | 规则 |
| D4 | `ExitStatus` 四态（None/Fled/Surrendered/Defeated）+ `ActionKind.Flee`（M1）/`Surrender`（Broca）+ `IsOver` 扩展（任一方全员 ExitStatus ≠ None → 结束）；退出者保留状态快照 | 范围 |

## 三、规则补全（[NEW]）

| 参数 | 符号 | 初始值 | 位置 |
|------|------|--------|------|
| 逃跑 SAN 恢复 | FleeSanRestore | +10 [NEW] | CalibrationConfig |
| 理性残余阈值 | SurrenderSanThreshold | 30% SAN [NEW] | CalibrationConfig（与恐慌阈值对齐） |
| 投降接受判定 | — | demo 默认接受 [NEW] | 叙事对话系统细化后替换 |

## 四、ExitStatus 与动作扩展

```csharp
// Types/Enums.cs
public enum ExitStatus { None, Fled, Surrendered, Defeated }

// Types/ParticipantState.cs（+ExitStatus，默认 None）
// 语义: HP=0 → Defeated（即时退出队列，保留场地）；逃跑 → Fled；投降 → Surrendered

// Types/Enums.cs ActionKind 扩展
public enum ActionKind { PhysicalAttack, MentalAttack, Defend, Skill, Flee, Surrender }

// 通道校验（回合战斗流程 §8.2/§8.3）:
//   Flee → M1 通道；Surrender → Broca 通道
```

## 五、逃跑流程

```
Phase 4 行动窗口 — FleeAction（M1 通道）:
1. L5 控制压制检查（接口预留——demo 无 L5 技能 → 恒不压制）
2. ExitStatus = Fled
3. 移出行动队列（保留在 Participants——状态快照供结算/叙事）
4. A7 事件 emit（对逃跑者自身）: δ (1,−1,0,0) + α [1,0,1,0,0,0,0,0]（视觉+躯体）m=1.0
5. SAN 恢复: san ← clamp(san + FleeSanRestore, 0, sanMax)   // +10 [NEW]
6. Δm 跳过标记: 逃跑者不参与战后 Δm 结算（P1b 衔接——MyleinGrowth 跳过 ExitStatus ≠ None 参与者）
```

## 六、投降流程

```
Phase 4 行动窗口 — SurrenderAction（Broca 通道）:
1. 判定（D3）:
   敌方类型 ∈ {医疗人员, 拜月教徒}（理性敌方）   // 敌方模板字段
   且 敌方 SAN% ≥ SurrenderSanThreshold（30%——恐慌=无理性）
   → 有效；否则无效（战斗继续）
2. 接受判定（demo 默认接受；拒绝条件 [NEW] 待 P3 性格 + 叙事对话系统）
3. 接受 → 投降方全员 ExitStatus = Surrendered → 战斗结束（IsOver）
   投降方败北——非死亡: 无尸体、SAN 不归零、可继续叙事
```

## 七、战斗结束条件扩展

```
IsOver(state):
  if state.Round >= MaxRounds → true
  foreach team: members.All(p => p.ExitStatus != None) → true   // 全员退出（含逃跑/投降/击败）
  // HP=0 语义并入 ExitStatus.Defeated（保留既有 HP≤0 判定等价）
```

## 八、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | 正典写入：回合战斗流程 §8.2/§8.3 补 [NEW] 值（FleeSanRestore/理性阈值/投降 demo 判定注） | 文档 | `design/rules/回合战斗流程.md` | D1-D3 |
| T2 | `ExitStatus` + `ActionKind.Flee/Surrender` + 通道校验 | 代码 | `Types/Enums.cs` + `Types/ParticipantState.cs` + `Types/CombatAction.cs` | D4 |
| T3 | 逃跑流程（Fled 标记 + 移出队列 + A7 emit + SAN 恢复 + Δm 跳过标记） | 代码 | `Flow/ActionResolver.cs` + `Engine/EventProcessor.cs`（A7 接线） | T2 |
| T4 | 投降流程（判定 + Surrendered + 战斗结束触发） | 代码 | `Flow/ActionResolver.cs` | T2 |
| T5 | `IsOver` 扩展（全员 ExitStatus ≠ None） | 代码 | `Flow/TurnManager.cs` | T3/T4 |
| T6 | Console demo 接线（逃跑/投降命令 + A7 日志 + 结束原因显示）+ 测试 + 文档同步 | 代码+测试+文档 | 测试绿 + 决策树/六维状态/memory | T1-T5 |

## 九、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `design/rules/回合战斗流程.md`（§8.2/§8.3 补 [NEW]） | 改写 | 文档 |
| `code/src/YouAreNotTheFish.Core/Types/Enums.cs` | 改写（ExitStatus/ActionKind） | 代码 |
| `code/src/YouAreNotTheFish.Core/Types/ParticipantState.cs` | 改写（+ExitStatus） | 代码 |
| `code/src/YouAreNotTheFish.Core/Flow/ActionResolver.cs` | 改写（逃跑/投降） | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/EventProcessor.cs` | 改写（A7 接线） | 代码 |
| `code/src/YouAreNotTheFish.Core/Flow/TurnManager.cs` | 改写（IsOver） | 代码 |
| `code/src/YouAreNotTheFish.Core.Types/CalibrationConfig.cs` | 改写（+2 [NEW]） | 代码 |
| `code/src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `code/src/YouAreNotTheFish.Console/` | 改写 | 代码 |
| `design/decisions/` / `design/framework/six-dimensions.md` / memory | 追加 | 文档 |

## 十、数据契约与校验

### 不变量

- 逃跑/投降通道校验：Flee→M1、Surrender→Broca（CombatAction.IsValidChannelUsage 扩展）
- ExitStatus 单向：None → Fled/Surrendered/Defeated（不可逆）；退出者保留在 Participants（快照）
- A7 emit 恒伴随逃跑成功（事件不丢失）；SAN 恢复 clamp [0, sanMax]
- IsOver：ExitStatus ≠ None 全员判定与既有 HP≤0∨SAN≤0 等价（Defeated 语义合并）

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test code/src/YouAreNotTheFish.Core.Tests` |
| 通道校验 | Flee/Surrender 非法通道抛错 |
| 逃跑流程 | A7 design/events/恢复/Δm 跳过 单测 |
| 投降判定 | 理性/非理性/SAN 边界 单测 |
| IsOver | 全员逃跑/投降 → 结束 单测 |
| 交叉引用 | `python3 code/tools/validate_cross_refs.py` |

## 十一、验收标准

- [ ] 正典 §8.2/§8.3 补 [NEW] 值完成
- [ ] ExitStatus 四态 + Flee/Surrender 动作 + 通道校验生效
- [ ] 逃跑流程完整（Fled + A7 + SAN+10 + Δm 跳过）
- [ ] 投降判定生效（理性类型 + SAN≥30%；demo 默认接受）
- [ ] IsOver 全员退出判定生效
- [ ] Console demo 可执行逃跑/投降；测试绿；文档落位

## 十二、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| L5 控制压制回避 | L5 技能未实现 | L5 技能批次 |
| 软边界自动逃跑 | 空间系统未实现 | P4e |
| 投降拒绝查表（性格/概率） | P3 性格 + 叙事对话系统未完成 | P3 后 + 对话系统 grilling |
| 逃跑成功率（若未来需要） | 正典未定义 | 数值校准讨论 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](../grilling-70-engine-roadmap/task-plan.md), [回合战斗流程](../../../rules/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md), [核心机制](../../../rules/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [Grilling #73 P1b task-plan](../grilling-73-p1b-linkstate/task-plan.md), [数学语言书写规范](../../../conventions/agents/math-language-writing.md)*
