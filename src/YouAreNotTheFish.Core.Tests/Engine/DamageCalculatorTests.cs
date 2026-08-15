using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Tests.Engine;

/// <summary>
/// DamageCalculator spec@v1.1（.scratch/csharp-damage/design/spec.md）§六 AC-1~AC-17 + AC-18 新实证。
/// 锚点来源：spec §六（任务issue 01 第三轮实测表 #15-#19，runtime 8.0.29 本地实测 + 审计独立复算）；
/// 「逐位」标注者精确相等（Assert.Equal float 无容差 = 逐位）。
/// 无需数据加载（纯结算模块，输入全部合成）。
/// </summary>
public class DamageCalculatorTests
{
    private static readonly CalibrationConfig Cal = CalibrationConfig.Default;

    private static DamageCalculator New() => new(Cal);

    // ---- AC-1 物理基线：全默认 → 4.0f 命中（逐位） ----

    [Fact]
    public void Physical_DefaultBaseline_Returns4()
    {
        var calc = New();
        var (damage, hit) = calc.CalcPhysicalDamage(4, 0, 0f, 0f, 1.0f, false, new SeqRng(0.0f));
        Assert.Equal(4.0f, damage);
        Assert.True(hit);
    }

    // ---- AC-2 调制链：满调制 → 10.0f；部分调制 + gate → 5.6f（逐位） ----

    [Fact]
    public void Physical_FullModulation_Returns10()
    {
        var (damage, _) = New().CalcPhysicalDamage(4, 0, 0.5f, 1.0f, 1.0f, false, new SeqRng(0.0f));
        Assert.Equal(10.0f, damage);
    }

    [Fact]
    public void Physical_PartialModulationWithGate_Returns5_6()
    {
        var (damage, _) = New().CalcPhysicalDamage(4, 0, 0.25f, 0.5f, 0.8f, false, new SeqRng(0.0f));
        // s2=(1+0.25)+0.5=1.75 → 4×1.75×0.8=5.6（f32 结合序契约 §五 1）
        Assert.Equal(5.6f, damage);
    }

    // ---- AC-3 Round1 / Floor1 直接锚（公开 static） ----

    [Theory]
    [InlineData(1.95f, 2.0f)]
    [InlineData(1.5f, 1.5f)]
    [InlineData(2.6f, 2.6f)]
    [InlineData(1.3f, 1.3f)]
    [InlineData(0.75f, 0.8f)]
    public void Round1_HalfAwayFromZero_MatchesAnchors(float input, float expected)
    {
        Assert.Equal(expected, DamageCalculator.Round1(input));
    }

    [Theory]
    [InlineData(1.95f, 1.9f)]
    [InlineData(0.75f, 0.7f)]
    [InlineData(3.36f, 3.3f)]
    public void Floor1_FloorToTenth_MatchesAnchors(float input, float expected)
    {
        Assert.Equal(expected, DamageCalculator.Floor1(input));
    }

    // ---- AC-4 clamp：超上限截断、负 motivation 保留（E-1 裁决 2026-08-14） ----

    [Theory]
    [InlineData(0.7f, 0f, 6.0f)]    // force 超 cap 0.5 → 截断
    [InlineData(0f, 1.5f, 8.0f)]    // motivation 超 cap 1.0 → 截断
    [InlineData(-0.3f, -0.5f, 2.0f)] // motivation 下界 −1（E-1 裁决）：沮丧降伤害——(1+0)+(−0.5)=0.5 → 4×0.5=2.0
    public void Physical_ClampsForceAndMotivation(float force, float motivation, float expected)
    {
        var (damage, _) = New().CalcPhysicalDamage(4, 0, force, motivation, 1.0f, false, new SeqRng(0.0f));
        Assert.Equal(expected, damage);
    }

    // ---- AC-5 命中边界：roll < 0.75f 严格；miss 仍返回完整伤害值（哨兵） ----

    [Fact]
    public void Physical_HitBoundary_MatchesSequence()
    {
        // roll 序列: 0.0, 0.74, 0.75, 0.74999994, 0.999 → 期望 hit/hit/miss/hit/miss
        var calc = New();
        var rng = new SeqRng(0.0f, 0.74f, 0.75f, 0.74999994f, 0.999f);
        var hits = new bool[5];
        for (int i = 0; i < 5; i++)
        {
            (_, hits[i]) = calc.CalcPhysicalDamage(4, 0, 0f, 0f, 1.0f, false, rng);
        }
        Assert.Equal([true, true, false, true, false], hits);
    }

