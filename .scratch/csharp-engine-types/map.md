# map: csharp-engine-types

> csharp-engine step 2（plan §十一）——Types/ 共享状态类型 + CombatContext 依赖项。Status: spec v1.1 已批准（2026-08-13 sign-off），等待创建工作issue

## Notes

- 依赖 csharp-engine plan v1.1（sign-off 2026-08-13 获批）§三 状态类型总表
- 11 种类型 = step 3-9 全部引擎模块的输入输出契约；SpeedWeights/SpeedComponents 归 step 7（plan §4.5）
- CombatContext 三个依赖项（IRng/GameData/CalibrationConfig）不在 §三 表内——本 feature 一并定义
- **审计拦截的关键错误（v1.0）**：行序恒等式「= Regions 顺序」与实测矛盾——两 JSON 69 key 集合相同、顺序第 0 位即不同；canonical 唯一 = WsensoryMatrix.RegionIds

## Decisions-so-far

- [任务issue 01](design/issues/01-types-spec.md) → 4 决策（D1-D4）+ 4 取舍记录 → resolved（2026-08-13）
- [spec.md v1.0 → v1.1](design/spec.md) → 审计退回 → 修复 → Δ审计 pass → L1 修正 ×4
- [sign-off](design/audit/sign-off.md) → 批准（2026-08-13）；5 项结转清单随实现验证

## Fog

- 5 项结转（防御判别取整边界 / A5 归属复核 / A4 忍耐常量 / gates 覆盖时序 / step 3 行序承接）
- 工作issue 尚未创建（文件所有权声明待定）
