# 任务issue 01: 引擎共享状态类型（plan §三）

> Status: claimed | Type: task | 维度: 管线 | Blocked by: csharp-engine sign-off ✅ (2026-08-13) | GitHub: [#45](https://github.com/verystrongdog/game/issues/45)

## 问题（这件事要解决什么）

Types/ 目前只有一个 0 字节占位文件（SpeedComponents.cs）。plan §三 定义的共享状态类型是 step 3-9 全部引擎模块的输入输出契约——WcDynamics 吃 WcState、CstcGating 吃 GurneyState、DamageCalculator 产 DamageEvent。**类型不落地，后续 8 个 feature 全部无法编译。** 审计修复 #2（HP/SAN 缺失→ParticipantState）和 #3（双通道缺失→CombatAction）的产物就落在这个 feature。另外 CombatContext 引用的三个依赖项（IRng、GameData 聚合、CalibrationConfig）不在 §三 表内，不定义则 CombatContext 无法声明。

## 目标

按 plan §三 定义并实现全部共享状态类型 + CombatContext 三个依赖项，产出 spec.md 走二层流水线。

## 指标

- plan §三 11 种类型 100% 定义（SpeedWeights 除外——归 step 7，plan §4.5 显式）
- 4 个引擎输出事件类型（框架 memory §3.5）全部定义，字段覆盖 §5.5 m 公式与 §九 console 输出的消费需求
- 每个字段有来源注释（plan 章节 + 设计文档章节）——审计逐字段核查
- CalibrationConfig 值与 plan §七 表逐条一致（测试逐常量断言）
- IRng 确定性（同种子同序列）
- `dotnet build` 0 错误 + 测试全绿 + 审计通过 + sign-off 获批

## 工作方式

- **引用即读取地基**：plan 全文（§三/§四/§七/§九）+ 运行时状态模型（§三 状态清单 / §4.5 α 表 / §5.5 δ+mag 表 / §6.1-6.5 / §7 集成）+ 回合战斗流程（§2 双通道 / §7 防御 / §9.1 CD）+ 框架 memory code-framework-plan（核心类型 §3.5）+ 现有 Data 层代码（BrainEnums.cs / GameDataLoader.cs / WsensoryMatrix.cs / TripartiteModel.cs / BrainRegionsData.cs）
- 逐类型定义字段表（文档符号 / 类型 / 来源列），字段命名与文档符号对照
- **事件类型设计**：框架 memory 只给 4 个名字无字段——按 plan §4.7 消费方（§5.5 m 公式）与 §九 console 输出需求反推最小字段集，每字段标注来源

## 判断与取舍

- **SpeedWeights 归 step 7**：plan §三 表列了它但 §4.5 显式"SpeedComponents/SpeedWeights 两个 record 均在 Step 7 从零实现"——以更具体的 §4.5 为准（D1）
- **GameData 聚合放 Data/ 命名空间**：L1 聚合 record，csharp-data-layer 未交付（其 spec 只覆盖 loader + record），plan §三 CombatContext 引用它——本 feature 补（D2）
- **CalibrationConfig 用 instance record + static Default**，而非 plan §七 字面"static class"——sign-off 结转 #4 蒙特卡洛校准需要参数 sweep，实例化才能注入变体；对 plan 的偏差显式声明（D3）
- **事件记录装"客观结果"而非"每角色视角"**：§5.5 的 A/B 视角推导归 EventProcessor（step 9）；一次物理攻击产一条 PhysicalDamageEvent，攻击者 A1/承受者 B1 由处理器派生（D4）
- 数组字段（a_j[69] 等）不可变约定：构造时拷贝；91 浮点由 4 个嵌套 record 分解（§三 表）

## 范围

产出 spec.md 覆盖（命名空间 `YouAreNotTheFish.Core.Types`，另有 Data/ 补充项）：

- 状态 record ×8：WcState / ToneState / GurneyState / GateState / ParticipantState / WMatrix / LoopSalience / TurnResult
- 声明与上下文 ×2：CombatAction（+ActionSlot）/ CombatContext
- 事件记录 ×5：CombatEvent 基类 + PhysicalDamageEvent / MentalDamageEvent / HealEvent / StatusChangeEvent / LinkGrowthEvent
- 接口与实现：IRng + DeterministicRng
- 枚举 ×4：ActionKind / ChannelOrder / GurneyPopulation / StatusKind
- Data/ 补充：GameData 聚合 record + GameDataLoader.LoadAll(dataDir)
- 常量：CalibrationConfig（plan §七 全表）

不覆盖：SpeedWeights/SpeedComponents（step 7）、s_pending（CombatState，step 10）、CombatState/TurnManager（step 10）、14 事件 kind 枚举与 δ 派生逻辑（step 9，映射表仅作为约束文档列出）

## 追问

### Q1: GameData 聚合放哪个命名空间
Data/（L1 聚合，csharp-data-layer 已交付 5 个加载方法但未含聚合 record）。

### Q2: CalibrationConfig 静态类还是实例
实例 record + `static Default`——plan §七 字面写 static class，但结转 #4 蒙特卡洛校准需要参数 sweep，实例化可注入。偏差显式声明。

### Q3: 事件类型装什么视角
客观结果（一次攻击一条事件），A/B 每角色视角由 EventProcessor（step 9）按 §5.5 派生——绑定语义"e = (δ, s) 绑定到具体角色实例"在处理器内完成。

### Q4: SpeedWeights 是否本 feature 实现
否——plan §4.5 显式归 step 7。

## 决策

| D# | 决策 | 理由 |
|----|------|------|
| D1 | SpeedWeights/SpeedComponents 排除出本 feature | plan §4.5 显式归 step 7（§三 表与 §4.5 冲突取更具体者） |
| D2 | GameData 聚合 + LoadAll 放 Data/ 命名空间 | L1 聚合；plan §三 CombatContext 引用、数据层未交付 |
| D3 | CalibrationConfig 为 instance record + static Default | 结转 #4 蒙特卡洛 sweep 需要参数注入；对 plan §七 字面的偏差 |
| D4 | 事件记录装客观结果，A/B 视角归 step 9 EventProcessor | §5.5 绑定语义；避免事件在 L2 内重复膨胀 |

## 产出

- [x] spec.md v1.0
- [x] spec.md 通过 workflow 审计（v1.0 全量审计：2 reject + 1 conditional → **退回**；v1.1 吸收 1❌+7⚠️+10ℹ️ → Δ审计进行中）
- [ ] sign-off.md 获批

## Comments
