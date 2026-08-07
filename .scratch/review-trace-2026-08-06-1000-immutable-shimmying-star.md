# Review Trace: immutable-shimmying-star.md

> 审查日期: 2026-08-06 10:00 | 审查范围: `/home/dog/.claude/plans/immutable-shimmying-star.md`
> 方法: 符号执行 + 限界验证 | 前置检查: 无

## 前置输入
- [x] 被引用文件自动拉入: 无（计划中引用的 CLAUDE.md、核心机制.md 等已在会话上下文中，且为项目级引用非数据依赖）

---

## Trace Table

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| 1 | §三 分层架构 — 5层定义 | 项目需求 | 文本（设计意图） | 定义抽象层级：数据→引擎→实体→游戏流→呈现 | 枚举<Layer> = {Data, Engine, Entity, GameFlow, Presentation} | D1-D5 决策（使用层概念）、§3.2-3.3 模块划分（按层分配模块）、§四 深模块设计（按层定位接口） | 层边界模糊时（如"事件总线"属于 Engine 还是 Infrastructure？文中放在跨层基础设施）→ ⚠️ 事件总线定位不明确 | ⚠️ |
| 2 | §3.2 D1 — 数据层与逻辑层严格分离 | Layer 1 数据对象 | 枚举<ScriptableObject\|JSON> | 规则声明：Layer1 不可变纯数据，Layer2 只读不写 | 约束：Layer1→Layer2 单向只读依赖 | §3.3 Layer1 模块划分（Data/ 下各 Config 类）、§六 Python 过渡期规范（"模拟和 Unity 代码共享同一数据层"） | 运行时状态（如 NPC 战斗中 m 值变化）存在 Layer3 实体中——但 Layer2 引擎计算 Δm 后如何写回 Layer3？D1 说引擎"只读取"数据层，但引擎输出（TurnResult）需被 Layer3 消费并修改实体状态 → ⚠️ 写入路径未定义 | ⚠️ |
| 3 | §3.2 D2 — 模拟引擎是纯函数核心 | CombatContext（参战者状态/战场网格/η等） | 未定义类型签名 | 纯函数：输入状态+参数 → 输出新状态。不持有 Unity 引用 | 新状态（TurnResult 等） | Layer 4 游戏流（调用引擎）、Layer 3 实体（状态更新）、单元测试（独立验证） | "纯函数"意味着无副作用——但引擎需要产生随机数（命中判定、ε 噪声）、需要查预烘焙表（I/O）→ ⚠️ 纯函数边界未定义：随机数/RNG 种子如何注入？查表算不算副作用？ | ⚠️ |
| 4 | §3.2 D3 — 游戏流层不实现具体逻辑 | Layer2 引擎输出（TurnResult） | 引用<CombatResolver.TurnResult> | 编排：调用引擎 → 通知实体更新 → 触发呈现 | 编排序列 | Layer3 实体（状态变更）、Layer5 呈现（事件触发） | "不实现具体逻辑"的边界是什么？速度排序在引擎中，但回合阶段切换（情境更新→继承→排序→执行→收束）的编排代码在 TurnManager 还是 CombatResolver？→ ⚠️ 引擎/流层的职责分界线模糊 | ⚠️ |
| 5 | §3.2 D4 — 事件总线解耦跨层通信 | 实体状态变更 | 未定义事件类型枚举 | 发布事件 → 订阅者响应 | 事件实例（如 HPChangedEvent） | Layer5 UI（更新血条）、Layer4 游戏流（检测死亡条件）、调试日志 | 事件总线的线程模型？Unity 主线程要求？事件是否可被中途拦截/修改？→ ⚠️ 事件总线行为规范未定义 | ⚠️ |
| 6 | §3.2 D5 — 通用机制与专用内容分离 | 通用框架（回合管理/战斗结算/物品系统）、专用内容（技能效果/物品数据/敌人数据） | 枚举<通用\|专用>（二元分类） | 分离：通用在引擎层，专用在数据层 | 两层间通过数据驱动连接 | §3.3 Layer 1（数据层 Config 类）、§3.3 Layer 2（引擎层 Resolver/Calculator 类） | "通用"和"专用"的边界在哪？技能效果（如"火焰伤害+20%"）是数据（Layer1）还是需要代码（Layer2 的 EffectResolver）？→ ⚠️ 通用/专用分界线需要更精确的定义 | ⚠️ |
| 7 | §3.3 Layer 1 模块列表 — 数据层类定义 | 设计文档中的数据结构规格 | 各 Config/ScriptableObject 类 | 定义数据容器：BrainRegion, LinkDefinition, WeaponConfig 等 | 约 15+ 个数据类 | Layer2 引擎（读取数据） | 这些类的字段定义未给出——只有类名列表。如 LinkDefinition 包含哪些字段？是否与 data/connectivity/link_registry.json 对齐？→ ⚠️ 数据类字段规格缺失 | ⚠️ |
| 8 | §3.3 Layer 2 模块列表 — CombatResolver | 设计文档 `规则/核心机制.md` §四 | 引用<战斗结算公式> | 实现战斗结算：5阶段/双通道/响应窗口/伤害公式 | 未在 §3.3 中详细说明——见 §4.1 | §4.1 深模块设计 | §3.3 和 §4.1 之间职责描述分离——§3.3 列模块名，§4.1 展开接口。但 §3.3 中 CombatResolver 描述为"战斗结算主入口"，§4.1 中展开为 ResolveTurn()。其他 Engine 模块（DamageCalculator 等）未在 §4 展开 → ⚠️ 仅 3/10+ Engine 模块有接口设计 | ⚠️ |
| 9 | §4.1 CombatResolver 接口设计 | actions: List<CombatAction>, context: CombatContext | List<引用<CombatAction>>、引用<CombatContext>（类型未定义） | ResolveTurn() → 5阶段回合结算 | TurnResult: {damageEvents, healEvents, statusChanges, linkGrowthEvents, newSpeedOrder} | Layer4 TurnManager（调用方）、Layer3 Entity（状态应用）、测试 | CombatAction 的字段？CombatContext 包含什么？如 context 包含"战场网格"——网格是 Layer2 还是 Layer3 的职责？→ ❌ 核心输入类型 CombatAction 和 CombatContext 未定义 | ❌ |
| 10 | §4.1 TurnResult 结构 | ResolveTurn 输出 | 结构体含 5 个 List 字段 | 回合结算结果的聚合容器 | List<DamageEvent>, List<HealEvent>, List<StatusChangeEvent>, List<LinkGrowthEvent>, float[] newSpeedOrder | Layer4 TurnManager、Layer3 Entity 状态更新、Layer5 战斗日志 | DamageEvent/HealEvent/StatusChangeEvent/LinkGrowthEvent 的内部字段？→ ❌ 事件类型未定义。newSpeedOrder 是 float[]——数组索引如何映射到参战者？→ ⚠️ 映射关系未定义 | ❌ |
| 11 | §4.2 LinkActivator 接口设计 | currentM: LinkMValues, situation: SituationType, focus: FocusSet, san: float | 引用<LinkMValues>（类型未定义）、枚举<SituationType>（值域=27情境）、引用<FocusSet>（类型未定义）、数值（0-100） | ComputeActivation() → 链路激活水平计算 | ActivationMap: Dictionary<string, float>（link_id → 0.0~2.0） | 战斗引擎（决定哪些链路效果生效）、预烘焙管线（NPC 行为采样）、UI（展示激活状态） | LinkMValues 是 Dictionary<string,float> 还是专用类型？FocusSet 的结构？→ ❌ 输入类型未定义。激活水平范围 0.0~2.0 中 2.0=聚焦——1.0 代表什么？→ ⚠️ 语义锚点未定义 | ❌ |
| 12 | §4.3 MoonlightField 接口设计 | type: EntityType, san: float, kappa: float | 枚举<EntityType>（值域=12种实体类型，引自 sim_moonlight_v2_sanity.py ENTITY_D0）、数值（0-100）、数值（默认1.0） | ComputeEta() → η = g0 × c(SAN) × κ | 数值（0.0 ~ ~4.0，零号病人可达 4.3） | 战斗引擎（难度缩放）、空间系统（η 空间分布）、NPC AI（行为调制） | ✅ 输入类型有定义来源（现有 sim + 设计文档）。kappa 默认 1.0 的理由？→ ⚠️ 默认值依据未说明 | ⚠️ |
| 13 | §4.3 CollapseResult 结构 | ComputeCollapse 输出 | 结构体含 situationBias, npcRelationModifier, narrativeLabel | ρ_off 坍缩三路输出 | 数值（0.0~1.0，偏置量）、数值（倍率修正）、文本（语义标签） | 情境系统（偏置应用）、NPC AI（关系修正）、叙事系统（标签触发） | situationBias 应用方式？"×0.3"在何处乘——调用方还是 MoonlightField 内部？→ ⚠️ 消费方不清楚自己该乘什么。npcRelationModifier 的 "baseline × (1 + conc × η × 0.5)" 公式——baseline 是什么？→ ⚠️ baseline 来源未定义 | ⚠️ |
| 14 | §五 R1 — 接口优先 | AI 生成代码前 | 文本（设计意图） | 先写接口注释：做什么、输入/输出、使用示例 | 接口注释文本 | 后续实现代码（指导编码）、代码审查（验证一致性） | ">5 句话才能说清的接口 = 设计有问题"——五句话的度量标准是什么？英文还是中文？句子复杂度差异大 → ⚠️ 度量主观，缺乏可操作标准 | ⚠️ |
| 15 | §五 R2 — 设计两次 | 关键模块（战斗/链路/AI/月光场） | 枚举<关键模块> = {CombatResolver, LinkActivator, BehaviorQuery, MoonlightField} | 提出 ≥2 种设计方案，比较接口复杂度/信息隐藏/耦合度 | 方案比较文档（A/B 方案注释） | 设计审查（选择最优方案）、决策树（记录设计理由） | "关键模块"清单是否闭合？枚举为 4 个——但物品系统、回合管理、存档系统是否也算关键？→ ⚠️ 关键模块判定标准未定义 | ⚠️ |
| 16 | §五 R3 — 信息泄露检查 | AI 生成的类 | 文本（源代码） | 自检：设计决策是否散落？透传变量？共享数据格式知识？ | 检查结论（通过/重构建议） | 代码审查（验证） | "两个类共享数据格式知识"——这里的"数据格式"指什么？JSON schema？类字段定义？→ ⚠️ 检查粒度未定义 | ⚠️ |
| 17 | §五 R5 — 异常消减 | AI 生成的 API | 文本（方法签名+语义） | 异常消减优先序：(1)重新定义语义消除异常 (2)底层屏蔽 (3)聚合 (4)崩溃 | 修改后的 API 语义 | API 调用方（更简单的使用） | "GetLink(id) 不存在返回 Link.None"——这与 Unity 惯例（通常返回 null 或抛异常）的关系？Link.None 是 null object pattern 还是特殊枚举值？→ ⚠️ 错误处理模式需统一声明 | ⚠️ |
| 18 | §五 命名规范表 | AI 生成的标识符 | 文本（标识符字符串） | 按规范表命名：类=名词、方法=动词+名词、布尔=谓词、集合=复数名词 | 规范化的标识符 | 所有代码文件 | ✅ 规范表 6 行，每行有好的/坏的例子。但缺少：接口命名（I-前缀？）、抽象类命名（Base-前缀？）、常量命名（全大写？）、Unity 特有命名（SerializeField 字段前缀 m_ 或 _？）→ ⚠️ 命名规范覆盖不完整 | ⚠️ |
| 19 | §五 代码审查清单 | AI 生成的文件 | 文本（源代码+注释） | 逐项检查 10 条 | 检查结论（每项 ✅/⚠️/❌） | 提交前审查 | 清单 10 项——但各项目标的主观性不同（"有没有深模块？"→ 判断标准是什么？"代码是否对读者易理解？"→ 谁来判断？）→ ⚠️ 缺少可操作的判定标准 | ⚠️ |
| 20 | §六 Python 过渡期规范 — 数据层共享 | JSON 数据文件（data/） | 外部 JSON 文件 | Python 模拟和 C# Unity 各自读取同一 JSON → 分别解析 | Python: dict/list; C#: ScriptableObject/反序列化类 | Python 模拟脚本、C# 运行时 | JSON 中的数据如果 Python 模拟需要修改（如参数调优），C# 如何同步？手动复制还是共享引用？→ ❌ 数据同步机制未定义 | ❌ |
| 21 | §七 阶段 1 — 数据层+基础工具链 | 设计文档中的参数规格 | 引用<规则/核心机制.md §十 参数速查> | 定义 C# 数据结构 + 迁移 Python 公式到 C# | C# class/ScriptableObject + CombatResolver 等 | 阶段 2（实体层+游戏流） | "将现有 JSON 数据设计 C# 序列化格式"——谁来做这个转换？手动还是工具？→ ⚠️ 未定义。CombatResolver "从现有 Python 模拟迁移公式"——sim_moonlight_v2_sanity.py 是月光场公式，sim_battle 系列已废弃→战斗公式的 Python 参考在哪里？→ ❌ 迁移源不存在 | ❌ |
| 22 | §八 验证方式 — "代码公式必须与设计文档一致" | 代码中的公式实现、设计文档中的公式 | 引用<设计文档公式>、引用<C#代码公式> | 逐公式比对验证 | 一致性结论（✅/⚠️/❌） | 代码审查、自动化测试 | 如何自动化验证公式一致性？手工比对不 scalable（364 条链路 × N 条公式）→ ⚠️ 验证手段不明确 | ⚠️ |

