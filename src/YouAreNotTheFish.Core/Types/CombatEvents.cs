namespace YouAreNotTheFish.Core.Types;

/// <summary>
/// 引擎输出事件基类——框架 memory §3.5 + spec@v1.1 §二 2.11。
/// ActorId = 事件主动方（攻击者/倒下者），TargetId = 承受方；语义逐子类注明。
/// 事件装客观结果（决策 D4）；§5.5 的 A/B 每角色视角由 EventProcessor（step 9）派生。
/// 偏差声明：框架 memory 的 DamageEvent 名称不落地，拆为 Physical/Mental 两子类（plan §4.6 字段集不同）。
/// </summary>
public abstract record CombatEvent
{
    /// <summary>回合编号（标注用）。</summary>
    public int Round { get; }

    /// <summary>事件主动方 participant 索引（攻击者/倒下者）。</summary>
    public int ActorId { get; }

    /// <summary>承受方 participant 索引。</summary>
    public int TargetId { get; }

    /// <summary>子类构造入口。</summary>
    protected CombatEvent(int round, int actorId, int targetId)
    {
        Round = round;
        ActorId = actorId;
        TargetId = targetId;
    }
}

/// <summary>
/// 物理攻击事件——plan §4.6 物理公式逐因子（§九 console 输出需要）；
/// §5.5 m 公式（A1/A2: actual/expected、B1: |ΔHP|/HP_max、A5/B2: blocked/incoming）。
/// </summary>
public sealed record PhysicalDamageEvent : CombatEvent
{
    /// <summary>命中与否（L0 回避等影响）。来源：plan §4.6。</summary>
    public bool Hit { get; init; }

    /// <summary>基础伤害。来源：plan §4.6。</summary>
    public int BaseDamage { get; init; }

    /// <summary>武器加成。来源：plan §4.6。</summary>
    public int WeaponBonus { get; init; }

    /// <summary>力量调制因子。来源：plan §4.6。</summary>
    public float ForceMod { get; init; }

    /// <summary>动机调制因子。来源：plan §4.6。</summary>
    public float MotivationMod { get; init; }

    /// <summary>门控加成因子。来源：plan §4.6（gate→结算接线，审计修复 #10）。</summary>
    public float GateBonus { get; init; }

    /// <summary>实际造成伤害。来源：§5.5 A1（actual）。float——一位小数结算（csharp-damage spec §二 2.2 B5）。</summary>
    public float DamageDealt { get; init; }

    /// <summary>被防御减免量。来源：§5.5 A5/B2（blocked）。</summary>
    public float DamageBlocked { get; init; }

    /// <summary>减免前总伤害（blocked + dealt）。来源：§5.5 A5/B2（incoming）。</summary>
    public float IncomingDamage { get; init; }

    /// <summary>承受者 HP 变化前/后/上限。来源：§5.5 B1（|ΔHP|/HP_max）。</summary>
    public float TargetHpBefore { get; init; }

    /// <summary>承受者 HP 变化后。</summary>
    public float TargetHpAfter { get; init; }

    /// <summary>承受者 HP 上限。</summary>
    public float TargetHpMax { get; init; }

    /// <summary>构造入口。</summary>
    public PhysicalDamageEvent(int round, int actorId, int targetId) : base(round, actorId, targetId) { }
}

/// <summary>
/// 精神攻击事件——plan §4.6 精神公式；
/// §5.5（A4: actual/expected、B4: |ΔSAN|/SAN_max）。
/// A4 expected 重算注意（step 9 消费方）：expected = 2×(1+motivation) − 忍耐被动，
/// 需忍耐被动常量（基础行动设计 §四，值 −1，未进 CalibrationConfig——plan §七 同样未列）与
/// 低 SAN 穿透逻辑（核心机制 §4.3）；EventProcessor 需读 ParticipantState.EnduranceActiveCd 或在 step 9 补常量。
/// </summary>
public sealed record MentalDamageEvent : CombatEvent
{
    /// <summary>SAN 伤害。来源：plan §4.6。float（B5）。</summary>
    public float SanDamage { get; init; }

