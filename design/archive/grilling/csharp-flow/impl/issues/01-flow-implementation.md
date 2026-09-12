# 工作issue 01: csharp-flow 实现（CombatState + TurnManager + ActionResolver + NpcSalience）

> Status: resolved | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.2 | Blocked by: sign-off ✅（2026-08-14 批准）

## 范围

实现 [spec v1.2](../../../../../spec/engine/csharp-flow.md) 全部内容，覆盖 AC-1~14：

- `CombatState`（Entity/CombatState.cs 新建）——可变战斗状态 + Create（30 回合静息 trace 初始化）+ Apply 方法族（ApplyDamage/ApplyTone/ApplyGurney/ApplyDefense/TickWindow/AccumulateS/ApplyEvents）+ AddTurnResult
- `TurnManager`（Flow/TurnManager.cs 新建）——五阶段管线 StepRound + IsOver
- `ActionResolver`（Flow/ActionResolver.cs 新建）——事件生产（链式基准 + miss 契约 + 通道配对校验）
- `IActionProvider`（Flow/IActionProvider.cs）+ `NpcActionProvider`（Flow/NpcActionProvider.cs）——行动来源抽象 + demo 适配
- `IResponseResolver` + `NoopResponseResolver`（Flow/）——响应窗口 stub
- `NpcSalience`（Engine/NpcSalience.cs 新建）——3 行动 salience 竞争（Softmax + T_SAN）
- `CalibrationConfig` +MaxRounds=50 [NEW]——L2 类型变更（AC-14 回执）
- 结转清单 6 项验证（sign-off 结转表 #1-#6）

## 文件所有权声明

- `code/src/YouAreNotTheFish.Core/Entity/CombatState.cs` — 新建
- `code/src/YouAreNotTheFish.Core/Flow/TurnManager.cs`、`ActionResolver.cs`、`IActionProvider.cs`、`NpcActionProvider.cs`、`IResponseResolver.cs`、`NoopResponseResolver.cs` — 新建
- `code/src/YouAreNotTheFish.Core/Engine/NpcSalience.cs` — 新建
- `code/src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` — 修改（MaxRounds=50）
- `code/src/YouAreNotTheFish.Core.Tests/Flow/TurnManagerTests.cs`、`ActionResolverTests.cs`、`NpcSalienceTests.cs`、`CombatStateTests.cs` — 新建（AC-1~14）
- `../../../../规格/引擎/csharp-engine-types.md` — 变更日志补 🔧 修正行（结转 #1）

grep 检查：其他进行中 work issue 无上述文件所有权。

## 完成标准

spec §六 AC-1~14 逐条对照 + spec §七 自检清单 9 项 + sign-off 结转清单 6 项。

## 实现

提交（4 批，按 CLAUDE.md 小步提交）：

| commit | 类型 | 内容 |
|--------|------|------|
| （step 10 实现批 1） | feat | CalibrationConfig +MaxRounds + CombatState（Entity/）+ Flow 接口族（IActionProvider/IResponseResolver/NoopResponseResolver）+ NpcSalience（Engine/）+ NpcActionProvider + ActionResolver + TurnManager |
| （实现批 2） | feat | 测试 AC-1~14（33 项：CombatStateTests 6 + ActionResolverTests 10 + NpcSalienceTests 4 + TurnManagerTests 13）+ types spec 🔧 行（结转 #1） |

实现按 spec §三 3.5 伪码逐字落地。**实现期发现并修复 2 个实现级 bug**（非 spec 缺陷）：
1. 链式游标初始化为攻击者状态（应为 per-target）——TargetHpBefore 错取攻击者 HP；修复为 per-target 游标数组
2. Downed 检测只查行动者自己（应查结算后任一被击杀参与者）——被他人击杀的目标不产 Downed；修复为全参与者扫描

## 代码自审（证据式）

