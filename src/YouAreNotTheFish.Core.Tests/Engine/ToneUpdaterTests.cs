using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// ToneUpdater spec@v1.1（.scratch/csharp-tone/design/spec.md）§六 AC-1~AC-8。
/// 测试侧约定（wmatrix 结转 #1）：锚点一律 MathF 现算（1e-5 容差）或逐位比较，不裸写字面量。
/// </summary>
public class ToneUpdaterTests
{
    /// <summary>baseline tone（运行时状态模型 §5.4）。</summary>
    private static ToneState Baseline() => new()
    {
        Ne = 0.3f,
        DaVta = 0.4f,
        DaSnc = 0.5f,
        Ht5 = 0.5f,
    };

    /// <summary>δ_scale=0.3 默认配置（CalibrationConfig.DeltaScale，plan §七 [NEW]）。</summary>
    private static CalibrationConfig Default() => CalibrationConfig.Default;

    /// <summary>指定下标的单脉冲 delta（其余分量 0）。</summary>
    private static float[] Pulse(int index, float value)
    {
        var d = new float[4];
        d[index] = value;
        return d;
    }

    /// <summary>测试侧解析解（镜像 spec §三公式）：baseline + δ_eff + (tone − baseline − δ_eff)·e^(−Δ/τ)，Δ=1.0。</summary>
    private static float Expected(float current, float rawDelta, float scale, float baseline, float tau)
    {
        float deltaEff = rawDelta * scale;
        float decay = MathF.Exp(-1f / tau);
        return Math.Clamp(baseline + deltaEff + (current - baseline - deltaEff) * decay, 0f, 1f);
    }

    /// <summary>绝对容差 1e-5 断言（spec §六：标注「逐位」者精确相等，其余 1e-5f）。</summary>
    private static void AssertApprox(float expected, float actual, string what)
    {
        Assert.True(Math.Abs(expected - actual) <= 1e-5f,
            $"{what}: 期望 {expected}，实际 {actual}，偏差 {Math.Abs(expected - actual)}");
    }

    // ---- AC-1：形状与不可变性 ----

    [Fact]
    public void Step_ReturnsNewState_AndDoesNotMutateInputs()
    {
        var tone = Baseline();
        var delta = Pulse(0, 1f);
        var cfg = Default();
        var deltaCopy = (float[])delta.Clone();

        var result = ToneUpdater.Step(tone, delta, cfg);

        Assert.NotSame(tone, result);
        Assert.Equal(deltaCopy, delta); // delta 数组不突变
        Assert.Equal(0.3f, tone.Ne); // tone 不可变（record）
        // 输出与输入解耦：改动 delta 后再算一次，结果一致
        delta[0] = 99f;
        var result2 = ToneUpdater.Step(tone, Pulse(0, 1f), cfg);
        Assert.Equal(result, result2);
    }

    // ---- AC-2：δ=0 回基线衰减 ----

    [Fact]
    public void Step_ZeroDelta_DecaysTowardBaseline()
    {
        var cfg = Default();
        var zero = new float[4];

        // NE from 0.8：解析解 0.367667642（1e-5）
        var high = new ToneState { Ne = 0.8f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.5f };
        var r = ToneUpdater.Step(high, zero, cfg);
        AssertApprox(Expected(0.8f, 0f, 0.3f, 0.3f, 0.5f), r.Ne, "NE 0.8 δ=0");

        // NE from baseline：不动点精确相等（current − baseline = 0 精确，decay 项为 0）
        var atBaseline = ToneUpdater.Step(Baseline(), zero, cfg);
        Assert.Equal(0.3f, atBaseline.Ne);
        Assert.Equal(0.4f, atBaseline.DaVta);
        Assert.Equal(0.5f, atBaseline.DaSnc);
        Assert.Equal(0.5f, atBaseline.Ht5);
    }

    // ---- AC-3：单脉冲 4 tone 锚点（δ_scale=0.3）----

    [Theory]
    [InlineData(0, 0.3f, 0.5f)] // NE 0.3 +d1 → 0.559399415
    [InlineData(1, 0.4f, 0.3f)] // DA_VTA 0.4 +d1 → 0.689297802
    [InlineData(2, 0.5f, 0.8f)] // DA_SNc 0.5 +d1 → 0.714048561
    [InlineData(3, 0.5f, 1.5f)] // 5HT 0.5 +d1 → 0.645974864
    public void Step_SinglePulse_MatchesAnalyticAnchor(int index, float baseline, float tau)
    {
        var tone = Baseline();
        var result = ToneUpdater.Step(tone, Pulse(index, 1f), Default());

        float expected = Expected(baseline, 1f, 0.3f, baseline, tau);
        float actual = index switch
        {
            0 => result.Ne,
            1 => result.DaVta,
            2 => result.DaSnc,
            _ => result.Ht5,
        };
        AssertApprox(expected, actual, $"分量 {index} +d1");
    }

    // ---- AC-4：δ_scale 杠杆 + DA 饱和边界 ----

