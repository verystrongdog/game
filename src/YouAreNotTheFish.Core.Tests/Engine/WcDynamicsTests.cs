using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// WcDynamics spec@v1.1（.scratch/csharp-wc-dynamics/design/spec.md）§六 AC-1~AC-12。
/// 数据依赖断言（AC-5/6/9/12）兼作数据漂移哨兵——数据 JSON 变更时同步复核期望值。
/// 测试侧约定（sign-off 结转 #1/#2）：RowFids 用 fid 名（'Pericalcarine' 大写）；
/// 逐位断言与公式期望一律 MathF 自算，不写字面量。
/// </summary>
public class WcDynamicsTests
{
    // ---- 数据加载（复用 WMatrixBuilderTests 的 FindDataDir 候选路径模式）----

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

    private static WMatrix BuildReal() => WMatrixBuilder.Build(GameDataLoader.LoadAll(FindDataDir()));

    /// <summary>合成矩阵助手：W 全 0 或给定值、τ 给定、RowFids 占位（Step 不消费名字——C1）。</summary>
    private static WMatrix Synthetic(float[,] w, float[] tau)
    {
        return new WMatrix(w, tau, Enumerable.Range(0, 69).Select(i => $"F{i}").ToArray());
    }

    private static float[] Fill(float v) => Enumerable.Repeat(v, 69).ToArray();

    private static int RowOf(WMatrix m, string fid)
    {
        int i = Array.IndexOf(m.RowFids, fid);
        if (i < 0)
        {
            throw new InvalidDataException($"RowFids 中无 {fid}");
        }

        return i;
    }

    /// <summary>测试侧 σ（镜像 spec §二：v=1.0、θ=0.5；结转 #2——逐位断言用 MathF 自算）。</summary>
    private static float SigmaT(float x) => 1f / (1f + MathF.Exp(-(x - 0.5f)));

    /// <summary>绝对容差 1e-5 断言（spec §六：标注「逐位」者精确相等，其余 1e-5f）。</summary>
    private static void AssertApprox(float expected, float actual, string what)
    {
        Assert.True(Math.Abs(expected - actual) <= 1e-5f,
            $"{what}: 期望 {expected}，实际 {actual}，偏差 {Math.Abs(expected - actual)}");
    }

    /// <summary>行和——排除节点（W 行=0）由矩阵自身推导，不硬编码名单（与 wmatrix AC-5 口径一致）。</summary>
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

    // ---- AC-1：形状与不可变性 ----

    [Fact]
    public void Step_ReturnsNew69Array_AndDoesNotMutateInputs()
    {
        float[] aIn = Enumerable.Range(0, 69).Select(i => 0.10f + i * 0.001f).ToArray();
        float[] b = Enumerable.Range(0, 69).Select(i => 0.05f + i * 0.0005f).ToArray();
        float[] s = Enumerable.Range(0, 69).Select(i => 0.02f + i * 0.0002f).ToArray();
        float[,] wIn = new float[69, 69];
        wIn[3, 5] = 0.5f;
        float[] tau = Fill(0.05f);
        var a = new WcState(aIn);
        var w = Synthetic(wIn, tau);

        float[] aSnap = (float[])aIn.Clone();
        float[] bSnap = (float[])b.Clone();
        float[] sSnap = (float[])s.Clone();
        float[,] wSnap = (float[,])wIn.Clone();
        float[] tauSnap = (float[])tau.Clone();

        WcState result = WcDynamics.Step(a, b, s, w);

        Assert.Equal(69, result.A.Length);
        Assert.NotSame(a.A, result.A);

        // 输出可改不影响输入（防御拷贝契约 C5）
        result.A[0] = 999f;
        Assert.Equal(aSnap, a.A);
        Assert.Equal(bSnap, b);
        Assert.Equal(sSnap, s);

        for (int j = 0; j < 69; j++)
        {
            for (int k = 0; k < 69; k++)
            {
                Assert.Equal(wSnap[j, k], w.W[j, k]);
            }

            Assert.Equal(tauSnap[j], w.Tau[j]);
        }
    }

    // ---- AC-2：快节点精确收敛（e^(−100) 修正项低于 float32 舍入粒度 → 逐位相等）----

