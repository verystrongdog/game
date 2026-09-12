# Grilling #70 引擎补全路线图 — 实施任务计划

> Grilling #70 (GitHub #70) 结论：以 `src/YouAreNotTheFish.Core`（step 1-12 交付，294/294 绿）为基线，盘点逻辑引擎全部缺口、排依赖序、产出分 feature 任务计划（全量路线图）。8 项共识：全量范围 / 依赖链顺序 / 技能激活机制 C 混合注入 / E-2·3·4 按归属并入 / 校准并行轨 / 批次拆细 / Console 完整 demo 里程碑。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [依赖图与批次总览](#三依赖图与批次总览)
4. [P0 并行校准轨](#四p0-并行校准轨)
5. [P1 技能系统（3 子批）](#五p1-技能系统3-子批)
6. [P2 情境系统](#六p2-情境系统)
7. [P3 NPC Affordance 全量](#七p3-npc-affordance-全量)
8. [P4 战斗扩展（5 子批）](#八p4-战斗扩展5-子批)
9. [P5 实体系统 / P6 管线收尾](#九p5-实体系统--p6-管线收尾)
10. [数据链断裂与规则空缺发现](#十数据链断裂与规则空缺发现)
11. [文件清单](#十一文件清单)
12. [数据契约与校验](#十二数据契约与校验)
13. [参数速查表](#十三参数速查表)
14. [验收标准](#十四验收标准)
15. [推迟清单](#十五推迟清单)

---

## 一、背景与动机

引擎核心已交付（[csharp-engine plan](./../csharp-engine/design/plan.md) §十一 v1.2：step 1-12 全部 ✅，294/294 绿），覆盖 WC 69 节点动力学 / 4 tone + b_j / CSTC 3 环路 Gurney / 速度排序 / 物理·精神伤害 / 14 事件 δ/s（10 落地）/ NPC demo salience / 5 Phase 回合编排 / 1v1 Console。

Grilling #24 盘点确认引擎与正典**结构性偏差≈0**（[引擎数据层偏差清单](./../grilling-24-engine-data-relations/引擎数据层偏差清单.md) §六），遗留 E-2/3/4/5 四类引擎内缺口 + 5 类结构性系统缺口（技能/情境/NPC/战斗扩展/实体系统）未进引擎。本次 grilling 承接 #24 延迟项，产出全量补全路线图。

**边界（本地约定）**：本次只**排期不实现**——每条 feature 独立开 grilling/issue 后实施；任务目标「持续压力」内部认知态、月光场 m_field 节点级落点、观察者效应机制桥接 不入引擎批（见 §十五）。

## 二、决策清单

| 编号 | 决策 | 类型 | 影响批次 |
|------|------|------|---------|
| D1 | 范围 = 全量路线图（①引擎内 E-2/3/4/5 ②结构性系统 ③管线）排依赖序 | 范围 | 全部 |
| D2 | 结构性系统按依赖链顺序：①技能接口裁决 → ②LinkState+m → ③情境 → ④NPC 全量 → ⑤战斗扩展+实体；⑥校准全程并行 | 顺序 | 全部 |
| D3 | skill.cortical_nodes 激活机制 = **C 混合注入+传播**：核心节点直接注入 Δ_skill + W·a 网络自然传播 | 规则接口 | P1c |
| D4 | E-2/3/4 按归属并入对应批次（不设独立 fixup 批）：E-4→P3、E-2 拆入（A3/B3→P4d、A6→P1c、A7→P4a）、E-3→P0、响应窗口 stub→P4c | 处置 | P1c/P3/P4a/P4c/P4d/P0 |
| D5 | E-5 校准 = 并行校准轨：数值平衡工具 + #35 独立推进，结构批用参数化占位值经 `CalibrationConfig` 回填 | 校准 | P0 |
| D6 | 批次粒度 = 拆细：P1 拆 3 子批、P4 拆 5 子批，每子批独立 feature issue | 粒度 | P1/P4 |
| D7 | 里程碑 = 每批 RED→GREEN + 总里程碑 **Console 完整战斗 demo**（多敌方+技能+情境+NPC 全量+装备/消耗品+校准值） | 验证 | 全部 |
| D8 | 数据链断裂修复 = 三体技能上下文重建（link_contexts 重生于 tripartite + 8 行为角色分类器 + 60 候选池验证） | 数据 | P1a |

## 三、依赖图与批次总览

```
P0 并行校准轨（不阻塞，全程并行）
   ├─ 数值平衡工具（蒙特卡洛/参数扫描）        ─┐
   └─ #35 校准 grilling（已开放，产出 E-5 常量）─┴→ 常量回填 CalibrationConfig（D5）

P1a 技能上下文三体重建（数据）──────────────────┐
P1b LinkState + m 成长进引擎 ──────────────────┤  依赖: P1a（m 载体=三体连接）
P1c 技能执行引擎（混合注入+效果+A6）───────────┘
P2 情境系统（α_patterns 数据化 + 27 原型选择器 + s_env/m_field 三通道）
P3 NPC Affordance 全量（7 参数化 + NpcSalience 正式化 + E-4）  依赖: P1c + P2
P4a 逃跑/投降（A7）        ┐
P4b HP↔SAN 互转            │
P4c 响应窗口+防御主动/忍耐  │  P4e 依赖 P3（多敌方 salience 共享窗口）
P4d 暴击机制补全（A3/B3）   │
P4e 空间系统（3 子任务）    ┘
P5 实体系统（武器/消耗品/组件）  依赖: P1b（m 状态）
P6 管线收尾（Unity/测试/校验/review-plan）  依赖: P1-P5 引擎完整
```

| 批次 | 名称 | feature issue | 里程碑 |
|------|------|--------------|--------|
| P0 | 并行校准轨 | #35（已有）+ 平衡工具（新） | δ_scale/M1/感知阈值/scale_mental/θ_mem/静息常量 定值 |
| P1a | 技能上下文三体重建 | 新 | link_contexts_tripartite.json + 60 候选池验证 |
| P1b | LinkState + m 成长 | 新 | WMatrix 消费真实 m；战后 Δm 生效 |
| P1c | 技能执行引擎 | 新 | skill 执行改变 a(t)；A6 事件发射 |
| P2 | 情境系统 | 新 | EventProcessor 配置驱动；27 原型选择器；s_env/m_field 输入 |
| P3 | NPC Affordance 全量 | 新 | NPC 用正式技能候选集 + 7 参数化行动（E-4 闭合） |
| P4a | 逃跑/投降 | 新 | A7 闭环；退出战斗 |
| P4b | HP↔SAN 互转 | 新 | 互转规则进引擎（占 M1） |
| P4c | 响应窗口 link 交互 | 新 | L1 期待/L3 精准/L5 叙事重构 + 防御主动/忍耐主动 |
| P4d | 暴击机制补全 | 新 | 暴击规则正典 + A3/B3 闭环 |
| P4e | 空间系统 | 新（3 子任务） | 战棋/多敌方/AOE/视线/友伤 |
| P5 | 实体系统 | 新（3 子任务） | 武器/消耗品/组件进引擎 |
| P6 | 管线收尾 | 新（4 子任务） | Unity/测试/校验/review-plan |

## 四、P0 并行校准轨

- **#35 战斗输出权重校准**（已开放，`[Grilling] 战斗输出权重校准 + 精神攻击节点集 + 事件上限`）：产出 scale_mental / θ_mem / δ_scale / M1SustainPenalty / PerceptionThreshold / MaxRounds / 4 静息常量（E-3 去硬编码归属）/ 暴击参数（依赖 P4d 规则补全，标注延迟）
- **数值平衡工具**（管线队列第 2 项）：蒙特卡洛战斗模拟 + 参数扫描，验证战斗长度目标（杂兵 4-6 回合 / 精英 8-10 / Boss 16-20，[核心机制 §十](../../../%E8%A7%84%E5%88%99/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md)）
- **回填机制**：全部常量经 `CalibrationConfig.cs`（单一入口已就位，[引擎数据关系规格 §七](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%BC%95%E6%93%8E%E6%95%B0%E6%8D%AE%E5%85%B3%E7%B3%BB%E8%A7%84%E6%A0%BC.md)），P1-P5 批次用参数化占位值实现，校准产出后回填并摘除 `[NEW]` 标注

## 五、P1 技能系统（3 子批）

### P1a 技能上下文三体重建（数据层）

**背景**：`link_contexts.json`（364 条，`link_000_L` 键）与 `link_registry.json`（⚠️ 标注"已废弃 2026-08-07 #26"）均基于旧 pairwise 364 链路 → 「60 候选池」实测数据已失效（D8，见 §十）。

| 子任务 | 内容 | 产出 |
|--------|------|------|
| 1a-1 | 三体连接上下文计算：tripartite 边（776 CC + 112 PP + 114 brainstem + 47 cstc）→ 网络归属（kroell14_networks.json，dk 级推导）× 主导角色 | `link_contexts_tripartite.json` |
| 1a-2 | 8 行为角色分类器：从 function_label（signal_type）+ gameplay_labels（12 gameplay_domain）+ 网络推导 8 角色（attack_physical/attack_mental/defend/flee/approach/perceive/support/disrupt），工具脚本入 `tools/` | 角色分类器脚本 |
| 1a-3 | 60 候选池重建验证：联合上下文 × 8 角色过滤（≥2 连接），对比旧 60 候选分布 | 验证报告 |

**数据契约**：`link_contexts_tripartite.json` 的键 = 三体边标识（`(source,target,type)` 或边索引），非旧 link_NNN。

### P1b LinkState + m 成长进引擎

| 子任务 | 内容 | 正典依据 |
|--------|------|---------|
| 1b-1 | `LinkState`：三体边级 m ∈ [0,1]，`combat_state.link_states[edge_id].m` | [皮层动力学 §5.3](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E7%9A%AE%E5%B1%82%E5%8A%A8%E5%8A%9B%E5%AD%A6-%E9%80%9A%E7%94%A8%E5%B1%82.md) |
| 1b-2 | `m_mean` 入 WMatrix：替换 demo `m_default=0.3`，按 dk 对聚合 m_mean（连接→链路映射） | 同上 §5.2 |
| 1b-3 | Δm 战后增长：`Δm = base(L) × (1−sigmoid(m, 0.45, 10)) × g(n) × 标记倍率`，战斗事件后结算 | [核心机制 §2.3](../../../%E8%A7%84%E5%88%99/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md) |
| 1b-4 | 可塑性巩固事件：标记（Δm×2）/增强（m+0.03~0.20），巩固窗口 | term_registry 可塑性巩固 |
| 1b-5 | 聚焦：focus_multiplier ×2.0 入 W（激活点=常驻聚焦容量，构建层分配） | term_registry 激活点 |

### P1c 技能执行引擎

| 子任务 | 内容 | 依据 |
|--------|------|------|
| 1c-1 | skill 定义数据结构：cortical_nodes + role + base_effect 参数 | [技能生成机制 §一](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E6%8A%80%E8%83%BD%E7%94%9F%E6%88%90%E6%9C%BA%E5%88%B6.md) |
| 1c-2 | **混合注入实现**（D3）：执行时核心节点 `a_j ← clip(a_j + Δ_skill, 0, 1)`（Δ_skill [NEW] 待校准）+ W·a 自然传播 | [运行时状态模型 §4.5](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) 延迟项闭合 |
| 1c-3 | skill_base_effect × gate_bonus(role) 结算（a(t) 派生：精神攻击/物理/记忆检索/察觉） | 技能生成机制 §五 |
| 1c-4 | A6 事件闭环：`δ = sign(tone_bias[skill.role])`（权重表固定符号），α=0 | [运行时状态模型 §5.5](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) |

## 六、P2 情境系统

| 子任务 | 内容 | 依据 |
|--------|------|------|
| 2-1 | α_patterns.json 数据化：EventProcessor.cs 去硬编码（#69 D9 落地，`data/connectivity/alpha_patterns.json`） | [grilling-69 task-plan](./../grilling-69-external-stimulus/task-plan.md) §五 |
| 2-2 | 27 原型选择器：situation_primitives.json 消费方（SituationPrimitives 已加载，demo 未用） | [引擎数据关系规格 §六](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%BC%95%E6%93%8E%E6%95%B0%E6%8D%AE%E5%85%B3%E7%B3%BB%E8%A7%84%E6%A0%BC.md) 接缝 🔶 |
| 2-3 | s_env 环境基调 + m_field 月光场通道（三通道输入）：`h_j = ΣW·a + b + s_事件 + s_env + m_field` | [运行时状态模型 §4.5](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) + #69 |
| 2-4 | 情境 salience 输出接口（供 P3 消费） | [NPC AI 行为模型 §三](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) |

> ⚠️ m_field 的**参数集与节点级落点**依赖 #38（月光场重建，开放中）→ 本批占位实现 + 接口参数化。

## 七、P3 NPC Affordance 全量

| 子任务 | 内容 | 依据 |
|--------|------|------|
| 3-1 | 7 参数化性格：4 tone baseline + 3 CSTC bias → ParticipantState/CombatContext；6 概念标签→参数映射表（§5.4 "后续定义"） | [NPC AI 行为模型 §四](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) |
| 3-2 | NpcSalience 正式化：技能候选集（P1a 产出）+ 情境 salience（P2）+ gate_bonus + tone_bias；Boss argmax / 杂兵 Softmax，T = T_base + T_SAN | 同上 §三 + 运行时 §8.4 |
| 3-3 | E-4 闭合：删除 demo 占位（3 行动节点集 + FirstEnemy 硬编码） | [偏差清单 E-4](./../grilling-24-engine-data-relations/引擎数据层偏差清单.md) |

## 八、P4 战斗扩展（5 子批）

| 子批 | 内容 | 正典依据 | 归属缺口 |
|------|------|---------|---------|
| P4a | 逃跑/投降：M1 通道逃跑、退出战斗、无髓鞘化增长；投降仅对有理性敌方；A7 事件闭环 | [回合战斗流程 §八](../../../%E8%A7%84%E5%88%99/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md) | E-2 A7 |
| P4b | HP↔SAN 互转：HP→SAN 前10 1:2 后5 1:1 单次≤15HP 单场≤30SAN；SAN→HP 前10 2:1 后10 3:1 单次≤20SAN 单场≤15HP；占 M1 | [核心机制 §5.3](../../../%E8%A7%84%E5%88%99/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md) | 范围表未覆盖 |
| P4c | 响应窗口 link 交互：L1 期待/L3 精准/L5 叙事重构（IResponseResolver 实现）；防御主动（−2 CD2 占 Broca）/忍耐主动（接口已预留） | [回合战斗流程 §六](../../../%E8%A7%84%E5%88%99/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md) | 响应窗口 stub + 接口预留 |
| P4d | 暴击机制补全：**规则空缺**（无暴击率/倍率/触发正典，仅"L4 揭示弱点→暴击率↑"）→ 先补规则（可并入 #35）→ A3/B3 闭环 | [基础行动设计 L123](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E6%93%8D%E4%BD%9C%E5%B1%82/%E5%9F%BA%E7%A1%80%E8%A1%8C%E5%8A%A8%E8%AE%BE%E8%AE%A1.md) | E-2 A3/B3 |
| P4e | 空间系统（3 子任务）：①空间模型（1m 网格/移动配额 12 格/部署/软边界）②战斗交互（控制区 1.5m/借机/夹击/高度/视线/友伤）③多敌方（共享窗口协调/隐藏/援军/AOE 链路赋予/伤害递减） | [回合战斗流程 §十](../../../%E8%A7%84%E5%88%99/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md) | 范围表未覆盖 |

## 九、P5 实体系统 / P6 管线收尾

### P5 实体系统（批内 3 子任务滚动）

| 子任务 | 内容 | 依据 |
|--------|------|------|
| 5-1 | 武器/护甲/精神武器：物理 base + weapon_bonus 入 DamageCalculator；护甲防御修正；Boss 专属 | [武器与装备](../../../%E5%AE%9E%E4%BD%93/%E6%AD%A6%E5%99%A8%E4%B8%8E%E8%A3%85%E5%A4%87.md) |
| 5-2 | 17 消耗品药物：链路调制（抑制↓/增强↑/钳制↕，三级强度），依赖/戒断/耐药/过量 | [消耗品系统](../../../%E5%AE%9E%E4%BD%93/%E6%B6%88%E8%80%97%E5%93%81%E7%B3%BB%E7%BB%9F.md) |
| 5-3 | 面具组件：病理链路激活(+)/抑制(−)，1 组件=1 症状=1 连接，同域加成 | [角色与面具 §8](../../../%E5%AE%9E%E4%BD%93/%E8%A7%92%E8%89%B2%E4%B8%8E%E9%9D%A2%E5%85%B7.md) |

### P6 管线收尾（批内 4 子任务滚动）

| 子任务 | 内容 | 依赖 |
|--------|------|------|
| 6-1 | Unity 工程搭建：引擎程序集直接引用（纯 .NET 8 无 Unity 引用），接缝 §六（JSON→ScriptableObject / 回合驱动 / 状态呈现） | P1-P5 |
| 6-2 | 测试策略：单元/集成/玩法测试方法与范围 | 6-1 |
| 6-3 | 校验脚本阶段 2-4：validate_* 扩展（三体上下文/暴击参数/校准常量） | P1a/P4d/P0 |
| 6-4 | review-plan SKILL.md 实现（方案 v2 已定） | — |

## 十、数据链断裂与规则空缺发现

| # | 发现 | 证据 | 处置 |
|---|------|------|------|
| F-1 | **技能数据链断裂**：link_contexts.json（364 条）+ link_registry.json（⚠️ 已废弃标注）基于旧 pairwise 364 链路 → 60 候选池失效 | python3 实测 link_contexts 364 键 link_000_L；link_registry `_description` 废弃标注 | P1a 重建（D8） |
| F-2 | **8 行为角色不在三体数据**：tripartite 边 role 字段 = active/silent/modulating（脑干广播权重），非 8 行为角色；function_label（signal_type）+ gameplay_labels（12 gameplay_domain）在 | tripartite_model.json role 分布实测 | P1a-2 新分类器 |
| F-3 | **暴击机制规则空缺**：全规则库仅"L4 揭示弱点→暴击率↑"效果方向，无暴击率基线/倍率/触发判定正典 | grep 暴击：基础行动设计 L123 / 核心机制 L300 | P4d 先补规则 |
| F-4 | **响应窗口全文未定义到引擎粒度**：IResponseResolver 为 Noop stub，L1/L3/L5 交互仅接口 | 引擎数据关系规格 §4.3 | P4c |

## 十一、文件清单

| 文件 | 操作 | 批次 |
|------|------|------|
| `data/connectivity/link_contexts_tripartite.json` | 新建 | P1a |
| `tools/build_contexts_tripartite.py`（含 8 角色分类器） | 新建 | P1a |
| `src/YouAreNotTheFish.Core/Entity/LinkState.cs` | 新建 | P1b |
| `src/YouAreNotTheFish.Core/Engine/WMatrixBuilder.cs` | 改写（m_mean 消费） | P1b |
| `src/YouAreNotTheFish.Core/Engine/*`（技能执行/情境/NPC/战斗扩展） | 按批次改写 | P1c-P4 |
| `data/connectivity/alpha_patterns.json` | 新建（#69 D9 落地） | P2 |
| `src/YouAreNotTheFish.Core/Engine/EventProcessor.cs` | 重构（配置驱动） | P2 |
| `data/connectivity/situation_primitives.json` | 消费（不改写） | P2 |
| `src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` | 常量回填 | P0 |
| `docs/决策树.md` | 追加 #70 | 本文档 |
| `docs/设计框架-六维状态.md` | 管线维度队列更新 | 本文档 |
| `data/term_registry.json` | Δ_skill 等入库（用户确认后） | 本文档 |
| `.claude/projects/-home-dog-game/memory/grill-engine-roadmap-70.md` | 新建 | 本文档 |

## 十二、数据契约与校验

### 不变量

- `link_contexts_tripartite.json` 键 = 三体边标识，与 `tripartite_model.json` 双射
- `WMatrix.RowFids` 行序契约（canonical 69）不被 LinkState 破坏——m_mean 只改权重值不改行序
- 技能执行混合注入：`a_j ∈ (0,1)` 由 clip 保证（解析解凸组合性质 + Δ_skill 注入后 clip）
- 全部常量经 `CalibrationConfig` 单一入口，无散落硬编码（E-3 验收）

### 校验

| 校验 | 命令 |
|------|------|
| 三体上下文双射 | `python3 tools/validate_link_data.py` 扩展 |
| 决策树/交叉引用 | `python3 tools/validate_cross_refs.py` |
| 注册表 deprecated | `python3 tools/list_deprecated_terms.py` |
| 每批测试绿 | `dotnet test src/YouAreNotTheFish.Core.Tests`（RED→GREEN） |

## 十三、参数速查表

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| 技能节点直接注入量 | `Δ_skill` | 待校准 [NEW] #70 | P1c；#35 校准 |
| 涌现条件 m 阈值 | — | ≥0.5（组内 ≥2 条，≥1 聚焦） | [技能生成机制 §六](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E6%8A%80%E8%83%BD%E7%94%9F%E6%88%90%E6%9C%BA%E5%88%B6.md) |
| 聚焦倍率 | `focus_multiplier` | 2.0 | 运行时 §九 |
| 全局 δ 缩放 | `δ_scale` | 0.3 [NEW] 待校准 | CalibrationConfig（#35） |
| M1 持续占用惩罚 | — | −0.1 [NEW] 待校准 | CalibrationConfig（#35） |
| 察觉阈值 | — | 0.15 [NEW] 待校准 | CalibrationConfig（#35） |
| 精神缩放 | `scale_mental` | 1.0（禁用）[NEW] 待校准 | CalibrationConfig（#35） |
| 记忆检索阈值 | `θ_mem` | 待校准 | CalibrationConfig（#35） |

## 十四、验收标准

- [ ] task-plan 决策表 8 项全部落位批次
- [ ] P0-P6 批次表含依赖序与里程碑（D2/D6/D7）
- [ ] 数据链断裂（F-1/F-2）与规则空缺（F-3）列入对应批次
- [ ] 决策树追加 Grilling #70 条目，且 #24 延迟项（E-2/3/4/5）加注「→ 见 #70」
- [ ] 六维状态管线维度队列反映 P0-P6
- [ ] term_registry 候选（Δ_skill）经用户确认后入库
- [ ] 总里程碑定义 = Console 完整战斗 demo（多敌方+技能+情境+NPC+装备+校准值）

## 十五、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| 任务目标/承诺「持续压力」= 内部认知态 | #69 延迟项，非外界刺激 | 独立 grilling：内部认知激励 |
| m_field 节点级落点（月光激活哪些 functional_id） | #38 月光场重建开放中 | 观察者效应机制节点映射 grilling |
| 观察者效应机制桥接（"相信被打败"→规则） | #38/#41 世界观地基已就位，桥接待开题 | 独立 grilling（六维状态规则空缺） |
| 14 角色→组件映射表（面具组件） | P5-3 前置，逐角色开 issue | 组件映射 grilling |
| 敌人 Stat 实例 + Boss 详细战斗设计 | 实体维度队列 | 数值校准后内容填充 |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [csharp-engine plan](./../csharp-engine/design/plan.md), [引擎数据层偏差清单](./../grilling-24-engine-data-relations/引擎数据层偏差清单.md), [引擎数据关系规格](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E5%BC%95%E6%93%8E%E6%95%B0%E6%8D%AE%E5%85%B3%E7%B3%BB%E8%A7%84%E6%A0%BC.md), [运行时状态模型](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md), [grilling-69 task-plan](./../grilling-69-external-stimulus/task-plan.md), [数学语言书写规范](../../../docs/agents/math-language-writing.md)*
