# 技能上下文三体重建 — Grilling #112 实施决策摘要（memory 镜像）

> Grilling #112 (2026-09-01) | 维度: 管线+规则 | Issue: [#112](https://github.com/verystrongdog/game/issues/112) | 分支: feat/p1a-context（commit 5de8968 + 9eed1c9）
> 本文件为 memory 文件的版本控制镜像（memory 本体在 ~/.claude/projects/-home-dog-game/memory/，沙箱只读无法直接追加）。

## Q 系列定案

- **Q0 边界**: P1a 实施前审查 ∪ #111 资格审查/六维验收表首个实战应用；候选池产物性质显式声明（程序化上下文，非手写技能）
- **Q1 对接契约**（外审 t_6a966「定稿技能对接契约」）: edge_contexts.source/target = **dk_name**（与 tripartite graph_nodes 对齐）；fid 反查归 P1c SkillCatalog；P1a 不承担引擎语义。「P1a 定义技能的结构事实，P1c 定义如何把这些结构事实变成可执行技能」
- **Q2 资格审查**（外审 t_6a96a「资格审查边界修正」）: 三步资格审查对象 = 「是否应成为 Module」非「是否有契约」；P1a 四产物全**非 Module**；link_contexts_tripartite = **非 Module 的强契约数据产物**（架构明确类别）——SchemaVersion + schema validation + 消费门禁 + fail-fast；**闭合 #111 推迟项「数据消费型试点验证 SchemaVersion 实际需求」**
- **Q3 六维验收表**: 适配为数据产物验收表，对 link_contexts_tripartite 6 条全判定（试点 PASS×5+N/A → 本轮首次 6 条实判，④版本敏感性不再 N/A）
- **Q3.5 前置核查**: 主路径无阻塞（tripartite/kroell14/gameplay_labels/role/dk_name 全就绪；domain 集合 12/12 对齐）；**function_label 实测 49%**（#92 重生成覆盖 build_function_labels.py 产物，git 66d1dd2/30108af）→ T4 推迟 + 上游修复单列（A′）
- **Q3.6 零角色**（外审 t_6a96a926）: flee（148 候选/0 主）/ disrupt（422 候选/0 主）= **KNOWN DESIGN LIMITATION**；本轮禁改权重；§六「无全零角色」不放宽不伪造 PASS；权重修正归 #35 校准轨，校准后复验

## 实施结果

- **888 边 → 71 contexts → 71 候选技能**（uncovered 0，优于预期 ≤30）
- 角色分布: attack_physical 246 / perceive 366 / support 110 / approach 103 / defend 57 / attack_mental 6 / **flee 0 / disrupt 0**
- 产物: `domain_role_map.json`（12×8 权重表）/ `build_contexts_tripartite.py`（D2/D3/D5 纯函数 + 转置断言 + role_health 诊断）/ `link_contexts_tripartite.json`（schema v1 双视图 + stats）/ `rebuild-report.md`
- 技能对接链声明: **P1a→P1b→P1c→技能系统 grilling→#35→呈现层**（P1a 为第 1 段；对接完成 ≠ 技能可玩）

## 下游待办

- P1b（LinkState m）/ P1c（SkillCatalog + SkillResolver + --demo-skill）实施——技能可执行管线
- #35: flee/disrupt 权重校准；上游 function_label 补跑（build_tripartite_model.py 重生成后重跑 build_function_labels.py）
- hansen_communities.json 补齐（F-6 独立话题）
- 技能系统 grilling: 涌现命名/独特效果/锚点对齐（P1c 后）

---
*创建: 2026-09-01 | 更新: 2026-09-01*
*关联: [rebuild-report](./rebuild-report.md), [task-plan](./task-plan.md), [外审-定稿技能对接契约](./外审-定稿技能对接契约-t_6a9661752658819183ff820d48d7bbaf-解码.md), [外审-资格审查边界修正](./外审-资格审查边界修正-t_6a96a2d7ed74819185311110b8b665eb-解码.md), [外审-验收标准六修正](./外审-验收标准六修正-t_6a96a92648ec8191923ca4178399fee5-解码.md)*
