# SpeedScoreCalculator + TurnOrderBuilder — 实现规格

> 三成分速度排序（察觉/决断/执行）与同速掷硬币破平——csharp-engine step 7 的两个引擎模块。版本: v1.1

## 一、范围与依赖

| 项 | 内容 |
|----|------|
| 覆盖 | `SpeedComponents`/`SpeedWeights` 两个 record（SpeedComponents.cs 从零实现）+ `SpeedScoreCalculator`（三分量提取 + 逐节点回落 + 加权合成）+ `TurnOrderBuilder.BuildOrder`（排序 + 破平） |
| 不覆盖 | 权重偏移逻辑（回合战斗流程 §3.1 偏移表 5 来源——本 feature 恒等权，B4）；等待（§3.5——step 10 行动窗口）；Phase 编排与事件（step 9-11）；NPC salience 竞争（step 12） |
| 前置依赖 | csharp-data-layer ✅（GameData/WsensoryMatrix.RegionIds 行序）、csharp-wmatrix ✅（canonical 69 行序契约）、csharp-wc-dynamics ✅（WcState）、csharp-tone ✅（M1 实测值表）、csharp-cstc ✅（GurneyState/LoopSalience——决断分与执行分数据源）、csharp-engine-types ✅（CalibrationConfig.SpeedW1/2/3/PerceptionThreshold/M1SustainPenalty；IRng） |
| 阻塞 | 阻塞哪些下游工作：step 8 基础行动结算（行动顺序是 gate_bonus 结算的前置）、step 10 战斗流程编排 |

## 二、数据结构

### 2.1 SpeedComponents（新建 record，SpeedComponents.cs）

速度三成分——均已回落/惩罚后的**终值**（计算方见 §三 3.2）：

| 字段 | 类型 | 值域 | 备注 |
|------|------|------|------|
| Perception | float | [0, 1] | 察觉分——4 节点均值（逐节点回落已应用） |
| Decision | float | [0, 1] | 决断分——mean(c_loop, 3 环路)；**无回落**（c_loop≈0 即决断慢，与 csharp-cstc「c=0 → gate 0.843 门控抑制」一致——0.843 为 csharp-cstc AC-4 的 300 回合迭代收敛值，非单步值） |
| Execution | float | [−0.1, 1.5] | 执行分——mean(a(Precentral), a_SD1_somatic) + M1 惩罚；上限 1.5 来自 a_SD1 单群体解析界 [0, 2]（运行时状态模型 §三「解析界：SD1 [0,2]」——可达性：u_SD1 = c·(1+DA)，c∈[0,1]、DA∈[0,1] → a_SD1 无条件 ∈ [0,2]，非负且可达 2.0），下限来自惩罚 −0.1 |

### 2.2 SpeedWeights（新建 record，SpeedComponents.cs）

| 字段 | 类型 | 值域 | 备注 |
|------|------|------|------|
| W1 | float | — | 察觉权重。默认 1/3（CalibrationConfig.SpeedW1） |
| W2 | float | — | 决断权重。默认 1/3 |
| W3 | float | — | 执行权重。默认 1/3 |

静态工厂 `SpeedWeights.FromCalibration(CalibrationConfig cal)` → (SpeedW1, SpeedW2, SpeedW3)（AC-15 覆盖）。权重只在 §3.1 合成层（非成分内部）——运行时状态模型 §8.1 已指针化（2026-08-13 step 7）。

## 三、接口定义

### 3.1 SpeedScoreCalculator

```csharp
public sealed class SpeedScoreCalculator
{
    public SpeedScoreCalculator(GameData data, CalibrationConfig cal);
    public IReadOnlyList<int> PerceptionRows { get; }   // 4 察觉节点行索引，顺序 = PerceptionFids（AC-1 可测性）
    public int PrecentralRow { get; }                   // Precentral 行索引（AC-1 可测性）
    public SpeedComponents ComputeComponents(WcState a, LoopSalience salience, GurneyState gurney, bool isDefending);
    public float ComputeScore(SpeedComponents components, SpeedWeights weights);
}
```

**构造**：从 `data.Wsensory.RegionIds` 解析 5 个行索引（4 察觉节点 + Precentral，§五）→ `fidToRow` 字典（镜像 WMatrixBuilder Step 1 / CstcGating 构造）。`cal` 保存引用（不可变 record）。

**公开访问器**：`PerceptionRows`/`PrecentralRow`——构造期解析结果只读公开（AC-1 可测性；镜像 CstcGating.CiRows 公开先例）。不泄露新信息：canonical 行序已由 RegionIds 公开锁定。🔧 修正 2026-08-13（实现新增访问器，L1 补正入接口块，免重审）。

