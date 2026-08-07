# Review Trace: immutable-shimmying-star.md（第二次审查）

> 审查日期: 2026-08-06 10:30 | 审查范围: `/home/dog/.claude/plans/immutable-shimmying-star.md` (v2, 修复后)
> 方法: 符号执行 + 限界验证 | 前置检查: 无
> 对比基线: `.scratch/review-trace-2026-08-06-1000-immutable-shimmying-star.md`

## 变更追踪 — 上次缺口闭合验证

| 上次缺口 | 上次判定 | 本次状态 | 验证 |
|---------|---------|---------|------|
| #1 事件总线定位 | ⚠️ | ✅ | D4 明确放在 Infrastructure，线程模型（主线程同步）、不可拦截规则已定义 |
| #2 写入路径 | ⚠️ | ✅ | D1 L74-76: TurnResult → Entity.ApplyEvents()，引擎只产出事件 |
| #3 纯函数边界 | ⚠️ | ✅ | D2 L82-83: RNG 注入（CombatContext.Rng），查表=读数据不算副作用 |
| #4 引擎/流层分界 | ⚠️ | ✅ | D3 L91: 排序算法在 L2，"按排序结果循环调度"在 L4 |
| #5 事件总线线程模型 | ⚠️ | ✅ | D4 L98: 主线程同步分发 |
| #6 通用/专用边界 | ⚠️ | ✅ | D5 L105: 技能效果=数据参数(L1)+效果解释器(L2)。新技能=新数据 |
| #7 数据类字段规格 | ⚠️ | ⚠️→保持 | §3.5 覆盖了跨层共享类型。BrainRegion/LinkDefinition 等 L1 专属类字段仍需逐类定义——但属内容填充阶段工作，非架构阻塞 |
| #8 Engine 模块接口 | ⚠️ | ✅ | R2 列出 6 个关键模块。剩余模块（HitCalculator/SpeedSorter 等）是 CombatResolver 内部实现细节，不需要独立公共接口 |
| #9 CombatAction 类型 | ❌ | ✅ | §3.5 L311-331: 完整字段定义，M1/Broca 双通道 + 技能槽 + 时间戳 |
| #10 TurnResult 子类型 | ❌ | ✅ | §3.5 L359-412: DamageEvent/HealEvent/StatusChangeEvent/LinkGrowthEvent 全部展开 + EndCondition |
| #11 LinkMValues 等类型 | ❌ | ✅ | §3.5 L239-265: LinkMValues/FocusSet/ActivationMap/SituationType 完整定义 |
| #12 CollapseResult 消费 | ⚠️ | ✅ | §4.3 L553-556: 三路输出的精确消费方+公式 |
| #13 R1 度量标准 | ⚠️ | ✅ | R1 L569-573: 4 条可操作信号替代主观的"5句话" |
| #14 R2 关键模块 | ⚠️ | ✅ | R2 L576-583: 6 模块明确列表 + 判定标准（≥2子系统 或 ≥3消费者 或 非确定性） |
| #15 R3 信息泄露粒度 | ⚠️ | ✅ | R3 L589-593: 三类泄露信号+检查方法（grep 核心数据格式→应只有1个类直接读写） |
| #16 R5 错误处理 | ⚠️ | ✅ | R5 L601-606: Null Object/TryXxx 统一模式声明 |
| #17 命名规范覆盖 | ⚠️ | ✅ | 命名表 10 行：接口/抽象基类/常量/Unity SerializeField 全部补全 |
| #18 审查清单可操作性 | ⚠️ | ✅ | 10 项每项有可量化判定标准（如 "≥3行代码块在另一处出现"） |
| #19 Python↔C# 同步 | ❌ | ✅ | §六 L696-700: JSON 唯一数据源 + RefreshDataAssets.cs 一键刷新 + 变更流程 |
| #20 战斗公式迁移源 | ❌ | ✅ | §六 L702: 新建 sim_combat_formulas.py + §七 L714 明确阶段1产出 |
| #21 公式验证手段 | ⚠️ | ✅ | §八 L743-746: 三阶段验证（手动标注→Monte Carlo对比→AST比对） |

### 闭合统计
- 上次 ❌ 5 → 本次 ❌ 0（全部闭合 ✅）
- 上次 ⚠️ 17 → 本次 ⚠️ 1（#7 降级为非阻塞）+ 新发现 2 → 实际 ⚠️ 3
- 上次 ✅ 0 → 本次 ✅ 19

---

