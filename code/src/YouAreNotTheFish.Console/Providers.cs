using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Flow;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.ConsoleApp;

/// <summary>
/// 玩家键盘行动提供者——csharp-console spec@v1.2 §三 3.1。
/// 1v1 场景（TargetId 固定为对方）；非法输入重试最多 3 次后默认等待（EOF/null 计为非法）。
/// </summary>
public sealed class PlayerActionProvider(TextReader input, TextWriter output) : IActionProvider
{
    private const int MaxRetries = 3;

    /// <inheritdoc/>
    public CombatAction GetAction(int participantIndex, CombatState state, CombatContext ctx)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(ctx);
        if (participantIndex < 0 || participantIndex >= state.Participants.Count)
            throw new ArgumentOutOfRangeException(nameof(participantIndex));

        var targetId = FirstEnemy(participantIndex, state);
        for (var attempt = 0; attempt < MaxRetries; attempt++)
        {
            output.Write("[玩家] 行动 (1=物理攻击 2=精神攻击 3=防御 0=等待): ");
            output.Flush();
            var line = input.ReadLine(); // EOF/null → 非法（计数）
            switch (line?.Trim())
            {
                case "1":
                    return new CombatAction { M1 = new ActionSlot { Kind = ActionKind.PhysicalAttack, TargetId = targetId }, Order = ChannelOrder.M1First };
                case "2":
                    return new CombatAction { Broca = new ActionSlot { Kind = ActionKind.MentalAttack, TargetId = targetId }, Order = ChannelOrder.M1First };
                case "3":
                    return new CombatAction { M1 = new ActionSlot { Kind = ActionKind.Defend, TargetId = targetId }, Order = ChannelOrder.M1First };
                case "0":
                    return new CombatAction(); // 0=等待
            }
            // 非法（含 EOF/null——计为一次非法，重试；3 次后默认等待，非交互不挂死）
        }
        return new CombatAction(); // 3 次后默认等待
    }

    /// <summary>目标 = 第一个异队参与者（复用 NpcSalience 同款规则——1v1 即对方）。</summary>
    private static int FirstEnemy(int selfIndex, CombatState state)
    {
        var selfTeam = state.Teams[selfIndex];
        for (var p = 0; p < state.Participants.Count; p++)
            if (p != selfIndex && state.Teams[p] != selfTeam)
                return p;
        return selfIndex;
    }
}

/// <summary>
/// 组合行动提供者——csharp-console spec@v1.2 §三 3.3（v1.2 修正：p 自由变量伪码不可执行，定义类型）。
/// GetAction 内按 participantIndex 分派：p==0 → 玩家键盘、否则 → NPC。
/// </summary>
public sealed class CompositeActionProvider(IActionProvider player, IActionProvider npc) : IActionProvider
{
    /// <inheritdoc/>
    public CombatAction GetAction(int participantIndex, CombatState state, CombatContext ctx)
        => participantIndex == 0 ? player.GetAction(participantIndex, state, ctx)
                                 : npc.GetAction(participantIndex, state, ctx);
}

/// <summary>恒空声明提供者——静息 trace 模式（csharp-console spec@v1.2 §三 3.3）。</summary>
public sealed class WaitProvider : IActionProvider
{
    /// <inheritdoc/>
    public CombatAction GetAction(int participantIndex, CombatState state, CombatContext ctx) => new();
}
