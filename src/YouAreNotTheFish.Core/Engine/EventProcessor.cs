using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// 战斗事件 → δ（tone 脉冲）+ s（皮层感官输入）派生器——csharp-events spec@v1.2.2。
/// 消费 CombatEvents，按 运行时状态模型 §5.5 δ pattern 表 + magnitude 表与 §4.5 s = W_sensory × α
/// 派生每参与者 δ 发射（Σ 聚合后恰好一次 ToneUpdater.Step）与 s 增量（float[69]，Phase 1 注入）。
///
/// 派生规则表（10 demo 事件）：A1/A2（物理攻击者）、A5/B1/B2（物理承受者三路分区，Q2=A）、
/// A4（精神攻击者）、B4（精神承受者）、C1（恐慌跨越）、D1/D2（倒下广播）。
/// 偏差 B1-B5（spec §八）：A3/B3/A6/A7 不落地（B1）；A2 m 恒 0（B2）；States 全参与者副本（B3）；
/// ∞ 显式防御（B4）；A4 expected ≤ 0 落 skip（B5）。
/// 计算序契约（spec §五）：Σ 事件序 → 一次 Step（参与者升序）；s 模态升序 k、节点升序 j、跨事件累加。
/// 确定性：无 static 可变状态、无内部缓存；同输入（含事件序）→ 逐位同输出。
/// </summary>
public sealed class EventProcessor
{
    private readonly WsensoryMatrix _wsensory;
    private readonly CalibrationConfig _cal;

    /// <summary>
    /// 构造。
    /// </summary>
    /// <param name="wsensory">W_sensory 矩阵（RegionIds = canonical 69，wmatrix 约束 C1 承接——数据层保证，不做形状校验）。</param>
    /// <param name="cal">校准常量（ExpectedDamage/BaseMentalDamage/EndurancePassivePenalty 消费方）。</param>
    /// <exception cref="ArgumentNullException">wsensory 或 cal 为 null。</exception>
    public EventProcessor(WsensoryMatrix wsensory, CalibrationConfig cal)
    {
        ArgumentNullException.ThrowIfNull(wsensory);
        ArgumentNullException.ThrowIfNull(cal);
        _wsensory = wsensory;
        _cal = cal;
    }

    /// <summary>
    /// 处理一个窗口的全部事件——每参与者 Σδ（事件序）→ 恰好一次 ToneUpdater.Step（零向量不调用）→
    /// 打包 States 副本；s 按事件序累积 → SensoryAccum 增量。
    /// </summary>
    /// <param name="events">窗口事件（输入序 = 累加序）。HealEvent/LinkGrowthEvent no-op（偏差注）。</param>
    /// <param name="states">结算后、δ 注入前的参与者状态（HP/SAN 已含本轮结算；Tone 为待注入态）。
    /// 信任事件字段，不重算 HP/SAN 变化。</param>
    /// <param name="teams">int[]，teams[p]==teams[q] ⇔ p、q 同队（D1/D2 分流用）。</param>
    /// <returns>EventProcessingResult：States（输入副本 + Tone 注入）、SensoryAccum（每参与者 float[69] s 增量）。</returns>
    /// <exception cref="ArgumentNullException">events/states/teams 任一为 null。</exception>
    /// <exception cref="ArgumentException">teams.Count != states.Count；任一事件 ActorId/TargetId ∉ [0, states.Count)。</exception>
    /// <remarks>
    /// 未定义行为：违反 §二 2.4 契约的字段组合（NaN/∞ 传播可能——δ 通道有天然/显式防御、s 通道 A 类恒发）；
    /// states/teams 元素为 null（NRE）；类型集封闭于 5 个具体子类。
    /// </remarks>
    public EventProcessingResult ProcessEvents(
        IReadOnlyList<CombatEvent> events,
        IReadOnlyList<ParticipantState> states,
        IReadOnlyList<int> teams)
    {
        ArgumentNullException.ThrowIfNull(events);
        ArgumentNullException.ThrowIfNull(states);
        ArgumentNullException.ThrowIfNull(teams);
        if (teams.Count != states.Count)
            throw new ArgumentException($"teams.Count({teams.Count}) != states.Count({states.Count})", nameof(teams));

        var count = states.Count;
        foreach (var ev in events)
        {
            if (ev.ActorId < 0 || ev.ActorId >= count)
                throw new ArgumentException($"事件 ActorId({ev.ActorId}) ∉ [0, {count})", nameof(events));
            if (ev.TargetId < 0 || ev.TargetId >= count)
                throw new ArgumentException($"事件 TargetId({ev.TargetId}) ∉ [0, {count})", nameof(events));
        }

        var deltaSum = new float[count][];
        var sensoryAcc = new float[count][];
        for (var p = 0; p < count; p++)
        {
            deltaSum[p] = new float[4];
            sensoryAcc[p] = new float[_wsensory.Matrix.Length];
        }

        foreach (var ev in events)
        {
            switch (ev)
            {
                case PhysicalDamageEvent ph:
                    DerivePhysical(ph, deltaSum, sensoryAcc);
                    break;
                case MentalDamageEvent me:
                    DeriveMental(me, deltaSum, sensoryAcc);
                    break;
                case StatusChangeEvent st:
                    DeriveStatus(st, deltaSum, sensoryAcc, states, teams);
                    break;
                case HealEvent:
                case LinkGrowthEvent:
                    break; // no-op（spec §五 5.2：无 δ/s 发射）
            }
        }

        var resultStates = new ParticipantState[count];
        for (var p = 0; p < count; p++)
        {
            var sum = deltaSum[p];
            var state = states[p];
            if (sum[0] != 0f || sum[1] != 0f || sum[2] != 0f || sum[3] != 0f)
                resultStates[p] = state with { Tone = ToneUpdater.Step(state.Tone, sum, _cal) };
            else
                resultStates[p] = state; // 零向量不调用 Step——tone 逐位同输入（偏差 B3）
        }

        return new EventProcessingResult(resultStates, sensoryAcc);
    }

