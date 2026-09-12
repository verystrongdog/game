# 规则

> 定义"能发生什么、怎么发生"。删除所有角色和地点后，这个逻辑仍然成立。

**分拣标准**：删除所有角色和地点后，这个逻辑仍然成立吗？成立 → 规则。

## 索引

### 核心文档
- [01-核心机制.md](../../rules/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md) — 脑区链路模型/战斗结算/SAN/情境
- [脑功能层级模型.md](../../rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md) — L0-L5六层/50解剖实体正典
- [运行时状态模型.md](../../rules/skill-tree/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) — 三层因果链动力学/91状态变量
- [记忆内容层.md](../../rules/skill-tree/%E8%AE%B0%E5%BF%86%E5%86%85%E5%AE%B9%E5%B1%82.md) — MemoryRecord 内容层存储（schema/写入/检索/生命周期），2026-08-20 grilling #90
- [NPC AI 行为模型.md](../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md) — Affordance Competition 实时 salience/7参数化性格/敌我同构
- [基础行动设计.md](../../rules/skill-tree/operations/%E5%9F%BA%E7%A1%80%E8%A1%8C%E5%8A%A8%E8%AE%BE%E8%AE%A1.md) — 物理攻击/精神攻击/防御
- [链路调制上限参考表-v2.md](../../rules/skill-tree/modulation/%E9%93%BE%E8%B7%AF%E8%B0%83%E5%88%B6%E4%B8%8A%E9%99%90%E5%8F%82%E8%80%83%E8%A1%A8-v2.md) — 三因子调制模型
- [时空结构数学框架.md](../../rules/%E6%97%B6%E7%A9%BA%E7%BB%93%E6%9E%84%E6%95%B0%E5%AD%A6%E6%A1%86%E6%9E%B6.md) — 时空分布量数学框架/CGL+AGC身份/边界声明

### 操作层（技能生成）

- [武器与装备.md](../../entities/%E6%AD%A6%E5%99%A8%E4%B8%8E%E8%A3%85%E5%A4%87.md) — 武器/护甲/精神武器/Boss 专属装备，2026-08-05 grilling #21
- [基础行动设计.md](../../rules/skill-tree/operations/%E5%9F%BA%E7%A1%80%E8%A1%8C%E5%8A%A8%E8%AE%BE%E8%AE%A1.md) — 物理攻击/精神攻击/防御，开局即存在
- [技能生成机制.md](../../rules/skill-tree/%E6%8A%80%E8%83%BD%E7%94%9F%E6%88%90%E6%9C%BA%E5%88%B6.md) — 链路上下文技能（网络集合×主导角色），60候选池 + 涌现触发

> ⚠️ 37 个 AI 操作技能（L0-L6）已于 2026-08-03 废弃（D20），移入垃圾桶。技能系统已改为链路上下文范式（Grilling #20）。

### 数据
- [tripartite_model.json](../../../data/connectivity/tripartite_model.json) — 三体神经模型（CSTC环路+皮层-皮层+脑干广播）
- [link_modulation_ceiling_v2.json](../../../data/connectivity/link_modulation_ceiling_v2.json) — 链路调制天花板
- [situation_primitives.json](../../../data/connectivity/situation_primitives.json) — 27情境原型

### 参考（已废弃，保留为数据源）
- 态度系统/ — ⚠️ 态度引擎（已废弃，参考数据源）
- 情绪系统/ — ⚠️ PAD情绪空间（已废弃，参考数据源）
- 行为系统/ — ⚠️ 7驱动模型（已废弃，参考数据源）
- 认知系统/ — ⚠️ 5模块模型（已废弃，参考数据源）

---

*创建: 2026-07-28*
*关联: [设计框架-六维状态](../six-dimensions.md)*
