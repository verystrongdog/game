# #107 工作issue 03: 引擎 fail-fast——四类边 Role 加 [JsonRequired] + 回归测试 + Console 契约

> 状态：关闭 · 创建 2026-08-30 · 关闭 2026-08-31
> 标签：维度:管线, implementation
> 原始：https://github.com/verystrongdog/game/issues/107

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 状态：排队中

> **排队**：按项目 implementation 串行惯例（Grilling #104 Q3），本 issue 入队待实施。开始前基于当时最新 HEAD 增量。

## 来源

Grilling [#106](https://github.com/verystrongdog/game/issues/106)（引擎 fail-fast，2026-09-02 开题）+ #91 Q5 后置项 ③。校验脚本 `tools/validate_tripartite_annotations.py`（管线侧门禁）已实现；本 issue 补齐**引擎层防御**。

## 决策摘要（Q1-Q6 已锁定）

| # | 决策 | 内容 |
|---|------|------|
| Q1 | 机制 | `[JsonRequired]`（net8.0 原生）——4 类边 record 的 `Role` 属性声明 `[JsonRequired]`，JSON 缺失 `role` → 反序列化边界抛 `JsonException`；保持 `EdgeRole` 非可空及 `Active(0)` 既有语义。实测确认：缺失 → JsonException；`"role":null` → converter 兜底抛 JsonException；显式 `active/silent/modulating` → 正常；`PropertyNameCaseInsensitive=true` 兼容 |
| Q2 | 范围 | 仅 `Role`。真实类名：`BrainstemProjection.Role` / `CstcEdge.Role` / `CorticocorticalEdge.Role` / `PrivilegedPathway.Role`（`TripartiteEdges.cs`）——注意不是 `CstcProjection` 等。其余字段（System/Direction/Loop/Pathway…）**不**加，维持现状 |
| Q3 | 测试 | 四类边各缺 role 回归测试（复用 `Loader_BadJsonThrowsJsonException` 临时文件模式）+ `"role":null` 失败断言 + `"role":"active"` 成功正例。验收语义锁死：缺失 role → JsonException；显式 active → 正常通过（不能写成「所有 Active 都失败」） |
| Q4 | 归属 | 本独立 issue 实施；不并入 #105（无数据依赖、范围已锁）、不回写 #91（已闭合） |
| Q5 | Console 契约 | `Program.cs` 增加 `catch (JsonException ex)` → stderr「数据校验失败: {ex.Message}」+ 退出码 1；同步 Console spec AC-12；新增 Console 级缺 role 回归（复用 `InvalidArgs_Exit1` 进程测试模式，锁 stderr 内容而非仅 exit code） |
| Q6 | 延迟项 | 其余非可空枚举字段「缺失→默认 0」风险列为延迟项；触发标准 ①引擎数值消费者 ②静默错误语义 ③管线校验未覆盖 三项同时满足 → 独立评估 |

## 实施范围

1. **数据模型**：`src/YouAreNotTheFish.Core/Data/TripartiteEdges.cs` 4 类边 record（`BrainstemProjection`/`CstcEdge`/`CorticocorticalEdge`/`PrivilegedPathway`）的 `Role` 属性加 `[JsonRequired]`
2. **引擎测试**：`GameDataLoaderTests` 新增——四类边各缺 role → `Assert.Throws<JsonException>`；`"role":null` → 失败；`"role":"active"` → 成功正例
3. **Console**：`Program.cs` 加 `catch (JsonException ex)` → stderr「数据校验失败」+ exit 1
4. **Console 测试**：新增缺 role 数据 → 进程 exit 1 + stderr 含「数据校验失败」
5. **spec 同步**：`csharp-data-layer/spec.md` §四（EdgeRole 非可空行注明 JsonRequired）+ `csharp-console/spec.md` AC-12（JsonException → exit 1）

## 验收标准

- [ ] 4 类边 Role 均声明 `[JsonRequired]`
- [ ] 缺失 role → JsonException（四类各一回归）；`"role":null` → JsonException；`"role":"active"` → 正常
- [ ] Console 缺 role 数据 → exit 1 + stderr 含「数据校验失败」，无未处理异常堆栈
- [ ] 现有 309/309 测试全绿（数据门禁 `validate_tripartite_annotations.py` 仍 PASS——1049 边全含 role，无回归）
- [ ] 决策树 #106 条目 / 六维状态 / spec 落位；本 issue 关闭评论
- [ ] 延迟项（其余枚举字段静默默认风险 + ①+②+③ 触发标准）写入决策树

## 边界（不包含）

- 其余枚举字段加 `[JsonRequired]`（System/Direction/Loop/Pathway 等）→ 延迟项，触发条件成立后独立处理
- #105 P2 情境系统实施（无数据依赖，串行队列）

---

## 评论（1 条）

### verystrongdog · 2026-08-31

## ✅ 实施完成（2026-09-03，Grilling #110）

### 验收 6 项逐项核验

| # | 验收项 | 结果 | 证据 |
|---|--------|------|------|
| 1 | 4 类边 Role 均声明 `[JsonRequired]` | ✅ | `TripartiteEdges.cs` :20/:34/:49/:67（CorticocorticalEdge/BrainstemProjection/CstcEdge/PrivilegedPathway） |
| 2 | 缺 role → JsonException（四类各一）；`"role":null` → JsonException；`"role":"active"` → 正常 | ✅ | `GameDataLoaderTests.cs` +6：`Loader_MissingRole_ThrowsJsonException`（Theory ×4）/ `Loader_NullRole_ThrowsJsonException` / `Loader_ExplicitRole_LoadsFine`（Role == Active） |
| 3 | Console 缺 role → exit 1 + stderr 含「数据校验失败」，无未处理异常堆栈 | ✅ | `ConsoleAppTests.cs` `MissingRole_DataValidationFailed_Exit1`——exit 1 + stderr 含「数据校验失败」**且不含**「数据目录缺失」（Q4 防假阳性）+ 无 Unhandled |
| 4 | 现有测试全绿（数据门禁无回归） | ✅ | **353/353 全绿**（346 回归 + 7 新增）；`validate_tripartite_annotations.py` PASS（1049 边全含 role） |
| 5 | 决策树 #106 条目 / 六维状态 / spec 落位 | ✅ | 决策树 #106 条目注记「→ 见 Grilling #110（已实施）」+ 六维状态 #106 行更新 + spec 注记（#106 闭合时已同步） |
| 6 | 延迟项写入决策树 | ✅ | 决策树 #106 Q6 延迟项复核无遗漏 + #110 新增「FindDataDir 硬编码绝对路径兜底」延迟项 |

### 受影响文件

- `src/YouAreNotTheFish.Core/Data/TripartiteEdges.cs`（4 处 `[JsonRequired]`）
- `src/YouAreNotTheFish.Console/Program.cs`（`FindDataDir` 首查 `YANTF_DATA_DIR`）
- `src/YouAreNotTheFish.Core.Tests/Data/GameDataLoaderTests.cs`（+6 引擎测试）
- `src/YouAreNotTheFish.Core.Tests/ConsoleApp/ConsoleAppTests.cs`（+1 Console 进程测试）
- 文档：决策树 #106 注记 + #110 条目、六维状态、项目总览、[实现说明](../.scratch/grilling-107-fail-fast-impl/实现说明.md)、外审存档 ×3

### 提交

- `4ecdf63` feat: 四类三体边 Role 加 [JsonRequired] + YANTF_DATA_DIR 注入 + 缺 role 回归（#107）
- `c212211` docs: Grilling #110 闭合——#107 引擎 fail-fast 实施完成

### 环境注记（沙箱内可复现）

- 测试命令：`NUGET_PACKAGES=/home/dog/game/.nuget-pkgs DOTNET_ROLL_FORWARD=LatestMajor dotnet test --no-restore --no-build`（本机仅 .NET 10 运行时，net8.0 需 roll-forward；NuGet 客户端对 nuget.org 签名端点 SSL 失败，用工作区内离线缓存规避）

---
*导出: 2026-09-12 | 来源: GitHub issue*
