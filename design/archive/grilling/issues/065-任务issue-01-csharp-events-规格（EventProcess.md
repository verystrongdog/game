# #65 任务issue 01: csharp-events 规格（EventProcessor）

> 状态：开放 · 创建 2026-08-13
> 标签：维度:管线, ready-for-agent
> 原始：https://github.com/verystrongdog/game/issues/65

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

本地: .scratch/csharp-events/design/issues/01-events-spec.md

## 范围

产出 [spec.md](../spec.md) v1.0，覆盖 plan §十一 step 9（csharp-events = EventProcessor）：

- 消费 CombatEvents（PhysicalDamageEvent / MentalDamageEvent / StatusChangeEvent / HealEvent / LinkGrowthEvent）→ 按 运行时状态模型 §5.5 派生 δ 发射（14 事件 δ pattern 表）与 s 累计（§4.5 s = W_sensory × α）
- δ：对每参与者 Σ 聚合后调用 ToneUpdater.Step（csharp-tone 交付，未缩放原始 δ + δ_scale=0.3 内部生效）
- s：W_sensory 69×6 × α 向量，float[69] 增量返回，Phase 1 注入（下游 step 10）
- 不覆盖：TurnManager/CombatState 编排（step 10）、NpcSalience（step 11）、事件生产（DamageCalculator 调用方）

## 数据实测

### 第一轮（设计级——事件覆盖 + 数据面）

| # | 实测项 | 结果 |
|---|--------|------|
| 1 | demo 可触发事件覆盖 | 10/14：A1/A2/A4/A5/B1/B2/B4/C1/D1/D2。A3/B3 crit、A6 skill、A7 flee 无事件类型（demo 无暴击/技能/逃跑），实现不落地、spec 偏差声明 |
| 2 | W_sensory 69×6 | 双模态 12 节点 / 单模态 25 / 全零 32 行（25 subcortical+脑干 + 7 皮层无感官输入，如 Precentral/PosteriorCingulate）。列和：visual 11 / auditory 6 / somatosensory 4 / pain 7 / social_cognition 15 / language_cognition 6。matrix/rows 失配 0 |
| 3 | s 例证 | A1 α=(1,0,1,0,0,0)×1.0 → s[Postcentral]=1.0；D1 α=(1,1,0,0,1,0)×1.0 → s[SuperiorTemporal]=2.0（双模态可达 2.0，无 clip——WC sigmoid 饱和） |
| 4 | §5.5 δ pattern 表核对 | A1(0,+,+,0)/A2(0,−,0,0)/A4(0,+,0,0)/A5(0,0,0,+)/B1(+,0,0,−)/B2(0,0,0,+)/B4(+,0,0,−)/C1(+,0,0,−)/D1(+,−,0,−)/D2(0,+,0,+)——见 运行时状态模型 §5.5（NE/DA_VTA/DA_SNc/5HT 序） |
| 5 | α pattern 表核对 | A1(1,0,1,0,0,0)/A4(0,0,0,0,1,1)/A5(0,0,1,0,0,0)/B1(1,0,1,1,0,0)/B2(1,0,1,0,0,0)/B4(0,0,0,1,1,1)/C1(0,0,0,1,0,0)/D1,D2(1,1,0,0,1,0)（视觉/听觉/躯体/痛觉/社会/语言序） |
| 6 | m 公式来源核对 | A1/A3/A4 m=actual/expected；A2 同式（≈0）；A5 m=damage_blocked/incoming_damage；A7/C1/D1/D2 m=1.0；B1/B3 m=|ΔHP|/HP_max；B2 m=blocked/incoming；B4 m=|ΔSAN|/SAN_max。m<0.01 → 跳过 emit |

### 第二轮（m 数值案例，f32）

| # | 案例 | m 值（f32） |
|---|------|------------|
| 7 | B1 杂兵 |ΔHP|/HP_max = 5/15 | 0.33333334 |
| 8 | B1 玩家 5/50 | 0.1 |
| 9 | A4 actual/expected = 2.0/2.0 | 1.0（2×(1+0)−1 忍耐被动，见 Q3） |
| 10 | A5 blocked/incoming = 0.5 | 0.5 |
| 11 | B4 |ΔSAN|/SAN_max = 2/60 | 0.033333335 |
| 12 | C1/D1/D2 | 1.0（恒定） |
| 13 | A2 miss（m=0） | δ 通道跳过（m≥0.01 才 emit）；s 通道 A 类 m_α=1.0 仍发（自身行动感官完整） |
| 14 | m 跳过边界 | 0.01f ≥ 0.01f = True（emit）；0.0099999f ≥ 0.01f = False（跳过）。NaN（0/0 防御性路径）< 0.01 → 跳过——emit 判据用 `m >= 0.01f` 形态，NaN 天然落 skip 侧 |

