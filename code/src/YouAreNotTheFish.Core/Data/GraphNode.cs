using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// 三体模型中的图节点——对应一个 FreeSurfer DK 图谱区域（或皮层下/脑干结构）。
/// 51 个节点，按 dk_name 索引。每个节点聚合了其覆盖的所有 functional_id 的信息。
/// </summary>
public record GraphNode
{
    /// <summary>FreeSurfer DK 图谱名称（如 "transversetemporal"），51 个各一。</summary>
    [JsonPropertyName("dk_name")]
    public string DkName { get; init; } = "";

    /// <summary>该图谱节点覆盖的 functional_id 列表（1:1 或 1:N）。</summary>
    [JsonPropertyName("functional_ids")]
    public string[] FunctionalIds { get; init; } = [];

    /// <summary>解剖分类。</summary>
    [JsonPropertyName("category")]
    public BrainRegionCategory Category { get; init; }

    /// <summary>皮层层级（L0-L5）。</summary>
    [JsonPropertyName("level")]
    public int Level { get; init; }

    /// <summary>MNI152 质心坐标 (mm, RAS+)。</summary>
    [JsonPropertyName("mni_xyz")]
    public double[] MniXyz { get; init; } = [];

    /// <summary>该节点覆盖的 functional_id 数量。</summary>
    [JsonPropertyName("profile_count")]
    public int ProfileCount { get; init; }

    /// <summary>是否缺少功能剖面（brainstem 节点可能为 true）。</summary>
    [JsonPropertyName("profile_missing")]
    public bool ProfileMissing { get; init; }

    /// <summary>聚合的玩法域。</summary>
    [JsonPropertyName("gameplay_domains")]
    public GameplayDomain[] GameplayDomains { get; init; } = [];

    /// <summary>聚合的 CSTC 环路归属。</summary>
    [JsonPropertyName("cstc_loops")]
    public CstcLoop[] CstcLoops { get; init; } = [];

    /// <summary>聚合的 CSTC 角色。</summary>
    [JsonPropertyName("cstc_roles")]
    public CstcRole[] CstcRoles { get; init; } = [];

    /// <summary>聚合的时间尺度。</summary>
    [JsonPropertyName("timescales")]
    public Timescale[] Timescales { get; init; } = [];

    /// <summary>聚合的振荡频段。</summary>
    [JsonPropertyName("oscillatory_bands")]
    public OscillatoryBand[] OscillatoryBands { get; init; } = [];

    /// <summary>聚合的神经递质。</summary>
    [JsonPropertyName("neurotransmitters")]
    public Neurotransmitter[] Neurotransmitters { get; init; } = [];
}
