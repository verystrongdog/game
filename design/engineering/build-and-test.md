# 构建与测试

> 「怎么把仓库跑起来、怎么验证」的**唯一权威**。工具版本、命令、判据以本文为准。
>
> 对应 owner 方案 P4a（锁定当前切片所需环境 + 建立最小 CI）。

## 目录

1. [一、环境锁定](#一环境锁定)
2. [二、命令](#二命令)
3. [三、CI](#三ci)
4. [四、判据](#四判据)
5. [五、已知缺口](#五已知缺口)

---

## 一、环境锁定

| 生态 | 版本 | 锁在哪 | 备注 |
|---|---|---|---|
| .NET SDK | **10.0.400** | [`global.json`](../../global.json)（`rollForward: latestFeature`） | 工程目标框架是 **net8.0**；SDK 10 可编译。**本机无 net8.0 runtime**，跑测试须 `DOTNET_ROLL_FORWARD=Major`——**口径的唯一权威处，理由与实测见 §1.3** |
| NuGet 源 | nuget.org | [`NuGet.config`](../../NuGet.config) | 此前包路径被烘焙进 `obj/*.nuget.g.props` 指向开发机（`/home/dog/game/.nuget-pkgs`），**干净检出无法复现**——本文件修掉该问题 |
| NuGet 依赖锁定 | 三份 `code/src/<工程>/packages.lock.json` + `RestoreLockedMode` | 三个 `.csproj` | 锁的是**包图**（含传递依赖），不是"源"。漂移即 `NU1004` 失败；做法与实测见 §1.2。**自 2026-09-13（#129）** |
| Python | **3.10.12** | CI 的 `setup-python` | 校验器与 sim 脚本 |
| 校验器依赖 | `PyYAML==6.0.3` · `numpy==2.2.6` | [`code/tools/requirements.txt`](../../code/tools/requirements.txt) | 15 个校验器里**只有两个**需要第三方库：`validate_disease.py`（YAML frontmatter）与 `validate_ceiling_generator.py`（numpy——它要真跑一次生成器，#134） |
| 数值实验依赖 | `numpy==2.2.6` · `scipy==1.15.3` · `numba==0.67.0` | [`code/sim/requirements.txt`](../../code/sim/requirements.txt) | 15 个 sim 脚本里只有 3 个需要 |
| Unity Editor | **6000.5.2f1**（revision `eb73d3b415a1`） | [`code/unity/ProjectSettings/ProjectVersion.txt`](../../code/unity/ProjectSettings/ProjectVersion.txt) | 版本与 revision 自 #136 起随工程入库（此前该文件只有 `m_EditorVersion` 一行）；包版本另有 `code/unity/Packages/packages-lock.json` 可复现。Unity 侧的**未验证项**见 §五 |

**锁定原则**：**不在锁定提交中升级**任何运行时或软件包。上表版本即当前实测版本。

### 1.1 引擎第三方包（nuget）

| 包 | 版本 |
|---|---|
| `Microsoft.NET.Test.Sdk` | 17.8.0 |
| `xunit` | 2.5.3 |
| `xunit.runner.visualstudio` | 2.5.3 |
| `coverlet.collector` | 6.0.0 |

`YouAreNotTheFish.Core`（逻辑库）**无第三方依赖**——这是刻意的：逻辑核要能被 Unity 稳定引用。

### 1.2 依赖锁定（nuget 包图，2026-09-13 · [#129](https://github.com/verystrongdog/game/issues/129)）

**锁在哪**：`code/src/<工程>/packages.lock.json`（三个工程各一份，随工程入库）**加上**工程属性
`RestorePackagesWithLockFile` / `RestoreLockedMode`（三个 `.csproj` 各 5 行）。锁定日 **2026-09-13**，SDK **10.0.400**。

| 工程 | 锁文件内容 |
|---|---|
| `YouAreNotTheFish.Core` | **0 依赖**（空 `net8.0` 节点——把"逻辑核无第三方依赖"变成机械可查的事实） |
| `YouAreNotTheFish.Console` | 1 条：对 `Core` 的**项目引用**（不是包） |
| `YouAreNotTheFish.Core.Tests` | 4 个直接依赖 + 89 条包图（含传递依赖，逐条带 `contentHash`） |

**为什么还要 `RestoreLockedMode`**：只提交锁文件时，`dotnet restore` 在"锁文件与工程不一致"的场合会**静默重写**它——
锁就退化成一份随时会被改写的快照，漂移照样进得来。打开锁模式后，不一致直接 `NU1004` 失败。
**它不需要改 CI**：CI 跑的就是普通 `dotnet restore`，强制点在工程属性里，`engine` job 自动受约束。

**加包 / 改版本后，更新锁文件的唯一正确做法**：

```bash
dotnet restore code/src/YouAreNotTheFish.sln --force-evaluate
```

#### 实测读数（2026-09-13）

| # | 检查 | 退出码 | 读数 |
|---|---|---|---|
| 1 | 锁定前后包集合逐条比对 | — | **零版本漂移**（89 条包图完全相同；差异只有 assets 里两个 `type: Project` 工程引用条目） |
| 2 | **注入漂移**：`xunit` `2.5.3` → `2.5.4` 后跑 `dotnet restore` | **1** | `NU1004: The package reference xunit version has changed from [2.5.3, ) to [2.5.4, ) … can't be run in locked mode`——**锁模式确实在生效**，不是摆设 |
| 3 | 锁模式下 restore 是否改写锁文件 | 0 | 工作区干净：**锁文件未被改写** |
| 4 | 干净 worktree + **空** `NUGET_PACKAGES`（初始 0 个文件）下 `dotnet restore` | 0 | 包全部由 nuget.org 现取（探针包目录 0 → 92 条），**不依赖开发机缓存**；探法与 P4a 的 `.ci-probe-pkgs` 同构 |
| 5 | 同环境 `dotnet restore --locked-mode` | 0 | 锁文件与工程图一致 |
| 6 | 同环境 `dotnet build --no-restore -c Release` | 0 | 0 error |
| 7 | 同环境 `dotnet test --no-build -c Release` | 0 | **416 passed / 0 failed** |
| 8 | 同环境 `dotnet restore --force-evaluate` 后比对 | 0 | 锁文件**逐字节不变**——**生成确定性成立**（空缓存态与开发机态生成同一份锁） |
| 9 | **真实 CI**（`ubuntu-latest`，空包缓存）`engine` job | 0 | run `34761263268`（`47b05ea`）四 job 全绿——锁模式在干净 runner 上同样生效，不是只在本机成立 |

> 探针环境的一处噪声（如实记）：`NU1900` 警告——本机 NuGet HTTP 缓存目录只读，取漏洞数据失败。
> 它不参与包图解析，也不改变上表任一条判定。

> ⚠️ **`.csproj` 注释里不能出现 `--`**：把 `dotnet restore --force-evaluate` 原样写进 XML 注释会让工程解析直接失败
> （`MSB4025: An XML comment cannot contain '--'`，三个工程全挂）。所以注释只指路（指到本节），命令写在这里。

### 1.3 roll-forward 口径（2026-09-13 · [#131](https://github.com/verystrongdog/game/issues/131)）

**规定值：`DOTNET_ROLL_FORWARD=Major`。** 本机只有 .NET 10 运行时（10.0.11）而工程目标框架是 net8.0，
所以跑测试**必须** roll-forward——它不是一个可有可无的偏好项。

| # | 命令（base `0a5e346`） | 退出码 | 读数 |
|---|---|---|---|
| 1 | `DOTNET_ROLL_FORWARD=Major dotnet test code/src/YouAreNotTheFish.sln -c Release` | 0 | **416 passed / 0 failed** |
| 2 | `DOTNET_ROLL_FORWARD=LatestMajor`（同上，只换这一个变量） | 0 | **416 passed / 0 failed** |
| 3 | **不设**该变量（同上） | **1** | testhost 起不来：`You must install or update .NET to run this application` |

**为什么规定 `Major` 而不是 `LatestMajor`**（两个值在本机都可行，所以必须写明理由，不能"任选其一"）：
`Major` 取**最近**的高主版本，`LatestMajor` 取**最高**的。本机将来装上 11/12 时，前者仍优先选最近的 runtime，
行为更保守、更可预测——门禁要的是"能跑起来"而不是"跑在最新上"。`gates.json` 的 `engine` 命令与
`code/tools/compare_fixture_verdicts.py` 的默认值同为此值。

> ⚠️ **实测推翻了 #131 立题时的一个前提**：两个值**不是**"只可能有一个成立"——只装一个主版本（10）时，
> 两者解析到同一个 runtime。真正会失败的是**不设**这一项（第 3 行）。所以本 issue 的结论不是"改正一个错值"，
> 而是"在两个可行值里**规定一个**并写死理由"。
>
> **历史时点口径不改写**（同 §四 的规矩）：`design/decisions/05-numbered-engine-implementation.md` 与
> `design/archive/grilling/` 里的环境注记写的是 `LatestMajor`，那是**当时**沙箱的记法；
> 决策树按 [项目规约 §六](../conventions/README.md) 是冻结历史层——看到旧口径不要"顺手统一"。

## 二、命令

### 2.1 设计正典与数据契约（改文档或数据后必跑）

```bash
pip install -r code/tools/requirements.txt

python3 code/tools/validate_cross_refs.py        # 跨文件引用：死链 / 段引用
python3 code/tools/validate_trash_isolation.py   # 归档隔离 + 废弃术语残留
python3 code/tools/validate_params.py            # 跨文件同名参数一致性
python3 code/tools/validate_spatial.py           # 空间坐标
python3 code/tools/validate_disease.py           # 疾病目录 ↔ pathology_edges
python3 code/tools/validate_cards.py             # 卡牌参数（已废弃系统，参考）
python3 code/tools/validate_eligibility.py       # 疾病资格门
python3 code/tools/validate_situation_fids.py    # 情境原型 fid
python3 code/tools/validate_tripartite_annotations.py  # 三体模型注释
python3 code/tools/validate_data_manifest.py     # 数据契约（runtime allowlist / 属性正交 / 清单一致）
python3 code/tools/validate_runtime_fixtures.py  # runtime 数据结构契约 + 53 条 fixture 判定（Python 侧）
python3 code/tools/validate_unity_assets.py      # Unity 资产身份：.meta 成对性 / GUID 唯一性 / guid 引用可解析 / FBX Rig（无 Editor 依赖）
python3 code/tools/validate_ceiling_generator.py # 生成链解耦：只写 MD 不得改写数据契约（#134，需 numpy）
python3 code/tools/validate_hansen_intake.py     # hansen2024 只读结构校验（#133，纯标准库）
python3 code/tools/build_runtime_data_fixtures.py --check   # fixture 索引与磁盘一致
```

**issue 契约**（新建或修改 issue 后跑；需要 `gh` 已认证或 `GH_TOKEN`）：

```bash
python3 code/tools/test_validate_issues.py                 # 规则 fixture：14 条规则各一正一反（36 条用例，不联网）
python3 code/tools/validate_issues.py --from-github        # 校验开放 issue 的字段/依赖/门禁/单线程
python3 code/tools/validate_issues.py --file <草稿.md>      # 创建前的门禁（草稿为临时文件，不入库）
```

规则表 I1–I12 与字段定义见 [issue-process.md §5.2](issue-process.md)。

> **为什么要 fixture**：`validate_issues.py` 是 1400+ 行、14 条规则的**元工具**——它错了没人替它把关。此前它没有任何自动化测试，代价已经付过两次：① §4.1.1 例外 1「门禁可引用尚不存在的脚本」**文档承诺了、代码从未实现**，存活到 #142 首次交付新门禁才被撞出；② #134 的门禁行因解析器从散文里误抓到一个**已存在的文档路径**而空过（越啰嗦越安全）。`test_validate_issues.py` 落地当天即抓出两处：**I13 读的 `snapshot["closed_numbers"]` 从未被 `fetch_snapshot` 产出**（恒为空集 → 「blocked-by 全部已关闭」判据永不成立）、**I8 的豁免标记会被路径自身的文件名命中**（`根本不存在.py` 让真缺失的引用被降级为警告）。两条都已修，并各有对应用例钉住。

**干净检出检查**（CI 已纳入）：

```bash
python3 code/tools/check_clean_checkout.py
```

查两件事：① 受控文件是否引用了**未受控**路径（本地因残留文件而通过、干净检出必然断）② **代码**里是否有开发机绝对路径。
文档/数据中的机器路径只报提示——那是出处引用（某文献来自某下载目录、某结论据某路径核查），不参与运行。

> 为何需要它：2026-09-12 CI 首跑失败的三类缺陷，**全部**是这一类——本地有残留产物与残留文件，模拟测试无法发现。

编排器：`python3 code/tools/run_all_checks.py`（⚠️ **有副作用**——写 `.checks-state.json`，CI 里不要用）

> 2026-09-12 修：编排器此前把校验器目录写成 `ROOT / "tools"`（Phase 3 之后该目录已不存在），于是 `get_active_validators()` 返回空列表——**跑了 0 个校验器却退出码 0**，是静默全绿。现已改为 `code/tools/`，注册表与 CI 的 14 个循环逐项对齐，并加「找不到校验器即退出 2」的断言。判据：编排器读数必须与 §三 的 `docs-integrity` job 一致。

### 2.2 引擎（改代码后必跑）

```bash
# 本机无 net8.0 runtime，必须 roll-forward；规定值 Major，口径与实测见 §1.3
export DOTNET_ROLL_FORWARD=Major

dotnet restore code/src/YouAreNotTheFish.sln
dotnet build   code/src/YouAreNotTheFish.sln --no-restore -c Release
dotnet test    code/src/YouAreNotTheFish.sln --no-build  -c Release
```

> **sln 里还有一项：桥接工程**（`code/src/YouAreNotTheFish.Core.Unity/`，`netstandard2.1`）——它是 [ARCHITECTURE.md §4.1](../../ARCHITECTURE.md) 的**机械护栏**（[#155](https://github.com/verystrongdog/game/issues/155)）：
> 用 `<Compile Include>` **链接** Core 的 3 个源文件（`Engine/DamageCalculator.cs` · `Types/CalibrationConfig.cs` · `Types/IRng.cs`）+ `IsExternalInit` 垫片。
> 上面那条 `dotnet build` 已经把它编了；CI 里另有一步**单独再编一次**，好让护栏红了时一眼可辨（护栏当前无 Unity 侧消费者——白盒宿主已退役）。

**离线环境**：设 `NUGET_PACKAGES=<repo>/.nuget-pkgs` 复用仓库内缓存（该目录被 gitignore，非干净检出可依赖）。

### 2.2.1 跨语言数据契约（P4c）

```bash
python3 code/tools/compare_fixture_verdicts.py
```

对 `data/runtime-fixtures/` 的 53 条 fixture，分别用 **Python 规则表**与 **C# 真实加载器**
判定「接受/拒绝」，再逐条比对。

**为何不能只"共用 fixture"**：两侧读同一批输入 ≠ 两侧给出同一判定。
owner 方案 §9.3 的判据是「跨语言**接受/拒绝集合一致**」——只有把判定逐条比对、
且差异为空，判据才成立。本脚本就是那条比对，CI 的 `engine` job 会跑它。

**两侧的分工**（不是分叉）：

| 侧 | 走什么 | 覆盖 |
|---|---|---|
| Python | `validate_runtime_fixtures.py` 的规则表 | 结构 / 枚举 / 长度 / 值域 |
| C# | `GameDataLoader` 真实加载器 | 同上 **+** 跨文件语义（moonlight 的 supp ⊆ W_active）+ 反序列化层契约（`[JsonRequired]`、枚举 converter） |

C# 的语义部分**只在引擎里实现一次**——Python 侧不重复实现，重复就是第二个真相源。

### 2.3 数值实验（**不在切片关键路径**，按需跑）

```bash
pip install -r code/sim/requirements.txt
python3 code/sim/sim_consciousness_v7_rb_test.py      # 例：判别三角自检
```

sim 脚本用**扁平 import**（`from sim_consciousness_cs4_test import ...`），必须**以 `code/sim/` 为工作目录**运行，否则 import 失败。

### 2.4 数据生成链（链路调制上限 · [#134](https://github.com/verystrongdog/game/issues/134)）

```bash
python3 code/tools/gen_modulation_ceiling.py --md-only   # 只写参考表，不重写数据契约（安全）
python3 code/tools/validate_ceiling_generator.py         # 把"解耦成立"钉成判据（CI 已纳入）
```

`gen_modulation_ceiling.py`（v1）默认模式会**重算并重写** `data/connectivity/link_modulation_ceiling.json`——
那份 JSON 是 **2026-07-27 的冻结快照**（`_metadata.provenance_note` 自述数值未重算），所以日常不要跑默认模式。
`--md-only` 是给"只想看表"和"验证解耦"用的：**一个字节的数据契约都不碰**。

MD 参考表的默认落点是被 gitignore 的 `artifacts/链路调制上限参考表.md`（可用 `--md-out PATH` 改）：

- **不写回 `design/`**：v1 参考表已被 v2（`gen_modulation_ceiling_v2.py` → `design/rules/skill-tree/modulation/链路调制上限参考表-v2.md`）取代，写回正典会制造第二个权威来源；
- **不刷新 `design/rules/skill-tree/deprecated/链路调制上限参考表.md`**：那是与 v1 JSON 同一份快照纪律的**历史快照**，重算等于把"当时的表"改成"今天的表"（2026-09-13 owner 决定）。

| # | 检查（2026-09-13 实测，base `e51b586`） | 退出码 | 读数 |
|---|---|---|---|
| 1 | 改动前：`python3 code/tools/gen_modulation_ceiling.py`（默认模式） | **1** | 数据契约**先被改写**（`79d7cab…` → `dc2e62f…`，273 行数值），随后抛 `FileNotFoundError: …/技能树系统/链路调制上限参考表.md`——「修路径」与「改 836 个数值」被绑在一起 |
| 2 | `… --md-only`（解耦后） | 0 | 两个 JSON SHA256 **不变**（`79d7cab…` / `95a7082…`）· MD 成功写出（84 行） |
| 3 | `validate_ceiling_generator.py` | 0 | 通过侧：数据契约不变 · MD 已写出 · 历史快照未被动 |
| 4 | 同校验器 + **注入缺陷 1**（让 `--md-only` 不生效） | **1** | `❌ 数据契约被改写：link_modulation_ceiling.json`（带 before/after SHA256） |
| 5 | 同校验器 + **注入缺陷 2**（把 MD 写回那份历史快照） | **1** | `❌ 历史快照被动过：design/rules/skill-tree/deprecated/链路调制上限参考表.md` |
| 6 | **真实 CI**（`docs-integrity` job 的循环，13 个校验器） | 0 | run `34762173574` 日志原文里有 `validate_ceiling_generator ✅`——干净 runner（numpy 由 `code/tools/requirements.txt` 装）上同样成立 |

第 4/5 行是**在临时 worktree 里注入缺陷后跑的**（跑完即删）——「两侧都要演示」不许只演通过侧。
校验器把 MD 写到 `<临时目录>`，**自己绝不写工作树**（§四「工作树」判据）。

> ⚠️ **一处已知的小疣**（如实记）：MD 模板里那行 JSON 链接（`../../data/connectivity/…`）是按旧落点写死的，
> 落到 `artifacts/` 后它是相对错误的。**没修**——#134 明确排除"改 MD 内容模板"，
> 且默认落点是非受控产物（不进任何校验器的引用面）。要点是"能写出来"，不是"这份产物完美"。

## 三、CI

[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — 四个 job，对应切片三轴 + issue 契约：

| job | 覆盖 | 本机可复现 |
|---|---|---|
| `docs-integrity` | 15 个校验器（与 §2.1 同一循环）+ fixture 索引契约 | ✅ |
| `engine` | SDK 版本核对 → restore → Release build → Release test → **跨语言 fixture 判定比对** → trx artifact | ✅ |
| `issues-snapshot` | 规则 fixture（`test_validate_issues.py`，不联网）+ 开放 issue 的契约校验（`validate_issues.py --from-github`，需 `issues: read`） | ✅ |
| `unity` | **显式报告 `NOT_AVAILABLE`** | ❌ 需 Editor |

**为何 `unity` job 是一个"什么也不做"的 job**：按 [WORKFLOW.md §五](../../WORKFLOW.md)，**未运行不是通过**。若直接省略该 job，整个 workflow 会全绿，而 Unity 门禁（P4b/P4d/P5）实际未执行——那是静默跳过。因此它存在、具名标注 `NOT_AVAILABLE`、并在作业摘要里列出受影响的门禁。

## 四、判据

> **测试计数的唯一权威处就是本节**（2026-09-13 实跑：`416 passed / 0 failed`，命令与工具口径见 §2.2；
> **同 commit 的 CI `engine` job 里也是 416/0**——run `34761515884` 的日志原文，不是"job 绿"的推论）。
> 其余文档**引用本节、不复述数字**——复述就是下一次漂移的入口（[#130](https://github.com/verystrongdog/game/issues/130) 的成因：
> `ARCHITECTURE.md` / `README.md` / `slice.md` 三处停在 `353`，与本节判据不一致）。
>
> **怎么在 CI 上核实一条判据**（2026-09-13 踩过）：`gh run view <run> --log` 在本环境**取不到正文**（返回空）。
> 取 job 日志用两步 API：`gh api /repos/<owner>/<repo>/actions/runs/<run_id>/jobs`（拿 job id）→
> `gh api --allow-escape-sequences /repos/<owner>/<repo>/actions/jobs/<job_id>/logs | sed -e 's/\x1b\[[0-9;]*m//g'`
> （少了 `--allow-escape-sequences` 会直接 exit 1 且不输出）。**"CI 表面绿色"不能代替日志原文**——见 [WORKFLOW.md §六](../../WORKFLOW.md)。
>
> **历史时点读数不改写**：`REFACTOR-PLAN.md` 各 Phase 结果表（4 处 `353 passed`）、`design/README.md` 路线图日志里
> `2026-09-03 … 353/353 绿`、`design/archive/`、以及 `evidence/` 里绑定 base/head 的读数——
> 记的都是"那一刻跑出来多少"，各自绑定当时的 commit。它们**不是当前口径**，看到旧数字不要"顺手统一"。

| 判据 | 要求 |
|---|---|
| 校验器 | 15/15 退出码 0 |
| `validate_cross_refs` | **0 死链 / 0 段引用警告** |
| 引擎测试 | **416 passed / 0 failed**（唯一权威；其余文档引用本节） |
| 跨语言 fixture 判定 | `compare_fixture_verdicts.py` 逐条比对 Python 与 C# 的接受/拒绝，**差异为空**（53 条） |
| 干净检出 | 无本地缓存（`.nuget-pkgs`）也能 restore + 构建 + 测试 |
| SDK 版本 | 与 `global.json` 一致，不一致即失败（CI 有显式断言） |
| issue 契约 | `validate_issues.py --from-github` 退出码 0（存量 issue 按 [issue-process.md §7.4](issue-process.md) 显式跳过，不算通过） |
| 工作树 | 跑完检查后**无非预期变化**（校验器不写工作树） |

## 五、已知缺口

| 缺口 | 影响 | 解除条件 |
|---|---|---|
| **Unity 门禁** | ✏️ 2026-09-12：**本机已可跑**——Linux 侧是同一台 Windows 上的 WSL2，`unity.exe` 经 interop 直驱 Windows Editor（实测 `unity status` → `state: ready`、`unity open` 工程 → 编译 0 错误）。**CI（ubuntu）侧仍不可用**，其 `unity` job 继续显式报告 `NOT_AVAILABLE`。判据按 [gates.json](gates.json) 的 `environment` 判定 | — |
| `code/unity/Packages/packages-lock.json` 缺失 | 包版本不可复现 | ✅ 2026-09-12 **已入库**（`code/unity/Packages/packages-lock.json` + 与之同源的 `manifest.json`——只提交锁会让两者立刻不一致）。一致性机械核法：锁里 builtin 依赖版本 = Editor 6000.5.2f1 安装自带的版本（`com.unity.ugui` 2.5.0 / `com.unity.test-framework` 1.7.0，取自该安装的 `BuiltInPackages/`） |
| `.meta` 2 个 / 场景 0 个 | Unity 工程不完整，场景靠 Editor 菜单运行时生成；**Blend Tree 阈值 / transition 参数 / Avatar Mask 无处安放**——手调动画成果无法入库。更具体地说：9 个 Mixamo FBX **已在 git 里却没有 `.meta`** → 干净检出每次开工程都重发 GUID，`ActionLab.controller` 的 clip 绑定必然失效 | ✅ 2026-09-12 [#136](https://github.com/verystrongdog/game/issues/136) 闭合：`.meta` **2 → 57**、场景 **0 → 1**（`ActionLab.unity`）、controller **0 → 1**、`ProjectSettings/` **1 → 23**，共 80 个新文件 + 2 个文件改动（`code/src/` 与 `data/` 零改动）。实测记录与证据见 [code/unity/README.md §二·H](../../code/unity/README.md)。**残留**：controller 的 4 条 locomotion 态仍引用不入库的 KI 包（#139 工作面）；干净检出的首次导入未实测（Editor 只跑在 Windows 拷贝上）；资产身份尚无常驻校验器 |
| 无 `NuGet.lock`（packages.lock.json） | 传递依赖版本可漂移 | ✅ 2026-09-13 [#129](https://github.com/verystrongdog/game/issues/129) 闭合：三个工程提交 `packages.lock.json` 并打开 `RestoreLockedMode`（SDK 10.0.400 · 锁定日 2026-09-13）——干净 worktree + **空**包目录下 restore/build/test 通过（**416 passed / 0 failed**），注入漂移实测 `NU1004`，锁文件生成确定性成立。读数见 §1.2 |

### 5.1 未验证项（诚实清单）

- CI **未在 GitHub 上真实跑过**——本机只逐条模拟了各 step 的命令与退出码。首次 push 后的 CI 结果才是真证据
- 数值实验（sim）**不在 CI 中**——它们不在切片关键路径上，且成本高（部分脚本需数分钟）
- Blender 相关工具（`code/tools/*blender*.py`）**无环境验证**——本机有 `/snap/bin/blender`，但未纳入 CI
- Unity **干净检出（无 `Library/`）的首次导入 / 编译 / Play 未实测**——Editor 只跑在 Windows 那份拷贝上（Linux 侧无 Editor，且 WSL 对 `/mnt/c` 只读）。#136 入库的正确性由三条间接证据支撑（逐文件字节一致 / GUID 引用全部可解析 / 来源工程内 0 错误且 16 项测试跑通），见 [code/unity/README.md §二·H](../../code/unity/README.md)
- **资产身份无常驻机械校验器**（`.meta` 齐全性、GUID 唯一性、场景与 controller 的引用可解析性）——#136 是用一次性脚本核的（294 个 `.meta` → 294 个唯一 GUID / 0 冲突）。缺它则本次的判据无法回归

---
*创建: 2026-09-12 | 更新: 2026-09-13（§1.2 依赖锁定 #129 · §1.3 roll-forward 口径 #131 · §2.4 生成链解耦 #134）*
*关联: [工程文档索引](README.md), [WORKFLOW.md](../../WORKFLOW.md), [ARCHITECTURE.md](../../ARCHITECTURE.md), [证据](evidence/README.md)*
