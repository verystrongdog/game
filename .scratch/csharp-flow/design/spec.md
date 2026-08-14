# csharp-flow — 实现规格

> L3 实体（CombatState）+ L4 流程（TurnManager 五阶段管线 + ActionResolver 行动分发 + NpcSalience demo 行动选择）编排层。消费全部 L2 引擎组件（WcDynamics/ToneUpdater/CstcGating/SpeedScoreCalculator/DamageCalculator/EventProcessor），把回合战斗流程 §四 五阶段管线落地为可运行引擎。版本: v1.0

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | `CombatState`（Entity/CombatState.cs 新建）；`TurnManager`（Flow/TurnManager.cs 新建）；`ActionResolver`（Flow/ActionResolver.cs 新建）；`IActionProvider`（Flow/IActionProvider.cs 新建）；`NpcActionProvider`（Flow/NpcActionProvider.cs 新建——demo 适配）；`NpcSalience`（Engine/NpcSalience.cs 新建，plan §4.8）；事件生产（DamageCalculator 调用方——csharp-events spec §一 明示落本 step）；SAN 阈值行为（<30% 恐慌 C1 / <15% 崩溃并入恐慌档 / =0 随机行动）；响应窗口 stub（接口保留 + 注释引用设计章节） |
| 不覆盖 | 空间系统（12 格/控制区/AOE/视线/借机攻击——回合战斗流程 §十，原型期推迟）；逃跑/投降（§8.2-8.3）；HP↔SAN 互转（核心机制 §5.3）；响应窗口 link 交互全文（L1 期待/L3 精准/L5 叙事重构——demo 无 link）；技能树/LinkState 全量（demo 仅 m_default）；情境 archetype 选择（demo 不消费 situation archetype，s 由事件驱动）；NPC Affordance Competition 全量（demo 硬编码 3 基础行动，plan §4.8 [NEW] 标注） |
| 前置依赖 | csharp-data-layer ✅ / csharp-engine-types ✅ / csharp-wmatrix ✅ / csharp-wc-dynamics ✅ / csharp-tone ✅ / csharp-cstc ✅ / csharp-speed ✅ / csharp-damage ✅ / csharp-events ✅（228/228） |
| 阻塞 | step 11 csharp-console（Console harness——玩家 IActionProvider 实现）；step 12 csharp-smoke（Smoke 集成测试） |

## 二、数据结构与决策

### 2.1 决策记录（2026-08-14 用户裁决，任务issue Q1-Q4）

| Q | 决策 | 内容 |
|---|------|------|
| Q1 | IActionProvider 接口 | Phase 4 行动来源抽象：`IActionProvider.GetAction(p, state, ctx) → CombatAction`。demo 两个实现：NpcActionProvider（适配 NpcSalience）+ 玩家实现（step 11 console）。引擎层零 UI 耦合，测试可注入固定行动 |
| Q2 | <15% 崩溃并入恐慌档 | demo 无链路可随机触发——数值行为并入 <30% 档（T_SAN +0.30 与 C1 事件路径相同）；文档化标注（本 spec §5.4），不新增状态字段 |
| Q3 | 防御持续到下次自己窗口 | 声明防御 → IsDefending=true + DefendCd=1；下回合自己窗口开始时：IsDefending=false + CD tick（1→0）——暴露一轮（回合战斗流程 §9.1「跨过完整窗口周期」语义） |
| Q4 | 跨越才发 Panic | TurnManager 在 SAN 扣减后检测 `old ≥ 30% ∧ new < 30%` 才生产 StatusChangeEvent(Panic, Entered=true, SanBefore/After/Max)；EventProcessor 的 C1 guard 保留为防御性二次校验 |

### 2.2 CombatState（Entity/）

可变战斗状态（plan §5.1）——内部持有参与者数组（record 替换语义），对外只读：

```csharp
public sealed class CombatState
{
    public IReadOnlyList<ParticipantState> Participants { get; }
    public int Round { get; }
    public IReadOnlyList<TurnResult> History { get; }
    public float[][] SPending { get; }   // per-participant float[69]：s 累计槽（Phase 4 累加、Phase 1 注入后清零）
}
```

