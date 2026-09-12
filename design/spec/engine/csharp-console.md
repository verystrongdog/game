# csharp-console — 实现规格

> 控制台 harness（plan §九）——加载真实脑数据 → 2 参与者 1v1（玩家 vs NPC 杂兵）→ 五阶段战斗 → 每回合完整输出 + 静息 trace 模式 + 种子 RNG。玩家行动经键盘 IActionProvider 注入（step 10 接口的玩家实现）。版本: v1.2

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | `YouAreNotTheFish.Console` 可执行项目（引用 Core）；`CliArgs`（--seed/--trace-resting 解析）；`PlayerActionProvider`（键盘 IActionProvider）；`RoundRenderer`（§九 每回合输出渲染）；`Program`（主循环：Create → StepRound 循环 → 结束）；静息 trace 模式（--trace-resting N → 30 回合零事件 → 不动点测量输出） |
| 不覆盖 | NPC AI 全量（step 10 NpcSalience demo 版已交付）；Unity 呈现；存档/读档；战斗外内容（探索/对话等） |
| 前置依赖 | csharp-data-layer ✅ / csharp-engine-types ✅ / csharp-wmatrix ✅ / csharp-wc-dynamics ✅ / csharp-tone ✅ / csharp-cstc ✅ / csharp-speed ✅ / csharp-damage ✅ / csharp-events ✅ / csharp-flow ✅（261/261） |
| 阻塞 | step 12 csharp-smoke（Smoke 集成测试——用 console 或直接引擎） |

## 二、项目结构与 CLI

### 2.1 项目

`code/src/YouAreNotTheFish.Console/YouAreNotTheFish.Console.csproj`——`<OutputType>Exe</OutputType>`、`net8.0`、ProjectReference → `YouAreNotTheFish.Core`。命名空间 `YouAreNotTheFish.ConsoleApp`。

### 2.2 CliArgs（参数解析，纯函数）

```csharp
public sealed record CliArgs(ulong Seed, int? TraceRestingRounds)
{
    public static CliArgs Parse(string[] args);
}
```

- `--seed <n>`：RNG 种子（默认 42）。非法值（非数字/负数/缺失）→ CliUsageException（含用法说明）。
- `--trace-resting <n>`：静息 trace 模式（n 回合零事件；默认 30）。**非法值（v1.1 补——审计 C9/console-13/C13）：非数字 / < 1 / 缺失 → CliUsageException**（与 --seed 同规则）。
- **重复参数/多余值（v1.1 补——审计 console-15）**：同参数出现两次 → 后者覆盖（最后出现者胜）；参数后多余 token → CliUsageException。
- 其他参数 → CliUsageException。
- 无参数 → 正常战斗模式。

### 2.3 战斗模板（§七 demo 值）

- 玩家：HP 50 / SAN 80（`cal.PlayerHp` / `cal.PlayerSan`）
- NPC 杂兵：HP 15 / SAN 60（`cal.NpcHp` / `cal.NpcSan`）
- teams = [1, 2]

## 三、接口定义

### 3.1 PlayerActionProvider（玩家键盘 IActionProvider）

```csharp
public sealed class PlayerActionProvider(TextReader input, TextWriter output) : IActionProvider
{
    public CombatAction GetAction(int participantIndex, CombatState state, CombatContext ctx);
}
```

- 职责：玩家键盘输入（1v1 场景——TargetId 固定为对方参与者；demo 无多目标选择）。
- 输入提示（中文）：`[玩家] 行动 (1=物理攻击 2=精神攻击 3=防御 0=等待): `——解析 1/2/3/0；非法输入 → 重新提示（循环，最多 3 次后默认 0=等待）。**EOF/null 输入（v1.1 补——审计 console-10）：ReadLine 返回 null（stdin 关闭/重定向空输入）计为一次非法输入（同非法值计数），3 次后默认等待——非交互运行不挂死**。
- 行动 → CombatAction 映射：1 → M1=PhysicalAttack（TargetId=对方）；2 → Broca=MentalAttack（对方）；3 → M1=Defend；0 → 空声明。
- 目标解析：`state.Teams[p] != state.Teams[selfIndex]` 的第一个参与者（复用 NpcSalience 同款规则——1v1 即对方）。
- 确定性：外部输入（键盘），无此约束。
- 可测性：TextReader/TextWriter 注入——测试可喂输入流断言输出。

### 3.2 RoundRenderer（回合输出渲染，纯函数）

