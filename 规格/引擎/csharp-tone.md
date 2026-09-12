# ToneUpdater + CorticalBias — 实现规格

> Layer 2（脑干广播调制）引擎规格——`ToneUpdater.Step`（4 tone 解析解单步动力学）与 `CorticalBias.Compute`（tone → b_j 69 维注入）的实现规格，附 M1 静息 trace 里程碑。版本: v1.1

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
| 覆盖 | `ToneUpdater.Step(ToneState, float[], CalibrationConfig) → ToneState`：4 tone 解析解单步动力学；`CorticalBias.Compute(ToneState, GameData) → float[69]`：tone → b_j 注入计算；M1 静息 trace 里程碑（AC-15 + 实测值写回设计文档） |
| 不覆盖 | δ 事件生产/聚合语义（step 9 EventProcessor）、CstcGating（step 6）、战斗初始化 tone=baseline（step 10 职责）、7 参数化性格→baseline 映射（设计延迟项） |
| 前置依赖 | csharp-data-layer ✅（GameData / TripartiteModel.Brainstem 114 边 / GraphNodes 51）、csharp-engine-types ✅（ToneState / CalibrationConfig.DeltaScale）、csharp-wmatrix ✅（WMatrix 行序契约）、csharp-wc-dynamics ✅（WcDynamics.Step + Δ=1.0 常量先例） |
| 阻塞 | step 6 csharp-cstc（DA 环路混合需要 tone）、step 9 csharp-events（调用 Step）、step 11 csharp-console（--trace-resting） |
| 输入数据 | `data/connectivity/tripartite_model.json` brainstem（114 条）——均经 GameDataLoader.LoadAll 加载 |

本规格的决策依据 = [任务issue 01](../../.scratch/csharp-tone/design/issues/01-tone-spec.md) D1-D12（其「数据实测」表为本 spec 全部计数与锚点的出处，2026-08-13 python 实测 JSON，非凭记忆）。

### 偏差声明（与设计文档/plan 的已知差异，实现必须照此执行）

| # | 偏差 | 依据 |
|----|------|------|
| B1 | **Step 签名加参**：plan §4.3 签名 `Step(ToneState, float[])` → 本 spec `Step(ToneState, float[], CalibrationConfig)`，Step 内部应用 `cfg.DeltaScale` | 任务issue Q2 用户裁决（2026-08-13）；δ_scale 杠杆留在动力学层 + 可注入（对齐 csharp-engine-types 决策 D3 实例化模式） |
| B2 | **tone 解析解**：[运行时状态模型](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) §5.2/§7.1 为 Euler → 解析指数解（plan §十二-2 已裁定） | plan 审计数值证明 Euler 在此参数下失真；τ_tone 0.3-1.5 无 underflow 风险（k_t ≥ 0.0357） |
| B3 | **tone 值域 [0,1]**：核心机制 §十一 写 [0.1, 2.0] → 取 NPC AI §4.1 [0, 1] + clip（plan §十二-7 已裁定） | 文档内部冲突，与 §5.2 clip(tone, 0, 1) 一致 |
| B4 | **M1「略高」预测修正**：plan §八 预测「实际 b_j>0 会略高」→ 实测 max 0.7712（python 预览；C# 实测值最终写回文档） | 任务issue 数据实测表 M1 预览行；文档写回以 C# 实测为准 |

## 二、数据结构

### 2.1 ToneState（csharp-engine-types 已交付，直接消费）

`record ToneState { Ne; DaVta; DaSnc; Ht5; }`——4 个 tone 分量，值域 [0,1]（§5.2 clip）。本 feature 不新增类型。

### 2.2 delta 输入（float[4]）

| 下标 | 分量 | ToneState 属性 | 来源 |
|------|------|---------------|------|
| 0 | NE | Ne | §5.3 表序 |
| 1 | DA_VTA | DaVta | §5.3 表序 |
| 2 | DA_SNc | DaSnc | §5.3 表序 |
| 3 | 5HT | Ht5 | §5.3 表序 |

