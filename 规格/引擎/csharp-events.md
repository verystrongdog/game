# EventProcessor — 实现规格

> 战斗事件 → δ（tone 脉冲）+ s（皮层感官输入）派生器。消费 CombatEvents，按 运行时状态模型 §5.5 δ pattern 表 + magnitude 表与 §4.5 s = W_sensory × α 派生每参与者 δ 发射（Σ 聚合后调用 ToneUpdater.Step）与 s 增量（float[69]，Phase 1 注入）。版本: v1.2.2

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | `EventProcessor`（Engine/EventProcessor.cs 新建）；`EventProcessingResult`（Types/EventProcessingResult.cs 新建）；StatusChangeEvent + 3 float 字段（L2 类型变更，Q1=A）；CalibrationConfig + EndurancePassivePenalty=1 [NEW]（Q3=A）；10 个 demo 可触发事件的 δ/s 派生（A1/A2/A4/A5/B1/B2/B4/C1/D1/D2） |
| 不覆盖 | A3/B3（crit）、A6（skill sign(tone_bias[role])——NPC AI §3.3 权重表）、A7（flee）——demo 无事件类型（偏差 B1）；事件生产（DamageCalculator 调用方，step 10）；s 的 Phase 1 注入（step 10）；TurnManager 编排；NpcSalience |
| 前置依赖 | csharp-damage ✅（Physical/MentalDamageEvent 数值字段已 float 化）；csharp-tone ✅（ToneUpdater.Step——未缩放原始 δ + δ_scale=0.3 内部生效）；csharp-data-layer ✅（WsensoryMatrix：RegionIds 即 canonical 69，Matrix 69×6）；csharp-engine-types ✅（CalibrationConfig/ParticipantState/ToneState/事件框架） |
| 阻塞 | step 10 csharp-flow（CombatState/TurnManager 编排层） |

## 二、数据结构

### 2.1 StatusChangeEvent 扩展（L2 跨 feature 类型变更，任务issue Q1=A）

`src/YouAreNotTheFish.Core/Types/CombatEvents.cs`——StatusChangeEvent 追加 3 个 float 字段：

| 字段 | 类型 | 语义 | 来源 |
|------|------|------|------|
| SanBefore | float | 状态变化前 SAN 值（跨越判定的 old） | §5.5 C1 guard：old ≥ 30% |
| SanAfter | float | 状态变化后 SAN 值（new） | §5.5 C1 guard：new < 30% |
| SanMax | float | 状态变化时的 SAN 上限（比率分母） | §5.5 C1：SAN < 30% × SAN_max |

- 仅 StatusChangeEvent 扩展；Physical/MentalDamageEvent 已有 TargetSanBefore/After/Max（types spec §二 2.11），不重复。
- 变更管理走八航四位一体模式：本 spec AC-13 回执 + types spec 变更日志 🔧 修正行（结转）。
- Kind=Downed 时 3 字段语义未定义（D1/D2 只按 teams 分流，不用 SAN 字段）——Downed 事件可不填（默认 0f）。

### 2.2 CalibrationConfig 新增常量

`src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs`——追加 1 个常量：

| 常量 | 类型 | 值 | 来源 |
|------|------|-----|------|
| EndurancePassivePenalty | int | 1 [NEW] | 基础行动设计 §四「忍耐·被动 SAN减免 -1（被动永久）」；A4 expected 公式（Q3=A） |

现有 12 伤害常量与 4 demo 模板不动。

### 2.3 EventProcessingResult（新类型，Types/）

```csharp
public sealed record EventProcessingResult(
    IReadOnlyList<ParticipantState> States,
    IReadOnlyList<float[]> SensoryAccum);
```

- `States`：与输入 states 同长度；每元素 = 输入副本，δ 接收者的 `Tone` 替换为 Step 后值（零 delta 参与者 Tone 与输入逐位相同——偏差 B3）。
- `SensoryAccum[p]`：参与者 p 的 s 增量，长度 69，索引序 = WsensoryMatrix.RegionIds 序（canonical 69，wmatrix 约束 C1 承接）。本调用产生的增量（不含调用前累积——调用方 step 10 负责跨调用累加）。

### 2.4 输入语义与 producer 契约

