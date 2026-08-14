using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Flow;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.ConsoleApp;

/// <summary>
/// 控制台 harness 主循环——csharp-console spec@v1.2 §三 3.3。
/// 战斗模式：Create → RenderSetup → StepRound 循环（RenderRound 输出）→ 结束（[结束] 由 RenderRound 段 9 输出）。
/// 静息 trace 模式：--trace-resting N → 单参与者零事件 N 回合 → RenderResting。
/// 退出码：0 正常；1 参数错误/数据缺失。
/// </summary>
public static class Program
{
    public static int Main(string[] args)
    {
        try
        {
            var cli = CliArgs.Parse(args);
            var data = GameDataLoader.LoadAll(FindDataDir());
            var cal = CalibrationConfig.Default;

            if (cli.TraceRestingRounds is { } rounds)
                RunResting(cli.Seed, rounds, data, cal);
            else
                RunBattle(cli.Seed, data, cal);

            return 0;
        }
        catch (CliUsageException ex)
        {
            Console.Error.WriteLine(ex.Message);
            Console.Error.WriteLine("用法: YouAreNotTheFish.Console [--seed <n>] [--trace-resting <n>]");
            return 1;
        }
        catch (Exception ex) when (ex is DirectoryNotFoundException or FileNotFoundException)
        {
            Console.Error.WriteLine($"数据目录缺失: {ex.Message}");
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
        var state = CombatState.Create([player], [1], data, cal);
        var tm = new TurnManager(data, cal, new WaitProvider());

        for (var i = 0; i < rounds; i++)
            tm.StepRound(state, ctx);

        Console.Write(RoundRenderer.RenderResting(state.Participants[0].Wc, data));
    }

    private static string FindDataDir()
    {
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
