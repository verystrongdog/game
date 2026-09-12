using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// SpeedScoreCalculator spec@v1.1（../../../规格/引擎/csharp-speed.md）§六 AC-1~AC-14（AC-15 见 Types/SpeedComponentsTests）。
/// 测试侧约定（wmatrix 结转 #1）：锚点一律经行序解析（RowOf），不裸写下标——dk/fid 命名陷阱。
/// 锚点来源：spec §六（任务issue 01 实测表 + Δ审计独立复算）；「逐位」标注者精确相等，其余 1e-5。
/// 无首回合特判（B1）——静息锚点直算即静息值。
/// </summary>
public class SpeedScoreCalculatorTests
{
    // ---- 数据加载（复用 CstcGatingTests 的 FindDataDir 候选路径模式）----

    private static readonly string[] DataDirCandidates =
    [
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..", "data"),
        Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..", "data")),
        "/home/dog/game/data",
    ];

    private static string FindDataDir()
    {
        foreach (var dir in DataDirCandidates)
        {
            if (File.Exists(Path.Combine(dir, "brain_regions.json"))) return dir;
        }

        throw new DirectoryNotFoundException(
            "Cannot find data/ directory. Tried:\n" + string.Join("\n", DataDirCandidates));
    }

    private static readonly Lazy<GameData> Data =
        new(() => GameDataLoader.LoadAll(FindDataDir()));

    private static readonly Lazy<SpeedScoreCalculator> Calc =
        new(() => new SpeedScoreCalculator(Data.Value, CalibrationConfig.Default));

    // ---- 合成输入助手 ----

    private static float[] Fill(float v) => Enumerable.Repeat(v, 69).ToArray();

    private static float[] Fill5(float v) => [v, v, v, v, v];

    private static GurneyState ZeroGurney() =>
        new(Fill5(0f), Fill5(0f), Fill5(0f));

    /// <summary>任意 salience（察觉/执行测试用——决断无关的场合）。</summary>
    private static LoopSalience AnySalience() =>
        new(new LoopValue(0.5f, 0f), new LoopValue(0.5f, 0f), new LoopValue(0.5f, 0f));

    /// <summary>fid → canonical 行（经 Wsensory.RegionIds 解析，不裸写下标——结转 #1）。</summary>
    private static Dictionary<string, int> RowOf()
    {
        var regionIds = Data.Value.Wsensory.RegionIds;
        var rowOf = new Dictionary<string, int>(regionIds.Length);
        for (int i = 0; i < regionIds.Length; i++)
        {
            rowOf[regionIds[i]] = i;
        }

        return rowOf;
    }

    /// <summary>绝对容差 1e-5 断言（spec §六：标注「逐位」者精确相等，其余 1e-5）。</summary>
    private static void AssertApprox(float expected, float actual, string what)
    {
        Assert.True(Math.Abs(expected - actual) <= 1e-5f,
            $"{what}: 期望 {expected}，实际 {actual}，偏差 {Math.Abs(expected - actual)}");
    }

    // ---- AC-1 构造解析 ----

    [Fact]
    public void Constructor_ResolvesFiveRows_MatchesRegionIds()
    {
        var rowOf = RowOf();
        IReadOnlyList<int> rows = Calc.Value.PerceptionRows;

        Assert.Equal(4, rows.Count);
        Assert.Equal(rowOf["Pericalcarine"], rows[0]);
        Assert.Equal(rowOf["TransverseTemporal"], rows[1]);
        Assert.Equal(rowOf["Insula"], rows[2]);
        Assert.Equal(rowOf["AnteriorCingulateCortex"], rows[3]);
        Assert.Equal(rowOf["Precentral"], Calc.Value.PrecentralRow);
    }

    [Fact]
    public void Constructor_MissingFid_ThrowsKeyNotFound()
    {
        // 名删除哨兵（spec §六 AC-1）：合成 Wsensory 缺 Insula；其余 GameData 组件不消费 → null! 占位
        var wsensory = new WsensoryMatrix
        {
            RegionIds = ["Pericalcarine", "TransverseTemporal", "AnteriorCingulateCortex", "Precentral"],
        };
        var data = new GameData(null!, null!, wsensory, null!, null!, null!, null!, null!);

        Assert.Throws<KeyNotFoundException>(() => new SpeedScoreCalculator(data, CalibrationConfig.Default));
    }

    // ---- AC-2 察觉无回落 ----

    [Fact]
    public void Perception_AllAboveThreshold_NoFallback_Mean()
    {
        var c = Calc.Value.ComputeComponents(new WcState(Fill(0.7f)), AnySalience(), ZeroGurney(), false);
        AssertApprox(0.7f, c.Perception, "全 0.7 察觉");
    }

    [Fact]
    public void Perception_MixedAboveThreshold_BitEquals0565f()
    {
        // 结转 #5：不变式 = 结果与 0.565f 字面量逐位相等（十进制 0.565 非 f32 精确可表示）
        // f32 结合序陷阱：0.16 须放引擎求和序最后一位（ACC）——锚点按 (0.7+0.7+0.7+0.16)/4 实测
        var rowOf = RowOf();
        var arr = Fill(0.7f);
        arr[rowOf["AnteriorCingulateCortex"]] = 0.16f;

        var c = Calc.Value.ComputeComponents(new WcState(arr), AnySalience(), ZeroGurney(), false);
        Assert.Equal(0.565f, c.Perception);
    }

