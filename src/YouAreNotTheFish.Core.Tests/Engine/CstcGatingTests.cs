using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// CstcGating spec@v1.1（.scratch/csharp-cstc/design/spec.md）§六 AC-1~AC-15。
/// 测试侧约定（wmatrix 结转 #1）：锚点一律测试侧公式现算（1e-5 容差）或逐位比较，不裸写可推导字面量；
/// 例外：迭代 300 回合固定点（0.8434211/0.8065790/1.0）无闭式解，按 spec §六 实测锚点（1e-5）。
/// 迭代语义（spec §六 声明）：固定 300 回合，禁止 max|Δ| 终止判据（结转 #1 预防）。
/// </summary>
public class CstcGatingTests
{
    // ---- 数据加载（复用 M1RestingTraceTests 的 FindDataDir 候选路径模式）----

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

    private static readonly Lazy<GameData> Data =
        new(() => GameDataLoader.LoadAll(FindDataDir()));

    private static readonly Lazy<CstcGating> Gating = new(() => new CstcGating(Data.Value));

    /// <summary>spec §二 2.3 实测 CI fid 名单（2026-08-13 python 实测，任务issue 数据实测表 #1）。</summary>
    private static readonly string[] SomaticCiFids = ["Paracentral", "Precentral", "SuperiorFrontal"];

    private static readonly string[] CognitiveCiFids =
    [
        "AnteriorCingulateCortexDorsal", "CaudalMiddleFrontal", "FrontalPole", "FrontalPoleExtreme",
        "FrontalPoleFPN", "ParsOpercularis", "RostralMiddleFrontalDLPFC",
    ];

    private static readonly string[] LimbicCiFids =
    [
        "Amygdala", "AnteriorCingulateCortex", "FrontalPoleDMN", "FrontalPoleSN",
        "HippocampusCA1", "HippocampusCA3", "Insula", "LateralOrbitofrontal",
        "MedialOrbitalPrefrontalDMN", "MedialOrbitalPrefrontalVMPFC",
        "RostralAnteriorCingulateCortex", "SuperiorFrontalMPFC",
    ];

    // ---- 合成输入助手 ----

    private static ToneState Baseline() => new()
    {
        Ne = 0.3f,
        DaVta = 0.4f,
        DaSnc = 0.5f,
        Ht5 = 0.5f,
    };

    private static ToneState ToneOf(float vta, float snc) => new()
    {
        Ne = 0.3f,
        DaVta = vta,
        DaSnc = snc,
        Ht5 = 0.5f,
    };

    private static float[] Fill(float v) => Enumerable.Repeat(v, 69).ToArray();

    private static float[] Fill5(float v) => [v, v, v, v, v];

    private static GurneyState ZeroGurney() =>
        new(Fill5(0f), Fill5(0f), Fill5(0f));

    /// <summary>指定 fid 置 1、其余 0 的合成 WC 状态（fid → canonical 行经 Wsensory.RegionIds 解析，不裸写下标）。</summary>
    private static WcState FidsOn(params string[] fids)
    {
        var rowOf = RowOf();
        var a = Fill(0f);
        foreach (var fid in fids)
        {
            a[rowOf[fid]] = 1f;
        }

        return new WcState(a);
    }

    private static Dictionary<string, int> RowOf()
    {
        var regionIds = Data.Value.Wsensory.RegionIds;
        var rowOf = new Dictionary<string, int>(regionIds.Length);
        for (int i = 0; i < regionIds.Length; i++)
        {
            rowOf[regionIds[i]] = i;
        }

        return rowOf;
    }

    private static string[] FidsOf(CstcLoop loop) =>
        Gating.Value.CiRows[loop].Select(r => Data.Value.Wsensory.RegionIds[r]).ToArray();

    /// <summary>绝对容差 1e-5 断言（spec §六：标注「逐位」者精确相等，其余 1e-5）。</summary>
    private static void AssertApprox(float expected, float actual, string what)
    {
        Assert.True(Math.Abs(expected - actual) <= 1e-5f,
            $"{what}: 期望 {expected}，实际 {actual}，偏差 {Math.Abs(expected - actual)}");
    }

