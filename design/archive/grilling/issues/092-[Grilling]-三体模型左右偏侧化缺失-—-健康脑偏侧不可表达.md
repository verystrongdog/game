# #92 [Grilling] 三体模型左右偏侧化缺失 — 健康脑偏侧不可表达

> 状态：关闭 · 创建 2026-08-20 · 关闭 2026-08-20
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/92

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

本地: .scratch/grilling-91-lateralization/grilling-91.md

## 问题

**正常人类大脑存在稳健的左右功能差异，但项目神经系统模型（三体模型）完全无法表达这一点——且这不是有意的设计决策，而是 #26 重构时被静默丢弃的既有能力。**

### 证据链（已核验，引用即读取）

1. **健康脑偏侧真实且显著**（文献层）：
   - Kong et al. 2018（ENIGMA，17,141 健康人/99 数据集，PMID 29764998）：左半球皮层更厚/表面积更小；语言区（额下回岛盖部、Heschl 回、颞上回/颞平面）左偏最强；区域级偏侧效应量远大于疾病组差异
   - Karolis et al. 2019（PMID 30926845）：偏侧沿四功能轴分布——符号沟通（语言）→左、情绪→右
   - 详见 `参考/文献/左右脑偏侧化-文献数据源.md`（2026-08-03 建）+ `参考/文献/ENIGMA偏侧化-精神疾病大样本meta-文献数据源.md`（2026-08-20 建）

2. **三体模型无左右（数据层）**：
   - `data/connectivity/tripartite_model.json`：51 个节点，**0 个 L/R 皮层节点**；唯一带侧向标记 = `LocusCoeruleusRight`/`SubstantiaNigraParsCompactaRight`（脑干镜像，0 出边、0 次作端点）
   - 语言区（parsopercularis/superiortemporal/transversetemporal）各一个合并节点

3. **设计文档从未讨论左右（文档层）**：
   - `规则/技能树系统/脑功能层级模型.md`（三体模型正典）grep `左右/偏侧/双侧/合并/hemisphere/镜像` **零命中**

4. **历史沿革（决策层）**：
   - Grilling #20 D10（决策树 :1414）：「链路粒度 = 解剖粒度（DK 左右边独立），偏侧异常值得作为游戏机制」——旧 364 链路系统支持左右独立
   - Grilling #26（2026-08-07）三体模型重构（51 节点）**静默丢弃左右独立**，无任何决策记录讨论此取舍

### 暴露的连带问题

- **SZ 偏侧异常无法承载**：ENIGMA 三独立大样本（Schijven 2023 PMID 36976765 / Okada 2016 PMID 26782053 / Gutman 2022 PMID 34498337）确认 SZ 是唯一偏侧稳健的精神疾病（左语言网络薄化↔幻听、rACC 偏侧反转、苍白球左偏），效应量 |d|<0.1（极小）——但合并节点无法表达"左"的异常
- **#88 重映射端点规格无落点**：`pathology_edges.json` 若用 DK 偏侧名（L_/R_）记录文献（数据保真方案），结算时合并到"无左右节点"——偏侧信息无处安放
- **镜像实体数据断链**：`LC_R`/`SNc_R` 的 `function_profile: {mirror_of: …}` 未展开（input/output_types 为 None），T8 校验只查"目标缺失"不查"未展开"

## 已知待讨论问题（grilling 逐题展开）

1. **三体模型是否应表达健康偏侧**：语言左/情绪右作为游戏可见要素（技能命名/展示/叙事锚点），还是彻底合并（偏侧仅存文献层）
2. **SZ 单侧异常承载方式**：若保留偏侧，SZ 的左语言网络/苍白球左偏如何落地（节点级元数据 vs 微调 m vs 叙事装饰）
3. **节点加偏侧元数据（方案 B″）的字段设计**：`lateralization`（left_dominant/right_dominant/bilateral）+ `strength`（0-1）+ 不进结算的范围声明
4. **镜像实体（LC_R/SNc_R）处置**：mirror_of 展开（完整剖面）vs 显示占位（坐标/显示用，机制引用主变体）
5. **pathology_edges.json 端点规格**：DK 偏侧名（L_/R_，文献保真）+ 合并规则 vs 直接 50 实体名（偏侧仅注释）
6. **与 #88 的边界**：本 issue 定偏侧架构，#88 定疾病→映射内容——谁先谁后、依赖关系

