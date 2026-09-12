# #123 [Grilling] Unity 沙盘角色动作集规格 — 动作受控词表 + 动画来源 + 引用契约

> 状态：关闭 · 创建 2026-09-07 · 关闭 2026-09-07
> 标签：维度:呈现, 维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/123

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

以 #122 呈现沙盘载体 + KiWalkerLab 已验证的 Humanoid+Animator 接入路线为基础，为沙盘角色定义**动作受控词表**（哪些命名动作、分哪些批次）、每动作的**动画来源**（现成引用 vs 制作 vs 程序化兜底）、以及**引用契约**（保持"简单动作引用"低复杂度高可信的映射架构）与**验证清单**（用户本机 Play + PlayMode 冒烟）。

**动机（用户原话要点）**：AI 仅在"简单的动作引用"上可信，复杂度一升可信度就降；故先把动作库做厚，之后功能只做简单引用；过程同时是用户学习 Unity 的路径。

**维度定位**：呈现（角色动作呈现，服务 反馈动画/状态面板/NPC 行为可视化 等空缺）+ 管线（动画资产接入/生成方式、资产与代码的版本管理）。

**依赖**：#122 Unity 呈现沙盘（✅ 已交付，本机验证中）；KI Humanoid 模型 + Animator 4 态（✅ KiWalkerLab 已验证）。

**阻塞解除对象**：呈现空缺「反馈动画」、呈现队列「状态面板细部规格」（间接）、管线 P6 Unity 项目结构、unity-brain-connect 神经→行为演示（接近/远离/警觉/冻结等）。

**边界（用户已确认）**：只定 词表/动画来源/引用契约/验证清单；**不含** 数值、UI 规格、特效与声音（留给「反馈动画方向」grilling）。

## 当前事实基线（已核验）

- 白盒动作词表 CharacterVisual.AnimKind = {Idle, Walk, PhysicalAttack, MentalAttack, Defend, HitReaction, Down}（CharacterVisual.cs:10）
- 驱动层实际调用（DemoCombatDriver.cs）：PlayWalk/PlayIdle（移动）、PlayActionFeedback(kind)（出招，含未命中/超射程）、PlayHitReaction()（目标受击）、PlayDown()（HP=0 倒下）、防御经 DemoActor.BeginDefend
- 已入库资产：Kevin Iglesias Human Animations 123 FBX（Idles/Movement 8向走跑冲刺转身含 RM/Jump/Fall/Social Talk01/Masked Poses）；Mixamo 手工导入 Sit To Stand + Stand To Sit + SitCheck.controller（用户实验）
- 缺口：物攻/精攻/防御/受击/倒下 五类战斗与反馈动作在现有资产中不存在 → 引用 vs 制作 的决策点
- 正典语义约束（term_registry + 基础行动设计.md）：物攻=M1 身体动作（出拳）；精攻=Broca 言语/凝视（**明确否定"发出精神波"**，动画不得做成发波手势）；防御=M1 运动抑制（护前姿态）

## 决策域（预排）

1. 动作受控词表：枚举与批次分层（落地集 vs 登记集）
2. 每动作动画来源矩阵（KI 引用 / Mixamo / 其他免费包 / 程序化兜底）+ 资产入库策略
3. 引用契约架构（状态机形态 / 命名动作→状态 1:1 / 受击打断 / 原地 vs RootMotion）
4. 载体形态（DemoSandbox 白盒换 Humanoid？动作展示场？）+ 接口统一（CharacterVisual 抽象化）
5. 实施批次与验证协议（PlayMode 断言 + 用户目视清单 + AI 自动化边界）

## 参照

- Issue #122（呈现沙盘，前置交付）
- unity/README.md §二·C（KiWalkerLab）
- unity-brain-connect/task-plan.md（下游行为演示，存档任务）

---

## 评论（2 条）

### verystrongdog · 2026-09-07

## ✅ Grilling #123 闭合 — 决策表

