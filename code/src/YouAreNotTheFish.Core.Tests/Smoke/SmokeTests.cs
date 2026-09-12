using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Flow;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Smoke;

/// <summary>
/// csharp-smoke spec@v1.2.1 §五 AC-1~9：端到端完整战斗验证（plan §八 落地）。
/// 参与者：双方 NPC 自动（NpcActionProvider）+ HP 80/SAN 80 smoke 专用模板（保证 ≥10 回合窗口）。
/// 锚点来源：seed sweep 实测固定（seed=7——45 回合/物理事件/双防御回合/序变化全成立，spec §2.1 程序）+ M1 实测区间。
/// </summary>
public class SmokeTests
{
    private static readonly string[] DataDirCandidates =
    [
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..", "data"),
        Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..", "data")),
    ];

    private const ulong Seed = 7; // seed sweep 实测选定（spec §2.1 程序）

    private static string FindDataDir()
    {
        foreach (var dir in DataDirCandidates)
            if (File.Exists(Path.Combine(dir, "brain_regions.json"))) return dir;
        throw new DirectoryNotFoundException("Cannot find data/ directory.");
    }

    private static GameData Data() => GameDataLoader.LoadAll(FindDataDir());

    private static CombatState NewState() => CombatState.Create(
        new[] { ParticipantState.CreateDefault(80f, 80f), ParticipantState.CreateDefault(80f, 80f) },
        new[] { 1, 2 }, Data(), CalibrationConfig.Default);

    private static CombatContext Ctx() => new(new DeterministicRng(Seed), Data(), CalibrationConfig.Default);

    /// <summary>完整战斗（NPC vs NPC 全自动）——跑到 IsOver 或步数上限。返回含每回合 order 历史（AC-6 消费）。</summary>
    private static (CombatState State, TurnManager Tm, List<TurnResult> Results, List<int[]> OrderHistory) FullBattle(IActionProvider? provider = null)
    {
        var state = NewState();
        var tm = new TurnManager(Data(), CalibrationConfig.Default, provider ?? new NpcActionProvider());
        var ctx = Ctx();
        var results = new List<TurnResult>();
        var orderHistory = new List<int[]>();
        while (!tm.IsOver(state) && results.Count < 51)
        {
            results.Add(tm.StepRound(state, ctx));
            orderHistory.Add(tm.LastRoundOrder.ToArray()); // 每回合末读（StepRound 后有效，下回合覆盖）
        }
        return (state, tm, results, orderHistory);
    }

    /// <summary>0.1 网格检查（Round1 量化不变式——负值合法，spec AC-3）。</summary>
    private static bool OnGrid(float x) => Math.Abs(x * 10f - MathF.Round(x * 10f)) < 1e-4f;

    // ---- AC-1：完整战斗结束 ----

    [Fact]
    public void FullBattle_Ends_WithReason()
    {
        var (state, tm, results, _) = FullBattle();

        Assert.True(tm.IsOver(state));
        Assert.True(results.Count >= 1 && results.Count <= 51);
        Assert.Equal(results.Count, state.History.Count);
        // 结束原因 ∈ {全灭, 上限}
        var defeated = state.Teams.Distinct().Any(team =>
            Enumerable.Range(0, state.Participants.Count)
                .Where(p => state.Teams[p] == team)
                .All(p => state.Participants[p].Hp <= 0f || state.Participants[p].San <= 0f));
        Assert.True(defeated || state.Round >= CalibrationConfig.Default.MaxRounds);
    }

    // ---- AC-2：事件流 ----

    [Fact]
    public void FullBattle_HasPhysicalDamage_NonEmptyExceptDualDefend()
    {
        var (_, _, results, _) = FullBattle();
        var allEvents = results.SelectMany(r => r.Events).ToList();

        Assert.Contains(allEvents, e => e is PhysicalDamageEvent); // 伤害链生效
        // 除双防御回合（双方 defend → 零事件）外非空
        foreach (var r in results)
            if (r.Events.Count == 0)
                Assert.True(r.ParticipantSnapshots.All(p => p.IsDefending),
                    "零事件回合必须是双方防御（双防御豁免——spec §3.1）");
    }

    // ---- AC-3：HP/SAN 网格不变式 ----

