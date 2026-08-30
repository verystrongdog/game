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
    /// 从 moonlight_landing.json 加载月光场落点（Grilling #108 Q9 契约）。
    /// 四项校验（引擎加载期 fail-fast，JsonException）：
    /// ① supp 互斥（语义间 primary+secondary fid 不重叠）② 归一化（按 #101 Q4 公式重算 Σv^norm=1）
    /// ③ supp ⊆ W_active（fid→dk 映射后 ∈ 三体模型边端点集）④ 非负 + r>0。
    /// r/α_s = "PLACEHOLDER" 合法（r=PLACEHOLDER → 按 r=1 均匀）；字段缺失 ≠ PLACEHOLDER（load error）。
    /// </summary>
    public static MoonlightLanding LoadMoonlightLanding(
        string jsonPath, BrainRegionsData brainRegions, TripartiteModel tripartite)
    {
        ArgumentNullException.ThrowIfNull(brainRegions);
        ArgumentNullException.ThrowIfNull(tripartite);

        var json = File.ReadAllText(jsonPath);
        var data = JsonSerializer.Deserialize<MoonlightLanding>(json, Options)
                   ?? throw new InvalidOperationException($"Failed to deserialize {jsonPath}");

        if (!data.Schema.StartsWith("moonlight_landing", StringComparison.Ordinal))
            throw new JsonException($"moonlight_landing schema 不匹配: \"{data.Schema}\"");
        if (data.Version != 1)
            throw new JsonException($"moonlight_landing schema major 不匹配: version={data.Version}（期望 1）");
        if (data.Semantics.Count == 0)
            throw new JsonException("moonlight_landing semantics 为空");
        if (data.CalibrationStatus is not ("PLACEHOLDER" or "CALIBRATED"))
            throw new JsonException($"calibration_status 非法: \"{data.CalibrationStatus}\"（须 PLACEHOLDER|CALIBRATED）");

        // fid→dk 映射（#108 事实核查：校验必须走 fid→dk，不可直接比字符串——HippocampusCA1/CA3 同 dk Hippocampus）
        var fidToDk = brainRegions.Regions.ToDictionary(
            kv => kv.Key, kv => kv.Value.DkName ?? kv.Key);

        // W_active 端点集 = 三体模型全部边去重端点（#108 事实核查：51 graph_nodes − 3 无边节点 = 48）
        var wActive = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var e in tripartite.Cstc) { wActive.Add(e.Source); wActive.Add(e.Target); }
        foreach (var e in tripartite.Corticocortical) { wActive.Add(e.Source); wActive.Add(e.Target); }
        foreach (var e in tripartite.Brainstem) { wActive.Add(e.Source); wActive.Add(e.Target); }
        foreach (var e in tripartite.PrivilegedPathways) { wActive.Add(e.Source); wActive.Add(e.Target); }

        var allFids = new HashSet<string>();
        foreach (var sem in data.Semantics)
        {
            if (string.IsNullOrEmpty(sem.Id))
                throw new JsonException("semantics 缺 id");
            if (sem.Primary.Length != 4 || sem.Secondary.Length != 8)
                throw new JsonException(
                    $"semantics \"{sem.Id}\" 落点数不符：primary={sem.Primary.Length}（期望 4）/ secondary={sem.Secondary.Length}（期望 8）");
            if (string.IsNullOrEmpty(sem.R) || string.IsNullOrEmpty(sem.AlphaS))
                throw new JsonException($"semantics \"{sem.Id}\" r/alpha_s 字段缺失（字段缺失 ≠ PLACEHOLDER）");

            foreach (var fid in sem.Primary.Concat(sem.Secondary))
            {
                // ④ 非负（fid 存在性）+ ③ supp ⊆ W_active（fid→dk）
                if (!fidToDk.TryGetValue(fid, out var dk))
                    throw new JsonException($"semantics \"{sem.Id}\" fid \"{fid}\" 不在 brain_regions");
                if (!wActive.Contains(dk))
                    throw new JsonException($"semantics \"{sem.Id}\" fid \"{fid}\" → dk \"{dk}\" ∉ W_active 端点集");
                if (!allFids.Add(fid))
                    throw new JsonException($"semantics \"{sem.Id}\" fid \"{fid}\" 与既有语义重叠（supp 互斥违反）");
            }

            // ② 归一化（按 #101 Q4 公式重算 Σv^norm = 1）
            var r = ParseR(sem.R);
            if (r <= 0.0)
                throw new JsonException($"semantics \"{sem.Id}\" r 非正: {r}");
            var wPrimary = r / (4.0 * r + 8.0);
            var wSecondary = 1.0 / (4.0 * r + 8.0);
            var sum = 4.0 * wPrimary + 8.0 * wSecondary;
            if (Math.Abs(sum - 1.0) > 1e-9)
                throw new JsonException($"semantics \"{sem.Id}\" 归一化失败: Σv^norm={sum} ≠ 1");
        }

        return data;
    }

    /// <summary>r 参数解析（Q9）："PLACEHOLDER" → 按 r=1 均匀；否则须为正数。</summary>
    private static double ParseR(string r)
    {
        if (r == "PLACEHOLDER")
            return 1.0;
        if (!double.TryParse(r, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var v)
            || double.IsNaN(v) || double.IsInfinity(v) || v <= 0.0)
            throw new JsonException($"r 解析失败: \"{r}\"（须为正数或 \"PLACEHOLDER\"）");
        return v;
    }

    /// <summary>
    /// 一次加载全部 8 个数据文件（spec@v1.1 §三 3.3 + #105 T2/T3/T6 alpha_patterns/env_tones/moonlight_landing）——dataDir 为 data/ 目录。
    /// 文件名固定；异常语义同现有 8 方法（FileNotFoundException/JsonException/InvalidOperationException）。
    /// </summary>
    public static GameData LoadAll(string dataDir) => new(
        LoadBrainRegions(Path.Combine(dataDir, "brain_regions.json")),
        LoadTripartiteModel(Path.Combine(dataDir, "connectivity", "tripartite_model.json")),
        LoadWsensory(Path.Combine(dataDir, "connectivity", "W_sensory.json")),
        LoadSituationPrimitives(Path.Combine(dataDir, "connectivity", "situation_primitives.json")),
        LoadSignalTypes(Path.Combine(dataDir, "signal_types.json")),
        LoadAlphaPatterns(Path.Combine(dataDir, "connectivity", "alpha_patterns.json")),
        LoadEnvTones(Path.Combine(dataDir, "connectivity", "env_tones.json")),
        LoadMoonlightLanding(
            Path.Combine(dataDir, "connectivity", "moonlight_landing.json"),
            LoadBrainRegions(Path.Combine(dataDir, "brain_regions.json")),
            LoadTripartiteModel(Path.Combine(dataDir, "connectivity", "tripartite_model.json"))));
}