- **初始化**：`CombatState.Create(IReadOnlyList<ParticipantState> initial, GameData data, CalibrationConfig cal)`——WC 状态置静息不动点（内部跑 30 回合静息 trace：tone=baseline、s=0，对齐 csharp-tone AC-15 方法与 运行时状态模型 §7.3「遭遇进入战斗时 WC 状态为静息不动点」；Gurney 从 0 起步——§7.3 实测首回合即收敛）；tone 取初始值（demo = baseline）；HP/SAN 由调用方提供。
- **Apply 方法**（实体自己 Apply 引擎产出——框架 D1）：
  - `ApplyDamage(int p, float hpAfter, float sanAfter)`——HP/SAN 设为事件字段结算后值（**事件字段搬运语义**：ActionResolver 已按 state 当前值推算结算后值，TurnManager 搬运，无二次计算）
  - `ApplyTone(int p, ToneState tone)`——替换 tone（EventProcessor 输出）
  - `ApplyGurney(int p, WcState a, GurneyState gurney, GateState gates, LoopSalience salience)`——Phase 1 全链替换（WC/CSTC 输出）
  - `ApplyDefense(int p, bool defending, int cd)`——防御状态与 CD 设置
  - `TickWindow(int p)`——自己窗口开始：`DefendCd = max(0, DefendCd − 1)`；`EnduranceActiveCd` 同（demo 未用，保持对称）；**IsDefending = false**（Q3=A）
  - `AccumulateS(int p, float[] s)`——s 累计到 SPending（EventProcessor SensoryAccum 累加）
- **确定性**：无 static 可变状态；同输入序列 → 同终态。

### 2.3 行动与响应

- `CombatAction`：types 已交付（M1/Broca 双通道 + Order + IsValidChannelUsage）。`(null, null)` 空声明合法（对应等待语义——types spec §三 3.5）。
- **响应窗口 stub**（plan §一 范围表）：`IResponseResolver` 接口保留（`Resolve(CombatAction declared, CombatState state, CombatContext ctx) → IReadOnlyList<CombatEvent>` 响应产出的调整事件），demo 提供 `NoopResponseResolver`（恒空列表）。接口注释引用 回合战斗流程 §六（L0 回避自动触发已在 DamageCalculator 内生效——命中率 −10%；忍耐主动/L4 读意图/L5 叙事重构 B 留后续链路 feature）。**L0 回避不占响应窗口**（免费自动，damage calc 已消费）。

## 三、接口定义

### 3.1 IActionProvider（Flow/）

```csharp
public interface IActionProvider
{
    CombatAction GetAction(int participantIndex, CombatState state, CombatContext ctx);
}
```

- 职责：为参与者 p 声明行动。demo 实现：`NpcActionProvider`（Flow/，适配 NpcSalience——固定 Softmax 杂兵模板）；玩家实现由 step 11 console 提供。
- 异常契约：state/ctx null → ArgumentNullException；participantIndex ∉ [0, Count) → ArgumentOutOfRangeException。
- 确定性：NpcActionProvider 消费 ctx.Rng（Softmax 抽样）——同种子同输出；玩家实现无此约束（外部输入）。

### 3.2 NpcSalience（Engine/，plan §4.8 demo 版）

```csharp
public static class NpcSalience
{
    public static CombatAction SelectAction(ParticipantState state, CombatContext ctx);
}
```

- 职责：demo 硬编码 3 基础行动候选集的 salience 竞争选择（Cisek 2007 + GPR 2001 的 demo 落地，plan §4.8 [NEW]——正式 skill 系统接入后替换）。
- 候选行动 → 皮层节点 + role/gate 映射（plan §4.8 表，[NEW]）：

| 行动 | 皮层节点 | role / gate |
|------|----------|-------------|
| physical_attack | Precentral（M1，核心机制 §4.2）+ Putamen | attack_physical / somatic |
| mental_attack | rostralmiddlefrontal（dlPFC）+ parsopercularis（Broca）+ caudalanteriorcingulate（ACC）（§4.3） | attack_mental / cognitive |
| defend | Amygdala + insula（威胁检测，运行时状态模型 §6.5 理由行） | defend / limbic |

