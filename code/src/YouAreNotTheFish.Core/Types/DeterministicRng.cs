namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// splitmix64 确定性随机数生成器 [NEW]——spec@v1.1 §三 3.2。
/// 选择理由：System.Random 种子序列不保证跨 .NET 版本稳定；splitmix64 为 counter-based
/// 生成器——单一 64 位状态、周期 2^64、实现 5 行可审计，保证同种子同序列的确定性契约（约束 C8/AC-6）。
/// </summary>
public sealed class DeterministicRng : IRng
{
    private ulong _state;

    /// <summary>以给定种子构造。同种子 → 同序列（AC-6）。</summary>
    public DeterministicRng(ulong seed) => _state = seed;

    /// <summary>splitmix64 混洗：一次递增 + 三次异或位移乘法，返回混洗后的 64 位。</summary>
    private ulong NextUlong()
    {
        _state += 0x9E3779B97F4A7C15UL;
        ulong z = _state;
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBUL;
        return z ^ (z >> 31);
    }

    /// <summary>返回 [0,1) 均匀分布浮点（取高 24 位，保证含 0 不含 1）。</summary>
    public float NextFloat() => (NextUlong() >> 40) * (1.0f / 16777216.0f);

    /// <summary>返回 [0, maxExclusive) 均匀分布整数（取模——demo 用量下偏差可忽略）。</summary>
    public int NextInt(int maxExclusive)
    {
        if (maxExclusive <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(maxExclusive),
                $"maxExclusive must be positive, got {maxExclusive}");
        }

        return (int)(NextUlong() % (ulong)maxExclusive);
    }
}
