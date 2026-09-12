# #33 [Grilling] 公式同步 — 核心文档旧公式 (m×rel×focus) → 运行时状态模型新公式体系

> 状态：关闭 · 创建 2026-08-09 · 关闭 2026-08-09
> 标签：维度:规则, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/33

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 六维定位

- **维度**: 规则
- **性质**: Grilling #32（运行时状态模型）的执行遗留项——不是新设计
- **依赖**: #32 已完成（15 决策），运行时状态模型.md §十 明确列出 4 个待更新文件
- **阻塞**: 无

## 当前状态

Grilling #32 确立了新的三层因果链动力学（WC + brainstem tone + Gurney gating），废弃了链路级 `m × rel × focus` 乘积公式。但 3 份核心文档仍保留旧公式：

| 文件 | 位置 | 旧内容 |
|------|------|--------|
| `规则/核心机制.md` | §2.1 | `激活水平(link) = 基线(m) × 情境调制(rel) × 聚焦倍率(focus)` |
| `规则/技能树系统/技能生成机制.md` | §一, §五 | `skill_effect = Σ m_i × focus_i × rel(i, current_situation)` |
| `规则/回合战斗流程.md` | §三 | 速度排序察觉/决断/执行分从"静息 m 值"取 |

第 4 个文件 `data/term_registry.json` 已在 2026-08-09 一致性清扫 batch 2 中更新。

## 范围

只做公式替换（废弃标注 + 新公式摘要 + 指向运行时状态模型），不引入新参数/新机制。

---

## 评论（3 条）

### verystrongdog · 2026-08-09

## Grilling 完成 — 公式同步

### 决策表

| # | 决策 | 内容 |
|---|------|------|
| D1 | 替换策略 | 直接替换，不保留旧公式（历史已存于皮层动力学 §2.1 / 运行时状态模型 §九 / 决策树 #32） |
| D2 | 核心机制 §2.1 | 三层因果链摘要 + 四要点 + 指向 运行时状态模型 |
| D3 | 技能生成 §一/§五 | skill_effect → skill_base_effect × gate_bonus(role)；§五 整节重定向 |
| D4 | 回合战斗流程 §三 | 速度排序数据源 静息 m → a(t) 节点 |

### 受影响文件

- `规则/核心机制.md` §2.1
- `规则/技能树系统/技能生成机制.md` §一, §五, §六
- `规则/回合战斗流程.md` §3.1, §3.2, §3.3
- `docs/决策树.md`

### 推迟

无——本次为 #32 执行遗留项，所有变更已完成。

### 一致性验证

- `m × rel × focus` grep: 零残留（仅出现在已废弃段/历史对照中）
- `静息 m` grep: 零残留
- `skill_effect Σ m` grep: 零残留

### verystrongdog · 2026-08-13

## 🔧 闭合后修正 (2026-08-13)

csharp-engine 引擎实现（csharp-wc-dynamics + csharp-tone）对 Grilling #32 三条决策的实质性修正——commit `f3cfbbc`：

| 原决策 | 修正后 | 根因 |
|--------|--------|------|
| D3 — fast 节点解析解特例（Δ/τ≥50），其余 Euler+clip | 全节点统一解析解 `a_j' = σ(h_j) + (a_j − σ(h_j))·e^(−Δ/τ_j)`（fast 特例即其 e^(−100)≈0 情形） | 审计数值证明 Δ=1、τ=0.01-0.15 下 Euler 对 medium/slow 同样产生 bang-bang 振荡 |
| D6 — 自然上限=2.0（Accumbens-area 接收 DA_VTA+DA_SNc 均 active） | mOFC 3 fid（FrontalPoleDMN / MedialOrbitalPrefrontalDMN / MedialOrbitalPrefrontalVMPFC）pre-clamp 2.5（5HT active + VTA active + LC modulating），clip [0,2] 兜底 | C# 实测（csharp-tone AC-13）；决策核心（clip [0,2]）不变 |
| D7 — tone 离散 Euler + clip [0,1] | 解析解 `tone' = clip(baseline + δ_eff + (tone−baseline−δ_eff)·e^(−Δ/τ), 0, 1)`，δ_eff = δ × δ_scale（δ_scale=0.3 [NEW]） | 同 D3；Euler 在 Δ/τ 0.67-3.33 下数值行为差。无 sigmoid、τ 值、clip [0,1] 不变 |

受影响文档：运行时状态模型 §4.1/§5.2/§5.5/§7.1/§7.2/§7.3.1（新增 M1 静息不动点实测）、皮层动力学-通用层 §3.3/§4.2/§4.3、回合战斗流程 §3.2/§3.3、决策树 #32 D3/D6/D7 🔧 行、term_registry v1.6。

### verystrongdog · 2026-08-13

## 🔧 闭合后修正 (2026-08-13)

> 触发：csharp-engine step 6（csharp-cstc）任务issue 数据实测暴露——设计参数下 CSTC 门控惰性（gate 恒 1.0），且跨环路「双重消费」与运行时 fid 级状态不符。用户 Q1/Q2/Q3 裁决后写回。

| 原决策 | 修正后 | 根因 |
|--------|--------|------|
| D9/D13：跨环路 CI「a(t) 双重消费」 | fid 级归属：同 dk 不同 fid 分属两环（caudalanteriorcingulate / superiorfrontal 各按 fid 拆分），每 fid 只贡献一环 | 运行时 WC 状态为 fid 级 69 维，无 dk 级聚合层（Q3 裁决 B） |
| D10：ramp 统一阈值 e=0.2（§6.3 简化） | per-population 阈值：e_SEL/e_CONT=0.2、e_STN=−0.25、e_GPe=−0.2、e_GPi=−0.2（对齐 ModelDB 83560 GPR_engine.m 原始实现） | 统一 e=0.2 下 GPi 输入 0.9·O_STN − O_SD1 永不过阈 → gate 恒 1.0，CstcGating 惰性；tonic 抑制来自负阈值（Q2 裁决 A） |
| 91-var 表 L3 十五群体值域 [0,1]（clamp） | [−1.5, 2.0]，无 clamp | 负阈值机制要求 a 可为负；clamp[0,1] 与负阈值互斥（实测 gate 被锁 ≤0.8）（Q2 裁决 A） |
| 权重表缺 W_SEL_GPe（文献缺口传播） | 补 W_SEL_GPe = 0.0（SD1→GPe 无连接；Gurney 2004 'g' 选项 −0.25 备用） | ModelDB 83560 默认；csharp-engine plan §十三-3 遗留闭合（Q1 裁决 A） |

**修正后实测行为**：c=0 → gate=0.843（门控抑制恢复）；DA≥0.5 且 c≥0.4 → gate=1.0（全放行）；静息 → 1.0。

**受影响文件**：`规则/技能树系统/运行时状态模型.md` §6.1/§6.2/§6.3/§三/§十一、`data/connectivity/README_gurney_model.md`、`.scratch/csharp-engine/design/plan.md` §4.4、`src/YouAreNotTheFish.Core/Types/GurneyState.cs`（值域注）、`data/term_registry.json`（c_loop/gate_bonus/Gurney模型）、`docs/决策树.md`（D9/D10/D13 🔧）。

---
*导出: 2026-09-12 | 来源: GitHub issue*
