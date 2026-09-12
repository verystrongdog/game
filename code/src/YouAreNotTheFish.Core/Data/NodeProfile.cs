using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// 图节点的功能剖面——聚合了该节点下所有 functional_id 的信号类型和功能标签。
/// 51 个节点各一份，按 dk_name 索引。
/// </summary>
public record NodeProfile
{
    /// <summary>聚合的输入信号类型。</summary>
    [JsonPropertyName("input_types")]
    public string[] InputTypes { get; init; } = [];

    /// <summary>聚合的输出信号类型。</summary>
    [JsonPropertyName("output_types")]
    public string[] OutputTypes { get; init; } = [];

    /// <summary>聚合的玩法域。</summary>
    [JsonPropertyName("gameplay_domains")]
    public GameplayDomain[] GameplayDomains { get; init; } = [];

    /// <summary>聚合的 CSTC 环路。</summary>
    [JsonPropertyName("cstc_loops")]
    public CstcLoop[] CstcLoops { get; init; } = [];

    /// <summary>聚合的 CSTC 角色。</summary>
    [JsonPropertyName("cstc_roles")]
    public CstcRole[] CstcRoles { get; init; } = [];

    /// <summary>聚合的振荡频段。</summary>
    [JsonPropertyName("oscillatory_bands")]
    public OscillatoryBand[] OscillatoryBands { get; init; } = [];

    /// <summary>聚合的神经递质。</summary>
    [JsonPropertyName("neurotransmitters")]
    public Neurotransmitter[] Neurotransmitters { get; init; } = [];
}
