using YouAreNotTheFish.Core.Data;

namespace YouAreNotTheFish.Core.Tests.Data;

/// <summary>AC-7（LoadAll 5 文件加载，结果与 5 个单文件方法一致）。</summary>
public class GameDataLoadAllTests
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
        {
            if (File.Exists(Path.Combine(dir, "brain_regions.json"))) return dir;
        }

        throw new DirectoryNotFoundException(
            "Cannot find data/ directory. Tried:\n" + string.Join("\n", DataDirCandidates));
    }

    [Fact]
    public void LoadAll_LoadsAllFiveFiles()
    {
        // AC-7: 一次加载 5 文件，逐字段与单文件加载结果一致
        var dataDir = FindDataDir();
        var all = GameDataLoader.LoadAll(dataDir);

        Assert.NotNull(all.BrainRegions);
        Assert.NotNull(all.Tripartite);
        Assert.NotNull(all.Wsensory);
        Assert.NotNull(all.SituationPrimitives);
        Assert.NotNull(all.SignalTypes);
    }

    [Fact]
    public void LoadAll_MatchesIndividualLoads()
    {
        // AC-7 续: 关键结构属性与 5 个单文件方法一致
        var dataDir = FindDataDir();
        var all = GameDataLoader.LoadAll(dataDir);

        var regions = GameDataLoader.LoadBrainRegions(Path.Combine(dataDir, "brain_regions.json"));
        Assert.Equal(regions.Regions.Count, all.BrainRegions.Regions.Count);

        var tri = GameDataLoader.LoadTripartiteModel(Path.Combine(dataDir, "connectivity", "tripartite_model.json"));
        Assert.Equal(tri.GraphNodes.Count, all.Tripartite.GraphNodes.Count);

        var ws = GameDataLoader.LoadWsensory(Path.Combine(dataDir, "connectivity", "W_sensory.json"));
        Assert.Equal(ws.RegionIds, all.Wsensory.RegionIds);

        var situations = GameDataLoader.LoadSituationPrimitives(Path.Combine(dataDir, "connectivity", "situation_primitives.json"));
        Assert.Equal(situations.Archetypes.Count, all.SituationPrimitives.Archetypes.Count);

        var signalTypes = GameDataLoader.LoadSignalTypes(Path.Combine(dataDir, "signal_types.json"));
        Assert.Equal(signalTypes.Categories.Count, all.SignalTypes.Categories.Count);
    }

    [Fact]
    public void LoadAll_WsensoryRegionIds_IsCanonical69()
    {
        // 约束 C1 / AC-10 的 canonical 行序源（step 3 承接验证的基础）
        var all = GameDataLoader.LoadAll(FindDataDir());
        Assert.Equal(69, all.Wsensory.RegionIds.Length);
        Assert.Equal(69, all.Wsensory.RegionIds.Distinct().Count());
    }
}