    private static void AssertArrayApprox(float[] expected, float[] actual, string what)
    {
        Assert.Equal(expected.Length, actual.Length);
        for (int i = 0; i < expected.Length; i++)
        {
            AssertApprox(expected[i], actual[i], $"{what}[{i}]");
        }
    }

    // ---- 测试侧镜像（spec §三 Step 职责 1-6；常量逐字来自 spec §四——公式现算，不复制锚点输出）----

    /// <summary>测试侧 ramp（spec §四 4.5；B2 m≤0→O≡0）。</summary>
    private static float RampT(float a, float e, float m)
    {
        if (m <= 0f) return 0f;
        if (a < e) return 0f;
        float upper = (1f / m) + e;
        if (a > upper) return 1f;
        return m * (a - e);
    }

    /// <summary>测试侧单环路一步（u 五式与引擎逐字同序；不含衰减项时即 u 值——AC-11 逐位断言用）。</summary>
    private static (float[] Next, float Gate) ExpectedLoop(float[] prev, float c, float da)
    {
        float mSd1 = 1f + da;
        float mSd2 = 1f - da;
        float oSd1 = RampT(prev[0], 0.2f, mSd1);
        float oSd2 = RampT(prev[1], 0.2f, mSd2);
        float oStn = RampT(prev[2], -0.25f, 1f);
        float oGPe = RampT(prev[3], -0.2f, 1f);

        float uSd1 = 1f * c * (1f + da);
        float uSd2 = 1f * c * (1f - da);
        float uStn = (1f * c) + (-1f * oGPe);
        float uGPe = (0.9f * oStn) + (-1f * oSd2) + (0f * oSd1);
        float uGpi = (0.9f * oStn) + (-0.3f * oGPe) + (-1f * oSd1);

        float decay = MathF.Exp(-25f);
        float[] next =
        [
            uSd1 + ((prev[0] - uSd1) * decay),
            uSd2 + ((prev[1] - uSd2) * decay),
            uStn + ((prev[2] - uStn) * decay),
            uGPe + ((prev[3] - uGPe) * decay),
            uGpi + ((prev[4] - uGpi) * decay),
        ];

        float gate = 1f - RampT(next[4], -0.2f, 1f); // 偏差 B1：O 取更新后 a
        return (next, gate);
    }

    /// <summary>测试侧 u2（无衰减项——AC-11 逐位断言；与引擎 u 五式同序，c=0.5/DA=0.5）。</summary>
    private static float[] ExpectedU2(float[] a1)
    {
        float oSd1 = RampT(a1[0], 0.2f, 1.5f);
        float oSd2 = RampT(a1[1], 0.2f, 0.5f);
        float oStn = RampT(a1[2], -0.25f, 1f);
        float oGPe = RampT(a1[3], -0.2f, 1f);

        return
        [
            1f * 0.5f * (1f + 0.5f),
            1f * 0.5f * (1f - 0.5f),
            (1f * 0.5f) + (-1f * oGPe),
            (0.9f * oStn) + (-1f * oSd2) + (0f * oSd1),
            (0.9f * oStn) + (-0.3f * oGPe) + (-1f * oSd1),
        ];
    }

    /// <summary>每回合镜像对照（引擎 vs 测试侧公式，1e-5；c/da 取引擎 salience 输出）。</summary>
    private static void AssertLoopMatches(GurneyState next, GateState gates, LoopSalience sal, GurneyState prev)
    {
        var (eS, gS) = ExpectedLoop(prev.Somatic, sal.Somatic.C, sal.Somatic.Da);
        var (eC, gC) = ExpectedLoop(prev.Cognitive, sal.Cognitive.C, sal.Cognitive.Da);
        var (eL, gL) = ExpectedLoop(prev.Limbic, sal.Limbic.C, sal.Limbic.Da);
        AssertArrayApprox(eS, next.Somatic, "somatic");
        AssertArrayApprox(eC, next.Cognitive, "cognitive");
        AssertArrayApprox(eL, next.Limbic, "limbic");
        AssertApprox(gS, gates.GateSomatic, "gate_somatic");
        AssertApprox(gC, gates.GateCognitive, "gate_cognitive");
        AssertApprox(gL, gates.GateLimbic, "gate_limbic");
    }

