# 任务issue 01: Data Layer 完整规格

> Status: resolved | Type: task | 维度: 管线 | GitHub: [#42](https://github.com/verystrongdog/game/issues/42)

## 问题（这件事要解决什么）

Data Layer 是引擎的地基——所有 JSON 设计数据（脑区注册表 / 三体网络 / W_sensory 矩阵 / 情境原型 / 信号词表）要经它进入运行时，后续每个引擎 step 都站在它上面。但地基当时是裸奔的：已有代码从未被系统核查过，三个新 JSON 尚无 C# 类型。若规格写错（如 snake_case 映射缺失），错误会**静默扩散**到整个引擎——数据全丢而测试全绿。同时这是二层流水线的首航 feature，流水线本身也要借它验证。

## 目标

为 C# Data Layer 产出完整实现规格 spec.md——覆盖**全部已写 + 待写**的数据类型与 GameDataLoader，供审计与实现引用。

## 指标

- spec 覆盖 13 enum + 18 record + 5 loader 方法
- 14 条验收标准（AC-1~14）全部定义
- 审计 v1.0 的 6 个 Error 全部修复，Δ审计无新 Error
- sign-off 获批（5 项结转清单进入实现）
- 实现端：24/24 测试绿（工作issue 01）

## 工作方式

- **逐字段读 JSON 写 spec**——首航教训：v1.0 的 E1/E3 本质是"凭设计文档记忆写 spec"而非"读 JSON 写 spec"
- v1.0 全量审计（workflow 多专家）→ 退回修改 → v1.1 → Δ审计（只重审变更章节 + 半径扩张复查）→ v1.2
- 审计发现数据文件问题时分两类：执行已有决策的补漏（走一致性清扫通道）vs 需要新决策（升级为用户决策点，不擅自改数据）
- 数据修复（situation_primitives.json 悬挂引用 + primary_networks 注册表失配）在用户确认后**先行于** spec 修复

## 判断与取舍

- **存量代码不豁免**——纳入 spec 通过一致性核查而非重写（D1）
- **term_registry.json 不入 Data Layer**——设计期参考，非运行时数据（D2）
- **W_sensory 加载为 69×6 int 矩阵 + RegionIds 派生填充**——行序用 Rows.Keys 顺序 pin 住
- **31 个情境原型中 27 个有效**（4 个已废弃）（D4）
- **"有意不映射"清单**——把 System.Text.Json 的静默忽略变成显式决策

## 审计明细（v1.0 全量审计 → v1.2 补修）

**v1.0 退回修改：6 Error（全部真实，无一误报）**

| # | 缺口 | 影响 |
|----|------|------|
| E1 | §2.2 全部代码块缺 `[JsonPropertyName]`（18 字段失配）——根因：`PropertyNameCaseInsensitive` 只忽略大小写**不忽略下划线**，snake_case 字段静默反序列化为默认值，不抛错、数据全丢 | 静默数据全丢；AC-3/AC-5 必挂 |
| E2 | `Matrix` 声明 `bool[][]` ← JSON 实际 int 0/1（.NET 8 实测反序列化抛 JsonException） | AC-1 必挂 |
| E3 | signal_types 词表过时（19→18，10 个 subtype 名不存在）——spec 引用 Grilling #26 时代旧词表，数据文件已更新 | AC-5 必挂；实现者按 spec 造数据会污染词表 |
| E4 | RdocProfile 3 域 vs 数据 6 域（缺 positive_valence/arousal_regulatory/sensorimotor） | 静默丢 3 域数据 |
| E5 | AC-4 数据悬挂：3 个 region 引用无对应脑区（ReflexEscape/SeptalRegion/Habenula） | AC-4 必失败；根源在设计层数据文件，非 spec |
| E6 | agency/valence 值域文档错误（"environment"→实际 `circumstance`；"neutral"→实际 `ambiguous`） | 按 spec 写校验会误报 |

**10 Warning（进处置，非阻断）**：W1 RegionIds 填充方案无 AC、W2 SignalSubtype 异构字段静默丢弃、W3 三体边 `type`/`_` 前缀 key 未声明不映射、W4 W_sensory 3 个未建模顶层 key、W5 约束 2 验证太弱（只查行数不查行序）、W6 约束 2/4/5 + 异常分支无 AC、W7 AC-6 不可自动化、W8 遗漏约束需设计决策、W9 §七自检清单与新类型脱节、W10 无下划线字段靠 case-insensitive 碰巧匹配。

**v1.1 Δ审计：三路独立实测**——41 个 `[JsonPropertyName]` 逐字段吻合、69×6 int 矩阵、18 子类词表、RdocProfile 6 域、0 悬挂引用；11 条约束 11/11 通过（C1 69/69 双向双射、C2 逐行逐模态 0 mismatch、C3 201 引用 0 悬挂、C5 588/588 ∈ 词表、C9 1049 条边 0 坏引用、C10 88 引用 0 失配）。发现 2 个 AC 覆盖缺口：E-Δ1 mirror_of 无 AC、E-Δ2 1049 三体边（最大引用面）无 AC——v1.0 核心问题只修了一半，被 Δ审计拦截 → v1.2 补 AC-13/AC-14。

**无审计会怎样**：3 个 AC（1/3/5）按 spec 原样实现必失败，且失败原因是 spec 自身错误；18 处映射失配导致"测试全绿但数据全丢"的假阳性代码。

## 范围

产出 spec.md 覆盖 C# Data Layer 的全部类型和加载器：
- 已写代码（BrainRegion / TripartiteModel / enums / loader）纳入一致性核查
- 待加载 JSON（W_sensory / situation_primitives / signal_types）定义新类型
- 跨文件引用完整性约束
- GameDataLoader 完整接口

## 追问

### Q1: 存量代码怎么处理
全部纳入 spec——通过一致性核查（不重写，核对字段/类型/测试是否与 JSON 一致），发现问题记录为 spec 修正。

### Q2: term_registry.json 是否需要 C# 加载
term_registry.json 是术语参考，不是运行时数据——暂不纳入 C# Data Layer。

## 决策

| D# | 决策 | 理由 |
|----|------|------|
| D1 | spec 覆盖全部 Data Layer 代码（已写 + 待写） | 审计建议：存量代码不豁免，一致性核查即可 |
| D2 | term_registry.json 不入 C# Data Layer | 纯设计期参考，非运行时数据 |
| D3 | W_sensory 加载为 69×6 bool 矩阵 + 6 模态标签 | 设计文档规定的格式 |
| D4 | situation_primitives 加载为 27 情境原型 + 查找字典 | 31 情境原型中 27 个有效（4 个已废弃） |

## 产出

- [x] spec.md v1.0 → v1.2（v1.0 审计退回：E1-E6，v1.1 Δ审计有条件通过，v1.2 补修）
- [x] spec.md v1.2 通过 Δ审计
- [x] sign-off.md 获批（2026-08-12）
- [x] 工作issue 01 实现 + 自审闭合（GitHub #43）

## Comments

### 2026-08-12 审计 v1.0 结果与修复

- v1.0 审计结论：退回修改（6 Error + 10 Warning）——E1 [JsonPropertyName] 全面缺失、E2 bool→int、E3 词表过时（19→18）、E4 RdocProfile 6 域、E5 悬挂引用、E6 agency/valence 值域
- 数据修复（commit 0063ae9 + d3eee7d）：situation_primitives.json 悬挂引用清扫（#25 D1/D3 补执行）+ primary_networks 注册表对齐（16 处）
- spec v1.1 已产出，Δ审计进行中

### 2026-08-13 收尾简要（closed）

- **目标达成**：spec v1.2 获批，Data Layer 完整规格成为实现基线
- **指标**：13 enum + 18 record + 5 loader 方法全覆盖、14 AC 定义、审计 Error 0 残留、实现端 24/24 绿
- **审计拦截价值**：6 个 Error 全部真实（3 个"按 spec 实现必失败"、2 个静默数据丢失、1 个数据悬挂）——无审计直接实现会产出"测试全绿但数据全丢"的假阳性代码
- **遗留**：sign-off 5 项结转已全部在工作issue 01 回填