    [Fact]
    public void Physical_Miss_StillReturnsFullDamage()
    {
        // 哨兵：结算不可放进 if(hit) 分支——miss 也返回完整伤害（结转 #2）
        var (damage, hit) = New().CalcPhysicalDamage(4, 0, 0f, 0f, 1.0f, false, new SeqRng(0.75f));
        Assert.Equal(4.0f, damage);
        Assert.False(hit);
    }

    // ---- AC-6 命中率分布：roll 0.80 miss；同种子分布镜像 ----

    [Fact]
    public void Physical_Roll080_IsMiss()
    {
        var (_, hit) = New().CalcPhysicalDamage(4, 0, 0f, 0f, 1.0f, false, new SeqRng(0.80f));
        Assert.False(hit);
    }

    [Fact]
    public void Physical_HitDistribution_MirrorsRngThresholdCount()
    {
        const ulong seed = 12345;
        const int n = 1000;

        // 期望：同种子下 1000 次 NextFloat 中 roll < 0.75f 的计数
        int expected = 0;
        var refRng = new DeterministicRng(seed);
        for (int i = 0; i < n; i++)
        {
            if (refRng.NextFloat() < 0.75f) expected++;
        }

        // 实际：同种子下 1000 次 CalcPhysicalDamage 的命中数（每次恰好消费 1 次 NextFloat）
        int hits = 0;
        var calc = New();
        var rng = new DeterministicRng(seed);
        for (int i = 0; i < n; i++)
        {
            (_, var hit) = calc.CalcPhysicalDamage(4, 0, 0f, 0f, 1.0f, false, rng);
            if (hit) hits++;
        }

        Assert.Equal(expected, hits);
    }

    // ---- AC-7 防御减半仅物理；精神签名不含 defenderIsDefending ----

    [Fact]
    public void Physical_Defending_HalvesDamage()
    {
        var calc = New();
        var (defending, _) = calc.CalcPhysicalDamage(4, 0, 0.5f, 1.0f, 1.0f, true, new SeqRng(0.0f));
        var (open, _) = calc.CalcPhysicalDamage(4, 0, 0.5f, 1.0f, 1.0f, false, new SeqRng(0.0f));
        Assert.Equal(5.0f, defending);
        Assert.Equal(10.0f, open);
    }

    [Fact]
    public void Mental_Signature_HasNoDefenderIsDefending()
    {
        var paramNames = typeof(DamageCalculator)
            .GetMethod(nameof(DamageCalculator.CalcMentalDamage))!
            .GetParameters()
            .Select(p => p.Name);
        Assert.DoesNotContain("defenderIsDefending", paramNames);
    }

    // ---- AC-8 武器加成；精神 baseDamage 消费哨兵（写死 2f 实现必挂） ----

    [Fact]
    public void Physical_WeaponBonus_AddsBeforeModulation()
    {
        var calc = New();
        var (withWeapon, _) = calc.CalcPhysicalDamage(4, 6, 0f, 0f, 1.0f, false, new SeqRng(0.0f));
        var (bare, _) = calc.CalcPhysicalDamage(1, 0, 0f, 0f, 1.0f, false, new SeqRng(0.0f));
        Assert.Equal(10.0f, withWeapon);
        Assert.Equal(1.0f, bare);
    }

    [Fact]
    public void Mental_BaseDamage3_ConsumedNotHardcoded2()
    {
        // 哨兵：写死 2f 的实现输出 2.0/1.0 必挂（结转 #2）
        var (san, hp) = New().CalcMentalDamage(3, 0f, 0, 1.0f, 1.0f);
        Assert.Equal(3.0f, san);
        Assert.Equal(1.5f, hp);
    }

    // ---- AC-9 物理恰好消费 1 次 rng（抛异常即漏馅）；精神零消费 ----

    [Fact]
    public void Physical_ThrowingRng_Propagates()
    {
        var ex = Assert.Throws<InvalidOperationException>(() =>
            New().CalcPhysicalDamage(4, 0, 0f, 0f, 1.0f, false, new ThrowingRng()));
        Assert.NotNull(ex);
    }

    [Fact]
    public void Mental_NoRng_Completes()
    {
        var (san, hp) = New().CalcMentalDamage(2, 0f, 0, 1.0f, 1.0f);
        Assert.Equal(2.0f, san);
        Assert.Equal(1.0f, hp);
    }

    // ---- AC-10 精神基线 ----

    [Fact]
    public void Mental_DefaultBaseline_Returns2And1()
    {
        var (san, hp) = New().CalcMentalDamage(2, 0f, 0, 1.0f, 1.0f);
        Assert.Equal(2.0f, san);
        Assert.Equal(1.0f, hp);
    }

