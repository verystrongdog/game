# 任务issue 01: 伤害结算规格（DamageCalculator）

> Status: claimed | Type: task | 维度: 管线

## 问题（这件事要解决什么）

csharp-engine plan §十一 step 8 = **DamageCalculator**——物理/精神伤害结算（plan §4.6 + §六 伤害结算接线）。没有它：step 10（CombatState + TurnManager + ActionResolver）无伤害公式可接线，战斗闭环无法形成。step 7 已交付的速度排序确定行动顺序，本 feature 结算行动落地后的伤害。

本 issue 产出 DamageCalculator 的精确实现规格，并裁决**三个设计疑问**（低 SAN 穿透双文档矛盾、精神攻击 motivation 生产者、取整链）。

## 目标

- spec.md v1.0（§一~§八 + 变更日志），通过 workflow 审计 + 用户 sign-off
- 覆盖 plan §4.6 全部内容 + plan §十 Damage 测试行（命中率分布/L0 回避/永远命中+最低 1/穿透边界/防御 −50%）
- 三个设计疑问经用户裁决后固化为偏差声明 / 设计文档修正项

## 指标

- spec 中全部数值断言经 python f32 实测验证（本 issue 实测表）
- 审计 0 阻塞项；AC 全部可测

## 范围

- **覆盖**：`DamageCalculator`（物理：`CalcPhysicalDamage`；精神：`CalcMentalDamage`）+ CalibrationConfig 新增伤害常量（11 个 [NEW]）
- **不覆盖**：force/motivation/gate 的**生产者**（tone_bias 计算、DA_SNc clamp——公式在 spec §五 文档化，实现归 step 10 接线层）、命中链路调制（L1 失望/L3 精准——demo 无 link 修正项）、武器数据与 weapon_hit_mod（demo 空手）、护甲减伤（demo 无护甲）、忍耐·主动（CD2 占 Broca，demo 未实现——签名经 endurance 参数预留）、事件产出（CombatEvent——step 10）
- **输入**：csharp-engine-types ✅（CalibrationConfig/IRng/ParticipantState.IsDefending）、csharp-cstc ✅（GateState 三 gate 语义）、csharp-speed ✅（速度排序→行动顺序，本 feature 的行动顺序消费者在 step 10）

## 数据实测（2026-08-13，本 issue 第一轮，python f32 可复算）

| # | 断言 | 实测值 |
|---|------|--------|
| 1 | tone_bias(attack_physical) 值域（tones ∈ [0,1] 角点网格，NPC AI §3.3 权重表） | **[−0.52, 0.58000004]**（min@tone=(0,0,0,1)，max@tone=(0,1,1,0)）——motivation cap +100%（核心机制 §4.2）为设计界，tone_bias 生产者自然到不了（max 0.58） |
| 2 | tone_bias(attack_mental) 值域（权重 (0,+0.4,0,−0.3)） | **[−0.31, 0.39000002]**（max@tone=(0,1,0,0)） |
| 3 | tone_bias 基线 | tone=baseline(0.3/0.4/0.5/0.5) → **0.0** 精确（t−baseline 全 0） |
| 4 | 低 SAN 穿透阈值（demo SAN_max） | NPC 60：tier1 **<18** → +30%，tier2 **<9** → ×2；玩家 80：<24 / <12 |
| 5 | 物理 RED：base 4, f=0.5, m=1.0, gate=1.0 | 4×2.5×1.0 = **10.0**（f32 精确） |
| 6 | 物理：f=0.25, m=0.5, gate=0.8 | 4×1.75×0.8 = **5.6** → floor 5 / round 6（取整方式可见差异） |
| 7 | 精神 inner = 2×(1+m)−1 | m=0 → 1.0；**m=0.25 → 1.5 精确**（0.25 f32 可表示）→ round-half-up 2 / floor 1（取整方式可见差异）；m=−0.31 → 0.38 → max(1,·) → 1 |
| 8 | 穿透取整 | san=2 ×1.3 = **2.6** → round 3 / floor 2（floor 使穿透在基础伤害失效）；san=1 ×1.3 = 1.3 → 两法皆 1；×2.0 → 4 精确 |
| 9 | 命中边界 | 0.85f−0.10f = **0.75 精确**（0.75 f32 可表示）；阈值判定严格小于（roll < 0.75；f32 次邻 0.74999994 → 命中） |

### 第二轮（2026-08-13，Q3=D 一位小数量化仿真）

注：round1/floor1 仿真基于 .NET 8 `MathF.Round(x,1,AwayFromZero)` 委托 double 精度（`Math.Round((double)x, 1, mode)`）的文档化实现语义 + python f32 复算；实现测试以真实 MathF.Round 输出钉 AC 锚点（RED 阶段实测）。

