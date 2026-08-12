# C# Data Layer — 实现规格

> 加载 brain_regions.json + tripartite_model.json + W_sensory.json + situation_primitives.json + signal_types.json 全部数据文件。版本: v1.0

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | 所有 JSON→C# record 映射 + 枚举类型 + JSON 转换器 + GameDataLoader 完整接口 + 交叉引用完整性验证 |
| 不覆盖 | term_registry.json（设计期参考，非运行时数据）；link_modulation_ceiling_v2.json（待 Engine 层确认需求） |
| 前置依赖 | data/brain_regions.json, data/connectivity/tripartite_model.json, data/connectivity/W_sensory.json, data/connectivity/situation_primitives.json, data/signal_types.json |
| 阻塞 | Engine Layer（WcState 需要 GameDataLoader 产出） |

## 二、数据结构

### 2.1 已实现（纳入一致性核查，不重写）

#### BrainEnums.cs — 13 enum 类型

| Enum | 值 | JSON 值 | 来源 | 可空 |
|------|-----|---------|------|------|
| `Timescale` | Fast, Medium, Slow | fast, medium, slow | brain_regions.function_profile.timescale | FunctionProfile 中可空 |
| `CstcLoop` | None, Somatic, Limbic, Cognitive, Global | none, somatic, limbic, cognitive, global | brain_regions + cstc edges | 可空 |
| `CstcRole` | None, CorticalInput, StriatalGate, PallidalOutput, ThalamicRelay, Modulator | none, cortical_input, ... | brain_regions.function_profile.cstc_role | 可空 |
| `HierarchyDirection` | Feedforward, Feedback, Both, Lateral | feedforward, feedback, both, lateral | CC edges + brain_regions | 非可空 |
| `GameplayDomain` | ActionGating, ArousalModulation, CognitiveControl, HabitLearning, Interoception, MemoryConsolidation, MotorExecution, RewardLearning, SensoryPerception, SocialCognition, ThalamicRelay, ThreatDefense | 对应 snake_case | brain_regions + graph nodes | 可空 |
| `BrainRegionCategory` | Cortical, Subcortical, Brainstem | cortical, subcortical, brainstem | brain_regions | 非可空 |
| `OscillatoryBand` | Alpha, Beta, Gamma, Theta | alpha, beta, gamma, theta | brain_regions | 可空 |
| `Neurotransmitter` | Gaba, Dopamine, Glutamate, Norepinephrine, Serotonin | GABA, dopamine, glutamate, norepinephrine, serotonin | brain_regions + brainstem edges | 可空 |
| `EdgeRole` | Active, Silent, Modulating | active, silent, modulating | tripartite edges | 非可空 |
| `BrainstemSystem` | LcNe, Raphe5Ht, SncDa, VtaDa | LC_NE, Raphe_5HT, SNc_DA, VTA_DA | brainstem edges | 非可空 |
| `CstcPathway` | GoDirect, NogoIndirect, StopHyperdirect, Disinhibition, Thalamocortical | go_direct, ... | cstc edges | 非可空 |
| `CstcStation` | CorticalInput, StriatalGate, PallidalOutput, ThalamicRelay, Stn | cortical_input, ..., stn | cstc edges | 非可空 |
| `BrainstemProjectionType` | DiffuseBroadcast, TargetedBroadcast | diffuse_broadcast, targeted_broadcast | brainstem edges | 非可空 |

**转换器**: `SnakeCaseEnumConverter<T>` — 泛型，JSON snake_case_lower ↔ C# PascalCase，大小写不敏感反序列化，含 letter↔digit 过渡处理（Raphe5Ht → raphe_5ht）。

#### 脑区与三体模型 Records

| Record | 字段数 | JSON 源 | 文件 |
|--------|--------|---------|------|
| `FunctionProfile` | 11 | brain_regions.function_profile | Data/FunctionProfile.cs |
| `BrainRegion` | 16 | brain_regions 单个 entry | Data/BrainRegion.cs |
| `BrainRegionsData` | 1 (dict) | brain_regions.json 根 | Data/BrainRegionsData.cs |
| `FunctionLabel` | 4 | tripartite edges function_label[] | Data/FunctionLabel.cs |
| `GraphNode` | 13 | tripartite graph_nodes | Data/GraphNode.cs |
| `NodeProfile` | 7 | tripartite node_profiles | Data/NodeProfile.cs |
| `CorticocorticalEdge` | 11 | tripartite corticocortical[] | Data/TripartiteEdges.cs |
| `BrainstemProjection` | 9 | tripartite brainstem[] | Data/TripartiteEdges.cs |
| `CstcEdge` | 10 | tripartite cstc[] | Data/TripartiteEdges.cs |
| `PrivilegedPathway` | 12 | tripartite privileged_pathways[] | Data/TripartiteEdges.cs |
| `TripartiteModel` | 6 | tripartite_model.json 根 | Data/TripartiteModel.cs |

