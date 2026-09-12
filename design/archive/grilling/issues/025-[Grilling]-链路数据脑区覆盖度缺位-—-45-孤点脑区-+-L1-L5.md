# #25 [Grilling] 链路数据脑区覆盖度缺位 — 45 孤点脑区 + L1/L5 结构性缺位

> 状态：关闭 · 创建 2026-08-06 · 关闭 2026-08-07
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/25

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

364 条合法链路的**脑区覆盖度系统性缺位**：89 个脑区中 45 个（51%）不参与任何链路，L1 边缘系统与 L5 高阶前额叶整层结构性缺位。暴露于代码就绪度 grilling（#24）的速度排序实现中。

## 发现过程

实现速度排序（决断分 = 基底节 CSTC 环路 m 值）时发现基底节链路缺失 → 盘点全图 → 发现是系统性问题。

## 数据事实

- 仅 44/89 脑区（49%）参与链路
- 度分布极端不均：mPFC(61)/前脑岛(47)/DMN+OFC(43)/ACC(41) 四脑区占 192/364 条
- 0 链路脑区：L0 7个 / L1 12个 / L2 2个 / L3 3个 / L4 5个 / L5 16个
- 基底节（壳核3/尾状核1/苍白球0/纹状体0）CSTC 环路链路为 0——速度排序决断分无数据可取

## 根因（已定位）

三个数据源结构性缺陷：
- ENIGMA DTI 仅 68 个 DK 皮层标签（无皮下）
- Hansen FC 仅脑干核团（L0）
- subcortical_links.json 手动补充通道 connections: 0（从未补过）

## 六维定位

- 主要：管线（数据层完整性）
- 交叉：规则（速度排序/NPC AI/技能生成依赖链路数据）

## 影响面

- 速度排序决断分（#24 代码就绪度阻塞项）
- NPC AI 预烘焙查表（性格标签链路可能落在缺位脑区）
- 技能树生成（L1 情绪技能 / L5 高阶认知技能无链路载体）

## 前置

- #20（364 链路建模能力审查——本次为审查遗漏项）
- #23（校验管线体系——覆盖度校验可纳入）

---

## 评论（1 条）

### verystrongdog · 2026-08-07

## 🔒 Grilling 闭合总结 (2026-08-07)

### 决策表

| # | 决策 | 摘要 |
|---|------|------|
| D1 | 删除 7 设计节点 | VTA-NAcc/全脑整合/反射环路×3/AmygdalaPAGPathway/额顶网络 → brain_regions.json 移除 |
| D2 | 删除 8 通路型点位 | 弓状束/岛叶通路×5/mPFC-杏仁核/前额叶-海马/vmPFC-TPJ → 功能标签迁移到解剖端点 |
| D3 | 删除 4 细结构 | BNST/下丘脑/隔区/缰核 → Option B，附功能代偿方案 |
| D4 | 功能变体 collapse 到 dk_name | 10 组共享 OBJ，functional_id 保留 70 条目 |
| D5 | obj_file 60 条路径修复 | `技能树系统/` → `规则/技能树系统/3D可视化/` |
| D6 | L6 删除 | 旧 L6 5 条目全部 collapse/删除；L5 吸收终极链路约束 |
| D7 | 3 组层级冲突解决 | superiortemporal L4 / lateraloccipital L4 / caudalanteriorcingulate L2 |
| D8 | 三层功能网络覆盖框架 | Yeo 2011 (皮层) + CAB-NP (皮下) + Hansen 2024 (脑干) |
| D9 | 脑功能层级模型.md 重写 | 19 小节 11 个修改，L0-L5 六层架构 |

### 受影响文件

- **数据层**: `brain_regions.json` (70 fids) + `region_name_map.json` (70 同步)
- **核心文档**: `脑功能层级模型.md` (全面重写) + `决策树.md` + `六维状态.md` (3 处)
- **一致性清扫**: 15 .md 文件 `89脑区`→`50解剖实体` 引用修正
- **Python 脚本**: 7 文件，23 处修复（10 处 89脑区 + 13 处 L6 连带）
- **Memory**: `anatomical-foundation-refactor-2026-08-07.md`

### 质量门禁

| 校验器 | 结果 |
|--------|------|
| validate_link_data.py | ✅ 8/8 PASS |
| validate_disease.py | ✅ 0 ERROR |
| validate_cross_refs.py | ✅ 480/481 PASS |
| validate_trash_isolation.py | ✅ 全部通过 |
| validate_params.py | ⚠️ 23/27 PASS, 4 WARN (SAN阈值，已知) |
| validate_spatial.py | ⚠️ 3/4 PASS, S4 FAIL (is_design_node=0 硬编码，已知) |

### 推迟清单

- P-1: `build_link_legitimacy_matrix.py` bfb_region 键断裂
- P0: CSTC 皮层-纹状体-苍白球-丘脑-皮层链路生成
- 链路重放路径选择（A/B/C）
- `validate_spatial.py:77` 硬编码修复
- caudalanteriorcingulate {L2, L5} 1 组层级残留

### 审查 Trace

- `.scratch/review-trace-2026-08-06-2331-脑区数据反转-54实体.md`
- `.scratch/review-trace-2026-08-07-1138-brain-regions-data-refactor.md`
- `.scratch/review-trace-2026-08-07-1154-brain-regions-final.md`

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---
*导出: 2026-09-12 | 来源: GitHub issue*
