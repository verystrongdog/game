# csharp-flow — 实现规格

> L3 实体（CombatState）+ L4 流程（TurnManager 五阶段管线 + ActionResolver 行动分发 + NpcSalience demo 行动选择）编排层。消费全部 L2 引擎组件（WcDynamics/ToneUpdater/CstcGating/SpeedScoreCalculator/DamageCalculator/EventProcessor），把回合战斗流程 §四 五阶段管线落地为可运行引擎。版本: v1.2

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
    public IReadOnlyList<int> Teams { get; }       // teams[p] == teams[q] ⇔ p、q 同队（审计 E1 修复：D1/D2 分流与结束条件的数据源）
    public int Round { get; internal set; }        // internal set——TurnManager 每回合递增（审计 E6 修复）
    public IReadOnlyList<TurnResult> History { get; }
    // 追加方法（内部——Δ审计 Δ-04 修复：IReadOnlyList 无 Add，伪码 state.History.Add 需显式 API）
    internal void AddTurnResult(TurnResult result);
    public IReadOnlyList<float[]> SPending { get; } // per-participant float[69]：s 累计槽（Phase 4 累加、Phase 1 注入后清零；IReadOnlyList 集合只读——审计 I3 修复）
    public IReadOnlyList<LoopSalience> Salience { get; } // CSTC 环路 salience 存储槽（ApplyGurney 参数落点——Phase 3 速度重算与 console 渲染消费；🔧 2026-08-14 console 终审：Δ-C05 跨 spec 声明补记——实现已交付）
}
```

- **初始化**：`CombatState.Create(IReadOnlyList<ParticipantState> initial, IReadOnlyList<int> teams, GameData data, CalibrationConfig cal)`——teams.Count == initial.Count（否则 ArgumentException）；WC 状态置静息不动点（内部跑 30 回合静息 trace：**tone=baseline**、s=0，对齐 csharp-tone AC-15 方法与 运行时状态模型 §7.3「遭遇进入战斗时 WC 状态为静息不动点」；Gurney 从 0 起步——§7.3 实测首回合即收敛）；**初始 tone 必须为 baseline**（(0.3,0.4,0.5,0.5)——否则不动点不匹配，声明为未定义行为，NPC AI §4.1 性格偏移留全量）；HP/SAN 由调用方提供。
- **Apply 方法**（实体自己 Apply 引擎产出——框架 D1）：
  - `ApplyDamage(int p, float hpAfter, float sanAfter)`——HP/SAN 设为事件字段结算后值（**事件字段搬运语义**：ActionResolver 已按链式基准推算结算后值，TurnManager 搬运，无二次计算）
  - `ApplyTone(int p, ToneState tone)`——替换 tone（EventProcessor 输出）
  - `ApplyGurney(int p, WcState a, GurneyState gurney, GateState gates, LoopSalience salience)`——Phase 1 全链替换（WC/CSTC 输出）
  - `ApplyDefense(int p, bool defending, int cd)`——防御状态与 CD 设置
  - `TickWindow(int p)`——自己窗口开始：`DefendCd = max(0, DefendCd − 1)`；`EnduranceActiveCd` 同（demo 未用，保持对称）；**IsDefending = false**（Q3=A）
  - `AccumulateS(int p, float[] s)`——s 累计到 SPending（EventProcessor SensoryAccum 累加）
  - `ApplyEvents(IReadOnlyList<CombatEvent> events)`——**按事件序搬运** DamageEvent 的 TargetHpAfter/TargetSanAfter 到 Participants（审计 W4/W7 修复：补 API 清单缺失项；链式基准下事件字段已自洽）
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
    public static CombatAction SelectAction(int selfIndex, CombatState state, CombatContext ctx);
}
```

- 职责：demo 硬编码 3 基础行动候选集的 salience 竞争选择（Cisek 2007 + GPR 2001 的 demo 落地，plan §4.8 [NEW]——正式 skill 系统接入后替换）。**签名修复（审计 E3/F6）：selfIndex + state（含 Teams/全体参与者）——目标选择与 salience 计算所需数据全部在位**。
- 候选行动 → 节点 + role/gate 映射（plan §4.8 表 + **审计 W5 修复：subcortical 节点用环路代理**——salience 只取有 WC a(t) 的节点，Putamen/Amygdala 用代理值）：