- `states`：**结算后、δ 注入前**的参与者状态（HP/SAN 已含本轮结算；Tone 为待注入态）。事件字段装客观结果（types spec 决策 D4），EventProcessor 信任事件字段，不重算 HP/SAN 变化。
- `teams`：int[]，`teams[p] == teams[q]` ⇔ p、q 同队（D1/D2 分流用）。
- **PhysicalDamageEvent 契约**：`IncomingDamage == DamageDealt + DamageBlocked`；`Hit=true` → dealt ≥ 0、blocked ≥ 0；`Hit=false` → dealt=0 ∧ blocked == incoming > 0（全额回避——damage calc AC-5「miss 仍返回完整伤害」正是为此：producer 把该值填入 incoming/blocked）。
- **MentalDamageEvent 契约（字段语义，非算术恒等式）**：`TargetSanBefore/TargetSanAfter = 结算前后 SAN 状态实际值（0.1 网格，producer 量化后填写）`；`|TargetSanAfter − TargetSanBefore|` 与 `SanDamage` 在 0.1 网格上一致（**f32 减法不封闭，偏差绝对上界 ≤ 4e-6（终审独立复算：量级 ≥32 处 1 ulp ≈ 3.815e-6，如 (0.1f, 32.2f) 对；601×601 全网格 (32.2f, 32.1f) 对 307 ulp ≈ 2.287e-6 为**相对最大**（按结果量级折算）非绝对最大，约 6% 合法对超过 3e-6——故取 4e-6 绝对上界）；对 B4 m = |Δ|/SanMax 与 0.01 阈值无行为影响（m 偏差 ≤ 8e-8，SanMax ≥ 30 时）**）。**EventProcessor 只消费差值对（TargetSanAfter − TargetSanBefore）与 TargetSanMax 分母（B4 公式），不消费 SanDamage，不验算三字段间的逐位恒等式**——f32 减法在 0.1 网格上不封闭（实测 0.1f − 0.3f = −0.20000002 ≠ −0.2f；审计 W1 穷举 14616 组离格反例），逐位恒等式对合法 producer 输入不保真。
- **StatusChangeEvent 契约**：Panic 的 SanBefore/SanAfter 为跨越前后实际值；被动 SAN_max 变化（ΔSAN=0）→ SanBefore==SanAfter。
- **契约违反 → 未定义行为**（NaN/∞ 传播可能——§五 5.3 emit 判据对 NaN 有天然防御、∞ 有显式防御，仅防御 m 通道；States 中毒不在本 feature 防务范围）。
- `Round` 字段不参与派生（标注用）。

## 三、接口定义

### 3.1 EventProcessor

```csharp
namespace YouAreNotTheFish.Core.Engine;

public sealed class EventProcessor
{
    public EventProcessor(WsensoryMatrix wsensory, CalibrationConfig cal);
    public EventProcessingResult ProcessEvents(
        IReadOnlyList<CombatEvent> events,
        IReadOnlyList<ParticipantState> states,
        IReadOnlyList<int> teams);
}
```

**职责**：按 §五 派生规则处理一个窗口的全部事件——每参与者 Σδ（事件序）→ 恰好一次 ToneUpdater.Step（零向量不调用）→ 打包 States 副本；s 按 §五 5.4 累积 → SensoryAccum 增量。

**异常契约**：

| 条件 | 异常 |
|------|------|
| 构造：wsensory null | ArgumentNullException(nameof(wsensory)) |
| 构造：cal null | ArgumentNullException(nameof(cal)) |
| events null / states null / teams null | ArgumentNullException |
| teams.Count != states.Count | ArgumentException |
| 任一事件 ActorId 或 TargetId ∉ [0, states.Count) | ArgumentException（含 0 参与者时任何事件） |

**数据层保证（不重复验证）**：`WsensoryMatrix.RegionIds.Count == 69`（canonical 69，wmatrix 约束 C1 承接——审计 I-4；wmatrix 已验证闭合，EventProcessor 不做运行时形状校验）。

**确定性**：无 static 可变状态、无内部缓存；同输入（含事件序）→ 逐位同输出（AC-12）。

**未定义行为**：违反 §二 2.4 契约的字段组合；states/teams 元素为 null（NRE）；类型集封闭于 5 个具体子类（PhysicalDamageEvent / MentalDamageEvent / StatusChangeEvent / HealEvent / LinkGrowthEvent——审计 I-6）。

### 3.2 处理流程（伪码，实现逐字遵循）

```
1. 验证（§3.1 异常契约）
2. δSum[p] = (0,0,0,0)，sAcc[p] = float[69] 全零
3. for ev in events（输入序）:
       if ev is PhysicalDamageEvent ph:   派生 A1/A2（攻击者）+ A5/B1/B2（承受者，三路分区 Q2=A）
       if ev is MentalDamageEvent me:     派生 A4（攻击者）+ B4（承受者）
       if ev is StatusChangeEvent st:     派生 C1（guard 全条件）/ D1,D2（Downed 广播）
       if ev is HealEvent / LinkGrowthEvent: no-op（偏差注）
   （派生规则见 §五 5.2；δ 与 s 按各自 emit 判据独立累加）
4. for p in 0..states.Count-1（升序）:
       if δSum[p] 非全零: states'[p] = states[p] with { Tone = ToneUpdater.Step(states[p].Tone, δSum[p], cal) }
       else: states'[p] = states[p]（副本，Tone 引用原值）
5. return EventProcessingResult(states', sAcc)
```

## 四、枚举与常量

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| 忍耐被动 SAN 减免 | EndurancePassivePenalty | 1 [NEW] | CalibrationConfig（本 spec §二 2.2） |
| A1 expected 基础伤害 | ExpectedDamage | 4（step 2 已交付，**消费不重定义**） | CalibrationConfig（§五 5.3.1 分母，审计 W-a） |
| A4 expected 基础伤害 | BaseMentalDamage | 2（step 2 已交付，**消费不重定义**） | CalibrationConfig（§五 5.3.2，审计 W-b） |
| C1 恐慌阈值 | — | 0.30f（公式字面量，不消费常量） | §五 5.5.1（**漂移注**：与 SanPenetrationTier1Ratio=0.30f 同值不同义——穿透比率 vs 恐慌阈值，各自来源 核心机制 §4.3 / 运行时状态模型 §5.5，不互引，审计 I-1） |
| δ 全局缩放 | δ_scale | 0.3（ToneUpdater 内部） | 运行时状态模型 §5.2（**不重定义**） |
| tone τ / baseline | τ=(0.5,0.3,0.8,1.5)；baseline=(0.3,0.4,0.5,0.5) | ToneUpdater 内部 | csharp-tone spec §三（**不重定义**） |