**ComputeComponents**（纯函数，无首回合特判——B1）：

```
察觉 = mean(a[4 察觉节点]，逐节点回落)     回落: a_j < PerceptionThreshold → RestPerception_j（§四 4 常量）
决断 = (salience.Somatic.C + salience.Cognitive.C + salience.Limbic.C) / 3    无回落
执行 = (a[Precentral 行] + gurney.Somatic[0]) / 2 + (isDefending ? cal.M1SustainPenalty : 0)
```

- `gurney.Somatic[0]` = a_SD1（GurneyPopulation 枚举序 0=SD1——GurneyState 文档契约）——Putamen 代理（Q3=A，B3）。
- 输入不可变（防御性拷贝/只读消费，AC-13）；输出为新对象。
- 异常：null 输入 → ArgumentNullException；`a.A` 长度 ≠ 69 → ArgumentException；`gurney.Somatic` 长度 ≠ 5 → ArgumentException（镜像 CstcGating 防御；GurneyState 契约 = 每环路 5 群体，本方法仅消费 Somatic[0]）（AC-12）。
- 未定义行为（文档化，不防御）：NaN/Infinity 输入。

**ComputeScore**：`speed = W1×Perception + W2×Decision + W3×Execution`（回合战斗流程 §3.1；分量归一化 mean 见 B2）。speed 为**序数值**——绝对量无意义（§3.1「速度只需要一个序数结果」）。值域等权下数学界 [−0.0333, 1.1667]；含回落后可达界 ≈ [0.0167, 1.1667)——上端为上确界（a(Precentral) 严格 < 1.0，运行时状态模型 §4.1 凸组合保证，1.1667 仅渐近/合成可达），下端可达（察觉 ≥ 0.15 由回落保证——数学下界不可达）。异常：components/weights null → ArgumentNullException（分别校验）。

### 3.2 TurnOrderBuilder

```csharp
public static class TurnOrderBuilder
{
    public static int[] BuildOrder(float[] scores, IRng rng);
}
```

- 输出 = 输入索引数组，[0] = 最快（回合战斗流程 §3.4）。
- **排序**：score 降序；平局 = **逐位相等（float ==）**——demo 中平局来自相同状态，天然精确相等（声明：无 epsilon 合并）。
- **破平**（§3.4「同速时掷硬币，每回合重新破平」）：每个平局组内 Fisher-Yates 洗牌。**算法写死**（RNG 消费序契约，测试镜像依赖）。注：任务issue D9 草案写「IRng.NextFloat()」——本 spec 定为 NextInt(i+1)（m 面骰），以本 spec 为准：
  1. 组内索引保持输入升序；
  2. `for i = m−1 downto 1: j = rng.NextInt(i+1); swap(group[i], group[j])`；
  3. m = 1 时不消费 rng。
- 组间顺序 = 分数降序；组内 = 洗牌结果。拼接输出。
- 异常：null → ArgumentNullException（scores 与 rng 分别校验）。长度 0 → 空数组；长度 1 → [0]（不消费 rng）。NaN → 未定义行为。

## 四、枚举与常量

| 常量 | 符号 | 值 | 来源 |
|------|------|-----|------|
| 察觉静息值 ×4（SpeedScoreCalculator 私有常量） | RestPerception_Pericalcarine 等 | **0.6309757f / 0.6316023f / 0.6327866f / 0.6751733f** | csharp-tone 工作issue 01 M1 实测值表（69 行附录）逐 fid 值；⚠️ 数据漂移注：脑区数据变更 → M1 实测值变更 → 常量须同步（AC-3 锚点即哨兵） |
| 察觉回落阈值 | PerceptionThreshold | 0.15f | CalibrationConfig（[NEW] 占位待校准，回合战斗流程 §3.3）——**引用，不重定义** |
| M1 占用惩罚 | M1SustainPenalty | −0.1f | CalibrationConfig（[NEW] 占位待校准，§3.3）——**引用，不重定义** |
| 速度权重 | SpeedW1/W2/W3 | 1f/3f | CalibrationConfig（回合战斗流程 §3.1 默认等权）——**引用，不重定义** |
| WC 维度 | RegionCount | 69 | WcState.A 长度（csharp-wmatrix canonical 契约） |

## 五、交叉引用约束