| 行动 | 通道（审计 W5 补声明） | salience 节点 | role / gate |
|------|----------------------|---------------|-------------|
| physical_attack | M1 | Precentral（WC a）+ **Putamen 代理 = a_SD1_somatic**（plan §十三-4 同款代理——Putamen 无 WC a） | attack_physical / somatic |
| mental_attack | Broca | rostralmiddlefrontal + parsopercularis + caudalanteriorcingulate（均 WC 节点） | attack_mental / cognitive |
| defend | M1 | **Insula + Amygdala（均 WC 节点直读 a(t)——v1.2 修正（Δ审计 F2/Δ-03）：Amygdala 是 48 W-active 节点之一（运行时状态模型 §4.1），有真实 a(t)；原 c_loop_limbic 代理会造成 limbic CI 双重计数** | defend / limbic |

- Salience 公式（NPC AI §3.2/§3.3）：`Salience(skill) = mean(节点值) × gate_bonus(role) × (1 + tone_bias(role))`
  - `gate_bonus(role)`：attack_physical → gates.Somatic；attack_mental → gates.Cognitive；defend → gates.Limbic（perceive/support bypass=1.0——demo 无此二行动）
  - `tone_bias(role) = Σ_t w_t(role) × (tone_t − baseline_t)`（NPC AI §3.3 权重表，§四；baseline=(0.3,0.4,0.5,0.5) 常量——**demo 简化**，NPC AI §4.1 7 参数化性格偏移留全量）
- **目标选择**（[NEW] demo 简化）：第一个异队参与者（`Teams[p] ≠ Teams[selfIndex]`）——1v1 场景下即对方。多目标 argmax 竞争留 Affordance Competition 全量。
- **选择**（plan §4.8）：demo 固定 Softmax（杂兵模板）——`P(skill) = exp(Salience/T) / Σ exp(...)`，`T = T_base + T_SAN`；T_SAN 分段（NPC AI §3.4 正典，**判定序显式化——v1.2 修正（Δ审计 F4/Δ-08）：`SAN == 0` 必须先于 `<30%` 判定，否则 =0 落入 +0.30 档**）：`if SAN == 0 → T=∞ 均匀随机`（思维断裂——直接均匀抽，不经 Softmax，防 exp(0/∞) 数值问题）/ `else if SAN < 30% → +0.30`（恐慌高噪声） / `else if SAN < 60% → +0.10`（中等噪声） / `else → +0`（最确定）。抽样消费 ctx.Rng。
- 空声明（等待）不产出：三候选必有 winner（Softmax 全正概率）——demo 无等待语义（Q：NpcSalience 不产生 (null,null)——玩家可）。

### 3.3 ActionResolver（Flow/）

```csharp
public sealed class ActionResolver
{
    public ActionResolver(GameData data, CalibrationConfig cal);
    public IReadOnlyList<CombatEvent> Resolve(int actorIndex, CombatAction action, CombatState state, CombatContext ctx);
}
```

- 职责：Phase 4 声明→响应→结算 dispatch（plan §5.3）。**纯函数**：只读 state，产事件列表，不修改实体状态（框架 D1——状态应用由 TurnManager 完成）。事件字段装客观结果（types D4）。**签名（审计 E2）：actorIndex 显式传入（CombatEvent 构造器强制 ActorId/Round；round 取 state.Round——StepRound 顶部已递增（E6），v1.2 修正：原「+1」为 Phase 末递增时代的残留，Δ审计 F1 双口径矛盾）**。
- **链式基准（审计 E8/W3 修复）**：内部维护局部 hp/san 游标（初值 = state 当前值）；每通道结算后游标更新（`hp = Round1(hp − dealt)`），**后事件的 Before/After 字段基于前事件后的游标**——双通道同目标（M1 物理 + Broca 精神）链式正确，终态 = 两伤害叠加。resolver 仍为纯函数（局部状态不落实体）。
- **通道-动作配对校验（审计 W9/W4 修复）**：回合战斗流程 §2.1 定义通道归属——M1 ∈ {PhysicalAttack, Defend}、Broca ∈ {MentalAttack}。违规（M1=MentalAttack、Broca=PhysicalAttack/Defend）→ ArgumentException（比静默未定义好；IsValidChannelUsage 只锁 Broca=Defend，本校验为完整配对锁）。
- 内部流程（每通道按 Order 序）：
  1. 响应窗口：`_responseResolver.Resolve(action, state, ctx)`（demo = Noop，恒空）
  2. M1 通道（ActionSlot）：PhysicalAttack → 物理结算（§5.1）；Defend → 无事件（防御标记——TurnManager 读取 action 应用 IsDefending/CD，§5.2）
  3. Broca 通道（ActionSlot）：MentalAttack → 精神结算（§5.1）