## 五、交叉引用约束（事件派生规则）

### 5.1 总则

- 战斗事件 e = (δ, s) 绑定角色实例；同角色同回合多事件加法叠加 `δ = Σ δ_i`（§5.5）；δ 实时注入（本 feature 即注入点），s 打包到下一 Phase 1（本 feature 只产出增量）。
- δ = pattern_δ × m，m ∈ [0, ∞)；α = pattern_α × m_α；A 类 m_α = 1.0（自身行动感官完整），B/C/D 类 m_α = m（§5.5）。
- δ pattern 与 α pattern 见下表（14 事件表中 demo 可触发的 10 行，逐字取自 运行时状态模型 §5.5 δ pattern 表 + §4.5 α pattern 表）。

### 5.2 事件 → 派生规则表（10 demo 事件）

| 事件 | 视角 | 条件 | 事件号 | δ pattern (NE,VTA,SNc,5HT) | m 公式 | α pattern (视,听,躯,痛,社,语) | m_α |
|------|------|------|--------|---------------------------|--------|------------------------------|-----|
| PhysicalDamageEvent | 攻击者 | Hit | A1 | (0,+1,+1,0) | §5.3.1 | (1,0,1,0,0,0) | 1.0 |
| PhysicalDamageEvent | 攻击者 | ¬Hit | A2 | (0,−1,0,0) | 0（固定，偏差 B2） | (1,0,1,0,0,0) | 1.0 |
| PhysicalDamageEvent | 承受者 | Hit ∧ blocked>0 | A5 | (0,0,0,+1) | §5.3.3 | (0,0,1,0,0,0) | 1.0 |
| PhysicalDamageEvent | 承受者 | Hit ∧ blocked=0 | B1 | (+1,0,0,−1) | §5.3.4 | (1,0,1,1,0,0) | m |
| PhysicalDamageEvent | 承受者 | ¬Hit | B2 | (0,0,0,+1) | §5.3.3 | (1,0,1,0,0,0) | m |
| MentalDamageEvent | 攻击者 | 恒 | A4 | (0,+1,0,0) | §5.3.2 | (0,0,0,0,1,1) | 1.0 |
| MentalDamageEvent | 承受者 | 恒 | B4 | (+1,0,0,−1) | §5.3.5 | (0,0,0,1,1,1) | m |
| StatusChangeEvent | 自身 | Kind=Panic ∧ Entered ∧ guard 全条件（§5.5.1） | C1 | (+1,0,0,−1) | 1.0 | (0,0,0,1,0,0) | 1.0 |
| StatusChangeEvent | 观察者 p | Kind=Downed ∧ Entered ∧ p≠ActorId ∧ states[p].Hp>0 ∧ teams[p]==teams[ActorId] | D1 | (+1,−1,0,−1) | 1.0 | (1,1,0,0,1,0) | 1.0 |
| StatusChangeEvent | 观察者 p | 同上 ∧ teams[p]≠teams[ActorId] | D2 | (0,+1,0,+1) | 1.0 | (1,1,0,0,1,0) | 1.0 |

- **三路分区（Q2=A，sign-off 结转 #2 复核）**：Hit∧blocked>0 → 承受者**只**收 A5（不收 B1）；Hit∧blocked=0 → B1；¬Hit → B2。blocked>0 即「防御生效」判别（demo d=0.5：incoming>0 时 blocked=incoming×0.5>0 恒成立——任务issue 实测 #10）。
- **A5 属 A 类（m_α=1.0，审计 W-c）**：A5 在 δ pattern 表 A 块（行动者：我的行动结果——防御成功），正典 §4.5「A 类事件 m_α = 1.0」→ s 通道恒发；**δ 的 m 仍按 §5.3.3（blocked/incoming）**，两通道 magnitude 独立。
- 攻击者的 A1/A2 与承受者的 A5/B1/B2 独立派生（同事件两视角，types spec 决策 D4）。
- **承受者派生不豁免 HP=0（审计 W-e，v1.2 枚举补全）**：承受者派生（**A5/B1/B2/B4/C1 一律**）不设存活守卫——击杀窗口（伤害事件与 Downed 事件同批）中被击杀者照收 B1 δ 与 s（§5.5 无存活守卫声明，D 注仅约束广播方向；A5 的 δ m=blocked/incoming 与 s m_α=1.0 均与 HP 无关）。豁免仅存在于 D1/D2 广播（p ≠ ActorId ∧ states[p].Hp > 0，§5.5.2）。击杀窗口锚点见 AC-15。
- StatusChangeEvent(Kind=Panic, Entered=false)、StatusChangeEvent(Kind=Downed, Entered=false)、HealEvent、LinkGrowthEvent → 不产生任何 δ/s（§5.5 未定义脱离方向；Heal/LinkGrowth 无表行）。
- 多 Downed 事件 → 各自广播，观察者 Σ 自然叠加。

