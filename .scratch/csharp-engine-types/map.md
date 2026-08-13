# map: csharp-engine-types

> csharp-engine step 2（plan §十一）——Types/ 共享状态类型 + CombatContext 依赖项。Status: open

## Notes

- 依赖 csharp-engine plan v1.1（sign-off 2026-08-13 获批）§三 状态类型总表
- 11 种类型 = step 3-9 全部引擎模块的输入输出契约；SpeedWeights/SpeedComponents 归 step 7（plan §4.5）
- CombatContext 三个依赖项（IRng/GameData/CalibrationConfig）不在 §三 表内——本 feature 一并定义

## Decisions-so-far

- [任务issue 01](design/issues/01-types-spec.md) → 4 决策（D1-D4）

## Fog

- 事件类型字段是 spec 设计决策（框架 memory 只给 4 个名字无字段）——审计重点
- CalibrationConfig instance 化是对 plan §七 字面（static class）的偏差——sign-off 决策点
- §5.5 事件派生映射表在 spec §五 列出，step 9（csharp-events）消费
