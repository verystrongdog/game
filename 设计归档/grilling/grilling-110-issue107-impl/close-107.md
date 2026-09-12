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
- 文档：决策树 #106 注记 + #110 条目、六维状态、项目总览、[实现说明](../grilling-107-fail-fast-impl/%E5%AE%9E%E7%8E%B0%E8%AF%B4%E6%98%8E.md)、外审存档 ×3

### 提交

- `4ecdf63` feat: 四类三体边 Role 加 [JsonRequired] + YANTF_DATA_DIR 注入 + 缺 role 回归（#107）
- `c212211` docs: Grilling #110 闭合——#107 引擎 fail-fast 实施完成

### 环境注记（沙箱内可复现）

- 测试命令：`NUGET_PACKAGES=/home/dog/game/.nuget-pkgs DOTNET_ROLL_FORWARD=LatestMajor dotnet test --no-restore --no-build`（本机仅 .NET 10 运行时，net8.0 需 roll-forward；NuGet 客户端对 nuget.org 签名端点 SSL 失败，用工作区内离线缓存规避）
