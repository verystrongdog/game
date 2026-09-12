# Issue 流程：创建约束与需求分解

> 本仓库 **issue 的创建约束与需求分解规则**。上游是 grilling 讨论，下游是 [WORKFLOW.md](../../WORKFLOW.md) 的准入、执行与闭合判据。本文回答一件事：**一个需求怎么变成一组依赖有序、可以逐步实现、能被机械验收的 issue。**

> **来源**：2026-09-12 建立。借鉴 KEP 的 `kep.yaml` 元数据校验、Rust tracking issue 的步骤化 checklist、GitHub Issue Forms 的结构强制（见 [§八](#八来源与借鉴)），并按本仓**当前实际依赖**适配：四轴能力状态、`design → data → code → unity` 依赖方向、11 个校验器与 4 个 CI job、Unity 门禁本机 `NOT_AVAILABLE`、单线程约束。

## 目录

1. [一、本文管什么，不管什么](#一本文管什么不管什么)
2. [二、上游：讨论与导入门](#二上游讨论与导入门)
3. [三、分解算法](#三分解算法)
4. [四、一条 issue 的字段](#四一条-issue-的字段)
5. [五、依赖与门禁如何被机械判定](#五依赖与门禁如何被机械判定)
6. [六、伪分解反例](#六伪分解反例)
7. [七、创建通道](#七创建通道)
8. [八、来源与借鉴](#八来源与借鉴)

---

## 一、本文管什么，不管什么

**管**：一条需求如何被分解成 issue；一条 issue 被创建时必须带什么；创建动作本身怎么执行、怎么被校验。

**不管**（各自有唯一权威，本文不重复也不得覆盖）：

| 不管什么 | 权威 |
|---|---|
| issue 的**六种类型各是什么** | [WORKFLOW.md §三](../../WORKFLOW.md) |
| 状态模型（四轴 / must-prove / 状态必须绑定） | [WORKFLOW.md §二](../../WORKFLOW.md) |
| 阶段的两次闭合、阶段处置流程、问题差分 | [WORKFLOW.md §四/§五](../../WORKFLOW.md) |
| 每类问题的**解决证据判据** | [WORKFLOW.md §六](../../WORKFLOW.md) |
| 依赖方向与已知越界点 | [ARCHITECTURE.md](../../ARCHITECTURE.md) |
| 门禁的命令、判据、已知缺口 | [build-and-test.md](build-and-test.md) |
| 当前可玩切片与准入状态 | [PLAYABLE.md](../../PLAYABLE.md) |

**一条硬约束**：本文与上表冲突时以上表为准，并修本文。

### 1.1 本文不得变成仪式

本仓曾有一套十步 grilling 流程（2026-09-12 停用），它产出 47% 的仓库行数却只贡献 31% 的硬约束。**本约束体系不得重蹈该覆辙**，判据有两条，二者同时成立才允许某条规则留在本文：

1. **可机械判定**——它有校验器规则、有枚举、有可解析字段；或
2. **有具名消费时刻**——有人会在某个具体时刻读它来做决定（见 [§四](#四一条-issue-的字段) 的「消费时刻」列）。

只能回答"这样写比较规范"的规则，不进本文、不进模板。

## 二、上游：讨论与导入门

### 2.1 讨论阶段不建 issue

设计讨论（grilling 或任何顺手的方式）**不产生 issue**。理由：讨论的产物是**决策**，不是**任务**；决策的归属是 `design/` 正典与 [决策树](../decisions/README.md)，不是 issue 队列。

> 历史对照：旧 grilling 流程的 Step 2 是"先 `gh issue create -t "[Grilling] ..."` 再逐题追问"，122 个 issue 里 89 个带 `grilling` 标签。讨论记录留在 issue 里，导致结论与正典脱钩、issue 队列被非任务条目占据。该做法于 2026-09-12 随流程一并停用。

### 2.2 导入门

讨论收敛后，进入 issue 流程前必须过导入门。**输入契约**——收敛结论至少含以下四块，缺一块则不得导入：

| 块 | 内容 | 为什么必需 |
|---|---|---|
| **决策表** | 每条决策：结论 · 依据（`文件 §节`）· 状态（已定 / 推迟） | 分解的原料；依据缺失 → 无法核对是否与正典冲突 |
| **受影响面** | 按 设计 / 数据 / 代码 / 门禁 四类逐条列出 | 决定依赖图的边；漏一类就是隐藏依赖 |
| **推迟清单** | 明确不做的、以后做的 | 直接灌进每条 issue 的「明确排除」，防 scope 膨胀 |
| **未决问题** | 仍未定的问题 | 有未决问题时，**不得导入为 `Implementation`/`Task`**——只能导入为 `Experiment`（可行性未知）或 `RFC`（需 owner 决策） |

**门禁判据**（任一不满足 → 退回讨论，不导入）：

1. 涉及新数值参数的决策必须带来源（本仓硬约束：参数来源注释）
2. 决策**必须先落进 `design/`**。设计驱动代码：没有设计文档支撑的机制不实现（[项目规约 §一](../conventions/README.md)）
3. 决策与 `data/term_registry.json` 冲突的，先解决术语口径再导入

## 三、分解算法

输入：过门的收敛结论。输出：一组 issue 及其依赖边，排成**有序 frontier**（每步的前置都明确，同通道内串行）。七步，每步有可核对产物。

### Step 0 — 读现状（分解的事实基础）

分解不许凭记忆。四样必读，且都要读到具体状态：

| 读什么 | 取什么 |
|---|---|
| [PLAYABLE.md](../../PLAYABLE.md) | 当前是 `NO_AUTHORIZED_PLAYABLE` 还是 `AUTHORIZED_PLAYABLE: <id>` |
| `design/slices/<id>/slice.md` | 被消费能力的**四轴状态表**（哪些能力停在 `NONE`/`FAKE`/`ISOLATED`） |
| [`design/engineering/gates.json`](gates.json) | 哪些门禁**当前可用**、哪些不可用及其阻塞面 |
| 开放 issue 的 frontier | 已有哪些 `blocked-by` 边、当前 `in-progress` 是谁 |

### Step 1 — 抽能力增量

把每条决策翻译成**能力增量单元格**：`(能力, 轴, 从 → 到)`。轴与取值只用 [WORKFLOW.md §二](../../WORKFLOW.md) 的四轴枚举，不另造词。

| 例（真实取自 CP-01 切片） | 能力 | 轴 | 从 → 到 |
|---|---|---|---|
| 让 Unity 走真实 Core 而不是手抄常量 | Core → Unity 适配层 | Implementation | `FAKE` → `PARTIAL` |
| 同上 | Core → Unity 适配层 | Integration | `ISOLATED` → `CONNECTED` |
| 提交 Unity 工程资产身份 | Unity 资产身份 | Implementation | `NONE` → `PARTIAL` |

**翻不出单元格的决策不是实现任务**——它要么是设计决策（落 `design/` 即可，不建 issue），要么是还没想清楚（回讨论）。

### Step 2 — 建依赖图

三类边，方向不许自定：

| 边型 | 规则 | 出处 |
|---|---|---|
| **方向边** | `design/ → data/ → code/src/ → code/unity/`；反向边非法。例：数据契约 issue 不得依赖引擎 issue | [ARCHITECTURE.md §二](../../ARCHITECTURE.md) |
| **轴序边** | 同一能力上，`Design` 未到 `ACCEPTED` 不得声明 `Implementation` 迁移；`Implementation` 未到 `DONE_FOR_SLICE` 不得声明 `Integration: E2E` | [WORKFLOW.md §二](../../WORKFLOW.md) |
| **门禁边** | 要验收就必须跑门禁；门禁不可用 → 依赖不成立。Unity 门禁本机 `NOT_AVAILABLE`，因此**任何声称"实现并试玩 CP-01"的 issue 在本环境无法闭合**，必须改声明或标阻塞 | [build-and-test.md §三/§五](build-and-test.md) |

### Step 3 — 切分到原子

一条 issue 必须同时满足四条原子性判据。任一不满足 → 继续切。

| 判据 | 含义 | 反例 |
|---|---|---|
| **A1 单能力** | 声明的能力增量 ≤ 3 行，轴迁移 ≤ 4 个单元格 | "完成战斗系统" |
| **A2 独立可验证** | 至少一条门禁能给出**变化**：做之前失败/缺失，做之后通过。不是"顺便把 X 也做了" | "重构目录顺便补测试" |
| **A3 有具名消费方** | 产物被具名的下游消费：`#NN` / 切片 id / 证据文件；或显式声明 `终态` | "写一份说明文档"（没人消费） |
| **A4 可回滚** | `git revert` 该提交组能恢复上一状态；**不可回滚**的（数据迁移、大范围改名、删除）必须单独成 issue 并写明回滚方案 | "改数据格式 + 顺手改名" |

### Step 4 — 拓扑排序成单线程 frontier

按依赖边排序，输出有序 frontier。判据来自 [WORKFLOW.md §一](../../WORKFLOW.md)：同一时刻只有一个叶子 issue 处于 `in-progress`。

```
frontier = { i ∈ 开放 issue | 所有 blocked-by 已关闭 且 所有 requires 已满足 且 未被认领 }
```

要求：**frontier 里的每一条都必须能说清它属于哪条独立通道**（阶段闭合 / 数据权威 / 呈现 / 依赖可复现性……）。判据不是"数量必须为 1"，而是：

- 若**同一条通道**上出现多条同时可开工 → 说明切分没找到真实依赖，回 Step 2 找漏掉的边
- 若**不同通道**各有一条 → 合法。单线程约束管的是"同一时刻只推进一个主要成果"（[WORKFLOW.md §一](../../WORKFLOW.md)），不是"全仓只能有一件可做的事"
- **但语义独立 ≠ 可以并行**：还要过一道**文件相交检查**——两条就绪 issue 的「预期差分」文件集合若有交集，它们就不是真并行（改同一个文件，谁先落地都会让另一条的 diff 变成冲突），必须**串行**并在 frontier 里写明顺序。判据由 I13 机械给出

[backlog 分解示范](backlog-decomposition-2026-09-12.md) §四 就是后一种情形：5 条就绪项分属 4 条互不相干的通道。

### Step 5 — 绑定五件套

每条 issue 必须绑定（对应 [§四](#四一条-issue-的字段) 的必填项）：

1. **门禁**：将跑的 gate id 或脚本命令（必须存在于 [`gates.json`](gates.json)）
2. **验收标准**：每条独立可判，且写明"做之前是什么样"
3. **预期差分**：开工前登记允许的变化（[WORKFLOW.md §5.1](../../WORKFLOW.md) 的 `expected_delta`）
4. **回滚**：方式 + 演练结论
5. **消费方**：A3 的具名下游

### Step 6 — 过反例清单

逐条对照 [§六](#六伪分解反例)。**不与反例中的任何一条重合**才可提交创建。

### Step 7 — 机械校验并创建

```bash
python3 code/tools/validate_issues.py --file <临时草稿>   # 必须 exit 0
gh issue create --title "..." --body-file <临时草稿> --label type:task --label state:needs-triage
```

校验器规则见 [§五](#五依赖与门禁如何被机械判定)。创建通道见 [§七](#七创建通道)。

## 四、一条 issue 的字段

字段即 Issue Forms 的必填项，也是校验器的检查对象。**「消费时刻」列是准入条件**：写不出消费时刻的字段，删。

**正文中的顺序**：`类型` 在最前（表单把单选 dropdown 置于 body 首位，使网页通道也渲染出 `### 类型` 章节），其后按本表顺序，类型专属字段追加在最后（[§4.2](#42-按类型追加必填)）。校验器只判存在性、不判顺序，但两条通道的正文必须**逐字一致**。

### 4.1 所有类型必填

| 字段（表单标签） | 内容 | 消费时刻（谁在何时读它、不填会怎样） | 机器可判 |
|---|---|---|---|
| **类型** | `Task` / `Implementation` / `Bug` / `Experiment` / `RFC` / `Slice` 六选一 | 创建时选模板；关闭时据 [WORKFLOW.md §六](../../WORKFLOW.md) 选证据标准。不填 → 无法判定"什么算解决" | ✅ 枚举 |
| **动机** | 这件事解决什么问题、为什么是现在、不做会怎样 | triage 时判断该不该做（没有动机就无法拒绝）；关闭时判断"是否真的解决了那个问题"，而不是只看"代码写完" | ⚠️ 非空可判，质量人工 |
| **能力增量** | 表格：能力 · 轴 · 从 → 到 | 关闭时据此更新 `slice.md` 的四轴表；下一次分解时据此判断前置是否满足 | ✅ 枚举 + 设计状态 |
| **依赖** | `key: value` 逐行：`blocked-by` · `consumed-by` · `requires` | 分解时拓扑排序；开工前算 frontier；CI 快照校验。不填 → 单线程约束失效 | ✅ 引用存在性 |
| **门禁** | 将跑的 gate id 或脚本命令，一行一条；`RFC`/`Experiment` 可写 `none`（它们的判据是决策/结论，不是机器门禁） | 开工前确认本机可跑；关闭时逐条执行并把退出码写进证据 | ✅ 查 `gates.json` |
| **预期差分** | 允许发生什么变化，以及**预期不变**的是什么。允许变化的文件必须**逐条写出仓库相对路径**（不写「相关文档」这类指代）——并行就绪时校验器按这份文件集合判相交（I13） | 阶段开始时登记；退出时算 `new_finding = after − mapped(before) − expected_delta`。事后补登 → 该阶段判据失效 | ✅ 文件集合（I13） |
| **验收标准** | checklist，2–8 条，每条独立可判并写明改动前的状态 | 关闭时逐条对照；[WORKFLOW.md §六](../../WORKFLOW.md) 明令"代码写完/文档写完/CI 表面绿色"都不能单独作为关闭证据 | ⚠️ 条数可判，质量人工 |
| **明确排除** | 本 issue 不做的事（含推迟清单里相关的条目） | triage 与评审时防 scope 膨胀 | ⚠️ 非空可判 |
| **回滚** | 回滚方式；不可回滚者写明为何 | 阶段退出时做回滚演练 | ⚠️ 非空可判 |

### 4.1.1 三个受控取值域

校验器按这三套取值域判定，**不得自造**。另外两件事由**标签**承载（正文里没有对应字段）：**类型**用 `type:*` 标签（与正文 `### 类型` 交叉比对，不一致即失败），**状态**用 `state:*` 标签（`needs-triage` / `ready-for-agent` / `ready-for-human` / `in-progress` / `blocked` / `wontfix`）——单线程判据（I11）与阻塞判据（I7）都以标签为准。

| 域 | 合法取值 |
|---|---|
| `依赖:` 的 key | `blocked-by`（必须已关闭的 `#NN`，或 `无`）· `consumed-by` · `requires`（或 `无`） |
| `consumed-by` 的值 | `#NN`（下游 issue）· `<切片 id>`（切片合同）· `证据:<路径>`（证据文件）· `门禁:<gate id>`（某门禁消费它）· `待建:<描述>`（下游尚未创建）· `终态`（无下游，且写明为何） |
| `requires` 的值 | `gate:<gate id>` · `PLAYABLE:<状态>` · `能力:<能力名>=<轴>:<状态>` · `owner:<决策项>` |

**能力名的分隔符约束**：能力名逐字取自 `design/slices/<id>/slice.md` §二 的四轴表行名，**不得含 `、` `,` `，` `;` `；`**——那五个字符是多个取值之间的分隔符，出现在名字里会把一个能力切成两段（实测：`能力:含、顿号的名字=Design:ACCEPTED` 报"不符合格式"）。含则**先改切片表的行名**，不要在该格式里塞转义。

**实测不受影响**（不要为此加限制）：中文、空格、`→`、以及 `=` 与 `:` 都安全——解析以末尾的 `=<轴>:<状态>` 为锚回溯切分，故 `能力:含=等号的名字=Design:ACCEPTED` 与 `能力:含:冒号的名字=Design:ACCEPTED` 都能正确解析（2026-09-12 实测，见 [§5.3](#53-校验器的覆盖边界诚实清单) 同源的校验器）。

**四个例外情形**（真实 backlog 逼出来的，不是假想）：

1. **issue 交付的是新门禁本身**——`门禁:` 可以引用一个**尚不存在、由本 issue 交付**的脚本，但必须在「交付物」中明列，且验收标准要包含"创建后登记进 [`gates.json`](gates.json)"。否则就是拿不存在的门禁冒充可闭合（[§六](#六伪分解反例) R4 的变体）。
2. **`RFC` / `Experiment` 无机器门禁**——写 `门禁: none`，但验收标准必须写明"谁在何处记录该决策/结论"（`design/decisions/` 条目或证据文件）。
3. **下游尚未创建**——`consumed-by: 待建:<描述>`。这是真实情形的诚实写法：消费方在候选队列里（[WORKFLOW.md §一](../../WORKFLOW.md) 不允许顺手把非阻塞项都建出来），此刻没有编号可指。校验器对此出**警告**而非失败，因为"产物暂无具名消费者"正是 triage 需要看到的信号（A3 的弱化形态）。
4. **正文必须命名一个尚不存在的产物**——例如"补齐 `NuGet` 的 `packages.lock.json`"或"补齐缺失的外部数据许可登记"，那个路径此刻本就不存在，而它是 issue 的**主题**，不是隐藏依赖。判据：**同一行显式标注**了它尚不存在（含"缺失 / 不存在 / 尚未 / 待建 / 将新增 / 新建 / 0 个"等标记）→ 校验器 I8 降为**警告**；未标注 → 仍按死引用失败。

   > 这条例外的边界很重要：它只放宽"命名缺失物"，不放宽"引用不存在的**依赖**"。后者照旧失败。

### 4.2 按类型追加必填

**顺序是契约的一部分**：先 9 个必填字段（按 §4.1 表中的顺序），类型专属字段追加在其后。Issue Forms 与 CLI 两条通道产出的正文结构必须逐字一致——否则校验器（按 `### 标题` 解析）会在两条通道上产生不同判定。

| 类型 | 追加字段 | 消费时刻 |
|---|---|---|
| `Bug` | **复现**（稳定失败的步骤/命令）· **期望 vs 实际** | 关闭判据要求"修复前稳定失败、修复后通过"——复现就是那句话的机器形态 |
| `Experiment` | **假设** · **判定标准**（支持/否定/证据不足各是什么样）· **原型去向**（删除 / 进正典 / 归档） | 关闭判据要求"得到结论 + 原型去向明确"。本仓"walking skeleton"与"spike"必须分清：前者是永久代码带回归测试，后者用完即弃——混用会让实验代码进主干 |
| `RFC` | **选项**（≥2 个，含代价）· **owner 决策**（待决/已决 + 结论） | 关闭判据要求"真实选项、代价、回滚与 owner 决策完成" |
| `Slice` | **玩家路径** · **must-prove**（逐条） | 切片合同在 `design/slices/<id>/slice.md`，issue 只引用并复述 must-prove；完成判据是"玩家能从入口到出口且有试玩证据" |
| `Task` / `Implementation` | **交付物** · **接入位置**（产物接进哪个位置，不是"写完了"） | 关闭判据要求"交付物存在 + 接入目标位置 + 直接验证与阶段回归通过" |

### 4.3 引用格式：契约面 vs 定位面

本仓既有两条规则在这里交锋：[AGENT-BRIEF.md](../../.agents/skills/triage/AGENT-BRIEF.md) 要求"不写文件路径与行号"（它们会过期），而本仓要求"引用即读取"、参数必须带来源。区分如下：

| 面 | 允许 | 理由 |
|---|---|---|
| **契约面**（稳定） | `design/rules/核心机制.md` §4（段引用）· 能力名 · 类型名 · gate id | 段引用是本仓推荐格式（[写作与引用规范 §一](../conventions/writing-and-references.md)）；且**存在性可被校验** → 引用即读取变成机械判据 |
| **定位面**（易变） | ❌ 代码行号 `X.cs:42` · ❌ "打开 A 文件改第 N 行"式步骤 · ❌ 临时本地路径 | 行号随编辑漂移；过程化步骤会随实现结构变化而失效 |

**判据**：issue 写的是**行为契约**（系统应当怎样），不是**操作步骤**（你该敲哪个文件）。校验器对正文中的行号式引用出警告（见 [§五](#五依赖与门禁如何被机械判定) I9）。

## 五、依赖与门禁如何被机械判定

### 5.1 门禁能力表

门禁的**机器可读清单**是 [`design/engineering/gates.json`](gates.json)：gate id、命令、CI job、本机可用性、不可用时阻塞什么。它是 issue 里 `门禁:` 字段的引用目标，也是校验器 I6 的判定依据。

散文权威仍在 [build-and-test.md](build-and-test.md)——本表只是它的机器形态。**两侧不一致时以 build-and-test.md 为准**，并修 `gates.json`。

### 5.2 校验器规则表

`code/tools/validate_issues.py` 的规则。两种模式：`--file <草稿>`（创建前门禁）、`--from-github`（CI 快照，校验真相源本身）。

| id | 规则 | 判定方式 | 机器可判 |
|---|---|---|---|
| I1 | 必填章节齐全（按 [§4.1](#41-所有类型必填)/[§4.2](#42-按类型追加必填)） | 章节标题存在且非空 | ✅ |
| I2 | 类型 ∈ 六种枚举 | 值比对 | ✅ |
| I3 | 能力轴 ∈ 四轴枚举；状态 ∈ 各轴合法值 | 值比对 | ✅ |
| I4 | `Design` 未 `ACCEPTED` 的能力，不得声明 `Implementation` 迁移；切片表中 `Design` 为 `—`（无设计面）的能力按不适用处理 | 跨 issue + `design/` 状态 | ✅ |
| I5 | `blocked-by` / `consumed-by` 引用的 issue 编号存在；`blocked-by` 缺失或指向不存在的编号 → 失败，`consumed-by: 待建:<描述>` → 警告（[§4.1.1](#411-三个受控取值域) 例外 3） | 快照内编号集合 | ✅ |
| I6 | 声明的 gate id 存在于 `gates.json`；若该 gate **当前不可用**，本 issue 不得标 `state:ready-for-agent`。**例外**：issue 自己交付新门禁时（[§4.1.1](#411-三个受控取值域) 例外 1），校验器只要求「交付物」里明列了它 | 查表 | ✅ |
| I7 | `blocked-by` 未全部关闭时，本 issue 不得处于 `state:in-progress` | 状态 + 引用状态 | ✅ |
| I8 | 引用的脚本/证据/文档路径存在；段引用 `§N` 在目标文件中存在（段不存在为警告，文件不存在为失败）。豁免：「交付物」/「预期差分」两节（按定义描述未存在的产物）+ 显式标注缺失的行（[§4.1.1](#411-三个受控取值域) 例外 4） | 文件系统 + 标题扫描 | ✅ |
| I9 | 正文**不得**出现 `文件:行号` 式脆弱引用（[§4.3](#43-引用格式契约面-vs-定位面)） | 正则 | ✅（警告） |
| I10 | 正文不得引用 `design/archive/trash/`、不得使用 `term_registry.json` 中 `deprecated` 的术语 | 复用既有判据 | ✅ |
| I11 | 全仓同时 `in-progress` 的 issue ≤ 1（[WORKFLOW.md §一](../../WORKFLOW.md)） | 快照统计 | ✅ |
| I12 | 验收标准 2–8 条；能力增量 ≤ 3 行；门禁 ≥ 1 条（`门禁: none` 仅限 `RFC`/`Experiment`） | 计数 | ✅ |
| I13 | 并行就绪（`blocked-by` 全部已关闭或为空）的多条 issue，其「预期差分」声明的文件路径集合不得相交；相交 → 警告并指出共享文件（须串行） | 集合相交 | ✅（警告） |

**机器判不了的部分老实标出来**（模板只能改变形状，不能改变判断）：验收标准是否**充分**、依赖影响评估是否**诚实**、预期差分是否**真的**覆盖了变化、"单能力"是否切得**合理**。这些由 owner 在 triage 时判断。

### 5.3 校验器的覆盖边界（诚实清单）

规则能判不等于判得全。以下边界如实列出，避免把"校验器绿了"误读成"契约被完整执行"：

| 规则 | 覆盖边界 |
|---|---|
| I5 | 取值域（§4.1.1）在两种模式下都判；**引用存在性**需要快照。`待建:<描述>` 与 `终态（…）` 按定义携带自由文本，其中的顿号/逗号不作分隔符 |
| I8 | 只查**反引号内**与 **markdown 链接目标**中带已知顶层前缀（`design/ code/ data/ reference/ .github/ .agents/`）的路径。散文裸路径、`../` 引用、含 `...` 的省略写法**不查**；``` 代码块内跳过 |
| I9 | 会查代码块内——粘贴的 stack trace 也会出警告，不做豁免 |
| I10 | 不做「⚠️ 已废弃」行豁免（比 `validate_trash_isolation.py` 严），故警告偏多；只覆盖 `term_registry.json` 里有替代说明的 deprecated 条目 |
| I12 | 计数的列表项接受 `- [ ]` / `-` / `*` / `+` / 有序列表 |
| I6 | 无法解析成 gate id 或命令的**散文化**门禁行给警告而非失败（否则"本机不可用，替代验证见…"会误报） |
| I4 | 只在 `design/slices/*/slice.md` 的四轴表里匹配能力名；匹配不到只出警告（工程侧能力本就不在切片表里） |
| I13 | 依赖「预期差分」写出显式文件路径；只认文件不认目录；裸文件名按唯一基名解析 |
| — | `--from-github` 默认 `--limit 200`，触顶时告警但**不自动翻页**；未使用 gh 原生依赖边（本机 2.4.0 限制，见 [§7.3](#73-本机工具限制实测)）；无 `--format json` |

**这些边界不是"以后再说"**：它们决定了哪些契约条款实际上只靠人工把关。改动校验器时必须同步改本表。

## 六、伪分解反例

| # | 反例 | 为什么错 | 正确做法 |
|---|---|---|---|
| R1 | **按文件拆**："改 `DemoSolver.cs`" / "改 `GameDataLoader.cs`" | 文件不是行为，重构一改名 issue 即失效；且无法验收 | 按能力增量拆："Core→Unity 适配层 `FAKE→PARTIAL`" |
| R2 | **按层横切**："先写全部 schema，再写全部 loader" | 中间态不可验收，第一层做完时系统行为毫无变化（A2 违反） | 纵切：一条 issue 打通一条最小端到端路径（walking skeleton） |
| R3 | **巨型 issue**："实现 CP-01 切片" | 无门禁能在中间给出判定；失败时无法定位 | 按 must-prove 与阻塞项拆成依赖有序的多条 |
| R4 | **无门禁 issue**："整理文档" / "调研一下" | 没有变化的门禁，做没做不知道 | 若真是调研 → `Experiment`，必须写判定标准与原型去向 |
| R5 | **依赖倒挂**：`code/` 的 issue 阻塞 `design/` 的 issue | 违反 [ARCHITECTURE.md §二](../../ARCHITECTURE.md) 的依赖方向 | 反转：设计先落 `design/`，代码消费它 |
| R6 | **隐藏依赖**：正文引用了尚未存在的能力/文件，却没写进 `blocked-by` | 开工才发现等待，单线程约束失效 | 每条前置都写进 `依赖:` 的对应 key |
| R7 | **前置未准入**：开"实现并试玩 CP-01"的 issue，而 [PLAYABLE.md](../../PLAYABLE.md) 仍是 `NO_AUTHORIZED_PLAYABLE` | 未准入期间不得新增正式玩家行为；该 issue 不可能合法闭合 | 要么先解决准入（owner 决策，`RFC`），要么把 issue 声明为被阻塞 |
| R8 | **门禁不可用却声称可闭合**：issue 要求 Unity 验证，而本机门禁 `NOT_AVAILABLE` | 产出的 issue 无法验收（[build-and-test.md §三](build-and-test.md)：未运行不是通过） | 改声明为可本机验证的部分，或标阻塞并写明替代验证方式 |
| R9 | **事后补登预期差分**：开工后才写"我打算改这些" | [WORKFLOW.md §5.1](../../WORKFLOW.md) 明令"本阶段产生的新问题不得事后倒填为已知债务" | 创建时即登记 |

## 七、创建通道

### 7.1 三条通道

| 通道 | 形态 | 强制力 |
|---|---|---|
| **A 网页 Issue Forms** | `.github/ISSUE_TEMPLATE/*.yml`（按六类型各一份） | GitHub 侧强制必填；缺项提交不了 |
| **B CLI** | `validate_issues.py --file <草稿>` → `gh issue create --body-file <草稿>` | 校验器门禁；草稿是**临时文件，不入库** |
| **C CI 快照** | `validate_issues.py --from-github` | 校验**真相源本身**：开放 issue 的字段、依赖边与单线程约束 |

**真相源 = GitHub issue**。仓库内不留 issue 副本：草稿创建后即弃；需要留存的（历史归档、阶段证据）走既有导出与证据机制。

### 7.2 授权

[WORKFLOW.md §一](../../WORKFLOW.md) 规定"外部标签同步、Issue 编辑与自动化**不属于本流程的隐式权限**"。据此，**创建/编辑 issue 需要 owner 显式授权**。

> **本次授权（2026-09-12）**：owner 授权 agent 在通过校验器门禁的前提下，**直接创建 issue 并施加类型/状态标签**。授权范围仅限创建与标签；关闭 issue、修改历史 issue、删除评论仍需逐次确认。

### 7.3 本机工具限制（实测）

| 限制 | 影响 | 处置 |
|---|---|---|
| 本机 `gh` 为 **2.4.0（2022-03）**，`issue create` 无 `--blocked-by` / `--parent` | GitHub 原生依赖边无法用 CLI 建立 | 依赖写在正文 `依赖:` 字段，由校验器解析（I5/I7）。**升级 `gh` 后可迁移到原生依赖边**，字段格式保持不变 |
| GitHub tasklist `- [ ] #123` 已退役（官方文档原文 "Tasklist blocks are retired"，见 [2025-02-18 changelog](https://github.blog/changelog/2025-02-18-github-issues-projects-february-18th-update/)） | 旧式勾选依赖不再有语义保证 | 不用 tasklist 表达依赖 |

### 7.4 存量异常（不追溯）

仓库现存 16 个开放 issue 属于 grilling 时代，与本文不兼容：标签为 `维度:*` / `ready-for-agent`（与 [WORKFLOW.md §三](../../WORKFLOW.md) 的类型词汇不符），正文引用 `.scratch/` 下的路径（该目录已在重构中移出仓库）。**本文只约束新建 issue，不追溯处置存量。** 是否关闭/重写由 owner 逐条决定。

## 八、来源与借鉴

| 借鉴对象 | 借了什么 | 本仓适配 |
|---|---|---|
| KEP `kep.yaml` + `verify-kep-metadata.sh`（Kubernetes） | 把提案元数据枚举化，用 CI 脚本卡关（`go test ./test/metadata_test.go` 断言校验错误为空） | 换成 [`gates.json`](gates.json) + `validate_issues.py`，接进既有 11 校验器与 CI 的 `docs-integrity` job |
| Rust tracking issue 模板 | 步骤化 checklist（每步是一个可交付 PR）+ `Unresolved Questions` | "未决问题"成为导入门的第四块（[§2.2](#22-导入门)）：有未决问题不许导入 `Implementation` |
| Rust RFC 模板 | `Motivation` / `Guide-level` / `Reference-level` / `Alternatives` / `Future possibilities` | 决策表 + 受影响面（[§2.2](#22-导入门)）；`Future possibilities` → 「明确排除」 |
| GitHub Issue Forms | 结构强制：必填项、枚举下拉、校验 | 六类型各一份表单；标签名与校验器的章节名逐字对齐（表单渲染出的 `### 标题` 即校验器的解析锚点） |
| GitHub issue dependencies / sub-issues | 关系边可读可查 | 受本机 `gh` 版本限制，暂以正文 `依赖:` 字段承载 |
| INVEST · vertical slicing · walking skeleton vs spike | **判断依据**，不是模板字段——成熟仓库里几乎不把 INVEST 写进模板（GitHub 不校验） | 落成 [§三](#三分解算法) 的 A1–A4 原子性判据与 R1–R9 反例 |
| KEP Graduation Criteria（Alpha/Beta/GA 分阶段门槛） | 用分阶段可观察条件替代"做完了" | 本仓已有同构物：四轴状态 + must-prove（[WORKFLOW.md §二](../../WORKFLOW.md)）——**不新造，直接对接** |
| 本仓既有机制 | 四轴状态（[slice.md](../slices/CP-01-ward-1f/slice.md) §二）· 依赖方向（[ARCHITECTURE.md §二](../../ARCHITECTURE.md)）· 预期差分与问题差分（[WORKFLOW.md §5.1](../../WORKFLOW.md)）· 门禁清单（[build-and-test.md](build-and-test.md)） | 全部复用，零新造概念 |

详细调研记录（含逐条英文原文摘录与出处 URL）：[需求分解与 Agent-Issue 规范文献综述](../../reference/literature/需求分解与Agent-Issue规范-文献综述.md)。

### 8.1 未采纳的候选字段（以及为什么）

调研整理出 36 个可借用的字段。**不采纳的也要记下来**——否则下一个人会把它们重新加回来，而每次加都要过一次 [§1.1](#11-本文不得变成仪式) 的两条判据。

| 候选字段 | 出处 | 为什么不采纳 |
|---|---|---|
| `dependency_impact`（依赖挂掉/降级对本特性的影响） | KEP PRR `### Dependencies` | 本仓的依赖不是常驻服务，"挂掉"对应的是前置 issue 未关闭或门禁不可用——已由 `blocked-by` + 门禁可用性（I6/I7）**机械**表达。再加一段自由文本，没有具名消费时刻 |
| `steps`（一个 issue 内多步 checklist） | Rust tracking issue | 未采纳为**字段**，改为**分解算法**：Rust 把多步放进一个 tracking issue，本仓要求每条 issue 独立闭合、独立证据（[WORKFLOW.md §六](../../WORKFLOW.md)），故步骤**外化**为带 `blocked-by` 边的多条 issue（[§三 Step 3–4](#三分解算法)） |
| `feature_gates{name,components}` / `disable_supported` / `milestone{alpha,beta,stable}` | `kep.yaml` | 那套是灰度发布与版本火车的产物；本仓无发布路径、无 feature flag、无 N-1 升级。成熟度由四轴状态 + must-prove 表达 |
| `monitoring_requirements`（metrics / SLI / SLO） | KEP PRR | 无线上服务，无可观测性要求 |
| `upgrade_downgrade_strategy` / `version_skew_strategy` | KEP / nova | 单人游戏原型不存在滚动升级与混版本运行 |
| `implementation_history`（日期-事件时间线） | KEP | 不采纳为字段：GitHub issue 自身的创建/评论/关闭时间线就是它，另写一份是第二个真相源 |
| `tracking_issue`（设计→实现→稳定的枢纽链接） | rust-project-goals | 本仓的枢纽已是 `slice.md` 的四轴表 + `consumed-by` 边；再加索引会形成两条互相追不上的线 |
| `design_axioms`（可判定的设计约束） | rust-project-goals | 正典级禁令在 [项目规约 §二](../conventions/README.md) 与 `term_registry.json`；issue 级禁令由「明确排除」承担。它们已各有唯一权威，issue 不该是第二处 |
| `ownership_and_team_asks`（Task / Owner / Notes） | rust-project-goals | 单人仓库，owner 即唯一负责人；需要多人时再加 |
| `user_stories` / `backwards_compat_policy` / `source·abi_compatibility` | KEP / PEP 387 / swift-evolution | 无外部 API 消费者、无兼容性承诺。`Slice` 类型的「玩家路径」承担了"具体使用场景"那一项 |
| `Timebox`（spike 的时间盒） | INVEST `Estimable`；Cockburn 的 spike | **暂缓，不是否决**——本仓尚无 `Experiment` 类型的 issue在跑，此刻加字段没有消费时刻。触发条件：**第一条 `Experiment` issue 创建时**，由它决定时间盒是进模板字段、还是留在正文里 |
| `ready-for-human` 的委派判据（不该交给 agent 的清单） | GitHub Copilot 最佳实践的反向清单 | 暂缓：本仓的"不能交给 agent"已被更硬的机制覆盖——需 owner 决策的走 `RFC`，需 Unity Editor 的按 `gate:unity` 判 `state:blocked`（I6）。人工清单会与这两者重复且更难维护 |

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [WORKFLOW.md](../../WORKFLOW.md), [ARCHITECTURE.md](../../ARCHITECTURE.md), [构建与测试](build-and-test.md), [门禁能力表](gates.json), [工程文档索引](README.md), [项目规约](../conventions/README.md)*
