# #12 [Grilling] 预烘焙管线脚本设计

> 状态：关闭 · 创建 2026-07-31 · 关闭 2026-07-31
> 标签：维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/12

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

预烘焙管线脚本设计 — 将 NPC AI 行为模型中定义的"设计师选标签 → 髓鞘化偏移 → 27 情境 × N SAN 分段行为概率分布表"转化为可运行的脚本/工具。

## 六维定位

- **维度**: 管线
- **依赖**: NPC AI 行为模型 ✅ / 情境系统 ✅ / 链路合法性矩阵 ✅ / 髓鞘化成长 ✅ / 性格标签 ✅ / SAN 系统 ✅
- **阻塞**: 具体敌人 Stat 实例 / 数值平衡工具

## 当前状态

- NPC AI 行为模型 §三 已定义管线流程框架（6 步）
- NPC AI 行为模型 §十二 已定义设计师工作流（4 步必需 + 脚本自动完成）
- 数据源已就绪：27 情境原型 / 228 合法链路 / 89 脑区 / 6 性格标签
- 管线脚本本身尚未设计

## 核心决策待定

- 采样算法的具体实现
- 行为表的输出格式/数据结构
- 脚本架构（模块划分/输入输出）
- 链路效果量化如何嵌入管线
- 运行时查表 API 设计
- 与 Unity 的集成方式

---

## 评论（1 条）

### verystrongdog · 2026-07-31

## Grilling 完成 — 预烘焙管线脚本设计

### 15 项决策

- 范围界定: 管线架构+算法+数据格式, 228量化延迟
- 名称规范化: situation_primitives.json 85→66规范名, 100%命中
- 标签映射: personality_tag_links.json自动生成, 连带偏移共享脑区计算
- 行为角色: 8类自动分类, 用于采样校验
- 采样算法: **Softmax** (Boltzmann) 替代 Monte Carlo
- beta动态: clamp(beta_base(SAN) + tag_mods, 0.1, 5.0)
- 情境匹配: **模型 A 分层门控** (L0=2.0, L1=1.5, L2=1.3, L3+ x epsilon)
- 槽位梯度: L0=0, L1=0.5, L2+=1, NPC复用髓鞘化减免
- 输出格式: 单JSON 27情境x3SAN段, 1%截断, default回退
- 不放回多选: Luce's choice axiom 乘积近似

### 受影响文件 (13个)

新建: 管线/预烘焙管线脚本设计.md, link_behavior_roles.json, personality_tag_links.json, 3个工具脚本
修改: situation_primitives.json, NPC AI 行为模型.md, 核心机制.md, 回合战斗流程.md, 链路槽位与激活系统.md, 决策树.md, 六维状态.md, 维度/管线.md, 项目总览.md, 灵感收件箱.md

### 延迟

- 228链路效果量化 (内容填充)
- bake_npc_behavior.py 主脚本实现 (规格已定)
- Unity C# 运行时查表
- 标签→链路映射人工微调

---
*导出: 2026-09-12 | 来源: GitHub issue*
