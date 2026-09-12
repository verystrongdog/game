using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Types;

/// <summary>AC-8（IsValidChannelUsage 双通道约束，spec@v1.1 §三 3.5 真值表）。</summary>
public class CombatActionTests
{
    private static ActionSlot M1(ActionKind kind) => new() { Kind = kind, TargetId = 1 };
    private static ActionSlot Broca(ActionKind kind) => new() { Kind = kind, TargetId = 1 };

    [Fact]
    public void Defend_OnlyAllowedInM1()
    {
        // Defend 只能作为 m1（§2.1 防御是 M1 动作）
        Assert.True(CombatAction.IsValidChannelUsage(M1(ActionKind.Defend), null));
        Assert.True(CombatAction.IsValidChannelUsage(M1(ActionKind.Defend), Broca(ActionKind.MentalAttack)));
        Assert.False(CombatAction.IsValidChannelUsage(null, Broca(ActionKind.Defend)));
        Assert.False(CombatAction.IsValidChannelUsage(M1(ActionKind.PhysicalAttack), Broca(ActionKind.Defend)));
    }

    [Fact]
    public void NullNull_IsValid()
    {
        // (null, null) 空声明合法（对应等待语义，step 10 依赖）
        Assert.True(CombatAction.IsValidChannelUsage(null, null));
    }

    [Fact]
    public void NormalCombinations_AreValid()
    {
        // 双通道正常组合（§7.4 防御期间 Broca 仍可用已在上方覆盖）
        Assert.True(CombatAction.IsValidChannelUsage(M1(ActionKind.PhysicalAttack), Broca(ActionKind.MentalAttack)));
        Assert.True(CombatAction.IsValidChannelUsage(M1(ActionKind.PhysicalAttack), null));
        Assert.True(CombatAction.IsValidChannelUsage(null, Broca(ActionKind.MentalAttack)));
    }
}