    /// <summary>固定 300 回合迭代 + 每回合镜像对照 + 终态 gate 锚点（spec §六 迭代语义；结转 #1）。</summary>
    private static GurneyState Iterate300(WcState a, ToneState tone, GurneyState prev,
        float gateAnchor, string what)
    {
        var state = prev;
        GateState gates = null!;
        for (int round = 1; round <= 300; round++)
        {
            var (g, gts, sal) = Gating.Value.Step(a, tone, state);
            AssertLoopMatches(g, gts, sal, state);
            state = g;
            gates = gts;
        }

        AssertApprox(gateAnchor, gates.GateSomatic, $"{what} 300 回合 gate_somatic");
        AssertApprox(gateAnchor, gates.GateCognitive, $"{what} 300 回合 gate_cognitive");
        AssertApprox(gateAnchor, gates.GateLimbic, $"{what} 300 回合 gate_limbic");
        return state;
    }

    /// <summary>M1 静息链（csharp-tone spec AC-15）：WMatrixBuilder + CorticalBias + WcDynamics ×30，s=0、a(0)=0.10。</summary>
    private static WcState RestingA()
    {
        var w = WMatrixBuilder.Build(Data.Value);
        var b = CorticalBias.Compute(Baseline(), Data.Value);
        var s = Fill(0f);
        var state = new WcState(Fill(0.10f));
        for (int round = 1; round <= 30; round++)
        {
            state = WcDynamics.Step(state, b, s, w);
        }

        return state;
    }

    // ---- AC-1：CI 成员资格（fid 级，Q3=B）----

    [Fact]
    public void Constructor_CI_Membership_MatchesMeasuredFidLists()
    {
        Assert.Equal(new HashSet<CstcLoop> { CstcLoop.Somatic, CstcLoop.Cognitive, CstcLoop.Limbic },
            Gating.Value.CiRows.Keys.ToHashSet()); // 键集不含 Global/None（C3/D5）

        Assert.True(SomaticCiFids.ToHashSet().SetEquals(FidsOf(CstcLoop.Somatic)),
            "somatic CI fid 集与 §二 2.3 名单不符");
        Assert.True(CognitiveCiFids.ToHashSet().SetEquals(FidsOf(CstcLoop.Cognitive)),
            "cognitive CI fid 集与 §二 2.3 名单不符");
        Assert.True(LimbicCiFids.ToHashSet().SetEquals(FidsOf(CstcLoop.Limbic)),
            "limbic CI fid 集与 §二 2.3 名单不符");

        Assert.Equal(3, Gating.Value.CiRows[CstcLoop.Somatic].Count);
        Assert.Equal(7, Gating.Value.CiRows[CstcLoop.Cognitive].Count);
        Assert.Equal(12, Gating.Value.CiRows[CstcLoop.Limbic].Count);

        // canonical 行下标升序（§二 2.3）
        foreach (var loop in new[] { CstcLoop.Somatic, CstcLoop.Cognitive, CstcLoop.Limbic })
        {
            var rows = Gating.Value.CiRows[loop];
            for (int i = 1; i < rows.Count; i++)
            {
                Assert.True(rows[i - 1] < rows[i], $"{loop} CI 行未升序：{rows[i - 1]} ≥ {rows[i]}");
            }
        }

        // global 0 成员不报错（实测 #4）——构造已成功即验证
    }

    // ---- AC-2：空 CI 环路防御（D4）----

    [Fact]
    public void Constructor_EmptyCILoop_ThrowsInvalidData()
    {
        var data = Data.Value;
        var regions = new Dictionary<string, BrainRegion>();
        foreach (var (fid, region) in data.BrainRegions.Regions)
        {
            regions[fid] = LimbicCiFids.Contains(fid)
                ? region with { FunctionProfile = region.FunctionProfile with { CstcRole = CstcRole.None } }
                : region;
        }

        var modified = new GameData(
            new BrainRegionsData { Regions = regions },
            data.Tripartite, data.Wsensory, data.SituationPrimitives, data.SignalTypes, data.AlphaPatterns);

        var ex = Assert.Throws<InvalidDataException>(() => new CstcGating(modified));
        Assert.Contains("Limbic", ex.Message); // 含环路名（D4）
    }

    // ---- AC-3：Global/None 环路不收集不校验 ----

