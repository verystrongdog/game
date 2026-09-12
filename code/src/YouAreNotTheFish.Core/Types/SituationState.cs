namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 当前情境只读状态（#75 D4 / #108 Q4）——全局单一情境（战斗/遭遇级）。
/// 消费方：P3 NPC 行为偏置参考（非 salience 乘子）、UI 情境标签、叙事、玩家观察。
/// 刷新 = 空间切换（战斗外）∪ 任意 C1（战斗内重选，下一回合 Phase 1 生效，Q8）。
/// </summary>
/// <param name="ArchetypeId">当前情境原型 id（situation_primitives.json name）。</param>
/// <param name="Strength">情境强度（Q7 双档：恐慌假 1.0 / 恐慌真 s_neg；情境生命周期内恒定）。</param>
/// <param name="EnvironmentId">当前环境 id（env_tones.json 键）。</param>
public sealed record SituationState(string ArchetypeId, float Strength, string EnvironmentId);