#### GameDataLoader（已实现）

| 方法 | 输入 | 输出 | 文件 |
|------|------|------|------|
| `LoadBrainRegions(string path)` | JSON 文件路径 | `BrainRegionsData` | Data/GameDataLoader.cs |
| `LoadTripartiteModel(string path)` | JSON 文件路径 | `TripartiteModel` | Data/GameDataLoader.cs |

### 2.2 待实现

#### WsensoryMatrix — 69×6 感觉模态矩阵

**JSON 源**: `data/connectivity/W_sensory.json`

```csharp
public record WsensoryMatrix
{
    /// <summary>6 种感觉模态: visual/auditory/somatosensory/pain/social_cognition/language_cognition</summary>
    public string[] Modalities { get; init; } = [];
    /// <summary>69×6 bool 矩阵，行序与 region_ids 一致</summary>
    public bool[][] Matrix { get; init; } = [];
    /// <summary>每行对应的 functional_id（69 脑区）</summary>
    public string[] RegionIds { get; init; } = [];
    /// <summary>按 functional_id 索引的行查询字典</summary>
    public Dictionary<string, Dictionary<string, int>> Rows { get; init; } = new();
}
```

**字段映射**:

| C# 属性 | JSON key | 类型 | 说明 |
|---------|----------|------|------|
| `Modalities` | modalities | string[6] | 固定 6 种 |
| `Matrix` | matrix_2d | bool[69][6] | 原始 2D 数组 |
| `RegionIds` | (来自 rows 的 key 顺序) | string[69] | functional_id 列表 |
| `Rows` | rows | dict | functional_id → {modality: 0\|1} |

#### SituationArchetype — 情境原型

**JSON 源**: `data/connectivity/situation_primitives.json`（27 个 archetype）

```csharp
public record SituationArchetype
{
    public string Name { get; init; } = "";
    public string DisplayName { get; init; } = "";
    public string Summary { get; init; } = "";
    public RdocProfile RdocProfile { get; init; } = new();
    public AppraisalProfile AppraisalProfile { get; init; } = new();
    public string[] PrimaryNetworks { get; init; } = [];
    public string[] KeyBrainRegions { get; init; } = [];
    public string[] LevelsInvolved { get; init; } = [];
    public string[] AutoActivatedLinks { get; init; } = [];
    public string TypicalGameScenario { get; init; } = "";
}

public record RdocProfile
{
    public double SocialProcesses { get; init; }
    public double NegativeValence { get; init; }
    public double CognitiveSystems { get; init; }
}

public record AppraisalProfile
{
    public string Agency { get; init; } = "";
    public string Valence { get; init; } = "";
    public double GoalRelevance { get; init; }
    public double Coping { get; init; }
    public double Certainty { get; init; }
    public double Novelty { get; init; }
    public double NormCompatibility { get; init; }
}

public record SituationPrimitives
{
    public List<SituationArchetype> Archetypes { get; init; } = [];
}
```

**rdoc_profile 字段**: social_processes, negative_valence, cognitive_systems（均为 double 0..1）
**appraisal_profile 字段**: agency ("other"/"self"/"environment"), valence ("positive"/"negative"/"neutral"), + 5 个 double 0..1

#### SignalTypesCatalog — 信号类型词表

**JSON 源**: `data/signal_types.json`

```csharp
public record SignalTypesCatalog
{
    public string Description { get; init; } = "";
    public Dictionary<string, SignalCategory> Categories { get; init; } = new();
}

public record SignalCategory
{
    public string Definition { get; init; } = "";
    public string Source { get; init; } = "";
    public Dictionary<string, SignalSubtype> Subtypes { get; init; } = new();
}

public record SignalSubtype
{
    public string Definition { get; init; } = "";
    public string[] AnatomicalCarriers { get; init; } = [];
    public string OscillatoryBand { get; init; } = "";
}
```

