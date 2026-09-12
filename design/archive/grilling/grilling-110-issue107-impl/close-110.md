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
| Q1-Q6 | `design/decisions/` | §Grilling #110 | ✅ 已验证 |
| #106 注记 | `design/decisions/` | §Grilling #106 推迟段「→ 见」 | ✅ 已验证 |
| 实施（4 处 [JsonRequired] + 7 测试） | `TripartiteEdges.cs` / `GameDataLoaderTests.cs` / `ConsoleAppTests.cs` | 353/353 绿 | ✅ 已验证 |
| 六维状态 | `design/framework/six-dimensions.md` | #106 行 + 完成度 25→26 + footer | ✅ 已验证 |
| 项目总览 | `design/README.md` | 5.0 行 #107 注记 | ✅ 已验证 |
| 实现说明 | `../../设计归档/grilling/grilling-107-fail-fast-impl/实现说明.md` | 全文 | ✅ 已验证 |
| 外审存档 | `.` ×3 | — | ✅ 已验证 |

### 质量门禁（手动等效检查）

- ✅ cross-ref grep：`JsonRequired`/`YANTF_DATA_DIR` 全部命中预期位置（代码 10 + 活跃文档 13），无残留、无废弃引用
- ✅ 产物完整性：决策树条目 / 六维状态 / 项目总览 / 实现说明 / 外审存档 / 双 issue 关闭评论全部落盘
- ✅ term_registry：无新术语入库（`EdgeRole` 8 字符代码级枚举不触发 ≤4 规则；`YANTF_DATA_DIR` 为测试基础设施非设计术语；与 #106 一致）

### 推迟清单

- 其余非可空枚举字段「缺失 → 默认 0」风险 → #106 Q6 触发标准（①+②+③）未触发，独立评估
- `FindDataDir` 硬编码绝对路径兜底 → 延迟项（触发标准：移植/打包场景出现；`YANTF_DATA_DIR` 已留注入点）
- 正式校准数值 → #35；#103 artifact 校验 → #71；内容填充 / q̂ 空间差异 / D 推进 → 游戏循环实施
