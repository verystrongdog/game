using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// m_field 通道合成（Grilling #108 Q12 + #101 Q4 公式）。
/// m_field_vec⁽ⁱ⁾[j] = QhatBaseline[j] × g(SAN_i) × R[j]
/// - q̂ = MoonState.Query(D).QhatBaseline（占位；无空间差异 q̂_{x_i}——延迟）
/// - g ≡ MFieldGain（E7/#35 定正式形式，不动架构）
/// - R[j] = 落点权重 v^norm（Q9：r/(4r+8) 主 / 1/(4r+8) 辅；r=PLACEHOLDER → 按 r=1 均匀）
/// 门禁（Q11）：m_field 合成注入点挂 EnsureCalibrated——PLACEHOLDER/版本不匹配 → fail-fast；
/// AllowPlaceholderDemo → 放行（调用方输出醒目警告）。
/// </summary>
public static class MFieldComposer
{
    /// <summary>
    /// 计算单个参与者 m_field 向量。
    /// </summary>
    /// <param name="landing">月光场落点（r/α_s 参数，Q9 校验在加载期完成）。</param>
    /// <param name="moon">moonState(D) 查询结果（q̂ 基线 + calibration 元数据）。</param>
    /// <param name="wsensory">W_sensory 矩阵（RegionIds 69 fid——落点 fid → 索引映射）。</param>
    /// <param name="san">参与者当前 SAN。</param>
    /// <param name="cal">校准常量（MFieldGain + 门禁开关）。</param>
    /// <returns>float[69] m_field（RegionIds 序）。</returns>
    /// <exception cref="InvalidDataException">门禁拦截（PLACEHOLDER 非 demo / 版本不匹配）。</exception>
    public static float[] Compute(
        MoonlightLanding landing, MoonStateResult moon, WsensoryMatrix wsensory,
        float san, CalibrationConfig cal)
    {
        ArgumentNullException.ThrowIfNull(landing);
        ArgumentNullException.ThrowIfNull(moon);
        ArgumentNullException.ThrowIfNull(wsensory);
        ArgumentNullException.ThrowIfNull(cal);

        // 门禁（Q11）：PLACEHOLDER/版本不匹配 → fail-fast；AllowPlaceholderDemo → 放行
        CalibrationGate.EnsureCalibrated(landing, cal);

        // R[69]：落点权重 v^norm（Q9 公式重算——预计算数组不作第二数据源）
        var r = 1.0;
        if (double.TryParse(landing.Semantics[0].R, System.Globalization.NumberStyles.Float,
                System.Globalization.CultureInfo.InvariantCulture, out var rv) && rv > 0.0)
            r = rv;
        var wPrimary = (float)(r / (4.0 * r + 8.0));
        var wSecondary = (float)(1.0 / (4.0 * r + 8.0));

        var weights = new float[wsensory.Matrix.Length];
        var fidIndex = wsensory.RegionIds.Select((fid, i) => (fid, i))
            .ToDictionary(x => x.fid, x => x.i);
        foreach (var sem in landing.Semantics)
        {
            foreach (var fid in sem.Primary)
                if (fidIndex.TryGetValue(fid, out var j)) weights[j] += wPrimary;
            foreach (var fid in sem.Secondary)
                if (fidIndex.TryGetValue(fid, out var j)) weights[j] += wSecondary;
        }

        // m_field[i][j] = q̂[j] × g(SAN_i) × R[j]（g ≡ MFieldGain 占位）
        var g = cal.MFieldGain;
        var result = new float[moon.QhatBaseline.Length];
        for (var j = 0; j < result.Length; j++)
            result[j] = moon.QhatBaseline[j] * g * weights[j];
        return result;
    }
}
