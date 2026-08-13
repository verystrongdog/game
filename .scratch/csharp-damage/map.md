# map: csharp-damage

> csharp-engine step 8（plan §十一）——DamageCalculator：物理/精神伤害结算（命中判定 + 低 SAN 穿透 + 防御/回避修正 + SAN→HP 成分）。Status: active

## Notes

- 依赖 csharp-engine plan §4.6（DamageCalculator 方法签名 + 精神公式 round [NEW]）+ §六（伤害结算接线 = 修复 #10 全文：motivation = clamp(tone_bias, −1, 1)、force = clamp(DA_SNc − 0.5, 0, 0.5)、防御 −50% 仅物理、L0 回避 −10% 命中无条件生效、精神 HP 成分 floor(san/2)）+ §十 Damage 测试行（命中率分布/L0 回避/永远命中+最低 1/穿透边界/防御 −50%）
- 上游交付：csharp-engine-types ✅（CalibrationConfig 实例 record / IRng / ParticipantState.IsDefending / ToneState / GateState）、csharp-cstc ✅（gate 三值语义）、csharp-speed ✅（行动顺序；本 feature 的消费者在 step 10）
- 设计文档依据：核心机制 §4.2（物理伤害公式 + 精神伤害公式 + 动机/发力修正）、§4.3（低 SAN 穿透双档 + 精神永远命中 + 防御仅物理）、§5.0；基础行动设计 行动1-3 + §四 参数速查（HP 成分向下取整）；回合战斗流程 §6.2（L0 回避 90%→L3 45%，L0 无条件自动触发）；运行时状态模型 §6.5（gate_bonus 映射：attack_physical → gate_somatic / attack_mental → gate_cognitive；技能 role）；NPC AI 行为模型 §3.3（tone_bias 权重表 attack_physical/attack_mental）；武器与装备 §1.1（weapon_bonus 0~+6 括号内同等放大）/§1.2（weapon_hit_mod −15%~+10%）/§1.3（精神武器现不造成直接伤害，`(2+weapon_bonus)` 为未来条件式）/§1.4（护甲减伤 = 主动防御 + 护甲被动）
- 关键实测（任务issue 01 数据实测第一轮）：tone_bias(attack_physical) ∈ [−0.52, 0.58000004]（motivation cap +1.0 为设计界，生产者自然到不了）；attack_mental ∈ [−0.31, 0.39000002]；穿透阈值 demo NPC 60 → 18/9、玩家 80 → 24/12；取整可见差异三例（5.6 / 1.5 / 2.6）；命中边界 0.75 f32 精确、严格小于
- demo 范围：空手（weapon_bonus=0、无 weapon_hit_mod）、无护甲、无 link 修正项、忍耐·主动未实现（endurance 参数预留）——武器/护甲/链路调制属 step 10+ 接线

## Decisions-so-far

- [任务issue 01](design/issues/01-damage-spec.md) → 数据实测第一轮（9 条：tone_bias 值域/穿透阈值/RED 算术/取整可见差异/命中边界 f32）→ claimed（2026-08-13）
- Q 裁决（待用户）：Q1 低 SAN 穿透双档矛盾 / Q2 精神 motivation 生产者 / Q3 取整链

## Fog

- 任务issue 数据实测 ✓ → Q 裁决 → 设计文档写回 → spec v1.0 → 全量审计 → 修复升版 → Δ审计 → sign-off → 工作issue 01 实现 + 自审 → feature 闭合

---
*创建: 2026-08-13 | 更新: 2026-08-13*
*关联: [任务issue 01](design/issues/01-damage-spec.md)*