    [Fact]
    public void Step_FastTau_ConvergesBitExactToSigma()
    {
        var w = Synthetic(new float[69, 69], Fill(0.01f));
        var a = new WcState(Fill(0.10f));

        WcState result = WcDynamics.Step(a, Fill(1.0f), Fill(0f), w);

        float expected = SigmaT(1.0f); // 锚点 0.622459331（σ(1.0)，逐位）
        for (int j = 0; j < 69; j++)
        {
            Assert.Equal(expected, result.A[j]);
        }
    }

    // ---- AC-3：解析解公式锚点（slow τ=0.15）----

    [Fact]
    public void Step_SlowTau_MatchesAnalyticAnchors()
    {
        var w = Synthetic(new float[69, 69], Fill(0.15f));

        // (a) b=1.0、a=0.10 → 0.621794432
        WcState r1 = WcDynamics.Step(new WcState(Fill(0.10f)), Fill(1.0f), Fill(0f), w);
        AssertApprox(0.621794432f, r1.A[0], "AC-3a slow 锚点");

        // (b) b=0、a=0.90 → 0.378205568
        WcState r2 = WcDynamics.Step(new WcState(Fill(0.90f)), Fill(0f), Fill(0f), w);
        AssertApprox(0.378205568f, r2.A[0], "AC-3b slow 锚点");
    }

    // ---- AC-4：单调不振荡（解析解保证；Euler 违反——B1 的动机）----

    [Fact]
    public void Step_SlowTau_IsStrictlyBetweenAAndSigma()
    {
        var w = Synthetic(new float[69, 69], Fill(0.15f));
        float a0 = 0.10f;
        float sigma = SigmaT(1.0f);

        WcState result = WcDynamics.Step(new WcState(Fill(a0)), Fill(1.0f), Fill(0f), w);

        Assert.True(result.A[0] > a0, $"a' 应 > a={a0}，实际 {result.A[0]}");
        Assert.True(result.A[0] < sigma, $"a' 应 < σ(1.0)={sigma}，实际 {result.A[0]}");
    }

    // ---- AC-5：静息吸引子（真实 W，b=s=0，a(0)=0.10，30 回合）----

    [Fact]
    public void Step_RestingAttractor_MatchesMeasuredFixedPoint()
    {
        WMatrix m = BuildReal();
        bool[] excluded = ExcludedRows(m);
        int activeCount = excluded.Count(e => !e);
        Assert.Equal(48, activeCount);
        Assert.Equal(21, excluded.Count(e => e));

        float[] zero = Fill(0f);
        WcState cur = new WcState(Fill(0.10f));
        for (int round = 0; round < 30; round++)
        {
            cur = WcDynamics.Step(cur, zero, zero, m);
        }

        WcState next = WcDynamics.Step(cur, zero, zero, m);

        float maxDelta = 0f;
        for (int j = 0; j < 69; j++)
        {
            if (excluded[j])
            {
                // 21 排除节点终态 == σ(0)（1e-5）
                AssertApprox(0.377540669f, cur.A[j], $"排除节点 {m.RowFids[j]} 终态");
            }
            else
            {
                // 48 活跃节点终态 ∈ [0.4986, 0.49951]（实测锚点范围——数据漂移哨兵；
                // AC 规范区间 [0.49, 0.50] 为其子集）
                Assert.True(cur.A[j] >= 0.4986f && cur.A[j] <= 0.49951f,
                    $"活跃节点 {m.RowFids[j]} 终态 {cur.A[j]} 应 ∈ [0.4986, 0.49951]");
            }

            // 终态 ≠ 0.10（B2：0.10 是初始值非吸引子）
            Assert.True(Math.Abs(cur.A[j] - 0.10f) > 1e-3f,
                $"节点 {m.RowFids[j]} 终态不应停留在初始值 0.10");

            maxDelta = Math.Max(maxDelta, Math.Abs(next.A[j] - cur.A[j]));
        }

        // round30 vs 31 max|Δ| < 1e-4
        Assert.True(maxDelta < 1e-4f, $"round30 vs 31 max|Δ|={maxDelta} 应 < 1e-4");
    }

    // ---- AC-6：排除节点响应 b/s（真实 W，h 与 a 无关）----