    [Fact]
    public void Step_DeltaScaleOne_DemonstratesSaturationBoundary()
    {
        var cfg = new CalibrationConfig { DeltaScale = 1.0f };

        // 5HT 0.5 +d1 → 1.5 − e^(−1/1.5) ≈ 0.986582881，不 clip
        var r5 = ToneUpdater.Step(Baseline(), Pulse(3, 1f), cfg);
        AssertApprox(Expected(0.5f, 1f, 1f, 0.5f, 1.5f), r5.Ht5, "5HT Δscale=1 +d1");
        Assert.True(r5.Ht5 < 1f);

        // DA_VTA 0.4 +d1 → pre-clamp 1.364326 > 1 被 clip 到 1.0（无杠杆时单次命中即饱和）
        // 注：此处用无 clamp 的原始公式（Expected 助手含 clamp，会掩盖超界值）
        float preClamp = 0.4f + 1f + (0.4f - 0.4f - 1f) * MathF.Exp(-1f / 0.3f);
        Assert.True(preClamp > 1f, "pre-clamp 应超界（1.364326）");
        var rDa = ToneUpdater.Step(Baseline(), Pulse(1, 1f), cfg);
        Assert.Equal(1f, rDa.DaVta);
    }

    // ---- AC-5：大 δ clip [0,1] ----

    [Fact]
    public void Step_LargeDelta_ClipsToUnitRange()
    {
        var cfg = Default();

        // NE 0.3 +d10 → 3.3 − 3k ≈ 2.89 超界 → 1.0
        Assert.Equal(1f, ToneUpdater.Step(Baseline(), Pulse(0, 10f), cfg).Ne);

        // 5HT 1.0 −d10 → −2.5 + 3.5k ≈ −0.70 超界 → 0.0
        var high = new ToneState { Ne = 0.3f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 1.0f };
        Assert.Equal(0f, ToneUpdater.Step(high, Pulse(3, -10f), cfg).Ht5);

        // 极端输入扫描：输出全部 ∈ [0,1] 有限无 NaN
        var extreme = new ToneState { Ne = 0f, DaVta = 1f, DaSnc = 0f, Ht5 = 1f };
        var r = ToneUpdater.Step(extreme, new[] { 10f, -10f, 10f, -10f }, cfg);
        Assert.All(new[] { r.Ne, r.DaVta, r.DaSnc, r.Ht5 }, v =>
        {
            Assert.True(float.IsFinite(v), "输出必须有限");
            Assert.InRange(v, 0f, 1f);
        });
    }

    // ---- AC-6：连续双脉冲 back-to-back ----

    [Fact]
    public void Step_BackToBack_MatchesAnalyticSequence()
    {
        var cfg = Default();
        var tone = Baseline();

        var r1 = ToneUpdater.Step(tone, Pulse(0, 1f), cfg); // 0.559399415
        AssertApprox(Expected(0.3f, 1f, 0.3f, 0.3f, 0.5f), r1.Ne, "NE 第一脉冲");

        var r2 = ToneUpdater.Step(r1, Pulse(0, 1f), cfg); // 0.594505308
        AssertApprox(Expected(r1.Ne, 1f, 0.3f, 0.3f, 0.5f), r2.Ne, "NE 第二脉冲");

        // 任务issue D5：连续两次 Step ≠ 聚合一次 Step（数学不等价）——聚合一次为另一个值
        float aggregated = Expected(0.3f, 2f, 0.3f, 0.3f, 0.5f);
        Assert.True(Math.Abs(aggregated - r2.Ne) > 1e-5f,
            $"聚合一次 {aggregated} 不应等于 back-to-back {r2.Ne}");
    }

    // ---- AC-7：契约防御 ----

    [Fact]
    public void Step_NullArguments_Throw()
    {
        var delta = new float[4];
        Assert.Throws<ArgumentNullException>(() => ToneUpdater.Step(null!, delta, Default()));
        Assert.Throws<ArgumentNullException>(() => ToneUpdater.Step(Baseline(), null!, Default()));
        Assert.Throws<ArgumentNullException>(() => ToneUpdater.Step(Baseline(), delta, null!));
    }

    [Theory]
    [InlineData(0)]
    [InlineData(3)]
    [InlineData(5)]
    public void Step_WrongDeltaLength_Throws(int length)
    {
        Assert.Throws<ArgumentException>(
            () => ToneUpdater.Step(Baseline(), new float[length], Default()));
    }

    // ---- AC-8：确定性 ----

    [Fact]
    public void Step_IsDeterministic()
    {
        var tone = new ToneState { Ne = 0.6f, DaVta = 0.9f, DaSnc = 0.2f, Ht5 = 0.8f };
        var delta = new[] { 1.5f, -2f, 0.25f, 3f };

        var r1 = ToneUpdater.Step(tone, delta, Default());
        var r2 = ToneUpdater.Step(tone, delta, Default());

        Assert.Equal(r1, r2); // record 结构比较 + float.Equals 逐位
        Assert.Equal(r1.Ne, r2.Ne);
        Assert.Equal(r1.DaVta, r2.DaVta);
        Assert.Equal(r1.DaSnc, r2.DaSnc);
        Assert.Equal(r1.Ht5, r2.Ht5);
    }
}