1. **行序契约**：`a.A` 行序 = canonical 69 = `Wsensory.RegionIds`（csharp-wmatrix spec 行序契约唯一 canonical）。5 个解析名：Pericalcarine、TransverseTemporal、Insula、AnteriorCingulateCortex（4 察觉节点，回合战斗流程 §3.2 节点清单）+ Precentral（执行分 M1 项）。解析失败 → KeyNotFoundException（隐式，镜像 CstcGating 构造 C1 文档化行为）。
2. **数据流时序**（运行时状态模型 §7.1）：`salience` 与 `gurney` 必须来自**本回合同一次** `CstcGating.Step` 的返回值（步骤 4-5 → Phase 3 速度重算）——不跨回合混用（编排层职责，本 spec 只声明输入语义）。注意：ComputeComponents 参数序 `(a, salience, gurney)` 与 `CstcGating.Step` 返回序 `(Gurney, Gates, Salience)` 相反——调用侧按参数名配对，勿按返回序位置错配。
3. **a_SD1 语义**：`gurney.Somatic[0]`——群体索引按 GurneyPopulation 枚举序（GurneyState 文档契约），不得按位置硬猜。
4. **破平 RNG 消费序**：§三 3.2 写死的 Fisher-Yates 方向与 NextInt 参数即契约——任何改动破坏 AC-10 镜像。

## 六、验收标准

| AC | 验收标准 | 锚点/判定 |
|----|---------|----------|
| AC-1 | 构造解析 5 行索引（4 察觉 + Precentral），行序 = RegionIds | 测试从 RegionIds 现算期望索引；未命中名 → KeyNotFoundException。**哨兵覆盖边界**：名删除 → KeyNotFound 哨兵；值漂移 → AC-3/AC-8 静息锚点哨兵；行序重排 → 契约中性（全消费者按名解析，canonical 行序契约 §五 1，无需哨兵） |
| AC-2 | 察觉 = mean(4 节点)，回落不触发（全部 ≥ 阈值 0.15） | 全 0.7 → 0.7；混合 (0.7,0.7,0.7,0.16) → **0.565f**（f32 复算与 0.565f 字面量逐位相等——十进制 0.565 并非 f32 精确可表示，不变式为「计算结果与 0.565f 字面量逐位相等」，测试侧现算，1e-5） |
| AC-3 | 察觉逐节点回落（Q2=A）——4 个回落常量逐节点单独钉住 | (0.7, 0.7, 0.7, 0.05) → **0.6937933**（0.05→ACC 静息 0.6751733）；(0.05, 0.7, 0.7, 0.7) → **0.68274397**（→Pericalcarine 0.6309757）；(0.7, 0.05, 0.7, 0.7) → **0.68290060**（→TransverseTemporal 0.6316023）；(0.7, 0.7, 0.05, 0.7) → **0.68319666**（→Insula 0.6327866）；全回落（4 节点 <0.15）→ **0.64263445**（4 静息均值）；端点：恰好 0.15 → 不回落（≥ 阈值）；锚点 1e-5，回落常量 = §四 4 值 |
| AC-4 | 决断 = mean(c_loop, 3 环路)，无回落 | 静息锚：C=(0.665469, 0.696963, 0.692102) → **0.68484467**（1e-5）；全 0 → 0（不回落） |
| AC-5 | 执行 = mean(a(Precentral), a_SD1)，未防御无惩罚 | 静息锚：a(Precentral)=0.6306536、Somatic[0]=0.9848941 → **0.80777383**（1e-5） |
| AC-6 | M1 惩罚：IsDefending → 执行 −0.1 | 0.80777383 → 0.70777383（1e-5）；IsDefending=false → 不变 |
| AC-7 | 加权合成 3 RED 用例（plan §4.5） | 等权 (0.5,0.5,0.5) → **0.5**；w(0.5,0.25,0.25)·(0.5,0.4,0.4) → **0.45**（f32 实测 0.44999999，1e-5）；等权 (1,1,1) → **1.0** |
| AC-8 | 首回合静息 speed（B1 交付机制——静息状态直算，无特判） | ComputeComponents(静息状态) → (0.64263445, 0.68484467, 0.80777383)；等权 ComputeScore → **0.71175098**（1e-5；任务issue 实测 #6） |
| AC-9 | BuildOrder 非平局：分数降序，rng 无关 | [0.9, 0.5, 0.7] → [0, 2, 1]；不同 rng 同结果 |
| AC-10 | BuildOrder 全平局：破平 = §三 3.2 Fisher-Yates | 测试镜像**独立实现**（不得复制引擎代码——独立实现镜像即证伪器）+ 同种子 DeterministicRng → 期望排列**逐元素相等**（RNG 消费序契约）；[0.5,0.5,0.5] 即组大小 m=3；结果 ⊆ 输入索引排列；同种子两次调用 → 相同 |
| AC-11 | BuildOrder 混合平局组 | [0.8, 0.5, 0.5, 0.2] → 结果[0]=0、结果[3]=3、中间两位 = {1,2} 的洗牌；固定种子 → 精确序 |
| AC-12 | 契约防御 | ComputeComponents：a/salience/gurney null → ArgumentNullException；a.A 长度 {0,68,70} → ArgumentException；gurney.Somatic 长度 {0,4} → ArgumentException；ComputeScore：components/weights null → ArgumentNullException；BuildOrder：scores/rng null → ArgumentNullException |
| AC-13 | 输入不可变 + 确定性 | ComputeComponents 输入快照不变 + 输出为新 record（值语义，与输入无引用共享——SpeedComponents 仅 3 个 float 字段，构造性保证）+ 重复调用逐位相等；BuildOrder 同种子重复调用逐位相等 |
| AC-14 | 边界 | 空 scores → 空数组（不消费 rng）；单元素 → [0]（不消费 rng）；a_SD1=0 → 执行 = mean(a(Precentral), 0)；**a(Precentral)=1.0 且 Somatic[0]=2.0 且未防御 → 执行 = 1.5**（完整输入组合——Somatic[0]=2.0 为合成状态 c=1.0 ∧ DA=1.0 使 u_SD1 达解析界上限，§二 2.1）；c_loop 全 0 → 决断 0 |
| AC-15 | SpeedWeights.FromCalibration | 默认 CalibrationConfig（SpeedW1/2/3 = 1/3）→ 三字段逐位等于 1f/3f；自定义 cal（SpeedW1=0.5/SpeedW2=0.25/SpeedW3=0.25）→ (0.5, 0.25, 0.25) 逐位相等 |