delta 为**未缩放原始 δ**（pattern × magnitude，§5.5）；缩放由 Step 内部 `δ_eff = δ × cfg.DeltaScale` 执行（B1）。

### 2.3 CalibrationConfig.DeltaScale（已交付，直接消费）

`CalibrationConfig.DeltaScale` = 0.3f [NEW] 待校准（plan §七；运行时状态模型 §5.5 ⚠️ 延迟注）。本 feature 不新增常量字段。

## 三、接口定义

新文件 `src/YouAreNotTheFish.Core/Engine/ToneUpdater.cs` 与 `src/YouAreNotTheFish.Core/Engine/CorticalBias.cs`（Engine/ 目录已存在；plan §3.2 L2 约定：纯函数、无副作用、无 RNG）。

```csharp
namespace YouAreNotTheFish.Core.Engine;

public static class ToneUpdater
{
    /// <summary>
    /// 单步更新 4 个脑干 tone（解析解 + clip）。
    /// 职责：对每个 tone 应用解析指数解
    ///   tone' = clip(baseline_t + δ_eff + (tone_t − baseline_t − δ_eff) · e^(−Δ/τ_t), 0, 1)，
    ///   其中 δ_eff = δ × cfg.DeltaScale；Δ=1.0、τ 与 baseline 为私有常量（§四）。
    /// 输入：tone 当前状态（值域 [0,1]，ToneState 契约，不校验）；
    ///       delta float[4]（分量顺序 NE/DA_VTA/DA_SNc/5HT，§5.3 表序），值为未缩放原始 δ；
    ///       cfg 校准配置（消费 DeltaScale）。
    /// 输出：新 ToneState（输入不突变）。
    /// 异常：tone/delta/cfg 为 null → ArgumentNullException；delta.Length ≠ 4 → ArgumentException。
    /// 未定义行为：同窗口多事件 δ 聚合（Σ）与实时发射时序由调用方（step 9 EventProcessor）负责，
    ///   本方法只处理单次 δ（任务issue D5——连续 Step ≠ 聚合一次，语义归属唯一）。
    /// 来源：csharp-engine plan §4.3；运行时状态模型 §5.2-5.4。
    /// 偏差：B1（签名加参）、B2（解析解）、B3（值域 [0,1]）。
    /// </summary>
    public static ToneState Step(ToneState tone, float[] delta, CalibrationConfig cfg);
}

public static class CorticalBias
{
    /// <summary>
    /// 计算 tone → 皮层 b_j 注入向量（69 维）。
    /// 职责：b_j = Σ_t tone_t × w_t(j)，w_t(j) 从 brainstem 边的 role 字段取
    ///   （active→1.0 / modulating→0.5；per-target 唯一——同 system 同 target 多条边只取一次，任务issue Q1）；
    ///   求和后逐分量 clamp [0, 2]（§7.2）。
    /// 输入：tone 当前 4 tone（值域 [0,1]）；data 全量游戏数据（消费 Tripartite.GraphNodes 与 Tripartite.Brainstem）。
    /// 输出：新 float[69]，行序 = Wsensory.RegionIds（canonical 行序，csharp-wmatrix spec Step 1），供 WcDynamics.Step 直接消费。
    /// 异常：tone/data 为 null → ArgumentNullException；
    ///       边 target 不在 GraphNodes → InvalidDataException（含边描述）；
    ///       边 Role == Silent → InvalidDataException（brainstem 数据契约只允许 Active|Modulating，实测 114/114）。
    /// 来源：csharp-engine plan §4.3（修复 #8b）；运行时状态模型 §5.6-5.7、§7.2。
    /// </summary>
    public static float[] Compute(ToneState tone, GameData data);
}
```

## 四、枚举与常量

### 4.1 ToneUpdater 私有常量

