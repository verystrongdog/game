using System.Text.Json.Serialization;

namespace YouAreNotTheFish.Core.Data;

/// <summary>神经元群体时间尺度：fast (τ=0.01s) / medium (τ=0.05s) / slow (τ=0.15s)。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<Timescale>))]
public enum Timescale { Fast, Medium, Slow }

/// <summary>CSTC 环路归属。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<CstcLoop>))]
public enum CstcLoop { None, Somatic, Limbic, Cognitive, Global }

/// <summary>CSTC 环路中的功能角色。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<CstcRole>))]
public enum CstcRole
{
    None,
    CorticalInput,
    StriatalGate,
    PallidalOutput,
    ThalamicRelay,
    Modulator
}

/// <summary>层级信息流方向。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<HierarchyDirection>))]
public enum HierarchyDirection { Feedforward, Feedback, Both, Lateral }

/// <summary>玩法域——脑区在游戏机制中的功能归属。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<GameplayDomain>))]
public enum GameplayDomain
{
    ActionGating,
    ArousalModulation,
    CognitiveControl,
    HabitLearning,
    Interoception,
    MemoryConsolidation,
    MotorExecution,
    RewardLearning,
    SensoryPerception,
    SocialCognition,
    ThalamicRelay,
    ThreatDefense
}

/// <summary>脑区解剖分类：皮层 / 皮层下 / 脑干。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<BrainRegionCategory>))]
public enum BrainRegionCategory { Cortical, Subcortical, Brainstem }

/// <summary>主导振荡频段。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<OscillatoryBand>))]
public enum OscillatoryBand { Alpha, Beta, Gamma, Theta }

/// <summary>主导神经递质。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<Neurotransmitter>))]
public enum Neurotransmitter { Gaba, Dopamine, Glutamate, Norepinephrine, Serotonin }

/// <summary>边/通路的功能角色：active（传导信号）/ silent（解剖存在但无功能信号）/ modulating（调节）。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<EdgeRole>))]
public enum EdgeRole { Active, Silent, Modulating }

/// <summary>脑干神经调质系统。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<BrainstemSystem>))]
public enum BrainstemSystem { LcNe, Raphe5Ht, SncDa, VtaDa }

/// <summary>CSTC 环路中的通路类型。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<CstcPathway>))]
public enum CstcPathway
{
    GoDirect,
    NogoIndirect,
    StopHyperdirect,
    Disinhibition,
    Thalamocortical
}

/// <summary>CSTC 环路中的解剖站点。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<CstcStation>))]
public enum CstcStation
{
    CorticalInput,
    StriatalGate,
    PallidalOutput,
    ThalamicRelay,
    Stn
}

/// <summary>脑干投射类型。</summary>
[JsonConverter(typeof(SnakeCaseEnumConverter<BrainstemProjectionType>))]
public enum BrainstemProjectionType { DiffuseBroadcast, TargetedBroadcast }
