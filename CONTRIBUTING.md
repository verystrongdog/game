# 协作指南

> 这个仓库是**一个人的游戏设计项目**，配合 AI 助手推进。本文档定义协作方式与 Git 约定，**不绑定任何特定的 AI 工具**——助手可以是任何模型、任何编辑器。

> **内容规约见** [design/conventions/README.md](design/conventions/README.md)（文档格式、内容禁令、引用规范、归档隔离）；**代码与设计的边界见** [ARCHITECTURE.md](ARCHITECTURE.md)。本文只讲**怎么协作与怎么提交**。

## 目录

1. [一、仓库结构](#一仓库结构)
2. [二、工作方式](#二工作方式)
3. [三、Git 约定](#三git-约定)
4. [四、改动前自检](#四改动前自检)

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
| `feat/<功能名>` | 新子系统或大规模重构 |
| `exp/<实验名>` | 不确定方向的实验 |

工作完成后合并回 `main`。

### 危险操作

`git reset --hard`、`git rebase`、`git push --force`、`git clean -fd` —— **执行前必须确认**。大规模结构改动先在分支上做。

### 文件管理

设计文档（`.md`）、模拟脚本（`.py`）、原型（`.html`）、数据（`.json`）、工具脚本（`code/tools/`）**全部进版本控制**。

`data/` 与 `code/tools/` 是设计的数据源和工具，不是生成物，必须提交。生成物（`data/sim_results/`、Unity 的 `Library/`、`.nuget-pkgs/`）已在 `.gitignore` 中排除。

## 四、改动前自检

改设计文档或数据后，跑一遍校验器：

```bash
python3 code/tools/validate_cross_refs.py        # 死链 / 段引用
python3 code/tools/validate_trash_isolation.py   # 归档隔离 + 废弃术语残留
python3 code/tools/validate_params.py            # 跨文件参数一致性
dotnet test code/src/YouAreNotTheFish.sln        # 引擎测试（改代码时）
```

`validate_cross_refs.py` 报 0 死链、`dotnet test` 全绿，是提交前的底线。

---
*创建: 2026-09-12（重写自旧版「人类 vs AI + Grilling 工作流」）| 更新: 2026-09-12*
*关联: [项目规约](design/conventions/README.md), [README](README.md), [设计总览](design/README.md)*