### 第三轮（runtime 8.0.29 实测锚点——真实 ToneUpdater.Step）

| # | 场景 | δ | tone′（NE,DA_VTA,DA_SNc,5HT） |
|---|------|---|------------------------------|
| 15 | B1 杂兵（m=5/15） | (0.33333334,0,0,−0.33333334) | (0.3864665, 0.4, 0.5, 0.4513417) |
| 16 | B1 玩家（m=0.1） | (0.1,0,0,−0.1) | (0.32593995, 0.4, 0.5, 0.48540252) |
| 17 | A1（m=1.0） | (0,1,1,0) | (0.3, 0.68929785, 0.71404856, 0.5) |
| 18 | A4（m=1.0） | (0,1,0,0) | (0.3, 0.68929785, 0.5, 0.5) |
| 19 | A5（m=0.5） | (0,0,0,0.5) | (0.3, 0.4, 0.5, 0.57298744) |
| 20 | B2（m=1.0 完全回避） | (0,0,0,1) | (0.3, 0.4, 0.5, 0.6459749) |
| 21 | C1（m=1.0） | (1,0,0,−1) | (0.5593994, 0.4, 0.5, 0.35402513) |
| 22 | D2（m=1.0） | (0,1,0,1) | (0.3, 0.68929785, 0.5, 0.6459749) |
| 23 | B4（m=2/60） | (0.033333335,0,0,−0.033333335) | (0.30864665, 0.4, 0.5, 0.49513417) |
| 24 | B1×2 叠加（非 baseline 输入） | 同 #15 两次 | t1=(0.3864665,0.4,0.5,0.4513417) → t2=(0.39816847,0.4,0.5,0.42635968) |
| 25 | A4 穿透放大（m=2.6/2.0=1.3） | (0,1.3,0,0) | (0.3, 0.77608716, 0.5, 0.5) |

锚点生成：/tmp/eventsprobe 引用 core 项目实测（2026-08-13）；tone 基线 (0.3,0.4,0.5,0.5)，Δ=1.0，τ=(0.5,0.3,0.8,1.5)，δ_scale=0.3（ToneUpdater 内部）。

## 追问

### Q1: C1 guard 实现位置（StatusChangeEvent 是否扩展）

C1 guard = `ΔSAN<0 且 old≥30% 且 new<30%`。StatusChangeEvent 现有字段仅 Kind+Entered（types spec §二 2.6 实测确认）——处理器无法判别 SAN 前后值。

- **A（推荐）**：扩展 StatusChangeEvent + 3 个 float 字段（SanBefore/SanAfter/SanMax）——L2 类型变更，走八航四位一体模式（types spec 🔧 行 + 重载探针 AC + 现有 types 测试零改动回执）。EventProcessor 完整实现 guard（含「被动 SAN_max 变化不触发」= SanBefore==SanAfter → 不发 C1），plan §4.7 + §十 测试行（「C1 guard（被动 SAN_max 变化不触发）」）字面兑现，处理器级可测。
- **B**：guard 上移 step 10 状态机（只在真实跨越时发 Entered=true，处理器只信事件）——plan §4.7 文本与 §十 测试行需改写，step 9 测试只能覆盖「Entered=true → C1」半截。

**✅ 裁决（2026-08-13 用户）：Q1 = A**——扩展事件 + 处理器实现。

### Q2: A5/B1 互斥（sign-off 结转 #2）

types sign-off 处置表 row 3 已接受「C5 防御生效 → 承受者收 A5（非 B1）」为解释性选择，并标注「step 9 实现时复核」。现给出具体映射：

- **A（推荐）**：三路分区——`Hit ∧ blocked>0` → 承受者只收 A5（m=blocked/incoming）；`Hit ∧ blocked=0` → B1；`¬Hit` → B2（m=blocked/incoming=1.0；incoming=dealt+blocked 契约）。blocked>0 即「防御生效」判别（结转 #1：demo d=0.5 下 incoming>0 时 blocked=incoming×0.5>0 恒成立，判别精确）。
- **B**：双发叠加——Hit∧blocked>0 → B1 + A5 都发（§5.5 表行无互斥声明，字面叠加，Σ 加法）。

**✅ 裁决（2026-08-13 用户）：Q2 = A**——三路分区（sign-off 结转 #2 复核闭合）。

### Q3: A4 expected 忍耐路线（sign-off 结转 #3）