- 异常契约：构造 null → ArgumentNullException；Resolve 参数 null → ArgumentNullException；actorIndex ∉ [0, Count) → ArgumentOutOfRangeException；通道-动作配对违规 → ArgumentException。
- 确定性：消费 ctx.Rng（物理命中判定）；同输入同种子 → 同事件序列。

### 3.4 TurnManager（Flow/）

```csharp
public sealed class TurnManager
{
    public TurnManager(GameData data, CalibrationConfig cal, IActionProvider actionProvider);
    public TurnResult StepRound(CombatState state, CombatContext ctx);
    public bool IsOver(CombatState state);
}
```

- 职责：五阶段回合管线编排（plan §5.2 + 回合战斗流程 §四 + 运行时状态模型 §7.1），每步调 L2 组件 + state.Apply。产 TurnResult（Round + 全部事件 + 快照）。IsOver：§5.5 结束判定（实例方法，用 `_cal.MaxRounds`）。
- 异常契约：构造 null → ArgumentNullException；StepRound 参数 null → ArgumentNullException；**IsOver(state) 参数 null → ArgumentNullException（v1.2 修正——Δ审计 F7：新拍板 API 的 null 契约补全）**。
- 确定性：同种子同输入（含 provider 行动序列）→ 逐位同 TurnResult。

### 3.5 处理流程（伪码，实现逐字遵循）

```
StepRound(state, ctx):
  state.Round += 1（审计 E6 修复：Round 递增显式化）
  round = state.Round
  # Phase 1: 情境更新（运行时状态模型 §7.1 步骤 1-5）
  for p in 0..Count-1:
      tone[p] = ToneUpdater.Step(tone[p], 零向量, cal)            # 步骤 1：纯衰减一步（审计 E9/W2 修复——
      state.ApplyTone(p, tone[p])                                  #   events §5.5.3「衰减是 step 10 Phase 1 的职责」；
                                                                   #   事件接收者 Phase 4 已注入，此处统一衰减步进；
                                                                   #   v1.2 终审注：events spec 锚点为 Phase 4 注入瞬间值，
                                                                   #   回合末 tone 值 = 注入 + Phase 1 衰减两步合成——测试锚点本地探针实测）
      b = CorticalBias.Compute(tone[p], data)                     # 步骤 2
      a' = WcDynamics.Step(a[p], b, SPending[p], W)               # 步骤 3（s=上回合累计）
      state.SPending[p] 清零                                      # 注入后清零
      (gurney', gates', salience') = CstcGating.Step(a', tone[p], gurney[p])   # 步骤 4-5
      state.ApplyGurney(p, a', gurney', gates', salience')

  # Phase 2: 继承（连续状态原样带入，不递减 CD）→ 无操作

  # Phase 3: 速度重算（审计 E7 修复：仅存活参与者参与排序）
  alive = [p | state.Participants[p].Hp > 0f]
  for p in alive:
      scores[p] = speedScore.ComputeScore(
          speedScore.ComputeComponents(a[p], salience[p], gurney[p], isDefending[p]), weights)
  order = TurnOrderBuilder.BuildOrder(scores[alive], ctx.Rng)（映射回全局索引）

  # Phase 4: 按序执行
  events = []
  for p in order:
      if state.Participants[p].Hp <= 0f: continue                  # 审计 E7/F4 修复：窗口前检查——被击杀者跳过（不 Tick/GetAction）
      state.TickWindow(p)                                         # 0. 窗口开始：CD tick + IsDefending=false（Q3）
      action = provider.GetAction(p, state, ctx)                  # 1. 行动选择
      evs = resolver.Resolve(p, action, state, ctx)               # 2-4. 声明→响应(stub)→结算（链式基准）
      state.ApplyEvents(evs)                                      #     HP/SAN = 事件字段（搬运）
      if action 含 M1=Defend: state.ApplyDefense(p, true, 1)      #     防御标记（§5.2）
      # Q4=A + 审计 E5/F3/W1 修复：Panic 跨越检测——逐伤害事件判定（每事件用其 TargetSanBefore/After），
      # 跨越（old ≥ 0.30f×SanMax ∧ new < 0.30f×SanMax）→ 生产 StatusChangeEvent(Panic) 并入同批。
      # v1.2 修正（Δ审计 F3/Δ-02）：**快照收集后合并**——遍历不可变快照（evs 副本），Panic 收集到独立列表，
      # 合并为 evsAll = evs + panics（不修改原集合——IReadOnlyList 无 Add / foreach 中 Add 抛异常）
      panics = []
      for ev in evs.ToArray():                                    # 快照遍历
          if ev is MentalDamageEvent me && 跨越(me.TargetSanBefore, me.TargetSanAfter, me.TargetSanMax):
              panics.Add(StatusChangeEvent(round, me.TargetId, me.TargetId) { Kind=Panic, Entered=true,
                  SanBefore=me.TargetSanBefore, SanAfter=me.TargetSanAfter, SanMax=me.TargetSanMax })
      evsAll = evs.Concat(panics).ToArray()                       # 同批一次 ProcessEvents（B4+C1 Σδ 一次 Step）
      result = eventProcessor.ProcessEvents(evsAll, state.Participants, state.Teams)   # 5. δ/s 派生（teams 来自 state——审计 E1 修复）
      for p2: state.ApplyTone(p2, result.States[p2].Tone)
      for p2: state.AccumulateS(p2, result.SensoryAccum[p2])
      events.AddRange(evsAll)
      if state.Participants[p].Hp <= 0f:                           # 6. HP=0 → 移除队列（跳过剩余窗口）
          downedEv = StatusChangeEvent(round, p, p) { Kind=Downed, Entered=true }
          dResult = eventProcessor.ProcessEvents([downedEv], state.Participants, state.Teams)  # D 广播实时
          ApplyTone/AccumulateS 同上
          events.Add(downedEv)

  # Phase 5: 回合收束（IsOver 由调用方轮询——v1.2 清理 CheckEnd 残留措辞，Δ-09）
  state.AddTurnResult(new TurnResult(round, events, state.Participants))
  return 上述 TurnResult
```

