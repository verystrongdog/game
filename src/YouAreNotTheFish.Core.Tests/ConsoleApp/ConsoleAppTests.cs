using System.Text.RegularExpressions;
using YouAreNotTheFish.ConsoleApp;
using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Flow;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.ConsoleApp;

/// <summary>
/// csharp-console spec@v1.2 §六 AC-1~13。
/// 锚点来源：M1 实测（静息区间）+ 组件级已验证 + 渲染格式断言（spec §3.2 九段）。
/// </summary>
public class ConsoleAppTests
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

    private static CombatState State2P() => CombatState.Create(
        new[] { ParticipantState.CreateDefault(50f, 80f), ParticipantState.CreateDefault(15f, 60f) },
        new[] { 1, 2 }, Data(), CalibrationConfig.Default);

    // ---- AC-1：CliArgs 解析 ----

    [Fact]
    public void CliArgs_Valid()
    {
        Assert.Equal(new CliArgs(7, null), CliArgs.Parse(["--seed", "7"]));
        Assert.Equal(new CliArgs(7, 30), CliArgs.Parse(["--seed", "7", "--trace-resting", "30"]));
        Assert.Equal(new CliArgs(42, null), CliArgs.Parse([]));
        // 重复参数后者覆盖
        Assert.Equal(new CliArgs(2, null), CliArgs.Parse(["--seed", "1", "--seed", "2"]));
    }

    [Theory]
    [InlineData("--seed")]
    [InlineData("--seed abc")]
    [InlineData("--seed -1")]
    [InlineData("--trace-resting")]
    [InlineData("--trace-resting abc")]
    [InlineData("--trace-resting -5")]
    [InlineData("--trace-resting 0")]
    [InlineData("--unknown")]
    public void CliArgs_Invalid_Throws(string argLine)
    {
        Assert.Throws<CliUsageException>(() => CliArgs.Parse(argLine.Split(' ')));
    }

    // ---- AC-2：PlayerActionProvider 输入映射 ----

    [Theory]
    [InlineData("1\n", ActionKind.PhysicalAttack, true, false)]
    [InlineData("2\n", ActionKind.MentalAttack, false, true)]
    [InlineData("3\n", ActionKind.Defend, true, false)]
    [InlineData("0\n", null, false, false)]
    public void PlayerProvider_InputMapping(string input, ActionKind? m1Kind, bool hasM1, bool hasBroca)
    {
        var state = State2P();
        var provider = new PlayerActionProvider(new StringReader(input), new StringWriter());
        var action = provider.GetAction(0, state, Ctx());

        Assert.Equal(hasM1, action.M1 is not null);
        Assert.Equal(hasBroca, action.Broca is not null);
        if (hasM1) Assert.Equal(m1Kind, action.M1!.Kind);
        if (hasBroca) Assert.Equal(ActionKind.MentalAttack, action.Broca!.Kind);
        // 目标 = 对方（p1）（空声明无目标）
        var target = action.M1?.TargetId ?? action.Broca?.TargetId;
        if (target is not null)
            Assert.Equal(1, target);
    }

    [Fact]
    public void PlayerProvider_InvalidRetry_ThenValid()
    {
        var provider = new PlayerActionProvider(new StringReader("x\n2\n"), new StringWriter());
        var action = provider.GetAction(0, State2P(), Ctx());
        Assert.True(action.Broca is { Kind: ActionKind.MentalAttack });
    }

    [Fact]
    public void PlayerProvider_ThreeInvalid_DefaultsToWait()
    {
        var provider = new PlayerActionProvider(new StringReader("x\ny\nz\n"), new StringWriter());
        var action = provider.GetAction(0, State2P(), Ctx());
        Assert.Null(action.M1);
        Assert.Null(action.Broca);
    }

    [Fact]
    public void PlayerProvider_Eof_DefaultsToWait()
    {
        var provider = new PlayerActionProvider(new StringReader(""), new StringWriter());
        var action = provider.GetAction(0, State2P(), Ctx());
        Assert.Null(action.M1);
        Assert.Null(action.Broca);
    }

    // ---- AC-3：RenderSetup ----

    [Fact]
    public void RenderSetup_ContainsParticipants()
    {
        var s = RoundRenderer.RenderSetup(State2P(), Data());
        Assert.Contains("== 战斗开始 ==", s);
        Assert.Contains("玩家: HP 50/50 SAN 80/80 队伍 1", s);
        Assert.Contains("杂兵: HP 15/15 SAN 60/60 队伍 2", s);
    }

    // ---- AC-4~8、13：RenderRound 九段 ----

    [Fact]
    public void RenderRound_AllSections()
    {
        var state = State2P();
        var tm = new TurnManager(Data(), CalibrationConfig.Default, new NpcActionProvider());
        // 玩家首回合物理攻击（脚本化输入 1）
        var ctx = new CombatContext(new DeterministicRng(42), Data(), CalibrationConfig.Default);
        // 用组合 provider：p0 玩家喂 "1\n"、p1 NPC
        var provider = new CompositeActionProvider(
            new PlayerActionProvider(new StringReader("1\n"), new StringWriter()), new NpcActionProvider());
        tm = new TurnManager(Data(), CalibrationConfig.Default, provider);
        var result = tm.StepRound(state, ctx);
        var s = RoundRenderer.RenderRound(state.Round, state, result, tm, Data(), CalibrationConfig.Default);

        // AC-4 速度段
        Assert.Contains("[速度] p0 玩家: 察觉 ", s);
        Assert.Contains("[速度] p1 杂兵: 察觉 ", s);
        Assert.Contains("→ 总分 ", s);
        // AC-13 [顺序] 行
        Assert.Contains("[顺序] p0 → p1", s);
        // AC-5 行动段
        Assert.Contains("[行动] p0 玩家: 物理攻击 → p1", s);
        // AC-7 状态段
        Assert.Contains("[状态] p0: HP ", s);
        Assert.Contains("tone(NE ", s);
        Assert.Contains("gates(S ", s);
        // AC-13 [a(t)] 段
        Assert.Contains("[a(t)] p0: sensory ", s);
        Assert.Contains("Precentral ", s);
        Assert.Contains("Broca ", s);
        // AC-6 结算段（m F4）
        Assert.Contains("[结算] A1 m=", s);
        Assert.Matches(@"A1 m=\d\.\d{4} \(dealt", s);
        // AC-13 [因子] 段
        Assert.Contains("[因子] p0→p1: base 4 × force ", s);
        // 等待参与者（p1 NPC 已行动——行动段有 p1 行）
        Assert.Contains("[行动] p1 杂兵: ", s);
    }

    [Fact]
    public void RenderRound_EndReason_MaxRounds()
    {
        var cal = new CalibrationConfig { MaxRounds = 1 };
        var state = State2P();
        var tm = new TurnManager(Data(), cal, new NpcActionProvider());
        var ctx = new CombatContext(new DeterministicRng(42), Data(), cal);
        var result = tm.StepRound(state, ctx);
        var s = RoundRenderer.RenderRound(state.Round, state, result, tm, Data(), cal);

        Assert.Contains("[结束] MaxRounds（回合上限 1 达成）", s);
        Assert.Single(Regex.Matches(s, "\\[结束\\]")); // 唯一输出源
    }

    // ---- AC-9：完整战斗冒烟（进程级）----

    [Fact]
    public void FullBattle_Smoke_Exit0()
    {
        var exe = ConsoleDll();
        var psi = new System.Diagnostics.ProcessStartInfo("dotnet", $"\"{exe}\" --seed 42")
        {
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        using var proc = System.Diagnostics.Process.Start(psi)!;
        for (var i = 0; i < 60; i++)
            proc.StandardInput.WriteLine("1"); // 玩家一直物理攻击（NPC 自动）
        proc.StandardInput.Close();
        var output = proc.StandardOutput.ReadToEnd();
        proc.WaitForExit(120_000);

        Assert.Equal(0, proc.ExitCode);
        Assert.Contains("== 战斗开始 ==", output);
        Assert.Contains("[结束]", output);
        Assert.Contains("===== 回合 ", output);
    }

    // ---- AC-10：静息 trace（进程级）----

    [Fact]
    public void RestingTrace_M1Range()
    {
        var exe = ConsoleDll();
        var psi = new System.Diagnostics.ProcessStartInfo("dotnet", $"\"{exe}\" --trace-resting 30")
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        using var proc = System.Diagnostics.Process.Start(psi)!;
        var output = proc.StandardOutput.ReadToEnd();
        proc.WaitForExit(60_000);

        Assert.Equal(0, proc.ExitCode);
        Assert.Contains("== 静息不动点 ==", output);
        var match = Regex.Match(output, @"active 节点 (\d+\.\d+) ~ (\d+\.\d+)");
        Assert.True(match.Success, $"未找到 active 区间: {output}");
        var min = double.Parse(match.Groups[1].Value);
        var max = double.Parse(match.Groups[2].Value);
        Assert.InRange(min, 0.535, 0.536); // F3 渲染串 [0.535, 0.772]
        Assert.InRange(max, 0.770, 0.772);
    }

    // ---- AC-11：确定性（进程级，脚本化输入）----

    [Fact]
    public void Determinism_ScriptedInput_SameOutput()
    {
        string Run()
        {
            var exe = Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..",
                "YouAreNotTheFish.Console", "bin", "Debug", "net8.0", "YouAreNotTheFish.Console.dll");
            var psi = new System.Diagnostics.ProcessStartInfo("dotnet", $"\"{exe}\" --seed 42")
            {
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };
            using var proc = System.Diagnostics.Process.Start(psi)!;
            for (var i = 0; i < 60; i++)
                proc.StandardInput.WriteLine("1");
            proc.StandardInput.Close();
            var output = proc.StandardOutput.ReadToEnd();
            proc.WaitForExit(120_000);
            return output;
        }

        var a = Run();
        var b = Run();
        Assert.Equal(a, b); // 同种子同脚本化输入 → 逐字符相同
    }

    // ---- AC-12：异常（CliUsage 退出码）----

    [Fact]
    public void InvalidArgs_Exit1()
    {
        var exe = ConsoleDll();
        var psi = new System.Diagnostics.ProcessStartInfo("dotnet", $"\"{exe}\" --seed abc")
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        using var proc = System.Diagnostics.Process.Start(psi)!;
        var err = proc.StandardError.ReadToEnd();
        proc.WaitForExit(30_000);

        Assert.Equal(1, proc.ExitCode);
        Assert.Contains("用法", err);
    }

    private static CombatContext Ctx() => new(new DeterministicRng(42), Data(), CalibrationConfig.Default);

    /// <summary>Console exe 路径（测试 bin → src → YouAreNotTheFish.Console/bin/Debug/net8.0）。</summary>
    private static string ConsoleDll() => Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..",
        "YouAreNotTheFish.Console", "bin", "Debug", "net8.0", "YouAreNotTheFish.Console.dll");
}
