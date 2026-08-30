# C# Data Layer — 实现规格

> 加载 brain_regions.json + tripartite_model.json + W_sensory.json + situation_primitives.json + signal_types.json 全部数据文件。版本: v1.2

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | 所有 JSON→C# record 映射 + 枚举类型 + JSON 转换器 + GameDataLoader 完整接口 + 交叉引用完整性验证 |
| 不覆盖 | term_registry.json（设计期参考，非运行时数据）；link_modulation_ceiling_v2.json（待 Engine 层确认需求）；link_registry.json / link_name_lookup.json（364 链路旧数据，待迁移决策） |
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
| `EdgeRole` | Active, Silent, Modulating | active, silent, modulating | tripartite edges | 非可空（⚠️ Grilling #106：4 类边 `Role` 属性加 `[JsonRequired]`——JSON 缺失 `role` → `JsonException`，禁止静默回退 Active(0)） |
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

**有意不映射的 JSON key**（System.Text.Json 静默忽略，与 §七自检第 1 条的关系见下）：
- tripartite 4 种边的 `type` key（值为 corticocortical / brainstem_broadcast / cstc / privileged_pathway——反序列化时已按所在数组确定类型，无需二次标注）
- brain_regions.json 根 `_description` / `_coordinate_system`；tripartite_model.json 根 4 个 `_` 前缀元数据 key（_description/_design_doc/_generated_by/_created——🔧 2026-08-14 Grilling #24 D-5：原"7 个"实测 4）

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
    [JsonPropertyName("modalities")]
    public string[] Modalities { get; init; } = [];

    /// <summary>69×6 int 矩阵（值 0/1），行序与 Rows 的 key 序一致</summary>
    [JsonPropertyName("matrix_2d")]
    public int[][] Matrix { get; init; } = [];

    /// <summary>functional_id → {modality: 0|1}</summary>
    [JsonPropertyName("rows")]
    public Dictionary<string, Dictionary<string, int>> Rows { get; init; } = new();

    /// <summary>每行对应的 functional_id（非 JSON 字段，由 loader 按 Rows.Keys 顺序填充）</summary>
    public string[] RegionIds { get; init; } = [];
}
```

**字段映射**:

| C# 属性 | JSON key | 类型 | 说明 |
|---------|----------|------|------|
| `Modalities` | modalities | string[6] | 固定 6 种 |
| `Matrix` | matrix_2d | int[69][6] | 值 0/1（JSON 实测为 int 非 bool） |
| `Rows` | rows | dict | functional_id → {modality: 0\|1} |
| `RegionIds` | （派生，非 JSON） | string[69] | loader 后处理：`Rows.Keys.ToArray()` |

**有意不映射**: `description` / `grilling` / `dimensions` / `modality_nodes` / `cortical_nodes_with_sensory_input` / `cortical_nodes_without_sensory_input` / `metadata`（文档性/冗余 key，运行时不需要）。

#### SituationArchetype — 情境原型

**JSON 源**: `data/connectivity/situation_primitives.json`（根 key `situation_archetypes`，27 个 archetype）

```csharp
public record SituationArchetype
{
    [JsonPropertyName("name")] public string Name { get; init; } = "";
    [JsonPropertyName("display_name")] public string DisplayName { get; init; } = "";
    [JsonPropertyName("summary")] public string Summary { get; init; } = "";
    [JsonPropertyName("rdoc_profile")] public RdocProfile RdocProfile { get; init; } = new();
    [JsonPropertyName("appraisal_profile")] public AppraisalProfile AppraisalProfile { get; init; } = new();
    [JsonPropertyName("primary_networks")] public string[] PrimaryNetworks { get; init; } = [];
    [JsonPropertyName("key_brain_regions")] public string[] KeyBrainRegions { get; init; } = [];
    [JsonPropertyName("levels_involved")] public string[] LevelsInvolved { get; init; } = [];
    /// <summary>⚠️ legacy：指向已废弃 364 链路模型（Grilling #26 前），不做校验，待 CSTC 词表迁移</summary>
    [JsonPropertyName("auto_activated_links")] public string[] AutoActivatedLinks { get; init; } = [];
    [JsonPropertyName("typical_game_scenario")] public string TypicalGameScenario { get; init; } = "";
}

