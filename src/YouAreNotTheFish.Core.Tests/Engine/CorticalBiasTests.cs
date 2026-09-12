using System.IO;
using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// CorticalBias spec@v1.1（../../../规格/引擎/csharp-tone.md）§六 AC-9~AC-14、AC-16。
/// 行序定位一律经 RegionIds 推导（wmatrix 结转 #1：不裸写 fid 名下标，防 dk/fid 命名陷阱）。
/// 数据依赖断言（AC-10~14）兼作数据漂移哨兵。
/// </summary>
public class CorticalBiasTests
{
    // ---- 数据加载（复用 WcDynamicsTests 的 FindDataDir 候选路径模式）----

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

    private static GameData Load() => GameDataLoader.LoadAll(FindDataDir());

    private static ToneState Baseline() => new()
    {
        Ne = 0.3f,
        DaVta = 0.4f,
        DaSnc = 0.5f,
        Ht5 = 0.5f,
    };

    /// <summary>fid → 行序（经 RegionIds 推导，不裸写下标）。</summary>
    private static int RowOf(GameData data, string fid)
    {
        int i = Array.IndexOf(data.Wsensory.RegionIds, fid);
        if (i < 0)
        {
            throw new InvalidDataException($"RegionIds 中无 {fid}");
        }

        return i;
    }

    private static void AssertApprox(float expected, float actual, string what)
    {
        Assert.True(Math.Abs(expected - actual) <= 1e-5f,
            $"{what}: 期望 {expected}，实际 {actual}，偏差 {Math.Abs(expected - actual)}");
    }

    /// <summary>合成伪边（AC-16 用）——真实数据 + 追加伪造 brainstem 边（经 record with + 集合表达式）。</summary>
    private static GameData WithExtraEdge(GameData data, BrainstemProjection edge) =>
        data with
        {
            Tripartite = data.Tripartite with
            {
                Brainstem = [.. data.Tripartite.Brainstem, edge],
            },
        };

    // ---- AC-9：形状与行序 ----

    [Fact]
    public void Compute_ReturnsNew69Array_WithCanonicalRowOrder()
    {
        var data = Load();
        var b1 = CorticalBias.Compute(Baseline(), data);
        var b2 = CorticalBias.Compute(Baseline(), data);

        Assert.Equal(69, b1.Length);
        Assert.NotSame(b1, b2); // 新数组输出
        Assert.Equal(b1, b2); // 确定性（同输入同输出）

        // 契约 C1：canonical 行序首键 AccumbensCore（csharp-wmatrix spec Step 1）
        Assert.Equal("AccumbensCore", data.Wsensory.RegionIds[0]);
        // 行序 = RegionIds：AccumbensCore 的行值按 AC-11 锚点核对（b=0.9）即证行序正确
        AssertApprox(0.9f, b1[RowOf(data, "AccumbensCore")], "AccumbensCore 行序锚点");
    }

    // ---- AC-10：per-target 唯一（Q1 裁决锁定）----

    [Fact]
    public void Compute_BanksSTS_PerTargetUnique()
    {
        var data = Load();
        var b = CorticalBias.Compute(Baseline(), data);

        // BanksSTS（LC mod 0.5×0.3=0.15 + Raphe mod 0.5×0.5=0.25）= 0.4
        // per-edge 求和（DR+MnR 双计）会得 0.65——断言 0.4 锁定 Q1 裁决
        AssertApprox(0.3f * 0.5f + 0.5f * 0.5f, b[RowOf(data, "BanksSTS")], "BanksSTS per-target");
    }

    // ---- AC-11：role 两档 + 排除节点接收 b_j ----

