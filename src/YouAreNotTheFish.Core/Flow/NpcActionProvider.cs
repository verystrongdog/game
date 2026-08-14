using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Flow;

/// <summary>
/// NPC 行动提供者（demo 适配器）——csharp-flow spec@v1.2 §三 3.1。
/// 固定 Softmax 杂兵模板（plan §4.8）；Boss 模板留接口。
/// 确定性：消费 ctx.Rng（NpcSalience Softmax 抽样）——同种子同输出。
/// </summary>
public sealed class NpcActionProvider : IActionProvider
{
    /// <inheritdoc/>
    public CombatAction GetAction(int participantIndex, CombatState state, CombatContext ctx)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(ctx);
        return NpcSalience.SelectAction(participantIndex, state, ctx);
    }
}
