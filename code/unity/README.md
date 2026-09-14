# Unity 呈现沙盘 — 可控角色 + 指令→动作→UI 反馈（Grilling #122）

> 呈现维度的可运行验证载体：Unity 工程 + 白盒人形角色，可接收基础行动指令并作出动作，底部 HUD 显示 HP/SAN 状态变化——为「状态面板细部规格」grilling 提供 UI 调试反馈底子。
>
> **维度: 呈现 + 管线** — Issue [#122](https://github.com/verystrongdog/game/issues/122)。
>
> 🔧 **2026-09-13（[#155](https://github.com/verystrongdog/game/issues/155)）**：本文档已从 #122 的白盒战斗沙盘扩展成 **Unity 侧总览**；**那套白盒沙盘本身已按 owner 裁定整体退役**（`DemoSolver`/`DemoActor`/`DemoCombatDriver`/`DemoHud`/`DemoTypes`/`DemoBootstrapper`/`CharacterVisual` + `SceneBuilder` + `DemoSmokeTests`）。现行基准场景是 `Assets/Scenes/ActionLab.unity`（[#136](https://github.com/verystrongdog/game/issues/136)）。

## 一、这是什么

| 项 | 内容 |
|----|------|
| 场景 | **现行基准场景**：`Assets/Scenes/ActionLab.unity`（入库，#136）——动作系统（13 词表 / 契约 A+B）+ 就座交互 + 持椅挂点；其余 lab 场景由 Editor 菜单重建、不入库 |
| ~~白盒战斗沙盘~~ | 🚫 **2026-09-13 整体退役**（#155）：演示者/陪练两个白盒小人 + 指令回合 + HUD 那一套连同它的场景生成器与冒烟测试一并删除 |
| 数值源 | 🚫 **随沙盘一起消失**：原 `WhiteboxSolver`（手抄 `CalibrationConfig.Default` 常量）就是 [ARCHITECTURE.md §四](../../ARCHITECTURE.md) 认定的**本仓唯一反向污染点**——owner 裁定把宿主整套退役，该风险随之归零。Core→Unity 接缝的技术定案（[§4.1](../../ARCHITECTURE.md)）与桥接工程保留，**接线推迟到接缝真正需要时** |

## 二、本地验证步骤（Windows/macOS/Linux 桌面）

前置：Unity 6 Editor（6000.0.x；本工程 `ProjectVersion.txt` 锁 6000.5.2f1——版本不一致时 Unity 会提示升级/降级，接受即可，或改该文件为你的版本）。

1. 用 Unity Hub/Editor 打开本目录（`code/unity/`）作为工程；首次导入会自动还原包（uGUI + Test Framework）。
2. 打开基准场景 **`Assets/Scenes/ActionLab.unity`** → 按 **Play**（其余 lab 场景由 `Assets/Editor/` 下各 builder 的菜单重建；🔧 `YANTF → 呈现沙盘 → 创建 Demo 场景` 那条菜单已随白盒沙盘退役，#155）。
3. 操作见 §二·J/§二·M/§二·N 各节（动作系统、就座交互、持椅挂点）。
4. 跑测试：**Window → General → Test Runner → PlayMode → Run All**（计数以最近一次实测为准，见 §二·O）。

### unity-cli 自动化（可选）

装有 [Unity CLI](https://docs.unity.com/en-us/unity-cli/unity-cli-reference) 且 Editor 已打开本工程时：

```bash
unity pipeline install     # 首次：装入 com.unity.pipeline（Editor 打开状态下）
unity status               # 确认 Editor 连接
unity command editor_play  # 进 Play 模式（验证用）
# 测试命令行：Unity -batchmode -runTests -testPlatform PlayMode -projectPath . -testResults results.xml
```

## 二·B、Walker 移动实验场景（几何体人体走/跑/跳）

> 独立于回合战斗沙盘的 **locomotion（自由移动）呈现验证**：几何体白盒人体（Capsule/Sphere 拼装）+ `CharacterController` 实时移动，验证「在地面上走动/奔跑/跳跃」的手感与程序化步态动画。维度：呈现 + 规则（移动层）。

| 项 | 内容 |
|----|------|
| 场景 | `WalkerLab.unity`（新）：蓝色几何体人体 + 参照柱 ×4 + 地面 |
| 操作 | **WASD/方向键** 移动（相对相机）、**Shift** 奔跑、**Space** 跳跃 |
| 移动 | `CharacterController`（重力 / 碰撞 / 贴地 / 45° 坡度 / 0.3 台阶）；走 3.2 m/s、跑 6.4 m/s、跳 1.5 m 抬升 |
| 动画 | 程序化（无 Animator）：摆臂摆腿随速度变频变幅（走/跑区分）、空中收腿姿态、Idle 呼吸 |
| 相机 | 第三人称平滑跟随（WalkerController.followCamera） |
| 骨架 | `WalkerController.BuildBody()` 幂等组装 hips→torso/head/armL/R(+mesh)/legL/R(+mesh)，图元去 Collider（碰撞全交给 CC） |
| 测试 | `WalkerLabSmokeTests`（3 个 PlayMode）：骨架完整 / 重力落地+走跑速度差 / 跳跃离地回落 |

**生成/运行**：菜单 **YANTF → 移动实验 → 创建 Walker 场景**（`Assets/Editor/WalkerLabBuilder.cs`，Editor 模式实体化几何体并保存场景，打开即见人体层级）→ 打开 `Assets/Scenes/WalkerLab.unity` → 按 **Play**。

> ⚠️ 已知简化：白盒人体为单段四肢（无肘/膝细分），摆动为枢轴旋转占位——外部人形模型/Animator 接入点即 `WalkerController.BuildBody` 与 `UpdatePose`；移动参数为演示常量（非正典数值）。

## 二·C、Ki 动画角色场景（Kevin Iglesias 人形模型 + 走/跑/跳动画）

> 在 Walker（几何体程序动画）基础上，验证**外部人形模型 + 现成动画资产**的接入：官方演示模型（Humanoid Avatar + 完整骨骼：脊柱/肩臂/五指/腿脚趾）配 Animator，播放 Kevin Iglesias Human Basic Motions 的 Idle/Walk/Run/Jump 动画。维度：呈现 + 管线（外部模型/动画接入点）。

| 项 | 内容 |
|----|------|
| 场景 | `KiWalkerLab.unity`（新）：Kevin Iglesias 演示人形 + Animator 四状态 |
| 操作 | **WASD/方向键** 移动、**Shift** 奔跑、**Space** 跳跃 |
| 模型 | `Human_BasicMotionsDummy_M.prefab`（Avatar=`HumanM_ModelAvatar`，Humanoid） |
| 动画 | `AnimatorWalker.controller`（Idle/Walk/Run/Jump 四状态，clip 取自导入 FBX：`Male/Idles`、`Movement/Walk|Run|Jump`） |
| 位移 | CharacterController（`AnimatorWalker.Awake` 按 SkinnedMesh bounds 自适应胶囊） |
| 接入点 | `AnimatorWalker.cs`（状态机切换）+ `KiWalkerLabBuilder.cs`（Editor 构建 controller + 场景） |

**生成/运行**：菜单 **YANTF → 移动实验 → 创建 Kevin Iglesias 动画场景** → 打开 `Assets/Scenes/KiWalkerLab.unity` → 按 **Play**。

> ⚠️ 已知简化：动画原地播放、位移全交 CC（非 RootMotion，`[RM]` 版动画留作后续对照）；跳高/速度参数为演示常量（非正典）；Jump 动画非循环，空中播完定格末帧、落地切回地面状态。

## 二·D、动作集规格与 ActionLab（Grilling #123 ✅ + #124 实施执行层）

> 动作受控词表（12 词条：L1 落地 9 = 待机/走/跑/跳/物攻/精攻/防御/受击/倒下；L2 登记 3 = 坐/站/对话）+ 引用契约 A（纯状态 + 脚本 CrossFade）+ 来源矩阵 + 扩展协议——见 [动作库规格.md](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md)。
> 载体 = 新建 `ActionLab` 演示场（**Mixamo X Bot 真人模型** 🔧（#124 锚定，Y Bot 备用）+ 词表 controller + 按键触发 + HUD 当前动作名），实施分 Batch0（AI 产码：词表/`ActionIds`/`ActionPlayer`/幂等 builder/PlayMode 断言）→ Batch1（用户手动：Mixamo 导入 + 9 状态手摆）→ Batch2（手感收尾）。执行层契约见 [决策记录 #124](../../design/archive/grilling/grilling-124-actionlab/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md)。

## 二·E、ActionLab 实施手册（Batch0 交付）

**前提**：Windows 侧 `git pull`（Batch0 代码与一键工具入库）；下载的 7 个 FBX 在 `C:\Users\9527\Downloads\`。

**目标**：把词表 L1 9 态在 X Bot 载体上接成可 Play 演示的动作场；防漂移断言随导入自动升级。

1. **一键导入 + 生成**（取代手动的复制/改名/Rig/菜单四步）：菜单 **YANTF → 动作演示 → 一键导入 Mixamo 资产并生成 ActionLab（首次）**（`Assets/Editor/MixamoSetup.cs`）——自动完成：
   - 复制 `X Bot.fbx`/`Y Bot.fbx` → `Assets/Mixamo/Characters/`；复制 5 条 clip 并**改名 = 词表 id** → `Assets/Animations/Mixamo/Combat/`（映射见下，文件名 ≠ 语义，见 [动作库规格.md](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) §二 来源列）；
   - 全部设 Rig = **Humanoid** → Apply；
   - 调幂等 builder：建 12 态 controller（L1 9 态命名=id）→ 按资产存在性挂 clip（缺口留空 + Console 清单）→ 生成 `Assets/Scenes/ActionLab.unity`。

   | 下载文件 | 复制为 `Assets/Animations/Mixamo/Combat/` | 词条 |
   |---|---|---|
   | `Jab Cross.fbx` | `PhysicalAttack.fbx` | 物攻（直拳；单次性 Play 后判） |
   | `Charge.fbx` | `MentalAttack.fbx` | 精攻（伸手指人 = A 前指宣言） |
   | `Short Left Side Step.fbx` | `Defend.fbx` | 防御（循环格挡） |
   | `Head Hit.fbx` | `HitReaction.fbx` | 受击（通用性 Play 后判） |
   | `Dying.fbx` | `Down.fbx` | 倒下 |

   （源目录不是默认值时改 `MixamoSetup.SourceDir`；单项手动导入与生成仍可用「创建 ActionLab 场景」菜单。）
2. **操作**：打开 `Assets/Scenes/ActionLab.unity` → **Play**：WASD/方向键 移动、Shift 跑、Space 跳（locomotion）；`1`物攻 `2`精攻 `3`防御(再按退出) `4`受击 `5`倒下 `R`重置；HUD 顶部显示当前动作名。
3. **验收（目视清单，规格 §六）**：① 待机→走→跑→停顺滑；② 每动作触发后 HUD 显示正确动作名；③ 物攻→受击（打断）→回待机；④ 防御姿态循环不穿模；⑤ 倒下停留不悬浮；⑥ 衔接过渡帧可接受（不可接受 → 调 fade / 换 clip / 该动作局部迁 B，见规格 §四）。
4. **测试**：Test Runner → PlayMode → Run All（防漂移断言按资产存在性分档：已导入 clip 的状态断言「有 clip」，未导入状态断言「状态存在 + clip 空」，随导入自动全绿）。

> ⚠️ 已知：Jab Cross 为组合拳，若直拳单次语义不合 → 换 Punch 类 clip 或走程序化兜底。
>
> **🔧 2026-09-12 修正**：本节的 KI 引用路径（`Assets/Kevin Iglesias/...`）**已作废**——来源整条切 Mixamo，KI 包弃用（三条理由见 [动作库规格.md §五](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md)）。后果与处置见 §二·G。原「X Bot 上 KI Walk/Run retarget 质量」这条已知项随之消失：不再有 retarget。

## 二·G、本轮工作：动作系统结构升级（#137–#140，2026-09-12）

> 目标：把动作集从「演示够用」推到「**足够多完整动作 + 姿态切换自然**」的工程底子。范围裁定为**结构升级 + 站↔坐探针**，动作内容仍限 L1 九条（决策记录见 [动作库规格.md](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) 第二次 🔧 修正；分解见 [动作系统分解](../../design/engineering/%E5%8A%A8%E4%BD%9C%E7%B3%BB%E7%BB%9F%E5%88%86%E8%A7%A3-2026-09-12.md)）。

### 怎么驱动 Unity（2026-09-12 全部实测）

**🔧 关键事实：本机就是那台 Windows 机。** 这个仓库所在的 Linux 是**同一台 Windows 上的 WSL2**，`unity.exe` 经 WSL interop 可直接执行并连上 Windows 侧的 Editor。故**不需要另开一个"Windows 会话"**——本会话即可驱动、验证、跑测试。

| 项 | 实际值（实测） |
|---|---|
| 工程路径 | `C:\Users\9527\game\code\unity`（= `/mnt/c/Users/9527/game/code/unity`） |
| unity CLI | `C:\Users\9527\AppData\Local\Unity\bin\unity.exe` |
| Editor 本体 | `C:\Totall\unity\install\6000.5.2f1\Editor\Unity.exe`（版本 6000.5.2f1，与 `ProjectVersion.txt` 一致） |
| 许可证 | `C:\Users\9527\AppData\Local\Unity\licenses\UnityEntitlementLicense.xml`（已激活） |

驱动方式（**不需要提权**——命令本身不改文件；Editor 侧写盘由 Editor 进程完成）：

```bash
U="/mnt/c/Users/9527/AppData/Local/Unity/bin/unity.exe"
P="C:\Users\9527\game\code\unity"
"$U" status                                   # 期望 state: ready
"$U" command --project-path "$P"              # 列出 Editor 暴露的全部命令
"$U" command get_scene_hierarchy --project-path "$P" --json
"$U" command editor_focus   --project-path "$P"   # 把 Unity 窗口切到前台
"$U" command editor_play    --project-path "$P"
"$U" command capture_game_view --project-path "$P" --json   # 返回 base64 PNG
"$U" open "C:\Users\9527\game\code\unity"     # 用正确 Editor 版本打开工程
```

- ⚠️ **改 `/mnt/c` 下的文件本身需要提权**（沙箱把 workspace 之外设为只读）——`git`、`cp` 等写操作要申请 `danger-full-access`。
- 连不上先查 **Safe Mode**：有 C# 编译错误时 Pipeline 包不加载，`unity status` / `unity command` 全连不上。先修编译错误再重启 Editor。
- 多于一个 Editor 在跑时必须传 `--project-path`，否则报 `AMBIGUOUS_EDITOR`。
- **资产区单机所有权**：`code/unity/Assets/**` 的资产只由**这一台机**生成与手调（[ARCHITECTURE.md §五](../../ARCHITECTURE.md)）。GUID 必须稳定——这与 #136 是同一件事的两面。

### 🔧 2026-09-12 迁移：Windows 那份拷贝已并入 main

原先存在**两份分叉的拷贝**，现已合并为一份：

| 之前 | 现在 |
|---|---|
| `C:\Users\9527\game` 在分支 `feat/unity-presentation-slice`（旧目录结构 `unity/`），整个 Unity 工程**从未入 git**（100 个未跟踪项） | 同一路径 **已在 `main`**，工程位于 `code/unity`（main 布局） |
| 294 个 `.meta`、5 个场景、5 个 controller、`Kevin Iglesias/`(68M)、23 个 `ProjectSettings`、`packages-lock.json` 只存在于 Windows 侧 | 全部已移植进 `code/unity/`（`cp -rn` 不覆盖策略，main 既有文件优先） |
| `remote.origin.fetch` 只配了单条分支（单分支克隆，看不到 main） | 已修为标准 glob `+refs/heads/*:refs/remotes/origin/*` |

**迁移的验证**：新工程已由 Unity 6000.5.2f1 打开并完成首次导入 → `compiling: false`、`status: ready`、**Console 0 错误**（仅 2 条与迁移无关的弃用警告）。旧 `unity/` 目录**已于 2026-09-12 删除**（254 MB）——删除前做过完整性核对：旧工程 534 个文件 → 新工程缺失 **0** 个；且旧目录无任何跟踪文件（`git ls-files unity/` = 0），故删除不动 git 历史。迁移前的完整备份在 Linux 侧 `.scratch/win-backup/`：`unity-project-2026-09-12.tar.gz`（22 MB，含 Assets/ProjectSettings/Packages）+ `unity-root-files/`（导入日志、测试结果、两个旧 md）。

**🔧 2026-09-13 更正：这一处「待合的分叉」已作废，不要再去合它。**

`AnimatorWalker.cs` 确实双向发散（原 Windows 拷贝有 `SitPhase` 状态机 + `OnAnimatorMove` 接管 root motion；
`main` 有 `airControl` 0.15 / `airDrag` 0.5 的空中方向修正参数化）。但 **owner 已于 2026-09-12 裁定把这套 KI 旧线的坐/起实现「整体舍弃、不再作为工作面」**
（见 [动作库规格.md](../../design/presentation/动作库规格.md) 第四次修正），随后坐立三段改在 **ActionLab + `ActionPlayer`** 上落地（同文第五、六次修正）。
**合并这份分叉 = 把一份已作废的实现搬回工作面**，属反工。

现行的坐立口径与读数在 [动作库规格.md §四·乙/§四·丁](../../design/presentation/动作库规格.md)：
「Y 烘进姿势」+ 默认 `applyRootMotion = false`，坐立三段按词条 `RootMotionXZ` **逐状态**切换；接缝 ≤1.9 mm、足底 +2.0/+2.3 mm、PlayMode 23/23。
`main` 的 airControl/airDrag 仍然有效（在 `AnimatorWalker.cs` 的 main 版里），**不是待合并项**。

### 会话启动清单

1. **确认 Editor 可直驱**：上表的 `unity status`，期望 `state: ready`（Editor 已开则直接连；未开则 `unity open`）。
2. **认准起点**：先读 [AGENTS.md](../../AGENTS.md)（全仓约束入口，含提交前必跑的校验器）→ 本 README §二·G → [危险点表](../../design/engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md)（**改 `Assets/**`、或驱动 Editor 前先查你要动的那处**）→ [动作库规格.md §四·乙/§六](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) → [动作系统分解](../../design/engineering/%E5%8A%A8%E4%BD%9C%E7%B3%BB%E7%BB%9F%E5%88%86%E8%A7%A3-2026-09-12.md)。
3. **开工顺序**：**#138 → #139 → #140**（严格串行，工作面相交）。每条的门禁、验收标准、预期差分、明确排除都在 issue 正文里，照做即可。
   🔧 `#137`（站↔坐探针）已于 2026-09-13 **按 superseded 关闭**——原假设被实测否定、其后续口径在 ActionLab 上落地（见上一节更正块），无剩余工作面。
4. **本侧对 `code/unity/Assets/**` 可写**（经提权），实现与验证能在同一侧闭环——**不再需要跨机交接**。

### 三条 issue（严格串行，工作面相交所致）

> `#137` 曾在本表第 1 行，已于 2026-09-13 按 superseded 关闭（原假设否定 + 口径改在 ActionLab 落地）。

| 序 | issue | 做什么 | 状态 |
|---|---|---|---|
| 1 | [#138](https://github.com/verystrongdog/game/issues/138) | **数据契约消费**：生成器读 `data/action_set.json` 产出 controller 与 C# 静态表，且**非破坏**（不覆盖已手调值） | `ready-for-human` |
| 2 | [#139](https://github.com/verystrongdog/game/issues/139) | **五条 clip 到库**：Idle/Walk/Run/Jump/Talk 下载 + Humanoid 导入 + **Play 预览实证归槽**（文件名不作依据），PlayMode 断言转绿 | `blocked`（by #138） |
| 3 | [#140](https://github.com/verystrongdog/game/issues/140) | **locomotion 迁契约 B**：1D blend tree（`speed01`，采样点 0 / 3.0 / 6.0）取代三态硬切 | `blocked`（by #139） |

> 门禁可用性：`unity` 在**本机可跑**（WSL 经 interop 直驱 Windows Editor），故 [`gates.json`](../../design/engineering/gates.json) 的 `available` 为 `true`。CI（ubuntu，无 Unity）侧仍不可跑，其 `unity` job 继续显式报告 `NOT_AVAILABLE`。

### 两条必须先懂的陷阱

1. **文件名 ≠ 动作语义**（#124 实证）：`Charge` 实为伸手指人、`Short Left Side Step` 实为循环格挡。每条新 clip 都要 Play 预览后归槽。
2. **坐立两条连方向都判不出来**：`Sit To Stand.fbx` 与 `Stand To Sit.fbx` 的内部 take 名均为 `mixamo.com`、`Title`/`Subject` 为空（2026-09-12 逐字节核验）。**必须预览**，不得据文件名预设——两条是近似镜像动作，误配比战斗类更隐蔽。
3. **新拖进来的 FBX 不会自动是 Humanoid**（🔧 2026-09-12 实测，代价很大）：Unity 默认导成 **`Generic` + `NoAvatar`**——既**挂不上** Humanoid 载体（X Bot 的 Animator 要 Humanoid clip），也**读不到 `RootT` 根曲线**（Generic 没有根位移抽象，你会以为这条 clip「没有根位」）。
   - **判据**：`ModelImporter.animationType == Human`、`avatarSetup == CreateFromThisModel`，且 `AssetDatabase.LoadAllAssetsAtPath` 里**有 Avatar 子资产**、`clip.humanMotion == true`。
   - **解**：Inspector → Rig → Animation Type = **Humanoid** → Apply；或用 `ModelImporter` API 设 `animationType = ModelImporterAnimationType.Human`（⚠️ 枚举成员叫 `Human`，UI 上叫 Humanoid）+ `avatarSetup = CreateFromThisModel` 再 `SaveAndReimport()`。
4. **`.meta` 的 `clipAnimations` 读回值不代表写盘值，且烘焙策略没有 `lockRoot*` 字段**：`AnimationClipSettings` 根本不暴露"Bake Into Pose"，`ModelImporterClipAnimation.lockRootHeightY` 的读回也不可信。**只有 Play 实测能验**（详见 [动作库规格.md](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) §二 修正块）。

### 观察用移动视角（🔧 已折进 builder，重建即有）

ActionLab 的 `Main Camera` **自带环绕跟随**：`ActionLabBuilder.CreateScene()` 直接挂 `CameraOrbit` 并设好 `target`。对比 WalkerLab 的 `WalkerController.followCamera`，两者都是"可自由观察"的相机，只是载体不同。自由观察三步：

1. 生成场景：菜单 **YANTF → 动作演示 → 创建 ActionLab 场景** → 打开 `Assets/Scenes/ActionLab.unity`
2. **不需要做任何手工挂载**——builder 已把 `CameraOrbit` 挂好、`target` 也设好了（2026-09-12 修订，见下）
3. 直接 **Play**，按住右键拖拽即可自由观察

操作：**按住右键拖拽** = 环绕旋转视角；**滚轮** = 缩放远近（1.5–14 m）；相机注视胸口高度并平滑跟随。移动输入仍走相机相对，转视角后 WASD 前进方向跟着变。

> 🔧 **2026-09-12 修订：改为「折进 builder，自动挂载」。** 触发条件正是原裁定预留的那条（「若日后需要重建场景时自动挂上」）——而它**当天就发生了**：场景自 #136 起已入库，本 builder 每次都是**新建场景**，于是重建把手工挂载冲掉（实测踩到：重建后自由视角消失）。
>
> 现在 `ActionLabBuilder.CreateScene()` 直接给 `Main Camera` 挂 `CameraOrbit` 并设 `target = 演示者`、调 `Snap()` 定初位（`orbit.target` 必须显式设——留空时 `CameraOrbit.Start()` 会兜底成自身 transform，相机会绕自己头顶打转）。**重建即有，无需手工挂。** 原「不建 issue、不改 builder」的裁定就此作废（就地记修正，不进 #137）。

> ⚠️ **仍然必知**：`CameraOrbit` 是 `YANTF.WalkerLab` 命名空间下的组件，与 `ActionLab` 同属 `YANTF.Demo` 程序集——若日后拆 asmdef 需注意跨命名空间引用。

> 🔧 **2026-09-12（#136）：「场景不入库」有一条显式例外。** 基准场景 `Assets/Scenes/ActionLab.unity`（连同 `Assets/ActionLab/ActionLab.controller`）**已入库**——[#136](https://github.com/verystrongdog/game/issues/136) 的交付物 2 要求「至少一个可打开的基准场景，替代靠 Editor 菜单运行时生成」，owner 裁定取 ActionLab（早期白盒 `DemoSandbox` 太简陋，不用）。因此对 ActionLab：**菜单重建会覆盖已入库的场景，差异必须显式提交**。其余 lab 场景仍不入库，见 §二·H。

### 与既有文档的关系

- 机器源 `data/action_set.json`：词条元数据 + blend 参数，每个数值带来源；`role=generator-input`（生成期输入，**运行时 Unity 不读它**）。
- `ActionCatalog.cs` 的 KI 路径为已知作废项，#138 落地后由生成表取代。
- `KiWalkerLab` 保留为历史对照场景，但**不再是词表来源**。


## 二·H、资产身份与提交范围（[#136](https://github.com/verystrongdog/game/issues/136)，2026-09-12 实测）

> **要解决的是什么**：`Assets/**` 此前只有 2 个 `.meta`（`SitPoint` / `CameraOrbit`），而 9 个 Mixamo FBX（5 条 combat clip + `Sit To Stand` / `Stand To Sit` + X Bot / Y Bot）**已在 git 里却没有一个 `.meta`**。后果不是"少几个文件"，而是**干净检出每次开工程都重发 GUID**——`ActionLab.controller` 的 clip 绑定、场景里的组件引用必然失效，手调资产成果既无法入库也无法合并（[build-and-test.md §五](../../design/engineering/build-and-test.md) 登记为缺口）。

### 入库了什么（3 个提交，80 个新文件 + 2 个文件改动，+4843/−2 行）

| 类别 | 内容 | 为什么是它 |
|---|---|---|
| `.meta` ×51（新） | 每个**已跟踪**资产一份 + 干净检出里会存在的目录各一份 | 锁 GUID。**未入库资产不给 `.meta`**——孤儿 `.meta` 会制造"引用了不存在资产"的假象 |
| `ProjectSettings/` ×23 | 含 `ProjectVersion.txt`（补 `m_EditorVersionWithRevision: 6000.5.2f1 (eb73d3b415a1)`）、`EditorSettings.asset`（`m_SerializationMode: 2` = **Force Text**，资产是文本才可合并）、`ProjectSettings.asset`（`runInBackground: 1`，编辑器失焦不冻结 Update 循环） | 工程身份：换机/重装后行为一致 |
| `Packages/manifest.json` + `packages-lock.json` | manifest 新增 `com.unity.pipeline: 0.6.0-exp.1`（unity-cli 直驱用） | 锁是在**这份 manifest** 下由 Editor 生成的；只提交锁会让两者立刻不一致 |
| `Assets/Scenes/ActionLab.unity` + `Assets/ActionLab/ActionLab.controller`（+4 个 `.meta`） | 基准场景 + 12 态控制器 | 5 条 combat clip 的 FBX 早已在 git，缺的只是 `.meta`；补齐后这两件一入库，干净检出即可打开并 Play。controller 正是缺口行抱怨的「Blend Tree 阈值 / transition 参数无处安放」那份手调成果 |

### 没入库什么（以及为什么）

| 排除项 | 理由 |
|---|---|
| `Assets/Kevin Iglesias/`（**68 MB**） | 第三方资产包；来源已整条切 Mixamo（[动作库规格 §五](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md)）；[#139](https://github.com/verystrongdog/game/issues/139) 的验收标准明写「干净检出下 `Assets/Kevin Iglesias/` 不存在」。`.gitignore` 已排除 |
| `Assets/Temp/` | #137 站↔坐探针的过程物（`SitCheck.controller` + 两张截图），不是工程资产 |
| `WalkerLab` / `KiWalkerLab` 两个 lab 场景 | 由 builder 菜单重建，随各自 issue 落地。（`DemoSandbox` 已于 2026-09-13 随白盒沙盘整体退役并删除，#155） |
| `Assets/Settings/Pipeline/EditorPipelineManager.asset` | `com.unity.pipeline` 首次使用的自动产物，可再生 |

### 实测记录（改前 / 改后）

| 指标 | 改前（干净检出 = git 跟踪） | 改后 |
|---|---|---|
| `code/unity/**/*.meta` | **2** | **57** |
| 场景 `.unity` | **0** | **1**（`ActionLab.unity`） |
| controller | **0** | **1**（`ActionLab.controller`） |
| `Packages/packages-lock.json` | **不存在** | 在位 |
| `ProjectSettings/` 跟踪文件数 | 1 | 23 |
| 同一时刻 Windows 工程实况（Editor 所见） | 294 `.meta` / 5 场景 / 5 controller / 23 ProjectSettings / 锁在位 | 未变（入库是它的子集） |
| `code/src/` 与 `data/` 是否被动过 | — | **0 个文件**（#136 预期不变项） |
| `YANTF.Demo.asmdef` 的 `references` | `[]` | `[]`（结构性保证未破） |

### 门禁 `unity` 的证据（Windows Editor 6000.5.2f1，unity-cli 经 WSL interop 直驱）

| 项 | 实测 |
|---|---|
| `unity status` | `state: ready`（PID 32804，工程 `C:\Users\9527\game\code\unity`） |
| `editor_status` | `compiling: false`、`playMode: stopped`、`domainReloadInProgress: false` |
| `console` | **0 error**（仅 2 条与本主题无关的弃用警告：Input Manager / Dynamic Batching） |
| 基准场景可打开 | `open_scene Assets/Scenes/ActionLab.unity` 返回 `guid: dee800a53d8d6934e91729219e7411f1`，与本仓库的 `ActionLab.unity.meta` **逐字一致** |
| Play 后层级 | `ActionLab演示者(X Bot)` 带 `Animator`+`CharacterController`+`ActionPlayer`+`ActionLabDriver`，`Beta_Joints`/`Beta_Surface` 蒙皮 + 完整 `mixamorig` 骨架；`Main Camera` 带手挂的 `CameraOrbit` |
| 抓帧 | 640×360 = **3625 种颜色**，均值 (193,220,219)；作为对照，早期 `DemoSandbox` 抓帧是 84% 纯白（该场景已于 2026-09-13 退役，#155） |
| `run_tests`（`--mode playmode --async_tests`） | `status: completed`，**16 项：14 过 / 2 败**（5.22 s） |
| 2 项失败的真因 | `ActionPlayer_OneShotElapsed_Threshold`、`ActionPlayer_Play_PriorityAndLevelRules`——**纯逻辑断言，不碰任何 clip**（`ResetToIdle()` 后 `CurrentActionId` 仍为 `Down`）。**与资产缺失无关**，见下方残留缺口 ② |
| 提交字节的来源证明 | 84 个入库文件逐个 `sha256` 与 Windows 工程比对：**84/84 一致**（`git show HEAD:<path>` vs 工程文件） |

### 残留缺口（诚实清单）

1. **4 条 locomotion 态仍引用不入库的 KI 包**：`ActionLab.controller` 的 Idle/Walk/Run/Jump 指向 `Assets/Kevin Iglesias/...`。干净检出下这 4 态是「状态存在 + clip 空（Missing）」——正是 [#139](https://github.com/verystrongdog/game/issues/139) 的工作面（整条切 Mixamo 并落库）。入库的是**工程当前的真实状态**，不是伪造的完整态。
2. **2 项常红 PlayMode 断言的真因与 #139 的归因不符**（实测见上表）：那两条是 `ActionPlayer` 的纯逻辑缺陷，落 5 条 clip **不会**让它们转绿；而 `ActionPlayer.cs` / 断言文件都不在 #139 的「允许变化」里 → #139 按现文写达不到自己的验收标准。按 [WORKFLOW.md §一](../../WORKFLOW.md) 非阻塞发现进候选队列，**不在 #136 里顺手修**。
   - **🔧 2026-09-12 已修（随坐立三段那一批，非顺手牵羊——两条都在坐立路径上）**：
     - ① `OneShotElapsed`——C# 允许浮点运算使用**高于结果类型的精度**：`elapsed >= clipLength + OneShotTailSeconds` 的右侧可能以 **double 中间值**参与比较，与外部按 float 落回的同一个和**差 1 ulp**，恰好到点被判"未到点"（实测：`a = clipLen + 0.05f` 与函数内的和同为 bits `1065772646`，函数却返回 `False`）。改为显式落回 float 再比。此计时正是 `Sit` 播完切 `SitIdle` 的依据。
     - ② `ResetToIdle` 不清 `CurrentActionId`——重置后仍留旧值，凡靠它做输入守卫的路径被误导（例：7 起身的守卫要求"当前是 `SitIdle`"）。
   - **证据**：PlayMode **23 项 23 过 / 0 红**（此前 21 项中 2 项常红，见 §二·I）。
3. **干净检出的首次导入 / 编译 / Play 未实测**：Editor 只跑在 Windows 拷贝上（Linux 侧无 Editor，且 WSL 对 `/mnt/c` 只读）。正确性由三条间接证据支撑：① 84/84 逐文件字节一致；② 场景与 controller 的 GUID 引用全部可解析到已跟踪资产（含 X Bot.fbx、5 条 combat clip）〔🔧 2026-09-13 更正：**此句当时写宽了**——`ActionLab.controller` 的 4 条 locomotion 态引用**不可解析**（KI 包未入库），即下方残留缺口 ①；现由 `validate_unity_assets.py` 的 A3 每次报出，并登记在允许清单 `known_dangling`〕；③ 来源工程（就是提交的那批字节）内 Editor 0 错误、16 项测试跑通。
4. ~~**资产身份还没有常驻机械校验器**~~ → **✅ 2026-09-13 已闭合（#142）**：当时 `.meta` 齐全性、GUID 唯一性、场景/controller 引用可解析性是用一次性脚本核的（294 个 `.meta` → 294 个唯一 GUID，0 冲突），**核完即弃**。现在常驻 **`code/tools/validate_unity_assets.py`**，四条规则（成对性 / GUID 唯一性 / 引用可解析 / FBX Rig）进 `docs-integrity` 循环；它**不需要 Unity Editor**，故在 CI 上也能拦（`unity` 门禁在 CI 上是 `NOT_AVAILABLE`）。已登录在案的例外见 `code/tools/validate_unity_assets_exceptions.json` 的三段允许清单——其中 4 条 KI 悬空引用归属 [#139](https://github.com/verystrongdog/game/issues/139)，**该 issue 关闭时必须删除那 4 条**。

### 怎么复核

```bash
git ls-files 'code/unity/**/*.meta' | wc -l        # 期望 57
git ls-files 'code/unity/**/*.unity'               # 期望 1（ActionLab）
git ls-files code/unity/Packages/packages-lock.json
grep -A2 '"references"' code/unity/Assets/Scripts/YANTF.Demo.asmdef   # 期望 []
```

### ⚠️ Windows 拷贝怎么对齐（**不要直接 `git pull`**）

Windows 侧那份拷贝里，这些文件是**未跟踪但已存在**的（本次入库把它们变成了跟踪文件）。`git pull` 会以「untracked working tree files would be overwritten by merge」拒绝——**即使字节完全相同**（2026-09-12 实测）。正确做法是只对齐 HEAD 与索引，不碰工作树：

```bat
cd C:\Users\9527\game
git fetch origin
git reset --mixed origin/main
```

`reset --mixed` 不动工作树，所以那两处既有分叉（`AnimatorWalker.cs` 的坐/起 vs main 的空中方向修正、`KiWalkerLabBuilder.cs`）作为"已修改"原样保留，留给 [#137](https://github.com/verystrongdog/game/issues/137)。**不要用 `git reset --hard` / `checkout -f`**——那会覆盖这两处未提交的分叉实现。

## 二·I、ActionLab 落地回切修复（提交 `6bd8ddc`，2026-09-12）

> 演示者可走/跑/跳，但**按住方向键起跳、按键不放，落地后角色沿该方向平移、腿部不走**。本段记录根因、修法与红/绿实测（含用户 Play 目视验证）。与 §二·H 的关系：#136 立的是"资产身份"，这条是它暴露出的第一个**行为**缺陷。

### 症状 → 根因（四环，缺一不成立）

| 环 | 事实（读源码/资产确认） |
|---|---|
| ① 决策层 | `ActionPlayer.TickLocomotion` 的**地面守卫**比较「本帧目标态 vs 缓存 `_locomotionTarget`」；而空中播 `Jump` 的那次 `CrossFade` **不进缓存**（空中分支赋值后直接 `return`） |
| ② 触发条件 | 落地目标与起跳前**同档**（走的仍是 Walk、跑的仍是 Run）→ 守卫判「无变化」→ **一次切态都不发**。只按住同一个键、甚至只换方向都不改变这个量；只有换挡（走↔跑）或松手才改变它 |
| ③ 状态机 | `ActionLab.controller` 零参数、零 transition（[动作库规格.md §四·甲](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md)：切态只由 C# 发 `CrossFade`）→ Animator **无法自行离开 Jump**；`Jump` clip `loopTime: 0` → 状态时间继续走、**姿势定格末帧** |
| ④ 位移层 | `ActionLabDriver` 落地帧即按 `dir * speed` 全速位移（`_cc.Move`） |

①+②+③ 让状态停在 Jump，④ 让身体照走 → 呈现为"平移"。

### 修法（`ActionPlayer.cs`，+25/−2）

1. 空中发 `Jump` 时置 `_returnFromJumpPending`，**落地边沿强制补发一次回切**（补发后清零，不逐帧刷）。
2. 决策层不再因缺 `Animator`/`runtimeAnimatorController` 提前 `return`——状态选择始终成立并留痕（新增只读面 `LastRequestedState` / `StateRequestCount`），使这条行为**无 controller 资产也能断言**。
3. `ResetToIdle()` 清 `_returnFromJumpPending`；Defend 判定抽成判空的 `IsCurrentState`。

设计侧无改动：行为与 [动作库规格.md §四·甲](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md)（回退 locomotion 目标态）同向，属缺陷修复；批次 4 迁契约 B（§四·乙）之后，**这条"落地边沿补发"仍需保留**（§四·乙：一次性动作 ↔ locomotion 的切换仍走 A）。

### 红 / 绿实测（Unity 6000.5.2f1 直驱 ActionLab 场景）

脚本输入模拟"按住方向键 + 跳一次"，逐 0.1 s 采样：

| 时刻 | 红（未修） | 绿（已修 `6bd8ddc`） |
|---|---|---|
| 起跳前 | `anim=Walk  spd01=0.50`（缓存 = Walk） | 同 |
| 落地帧 | `anim=Jump  grounded=True  spd01=0.36` | `anim=Jump  grounded=True  lastReq=Walk`（补发请求，`reqs` 2→3） |
| 落地 +0.2 s | `anim=Jump  nxt=0`（无过渡在途） | `anim=Jump  nxt=Walk`（过渡在途） |
| 落地 +0.4 s | `anim=Jump` | `anim=Walk` |
| 落地 +2.9 s | `anim=Jump`（仍在）· z 以 **3.05 m/s** 推进 · `y=0.08` 贴地 | `anim=Walk` · z 同速推进 · `reqs` 停在 3（不逐帧刷） |

**用户 Play 目视验证（2026-09-12，绑 `6bd8ddc`）**：按住方向键起跳 → 落地即回到走/跑动画，问题消失。

### 复现 / 复核方法（本机可直跑）

```bash
U="/mnt/c/Users/9527/AppData/Local/Unity/bin/unity.exe"; P="C:\Users\9527\game\code\unity"
"$U" command editor_play  --project-path "$P" --json
"$U" command eval --code '<取 ActionLabDriver → SetMoveInput(方向, 3f, false, true)；协程每 0.1 s Debug.Log 状态>' --project-path "$P" --json
"$U" command get_console_logs --project-path "$P" --json   # 返回按时间倒序，读时 tac 过来
"$U" command editor_stop  --project-path "$P" --json
```

- 读数量：`Animator.GetCurrentAnimatorStateInfo(0)`（`shortNameHash` / `loop` / `normalizedTime`）＋ `GetNextAnimatorStateInfo(0)`（`nxt=0` = 无过渡在途）＋ `CharacterController.isGrounded` ＋ `ActionPlayer.HorizontalSpeed01`。
- ⚠️ **两个参照柱会毁掉复现**：起点 `(0,0,0)` 朝 `+z` 走，会在 `z≈2.41` 顶住 `(0,0,3)` 的参照柱 → `CharacterController.velocity≈0` → `spd01=0` → 动画选 Idle → **起跳前缓存变成 Idle**，落地目标 Walk 与之不同，守卫反而会正常发切态，**bug 不复现**。要复现就走 `-z`（柱子只在 `(0,0,3)` / `(3,0,0)`，起点后方空旷）。
- 副产品读数（不算缺陷，但要知道）：顶住障碍时 `spd01=0` → 播 Idle，所以"被挡住"与"没输入"在动画上不可区分。

### 机器断言与残留

| 项 | 实测 |
|---|---|
| PlayMode | **21 项：19 过 / 2 红**；新增 `ActionLabLocomotionTests` **5 项全过**（同档落地必补发 / 原地跳落地回 Idle / 跑档落地回 Run / 补发只发一次 / 地面换挡仍发切态） |
| 2 项红 | 仍是 §二·H 残留缺口 ② 那两条既有缺陷（`OneShotElapsed` 阈值 / `ResetToIdle` 不清 `CurrentActionId`），本次**未顺手修**（[WORKFLOW.md §一](../../WORKFLOW.md)） |
| 编译 | Windows Editor **0 个 CS 错误**；Linux 侧用 Unity 6000.5.2f1 程序集单独编译 `ActionPlayer.cs` 也是 0 warning / 0 error |
| 候选队列 | ① `AnimatorWalker.cs` 有**同源守卫缺陷**（`CurrentAnimState` 空中不更新 + KiWalkerLab controller 零 transition）→ **KiWalkerLab 存在同一现象**，归 [#137](https://github.com/verystrongdog/game/issues/137) 工作面；② 上述 2 项常红 |

### 运维补充（修正 §二·G 的表述）

驱动 Unity 时**经 pipeline 写工程内文件不需要提权**——写盘由 Editor 进程完成（§二·G 那句"改 `/mnt/c` 下的文件需要提权"只对 shell 直写成立）：

| 命令 | 要点 |
|---|---|
| `write_text_file --path <工程相对路径> --contents "<文本>"` | 覆盖已有文件须加 `--confirm true`；支持多行 + 中文 + 引号 |
| `read_text_file --path <工程相对路径>` | 回读核对字节（本次用它验了两侧 sha256 一致） |
| `delete_asset --asset <路径> --confirm true` | 参数名是 `--asset`（不是 `--path`），删除须 `--confirm true` |
| `test_status` / `run_tests --mode playmode --async_tests` | PlayMode 测试**只能异步跑**（同步会因进 Play 触发域重载而断连），再轮询 `test_status` |
| 新增 `.cs` | Unity 导入时**自动生成 `.meta`**（GUID 由 Windows 侧决定）→ 仓库侧 `.meta` 必须采用该 GUID（[动作库规格.md §八](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) 资产区单机所有权） |

## 二·J、ActionLab 就座交互——先找到椅子才能坐（[#141](https://github.com/verystrongdog/game/issues/141)，2026-09-13）

> **要解决什么**：按 `6` 就播 `Sit`——**不看有没有椅子，也不看人在哪**。凳子位置是烘死的常量（`StoolCenterZ = −0.104`，按"角色 transform 在原点"实测摆位），所以"坐到椅子上"只在出生点成立；走开一步再按 6，人坐在空气里。本轮把"坐"变成**有前提的交互**：走到椅子前（距离 + 前侧 + 空闲三条件命中）才允许坐，命中后先对齐到**由椅子 transform 实时求得**的锚点再播坐下；起身同样要走完整动作。

**口径（正典）**：[动作库规格.md §四·丁](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) 新增就座交互契约（判定/对齐/占用锁/`ExitVia`）+ §四·乙 再修正（坐立三段重新启用 XZ 根位移）+ §七 参数行；`data/action_set.json` 同步两个新字段（`exit_via` / `root_motion_xz`，带 `_sources`）。

### 交付物与接入位置

| 件 | 干了什么 |
|---|---|
| `Assets/Scripts/ChairSeat.cs`（新） | 椅子组件：**实时**就座锚点（`坐面中心 + forward × 0.423`）· 判定纯函数 `IsUsable`（距离 + 前侧 + 空闲）· `FindBest`/`FindNearest` · 占用锁（`isKinematic`）· 与角色 CC 的碰撞忽略开关 |
| `Assets/Scripts/ActionCatalog.cs` | 词条新增 `ExitVia`（持续态退出先播的一次性动作）与 `RootMotionXZ`（XZ 根位移）两字段；`Sit`/`SitIdle`/`Stand` 声明 |
| `Assets/Scripts/ActionPlayer.cs` | 持续态退出走 `ExitVia`（坐姿下按 WASD **先起身**）· 暴露 `ApplyRootMotionXZ` · 一次性动作回退档位改按当前速度取 |
| `Assets/Scripts/ActionLabDriver.cs` | 按键 6 从"直接 `Play(Sit)`"改为**判定 → 对齐 → 坐下**；新增 `OnAnimatorMove`（XZ 根位移经 CC）与 `OnControllerColliderHit`（推椅）；HUD 显示椅子状态与拒绝理由；`TrySitOnNearestChair()` / `OccupiedChair` / `LastSitHint` / `LastAlignmentError` 为测试与读数面 |
| `Assets/Editor/ActionLabBuilder.cs` | 一张无碰撞凳子 → **三张实心可推椅子**（坐板 + 四腿 + 靠背 + Rigidbody + `ChairSeat`），摆位为演示常量 |
| `Assets/Tests/PlayMode/ActionLabChairTests.cs`（新） | 10 项断言 |
| `Assets/Scenes/ActionLab.unity` | 基准场景重建（椅子随 `.meta` GUID 入库；重建会覆盖，差异须显式提交——§二·H） |

### Unity 门禁实测（Editor 6000.5.2f1，WSL interop 直驱）

| 项 | 实测 |
|---|---|
| 编译 | **0 error**（`FindObjectsByType` 弃用告警已改；`rb.velocity` 由 Editor 的 API Updater 自动改写为 `linearVelocity`——**仓库侧随后采用了改写后的写法**） |
| PlayMode | **29 项：29 过 / 0 红**（原 33 = 既有 23 + #141 新增 10，减去 #126 花海移除的 4 项；花海移除后未重跑 Editor，此项为算术推断） |
| 判定链路 | 无椅子 → `TrySitOnNearestChair()` 返回 false、不切态、HUD 提示；有椅子 → 对齐 → `Sit` → `SitIdle`，椅子 `isKinematic=true` |
| 对齐残差 | **0.6 mm**（`LastAlignmentError`） |
| 坐姿落点 | 髋 ↔ 坐面中心水平偏差 **48.6 mm**（沿椅子 forward 44.0）；臀部（髋下 r≤0.30 m 蒙皮最低点）↔ 坐面上表面 **+4.8 mm**；足底 **+1.6 mm** |
| 根位移 | Sit 段 transform 水平行程 **0.3206 m**（沿椅子 forward **−0.3188**）——即 clip 自带的"退到椅子上" |
| 推椅 | 椅子位移 **36.3 mm** → 锚点位移 **36.3 mm**（锚点确实实时） |
| 抓帧 | `capture_game_view` 640×360；`.scratch/sit-seated.png`（不入库，过程物） |
| **owner 目视（Play，2026-09-13）** | **通过**——目视清单 ⑧（走到椅子前按 6 就座 / 走开不坐下 / 坐姿按 W 先起身 / 推开椅子后仍命中）与"椅子高度观感"均无问题；本行是试玩证据，绑提交 `2b57b03` |

### 🔧 本轮踩到并修掉的一处既有缺陷：角色整体悬浮 80 mm

**症状（owner 目视）**：「椅子本身好像不够高」。**真因不是椅子矮，是人高**——`CharacterController.skinWidth` 默认 `0.08`，而 CC 静止时 `transform.y ≈ skinWidth` → 整个角色被抬到地面上方 80 mm（实测站姿蒙皮足底 **+45.8 mm**、坐姿髋 **0.6790**，按 transform 在原点应为 0.5990）。坐面高 0.4449 是"transform 在原点"时测的，于是臀部比坐面高 80 mm。

**为何此前没暴露**：[动作库规格.md §四·乙](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) 的足 IK 假定 `groundY = 0` 且**只上抬不下压**——transform 抬高后足底本就"在地面之上"，IK 判"需要量 ≤ 0"而不介入（既有读数"逐位一致"正是这条规则的结果，不是没问题）。

**修法**：`ActionLabDriver.SizeControllerToModel()` 里把 `skinWidth` 收到 **0.005**（**必须在 Awake / CC 落定前设**；中途改无效——实测改到 0.02 后 3 s 仍停在 0.08，CC 只排开穿插、不会自己往下坐）。修后：站姿足底 **+4.9 mm**、站姿髋高 **1.025**、坐姿臀↔坐面 **+4.8 mm**、坐姿足底 **+1.6 mm**。

### 三条新踩的坑（已写进 [unity-cli README §四](../../code/tools/unity-cli/README.md)）

1. **Unity 6 在窗口处于后台时节流主线程** → 所有 `unity command` 报「Main thread operation timed out after 30000ms」，而 `unity status` 仍 `ready`（健康检查走后台线程）。**`editor_focus` 自己也走主线程**（所以节流后救不回来）→ 用新增的 `code/tools/unity-cli/focus.sh` 从 Windows 侧把窗口调到前台。
2. **直接 `cp` 进 `Assets/` 的新文件由 Unity 生成 `.meta`**（GUID 由 Windows 侧定），仓库侧必须采用同 GUID——本次两个新文件：`ChairSeat.cs` = `31496bc4…`、`ActionLabChairTests.cs` = `e5c01136…`。
3. **Editor 的 API Updater 会改写你同步过去的源文件**（`rb.velocity` → `rb.linearVelocity`）→ 两次同步之间会出现"两侧不一致"，先 diff 再判定是谁改了谁。

## 二·K、脑壳资产入库（[#143](https://github.com/verystrongdog/game/issues/143)，2026-09-13）

> 把 3D 脑区面板要用的**真实脑曲面**烘成一份可进工程的 mesh。资产身份契约（`.meta` GUID 由 Editor 定、仓库采用同 GUID）见 §二·H；本节的动线是它的第一次实战。

### 交付物与接入位置

| 项 | 值 |
|---|---|
| 资产 | `code/unity/Assets/SkillTree/Models/brain_shell.fbx`（**6.8 MB** · 双侧 · sha256 前 16 `20f3424f0139b6fe` —— [#147](https://github.com/verystrongdog/game/issues/147) 替换；单侧旧值 `e983c347471e0827`） |
| 目录 | `Assets/SkillTree/`（GUID `44b2e4aa2db3ccb45bd480b630e04fc0`）· `Assets/SkillTree/Models/`（GUID `42a08dffda1b07d4890feda12e5e2026`） |
| 资产 GUID | `6551384821590304e9bb1979565e9b4e`（**由 Editor 生成**，仓库采用同一值） |
| 来源 | `code/tools/bake_brain_shell.py` ← `data/brain_regions.json` 的 **40 个受控解剖载体 × 两侧**（58 个 functional_id 共享这些载体） |
| 对侧口径 | 契约的 58 条 `obj_file` **全为左半球**，故烘焙侧按**命名约定**派生对侧：`lh.`↔`rh.` · `Left-`↔`Right-`，并**逐个校验存在性**（实测 40/40 都有真实对照文件 → 用真实网格，不做几何镜像）。**派生规则只从既有契约字段推导，故不新增第二份真相源、不动数据契约**（理由见 [#147](https://github.com/verystrongdog/game/issues/147)） |
| 接入位置 | 工程资产区。**未接进任何场景**：装配属视图实现，等归属与准入裁定（[#145](https://github.com/verystrongdog/game/issues/145)） |

### 导入动线（实测跑通，2026-09-13）

```bash
# 1) 烘焙到 gitignored 的 build 目录（默认落 blender_assets/build/）
blender.exe --background --factory-startup \
  --python code/tools/bake_brain_shell.py

# 2) 建目录 + 导入（Editor 在 Windows 侧执行，故经 unity-cli 而非 cp——
#    沙箱把 /mnt/c 设为只读，且 .meta GUID 必须由 Editor 生成）
./code/tools/unity-cli/uc.sh create_folder Assets/SkillTree
./code/tools/unity-cli/uc.sh create_folder Assets/SkillTree/Models
./code/tools/unity-cli/uc.sh import_asset \
  --source '\\wsl.localhost\Ubuntu-22.04\home\dog\game\design\presentation\visualization-3d\blender_assets\build\brain_shell.fbx' \
  --path   'Assets/SkillTree/Models/brain_shell.fbx'

# 3) 把产物搬进仓库（Linux 侧）：FBX 字节与 Editor 侧逐字节一致（sha256 可核），
#    .meta 采用 Editor 生成的 GUID
```

> **为什么不是 `cp` 进 `Assets/`**：本机沙箱把 `/mnt/c` 设为只读，写不进去；`import_asset` 由 Editor 自己执行，顺带完成 `.meta` 生成——与 §二·H 的"GUID 由 Windows 侧定"是同一件事。

### 实测读数（Editor 6000.5.2f1，`unity-cli` 经 WSL interop 直驱）

| 项 | 读数 | 判据 |
|---|---|---|
| 区域对象数 | **40** | `MeshFilter` 计数（= `obj_file` 去重后的载体数） |
| 无 mesh 对象 | 0 | — |
| 共享材质数 | **8** | `MeshRenderer.sharedMaterials` 去重（bake 侧同为 8） |
| 顶点数 | 507,950 | Unity 侧 weld 后 |
| 三角面（烘焙侧） | 199,966 | `bake_report.json`（预算 20 万，达成 100%） |
| 导入设置 | `globalScale: 1` · `animationType: Generic` · `clipAnimations: []` | `.fbx.meta` |
| 字节一致性 | Editor 侧与仓库侧 FBX sha256 逐字节相同 | 见上表 |

### ⚠️ 本轮三个发现（已全部裁定/处置，2026-09-13）

| # | 发现 | 处置 |
|---|---|---|
| 1 | **Console 非 0 错误，但与本次导入无关**——最近一条是 `ActionLabDriver.cs` 的 `CS0103: The name 'chair' does not exist`（01:35:51Z，早于本次导入 3 小时，且**当前该文件第 212 行根本没有这个标识符**，属中间态残留） | ✅ **已按 owner 裁定处理**：对齐 Windows 拷贝（§二·H 的 `fetch` + `reset --mixed`，HEAD `fa60ef1` → `ed44ccd`，工作树未动、两处分叉保留）后**强制一次重编译**（`RequestScriptCompilation` → `recompile_status: completed`）——**新增 error 0 条**；控制台内 6 条历史 error 全部可归因（1 条旧编译残留 + 5 条本次探测命令缺参数）。详见 #143 评论 |
| 2 | **FBX 未携带 `functional_ids`**——对象名只带**主** `functional_id`（如 `AccumbensShell`）；`functional_ids` / `lobe` 字符串在 FBX 中零命中（Blender FBX 需 `use_custom_props` 才导出自定义属性） | **owner 裁定：不加进 FBX**。完整映射运行时读 `data/brain_regions.json` 的 `obj_file` 字段（本就受控）——FBX 不背第二份真相源；[#143](https://github.com/verystrongdog/game/issues/143) 的 AC 已据此改写并退回 triage |
| 3 | **尺度口径矛盾**（本次新发现）——资产是 MNI 毫米（世界包围盒 72.5 × 169.3 × 121.6），而 [Unity接入设计 §五](../presentation/visualization-3d/Unity%E6%8E%A5%E5%85%A5%E8%AE%BE%E8%AE%A1.md) 原写"单位 m" | **owner 裁定：视图内部统一用 MNI 毫米 + 根部单一等比变换（≈1/90）**；`game_xyz`/§14.1 明确为**点位映射**（Z 除以 148.2，非等比），不得当作网格变换——否则网格与节点在 Z 轴差 1.65 倍。已落 [Unity接入设计 §8.5](../presentation/visualization-3d/Unity%E6%8E%A5%E5%85%A5%E8%AE%BE%E8%AE%A1.md) |

> **门禁基线提醒**：本节的 Editor 读数取自 `C:\Users\9527\game`（Editor 实际打开的拷贝）。跑 `unity` 门禁前先读 `projectPath` 与仓库 HEAD 的距离——见[危险点表](../engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md) §七「`unity status` 的 `projectPath`」行。

### 怎么复核

```bash
sha256sum code/unity/Assets/SkillTree/Models/brain_shell.fbx   # e983c347471e0827…
grep '^guid:' code/unity/Assets/SkillTree*/**/*.meta 2>/dev/null || \
  grep -h '^guid:' code/unity/Assets/SkillTree.meta \
    code/unity/Assets/SkillTree/Models.meta \
    code/unity/Assets/SkillTree/Models/brain_shell.fbx.meta
./code/tools/unity-cli/uc.sh eval 'var go = UnityEditor.AssetDatabase.LoadAssetAtPath<UnityEngine.GameObject>("Assets/SkillTree/Models/brain_shell.fbx"); return go.GetComponentsInChildren<UnityEngine.MeshFilter>(true).Length;'
```

---

## 二·L、只读骨架 BrainViewLab（[#146](https://github.com/verystrongdog/game/issues/146)，2026-09-13）

> 把 [#143](https://github.com/verystrongdog/game/issues/143) 入库的脑壳接进一个**独立演示场**：脑壳 + 脑区 + 1049 条三体边 + 相机绕看。**零玩家可操作行为**——玩家的可操作面（构建层聚焦配置等）按 [#145](https://github.com/verystrongdog/game/issues/145) 的裁定随切片准入进入。

### 交付物与接入位置

| 项 | 值 |
|---|---|
| 场景 | `code/unity/Assets/Scenes/BrainViewLab.unity`（独立演示场，与 `ActionLab` 并存、互不引用；**未加入 Build Settings**） |
| builder | `code/unity/Assets/Editor/BrainViewLabBuilder.cs` — 菜单 **YANTF → 大脑视图 → 创建 BrainViewLab 场景** |
| 运行时 | `code/unity/Assets/Scripts/BrainViewRig.cs`（根变换 / 计数 / 脑壳透明度）· `BrainLinkRenderer.cs`（三体边 → 单 Mesh + 16 材质槽，内含极简 JSON 解析器） |
| 断言 | `code/unity/Assets/Tests/PlayMode/BrainViewSmokeTests.cs`（5 条，判据全部读数据推导） |

### 实测读数（Editor 6000.5.2f1 · 基线 `C:\Users\9527\game\code\unity`）

| 判据 | 读数 |
|---|---|
| builder 产出 | 脑壳 区域对象 **80**（数据侧载体 40 × 双侧；**左 40 / 右 40**）· 材质 **8**（不因双侧增加） |
| | 链路 **1049** 条 · submesh **16** · 材质 **16** |
| 根变换 | rot **(270, 0, 0)**（= −90° X）· scale **0.01111**（= 1/90，口径见接入设计 §8.5） |
| 网格/链路对齐 | links 世界包围盒中心落在 shell 包围盒内 **True**；轴向比 shell/link = **0.71 / 1.15 / 1.19**（shell 是左半球、链路跨双侧，故 X 更窄——比例关系自洽） |
| PlayMode 测试 | **38/38 通过**（含本条 5 条；其余 33 条为阶段回归，无失败） |
| 抓帧 | 非背景像素 **3.9%** · 内容包围盒 **211×262 px** · 非背景平均亮度 **158** · 色相桶 **11/12 非空**（多网络链路确实在渲染） |

### 观察方式：**转模型**，不是转相机（[#148](https://github.com/verystrongdog/game/issues/148)）

owner 反馈"用摄像机调整角度看大脑模型有点费劲"，故观察交互改为**模型自转 + 固定机位**：盯住某个脑区时观察者始终在同一侧，空间关系稳定（相机绕行会同时改变朝向与背景）。后续玩法面要在脑区上点选，这个手感会被继承。

| 输入 | 效果 |
|---|---|
| 右键拖动 | 水平 = 绕**世界 Y** 自转 · 垂直 = 绕**世界 X** 俯仰（俯仰夹取 ±85°，防上下颠倒） |
| 滚轮 | 缩放——改的是**相机距离**，不是模型缩放（后者会同时放大脑区间距，观感不同） |
| `R` | 复位（yaw/pitch 归零，距离不变） |

**结构上为什么分两层**：`Spin`（`BrainViewSpin`，只表达**观察角**）→ `BrainView`（`BrainViewRig`，承担**资产基线 −90° X** + 等比 1/90）→ `BrainShell`/`Links`。自转若与资产基线复合同一个 transform，既难读也难验（分不清哪部分是资产口径、哪部分是观察角）。

**驱动实测**（`SetView()` 是给 builder/断言用的公开入口；判断"转的是模型"的判据不是"看着对"）：

| 设定 | `Spin` 旋转 | 相机旋转 | 相机距离 | 画面 md5 / 包围盒 / 非背景 |
|---|---|---|---|---|
| yaw 0 · pitch 0 | (0, 0, 0) | **(12, 0, 0)** | 2.80 | `ceba1d92d0` · 339×317 · 9.3% |
| yaw 45 · pitch 20 | **(20, 45, 0)** | **(12, 0, 0)** | 2.80 | `efd18a53e4` · 403×311 · 10.1% |
| yaw −60 · pitch 35 | **(35, 300, 0)** | **(12, 0, 0)** | 2.80 | `2f7a67521c` · 388×361 · 10.4% |

⚠️ **"拖动 → 角度"这一段无法机器验证**：本工程输入是**旧版 Input**（`ProjectSettings.activeInputHandler = 0`），而 Unity 的 `simulate_pointer` **只支持新输入系统**（实测报 `Legacy input injection is not supported.`）。故可机器验证的是 `SetView()` 之后的链路（角度 → 变换 → 相机不动），**拖动手感由 owner 目视**——见下方记录。

### owner 目视验证（2026-09-13）

> owner 原话：**"目视没有问题"**。

| 验证项 | 载体 | 结论 |
|---|---|---|
| 观察交互：右键拖动转模型 / 滚轮缩放 / `R` 复位的手感与方向 | `Assets/Scenes/BrainViewLab.unity`（Play） | ✅ 无问题 |
| 整脑观感（对侧半球补齐后的完整形态） | 同上 | ✅ 无问题 |

这条同时补上了两处机器判不了的空白：**#148 的"拖动 → 角度"**（旧版 Input 不支持注入）与 **#147 的"看起来是不是一整颗脑"**（形状/比例属目视范畴）。

### 坐标口径（实测，非推导）

资产以 **MNI 轴向**存储、单位毫米，在 Unity 里是**躺着**的：

- 以 40 个载体的网格质心对 MNI 标签坐标做候选映射拟合 → `资产空间 = (−mni_X, mni_Y, mni_Z)`，平均绝对误差 **9.5 mm**（次优候选 30 mm 以上）
- 故根部施加 **−90° X 旋转**使其立起 + **等比 1/90**
- FBX 导入的局部缩放实测为 **100**（Unity 对 Blender 单位的换算），由根变换统一处理

### ⚠️ 诚实清单（四项，均已在案）

| # | 事项 | 说明 |
|---|---|---|
| 1 | **链路在 builder 时生成，不是 Play 时** | 场景自带烘好的链路 Mesh；改 `data/` 后需**重跑 builder**才反映。这与接入设计 A7"改数据不改场景"尚有距离——A7 的达成需要数据进 Assets（生成式 C# 静态表，参考 [#138](https://github.com/verystrongdog/game/issues/138) 的方向），属后续工作面 |
| 2 | ~~脑壳只覆盖左半球~~ → ✅ **已解决（[#147](https://github.com/verystrongdog/game/issues/147)，2026-09-13）** | 对侧按命名约定派生并用**真实网格**补齐：40 载体 → **80 区域对象**（左 40 / 右 40）。实测画面非背景像素 3.9% → **7.9%**、内容包围盒 211×262 → **309×274 px**。**未改数据契约**（派生规则只依赖既有 `obj_file` 值） |
| 3 | **脑壳不透明度被运行时改写过** | 烘焙件沿用 v2 世代的逐脑叶 `alpha=0.10`，深色背景下近乎不可见；该材质是**导入资产的内嵌材质**，直接改不持久（重导入即还原）→ `BrainViewRig` 用 `MaterialPropertyBlock` 覆盖为 **0.35**（呈现层取值，可调），不碰资产 |
| 4 | **`write_text_file` 与仓库版差一个尾换行** | Editor 侧写出的文件无尾换行（`.meta` 同现象），仓库侧有。逐文件 `diff` 只此一处差异；已核对 **API Updater 未改写任何源码**（危险点表 §七 的行） |
| 5 | **测试不得断言 gitignore 资产的存在** | 首版"对侧文件存在性"断言在 Windows 侧**假失败**——那份拷贝里没有 `all_obj/`（gitignore，从未复制过去）。已改为两层判定：**命名约定（字符串层）必判**，**文件存在性（文件层）仅在目录可用时判**并留痕。教训：断言只能依赖"每个环境都有的东西" |

### 怎么复核

```bash
./code/tools/unity-cli/uc.sh menu "YANTF/大脑视图/创建 BrainViewLab 场景"   # 幂等：重建场景
./code/tools/unity-cli/uc.sh editor_play                                   # 进 Play
./code/tools/unity-cli/uc.sh capture_game_view --source camera --save_path Assets/Temp/brainview.png
./code/tools/unity-cli/uc.sh run_tests && ./code/tools/unity-cli/uc.sh test_status
```

> builder **幂等**：每次都 `NewScene(EmptyScene)` 从零重建，无手工挂载件（危险点表 §四 的"一切折进 builder"）。重复执行不产生重复对象——实测两次运行的计数完全一致。

---

## 二·M、派生件加「镜像」变换（[#150](https://github.com/verystrongdog/game/issues/150)，2026-09-13）

> 给派生件机制加**第二种变换**：此前只有时间反转（`Derived/SitDown.anim`）。本条产出格挡 clip 的 **Humanoid L/R 镜像件**，把盾手从左手换到右手（规格 §四·戊·1#6：单手链统一右手）。

### 交付物与接入位置

| 项 | 值 |
|---|---|
| 生成器 | `code/unity/Assets/Editor/DerivedClipBuilder.cs` — 新增 `DeriveMirrored()`（纯函数）· `FixRootTranslation()`（实测根修正）· `MirrorCheck()`（骨骼级断言）；菜单 **YANTF → 动作演示 → 重建派生动画（格挡镜像）** |
| 资产 | `code/unity/Assets/Animations/Derived/Defend_Carry1H_Mirrored.anim`（+ `.meta`）——130 曲线 / 1.4000 s / `humanMotion` ✓ / `loopTime` ✓ |
| 断言 | `code/unity/Assets/Tests/PlayMode/ActionLabGripTests.cs`（新建，4 条）：镜像位姿 / 播放口径 / 非破坏对拍 / 二次镜像回原件 |
| 接入 | **本条不接线**：controller 状态与按键属「持椅状态链接线」issue（§戊·1#4 的 `Variants` 解析） |

### 实测读数（Editor 6000.5.2f1 · 基线 `C:\Users\9527\game\code\unity` @ 仓库 HEAD `6ea806a`）

| 判据 | 读数 |
|---|---|
| 镜像变换三条口径 | 见 [动作库规格.md §戊·3](../../design/presentation/动作库规格.md) 实测块：肢体肌肉符号全 +（4.98–5.54 mm 基线 vs 反号 30–1400 mm）· 中轴含 `Left-Right` 取 −（4.98 mm vs 30–400 mm）· 根位移按载体实测解 |
| 骨骼级镜像 | `LeftHand`↔`RightHand` 世界位差 **0.069 mm** · 全骨扣掉骨架自身不对称 **0.52 mm** · 世界旋转 **0.00000°** · **对照项**（不对拍左右）**1199 mm** |
| 骨架自身不对称 | 无名指中节/末节 **2.283 / 1.68 mm**（rest 姿势同口径读数）——故全骨判据扣掉它，否则任何镜像都会"超差" |
| 根位移 | 朴素的「`RootT.x` 取负」残差 **4.59 mm**（全骨一致）→ 实测求解后 **0.0002 mm** |
| 非破坏 | 重建镜像件后 `Derived/SitDown.anim` **逐曲线不变**（`git status` 无该文件）· `VerifyDerived()` 覆盖两件并报 **0** |
| 门禁 `unity` | `run_tests` **47/47 通过**（含本条 4 条）· 强制重编译后新增 error **0** |
| 门禁 `unity-assets` | `validate_unity_assets.py` 四条规则全过（受控 Unity 文件 155、A1 0 · A2 0 · A3 0 · A4 0） |

### 🔴 owner 目视：不通过（2026-09-13）

**owner 在同一批读数截图（格挡原件 vs 镜像件）上判定「镜像/格挡也有问题」。**
注意：本节那些机械判据**全部为真**（逐骨镜像 0.069 mm、根位移 0.0002 mm、非破坏、`run_tests` 含本条 4 条全过）——**是"看起来不对"，不是"算错了"**。这正好是机械判据抓不到的一类：

- 镜像把 `Sword And Shield Block Idle` 的**盾手换到右手**，但**整套姿势仍是借来的持械姿势**（椅子不是盾）；
- 同一批图里还有椅子挂点的问题（见 §二·N），两个问题**在同一张图上叠着**，故"格挡看着不对"里有多少属镜像、多少属椅子，尚未逐项分离；
- **具体错在哪需要 owner 描述，或补拍更干净的对照**（不含椅子、原件 vs 镜像件、多取几个时刻）。这一条**未闭合**。

**与 §二·N 同属一个更大的判断**：owner 已裁定**暂停**「手里有东西」这条线，理由是「可能设计思路出问题了」——而"借 Mixamo 的持械/搬物姿势 + 把道具贴到手骨 + 镜像换手"正是那条思路的三个组成部分。

### ⚠️ 本轮两个新坑（已进[危险点表](../../design/engineering/危险点表.md) §七）

1. **`bodyPosition → 根节点世界位` 是按 Avatar 不同的仿射映射**：`∂Hips/∂p = 1.050·I` 且 `p=0` 时 Hips 不在原点（X Bot 偏 `(−1.67, −25.0, −18.2) mm`）。所以"把 `RootT.x` 取负"**不等于**镜像根位移——必须按目标载体实测解。代价实测：不修则整体偏 4.59 mm（看着完全对，量出来超差）。⇒ 镜像件**与载体绑定**，换载体要重跑生成器。
2. **`AnimationMode` 采样必须"窗口内读"**：`EndSampling` 会回滚上一次采样，跨窗口读骨骼拿到的是 rest——同一份 eval 因此把 4.6 mm 量成 26 mm、旋转量成 4°，方向完全错。

### 怎么复核

```bash
./code/tools/unity-cli/uc.sh menu "YANTF/动作演示/重建派生动画（格挡镜像）"   # 幂等：重算 + 写盘
./code/tools/unity-cli/uc.sh run_tests && ./code/tools/unity-cli/uc.sh test_status   # 47 条（含 ActionLabGripTests 4 条）
python3 code/tools/validate_unity_assets.py                                        # A1–A4
```

> ⚠️ 跑 `unity` 门禁前先读 `editor_status` 的 `projectPath` 并核对与仓库 HEAD 的距离（危险点表 §七），跑 `run_tests` 前先 `focus.sh`。

### 回滚演练（实测）

`git revert` 本条提交组时**必须按时间倒序**（`git log --oneline 6ea806a..HEAD` 从新到旧）——正序会冲突（`fix` 提交改的正是 `feat` 引入的那几行；实测报 `hint: after resolving the conflicts…`）。倒序 revert 后，临时 worktree 的工作树与基线 `6ea806a` **逐字节一致**（`git diff 6ea806a` 为空）：镜像件与 `ActionLabGripTests` 连同 `.meta` 一并消失、`Derived/` 只剩 `SitDown.anim`，即 `DerivedClipBuilder.cs` 退回"只做时间反转"。**无数据迁移**；`VerifyDerived()` 恢复为只校验 `SitDown.anim`（回滚后的文件与基线逐字节相同，故该行为由同一性保证——Unity 层未重跑）。

---

## 二·N、持椅挂点组件（[#152](https://github.com/verystrongdog/game/issues/152)，2026-09-13）

> 「手里有东西」这一层在代码里**此前完全不存在**（全工程唯一 `OnAnimatorIK` 在 `FootGroundingIK.cs`：无挂点代码、无 `GetBoneTransform`、无父级切换）。本条是规格 §一 道具口径（「不换模型，作为**骨骼挂点道具**」）的**第一次落地**，实现 §戊·2 的三个机制件。

### 交付物与接入位置

| 项 | 值 |
|---|---|
| 组件 | `code/unity/Assets/Scripts/ChairGrip.cs`（挂在场景椅子上，与 `ChairSeat.cs` 共用同一把椅子）——可握锚点表 / 逐状态挂点表 / 自动对齐 / 手到位帧读数 / 阻尼摆动 / 挂点与解除 |
| builder | `code/unity/Assets/Editor/ActionLabBuilder.cs` — `BuildGripAnchors()`（锚点由椅子几何常量算出，**局部坐标**）· `DefaultGripPoses()`（逐状态表）· 给椅子挂 `ChairGrip` |
| 场景 | `code/unity/Assets/Scenes/ActionLab.unity` 已重建并显式提交（3 张椅子各带挂点组件；关键标记计数逐个对齐：ChairSeat 3→3 · CameraOrbit / FootGroundingIK / ActionLabDriver / ActionPlayer / CharacterController 各 1→1 · Rigidbody 3→3） |
| 断言 | `code/unity/Assets/Tests/PlayMode/ActionLabGripTests.cs` 新增 6 条（锚点实时性 / 三者同时 / 逐状态基准朝向 / 手到位帧 / 阻尼收敛 / 与就座不互抢） |
| 接入 | **本条不接线**：状态机、按键、`Variants` 解析属「持椅状态链接线」issue；副手 IK 属双手链 issue |

### 实测读数（Editor 6000.5.2f1 · 基线 `C:\Users\9527\game\code\unity`）

| 判据 | 读数 |
|---|---|
| 锚点实时性 | 推椅 0.8 m → 锚点同步 **0.8 m**（容差 1 mm）；转向 130° 后仍贴在椅子几何上；锚点 ≠ 椅子原点（对照项） |
| 逐状态基准朝向 | `Carry1H` 垂下 / `Wield2H` 横在身前 / `DefendCarry1H` 当盾 → 两两夹角 **120° / 120° / 180°**；手骨平移+旋转后组内位姿**逐位稳定**，锚点始终落在手骨原点（≤1 mm） |
| 手到位帧（距离曲线最低点） | 角色在原点、椅子正前 1.6 m、41 点采样：`Lift1H` **t=0.325**（1662.9 → 1374.7 → 1767.2 mm，真低谷）· `Carry1H` t=0.750 · `Wield2H` t=0.425 · 镜像格挡 t=0.375 |
| 挂点"三者同时" | 父子到 `RightHand` ✓ · 椅子 `isKinematic` ✓ · `Physics.GetIgnoreCollision(cc, 椅子)` ✓——解除时三条一起还原 |
| 阻尼摆动 | 刚度 120 / 阻尼 18（ζ≈0.82）→ 收敛 **0.800 s**，残差 0.0015 m / 0.00000°，随后**精确定位**到基准；刚度 0 → 耗时为 0 的刚性退化（A） |
| 两种占用不互抢 | 就座占用中 → 挂点被拒（理由留痕"椅子正被就座占用 → 拒绝挂点"）；解除后挂点成功 |
| 门禁 `unity` | `run_tests` **53/53 通过**（含挂点 6 条 + 镜像 4 条；这是 #152 当时的读数） |
| 门禁 `unity`（🔧 2026-09-13 复跑 · #155） | `run_tests` **51/51 通过**——白盒 Demo 沙盘退役后 `DemoSmokeTests` 的 2 条随之删除（53 − 2 = 51，**实测非推断**）；强制重编译后新增 error **0** |
| 门禁 `unity-assets` | 受控 Unity 文件 **161**（`.meta` 75）· A1 0 · A2 0 · A3 0 · A4 0（17 条受控 FBX 全 Humanoid） |
| 门禁 `unity-assets`（🔧 2026-09-14 复测） | 受控 Unity 文件 **141**（`.meta` 65）· A1 0 · A2 0 · A3 0 · A4 0（17 条受控 FBX 全 Humanoid）——**上一行的 161 是该轮当时的读数，保留不改**。差额 **20** = #155 退役的 **10 资产 + 10 `.meta`**（`SceneBuilder` / `CharacterVisual` / `DemoActor` / `DemoBootstrapper` / `DemoCombatDriver` / `DemoHud` / `DemoSolver` / `DemoTypes` / `DemoSmokeTests` / `SitPoint`），逐条经 `git log --diff-filter=D 6ea806a..HEAD -- code/unity/Assets` 核对——**不是丢文件** |

### ⚠️ 未闭合（诚实清单）

1. **🔴 owner 目视：不通过（2026-09-13）**——原定「三个基准朝向角度与刚度/阻尼待目视调」这一步做了，结论比"调角度"严重得多。
   **owner 原话**：「**忽略了碰撞体积，人体模型根本不是用人类的方式跟椅子在进行互动**」；并点名两处现象：**左手没扶椅子**（双手姿势只有一只手在持）、**椅子没握在手里（悬空 / 穿模）**。
   **我的实测读数（对上他的判断）**：
   - 锚点**精确**落在手骨原点：右手 → 椅子表面距离 **0.0000 m**（`DefendCarry1H`）——机制**按设计工作**，问题不在"没挂上"，在"挂上了也不像人拿"；
   - 同一姿势下**左手离椅子表面 0.7415 m**（两手间距 0.999 m）——"当盾"只有一只手在持，另一只手悬在 74 cm 外；
   - `Carry1H`（垂下）挂 `leg_front`、`Wield2H`/格挡挂 `backrest_rail`，三组基准朝向 `(0,0,90)`/`(90,0,0)`/`(90,0,180)` 都只是**绕手骨的转角**——椅子是按"点"贴到手骨上的，没有"手包住构件"这回事；
   - 挂点期间椅子 `isKinematic=true` 且与角色 CC 的碰撞被忽略（**这是规格 §戊·2 明写的设计**，不是 bug）——即"没有物理交互，只有贴附"。
   **结论**：这不是调三个 euler 角度能修的观感问题，而是**规格 §戊·2 的挂点机制本身在视觉上不成立**（缺副手 IK、缺握持姿态匹配、且明确不做碰撞交互）。已升级为需要 owner 裁定的设计问题，见下方第 1′ 条。
1′. **✅ owner 已裁定（2026-09-13）：暂停这条线**——原话「**先暂停吧，可能设计思路出问题了**」。
   **据此执行的口径**：
   - **不再**往"接线 / 调参 / 补副手 IK"方向推进——不是排期问题，是**思路本身要重新审视**（§戊·2 的 19 条决策机械上成立、视觉上不成立）；
   - `ChairGrip.cs` 与那 6 条断言**保留**（它们各自是对的，且是将来任何新方案的回归面），但**整套「挂点 = 把椅子贴到手骨 + 关掉物理」的思路待重新设计**；
   - 下游 [#153](https://github.com/verystrongdog/game/issues/153)（单手链）/ [#154](https://github.com/verystrongdog/game/issues/154)（双手链）建立在这个机制上 → **保持 `state:blocked`，且不得被当成"机制已就绪即可开工"**；
   - **在思路收敛并形成新的设计决策之前，本文档与 `slice.md` 的「持椅交互」行都不得声称该层"已落地"。**
   - 设计侧入口：重新审视 [动作库规格.md §四·戊](../../design/presentation/动作库规格.md)（该节已加 🔴 状态注）。按 [issue-process.md §三](../../design/engineering/issue-process.md)，**讨论阶段不建 issue**——先出决策，再分解。
2. **未接线**：本条不驱动状态机（链接线 issue 才会让 `Lift1H`/`Carry1H`/`Wield2H`/格挡各自挂上并按"手到位帧"切换）。
3. 场景重建是**整文件重写**（builder 每次 `NewScene`）——与前两次重建同口径（#141 那次 3620/777 行），差异已显式提交。

### 怎么复核

```bash
./code/tools/unity-cli/uc.sh menu "YANTF/动作演示/创建 ActionLab 场景"   # 幂等：重建场景（含挂点组件与两张表）
./code/tools/unity-cli/uc.sh run_tests && ./code/tools/unity-cli/uc.sh test_status   # 51 条（#155 后实测）
python3 code/tools/validate_unity_assets.py                                          # A1–A4
```

> 只读读数（不重建场景）：调 `ChairGrip.MeasureHandArrival(animator, clip, state)` 与 `StepSwayToSettle(...)`——读数都写进 `LastArrival` / `LastSwaySettleSeconds` / `LastAttachReport`。

---

## 二·O、Animation Rigging 接入（2026-09-14）

> 给「手里有东西」这条线**预备**约束工具：`com.unity.animation.rigging` 1.4.1 入库。**本次只接接入点与能力探针，不产生任何行为**——规格 §四·戊·2 #11 的副手 IK 属被暂停的那条线（见本文件 §二·N 未闭合 1′），**未实现**。

### 交付物与接入位置

| 项 | 值 |
|---|---|
| 依赖 | `Packages/manifest.json` + `packages-lock.json` 净 **+3**（`animation.rigging` 1.4.1 / `burst` 1.8.29 / `mathematics` 1.4.0）；同批装入的 `com.unity.formats.fbx` 已按 owner 裁定撤除（提交 `dcc0073`） |
| builder | `Assets/Editor/ActionLabBuilder.cs` — `BuildRigInfrastructure(actor, animator)`（幂等，折进 `CreateScene`）+ `VerifyRigInfrastructure(actor)`（建场景后自检；骨链空 / 权重非 0 / layers 数不对 → `LogError`） |
| 场景 | `ActionLab.unity` 重建：载体上 `RigBuilder` + `Rig(AnimationRigging)` + `LeftArmIK`（TwoBoneIK：`LeftUpperArm`→`LeftLowerArm`→`LeftHand`）+ 哑目标 `LeftHandTarget`；**`rig.weight = ik.weight = 0`（惰性）** |
| 断言 | `Assets/Tests/PlayMode/AnimationRiggingProbeTests.cs`（新建 2 条，**都在真场景上跑**，不另搭合成 Rig） |
| build settings | `ProjectSettings/EditorBuildSettings.asset`：`ActionLab` 登记为 **index 0**（测试经 `SceneManager.LoadScene` 按名加载） |
| 白名单 | `code/tools/validate_unity_assets_exceptions.json` 新增 **`package_guids`** 段（3 条包脚本 guid）。该段生命周期**跟锁文件走**——换 `animation.rigging` 版本须回核这三条；`validate_unity_assets.py` 的汇总与 verbose 明细已同步支持该段 |

### 实测读数（Editor 6000.5.2f1 · 基线 `C:\Users\9527\game\code\unity`）

| 判据 | 读数 |
|---|---|
| 结构（断言 ①） | `RigBuilder` 层数 **1** · 骨链 `root/mid/tip` 与 `HumanBodyBones.LeftUpperArm/LeftLowerArm/LeftHand` **逐骨相等** · `rig.weight = ik.weight = 0` |
| 能力（断言 ②） | 真场景 Play：层 `IsValid()=True` · `constraints=1`；权重拉满 + `RigBuilder.Build()` 后 **手↔目标 = 0.0 mm**（对照：权重 0 时 **187.1 mm**；目标偏移模长 187 mm） |
| 门禁 `unity` | `run_tests` **53/53 通过**（含本条 2 条）；强制重编译后新增 error **0** |
| 门禁 `unity-assets` | 受控文件 141（`.meta` 65）· A1 0 · A2 0 · **A3 悬空 0**（经允许清单放行 88：builtin 81 / package 3 / known 4）· A4 0 |
| 场景标记计数 | `ChairSeat` 3 · `ChairGrip` 3 · `Rigidbody` 3 · `CameraOrbit`/`FootGroundingIK`/`ActionLabDriver`/`ActionPlayer`/`CharacterController` 各 1（与 §二·N 逐个对齐）**+ `RigBuilder` 1 · `TwoBoneIKConstraint` 1**；场景 4954 → **5126** 行 |

### ⚠️ 未闭合（诚实清单）

1. **无消费方**：接入点按设计**惰性**（权重恒 0）——真正的约束（副手拉向椅子第二锚点）等持椅线重新设计并形成新决策后再挂。**别把本节的"绿"读成"机制已就绪"**（同 §二·N 的口径）。
2. **合成搭建的 Rig 不建图**（2026-09-14 实测，代价：4 轮测试）：`RigBuilder` 在 `Awake`/`OnEnable` 里建图，运行时"先 `AddComponent`、后 `Add layer`"那一轮 Awake 看到的 layers 是空的。事后在同一实例上再 `Build()` **返回 true**、层也 `IsValid()=True`、`constraints=1`，但约束**始终不生效**（四组 `animator.speed` × 权重组合读数**逐位相同** = 初始偏移 187.1 mm）；连"建好模板再整体 `Instantiate`"也一样。⇒ 断言因此**只认真场景路径**。已进[危险点表](../engineering/危险点表.md) §六。
3. **与既有 `OnAnimatorIK` 的求值顺序未验**：`FootGroundingIK` 走内置 IK（`OnAnimatorIK`），Animation Rigging 走独立 `PlayableGraph`（`DirectorUpdateMode.GameTime`）+ `AnimationStreamSource.PreviousInputs` 输出。二者目前改的是**不同骨链**（腿 vs 左臂）故互不干扰，但**同一骨链时会互相覆盖**——标为待实测，接真约束前先验。
4. **基线**：本节读数取自 Windows 工作拷贝（其 git HEAD 落后仓库 HEAD、dirty 数百条，见[危险点表](../engineering/危险点表.md) §七），**不是仓库 HEAD 的门禁证据**；该拷贝 `Assets/**` 另有与仓库的既有分叉（退役 lab 残留、若干注释级差异）未处置。

### 怎么复核

```bash
./code/tools/unity-cli/uc.sh menu "YANTF/动作演示/创建 ActionLab 场景"   # 幂等：重建场景（含 Rig 接入点与自检日志）
./code/tools/unity-cli/uc.sh run_tests && ./code/tools/unity-cli/uc.sh test_status   # 53 条（含 AnimationRiggingProbeTests 2 条）
python3 code/tools/validate_unity_assets.py                                          # A1–A4
```

> 想单独复现"能力"那条读数（不进测试框架）：`editor_play` 后 `eval` 设 `rig.weight = ik.weight = 1` 并调 `Build()`，等几帧读 `LeftHand` 与约束目标的世界距离——2026-09-14 实测 **0.0 mm**。

---

## 三、工程结构

```
code/unity/
├── Assets/
│   ├── Editor/
│   │   ├── WalkerLabBuilder.cs    # 菜单/headless 生成 Walker 移动实验场景
│   │   ├── KiWalkerLabBuilder.cs  # 菜单/headless 生成 Ki 动画角色场景（含 controller）
│   │   ├── ActionLabBuilder.cs    # 菜单/headless 生成 ActionLab（12 态 controller + X Bot 场景）
│   │   └── MixamoSetup.cs         # 一键导入 Mixamo 资产（复制/改名/Rig Humanoid）+ 生成 ActionLab
│   ├── Scripts/                      # 运行时（asmdef: YANTF.Demo）
│   │   ├── WalkerController.cs       # 几何体人体 + CharacterController 走/跑/跳（WalkerLab）
│   │   ├── AnimatorWalker.cs         # Animator + CharacterController 走/跑/跳（KiWalkerLab）
│   │   ├── ActionIds.cs              # 12 词条常量（词表三面对一锚）
│   │   ├── ActionCatalog.cs          # 只读元数据（id → category/loop/priority/fade/clipFbxPath）
│   │   ├── ActionPlayer.cs           # 契约 A 驱动（CrossFade 优先级 + 计时回退 + locomotion 通道）
│   │   ├── ActionLabDriver.cs        # ActionLab 场景驱动（CC 物理 + 输入 + 就座判定/对齐/根位移/推椅 + HUD）
│   │   └── ChairSeat.cs              # 椅子组件（实时就座锚点 + 占用锁 + 碰撞忽略，就座交互 §四·丁）
│   └── Tests/PlayMode/               # asmdef: YANTF.Demo.Tests（冒烟测试）
│       ├── ActionLabChairTests.cs    # 就座交互：判定口径 / 实时锚点 / 占用锁 / 对齐 / 离座先起身
│       ├── ActionLabGripTests.cs     # 持椅交互：镜像派生件 + 挂点六条（#150 / #152）
│       ├── ActionLabLocomotionTests.cs # locomotion 连续混合
│       ├── ActionLabSmokeTests.cs    # 防漂移分档断言 + ActionPlayer 优先级冒烟
│       ├── AnimationRiggingProbeTests.cs # Animation Rigging 接入点：结构与能力（真场景）
│       ├── BrainViewSmokeTests.cs    # 脑壳只读骨架视图
│       └── WalkerLabSmokeTests.cs    # 白盒人形移动/落体
├── Packages/manifest.json            # uGUI + Test Framework + com.unity.pipeline（unity-cli）+ Animation Rigging
├── Packages/packages-lock.json      # 包版本可复现（#136 起入库）
└── ProjectSettings/                  # 工程身份 23 个文件（#136 起入库，含 Editor 版本与序列化模式）
```

> 场景与控制器：`Assets/Scenes/ActionLab.unity` + `Assets/ActionLab/ActionLab.controller` 已入库（基准场景，#136）；其余 lab 场景由 builder 菜单重建，不入库——范围与理由见 §二·H。

## 四、替换/扩展指引

- ~~**外部人形模型**：`CharacterVisual.BuildWhitebox()` 即接入点~~ → 🚫 随白盒沙盘退役（#155）。现行角色的载体是 X Bot + `Animator` + `ActionPlayer`（见 §二·H/§二·J）。
- **引擎核接入（Q6b 定案 A · 桥接已就位、接线待做）**：桥接工程 `code/src/YouAreNotTheFish.Core.Unity/` 已按 [ARCHITECTURE.md §4.1](../../ARCHITECTURE.md) 建好（`netstandard2.1`，链接 Core 的 3 个源文件 + `IsExternalInit` 垫片），`DamageCalculator.cs` 的 1 处 `ThrowIfNull` 已改写，**构建进 CI 的 `engine` job 当护栏**。🔧 2026-09-13（#155）：原计划接的那个消费者（Demo 战斗沙盘）已整体退役，故 **Unity 侧暂无消费者**——将来需要接缝时（P4d / CP-01 准入后）照 §4.1 接线即可，Core 侧不必再动。
- **状态面板细部规格 grilling**：以本 HUD 雏形为底子回炉。

## 五、已知简化（演示口径，非正典）

- M1→Broca 固定顺序（正典由玩家自定）；物攻/精攻射程为演示常量（2.0/6.0m）；陪练 AI = 简单随机（非 NPC Affordance Competition）；移动无网格/无移动配额显示。
- 颜色仅用于双方区分与 HP/SAN 条（§4.3），**不用颜色表情绪**（正典约束）。
- 已废弃口径提醒：HUD 无 AP 显示（正典不设 AP，回合流程 §1.1）。

---

*创建: 2026-09-06 | 更新: 2026-09-14（🔧 第十三次：**Animation Rigging 接入**（§二·O）——`com.unity.animation.rigging` 1.4.1 入库 + 惰性接入点（`RigBuilder`/`Rig`/左臂 `TwoBoneIK`，权重 0）+ 2 条**真场景**断言 + build settings 登记 index 0 + 资产白名单新增 `package_guids` 段；run_tests 53/53；⚠️ 副手 IK 属被暂停的线，**未实现**；🔧 第十二次：Unity 依赖入库——`com.unity.animation.rigging` 1.4.1（连带 `burst` 1.8.29 / `mathematics` 1.4.0），§二·N 加 `unity-assets` 计数**复测状态注**（141，差额 20 = #155 退役；历史读数 161 保留不改）；同批装入的 `com.unity.formats.fbx` 已按裁定 `package_remove` 撤除；🔧 第十一次：owner 裁定「手里有东西」这条线**暂停**（设计思路待重审）；§二·M 加「镜像目视不通过」、§二·N 加「已裁定」；🔧 第十次：owner 目视持椅挂点**不通过**——「不是用人类的方式跟椅子互动」；§二·N 未闭合项 1 改为实测结论 + 升级为待裁定设计问题；🔧 第九次：白盒 Demo 战斗沙盘整套退役 + 桥接工程就位（#155）——§一/§二/§四/§二·H 与目录树同步；🔧 第八次：#137 按 superseded 关闭——KI 旧线坐/起实现「待合的分叉」改为**作废更正**、开工顺序 4→3 条；`SitPoint.cs` 随舍弃裁定删除（#137）；🔧 第七次：Q6b 裁定 A（子集桥接）——数值源行与 §四 接缝指引指向 ARCHITECTURE §4.1（#135）；🔧 第五次修正：§二·J 就座交互（先找到椅子才能坐，#141）——判定/对齐/占用锁/XZ 根位移/三张可推椅子 + PlayMode 33/33 + 六条实测读数 + 修掉"角色整体悬浮 80 mm"（`skinWidth`）+ 三条新坑；🔧 第四次修正：§二·I ActionLab 落地回切修复（`6bd8ddc`）红/绿实测 + 目视验证 + 运维补充；🔧 第三次修正：§二·H 资产身份与提交范围（#136）+ §二·G 的「场景不入库」加显式例外；🔧 第二次：§二·G 本轮工作 #137–#140 + KI 引用作废；§二·F 玫瑰花海场景 — Grilling #126；🔧 第六次修正（2026-09-13，owner 裁定移除花海 lab）：删 §二·F 全节 + 6 个源文件 + `Assets/Shaders/` + `Assets/Resources/YANTF/` 高度图 + 4 项 PlayMode 测试，§二·H 排除表与 §三 目录树同步，PlayMode 33 → 29（算术推断，未重跑 Editor）；地块数据/玫瑰株丛密度两篇口径文档标记 ⚠️ 已废弃，保留仅供 #126 冻结历史引用）*
*关联: [战斗界面布局](../../design/presentation/%E6%88%98%E6%96%97%E7%95%8C%E9%9D%A2%E5%B8%83%E5%B1%80.md), [核心机制](../../design/rules/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [回合战斗流程](../../design/rules/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md), [关键突破](../../design/rules/skill-tree/%E5%85%B3%E9%94%AE%E7%AA%81%E7%A0%B4.md), [动作库规格](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md), [动作系统分解](../../design/engineering/%E5%8A%A8%E4%BD%9C%E7%B3%BB%E7%BB%9F%E5%88%86%E8%A7%A3-2026-09-12.md), [决策树](../../design/decisions/README.md)*
