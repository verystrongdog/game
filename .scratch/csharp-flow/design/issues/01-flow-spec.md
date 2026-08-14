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

### Q1: Phase 4 行动来源抽象（2026-08-14 用户裁决）

- **A（推荐，✅ 裁决）**：IActionProvider 接口——demo 两个实现（NpcActionProvider 适配 NpcSalience + 玩家实现 step 11 console），引擎零 UI 耦合、测试可注入固定行动
- B：内嵌分支

### Q2: SAN <15% 崩溃档（2026-08-14 用户裁决）

- **A（推荐，✅ 裁决）**：并入恐慌档——数值行为同 <30% 档（T_SAN +0.30），文档化标注，无新状态字段
- B：独立崩溃档

### Q3: 防御持续时间（2026-08-14 用户裁决）

- **A（推荐，✅ 裁决）**：到下次自己窗口——声明 → IsDefending=true + DefendCd=1；下次窗口开始解除 + CD tick（暴露一轮，§9.1 语义）
- B：到 CD 归零

### Q4: Panic 事件生产时机（2026-08-14 用户裁决）

- **A（推荐，✅ 裁决）**：跨越才发——TurnManager 检测 old≥30% ∧ new<30% 生产；EventProcessor C1 guard 为二次校验
- B：每次扣减都发

## 决策

| D# | 决策 | 理由 |
|----|------|------|
| D1 | IActionProvider 接口（Q1=A） | 引擎零 UI 耦合；测试可注入固定行动 |
| D2 | <15% 崩溃并入恐慌档（Q2=A） | demo 无链路可随机触发；文档化标注 |
| D3 | 防御持续到下次自己窗口（Q3=A） | 回合战斗流程 §9.1「跨过完整窗口周期」语义 |
| D4 | Panic 跨越才发（Q4=A） | Entered=true = 真正进入恐慌；C1 guard 双保险 |
| D5 | 链式基准（审计 E8） | 双通道同目标终态正确；resolver 局部游标 |
| D6 | Phase 1 纯衰减步（审计 E9） | events §5.5.3「衰减是 step 10 Phase 1 职责」落地；tone 回基线 |
| D7 | IsOver 实例方法（审计 W4） | 结束判定统一入口；TurnResult 不扩展（B6） |
| D8 | 通道-动作配对校验（审计 W9/W4） | 回合战斗流程 §2.1 通道归属；M1∈{Physical,Defend}、Broca∈{Mental} |
| D9 | T_SAN 判定序 SAN==0 最先（v1.2 Δ审计 F4） | 否则 =0 落入 +0.30 档；正典「思维断裂均匀随机」 |
| D10 | Amygdala 直读（v1.2 Δ审计 F2） | 48 W-active 节点；c_loop_limbic 代理双重计数废弃 |

## 产出

- [ ] spec.md v1.0
- [ ] spec.md 通过审计（workflow 多专家）
- [ ] sign-off.md 获批

## Comments

- 2026-08-14：创建。上游 csharp-events 闭合 ✅（228/228，九航）。

---
*创建: 2026-08-14*
*关联: [plan §五](../../../csharp-engine/design/plan.md), [回合战斗流程](../../../../规则/回合战斗流程.md)*
