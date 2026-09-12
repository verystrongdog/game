# #82 [Grilling] P5-1 武器与护甲进引擎 — 装备槽 + 数值集成

> 状态：关闭 · 创建 2026-08-16 · 关闭 2026-08-16
> 标签：维度:规则, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/82

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

承接 Grilling #70 路线图 P5-1：武器/护甲系统（实体/武器与装备.md 正典完整）落地引擎——装备数据结构 + 槽位 + 数值集成（weapon_bonus/命中/被动减伤/SAN 阈值偏移）+ 效果分级实现。

## 六维定位

- **维度**: 规则（装备公式集成）+ 管线（引擎实现）
- **依赖**: 武器与装备.md（11 物理武器 + 25 护甲 + 12 精神武器 + Boss 6 件——正典完整）+ 引擎 DamageCalculator（weaponBonus 参数已就位——#24 核查）+ P1b LinkState（精神武器 m 阈值 + 武器链路解锁）+ 核心机制 §5.0（equipment_SAN/HP）
- **承接**: #70 路线图 P5-1

## 当前状态

- 正典（武器与装备.md）：物理伤害 = (4+weapon_bonus)×(1+force+motivation)；命中 85%+weapon_hit_mod；护甲减伤 = 主动防御(−50%) + Σ被动减伤（无上限）+ 盾替换(−70%)；SAN 阈值偏移累加；equipment_SAN/HP +1 占位；精神武器 m 阈值 + 复杂效果（占 M1）
- 引擎：DamageCalculator 签名含 weaponBonus（可传）+ hit 判定含 85% 基础；无装备数据结构/槽位

## 关键待决

1. 装备数据结构 + 槽位（主手/副手/饰品×5 + 精神防护——正典 §4.1）
2. 效果实现范围（数值类全实现 + 简单状态 vs 全效果）
3. 精神武器（m 阈值校验 + 效果接口预留）
4. 装备流程（构建层装备 → 战斗快照，与 P1b 同模式）

## 预期产出

- `.scratch/grilling-82-p5-1-equipment/task-plan.md` + 决策树 + 六维状态 + memory

---

## 评论（1 条）

### verystrongdog · 2026-08-16

## Grilling #82 关闭总结

### 决策表（4 项共识）

| 编号 | 决策 | 落位 |
|------|------|------|
| D1 | equipment.json + 槽位校验 + 构建层快照 | T1/T2 |
| D2 | 数值全实现 + 4 简单状态；复杂效果接口预留 | T3/T4 |
| D3 | 精神武器 m 阈值校验 + M1 占用 + 效果接口预留 | T5 |
| D4 | EquipmentSet 构建层→快照 + DamageCalculator 接入 + demo | T6 |

### 受影响文件

- `.scratch/grilling-82-p5-1-equipment/task-plan.md`（新建：T1-T7）
- `docs/决策树.md`（#82）、`docs/设计框架-六维状态.md`（P5-1 ✅）、memory
- 实施后：equipment.json + Equipment/EquipmentSet/StatusEffects/MentalWeaponResolver + DamageCalculator/Enums/CombatState/Console/Tests

### 推迟清单

- 复杂效果 → 状态系统扩展批次；武器链路解锁 → P1b 后；精神武器 12 效果 → 状态扩展；稀有/Boss → Boss 批次；装备数值 → #35

### 质量门禁

- 4 决策全落位；不变量：槽位互斥/伤害公式正典一致/减伤累加/精神武器阈值校验/确定性
- 后续：T1-T7 实施（依赖 P1b LinkState——精神武器 m 阈值校验点）

---
*导出: 2026-09-12 | 来源: GitHub issue*
