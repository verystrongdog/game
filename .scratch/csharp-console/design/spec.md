# csharp-console — 实现规格

> 控制台 harness（plan §九）——加载真实脑数据 → 2 参与者 1v1（玩家 vs NPC 杂兵）→ 五阶段战斗 → 每回合完整输出 + 静息 trace 模式 + 种子 RNG。玩家行动经键盘 IActionProvider 注入（step 10 接口的玩家实现）。版本: v1.0

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | `YouAreNotTheFish.Console` 可执行项目（引用 Core）；`CliArgs`（--seed/--trace-resting 解析）；`PlayerActionProvider`（键盘 IActionProvider）；`RoundRenderer`（§九 每回合输出渲染）；`Program`（主循环：Create → StepRound 循环 → 结束）；静息 trace 模式（--trace-resting N → 30 回合零事件 → 不动点测量输出） |
| 不覆盖 | NPC AI 全量（step 10 NpcSalience demo 版已交付）；Unity 呈现；存档/读档；战斗外内容（探索/对话等） |
| 前置依赖 | csharp-data-layer ✅ / csharp-engine-types ✅ / csharp-wmatrix ✅ / csharp-wc-dynamics ✅ / csharp-tone ✅ / csharp-cstc ✅ / csharp-speed ✅ / csharp-damage ✅ / csharp-events ✅ / csharp-flow ✅（261/261） |
| 阻塞 | step 12 csharp-smoke（Smoke 集成测试——用 console 或直接引擎） |

## 二、项目结构与 CLI

### 2.1 项目

`src/YouAreNotTheFish.Console/YouAreNotTheFish.Console.csproj`——`<OutputType>Exe</OutputType>`、`net8.0`、ProjectReference → `YouAreNotTheFish.Core`。命名空间 `YouAreNotTheFish.ConsoleApp`。

### 2.2 CliArgs（参数解析，纯函数）

```csharp
public sealed record CliArgs(ulong Seed, int? TraceRestingRounds)
{
    public static CliArgs Parse(string[] args);
}
```

- `--seed <n>`：RNG 种子（默认 42）。非法值（非数字/负数/缺失）→ CliUsageException（含用法说明）。
- `--trace-resting <n>`：静息 trace 模式（n 回合零事件；默认 30）。
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
- 输入提示（中文）：`[玩家] 行动 (1=物理攻击 2=精神攻击 3=防御 0=等待): `——解析 1/2/3/0；非法输入 → 重新提示（循环，最多 3 次后默认 0=等待）。
- 行动 → CombatAction 映射：1 → M1=PhysicalAttack（TargetId=对方）；2 → Broca=MentalAttack（对方）；3 → M1=Defend；0 → 空声明。
- 目标解析：`state.Teams[p] != state.Teams[selfIndex]` 的第一个参与者（复用 NpcSalience 同款规则——1v1 即对方）。
- 确定性：外部输入（键盘），无此约束。
- 可测性：TextReader/TextWriter 注入——测试可喂输入流断言输出。

### 3.2 RoundRenderer（回合输出渲染，纯函数）

```csharp
public static class RoundRenderer
{
    public static string RenderRound(int round, CombatState state, TurnResult result, GameData data);
    public static string RenderSetup(CombatState state, GameData data);
    public static string RenderResting(WcState resting, GameData data);
}
```

- 职责：§九 每回合输出清单（人类可读 + 结构化可断言）。纯函数（无 I/O）——测试直接断言字符串。
- RenderRound 输出段（§九 清单逐项）：
  1. `===== 回合 N =====`
  2. `[速度] p{i} {名字}: 察觉 {x:F3} / 决断 {y:F3} / 执行 {z:F3} → 总分 {s:F3}`（speed 分量展开——调用 SpeedScoreCalculator 重算，与回合内一致）
  3. `[顺序] p3 → p1 → p2`（TurnResult 内行动序——从 Events 无法还原序；TurnManager 需暴露？→ **序输出从 state.Salience 反推不可行**——见 §四 决策 D1）
  4. `[状态] p{i}: HP {hp}/{max} SAN {san}/{max} tone(NE {t} VTA {t} SNc {t} 5HT {t}) gates(S {g} C {g} L {g})` + `[CD] Defend={cd}`（IsDefending 时标注 `[防御中]`）
  5. `[行动] p{i} {名字}: {动作描述}`（来自 TurnResult——事件不足以还原声明；**行动声明需 TurnManager 暴露**——见 D1）
  6. `[结算] {事件清单}`：每事件一行——`A1 m=0.625 (dealt 2.5 / expected 4)`、`B1 m=0.16666667 (|ΔHP| 2.5 / 15)`、`C1 恐慌跨越 (SAN 18.5→17.9)`、`D1/D2 倒下广播`（§九「damage 公式逐因子展开 + 事件清单 A1 m=…/B1 m=…」）
  7. `[结束] {原因}`：`TeamDefeated（一方全灭）` / `MaxRounds（回合上限 {n} 达成）`（IsOver 为 true 时）
- RenderSetup：`== 战斗开始 ==` + 参与者列表（名字/HP/SAN/队伍）。
- RenderResting：`== 静息不动点 ==` + 48 active 节点 min/max + 排除节点三组值（对齐 csharp-tone AC-15 输出形态）。

### 3.3 Program（主循环）

```csharp
public static class Program
{
    public static int Main(string[] args);
}
```