| # | 决策 | 摘要 |
|---|------|------|
| Q1 | 词表结构与范围 | 分层二维判定（Q-a 消费端就绪 × Q-b 来源就绪）→ L1 落地 / L2 登记 / 不入表；**12 词条**：L1=9 {Idle,Walk,Run,Jump,PhysicalAttack,MentalAttack,Defend,HitReaction,Down}，L2=3 {Sit,Stand,Talk}；不入表：逃跑/投降/借机、恐慌/警觉/冻结/随机行为、技能动画 |
| Q1b | 分类标签 | category ∈ {locomotion, combat, reaction, social, interaction, status} |
| Q2 | 内容形态 | 物攻=空手直拳；精攻主形态=A 前指宣言（B/C=变体候选）；防御=循环护前格挡；受击=单型通用；倒下=倒地停留 |
| Q2b | 来源矩阵 | Mixamo 优先 + 程序化兜底；source ∈ {KI引用, Mixamo引用, 程序化, 制作} |
| Q2c | 工作流/命名 | Mixamo 批量 zip → Humanoid 导入 → 资源名=词表 id；许可逐词条记录 |
| Q2d | 分工 | Editor 内操作全用户手动（学习目标）；AI 只产代码/文档/测试 |
| Q3 | 引用契约 | 形态 A：纯状态集 + 脚本 CrossFade（零参数零手动 transition）；升级触发器写入（连续混合/层分离/组合爆炸） |
| Q4 | 载体 | 新建 ActionLab + 可复用 ActionPlayer 组件；DemoSandbox 换真人 = 下游消费者 |
| Q5 | 实施批次 | Batch0 词表+ActionIds+ActionPlayer+PlayMode 断言 → Batch1 用户手动 → Batch2 手感收尾 |

**受影响文件**：unity/动作库规格.md（新建，正典规格位）、.scratch/grilling-123-action-vocabulary/决策记录.md（新建）、docs/决策树.md（#123 条目 + #122 推迟项注记）、docs/设计框架-六维状态.md（呈现 ✅ +1）、unity/README.md + 项目总览.md（入口）、memory（动作集-grilling-123.md）

**推迟清单**：ActionLab 实施（Batch 0-2）；DemoSandbox 换真人（反馈动画期）；精攻变体 B/C 与受击多态填充；词表 JSON 化；反馈动画方向 grilling（动作底子已备）

### verystrongdog · 2026-09-08

## 🔧 闭合后修正 (2026-09-08)

来源：[Grilling #124 ActionLab 动作填充尝试](https://github.com/verystrongdog/game/issues/124)（实施执行层闭合）。

| 项 | 原决策（#123） | 修正后 | 根因 |
|----|------|------|------|
| ActionLab 演示载体默认 | KI 真人模型（`Human_BasicMotionsDummy_M`，即 KiWalkerLab 载体） | **Mixamo X Bot（默认）/ Y Bot（备用）**；KI dummy 仅保留作 KiWalkerLab 对照场景 | 词表 12 条中 7 条动画来自 Mixamo；载体锚 Mixamo 侧 → 高风险接触动作（物攻/受击/倒下/坐立）全原生，仅 5 条 KI 通用动作 retarget（低风险） |
| 来源矩阵（5 条 L1 缺口） | PhysicalAttack=Mixamo Punching；MentalAttack=Mixamo Pointing（预测无合意 → 程序化兜底）；Defend=Mixamo Guard；HitReaction=Mixamo Getting Hit；Down=Mixamo Dying/Death | 实证映射（5 条已下载核验、无蒙皮）：PhysicalAttack=`Jab Cross`（直拳）；MentalAttack=`Charge`（伸手指人 = **A 前指宣言**，预测被推翻）；Defend=`Short Left Side Step`（循环格挡）；HitReaction=`Head Hit`；Down=`Dying` | 实际下载文件名 ≠ 语义：Charge 实为伸手指人、Short Left Side Step 实为循环格挡；精攻 A 形态获合意真 clip，程序化兜底降级为退路 |

词表结构（12 词条/分层）、契约 A、扩展协议、批次划分均不变。受影响文件：`unity/动作库规格.md`（🔧 注记 + §一载体 + §二来源列）、`docs/决策树.md`（#124 条目）、决策记录 #124。

---
*导出: 2026-09-12 | 来源: GitHub issue*
