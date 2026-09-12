using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// 脑干 tone 单步动力学（csharp-engine plan §十一 step 5）——spec@v1.1（../../../规格/引擎/csharp-tone.md）。
/// 职责：对 4 个 tone 应用解析指数解 + clip（运行时状态模型 §5.2/§7.1 步骤 4）。
/// 纯函数：无 static 可变状态、无 RNG、同输入同输出（AC-8）。
/// 来源：csharp-engine plan §4.3；运行时状态模型 §5.2-5.4。
/// </summary>
public static class ToneUpdater
{
    /// <summary>回合时长 Δ = 1.0 秒（皮层动力学-通用层 §4.3；spec@v1.1 §四 4.1）。
    /// 漂移风险注（wc-dynamics 结转 F8）：WcDynamics 与 step 6（Gurney k=25 隐含 Δ）复用同一 Δ——
    /// 本常量引用 csharp-wc-dynamics spec §四 常量来源，不重新定义。</summary>
    private const float DeltaSeconds = 1.0f;

    /// <summary>τ_tone（秒）：NE 0.5 / DA_VTA 0.3 / DA_SNc 0.8 / 5HT 1.5——运行时状态模型 §5.3（spec@v1.1 §四 4.1）。</summary>
    private const float TauNe = 0.5f;
    private const float TauDaVta = 0.3f;
    private const float TauDaSnc = 0.8f;
    private const float TauHt5 = 1.5f;

    /// <summary>baseline tone：NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5——运行时状态模型 §5.4（spec@v1.1 §四 4.1）。</summary>
    private const float BaselineNe = 0.3f;
    private const float BaselineDaVta = 0.4f;
    private const float BaselineDaSnc = 0.5f;
    private const float BaselineHt5 = 0.5f;

    /// <summary>
    /// 单步更新 4 个脑干 tone（解析解 + clip——偏差 B2/B3）。
    /// 公式：tone' = clip(baseline_t + δ_eff + (tone_t − baseline_t − δ_eff)·e^(−Δ/τ_t), 0, 1)，
    /// 其中 δ_eff = δ × cfg.DeltaScale（偏差 B1：δ_scale 在 Step 内部应用——任务issue Q2 裁决）。
    /// 输入：tone 当前状态（值域 [0,1]，ToneState 契约，不校验——spec §五 C5 姿态）；
    ///       delta float[4]（未缩放原始 δ，分量序 NE/DA_VTA/DA_SNc/5HT，§5.3 表序）；cfg 校准配置。
    /// 输出：新 ToneState（输入不突变）。
    /// 异常：tone/delta/cfg 为 null → ArgumentNullException；delta.Length ≠ 4 → ArgumentException。
    /// 未定义行为：同窗口多事件 δ 聚合（Σ）与实时发射时序由调用方（step 9 EventProcessor）负责，
    ///   本方法只处理单次 δ（任务issue D5——连续 Step ≠ 聚合一次，语义归属唯一）。
    /// 来源：csharp-engine plan §4.3；运行时状态模型 §5.2-5.4；spec@v1.1 §三。
    /// </summary>
    public static ToneState Step(ToneState tone, float[] delta, CalibrationConfig cfg)
    {
        ArgumentNullException.ThrowIfNull(tone);
        ArgumentNullException.ThrowIfNull(delta);
        ArgumentNullException.ThrowIfNull(cfg);

        if (delta.Length != 4)
        {
            throw new ArgumentException($"delta 长度必须为 4（当前 {delta.Length}）", nameof(delta));
        }

        float scale = cfg.DeltaScale; // 偏差 B1：δ_scale 注入点（任务issue Q2 裁决 A）
        return new ToneState
        {
            Ne = Apply(tone.Ne, delta[0], scale, BaselineNe, TauNe),
            DaVta = Apply(tone.DaVta, delta[1], scale, BaselineDaVta, TauDaVta),
            DaSnc = Apply(tone.DaSnc, delta[2], scale, BaselineDaSnc, TauDaSnc),
            Ht5 = Apply(tone.Ht5, delta[3], scale, BaselineHt5, TauHt5),
        };
    }

    /// <summary>单分量解析解：baseline + δ_eff + (tone − baseline − δ_eff)·e^(−Δ/τ)，clip [0,1]（偏差 B3 值域）。</summary>
    private static float Apply(float current, float rawDelta, float scale, float baseline, float tau)
    {
        float deltaEff = rawDelta * scale;
        float decay = MathF.Exp(-DeltaSeconds / tau);
        float next = baseline + deltaEff + (current - baseline - deltaEff) * decay;
        return Math.Clamp(next, 0f, 1f);
    }
}