## 四、枚举与常量

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| 回合上限 | MaxRounds | 50 [NEW] | CalibrationConfig（§5.5 结束条件，待校准）。**L2 类型变更声明（审计 F5/W6 修复）**：加入已交付 CalibrationConfig——走 events 先例（EndurancePassivePenalty 模式）：本 spec AC-14 回执 + types spec 变更日志 🔧 行（结转） |
| Softmax 温度基线 | T_base | 0.15（已交付） | CalibrationConfig.TBase（NPC AI §3.4，**不重定义**） |
| 察觉回落阈值 | PerceptionThreshold | 0.15（已交付） | CalibrationConfig（回合战斗流程 §3.3，**不重定义**） |
| M1 持续占用惩罚 | M1SustainPenalty | −0.1（已交付） | CalibrationConfig（回合战斗流程 §3.3，**不重定义**） |
| tone baseline | (NE,VTA,SNc,5HT) | (0.3,0.4,0.5,0.5) 常量 | 运行时状态模型 §5.4（tone_bias/force_mod 基准——**demo 简化**，NPC AI §4.1 性格偏移留全量，审计 W6 声明） |
| 防御 CD | DefendCd 初值 | 1（语义） | 基础行动设计 §四（Q3=A 落地） |
| tone_bias 权重 | w_t(role) | 见 §五 5.3 表 | NPC AI §3.3 表（attack_physical/attack_mental/defend 三行） |

## 五、交叉引用约束（管线规则）

### 5.1 事件生产（ActionResolver 内，csharp-events spec §一 承接）

**target 定义（v1.2 修正——Δ审计 Δ-06：ActionSlot.TargetId 语义由 Flow 层定义）**：`target = state.Participants[slot.TargetId]`（越界 → ArgumentOutOfRangeException）；双通道各自独立目标（M1 打 A、Broca 骂 B——回合战斗流程 §2.2）。

**物理攻击**（baseDamage 消费 `cal.BasePhysicalDamage`=4、weaponBonus=0——审计 W7 修复：不写死字面量）：

