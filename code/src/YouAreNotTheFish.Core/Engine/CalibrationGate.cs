using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// 校准门禁（Grilling #108 Q11）——挂载于 m_field 合成注入点。
/// PLACEHOLDER / 版本不匹配 → fail-fast（InvalidDataException，Data/Engine 层抛 → Console 转 stderr+exit 1，接 #106 分层）。
/// 门禁范围 = moonlight→m_field 正式消费链路；s_env/α_env/情境原型注入不挂（三通道正交，#101 Q3）。
/// demo 例外 = CalibrationConfig.AllowPlaceholderDemo（默认 false）。
/// </summary>
public static class CalibrationGate
{
    /// <summary>当前 schema 契约期望的 calibration_status/version 匹配（Q9：status ∈ {PLACEHOLDER, CALIBRATED}，version 须一致）。</summary>
    public static void EnsureCalibrated(MoonlightLanding landing, CalibrationConfig cal)
    {
        ArgumentNullException.ThrowIfNull(landing);
        ArgumentNullException.ThrowIfNull(cal);

        if (cal.AllowPlaceholderDemo)
            return; // demo 例外（Q11）：显式放行 + 调用方输出醒目警告

        if (landing.CalibrationStatus != "CALIBRATED")
            throw new InvalidDataException(
                $"m_field 消费被门禁拦截：calibration_status=\"{landing.CalibrationStatus}\"（须 CALIBRATED；PLACEHOLDER 数据仅 --mfield-demo 显式例外可用）");
        if (landing.CalibrationVersion != cal.ExpectedCalibrationVersion)
            throw new InvalidDataException(
                $"m_field 消费被门禁拦截：calibration_version={landing.CalibrationVersion} ≠ 期望 {cal.ExpectedCalibrationVersion}");
    }
}