    [Fact]
    public void Step_ExcludedNode_RespondsToBAndS_IndependentOfA()
    {
        WMatrix m = BuildReal();
        bool[] excluded = ExcludedRows(m);
        int idx = Array.FindIndex(excluded, e => e);
        Assert.True(idx >= 0, "应存在排除节点");
        string fid = m.RowFids[idx];

        float[] b = Fill(0f);
        float[] s = Fill(0f);
        b[idx] = 0.7f;
        s[idx] = 0.3f;

        // h_j = b_j + s_j = 1.0（W 行=0），与 a 无关——a 全 1.0 与 a 全 0.3 两次调用结果一致
        WcState r1 = WcDynamics.Step(new WcState(Fill(1.0f)), b, s, m);
        WcState r2 = WcDynamics.Step(new WcState(Fill(0.3f)), b, s, m);

        // 期望按实际 τ_j 自算（结转 #2：MathF，不写字面量）
        float expected = SigmaT(1.0f) + (1.0f - SigmaT(1.0f)) * MathF.Exp(-1f / m.Tau[idx]);
        AssertApprox(expected, r1.A[idx], $"排除节点 {fid}（a=1.0）");
        Assert.Equal(r1.A[idx], r2.A[idx]);
    }

    // ---- AC-7：bimodal s=2.0（合成 W=0、τ fast → 逐位 == σ(2.0)）----

    [Fact]
    public void Step_BimodalInput_BitExactSigma2()
    {
        var w = Synthetic(new float[69, 69], Fill(0.01f));

        WcState result = WcDynamics.Step(new WcState(Fill(0.10f)), Fill(0f), Fill(2.0f), w);

        float expected = SigmaT(2.0f); // 锚点 0.817574476（σ(2.0)，逐位——MathF 自算）
        for (int j = 0; j < 69; j++)
        {
            Assert.Equal(expected, result.A[j]);
            Assert.False(float.IsNaN(result.A[j]));
            Assert.True(result.A[j] >= 0f && result.A[j] <= 1f);
        }
    }

    // ---- AC-8：同步更新（就地逐行更新会得到反例 0.422814620 → 失败）----

    [Fact]
    public void Step_UsesSynchronousUpdate()
    {
        float[,] wIn = new float[69, 69];
        wIn[1, 0] = 0.5f;
        var w = Synthetic(wIn, Fill(0.01f));

        float[] aIn = Fill(0f);
        aIn[0] = 1.0f;
        float[] zero = Fill(0f);

        WcState result = WcDynamics.Step(new WcState(aIn), zero, zero, w);

        // a'_0 == σ(0)（h_0=0，τ fast 逐位）
        Assert.Equal(SigmaT(0f), result.A[0]);
        // a'_1 == σ(0.5) == 0.5（h_1 = W[1][0]·a_0 = 0.5·1.0 = 0.5）
        // 就地实现会先写 a'_0=σ(0)=0.3775 再算 h_1=0.5·0.3775 → a'_1=0.422814620 ≠ 0.5
        Assert.Equal(0.5f, result.A[1]);
    }

    // ---- AC-9：方向契约哨兵（真实 W；结转 #1：RowFids 用 fid 名 'Pericalcarine' 大写）----

    [Fact]
    public void Step_DirectionSentinel_PericalcarineToAmygdala()
    {
        WMatrix m = BuildReal();
        int rowAmy = RowOf(m, "Amygdala");
        int rowPeri = RowOf(m, "Pericalcarine");

        // 唯一非互惠对：W[Amygdala][Pericalcarine] > 0、反向 0（wmatrix AC-7 锚点）
        float wAmyPeri = m.W[rowAmy, rowPeri];
        Assert.True(wAmyPeri > 0f, "W[Amygdala][Pericalcarine] 应 > 0");
        Assert.Equal(0f, m.W[rowPeri, rowAmy]);

        // a 仅 Pericalcarine=1.0
        float[] aIn = Fill(0f);
        aIn[rowPeri] = 1.0f;
        float[] zero = Fill(0f);

        WcState result = WcDynamics.Step(new WcState(aIn), zero, zero, m);

        // h_Amygdala = W[Amygdala][Pericalcarine]·1 = wAmyPeri（按实际 τ 自算期望）
        float tauAmy = m.Tau[rowAmy];
        float expAmy = SigmaT(wAmyPeri) + (0f - SigmaT(wAmyPeri)) * MathF.Exp(-1f / tauAmy);
        AssertApprox(expAmy, result.A[rowAmy], "a'_Amygdala");

        // h_Pericalcarine == 0：自连接 w(Peri,Peri)=0 且其余列 a=0 → 按公式自算（a_j=1.0）
        float tauPeri = m.Tau[rowPeri];
        float expPeri = SigmaT(0f) + (1f - SigmaT(0f)) * MathF.Exp(-1f / tauPeri);
        AssertApprox(expPeri, result.A[rowPeri], "a'_Pericalcarine");

        // 转置实现必失败：转置时 h_Amy=W[Peri][Amy]·a_Peri=0 → a'_Amy≈σ(0)，与 expAmy 差 ~4.9e-3
    }

