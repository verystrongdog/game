# 任务issue 01: csharp-flow 规格（CombatState + TurnManager + ActionResolver）

> Status: claimed | Type: task | 维度: 管线 | Blocked by: csharp-events ✅（2026-08-14 闭合） | GitHub: [#66](https://github.com/verystrongdog/game/issues/66)

## 范围

产出 [spec.md](../spec.md) v1.0，覆盖 plan §十一 step 10（csharp-flow）：

- `CombatState`（Entity/）——可变战斗状态：per-participant ParticipantState（含 s_pending `float[69]` 累计槽）+ 回合计数 + 事件日志（TurnResult 列表）+ 行动队列；Apply 方法：ApplyDamage / ApplyTone / ApplyGurney / ApplyDefense
- `TurnManager`（Flow/）——5 Phase 回合管线（情境更新 → 继承 → 速度重算 → 按序执行 → 回合收束），SAN 阈值行为（<30% 恐慌 C1 / <15% 崩溃 / =0 随机行动）
- `ActionResolver`（Flow/）——Phase 4 声明→响应→结算 dispatch；**事件生产**（DamageCalculator 调用方，csharp-events spec §一 明示落此 step）
- 响应窗口 stub（plan §一 范围表：保留接口 + 注释引用设计章节）
- 不覆盖：空间系统（12 格/控制区/AOE/视线）、逃跑/投降、HP↔SAN 互转、响应窗口 link 交互全文、技能树/LinkState 全量、情境 archetype 选择、NPC Affordance Competition 全量（demo 硬编码 3 基础行动，plan §4.8）

## 数据实测

待 spec 写作期补：已有引擎组件（WcDynamics/ToneUpdater/CstcGating/SpeedScoreCalculator/DamageCalculator/EventProcessor）的接口与调用点；CombatAction/CombatContext/TurnResult 已交付类型；回合战斗流程 §2（双通道）/§3（速度）/§9（CD）正典。

## 追问

待 spec 写作期如遇设计决策冲突提交用户裁决。

## 决策

（待追问）

## 产出

- [ ] spec.md v1.0
- [ ] spec.md 通过审计（workflow 多专家）
- [ ] sign-off.md 获批

## Comments

- 2026-08-14：创建。上游 csharp-events 闭合 ✅（228/228，九航）。

---
*创建: 2026-08-14*
*关联: [plan §五](../../../csharp-engine/design/plan.md), [回合战斗流程](../../../../规则/回合战斗流程.md)*