```
gate_bonus = gates.Somatic
motivation_mod = clamp(tone_bias(attack_physical), −1, +1)   （plan §六，cap +100% 对齐核心机制 §4.2）
force_mod = clamp(DA_SNc − baseline_SNc, 0, 0.5)              （plan §六，cap +50%；baseline_SNc = 0.5 常量，demo 简化）
(defenderIsDefending = target.IsDefending)
(damage, hit) = DamageCalculator.CalcPhysicalDamage(cal.BasePhysicalDamage, 0, force_mod, motivation_mod, gate_bonus, defenderIsDefending, rng)
→ PhysicalDamageEvent（hit 分支）:
    Hit = true；BaseDamage = cal.BasePhysicalDamage；WeaponBonus = 0；ForceMod = force_mod；MotivationMod = motivation_mod；GateBonus = gate_bonus
    DamageDealt = damage
    DamageBlocked = defenderIsDefending ? damage : 0f          （减免 50% → 减免量 = 造成量，[NEW] demo 简化）
    IncomingDamage = DamageDealt + DamageBlocked               （f32 加法——保证 §2.4 契约恒等）
    TargetHpBefore = 游标 Hp；TargetHpAfter = Round1(游标 Hp − damage)；TargetHpMax = HpMax
→ PhysicalDamageEvent（miss 分支——**审计 E2/F1 修复：遵守 events §2.4 契约**）:
    Hit = false；DamageDealt = 0f；DamageBlocked = damage（完整伤害——damage calc AC-5「miss 仍返回完整伤害」）
    IncomingDamage = DamageBlocked（= dealt + blocked = 0 + damage，契约恒等）
    TargetHp* 同上（HP 不变——miss 无伤害，After == Before）
    （承受者 B2 m=blocked/incoming=1.0 恒发——events AC-3 锚点路径可达；
    **v1.2 表述修正（Δ审计 F9/Δ-07）：正常域（gate>0）下 blocked==incoming>0 恒成立；
    gate=0 边角 damage=0 → blocked=incoming=0，字面「>0」不成立——events §5.3.3 0/0→NaN 天然 skip 防御覆盖，
    行为安全；「契约恒等」限定正常域**）
```

**精神攻击**（baseDamage 消费 `cal.BaseMentalDamage`=2、endurance 消费 `cal.EndurancePassivePenalty`=1——审计 W7 修复）：