/// <summary>RDoC 六域，各 archetype 只含子集 → 全部可空</summary>
public record RdocProfile
{
    [JsonPropertyName("social_processes")] public double? SocialProcesses { get; init; }
    [JsonPropertyName("negative_valence")] public double? NegativeValence { get; init; }
    [JsonPropertyName("cognitive_systems")] public double? CognitiveSystems { get; init; }
    [JsonPropertyName("positive_valence")] public double? PositiveValence { get; init; }
    [JsonPropertyName("arousal_regulatory")] public double? ArousalRegulatory { get; init; }
    [JsonPropertyName("sensorimotor")] public double? Sensorimotor { get; init; }
}

public record AppraisalProfile
{
    /// <summary>值域: circumstance | other | self（9 例各半，实测）</summary>
    [JsonPropertyName("agency")] public string Agency { get; init; } = "";
    /// <summary>值域: ambiguous | negative | positive（实测）</summary>
    [JsonPropertyName("valence")] public string Valence { get; init; } = "";
    [JsonPropertyName("goal_relevance")] public double GoalRelevance { get; init; }
    [JsonPropertyName("coping")] public double Coping { get; init; }
    [JsonPropertyName("certainty")] public double Certainty { get; init; }
    [JsonPropertyName("novelty")] public double Novelty { get; init; }
    [JsonPropertyName("norm_compatibility")] public double NormCompatibility { get; init; }
}

public record SituationPrimitives
{
    [JsonPropertyName("situation_archetypes")]
    public List<SituationArchetype> Archetypes { get; init; } = [];
}
```

**有意不映射**: 根 `_metadata` / `rdoc_domains` / `appraisal_dimensions` / `functional_networks` / `game_levels` / `composition_rules`（自描述元数据，运行时不需要）。

#### SignalTypesCatalog — 信号类型词表

**JSON 源**: `data/signal_types.json`（根 key `_categories`，4 类 18 子类）

```csharp
public record SignalTypesCatalog
{
    [JsonPropertyName("_description")] public string Description { get; init; } = "";
    [JsonPropertyName("_categories")] public Dictionary<string, SignalCategory> Categories { get; init; } = new();
}

public record SignalCategory
{
    [JsonPropertyName("definition")] public string Definition { get; init; } = "";
    [JsonPropertyName("source")] public string Source { get; init; } = "";
    [JsonPropertyName("subtypes")] public Dictionary<string, SignalSubtype> Subtypes { get; init; } = new();
}

/// <summary>子类字段按类目异构，未出现的 key 为 null</summary>
public record SignalSubtype
{
    [JsonPropertyName("definition")] public string Definition { get; init; } = "";
    [JsonPropertyName("anatomical_carriers")] public string[] AnatomicalCarriers { get; init; } = [];
    /// <summary>仅 excitation 6 子类有</summary>
    [JsonPropertyName("oscillatory_band")] public string? OscillatoryBand { get; init; }
    /// <summary>仅 modulation 5 子类有</summary>
    [JsonPropertyName("neurotransmitter")] public string? Neurotransmitter { get; init; }
    [JsonPropertyName("projection_pattern")] public string? ProjectionPattern { get; init; }
    [JsonPropertyName("target_scope")] public string? TargetScope { get; init; }
    /// <summary>仅 gating 4 子类有</summary>
    [JsonPropertyName("pathway")] public string? Pathway { get; init; }
    [JsonPropertyName("effect")] public string? Effect { get; init; }
    /// <summary>仅 plasticity 3 子类有</summary>
    [JsonPropertyName("mechanism")] public string? Mechanism { get; init; }
}
```

**词表实测内容**（2026-08-12 实测 `data/signal_types.json`）：

| 类目 | 子类数 | 子类 |
|------|--------|------|
| excitation | 6 | motor_command, sensory_feature, cognitive_goal, emotional_salience, memory_trace, social_intention |
| modulation | 5 | arousal_NE, reward_DA, motor_DA, mood_5HT, pain_opioid |
| gating | 4 | go_direct, nogo_indirect, stop_hyperdirect, disinhibition_thalamic |
| plasticity | 3 | ltp_consolidation, ltd_depression, context_code |

**有意不映射**: 根 `_usage` / `_validation_rules` / `_created` / `_grilling`（元数据）。

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

所有方法：`File.ReadAllText` → `JsonSerializer.Deserialize<T>`。

**异常行为**（三个分支由 AC-11 测试）：
- 文件不存在 → `FileNotFoundException`（.NET 内建，不包装）
- JSON 格式错误 → `JsonException`（.NET 内建，不包装）
- JSON 为 `null` 字面量 → `InvalidOperationException`（现有 `?? throw` 模式）

JsonSerializerOptions: `PropertyNameCaseInsensitive = true`, `ReadCommentHandling = JsonCommentHandling.Skip`。

**Loader 后处理**: `LoadWsensory` 反序列化后填充 `RegionIds = Rows.Keys.ToArray()`。

### GameData 聚合 + LoadAll（🔧 2026-08-14 Grilling #24 D-2 收录——审计后新增，spec v1.2 未含）

```csharp
// Data/GameData.cs（命名空间 YouAreNotTheFish.Core.Data）
public sealed record GameData(
    BrainRegionsData BrainRegions,     // brain_regions.json
    TripartiteModel Tripartite,        // connectivity/tripartite_model.json
    WsensoryMatrix Wsensory,           // connectivity/W_sensory.json（RegionIds = canonical 69）
    SituationPrimitives SituationPrimitives,  // connectivity/situation_primitives.json
    SignalTypesCatalog SignalTypes);   // signal_types.json

