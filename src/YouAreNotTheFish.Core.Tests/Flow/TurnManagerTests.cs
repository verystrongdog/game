using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Flow;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Flow;

/// <summary>
/// TurnManager spec@v1.2 §三 3.4/3.5：五阶段管线（AC-2/3/6/7/8/9/10/12/13/14）。
/// 锚点来源：组件级已验证（WcDynamics/CstcGating/EventProcessor）+ 探针实测（静息/回合末合成值）。
/// </summary>
public class TurnManagerTests
{
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

    private static CombatState State2P() => CombatState.Create(
        new[] { ParticipantState.CreateDefault(50f, 80f), ParticipantState.CreateDefault(15f, 60f) },
        new[] { 1, 2 }, Data(), CalibrationConfig.Default);

    private static CombatContext Ctx(ulong seed = 42) => new(new DeterministicRng(seed), Data(), CalibrationConfig.Default);


    /// <summary>按参与者索引给行动的 provider（Func 版——防自打/双攻击者误用）。</summary>
    private sealed class FixedProvider(Func<int, CombatAction> selector) : IActionProvider
    {
        public CombatAction GetAction(int participantIndex, CombatState state, CombatContext ctx)
            => selector(participantIndex);
    }

    private static readonly CombatAction Wait = new(); // (null,null) 空声明
    private static TurnManager Tm(CombatAction action) => Tm(_ => action);
    private static TurnManager Tm(Func<int, CombatAction> selector) => new(Data(), CalibrationConfig.Default, new FixedProvider(selector));

    private static readonly CombatAction P0Attacks = new()
    {
        M1 = new ActionSlot { Kind = ActionKind.PhysicalAttack, TargetId = 1 },
        Order = ChannelOrder.M1First,
    };

    // ---- AC-2：Phase 1 情境更新（零事件回合）----

    [Fact]
    public void ZeroEventRound_Phase1Chain_ToneDecayBaseline()
    {
        var state = State2P();
        var tm = Tm(Wait);
        var before = state.Participants[0].Wc.A;
        var tr = tm.StepRound(state, Ctx());

        Assert.Equal(1, state.Round);
        Assert.Empty(tr.Events);
        Assert.Single(state.History);

        // ① baseline 输入 → tone 逐位不变（衰减恒等——Δ审计 Δ-05）
        Assert.Equal(0.3f, state.Participants[0].Tone.Ne);
        Assert.Equal(0.4f, state.Participants[0].Tone.DaVta);

        // WC/CSTC 更新（静息不动点 → 首回合稳定）
        var after = state.Participants[0].Wc.A;
        Assert.True(Math.Abs(after[0] - before[0]) < 1e-4f, "静息不动点稳定");
        Assert.NotNull(state.Salience[0]);

        // SPending 保持全零（零事件无累计）
        Assert.All(state.SPending[0], v => Assert.Equal(0f, v));
    }

    // ---- AC-2 ②：非 baseline tone 衰减严格靠近 ----

    [Fact]
    public void ZeroEventRound_ToneDecaysTowardBaseline_FromInjected()
    {
        var state = State2P();
        // 注入非 baseline tone（模拟事件回合后）
        var injected = new ToneState { Ne = 0.9f, DaVta = 0.9f, DaSnc = 0.9f, Ht5 = 0.9f };
        state.ApplyTone(0, injected);

        var tm = Tm(Wait);
        tm.StepRound(state, Ctx());

        var t = state.Participants[0].Tone;
        Assert.True(Math.Abs(t.Ne - 0.3f) < Math.Abs(injected.Ne - 0.3f), "NE 向 baseline 靠近");
        Assert.True(Math.Abs(t.Ht5 - 0.5f) < Math.Abs(injected.Ht5 - 0.5f), "5HT 向 baseline 靠近");
    }

    // ---- AC-3：Phase 3 速度重算 ----

    [Fact]
    public void SpeedOrder_Deterministic_WithSameSeed()
    {
        var tm = Tm(Wait);
        var s1 = State2P();
        var s2 = State2P();
        var r1 = tm.StepRound(s1, Ctx(7));
        var r2 = tm.StepRound(s2, Ctx(7));
        // TurnResult record 对数组字段为引用比较——深度断言（Round/事件数/终态 HP）
        Assert.Equal(r1.Round, r2.Round);
        Assert.Equal(r1.Events.Count, r2.Events.Count);
        Assert.Equal(s1.Participants[0].Hp, s2.Participants[0].Hp);
        Assert.Equal(s1.Participants[0].San, s2.Participants[0].San);
    }

    // ---- AC-4/5：物理/精神攻击完整链（事件 → 状态 → tone/s）----

