using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// ThreatJudge 单元测试——神经模型的「外部威胁判断」读法验证。
/// 锚点：脑功能层级模型 §三 3.3（阈值型恐慌触发）+ §四 4.1（杏仁核降低 PAG 防御触发阈值）。
/// canonical 69 行序索引来自 data/connectivity/W_sensory.json rows：Amygdala=2, PeriaqueductalGray=40。
/// </summary>
public class ThreatJudgeTests
{
    private const int AmygdalaIdx = 2;
    private const int PagIdx = 40;

    // 构造一个 69 位都能写的 state，只把威胁脑区置于指定激活。
    private static WcState ThreatState(float amygdala, float pag)
    {
        var a = new float[69];
        a[AmygdalaIdx] = amygdala;
        a[PagIdx] = pag;
        return new WcState(a);
    }

    private static ThreatJudge Judge() => new(AmygdalaIdx, PagIdx);

    // ---- 威胁评分（双通道混合，各 0.5）----

    [Fact]
    public void ThreatScore_HalfHalfBlend()
    {
        // score = 0.5×amyg + 0.5×pag
        Assert.Equal(0.5f, Judge().Evaluate(ThreatState(0.6f, 0.4f)).ThreatScore, 3);
        Assert.Equal(0.95f, Judge().Evaluate(ThreatState(0.9f, 1.0f)).ThreatScore, 3);
        Assert.Equal(0.0f, Judge().Evaluate(ThreatState(0f, 0f)).ThreatScore, 3);
    }

    [Fact]
    public void ThreatScore_MonotonicInPag()
    {
        // PAG 越高 → 威胁评分越高（其余相同）
        var low = Judge().Evaluate(ThreatState(0.3f, 0.2f)).ThreatScore;
        var high = Judge().Evaluate(ThreatState(0.3f, 0.8f)).ThreatScore;
        Assert.True(high > low, $"PAG 升高应抬升威胁评分（low={low}, high={high}）");
    }

    [Fact]
    public void ThreatScore_ClampedToUnitInterval()
    {
        // 输入越界（>1/<0 非契约输入），防御性 Clamp01 保证评分 ∈ [0,1]
        var a = new float[69];
        a[AmygdalaIdx] = 2.0f;
        a[PagIdx] = -0.5f;
        var v = Judge().Evaluate(new WcState(a));
        Assert.InRange(v.ThreatScore, 0f, 1f);
    }

    // ---- 恐慌触发（阈值型）----

    [Fact]
    public void Panic_HighPagTriggers()
    {
        // 杏仁核=0 → 有效阈值 = 基础阈值 0.65；PAG=0.8 ≥ 0.65 → 触发
        var v = Judge().Evaluate(ThreatState(0f, 0.80f));
        Assert.True(v.PanicTriggered);
        Assert.Equal(0.65f, v.EffectiveThreshold, 3);
    }

    [Fact]
    public void Panic_LowPagDoesNotTrigger()
    {
        // PAG=0.4 < 有效阈值 → 不触发
        var v = Judge().Evaluate(ThreatState(0.1f, 0.40f));
        Assert.False(v.PanicTriggered);
    }

    [Fact]
    public void Panic_AmygdalaLowersThreshold()
    {
        // 同一 PAG=0.55：杏仁核低（阈值 0.65-0.02=0.63）→ 不触发；杏仁核高（阈值降到 0.65-0.18=0.47）→ 触发。
        // 验证「恐惧条件化降低 PAG 防御触发阈值」（脑功能层级模型 §四 4.1）。
        var lowAmyg = Judge().Evaluate(ThreatState(0.1f, 0.55f));
        var highAmyg = Judge().Evaluate(ThreatState(0.9f, 0.55f));

        Assert.False(lowAmyg.PanicTriggered, $"杏仁核低时 PAG=0.55 < 0.63，不应恐慌（实际有效阈值 {lowAmyg.EffectiveThreshold}）");
        Assert.True(highAmyg.PanicTriggered, $"杏仁核高时阈值降至 0.47，PAG=0.55 应触发恐慌（实际有效阈值 {highAmyg.EffectiveThreshold}）");
        Assert.True(highAmyg.EffectiveThreshold < lowAmyg.EffectiveThreshold,
            "杏仁核升高应降低有效阈值");
    }

    [Fact]
    public void Panic_ThresholdFlooredAtZeroPointThree()
    {
        // 杏仁核=1.0：阈值 = 0.65 - 0.2×1.0 = 0.45 → 落到 floor 0.30（实测计算路径）
        var v = Judge().Evaluate(ThreatState(1.0f, 0.10f));
        // 0.65 - 0.2×1.0 = 0.45 > 0.30，未到 floor
        Assert.Equal(0.45f, v.EffectiveThreshold, 3);

        // 极端：杏仁核=1.0，PAG=0.35 → 若 0.35 ≥ 0.45 则不触发；验证边界在阈值下不触发
        Assert.False(Judge().Evaluate(ThreatState(1.0f, 0.35f)).PanicTriggered);
    }

    // ---- 索敌优先级 ----

    [Fact]
    public void TargetPriority_EqualsThreatScore()
    {
        var v = Judge().Evaluate(ThreatState(0.6f, 0.8f));
        Assert.Equal(v.ThreatScore, v.TargetPriority, 3);
    }

    // ---- 索引校验 ----

    [Theory]
    [InlineData(-1, PagIdx)]
    [InlineData(69, PagIdx)]
    [InlineData(AmygdalaIdx, -1)]
    [InlineData(AmygdalaIdx, 69)]
    public void Constructor_RejectsOutOfRange(int amygdala, int pag)
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => new ThreatJudge(amygdala, pag));
    }

    [Fact]
    public void Evaluate_RejectsWrongLength()
    {
        Assert.Throws<ArgumentException>(() => Judge().Evaluate(new WcState(new float[3])));
    }

    // ---- 从真实数据解析索引 ----

    private static readonly string[] DataDirCandidates =
    [
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "data"),
        Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "data")),
        "/home/dog/game/data",
    ];

    private static string FindDataDir()
    {
        foreach (var dir in DataDirCandidates)
            if (File.Exists(Path.Combine(dir, "brain_regions.json"))) return dir;
        throw new DirectoryNotFoundException("Cannot find data/ directory.");
    }

    private static GameData Data() => GameDataLoader.LoadAll(FindDataDir());

    [Fact]
    public void FromGameData_ResolvesThreatRegions()
    {
        // data/connectivity/W_sensory.json rows 序：Amygdala=2, PeriaqueductalGray=40
        var judge = ThreatJudge.FromGameData(Data());
        Assert.Equal(AmygdalaIdx, judge.AmygdalaIndex);
        Assert.Equal(PagIdx, judge.PagIndex);
    }

    [Fact]
    public void FromGameData_MissingRegionThrows()
    {
        // 空 RegionIds → 抛错；缺威胁脑区 → 抛错
        var ws = new WsensoryMatrix { RegionIds = [] };
        var gd = Data() with { Wsensory = ws };
        Assert.Throws<InvalidOperationException>(() => ThreatJudge.FromGameData(gd));
    }
}
