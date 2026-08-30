using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// EventProcessor spec@v1.2.2（.scratch/csharp-events/design/spec.md）§六 AC-1~AC-15。
/// 锚点来源纪律：全部锚点来自任务issue 01 实测表 + 探针（probe-v1.1.md P1-P13 / probe-v1.2.md Q1-Q4）
/// + 审计独立复现（numpy float32 镜像 ToneUpdater 结合序，audit report §四）；不凭记忆写任何锚点。
/// 标注「逐位」者 Assert.Equal 精确相等；其余 1e-5f 容差。
/// </summary>
public class EventProcessorTests
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

    private static WsensoryMatrix Wsensory() =>
        GameDataLoader.LoadWsensory(Path.Combine(FindDataDir(), "connectivity", "W_sensory.json"));

    private static CalibrationConfig Cal() => CalibrationConfig.Default;

    private static ParticipantState Participant(float hp, float san) => ParticipantState.CreateDefault(hp, san);

    /// <summary>baseline tone（运行时状态模型 §5.4，与 ToneUpdaterTests 同约定）。</summary>
    private static ToneState Baseline() => new() { Ne = 0.3f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.5f };

    private static void AssertTone(ToneState expected, ToneState actual, string what)
    {
        Assert.True(expected == actual,
            $"{what}: 期望 ({expected.Ne:R},{expected.DaVta:R},{expected.DaSnc:R},{expected.Ht5:R})，实际 ({actual.Ne:R},{actual.DaVta:R},{actual.DaSnc:R},{actual.Ht5:R})");
    }

    private static int RegionIndex(WsensoryMatrix ws, string functionalId)
    {
        for (var i = 0; i < ws.RegionIds.Length; i++)
            if (ws.RegionIds[i] == functionalId) return i;
        throw new ArgumentException($"RegionIds 无 {functionalId}");
    }

    /// <summary>非零行集合（从数据推导，零行哨兵）。</summary>
    private static HashSet<int> NonZeroRows(WsensoryMatrix ws, int[] alphaPattern, float mAlpha)
    {
        var rows = new HashSet<int>();
        for (var j = 0; j < ws.Matrix.Length; j++)
        {
            for (var k = 0; k < 6; k++)
                if (ws.Matrix[j][k] != 0 && alphaPattern[k] != 0) { rows.Add(j); break; }
        }
        return rows;
    }

    // ---- AC-1：构造与参数验证 ----

    [Fact]
    public void Ctor_NullArgs_ThrowArgumentNull()
    {
        var ws = Wsensory();
        Assert.Throws<ArgumentNullException>(() => new EventProcessor(null!, Cal()));
        Assert.Throws<ArgumentNullException>(() => new EventProcessor(ws, null!));
    }

    [Fact]
    public void ProcessEvents_NullArgs_ThrowArgumentNull()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var states = new[] { Participant(50f, 80f) };
        Assert.Throws<ArgumentNullException>(() => ep.ProcessEvents(null!, states, new[] { 1 }));
        Assert.Throws<ArgumentNullException>(() => ep.ProcessEvents([], null!, new[] { 1 }));
        Assert.Throws<ArgumentNullException>(() => ep.ProcessEvents([], states, null!));
    }

    [Fact]
    public void ProcessEvents_TeamsMismatch_Throws()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var states = new[] { Participant(50f, 80f), Participant(50f, 80f) };
        Assert.Throws<ArgumentException>(() => ep.ProcessEvents([], states, new[] { 1 }));
    }

    [Theory]
    [InlineData(-1, 0)]
    [InlineData(5, 0)]
    [InlineData(0, -1)]
    [InlineData(0, 5)]
    public void ProcessEvents_OutOfRangeId_Throws(int actorId, int targetId)
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var states = new[] { Participant(50f, 80f) };
        var ev = new PhysicalDamageEvent(1, actorId, targetId) { DamageDealt = 4f };
        Assert.Throws<ArgumentException>(() => ep.ProcessEvents([ev], states, new[] { 1 }));
    }

    // ---- AC-2：物理命中无防御（A1 + B1）----

    [Fact]
    public void PhysicalHit_NoDefense_A1AndB1()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var attacker = Participant(50f, 80f);
        var target = Participant(15f, 60f);
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = 4f, DamageBlocked = 0f, IncomingDamage = 4f,
            TargetHpBefore = 15f, TargetHpAfter = 10f, TargetHpMax = 15f,
        };
        var result = ep.ProcessEvents([ev], new[] { attacker, target }, new[] { 1, 2 });

        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.68929785f, DaSnc = 0.71404856f, Ht5 = 0.5f },
            result.States[0].Tone, "攻击者 A1");
        AssertTone(new ToneState { Ne = 0.3864665f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.4513417f },
            result.States[1].Tone, "承受者 B1");

        var postcentral = RegionIndex(Wsensory(), "Postcentral");
        Assert.Equal(1.0f, result.SensoryAccum[0][postcentral]); // A1 s（m_α=1.0）
        Assert.Equal(0.6666667f, result.SensoryAccum[1][postcentral]); // B1 s（m_α=m=0.33333334×2 模态）
    }

    // ---- AC-3：三路分区（Q2=A）----

    [Fact]
    public void DefendedHit_TargetReceivesOnlyA5()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var target = Participant(15f, 60f);
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = 2f, DamageBlocked = 2f, IncomingDamage = 4f,
            TargetHpBefore = 15f, TargetHpAfter = 13f, TargetHpMax = 15f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), target }, new[] { 1, 2 });

        // 仅 A5：5HT 0.57298744，NE/DA_VTA/DA_SNc 与基线逐位相同（无 B1 混入）
        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.57298744f },
            result.States[1].Tone, "承受者 A5（防御生效）");
        // A5 s：m_α=1.0（A 类恒发）
        var postcentral = RegionIndex(Wsensory(), "Postcentral");
        Assert.Equal(1.0f, result.SensoryAccum[1][postcentral]);
    }

    [Fact]
    public void Miss_ReceiverGetsB2_NotB1()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = false, DamageDealt = 0f, DamageBlocked = 4f, IncomingDamage = 4f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        // B2 m=1.0（blocked==incoming 契约）
        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.6459749f },
            result.States[1].Tone, "承受者 B2");
    }

    // ---- AC-4：A2 miss（δ 跳过、s 恒发）----

    [Fact]
    public void Miss_AttackerToneUnchanged_ButSStillSent()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var attacker = Participant(50f, 80f);
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = false, DamageDealt = 0f, DamageBlocked = 4f, IncomingDamage = 4f,
        };
        var result = ep.ProcessEvents([ev], new[] { attacker, Participant(15f, 60f) }, new[] { 1, 2 });

        AssertTone(Baseline(), result.States[0].Tone, "攻击者 A2（零向量不调用 Step）");
        var postcentral = RegionIndex(Wsensory(), "Postcentral");
        Assert.Equal(1.0f, result.SensoryAccum[0][postcentral]); // m_α=1.0 恒发（任务issue D1）
    }

    // ---- AC-5：A4 + B4 ----

    [Fact]
    public void MentalAttack_A4_ExpectedFormula()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new MentalDamageEvent(1, 0, 1)
        {
            SanDamage = 1.0f, MotivationMod = 0f,
            TargetSanBefore = 60f, TargetSanAfter = 59f, TargetSanMax = 60f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        // A4 mot=0 → expected=2×1−1=1.0 → m=1.0
        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.68929785f, DaSnc = 0.5f, Ht5 = 0.5f },
            result.States[0].Tone, "攻击者 A4 m=1.0");
        // B4 |ΔSAN|=1/60 → m=0.016666668 → 不发断言，见 B4 专项
    }

    [Fact]
    public void MentalAttack_PenetrationM13_E1Fixed()
    {
        // E1 修正：mot=0.5 → expected=2×1.5−1=2.0 → m=2.6/2.0=1.3（mot=0 时 expected=1.0 → m=2.6，非 1.3）
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new MentalDamageEvent(1, 0, 1)
        {
            SanDamage = 2.6f, MotivationMod = 0.5f,
            TargetSanBefore = 60f, TargetSanAfter = 57.4f, TargetSanMax = 60f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.77608716f, DaSnc = 0.5f, Ht5 = 0.5f },
            result.States[0].Tone, "A4 m=1.3（任务issue #25 锚点）");
    }

    [Theory]
    [InlineData(-1f, "m<0")] // expected=2×0−1=−1 → m=2.6/−1<0 → δ skip
    [InlineData(-0.5f, "m=+∞")] // expected=2×0.5−1=0 → m=2.6/0=+∞ → IsInfinity skip（probe Q8）
    public void MentalAttack_NegativeMotivation_DeltaSkipped_SStillSent(float motivation, string what)
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new MentalDamageEvent(1, 0, 1)
        {
            SanDamage = 2.6f, MotivationMod = motivation,
            TargetSanBefore = 60f, TargetSanAfter = 57.4f, TargetSanMax = 60f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        AssertTone(Baseline(), result.States[0].Tone, $"A4 {what} δ skip");
        // s 仍发（A 类 m_α=1.0 恒发）：A4 α=(0,0,0,0,1,1) → 社会+语言模态
        var ws = Wsensory();
        var nonzero = NonZeroRows(ws, new[] { 0, 0, 0, 0, 1, 1 }, 1.0f);
        foreach (var j in nonzero)
            Assert.NotEqual(0f, result.SensoryAccum[0][j]);
    }

    [Fact]
    public void MentalB4_SanDrop_ToneAnchor()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new MentalDamageEvent(1, 0, 1)
        {
            SanDamage = 2.0f, MotivationMod = 0f,
            TargetSanBefore = 60f, TargetSanAfter = 58f, TargetSanMax = 60f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        // B4 m=2/60=0.033333335
        AssertTone(new ToneState { Ne = 0.30864665f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.49513417f },
            result.States[1].Tone, "承受者 B4（任务issue #23）");
    }

    [Fact]
    public void MentalAttack_Mot025_Expected15_ExpressionAnchor()
    {
        // expected = 2×1.25−1 = 1.5（表达式锚，f32 先乘后减）
        var cal = Cal();
        var expected = (float)cal.BaseMentalDamage * (1f + 0.25f) - cal.EndurancePassivePenalty;
        Assert.Equal(1.5f, expected);
    }

    // ---- AC-6：C1 guard 全条件 ----

    [Fact]
    public void Panic_Crosses30_SendsC1()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new StatusChangeEvent(1, 0, 0)
        {
            Kind = StatusKind.Panic, Entered = true,
            SanBefore = 19f, SanAfter = 17.9f, SanMax = 60f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f) }, new[] { 1 });

        AssertTone(new ToneState { Ne = 0.5593994f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.35402513f },
            result.States[0].Tone, "C1（任务issue #21）");
        var postcentral = RegionIndex(Wsensory(), "Postcentral");
        Assert.Equal(1.0f, result.SensoryAccum[0][postcentral]); // C1 α=(0,0,0,1,0,0)×1.0
    }

    [Theory]
    [InlineData(19f, 18f, "new 恰好 30%（18f<18f=False，严格）")]
    [InlineData(18f, 18f, "SanBefore==SanAfter（被动变化 ΔSAN=0）")]
    [InlineData(17f, 17.9f, "SanBefore<SanAfter（治疗）")]
    public void Panic_GuardFails_NoC1(float before, float after, string what)
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new StatusChangeEvent(1, 0, 0)
        {
            Kind = StatusKind.Panic, Entered = true,
            SanBefore = before, SanAfter = after, SanMax = 60f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f) }, new[] { 1 });

        AssertTone(Baseline(), result.States[0].Tone, what);
    }

    [Fact]
    public void Panic_OldInclusive18_Sends()
    {
        // old 含端：18 ≥ 0.30×60=18（含端发）
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new StatusChangeEvent(1, 0, 0)
        {
            Kind = StatusKind.Panic, Entered = true,
            SanBefore = 18f, SanAfter = 17.9f, SanMax = 60f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f) }, new[] { 1 });
        AssertTone(new ToneState { Ne = 0.5593994f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.35402513f },
            result.States[0].Tone, "C1 old 含端");
    }

    [Fact]
    public void Panic_EnteredFalse_NoC1()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new StatusChangeEvent(1, 0, 0)
        {
            Kind = StatusKind.Panic, Entered = false,
            SanBefore = 19f, SanAfter = 17.9f, SanMax = 60f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f) }, new[] { 1 });
        AssertTone(Baseline(), result.States[0].Tone, "Entered=false 不发");
    }

    // ---- AC-7：D1/D2 广播 ----

    [Fact]
    public void Downed_Broadcasts_D1ToTeammate_D2ToEnemy()
    {
        // E2 修正：teams=[1,1,2]——p1 与 p0 同队收 D1、p2 异队收 D2
        var ep = new EventProcessor(Wsensory(), Cal());
        var states = new[] { Participant(50f, 80f), Participant(15f, 60f), Participant(15f, 60f) };
        var downed = Participant(15f, 60f) with { Hp = 0f };
        states[0] = downed;
        var ev = new StatusChangeEvent(1, 0, 0) { Kind = StatusKind.Downed, Entered = true };
        var result = ep.ProcessEvents([ev], states, new[] { 1, 1, 2 });

        AssertTone(new ToneState { Ne = 0.5593994f, DaVta = 0.110702194f, DaSnc = 0.5f, Ht5 = 0.35402513f },
            result.States[1].Tone, "p1 同队 D1（任务issue #21）");
        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.68929785f, DaSnc = 0.5f, Ht5 = 0.6459749f },
            result.States[2].Tone, "p2 异队 D2（任务issue #22）");
        // p0（倒者）tone 不变、s 全零
        AssertTone(Baseline(), result.States[0].Tone, "p0 倒者排除");
        Assert.All(result.SensoryAccum[0], v => Assert.Equal(0f, v));
    }

    [Fact]
    public void Downed_DeadObserver_Excluded()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var states = new[]
        {
            Participant(50f, 80f) with { Hp = 0f }, // p0 倒者
            Participant(15f, 60f) with { Hp = 0f }, // p1 非倒者但 Hp=0 → 排除
            Participant(15f, 60f),
        };
        var ev = new StatusChangeEvent(1, 0, 0) { Kind = StatusKind.Downed, Entered = true };
        var result = ep.ProcessEvents([ev], states, new[] { 1, 1, 1 });

        AssertTone(Baseline(), result.States[0].Tone, "p0 倒者");
        AssertTone(Baseline(), result.States[1].Tone, "p1 Hp=0 不收");
        AssertTone(new ToneState { Ne = 0.5593994f, DaVta = 0.110702194f, DaSnc = 0.5f, Ht5 = 0.35402513f },
            result.States[2].Tone, "p2 同队 D1");
    }

    [Fact]
    public void Downed_EnteredFalse_NoBroadcast()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var states = new[] { Participant(50f, 80f) with { Hp = 0f }, Participant(15f, 60f) };
        var ev = new StatusChangeEvent(1, 0, 0) { Kind = StatusKind.Downed, Entered = false };
        var result = ep.ProcessEvents([ev], states, new[] { 1, 1 });
        Assert.All(result.States, s => AssertTone(Baseline(), s.Tone, "Entered=false 全不发"));
    }

    [Fact]
    public void MultiDowned_ObserverAccumulatesD2x2()
    {
        // W-h：p0、p1 同批倒下 → p2（异队）收 D2×2 → Σδ=(0,2,0,2)（probe P6）
        var ep = new EventProcessor(Wsensory(), Cal());
        var states = new[]
        {
            Participant(50f, 80f) with { Hp = 0f },
            Participant(15f, 60f) with { Hp = 0f },
            Participant(15f, 60f),
        };
        var events = new CombatEvent[]
        {
            new StatusChangeEvent(1, 0, 0) { Kind = StatusKind.Downed, Entered = true },
            new StatusChangeEvent(1, 1, 1) { Kind = StatusKind.Downed, Entered = true },
        };
        var result = ep.ProcessEvents(events, states, new[] { 1, 1, 2 });

        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.9785956f, DaSnc = 0.5f, Ht5 = 0.79194975f },
            result.States[2].Tone, "p2 收 D2×2（probe P6）");
    }

    [Fact]
    public void MultiDowned_TeammateObserverGetsD1x2()
    {
        // v1.2 修正：双 D1 需 4 人 teams=[1,1,1,2]——p0、p1 倒下 → p2（同队存活）收 D1×2（probe P7）
        var ep = new EventProcessor(Wsensory(), Cal());
        var states = new[]
        {
            Participant(50f, 80f) with { Hp = 0f },
            Participant(15f, 60f) with { Hp = 0f },
            Participant(15f, 60f),
            Participant(15f, 60f),
        };
        var events = new CombatEvent[]
        {
            new StatusChangeEvent(1, 0, 0) { Kind = StatusKind.Downed, Entered = true },
            new StatusChangeEvent(1, 1, 1) { Kind = StatusKind.Downed, Entered = true },
        };
        var result = ep.ProcessEvents(events, states, new[] { 1, 1, 1, 2 });

        AssertTone(new ToneState { Ne = 0.81879884f, DaVta = 0f, DaSnc = 0.5f, Ht5 = 0.20805025f },
            result.States[2].Tone, "p2 收 D1×2（probe P7）");
        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.9785956f, DaSnc = 0.5f, Ht5 = 0.79194975f },
            result.States[3].Tone, "p3 收 D2×2");
    }

    // ---- AC-8：m<0.01 skip 双通道 ----

    [Fact]
    public void SmallM_BelowThreshold_ToneUnchanged_SZero()
    {
        // B4 |ΔSAN|=0.5/60 → m=0.008333334（I-3 最短往返）< 0.01 → 双通道 skip
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new MentalDamageEvent(1, 0, 1)
        {
            SanDamage = 0.5f, MotivationMod = 0f,
            TargetSanBefore = 60f, TargetSanAfter = 59.5f, TargetSanMax = 60f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        AssertTone(Baseline(), result.States[1].Tone, "B4 m=0.008333334 skip");
        Assert.All(result.SensoryAccum[1], v => Assert.Equal(0f, v));
    }

    [Theory]
    [InlineData(0.1f, true, "m=0.01f 逐位 → 发")]
    [InlineData(0.05f, false, "m=0.005 < 0.01 → 不发")]
    public void B1_ThresholdBoundary(float hpDelta, bool sends, string what)
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = hpDelta, DamageBlocked = 0f, IncomingDamage = hpDelta,
            TargetHpBefore = 10f, TargetHpAfter = 10f - hpDelta, TargetHpMax = 10f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(10f, 60f) }, new[] { 1, 2 });

        if (sends)
            Assert.True(result.States[1].Tone != Baseline(), what);
        else
            AssertTone(Baseline(), result.States[1].Tone, what);
    }

    [Fact]
    public void NaN_Infinity_ByEventClass()
    {
        // W-k：B/C/D 类（B2 incoming=0 → NaN）双通道全 skip；A 类（A1 dealt=NaN、A5 +∞）δ skip 但 s 照发
        var ep = new EventProcessor(Wsensory(), Cal());
        var ws = Wsensory();
        var postcentral = RegionIndex(ws, "Postcentral");

        // A1 dealt=NaN：δ skip、s 发（m_α=1.0）
        var a1 = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = float.NaN, DamageBlocked = 0f, IncomingDamage = 4f,
        };
        var r1 = ep.ProcessEvents([a1], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });
        AssertTone(Baseline(), r1.States[0].Tone, "A1 NaN δ skip");
        Assert.Equal(1.0f, r1.SensoryAccum[0][postcentral]); // s 恒发

        // A5 incoming=0 ∧ blocked>0 → m=+∞：δ skip、s 发（m_α=1.0，v1.2 修正）
        var a5 = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = 0f, DamageBlocked = 2f, IncomingDamage = 0f,
        };
        var r2 = ep.ProcessEvents([a5], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });
        AssertTone(Baseline(), r2.States[1].Tone, "A5 +∞ δ skip");
        Assert.Equal(1.0f, r2.SensoryAccum[1][postcentral]); // A5 s m_α=1.0 恒发（A 类）

        // B2 incoming=0 → NaN：双通道全 skip
        var b2 = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = false, DamageDealt = 0f, DamageBlocked = 0f, IncomingDamage = 0f,
        };
        var r3 = ep.ProcessEvents([b2], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });
        AssertTone(Baseline(), r3.States[1].Tone, "B2 NaN 双通道 skip");
        Assert.All(r3.SensoryAccum[1], v => Assert.Equal(0f, v));
    }

    // ---- AC-9：Σ 聚合后单次 Step ----

    [Fact]
    public void Summation_B1PlusB4_SingleStep()
    {
        // B1(m=0.33333334)+B4(m=0.033333335) 同承受者（probe P11 复核）
        var ep = new EventProcessor(Wsensory(), Cal());
        var target = Participant(15f, 60f);
        var events = new CombatEvent[]
        {
            new PhysicalDamageEvent(1, 0, 1)
            {
                Hit = true, DamageDealt = 5f, DamageBlocked = 0f, IncomingDamage = 5f,
                TargetHpBefore = 15f, TargetHpAfter = 10f, TargetHpMax = 15f,
            },
            new MentalDamageEvent(1, 0, 1)
            {
                SanDamage = 2f, MotivationMod = 0f,
                TargetSanBefore = 60f, TargetSanAfter = 58f, TargetSanMax = 60f,
            },
        };
        var result = ep.ProcessEvents(events, new[] { Participant(50f, 80f), target }, new[] { 1, 2 });

        AssertTone(new ToneState { Ne = 0.39511314f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.44647586f },
            result.States[1].Tone, "B1+B4 Σ 一次 Step");
    }

    [Fact]
    public void Summation_A1PlusA4_SingleStep()
    {
        // A1(m=1.0)+A4(m=1.0) 同攻击者 → Σδ=(0,2,1,0)（审计 numpy 复现）
        var ep = new EventProcessor(Wsensory(), Cal());
        var attacker = Participant(50f, 80f);
        var events = new CombatEvent[]
        {
            new PhysicalDamageEvent(1, 0, 1)
            {
                Hit = true, DamageDealt = 4f, DamageBlocked = 0f, IncomingDamage = 4f,
            },
            new MentalDamageEvent(1, 0, 1)
            {
                SanDamage = 1f, MotivationMod = 0f,
                TargetSanBefore = 60f, TargetSanAfter = 59f, TargetSanMax = 60f,
            },
        };
        var result = ep.ProcessEvents(events, new[] { attacker, Participant(15f, 60f) }, new[] { 1, 2 });

        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.9785956f, DaSnc = 0.71404856f, Ht5 = 0.5f },
            result.States[0].Tone, "A1+A4 Σ 一次 Step");
    }

    [Fact]
    public void Summation_C1PlusB1_SingleStep_WithSAssertion()
    {
        // C1+B1 同承受者（probe P12 复核）+ s 断言（W-f：s[Postcentral]=1.6666667，probe P5）
        var ep = new EventProcessor(Wsensory(), Cal());
        var target = Participant(15f, 60f);
        var events = new CombatEvent[]
        {
            new PhysicalDamageEvent(1, 0, 1)
            {
                Hit = true, DamageDealt = 5f, DamageBlocked = 0f, IncomingDamage = 5f,
                TargetHpBefore = 15f, TargetHpAfter = 10f, TargetHpMax = 15f,
            },
            new StatusChangeEvent(1, 1, 1)
            {
                Kind = StatusKind.Panic, Entered = true,
                SanBefore = 19f, SanAfter = 17.9f, SanMax = 60f,
            },
        };
        var result = ep.ProcessEvents(events, new[] { Participant(50f, 80f), target }, new[] { 1, 2 });

        AssertTone(new ToneState { Ne = 0.6458659f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.3053668f },
            result.States[1].Tone, "C1+B1 Σ 一次 Step");
        var postcentral = RegionIndex(Wsensory(), "Postcentral");
        Assert.Equal(1.6666667f, result.SensoryAccum[1][postcentral]); // C1 s 1.0 + B1 s 0.6666667
    }

    [Fact]
    public void Summation_B1x2_SigmaThenSingleStep_E3Fixed()
    {
        // E3 修正：B1×2 → Σδ=(0.66666669,0,0,−0.66666669) → 一次 Step（probe P1，非逐事件两次 Step）
        var ep = new EventProcessor(Wsensory(), Cal());
        var target = Participant(15f, 60f);
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = 5f, DamageBlocked = 0f, IncomingDamage = 5f,
            TargetHpBefore = 15f, TargetHpAfter = 10f, TargetHpMax = 15f,
        };
        var result = ep.ProcessEvents([ev, ev], new[] { Participant(50f, 80f), target }, new[] { 1, 2 });

        AssertTone(new ToneState { Ne = 0.47293293f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.4026834f },
            result.States[1].Tone, "B1×2 Σ 一次 Step（probe P1）");
    }

    // ---- AC-10：s 打包 ----

    [Fact]
    public void Sensory_A1_15Rows_Postcentral1()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ws = Wsensory();
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = 4f, DamageBlocked = 0f, IncomingDamage = 4f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        var postcentral = RegionIndex(ws, "Postcentral");
        Assert.Equal(1.0f, result.SensoryAccum[0][postcentral]);
        var nonzero = NonZeroRows(ws, new[] { 1, 0, 1, 0, 0, 0 }, 1.0f);
        Assert.Equal(15, nonzero.Count);
        Assert.Equal(69, result.SensoryAccum[0].Length); // RegionIds 序
    }

    [Fact]
    public void Sensory_B2_SameAsA1Pattern()
    {
        // W-f 补行：B2 m_α=m=1.0（契约恒等）→ 与 A1 同 α pattern
        var ep = new EventProcessor(Wsensory(), Cal());
        var ws = Wsensory();
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = false, DamageDealt = 0f, DamageBlocked = 4f, IncomingDamage = 4f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        var postcentral = RegionIndex(ws, "Postcentral");
        Assert.Equal(1.0f, result.SensoryAccum[1][postcentral]);
        Assert.Equal(15, NonZeroRows(ws, new[] { 1, 0, 1, 0, 0, 0 }, 1.0f).Count);
    }

    [Fact]
    public void Sensory_D1_26Rows_DualModal2()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ws = Wsensory();
        var states = new[] { Participant(50f, 80f) with { Hp = 0f }, Participant(15f, 60f) };
        var ev = new StatusChangeEvent(1, 0, 0) { Kind = StatusKind.Downed, Entered = true };
        var result = ep.ProcessEvents([ev], states, new[] { 1, 1 });

        var st = RegionIndex(ws, "SuperiorTemporal");
        Assert.Equal(2.0f, result.SensoryAccum[1][st]); // 双模态（aud+…）可达 2.0
        Assert.Equal(2.0f, result.SensoryAccum[1].Max());
        Assert.Equal(26, NonZeroRows(ws, new[] { 1, 1, 0, 0, 1, 0 }, 1.0f).Count);
    }

    [Fact]
    public void Sensory_B1_20Rows_And_Max()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ws = Wsensory();
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = 5f, DamageBlocked = 0f, IncomingDamage = 5f,
            TargetHpBefore = 15f, TargetHpAfter = 10f, TargetHpMax = 15f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        var postcentral = RegionIndex(ws, "Postcentral");
        Assert.Equal(0.6666667f, result.SensoryAccum[1][postcentral]); // soma+pain × 0.33333334
        Assert.Equal(0.6666667f, result.SensoryAccum[1].Max());
        Assert.Equal(20, NonZeroRows(ws, new[] { 1, 0, 1, 1, 0, 0 }, 0.33333334f).Count);
    }

    [Fact]
    public void Sensory_A5_MAlpha1_FourRows()
    {
        // W-c 修正：A5 m_α=1.0（A 类恒发）——非旧口径 0.5
        var ep = new EventProcessor(Wsensory(), Cal());
        var ws = Wsensory();
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = 2f, DamageBlocked = 2f, IncomingDamage = 4f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        var postcentral = RegionIndex(ws, "Postcentral");
        Assert.Equal(1.0f, result.SensoryAccum[1][postcentral]);
        Assert.Equal(1.0f, result.SensoryAccum[1].Max());
        Assert.Equal(4, NonZeroRows(ws, new[] { 0, 0, 1, 0, 0, 0 }, 1.0f).Count);
    }

    [Fact]
    public void Sensory_ZeroRowSentinel_AccumbensIsZero()
    {
        // 零行哨兵：subcortical fid 无感官输入（AccumbensCore——Amygdala 自 #108 Q2 起为嗅觉锚点，不再是零行）
        // 从数据推导
        var ws = Wsensory();
        var acc = RegionIndex(ws, "AccumbensCore");
        Assert.All(ws.Matrix[acc], v => Assert.Equal(0, v));

        var ep = new EventProcessor(ws, Cal());
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = 4f, DamageBlocked = 0f, IncomingDamage = 4f,
        };
        var result = ep.ProcessEvents([ev], new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });
        Assert.Equal(0f, result.SensoryAccum[0][acc]);
    }

    // ---- AC-11：HealEvent/LinkGrowthEvent no-op ----

    [Fact]
    public void HealAndLinkGrowth_PureBatch_AllZero()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var states = new[] { Participant(50f, 80f), Participant(15f, 60f) };
        var events = new CombatEvent[]
        {
            new HealEvent(1, 0, 1) { HealAmount = 10 },
            new LinkGrowthEvent(1, 0, 1) { LinkId = "L1", DeltaM = 0.2f },
        };
        var result = ep.ProcessEvents(events, states, new[] { 1, 2 });

        Assert.All(result.States, s => AssertTone(Baseline(), s.Tone, "no-op 批次"));
        Assert.All(result.SensoryAccum, acc => Assert.All(acc, v => Assert.Equal(0f, v)));
    }

    [Fact]
    public void Heal_MixedBatch_NoInterference()
    {
        // W-i：Heal 混入 A1 批次 → A1 照发、Heal 贡献零
        var ep = new EventProcessor(Wsensory(), Cal());
        var events = new CombatEvent[]
        {
            new HealEvent(1, 0, 1) { HealAmount = 10 },
            new PhysicalDamageEvent(1, 0, 1)
            {
                Hit = true, DamageDealt = 4f, DamageBlocked = 0f, IncomingDamage = 4f,
            },
        };
        var result = ep.ProcessEvents(events, new[] { Participant(50f, 80f), Participant(15f, 60f) }, new[] { 1, 2 });

        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.68929785f, DaSnc = 0.71404856f, Ht5 = 0.5f },
            result.States[0].Tone, "A1 照发");
    }

    // ---- AC-12：确定性 + 输入不可变 ----

    [Fact]
    public void Determinism_SameInput_BitwiseIdentical()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = 4f, DamageBlocked = 0f, IncomingDamage = 4f,
            TargetHpBefore = 15f, TargetHpAfter = 10f, TargetHpMax = 15f,
        };
        var states = new[] { Participant(50f, 80f), Participant(15f, 60f) };

        var first = ep.ProcessEvents([ev], states, new[] { 1, 2 });
        for (var i = 0; i < 4; i++)
        {
            var again = ep.ProcessEvents([ev], states, new[] { 1, 2 });
            Assert.Equal(first.States, again.States);
            Assert.Equal(first.SensoryAccum, again.SensoryAccum);
        }
    }

    [Fact]
    public void Inputs_NotMutated_OutputsNewReferences()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var tone = Baseline();
        var states = new[] { Participant(50f, 80f), Participant(15f, 60f) };
        states[0] = states[0] with { Tone = tone };
        var ev = new PhysicalDamageEvent(1, 0, 1)
        {
            Hit = true, DamageDealt = 4f, DamageBlocked = 0f, IncomingDamage = 4f,
        };

        var result = ep.ProcessEvents([ev], states, new[] { 1, 2 });

        Assert.Equal(0.3f, tone.Ne); // 输入 tone 不变
        Assert.NotSame(states[0], result.States[0]); // 输出新引用（Step 接收者）
        Assert.Same(states[1], result.States[1]); // 零 delta 参与者——record 副本即输入引用（Tone 逐位相同）
    }

    // ---- AC-13：L2 类型变更回执 ----

    [Fact]
    public void StatusChangeEvent_NewFields_RoundTripBitwise()
    {
        var ev = new StatusChangeEvent(1, 2, 2)
        {
            Kind = StatusKind.Panic,
            Entered = true,
            SanBefore = 5.6f,
            SanAfter = 4.2f,
            SanMax = 60f,
        };
        Assert.Equal(5.6f, ev.SanBefore);
        Assert.Equal(4.2f, ev.SanAfter);
        Assert.Equal(60f, ev.SanMax);
        Assert.Equal(StatusKind.Panic, ev.Kind);
        Assert.Equal(2, ev.ActorId);
    }

    [Fact]
    public void CalibrationConfig_EndurancePassivePenalty_IsOne()
    {
        Assert.Equal(1, CalibrationConfig.Default.EndurancePassivePenalty);
        Assert.Equal(1, Cal().EndurancePassivePenalty);
    }

    // ---- AC-14：空事件列表 ----

    [Fact]
    public void EmptyEvents_StatesCopy_SensoryZero()
    {
        var ep = new EventProcessor(Wsensory(), Cal());
        var states = new[] { Participant(50f, 80f), Participant(15f, 60f) };
        var result = ep.ProcessEvents([], states, new[] { 1, 2 });

        Assert.Equal(states, result.States); // 逐字段等于输入（Tone 逐位）
        Assert.All(result.SensoryAccum, acc => Assert.All(acc, v => Assert.Equal(0f, v)));
    }

    // ---- AC-15：击杀窗口 ----

    [Fact]
    public void KillWindow_DownedReceiverStillGetsB1()
    {
        // W-e 锚点（v1.2）：p1=攻击者（ActorId=1，收 A1 m=3.75 不在断言范围）、p0=被击杀者
        // （伤害 TargetId + Downed ActorId）——p0 只收 B1（m=15/15=1.0）（probe Q1-Q4）
        var ep = new EventProcessor(Wsensory(), Cal());
        var ws = Wsensory();
        var states = new[]
        {
            Participant(50f, 80f) with { Hp = 0f, HpMax = 50f },
            Participant(50f, 80f),
            Participant(15f, 60f),
        };
        var events = new CombatEvent[]
        {
            new PhysicalDamageEvent(1, 1, 0)
            {
                Hit = true, DamageDealt = 15f, DamageBlocked = 0f, IncomingDamage = 15f,
                TargetHpBefore = 50f, TargetHpAfter = 0f, TargetHpMax = 50f,
            },
            new StatusChangeEvent(1, 0, 0) { Kind = StatusKind.Downed, Entered = true },
        };
        var result = ep.ProcessEvents(events, states, new[] { 1, 1, 2 });

        // p0（被击杀者）照收 B1：δ=(1,0,0,−1) → tone + s[Postcentral]=2.0（soma+pain ×1.0）
        AssertTone(new ToneState { Ne = 0.5593994f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.35402513f },
            result.States[0].Tone, "p0 击杀窗口 B1（probe Q1）");
        var postcentral = RegionIndex(ws, "Postcentral");
        Assert.Equal(2.0f, result.SensoryAccum[0][postcentral]); // probe Q2
        Assert.Equal(20, NonZeroRows(ws, new[] { 1, 0, 1, 1, 0, 0 }, 1.0f).Count); // probe Q4

        // p0 不另收 D 广播（p≠ActorId 排除——Downed 的 ActorId=0）
        // p1 收 A1（m=3.75，δ=(0,3.75,3.75,0)）+ D1（同队）——不在断言范围
        // p2 收 D2（异队）——分流逻辑同 §5.5.2
        AssertTone(new ToneState { Ne = 0.3f, DaVta = 0.68929785f, DaSnc = 0.5f, Ht5 = 0.6459749f },
            result.States[2].Tone, "p2 异队 D2");
    }
}