---

## 缺口汇总

| # | 位置 | 严重度 | 描述 |
|----|------|--------|------|
| 1 | §三 | ⚠️ | 事件总线定位不明确——属于 Engine 还是 Infrastructure？ |
| 2 | §3.2 D1 | ⚠️ | 数据层"只读"——但引擎输出（TurnResult）如何写回实体？写入路径未定义 |
| 3 | §3.2 D2 | ⚠️ | 纯函数边界：随机数/RNG 种子注入机制未定义；查表是否算副作用？ |
| 4 | §3.2 D3 | ⚠️ | 引擎/游戏流层职责分界线模糊——5阶段回合流程的编排代码在哪里？ |
| 5 | §3.2 D4 | ⚠️ | 事件总线线程模型、Unity 主线程约束、事件拦截/修改规则未定义 |
| 6 | §3.2 D5 | ⚠️ | "通用"与"专用"的精确边界：技能效果是数据还是代码？ |
| 7 | §3.3 Layer1 | ⚠️ | 15+ 数据类仅列出类名——字段规格全部缺失 |
| 8 | §3.3 Layer2 | ⚠️ | 仅 CombatResolver(§4.1)/LinkActivator(§4.2)/MoonlightField(§4.3) 有接口设计——其余 7+ Engine 模块无接口 |
| 9 | §4.1 | ❌ | **CombatAction 和 CombatContext 类型未定义**——核心输入类型缺失 |
| 10 | §4.1 | ❌ | **TurnResult 的子事件类型（DamageEvent 等）字段未定义**；newSpeedOrder 数组索引→参战者映射未定义 |
| 11 | §4.2 | ❌ | **LinkMValues、SituationType、FocusSet 类型未定义**——核心输入类型缺失 |
| 12 | §4.3 | ⚠️ | CollapseResult 的消费方不清楚各字段的精确应用方式（谁乘 0.3？baseline 是什么？） |
| 13 | §五 R1 | ⚠️ | ">5句话"度量标准主观——缺少可操作判定标准 |
| 14 | §五 R2 | ⚠️ | "关键模块"判定标准未定义——枚举闭合性存疑 |
| 15 | §五 R3 | ⚠️ | 信息泄露检查的粒度和判定标准未定义 |
| 16 | §五 R5 | ⚠️ | 错误处理模式（null object vs 异常 vs TryXxx）未统一声明 |
| 17 | §五 命名 | ⚠️ | 缺少接口/抽象类/常量/Unity 特有字段的命名规范 |
| 18 | §五 审查清单 | ⚠️ | 审查清单 10 项多为主观判断——缺少可操作判定标准 |
| 19 | §六 | ❌ | **Python↔C# 数据同步机制未定义**——JSON 修改后如何同步？ |
| 20 | §七 阶段1 | ❌ | **CombatResolver 的 Python 公式迁移源不存在**——sim_battle 系列已废弃，战斗公式无 Python 参考 |
| 21 | §八 | ⚠️ | 公式一致性验证手段未定义——手动比对不 scalable |

