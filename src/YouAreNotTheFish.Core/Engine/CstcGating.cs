using System.IO;
using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// Layer 3 CSTC Gurney 门控（csharp-engine plan §十一 step 6）——spec@v1.1（.scratch/csharp-cstc/design/spec.md）。
/// 职责：把 WC 激活 a(t) 与 DA tone 转化为三环路（somatic/cognitive/limbic）各 5 群体 Gurney 激活
/// + 3 个 gate + 3 环路 salience（运行时状态模型 §6.2-6.4；每回合 Phase 3 的最后一个数值引擎）。
/// 纯函数：无 static 可变状态、无 RNG、同输入同输出（契约 C8）。
/// 来源：csharp-engine plan §4.4；运行时状态模型 §6.1-6.4、§7.1 步骤 4-5；spec@v1.1 §三。
/// </summary>
public sealed class CstcGating
{
    /// <summary>
    /// 解析三环路 CI 行索引（构造期一次）。
    /// 职责：rowFids = data.Wsensory.RegionIds（canonical 69）；对 somatic/cognitive/limbic 三环路，
    ///   收集 function_profile 中 cstc_role == CorticalInput && cstc_loop == <loop> 的 fid（单数字段，Q3=B），
    ///   fid → 行号解析镜像 WMatrixBuilder Step 1（fidToRow 字典）；CI 行按升序存储。
    ///   CstcLoop.Global/None 不收集、不校验（任务issue D5——实测 global 0 成员）。
    /// 异常：data 为 null → ArgumentNullException；
    ///       任一环路 CI 空集 → InvalidDataException（任务issue D4，含环路名）；
    ///       CI fid 未命中 RegionIds → KeyNotFoundException（隐式，镜像 WMatrixBuilder 不防御——数据契约由数据层双射锁定，约束 C1）。
    /// 来源：csharp-engine plan §4.4 步骤 1；运行时状态模型 §6.1/§6.2。
    /// 偏差：B4（构造入口为 spec 新增——plan §4.4 仅给 Step 签名）；Q3=B（fid 级口径）已写回文档。
    /// </summary>
    public CstcGating(GameData data)
    {
        ArgumentNullException.ThrowIfNull(data);

        // Step 1 — 行序契约：canonical = Wsensory.RegionIds（约束 C1，镜像 WMatrixBuilder Step 1）
        string[] rowFids = data.Wsensory.RegionIds;
        var fidToRow = new Dictionary<string, int>(rowFids.Length);
        for (int i = 0; i < rowFids.Length; i++)
        {
            fidToRow[rowFids[i]] = i;
        }

        // Step 2 — 三环路 CI 行（单数字段过滤，Q3=B；Global/None 不收集——任务issue D5/C3）
        // 环路按枚举常量名显式列举，不使用枚举序（结转 #2 预防——枚举序与字段序/文档序两两不同）
        var rows = new Dictionary<CstcLoop, IReadOnlyList<int>>();
        foreach (var loop in Loops)
        {
            var ci = new List<int>();
            foreach (var (fid, region) in data.BrainRegions.Regions)
            {
                FunctionProfile profile = region.FunctionProfile;
                if (profile.CstcRole == CstcRole.CorticalInput && profile.CstcLoop == loop)
                {
                    ci.Add(fidToRow[fid]); // 未命中 → KeyNotFoundException（隐式，约束 C1 文档化行为）
                }
            }

            if (ci.Count == 0)
            {
                // 契约 C2：三环路 CI 集非空（任务issue D4，含环路名）
                throw new InvalidDataException(
                    $"CSTC 环路 {loop} 无 CI 成员（cstc_role==CorticalInput && cstc_loop=={loop}），数据契约破坏。");
            }

            ci.Sort(); // canonical 行下标升序（§二 2.3）
            rows[loop] = ci;
        }

        CiRows = rows;
    }

    /// <summary>
    /// 构造期解析的三环路 CI 行索引——公开只读访问器（AC-1 可测性；镜像 WMatrix.RowFids 公开先例）。
    /// 键 = CstcLoop.Somatic/Cognitive/Limbic（Global/None 无成员不入表——C3/D5）；
    /// 值 = canonical 行下标升序 int 列表（fid 名经 Wsensory.RegionIds[row] 反查）。
    /// 不泄露新信息：canonical 行序已由 Wsensory.RegionIds 公开锁定。
    /// </summary>
    public IReadOnlyDictionary<CstcLoop, IReadOnlyList<int>> CiRows { get; }

