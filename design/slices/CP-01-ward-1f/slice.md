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
| **角色动作呈现**（✏️ 2026-09-12 新增） | `ACCEPTED` | **`PARTIAL`** | `ISOLATED` | **`PASS`** | [动作库规格.md](../../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) 13 词表 + 契约 A+B；`ActionPlayer.cs` / `ActionCatalog.cs` 已入库。**缺口**（属 `Implementation`，非健康度问题）：L1 九条中仅 5 条有 clip（locomotion 四条引用仓库外 KI 资产）→ 干净检出下 4 态 clip 空；[动作系统分解](../../engineering/%E5%8A%A8%E4%BD%9C%E7%B3%BB%E7%BB%9F%E5%88%86%E8%A7%A3-2026-09-12.md) 为本轮 frontier。🔧 2026-09-13 回填：`Health` 原为 `REGRESSED`，判据写的是「PlayMode 2 项常红」——那两条是 `ActionPlayer` 的**纯逻辑缺陷**（非 clip 缺失），已于 2026-09-12 修复，`code/unity/README.md` §二·J 实测 **33/33 全过**，判据失效故改 `PASS`。⚠️ 花海 lab 移除后测试数 33→29 系**算术推断、未重跑**（该 README 页脚自述），故 `PASS` 的依据是移除前最后一次实测 |
| **就座交互（找椅子才能坐）**（✏️ 2026-09-13 新增） | `ACCEPTED` | **`DONE_FOR_SLICE`** | `ISOLATED` | **`PASS`** | [动作库规格.md](../../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) §四·丁：就座判定（距离 + 前侧 + 空闲）· 对齐段 · 占用锁 · 就座锚点 0.423 m 实测。实现已落地（`ChairSeat.cs` + 驱动层判定/对齐/根位移 + 10 项 PlayMode 断言；就座后臀部↔坐面 +4.8 mm），且 owner 目视清单 ⑧ **已通过**（试玩证据绑提交 `2b57b03`，见 `code/unity/README.md` §二·J 门禁实测末行）。🔧 2026-09-13 回填：本行原写「未 `DONE_FOR_SLICE`：owner 目视清单 ⑧ 未确认」——而 ⑧ 的记录提交 `ae33281` 当时**未回填本行**；该行自述的唯一缺口即 ⑧，故按证据判 `DONE_FOR_SLICE`（**此格为按行内判据的推导升级，非新增实现；若 owner 认为还有未记录的缺口，改回 `PARTIAL` 即可**） |
| **持椅交互（手里有东西）**（✏️ 2026-09-13 新增） | **`ACCEPTED`** | **`NONE`** | `ISOLATED` | `UNKNOWN` | [动作库规格.md](../../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) §四·戊（第七次修正）：词表 13→17 · **两条链可互切、双手链由 `Carry1H` 换握进入**（原 `Grab2H` 取消——Mixamo 无"双手拾取"素材）· `Variants` 字段 · 挂点三层（逐状态可握锚点 / 阻尼摆动 / "手到位帧"）· 副手 IK（仅格挡变体）· 派生件新增**镜像**。**设计侧 `ACCEPTED`**（18 条决策全部有实测读数支撑：7 条 Mixamo clip 归槽 + HUMOTO 参照量测）；**代码侧 `NONE`**（尚未实现）→ 故**非** `DONE_FOR_SLICE`。⚠️ 本项是**呈现探针**（`PLAYABLE.md` 当前 `NO_AUTHORIZED_PLAYABLE` → 不得新增正式玩家行为），规则层 §10.13 **不动** |
| 结束条件 | `UNRESOLVED` | `NONE` | `ISOLATED` | `UNKNOWN` | — |
| Unity 资产身份（`.meta`/ProjectSettings） | — | **`DONE_FOR_SLICE`** | `ISOLATED` | **`PASS`** | `code/unity/README.md` §二·H（#136 资产身份入库）+ `code/tools/validate_unity_assets.py`（#142 常驻校验：128 个受控 Unity 文件 / 58 个 `.meta` / 1 场景 / 1 controller，四条规则 0 违规）。🔧 2026-09-13 回填——本行原写「`.meta` 0 个、场景 0 个 → 阻塞 P4b」，与 #136 落地后的事实不符 |

