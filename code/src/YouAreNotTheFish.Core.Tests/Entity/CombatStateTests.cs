using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Entity;

/// <summary>
/// CombatState spec@v1.2（../../../规格/引擎/csharp-flow.md）AC-1 部分 + 异常契约。
/// 锚点来源：csharp-tone AC-15 M1 实测（active 48 ∈ [0.535174, 0.771229]；排除 21 = σ(b_j) 三组）。
/// </summary>
public class CombatStateTests
{
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
            if (File.Exists(Path.Combine(dir, "brain_regions.json"))) return dir;
        throw new DirectoryNotFoundException("Cannot find data/ directory.");
    }

    private static GameData Data() => GameDataLoader.LoadAll(FindDataDir());

    private static ParticipantState Participant(float hp, float san) => ParticipantState.CreateDefault(hp, san);

    // ---- AC-1：创建 + 静息初始化 ----

    [Fact]
    public void Create_WcIsRestingFixedPoint()
    {
        var data = Data();
        var state = CombatState.Create(
            new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 }, data, CalibrationConfig.Default);

        var w = WMatrixBuilder.Build(data);
        var a = state.Participants[0].Wc.A;

        // active（W 行非零）节点 ∈ [0.535174, 0.771229]（M1 实测，csharp-tone AC-15）
        float min = float.MaxValue, max = float.MinValue;
        for (var i = 0; i < a.Length; i++)
        {
            var rowActive = false;
            for (var k = 0; k < w.W.GetLength(1); k++)
                if (w.W[i, k] != 0f) { rowActive = true; break; }
            if (!rowActive)
                continue;
            min = Math.Min(min, a[i]);
            max = Math.Max(max, a[i]);
        }
        Assert.InRange(min, 0.535f, 0.536f);
        Assert.InRange(max, 0.771f, 0.772f);

        // 排除节点 = σ(b_j) 三组（M1 实测：b=0→0.3775407 ×14 / b=0.7→0.5498340 ×3 / b=0.9→0.5986876 ×4）
        Assert.InRange(a[0], 0.37f, 0.60f); // CerebellumCortex（b=0.9 组——实测 0.5986876）

        // 结构断言
        Assert.Equal(0.3f, state.Participants[0].Tone.Ne);
        Assert.Equal(0, state.Round);
        Assert.Empty(state.History);
        Assert.Equal(69, state.SPending[0].Length);
        Assert.All(state.SPending, s => Assert.All(s, v => Assert.Equal(0f, v)));
        Assert.Equal(new[] { 1, 2 }, state.Teams);
    }

    [Fact]
    public void Create_TeamsMismatch_Throws()
    {
        Assert.Throws<ArgumentException>(() => CombatState.Create(
            new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1 }, Data(), CalibrationConfig.Default));
    }

    [Fact]
    public void Create_NullArgs_ThrowArgumentNull()
    {
        var data = Data();
        var states = new[] { Participant(50f, 80f) };
        Assert.Throws<ArgumentNullException>(() => CombatState.Create(null!, new[] { 1 }, data, CalibrationConfig.Default));
        Assert.Throws<ArgumentNullException>(() => CombatState.Create(states, null!, data, CalibrationConfig.Default));
        Assert.Throws<ArgumentNullException>(() => CombatState.Create(states, new[] { 1 }, null!, CalibrationConfig.Default));
        Assert.Throws<ArgumentNullException>(() => CombatState.Create(states, new[] { 1 }, data, null!));
    }

    // ---- Apply 方法族 ----

    [Fact]
    public void ApplyDamage_EventFieldCarry()
    {
        var data = Data();
        var state = CombatState.Create(new[] { Participant(15f, 60f) }, new[] { 1 }, data, CalibrationConfig.Default);
        state.ApplyDamage(0, 10f, 55f);
        Assert.Equal(10f, state.Participants[0].Hp);
        Assert.Equal(55f, state.Participants[0].San);
    }

    [Fact]
    public void TickWindow_CooldownTick_AndDefenseReset()
    {
        var data = Data();
        var state = CombatState.Create(new[] { Participant(15f, 60f) }, new[] { 1 }, data, CalibrationConfig.Default);
        state.ApplyDefense(0, true, 1);
        Assert.True(state.Participants[0].IsDefending);

        state.TickWindow(0);
        Assert.False(state.Participants[0].IsDefending); // Q3=A：窗口开始解除
        Assert.Equal(0, state.Participants[0].DefendCd); // CD tick 1→0
    }

    [Fact]
    public void AccumulateS_AddsToSlot()
    {
        var data = Data();
        var state = CombatState.Create(new[] { Participant(15f, 60f) }, new[] { 1 }, data, CalibrationConfig.Default);
        var s = new float[69];
        s[10] = 0.5f;
        state.AccumulateS(0, s);
        Assert.Equal(0.5f, state.SPending[0][10]);
        state.AccumulateS(0, s);
        Assert.Equal(1.0f, state.SPending[0][10]);
    }
}