```
gate_bonus = gates.Cognitive
motivation_mod = clamp(tone_bias(attack_mental), −1, +1)      （plan §六：语言攻击动机 = DA_VTA 认知动机 + 5HT 去抑制）
enemySanRatio = target.San / target.SanMax
(sanDamage, hpDamage) = DamageCalculator.CalcMentalDamage(cal.BaseMentalDamage, motivation_mod, cal.EndurancePassivePenalty, enemySanRatio, gate_bonus)
→ MentalDamageEvent:
    SanDamage = sanDamage；HpDamage = hpDamage；MotivationMod = motivation_mod；GateBonus = gate_bonus
    TargetSanBefore = 游标 San；TargetSanAfter = Round1(游标 San − sanDamage)；TargetSanMax = SanMax
    TargetHpBefore = 游标 Hp；TargetHpAfter = Round1(游标 Hp − hpDamage)；TargetHpMax = HpMax
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

- 一方全灭（**审计 W1 修复：双口径**——正典 核心机制 §5「清空 HP 是最直接的判定基准」+ §8.2「SAN=0 先进入随机行为阶段」+ plan §5.2）：`所有同队参与者 Hp ≤ 0 ∨ San ≤ 0`（SanMax > 0 时 San == 0 为随机行为终态）→ TeamDefeated
- 回合上限：round ≥ MaxRounds（50 [NEW]，CalibrationConfig）→ MaxRounds
- 否则 → 继续。

**IsOver API（审计 W4/I4 拍板）**：`TurnManager.IsOver(CombatState state) → bool` **实例方法**（用 `_cal.MaxRounds`）——Phase 5 结束判定 + 调用方轮询统一入口。TurnResult **不扩展**（B6——避免跨 feature 类型变更；结束原因由调用方按 state 自判或 IsOver 布尔）。**v1.2 终审清理（原「伪码 CheckEnd 返回值由 IsOver 消费」为 Δ-09 已清理伪码的残留措辞——原 CheckEnd 角色由 IsOver 承接，调用方轮询）**。

## 六、验收标准

| AC | 验收标准 | 锚点/断言 |
|----|---------|-----------|
| AC-1 | CombatState 创建 + 静息初始化 | Create 后：WC = 静息不动点（30 回合 trace 与 M1 实测一致：active 48 节点 ∈ [0.535174, 0.771229]，排除节点 σ(b_j)；对齐 csharp-tone AC-15 方法）；tone = baseline（= 输入值）；SPending 全零；Round=0；History 空；Teams 与输入一致；teams.Count≠initial.Count → ArgumentException |
| AC-2 | Phase 1 情境更新全链 | 零事件回合 StepRound 后：a 更新（WcDynamics 输出）、gurney/gates/salience 更新（CstcGating 输出）、SPending 保持全零（零事件无累计——审计 W8 表述修正）。**tone 衰减锚点（v1.2 修正——Δ审计 Δ-05：首回合 tone=baseline → Step(δ=0)=baseline，「靠近」不可观测）**：① baseline 输入 → tone 逐位不变（衰减恒等）；② 注入回合后（tone ≠ baseline，如 A1 后 VTA≈0.689）→ 下一零事件回合 → `|tone' − baseline| < |tone − baseline|`（严格不等） |
| AC-3 | Phase 3 速度重算 | 同 RNG 种子 → order 确定性；首回合（静息状态）三分量 = 静息值（SpeedScoreCalculator 首回合无特判——静息输入自然给出）；防御中执行分含 M1SustainPenalty；Hp≤0 参与者不参与排序 |
| AC-4 | 物理攻击完整链 | 注入固定行动（IActionProvider）：攻击者 → PhysicalDamageEvent 字段全填（契约 IncomingDamage == Dealt + Blocked 逐位）；HP = TargetHpAfter（搬运）；攻击者 tone VTA 上升（A1 δ）；承受者 tone NE↑5HT↓（B1）；s[Postcentral] > 0；**miss → dealt=0 ∧ blocked==incoming>0（审计 E2 锚点）+ 承受者 B2 5HT↑（m=1.0）** |
| AC-5 | 精神攻击完整链 | 注入 mental_attack：MentalDamageEvent 字段全填；SAN = TargetSanAfter；HP 含 HpDamage 成分；A4/B4 tone 模式；**跨越 30% → Panic 事件同批 + C1 一次 Step（Σδ 叠加）** |
| AC-6 | 防御生命周期 | 声明 Defend → IsDefending=true + DefendCd=1；目标防御中物理伤害减半（DamageDealt 精确值）；下回合自己窗口开始 → IsDefending=false + DefendCd=0；防御中 Broca 精神攻击可用（M1=Defend + Broca=MentalAttack 合法）；防御 + 精神攻击同目标 → 链式终态（HP/SAN 双扣） |
| AC-7 | Panic 跨越事件生产（Q4=A） | SAN 扣减跨越 30%（old≥18 ∧ new<18，SanMax=60）→ StatusChangeEvent(Panic) 生产 + C1 事件（tone 变化）；未跨越（new=18 严格 / ΔSAN=0）→ 不生产；**逐事件基准（审计 W3 裁决，v1.2 表述修正——Δ审计 Δ-10：W9 配对校验下单窗口至多一次 SAN 扣减（仅 Broca=MentalAttack），「两次扣减」由两窗口/两攻击者构造；治疗分支 demo 不可达（3 基础行动无治疗）** |
| AC-8 | Downed 生产 + 队列移除 | HP=0 结算 → StatusChangeEvent(Downed) 生产 + D 广播实时生效（存活观察者 tone 变化）；**窗口前检查：被他人击杀的参与者轮到窗口时跳过（不 Tick/GetAction/Resolve——审计 E7/F4 锚点）** |
| AC-9 | 结束条件 | 一方全灭（Hp≤0 ∨ San≤0 同队全员——审计 W1 双口径）→ IsOver=true；回合上限 50 → IsOver=true；IsOver 为 TurnManager 实例方法（存在性断言） |
| AC-10 | TurnResult 打包 | Round 正确（state.Round 递增）；Events 全量（含 Phase 4 全部 + Panic + Downed）；ParticipantSnapshots = 回合末状态；History 追加 |
| AC-11 | NpcSalience | 3 候选 salience 计算（节点均值 × gate × (1+tone_bias)；Putamen 代理 a_SD1_somatic；Insula/Amygdala 直读）；tone_bias 按权重表（attack_physical (0,+0.3,+0.5,−0.3)）；Softmax 归一（ΣP=1）；**T_SAN 判定序（v1.2 修正——Δ审计 F4/Δ-08）：SAN==0 最先 → 均匀随机（不经 Softmax，同种子确定性）；<30% → +0.30；<60% → +0.10；≥60% → +0**；目标 = 第一个异队参与者（selfIndex + Teams） |
| AC-12 | 确定性 | 同种子 + **相同初始 state（每次重新 Create）** + 相同 provider 序列 → 连续 5 次完整战斗逐位同（审计 W2 表述修正：StepRound 推进 state，非"同输入重复调用"）；SPending 经只读访问器不可替换集合（审计 I3） |
| AC-13 | 异常契约 | 构造/参数 null → ArgumentNullException；通道-动作配对违规（M1=Mental、Broca=Physical/Defend）→ ArgumentException（审计 W9 扩展）；actorIndex ∉ [0, Count) → ArgumentOutOfRangeException |
| AC-14 | MaxRounds L2 类型变更回执（审计 F5/W6） | CalibrationConfig.MaxRounds == 50（int）；现有 types 测试零改动在全量 test run 通过；types spec 变更日志 🔧 行（结转 #1） |

## 七、本 spec 自检清单

