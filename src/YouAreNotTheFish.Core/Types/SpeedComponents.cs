namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 速度三成分终值——csharp-speed spec@v1.1 §二 2.1（均已回落/惩罚后）。
/// 察觉 = mean(4 察觉节点 a，逐节点回落)；决断 = mean(c_loop, 3 环路，无回落)；
/// 执行 = mean(a(Precentral), a_SD1_somatic) + M1 惩罚。
/// 值域：Perception/Decision [0,1]；Execution [−0.1, 1.5]（文档化不强制，生产方保证——同 WcState 姿态）。
/// 来源：回合战斗流程 §3.1-3.3；偏差 B2（归一化 mean）/B3（Putamen 代理）。
/// </summary>
/// <param name="Perception">察觉分——4 节点均值（逐节点回落已应用）。</param>
/// <param name="Decision">决断分——mean(c_loop, 3 环路)；无回落。</param>
/// <param name="Execution">执行分——mean(a(Precentral), a_SD1) + M1 惩罚。</param>
public sealed record SpeedComponents(float Perception, float Decision, float Execution);

/// <summary>
/// 速度合成权重——csharp-speed spec@v1.1 §二 2.2。默认等权 1/3（CalibrationConfig.SpeedW1/2/3）。
/// 权重只作用于合成层（速度 = W1×察觉 + W2×决断 + W3×执行），非成分内部（运行时状态模型 §8.1 已指针化）。
/// 来源：回合战斗流程 §3.1；偏差 B4（偏移逻辑不覆盖——本 feature 恒等权）。
/// </summary>
/// <param name="W1">察觉权重（CalibrationConfig.SpeedW1，默认 1/3）。</param>
/// <param name="W2">决断权重（SpeedW2）。</param>
/// <param name="W3">执行权重（SpeedW3）。</param>
public sealed record SpeedWeights(float W1, float W2, float W3)
{
    /// <summary>
    /// 从校准配置提取三速度权重（AC-15）。cal 为 null → ArgumentNullException。
    /// </summary>
    public static SpeedWeights FromCalibration(CalibrationConfig cal)
    {
        ArgumentNullException.ThrowIfNull(cal);
        return new SpeedWeights(cal.SpeedW1, cal.SpeedW2, cal.SpeedW3);
    }
}
