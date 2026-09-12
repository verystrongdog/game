# map: csharp-damage

> csharp-engine step 8（plan §十一）——DamageCalculator：物理/精神伤害结算（命中判定 + 低 SAN 穿透 + 防御/回避修正 + SAN→HP 成分）。Status: closed ✅（2026-08-13，八航）

## Notes

- 依赖 csharp-engine plan §4.6（DamageCalculator 方法签名 + 精神公式 round [NEW]）+ §六（伤害结算接线 = 修复 #10 全文：motivation = clamp(tone_bias, −1, 1)、force = clamp(DA_SNc − 0.5, 0, 0.5)、防御 −50% 仅物理、L0 回避 −10% 命中无条件生效、精神 HP 成分向下取至 0.1（floor1））+ §十 Damage 测试行（命中率分布/L0 回避/永远命中+最低 1/穿透边界/防御 −50%）
- 上游交付：csharp-engine-types ✅（CalibrationConfig 实例 record / IRng / ParticipantState.IsDefending / ToneState / GateState）、csharp-cstc ✅（gate 三值语义）、csharp-speed ✅（行动顺序；本 feature 的消费者在 step 10）
- 设计文档依据：核心机制 §4.2（物理伤害公式 + 精神伤害公式 + 动机/发力修正）、§4.3（低 SAN 穿透双档 + 精神永远命中 + 防御仅物理）、§5.0；基础行动设计 行动1-3 + §四 参数速查（HP 成分向下取整）；回合战斗流程 §6.2（L0 回避 90%→L3 45%，L0 无条件自动触发）；运行时状态模型 §6.5（gate_bonus 映射：attack_physical → gate_somatic / attack_mental → gate_cognitive；技能 role）；NPC AI 行为模型 §3.3（tone_bias 权重表 attack_physical/attack_mental）；武器与装备 §1.1（weapon_bonus 0~+6 括号内同等放大）/§1.2（weapon_hit_mod −15%~+10%）/§1.3（精神武器现不造成直接伤害，`(2+weapon_bonus)` 为未来条件式）/§1.4（护甲减伤 = 主动防御 + 护甲被动）
- 关键实测（任务issue 01 数据实测第一轮）：tone_bias(attack_physical) ∈ [−0.52, 0.58000004]（motivation cap +1.0 为设计界，生产者自然到不了）；attack_mental ∈ [−0.31, 0.39000002]；穿透阈值 demo NPC 60 → 18/9、玩家 80 → 24/12；取整可见差异三例（5.6 / 1.5 / 2.6）；命中边界 0.75 f32 精确、严格小于
- demo 范围：空手（weapon_bonus=0、无 weapon_hit_mod）、无护甲、无 link 修正项、忍耐·主动未实现（endurance 参数预留）——武器/护甲/链路调制属 step 10+ 接线

## Decisions-so-far

- [任务issue 01](design/issues/01-damage-spec.md) → 数据实测第一轮（9 条）+ 第二轮（5 条量化仿真）→ claimed（2026-08-13）
- **Q 裁决（2026-08-13 用户）**：Q1=A（低 SAN 穿透双档百分比 <30%→×1.3 / <15%→×2.0——核心机制 §4.3 + 基础行动设计 §四 速查表一致，仅行动2 叙述行离群）、Q2=A（精神 motivation = tone_bias(attack_mental)——plan §六 行拆物理/精神两行）、Q3=D（**用户反提案：一位小数结算**——放弃整数取整，伤害/SAN/HP 全程 float + 每步量化到 0.1：主伤害 round1 半进位 / HP 成分 floor1 向下取至 0.1）
- Q3=D 连带决策：D13 量化函数（MathF.Round(x,1,AwayFromZero)——.NET 8 全 f32 域（2026-08-13 审计 F1 修正）+ MathF.Floor(x×10f)/10f，每步结算后量化防 f32 漂移）、D14 **L2 跨 feature 类型变更 22 字段 int→float**（ParticipantState 4 + PhysicalDamageEvent 6 + MentalDamageEvent 8 + CalibrationConfig 4 demo 模板 PlayerHp/PlayerSan/NpcHp/NpcSan——types 文件当前零消费者）、D15 设计文档写回（基础行动设计 行动2/§四 + plan §六 + 核心机制 §4.2 + term_registry）、D16 呈现层显示规则不覆盖
- 关键实测（第二轮）：三敏感值全保留（5.6/1.5/2.6）；**最低档穿透救活** 1.0×1.3→1.3（整数世界两法皆 1）；inner m=0.25→1.5（动机不再被取整吞掉）；0.7 网格点 f32 存储 0.699999988079071
- **spec v1.1 + sign-off 批准（2026-08-13 dog）**：全量审计（3 专家）退回——F1（MathF.Round 语义模型错误：.NET 8 全 f32 域，非 double 委托）等 14 项 → v1.1 修复 → Δ审计（2 专家 + refute）通过（0❌/0⚠️ 阻塞）→ 残差清扫 → 人类签字 + 结转 5 项
- **实现（2026-08-13）**：4 批提交（1d02ff5 类型变更 / 2fe45f1 DamageCalculator / 4998602 测试 38 项 / 341dc9a types spec 🔧 行）——178/178 全绿，AC-1~18 逐条 ✅，结转 5 项全部回填，**0 spec 缺陷**（连续第六航）。下一步 step 9 csharp-events（EventProcessor）→ step 10 csharp-flow

## Fog

- 任务issue 数据实测 ✓ → Q 裁决 ✓（Q1=A/Q2=A/Q3=D 一位小数）→ 设计文档写回 ✓ → spec v1.0 ✓ → 全量审计 ✓（退回修复）→ Δ审计 ✓（refute 推翻 AC-17 原机制）→ sign-off ✓（dog 批准 2026-08-13）→ 工作issue 01 实现 + 自审 ✓（178/178）→ feature 闭合 ✅

---
*创建: 2026-08-13 | 更新: 2026-08-13*
*关联: [任务issue 01](design/issues/01-damage-spec.md)*
