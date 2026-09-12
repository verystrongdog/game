# #24 [Grilling] 设计文档代码就绪度 — 子系统模块接口提取与重构

> 状态：关闭 · 创建 2026-08-06 · 关闭 2026-08-15
> 标签：维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/24

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题
从《软件设计的哲学》《游戏编程模式》《TDD by Example》三本书的原则出发，逐个审视项目现有子系统设计文档，提取模块接口、检查信息隐藏、消除复杂性，使文档具备直接驱动简洁高效代码框架的能力。

## 六维定位
- **主维度**: 管线
- **跨维度影响**: 全部六维

## 当前状态
- 已有代码框架初步规划（五层架构），review 发现 5❌17⚠️
- 设计文档 ~30+ md 文件，质量参差不齐
- 目标：每个子系统的文档 → 可以直接提取出深模块接口

## 参考书籍
- 《软件设计的哲学》— 深模块/信息隐藏/下沉复杂性/通过定义规避错误
- 《游戏编程模式》— Command/Observer/Component/Game Loop/State
- 《TDD by Example》— 测试驱动设计

---

## 评论（3 条）

### verystrongdog · 2026-08-06

## 🔧 暂停 (2026-08-06)

**原因**: 用户决定先获得实现反馈再做模块设计。三本书都支持这个判断——APOSD 战略式编程不排斥编码、TDD 从具体提取抽象、GPP 每个模式从真实烂摊子开始。

**决策**: 
- 暂停 #24，不关闭话题
- 用户先写单回合 Python 模拟（2 参与者，M1 单通道，Phase 3→4）
- 获得实现反馈后重新打开

**受影响的产出**:
- SKILL.md §3.4 已写入（A/B/C/D 四步流程），下次 grilling 使用
- review-trace-grilling-skill-v4.md 已存档（4 个 ❌ 缺口已修复）

### verystrongdog · 2026-08-15

## 🔄 恢复 (2026-08-14)

**触发**: 用户调用 /grilling，话题「引擎数据层重描述 — 以正典数据为锚的 C# 引擎重构规格」。暂停条件（等实现反馈）已解除——csharp-engine step 1-7 已交付（data-layer/types/wmatrix/wc-dynamics/tone/cstc/speed，140/140 测试绿）。

**本次聚焦**:
- 引擎代码（src/YouAreNotTheFish.Core）在正典演进期（step 6/7 裁决、csharp-damage Q3 等 2026-08-13 裁决）写成，存在信息不完整时强行编写的痕迹
- 从已确定的正典数据（解剖 brain_regions/tripartite、物理背景 运行时状态模型、战斗逻辑 核心机制/回合流程）重新描述数据彼此的关系，产出数据结构规格，驱动 step 8-12 及后续重构
- 过程中兼作 C# 教学（教学/CSharp 已上 3 课）

**六维定位**: 管线（主）+ 规则（数据关系语义）

**依赖**: 运行时状态模型/核心机制/回合战斗流程/皮层动力学-通用层（正典）；csharp-engine plan.md v1.1（实施基线）
**阻塞**: Unity 项目搭建 / 测试策略 / step 8-12 后续 feature

### verystrongdog · 2026-08-15

## ✅ 闭合总结 (2026-08-14) — 引擎数据层重描述

### 决策表

| # | 决策 | 内容 |
|---|------|------|
| D1 | 话题形态 | 先盘点后决定——产出《引擎数据层偏差清单》 |
| D2 | 偏差基准 | 正典文档 + data/ JSON 为准（A+B）；正典内部冲突按决策树最新裁决 |
| D3 | 盘点后范围 | 文档同步 + 重描述数据关系文档（B 方案） |
| D4 | E-1 motivation 下界 | 物理 motivation clamp(−1,1)——沮丧降伤，与精神/flow 层口径统一 |
| D5 | D-1 region_name_map | 70→69：删 2 聚合体 + 补 STN，与 brain_regions.json 键集一致 |
| D6 | C-1 plan step 表 | step 8-12 更新为 ✅ 已交付（294/294 绿） |
| D7 | 规格形态 | 数据流图 + 模块接口表合一，落位规则/技能树系统/（正式正典），ASCII，含 Unity 接缝 |
| D8 | 附带清扫 | 核心机制 Euler 残留/tone baseline、脑功能层级模型 §十八、data/README、CombatEvents 注释、spec v1.3、term_registry、tools 废弃标记 |

### 写入验证表

| 决策 | 写入文件 | 位置 | 验证 |
|------|---------|------|------|
| D7 | 规则/技能树系统/引擎数据关系规格.md | 新建（8 章） | ✅ 全量测试 294/294 绿后文档一致 |
| 盘点 | .scratch/grilling-24-engine-data-relations/引擎数据层偏差清单.md | 新建 | ✅ |
| D4 | DamageCalculator.cs:52 + Tests AC-4 + damage spec B7 + 核心机制 §4.2 + term_registry | 5 处 | ✅ 全量测试 294/294 绿 |
| D5 | region_name_map.json + build_region_name_map.py | 数据+工具 | ✅ python3 验证 69 键集一致 |
| D6 | csharp-engine plan.md §十一 + 变更日志 | 2 处 | ✅ |
| D8 | 核心机制 §2.1/§十一、脑功能层级模型 §十八、data/README、CombatEvents.cs:87、data-layer spec v1.3、engine-types spec、决策树、六维状态、NOTES.md | 9 文件 | ✅ |

### 质量门禁

- ✅ 引擎全量测试 294/294 通过（E-1 修改后）
- ✅ 一致性清扫：tone baseline [0.1,2.0]、AmygdalaHippocampus/BasalGangliaIndirectPathway、负值归零、心理伤害规则 grep 全部清零/标注
- ✅ JSON 合法性：region_name_map.json python3 解析通过、键集与 brain_regions.json 完全一致

### 推迟清单

- E-2 14 事件闭环（A3/B3/A6/A7）、E-3 静息常量去硬编码、E-4 NpcSalience 正式化 → 数值校准/技能系统 grilling
- [NEW] 待校准常量群（δ_scale=0.3 等）→ 数值平衡工具
- 纯文档问题 8 项（决策树 D10 笔误、audit 字段数等）→ 随文档维护
- Unity 工程搭建 → 依赖本规格 §六 接缝

---
*导出: 2026-09-12 | 来源: GitHub issue*