    /// <summary>附带 HP 伤害（SAN=0 时转为 HP，核心机制心理伤害规则）。来源：plan §4.6。float（B5）。</summary>
    public float HpDamage { get; init; }

    /// <summary>动机调制因子。来源：plan §4.6。</summary>
    public float MotivationMod { get; init; }

    /// <summary>门控加成因子。来源：plan §4.6。</summary>
    public float GateBonus { get; init; }

    /// <summary>承受者 SAN 变化前。</summary>
    public float TargetSanBefore { get; init; }

    /// <summary>承受者 SAN 变化后。</summary>
    public float TargetSanAfter { get; init; }

    /// <summary>承受者 SAN 上限。</summary>
    public float TargetSanMax { get; init; }

    /// <summary>承受者 HP 变化前。</summary>
    public float TargetHpBefore { get; init; }

    /// <summary>承受者 HP 变化后。</summary>
    public float TargetHpAfter { get; init; }

    /// <summary>承受者 HP 上限。</summary>
    public float TargetHpMax { get; init; }

    /// <summary>构造入口。</summary>
    public MentalDamageEvent(int round, int actorId, int targetId) : base(round, actorId, targetId) { }
}

/// <summary>
/// 治疗事件——demo 3 基础行动无治疗动作（plan §一 范围表无治疗项，推断）；
/// 保留系框架 memory §3.5 4 事件类型完整性要求。占位字段。
/// </summary>
public sealed record HealEvent : CombatEvent
{
    /// <summary>治疗量。占位字段（demo 未用）。</summary>
    public int HealAmount { get; init; }

    /// <summary>构造入口。</summary>
    public HealEvent(int round, int actorId, int targetId) : base(round, actorId, targetId) { }
}

/// <summary>
/// 状态变化事件——§5.5 C1（SAN&lt;30% 跨越，old≥30%∧new&lt;30%）/ D 注（HP≤0 即时 → D1/D2 派生）。
/// ActorId = 状态变化者，TargetId = ActorId（Downed 时同为倒下者，观察者由 step 9 派生）。
/// </summary>
public sealed record StatusChangeEvent : CombatEvent
{
    /// <summary>状态类型（Panic/Downed）。来源：§5.5 C1 / D 注。</summary>
    public StatusKind Kind { get; init; }

    /// <summary>true=进入状态，false=脱离。</summary>
    public bool Entered { get; init; }

    // L2 类型变更（csharp-events spec §二 2.1，任务issue Q1=A，2026-08-14）——
    // C1 guard 需要 SAN 跨越前后值；Kind=Downed 时 3 字段语义未定义（可不填，默认 0f）。

    /// <summary>状态变化前 SAN 值（跨越判定的 old）。来源：运行时状态模型 §5.5 C1 guard：old ≥ 30%。</summary>
    public float SanBefore { get; init; }

    /// <summary>状态变化后 SAN 值（new）。来源：§5.5 C1 guard：new &lt; 30%。</summary>
    public float SanAfter { get; init; }

    /// <summary>状态变化时的 SAN 上限（比率分母）。来源：§5.5 C1：SAN &lt; 30% × SAN_max。</summary>
    public float SanMax { get; init; }

    /// <summary>构造入口。</summary>
    public StatusChangeEvent(int round, int actorId, int targetId) : base(round, actorId, targetId) { }
}

/// <summary>
/// 链路成长事件——demo 未用（无 link）；字段按 link 系统实装时扩充，占位注明。
/// </summary>
public sealed record LinkGrowthEvent : CombatEvent
{
    /// <summary>链路标识。占位字段（demo 未用）。</summary>
    public string LinkId { get; init; } = "";

    /// <summary>Δm 成长量。占位字段。</summary>
    public float DeltaM { get; init; }

    /// <summary>构造入口。</summary>
    public LinkGrowthEvent(int round, int actorId, int targetId) : base(round, actorId, targetId) { }
}
