# 工作issue 01: WMatrixBuilder 实现

> Status: resolved | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.1 | Blocked by: sign-off ✅ (2026-08-13) | GitHub: [#51](https://github.com/verystrongdog/game/issues/51)

## 问题（这件事要解决什么）

spec v1.1 已批准的 WMatrixBuilder（6 步构建算法）落地为可编译 C#：69×69 归一化权重矩阵 W + τ[69] 时间常数 + RowFids 行序。这是 WC 引擎 Layer 1 的输入——没有它，step 4（WcDynamics）无法编译、运行时状态模型 §四 Layer 1 无法落地。

## 目标

按 spec@v1.1 §二-§六 实现 `WMatrixBuilder.Build` 及 12 条 AC 的全部测试，`dotnet build` 0 错误 + 测试全绿。

## 指标

- AC-1 ~ AC-12 全部 ✅（含门禁 build/test）
- Build XML doc 含职责/输入/输出/异常/来源（spec §三 + plan「设计两次」约束）
- 2 项 sign-off 结转在本 feature 范围内回填验证（#1 AC-7 解析规则 / #2 AC-11 计数推导）

## 范围

引用 spec@v1.1 章节：§二 构建算法（Step 1-6）、§三 接口定义、§四 枚举与常量、§五 交叉引用约束 C1-C9。覆盖 AC-1~AC-12。

不覆盖：WcDynamics（step 4）、脑干 b_j 广播（step 5）、运行时 m/focus 接口（B4 注释预留）、5 处设计文档修正（sign-off 结转 #3，feature 闭合后执行）。

## 文件所有权声明

本 issue 独占修改（grep 已确认无其他进行中 work issue 冲突；src/YouAreNotTheFish.Core/Engine/ 目录存在且为空）：

- `src/YouAreNotTheFish.Core/Engine/WMatrixBuilder.cs` — 新建
- `src/YouAreNotTheFish.Core.Tests/Engine/WMatrixBuilderTests.cs` — 新建

不碰 csproj（Engine/ 与 Engine tests/ 目录随文件自动纳入，无新依赖）。

## 完成标准

spec@v1.1 §六 AC-1 ~ AC-12 逐条对照（见「代码自审」段）。

## 实现

- `e27292e` feat: WMatrixBuilder 6 步构建算法 + AC-1~12 测试（spec@v1.1，12/12 绿）

## 代码自审（证据式）

### 门禁证据
- [x] `dotnet build` 零错误 —— `Build succeeded. 0 Warning(s) 0 Error(s)`（`src/YouAreNotTheFish.Core.csproj`）
- [x] `dotnet test` 全绿 —— `Passed! - Failed: 0, Passed: 62, Skipped: 0, Total: 62`（其中 WMatrixBuilderTests 12/12）

### 验收标准逐条对照
| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | W 69×69 / Tau 69 / RowFids 69 | ✅ | `Build_Returns69Shapes` |
| AC-2 | RowFids == RegionIds；与 GraphNodes fids 双射 | ✅ | `RowFids_EqualsRegionIdsAndBijectiveWithGraphFids` |
| AC-3 | 21 排除 fid 行列全 0 | ✅ | `ExcludedFids_HaveZeroRowsAndColumns`（21 计数由数据推导并断言） |
| AC-4 | 非零元 == 1389 | ✅ | `NonzeroCount_Is1389` |
| AC-5 | 48 行 ∈(0,1)；21 行 == 0 | ✅ | `RowSums_48ActiveInOpen01_21Zero` |
| AC-6 | 735 幸存对块等值；CC∩PP 重叠 0 | ✅ | `FanOut_All735SurvivingPairsHaveEqualBlockCells_NoCcPpOverlap` |
| AC-7 | 5 锚点值（绝对容差 1e-5） | ✅ | `Anchors_MatchIndependentlyComputedValues`（含方向哨兵 W[Amygdala][Pericalcarine]≈0.02277450 且反方向 0、tt↔cac 不对称对、HC→entorhinal PP 锚点） |
| AC-8 | τ 分布 27/30/12 + 2 mirror 点名 | ✅ | `Tau_DistributionAndMirrorInheritance`（LC-Right 0.15、SNc-Right 0.05） |
| AC-9 | 双 Build 逐元相等 | ✅ | `Build_IsDeterministic` |
| AC-10 | 不可解析端点 → InvalidDataException | ✅ | `UnresolvableEndpoint_ThrowsInvalidDataException`（合成 GameData，伪边 target='Ghost'） |
| AC-11 | 69 对角 0 + 同 dk 非对角 50 格 0 | ✅ | `DiagonalAndSameDkOffDiagonal_AllZero` |
| AC-12 | 21 排除 fid Tau > 0 | ✅ | `ExcludedFids_TauAllPositive` |

### spec §七 自检清单
- [x] **数学公式逐项对照**：w = edr × m_mean × focus（§5.2）/ 行归一化 +ε=0.01（§5.4 + 运行时 §4.3）/ τ 映射四档（§4.4）逐字实现于 AddEdge / Step 5 / ResolveTau，各有来源注释
- [x] **数据断言全部实测**：实现不携带任何硬编码计数（1389/735/50/21 全部由测试从数据推导或作为期望断言），与 2026-08-13 python 实测一致——12/12 绿即实证
- [x] **行序契约唯一 canonical** = RegionIds：Step 1 唯一来源 `data.Wsensory.RegionIds`，无 BrainRegionsData.Regions 序引用
- [x] **方向契约明确**（行=接收者，B3）且方向哨兵锚点入 AC-7：fan-out 行 `w[fidToRow[t], fidToRow[s]]` + AC-7 唯一非互惠对断言锁定
- [x] **边界值覆盖**：零行（AC-3/5）/ 唯一非互惠对（AC-7）/ mirror 继承（AC-8）/ 不可解析端点（AC-10）/ 自连接+同 dk 对（AC-11）/ 排除节点 τ（AC-12）
- [x] **确定性**：无 RNG、无 static 可变状态（AC-9 实证）
- [x] **接口注释先行**：Build XML doc 含职责/输入/输出/异常/来源（与 spec §三 逐字一致）
- [x] **偏差声明完整**：B1（Step 3 注释）/ B2（Step 3 注释）/ B3（AddEdge 注释 + fan-out 行）/ B4（Step 4 注释 + FocusMultiplier 常量注释）全部有对应实现注释
- [x] **排除清单逐名一致**：CstcDk 6 名与运行时状态模型 §4.2 逐字一致（builder 与测试双份对照）

### ⚠️ 结转验证（来自 sign-off 结转清单）
| # | 结转项 | 验证结果 |
|----|--------|---------|
| 1 | AC-7 锚点测试按 Step 4.3 解析规则展开（graph_nodes 键优先 → fid→dk 兜底；'Pericalcarine' 是 fid 名而 dk 键为小写 'pericalcarine'） | ✅ 测试侧 `ResolveFids` 镜像 Step 4.3 规则：'Pericalcarine' 大小写敏感经 fid 兜底解析为单 fid（dk 键 'pericalcarine' 不匹配）；'Amygdala'/cac/tt/entorhinal/Hippocampus 经 dk 键展开。**实测首跑即被本规则拦截一次测试侧错误**（'transversetemporal' 是 dk 键、fid 名为 'TransverseTemporal'，直接当 fid 查 RowFids 失败）→ 修正为统一 ResolveFids 展开后 12/12 绿 |
| 2 | AC-11 计数 50 由 graph_nodes 全量推导（Σ n(n−1)，不硬编码） | ✅ 测试遍历全部 51 个 GraphNodes 的 fid 对逐对断言 0，计数由推导累计，`Assert.Equal(50, count)` 仅锁定期望总数 |

### 发现的问题
| # | 问题 | 处置 |
|----|------|------|
| 1 | 测试首版把 dk 名 'transversetemporal' 当 fid 用（实际 fid 名 'TransverseTemporal'）→ RowFids 查无此键 | 修正测试统一走 ResolveFids（Step 4.3 规则）展开——正是结转 #1 要防的错，被它拦截。builder 零修改，非 spec 缺陷 |
| 2 | `dotnet test` 输出 NU1900（NuGet 漏洞数据源不可达）warning | 离线环境既有现象，与代码无关，不动 |

## Comments

（工作issue 关闭，见 Status）
