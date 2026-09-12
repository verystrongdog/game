using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// 感觉模态输入矩阵（W_sensory.json）——69 个脑区 × 8 种感觉模态的输入连接（0/1）。
/// 数据源: data/connectivity/W_sensory.json
/// 有意不映射: description / grilling / dimensions / modality_nodes /
/// cortical_nodes_with_sensory_input / cortical_nodes_without_sensory_input / metadata。
/// </summary>
public record WsensoryMatrix
{
    /// <summary>8 种感觉模态: visual/auditory/somatosensory/pain/social_cognition/language_cognition/olfactory/thermoreception。</summary>
    [JsonPropertyName("modalities")]
    public string[] Modalities { get; init; } = [];

    /// <summary>69×8 int 矩阵（值 0/1），行序与 Rows 的 key 序一致（spec §五 约束2）。</summary>
    [JsonPropertyName("matrix_2d")]
    public int[][] Matrix { get; init; } = [];

    /// <summary>functional_id → {modality: 0|1}，69 个 key 与 brain_regions functional_ids 双向双射。</summary>
    [JsonPropertyName("rows")]
    public Dictionary<string, Dictionary<string, int>> Rows { get; init; } = new();

    /// <summary>
    /// 每行对应的 functional_id（非 JSON 字段）——由 LoadWsensory 按 Rows.Keys 顺序填充，
    /// 与 Matrix 行序一致（spec §二 2.2）。
    /// </summary>
    public string[] RegionIds { get; init; } = [];
}
