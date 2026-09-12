# #58 任务issue 01: 速度排序规格（SpeedScoreCalculator + TurnOrderBuilder）

> 状态：开放 · 创建 2026-08-13
> 标签：维度:管线, ready-for-agent
> 原始：https://github.com/verystrongdog/game/issues/58

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

本地: .scratch/csharp-speed/design/issues/01-speed-spec.md

## 问题（这件事要解决什么）

csharp-engine plan §十一 step 7 = **SpeedScoreCalculator + TurnOrderBuilder**——三成分速度排序（回合战斗流程 §3.1：速度 = 察觉分×w₁ + 决断分×w₂ + 执行分×w₃）+ 同速掷硬币破平（§3.4）。

没有它：Phase 3 速度重算（运行时状态模型 §7.1「Phase 2-3: 继承 + 速度重算，a(t) 贡献察觉分/决断分/执行分」）无引擎实现，step 8（基础行动结算，gate_bonus 需要行动顺序）被阻塞。step 6 已交付的 CstcGating 正是决断分（mean(c_loop)）与执行分（a_SD1）的数据源——本 feature 把它们与 WC 激活 a(t) 合成为行动顺序。

本 issue 产出 SpeedScoreCalculator + TurnOrderBuilder 的精确实现规格，并裁决**三个设计疑问**（§3.2 内部矛盾、§3.3 回落粒度、plan §十三-4 Putamen 代理）。

## 目标

- spec.md v1.0（§一~§七 + 变更日志），通过 workflow 审计 + 用户 sign-off
- 覆盖 plan §4.5 全部内容 + plan §十 SpeedScore 测试行（3 RED 用例）
- 三个设计疑问经用户裁决后固化为偏差声明 / 设计文档修正项

## 指标

- spec 中全部数值断言（4 察觉节点行索引、静息锚点、a_SD1 静息值、首回合 speed、破平确定性）经 python 实测验证
- 审计 0 阻塞项；AC 全部可测

## 工作方式

二层流水线：任务issue → 数据实测 + Q 裁决 → spec v1.0 → workflow 多专家审计 → sign-off → 工作issue → 实现 → 证据式自审 → feature 闭合（含设计文档修正写回）。

## 范围

- **覆盖**：`SpeedComponents`/`SpeedWeights` 两个 record（SpeedComponents.cs 占位文件从零实现）+ `SpeedScoreCalculator`（察觉/决断/执行三分量提取 + 回落 + 加权合成）+ `TurnOrderBuilder.BuildOrder(float[] scores, IRng rng) → int[]`（排序 + 破平）
- **不覆盖**：权重偏移逻辑（§3.1 偏移表 5 来源——plan §4.5 公式块无偏移项，demo 用默认等权；偏移属 step 10 编排/后续 feature）、等待（§3.5——行动窗口机制，step 10）、Phase 编排（step 9-11）、NPC salience 竞争（step 12）
- **输入**：csharp-data-layer ✅（GameData/FunctionProfile）、csharp-wmatrix ✅（canonical 69 行序契约）、csharp-wc-dynamics ✅（WcState.A）、csharp-tone ✅（M1 实测值表）、csharp-cstc ✅（GurneyState——执行分 a_SD1_somatic 数据源）、csharp-engine-types ✅（CalibrationConfig 已有 SpeedW1/2/3 = 1/3、M1SustainPenalty = −0.1、PerceptionThreshold = 0.15；IRng；ParticipantState.IsDefending）

## 数据实测（2026-08-13，本 issue 第一轮，python 可复算）

