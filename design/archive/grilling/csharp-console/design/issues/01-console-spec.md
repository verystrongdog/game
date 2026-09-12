# 任务issue 01: csharp-console 规格（Console harness）

> Status: claimed | Type: task | 维度: 管线 | Blocked by: csharp-flow ✅（2026-08-14 闭合） | GitHub: [#67](https://github.com/verystrongdog/game/issues/67)

## 范围

产出 [spec.md](../spec.md) v1.0，覆盖 plan §九（step 11 csharp-console = Console harness）：

- `YouAreNotTheFish.Console` 可执行项目（引用 Core）
- 2 参与者 1v1：玩家（HP 50/SAN 80 模板）+ NPC 杂兵（HP 15/SAN 60 模板——CalibrationConfig demo 值）
- 每回合输出（§九 清单）：顺序（speed 分量展开）、a(t) 摘要（sensory/Precentral/Broca 节点）、tones、gates、行动声明、结算详情（damage 逐因子）、SAN 阈值跨越（C1）、事件清单（A1 m=…）、回合末 HP/SAN/CD、结束原因
- 静息 trace 模式（--trace-resting N）——a(t) 不动点测量输出
- 种子 RNG（--seed）可复现
- 玩家 IActionProvider（键盘输入——step 10 接口的玩家实现）
- 不覆盖：NPC AI 全量（step 10 已交付 NpcSalience demo 版）、Unity 呈现

## 数据实测

待 spec 写作期补：Console 项目结构、玩家输入方案、输出格式细节。

## 产出

- [ ] spec.md v1.0
- [ ] spec.md 通过审计（workflow 多专家）
- [ ] sign-off.md 获批

## Comments

- 2026-08-14：创建。上游 csharp-flow 闭合 ✅（261/261，十航）。

---
*创建: 2026-08-14*
*关联: [plan §九](../../../../../spec/engine/csharp-engine-roadmap.md)*