    [Fact]
    public void Constructor_GlobalAndNoneLoops_NotCollected()
    {
        var data = Data.Value;
        var regions = new Dictionary<string, BrainRegion>();
        foreach (var (fid, region) in data.BrainRegions.Regions)
        {
            regions[fid] = fid switch
            {
                "Paracentral" => region with { FunctionProfile = region.FunctionProfile with { CstcLoop = CstcLoop.Global } },
                "Precentral" => region with { FunctionProfile = region.FunctionProfile with { CstcLoop = CstcLoop.None } },
                _ => region,
            };
        }

        var modified = new GameData(
            new BrainRegionsData { Regions = regions },
            data.Tripartite, data.Wsensory, data.SituationPrimitives, data.SignalTypes, data.AlphaPatterns);

        var gating = new CstcGating(modified); // 构造成功——Global/None 不校验（C3）
        Assert.Equal(new HashSet<CstcLoop> { CstcLoop.Somatic, CstcLoop.Cognitive, CstcLoop.Limbic },
            gating.CiRows.Keys.ToHashSet());
        Assert.True(new[] { "SuperiorFrontal" }.ToHashSet()
            .SetEquals(gating.CiRows[CstcLoop.Somatic]
                .Select(r => data.Wsensory.RegionIds[r]))); // 两个被改 fid 不落入任何环路
        // 输出三字段无 global 分量——类型级断言（LoopSalience 仅 Somatic/Cognitive/Limbic 三字段）
    }

    // ---- AC-4：c=0 门控抑制 ----

    [Fact]
    public void Step_CZero_GateSuppressed_ConvergesToAnchor()
    {
        var a = new WcState(Fill(0f)); // c=0 三环路
        var tone = Baseline(); // c=0 时 DA 不参与 u_SD1/u_SD2（×0 项）

        var (first, firstGates, firstSal) = Gating.Value.Step(a, tone, ZeroGurney());
        // 首回合锚点 [0, 0, −0.2, 0.225, 0.165]、gate=0.635——镜像公式现算（ExpectedLoop）
        AssertLoopMatches(first, firstGates, firstSal, ZeroGurney());

        // 固定 300 回合（spec §六 迭代语义；结转 #1——禁止 max|Δ| 终止判据）
        // 300 回合实测 gate = 0.8434211（1e-5；√0.9≈0.9487/回合收敛，首达 251 回合）
        var final = Iterate300(a, tone, ZeroGurney(), 0.8434211f, "AC-4");

        // gate < 1：门控抑制成立（对比静息 gate=1.0）
        var (_, gates300, _) = Gating.Value.Step(a, tone, final);
        Assert.True(gates300.GateSomatic < 1f && gates300.GateCognitive < 1f && gates300.GateLimbic < 1f,
            $"门控抑制应 gate < 1（实际 s={gates300.GateSomatic} c={gates300.GateCognitive} l={gates300.GateLimbic}）");
    }

    // ---- AC-5：静息 gate = 1.0（M1 链整合）----

    [Fact]
    public void Step_RestingM1Chain_GatesReachOne()
    {
        var rest = RestingA();
        var tone = Baseline();

        var (first, firstGates, _) = Gating.Value.Step(rest, tone, ZeroGurney());
        // 首回合三环路 gate = 0.635（prev=0 → u_GPi=0.165 与 c/DA 无关；镜像现算）
        AssertApprox(1f - RampT(0.165f, -0.2f, 1f), firstGates.GateSomatic, "gate1_somatic");
        AssertApprox(1f - RampT(0.165f, -0.2f, 1f), firstGates.GateCognitive, "gate1_cognitive");
        AssertApprox(1f - RampT(0.165f, -0.2f, 1f), firstGates.GateLimbic, "gate1_limbic");

        var (_, secondGates, _) = Gating.Value.Step(rest, tone, first);
        AssertApprox(1.0f, secondGates.GateSomatic, "gate2_somatic"); // 静息 gate=1.0（M1 实测）
        AssertApprox(1.0f, secondGates.GateCognitive, "gate2_cognitive");
        AssertApprox(1.0f, secondGates.GateLimbic, "gate2_limbic");
    }

    // ---- AC-6：静息 c/DA 锚点（行序正确性锁定）----