```csharp
public static class RoundRenderer
{
    public static string RenderRound(int round, CombatState state, TurnResult result, TurnManager tm, GameData data, CalibrationConfig cal);
    public static string RenderSetup(CombatState state, GameData data);
    public static string RenderResting(WcState resting, GameData data);
}
```

- 职责：§九 每回合输出清单（人类可读 + 结构化可断言）。纯函数（无 I/O）——测试直接断言字符串。**签名 v1.1 修正（审计 C11/console-08）：+CalibrationConfig cal——结算 m 重算（events §5.3 公式消费 ExpectedDamage/BaseMentalDamage 等）与结束原因上限数需要。v1.2 修正（审计 C-01）：+TurnManager tm——段 3 [顺序] 与段 6 [行动] 消费 tm.LastRoundOrder/LastRoundActions（决策 D1）**。
- **名字来源（审计 C10 声明）**：ParticipantState 无名字字段——console 硬编码 `p0=玩家`、`p1=杂兵`（索引语义，§2.3 模板序）。渲染 `{名字}` = 该映射。
- RenderRound 输出段（§九 清单逐项，v1.1 补 a(t)/因子段——审计 C3/C4/console-07/console-08）：
  1. `===== 回合 N =====`
  2. `[速度] p{i} {名字}: 察觉 {x:F3} / 决断 {y:F3} / 执行 {z:F3} → 总分 {s:F3}`（speed 分量展开——`new SpeedScoreCalculator(data, cal)` 实例重算（审计 C14：实例方法）；**回合末快照重算语义（v1.1 统一表述——审计 console-06）：分量基于渲染时点 a/salience/isDefending（与 Phase 3 时点可能不同——isDefending 已在窗口开始清除（Q3）），标注「回合末」**）
  3. `[顺序] p3 → p1 → p2`（`tm.LastRoundOrder`——决策 D1；StepRound 后有效）
  4. `[状态] p{i}: HP {hp}/{max} SAN {san}/{max} tone(NE {t:F3} VTA {t:F3} SNc {t:F3} 5HT {t:F3}) gates(S {g:F3} C {g:F3} L {g:F3})` + `[CD] Defend={cd}`（IsDefending 时标注 `[防御中]`）
  5. **`[a(t)] p{i}: sensory {s:F3} / Precentral {p:F3} / Broca {b:F3}`（v1.1 补段——§九「每参与者 a(t) 摘要（sensory/Precentral/Broca 节点）」；sensory = mean(a[Pericalcarine], a[TransverseTemporal], a[Insula], a[AnteriorCingulateCortex]) 察觉四节点、Precentral = a[Precentral]、Broca = a[ParsOpercularis]——fid 解析同 NpcSalience 方式）**
  6. `[行动] p{i} {名字}: {动作描述}`（`tm.LastRoundActions`——决策 D1；物理/精神/防御/等待）
  7. `[结算] {事件清单}`：每事件一行（**v1.1 修正——审计 C7/console-09：示例与 {m:F4} 格式统一；v1.2 修正——审计 D8/Δ-C07：A1 示例补「命中」后缀与 §5.2 模板一致**）——`A1 m=0.6250 (dealt 2.5 / expected 4.0 命中)`、`B1 m=0.1667 (|ΔHP| 2.5 / 15.0)`、`C1 恐慌跨越 (SAN 18.5→17.9)`、`D1/D2 倒下广播 (p{actor})`
  8. **`[因子] p{i}→p{j}: {因子描述}`（v1.1 补段——§九「damage 公式逐因子展开（base × force × motivation × gate）」；v1.2 修正——审计 D2/Δ-C04/C-02：按事件类型区分形态）**：
     - PhysicalDamageEvent（A1/A2/A5/B1/B2）→ `base {BaseDamage} × force {ForceMod:F3} × motivation {MotivationMod:F3} × gate {GateBonus:F3}`（字段来自事件——flow §5.1 已填）
     - MentalDamageEvent（A4/B4）→ `base {cal.BaseMentalDamage} × motivation {MotivationMod:F3} × gate {GateBonus:F3}`（**精神公式无 force 因子——MentalDamageEvent 无 BaseDamage/ForceMod 字段，base 回退 cal 常量**）
     - StatusChangeEvent（C1/D1/D2）/ 其他 → 无 [因子] 行（非伤害事件）
  9. `[结束] {原因}`：`TeamDefeated（一方全灭——Hp≤0 ∨ San≤0）` / `MaxRounds（回合上限 {cal.MaxRounds} 达成）`（IsOver 为 true 时；上限数取 cal——审计 C11）。**v1.2 裁决（审计 D7/Δ-C03/C-05）：[结束] 唯一输出源 = RenderRound 段 9；§3.3 主循环退出后不重复输出**