| 常量 | 值 | 来源 | 备注 |
|------|-----|------|------|
| DeltaSeconds | 1.0f | **csharp-wc-dynamics spec §四**（Δ=1.0 复用漂移风险注——引用其常量来源，不重新定义） | 回合时长默认 1.0 秒（皮层动力学-通用层 §4.3） |
| TauNe / TauDaVta / TauDaSnc / TauHt5 | 0.5f / 0.3f / 0.8f / 1.5f | 运行时状态模型 §5.3 | 设计定值无校准需求（任务issue D2，同 wc-dynamics D3 先例） |
| BaselineNe / BaselineDaVta / BaselineDaSnc / BaselineHt5 | 0.3f / 0.4f / 0.5f / 0.5f | 运行时状态模型 §5.4 | 同上 |

### 4.2 CorticalBias 常量

| 常量 | 值 | 来源 |
|------|-----|------|
| WeightActive / WeightModulating | 1.0f / 0.5f | 运行时状态模型 §5.6 role 两档 |
| BiasMin / BiasMax | 0f / 2f | 运行时状态模型 §7.2（b_j ∈ [0,2]，clip 兜底） |

### 4.3 系统 → tone 映射

| BrainstemSystem（已交付 enum） | tone 分量（ToneState 属性） |
|-------------------------------|---------------------------|
| LcNe | Ne |
| Raphe5Ht | Ht5 |
| SncDa | DaSnc |
| VtaDa | DaVta |

## 五、交叉引用约束

| # | 约束 | 违反处置 | 来源 |
|---|------|---------|------|
| C1 | 输出行序 = `data.Wsensory.RegionIds`（69，首键 AccumbensCore），与 WMatrix.RowFids 逐位一致 | — | csharp-wmatrix spec Step 1 行序契约 |
| C2 | brainstem 边 target 必须命中 `Tripartite.GraphNodes` 的 dk 键 → functional_ids fan-out 到行序下标 | InvalidDataException（含边描述） | 任务issue D8；实测 114/114 命中 |
| C3 | brainstem 边 Role ∈ {Active, Modulating} | InvalidDataException | 任务issue D7；实测 silent 0 条 |
| C4 | 排除 fid（21 个，W 行=0）**仍接收 b_j**（7 个纹状体 fid：VTA+SNc DA tone） | — | 运行时状态模型 §7.2 锚点；数据实测表 |
| C5 | 输入 tone 值域 [0,1] 不校验（ToneState 契约）；输出 clip [0,1] 保证 | — | 任务issue D10/D12；同 wc-dynamics AC-12 极端输入姿态 |
| C6 | 同一 system 同一 target 的重复边（Raphe DR+MnR）只贡献一次 role 权重 | — | 任务issue Q1 裁决（2026-08-13，per-target 唯一） |

## 六、验收标准

数值锚点全部来自任务issue「数据实测」表（2026-08-13 python 实测）；测试断言用 MathF 现算（1e-5 容差）或逐位比较，不裸写锚点字面量（wmatrix 结转 #1 教训）。

### ToneUpdater

| # | 验收标准 | 锚点/断言 |
|---|---------|----------|
| AC-1 | 形状与不可变性 | Step 返回新 ToneState；输入 tone/delta/cfg 不突变（改输出后逐元不变） |
| AC-2 | δ=0 回基线衰减 | NE from 0.8 → 0.367667642（解析解 1e-5）；NE from 0.3（=baseline）→ 0.3 精确（不动点） |
| AC-3 | 单脉冲 4 tone 锚点（δ_scale=0.3） | NE 0.3 +d1 → 0.559399415；DA_VTA 0.4 +d1 → 0.689297802；DA_SNc 0.5 +d1 → 0.714048561；5HT 0.5 +d1 → 0.645974864 |
| AC-4 | δ_scale 杠杆 + DA 饱和边界（plan §十「DA 饱和边界」） | cfg DeltaScale=1.0：5HT 0.5 +d1 → 0.986582881（不 clip）；DA_VTA 0.4 +d1 → 1.0（1.364326 超界被 clip——无杠杆时单次命中即饱和的演示） |
| AC-5 | 大 δ clip [0,1]（plan §十「大 δ clip」） | NE 0.3 +d10 → 1.0；5HT 1.0 −d10 → 0.0；输出全部 ∈ [0,1] 有限无 NaN |
| AC-6 | 连续双脉冲 back-to-back（plan §十） | NE +1,+1 两次 Step：0.559399415 → 0.594505308 |
| AC-7 | 契约防御 | tone/delta/cfg 各 null → ArgumentNullException；delta.Length ∈ {0,3,5} → ArgumentException |
| AC-8 | 确定性 | 同输入两次逐位相等（纯函数，无静态状态） |

