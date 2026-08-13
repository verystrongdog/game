# 任务issue 00: 引擎实施计划修订（审计 step 0）

> Status: claimed | Type: task | 维度: 管线 | GitHub: [#44](https://github.com/verystrongdog/game/issues/44)

## 目标

把 2026-08-12 四专家审计（结论"有条件放行"）的 10 项关键修复正式落成 **C# 引擎实施计划文档 plan.md**（此前只存在于 memory digest）。该计划是后续 step 2-12 每个实施 feature 的引用基线（umbrella 计划）。

## 指标

- 10 项关键修复逐条**真实吸收**（再审计专家 A 逐条验证：落实为公式/字段/管线步骤，而非口头提及）——F1-F10 全部 ✅
- 6 项放行条件全部覆盖（范围表 / 偏差声明 / [NEW] 标注 / 实测吸引子验证 / 再审计 / 解析解先例）
- 再审计 3 专家 verdict 无 reject，发现项 **0 未处置**
- sign-off 获批 → plan v1.1 成为引用基线

## 工作方式

1. **引用即读取地基**：完整 Read 6 份权威设计文档（运行时状态模型 / 回合战斗流程 / 核心机制 / 皮层动力学-通用层 / NPC AI / 基础行动设计）+ 框架 memory + 审计原始输出 + 原计划全文（从会话 transcript 恢复，原文件已被覆盖）
2. **再审计**：workflow 3 专家并行（修复吸收 / 公式一致性 / 架构分层），结构化输出 verdict + findings，人工综合成 report.md Trace Table
3. **发现逐条核实**：审计引用的文档矛盾逐条 grep 源文档验证（如回合战斗流程 §9.1 原文核实）

## 判断与取舍

- **T_base = 0.15 不采纳审计临时建议 1.0**——NPC AI §3.4 是正典值，审计建议只是临时占位（plan §4.8）
- **v1.0 §十二-4 虚构了文档矛盾**（回合战斗流程 §9.1 实际一致）——公式专家拦截，v1.1 改为"原计划 Phase 2 递减错误"修正记录
- **速度分量求和→均值**：文档求和形态下察觉实际权重 4×，取均值使等权 1/3 语义成立——显式声明为 §十二-8 偏差 + [NEW]
- **文档内部冲突不阻塞编码**（决断分公式、tone 基线范围）——进 §十三待决清单升级为用户决策点
- **类型缺口当场补齐**（事件类型/LoopSalience/s_pending/方法签名）——这是接口漂移风险，不做结转

## 范围

2026-08-12 四专家 workflow 审计（结论：有条件放行）的第 0 步交付物：把审计的 10 项关键修复正式落成一份 C# 引擎实施计划文档（此前仅存在于 memory digest），后续每个实施 feature 引用它。

产出：
- [x] design/plan.md v1.0（审计修订版）——10 修复 + 13 改进 + 6 条件 + 范围表 + 偏差声明 + 待决清单 + 修订实施序
- [x] plan.md 通过 workflow 再审计（审计条件 2：3 专家 conditional → v1.1 修正全部处置）
- [ ] sign-off.md 获批（待用户复核）

## 追问

### Q1: 计划文档 vs spec 文档的关系
plan.md 是 umbrella 计划（跨 feature），不走 spec.md 机制；每个实施 step（§十一 表）各自成为 feature，走完整二层流水线。plan.md 的再审计沿用 workflow 审计 + sign-off 审批格式。

### Q2: 审计建议 T_base=1.0 临时值怎么处理
不采纳——NPC AI 行为模型 §3.4 正典值 T_base = 0.15，文档优先（记录于 plan §4.8）。

## 决策

| D# | 决策 | 理由 |
|----|------|------|
| D1 | plan.md 落 `.scratch/csharp-engine/design/plan.md` 作为 umbrella | 每个实施 step 一个 feature，spec 引用 plan 章节 |
| D2 | 文档冲突（决断分/tone 基线范围）不阻塞编码，进 §十三待决清单升级用户决策 | 用户选择"自己编码并逐步发现修复"路径 |
| D3 | 再审计范围 = 10 修复吸收验证 + 公式一致性 + 架构分层 | 审计条件 2 |

## 产出

- [x] plan.md v1.0 → v1.1
- [x] workflow 再审计报告（audit/report.md）
- [ ] sign-off.md

## Comments

### 2026-08-13 再审计结果与 v1.1 修正

- 3 专家（修复吸收/公式一致性/架构分层）全部 conditional；10 修复全部真实吸收 ✅
- 关键发现：§十二-4 虚构文档矛盾（回合战斗流程 §9.1 实际一致）、事件类型/LoopSalience/方法签名缺失、速度分量求和→均值未声明——v1.1 全部修正
- 详见 [audit/report.md](../audit/report.md)
