# 架构

> 本仓库的**边界声明**：四层各自的职责、允许的依赖方向、已知的越界点。
>
> 这是一份**声明**而非建议——[项目规约](design/conventions/README.md) 与校验器以此为据。

## 目录

1. [一、四层结构](#一四层结构)
2. [二、依赖方向](#二依赖方向)
3. [三、数据流：设计与代码如何对齐](#三数据流设计与代码如何对齐)
4. [四、已知越界点](#四已知越界点)
5. [五、边界如何被强制](#五边界如何被强制)

---

## 一、四层结构

```
design/      设计文档（正典）      primary artifact —— 回答「这个游戏是什么」
  rules/ entities/ space/ events/ presentation/ pipeline/   六维正典
  spec/      实现规格与输入素材（被代码或正典消费的承重内容）
  framework/ 六维状态 + 维度索引   decisions/ 决策树   conventions/ 规约
  archive/   grilling 源记录 + 垃圾箱（非正典）

reference/   外部参考            文献 / 书籍 / 已废弃子系统（保留为数据源）

code/        实现与验证          证明设计跑得起来，不反向定义设计
  src/       C# 逻辑引擎（.NET 8）—— 规则结算的唯一实现
  unity/     Unity 呈现沙盘 —— 纯呈现，不含逻辑正典
  sim/       Python 数值验证 —— 一次性研究脚本
  tools/     校验器与数据生成 —— 服务于 design/ 与 data/

data/        结构化数据契约      设计参数的机器可读形态
```

**核心判据**：`design/` 是唯一真相源。当代码与设计冲突时，**以 `design/` 为准并修代码**——不是反过来。

## 二、依赖方向

```
        design/  ──────┐
           │           │  （人工同步：设计 → 数据 → 代码）
           ▼           ▼
        data/  ────►  code/src/  ────►  code/unity/
                       ▲                    │
                       └────────────────────┘
                         ✗ 不允许：unity 不得反向定义逻辑
```

| 方向 | 允许 | 说明 |
|---|---|---|
| `design/` → `data/` | ✅ | 参数的权威定义在 `design/`，`data/` 是其机器可读形态 |
| `data/` → `code/src/` | ✅ | 引擎读数据文件，不硬编码参数 |
| `data/` → `code/unity/` | ✅ **仅生成期** | ✏️ 2026-09-12 新增。Unity **Editor 侧生成器**可读 `data/` 作为生成输入（`role: generator-input`，首个实例 `data/action_set.json`）；**运行时不得读 `data/`**——运行时消费的是生成器写出的 C# 静态表。生成器是「呈现管线」的一部分，不是逻辑正典 |
| `code/src/` → `code/unity/` | ✅（**当前未接线**） | 计划为 DLL 桥接；现状见 §四 |
| `code/` → `design/` | ✅ 仅注释引用 | 代码可引设计文档作为**来源注记**，但不得把设计文本当运行时输入 |
| `design/` → `code/` | ❌ | 设计文档不依赖实现细节 |
| `code/unity/` → 逻辑正典 | ❌ | Unity 不得重新实现规则（见 §四） |
| `code/` → `reference/` | ❌ | 参考材料不参与正典 |

**当前阶段的特殊分界**：玩家交互 = 3D 技能树 + 快捷槽，技能直接走数值结算（伤害 / buff / debuff）；NPC AI = 脑区链路预烘焙查表（6 性格标签 → 髓鞘化偏移 → 27 情境 × SAN 分段行为概率分布）。

## 三、数据流：设计与代码如何对齐

```
design/rules/核心机制.md §10.1（权威参数表）
        │  人工同步（参数必须带来源注释）
        ▼
data/*.json（引擎契约）           ← 8 个文件由 GameDataLoader.LoadAll 消费：
        │                            brain_regions / tripartite_model / W_sensory /
        │                            situation_primitives / signal_types /
        │                            alpha_patterns / env_tones / moonlight_landing
        ▼
code/src/YouAreNotTheFish.Core（.NET 8 库）
        │  CalibrationConfig 集中承载可调常量，每个字段的 XML 注释写明来源章节
        ▼
code/src/YouAreNotTheFish.Console（harness）/ Tests（计数见 构建与测试 §四）
```

**对齐规则**：

1. **参数只在 `design/` 定义一次**，`data/` 与 `code/` 都是它的下游形态。
2. **代码里每个常量必须有来源注释**（`来源：<文档> §<节>`），无来源的常量视为缺陷。
3. **同一参数出现在多处时必须一致**——由 `code/tools/validate_params.py` 跨文件机械核验（`data/term_registry.json` 的 `numerical_locations` 是其索引）。
4. **迁移必须一次做完**：数据格式变更（如 `W_sensory` 从 69×6 扩到 69×8）必须同时更新数据、代码、代码注释、设计文档、数据 README——历史上漏做过一次（挂账 T6b，2026-09-12 才补齐）。

## 四、已知越界点

| 越界点 | 现状 | 处置 |
|---|---|---|
| **`code/unity/Assets/Scripts/DemoSolver.cs`** | 手抄了 `CalibrationConfig.Default` 的结算常量（伤害 `4f`、命中 `0.75f`、SAN 惩罚 `1.3`/`2`、HP = `san×0.5`）。文件自述「临时白盒结算（待 EngineSolver 替换）」 | **这是本仓唯一的反向污染点。** 处置已定：**Q6b 裁定 A（子集桥接）**，见下方 §4.1——桥接工程链接 Core 的 3 个源文件产出 netstandard2.1 程序集，Unity 侧 `EngineSolver` 替换 `WhiteboxSolver`；在那之前，**凡修改结算常量必须同时改这里**，否则 demo 与引擎静默分叉 |
| `code/src/YouAreNotTheFish.Core.Unity/` | 桥接工程草稿，**从未构建成功** | 已于 2026-09-12 删除（D10）。**Q6b 已定案（2026-09-13，裁定 A）**，重建范围与准入条件见 §4.1 |
| `code/unity/` 的 `.meta` 全缺、场景不入库 | Unity 工程不完整：`ProjectSettings/` 只有 `ProjectVersion.txt`、`Assets/Scenes/` 空、`Packages/packages-lock.json` 缺失，场景靠 Editor 菜单运行时生成 | ✏️ 2026-09-12：**已立项**（[#136](https://github.com/verystrongdog/game/issues/136)「Unity 资产身份」）。在此之前是已知取舍：重开工程会重新生成 GUID。**不是设计问题，是工程卫生**——但它是「手调动画成果无法入库」的根因：Blend Tree 阈值、transition 参数、Avatar Mask 全部序列化在需要 GUID 的资产里 |
| `code/sim/` 写 `data/sim_results/` | 研究脚本的 `--outdir` 默认 `.`，即写入 `data/` | 已在 `.gitignore` 排除（2.6G 生成物）。建议改为默认落仓库外 |

### 4.1 Q6b 桥接范围裁定：**A — 子集桥接 + 机械护栏**（2026-09-13 · [#135](https://github.com/verystrongdog/game/issues/135) · owner）

**结论：重建 `code/src/YouAreNotTheFish.Core.Unity/` 时只桥接 `DamageCalculator` 的传递闭包，用「链接源文件」而不是拷贝，并让桥接工程的编译进 CI 当护栏。**

**为什么必须定**：不定案则 `EngineSolver` 无法开工、`WhiteboxSolver` 继续手抄常量——上面表格第一行的反向污染点会一直挂着，CP-01 的 must-prove M1（Unity 通过适配层使用真实 Core）不可能成立。

**A 的闭包（2026-09-13 按类型引用 BFS 实测，不是估计）**：

| 文件 | 行数 | 需要的改动 |
|---|---|---|
| `code/src/YouAreNotTheFish.Core/Engine/DamageCalculator.cs` | 101 | **1 处**：`ArgumentNullException.ThrowIfNull(rng)` → 等价的 `if (rng is null) throw new ArgumentNullException(nameof(rng));`（netstandard2.1 无该 API；行为不变，引擎 416 项回归可证） |
| `code/src/YouAreNotTheFish.Core/Types/CalibrationConfig.cs` | 136 | `sealed record` + `init` → netstandard2.1 需 **`IsExternalInit` 垫片**（新增 1 个文件，业界标准做法） |
| `code/src/YouAreNotTheFish.Core/Types/IRng.cs` | 13 | 无需改动 |

> D6 原文的「4 文件」在仓内**没有依据可查**；上表这 3 个源文件 + 1 个垫片是按代码实测的闭包。

**护栏（A 的关键，解决"以后还会撞墙"）**：桥接工程用 `<Compile Include="../YouAreNotTheFish.Core/Engine/DamageCalculator.cs" Link="…"/>` **链接**（不是拷副本）这 3 个文件，目标框架 `netstandard2.1`；**它的编译进 CI**（现成的 `engine` job 即可承载）。于是：

- 任何动到这几个文件、破坏 netstandard2.1 的提交 → **编译当场红**，不靠约定也不靠人记得检查；
- 扩子集 = 往链接清单加一条，编译器立刻验证——所以"桥接面窄"不再是一条长期约束，而是一次可验证的小步骤。

**实测依据（2026-09-13，base `b7874b8`）**：

| # | 事实 | 读数 |
|---|---|---|
| 1 | Unity 侧的天花板 | Unity 6000.5.2f1 安装里只有 `Data/NetStandard/ref/**2.1.0**/netstandard.dll` 与 `Data/UnityReferenceAssemblies/unity-4.8-api/`，运行时是 `MonoBleedingEdge`（`unityjit-win32` / `unityaot-*`）→ **net8.0 程序集不可能被 Unity 直接加载** |
| 2 | B 选项的账（已随代码增长） | Core 里 `ThrowIfNull` **74 处 / 24 文件**（D6 记的 71/22 已过期）· `record` 声明 **56 个** · 集合表达式形态 **66 处**。B 也可做多目标 `net8.0;netstandard2.1`（引擎与 416 项测试不必降级），但**全部源码都要能在 ns2.1 下编译** |
| 3 | issue 的一条过期前提 | 原文「本机无 Unity Editor，`unity` 门禁 `available: false`」**已不成立**：实测 [gates.json](design/engineering/gates.json) 的 `unity` 门禁 `available: true`（2026-09-12 起 WSL interop 直驱 Windows Editor）。**C 与 B 的 Unity 侧前提本机可验** |

**三选项的代价与回滚**（裁定前评估，留档）：

| 选项 | 代价 | 可回滚性 |
|---|---|---|
| **A 子集桥接（已选）** | 3 文件 + 1 垫片的闭包；1 处 API 改写 + 1 处判空重写；新增桥接工程与 CI 一步。缺点：桥接面窄——由上面的护栏转成"编译期可发现" | 新增工程 + 2 处小改，`git revert` 即可；**不改数值、不改行为** |
| B 全量重构 | 74 + 56 + 66 处（多目标或降级两种做法）· 大范围改动 + 416 项全量回归 · 与「不在锁定提交中升级」的原则需协调 | 改动面大，回滚成本高（但仍是源码改动，无数据风险） |
| C 换桥接机制 | **C2「Unity 直接吃 net8.0 程序集」已被实测排除**（第 1 条）；剩下 C1 进程边界：不碰兼容墙，但要新增 IPC 协议、进程生命周期、确定性/日志一整套面 | 无数据风险，但架构面变更难回退 |

**为什么选 A**：闭包只有 3 个文件（实测），改动是 1 处 API 改写 + 1 处判空重写 + 1 个垫片，就能消灭本仓唯一的反向污染点、让 M1 成立；而 A 唯一的软肋（桥接面窄）被「链接源文件 + 编译进 CI」变成编译期问题。B 的收益只是"以后加文件不用动清单"，账单却是 74+56+66 处；C1 给 M1 换一种含义并新增一层 IPC，对一个确定性回合制引擎不值得。

**后续实施 issue 的准入条件**（供候选队列中的 P4d「Core→Unity 接缝实现」消费）：

1. **前置**：本裁定（§4.1）· `Unity 资产身份` 已闭合（[#136](https://github.com/verystrongdog/game/issues/136) / [#142](https://github.com/verystrongdog/game/issues/142)）· 本机 Unity 门禁可用
2. **范围**：① 新建 `code/src/YouAreNotTheFish.Core.Unity/`（`netstandard2.1`，链接上表 3 文件 + `IsExternalInit` 垫片）② `DamageCalculator.cs` 的 1 处 API 改写 ③ Unity 侧 `EngineSolver : IDemoSolver`（`CalibrationConfig.Default` + Unity 侧 `IRng` 实现）替换 `DemoCombatDriver.solver` 默认值
3. **判据**：① 桥接工程 `dotnet build` 退出码 0，且编译进 CI（`engine` job）② 引擎门禁回归 **416/0 不变** ③ Unity 侧编译 0 错误、`run_tests` 退出码 0 ④ **`WhiteboxSolver` 与 `DemoSolver.cs` 的手抄常量被移除或改为引用引擎值**——这是本 issue 存在的理由，不可省 ⑤ 手抄常量与 `CalibrationConfig.Default` 的逐字段一致性由测试钉住（替换前/后数值不变）
4. **不可省的反例**：只新建工程、不换 `DemoSolver` 的手抄常量 → 反向污染点仍在，**不算完成**

## 五、边界如何被强制

| 机制 | 覆盖什么 |
|---|---|
| `code/unity/Assets/Scripts/YANTF.Demo.asmdef` 的 `"references": []` | Unity 不引用 .NET 逻辑库——**结构性保证**逻辑正典只在 `code/src/` |
| `code/tools/validate_params.py` | 跨文件同名参数一致性（C1）+ 值域（C3）+ 跨系统聚合（C4） |
| `code/tools/validate_cross_refs.py` | 设计文档间引用完整性（死链 / 段引用） |
| `code/tools/validate_trash_isolation.py` | 归档隔离——活跃文档不引用垃圾箱 |
| `code/tools/validate_disease.py` / `validate_eligibility.py` / `validate_situation_fids.py` / `validate_tripartite_annotations.py` | `data/` 与 `design/entities/` 的契约 |
| `dotnet test code/src/YouAreNotTheFish.sln` | 引擎行为（测试计数见 [构建与测试 §四](design/engineering/build-and-test.md)——本节**不复述数字**，避免第二次漂移） |
| `data/term_registry.json` | 术语边界——哪些词在本项目里是**已废弃**的旧模型 |
| **资产区单机所有权**（✏️ 2026-09-12，人工约定，**尚无机械校验**） | `code/unity/Assets/**` 的资产（`.meta` / `.controller` / `.asset` / 场景）**只由这一台机生成与手调**。理由：手调成果入库要求 `.meta` GUID 稳定，多台机器各自手调资产则合并必然 GUID 冲突。**2026-09-12 补充**：原先的两份分叉拷贝已合并为一份（Linux 侧 WSL2 + Windows 侧 Editor 属同一台物理机，unity-cli 经 interop 直驱），该约束现在是"一台机一份拷贝"，不再有跨机面。文本（`design/` `data/` C# 源码与断言）不受此限 |

**提交前的底线**：`validate_cross_refs.py` 报 0 死链 + `dotnet test` 全绿。

---
*创建: 2026-09-12 | 更新: 2026-09-13（新增 §4.1：Q6b 桥接范围裁定 A · #135；测试计数改为引用构建与测试 §四 · #130）*
*关联: [项目规约](design/conventions/README.md), [设计总览](design/README.md), [协作指南](CONTRIBUTING.md), [数据说明](data/README.md)*