- RenderSetup：`== 战斗开始 ==` + 参与者列表（名字/HP/SAN/队伍）——**循环前输出（v1.1 时序修正——审计 C7/console-11）**。
- RenderResting：`== 静息不动点 ==` + 48 active 节点 min/max（**F3 渲染串断言——审计 C5：M1 实测 max=0.771229，浮点区间比较取 [0.535, 0.772]**）+ 排除节点三组值（对齐 csharp-tone AC-15 输出形态）。

### 3.3 Program（主循环）

```csharp
public static class Program
{
    public static int Main(string[] args);
}
```

- 流程（v1.1 修正——审计 C2/C7/C8/console-09/console-11；v1.2 修正——审计 Δ-C01/D6/Δ-C06/C-01/D7）：
  1. `CliArgs.Parse(args)`（异常 → stderr 用法 + 退出 1）
  2. 战斗模式：
     - `data = GameDataLoader.LoadAll(dataDir)`；`cal = CalibrationConfig.Default`
     - **ctx 构造（审计 C8 补定义）**：`ctx = new CombatContext(new DeterministicRng(cli.Seed), data, cal)`——`--seed` → IRng 接线点（AC-11 确定性依赖）
     - `state = CombatState.Create([玩家, 杂兵], [1,2], data, cal)`（玩家 = CreateDefault(cal.PlayerHp, cal.PlayerSan)、杂兵 = CreateDefault(cal.NpcHp, cal.NpcSan)）
     - **组合 provider（v1.2 修正——审计 Δ-C01：p 自由变量伪码不可执行）**：定义 `CompositeActionProvider(IActionProvider player, IActionProvider npc) : IActionProvider`（console 层新类——`GetAction(p, state, ctx)` 内按 participantIndex 分派：p==0 → player、否则 → npc）；`playerProvider = new PlayerActionProvider(Console.In, Console.Out)`、`npcProvider = new NpcActionProvider()`（flow §3.1 已交付——**构造签名补定义：无参**）；`provider = new CompositeActionProvider(playerProvider, npcProvider)`
     - `tm = new TurnManager(data, cal, provider)`
     - **循环前输出 RenderSetup**（审计 C7 时序修正）；`while !tm.IsOver(state): result = tm.StepRound(state, ctx); 输出 RenderRound(round, state, result, tm, data, cal)`（**+tm 传入——v1.2 审计 C-01：段 3/6 消费 LastRoundOrder/LastRoundActions**）；**循环后不输出 [结束]（v1.2 裁决——审计 D7/Δ-C03/C-05：RenderRound 段 9 为唯一输出源，防重复行）**
  3. 静息 trace 模式（`--trace-resting`）：单参与者（玩家模板）零事件 N 回合 → RenderResting 输出。实现（v1.2 修正——审计 D6/Δ-C06/C-04：补 ctx 与 WaitProvider 定义）：
     - `WaitProvider`（console 层新类，恒空声明）：`sealed class WaitProvider : IActionProvider { GetAction(...) => new CombatAction(); }`
     - `state = CombatState.Create([玩家], [1], data, cal)`；`tm = new TurnManager(data, cal, new WaitProvider())`；`ctx = new CombatContext(new DeterministicRng(cli.Seed), data, cal)`（与战斗模式同接线）；循环 `tm.StepRound(state, ctx)` N 次 → `RenderResting(state.Participants[0].Wc, data)`。
- dataDir 定位：`AppContext.BaseDirectory` 向上回溯找 `data/`（镜像测试项目 DataDirCandidates——console 与测试共用数据源约定）。
- 退出码：0（正常结束）；1（CliUsageException 参数错误/数据目录缺失——错误信息到 stderr）。

## 四、枚举与常量

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| RNG 种子 | — | 42（CliArgs 默认） | §2.2 |
| 静息 trace 回合 | — | 30（--trace-resting 默认） | §2.2（运行时状态模型 §7.3） |
| 玩家模板 | PlayerHp/PlayerSan | 50/80（已交付） | CalibrationConfig（**不重定义**） |
| 杂兵模板 | NpcHp/NpcSan | 15/60（已交付） | CalibrationConfig（**不重定义**） |

