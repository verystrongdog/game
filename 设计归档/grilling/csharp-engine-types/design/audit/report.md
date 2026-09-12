# 审计报告: 引擎共享状态类型 spec

> 审计日期: 2026-08-13 | 审计方法: workflow 3 专家 agent（类型完整性 / 字段来源核实 / 架构与接口契约）| spec 版本: v1.0 | 审计结论: **退回修改**

## 审计概要

三专家独立审计 spec v1.0，结论：类型完整性 conditional、字段来源核实 **reject**、架构与接口契约 **reject**。

**核心发现（3/3 专家独立命中同一个 ❌）**：spec §五 C1 / §二 2.1 / §六 AC-10 断言「WcState.A 行序 = BrainRegionsData.Regions 顺序 = WsensoryMatrix.RegionIds」与实测数据矛盾——`brain_regions.json` 与 `W_sensory.json` 的 key 序第 0 位即不同（TransverseTemporal vs AccumbensCore，69 集合相同顺序不同）。plan §三 的 canonical 定义只有「与 W_sensory 行序一致」，spec 多写的 Regions 顺序等式是错误引用。按现文实现：AC-10 测试必失败（step 2 门禁不过），且实现者按 Regions 序填充 A 会与 W·a 静默错位。

## Trace Table

| # | spec 位置 | 检查项 | 输入 | 判定 | 详情 |
|---|----------|--------|------|------|------|
| 1 | §五 C1 / §二 2.1 / §六 AC-10 | 行序恒等式「= Regions 顺序 = RegionIds」 | 实测 brain_regions.json vs W_sensory.json key 序 | ❌ | 3/3 专家命中。两 JSON 69 集合相同、顺序不同、首处分歧位置 0。数据层 AC-2（集合双射）/AC-8（matrix 内部一致）均不支撑顺序相等。plan §三 原文只定义 W_sensory 序 |
| 2 | §三 3.3 / §二 2.7 / AC-7 | GameData 聚合字段结构 | spec 全文 vs 消费方签名（plan §4.3） | ⚠️ | 2/2 专家命中。LoadAll 返回类型与 CombatContext.Data 被引用但无字段表——实现者须自行发明接口，正是 C-C 系列审计要消灭的模式 |
| 3 | §二 2.5 / §3.4 / AC-5 | CreateDefault gates 初值 0 | §7.3 原文 + §6.3/§6.4 推导 | ⚠️ | 3/3 专家命中。§7.3 未定义 gate 初值；按公式推导 Gurney=0 → O(0)=0 → gate=1−0=1。gate=0 语义「完全门控抑制」与初始状态矛盾 |
| 4 | §二 2.9 | LoopSalience DA 混合序歧义 | §6.3 文档序 limbic→cognitive→somatic vs 字段序 | ⚠️ | 2/2 专家命中。数值序列 0.8/0.2、0.4/0.6、0.2/0.8 照抄文档序，按位置直配会把 somatic 配成 0.8VTA+0.2SNc（文档实为 0.2VTA+0.8SNc） |
| 5 | §五 C5 第 2 行 | 「防御生效」承受者侧 A5 归属 | §5.5 A5 与 B1 触发条件原文 | ⚠️ | 1/1 专家命中。B1「被物理攻击击中」与 A5「防御成功」在「防御中仍被命中」场景同时成立，§5.5 未定义互斥；两 δ 的 5HT 方向相反（A5 +1 vs B1 −1），选错翻转 tone 响应 |
| 6 | §五 C5 第 3 行 | Hit=false 时 B2 m=0/0 | §5.5「m<0.01 跳过 emit」对 NaN 失效 | ⚠️ | 1/1 专家命中。L0 回避落空时 incoming=0、blocked=0 → m=0/0=NaN 会 emit NaN δ |
| 7 | §三 3.5 / AC-8 | IsValidChannelUsage 空值分支 | m1==null 时按字面实现 NRE | ℹ️ | 1/1 专家命中。broca.Kind==Defend 在 m1==null 时未定义；(null,null) 是否合法未声明，step 10 依赖此契约 |
| 8 | §二 2.11 | DamageEvent 名称不落地 | 框架 memory §3.5 四事件类型字面 | ℹ️ | 1/1 专家命中。拆为 Physical/Mental 两子类但无 DamageEvent 中间层，偏差未显式声明 |
| 9 | §五 C1 | C1 归因「AC-2/AC-8 保证行序」 | 数据层 spec AC-2/AC-8 原文 | ℹ️ | 1/1 专家命中。AC-2 是集合双射非顺序断言；AC-8 是同文件内部比对。归因过度引用 |
| 10 | §二 2.11 MentalDamageEvent | A4 expected 重算缺输入 | plan §4.6 公式（忍耐被动 −1、低 SAN 穿透） | ℹ️ | 1/1 专家命中。event 字段无法唯一重算 expected；忍耐常量未进 CalibrationConfig（plan §七 同样未列） |
| 11 | §四 4.2 | PlayerHp/PlayerSan 来源「取中值」 | 核心机制 §10.1 原文 | ℹ️ | 1/1 专家命中。玩家 50/80 是基线值（±10 角色偏移），非取中值；「取中值」仅对 NPC 轻度病人区间成立 |
| 12 | §三 3.2 | splitmix64 理由「.NET 无内置种子控制」 | .NET Random(seed) 事实 | ℹ️ | 2/2 专家命中。Random(seed) 一直支持种子控制；真实理由是跨版本序列不保证稳定 |
| 13 | §二 2.11 HealEvent | 来源「plan §一 范围无治疗」 | plan §一 覆盖/不覆盖表原文 | ℹ️ | 1/1 专家命中。plan 未明言「无治疗」，系推断；保留理由应为框架 memory §3.5 完整性 |
| 14 | §一 覆盖行 | 漏计 CalibrationConfig + DeterministicRng | 任务issue 范围清单 | ℹ️ | 1/1 专家命中。计数小漏，与 §3.2/§4.2 实际内容不一致 |
| 15 | §二 2.1 | WcState 无身份映射字段 | plan §三 行定义 | ℹ️（建议） | 1/1 专家建议加 Fids string[69] 与 WMatrix.RowFids 同构——已评估，见下「取舍记录」 |

