using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// TurnOrderBuilder spec@v1.1（../../../规格/引擎/csharp-speed.md）§六 AC-9~AC-14。
/// RNG 消费序契约（spec §三 3.2）：组内索引升序 → for i = m−1 downto 1: j = NextInt(i+1) → swap；
/// m=1 不消费 rng；组间 = 分数降序。镜像实现（结转 #3）逐字复述算法，不复制引擎代码。
/// </summary>
public class TurnOrderBuilderTests
{
    /// <summary>
    /// 独立镜像 Fisher-Yates（结转 #3——不得复制引擎代码，按 spec §三 3.2 逐字复述）：
    /// for i = m−1 downto 1: j = NextInt(i+1); swap(group[i], group[j])。
    /// </summary>
    private static int[] MirrorShuffle(int[] group, IRng rng)
    {
        int m = group.Length;
        for (int i = m - 1; i >= 1; i--)
        {
            int j = rng.NextInt(i + 1);
            (group[i], group[j]) = (group[j], group[i]);
        }

        return group;
    }

    /// <summary>消费 rng 即抛——验证 m=0/1 路径零消费（AC-14）。</summary>
    private sealed class ThrowingRng : IRng
    {
        public float NextFloat() => throw new InvalidOperationException("rng 不应被消费");
        public int NextInt(int maxExclusive) => throw new InvalidOperationException("rng 不应被消费");
    }

    // ---- AC-9 无平局 ----

    [Fact]
    public void BuildOrder_NoTies_Descending_RngIndependent()
    {
        float[] scores = [0.9f, 0.5f, 0.7f];
        Assert.Equal(new[] { 0, 2, 1 }, TurnOrderBuilder.BuildOrder(scores, new DeterministicRng(1)));
        Assert.Equal(new[] { 0, 2, 1 }, TurnOrderBuilder.BuildOrder(scores, new DeterministicRng(999)));
    }

    // ---- AC-10 全平局（RNG 消费序契约）----

    [Fact]
    public void BuildOrder_AllTied_MirrorsFisherYates_ConsumptionContract()
    {
        float[] scores = [0.5f, 0.5f, 0.5f];

        var expected = MirrorShuffle([0, 1, 2], new DeterministicRng(42));
        var actual = TurnOrderBuilder.BuildOrder(scores, new DeterministicRng(42));
        Assert.Equal(expected, actual); // 逐元素相等——RNG 消费序契约

        var again = TurnOrderBuilder.BuildOrder(scores, new DeterministicRng(42));
        Assert.Equal(actual, again); // 同种子两次 → 相同

        Assert.Equal([0, 1, 2], actual.OrderBy(x => x).ToArray()); // 输出 = 输入索引的排列
    }

    // ---- AC-11 混合平局组（m=2 组恰好一次 NextInt(2)）----

    [Fact]
    public void BuildOrder_MixedTieGroups_FixedSeedExact()
    {
        float[] scores = [0.8f, 0.5f, 0.5f, 0.2f];
        var actual = TurnOrderBuilder.BuildOrder(scores, new DeterministicRng(7));

        Assert.Equal(0, actual[0]); // 唯一最高分不动
        Assert.Equal(3, actual[3]); // 唯一最低分不动

        // 镜像 m=2 组 [1,2]：仅一次 NextInt(2)。j=0 → swap → [2,1]；j=1 → 不变 → [1,2]
        int j = new DeterministicRng(7).NextInt(2);
        int[] expected = j == 0 ? [0, 2, 1, 3] : [0, 1, 2, 3];
        Assert.Equal(expected, actual);
    }

    // ---- AC-12 契约防御 ----

    [Fact]
    public void BuildOrder_NullDefenses_Throw()
    {
        Assert.Throws<ArgumentNullException>(
            () => TurnOrderBuilder.BuildOrder(null!, new DeterministicRng(1)));
        Assert.Throws<ArgumentNullException>(
            () => TurnOrderBuilder.BuildOrder([0.5f], null!));
    }

    // ---- AC-13 确定性 ----

    [Fact]
    public void BuildOrder_SameSeedRepeated_BitEqual()
    {
        float[] scores = [0.5f, 0.5f, 0.5f, 0.5f];
        var a = TurnOrderBuilder.BuildOrder(scores, new DeterministicRng(42));
        var b = TurnOrderBuilder.BuildOrder(scores, new DeterministicRng(42));
        Assert.Equal(a, b);
    }

    // ---- AC-14 空/单元素 + 零 rng 消费 ----

    [Fact]
    public void BuildOrder_EmptyOrSingle_NoRngConsumed()
    {
        Assert.Empty(TurnOrderBuilder.BuildOrder([], new ThrowingRng()));
        Assert.Equal(new[] { 0 }, TurnOrderBuilder.BuildOrder([0.42f], new ThrowingRng()));
    }
}
