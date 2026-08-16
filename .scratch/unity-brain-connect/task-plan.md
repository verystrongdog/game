# [Unity 接入] Unity 引入引擎创建人物——任务规划（存档）

> **状态：规划存档，暂不实施。** 触发条件：在另一工作区学会用 Unity 简单创建模型并接入引擎后，再回到本任务开始执行。
> 本文件是任务起点，实施时应据此从 `main` 开 `feat/unity-brain-connect` 分支逐条推进。

---

## 一、目标

新建一个 **Unity 3D 工程（位于本仓库内，与仓库一致）**，把 `src/YouAreNotTheFish.Core` 引擎作为**纯类库**引入，驱动一个**通用演示角色**的「神经 → 行为」闭环：角色能感知环境、神经模型实时演化、脑区激活驱动其基础行为（接近 / 远离 / 静止 / 警觉 / 冻结等）。

**本期只做阶段 0 / 1**，并**存档阶段 2 的规划**（不实施）。

---

## 二、引擎能力现状盘点（规划依据）

> 事实性引用均已在对话中通过读源文件核实。引擎 = `src/YouAreNotTheFish.Core`（纯 .NET 类库，**零 UnityEngine 依赖**）。

### 已具备（神经层面，强项）
| 能力 | 位置 | 说明 |
|------|------|------|
| 脑活动快照 | `ParticipantState` | 91 浮点：69 WC 激活 + 4 tone + 15 Gurney + 3 gate |
| 神经演化 | `Engine/WcDynamics.cs` | `Step(a,b,s,w)` 让 69 脑区随信号演化（Δ=1s，同步更新，纯函数） |
| 事件→神经输入 | `Engine/EventProcessor.cs` | 战斗事件 → δ + 69 维感官 s（= W_sensory×α） |
| 脑干调质+门控 | `Engine/ToneUpdater.cs` `CstcGating.cs` `CorticalBias.cs` | tone 更新、CSTC 门控/salience、皮层偏置 |
| 从神经到行为 | `Engine/NpcSalience.cs`、`SpeedScoreCalculator.cs`、`TurnOrderBuilder.cs` | 战斗版 3 行动 salience 选择 + 速度排序 |
| 威胁判断 | `Engine/ThreatJudge.cs`（本轮新增） | 读 PAG/杏仁核 → 威胁评分/恐慌/索敌优先级 |

### 关键缺口（本期要填 / 阶段 2 要扩展）
1. **时间骨架是「回合制 + 战斗场景」**：`TurnManager` 五阶段管线（Phase 1~5）把引擎钉死在回合战斗。自由走动人物需要**节拍驱动（非回合）**入口。
2. **行为库只有 3 个战斗行动**：无移动/探索/社交等非战斗基础行为。
3. **感官输入有限**：仅 6 模态（visual/auditory/somatosensory/pain/social_cognition/language_cognition）；且 `W_sensory.json` 中 PAG/Amygdala/SuperiorColliculus 三敌区**感官行目前全为 0**（威胁主要靠脑区内部网络传导，需决定是否补直接通路）。
4. **无长期状态**：无记忆/经历、无性格配置、无跨场景关系状态（阶段 2）。

---

## 三、阶段 0 · 硬接入（地基）

> 目标：空场景 + 1 角色，引擎以节拍驱动（不经回合）跑起来，能打印角色实时神经状态。

| # | 任务 | 产出 |
|---|------|------|
| 0.1 | 新建 Unity 3D 工程（仓库内），引入 `YouAreNotTheFish.Core.dll` | Unity 工程脚手架 |
| 0.2 | 引擎新增节拍驱动入口 `Engine/BrainDriver.cs`（独立于 TurnManager）：`Step(sensation[], state) → nextState`，单步演化 WC+Tone+Gurney+CSTC | 新文件 + 单测 |
| 0.3 | Unity 适配层：`MonoBehaviour` 固定节拍（如 10Hz）调 BrainDriver，`[SerializeField]` 暴露参数，Debug.Log 打印 PAG/杏仁核/威胁/恐慌 | Unity 脚本 |
| 0.4 | Unity 侧加载 `data/`（brain_regions / W_sensory / …）生成 `GameData` | 数据加载脚本 |
| **验收** | 场景角色神经在 tick，控制台可打印当前神经状态 | — |

---

## 四、阶段 1 · 行为闭环

> 目标：脑区激活 → 基础行为倾向，角色在场景中基于神经状态移动/静止/远离/靠近。

| # | 任务 | 产出 |
|---|------|------|
| 1.1 | 定义行为映射：脑区激活 + salience → 非战斗基础行为候选（来源：`规则/技能树系统/脑功能层级模型.md` L0 基础行动：逃离/趋近/警觉/冻结…） | 新 `Engine/BehaviorMappings` 或数据文件 |
| 1.2 | 感官填充：Unity 感知（物体距离/朝向/威胁源）→ 填 6 模态 `s`；决策是否补 PAG/杏仁核/上丘的直接感官通路 | Unity 感知脚本 + 可选数据补充 |
| 1.3 | 行为选择器（非战斗 salience）+ 移动驱动（NavMeshAgent 或 transform） | Unity 行为脚本 |
| 1.4 | 威胁闭环：复用 `ThreatJudge` 读威胁/恐慌 → 触发逃离/僵住 | 复用已写组件 |
| **验收** | 角色根据环境"自己决定"靠近/远离/静止，行为变化可观察可控 | — |

---

## 五、阶段 2 · 数据与结构扩展（⚠️ 仅存档规划，不实施）

> 待阶段 0/1 跑通后，以此为依据扩展。列出的扩展点是已知方向，具体参数/结构需届时 grilling 校准。

- **新增数据文件**：
  - `person_profiles.json`：人物配置（性格特征 → 各脑区阈值/权重偏置）
  - 行为映射表（脑区 → 行为倾向）
  - 记忆/经历状态（杏仁核条件化需要"见过什么"）
- **结构新增**：
  - 长期状态类型（跨场景）、Person/Actor 配置类型
  - 关系状态（阶段 3：社会认知输入）
  - 自由度更高的感官/感知数据（从"战斗事件"扩为"自由世界感知"）
- **数据补齐候选**：
  - `W_sensory.json` 中威胁脑区（PAG/杏仁核/上丘）直接感官通路——当前为 0

---

## 六、风险与注意

1. **不要先补阶段 2 再接入**：先跑通 0/1，避免在未验证接入时过度设计（对齐决策 B）。
2. **引擎保持零 Unity 依赖**：核心库继续纯函数、可单测；Unity 只在适配层引用 DLL。
3. **感官缺口**（威胁脑区 0 通路）在 1.2 明确决策。
4. **分离「回合战斗管线」与「自由节拍驱动」**：新增的 BrainDriver 不改动/破坏现有 TurnManager（已过 309 项测试的存量逻辑不动）。

---

*创建: 2026-08-16 | 更新: 2026-08-16*
*关联: [src/YouAreNotTheFish.Core](../../src/YouAreNotTheFish.Core), [脑功能层级模型](../../规则/技能树系统/脑功能层级模型.md), [角色与面具](../../实体/角色与面具.md)*
