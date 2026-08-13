# 工作issue 01: SpeedScoreCalculator + TurnOrderBuilder 实现

> Status: claimed | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.1（含 L1 修正） | Blocked by: sign-off ✅（2026-08-13 批准）

## 范围

实现 spec@v1.1 §二~§三：`SpeedComponents`/`SpeedWeights` 两个 record（Types）+ `SpeedScoreCalculator`（三分量提取 + 逐节点回落 + 加权合成）+ `TurnOrderBuilder.BuildOrder`（排序 + Fisher-Yates 破平）。覆盖 AC-1~AC-15 全部。

## 文件所有权声明

- `src/YouAreNotTheFish.Core/Types/SpeedComponents.cs` — 从 0 字节占位实现（SpeedComponents + SpeedWeights）
- `src/YouAreNotTheFish.Core/Engine/SpeedScoreCalculator.cs` — 新建
- `src/YouAreNotTheFish.Core/Engine/TurnOrderBuilder.cs` — 新建
- `src/YouAreNotTheFish.Core.Tests/Engine/SpeedScoreCalculatorTests.cs` — 新建
- `src/YouAreNotTheFish.Core.Tests/Engine/TurnOrderBuilderTests.cs` — 新建
- `src/YouAreNotTheFish.Core.Tests/Types/SpeedComponentsTests.cs` — 新建（AC-15）

## 完成标准

spec §六 AC-1~AC-15 逐条 ✅ + §七 自检清单 9 项 + sign-off 结转清单 6 项回填。

## 实现

见 commit 记录（小步提交：Types record → SpeedScoreCalculator → TurnOrderBuilder → 测试）。

## Comments

- 2026-08-13：创建。sign-off 已批准（spec@v1.1 含 L1 修正，Δ审计 0❌/0⚠️）。