| # | 断言 | 实测值 |
|---|------|--------|
| 1 | 4 察觉 fid 名存在性 + canonical 行索引（W_sensory rows 文件序 69 键） | Pericalcarine=41、TransverseTemporal=66、Insula=23、AnteriorCingulateCortex=3；全部 ∈ cortical_nodes_with_sensory_input（37 成员）✓ |
| 2 | 察觉静息 mean（M1 实测值表，csharp-tone 01-tone.md 附录） | (0.6309757+0.6316023+0.6327866+0.6751733)/4 = **0.64263445**（f32） |
| 3 | 决断静息 mean(c_loop)（csharp-cstc AC-6 锚点） | (0.665469+0.696963+0.692102)/3 = **0.68484467**（f32） |
| 4 | 🔑 **a_SD1_somatic 静息候选对比**：一步输出（prev=0, c=0.665469, DA=0.48）vs 300 回合固定点 | 两者**逐位相等 = 0.98489410**（SD1 纯前馈：u_SD1 = c·(1+DA) 只依赖 c/DA，e^(−25)≈0 → a≡u 与迭代无关）→「a_SD1 静息定义」问题自动消解（无 Q 需要） |
| 5 | 执行静息 mean(a(Precentral), a_SD1) | (0.6306536+0.9848941)/2 = **0.80777383**（f32；M1 惩罚 0 未防御） |
| 6 | 首回合 speed 变体 A（§3.2 表「静息值」为准） | w 等权：(0.64263445+0.68484467+0.80777383)/3 = **0.71175098** |
| 7 | 首回合 speed 变体 B（§3.2 残留注「所有 a(0)=0.10」直用） | ≈ **0.1077**（察觉 0.10 / 决断 c_loop(1)≈0.0995 / 执行 mean(0.0995, 0.147)≈0.123）——全员同初始化 → 全平局 → **序数结果与 A 相同**，差异仅在数值显示与文档连贯性 |
| 8 | 回落粒度对比示例（察觉节点 0.7/0.7/0.7/0.05，阈值 0.15） | 逐节点回落 = **0.6937933** vs 成分级（mean=0.5375 ≥ 0.15 → 不回落）= 0.5375——语义差异显著，见 Q2 |
| 9 | RED 用例算术（plan §4.5，2026-08-06 已定） | 等权 (0.5,0.5,0.5)→0.5 ✓；w(0.5,0.25,0.25)·(0.5,0.4,0.4) = 0.25+0.10+0.10 = 0.45（f32 实测 0.44999999）✓；(1,1,1)→1.0 ✓ |

注：fid 名大小写（Pericalcarine vs pericalcarine）与 dk/fid 命名陷阱同源（wmatrix 结转 #1 教训）——本 feature 测试锚点统一走行序解析（RowOf），不裸写下标。

## 追问

### Q1: §3.2 首回合语义矛盾（表 vs 残留注）

回合战斗流程 §3.2 首回合表：察觉/决断/执行三分量来源均为「**静息值**」（4 节点静息值 / c_loop 静息值 / a(Precentral)+a(Putamen) 静息值），但同段末行「所有 a(0) = 0.10，c_loop(0) = 0.10」与表直接矛盾。Phase 3 图「首次回合：初始化值 a(0)=0.10（§3.2）」同源含混。

**✅ 裁决（2026-08-13）：A——首回合 = 静息值，删残留注**。§3.2 表是主体；§3.3 回落规则（0.10 < 0.15 → 静息）使 0.10 语义自我作废；§7.3「Gurney 从静息开始快速收敛稳态」与静息值自洽（a_SD1 首回合 = 0.9849，实测 #4）。残留注删除 + Phase 3 图行修正（设计文档写回）。

### Q2: §3.3 察觉回落粒度（逐节点 vs 成分级）

§3.3 察觉分「低于『未显著激活』阈值时回落至静息不动点——实测 ∈ [0.535, 0.771]」。回落作用于 4 个察觉节点各自，还是作用于察觉分（mean）整体？

**✅ 裁决（2026-08-13）：A——逐节点回落**。每节点 a(t) < 0.15 → 用该节点 M1 静息值（4 个常量入引擎，实测 #2 各值）。文档区间 [0.535, 0.771] 是逐节点静息值域；「抑制某一路感官不拖垮整体察觉」符合 §3.1 三成分模型意图。成分级回落因 3 个正常节点稀释永不触发（实测 #8），规则失能。

注：回落只作用于察觉分（§3.3 原文仅察觉分行有此注）；决断分/执行分无回落（c_loop≈0 即决断慢，与 csharp-cstc「c=0 → gate 0.843 门控抑制」设计一致）。

### Q3: 执行分 Putamen 代理（plan §十三-4，升级为用户决策点）

Putamen 是 CSTC 节点（无 WC a(t)）。plan §十三-4：计划用 somatic 环路 Gurney a_SD1 作代理（[NEW] 映射，§4.5）。

**✅ 裁决（2026-08-13）：A——a_SD1_somatic**。SD1 = 壳核直接通路（D1 MSN）的 Gurney 化身——结构同构映射，非任意代理；「DA 高 → a_SD1 高 → 执行快」符合运动发起神经科学（§3.1 执行分定义）。实测 #4：静息值 0.9849 明确无歧义。B 语义矛盾（a_SD2 是「抑制执行」信号，加进执行分方向反了）；C 丢弃 CSTC 层贡献且需改 §3.3 删除 Putamen 项。

## 判断与取舍（草案，Q 裁决后定稿）

