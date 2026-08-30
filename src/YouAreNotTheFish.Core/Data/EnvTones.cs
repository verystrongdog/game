using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// 环境基调表（env_tones.json）——Grilling #108 Q3/Q5 契约。
/// 环境键 = 英文 slug id + display_name 中文显示名；`situation.primary` 引用情境原型 name（不复制内容）；
/// 无 alternates 字段（#108 Q5 已删除——恐慌偏移统一走全局 G 组）。
/// 数据源: data/connectivity/env_tones.json（根 key: environments）
/// </summary>
public sealed record EnvTones
{
    [JsonPropertyName("schema")]
    public string Schema { get; init; } = "";

    [JsonPropertyName("version")]
    public int Version { get; init; }

    [JsonPropertyName("modalities")]
    public string[] Modalities { get; init; } = [];

    [JsonPropertyName("environments")]
    public Dictionary<string, EnvironmentTone> Environments { get; init; } = new();
}

/// <summary>单环境基调（Q3：alpha_env 恰好 8 值 ∈ [0,1]；Q5：situation.primary 引用原型 name）。</summary>
public sealed record EnvironmentTone
{
    [JsonPropertyName("display_name")]
    public string DisplayName { get; init; } = "";

    [JsonPropertyName("alpha_env")]
    public double[] AlphaEnv { get; init; } = [];

    [JsonPropertyName("situation")]
    public EnvironmentSituation Situation { get; init; } = new();
}

/// <summary>环境 → 情境原型引用（Q5：仅 primary，无 alternates）。</summary>
public sealed record EnvironmentSituation
{
    [JsonPropertyName("primary")]
    public string Primary { get; init; } = "";
}
