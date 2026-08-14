# 工作issue 01: csharp-flow 实现（CombatState + TurnManager + ActionResolver + NpcSalience）

> Status: claimed | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.2 | Blocked by: sign-off ✅（2026-08-14 批准）

## 范围

实现 [spec v1.2](../../design/spec.md) 全部内容，覆盖 AC-1~14：

- `CombatState`（Entity/CombatState.cs 新建）——可变战斗状态 + Create（30 回合静息 trace 初始化）+ Apply 方法族（ApplyDamage/ApplyTone/ApplyGurney/ApplyDefense/TickWindow/AccumulateS/ApplyEvents）+ AddTurnResult
- `TurnManager`（Flow/TurnManager.cs 新建）——五阶段管线 StepRound + IsOver
- `ActionResolver`（Flow/ActionResolver.cs 新建）——事件生产（链式基准 + miss 契约 + 通道配对校验）
- `IActionProvider`（Flow/IActionProvider.cs）+ `NpcActionProvider`（Flow/NpcActionProvider.cs）——行动来源抽象 + demo 适配
- `IResponseResolver` + `NoopResponseResolver`（Flow/）——响应窗口 stub
- `NpcSalience`（Engine/NpcSalience.cs 新建）——3 行动 salience 竞争（Softmax + T_SAN）
- `CalibrationConfig` +MaxRounds=50 [NEW]——L2 类型变更（AC-14 回执）
- 结转清单 6 项验证（sign-off 结转表 #1-#6）

## 文件所有权声明

- `src/YouAreNotTheFish.Core/Entity/CombatState.cs` — 新建
- `src/YouAreNotTheFish.Core/Flow/TurnManager.cs`、`ActionResolver.cs`、`IActionProvider.cs`、`NpcActionProvider.cs`、`IResponseResolver.cs`、`NoopResponseResolver.cs` — 新建
- `src/YouAreNotTheFish.Core/Engine/NpcSalience.cs` — 新建
- `src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` — 修改（MaxRounds=50）
- `src/YouAreNotTheFish.Core.Tests/Flow/TurnManagerTests.cs`、`ActionResolverTests.cs`、`NpcSalienceTests.cs`、`CombatStateTests.cs` — 新建（AC-1~14）
- `.scratch/csharp-engine-types/design/spec.md` — 变更日志补 🔧 修正行（结转 #1）

grep 检查：其他进行中 work issue 无上述文件所有权。

## 完成标准

spec §六 AC-1~14 逐条对照 + spec §七 自检清单 9 项 + sign-off 结转清单 6 项。

## 实现

提交分批（按 CLAUDE.md 小步提交），待实现后回填。

## 代码自审（证据式）

待实现后回填：门禁证据 / 验收标准逐条对照 / §七 自检清单 / 结转验证 / 发现的问题。

---
*创建: 2026-08-14*
*关联: [spec v1.2](../../design/spec.md), [sign-off](../../design/audit/sign-off.md)*