- Salience 公式（NPC AI §3.2/§3.3）：`Salience(skill) = mean(a_j, j ∈ skill.cortical_nodes) × gate_bonus(role) × (1 + tone_bias(role))`
  - `gate_bonus(role)`：attack_physical → gates.Somatic；attack_mental → gates.Cognitive；defend → gates.Limbic（perceive/support bypass=1.0——demo 无此二行动）
  - `tone_bias(role) = Σ_t w_t(role) × (tone_t − baseline_t)`（NPC AI §3.3 权重表，§四）
- **目标选择**（[NEW] demo 简化）：第一个异队参与者（teams[p] ≠ teams[state 内查询者]）——1v1 场景下即对方。多目标 argmax 竞争留 Affordance Competition 全量。
- **选择**（plan §4.8）：demo 固定 Softmax（杂兵模板）——`P(skill) = exp(Salience/T) / Σ exp(...)`，`T = T_base + T_SAN`；T_SAN 分段（NPC AI §3.4 正典）：`SAN% ≥ 60% → +0`（最确定） / `30-59% → +0.10`（中等噪声） / `< 30% → +0.30`（恐慌高噪声） / `= 0 → T=∞ 均匀随机`（思维断裂——直接均匀抽，不经 Softmax，防 exp(0/∞) 数值问题）。抽样消费 ctx.Rng。
- 空声明（等待）不产出：三候选必有 winner（Softmax 全正概率）——demo 无等待语义（Q：NpcSalience 不产生 (null,null)——玩家可）。

### 3.3 ActionResolver（Flow/）

```csharp
public sealed class ActionResolver
{
    public ActionResolver(GameData data, CalibrationConfig cal);
    public IReadOnlyList<CombatEvent> Resolve(CombatAction action, CombatState state, CombatContext ctx);
}
```

- 职责：Phase 4 声明→响应→结算 dispatch（plan §5.3）。**纯函数**：只读 state，产事件列表，不修改实体状态（框架 D1——状态应用由 TurnManager 完成）。事件字段装客观结果（types D4）。
- 内部流程（每通道按 Order 序）：
  1. 响应窗口：`_responseResolver.Resolve(action, state, ctx)`（demo = Noop，恒空）
  2. M1 通道（ActionSlot）：PhysicalAttack → 物理结算；MentalAttack → 精神结算；Defend → 无事件（防御标记——TurnManager 读取 action 应用 IsDefending/CD，§5.2）
  3. Broca 通道（ActionSlot）：MentalAttack → 精神结算（同 2 逻辑）
- 异常契约：构造 null → ArgumentNullException；Resolve 参数 null → ArgumentNullException；action 非法（IsValidChannelUsage false，如 Broca=Defend）→ ArgumentException。
- 确定性：消费 ctx.Rng（物理命中判定）；同输入同种子 → 同事件序列。

### 3.4 TurnManager（Flow/）

```csharp
public sealed class TurnManager
{
    public TurnManager(GameData data, CalibrationConfig cal, IActionProvider actionProvider);
    public TurnResult StepRound(CombatState state, CombatContext ctx);
}
```

- 职责：五阶段回合管线编排（plan §5.2 + 回合战斗流程 §四 + 运行时状态模型 §7.1），每步调 L2 组件 + state.Apply。产 TurnResult（Round + 全部事件 + 快照）。
- 异常契约：构造 null → ArgumentNullException；StepRound 参数 null → ArgumentNullException。
- 确定性：同种子同输入（含 provider 行动序列）→ 逐位同 TurnResult。

### 3.5 处理流程（伪码，实现逐字遵循）