    // ---- AC-3 察觉逐节点回落（4 常量逐节点单独钉住）----

    [Fact]
    public void Perception_PerNodeFallback_PinsEachConstant()
    {
        AssertPerceptionFallback("Pericalcarine", 0.68274397f);
        AssertPerceptionFallback("TransverseTemporal", 0.68290060f);
        AssertPerceptionFallback("Insula", 0.68319666f);
        AssertPerceptionFallback("AnteriorCingulateCortex", 0.6937933f);
    }

    private static void AssertPerceptionFallback(string fid, float expected)
    {
        var rowOf = RowOf();
        var arr = Fill(0.7f);
        arr[rowOf[fid]] = 0.05f;

        var c = Calc.Value.ComputeComponents(new WcState(arr), AnySalience(), ZeroGurney(), false);
        AssertApprox(expected, c.Perception, $"{fid} 回落锚点");
    }

    [Fact]
    public void Perception_AllBelowThreshold_AllFallback_RestingMean()
    {
        var c = Calc.Value.ComputeComponents(new WcState(Fill(0.05f)), AnySalience(), ZeroGurney(), false);
        AssertApprox(0.64263445f, c.Perception, "全回落 4 静息均值");
    }

    [Fact]
    public void Perception_ExactlyAtThreshold_NoFallback()
    {
        var rowOf = RowOf();
        var arr = Fill(0.7f);
        arr[rowOf["Pericalcarine"]] = 0.15f; // 恰好阈值 → 不回落（≥）

        var c = Calc.Value.ComputeComponents(new WcState(arr), AnySalience(), ZeroGurney(), false);
        AssertApprox((0.15f + 0.7f + 0.7f + 0.7f) / 4f, c.Perception, "端点 0.15 不回落");
    }

    // ---- AC-4 决断无回落 ----

    [Fact]
    public void Decision_MeanOfThreeLoops_NoFallback()
    {
        var salience = new LoopSalience(
            new LoopValue(0.665469f, 0f), new LoopValue(0.696963f, 0f), new LoopValue(0.692102f, 0f));

        var c = Calc.Value.ComputeComponents(new WcState(Fill(0f)), salience, ZeroGurney(), false);
        AssertApprox(0.68484467f, c.Decision, "决断静息锚");
    }

    [Fact]
    public void Decision_AllZero_NoFallback_Zero()
    {
        var zero = new LoopSalience(
            new LoopValue(0f, 0f), new LoopValue(0f, 0f), new LoopValue(0f, 0f));

        var c = Calc.Value.ComputeComponents(new WcState(Fill(0f)), zero, ZeroGurney(), false);
        AssertApprox(0f, c.Decision, "全 0 不回落");
    }

    // ---- AC-5/AC-6 执行与 M1 惩罚 ----

    [Fact]
    public void Execution_RestingAnchor_NoDefending()
    {
        var c = RestingExecutionState(isDefending: false);
        AssertApprox(0.80777383f, c.Execution, "执行静息锚");
    }

    [Fact]
    public void Execution_Defending_AppliesM1Penalty()
    {
        var defending = RestingExecutionState(isDefending: true);
        AssertApprox(0.70777383f, defending.Execution, "防御惩罚后执行");

        var free = RestingExecutionState(isDefending: false);
        AssertApprox(0.80777383f, free.Execution, "未防御不变");
    }

    /// <summary>执行静息锚状态：a(Precentral)=0.6306536、a_SD1=0.9848941（任务issue 实测 #5）。</summary>
    private static SpeedComponents RestingExecutionState(bool isDefending)
    {
        var rowOf = RowOf();
        var arr = Fill(0f);
        arr[rowOf["Precentral"]] = 0.6306536f;
        var gurney = new GurneyState([0.9848941f, 0f, 0f, 0f, 0f], Fill5(0f), Fill5(0f));

        return Calc.Value.ComputeComponents(new WcState(arr), AnySalience(), gurney, isDefending);
    }

    // ---- AC-7 加权合成（plan §4.5 三个 RED 用例）----

    [Fact]
    public void Score_RedCases_FromPlan()
    {
        var equal = new SpeedWeights(1f / 3f, 1f / 3f, 1f / 3f);
        AssertApprox(0.5f, Calc.Value.ComputeScore(new SpeedComponents(0.5f, 0.5f, 0.5f), equal), "RED1 等权");

        var w = new SpeedWeights(0.5f, 0.25f, 0.25f);
        AssertApprox(0.45f, Calc.Value.ComputeScore(new SpeedComponents(0.5f, 0.4f, 0.4f), w), "RED2 加权");

        AssertApprox(1.0f, Calc.Value.ComputeScore(new SpeedComponents(1f, 1f, 1f), equal), "RED3 满值");
    }

