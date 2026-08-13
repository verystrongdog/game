# map: csharp-speed

> csharp-engine step 7（plan §十一）——SpeedScoreCalculator + TurnOrderBuilder：三成分速度排序（察觉/决断/执行）+ 掷硬币破平。Status: claimed（2026-08-13）

## Notes

- 依赖 csharp-engine plan §4.5（方案B：SpeedScoreCalculator 纯数值 + TurnOrderBuilder 排序破平，2026-08-06 D4/D5 已定）+ §十 SpeedScore 测试行（3 RED 用例）+ §十二-6（决断分公式冲突：按 回合战斗流程 §3.3 mean(c_loop) 实现，运行时状态模型 §8.1 为指针）+ §十二-8（分量归一化 mean 偏差）+ §十三-4（Putamen 代理 = a_SD1_somatic，用户决策点）
- 上游交付：csharp-data-layer（GameData/FunctionProfile cstc_* 字段）、csharp-engine-types（SpeedComponents.cs 0 字节占位待实现）、csharp-wmatrix（canonical 69 行序契约）、csharp-wc-dynamics（WcState + M1 链）、csharp-tone（ToneState + M1 实测值表 69 行）、csharp-cstc（GurneyState + CstcGating——决断分 c_loop 与执行分 a_SD1 的数据源）
- 设计文档依据：回合战斗流程 §3.1-3.5（三成分模型/首次回合/后续回合/破平/等待）+ 运行时状态模型 §7.1（Phase 3 执行顺序）、§7.3/§7.3.1（初始化 + M1 静息不动点）、§8.1（输出映射表——与 §3.2/§3.3 冲突，plan §十二-6）
- 关键实测（任务issue 01 数据实测第一轮）：a_SD1 一步输出 == 300 回合固定点（逐位相等 0.9848941，SD1 纯前馈）→ 「a_SD1 静息定义」问题自动消解；首回合静息 speed = 0.7117510

## Decisions-so-far

- [任务issue 01](design/issues/01-speed-spec.md) → 数据实测第一轮 → claimed（2026-08-13）

## Fog

- 任务issue 数据实测 ✓ → Q 裁决 ⏳ → 设计文档写回 ⏳ → spec v1.0 ⏳ → 全量审计 ⏳ → Δ审计（如需）⏳ → sign-off ⏳ → 工作issue 01 实现 + 自审 ⏳ → feature 闭合 ⏳

---
*创建: 2026-08-13 | 更新: 2026-08-13*
*关联: [任务issue 01](design/issues/01-speed-spec.md)*