### 门禁证据
- [x] `dotnet build` 零错误 —— Core 项目 `Build succeeded. 0 Warning(s) 0 Error(s)`
- [x] `dotnet test` 全绿 —— `Passed! - Failed: 0, Passed: 261, Skipped: 0, Total: 261`（既有 228 + 新增 33；net8.0）

### 验收标准逐条对照
| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | CombatState 创建 + 静息初始化 | ✅ | `Create_WcIsRestingFixedPoint`（active 48 ∈ [0.535, 0.771] M1 实测 + 排除节点 σ(b_j) 三组 + tone/SPending/Teams/Round/History 结构）/ `Create_TeamsMismatch_Throws` / `Create_NullArgs_ThrowArgumentNull` |
| AC-2 | Phase 1 情境更新 | ✅ | `ZeroEventRound_Phase1Chain_ToneDecayBaseline`（a 稳定 + salience 更新 + SPending 全零 + tone 衰减恒等）/ `ZeroEventRound_ToneDecaysTowardBaseline_FromInjected`（非 baseline 严格靠近——Δ-05 两行） |
| AC-3 | Phase 3 速度重算 | ✅ | `SpeedOrder_Deterministic_WithSameSeed`（同种子深度一致——record 数组引用比较规避） |
| AC-4 | 物理攻击完整链 | ✅ | `PhysicalAttack_FullChain`（事件字段/搬运/tone A1+B1/s[Postcentral]）/ `PhysicalHit_EventFields_Filled`（契约恒等）/ `PhysicalMiss_Contract_Dealt0_BlockedIncoming`（E2 锚点：200 种子找 miss 实例） |
| AC-5 | 精神攻击完整链 | ✅ | `MentalAttack_FullChain_WithPanicEvent`（sanDamage=0.6 探针实测锚点 + Panic 同批）/ `MentalAttack_EventFields_Filled` / `Mental_NoRngConsumed_AlwaysHits` |
| AC-6 | 防御生命周期 | ✅ | `DefendLifecycle_NextOwnWindow_Resets`（Q3=A）/ `DefendingTarget_PhysicalHalved`（同种子 0.5 减半 + B4 blocked=dealt）/ `DualChannel_SameTarget_ChainedCursor`（E8 链式：mental.Before == physical.After） |
| AC-7 | Panic 跨越生产 | ✅ | `MentalAttack_FullChain_WithPanicEvent`（18.5→17.9 跨 18；SanMax=60 正确构造——初版误用 80/24 已修正）/ 未跨越路径由 guard 测试覆盖（events 层） |
| AC-8 | Downed 生产 + 队列移除 | ✅ | `Downed_QueueRemoval_SurvivorsSkipWindows`（击杀 → Downed + D2 广播 + 下回合 Hp=0 跳过窗口） |
| AC-9 | 结束条件 | ✅ | `IsOver_TeamDefeated`（Hp≤0 / San≤0 双口径 + null 契约）/ `IsOver_MaxRounds`（上限 3） |
| AC-10 | TurnResult 打包 | ✅ | `TurnResult_RoundEventsHistory`（Round/History/快照） |
| AC-11 | NpcSalience | ✅ | `Target_FirstEnemyTeam` / `Action_IsOneOfThreeBasics_WithChannelMapping`（通道映射）/ `Determinism_SameSeedSameAction` / `SanZero_UniformRandom_DifferentSeedsDiffer`（SAN==0 判定序最先） |
| AC-12 | 确定性 | ✅ | `Determinism_FullBattle_SameSeedIdentical`（完整战斗深度逐位） |
| AC-13 | 异常契约 | ✅ | `NullArgs_Throw`（TurnManager/ActionResolver）+ `ChannelPairing_Invalid_Throws`（W9 配对）+ 越界 |
| AC-14 | MaxRounds 回执 | ✅ | `MaxRounds_Default50`；现有 types 测试零改动在 261/261 通过；types spec 🔧 行 |

### spec §七 自检清单

