# 协作指南

> 这个仓库是**一个人的游戏设计项目**，配合 AI 助手推进。本文档定义协作方式与 Git 约定，**不绑定任何特定的 AI 工具**——助手可以是任何模型、任何编辑器。

> **内容规约见** [design/conventions/README.md](design/conventions/README.md)（文档格式、内容禁令、引用规范、归档隔离）；**代码与设计的边界见** [ARCHITECTURE.md](ARCHITECTURE.md)。本文只讲**怎么协作与怎么提交**。

## 目录

1. [一、仓库结构](#一仓库结构)
2. [二、工作方式](#二工作方式)
3. [三、Git 约定](#三git-约定)
4. [四、改动前自检](#四改动前自检)
5. [五、外部贡献与权利](#五外部贡献与权利)

---

## 一、仓库结构

```
design/     设计文档（正典）      ← primary artifact
reference/  外部文献与已废弃子系统
code/       实现与验证（src / unity / sim / tools）
data/       结构化数据契约
```

心智模型：**`design/` 说这个游戏是什么；`code/` 证明它跑得起来；`data/` 是两者的机器可读接口。**

## 二、工作方式

**设计驱动**：先有设计文档，再写代码。没有设计文档支撑的机制不要实现。

**讨论方式**：本仓库曾用一套十步 "grilling" 流程（GitHub issue 逐题追问 + 决策树落盘）。该流程已于 2026-09-12 停用——它产生了 47% 的仓库行数却只有 31% 的硬约束，投入产出比不成立。历史记录保留在：

- [`design/decisions/`](design/decisions/README.md) — 决策树（跨轮次索引，93 个条目）
- [`design/archive/grilling/`](design/archive/grilling/) — 各轮源记录（决策记录 / 任务计划 / 工作稿）
- [`design/archive/grilling/issues/`](design/archive/grilling/issues/README.md) — 122 个 GitHub issue 的落盘存档

**这些是历史，不是流程。** 新的设计讨论用你顺手的方式（对话、笔记、issue 都行），只要求一件事：**结论要落进 `design/`，并在此处或决策树留一条索引**。

**讨论收敛之后**，需要动手做的部分按 [issue 创建约束与需求分解](design/engineering/issue-process.md) 导入 issue 流程：讨论阶段**不建 issue**（讨论的产物是决策），收敛后过导入门，把结论分解成依赖有序、可逐步实现、带验收判据的 issue。⚠️ 2026-09-17 起新建 issue **不再有机械校验**——原来守住字段完整性的 `code/tools/validate_issues.py` 已随全部门禁一并删除，字段完整性改由人核对。

## 三、Git 约定

### 提交

- **小步提交**：完成一个独立设计文档、一个可运行脚本、或一批关联修改 → 立即提交。不要等"全部做完"。
- **按主题分批**：不同子系统的改动分开提交，不要混在一个 commit 里。
- **提交信息用中文**，格式 `类型: 描述`：

| 类型 | 用途 | 例 |
|---|---|---|
| `feat:` | 新功能 / 新系统 | `feat: 技能树系统架构文档` |
| `docs:` | 文档修改 / 新增 | `docs: 修正回合战斗流程 §五 响应窗口规则` |
| `fix:` | 修正错误 | `fix: 敌人杂兵 HP 与权威表不一致（15 → 25）` |
| `sim:` | 模拟脚本 | `sim: CTRNN 进化模拟器` |
| `refactor:` | 结构重组（不改语义） | `refactor: 路径全面改英文` |
| `chore:` | 杂项 | `chore: 清理构建产物` |

### 分支

| 分支 | 用途 |
|---|---|
| `main` | 唯一真相源，永远可发布 |
| `feat/<issue>-<功能名>-<所有者>` | 新子系统或大规模重构；多主机并行时使用所有者后缀 |
| `exp/<issue>-<实验名>-<所有者>` | 不确定方向的实验 |
| `docs/<主题>-<所有者>` | 不依附实现 Issue 的纯文档或仓库治理变更 |
| `integration/<issue>-<主题>` | 同一 Issue 有多个独立子分支时的唯一汇总分支 |

分支名中的“所有者”可以是 Agent 或主机的稳定短标识，例如 `feat/203-opening-story-host-a`。单主机工作可省略后缀。

工作完成后合并回 `main`。分支的状态与退役判据以 [WORKFLOW.md §1.1](WORKFLOW.md) 为准。

### 多主机 / 多 Agent 协作

#### 开工前

每个主机或 Agent 在改文件前先运行：

```bash
git fetch origin
git status --short --branch
git branch --show-current
git rev-list --left-right --count origin/main...HEAD
```

如果当前分支已经对应某个 PR，还必须查该 PR 是 `OPEN`、`MERGED` 还是 `CLOSED`。无法访问 GitHub 时，不得假定旧分支仍可写；可以先做只读工作，或从已确认的最新 `origin/main` 创建新分支。

查已知分支的 PR 历史（示例）：

```bash
gh pr list --head feat/204-npc-dialogue-host-a --state all
```

从最新主分支开始新任务：

```bash
git fetch origin
git switch -c feat/204-npc-dialogue-host-a origin/main
```

#### 分支所有权

- 同一个远程分支不能被两个主机同时写入。
- “我只改另一个文件”也不构成例外：两台主机同时 push 仍会产生远程分支竞争。
- PR 开启后，PR 模板中的“分支所有者”字段是该分支当前写入权的协作记录；发生交接时同步更新。
- 交接时使用“分支名 + 完整 HEAD SHA + 工作树状态”作为交接凭据。
- 新所有者必须 `fetch` 并确认本地 HEAD 与远程 SHA 相同，不得在“差不多是最新”的状态下继续。

#### PR 合并后

PR 合并后，原分支**立即只读**。如果还有后续工作，从最新 `origin/main` 新建分支：

```bash
git fetch origin
git switch -c feat/205-opening-followup-host-a origin/main
```

不得：

- 在已合并分支上再提交；
- 用已合并分支再开一个 PR；
- 因为“文件内容看起来一样”就认为 squash 后的历史仍然连续；
- 用 `push --force` 把旧分支强行改造成新分支。

应先核对合并提交与 CI，再删除已干净的本地 worktree。远程分支可在确认没有未合并提交后删除；删除不是“退役”的前提，**不再写入**才是。

### worktree

worktree 用于同一主机上的目录与分支隔离：

```bash
git fetch origin
git worktree add ../game-204-host-a -b feat/204-npc-dialogue-host-a origin/main
```

规则：

- 一个 worktree 对应一个任务分支；
- 不在两个 worktree 之间手工复制未提交文件；
- PR 合并后，确认 worktree 干净再移除；
- 不同主机之间仍依靠远程分支所有权协调，worktree 不提供跨主机锁。

### 危险操作

`git reset --hard`、`git rebase`、`git push --force`、`git clean -fd` —— **执行前必须确认**。大规模结构改动先在分支上做。

### 文件管理

设计文档（`.md`）、模拟脚本（`.py`）、原型（`.html`）、数据（`.json`）、工具脚本（`code/tools/`）**全部进版本控制**。

`data/` 与 `code/tools/` 是设计的数据源和工具，不是生成物，必须提交。生成物（`data/sim_results/`、Unity 的 `Library/`、`.nuget-pkgs/`）已在 `.gitignore` 中排除。

## 四、改动前自检

> 🔧 **2026-09-17（owner 裁定）：全部门禁已撤销。**
> 本节原列的 4 个校验器（`validate_cross_refs.py` / `validate_trash_isolation.py` / `validate_params.py` / `validate_issues.py`）已随 `code/tools/` 下的 26 个校验器与 `design/engineering/gates.json` 注册表一并删除。
> **现在没有任何机械校验在跑。** CI 只做构建与测试：

```bash
dotnet test code/src/YouAreNotTheFish.sln        # 引擎测试（CI 里跑的只有这一个）
```

改设计文档或数据后**没有命令可跑**：交叉引用死链、归档隔离、跨文件参数一致性、issue 字段完整性都只能靠人核对。引用规范本身未变（见 [写作与引用规范](design/conventions/writing-and-references.md)），只是不再有工具强制。

## 五、外部贡献与权利

本项目当前是一个人的专有游戏项目，**不默认接受未经事先约定的外部代码、设计、文本、数据或美术贡献**。提交 Issue、评论、建议或 Pull Request，不会使项目材料转为开源，也不会向提交者授予使用本项目的权利。

如希望贡献，请先通过 GitHub 联系仓库所有者，书面确认贡献范围及适用条款。贡献者必须保证：

1. 对提交内容拥有必要权利，且有权按双方书面约定授权项目使用；
2. 不提交来源不明、违反保密义务、受雇主权利约束或许可不兼容的代码、素材、数据及文本；
3. 完整披露第三方来源、许可、修改情况及必须保留的归属信息；
4. 不把 Mixamo 原始资产、论文/书籍全文、网页快照、医疗数据或其他受限制材料作为贡献提交，除非已取得明确的再分发权。

仓库所有者可自行决定拒绝、关闭或删除未约定的贡献。任何贡献只有在双方明确接受适用的书面许可或转让安排后才会合并。项目版权边界见 [`LICENSE.md`](LICENSE.md)，第三方材料边界见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

---
*创建: 2026-09-12（重写自旧版「人类 vs AI + Grilling 工作流」）| 更新: 2026-09-20（新增多主机分支所有权、worktree 隔离与 PR 合并后退役流程）*
*关联: [项目规约](design/conventions/README.md), [README](README.md), [设计总览](design/README.md)*
