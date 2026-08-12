# 任务issue 01: Data Layer 完整规格

> Status: claimed | Type: task | 维度: 管线 | GitHub: [#42](https://github.com/verystrongdog/game/issues/42)

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

- [x] spec.md v1.0 → v1.1（v1.0 审计退回：E1-E6，见 design/audit/report.md）
- [ ] spec.md v1.1 通过 Δ审计
- [ ] sign-off.md 获批

## Comments

### 2026-08-12 审计 v1.0 结果与修复

- v1.0 审计结论：退回修改（6 Error + 10 Warning）——E1 [JsonPropertyName] 全面缺失、E2 bool→int、E3 词表过时（19→18）、E4 RdocProfile 6 域、E5 悬挂引用、E6 agency/valence 值域
- 数据修复（commit 0063ae9 + d3eee7d）：situation_primitives.json 悬挂引用清扫（#25 D1/D3 补执行）+ primary_networks 注册表对齐（16 处）
- spec v1.1 已产出，Δ审计进行中
