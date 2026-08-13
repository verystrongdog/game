# map: csharp-engine-types

> csharp-engine step 2（plan §十一）——Types/ 共享状态类型 + CombatContext 依赖项。Status: closed（2026-08-13 工作issue 01 resolved，AC-1~10 全绿）

## Notes

- 依赖 csharp-engine plan v1.1（sign-off 2026-08-13 获批）§三 状态类型总表
- 11 种类型 = step 3-9 全部引擎模块的输入输出契约；SpeedWeights/SpeedComponents 归 step 7（plan §4.5）
- CombatContext 三个依赖项（IRng/GameData/CalibrationConfig）不在 §三 表内——本 feature 一并定义
- **审计拦截的关键错误（v1.0）**：行序恒等式「= Regions 顺序」与实测矛盾——两 JSON 69 key 集合相同、顺序第 0 位即不同；canonical 唯一 = WsensoryMatrix.RegionIds
- 实现阶段 0 spec 缺陷（审计全拦截）；发现 2 项仓库卫生问题（.gitignore / 未提交文件）已处置

## Decisions-so-far

- [任务issue 01](design/issues/01-types-spec.md) → 4 决策（D1-D4）+ 4 取舍记录 → resolved（2026-08-13）
- [spec.md v1.0 → v1.1](design/spec.md) → 审计退回 → 修复 → Δ审计 pass → L1 修正 ×4
- [sign-off](design/audit/sign-off.md) → 批准（2026-08-13）；5 项结转清单随实现验证
- [工作issue 01](impl/issues/01-types-implementation.md) → 20 文件实现 + 26 测试 → 证据式自审 → resolved（2026-08-13）

## Fog

- 结转 #1-3（防御判别取整边界 / A5 归属复核 / A4 忍耐常量 −1+低 SAN 穿透）→ step 9（事件空间）
- 结转 #4（gates=1.0 消费时序覆盖）→ step 6（CSTC）首回合 + step 10（流程）测试
- 结转 #5（W.RowFids == RegionIds 行序对齐断言）→ step 3（wmatrix）WMatrixBuilder 测试

## 总结（2026-08-13 closed）

spec@v1.1 全部落地：15 个 Types 类型 + GameData + LoadAll + 7 测试文件（26 测试），build 0 错误 0 警告，test 50/50。首航验证了审计拦截的有效性（v1.0 行序恒等式凭记忆错误被 3/3 专家命中）；实现零 spec 偏差。下游 8 个 feature 的类型契约就绪。
