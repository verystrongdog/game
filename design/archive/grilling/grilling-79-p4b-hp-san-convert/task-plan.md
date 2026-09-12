# Grilling #79 P4b HP↔SAN 互转进引擎 — 实施任务计划

> Grilling #79 (GitHub #79) 结论：HP↔SAN 互转（核心机制 §5.3 正典数值完整）落地引擎。4 项共识：两独立动作 + M1 / 正典字面公式（floor1+cap 8）/ ≥1 边界 + per-participant 累计 / 只改状态不产事件 + demo。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [兑换规则](#三兑换规则)
4. [动作与通道](#四动作与通道)
5. [引擎落点](#五引擎落点)
6. [任务分解](#六任务分解)
7. [文件清单](#七文件清单)
8. [数据契约与校验](#八数据契约与校验)
9. [验收标准](#九验收标准)
10. [推迟清单](#十推迟清单)

---

## 一、背景与动机

HP↔SAN 互转正典数值完整（核心机制 §5.3：兑换率/单次上限/单场上限/占 M1），引擎无此动作。本批落地——少数无 [NEW] 参数的批次（全部数值为正典值）。互转是不对称交易：HP→SAN 效率更高（真金白银的痛苦换稳定），SAN→HP 是危险交易。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | 两独立动作：`ActionKind.ConvertHpToSan`（自残/疼痛接地）+ `ActionKind.ConvertSanToHp`（吃怪物肉）；payload = 花费量 float；均占 **M1 通道**（与物理攻击互斥）；无冷却 | 动作 |
| D2 | 正典字面公式：HP→SAN `min(spent,10)×2 + max(spent−10,0)×1`（round1）；SAN→HP `min(spent,10)/2 + max(spent−10,0)/3`（**floor1 + cap 8.0**——"换最多 8 HP"字面）；单次上限 15/20 | 公式 |
| D3 | 边界：花费后 **HP ≥ 1 / SAN ≥ 1**（不能自残致死/主动进入随机行为）；单场上限 per-participant 累计（30 SAN / 15 HP），超上限拒绝 | 边界 |
| D4 | 互转**不产生 δ/s 事件**（正典未定义——避免发明）；Console demo 命令 + 额度显示 | 落点 |

## 三、兑换规则

```
HP→SAN（自残——疼痛接地）:
  单次: spent ∈ [0, 15]（≤ 当前 HP − 1，花费后 HP ≥ 1）
  san_gain = min(spent, 10) × 2 + max(spent − 10, 0) × 1    // 满额 25 SAN
  应用: san ← round1(clamp(san + san_gain, 0, sanMax))
  累计: ConvertHpToSanTotal += san_gain；约束 ≤ 30（单场）

SAN→HP（吃怪物肉——月光下信仰赋能的肉体恢复）:
  单次: spent ∈ [0, 20]（≤ 当前 SAN − 1，花费后 SAN ≥ 1）
  hp_gain = floor1(min(spent, 10) / 2 + max(spent − 10, 0) / 3)  // 满额 8.0（cap）
  hp_gain = min(hp_gain, 8.0)                                    // 正典"换最多 8 HP"字面
  应用: hp ← round1(clamp(hp + hp_gain, 0, hpMax))
  累计: ConvertSanToHpTotal += hp_gain；约束 ≤ 15（单场）

校验顺序: 动作声明 → 单次上限 → 当前资源−1 边界 → 单场剩余额度 → 分段公式 → 应用+累计
```

## 四、动作与通道

```csharp
public enum ActionKind { PhysicalAttack, MentalAttack, Defend, Skill, Flee, Surrender, ConvertHpToSan, ConvertSanToHp }

// CombatAction payload: ConvertAmount（float，花费量）
// 通道: ConvertHpToSan / ConvertSanToHp → M1（与物理攻击互斥；正典 §5.3 占 M1 通道）
// 冷却: 无（正典未定义）
```

## 五、引擎落点

```
CombatState:
  float[] ConvertHpToSanTotal   // per-participant 累计恢复 SAN（≤ 30）
  float[] ConvertSanToHpTotal   // per-participant 累计恢复 HP（≤ 15）

ActionResolver 兑换结算（ConvertHpToSan/ConvertSanToHp dispatch）:
  1. 校验: ConvertAmount ≤ 单次上限（15/20）
  2. 校验: 当前资源 − ConvertAmount ≥ 1（D3 边界）
  3. 校验: 累计 + 本次增量 ≤ 单场上限（30/15）
  4. 分段公式（D2）→ 应用 HP/SAN + 累计
  5. 不产生 δ/s 事件（D4）；产生 HealEvent（供结算日志/上层）或仅状态变更（实现时定——日志可经 TurnResult）
```

## 六、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | 正典注：核心机制 §5.3 补边界注（花费后 ≥1、per-participant 累计、不产事件） | 文档 | `规则/核心机制.md` | D3/D4 |
| T2 | `ActionKind` 扩展 + payload 花费量 + M1 通道校验 | 代码 | `Types/Enums.cs` + `Types/CombatAction.cs` | D1 |
| T3 | `CombatState` 累计字段（ConvertHpToSanTotal/ConvertSanToHpTotal） | 代码 | `Entity/CombatState.cs` | D3 |
| T4 | 兑换结算器（校验链 → 分段公式 → 应用+累计） | 代码 | `Flow/ActionResolver.cs` | T2/T3 |
| T5 | Console demo 接线（`convert hp→san N` / `convert san→hp N` + 额度显示） | 代码 | `YouAreNotTheFish.Console` | T4 |
| T6 | 测试（分段公式边界/单次上限/资源−1/累计上限/互斥）+ 决策树/六维状态/memory | 测试+文档 | 测试绿 + 文档 | T1-T5 |

## 七、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `规则/核心机制.md`（§5.3 边界注） | 改写 | 文档 |
| `src/YouAreNotTheFish.Core/Types/Enums.cs` + `CombatAction.cs` | 改写 | 代码 |
| `src/YouAreNotTheFish.Core/Entity/CombatState.cs` | 改写（累计字段） | 代码 |
| `src/YouAreNotTheFish.Core/Flow/ActionResolver.cs` | 改写（兑换结算） | 代码 |
| `src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `src/YouAreNotTheFish.Console/` | 改写 | 代码 |
| `docs/决策树/` / `docs/设计框架-六维状态.md` / memory | 追加 | 文档 |

## 八、数据契约与校验

### 不变量

- 兑换公式与核心机制 §5.3 逐值一致（25 SAN 满额 / 8.0 HP 满额 cap）
- 花费后 HP/SAN ≥ 1（边界保护）；单次 ≤ 15/20；累计 ≤ 30/15（per-participant）
- 通道：两动作均 M1（与物理攻击互斥——IsValidChannelUsage 扩展）
- 一位小数：HP→SAN round1；SAN→HP floor1 + cap 8.0
- 互转不产生 δ/s 事件（确定性——同输入同输出）

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test src/YouAreNotTheFish.Core.Tests` |
| 分段公式 | 满额/半额/边界（10 HP、15 HP、20 SAN 等）单测 |
| 上限 | 单次超限拒绝；累计超限拒绝 单测 |
| 边界 | 花费后 =0 拒绝 单测 |
| 通道互斥 | Convert + PhysicalAttack 同回合非法 单测 |
| 交叉引用 | `python3 tools/validate_cross_refs.py` |

## 九、验收标准

- [ ] 核心机制 §5.3 边界注写入
- [ ] ConvertHpToSan/ConvertSanToHp 动作 + M1 通道校验生效
- [ ] 兑换结算：公式/单次上限/资源−1 边界/累计上限全部生效
- [ ] per-participant 累计（30/15）正确
- [ ] Console demo 可执行互转 + 额度显示
- [ ] 测试绿；决策树 #79 / 六维状态 / memory 落位

## 十、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 互转的 δ/s 事件（自残痛觉感知等） | 正典未定义，避免发明 | 事件系统扩展讨论（观察者效应/内感受批次） |
| 互转与药物/装备交互验证 | 消耗品/装备未进引擎 | P5 实体批次 |
| 互转 UI（确认花费量交互） | 呈现层 | 战斗界面 grilling |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](./../grilling-70-engine-roadmap/task-plan.md), [核心机制](../../../%E8%A7%84%E5%88%99/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [回合战斗流程](../../../%E8%A7%84%E5%88%99/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md), [数学语言书写规范](../../../docs/agents/math-language-writing.md)*