    [Fact]
    public void FullBattle_HpSan_GridInvariant()
    {
        var (state, tm, results, _) = FullBattle();
        var ctx = Ctx();

        // 全程检查（含每回合中间态——用独立战斗逐步收集）
        var all = new List<(float Hp, float San, float HpMax, float SanMax)>();
        var s = NewState();
        var tm2 = new TurnManager(Data(), CalibrationConfig.Default, new NpcActionProvider());
        while (!tm2.IsOver(s) && all.Count < 51)
        {
            tm2.StepRound(s, ctx);
            foreach (var p in s.Participants)
                all.Add((p.Hp, p.San, p.HpMax, p.SanMax));
        }

        foreach (var (hp, san, hpMax, sanMax) in all)
        {
            Assert.True(OnGrid(hp), $"HP 非 0.1 网格: {hp}");
            Assert.True(OnGrid(san), $"SAN 非 0.1 网格: {san}");
            Assert.True(hp <= hpMax + 0.1f, $"HP 超上界: {hp} > {hpMax}"); // 0.1 网格容差
            Assert.True(san <= sanMax + 0.1f, $"SAN 超上界: {san} > {sanMax}");
            // 过杀负值合法（无 clamp——spec B4）
        }
        Assert.NotEmpty(all);
    }

    // ---- AC-4：tone 动态 ----

    [Fact]
    public void Tone_EventReceiver_DeviatesFromBaseline()
    {
        var (state, tm, results, _) = FullBattle();
        // ① 事件接收者 tone 偏离 baseline（任一参与者任一 tone 分量 |Δ| > 0.01）
        var baseline = new ToneState { Ne = 0.3f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.5f };
        var deviated = results.SelectMany(r => r.ParticipantSnapshots)
            .Any(p => Math.Abs(p.Tone.Ne - baseline.Ne) > 0.01f
                   || Math.Abs(p.Tone.DaVta - baseline.DaVta) > 0.01f
                   || Math.Abs(p.Tone.DaSnc - baseline.DaSnc) > 0.01f
                   || Math.Abs(p.Tone.Ht5 - baseline.Ht5) > 0.01f);
        Assert.True(deviated, "存在事件接收者 tone 偏离 baseline");
    }

    [Fact]
    public void Tone_WaitRound_DecaysTowardBaseline()
    {
        // ② 纯衰减观测：脚本化等待回合（(null,null)）后 tone 向 baseline 靠近（spec §3.1——审计 F1）
        var state = NewState();
        var tm = new TurnManager(Data(), CalibrationConfig.Default, new NpcActionProvider());
        var ctx = Ctx();
        // 先跑事件回合（NPC 自动）注入 tone 偏离
        for (var i = 0; i < 3; i++)
            tm.StepRound(state, ctx);
        var before = state.Participants[0].Tone;

        // 等待回合（WaitProvider——双方空声明 → 零事件 + Phase 1 纯衰减）
        var waitTm = new TurnManager(Data(), CalibrationConfig.Default, new WaitProviderForSmoke());
        waitTm.StepRound(state, ctx);
        var after = state.Participants[0].Tone;

        var baseline = new ToneState { Ne = 0.3f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.5f };
        Assert.True(DistToBaseline(after) < DistToBaseline(before), "等待回合后 tone 向 baseline 靠近（严格缩小）");

        static float DistToBaseline(ToneState t) =>
            Math.Abs(t.Ne - 0.3f) + Math.Abs(t.DaVta - 0.4f) + Math.Abs(t.DaSnc - 0.5f) + Math.Abs(t.Ht5 - 0.5f);
    }

    // ---- AC-5：gate 动态（v1.2.1 实测修正：热身收敛观测）----

    [Fact]
    public void Gate_WarmupConvergence()
    {
        // round 1 = 0.635 → round 2 = 1.0（热身瞬态——spec §3.1；事件驱动抑制在 demo 参数下不可观测，50/50 seed 实测）
        var state = NewState();
        var tm = new TurnManager(Data(), CalibrationConfig.Default, new NpcActionProvider());
        var ctx = Ctx();

        var r1 = tm.StepRound(state, ctx);
        foreach (var p in state.Participants)
        {
            Assert.InRange(p.Gates.GateSomatic, 0f, 1f);
            Assert.InRange(p.Gates.GateCognitive, 0f, 1f);
            Assert.InRange(p.Gates.GateLimbic, 0f, 1f);
            Assert.Equal(0.635f, p.Gates.GateSomatic, 3); // 热身首回合（cstc 实测）
        }

        var r2 = tm.StepRound(state, ctx);
        foreach (var p in state.Participants)
        {
            Assert.Equal(1.0f, p.Gates.GateSomatic, 5); // 收敛 1.0（静息）
            Assert.Equal(1.0f, p.Gates.GateCognitive, 5);
            Assert.Equal(1.0f, p.Gates.GateLimbic, 5);
        }
    }