| # | 断言 | 实测值 |
|---|------|--------|
| 10 | round1（主伤害，半进位） | 5.6→**5.6** / 1.5→**1.5** / 2.6→**2.6**（三敏感值全保留）/ 1.95→**2.0**（half 案例）/ 1.3→**1.3** / 0.75→**0.8** / 3.36→**3.4** / 1.2→**1.2** |
| 11 | floor1（HP 成分，向下取至 0.1：`MathF.Floor(x×10f)/10f`——2026-08-13 复测：×0.1f 乘法离格 1.3f→1.3000000715，/10f 精确落回 f32 网格点） | 5.6→**5.6** / 1.95→**1.9** / 0.75→**0.7** / 3.36→**3.3**；HP 成分 1.5/2→**0.7**、2.6/2→**1.3**、2.0/2→**1.0** |
| 12 | 穿透在最低伤害生效 | 1.0×1.3→round1=**1.3**（整数世界 round/floor 皆 1——一位小数救活最低档穿透）；2.0×1.3→**2.6** |
| 13 | 存储网格 f32 | 0.7 网格点存储 = **0.699999988079071**（f32 最近值）——显示层格式化「0.7」；每步量化 → 状态恒在 0.1 网格 → 跨回合无漂移 |
| 14 | 精神 inner（m=0.25） | round1(2×1.25−1) = **1.5** 精确（动机不再被取整吞掉；整数世界 floor 1 / round 2） |

## 追问

### Q1: 低 SAN 穿透双文档矛盾

- 核心机制 §4.3：`敌方 SAN < 30% → 额外 +30%；SAN < 15% → ×2`（双档，百分比）
- 基础行动设计 §四 参数速查表：`敌方低SAN穿透 | SAN<30→+30%, SAN<15→×2`（双档，百分比——与核心机制一致）
- 基础行动设计 行动2 叙述（仅此一处不同）：`敌方 SAN < 30 时 → 精神攻击额外 +30% 效果`（单档，绝对值）
- plan §4.6 已按核心机制双档百分比写（签名参数 enemySanRatio 亦为比例形态）

**建议 A（推荐）：核心机制双档百分比**——`ratio < 0.30 → ×1.3；ratio < 0.15 → ×2.0（互斥取高档）`。两处权威（核心机制 §4.3 + 基础行动设计 §四 速查表）一致，仅行动2 叙述行离群；NpcSan=60 下绝对值 30 等于 50%，与 30% 语义差近一倍；双档给 SAN 濒危（<15%）更强的崩溃反馈。基础行动设计 行动2 叙述行同步写回修正（一致性清扫）。

**✅ 裁决（2026-08-13）：A——双档百分比**。行动2 叙述行写回修正。

- B：基础行动设计单档绝对值（SAN < 30 → +30%）——与百分比语义冲突，SAN_max 高的角色阈值不变
- C：单档百分比（< 30% → +30%，无 ×2 档）——丢弃核心机制第二档

### Q2: 精神攻击 motivation 生产者

plan §六 motivation_mod 行字面写 `clamp(tone_bias(attack_physical), −1, +1.0)`。但精神攻击 role = attack_mental（运行时状态模型 §6.5 技能映射），NPC AI §3.3 权重表有独立的 attack_mental 行。

**建议 A（推荐）：按角色映射 tone_bias(attack_mental)**（权重 (0, +0.4, 0, −0.3)）——语言攻击的动机偏置来自 DA_VTA（认知动机）+ 5HT 去抑制；attack_physical 的 DA_SNc（运动启动）对语言攻击无意义。plan §六 行的 attack_physical 为物理行示例，精神行缺失为遗漏。

**✅ 裁决（2026-08-13）：A——attack_mental**。plan §六 行写回修正（物理/精神两行并列）。

- B：统一用 attack_physical 的 tone_bias——plan §六 字面，但语义错位

### Q3: 取整链

文档仅定义 HP 成分向下取整（`HP伤害 = SAN伤害的 1/2（向下取整）`，基础行动设计 §四）。plan §4.6 精神公式写 round（[NEW]），物理未定义。实测暴露三处可见差异：物理 5.6（floor 5 vs round 6）、精神 m=0.25 的 1.5（floor 1 vs round 2——floor 使 motivation ≤0.5 全程无法突破忍耐）、穿透 2.6（floor 2 使 +30% 在基础伤害失效）。

**建议 A（推荐）：精神 = 内层 round 半进位 → ×gate → ×穿透倍率 → 最终 round 半进位；物理 = 全乘法后 floor 一次**——精神双层 round（plan 字面 round + 穿透有效性：2.6→3）；物理 floor（文档 floor 先例 + 保守向下）。max(1,·) 在 gate 前（plan 字面——gate=0 → 0 伤害语义保留）。

- B：全部 floor——穿透在基础伤害失效（2.6→2），motivation 在精神侧失效（1.5→1），不推荐
- C：全部 round 半进位——物理无文档依据，且 max(1,·) 位置若在 gate 后则破坏 gate=0 语义