    [Fact]
    public void Step_RestingM1Chain_SalienceAnchors()
    {
        var rest = RestingA();
        var (_, _, sal) = Gating.Value.Step(rest, Baseline(), ZeroGurney());

        // C 锚点源 = csharp-tone 工作issue 01 附录 M1 实测值表（C# 实测，2026-08-13 python 验算均值）
        AssertApprox(0.665469f, sal.Somatic.C, "C_somatic");
        AssertApprox(0.696963f, sal.Cognitive.C, "C_cognitive");
        AssertApprox(0.692102f, sal.Limbic.C, "C_limbic");

        // Da 锚点：baseline tone VTA=0.4/SNc=0.5 → 0.48/0.46/0.42（字段序 Somatic/Cognitive/Limbic）
        AssertApprox(0.48f, sal.Somatic.Da, "Da_somatic");
        AssertApprox(0.46f, sal.Cognitive.Da, "Da_cognitive");
        AssertApprox(0.42f, sal.Limbic.Da, "Da_limbic");
    }

    // ---- AC-7：跨环路 fid 归属断言（D13/Q3=B）----

    [Fact]
    public void Step_CrossLoopFids_ContributeToRespectiveLoopsOnly()
    {
        var tone = Baseline();
        var zero = ZeroGurney();

        // caudalanteriorcingulate dk 的 3 fid：AnteriorCingulateCortex(limbic) +
        // AnteriorCingulateCortexDorsal(cognitive) + FrontalPoleSN(limbic)
        var (_, _, sal1) = Gating.Value.Step(
            FidsOn("AnteriorCingulateCortex", "AnteriorCingulateCortexDorsal", "FrontalPoleSN"),
            tone, zero);
        Assert.Equal(0f, sal1.Somatic.C); // 无 fid 双计（每个 fid 恰好贡献一环）
        AssertApprox(1f / 7f, sal1.Cognitive.C, "C_cognitive（1/7）");
        AssertApprox(2f / 12f, sal1.Limbic.C, "C_limbic（2/12）");

        // superiorfrontal dk 的 2 fid：SuperiorFrontal(somatic) + SuperiorFrontalMPFC(limbic)
        var (_, _, sal2) = Gating.Value.Step(
            FidsOn("SuperiorFrontal", "SuperiorFrontalMPFC"), tone, zero);
        AssertApprox(1f / 3f, sal2.Somatic.C, "C_somatic（1/3）");
        Assert.Equal(0f, sal2.Cognitive.C);
        AssertApprox(1f / 12f, sal2.Limbic.C, "C_limbic（1/12）");
    }

    // ---- AC-8：DA 混合逐字段配对（D8）----

    [Fact]
    public void Step_DAMixing_PairedByFieldName()
    {
        var a = new WcState(Fill(0.5f));
        var zero = ZeroGurney();

        // tone(VTA=1, SNc=0) → Da = 0.2/0.4/0.8（Somatic/Cognitive/Limbic 字段序）
        var (_, _, sal1) = Gating.Value.Step(a, ToneOf(1f, 0f), zero);
        AssertApprox((0.2f * 1f) + (0.8f * 0f), sal1.Somatic.Da, "Da_somatic(VTA=1)");
        AssertApprox((0.4f * 1f) + (0.6f * 0f), sal1.Cognitive.Da, "Da_cognitive(VTA=1)");
        AssertApprox((0.8f * 1f) + (0.2f * 0f), sal1.Limbic.Da, "Da_limbic(VTA=1)");

        // tone(VTA=0, SNc=1) → Da = 0.8/0.6/0.2
        var (_, _, sal2) = Gating.Value.Step(a, ToneOf(0f, 1f), zero);
        AssertApprox((0.2f * 0f) + (0.8f * 1f), sal2.Somatic.Da, "Da_somatic(SNc=1)");
        AssertApprox((0.4f * 0f) + (0.6f * 1f), sal2.Cognitive.Da, "Da_cognitive(SNc=1)");
        AssertApprox((0.8f * 0f) + (0.2f * 1f), sal2.Limbic.Da, "Da_limbic(SNc=1)");
    }

    // ---- AC-9：DA=1 → m_SD2=0（偏差 B2 除零防护）----