### 5.3 m 公式（f32，计算序写死）

#### 5.3.1 A1：`DamageDealt / (float)cal.ExpectedDamage`

- 分子为事件字段，分母消费已交付常量 `cal.ExpectedDamage = 4`（CalibrationConfig.cs:33，用途注即「A1 m 公式分母」——审计 W-a：B3 撤销，无偏差）。demo 空手 BaseDamage=4 与常量同值，行为不变。
- 0.1 网格量化后的 DamageDealt（csharp-damage B4 交付）直接参与除法，不二次量化。

#### 5.3.2 A4：`SanDamage / expected`，expected = `(float)cal.BaseMentalDamage * (1f + MotivationMod) - (float)cal.EndurancePassivePenalty`

- expected 表达式与 CalcMentalDamage.raw 同构：`(float)cal.BaseMentalDamage * (1f + mot)` 先乘后减（f32 序，damage spec §五 1 同款）。常量消费：`BaseMentalDamage=2`（CalibrationConfig.cs:59，step 2 已交付——审计 W-b，修复「写死 2f 使参数失效」缺陷类，damage spec §五 6 纪律）+ `EndurancePassivePenalty=1` [NEW]（本 spec §二 2.2）。
- actual = SanDamage（事件字段——含 gate/穿透的 0.1 网格结算产物；expected 用基础公式、actual 用结算产物——与 A1 口径一致，任务issue D4）。
- mot=−1 → expected = −1 → m < 0 → δ skip；s 仍发（A 类 m_α=1.0 恒发）。
- **mot=−0.5 → expected = 0 → m = +∞（SanDamage ≥ 1.0 恒，damage 最低伤害兜底）→ !float.IsInfinity 显式防御 skip（审计 W-j）**；s 仍发（m_α=1.0）。

#### 5.3.3 A5/B2：`DamageBlocked / IncomingDamage`

- B2 在 producer 契约（§二 2.4：¬Hit → blocked==incoming>0）下恒 m=1.0。
- 契约违反 incoming=0 → 0/0=NaN → emit 判据天然 skip；incoming=0 ∧ blocked>0 → +∞ → 显式 ∞ 防御 skip（偏差 B4）。
- **通道限定（复查审计 info）**：本节的 skip 表述均指 **δ 通道**。A5 属 A 类——s 通道按 §5.3.7 独立判定（m_α=1.0 恒发，与 δ 的 skip 无关）；B2 属 B 类（m_α=m）→ 双通道同 skip。勿按本节字面对 A5 得出「双通道 skip」（AC-8 修正段同语义）。

#### 5.3.4 B1：`MathF.Abs(TargetHpAfter - TargetHpBefore) / TargetHpMax`

- After − Before 序写死（Abs 精确）。

#### 5.3.5 B4：`MathF.Abs(TargetSanAfter - TargetSanBefore) / TargetSanMax`

- 序同 5.3.4。

#### 5.3.6 emit 判据（δ 通道）

- δ 通道 emit ⇔ `m >= 0.01f && !float.IsInfinity(m)`（§5.5「m<0.01 跳过 emit」+ ∞ 防御；NaN 比较为 false 天然落 skip——任务issue 实测 #14）。
- 不 emit → 该事件对该参与者的 δ 贡献为零向量。

#### 5.3.7 emit 判据（s 通道）

- s 通道 emit ⇔ m_α ≥ 0.01f 且有限。A 类 m_α=1.0 恒发（**独立于 δ 通道**——A2 miss、A4 mot=−1 的 δ 被跳过时 s 照发；§5.5「自身行动的感官输入总是完整的，情绪冲击走 δ」的落地，任务issue D1）；B/C/D 类 m_α = m → 判据与 δ 通道相同。

### 5.4 s 计算

- α = pattern_α × m_α（f32，逐模态：pattern=0 → 0f；pattern=1 → m_α）。
- 单事件 s 向量：`s_event[j] = Σ_{k: W[j][k]=1} α[k]`（W ∈ {0,1} → 乘为精确；加 f32 左折叠、k 升序）。
- 跨事件累积：`sAcc[p][j] += s_event[j]`（事件序、j 升序——f32 结合序契约）。
- 无 clip（§4.5：双模态节点可达 2.0，WC sigmoid 自然饱和）。
- 单模态节点 s_j ∈ [0,1]；双模态可达 2.0（任务issue 实测 #3）。

### 5.5 特殊规则

#### 5.5.1 C1 guard（全条件，Q1=A 处理器实现）

`Kind == Panic ∧ Entered ∧ SanBefore > SanAfter ∧ SanBefore >= 0.30f * SanMax ∧ SanAfter < 0.30f * SanMax` → emit C1。

- 三条件：ΔSAN<0、old ≥ 30%（含端，§5.5 字面）、new < 30%（严格）。
- 比率阈值表达式 `0.30f * SanMax`（f32 乘法；实测 0.30f×60f == 18f 逐位、0.30f×80f == 24f 逐位——任务issue 探针）。
- **被动 SAN_max 变化不触发**：SanBefore == SanAfter → ΔSAN=0 → 不发（plan §十 测试行字面）。Entered=false → 不发。

