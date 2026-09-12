# 任务issue 01: csharp-smoke 规格（Smoke 集成测试）

> Status: claimed | Type: task | 维度: 管线 | Blocked by: csharp-console ✅（2026-08-14 闭合） | GitHub: [#68](https://github.com/verystrongdog/game/issues/68)

## 范围

产出 [spec.md](../spec.md) v1.0，覆盖 plan step 12（csharp-smoke = Smoke 集成测试）：

- 端到端完整战斗（引擎级：TurnManager + 双方自动行动）→ 战斗结束（全灭/上限）→ 状态合理性断言
- 确定性（同种子同结果）
- 集成点验证：静息初始化 → 首回合 → 战斗全流程（tone 动态/gate 响应/速度序变化/伤害收敛）
- 跨组件数据流（GameData → WMatrix/CorticalBias → WcDynamics/CstcGating → Speed → Damage/Events → TurnManager）

## 产出

- [ ] spec.md v1.0
- [ ] spec.md 通过审计
- [ ] sign-off.md 获批
- [ ] 实现 + 工作issue 闭合

## Comments

- 2026-08-14：创建。上游 csharp-console 闭合 ✅（284/284，十一航）。12 个引擎任务最后一个。

---
*创建: 2026-08-14*
*关联: [plan §八/§十](../../../../../spec/engine/csharp-engine-roadmap.md)*
