# #27 [Grilling] 链路生成管线全面审视与重构

> 状态：关闭 · 创建 2026-08-07 · 关闭 2026-08-07
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/27

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

审视并可能重构神经链路的整条生成管线——从数据源（50 解剖实体）到最终产物（链路合法性矩阵 + 链路注册表 + 调制天花板 + 技能参考）。

## 六维定位

- **维度**: 管线（主要） + 规则（链路数据是战斗/NPC AI/技能的底层基础）
- **依赖**: #25 解剖基座重构（已闭合）
- **阻塞**: 预烘焙 NPC 管线（bake_npc_behavior.py）、技能系统、战斗结算链路选择

## 当前状态

- `data/brain_regions.json` — 70 fids（#25 重构后）
- 364 条链路，由 `build_link_legitimacy_matrix.py` 生成
- CSTC 环路生成待完成（#25 遗留 P0）
- 链路重放路径待决策（A 全量/B 候选/C 手动）
- 多个生成脚本经 #20 和 #25 多次修补，可能存在架构债务

## 核心审视方向

1. 生成逻辑是否正确——从 50 实体的解剖连接约束推导链路的规则是否合理
2. 脚本间数据流是否清晰——10+ 工具脚本的依赖关系和调用顺序
3. 是否需要重构——合并/拆分/重写
4. CSTC 环路如何纳入当前体系

---

## 评论（1 条）

### verystrongdog · 2026-08-07

## Grilling #26 关闭总结 — 三体神经模型

### 决策表
| # | 决策 | 领域 |
|---|------|------|
| D1 | 三体模型：CSTC环路+皮层-皮层+脑干广播替代364链路 | 架构 |
| D2 | CSTC 3环路：躯体(Putamen)/认知(Caudate)/边缘(NAcc) | 设计 |
| D3 | 每环路3通路：GO(D1)/NO-GO(D2)/STOP(STN) | 设计 |
| D4 | 皮层-皮层四层渐降：EDR→层级→双向→功能标签交集 | 设计 |
| D5 | 脑干广播3系统：LC-NE/中缝-5HT/VTA-SNc-DA | 设计 |
| D6 | +STN, -2聚合体(BasalGangliaIndirectPathway, AmygdalaHippocampus) | 数据 |
| D7 | 图节点=dk_name(51), functional_id=通信模式标签(方案B) | 架构 |
| D8 | 功能剖面粒度=functional_id级, mirror_of共享 | 数据 |
| D9 | cstc_loop字段(somatic/cognitive/limbic/none) | 设计 |
| D10 | signal_type受控词表4大类×19子类 | 数据 |
| D11 | EDR p≥0.10天花板, 功能筛选交function_label层 | 设计 |
| D12 | 三种通信原语不平压为pairwise边 | 架构 |
| D13 | gameplay_domain 12项 | 设计 |
| D14 | Kroell网络→JSON | 数据 |
| D15 | 旧文件垃圾桶迁移9文件 | 清理 |
| D16 | 一致性清扫 | 清理 |

### 受影响文件
**已修改**: 脑功能层级模型.md(§十五废弃+§二十三体模型), 决策树.md, 六维状态.md, task-plan v3 + 2轮review-plan trace
**待实施**: signal_types.json, brain_regions.json(+STN+20profile-2), kroell14_networks.json, term_registry.json(+14), build_tripartite_model.py, build_function_labels.py, 垃圾桶迁移9文件

### 推迟
- batch 2功能剖面(~35 fids) / 术语注册表入库 / 一致性清扫 / NPC AI预烘焙更新 / 技能树3D可视化更新 / 战斗结算链路引用更新

### 质量
✅ review-plan v3: 0❌0⚠️ | ✅ Layer 1: 5/6 passed | ✅ cross_refs: 480/481 | ✅ trash_isolation: 238 clean | ✅ 引用即读取铁律全程遵守

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---
*导出: 2026-09-12 | 来源: GitHub issue*
