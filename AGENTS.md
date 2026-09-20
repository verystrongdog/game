# AGENTS.md — 子非鱼

> 本仓库唯一的通用 Agent 约束入口。**任何 AI 助手在改动本仓库前读这一份。**内容规约见 [design/conventions/README.md](design/conventions/README.md)，架构边界见 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 一、这是什么仓库

一个人的**游戏设计项目**：3D 回合制心理对抗游戏《子非鱼》。**设计文档是 primary artifact**，代码是验证与实现工具。

```
design/      设计文档（正典）     ← 唯一真相源
reference/   文献与已废弃子系统
code/        src(C#逻辑) unity(呈现) sim(实验) tools(校验)
data/        结构化数据契约
```

**当前可玩状态见 [PLAYABLE.md](PLAYABLE.md)**。工作与 Issue 流程见 [WORKFLOW.md](WORKFLOW.md)；**issue 的创建约束与需求分解**见 [design/engineering/issue-process.md](design/engineering/issue-process.md)——讨论阶段不建 issue，收敛后过导入门再分解。

## 二、硬约束

### 内容

- **设计驱动代码**：先有设计文档，再写代码。没有设计文档支撑的机制不要实现。
- **设计与代码冲突时以 `design/` 为准**，并修代码——不是反过来。
- **代码里每个数值常量必须有来源注释**（`来源：<文档> §<节>`）。
- **同一事实只有一个权威来源**：设计声明、代码实现、试玩证据不得混为"已完成"。

### 术语

术语状态以 [`data/term_registry.json`](data/term_registry.json) 的 `status` 字段为准。**很多常规词汇在本项目里是已废弃的旧模型**：

| 术语 | 状态 | 替代 |
|---|---|---|
| 态度 / 7驱动 / 5模块 / CPM / 意志力 | ⚠️ deprecated | 技能分类现为**主导网络（Kroell 14 网络）× 主导角色（8 行为角色）**；意志力已换为**认知负荷模型** |
| PAD | ✅ 活跃（情绪表示） | 但作为**技能定位空间**已废弃（坐标已迁 MNI） |
| SAN | ✅ 活跃 | 是护盾不是血条 |

**禁止重新引入**：颜色表示情绪/态度 · 离散 ±1/0 态度晶体 · "态度卡" · 卡牌交互 · 战斗简化为削血 · 治疗模拟框架。完整清单见 [项目规约 §二](design/conventions/README.md)。

### 引用

- **引用即读取**：任何事实性引用（参数、公式、已有决策、文件路径）**必须先读源文件确认**，不得凭记忆引用。
- 引用格式：优先段引用（`§八`）而非 URL 锚点。完整规范见 [写作与引用规范](design/conventions/writing-and-references.md)。

### 归档隔离

活跃文档**不得引用垃圾桶下的路径**——原 `design/archive/trash/` 已于 2026-09-13 整份移出仓库，现本地保留在 `.trash/`（被忽略），**两个位置都不得指向**；也不得使用已废弃的数字/术语（只允许出现在 [决策树](design/decisions/README.md) 历史记录或标注 `⚠️ 已废弃` 的段落中）。详见 [项目规约 §六](design/conventions/README.md)。

## 三、改动前自检

> 🔧 **2026-09-17（owner 裁定）：全部门禁已撤销。**
> 本节原列的 5 条必跑校验器、`design/engineering/gates.json` 注册表、`code/tools/` 下 26 个校验器与 fixture 脚本、以及 CI 里的 `docs-integrity` / `issues-snapshot` / `unity` 三个门禁 job，已一并删除。
> **现在没有任何机械校验在跑。** 🔧 **2026-09-18 注**：新增了一个**只报不拦**的 CI job（`npc-materials-report` + `code/tools/check_npc_materials.py`）——它**不是门禁**：单脚本、只用 stdlib、不建例外表、`continue-on-error: true`、永远不改红叉，只产出报告 artifact。**门禁的处境不变**（撤销状态维持），上面这句在本节其余部分的含义也不变。CI 只做构建与测试：

```bash
dotnet test code/src/YouAreNotTheFish.sln        # 引擎测试（CI 里跑的只有这一个）
```

⚠️ **须知（事实，不是劝阻）**：`design/` 下 526 篇文档、`data/` 下 1904 个契约文件之间的交叉引用，以前由 `validate_cross_refs` 守着——撤销前最后一次读数是 **2163 条引用 / 0 死链**。**那条护栏现在没有了**：死链、废弃术语残留、参数漂移、归档隔离违规都只能靠人盯。引用规范本身（[写作与引用规范](design/conventions/writing-and-references.md)）未变，只是不再有工具强制。

**改 `code/unity/Assets/**`、或经 CLI 驱动 Unity Editor 之前**，先查 [危险点表](design/engineering/危险点表.md)（按**位置**检索的排障索引：这个位置反复出什么事、判据是什么、怎么躲）。该表是**人工查阅的文档，不是门禁**；它覆盖 Unity 侧的坑。

## 四、Git

- **小步提交**，按主题分批，不混 commit
- 提交信息用中文，格式 `类型: 描述`（`feat` / `docs` / `fix` / `sim` / `refactor` / `chore`）
- **一个远程可写分支同时只能由一个主机 / Agent 会话拥有**；多主机并行必须使用独立分支，见 [WORKFLOW.md §1.1.1](WORKFLOW.md)
- **PR 合并后原分支立即退役，不得继续提交或再开 PR**；后续工作必须从最新 `origin/main` 创建新分支，对 squash merge 也无例外，见 [WORKFLOW.md §1.1.3](WORKFLOW.md)
- 开工前必须 `fetch` 并确认：当前分支所属任务、PR 状态、工作树、与 `origin/main` 的差异、以及本会话的分支所有权
- 大规模结构改动先开分支；`git reset --hard` / `rebase` / `push --force` **执行前必须确认**
- 过程物（会话存档、书籍全文、运行日志、模拟结果）由 `.gitignore` 排除，磁盘保留

## 五、历史说明

本仓库曾长期运行一套十步 "grilling" 流程（2026-09-12 停用）。历史记录保留在：

- [决策树](design/decisions/README.md) — 93 个条目的决策分叉记录（**已冻结，只读**）
- [design/archive/grilling/](design/archive/grilling/) — 各轮源记录 + 122 个 GitHub issue 存档

**这些是历史，不是流程。** 新的设计讨论用你顺手的方式，只要求结论落进 `design/`。

---
*创建: 2026-09-12 | 更新: 2026-09-20（§四新增多主机分支所有权与合并后强制退役约束）*
*关联: [项目规约](design/conventions/README.md), [架构](ARCHITECTURE.md), [可玩状态](PLAYABLE.md), [工作流程](WORKFLOW.md), [协作指南](CONTRIBUTING.md)*