    // ---- AC-11 精神 motivation 与 endurance：inner 量化（镜像式） ----

    [Fact]
    public void Mental_MotivationAndEndurance_QuantizedInner()
    {
        var calc = New();
        // inner 镜像：Round1(2×1.25−1) = Round1(1.5) = 1.5（与引擎同序同算）
        Assert.Equal(1.5f, DamageCalculator.Round1(2f * 1.25f - 1f));
        var (san, hp) = calc.CalcMentalDamage(2, 0.25f, 1, 1.0f, 1.0f);
        Assert.Equal(1.5f, san);  // san = Round1(inner×1×1) = inner（pen=1、gate=1）
        Assert.Equal(0.7f, hp);   // Floor1(1.5×0.5) = Floor1(0.75) = 0.7
    }

    // ---- AC-12 精神下界：inner 最低 1.0；gate=0 → 0 ----

    [Fact]
    public void Mental_NegativeRaw_ClampsTo1()
    {
        var calc = New();
        // raw = 2×0.69−2 = −0.62 → Round1(−0.62) = −0.6 → max(1.0, −0.6) = 1.0
        var (san, hp) = calc.CalcMentalDamage(2, -0.31f, 2, 1.0f, 1.0f);
        Assert.Equal(1.0f, san);
        Assert.Equal(0.5f, hp);

        // raw = 0 → inner 1.0
        var (san2, hp2) = calc.CalcMentalDamage(2, 0f, 2, 1.0f, 1.0f);
        Assert.Equal(1.0f, san2);
        Assert.Equal(0.5f, hp2);

        // gate=0 → 0（max 在 gate 前：inner=1，1×0=0）
        var (san3, hp3) = calc.CalcMentalDamage(2, 0f, 0, 1.0f, 0.0f);
        Assert.Equal(0.0f, san3);
        Assert.Equal(0.0f, hp3);
    }

    // ---- AC-13 穿透档位：严格小于、先判 tier2 后判 tier1、互斥取高档 ----

    [Theory]
    [InlineData(0.30f, 1.0f)]    // 恰好 0.30 → 不穿透
    [InlineData(0.2999f, 1.3f)]  // <0.30 → tier1 ×1.3
    [InlineData(0.15f, 1.3f)]    // 恰好 0.15 → tier1（非 tier2）
    [InlineData(0.149f, 2.0f)]   // <0.15 → tier2 ×2.0
    public void Mental_PenetrationTiers_StrictLess(float ratio, float expectedSan)
    {
        // inner=1：baseDamage=2, endurance=1 → raw=1 → inner=1.0
        var (san, _) = New().CalcMentalDamage(2, 0f, 1, ratio, 1.0f);
        Assert.Equal(expectedSan, san);
    }

    // ---- AC-14 穿透组合锚点（逐位） ----

    [Fact]
    public void Mental_PenetrationCombos_MatchAnchors()
    {
        var calc = New();

        // 2×1×1.3 = 2.6 → san 2.6、hp Floor1(1.3)=1.3
        var (san1, hp1) = calc.CalcMentalDamage(2, 0f, 0, 0.299f, 1.0f);
        Assert.Equal(2.6f, san1);
        Assert.Equal(1.3f, hp1);

        // inner=Round1(2×1.25−1)=1.5 → 1.5×1×1.3=1.95 → Round1(1.95f)=2.0（f32 域，F1）、hp 1.0
        var (san2, hp2) = calc.CalcMentalDamage(2, 0.25f, 1, 0.299f, 1.0f);
        Assert.Equal(2.0f, san2);
        Assert.Equal(1.0f, hp2);

        // 2×0.9×2.0 = 3.6 → san 3.6、hp 1.8
        var (san3, hp3) = calc.CalcMentalDamage(2, 0f, 0, 0.149f, 0.9f);
        Assert.Equal(3.6f, san3);
        Assert.Equal(1.8f, hp3);
    }

    // ---- AC-15 确定性：同输入同种子重复调用逐位一致；输入不可变（值类型语义） ----

    [Fact]
    public void Determinism_SameSeedSameResult()
    {
        const ulong seed = 999;
        var calc = New();
        var results = new float[5];
        for (int i = 0; i < 5; i++)
        {
            (var dmg, _) = calc.CalcPhysicalDamage(4, 3, 0.2f, 0.4f, 0.7f, false, new DeterministicRng(seed));
            results[i] = dmg;
        }
        for (int i = 1; i < 5; i++)
        {
            Assert.Equal(results[0], results[i]); // 逐位一致——无 static 可变状态
        }
    }