    [Fact]
    public void Compute_BaselineTone_StriatalAndAmygdalaAnchors()
    {
        var data = Load();
        var b = CorticalBias.Compute(Baseline(), data);

        // NAcc 4 fid：VTA act 1.0×0.4 + SNc act 1.0×0.5 = 0.9
        foreach (var fid in new[] { "AccumbensCore", "AccumbensShell", "NucleusAccumbens", "VentralStriatum" })
        {
            AssertApprox(1.0f * 0.4f + 1.0f * 0.5f, b[RowOf(data, fid)], fid);
        }

        // Caudate/StriatumMatrix/Putamen：VTA mod 0.5×0.4 + SNc act 1.0×0.5 = 0.7
        foreach (var fid in new[] { "Caudate", "StriatumMatrix", "Putamen" })
        {
            AssertApprox(0.5f * 0.4f + 1.0f * 0.5f, b[RowOf(data, fid)], fid);
        }

        // Amygdala：VTA mod 0.5×0.4 + Raphe mod 0.5×0.5 = 0.45
        AssertApprox(0.5f * 0.4f + 0.5f * 0.5f, b[RowOf(data, "Amygdala")], "Amygdala");
    }

    // ---- AC-12：零广播节点 ----

    [Fact]
    public void Compute_ZeroBroadcastNodes_AreExactlyZero()
    {
        var data = Load();
        var b = CorticalBias.Compute(Baseline(), data);

        // §5.7 正典四名逐位为 0
        foreach (var fid in new[] { "PeriaqueductalGray", "SuperiorColliculus", "PontineReticularNucleus", "CerebellumCortex" })
        {
            Assert.Equal(0f, b[RowOf(data, fid)]);
        }

        // 全零集合由数据推导：brainstem 类别节点的全部 fids + 5 个已知零接收者 = 15
        var expected = new HashSet<string>(
            data.Tripartite.GraphNodes.Values
                .Where(n => n.Category == BrainRegionCategory.Brainstem)
                .SelectMany(n => n.FunctionalIds));
        expected.UnionWith(new[] { "CerebellumCortex", "Pallidum", "SubthalamicNucleus", "Thalamus", "ThalamusPulvinar" });

        var actual = new HashSet<string>(
            data.Wsensory.RegionIds.Where((_, i) => b[i] == 0f));

        Assert.Equal(15, expected.Count);
        Assert.True(expected.SetEquals(actual),
            $"零广播集合失配。仅预期: {string.Join(",", expected.Except(actual))}；仅实际: {string.Join(",", actual.Except(expected))}");
    }

    // ---- AC-13：clamp [0,2] ----

    [Fact]
    public void Compute_AllOnesTone_ClampsToTwo()
    {
        var data = Load();
        var tone1 = new ToneState { Ne = 1f, DaVta = 1f, DaSnc = 1f, Ht5 = 1f };
        var b = CorticalBias.Compute(tone1, data);

        // 输出全部 ∈ [0,2]
        Assert.All(b, v => Assert.InRange(v, 0f, 2f));
        Assert.Equal(2f, b.Max());

        // clamp 命中集合由数据推导（pre-clamp > 2 的 fid 重算自脑干边，per-target 唯一口径）：
        // == {FrontalPoleDMN, MedialOrbitalPrefrontalDMN, MedialOrbitalPrefrontalVMPFC}（pre-clamp 2.5 → 2.0）
        var preClamp = PreClamp(tone1, data);
        var hit = data.Wsensory.RegionIds.Where((f, i) => preClamp[i] > 2f + 1e-5f).ToHashSet();
        var boundary = data.Wsensory.RegionIds.Where((f, i) =>
            Math.Abs(preClamp[i] - 2f) <= 1e-5f).ToHashSet();

        Assert.Equal(
            new HashSet<string> { "FrontalPoleDMN", "MedialOrbitalPrefrontalDMN", "MedialOrbitalPrefrontalVMPFC" },
            hit);
        // 10 个边界 fid（pre-clamp 恰 2.0）clamp 数值不变，不属命中集合：
        // Accumbens-area 4 + rostralmiddlefrontal 3 + superiorfrontal 2 + lateralorbitofrontal 1
        Assert.Equal(10, boundary.Count);
        foreach (var fid in hit.Concat(boundary))
        {
            Assert.Equal(2f, b[RowOf(data, fid)]);
        }
    }

