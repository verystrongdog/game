# #55 工作issue 01: ToneUpdater + CorticalBias 实现 + M1 里程碑

> 状态：关闭 · 创建 2026-08-13 · 关闭 2026-08-13
> 标签：implementation
> 原始：https://github.com/verystrongdog/game/issues/55

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

本地: .scratch/csharp-tone/impl/issues/01-tone.md

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

commit `8239459`（feat: ToneUpdater + CorticalBias 实现 + M1 里程碑测试）+ `224e56c`（fix: 测试侧两处笔误）。

- `ToneUpdater.cs`：Step = 解析解 + clip（偏差 B1/B2/B3 注释逐条对应），Δ=1.0 常量注释引用 csharp-wc-dynamics spec §四（漂移风险注）
- `CorticalBias.cs`：role 权重 + per-target 唯一（C6，Q1）+ clamp [0,2]（C1 行序 / C2 目标解析 / C3 Silent 拒绝）
- 测试三个类：锚点全部 MathF 现算 / 数据推导，无裸写字面量

## 代码自审（证据式）

### 门禁证据
- [x] `dotnet build` 零错误 —— `0 Error(s)`（commit 8239459 构建输出）
- [x] `dotnet test` 全绿 —— `Passed! - Failed: 0, Passed: 100, Skipped: 0, Total: 100`（前航 76 + 本航新增 24）

### 验收标准逐条对照
| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | 形状与不可变性 | ✅ | Step_ReturnsNewState_AndDoesNotMutateInputs |
| AC-2 | δ=0 回基线衰减 | ✅ | Step_ZeroDelta_DecaysTowardBaseline（不动点逐位 0.3） |
| AC-3 | 单脉冲 4 tone 锚点 | ✅ | Step_SinglePulse_MatchesAnalyticAnchor ×4（Theory） |
| AC-4 | δ_scale 杠杆 + DA 饱和边界 | ✅ | Step_DeltaScaleOne_DemonstratesSaturationBoundary（5HT 0.9866 不 clip；DA_VTA pre-clamp 1.3643 超界 clip 1.0） |
| AC-5 | 大 δ clip [0,1] | ✅ | Step_LargeDelta_ClipsToUnitRange（NE +10→1.0 / 5HT −10→0.0 / 极端扫描有限 ∈[0,1]） |
| AC-6 | back-to-back 双脉冲 | ✅ | Step_BackToBack_MatchesAnalyticSequence（0.5594→0.5945，且 ≠ 聚合一次——D5 语义锁定） |
| AC-7 | 契约防御 | ✅ | Step_NullArguments_Throw + Step_WrongDeltaLength_Throws ×3 |
| AC-8 | 确定性 | ✅ | Step_IsDeterministic（逐位相等） |
| AC-9 | 形状与行序 | ✅ | Compute_ReturnsNew69Array_WithCanonicalRowOrder（首键 AccumbensCore + 行序锚点） |
| AC-10 | per-target 唯一 | ✅ | Compute_BanksSTS_PerTargetUnique（0.4 ≠ per-edge 0.65——Q1 锁定） |
| AC-11 | role 两档 + 排除节点接收 b_j | ✅ | Compute_BaselineTone_StriatalAndAmygdalaAnchors（0.9/0.7/0.45） |
| AC-12 | 零广播节点 | ✅ | Compute_ZeroBroadcastNodes_AreExactlyZero（正典四名逐位 0 + 全零集合数据推导 == 15） |
| AC-13 | clamp [0,2] | ✅ | Compute_AllOnesTone_ClampsToTwo（命中集合 3 fid pre-clamp 2.5 + 边界 10 fid 恰 2.0 数据推导） |
| AC-14 | 基线 b_j 锚点 | ✅ | Compute_BaselineTone_MedialOrbitofrontalAnchor（1.05） |
| AC-15 | M1 静息 trace | ✅ | RestingTrace_30Rounds_ConvergesToMeasuredFixedPoint（maxΔ=0；active 48 ∈ [0.53517413, 0.7712287]；排除三组 14/3/4） |
| AC-16 | 契约防御（E2） | ✅ | Compute_NullArguments_Throw + Compute_UnknownTarget_ThrowsInvalidData（消息含边描述）+ Compute_SilentEdge_ThrowsInvalidData |

