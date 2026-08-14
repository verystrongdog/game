using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Flow;

/// <summary>
/// 响应窗口解析器接口——csharp-flow spec@v1.2 §二 2.3（响应窗口 stub，plan §一 范围表）。
/// 响应窗口内容（L0 回避自动触发已在 DamageCalculator 内生效；忍耐主动/L4 读意图/L5 叙事重构 B）
/// 留后续链路 feature——回合战斗流程 §六。
/// </summary>
public interface IResponseResolver
{
    /// <summary>
    /// 响应窗口：对已声明行动产出的调整事件（demo = Noop 恒空）。
    /// </summary>
    /// <param name="declared">已声明行动。</param>
    /// <param name="state">当前战斗状态（只读）。</param>
    /// <param name="ctx">只读上下文。</param>
    /// <returns>调整事件列表（可空列表）。</returns>
    IReadOnlyList<CombatEvent> Resolve(CombatAction declared, CombatState state, CombatContext ctx);
}

/// <summary>demo 恒空实现（响应窗口 stub）。</summary>
public sealed class NoopResponseResolver : IResponseResolver
{
    public IReadOnlyList<CombatEvent> Resolve(CombatAction declared, CombatState state, CombatContext ctx) => [];
}
