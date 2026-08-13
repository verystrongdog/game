using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// brain_regions.json 的根对象——69 个脑区按 functional_id 索引的字典。
/// </summary>
public record BrainRegionsData
{
    [JsonPropertyName("regions")]
    public Dictionary<string, BrainRegion> Regions { get; init; } = new();
}
