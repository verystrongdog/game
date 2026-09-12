# #15 [Grilling] 疾病系统独立建模

> 状态：关闭 · 创建 2026-07-31 · 关闭 2026-08-01
> 标签：维度:实体, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/15

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题
疾病作为一等实体独立建模。疾病 = 功能域 × 链路 × (病理类型, m偏移) 的配置。玩家角色和敌人 Stat Block 都引用同一套疾病目录。

## 六维定位
- **维度**: 实体
- **依赖**: 13 功能域 ✅ / 4 病理链路类型 ✅ / 228 链路 ✅ / CGI-S 分级 ✅
- **阻塞**: 敌人 Stat 实例 / 玩家角色正式化 / 14 角色→组件映射表

## 当前状态
- 疾病定义散落四处（玩家角色 ad-hoc 修改 / 敌人 §2.2 ICD-11 占位表 / 面具 §8.3 + §8.8）
- 13 功能域框架完整，4 病理链路类型已定义
- CGI-S 三级严重度已定义但未与功能域层对接
- 缺失：疾病作为独立实体的结构定义、疾病目录、CGI-S×功能域的缩放规则

---

## 评论（1 条）

### verystrongdog · 2026-08-01

## Grilling 关闭总结 — 疾病系统独立建模 + 工具链

### 决策表 (15 项)

| # | 决策 | 验证 |
|----|------|:--:|
| 1 | 疾病=一等实体，功能域×链路×(病理类型,m偏移)×CGI-S | ✅ |
| 2 | 13功能域为结算层，5 ICD-11症状域降级为表现维度 | ✅ |
| 3 | m偏移用固定值，个体差异从性格标签+seed涌现 | ✅ |
| 4 | CGI-S缩放 B模型基线，C模型(+行为临界)留给Boss | ✅ |
| 5 | 域数: 轻度1-2核心/中度+关联/重度+边缘 | ✅ |
| 6 | 目录规模~20+种含亚型 | ✅ |
| 7 | 第5种病理类型: 边界崩溃(Boundary Collapse) | ✅ |
| 8 | link_registry.json → 364条目 | ✅ |
| 9 | validate_disease.py → ERROR/WARNING分级校验 | ✅ |
| 10 | 模板: frontmatter + markdown表格混合 | ✅ |
| 11 | 层级相邻降级为信息性标记 → 228→364条链路 | ✅ |
| 12 | build_link_registry.py 自动生成注册表 | ✅ |
| 13 | 5种病理类型全覆盖 | ✅ |
| 14 | 组件掉落池三层权重(核心3/关联2/边缘1) | ✅ |
| 15 | 思路链必须标注文献来源和已知链路缺口 | ✅ |

### 受影响文件
- 实体/疾病目录/偏执型精神分裂症.md — 首个exemplar
- data/connectivity/link_registry.json — 364条链路注册表
- data/connectivity/link_behavior_roles.json — 364条全覆盖
- tools/build_link_registry.py — 注册表生成器
- tools/validate_disease.py — 6维校验
- 参考/文献/疾病-脑区链路映射-文献数据源.md — 文献锚点

### 回溯审计修正 (2026-08-01)
- 全局 228→364 链路数更新 (11文件)
- link_behavior_roles 重新分类为 364 全覆盖
- validate_disease 域数约束改为域级角色，删除冗余角色列

### 推迟
- 父类继承结构实现
- 剩余19+疾病填充
- 枕叶V1→楔叶+海马→杏仁核缺失链路

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---
*导出: 2026-09-12 | 来源: GitHub issue*