    // ---- AC-6：速度序变化 ----

    [Fact]
    public void SpeedOrder_ChangesDuringBattle()
    {
        var (_, _, results, orderHistory) = FullBattle();
        Assert.True(results.Count >= 10, $"长战斗窗口不足: {results.Count} 回合");

        var first = orderHistory[0];
        Assert.True(orderHistory.Skip(1).Any(o => !o.SequenceEqual(first)),
            "速度序至少一次与首回合不同（a(t) 动态驱动）");
    }

    // ---- AC-7：静息→战斗 ----

    [Fact]
    public void InitialState_IsRestingFixedPoint()
    {
        var state = NewState();
        var w = WMatrixBuilder.Build(Data());
        var a = state.Participants[0].Wc.A;
        float min = float.MaxValue, max = float.MinValue;
        for (var i = 0; i < a.Length; i++)
        {
            var active = false;
            for (var k = 0; k < w.W.GetLength(1); k++)
                if (w.W[i, k] != 0f) { active = true; break; }
            if (!active) continue;
            min = Math.Min(min, a[i]);
            max = Math.Max(max, a[i]);
        }
        Assert.InRange(min, 0.535f, 0.536f); // M1 实测
        Assert.InRange(max, 0.771f, 0.772f);
    }

    // ---- AC-8：确定性 ----

    [Fact]
    public void Determinism_SameSeed_BitwiseIdentical()
    {
        (int Round, int EventCount, ParticipantState[] Final) Run()
        {
            var (state, tm, results, _) = FullBattle();
            return (state.Round, results.Sum(r => r.Events.Count), state.Participants.ToArray());
        }

        var a = Run();
        var b = Run();
        Assert.Equal(a.Round, b.Round);
        Assert.Equal(a.EventCount, b.EventCount);
        for (var p = 0; p < a.Final.Length; p++)
        {
            Assert.Equal(a.Final[p].Hp, b.Final[p].Hp);
            Assert.Equal(a.Final[p].San, b.Final[p].San);
            Assert.Equal(a.Final[p].Tone, b.Final[p].Tone);
            Assert.Equal(a.Final[p].Wc.A, b.Final[p].Wc.A);
        }
    }

    // ---- AC-9：NaN 毒化防御（全程）----

    [Fact]
    public void NoNaN_ThroughoutBattle()
    {
        var state = NewState();
        var tm = new TurnManager(Data(), CalibrationConfig.Default, new NpcActionProvider());
        var ctx = Ctx();
        var steps = 0;
        while (!tm.IsOver(state) && steps < 51)
        {
            tm.StepRound(state, ctx);
            steps++;
            foreach (var p in state.Participants)
            {
                Assert.True(float.IsFinite(p.Hp), $"HP 非有限: {p.Hp}");
                Assert.True(float.IsFinite(p.San), $"SAN 非有限: {p.San}");
                Assert.True(float.IsFinite(p.Tone.Ne) && float.IsFinite(p.Tone.DaVta)
                    && float.IsFinite(p.Tone.DaSnc) && float.IsFinite(p.Tone.Ht5), "tone 非有限");
                Assert.True(float.IsFinite(p.Gates.GateSomatic) && float.IsFinite(p.Gates.GateCognitive)
                    && float.IsFinite(p.Gates.GateLimbic), "gates 非有限");
            }
        }
        Assert.True(steps >= 1);
    }

    /// <summary>smoke 用等待 provider（双方空声明——spec §3.1 纯衰减观测）。</summary>
    private sealed class WaitProviderForSmoke : IActionProvider
    {
        public CombatAction GetAction(int participantIndex, CombatState state, CombatContext ctx) => new();
    }
}
