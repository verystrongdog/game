# 任务issue 01: Data Layer 完整规格

> Status: resolved | Type: task | 维度: 管线 | GitHub: [#42](https://github.com/verystrongdog/game/issues/42)

## 目标

为 C# Data Layer 产出完整实现规格 spec.md——覆盖**全部已写 + 待写**的数据类型与 GameDataLoader，供审计与实现引用。二层流水线的首航 feature（同时验证流水线本身）。

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
