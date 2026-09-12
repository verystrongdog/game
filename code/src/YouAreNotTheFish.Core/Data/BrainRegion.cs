using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// brain_regions.json 中单个脑区的完整数据（50 解剖实体 + 19 细分 = 69 functional_id）。
/// </summary>
public record BrainRegion
{
    /// <summary>规范标识符（如 "TransverseTemporal", "PeriaqueductalGray"），69 个脑区各一。</summary>
    [JsonPropertyName("functional_id")]
    public string FunctionalId { get; init; } = "";

    /// <summary>中文简称（如 "A1", "PAG", "ACC"）。</summary>
    [JsonPropertyName("zh_name")]
    public string ZhName { get; init; } = "";

    /// <summary>英文全称（如 "Primary Auditory Cortex (A1, BA41, Heschl's Gyrus)"）。</summary>
    [JsonPropertyName("std_name")]
    public string StdName { get; init; } = "";

    /// <summary>
    /// FreeSurfer DK 图谱名称（如 "transversetemporal"）。
    /// 11 个脑干核团（category=brainstem）为 null——它们没有皮层标签。
    /// </summary>
    [JsonPropertyName("dk_name")]
    public string? DkName { get; init; }

    /// <summary>解剖分类：Cortical（44）/ Subcortical（14）/ Brainstem（11）。</summary>
    [JsonPropertyName("category")]
    public BrainRegionCategory Category { get; init; }

    /// <summary>脑叶归属（如 "temporal", "cingulate", "midbrain"）。</summary>
    [JsonPropertyName("lobe")]
    public string Lobe { get; init; } = "";

    /// <summary>皮层层级（L0-L5；brainstem 核团为 L0）。</summary>
    [JsonPropertyName("level")]
    public int Level { get; init; }

    /// <summary>是否为占位设计节点（当前 69 个全为 false）。</summary>
    [JsonPropertyName("is_design_node")]
    public bool IsDesignNode { get; init; }

    /// <summary>MNI152 坐标 (mm, RAS+): [X, Y, Z]。</summary>
    [JsonPropertyName("mni_xyz")]
    public double[] MniXyz { get; init; } = [];

    /// <summary>MNI 坐标来源：literature_mni（文献）或 obj_centroid（Blender 网格中心）。</summary>
    [JsonPropertyName("mni_xyz_source")]
    public string MniXyzSource { get; init; } = "";

    /// <summary>游戏世界空间坐标 [X, Y, Z]——由 MNI 经 transform 公式预计算。</summary>
    [JsonPropertyName("game_xyz")]
    public double[] GameXyz { get; init; } = [];

    /// <summary>FreeSurfer 顶点坐标，32 个脑区为 null。</summary>
    [JsonPropertyName("fs_xyz")]
    public double[]? FsXyz { get; init; }

    /// <summary>Blender .obj 模型文件路径，brainstem 核团为 null。</summary>
    [JsonPropertyName("obj_file")]
    public string? ObjFile { get; init; }

    /// <summary>中文设计注记，可为 null。</summary>
    [JsonPropertyName("notes")]
    public string? Notes { get; init; }

    /// <summary>半球标注——仅在 LocusCoeruleusRight 和 SubstantiaNigraParsCompactaRight 出现。</summary>
    [JsonPropertyName("hemisphere")]
    public string? Hemisphere { get; init; }

    /// <summary>功能剖面（信号类型、CSTC 环路、玩法域等）。69 个脑区各有一份，从不为 null。</summary>
    [JsonPropertyName("function_profile")]
    public FunctionProfile FunctionProfile { get; init; } = new();
}
