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

活跃文档**不得引用** `design/archive/trash/` 下的路径，也不得使用已废弃的数字/术语（只允许出现在 [决策树](design/decisions/README.md) 历史记录或标注 `⚠️ 已废弃` 的段落中）。

## 三、改动前自检（提交底线）

```bash
python3 code/tools/validate_cross_refs.py        # 跨文件引用：必须 0 死链 / 0 段引用警告
python3 code/tools/validate_trash_isolation.py   # 归档隔离 + 废弃术语残留
python3 code/tools/validate_params.py            # 跨文件参数一致性
python3 code/tools/validate_issues.py --from-github  # issue 契约（字段/依赖/门禁/单线程）
dotnet test code/src/YouAreNotTheFish.sln        # 引擎测试（改代码时）
```

改设计文档或数据后跑前三条；改代码后跑第四条；**新建或修改 issue 后跑第四条**（issue 是准入载体，其字段与依赖边同样受机械校验）。**报 0 死链 + 测试全绿是底线**，不是"锦上添花"。

## 四、Git

- **小步提交**，按主题分批，不混 commit
- 提交信息用中文，格式 `类型: 描述`（`feat` / `docs` / `fix` / `sim` / `refactor` / `chore`）
- 大规模结构改动先开分支；`git reset --hard` / `rebase` / `push --force` **执行前必须确认**
- 过程物（会话存档、书籍全文、运行日志、模拟结果）由 `.gitignore` 排除，磁盘保留

## 五、历史说明

本仓库曾长期运行一套十步 "grilling" 流程（2026-09-12 停用）。历史记录保留在：

- [决策树](design/decisions/README.md) — 93 个条目的决策分叉记录（**已冻结，只读**）
- [design/archive/grilling/](design/archive/grilling/) — 各轮源记录 + 122 个 GitHub issue 存档

**这些是历史，不是流程。** 新的设计讨论用你顺手的方式，只要求结论落进 `design/`。

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [项目规约](design/conventions/README.md), [架构](ARCHITECTURE.md), [可玩状态](PLAYABLE.md), [工作流程](WORKFLOW.md), [协作指南](CONTRIBUTING.md)*
