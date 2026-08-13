using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>皮层-皮层连接边（776 条）。source/target 均为 dk_name。</summary>
public record CorticocorticalEdge
{
    [JsonPropertyName("source")] public string Source { get; init; } = "";
    [JsonPropertyName("target")] public string Target { get; init; } = "";
    [JsonPropertyName("direction")] public HierarchyDirection Direction { get; init; }
    [JsonPropertyName("distance_mm")] public double DistanceMm { get; init; }
    [JsonPropertyName("edr_probability")] public double EdrProbability { get; init; }
    [JsonPropertyName("level_diff")] public int LevelDiff { get; init; }
    /// <summary>反向边的 source→target 标识（如 "caudalanteriorcingulate→transversetemporal"）。</summary>
    [JsonPropertyName("reciprocal_of")] public string? ReciprocalOf { get; init; }
    [JsonPropertyName("function_label")] public FunctionLabel[] FunctionLabel { get; init; } = [];
    [JsonPropertyName("gameplay_labels")] public GameplayDomain[] GameplayLabels { get; init; } = [];
    [JsonPropertyName("description")] public string Description { get; init; } = "";
    [JsonPropertyName("role")] public EdgeRole Role { get; init; }
}

/// <summary>脑干投射边（114 条）。source 为 functional_id，target 为 dk_name。</summary>
public record BrainstemProjection
{
    [JsonPropertyName("source")] public string Source { get; init; } = "";
    [JsonPropertyName("target")] public string Target { get; init; } = "";
    [JsonPropertyName("system")] public BrainstemSystem System { get; init; }
    [JsonPropertyName("neurotransmitter")] public Neurotransmitter Neurotransmitter { get; init; }
    [JsonPropertyName("projection")] public BrainstemProjectionType Projection { get; init; }
    [JsonPropertyName("description")] public string Description { get; init; } = "";
    [JsonPropertyName("function_label")] public FunctionLabel[] FunctionLabel { get; init; } = [];
    [JsonPropertyName("gameplay_labels")] public GameplayDomain[] GameplayLabels { get; init; } = [];
    [JsonPropertyName("role")] public EdgeRole Role { get; init; }
}

/// <summary>CSTC 环路边（47 条）。source/target 均为 dk_name。</summary>
public record CstcEdge
{
    [JsonPropertyName("source")] public string Source { get; init; } = "";
    [JsonPropertyName("target")] public string Target { get; init; } = "";
    [JsonPropertyName("loop")] public CstcLoop Loop { get; init; }
    [JsonPropertyName("pathway")] public CstcPathway Pathway { get; init; }
    [JsonPropertyName("station_from")] public CstcStation StationFrom { get; init; }
    [JsonPropertyName("station_to")] public CstcStation StationTo { get; init; }
    [JsonPropertyName("description")] public string Description { get; init; } = "";
    [JsonPropertyName("function_label")] public FunctionLabel[] FunctionLabel { get; init; } = [];
    [JsonPropertyName("gameplay_labels")] public GameplayDomain[] GameplayLabels { get; init; } = [];
    [JsonPropertyName("role")] public EdgeRole Role { get; init; }
}

/// <summary>特化通路（112 条）——跨层级快速通道（杏仁核捷径、穿通通路等）。source/target 为 dk_name 或 functional_id。</summary>
public record PrivilegedPathway
{
    [JsonPropertyName("source")] public string Source { get; init; } = "";
    [JsonPropertyName("target")] public string Target { get; init; } = "";
    [JsonPropertyName("pathway_class")] public string PathwayClass { get; init; } = "";
    [JsonPropertyName("anatomical_basis")] public string AnatomicalBasis { get; init; } = "";
    [JsonPropertyName("direction")] public HierarchyDirection Direction { get; init; }
    [JsonPropertyName("distance_mm")] public double DistanceMm { get; init; }
    [JsonPropertyName("edr_probability")] public double EdrProbability { get; init; }
    [JsonPropertyName("level_diff")] public int LevelDiff { get; init; }
    [JsonPropertyName("function_label")] public FunctionLabel[] FunctionLabel { get; init; } = [];
    [JsonPropertyName("gameplay_labels")] public GameplayDomain[] GameplayLabels { get; init; } = [];
    [JsonPropertyName("description")] public string Description { get; init; } = "";
    [JsonPropertyName("role")] public EdgeRole Role { get; init; }
}
