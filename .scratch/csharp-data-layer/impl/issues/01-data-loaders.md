# 工作issue 01: W_sensory / situation_primitives / signal_types 加载器

> Status: resolved | Type: implementation | 维度: 管线 | Spec: ../../design/spec.md@v1.2 | Blocked by: sign-off ✅ (2026-08-12) | GitHub: [#43](https://github.com/verystrongdog/game/issues/43)

## 范围

按 spec v1.2 §2.2 + §三 实现：

- 新 record：`WsensoryMatrix`（含 `RegionIds` 派生填充）、`SituationArchetype` + `RdocProfile`（6 域可空）+ `AppraisalProfile` + `SituationPrimitives`、`SignalTypesCatalog` + `SignalCategory` + `SignalSubtype`（异构字段可空）
- `GameDataLoader` 扩展：`LoadWsensory` / `LoadSituationPrimitives` / `LoadSignalTypes`（沿用现有 Options 与 `?? throw` 模式）
- 测试覆盖 AC：AC-1, AC-2, AC-3, AC-4, AC-5, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14（AC-6 为一次性审计产物、AC-7 为 build/test 门禁）

## 文件所有权声明

- `src/YouAreNotTheFish.Core/Data/WsensoryMatrix.cs` — 新建
- `src/YouAreNotTheFish.Core/Data/SituationPrimitives.cs` — 新建（SituationArchetype/RdocProfile/AppraisalProfile/SituationPrimitives 四类型）
- `src/YouAreNotTheFish.Core/Data/SignalTypesCatalog.cs` — 新建（SignalTypesCatalog/SignalCategory/SignalSubtype 三类型）
- `src/YouAreNotTheFish.Core/Data/GameDataLoader.cs` — 扩展（3 新方法 + LoadWsensory 的 RegionIds 后处理）
- `src/YouAreNotTheFish.Core.Tests/Data/GameDataLoaderTests.cs` — 扩展（新测试 + 现有 2 测试的 membership 断言扩展）

## 完成标准

spec v1.2 §六 AC-1~5、AC-8~14 逐条 ✅ + `dotnet build` 零错误 + `dotnet test` 全绿。

## ⚠️ 结转验证（来自 sign-off 结转清单）

| # | 结转项 | 验证方式 |
|----|--------|---------|
| 1 | Matrix 行序 == Rows.Keys 序的显式断言（W-6） | AC-8 测试内加行序断言 |
| 2 | AC-11 异常三分支（FileNotFoundException/JsonException/InvalidOperationException） | 3 个新测试 |
| 3 | AC-14 覆盖 brainstem target + privileged_pathways source/target membership | membership 测试 |
| 4 | AC-12 注册表另读原始 JSON（SituationPrimitives 未映射 functional_networks） | 测试内直接读 JSON |
| 5 | 现有测试扩展：mirror_of membership + PrivilegedPathway membership | 扩展现有 2 测试 |

## 实现

- commit `4c752c2`: 三个新 record 文件 + GameDataLoader 扩展（3 方法 + RegionIds 后处理）
- commit `e480707`: 测试（+14 个新测试，24/24 绿）

## 代码自审（证据式）

### 门禁证据

- [x] `dotnet build` 零错误 — `Build succeeded. 0 Error(s)`（2 个 NU1900 警告为 NuGet 网络不可达的环境警告，非代码警告）
- [x] `dotnet test` 全绿 — `Passed! - Failed: 0, Passed: 24, Skipped: 0, Total: 24`

### 验收标准逐条对照

| AC | 验收标准 | 状态 | 证据 |
|----|---------|------|------|
| AC-1 | LoadWsensory 69×6 int 矩阵 + 6 模态 + RegionIds 69 且序一致 | ✅ | `LoadWsensory_DimensionsModalitiesAndRegionIds` |
| AC-2 | 69 row key ∈ functional_ids 双向双射 | ✅ | `LoadWsensory_RowKeysAreFunctionalIdsBidirectional` |
| AC-3 | LoadSituationPrimitives 27 archetype | ✅ | `LoadSituationPrimitives_Loads27Archetypes` |
| AC-4 | key_brain_regions ∈ functional_ids | ✅ | `LoadSituationPrimitives_KeyBrainRegionsAreFunctionalIds` |
| AC-5 | 4 categories × 18 subtypes（6/5/4/3） | ✅ | `LoadSignalTypes_CategoriesAndSubtypeCounts`（含异构字段抽查） |
| AC-6 | 已有代码一致性 | ✅ | 一次性审计产物——见 design/audit/report.md（§2.1 100 字段 ✅） |
| AC-7 | build 零错误 + test 全绿 | ✅ | 门禁证据（24/24） |
| AC-8 | matrix 行序与 rows 逐行逐模态一致 | ✅ | `LoadWsensory_MatrixRowsMatchRowsCellByCell` |
| AC-9 | levels_involved ∈ L0..L5 | ✅ | `LoadSituationPrimitives_LevelsAreL0ToL5` |
| AC-10 | function_label + types ∈ 词表；signal_type 拼接一致 | ✅ | `FunctionLabelsAndTypesAreInVocabulary` |
| AC-11 | 异常三分支 | ✅ | `Loader_MissingFileThrowsFileNotFoundException` / `Loader_BadJsonThrowsJsonException` / `Loader_NullLiteralThrowsInvalidOperationException` |
| AC-12 | primary_networks ∈ 注册表 | ✅ | `LoadSituationPrimitives_PrimaryNetworksMatchInFileRegistry` |
| AC-13 | mirror_of ∈ functional_ids（2 条） | ✅ | `MirrorOfTargetsAreFunctionalIds` |
| AC-14 | 1049 条三体边 membership（brainstem 交集语义） | ✅ | `AllTripartiteEdgesAreWithinGraphNodes` |

### spec §七 自检清单

- [x] 所有 JSON key 有 [JsonPropertyName] 或列入"有意不映射"清单（4 组清单已在 §2.1/§2.2 声明）
- [x] snake_case 映射正确（下划线 key 全部显式 attribute，含 _categories/_description）
- [x] Nullable 与 JSON 可缺失 key 一致（RdocProfile 6 域、SignalSubtype 异构字段全 nullable——实测 27 archetype 0 解析失败）
- [x] 数组/字典字段初始化非 null（`= []` / `= new()`）
- [x] 每个新增类型有测试（计数 + 字段解析 + 交叉引用）
- [x] loader 每个方法有测试（含异常三分支）
- [x] 数值参数来源注释（JSON 路径 + 字段路径在 XML doc）
- [x] 派生字段 RegionIds 填充逻辑（LoadWsensory `with { RegionIds = Rows.Keys.ToArray() }`）

### ⚠️ 结转验证（来自 sign-off 结转清单）

| # | 结转项 | 验证结果 |
|----|--------|---------|
| 1 | Matrix 行序 == Rows.Keys 序显式断言（W-6） | ✅ `LoadWsensory_MatrixRowsMatchRowsCellByCell` 每行断言 `rowKeys[i] == RegionIds[i]` |
| 2 | AC-11 异常三分支 | ✅ 3 个测试（缺失文件/坏 JSON/null 字面量） |
| 3 | AC-14 覆盖 brainstem target + privileged source/target | ✅ `AllTripartiteEdgesAreWithinGraphNodes` 全 4 类边 |
| 4 | AC-12 注册表另读原始 JSON | ✅ 测试内 JsonDocument 直接读 functional_networks |
| 5 | 现有测试扩展 membership 断言 | ✅ `EnumFieldsAreParsedCorrectly` 加 mirror membership；`PrivilegedPathwayFieldsExist` 加端点 membership |

### 发现的问题

| # | 问题 | 处置 |
|----|------|------|
| 1 | 缺失文件在「目录不存在」时抛 DirectoryNotFoundException 而非 FileNotFoundException（.NET 行为） | 测试用「目录存在+文件缺失」路径（AC-11 真实语义）；spec 文本无需改（"文件不存在"即指此语义） |
| 2 | 解决方案级 build 出现 NU1900 警告（NuGet 网络不可达） | 环境问题，与代码无关；已如实记录 |

## Comments
