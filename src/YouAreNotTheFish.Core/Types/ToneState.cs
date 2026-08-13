namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 脑干 tone 状态（91 浮点中的 4 个）——运行时状态模型 §5.1/§5.4。
/// 值域 [0,1]（§5.2 clip）。baseline 默认值来源 §5.4。
/// </summary>
public sealed record ToneState
{
    /// <summary>NE_tone：蓝斑去甲肾上腺素 tone，baseline 0.3。来源：运行时状态模型 §5.1/§5.4。</summary>
    public float Ne { get; init; }

    /// <summary>DA_VTA_tone：腹侧被盖区多巴胺 tone，baseline 0.4。来源：§5.1/§5.4。</summary>
    public float DaVta { get; init; }

    /// <summary>DA_SNc_tone：黑质致密部多巴胺 tone，baseline 0.5。来源：§5.1/§5.4。</summary>
    public float DaSnc { get; init; }

    /// <summary>5HT_tone：中缝核血清素 tone，baseline 0.5。来源：§5.1/§5.4。</summary>
    public float Ht5 { get; init; }
}
