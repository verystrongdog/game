# CP-01 — 住院楼 1F（候选切片）

> **状态：`CANDIDATE — 未经 owner 准入`**。准入状态记录在 [PLAYABLE.md](../../../PLAYABLE.md)。未经准入前，本切片只能用于**限制基础设施范围**，不能授权新增玩家行为。

## 一、切片合同

### 1.1 玩家路径

```
夜间病房醒来
  → 进入短走廊
  → 遭遇一个同时具有 HP/SAN 的敌对实体
  → 使用真实 Core 完成物理攻击、防御、精神攻击
  → 到达护士站并结束切片
```

### 1.2 must-prove

| # | 断言 | 试玩状态 |
|---|---|---|
| M1 | Unity 能通过**适配层使用真实 Core**完成一次战斗闭环（不是白盒手抄常量） | `UNTESTED` |
| M2 | 玩家能从 HUD 与反馈中**区分 HP / SAN 与三种基础行动的后果** | `UNTESTED` |
| M3 | 探索、接敌、回合战斗与结束条件能形成**连续体验** | `UNTESTED` |

### 1.3 明确排除

完整技能树 · 完整 NPC AI · Boss · 月相全系统 · 完整叙事 · 多角色 · 美术精修。

## 二、消费能力的四轴状态

> 状态定义见 [WORKFLOW.md §二](../../../WORKFLOW.md)。**四轴不得混为"已完成"。**

| 能力 | Design | Implementation | Integration | Health | 证据 |
|---|---|---|---|---|---|
| 回合结算（物理/精神攻击/防御） | `ACCEPTED` | `DONE_FOR_SLICE` | Console `E2E` · Unity `ISOLATED` | `PASS` | [design/rules/核心机制.md](../../rules) §4；`code/src/.../Engine/` + 353 测试 |
| 敌方 HP / SAN 双资源 | `ACCEPTED` | `DONE_FOR_SLICE` | 同上 | `PASS` | [design/entities/敌人与事件.md](../../entities) §4.1 权威表（轻度病人 HP 20-30 / SAN 50-70） |
| 基础行动（物攻/精攻/防御） | `ACCEPTED` | `DONE_FOR_SLICE` | 同上 | `PASS` | [design/rules/skill-tree/operations/](../../rules/skill-tree/operations/) §二/§三 |
| 速度排序 / 响应窗口 | `ACCEPTED` | `DONE_FOR_SLICE` | 同上 | `PASS` | [design/rules/回合战斗流程.md](../../rules) §三/§六 |
| **Core → Unity 适配层** | `ACCEPTED` | **`FAKE`** | `ISOLATED` | `UNKNOWN` | `code/unity/Assets/Scripts/DemoSolver.cs` 手抄 `CalibrationConfig` 常量，自述"待 EngineSolver 替换"——见 [ARCHITECTURE.md §四](../../../ARCHITECTURE.md) |
| **探索与接敌** | **`UNRESOLVED`** | `NONE` | `ISOLATED` | `UNKNOWN` | 无空间切片设计；Unity 场景靠 Editor 菜单运行时生成 |
| **HUD 与反馈** | `ACCEPTED` | **`NONE`** | `ISOLATED` | `UNKNOWN` | [design/presentation/战斗界面布局.md](../../presentation) 有 37 项决策，但 Unity 侧未实现 |
| **角色动作呈现**（✏️ 2026-09-12 新增） | `ACCEPTED` | **`PARTIAL`** | `ISOLATED` | **`REGRESSED`** | [动作库规格.md](../../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) 12 词表 + 契约 A+B；`ActionPlayer.cs` / `ActionCatalog.cs` 已入库。**缺口**：L1 九条中仅 5 条有 clip（locomotion 四条引用仓库外 KI 资产）→ PlayMode 2 项常红（健康度 `REGRESSED` 的判据）；[动作系统分解](../../engineering/%E5%8A%A8%E4%BD%9C%E7%B3%BB%E7%BB%9F%E5%88%86%E8%A7%A3-2026-09-12.md) 为本轮 frontier |
| 结束条件 | `UNRESOLVED` | `NONE` | `ISOLATED` | `UNKNOWN` | — |
| Unity 资产身份（`.meta`/ProjectSettings） | — | **`NONE`** | `ISOLATED` | `UNKNOWN` | `.meta` 0 个、场景 0 个 → 阻塞 P4b |

**读法**：结算与资源**逻辑已真实可用**（Console 端 E2E）；但**呈现侧几乎全停在 `ISOLATED` 或 `NONE`**——这正是 M1/M2/M3 全部 `UNTESTED` 的原因。

## 三、假实现与临时捷径

| 位置 | 性质 | 替换条件 |
|---|---|---|
| `code/unity/Assets/Scripts/DemoSolver.cs` | 手抄 `CalibrationConfig.Default` 的结算常量（伤害 4 / 命中 0.75 / SAN 惩罚 1.3·2 / HP=san×0.5）。**后果**：凡改结算常量必须同时改它，否则 demo 与引擎静默分叉 | P4d 完成 Core→Unity 接缝后删除 |
| Unity 场景 | 不入库，靠 Editor 菜单运行时生成 | P4b 建立资产身份后改为提交场景 |
| `code/unity/Assets/Kevin Iglesias/*` 引用 | 该资产包**不在仓库**，导致 PlayMode 2 项失败（locomotion clip 缺失） | 要么入库、要么改为仓库内资产 |

## 四、阻塞项

| 阻塞 | 影响 | 解除条件 |
|---|---|---|
| 无 Unity Editor（本环境 `NOT_AVAILABLE`） | 阻塞 P4b（资产身份）、P4d（Core→Unity 接缝）、P5（实现与试玩） | 在有 Unity 的机器上执行；或 owner 指定替代验证方式 |
| 切片未准入 | 不得新增正式玩家行为 | owner 在 [PLAYABLE.md](../../../PLAYABLE.md) 改为 `AUTHORIZED_PLAYABLE: CP-01` |

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [PLAYABLE.md](../../../PLAYABLE.md), [WORKFLOW.md](../../../WORKFLOW.md), [架构](../../../ARCHITECTURE.md), [六维状态](../../framework/six-dimensions.md)*