| D# | 决策（草案） | 依据 |
|----|------------|------|
| D1 | SpeedComponents 三字段 = 察觉/决断/执行（float，均已回落/惩罚后）；SpeedWeights = w1/w2/w3（CalibrationConfig.SpeedW1/2/3，默认 1/3） | plan §4.5 公式块；回合战斗流程 §3.1 |
| D2 | 察觉 = mean(4 节点 a)；决断 = mean(c_loop 3 环路)；执行 = mean(a(Precentral), a_SD1_somatic) + M1 惩罚——**分量归一化 mean**（文档为求和形态） | plan §十二-8 偏差；实测 #2/#3/#5 |
| D3 | 察觉回落：逐节点（Q2 裁决）；阈值 PerceptionThreshold = 0.15（CalibrationConfig 已有）；回落目标 = 该节点 M1 静息值（4 个引擎私有常量，来源注释 = csharp-tone M1 实测表） | §3.3；实测 #8 |
| D4 | 决断分/执行分无回落（§3.3 原文回落注仅察觉分行） | §3.3 原文；csharp-cstc c=0 门控语义 |
| D5 | M1 惩罚：IsDefending == true → 执行分 += M1SustainPenalty（−0.1，CalibrationConfig 已有）；触发位 = ParticipantState.IsDefending | §3.3「M1 是否被持续占用惩罚」；防御持续 = 战斗界面/回合流程既有机制 |
| D6 | 首回合语义（Q1=A）→ spec 固化 + 设计文档写回（§3.2 残留注 / Phase 3 图行） | 实测 #6/#7；Q1=A |
| D7 | Putamen 代理（Q3=A）→ spec 固化 + plan §十三-4 由待决转已决 | plan §十三-4；Q3=A |
| D8 | 行序 = canonical 69（Wsensory.RegionIds 契约）；4 察觉 fid→行号解析镜像 WMatrixBuilder Step 1-2 | csharp-wmatrix 行序契约复用 |
| D9 | TurnOrderBuilder.BuildOrder：排序（分数降序）+ 同速组内掷硬币破平（每回合重新破平，IRng.NextFloat()）；输出 = 参与者索引数组（0 = 最快）。**排序稳定策略 + 破平算法写死**（确定性测试：固定 RNG） | §3.4；plan §十 测试行「破平 coin flip 固定 RNG 确定性」 |
| D10 | 权重偏移逻辑（§3.1 偏移表）不覆盖——本 feature 用默认等权；偏移属后续 feature（demo 不需要） | plan §4.5 公式块无偏移项（范围声明） |
| D11 | plan §4.5 行「未显著激活回静息基线 0.10」已过时——§3.3 于 2026-08-13 M1 写回更新为「回落至静息不动点」（0.10 仅初始化值）→ 设计文档写回时同步 plan 该行 | 回合战斗流程.md 更新日志（2026-08-13）；§3.3 原文 |
| D12 | 运行时状态模型 §8.1 输出映射表（察觉/决断/执行分公式与 §3.2/§3.3 冲突，plan §十二-6 已裁定按 §3.3 实现）→ 设计文档写回：§8.1 改为指针式引用 §3.2/§3.3 现行公式 | plan §十二-6 |

## 产出

- [x] 数据实测第一轮（本 issue，已完成——见上表）
- [x] Q1/Q2/Q3 用户裁决（Q1=A / Q2=A / Q3=A）
- [ ] 设计文档修正写回（Q1/Q3 决议关联：回合战斗流程 §3.2/Phase 3 图、plan §4.5/§十三-4、运行时状态模型 §8.1——D6/D7/D11/D12）
- [ ] spec.md v1.0（§一~§七 + 变更日志 + 参数速查表；AC + 偏差 B）
- [ ] workflow 多专家审计 → report.md
- [ ] 人类复核 → sign-off.md
- [ ] 工作issue 01 → 实现 + 证据式自审
- [ ] map.md 更新 + 回顾段（feature 闭合）

## Comments

- 2026-08-13：创建。数据实测第一轮完成（4 察觉节点存在性/静息锚点/🔑a_SD1 一步==300回合逐位相等/首回合 speed 两变体/回落粒度对比/RED 算术）。三个疑问提交用户裁决（Q1 首回合语义、Q2 回落粒度、Q3 Putamen 代理）。
- 2026-08-13：裁决完成（Q1=A 静息值 / Q2=A 逐节点回落 / Q3=A a_SD1_somatic）。Q3 用户要求详细说明后裁决——SD1 = 壳核直接通路的 Gurney 结构同构映射。进入设计文档修正写回 + spec v1.0。

---
*导出: 2026-09-12 | 来源: GitHub issue*
