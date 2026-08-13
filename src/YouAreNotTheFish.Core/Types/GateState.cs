namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 三环路门控状态（91 浮点中的 3 个）——运行时状态模型 §6.4。
/// gate_loop = 1 − O_GPi_loop，值域 [0,1]（gate=1 全放行，gate=0 完全门控抑制）。
/// </summary>
public sealed record GateState
{
    /// <summary>gate_somatic。来源：运行时状态模型 §6.4。</summary>
    public float GateSomatic { get; init; }

    /// <summary>gate_cognitive。来源：§6.4。</summary>
    public float GateCognitive { get; init; }

    /// <summary>gate_limbic。来源：§6.4。</summary>
    public float GateLimbic { get; init; }
}
