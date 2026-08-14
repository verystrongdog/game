using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Entity;

/// <summary>
/// 可变战斗状态——csharp-flow spec@v1.2 §二 2.2（plan §5.1 L3 实体）。
/// 内部持有参与者数组（record 替换语义），对外只读；实体自己 Apply 引擎产出（框架 D1）。
/// 初始化：WC 状态置静息不动点（内部 30 回合静息 trace——运行时状态模型 §7.3，
/// 对齐 csharp-tone AC-15 方法）；Gurney 从 0 起步（§7.3 实测首回合即收敛）。
/// </summary>
public sealed class CombatState
{
    private readonly ParticipantState[] _participants;
    private readonly int[] _teams;
    private readonly List<TurnResult> _history = [];
    private readonly float[][] _sPending;
    private readonly LoopSalience[] _salience;

    /// <summary>参与者状态（读快照数组——不可经此替换元素）。</summary>
    public IReadOnlyList<ParticipantState> Participants => _participants;

    /// <summary>teams[p] == teams[q] ⇔ p、q 同队（D1/D2 分流与结束条件数据源——审计 E1）。</summary>
    public IReadOnlyList<int> Teams => _teams;

    /// <summary>CSTC 环路 salience（Phase 1 CstcGating 输出——Phase 3 速度重算消费；ParticipantState 无此字段，CombatState 持有）。</summary>
    public IReadOnlyList<LoopSalience> Salience => _salience;

    /// <summary>当前回合数（internal set——TurnManager 每回合递增，审计 E6）。</summary>
    public int Round { get; internal set; }

    /// <summary>回合结果历史（只读集合；追加走 internal AddTurnResult——审计 Δ-04）。</summary>
    public IReadOnlyList<TurnResult> History => _history;

    /// <summary>s 累计槽（per-participant float[69]——Phase 4 累加、Phase 1 注入后清零；集合只读，审计 I3）。</summary>
    public IReadOnlyList<float[]> SPending => _sPending;

    private CombatState(ParticipantState[] participants, int[] teams, float[][] sPending)
    {
        _participants = participants;
        _teams = teams;
        _sPending = sPending;
        // salience 初值零——Phase 1 首次 CstcGating.Step 后写入（首回合速度 = Phase 1 后状态，运行时状态模型 §7.3）
        _salience = Enumerable.Repeat(
            new LoopSalience(new LoopValue(0f, 0f), new LoopValue(0f, 0f), new LoopValue(0f, 0f)),
            participants.Length).ToArray();
    }

    /// <summary>
    /// 创建战斗状态——WC 置静息不动点（30 回合 trace：tone=baseline、s=0）。
    /// </summary>
    /// <param name="initial">初始参与者（HP/SAN 由调用方提供；tone 必须 = baseline——否则不动点不匹配，未定义行为）。</param>
    /// <param name="teams">teams[p] == teams[q] ⇔ 同队（Count 必须 == initial.Count）。</param>
    /// <param name="data">游戏数据（WMatrixBuilder.Build 消费）。</param>
    /// <param name="cal">校准常量（WcDynamics 消费）。</param>
    /// <exception cref="ArgumentNullException">任一参数 null。</exception>
    /// <exception cref="ArgumentException">teams.Count != initial.Count。</exception>
    public static CombatState Create(
        IReadOnlyList<ParticipantState> initial, IReadOnlyList<int> teams,
        GameData data, CalibrationConfig cal)
    {
        ArgumentNullException.ThrowIfNull(initial);
        ArgumentNullException.ThrowIfNull(teams);
        ArgumentNullException.ThrowIfNull(data);
        ArgumentNullException.ThrowIfNull(cal);
        if (teams.Count != initial.Count)
            throw new ArgumentException($"teams.Count({teams.Count}) != initial.Count({initial.Count})", nameof(teams));

        var resting = RestingWc(data, cal);
        var participants = new ParticipantState[initial.Count];
        var sPending = new float[initial.Count][];
        for (var p = 0; p < initial.Count; p++)
        {
            participants[p] = initial[p] with { Wc = resting };
            sPending[p] = new float[resting.A.Length];
        }
        return new CombatState(participants, teams.ToArray(), sPending);
    }

    /// <summary>30 回合静息 trace 得 WC 不动点（tone=baseline、s=0；对齐 csharp-tone AC-15 方法）。</summary>
    private static WcState RestingWc(GameData data, CalibrationConfig cal)
    {
        var w = WMatrixBuilder.Build(data);
        var a = new WcState(Enumerable.Repeat(0.10f, w.RowFids.Length).ToArray());
        var tone = new ToneState { Ne = 0.3f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.5f };
        var zero = new float[69];
        for (var i = 0; i < 30; i++)
        {
            var b = CorticalBias.Compute(tone, data);
            a = WcDynamics.Step(a, b, zero, w);
        }
        return a;
    }

    /// <summary>HP/SAN 设为事件字段结算后值（事件字段搬运语义——ActionResolver 已按链式基准推算，无二次计算）。</summary>
    public void ApplyDamage(int p, float hpAfter, float sanAfter)
        => _participants[p] = _participants[p] with { Hp = hpAfter, San = sanAfter };

    /// <summary>替换 tone（EventProcessor 输出）。</summary>
    public void ApplyTone(int p, ToneState tone)
        => _participants[p] = _participants[p] with { Tone = tone };

    /// <summary>Phase 1 全链替换（WC/CSTC 输出 + salience 存 CombatState 槽）。</summary>
    public void ApplyGurney(int p, WcState a, GurneyState gurney, GateState gates, LoopSalience salience)
    {
        _participants[p] = _participants[p] with { Wc = a, Gurney = gurney, Gates = gates };
        _salience[p] = salience;
    }

    /// <summary>防御状态与 CD 设置。</summary>
    public void ApplyDefense(int p, bool defending, int cd)
        => _participants[p] = _participants[p] with { IsDefending = defending, DefendCd = cd };

    /// <summary>自己窗口开始：CD 递减（DefendCd/EnduranceActiveCd）；IsDefending=false（Q3=A 暴露一轮）。</summary>
    public void TickWindow(int p)
    {
        var s = _participants[p];
        _participants[p] = s with
        {
            DefendCd = Math.Max(0, s.DefendCd - 1),
            EnduranceActiveCd = Math.Max(0, s.EnduranceActiveCd - 1),
            IsDefending = false,
        };
    }

    /// <summary>s 累计到 SPending（EventProcessor SensoryAccum 累加）。</summary>
    public void AccumulateS(int p, float[] s)
    {
        var acc = _sPending[p];
        for (var j = 0; j < acc.Length; j++)
            acc[j] += s[j];
    }

    /// <summary>按事件序搬运 DamageEvent 的 TargetHpAfter/TargetSanAfter（链式基准下事件字段已自洽）。</summary>
    public void ApplyEvents(IReadOnlyList<CombatEvent> events)
    {
        foreach (var ev in events)
        {
            switch (ev)
            {
                case PhysicalDamageEvent ph:
                    _participants[ph.TargetId] = _participants[ph.TargetId] with { Hp = ph.TargetHpAfter };
                    break;
                case MentalDamageEvent me:
                    _participants[me.TargetId] = _participants[me.TargetId] with
                    {
                        San = me.TargetSanAfter,
                        Hp = me.TargetHpAfter,
                    };
                    break;
            }
        }
    }

    /// <summary>回合结果追加（内部——TurnManager Phase 5 调用）。</summary>
    internal void AddTurnResult(TurnResult result) => _history.Add(result);
}
