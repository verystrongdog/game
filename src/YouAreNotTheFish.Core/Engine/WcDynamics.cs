using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// WC 69 节点单步动力学（csharp-engine plan §十一 step 4）——spec@v1.1（.scratch/csharp-wc-dynamics/design/spec.md）。
/// 职责：运行时状态模型 Layer 1 每回合 Phase 1 步骤 3 的一轮（Δ=1.0 秒）动力学更新。
/// 纯函数：无 static 可变状态、无 RNG、同输入同输出（契约 C6）。
/// 来源：csharp-engine plan §4.2；运行时状态模型 §4.1/§7.1 步骤 3；皮层动力学-通用层 §4.2-4.4。
/// </summary>
public static class WcDynamics
{
    /// <summary>回合时长 Δ = 1.0 秒（皮层动力学-通用层 §4.3；spec@v1.1 §四）。不在 Step 签名中（任务issue D2）。
    /// 漂移风险注：step 5（ToneUpdater）与 step 6（Gurney k=25 隐含 Δ）复用同一 Δ——后续 feature 引用本常量来源，不得各自重定义。</summary>
    private const float DeltaSeconds = 1.0f;

    /// <summary>σ 增益 v = 1.0（皮层动力学-通用层 §4.2；spec@v1.1 §四）。不扩 CalibrationConfig（任务issue D3）。</summary>
    private const float SigmaGain = 1.0f;

    /// <summary>σ 阈值 θ = 0.5（皮层动力学-通用层 §4.2；spec@v1.1 §四）。</summary>
    private const float SigmaThreshold = 0.5f;

    /// <summary>
    /// 计算 WC 层一轮（Δ=1.0 秒）动力学更新，返回新状态。
    /// 解析解（偏差 B1——替代设计文档的「Δ/τ≥50 则 a←σ(h) 否则 Euler+clip」分支）：
    /// a_j' = σ(h_j) + (a_j − σ(h_j))·exp(−Δ/τ_j)；h_j = Σ_k W[j,k]·a_k + b_j + s_j（行=接收者）。
    /// 同步更新：全部 h_j 由旧 a 计算后再统一写出（运行时状态模型 §7.1 步骤 3）。
    /// 排除节点（W 行=0）：h_j = b_j + s_j 由统一公式自然覆盖，无特判分支（任务issue D7）。
    /// 输入：a 旧状态（69 维，行序 = canonical 69）；b 脑干调制（69 维，[0,2]——运行时状态模型 §7.2）；
    /// s 感官输入（69 维，≤2.0——运行时状态模型 §4.5）；w 权重矩阵（W[69,69] 行归一化 / Tau[69] / RowFids[69]）。
    /// 输出：新 WcState（防御拷贝，不改输入——契约 C5）。
    /// 异常：ArgumentNullException（a/b/s/w 任一 null）；
    /// ArgumentException（b.Length ≠ 69、s.Length ≠ 69、w.W 非 69×69、w.Tau.Length ≠ 69、任一 τ_j ≤ 0）。
    /// 未定义行为（不校验，调用方契约）：输入 a 含 NaN/Infinity 时输出未定义——生产方（CombatState/EventProcessor）保证输入有限。
    /// 偏差：B1（解析解替代 Euler+clip）、B2（静息吸引子 ≈0.5，0.10 仅初始值——a(0)=0.10 初始化是 step 10 CombatState 职责，任务issue D8）、
    /// B3（解析解推论：全节点单回合收敛 ≥99.87%，动力学实质为固定点迭代——任务issue Q2 裁决，文档叙述修正并入 plan §十三-8）。
    /// 来源：csharp-engine plan §4.2 + 运行时状态模型 §4.1/§7.1 步骤 3；spec@v1.1 §二。
    /// </summary>
    public static WcState Step(WcState a, float[] b, float[] s, WMatrix w)
    {
        ArgumentNullException.ThrowIfNull(a);
        ArgumentNullException.ThrowIfNull(b);
        ArgumentNullException.ThrowIfNull(s);
        ArgumentNullException.ThrowIfNull(w);

        float[] aArr = a.A;
        float[,] wArr = w.W;
        float[] tau = w.Tau;

        if (b.Length != 69)
        {
            throw new ArgumentException($"b 长度必须为 69（当前 {b.Length}）", nameof(b));
        }

        if (s.Length != 69)
        {
            throw new ArgumentException($"s 长度必须为 69（当前 {s.Length}）", nameof(s));
        }

        if (wArr.GetLength(0) != 69 || wArr.GetLength(1) != 69)
        {
            throw new ArgumentException(
                $"w.W 必须为 69×69（当前 {wArr.GetLength(0)}×{wArr.GetLength(1)}）", nameof(w));
        }

        if (tau.Length != 69)
        {
            throw new ArgumentException($"w.Tau 长度必须为 69（当前 {tau.Length}）", nameof(w));
        }

        for (int j = 0; j < 69; j++)
        {
            if (tau[j] <= 0f)
            {
                throw new ArgumentException($"w.Tau[{j}] 必须 > 0（当前 {tau[j]}）", nameof(w));
            }
        }

        // 同步更新（契约 C2/§三实现要求 1）：h_j 全部由旧 aArr 计算（aArr 全程只读），
        // 新值写入独立数组——就地边算边写会违反同步语义（AC-8 反例锚点）。
        // 偏差 B3：Δ=1 秒远超全部 τ（0.01-0.15），每回合收敛 ≥99.87%——本函数实质为
        // 固定点迭代 a ← σ(W·a+b+s)（「慢节点跨回合保留历史」叙述不成立，文档修正并入 plan §十三-8）。
        var next = new float[69];
        for (int j = 0; j < 69; j++)
        {
            // 偏差 B1：解析指数解 a' = σ(h) + (a − σ(h))·exp(−Δ/τ)——设计文档的 Euler+clip 分支
            // 在 Δ/τ ≥ 50（快节点）时与解析解等价（e^(−100) 修正项低于 float32 舍入粒度，逐位相等），
            // 慢节点时 Euler 产生 bang-bang 振荡，故统一走解析解。
            // 任务issue D7：排除节点 W 行=0 → Σ 项自然为 0，h_j = b_j + s_j，无需分支。
            float h = b[j] + s[j];
            for (int k = 0; k < 69; k++)
            {
                h += wArr[j, k] * aArr[k];
            }

            float sigma = Sigma(h);
            float decay = MathF.Exp(-DeltaSeconds / tau[j]);
            next[j] = sigma + (aArr[j] - sigma) * decay;
        }

        return new WcState(next);
    }

    /// <summary>
    /// σ(x) = 1 / (1 + exp(−v·(x − θ)))——皮层动力学-通用层 §4.2。
    /// v = SigmaGain = 1.0 时与 spec@v1.1 §四辅助式 1/(1+exp(−(x−θ))) 逐位等价（IEEE 754 下 ×1.0f 精确）。
    /// </summary>
    private static float Sigma(float x)
    {
        return 1f / (1f + MathF.Exp(-SigmaGain * (x - SigmaThreshold)));
    }
}