    /// <summary>测试侧重算 pre-clamp b_j（镜像生产算法但不 clamp）——用于区分「严格超界」与「恰为 2.0」。</summary>
    private static float[] PreClamp(ToneState tone, GameData data)
    {
        var rowOf = new Dictionary<string, int>(data.Wsensory.RegionIds.Length);
        for (int i = 0; i < data.Wsensory.RegionIds.Length; i++)
        {
            rowOf[data.Wsensory.RegionIds[i]] = i;
        }

        var seen = new HashSet<(BrainstemSystem, string)>();
        var b = new float[data.Wsensory.RegionIds.Length];
        foreach (var e in data.Tripartite.Brainstem)
        {
            if (!seen.Add((e.System, e.Target))) continue;
            float w = e.Role == EdgeRole.Active ? 1f : 0.5f;
            float t = e.System switch
            {
                BrainstemSystem.LcNe => tone.Ne,
                BrainstemSystem.Raphe5Ht => tone.Ht5,
                BrainstemSystem.SncDa => tone.DaSnc,
                _ => tone.DaVta,
            };
            foreach (var fid in data.Tripartite.GraphNodes[e.Target].FunctionalIds)
            {
                b[rowOf[fid]] += t * w;
            }
        }

        return b;
    }

    // ---- AC-14：基线 b_j 锚点 ----

    [Fact]
    public void Compute_BaselineTone_MedialOrbitofrontalAnchor()
    {
        var data = Load();
        var b = CorticalBias.Compute(Baseline(), data);

        // mOFC 3 fid：5HT act 1.0×0.5 + VTA act 1.0×0.4 + LC mod 0.5×0.3 = 1.05
        foreach (var fid in new[] { "FrontalPoleDMN", "MedialOrbitalPrefrontalDMN", "MedialOrbitalPrefrontalVMPFC" })
        {
            AssertApprox(1.0f * 0.5f + 1.0f * 0.4f + 0.5f * 0.3f, b[RowOf(data, fid)], fid);
        }
    }

    // ---- AC-16：契约防御（E2 新增）----

    [Fact]
    public void Compute_NullArguments_Throw()
    {
        var data = Load();
        Assert.Throws<ArgumentNullException>(() => CorticalBias.Compute(null!, data));
        Assert.Throws<ArgumentNullException>(() => CorticalBias.Compute(Baseline(), null!));
    }

    [Fact]
    public void Compute_UnknownTarget_ThrowsInvalidData()
    {
        var data = Load();
        var pseudo = WithExtraEdge(data, new BrainstemProjection
        {
            Source = "VentralTegmentalArea",
            Target = "no-such-dk",
            System = BrainstemSystem.VtaDa,
            Neurotransmitter = Neurotransmitter.Dopamine,
            Projection = BrainstemProjectionType.TargetedBroadcast,
            Role = EdgeRole.Active,
        });

        var ex = Assert.Throws<InvalidDataException>(() => CorticalBias.Compute(Baseline(), pseudo));
        Assert.Contains("no-such-dk", ex.Message); // 含边描述
        Assert.Contains("VtaDa", ex.Message);
    }

    [Fact]
    public void Compute_SilentEdge_ThrowsInvalidData()
    {
        var data = Load();
        var realTarget = data.Tripartite.GraphNodes.Keys.First();
        var pseudo = WithExtraEdge(data, new BrainstemProjection
        {
            Source = "LocusCoeruleus",
            Target = realTarget,
            System = BrainstemSystem.LcNe,
            Neurotransmitter = Neurotransmitter.Norepinephrine,
            Projection = BrainstemProjectionType.DiffuseBroadcast,
            Role = EdgeRole.Silent,
        });

        var ex = Assert.Throws<InvalidDataException>(() => CorticalBias.Compute(Baseline(), pseudo));
        Assert.Contains("Silent", ex.Message);
    }
}