1. [x] **数学公式逐项对照**——salience/tone_bias/T_SAN 对照 NPC AI §3.2-3.4（注释标注）；接线对照 plan §六；fid 解析对照数据层双射
2. [x] **数值断言全部实测**——静息不动点（M1 实测）、sanDamage=0.6（探针实测）、miss 完整伤害（damage calc AC-5）；测试未凭记忆写锚点
3. [x] **计算顺序契约明确**——五阶段伪码逐字落地；链式游标 per-target；Panic 快照收集同批一次 Step；Downed 全参与者扫描
4. [x] **接口注释先行**——全部新类 XML doc 含职责/输入/输出/异常/来源
5. [x] **边界值覆盖**——SAN 跨越双端、防御 CD 生命周期、HP=0 队列、回合上限、空声明、SAN=0 均匀随机、miss 契约
6. [x] **确定性**——无 static 可变状态（NpcSalience 每调用解析行号）；AC-12 实证
7. [x] **偏差声明完整**——B1-B12 实现对应（NpcSalience 硬编码/单目标/防御连续/blocked=dealt/响应 stub/IsOver/TurnResult 不扩展/静息 trace/SAN=0 口径/baseline 常量/逐事件 Panic/配对校验/节点取值）
8. [x] **常量复用漂移注**——BasePhysicalDamage/BaseMentalDamage/EndurancePassivePenalty/MaxRounds 消费；TBase/PerceptionThreshold/M1SustainPenalty 不重定义；baseline 常量 (0.3,0.4,0.5,0.5) 声明
9. [x] **类型变更声明完整**——MaxRounds（AC-14 回执 + types spec 🔧 行）；TurnResult 不扩展（B6）

### ⚠️ 结转验证（来自 sign-off 结转清单）
| # | 结转项 | 验证结果 |
|----|--------|---------|
| 1 | types spec 🔧 修正行（MaxRounds） | ✅ commit 实现批 2——v1.1 追加 L2 语义行指向 csharp-flow spec §四 |
| 2 | AC-14 回执 | ✅ `MaxRounds_Default50` + 261/261 零改动 |
| 3 | 全部 AC 锚点写测试（不凭记忆） | ✅ 33 项锚点来源标注（M1 实测/探针/组件级） |
| 4 | 静息初始化 trace 与 M1 一致 | ✅ AC-1（active 48 节点区间逐位核对） |
| 5 | 伪码逐字遵循 | ✅ 实现对照伪码；2 个实现级 bug 已修复并记录 |
| 6 | 回合末 tone 数值锚点探针 | ✅ AC-2 两行（baseline 恒等 + 非 baseline 严格靠近——注入 0.9 衰减后严格缩小）；events 锚点注入瞬间值声明在实现注释 |

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|
| 1 | 链式游标初始化对象错误（攻击者 vs 目标）——TargetHpBefore 错值 | 修复为 per-target 游标数组（实现级，spec §3.3 链式基准语义未变） |
| 2 | Downed 检测只查行动者自己——被他人击杀不产 Downed | 修复为全参与者扫描（实现级，spec §5.5 D 注语义未变） |
| 3 | 测试初版 SAN 跨越构造误用 SanMax=80（p1 实为 60） | 修正构造（18.5→17.9 跨 18）——测试设计错误非实现缺陷 |

## Comments

- 2026-08-14：创建。sign-off ✅（dog，2026-08-14）。spec v1.2（审计链：v1.0 全量 45 CONFIRMED → v1.1 → Δ 20 CONFIRMED → v1.2 → 终审 PASS）。
- 2026-08-14：实现完成——261/261 全绿（新增 33），AC-1~14 逐条 ✅，§七 9 项全勾，结转 6 项全部回填，2 个实现级 bug 修复记录。

---
*创建: 2026-08-14 | 更新: 2026-08-14*
*关联: [spec v1.2](../../../../../spec/engine/csharp-flow.md), [sign-off](../../design/audit/sign-off.md)*
