using YouAreNotTheFish.Core.Data;
using YouAreNotTheFish.Core.Types;

namespace YouAreNotTheFish.Core.Engine;

/// <summary>
/// Layer 3 速度排序计算器（csharp-engine plan §十一 step 7）——csharp-speed spec@v1.1（.scratch/csharp-speed/design/spec.md）。
/// 职责：把 WC 激活 a(t)、三环路 salience（决断分 c_loop）、Gurney 状态（执行分 a_SD1）提取为三成分终值
/// （察觉逐节点回落）→ 加权合成 speed 序数值（序数语义——绝对量无意义，回合战斗流程 §3.1）。
/// 纯函数：无 static 可变状态、无 RNG、同输入同输出。
/// 来源：csharp-engine plan §4.5 方案 B；回合战斗流程 §3.1-3.4；spec@v1.1 §三。
/// 偏差：B1（无首回合特判——静息值由战斗初始状态自然给出）、B2（归一化 mean）、
///       B3（Putamen 代理 = a_SD1_somatic，Q3=A）、B4（权重偏移不覆盖——恒等权）。
/// </summary>
public sealed class SpeedScoreCalculator
{
    // ---- 察觉静息常量（spec §四；来源 = csharp-tone 工作issue 01 M1 实测值表 69 行附录逐 fid 值）----
    // ⚠️ 数据漂移注：脑区数据变更 → M1 实测值变更 → 常量须同步（AC-3 锚点即哨兵）——spec §四。

    /// <summary>Pericalcarine M1 静息值（spec §四）。</summary>
    private const float RestPericalcarine = 0.6309757f;

    /// <summary>TransverseTemporal M1 静息值（spec §四）。</summary>
    private const float RestTransverseTemporal = 0.6316023f;

    /// <summary>Insula M1 静息值（spec §四）。</summary>
    private const float RestInsula = 0.6327866f;

    /// <summary>AnteriorCingulateCortex M1 静息值（spec §四）。</summary>
    private const float RestAnteriorCingulateCortex = 0.6751733f;

    /// <summary>4 察觉节点 fid 名（spec §五 1；回合战斗流程 §3.2 节点清单）——构造解析用。</summary>
    private static readonly string[] PerceptionFids =
    [
        "Pericalcarine", "TransverseTemporal", "Insula", "AnteriorCingulateCortex",
    ];

    private readonly int[] _perceptionRows;
    private readonly int _precentralRow;
    private readonly CalibrationConfig _cal;

    /// <summary>
    /// 解析 5 行索引（4 察觉节点 + Precentral）（构造期一次）。
    /// 职责：rowFids = data.Wsensory.RegionIds（canonical 69）；fid → 行号解析镜像 WMatrixBuilder Step 1 / CstcGating 构造。
    /// 异常：data/cal 为 null → ArgumentNullException；
    ///       解析名未命中 RegionIds → KeyNotFoundException（隐式，镜像 CstcGating 构造——数据契约由数据层双射锁定）。
    /// 来源：spec@v1.1 §三 3.1、§五 1。
    /// </summary>
    public SpeedScoreCalculator(GameData data, CalibrationConfig cal)
    {
        ArgumentNullException.ThrowIfNull(data);
        ArgumentNullException.ThrowIfNull(cal);

        // Step 1 — 行序契约：canonical = Wsensory.RegionIds（约束 C1，镜像 WMatrixBuilder Step 1）
        string[] rowFids = data.Wsensory.RegionIds;
        var fidToRow = new Dictionary<string, int>(rowFids.Length);
        for (int i = 0; i < rowFids.Length; i++)
        {
            fidToRow[rowFids[i]] = i;
        }

        // Step 2 — 5 解析名（4 察觉 + Precentral）。未命中 → KeyNotFoundException（隐式，数据契约锁定）
        _perceptionRows = new int[PerceptionFids.Length];
        for (int i = 0; i < PerceptionFids.Length; i++)
        {
            _perceptionRows[i] = fidToRow[PerceptionFids[i]];
        }

        _precentralRow = fidToRow["Precentral"];
        _cal = cal; // 保存引用（不可变 record）
    }

    /// <summary>
    /// 构造期解析的 4 察觉节点 canonical 行索引——公开只读访问器（AC-1 可测性；镜像 CstcGating.CiRows 公开先例）。
    /// 顺序 = PerceptionFids 顺序（Pericalcarine/TransverseTemporal/Insula/AnteriorCingulateCortex）。
    /// 不泄露新信息：canonical 行序已由 Wsensory.RegionIds 公开锁定。
    /// </summary>
    public IReadOnlyList<int> PerceptionRows => _perceptionRows;

