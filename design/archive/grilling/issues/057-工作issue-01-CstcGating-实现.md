# #57 工作issue 01: CstcGating 实现

> 状态：关闭 · 创建 2026-08-13 · 关闭 2026-08-13
> 标签：implementation
> 原始：https://github.com/verystrongdog/game/issues/57

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

本地: .scratch/csharp-cstc/impl/issues/01-cstc-gating.md

## 范围

实现 spec v1.1 §三 `CstcGating` 类（构造 + Step + CiRows）+ §四 全部常量 + 偏差 B1-B4 注释逐条对应。声明覆盖 AC：**AC-1 ~ AC-15**（全部）。

## 文件所有权声明

- `src/YouAreNotTheFish.Core/Engine/CstcGating.cs` — 新建
- `src/YouAreNotTheFish.Core.Tests/Engine/CstcGatingTests.cs` — 新建

（创建前 grep 确认无其他进行中 work issue 冲突。）

## 完成标准

spec v1.1 §六 AC-1~AC-15 逐条 ✅ + `dotnet build` 零错误 + `dotnet test` 全绿（既有 100 + 新增全绿）。

## ⚠️ 结转验证（来自 sign-off 结转清单）

| # | 结转项 | 验证结果 |
|---|--------|---------|
| 1 | 迭代固定 300 回合，禁止 max\|Δ\|<1e-7 终止判据（AC-9 f32 极限环 ~3.9e-7 会死循环） | ✅ 引擎 Step 为单回合纯函数，无任何迭代/终止判据逻辑（结构性满足）；测试侧 `Iterate300` 固定 300 回合，AC-9 注释载明 f32 极限环 max\|Δ\|≈3.9e-7 永不达 1e-7 的依据 |
| 2 | DA 混合配对按枚举常量名显式写，禁止按枚举序数建表 | ✅ 引擎三个 StepLoop 调用显式传 `WvtaSomatic/WvtaCognitive/WvtaLimbic` + `CiRows[CstcLoop.X]`；`Loops` 数组按枚举常量名列举；无任何 `(int)CstcLoop` 序数建表 |
| 3 | AC-11 负锚点 −0.4575 哨兵测试必须存在（AC-12 包含性断言不可证伪 clamp） | ✅ `Step_AnalyticConvergence_A2BitwiseEqualsU2`（a2==u2 逐位含 GPi=−0.4575）+ `Step_NoClamp_NegativeGPiPreserved`（u2_GPi<0 显式断言 + Assert.Equal 逐位） |
| 4 | 偏差注释逐条对应 B1/B2/B3/B4；CI 行解析失败抛 KeyNotFoundException | ✅ B1（StepLoop 第 6 步 gate 注释）、B2（Ramp m≤0 分支注释）、B3（decay 常量注释）、B4（构造 XML doc）逐条标注；构造 doc + 代码行注释载明「未命中 → KeyNotFoundException（隐式）」 |

## 实现

- `src/YouAreNotTheFish.Core/Engine/CstcGating.cs` — 按 spec §三/§四 实现（构造 + CiRows + Step + StepLoop + Ramp + 常量），一次成型零修改
- `src/YouAreNotTheFish.Core.Tests/Engine/CstcGatingTests.cs` — AC-1~15 共 15 个测试方法（测试侧 ExpectedLoop/ExpectedU2 镜像 + Iterate300 固定 300 回合 + M1 链重建 + 合成数据防御）

## 代码自审（证据式）

### 门禁证据

- [x] `dotnet build YouAreNotTheFish.sln` 零错误 —— `Build succeeded. 0 Error(s)`（仅 2 个 NU1900 网络警告：nuget.org 不可达，与代码无关）
- [x] `dotnet test YouAreNotTheFish.sln --no-build` 全绿 —— `Passed! - Failed: 0, Passed: 115, Skipped: 0, Total: 115`（既有 100 + 新增 15）

### 验收标准逐条对照

| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | CI 成员资格（fid 级，Q3=B） | ✅ | `Constructor_CI_Membership_MatchesMeasuredFidLists`：三环路 SetEquals §二 2.3 名单 + 计数 3/7/12 + 键集 == {Somatic,Cognitive,Limbic} + 行升序 |
| AC-2 | 空 CI 环路防御（D4） | ✅ | `Constructor_EmptyCILoop_ThrowsInvalidData`：limbic 12 fid 改 CstcRole=None → InvalidDataException 含 "Limbic" |
| AC-3 | Global 环路不校验 | ✅ | `Constructor_GlobalAndNoneLoops_NotCollected`：Global/None 改签后构造成功，被改 fid 不落入任何环路，键集不变 |
| AC-4 | c=0 门控抑制 | ✅ | `Step_CZero_GateSuppressed_ConvergesToAnchor`：首回合镜像对照 + 固定 300 回合 gate=0.8434211（1e-5）+ gate<1 |
| AC-5 | 静息 gate = 1.0（M1 链） | ✅ | `Step_RestingM1Chain_GatesReachOne`：M1 链重建（Build + CorticalBias + WcDynamics ×30）→ gate1=0.635（镜像）、gate2=1.0（1e-5） |
| AC-6 | 静息 c/DA 锚点 | ✅ | `Step_RestingM1Chain_SalienceAnchors`：C=0.665469/0.696963/0.692102、Da=0.48/0.46/0.42（1e-5；锚点源 = csharp-tone M1 附录） |
| AC-7 | 跨环路 fid 归属（D13） | ✅ | `Step_CrossLoopFids_ContributeToRespectiveLoopsOnly`：1/7、2/12、0；1/3、0、1/12（测试侧现算 1f/7f 等） |
| AC-8 | DA 混合逐字段配对（D8） | ✅ | `Step_DAMixing_PairedByFieldName`：VTA=1→0.2/0.4/0.8、SNc=1→0.8/0.6/0.2（字段序 Somatic/Cognitive/Limbic） |
| AC-9 | DA=1 → m_SD2=0（B2） | ✅ | `Step_DAOne_MSD2Zero_NoDivisionError_GateReachesOne`：首回合镜像 + \|a1_SD2\|<1e-5（≈0 非逐位零）+ gate2=1.0 + 固定 300 回合=1.0 |
| AC-10 | DA=0 对称斜率 | ✅ | `Step_DAZero_SymmetricSlopes_ConvergesToAnchor`：首回合镜像 + 固定 300 回合 gate=0.8065790（1e-5） |
| AC-11 | 解析收敛（D9）+ B3 | ✅ | `Step_AnalyticConvergence_A2BitwiseEqualsU2`：a1 镜像（1e-5）+ a2==u2 逐位（Assert.Equal ×15）+ B3 网格复算 ≤5e-11（double） |
| AC-12 | 无 clamp 负值（D11） | ✅ | `Step_NoClamp_NegativeGPiPreserved`：u2_GPi<0 断言 + 逐位相等（哨兵，结转 #3）+ 网格 20 回合值域 [−1.5,2.0]（包含性断言） |
| AC-13 | 输入不可变 + 确定性（C7/C8） | ✅ | `Step_ImmutabilityAndDeterminism`：输入快照不变 + NotSame（输出不共享输入数组）+ 两次调用逐位相等 |
| AC-14 | 契约防御（D4） | ✅ | `Step_ContractDefense_Throws`：3 null → ArgumentNullException；a 长度 {0,68,70}、prev 三环路各 {0,4,6} → ArgumentException |
| AC-15 | gate 输出域 [0,1] | ✅ | `Step_GateDomain_WithinZeroOne`：网格 20 回合全部 gate ∈ [0,1] 有限无 NaN |

### spec §七 自检清单

1. ✅ 数学公式逐项对照——u 五式/DA 混合/ramp 与 spec §三/§四 逐字一致（含 W_SEL_GPe=0.0 项保留、per-population e 表、无 clamp）；测试镜像 ExpectedLoop 与引擎同序
2. ✅ 数值断言全部实测——公式类锚点测试侧 MathF 现算（镜像，不裸写字面量）；300 回合收敛值用 spec 实测字面量（0.8434211/0.8065790/1.0）；AC-6 C 锚点来自 csharp-tone M1 附录实测表
3. ✅ 行序契约明确——构造 fidToRow 镜像 WMatrixBuilder Step 1（canonical = Wsensory.RegionIds）；AC-6 锁定行序
4. ✅ 接口注释先行——构造 + Step XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差标注
5. ✅ 边界值覆盖——c=0 / DA=0 / DA=1（m_SD2=0）/ 负 prev（无 clamp）/ 静息整合 / 空 CI 防御 / 形状防御 / 输出域
6. ✅ 确定性——无 static 可变状态、无 RNG；AC-13 实证逐位相等
7. ✅ 偏差声明完整——B1（StepLoop 第 6 步注释）/B2（Ramp 分支注释）/B3（decay 注释）/B4（构造 doc）逐条对应 + Q1=A/Q3=B 注释
8. ✅ Δ/k 复用漂移注——GurneyK 常量注释 + Step decay 注释显式引用 csharp-wc-dynamics spec §四（Δ=1.0 复用，不重新定义）
9. ✅ 同时更新语义——StepLoop 内 u 全部由 prev 的 O 计算（注释标注「自检清单第 9 项」）；AC-11 锁定

### 发现的问题

| # | 问题 | 处置 |
|---|------|------|
| — | 无。实现一次成型零修改，115/115 首跑全绿；0 spec 缺陷 | — |

## Comments

- 2026-08-13：创建。spec v1.1 经全量审计（退回）→ 修复 → Δ审计（通过）→ 用户 sign-off 批准（1❌+5⚠️+7ℹ️ 全部处置「已修复」，结转清单 4 项）。
- 2026-08-13：实现完成——CstcGating.cs + CstcGatingTests.cs（AC-1~15 共 15 测试）。`dotnet build` 零错误 + `dotnet test` 115/115 全绿（首跑全绿）。证据式自审通过：15 AC 逐条 ✅、§七 自检 9 项 ✅、结转 4 项回填 ✅。Status: resolved。

---
*导出: 2026-09-12 | 来源: GitHub issue*
