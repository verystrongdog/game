namespace YouAreNotTheFish.ConsoleApp;

/// <summary>CLI 参数错误（含用法说明）——退出码 1。</summary>
public sealed class CliUsageException(string message) : Exception(message);

/// <summary>
/// CLI 参数解析——csharp-console spec@v1.2 §二 2.2 + #105 T7 Q14。
/// --seed &lt;n&gt;：RNG 种子（默认 42）；--trace-resting &lt;n&gt;：静息 trace 模式（默认 30）。
/// --demo-situation：情境 demo 非交互 trace 模式（Q14）——--env/--day/--rounds/--mfield-demo 子参数。
/// 非法值（非数字/负数/&lt;1/缺失）→ CliUsageException；重复参数后者覆盖；未知参数 → CliUsageException。
/// </summary>
public sealed record CliArgs(
    ulong Seed,
    int? TraceRestingRounds,
    bool DemoSituation = false,
    string? Environment = null,
    int Day = 0,
    int Rounds = 10,
    bool MfieldDemo = false)
{
    public const ulong DefaultSeed = 42;
    public const int DefaultTraceRounds = 30;
    public const int DefaultDay = 0;
    public const int DefaultRounds = 10;

    public static CliArgs Parse(string[] args)
    {
        ArgumentNullException.ThrowIfNull(args);
        ulong seed = DefaultSeed;
        int? traceRounds = null;
        var demoSituation = false;
        string? environment = null;
        var day = DefaultDay;
        var rounds = DefaultRounds;
        var mfieldDemo = false;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "--seed":
                    seed = ParseUlong(RequireValue(args, ref i, "--seed"), "--seed");
                    break;
                case "--trace-resting":
                    var n = ParseUlong(RequireValue(args, ref i, "--trace-resting"), "--trace-resting");
                    if (n < 1)
                        throw new CliUsageException("--trace-resting 必须 ≥ 1");
                    traceRounds = (int)n;
                    break;
                case "--demo-situation":
                    demoSituation = true;
                    break;
                case "--env":
                    environment = RequireValue(args, ref i, "--env");
                    break;
                case "--day":
                    day = (int)ParseUlong(RequireValue(args, ref i, "--day"), "--day");
                    break;
                case "--rounds":
                    var r = ParseUlong(RequireValue(args, ref i, "--rounds"), "--rounds");
                    if (r < 1)
                        throw new CliUsageException("--rounds 必须 ≥ 1");
                    rounds = (int)r;
                    break;
                case "--mfield-demo":
                    mfieldDemo = true;
                    break;
                default:
                    throw new CliUsageException(
                        $"未知参数: {args[i]}（用法: --seed &lt;n&gt; [--trace-resting &lt;n&gt;] [--demo-situation [--env &lt;id&gt;] [--day &lt;n&gt;] [--rounds &lt;n&gt;] [--mfield-demo]]）");
            }
        }

        return new CliArgs(seed, traceRounds, demoSituation, environment, day, rounds, mfieldDemo);
    }

    private static string RequireValue(string[] args, ref int i, string flag)
    {
        if (i + 1 >= args.Length)
            throw new CliUsageException($"{flag} 缺少值");
        return args[++i];
    }

    private static ulong ParseUlong(string value, string flag)
    {
        if (!ulong.TryParse(value, out var n))
            throw new CliUsageException($"{flag} 值非法: {value}（须为非负整数）");
        return n;
    }
}
