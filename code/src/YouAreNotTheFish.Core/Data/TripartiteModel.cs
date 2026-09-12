using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// tripartite_model.json 的根对象——51 节点图 + 三种通信原语 + 特化通路。
/// Grilling #26 (2026-08-07)：皮层-皮层、脑干广播、CSTC 环路三体模型。
/// </summary>
public record TripartiteModel
{
    /// <summary>51 个图节点，按 dk_name 索引。</summary>
    [JsonPropertyName("graph_nodes")]
    public Dictionary<string, GraphNode> GraphNodes { get; init; } = new();

    /// <summary>51 个节点的功能剖面，按 dk_name 索引。</summary>
    [JsonPropertyName("node_profiles")]
    public Dictionary<string, NodeProfile> NodeProfiles { get; init; } = new();

    /// <summary>776 条皮层-皮层连接。</summary>
    [JsonPropertyName("corticocortical")]
    public List<CorticocorticalEdge> Corticocortical { get; init; } = [];

    /// <summary>114 条脑干广播投射。</summary>
    [JsonPropertyName("brainstem")]
    public List<BrainstemProjection> Brainstem { get; init; } = [];

    /// <summary>47 条 CSTC 环路边。</summary>
    [JsonPropertyName("cstc")]
    public List<CstcEdge> Cstc { get; init; } = [];

    /// <summary>112 条特化通路。</summary>
    [JsonPropertyName("privileged_pathways")]
    public List<PrivilegedPathway> PrivilegedPathways { get; init; } = [];
}
