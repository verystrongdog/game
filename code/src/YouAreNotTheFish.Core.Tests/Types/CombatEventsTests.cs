using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Types;

/// <summary>AC-4（4 事件类型字段覆盖 §5.5 m 公式 + §九 console 消费需求——测试构造各事件）。</summary>
public class CombatEventsTests
{
    [Fact]
    public void PhysicalDamageEvent_CarriesAllFormulaFactors()
    {
        // §5.5 m 公式输入：A1/A2 actual/expected、B1 |ΔHP|/HP_max、A5/B2 blocked/incoming
        var e = new PhysicalDamageEvent(round: 1, actorId: 0, targetId: 1)
        {
            Hit = true,
            BaseDamage = 4,
            WeaponBonus = 2,
            ForceMod = 1.1f,
            MotivationMod = 1.3f,
            GateBonus = 1.05f,
            DamageDealt = 3,      // actual
            DamageBlocked = 3,    // blocked（防御减半）
            IncomingDamage = 6,   // incoming
            TargetHpBefore = 15,
            TargetHpAfter = 12,
            TargetHpMax = 15,
        };

        Assert.Equal(1, e.Round);
        Assert.Equal(0, e.ActorId);
        Assert.Equal(1, e.TargetId);
        Assert.True(e.Hit);
        Assert.Equal(4, e.BaseDamage);
        Assert.Equal(2, e.WeaponBonus);
        Assert.Equal(1.1f, e.ForceMod);
        Assert.Equal(1.3f, e.MotivationMod);
        Assert.Equal(1.05f, e.GateBonus);
        Assert.Equal(3, e.DamageDealt);
        Assert.Equal(3, e.DamageBlocked);
        Assert.Equal(6, e.IncomingDamage);
        Assert.Equal(15, e.TargetHpBefore);
        Assert.Equal(12, e.TargetHpAfter);
        Assert.Equal(15, e.TargetHpMax);
    }

    [Fact]
    public void MentalDamageEvent_CarriesSanAndHpState()
    {
        // §5.5 m 公式输入：A4 actual/expected、B4 |ΔSAN|/SAN_max
        var e = new MentalDamageEvent(round: 2, actorId: 0, targetId: 1)
        {
            SanDamage = 3,
            HpDamage = 0,
            MotivationMod = 1.0f,
            GateBonus = 0.9f,
            TargetSanBefore = 60,
            TargetSanAfter = 57,
            TargetSanMax = 60,
            TargetHpBefore = 15,
            TargetHpAfter = 15,
            TargetHpMax = 15,
        };

        Assert.Equal(3, e.SanDamage);
        Assert.Equal(1.0f, e.MotivationMod);
        Assert.Equal(0.9f, e.GateBonus);
        Assert.Equal(60, e.TargetSanBefore);
        Assert.Equal(57, e.TargetSanAfter);
        Assert.Equal(60, e.TargetSanMax);
    }

    [Fact]
    public void HealEvent_CarriesAmount()
    {
        var e = new HealEvent(round: 1, actorId: 1, targetId: 1) { HealAmount = 5 };
        Assert.Equal(5, e.HealAmount);
        Assert.Equal(1, e.ActorId);
        Assert.Equal(1, e.TargetId);
    }

    [Fact]
    public void StatusChangeEvent_CarriesKindAndDirection()
    {
        // §5.5 C1 Panic（SAN<30% 跨越）/ D 注 Downed
        var panic = new StatusChangeEvent(round: 3, actorId: 1, targetId: 1) { Kind = StatusKind.Panic, Entered = true };
        Assert.Equal(StatusKind.Panic, panic.Kind);
        Assert.True(panic.Entered);

        var downed = new StatusChangeEvent(round: 3, actorId: 1, targetId: 1) { Kind = StatusKind.Downed, Entered = true };
        Assert.Equal(StatusKind.Downed, downed.Kind);
        Assert.True(downed.Entered);
    }

    [Fact]
    public void LinkGrowthEvent_CarriesLinkAndDelta()
    {
        var e = new LinkGrowthEvent(round: 1, actorId: 0, targetId: 1) { LinkId = "a1-a2", DeltaM = 0.05f };
        Assert.Equal("a1-a2", e.LinkId);
        Assert.Equal(0.05f, e.DeltaM);
    }

    [Fact]
    public void Events_AreDistinctTypes()
    {
        // 类型层次：Physical/Mental 为兄弟子类，无 DamageEvent 中间层（spec@v1.1 §二 2.11 偏差声明）。
        // 兄弟互斥由 sealed 编译期保证（CS0184 会拦截不存在的转换），此处仅验证共同基类。
        var physical = new PhysicalDamageEvent(1, 0, 1);
        var mental = new MentalDamageEvent(1, 0, 1);

        Assert.IsAssignableFrom<CombatEvent>(physical);
        Assert.IsAssignableFrom<CombatEvent>(mental);
        Assert.NotEqual(physical.GetType(), mental.GetType());
    }
}