    // ---- AC-10：确定性（同输入两次调用逐位相等）----

    [Fact]
    public void Step_IsDeterministic()
    {
        WMatrix m = BuildReal();
        var a = new WcState(Enumerable.Range(0, 69).Select(i => 0.10f + i * 0.005f).ToArray());
        float[] b = Enumerable.Range(0, 69).Select(i => 0.05f + i * 0.001f).ToArray();
        float[] s = Enumerable.Range(0, 69).Select(i => 0.01f + i * 0.002f).ToArray();

        WcState r1 = WcDynamics.Step(a, b, s, m);
        WcState r2 = WcDynamics.Step(a, b, s, m);

        for (int j = 0; j < 69; j++)
        {
            Assert.Equal(r1.A[j], r2.A[j]);
        }
    }

    // ---- AC-11：契约防御 ----

    [Fact]
    public void Step_NullInputs_ThrowArgumentNullException()
    {
        var a = new WcState(Fill(0.10f));
        var b = Fill(0f);
        var s = Fill(0f);
        var w = Synthetic(new float[69, 69], Fill(0.05f));

        Assert.Throws<ArgumentNullException>(() => WcDynamics.Step(null!, b, s, w));
        Assert.Throws<ArgumentNullException>(() => WcDynamics.Step(a, null!, s, w));
        Assert.Throws<ArgumentNullException>(() => WcDynamics.Step(a, b, null!, w));
        Assert.Throws<ArgumentNullException>(() => WcDynamics.Step(a, b, s, null!));
    }

    [Fact]
    public void Step_InvalidShapes_ThrowArgumentException()
    {
        var a = new WcState(Fill(0.10f));
        var s = Fill(0f);
        var w = Synthetic(new float[69, 69], Fill(0.05f));

        Assert.Throws<ArgumentException>(() => WcDynamics.Step(a, new float[68], s, w));
        Assert.Throws<ArgumentException>(() => WcDynamics.Step(a, Fill(0f), new float[70], w));
        Assert.Throws<ArgumentException>(() => WcDynamics.Step(a, Fill(0f), s,
            Synthetic(new float[68, 69], Fill(0.05f))));
        Assert.Throws<ArgumentException>(() => WcDynamics.Step(a, Fill(0f), s,
            Synthetic(new float[69, 68], Fill(0.05f))));
        Assert.Throws<ArgumentException>(() => WcDynamics.Step(a, Fill(0f), s,
            Synthetic(new float[69, 69], new float[68])));
    }

    [Fact]
    public void Step_NonPositiveTau_ThrowsArgumentException()
    {
        var a = new WcState(Fill(0.10f));
        var s = Fill(0f);

        float[] tauZero = Fill(0.05f);
        tauZero[0] = 0f;
        Assert.Throws<ArgumentException>(() => WcDynamics.Step(a, Fill(0f), s,
            Synthetic(new float[69, 69], tauZero)));

        float[] tauNeg = Fill(0.05f);
        tauNeg[10] = -0.01f;
        Assert.Throws<ArgumentException>(() => WcDynamics.Step(a, Fill(0f), s,
            Synthetic(new float[69, 69], tauNeg)));
    }

    // ---- AC-12：极端输入无 NaN/上溢 ----

    [Fact]
    public void Step_ExtremeInputs_AllFiniteIn01()
    {
        WMatrix m = BuildReal();

        WcState result = WcDynamics.Step(new WcState(Fill(1.0f)), Fill(2.0f), Fill(2.0f), m);

        float max = 0f;
        for (int j = 0; j < 69; j++)
        {
            float v = result.A[j];
            Assert.False(float.IsNaN(v), $"节点 {m.RowFids[j]} 输出不应为 NaN");
            Assert.False(float.IsInfinity(v), $"节点 {m.RowFids[j]} 输出不应为 ±∞");
            Assert.True(v >= 0f && v <= 1f, $"节点 {m.RowFids[j]} 输出 {v} 应 ∈ [0,1]");
            max = Math.Max(max, v);
        }

        // 实测真实输出 max ∈ [0.9707, 0.9890]（h ≤ 行和+4 ≤ 5 → σ(5)=0.989013 上界）
        Assert.InRange(max, 0.9707f, 0.9890f);
    }
}