```
StepRound(state, ctx):
  round = state.Round + 1
  # Phase 1: 情境更新（运行时状态模型 §7.1 步骤 2-5）
  for p in 0..Count-1:
      b = CorticalBias.Compute(tone[p], data)                     # 步骤 2
      a' = WcDynamics.Step(a[p], b, SPending[p], W)               # 步骤 3（s=上回合累计）
      state.SPending[p] 清零                                      # 注入后清零
      (gurney', gates', salience') = CstcGating.Step(a', tone[p], gurney[p])   # 步骤 4-5
      state.ApplyGurney(p, a', gurney', gates', salience')
  # 步骤 1 tone 继承：demo 无跨窗口残留（δ 已在 Phase 4 实时注入——csharp-events）→ 无操作，文档化

  # Phase 2: 继承（连续状态原样带入，不递减 CD）→ 无操作

  # Phase 3: 速度重算
  scores[p] = speedScore.ComputeScore(
      speedScore.ComputeComponents(a[p], salience[p], gurney[p], isDefending[p]), weights)
  order = TurnOrderBuilder.BuildOrder(scores, ctx.Rng)

  # Phase 4: 按序执行
  events = []
  for p in order:
      state.TickWindow(p)                                         # 0. 窗口开始：CD tick + IsDefending=false（Q3）
      action = provider.GetAction(p, state, ctx)                  # 1. 行动选择
      evs = resolver.Resolve(action, state, ctx)                  # 2-4. 声明→响应(stub)→结算
      state.ApplyEvents(evs)                                      #     HP/SAN = 事件字段（搬运）
      if action 含 M1=Defend: state.ApplyDefense(p, true, 1)      #     防御标记（§5.2）
      result = eventProcessor.ProcessEvents(evs, state.Participants, teams)  # 5. δ/s 派生
      for p2: state.ApplyTone(p2, result.States[p2].Tone)
      for p2: state.AccumulateS(p2, result.SensoryAccum[p2])
      events.AddRange(evs)
      if state.Participants[p].Hp <= 0:                            # 6. HP=0 → 移除队列（跳过剩余窗口）
          downedEv = StatusChangeEvent(round, p, p) { Kind=Downed, Entered=true }
          dResult = eventProcessor.ProcessEvents([downedEv], state.Participants, teams)  # D 广播实时
          ApplyTone/AccumulateS 同上
          events.Add(downedEv)
          break

  # Phase 5: 回合收束
  endReason = CheckEnd(state, round)   # 一方全灭 / 回合上限（§5.5）
  turnResult = new TurnResult(round, events, state.Participants)
  state.History.Add(turnResult)
  return turnResult
```

## 四、枚举与常量

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| 回合上限 | MaxRounds | 50 [NEW] | CalibrationConfig（§5.5 结束条件，待校准） |
| Softmax 温度基线 | T_base | 0.15（已交付） | CalibrationConfig.TBase（NPC AI §3.4，**不重定义**） |
| 察觉回落阈值 | PerceptionThreshold | 0.15（已交付） | CalibrationConfig（回合战斗流程 §3.3，**不重定义**） |
| M1 持续占用惩罚 | M1SustainPenalty | −0.1（已交付） | CalibrationConfig（回合战斗流程 §3.3，**不重定义**） |
| 防御 CD | DefendCd 初值 | 1（语义） | 基础行动设计 §四（Q3=A 落地） |
| tone_bias 权重 | w_t(role) | 见 §五 5.3 表 | NPC AI §3.3 表（attack_physical/attack_mental/defend 三行） |

## 五、交叉引用约束（管线规则）

### 5.1 事件生产（ActionResolver 内，csharp-events spec §一 承接）

**物理攻击**（baseDamage=4 空手 [NEW] demo、weaponBonus=0）：

```
gate_bonus = gates.Somatic
motivation_mod = clamp(tone_bias(attack_physical), −1, +1)   （plan §六，cap +100% 对齐核心机制 §4.2）
force_mod = clamp(DA_SNc − baseline_SNc, 0, 0.5)              （plan §六，cap +50%）
(defenderIsDefending = target.IsDefending)
(damage, hit) = DamageCalculator.CalcPhysicalDamage(4, 0, force_mod, motivation_mod, gate_bonus, defenderIsDefending, rng)
→ PhysicalDamageEvent:
    Hit = hit；BaseDamage = 4；WeaponBonus = 0；ForceMod = force_mod；MotivationMod = motivation_mod；GateBonus = gate_bonus
    DamageDealt = damage
    DamageBlocked = defenderIsDefending ? damage : 0f          （减免 50% → 减免量 = 造成量，[NEW] demo 简化）
    IncomingDamage = DamageDealt + DamageBlocked               （f32 加法——保证 §2.4 契约恒等）
    TargetHpBefore = 当前 Hp；TargetHpAfter = Round1(Hp − damage)；TargetHpMax = HpMax
```

