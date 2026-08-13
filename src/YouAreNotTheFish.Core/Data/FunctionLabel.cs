using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// 边的功能信号标注（CSTC 和 privilege 通路共用）。
/// 出现在 function_label 数组中；数组为空表示无功能信号交集（silent 边）。
/// </summary>
public record FunctionLabel
{
    /// <summary>信号类型，格式 category/subtype（如 "excitation/motor_command"）。</summary>
    [JsonPropertyName("signal_type")]
    public string SignalType { get; init; } = "";

    /// <summary>信号大类（如 "excitation", "plasticity", "gating"）。</summary>
    [JsonPropertyName("category")]
    public string Category { get; init; } = "";

    /// <summary>信号子类（如 "motor_command", "context_code"）。</summary>
    [JsonPropertyName("subtype")]
    public string Subtype { get; init; } = "";

    /// <summary>信号类型的定义说明。</summary>
    [JsonPropertyName("definition")]
    public string Definition { get; init; } = "";
}
