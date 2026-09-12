# Unity 呈现沙盘 — 可控角色 + 指令→动作→UI 反馈（Grilling #122）

> 呈现维度的可运行验证载体：Unity 工程 + 白盒人形角色，可接收基础行动指令并作出动作，底部 HUD 显示 HP/SAN 状态变化——为「状态面板细部规格」grilling 提供 UI 调试反馈底子。
>
> **维度: 呈现 + 管线** — Issue [#122](https://github.com/verystrongdog/game/issues/122)。

## 一、这是什么

| 项 | 内容 |
|----|------|
| 场景 | 单场景沙盘：演示者（白盒人形，蓝） vs 陪练（红，脚本 AI） |
| 指令 | WASD 移动（自由走位，非战棋网格）+ `1`物理攻击 / `2`防御 / `3`精神攻击 + `Space`执行回合 + `R`重置 |
| 回合 | 轻量手动回合沙盘：每回合选 M1 动作 + Broca 动作 → 执行 → 陪练 AI 行动（不触碰引擎 TurnManager） |
| HUD | 左下状态面板（HP/SAN 条+数值、防御/冷却/回合标签）、右下行动栏、日志区、陪练头顶精确数值（**调试显示**，非正典敌方模糊规则 §3.8） |
| 数值源 | `WhiteboxSolver`（临时）镜像 `CalibrationConfig.Default`（物攻 4/命中 0.75/防御 ×0.5/精攻 2−忍耐1/低SAN穿透），结算一位小数。**引擎桥接（EngineSolver，直接调用 `DamageCalculator`）待 Q6b 定案后替换，替换透明** |

## 二、本地验证步骤（Windows/macOS/Linux 桌面）

前置：Unity 6 Editor（6000.0.x；本工程 `ProjectVersion.txt` 锁 6000.5.2f1——版本不一致时 Unity 会提示升级/降级，接受即可，或改该文件为你的版本）。

1. 用 Unity Hub/Editor 打开本目录（`code/unity/`）作为工程；首次导入会自动还原包（uGUI + Test Framework）。
2. 菜单 **YANTF → 呈现沙盘 → 创建 Demo 场景** → 打开生成的 `Assets/Scenes/DemoSandbox.unity` → 按 **Play**。
3. 操作：WASD 走位靠近陪练（物攻射程 2.0m）→ `1` 物攻 / `3` 精攻 → `Space` 执行回合，观察 HUD 数值与受击反馈；`2` 防御观察「防御中 (物理-50%)」与冷却。
4. 跑测试：**Window → General → Test Runner → PlayMode → Run All**（2 个冒烟测试：精攻确定性结算 59/14.5；防御回合推进与冷却口径）。

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

**⚠️ 遗留一处需要合的分叉**（不要盲目覆盖）：`AnimatorWalker.cs` 是**双向发散**，两侧各有对方没有的功能——

| 侧 | 独有内容 |
|---|---|
| 原 Windows 拷贝 | 整套坐/起：`SitPhase` 状态机、`E` 键、`OnAnimatorMove` 接管 root motion、`_standLift` 过程性起身 |
| `main` | 空中方向修正参数化：`airControl` 0.15 / `airDrag` 0.5 与 `_airVelocity` 衰减逻辑 |

迁移时**保留了 Windows 侧版本**（先保住能跑的坐/起功能；main 的 25 行仍在 git 历史里，未丢失）。两者的合并是 #137 范围内的实作工作。`KiWalkerLabBuilder.cs` 同理（Windows 侧多 `StandToSit` 第五状态与 `StandUpTrigger`）。

### 会话启动清单

1. **确认 Editor 可直驱**：上表的 `unity status`，期望 `state: ready`（Editor 已开则直接连；未开则 `unity open`）。
2. **认准起点**：先读 [AGENTS.md](../../AGENTS.md)（全仓约束入口，含提交前必跑的校验器）→ 本 README §二·G → [动作库规格.md §四·乙/§六](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) → [动作系统分解](../../design/engineering/%E5%8A%A8%E4%BD%9C%E7%B3%BB%E7%BB%9F%E5%88%86%E8%A7%A3-2026-09-12.md)。
3. **开工顺序**：**#137 → #138 → #139 → #140**（严格串行，工作面相交）。每条的门禁、验收标准、预期差分、明确排除都在 issue 正文里，照做即可。
4. **本侧对 `code/unity/Assets/**` 可写**（经提权），实现与验证能在同一侧闭环——**不再需要跨机交接**。

### 四条 issue（严格串行，工作面相交所致）

| 序 | issue | 做什么 | 状态 |
|---|---|---|---|
| 1 | [#137](https://github.com/verystrongdog/game/issues/137) | **站↔坐**。**注意：原假设已被既有实现否定**——本 issue 的实际内容已变为「核对落点读数 + 合并 `AnimatorWalker.cs` 的双向分叉」，见上一节的遗留项 | `ready-for-human` |
| 2 | [#138](https://github.com/verystrongdog/game/issues/138) | **数据契约消费**：生成器读 `data/action_set.json` 产出 controller 与 C# 静态表，且**非破坏**（不覆盖已手调值） | `ready-for-human` |
| 3 | [#139](https://github.com/verystrongdog/game/issues/139) | **五条 clip 到库**：Idle/Walk/Run/Jump/Talk 下载 + Humanoid 导入 + **Play 预览实证归槽**（文件名不作依据），PlayMode 断言转绿 | `blocked`（by #138） |
| 4 | [#140](https://github.com/verystrongdog/game/issues/140) | **locomotion 迁契约 B**：1D blend tree（`speed01`，采样点 0 / 3.0 / 6.0）取代三态硬切 | `blocked`（by #139） |

> 门禁可用性：`unity` 在**本机可跑**（WSL 经 interop 直驱 Windows Editor），故 [`gates.json`](../../design/engineering/gates.json) 的 `available` 为 `true`。CI（ubuntu，无 Unity）侧仍不可跑，其 `unity` job 继续显式报告 `NOT_AVAILABLE`。

### 两条必须先懂的陷阱

1. **文件名 ≠ 动作语义**（#124 实证）：`Charge` 实为伸手指人、`Short Left Side Step` 实为循环格挡。每条新 clip 都要 Play 预览后归槽。
2. **坐立两条连方向都判不出来**：`Sit To Stand.fbx` 与 `Stand To Sit.fbx` 的内部 take 名均为 `mixamo.com`、`Title`/`Subject` 为空（2026-09-12 逐字节核验）。**必须预览**，不得据文件名预设——两条是近似镜像动作，误配比战斗类更隐蔽。

### 观察用移动视角（手动挂载，不入库）

ActionLab 的 `Main Camera` 是**静止**的（builder 只给了固定位置与俯角，没有驱动；对比 WalkerLab 有 `WalkerController.followCamera`）。`CameraOrbit` 已归位进 `Assets/Scripts/`，手动挂三步即可自由观察：

1. 生成场景：菜单 **YANTF → 动作演示 → 创建 ActionLab 场景** → 打开 `Assets/Scenes/ActionLab.unity`
2. Hierarchy 选中 **`Main Camera`** → **Add Component** → `Camera Orbit`
3. 把 Hierarchy 里的 **`ActionLab演示者(X Bot)`** 拖进该组件的 **`Target`** 字段 → **Play**

操作：**按住右键拖拽** = 环绕旋转视角；**滚轮** = 缩放远近（1.5–14 m）；相机注视胸口高度并平滑跟随。移动输入仍走相机相对，转视角后 WASD 前进方向跟着变。

> ⚠️ 两点必知：① **必须设 `Target`** —— 留空时组件的 `Start()` 会兜底把它设成自身 transform，结果是相机绕自己头顶打转（那是调试兜底，不是你要的效果）。② **重新生成场景会丢掉挂载**（场景不入库、由 builder 重建）——#139/#140 改 builder 后会重建一次，届时需重挂。

> 裁定（owner，2026-09-12）：**走手动挂载，不建 issue、不改 builder**——它是观察工具、不是能力增量，且场景本就按单机所有权不入库。若日后需要重建场景时自动挂上，再折进 [#137](https://github.com/verystrongdog/game/issues/137)。
### 与既有文档的关系

- 机器源 `data/action_set.json`：词条元数据 + blend 参数，每个数值带来源；`role=generator-input`（生成期输入，**运行时 Unity 不读它**）。
- `ActionCatalog.cs` 的 KI 路径为已知作废项，#138 落地后由生成表取代。
- `KiWalkerLab` 保留为历史对照场景，但**不再是词表来源**。


## 二·F、玫瑰花海场景（真实草原 DEM + 商业化密度株丛 + 小人穿行）

> 独立实验场（Grilling #126）：把「100×100 m 草原地形 + 整片玫瑰覆盖 + 小人穿行」落成可跑场景。地形取自**真实 1 m lidar 高程数据**（非参数化描述），株距密度取自**商业化种植文献**——两者都把模糊描述换成了可机械核验的取值。维度：呈现 + 管线。

| 项 | 内容 |
|----|------|
| 场景 | `RoseFieldLab.unity`（新）：真实地形地面 + 4563 株玫瑰株丛 + 几何体小人 |
| 操作 | **WASD/方向键** 移动（相对相机）、**Shift** 奔跑、**Space** 跳跃（复用 `WalkerController`） |
| 地块 | 100×100 m，101×101 采样 @ 1.0 m；**高差 3.1075 m**，最大 1 m 高差 0.1145 m（6.53°） |
| 地形源 | USGS 3DEP **1 m lidar** DEM（Konza Prairie 高草草原，公有领域）——见 [地块数据-Konza草原.md](../../design/presentation/%E5%9C%B0%E5%9D%97%E6%95%B0%E6%8D%AE-Konza%E8%8D%89%E5%8E%9F.md) |
| 株丛 | **4563 株**，六角错行 s = 1.602 m，蓬径 D = 1.85 m → 覆盖率 1.0；密度 **304 株/亩**（文献区间 180–330）——见 [玫瑰株丛密度.md](../../design/presentation/%E7%8E%AB%E7%91%B0%E6%A0%AA%E4%B8%9B%E5%AF%86%E5%BA%A6.md) |
| 渲染 | 程序化低模株丛（106 tri），**每株一个 GameObject**（MeshFilter + MeshRenderer 共享网格与材质，开 GPU Instancing 自动合批 —— 运行时生成 4563 个）；株丛无碰撞体 |
| 小人 | `WalkerController`（几何体白盒 + 程序化步态，**零外部资产**） |
| HUD | IMGUI：地块/采样/高差/株数/密度/间距/蓬径/全覆盖判据/小人坐标 |
| 测试 | `RoseFieldSmokeTests`（4 个 PlayMode）：高度图解码 / 地面网格法线朝上 / 六角格间距与密度判据 / 小人落在实际地形上 |

**生成/运行**：菜单 **YANTF → 玫瑰实验 → 创建玫瑰花海场景**（`Assets/Editor/RoseFieldLabBuilder.cs`）→ 打开 `Assets/Scenes/RoseFieldLab.unity` → 按 **Play**。

### 本机实测结论（2026-09-12，Unity 6000.5.2f1）

用 Unity CLI（`com.unity.pipeline`）直驱编辑器跑通全链路：编译 0 error → 菜单生成场景 → PlayMode 测试 4/4 绿 → Play → 截图回读像素统计。

| 实测项 | 结果 |
|--------|------|
| 构建日志 | 株数 **4563** / 密度 **304 株/亩** / 间距 1.602 m / 蓬径 1.85 m = 判据 1.850 m → **覆盖率 1.0** / 地块高差 3.1075 m |
| 运行时层级 | `RoseField(玫瑰花海)/Roses` 下 **4563 个 MeshRenderer**；地面 MeshCollider 正常 |
| 渲染画面 | 红色（玫瑰）像素占比 **8.04%**，草地 68.4% —— 地平线以上为天，以下整片红绿交错，远处透视压缩成实心红带 |
| PlayMode 测试 | `RoseFieldSmokeTests` **4/4 通过**（全项目 16 项：14 过 / 2 败；败项为 ActionLab 既有问题，与本次无关） |

### ⚠️ 两个踩过的坑（都已修复并写进代码注释）

1. **失焦冻结玩家循环**：`Project Settings → Player → Run In Background` 默认关闭时，编辑器窗口失去焦点会**停止 Update 循环**（`Time.frameCount` 不再增长），场景照常渲染但所有动态内容静止 —— 表现为「玫瑰一株都不渲染」。`RoseFieldLabBuilder` 现在显式设 `PlayerSettings.runInBackground = true`。
2. **即时模式绘制不进抓帧路径**：`Graphics.DrawMesh / DrawMeshInstanced / RenderMeshInstanced` 在 `capture_game_view --source camera` 抓到的帧里**不存在**（`source=screen` 的差异经比对确认是编辑器 UI 红色，非场景内容）。故株丛改用真实 GameObject 渲染 —— 顺带在编辑器 Scene View 里不按 Play 也能直接看层级。

> ⚠️ 已知简化：① 株丛叶/瓣为单面几何 + `Cull Off`，背面在 Lambert 下偏暗；② 阴影投射关闭（4563 株）；③ 逐株仅有偏航与缩放差异（无异形变）；④ 地块为真实地形的一块切片，与游戏正典空间**无关**（本实验不入正典）；⑤ 株丛对象运行时生成（不烘焙进场景，避免 .unity 膨胀到数 MB）。

## 三、工程结构

```
code/unity/
├── Assets/
│   ├── Editor/
│   │   ├── SceneBuilder.cs        # 菜单/headless 生成 Demo 场景
│   │   ├── WalkerLabBuilder.cs    # 菜单/headless 生成 Walker 移动实验场景
│   │   ├── KiWalkerLabBuilder.cs  # 菜单/headless 生成 Ki 动画角色场景（含 controller）
│   │   ├── ActionLabBuilder.cs    # 菜单/headless 生成 ActionLab（12 态 controller + X Bot 场景）
│   │   ├── MixamoSetup.cs         # 一键导入 Mixamo 资产（复制/改名/Rig Humanoid）+ 生成 ActionLab
│   │   └── RoseFieldLabBuilder.cs # 菜单/headless 生成玫瑰花海场景（Grilling #126）
│   ├── Shaders/
│   │   └── RoseInstanced.shader   # 实例化玫瑰材质（顶点色 + multi_compile_instancing + Cull Off）
│   ├── Resources/YANTF/
│   │   └── konza_plot_101x101_r16.bytes  # 地块高度图（LE uint16，行 0 = 北，20 402 B）
│   ├── Scripts/                      # 运行时（asmdef: YANTF.Demo）
│   │   ├── DemoTypes.cs              # 动作/阶段枚举、结算请求/结果
│   │   ├── DemoActor.cs              # 实体运行时状态（HP/SAN/防御/CD，事件）
│   │   ├── CharacterVisual.cs        # 白盒人形 + 程序化动作（外部模型接入点）
│   │   ├── DemoSolver.cs             # IDemoSolver + WhiteboxSolver（临时）
│   │   ├── DemoCombatDriver.cs       # 回合沙盘驱动 + 输入
│   │   ├── DemoHud.cs                # uGUI HUD（代码构建）
│   │   ├── WalkerController.cs       # 几何体人体 + CharacterController 走/跑/跳（WalkerLab）
│   │   ├── AnimatorWalker.cs         # Animator + CharacterController 走/跑/跳（KiWalkerLab）
│   │   ├── ActionIds.cs              # 12 词条常量（词表三面对一锚）
│   │   ├── ActionCatalog.cs          # 只读元数据（id → category/loop/priority/fade/clipFbxPath）
│   │   ├── ActionPlayer.cs           # 契约 A 驱动（CrossFade 优先级 + 计时回退 + locomotion 通道）
│   │   ├── ActionLabDriver.cs        # ActionLab 场景驱动（CC 物理 + 输入 + HUD 动作名）
│   │   ├── HeightField.cs            # 地块高度图解码/双线性采样/地面网格（玫瑰实验）
│   │   ├── RoseMeshFactory.cs        # 程序化低模玫瑰株丛网格（106 tri，零外部资产）
│   │   ├── RoseFieldLab.cs           # 玫瑰花海实例化驱动（六角错行 + DrawMeshInstanced + HUD）
│   │   └── DemoBootstrapper.cs       # 运行时构建整个世界
│   └── Tests/PlayMode/               # asmdef: YANTF.Demo.Tests（冒烟测试）
│       ├── DemoSmokeTests.cs
│       ├── WalkerLabSmokeTests.cs
│       ├── RoseFieldSmokeTests.cs    # 高度图/地面网格/六角格密度判据/小人贴合地形
│       └── ActionLabSmokeTests.cs    # 防漂移分档断言 + ActionPlayer 优先级冒烟
├── Packages/manifest.json            # uGUI 2.0.0 + Test Framework 1.4.5
└── ProjectSettings/ProjectVersion.txt
```

## 四、替换/扩展指引

- **外部人形模型**：`CharacterVisual.BuildWhitebox()`/动作接口（`PlayPhysicalAttack` 等）即接入点——替换为模型+Animator 实现，驱动层（DemoActor/DemoCombatDriver）零改动。
- **引擎核接入（待 Q6b）**：新建 `EngineSolver : IDemoSolver` 包装 `YouAreNotTheFish.Core.Unity` DLL 的 `DamageCalculator`（`CalibrationConfig.Default` + Unity 侧 `IRng` 实现），替换 `DemoCombatDriver.solver` 默认值。
- **状态面板细部规格 grilling**：以本 HUD 雏形为底子回炉。

## 五、已知简化（演示口径，非正典）

- M1→Broca 固定顺序（正典由玩家自定）；物攻/精攻射程为演示常量（2.0/6.0m）；陪练 AI = 简单随机（非 NPC Affordance Competition）；移动无网格/无移动配额显示。
- 颜色仅用于双方区分与 HP/SAN 条（§4.3），**不用颜色表情绪**（正典约束）。
- 已废弃口径提醒：HUD 无 AP 显示（正典不设 AP，回合流程 §1.1）。

---

*创建: 2026-09-06 | 更新: 2026-09-12（🔧 第二次修正：§二·G 本轮工作 #137–#140 + KI 引用作废；§二·F 玫瑰花海场景 — Grilling #126）*
*关联: [战斗界面布局](../../design/presentation/%E6%88%98%E6%96%97%E7%95%8C%E9%9D%A2%E5%B8%83%E5%B1%80.md), [核心机制](../../design/rules/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [回合战斗流程](../../design/rules/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md), [关键突破](../../design/rules/skill-tree/%E5%85%B3%E9%94%AE%E7%AA%81%E7%A0%B4.md), [动作库规格](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md), [动作系统分解](../../design/engineering/%E5%8A%A8%E4%BD%9C%E7%B3%BB%E7%BB%9F%E5%88%86%E8%A7%A3-2026-09-12.md), [地块数据-Konza草原](../../design/presentation/%E5%9C%B0%E5%9D%97%E6%95%B0%E6%8D%AE-Konza%E8%8D%89%E5%8E%9F.md), [玫瑰株丛密度](../../design/presentation/%E7%8E%AB%E7%91%B0%E6%A0%AA%E4%B8%9B%E5%AF%86%E5%BA%A6.md), [决策树](../../design/decisions/README.md)*
