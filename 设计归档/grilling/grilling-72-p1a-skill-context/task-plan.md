# Grilling #72 P1a 技能上下文三体重建 — 实施任务计划

> Grilling #72 (GitHub #72) 结论：把技能生成的上下文基础从已废弃旧 pairwise 364 链路（F-1）重建到三体模型连接上。5 项共识：CC+PP 信息传递边 / gameplay_labels 桥接网络归属 / 12 domain→8 role 映射表 / 候选池实测值 / 双视图 schema。本文档为决策→实施的桥梁。

## 目录

1. [背景与动机](#一背景与动机)
2. [决策清单](#二决策清单)
3. [数据架构](#三数据架构)
4. [角色映射表（最终版）](#四角色映射表最终版)
5. [任务分解](#五任务分解)
6. [验证方案](#六验证方案)
7. [文件清单](#七文件清单)
8. [数据契约与校验](#八数据契约与校验)
9. [验收标准](#九验收标准)
10. [推迟清单](#十推迟清单)

---

## 一、背景与动机

Grilling #70 盘点发现 F-1：`link_contexts.json`（364 条）与 `link_registry.json`（⚠️ 已废弃标注）均基于旧 pairwise 364 链路，「60 候选池」实测数据失效。F-2：8 行为角色分类不在三体数据中（tripartite 边 role 字段 = active/silent/modulating，脑干广播权重用）。链路上下文是"组件分类、技能生成、药物调制的共同基础"（term_registry）——重建是 P1b/P1c/组件/药物的地基。

**可用数据**（引用即读取，2026-08-16 python3 实测）：
- `tripartite_model.json`：776 CC + 112 PP 边（888 信息传递边），全量含 `gameplay_labels`（12 domain）；588 边含 `function_label`（signal_type）
- `kroell14_networks.json`：14 网络，每网络含 `gameplay_domains`（2 个，机器可读）
- `NPC AI 行为模型.md §3.3`：8 角色 tone_bias 权重表（角色语义正典）
- `signal_types.json`：4 大类 18 子类（辅助修正用）

## 二、决策清单

| 编号 | 决策 | 类型 |
|------|------|------|
| D1 | 边集 = **CC + PP 信息传递边（888 条）**——brainstem/CSTC 是调制/门控原语，由 tone/gate 系统独立承载（NPC AI §3.3 + 运行时 §6.5），不入技能内容池 | 范围 |
| D2 | 网络归属 = **gameplay_labels 桥接**：`networks(edge) = {n : n.gameplay_domains ∩ edge.gameplay_labels ≠ ∅}`，零新映射表 | 算法 |
| D3 | 角色分类 = **12 gameplay_domain → 8 role 权重映射表**（§四），signal_type 辅助修正；主角色 = argmax，副角色 = 次高分 > 0.25 | 算法 |
| D4 | 候选池规模 = **实测值**（不设约束）；重建报告给出新规模与分布，供技能系统 grilling 评估 | 范围 |
| D5 | Schema = **双视图**：`contexts` 主视图（context→edges）+ `edge_contexts` 反视图（edge→contexts），`_rules` 声明算法，`stats` 含 uncovered 边 | 数据 |

## 三、数据架构

### 3.1 输出文件 `data/connectivity/link_contexts_tripartite.json`

```json
{
  "_description": "三体连接 → 上下文集合映射 (Grilling #72 P1a)，替代旧 link_contexts.json（基于已废弃 364 链路）",
  "_rules": [
    "edge_set = corticocortical ∪ privileged_pathways (888)",
    "networks(edge) = {n : n.gameplay_domains ∩ edge.gameplay_labels ≠ ∅} (kroell14, 14 网络)",
    "role_scores(edge)[r] = Σ_domain w(domain, r) × [domain ∈ edge.gameplay_labels] (domain_role_map.json)",
    "primary_role = argmax_r role_scores; secondary = 次高分 r (score > 0.25)",
    "contexts(edge) = {(network, primary_role) for network in networks(edge)}",
    "候选技能 context = 组内 edge_count ≥ 2"
  ],
  "contexts": {
    "Autobiographical Memory/support": {"network": "...", "role": "support", "edges": ["cc:012", "pp:003", "..."], "edge_count": 5}
  },
  "edge_contexts": {
    "cc:012": {"source": "dk_a", "target": "dk_b", "networks": ["..."], "role_scores": {"perceive": 0.8, "..."}, "primary_role": "perceive", "secondary_role": null, "contexts": [["Autobiographical Memory", "perceive"], "..."]}
  },
  "stats": {
    "total_edges": 888,
    "network_assigned": 885,
    "uncovered_edges": 3,
    "uncovered_reason": "仅含 thalamic_relay 标签",
    "role_assigned": 888,
    "contexts": 87,
    "candidate_skills": 61,
    "role_distribution": {"perceive": 210, "...": "..."}
  }
}
```

### 3.2 边键方案

- `cc:NNN` = corticocortical 数组索引（0-based）
- `pp:NNN` = privileged_pathways 数组索引
- 稳定键：与 `tripartite_model.json` 数组顺序绑定（重建脚本内声明索引契约）

### 3.3 输入依赖

| 文件 | 消费字段 |
|------|---------|
| `tripartite_model.json` | corticocortical[].gameplay_labels / privileged_pathways[].gameplay_labels / source / target |
| `kroell14_networks.json` | networks[].name / gameplay_domains |
| `data/connectivity/domain_role_map.json`（新建） | 12 domain → 8 role 权重（§四） |

## 四、角色映射表（最终版）

写入 `data/connectivity/domain_role_map.json`（独立数据文件——后续 #35 数值校准可直接调权重，不动脚本）：

| gameplay_domain | attack_physical | attack_mental | defend | flee | approach | perceive | support | disrupt |
|-----------------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| motor_execution | 1.0 | | | | | | | |
| sensory_perception | | | | | | 1.0 | | |
| cognitive_control | | 0.2 | | | | | 0.5 | 0.3 |
| social_cognition | | 0.4 | | | | | 0.3 | 0.3 |
| memory_consolidation | | 0.2 | | | | 0.3 | 0.5 | |
| reward_learning | | | | | 1.0 | | | |
| threat_defense | | | 0.6 | 0.4 | | | | |
| arousal_modulation | | | 0.3 | 0.2 | | 0.5 | | |
| interoception | | | 0.5 | | | 0.5 | | |
| habit_learning | 0.5 | | | | 0.3 | | | 0.2 |
| action_gating | 0.6 | | | | 0.4 | | | |
| thalamic_relay | | | | | | 0.5 | 0.5 | |

> 权重为初始值（对齐旧 classify_link_roles 的角色语义：attack_physical=运动输出、defend/flee=威胁响应、approach=奖赏趋近、perceive=感知、support=自我/友方、disrupt=社会压制）；具体数值属设计校准层（NPC AI §3.3 注），#35 可调。

**signal_type 辅助修正**（可选增强，T2 实现时评估）：`motor_command → attack_physical +0.2`、`social_intention → attack_mental +0.2` 等——若映射表分类与 signal_type 明显冲突（如 motor_command 边未获 attack_physical），修正。

## 五、任务分解

| # | 任务 | 类型 | 产出 | 依赖 |
|---|------|------|------|------|
| T1 | `domain_role_map.json`（§四 映射表落地） | 数据 | `data/connectivity/domain_role_map.json` | D3 |
| T2 | 重建脚本 `tools/build_contexts_tripartite.py`（读 tripartite+kroell14+映射表 → 双视图 JSON + stats + uncovered 报告） | 代码 | `link_contexts_tripartite.json` | T1 |
| T3 | 运行重建 + 验证报告：uncovered 边 / 角色分布 vs 旧 364 / 候选池规模与分布 | 执行 | `rebuild-report.md` | T2 |
| T4 | signal_type 辅助修正评估（冲突边清单 → 是否启用修正） | 分析 | 报告章节 | T3 |
| T5 | 文档同步：决策树 #72 / 六维状态 / `技能生成机制.md` 60 候选池 ⚠️ 注更新（填新规模）/ memory | 文档 | — | T3 |

## 六、验证方案

| 校验项 | 方法 | 通过标准 |
|--------|------|---------|
| 边键双射 | 重建脚本断言：888 边全部映射，键 = tripartite 索引 | 0 缺失 |
| 网络覆盖 | stats.network_assigned / uncovered_edges 报告 | uncovered ≤ 30（预期仅 thalamic_relay 独标签边） |
| 角色覆盖 | stats.role_assigned = 888；role_distribution 各角色 > 0 | 无全零角色 |
| 主副角色 | primary ≠ secondary；secondary 仅当 score > 0.25 | 规则一致 |
| 候选池 | stats.candidate_skills（context ≥2 边）；报告分布表 | 实测值（D4） |
| 旧对比 | 角色分布 vs 旧 364 分类（垃圾桶 classify_link_roles 输出） | 报告差异说明 |
| 确定性 | 重建脚本同输入同输出（纯函数） | 可复现 |

## 七、文件清单

| 文件 | 操作 | 类型 |
|------|------|------|
| `data/connectivity/domain_role_map.json` | 新建 | 数据 |
| `tools/build_contexts_tripartite.py` | 新建 | 代码 |
| `data/connectivity/link_contexts_tripartite.json` | 新建 | 数据 |
| `rebuild-report.md` | 新建 | 报告 |
| `规则/技能树系统/技能生成机制.md`（§二 ⚠️ 注更新） | 改写 | 文档 |
| `docs/决策树.md` / `docs/设计框架-六维状态.md` / memory | 追加 | 文档 |
| `data/README.md`（引擎 5 文件索引外补 link_contexts_tripartite） | 改写（可选） | 文档 |

## 八、数据契约与校验

### 不变量

- `link_contexts_tripartite.json` 的边键与 `tripartite_model.json` 数组索引双射（cc:NNN/pp:NNN）
- `contexts` 主视图与 `edge_contexts` 反视图互为转置（重建脚本断言）
- 候选技能定义 = context 内 `edge_count ≥ 2`（沿用技能生成机制 §二 过滤语义，链路→边迁移）
- 映射表权重 ∈ [0, 1]，每行至少一个正权重（除全零行——thalamic_relay 行需 ≥1）

### 校验

| 校验 | 命令 |
|------|------|
| 转置一致性 | 重建脚本内断言（contexts vs edge_contexts） |
| 交叉引用 | `python3 tools/validate_cross_refs.py` |
| 注册表 deprecated | `python3 tools/list_deprecated_terms.py`（任务 md 不出现旧 link_NNN/60 候选为当前值表述） |

## 九、验收标准

- [ ] `domain_role_map.json` 存在，12 domain × 8 role 权重表完整
- [ ] `link_contexts_tripartite.json` 双视图 + stats 生成，边键双射 0 缺失
- [ ] uncovered 边报告（预期 ≤30，thalamic_relay 独标签）
- [ ] 候选池规模实测值 + 分布报告（不设约束）
- [ ] `技能生成机制.md` §二 60 候选池注更新为三体重建新值
- [ ] 决策树 #72 条目 / 六维状态 / memory 落位
- [ ] 旧 link_contexts.json 未被任何活跃文档引用为当前数据源（#70 已加注，本次复核）

## 十、推迟清单

| 推迟项 | 原因 | 后续动作 |
|--------|------|---------|
| Hansen 社区（50 网络集合含混合+边缘） | `hansen_communities.json` 不存在（F-6，kroell14 _usage 引用但文件缺失） | 数据补齐 grilling（独立话题） |
| signal_type 辅助修正启用与否 | 需 T3 重建后看冲突边清单再定 | T4 分析 |
| 映射表权重校准 | 权重为初始值 | #35 数值校准 |
| 组件分类/药物调制复用双视图 | P5-3/P5-2 批次 | 消费方各自 grilling |

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [Grilling #70 路线图 task-plan](./../grilling-70-engine-roadmap/task-plan.md), [技能生成机制](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E6%8A%80%E8%83%BD%E7%94%9F%E6%88%90%E6%9C%BA%E5%88%B6.md), [NPC AI 行为模型](../../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md), [tripartite_model.json](../../../data/connectivity/tripartite_model.json), [kroell14_networks.json](../../../data/connectivity/kroell14_networks.json), [数学语言书写规范](../../../docs/agents/math-language-writing.md)*
