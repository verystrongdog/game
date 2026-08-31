using System.Text.Json;
using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Flow;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.ConsoleApp;

/// <summary>
/// 控制台 harness 主循环——csharp-console spec@v1.2 §三 3.3 + #105 T7 Q14。
/// 战斗模式：Create → RenderSetup → StepRound 循环（RenderRound 输出）→ 结束（[结束] 由 RenderRound 段 9 输出）。
/// 静息 trace 模式：--trace-resting N → 单参与者零事件 N 回合 → RenderResting（environment=null 纯静息，s=0）。
/// 情境 demo 模式：--demo-situation → 非交互 trace（Q14）——初始环境/情境/strength + 每回合 λ(D) + WC a(t) 摘要
///   + 首回合 s_env 注入前后对比 + --mfield-demo 时 PLACEHOLDER 警告；同 seed 同输出。
/// 退出码：0 正常；1 参数错误/数据缺失/校验失败。
/// </summary>
public static class Program
{
    public static int Main(string[] args)
    {
        try
        {
            var cli = CliArgs.Parse(args);
            var data = GameDataLoader.LoadAll(FindDataDir());
            var cal = cli.MfieldDemo
                ? CalibrationConfig.Default with { AllowPlaceholderDemo = true }
                : CalibrationConfig.Default;

            if (cli.TraceRestingRounds is { } rounds)
                RunResting(cli.Seed, rounds, data, cal);
            else if (cli.DemoSituation)
                RunDemoSituation(cli, data, cal);
            else
                RunBattle(cli.Seed, data, cal);

            return 0;
        }
        catch (CliUsageException ex)
        {
            Console.Error.WriteLine(ex.Message);
            Console.Error.WriteLine("用法: YouAreNotTheFish.Console [--seed <n>] [--trace-resting <n>] [--demo-situation [--env <id>] [--day <n>] [--rounds <n>] [--mfield-demo]]");
            return 1;
        }
        catch (Exception ex) when (ex is DirectoryNotFoundException or FileNotFoundException)
        {
            Console.Error.WriteLine($"数据目录缺失: {ex.Message}");
            return 1;
        }
        catch (JsonException ex)
        {
            // #106 Q5 分层：Data/Engine 层抛 JsonException → Console 转 stderr + exit 1
            Console.Error.WriteLine($"数据校验失败: {ex.Message}");
            return 1;
        }
    }

    private static void RunBattle(ulong seed, GameData data, CalibrationConfig cal)
    {
        var ctx = new CombatContext(new DeterministicRng(seed), data, cal);
        var player = ParticipantState.CreateDefault(cal.PlayerHp, cal.PlayerSan);
        var npc = ParticipantState.CreateDefault(cal.NpcHp, cal.NpcSan);
        var state = CombatState.Create([player, npc], [1, 2], data, cal);

        var provider = new CompositeActionProvider(
            new PlayerActionProvider(Console.In, Console.Out), new NpcActionProvider());
        var tm = new TurnManager(data, cal, provider);

        Console.Write(RoundRenderer.RenderSetup(state, data));
        while (!tm.IsOver(state))
        {
            var result = tm.StepRound(state, ctx);
            Console.Write(RoundRenderer.RenderRound(state.Round, state, result, tm, data, cal));
        }
    }

    private static void RunResting(ulong seed, int rounds, GameData data, CalibrationConfig cal)
    {
        var ctx = new CombatContext(new DeterministicRng(seed), data, cal);
        var player = ParticipantState.CreateDefault(cal.PlayerHp, cal.PlayerSan);
        // environment=null：纯静息 trace（s=0，无情境注入——csharp-tone AC-15 静息验证方法语义）
        var state = CombatState.Create([player], [1], data, cal, environment: null);
        var tm = new TurnManager(data, cal, new WaitProvider());

        for (var i = 0; i < rounds; i++)
            tm.StepRound(state, ctx);

        Console.Write(RoundRenderer.RenderResting(state.Participants[0].Wc, data));
    }

