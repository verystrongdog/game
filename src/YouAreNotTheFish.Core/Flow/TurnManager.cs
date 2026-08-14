using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Engine;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Flow;

/// <summary>
/// 五阶段回合管线编排——csharp-flow spec@v1.2 §三 3.4/3.5（plan §5.2 + 回合战斗流程 §四 + 运行时状态模型 §7.1）。
/// 每步调 L2 组件 + state.Apply；产 TurnResult（Round + 全部事件 + 快照）。
/// 确定性：同种子同输入（含 provider 行动序列）→ 逐位同 TurnResult。
/// </summary>
public sealed class TurnManager
{
    private readonly GameData _data;
    private readonly CalibrationConfig _cal;
    private readonly IActionProvider _actionProvider;
    private readonly ActionResolver _resolver;
    private readonly EventProcessor _eventProcessor;
    private readonly SpeedScoreCalculator _speedScore;
    private readonly CstcGating _cstcGating;
    private readonly WMatrix _wMatrix;

    /// <summary>
    /// 构造。
    /// </summary>
    /// <param name="data">游戏数据。</param>
    /// <param name="cal">校准常量。</param>
    /// <param name="actionProvider">行动来源（demo = NpcActionProvider；测试可注入固定行动）。</param>
    /// <exception cref="ArgumentNullException">任一参数 null。</exception>
    public TurnManager(GameData data, CalibrationConfig cal, IActionProvider actionProvider)
    {
        ArgumentNullException.ThrowIfNull(data);
        ArgumentNullException.ThrowIfNull(cal);
        ArgumentNullException.ThrowIfNull(actionProvider);
        _data = data;
        _cal = cal;
        _actionProvider = actionProvider;
        _resolver = new ActionResolver(data, cal);
        _eventProcessor = new EventProcessor(data.Wsensory, cal);
        _speedScore = new SpeedScoreCalculator(data, cal);
        _cstcGating = new CstcGating(data);
        _wMatrix = WMatrixBuilder.Build(data);
    }

    /// <summary>
    /// 推进一回合（五阶段）。
    /// </summary>
    /// <param name="state">可变战斗状态（Round 递增、参与者/SPending/History 更新）。</param>
    /// <param name="ctx">只读上下文（Rng——速度破平 + 物理命中 + NPC Softmax）。</param>
    /// <exception cref="ArgumentNullException">state/ctx null。</exception>
    public TurnResult StepRound(CombatState state, CombatContext ctx)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(ctx);

        state.Round += 1; // E6：Round 递增显式化
        var round = state.Round;

        // ---- Phase 1: 情境更新（运行时状态模型 §7.1 步骤 1-5）----
        for (var p = 0; p < state.Participants.Count; p++)
        {
            // 步骤 1：tone 纯衰减一步（events §5.5.3「衰减是 step 10 Phase 1 的职责」；事件接收者 Phase 4 已注入，
            // 此处统一衰减步进——events 锚点为 Phase 4 注入瞬间值，回合末 = 注入 + 衰减两步合成）
            var tone = ToneUpdater.Step(state.Participants[p].Tone, new float[4], _cal);
            state.ApplyTone(p, tone);

            // 步骤 2-5：b_j → WC 更新（s = 上回合累计，注入后清零）→ CSTC
            var b = CorticalBias.Compute(tone, _data);
            var aNew = WcDynamics.Step(state.Participants[p].Wc, b, state.SPending[p], _wMatrix);
            Array.Clear(state.SPending[p], 0, state.SPending[p].Length);

            var (gurney, gates, salience) = _cstcGating.Step(aNew, tone, state.Participants[p].Gurney);
            state.ApplyGurney(p, aNew, gurney, gates, salience);
        }

        // ---- Phase 2: 继承（连续状态原样带入，不递减 CD）→ 无操作 ----

        // ---- Phase 3: 速度重算（仅存活参与者；审计 E7）----
        var alive = new List<int>();
        var scores = new List<float>();
        for (var p = 0; p < state.Participants.Count; p++)
        {
            if (state.Participants[p].Hp <= 0f)
                continue;
            alive.Add(p);
            var ps = state.Participants[p];
            var components = _speedScore.ComputeComponents(
                ps.Wc, state.Salience[p], ps.Gurney, ps.IsDefending);
            scores.Add(_speedScore.ComputeScore(components, new SpeedWeights(1f / 3f, 1f / 3f, 1f / 3f)));
        }
        var localOrder = TurnOrderBuilder.BuildOrder(scores.ToArray(), ctx.Rng);
        var order = localOrder.Select(i => alive[i]).ToArray(); // 全局索引映射