## 七、本 spec 自检清单

1. **数学公式逐项对照**：三成分公式/逐节点回落/加权合成与 回合战斗流程 §3.1-3.3 + plan §4.5 逐字一致（含 mean 归一化 B2、Putamen 代理 B3）。
2. **数值断言全部实测**：全部锚点（§四 4 常量、静息三分量、0.71175098、0.6937933/0.68274397/0.68290060/0.68319666 逐节点回落、RED 0.5/0.45/1.0、AC-15 1f/3f）经 python f32 复算（任务issue 01 实测表 + audit report）——禁凭记忆写。
3. **行序契约明确**：canonical = RegionIds 唯一（§五 1）；AC-1 三面哨兵边界承接（名删除/值漂移/行序重排）。
4. **接口注释先行**：构造 + ComputeComponents + ComputeScore + BuildOrder 的 XML doc 含职责/输入/输出/异常/未定义行为/来源/偏差标注（"设计两次"约束，plan §十一）。
5. **边界值覆盖**：阈值端点 0.15 / 静息 / 全 0 / a_SD1=0 与 2.0（完整输入组合）/ 空与单元素 scores / 全平局 / 混合平局 / FromCalibration（AC-15）。
6. **确定性**：无 static 可变状态；RNG 只经 IRng 注入（BuildOrder）；AC-13 实证逐位相等。
7. **偏差声明完整**：B1（首回合交付机制）/B2（归一化 mean）/B3（Putamen 代理）/B4（偏移不覆盖）注释逐条对应。
8. **常量复用漂移注**：CalibrationConfig 三参数引用不重定义；4 静息常量来源注释（csharp-tone M1 表）+ 数据漂移哨兵声明（§四）。
9. **破平算法显式**：Fisher-Yates 方向/参数/RNG 消费序写死（§三 3.2）——AC-10 镜像锁定，禁实现侧自由发挥。

## 八、偏差声明

