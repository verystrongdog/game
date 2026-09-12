# #70 [Grilling] 引擎补全路线图 — 缺口盘点与依赖排期

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/70

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #24 延迟项（E-2/3/4/5），以 `src/YouAreNotTheFish.Core`（294/294 绿，step 1-12 已交付）为基线，盘点逻辑引擎全部缺口、排依赖序、产出分 feature 任务计划（全量路线图）。

## 六维定位

- **维度**: 规则（技能/情境/NPC/战斗扩展的系统缺口）+ 管线（数值平衡工具/Unity/测试的上游规划）
- **依赖**: #24 延迟项 + 运行时状态模型 §4.5 skill.cortical_nodes 接口延迟项 + 技能生成机制/情境系统/NPC AI 正典
- **阻塞**: 管线 Grilling 队列（数值平衡工具、Unity 结构、测试策略）

## 当前状态

引擎已交付：WC 69 节点动力学 / 4 tone+b_j / CSTC 3 环路 Gurney / 速度排序 / 伤害结算 / 14 事件 δ/s（10 落地）/ NPC demo salience / 5 Phase 回合编排 / 1v1 Console。

已知缺口（盘点产物，详见 grilling 会话）：
1. **引擎内**: E-2 14 事件闭环（A3/B3/A6/A7 裁剪）、E-3 4 静息常量硬编码、E-4 NpcSalience demo 占位、E-5 [NEW] 校准常量群、响应窗口 stub
2. **结构性系统**: LinkState/m 成长缺失（demo m_default=0.3）、skill.cortical_nodes 激活机制未定义、情境系统 27 原型未消费、NPC Affordance Competition 全量（7 参数化）未实现、战斗扩展（空间/HP↔SAN 互转/响应窗口 link 交互）、实体系统（装备/消耗品）未进引擎
3. **管线**: 数值平衡工具、校验脚本阶段 2-4、Unity 工程、测试策略、review-plan SKILL.md

## 关联

- 承接: [#24](https://github.com/verystrongdog/game/issues/24) 延迟项
- 对接: [#35](https://github.com/verystrongdog/game/issues/35)（战斗输出权重校准=E-5 校准群）
- 参考: [#23](https://github.com/verystrongdog/game/issues/23)（代码框架与校验管线）

## 预期产出

- `.scratch/grilling-NN-engine-roadmap/task-plan.md`（分 feature 任务计划 + 依赖图 + 里程碑）
- 决策树追加 + 六维状态更新 + 关键决策写 memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #70 关闭总结

### 决策表（8 项共识）

| 编号 | 决策 | 落位批次 |
|------|------|---------|
| D1 | 全量路线图（引擎内+结构性+管线）排依赖序 | 全部 |
| D2 | 依赖链顺序：技能接口→LinkState+m→情境→NPC 全量→战斗扩展+实体；校准并行 | P1-P6 |
| D3 | skill.cortical_nodes 激活 = C 混合注入+传播（Δ_skill 直接注入 + W·a 传播），闭合运行时状态模型 §4.5 延迟项 | P1c |
| D4 | E-2/3/4 按归属并入（E-4→P3、A3/B3→P4d、A6→P1c、A7→P4a、E-3→P0、响应窗口→P4c） | P1c/P3/P4/P0 |
| D5 | 校准并行轨（数值平衡工具 + #35），CalibrationConfig 回填 | P0 |
| D6 | 批次拆细（P1×3、P4×5 子批） | P1/P4 |
| D7 | 里程碑 = 每批 RED→GREEN + Console 完整战斗 demo | 全部 |
| D8 | 三体技能上下文重建（link_contexts 重生于 tripartite + 8 角色分类器 + 60 候选池验证） | P1a |

### 盘点发现

- **F-1** 数据链断裂：link_contexts.json（364 条）基于已废弃旧 pairwise 364 链路 → 60 候选池失效
- **F-2** 8 行为角色不在三体数据（tripartite role = active/silent/modulating）→ 需新分类器
- **F-3** 暴击机制规则空缺（无暴击率/倍率/触发正典）→ A3/B3 无法落地根因
- **F-4** 响应窗口 IResponseResolver 为 Noop stub

### 受影响文件

- `.scratch/grilling-70-engine-roadmap/task-plan.md`（新建：P0-P6 批次表 + 依赖图 + 数据契约 + 验收标准）
- `docs/决策树.md`（#70 条目 + #24 延迟项加注「→ 见 #70」）
- `docs/设计框架-六维状态.md`（管线 ✅+1=19、Grilling 队列 8 项、优先级 5.0、完成度 ~86%）
- `项目总览.md`（优先级 5.0 + 管线 ~86%）
- `规则/技能树系统/技能生成机制.md`（§二 60 候选池 ⚠️ 废弃注 + 关联修复）
- `data/term_registry.json`（+Δ_skill、+LinkState、链路上下文补注，142→144）
- `memory/引擎补全路线图-grilling-70.md`（决策摘要）

### 推迟清单

- 任务目标「持续压力」内部认知态 → 独立 grilling
- m_field 节点级落点 → #38 后
- 观察者效应机制桥接 → 独立 grilling
- 14 角色→组件映射表 → P5-3 前置

### 质量门禁

- cross-ref 校验：525/535 有效，新增 0 失效（7 个既有失效均为历史问题）
- 写入验证表：13 项全部 ✅ 已验证
- 后续：按 P0-P6 逐批开 feature issue（P0 = 数值平衡工具 + #35）

---
*导出: 2026-09-12 | 来源: GitHub issue*
