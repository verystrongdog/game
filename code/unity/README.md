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

> ⚠️ 已知：X Bot 上 KI Walk/Run retarget 质量为首验点（载体锚定 #124 决策依据）；Jab Cross 为组合拳，若直拳单次语义不合 → 换 Punch 类 clip 或走程序化兜底。

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

*创建: 2026-09-06 | 更新: 2026-09-12（§二·F 玫瑰花海场景 — Grilling #126）*
*关联: [战斗界面布局](../../design/presentation/%E6%88%98%E6%96%97%E7%95%8C%E9%9D%A2%E5%B8%83%E5%B1%80.md), [核心机制](../../design/rules/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [回合战斗流程](../../design/rules/%E5%9B%9E%E5%90%88%E6%88%98%E6%96%97%E6%B5%81%E7%A8%8B.md), [关键突破](../../design/rules/skill-tree/%E5%85%B3%E9%94%AE%E7%AA%81%E7%A0%B4.md), [动作库规格](../../design/presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md), [地块数据-Konza草原](../../design/presentation/%E5%9C%B0%E5%9D%97%E6%95%B0%E6%8D%AE-Konza%E8%8D%89%E5%8E%9F.md), [玫瑰株丛密度](../../design/presentation/%E7%8E%AB%E7%91%B0%E6%A0%AA%E4%B8%9B%E5%AF%86%E5%BA%A6.md), [决策树](../../design/decisions/README.md)*
