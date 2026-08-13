# 工作issue 01: 引擎共享状态类型实现

> Status: claimed | Type: implementation | Spec: ../../design/spec.md@v1.1 | Blocked by: sign-off ✅ (2026-08-13) | GitHub: 待同步

## 问题（这件事要解决什么）

spec v1.1 已批准的 20 个新文件（17 个 Types/ + 2 个 Data/ 补充 + 测试）落地为可编译 C#。这些类型是 step 3-9 全部引擎模块的输入输出契约——不落地，后续 8 个 feature 无法编译。

## 目标

按 spec@v1.1 实现全部类型与接口，`dotnet build` 0 错误 + 测试全绿。

## 指标

- AC-1 ~ AC-10 全部 ✅（含门禁 build/test）
- 每个字段 XML doc 含来源注释（spec §二/§四 来源列 + 设计文档章节）
- 5 项 sign-off 结转中本 feature 范围内的项回填验证

## 范围

引用 spec@v1.1 章节：§二 2.1-2.12（11 类型 + GameData）、§三 接口（IRng/DeterministicRng/LoadAll/CreateDefault/IsValidChannelUsage）、§四 枚举与常量（CalibrationConfig）。覆盖 AC-1~AC-10。

不覆盖：SpeedWeights/SpeedComponents（step 7）、CombatState/TurnManager（step 10）、δ/s 派生逻辑（step 9）、WMatrixBuilder（step 3）——本 issue 只定义 WMatrix 契约类型不实现构建。

## 文件所有权声明

本 issue 独占修改（grep 已确认无其他进行中 work issue 冲突）：

新建 `src/YouAreNotTheFish.Core/Types/`：
- `WcState.cs` — float[69] A，构造防御性拷贝
- `ToneState.cs` — Ne/DaVta/DaSnc/Ht5
- `GurneyState.cs` — Somatic/Cognitive/Limbic float[5]（GurneyPopulation 索引序）
- `GateState.cs` — GateSomatic/GateCognitive/GateLimbic
- `ParticipantState.cs` — 91 浮点嵌套 + Hp/San/IsDefending/CD + CreateDefault
- `CombatAction.cs` — ActionSlot + CombatAction（双通道）+ IsValidChannelUsage
- `CombatContext.cs` — Rng/Data/Calibration 只读上下文
- `WMatrix.cs` — W/Tau/RowFids（契约，不构建）
- `LoopSalience.cs` — LoopValue + Somatic/Cognitive/Limbic
- `TurnResult.cs` — Round/Events/ParticipantSnapshots
- `CombatEvents.cs` — CombatEvent 基类 + Physical/Mental/Heal/StatusChange/LinkGrowth 5 子类
- `Enums.cs` — ActionKind/ChannelOrder/GurneyPopulation/StatusKind
- `IRng.cs` — NextFloat/NextInt
- `DeterministicRng.cs` — splitmix64 [NEW]
- `CalibrationConfig.cs` — instance record + static Default（plan §七 全表）

新建 `src/YouAreNotTheFish.Core/Data/`：
- `GameData.cs` — 5 字段聚合（§2.12 表）

修改 `src/YouAreNotTheFish.Core/Data/`：
- `GameDataLoader.cs` — 新增 `LoadAll(string dataDir)`（不改动现有 5 方法）

新建 `src/YouAreNotTheFish.Core.Tests/`：
- `Types/ParticipantStateTests.cs` — AC-3/AC-5
- `Types/DeterministicRngTests.cs` — AC-6
- `Types/CombatActionTests.cs` — AC-8
- `Types/CalibrationConfigTests.cs` — AC-9
- `Types/WcStateTests.cs` — AC-10（长度 + CreateDefault 等值性）
- `Types/CombatEventsTests.cs` — AC-4（事件构造 + 字段完整性）
- `Data/GameDataLoadAllTests.cs` — AC-7

不碰：`src/YouAreNotTheFish.Core/Types/SpeedComponents.cs`（0 字节占位，step 7）、`src/YouAreNotTheFish.Core.Tests/Data/GameDataLoaderTests.cs`（数据层已交付测试）、任何 csproj（无需新依赖）。

## 完成标准

spec@v1.1 §六 AC-1~AC-10 逐条对照。

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
| # | 结转项 | 验证结果 |
|----|--------|---------|
| 4 | gates=1.0 覆盖时序（本 feature 仅定义初值；消费时序归 step 6/10） | |
| 5 | AC-10 行序对齐由 step 3 承接（本 feature 测试长度+等值性） | |

（结转 1-3 归 step 9，本 issue 不适用——事件类型字段已按 A4/A5/B2 派生需求预留）

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|

## Comments