    // ---- AC-16 异常契约 ----

    [Fact]
    public void Ctor_NullCal_ThrowsArgumentNull()
    {
        Assert.Throws<ArgumentNullException>(() => new DamageCalculator(null!));
    }

    [Fact]
    public void Physical_NullRng_ThrowsArgumentNull()
    {
        Assert.Throws<ArgumentNullException>(() =>
            New().CalcPhysicalDamage(4, 0, 0f, 0f, 1.0f, false, null!));
    }

    // ---- AC-17 CalibrationConfig：12 伤害常量 + 4 demo 模板 float 化（重载绑定探针） ----

    private static bool IsFloat(float _) => true;
    private static bool IsFloat(int _) => false;

    [Fact]
    public void CalibrationConfig_DamageConstants_DefaultValues()
    {
        Assert.Equal(4, Cal.BasePhysicalDamage);
        Assert.Equal(2, Cal.BaseMentalDamage);
        Assert.Equal(0.85f, Cal.BaseHitChance);
        Assert.Equal(0.10f, Cal.L0EvadeHitPenalty);
        Assert.Equal(0.5f, Cal.ForceCap);
        Assert.Equal(1.0f, Cal.MotivationCap);
        Assert.Equal(0.5f, Cal.DefendPhysicalReduction);
        Assert.Equal(0.30f, Cal.SanPenetrationTier1Ratio);
        Assert.Equal(1.3f, Cal.SanPenetrationTier1Multiplier);
        Assert.Equal(0.15f, Cal.SanPenetrationTier2Ratio);
        Assert.Equal(2.0f, Cal.SanPenetrationTier2Multiplier);
        Assert.Equal(0.1f, Cal.DamagePrecision);
    }

    [Fact]
    public void CalibrationConfig_DemoTemplates_AreFloat()
    {
        // 重载绑定探针（Δ审计 refute 方案）：int 字段绑定 IsFloat(int)=false，float 绑定 IsFloat(float)=true。
        // 赋值探针（float hp = cal.PlayerHp）已被实测证伪——int→float 隐式转换使其永远编译成功。
        Assert.True(IsFloat(Cal.PlayerHp));
        Assert.True(IsFloat(Cal.PlayerSan));
        Assert.True(IsFloat(Cal.NpcHp));
        Assert.True(IsFloat(Cal.NpcSan));
        Assert.Equal(50f, Cal.PlayerHp);
        Assert.Equal(80f, Cal.PlayerSan);
        Assert.Equal(15f, Cal.NpcHp);
        Assert.Equal(60f, Cal.NpcSan);
    }

    // ---- AC-18 新实证：L2 类型变更回执（22 字段 §二 2.2；现有 types 测试零改动编译+全绿） ----

    [Fact]
    public void Types_FloatFields_StoreAndReadBitwise()
    {
        // 事件字段 float 化回执：5.6f 存读回逐位（int 类型下 5.6 将被截断为 5）
        var evt = new PhysicalDamageEvent(1, 0, 1) { DamageDealt = 5.6f };
        Assert.Equal(5.6f, evt.DamageDealt);

        var mental = new MentalDamageEvent(1, 0, 1) { SanDamage = 2.6f, HpDamage = 1.3f };
        Assert.Equal(2.6f, mental.SanDamage);
        Assert.Equal(1.3f, mental.HpDamage);

        // CreateDefault(float,float) 回执：Hp 50f 逐位
        var ps = ParticipantState.CreateDefault(50f, 80f);
        Assert.Equal(50f, ps.Hp);
        Assert.Equal(80f, ps.San);
    }

    // ---- 测试辅助 RNG ----

    /// <summary>固定序列 RNG（AC-5 边界序列）。耗尽后再取 → InvalidOperationException。</summary>
    private sealed class SeqRng : IRng
    {
        private readonly Queue<float> _values;

        public SeqRng(params float[] values) => _values = new Queue<float>(values);

        public float NextFloat() => _values.Dequeue();

        public int NextInt(int maxExclusive) => throw new InvalidOperationException("序列 RNG 无 NextInt");
    }

    /// <summary>抛异常 RNG（AC-9：物理路径必须消费 rng——若实现跳过消费则不抛）。</summary>
    private sealed class ThrowingRng : IRng
    {
        public float NextFloat() => throw new InvalidOperationException("ThrowingRng");

        public int NextInt(int maxExclusive) => throw new InvalidOperationException("ThrowingRng");
    }
}
