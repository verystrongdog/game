# 工作issue 01: DamageCalculator 实现 + L2 类型变更

> Status: claimed | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.1 | Blocked by: sign-off ✅（2026-08-13 批准）

## 范围

实现 [spec v1.1](../../design/spec.md) 全部内容，覆盖 AC-1~18：

- `DamageCalculator`（Engine/DamageCalculator.cs 新建）——CalcPhysicalDamage / CalcMentalDamage / Round1 / Floor1
- CalibrationConfig 新增 12 伤害常量 [NEW] + 4 demo 模板常量 int→float
- L2 跨 feature 类型变更 22 字段 int→float（§二 2.2 清单）
- 结转清单 5 项验证（sign-off 结转表 #1-#5）

## 文件所有权声明

- `src/YouAreNotTheFish.Core/Engine/DamageCalculator.cs` — 新建
- `src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` — 修改（12 常量 + 4 模板 int→float）
- `src/YouAreNotTheFish.Core/Types/ParticipantState.cs` — 修改（Hp/HpMax/San/SanMax int→float + CreateDefault(float,float)）
- `src/YouAreNotTheFish.Core/Types/CombatEvents.cs` — 修改（PhysicalDamageEvent 6 + MentalDamageEvent 8 int→float）
- `src/YouAreNotTheFish.Core.Tests/Engine/DamageCalculatorTests.cs` — 新建（AC-1~17）
- `src/YouAreNotTheFish.Core.Tests/Types/ParticipantStateTests.cs` / `CombatEventsTests.cs` — 验证（不改断言值，AC-18 回执）
- `.scratch/csharp-engine-types/design/spec.md` — 变更日志补 🔧 修正行（结转 #1）

grep 检查：其他进行中 work issue 无上述文件所有权（全部 prior issue 已 resolved）。

## 完成标准

spec §六 AC-1~18 逐条对照 + spec §七 自检清单 9 项 + sign-off 结转清单 5 项。

## 实现

<!-- 写代码，提交（遵循 CLAUDE.md 提交规范） -->

## 代码自审（证据式）

### 门禁证据
- [ ] `dotnet build` 零错误
- [ ] `dotnet test` 全绿

### 验收标准逐条对照
| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|

### spec §七 自检清单
<!-- 逐项打勾 -->

### ⚠️ 结转验证（来自 sign-off 结转清单）
| # | 结转项 | 验证结果 |
|----|--------|---------|

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|

## Comments

- 2026-08-13：创建。sign-off ✅（dog，2026-08-13）。spec v1.1（全量审计退回修复 + Δ审计通过 + 残差清扫 cb129c1）。
