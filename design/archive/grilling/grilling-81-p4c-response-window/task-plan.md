# Grilling #81 P4c 响应窗口进引擎 — 实施任务计划

> Grilling #81 (GitHub #81) 结论：响应窗口（回合战斗流程 §六）落地引擎——IResponseResolver 从 Noop 实现为正式响应解析器。4 项共识：三响应全实现 / L4 读意图 a(t) 驱动 / 忍耐主动自动触发 / 叙事重构 B 条件触发 + "防御主动"表述残留澄清。P4 最后子批闭合。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [响应实现](#三响应实现)
4. [L4 读意图](#四l4-读意图)
5. [忍耐·主动](#五忍耐主动)
6. [L5 叙事重构 B](#六l5-叙事重构-b)
7. [参数速查（[NEW]）](#七参数速查new)
8. [任务分解](#八任务分解)
9. [文件清单](#九文件清单)
10. [数据契约与校验](#十数据契约与校验)
11. [验收标准](#十一验收标准)
12. [推迟清单](#十二推迟清单)

---

## 一、背景与动机

回合战斗流程 §六 响应窗口正典完整（4 种响应类型 + 边界：响应不取消对方行动——即时调整承受方式），引擎 `IResponseResolver` 接口已设计（`Resolve(declared, state, ctx) → IReadOnlyList<CombatEvent>`）但为 Noop stub（`NoopResponseResolver`，`ActionResolver.cs:34` 注入）。L0 回避已在 DamageCalculator 生效（-10% 命中）。P4c 实现剩余 3 种响应，闭合响应窗口 stub（#70 D4 归属）。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | 三响应全实现：L4 读意图 + 忍耐·主动 + L5 叙事重构 B（L0 保持 DamageCalculator 现状 ✅） | 范围 |
| D2 | L4 触发 = **a(t) 动力学驱动**：社会认知节点（mPFC/TPJ/STS——P1a `social_cognition` 域边端点）`mean(a) > 阈值 [NEW]` → 响应可用；效果 = **防御当回合无冷却**（核心机制 §4.4 "读到攻击→可提前防御"） | 规则 |
| D3 | 忍耐·主动 = **响应自动触发**（`EnduranceActiveCd == 0` 且 Broca 通道未用 → 被精神攻击声明时自动使用）：SAN 减免翻倍（−2 最低 1，DamageCalculator 忍耐参数接入）+ Broca 占用 + CD 置 2；UI 留呈现层 | 规则 |
| D4 | 叙事重构 B = 同队成员受伤害事件 + L5 整合节点 `mean(a) > 阈值 [NEW]` → `NarrativeBoost` 状态（下个行动窗口攻击 +25%，一窗口后消失）；**"防御主动"判为 #70 表述残留**（正典无此名词——忍耐·主动是唯一主动变体），不发明；L5 控制（防御借 M1 §7.5）留 L5 技能批次 | 规则 |

## 三、响应实现

```
IResponseResolver 正式实现（替换 Noop）:

Resolve(declared, state, ctx):
  declared 为攻击类行动（PhysicalDamage/MentalDamage 声明）时，对受影响的参与者触发响应:

  1. L4 读意图（被攻击者）: 社会认知节点 mean(a) > ReadIntentThreshold
     → 被攻击者自动进入防御状态（IsDefending = true，防御当回合无冷却——核心机制 §4.4）
  2. 忍耐·主动（被精神攻击者）: EnduranceActiveCd == 0 且 Broca 未用
     → EnduranceActiveEvent（SAN 减免翻倍 + Broca 占用 + CD 置 2）
  3. 叙事重构 B（同队成员）: 受伤害事件 + L5 整合节点 mean(a) > NarrativeThreshold
     → NarrativeBoost 状态（下窗口攻击 +25%）
  L0 回避: 已在 DamageCalculator（不在此处）
```

- 响应不取消对方行动（§6.3 边界——调整事件只是承受方式调整）
- 返回 `IReadOnlyList<CombatEvent>`（调整事件，ActionResolver 结算前应用）

## 四、L4 读意图

```
触发: 社会认知节点 mean(a) > ReadIntentThreshold [NEW]
  节点集: mPFC/TPJ/STS（P1a social_cognition 域边端点——与感知类技能节点一致）
效果: 被攻击者自动进入防御状态（IsDefending）
  当回合防御无冷却（核心机制 §4.4 "读到攻击→可提前防御"）——响应式防御不消耗行动窗口
边界: 仅对物理攻击类声明生效（精神攻击读意图 = 无防御效果——精神防御是认知重评非闪避）
```

## 五、忍耐·主动

```
触发: 被精神攻击声明 + EnduranceActiveCd == 0 + Broca 通道未用（自动）
效果: SAN 减免翻倍（−2 而非 −1，最低 1——DamageCalculator 忍耐参数接入）
  Broca 标记占用（本窗口）+ EnduranceActiveCd = 2
实现: ResponseResolver 返回 EnduranceActiveEvent → ActionResolver 结算前应用
```

## 六、L5 叙事重构 B

```
触发: 同队成员受伤害事件（Physical/Mental DamageEvent）+ L5 整合节点 mean(a) > NarrativeThreshold [NEW]
效果: 响应者获得 NarrativeBoost 状态（StatusKind 扩展）
  下个行动窗口攻击 +25%（物理/精神均生效），一窗口后消失
边界: 触发者自身被伤害不触发（"友方被伤害时"——§6.2 条件）
```

## 七、参数速查（[NEW]）

| 参数 | 符号 | 初始值 | 位置 |
|------|------|--------|------|
| 读意图阈值 | ReadIntentThreshold | 待 #35 [NEW] | CalibrationConfig |
| 叙事重构阈值 | NarrativeThreshold | 待 #35 [NEW] | CalibrationConfig |
| 叙事重构加成 | — | +25%（正典 §6.2） | NarrativeBoost 状态 |
| 忍耐主动减免 | — | −2（正典基础行动设计） | DamageCalculator |

## 八、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | 正典 §6.2 补注：触发条件语义（L4 a(t) 驱动/忍耐自动/叙事重构 B 条件）+ "防御主动"表述残留澄清 | 文档 | `design/rules/回合战斗流程.md` | D2-D4 |
| T2 | `ResponseResolver` 正式实现（3 响应分发 + 触发检查） | 代码 | `Flow/ResponseResolver.cs`（替换 Noop） | D1 |
| T3 | L4 读意图：社会认知节点集 + 阈值判定 + 自动防御（无冷却） | 代码 | `Engine/SocialCognitionNodes.cs` + `ResponseResolver` | T2 |
| T4 | 忍耐·主动：自动触发 + Broca 占用 + CD + 减免翻倍接入 DamageCalculator | 代码 | `ResponseResolver` + `Engine/DamageCalculator.cs` | T2 |
| T5 | 叙事重构 B：`NarrativeBoost` 状态（StatusKind 扩展）+ 下窗口生效 + 消失 | 代码 | `Types/Enums.cs` + `Entity/CombatState.cs` + `DamageCalculator.cs` | T2 |
| T6 | Console demo 接线（响应日志：读意图/忍耐/叙事重构 触发显示）+ 测试 + 文档同步 | 代码+测试+文档 | 测试绿 + 决策树/六维状态/memory | T1-T5 |

## 九、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `design/rules/回合战斗流程.md`（§6.2 补注） | 改写 | 文档 |
| `code/src/YouAreNotTheFish.Core/Flow/ResponseResolver.cs` | 新建（替换 Noop） | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/SocialCognitionNodes.cs` | 新建（节点集） | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/DamageCalculator.cs` | 改写（忍耐主动/NarrativeBoost） | 代码 |
| `code/src/YouAreNotTheFish.Core/Types/Enums.cs`（StatusKind.NarrativeBoost） | 改写 | 代码 |
| `code/src/YouAreNotTheFish.Core/Entity/CombatState.cs` | 改写（状态计时） | 代码 |
| `code/src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` | 改写（+2 [NEW]） | 代码 |
| `code/src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `code/src/YouAreNotTheFish.Console/` | 改写 | 代码 |
| `design/decisions/` / `design/framework/six-dimensions.md` / memory | 追加 | 文档 |

## 十、数据契约与校验

### 不变量

- 响应不取消对方行动（§6.3——调整事件只改承受方式，不拦截伤害事件本身）
- L4 仅物理攻击响应（精神攻击无防御响应——认知重评非闪避）
- 忍耐主动：CD=0 + Broca 未用才自动触发；减免 −2 最低 1；Broca 占用 + CD2
- NarrativeBoost：一行动窗口后消失；触发者自身受伤不触发
- 确定性：响应判定纯函数（节点 a(t) 快照 + 状态检查），同输入同输出

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test code/src/YouAreNotTheFish.Core.Tests` |
| L4 阈值 | 社会认知节点高/低于阈值 响应可用性 单测 |
| 忍耐主动 | CD/Broca 占用/减免翻倍 单测 |
| 叙事重构 | 友方受伤触发/自身受伤不触发/下窗口生效/消失 单测 |
| 交叉引用 | `python3 code/tools/validate_cross_refs.py` |

## 十一、验收标准

- [ ] 回合战斗流程 §6.2 补注完成（触发语义 + 防御主动澄清）
- [ ] ResponseResolver 正式实现（3 响应分发）替换 Noop
- [ ] L4 读意图：a(t) 阈值 + 自动防御无冷却生效
- [ ] 忍耐·主动：自动触发 + 减免翻倍 + Broca 占用 + CD 生效
- [ ] 叙事重构 B：NarrativeBoost 状态 + 下窗口 +25% + 消失生效
- [ ] Console demo 响应日志可见；测试绿；文档落位

## 十二、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 响应选择 UI（忍耐主动手动选择等） | 呈现层 | 战斗界面 grilling |
| L5 控制（防御期间借 M1，§7.5 暂定翻译） | L5 技能批次 | L5 技能 grilling |
| NPC 响应策略（读意图/忍耐的 salience 判定） | P3 基础已定，响应侧细化 | NPC 精细化批次 |
| 响应阈值校准 | [NEW] | #35 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](../grilling-70-engine-roadmap/task-plan.md), [回合战斗流程](../../../rules/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md), [核心机制](../../../rules/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [基础行动设计](../../../rules/skill-tree/operations/%E5%9F%BA%E7%A1%80%E8%A1%8C%E5%8A%A8%E8%AE%BE%E8%AE%A1.md), [Grilling #74 P1c task-plan](../grilling-74-p1c-skill-execution/task-plan.md), [数学语言书写规范](../../../conventions/agents/math-language-writing.md)*
