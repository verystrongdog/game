using Xunit.Abstractions;
using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// M1 静息 trace 里程碑——spec@v1.1（../../../规格/引擎/csharp-tone.md）§六 AC-15。
/// 组合 WMatrixBuilder.Build + CorticalBias.Compute(baseline) + WcDynamics.Step，tone=baseline、s=0、
/// a(0)=0.10，30 回合实测静息不动点。ITestOutputHelper 输出 69 节点实测值表（供 M1 文档写回：
/// plan §十三-8 清扫 + wc-dynamics 结转 #4）。
/// 偏差 B4 锁定：plan §八「b_j>0 会略高」预测被实测推翻——静息吸引子 ≈0.5 的基线偏移远非「略高」
/// （active max 0.7712）。
/// </summary>
public class M1RestingTraceTests
{
    private readonly ITestOutputHelper _out;

    public M1RestingTraceTests(ITestOutputHelper output)
    {
        _out = output;
    }

    // ---- 数据加载（复用 WcDynamicsTests 的 FindDataDir 候选路径模式）----

    private static readonly string[] DataDirCandidates =
    [
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..", "data"),
        Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..", "data")),
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

    private static ToneState Baseline() => new()
    {
        Ne = 0.3f,
        DaVta = 0.4f,
        DaSnc = 0.5f,
        Ht5 = 0.5f,
    };

    private static float[] Fill(float v) => Enumerable.Repeat(v, 69).ToArray();

    /// <summary>测试侧 σ（镜像 wc-dynamics spec §二：v=1.0、θ=0.5）。</summary>
    private static float SigmaT(float x) => 1f / (1f + MathF.Exp(-(x - 0.5f)));

    /// <summary>排除节点（W 行=0）由矩阵自身推导，不硬编码名单（与 wc-dynamics AC-5 口径一致）。</summary>
    private static bool[] ExcludedRows(WMatrix m)
    {
        var excluded = new bool[69];
        for (int j = 0; j < 69; j++)
        {
            float sum = 0f;
            for (int k = 0; k < 69; k++)
            {
                sum += m.W[j, k];
            }

            excluded[j] = sum == 0f;
        }

        return excluded;
    }

    private static void AssertApprox(float expected, float actual, string what)
    {
        Assert.True(Math.Abs(expected - actual) <= 1e-5f,
            $"{what}: 期望 {expected}，实际 {actual}，偏差 {Math.Abs(expected - actual)}");
    }

    // ---- AC-15：30 回合静息 trace ----

    [Fact]
    public void RestingTrace_30Rounds_ConvergesToMeasuredFixedPoint()
    {
        var data = GameDataLoader.LoadAll(FindDataDir());
        var w = WMatrixBuilder.Build(data);
        var b = CorticalBias.Compute(Baseline(), data);
        var s = Fill(0f);

        // a(0) = 0.10（回合战斗流程 §3.3 静息基线初始值——战斗初始化是 step 10 职责，此处仅设初态）
        var state = new WcState(Fill(0.10f));
        float[] prev = state.A;
        for (int round = 1; round <= 30; round++)
        {
            prev = state.A;
            state = WcDynamics.Step(state, b, s, w);
        }

        // 收敛断言：round 30 与 round 29 max|Δ| < 1e-5（python 预览 round 10 即 7e-7）
        float maxDelta = 0f;
        for (int i = 0; i < 69; i++)
        {
            maxDelta = MathF.Max(maxDelta, MathF.Abs(state.A[i] - prev[i]));
        }

        Assert.True(maxDelta < 1e-5f, $"round 30 vs 29 max|Δ| = {maxDelta}，应 < 1e-5");

        // active（W 行非零）∈ [0.53, 0.78]（预览 [0.535174, 0.771229]）
        var excluded = ExcludedRows(w);
        int activeCount = 0;
        for (int i = 0; i < 69; i++)
        {
            if (excluded[i]) continue;
            activeCount++;
            Assert.InRange(state.A[i], 0.53f, 0.78f);
        }

        Assert.Equal(48, activeCount); // 21 排除 + 48 active = 69（数据漂移哨兵）

        // 排除节点：a == σ(b_j) 三组（b=0→0.3775407 / b=0.7→0.5498340 / b=0.9→0.5986877）
        int c0 = 0, c07 = 0, c09 = 0;
        for (int i = 0; i < 69; i++)
        {
            if (!excluded[i]) continue;
            AssertApprox(SigmaT(b[i]), state.A[i], $"{w.RowFids[i]} 排除节点固定点");
            if (Math.Abs(b[i]) <= 1e-5f) c0++;
            else if (Math.Abs(b[i] - 0.7f) <= 1e-5f) c07++;
            else if (Math.Abs(b[i] - 0.9f) <= 1e-5f) c09++;
            else Assert.Fail($"排除节点 {w.RowFids[i]} 的 b={b[i]} 不在三组 {0f}/{0.7f}/{0.9f} 内");
        }

        Assert.Equal(14, c0);
        Assert.Equal(3, c07);
        Assert.Equal(4, c09);

        // 69 节点实测值表（供 M1 文档写回——plan §十三-8 + wc-dynamics 结转 #4）
        _out.WriteLine($"M1 静息 trace 实测（30 回合，maxΔ={maxDelta}，active 48 ∈ [{MinActive(w, excluded, state)}, {MaxActive(w, excluded, state)}]）");
        _out.WriteLine("fid\tb_j\ta(round30)");
        for (int i = 0; i < 69; i++)
        {
            _out.WriteLine($"{w.RowFids[i]}\t{b[i]:F7}\t{state.A[i]:F7}");
        }
    }

    private static float MinActive(WMatrix w, bool[] excluded, WcState state)
    {
        float min = float.MaxValue;
        for (int i = 0; i < 69; i++)
        {
            if (!excluded[i]) min = MathF.Min(min, state.A[i]);
        }

        return min;
    }

    private static float MaxActive(WMatrix w, bool[] excluded, WcState state)
    {
        float max = float.MinValue;
        for (int i = 0; i < 69; i++)
        {
            if (!excluded[i]) max = MathF.Max(max, state.A[i]);
        }

        return max;
    }
}