**决策 D1（TurnManager 暴露行动声明与行动序）**：§九 要求输出「行动声明」与「顺序」。TurnResult 只含事件（不含声明与序）。方案：**TurnResult 不扩展**（B6 延续）——console 从 `state.History.Last()` 事件反推声明不可靠（miss 无事件、等待无事件）。**推荐：TurnManager 暴露 `LastRoundActions`（IReadOnlyList<(int Participant, CombatAction Action)>）与 `LastRoundOrder`（int[]）**——实例属性，StepRound 末尾写入（StepRound 调用后有效，下回合覆盖）。console 渲染消费；不改变 TurnResult（类型变更面最小——TurnManager 内部字段）。**这是 L2 类型变更吗？否——TurnManager 是 Flow 层新类，非 types 交付物。** §七 自检项 9 声明。

## 五、交叉引用约束（输出细节）

### 5.1 速度分量重算（RenderRound 段 2）

- 调用 `SpeedScoreCalculator.ComputeComponents(a, salience, gurney, isDefending)` + `ComputeScore`（与 TurnManager Phase 3 同参）——渲染时 state 已是回合末；**salience 来源（v1.2 修正——审计 Δ-C05）：`state.Salience[p]`（flow §2.2 CombatState 已交付访问器——ApplyGurney 的 salience 参数存储槽）**；**分量值 = 回合末快照重算**（数值与 Phase 3 时点可能不同——isDefending 已在窗口开始清除（Q3），demo 语义：展示当前状态的速度分量，标注「回合末」）。
- 输出格式：`察觉 {x:F3} / 决断 {y:F3} / 执行 {z:F3} → 总分 {s:F3}`。

### 5.2 结算详情（RenderRound 段 7）

- 每事件一行，格式（§九「damage 公式逐因子展开 + 事件清单」；**v1.2 修正——审计 Δ-C10：A2 m 与 AC-13 F4 格式统一**）：
  - `A1 m={m:F4} (dealt {dealt}/{expected} 命中)` / `A2 m=0.0000 (miss)`
  - `B1 m={m:F4} (|ΔHP| {delta}/{max})`、`B2 m={m:F4} (回避)`、`A5 m={m:F4} (防御成功)`
  - `A4 m={m:F4} (SAN {san}/{expected})`、`B4 m={m:F4} (|ΔSAN| {delta}/{max})`
  - `C1 恐慌跨越 (SAN {before}→{after})`、`D1/D2 倒下广播 (p{actor})`
  - `Heal/LinkGrowth no-op`（demo 无——格式预留）
- m 值：**渲染时重算**（事件字段套 m 公式——与 events spec §5.3 同式；确定性组件可复算）。

### 5.3 结束原因（RenderRound 段 9——v1.2 修正段号，审计 D3/Δ-C02/C-06）

- `tm.IsOver(state)` 为 true 时输出（**唯一输出源——v1.2 裁决，审计 D7/Δ-C03/C-05：主循环退出后不重复**）。原因判定（console 自判，§5.5 双口径 + 回合上限）：`TeamDefeated（一方全灭——Hp≤0 ∨ San≤0）` / `MaxRounds（回合上限 {cal.MaxRounds} 达成）`。输出后主循环退出。

## 六、验收标准

