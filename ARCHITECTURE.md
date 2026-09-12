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
code/src/YouAreNotTheFish.Console（harness）/ Tests（353 个）
```

**对齐规则**：

1. **参数只在 `design/` 定义一次**，`data/` 与 `code/` 都是它的下游形态。
2. **代码里每个常量必须有来源注释**（`来源：<文档> §<节>`），无来源的常量视为缺陷。
3. **同一参数出现在多处时必须一致**——由 `code/tools/validate_params.py` 跨文件机械核验（`data/term_registry.json` 的 `numerical_locations` 是其索引）。
4. **迁移必须一次做完**：数据格式变更（如 `W_sensory` 从 69×6 扩到 69×8）必须同时更新数据、代码、代码注释、设计文档、数据 README——历史上漏做过一次（挂账 T6b，2026-09-12 才补齐）。

## 四、已知越界点

| 越界点 | 现状 | 处置 |
|---|---|---|
| **`code/unity/Assets/Scripts/DemoSolver.cs`** | 手抄了 `CalibrationConfig.Default` 的结算常量（伤害 `4f`、命中 `0.75f`、SAN 惩罚 `1.3`/`2`、HP = `san×0.5`）。文件自述「临时白盒结算（待 EngineSolver 替换）」 | **这是本仓唯一的反向污染点。** 计划通过 DLL 桥接让 Unity 调用 `src/` 的逻辑；在那之前，**凡修改结算常量必须同时改这里**，否则 demo 与引擎静默分叉 |
| `code/src/YouAreNotTheFish.Core.Unity/` | 桥接工程草稿，**从未构建成功** | 已于 2026-09-12 删除（D10）。Q6b 定案时重建 |
| `code/unity/` 的 `.meta` 全缺、场景不入库 | Unity 工程不完整：`ProjectSettings/` 只有 `ProjectVersion.txt`、`Assets/Scenes/` 空、`Packages/packages-lock.json` 缺失，场景靠 Editor 菜单运行时生成 | ✏️ 2026-09-12：**已立项**（[#136](https://github.com/verystrongdog/game/issues/136)「Unity 资产身份」）。在此之前是已知取舍：重开工程会重新生成 GUID。**不是设计问题，是工程卫生**——但它是「手调动画成果无法入库」的根因：Blend Tree 阈值、transition 参数、Avatar Mask 全部序列化在需要 GUID 的资产里 |
| `code/sim/` 写 `data/sim_results/` | 研究脚本的 `--outdir` 默认 `.`，即写入 `data/` | 已在 `.gitignore` 排除（2.6G 生成物）。建议改为默认落仓库外 |

## 五、边界如何被强制

| 机制 | 覆盖什么 |
|---|---|
| `code/unity/Assets/Scripts/YANTF.Demo.asmdef` 的 `"references": []` | Unity 不引用 .NET 逻辑库——**结构性保证**逻辑正典只在 `code/src/` |
| `code/tools/validate_params.py` | 跨文件同名参数一致性（C1）+ 值域（C3）+ 跨系统聚合（C4） |
| `code/tools/validate_cross_refs.py` | 设计文档间引用完整性（死链 / 段引用） |
| `code/tools/validate_trash_isolation.py` | 归档隔离——活跃文档不引用垃圾箱 |
| `code/tools/validate_disease.py` / `validate_eligibility.py` / `validate_situation_fids.py` / `validate_tripartite_annotations.py` | `data/` 与 `design/entities/` 的契约 |
| `dotnet test code/src/YouAreNotTheFish.sln` | 引擎行为（353 个测试） |
| `data/term_registry.json` | 术语边界——哪些词在本项目里是**已废弃**的旧模型 |
| **资产区单机所有权**（✏️ 2026-09-12，人工约定，**尚无机械校验**） | `code/unity/Assets/**` 的资产（`.meta` / `.controller` / `.asset` / 场景）**只由这一台机生成与手调**。理由：手调成果入库要求 `.meta` GUID 稳定，多台机器各自手调资产则合并必然 GUID 冲突。**2026-09-12 补充**：原先的两份分叉拷贝已合并为一份（Linux 侧 WSL2 + Windows 侧 Editor 属同一台物理机，unity-cli 经 interop 直驱），该约束现在是"一台机一份拷贝"，不再有跨机面。文本（`design/` `data/` C# 源码与断言）不受此限 |

**提交前的底线**：`validate_cross_refs.py` 报 0 死链 + `dotnet test` 全绿。

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [项目规约](design/conventions/README.md), [设计总览](design/README.md), [协作指南](CONTRIBUTING.md), [数据说明](data/README.md)*