**✅ 裁决（2026-08-13）：D——一位小数结算（用户反提案采纳）**。放弃整数取整，伤害/SAN/HP 全程 float + 每步结算后量化到 0.1：主伤害 round 半进位、HP 成分向下取至 0.1（保留「向下取整」语义）。三敏感值全保留（5.6/1.5/2.6），最低档穿透救活（1.0×1.3=1.3）。代价（用户已确认）：已交付 types 的 int→float 修改（L2 跨 feature 声明）+ 设计文档数值语义写回。

## 判断与取舍（2026-08-13 定稿：Q1=A / Q2=A / Q3=D）

| D# | 决策 | 依据 |
|----|------|------|
| D1 | DamageCalculator = 实例类 + CalibrationConfig 构造注入（镜像 SpeedScoreCalculator；plan §4.6 只给了方法签名未定类形态——types 结转 #4 校准 sweep 需要实例化） | csharp-speed 先例；CalibrationConfig 实例 record |
| D2 | 物理：`damage = round1((base + weapon_bonus) × (1 + clamp(force,0,ForceCap) + clamp(motivation,0,MotivationCap)) × gate × (defenderIsDefending ? DefendReduction : 1))`；`hit = rng.NextFloat() < BaseHitChance − L0EvadePenalty`（0.85−0.10=0.75，L0 回避无条件自动触发——回合战斗流程 §6.2，plan 修复 #10 demo 无 link 修正项） | plan §4.6 + §六；实测 #5/#6/#9/#10 |
| D3 | 精神：`inner = max(1.0, round1(2×(1+motivation) − endurance))`；`san = round1(inner × gate × penMultiplier)`（penMultiplier ∈ {1.0, 1.3, 2.0} 互斥取高档——Q1=A）；`hp = floor1(san × 0.5)`（向下取至 0.1——Q3=D） | plan §4.6 + 核心机制 §4.3 + 基础行动设计 §四；实测 #11/#12/#14 |
| D4 | 低 SAN 穿透用**受击前** SAN（caller 传 ratio = San/SanMax，受击前状态）；阈值严格小于（ratio < 0.30 / < 0.15——恰好 30%/15% 不触发，plan §十 RED 边界） | plan §十 Damage 行「敌方恰好 30%/15%」；实测 #4 |
| D5 | 精神永远命中（无 rng 参数）；防御 −50% 仅物理（精神攻击无视物理防御——「闪避/格挡无效——对方的言语/凝视必然进入感知」） | 核心机制 §4.3；基础行动设计 行动2/§四 速查表 |
| D6 | `defenderIsDefending` 入 CalcPhysicalDamage 签名（plan §4.6 签名缺失但 §六 明确属结算职责——偏差 B 声明） | plan §六 接线表 |
| D7 | CalibrationConfig 新增 12 常量 [NEW]：BasePhysicalDamage=4 / BaseMentalDamage=2 / BaseHitChance=0.85f / L0EvadeHitPenalty=0.10f / ForceCap=0.5f / MotivationCap=1.0f / DefendPhysicalReduction=0.5f / SanPenetrationTier1Ratio=0.30f / SanPenetrationTier1Multiplier=1.3f / SanPenetrationTier2Ratio=0.15f / SanPenetrationTier2Multiplier=2.0f / DamagePrecision=0.1f（floor1 用量化粒度；round1 走 MathF.Round(x,1,AwayFromZero) 固定 digits=1，一致性由测试守护）（EndurancePassive=1 不入 config——endurance 走方法参数，caller 传） | 核心机制 §4.2/§4.3 + 基础行动设计 §四 + 回合战斗流程 §6.2 + Q3=D；plan §七 校准常量表扩展 |
| D8 | baseDamage 参数保留（demo 传 4/2；weapon_bonus demo 传 0——武器系统 step 10+ 接线，物理公式武器加成在括号内放大，武器与装备 §1.1） | plan §4.6 签名；核心机制 §4.2 |
| D9 | 精神武器（武器与装备 §1.3 `(2+weapon_bonus)` 公式）为「未来有精神伤害型武器时」条件式——现精神武器走效果型不造成直接伤害，本 feature 不覆盖（偏差 B 声明） | 武器与装备 §1.3 |
| D10 | 生产者公式（motivation = clamp(tone_bias(role), −1, 1)——物理 attack_physical / 精神 attack_mental（Q2=A）、force = clamp(DA_SNc − 0.5, 0, 0.5)）在 spec §五 文档化，**实现归 step 10**（plan §十一 step 8 范围仅 DamageCalculator；§六 为接线规格） | plan §六 + §十一 + Q2=A |
| D11 | 穿透倍率与 gate 乘法可交换（max(1.0,·) 在两者之前）→ 结算顺序无歧义，spec 固定「inner → ×gate → ×pen → round1」叙述序 | 数学交换律；实测 #12 |
| D12 | 异常契约：null（config/rng）→ ArgumentNullException；参数值域（gate/motivation/ratio 等）不校验——文档化未定义行为（镜像 speed/WcState 姿态） | csharp-speed spec 先例 |
| D13 | **量化函数（Q3=D）**：round1 = `MathF.Round(x, 1, MidpointRounding.AwayFromZero)`（.NET 8 委托 double 精度，无 f32 ×10 乘法误差）；floor1 = `MathF.Floor(x × 10f) / 10f`（2026-08-13 复测：×DamagePrecision 乘法使 1.3f→1.3000000715 离格，/10f 精确除法落回 f32(0.1k) 网格点）。**每步结算产物立即量化** → 状态恒在 0.1 网格的 f32 最近值 → 跨回合无漂移、确定性（实测 #13） | 实测 #10/#11/#13 |
| D14 | **L2 跨 feature 类型变更（Q3=D）**：22 字段 int→float——ParticipantState 4（Hp/HpMax/San/SanMax，CreateDefault 签名同步）+ PhysicalDamageEvent 6（DamageDealt/DamageBlocked/IncomingDamage/TargetHpBefore/TargetHpAfter/TargetHpMax）+ MentalDamageEvent 8（SanDamage/HpDamage/TargetSanBefore/TargetSanAfter/TargetSanMax/TargetHpBefore/TargetHpAfter/TargetHpMax）+ CalibrationConfig 4 demo 模板（PlayerHp/PlayerSan/NpcHp/NpcSan 50/80/15/60 → 50f/80f/15f/60f，供 CreateDefault(float,float) 直传）。BaseDamage/WeaponBonus/HealEvent.HealAmount 保持 int（整数值输入/占位）。spec §二 数据结构声明 + 偏差 B（跨 feature L2）；types spec 变更日志补 🔧 修正行指向本 spec；文件所有权归 damage 工作issue（types 文件当前零消费者——grep 验证 .Hp/.San 无引擎引用） | Q3=D 用户确认；变更管理回路 L2 |
| D15 | **设计文档写回（Q1/Q2/Q3 关联）**：基础行动设计 行动2 叙述行改双档百分比（Q1=A）/ §四 速查表「HP伤害 = SAN伤害的 1/2（向下取整）」→「1/2（向下取至 0.1）」+ 数值语义注（Q3=D）/ plan §六 motivation_mod 拆物理·精神两行（Q2=A）/ 核心机制 §4.2 结算量化注（Q3=D）/ term_registry HP·SAN·向下取整相关条目复查更新 | 一致性清扫原则；垃圾桶隔离原则 |
| D16 | 呈现层显示规则：HP/SAN 显示格式（1 位小数 vs trim 尾零）属 呈现 维度决策，本 feature 不阻塞——spec 记录为「展示不覆盖」 | plan §十一 step 8 范围 |

