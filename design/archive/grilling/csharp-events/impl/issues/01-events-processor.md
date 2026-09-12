# 工作issue 01: EventProcessor 实现 + L2 类型变更

> Status: resolved | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.2.2 | Blocked by: sign-off ✅（2026-08-14 批准）

## 范围

实现 [spec v1.2.2](../../../../../spec/engine/csharp-events.md) 全部内容，覆盖 AC-1~15：

- `EventProcessor`（Engine/EventProcessor.cs 新建）——ProcessEvents：δ 派生（A1/A2/A4/A5/B1/B2/B4/C1/D1/D2）+ Σ 聚合一次 Step + s 打包
- `EventProcessingResult`（Types/EventProcessingResult.cs 新建）
- `StatusChangeEvent` +3 float 字段（SanBefore/SanAfter/SanMax）——L2 跨 feature 类型变更（Q1=A）
- `CalibrationConfig` +EndurancePassivePenalty=1 [NEW]
- 结转清单 6 项验证（sign-off 结转表 #1-#6）

## 文件所有权声明

- `code/src/YouAreNotTheFish.Core/Engine/EventProcessor.cs` — 新建
- `code/src/YouAreNotTheFish.Core/Types/EventProcessingResult.cs` — 新建
- `code/src/YouAreNotTheFish.Core/Types/CombatEvents.cs` — 修改（StatusChangeEvent +3 float 字段）
- `code/src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` — 修改（EndurancePassivePenalty=1）
- `code/src/YouAreNotTheFish.Core.Tests/Engine/EventProcessorTests.cs` — 新建（AC-1~15）
- `../../../../规格/引擎/csharp-engine-types.md` — 变更日志补 🔧 修正行（结转 #1）

grep 检查：其他进行中 work issue 无上述文件所有权（全部 prior issue 已 resolved）。

## 完成标准

spec §六 AC-1~15 逐条对照 + spec §七 自检清单 9 项 + sign-off 结转清单 6 项。

## 实现

提交（4 批，按 CLAUDE.md 小步提交）：

| commit | 类型 | 内容 |
|--------|------|------|
| 3bc3b01 | feat | L2 类型变更：StatusChangeEvent +3 float 字段 + CalibrationConfig.EndurancePassivePenalty + EventProcessingResult |
| 9caef4e | feat | Engine/EventProcessor.cs（240 行） |
| 79e8716 | test | Tests/Engine/EventProcessorTests.cs（50 项 AC-1~15）+ types spec 🔧 行（结转 #1） |

实现按 spec §三 3.2 伪码 + §五 全部规则逐字落地，一次成型零 spec 缺陷（唯一首跑修正：测试 unused 参数 warning 清扫——工程细节非 spec 缺陷）。

## 代码自审（证据式）

### 门禁证据
- [x] `dotnet build` 零错误零警告 —— 输出：`Build succeeded. 0 Warning(s) 0 Error(s)`（Core）；测试项目仅 pre-existing NU1900（离线环境）
- [x] `dotnet test` 全绿 —— 输出：`Passed! - Failed: 0, Passed: 228, Skipped: 0, Total: 228`（既有 178 + 新增 50；net8.0）

