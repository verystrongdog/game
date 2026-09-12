# #73 [Grilling] P1b LinkState + m 成长进引擎

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/73

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #70 路线图 P1b：把髓鞘化 m 从 demo 常量（m_mean ≡ MDefault=0.3，WMatrixBuilder B4 偏差）升级为三体边级 LinkState——数据结构 + m_mean 入 W + Δm 战后结算 + 可塑性巩固接口 + 聚焦接口。

## 六维定位

- **维度**: 规则（髓鞘化/可塑性巩固/聚焦语义）+ 管线（引擎实现）
- **依赖**: csharp-engine 294/294 ✅（WMatrixBuilder/CombatEvents/CombatState 现状已核查）+ P1a 角色分类（可复用驱动 Δm 激活）+ 核心机制 §1.3（Δm 公式）/§八（可塑性巩固）/§2.2（激活点聚焦）/§10.3（起始 m 层级表）+ 皮层动力学 §5.2/§5.3（m_mean/focus）
- **阻塞**: P1c 技能执行（Δm 的技能激活部分）/ P5 装备·消耗品（调制 m）/ 数值平衡工具 T3（Δm 曲线引擎内验证）

## 当前状态

- `WMatrixBuilder.Build(GameData)` 单参数；m_mean = `CalibrationConfig.Default.MDefault`（static）；focus ≡ 1.0（接口注释预留）
- `LinkGrowthEvent` 存在但 EventProcessor no-op（偏差注）
- `CombatState` 无 link_states；`ParticipantState` 无 m；WMatrix 每场战斗构建一次
- 正典：Δm = base(L) × f(m) × g(n) × 标记倍率；可塑性巩固标记(Δm×2)/增强(m+0.03~0.20)；聚焦 ×2.0 入 W

## 关键待决

1. m 载体范围：CC+PP（888，与 P1a 一致）vs 全 4 类边
2. m 初始值规则：统一 0.3 vs 核心机制 §10.3 层级表（L0 0.15-0.30 ... L4-L5 0.00-0.05）
3. Δm「激活次数」语义：P1a 角色分类驱动基础行动 vs 节点阈值代理 vs 技能驱动（P1c 延迟）
4. 可塑性巩固引擎接口形态
5. 聚焦接口 + WMatrixBuilder.Build 签名变化（数据放哪）

## 预期产出

- `.scratch/grilling-73-p1b-linkstate/task-plan.md`（数据结构/接口/结算规则/实现步骤）
- 决策树追加 + 六维状态更新 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #73 关闭总结

### 决策表（5 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | m 载体 = CC+PP 888 边（与 P1a 一致） | LinkState |
| D2 | m 初始值 = §10.3 层级表中值，边层级 max(source.L, target.L) | CreateInitial |
| D3 | Δm 激活 = P1a 角色驱动基础行动；g(n) 单场战斗内次数 | MyleinGrowth |
| D4 | 可塑性巩固 = TryConsolidate 引擎接口（Mark/Boost + 校验） | LinkState |
| D5 | 聚焦 = Build(GameData, LinkState, FocusSet)，×2.0 | WMatrixBuilder |

### 引擎现状核查

- Build(GameData) 单参数、m_mean=static Default 0.3（B4 偏差）、LinkGrowthEvent no-op、CombatState 无 link_states

### 受影响文件

- `.scratch/grilling-73-p1b-linkstate/task-plan.md`（新建：数据结构/初始化/Δm 规则/T1-T6/验收）
- `docs/决策树.md`（#73 条目）、`docs/设计框架-六维状态.md`（P1b ✅）、memory
- 实施后：LinkState.cs / FocusSet.cs / MyleinGrowth.cs（新建）+ WMatrixBuilder/TurnManager/CombatState/Console/Tests（改写）

### 推迟清单

- 技能使用激活边 → P1c；角色 m 偏移 → 角色批次；事件强度 → 平衡工具；NPC m 模板 → P3

### 质量门禁

- 5 决策全落位；不变量：888 边双射/m∈[0,1]/Boost 仅 m≤0.3/聚焦×2.0/确定性延续
- 后续：T1-T6 实施（依赖 P1a 产物 link_contexts_tripartite.json 的 primary_role）

---
*导出: 2026-09-12 | 来源: GitHub issue*
