# C# 战斗引擎 — 实施计划（审计修订版）

> 本计划是 2026-08-12 四专家 workflow 审计（结论：有条件放行）后的修订版引擎实施计划——完整吸收审计的 10 项关键修复、13 项重要改进与 6 项放行条件，作为 csharp-engine 总计划的 step 0 交付物。后续每个实施步骤拆为独立 feature，走二层流水线（任务issue → spec → 审计 → sign-off → 实现）。

版本: v1.0（审计修订版）

## 目录

1. [一、范围与目标](#一范围与目标)
2. [二、架构与分层](#二架构与分层)
3. [三、状态类型总表](#三状态类型总表)
4. [四、L2 引擎模块规格](#四l2-引擎模块规格)
5. [五、L3 实体 / L4 流程](#五l3-实体--l4-流程)
6. [六、伤害结算接线](#六伤害结算接线)
7. [七、校准常量 CalibrationConfig](#七校准常量-calibrationconfig)
8. [八、验证标准](#八验证标准)
9. [九、控制台 harness 规格](#九控制台-harness-规格)
10. [十、测试清单](#十测试清单)
11. [十一、实施顺序与 feature 划分](#十一实施顺序与-feature-划分)
12. [十二、对设计文档的偏差声明](#十二对设计文档的偏差声明)
13. [十三、设计待决清单](#十三设计待决清单)

---

## 一、范围与目标

**目标**：用 C# 写出可运行、可验证的战斗引擎核心（L1-L4 + 控制台 harness）——加载真实脑数据，运行回合战斗，证明神经动力学产生合理战斗结果。非 Unity：纯 .NET 8.0 库 + xUnit。引擎层确定性（RNG 注入），无 Unity 引用。

**范围表**（审计条件 5）：

| 项 | 内容 |
|----|------|
| 覆盖 | WC 69 节点动力学（解析解）、脑干 4 tone、b_j 注入、CSTC 3 环路 Gurney 门控、速度排序（察觉/决断/执行）、物理/精神伤害结算、14 事件 δ/s 处理、NPC 3 基础行动 salience、5 Phase 回合编排、控制台 demo（2 参与者 1v1） |
| 不覆盖 | 空间系统（12 格/控制区/AOE/借机攻击/视线——[回合战斗流程](../../规则/回合战斗流程.md) §十，原型期推迟）、逃跑/投降（§8.2-8.3）、HP↔SAN 互转（[核心机制](../../规则/核心机制.md) §5.3）、响应窗口 link 交互全文（L1 期待/L3 精准/L5 叙事重构等——demo 无 link）、观察者效应"相信被打败"（待设计）、技能树/LinkState 全量（demo 仅 m_default） |
| 前置依赖 | csharp-data-layer ✅ 已交付（2026-08-12，24/24 测试绿）、[运行时状态模型](../../规则/技能树系统/运行时状态模型.md)、[回合战斗流程](../../规则/回合战斗流程.md)、[核心机制](../../规则/核心机制.md)、[皮层动力学-通用层](../../规则/技能树系统/皮层动力学-通用层.md)、[NPC AI 行为模型](../../规则/技能树系统/NPC AI 行为模型.md)、[基础行动设计](../../规则/技能树系统/操作层/基础行动设计.md) |
| 阻塞 | 后续 link/技能/装备 feature 依赖本引擎核心；NPC Affordance Competition 全量（7 参数化）依赖 demo 验证 |

---

## 二、架构与分层

5 层架构（memory `code-framework-plan-2026-08-06` D1-D5），命名空间以已交付的 `YouAreNotTheFish.Core` 为准：

```
L1 Data  (已交付)    YouAreNotTheFish.Core/Data/      JSON → 不可变 record，无行为
L2 Engine            YouAreNotTheFish.Core/Engine/    纯函数、无副作用、RNG 注入、产事件不产状态
L3 Entity            YouAreNotTheFish.Core/Entity/    可变战斗状态，自己 Apply 引擎产出
L4 Flow              YouAreNotTheFish.Core/Flow/      编排（回合循环/行动分发），无结算逻辑
L5 Presentation      Unity（本阶段无）
共享值类型            YouAreNotTheFish.Core/Types/     (SpeedComponents.cs 已存在)
```

- **修复 #9**：TurnManager/ActionResolver 移入 `Flow/` 命名空间（L4 纳入本期范围）；LinkState 移入 Data 层为不可变 record（本期 demo 不实例化，仅 m_default 常量生效，见 §七）。
- **框架约束 D1**：引擎产出事件列表 → 实体自己 Apply。**D3**：速度排序算法在 L2，循环调度编排在 L4。
- **确定性原则**：L2 全部 static 纯函数，RNG 经 `IRng` 注入（NextFloat/NextInt），GameData 以参数传入，禁止 static 可变状态。

---

## 三、状态类型总表

（审计修复 #2/#3/#4 已并入）

| 类型 | 位置 | 字段 | 来源 |
|------|------|------|------|
| WcState | Types/ | `float[69] a_j`，按 canonical 69 行序（与 W_sensory 行序一致） | 运行时状态模型 §三 |
| ToneState | Types/ | NE, DA_VTA, DA_SNc, 5HT ∈ [0,1] | 同上 |
| GurneyState | Types/ | 15 floats：3 环路 × 5 群体（SD1/SD2/STN/GPe/GPi） | §6.3 |
| GateState | Types/ | gate_somatic, gate_cognitive, gate_limbic | §6.4 |
| ParticipantState | Types/ | 上述 91 floats + HP/HP_max/SAN/SAN_max + IsDefending + 忍耐主动CD + 防御CD | 修复 #2/#4 |
| CombatAction | Types/ | `(M1Action?, BrocaAction?, order)` 声明结构；通道动作 = enum + payload | 修复 #3, 回合战斗流程 §2 |
| CombatContext | Types/ | IRng + GameData + CalibrationConfig——只读上下文，**无**可变回合计数（归 CombatState） | 框架 memory |
| WMatrix | Types/ | `float[69,69]` + τ[69] + fid→index 行序映射 | 运行时状态模型 §4.2 |
| SpeedWeights | Types/ | w1/w2/w3 | 回合战斗流程 §3.1 |

91 floats 构成：69 a_j + 4 tone + 15 Gurney + 3 gate = 91（运行时状态模型 §三）。ParticipantState 在此之上携带 HP/SAN/防守状态/CD。

---

## 四、L2 引擎模块规格

### 4.1 WMatrixBuilder

`WMatrixBuilder.Build(GameData data) → WMatrix`（demo 无 LinkState：全部 m_mean = m_default）

数据绑定（修复 #8，逐条对照 [皮层动力学-通用层](../../规则/技能树系统/皮层动力学-通用层.md) §5.1-5.5）：

1. **fan-out broadcast**：同一 dk_name 的多个 functional_id 共享输入权重模式——`W[fid_A][fid_B] = w(dk(fid_A), dk(fid_B))`。通过 `graph_nodes.functional_ids[]` 建 dk_name→fid 列表（12/51 节点 fan-out 2-4）。
2. **w 公式**：`w(A,B) = edr_probability × m_mean × focus_multiplier`（§5.2），自连接 = 0，行归一化 `/(Σ + 0.01)`（ε=0.01，§5.4）。
3. **排除清单（完整）**：Pallidum、Thalamus-Proper、Putamen、Caudate、Accumbens-area、SubthalamicNucleus（CSTC 6 节点）+ brainstem dk_name=None 节点（PAG、上丘、脑桥网状核、小脑皮层，运行时状态模型 §5.7）→ 行=列=0。排除节点 h_j = b_j + s_j，仍由 WC 驱动。
4. **privileged_pathways**（112 条）与 CC 边（776 条）同源进入 W（§5.5）。
5. **cross-ref 测试**：每条边 source/target 必须能经 graph_nodes 解析到 functional_id（csharp-data-layer 已交付）。
6. τ 数组：fast 0.01 / medium 0.05 / slow 0.15 / unknown 0.05（§4.4）。

### 4.2 WcDynamics

`WcDynamics.Step(WcState a, float[] b, float[] s, WMatrix w) → WcState`

**解析解**（修复 #1；偏差声明见 §十二-1）：

```
a_j(t+Δ) = σ(h_j) + (a_j(t) − σ(h_j)) · exp(−Δ/τ_j)
h_j = Σ_k W_jk · a_k(t) + b_j(t) + s_j(t)
σ(x) = 1 / (1 + exp(−(x − 0.5)))
```

- 同步更新：W·a 用上一回合末 a（运行时状态模型 §7.1 步骤 3）。
- 快节点 τ=0.01：exp(−100) ≈ 0 → a_j ≈ σ(h_j)——与原计划的 Δ/τ≥50 分支等价，但免分支。
- 边界：bimodal 12 节点 s_j ≤ 2.0（§4.5）；排除节点 W 行=0 → h_j = b_j + s_j；初始化 a_j(0) = 0.10（§7.3）。

### 4.3 ToneUpdater

`ToneUpdater.Step(ToneState tone, float[] delta) → ToneState`

**解析解**（修复 #1；偏差声明见 §十二-2）：

```
tone_t(t+Δ) = clip(baseline_t + δ_t + (tone_t(t) − baseline_t − δ_t) · exp(−Δ/τ_t), 0, 1)
```

τ: NE 0.5 / DA_VTA 0.3 / DA_SNc 0.8 / 5HT 1.5（§5.3）；baseline: 0.3/0.4/0.5/0.5（§5.4）。

- **δ 实时注入**（修复 #5）：ToneUpdater.Step 在 Phase 4 事件**发射时刻**调用（非 Phase 1 批量），对齐 §5.5 注入时序表。同窗口多事件 δ 加法叠加（§5.5 首段）。
- δ 全局缩放 lever δ_scale（§七，[NEW] 0.3）——文档自身 §5.5 已标 ⚠️ 数值校准延迟（DA_VTA 单次命中即饱和）。
- **b_j 计算**（§5.6）：`b_j = Σ_t tone_t × w_t(j)`，w 从 brainstem 的 **role 字段**取（active→1.0 / modulating→0.5，修复 #8b——不是 projection 字段），clamp [0, 2]（§7.2）。

### 4.4 CstcGating

`CstcGating.Step(WcState a, ToneState tone, GurneyState prev) → (GurneyState, GateState)`

每环路（somatic/cognitive/limbic）独立，§6.3 正典：

1. `c_loop = mean(a[ci])`，ci = `cstc_role == "cortical_input" && cstc_loop == loop`（§6.2；role 字段绑定，修复 #8b）。跨环路节点（caudalanteriorcingulate、superiorfrontal）同时贡献两环路（§6.1）。
2. DA 混合：limbic 0.8VTA+0.2SNc / cognitive 0.4+0.6 / somatic 0.2+0.8（§6.3）。
3. 5 群体输入 u（§6.3 表）：
   - SD1: `u = c × W_SEL × (1 + DA_loop)`；SD2: `u = c × W_CONT × (1 − DA_loop)`
   - STN: `u = c × W_STN + O(GPe) × W_GPe_STN`
   - GPe: `u = O(STN)×W_STN_GPe + O(SD2)×W_CONT_GPe + O(SD1)×W_SEL_GPe`（⚠️ 见 §十三-3）
   - GPi: `u = O(STN)×W_STN_GPi + O(GPe)×W_GPe_GPi + O(SD1)×W_SEL_GPi`
4. 解析更新（§6.3 正典，无偏差）：`a(t+Δ) = u + (a(t) − u) · exp(−25·Δ)`，τ_gurney = 0.04。
5. ramp：O(a) 分段线性 e=0.2；SD1/SD2 斜率 m_SD1 = 1+DA_loop、m_SD2 = 1−DA_loop，其余 m=1.0。
6. `gate_loop = 1 − O_GPi`（§6.4）。

边界：DA_loop=1.0 → m_SD2=0 → SD2 恒 0（合法，NO-GO 全抑制）；global 环路（CstcLoop.Global）无 cortical_input 成员 → 不参与 gating（文档化行为）。

### 4.5 SpeedScoreCalculator（方案B）

暂停点已定方案B（2026-08-06 D4/D5）：`SpeedScoreCalculator`（纯数值）+ `TurnOrderBuilder`（排序 + coin-flip 破平）两个类；SpeedComponents.cs 已存在，补 SpeedWeights record。

```
speed = w1 × 察觉 + w2 × 决断 + w3 × 执行          (w1=w2=w3=1/3 默认，回合战斗流程 §3.1)
察觉 = mean(a(Pericalcarine), a(TransverseTemporal), a(Insula), a(AnteriorCingulateCortex))   (§3.2 节点清单)
决断 = mean(c_loop, 3 环路)                                                                    (§3.3；冲突见 §十二-6)
执行 = mean(a(Precentral), a_SD1_somatic) + M1 占用惩罚                                       (§3.3；Putamen 代理见 §十三-4)
```

- "未显著激活回静息基线 0.10"（§3.3）以 [NEW] 阈值 0.15 实现（CalibrationConfig，§七）。
- 破平：硬币（IRng），§3.4。
- RED 用例（2026-08-06 已定）：等权 (0.5,0.5,0.5)→0.5 / 权重(0.5,0.25,0.25) 偏察觉 (0.5,0.4,0.4)→0.45 / 全满 (1,1,1)→1.0。

### 4.6 DamageCalculator

物理（[核心机制](../../规则/核心机制.md) §4.2 + [基础行动设计](../../规则/技能树系统/操作层/基础行动设计.md) §四）：

```
damage = (4 + weapon_bonus) × (1 + clamp(force, 0, 0.5) + clamp(motivation, 0, 1.0)) × gate_bonus(attack_physical)
hit = roll < 0.85 − 0.10 (L0 回避自动触发, 回合战斗流程 §6.2)      [demo 无 link 修正项]
```

精神（核心机制 §4.3 + 基础行动设计 §四）：

```
san_damage = max(1, round(2 × (1 + motivation) − 忍耐被动)) × gate_bonus(attack_mental)
hp_damage = floor(san_damage / 2)
低 SAN 穿透: 敌方 SAN < 30%×SAN_max → +30%；< 15% → ×2        (核心机制 §4.3——敌方的 SAN)
永远命中
```

- 忍耐被动 = −1（最低受到 1）；忍耐主动 = −2 CD2 占 Broca（demo 未实现，接口预留）。
- 防御状态：物理伤害 ×0.5（−50%，仅物理）；force/motivation 生产者见 §六。

### 4.7 EventProcessor

14 事件 δ pattern 表 + magnitude 表完整实现（运行时状态模型 §5.5 两张表）：

- A6 δ = sign(权重表固定符号)（[NPC AI 行为模型](../../规则/技能树系统/NPC AI 行为模型.md) §3.3，非动态符号）；A6 α = 0。
- `m < 0.01` → 跳过 emit（§5.5）。
- C1 guard：仅 ΔSAN<0 且 old ≥ 30% 且 new < 30%（§5.5 C1 行）。
- α magnitude：A 类 m_α=1.0；B/C/D 类 m_α=m（§5.5）。
- s 打包：`s = W_sensory × α`（69×6 × 6 模态）累计到下一 Phase 1（§4.5/§5.5 时序）。
- D1/D2：HP≤0 结算完成即时 emit 到所有 HP>0 参与者（§5.5 D 注）。

### 4.8 NpcSalience（demo 版）

修复 #6：demo 硬编码 3 基础行动候选集（[NEW] 标注，正式 skill 系统接入后替换）：

| 行动 | 皮层节点（[NEW]） | role / gate |
|------|------------------|-------------|
| physical_attack | Precentral（M1，核心机制 §4.2）+ Putamen | attack_physical / somatic |
| mental_attack | rostralmiddlefrontal（dlPFC）+ parsopercularis（Broca）+ caudalanteriorcingulate（ACC）（§4.3） | attack_mental / cognitive |
| defend | Amygdala + insula（威胁检测，运行时状态模型 §6.5 理由行） | defend / limbic |

```
Salience(skill) = mean(a_j, j ∈ skill.cortical_nodes) × gate_bonus(role) × (1 + tone_bias(role))
tone_bias(role) = Σ_t w_t(role) × (tone_t − baseline_t)        (NPC AI §3.3 权重表)
```

- 选择：Boss argmax / 杂兵 Softmax，`T = T_base + T_SAN`，**T_base = 0.15**（NPC AI §3.4 正典值——审计建议的 1.0 临时值不采纳，文档优先），T_SAN = 0 / +0.10 / +0.30 / ∞（SAN ≥60% / 30-60% / <30% / =0，§9.1）。
- demo 固定 Softmax（杂兵模板），Boss 模板留接口。

---

## 五、L3 实体 / L4 流程

### 5.1 CombatState（Entity）

可变状态：per-participant ParticipantState + 回合计数 + 事件日志 + 行动队列。Apply 方法：ApplyDamage / ApplyTone / ApplyGurney / ApplyDefense。

### 5.2 TurnManager（Flow）——修复 #7 后的回合管线

```
Phase 1 (情境更新, 回合开始):
  1. tone 继承（δ 主体已在 Phase 4 实时注入——修复 #5；此处仅处理 D1/D2 等跨窗口残留，如有）
  2. b_j = Σ tone × w
  3. WcDynamics.Step(prev_a, b, 上回合累计 s, W) → a
  4. c_loop + DA_loop 混合
  5. CstcGating.Step → gurney, gates

Phase 2 (继承): 连续状态（a/tone/gurney/gate）原样带入，不递减 CD

Phase 3 (速度重算): SpeedScoreCalculator + TurnOrderBuilder → 行动顺序队列

Phase 4 (按序执行): for each participant in order:
  0. 行动窗口开始: CD 递减（修复 #7）——防御 CD、忍耐主动 CD 在**自己的**窗口开始时 tick
  1. NPC 行动选择 (NpcSalience) / 玩家输入
  2. 声明: CombatAction (M1Action?, BrocaAction?, order)——双通道，各自独立目标（回合战斗流程 §2）
  3. 响应窗口 (stub, §一范围)
  4. 结算: DamageCalculator + EventProcessor
  5. 事件发射时刻: δ 实时 → ToneUpdater.Step（发射者）；D1/D2 → 所有 HP>0 参与者；s 只累计不注入
  6. HP=0 → 立即从队列移除（跳过剩余窗口），触发 D1/D2

Phase 5 (回合收束): 结束条件检查（一方 HP=0 全灭 / 回合上限）→ 下一回合 Phase 1
```

SAN 阈值行为（重要改进）：SAN <30% 恐慌（C1 事件）、<15% 崩溃、=0 随机行动（T=∞ 均匀随机），全部在 5.2 管线中生效。

### 5.3 ActionResolver（Flow）

Phase 4 声明→响应→结算 dispatch。响应窗口内容按 §一范围 stub（保留接口 + 注释引用设计章节）。

---

## 六、伤害结算接线（修复 #10 全文）

| 接线 | 公式 | 来源 |
|------|------|------|
| gate → 结算 | damage × gate_bonus(role)（§6.5 表；perceive/support bypass=1.0） | 运行时状态模型 §6.5 |
| motivation_mod | `clamp(tone_bias(attack_physical), −1, +1.0)`（cap +100% 对齐核心机制 §4.2；用 NPC AI §3.3 权重表） | [NEW] 生产者 |
| force_mod | `clamp(DA_SNc − baseline_SNc, 0, 0.5)`（SNc 运动启动 → 出力，cap +50%） | [NEW] 生产者 |
| 防御 −50% | IsDefending → 物理伤害 ×0.5；M1 通道被占（修复 #4）；CD 1 在自己窗口起点 tick | 基础行动设计 §四 |
| L0 回避 −10% 命中 | 物理命中判定路径无条件生效（自动触发，回合战斗流程 §6.2） | 修复 #10 |
| 精神 HP 成分 | floor(san_damage / 2) | 基础行动设计 §四 |

---

## 七、校准常量 CalibrationConfig（审计条件 3）

单一 static class，全部 [NEW] 占位注明来源（设计文档 or 待校准）；对应 issue 关闭后摘除 [NEW] 标注。

| 常量 | 值 | 来源 |
|------|-----|------|
| SpeedWeights w1/w2/w3 | 1/3 | 回合战斗流程 §3.1（默认等权） |
| m_default | 0.3 | 皮层动力学 §5.3 |
| T_base | 0.15 | NPC AI §3.4 |
| δ_scale | 0.3 [NEW] 待校准 | 运行时状态模型 §5.5 ⚠️ 延迟注 |
| scale_mental | 未启用（demo 用固定 base 2） | 运行时状态模型 §8.1 ⚠️ 待赋值 |
| expected_damage | 4（A1 m 公式分母） | 核心机制 §4.2 |
| M1 持续占用惩罚 | −0.1 [NEW] 待校准 | 回合战斗流程 §3.3（值未定义） |
| 察觉"未显著激活"阈值 | 0.15 [NEW] 待校准 | 回合战斗流程 §3.3（值未定义） |
| demo 模板 | 玩家 HP 50/SAN 80；NPC 杂兵 HP 15/SAN 60 [NEW] | 核心机制 §10.1 表取中值 |

---

## 八、验证标准（审计条件 4）

原计划"a(t) 收敛到 0.10"**错误**——0.10 是初始条件（§7.3）不是吸引子。修订：

- **M1 里程碑（WcDynamics GREEN 后立即执行）**：零事件单参与者 trace——tone=baseline、s=0 运行 30 回合，**实测** a(t) 静息不动点并写入文档（理论参考：行和≈1 且 b≈0 时 x=σ(x) → x≈0.5；实际 b_j>0 会略高，以实测为准）。
- 控制台输出增强（§九）——目视验证 tone 回基线、gate 响应、顺序变化、伤害收敛。
- 全部 RED→GREEN 测试通过（§十）+ `dotnet build` 零错误。

---

## 九、控制台 harness 规格（YouAreNotTheFish.Console）

- 加载真实数据 → 2 参与者（玩家模板 + NPC 杂兵模板，§七 demo 值）。
- 每回合输出（在原计划基础上增强，审计条件 4）：
  - 顺序（各 speed 分量展开）、每参与者 a(t) 摘要（sensory/Precentral/Broca 节点）、tones、gates、行动声明；
  - 结算详情：damage 公式逐因子展开（base × force × motivation × gate）、SAN 阈值跨越（C1）、事件清单（A1 m=…、B1 m=…）；
  - 回合末：HP/SAN、CD 状态、结束原因。
- 静息 trace 模式（M1 里程碑）：`--trace-resting 30` → 30 回合零事件 → a(t) 不动点测量输出。
- 种子 RNG（--seed），可复现。

---

## 十、测试清单

按 feature 划分（§十一），每 feature 自带 RED→GREEN。关键边缘用例（审计补充）：

| 模块 | 用例 |
|------|------|
| WcDynamics | 快节点 exp(−100)≈0 → σ(h)；慢节点平滑过渡；静息吸引子 ≈0.5（非 0.10）；bimodal s=2.0 输入；排除节点 W 行=0 仍响应 b/s；init 0.10 |
| ToneUpdater | 解析解：δ=0 回基线；大 δ clip [0,1]；连续双脉冲（back-to-back）；DA 饱和边界 |
| CstcGating | DA 极端 0/1 下 ramp 斜率（m_SD2=0 at DA=1.0）；c_loop=0 门控抑制；跨环路节点双贡献；解析收敛到 u |
| SpeedScore | 3 RED 用例（§4.5）；破平 coin flip 固定 RNG 确定性 |
| Damage | 命中率分布（固定 RNG）；精神永远命中 + 最低 1；低 SAN 穿透边界（敌方恰好 30%/15%）；防御 −50% 仅物理 |
| EventProcessor | A1/B1 pattern；A6 sign 固定符号；m<0.01 skip；C1 guard（被动 SAN_max 变化不触发）；D1/D2 即时到所有 HP>0；s 打包与 α |
| NpcSalience | 3 行动候选；tone_bias 计算；T=0.15 与 T_SAN 分段；SAN=0 均匀随机 |
| Flow | 整回合 Phase 1-5；CD 在自己窗口起点递减；HP=0 即时移出队列；防御后 M1 被占 |

---

## 十一、实施顺序与 feature 划分（审计修订序）

| Step | Feature | 内容 | 状态 |
|------|---------|------|------|
| 0 | csharp-engine（本计划） | 计划修订 + 再审计 + sign-off | 进行中 |
| 1 | csharp-data-layer | L1 数据层 | ✅ 已交付 |
| 2 | csharp-engine-types | Types/ 状态类型（§三） | 待开始 |
| 3 | csharp-wmatrix | WMatrixBuilder | 待开始 |
| 4 | csharp-wc-dynamics | WcDynamics → **M1 静息 trace 里程碑** | 待开始 |
| 5 | csharp-tone | ToneUpdater + b_j | 待开始 |
| 6 | csharp-cstc | CstcGating | 待开始 |
| 7 | csharp-speed | SpeedScoreCalculator + TurnOrderBuilder（含 2026-08-06 RED 用例） | 待开始 |
| 8 | csharp-damage | DamageCalculator | 待开始 |
| 9 | csharp-events | EventProcessor | 待开始 |
| 10 | csharp-flow | CombatState + TurnManager + ActionResolver | 待开始 |
| 11 | csharp-console | Console harness | 待开始 |
| 12 | csharp-smoke | Smoke 集成测试 | 待开始 |

每 step 一个 feature：任务issue → spec → 审计 → sign-off → 工作issue → 自审（二层流水线）。Step 2 的 spec 同时建立引擎层 spec 模板（§七自检清单：数学公式逐项 vs 设计文档对照、边界值、确定性）。

---

## 十二、对设计文档的偏差声明（审计条件 6）

| # | 偏差 | 设计文档原文 | 计划采用 | 理由 |
|---|------|------------|---------|------|
| 1 | WC 更新用解析解 | 运行时状态模型 §4.3 Euler + clip | 解析指数解 | 审计数值证明：设计自身参数（Δ=1, τ=0.01-0.15）下 Euler 产生 bang-bang 振荡。先例：§6.3 Gurney 已用解析解（"Δ/τ 大但 k 也大，exp(−25)≈0，a→u"）。快节点两者等价（exp(−100)≈0） |
| 2 | tone 更新用解析解 | §5.2 Euler（§7.1 步骤 1 亦 Euler） | 解析指数解 | 同上（τ_tone 0.3-1.5，Δ/τ 0.67-3.33） |
| 3 | δ 注入时序 | §7.1 步骤 1 写"Phase 1 批量"；§5.5 注入时序表写"实时" | 实时（§5.5 为准） | 文档内部不一致，取 §5.5（更细粒度章节 + 神经科学理由）；审计修复 #5 |
| 4 | CD 递减时机 | 回合战斗流程 §9.1 "每回合开始" | 自己行动窗口起点（§5.1/§四 更细粒度表述） | 文档内部不一致，取行动窗口版本；审计修复 #7 |
| 5 | 静息吸引子 | 回合战斗流程 §3.2 "未显著激活回到静息基线 0.10" | a(t) 实测吸引子 ≈0.5（0.10 仅初始值 §7.3） | 审计数值证明 0.10 非不动点 |
| 6 | 决断分 | 回合战斗流程 §3.3 `mean(c_loop)(t)` | 同左（mean(c_loop)） | 与运行时状态模型 §8.1 "GPi 竞争解决时间代理"冲突——取 §3.3 具体公式，§8.1 为指针。冲突记录见 §十三-1 |
| 7 | tone 基线范围 | 核心机制 §十一 [0.1, 2.0] | NPC AI §4.1 [0, 1] + clip | 文档内部冲突，取 NPC AI（与 tone ∈ [0,1] 一致）。冲突记录见 §十三-2 |

---

## 十三、设计待决清单（升级为用户决策点，不阻塞编码）

1. **决断分公式冲突**：`mean(c_loop)`（回合战斗流程 §3.3）vs GPi 竞争解决时间代理（运行时状态模型 §8.1）——计划按 §3.3 实现，建议后续把 §8.1 更新为指针。
2. **tone baseline 范围冲突**：核心机制 §十一 表 [0.1, 2.0] vs NPC AI §4.1 [0, 1]——建议统一为 [0,1]（tone 定义域）。
3. **§6.3 GPe 输入方程引用 `W_SEL_GPe`，权重表无此项**——需文档补值。
4. **执行分 Putamen 项**：Putamen 是 CSTC 节点（无 WC a(t)）——计划用 somatic 环路 Gurney a_SD1 作代理（[NEW] 映射，§4.5）。
5. **M1 持续占用惩罚、察觉"未显著激活"阈值**：设计引用但未给值 → CalibrationConfig [NEW] 占位（§七）。
6. **A6 sign 依赖 NPC AI §3.3 权重表**——demo 仅 3 基础行动不触发 A6，实现保留。
7. **observer_filter 函数**（运行时状态模型 §5.5 [NEW] 延迟）——demo 不实现。

---

## 参数速查表

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| WC 时间常数 | τ_j | 0.01/0.05/0.15/0.05 | 运行时状态模型 §4.4 |
| WC 初始激活 | a_j(0) | 0.10 | §7.3 |
| sigmoid 中点 | σ 中点 | 0.5 | §4.1 |
| 归一化 ε | ε | 0.01 | 皮层动力学 §5.4 |
| m 默认值 | m_default | 0.3 | 皮层动力学 §5.3 |
| tone 时间常数 | τ_tone | 0.5/0.3/0.8/1.5 | 运行时状态模型 §5.3 |
| tone 基线 | baseline | 0.3/0.4/0.5/0.5 | §5.4 |
| b_j 上限 | b_max | 2.0 | §7.2 |
| 投射权重 | w_proj | active 1.0 / modulating 0.5 | §5.6 |
| Gurney τ | τ_gurney | 0.04（k=25） | §6.3 |
| ramp 阈值/斜率 | e / m | 0.2 / 1.0 | §6.3 |
| DA 混合 | — | 0.8/0.2, 0.4/0.6, 0.2/0.8 | §6.3 |
| Gurney 权重 | W_SEL 等 | 见 §6.3 权重表 | §6.3 |
| 速度权重 | w1/w2/w3 | 1/3 | 回合战斗流程 §3.1 |
| 物理基础伤害 | — | 4 | 核心机制 §4.2 |
| 物理命中率 | — | 0.85（−0.10 L0 回避） | 核心机制 §4.2, 回合战斗流程 §6.2 |
| force cap | — | +50% | 核心机制 §4.2 |
| motivation cap | — | +100% | 核心机制 §4.2 |
| 精神基础伤害 | — | 2 SAN + floor(SAN/2) HP | 核心机制 §4.3, 基础行动设计 §四 |
| 忍耐被动/主动 | — | −1 最低1 / −2 CD2 | 基础行动设计 §四 |
| 低 SAN 穿透 | — | 敌方 <30% +30%、<15% ×2 | 核心机制 §4.3 |
| 防御减伤 | — | 物理 ×0.5, CD1 | 基础行动设计 §四 |
| SAN 阈值 | — | ≥60% 稳定 / <30% 恐慌 / <15% 崩溃 / =0 随机 | 核心机制 §5.1 |
| Softmax 温度 | T_base | 0.15 | NPC AI §3.4 |
| T_SAN | — | 0 / +0.10 / +0.30 / ∞ | NPC AI §3.4 |
| δ 缩放 | δ_scale | 0.3 [NEW] | §七 |
| 事件跳过阈值 | m_min | 0.01 | 运行时状态模型 §5.5 |

---

## 变更日志

| 版本 | 日期 | 变更 | 触发 |
|------|------|------|------|
| v1.0 | 2026-08-13 | 审计修订版——吸收 10 关键修复 + 13 重要改进 + 6 放行条件 | 2026-08-12 workflow 审计（有条件放行） |

---
*创建: 2026-08-13 | 更新: 2026-08-13*
*关联: [csharp-data-layer map](../csharp-data-layer/map.md), [运行时状态模型](../../规则/技能树系统/运行时状态模型.md), [回合战斗流程](../../规则/回合战斗流程.md), [核心机制](../../规则/核心机制.md), [皮层动力学-通用层](../../规则/技能树系统/皮层动力学-通用层.md), [NPC AI 行为模型](../../规则/技能树系统/NPC AI 行为模型.md), [基础行动设计](../../规则/技能树系统/操作层/基础行动设计.md)*