1. **数学公式逐项对照**：Salience/tone_bias/T_SAN 分段逐字对照 NPC AI §3.2-3.4；五阶段管线对照 plan §5.2 + 回合战斗流程 §四 + 运行时状态模型 §7.1；接线表对照 plan §六。
2. **数值断言全部实测**：flow 层锚点（静息不动点、tone 方向、精确伤害值）来自组件级已验证输出 + 本地探针实测——测试不凭记忆写锚点。
3. **计算顺序契约明确**：Phase 1-5 顺序写死（伪码逐字遵循）；Apply 搬运语义（事件字段为权威，无二次计算）；Downed 实时处理（Phase 4 步骤 6）。
4. **接口注释先行**：CombatState/TurnManager/ActionResolver/NpcSalience/IActionProvider XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差标注。
5. **边界值覆盖**：SAN 跨越双端（old=18 含端/new=18 严格）、防御 CD 生命周期、HP=0 队列移除、回合上限、空声明 (null,null)、SAN=0 均匀随机。
6. **确定性**：无 static 可变状态；RNG 仅经 ctx 注入；同种子实证。
7. **偏差声明完整**：demo 简化项（NpcSalience 硬编码行动/单目标、防御连续声明、blocked=dealt 简化、MaxRounds [NEW]）逐条标注。
8. **常量复用漂移注**：T_base/PerceptionThreshold/M1SustainPenalty/DefendCd 引用不重定义；BasePhysicalDamage/BaseMentalDamage/EndurancePassivePenalty 事件生产消费（§5.1）；MaxRounds 唯一新常量 [NEW]；tone baseline 常量 (0.3,0.4,0.5,0.5)（demo 简化声明）。
9. **类型变更声明**：唯一 L2 类型变更 = CalibrationConfig +MaxRounds（§四 声明 + AC-14 回执 + types spec 🔧 行结转）；TurnResult 不扩展（§5.5 决策 B6）。

## 八、偏差声明

