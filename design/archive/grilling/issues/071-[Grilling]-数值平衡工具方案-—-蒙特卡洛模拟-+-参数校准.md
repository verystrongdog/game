# #71 [Grilling] 数值平衡工具方案 — 蒙特卡洛模拟 + 参数校准

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/71

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

设计数值平衡工具方案（蒙特卡洛战斗模拟 + 参数校准），作为 E-5 校准常量群（δ_scale/M1 惩罚/感知阈值/scale_mental/θ_mem/静息常量）与 #35 校准 grilling 的执行载体，并为 P1-P5 参数化占位值提供回填路径。

## 六维定位

- **维度**: 管线（工具/验证）+ 规则（校准目标参数）
- **依赖**: csharp-engine step 1-12 ✅（294/294 绿，可运行）+ CalibrationConfig 单一入口 + 核心机制 §十 数值基线（战斗长度目标 杂兵 4-6/精英 8-10/Boss 16-20 回合）+ #35（战斗输出权重校准，开放中）
- **阻塞**: E-5 校准常量回填 / #35 校准执行 / P1-P5 参数化占位值回填
- **承接**: Grilling #70 路线图 P0 并行校准轨

## 当前状态

- 引擎可跑（294/294 绿），demo 模板（玩家 HP50/SAN80，NPC 杂兵 HP15/SAN60）
- 待校准常量群集中在 CalibrationConfig（引擎数据关系规格 §七）：
  - δ_scale=0.3、M1SustainPenalty=-0.1、PerceptionThreshold=0.15、ScaleMental=1.0(禁用)、MaxRounds=50、4 静息常量（SpeedScoreCalculator 硬编码）
- 战斗长度目标：杂兵 4-6 / 精英 8-10 / Boss 16-20 回合（核心机制 §10.2）
- 旧 sim_battle.py 系列已废弃进垃圾桶（态度引擎三代）——新工具不得复刻旧路线，直接驱动 C# 引擎

## 关键待决

1. 工具形态：C# 驱动引擎 vs Python 分析壳（混合）vs 独立复刻
2. 校准目标集与优先级
3. 验证指标集（战斗长度分布/胜率/tone 动态范围/gate 使用率/SAN 阈值跨越/Δm 曲线）
4. 输出格式（JSON 报告 + 控制台摘要 + 可选图表）
5. 与 #35 / CalibrationConfig 的接口
6. 敌人 Stat 模板来源（demo 模板 vs enemy-stat-pipeline）

## 预期产出

- `.scratch/grilling-71-balance-tool/task-plan.md`（工具架构 + 指标集 + 接口 + 实现步骤）
- 决策树追加 + 六维状态更新 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #71 关闭总结

### 决策表（6 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | C# 批量模拟器 + Python 分析壳（零公式复刻） | 架构 |
| D2 | 校准优先级 T0 战斗长度 → T1 #35 权重组 → T2 E-5 动力学群 → T3 Δm 曲线 | T1-T8 |
| D3 | 五组指标全含（结算/动力学健康/SAN 行为/速度/成长） | T4/T5 |
| D4 | 独立 YouAreNotTheFish.Balance 工程，输出 data/calibration/ | T2 |
| D5 | demo + §4.1 全敌人模板；修 F-5 旧值表 | T3/T7 |
| D6 | 校准决策归 #35（工具不自动改 CalibrationConfig） | 范围 |

### 接口发现

- ✅ CalibrationConfig 已是 instance record（sign-off 结转 #4 预谋），参数扫描零引擎改动
- ⚠️ E-3 前置：4 静息常量硬编码 → T1 迁入 CalibrationConfig
- ⚠️ m_default 读 static Default → 需 m 扫描时小改
- ⚠️ T3 Δm 不在引擎 → Python 公式验证（validate_dm_curve.py）

### 一致性发现 F-5（已修复）

敌人 HP 基线三处不一致（§4.1 新值 vs §十二 旧值 vs 核心机制 §10.1 旧值；医疗人员同文件矛盾）→ 已同步为 §4.1 权威值并加 🔧 注，全库旧值 grep 0 命中。

### 受影响文件

- `.scratch/grilling-71-balance-tool/task-plan.md`（新建：架构/CLI/指标/接口契约/T1-T8/验收）
- `docs/决策树.md`（#71 条目）
- `docs/设计框架-六维状态.md`（管线队列 P0 ✅）
- `规则/核心机制.md`（§10.1 F-5 修表）
- `实体/敌人与事件.md`（§十二 F-5 修表）
- `memory/数值平衡工具-grilling-71.md`

### 推迟清单

- 暴击参数 → P4d 后；Δm 引擎内验证 → P1b 后；m_field → #38 后；敌人 Stat 细化（Boss）→ 实体队列

### 质量门禁

- F-5 一致性 grep：旧值 0 命中，新值三处一致
- 写入验证表：决策 6 项 + 接口 4 项 + F-5 全部落位
- 后续：按 T1-T8 实施（T1 E-3 前置 → T2-T5 工具 → T6 T0 校准报告 → 交 #35 裁决）

---
*导出: 2026-09-12 | 来源: GitHub issue*
