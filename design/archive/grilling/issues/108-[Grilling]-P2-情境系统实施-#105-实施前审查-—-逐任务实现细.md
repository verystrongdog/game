# #108 [Grilling] P2 情境系统实施 #105 实施前审查 — 逐任务实现细节

> 状态：关闭 · 创建 2026-08-30 · 关闭 2026-08-30
> 标签：维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/108

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

工作issue 02 [#105](https://github.com/verystrongdog/game/issues/105)（P2 情境系统实现：EventProcessor 配置驱动 + 27 原型选择器 + 三通道 + m_field 落点）**实施前审查**——在 Grilling #75 方案（D1-D4）+ Grilling #104 实施决策（Q1-Q4+Q6）已锁定约束下，逐实现任务 T1-T7 追问细节（数据 schema / SituationSelector 算法 / moonState(D) 契约骨架 / 门禁 / fid 一致性校验器 / Console demo / 测试），达成共识后更新 task-plan + 写决策树，随后执行 #105。

## 六维定位

- 维度：管线（+规则消费端）
- 依赖：#75 task-plan（.scratch/grilling-75-p2-situation/task-plan.md）+ #101 R 落点结构 + #103 moonState(D)/calibration_status 契约 + 引擎现状（#91 关闭后 309/309 绿）
- 阻塞：无（#91 已关闭，#105 已解锁）
- 承接：#104（P2 实施启动，已闭合）

## 当前状态

- #105 OPEN、排队中、可启动
- 顶层决策已锁定：#75 D1-D4、#104 Q1-Q4+Q6（m_field 结构实现+PLACEHOLDER+门禁、env_tones demo 3 环境、key_brain_regions fid 直用+27 原型全量校验器、无 dk→fid 映射表）
- 本 grilling 不重开顶层设计，只审查实施层细节

---

## 评论（1 条）

### verystrongdog · 2026-08-30

## ✅ Grilling #108 闭合 — P2 情境系统实施前审查（Q1-Q15 执行契约）

### 决策表（15 项，全部经外部 AI 评审逐题核验后采纳）

| # | 分支 | 定案 |
|---|------|------|
| Q1 | B1-① | alpha_patterns 契约：row_id→pattern[8]；绑定留代码；m_alpha 二态（[0,1]∪"m_delta"）；5 类加载错误 fail-fast（JsonException）；14 行/10 消费 |
| Q2 | B1-② | W_sensory 69×8 锚点：嗅觉{LOFC,Amygdala}/热觉{Postcentral,Insula}；允许三模态 |
| Q3 | B1-③ | env_tones：英文 slug id+display_name；ward/corridor/nurse_station；fail-fast；CurrentEnvironment=string |
| Q4 | B2-④ | 情境全局单一；存在性 SAN 调制；刷新=空间切换∪任意 C1 |
| Q5 | B2-⑤ | env_map 折叠进 env_tones（situation.primary）；删除 alternates |
| Q6 | B2-⑥ | G={neg_valence≥t_neg(0.2)∧valence=negative}（17 成员）；p_panic=0.5 语义；G 与 primary 不互斥 |
| Q7 | B2-⑦ | 强度双档 1.0/s_neg∈[1,1.5]（数值→#35）；与 α_env 正交 |
| Q8 | B2-⑧ | C1 事件流驱动重选、下一回合生效；恐慌消退不重选 |
| Q9 | B3-⑨ | moonlight_landing 参数 schema；r/α_s="PLACEHOLDER"；字段缺失≠占位；四项校验引擎侧 |
| Q10 | B3-⑩ | MoonState 静态纯函数 Query(int day)；N=69 占位契约；D 推进/广播不实现 |
| Q11 | B3-⑪ | CalibrationGate 挂 m_field 注入点；s_env 不挂门禁；--mfield-demo 例外 |
| Q12 | B3-⑫ | Phase 1 注入点合成 s_total=SPending+s_env+m_field；g≡1.0 占位；Step 签名零改动 |
| Q13 | B4-⑬ | fid 校验两层防线（validate_situation_fids.py + 引擎侧断言）；不建 dk→fid 映射表 |
| Q14 | B5-⑭ | --demo-situation 非交互 trace 模式（--env/--day/--rounds/--seed/--mfield-demo） |
| Q15 | B5-⑮ | 测试矩阵 G1-G9；309 回归门槛；p_panic 契约断言不做频率统计 |

### 受影响文件

- `.scratch/grilling-75-p2-situation/task-plan.md`（执行契约，Q1-Q15 注入）
- `.scratch/grilling-108-p2-impl-review/`（14 份外审存档）
- `docs/决策树.md`（Grilling #108 条目）
- `docs/设计框架-六维状态.md`（管线 +1 → 24）
- `项目总览.md`（5.0 P2 状态）
- `data/term_registry.json`（+6 术语：G/t_neg/s_neg/p_panic/m_delta/环境 id）
- memory（情境系统引擎-grilling-108.md）
- commit `c050945`

### 推迟清单

正式校准数值（r/α_s/q̂/E_c/E_th/g(SAN)/s_neg）→ #35；artifact 6 项硬校验 → #71；env_tones 全环境表值 + situation.primary 全表 + G 组精化 → 空间内容填充；q̂ 空间差异 → graph/spatial 校准；D 推进 + MOON_PHASE_CHANGED 广播 → 游戏循环实施。

### 质量门禁

一致性清扫通过（alternates 删除语境 / 旧 m 哨兵清零 / 占位全 0 仅历史 / dk→fid 仅 W 矩阵技术语境）；写入验证表 17 项全部 ✅已验证；commit c050945 落盘。

**#105（P2 情境系统实施）现已可执行**——按 task-plan 执行契约实施即可。

---
*导出: 2026-09-12 | 来源: GitHub issue*
