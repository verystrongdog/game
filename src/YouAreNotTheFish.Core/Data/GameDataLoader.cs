using System.Text.Json;
using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// 从 JSON 文件加载游戏数据。所有路径在调用时传入，无隐式依赖。
/// </summary>
public static class GameDataLoader
{
    private static readonly JsonSerializerOptions Options = new()
    {
        PropertyNameCaseInsensitive = true,
        ReadCommentHandling = JsonCommentHandling.Skip,
    };

    /// <summary>从脑区 JSON 文件加载 69 个脑区。</summary>
    public static BrainRegionsData LoadBrainRegions(string jsonPath)
    {
        var json = File.ReadAllText(jsonPath);
        return JsonSerializer.Deserialize<BrainRegionsData>(json, Options)
               ?? throw new InvalidOperationException($"Failed to deserialize {jsonPath}");
    }

    /// <summary>从三体模型 JSON 文件加载 51 节点 + 4 种边数据。</summary>
    public static TripartiteModel LoadTripartiteModel(string jsonPath)
    {
        var json = File.ReadAllText(jsonPath);
        return JsonSerializer.Deserialize<TripartiteModel>(json, Options)
               ?? throw new InvalidOperationException($"Failed to deserialize {jsonPath}");
    }

    /// <summary>从 W_sensory.json 加载 69×6 感觉模态矩阵，并按 Rows.Keys 顺序填充 RegionIds。</summary>
    public static WsensoryMatrix LoadWsensory(string jsonPath)
    {
        var json = File.ReadAllText(jsonPath);
        var data = JsonSerializer.Deserialize<WsensoryMatrix>(json, Options)
                   ?? throw new InvalidOperationException($"Failed to deserialize {jsonPath}");
        return data with { RegionIds = data.Rows.Keys.ToArray() };
    }

    /// <summary>从 situation_primitives.json 加载 27 个情境原型。</summary>
    public static SituationPrimitives LoadSituationPrimitives(string jsonPath)
    {
        var json = File.ReadAllText(jsonPath);
        return JsonSerializer.Deserialize<SituationPrimitives>(json, Options)
               ?? throw new InvalidOperationException($"Failed to deserialize {jsonPath}");
    }

    /// <summary>从 signal_types.json 加载信号类型词表（4 类目 × 18 子类）。</summary>
    public static SignalTypesCatalog LoadSignalTypes(string jsonPath)
    {
        var json = File.ReadAllText(jsonPath);
        return JsonSerializer.Deserialize<SignalTypesCatalog>(json, Options)
               ?? throw new InvalidOperationException($"Failed to deserialize {jsonPath}");
    }
}
