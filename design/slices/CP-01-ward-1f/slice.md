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
| 回合结算（物理/精神攻击/防御） | `ACCEPTED` | `DONE_FOR_SLICE` | Console `E2E` · Unity `ISOLATED` | `PASS` | [design/rules/核心机制.md](../../rules) §4；`code/src/.../Engine/` + 引擎测试（计数见 [构建与测试 §四](../../engineering/build-and-test.md)） |
| 敌方 HP / SAN 双资源 | `ACCEPTED` | `DONE_FOR_SLICE` | 同上 | `PASS` | [design/entities/敌人与事件.md](../../entities) §4.1 权威表（轻度病人 HP 20-30 / SAN 50-70） |
| 基础行动（物攻/精攻/防御） | `ACCEPTED` | `DONE_FOR_SLICE` | 同上 | `PASS` | [design/rules/skill-tree/operations/](../../rules/skill-tree/operations/) §二/§三 |
| 速度排序 / 响应窗口 | `ACCEPTED` | `DONE_FOR_SLICE` | 同上 | `PASS` | [design/rules/回合战斗流程.md](../../rules) §三/§六 |
| **Core → Unity 适配层** | `ACCEPTED` | **`NONE`** | `ISOLATED` | `UNKNOWN` | 🔧 2026-09-13（[#155](https://github.com/verystrongdog/game/issues/155)）：**桥接工程已按 [ARCHITECTURE.md §4.1](../../../ARCHITECTURE.md) 建好**（`code/src/YouAreNotTheFish.Core.Unity/`，`netstandard2.1`，链接 Core 的 3 个源文件 + `IsExternalInit` 垫片）**且进了 `engine` job 当机械护栏**；但**Unity 侧暂无消费者**——原消费者（白盒 Demo 战斗沙盘）经 owner 裁定**整体退役**，那个「手抄常量」的假实现随之消失。故 `Implementation` 由 `FAKE` 改判 **`NONE`**（`FAKE` = 有个假实现顶着；现在连假实现都没有——**这不是退步，是把一个已知假件换成了一块干净地基**）。接线推迟到 CP-01 准入 / P4d 真需要接缝时 |
| **探索与接敌** | **`UNRESOLVED`** | `NONE` | `ISOLATED` | `UNKNOWN` | 无空间切片设计；Unity 场景靠 Editor 菜单运行时生成 |
| **HUD 与反馈** | `ACCEPTED` | **`NONE`** | `ISOLATED` | `UNKNOWN` | [design/presentation/战斗界面布局.md](../../presentation) 有 37 项决策，但 Unity 侧未实现 |
| **角色动作呈现**（✏️ 2026-09-12 新增） | `ACCEPTED` | **`PARTIAL`** | `ISOLATED` | **`PASS`** | [动作库规格.md](../../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) 13 词表 + 契约 A+B；`ActionPlayer.cs` / `ActionCatalog.cs` 已入库。**缺口**（属 `Implementation`，非健康度问题）：L1 九条中仅 5 条有 clip（locomotion 四条引用仓库外 KI 资产）→ 干净检出下 4 态 clip 空；[动作系统分解](../../engineering/%E5%8A%A8%E4%BD%9C%E7%B3%BB%E7%BB%9F%E5%88%86%E8%A7%A3-2026-09-12.md) 为本轮 frontier。🔧 2026-09-13 回填：`Health` 原为 `REGRESSED`，判据写的是「PlayMode 2 项常红」——那两条是 `ActionPlayer` 的**纯逻辑缺陷**（非 clip 缺失），已于 2026-09-12 修复，`code/unity/README.md` §二·J 实测 **33/33 全过**，判据失效故改 `PASS`。⚠️ 花海 lab 移除后测试数 33→29 系**算术推断、未重跑**（该 README 页脚自述），故 `PASS` 的依据是移除前最后一次实测。🔧 2026-09-13 补：全量重跑已做——[#150](https://github.com/verystrongdog/game/issues/150) 门禁 `run_tests` **47/47 通过**（含 BrainView 9 条 / 花海 4 条 / 就座 10 条 / 本条新增 4 条），计数以这次实测为准 |
| **就座交互（找椅子才能坐）**（✏️ 2026-09-13 新增） | `ACCEPTED` | **`DONE_FOR_SLICE`** | `ISOLATED` | **`PASS`** | [动作库规格.md](../../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) §四·丁：就座判定（距离 + 前侧 + 空闲）· 对齐段 · 占用锁 · 就座锚点 0.423 m 实测。实现已落地（`ChairSeat.cs` + 驱动层判定/对齐/根位移 + 10 项 PlayMode 断言；就座后臀部↔坐面 +4.8 mm），且 owner 目视清单 ⑧ **已通过**（试玩证据绑提交 `2b57b03`，见 `code/unity/README.md` §二·J 门禁实测末行）。🔧 2026-09-13 回填：本行原写「未 `DONE_FOR_SLICE`：owner 目视清单 ⑧ 未确认」——而 ⑧ 的记录提交 `ae33281` 当时**未回填本行**；该行自述的唯一缺口即 ⑧，故按证据判 `DONE_FOR_SLICE`（**此格为按行内判据的推导升级，非新增实现；若 owner 认为还有未记录的缺口，改回 `PARTIAL` 即可**） |
| **持椅交互（手里有东西）**（✏️ 2026-09-13 新增） | **`ACCEPTED`** | **`PARTIAL`** | `ISOLATED` | `UNKNOWN` | [动作库规格.md](../../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) §四·戊（第七次修正）：词表 13→17 · **两条链可互切、双手链由 `Carry1H` 换握进入**（原 `Grab2H` 取消——Mixamo 无"双手拾取"素材）· `Variants` 字段 · 挂点三层（逐状态可握锚点 / 阻尼摆动 / "手到位帧"）· 副手 IK（仅格挡变体）· 派生件新增**镜像**。**设计侧 `ACCEPTED`**（18 条决策全部有实测读数支撑：7 条 Mixamo clip 归槽 + HUMOTO 参照量测）。🔧 2026-09-13 回填（[#150](https://github.com/verystrongdog/game/issues/150)）：Implementation `NONE` → **`PARTIAL`**——本条唯一的实现增量是**镜像派生件**（`DerivedClipBuilder.DeriveMirrored()` 纯函数 + 根位移实测修正 + `Derived/Defend_Carry1H_Mirrored.anim` + `ActionLabGripTests` 4 条断言）；门禁 `unity` **47/47**、`unity-assets` 四条 **0 违规**，绑提交 `6d7dd7e`/`da1c5c1`，读数见 `code/unity/README.md` §二·M。🔧 2026-09-13 再回填（[#152](https://github.com/verystrongdog/game/issues/152)）：挂点三层已落地**两个半**——`ChairGrip.cs`（可握锚点实时解 + 逐状态基准朝向 + 「手到位帧」读数 + 阻尼摆动 + 挂点三者同时），场景椅子带组件，`run_tests` **53/53**、`unity-assets` 0 违规，读数见 `code/unity/README.md` §二·N。🔧 2026-09-13（[#155](https://github.com/verystrongdog/game/issues/155)）：白盒 Demo 沙盘退役后**全量复跑 51/51**（53 − 2 条 `DemoSmokeTests`，实测非推断）——本行判据不受影响**仍缺**（故非 `DONE_FOR_SLICE`）：状态链与 `Variants` 解析（链接线 issue）、副手 IK（双手链 issue）。**🔴 2026-09-13 owner 目视：不通过**——原话「忽略了碰撞体积，人体模型根本不是用人类的方式跟椅子在进行互动」，并点名「左手没扶椅子」「椅子没握在手里（悬空/穿模）」。实测对上：锚点**精确**落在手骨（0.0000 m，机制按设计工作），但同姿势下**左手离椅子表面 0.7415 m**，且挂点期间椅子 `isKinematic` + 碰撞被忽略（规格明写的设计）。⇒ 这不是调 euler 角度能修的观感问题，而是**挂点机制本身在视觉上不成立**；已升级为待 owner 裁定的设计问题（见 `code/unity/README.md` §二·N 未闭合项 1′）。**裁定前，本行不得再声称该层"已落地"**。⚠️ 本项是**呈现探针**（`PLAYABLE.md` 当前 `NO_AUTHORIZED_PLAYABLE` → 不得新增正式玩家行为），规则层 §10.13 **不动** |
| **动作集机器源**（✏️ 2026-09-13 新增） | `ACCEPTED` | **`NONE`** | `ISOLATED` | `UNKNOWN` | [动作库规格.md](../../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) §四·丙（机器源与数据契约）+ 第二次修正的 D-a：`data/action_set.json` 已是 `role: generator-input`（词条元数据 + locomotion 混合参数）。**缺口**：**没有生成期消费方**——`ActionCatalog.cs` 仍是手写常量表、locomotion 四条仍指仓库外的 KI 路径 → [#138](https://github.com/verystrongdog/game/issues/138)。🔧 2026-09-13 登记：此前本行缺失，导致校验器规则 I4「Design 未 ACCEPTED 的能力不得声明 Implementation 迁移」**无法判定** |
| **locomotion 连续混合（契约 B）**（✏️ 2026-09-13 新增） | `ACCEPTED` | **`NONE`** | `ISOLATED` | `UNKNOWN` | [动作库规格.md](../../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) §四·乙 契约 B：1D blend tree（参数 `speed01`，采样点 `0 / 3.0 / 6.0` m/s，阈值源自 `ActionLabDriver` 的**演示常量**，非正典数值）。**现状**：仍是 Idle/Walk/Run **三态硬切**（`Implementation` = `NONE`——硬切不等于连续混合）→ [#140](https://github.com/verystrongdog/game/issues/140)（blocked by [#139](https://github.com/verystrongdog/game/issues/139)）。🔧 2026-09-13 登记：此前本行缺失，同上致 I4 无法判定 |
| 结束条件 | `UNRESOLVED` | `NONE` | `ISOLATED` | `UNKNOWN` | — |
| Unity 资产身份（`.meta`/ProjectSettings） | — | **`DONE_FOR_SLICE`** | `ISOLATED` | **`PASS`** | `code/unity/README.md` §二·H（#136 资产身份入库）+ `code/tools/validate_unity_assets.py`（#142 常驻校验：128 个受控 Unity 文件 / 58 个 `.meta` / 1 场景 / 1 controller，四条规则 0 违规）。🔧 2026-09-13 回填——本行原写「`.meta` 0 个、场景 0 个 → 阻塞 P4b」，与 #136 落地后的事实不符 |

**读法**：结算与资源**逻辑已真实可用**（Console 端 E2E）；但**呈现侧几乎全停在 `ISOLATED` 或 `NONE`**——这正是 M1/M2/M3 全部 `UNTESTED` 的原因。

## 三、假实现与临时捷径

| 位置 | 性质 | 替换条件 |
|---|---|---|
| ~~`code/unity/Assets/Scripts/DemoSolver.cs`~~ | ~~手抄 `CalibrationConfig.Default` 的结算常量（伤害 4 / 命中 0.75 / SAN 惩罚 1.3·2 / HP=san×0.5）~~ | ✅ **2026-09-13 已删除**（[#155](https://github.com/verystrongdog/game/issues/155)）：假件与它的宿主（Demo 战斗沙盘整套）一并退役，不再挂账 |
| Unity 场景 | **已解除**：`Assets/Scenes/ActionLab.unity` 自 #136 起入库，为可打开的基准场景（`docs`：`code/unity/README.md` §二·H） | 🔧 2026-09-13 修正——本行原写「不入库，靠 Editor 菜单运行时生成」，该捷径已由 #136 消除；其余 lab 场景仍由 builder 菜单重建 |
| `code/unity/Assets/Kevin Iglesias/*` 引用 | 该资产包**不在仓库** → 干净检出下 `ActionLab.controller` 的 4 条 locomotion 态（Idle/Walk/Jump/Run）`m_Motion` 为**空（Missing）** | 要么入库、要么改为仓库内资产（工作面 = [#139](https://github.com/verystrongdog/game/issues/139)）。🔧 2026-09-13 更正：原文写「**导致 PlayMode 2 项失败**（locomotion clip 缺失）」——**因果关系是错的**，那两条是 `ActionPlayer` 的纯逻辑缺陷，落 5 条 clip 不会让它们转绿（`code/unity/README.md` §二·H 残留缺口 ② 有逐字否定）。现在这 4 条悬空引用由 `code/tools/validate_unity_assets.py` 的 A3 每次报出 |

## 四、阻塞项

| 阻塞 | 影响 | 解除条件 |
|---|---|---|
| ~~无 Unity Editor~~ → **已解除**（🔧 2026-09-13） | 原写「阻塞 P4b（资产身份）、P4d、P5」。实际：**本机就是那台 Windows 机**，经 WSL interop 可直驱 Editor（`code/unity/README.md` §二·G 实测；`gates.json` 的 `unity` 为 `available: true`）；P4b（资产身份）已由 **#136** 落地，并有 #142 的常驻校验兜住 | — 不适用 |
| P4d（Core→Unity 接缝）未定案 | 接缝实现无法开工 | [#135](https://github.com/verystrongdog/game/issues/135)（RFC：Q6b 桥接范围）出结论 |
| 切片未准入 | 不得新增正式玩家行为 | owner 在 [PLAYABLE.md](../../../PLAYABLE.md) 改为 `AUTHORIZED_PLAYABLE: CP-01` |

---
*创建: 2026-09-12 | 更新: 2026-09-13（🔧 四轴表与 §三/§四 回填：`Unity 资产身份` 行 `NONE`/`UNKNOWN` → `DONE_FOR_SLICE`/`PASS`（#136 + #142）；`就座交互` 行 ⑧ 已通过 → `DONE_FOR_SLICE`；`角色动作呈现` 行 `REGRESSED` 判据失效 → `PASS`；§三 KI 行因果更正；§四 「无 Unity Editor」阻塞解除并拆出 P4d 的真实前置 #135；测试计数不再复述、改为引用构建与测试 §四（#130）；🔧 2026-09-13 补两行「动作集机器源」（#138）与「locomotion 连续混合（契约 B）」（#140）——两项此前未登记，致校验器 I4 对这两条 issue「无法判定」；🔧 2026-09-13 `Core → Unity 适配层` 行按 #155 改判 `FAKE`→`NONE`（假件随宿主退役，桥接工程就位待接线））*
*关联: [PLAYABLE.md](../../../PLAYABLE.md), [WORKFLOW.md](../../../WORKFLOW.md), [架构](../../../ARCHITECTURE.md), [六维状态](../../framework/six-dimensions.md)*
