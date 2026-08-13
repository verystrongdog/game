# 工作issue 01: WcDynamics.Step 实现 + AC-1~12 测试

> Status: resolved | Type: implementation | Spec: [../../design/spec.md@v1.1](../../design/spec.md) | Blocked by: sign-off ✅（2026-08-13 批准）| GitHub: [#53](https://github.com/verystrongdog/game/issues/53)

## 范围

实现 `WcDynamics.Step`（spec §三接口定义 + §四常量 + §五契约），覆盖 spec §六 **AC-1 ~ AC-12** 全部验收标准。

## 文件所有权声明

- `src/YouAreNotTheFish.Core/Engine/WcDynamics.cs` — 新建
- `src/YouAreNotTheFish.Core.Tests/Engine/WcDynamicsTests.cs` — 新建

（创建前已 grep：无其他进行中工作issue 修改上述文件。）

## 完成标准

spec §六 AC-1~12 逐条对照（见下自审表）。

## 实现

- `src/YouAreNotTheFish.Core/Engine/WcDynamics.cs` — Step（解析解，同步更新，契约防御，B1/B2/B3 注释逐条对应）
- `src/YouAreNotTheFish.Core.Tests/Engine/WcDynamicsTests.cs` — AC-1~12 共 14 个 [Fact]

## 代码自审（证据式）

### 门禁证据

- [x] `dotnet build` 零错误 —— 0 Error / 2 Warning（均为 NU1900：NuGet 漏洞源不可达，环境性非代码；本机离线 NuGet 缓存正常解析）
- [x] `dotnet test` 全绿 —— **Passed: 76 / Total: 76**（WcDynamics 14 + 既有 62；过滤 WcDynamics 单跑 14/14，Duration 650 ms）

### 验收标准逐条对照

| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | 形状与不可变性 | ✅ | `Step_ReturnsNew69Array_AndDoesNotMutateInputs`——NotSame + 改输出后输入逐元不变 |
| AC-2 | 快节点精确收敛 | ✅ | `Step_FastTau_ConvergesBitExactToSigma`——69 节点逐位 == MathF σ(1.0) |
| AC-3 | 解析解公式锚点（slow） | ✅ | `Step_SlowTau_MatchesAnalyticAnchors`——0.621794432 / 0.378205568（1e-5） |
| AC-4 | 单调不振荡 | ✅ | `Step_SlowTau_IsStrictlyBetweenAAndSigma`——0.10 < a' < σ(1.0) |
| AC-5 | 静息吸引子 | ✅ | `Step_RestingAttractor_MatchesMeasuredFixedPoint`——48 活跃 ∈ [0.4986, 0.49951]、21 排除 == σ(0)、max\|Δ\| < 1e-4、≠0.10 |
| AC-6 | 排除节点响应 b/s | ✅ | `Step_ExcludedNode_RespondsToBAndS_IndependentOfA`——a=1.0 与 a=0.3 结果逐位相同 |
| AC-7 | bimodal s=2.0 | ✅ | `Step_BimodalInput_BitExactSigma2`——逐位 == MathF σ(2.0)，全部 ∈[0,1] 无 NaN |
| AC-8 | 同步更新 | ✅ | `Step_UsesSynchronousUpdate`——a'_1 == 0.5（就地实现会得反例 0.422814620） |
| AC-9 | 方向契约哨兵 | ✅ | `Step_DirectionSentinel_PericalcarineToAmygdala`——W[Amy][Peri]>0、反向 0、双侧公式自算（1e-5） |
| AC-10 | 确定性 | ✅ | `Step_IsDeterministic`——同输入两次逐位相等 |
| AC-11 | 契约防御 | ✅ | `Step_NullInputs_ThrowArgumentNullException` + `Step_InvalidShapes_ThrowArgumentException` + `Step_NonPositiveTau_ThrowsArgumentException`——4 null / 5 形状 / τ=0 与 τ<0 |
| AC-12 | 极端输入 | ✅ | `Step_ExtremeInputs_AllFiniteIn01`——69 维全有限 ∈[0,1]，max ∈ [0.9707, 0.9890] |

### spec §七 自检清单

- [x] 数学公式逐项对照——解析解与 spec §二 逐字一致；σ 用 §四常量（v/θ）
- [x] 数值断言全部实测——AC 锚点全部来自 spec §六（python 实测 + 审计复算）
- [x] 方向契约明确——行=接收者，直接消费 W 无转置（AC-9 锁定）
- [x] 同步更新语义——新值写独立数组，aArr 全程只读（AC-8 锁定）
- [x] 边界值覆盖——fast/medium/slow τ、排除节点、bimodal、a=0.10、τ≤0、null/长度、极端输入
- [x] 确定性——纯函数无静态状态（AC-10 实证）
- [x] 接口注释先行——XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差（spec §三 逐字落地）
- [x] 偏差声明完整——B1（解析解，公式处）、B2（吸引子，XML doc）、B3（固定点迭代，同步更新注释处）

### ⚠️ 结转验证（来自 sign-off 结转清单）

| # | 结转项 | 验证结果 |
|----|--------|---------|
| 1 | AC-9 测试用 fid 名 'Pericalcarine'（大写 P） | ✅ RowOf(m, "Pericalcarine") 直接命中 RowFids；全程未出现小写 dk 键 |
| 2 | AC-6/7/9 期望值 MathF 自算 | ✅ SigmaT/公式全部 MathF 现算；唯一字面量锚点（AC-3/5 的 1e-5 容差断言）与计算值差 <1e-7 |
| 3 | 偏差 B1/B2/B3 实现注释逐条对应 | ✅ WcDynamics.cs：B1 公式处、B2 XML doc、B3 同步更新注释处 |
| 4 | 设计文档叙述修正并入 plan §十三-8 | ✅ 移交 feature 闭合后（M1 实测后执行——见 map.md 回顾段） |

### 发现的问题

| # | 问题 | 处置 |
|----|------|------|
| 1 | Sigma 辅助实现用完整式 `exp(−v·(x−θ))`（spec §四 辅助式为 v=1 省略形） | 保持——IEEE 754 下 ×1.0f 精确，逐位等价；SigmaGain 常量得以使用（spec §四 定义该常量但省略形用不到）。代码注释已注明等价性 |
| 2 | AC-5 测试断言锚点紧区间 [0.4986, 0.49951]（比 AC 文本 [0.49, 0.50] 更紧） | 保持——数据漂移哨兵模式（与 wmatrix 测试同类）；漂移时测试报错位置即真相位置 |

## Comments

- 2026-08-13：创建（sign-off 批准后）。
- 2026-08-13：实现完成，76/76 全绿，自审闭合 → resolved。
