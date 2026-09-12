# DamageCalculator — 实现规格

> 物理/精神伤害结算（命中判定 + 低 SAN 穿透 + 防御/回避修正 + 一位小数量化）——csharp-engine step 8 引擎模块。版本: v1.1

## 目录

- [一、范围与依赖](#一范围与依赖)
- [二、数据结构](#二数据结构)
- [三、接口定义](#三接口定义)
- [四、枚举与常量](#四枚举与常量)
- [五、交叉引用约束](#五交叉引用约束)
- [六、验收标准](#六验收标准)
- [七、本 spec 自检清单](#七本-spec-自检清单)
- [八、偏差声明](#八偏差声明)
- [参数速查表](#参数速查表)
- [变更日志](#变更日志)

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | `DamageCalculator`（实例类，Engine/）——`CalcPhysicalDamage`（伤害 + 命中判定 + 防御/L0 回避修正）+ `CalcMentalDamage`（SAN 伤害 + HP 成分 + 低 SAN 穿透 + 忍耐）+ 量化函数 `Round1`/`Floor1`（公开 static，AC-3 可测性）；CalibrationConfig 新增 12 伤害常量（[NEW]）+ 4 demo 模板常量 int→float |
| 不覆盖 | weapon_hit_mod（demo 空手，武器与装备 §1.2）；护甲减伤（demo 无护甲，§1.4）；链路调制（L1 失望/L3 精准等——demo 无 link 修正项，回合战斗流程 §6.2）；忍耐·主动（CD2 占 Broca——demo 未实现，接口经 endurance 参数预留）；精神武器伤害（§1.3 条件式——B2）；伤害**应用**到 ParticipantState（step 10 Flow 层——本 feature 只产出伤害数值）；事件产出 CombatEvent 填充（step 9/10）；呈现层 HP/SAN 显示格式（D16）；force/motivation/gate 的**生产者**（tone_bias 计算、DA_SNc clamp——公式见 §五 5，实现归 step 10 接线层，B3） |
| 前置依赖 | csharp-engine-types ✅（CalibrationConfig 实例 record / IRng.NextFloat ∈ [0,1) / ParticipantState.IsDefending / DeterministicRng）、csharp-cstc ✅（gate 三值语义——运行时状态模型 §6.5）、csharp-speed ✅（行动顺序——结算消费者在 step 10） |
| 阻塞 | step 9 EventProcessor（事件数值字段填充）、step 10 csharp-flow（CombatState/TurnManager/ActionResolver 结算调用点） |

## 二、数据结构

### 2.1 DamageCalculator（新建，Engine/DamageCalculator.cs）

实例类 + CalibrationConfig 构造注入（镜像 SpeedScoreCalculator 类形态——plan §4.6 只给了方法签名未定类形态；types 结转 #4 校准 sweep 需要实例化注入变体，D1）：

```csharp
public sealed class DamageCalculator
{
    public DamageCalculator(CalibrationConfig cal);
    public static float Round1(float x);
    public static float Floor1(float x);
    public (float Damage, bool Hit) CalcPhysicalDamage(int baseDamage, int weaponBonus, float forceMod, float motivationMod, float gateBonus, bool defenderIsDefending, IRng rng);
    public (float SanDamage, float HpDamage) CalcMentalDamage(int baseDamage, float motivationMod, int endurance, float enemySanRatio, float gateBonus);
}
```

- 无内部可变状态；cal 保存引用（不可变 record）。确定性：无 static 可变状态（AC-15）。
- Round1/Floor1 为纯函数 static（量化函数——§三 3.3），公开系 AC-3 直接锚定需要（可测性访问器模式，七航回顾建议）。

### 2.2 L2 跨 feature 类型变更——22 字段 int→float（Q3=D，偏差 B5）

一位小数结算要求 HP/SAN 状态与事件数值字段承载小数。变更清单（damage 工作issue 独占文件所有权；types 文件当前零消费者——grep 验证 `.Hp`/`.San` 无引擎引用）：

| 文件 | 字段 | 变更 |
|------|------|------|
| ParticipantState.cs | Hp / HpMax / San / SanMax | int → float；`CreateDefault(int hpMax, int sanMax)` → `CreateDefault(float hpMax, float sanMax)` |
| CombatEvents.cs PhysicalDamageEvent | DamageDealt / DamageBlocked / IncomingDamage / TargetHpBefore / TargetHpAfter / TargetHpMax | int → float（BaseDamage/WeaponBonus 保持 int——整数值输入） |
| CombatEvents.cs MentalDamageEvent | SanDamage / HpDamage / TargetSanBefore / TargetSanAfter / TargetSanMax / TargetHpBefore / TargetHpAfter / TargetHpMax | int → float |
| CalibrationConfig.cs | PlayerHp / PlayerSan / NpcHp / NpcSan | int → float（50f/80f/15f/60f——demo 模板值不变，供 CreateDefault(float,float) 直传） |

- HealEvent.HealAmount 保持 int（占位字段 demo 未用——未来 feature 决定）。
- 现有 types 测试（ParticipantStateTests/CombatEventsTests）以 int 字面量断言——xUnit 泛型推断绑定 `Assert.Equal<float>`（int 字面量在调用点隐式转换为 float 实参）继续成立；现有断言值均为 ≤80 的整数，在 f32 精确整数域（≤ 2^24）内。边界：①大整数（>2^24，如 16777217）int→float 转换失真——本 spec 断言值全在精确域内；②无 f 后缀的 double 字面量（如 `Assert.Equal(0.5, e.DamageDealt)`）会绑定 `Assert.Equal<double>` 并逐位失败——工作issue 仅验证现值编译+通过，不改断言值；AC-18 为回执（v1.1 审计 C-F1 + Δ审计残差修正）。
- types spec（csharp-engine-types）变更日志补 `🔧 修正` 行指向本 spec（跨 feature 变更记录）。

## 三、接口定义

### 3.1 CalcPhysicalDamage

```
CalcPhysicalDamage(baseDamage, weaponBonus, forceMod, motivationMod, gateBonus, defenderIsDefending, rng)
→ (damage, hit)
```

计算顺序**写死**（f32 结合序契约，§五 1——speed 结转 #5 先例：结合序影响逐位结果）：

```
s1 = (float)(baseDamage + weaponBonus)                    // int 加法精确，后转 float
cf = clamp(forceMod, 0, ForceCap)                          // 负值归零——沮丧不降伤害（plan §4.6 字面）
cm = clamp(motivationMod, −1, MotivationCap)               // 🔧 E-1 裁决 2026-08-14：下界 0→−1（与精神/flow producer 口径统一；沮丧降伤害）
s2 = (1f + cf) + cm                                        // 左结合
s3 = s1 × s2
s4 = s3 × gateBonus
s5 = s4 × (defenderIsDefending ? DefendPhysicalReduction : 1f)
damage = Round1(s5)                                        // 一位小数（Q3=D，B4）
roll = rng.NextFloat()                                     // 恰好 1 次，无条件（AC-9）
hit = roll < (BaseHitChance − L0EvadeHitPenalty)           // 0.85f−0.10f = 0.75f 精确（实测 #9）；L0 回避无条件自动触发（回合战斗流程 §6.2，plan 修复 #10）
```

- 无最低伤害（物理不设 min——plan §4.6 字面）。
- 异常：`cal` null → ArgumentNullException（构造）；`rng` null → ArgumentNullException（AC-16）。
- 未定义行为（文档化，不防御）：NaN/Infinity 输入、负 baseDamage、负 weaponBonus（s1 可为负）、gateBonus ∉ [0,1]（域内由生产者保证——运行时状态模型 §6.5）（调用方职责；v1.1 审计 K-F7 补漏）。
- 输入不可变（值类型参数）；输出为新值（AC-15）。

### 3.2 CalcMentalDamage

```
CalcMentalDamage(baseDamage, motivationMod, endurance, enemySanRatio, gateBonus)
→ (sanDamage, hpDamage)
```

**永远命中**（无 rng 参数——精神攻击无命中判定，核心机制 §4.3；AC-9 零消费证明）：

```
raw = (float)baseDamage × (1f + motivationMod) − (float)endurance   // baseDamage 消费（v1.1 审计 F2 修复——原写死 2f 使参数失效）；motivation 不 clamp（负值降伤害，下限由 max 兜底——plan §4.6 字面）
inner = max(1.0f, Round1(raw))                            // 最低 1.0——max 在 gate 前（plan 字面：gate=0 → 0 伤害语义保留）
pen = SanPenetrationTier2Multiplier  if enemySanRatio < SanPenetrationTier2Ratio      // 先判 tier2（<0.15 → ×2.0）
    = SanPenetrationTier1Multiplier  elif enemySanRatio < SanPenetrationTier1Ratio    // 再判 tier1（<0.30 → ×1.3）
    = 1f                                                    // 互斥取高档，严格小于（恰好 30%/15% 不触发，D4/AC-13）
s1 = inner × gateBonus
s2 = s1 × pen
sanDamage = Round1(s2)
hpDamage = Floor1(sanDamage × 0.5f)                        // 向下取至 0.1（「向下取整」语义，粒度 0.1——Q3=D）
```

- `baseDamage` 语义 = 基础 SAN 伤害（demo 传 BaseMentalDamage=2——B6）；`endurance` = 忍耐减免合计（被动 1 / 主动 2——caller 传；demo 恒 1）。
- 异常：`cal` null → ArgumentNullException（构造）。无 rng——无 rng 异常路径。
- 未定义行为（文档化，不防御）：NaN/Infinity 输入、ratio ∉ [0,1]、负 endurance、motivationMod ∉ [−1,1]（生产者 clamp 保证域内；v1.1 审计 K-F7 补漏）。

### 3.3 Round1 / Floor1（量化函数，公开 static）

```
Round1(x) = MathF.Round(x, 1, MidpointRounding.AwayFromZero)   // 主伤害量化：半进位到 0.1
Floor1(x) = MathF.Floor(x × 10f) / 10f                        // HP 成分量化：向下取至 0.1
```

- Round1 实现直接调用 MathF.Round——**.NET 8 语义为全 f32 域**：`x ×= power10 → Truncate(x + CopySign(0.49999997f, x)) → x /= power10`（dotnet/runtime v8.0.0 MathF.cs；本地 .NET 8 runtime 8.0.29（SDK 8.0.423）实测）。**非 double 委托**（v1.1 审计 F1 推翻 v1.0 表述）——f32 域的 ×10f 舍入使低于半档的 f32 值仍可半进位（如 1.94999993f×10f→19.5f→+0.49999997f→trunc 20→2.0，AC-14 第二行即哨兵）。
- Floor1 的 ×10f 步在 f32 域（利用 f32 舍入修正——如 1.3f×10f 精确舍入到 13.0f），scale-back 用 **`/ 10f` 精确除法**落回 f32(0.1k) 网格点——`× 0.1f` 乘法会引入 1e-7 级离格（本地实测：1.3f→1.3000000715、0.95f→0.9000000358，逐位锚点会挂）。
- 每步结算产物立即量化 → 状态恒在 0.1 网格的 f32 最近值 → 跨回合无漂移。
- 全部量化锚点以**真实运行时输出**为准（任务issue 实测表第三轮 #15-#19——本地 .NET 8 runtime 8.0.29 实测；第一/二轮为设计级仿真，仅作过程记录）。
- Floor1 仅用于非负输入（HP 成分域）——负值未定义。

## 四、枚举与常量

### 4.1 CalibrationConfig 新增 12 常量（[NEW]，实现时追加）

| 常量 | 符号 | 值 | 来源 |
|------|------|-----|------|
| 物理基础伤害 | BasePhysicalDamage | 4 | 核心机制 §4.2（空手伤害 4 HP） |
| 精神基础伤害 | BaseMentalDamage | 2 | 核心机制 §4.3（基础 2 SAN） |
| 基础命中率 | BaseHitChance | 0.85f | 核心机制 §4.2（基础命中 85%） |
| L0 回避命中惩罚 | L0EvadeHitPenalty | 0.10f | 基础行动设计 §二 行动1 命中判定 / §三 链路调制表（L0 回避 命中 −10%）；自动触发语义——回合战斗流程 §6.2 + plan 修复 #10（v1.1 审计 K-F5 引用修正） |
| 发力上限 | ForceCap | 0.5f | 基础行动设计 §四（force cap +50%） |
| 动机上限 | MotivationCap | 1.0f | 基础行动设计 §四（motivation cap +100%） |
| 防御物理减伤 | DefendPhysicalReduction | 0.5f | 基础行动设计 §四（防御 −50% 仅物理） |
| 穿透一档阈值 | SanPenetrationTier1Ratio | 0.30f | 核心机制 §4.3（SAN<30% → ×1.3） |
| 穿透一档倍率 | SanPenetrationTier1Multiplier | 1.3f | 同上（+30%） |
| 穿透二档阈值 | SanPenetrationTier2Ratio | 0.15f | 核心机制 §4.3（SAN<15% → ×2） |
| 穿透二档倍率 | SanPenetrationTier2Multiplier | 2.0f | 同上 |
| 结算量化粒度 | DamagePrecision | 0.1f | Q3=D（Floor1 粒度 0.1——实现为 /10f 精确除法；Round1 用 MathF.Round(x,1) 固定 digits=1——两者一致性由 AC-3 守护） |

### 4.2 引用不重定义

- `ScaleMental`：未启用（demo 用固定 base 2 经参数传入）——本 feature 不参与（运行时状态模型 §8.1 ⚠️ 待赋值）。
- `ExpectedDamage`：A1 m 公式分母（step 9 EventProcessor 用）——本 feature 不参与。
- 4 demo 模板常量（PlayerHp/PlayerSan/NpcHp/NpcSan）：值不变，类型 int→float（§二 2.2）。

## 五、交叉引用约束

1. **计算顺序契约（f32 结合序写死）**：§三 3.1/3.2 公式块的逐步计算序即契约——实现与测试镜像必须逐字遵循（物理 `(1f+cf)+cm` 左结合、精神 `(float)baseDamage×(1f+m)` 先乘后减——v1.1 审计 F2 修正，原写死 2f）。AC 锚点（5.6f/1.5f/2.6f/1.95→2.0f）即哨兵。
2. **穿透判定序**：先 tier2 后 tier1，互斥取高档，严格小于（ratio < 0.15f / < 0.30f）。0.30f 与 0.15f 端点为「不触发」（plan §十「敌方恰好 30%/15%」）。
3. **输入语义**：`enemySanRatio` = 受击前 San/SanMax（caller 职责，D4）；`gateBonus` = 本回合同一次结算的 gate_bonus(role)（运行时状态模型 §6.5 映射：attack_physical→gate_somatic、attack_mental→gate_cognitive；perceive/support bypass=1.0）；`forceMod`/`motivationMod` = 生产者产物（§五 5），公式内再 clamp。
4. **RNG 消费序**：CalcPhysicalDamage 恰好 1 次 NextFloat（无条件——先取 roll 再判，与 roll 值无关）；CalcMentalDamage 0 次（AC-9 ThrowingRng 双面证明）。
5. **生产者公式（文档化，实现归 step 10——B3）**：motivation（物理）= clamp(tone_bias(attack_physical), −1, 1)（权重 (0, +0.3, +0.5, −0.3)，NPC AI §3.3，实测值域 [−0.52, 0.58]——cap +1.0 为设计界，生产者自然到不了）；motivation（精神）= clamp(tone_bias(attack_mental), −1, 1)（权重 (0, +0.4, 0, −0.3)，Q2=A，实测值域 [−0.31, 0.39]）；force = clamp(DA_SNc − baseline_SNc(0.5), 0, 0.5)。tone_bias(t) = Σ_t w_t(role) × (tone_t − baseline_t)；baselines NE 0.3 / DA_VTA 0.4 / DA_SNc 0.5 / 5HT 0.5。
6. **常量引用**：结算路径消费的 9 常量（BaseHitChance/L0EvadeHitPenalty/ForceCap/MotivationCap/DefendPhysicalReduction/SanPenetrationTier1Ratio/Tier1Multiplier/Tier2Ratio/Tier2Multiplier）在 CalibrationConfig——DamageCalculator 不内置数值（构造注入 cal；AC-17 逐常量断言）。BasePhysicalDamage/BaseMentalDamage 经 baseDamage 参数传入（demo callers 传——B6）；DamagePrecision=0.1f 为量化粒度文档常量（Round1 固定 digits=1 / Floor1 分度 10f 与之对应，计算路径不直接消费——实现注释标注；v1.1 审计 C-F4）。

## 六、验收标准

| AC | 验收标准 | 锚点/判定 |
|----|---------|----------|
| AC-1 | 物理基线 | (4, 0, 0, 0, 1.0f, false) + roll<0.75 → damage **4.0f** 逐位、hit true |
| AC-2 | 物理全乘区（一位小数核心锚） | (4, 0, 0.5, 1.0, 1.0f, false) → **10.0f** 逐位（任务issue 实测 #5）；(4, 0, 0.25, 0.5, 0.8f, false) → **5.6f 逐位**（任务issue 实测 #6——整数世界 floor 5 / round 6 全失真，一位小数保留） |
| AC-3 | 量化函数直接锚 | Round1: 1.95f→**2.0f** / 1.5f→**1.5f** / 2.6f→**2.6f** / 1.3f→**1.3f** / 0.75f→**0.8f**；Floor1: 1.95f→**1.9f** / 0.75f→**0.7f** / 3.36f→**3.3f**（全部逐位；Round1 半进位、Floor1 向下） |
| AC-4 | 物理 clamp | (4, 0, 0.7, 0, 1.0f, false) → **6.0f**（force cap 0.5）；(4, 0, 0, 1.5, 1.0f, false) → **8.0f**（motivation cap 1.0）；(4, 0, −0.3, −0.5, 1.0f, false) → **2.0f**（🔧 E-1 裁决 2026-08-14：motivation 下界 −1——沮丧降伤害；(1+0)+(−0.5)=0.5 → 4×0.5=2.0。原锚点 4.0f「负值归零」作废） |
| AC-5 | 命中边界 | SeqRng 注入 roll 序列 [0.0, 0.74, 0.75, 0.74999994, 0.999] → [hit, hit, **miss**, hit, miss]（阈值 0.75f 严格小于且 f32 精确；0.74999994f = 次邻 → hit）；**miss 仍返回完整伤害值**：(4, 0, 0, 0, 1.0f, false) + roll 0.75 → damage **4.0f**、hit **false**（结算与判定解耦——v1.1 审计 K-F2） |
| AC-6 | L0 回避 + 命中率分布 | roll 0.80 → **miss**（无 −10% 时 0.85 阈值将命中——证明修复 #10 无条件生效）；分布：DeterministicRng(固定种子) 直接生成 1000 次 NextFloat 计数 `< 0.75f` 作为期望（独立镜像，不复制引擎代码）→ 同种子下 1000 次 CalcPhysicalDamage 的命中数 == 期望 |
| AC-7 | 防御 −50% 仅物理 | (4, 0, 0.5, 1.0, 1.0f, **true**) → **5.0f**（4×2.5×0.5）；false → 10.0f；CalcMentalDamage 签名**不含** defenderIsDefending（精神无视防御） |
| AC-8 | 武器加成 + baseDamage 参数 | (4, 6, 0, 0, 1.0f, false) → **10.0f**（(4+6)×1.0，武器与装备 §1.1 括号内同等放大）；(1, 0, 0, 0, 1.0f, false) → **1.0f**（baseDamage 参数语义——B6）；**精神消费哨兵**：(3, 0, 0, 1.0f, 1.0f) → san **3.0f**、hp **1.5f**（写死 2f 实现输出 2.0/1.0 必挂——F2 回归防线，Δ审计 INFO 采纳） |
| AC-9 | RNG 消费契约 | 物理：ThrowingRng → InvalidOperationException（必消费证明）；精神：无 rng 参数，正常返回（零消费） |
| AC-10 | 精神基线 | (2, 0, 0, 1.0f, 1.0f) → san **2.0f**、hp **1.0f** 逐位 |
| AC-11 | 精神动机保留（一位小数核心锚） | (2, 0.25, 1, 1.0f, 1.0f) → inner **1.5f**（Round1(2×1.25−1)）、san **1.5f**、hp **0.7f** 逐位（Floor1(0.75)——整数世界 inner floor 1 / round 2 全失真；motivation ≤0.5 失效案例救活） |
| AC-12 | 忍耐 + 最低 1.0 + gate=0 | (2, −0.31, 2, 1.0f, 1.0f) → inner **1.0f**（Round1(−0.62)=−0.6 → max → 1.0）、san 1.0f、hp 0.5f；(2, 0, 2, 1.0f, 1.0f) → 1.0f/0.5f（忍耐 2 抵消基础 2 但最低 1.0）；(2, 0, 0, 1.0f, **0.0f**) → san **0.0f**、hp **0.0f**（max 在 gate 前——plan §4.6 字面，gate=0 → 0 伤害语义） |
| AC-13 | 穿透边界（严格小于 + 互斥 + 最低档救活） | inner 1.0、gate 1.0f：ratio **0.30** → san **1.0f**（不触发）；**0.2999f** → **1.3f**；**0.15** → **1.3f**（tier1 非 tier2）；0.149 → **2.0f**；穿透在最低伤害生效：1.0f×1.3 → **1.3f**（整数世界两法皆 1——一位小数救活） |
| AC-14 | 穿透 + 量化组合 | (2, 0, 0, 0.299, 1.0f) → san **2.6f**、hp **1.3f** 逐位（任务issue 实测 #8/#11——floor1 经 /10f 精确落回 f32(1.3)）；(2, 0.25, 1, 0.299, 1.0f) → san **2.0f**、hp **1.0f** 逐位（inner 1.5×1.3 = f32 精确积 1.94999993f（低于 1.95）→ Round1 **2.0**——.NET 8 全 f32 域：×10f 舍入 19.5f + 0.49999997f → trunc 20 → /10f；本地 runtime 8.0.29 实测 0x40000000，任务issue #17）；(2, 0, 0, 0.149, 0.9f) → san **3.6f**、hp **1.8f**（任务issue #18） |
| AC-15 | 确定性 + 输入不可变 | 同输入重复调用 → 逐位相等（含命中序列——同种子 DeterministicRng）；输入快照不变（值类型）；无 static 可变状态 |
| AC-16 | 异常契约 | 构造 cal null → ArgumentNullException；CalcPhysicalDamage rng null → ArgumentNullException（D12） |
| AC-17 | CalibrationConfig 12 新常量 + 4 模板 | 默认值逐常量断言：4 / 2 / 0.85f / 0.10f / 0.5f / 1.0f / 0.5f / 0.30f / 1.3f / 0.15f / 2.0f / 0.1f（§四 4.1）；PlayerHp 50f / PlayerSan 80f / NpcHp 15f / NpcSan 60f——类型断言机制：**重载绑定探针** `static bool IsFloat(float _) => true; static bool IsFloat(int _) => false;` → 断言 `IsFloat(cal.PlayerHp) == true`（int 字段经重载决议精确匹配 int 重载返回 false——v1.1 审计 C-F2 的「float 赋值编译失败」声明经 Δ审计 refute 实测推翻：int→float 隐式转换使赋值探针无法区分；重载探针本地 dotnet 实测区分有效，属性与字段形态均验证）+ 值逐位断言 |
| AC-18 | L2 类型变更回执 | 现有 types 测试（ParticipantStateTests/CombatEventsTests）在新 float 类型下全绿（int 字面量经泛型推断 `Assert.Equal<float>` 绑定）；新实证：PhysicalDamageEvent.DamageDealt = 5.6f 存读回逐位；CreateDefault(50f, 80f) → Hp **50f** 逐位；types spec（csharp-engine-types）变更日志新增 🔧 修正行指向本 spec 偏差 B5——文件所有权归本工作issue（v1.1 审计 K-F3） |

## 七、本 spec 自检清单

1. **数学公式逐项对照**：物理/精神公式与 核心机制 §4.2/§4.3 + 基础行动设计 §四 + plan §4.6（2026-08-13 Q3=D 更新后）/§六 逐字一致（含 max 在 gate 前、motivation 物理 clamp 精神不 clamp、防御仅物理、L0 回避无条件）。
2. **数值断言全部实测**：全部锚点（10.0/5.6/2.0/1.5/0.7/2.6/1.3/3.6/1.8/阈值 0.75 与次邻）经本地 .NET 8 运行时实测（任务issue 01 实测表第三轮 #15-#19；第一/二轮为设计级仿真——第二轮的双精度委托前提已被审计 F1 推翻）——禁凭记忆写。
3. **计算顺序契约明确**：结合序写死（§五 1）——f32 结合序陷阱预防（speed 结转 #5 先例），AC-2/AC-11/AC-14 锚点即哨兵。
4. **接口注释先行**：构造 + Round1/Floor1 + 两计算方法 XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差标注。
5. **边界值覆盖**：穿透端点 0.30/0.15（严格小于）/ 命中阈值 0.75 与次邻 / clamp 上下界与负值 / gate=0 / 最低 1.0 / 量化 half 案例 1.95/0.75 / 武器加成 6 / 忍耐 2。
6. **确定性**：无 static 可变状态；RNG 仅经 IRng 注入（物理恰好 1 次）；AC-15 实证逐位相等。
7. **偏差声明完整**：B1-B6（§八）在实现注释逐条对应。
8. **常量复用漂移注**：12 新常量带来源注释（§四 4.1）；ScaleMental/ExpectedDamage 引用不重定义声明（§四 4.2）；demo 模板 4 常量类型变更注（§二 2.2）。
9. **类型变更声明完整**：22 字段 int→float 清单（§二 2.2）+ 现有 types 测试回执（AC-18）+ types spec 变更日志 🔧 修正行。

## 八、偏差声明

| # | 偏差 | 设计文档 | 本 spec | 理由 |
|---|------|---------|---------|------|
| B1 | defenderIsDefending 入签名 | plan §4.6 签名未列防御参数；§六 明示「防御 −50%」属结算接线 | CalcPhysicalDamage 第 7 参（D6） | 防御修正属伤害结算职责（基础行动设计 §四「仅物理伤害」）；demo 防御行动必须能结算 |
| B2 | 精神武器不覆盖 | 武器与装备 §1.3「未来有精神伤害型武器时：`(2+weapon_bonus)`」条件式 | 本 feature 精神 baseDamage 走参数（demo 传 2） | 现精神武器走效果型不造成直接伤害（§1.3）——条件式未触发，实现无意义 |
| B3 | 生产者不实现 | plan §六 motivation/force 接线公式 | 公式在 §五 5 文档化；实现归 step 10 接线层（D10） | plan §十一 step 8 范围仅 DamageCalculator；demo 结算由 callers 直传 |
| B4 | 一位小数结算 | 基础行动设计 §四 原「向下取整」+ 整数 HP/SAN 语义 | Round1/Floor1 量化到 0.1（Q3=D）——文档已写回 2026-08-13 | 乘区因子全小数（motivation/force/gate/穿透）——整数取整使 1.5→1 或 2（±33%）、最低档穿透 1.0×1.3→1 失效；0.1 粒度保留全部细粒度效果（实测 #10-#14） |
| B5 | L2 跨 feature 类型变更 22 字段 | csharp-engine-types 已交付（Hp/San/事件数值字段 int） | §二 2.2 清单 int→float（Q3=D） | 一位小数要求状态与事件承载小数；types 零消费者（grep 验证）；AC-18 回执 + types spec 变更日志 🔧 修正行 |
| B6 | baseDamage 参数化 | plan §4.6 公式写死「(4 + weapon_bonus)」 | 公式用 baseDamage 参数（demo 传 BasePhysicalDamage=4，D8） | plan 签名含 baseDamage 参数（公式块与签名不一致）；参数化支撑校准 sweep 与未来成长 |
| B7 | **motivation 下界 −1**（🔧 E-1 裁决 2026-08-14，Grilling #24） | plan §4.6 字面「负值归零」[0,1] | `clamp(motivationMod, −1, MotivationCap)` | 正典仅定义上界 +100%；下界无裁决。tone_bias(attack_physical) 实测下限 −0.52。统一为 [−1,1]：与精神攻击（不 clamp）及 flow 层 producer（csharp-flow spec §5.1 clamp(tone_bias,−1,1)）口径一致——沮丧（低动机）时物理出力下降。AC-4 第三锚点 4.0f→2.0f |

## 参数速查表

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| 物理基础伤害 | BasePhysicalDamage | 4 | 核心机制 §4.2；本 spec §四 |
| 精神基础伤害 | BaseMentalDamage | 2 | 核心机制 §4.3；本 spec §四 |
| 基础命中率 | BaseHitChance | 0.85 | 核心机制 §4.2；本 spec §四 |
| L0 回避命中惩罚 | L0EvadeHitPenalty | 0.10 | 基础行动设计 §二/§三（数值）+ 回合战斗流程 §6.2（自动触发）；本 spec §四 |
| 发力/动机上限 | ForceCap / MotivationCap | 0.5 / 1.0 | 基础行动设计 §四；本 spec §四 |
| 防御物理减伤 | DefendPhysicalReduction | 0.5 | 基础行动设计 §四；本 spec §四 |
| 穿透阈值/倍率 ×2 档 | SanPenetrationTier1/2Ratio、Tier1/2Multiplier | 0.30/1.3、0.15/2.0 | 核心机制 §4.3；本 spec §四 |
| 结算量化粒度 | DamagePrecision | 0.1 | Q3=D；本 spec §四 |
| 忍耐减免 | endurance（参数） | 1（被动）/ 2（主动） | 基础行动设计 §四 |
| 命中阈值（结算值） | BaseHitChance − L0EvadeHitPenalty | 0.75 | 本 spec §三 3.1（实测 #9） |

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-13 | 初稿（§一~§八 + AC-1~18 + B1-B6）；审计前自修正 2 处：AC-14 第二行锚点 f32 复测（1.5×1.3 链积 1.94999993f→san 1.9f/hp 0.9f，原 2.0/1.0 系仿真 float64 泄漏）、Floor1 scale-back ×0.1f→/10f（×0.1f 乘法离格实测）——**其中锚点自修正方向经 v1.1 审计 F1 证实为误修正，已回退** | 任务issue 01（Q1=A/Q2=A/Q3=D 裁决后；设计文档写回 commit 112616c/bddae18） | 全量审计 |
| v1.1 | 2026-08-13 | 修复全量审计 ❌1+⚠️8：①Round1 真实 .NET 8 语义（全 f32 域 `x*=power10→Truncate(x+CopySign(0.49999997f,x))→x/=power10`，非 double 委托——AC-14 第二行锚点回 2.0f/1.0f，本地 runtime 8.0.29 实测）；②精神公式消费 baseDamage（原写死 2f 死参数）；③AC-5 增 miss 伤害锚点；④§二 2.2 xUnit 机制+边界声明；⑤AC-17 类型断言机制；⑥AC-18 承接 types spec 🔧 行；⑦实测标签对齐 # 编号 + 第三轮 #15-#19；⑧L0EvadeHitPenalty 来源修正；⑨§五 6 常量消费措辞 + AC-13 0.2999f + 未定义行为补漏；Δ审计残差清扫：⑩AC-17 重载绑定探针（refute 实测推翻 v1.0 审计 C-F2 赋值声明）、⑪§二 2.2 ≤80+2^24 边界、⑫AC-8 精神 baseDamage≠2 哨兵、⑬SDK→runtime 措辞、⑭map.md 措辞（report.md Δ审计段） | 全量审计 report.md（退回修改） | Δ审计（变更章节 + 半径扩张）——通过 |

---
*创建: 2026-08-13 | 更新: 2026-08-13 | 版本: v1.1*
*关联: [任务issue 01](../../.scratch/csharp-damage/design/issues/01-damage-spec.md), [csharp-engine plan §4.6/§六](../../../csharp-engine/design/plan.md), [核心机制](../../%E8%A7%84%E5%88%99/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md) §4.2/§4.3, [基础行动设计](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E6%93%8D%E4%BD%9C%E5%B1%82/%E5%9F%BA%E7%A1%80%E8%A1%8C%E5%8A%A8%E8%AE%BE%E8%AE%A1.md) §二/§四, [回合战斗流程](../../%E8%A7%84%E5%88%99/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md) §6.2, [运行时状态模型](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) §6.5*