    /// <summary>
    /// 物理伤害事件派生：攻击者 A1/A2 + 承受者三路分区 A5/B1/B2（Q2=A，独立派生）。
    /// 承受者派生不豁免 HP=0（spec §五 5.2 W-e：击杀窗口照收——仅 D 广播排除倒者）。
    /// </summary>
    private void DerivePhysical(PhysicalDamageEvent ph, float[][] deltaSum, float[][] sensoryAcc)
    {
        // 攻击者视角（A1/A2，A 类 m_α=1.0）
        if (ph.Hit)
        {
            var m = ph.DamageDealt / _cal.ExpectedDamage; // A1：§5.3.1，分母消费常量（W-a）
            Emit(deltaSum, sensoryAcc, ph.ActorId, m, new[] { 0, 1, 1, 0 }, new[] { 1, 0, 1, 0, 0, 0 }, 1.0f);
        }
        else
        {
            // A2：m 恒 0（偏差 B2——miss 无实际伤害；防御 producer 误填 dealt）
            Emit(deltaSum, sensoryAcc, ph.ActorId, 0f, new[] { 0, -1, 0, 0 }, new[] { 1, 0, 1, 0, 0, 0 }, 1.0f);
        }

        // 承受者视角（三路分区）
        if (ph.Hit && ph.DamageBlocked > 0f)
        {
            // A5：δ m=blocked/incoming（§5.3.3）；s m_α=1.0（A 类恒发，W-c）
            var m = ph.DamageBlocked / ph.IncomingDamage;
            Emit(deltaSum, sensoryAcc, ph.TargetId, m, new[] { 0, 0, 0, 1 }, new[] { 0, 0, 1, 0, 0, 0 }, 1.0f);
        }
        else if (ph.Hit)
        {
            // B1：§5.3.4，|ΔHP|/HP_max（After − Before 序写死）
            var m = MathF.Abs(ph.TargetHpAfter - ph.TargetHpBefore) / ph.TargetHpMax;
            Emit(deltaSum, sensoryAcc, ph.TargetId, m, new[] { 1, 0, 0, -1 }, new[] { 1, 0, 1, 1, 0, 0 }, m);
        }
        else
        {
            // B2：§5.3.3，blocked/incoming（契约下恒 1.0）
            var m = ph.DamageBlocked / ph.IncomingDamage;
            Emit(deltaSum, sensoryAcc, ph.TargetId, m, new[] { 0, 0, 0, 1 }, new[] { 1, 0, 1, 0, 0, 0 }, m);
        }
    }

