# 工作issue 01: SpeedScoreCalculator + TurnOrderBuilder 实现

> Status: resolved | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.1（含 L1 修正） | Blocked by: sign-off ✅（2026-08-13 批准） | GitHub: [#61](https://github.com/verystrongdog/game/issues/61)

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

小步提交（2026-08-13）：

| commit | 内容 |
|--------|------|
| 3c97605 | feat: SpeedComponents/SpeedWeights 类型实现 |
| 105408d | feat: SpeedScoreCalculator 三成分提取 |
| d0489ce | feat: TurnOrderBuilder 排序 + Fisher-Yates 破平 |
| 95f951c | test: 测试 25 项（AC-1~15） |

## 代码自审（证据式）

### 门禁证据

- [x] `dotnet build` 零错误零警告 —— 输出：`Build succeeded. 0 Warning(s) 0 Error(s)`
- [x] `dotnet test` 全绿 —— 输出：`Passed! - Failed: 0, Passed: 140, Skipped: 0, Total: 140`（既有 115 + 新增 25；仅环境性 NU1900 警告——nuget.org 漏洞数据源不可达，见「发现的问题」）

### 验收标准逐条对照

| AC | 状态 | 证据（测试） |
|----|------|------|
| AC-1 | ✅ | `Constructor_ResolvesFiveRows_MatchesRegionIds`（期望索引从 RegionIds 现算）+ `Constructor_MissingFid_ThrowsKeyNotFound`（合成 GameData 缺 Insula → KeyNotFound 哨兵） |
| AC-2 | ✅ | `Perception_AllAboveThreshold_NoFallback_Mean`（全 0.7 → 0.7）+ `Perception_MixedAboveThreshold_BitEquals0565f`（0.16 置于 ACC 位——f32 结合序陷阱，`Assert.Equal(0.565f, …)` 逐位） |
| AC-3 | ✅ | `Perception_PerNodeFallback_PinsEachConstant`（4 常量逐节点单独钉住）+ `Perception_AllBelowThreshold_AllFallback_RestingMean`（全回落 → 0.64263445）+ `Perception_ExactlyAtThreshold_NoFallback`（端点 0.15 不回落） |
| AC-4 | ✅ | `Decision_MeanOfThreeLoops_NoFallback`（静息锚 0.68484467）+ `Decision_AllZero_NoFallback_Zero` |
| AC-5 | ✅ | `Execution_RestingAnchor_NoDefending`（0.80777383） |
| AC-6 | ✅ | `Execution_Defending_AppliesM1Penalty`（0.80777383 → 0.70777383；false 不变） |
| AC-7 | ✅ | `Score_RedCases_FromPlan`（RED1 0.5 / RED2 0.45 / RED3 1.0） |
| AC-8 | ✅ | `RestingState_ProducesRestingSpeed_NoSpecialCase`（三分量静息 + 等权 speed 0.71175098——B1 无特判） |
| AC-9 | ✅ | `BuildOrder_NoTies_Descending_RngIndependent`（[0,2,1]，两 rng 同结果） |
| AC-10 | ✅ | `BuildOrder_AllTied_MirrorsFisherYates_ConsumptionContract`（独立镜像逐元素相等 + 同种子重复 + 结果 ⊆ 排列） |
| AC-11 | ✅ | `BuildOrder_MixedTieGroups_FixedSeedExact`（端点不动 + 中间 = 镜像 m=2 精确序） |
| AC-12 | ✅ | `ContractDefenses_Throw`（ComputeComponents/ComputeScore 全防御路径）+ `BuildOrder_NullDefenses_Throw` |
| AC-13 | ✅ | `InputsImmutable_OutputDeterministic`（快照不变 + 重复调用逐位相等）+ `BuildOrder_SameSeedRepeated_BitEqual` |
| AC-14 | ✅ | `Boundaries_ExecutionAndDecision`（a_SD1=0 → 0.3；完整输入组合 → 1.5）+ `BuildOrder_EmptyOrSingle_NoRngConsumed`（ThrowingRng 零消费） |
| AC-15 | ✅ | `FromCalibration_DefaultConfig_ThirdWeights`（逐位 1f/3f）+ `FromCalibration_CustomConfig_FieldMapping` + `FromCalibration_Null_Throws` |

### spec §七 自检清单

1. ✅ 数学公式逐项对照：三成分/逐节点回落/加权合成逐字按 spec §三 3.1（B2 mean、B3 a_SD1 代理在实现注释逐条标注）。
2. ✅ 数值断言全部实测：测试锚点全部取自 spec §六（任务issue 01 实测表 + Δ审计独立复算），无凭记忆造数。
3. ✅ 行序契约明确：canonical = RegionIds；AC-1 三面哨兵边界按 spec 承接（名删除 KeyNotFound / 值漂移 AC-3/AC-8 / 行序重排契约中性）。
4. ✅ 接口注释先行：SpeedComponents/SpeedWeights/SpeedScoreCalculator/TurnOrderBuilder XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差标注。
5. ✅ 边界值覆盖：阈值端点 0.15 / 静息 / 全 0 / a_SD1=0 与 2.0 完整输入组合 / 空与单元素 / 全平局 / 混合平局 / FromCalibration。
6. ✅ 确定性：无 static 可变状态；RNG 仅经 IRng 注入；AC-13 实证逐位相等。
7. ✅ 偏差声明完整：B1/B2/B3/B4 在 SpeedScoreCalculator.cs 类注释 + SpeedComponents.cs 注释逐条对应。
8. ✅ 常量复用漂移注：CalibrationConfig 三参数引用不重定义；4 静息常量带「⚠️ 数据漂移注」+ 来源注释（csharp-tone M1 实测值表）。
9. ✅ 破平算法显式：Fisher-Yates 方向/参数/RNG 消费序按 §三 3.2 写死（SpeedScoreCalculator 无 RNG；TurnOrderBuilder 注释声明「实现侧禁改动」）。

### ⚠️ 结转验证（sign-off 结转清单 6 项）

| # | 结转项 | 验证结果 |
|----|--------|---------|
| 1 | 锚点测试统一走行序解析，不裸写下标 | ✅ 全部测试经 `RowOf()`（fid 名 → RegionIds 现算行号）；5 解析名均按 fid 名查，零裸写下标 |
| 2 | gurney.Somatic 长度防御对照 CstcGating | ✅ 异常类型 ArgumentException + 「长度必须为 5」消息，镜像 CstcGating 防御写法 |
| 3 | AC-10 镜像独立实现（不得复制引擎代码） | ✅ `MirrorShuffle` 按 spec §三 3.2 算法文字独立重写（7 行），引擎实现未参考 |
| 4 | RNG 消费序契约实现侧不得改动 | ✅ 实现严格按 §三 3.2（组内升序 → i=m−1 downto 1 → NextInt(i+1)）；AC-10/AC-11/AC-14 三测试实证锁死 |
| 5 | AC-2 不变式 = 与 0.565f 字面量逐位相等 | ✅ `Assert.Equal(0.565f, c.Perception)` 精确相等断言（非 1e-5）；0.16 置于 ACC 位（引擎求和序末位） |
| 6 | 4 静息常量附数据漂移注释 | ✅ SpeedScoreCalculator.cs 常量区带「⚠️ 数据漂移注：脑区数据变更 → M1 实测值变更 → 常量须同步（AC-3 锚点即哨兵）」+ 逐常量 spec §四 来源注释 |

### 发现的问题

| # | 问题 | 处置 |
|----|------|------|
| 1 | L1 spec 补正：spec §三 3.1 接口块未列实现新增的公开访问器 `PerceptionRows`/`PrecentralRow`（AC-1 可测性；镜像 CstcGating.CiRows 公开先例） | 按变更管理回路 L1：直接修 spec 接口块 + 变更日志记 `🔧 修正`，免重审 |
| 2 | `dotnet test` 时 NU1900 警告（nuget.org 漏洞数据源不可达） | 环境性（网络），与代码/spec 无关；不影响构建与测试 |

## Comments

- 2026-08-13：创建。sign-off 已批准（spec@v1.1 含 L1 修正，Δ审计 0❌/0⚠️）。
- 2026-08-13：实现完成，140/140 全绿，自审通过 → resolved。