**读法**：结算与资源**逻辑已真实可用**（Console 端 E2E）；但**呈现侧几乎全停在 `ISOLATED` 或 `NONE`**——这正是 M1/M2/M3 全部 `UNTESTED` 的原因。

## 三、假实现与临时捷径

| 位置 | 性质 | 替换条件 |
|---|---|---|
| `code/unity/Assets/Scripts/DemoSolver.cs` | 手抄 `CalibrationConfig.Default` 的结算常量（伤害 4 / 命中 0.75 / SAN 惩罚 1.3·2 / HP=san×0.5）。**后果**：凡改结算常量必须同时改它，否则 demo 与引擎静默分叉 | P4d 完成 Core→Unity 接缝后删除 |
| Unity 场景 | **已解除**：`Assets/Scenes/ActionLab.unity` 自 #136 起入库，为可打开的基准场景（`docs`：`code/unity/README.md` §二·H） | 🔧 2026-09-13 修正——本行原写「不入库，靠 Editor 菜单运行时生成」，该捷径已由 #136 消除；其余 lab 场景仍由 builder 菜单重建 |
| `code/unity/Assets/Kevin Iglesias/*` 引用 | 该资产包**不在仓库** → 干净检出下 `ActionLab.controller` 的 4 条 locomotion 态（Idle/Walk/Jump/Run）`m_Motion` 为**空（Missing）** | 要么入库、要么改为仓库内资产（工作面 = [#139](https://github.com/verystrongdog/game/issues/139)）。🔧 2026-09-13 更正：原文写「**导致 PlayMode 2 项失败**（locomotion clip 缺失）」——**因果关系是错的**，那两条是 `ActionPlayer` 的纯逻辑缺陷，落 5 条 clip 不会让它们转绿（`code/unity/README.md` §二·H 残留缺口 ② 有逐字否定）。现在这 4 条悬空引用由 `code/tools/validate_unity_assets.py` 的 A3 每次报出 |

## 四、阻塞项

| 阻塞 | 影响 | 解除条件 |
|---|---|---|
| ~~无 Unity Editor~~ → **已解除**（🔧 2026-09-13） | 原写「阻塞 P4b（资产身份）、P4d、P5」。实际：**本机就是那台 Windows 机**，经 WSL interop 可直驱 Editor（`code/unity/README.md` §二·G 实测；`gates.json` 的 `unity` 为 `available: true`）；P4b（资产身份）已由 **#136** 落地，并有 #142 的常驻校验兜住 | — 不适用 |
| P4d（Core→Unity 接缝）未定案 | 接缝实现无法开工 | [#135](https://github.com/verystrongdog/game/issues/135)（RFC：Q6b 桥接范围）出结论 |
| 切片未准入 | 不得新增正式玩家行为 | owner 在 [PLAYABLE.md](../../../PLAYABLE.md) 改为 `AUTHORIZED_PLAYABLE: CP-01` |

---
*创建: 2026-09-12 | 更新: 2026-09-13（🔧 四轴表与 §三/§四 回填：`Unity 资产身份` 行 `NONE`/`UNKNOWN` → `DONE_FOR_SLICE`/`PASS`（#136 + #142）；`就座交互` 行 ⑧ 已通过 → `DONE_FOR_SLICE`；`角色动作呈现` 行 `REGRESSED` 判据失效 → `PASS`；§三 KI 行因果更正；§四 「无 Unity Editor」阻塞解除并拆出 P4d 的真实前置 #135）*
*关联: [PLAYABLE.md](../../../PLAYABLE.md), [WORKFLOW.md](../../../WORKFLOW.md), [架构](../../../ARCHITECTURE.md), [六维状态](../../framework/six-dimensions.md)*