**categories**: excitation (5 subtypes: motor_command, sensory_feature, cognitive_goal, memory_trace, learning_signal), gating (5 subtypes: disinhibition_thalamic, sustain_working_memory, attention_enhancement, context_gating, action_selection), modulation (5 subtypes: arousal_ne, reward_da, punishment_da_signal, mood_5ht, stress_cortisol), plasticity (4 subtypes: context_code, prediction_error, pattern_separation, fear_extinction)

## 三、接口定义

### GameDataLoader（扩展后）

```csharp
public static class GameDataLoader
{
    // 已有
    public static BrainRegionsData LoadBrainRegions(string jsonPath);
    public static TripartiteModel LoadTripartiteModel(string jsonPath);

    // 新增
    public static WsensoryMatrix LoadWsensory(string jsonPath);
    public static SituationPrimitives LoadSituationPrimitives(string jsonPath);
    public static SignalTypesCatalog LoadSignalTypes(string jsonPath);
}
```

所有方法：`File.ReadAllText` → `JsonSerializer.Deserialize<T>`，反序列化失败抛 `InvalidOperationException`。

JsonSerializerOptions: `PropertyNameCaseInsensitive = true`, `ReadCommentHandling = JsonCommentHandling.Skip`。

## 四、枚举与常量

本次不新增 enum——已有的 13 个 enum 覆盖全部字段。`AppraisalProfile.Agency` / `.Valence` 等是 free-text 字符串，保持 string。

## 五、交叉引用约束

| 约束 | 来源 | 目标 | 验证方式 |
|------|------|------|----------|
| W_sensory rows 的 key 是 functional_id | rows dict keys | BrainRegionsData.Regions.Keys | 每条 row key ∈ regions |
| W_sensory matrix_2d 行序 = rows dict key 序 | matrix_2d[0..68] | rows keys 顺序 | 行数一致（69） |
| situation archetype key_brain_regions | KeyBrainRegions[] | BrainRegionsData.Regions.Keys | 每个引用 ∈ regions |
| situation levels_involved | LevelsInvolved[] | "L0".."L5" | 枚举值合法 |
| signal_types 词表格式 | subtype 的 "category/subtype" | function_label 的 signal_type | 格式校验 |

## 六、验收标准

| 编号 | 验收标准 | 验证方法 |
|------|---------|---------|
| AC-1 | `LoadWsensory` 返回 69 行 × 6 列矩阵，6 种模态标签 | 测试 |
| AC-2 | W_sensory 的 69 个 row key 全部 ∈ brain_regions functional_ids | 交叉引用测试 |
| AC-3 | `LoadSituationPrimitives` 返回 27 个 archetype | 测试 |
| AC-4 | situation archetype 中 key_brain_regions 全部 ∈ functional_ids | 交叉引用测试 |
| AC-5 | `LoadSignalTypes` 返回 4 categories × 19 subtypes | 测试 |
| AC-6 | 已有代码（BrainRegion/TripartiteModel/enums/loader）字段与 JSON 一致 | 核查（不重写） |
| AC-7 | `dotnet build` 零错误，`dotnet test` 全部通过（含已有 10 + 新增测试） | 命令验证 |

## 七、本 spec 自检清单

- [ ] 所有 JSON key 有对应 `[JsonPropertyName]` attribute
- [ ] snake_case JSON → PascalCase C# 属性名映射正确
- [ ] Nullable 字段与 JSON 可缺失 key 一致
- [ ] 数组/字典字段初始化非 null（`= []` / `= new()`）
- [ ] 每个新增类型有测试：正确记录数 + 枚举字段解析 + 交叉引用完整性
- [ ] GameDataLoader 每个方法有测试
- [ ] 新增数值参数有来源注释（JSON 文件路径 + 字段路径）

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-12 | 初稿——覆盖全部 Data Layer | 任务issue 01 | 全量审计 |

---
*创建: 2026-08-12 | 更新: 2026-08-12 | 版本: v1.0*
*关联: [脑功能层级模型](规则/技能树系统/脑功能层级模型.md), [三体神经模型](规则/技能树系统/脑功能层级模型.md) §二十*