## 新 Trace Table（仅追踪修复后引入的新增/变化内容）

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| N1 | §3.5 ParticipantState.GridPosition | Unity 引擎 | 引用<Vector2Int>（Unity 内置类型） | 存储战场坐标 | — | CombatContext.BattleGrid 使用 | GridState 类型在 §3.5 L354 被引用但未定义——GridState 的字段？→ ⚠️ 新缺口 | ⚠️ |
| N2 | §4.1 TurnResult 结构体 | — | — | §4.1 L477-483 定义了 TurnResult 的简化版（缺少 CombatEnded/EndCondition） | TurnResult（简化版，与 §3.5 L399-412 不一致） | §4.1 文本描述（"这是系统中最重要的深模块"） | 同一类型在两处定义，§4.1 版本是旧版残留——缺少 CombatEnded/EndCondition 字段 → ⚠️ 重复定义，§4.1 应删除或改为引用 §3.5 | ⚠️ |
| N3 | §3.5 CombatAction 通道约束 | BasicActionType 枚举 | 枚举<PhysicalAttack\|MentalAttack\|Defend\|UseItem\|Flee\|Surrender\|Wait>（7值） | M1Action 和 BrocaAction 都声明为 BasicActionType——但 MentalAttack/Surrender 只能走 Broca，PhysicalAttack/Defend/Flee/UseItem 只能走 M1。Wait 不走任何通道 | 枚举<BasicActionType>——不区分通道 | CombatResolver.ResolveTurn()（需根据通道验证合法性） | 类型系统不强制通道约束——允许将 PhysicalAttack 赋给 BrocaAction → ⚠️ 需运行时验证或用两个独立 enum（M1ActionType / BrocaActionType） | ⚠️ |
| N4 | §4.2 ActivationMap.Levels | ComputeActivation 输出 | Dict<string, float> | — | — | — | §3.5 L248 将 Levels 定义为 `Dictionary<LinkId, float>` 而 §4.2 L513 定义为 `Dictionary<string, float>` → ⚠️ 类型不一致（LinkId vs string） | ⚠️ |
| N5 | §4.3 DiseaseSemantic.DirectionWeights | 疾病目录文件 | 数值[6] | 映射：6 维权重对应 6 个 PersonalityTag | float[6] | MoonlightField.ComputeCollapse() | 数组索引到 PersonalityTag 的映射是隐式的（按 enum 声明顺序）→ ⚠️ 映射关系未显式声明 | ⚠️ |

---

## 缺口汇总（本次新发现）

| # | 位置 | 严重度 | 描述 |
|----|------|--------|------|
| N1 | §3.5 L354 | ⚠️ | **GridState 类型被引用但未定义**。CombatContext.BattleGrid 需要战场网格类型——网格尺寸/格子阻挡/控制区等字段未定义 |
| N2 | §4.1 L477 | ⚠️ | **TurnResult 重复定义**。§4.1 的简化版与 §3.5 完整版不一致（缺 CombatEnded/EndCondition）。应删除 §4.1 的重复定义，改为引用 §3.5 |
| N3 | §3.5 L315 | ⚠️ | **BasicActionType 不区分通道**。M1Action 和 BrocaAction 用同一枚举但合法值域不同——类型系统不强制约束 |
| N4 | §4.2 L513 | ⚠️ | **ActivationMap.Levels 键类型不一致**。§3.5 用 `Dictionary<LinkId, float>`，§4.2 用 `Dictionary<string, float>` |
| N5 | §4.3 L549 | ⚠️ | **DirectionWeights[6] 到 PersonalityTag 的映射隐式**。依赖 enum 声明顺序，未显式标注索引→标签对应关系 |

---

## 统计（本次）

- 总 trace 行数: 5（仅新增/变化）
- ✅ 0 / ⚠️ 5 / ❌ 0
- 上次缺口闭合率: 21/22（95%），#7 降级为非阻塞内容填充

## 总体评估

**上次 22 个缺口中 21 个已闭合（含全部 5 个 ❌）。** 计划从"架构草图"升级到了"可实施的规格"——核心类型有完整字段定义，层级间通信协议明确，错误处理/命名/注释规范可操作。

本次新发现的 5 个 ⚠️ 都是**小范围修复**（删除重复定义、统一类型名、补充 GridState、拆分通道枚举、显式标注映射）。不是架构级问题——5 分钟可全部修复。

建议：修完这 5 个 ⚠️ 后，计划可以正式进入阶段 1 实施。

---

*创建: 2026-08-06 10:30 | 对比基线: review-trace-2026-08-06-1000-immutable-shimmying-star.md*
*关联: [/home/dog/.claude/plans/immutable-shimmying-star.md](/home/dog/.claude/plans/immutable-shimmying-star.md)*
