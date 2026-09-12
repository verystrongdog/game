using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// moonState(D) 契约骨架（Grilling #108 Q10，继承 #103 Q4-Q6）。
/// 静态纯函数：Query(int day) → MoonStateResult（λ(D) 解析 + 壳参数结构 + QhatBaseline 占位）。
/// - λ(D) = (1−cos(2πD/29.5))/2，D=0 ↔ 新月（#103 Q4）
/// - E_c/E_th 按 #102 E2 线性端点族形式结构实现（占位常量挂 CalibrationConfig，正式数值归 #35）
/// - QhatBaseline N=69 是占位契约（≠「graph identity 已证明 N=69」；闭合后升级 + 硬维度校验）
/// - D 推进机制与 MOON_PHASE_CHANGED 广播不实现（demo 固定 D；无 P2 消费者，Q10）
/// - 运行时防御断言：0≤λ≤1 / E_c>0 / 0&lt;E_th&lt;E_c / 有限性（Q11）
/// </summary>
public static class MoonState
{
    /// <summary>月相周期 T_moon（游戏日）。来源：#103 Q4（29.5 连续周期）。</summary>
    public const double MoonPeriod = 29.5;

    /// <summary>λ(D) 解析推进——纯函数，无累积漂移（#103 Q4）。</summary>
    public static double Lambda(int day)
    {
        if (day < 0)
            throw new ArgumentOutOfRangeException(nameof(day), $"day 须 ≥ 0，实测 {day}");
        return (1.0 - Math.Cos(2.0 * Math.PI * day / MoonPeriod)) / 2.0;
    }

    /// <summary>
    /// 查询月相状态（纯函数，Q10）。
    /// </summary>
    /// <param name="day">游戏日 D ∈ ℕ₀（自开局已完成游戏日边界数）。</param>
    /// <param name="landing">月光场落点数据（r/α_s 参数；Q9 校验在加载期完成）。</param>
    /// <param name="cal">校准常量（E_c/E_th 占位常量 + MFieldGain）。</param>
    /// <exception cref="ArgumentOutOfRangeException">day &lt; 0。</exception>
    /// <exception cref="InvalidDataException">运行时防御断言失败（0≤λ≤1 / E_c&gt;0 / 0&lt;E_th&lt;E_c / 有限性）。</exception>
    public static MoonStateResult Query(int day, MoonlightLanding landing, CalibrationConfig cal)
    {
        ArgumentNullException.ThrowIfNull(landing);
        ArgumentNullException.ThrowIfNull(cal);

        var lambda = Lambda(day);
        // E2 线性端点族（#102 Q5）：E_c(λ)=E_c,min+ΔE_c·λ；E_th(λ)=E_th,min+ΔE_th·λ
        var eC = cal.EcMin + cal.DeltaEc * lambda;
        var eTh = cal.EthMin + cal.DeltaEth * lambda;

        // 运行时防御断言（Q11）
        if (double.IsNaN(lambda) || lambda < 0.0 || lambda > 1.0)
            throw new InvalidDataException($"MoonState λ(D) 越界: λ={lambda}");
        if (double.IsNaN(eC) || eC <= 0.0)
            throw new InvalidDataException($"MoonState E_c 非法: E_c={eC}");
        if (double.IsNaN(eTh) || eTh <= 0.0 || eTh >= eC)
            throw new InvalidDataException($"MoonState E_th 非法: E_th={eTh}（须 0&lt;E_th&lt;E_c={eC}）");

        // QhatBaseline[69] 占位（N=69 占位契约；正式数值归 #35；q̂ 无空间差异——延迟）
        var qhat = new float[69];
        Array.Fill(qhat, 1.0f); // 占位：均一基线（E2 Q4 占位 E_c(λ)/N 语义由 #35 定形，此处仅结构占位）

        return new MoonStateResult(
            (float)lambda,
            new MoonShell(eC, eTh),
            qhat,
            landing.CalibrationStatus,
            landing.CalibrationVersion);
    }
}

/// <summary>moonState(D) 查询结果（#103 Q6 基线壳态）。</summary>
/// <param name="Phase">λ(D) ∈ [0,1]（0=新月 / 1=满月）。</param>
/// <param name="Shell">壳参数 {E_c(λ), E_th(λ)}（E2 线性端点族占位）。</param>
/// <param name="QhatBaseline">q̂ 基线占位数组（N=69 占位契约）。</param>
/// <param name="CalibrationStatus">calibration_status ∈ {PLACEHOLDER, CALIBRATED}。</param>
/// <param name="Version">calibration_version。</param>
public sealed record MoonStateResult(
    float Phase, MoonShell Shell, float[] QhatBaseline, string CalibrationStatus, int Version);

/// <summary>能量壳参数（E2 线性端点族）。</summary>
public sealed record MoonShell(double EC, double ETh);