A4 的 expected = 2×(1+motivation) − 忍耐被动。忍耐被动常量值 −1（基础行动设计 §四「忍耐·被动 SAN减免 -1（被动永久）」）未进 CalibrationConfig；demo 忍耐·主动未实装（damage map 范围注）。

- **A（推荐）**：补常量 `EndurancePassivePenalty = 1` [NEW]（CalibrationConfig，int，来源 基础行动设计 §四）；expected = 2×(1+motivation) − EndurancePassivePenalty；主动 −2 待实装时再加。
- **B**：读 ParticipantState.EnduranceActiveCd（CD>0 → 用 2，否则 1）——主动未实装 CD 恒 0，行为等价 A 但多一层未来语义耦合。
- **C**：两常量都补（EnduranceActivePenalty=2 预留）——主动未实装即死常量，违背「不用即不建」。

**✅ 裁决（2026-08-13 用户）：Q3 = A**——补被动常量 1（sign-off 结转 #3 闭合）。

## 决策

| D# | 决策 | 理由 |
|----|------|------|
| D1 | m<0.01 跳过按双通道拆分：δ 通道 emit 判据 `m ≥ 0.01f`（NaN 天然落 skip 侧）；s 通道按 m_α 独立判定（A 类 m_α=1.0 恒发，B/C/D 类 m_α=m 同 δ） | §5.5「m<0.01 跳过 emit」未区分通道；A 类「自身行动感官完整」要求 miss 仍有 s（A2 的 δ=(0,−0,0,0)=0 向量但 s≠0——整事件跳过会丢感官输入，违背 m_α=1.0 的设计理由）。A2 miss：δ 不发、s 发 |
| D2 | δ 聚合：每参与者 Σδ（本窗口全部事件）后恰好一次 ToneUpdater.Step；Σδ 全零 → 不调用 | csharp-tone spec §三「Σ 聚合由 step 9 负责」；Step 只对事件方调用，零向量调用无意义 |
| D3 | D1/D2 广播：HP≤0 结算完成后即时 emit 到所有在场且 HP>0 的角色（被击倒者不接收）；teams 输入 int[]（同值=队友）：teams[p]==teams[downed] → D1 否则 D2 | plan §4.7 字面 + §5.5 D 注；多倒下者各自广播，Σ 聚合 |
| D4 | A4 expected 公式：expected = 2×(1+motivation) − 忍耐被动（Q3 裁决）；actual = SanDamage（含 gate/穿透的结算产物） | m=actual/expected 语义；expected 用基础公式、actual 用结算产物（与 A1 ExpectedDamage=4 口径一致） |
| D5 | HealEvent / LinkGrowthEvent：无 δ/s 发射（no-op，文档化） | §5.5 无对应行；demo 未用 |
| D6 | 索引校验：ActorId/TargetId ∉ [0, states.Count) → ArgumentException | 防御性契约（步 10 接线前测试独立运行） |
| D7 | 输出：EventProcessingResult（States：输入副本 + Tone 注入；SensoryAccum：每参与者 float[69] s 增量） | 纯函数；调用方（step 10）累积 s |
| D8 | A5/B1/B2 三路分区：Hit∧blocked>0 → A5；Hit∧blocked=0 → B1；¬Hit → B2（m=1.0） | Q2=A（用户 2026-08-13）；types sign-off row 3 + 结转 #2 复核闭合 |
| D9 | StatusChangeEvent + SanBefore/SanAfter/SanMax 3 float 字段；C1 guard 在 EventProcessor（含 SanBefore==SanAfter → 不触发） | Q1=A（用户 2026-08-13）；L2 类型变更走八航四位一体模式 |
| D10 | CalibrationConfig.EndurancePassivePenalty = 1 [NEW]；expected = 2×(1+motivation) − 1 | Q3=A（用户 2026-08-13）；结转 #3 闭合 |

## 产出

- [ ] spec.md v1.0
- [ ] spec.md 通过审计（workflow 多专家）
- [ ] sign-off.md 获批

## Comments

- 2026-08-13：创建。上游 csharp-damage 闭合 ✅（178/178，0 spec 缺陷，八航）。数据实测三轮完成（设计级 6 条 + m 数值 8 条 + runtime 锚点 11 条）。
- 2026-08-13：追问 Q1-Q3 提交用户裁决（AskUserQuestion）。

---
*创建: 2026-08-13 | 更新: 2026-08-13*
*关联: [plan §4.7](../../../csharp-engine/design/plan.md)*

---
*导出: 2026-09-12 | 来源: GitHub issue*
