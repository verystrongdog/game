# 子非鱼 — You Are Not the Fish

> 以神经科学为骨架、以「意识外显效应」为世界观的 3D 回合制心理对抗游戏设计项目。**设计文档是 primary artifact**；`code/` 是验证与实现工具。

## 目录

1. [这是什么](#这是什么)
2. [仓库导航](#仓库导航)
3. [从哪里开始读](#从哪里开始读)
4. [维护约定](#维护约定)

## 这是什么

游戏 = 规则 × 实体 × 空间 × 事件，通过**呈现**交付，由**管线**生产。设计文档按此六维组织。

**当前阶段**：纸面设计 + 数值模拟验证 + 引擎核心实施（战斗 / 情境 / NPC salience 已跑通，技能树与实体系统按 P 系列批次推进）。实时状态见 [设计框架-六维状态](design/framework/six-dimensions.md)。

## 仓库导航

| 路径 | 内容 |
|------|------|
| [`design/`](design/README.md) | **设计文档（正典，primary artifact）** |
| [`design/rules/`](design/rules) | 核心机制（脑区链路 / 战斗结算 / SAN）、回合流程、技能树系统、时空结构数学框架 |
| [`design/entities/`](design/entities) | 角色与面具、敌人与事件、疾病目录、武器装备、消耗品 |
| [`design/space/`](design/space) | 三层空间模型、关卡设计、治疗中心建模 |
| [`design/events/`](design/events) | 游戏循环、世界观与叙事、任务 / 剧情 / 奖励系统、NPC 人生生成器 |
| [`design/presentation/`](design/presentation) | 战斗界面布局、动作库规格、3D 可视化（规范 + HTML 原型 + Blender 资产） |
| [`design/pipeline/`](design/pipeline) | 预烘焙管线（已废弃）、引擎实施路线图 |
| [`design/spec/`](design/spec/README.md) | 实现规格与输入素材：C# 子系统规格 / NPC 起草素材 / 特征数据源 |
| [`design/framework/`](design/framework) | 六维状态路由表 + 六维度索引 |
| [`design/decisions/`](design/decisions/README.md) | 决策树——93 个条目的设计决策分叉记录 |
| [`design/conventions/`](design/conventions/README.md) | 项目规约、写作与引用规范、agent 工作流文档 |
| [`design/archive/`](design/archive) | 归档：`grilling/`（各轮源记录 + 122 issue 存档）· `trash/`（垃圾箱） |
| [`reference/`](reference) | 文献、书籍、灵感收件箱；`deprecated/` 保留已废弃子系统为参考数据源 |
| [`code/src/`](code/src) | C# 逻辑引擎（.NET 8 库 + Console harness + 353 个测试） |
| [`code/unity/`](code/unity) | Unity 6 呈现沙盘工程 |
| [`code/sim/`](code/sim) | Python 数值模拟验证脚本 |
| [`code/tools/`](code/tools) | 校验器（`validate_*.py`）与数据生成工具 |
| [`data/`](data/README.md) | 结构化数据契约：脑区、三体神经模型、情境原型、病理边、术语注册表 |

## 从哪里开始读

| 你想知道 | 去哪 |
|---|---|
| 这个游戏现在设计到哪一步了 | [设计框架-六维状态](design/framework/six-dimensions.md) |
| 某个机制怎么结算 | [design/rules/核心机制.md](design/rules) |
| 某个设计为什么这么定 | [决策树](design/decisions/README.md) → 对应轮的[源记录](design/archive/grilling/) |
| 某个名词在这个项目里是什么意思 | [`data/term_registry.json`](data/term_registry.json)（看 `status` 字段——很多常规词汇在本项目里是**已废弃**的旧模型） |
| 写文档/改设计要守什么规矩 | [项目规约](design/conventions/README.md) · [写作与引用规范](design/conventions/writing-and-references.md) |
| 怎么提交 | [协作指南](CONTRIBUTING.md) |
| 代码和设计之间的边界在哪 | [架构声明](ARCHITECTURE.md) |

## 维护约定

- **设计驱动代码**：先有设计文档，再写代码。边界见 [项目规约 §一](design/conventions/README.md)
- **改动后跑校验**：`python3 code/tools/validate_cross_refs.py` 报 0 死链、`dotnet test code/src/YouAreNotTheFish.sln` 全绿，是提交前的底线
- **过程物不入库**：外部 AI 会话存档、书籍全文、运行日志、模拟结果由 `.gitignore` 排除，磁盘保留
- **Git**：提交信息用中文，`类型: 描述`；按主题小步提交

---
*创建: 2026-09-06 | 更新: 2026-09-12（仓库重构后重写导航）*
*关联: [设计总览](design/README.md), [项目规约](design/conventions/README.md), [协作指南](CONTRIBUTING.md), [六维状态](design/framework/six-dimensions.md)*
