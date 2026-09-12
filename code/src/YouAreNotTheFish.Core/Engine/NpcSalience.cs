using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Entity;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// NPC 行动选择——demo 版 3 基础行动 salience 竞争（plan §4.8 [NEW]，正式 skill 系统接入后替换）。
/// Affordance Competition 的 demo 落地（NPC AI §3.2/§3.3/§3.4）：Salience = mean(节点值) × gate × (1 + tone_bias)。
/// 确定性：纯函数，无 static 可变状态；Softmax 抽样消费 ctx.Rng——同种子同输出。
/// 签名（审计 E3/F6）：selfIndex + state（Teams/全体参与者）——目标选择数据在位。
/// </summary>
public static class NpcSalience
{
    // tone baseline 常量（运行时状态模型 §5.4——demo 简化，NPC AI §4.1 性格偏移留全量）
    private const float BaselineNe = 0.3f;
    private const float BaselineDaVta = 0.4f;
    private const float BaselineDaSnc = 0.5f;
    private const float BaselineHt5 = 0.5f;

    // 行动→节点 fid（canonical 69 RegionIds 解析，构造期每次解析——无 static 缓存）。
    // plan §4.8 节点为 dk_name——functional_id 映射（2026-08-14 数据落地）：
    // rostralmiddlefrontal → RostralMiddleFrontalDLPFC（dlPFC，dk 多对一取主）；
    // caudalanteriorcingulate → AnteriorCingulateCortex（cACC 拆分两 fid 取首）；
    // parsopercularis → ParsOpercularis。
    private static readonly string[] PhysicalNodes = ["Precentral"];
    private static readonly string[] MentalNodes =
        ["RostralMiddleFrontalDLPFC", "ParsOpercularis", "AnteriorCingulateCortex"];
    private static readonly string[] DefendNodes = ["Insula", "Amygdala"];

    /// <summary>
    /// 为自身参与者选择行动。
    /// </summary>
    /// <param name="selfIndex">行动者索引。</param>
    /// <param name="state">当前战斗状态（只读）。</param>
    /// <param name="ctx">只读上下文（Data——节点解析；Rng——Softmax 抽样）。</param>
    /// <exception cref="ArgumentNullException">state/ctx null。</exception>
    /// <exception cref="ArgumentOutOfRangeException">selfIndex ∉ [0, Count)。</exception>
    public static CombatAction SelectAction(int selfIndex, CombatState state, CombatContext ctx)
    {
        ArgumentNullException.ThrowIfNull(state);
        ArgumentNullException.ThrowIfNull(ctx);
        if (selfIndex < 0 || selfIndex >= state.Participants.Count)
            throw new ArgumentOutOfRangeException(nameof(selfIndex));

        var self = state.Participants[selfIndex];
        var targetId = FirstEnemy(selfIndex, state);

        // 3 候选 salience（plan §4.8 表；Putamen 代理 = a_SD1_somatic——plan §十三-4 同款；Insula/Amygdala 直读）
        var rows = ResolveRows(ctx.Data, PhysicalNodes, MentalNodes, DefendNodes);
        var a = self.Wc.A;
        var gates = self.Gates;

        float physical = Mean(
            a[rows.Physical[0]],
            self.Gurney.Somatic[0]) // Putamen 代理（a_SD1_somatic）
            * gates.GateSomatic
            * (1f + ToneBias(self.Tone, 0f, 0.3f, 0.5f, -0.3f)); // attack_physical（NPC AI §3.3）

        float mental = Mean(
            a[rows.Mental[0]], a[rows.Mental[1]], a[rows.Mental[2]])
            * gates.GateCognitive
            * (1f + ToneBias(self.Tone, 0f, 0.4f, 0f, -0.3f)); // attack_mental

        float defend = Mean(
            a[rows.Defend[0]], a[rows.Defend[1]])
            * gates.GateLimbic
            * (1f + ToneBias(self.Tone, 0.4f, -0.2f, 0f, 0.4f)); // defend

        // Softmax 选择（T = T_base + T_SAN；判定序 SAN==0 最先——v1.2 Δ审计 F4）
        var choice = Pick(physical, mental, defend, self.San, self.SanMax, ctx);
        return choice switch
        {
            0 => new CombatAction { M1 = new ActionSlot { Kind = ActionKind.PhysicalAttack, TargetId = targetId }, Order = ChannelOrder.M1First },
            1 => new CombatAction { Broca = new ActionSlot { Kind = ActionKind.MentalAttack, TargetId = targetId }, Order = ChannelOrder.M1First },
            _ => new CombatAction { M1 = new ActionSlot { Kind = ActionKind.Defend, TargetId = targetId }, Order = ChannelOrder.M1First },
        };
    }