### CorticalBias

| # | 验收标准 | 锚点/断言 |
|---|---------|----------|
| AC-9 | 形状与行序 | 输出新 float[69]；行序 == Wsensory.RegionIds（测试用数据推导断言，不裸写序列） |
| AC-10 | per-target 唯一（Q1 裁决锁定） | BanksSTS（LC mod + Raphe mod）b = 0.3×0.5 + 0.5×0.5 = 0.4——per-edge 求和会得 0.65，断言 0.4 锁定裁决 |
| AC-11 | role 两档 + 排除节点接收 b_j | baseline tone 下：NAcc 4 fid（AccumbensCore/AccumbensShell/NucleusAccumbens/VentralStriatum）b = 0.9（VTA act + SNc act）；Caudate/StriatumMatrix/Putamen b = 0.7（VTA mod + SNc act）；Amygdala b = 0.45（VTA mod + Raphe mod） |
| AC-12 | 零广播节点 | §5.7 正典四名（PeriaqueductalGray/SuperiorColliculus/PontineReticularNucleus/CerebellumCortex）b == 0；全零集合由数据推导断言（15 fid：10 脑干源 + CerebellumCortex + Pallidum + SubthalamicNucleus + Thalamus + ThalamusPulvinar，任务issue 数据实测表） |
| AC-13 | clamp [0,2] | tone=1.0 全四分量：全部 b ∈ [0,2]，max == 2.0；clamp 命中集合 == {FrontalPoleDMN, MedialOrbitalPrefrontalDMN, MedialOrbitalPrefrontalVMPFC}（pre-clamp 2.5 → 2.0）。另有 10 fid pre-clamp 恰为 2.0（Accumbens-area 4 + rostralmiddlefrontal 3 + superiorfrontal 2 + lateralorbitofrontal 1），clamp 数值不变，不属命中集合 |
| AC-14 | 基线 b_j 锚点 | baseline tone 下 mOFC 3 fid（同 AC-13 三 fid）b = 1.05（5HT act + VTA act + LC mod 累积） |
| AC-16 | 契约防御（E2 新增） | tone/data 各 null → ArgumentNullException；合成伪边（真实数据 + 追加伪造 brainstem 边，经 csharp-data-layer 已交付 record 类型构造）target 不在 GraphNodes → InvalidDataException 且消息含边描述；合成伪边 Role==Silent → InvalidDataException |

### M1 静息 trace 里程碑

| # | 验收标准 | 锚点/断言 |
|---|---------|----------|
| AC-15 | 30 回合静息 trace（组合 WMatrixBuilder.Build + CorticalBias.Compute(baseline) + WcDynamics.Step；tone=baseline、s=0、a(0)=0.10） | 收敛断言：round 30 与 round 29 max\|Δ\| < 1e-5（python 预览 round 10 即 7e-7）；active（W 行非零，从 W 推导）∈ [0.53, 0.78]（预览 [0.535174, 0.771229]——经本 spec 复核；任务issue 预览行原为全 69 节点口径已修正，见 audit/report.md F3-data）；排除节点 a == σ(b_j) 三组：b=0 → 0.3775407 / b=0.7 → 0.5498340 / b=0.9 → 0.5986877（1e-5）；**ITestOutputHelper 输出 69 节点实测值表**（供 M1 文档写回） |

