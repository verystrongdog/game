# #78 [Grilling] P4a 逃跑/投降进引擎 — A7 闭环

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/78

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #70 路线图 P4a：逃跑/投降规则（回合战斗流程 §8.2/§8.3 正典已有）落地引擎——CombatAction 扩展 + 退出战斗逻辑 + A7 事件闭环 + 战斗结束条件扩展。

## 六维定位

- **维度**: 规则（逃跑/投降判定）+ 管线（引擎实现）
- **依赖**: 回合战斗流程 §8.2/§8.3（正典完整）+ 引擎 TurnManager.IsOver 现状（全灭/回合上限已实现）+ CombatAction 现状 + P1b（Δm 结算——逃跑者跳过）+ P3（NPC 性格——投降接受判定关联）
- **阻塞**: P4e 空间系统（软边界自动逃跑关联）
- **承接**: #70 路线图 P4a（E-2 A7 事件闭环）

## 当前状态

- 正典（回合战斗流程 §8.2/§8.3）：逃跑 = M1 通道宣布 → 成功退出（失败例外 = L5 控制压制回避）；惩罚 = SAN 部分恢复 + 无髓鞘化增长；投降 = Broca 通道（有理性残余敌方：医疗人员/拜月教徒查表接受/拒绝；对精神病人/思维造物无效；详细流程归叙事/对话系统）；全部剩余敌方逃跑/投降 → 战斗结束
- 引擎：IsOver 已实现（一方全灭 Hp≤0∨San≤0 或 MaxRounds）；无逃跑/投降动作；A7 事件（δ (1,-1,0,0) + α 视觉+躯体）未接线（E-2 缺口）

## 关键待决

1. 逃跑成功率（正典字面默认成功 + L5 压制接口预留）
2. 逃跑惩罚细节（SAN 恢复量 [NEW] + Δm 跳过）
3. 投降判定（接受条件——敌方类型 + demo 简化）
4. 战斗结束条件扩展 + A7 接线 + 退出队列处理

## 预期产出

- `.scratch/grilling-78-p4a-flee-surrender/task-plan.md` + 正典补充（SAN 恢复量等 [NEW]）+ 决策树 + 六维状态 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #78 关闭总结

### 决策表（4 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | 逃跑默认成功 + L5 接口预留 + 软边界 P4e | ActionResolver |
| D2 | FleeSanRestore +10 [NEW] + Δm 跳过 + A7 闭环 | ActionResolver/EventProcessor |
| D3 | 投降简化判定（理性类型 + SAN≥30%）demo 默认接受 | ActionResolver |
| D4 | ExitStatus 四态 + Flee/Surrender 动作 + IsOver 扩展 | Enums/ParticipantState/TurnManager |

### 受影响文件

- `.scratch/grilling-78-p4a-flee-surrender/task-plan.md`（新建）
- `规则/回合战斗流程.md`（§8.2 投降行 + §8.3 逃跑规则补 [NEW]）✅ 已写入
- `docs/决策树.md`（#78）、`docs/设计框架-六维状态.md`（P4a ✅）、memory
- 实施后：Enums/CombatAction/ParticipantState/ActionResolver/EventProcessor(A7)/TurnManager(IsOver)/CalibrationConfig(+2 [NEW])

### 推迟清单

- L5 压制 → L5 批次；软边界 → P4e；投降拒绝查表 → P3+对话系统；逃跑成功率（如需）→ 校准讨论

### 质量门禁

- 4 决策全落位；E-2 的 A7 事件闭环条件齐备；正典 §8 已补 [NEW] 值
- 后续：T2-T6 引擎实施

---
*导出: 2026-09-12 | 来源: GitHub issue*