    /// <summary>构造期解析的 Precentral canonical 行索引（AC-1 可测性；同上先例）。</summary>
    public int PrecentralRow => _precentralRow;

    /// <summary>
    /// 提取三成分终值（纯函数，无首回合特判——B1）。
    /// 察觉 = mean(a[4 察觉节点]，逐节点回落——a_j &lt; PerceptionThreshold → 该节点 M1 静息值，Q2=A)；
    /// 决断 = (salience.Somatic.C + Cognitive.C + Limbic.C) / 3（无回落）；
    /// 执行 = (a[Precentral 行] + gurney.Somatic[0]) / 2 + (isDefending ? M1SustainPenalty : 0)。
    ///   gurney.Somatic[0] = a_SD1（GurneyPopulation 枚举序 0=SD1——GurneyState 文档契约）——Putamen 代理（Q3=A，B3）。
    /// 输入不可变（只读消费）；输出为新 record。
    /// 异常：a/salience/gurney 为 null → ArgumentNullException；
    ///       a.A.Length ≠ 69 → ArgumentException；gurney.Somatic.Length ≠ 5 → ArgumentException（镜像 CstcGating 防御）。
    /// 未定义行为（文档化，不防御）：NaN/Infinity 输入。
    /// 来源：spec@v1.1 §三 3.1；回合战斗流程 §3.2-3.3。
    /// </summary>
    public SpeedComponents ComputeComponents(
        WcState a, LoopSalience salience, GurneyState gurney, bool isDefending)
    {
        ArgumentNullException.ThrowIfNull(a);
        ArgumentNullException.ThrowIfNull(salience);
        ArgumentNullException.ThrowIfNull(gurney);

        float[] aArr = a.A;
        if (aArr.Length != 69)
        {
            throw new ArgumentException($"a.A 长度必须为 69（当前 {aArr.Length}）", nameof(a));
        }

        if (gurney.Somatic.Length != 5)
        {
            throw new ArgumentException(
                $"gurney.Somatic 长度必须为 5（当前 {gurney.Somatic.Length}）", nameof(gurney));
        }

        // 察觉 = mean(4 节点，逐节点回落)。回落：a_j < 阈值 → 该节点静息常量（≥ 阈值不回落）
        float perception =
            (Fallback(aArr[_perceptionRows[0]], RestPericalcarine) +
             Fallback(aArr[_perceptionRows[1]], RestTransverseTemporal) +
             Fallback(aArr[_perceptionRows[2]], RestInsula) +
             Fallback(aArr[_perceptionRows[3]], RestAnteriorCingulateCortex)) / 4f;

        // 决断 = mean(c_loop, 3 环路)，无回落（c_loop≈0 即决断慢——csharp-cstc c=0 门控语义）
        float decision = (salience.Somatic.C + salience.Cognitive.C + salience.Limbic.C) / 3f;

        // 执行 = mean(a(Precentral), a_SD1) + M1 惩罚（B3：a_SD1 = Somatic[0]，枚举序非位置猜）
        float execution = (aArr[_precentralRow] + gurney.Somatic[0]) / 2f;
        if (isDefending)
        {
            execution += _cal.M1SustainPenalty;
        }

        return new SpeedComponents(perception, decision, execution);
    }

    /// <summary>
    /// 加权合成 speed = W1×Perception + W2×Decision + W3×Execution（回合战斗流程 §3.1）。
    /// speed 为序数值——绝对量无意义（§3.1）。
    /// 异常：components/weights 为 null → ArgumentNullException（分别校验）。
    /// 来源：spec@v1.1 §三 3.1；偏差 B2（分量归一化 mean）。
    /// </summary>
    public float ComputeScore(SpeedComponents components, SpeedWeights weights)
    {
        ArgumentNullException.ThrowIfNull(components);
        ArgumentNullException.ThrowIfNull(weights);

        return (weights.W1 * components.Perception)
             + (weights.W2 * components.Decision)
             + (weights.W3 * components.Execution);
    }

    /// <summary>逐节点回落：a_j 低于阈值 → 该节点 M1 静息值；否则原值（Q2=A）。</summary>
    private float Fallback(float value, float rest) =>
        value < _cal.PerceptionThreshold ? rest : value;
}