**精神攻击**（baseDamage=2、endurance=EndurancePassivePenalty=1）：

```
gate_bonus = gates.Cognitive
motivation_mod = clamp(tone_bias(attack_mental), −1, +1)      （plan §六：语言攻击动机 = DA_VTA 认知动机 + 5HT 去抑制）
enemySanRatio = target.San / target.SanMax
(sanDamage, hpDamage) = DamageCalculator.CalcMentalDamage(2, motivation_mod, 1, enemySanRatio, gate_bonus)
→ MentalDamageEvent:
    SanDamage = sanDamage；HpDamage = hpDamage；MotivationMod = motivation_mod；GateBonus = gate_bonus
    TargetSanBefore = 当前 San；TargetSanAfter = Round1(San − sanDamage)；TargetSanMax = SanMax
    TargetHpBefore = 当前 Hp；TargetHpAfter = Round1(Hp − hpDamage)；TargetHpMax = HpMax
```

**状态事件**（TurnManager 生产，Q4=A）：
- **Panic**：每次 SAN 扣减后检测跨越（`old ≥ 0.30f × SanMax ∧ new < 0.30f × SanMax`——含端/严格同 events spec §5.5.1）→ `StatusChangeEvent(round, p, p) { Kind=Panic, Entered=true, SanBefore=old, SanAfter=new, SanMax }`。EventProcessor C1 guard 保留为二次校验（双保险）。
- **Downed**：HP ≤ 0 结算完成 → `StatusChangeEvent(round, p, p) { Kind=Downed, Entered=true }`（§5.5 D 注「即时」——Phase 4 步骤 6 当场处理）。

### 5.2 防御（Q3=A + 基础行动设计 §四 + 回合战斗流程 §7/§9.1）

- 声明（M1=Defend）→ `ApplyDefense(p, true, 1)`：IsDefending=true、DefendCd=1（防御持续到下次自己窗口开始）。
- 下次自己窗口开始（TickWindow）：DefendCd 1→0、IsDefending=false——**暴露一轮**（§9.1「跨过完整窗口周期」）。
- 防御生效：目标 IsDefending → DamageCalculator 减 50%（仅物理——damage calc 已实现，AC-7 锁定签名）。
- 防御期间 Broca 可用（回合战斗流程 §7.4）——CombatAction 可 (M1=Defend, Broca=精神攻击)。
- 连续防御：CD=1 时下轮防御声明被拒？——demo：声明防御无条件设置 CD=1（重复防御导致 DefendCd 重置为 1，非叠加——防御本身无 CD 门槛，只有解除后暴露一轮）。**文档化 [NEW] demo 简化**：防御可连续声明（CD 重置），无「CD 未满不可防御」门槛。

### 5.3 tone_bias 权重表（NPC AI §3.3，demo 三行动行）

| 行为角色 | NE | DA_VTA | DA_SNc | 5HT |
|---------|----|--------|--------|-----|
| attack_physical | 0 | +0.3 | +0.5 | −0.3 |
| attack_mental | 0 | +0.4 | 0 | −0.3 |
| defend | +0.4 | −0.2 | 0 | +0.4 |

`tone_bias(role) = Σ_t w_t(role) × (tone_t − baseline_t)`——tone 处于基线时 tone_bias=0（NPC AI §3.3）。baseline = (0.3, 0.4, 0.5, 0.5)（§5.4）。

### 5.4 SAN 阈值行为（核心机制 §5 + plan §5.2，Q2=A）

| SAN | 行为 | demo 落地 |
|-----|------|----------|
| < 30% | 恐慌——C1 事件（跨越时）+ 切换恐慌行为表 | C1：Q4=A 跨越检测生产；行为表：T_SAN +0.30（NpcSalience） |
| < 15% | 崩溃边缘——可能随机触发不应激活的链路 | **并入恐慌档**（Q2=A）：数值行为同 <30% 档（T_SAN +0.30）；无链路可随机触发——文档化标注，不新增状态字段 |
| = 0 | 完全随机行为 | T=∞ 均匀随机（NpcSalience——不经 Softmax，防数值问题） |