## 产出

- [x] 数据实测第一轮 + 第二轮（本 issue，已完成——见上表）
- [x] Q1/Q2/Q3 用户裁决（Q1=A 双档百分比 / Q2=A attack_mental / Q3=D 一位小数结算）
- [ ] 设计文档修正写回（D15 清单：基础行动设计 行动2/§四、plan §六、核心机制 §4.2、term_registry）
- [ ] spec.md v1.0 → 审计 → 修复升版 → Δ审计
- [ ] 人类复核 → sign-off.md
- [ ] 工作issue 01 → 实现 + 证据式自审（含 D14 类型变更 22 字段）
- [ ] map.md 更新 + 回顾段（feature 闭合）

## Comments

- 2026-08-13：创建。数据实测第一轮完成（tone_bias 值域/穿透阈值/RED 算术/取整可见差异/命中边界 f32）。三个疑问提交用户裁决（Q1 穿透双档、Q2 精神 motivation 生产者、Q3 取整链）。
- 2026-08-13：裁决完成——Q1=A（双档百分比；基础行动设计 §四 速查表与核心机制 §4.3 本就一致，仅行动2 叙述行离群）、Q2=A（attack_mental；plan §六 行写回拆两行）、Q3=D（**用户反提案：一位小数结算**——放弃整数取整，全程 float + 每步量化到 0.1）。Q3=D 引发 L2 跨 feature 类型变更（22 字段 int→float，D14；18→22 补正：CalibrationConfig 4 demo 模板加入，2026-08-13 spec 写作期发现）+ 设计文档数值语义写回（D15），代价已向用户确认。数据实测第二轮完成（量化仿真 5 条：round1/floor1 对照、最低档穿透救活 1.0×1.3→1.3、存储网格 f32、inner 动机保留）。进入设计文档修正写回 + spec v1.0。