## Comments

- **2026-08-20（拆出背景）**：本 issue 从 #88（病因-疾病-神经转化接口）讨论中拆出。用户在重映射前置讨论中追问"左右脑功能是否有区别"，经文献检索（ENIGMA 偏侧 6 篇 + 项目已有偏侧文献数据源）确认：健康偏侧显著（值得可见）、疾病偏侧极小（仅 SZ 稳健、不值得拆 68 节点）。随后用户发现三体模型本身无左右——暴露本问题。
- **已否决的路线（备查）**：C″ 全拆 68 节点（推翻 #26 的 51 节点图，776 条皮层-皮层边按偏侧重算，成本与 d<0.1 收益不成比例）——用户此前讨论中已倾向否决。

---

## 评论（1 条）

### verystrongdog · 2026-08-20

## ✅ Grilling #92 闭合 — 三体模型左右偏侧化缺失

**决策表（10 项，全部共识确认）**

| # | 决策 | 内容 |
|---|------|------|
| D1 | 节点级元数据（B″） | 51 节点图不动 + 偏侧元数据，**不进战斗结算**；C″ 全拆 68 节点否决 |
| D2 | SZ 单侧异常 = 元数据微调 | 节点存健康基线，SZ 敌人/面具取值偏离（rACC 反转/MTG 增大/苍白球左偏），不进结算 |
| D3 | 可见性 A + 入库 | 偏侧标签仅玩家自角色可见（黑箱原则）；敌方/面具偏离如实入库（数据保真） |
| D4 | β 单一连续系数 | lateralization ∈ [−1,+1]（负左正右 0 双侧），Karolis 2019 原样；否决 α 双字段 |
| D5 | P1 解剖实体级 | 一合并节点一系数，写 graph_nodes + brain_regions |
| D6 | M1 + 前向规则 | 镜像展开 10 字段 + mirror_of 溯源；新镜像默认显示层、机制引用=报错 |
| D7 | Y′ 端点 + Δ | pathology_edges 端点 = 50 实体名 + laterality_delta ∈ [−1,+1]（默认 0） |
| D8 | Q0.1 以「B+Δ」定案 | #88 重映射锚点 = 50 实体名 + Δ，双轨废止 |
| D9 | 显示层派生 | t=0.5 [NEW 初值可调]；叠加 = baseline + ΣΔ 不落盘，显示层 clamp [−1,+1] |
| D10 | 正交声明 + Δ 随病理边 | mni_xyz = 解剖代表位置与偏侧正交；Δ 随 pathology_edges 病理边（§8.8.2 铁律） |

**受影响文件**
- 规则/技能树系统/偏侧化架构.md（新建正典）
- 规则/技能树系统/脑功能层级模型.md（§二十 20.11）
- docs/决策树.md（#92 记录 + #26 缺失补注）
- docs/设计框架-六维状态.md（规则 34→35、管线 21→22）
- data/connectivity/tripartite_model.json（49 节点 lateralization）
- data/brain_regions.json（58 条目 + 镜像展开）
- data/term_registry.json（5 术语入库）
- tools/build_tripartite_model.py（lateralization 生成）
- data/README.md、.scratch/grilling-88-etiology-disease-neural/grilling-88.md（Q0.1 标注）
- memory/偏侧化架构-grilling-92.md

**写入验证**：全部通过（JSON 校验 / lateralization 范围 [−1,+1] / 镜像 diff=0 / 脚本重跑一致 / 决策树+六维状态+注册表同步）

**推迟清单**：3D 偏侧呈现 → 呈现维度；健康基线数值表 → 内容批次；pathology_edges.json 创建 + Δ 取值 → #88（阻塞解除）；t 调参 → [NEW 初值可调]

**Git**: d643d5d（docs）+ 66d1dd2（data/tools）

---
*导出: 2026-09-12 | 来源: GitHub issue*
