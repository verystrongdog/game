namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 参与者完整状态——91 浮点（69 WC + 4 tone + 15 Gurney + 3 gate）+ 战斗量（审计修复 #2：
/// HP/SAN 独立于 91 浮点）+ 双通道战斗状态（修复 #3/#4）。运行时状态模型 §三 表尾「总计 91」。
/// </summary>
public sealed record ParticipantState
{
    /// <summary>WC 层 69 激活值。</summary>
    public WcState Wc { get; init; } = null!;

    /// <summary>脑干 tone 4 值。</summary>
    public ToneState Tone { get; init; } = null!;

    /// <summary>Gurney 三环路 15 值。</summary>
    public GurneyState Gurney { get; init; } = null!;

    /// <summary>三环路门控 3 值。</summary>
    public GateState Gates { get; init; } = null!;

    /// <summary>HP——审计修复 #2（原计划 91 浮点无血量）。</summary>
    public int Hp { get; init; }

    /// <summary>HP 上限。</summary>
    public int HpMax { get; init; }

    /// <summary>SAN——审计修复 #2。</summary>
    public int San { get; init; }

    /// <summary>SAN 上限。</summary>
    public int SanMax { get; init; }

    /// <summary>防御状态——审计修复 #4；回合战斗流程 §7.1（持续到下回合自己窗口）。</summary>
    public bool IsDefending { get; init; }

    /// <summary>忍耐主动 CD——基础行动设计 §四（−2 占 Broca）；回合战斗流程 §9.1（自己窗口起点递减）。</summary>
    public int EnduranceActiveCd { get; init; }

    /// <summary>防御 CD——回合战斗流程 §9.1（CD=1：暴露一轮后才能再防）。</summary>
    public int DefendCd { get; init; }

    /// <summary>
    /// 默认初始化工厂——spec@v1.1 §三 3.4：
    /// a_j=0.10、tone=baseline(0.3/0.4/0.5/0.5)、Gurney=0（运行时状态模型 §7.3）；
    /// gates=1.0（推导值——§7.3 未定义 gate 初值，1.0 = 1 − O_GPi(0)：§6.3 ramp O(a)=0 if a&lt;e=0.2，
    /// §6.4 gate=1−O_GPi；语义「初始全放行」，首回合 Phase 1 步骤 5 CstcGating.Step 重算覆盖）；
    /// CD=0、IsDefending=false。
    /// </summary>
    public static ParticipantState CreateDefault(int hpMax, int sanMax)
    {
        var a = new float[RegionCount];
        Array.Fill(a, 0.10f);
        return new ParticipantState
        {
            Wc = new WcState(a),
            Tone = new ToneState { Ne = 0.3f, DaVta = 0.4f, DaSnc = 0.5f, Ht5 = 0.5f },
            Gurney = new GurneyState(new float[5], new float[5], new float[5]),
            Gates = new GateState { GateSomatic = 1.0f, GateCognitive = 1.0f, GateLimbic = 1.0f },
            Hp = hpMax,
            HpMax = hpMax,
            San = sanMax,
            SanMax = sanMax,
            IsDefending = false,
            EnduranceActiveCd = 0,
            DefendCd = 0,
        };
    }

    /// <summary>canonical 脑区数（约束 C1）。</summary>
    private const int RegionCount = 69;
}
