using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>威胁判断的结算结果——读 WC 层激活值推出的「外部威胁」量化。</summary>
public sealed record ThreatVerdict
{
    /// <summary>威胁评分 [0, 1]——由杏仁核（威胁估计）与 PAG（防御驱动表达）双通道混合。</summary>
    public float ThreatScore { get; init; }

    /// <summary>是否触发恐慌（威胁 &gt; 有效阈值 → 自动激活逃跑/僵住）。来源：脑功能层级模型 §三 3.3。</summary>
    public bool PanicTriggered { get; init; }

    /// <summary>有效防御触发阈值——随杏仁核激活升高而降低（恐惧条件化→易恐慌）。</summary>
    public float EffectiveThreshold { get; init; }

    /// <summary>索敌优先级（用于敌方目标选择）——归一化后可直接排序。</summary>
    public float TargetPriority { get; init; }
}

/// <summary>
/// 神经模型的「外部威胁判断」最小组件——把脑区激活值翻译成游戏判断逻辑。
///
/// 对接口：运行时管线已通过 EventProcessor（感官事件 → W_sensory×α 的 69 维 s）→
/// WcDynamics.Step 算出每参与者 ParticipantState.Wc（69 激活值）。本组件只负责**读**其中
/// 两个 threat_defense 域脑区的激活，并推出游戏层判断：
///   - 杏仁核 Amygdala（L1）：恐惧条件化、标记威胁、降低 PAG 防御触发阈值（脑功能层级模型 §四 4.1）
///   - PAG（L0）：防御行为执行的表达——逃跑/僵住（§三 3.1）
///
/// 纯函数、确定性、无 static 可变状态、无 RNG（对齐 WC 引擎契约）：
/// 同输入（state + 索引）→ 逐位同输出。
/// </summary>
public sealed class ThreatJudge
{
    /// <summary>杏仁核在 canonical 69 行序中的索引（region_fid = "Amygdala"）。</summary>
    public int AmygdalaIndex { get; }

    /// <summary>PAG 在 canonical 69 行序中的索引（region_fid = "PeriaqueductalGray"）。</summary>
    public int PagIndex { get; }

    /// <summary>威胁评分中杏仁核通道权重。</summary>
    private const float AmygdalaWeight = 0.5f;

    /// <summary>威胁评分中 PAG 通道权重。</summary>
    private const float PagWeight = 0.5f;

    /// <summary>
    /// 恐慌基础阈值——PAG 激活 ≥ 该值即触发自动防御。
    /// 来源：脑功能层级模型 §三 3.3「阈值型触发（威胁 &gt; 某值 → 自动建议或强制执行）」。
    /// </summary>
    private const float PanicThresholdBase = 0.65f;

    /// <summary>杏仁核对恐慌阈值的调制增益——杏仁核激活 p 时阈值 = Base − p×Gain（§四 4.1 降低阈值）。</summary>
    private const float AmygdalaThresholdGain = 0.20f;

    /// <summary>恐慌阈值不可低于此绝对值（L5 只能调制不可完全消除的保证）。</summary>
    private const float PanicThresholdFloor = 0.30f;

    /// <summary>
    /// 构造。
    /// </summary>
    /// <param name="amygdalaIndex">杏仁核索引（canonical 69）。</param>
    /// <param name="pagIndex">PAG 索引（canonical 69）。</param>
    /// <exception cref="ArgumentOutOfRangeException">任一索引 ∉ [0, 69)。</exception>
    public ThreatJudge(int amygdalaIndex, int pagIndex)
    {
        if ((uint)amygdalaIndex >= 69)
            throw new ArgumentOutOfRangeException(nameof(amygdalaIndex), amygdalaIndex,
                $"杏仁核索引必须 ∈ [0, 69)，当前 {amygdalaIndex}");
        if ((uint)pagIndex >= 69)
            throw new ArgumentOutOfRangeException(nameof(pagIndex), pagIndex,
                $"PAG 索引必须 ∈ [0, 69)，当前 {pagIndex}");

        AmygdalaIndex = amygdalaIndex;
        PagIndex = pagIndex;
    }

    /// <summary>
    /// 【构造辅助】从 GameData 的 Wsensory.RegionIds（= canonical 69）解析脑区索引。
    /// 找不到任一脑区 → InvalidOperationException（数据契约 break，不做静默兜底）。
    /// </summary>
    /// <param name="gd">游戏数据（Wsensory.RegionIds 非空）。</param>
    /// <returns>解析好索引的 ThreatJudge。</returns>
    public static ThreatJudge FromGameData(GameData gd)
    {
        ArgumentNullException.ThrowIfNull(gd);
        var ids = gd.Wsensory.RegionIds;
        ArgumentNullException.ThrowIfNull(ids);
        if (ids.Length == 0)
            throw new InvalidOperationException("Wsensory.RegionIds 为空——无法解析威胁脑区索引。");

        int amygdala = Array.IndexOf(ids, "Amygdala");
        int pag = Array.IndexOf(ids, "PeriaqueductalGray");
        if (amygdala < 0 || pag < 0)
            throw new InvalidOperationException(
                $"区域表中缺少威胁脑区：Amygdala={(amygdala < 0 ? "missing" : amygdala.ToString())}, " +
                $"PeriaqueductalGray={(pag < 0 ? "missing" : pag.ToString())}");

        return new ThreatJudge(amygdala, pag);
    }

    /// <summary>
    /// 计算威胁判断。
    /// </summary>
    /// <param name="state">该参与者的 WC 层激活（69 维，值域 [0,1]；生产方保证有限）。</param>
    /// <returns>威胁评分 / 恐慌触发 / 索敌优先级。</returns>
    /// <exception cref="ArgumentNullException">state 为 null。</exception>
    /// <exception cref="ArgumentException">state.A 长度 ≠ 69。</exception>
    /// <remarks>输入含 NaN/Infinity 时输出未定义（调用方契约，同 WcDynamics）。</remarks>
    public ThreatVerdict Evaluate(WcState state)
    {
        ArgumentNullException.ThrowIfNull(state);
        if (state.A.Length != 69)
            throw new ArgumentException($"state.A 长度必须为 69（当前 {state.A.Length}）", nameof(state));

        float amygdala = Clamp01(state.A[AmygdalaIndex]);
        float pag = Clamp01(state.A[PagIndex]);

        // 1) 威胁评分：学习性威胁估计（杏仁核）× 防御驱动表达（PAG）各半混合。
        float threat = AmygdalaWeight * amygdala + PagWeight * pag;

        // 2) 恐慌触发：PAG 驱动的「已触发防御」超过有效阈值。
        //    杏仁核激活越高 → 阈值越低 → 更易触发（恐惧条件化降低 PAG 防御触发阈值）。
        float lowered = PanicThresholdBase - AmygdalaThresholdGain * amygdala;
        float effective = MathF.Max(lowered, PanicThresholdFloor);
        bool panic = pag >= effective;

        // 3) 索敌优先级：威胁评分本身就是压制力/关注度的读法——敌方优先点名高分者。
        float priority = threat;

        return new ThreatVerdict
        {
            ThreatScore = threat,
            PanicTriggered = panic,
            EffectiveThreshold = effective,
            TargetPriority = priority,
        };
    }

    private static float Clamp01(float v) => MathF.Max(0f, MathF.Min(1f, v));
}
