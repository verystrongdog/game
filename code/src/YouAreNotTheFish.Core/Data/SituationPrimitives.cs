using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// 情境原型集合（situation_primitives.json）——27 个有效情境原型（31 中 4 个已废弃）。
/// 数据源: data/connectivity/situation_primitives.json（根 key: situation_archetypes）
/// 有意不映射: _metadata / rdoc_domains / appraisal_dimensions /
/// game_levels / composition_rules（自描述元数据）。
/// </summary>
public record SituationPrimitives
{
    [JsonPropertyName("situation_archetypes")]
    public List<SituationArchetype> Archetypes { get; init; } = [];

    /// <summary>
    /// Kroell 14 网络注册表（根 key: functional_networks.networks）——**只映射 name**。
    /// 映射它的理由不是消费，而是**加载期引用完整性校验**：`primary_networks` 必须
    /// 指向注册表内的网络名（spec §五 约束10）。此前该字段整体未映射，于是"指向不存在
    /// 的网络"在加载期完全不可见（P4c fixture `SP-network-registry` 覆盖）。
    /// </summary>
    [JsonPropertyName("functional_networks")]
    public FunctionalNetworks FunctionalNetworks { get; init; } = new();
}

/// <summary>`functional_networks` 根对象（其余字段有意不映射）。</summary>
public record FunctionalNetworks
{
    [JsonPropertyName("networks")]
    public List<RegisteredNetwork> Networks { get; init; } = [];
}

/// <summary>注册表内的单个网络条目。</summary>
public record RegisteredNetwork
{
    [JsonPropertyName("name")]
    public string Name { get; init; } = "";
}

/// <summary>单个情境原型。</summary>
public record SituationArchetype
{
    /// <summary>英文标识名。</summary>
    [JsonPropertyName("name")]
    public string Name { get; init; } = "";

    [JsonPropertyName("display_name")]
    public string DisplayName { get; init; } = "";

    [JsonPropertyName("summary")]
    public string Summary { get; init; } = "";

    /// <summary>RDoC 六域剖面（各 archetype 只含 3-4 域子集）。</summary>
    [JsonPropertyName("rdoc_profile")]
    public RdocProfile RdocProfile { get; init; } = new();

    /// <summary>认知评估剖面。</summary>
    [JsonPropertyName("appraisal_profile")]
    public AppraisalProfile AppraisalProfile { get; init; } = new();

    /// <summary>主功能网络名，∈ 同文件 functional_networks.networks 注册表（spec §五 约束10）。</summary>
    [JsonPropertyName("primary_networks")]
    public string[] PrimaryNetworks { get; init; } = [];

    /// <summary>关键脑区（functional_id），∈ brain_regions functional_ids（spec §五 约束3）。</summary>
    [JsonPropertyName("key_brain_regions")]
    public string[] KeyBrainRegions { get; init; } = [];

    /// <summary>涉及的层级，值域 L0..L5（spec §五 约束4）。</summary>
    [JsonPropertyName("levels_involved")]
    public string[] LevelsInvolved { get; init; } = [];

    /// <summary>
    /// ⚠️ legacy：指向已废弃 364 链路模型（Grilling #26 前），不做校验，待 CSTC 词表迁移
    /// （spec §五 C11）。
    /// </summary>
    [JsonPropertyName("auto_activated_links")]
    public string[] AutoActivatedLinks { get; init; } = [];

    [JsonPropertyName("typical_game_scenario")]
    public string TypicalGameScenario { get; init; } = "";
}

/// <summary>RDoC 六域剖面——各 archetype 只含子集，全部可空（spec §二 2.2）。</summary>
public record RdocProfile
{
    [JsonPropertyName("social_processes")]
    public double? SocialProcesses { get; init; }

    [JsonPropertyName("negative_valence")]
    public double? NegativeValence { get; init; }

    [JsonPropertyName("cognitive_systems")]
    public double? CognitiveSystems { get; init; }

    [JsonPropertyName("positive_valence")]
    public double? PositiveValence { get; init; }

    [JsonPropertyName("arousal_regulatory")]
    public double? ArousalRegulatory { get; init; }

    [JsonPropertyName("sensorimotor")]
    public double? Sensorimotor { get; init; }
}

/// <summary>认知评估剖面（Smith & Lazarus 评估理论）。</summary>
public record AppraisalProfile
{
    /// <summary>值域: circumstance | other | self（spec §四：保持 string，不进 enum）。</summary>
    [JsonPropertyName("agency")]
    public string Agency { get; init; } = "";

    /// <summary>值域: ambiguous | negative | positive。</summary>
    [JsonPropertyName("valence")]
    public string Valence { get; init; } = "";

    [JsonPropertyName("goal_relevance")]
    public double GoalRelevance { get; init; }

    [JsonPropertyName("coping")]
    public double Coping { get; init; }

    [JsonPropertyName("certainty")]
    public double Certainty { get; init; }

    [JsonPropertyName("novelty")]
    public double Novelty { get; init; }

    [JsonPropertyName("norm_compatibility")]
    public double NormCompatibility { get; init; }
}
