# P1a 重建报告 — link_contexts_tripartite.json

> Grilling #72 (P1a) T3 产物。三体连接 → 上下文集合映射重建结果与诊断。实施与决策记录见 Grilling #112。

## 一、重建结果

| 指标 | 值 | 对比旧 364 数据 |
|------|-----|----------------|
| 边集 | 888（776 CC + 112 PP） | 旧 link_contexts.json 364 条 pairwise 链路 |
| 网络归属 | 888/888（uncovered 0） | 旧 60 候选池（14 网络 × 8 角色） |
| contexts | 71 | 旧 87 |
| 候选技能（≥2 边） | **71** | 旧 60（2026-08-03 实测，已失效） |
| 角色分布 | 见 §二 | 旧：support 12 / attack_mental 12 / perceive 11 / approach 9 / flee 6 / attack_physical 5 / disrupt 3 / defend 2 |

**uncovered = 0 说明**：task-plan 预期 uncovered ≤30（thalamic_relay 独标签边）——实测 kroell14 14 网络域并集不含 thalamic_relay，但**无任何 CC/PP 边仅含 thalamic_relay 标签**（实测 0 条），故实际 uncovered = 0，优于预期。

## 二、角色分布与健康性诊断

```
attack_physical: 246   perceive: 366   support: 110
approach: 103          defend: 57      attack_mental: 6
flee: 0                disrupt: 0
```

**flee / disrupt 零主角色 = KNOWN DESIGN LIMITATION（外审裁决，Q3.6）**：

- flee 出现在 **148** 条候选边的 role_scores 中，但主角色 0 次
- disrupt 出现在 **422** 条候选边的 role_scores 中，但主角色 0 次
- **根因**：task-plan §四 初始权重下同域高权重角色稳定支配——threat_defense `defend 0.6 > flee 0.4`；social_cognition/cognitive_control 域 `support 0.5/0.3` 与 `perceive 1.0` 高于 `disrupt 0.2-0.3`
- **本轮禁止修改权重**：P1a 严格按既定初始权重重建，权重修正归 **#35 数值校准轨**，校准后重新验证
- **边界声明**：flee/disrupt = 0 **不是**「没有 flee/disrupt 上下文」的证据，而是「当前主角色判定权重无法使其成为 argmax」的证据——不得由 P4 等下游误读为"游戏无逃跑/干扰能力"

## 三、function_label 缺口（A′ 处置记录）

- task-plan §一 声明「588 边含 function_label」，**实测 432/888（49%）**：cc 368/776、pp 64/112
- **根因（git 证据）**：`66d1dd2`（#92 偏侧化重建，2026-08-20）用 build_tripartite_model.py 重生成，覆盖了 2026-08-07 build_function_labels.py 的 function_label 产物；`30108af` 仅恢复边注释字段。`_function_labels_applied: True` 为元数据残留
- **处置**：T4（signal_type 辅助修正）本轮推迟（可选增强 + 输入覆盖不足）；**上游修复项**：build_tripartite_model.py 重生成后需重跑 build_function_labels.py（或修正元数据语义）——非 P1a 范围，登记推迟
- **不影响**：D1-D3 主路径只用 gameplay_labels + domain_role_map，不依赖 function_label

## 四、契约字段（Q2 定案）

`link_contexts_tripartite.json` = **非 Module 的强契约数据产物**（Grilling #112 Q2 外审裁决）：

- `schema: "link_contexts_tripartite"` / `version: 1`——消费方（P1c SkillCatalog 等）加载时 version 不匹配 → fail-fast（对标 alpha_patterns/env_tones 先例）
- `edge_contexts.source/target` = **dk_name**（Q1 契约：与 tripartite graph_nodes.dk_name 对齐）；functional_id 反查归 P1c SkillCatalog
- 双视图互为转置（脚本断言保障）
- 边键 `cc:NNN` / `pp:NNN` = tripartite 数组索引，与三体数据顺序绑定

## 五、候选池说明（D4）

候选技能 = context 内 `edge_count ≥ 2`（沿用技能生成机制 §二 过滤语义，链路→边迁移）。**71 个候选上下文为程序化产物，非手写技能**——无命名、无独特机制，效果走 P1c 通用 role 公式。涌现命名/独特效果设计/锚点对齐属技能系统 grilling（P1c 后）。

## 六、验收状态

| task-plan §九 验收项 | 状态 |
|---|---|
| domain_role_map.json 12×8 权重表完整 | ✅ |
| link_contexts_tripartite.json 双视图 + stats 生成，边键双射 0 缺失 | ✅（888/888） |
| uncovered 边报告 | ✅ 实测 0（优于预期 ≤30） |
| 候选池规模实测值 + 分布 | ✅ 71（本报告 §一/§二） |
| 技能生成机制.md §二 60 候选池注更新 | ⏳ T5 文档同步 |
| 决策树 #72 条目 / 六维状态 / memory 落位 | ⏳ T5 |
| 旧 link_contexts.json 无活跃引用为当前数据源 | ✅ 复核：仅废弃标注段引用 |

---
*创建: 2026-09-01 | 更新: 2026-09-01*
*关联: [task-plan](task-plan.md), [link_contexts_tripartite.json](../../../../data/connectivity/link_contexts_tripartite.json), [domain_role_map.json](../../../../data/connectivity/domain_role_map.json), [build_contexts_tripartite.py](../../../../code/tools/build_contexts_tripartite.py), [技能生成机制](../../../rules/skill-tree/%E6%8A%80%E8%83%BD%E7%94%9F%E6%88%90%E6%9C%BA%E5%88%B6.md), [Grilling #112 issue](https://github.com/verystrongdog/game/issues/112)*
