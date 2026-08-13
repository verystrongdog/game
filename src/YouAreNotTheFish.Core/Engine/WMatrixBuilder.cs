using System.IO;
using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// W 矩阵构建器（csharp-engine plan §十一 step 3）——spec@v1.1（.scratch/csharp-wmatrix/design/spec.md）。
/// 职责：边筛选（排除清单）→ 权重（w = edr × m_mean × focus）→ fan-out 广播
/// → 行归一化（ε=0.01）→ τ 查表（含 mirror 继承）。
/// 纯函数：无 static 可变状态、无 RNG、同输入同输出。
/// 来源：csharp-engine plan §4.1；皮层动力学-通用层 §5.1-5.5、§4.4；运行时状态模型 §4.1-4.3。
/// </summary>
public static class WMatrixBuilder
{
    /// <summary>
    /// 构建 69×69 皮层-皮层连接权重矩阵 W 与时间常数数组 Tau。
    /// 输入：GameData（消费 Tripartite / BrainRegions / Wsensory 三部分）。
    /// 输出：WMatrix（W[69,69] / Tau[69] / RowFids[69]），RowFids 顺序 == Wsensory.RegionIds。
    /// 异常：data 为 null → ArgumentNullException；
    ///       边端点无法经 GraphNodes 或 functional_id 解析 → InvalidDataException。
    /// 来源：csharp-engine plan §4.1；皮层动力学-通用层 §5.1-5.5、§4.4；运行时状态模型 §4.1-4.2。
    /// </summary>
    public static WMatrix Build(GameData data)
    {
        ArgumentNullException.ThrowIfNull(data);

        // Step 1 — 行序契约：canonical = Wsensory.RegionIds（spec §二 Step 1、§五 C1）
        string[] rowFids = data.Wsensory.RegionIds;
        int n = rowFids.Length;
        var fidToRow = new Dictionary<string, int>(n);
        for (int i = 0; i < n; i++)
        {
            fidToRow[rowFids[i]] = i;
        }

        // Step 2 — fid→dk 映射（spec §二 Step 2；69 fid 与 RegionIds 双射，C2 由数据层测试锁定）
        var fidToDk = new Dictionary<string, string>();
        foreach (var (dkName, node) in data.Tripartite.GraphNodes)
        {
            foreach (var fid in node.FunctionalIds)
            {
                fidToDk[fid] = dkName;
            }
        }

        // Step 3 — 排除集（spec §二 Step 3）：
        // B1 偏差声明：按运行时状态模型 §4.2 排除清单执行（非皮层动力学 §5.1「仅 cortical」措辞）。
        // B2 偏差声明：Cerebellum-Cortex category=subcortical 且不在 CSTC 清单 → 不排除。
        // 实测：16 dk / 21 fids（CSTC 6 + brainstem 11；SubthalamicNucleus 双归属只计一次）。
        var excludedDk = new HashSet<string>(CstcDk);
        foreach (var (_, node) in data.Tripartite.GraphNodes)
        {
            if (node.Category == BrainRegionCategory.Brainstem)
            {
                excludedDk.Add(node.DkName);
            }
        }

        // Step 4 — 边遍历与权重（spec §二 Step 4）：
        // B4 偏差声明：demo 无 LinkState → m_mean ≡ CalibrationConfig.Default.MDefault；
        // focus_multiplier ≡ 1.0（§5.2 基础档），聚焦接口以注释预留。
        float mMean = CalibrationConfig.Default.MDefault;
        float[,] w = new float[n, n];
        foreach (var edge in data.Tripartite.Corticocortical)
        {
            AddEdge(w, edge.Source, edge.Target, (float)edge.EdrProbability,
                mMean, excludedDk, fidToDk, fidToRow, data.Tripartite.GraphNodes);
        }

        foreach (var path in data.Tripartite.PrivilegedPathways)
        {
            AddEdge(w, path.Source, path.Target, (float)path.EdrProbability,
                mMean, excludedDk, fidToDk, fidToRow, data.Tripartite.GraphNodes);
        }

        // Step 5 — 行归一化（spec §二 Step 5；全部 69 行含排除行，无异常分支）：
        // 排除行 sum=0 → 0/(0+ε)=0 自然成立。
        for (int j = 0; j < n; j++)
        {
            float sum = 0f;
            for (int k = 0; k < n; k++)
            {
                sum += w[j, k];
            }

            float denom = sum + Epsilon;
            for (int k = 0; k < n; k++)
            {
                w[j, k] /= denom;
            }
        }

        // Step 6 — τ 数组（spec §二 Step 6；按 canonical 行序逐 fid，含 mirror 一层继承）
        float[] tau = new float[n];
        for (int j = 0; j < n; j++)
        {
            tau[j] = ResolveTau(rowFids[j], data.BrainRegions.Regions);
        }

        return new WMatrix(w, tau, rowFids);
    }