### 5.5 结束条件（Phase 5）

- 一方全灭：所有参与者 Hp ≤ 0（同队判据 teams）→ EndReason=TeamDefeated
- 回合上限：round ≥ MaxRounds（50 [NEW]）→ EndReason=MaxRounds
- 否则 → EndReason=None（继续）。TurnResult 携带 endReason 字段（新增——见 §六 AC-9 或扩展 TurnResult？）。

**TurnResult 扩展决策 [NEW]**：TurnResult 是 types 已交付 record（Round/Events/ParticipantSnapshots）。结束原因需要暴露给调用方（console/smoke 判断战斗结束）。方案：TurnManager 在 StepRound 后由调用方检查 state（无新字段）vs TurnResult 加字段（L2 类型变更）。**推荐：不加字段**——调用方检查 `state.History.Last()` 后自算结束条件（或 TurnManager 提供 `IsOver(state)` 静态检查）。console 轮询 `!IsOver`。避免跨 feature 类型变更。

## 六、验收标准

| AC | 验收标准 | 锚点/断言 |
|----|---------|-----------|
| AC-1 | CombatState 创建 + 静息初始化 | Create 后：WC = 静息不动点（30 回合 trace 与 M1 实测一致：active 48 节点 ∈ [0.535174, 0.771229]，排除节点 σ(b_j)；对齐 csharp-tone AC-15 方法）；tone = 输入值；SPending 全零；Round=0；History 空 |
| AC-2 | Phase 1 情境更新全链 | 单步 StepRound 后：a 更新（WcDynamics 输出）、gurney/gates/salience 更新（CstcGating 输出）、SPending 已清零 |
| AC-3 | Phase 3 速度重算 | 同 RNG 种子 → order 确定性；首回合（静息状态）三分量 = 静息值（SpeedScoreCalculator 首回合无特判——静息输入自然给出）；防御中执行分含 M1SustainPenalty |
| AC-4 | 物理攻击完整链 | 注入固定行动（IActionProvider）：攻击者 → PhysicalDamageEvent 字段全填（契约 IncomingDamage == Dealt + Blocked 逐位）；HP = TargetHpAfter（搬运）；攻击者 tone VTA 上升（A1 δ）；承受者 tone NE↑5HT↓（B1）；s[Postcentral] > 0 |
| AC-5 | 精神攻击完整链 | 注入 mental_attack：MentalDamageEvent 字段全填；SAN = TargetSanAfter；HP 含 HpDamage 成分；A4/B4 tone 模式 |
| AC-6 | 防御生命周期 | 声明 Defend → IsDefending=true + DefendCd=1；目标防御中物理伤害减半（DamageDealt 精确值）；下回合自己窗口开始 → IsDefending=false + DefendCd=0；防御中 Broca 精神攻击可用 |
| AC-7 | Panic 跨越事件生产（Q4=A） | SAN 扣减跨越 30%（old≥18 ∧ new<18，SanMax=60）→ StatusChangeEvent(Panic) 生产 + C1 事件（tone 变化）；未跨越（new=18 严格 / 治疗 / ΔSAN=0）→ 不生产 |
| AC-8 | Downed 生产 + 队列移除 | HP=0 结算 → StatusChangeEvent(Downed) 生产 + D 广播实时生效（存活观察者 tone 变化）；剩余队列参与者跳过（其窗口不执行） |
| AC-9 | 结束条件 | 一方全灭 → 战斗结束（IsOver 检查）；回合上限 50 → 结束 |
| AC-10 | TurnResult 打包 | Round 正确；Events 全量（含 Phase 4 全部 + Downed）；ParticipantSnapshots = 回合末状态；History 追加 |
| AC-11 | NpcSalience | 3 候选 salience 计算（节点均值 × gate × (1+tone_bias)）；tone_bias 按权重表（attack_physical (0,+0.3,+0.5,−0.3)）；Softmax 归一（ΣP=1）；T_SAN 分段（≥60%/30-60%/<30% 对应 0/+0.10/+0.30）；SAN=0 均匀随机（同种子确定性）；目标 = 第一个异队参与者 |
| AC-12 | 确定性 | 同种子同输入（含 provider 序列）连续 5 次 StepRound 逐位同输出；输入不突变（state 引用不可变字段、ctx 只读） |
| AC-13 | 异常契约 | 构造/参数 null → ArgumentNullException；非法 action（Broca=Defend）→ ArgumentException；p ∉ [0, Count) → ArgumentOutOfRangeException |