    /// <summary>目标 = 第一个异队参与者（[NEW] demo 简化——1v1 即对方；argmax 竞争留 Affordance Competition 全量）。</summary>
    private static int FirstEnemy(int selfIndex, CombatState state)
    {
        var selfTeam = state.Teams[selfIndex];
        for (var p = 0; p < state.Participants.Count; p++)
            if (p != selfIndex && state.Teams[p] != selfTeam)
                return p;
        // 无敌人（单方全灭前序）——回退自身（ActionResolver 目标校验会拦截非法使用）
        return selfIndex;
    }

    /// <summary>tone_bias(role) = Σ w_t × (tone_t − baseline_t)（NPC AI §3.3；tone 处基线时 = 0）。</summary>
    private static float ToneBias(ToneState tone, float wNe, float wVta, float wSnc, float wHt5) =>
        wNe * (tone.Ne - BaselineNe)
        + wVta * (tone.DaVta - BaselineDaVta)
        + wSnc * (tone.DaSnc - BaselineDaSnc)
        + wHt5 * (tone.Ht5 - BaselineHt5);

    /// <summary>Softmax 抽样（T = T_base + T_SAN；SAN==0 → 均匀随机不经 Softmax——防 exp(0/∞)）。</summary>
    private static int Pick(float physical, float mental, float defend, float san, float sanMax, CombatContext ctx)
    {
        if (san <= 0f)
        {
            // T=∞ 均匀随机（思维断裂——NPC AI §3.4）
            var roll = ctx.Rng.NextFloat();
            return roll < 1f / 3f ? 0 : roll < 2f / 3f ? 1 : 2;
        }

        float tSan = san < 0.30f * sanMax ? 0.30f
            : san < 0.60f * sanMax ? 0.10f
            : 0f;
        float t = ctx.Calibration.TBase + tSan;

        var s = new[] { physical, mental, defend };
        var exp = new[] { MathF.Exp(s[0] / t), MathF.Exp(s[1] / t), MathF.Exp(s[2] / t) };
        var sum = exp[0] + exp[1] + exp[2];

        var weighted = ctx.Rng.NextFloat() * sum;
        if (weighted < exp[0]) return 0;
        if (weighted < exp[0] + exp[1]) return 1;
        return 2;
    }

    private static float Mean(params float[] values)
    {
        float sum = 0f;
        foreach (var v in values) sum += v;
        return sum / values.Length;
    }

    /// <summary>fid → RegionIds 行号解析（镜像 SpeedScoreCalculator 构造；数据契约由数据层双射锁定）。</summary>
    private static (int[] Physical, int[] Mental, int[] Defend) ResolveRows(
        GameData data, string[] physical, string[] mental, string[] defend)
    {
        int Find(string fid)
        {
            var ids = data.Wsensory.RegionIds;
            for (var i = 0; i < ids.Length; i++)
                if (ids[i] == fid) return i;
            throw new KeyNotFoundException($"RegionIds 无 {fid}");
        }

        return (physical.Select(Find).ToArray(), mental.Select(Find).ToArray(), defend.Select(Find).ToArray());
    }
}