    [Fact]
    public void Step_DAOne_MSD2Zero_NoDivisionError_GateReachesOne()
    {
        var a = new WcState(Fill(1f)); // c=1 三环路
        var tone = ToneOf(1f, 1f); // DA=1 三环路
        var prevSd2One = new GurneyState([0f, 1f, 0f, 0f, 0f], [0f, 1f, 0f, 0f, 0f], [0f, 1f, 0f, 0f, 0f]);

        var (first, firstGates, firstSal) = Gating.Value.Step(a, tone, prevSd2One);
        // 首回合锚点 [2.0, ≈0, 0.8, 0.225, 0.165] + O1=[1,0,1,0.425,0.365] + gate=0.635——镜像现算
        AssertLoopMatches(first, firstGates, firstSal, prevSd2One);
        // SD2 = e^(−25) ≈ 1.39e-11 ≈ 0（非逐位零——按 1e-5 容差断言，勿与 AC-11 逐位模式混用）
        Assert.True(Math.Abs(first.Somatic[(int)GurneyPopulation.Sd2]) < 1e-5f,
            $"SD2 应 ≈ 0（实际 {first.Somatic[(int)GurneyPopulation.Sd2]}）");
        Assert.True(Math.Abs(first.Cognitive[(int)GurneyPopulation.Sd2]) < 1e-5f, "cognitive SD2 ≈ 0");
        Assert.True(Math.Abs(first.Limbic[(int)GurneyPopulation.Sd2]) < 1e-5f, "limbic SD2 ≈ 0");

        // 第 2 回合即达 gate=1.0（a2_GPi = −0.2275 < e_GPi = −0.2 → O_GPi=0，之后恒真）
        var (_, secondGates, _) = Gating.Value.Step(a, tone, first);
        AssertApprox(1.0f, secondGates.GateSomatic, "gate2_somatic");
        AssertApprox(1.0f, secondGates.GateCognitive, "gate2_cognitive");
        AssertApprox(1.0f, secondGates.GateLimbic, "gate2_limbic");

        // 固定 300 回合 → gate = 1.0（实测；f32 极限环 max|Δ|≈3.9e-7 永不达 1e-7——禁止终止判据，结转 #1）
        Iterate300(a, tone, prevSd2One, 1.0f, "AC-9");
    }

    // ---- AC-10：DA=0 → 对称斜率（m_SD1=m_SD2=1）----

    [Fact]
    public void Step_DAZero_SymmetricSlopes_ConvergesToAnchor()
    {
        var a = new WcState(Fill(1f)); // c=1
        var tone = ToneOf(0f, 0f); // DA=0 三环路

        var (first, firstGates, firstSal) = Gating.Value.Step(a, tone, ZeroGurney());
        // 首回合锚点 [1, 1, 0.8, 0.225, 0.165] + O1=[0.8,0.8,1,0.425,0.365] + gate=0.635——镜像现算
        AssertLoopMatches(first, firstGates, firstSal, ZeroGurney());

        // 固定 300 回合 → gate = 0.8065790（1e-5；首达 253 回合 f64 / 237 f32）
        // 注：DA=0 下 gate 对 c 非单调（极小 0.7771 @ c=0.2）；0.806579 是 c=1（c 域端点）处固定点值、非区间极值
        Iterate300(a, tone, ZeroGurney(), 0.8065790f, "AC-10");
    }

    // ---- AC-11：解析收敛（D9——a2 与 u2 逐位相等）+ B3 残差上界 ----

