namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 校准常量集——plan §七 全表（spec@v1.1 §四 4.2，AC-9 逐常量断言）。
/// instance record + static Default（决策 D3——plan §七 字面「static class」的偏差：
/// sign-off 结转 #4 蒙特卡洛校准需要参数 sweep，实例化才能注入变体）。
/// [NEW] 标注待对应 issue 关闭后摘除（plan §七 规则）。
/// </summary>
public sealed record CalibrationConfig
{
    /// <summary>速度权重 w1。值 1/3。来源：回合战斗流程 §3.1（默认等权）。</summary>
    public float SpeedW1 { get; init; } = 1f / 3f;

    /// <summary>速度权重 w2。值 1/3。来源：回合战斗流程 §3.1。</summary>
    public float SpeedW2 { get; init; } = 1f / 3f;

    /// <summary>速度权重 w3。值 1/3。来源：回合战斗流程 §3.1。</summary>
    public float SpeedW3 { get; init; } = 1f / 3f;

    /// <summary>m 默认值。来源：皮层动力学 §5.3。</summary>
    public float MDefault { get; init; } = 0.3f;

    /// <summary>Softmax 温度基线。来源：NPC AI §3.4。</summary>
    public float TBase { get; init; } = 0.15f;

    /// <summary>δ 缩放因子 [NEW] 待校准。来源：运行时状态模型 §5.5 ⚠️ 延迟注。</summary>
    public float DeltaScale { get; init; } = 0.3f;

    /// <summary>精神缩放——未启用（demo 用固定 base 2），1.0 为禁用占位。来源：运行时状态模型 §8.1 ⚠️ 待赋值。</summary>
    public float ScaleMental { get; init; } = 1.0f;

    /// <summary>期望伤害（A1 m 公式分母）。来源：核心机制 §4.2。</summary>
    public int ExpectedDamage { get; init; } = 4;

    /// <summary>M1 持续占用惩罚 [NEW] 待校准。来源：回合战斗流程 §3.3（值未定义）。</summary>
    public float M1SustainPenalty { get; init; } = -0.1f;

    /// <summary>察觉「未显著激活」阈值 [NEW] 待校准。来源：回合战斗流程 §3.3（值未定义）。</summary>
    public float PerceptionThreshold { get; init; } = 0.15f;

    /// <summary>demo 玩家 HP [NEW]。来源：核心机制 §10.1 玩家基线值默认（±10 为角色类型偏移，此处取基线）。float——一位小数结算（csharp-damage spec §二 2.2 B5）。</summary>
    public float PlayerHp { get; init; } = 50f;

    /// <summary>demo 玩家 SAN [NEW]。来源：核心机制 §10.1 玩家基线值默认。float（B5）。</summary>
    public float PlayerSan { get; init; } = 80f;

    /// <summary>demo NPC 杂兵 HP [NEW]。来源：核心机制 §10.1 轻度病人区间取中值（HP 12-18→15）。float（B5）。</summary>
    public float NpcHp { get; init; } = 15f;

    /// <summary>demo NPC 杂兵 SAN [NEW]。来源：核心机制 §10.1 轻度病人区间取中值（SAN 50-70→60）。float（B5）。</summary>
    public float NpcSan { get; init; } = 60f;

    // ---- 伤害结算常量（csharp-damage spec@v1.1 §四 4.1，[NEW] 待 issue 关闭后摘除）----

    /// <summary>物理基础伤害 [NEW]。来源：核心机制 §4.2（空手伤害 4 HP）。经 baseDamage 参数传入（B6）。</summary>
    public int BasePhysicalDamage { get; init; } = 4;

    /// <summary>精神基础伤害 [NEW]。来源：核心机制 §4.3（基础 2 SAN）。经 baseDamage 参数传入（B6）。</summary>
    public int BaseMentalDamage { get; init; } = 2;

    /// <summary>基础命中率 [NEW]。来源：核心机制 §4.2（基础命中 85%）。</summary>
    public float BaseHitChance { get; init; } = 0.85f;

    /// <summary>L0 回避命中惩罚 [NEW]。来源：基础行动设计 §二/§三（L0 回避 命中 −10%）；自动触发——回合战斗流程 §6.2。</summary>
    public float L0EvadeHitPenalty { get; init; } = 0.10f;

    /// <summary>发力上限 [NEW]。来源：基础行动设计 §四（force cap +50%）。</summary>
    public float ForceCap { get; init; } = 0.5f;

    /// <summary>动机上限 [NEW]。来源：基础行动设计 §四（motivation cap +100%）。</summary>
    public float MotivationCap { get; init; } = 1.0f;

    /// <summary>防御物理减伤 [NEW]。来源：基础行动设计 §四（防御 −50% 仅物理）。</summary>
    public float DefendPhysicalReduction { get; init; } = 0.5f;

    /// <summary>穿透一档阈值 [NEW]。来源：核心机制 §4.3（SAN&lt;30% → ×1.3）。严格小于。</summary>
    public float SanPenetrationTier1Ratio { get; init; } = 0.30f;

    /// <summary>穿透一档倍率 [NEW]。来源：核心机制 §4.3（+30%）。</summary>
    public float SanPenetrationTier1Multiplier { get; init; } = 1.3f;

    /// <summary>穿透二档阈值 [NEW]。来源：核心机制 §4.3（SAN&lt;15% → ×2）。严格小于。</summary>
    public float SanPenetrationTier2Ratio { get; init; } = 0.15f;

    /// <summary>穿透二档倍率 [NEW]。来源：核心机制 §4.3。</summary>
    public float SanPenetrationTier2Multiplier { get; init; } = 2.0f;

    /// <summary>结算量化粒度 [NEW]——文档常量：计算路径不直接消费（Round1 固定 digits=1 / Floor1 分度 10f 与之对应，§五 6）。来源：Q3=D。</summary>
    public float DamagePrecision { get; init; } = 0.1f;

    /// <summary>忍耐·被动 SAN 减免 [NEW]。来源：基础行动设计 §四「忍耐·被动 SAN减免 -1（被动永久）」；A4 expected 公式（csharp-events spec §二 2.2，任务issue Q3=A）。</summary>
    public int EndurancePassivePenalty { get; init; } = 1;

    /// <summary>回合上限 [NEW] 待校准。来源：csharp-flow spec §5.5 结束条件（demo 防死循环，待校准）。</summary>
    public int MaxRounds { get; init; } = 50;

    /// <summary>默认配置（demo 用）。</summary>
    public static CalibrationConfig Default { get; } = new();
}
