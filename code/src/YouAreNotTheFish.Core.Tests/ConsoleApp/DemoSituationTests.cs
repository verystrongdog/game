using System.Diagnostics;
using System.Text.RegularExpressions;
using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.ConsoleApp;

namespace YouAreNotTheFish.Core.Tests.ConsoleApp;

/// <summary>
/// #105 G9：Console --demo-situation 进程级测试（Grilling #108 Q14）。
/// 复用 InvalidArgs_Exit1 进程测试模式（锁 stderr/输出内容）。
/// </summary>
public class DemoSituationTests
{
    /// <summary>
    /// Console 程序集路径。配置名从本测试程序集自身路径推导，不硬编码 Debug
    /// （否则 Release 构建下 CI 失败、本机因残留产物误通过，2026-09-12 实测）。
    /// </summary>
    private static string ConsoleDll()
    {
        // BaseDirectory = <proj>/bin/<Config>/net8.0/ → 一层上溯即 <proj>/bin/<Config>
        var config = Path.GetFileName(Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..")));
        var srcDir = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));
        var dll = Path.Combine(srcDir, "YouAreNotTheFish.Console", "bin", config, "net8.0",
                               "YouAreNotTheFish.Console.dll");
        if (!File.Exists(dll))
            throw new FileNotFoundException(
                $"Console 程序集不存在：{dll}\n（先构建 Console 工程，且配置需与测试一致）", dll);
        return dll;
    }

    private static (int ExitCode, string Stdout, string Stderr) Run(string args)
    {
        var psi = new ProcessStartInfo("dotnet", $"\"{ConsoleDll()}\" {args}")
        {
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };
        using var proc = Process.Start(psi)!;
        var stdout = proc.StandardOutput.ReadToEnd();
        var stderr = proc.StandardError.ReadToEnd();
        proc.WaitForExit(60_000);
        return (proc.ExitCode, stdout, stderr);
    }

    [Fact]
    public void DemoSituation_Outputs_EnvironmentSituationLambda()
    {
        var (code, stdout, _) = Run("--demo-situation --env ward --day 7 --rounds 3 --seed 42");
        Assert.Equal(0, code);
        Assert.Contains("== 情境 demo trace ==", stdout);
        Assert.Contains("环境: ward（病房）", stdout);
        Assert.Contains("情境: ", stdout);
        Assert.Contains("strength=", stdout);
        Assert.Contains("λ(D)=", stdout);
        Assert.Contains("回合 1:", stdout);
        Assert.Contains("回合 3:", stdout);
        Assert.Contains("a(t) 摘要", stdout);
    }

    [Fact]
    public void DemoSituation_DefaultEnvIsWard()
    {
        var (code, stdout, _) = Run("--demo-situation --rounds 1 --seed 1");
        Assert.Equal(0, code);
        Assert.Contains("环境: ward（病房）", stdout); // Q14：CombatState.Create 默认 ward
    }

    [Fact]
    public void DemoSituation_UnknownEnv_Exit1()
    {
        var (code, _, stderr) = Run("--demo-situation --env nonexistent --rounds 1");
        Assert.Equal(1, code);
        Assert.Contains("环境 id 非法", stderr);
    }

    [Fact]
    public void DemoSituation_SameSeed_SameOutput()
    {
        var (_, a, _) = Run("--demo-situation --env corridor --day 3 --rounds 5 --seed 99");
        var (_, b, _) = Run("--demo-situation --env corridor --day 3 --rounds 5 --seed 99");
        Assert.Equal(a, b); // 同 seed 同输出（Q14）
    }

    [Fact]
    public void DemoSituation_MfieldDemo_WarnsPlaceholder()
    {
        var (code, stdout, _) = Run("--demo-situation --env ward --rounds 2 --seed 5 --mfield-demo");
        Assert.Equal(0, code);
        Assert.Contains("PLACEHOLDER 数据，仅原型测试", stdout);
    }

    [Fact]
    public void DemoSituation_NoMfieldDemo_NoWarning()
    {
        var (code, stdout, _) = Run("--demo-situation --env ward --rounds 2 --seed 5");
        Assert.Equal(0, code);
        Assert.DoesNotContain("PLACEHOLDER 数据", stdout); // 默认 m_field 通道关闭
    }

    [Fact]
    public void DemoSituation_LambdaVariesWithDay()
    {
        // D=0 → λ=0；D=14 → λ≈0.9936（离散近满月，峰值 D=14.75）——渲染值应不同
        var (_, d0, _) = Run("--demo-situation --env ward --day 0 --rounds 1 --seed 2");
        var (_, d14, _) = Run("--demo-situation --env ward --day 14 --rounds 1 --seed 2");
        Assert.Contains("λ(D)=0", d0);
        Assert.Contains("λ(D)=0.99", d14); // (1-cos(2π·14/29.5))/2 ≈ 0.9936
    }
}