    [Fact]
    public void Step_AnalyticConvergence_A2BitwiseEqualsU2()
    {
        var a = new WcState(Fill(0.5f)); // c=0.5
        var tone = ToneOf(0.5f, 0.5f); // DA=0.5 三环路（VTA=SNc 时与 wVta 无关）

        var (first, _, firstSal) = Gating.Value.Step(a, tone, ZeroGurney());
        // 首回合锚点 [0.75, 0.25, 0.3, 0.225, 0.165]——镜像现算
        AssertLoopMatches(first, GateStateOf(first), firstSal, ZeroGurney());

        var (second, _, _) = Gating.Value.Step(a, tone, first);
        // 第二步 a2 == u2 逐位（测试侧同公式复算 u2 不含衰减项；锚点 |u| ≥ 0.075 ≥ 0.01 逐位安全域）
        var u2S = ExpectedU2(first.Somatic);
        var u2C = ExpectedU2(first.Cognitive);
        var u2L = ExpectedU2(first.Limbic);
        Assert.Equal(u2S, second.Somatic);
        Assert.Equal(u2C, second.Cognitive);
        Assert.Equal(u2L, second.Limbic);

        // B3 残差上界：|a_new − u| = |a − u|·e^(−25) ≤ 3.5×1.39e-11 ≈ 4.9e-11 ≤ 5e-11
        //（网格复算——数学界验证，double 精度；float32 输出粒度 ~1e-7 不适用于此界，引擎级收敛由逐位断言覆盖）
        double[] grid = [-1.5, -0.4575, 0.0, 0.165, 0.75, 2.0];
        foreach (var p in grid)
        {
            foreach (var u in grid)
            {
                double residual = Math.Abs(p - u) * Math.Exp(-25.0);
                Assert.True(residual <= 5e-11,
                    $"B3 残差上界违反：prev={p}, u={u} → |a−u|·e^(−25) = {residual} > 5e-11");
            }
        }
    }

    /// <summary>由 GurneyState 反推的 GateState（仅供 AC-11 镜像对照——测试侧 RampT 从 first 各环路算 gate）。</summary>
    private static GateState GateStateOf(GurneyState g) => new()
    {
        GateSomatic = 1f - RampT(g.Somatic[(int)GurneyPopulation.GPi], -0.2f, 1f),
        GateCognitive = 1f - RampT(g.Cognitive[(int)GurneyPopulation.GPi], -0.2f, 1f),
        GateLimbic = 1f - RampT(g.Limbic[(int)GurneyPopulation.GPi], -0.2f, 1f),
    };

    // ---- AC-12：无 clamp 负值（D11/Q2=A）+ 值域包含性断言 ----

    [Fact]
    public void Step_NoClamp_NegativeGPiPreserved()
    {
        var a = new WcState(Fill(0.5f));
        var tone = ToneOf(0.5f, 0.5f);
        var (first, _, _) = Gating.Value.Step(a, tone, ZeroGurney());
        var (second, _, _) = Gating.Value.Step(a, tone, first);

        // AC-11 第二步 a_GPi = −0.4575 原样返回（不抬升到 0）——唯一可证伪 clamp[0,1] 违规的断言（结转 #3 哨兵）
        var u2 = ExpectedU2(first.Somatic);
        Assert.True(u2[(int)GurneyPopulation.GPi] < 0f, "u2_GPi 应为负");
        Assert.Equal(u2[(int)GurneyPopulation.GPi], second.Somatic[(int)GurneyPopulation.GPi]);

        // 网格扫描（包含性断言——验证输出落在值域 [−1.5, 2.0] 内、负值合法；
        // 不验证 clamp 有无：e^(−25)≈0 使输出对输入历史不敏感，clamp[−1.5,2.0] 在当前参数下不可观测）
        foreach (var (c, da) in Grid())
        {
            var state = ZeroGurney();
            for (int round = 1; round <= 20; round++)
            {
                var (g, _, _) = Gating.Value.Step(new WcState(Fill(c)), ToneOf(da, da), state);
                AssertInRangeAll(g, -1.5f, 2.0f, $"c={c} da={da} round={round}");
                state = g;
            }
        }
    }

    // ---- AC-15：gate 输出域 [0,1] ----

    [Fact]
    public void Step_GateDomain_WithinZeroOne()
    {
        foreach (var (c, da) in Grid())
        {
            var state = ZeroGurney();
            for (int round = 1; round <= 20; round++)
            {
                var (g, gates, _) = Gating.Value.Step(new WcState(Fill(c)), ToneOf(da, da), state);
                AssertGateDomain(gates, $"c={c} da={da} round={round}");
                state = g;
            }
        }
    }

    private static IEnumerable<(float C, float Da)> Grid()
    {
        foreach (var c in new[] { 0f, 0.3f, 0.5f, 1f })
        {
            foreach (var da in new[] { 0f, 0.5f, 1f })
            {
                yield return (c, da);
            }
        }
    }