#### 5.5.2 D1/D2 广播

- 条件：`Kind == Downed ∧ Entered`；对每个 p：`p != ActorId ∧ states[p].Hp > 0` → 按 teams 分流 D1/D2（§5.2 表）。
- 倒者排除显式化（p ≠ ActorId）——防御 stale 事件（契约：producer 在 HP≤0 结算完成后即时发 Downed，§5.5 D 注）。
- **观察者判定语义（审计 W-h 锁定）**：以**输入 states 的 Hp** 判定（本窗口结算后快照），非累加中值——同一窗口内倒下的参与者对其后事件按 Hp=0 排除。
- **多倒下者**：同一窗口多个 Downed 事件各自广播，观察者收多份 δ，Σ 后一次 Step（AC-7 多倒下者行锚点）。
- 「即时到所有 HP>0」：本 feature 对全部满足条件的参与者立即调用 Step（含窗口已过者——§5.5 D 注「排在 Phase 4 后面的人的 δ 实时收到冲击」）。

#### 5.5.3 Step 调用语义

- 每参与者恰好一次（Σδ 后）；Σδ 全零 → **不调用**（tone 不变，非「δ=0 衰减一步」——衰减是 step 10 Phase 1 的职责，非事件驱动）。
- 参与者升序调用（确定性文档化；参与者间无依赖，序无数学影响）。
- 传入 ToneUpdater.Step 的 δ 为**未缩放原始值**（δ_scale=0.3 由 ToneUpdater 内部施加——csharp-tone spec §三）；锚点值（δ=+1 → VTA 0.68929785）即锁定此契约：若处理器预缩放，锚点必错位。

## 六、验收标准

