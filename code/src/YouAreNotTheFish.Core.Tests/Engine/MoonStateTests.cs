using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// MoonState + CalibrationGate + MFieldComposer 测试（Grilling #108 Q9-Q12，测试矩阵 G5/G6/G7）。
/// </summary>
public class MoonStateTests
{
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
            if (File.Exists(Path.Combine(dir, "brain_regions.json"))) return dir;
        throw new DirectoryNotFoundException("Cannot find data/ directory.");
    }

    private static GameData Data() => GameDataLoader.LoadAll(FindDataDir());

    private static CalibrationConfig Cal() => CalibrationConfig.Default;

    // ---- G5 MoonState ----

    [Fact]
    public void Lambda_TableValues()
    {
        // 表值由 λ(D)=(1−cos(2πD/29.5))/2 解析计算（#103 Q4），D=14.75 为连续满月峰值
        Assert.Equal(0.0, MoonState.Lambda(0), 1e-9);          // D=0 新月
        Assert.Equal(0.9936, MoonState.Lambda(14), 1e-4);      // D=14 离散近满月
        Assert.Equal(0.4601, MoonState.Lambda(7), 1e-4);       // D=7 上弦前
        Assert.Equal(0.5133, MoonState.Lambda(22), 1e-4);      // D=22 下弦后
        Assert.Equal(0.0028, MoonState.Lambda(29), 1e-4);      // D=29 近新月
        // 周期闭合：λ(D+29.5)=λ(D)（连续）；离散整数 D 上 λ(29.5·k)≈0
        Assert.Equal(MoonState.Lambda(0), MoonState.Lambda(29), 1e-2);
    }

    [Fact]
    public void Query_ReturnsContractShape()
    {
        var data = Data();
        var r = MoonState.Query(7, data.MoonlightLanding, Cal());
        Assert.InRange(r.Phase, 0f, 1f);
        Assert.True(r.Shell.EC > 0.0);
        Assert.True(r.Shell.ETh > 0.0 && r.Shell.ETh < r.Shell.EC);
        Assert.Equal(69, r.QhatBaseline.Length);
        Assert.Equal("PLACEHOLDER", r.CalibrationStatus);
        Assert.Equal(0, r.Version);
    }

    [Fact]
    public void Query_PureFunction_SameInputSameOutput()
    {
        var data = Data();
        var a = MoonState.Query(10, data.MoonlightLanding, Cal());
        var b = MoonState.Query(10, data.MoonlightLanding, Cal());
        Assert.Equal(a.Phase, b.Phase);
        Assert.Equal(a.Shell, b.Shell);
        Assert.Equal(a.QhatBaseline, b.QhatBaseline);
    }

    [Fact]
    public void Query_NegativeDay_Throws()
    {
        var data = Data();
        Assert.Throws<ArgumentOutOfRangeException>(() => MoonState.Query(-1, data.MoonlightLanding, Cal()));
    }

    // ---- G6 CalibrationGate ----

    [Fact]
    public void Gate_Placeholder_FailsWithoutDemo()
    {
        var data = Data(); // calibration_status=PLACEHOLDER
        var ex = Assert.Throws<InvalidDataException>(
            () => CalibrationGate.EnsureCalibrated(data.MoonlightLanding, Cal()));
        Assert.Contains("PLACEHOLDER", ex.Message);
    }

    [Fact]
    public void Gate_Placeholder_PassesWithDemoFlag()
    {
        var data = Data();
        var cal = Cal() with { AllowPlaceholderDemo = true };
        CalibrationGate.EnsureCalibrated(data.MoonlightLanding, cal); // 不抛
    }

    [Fact]
    public void Gate_VersionMismatch_Fails()
    {
        var data = Data();
        var cal = Cal() with { ExpectedCalibrationVersion = 99 };
        Assert.Throws<InvalidDataException>(
            () => CalibrationGate.EnsureCalibrated(data.MoonlightLanding, cal));
    }

    // ---- G7 MFieldComposer 三通道合成 ----

    [Fact]
    public void Composer_PlaceholderWithoutDemo_Throws()
    {
        var data = Data();
        var moon = MoonState.Query(0, data.MoonlightLanding, Cal());
        // 默认（非 demo）：PLACEHOLDER → 门禁拦截
        Assert.Throws<InvalidDataException>(() => MFieldComposer.Compute(
            data.MoonlightLanding, moon, data.Wsensory, 80f, Cal()));
    }

    [Fact]
    public void Composer_Demo_InjectsOnLandingNodes()
    {
        var data = Data();
        var cal = Cal() with { AllowPlaceholderDemo = true };
        var moon = MoonState.Query(0, data.MoonlightLanding, cal);
        var m = MFieldComposer.Compute(data.MoonlightLanding, moon, data.Wsensory, 80f, cal);
        Assert.Equal(69, m.Length);
        // 12 落点 fid 应非零（Amygdala/HippocampusCA1/...），非落点应为 0
        var fidIdx = data.Wsensory.RegionIds.Select((fid, i) => (fid, i)).ToDictionary(x => x.fid, x => x.i);
        Assert.True(m[fidIdx["Amygdala"]] > 0f);
        Assert.True(m[fidIdx["HippocampusCA1"]] > 0f);
        Assert.True(m[fidIdx["TemporalPole"]] > 0f);
        // 非落点（如 Precentral）应为 0
        Assert.Equal(0f, m[fidIdx["Precentral"]]);
        // 主辅权重：r=PLACEHOLDER → 按 r=1 均匀（主 1/12、辅 1/12）
        Assert.Equal(1f / 12f, m[fidIdx["Amygdala"]], 3); // 主落点
        Assert.Equal(1f / 12f, m[fidIdx["TemporalPole"]], 3); // 辅落点
    }

    // ---- G7 三通道合成时序（s_env 更新）----

    [Fact]
    public void SEnv_ComputedFromEnvironmentAndArchetype()
    {
        var data = Data();
        var sEnv = SituationEnv.Compute(
            data.Wsensory, data.EnvTones, data.SituationPrimitives,
            "ward", "investigation_search", 1.0f);
        Assert.Equal(69, sEnv.Length);
        // 环境基调：ward α_env=[0.3,0.2,0.2,0,0.1,0,0.4,0.2] × W_sensory
        // 原型注入：investigation_search key_brain_regions +1.0
        var fidIdx = data.Wsensory.RegionIds.Select((fid, i) => (fid, i)).ToDictionary(x => x.fid, x => x.i);
        // investigation_search 的 key_brain_regions 之一（查数据推导）非零
        var archetype = data.SituationPrimitives.Archetypes.First(a => a.Name == "investigation_search");
        Assert.NotEmpty(archetype.KeyBrainRegions);
        foreach (var fid in archetype.KeyBrainRegions)
            Assert.True(sEnv[fidIdx[fid]] >= 1.0f, $"{fid} 应有原型注入");
    }
}
