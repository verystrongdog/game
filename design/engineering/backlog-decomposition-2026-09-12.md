# Backlog 分解示范 — 2026-09-12

> 按 [issue-process.md](issue-process.md) 的七步算法，对重构后仓库的**当前 backlog** 做的一次实际分解。目的有两个：验证约束体系可执行；产出第一批可按依赖顺序实现的 issue。
>
> **输入的诚实说明**：本次输入**不是一次新的 grilling 讨论**，而是已登记的未闭合项——证据文件与缺口表本身就是一份已收敛的结论，[§2.2 导入门](issue-process.md) 的四块由它们提供（见 §一）。凡导入门要求而现有记录没有的（例如"未决问题"），在本文件中显式补记，不由本文发明。

## 目录

1. [一、导入门：输入四块](#一导入门输入四块)
2. [二、Step 0：现状（读到的状态）](#二step-0现状读到的状态)
3. [三、Step 1–2：能力增量与依赖图](#三step-12能力增量与依赖图)
4. [四、Step 3–4：切分与有序 frontier](#四step-34切分与有序-frontier)
5. [五、Step 5–7：绑定、过反例、创建](#五step-57绑定过反例创建)
6. [六、候选队列（不建 issue 的项及其理由）](#六候选队列不建-issue-的项及其理由)
7. [七、本次分解暴露的问题（诚实清单）](#七本次分解暴露的问题诚实清单)

---

## 一、导入门：输入四块

| 块 | 本次来源 |
|---|---|
| **决策表** | 阶段证据的已闭合/未闭合项（[P4a](evidence/P4a-2026-09-12.md)、[P4c](evidence/P4c-2026-09-12.md)、[evidence/README.md](evidence/README.md) 的"未闭合项"列）· 已知缺口（[build-and-test.md §五](build-and-test.md)、[external-sources.md §二](../../data/connectivity/external-sources.md)）· 已裁定决策（[REFACTOR-PLAN.md](../../REFACTOR-PLAN.md) 的 D10/§九/§十） |
| **受影响面** | 设计：`ARCHITECTURE.md` §三/§五、`README.md`、`slice.md` §二（计数口径）· 数据：`data/connectivity/*.json`（重算与否）· 代码：`code/tools/gen_modulation_ceiling.py`、`code/src/` 依赖锁 · 门禁：`engine`（本机可用）、`unity`（本机不可用） |
| **推迟清单** | 不做 Blender 工具纳入 CI（[build-and-test.md §5.1](build-and-test.md)）· 不做 sim 产物治理 · 不重构 `code/unity/` 资产组织（[REFACTOR-PLAN.md §九](../../REFACTOR-PLAN.md)） |
| **未决问题** | ① **Q6b**：桥接范围——子集桥接（4 文件 + `DamageCalculator.cs` 1 处引擎改动）vs 全量引擎重构（71 处/22 文件），见 [决策树 06 §D6](../decisions/06-numbered-disease-and-presentation.md) ② **hansen2024 是否真正接入**（会改 836 个数值，见 [external-sources.md §二](../../data/connectivity/external-sources.md) 缺口 1）③ **CP-01 是否准入**（[PLAYABLE.md](../../PLAYABLE.md) 仍为 `NO_AUTHORIZED_PLAYABLE`） |

**门禁判据核对**：三条未决问题都不涉及新数值参数、且都已有正典位置，故不退回讨论；但按 [issue-process.md §2.2](issue-process.md)，**有未决问题的只能导入为 `RFC`**——本文档第 ③ 条（CP-01 准入）连 issue 都不建（见 §六）。

## 二、Step 0：现状（读到的状态）

| 读什么 | 读到的 |
|---|---|
| [PLAYABLE.md](../../PLAYABLE.md) | `NO_AUTHORIZED_PLAYABLE`——未准入期间**不得新增正式玩家行为** |
| [slice.md](../slices/CP-01-ward-1f/slice.md) §二 | 结算与资源逻辑 `ACCEPTED`/`DONE_FOR_SLICE`（Console `E2E`）；**Core→Unity 适配层 `FAKE`**、HUD `NONE`、探索接敌与结束条件 `UNRESOLVED`——呈现侧几乎全停在 `ISOLATED` |
| [gates.json](gates.json) | 可用：`docs-integrity` `clean-checkout` `fixture-index` `engine` `cross-language` `issues`。**不可用：`unity`**（无 Editor）→ 阻塞 P4b / P4d / P5 |
| 开放 issue 的 frontier | 16 个存量 issue（grilling 时代），标签为 `维度:*`、正文引用已移出仓库的 `.scratch/` 路径。按 [issue-process.md §7.4](issue-process.md) **不追溯**，故不进本次依赖图 |
| 实测基线 | `DOTNET_ROLL_FORWARD=Major dotnet test …` → **416 passed / 0 failed**（2026-09-12，本机）；`run_all_checks.py` → 11/11 校验器退出码 0 |

## 三、Step 1–2：能力增量与依赖图

### 3.1 能力增量

| issue | 能力 | 轴 | 从 → 到 |
|---|---|---|---|
| **I1** #128 | 阶段退出门禁（P4a 回滚演练） | Health | `UNKNOWN` → `PASS` |
| **I2** #129 | 干净检出可复现性（依赖锁定） | Health | `UNKNOWN` → `PASS` |
| **I3** #130 | 正典一致性（测试计数口径） | Health | `REGRESSED` → `PASS` |
| **I4** #131 | 构建文档一致性（roll-forward 口径） | Health | `REGRESSED` → `PASS` |
| **I5** #134 | 链路调制上限生成链 | Integration | `ISOLATED` → `CONNECTED` |
| **I6** #132 | 链路调制上限的数值权威 | Design | `UNRESOLVED` → `ACCEPTED` |
| **I7** #133 | 链路调制上限的数值权威 | Implementation / Integration | `NONE` → `PARTIAL` / `ISOLATED` → `CONNECTED` |
| **I8** #135 | Core → Unity 适配层 | Design | `UNRESOLVED` → `ACCEPTED` |
| **I9** #136 | Unity 资产身份 | Implementation | `NONE` → `PARTIAL` |

> I1–I4 的能力名不在 [slice.md §二](../slices/CP-01-ward-1f/slice.md) 的表里——它们是**工程侧能力**，不是玩家可观察能力。校验器按 [issue-process.md §5.2](issue-process.md) I4 对这类只出警告（`Design=—` 视为"无设计面"，「未登记」视为"无法判定"），不误判为失败。

### 3.2 依赖图

```
   I6 RFC: hansen2024 接入裁定 (#132) ──► I7 真正接入并重算 (#133)          I5 生成器输出解耦 (#134) ──► I7
   I8 RFC: Q6b 桥接范围 (#135) ────────► [P4d 接缝]（候选队列）──┐
   I9 Unity 资产身份 (#136)  🚫 gate:unity 不可用 ──────────────┴──► [P5 实现与试玩]（候选队列）

   I1 (#128)   I2 (#129)   I3 (#130)   I4 (#131)     ← 四条彼此独立，均不被阻塞
```

**方向边核对**（[ARCHITECTURE.md §二](../../ARCHITECTURE.md)）：I6/I7 属 `data/` 侧（生成链 → 数据），不依赖任何 `code/` 侧 issue ✅。I5 属 `code/tools/`（生成器），不依赖 `data/` 的数值裁定 ✅——这正是把它从 I7 切出来的理由。

## 四、Step 3–4：切分与有序 frontier

### 4.1 原子性判据核对（A1–A4）

| issue | A1 单能力 | A2 独立可验证 | A3 具名消费方 | A4 可回滚 |
|---|---|---|---|---|
| I1 #128 | ✅ 1 行 | ✅ 演练前后 `docs-integrity` + `engine` 判定不同 | 证据:P4a | ✅ 演练不留变更 |
| I2 #129 | ✅ 1 行 | ✅ 干净检出 restore 由失败变通过 | 门禁:engine | ✅ 删锁文件即恢复 |
| I3 #130 | ✅ 1 行 | ✅ 改动前实测 416 与文档 353 不符 | 门禁:engine | ✅ 文档改动 |
| I4 #131 | ✅ 1 行 | ✅ 两个取值实跑，只有一个成立 | 门禁:engine | ✅ 文档改动 |
| I5 #134 | ✅ 1 行 | ✅ 加"只写 MD"路径后 JSON 哈希不变 | #133 | ✅ 脚本改动 |
| I6 #132 | ✅ 1 行 | ✅ `门禁: none`，判据是 owner 决策落决策树 | #133 | — 决策不可回滚，故单独成 issue（A4 要求） |
| I7 #133 | ✅ 2 行 | ✅ 生成器读数与数据集文件一致 | 终态 | ⚠️ **不可回滚**：836 个数值会变 → 单独成 issue 并写明备份前提 |
| I8 #135 | ✅ 1 行 | ✅ `门禁: none`，判据同 I6 | 待建:P4d 接缝 | — 决策不可回滚 |
| I9 #136 | ✅ 1 行 | ❌ 本机 `gate:unity` 不可用 → **标 `state:blocked`**，不冒充可闭合 | 待建:P5 | ✅ 提交资产可 revert（注意 GUID） |

### 4.2 有序 frontier

| 就绪 | issue | 通道 | 依赖 |
|---|---|---|---|
| ✅ | **I1 #128** P4a 回滚演练实测 | 阶段闭合 | 无 |
| ✅ | **I2 #129** NuGet 依赖锁定 | 依赖可复现性 | 无 |
| ✅ | **I3 #130** 测试计数口径 | 正典一致性 | 无 |
| ✅ | **I4 #131** roll-forward 口径 | 正典一致性 | 无 |
| ✅ | **I5 #134** 生成器输出解耦 | 生成链 | 无 |
| 🗳️ | **I6 #132** RFC: hansen2024 接入裁定 | 决策 | 无（`requires: owner:…`） |
| 🗳️ | **I8 #135** RFC: Q6b 桥接范围 | 决策 | 无 |
| 🚫 | **I7 #133** 真正接入并重算 | 生成链 | `blocked-by: #132` |
| 🚫 | **I9 #136** Unity 资产身份 | 呈现 | `requires: gate:unity`（不可用） |

5 条工程项同时就绪，看似违反单线程。按 [issue-process.md §三 Step 4](issue-process.md) 的判据：它们**分属四条互不相干的通道**（阶段闭合 / 依赖可复现性 / 正典一致性 / 生成链），两两之间既无 `blocked-by` 边也无共同消费方——是四条独立通道各有一条就绪项，不是被拆错的一条。若 owner 要严格串行，顺序即 I1 → I2 → I3 → I4 → I5。

## 五、Step 5–7：绑定、过反例、创建

### 5.1 创建结果

| issue | 标题 | 类型 | 状态标签 | 门禁 |
|---|---|---|---|---|
| **#128** | [Task] P4a 回滚演练实测——补齐阶段退出门禁 | `type:task` | `state:needs-triage` | `docs-integrity` · `engine` |
| **#129** | [Task] NuGet 依赖锁定——提交 packages.lock.json | `type:task` | `state:needs-triage` | `engine` · `clean-checkout` |
| **#130** | [Bug] 测试计数口径不一致（353 vs 416） | `type:bug` | `state:needs-triage` | `engine` |
| **#131** | [Bug] DOTNET_ROLL_FORWARD 口径不一致（Major vs LatestMajor） | `type:bug` | `state:needs-triage` | `engine` |
| **#132** | [RFC] hansen2024 接入裁定——链路调制上限的数值权威 | `type:rfc` | `state:needs-triage` | `none` |
| **#133** | [Task] 真正接入 hansen2024 并重算链路调制上限 | `type:task` | `state:blocked` | `docs-integrity` · `engine` |
| **#134** | [Task] 生成器输出解耦——让路径修复可验证而不改数值 | `type:task` | `state:needs-triage` | 本 issue 交付的新门禁 · `docs-integrity` |
| **#135** | [RFC] Q6b 桥接范围定案——子集桥接 vs 全量重构 | `type:rfc` | `state:needs-triage` | `none` |
| **#136** | [Task] Unity 资产身份——提交 .meta / ProjectSettings / packages-lock.json | `type:task` | `state:blocked` | `unity`（不可用） |

创建动作经 [issue-process.md §7.2](issue-process.md) 记录的本次授权执行（owner 授权 agent 直接创建并施加类型/状态标签）。每条 issue 在创建**前**都过了 `validate_issues.py --file` 门禁（9/9 退出码 0）；创建**后**又过了快照校验：

```bash
python3 code/tools/validate_issues.py --from-github
# 受校验 issue: 9 · 存量豁免: 16 · 12 rules: 7 passed, 0 failed, 5 warnings
```

5 条警告全部是**该看到的信号**，不是遗漏：`Design=—`（无设计面，I4）、能力未在切片表登记（I4 无法判定）、两处 `consumed-by: 待建:`（下游在候选队列）、`unity` 门禁不可用（I6）、命名了尚不存在的产物（I8 例外 4）、快照内无 `in-progress`（I11 空跑提醒）。

### 5.2 过反例清单（[issue-process.md §六](issue-process.md)）

| 反例 | 本次是否踩到 |
|---|---|
| R1 按文件拆 | ❌ 未踩——I5 按"生成器输出解耦"这一行为拆，虽然当下只涉及一个文件 |
| R2 按层横切 | ❌ 未踩——I7 是从数据源到产出 JSON 的一条纵切 |
| R3 巨型 issue | ❌ 未踩——原本"P4c 遗留"是一坨，已切成 I5/I6/I7 三条 |
| R4 无门禁 issue | ⚠️ **踩到后修正**：I5 需要一个尚不存在的新门禁 → 逼出 §4.1.1 例外 1；I6/I8 作为 RFC 按例外 2 写 `门禁: none` |
| R5 依赖倒挂 | ❌ 未踩——I7（数据）不依赖任何代码 issue |
| R6 隐藏依赖 | ⚠️ **踩到后修正**：I5 与 I7 的耦合（跑一次就重写 JSON）最初写在同一条里，切分后才有真实前置 |
| R7 前置未准入 | ✅ 命中并**据此拒建 issue**——CP-01 未准入，故 P5 系列一条都不建（见 §六） |
| R8 门禁不可用却声称可闭合 | ✅ 命中——I9 标 `state:blocked` 而非 `ready-for-agent` |
| R9 事后补登预期差分 | ❌ 未踩——预期差分在创建时写入 |

## 六、候选队列（不建 issue 的项及其理由）

按 [WORKFLOW.md §一](../../WORKFLOW.md)"非阻塞发现进入候选队列，不在当前变更中顺手解决"：

| 项 | 为什么不建 issue |
|---|---|
| **CP-01 准入**（owner 改 `PLAYABLE.md` 为 `AUTHORIZED_PLAYABLE: CP-01`） | 它是**决策**，权威位置就是 [PLAYABLE.md](../../PLAYABLE.md)——翻不出能力增量单元格（[§三 Step 1](issue-process.md)）。它作为 `requires: PLAYABLE:AUTHORIZED_PLAYABLE:CP-01` 出现在将来的 P5 系列 issue 上 |
| **P4d Core→Unity 接缝实现** | 依赖 I8（Q6b 定案）与 I9（资产身份），且 `gate:unity` 不可用。等 I8 出结论后再分解——现在建就是 R6/R8 |
| **P5 探索接敌 / HUD / 结束条件** | ① `PLAYABLE.md` 未准入（R7）② 依赖 P4d。且 HUD 在 `design/presentation/` 有 37 项决策但 Unity 侧未实现，是一条独立的呈现线 |
| **三项外部数据许可登记**（hansen2024 / cab-np / kroell14） | 缺口表已登记为"进入发布路径前必须补齐"，**当前无发布行为 → 不阻塞当前成果** |
| **`abagen/` 入库策略** | 同上，零消费者，不阻塞 |
| **Blender 工具纳入 CI** | 已在 [build-and-test.md §5.1](build-and-test.md) 登记为未验证项，不在切片关键路径 |
| **处置 Kevin Iglesias 资产包缺失** | 需 `gate:unity` 才能确认失败范围（PlayMode 失败项**未确认**） |
| **`.refactor-backup/` 清理** · **sim `--outdir` 落仓库外** | 工程卫生，不阻塞任何门禁；编排器自身的副作用已随 §7.2 的缺陷修复处理 |

## 七、本次分解暴露的问题（诚实清单）

### 7.1 约束文档自身被改了四处（真实 backlog 逼出来的）

**先改约束、再建 issue**，不是建完再补。四次都写进了 [§4.1.1 的例外](issue-process.md)：

| # | 逼出它的 issue | 例外 |
|---|---|---|
| 1 | I5 #134 | issue 交付的是**新门禁本身**——允许 `门禁:` 引用尚不存在但由本 issue 交付的脚本，前提是交付物明列且验收标准含登记动作 |
| 2 | I6 #132 · I8 #135 | `RFC`/`Experiment` 无机器门禁——写 `门禁: none`，但验收标准必须写明谁在何处记录决策 |
| 3 | I8 #135 · I9 #136 | 下游尚未创建——`consumed-by: 待建:<描述>`，校验器出警告而非失败 |
| 4 | I9 #136 | 正文必须**命名一个尚不存在的产物**（issue 的主题）——同行显式标注"缺失/待建/将新增"即降为警告 |
| 附加 | I9 #136 | I4 的 `Design: —`（无设计面）按不适用处理——工程侧能力没有设计轴 |

另外修正了两处**先前就存在的口径矛盾**（校验器与契约打架）：`WORKFLOW.md §一` 写 `status:in-progress` 而契约写 `state:in-progress`，已统一为 `state:*`。

### 7.2 本次工作自身发现并修复的缺陷（**不倒填成 issue**）

建立约束体系的过程中发现 `code/tools/run_all_checks.py` 有**静默全绿**缺陷：Phase 3 把 `tools/` 迁到 `code/tools/` 后，编排器仍写 `ROOT / "tools"`（已不存在的目录），于是 `get_active_validators()` 返回空列表——**跑了 0 个校验器却退出码 0**。同时注册表只有 7 条、与 CI 的 11 条循环不一致。

已在本轮工作内修复：路径改为 `code/tools/`、注册表与 CI 逐项对齐、并加"零校验器即失败（退出码 2）"的显式断言。

**为什么不补建一条 issue 来承载它**：那正是 [§六](issue-process.md) R9 禁止的"事后倒填"。修复先于约束体系存在，如实记录在此，不伪装成"由 issue 驱动"。

### 7.3 未闭合项：本次分解**没有**覆盖到的

- **P4a 的消费闭合**（[evidence/README.md](evidence/README.md)）——消费者 P4b/P4c/P4d 中 P4c 已开始，P4b/P4d 被环境阻塞，无法判定
- **CI 是否真跑过**：`build-and-test.md §5.1` 说"未在 GitHub 上真实跑过"，而 P4a 证据记录了四连 `success`。**两处口径不一致，本次未处置**（需 `gh run list` 实测才能定性）
- **`GameData` 消费者数量**：`data/README.md` §一 说 5 record 聚合，实测 8 字段——本次未处置
- **PlayMode 失败项计数**（2 项 / 共 16 项）**未确认**（无 Editor）

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [issue-process.md](issue-process.md), [gates.json](gates.json), [WORKFLOW.md](../../WORKFLOW.md), [构建与测试](build-and-test.md), [证据](evidence/README.md)*
