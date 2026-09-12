using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// 伤害结算器——csharp-damage spec@v1.1 §三：物理/精神伤害 + 一位小数量化（Q3=D）。
/// 无内部可变状态（cal 引用不可变 record）；无 static 可变状态 → 确定性（AC-15）。
/// 偏差声明对应（spec §八）：B1 defenderIsDefending 入签名（Audit F5）/
/// B2 精神武器不覆盖 / B3 生产者不实现（§五 5）/ B4 一位小数结算 / B5 类型变更（§二 2.2）/ B6 baseDamage 参数化（§五 6）。
/// </summary>
public sealed class DamageCalculator
{
    private readonly CalibrationConfig _cal;

    /// <summary>以校准配置构造。cal null → ArgumentNullException（spec §三 D12/AC-16）。</summary>
    public DamageCalculator(CalibrationConfig cal)
    {
        _cal = cal ?? throw new ArgumentNullException(nameof(cal));
    }

    /// <summary>
    /// 主伤害量化：半进位到 0.1（Q3=D）。公开 static（AC-3 可测性）。
    /// .NET 8 全 f32 域实现：x×10 → Truncate(x + CopySign(0.49999997f, x)) → x÷10（审计 F1 实测语义）；
    /// 如 1.9499999f×10f 先舍入为 19.5f → 2.0f。实现不可自手写近似算法替代。
    /// </summary>
    public static float Round1(float x) => MathF.Round(x, 1, MidpointRounding.AwayFromZero);

    /// <summary>
    /// HP 成分量化：向下取至 0.1（Q3=D「向下取整」语义）。/10f 精确除法落回 f32(0.1k) 网格点。
    /// 仅非负输入（spec §三 3.3——调用侧 sanDamage ≥ 0）。
    /// </summary>
    public static float Floor1(float x) => MathF.Floor(x * 10f) / 10f;

    /// <summary>
    /// 物理伤害结算——spec §三 3.1。计算序写死（f32 结合序契约 §五 1，重排即破坏逐位锚点）：
    /// s1=(float)(baseDamage+weaponBonus) → s2=(1f+cf)+cm 左结合 → s3=s1×s2 → s4=s3×gateBonus
    /// → s5=s4×(防御因子) → damage=Round1(s5)。
    /// rng 恰好消费 1 次（无条件，AC-9）；hit = roll &lt; BaseHitChance − L0EvadeHitPenalty（0.75f 精确，
    /// L0 回避自动触发——回合战斗流程 §6.2）。miss 仍返回完整伤害值（结算与判定解耦——AC-5）。
    /// 异常：rng null → ArgumentNullException（AC-16）。
    /// 未定义行为：NaN/Infinity、负 baseDamage/weaponBonus（s1 可为负）、gateBonus ∉ [0,1]。
    /// </summary>
    public (float Damage, bool Hit) CalcPhysicalDamage(
        int baseDamage, int weaponBonus, float forceMod, float motivationMod,
        float gateBonus, bool defenderIsDefending, IRng rng)
    {
        ArgumentNullException.ThrowIfNull(rng);

        // B4：一位小数结算——每步结算产物在最后一步统一量化（中间步保持全精度，Round1 仅作用于 s5）
        float s1 = (float)(baseDamage + weaponBonus);                    // int 加法精确，后转 float
        float cf = Math.Clamp(forceMod, 0f, _cal.ForceCap);              // 负值归零——沮丧不降伤害（plan §4.6 字面）
        // 🔧 2026-08-14 Grilling #24 E-1 裁决：motivation 下界由 0 改为 −1——与精神攻击（不 clamp）及
        // flow 层 producer（csharp-flow spec §5.1 clamp(tone_bias,−1,1)）口径统一；沮丧（低动机）时物理出力下降。
        float cm = Math.Clamp(motivationMod, -1f, _cal.MotivationCap);
        float s2 = (1f + cf) + cm;                                       // 左结合（§五 1）
        float s3 = s1 * s2;
        float s4 = s3 * gateBonus;
        float s5 = s4 * (defenderIsDefending ? _cal.DefendPhysicalReduction : 1f);
        float damage = Round1(s5);

        float roll = rng.NextFloat();                                    // 恰好 1 次，无条件（AC-9）
        bool hit = roll < (_cal.BaseHitChance - _cal.L0EvadeHitPenalty); // 0.75f 精确（任务issue 实测 #9）
        return (damage, hit);
    }

    /// <summary>
    /// 精神伤害结算——spec §三 3.2。永远命中（无 rng——精神攻击无命中判定，核心机制 §4.3）。
    /// raw=(float)baseDamage×(1f+motivationMod)−(float)endurance（F2：baseDamage 必须消费）
    /// → inner=max(1.0f, Round1(raw))（最低 1.0；max 在 gate 前——gate=0 → san 0 语义，plan §4.6 字面）
    /// → s1=inner×gateBonus → s2=s1×pen → sanDamage=Round1(s2)；hpDamage=Floor1(sanDamage×0.5f)。
    /// 穿透：先判 tier2（ratio&lt;0.15 → ×2.0）后判 tier1（ratio&lt;0.30 → ×1.3），互斥取高档，严格小于（D4/AC-13）。
    /// 异常：cal null → ArgumentNullException（构造时抛出）。
    /// 未定义行为：NaN/Infinity、ratio ∉ [0,1]、负 endurance、motivationMod ∉ [−1,1]。
    /// </summary>
    public (float SanDamage, float HpDamage) CalcMentalDamage(
        int baseDamage, float motivationMod, int endurance, float enemySanRatio, float gateBonus)
    {
        float raw = (float)baseDamage * (1f + motivationMod) - (float)endurance; // motivation 不 clamp（负值降伤害，下限由 max 兜底）
        float inner = MathF.Max(1.0f, Round1(raw));

        float pen;
        if (enemySanRatio < _cal.SanPenetrationTier2Ratio)
        {
            pen = _cal.SanPenetrationTier2Multiplier;                    // 先判 tier2（<0.15 → ×2.0）
        }
        else if (enemySanRatio < _cal.SanPenetrationTier1Ratio)
        {
            pen = _cal.SanPenetrationTier1Multiplier;                    // 再判 tier1（<0.30 → ×1.3）
        }
        else
        {
            pen = 1f;                                                    // 互斥取高档，严格小于（AC-13）
        }

        float s1 = inner * gateBonus;
        float s2 = s1 * pen;
        float sanDamage = Round1(s2);
        float hpDamage = Floor1(sanDamage * 0.5f);                       // 向下取至 0.1（Q3=D）
        return (sanDamage, hpDamage);
    }
}