    /// <summary>
    /// 单条边处理：排除检查（先于解析）→ 自连接跳过 → 端点解析 → 权重 → fan-out 广播。
    /// 行=接收者=target（spec 偏差声明 B3：以运行时状态模型 §4.1 h_j = Σ_k W_jk·a_k 方向为准，
    /// 非皮层动力学 §5.1 的 [源][目标] 序——两者互为转置，归一化后行和不同会分叉）。
    /// </summary>
    private static void AddEdge(
        float[,] w,
        string source,
        string target,
        float edr,
        float mMean,
        HashSet<string> excludedDk,
        Dictionary<string, string> fidToDk,
        Dictionary<string, int> fidToRow,
        Dictionary<string, GraphNode> graphNodes)
    {
        // 1. 排除检查先于解析（spec Step 4 第 1 条：Caudate 2 fids ∈ CSTC 排除集，歧义解析永不触达）
        if (IsExcludedEndpoint(source, excludedDk, fidToDk, graphNodes)
            || IsExcludedEndpoint(target, excludedDk, fidToDk, graphNodes))
        {
            return;
        }

        // 2. 自连接跳过（w(A,A)=0，皮层动力学-通用层 §5.2；实测 0 条自环，防御性规则）
        if (source == target)
        {
            return;
        }

        // 3. 端点解析：dk_name 优先（graph_nodes 键），未命中按 functional_id 兜底（单 fid）
        //    （spec Step 4 第 3 条 / 任务issue D4）；两者失败 = 数据错误（AC-10）
        if (!TryResolve(source, graphNodes, fidToDk, out string[] sourceFids))
        {
            throw new InvalidDataException(
                $"WMatrixBuilder: 无法解析边端点 source='{source}'（既非 graph_nodes 键也非 functional_id）。");
        }

        if (!TryResolve(target, graphNodes, fidToDk, out string[] targetFids))
        {
            throw new InvalidDataException(
                $"WMatrixBuilder: 无法解析边端点 target='{target}'（既非 graph_nodes 键也非 functional_id）。");
        }

        // 4. 权重 w = edr × m_mean × focus_multiplier（皮层动力学-通用层 §5.2；B4）
        float weight = edr * mMean * FocusMultiplier;

        // 5. fan-out 广播：W[行=接收者=target][列=发送者=source] += w（spec Step 4 第 5 条、B3）
        //    同 dk 对内多个 fid 共享同一权重模式（plan §4.1 第 1 条）
        foreach (var s in sourceFids)
        {
            foreach (var t in targetFids)
            {
                // 6. 累加为防御语义：实测 CC∩PP 幸存 dk 对重叠 = 0，当前数据下与赋值等价（AC-6）
                w[fidToRow[t], fidToRow[s]] += weight;
            }
        }
    }

    /// <summary>端点是否属于排除 dk：graph_nodes 键直查，未命中按 fid→dk 兜底；均未命中 → 不排除（解析阶段抛异常）。</summary>
    private static bool IsExcludedEndpoint(
        string endpoint,
        HashSet<string> excludedDk,
        Dictionary<string, string> fidToDk,
        Dictionary<string, GraphNode> graphNodes)
    {
        if (graphNodes.TryGetValue(endpoint, out var node))
        {
            return excludedDk.Contains(node.DkName);
        }

        return fidToDk.TryGetValue(endpoint, out var dk) && excludedDk.Contains(dk);
    }

    /// <summary>端点解析（spec Step 4 第 3 条）：graph_nodes 键优先（dk 名 → 全部 fids），fid 兜底（单 fid）。</summary>
    private static bool TryResolve(
        string endpoint,
        Dictionary<string, GraphNode> graphNodes,
        Dictionary<string, string> fidToDk,
        out string[] fids)
    {
        if (graphNodes.TryGetValue(endpoint, out var node))
        {
            fids = node.FunctionalIds;
            return true;
        }

        if (fidToDk.ContainsKey(endpoint))
        {
            fids = [endpoint];
            return true;
        }

        fids = [];
        return false;
    }

    /// <summary>
    /// 单 fid 的 τ 解析（spec §二 Step 6）：
    /// Timescale 为 null → MirrorOf 非空时继承镜像目标（一层继承）；仍为 null → medium（τ_default）。
    /// 映射：Fast 0.01 / Medium 0.05 / Slow 0.15（皮层动力学-通用层 §4.4）。
    /// </summary>
    private static float ResolveTau(string fid, Dictionary<string, BrainRegion> regions)
    {
        BrainRegion region = regions[fid]; // C2 双射由数据层锁定；缺失 = 数据错误（KeyNotFoundException）
        Timescale? ts = region.FunctionProfile.Timescale;

        if (ts == null
            && region.FunctionProfile.MirrorOf is { } mirrorOf
            && regions.TryGetValue(mirrorOf, out var mirrorRegion))
        {
            ts = mirrorRegion.FunctionProfile.Timescale; // 一层继承，不递归（spec Step 6 第 2 条）
        }

        return ts switch
        {
            Timescale.Fast => TauFast,
            Timescale.Slow => TauSlow,
            _ => TauMedium, // Medium 与缺失默认同值 0.05f（τ_default）
        };
    }

    /// <summary>CSTC 排除 dk 集——运行时状态模型 §4.2 六名逐字（spec §四；SubthalamicNucleus 与 brainstem 双归属只计一次）。</summary>
    private static readonly string[] CstcDk =
    [
        "Pallidum",
        "Thalamus-Proper",
        "Putamen",
        "Caudate",
        "Accumbens-area",
        "SubthalamicNucleus",
    ];

    /// <summary>归一化兜底 ε——皮层动力学-通用层 §5.4（spec §四）。</summary>
    private const float Epsilon = 0.01f;

    /// <summary>focus 乘子（demo 基础档）——皮层动力学-通用层 §5.2 / 偏差声明 B4。聚焦接口预留：未来 Build 增 focus 参数。</summary>
    private const float FocusMultiplier = 1.0f;

    /// <summary>τ_fast——皮层动力学-通用层 §4.4（spec §四）。</summary>
    private const float TauFast = 0.01f;

    /// <summary>τ_medium——皮层动力学-通用层 §4.4（spec §四）。</summary>
    private const float TauMedium = 0.05f;

    /// <summary>τ_slow——皮层动力学-通用层 §4.4（spec §四）。</summary>
    private const float TauSlow = 0.15f;
}
