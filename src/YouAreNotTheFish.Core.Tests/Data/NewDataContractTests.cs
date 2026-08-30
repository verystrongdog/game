using System.Text.Json;
using YouAreNotTheFish.Core.Data;

namespace YouAreNotTheFish.Core.Tests.Data;

/// <summary>
/// #105 新增数据文件契约 fail-fast 测试（Grilling #108 Q1/Q3/Q9，测试矩阵 G1）。
/// 复用 Loader_BadJsonThrowsJsonException 临时文件模式。
/// </summary>
public class AlphaPatternsContractTests
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

    private static string AlphaPatternsJson() =>
        Path.Combine(FindDataDir(), "connectivity", "alpha_patterns.json");

    // ---- G1：alpha_patterns 契约 ----

    [Fact]
    public void AlphaPatterns_Loads_14Events_8Modalities()
    {
        var ap = GameDataLoader.LoadAlphaPatterns(AlphaPatternsJson());
        Assert.Equal(14, ap.Events.Count);
        Assert.Equal(8, ap.Modalities.Length);
        // 消费 10 行存在（加载器已校验）；A3/A6/A7 保留不消费
        Assert.True(ap.Events.ContainsKey("A3"));
        Assert.True(ap.Events.ContainsKey("A6"));
        Assert.True(ap.Events.ContainsKey("A7"));
    }

    [Fact]
    public void AlphaPatterns_MissingConsumedRow_ThrowsJson()
    {
        var tmp = Path.GetTempFileName();
        var baseData = File.ReadAllText(AlphaPatternsJson());
        var doc = JsonDocument.Parse(baseData).RootElement.Clone();
        using var stream = new MemoryStream();
        using (var w = new Utf8JsonWriter(stream))
        {
            w.WriteStartObject();
            foreach (var prop in doc.EnumerateObject())
            {
                if (prop.Name == "events")
                {
                    w.WritePropertyName("events");
                    w.WriteStartObject();
                    foreach (var ev in prop.Value.EnumerateObject())
                        if (ev.Name != "A1") ev.WriteTo(w); // 删除消费行 A1
                    w.WriteEndObject();
                }
                else
                {
                    prop.WriteTo(w);
                }
            }
            w.WriteEndObject();
        }
        File.WriteAllText(tmp, System.Text.Encoding.UTF8.GetString(stream.ToArray()));
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadAlphaPatterns(tmp));
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    [Fact]
    public void AlphaPatterns_BadMAlphaString_ThrowsJson()
    {
        var tmp = Path.GetTempFileName();
        var text = File.ReadAllText(AlphaPatternsJson())
            .Replace("\"m_alpha\": 1.0", "\"m_alpha\": \"bogus\"", StringComparison.Ordinal);
        File.WriteAllText(tmp, text);
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadAlphaPatterns(tmp));
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    [Fact]
    public void AlphaPatterns_PatternLengthNot8_ThrowsJson()
    {
        var tmp = Path.GetTempFileName();
        var text = File.ReadAllText(AlphaPatternsJson())
            .Replace("[1, 0, 1, 0, 0, 0, 0, 0]", "[1, 0, 1, 0, 0, 0]", StringComparison.Ordinal);
        File.WriteAllText(tmp, text);
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadAlphaPatterns(tmp));
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    [Fact]
    public void AlphaPatterns_MAlphaOutOfRange_ThrowsJson()
    {
        var tmp = Path.GetTempFileName();
        var text = File.ReadAllText(AlphaPatternsJson())
            .Replace("\"m_alpha\": 1.0", "\"m_alpha\": 7.0", StringComparison.Ordinal);
        File.WriteAllText(tmp, text);
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadAlphaPatterns(tmp));
        }
        finally
        {
            File.Delete(tmp);
        }
    }
}

