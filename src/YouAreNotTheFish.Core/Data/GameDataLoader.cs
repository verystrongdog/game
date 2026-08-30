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

    /// <summary>
    /// 从 alpha_patterns.json 加载 α pattern 表（Grilling #108 Q1 契约）。
    /// 加载期 fail-fast（抛 JsonException，接 #106 分层 → Console exit 1）：
    /// 消费行缺失（A1/A2/A4/A5/B1/B2/B4/C1/D1/D2）/ schema major 不匹配 / pattern 长度≠8 /
    /// pattern 值 ∉ {0,1} / m_alpha 类型非法或越界（MAlphaValueConverter）。数据表不是可选配置——
    /// 不静默补零/截断/自动修复。
    /// </summary>
    public static AlphaPatterns LoadAlphaPatterns(string jsonPath)
    {
        var json = File.ReadAllText(jsonPath);
        var data = JsonSerializer.Deserialize<AlphaPatterns>(json, Options)
                   ?? throw new InvalidOperationException($"Failed to deserialize {jsonPath}");

        if (!data.Schema.StartsWith("alpha_patterns", StringComparison.Ordinal))
            throw new JsonException($"alpha_patterns schema 不匹配: \"{data.Schema}\"");
        if (data.Version != 1)
            throw new JsonException($"alpha_patterns schema major 不匹配: version={data.Version}（期望 1）");

        // 引擎映射消费的 10 行（Q1：行 id ↔ 派生分支绑定留代码——Emit 调用点持有）
        string[] consumedRows = ["A1", "A2", "A4", "A5", "B1", "B2", "B4", "C1", "D1", "D2"];
        foreach (var row in consumedRows)
        {
            if (!data.Events.TryGetValue(row, out var entry))
                throw new JsonException($"alpha_patterns 消费行缺失: \"{row}\"");
            if (entry.Pattern.Length != 8)
                throw new JsonException($"alpha_patterns {row} pattern 长度≠8: {entry.Pattern.Length}");
            foreach (var v in entry.Pattern)
                if (v is not (0 or 1))
                    throw new JsonException($"alpha_patterns {row} pattern 值 ∉ {{0,1}}: {v}");
        }
        // 14 行完整保留（数据层完整性；A3/A6/A7 保留不消费）
        if (data.Events.Count < 14)
            throw new JsonException($"alpha_patterns 行数不足 14: {data.Events.Count}");

        return data;
    }

    /// <summary>从 signal_types.json 加载信号类型词表（4 类目 × 18 子类）。</summary>
    public static SignalTypesCatalog LoadSignalTypes(string jsonPath)
    {
        var json = File.ReadAllText(jsonPath);
        return JsonSerializer.Deserialize<SignalTypesCatalog>(json, Options)
               ?? throw new InvalidOperationException($"Failed to deserialize {jsonPath}");
    }

    /// <summary>
    /// 从 env_tones.json 加载环境基调表（Grilling #108 Q3/Q5 契约）。
    /// fail-fast（JsonException）：schema major 不匹配 / alpha_env 长度≠8 / 值 ∉ [0,1] /
    /// 无 environments 键 / 环境键缺 display_name 或 situation.primary。
    /// 运行时缺失环境键 → 抛（禁止回退零向量，Q3）。
    /// </summary>
    public static EnvTones LoadEnvTones(string jsonPath)
    {
        var json = File.ReadAllText(jsonPath);
        var data = JsonSerializer.Deserialize<EnvTones>(json, Options)
                   ?? throw new InvalidOperationException($"Failed to deserialize {jsonPath}");

        if (!data.Schema.StartsWith("env_tones", StringComparison.Ordinal))
            throw new JsonException($"env_tones schema 不匹配: \"{data.Schema}\"");
        if (data.Version != 1)
            throw new JsonException($"env_tones schema major 不匹配: version={data.Version}（期望 1）");
        if (data.Environments.Count == 0)
            throw new JsonException("env_tones environments 为空");

        foreach (var (id, env) in data.Environments)
        {
            if (string.IsNullOrEmpty(env.DisplayName))
                throw new JsonException($"env_tones 环境 \"{id}\" 缺 display_name");
            if (env.AlphaEnv.Length != 8)
                throw new JsonException($"env_tones {id} alpha_env 长度≠8: {env.AlphaEnv.Length}");
            foreach (var v in env.AlphaEnv)
                if (double.IsNaN(v) || double.IsInfinity(v) || v < 0.0 || v > 1.0)
                    throw new JsonException($"env_tones {id} alpha_env 值 ∉ [0,1]: {v}");
            if (string.IsNullOrEmpty(env.Situation.Primary))
                throw new JsonException($"env_tones {id} 缺 situation.primary");
        }
        return data;
    }

    /// <summary>
    /// 一次加载全部 7 个数据文件（spec@v1.1 §三 3.3 + #105 T2/T3 alpha_patterns/env_tones）——dataDir 为 data/ 目录。
    /// 文件名固定；异常语义同现有 7 方法（FileNotFoundException/JsonException/InvalidOperationException）。
    /// </summary>
    public static GameData LoadAll(string dataDir) => new(
        LoadBrainRegions(Path.Combine(dataDir, "brain_regions.json")),
        LoadTripartiteModel(Path.Combine(dataDir, "connectivity", "tripartite_model.json")),
        LoadWsensory(Path.Combine(dataDir, "connectivity", "W_sensory.json")),
        LoadSituationPrimitives(Path.Combine(dataDir, "connectivity", "situation_primitives.json")),
        LoadSignalTypes(Path.Combine(dataDir, "signal_types.json")),
        LoadAlphaPatterns(Path.Combine(dataDir, "connectivity", "alpha_patterns.json")),
        LoadEnvTones(Path.Combine(dataDir, "connectivity", "env_tones.json")));
}