**通过项**（三专家未发现问题的部分）：plan §三 11 类型 100% 覆盖（SpeedWeights 排除正当）；91 浮点构成与 §三 表尾一致；修复 #2/#3 与再审计 C-C2 产物落地；C5 映射表与 §5.5 四张表逐行吻合；CalibrationConfig 与 plan §七 全表逐条一致；D1-D4 决策全部落实；C# record 继承层次可编译；事件字段覆盖 §5.5 全部 m 公式与 §九 console 输出需求；引用章节（回合战斗流程 §2.1/§7.1/§7.2/§9.1、tone baseline、Gurney 5 群体、gate 公式）全部核实无误。

## 缺口汇总

| # | 严重度 | 描述 |
|---|--------|------|
| 1 | ❌ | C1/AC-10 行序恒等式与实测数据矛盾（3/3 专家命中） |
| 2 | ⚠️ | GameData 聚合字段结构未定义（2/2 专家命中） |
| 3 | ⚠️ | gates 初值 0 与 §6.3+§6.4 推导矛盾（3/3 专家命中） |
| 4 | ⚠️ | LoopSalience DA 混合位置序歧义（2/2 专家命中） |
| 5 | ⚠️ | C5 防御生效 A5/B1 归属未声明（1/1 专家命中） |
| 6 | ⚠️ | C5 Hit=false B2 0/0=NaN 边界未定义（1/1 专家命中） |
| 7 | ℹ️ | IsValidChannelUsage 空值分支未定义 |
| 8 | ℹ️ | DamageEvent 类型层级偏差未声明 |
| 9 | ℹ️ | C1 归因过度引用（被 #1 修复吸收） |
| 10 | ℹ️ | A4 expected 重算缺输入注释 |
| 11 | ℹ️ | PlayerHp/PlayerSan 来源表述不准确 |
| 12 | ℹ️ | splitmix64 选择理由不准确 |
| 13 | ℹ️ | HealEvent 来源引用为推断未标注 |
| 14 | ℹ️ | 覆盖行漏计 2 个新文件 |
| 15 | ℹ️ | WcState 身份映射字段建议（已评估，取舍见下） |

## 审计结论

- [ ] 通过（无阻塞项）
- [ ] 有条件通过（⚠️ 项需人类确认）
- [x] **退回修改（❌ 项必须修复）** —— #1 行序恒等式为事实错误（实测数据矛盾 + plan 原文过度引用），按现文实现 AC-10 必失败且存在运行时错位风险

**处置**：spec v1.0 → v1.1 吸收全部 15 项发现（❌ 修复 + ⚠️ 修复/解释声明 + ℹ️ 表述修正），随后 Δ审计（只重审变更章节 + 半径扩张表）。

## 半径扩张