| # | 偏差 | 理由与处置 |
|----|------|-----------|
| B1 | NpcSalience 硬编码 3 基础行动候选集（plan §4.8 [NEW]） | 正式 skill 系统接入后替换；demo 验证引擎核心 |
| B2 | NpcSalience 目标选择 = 第一个异队参与者（[NEW] demo 简化） | 1v1 场景即对方；多目标 argmax 竞争留 Affordance Competition 全量 |
| B3 | 防御可连续声明（CD 重置非门槛）（[NEW] demo 简化） | 回合战斗流程 §7.3 连续防御细节待链路系统实装时细化 |
| B4 | 物理 DamageBlocked = dealt（防御时）（[NEW] demo 简化） | 减免 50% → 减免量 = 造成量（数学恒等）；IncomingDamage = dealt + blocked 契约恒等（f32 加法） |
| B5 | 响应窗口 stub（IResponseResolver + Noop） | plan §一 范围表：响应窗口 link 交互全文留链路 feature；L0 回避已在 damage calc 内生效 |
| B6 | TurnResult 不扩展结束原因字段 | 调用方轮询 TurnManager.IsOver（实例方法）；避免跨 feature 类型变更 |
| B7 | CombatState 初始化内部跑 30 回合静息 trace | 对齐运行时状态模型 §7.3「遭遇进入战斗时 WC=静息不动点」；M1 实测方法复用 |
| B8 | 结束条件双口径（Hp≤0 ∨ San≤0 同队全员）（审计 W1 修复） | 核心机制 §5「SAN=0 先进入随机行为阶段」——demo 精神攻击可达 SAN=0，即时结束而非拖到回合上限 |
| B9 | tone baseline 常量 (0.3,0.4,0.5,0.5)（审计 W6 声明） | tone_bias/force_mod 基准；NPC AI §4.1 7 参数化性格偏移留 Affordance Competition 全量 |
| B10 | Panic 逐事件基准检测（审计 W3 裁决，v1.2 终审表述修正） | C1「每次跨越」正典字面；**多攻击者/多窗口各自判定**（各批内 Σδ 叠加一次 Step——单窗口至多一次 SAN 扣减：仅 Broca=MentalAttack 扣 SAN，W9/B11 配对校验下 M1 无 SAN 动作） |
| B11 | 通道-动作配对完整校验（审计 W9/W4 修复） | 回合战斗流程 §2.1 通道归属（M1∈{Physical,Defend}、Broca∈{Mental}）；IsValidChannelUsage 只锁 Broca=Defend，本校验补全 |
| B12 | salience 节点取值（审计 W5 修复 + v1.2 修正——Δ审计 F2/Δ-03） | **仅 Putamen 需代理**（→a_SD1_somatic，plan §十三-4 同款；Putamen 无 WC a）；Insula/Amygdala 均 W-active 节点直读 a(t)（Amygdala 是 48 活跃节点之一——运行时状态模型 §4.1；原 c_loop_limbic 代理会 limbic CI 双重计数，已废弃） |

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-14 | 初稿 | 任务issue 01 | 全量审计 |
| v1.1 | 2026-08-14 | 全量审计（3 专家 + 对抗验证，53 发现 → 45 CONFIRMED）修复：E1（teams 进 CombatState——Teams 属性 + Create 参数）；E2（miss 字段契约——dealt=0 ∧ blocked=incoming）；E3（Resolve 签名 +actorIndex）；E4（NpcSalience +selfIndex）；E5（Panic 生产入伪码——逐事件基准 + 同批 ProcessEvents）；E6（Round 递增显式化）；E7（Phase 3/4 HP≤0 过滤）；E8（链式基准——resolver 局部游标）；E9（Phase 1 纯衰减步——events §5.5.3 落地）；W1（SAN=0 结束口径）；W3（ApplyEvents 补 API）；W4（IsOver 实例方法拍板）；W5（行动→通道映射 + subcortical 代理）；W6（baseline 常量声明）；W7（常量消费——BasePhysicalDamage/BaseMentalDamage/EndurancePassivePenalty）；W9（通道-动作配对校验）；F5/W6（MaxRounds L2 类型变更声明 + AC-14 回执）；AC-2/AC-11/AC-12 锚点表述修正；偏差 B8-B12 新增 | 全量审计（2❌×多专家 + 9⚠️ + 3ℹ️ 去重） | Δ审计 |
| v1.2 | 2026-08-14 | Δ审计（3 专家 + 对抗验证，30 发现 → 20 CONFIRMED）修复：F1/Δ-01（round 双口径——§3.3 改取 state.Round，去 +1 残留）；F3/Δ-02（Panic 快照收集后合并——IReadOnlyList 无 Add / foreach 中 Add 抛异常）；F2/Δ-03（Amygdala 直读——48 W-active 节点，c_loop_limbic 代理双重计数废弃，B12 修正）；F4/Δ-08（T_SAN 判定序——SAN==0 最先）；F5（双步衰减语义注明——事件 Step 含衰减 + Phase 1 纯衰减 = 跨回合连续时间步进；events 锚点为注入瞬间值，回合末锚点探针实测）；F9/Δ-07（miss 契约正常域限定，并入 F9 处置）；Δ-04（History internal AddTurnResult）；Δ-05（AC-2 衰减锚点拆两行——baseline 恒等 + 非 baseline 严格靠近）；Δ-06（target 定义——Participants[slot.TargetId]）；F7（IsOver null 契约）；Δ-09（伪码 CheckEnd 残留清理）；Δ-10（AC-7 两窗口构造 + B10 同步） | Δ审计（2❌ + 6⚠️ + 3ℹ️ 去重） | 终审确认 |
| v1.2 | 2026-08-14 🔧 修正（csharp-console spec@v1.0 §四 决策 D1 承接）：TurnManager 新增 `LastRoundActions`（IReadOnlyList&lt;(int Participant, CombatAction Action)&gt;）与 `LastRoundOrder`（int[]）实例属性——StepRound 末尾写入（console 渲染行动声明与顺序；§九 要求）。Flow 层属性，非 L2 类型变更（types 交付物不动） | console 任务issue（§九 输出清单） | 随 console 审计 |
| v1.2 | 2026-08-14 🔧 修正（console 终审 Δ-C05 跨 spec 声明补记）：CombatState 新增 `Salience` 只读访问器（IReadOnlyList&lt;LoopSalience&gt;）——ApplyGurney 的 salience 参数存储槽（Phase 3 速度重算 + console 渲染消费；实现已交付，spec 补记） | console 终审（Δ-C05 悬空契约） | 随 console 审计 |

---
*创建: 2026-08-14 | 更新: 2026-08-14 | 版本: v1.2*
*关联: [任务issue 01](../../archive/grilling/csharp-flow/design/issues/01-flow-spec.md), [plan §五](csharp-engine-roadmap.md), [回合战斗流程](../../rules/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md), [NPC AI 行为模型](../../rules/skill-tree/NPC%20AI%20%E8%A1%8C%E4%B8%BA%E6%A8%A1%E5%9E%8B.md), [运行时状态模型](../../rules/skill-tree/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md)*
