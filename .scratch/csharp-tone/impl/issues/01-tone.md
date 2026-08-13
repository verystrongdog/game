# 工作issue 01: ToneUpdater + CorticalBias 实现 + M1 里程碑

> Status: claimed | Type: implementation | Spec: ../../design/spec.md@v1.1 | Blocked by: sign-off（✅ 2026-08-13 批准）

## 范围

实现 spec v1.1 全部交付物：

- `ToneUpdater.Step(ToneState, float[], CalibrationConfig) → ToneState`（spec §三 + §四 4.1 私有常量）
- `CorticalBias.Compute(ToneState, GameData) → float[69]`（spec §三 + §四 4.2 常量 + §五 C1-C6）
- M1 静息 trace 里程碑测试（spec §六 AC-15，30 回合组合验证 + 实测值表输出）
- 覆盖 AC：**AC-1~16 全部**

## 文件所有权声明

本 issue 独占修改的文件清单（已 grep 其他进行中 work issue：无冲突；各测试类自带 FindDataDir helper，无需改动共享测试基础设施）：

- `src/YouAreNotTheFish.Core/Engine/ToneUpdater.cs` — 新建
- `src/YouAreNotTheFish.Core/Engine/CorticalBias.cs` — 新建
- `src/YouAreNotTheFish.Core.Tests/Engine/ToneUpdaterTests.cs` — 新建（AC-1~8）
- `src/YouAreNotTheFish.Core.Tests/Engine/CorticalBiasTests.cs` — 新建（AC-9~14, AC-16）
- `src/YouAreNotTheFish.Core.Tests/Engine/M1RestingTraceTests.cs` — 新建（AC-15）

## 完成标准

spec §六 AC-1~16 逐条对照（证据式自审表见下）。

## 实现

<!-- 写代码，提交（遵循 CLAUDE.md 提交规范） -->

## 代码自审（证据式）

### 门禁证据
- [ ] `dotnet build` 零错误 —— [输出粘贴]
- [ ] `dotnet test` 全绿 —— [输出粘贴，含通过数/总数]

### 验收标准逐条对照
| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|

### spec §七 自检清单
<!-- 逐项打勾 -->

### ⚠️ 结转验证（来自 sign-off 结转清单）
无结转项（sign-off 注明「工作issue 实现时直接按 spec v1.1 执行即可」）。

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|

## Comments