| 修复点 | 受影响消费者 | 复查状态 |
|--------|-------------|---------|
| C1 行序 canonical=RegionIds | §2.1（含实测警示 + 取舍记录）、§2.8 WMatrix 行序契约、§五 C1、AC-10、step 3 WMatrixBuilder、step 9 EventProcessor | Δ审计 |
| gates 初值 → 1.0（推导） | §2.5、§3.4、AC-5、step 6 CstcGating、step 10 CombatState | Δ审计 |
| GameData 字段表（§2.12 新增） | §3.3 LoadAll、§2.7 CombatContext.Data、AC-7、step 3/5 消费方 | Δ审计 |
| DA 混合逐字段公式 | §2.9、step 6 CstcGating | Δ审计 |
| C5 A5 归属解释 + B2 NaN 边界 | step 9 EventProcessor | Δ审计 |
| IsValidChannelUsage 真值表 | §3.5、AC-8、step 10 ActionResolver | Δ审计 |
| 表述修正（DamageEvent 偏差声明、splitmix64、HealEvent、PlayerHp、覆盖行、A4 注释） | 各自所在章节 | Δ审计 |

## 取舍记录（人类 sign-off 关注点）

1. **WcState 不加身份映射字段**（发现 #15）：canonical 序的 fid 身份已由 `WsensoryMatrix.RegionIds`（Data 层）+ `WMatrix.RowFids`（step 3）承担两份；WcState 是每 tick 更新的运行时状态，第三份纯冗余。行序对齐由 C1 规范 + step 3 测试验证。sign-off 时可推翻。
2. **gates 初值取推导值 1.0**（发现 #3 选项 a）：而非「0 占位 + 声明不被消费」（选项 b）。1.0 语义正确（初始全放行），首回合 CstcGating.Step 覆盖。
3. **C5 防御生效 → 承受者收 A5**（发现 #5）：§5.5 未定义互斥，本 spec 取「防御成功」解释（m=blocked/incoming），标注 step 9 实现时复核。
4. **不加 DamageEvent 中间抽象层**（发现 #8）：两子类字段集不同（plan §4.6），中间层无共享字段增量；step 9 若需统一分支再加。

---

## Δ审计（spec v1.1）

> 审计日期: 2026-08-13 | 审计方法: workflow 2 专家（修复充分性 / 半径扩张核查）| 审计范围: v1.1 变更章节 + 半径扩张表（非全量）| 结论: **通过（pass）**

两专家独立核查：15 项发现全部修复到位——❌#1 三处改写逐字核对（实测警示经 python 复核属实：regions[0]=TransverseTemporal vs rows[0]=AccumbensCore，69 集合相同序全不同）；⚠️#2 GameData 5 字段类型名与 Data 层实际 record 声明一致；⚠️#3 gates=1.0 推导链（§7.3 未定义 → §6.3 ramp → §6.4 gate=1−O_GPi）与设计文档吻合；⚠️#4 DA 逐字段值与 §6.3 逐值一致；⚠️#5 A5/B1 声明与 δ pattern 表相符；⚠️#6 B2 NaN 边界与 §5.5「m<0.01 跳过 emit」兼容。半径扩张 8 项消费者侧复查全部通过，未发现修复引入的新 ❌/⚠️。

| Δ# | 发现 | 处置 |
|----|------|------|
| Δ-1 | 变更日志计数「1❌+7⚠️+10ℹ️」与缺口汇总实际（1+5+9=15）不符 | 🔧 L1 修正 |
| Δ-2 | §一 覆盖行「事件 ×5」计数歧义（抽象基类未计） | 🔧 改为 ×6（1 抽象基类 + 5 具体子类） |
| Δ-3 | §2.8「三数据文件 functional_id 序」措辞（graph_nodes 为 51 个 dk_name 小写） | 🔧 措辞精确化 |
| Δ-4 | C5 防御生效判别字段未声明 | 🔧 补判别约定 DamageBlocked>0（step 9 可重定义） |
| Δ-5 | §3.5 不校验通道-动作类型配对（如 broca=PhysicalAttack 可通过） | 保持现状——§2.6 契约已自限「Defend 独占 M1」，demo 3 行动集不会产出跨通道组合；若 step 10 需要则在 step 10 spec 新增规则 |
| Δ-6 | AC-10「复用数据层 fixture」措辞（实际无 fixture 类） | 🔧 改为复用 GameDataLoader.LoadWsensory 加载真实 JSON 取 RegionIds |

4 项 🔧 修正均为 L1 笔误级，已直接修入 spec 变更日志，免重审。

**最终审计结论：通过**（v1.0 全量审计 退回 → v1.1 修复 → Δ审计 pass → L1 修正）——spec v1.1（含 🔧 修正）可进入 sign-off。

---

*创建: 2026-08-13*
*关联: [spec v1.1](../spec.md), [任务issue 01](../issues/01-types-spec.md), [csharp-engine plan v1.1](../../../../../规格/引擎/csharp-engine-roadmap.md)*