| AC | 验收标准 | 锚点/断言（全部来自任务issue 实测表 + 探针，2026-08-13） |
|----|---------|------|
| AC-1 | 构造与参数验证 | wsensory/cal null → ArgumentNullException；events/states/teams null → ArgumentNullException；teams.Count≠states.Count → ArgumentException；ActorId/TargetId ∉ [0,Count) → ArgumentException（含负与越界） |
| AC-2 | 物理命中无防御：攻击者 A1 + 承受者 B1 | 事件(4,0,0,0,1, dealt=4, blocked=0, incoming=4, Hit=true, Hp 15→10, HpMax=15)：攻击者 m=4/4=1.0 → tone (0.3, 0.68929785, 0.71404856, 0.5)；承受者 m=0.33333334 → tone (0.3864665, 0.4, 0.5, 0.4513417)；s[Postcentral] 攻击者=1.0、承受者=0.6666667 |
| AC-3 | 三路分区（Q2=A） | defended hit（dealt=2, blocked=2, incoming=4, Hit=true）→ 承受者仅 A5：5HT 0.57298744、NE/DA_VTA/DA_SNc 与基线逐位相同（无 B1 混入）；blocked=0 hit → B1（同 AC-2 承受者）；¬Hit（dealt=0, blocked=4, incoming=4）→ B2 m=1.0：5HT 0.6459749 |
| AC-4 | A2（miss）：δ 跳过、s 恒发 | miss 事件（Hit=false, dealt=0, blocked=4, incoming=4）→ 攻击者 tone 与输入逐位相同（零向量不调用 Step）；s[Postcentral]=1.0（m_α=1.0 恒发——D1） |
| AC-5 | A4 + B4 | A4（SanDamage=1.0, mot=0）→ expected=1.0 → m=1.0 → (0.3, 0.68929785, 0.5, 0.5)；A4（SanDamage=2.6, **mot=0.5**）→ expected=2×1.5−1=2.0 → m=1.3 → (0.3, 0.77608716, 0.5, 0.5)（**E1 修正：mot 必须 0.5 才得 expected=2.0；mot=0 时 expected=1.0 → m=2.6 ≠ 1.3**）；A4（mot=−1）→ expected=−1 → m<0 → δ skip、s 发；A4（mot=−0.5）→ expected=0 → m=+∞ → δ skip（!IsInfinity）、s 发（W-j）；B4（San 60→58）→ m=0.033333335 → (0.30864665, 0.4, 0.5, 0.49513417)；A4 mot=0.25 → expected=1.5（表达式锚） |
| AC-6 | C1 guard 全条件 | SanBefore=19, SanAfter=17.9, SanMax=60 → C1：tone (0.5593994, 0.4, 0.5, 0.35402513) + s[Postcentral]=1.0；SanAfter=18（恰好 30%，18f<18f=False）→ 不发；SanBefore=18, SanAfter=17.9（old 含端）→ 发；被动变化（SanBefore==SanAfter=18, Entered=true）→ 不发；Entered=false → 不发；SanBefore<SanAfter（治疗）→ 不发 |
| AC-7 | D1/D2 广播 | **批次构成（v1.2 限定）**：本 AC 全部场景批次仅含 StatusChangeEvent(Downed) 事件，不含伤害事件——「p0 tone 不变」仅在此构成下成立；击杀窗口（伤害事件+Downed 同批）见 AC-15。**3 人 teams=[1,**1**,2]**（E2 修正：p1 与 p0 同队才收 D1；原 [1,2,2] 使 p1/p2 均 team 2 → 双收 D2，「p1→D1」不可复现），p0 倒下（Hp=0, Downed Entered=true, ActorId=0）：p1（同队）→ D1 (0.5593994, 0.110702194, 0.5, 0.35402513)；p2（异队）→ D2 (0.3, 0.68929785, 0.5, 0.6459749)；p0（倒者）tone 不变、s 全零；Hp=0 的非倒者也不收；Downed Entered=false → 全不发；多倒下者（W-h）：p0、p1 同批倒下 → p2 收 D2×2 → Σδ=(0,2,0,2) → 一次 Step (0.3, 0.9785956, 0.5, 0.79194975)；双 D1（**v1.2 修正：3 人 [1,1,2] 下不可构造——team 1 倒下后无存活同队观察者；改 4 人 teams=[1,1,1,2]**，p0、p1 倒下 → p2（team 1 存活）收 D1×2 → Σδ=(2,−2,0,−2) → (0.81879884, 0, 0.5, 0.20805025)；p3（team 2）收 D2×2 → (0.3, 0.9785956, 0.5, 0.79194975)） |
| AC-8 | m<0.01 skip 双通道 | B4（\|ΔSAN\|=0.5, SanMax=60 → m=0.008333334，**I-3 修正：0.5f/60f 最短往返**）→ 承受者 tone 不变、s 全零；B1（Δ=0.1, HP_max=10 → m=0.01f 逐位）→ 发；B1（Δ=0.05, HP_max=10 → m=0.005）→ 不发；A2（m=0）→ δ 不发 s 发（AC-4）；**NaN/∞ 契约违反按事件类限定（W-k + v1.2 修正）**：B/C/D 类事件（如 B2 incoming=0 → NaN）→ 双通道全 skip；A 类事件（A1 dealt=NaN、**A5 incoming=0 ∧ blocked>0 → m=+∞——v1.2 修正：A5 属 A 类，与 A1 同侧，不再归 B/C/D**）→ δ skip（NaN 天然 / ∞ 显式防御 B4）但 s 照发（m_α=1.0 恒发，有限——与 §5.3.7 A 类独立判定一致） |
| AC-9 | Σ 聚合后单次 Step | B1(m=0.33333334)+B4(m=0.033333335) 同承受者 → (0.39511314, 0.4, 0.5, 0.44647586)；A1(m=1.0)+A4(m=1.0) 同攻击者 → (0.3, 0.9785956, 0.71404856, 0.5)；C1+B1 同承受者 → (0.6458659, 0.4, 0.5, 0.3053668) 且 s[Postcentral]=1.6666667（C1 s 1.0 + B1 s 0.6666667 累加——**W-f 补 s 断言**，探针实测）；B1×2（同事件两次）→ δSum=(0.66666669,0,0,−0.66666669) → 一次 Step (0.47293293, 0.4, 0.5, 0.4026834)（**E3 修正：原锚点 (0.39816847,…) 是逐事件两次 Step 的第二步，与「Σδ 后恰好一次 Step」（§5.5.3/决策 D2）矛盾——审计独立复算 + 本地探针逐位复现**） |
| AC-10 | s 打包（W×α + 积累序） | A1 → 15 非零行、s[Postcentral]=1.0；**B2 → 15 行、s[Postcentral]=1.0（m_α=m=1.0 契约恒等 → 与 A1 同 α pattern，但走承受者 B2 路径——W-f 补行）**；D1 → 26 非零行、s[SuperiorTemporal]=2.0（双模态）、max=2.0；B1(m=5/15) → 20 行、s[Postcentral]=0.6666667（soma+pain 双模态）、max=0.6666667；B4(m=2/60) → 27 行、s[Postcentral]=0.033333335、max=0.06666667；C1 → 7 行、s[Postcentral]=1.0；A5 → 4 行、s[Postcentral]=**1.0**、max=**1.0**（**W-c 修正：A 类 m_α=1.0 恒发——原 0.5 是 m_α=m 的旧口径；δ 的 m 仍按 §5.3.3**）；零行哨兵（subcortical fid，测试从数据推导零行集合，如 Amygdala）；长度 69、RegionIds 序 |
| AC-11 | HealEvent/LinkGrowthEvent no-op | **拆两行（W-i）**：① 纯批次（只含 Heal/LinkGrowth 事件）→ 全部参与者 tone 与输入逐位相同、SensoryAccum 全零；② 混入批次（Heal 混入 A1 发射批次）→ A1 照发（攻击者 tone 与 AC-2 同值）、Heal 贡献零（无叠加、无干扰） |
| AC-12 | 确定性 + 输入不可变 | 同输入（含事件序）连续 5 次输出逐位一致；states/events/teams 元素不被修改（输入引用元素 Tone 断言不变）；输出 States 与输入不同引用 |
| AC-13 | L2 类型变更回执 | StatusChangeEvent 3 新 float 字段存读回逐位（5.6f）；CalibrationConfig.EndurancePassivePenalty == 1（int）；现有 types 测试零改动在全量 test run 中通过（csharp-damage AC-18 模式）；types spec 变更日志 🔧 行（结转 #1） |
| AC-14 | 空事件列表 | States 副本逐字段等于输入（Tone 逐位）；SensoryAccum 每元素 float[69] 全零 |
| AC-15 | 击杀窗口（W-e 锚点，v1.2 新增，v1.2.1 修正） | **参与者（v1.2.1 声明，复查审计 F1）**：3 人 teams=[1,1,2]；p0 = 被击杀者（伤害事件 TargetId + Downed 事件 ActorId）、**p1 = 伤害事件攻击者（ActorId=1——p1 收 A1，m=15/4=3.75 → VTA/SNc clip，不在本 AC 断言范围）**、p2 = 旁观者。批次 = PhysicalDamageEvent（dealt=15, Hp 15→0, HpMax=15, Hit=true, blocked=0）+ StatusChangeEvent(Downed, Entered=true) 同批：**p0 只收 B1** → m=15/15=1.0 → δ=(1,0,0,−1) → tone (0.5593994, 0.4, 0.5, 0.35402513)（探针实测，probe-v1.2.md Q1，同 C1 pattern 同值）+ s 20 行、s[Postcentral]=2.0（probe-v1.2.md Q2/Q4，soma+pain 双模态 × m_α=1.0）；p0 不另收 D 广播（p≠ActorId 排除）；p1 收 A1+D1、p2 收 D2（分流逻辑 §5.5.2，tone 值不在本 AC 断言——攻击者双视角超出范围）——**实现若对 B1/B2/B4/C1 误加 HP>0 存活守卫则本 AC 必红** |

