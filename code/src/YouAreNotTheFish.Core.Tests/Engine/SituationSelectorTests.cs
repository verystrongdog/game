using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// SituationSelector 测试（Grilling #108 Q4-Q8，测试矩阵 G4）。
/// 契约断言（Q15）：恐慌假 → 必 primary；恐慌真 → 必 ∈ {G ∪ primary}；同 seed 同输入 → 同选择。
/// G=17 构造断言（Q6 实测值）。
/// </summary>
public class SituationSelectorTests
{
    private static readonly string[] DataDirCandidates =
    [
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", "..", "data"),
        Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
            "..", "..", "..", "..", "..", "..", "..", "data")),
    ];

    private static string FindDataDir()
    {
        foreach (var dir in DataDirCandidates)
            if (File.Exists(Path.Combine(dir, "brain_regions.json"))) return dir;
        throw new DirectoryNotFoundException("Cannot find data/ directory.");
    }

    private static GameData Data() => GameDataLoader.LoadAll(FindDataDir());

    private static SituationSelector Selector() => new(
        Data().EnvTones, Data().SituationPrimitives, Data().BrainRegions.Regions.Keys, CalibrationConfig.Default);

    // ---- G 组构造断言（Q6：实测 17 成员）----

    [Fact]
    public void GGroup_Construction_17Members()
    {
        var sel = Selector();
        Assert.Equal(17, sel.GGroup.Count);
        // G 成员全为 negative_valence ≥ 0.2 ∧ valence=negative
        var primitives = Data().SituationPrimitives;
        var expect = primitives.Archetypes
            .Where(a => a.RdocProfile.NegativeValence is { } nv && nv >= CalibrationConfig.Default.TNeg
                        && string.Equals(a.AppraisalProfile.Valence, "negative", StringComparison.Ordinal))
            .Select(a => a.Name)
            .OrderBy(x => x)
            .ToArray();
        Assert.Equal(expect, sel.GGroup.OrderBy(x => x).ToArray());
    }

    // ---- Q5 候选池 + Q4 确定性 primary ----

    [Fact]
    public void Select_NoPanic_DeterministicPrimary()
    {
        var sel = Selector();
        var rng1 = new DeterministicRng(42);
        var rng2 = new DeterministicRng(42);
        var a = sel.Select("ward", false, rng1);
        var b = sel.Select("ward", false, rng2);
        Assert.Equal("investigation_search", a.ArchetypeId); // ward.primary（env_tones.json）
        Assert.Equal(a, b);
        Assert.Equal(1.0f, a.Strength); // Q7 恐慌假 strength=1.0
    }

    [Fact]
    public void Select_NoPanic_EachEnvironmentPrimary()
    {
        var sel = Selector();
        var data = Data();
        foreach (var (id, env) in data.EnvTones.Environments)
        {
            var r = sel.Select(id, false, new DeterministicRng(1));
            Assert.Equal(env.Situation.Primary, r.ArchetypeId);
        }
    }

    // ---- Q6 恐慌概率路径（契约断言，非频率统计）----

    [Fact]
    public void Select_Panic_AlwaysInGOrPrimary()
    {
        var sel = Selector();
        var g = sel.GGroup.ToHashSet();
        var data = Data();
        // 多 seed 扫描：恐慌真 → 必 ∈ {G ∪ primary}
        for (ulong seed = 0; seed < 50; seed++)
        {
            foreach (var (id, env) in data.EnvTones.Environments)
            {
                var r = sel.Select(id, true, new DeterministicRng(seed));
                Assert.True(g.Contains(r.ArchetypeId) || r.ArchetypeId == env.Situation.Primary,
                    $"seed={seed} env={id} 选择 {r.ArchetypeId} ∉ G∪{{primary}}");
                Assert.InRange(r.Strength, 1.0f, 1.5f); // Q7 恐慌真 strength=s_neg ∈ [1,1.5]
            }
        }
    }

    [Fact]
    public void Select_Panic_SameSeedSameChoice()
    {
        var sel = Selector();
        var rng1 = new DeterministicRng(7);
        var rng2 = new DeterministicRng(7);
        var a = sel.Select("corridor", true, rng1);
        var b = sel.Select("corridor", true, rng2);
        Assert.Equal(a, b);
    }

    // ---- Q3 非法环境 fail-fast ----

    [Fact]
    public void Select_UnknownEnvironment_Throws()
    {
        var sel = Selector();
        Assert.Throws<KeyNotFoundException>(() => sel.Select("nonexistent_room", false, new DeterministicRng(1)));
    }

    // ---- Q13 第二层防线：引擎侧 fid 断言 ----

    [Fact]
    public void Ctor_UnknownFid_ThrowsInvalidData()
    {
        var data = Data();
        // 注入一个伪造原型（key_brain_regions 含未知 fid）→ 构造抛 InvalidDataException
        var bogus = new SituationPrimitives
        {
            Archetypes =
            [
                new SituationArchetype
                {
                    Name = "bogus_archetype",
                    KeyBrainRegions = ["NotARealFid"],
                },
            ],
        };
        Assert.Throws<InvalidDataException>(() => new SituationSelector(
            data.EnvTones, bogus, data.BrainRegions.Regions.Keys, CalibrationConfig.Default));
    }
}
