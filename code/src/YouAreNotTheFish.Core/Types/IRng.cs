namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 随机数源抽象——plan §二 确定性原则：RNG 注入，引擎层无隐式随机。
/// </summary>
public interface IRng
{
    /// <summary>返回 [0,1) 均匀分布浮点。</summary>
    float NextFloat();

    /// <summary>返回 [0, maxExclusive) 均匀分布整数。maxExclusive ≤ 0 时抛 ArgumentOutOfRangeException。</summary>
    int NextInt(int maxExclusive);
}