        // ---- Phase 4: 按序执行 ----
        var events = new List<CombatEvent>();
        foreach (var p in order)
        {
            if (state.Participants[p].Hp <= 0f)
                continue; // 窗口前检查（审计 E7/F4）：被击杀者跳过

            state.TickWindow(p); // 0. 窗口开始：CD tick + IsDefending=false（Q3）
            var action = _actionProvider.GetAction(p, state, ctx); // 1. 行动选择

            var evs = _resolver.Resolve(p, action, state, ctx); // 2-4. 声明→响应(stub)→结算（链式基准）
            state.ApplyEvents(evs); // HP/SAN = 事件字段（搬运）
            if (action.M1?.Kind == ActionKind.Defend)
                state.ApplyDefense(p, true, 1); // 防御标记（§5.2）

            // Q4=A：Panic 跨越检测——逐事件判定 + 快照收集后合并同批（v1.2：IReadOnlyList 无 Add / foreach 中 Add 抛异常）
            var evsAll = evs.ToArray();
            var panics = new List<CombatEvent>();
            foreach (var ev in evsAll)
            {
                if (ev is MentalDamageEvent me
                    && me.TargetSanBefore > me.TargetSanAfter
                    && me.TargetSanBefore >= 0.30f * me.TargetSanMax
                    && me.TargetSanAfter < 0.30f * me.TargetSanMax)
                {
                    panics.Add(new StatusChangeEvent(round, me.TargetId, me.TargetId)
                    {
                        Kind = StatusKind.Panic,
                        Entered = true,
                        SanBefore = me.TargetSanBefore,
                        SanAfter = me.TargetSanAfter,
                        SanMax = me.TargetSanMax,
                    });
                }
            }
            var batch = evsAll.Concat(panics).ToArray(); // 同批一次 ProcessEvents（B4+C1 Σδ 一次 Step）

            var result = _eventProcessor.ProcessEvents(batch, state.Participants, state.Teams); // 5. δ/s 派生
            for (var p2 = 0; p2 < state.Participants.Count; p2++)
            {
                state.ApplyTone(p2, result.States[p2].Tone);
                state.AccumulateS(p2, result.SensoryAccum[p2]);
            }
            events.AddRange(batch);

            // 6. HP=0 → 移除队列（跳过剩余窗口）+ D 广播实时。
            // 修复（实现自审）：检查对象为**结算后被击杀的任一参与者**（非仅行动者 p——
            // 被他人击杀的目标 HP≤0 也须生产 Downed；原检查 state.Participants[p] 只覆盖行动者自己）
            foreach (var dp in Enumerable.Range(0, state.Participants.Count))
            {
                if (state.Participants[dp].Hp <= 0f
                    && !events.OfType<StatusChangeEvent>().Any(e => e.Kind == StatusKind.Downed && e.ActorId == dp))
                {
                    var downed = new StatusChangeEvent(round, dp, dp) { Kind = StatusKind.Downed, Entered = true };
                    var dResult = _eventProcessor.ProcessEvents([downed], state.Participants, state.Teams);
                    for (var p2 = 0; p2 < state.Participants.Count; p2++)
                    {
                        state.ApplyTone(p2, dResult.States[p2].Tone);
                        state.AccumulateS(p2, dResult.SensoryAccum[p2]);
                    }
                    events.Add(downed);
                }
            }
        }

        // ---- Phase 5: 回合收束 ----
        var turnResult = new TurnResult(round, events, state.Participants);
        state.AddTurnResult(turnResult);
        return turnResult;
    }

    /// <summary>
    /// 结束判定（§5.5）——一方全灭（Hp≤0 ∨ San≤0 同队全员）或回合上限。
    /// </summary>
    /// <param name="state">当前战斗状态。</param>
    /// <exception cref="ArgumentNullException">state null。</exception>
    public bool IsOver(CombatState state)
    {
        ArgumentNullException.ThrowIfNull(state);
        if (state.Round >= _cal.MaxRounds)
            return true;

        // 任一方全员 Hp≤0 ∨ San≤0 → 结束
        foreach (var team in state.Teams.Distinct())
        {
            var members = Enumerable.Range(0, state.Participants.Count)
                .Where(p => state.Teams[p] == team)
                .ToList();
            var down = members.All(p =>
                state.Participants[p].Hp <= 0f || state.Participants[p].San <= 0f);
            if (down)
                return true;
        }
        return false;
    }
}
