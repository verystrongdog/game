# #80 [Grilling] P4e 空间系统进引擎 — 战棋网格 + 多敌方

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/80

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #70 路线图 P4e：空间系统（回合战斗流程 §十 27 项决策正典完整）落地引擎——战棋网格 + 移动经济 + 射程/视线 + 控制区/借机/夹击 + 友伤/AOE + 多敌方窗口。P4 最大批。

## 六维定位

- **维度**: 规则（空间战斗交互）+ 管线（引擎实现）
- **依赖**: 回合战斗流程 §十（27 项决策完整）+ 引擎多参与者现状（Participants/Teams 已支持）+ P3 目标选择框架 + P1c 技能效果（AOE 扩展）+ P4a 软边界自动逃跑（§10.11 关联）
- **阻塞**: 具体敌人 Stat 实例（多敌方战斗验证）+ 平衡工具（空间参数校准）
- **承接**: #70 路线图 P4e（范围表未覆盖）

## 当前状态

- 正典（回合战斗流程 §十）完整：网格 1m/对角 1.5；移动独立配额 12 格 ±30%；穿越（友方可/敌方不可/SAN=0 可）；控制区 1.5m 球体 + 借机攻击；射程 5 级；AOE 链路赋予 + 友伤分级；夹击（-25%/-50%+察觉-2/135°+20%）；高度/视线/掩体；部署/软边界/隐藏敌人/同种共享窗口
- 引擎：Participants/Teams 数组已支持多参与者；TurnOrderBuilder 排序已有多参与者支持；无位置/移动/射程/视线/控制区

## 关键待决（P4e 最大批——按优先级逐题）

1. 空间数据模型（位置 2D+高度 / 战场障碍物 / 距离计算）
2. 移动规则落地（配额/CombatAction 表达/穿越）
3. 射程 + 视线校验（目标合法性）
4. 控制区/借机/夹击/友伤/AOE（战斗交互层）
5. 多敌方窗口/隐藏敌人/部署（范围界定——demo 简化项）

## 预期产出

- `.scratch/grilling-80-p4e-space/task-plan.md`（空间模型/移动/射程/交互/范围 + 实现步骤，可拆子任务）
- 决策树 + 六维状态 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #80 关闭总结

### 决策表（5 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | battlefields.json + Position + 双距离（网格/欧几里得） | T1/T2 |
| D2 | Movement 同窗口 + 配额公式 + 穿越校验 + 软边界→P4a | T3 |
| D3 | 射程视线合法性校验 + SkillDefinition.Range | T4 |
| D4 | 控制区/借机 + 夹击 + 友伤 + AOE 结算器（纯 C# 逻辑） | T5-T7 |
| D5 | 多敌方 5v3 + 部署 + 目标框架；隐藏/伏击接口预留 | T8/T9 |

### 用户架构澄清

「位置/视野涉及渲染只用 C# 模拟可行么」→ 可行且正确：判定=规则层几何算法（DDA 线段-格采样/距离/夹角），Unity 只渲染结果+输入；数据流 battlefields.json → 引擎判定（确定性）→ Unity 显示。符合引擎纯 .NET 库架构。

### 受影响文件

- `.scratch/grilling-80-p4e-space/task-plan.md`（新建：T1-T9）
- `docs/决策树.md`（#80）、`docs/设计框架-六维状态.md`（P4 4/5 闭合）、memory
- 实施后：battlefields.json + Position/BattlefieldMath/ZoneAttack/Flanking/AoeResolver（新建）+ SkillDefinition(+Range/Aoe) + CombatAction(+Movement) + CombatState(+Positions) + ActionResolver + NpcSalience（攻最近）+ Console/Tests

### 推迟清单

- 隐藏/伏击 → 遭遇设计；AOE 链路赋予 → P1 后；目标四节点群 → NPC 精细化；高度/坠落 → 关卡数据；环境交互 → 独立 grilling；空间参数 → #35

### 质量门禁

- 5 决策全落位；不变量：双距离不混用/LOS 纯函数/配额边界/穿越不可违反/全部纯逻辑判定与渲染解耦
- 后续：T1-T9 实施（依赖 P1c SkillDefinition.Range/Aoe 接口 + P3 目标框架 + P4a 软边界逃跑）

---
*导出: 2026-09-12 | 来源: GitHub issue*