## 七、本 spec 自检清单

1. **数学公式逐项对照**：δ pattern 10 行 × m 公式 6 式 × α pattern 10 行逐字对照 运行时状态模型 §5.5（δ pattern 表 + magnitude 表 + 注入时序）+ §4.5（α pattern 表 + s = W×α + 值域）——实现注释逐项标注来源。
2. **数值断言全部实测**：全部锚点来自任务issue 01 实测表第三轮（#15-#25，runtime 8.0.29 真实 ToneUpdater）+ 补充探针（C1 阈值边界 / s 锚点 / m 边界 f32 语义 / Σ 聚合）——测试文件不凭记忆写任何锚点。
3. **计算顺序契约明确**：Σ 事件序（Σδ 后恰好一次 Step，B1×2 锚点即哨兵——E3 教训）、s 模态升序与节点升序、m 公式逐式 f32 序（5.3.1-5.3.5）——写死并在实现标注；AC-2/AC-9/AC-10 锚点全绿即哨兵在位。
4. **接口注释先行**：EventProcessor 类头 + 构造 + ProcessEvents + EventProcessingResult 字段 XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差标注（B1-B5 类头逐条对照表）。
5. **边界值覆盖**：C1 双端边界（old=18 含端 / new=18 严格）、m=0.01 逐位边界与 0.005 跳过、miss 的 blocked=incoming 契约事件、空列表、越界索引、Entered=false、倒者排除、NaN/∞ 防御、**击杀窗口（AC-15：被击杀者照收 B1 δ/s，防误加存活守卫）**。
6. **确定性**：无 static 可变状态；参与者 Step 升序；同输入逐位同输出实证。
7. **偏差声明完整**：B1-B5 在实现注释逐条对应（§八，v1.1 重编号——B3 撤销）。
8. **常量复用漂移注**：EndurancePassivePenalty 唯一新常量（来源注释 基础行动设计 §四）；δ_scale/τ/baseline/ExpectedDamage/BaseMentalDamage 引用不重定义声明（§四）；A1 分母消费 cal.ExpectedDamage、A4 消费 cal.BaseMentalDamage（§5.3.1/§5.3.2，审计 W-a/W-b）。
9. **类型变更声明完整**：StatusChangeEvent 3 字段对照 §二 2.1 表逐字段核对；AC-13 回执（现有 types 测试零改动通过）；types spec 变更日志 🔧 修正行（结转 #1）。

## 八、偏差声明