### spec §七 自检清单
1. [x] 数学公式逐项对照——解析解与 plan §4.3 逐字一致；b_j 公式与 §5.6 逐字一致；clip [0,1]/[0,2] 来源 §5.2/§7.2
2. [x] 数值断言全部实测——测试锚点全部 MathF 现算或数据推导（写测试前另跑了 python 复算核对 fid 名单归属）
3. [x] 行序契约明确——输出行序 = Wsensory.RegionIds（AC-9 首键断言 + 全测试经 RowOf 推导定位）
4. [x] 接口注释先行——两个 XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差
5. [x] 边界值覆盖——δ=0/正负大 δ/back-to-back/排除节点接收 b_j/零广播/clamp 两向/tone 极值/CorticalBias 契约防御（null/未命中/Silent）
6. [x] 确定性——纯函数无静态状态（AC-8/AC-9 实证）
7. [x] 偏差声明完整——B1（签名加参）/B2（解析解）/B3（值域）/B4（M1 预测修正）实现注释逐条对应
8. [x] Δ=1.0 复用漂移注——ToneUpdater 常量注释显式引用 csharp-wc-dynamics spec §四

### ⚠️ 结转验证（来自 sign-off 结转清单）
无结转项（sign-off 注明「工作issue 实现时直接按 spec v1.1 执行即可」）。

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|
| 1 | ToneUpdaterTests 缺 `using YouAreNotTheFish.Core.Engine;`——首跑编译错误 | 已修（commit 224e56c） |
| 2 | 测试侧 `Expected` 助手含 clamp，AC-4 的「pre-clamp 应超界」断言拿到 clamp 后值 1.0 恒不成立 | 已修（commit 224e56c）：超界断言改用无 clamp 原始公式，注释说明 |
| 3 | 实测中确认 fid→dk 归属存在「名不符实」（FrontalPole/FrontalPoleFPN 属 rostralmiddlefrontal 节点，frontalpole 节点只有 FrontalPoleExtreme）——AC-13/F6 边界 fid 归属无错，但写测试前用 python 复算归属才放心 | 预防性：本 feature 全部测试经 RowOf 数据推导定位，未裸写下标；此坑记录供后续 feature 参考（dk 名 ≠ fid 名前缀） |

## Comments

- 2026-08-13：创建，实现 + 自审完成。M1 实测值表已捕获（69 行，active 48 ∈ [0.53517413, 0.7712287]，maxΔ=0），转入 Task 文档写回（plan §十三-8 + wc-dynamics 结转 #4）。
- 2026-08-13：文档写回完成（运行时状态模型 §4.1/§5.2/§5.5/§7.1/§7.2/§7.3.1、皮层动力学-通用层 §3.3/§4.2/§4.3、回合战斗流程 §3.2/§3.3、决策树 #32 D3/D6/D7 🔧、term_registry v1.6）。M1 实测值表附录如下。

## M1 实测值表（附录，M1RestingTraceTests 输出）

30 回合静息 trace（tone=baseline、s=0、a(0)=0.10）；round 30 vs 29 maxΔ=0；active 48 ∈ [0.53517413, 0.7712287]；排除 21 = σ(b_j) 三组 14/3/4。