### 验收标准逐条对照
| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | 构造与参数验证 | ✅ | `Ctor_NullArgs_ThrowArgumentNull` / `ProcessEvents_NullArgs_ThrowArgumentNull` / `ProcessEvents_TeamsMismatch_Throws` / `ProcessEvents_OutOfRangeId_Throws`（4 组合） |
| AC-2 | 物理命中无防御 A1+B1 | ✅ | `PhysicalHit_NoDefense_A1AndB1`（攻击者 0.68929785/0.71404856 + 承受者 0.3864665/0.4513417 + s[Postcentral] 1.0/0.6666667 逐位） |
| AC-3 | 三路分区 Q2=A | ✅ | `DefendedHit_TargetReceivesOnlyA5`（仅 5HT 0.57298744，NE/VTA/SNc 与基线逐位相同——无 B1 混入）/ `Miss_ReceiverGetsB2_NotB1`（0.6459749） |
| AC-4 | A2 miss：δ 跳过、s 恒发 | ✅ | `Miss_AttackerToneUnchanged_ButSStillSent`（tone 与输入逐位相同 + s[Postcentral]=1.0） |
| AC-5 | A4 + B4 | ✅ | `MentalAttack_A4_ExpectedFormula` / `MentalAttack_PenetrationM13_E1Fixed`（mot=0.5 → m=1.3 → 0.77608716，E1 修正锚）/ `MentalAttack_NegativeMotivation_DeltaSkipped_SStillSent`（mot=−1 m<0 + mot=−0.5 m=+∞ 双路径）/ `MentalB4_SanDrop_ToneAnchor`（0.30864665/0.49513417）/ `MentalAttack_Mot025_Expected15_ExpressionAnchor` |
| AC-6 | C1 guard 全条件 | ✅ | `Panic_Crosses30_SendsC1` / `Panic_GuardFails_NoC1`（new=18 严格 / ΔSAN=0 / 治疗 3 态）/ `Panic_OldInclusive18_Sends`（含端）/ `Panic_EnteredFalse_NoC1` |
| AC-7 | D1/D2 广播 | ✅ | `Downed_Broadcasts_D1ToTeammate_D2ToEnemy`（teams=[1,1,2]，E2 修正）/ `Downed_DeadObserver_Excluded` / `Downed_EnteredFalse_NoBroadcast` / `MultiDowned_ObserverAccumulatesD2x2`（P6）/ `MultiDowned_TeammateObserverGetsD1x2`（4 人 [1,1,1,2]，P7） |
| AC-8 | m<0.01 skip 双通道 | ✅ | `SmallM_BelowThreshold_ToneUnchanged_SZero`（0.008333334，I-3）/ `B1_ThresholdBoundary`（0.01f 逐位发 / 0.005 不发）/ `NaN_Infinity_ByEventClass`（A1 NaN s 发 / A5 +∞ s 发——v1.2 修正 / B2 NaN 双通道 skip——W-k） |
| AC-9 | Σ 聚合后单次 Step | ✅ | `Summation_B1PlusB4_SingleStep`（0.39511314）/ `Summation_A1PlusA4_SingleStep`（0.9785956/0.71404856）/ `Summation_C1PlusB1_SingleStep_WithSAssertion`（0.6458659 + s[Postcentral]=1.6666667——W-f）/ `Summation_B1x2_SigmaThenSingleStep_E3Fixed`（0.47293293，E3 修正锚，probe P1） |
| AC-10 | s 打包 | ✅ | `Sensory_A1_15Rows_Postcentral1` / `Sensory_B2_SameAsA1Pattern`（W-f 补行）/ `Sensory_D1_26Rows_DualModal2`（SuperiorTemporal=2.0）/ `Sensory_B1_20Rows_And_Max` / `Sensory_A5_MAlpha1_FourRows`（W-c：m_α=1.0 → 1.0 非 0.5）/ `Sensory_ZeroRowSentinel_AmygdalaIsZero` |
| AC-11 | Heal/LinkGrowth no-op | ✅ | `HealAndLinkGrowth_PureBatch_AllZero`（W-i ①）/ `Heal_MixedBatch_NoInterference`（W-i ② A1 照发） |
| AC-12 | 确定性 + 输入不可变 | ✅ | `Determinism_SameInput_BitwiseIdentical`（5 次逐位）/ `Inputs_NotMutated_OutputsNewReferences`（tone 不变 + 新引用/引用语义） |
| AC-13 | L2 类型变更回执 | ✅ | `StatusChangeEvent_NewFields_RoundTripBitwise`（5.6f 存读回逐位）/ `CalibrationConfig_EndurancePassivePenalty_IsOne`；现有 types 测试零改动在全量 228/228 通过 |
| AC-14 | 空事件列表 | ✅ | `EmptyEvents_StatesCopy_SensoryZero` |
| AC-15 | 击杀窗口 | ✅ | `KillWindow_DownedReceiverStillGetsB1`（p0 收 B1 m=1.0 → 0.5593994/0.35402513 + s[Postcentral]=2.0 + 20 行——probe Q1-Q4；p0 不另收 D；p2 收 D2） |

### spec §七 自检清单