    /// <summary>
    /// 情境 demo 非交互 trace 模式（Q14）——不污染 RunBattle；同 seed 同输出。
    /// 输出：初始环境/情境/strength + 每回合 λ(D) + WC a(t) 摘要 + 首回合 s_env 注入前后对比 +
    /// --mfield-demo 时 PLACEHOLDER 警告。
    /// </summary>
    private static void RunDemoSituation(CliArgs cli, GameData data, CalibrationConfig cal)
    {
        var envId = cli.Environment ?? "ward";
        if (!data.EnvTones.Environments.ContainsKey(envId))
            throw new CliUsageException($"环境 id 非法: \"{envId}\"（须 ∈ env_tones.json: {string.Join("/", data.EnvTones.Environments.Keys)}）");

        var ctx = new CombatContext(new DeterministicRng(cli.Seed), data, cal);
        var player = ParticipantState.CreateDefault(cal.PlayerHp, cal.PlayerSan);
        var npc = ParticipantState.CreateDefault(cal.NpcHp, cal.NpcSan);
        var state = CombatState.Create([player, npc], [1, 2], data, cal, envId);
        var tm = new TurnManager(data, cal, new NpcActionProvider(), cli.Day);

        var env = data.EnvTones.Environments[envId];
        Console.WriteLine($"== 情境 demo trace ==");
        Console.WriteLine($"环境: {envId}（{env.DisplayName}）");
        Console.WriteLine($"情境: {state.Situation.ArchetypeId} | strength={state.Situation.Strength:R} | 环境基调 α_env=[{string.Join(",", env.AlphaEnv.Select(v => v.ToString("R")))}]");
        Console.WriteLine($"游戏日 D={cli.Day} | λ(D)={MoonState.Lambda(cli.Day):R}");

        // 首回合 s_env 注入前后对比（Q14）：初始 WC a(t) vs Phase 1 合成后
        var sEnv = state.SEnv;
        Console.WriteLine($"s_env[69] 非零节点 {sEnv.Count(v => v != 0f)} 个 | 注入前 a[0] 摘要: {Summarize(state.Participants[0].Wc.A)}");
        Console.WriteLine($"s_env 前 8 值: [{string.Join(",", sEnv.Take(8).Select(v => v.ToString("R")))}]");

        if (cal.AllowPlaceholderDemo)
        {
            Console.WriteLine("⚠️ PLACEHOLDER 数据，仅原型测试——m_field 注入中（moonlight_landing 未校准）");
        }

        for (var round = 1; round <= cli.Rounds; round++)
        {
            var result = tm.StepRound(state, ctx);
            Console.WriteLine($"回合 {round}: λ(D)={MoonState.Lambda(cli.Day):R} | 情境={state.Situation.ArchetypeId}(strength={state.Situation.Strength:R}) | a(t) 摘要: {Summarize(state.Participants[0].Wc.A)}");
            if (round == 1)
                Console.WriteLine($"  （首回合 Phase 1 合成后）a[0] 摘要: {Summarize(state.Participants[0].Wc.A)}");
        }
    }

    private static string Summarize(float[] a)
    {
        if (a.Length == 0) return "[]";
        var min = a.Min();
        var max = a.Max();
        var mean = a.Average();
        return $"[min={min:R} max={max:R} mean={mean:R}]";
    }

    private static string FindDataDir()
    {
        // #107 Q4：YANTF_DATA_DIR 显式覆盖（Console 回归测试注入坏数据用）——
        // 已设置 → 用之（无效路径自然走「数据目录缺失」fail-fast）；未设置 → 完全走既有发现策略。
        if (Environment.GetEnvironmentVariable("YANTF_DATA_DIR") is { Length: > 0 } envDir)
            return envDir;

        // 从执行目录向上回溯 + 绝对路径候选（镜像测试项目 DataDirCandidates 约定）
        var dir = AppContext.BaseDirectory;
        for (var i = 0; i < 8 && dir is not null; i++)
        {
            if (File.Exists(Path.Combine(dir, "brain_regions.json")))
                return dir;
            dir = Path.GetDirectoryName(dir);
        }
        if (File.Exists("/home/dog/game/data/brain_regions.json"))
            return "/home/dog/game/data";
        throw new DirectoryNotFoundException("data/ 目录未找到（从执行目录向上回溯）");
    }
}
