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

## 三、改动前自检（提交底线）

```bash
python3 code/tools/validate_cross_refs.py        # 跨文件引用：必须 0 死链 / 0 段引用警告
python3 code/tools/validate_trash_isolation.py   # 归档隔离 + 废弃术语残留
python3 code/tools/validate_params.py            # 跨文件参数一致性
python3 code/tools/validate_issues.py --from-github  # issue 契约快照（字段/依赖/门禁/单线程）
python3 code/tools/test_validate_issues.py       # issue 规则正反例 fixture（门禁 issues-fixtures）
dotnet test code/src/YouAreNotTheFish.sln        # 引擎测试（改代码时）
```

**按名字对应，不按行号**（行号一插就错位）：改设计文档或数据后跑 `validate_cross_refs` · `validate_trash_isolation` · `validate_params`；**新建或修改 issue 后跑 `validate_issues --from-github` 与 `test_validate_issues` 两条**（前者是快照校验，后者是规则的正反例 fixture——两者是**不同的门禁**，只跑前者会让规则回归漏到 CI 才暴露，实例见 [#188](https://github.com/verystrongdog/game/issues/188)）；改代码后跑 `dotnet test`。**报 0 死链 + 测试全绿是底线**，不是"锦上添花"。

**本节是默认必跑的子集，权威清单是 [`gates.json`](design/engineering/gates.json)**（机器可读：gate id / 命令 / CI job / 本机可用性 / 不可用时阻塞什么）。其余门禁按改动面挑选：`unity` 与 `unity-assets` 属 Unity 资产面（`unity` 需 Editor——本机经 WSL interop 可用、CI 侧报 `NOT_AVAILABLE`）、`engine` 需 .NET SDK 且耗时（CI 每次跑）、`npc-materials-fixtures` 与 `issues-fixtures` 是素材与 issue 的 fixture 套件。**清单与门禁表漂移没有机械护栏**，所以本节只列默认子集并指向 `gates.json`，不抄第二份列表。

**改 `code/unity/Assets/**`、或经 CLI 驱动 Unity Editor 之前**，先查 [危险点表](design/engineering/危险点表.md)（按**位置**检索的排障索引：这个位置反复出什么事、判据是什么、怎么躲）。⚠️ 该表覆盖 Unity 侧的坑，而 **`code/` 与根目录文档不在上述校验器的扫描范围内**——它的死链要人盯。

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
*创建: 2026-09-12 | 更新: 2026-09-17（[#190](https://github.com/verystrongdog/game/issues/190)：§三 自检清单补入 `issues-fixtures` 门禁——它此前不在清单里，导致 agent 侧自查全绿而 CI 恒红，实例 [#188](https://github.com/verystrongdog/game/issues/188)；同一段落的「改代码后跑第四条」按行号指错了命令（第四条其实是 issue 快照），改为**按名字对应**并指向 `gates.json`。触发 = #188 的 CI 红灯）*
*关联: [项目规约](design/conventions/README.md), [架构](ARCHITECTURE.md), [可玩状态](PLAYABLE.md), [工作流程](WORKFLOW.md), [协作指南](CONTRIBUTING.md)*
