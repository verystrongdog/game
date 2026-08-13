using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Types;

/// <summary>AC-6（同种子同序列 / 异种子异序列 / NextInt 值域）。</summary>
public class DeterministicRngTests
{
    [Fact]
    public void SameSeed_ProducesSameSequence()
    {
        // AC-6: 同种子同序列（100 值对拍）
        var a = new DeterministicRng(seed: 42UL);
        var b = new DeterministicRng(seed: 42UL);

        for (var i = 0; i < 100; i++)
        {
            Assert.Equal(a.NextFloat(), b.NextFloat());
            Assert.Equal(a.NextInt(10), b.NextInt(10));
        }
    }

    [Fact]
    public void DifferentSeeds_ProduceDifferentSequences()
    {
        // AC-6: 异种子异序列（首个浮点即不同——对拍用）
        var a = new DeterministicRng(seed: 42UL);
        var b = new DeterministicRng(seed: 43UL);

        Assert.NotEqual(a.NextFloat(), b.NextFloat());
    }

    [Fact]
    public void NextFloat_StaysInUnitInterval()
    {
        // AC-6: NextFloat 值域 [0,1)
        var rng = new DeterministicRng(seed: 7UL);
        for (var i = 0; i < 1000; i++)
        {
            var v = rng.NextFloat();
            Assert.InRange(v, 0f, 1f);
            Assert.True(v < 1f, $"NextFloat must be < 1, got {v}");
        }
    }

    [Fact]
    public void NextInt_StaysInRange_AndCoversMultipleValues()
    {
        // AC-6: NextInt 值域 [0, maxExclusive) 且分布覆盖多值
        var rng = new DeterministicRng(seed: 99UL);
        var seen = new HashSet<int>();
        for (var i = 0; i < 100; i++)
        {
            var v = rng.NextInt(10);
            Assert.InRange(v, 0, 9);
            seen.Add(v);
        }

        Assert.True(seen.Count >= 5, $"expected at least 5 distinct values, got {seen.Count}");
    }

    [Fact]
    public void NextInt_NonPositiveBound_Throws()
    {
        var rng = new DeterministicRng(seed: 1UL);
        Assert.Throws<ArgumentOutOfRangeException>(() => rng.NextInt(0));
        Assert.Throws<ArgumentOutOfRangeException>(() => rng.NextInt(-1));
    }
}
