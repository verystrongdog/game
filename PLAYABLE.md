# 当前可玩状态

> 本仓库**唯一的 current playable 声明**。任何"做完了"的说法都必须在这里有对应条目，否则不算交付。

---

## 状态

```
NO_AUTHORIZED_PLAYABLE
```

**本仓库当前没有被 owner 正式准入的可玩切片。** 记录于 2026-09-12。

未准入期间：**可以继续仓库维护与 bootstrap 工作（校验器、数据契约、构建链），但不得新增正式玩家行为。**

---

## 已存在但未准入的运行载体

这些能跑，但它们是**技术验证载体**，不是产品切片——不得据此宣称"游戏可玩"。

| 载体 | 是什么 | 缺口 |
|---|---|---|
| `code/src/YouAreNotTheFish.Console` | .NET 控制台 harness。真实 Core 的回合结算跑通（`--seed` / `--demo-situation` / `--trace-resting` 等） | 无图形、无玩家输入、无探索与接敌 |
| `code/unity/` 的 Editor 菜单场景生成器 | 6 个 builder（`SceneBuilder` / `ActionLabBuilder` / `WalkerLabBuilder` / `KiWalkerLabBuilder` / `RoseFieldLabBuilder` / `MixamoSetup`），运行时生成场景 | **场景与 `.meta` 均不入库**——必须先在 Editor 里手动跑菜单才能得到场景；且 `DemoSolver.cs` 走的是**手抄常量的白盒结算**，不是真实 Core（见 [ARCHITECTURE.md §四](ARCHITECTURE.md)） |
| `code/sim/`（15 个 Python 脚本） | 数值模拟与验证实验 | 研究产物，**不入游戏正典** |

## 候选切片（待 owner 准入）

### CP-01 候选：住院楼 1F

```
夜间病房醒来
  → 进入短走廊
  → 遭遇一个同时具有 HP/SAN 的敌对实体
  → 使用真实 Core 完成物理攻击、防御、精神攻击
  → 到达护士站并结束切片
```

**must-prove（三条，缺一不可）**

1. Unity 能通过**适配层使用真实 Core**完成一次战斗闭环（不是白盒手抄）
2. 玩家能从 HUD 和反馈中**区分 HP/SAN 与三种基础行动的后果**
3. 探索、接敌、回合战斗与结束条件能形成**连续体验**

**明确排除**：完整技能树 · 完整 NPC AI · Boss · 月相全系统 · 完整叙事 · 多角色 · 美术精修。

**当前状态**：`CANDIDATE — 未经 owner 准入`。准入前它只能用于**限制基础设施范围**，不能授权新增玩家行为。

---

## 准入 / 更换流程

1. Owner 在此文件把状态改为 `AUTHORIZED_PLAYABLE: <slice-id>`，或指定另一 Slice 替换候选
2. 在 `design/slices/<slice-id>/` 建立 `slice.md`（切片合同 + 四轴状态）与 `playtest.md`（绑定 build 的试玩证据）
3. 四轴状态：**设计声明 / 代码实现 / 系统集成 / 试玩证据**——四者不得混为"已完成"
4. 切片完成的判据是**玩家能从入口走到出口且 must-prove 有试玩证据**，不是"代码写完"或"文档写完"

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [AGENTS.md](AGENTS.md), [架构](ARCHITECTURE.md), [工作流程](WORKFLOW.md), [设计总览](design/README.md)*
