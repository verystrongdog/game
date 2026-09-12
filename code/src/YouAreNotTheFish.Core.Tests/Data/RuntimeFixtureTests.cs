using System.Text.Json;
using System.Text.Json.Serialization;
using YouAreNotTheFish.Core.Data;

namespace YouAreNotTheFish.Core.Tests.Data;

/// <summary>
/// 跨语言 fixture runner（P4c）：对 <c>data/runtime-fixtures/</c> 的每一条 fixture
/// 调用**真实加载器**，比对 <c>index.json</c> 声明的 expect。
///
/// 对应 Python 侧 runner: <c>code/tools/validate_runtime_fixtures.py</c>。
/// 两侧必须给出**逐条相同**的接受/拒绝判定——这正是 owner 方案 §9.3 的判据
/// 「Python/C# 共用合法与非法 fixture，跨语言接受/拒绝集合一致」。
///
/// 分工（详见 Python runner 的文件头）：
/// - 本 runner 走**引擎加载器**，覆盖结构 + 跨文件语义（如 moonlight 的 supp ⊆ W_active）
/// - Python runner 走**规则表**，覆盖结构规则
/// - 两者的结构部分必须一致；语义部分是 C# 独有的**加强**，不是分叉
/// </summary>
public class RuntimeFixtureTests
{
    private static string FindRepoRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir is not null && !Directory.Exists(Path.Combine(dir.FullName, "data")))
            dir = dir.Parent;
        if (dir is null) throw new DirectoryNotFoundException("Cannot find repo root (data/).");
        return dir.FullName;
    }

    private static readonly string Root = FindRepoRoot();
    private static string FixtureDir => Path.Combine(Root, "data", "runtime-fixtures");

    private sealed record FixtureCase(string File, string Case, string LogicalId,
                                      string Expect, string? Rule, List<string> DependsOn);

    private static List<FixtureCase> Cases()
    {
        var text = File.ReadAllText(Path.Combine(FixtureDir, "index.json"));
        using var doc = JsonDocument.Parse(text);
        var list = new List<FixtureCase>();
        foreach (var e in doc.RootElement.GetProperty("cases").EnumerateArray())
        {
            var deps = new List<string>();
            if (e.TryGetProperty("depends_on", out var d))
                foreach (var x in d.EnumerateArray()) deps.Add(x.GetString()!);
            list.Add(new FixtureCase(
                e.GetProperty("file").GetString()!,
                e.GetProperty("case").GetString()!,
                e.GetProperty("logical_id").GetString()!,
                e.GetProperty("expect").GetString()!,
                e.TryGetProperty("rule", out var r) && r.ValueKind == JsonValueKind.String
                    ? r.GetString() : null,
                deps));
        }
        return list;
    }

    /// <summary>
    /// 用真实加载器判定一条 fixture 是否被接受。
    /// 依赖文件（moonlight → brain_regions + tripartite_model）从**仓库实测路径**取，
    /// 不复制进 fixture 目录——契约校验的是"这条数据能否被引擎加载"，
    /// 而跨文件语义依赖真实数据闭包。
    /// </summary>
    private static bool Accepts(string logicalId, string path, out string detail)
    {
        try
        {
            var dataDir = Path.Combine(Root, "data");
            switch (logicalId)
            {
                case "brain_regions":
                    GameDataLoader.LoadBrainRegions(path);
                    break;
                case "signal_types":
                    GameDataLoader.LoadSignalTypes(path);
                    break;
                case "tripartite_model":
                    GameDataLoader.LoadTripartiteModel(path);
                    break;
                case "W_sensory":
                    GameDataLoader.LoadWsensory(path);
                    break;
                case "situation_primitives":
                    GameDataLoader.LoadSituationPrimitives(path);
                    break;
                case "alpha_patterns":
                    GameDataLoader.LoadAlphaPatterns(path);
                    break;
                case "env_tones":
                    GameDataLoader.LoadEnvTones(path);
                    break;
                case "moonlight_landing":
                    GameDataLoader.LoadMoonlightLanding(
                        path,
                        GameDataLoader.LoadBrainRegions(Path.Combine(dataDir, "brain_regions.json")),
                        GameDataLoader.LoadTripartiteModel(
                            Path.Combine(dataDir, "connectivity", "tripartite_model.json")));
                    break;
                default:
                    throw new InvalidOperationException($"未知 logical_id: {logicalId}");
            }
            detail = "";
            return true;
        }
        catch (JsonException ex)
        {
            detail = ex.Message;
            return false;
        }
        catch (InvalidOperationException ex)
        {
            detail = ex.Message;
            return false;
        }
    }

    public static TheoryData<string> AllFixtures()
    {
        var data = new TheoryData<string>();
        foreach (var c in Cases()) data.Add(c.File);
        return data;
    }

    private static FixtureCase CaseOf(string file) =>
        Cases().Single(c => c.File == file);

    /// <summary>
    /// 逐条 fixture 判定：expect=accept → 加载器必须成功；expect=reject → 必须抛。
    /// 失败消息里带上 rule id 与 mutation 说明，便于与 Python 侧归因对齐。
    /// </summary>
    [Theory]
    [MemberData(nameof(AllFixtures))]
    public void Fixture_JudgeMatchesExpectation(string file)
    {
        var c = CaseOf(file);
        var path = Path.Combine(Root, file);
        Assert.True(File.Exists(path), $"fixture 文件缺失: {file}");

        var accepted = Accepts(c.LogicalId, path, out var detail);
        var want = c.Expect == "accept";

        Assert.True(accepted == want,
            $"{file}\n  logical_id={c.LogicalId} case={c.Case} rule={c.Rule}\n" +
            $"  期望 {(want ? "接受" : "拒绝")}，实得 {(accepted ? "接受" : "拒绝")}\n" +
            $"  加载器消息: {detail}");
    }

    /// <summary>
    /// 每条的 fixture 集合必须**至少各有一条 accept 与一条 reject**——
    /// 只有 reject 的集合无法发现"合法数据被误拒"，只有 accept 的集合没有约束力。
    /// </summary>
    [Fact]
    public void EveryFile_HasBothAcceptAndRejectCases()
    {
        var groups = Cases().GroupBy(c => c.LogicalId);
        Assert.Equal(8, groups.Count());
        foreach (var g in groups)
        {
            Assert.Contains(g, c => c.Expect == "accept");
            Assert.Contains(g, c => c.Expect == "reject");
        }
    }

    /// <summary>真实数据文件必须全部被接受（契约不得比现实更严）。</summary>
    [Theory]
    [InlineData("brain_regions", "data/brain_regions.json")]
    [InlineData("signal_types", "data/signal_types.json")]
    [InlineData("tripartite_model", "data/connectivity/tripartite_model.json")]
    [InlineData("W_sensory", "data/connectivity/W_sensory.json")]
    [InlineData("situation_primitives", "data/connectivity/situation_primitives.json")]
    [InlineData("alpha_patterns", "data/connectivity/alpha_patterns.json")]
    [InlineData("env_tones", "data/connectivity/env_tones.json")]
    [InlineData("moonlight_landing", "data/connectivity/moonlight_landing.json")]
    public void RealData_IsAccepted(string logicalId, string rel)
    {
        var accepted = Accepts(logicalId, Path.Combine(Root, rel), out var detail);
        Assert.True(accepted, $"{rel} 被契约拒绝: {detail}");
    }

    /// <summary>
    /// 导出 C# 的逐条判定，供 <c>code/tools/compare_fixture_verdicts.py</c> 与 Python 侧
    /// 判定**逐条比对**。
    ///
    /// 为何需要它：「两侧共用 fixture」本身不能证明「跨语言接受/拒绝集合一致」——
    /// 只有当两侧的判定结果被发现**逐条相同**时，那条判据才成立。
    /// 导出路径由环境变量 `DSH_FIXTURE_VERDICTS` 给出；未设置时本测试只做自检不落盘
    /// （默认跑测试不应污染工作树）。
    /// </summary>
    [Fact]
    public void ExportVerdicts_ForCrossLanguageComparison()
    {
        var target = Environment.GetEnvironmentVariable("DSH_FIXTURE_VERDICTS");
        var verdicts = new List<object>();
        foreach (var c in Cases())
        {
            var accepted = Accepts(c.LogicalId, Path.Combine(Root, c.File), out var detail);
            verdicts.Add(new
            {
                file = c.File,
                logical_id = c.LogicalId,
                @case = c.Case,
                expect = c.Expect,
                accepted,
                detail,
            });
        }
        var json = JsonSerializer.Serialize(
            new { _source = "csharp", count = verdicts.Count, verdicts },
            new JsonSerializerOptions { WriteIndented = true });

        if (string.IsNullOrEmpty(target))
        {
            // 未指定导出路径：只断言判定与 expect 一致（本测试自身也是一道门禁）
            foreach (var c in Cases())
            {
                var accepted = Accepts(c.LogicalId, Path.Combine(Root, c.File), out _);
                Assert.Equal(c.Expect == "accept", accepted);
            }
            return;
        }
        File.WriteAllText(target, json);
    }
}
