namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 动作类型——plan §4.8 3 基础行动候选（demo 战斗动作全集）。
/// </summary>
public enum ActionKind
{
    /// <summary>物理攻击（M1 通道）。</summary>
    PhysicalAttack,

    /// <summary>精神攻击（Broca 通道）。</summary>
    MentalAttack,

    /// <summary>防御（独占 M1 通道，回合战斗流程 §2.1）。</summary>
    Defend,
}

/// <summary>
/// 双通道窗口内先后顺序——回合战斗流程 §2.3（先后由玩家决定）。
/// </summary>
public enum ChannelOrder
{
    /// <summary>先 M1 后 Broca。</summary>
    M1First,

    /// <summary>先 Broca 后 M1。</summary>
    BrocaFirst,
}

/// <summary>
/// Gurney 环路 5 群体索引——运行时状态模型 §6.3（索引序即本枚举序：0=SD1, 1=SD2, 2=STN, 3=GPe, 4=GPi）。
/// </summary>
public enum GurneyPopulation
{
    Sd1 = 0,
    Sd2 = 1,
    Stn = 2,
    GPe = 3,
    GPi = 4,
}

/// <summary>
/// 状态变化事件类型——运行时状态模型 §5.5（C1 Panic / D 注 Downed）。
/// </summary>
public enum StatusKind
{
    /// <summary>SAN 低于 30% 阈值跨越（§5.5 C1）。</summary>
    Panic,

    /// <summary>HP ≤ 0 倒下（§5.5 D 注）。</summary>
    Downed,
}