1. [x] **数学公式逐项对照**——实现注释逐项标注（§5.3.1-5.3.5 m 公式 + §5.2 pattern 表逐字落地；A5 两通道 magnitude 独立（W-c）；三路分区（Q2=A）；C1 guard 全条件；D1/D2 观察者判定）
2. [x] **数值断言全部实测**——全部锚点来自任务issue 01 实测表 + probe-v1.1.md P1-P13 + probe-v1.2.md Q1-Q4 + 审计 numpy 复现（report §四）；测试未凭记忆写任何锚点
3. [x] **计算顺序契约明确**——Σ 事件序 → 一次 Step（B1×2 哨兵在 AC-9）；s 模态升序 k、节点升序 j、跨事件累加；m 公式逐式 f32 序（先乘后减）
4. [x] **接口注释先行**——类头 + 构造 + ProcessEvents + EventProcessingResult XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差标注（B1-B5）
5. [x] **边界值覆盖**——C1 双端（old=18 含端/new=18 严格）、m=0.01 逐位/0.005 跳过、NaN/∞ 按事件类、空列表、越界索引、Entered=false、倒者排除、击杀窗口（AC-15）
6. [x] **确定性**——无 static 可变状态；参与者升序；AC-12 实证逐位相等
7. [x] **偏差声明完整**——B1（A3/B3/A6/A7 不落地 + A6 顺延）/B2（A2 m 恒 0——理由改写 I-2）/B3（全参与者副本）/B4（∞ 防御）/B5（A4 expected ≤0）在实现注释逐条对应
8. [x] **常量复用漂移注**——EndurancePassivePenalty 唯一新常量（来源 基础行动设计 §四）；ExpectedDamage/BaseMentalDamage 消费（W-a/W-b）；δ_scale/τ/baseline 不重定义（ToneUpdater 内部）
9. [x] **类型变更声明完整**——StatusChangeEvent 3 字段对照 §二 2.1 表逐字段；AC-13 回执（228/228 零改动）；types spec 变更日志 🔧 行已提交（79e8716）

### ⚠️ 结转验证（来自 sign-off 结转清单）
| # | 结转项 | 验证结果 |
|----|--------|---------|
| 1 | types spec 变更日志 🔧 修正行 | ✅ commit 79e8716——v1.1 追加 L2 语义行，指向 csharp-events spec §二 2.1（StatusChangeEvent 3 字段 + EndurancePassivePenalty） |
| 2 | AC-13 回执（现有 types 测试零改动 + 新字段存读回逐位） | ✅ 228/228 全绿（含既有 178 零改动）；`StatusChangeEvent_NewFields_RoundTripBitwise` 5.6f 存读回逐位 |
| 3 | 全部 AC 锚点写测试（不凭记忆） | ✅ 50 项全部锚点来源标注在类头 + 测试注释（探针/实测/审计复现） |
| 4 | 零向量不调用 Step + Σ 一次 Step | ✅ `Miss_AttackerToneUnchanged_ButSStillSent`（A2）+ `Summation_B1x2_SigmaThenSingleStep_E3Fixed`（哨兵） |
| 5 | AC-15 击杀窗口 + AC-8 A5 +∞ s 照发 | ✅ `KillWindow_DownedReceiverStillGetsB1`（防误加存活守卫）+ `NaN_Infinity_ByEventClass`（A5 侧，防 W-k 复发） |
| 6 | plan §十「A6 sign」测试行顺延 | ✅ 记录于 spec §八 B1（A6 权重表依赖 NPC AI §3.3，skill 系统实装时承接） |

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|
| 1 | 测试首跑 xUnit1026（Theory 未使用参数） | 参数删除——工程细节非 spec 缺陷 |

## Comments

- 2026-08-14：创建。sign-off ✅（dog，2026-08-14）。spec v1.2.2（审计链：v1.0 全量退回 → v1.1 Δ 4 问题 → v1.2 复查 4 问题 → v1.2.2 终审 PASS）。
- 2026-08-14：实现完成——4 批提交（3bc3b01/9caef4e/79e8716），228/228 全绿（新增 50），AC-1~15 逐条 ✅，§七 9 项全勾，结转 6 项全部回填。

---
*创建: 2026-08-14 | 更新: 2026-08-14*
*关联: [spec v1.2.2](../../../../../spec/engine/csharp-events.md), [审计报告](../../design/audit/report.md), [sign-off](../../design/audit/sign-off.md)*