    [Fact]
    public void PhysicalAttack_FullChain()
    {
        var state = State2P();
        var tm = Tm(p => p == 0 ? P0Attacks : Wait);
        var tr = tm.StepRound(state, Ctx());

        var ev = Assert.IsType<PhysicalDamageEvent>(Assert.Single(tr.Events));
        Assert.True(ev.Hit);
        // 状态搬运：HP = TargetHpAfter
        Assert.Equal(ev.TargetHpAfter, state.Participants[1].Hp);
        Assert.Equal(15f - ev.DamageDealt, state.Participants[1].Hp);

        // 攻击者 tone VTA 上升（A1 δ——Phase 4 注入 + Phase 1 下一回合衰减前）
        Assert.True(state.Participants[0].Tone.DaVta > 0.4f, "VTA 上升（A1）");
        // 承受者 NE↑ 5HT↓（B1）
        Assert.True(state.Participants[1].Tone.Ne > 0.3f, "NE 上升（B1）");
        Assert.True(state.Participants[1].Tone.Ht5 < 0.5f, "5HT 下降（B1）");
        // s[Postcentral] > 0
        var postcentral = IndexOf(state, "Postcentral");
        Assert.True(state.SPending[0][postcentral] > 0f, "攻击者 s[Postcentral] > 0");
        Assert.True(state.SPending[1][postcentral] > 0f, "承受者 s[Postcentral] > 0");
    }

    [Fact]
    public void MentalAttack_FullChain_WithPanicEvent()
    {
        // AC-5 + AC-7：精神攻击 → SAN 扣减 → 跨越 30% → Panic 同批 + C1
        var state = State2P();
        // 承受者 SanMax=60 → 30% = 18（跨越点）。构造 SAN=18.5 → 扣 0.6 → 17.9 < 18 跨越 ✓
        state.ApplyDamage(1, state.Participants[1].Hp, 18.5f);

        var mental = new CombatAction
        {
            Broca = new ActionSlot { Kind = ActionKind.MentalAttack, TargetId = 1 },
            Order = ChannelOrder.M1First,
        };
        var tm = Tm(p => p == 0 ? mental : Wait);

        var tr = tm.StepRound(state, Ctx());

        Assert.True(tr.Events.OfType<MentalDamageEvent>().Any(), "精神事件");
        var panic = Assert.Single(tr.Events.OfType<StatusChangeEvent>());
        Assert.Equal(StatusKind.Panic, panic.Kind);
        Assert.True(panic.Entered);
        Assert.Equal(18.5f, panic.SanBefore);
        Assert.Equal(DamageCalculator.Round1(18.5f - 0.6f), panic.SanAfter); // gate=0.635 → san=Round1(0.635)=0.6（探针实测）
        Assert.Equal(60f, panic.SanMax);

        // C1 δ 已注入（tone NE↑ 5HT↓——同批 B4+C1 Σ 一次 Step）
        Assert.True(state.Participants[1].Tone.Ne > 0.3f);
        Assert.True(state.Participants[1].Tone.Ht5 < 0.5f);
        Assert.Equal(panic.SanAfter, state.Participants[1].San); // 搬运
    }

    // ---- AC-6：防御生命周期（Q3=A）----

    [Fact]
    public void DefendLifecycle_NextOwnWindow_Resets()
    {
        var state = State2P();
        var tm = Tm(Wait);

        // 声明防御（直接经 provider 无法控制每参与者——用固定防御声明）
        var defend = new CombatAction
        {
            M1 = new ActionSlot { Kind = ActionKind.Defend, TargetId = 0 },
            Order = ChannelOrder.M1First,
        };
        var defTm = Tm(p => p == 0 ? defend : Wait);
        defTm.StepRound(state, Ctx());
        Assert.True(state.Participants[0].IsDefending, "声明后防御生效");
        Assert.Equal(1, state.Participants[0].DefendCd);

        // 下回合自己窗口开始 → 解除 + CD tick
        tm.StepRound(state, Ctx());
        Assert.False(state.Participants[0].IsDefending, "Q3=A：下次窗口开始解除");
        Assert.Equal(0, state.Participants[0].DefendCd);
    }

    // ---- AC-8：Downed 生产 + 队列移除 ----

    [Fact]
    public void Downed_QueueRemoval_SurvivorsSkipWindows()
    {
        // 3 人：p0 击杀 p1（一击 15 HP 打空）→ p1 Downed + D 广播；p2 仍执行
        var state = CombatState.Create(
            new[]
            {
                ParticipantState.CreateDefault(50f, 80f),
                ParticipantState.CreateDefault(15f, 60f),
                ParticipantState.CreateDefault(15f, 60f),
            },
            new[] { 1, 1, 2 }, Data(), CalibrationConfig.Default);

        // p0 一击必杀（命中 + 满伤害 4？15 HP 需多回合——用高 baseDamage 注入？demo 空手 4。
        // 改为多回合策略：p1 先被削弱到 1 HP（ApplyDamage 直接设），p0 一击 4 → 0。
        state.ApplyDamage(1, 1f, 60f);

        var tm = Tm(p => p == 0 ? P0Attacks : Wait);
        var tr = tm.StepRound(state, Ctx());

        Assert.True(state.Participants[1].Hp <= 0f, "p1 被击杀");
        Assert.Contains(tr.Events, e => e is StatusChangeEvent sc && sc.Kind == StatusKind.Downed);

        // D 广播：p2（异队）收 D2 → tone 变化（Phase 4 实时）
        Assert.True(state.Participants[2].Tone.DaVta > 0.4f || state.Participants[2].Tone.Ht5 > 0.5f,
            "p2 观察者 D2 广播生效");

        // 下回合：p1（Hp=0）跳过窗口（不 Tick/GetAction/Resolve——窗口前检查）
        var tm2 = Tm(Wait);
        var tr2 = tm2.StepRound(state, Ctx());
        Assert.Equal(2, state.Round);
        Assert.True(state.Participants[1].Hp <= 0f);
    }

