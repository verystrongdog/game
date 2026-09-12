# #79 [Grilling] P4b HP↔SAN 互转进引擎 — 兑换逻辑 + 上限追踪

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/79

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #70 路线图 P4b：HP↔SAN 互转（核心机制 §5.3 正典数值完整）落地引擎——兑换动作 + 分段兑换公式 + 单次/单场上限追踪。

## 六维定位

- **维度**: 规则（兑换语义）+ 管线（引擎实现）
- **依赖**: 核心机制 §5.3（正典完整：兑换率/上限/占 M1）+ 引擎 CombatAction/CombatState 现状 + 一位小数结算契约（#33 裁决）
- **承接**: #70 路线图 P4b（范围表未覆盖项）

## 当前状态

- 正典（核心机制 §5.3）：
  - HP→SAN: 前 10 HP 1:2、后 5 HP 1:1；单次 ≤15 HP（换最多 25 SAN）；单场 ≤30 SAN；占 M1
  - SAN→HP: 前 10 SAN 2:1、后 10 SAN 3:1；单次 ≤20 SAN（换最多 8 HP）；单场 ≤15 HP；占 M1
  - 不对称：HP→SAN 效率更高（真金白银的痛苦换稳定）
- 引擎：CombatAction = M1/Broca 双通道（3+Skill 动作）；CombatState 无兑换累计字段；无 HP↔SAN 动作

## 关键待决

1. 动作类型与通道（ConvertHpToSan/ConvertSanToHp，M1）
2. 兑换公式实现口径（分段线性 + 单次上限 + 一位小数量化——正典已有，确认）
3. 单场上限追踪（per-participant 累计）+ 边界（能否换到 HP=0 / SAN=0）
4. 引擎落点 + Console demo 接线

## 预期产出

- `.scratch/grilling-79-p4b-hp-san-convert/task-plan.md` + 决策树 + 六维状态 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #79 关闭总结

### 决策表（4 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | 两独立动作（ConvertHpToSan/ConvertSanToHp）+ M1 通道 + 花费量 payload | Enums/CombatAction |
| D2 | 正典字面公式（floor1+cap 8.0）；单次上限 15/20 | ActionResolver |
| D3 | ≥1 边界 + per-participant 累计（30/15） | CombatState |
| D4 | 不产 δ/s 事件；demo 命令+额度显示 | Console |

### 特性

- **无 [NEW] 参数批次**（兑换率/上限全为正典值——互转是少数零新参数批次）

### 受影响文件

- `.scratch/grilling-79-p4b-hp-san-convert/task-plan.md`（新建）
- `规则/核心机制.md`（§5.3 边界注待写）
- `docs/决策树.md`（#79）、`docs/设计框架-六维状态.md`（P4b ✅）、memory
- 实施后：Enums/CombatAction/CombatState/ActionResolver/Console/Tests

### 推迟清单

- 互转 δ/s 事件（自残痛觉）→ 事件系统扩展；药物/装备交互 → P5；UI → 战斗界面

### 质量门禁

- 4 决策全落位；不变量：公式逐值一致/边界保护/累计上限/通道互斥/一位小数契约
- 后续：T1-T6 实施

---
*导出: 2026-09-12 | 来源: GitHub issue*
