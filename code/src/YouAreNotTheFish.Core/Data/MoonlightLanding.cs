using System.Text.Json;
using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// 月光场落点数据（moonlight_landing.json）——Grilling #108 Q9 契约（#101 R 落点落地）。
/// 参数形式 schema：semantics[]（id/primary[4]/secondary[8]/r/alpha_s）；r/α_s = 字符串 "PLACEHOLDER"
/// （r=PLACEHOLDER → 按 r=1 均匀分配 12 落点权重：主 r/(4r+8) / 辅 1/(4r+8)）。
/// 预计算 v^norm 数组不作第二数据源（防双源漂移）；字段缺失 ≠ PLACEHOLDER（load error）。
/// 数据源: data/connectivity/moonlight_landing.json
/// </summary>
public sealed record MoonlightLanding
{
    [JsonPropertyName("schema")]
    public string Schema { get; init; } = "";

    [JsonPropertyName("version")]
    public int Version { get; init; }

    [JsonPropertyName("calibration_status")]
    public string CalibrationStatus { get; init; } = "";

    [JsonPropertyName("calibration_version")]
    public int CalibrationVersion { get; init; }

    [JsonPropertyName("semantics")]
    public List<LandingSemantics> Semantics { get; init; } = [];
}

/// <summary>单一语义落点组（Q9：primary[4] + secondary[8] = 12 落点；r/α_s 参数或 PLACEHOLDER）。</summary>
public sealed record LandingSemantics
{
    [JsonPropertyName("id")]
    public string Id { get; init; } = "";

    [JsonPropertyName("primary")]
    public string[] Primary { get; init; } = [];

    [JsonPropertyName("secondary")]
    public string[] Secondary { get; init; } = [];

    [JsonPropertyName("r")]
    public string R { get; init; } = "";

    [JsonPropertyName("alpha_s")]
    public string AlphaS { get; init; } = "";
}
