namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// Gurney 基底节门控模型状态（91 浮点中的 15 个）——运行时状态模型 §6.3。
/// 三环路各 5 群体，群体索引按 GurneyPopulation 枚举序（0=SD1…4=GPi）。
/// 环路字段命名显式（Somatic/Cognitive/Limbic），不依赖 CstcLoop 枚举序——约束 C2。
/// 值域 [0,1]。构造时防御性拷贝（约束 C7）。
/// </summary>
public sealed record GurneyState
{
    /// <summary>somatic 环路 5 群体激活 a_SD1/a_SD2/a_STN/a_GPe/a_GPi。来源：§6.3。</summary>
    public float[] Somatic { get; }

    /// <summary>cognitive 环路 5 群体激活。来源：§6.3。</summary>
    public float[] Cognitive { get; }

    /// <summary>limbic 环路 5 群体激活。来源：§6.3。</summary>
    public float[] Limbic { get; }

    /// <summary>从外部数组构造——三个数组各拷贝一份。</summary>
    public GurneyState(float[] somatic, float[] cognitive, float[] limbic)
    {
        Somatic = (float[])somatic.Clone();
        Cognitive = (float[])cognitive.Clone();
        Limbic = (float[])limbic.Clone();
    }
}
