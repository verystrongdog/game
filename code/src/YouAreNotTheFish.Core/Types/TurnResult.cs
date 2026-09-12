namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 回合结果——框架 memory code-framework-plan-2026-08-06 §3.5（引擎输出）+ plan §三。
/// Round 为结果标注（回合计数归 CombatState，plan §五 5.1）。
/// 构造时防御性拷贝（约束 C7）。
/// </summary>
public sealed record TurnResult
{
    /// <summary>回合编号（标注用）。来源：plan §五 5.1。</summary>
    public int Round { get; }

    /// <summary>本回合引擎输出事件列表。来源：框架 memory §3.5。</summary>
    public IReadOnlyList<CombatEvent> Events { get; }

    /// <summary>参与者状态快照。来源：框架 memory §3.5「参与者快照」。</summary>
    public IReadOnlyList<ParticipantState> ParticipantSnapshots { get; }

    /// <summary>从任意可枚举构造——立即拷贝为数组。</summary>
    public TurnResult(int round, IEnumerable<CombatEvent> events, IEnumerable<ParticipantState> participantSnapshots)
    {
        Round = round;
        Events = events.ToArray();
        ParticipantSnapshots = participantSnapshots.ToArray();
    }
}