- 流程：`CliArgs.Parse` → 战斗模式：`GameDataLoader.LoadAll(dataDir)` → `CombatState.Create([玩家, 杂兵], [1,2], data, cal)` → `TurnManager(data, cal, PlayerActionProvider)` → `while !tm.IsOver(state): result = tm.StepRound(state, ctx); 输出 RenderRound` → 结束输出 RenderSetup 补头 + 结尾。
- 静息 trace 模式：`--trace-resting` → 单参与者（玩家模板）零事件 30 回合 → RenderResting 输出（用 TurnManager + Wait provider 跑 30 回合，输出终态 a——对齐 M1 里程碑方法）。
- dataDir 定位：`AppContext.BaseDirectory` 向上回溯找 `data/`（镜像测试项目 DataDirCandidates——console 与测试共用数据源约定）。
- 退出码：0（正常结束）；1（CliUsageException 参数错误——用法输出到 stderr）。

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

- 调用 `SpeedScoreCalculator.ComputeComponents(a, salience, gurney, isDefending)` + `ComputeScore`（与 TurnManager Phase 3 同参）——渲染时 state 已是回合末，a/salience 是下一回合 Phase 1 前状态；**分量值 = 回合末快照重算**（数值与 Phase 3 时点不同——demo 语义：展示当前状态的速度分量，标注「回合末重算」）。
- 输出格式：`察觉 {x:F3} / 决断 {y:F3} / 执行 {z:F3} → 总分 {s:F3}`。

### 5.2 结算详情（RenderRound 段 6）

- 每事件一行，格式（§九「damage 公式逐因子展开 + 事件清单」）：
  - `A1 m={m:F4} (dealt {dealt}/{expected} 命中)` / `A2 m=0 (miss)`
  - `B1 m={m:F4} (|ΔHP| {delta}/{max})`、`B2 m={m:F4} (回避)`、`A5 m={m:F4} (防御成功)`
  - `A4 m={m:F4} (SAN {san}/{expected})`、`B4 m={m:F4} (|ΔSAN| {delta}/{max})`
  - `C1 恐慌跨越 (SAN {before}→{after})`、`D1/D2 倒下广播 (p{actor})`
  - `Heal/LinkGrowth no-op`（demo 无——格式预留）
- m 值：**渲染时重算**（事件字段套 m 公式——与 events spec §5.3 同式；确定性组件可复算）。

### 5.3 结束原因（RenderRound 段 7）

- `tm.IsOver(state)` 为 true 时输出。原因判定（console 自判，§5.5 双口径 + 回合上限）：`一方全灭（Hp≤0 ∨ San≤0）` / `回合上限 {MaxRounds} 达成`。输出后主循环退出。

## 六、验收标准

| AC | 验收标准 | 锚点/断言 |
|----|---------|-----------|
| AC-1 | CliArgs 解析 | `--seed 7` → (7, null)；`--seed 7 --trace-resting 30` → (7, 30)；`--trace-resting` 缺值 / `--seed abc` / 未知参数 → CliUsageException；无参数 → (42, null) |
| AC-2 | PlayerActionProvider 输入映射 | 喂 "1\n" → M1=PhysicalAttack（TargetId=对方）；"2\n" → Broca=MentalAttack；"3\n" → M1=Defend；"0\n" → 空声明；"x\n2\n"（非法后重试）→ 第二次生效；连续非法 3 次 → 默认等待 |
| AC-3 | RenderSetup | 含玩家/杂兵名字与 HP/SAN/队伍行 |
| AC-4 | RenderRound 速度段 | 含 `[速度]` + 三分量 F3 格式 + 总分；两参与者各一行 |
| AC-5 | RenderRound 行动段（D1） | 含 `[行动]` + 动作描述（物理/精神/防御/等待）；等待参与者显示「等待」 |
| AC-6 | RenderRound 结算段 | 事件清单逐行（A1 m=… 格式）；miss → A2 行；防御 → A5 行；C1 → 恐慌跨越行 |
| AC-7 | RenderRound 状态段 | 含 HP/SAN/tone 四分量/gates/CD 标注 |
| AC-8 | 结束输出 | IsOver 后含 `[结束]` + 原因（全灭/上限） |
| AC-9 | 完整战斗冒烟 | `--seed 42` 无参数跑完整战斗（最大 60 回合）→ 正常退出 0；每回合 RenderRound 非空 |
| AC-10 | 静息 trace 模式 | `--trace-resting 30` → 输出 `== 静息不动点 ==` + active 节点 min/max ∈ [0.535, 0.771]（M1 实测） |
| AC-11 | 确定性 | `--seed 42` 两次运行输出逐字符相同（重定向 stdout 比较） |
| AC-12 | 异常 | 数据目录缺失 → 非零退出 + 错误信息 |

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
| B2 | 速度分量 = 回合末快照重算（非 Phase 3 时点值） | 渲染在回合末进行，重算展示当前状态分量；标注「回合末重算」 |
| B3 | 玩家输入 3 次非法 → 默认等待 | 防键盘死循环（demo 健壮性） |
| B4 | 结算 m 渲染时重算（非事件携带） | events spec 事件不携带 m（派生量）；重算公式与 events §5.3 同式 |
| B5 | dataDir 回溯定位 | console 与测试项目共用约定；非打包部署场景（demo 阶段） |

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-14 | 初稿 | 任务issue 01 | 全量审计 |

---
*创建: 2026-08-14 | 更新: 2026-08-14 | 版本: v1.0*
*关联: [任务issue 01](issues/01-console-spec.md), [plan §九](../../../csharp-engine/design/plan.md), [csharp-flow spec](../../../csharp-flow/design/spec.md)*