/// <summary>env_tones 契约测试（G1，Q3/Q5）。</summary>
public class EnvTonesContractTests
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

    private static string EnvTonesJson() =>
        Path.Combine(FindDataDir(), "connectivity", "env_tones.json");

    [Fact]
    public void EnvTones_Loads_3DemoEnvironments()
    {
        var env = GameDataLoader.LoadEnvTones(EnvTonesJson());
        Assert.Equal(3, env.Environments.Count);
        Assert.True(env.Environments.ContainsKey("ward"));
        Assert.True(env.Environments.ContainsKey("corridor"));
        Assert.True(env.Environments.ContainsKey("nurse_station"));
        foreach (var (id, e) in env.Environments)
        {
            Assert.False(string.IsNullOrEmpty(e.DisplayName));
            Assert.Equal(8, e.AlphaEnv.Length);
            Assert.False(string.IsNullOrEmpty(e.Situation.Primary));
        }
    }

    [Fact]
    public void EnvTones_NoAlternatesField_BySchema()
    {
        // alternates 字段已删除（Q5）——反序列化不消费该字段（无锁定消费者语义）
        var text = File.ReadAllText(EnvTonesJson());
        Assert.DoesNotContain("alternates", text);
    }

    [Fact]
    public void EnvTones_AlphaEnvWrongLength_ThrowsJson()
    {
        var tmp = Path.GetTempFileName();
        var text = File.ReadAllText(EnvTonesJson())
            .Replace("[0.3, 0.2, 0.2, 0.0, 0.1, 0.0, 0.4, 0.2]", "[0.3, 0.2, 0.2]", StringComparison.Ordinal);
        File.WriteAllText(tmp, text);
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadEnvTones(tmp));
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    [Fact]
    public void EnvTones_AlphaEnvOutOfRange_ThrowsJson()
    {
        var tmp = Path.GetTempFileName();
        var text = File.ReadAllText(EnvTonesJson())
            .Replace("[0.3, 0.2, 0.2, 0.0, 0.1, 0.0, 0.4, 0.2]", "[3.0, 0.2, 0.2, 0.0, 0.1, 0.0, 0.4, 0.2]", StringComparison.Ordinal);
        File.WriteAllText(tmp, text);
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadEnvTones(tmp));
        }
        finally
        {
            File.Delete(tmp);
        }
    }
}

/// <summary>moonlight_landing 契约测试（G1，Q9 四项校验）。</summary>
public class MoonlightLandingContractTests
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

    private static string MoonlightJson() =>
        Path.Combine(FindDataDir(), "connectivity", "moonlight_landing.json");

    private static BrainRegionsData Brain() =>
        GameDataLoader.LoadBrainRegions(Path.Combine(FindDataDir(), "brain_regions.json"));

    private static TripartiteModel Tri() =>
        GameDataLoader.LoadTripartiteModel(Path.Combine(FindDataDir(), "connectivity", "tripartite_model.json"));

    [Fact]
    public void Moonlight_Loads_12LandingPoints_PLACEHOLDER()
    {
        var ml = GameDataLoader.LoadMoonlightLanding(MoonlightJson(), Brain(), Tri());
        Assert.Equal(1, ml.Semantics.Count);
        var sem = ml.Semantics[0];
        Assert.Equal(4, sem.Primary.Length);
        Assert.Equal(8, sem.Secondary.Length);
        Assert.Equal("PLACEHOLDER", sem.R);
        Assert.Equal("PLACEHOLDER", sem.AlphaS);
        Assert.Equal("PLACEHOLDER", ml.CalibrationStatus);
        Assert.Equal(0, ml.CalibrationVersion);
    }

    [Fact]
    public void Moonlight_FieldMissing_ThrowsJson()
    {
        var tmp = Path.GetTempFileName();
        var text = File.ReadAllText(MoonlightJson())
            .Replace("\"r\": \"PLACEHOLDER\",", "", StringComparison.Ordinal);
        File.WriteAllText(tmp, text);
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadMoonlightLanding(tmp, Brain(), Tri()));
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    [Fact]
    public void Moonlight_SuppNotInWActive_ThrowsJson()
    {
        var tmp = Path.GetTempFileName();
        var text = File.ReadAllText(MoonlightJson())
            .Replace("\"Amygdala\", \"HippocampusCA1\"", "\"Precentral\", \"HippocampusCA1\"", StringComparison.Ordinal);
        File.WriteAllText(tmp, text);
        try
        {
            // Precentral → dk precentral ∈ W_active？实测 precentral 是 CSTC 端点 → 在集内。
            // 用不在 48 端点的 fid 更稳：LocusCoeruleusRight（无边节点）
            var text2 = File.ReadAllText(MoonlightJson())
                .Replace("\"Amygdala\"", "\"LocusCoeruleusRight\"", StringComparison.Ordinal);
            File.WriteAllText(tmp, text2);
            Assert.Throws<JsonException>(() => GameDataLoader.LoadMoonlightLanding(tmp, Brain(), Tri()));
        }
        finally
        {
            File.Delete(tmp);
        }
    }

    [Fact]
    public void Moonlight_SuppOverlap_ThrowsJson()
    {
        var tmp = Path.GetTempFileName();
        var text = File.ReadAllText(MoonlightJson())
            .Replace("\"Amygdala\", \"HippocampusCA1\", \"HippocampusCA3\", \"Parahippocampal\"",
                "\"Amygdala\", \"HippocampusCA1\", \"HippocampusCA3\", \"Amygdala\"", StringComparison.Ordinal);
        File.WriteAllText(tmp, text);
        try
        {
            Assert.Throws<JsonException>(() => GameDataLoader.LoadMoonlightLanding(tmp, Brain(), Tri()));
        }
        finally
        {
            File.Delete(tmp);
        }
    }
}