// GameDataLoader 新增
public static GameData LoadAll(string dataDir)
```

- `LoadAll` 一次加载 5 文件（文件名固定；路径 dataDir + 各相对路径），异常语义同现有 5 方法（FileNotFoundException/JsonException/InvalidOperationException）。
- 消费者：plan §三 CombatContext 行、§4.3 `WMatrixBuilder.Build(GameData)`、`CorticalBias.Compute(ToneState, GameData)`（csharp-engine-types spec §2.12 亦引用——跨 spec 声明，以本段为准）。

## 四、枚举与常量

本次不新增 enum——已有的 13 个 enum 覆盖全部字段。`AppraisalProfile.Agency` / `.Valence` 保持 string，值域在注释中声明（见 §2.2）。

## 五、交叉引用约束

| 约束 | 来源 | 目标 | 验证方式 |
|------|------|------|----------|
| W_sensory rows 的 key 是 functional_id | rows dict keys | BrainRegionsData.Regions.Keys | 每条 row key ∈ regions，且 69 双向双射 |
| W_sensory matrix_2d 行序 = rows key 序 | matrix_2d[i] | rows 第 i 个 key 的 {modality: 0\|1} | **逐行逐模态值比对**（69×6 全比对，非只查行数） |
| situation key_brain_regions | KeyBrainRegions[] | BrainRegionsData.Regions.Keys | 每个引用 ∈ regions（数据 2026-08-12 已修复，0 悬挂） |
| situation levels_involved | LevelsInvolved[] | "L0".."L5" | 枚举值合法 |
| signal_types 词表 membership | function_label 的 "category/subtype" | Categories.Keys + Subtypes.Keys | membership 校验（非正则格式校验；词表最大消费方——588 引用） |
| function_profile input/output_types | InputTypes[] / OutputTypes[] | 词表 "category/subtype" | membership 校验（283 引用） |
| function_label 内部一致性 | signal_type | category + "/" + subtype 拼接 | 全量比对 |
| mirror_of | FunctionProfile.MirrorOf | BrainRegionsData.Regions.Keys | 每个引用 ∈ regions |
| tripartite 边 source/target | 4 类边 | graph_nodes（小写 dk_name） | 全量比对：全部端点 ∈ graph_nodes；brainstem source 同时 ∈ brain_regions functional_ids（交集语义） |
| primary_networks | PrimaryNetworks[] | 同文件 functional_networks.networks 注册表 | membership（数据 2026-08-12 已修复，0 失配） |
| ~~auto_activated_links~~ | — | — | ⚠️ legacy 不校验（指向已废弃 364 链路模型，待 CSTC 迁移） |

## 六、验收标准

| 编号 | 验收标准 | 验证方法 |
|------|---------|---------|
| AC-1 | `LoadWsensory` 返回 69 行 × 6 列 int 矩阵，6 种模态标签，RegionIds 69 个且与 Rows.Keys 序一致 | 测试 |
| AC-2 | W_sensory 的 69 个 row key 全部 ∈ brain_regions functional_ids，且双向双射 | 交叉引用测试 |
| AC-3 | `LoadSituationPrimitives` 返回 27 个 archetype | 测试 |
| AC-4 | situation archetype 中 key_brain_regions 全部 ∈ functional_ids | 交叉引用测试 |
| AC-5 | `LoadSignalTypes` 返回 4 categories × 18 subtypes（6/5/4/3） | 测试 |
| AC-6 | 已有代码（BrainRegion/TripartiteModel/enums/loader）字段与 JSON 一致 | 一次性审计产物（sign-off 记录，不自动化——JSON 新增 key 会被静默忽略，测试无法发现） |
| AC-7 | `dotnet build` 零错误，`dotnet test` 全部通过（含已有 10 + 新增测试） | 命令验证 |
| AC-8 | matrix_2d 行序与 rows 逐行逐模态值一致（69×6 全比对） | 测试 |
| AC-9 | levels_involved 全部 ∈ {L0..L5} | 测试 |
| AC-10 | function_label signal_type 与 input/output_types 全部 ∈ 词表；signal_type == category/subtype 拼接 | membership 测试 |
| AC-11 | loader 异常三分支：缺文件 → FileNotFoundException；坏 JSON → JsonException；null 字面量 → InvalidOperationException | 测试 |
| AC-12 | primary_networks 全部 ∈ 同文件 functional_networks 注册表 | membership 测试 |
| AC-13 | mirror_of 目标全部 ∈ functional_ids（2 条） | membership 测试 |
| AC-14 | tripartite 4 类边 1049 条 source/target 全部 ∈ graph_nodes；brainstem source 同时 ∈ functional_ids | membership 测试 |

> 注：auto_activated_links 为 legacy 字段（见 §五 C11），有意不做 membership 校验，不在任何 AC 中要求。

## 七、本 spec 自检清单

- [ ] 所有 JSON key 有对应 `[JsonPropertyName]` attribute **或列入"有意不映射"清单**
- [ ] snake_case JSON → PascalCase C# 属性名映射正确（下划线 key 必须显式 attribute，不依赖 case-insensitive）
- [ ] Nullable 字段与 JSON 可缺失 key 一致（RdocProfile 6 域 / SignalSubtype 异构字段全 nullable）
- [ ] 数组/字典字段初始化非 null（`= []` / `= new()`）
- [ ] 每个新增类型有测试：正确记录数 + 字段解析 + 交叉引用完整性
- [ ] GameDataLoader 每个方法有测试（含异常三分支）
- [ ] 新增数值参数有来源注释（JSON 文件路径 + 字段路径）
- [ ] 派生字段（RegionIds）有填充逻辑说明

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-12 | 初稿——覆盖全部 Data Layer | 任务issue 01 | 全量审计 |
| v1.1 | 2026-08-12 | 修复审计 E1-E6 + W 级：§2.2 补 [JsonPropertyName]×41；Matrix→int[][]; RdocProfile 6 域可空；SignalSubtype 异构字段全量可空；signal_types 词表更新为实测 18 子类；agency/valence 值域修正；AC-4/AC-12 数据修复（悬挂引用+注册表对齐）；AC-6 改为一次性审计产物；AC-8~12 新增；约束表扩至 11 条 | 审计退回（report.md 2026-08-12） | Δ审计（§2.2 + §五 + §六 + §七） |
| v1.2 | 2026-08-12 | Δ审计"有条件通过"补修：AC-13（mirror_of membership）/AC-14（1049 三体边 membership）新增；auto_activated_links 豁免在 AC 层注明；文本修正（词表最大消费方备注移位、约束8 来源列、异常行为时态、约束9 交集语义） | Δ审计结论（report.md v1.1 段） | 免重审（数据侧三路实测闭环） |
| v1.3 | 2026-08-14 | Grilling #24 文档同步：D-2 收录 GameData + LoadAll（§三 新增段）；D-5 tripartite 根 `_` key 7→4；SituationPrimitives.cs 注释历史口径修正 | Grilling #24 盘点（引擎数据层偏差清单 D-2/D-5） | 免重审（纯文档同步） |
| v1.4 | 2026-09-02 | Grilling #106：EdgeRole 行注明 4 类边 Role 加 `[JsonRequired]`（缺失 → JsonException） | Grilling #106 引擎 fail-fast（实施 #107） | 免重审（实现细节同步，随 #107 测试验证） |

---
*创建: 2026-08-12 | 更新: 2026-08-12 | 版本: v1.2*
*关联: [脑功能层级模型](规则/技能树系统/脑功能层级模型.md), [三体神经模型](规则/技能树系统/脑功能层级模型.md) §二十*