    private static void AssertInRangeAll(GurneyState g, float min, float max, string what)
    {
        foreach (var (name, arr) in new[]
                 {
                     ("somatic", g.Somatic), ("cognitive", g.Cognitive), ("limbic", g.Limbic),
                 })
        {
            foreach (var v in arr)
            {
                Assert.True(v >= min && v <= max && !float.IsNaN(v),
                    $"{what} {name} 值 {v} 超出 [{min}, {max}]");
            }
        }
    }

    private static void AssertGateDomain(GateState gates, string what)
    {
        foreach (var (name, v) in new[]
                 {
                     ("gate_somatic", gates.GateSomatic),
                     ("gate_cognitive", gates.GateCognitive),
                     ("gate_limbic", gates.GateLimbic),
                 })
        {
            Assert.True(v >= 0f && v <= 1f && !float.IsNaN(v), $"{what} {name} = {v} 超出 [0,1]");
        }
    }

    // ---- AC-13：输入不可变 + 确定性（C7/C8）----

    [Fact]
    public void Step_ImmutabilityAndDeterminism()
    {
        var aArr = Fill(0.5f);
        var aArrSnapshot = (float[])aArr.Clone();
        var a = new WcState(aArr);
        var tone = Baseline();
        var prev = new GurneyState([0.1f, 0.2f, 0.3f, -0.4f, 0.5f], [0.6f, 0.7f, -0.8f, 0.9f, 1.0f], [1.1f, -1.2f, 1.3f, 1.4f, 0.0f]);
        var prevSomaticSnapshot = (float[])prev.Somatic.Clone();
        var prevCognitiveSnapshot = (float[])prev.Cognitive.Clone();
        var prevLimbicSnapshot = (float[])prev.Limbic.Clone();

        var r1 = Gating.Value.Step(a, tone, prev);
        var r2 = Gating.Value.Step(a, tone, prev);

        // 输入不突变
        Assert.Equal(aArrSnapshot, a.A);
        Assert.Equal(prevSomaticSnapshot, prev.Somatic);
        Assert.Equal(prevCognitiveSnapshot, prev.Cognitive);
        Assert.Equal(prevLimbicSnapshot, prev.Limbic);

        // 输出与输入不共享数组（C7）
        Assert.NotSame(prev.Somatic, r1.Gurney.Somatic);
        Assert.NotSame(prev.Cognitive, r1.Gurney.Cognitive);
        Assert.NotSame(prev.Limbic, r1.Gurney.Limbic);

        // 确定性：两次调用逐位相等
        Assert.Equal(r1.Gurney.Somatic, r2.Gurney.Somatic);
        Assert.Equal(r1.Gurney.Cognitive, r2.Gurney.Cognitive);
        Assert.Equal(r1.Gurney.Limbic, r2.Gurney.Limbic);
        Assert.Equal(r1.Gates, r2.Gates);
        Assert.Equal(r1.Salience, r2.Salience);
    }

    // ---- AC-14：契约防御（D4）----

    [Fact]
    public void Step_ContractDefense_Throws()
    {
        var a = new WcState(Fill(0.5f));
        var tone = Baseline();
        var prev = ZeroGurney();

        Assert.Throws<ArgumentNullException>(() => new CstcGating(null!));
        Assert.Throws<ArgumentNullException>(() => Gating.Value.Step(null!, tone, prev));
        Assert.Throws<ArgumentNullException>(() => Gating.Value.Step(a, null!, prev));
        Assert.Throws<ArgumentNullException>(() => Gating.Value.Step(a, tone, null!));

        foreach (var len in new[] { 0, 68, 70 })
        {
            Assert.Throws<ArgumentException>(() =>
                Gating.Value.Step(new WcState(new float[len]), tone, prev));
        }

        foreach (var len in new[] { 0, 4, 6 })
        {
            Assert.Throws<ArgumentException>(() =>
                Gating.Value.Step(a, tone, new GurneyState(new float[len], Fill5(0f), Fill5(0f))));
            Assert.Throws<ArgumentException>(() =>
                Gating.Value.Step(a, tone, new GurneyState(Fill5(0f), new float[len], Fill5(0f))));
            Assert.Throws<ArgumentException>(() =>
                Gating.Value.Step(a, tone, new GurneyState(Fill5(0f), Fill5(0f), new float[len])));
        }
    }
}
