namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 单通道动作槽——回合战斗流程 §2.2（一次一个目标）。TargetId 为 participant 索引，语义由 Flow 层定义。
/// </summary>
public sealed record ActionSlot
{
    /// <summary>动作类型。来源：plan §4.8 3 基础行动（PhysicalAttack/MentalAttack/Defend）。</summary>
    public ActionKind Kind { get; init; }

    /// <summary>目标 participant 索引。来源：回合战斗流程 §2.2。</summary>
    public int TargetId { get; init; }
}

/// <summary>
/// 双通道窗口声明——回合战斗流程 §2.1（每窗口 M1 ≤1 + Broca ≤1，各自独立目标）、§2.3（先后由玩家决定）。
/// 审计修复 #3 产物。
/// </summary>
public sealed record CombatAction
{
    /// <summary>M1 通道动作（可空）。来源：回合战斗流程 §2.1。</summary>
    public ActionSlot? M1 { get; init; }

    /// <summary>Broca 通道动作（可空）。来源：§2.1。</summary>
    public ActionSlot? Broca { get; init; }

    /// <summary>窗口内先后顺序。来源：§2.3。</summary>
    public ChannelOrder Order { get; init; }

    /// <summary>
    /// 双通道合法性校验——spec@v1.1 §三 3.5 真值表（§2.1 防御是 M1 动作 + §7.4 防御期间 Broca 可用）：
    /// Defend 只能作为 m1；broca.Kind==Defend 恒非法（含 m1==null 时——空值短路求值）；
    /// (null, null) 空声明合法（对应等待语义，step 10 ActionResolver 依赖此契约）。
    /// 注：通道-动作类型配对不校验（§2.6 契约自限「Defend 独占 M1」；demo 3 行动集不会产出跨通道组合）。
    /// </summary>
    public static bool IsValidChannelUsage(ActionSlot? m1, ActionSlot? broca) =>
        broca?.Kind != ActionKind.Defend;
}
