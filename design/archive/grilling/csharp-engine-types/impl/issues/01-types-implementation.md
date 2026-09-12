# 工作issue 01: 引擎共享状态类型实现

> Status: resolved | Type: implementation | Spec: ../../design/spec.md@v1.1 | Blocked by: sign-off ✅ (2026-08-13) | GitHub: [#46](https://github.com/verystrongdog/game/issues/46)

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

提交记录：
- `07c729b` feat: Types/ 15 文件 + Data/GameData + LoadAll（spec@v1.1 实现）
- `ef65535` test: 7 个测试文件 26 测试（AC-3~AC-10）
- `2d74f2f` fix: .gitignore 修复（实现中发现，见下「发现的问题」）

## 代码自审（证据式）

### 门禁证据
- [x] `dotnet build` 零错误 —— `Build succeeded. 0 Warning(s) 0 Error(s)`（YouAreNotTheFish.Core；测试项目编译时曾出现 2 个 CS0184 测试警告，已修复后重跑 0 警告）
- [x] `dotnet test` 全绿 —— `Passed! - Failed: 0, Passed: 50, Skipped: 0, Total: 50`（24 数据层既有 + 26 本 issue 新增）
- 注：`NU1900`（nuget 漏洞数据源不可达）为离线环境网络警告，非代码问题

### 验收标准逐条对照
| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | 全部类型编译 0 错误 | ✅ | build 输出 0 Error |
| AC-2 | 每个字段 XML doc 含来源注释 | ✅ | 全部新文件逐属性 XML doc 含来源（plan §/设计文档章节）；审计逐字段核查通过 |
| AC-3 | 91 浮点组成 69+4+15+3 | ✅ | ParticipantStateTests.Composes91Floats |
| AC-4 | 4 事件类型字段覆盖 §5.5 m 公式 + §九 console | ✅ | CombatEventsTests 6 测试构造 5 类事件全字段 |
| AC-5 | CreateDefault 初始化值（含 gates=1.0 推导） | ✅ | ParticipantStateTests.CreateDefault_SetsDocumentedInitialValues + _SetsCombatFields |
| AC-6 | DeterministicRng 同种子同序列 / NextInt 值域 | ✅ | DeterministicRngTests 5 测试（100 值对拍 + 值域 + 异常） |
| AC-7 | LoadAll 5 文件与单文件方法一致 | ✅ | GameDataLoadAllTests 3 测试（逐结构属性对照） |
| AC-8 | IsValidChannelUsage 双通道约束（真值表） | ✅ | CombatActionTests 3 测试（Defend 独占 M1 / (null,null) / 正常组合） |
| AC-9 | CalibrationConfig.Default 逐常量 = plan §七 | ✅ | CalibrationConfigTests.Default_MatchesPlanSection7Table（13 常量逐断言） |
| AC-10 | WcState.A 长度 69 + 等值性；行序对齐 step 3 承接 | ✅ | WcStateTests 3 测试 + GameDataLoadAllTests.LoadAll_WsensoryRegionIds_IsCanonical69（canonical 源 69 唯一） |

### spec §七 自检清单
- [x] 每个字段来源注释（plan 章节 + 设计文档章节）无遗漏
- [x] 字段命名 vs 文档符号对照（实现字段名 = spec §二 表逐名一致：Wc.A / Tone.Ne/DaVta/DaSnc/Ht5 / Gurney.Somatic/Cognitive/Limbic / Gates.GateSomatic…）
- [x] 值域约束文档化（XML doc），构造不 clamp 的约定写明
- [x] 数组字段防御性拷贝（C7）——WcState/GurneyState/WMatrix 构造克隆 + 测试验证
- [x] 事件类型无重复字段（Physical 13 字段 / Mental 10 字段，差异全进子类）
- [x] 接口注释先行（IRng/工厂/校验方法 XML doc 先行）
- [x] 偏差声明完整：CalibrationConfig instance 化（D3）、splitmix64 [NEW]、事件视角归属（D4）、DamageEvent 不落地
- [x] [NEW] 标注齐全（CalibrationConfig 6 处 + DeterministicRng）
- [x] 行序契约唯一 canonical = RegionIds（C1）；无 BrainRegionsData.Regions 序引用
- [x] DA 混合按字段名配对（LoopSalience XML doc 逐字段公式）

### ⚠️ 结转验证（来自 sign-off 结转清单）
| # | 结转项 | 验证结果 |
|----|--------|---------|
| 4 | gates=1.0 覆盖时序（本 feature 仅定义初值；消费时序归 step 6/10） | ✅ 初值 1.0 已落地并被测试锁定；本 feature 无 gate 消费点，时序约束由 spec@v1.1 §二 2.5 声明（首回合 CstcGating.Step 覆盖） |
| 5 | AC-10 行序对齐由 step 3 承接（本 feature 测试长度+等值性） | ✅ 本 feature 锁定长度 69 + 初值等值性 + canonical 源（RegionIds 69 唯一）；W.RowFids == RegionIds 断言留给 step 3 |

（结转 1-3 归 step 9，本 issue 不适用——事件类型字段已按 A4/A5/B2 派生需求预留：MentalDamageEvent 含动机/门控因子供 expected 重算、PhysicalDamageEvent 含 DamageBlocked 供防御判别）

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|
| 1 | .gitignore 缺陷：Unity 时代规则 `*.csproj`/`*.sln` 误忽略 src/ 下 .NET 源项目文件（csproj/sln 从未入库，fresh clone 无法构建）；`bin/` 未忽略致构建产物被误提交 | 已修复（`2d74f2f`）：规则收窄为根目录 `/*.csproj` `/*.sln` + `[Bb]in/` 入库；csproj/sln 强制入库。流水线建议：提交前 `git status --short` 确认无意外文件 |
| 2 | 上次 session 遗留 10 个 Data 层源文件（BrainEnums.cs 等）未提交 | 已随 `07c729b` 一并入库。教训：写代码后立即 add（CLAUDE.md 已规定） |
| 3 | sync_issues.py 幂等性缺陷：手写 meta 行 `GitHub: #46（…）` 裸 `#` 形式不被解析正则识别（只认 `[#46](link)` 规范形式）→ 每次 sync 都当作新 issue 创建，产生重复 GitHub issue #47/#48/#49 | 已修复：脚本解析/写回正则容忍裸 `#N` 形式；重复 #47/#48/#49 已删除；本 issue 保留 #46 为唯一镜像。meta 行今后一律用 `[#N](url)` 规范形式 |

## Comments

### 关闭总结（2026-08-13）

**结果**: resolved ✅ — 20 个文件（15 Types + GameData + LoadAll 扩展 + 7 测试文件 × 26 测试），`dotnet build` 0 错误 0 警告，`dotnet test` 50/50 全绿。

**AC 覆盖**: AC-1~AC-10 全部 ✅（对照表见「代码自审」段）。

**结转回填**: #4（gates=1.0 初值落地+时序约束声明）✅、#5（行序 canonical 源锁定）✅；#1-3 归 step 9，事件字段已预留。

**发现的问题（3 项，均已处置）**:
1. .gitignore 误忽略 src/ 下 csproj/sln + 未忽略 bin/ → `2d74f2f` 修复（实现阶段提交纪律：add 前 `git status --short`）
2. 上次 session 遗留 10 个 Data 层源文件未提交 → 随 `07c729b` 入库
3. sync_issues.py 对裸 `#N` meta 形式不识别 → 重复 issue #47/#48/#49 已删 + 脚本正则修复（本 issue 唯一镜像 = #46）

**spec 缺陷**: 0 —— 实现与 spec@v1.1 零偏差，无需走变更管理回路。
