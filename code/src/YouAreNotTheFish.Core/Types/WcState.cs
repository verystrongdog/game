namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// Wilson-Cowan 层激活状态——运行时状态模型 §三（91 浮点中的 69 个 a_j）。
/// 行序 = canonical 69 = WsensoryMatrix.RegionIds（W_sensory.json rows 序）——约束 C1。
/// 值域 [0,1]（文档化不强制，L2 生产方保证）。构造时防御性拷贝（约束 C7）。
/// </summary>
public sealed record WcState
{
    /// <summary>a_j(t)：69 个脑区激活值，值域 [0,1]。来源：运行时状态模型 §三。</summary>
    public float[] A { get; }

    /// <summary>从外部数组构造——立即拷贝，之后外部修改不影响本状态。</summary>
    public WcState(float[] a) => A = (float[])a.Clone();
}