| # | 偏差 | 理由与处置 |
|----|------|-----------|
| B1 | 14 事件表中 4 行不落地（A3/B3 crit、A6 skill、A7 flee） | demo 无事件类型（无暴击/技能/逃跑——plan §一 范围表）；A6 的 sign(tone_bias[role]) 权重表（NPC AI §3.3）留 step 10+ skill 系统；实现类头 + 注释标注。**顺延声明（W-g）**：plan §十测试行「A6 sign 固定符号」1 条随 A6 一并顺延至 skill 系统实装（sign-off 记录在案，非遗漏） |
| B2 | A2 m 恒 0（不读 DamageDealt 字段） | §5.5「actual/expected（≈0 → 跳过 emit）」的落地：miss 无实际伤害。**理由改写（I-2）**：契约内（¬Hit → dealt=0）读字段行为等价于恒 0；恒 0 的真实价值是防御 producer 误填——damage calc AC-5「miss 仍返回完整伤害 4.0f」，若 producer 误填到 dealt 将得 m=4/4=1.0 → miss 得正 δ（错误）。恒 0 使 miss 的 δ 语义与设计一致（无伤害无情绪脉冲） |
| B3 | 输出 States 副本含全部参与者（非仅 δ 接收者） | 调用方一步替换；零 delta 参与者 Tone 与输入逐位相同（记录断言，非仅"引用相同"）。（v1.1 重编号：原 B4，B3「A1 分母事件字段」已撤销——ExpectedDamage 已交付，见 §5.3.1，W-a） |
| B4 | m 的 ∞ 显式防御（emit 判据含 `!float.IsInfinity`） | 契约违反（incoming=0 ∧ blocked>0）→ blocked/0=+∞ → Step 输出 NaN 毒化；NaN 已被 `>=` 天然排除、∞ 需显式排除（探针实测 1f/0f ≥ 0.01f == True）。有效输入行为不变。（v1.1 重编号：原 B5） |
| B5 | A4 expected 允许 ≤ 0（m ≤ 0 或 +∞ → δ skip） | §5.5 m ∈ [0,∞) 未覆盖非正 expected；mot=−1 → expected=−1 → m<0 落 skip（与 m<0.01 同通道）；mot=−0.5 → expected=0 → m=+∞（SanDamage ≥ 1.0 恒）→ B4 的 !IsInfinity 防御 skip（W-j 扩展：+∞ 为合法输入下的合法路径，非契约违反）。s 均仍发（m_α=1.0）。（v1.1 重编号：原 B6） |

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-13 | 初稿 | 任务issue 01 | 全量审计 |
| v1.1 | 2026-08-14 | 审计 v1.0 修复：E1（AC-5 mot=0.5）、E2（AC-7 teams=[1,1,2]）、E3（AC-9 B1×2 Σ 锚点）3❌；W-a（A1 消费 ExpectedDamage，B3 撤销）、W-b（A4 消费 BaseMentalDamage）、W-c（A5 m_α=1.0）、W-d（2.4 字段语义契约）、W-e（承受者 HP=0 不豁免声明）、W-f（AC-9 s 断言 + AC-10 B2 行）、W-g（A6 顺延声明）、W-h（多倒下者锚点 + 判定语义）、W-i（AC-11 拆两行）、W-j（B6→B5 +∞ 路径）、W-k（AC-8 NaN/∞ 限定事件类）11⚠️；I-1（§四 C1 漂移注）、I-2（B2 理由改写）、I-3（0.008333334）、I-5（表头改「默认值」）、I-6（5 事件子类）5ℹ️；I-4 处置 = 数据层保证声明 + NRE 入未定义行为（v1.2 修正记录：非「异常表补行」）。偏差重编号 B4-B6→B3-B5。全部锚点本地探针实测 | 审计 v1.0（3❌ + 11⚠️ + 7ℹ️） | Δ审计 |
| v1.2 | 2026-08-14 | Δ审计（3 专家 + 对抗验证，11 发现 → 10 CONFIRMED）修复：AC-8 A5 +∞ 移出 B/C/D 归 A 类（W-k × W-c 交互副作用——δ skip、s 照发）；AC-7 批次构成限定 + 双 D1 改 4 人 teams=[1,1,1,2]（3 人下不可构造）；新增 AC-15 击杀窗口锚点（W-e 补全——B1 m=1.0 → (0.5593994, 0.4, 0.5, 0.35402513)、s[Postcentral]=2.0 探针实测）；§5.2 豁免枚举补 A5；§2.4 消费字段措辞精确化（差值对 + SanMax 分母）；变更日志 v1.1 行失实修正 | Δ审计发现（1❌ + 2⚠️ + 1ℹ️） | 复查审计 |
| v1.2.1 | 2026-08-14 | 复查审计（2 专家，6 发现去重 4）修复：AC-15 参与者声明补全（F1——伤害事件 ActorId=p1 显式化，p0 只收 B1；原「p0 为 ActorId/TargetId」字面读为 A1 也作用于 p0 → δSum 污染）；§2.4 ±1ulp 界修正（F2——全网格穷举最大 307 ulp，改偏差绝对量 ≤3e-6）；§5.3.3 通道限定声明（info——skip 表述仅指 δ 通道，A5 s 恒发）；AC-15 探针出处补 probe-v1.2.md（F3） | 复查审计发现（1❌ + 1⚠️ + 2ℹ️） | 终审确认 |
| v1.2.2 | 2026-08-14 | 终审（1 专家独立复算）残差清扫：§2.4 偏差上界 3e-6 → **4e-6**（原值被独立复算推翻——307 ulp ≈ 2.287e-6 为相对最大非绝对最大；量级 ≥32 处 1 ulp ≈ 3.815e-6，约 6% 合法对超 3e-6；m 偏差 ≤ 1e-7 → 8e-8）；AC-15 补探针文件显式引用（probe-v1.2.md Q1/Q2/Q4） | 终审发现（1⚠️ + 1ℹ️） | sign-off |

---
*创建: 2026-08-13 | 更新: 2026-08-14 | 版本: v1.2.2*
*关联: [任务issue 01](../../设计归档/grilling/csharp-events/design/issues/01-events-spec.md), [plan §4.7](csharp-engine-roadmap.md), [运行时状态模型 §5.5](../../%E8%A7%84%E5%88%99/%E6%8A%80%E8%83%BD%E6%A0%91%E7%B3%BB%E7%BB%9F/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md), [types spec §二 2.11](csharp-engine-types.md)*
