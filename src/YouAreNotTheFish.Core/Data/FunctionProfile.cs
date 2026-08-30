using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// 单个脑区的功能剖面（brain_regions.json 中每个 region 的 function_profile 字段）。
/// 69 个脑区各有一份；其中 2 个（LocusCoeruleusRight, SubstantiaNigraParsCompactaRight）
/// 通过 MirrorOf 指向左半球主变体——Grilling #92 D6：镜像复制主变体完整剖面 + mirror_of 溯源
/// （偏侧化架构 §五/§9.2 T8）。
/// </summary>
public record FunctionProfile
{
    /// <summary>主要功能描述（英文）。</summary>
    [JsonPropertyName("primary_function")]
    public string PrimaryFunction { get; init; } = "";

    /// <summary>输入信号类型，格式 category/subtype（如 "gating/disinhibition_thalamic"）。</summary>
    [JsonPropertyName("input_types")]
    public string[] InputTypes { get; init; } = [];

    /// <summary>输出信号类型，格式 category/subtype（如 "excitation/sensory_feature"）。</summary>
    [JsonPropertyName("output_types")]
    public string[] OutputTypes { get; init; } = [];

    /// <summary>时间尺度：Fast (τ=0.01s) / Medium (τ=0.05s) / Slow (τ=0.15s)。</summary>
    [JsonPropertyName("timescale")]
    public Timescale? Timescale { get; init; }

    /// <summary>主导神经递质。</summary>
    [JsonPropertyName("neurotransmitter_dominant")]
    public Neurotransmitter? NeurotransmitterDominant { get; init; }

    /// <summary>主导振荡频段。</summary>
    [JsonPropertyName("oscillatory_band")]
    public OscillatoryBand? OscillatoryBand { get; init; }

    /// <summary>CSTC 环路归属。</summary>
    [JsonPropertyName("cstc_loop")]
    public CstcLoop? CstcLoop { get; init; }

    /// <summary>CSTC 角色。</summary>
    [JsonPropertyName("cstc_role")]
    public CstcRole? CstcRole { get; init; }

    /// <summary>层级信息流方向。</summary>
    [JsonPropertyName("hierarchy_direction")]
    public HierarchyDirection? HierarchyDirection { get; init; }

    /// <summary>玩法域分类。</summary>
    [JsonPropertyName("gameplay_domain")]
    public GameplayDomain? GameplayDomain { get; init; }

    /// <summary>
    /// 镜像引用——仅 2 个脑区（LocusCoeruleusRight, SubstantiaNigraParsCompactaRight）
    /// 使用此字段指向左半球的剖面。69 个脑区中仅此 2 个有此字段。
    /// </summary>
    [JsonPropertyName("mirror_of")]
    public string? MirrorOf { get; init; }
}
