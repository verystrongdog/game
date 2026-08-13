# CstcGating — 实现规格

> Layer 3（CSTC Gurney 门控）引擎规格——`CstcGating` 把 WC 激活 a(t) 与 DA tone 转化为 15 个 Gurney 群体激活 + 3 个 gate + 3 环路 salience（每回合 Phase 3 的最后一个数值引擎）。版本: v1.0

## 目录

- [一、范围与依赖](#一范围与依赖)
- [二、数据结构](#二数据结构)
- [三、接口定义](#三接口定义)
- [四、枚举与常量](#四枚举与常量)
- [五、交叉引用约束](#五交叉引用约束)
- [六、验收标准](#六验收标准)
- [七、本 spec 自检清单](#七本-spec-自检清单)
- [变更日志](#变更日志)
- [参数速查表](#参数速查表)

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | `CstcGating` 类：构造函数（GameData → 三环路 CI 行索引）+ `Step(WcState, ToneState, GurneyState) → (GurneyState, GateState, LoopSalience)`（csharp-engine plan §4.4 签名） |
| 不覆盖 | SpeedScoreCalculator/TurnOrderBuilder（step 7）、Phase 4 gate_bonus 结算（应用侧——[运行时状态模型](../../../规则/技能树系统/运行时状态模型.md) §6.5 公式由 step 8/10 消费）、Phase 编排与事件（step 9-11）、NPC salience 竞争（step 12） |
| 前置依赖 | csharp-data-layer ✅（GameData / BrainRegionsData.Regions fid→FunctionProfile **单数** cstc_loop/cstc_role）、csharp-engine-types ✅（WcState/ToneState/GurneyState/GateState/LoopSalience/LoopValue/GurneyPopulation/CstcLoop/CstcRole）、csharp-wmatrix ✅（canonical 行序契约 Step 1）、csharp-wc-dynamics ✅（WcState + Δ=1.0 常量先例）、csharp-tone ✅（ToneState.DaVta/DaSnc + M1 实测值表） |
| 阻塞 | step 7 csharp-speed（决断分 mean(c_loop) 与执行分 a_SD1 数据源）、step 8 csharp-damage（gate_bonus）、step 10 csharp-flow（Phase 3 编排）、step 12 csharp-smoke |
| 输入数据 | `data/brain_regions.json` function_profile（fid 级 cstc_loop/cstc_role）——经 GameDataLoader.LoadAll 加载 |

本规格的决策依据 = [任务issue 01](issues/01-cstc-spec.md) D1-D13 + Q1/Q2/Q3 裁决（其「数据实测」表为全部计数与锚点出处，2026-08-13 python 实测）。本 spec 的 Step 锚点另经第二轮实测复算（gate 时刻语义修正——见 B1），锚点数值以本 spec §六 为准。

### 偏差声明（与设计文档/plan 的已知差异，实现必须照此执行）

| # | 偏差 | 依据 |
|----|------|------|
| B1 | **gate 时刻**：`gate_loop = 1 − O_GPi(a_new)`——O 取**更新后** a（非 prev） | 运行时状态模型 §7.1 步骤 5 顺序「更新 → O_GPi → gate」；plan §4.4 步骤 6 未指明时刻。AC-5/AC-9 锚点锁定（若误用 O(prev)，gate1 会得 0.8 而非 0.635） |
| B2 | **m ≤ 0 → O ≡ 0**：DA=1 时 m_SD2 = 0，文档 ramp 第三分支 `a > 1/m + e` 除零 | 文档 §6.3 ramp 公式未定义 m=0；ModelDB 语义（零输出）。AC-9 锚点锁定 |
| B3 | **收敛残差上界 5e-11**：\|a_new − u\| = \|a − u\|·e^(−25) ≤ 3.5 × 1.3887944e-11 ≈ 4.9e-11（值域 [−1.5, 2.0] 下 max\|a−u\| = 3.5） | 任务issue 数据实测表 :13 的「2.2 → 3e-11」按旧值域 [0,1] 推导；值域修正后上界 3.5（任务issue 表已同步修正） |

### Q 裁决记录（2026-08-13 已写回设计文档，commit f039f93）

| 裁决 | 内容 | 写回位置 |
|------|------|---------|
| Q1=A | W_SEL_GPe = 0.0 入权重表（SD1→GPe 无连接，ModelDB 83560 默认） | 运行时状态模型 §6.3 权重表 + plan §4.4 步骤 3 + README_gurney_model.md |
| Q2=A | per-population 阈值 e 表（对齐 ModelDB 83560）+ 取消 clamp（值域 [−1.5, 2.0]） | 运行时状态模型 §6.3/§三 + plan §4.4 步骤 4/5 + GurneyState 值域注 |
| Q3=B | c_loop 按 **fid 级**取（FunctionProfile 单数字段过滤）；跨环路 = 同 dk 不同 fid 分属两环 | 运行时状态模型 §6.1/§6.2 + plan §4.4 步骤 1 |

## 二、数据结构

### 2.1 已交付类型直接消费（csharp-engine-types ✅，本 feature 不新增类型）

| 类型 | 字段 | 本 feature 消费方式 |
|------|------|-------------------|
| WcState | `float[] A`（69 维，行序 = canonical 69 = Wsensory.RegionIds） | 输入——CI 行取均值 |
| ToneState | `Ne / DaVta / DaSnc / Ht5` | 输入——只消费 DaVta/DaSnc（Ne/Ht5 不参与 CSTC，文档化行为） |
| GurneyState | `float[] Somatic/Cognitive/Limbic`（各 5） | 输入（prev）+ 输出 |
| GateState | `GateSomatic/GateCognitive/GateLimbic` | 输出 |
| LoopValue | `(float C, float Da)` | 输出分量 |
| LoopSalience | `(LoopValue Somatic, LoopValue Cognitive, LoopValue Limbic)` | 输出 |
| GurneyPopulation | 枚举序 0=SD1, 1=SD2, 2=STN, 3=GPe, 4=GPi | 每环路数组序 |

### 2.2 每环路 Gurney 数组序

每环路 `float[5]` 下标 = **GurneyPopulation 枚举序**（0=SD1, 1=SD2, 2=STN, 3=GPe, 4=GPi）。三环路字段命名显式（Somatic/Cognitive/Limbic），不依赖 CstcLoop 枚举序（GurneyState 约束 C2）。

### 2.3 CI 行索引（构造期解析产物，非公开类型）

构造时每环路解析一次 `int[]`（canonical 行下标，升序）：fid 集 = `data.BrainRegions.Regions` 中 `FunctionProfile.CstcRole == CorticalInput && CstcLoop == <loop>` 的 fid（**单数字段**，Q3=B 裁决）。实测成员（2026-08-13 python）：

| 环路 | fid 数 | fid 名单 |
|------|--------|---------|
| somatic | 3 | Paracentral, Precentral, SuperiorFrontal |
| cognitive | 7 | AnteriorCingulateCortexDorsal, CaudalMiddleFrontal, FrontalPole, FrontalPoleExtreme, FrontalPoleFPN, ParsOpercularis, RostralMiddleFrontalDLPFC |
| limbic | 12 | Amygdala, AnteriorCingulateCortex, FrontalPoleDMN, FrontalPoleSN, HippocampusCA1, HippocampusCA3, Insula, LateralOrbitofrontal, MedialOrbitalPrefrontalDMN, MedialOrbitalPrefrontalVMPFC, RostralAnteriorCingulateCortex, SuperiorFrontalMPFC |
| global | 0 | —（不收集、不校验、不参与 gating，任务issue D5） |

跨环路（任务issue D13，归属断言数据）：caudalanteriorcingulate dk 的 3 fid = AnteriorCingulateCortex(limbic) + AnteriorCingulateCortexDorsal(cognitive) + FrontalPoleSN(limbic)；superiorfrontal dk 的 2 fid = SuperiorFrontal(somatic) + SuperiorFrontalMPFC(limbic)。每个 fid 只贡献一个环路，无单点双消费。

## 三、接口定义

新文件 `src/YouAreNotTheFish.Core/Engine/CstcGating.cs`（Engine/ 目录已存在；plan §3.2 L2 约定：纯函数、无副作用、无 RNG）。

```csharp
namespace YouAreNotTheFish.Core.Engine;

public sealed class CstcGating
{
    /// <summary>
    /// 解析三环路 CI 行索引（构造期一次）。
    /// 职责：rowFids = data.Wsensory.RegionIds（canonical 69）；对 somatic/cognitive/limbic 三环路，
    ///   收集 function_profile 中 cstc_role == CorticalInput && cstc_loop == <loop> 的 fid（单数字段，Q3=B），
    ///   fid → 行号解析镜像 WMatrixBuilder Step 1（fidToRow 字典）；CI 行按升序存储。
    ///   CstcLoop.Global/None 不收集、不校验（任务issue D5——实测 global 0 成员）。
    /// 异常：data 为 null → ArgumentNullException；
    ///       任一环路 CI 空集 → InvalidDataException（任务issue D4，含环路名）。
    /// 来源：csharp-engine plan §4.4 步骤 1；运行时状态模型 §6.1/§6.2。
    /// 偏差：Q3=B（fid 级口径）已写回文档，无偏差。
    /// </summary>
    public CstcGating(GameData data);

    /// <summary>
    /// 单回合 CSTC 门控更新（三环路独立，每环路 5 群体）。
    /// 职责（每环路，同时更新——u 全部由 prev 的 O 计算，镜像 WC 骨架）：
    ///   1. c = mean(a[ci rows])；2. DA = wVta×tone.DaVta + (1−wVta)×tone.DaSnc（§四 wVta 表）；
    ///   3. m = [1+DA, 1−DA, 1, 1, 1]；O_prev = ramp(prev, e, m)；
    ///   4. u = [c·(1+DA), c·(1−DA), c − O_prev[GPe], 0.9·O_prev[STN] − O_prev[SD2] + 0.0·O_prev[SD1],
    ///           0.9·O_prev[STN] − 0.3·O_prev[GPe] − O_prev[SD1]]（§6.3 u 表；W_SEL_GPe=0.0 项保留——Q1=A）；
    ///   5. a_new[p] = u[p] + (prev[p] − u[p])·exp(−25)（解析解，无 clamp——a 可为负，Q2=A；偏差 B2/B3）；
    ///   6. O_new = ramp(a_new, e, m)；gate = 1 − O_new[GPi]（偏差 B1——O 取更新后 a）。
    /// 输出：GurneyState（三环路 a_new）/ GateState（三 gate）/ LoopSalience（三 (c, DA)）。
    ///   LoopSalience.Da 按字段名配对（Somatic.Da = 0.2×VTA+0.8×SNc 等——LoopSalience 已交付文档警告，
    ///   不得按文档 §6.3 列表序 limbic→cognitive→somatic 直配，任务issue D8）。
    /// 输入：a 旧 WC 状态（69 维，canonical 行序）；tone 当前 4 tone（只消费 DaVta/DaSnc）；
    ///       prev 旧 Gurney 状态（三环路各 5，群体序 = GurneyPopulation 枚举序）。
    /// 异常：a/tone/prev 为 null → ArgumentNullException；
    ///       a.A.Length ≠ 69 → ArgumentException；prev 任一环路数组 Length ≠ 5 → ArgumentException。
    /// 未定义行为（不校验，调用方契约）：输入含 NaN/Infinity 输出未定义（生产方保证输入有限，同 wc-dynamics 姿态）。
    /// 来源：csharp-engine plan §4.4；运行时状态模型 §6.2-6.4、§7.1 步骤 4-5。
    /// 偏差：B1（gate 时刻）、B2（m=0 防护）、B3（残差上界）。
    /// </summary>
    public (GurneyState Gurney, GateState Gates, LoopSalience Salience) Step(
        WcState a, ToneState tone, GurneyState prev);
}
```

## 四、枚举与常量

### 4.1 连接权重（CstcGating 私有常量，不扩 CalibrationConfig——任务issue D3；运行时状态模型 §6.3 表）

| 权重 | 值 | 含义 |
|------|-----|------|
| W_SEL | 1.0f | 皮层→SD1 |
| W_CONT | 1.0f | 皮层→SD2 |
| W_STN | 1.0f | 皮层→STN |
| W_SEL_GPi | −1.0f | SD1→GPi（GO） |
| W_SEL_GPe | 0.0f | SD1→GPe（无连接——Q1=A 裁决入表） |
| W_CONT_GPe | −1.0f | SD2→GPe |
| W_STN_GPi | 0.9f | STN→GPi（STOP） |
| W_STN_GPe | 0.9f | STN→GPe |
| W_GPe_STN | −1.0f | GPe→STN |
| W_GPe_GPi | −0.3f | GPe→GPi |

### 4.2 per-population 阈值 e（Q2=A 裁决；运行时状态模型 §6.3 表；群体序 = GurneyPopulation）

| 群体 | e | 备注 |
|------|-----|------|
| SD1 | 0.2f | GO 激活阈值 |
| SD2 | 0.2f | NO-GO 激活阈值 |
| STN | −0.25f | 超直接通路低阈（快速响应） |
| GPe | −0.2f | tonic 输出（a=0 → O=0.2） |
| GPi | −0.2f | **tonic 抑制**（a=0 → O=0.2 → gate=0.8） |

### 4.3 DA 混合权重（按 CstcLoop 值配对，不按 §6.3 文档列表序）

| 环路（CstcLoop 枚举值） | wVta | wSnc = 1 − wVta |
|------------------------|------|-----------------|
| Somatic | 0.2f | 0.8f |
| Cognitive | 0.4f | 0.6f |
| Limbic | 0.8f | 0.2f |

### 4.4 其余常量

| 常量 | 值 | 来源 |
|------|-----|------|
| GurneyK | 25f（τ = 0.04s；Δ=1.0 隐含——复用注：Δ 引用 csharp-wc-dynamics spec §四，不重新定义） | 运行时状态模型 §6.3 |
| m_SD1 / m_SD2 | 1 + DA / 1 − DA | 运行时状态模型 §6.3（DA=1 → m_SD2=0 → O≡0，偏差 B2） |
| m_STN / m_GPe / m_GPi | 1.0f | 运行时状态模型 §6.3 |
| 值域 | [−1.5, 2.0]（无 clamp） | 运行时状态模型 §三 |

## 五、交叉引用约束

| # | 约束 | 违反处置 | 来源 |
|---|------|---------|------|
| C1 | CI fid→行号解析镜像 WMatrixBuilder Step 1（canonical = Wsensory.RegionIds，fidToRow 字典） | — | csharp-wmatrix spec Step 1 行序契约 |
| C2 | 三环路 CI 集非空 | 构造 InvalidDataException（含环路名） | 任务issue D4 |
| C3 | CstcLoop.Global/None 不收集、不校验、不产出 | — | 任务issue D5；实测 global 0 成员 |
| C4 | 只有 CI 成员资格影响 c_loop——striatal_gate/pallidal_output/thalamic_relay/modulator 角色不被 Step 消费 | — | 任务issue D6；Gurney 5 群体是每环路抽象变量 |
| C5 | 输出不 clamp——a 可为负（值域 [−1.5, 2.0]），负阈值机制要求 | — | 任务issue D11（Q2=A） |
| C6 | LoopSalience.Da 按字段名配对（Somatic/Cognitive/Limbic 显式字段），不得按位置直配 | — | LoopSalience 已交付文档警告；任务issue D8 |
| C7 | 输入不突变（a/tone/prev 全程只读）；输出为新建状态 | — | 契约 C5（GurneyState 构造防御拷贝，输入数组不共享） |
| C8 | 纯函数：无 static 可变状态、无 RNG、同输入同输出 | — | 契约 C6 |

## 六、验收标准

数值锚点全部来自本 spec §二 2.3 + 第二轮 python 实测（2026-08-13）；测试断言用 MathF 现算（1e-5 容差）或逐位比较，不裸写锚点字面量（wmatrix 结转 #1 教训）。合成输入（synthetic WcState/ToneState/GurneyState）直接从已交付 record 类型构造。

### 构造与成员

| # | 验收标准 | 锚点/断言 |
|---|---------|----------|
| AC-1 | CI 成员资格（fid 级，Q3=B） | 构造解析的三环路 fid 集 == §二 2.3 表名单（SetEquals）+ 计数 3/7/12；global 0 成员不报错 |
| AC-2 | 空 CI 环路防御（D4） | 合成 GameData（真实数据克隆 + 将 limbic 全部 12 个 CI fid 的 FunctionProfile.CstcRole 改为非 CorticalInput）→ 构造抛 InvalidDataException 且消息含环路名 |
| AC-3 | Global 环路不校验 | 合成数据将 global 环路（无成员）与 None 值保持 → 构造成功；输出三字段无 global 分量（类型级断言） |

### Step 数值锚点（每环路 5 群体，群体序 = GurneyPopulation；锚点列 [SD1, SD2, STN, GPe, GPi]）

| # | 验收标准 | 锚点/断言 |
|---|---------|----------|
| AC-4 | c=0 门控抑制（plan §十「c_loop=0 门控抑制」） | synthetic a = 全零（c=0 三环路）→ Step(prev=零)：a1 = [0, 0, −0.2, 0.225, 0.165]，gate1 = 0.635（三环路相同——c=0 时 DA 不参与 u_SD1/u_SD2）；迭代 Step 至 max\|Δ\| < 1e-7（≤100 回合）→ gate = 0.843421（1e-5）且 **gate < 1**（门控抑制成立，对比静息 gate=1.0） |
| AC-5 | 静息 gate = 1.0（整合，M1 链） | 测试重建 M1 静息 a（WMatrixBuilder.Build + CorticalBias.Compute(baseline) + WcDynamics.Step ×30——csharp-tone AC-15 同链）→ Step(prev=零)：三环路 gate1 = 0.635；Step(prev=第一步结果)：三环路 gate2 = 1.0（1e-5） |
| AC-6 | 静息 c/DA 锚点（行序正确性锁定） | 同 AC-5 链：LoopSalience C = 0.665469/0.696963/0.692102（somatic/cognitive/limbic，1e-5）；Da = 0.48/0.46/0.42（baseline tone VTA=0.4, SNc=0.5，1e-5） |
| AC-7 | 跨环路 fid 归属断言（D13/Q3=B，plan §十「跨环路节点双贡献」→ fid 级语义） | synthetic a：仅 caudalanteriorcingulate 的 3 fid（AnteriorCingulateCortex, AnteriorCingulateCortexDorsal, FrontalPoleSN）= 1.0，其余 0 → C_cognitive = 1/7 = 0.142857、C_limbic = 2/12 = 0.166667、C_somatic = 0（1e-5）。仅 superiorfrontal 2 fid（SuperiorFrontal, SuperiorFrontalMPFC）= 1.0 → C_somatic = 1/3 = 0.333333、C_limbic = 1/12 = 0.083333、C_cognitive = 0。无 fid 双计（每个 fid 恰好贡献一环） |
| AC-8 | DA 混合逐字段配对（D8） | tone(VTA=1.0, SNc=0.0) → Da = 0.2/0.4/0.8（Somatic/Cognitive/Limbic 字段序，1e-5）；tone(VTA=0.0, SNc=1.0) → Da = 0.8/0.6/0.2。文档 §6.3 列表序（limbic→cognitive→somatic）与字段序不同——断言按字段名 |
| AC-9 | DA=1 → m_SD2=0（plan §十「DA 极端 0/1 下 ramp 斜率」+ 偏差 B2 除零防护） | tone(VTA=1, SNc=1)（DA=1 三环路）、synthetic a 全 1.0（c=1）、prev a_SD2=1.0：a1 = [2.0, 0.0, 0.8, 0.225, 0.165]（SD1 饱和 2.0、SD2 归零——m=0 除零防护生效不抛异常）；O1 = [1.0, 0.0, 1.0, 0.425, 0.365]（m_SD1=2 饱和点 a≥0.7 → O=1.0；O_SD2 ≡ 0）；gate1 = 0.635；迭代 → gate = 1.0（1e-5） |
| AC-10 | DA=0 → 对称斜率（m_SD1=m_SD2=1） | tone(VTA=0, SNc=0)、synthetic a 全 1.0（c=1）、prev 零：a1 = [1.0, 1.0, 0.8, 0.225, 0.165]，O1 = [0.8, 0.8, 1.0, 0.425, 0.365]，gate1 = 0.635；迭代 → gate = 0.806579（1e-5，DA=0 门控窄区间端点） |
| AC-11 | 解析收敛（D9，plan §十「解析收敛到 u」） | c=0.5 DA=0.5（synthetic a 使 c=0.5：如全 0.5；tone 使 DA=0.5）prev 零：a1 = [0.75, 0.25, 0.3, 0.225, 0.165]（1e-5）；第二步 a2 = [0.75, 0.25, 0.075, 0.47, −0.4575] 且 **a2 == u2 逐位**（测试以 float32 同公式复算 u2 不含衰减项，Assert.Equal 精确比较——锚点 \|u\| ≥ 0.075 ≥ 0.01 逐位安全域）；全值域断言 \|a_new − u\| ≤ 5e-11（偏差 B3，测试在 [−1.5, 2.0] 网格复算） |
| AC-12 | 无 clamp 负值（D11/Q2=A） | AC-11 第二步 a_GPi = −0.4575 原样返回（不抬升到 0）；网格扫描 c∈{0, 0.3, 0.5, 1} × DA∈{0, 0.5, 1} 各迭代 20 回合 → 全部 a ∈ [−1.5, 2.0]（§三 值域），负值合法 |
| AC-13 | 输入不可变 + 确定性（C7/C8） | a/tone/prev 三环路数组逐元不变（改输出后比较）；同输入两次调用三元组逐位相等（含 GateState/LoopSalience） |
| AC-14 | 契约防御（D4） | a/tone/prev 各 null → ArgumentNullException；a.A.Length ∈ {0, 68, 70} → ArgumentException；prev 任一环路数组 Length ∈ {0, 4, 6} → ArgumentException |
| AC-15 | gate 输出域 [0,1] | 网格扫描（同 AC-12）全部 gate ∈ [0, 1] 有限无 NaN |

## 七、本 spec 自检清单

1. 数学公式逐项对照——u 五式/ramp/gate/DA 混合与 [运行时状态模型](../../../规则/技能树系统/运行时状态模型.md) §6.3/§6.4 及 plan §4.4 逐字一致（含 W_SEL_GPe=0.0 项保留、per-population e 表、无 clamp）
2. 数值断言全部实测——AC 锚点全部来自 2026-08-13 python 实测（任务issue 数据实测表 + 本 spec 第二轮复算），无凭记忆数字
3. 行序契约明确——CI fid→行解析镜像 WMatrixBuilder Step 1（canonical = Wsensory.RegionIds）；AC-6 静息 c 锚点锁定行序正确性
4. 接口注释先行——构造 + Step XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差（「设计两次」约束）
5. 边界值覆盖——c=0 / DA=0 / DA=1（m_SD2=0 除零）/ 负 prev（无 clamp）/ 静息整合 / 空 CI 防御 / 形状防御 / 输出域
6. 确定性——纯函数无静态状态（AC-13 实证）
7. 偏差声明完整——B1（gate 时刻）/B2（m=0 防护）/B3（残差上界）+ Q1/Q2/Q3 裁决标注，实现注释逐条对应
8. Δ/k 复用漂移注——exp(−25) 的 k=25 隐含 Δ=1.0 复用（常量注释显式引用 csharp-wc-dynamics spec §四，不重新定义 Δ）
9. 同时更新语义——u 全部由 O(prev) 计算（镜像 WC 骨架），无顺序偏倚；AC-11 锚点锁定

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-13 | 初稿（构造 + Step 规格；AC-1~15；偏差 B1-B3） | 任务issue 01（数据实测 + Q1/Q2/Q3 裁决 + D1-D13） | 全量审计 |

---
*创建: 2026-08-13 | 更新: 2026-08-13 | 版本: v1.0*
*关联: [csharp-engine plan](../../csharp-engine/design/plan.md) §4.4/§十/§十三-3, [任务issue 01](issues/01-cstc-spec.md), [运行时状态模型](../../../规则/技能树系统/运行时状态模型.md) §6/§三, [csharp-tone spec](../../csharp-tone/design/spec.md)（M1 链 + AC-15）, [csharp-wc-dynamics spec](../../csharp-wc-dynamics/design/spec.md) §四（Δ 先例）*

## 参数速查表

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| Gurney 时间常数 | τ_gurney（k） | 0.04 s（25） | 运行时状态模型 §6.3 |
| 连接权重 10 项 | W_SEL … W_GPe_GPi | 1.0 / 1.0 / 1.0 / −1.0 / 0.0 / −1.0 / 0.9 / 0.9 / −1.0 / −0.3 | 运行时状态模型 §6.3 |
| 群体阈值 | e_SEL/e_CONT/e_STN/e_GPe/e_GPi | 0.2 / 0.2 / −0.25 / −0.2 / −0.2 | 运行时状态模型 §6.3 |
| DA 混合 VTA 权重 | w_VTA_somatic/cognitive/limbic | 0.2 / 0.4 / 0.8 | 运行时状态模型 §6.3 |
| Ramp 斜率 | m_SD1 / m_SD2 / 其余 | 1+DA / 1−DA / 1.0 | 运行时状态模型 §6.3 |
| Gurney 群体值域 | — | [−1.5, 2.0]（无 clamp） | 运行时状态模型 §三 |
| gate 值域 | — | [0, 1] | 运行时状态模型 §6.4 |
