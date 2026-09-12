# Grilling #71 数值平衡工具方案 — 实施任务计划

> Grilling #71 (GitHub #71) 结论：设计数值平衡工具（蒙特卡洛战斗模拟 + 参数校准），作为 E-5 校准常量群与 #35 校准 grilling 的执行载体。6 项共识：C# 模拟器 + Python 分析壳 / T0-T3 校准优先级 / 五组指标 / 独立 Balance 工程 / demo+§4.1 全模板（含 F-5 修表）/ T1-T8 任务分解。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [工具架构](#三工具架构)
4. [CLI 规格](#四cli-规格)
5. [验证指标集](#五验证指标集)
6. [校准目标与优先级](#六校准目标与优先级)
7. [接口契约与前置](#七接口契约与前置)
8. [任务分解](#八任务分解)
9. [文件清单](#九文件清单)
10. [数据契约与校验](#十数据契约与校验)
11. [验收标准](#十一验收标准)
12. [推迟清单](#十二推迟清单)

---

## 一、背景与动机

引擎核心已交付（294/294 绿，确定性 RNG 注入，同种子同输出），但 E-5 校准常量群（[引擎数据关系规格 §七](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%BC%95%E6%93%8E%E6%95%B0%E6%8D%AE%E5%85%B3%E7%B3%BB%E8%A7%84%E6%A0%BC.md)）全部为 `[NEW]` 占位：`δ_scale=0.3`、`M1SustainPenalty=-0.1`、`PerceptionThreshold=0.15`、`ScaleMental=1.0(禁用)`、`MaxRounds=50`、4 静息常量（`SpeedScoreCalculator` 硬编码）。#35（战斗输出权重校准）因"缺少实现反馈"暂停（#35 body）——本工具正是该反馈的提供者。战斗长度目标（杂兵 4-6 / 精英 8-10 / Boss 16-20 回合，[核心机制 §10.2](../../../%E8%A7%84%E5%88%99/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md)）是"引擎产生合理战斗结果"的第一门禁。

承接 [Grilling #70 P0 并行校准轨](./../grilling-70-engine-roadmap/task-plan.md) §四。

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | 工具形态 = **C# 批量模拟器 + Python 分析壳**（C# 驱动引擎确定性批量，Python 只做聚合/图表/报告，零公式复刻） | 架构 |
| D2 | 校准优先级 = **T0 战斗长度 → T1 #35 权重组 → T2 E-5 动力学群 → T3 Δm 成长曲线** | 优先级 |
| D3 | 验证指标 = **五组全含**（战斗结算/动力学健康/SAN 行为/速度/成长） | 指标 |
| D4 | 工程形态 = **独立 `YouAreNotTheFish.Balance` 控制台工程**，CLI 参数扫描，输出 `data/calibration/`（raw+reports 分离） | 架构 |
| D5 | 场景模板 = demo 模板 + 敌人与事件 §4.1 权威表全敌人类型（三档覆盖）；**顺带修 F-5 旧值表** | 数据 |
| D6 | 任务划分 = T1-T8；**校准决策归 #35 grilling**（工具只报指标，不自动改 CalibrationConfig） | 范围 |

## 三、工具架构

```
┌─ C# 侧：YouAreNotTheFish.Balance（新工程，引用 YouAreNotTheFish.Core）──────────┐
│  CLI 解析 → 场景模板库（JSON）→ 批量模拟循环（N 场 × 参数矩阵扫描）                │
│  每场: TurnManager.StepRound × N 回合（确定性 IRng 注入，seed 派生 per-battle）     │
│  产出: 每场摘要 JSON（五组指标原始值 + 事件日志指针）                               │
└──────────────────────────┬──────────────────────────────────────────────────────┘
                           │ data/calibration/raw/<run>.json
┌─ Python 侧：tools/balance_report.py（分析壳，零公式复刻）────────────────────────┐
│  读 raw → 聚合（中位数/分位数/直方图/分布）→ data/calibration/reports/<run>.md     │
│  + 可选图表（matplotlib: 回合数直方图/tone 动态范围热力图）                          │
└──────────────────────────────────────────────────────────────────────────────────┘
```

**零漂移原则**：C# 侧直接调用引擎 `TurnManager`/`DamageCalculator` 等真实代码路径（294/294 测试保障）；Python 侧只读 JSON 做统计，**不接触任何公式**。校准常量注入经 `CombatContext.Calibration`（instance record，见 §七）。

## 四、CLI 规格

```
dotnet run --project src/YouAreNotTheFish.Balance -- \
  --battles 1000          # 每配置场次数
  --seed 42               # 全局种子（确定性可复现；per-battle 种子 = hash(seed, battleIndex, config)）
  --scan <param>:<min>:<max>:<steps>   # 参数矩阵扫描（可重复指定多参数；参数 ∈ CalibrationConfig 字段）
  --scenario 轻度病人      # 场景模板名（demo / 轻度病人 / 中度病人 / 重度病人 / 投影 / 碎片 / 完整体 / 医疗人员）
  --out data/calibration/raw/run-01.json
```

- `--scan` 不指定 → 单配置运行（用 CalibrationConfig 默认值）
- 多参数 `--scan` → 笛卡尔积（输出标注每个 cell 的参数组合）
- 确定性保证：同 `--seed` 同参数 → 逐位同输出（引擎 SmokeTests AC-8 契约延续）
- 静息常量扫描前置：T1（E-3 去硬编码）完成后 `SpeedM1Rest*` 进入 CalibrationConfig 才可 `--scan`

## 五、验证指标集

每场战斗输出原始值，批量聚合为报告：

| 组 | 指标（每场） | 聚合（报告） | 服务校准项 |
|----|-------------|-------------|-----------|
| **战斗结算** | 回合数 / 胜负 / 结束方式（HP=0, SAN=0, 超时） / HP·SAN 残量 | 回合数中位数+P10-P90+直方图；胜率；结束方式占比；残量分布 | T0 |
| **动力学健康** | 4 tone 每回合值序列 / 3 环路 gate 值 / a(t) 激活带 | tone min/max/饱和率（=1.0 占比）/死区率（<0.01 占比）；gate 均值+分布（防 step 6 gate 恒 1 惰性复发）；a(t) 直方图 | T2 |
| **SAN 行为** | SAN 阈值跨越次数（60/30/15）/ 恐慌回合占比 / 随机行为回合数 | 跨越次数分布；恐慌/随机占比 | T2（C1 频率验证） |
| **速度** | 先手者 / 行动顺序序列 | 先手率；顺序分布 | 验证速度排序 |
| **成长** | 参战链路激活次数 n / Δm 逐次值（公式层） | Δm 总和分布；按层级分解；m 增长曲线（跨战斗） | T3 |

## 六、校准目标与优先级

| 组 | 参数 | 当前值 | 校准依据 | 工具方式 |
|----|------|--------|---------|---------|
| T0 | 杂兵/精英/Boss 战斗回合数 | demo HP15 | 核心机制 §10.2：4-6/8-10/16-20 | 场景模板×默认常量 → 回合数分布 vs 目标区间 |
| T1 | scale_mental / θ_mem / 精神攻击节点集 | 1.0(禁用) / 待定 | #35 开放 issue | `--scan scale_mental:...` + 节点集调参（#35 裁决） |
| T2 | δ_scale / M1SustainPenalty / PerceptionThreshold / 4 静息常量 | 0.3 / −0.1 / 0.15 / M1 实测 | 引擎数据关系规格 §七 | `--scan` 矩阵 → tone 动态范围/gate/察觉分 |
| T3 | Δm 公式曲线（base(L)×f(m)×g(n)） | 正典已定 | 核心机制 §1.3 | **Python 公式验证脚本**（非引擎——Δm 属 P1b LinkState，引擎未实现；验证正典公式本身，非复刻引擎） |

## 七、接口契约与前置

| 项 | 状态 | 说明 |
|----|------|------|
| CalibrationConfig 注入 | ✅ 已就位 | instance record + static Default（`CalibrationConfig.cs` 注释：sign-off 结转 #4 蒙特卡洛参数 sweep 需要实例化注入）；经 `CombatContext.Calibration` 传递 |
| E-3 前置（T1） | ⚠️ 需做 | 4 静息常量硬编码于 `SpeedScoreCalculator.cs:21-30` → 迁入 CalibrationConfig（[#70 已归 P0](./../grilling-70-engine-roadmap/task-plan.md)） |
| m_default 注入 | ⚠️ 小改 | `WMatrixBuilder.cs:63` 读 `CalibrationConfig.Default.MDefault`（static）→ 如需 m 扫描需将 config 传入 Build 签名 |
| T3 Δm | ⚠️ 不在引擎 | Δm 属 P1b LinkState——本次用 Python 公式验证（`tools/validate_dm_curve.py`），引擎内验证延后 P1b |
| 校准决策归属 | ✅ 已定 | 工具只产报告；常量值由 #35 grilling 裁决后回填 CalibrationConfig |

## 八、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | E-3 前置：4 静息常量迁入 CalibrationConfig，SpeedScoreCalculator 去硬编码 | 代码 | `CalibrationConfig.cs` + `SpeedScoreCalculator.cs` + 测试 | — |
| T2 | 新建 `YouAreNotTheFish.Balance` 工程（CLI 解析 + 场景模板加载 + 输出框架） | 代码 | `src/YouAreNotTheFish.Balance/` | T1 |
| T3 | 场景模板库：demo + 敌人与事件 §4.1 全敌人类型（取中值）→ JSON | 数据 | `data/calibration/scenarios.json` | D5 |
| T4 | 批量模拟器核心：N 场循环 + 参数矩阵扫描 + 每场五组指标原始值 + 确定性 JSON 输出 | 代码 | `data/calibration/raw/<run>.json` | T2/T3 |
| T5 | Python 分析壳 `tools/balance_report.py`：五组指标聚合 + 报告 md + 图表 | 代码 | `data/calibration/reports/<run>.md` | T4 |
| T6 | T0 校准执行：demo/全敌人模板 × 默认常量 → 回合数分布报告 | 执行 | 首份校准报告 | T4/T5 |
| T7 | F-5 修表：核心机制 §10.1 + 敌人与事件 §十二 敌人 HP 旧值 → 新值（§4.1 权威表） | 文档 | 两处表格 | D5 |
| T8 | 文档同步：决策树 #71 / 六维状态管线队列 / memory | 文档 | — | 全部 |

> T3（校准目标组）执行于 T6 之后或与 #35 并行：`tools/validate_dm_curve.py` 独立公式验证。

## 九、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `src/YouAreNotTheFish.Balance/`（Program/CLI/Simulator/ScenarioLoader） | 新建 | 代码 |
| `src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` | 改写（+4 静息常量） | 代码 |
| `src/YouAreNotTheFish.Core/Engine/SpeedScoreCalculator.cs` | 改写（去硬编码） | 代码 |
| `src/YouAreNotTheFish.Core.Tests/`（E-3 常量注入测试） | 新增 | 测试 |
| `data/calibration/scenarios.json` | 新建 | 数据 |
| `data/calibration/raw/`（运行时产物） | 新建目录 | 产物 |
| `data/calibration/reports/`（运行时产物） | 新建目录 | 产物 |
| `tools/balance_report.py` | 新建 | 代码 |
| `tools/validate_dm_curve.py` | 新建 | 代码 |
| `规则/核心机制.md`（§10.1 敌人 HP 表） | 改写（F-5） | 文档 |
| `实体/敌人与事件.md`（§十二 参数速查） | 改写（F-5） | 文档 |
| `docs/决策树/` / `docs/设计框架-六维状态.md` / memory | 追加 | 文档 |

## 十、数据契约与校验

### 不变量

- raw JSON schema：`{run, seed, configs:[{params, battles:[{outcome, rounds, metrics...}]}]}`，每场含五组指标原始值
- 确定性：同 seed 同 config → 逐位同输出（引擎契约延续）
- 报告不变量：回合数 P10/P50/P90、胜率、结束方式占比、tone 饱和率/死区率、gate 均值——五组全含
- F-5 修表后：核心机制 §10.1 与敌人与事件 §十二 与 §4.1 权威表完全一致（轻度 20-30 / 投影 10-16 / 中度 40-60 / 碎片 25-40 / 重度 80-120 / 完整体 60-90 / 医疗 25-40）

### 校验

| 校验 | 命令 |
|------|------|
| 引擎测试绿 | `dotnet test src/YouAreNotTheFish.Core.Tests`（T1 后仍 294+ 绿） |
| 平衡工具 smoke | `dotnet run --project src/YouAreNotTheFish.Balance -- --battles 10 --seed 1` |
| 确定性复现 | 同 seed 跑两次 diff raw JSON |
| 交叉引用 | `python3 tools/validate_cross_refs.py` |
| F-5 表一致 | grep 敌人 HP 值三处比对 |

## 十一、验收标准

- [ ] T1 完成：4 静息常量入 CalibrationConfig，SpeedScoreCalculator 无硬编码，测试全绿
- [ ] T2-T4 完成：`--battles/--seed/--scan/--scenario/--out` 全部生效；同 seed 确定性验证通过
- [ ] T3 场景库：demo + 6 类敌人模板（§4.1 新值）加载成功
- [ ] T5 报告：五组指标全含，输出 `reports/<run>.md`
- [ ] T6 首份 T0 校准报告：杂兵/精英/Boss 回合数分布 vs 目标区间（4-6/8-10/16-20）
- [ ] T7 F-5 修表完成（三处 HP 值一致）
- [ ] 校准决策未自动改 CalibrationConfig（归 #35）
- [ ] 决策树含 #71 条目；六维状态管线队列更新

## 十二、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 暴击参数校准 | 暴击机制规则空缺（#70 F-3） | P4d 补规则后（#70 路线图） |
| Δm 引擎内验证（LinkState 驱动） | Δm 属 P1b，引擎未实现 | P1b 交付后并入 |
| m_field / 月光场相关校准 | #38 月光场重建开放中，参数集待定 | #38 闭合后 |
| 敌人 Stat 实例细化（Boss 详细设计） | 实体维度队列 | 数值校准后内容填充 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [csharp-engine plan](../../../规格/引擎/csharp-engine-roadmap.md), [引擎数据关系规格](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%BC%95%E6%93%8E%E6%95%B0%E6%8D%AE%E5%85%B3%E7%B3%BB%E8%A7%84%E6%A0%BC.md), [核心机制](../../../%E8%A7%84%E5%88%99/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [Grilling #70 路线图 task-plan](./../grilling-70-engine-roadmap/task-plan.md), [数学语言书写规范](../../../docs/agents/math-language-writing.md)*
