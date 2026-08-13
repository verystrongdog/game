# 引擎共享状态类型 — 实现规格

> csharp-engine step 2：定义 plan §三 全部共享状态类型 + CombatContext 三个依赖项（IRng / GameData / CalibrationConfig），作为 step 3-9 引擎模块的输入输出契约。版本: v1.1

## 目录

1. [一、范围与依赖](#一范围与依赖)
2. [二、数据结构](#二数据结构)
3. [三、接口定义](#三接口定义)
4. [四、枚举与常量](#四枚举与常量)
5. [五、交叉引用约束](#五交叉引用约束)
6. [六、验收标准](#六验收标准)
7. [七、本 spec 自检清单](#七本-spec-自检清单)

---

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | `YouAreNotTheFish.Core/Types/` 全部新文件（状态 record ×8 + 声明/上下文 ×2 + 事件 ×6（1 抽象基类 CombatEvent + 5 具体子类）+ 接口 IRng + RNG 实现 ×1（DeterministicRng）+ 常量 ×1（CalibrationConfig）+ 枚举 ×4）；`Data/` 补充 GameData 聚合 + LoadAll |
| 不覆盖 | SpeedWeights/SpeedComponents（plan §4.5 → step 7）；s_pending、CombatState、TurnManager（step 10）；14 事件 kind 枚举与 δ 派生逻辑（step 9，本 spec §五仅列映射约束） |
| 前置依赖 | csharp-data-layer ✅（24/24 绿）；[csharp-engine plan v1.1](../csharp-engine/design/plan.md) sign-off ✅ 2026-08-13 |
| 阻塞 | step 3-9 全部引擎模块（类型契约未落地则无法编译） |
| 引用源 | [运行时状态模型](../../规则/技能树系统/运行时状态模型.md)、[回合战斗流程](../../规则/回合战斗流程.md)、[核心机制](../../规则/核心机制.md)、[基础行动设计](../../规则/技能树系统/操作层/基础行动设计.md)、框架 memory `code-framework-plan-2026-08-06` §3.5 |

---

## 二、数据结构

通用约定：
- 全部为不可变 `record`（或 abstract record 基类）；数组字段构造时拷贝（`ToArray()`/`Clone()`），无 setter 暴露可变引用。
- 值域约束（[0,1] 等）**文档化不强制**——L2 生产方保证，性能考虑构造时不 clamp；约束写入 XML doc。
- 每个字段 XML doc 含来源注释（plan 章节 + 设计文档章节）。

### 2.1 WcState

| 文档符号 | 字段 | 类型 | 来源 |
|---------|------|------|------|
| a_j(t) | A | float[69] | 运行时状态模型 §三（值域 [0,1]） |

- 行序 = canonical 69 = `WsensoryMatrix.RegionIds`（W_sensory.json rows 序）——约束 C1。
- **无身份映射字段**（设计取舍）：canonical 序的 fid 身份已由 `WsensoryMatrix.RegionIds`（Data 层）与 `WMatrix.RowFids`（step 3 构建）承担两份；WcState 是每 tick 更新的运行时状态，持有第三份 fid 数组纯冗余。行序对齐由约束 C1 规范 + 下游消费方测试验证（step 3 WMatrixBuilder 断言 W.RowFids == RegionIds）。**实测警示**：`brain_regions.json` regions 的 key 序与 W_sensory rows 序**不同**（69 集合相同；首处分歧位置 0：TransverseTemporal vs AccumbensCore）——凡需要 Regions 序处必须按 functional_id 映射，不得按位置直取。

### 2.2 ToneState

| 文档符号 | 字段 | 类型 | 来源 |
|---------|------|------|------|
| NE_tone | Ne | float | §5.1 蓝斑，默认 baseline 0.3（§5.4） |
| DA_VTA_tone | DaVta | float | §5.1 VTA，baseline 0.4 |
| DA_SNc_tone | DaSnc | float | §5.1 SNc，baseline 0.5 |
| 5HT_tone | Ht5 | float | §5.1 中缝核，baseline 0.5 |

值域 [0,1]（§5.2 clip）。

### 2.3 GurneyState

| 文档符号 | 字段 | 类型 | 来源 |
|---------|------|------|------|
| a_SD1/a_SD2/a_STN/a_GPe/a_GPi（somatic） | Somatic | float[5] | §6.3 |
| 同上（cognitive） | Cognitive | float[5] | §6.3 |
| 同上（limbic） | Limbic | float[5] | §6.3 |

- 群体索引 = `GurneyPopulation` 枚举序：0=SD1, 1=SD2, 2=STN, 3=GPe, 4=GPi。值域 [0,1]。
- 环路顺序（Somatic/Cognitive/Limbic）与 `CstcLoop` 枚举的 Somatic/Limbic/Cognitive 序**不同**——本 spec 以显式命名字段消歧，不依赖枚举序（约束 C2）。

### 2.4 GateState

| 文档符号 | 字段 | 类型 | 来源 |
|---------|------|------|------|
| gate_somatic | GateSomatic | float | §6.4 gate = 1 − O_GPi，值域 [0,1] |
| gate_cognitive | GateCognitive | float | §6.4 |
| gate_limbic | GateLimbic | float | §6.4 |

### 2.5 ParticipantState

| 文档符号 | 字段 | 类型 | 来源 |
|---------|------|------|------|
| 91 浮点（69+4+15+3） | Wc / Tone / Gurney / Gates | WcState / ToneState / GurneyState / GateState | §三 表尾"总计 91" |
| HP / HP_max | Hp / HpMax | int | 审计修复 #2（原计划 91 浮点无血量） |
| SAN / SAN_max | San / SanMax | int | 修复 #2 |
| 防御状态 | IsDefending | bool | 修复 #4；回合战斗流程 §7.1（持续到下回合自己窗口） |
| 忍耐主动 CD | EnduranceActiveCd | int | 基础行动设计 §四（−2 CD2 占 Broca）；回合战斗流程 §9.1（自己窗口起点递减） |
| 防御 CD | DefendCd | int | 回合战斗流程 §9.1（CD=1：暴露一轮后才能再防） |

- 工厂 `CreateDefault(hpMax, sanMax)`：a_j=0.10、tone=baseline(0.3/0.4/0.5/0.5)、Gurney=0（§7.3 初始化）；**gates=1.0**（推导值——§7.3 未定义 gate 初值，本 feature 取 1.0 = 1 − O_GPi(0)：§6.3 ramp O(a)=0 if a<e=0.2 ⇒ O_GPi(0)=0，§6.4 gate=1−O_GPi。语义"初始全放行"，首回合 Phase 1 步骤 5 CstcGating.Step 重算覆盖）；CD=0、IsDefending=false。
- **s_pending 不在本类型**——归 CombatState（plan §五 5.1 + 再审计 C-C3），step 10 实现。

### 2.6 CombatAction + ActionSlot

| 文档符号 | 字段 | 类型 | 来源 |
|---------|------|------|------|
| M1 通道动作（可空） | M1 | ActionSlot? | 回合战斗流程 §2.1（每窗口 M1 ≤1） |
| Broca 通道动作（可空） | Broca | ActionSlot? | §2.1（Broca ≤1） |
| 窗口内顺序 | Order | ChannelOrder | §2.3（先后由玩家决定） |

ActionSlot：

| 字段 | 类型 | 来源 |
|------|------|------|
| Kind | ActionKind | plan §4.8 3 基础行动（PhysicalAttack/MentalAttack/Defend） |
| TargetId | int | §2.2（一次一个目标）——participant 索引，语义由 Flow 层定义 |

- 静态校验 `IsValidChannelUsage(M1, Broca)`：M1 与 Broca 各 ≤1（类型天然保证）；**Defend 独占 M1**（§7.2 防御期间 M1 被占、§2.1 物理攻击↔防御互斥）。返回 bool，供 step 10 ActionResolver 使用。

### 2.7 CombatContext

| 字段 | 类型 | 来源 |
|------|------|------|
| Rng | IRng | plan §二 确定性原则（RNG 注入） |
| Data | GameData | plan §三（框架 memory：含 RNG 的只读上下文） |
| Calibration | CalibrationConfig | plan §三 |

只读上下文，**无**可变回合计数（归 CombatState，plan §三 行注）。

### 2.8 WMatrix

| 文档符号 | 字段 | 类型 | 来源 |
|---------|------|------|------|
| W_norm[j][k] | W | float[69,69] | §4.3（行归一化后） |
| τ_j | Tau | float[69] | §4.4 四档（0.01/0.05/0.15/0.05） |
| fid→行序映射 | RowFids | string[69] | plan §三（行序 = canonical 69） |

由 WMatrixBuilder（step 3）构建；本 feature 仅定义契约。
- **行序契约**：WMatrixBuilder 必须按 canonical 序（= `WsensoryMatrix.RegionIds`）构建 W 行，**不得**按 graph_nodes 迭代序（实测三数据文件 key 序互不相同——graph_nodes 为 51 个 dk_name 空间，小写，且数量本就不足 69）；RowFids 承担 fid→行校验职责（step 3 测试断言 RowFids == RegionIds）。

### 2.9 LoopSalience

| 文档符号 | 字段 | 类型 | 来源 |
|---------|------|------|------|
| c_loop[3] + DA_loop[3] | Somatic / Cognitive / Limbic | LoopValue | §6.2（c=mean(a(ci))）+ §6.3（DA 混合） |

DA 混合逐字段显式公式（§6.3 文档序为 limbic→cognitive→somatic，与字段序不同——按字段名配对，不得按位置直配）：
- `Somatic.Da` = 0.2×DA_VTA + 0.8×DA_SNc（运动执行主导）
- `Cognitive.Da` = 0.4×DA_VTA + 0.6×DA_SNc
- `Limbic.Da` = 0.8×DA_VTA + 0.2×DA_SNc（动机主导）

`LoopValue(float C, float Da)`——C=c_loop ∈[0,1]，Da=DA_loop ∈[0,1]。再审计 C-C2 产物：CstcGating.Step 返回三元组含本类型。

### 2.10 TurnResult

| 字段 | 类型 | 来源 |
|------|------|------|
| Round | int | plan §五 5.1（回合计数归 CombatState，此处为结果标注） |
| Events | IReadOnlyList\<CombatEvent\> | 框架 memory §3.5（引擎输出事件列表）；plan §三 |
| ParticipantSnapshots | IReadOnlyList\<ParticipantState\> | 框架 memory §3.5"参与者快照" |

### 2.11 事件类型（引擎输出）

基类 `abstract record CombatEvent(int Round, int ActorId, int TargetId)`——ActorId=事件主动方（攻击者/倒下者），TargetId=承受方；语义逐子类注明。

| 类型 | 字段 | 来源 |
|------|------|------|
| PhysicalDamageEvent : CombatEvent | Hit(bool)；BaseDamage(int)；WeaponBonus(int)；ForceMod(float)；MotivationMod(float)；GateBonus(float)；DamageDealt(int)；DamageBlocked(int)；IncomingDamage(int)；TargetHpBefore/After/Max(int×3) | plan §4.6 物理公式逐因子（§九 console 输出需要）；§5.5 m 公式（A1/A2: actual/expected、B1: \|ΔHP\|/HP_max、A5/B2: blocked/incoming） |
| MentalDamageEvent : CombatEvent | SanDamage(int)；HpDamage(int)；MotivationMod(float)；GateBonus(float)；TargetSanBefore/After/Max(int×3)；TargetHpBefore/After/Max(int×3) | plan §4.6 精神公式；§5.5（A4: actual/expected、B4: \|ΔSAN\|/SAN_max） |
| HealEvent : CombatEvent | HealAmount(int) | demo 3 基础行动无治疗动作（plan §一 范围表无治疗项，推断）；保留系框架 memory §3.5 4 事件类型完整性要求；占位字段 |
| StatusChangeEvent : CombatEvent | Kind(StatusKind)；Entered(bool) | Panic：§5.5 C1（SAN<30% 跨越，old≥30%∧new<30%）；Downed：§5.5 D 注（HP≤0 即时 → D1/D2 派生）。ActorId=状态变化者，TargetId=ActorId（Downed 时同为倒下者，观察者由 step 9 派生） |
| LinkGrowthEvent : CombatEvent | LinkId(string)；DeltaM(float) | demo 未用（无 link）；字段按 link 系统实装时扩充，占位注明 |

- 框架 memory 4 类型覆盖：DamageEvent（Physical/Mental 子类）+ HealEvent + StatusChangeEvent + LinkGrowthEvent ✅。
- **A4 expected 重算注意**（step 9 消费方）：A4 的 m=actual/expected 中 expected = 2×(1+motivation) − 忍耐被动，需忍耐被动常量（基础行动设计 §四，值 −1，未进 CalibrationConfig——plan §七 同样未列）与低 SAN 穿透逻辑（核心机制 §4.3）；EventProcessor 需读 ParticipantState.EnduranceActiveCd 或在 step 9 补常量。
- **视角归属**（决策 D4）：事件装客观结果；§5.5 的 A/B 每角色视角（攻击者 A1、承受者 B1 等）由 EventProcessor（step 9）派生——映射约束见 §五 C5。
- **偏差声明（类型层级）**：框架 memory §3.5 的 `DamageEvent` 名称不落地——拆为 PhysicalDamageEvent/MentalDamageEvent 两子类（plan §4.6 物理/精神公式字段集不同），不存在名为 DamageEvent 的类型。step 9 若需统一分支可加 `abstract record DamageEvent : CombatEvent` 中间层（本 feature 不加）。

### 2.12 GameData（Data/GameData.cs 新建，命名空间 `YouAreNotTheFish.Core.Data`）

L1 聚合 record——5 个数据文件各对应一个已交付 record（决策 D2）。plan §三 CombatContext 行、§4.3 `WMatrixBuilder.Build(GameData)`、`CorticalBias.Compute(ToneState, GameData)` 均消费本类型。

| 字段 | 类型 | JSON 源 | 来源 |
|------|------|---------|------|
| BrainRegions | BrainRegionsData | brain_regions.json | csharp-data-layer spec AC-1~5 |
| Tripartite | TripartiteModel | connectivity/tripartite_model.json | 同上 |
| Wsensory | WsensoryMatrix | connectivity/W_sensory.json | 同上（RegionIds 即 canonical 69——约束 C1） |
| SituationPrimitives | SituationPrimitives | connectivity/situation_primitives.json | 同上 |
| SignalTypes | SignalTypesCatalog | signal_types.json | 同上 |

字段类型名与 Data 层已交付 record 一致（已核对 `src/YouAreNotTheFish.Core/Data/` 实际声明；实现时如发现漂移按 L2 修正回路处理）。

---

## 三、接口定义

### 3.1 IRng（Types/IRng.cs）

```csharp
public interface IRng
{
    /// <summary>返回 [0,1) 均匀分布浮点。</summary>
    float NextFloat();
    /// <summary>返回 [0, maxExclusive) 均匀分布整数。</summary>
    int NextInt(int maxExclusive);
}
```

来源：plan §二 确定性原则（NextFloat/NextInt）。

### 3.2 DeterministicRng（Types/DeterministicRng.cs）

- 构造 `DeterministicRng(ulong seed)`；实现 splitmix64 [NEW]（选择理由：System.Random 种子序列不保证跨 .NET 版本稳定；splitmix64 为 counter-based 生成器——单一 64 位状态、周期 2^64、实现 5 行可审计，保证同种子同序列的确定性契约 C8/AC-6）。
- 同种子同序列（确定性），异种子异序列（smoke 测试对拍）。

### 3.3 GameDataLoader.LoadAll（Data/GameDataLoader.cs 扩展）

```csharp
public static GameData LoadAll(string dataDir)
```

- 加载 5 文件：`brain_regions.json`、`connectivity/tripartite_model.json`、`connectivity/W_sensory.json`、`connectivity/situation_primitives.json`、`signal_types.json`（文件名固定，路径来自 csharp-data-layer 测试已使用布局）。
- 异常语义同现有 5 方法（FileNotFoundException/JsonException/InvalidOperationException——csharp-data-layer AC-11）。

### 3.4 ParticipantState.CreateDefault（Types/ParticipantState.cs）

```csharp
public static ParticipantState CreateDefault(int hpMax, int sanMax)
```

初始化值：a_j=0.10、tone=baseline、Gurney=0（§7.3）；gates=1.0（推导值——§7.3 未定义 gate 初值，1.0 = 1 − O_GPi(0)，§6.3 ramp + §6.4 gate 公式；语义"初始全放行"，首回合 CstcGating.Step 覆盖）；Hp=hpMax、San=sanMax、CD=0。

### 3.5 CombatAction.IsValidChannelUsage（Types/CombatAction.cs）

```csharp
public static bool IsValidChannelUsage(ActionSlot? m1, ActionSlot? broca)
```

规则（§2.1 防御是 M1 动作 + §7.4 防御期间 Broca 可用）：
- Defend 只能作为 m1；**broca.Kind==Defend 恒非法**（含 m1==null 时——实现须空值短路求值，不得先解引用 m1）
- m1.Kind==Defend → broca 仍可 MentalAttack（§7.4）
- (null, null) 空声明**合法**（对应等待语义，step 10 ActionResolver 依赖此契约）

---

## 四、枚举与常量

### 4.1 枚举（Types/）

| 枚举 | 值 | 来源 |
|------|-----|------|
| ActionKind | PhysicalAttack, MentalAttack, Defend | plan §4.8 3 基础行动候选 |
| ChannelOrder | M1First, BrocaFirst | 回合战斗流程 §2.3 |
| GurneyPopulation | Sd1=0, Sd2, Stn, GPe, GPi | §6.3 5 群体（索引序即本枚举序） |
| StatusKind | Panic, Downed | §5.5 C1 / D 注 |

### 4.2 CalibrationConfig（Types/CalibrationConfig.cs）

instance record + `static CalibrationConfig Default`（决策 D3——plan §七 字面"static class"的偏差：结转 #4 蒙特卡洛 sweep 需要实例注入）。

| 常量 | 字段 | 值 | 来源 |
|------|------|-----|------|
| 速度权重 | SpeedW1/SpeedW2/SpeedW3 | 1/3 | 回合战斗流程 §3.1 |
| m 默认 | MDefault | 0.3 | 皮层动力学 §5.3 |
| Softmax T | TBase | 0.15 | NPC AI §3.4 |
| δ 缩放 | DeltaScale | 0.3 [NEW] | 运行时状态模型 §5.5 ⚠️ 延迟注 |
| 精神缩放 | ScaleMental | 未启用（demo 固定 base 2） | §8.1 ⚠️ |
| 期望伤害 | ExpectedDamage | 4 | 核心机制 §4.2 |
| M1 持续占用惩罚 | M1SustainPenalty | −0.1 [NEW] | 回合战斗流程 §3.3（值未定义） |
| 察觉"未显著激活"阈值 | PerceptionThreshold | 0.15 [NEW] | 回合战斗流程 §3.3（值未定义） |
| demo 玩家 | PlayerHp/PlayerSan | 50/80 [NEW] | 核心机制 §10.1 玩家基线值默认（±10 为角色类型偏移，此处取基线） |
| demo NPC 杂兵 | NpcHp/NpcSan | 15/60 [NEW] | 核心机制 §10.1 轻度病人区间取中值（HP 12-18→15、SAN 50-70→60） |

[NEW] 标注待对应 issue 关闭后摘除（plan §七 规则）。

---

## 五、交叉引用约束

- **C1** WcState.A 长度 69，行序 = canonical 69 = `WsensoryMatrix.RegionIds`（W_sensory.json rows 序，plan §三「按 canonical 69 行序（与 W_sensory 行序一致）」）。**不等于** `BrainRegionsData.Regions` 的 key 序（实测两 JSON 69 集合相同、顺序不同、首处分歧位置 0）——集合双射由 csharp-data-layer AC-2 保证，matrix 行序一致性由 AC-8 保证，canonical 序归属由本约束定义。凡需按 fid 定位（如 W_sensory 行 → 脑区元数据）须经 functional_id 映射，不得按位置直取。
- **C2** GurneyState 三数组各长 5，群体索引按 GurneyPopulation 枚举序；环路字段命名显式，不依赖 CstcLoop 枚举序。
- **C3** 91 浮点 = 69（Wc）+ 4（Tone）+ 15（Gurney）+ 3（Gate）——ParticipantState 嵌套结构与之对应（§三 表尾）。
- **C4** CombatAction：M1/Broca 各 ≤1；Defend 仅 M1 通道（§2.1/§7.2）。
- **C5** 事件 → §5.5 δ/s 派生映射（step 9 EventProcessor 消费，本 feature 不实现）：

| 客观事件 | 攻击者侧（A） | 承受者侧（B） | 备注 |
|---------|-------------|-------------|------|
| PhysicalDamageEvent(Hit=true, 防御未生效) | A1（m=actual/expected） | B1（m=\|ΔHP\|/HP_max） | A3 暴击 demo 无（plan §4.6 无 crit 项） |
| PhysicalDamageEvent(Hit=true, 防御生效) | A1 | A5（防御成功 5HT+1，m=blocked/incoming） | 承受者侧取 A5 非 B1 为本 spec 解释——§5.5 未定义互斥（B1「被物理攻击击中」与 A5「防御成功」在「防御中仍被命中」场景同时成立，防御=减伤 50% 命中仍落地）；A5 δ=(0,0,0,+1) 与 B1 δ=(+1,0,0,−1) 5HT 方向相反，step 9 实现时须复核。**判别约定**：防御生效判定 = DamageBlocked>0（小伤害取整边界下 blocked 可能为 0，如 incoming=1 减半后 dealt=1——step 9 spec 可重定义，本 spec 仅给建议判别式） |
| PhysicalDamageEvent(Hit=false) | A2（m≈0 → 跳过 emit） | B2（m=blocked/incoming）；**incoming_damage=0 时 m=0 直接跳过 emit**（本 spec 边界约定——§5.5 的「m<0.01 跳过 emit」对 0/0=NaN 失效） | §5.5 A2 行注 + 本 spec 边界约定 |
| MentalDamageEvent | A4（m=actual/expected） | B4（m=\|ΔSAN\|/SAN_max） | |
| StatusChangeEvent(Panic) | — | C1（m=1.0，自身阈值突破） | §5.5 C1 guard |
| StatusChangeEvent(Downed) | — | D1/D2（m=1.0，emit 到所有 HP>0 观察者，按队伍关系分流） | §5.5 D 注 |

- **C6** CalibrationConfig.Default 值 = plan §七 表逐条一致（AC-9 逐常量断言）。
- **C7** 所有数组字段构造时防御性拷贝。
- **C8** 确定性：Types/ 无 static 可变状态（CalibrationConfig 只读；DeterministicRng 无共享状态）。

---

## 六、验收标准

| AC | 验收标准 | 验证方式 |
|----|---------|---------|
| AC-1 | 全部类型编译——`dotnet build` 0 错误 | 门禁 |
| AC-2 | §二 每个字段 XML doc 含来源注释（plan + 设计文档章节） | 审计逐字段核查 |
| AC-3 | 91 浮点组成：69+4+15+3 计数测试 | 测试 `ParticipantState_Composes91Floats` |
| AC-4 | 4 事件类型字段覆盖 §5.5 m 公式 + §九 console 消费需求 | 审计逐 m 公式核查 + 测试构造各事件 |
| AC-5 | CreateDefault 初始化值：a_j=0.10 / tone=baseline / Gurney=0（§7.3）+ gates=1.0（§6.3+§6.4 推导） | 测试逐字段断言 |
| AC-6 | DeterministicRng 同种子同序列 / NextInt 值域 | 测试 100 值对拍 |
| AC-7 | LoadAll 5 文件加载，结果与 5 个单文件方法一致 | 测试逐字段对照 |
| AC-8 | IsValidChannelUsage 双通道约束（Defend 独占 M1；broca.Kind==Defend 恒非法含 m1=null；(null,null) 合法） | 测试用例表 |
| AC-9 | CalibrationConfig.Default 逐常量 = plan §七 表 | 测试逐常量断言 |
| AC-10 | WcState.A 长度 69；行序 = canonical（RegionIds，约束 C1）——本 feature 测试长度 + CreateDefault 等值性；行序对齐验证由 step 3 WMatrixBuilder 测试承担（W.RowFids == WsensoryMatrix.RegionIds） | 测试（复用 GameDataLoader.LoadWsensory 加载真实 W_sensory.json 取 RegionIds） |

---

## 七、本 spec 自检清单

- [ ] 每个字段来源注释（plan 章节 + 设计文档章节）无遗漏
- [ ] 字段命名 vs 文档符号对照表（§二 各表"文档符号"列）齐全
- [ ] 值域约束文档化（XML doc），构造不 clamp 的约定写明
- [ ] 数组字段防御性拷贝（C7）
- [ ] 行序契约唯一 canonical = RegionIds（C1）；全文无 BrainRegionsData.Regions 序引用
- [ ] DA 混合按字段名配对（Somatic 0.2/0.8、Cognitive 0.4/0.6、Limbic 0.8/0.2），非位置直配
- [ ] 事件类型无重复字段（Physical/Mental 差异全进子类）
- [ ] 接口注释先行（IRng/工厂/校验方法先 XML doc 后实现——"设计两次"约束，plan §十一）
- [ ] 偏差声明完整：CalibrationConfig instance 化（D3）、splitmix64 [NEW]、事件视角归属（D4）
- [ ] [NEW] 标注齐全（plan §七 规则：对应 issue 关闭后摘除）

---

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-13 | 初稿——§三 全部类型 + CombatContext 依赖项 + 事件类型字段设计 | 任务issue 01 | 全量审计 |
| v1.1 | 2026-08-13 | 吸收 v1.0 审计 1❌+5⚠️+9ℹ️：C1/AC-10 行序恒等式修正（canonical=RegionIds，实测两 JSON 序不同）；GameData 字段表（§2.12）；gates 初值 0→1.0（§6.3+§6.4 推导）；LoopSalience DA 逐字段公式；C5 补 A5 归属解释 + B2 NaN 边界；IsValidChannelUsage 空值真值表；DamageEvent 层级偏差声明；splitmix64 理由修正；来源表述修正 ×4 | v1.0 全量审计（3 专家，2 reject + 1 conditional） | Δ审计（变更章节 + 半径扩张） |
| v1.1 | 2026-08-13 🔧 修正（L1 笔误级，免重审）：Δ审计 4 项表述建议——覆盖行事件计数 ×5→×6（含抽象基类）；§2.8 graph_nodes 序措辞（51 个 dk_name 空间）；C5 补防御生效判别约定（DamageBlocked>0，step 9 可重定义）；AC-10 验证方式措辞（无 fixture 类，用 LoadWsensory） | Δ审计 6 info（2 计数 + 4 措辞） | 免重审 |

---

*创建: 2026-08-13 | 更新: 2026-08-13 | 版本: v1.1*
*关联: [csharp-engine plan v1.1](../csharp-engine/design/plan.md), [任务issue 01](issues/01-types-spec.md), [运行时状态模型](../../规则/技能树系统/运行时状态模型.md), [回合战斗流程](../../规则/回合战斗流程.md), [核心机制](../../规则/核心机制.md)*