    /// <summary>
    /// 单回合 CSTC 门控更新（三环路独立，每环路 5 群体）。
    /// 职责（每环路，同时更新——u 全部由 prev 的 O 计算，镜像 WC 骨架）：
    ///   1. c = mean(a[ci rows])；2. DA = wVta×tone.DaVta + (1−wVta)×tone.DaSnc（§四 wVta 表）；
    ///   3. m = [1+DA, 1−DA, 1, 1, 1]；O_prev = ramp(prev, e, m)；
    ///   4. u = [c·(1+DA), c·(1−DA), c − O_prev[GPe], 0.9·O_prev[STN] − O_prev[SD2] + 0.0·O_prev[SD1],
    ///           0.9·O_prev[STN] − 0.3·O_prev[GPe] − O_prev[SD1]]（§6.3 u 表；W_SEL_GPe=0.0 项保留——Q1=A）；
    ///   5. a_new[p] = u[p] + (prev[p] − u[p])·exp(−25)（解析解，无 clamp——a 可为负，Q2=A；偏差 B2/B3）；
    ///   6. O_new = ramp(a_new, e, m)；gate = 1 − O_new[GPi]（偏差 B1——O 取更新后 a）。
    /// 输出：GurneyState（三环路 a_new）/ GateState（三 gate）/ LoopSalience（三 (c, DA)）。
    ///   LoopSalience.Da 按字段名配对（Somatic.Da = 0.2×VTA+0.8×SNc 等——LoopSalience 已交付文档警告，
    ///   不得按文档 §6.3 列表序 limbic→cognitive→somatic 直配，任务issue D8）。
    /// 输入：a 旧 WC 状态（69 维，canonical 行序）；tone 当前 4 tone（只消费 DaVta/DaSnc）；
    ///       prev 旧 Gurney 状态（三环路各 5，群体序 = GurneyPopulation 枚举序）。
    /// 异常：a/tone/prev 为 null → ArgumentNullException；
    ///       a.A.Length ≠ 69 → ArgumentException；prev 任一环路数组 Length ≠ 5 → ArgumentException。
    /// 未定义行为（不校验，调用方契约）：输入含 NaN/Infinity 输出未定义（生产方保证输入有限，同 wc-dynamics 姿态）。
    /// 来源：csharp-engine plan §4.4；运行时状态模型 §6.2-6.4、§7.1 步骤 4-5。
    /// 偏差：B1（gate 时刻）、B2（m=0 防护）、B3（残差上界）。
    /// </summary>
    public (GurneyState Gurney, GateState Gates, LoopSalience Salience) Step(
        WcState a, ToneState tone, GurneyState prev)
    {
        ArgumentNullException.ThrowIfNull(a);
        ArgumentNullException.ThrowIfNull(tone);
        ArgumentNullException.ThrowIfNull(prev);

        float[] aArr = a.A;
        if (aArr.Length != 69)
        {
            throw new ArgumentException($"a.A 长度必须为 69（当前 {aArr.Length}）", nameof(a));
        }

        if (prev.Somatic.Length != 5)
        {
            throw new ArgumentException($"prev.Somatic 长度必须为 5（当前 {prev.Somatic.Length}）", nameof(prev));
        }

        if (prev.Cognitive.Length != 5)
        {
            throw new ArgumentException($"prev.Cognitive 长度必须为 5（当前 {prev.Cognitive.Length}）", nameof(prev));
        }

        if (prev.Limbic.Length != 5)
        {
            throw new ArgumentException($"prev.Limbic 长度必须为 5（当前 {prev.Limbic.Length}）", nameof(prev));
        }

        // 解析收敛系数（偏差 B3：|a_new − u| = |a − u|·e^(−25) ≤ 3.5×1.39e-11 ≈ 4.9e-11）
        // Δ 复用注：k=25 隐含 Δ=1.0（引用 csharp-wc-dynamics spec §四，不重新定义 Δ）——自检清单第 8 项
        float decay = MathF.Exp(-GurneyK);

        // DA 混合权重按枚举常量名显式配对（§四 4.3；结转 #2——禁止按枚举序数建表）
        (float[] Somatic, float GateSomatic, float CSomatic, float DaSomatic) =
            StepLoop(aArr, tone.DaVta, tone.DaSnc, prev.Somatic, WvtaSomatic, CiRows[CstcLoop.Somatic], decay);
        (float[] Cognitive, float GateCognitive, float CCognitive, float DaCognitive) =
            StepLoop(aArr, tone.DaVta, tone.DaSnc, prev.Cognitive, WvtaCognitive, CiRows[CstcLoop.Cognitive], decay);
        (float[] Limbic, float GateLimbic, float CLimbic, float DaLimbic) =
            StepLoop(aArr, tone.DaVta, tone.DaSnc, prev.Limbic, WvtaLimbic, CiRows[CstcLoop.Limbic], decay);

        return (
            new GurneyState(Somatic, Cognitive, Limbic), // 构造防御拷贝（契约 C7）
            new GateState
            {
                GateSomatic = GateSomatic,
                GateCognitive = GateCognitive,
                GateLimbic = GateLimbic,
            },
            // Da 按字段名配对（约束 C6）——不得按位置直配
            new LoopSalience(
                new LoopValue(CSomatic, DaSomatic),
                new LoopValue(CCognitive, DaCognitive),
                new LoopValue(CLimbic, DaLimbic)));
    }

