# map: csharp-engine

> C# 战斗引擎总计划——审计修订版 plan.md 为 umbrella，每个实施 step 一个 feature 走二层流水线。Status: open

## Notes

- 2026-08-12 四专家 workflow 审计原计划（结论：有条件放行）→ step 0 计划修订（本 feature 的 00 号任务issue）→ step 2-12 各拆 feature
- 审计 10 项关键修复全部吸收进 [plan.md](design/plan.md)：解析解数值、ParticipantState HP/SAN、双通道声明结构、IsDefending、δ 实时注入、3 行动 NPC 候选集、CD 窗口起点 tick、W 数据绑定、命名空间分层、gate→结算接线
- 设计文档内部冲突（决断分公式、tone 基线范围）记录在 plan §十三待决清单，不阻塞编码

## Decisions-so-far

- [任务issue 00](design/issues/00-plan-revision.md) → 3 决策（D1-D3）
- [plan.md v1.0](design/plan.md) → 审计修订版实施计划

## Fog

- plan §十三 7 项待决（含 §6.3 W_SEL_GPe 权重缺失——需文档补值）
- step 2-12 feature 尚未创建
- δ_scale=0.3、M1 占用惩罚等 [NEW] 占位待校准
