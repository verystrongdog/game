using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Flow;

/// <summary>
/// Phase 4 声明→响应→结算 dispatch——csharp-flow spec@v1.2 §三 3.3（plan §5.3）。
/// 纯函数：只读 state，产事件列表，不修改实体状态（框架 D1——状态应用由 TurnManager 完成）。
/// 事件字段装客观结果（types D4）；链式基准（审计 E8）：内部 hp/san 游标——双通道同目标终态正确。
/// 事件生产（csharp-events spec §一 明示落本 step）：DamageCalculator 调用方。
/// </summary>
public sealed class ActionResolver
{
    private readonly GameData _data;
    private readonly CalibrationConfig _cal;
    private readonly IResponseResolver _responseResolver;
    private readonly DamageCalculator _damageCalculator;

    /// <summary>
    /// 构造。
    /// </summary>
    /// <param name="data">游戏数据（节点解析）。</param>
    /// <param name="cal">校准常量（伤害基础值等）。</param>
    /// <param name="responseResolver">响应窗口解析器（demo = Noop）。</param>
    /// <exception cref="ArgumentNullException">任一参数 null。</exception>
    public ActionResolver(GameData data, CalibrationConfig cal, IResponseResolver? responseResolver = null)
    {
        ArgumentNullException.ThrowIfNull(data);
        ArgumentNullException.ThrowIfNull(cal);
        _data = data;
        _cal = cal;
        _responseResolver = responseResolver ?? new NoopResponseResolver();
        _damageCalculator = new DamageCalculator(cal);
    }

    /// <summary>
    /// 结算声明行动并产出事件。
    /// </summary>
    /// <param name="actorIndex">行动者索引（事件 ActorId/Round 来源——round 取 state.Round，StepRound 已递增）。</param>
    /// <param name="action">声明行动（通道-动作配对校验：M1∈{Physical,Defend}、Broca∈{Mental}）。</param>
    /// <param name="state">当前战斗状态（只读）。</param>
    /// <param name="ctx">只读上下文（Rng——物理命中判定）。</param>
    /// <returns>事件列表（按 Order 序；Defend 无事件）。</returns>
    /// <exception cref="ArgumentNullException">参数 null。</exception>
    /// <exception cref="ArgumentOutOfRangeException">actorIndex 或 TargetId ∉ [0, Count)。</exception>
    /// <exception cref="ArgumentException">通道-动作配对违规（M1=MentalAttack、Broca=PhysicalAttack/Defend）。</exception>
    public IReadOnlyList<CombatEvent> Resolve(
        int actorIndex, CombatAction action, CombatState state, CombatContext ctx)
    {
        ArgumentNullException.ThrowIfNull(action);
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(ctx);
        if (actorIndex < 0 || actorIndex >= state.Participants.Count)
            throw new ArgumentOutOfRangeException(nameof(actorIndex));

        // 通道-动作配对校验（回合战斗流程 §2.1：M1 ∈ {Physical,Defend}、Broca ∈ {Mental}）
        if (action.M1?.Kind is ActionKind.MentalAttack)
            throw new ArgumentException("M1 通道不允许 MentalAttack（回合战斗流程 §2.1）", nameof(action));
        if (action.Broca is { Kind: not ActionKind.MentalAttack })
            throw new ArgumentException("Broca 通道仅允许 MentalAttack（回合战斗流程 §2.1）", nameof(action));

        var events = new List<CombatEvent>();
        // 链式基准（审计 E8）：per-target hp/san 游标（初值 = state 当前值；
        // 每事件结算后更新目标游标——同目标后事件 Before = 前事件 After；不同目标互不影响）
        var cursors = state.Participants.Select(p => (Hp: p.Hp, San: p.San)).ToArray();

        _ = _responseResolver.Resolve(action, state, ctx); // 响应窗口（demo Noop——调整事件留链路 feature）

        if (action.Order == ChannelOrder.M1First)
        {
            ResolveSlot(action.M1, cursors, actorIndex, state, ctx, events);
            ResolveSlot(action.Broca, cursors, actorIndex, state, ctx, events);
        }
        else
        {
            ResolveSlot(action.Broca, cursors, actorIndex, state, ctx, events);
            ResolveSlot(action.M1, cursors, actorIndex, state, ctx, events);
        }

        return events;
    }

    /// <summary>单槽结算（null = 无动作）。</summary>
    private void ResolveSlot(ActionSlot? slot, (float Hp, float San)[] cursors,
        int actorIndex, CombatState state, CombatContext ctx, List<CombatEvent> events)
    {
        if (slot is null)
            return;

        switch (slot.Kind)
        {
            case ActionKind.PhysicalAttack:
                events.Add(ResolvePhysical(slot, cursors, actorIndex, state, ctx));
                break;
            case ActionKind.MentalAttack:
                events.Add(ResolveMental(slot, cursors, actorIndex, state, ctx));
                break;
            case ActionKind.Defend:
                break; // 防御标记——TurnManager 读取 action 应用 IsDefending/CD（§5.2）
        }
    }

