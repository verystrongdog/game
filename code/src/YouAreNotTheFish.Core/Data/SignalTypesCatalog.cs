using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// 信号类型受控词表（signal_types.json）——4 类目 × 18 子类。
/// 数据源: data/signal_types.json（根 key: _categories / _description）
/// 有意不映射: _usage / _validation_rules / _created / _grilling（元数据）。
/// </summary>
public record SignalTypesCatalog
{
    [JsonPropertyName("_description")]
    public string Description { get; init; } = "";

    /// <summary>类目名（excitation/modulation/gating/plasticity）→ 类目定义。</summary>
    [JsonPropertyName("_categories")]
    public Dictionary<string, SignalCategory> Categories { get; init; } = new();
}

/// <summary>单个信号类目。</summary>
public record SignalCategory
{
    [JsonPropertyName("definition")]
    public string Definition { get; init; } = "";

    [JsonPropertyName("source")]
    public string Source { get; init; } = "";

    /// <summary>子类名（如 go_direct）→ 子类定义。</summary>
    [JsonPropertyName("subtypes")]
    public Dictionary<string, SignalSubtype> Subtypes { get; init; } = new();
}

/// <summary>
/// 单个信号子类——字段按类目异构，未出现的 key 为 null（spec §二 2.2）：
/// excitation 有 oscillatory_band；modulation 有 neurotransmitter/projection_pattern/target_scope；
/// gating 有 pathway/effect；plasticity 有 mechanism。
/// </summary>
public record SignalSubtype
{
    [JsonPropertyName("definition")]
    public string Definition { get; init; } = "";

    [JsonPropertyName("anatomical_carriers")]
    public string[] AnatomicalCarriers { get; init; } = [];

    /// <summary>仅 excitation 6 子类有。</summary>
    [JsonPropertyName("oscillatory_band")]
    public string? OscillatoryBand { get; init; }

    /// <summary>仅 modulation 5 子类有。</summary>
    [JsonPropertyName("neurotransmitter")]
    public string? Neurotransmitter { get; init; }

    /// <summary>仅 modulation 5 子类有。</summary>
    [JsonPropertyName("projection_pattern")]
    public string? ProjectionPattern { get; init; }

    /// <summary>仅 modulation 5 子类有。</summary>
    [JsonPropertyName("target_scope")]
    public string? TargetScope { get; init; }

    /// <summary>仅 gating 4 子类有。</summary>
    [JsonPropertyName("pathway")]
    public string? Pathway { get; init; }

    /// <summary>仅 gating 4 子类有。</summary>
    [JsonPropertyName("effect")]
    public string? Effect { get; init; }

    /// <summary>仅 plasticity 3 子类有。</summary>
    [JsonPropertyName("mechanism")]
    public string? Mechanism { get; init; }
}
