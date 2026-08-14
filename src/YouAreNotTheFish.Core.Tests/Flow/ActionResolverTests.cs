using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Flow;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Flow;

/// <summary>
/// ActionResolver spec@v1.2 §三 3.3 + §五 5.1：事件生产（链式基准/miss 契约/配对校验/常量消费）。
/// 锚点来源：DamageCalculator 组件级已验证 + csharp-damage AC-5（miss 完整伤害）+ 本测试推导（确定性组件）。
/// </summary>
public class ActionResolverTests
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

    private static ActionResolver Resolver() => new(Data(), CalibrationConfig.Default);

    private static CombatAction Physical(int target = 1) => new()
    {
        M1 = new ActionSlot { Kind = ActionKind.PhysicalAttack, TargetId = target },
        Order = ChannelOrder.M1First,
    };

    private static CombatAction Mental(int target = 1) => new()
    {
        Broca = new ActionSlot { Kind = ActionKind.MentalAttack, TargetId = target },
        Order = ChannelOrder.M1First,
    };

    // ---- AC-4：物理攻击完整链 ----

    [Fact]
    public void PhysicalHit_EventFields_Filled()
    {
        var state = State2P();
        var events = Resolver().Resolve(0, Physical(), state, Ctx());

        var ev = Assert.IsType<PhysicalDamageEvent>(Assert.Single(events));
        Assert.True(ev.Hit);
        Assert.Equal(4, ev.BaseDamage); // 消费 cal.BasePhysicalDamage
        Assert.Equal(0, ev.WeaponBonus);
        Assert.Equal(state.Participants[0].Gates.GateSomatic, ev.GateBonus);
        Assert.True(ev.DamageDealt > 0f);
        Assert.Equal(0f, ev.DamageBlocked); // 无防御
        Assert.Equal(ev.DamageDealt, ev.IncomingDamage); // 契约恒等
        Assert.Equal(15f, ev.TargetHpBefore); // 目标 HP（p1=15）
        Assert.Equal(15f - ev.DamageDealt, ev.TargetHpAfter); // 0.1 网格
        Assert.Equal(15f, ev.TargetHpMax);
    }

    [Fact]
    public void PhysicalMiss_Contract_Dealt0_BlockedIncoming()
    {
        // 审计 E2 锚点：miss → dealt=0 ∧ blocked==incoming>0（events §2.4 契约——B2 m=1.0 路径可达）
        var state = State2P();
        // 命中率 0.75——RNG 必须产出 ≥0.75 的 roll。DeterministicRng(42) 首值未知——先探测或循环构造。
        // 用直接构造：固定 provider 场景下 roll 不可控，此处用多次尝试找 miss 实例（确定性引擎——同种子必同 roll）。
        var resolver = Resolver();
        for (ulong seed = 0; seed < 200; seed++)
        {
            var evs = resolver.Resolve(0, Physical(), State2P(), Ctx((ulong)seed));
            var ev = (PhysicalDamageEvent)evs[0];
            if (!ev.Hit)
            {
                Assert.Equal(0f, ev.DamageDealt);
                Assert.Equal(ev.DamageBlocked, ev.IncomingDamage);
                Assert.True(ev.IncomingDamage > 0f); // 完整伤害（damage calc AC-5）
                Assert.Equal(ev.TargetHpBefore, ev.TargetHpAfter); // miss 无伤害
                return;
            }
        }
        Assert.Fail("200 种子内未找到 miss 实例");
    }

    // ---- AC-5：精神攻击完整链 ----

    [Fact]
    public void MentalAttack_EventFields_Filled()
    {
        var state = State2P();
        var events = Resolver().Resolve(0, Mental(), state, Ctx());

        var ev = Assert.IsType<MentalDamageEvent>(Assert.Single(events));
        Assert.True(ev.SanDamage > 0f);
        Assert.Equal(60f, ev.TargetSanMax); // SanMax 来自目标（p1）
        Assert.Equal(60f, ev.TargetSanBefore);
        Assert.Equal(DamageCalculator.Round1(60f - ev.SanDamage), ev.TargetSanAfter);
        Assert.Equal(15f, ev.TargetHpBefore);
        Assert.Equal(DamageCalculator.Round1(15f - ev.HpDamage), ev.TargetHpAfter);
        Assert.Equal(state.Participants[0].Gates.GateCognitive, ev.GateBonus);
    }

    [Fact]
    public void Mental_NoRngConsumed_AlwaysHits()
    {
        // 精神永远命中（无命中判定——damage calc AC-9：Mental_NoRng_Completes）
        var state = State2P();
        var evs = Resolver().Resolve(0, Mental(), state, Ctx());
        Assert.Single(evs);
    }

    // ---- AC-6：防御 + 链式基准 ----

    [Fact]
    public void DefendingTarget_PhysicalHalved()
    {
        var state = State2P();
        state.ApplyDefense(1, true, 1); // 目标防御

        var undefended = (PhysicalDamageEvent)Resolver().Resolve(0, Physical(), State2P(), Ctx(7))[0];
        var defended = (PhysicalDamageEvent)Resolver().Resolve(0, Physical(), state, Ctx(7))[0];

        // 同种子同 roll：防御伤害减半（DamageCalculator 0.5——damage calc AC-7）
        Assert.Equal(DamageCalculator.Round1(undefended.DamageDealt * 0.5f), defended.DamageDealt);
        Assert.Equal(defended.DamageDealt, defended.DamageBlocked); // 减免量 = 造成量（B4）
        Assert.Equal(defended.DamageDealt + defended.DamageBlocked, defended.IncomingDamage);
    }

    [Fact]
    public void DualChannel_SameTarget_ChainedCursor()
    {
        // 审计 E8 锚点：M1 物理 + Broca 精神同目标——后事件 Before = 前事件 After（链式游标）
        var state = State2P();
        var action = new CombatAction
        {
            M1 = new ActionSlot { Kind = ActionKind.PhysicalAttack, TargetId = 1 },
            Broca = new ActionSlot { Kind = ActionKind.MentalAttack, TargetId = 1 },
            Order = ChannelOrder.M1First,
        };
        var events = Resolver().Resolve(0, action, state, Ctx());

        Assert.Equal(2, events.Count);
        var physical = (PhysicalDamageEvent)events[0];
        var mental = (MentalDamageEvent)events[1];

        // 链式：精神事件的 Before = 物理事件后的 HP（游标）
        Assert.Equal(physical.TargetHpAfter, mental.TargetHpBefore);
        Assert.Equal(DamageCalculator.Round1(physical.TargetHpAfter - mental.HpDamage), mental.TargetHpAfter);

        // 防御标记：Defend 无事件
        var defendAction = new CombatAction
        {
            M1 = new ActionSlot { Kind = ActionKind.Defend, TargetId = 0 },
            Order = ChannelOrder.M1First,
        };
        Assert.Empty(Resolver().Resolve(0, defendAction, state, Ctx()));
    }

    // ---- 配对校验（审计 W9/W4）----

    [Theory]
    [InlineData(ActionKind.MentalAttack, null)] // M1=MentalAttack 违规
    [InlineData(null, ActionKind.PhysicalAttack)] // Broca=PhysicalAttack 违规
    [InlineData(null, ActionKind.Defend)] // Broca=Defend 违规
    public void ChannelPairing_Invalid_Throws(ActionKind? m1, ActionKind? broca)
    {
        var action = new CombatAction
        {
            M1 = m1 is null ? null : new ActionSlot { Kind = m1.Value, TargetId = 1 },
            Broca = broca is null ? null : new ActionSlot { Kind = broca.Value, TargetId = 1 },
            Order = ChannelOrder.M1First,
        };
        Assert.Throws<ArgumentException>(() => Resolver().Resolve(0, action, State2P(), Ctx()));
    }

    [Fact]
    public void NullArgs_Throw()
    {
        var resolver = Resolver();
        var state = State2P();
        Assert.Throws<ArgumentNullException>(() => resolver.Resolve(0, null!, state, Ctx()));
        Assert.Throws<ArgumentNullException>(() => resolver.Resolve(0, Physical(), null!, Ctx()));
        Assert.Throws<ArgumentNullException>(() => resolver.Resolve(0, Physical(), state, null!));
        Assert.Throws<ArgumentOutOfRangeException>(() => resolver.Resolve(5, Physical(), state, Ctx()));
        Assert.Throws<ArgumentOutOfRangeException>(() => Resolver().Resolve(0, Physical(9), state, Ctx()));
    }
}
