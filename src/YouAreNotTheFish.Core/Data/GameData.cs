namespace YouAreNotTheFish.Core.Data;

/// <summary>
/// L1 数据聚合 record（决策 D2）——spec@v1.1 §二 2.12：
/// 5 个数据文件各对应一个已交付 record。plan §三 CombatContext 行、
/// §4.3 WMatrixBuilder.Build(GameData)、CorticalBias.Compute(ToneState, GameData) 均消费本类型。
/// </summary>
/// <param name="BrainRegions">69 脑区。来源：brain_regions.json（csharp-data-layer spec AC-1~5）。</param>
/// <param name="Tripartite">三体模型 51 节点 + 4 种边。来源：connectivity/tripartite_model.json。</param>
/// <param name="Wsensory">69×8 感觉模态矩阵（RegionIds 即 canonical 69——约束 C1；#108 Q2 扩列嗅觉/热觉）。来源：connectivity/W_sensory.json。</param>
/// <param name="SituationPrimitives">27 情境原型。来源：connectivity/situation_primitives.json。</param>
/// <param name="SignalTypes">信号类型词表（4 类目 × 18 子类）。来源：signal_types.json。</param>
/// <param name="AlphaPatterns">α pattern 表（14 事件 × 8 模态，Q1 契约）。来源：connectivity/alpha_patterns.json。</param>
/// <param name="EnvTones">环境基调表（环境键 → α_env + situation.primary，Q3/Q5 契约）。来源：connectivity/env_tones.json。</param>
public sealed record GameData(
    BrainRegionsData BrainRegions,
    TripartiteModel Tripartite,
    WsensoryMatrix Wsensory,
    SituationPrimitives SituationPrimitives,
    SignalTypesCatalog SignalTypes,
    AlphaPatterns AlphaPatterns,
    EnvTones EnvTones);
