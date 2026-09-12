# #113 [Grilling] 疾病资格层 Eligibility(d) 解耦 — 创伤负荷 ≠ 疾病资格

> 状态：关闭 · 创建 2026-09-01 · 关闭 2026-09-01
> 标签：维度:规则, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/113

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

# [Grilling] 疾病资格层 Eligibility(d) 解耦 — 创伤负荷 ≠ 疾病资格

*创建: 2026-09-03 | 状态: open*
*关联: [grilling-89](../grilling-89-npc-material/grilling-89-npc-material.md), [评审-顾维扬草稿-外部AI审查-t6a96e985](../grilling-89-npc-material/评审-顾维扬草稿-外部AI审查-t6a96e985.md), [评审-资格层解耦-外部AI审查-t6a96ecd6](../grilling-89-npc-material/评审-资格层解耦-外部AI审查-t6a96ecd6.md), [创伤记忆转化接口](../../规则/技能树系统/创伤记忆转化接口.md)*

---

## 评论（1 条）

### verystrongdog · 2026-09-01

## ✅ Grilling #113 闭合总结（2026-09-03）

### 决策表（机制层全量锁定）

| # | 决策 | 内容 |
|---|------|------|
| Q1 | 方案 A 前置硬门 | `Candidate → Eligibility → L_agg → Severity`；**Eligibility ⊥ L_agg**；Eligibility=0 ⟹ 不参与疾病竞争（主病选择+聚合+档位） |
| Q2 | 证据域 B | `E_d = E_d^mem ∪ E_d^hist`（记忆内表征域 + 记忆外临床史域）；H 为专门定义的资格证据域，非任意人物属性 |
| Q2-2 | 受控枚举 | 非自由文本解析；证据原子 ≠ 疾病—证据映射两层分离；新增映射附权威依据 |
| Q2-3 | 产出方 A | #87 A′-Generator 规范化声明字段；转化接口不解析叙事 |
| Q2-4 | MANIA/HYPOMANIA 分离 | BD-II → {HYPOMANIA, DEPRESSIVE_EPISODE_HISTORY}；铁律 `L_agg 不能充当任何发作史原子` |
| Q2-5 | 必要条件门 | Signature ⊆ Necessary（可共享）；BD-II = HYPOMANIA ∧ DEPRESSIVE ∧ ¬MANIA |
| Q2-6/7 | 三值两层 | 证据 {1,0,MISSING} × 状态 {ELIGIBLE,INELIGIBLE,UNDETERMINED}；组合规则；ELIGIBLE ≠ 已诊断 |
| Q2-8/9/10/11 | 核验体系 | 归位原则（d⟹P_i / N_j⟹¬d）/ 五步协议 / 资格语义锚（DSM/ICD 优先）/ A′ 原子依赖优先 + 疾病级分别核验 |
| G1-G4 | 全局不变量 | 原子语义≠成立依据 / DSM=语义锚≠输入清单 / 暂不拆分≠无需拆分 / 逻辑地位≠临床存在性 |
| 五基础原子 | 核验闭合 | DEPRESSIVE（MDD/BD-II 必要）/ SUBSTANCE_USE（SUD 必要候选）/ MANIA（BD-I 必要、BD-II 排除）/ HYPOMANIA（BD-II 必要）/ CYCLIC（环性必要候选） |
| #1/#2 | 语义与兼容 | 主/卫=召回级 vs Eligibility=资格级，正交；资格门只作用新生成，已落盘不回溯 |

### 顾维扬回放裁决（七步⑥⑦）

证据声明 {DEPRESSIVE=1, HYPOMANIA=0, MANIA=0, SUBSTANCE=0, CYCLIC=0} → **BD-II/环性/SUD INELIGIBLE，MDD ELIGIBLE → 主病 MDD 轻**（BD-II 被排除 = 必要原子 HYPOMANIA 未由 #87 声明成立，非叙事判断）。**顾维扬 BD-II 去留：降为 MDD。** #89 阻塞解除。

### 受影响文件

- `规则/技能树系统/创伤记忆转化接口.md`（§3.2.2 资格层 + §3.2.3 顺延 + §3.3 前置条件 + §四 + 头部/文末）
- `docs/决策树.md`（Grilling #113 条目）
- `docs/设计框架-六维状态.md`（规则维度）
- `data/term_registry.json`（+5 术语）
- `.scratch/grilling-113-disease-eligibility/`（决策记录 + 外审存档 19 份）
- `参考/灵感收件箱.md`（2 条灵感，含资格门活例）
- memory（`疾病资格层-grilling-113.md`）

### 推迟清单（#113 后续批次——方法已定、当前无消费者）

- SUD 三原子（LOSS_OF_CONTROL/TOLERANCE/WITHDRAWAL）归位（五步协议方法已定）
- 剩余 ~19 病逐病核验（24 病分类框架表：A 临床史/B 表征/C 混合三通道，初判/待核验）
- 物质类别拆分（暂不拆分，G3）
- E_d^mem 阈值化（DID→D_seg、PTSD→F）
- 前瞻性风险分层（不属 Eligibility 职责）

**过度设计刹车**：机制层 + 五基础原子 = 收敛点；本轮停止继续核验，后续批次按需恢复（有真实消费者时）。

---
*导出: 2026-09-12 | 来源: GitHub issue*