    /// <summary>单环路 6 步（spec §三 Step 职责 1-6；u 全部由 prev 的 O 计算——同时更新，自检清单第 9 项）。</summary>
    private static (float[] Next, float Gate, float C, float Da) StepLoop(
        float[] a, float daVta, float daSnc, float[] prev, float wVta, IReadOnlyList<int> ciRows, float decay)
    {
        // 1. c = mean(a[ci])（Q3=B fid 级口径；CI 行升序但均值与顺序无关）
        float sum = 0f;
        foreach (int row in ciRows)
        {
            sum += a[row];
        }

        float c = sum / ciRows.Count;

        // 2. DA 混合（§四 4.3；任务issue D8）
        float da = (wVta * daVta) + ((1f - wVta) * daSnc);

        // 3. m 与 O_prev（群体序 = GurneyPopulation；ramp 见 Ramp）
        float mSd1 = 1f + da;
        float mSd2 = 1f - da;
        float oSd1 = Ramp(prev[(int)GurneyPopulation.Sd1], ESd1, mSd1);
        float oSd2 = Ramp(prev[(int)GurneyPopulation.Sd2], ESd2, mSd2);
        float oStn = Ramp(prev[(int)GurneyPopulation.Stn], EStn, MOne);
        float oGPe = Ramp(prev[(int)GurneyPopulation.GPe], EGPe, MOne);

        // 4. u（§6.3 u 表；W_SEL_GPe=0.0 项保留——Q1=A；自检清单第 1 项）
        float uSd1 = WSel * c * (1f + da);
        float uSd2 = WCont * c * (1f - da);
        float uStn = (WStn * c) + (WGPeStn * oGPe);
        float uGPe = (WStnGPe * oStn) + (WContGPe * oSd2) + (WSelGPe * oSd1);
        float uGpi = (WStnGpi * oStn) + (WGPeGpi * oGPe) + (WSelGpi * oSd1);

        // 5. 解析解 a_new = u + (a − u)·e^(−25)（无 clamp，Q2=A；偏差 B2/B3）
        float aSd1 = uSd1 + ((prev[(int)GurneyPopulation.Sd1] - uSd1) * decay);
        float aSd2 = uSd2 + ((prev[(int)GurneyPopulation.Sd2] - uSd2) * decay);
        float aStn = uStn + ((prev[(int)GurneyPopulation.Stn] - uStn) * decay);
        float aGPe = uGPe + ((prev[(int)GurneyPopulation.GPe] - uGPe) * decay);
        float aGpi = uGpi + ((prev[(int)GurneyPopulation.GPi] - uGpi) * decay);

        // 6. O_new + gate（偏差 B1：gate = 1 − O_GPi(a_new)——O 取更新后 a，非 prev）
        float gate = 1f - Ramp(aGpi, EGpi, MOne);

        return (new[] { aSd1, aSd2, aStn, aGPe, aGpi }, gate, c, da);
    }