## 七、本 spec 自检清单

1. **数学公式逐项对照**：Salience/tone_bias/T_SAN 分段逐字对照 NPC AI §3.2-3.4；五阶段管线对照 plan §5.2 + 回合战斗流程 §四 + 运行时状态模型 §7.1；接线表对照 plan §六。
2. **数值断言全部实测**：flow 层锚点（静息不动点、tone 方向、精确伤害值）来自组件级已验证输出 + 本地探针实测——测试不凭记忆写锚点。
3. **计算顺序契约明确**：Phase 1-5 顺序写死（伪码逐字遵循）；Apply 搬运语义（事件字段为权威，无二次计算）；Downed 实时处理（Phase 4 步骤 6）。
4. **接口注释先行**：CombatState/TurnManager/ActionResolver/NpcSalience/IActionProvider XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差标注。
5. **边界值覆盖**：SAN 跨越双端（old=18 含端/new=18 严格）、防御 CD 生命周期、HP=0 队列移除、回合上限、空声明 (null,null)、SAN=0 均匀随机。
6. **确定性**：无 static 可变状态；RNG 仅经 ctx 注入；同种子实证。
7. **偏差声明完整**：demo 简化项（NpcSalience 硬编码行动/单目标、防御连续声明、blocked=dealt 简化、MaxRounds [NEW]）逐条标注。
8. **常量复用漂移注**：T_base/PerceptionThreshold/M1SustainPenalty/DefendCd 引用不重定义；MaxRounds 唯一新常量 [NEW]。
9. **类型变更声明**：本 step 无 L2 类型变更（TurnResult 不扩展——§5.5 决策）。

## 八、偏差声明

| # | 偏差 | 理由与处置 |
|----|------|-----------|
| B1 | NpcSalience 硬编码 3 基础行动候选集（plan §4.8 [NEW]） | 正式 skill 系统接入后替换；demo 验证引擎核心 |
| B2 | NpcSalience 目标选择 = 第一个异队参与者（[NEW] demo 简化） | 1v1 场景即对方；多目标 argmax 竞争留 Affordance Competition 全量 |
| B3 | 防御可连续声明（CD 重置非门槛）（[NEW] demo 简化） | 回合战斗流程 §7.3 连续防御细节待链路系统实装时细化 |
| B4 | 物理 DamageBlocked = dealt（防御时）（[NEW] demo 简化） | 减免 50% → 减免量 = 造成量（数学恒等）；IncomingDamage = dealt + blocked 契约恒等（f32 加法） |
| B5 | 响应窗口 stub（IResponseResolver + Noop） | plan §一 范围表：响应窗口 link 交互全文留链路 feature；L0 回避已在 damage calc 内生效 |
| B6 | TurnResult 不扩展结束原因字段 | 调用方检查 IsOver（静态方法）；避免跨 feature 类型变更 |
| B7 | CombatState 初始化内部跑 30 回合静息 trace | 对齐运行时状态模型 §7.3「遭遇进入战斗时 WC=静息不动点」；M1 实测方法复用 |

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-14 | 初稿 | 任务issue 01 | 全量审计 |

---
*创建: 2026-08-14 | 更新: 2026-08-14 | 版本: v1.0*
*关联: [任务issue 01](issues/01-flow-spec.md), [plan §五](../../../csharp-engine/design/plan.md), [回合战斗流程](../../../../规则/回合战斗流程.md), [NPC AI 行为模型](../../../../规则/技能树系统/NPC%20AI%20行为模型.md), [运行时状态模型](../../../../规则/技能树系统/运行时状态模型.md)*
