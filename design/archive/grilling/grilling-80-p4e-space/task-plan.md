# Grilling #80 P4e 空间系统进引擎 — 实施任务计划

> Grilling #80 (GitHub #80) 结论：空间系统（回合战斗流程 §十 27 项决策）落地引擎。5 项共识：battlefields 数据+双距离 / Movement+配额+穿越 / 射程视线合法性校验 / 交互层+AOE 结算器（纯 C# 逻辑判定） / demo 范围界定（隐藏/伏击接口预留）。本文档为决策→实施的桥梁。P4 最大批。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [空间模型](#三空间模型)
4. [移动规则](#四移动规则)
5. [射程与视线](#五射程与视线)
6. [战斗交互层](#六战斗交互层)
7. [多敌方与部署](#七多敌方与部署)
8. [参数速查（[NEW]）](#八参数速查new)
9. [任务分解](#九任务分解)
10. [文件清单](#十文件清单)
11. [数据契约与校验](#十一数据契约与校验)
12. [验收标准](#十二验收标准)
13. [推迟清单](#十三推迟清单)

---

## 一、背景与动机

回合战斗流程 §十 27 项决策正典完整（网格/移动/穿越/控制区/射程/夹击/高度/视线/部署/软边界/友伤/隐藏/多敌方），引擎无空间层。P4e 落地——**全部为纯 C# 逻辑判定**（用户确认：位置/视线/掩体 = 规则层几何算法，Unity 只渲染结果与输入，与引擎纯 .NET 库架构一致，确定性保持）。P4 最后一大批。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | 空间模型 = `battlefields.json`（尺寸+障碍物+初始站位）+ `Position(x,y,z 整米)` + **双距离**（移动用网格距离对角 1.5 / 射程控制区用欧几里得） | 数据 |
| D2 | 移动 = `CombatAction.Movement` 同窗口并存 + 配额 `12×clamp(1+k_move×(执行分−0.5), 0.8, 1.2)` [NEW] + 穿越校验（敌方格不可穿/友方可/SAN=0 与倒地可/同格禁两人）+ 软边界→P4a 逃跑 | 规则 |
| D3 | 射程视线 = 目标合法性校验（欧几里得 ≤ 射程；全高阻挡拒绝含精神；半高/生物命中修正 −20%/−10%×挡路数）+ `SkillDefinition.Range` [NEW] | 规则 |
| D4 | 交互层 = 控制区 1.5m + 自动借机（占未用通道）+ 夹击（−25%/−50%+察觉−2/135°+20%）+ 友伤分级 + AOE 结算器（形状/半径/递减，`SkillDefinition.Aoe` 接口预留）——全部纯逻辑判定 | 规则 |
| D5 | demo 范围 = 多敌方（现有排序满足，5v3 可跑）+ 部署预设（battlefields 站位）+ P3 目标框架激活（攻最近）；隐藏/伏击**接口预留后置** | 范围 |

## 三、空间模型

### 3.1 `data/battlefields.json`（新建）

```json
{
  "schema": "battlefields", "version": 1,
  "battlefields": [
    {
      "id": "ward_7x7",
      "name": "病房（7×7）",
      "width": 7, "height": 7,
      "obstacles": [
        {"x": 3, "y": 3, "height": 2, "block": "full"},     // 全高阻挡（床柱/柜）
        {"x": 2, "y": 4, "height": 1, "block": "half"}      // 半高（病床）
      ],
      "deploy": {
        "team0": [{"x": 0, "y": 3, "z": 0}],                // 玩家侧站位
        "team1": [{"x": 6, "y": 3, "z": 0}]                 // 敌方侧站位
      }
    }
  ]
}
```

- demo 预设：病房 7×7 / 走廊 3×12（§10.1 尺寸推导：走廊 3m 宽、病房 6.9m）
- 高度 z 整米（§10.8 关卡数据，不画 Z 网格）

### 3.2 Position 与双距离

```csharp
public sealed record Position(float X, float Y, int Z);

// 网格距离（移动消耗，§10.1）: |dx|+|dy| + (对角步 × 0.5) —— 对角 1.5 格
// 欧几里得距离（射程/控制区，§10.4 物理球体）: sqrt(dx² + dy² + dz²)
```

- 距离函数 `BattlefieldMath`：`GridDistance(p1, p2)` / `EuclideanDistance(p1, p2)`（纯函数，确定性）

### 3.3 视线算法（DDA 线段-格采样）

```
LOS(origin, target, battlefield):
  采样 origin→target 线段经过的格子（DDA/Bresenham）
  → 遇全高阻挡（height ≥ 2 且 z 区间遮挡）→ blocked（不可瞄准，含精神 §10.9）
  → 遇半高 → 命中修正 −20%；生物（敌方/友方在瞄准线）→ −10%×挡路数
```

## 四、移动规则

```
CombatAction.Movement（float 距离，与 M1/Broca 动作并存——先走位后攻击或反之，Order 决定）

移动配额: MoveQuota = 12 × clamp(1 + k_move × (执行分 − 0.5), 0.8, 1.2)   [k_move 待 #35]
  （§10.2 "察觉快/执行快的人移动力更高"；执行分 0.5 = 静息基准）

移动校验（移动结算时）:
  1. 移动距离 ≤ MoveQuota（配额内）
  2. 路径穿越（§10.3）: 敌方格不可穿（控制区阻挡）/友方可免费/SAN=0 与倒地可穿/同格不可站两人
  3. 软边界（§10.11）: 终点超出战场范围 → 触发 P4a 逃跑流程（Fled + A7 + SAN 恢复——已设计）
```

## 五、射程与视线

```
目标合法性校验（行动声明时）:
  1. 距离: 欧几里得(target − origin) ≤ 射程
     基础行动: 物理 = 近战（≤ 控制区 1.5m）/ 精神 = 视线内（不限距离 §10.5）
     技能: SkillDefinition.Range（近战/短 3/中 8/远 20/视线内）
  2. 视线: LOS 判定（§3.3）——全高阻挡 → 拒绝（精神也受阻）；半高/生物 → 命中修正
  3. 非法目标（超射程/无视线）→ 声明拒绝（重选）

命中修正链（物理）: 85% + 武器修正 + 链路修正 − L0 回避 − 半掩体 20% − 生物挡路 10%×N + 夹击 20%（§六）
```

## 六、战斗交互层

### 6.1 控制区与自动借机（§10.4）

```
控制区: 以位置为中心 1.5m 欧几里得球体（覆盖相邻格：角格中心 1.4 < 1.5）
借机: 移动路径出敌方控制区 → 自动触发（占该敌方未用 M1/Broca 通道）
  - 通道未用 → 借机反击（物理 M1 / 精神 Broca）
  - 通道已用 → 不可借机（"先动了手就反应不过来" §10.4）
```

### 6.2 夹击（§10.7）

```
被围判定: 敌方在自身控制区内数量
  2 敌 → 防御效果 −25%
  3+ 敌 → 防御 −50% + 察觉分 −2（速度排序劣势）
角度夹击: 两敌相对自身夹角 ≥ 135° → 该敌 M1 命中 +20%
  （向量夹角 = acos(dot(v1, v2) / |v1||v2|)，纯几何）
```

### 6.3 友伤与 AOE（§10.6/§10.12）

```
FriendlyFireLevel [NEW]（CalibrationConfig）: 0 关 / 0.5 中 / 1.0 高

AOE 结算器（范围命中）:
  技能定义加 Aoe 参数 [NEW]（SkillDefinition 扩展——接口预留）:
    shape: cone / circle / multi_target
    radius: float（米）
    falloff: 伤害递减（如边缘 50%）
    friendly_fire: bool（默认 true——友伤按难度分级）
  结算: 范围内所有目标（含友方）→ 伤害 × (1 − falloff) + 友伤 × FriendlyFireLevel
  链路赋予语义（哪些链路给 AOE，§10.6）随技能批次（P1a 角色分类 → AOE 技能定义）
```

## 七、多敌方与部署

```
多敌方: TurnOrderBuilder 现有多参与者排序满足（同种共享窗口 ≈ 同速同组依次执行——硬币破平已存在，§10.16）
部署: battlefields.json deploy 站位 → CombatState 初始化 Position（§10.10 常态预设；伏击/被偷袭接口预留）
目标选择: P3 目标框架激活——demo 简化版: 攻击欧几里得最近敌方（§7.2 四节点群全量留后续）
隐藏敌人: 接口预留（隐藏标记 + 排序跳过逻辑——demo 战场无隐藏）
伏击: 接口预留（伏击自由轮标志——demo 不设伏击）
```

## 八、参数速查（[NEW]）

| 参数 | 符号 | 初始值 | 位置 |
|------|------|--------|------|
| 移动力斜率 | k_move | 待 #35 [NEW] | CalibrationConfig |
| 友伤分级 | FriendlyFireLevel | 0（低=关）[NEW] | CalibrationConfig |
| 技能射程 | SkillDefinition.Range | 近战/短3/中8/远20/视线内 [NEW] | SkillDefinition |
| AOE 参数 | SkillDefinition.Aoe | shape/radius/falloff/友伤 [NEW] | SkillDefinition |

## 九、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | `battlefields.json` + `Battlefield` 数据 + `Position` 结构 | 数据+代码 | `data/battlefields.json` + `Types/Position.cs` | D1 |
| T2 | 距离计算（网格/欧几里得）+ 视线算法（DDA 线段-格采样） | 代码 | `Engine/BattlefieldMath.cs` | T1 |
| T3 | 移动：`CombatAction.Movement` + 配额公式 + 穿越校验 + 软边界→P4a 逃跑 | 代码 | `Flow/ActionResolver.cs`（移动段） | T2 |
| T4 | 射程校验 + 视线命中修正 + `SkillDefinition.Range` 扩展 | 代码 | `Types/SkillDefinition.cs` + `ActionResolver.cs` | T2/T3 |
| T5 | 控制区 + 自动借机（占未用通道） | 代码 | `Engine/ZoneAttack.cs` | T2 |
| T6 | 夹击（防御修正/察觉−2/135° 命中） | 代码 | `Engine/Flanking.cs` | T2 |
| T7 | AOE 结算器（形状/半径/递减/友伤分级）+ `SkillDefinition.Aoe` 接口 | 代码 | `Engine/AoeResolver.cs` | T4 |
| T8 | 部署站位 + P3 目标框架激活（攻最近）+ 隐藏/伏击接口 | 代码 | `Entity/CombatState.cs`（Position 初始化）+ `NpcSalience.cs`（目标选择） | T5 |
| T9 | Console demo（多敌方战场演示：移动/射程/视线/夹击/借机）+ 测试 + 文档同步 | 代码+测试+文档 | 测试绿 + 决策树/六维状态/memory | T1-T8 |

## 十、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `data/battlefields.json` | 新建 | 数据 |
| `code/src/YouAreNotTheFish.Core/Types/Position.cs` | 新建 | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/BattlefieldMath.cs` | 新建 | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/ZoneAttack.cs` / `Flanking.cs` / `AoeResolver.cs` | 新建 | 代码 |
| `code/src/YouAreNotTheFish.Core/Types/SkillDefinition.cs` | 改写（+Range/Aoe） | 代码 |
| `code/src/YouAreNotTheFish.Core/Types/CombatAction.cs` | 改写（+Movement） | 代码 |
| `code/src/YouAreNotTheFish.Core/Entity/CombatState.cs` | 改写（+Positions/战场） | 代码 |
| `code/src/YouAreNotTheFish.Core/Flow/ActionResolver.cs` | 改写（移动/射程/借机） | 代码 |
| `code/src/YouAreNotTheFish.Core/Engine/NpcSalience.cs` | 改写（目标=攻最近） | 代码 |
| `code/src/YouAreNotTheFish.Core.Tests/` | 新增 | 测试 |
| `code/src/YouAreNotTheFish.Console/` | 改写（多敌方战场演示） | 代码 |
| `design/decisions/` / `design/framework/six-dimensions.md` / memory | 追加 | 文档 |

## 十一、数据契约与校验

### 不变量

- 双距离语义：移动=网格（对角 1.5）、射程/控制区=欧几里得——不混用
- LOS 纯函数：同战场同位置同输出（确定性）
- 移动配额 ∈ [9.6, 14.4]（12×0.8 / 12×1.2 边界）；穿越规则不可违反
- 夹击/借机/友伤全部纯逻辑判定，与渲染解耦
- Position 更新唯一入口（ActionResolver 移动结算）

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test code/src/YouAreNotTheFish.Core.Tests` |
| 距离 | 网格对角 1.5 / 欧几里得 单测 |
| LOS | 全高阻断/半高修正/生物挡路 单测 |
| 移动 | 配额边界/穿越拒绝/软边界逃跑 单测 |
| 夹击 | 2 敌/3+敌/135° 单测 |
| 友伤 | 三级难度 AOE 伤害 单测 |
| 交叉引用 | `python3 code/tools/validate_cross_refs.py` |

## 十二、验收标准

- [ ] battlefields.json（病房/走廊）+ Position + 双距离生效
- [ ] 移动（配额/穿越/软边界）完整；CombatAction.Movement 同窗口
- [ ] 射程 + 视线校验（全高拒绝/修正）生效
- [ ] 控制区/自动借机/夹击/友伤分级/AOE 结算器可用
- [ ] 多敌方（5v3）demo 可跑；部署站位生效；目标=攻最近
- [ ] 隐藏/伏击接口预留（无 demo 场景）
- [ ] 测试绿；决策树 #80 / 六维状态 / memory 落位

## 十三、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 隐藏敌人/伏击/被偷袭 | demo 战场无此场景 | 内容填充（遭遇设计批次） |
| AOE 链路赋予语义（哪些链路给 AOE） | 技能批次（P1a 角色分类→AOE 定义） | P1 实施后 |
| 目标选择四节点群全量（恐惧/奖赏/认知/社交） | demo 简化=攻最近 | NPC 精细化批次 |
| 高度/坠落/攀爬细节验证 | demo 战场平面 | 关卡设计数据就绪后 |
| 环境交互（关门/推倒/推挤 §10.13） | 战场道具数据未设计 | 环境交互 grilling |
| 空间参数校准（k_move/射程平衡） | 初始值 [NEW] | #35 数值校准 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](../grilling-70-engine-roadmap/task-plan.md), [回合战斗流程](../../../rules/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md), [Grilling #73 P1b task-plan](../grilling-73-p1b-linkstate/task-plan.md), [Grilling #76 P3 task-plan](../grilling-76-p3-npc-affordance/task-plan.md), [Grilling #78 P4a task-plan](../grilling-78-p4a-flee-surrender/task-plan.md), [数学语言书写规范](../../../conventions/agents/math-language-writing.md)*