---

## 半径扩张 — 待复查

| 修复点 | 受影响消费者 | 复查状态 |
|--------|------------|---------|
| #9 CombatAction/CombatContext 类型定义 | #1 ResolveTurn 接口、#4 游戏流层调用、所有 Engine 模块 | 待修复 |
| #10 TurnResult 子类型定义 | #4 游戏流层消费、#5 事件总线事件类型、Layer3 实体状态更新 | 待修复 |
| #11 LinkMValues/SituationType/FocusSet 类型定义 | #1 LinkActivator 接口、Layer1 数据类、预烘焙管线 | 待修复 |
| #19 Python↔C# 同步机制 | §六 全部过渡期规范、Layer1 数据类设计、data/ JSON 维护流程 | 待修复 |
| #20 战斗公式 Python 迁移源 | §七 阶段1 实施、CombatResolver 实现、单元测试基线 | 待修复 |

---

## 统计
- 总 trace 行数: 22
- ✅ 0 / ⚠️ 17 / ❌ 5
- 待复查: 5 个修复点

---

## 总体评估

计划在**架构层面**（分层思路、深模块理念、书中原则映射）是清晰的——这是它的强项。但在**类型定义层面**有系统性的缺口：核心接口使用的输入/输出类型（CombatAction, CombatContext, LinkMValues, FocusSet 等）只有名称没有字段定义。这不是设计错误——这是设计阶段的自然状态——但意味着计划目前处于"架构草图"阶段，还无法直接进入实现。

**5 个 ❌ 缺口的共性**：都是"名字有了，类型体没有"——接口签名写出来了，但参数和返回值的内部结构未定义。这 5 个是阻塞级缺口——在进入代码生成之前必须补全。

**17 个 ⚠️ 缺口的共性**：边界条件/职责分界未细化——层间通信协议、纯函数副作用边界、错误处理策略、命名规范覆盖范围等。这些是实现过程中会遇到的具体问题，建议在阶段 1 开始前通过 grilling 逐项决策。

**建议**：在进行任何 C# 代码生成之前，先补全 5 个 ❌ 的类型定义。可以单开一个 grilling 话题："代码框架计划的类型定义闭合"，逐个敲定 CombatAction、CombatContext、TurnResult 子类型、LinkMValues、FocusSet 的字段规格。

---

*创建: 2026-08-06 10:00 | 基于: review-plan SKILL.md v2*
*关联: [/home/dog/.claude/plans/immutable-shimmying-star.md](/home/dog/.claude/plans/immutable-shimmying-star.md)*
