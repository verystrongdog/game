# #110 [Grilling] #107 实施执行层（引擎 fail-fast）

> 状态：关闭 · 创建 2026-08-31 · 关闭 2026-08-31
> 标签：维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/110

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

工作issue 03 #107（引擎 fail-fast——四类三体边 Role 加 `[JsonRequired]` + 回归测试 + Console 契约）的实施执行层定案。承接: Grilling #106（2026-09-02 闭合，Q1-Q7 已把机制/范围/测试/归属/Console 契约/延迟项全部锁死，即 #107 的规格）；阻塞: 无（串行队列中 #105 已完成并合回 main，轮到 #107）。

## 六维定位

维度: 管线（怎么造出来、怎么验证）——引擎数据层反序列化边界防御的实施。

## 当前状态（2026-09-03 核查）

| 项 | 状态 |
|----|------|
| `Program.cs` catch JsonException → stderr「数据校验失败」+ exit 1 | ✅ 已存在（98d5b27，#109 T7 为 #108 Q11 门禁分层引入，覆盖 #106 Q5） |
| 两个 spec 同步（data-layer §四 v1.4 + console AC-12 v1.3） | ✅ 已存在（fdae389，#106 闭合时完成） |
| 决策树 #106 条目（含 Q6 延迟项）+ 六维状态 #106 行 | ✅ 已存在 |
| `TripartiteEdges.cs` 4 类边 Role 加 `[JsonRequired]` | ❌ 待实施（剩余核心工作） |
| 引擎回归测试（四类缺 role / `"role":null` / `"role":"active"` 正例） | ❌ 待实施 |
| Console 缺 role 进程测试（exit 1 + stderr 含「数据校验失败」） | ❌ 待实施 |
| 全绿回归 + 关闭 #107 + 总结评论 | ❌ 待实施 |

环境已验证：基线 346/346 全绿；build 可行（NUGET_PACKAGES 重定向 + roll-forward）；`.gitignore` 已补 `.nuget-pkgs/`。

## 执行形态（Q1 已定）

方案 A：执行层决策 + 本会话直接实施并关闭 #107（#109 Q6 先例）。

---

## 评论（5 条）

### verystrongdog · 2026-08-31

## 决策记录（Q1-Q2）

| # | 决策 | 内容 | 来源 |
|---|------|------|------|
| Q1 | 执行形态 | 方案 A——执行层决策 + 本会话直接实施并关闭 #107（#109 Q6 先例） | 用户采纳推荐 |
| Q2 | 分支策略 | **main 直改**——改动面 1 源文件 + 2 测试文件 + 关闭文档，边界封闭（无数据/schema/跨模块变更），346 基线 + 新增一步回归；#91/#106 同量级惯例；`feat/107-fail-fast` 无实质风险隔离 | 外审 [t_6a9508b77b948191876d5d95bacc1437](https://chatgpt.com/s/t_6a9508b77b948191876d5d95bacc1437) 采纳 |

**Q2 定案要点（外审原文）**：改动面很小、边界封闭、验证一次完成、近期惯例匹配 → main 直改。

### verystrongdog · 2026-08-31

## Q3 定案 — 提交分批

**两 commit**（用户采纳推荐）：
1. `feat:` — `TripartiteEdges.cs`（4 个 `[JsonRequired]`）+ 全部新测试（引擎 6 + Console 1，就近落位）——同一 fail-fast 特性
2. `docs:` — 决策树 #106 注记实施完成 + Grilling #110 条目 + 六维状态 + 项目总览核查

### verystrongdog · 2026-08-31

## Q4 定案 — Console 进程测试数据注入机制

**方案 (a)：`YANTF_DATA_DIR` 环境变量**（外审 t_6a950e055ad48191af18928a592bacb5 终局确认 + 用户采纳）。

| 项 | 定案 |
|----|------|
| 注入语义 | `FindDataDir` 首查 `YANTF_DATA_DIR`：已设置 → 用之；未设置 → 完全走现有发现策略（生产行为零变化） |
| Console 夹具 | 临时目录 = 真实 `brain_regions.json` + 缺 role 的 `tripartite_model.json`（仅此两文件；`LoadAll` 中 tripartite 第 2 个加载，先于后续 FileNotFound） |
| 夹具输入 | **缺 role**（非 `role:null`）——还原 #92 事故原貌，端到端验证 `[JsonRequired]` 路径；`null` 路径由引擎级测试 + #106 Q1 实测覆盖 |
| 防假阳性断言（外审新增价值，采纳） | exit 1 + stderr **含**「数据校验失败」**且不含**「数据目录缺失」——夹具缺后续文件走 FileNotFound（错误路径）时断言失败 |
| 无未处理异常堆栈 | stderr 不含未处理异常堆栈标记（#106 Q5 原文要求） |
| 范围 | 不改 CLI / 不扩公开 spec / 不增加用户可见参数——测试后门不升级为产品功能 |

