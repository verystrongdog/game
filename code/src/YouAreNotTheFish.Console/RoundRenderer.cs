using System.Text;
using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Flow;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.ConsoleApp;

/// <summary>
/// 回合输出渲染——csharp-console spec@v1.2 §三 3.2（plan §九 输出清单 9 段）。
/// 纯函数（无 I/O）——测试直接断言字符串。名字映射：p0=玩家、p1=杂兵（ParticipantState 无名字字段）。
/// 结算 m 渲染时重算（events §5.3 同式）；速度分量 = 回合末快照重算（state.Salience[p]——flow §2.2）。
/// </summary>
public static class RoundRenderer
{
    private static readonly string[] Names = ["玩家", "杂兵"];

    private static readonly string[] PerceptionFids =
        ["Pericalcarine", "TransverseTemporal", "Insula", "AnteriorCingulateCortex"];

    private static string Name(int p) => p < Names.Length ? Names[p] : $"p{p}";

    /// <summary>RenderRound：9 段输出（§九 清单）。[结束] 唯一输出源（IsOver 时）。</summary>
    public static string RenderRound(int round, CombatState state, TurnResult result,
        TurnManager tm, GameData data, CalibrationConfig cal)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"===== 回合 {round} =====");

        // 段 2：速度（回合末快照重算——new SpeedScoreCalculator(data, cal) 实例）
        var speed = new SpeedScoreCalculator(data, cal);
        for (var p = 0; p < state.Participants.Count; p++)
        {
            var ps = state.Participants[p];
            var comps = speed.ComputeComponents(ps.Wc, state.Salience[p], ps.Gurney, ps.IsDefending);
            var score = speed.ComputeScore(comps, new SpeedWeights(1f / 3f, 1f / 3f, 1f / 3f));
            sb.AppendLine($"[速度] p{p} {Name(p)}: 察觉 {comps.Perception:F3} / 决断 {comps.Decision:F3} / 执行 {comps.Execution:F3} → 总分 {score:F3}（回合末）");
        }

        // 段 3：顺序（tm.LastRoundOrder——决策 D1）
        if (tm.LastRoundOrder.Count > 0)
            sb.AppendLine($"[顺序] {string.Join(" → ", tm.LastRoundOrder.Select(i => $"p{i}"))}");

        // 段 4：状态 + 段 5：a(t)
        var rows = ResolveRows(data);
        for (var p = 0; p < state.Participants.Count; p++)
        {
            var ps = state.Participants[p];
            var defending = ps.IsDefending ? " [防御中]" : "";
            sb.AppendLine($"[状态] p{p}: HP {ps.Hp}/{ps.HpMax} SAN {ps.San}/{ps.SanMax} " +
                $"tone(NE {ps.Tone.Ne:F3} VTA {ps.Tone.DaVta:F3} SNc {ps.Tone.DaSnc:F3} 5HT {ps.Tone.Ht5:F3}) " +
                $"gates(S {ps.Gates.GateSomatic:F3} C {ps.Gates.GateCognitive:F3} L {ps.Gates.GateLimbic:F3})" +
                $"{defending} [CD] Defend={ps.DefendCd}");
            var sensory = (ps.Wc.A[rows.Perception[0]] + ps.Wc.A[rows.Perception[1]]
                + ps.Wc.A[rows.Perception[2]] + ps.Wc.A[rows.Perception[3]]) / 4f;
            sb.AppendLine($"[a(t)] p{p}: sensory {sensory:F3} / Precentral {ps.Wc.A[rows.Precentral]:F3} / Broca {ps.Wc.A[rows.Broca]:F3}");
        }

        // 段 6：行动（tm.LastRoundActions——决策 D1）
        foreach (var (p, action) in tm.LastRoundActions)
            sb.AppendLine($"[行动] p{p} {Name(p)}: {Describe(action)}");

        // 段 7：结算（m F4 重算——events §5.3 同式）+ 段 8：因子
        foreach (var ev in result.Events)
        {
            sb.AppendLine($"[结算] {DescribeEvent(ev, cal)}");
            var factor = DescribeFactor(ev, cal);
            if (factor is not null)
                sb.AppendLine($"[因子] {factor}");
        }

        // 段 9：结束（唯一输出源——v1.2 裁决）
        if (tm.IsOver(state))
        {
            var reason = IsTeamDefeated(state)
                ? "TeamDefeated（一方全灭——Hp≤0 ∨ San≤0）"
                : $"MaxRounds（回合上限 {cal.MaxRounds} 达成）";
            sb.AppendLine($"[结束] {reason}");
        }

        return sb.ToString();
    }

    /// <summary>RenderSetup：战斗开始头（循环前输出）。</summary>
    public static string RenderSetup(CombatState state, GameData data)
    {
        var sb = new StringBuilder();
        sb.AppendLine("== 战斗开始 ==");
        for (var p = 0; p < state.Participants.Count; p++)
        {
            var ps = state.Participants[p];
            sb.AppendLine($"{Name(p)}: HP {ps.Hp}/{ps.HpMax} SAN {ps.San}/{ps.SanMax} 队伍 {state.Teams[p]}");
        }
        return sb.ToString();
    }

    /// <summary>RenderResting：静息不动点（F3 渲染串断言 [0.535, 0.772]）。</summary>
    public static string RenderResting(WcState resting, GameData data)
    {
        var w = WMatrixBuilder.Build(data);
        float min = float.MaxValue, max = float.MinValue;
        for (var i = 0; i < resting.A.Length; i++)
        {
            var rowActive = false;
            for (var k = 0; k < w.W.GetLength(1); k++)
                if (w.W[i, k] != 0f) { rowActive = true; break; }
            if (!rowActive)
                continue;
            min = Math.Min(min, resting.A[i]);
            max = Math.Max(max, resting.A[i]);
        }
        return $"== 静息不动点 ==\nactive 节点 {min:F3} ~ {max:F3}（48 节点，M1 实测 [0.535, 0.771]）";
    }

    private static string Describe(CombatAction action)
    {
        if (action.M1 is null && action.Broca is null)
            return "等待";
        var parts = new List<string>();
        if (action.M1 is { } m1)
            parts.Add(m1.Kind switch
            {
                ActionKind.PhysicalAttack => $"物理攻击 → p{m1.TargetId}",
                ActionKind.Defend => "防御",
                _ => "?",
            });
        if (action.Broca is { } b)
            parts.Add($"精神攻击 → p{b.TargetId}");
        return string.Join(" + ", parts);
    }

    private static string DescribeEvent(CombatEvent ev, CalibrationConfig cal) => ev switch
    {
        PhysicalDamageEvent ph when ph.Hit && ph.DamageBlocked > 0f =>
            $"A5 m={ph.DamageBlocked / ph.IncomingDamage:F4} (防御成功)",
        PhysicalDamageEvent ph when ph.Hit =>
            $"A1 m={ph.DamageDealt / cal.ExpectedDamage:F4} (dealt {ph.DamageDealt} / expected {cal.ExpectedDamage} 命中)",
        PhysicalDamageEvent ph =>
            "A2 m=0.0000 (miss)",
        MentalDamageEvent me =>
            $"A4 m={me.SanDamage / Expected(me.MotivationMod, cal):F4} (SAN {me.SanDamage} / expected {Expected(me.MotivationMod, cal):F1})",
        StatusChangeEvent { Kind: StatusKind.Panic } sc =>
            $"C1 恐慌跨越 (SAN {sc.SanBefore}→{sc.SanAfter})",
        StatusChangeEvent { Kind: StatusKind.Downed } sc =>
            $"D1/D2 倒下广播 (p{sc.ActorId})",
        _ => "no-op",
    };

    private static string? DescribeFactor(CombatEvent ev, CalibrationConfig cal) => ev switch
    {
        PhysicalDamageEvent ph =>
            $"p{ph.ActorId}→p{ph.TargetId}: base {ph.BaseDamage} × force {ph.ForceMod:F3} × motivation {ph.MotivationMod:F3} × gate {ph.GateBonus:F3}",
        MentalDamageEvent me =>
            $"p{me.ActorId}→p{me.TargetId}: base {cal.BaseMentalDamage} × motivation {me.MotivationMod:F3} × gate {me.GateBonus:F3}",
        _ => null, // 非伤害事件无因子行
    };

    /// <summary>A4 expected = cal.BaseMentalDamage×(1+mot) − cal.EndurancePassivePenalty（events §5.3.2 同式）。</summary>
    private static float Expected(float motivationMod, CalibrationConfig cal) =>
        cal.BaseMentalDamage * (1f + motivationMod) - cal.EndurancePassivePenalty;

    private static bool IsTeamDefeated(CombatState state)
    {
        foreach (var team in state.Teams.Distinct())
        {
            var members = Enumerable.Range(0, state.Participants.Count)
                .Where(p => state.Teams[p] == team)
                .ToList();
            if (members.All(p => state.Participants[p].Hp <= 0f || state.Participants[p].San <= 0f))
                return true;
        }
        return false;
    }

    private static (int[] Perception, int Precentral, int Broca) ResolveRows(GameData data)
    {
        int Find(string fid)
        {
            var ids = data.Wsensory.RegionIds;
            for (var i = 0; i < ids.Length; i++)
                if (ids[i] == fid) return i;
            throw new KeyNotFoundException($"RegionIds 无 {fid}");
        }

        return (PerceptionFids.Select(Find).ToArray(), Find("Precentral"), Find("ParsOpercularis"));
    }
}