M1 文档写回义务（工作issue 完成标准之一）：实测值写入 [运行时状态模型](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) §7.3（静息态叙述）+ [回合战斗流程](../../../规则/技能树系统/回合战斗流程.md) §3.3（静息基线 0.10 叙述）+ [皮层动力学-通用层](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E7%9A%AE%E5%B1%82%E5%8A%A8%E5%8A%9B%E5%AD%A6-%E9%80%9A%E7%94%A8%E5%B1%82.md) §4.2/§4.3（σ(0) 笔误 + Euler 叙述）——plan §十三-8 清扫清单 + csharp-wc-dynamics sign-off 结转 #4 一并执行。

## 七、本 spec 自检清单

1. 数学公式逐项对照——解析解与 plan §4.3 逐字一致；b_j 公式与运行时状态模型 §5.6 逐字一致；clip [0,1]/[0,2] 来源 §5.2/§7.2
2. 数值断言全部实测——AC 锚点全部来自任务issue「数据实测」表（python 实测），无凭记忆数字
3. 行序契约明确——输出行序 = Wsensory.RegionIds（csharp-wmatrix spec Step 1），b_j 与 WMatrix 行对齐可直接消费
4. 接口注释先行——两个 XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差（「设计两次」约束）
5. 边界值覆盖——δ=0 / 正负大 δ / back-to-back / 排除节点接收 b_j / 零广播节点 / clamp 两向 / tone 极值输入 / CorticalBias 契约防御（null / 未命中 / Silent）
6. 确定性——纯函数无静态状态（AC-8 实证）
7. 偏差声明完整——B1（签名加参）/B2（解析解）/B3（值域 [0,1]）/B4（M1 预测修正）实现注释逐条对应
8. Δ=1.0 复用漂移注——ToneUpdater 常量注释显式引用 csharp-wc-dynamics spec §四，不重新定义 Δ

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-13 | 初稿 | 任务issue 01（数据实测 + Q1/Q2 裁决 + D1-D12） | 全量审计 |
| v1.1 | 2026-08-13 | E1 §四 4.1 Δ 备注出处修正（运行时状态模型 §4.3 → 皮层动力学-通用层 §4.3）；E2 新增 AC-16（CorticalBias 契约防御）+ §七 第 5 项补契约防御；E3 AC-11 Shell→AccumbensShell；E4 AC-12 PAG→PeriaqueductalGray + Thalamus×2 明确为 Thalamus+ThalamusPulvinar；E5 AC-15 复核注释（任务issue 预览行口径修正）；F6 AC-13 边界 fid 注释（10 个 pre-clamp 恰 2.0）；任务issue 数据实测表 + map.md 同源数字一并修正 | 全量审计 conditional（0❌/5⚠️/1 refuted，[report.md](../../.scratch/csharp-tone/design/audit/report.md)） | Δ审计（变更章节 + 半径扩张） |

---
*创建: 2026-08-13 | 更新: 2026-08-13 | 版本: v1.1*
*关联: [csharp-engine plan](../../csharp-engine/design/plan.md) §4.3/§八/§十二-2/§十二-7, [任务issue 01](../../.scratch/csharp-tone/design/issues/01-tone-spec.md), [运行时状态模型](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) §5, [csharp-wc-dynamics spec](../../csharp-wc-dynamics/design/spec.md) §四*

## 参数速查表

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| 回合时长 | Δ | 1.0 | csharp-wc-dynamics spec §四 |
| tone 时间常数 | τ_NE / τ_VTA / τ_SNc / τ_5HT | 0.5 / 0.3 / 0.8 / 1.5 | 运行时状态模型 §5.3 |
| tone 基线 | b_NE / b_VTA / b_SNc / b_5HT | 0.3 / 0.4 / 0.5 / 0.5 | 运行时状态模型 §5.4 |
| δ 缩放因子 | δ_scale | 0.3 [NEW] | CalibrationConfig.DeltaScale（plan §七） |
| role 权重 | w_active / w_modulating | 1.0 / 0.5 | 运行时状态模型 §5.6 |
| b_j 值域 | — | [0, 2] | 运行时状态模型 §7.2 |
