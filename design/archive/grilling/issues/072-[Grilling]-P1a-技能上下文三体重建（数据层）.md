# #72 [Grilling] P1a 技能上下文三体重建（数据层）

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/72

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #70 路线图 P1a：把技能生成的上下文基础从「已废弃的旧 pairwise 364 链路」（link_contexts.json，F-1）重建到三体模型连接上——产出 `link_contexts_tripartite.json` 结构 + 8 行为角色分类规则 + 60 候选池验证方案。

## 六维定位

- **维度**: 规则（链路上下文/技能生成语义）+ 管线（数据重建工具链）
- **依赖**: Grilling #70 D8 / F-1/F-2 发现 + tripartite_model.json（1049 边，含 gameplay_labels/function_label）+ kroell14_networks.json（14 网络，含 gameplay_domains）+ signal_types.json（18 子类）+ NPC AI §3.3（8 角色 tone_bias 权重表）+ 技能生成机制.md（上下文→候选池规则）
- **阻塞**: P1b LinkState+m 成长 / P1c 技能执行 / 组件分类 / 药物调制（链路上下文是四者共同基础）
- **承接**: #70 路线图 P1a（拆细后独立 issue）

## 当前状态

- link_contexts.json（364 条，link_000_L 键）基于已废弃旧 364 链路（link_registry.json ⚠️ 已废弃标注）——F-1 确认「60 候选池」实测数据失效
- 8 行为角色分类不在三体数据中（tripartite 边 role = active/silent/modulating，脑干广播权重用）——F-2 确认需新分类器
- 可用数据：三体边全量含 gameplay_labels（12 domain，495 sensory_perception / 348 social_cognition / 276 memory_consolidation 等）；588 边含 function_label（signal_type）；kroell14 每网络含 2 个 gameplay_domains
- 旧 classify_link_roles.py（垃圾桶）为区域+网络+层级打分制（0.5/0.3/0.2 × 角色权重）——参考反面/迁移源

## 关键待决

1. 边集范围：CC+PP 仅信息传递边 vs 全 4 类边（brainstem/CSTC 是调制/门控原语）
2. 网络归属算法：gameplay_labels 桥接（边 labels ∩ 网络 domains）vs 端点区域→网络映射表重建
3. 8 行为角色分类器：gameplay_labels→角色映射表 vs signal_type 映射 vs 混合打分
4. 候选池规模语义：60 是设计约束还是旧数据实测快照
5. 数据 schema：context→edges 主视图 + edge→contexts 反视图

## 预期产出

- `.scratch/grilling-72-p1a-skill-context/task-plan.md`（数据结构 + 分类规则 + 重建步骤 + 验证方案）
- 决策树追加 + 六维状态更新 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #72 关闭总结

### 决策表（5 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | 边集 = CC+PP 信息传递边（888 条） | 范围 |
| D2 | 网络归属 = gameplay_labels 桥接（kroell14 domains ∩ 边 labels） | T2 |
| D3 | 角色分类 = 12 domain→8 role 映射表（domain_role_map.json） | T1 |
| D4 | 候选池规模 = 实测值不设约束 | T3 报告 |
| D5 | Schema = 双视图（contexts 主 + edge_contexts 反 + _rules + stats） | T2 |

### 数据发现

- kroell14 每网络含 gameplay_domains（机器可读）→ 桥接零新映射表
- **F-6 新发现**: hansen_communities.json 被引用但文件不存在（50 网络集合概念）→ 推迟独立话题

### 受影响文件

- `.scratch/grilling-72-p1a-skill-context/task-plan.md`（新建：schema/映射表/T1-T5/验证/验收）
- `docs/决策树.md`（#72 条目）
- `docs/设计框架-六维状态.md`（管线队列 P1a ✅）
- `memory/技能上下文三体重建-grilling-72.md`
- 实施后产出：domain_role_map.json / link_contexts_tripartite.json / build_contexts_tripartite.py / rebuild-report.md

### 推迟清单

- Hansen 社区/50 网络集合 → hansen_communities.json 补齐；signal_type 修正 → T3 后；映射表权重 → #35；组件/药物复用 → P5

### 质量门禁

- 5 决策全部落位 task-plan；边键双射/转置一致性/确定性写入不变量
- 后续：T1-T5 实施 → 重建报告 → 填回技能生成机制 §二

---
*导出: 2026-09-12 | 来源: GitHub issue*
