using System.Text.Json;
using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// α pattern 数据表（alpha_patterns.json）——Grilling #108 Q1 契约。
/// `row_id → pattern[8]`；行 id ↔ 派生分支绑定留代码（EventProcessor Emit 调用点持有
/// A1/A2/A4/A5/B1/B2/B4/C1/D1/D2），JSON 不描述触发分支。
/// 数据源: data/connectivity/alpha_patterns.json（根 key: events）
/// </summary>
public sealed record AlphaPatterns
{
    [JsonPropertyName("schema")]
    public string Schema { get; init; } = "";

    [JsonPropertyName("version")]
    public int Version { get; init; }

    [JsonPropertyName("modalities")]
    public string[] Modalities { get; init; } = [];

    [JsonPropertyName("events")]
    public Dictionary<string, AlphaPatternEntry> Events { get; init; } = new();
}

/// <summary>单事件 α pattern 行（Q1 契约：pattern 恰好 8 值；m_alpha 二态）。</summary>
public sealed record AlphaPatternEntry
{
    [JsonPropertyName("trigger")]
    public string Trigger { get; init; } = "";

    [JsonPropertyName("pattern")]
    public int[] Pattern { get; init; } = [];

    [JsonPropertyName("m_alpha")]
    public MAlphaValue MAlpha { get; init; }
}

/// <summary>
/// m_alpha 二态（Q1）：有限数字 [0,1] = 常量（A 类 = 1.0）∪ "m_delta" = 用该分支现有算法计算 m。
/// 自定义 converter 保证：类型非法 / 数值越界 / 非 "m_delta" 字符串 → JsonException（加载期 fail-fast）。
/// </summary>
[JsonConverter(typeof(MAlphaValueConverter))]
public readonly record struct MAlphaValue(double? Constant, bool IsDelta)
{
    public static MAlphaValue ConstantValue(double value) => new(value, false);
    public static MAlphaValue Delta() => new(null, true);

    public override string ToString() => IsDelta ? "m_delta" : Constant?.ToString("R") ?? "?";
}

/// <summary>m_alpha 二态解析 converter——非法形态抛 JsonException（Q1 契约，接 #106 分层）。</summary>
public sealed class MAlphaValueConverter : JsonConverter<MAlphaValue>
{
    public override MAlphaValue Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        if (reader.TokenType == JsonTokenType.Number)
        {
            var v = reader.GetDouble();
            if (double.IsNaN(v) || double.IsInfinity(v) || v < 0.0 || v > 1.0)
                throw new JsonException($"m_alpha 数值越界（须 ∈ [0,1]）: {v}");
            return MAlphaValue.ConstantValue(v);
        }
        if (reader.TokenType == JsonTokenType.String)
        {
            var s = reader.GetString();
            if (s == "m_delta")
                return MAlphaValue.Delta();
            throw new JsonException($"m_alpha 字符串非法（仅允许 \"m_delta\"）: \"{s}\"");
        }
        throw new JsonException($"m_alpha 类型非法（须为有限数字 [0,1] 或字符串 \"m_delta\"）: {reader.TokenType}");
    }

    public override void Write(Utf8JsonWriter writer, MAlphaValue value, JsonSerializerOptions options)
    {
        if (value.IsDelta)
            writer.WriteStringValue("m_delta");
        else
            writer.WriteNumberValue(value.Constant ?? 0.0);
    }
}
