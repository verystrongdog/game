namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 只读战斗上下文——plan §三（框架 memory：含 RNG 的只读上下文）。
/// 无可变回合计数（归 CombatState，plan §三 行注）。
/// </summary>
/// <param name="Rng">随机数源——plan §二 确定性原则（RNG 注入）。</param>
/// <param name="Data">全部游戏数据聚合——plan §三 CombatContext 行。</param>
/// <param name="Calibration">校准常量——plan §三。</param>
public sealed record CombatContext(IRng Rng, Data.GameData Data, CalibrationConfig Calibration);
