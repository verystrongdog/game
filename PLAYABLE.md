# 当前可玩状态

> 本仓库**唯一的 current playable 声明**。任何"做完了"的说法都必须在这里有对应条目，否则不算交付。

---

## 状态

```
AUTHORIZED_PLAYABLE: CP-01
```

**owner 于 2026-09-16 正式准入 CP-01（住院楼 1F）为当前可玩切片**，同日落定 [#181](https://github.com/verystrongdog/game/issues/181) 选项 A（叙事驱动的心理 CRPG）⇒ CP-01 的合同按**叙事优先重写**（见下）。准入记录于 2026-09-16。

准入期间：**可以新增正式玩家行为**，但必须落在本切片合同（[design/slices/CP-01-ward-1f/slice.md](design/slices/CP-01-ward-1f/slice.md)）声明的范围内；依赖方向（`design → data → code → unity`）与 [WORKFLOW.md §一](WORKFLOW.md) 的单线程约束不变。

> ⚠️ **准入 ≠ 可玩**：本切片当前**没有任何试玩证据**（M1–M3 全部 `UNTESTED`），且 M1 的实现前置——叙事解释器 `StoryEngine` 与 `data/story/` 数据契约——**尚未建立**（[剧情系统设计 §六](design/events/剧情系统设计.md) 待办）。完成判据仍是本文件 §准入/更换流程 第 4 条：**玩家能从入口走到出口且有试玩证据**。

---

## 已存在的技术验证载体（不等同切片）

这些能跑，但它们是**技术验证载体**，不是产品切片——不得据此宣称"游戏可玩"。

| 载体 | 是什么 | 缺口 |
|---|---|---|
| `code/src/YouAreNotTheFish.Console` | .NET 控制台 harness。真实 Core 的回合结算跑通（`--seed` / `--demo-situation` / `--trace-resting` 等） | 无图形、无玩家输入、无探索与接敌 |
| `code/unity/` 的 Editor 菜单场景生成器 | 5 个 builder（`ActionLabBuilder` / `WalkerLabBuilder` / `KiWalkerLabBuilder` / `MixamoSetup` / `BrainViewLabBuilder`），运行时生成场景 | **场景与 `.meta` 均不入库**（`ActionLab` 是唯一例外，见 [code/unity/README.md §二·H](code/unity/README.md)）——必须先在 Editor 里手动跑菜单才能得到场景。🔧 2026-09-13：白盒 Demo 沙盘那套（`SceneBuilder` + `DemoSolver.cs` 手抄常量）已按 owner 裁定**整体退役**（[#155](https://github.com/verystrongdog/game/issues/155)），故本条不再有「不是真实 Core」的例外 |
| `code/sim/`（15 个 Python 脚本） | 数值模拟与验证实验 | 研究产物，**不入游戏正典** |

## 当前切片（owner 已准入）

### CP-01：住院楼 1F

> 🔧 **2026-09-16**：owner 准入为当前可玩切片（本条上方 `状态`），并同日按 [#181](https://github.com/verystrongdog/game/issues/181) 选项 A **重写合同为叙事优先**——原合同以强制战斗闭环为 must-prove 并排除完整叙事。合同正本见 [design/slices/CP-01-ward-1f/slice.md](design/slices/CP-01-ward-1f/slice.md)，试玩证据位见 [playtest.md](design/slices/CP-01-ward-1f/playtest.md)。

```
夜间病房醒来
  → 进入短走廊：与 1F NPC 对话、观察环境拿到线索
  → 线索写进笔记本（承诺层 / 线索层）
  → 遭遇一个同时具有 HP/SAN 的敌对实体
  → 用对话 / 认知检定 / 回合战斗中的任一路径解决该冲突
  → 选择产生可观察后果（关系 / 世界状态 / 感知版本 / 空间访问 / 自问）
  → 到达护士站并结束切片
```

**must-prove（三条，缺一不可）**

1. Unity 能通过**适配层使用真实 Core**完成一次**叙事闭环**（对话节点求值 → 选择效果写回 `Q/R/F/W` → 笔记本可见），不是白盒手抄常量
2. 玩家能从 HUD 与笔记本反馈中**区分战斗路径（HP/SAN/三种基础行动）与非战斗路径（关系/世界状态/自问）的后果**
3. 探索、接敌、**解决（含不进入战斗的路径）**与结束条件能形成**连续体验**

**明确排除**：完整技能树 · 完整 NPC AI · Boss · 月相全系统 · **完整主线与全量 NPC 素材**（叙事内容按 1F 生态最小集）· 多角色 · 美术精修。

**当前状态**：`AUTHORIZED — owner 2026-09-16 准入`。可新增**落在本合同范围内**的正式玩家行为。⚠️ M1 的前置（叙事解释器 `StoryEngine` + `data/story/` 契约）**尚未实现**，故本切片当前**不具备闭合条件**；四轴状态见切片合同 §二，试玩证据逐条记在 `playtest.md`（现全 `UNTESTED`）。

---

## 准入 / 更换流程

1. Owner 在此文件把状态改为 `AUTHORIZED_PLAYABLE: <slice-id>`，或指定另一 Slice 替换当前切片（🔧 2026-09-16 已执行：`AUTHORIZED_PLAYABLE: CP-01`，[#181](https://github.com/verystrongdog/game/issues/181)）
2. 在 `design/slices/<slice-id>/` 建立 `slice.md`（切片合同 + 四轴状态）与 `playtest.md`（绑定 build 的试玩证据）
3. 四轴状态：**设计声明 / 代码实现 / 系统集成 / 试玩证据**——四者不得混为"已完成"
4. 切片完成的判据是**玩家能从入口走到出口且 must-prove 有试玩证据**，不是"代码写完"或"文档写完"

---
*创建: 2026-09-12 | 更新: 2026-09-16（**owner 准入 CP-01** = `AUTHORIZED_PLAYABLE: CP-01`，同日落定 [#181](https://github.com/verystrongdog/game/issues/181) 选项 A「叙事驱动的心理 CRPG」并按叙事优先重写切片合同）*
*关联: [AGENTS.md](AGENTS.md), [架构](ARCHITECTURE.md), [工作流程](WORKFLOW.md), [设计总览](design/README.md)*