    /// <summary>物理结算（§5.1；miss 契约遵守 events §2.4）。</summary>
    private PhysicalDamageEvent ResolvePhysical(ActionSlot slot, (float Hp, float San)[] cursors,
        int actorIndex, CombatState state, CombatContext ctx)
    {
        var target = Target(state, slot.TargetId);
        var cursor = cursors[slot.TargetId];

        // 接线（plan §六 + §5.1）
        var toneBias = ToneBias(state.Participants[actorIndex].Tone, 0f, 0.3f, 0.5f, -0.3f); // attack_physical
        var motivationMod = Math.Clamp(toneBias, -1f, 1f);
        var tone = state.Participants[actorIndex].Tone;
        var forceMod = Math.Clamp(tone.DaSnc - 0.5f, 0f, 0.5f); // clamp(DA_SNc − baseline, 0, +50%)
        var gateBonus = state.Participants[actorIndex].Gates.GateSomatic;

        var (damage, hit) = _damageCalculator.CalcPhysicalDamage(
            _cal.BasePhysicalDamage, 0, forceMod, motivationMod, gateBonus,
            target.IsDefending, ctx.Rng);

        // 链式游标：HP 扣减（miss 不扣）
        var hpAfter = hit ? DamageCalculator.Round1(cursor.Hp - damage) : cursor.Hp;

        // miss 契约（events §2.4）：dealt=0 ∧ blocked==incoming>0（全额回避——B2 m=1.0 路径可达）；
        // hit 防御时减免 50% → 减免量 = 造成量（B4 简化）；IncomingDamage = dealt + blocked（f32 加法契约恒等）
        var dealt = hit ? damage : 0f;
        var blocked = hit ? (target.IsDefending ? damage : 0f) : damage;

        var ev = new PhysicalDamageEvent(state.Round, actorIndex, slot.TargetId)
        {
            Hit = hit,
            BaseDamage = _cal.BasePhysicalDamage,
            WeaponBonus = 0,
            ForceMod = forceMod,
            MotivationMod = motivationMod,
            GateBonus = gateBonus,
            DamageDealt = dealt,
            DamageBlocked = blocked,
            IncomingDamage = dealt + blocked,
            TargetHpBefore = cursor.Hp,
            TargetHpAfter = hpAfter,
            TargetHpMax = target.HpMax,
        };

        cursors[slot.TargetId] = (hpAfter, cursor.San); // 链式游标更新（目标）
        return ev;
    }

    /// <summary>精神结算（§5.1；永远命中）。</summary>
    private MentalDamageEvent ResolveMental(ActionSlot slot, (float Hp, float San)[] cursors,
        int actorIndex, CombatState state, CombatContext ctx)
    {
        var target = Target(state, slot.TargetId);
        var self = state.Participants[actorIndex];
        var cursor = cursors[slot.TargetId];

        var toneBias = ToneBias(self.Tone, 0f, 0.4f, 0f, -0.3f); // attack_mental
        var motivationMod = Math.Clamp(toneBias, -1f, 1f);
        var gateBonus = self.Gates.GateCognitive;
        var enemySanRatio = target.SanMax > 0f ? target.San / target.SanMax : 0f;

        var (sanDamage, hpDamage) = _damageCalculator.CalcMentalDamage(
            _cal.BaseMentalDamage, motivationMod, _cal.EndurancePassivePenalty, enemySanRatio, gateBonus);

        var sanAfter = DamageCalculator.Round1(cursor.San - sanDamage);
        var hpAfter = DamageCalculator.Round1(cursor.Hp - hpDamage);

        var ev = new MentalDamageEvent(state.Round, actorIndex, slot.TargetId)
        {
            SanDamage = sanDamage,
            HpDamage = hpDamage,
            MotivationMod = motivationMod,
            GateBonus = gateBonus,
            TargetSanBefore = cursor.San,
            TargetSanAfter = sanAfter,
            TargetSanMax = target.SanMax,
            TargetHpBefore = cursor.Hp,
            TargetHpAfter = hpAfter,
            TargetHpMax = target.HpMax,
        };

        cursors[slot.TargetId] = (hpAfter, sanAfter); // 链式游标更新（目标）
        return ev;
    }

    /// <summary>target 解析（Δ-06：ActionSlot.TargetId 语义由 Flow 层定义）。</summary>
    private static ParticipantState Target(CombatState state, int targetId)
    {
        if (targetId < 0 || targetId >= state.Participants.Count)
            throw new ArgumentOutOfRangeException(nameof(targetId));
        return state.Participants[targetId];
    }

    /// <summary>tone_bias(role) = Σ w_t × (tone_t − baseline_t)（NPC AI §3.3；baseline 常量 demo 简化）。</summary>
    private static float ToneBias(ToneState tone, float wNe, float wVta, float wSnc, float wHt5) =>
        wNe * (tone.Ne - 0.3f)
        + wVta * (tone.DaVta - 0.4f)
        + wSnc * (tone.DaSnc - 0.5f)
        + wHt5 * (tone.Ht5 - 0.5f);
}