三层职责（外审表）：#106 Q1 `role:null` → converter 兜底路径；#106 Q3 `role:null` 等 → 引擎级非法输入；#107 Console **缺 role** → `[JsonRequired]` → fail-fast 端到端链路。

### verystrongdog · 2026-08-31

## Q5 定案 — 问题处置机制

**产出** `.scratch/grilling-107-fail-fast-impl/实现说明.md`（#96/#109 同构）——记录机械实现自主决策（引擎测试临时 JSON 最小结构 / active 正例单条覆盖 / FindDataDir env 覆盖实现位置 / 新增测试数 346→353）+ 数值不匹配如实呈现 + 设计越界另开轮。

### verystrongdog · 2026-08-31

## ✅ Grilling #110 闭合（2026-09-03）

### 决策表（Q1-Q6）

| # | 决策 | 内容 | 定案方式 |
|---|------|------|----------|
| Q1 | 执行形态 | 方案 A——执行层决策 + 本会话直接实施并关闭 #107（#109 Q6 先例） | 用户采纳推荐 |
| Q2 | 分支策略 | **main 直改**——改动面小、边界封闭、346 基线一步回归；`feat/107-fail-fast` 无实质风险隔离 | 外审 [t_6a9508b77…](https://chatgpt.com/s/t_6a9508b77b948191876d5d95bacc1437) 采纳 |
| Q3 | 提交分批 | 两 commit——feat（代码+全部测试）/ docs（关闭文档） | 用户采纳推荐 |
| Q4 | Console 测试注入 | **`YANTF_DATA_DIR` 环境变量**（FindDataDir 首查，生产零变化）；夹具 2 文件（真实 brain_regions + 缺 role tripartite）；**防假阳性断言**（stderr 含「数据校验失败」且不含「数据目录缺失」）；夹具用**缺 role**（还原 #92 事故） | 外审 [t_6a950b659…](https://chatgpt.com/s/t_6a950b6597d48191a0ab54d5abf3e0af) + [t_6a950e055…](https://chatgpt.com/s/t_6a950e055ad48191af18928a592bacb5) 两轮定案 |
| Q5 | 问题处置 | 产出 `实现说明.md`（#96/#109 同构） | 用户选产出 |
| Q6 | 验收关闭 | #107 验收 6 项逐项核验 + 门禁复核 + 双 issue 关闭评论；实施不做外部评审 | 用户确认 |

### 实施结果

- **353/353 测试全绿**（346 回归 + 7 新增，一次通过）；`validate_tripartite_annotations.py` PASS（1049 边全含 role，无回归）
- commit `4ecdf63`（feat）+ `c212211`（docs）
- 相关 issue：#107（implementation）已关闭

### 写入验证表

| 决策 | 写入文件 | 位置 | 验证 |
|------|----------|------|------|
| Q1-Q6 | `docs/决策树.md` | §Grilling #110 | ✅ 已验证 |
| #106 注记 | `docs/决策树.md` | §Grilling #106 推迟段「→ 见」 | ✅ 已验证 |
| 实施（4 处 [JsonRequired] + 7 测试） | `TripartiteEdges.cs` / `GameDataLoaderTests.cs` / `ConsoleAppTests.cs` | 353/353 绿 | ✅ 已验证 |
| 六维状态 | `docs/设计框架-六维状态.md` | #106 行 + 完成度 25→26 + footer | ✅ 已验证 |
| 项目总览 | `项目总览.md` | 5.0 行 #107 注记 | ✅ 已验证 |
| 实现说明 | `.scratch/grilling-107-fail-fast-impl/实现说明.md` | 全文 | ✅ 已验证 |
| 外审存档 | `.scratch/grilling-110-issue107-impl/` ×3 | — | ✅ 已验证 |

### 质量门禁（手动等效检查）

- ✅ cross-ref grep：`JsonRequired`/`YANTF_DATA_DIR` 全部命中预期位置（代码 10 + 活跃文档 13），无残留、无废弃引用
- ✅ 产物完整性：决策树条目 / 六维状态 / 项目总览 / 实现说明 / 外审存档 / 双 issue 关闭评论全部落盘
- ✅ term_registry：无新术语入库（`EdgeRole` 8 字符代码级枚举不触发 ≤4 规则；`YANTF_DATA_DIR` 为测试基础设施非设计术语；与 #106 一致）

### 推迟清单

- 其余非可空枚举字段「缺失 → 默认 0」风险 → #106 Q6 触发标准（①+②+③）未触发，独立评估
- `FindDataDir` 硬编码绝对路径兜底 → 延迟项（触发标准：移植/打包场景出现；`YANTF_DATA_DIR` 已留注入点）
- 正式校准数值 → #35；#103 artifact 校验 → #71；内容填充 / q̂ 空间差异 / D 推进 → 游戏循环实施

---
*导出: 2026-09-12 | 来源: GitHub issue*
