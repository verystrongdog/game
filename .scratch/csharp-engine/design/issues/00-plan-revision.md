# 任务issue 00: 引擎实施计划修订（审计 step 0）

> Status: claimed | Type: task | 维度: 管线 | GitHub: [#44](https://github.com/verystrongdog/game/issues/44)

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