    /// <summary>
    /// ramp 输出函数（spec §四 4.5；运行时状态模型 §6.3 内联）：下截止 a&lt;e → 0；
    /// 线性区 e ≤ a ≤ 1/m+e → m·(a−e)；饱和 a &gt; 1/m+e → 1。
    /// 偏差 B2：m ≤ 0 → O ≡ 0（显式防护分支，不依赖 float 除零语义——DA=1 时 m_SD2=0，第三分支 1/m 无定义）。
    /// </summary>
    private static float Ramp(float a, float e, float m)
    {
        if (m <= 0f)
        {
            return 0f; // 偏差 B2：m=0 时 O≡0（ModelDB 语义——DA=1 的 SD2 恒零输出合法）
        }

        if (a < e)
        {
            return 0f;
        }

        float upper = (1f / m) + e;
        if (a > upper)
        {
            return 1f;
        }

        return m * (a - e);
    }

    /// <summary>参与 gating 的三环路（枚举常量名显式列举，不使用枚举序——§四 4.3 防 ordinal）。</summary>
    private static readonly CstcLoop[] Loops = [CstcLoop.Somatic, CstcLoop.Cognitive, CstcLoop.Limbic];

    // ---- 连接权重（spec §四 4.1；运行时状态模型 §6.3；私有常量不扩 CalibrationConfig——任务issue D3）----

    /// <summary>W_SEL：皮层→SD1。</summary>
    private const float WSel = 1.0f;

    /// <summary>W_CONT：皮层→SD2。</summary>
    private const float WCont = 1.0f;

    /// <summary>W_STN：皮层→STN。</summary>
    private const float WStn = 1.0f;

    /// <summary>W_SEL_GPi：SD1→GPi（GO）。</summary>
    private const float WSelGpi = -1.0f;

    /// <summary>W_SEL_GPe：SD1→GPe（无连接——Q1=A 裁决入表，ModelDB 83560 默认；GPe 方程保留该项）。</summary>
    private const float WSelGPe = 0.0f;

    /// <summary>W_CONT_GPe：SD2→GPe。</summary>
    private const float WContGPe = -1.0f;

    /// <summary>W_STN_GPi：STN→GPi（STOP）。</summary>
    private const float WStnGpi = 0.9f;

    /// <summary>W_STN_GPe：STN→GPe。</summary>
    private const float WStnGPe = 0.9f;

    /// <summary>W_GPe_STN：GPe→STN。</summary>
    private const float WGPeStn = -1.0f;

    /// <summary>W_GPe_GPi：GPe→GPi。</summary>
    private const float WGPeGpi = -0.3f;

    // ---- per-population 阈值 e（spec §四 4.2；Q2=A 裁决，对齐 ModelDB 83560；群体序 = GurneyPopulation）----

    /// <summary>e_SD1：GO 激活阈值。</summary>
    private const float ESd1 = 0.2f;

    /// <summary>e_SD2：NO-GO 激活阈值。</summary>
    private const float ESd2 = 0.2f;

    /// <summary>e_STN：超直接通路低阈（快速响应）。</summary>
    private const float EStn = -0.25f;

    /// <summary>e_GPe：tonic 输出（a=0 → O=0.2）。</summary>
    private const float EGPe = -0.2f;

    /// <summary>e_GPi：tonic 抑制（a=0 → O=0.2 → gate=0.8）。</summary>
    private const float EGpi = -0.2f;

    // ---- DA 混合权重（spec §四 4.3；按枚举常量名显式配对，禁止按序数——见 Step）----

    /// <summary>w_VTA_somatic：运动执行主导。</summary>
    private const float WvtaSomatic = 0.2f;

    /// <summary>w_VTA_cognitive：0.4。</summary>
    private const float WvtaCognitive = 0.4f;

    /// <summary>w_VTA_limbic：动机主导。</summary>
    private const float WvtaLimbic = 0.8f;

    // ---- 其余常量（spec §四 4.4）----

    /// <summary>Gurney 时间常数 k=25（τ=0.04s；Δ=1.0 隐含——复用注：Δ 引用 csharp-wc-dynamics spec §四，不重新定义）。</summary>
    private const float GurneyK = 25f;

    /// <summary>m_STN / m_GPe / m_GPi = 1.0（运行时状态模型 §6.3）。</summary>
    private const float MOne = 1.0f;
}
