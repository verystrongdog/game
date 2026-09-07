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

前置：Unity 6 Editor（6000.0.x；本工程 `ProjectVersion.txt` 锁 6000.0.83f1——版本不一致时 Unity 会提示升级/降级，接受即可，或改该文件为你的版本）。

1. 用 Unity Hub/Editor 打开本目录（`unity/`）作为工程；首次导入会自动还原包（uGUI + Test Framework）。
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

## 三、工程结构

```
unity/
├── Assets/
│   ├── Editor/
│   │   ├── SceneBuilder.cs        # 菜单/headless 生成 Demo 场景
│   │   ├── WalkerLabBuilder.cs    # 菜单/headless 生成 Walker 移动实验场景
│   │   └── KiWalkerLabBuilder.cs  # 菜单/headless 生成 Ki 动画角色场景（含 controller）
│   ├── Scripts/                      # 运行时（asmdef: YANTF.Demo）
│   │   ├── DemoTypes.cs              # 动作/阶段枚举、结算请求/结果
│   │   ├── DemoActor.cs              # 实体运行时状态（HP/SAN/防御/CD，事件）
│   │   ├── CharacterVisual.cs        # 白盒人形 + 程序化动作（外部模型接入点）
│   │   ├── DemoSolver.cs             # IDemoSolver + WhiteboxSolver（临时）
│   │   ├── DemoCombatDriver.cs       # 回合沙盘驱动 + 输入
│   │   ├── DemoHud.cs                # uGUI HUD（代码构建）
│   │   ├── WalkerController.cs       # 几何体人体 + CharacterController 走/跑/跳（WalkerLab）
│   │   ├── AnimatorWalker.cs         # Animator + CharacterController 走/跑/跳（KiWalkerLab）
│   │   └── DemoBootstrapper.cs       # 运行时构建整个世界
│   └── Tests/PlayMode/               # asmdef: YANTF.Demo.Tests（冒烟测试）
│       ├── DemoSmokeTests.cs
│       └── WalkerLabSmokeTests.cs
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

*创建: 2026-09-06*
*关联: [战斗界面布局](../../呈现/战斗界面布局.md), [核心机制](../../规则/核心机制.md), [回合战斗流程](../../规则/回合战斗流程.md), [关键突破](../../规则/技能树系统/关键突破.md), [决策树 #122](../../docs/决策树.md)*