    // ---- AC-8 首回合静息 speed（B1 交付机制——静息状态直算，无特判）----

    [Fact]
    public void RestingState_ProducesRestingSpeed_NoSpecialCase()
    {
        var rowOf = RowOf();
        var arr = Fill(0f);
        arr[rowOf["Pericalcarine"]] = 0.6309757f;
        arr[rowOf["TransverseTemporal"]] = 0.6316023f;
        arr[rowOf["Insula"]] = 0.6327866f;
        arr[rowOf["AnteriorCingulateCortex"]] = 0.6751733f;
        arr[rowOf["Precentral"]] = 0.6306536f;
        var salience = new LoopSalience(
            new LoopValue(0.665469f, 0f), new LoopValue(0.696963f, 0f), new LoopValue(0.692102f, 0f));
        var gurney = new GurneyState([0.9848941f, 0f, 0f, 0f, 0f], Fill5(0f), Fill5(0f));

        var c = Calc.Value.ComputeComponents(new WcState(arr), salience, gurney, false);
        AssertApprox(0.64263445f, c.Perception, "察觉静息");
        AssertApprox(0.68484467f, c.Decision, "决断静息");
        AssertApprox(0.80777383f, c.Execution, "执行静息");
        AssertApprox(0.71175098f,
            Calc.Value.ComputeScore(c, new SpeedWeights(1f / 3f, 1f / 3f, 1f / 3f)), "首回合 speed（任务issue 实测 #6）");
    }

    // ---- AC-12 契约防御 ----

    [Fact]
    public void ContractDefenses_Throw()
    {
        var calc = Calc.Value;

        Assert.Throws<ArgumentNullException>(
            () => calc.ComputeComponents(null!, AnySalience(), ZeroGurney(), false));
        Assert.Throws<ArgumentNullException>(
            () => calc.ComputeComponents(new WcState(Fill(0f)), null!, ZeroGurney(), false));
        Assert.Throws<ArgumentNullException>(
            () => calc.ComputeComponents(new WcState(Fill(0f)), AnySalience(), null!, false));

        foreach (var len in new[] { 0, 68, 70 })
        {
            Assert.Throws<ArgumentException>(() => calc.ComputeComponents(
                new WcState(new float[len]), AnySalience(), ZeroGurney(), false));
        }

        foreach (var len in new[] { 0, 4 })
        {
            var bad = new GurneyState(new float[len], Fill5(0f), Fill5(0f));
            Assert.Throws<ArgumentException>(() => calc.ComputeComponents(
                new WcState(Fill(0f)), AnySalience(), bad, false));
        }

        Assert.Throws<ArgumentNullException>(
            () => calc.ComputeScore(null!, new SpeedWeights(1f / 3f, 1f / 3f, 1f / 3f)));
        Assert.Throws<ArgumentNullException>(
            () => calc.ComputeScore(new SpeedComponents(0f, 0f, 0f), null!));
    }

    // ---- AC-13 输入不可变 + 确定性 ----

    [Fact]
    public void InputsImmutable_OutputDeterministic()
    {
        var rowOf = RowOf();
        var arr = Fill(0.7f);
        arr[rowOf["Insula"]] = 0.05f;
        var a = new WcState(arr);
        var gurney = new GurneyState([0.8f, 0.1f, 0.1f, 0.1f, 0.1f], Fill5(0.1f), Fill5(0.1f));
        var salience = AnySalience();

        var snapA = (float[])a.A.Clone();
        var snapG = (float[])gurney.Somatic.Clone();

        var c1 = Calc.Value.ComputeComponents(a, salience, gurney, true);
        var c2 = Calc.Value.ComputeComponents(a, salience, gurney, true);

        Assert.True(c1 == c2, "重复调用逐位相等");
        Assert.Equal(snapA, a.A);
        Assert.Equal(snapG, gurney.Somatic);
    }

    // ---- AC-14 边界 ----

    [Fact]
    public void Boundaries_ExecutionAndDecision()
    {
        var rowOf = RowOf();

        // a_SD1=0 → 执行 = mean(a(Precentral), 0)
        var arr = Fill(0f);
        arr[rowOf["Precentral"]] = 0.6f;
        var cZero = Calc.Value.ComputeComponents(
            new WcState(arr), AnySalience(), ZeroGurney(), false);
        AssertApprox(0.3f, cZero.Execution, "a_SD1=0 执行");

        // 完整输入组合：a(Precentral)=1.0 ∧ Somatic[0]=2.0 ∧ 未防御 → 1.5
        // （Somatic[0]=2.0 为合成状态 c=1.0 ∧ DA=1.0 使 u_SD1 达解析界上限——spec §二 2.1）
        var arrMax = Fill(0f);
        arrMax[rowOf["Precentral"]] = 1.0f;
        var gurneyMax = new GurneyState([2.0f, 0f, 0f, 0f, 0f], Fill5(0f), Fill5(0f));
        var cMax = Calc.Value.ComputeComponents(
            new WcState(arrMax), AnySalience(), gurneyMax, false);
        AssertApprox(1.5f, cMax.Execution, "执行上限 1.5");
    }
}
