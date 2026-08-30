using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// WMatrixBuilder spec@v1.1（.scratch/csharp-wmatrix/design/spec.md）§六 AC-1~AC-12。
/// 数据依赖断言（AC-3/4/5/6/7/8/11/12）兼作数据漂移哨兵——数据 JSON 变更时同步复核期望值。
/// </summary>
public class WMatrixBuilderTests
{
    // ---- 数据加载（复用 GameDataLoadAllTests 的 FindDataDir 候选路径模式）----

    private static readonly string[] DataDirCandidates =
    [
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "data"),
        Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "data")),
        "/home/dog/game/data",
    ];

    private static string FindDataDir()
    {
        foreach (var dir in DataDirCandidates)
        {
            if (File.Exists(Path.Combine(dir, "brain_regions.json"))) return dir;
        }

        throw new DirectoryNotFoundException(
            "Cannot find data/ directory. Tried:\n" + string.Join("\n", DataDirCandidates));
    }

    private static GameData LoadData() => GameDataLoader.LoadAll(FindDataDir());

    private static WMatrix Build() => WMatrixBuilder.Build(LoadData());

    // ---- 测试侧助手：镜像 spec §二 Step 4.3 端点解析规则（sign-off 结转 #1）----

    /// <summary>CSTC 排除 dk——运行时状态模型 §4.2 六名逐字（spec §二 Step 3）。</summary>
    private static readonly string[] CstcDk =
    [
        "Pallidum",
        "Thalamus-Proper",
        "Putamen",
        "Caudate",
        "Accumbens-area",
        "SubthalamicNucleus",
    ];

    private static Dictionary<string, string> FidToDk(TripartiteModel tri)
    {
        var map = new Dictionary<string, string>();
        foreach (var (dkName, node) in tri.GraphNodes)
        {
            foreach (var fid in node.FunctionalIds)
            {
                map[fid] = dkName;
            }
        }

        return map;
    }

    /// <summary>排除 dk 集 = CSTC 6 ∪ category==Brainstem（镜像 builder Step 3）。</summary>
    private static HashSet<string> ExcludedDks(TripartiteModel tri)
    {
        var set = new HashSet<string>(CstcDk);
        foreach (var (_, node) in tri.GraphNodes)
        {
            if (node.Category == BrainRegionCategory.Brainstem)
            {
                set.Add(node.DkName);
            }
        }

        return set;
    }

    /// <summary>排除 fid 列表（按 node.DkName 归属）。</summary>
    private static string[] ExcludedFids(TripartiteModel tri)
    {
        var excluded = ExcludedDks(tri);
        return tri.GraphNodes.Values
            .Where(n => excluded.Contains(n.DkName))
            .SelectMany(n => n.FunctionalIds)
            .ToArray();
    }

    /// <summary>
    /// 端点解析（结转 #1）：graph_nodes 键优先（dk 名 → 全部 fids）→ fid 兜底（单 fid）。
    /// 大小写敏感——'Pericalcarine' 是 fid 名，dk 键为小写 'pericalcarine'。
    /// </summary>
    private static string[] ResolveFids(string endpoint, TripartiteModel tri)
    {
        if (tri.GraphNodes.TryGetValue(endpoint, out var node))
        {
            return node.FunctionalIds;
        }

        var fidToDk = FidToDk(tri);
        if (fidToDk.ContainsKey(endpoint))
        {
            return [endpoint];
        }

        throw new InvalidDataException($"测试解析失败: {endpoint}");
    }

    /// <summary>端点 → dk 名（dk 键直返自身；fid 名经 fid→dk 兜底）。</summary>
    private static string DkOf(string endpoint, TripartiteModel tri)
    {
        if (tri.GraphNodes.ContainsKey(endpoint))
        {
            return endpoint;
        }

        var fidToDk = FidToDk(tri);
        if (fidToDk.TryGetValue(endpoint, out var dk))
        {
            return dk;
        }

        throw new InvalidDataException($"测试解析失败: {endpoint}");
    }

    private static int RowOf(WMatrix m, string fid)
    {
        int i = Array.IndexOf(m.RowFids, fid);
        if (i < 0)
        {
            throw new InvalidDataException($"RowFids 中无 {fid}");
        }

        return i;
    }

    /// <summary>绝对容差 1e-5 断言（spec AC-7：float32 实测偏差 &lt;2e-7，余量 ~100×）。</summary>
    private static void AssertApprox(float expected, float actual, string what)
    {
        Assert.True(Math.Abs(expected - actual) <= 1e-5f,
            $"{what}: 期望 {expected}，实际 {actual}，偏差 {Math.Abs(expected - actual)}");
    }

    private static int NonzeroCount(float[,] w)
    {
        int count = 0;
        foreach (var v in w)
        {
            if (v != 0f)
            {
                count++;
            }
        }

        return count;
    }

    // ---- AC-1：形状 69×69 / 69 / 69 ----

    [Fact]
    public void Build_Returns69Shapes()
    {
        WMatrix m = Build();

        Assert.Equal(69, m.W.GetLength(0));
        Assert.Equal(69, m.W.GetLength(1));
        Assert.Equal(69, m.Tau.Length);
        Assert.Equal(69, m.RowFids.Length);
    }

    // ---- AC-2：RowFids == RegionIds（C1，结转 #5 落地）；与 graph fids 双射 ----

    [Fact]
    public void RowFids_EqualsRegionIdsAndBijectiveWithGraphFids()
    {
        GameData data = LoadData();
        WMatrix m = WMatrixBuilder.Build(data);

        Assert.Equal(data.Wsensory.RegionIds, m.RowFids);

        var graphFids = data.Tripartite.GraphNodes.Values
            .SelectMany(n => n.FunctionalIds)
            .ToHashSet();
        Assert.Equal(69, graphFids.Count);
        Assert.True(graphFids.SetEquals(m.RowFids), "GraphNodes fids 与 RowFids 应双向双射（C2）");
    }

    // ---- AC-3：21 排除 fid 行列全 0（C3）----

    [Fact]
    public void ExcludedFids_HaveZeroRowsAndColumns()
    {
        GameData data = LoadData();
        WMatrix m = WMatrixBuilder.Build(data);

        string[] excluded = ExcludedFids(data.Tripartite);
        Assert.Equal(21, excluded.Length);

        foreach (var fid in excluded)
        {
            int r = RowOf(m, fid);
            for (int k = 0; k < 69; k++)
            {
                Assert.Equal(0f, m.W[r, k]);
                Assert.Equal(0f, m.W[k, r]);
            }
        }
    }

    // ---- AC-4：非零元计数 == 1389（C8）----

    [Fact]
    public void NonzeroCount_Is1389()
    {
        WMatrix m = Build();

        Assert.Equal(1389, NonzeroCount(m.W));
    }

    // ---- AC-5：48 行 0<sum<1；21 行 sum==0（C7）----

    [Fact]
    public void RowSums_48ActiveInOpen01_21Zero()
    {
        WMatrix m = Build();

        int active = 0;
        int zero = 0;
        for (int j = 0; j < 69; j++)
        {
            float sum = 0f;
            for (int k = 0; k < 69; k++)
            {
                sum += m.W[j, k];
            }

            if (sum == 0f)
            {
                zero++;
            }
            else
            {
                Assert.True(sum > 0f && sum < 1f, $"行 {j} 行和应 ∈ (0,1)，实际 {sum}");
                active++;
            }
        }

        Assert.Equal(48, active);
        Assert.Equal(21, zero);
    }

    // ---- AC-6：735 幸存 dk 对块内等值；CC∩PP 幸存 dk 对重叠 0 ----

    [Fact]
    public void FanOut_All735SurvivingPairsHaveEqualBlockCells_NoCcPpOverlap()
    {
        GameData data = LoadData();
        WMatrix m = WMatrixBuilder.Build(data);
        var tri = data.Tripartite;
        var excluded = ExcludedDks(tri);

        var ccPairs = new HashSet<(string, string)>();
        var ppPairs = new HashSet<(string, string)>();
        var seenPairs = new HashSet<(string, string)>();

        foreach (var e in tri.Corticocortical)
        {
            var (sDk, tDk) = (DkOf(e.Source, tri), DkOf(e.Target, tri));
            if (excluded.Contains(sDk) || excluded.Contains(tDk))
            {
                continue;
            }

            ccPairs.Add((sDk, tDk));
            seenPairs.Add((sDk, tDk));
            AssertBlockEqual(m, tri, sDk, tDk);
        }

        foreach (var p in tri.PrivilegedPathways)
        {
            var (sDk, tDk) = (DkOf(p.Source, tri), DkOf(p.Target, tri));
            if (excluded.Contains(sDk) || excluded.Contains(tDk))
            {
                continue;
            }

            ppPairs.Add((sDk, tDk));
            seenPairs.Add((sDk, tDk));
            AssertBlockEqual(m, tri, sDk, tDk);
        }

        Assert.Equal(735, seenPairs.Count);
        Assert.Empty(ccPairs.Intersect(ppPairs));
    }

    /// <summary>dk 对 (S,T) 的 fan-out 块内全部单元格等值（行=接收者=T，B3）。</summary>
    private static void AssertBlockEqual(WMatrix m, TripartiteModel tri, string sDk, string tDk)
    {
        string[] sFids = tri.GraphNodes[sDk].FunctionalIds;
        string[] tFids = tri.GraphNodes[tDk].FunctionalIds;
        float first = m.W[RowOf(m, tFids[0]), RowOf(m, sFids[0])];
        foreach (var s in sFids)
        {
            foreach (var t in tFids)
            {
                Assert.Equal(first, m.W[RowOf(m, t), RowOf(m, s)]);
            }
        }
    }

    // ---- AC-7：5 锚点值（绝对容差 1e-5；结转 #1：锚点标识符按 Step 4.3 解析规则展开）----

    [Fact]
    public void Anchors_MatchIndependentlyComputedValues()
    {
        GameData data = LoadData();
        WMatrix m = WMatrixBuilder.Build(data);
        var tri = data.Tripartite;

        // 唯一非互惠对 pericalcarine→Amygdala（方向契约哨兵，C6）：
        // 'Amygdala' 是 graph_nodes 键（dk，单 fid）；'Pericalcarine' 是 fid 名（dk 键为小写 'pericalcarine'）
        AssertApprox(0.02277450f, m.W[RowOf(m, "Amygdala"), RowOf(m, "Pericalcarine")],
            "W[Amygdala][Pericalcarine]");
        Assert.Equal(0f, m.W[RowOf(m, "Pericalcarine"), RowOf(m, "Amygdala")]);

        // cac→tt：3 fid 行 × 1 fid 列，块内等值
        string[] cacFids = ResolveFids("caudalanteriorcingulate", tri);
        string[] ttFids = ResolveFids("transversetemporal", tri);
        foreach (var t in cacFids)
        {
            foreach (var tt in ttFids)
            {
                AssertApprox(0.03620595f, m.W[RowOf(m, t), RowOf(m, tt)],
                    $"W[{t}][{tt}]");
            }
        }

        // tt→cac：锁定归一化后不对称
        foreach (var tt in ttFids)
        {
            foreach (var t in cacFids)
            {
                AssertApprox(0.02819380f, m.W[RowOf(m, tt), RowOf(m, t)],
                    $"W[{tt}][{t}]");
            }
        }

        // Hippocampus→entorhinal（PP 边锚点）：2 fid 行 × 1 fid 列
        string[] entFids = ResolveFids("entorhinal", tri);
        foreach (var h in ResolveFids("Hippocampus", tri))
        {
            foreach (var ent in entFids)
            {
                AssertApprox(0.07386513f, m.W[RowOf(m, h), RowOf(m, ent)],
                    $"W[{h}][{ent}]");
            }
        }
    }

    // ---- AC-8：τ 分布（继承后最终 Tau）27/30/12 + mirror 点名 ----

    [Fact]
    public void Tau_DistributionAndMirrorInheritance()
    {
        WMatrix m = Build();

        Assert.Equal(27, m.Tau.Count(t => t == 0.01f));
        Assert.Equal(30, m.Tau.Count(t => t == 0.05f));
        Assert.Equal(12, m.Tau.Count(t => t == 0.15f));

        Assert.Equal(0.15f, m.Tau[RowOf(m, "LocusCoeruleusRight")]);
        Assert.Equal(0.05f, m.Tau[RowOf(m, "SubstantiaNigraParsCompactaRight")]);
    }

    // ---- AC-9：确定性——双 Build 逐元相等 ----

    [Fact]
    public void Build_IsDeterministic()
    {
        GameData data = LoadData();
        WMatrix a = WMatrixBuilder.Build(data);
        WMatrix b = WMatrixBuilder.Build(data);

        for (int j = 0; j < 69; j++)
        {
            for (int k = 0; k < 69; k++)
            {
                Assert.Equal(a.W[j, k], b.W[j, k]);
            }

            Assert.Equal(a.Tau[j], b.Tau[j]);
        }

        Assert.Equal(a.RowFids, b.RowFids);
    }

    // ---- AC-10：端点不可解析 → InvalidDataException（C4）----

    [Fact]
    public void UnresolvableEndpoint_ThrowsInvalidDataException()
    {
        var tri = new TripartiteModel
        {
            GraphNodes = new Dictionary<string, GraphNode>
            {
                ["BogusSource"] = new GraphNode { DkName = "BogusSource", FunctionalIds = ["BogusSourceFid"] },
                ["BogusTarget"] = new GraphNode { DkName = "BogusTarget", FunctionalIds = ["BogusTargetFid"] },
            },
            Corticocortical =
            [
                new CorticocorticalEdge { Source = "BogusSource", Target = "Ghost", EdrProbability = 0.5 },
            ],
        };

        var data = new GameData(
            new BrainRegionsData(),
            tri,
            new WsensoryMatrix { RegionIds = ["BogusSourceFid", "BogusTargetFid"] },
            new SituationPrimitives(),
            new SignalTypesCatalog(),
            new AlphaPatterns(),
            new EnvTones());

        Assert.Throws<InvalidDataException>(() => WMatrixBuilder.Build(data));
    }

    // ---- AC-11：69 对角全 0；同 dk 非对角 fid 对共 50 格全 0（结转 #2：计数由 graph_nodes 推导）----

    [Fact]
    public void DiagonalAndSameDkOffDiagonal_AllZero()
    {
        GameData data = LoadData();
        WMatrix m = WMatrixBuilder.Build(data);

        for (int i = 0; i < 69; i++)
        {
            Assert.Equal(0f, m.W[i, i]);
        }

        // 同 dk 非对角 fid 对：逐对由 graph_nodes 全量推导（Σ n(n−1)），不硬编码枚举
        int count = 0;
        foreach (var (_, node) in data.Tripartite.GraphNodes)
        {
            string[] fids = node.FunctionalIds;
            for (int a = 0; a < fids.Length; a++)
            {
                for (int b = 0; b < fids.Length; b++)
                {
                    if (a == b)
                    {
                        continue;
                    }

                    count++;
                    Assert.Equal(0f, m.W[RowOf(m, fids[a]), RowOf(m, fids[b])]);
                }
            }
        }

        Assert.Equal(50, count);
    }

    // ---- AC-12：21 排除 fid 的 Tau 均 > 0（排除节点仍 WC 驱动，C9）----

    [Fact]
    public void ExcludedFids_TauAllPositive()
    {
        GameData data = LoadData();
        WMatrix m = WMatrixBuilder.Build(data);

        foreach (var fid in ExcludedFids(data.Tripartite))
        {
            Assert.True(m.Tau[RowOf(m, fid)] > 0f, $"{fid} 的 Tau 应 > 0（排除节点仍由 WC 驱动）");
        }
    }
}