    // ---- AC-9：结束条件 ----

    [Fact]
    public void IsOver_TeamDefeated()
    {
        var state = State2P();
        state.ApplyDamage(1, 0f, 60f); // p1 HP=0
        var tm = Tm(Wait);
        Assert.True(tm.IsOver(state), "一方全灭（Hp≤0）");

        var s2 = State2P();
        s2.ApplyDamage(1, 15f, 0f); // p1 SAN=0
        Assert.True(tm.IsOver(s2), "一方全灭（San≤0——审计 W1 双口径）");

        var s3 = State2P();
        Assert.False(tm.IsOver(s3), "双方存活不结束");

        Assert.Throws<ArgumentNullException>(() => tm.IsOver(null!));
    }

    [Fact]
    public void IsOver_MaxRounds()
    {
        var cal = new CalibrationConfig { MaxRounds = 3 };
        var tm = new TurnManager(Data(), cal, new FixedProvider(_ => Wait));
        var state = State2P();
        for (var i = 0; i < 3; i++)
        {
            Assert.False(tm.IsOver(state));
            tm.StepRound(state, Ctx((ulong)i));
        }
        Assert.True(tm.IsOver(state), "回合上限 3 结束");
    }

    // ---- AC-10：TurnResult 打包 ----

    [Fact]
    public void TurnResult_RoundEventsHistory()
    {
        var state = State2P();
        var tm = Tm(P0Attacks);
        var tr = tm.StepRound(state, Ctx());

        Assert.Equal(1, tr.Round);
        Assert.Equal(1, state.Round);
        Assert.Single(state.History);
        Assert.Same(tr, state.History[0]);
        // 快照 = 回合末状态（ParticipantState record 值相等——Wc.A 数组引用同源）
        Assert.Equal(state.Participants[0].Hp, tr.ParticipantSnapshots[0].Hp);
        Assert.Equal(state.Participants[0].San, tr.ParticipantSnapshots[0].San);
    }

    // ---- AC-12：确定性 ----

    [Fact]
    public void Determinism_FullBattle_SameSeedIdentical()
    {
        var provider = new FixedProvider(p => p == 0 ? P0Attacks : Wait);

        // 完整战斗（到结束），两遍同种子 → 逐位同
        // record 相等对数组字段为引用比较——深度断言：Round/事件数/终态参与者（Hp/San/Tone/Wc.A 逐位）
        (int Round, int EventCount, ParticipantState[] Final) Run()
        {
            var state = State2P();
            var tm = new TurnManager(Data(), CalibrationConfig.Default, provider);
            var ctx = Ctx(99uL);
            while (!tm.IsOver(state) && state.Round < 60)
                tm.StepRound(state, ctx);
            return (state.Round, state.History.Sum(t => t.Events.Count), state.Participants.ToArray());
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
            Assert.Equal(a.Final[p].Wc.A, b.Final[p].Wc.A); // float[] 逐元素（xUnit 对数组做序列比较）
        }
    }

    // ---- AC-13：异常契约 ----

    [Fact]
    public void NullArgs_Throw()
    {
        var tm = Tm(Wait);
        Assert.Throws<ArgumentNullException>(() => tm.StepRound(null!, Ctx()));
        Assert.Throws<ArgumentNullException>(() => tm.StepRound(State2P(), null!));
        Assert.Throws<ArgumentNullException>(() => new TurnManager(Data(), CalibrationConfig.Default, null!));
        Assert.Throws<ArgumentNullException>(() => new TurnManager(null!, CalibrationConfig.Default, new FixedProvider(_ => Wait)));
    }

    // ---- AC-14：MaxRounds 类型变更回执 ----

    [Fact]
    public void MaxRounds_Default50()
    {
        Assert.Equal(50, CalibrationConfig.Default.MaxRounds);
    }

    private static int IndexOf(CombatState state, string fid)
    {
        var ids = Data().Wsensory.RegionIds;
        for (var i = 0; i < ids.Length; i++)
            if (ids[i] == fid) return i;
        throw new ArgumentException($"无 {fid}");
    }
}
