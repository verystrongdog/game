using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Flow;

/// <summary>
/// Phase 4 行动来源抽象——csharp-flow spec@v1.2 §三 3.1（任务issue Q1=A）。
/// demo 实现：NpcActionProvider（适配 NpcSalience）+ 玩家实现（step 11 console 提供）。
/// </summary>
public interface IActionProvider
{
    /// <summary>
    /// 为参与者 p 声明行动。
    /// </summary>
    /// <param name="participantIndex">行动者索引。</param>
    /// <param name="state">当前战斗状态（只读——provider 不得修改）。</param>
    /// <param name="ctx">只读上下文（RNG/数据/常量）。</param>
    /// <returns>CombatAction——(null,null) 空声明合法（等待语义）。</returns>
    /// <exception cref="ArgumentNullException">state/ctx null。</exception>
    /// <exception cref="ArgumentOutOfRangeException">participantIndex ∉ [0, Count)。</exception>
    CombatAction GetAction(int participantIndex, CombatState state, CombatContext ctx);
}