| AC | 验收标准 | 锚点/断言 |
|----|---------|-----------|
| AC-1 | CliArgs 解析 | `--seed 7` → (7, null)；`--seed 7 --trace-resting 30` → (7, 30)；`--trace-resting` 缺值 / `--trace-resting abc` / `--trace-resting -5`（**v1.1 补——审计 C9**）/ `--seed abc` / `--seed -1` / 未知参数 → CliUsageException；重复参数后者覆盖（`--seed 1 --seed 2` → 2——**v1.1 补，审计 console-15**）；无参数 → (42, null) |
| AC-2 | PlayerActionProvider 输入映射 | 喂 "1\n" → M1=PhysicalAttack（TargetId=对方）；"2\n" → Broca=MentalAttack；"3\n" → M1=Defend；"0\n" → 空声明；"x\n2\n"（非法后重试）→ 第二次生效；连续非法 3 次 → 默认等待 |
| AC-3 | RenderSetup | 含玩家/杂兵名字与 HP/SAN/队伍行 |
| AC-4 | RenderRound 速度段 | 含 `[速度]` + 三分量 F3 格式 + 总分；两参与者各一行 |
| AC-5 | RenderRound 行动段（D1） | 含 `[行动]` + 动作描述（物理/精神/防御/等待）；等待参与者显示「等待」 |
| AC-6 | RenderRound 结算段 | 事件清单逐行（A1 m=… 格式）；miss → A2 行；防御 → A5 行；C1 → 恐慌跨越行 |
| AC-7 | RenderRound 状态段 | 含 HP/SAN/tone 四分量/gates/CD 标注 |
| AC-8 | 结束输出 | IsOver 后含 `[结束]` + 原因（全灭/上限） |
| AC-9 | 完整战斗冒烟 | `--seed 42` 无参数跑完整战斗（上限 = cal.MaxRounds=50——**v1.1 修正：原「60」与正典矛盾，审计 C1/console-03**）→ 正常退出 0；每回合 RenderRound 非空；NPC（p1）行动由 NpcActionProvider 自动（无键盘提示——审计 C2 组合 provider） |
| AC-10 | 静息 trace 模式 | `--trace-resting 30` → 输出 `== 静息不动点 ==` + active 节点 min/max **渲染串（F3）∈ [0.535, 0.772]（v1.1 修正——审计 C5：M1 实测 max=0.771229 > 0.771，浮点区间取 0.772）** |
| AC-11 | 确定性 | **脚本化输入前提（v1.1 补——审计 console-04）：两次运行喂同一脚本化输入流（PlayerActionProvider 的 TextReader 注入同一输入序列）** + `--seed 42` → 输出逐字符相同（重定向 stdout 比较） |
| AC-12 | 异常 | 数据目录缺失 → 非零退出 + 错误信息；CliUsageException → 退出 1 + stderr 用法；**数据校验失败（`JsonException`，如四类三体边缺 `role`——Grilling #106）→ 退出 1 + stderr「数据校验失败: {ex.Message}」（无未处理异常堆栈）** |
| AC-13 | 渲染格式（v1.1 新增——审计 C3/C4/C7；v1.2 补 [顺序] 行——审计 C-07） | 完整回合输出含：`[速度]` 三分量行 ×2、`[顺序]` 行（`p{0} → p{1}` 形态——审计 C-07 补锚点）、`[a(t)]` 行 ×2（sensory/Precentral/Broca）、`[状态]` 行 ×2、`[行动]` 行 ×2（等待参与者含「等待」）、`[结算]` 事件行（m 为 F4 格式——`m=0.6250` 形态，审计 C7 格式统一；**A2 miss 行同 F4——`m=0.0000 (miss)`，v1.2 修正审计 Δ-C10**）、`[因子]` 行（物理四因子 / 精神三因子无 force——v1.2 修正审计 D2/Δ-C04）、结束含 `[结束]` 原因（**仅最终回合一次——v1.2 裁决审计 D7**） |

## 七、本 spec 自检清单

1. **数学公式逐项对照**——结算 m 重算与 events spec §5.3 同式；速度重算与 flow spec Phase 3 同参。
2. **数值断言全部实测**——AC-10 静息区间 M1 实测；其余为格式/结构断言（无新数值锚点——复用组件级已验证）。
3. **计算顺序契约明确**——主循环 Create → StepRound → Render；渲染发生在回合末（状态已推进）。
4. **接口注释先行**——CliArgs/PlayerActionProvider/RoundRenderer/Program XML doc。
5. **边界值覆盖**——非法参数、非法输入重试、空声明、防御标注、miss 行、C1 行、上限结束。
6. **确定性**——同种子同输出（AC-11）；RoundRenderer 纯函数。
7. **偏差声明完整**——D1（TurnManager 暴露 LastRoundActions/LastRoundOrder）标注；玩家输入不确定性声明。
8. **常量复用漂移注**——PlayerHp/PlayerSan/NpcHp/NpcSan 消费不重定义；无新常量。
9. **类型变更声明**——本 step 无 L2 类型变更（D1 是 Flow 层 TurnManager 属性新增，非 types 交付物）。

## 八、偏差声明