| fid | b_j | a(round30) |
|-----|-----|------------|
| AccumbensCore | 0.9000000 | 0.5986876 |
| AccumbensShell | 0.9000000 | 0.5986876 |
| Amygdala | 0.4500000 | 0.6489847 |
| AnteriorCingulateCortex | 0.5500000 | 0.6751733 |
| AnteriorCingulateCortexDorsal | 0.5500000 | 0.6751733 |
| BanksSTS | 0.4000000 | 0.6340001 |
| CaudalMiddleFrontal | 0.6000000 | 0.6827380 |
| Caudate | 0.7000000 | 0.5498340 |
| CerebellumCortex | 0.0000000 | 0.5351741 |
| Cuneus | 0.4000000 | 0.6307744 |
| DorsalRapheNucleus | 0.0000000 | 0.3775407 |
| Entorhinal | 0.4000000 | 0.6358709 |
| FrontalPole | 0.7500000 | 0.7157741 |
| FrontalPoleDMN | 1.0500000 | 0.7712287 |
| FrontalPoleExtreme | 0.6000000 | 0.6880417 |
| FrontalPoleFPN | 0.7500000 | 0.7157741 |
| FrontalPoleSN | 0.5500000 | 0.6751733 |
| Fusiform | 0.4000000 | 0.6339693 |
| HippocampusCA1 | 0.2500000 | 0.6040916 |
| HippocampusCA3 | 0.2500000 | 0.6040916 |
| InferiorParietal | 0.4000000 | 0.6349315 |
| InferiorParietalAngular | 0.4000000 | 0.6349315 |
| InferiorTemporal | 0.4000000 | 0.6350031 |
| Insula | 0.4000000 | 0.6327866 |
| IsthmusCingulate | 0.4000000 | 0.6316203 |
| LateralOccipital | 0.4000000 | 0.6333711 |
| LateralOccipitalOccipitoParietal | 0.4000000 | 0.6333711 |
| LateralOrbitofrontal | 0.8000000 | 0.7200740 |
| Lingual | 0.4000000 | 0.6336310 |
| LocusCoeruleus | 0.0000000 | 0.3775407 |
| LocusCoeruleusRight | 0.0000000 | 0.3775407 |
| MedialOrbitalPrefrontalDMN | 1.0500000 | 0.7712287 |
| MedialOrbitalPrefrontalVMPFC | 1.0500000 | 0.7712287 |
| MedianRapheNucleus | 0.0000000 | 0.3775407 |
| MiddleTemporal | 0.4000000 | 0.6340925 |
| NucleusAccumbens | 0.9000000 | 0.5986876 |
| Pallidum | 0.0000000 | 0.3775407 |
| Paracentral | 0.4000000 | 0.6306826 |
| Parahippocampal | 0.5500000 | 0.6673833 |
| ParsOpercularis | 0.6000000 | 0.6854688 |
| PeriaqueductalGray | 0.0000000 | 0.3775407 |
| Pericalcarine | 0.4000000 | 0.6309757 |
| PontineReticularNucleus | 0.0000000 | 0.3775407 |
| Postcentral | 0.4000000 | 0.6305829 |
| PosteriorCingulate | 0.4000000 | 0.6324062 |
| Precentral | 0.4000000 | 0.6306536 |
| Precuneus | 0.4000000 | 0.6339999 |
| Putamen | 0.7000000 | 0.5498340 |
| RostralAnteriorCingulateCortex | 0.6500000 | 0.6960939 |
| RostralMiddleFrontalDLPFC | 0.7500000 | 0.7157741 |
| StriatumMatrix | 0.7000000 | 0.5498340 |
| SubstantiaNigraParsCompacta | 0.0000000 | 0.3775407 |
| SubstantiaNigraParsCompactaRight | 0.0000000 | 0.3775407 |
| SubthalamicNucleus | 0.0000000 | 0.3775407 |
| SuperiorColliculus | 0.0000000 | 0.3775407 |
| SuperiorFrontal | 0.8500000 | 0.7350714 |
| SuperiorFrontalMPFC | 0.8500000 | 0.7350714 |
| SuperiorParietal | 0.4000000 | 0.6342828 |
| SuperiorTemporal | 0.4000000 | 0.6359175 |
| SuperiorTemporalSulcus | 0.4000000 | 0.6359175 |
| SuperiorTemporalWernicke | 0.4000000 | 0.6359175 |
| Supramarginal | 0.4000000 | 0.6350251 |
| SupramarginalTPJ | 0.4000000 | 0.6350251 |
| TemporalPole | 0.4000000 | 0.6332459 |
| Thalamus | 0.0000000 | 0.3775407 |
| ThalamusPulvinar | 0.0000000 | 0.3775407 |
| TransverseTemporal | 0.4000000 | 0.6316023 |
| VentralStriatum | 0.9000000 | 0.5986876 |
| VentralTegmentalArea | 0.0000000 | 0.3775407 |

---

## 评论（1 条）

### verystrongdog · 2026-08-13

## ✅ 工作issue 01 闭合 (2026-08-13)

- 实现 commit 8239459 + 224e56c：ToneUpdater.cs / CorticalBias.cs + 3 个测试类（24 测试）
- 门禁证据：dotnet build 0 Error；dotnet test Passed 100/100
- AC-1~16 逐条 ✅（自审表见工作issue）
- spec 缺陷：0（实现一次成型）；测试侧笔误 2 处已修
- M1 里程碑：30 回合静息 trace 收敛（maxΔ=0），69 行实测值表已入工作issue 附录
- 文档写回完成：plan §十三-8 Euler 清扫 + wc-dynamics 结转 #4 + 决策树 #32 闭合后修正（D3/D6/D7）

feature csharp-tone 闭合，下一步 step 6 csharp-cstc。

---
*导出: 2026-09-12 | 来源: GitHub issue*
