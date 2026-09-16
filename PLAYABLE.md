# 当前可玩状态

> 本仓库**唯一的 current playable 声明**。任何"做完了"的说法都必须在这里有对应条目，否则不算交付。

---

## 状态

```
NO_AUTHORIZED_PLAYABLE
```

**本仓库当前没有被 owner 正式准入的可玩切片。** 记录于 2026-09-12。

未准入期间：**可以继续仓库维护与 bootstrap 工作（校验器、数据契约、构建链），但不得新增正式玩家行为。**

> 🔧 **2026-09-16（[#181](https://github.com/verystrongdog/game/issues/181) 选项 A）**：产品定位已裁定为**叙事驱动的心理 CRPG**（主循环 = 对话 / 调查 / 认知检定 / 承诺·线索·自问；回合战斗为**并列解决路径之一**）。**准入状态不变**——本文件仍是 `NO_AUTHORIZED_PLAYABLE`，候选切片 CP-01 的合同已按新定位重写（见下）。

---

## 已存在但未准入的运行载体

这些能跑，但它们是**技术验证载体**，不是产品切片——不得据此宣称"游戏可玩"。

| 载体 | 是什么 | 缺口 |
|---|---|---|
| `code/src/YouAreNotTheFish.Console` | .NET 控制台 harness。真实 Core 的回合结算跑通（`--seed` / `--demo-situation` / `--trace-resting` 等） | 无图形、无玩家输入、无探索与接敌 |
| `code/unity/` 的 Editor 菜单场景生成器 | 5 个 builder（`ActionLabBuilder` / `WalkerLabBuilder` / `KiWalkerLabBuilder` / `MixamoSetup` / `BrainViewLabBuilder`），运行时生成场景 | **场景与 `.meta` 均不入库**（`ActionLab` 是唯一例外，见 [code/unity/README.md §二·H](code/unity/README.md)）——必须先在 Editor 里手动跑菜单才能得到场景。🔧 2026-09-13：白盒 Demo 沙盘那套（`SceneBuilder` + `DemoSolver.cs` 手抄常量）已按 owner 裁定**整体退役**（[#155](https://github.com/verystrongdog/game/issues/155)），故本条不再有「不是真实 Core」的例外 |
| `code/sim/`（15 个 Python 脚本） | 数值模拟与验证实验 | 研究产物，**不入游戏正典** |

## 候选切片（待 owner 准入）

### CP-01 候选：住院楼 1F

> 🔧 **2026-09-16 重写（[#181](https://github.com/verystrongdog/game/issues/181) 选项 A）**：owner 裁定定位为**叙事驱动的心理 CRPG** 后，CP-01 **保留**为候选切片（不标 `SUPERSEDED`），合同按叙事优先**重写**——原合同以强制战斗闭环为 must-prove 并排除完整叙事。合同正本见 [design/slices/CP-01-ward-1f/slice.md](design/slices/CP-01-ward-1f/slice.md)。

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

**当前状态**：`CANDIDATE — 未经 owner 准入`。准入前它只能用于**限制基础设施范围**，不能授权新增玩家行为。⚠️ M1 的前置（叙事解释器 `StoryEngine`）**尚未实现**，故本切片当前**不具备闭合条件**。

---

## 准入 / 更换流程

1. Owner 在此文件把状态改为 `AUTHORIZED_PLAYABLE: <slice-id>`，或指定另一 Slice 替换候选
2. 在 `design/slices/<slice-id>/` 建立 `slice.md`（切片合同 + 四轴状态）与 `playtest.md`（绑定 build 的试玩证据）
3. 四轴状态：**设计声明 / 代码实现 / 系统集成 / 试玩证据**——四者不得混为"已完成"
4. 切片完成的判据是**玩家能从入口走到出口且 must-prove 有试玩证据**，不是"代码写完"或"文档写完"

---
*创建: 2026-09-12 | 更新: 2026-09-16（定位裁定为叙事驱动的心理 CRPG · CP-01 合同按 [#181](https://github.com/verystrongdog/game/issues/181) 选项 A 重写；准入状态不变）*
*关联: [AGENTS.md](AGENTS.md), [架构](ARCHITECTURE.md), [工作流程](WORKFLOW.md), [设计总览](design/README.md)*
