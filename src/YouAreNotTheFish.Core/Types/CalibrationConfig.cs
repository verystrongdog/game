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

    /// <summary>demo 玩家 HP [NEW]。来源：核心机制 §10.1 玩家基线值默认（±10 为角色类型偏移，此处取基线）。</summary>
    public int PlayerHp { get; init; } = 50;

    /// <summary>demo 玩家 SAN [NEW]。来源：核心机制 §10.1 玩家基线值默认。</summary>
    public int PlayerSan { get; init; } = 80;

    /// <summary>demo NPC 杂兵 HP [NEW]。来源：核心机制 §10.1 轻度病人区间取中值（HP 12-18→15）。</summary>
    public int NpcHp { get; init; } = 15;

    /// <summary>demo NPC 杂兵 SAN [NEW]。来源：核心机制 §10.1 轻度病人区间取中值（SAN 50-70→60）。</summary>
    public int NpcSan { get; init; } = 60;

    /// <summary>默认配置（demo 用）。</summary>
    public static CalibrationConfig Default { get; } = new();
}