    /// <summary>
    /// 精神伤害事件派生：攻击者 A4 + 承受者 B4。
    /// </summary>
    private void DeriveMental(MentalDamageEvent me, float[][] deltaSum, float[][] sensoryAcc)
    {
        // A4：§5.3.2，expected = BaseMentalDamage×(1+mot) − EndurancePassivePenalty（先乘后减，f32 序）
        var expected = (float)_cal.BaseMentalDamage * (1f + me.MotivationMod) - _cal.EndurancePassivePenalty;
        var mA4 = me.SanDamage / expected;
        Emit(deltaSum, sensoryAcc, me.ActorId, mA4, new[] { 0, 1, 0, 0 }, new[] { 0, 0, 0, 0, 1, 1 }, 1.0f);

        // B4：§5.3.5，|ΔSAN|/SAN_max（只消费差值对 + 分母，不消费 SanDamage——W-d 字段语义契约）
        var mB4 = MathF.Abs(me.TargetSanAfter - me.TargetSanBefore) / me.TargetSanMax;
        Emit(deltaSum, sensoryAcc, me.TargetId, mB4, new[] { 1, 0, 0, -1 }, new[] { 0, 0, 0, 1, 1, 1 }, mB4);
    }

    /// <summary>
    /// 状态变化事件派生：C1（自身恐慌跨越，guard 全条件）+ D1/D2（倒下广播，观察者）。
    /// </summary>
    private void DeriveStatus(StatusChangeEvent st, float[][] deltaSum, float[][] sensoryAcc,
        IReadOnlyList<ParticipantState> states, IReadOnlyList<int> teams)
    {
        if (!st.Entered)
            return; // 脱离方向无表行

        if (st.Kind == StatusKind.Panic)
        {
            // C1 guard（§5.5.1，Q1=A 处理器实现）：ΔSAN<0 且 old≥30%（含端）且 new<30%（严格）
            if (st.SanBefore > st.SanAfter
                && st.SanBefore >= 0.30f * st.SanMax
                && st.SanAfter < 0.30f * st.SanMax)
            {
                Emit(deltaSum, sensoryAcc, st.ActorId, 1.0f, new[] { 1, 0, 0, -1 }, new[] { 0, 0, 0, 1, 0, 0 }, 1.0f);
            }
        }
        else if (st.Kind == StatusKind.Downed)
        {
            // D1/D2 广播（§5.5.2）：观察者 p ≠ ActorId ∧ states[p].Hp > 0（输入 states 快照判定）；
            // 倒者排除显式化；多倒下者各自广播，Σ 自然叠加。
            for (var p = 0; p < states.Count; p++)
            {
                if (p == st.ActorId || states[p].Hp <= 0f)
                    continue;
                var pattern = teams[p] == teams[st.ActorId] ? new[] { 1, -1, 0, -1 } : new[] { 0, 1, 0, 1 };
                Emit(deltaSum, sensoryAcc, p, 1.0f, pattern, new[] { 1, 1, 0, 0, 1, 0 }, 1.0f);
            }
        }
    }

    /// <summary>
    /// 单视角派生：δ 与 s 按各自 emit 判据独立累加。
    /// δ：m ≥ 0.01f 且有限（NaN 天然落 skip——NaN>=0.01f 为 False；∞ 显式防御，偏差 B4）。
    /// s：m_α ≥ 0.01f 且有限（A 类 m_α=1.0 恒发，独立于 δ 通道——§5.3.7）。
    /// </summary>
    private void Emit(float[][] deltaSum, float[][] sensoryAcc, int p,
        float m, int[] deltaPattern, int[] alphaPattern, float mAlpha)
    {
        // δ 通道
        if (m >= 0.01f && !float.IsInfinity(m))
        {
            var acc = deltaSum[p];
            for (var k = 0; k < 4; k++)
            {
                if (deltaPattern[k] != 0)
                    acc[k] += deltaPattern[k] == 1 ? m : -m;
            }
        }

        // s 通道（m_α 独立判定）
        if (mAlpha >= 0.01f && !float.IsInfinity(mAlpha) && !float.IsNaN(mAlpha))
        {
            // α[k] = pattern × m_α（pattern 0 → 0）；s_event[j] = Σ_{k: W[j][k]=1} α[k]（k 模态升序）
            // sAcc 累加：节点 j 升序（spec §5.4 f32 结合序契约）
            var acc = sensoryAcc[p];
            var matrix = _wsensory.Matrix;
            for (var j = 0; j < acc.Length; j++)
            {
                var row = matrix[j];
                float s = 0f;
                for (var k = 0; k < 6; k++)
                {
                    if (row[k] != 0 && alphaPattern[k] != 0)
                        s += mAlpha; // pattern=1 → m_α（W∈{0,1}，乘为精确；α=1×m_α）
                }
                if (s != 0f)
                    acc[j] += s;
            }
        }
    }
}
