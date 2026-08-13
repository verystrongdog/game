using System.IO;
using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// tone → 皮层 b_j 注入向量（csharp-engine plan §十一 step 5）——spec@v1.1（.scratch/csharp-tone/design/spec.md）。
/// 职责：b_j = Σ_t tone_t × w_t(j)，w 从 brainstem 边的 role 字段取（active→1.0 / modulating→0.5——
/// plan 修复 #8b，不是 projection 字段），per-target 唯一（同 system 同 target 多条边只取一次——
/// 任务issue Q1 裁决，Raphe DR+MnR 不叠加），求和后逐分量 clamp [0,2]（运行时状态模型 §7.2）。
/// 纯函数：无 static 可变状态、无 RNG。
/// 来源：csharp-engine plan §4.3；运行时状态模型 §5.6-5.7、§7.2。
/// </summary>
public static class CorticalBias
{
    /// <summary>role 权重两档：active 1.0 / modulating 0.5——运行时状态模型 §5.6（spec@v1.1 §四 4.2）。</summary>
    private const float WeightActive = 1.0f;
    private const float WeightModulating = 0.5f;

    /// <summary>b_j 值域 [0,2] clip——运行时状态模型 §7.2（spec@v1.1 §四 4.2）。</summary>
    private const float BiasMin = 0f;
    private const float BiasMax = 2f;

    /// <summary>
    /// 计算 tone → 皮层 b_j 注入向量（69 维）。
    /// 解析路径（spec §五 C2/C3/C6）：brainstem 边 target 按 graph_nodes dk 键直查 → functional_ids
    /// fan-out 到行序下标；Role ∈ {Active, Modulating}，Silent → InvalidDataException；
    /// 同 system 同 target 重复边只贡献一次 role 权重（取首边，实测同 target 两边 role 相同）。
    /// 输入：tone 当前 4 tone（值域 [0,1]，不校验）；data 全量游戏数据（消费 Wsensory.RegionIds /
    ///   Tripartite.GraphNodes / Tripartite.Brainstem）。
    /// 输出：新 float[69]，行序 = Wsensory.RegionIds（canonical 行序契约 C1，csharp-wmatrix spec Step 1），
    ///   供 WcDynamics.Step 直接消费。
    /// 异常：tone/data 为 null → ArgumentNullException；
    ///   边 target 不在 GraphNodes → InvalidDataException（含边描述）；
    ///   边 Role == Silent → InvalidDataException（brainstem 数据契约只允许 Active|Modulating，实测 114/114）；
    ///   边 functional_ids 含不在 RegionIds 的 fid → InvalidDataException（同一数据完整性类，实测不触发）。
    /// 来源：csharp-engine plan §4.3（修复 #8b）；运行时状态模型 §5.6-5.7、§7.2；spec@v1.1 §三。
    /// </summary>
    public static float[] Compute(ToneState tone, GameData data)
    {
        ArgumentNullException.ThrowIfNull(tone);
        ArgumentNullException.ThrowIfNull(data);

        // 契约 C1：输出行序 = Wsensory.RegionIds（canonical 69，首键 AccumbensCore）
        string[] regionIds = data.Wsensory.RegionIds;
        var rowOf = new Dictionary<string, int>(regionIds.Length);
        for (int i = 0; i < regionIds.Length; i++)
        {
            rowOf[regionIds[i]] = i;
        }

        var nodes = data.Tripartite.GraphNodes;
        // 契约 C6：per-target 唯一（任务issue Q1）——同 system 同 target 多条边只取一次
        var seen = new HashSet<(BrainstemSystem System, string Target)>();
        var bias = new float[regionIds.Length];

        foreach (var edge in data.Tripartite.Brainstem)
        {
            if (edge.Role == EdgeRole.Silent)
            {
                // 契约 C3：brainstem 数据契约只允许 Active|Modulating（实测 silent 0 条）
                throw new InvalidDataException($"brainstem 边 role 不允许 Silent：{Describe(edge)}");
            }

            if (!seen.Add((edge.System, edge.Target)))
            {
                continue; // C6：重复边（Raphe DR+MnR）只贡献一次
            }

            if (!nodes.TryGetValue(edge.Target, out var node))
            {
                // 契约 C2：target 必须命中 graph_nodes dk 键（实测 114/114 命中）
                throw new InvalidDataException($"brainstem 边 target 未命中 graph_nodes：{Describe(edge)}");
            }

            float w = edge.Role == EdgeRole.Active ? WeightActive : WeightModulating;
            float t = ToneOf(edge.System, tone);
            foreach (var fid in node.FunctionalIds)
            {
                if (!rowOf.TryGetValue(fid, out int row))
                {
                    throw new InvalidDataException(
                        $"brainstem 边 fan-out fid 不在 RegionIds：{fid}（{Describe(edge)}）");
                }

                bias[row] += t * w;
            }
        }

        // 值域 [0,2] clamp（§7.2）——tone=1 时 mOFC 3 fid pre-clamp 2.5 由本 clamp 兜底
        for (int i = 0; i < bias.Length; i++)
        {
            bias[i] = Math.Clamp(bias[i], BiasMin, BiasMax);
        }

        return bias;
    }

    /// <summary>系统 → tone 分量映射（spec@v1.1 §四 4.3）。</summary>
    private static float ToneOf(BrainstemSystem system, ToneState tone) => system switch
    {
        BrainstemSystem.LcNe => tone.Ne,
        BrainstemSystem.Raphe5Ht => tone.Ht5,
        BrainstemSystem.SncDa => tone.DaSnc,
        BrainstemSystem.VtaDa => tone.DaVta,
        _ => throw new ArgumentOutOfRangeException(nameof(system), system, "未知 brainstem 系统"),
    };

    /// <summary>边描述（异常消息用）。</summary>
    private static string Describe(BrainstemProjection edge) =>
        $"{edge.System} {edge.Source}→{edge.Target}（role={edge.Role}，projection={edge.Projection}）";
}