| # | 偏差 | 设计文档 | 本 spec | 理由 |
|---|------|---------|---------|------|
| B1 | 首回合静息值交付机制 | 回合战斗流程 §3.2（Q1=A：首回合三分量取静息值）；运行时状态模型 §7.3「战斗开始时 a(0)=0.10」 | 计算器**无首回合特判**——静息值由战斗初始状态自然给出：遭遇前静息 trace → 战斗初始 WC = 静息不动点（step 10 编排层职责）；a(0)=0.10 仅为 WC 模拟冷启动种子。Gurney a=0 起步亦无碍（a_SD1 纯前馈，一步即静息 0.9849，任务issue 实测 #4） | 引擎保持纯状态函数；「首回合静息」= 状态的静息，非计算的特判。§7.3 已加澄清句（2026-08-13） |
| B2 | 分量归一化 mean | 回合战斗流程 §3.2/§3.3 原求和形态（察觉 4 节点和、执行 2 节点和）——🔧 2026-08-13 已按 plan §十二-8 写回修正为均值形态（commit cb68803），本 spec 与修正后文档一致 | 统一取均值 | plan §十二-8：三成分量纲可比（0-1）、等权 1/3 语义成立；求和形态下察觉实际权重 4× |
| B3 | Putamen 代理 | 回合战斗流程 §3.3 原「a(Putamen)(t)」——Putamen 为 CSTC 节点无 WC a(t)；🔧 2026-08-13 已写回（§3.2/§3.3 现为 Putamen 代理 = a_SD1_somatic，commit cb68803），本 spec 与修正后文档一致 | a_SD1_somatic（Q3=A，plan §十三-4 已裁决） | SD1 = 壳核直接通路（D1 MSN）的 Gurney 结构同构映射，非任意代理 |
| B4 | 权重偏移不覆盖 | 回合战斗流程 §3.1 偏移表（5 来源） | 本 feature 恒等权（CalibrationConfig 默认 1/3） | plan §4.5 公式块无偏移项；demo 范围外；偏移属后续 feature |

## 参数速查表

| 参数 | 符号 | 默认值 | 位置 |
|------|------|--------|------|
| 察觉节点 | — | Pericalcarine/TransverseTemporal/Insula/AnteriorCingulateCortex | 回合战斗流程 §3.2 |
| 察觉静息值 ×4 | RestPerception_j | 0.6309757/0.6316023/0.6327866/0.6751733 | 本 spec §四（csharp-tone M1 实测表） |
| 察觉回落阈值 | PerceptionThreshold | 0.15 | CalibrationConfig（[NEW] 占位待校准） |
| M1 占用惩罚 | M1SustainPenalty | −0.1 | CalibrationConfig（[NEW] 占位待校准） |
| 速度权重 | SpeedW1/W2/W3 | 1/3 | CalibrationConfig；回合战斗流程 §3.1 |
| Putamen 代理 | a_SD1_somatic | 静息 0.9848941 | 本 spec §三 3.1（Q3=A）；GurneyState.Somatic[0] |

## 变更日志

| 版本 | 日期 | 变更 | 触发 | 审计范围 |
|------|------|------|------|----------|
| v1.0 | 2026-08-13 | 初稿（§一~§八 + AC-1~14 + B1-B4） | 任务issue 01（Q1=A/Q2=A/Q3=A 裁决后） | 全量审计 |
| v1.1 | 2026-08-13 | F1 执行分值域引用改正（→运行时状态模型 §三）+ 可达性论证；F2 AC-14 完整输入组合声明；F3 gurney.Somatic 长度防御；F4 ComputeScore null 防御；F5 AC-1 三面哨兵边界；F6 3 个逐节点回落锚点（0.68274397/0.68290060/0.68319666）；F7 AC-15 FromCalibration；L1 批（AC-2 措辞+用例 0.565、0.843 收敛语境、D9 NextInt 注、§五 2 参数按名配对、值域可达界 0.0167、AC-13 措辞、AC-10 镜像独立实现+m=3）；B2 写回记录 | 全量审计 v1.0 报告（0❌/7⚠️ CONFIRMED/2 REFUTED/15 info——有条件通过） | Δ审计（变更章节 + 半径扩张） |
| v1.1 (L1 修正) | 2026-08-13 | Δ审计 3 info 清扫：AC-2「0.565f 字面量逐位相等」措辞（十进制 0.565 非 f32 精确）；§三 3.1 可达上界渐近注（1.1667 为上确界，可达界半开）；B3 补「已写回」标注（与 B2 对称） | Δ审计（0❌/0⚠️/3info——等效通过） | 免重审（L1） |
| v1.1 (🔧 修正) | 2026-08-13 | 实现新增公开访问器 `PerceptionRows`/`PrecentralRow` 补入 §三 3.1 接口块（AC-1 可测性；镜像 CstcGating.CiRows 先例） | 工作issue 01 实现发现（L1） | 免重审（L1） |

---
*创建: 2026-08-13 | 更新: 2026-08-13 | 版本: v1.1*
*关联: [任务issue 01](../../archive/grilling/csharp-speed/design/issues/01-speed-spec.md), [csharp-engine plan §4.5](csharp-engine-roadmap.md), [回合战斗流程](../../rules/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md) §3.1-3.5, [运行时状态模型](../../rules/skill-tree/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md) §7.1/§7.3/§8.1*
