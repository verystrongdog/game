# #122 [Grilling] Unity 呈现验证骨架 — 可控角色 + 指令→动作→UI 反馈最小闭环

> 状态：关闭 · 创建 2026-09-06 · 关闭 2026-09-06
> 标签：维度:呈现, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/122

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题
呈现维度的可运行起点：Unity 工程骨架 + 单场景演示——**Unity 界面上可见的角色模型，能接收"当前可实现"的指令并作出相应动作，使 UI 调试获得真实反馈**。

## 六维定位
- **呈现**（主线）：玩家感知/操作的可运行载体——状态面板细部规格 grilling 的原型底子（该 grilling 本会话已挂起，等待本骨架）
- **管线**（工程）：Unity 工程搭建（六维状态 管线空缺 "Unity项目搭建"，P6 批次 5.4；引擎核 `src/YouAreNotTheFish.Core` 294/294+ 测试绿，Unity 工程待搭建）

## 当前状态
- 用户裁定：无可见可控角色前，纯纸面 UI 规格不可调试（本会话 状态面板细部规格 话题挂起）
- `.scratch/unity-brain-connect/task-plan.md`（2026-08-16 规划存档，暂不实施）：其阶段 0.1 "Unity 工程建立 + Core 引入" 与本话题同源；目标不同（它为神经→行为演示）——本话题聚焦"可控角色→动作→UI 反馈"，神经驱动演示保持存档
- `.gitignore` 已预留 Unity 规则；`规则/技能树系统/引擎数据关系规格.md` §六 Unity 接缝已标注（Engine 层可整体引用 ✅ / 回合驱动 🔶 / 视觉动画不入数值路径 ✅）
- 环境约束：本沙箱无 Unity Editor——产出 = 工程骨架 + C# 脚本 + 搭建/验证指引，用户本地 Unity Editor 运行验证

## 待裁决（Step 3 逐题）
范围内容 / 角色形态 / 数值源（白盒 stub vs 引擎核直连）/ UI 反馈集 / Unity 版本与目录 / 分支与提交策略

---

## 评论（1 条）

### verystrongdog · 2026-09-06

## ✅ 关闭总结 — Unity 呈现沙盘（Grilling #122）

### 决策表
| # | 决策 | 内容 |
|---|------|------|
| D1 | 载体与范围 | `unity/` 工程骨架 + 白盒演示场；移动+基础行动 1/2/3；不含回合全量/网格/敌方AI/脑区3D |
| D2 | 结算驱动 | 轻量手动回合沙盘（玩家 M1+Broca → 陪练 AI → 行动窗口口径冷却/防御）；不触碰 TurnManager |
| D3 | 版本/目录 | Unity 6 (6000.0.83f1)；`unity/` |
| D4/D5 | 角色模型 | 白盒人形+程序化动作；`CharacterVisual` 为外部模型接入点 |
| D6 | 引擎消费 ⏸ | Q6b 挂起：netstandard2.1 兼容墙（ThrowIfNull 71处）— 子集 vs 全量待定；现 WhiteboxSolver 镜像引擎值 |
| D7 | UI 集 | uGUI：状态面板(HP/SAN/防御/CD) + 行动栏 + 日志；陪练数值=调试显示；无 AP |
| 验证环境 | — | 沙箱 Personal 激活死锁（无钥匙串）→ 用户本机（Windows unity-cli 登录 ✅） |

### 受影响文件
- `unity/` 新工程（8 运行时脚本 + SceneBuilder + PlayMode 测试 2 例 + README）— commit `c6e1f8c`
- `.gitignore`、`docs/决策树.md`、`docs/设计框架-六维状态.md`、`.scratch/grilling-122-unity-slice/决策记录.md` — commit `46dcec8`
- memory `unity-呈现沙盘-grilling-122.md`

### 写入验证
✅ 决策记录/决策树/六维状态/README 已写；⚠️ Unity 脚本编译与 PlayMode 测试需本机验证（沙箱无许可）

### 推迟清单
Q6b 桥接范围 → EngineSolver；状态面板细部规格 grilling（沙盘为底）；外部模型接入；unity-brain-connect 神经演示

### 本机验证步骤
打开 `unity/`（Unity 6）→ 菜单 YANTF → 创建 Demo 场景 → Play；或 PlayMode Test Runner 跑 2 冒烟测试；可选 unity-cli pipeline 自动化

---
*导出: 2026-09-12 | 来源: GitHub issue*
