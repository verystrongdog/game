# map: csharp-engine

> C# 战斗引擎总计划——审计修订版 plan.md 为 umbrella，每个实施 step 一个 feature 走二层流水线。Status: 计划已批准（2026-08-13 sign-off），等待创建第一个实施 feature

## Notes

- 2026-08-12 四专家 workflow 审计原计划（结论：有条件放行）→ step 0 计划修订（本 feature 的 00 号任务issue）→ step 2-12 各拆 feature
- 审计 10 项关键修复全部吸收进 [plan.md](../../../规格/引擎/csharp-engine-roadmap.md)：解析解数值、ParticipantState HP/SAN、双通道声明结构、IsDefending、δ 实时注入、3 行动 NPC 候选集、CD 窗口起点 tick、W 数据绑定、命名空间分层、gate→结算接线
- 设计文档内部冲突（决断分公式、tone 基线范围）记录在 plan §十三待决清单，不阻塞编码
- 2026-08-13 sign-off 获批——plan v1.1 成为各实施 feature 引用基线；5 项结转清单随实施验证

## Decisions-so-far

- [任务issue 00](design/issues/00-plan-revision.md) → 3 决策（D1-D3）→ resolved（2026-08-13）
- [plan.md v1.0 → v1.1](../../../规格/引擎/csharp-engine-roadmap.md) → 审计修订版实施计划 → 获批
- [sign-off](design/audit/sign-off.md) → 批准（2026-08-13，已读范围: 全表 Trace Table）

## Fog

- plan §十三 7 项待决（含 §6.3 W_SEL_GPe 权重缺失——需文档补值）
- step 2-12 feature 尚未创建（step 1 = 数据类型修正 + 词表断言）
- δ_scale=0.3、M1 占用惩罚等 [NEW] 占位待校准
- 5 项结转（静息吸引子实测 / Euler 文档修订 / W_SEL_GPe 权重表 / [NEW] 校准 / 归一化确认）