| # | 偏差 | 理由与处置 |
|----|------|-----------|
| B1 | TurnManager 新增 LastRoundActions/LastRoundOrder 属性（决策 D1） | §九 要求输出行动声明与顺序；TurnResult 不扩展（B6 延续）——Flow 层属性，非 L2 类型变更 |
| B2 | 速度分量 = 回合末快照重算（非 Phase 3 时点值） | 渲染在回合末进行，重算展示当前状态分量；标注「回合末」——v1.1 统一表述（审计 console-06） |
| B3 | 玩家输入 3 次非法（含 EOF/null）→ 默认等待 | 防键盘死循环 + 非交互运行不挂死（demo 健壮性；审计 console-10） |
| B4 | 结算 m 渲染时重算（非事件携带） | events spec 事件不携带 m（派生量）；重算公式与 events §5.3 同式（消费 cal——RenderRound 签名 +cal，审计 C11/console-08） |
| B5 | dataDir 回溯定位 | console 与测试项目共用约定；非打包部署场景（demo 阶段） |
| B6 | 组合 provider（p==0 玩家键盘 / p==1 NpcActionProvider） | 1v1 双参与者行动来源接线（审计 C2）；NpcActionProvider 已交付（flow spec §3.1） |
| B7 | 参与者名字硬编码 p0=玩家 / p1=杂兵 | ParticipantState 无名字字段（审计 C10）；索引语义 + §2.3 模板序 |
| B8 | 速度分量渲染 = 回合末快照（a/salience/isDefending 为渲染时点） | isDefending 已在窗口开始清除（Q3）——分量与 Phase 3 时点可能不同，标注「回合末」 |

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-14 | 初稿 | 任务issue 01 | 全量审计 |
| v1.1 | 2026-08-14 | 全量审计（3 专家 + 对抗验证，44 发现 → 31 CONFIRMED）修复：C1/console-03（AC-9「60」→ 50——MaxRounds 正典）；C2（组合 provider——NPC 行动接线 NpcActionProvider）；C3/console-07（补 [a(t)] 段——sensory/Precentral/Broca）；C4/console-08（补 [因子] 段——base×force×motivation×gate）；C5（静息区间 [0.535, 0.772]——M1 实测 0.771229）；C7/console-09（结算示例与 F4 格式统一）；C7/console-11（RenderSetup 循环前输出）；C8/console-09（ctx 构造定义——DeterministicRng 接线）；C9/console-13/C13（--trace-resting 非法值 <1）；C10（名字硬编码声明）；C11/console-08（RenderRound +cal 参数）；C14（SpeedScoreCalculator 实例化说明）；console-04（AC-11 脚本化输入前提）；console-06（速度重算表述统一）；console-10（EOF/null 输入处理）；console-15（重复参数后者覆盖）；AC-13 新增渲染格式验收；偏差 B6-B8 新增 | 全量审计（3❌ + 10⚠️ + 3ℹ️ 去重） | Δ审计 |
| v1.2 | 2026-08-14 | Δ审计（3 专家 + 对抗验证，43 发现 → 21 CONFIRMED）修复：C-01（RenderRound +TurnManager tm——段 3/6 消费 LastRoundOrder/LastRoundActions，3 重断裂）；D2/Δ-C04/C-02（[因子] 段按事件类型区分——精神无 force 因子 base 回退 cal，3 专家同命中）；D3/Δ-C02/C-06（§5.2/§5.3 段号引用同步——结算段 7、结束段 9）；Δ-C01/C-03（CompositeActionProvider 类型定义——p 自由变量伪码不可执行；NpcActionProvider 无参构造声明）；D6/Δ-C06/C-04（WaitProvider 类定义 + 静息 trace 分支补 ctx）；D7/Δ-C03/C-05（[结束] 唯一输出源裁决——RenderRound 段 9，主循环退出后不重复，3 专家同命中）；D8/Δ-C07（A1 示例补「命中」后缀）；Δ-C05（salience 来源 = state.Salience[p]——flow 已交付）；Δ-C10（A2 m=0.0000 F4 格式）；C-07（AC-13 补 [顺序] 行锚点） | Δ审计（2❌ + 7⚠️ 去重） | 终审确认 |
| v1.3 | 2026-09-02 | Grilling #106：AC-12 增「JsonException（数据校验失败，如缺 role）→ 退出 1 + stderr 数据校验失败」 | Grilling #106 引擎 fail-fast（实施 #107） | 免重审（实现细节同步，随 #107 测试验证） |

---
*创建: 2026-08-14 | 更新: 2026-09-02 | 版本: v1.3*
*关联: [任务issue 01](../../archive/grilling/csharp-console/design/issues/01-console-spec.md), [plan §九](csharp-engine-roadmap.md), [csharp-flow spec](csharp-flow.md)*
