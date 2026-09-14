# Unity 动画约束与接触修正证据（X Bot 约束修正与派生动画）

> [#157](https://github.com/verystrongdog/game/issues/157) 的收口证据。样本与口径的权威是 [动画处理能力对照实验](../../presentation/动画处理能力对照实验.md) §二/§三/§四；必填字段按 [WORKFLOW.md §五/§六](../../../WORKFLOW.md) 与 [阶段证据说明](README.md) 记录。
> **这是"两线对照"里 Unity 这一线的读数**（Unreal 线已于 2026-09-14 由 owner 裁定不建，见 [Unreal 探针证据](unreal-animation-probe-2026-09-14.md)）——对照方是待建的 Blender 线。

## 一、结论（先读这一段）

| 项 | 值 |
|---|---|
| 达成 | 能力增量：`Unity 动画约束与接触修正` · Implementation `NONE → PARTIAL` · Health `UNKNOWN → PASS`（判据见 §八） |
| 一句话 | 隔离 lab 建成并可重复生成；**三条**最小约束（右手 / 左腿 / 右腿）在真场景里求值；关/开**同一帧**读数齐（M1–M7）；修正结果烘成**独立 Animation Sequence**，关约束单独采样能复现（差 ≤ 0.06 mm） |
| ⚠️ 一条要点 | **M1「约束开」= 96.45 mm，不是 0 mm**——不是失败，是读数：固定目标偏移（187.08 mm）落在这个接触帧的手**够不到**的位置（肩→靶 658 mm > 臂长 562 mm）。详见 §四·M1 |
| 未做的事 | 未做完整 Editor **重启**后的 M7（只做了 Play 重启 + 重编译/域重载）；M6 的"符号与源 clip 同号"收窄为只报**屈曲量**（见 §十） |

## 二、绑定

| 字段 | 值 |
|---|---|
| base SHA | `b7f6b02`（#158 收口提交） |
| head SHA | 本轮 5 个提交：`3b5ee5c`（工具 push_file.sh）· `fc4e200`（lab builder + 探针 + 场景 + build settings）· `62d0490`（派生件 + 测试）· `cc78dff`（证据 + 四轴表 + 危险点表 + README）· 本回填提交 |
| 阶段 | [#157](https://github.com/verystrongdog/game/issues/157)（Task） |
| 执行者 | DSH agent（本机） |
| 工具版本 | Unity **6000.5.2f1**（`ProjectVersion.txt` 锁 6000.5.2f1 · `eb73d3b415a1`）· Windows 11 家庭中文版 build 26200 · Python 3.10.12 · gh 2.100.0 |
| 依赖 | `com.unity.animation.rigging` **1.4.1**（`dcc0073` 已入库，本条**未改**包版本）· `com.unity.pipeline`（unity-cli 直驱） |

### 证据基线（危险点表 §七 要求写明）

| 项 | 值 |
|---|---|
| Editor 打开的工程 | `C:\Users\9527\game\code\unity`（**Windows 拷贝**，非仓库工作树） |
| 该拷贝的 git HEAD | `6ea806a`（落后仓库 HEAD **53 提交**；`git status --short` 131 条） |
| **内容基线**（补偿证据） | `code/unity/**` 受跟踪文件逐字节 `sha256` 比对：**141 一致 / 14 不一致 / 0 缺失**；14 处不一致**全是 #157 之前就存在的分叉**（`BrainView*`、`KiWalkerLabBuilder`、`ChairSeat`、两个 Chairhold `.meta`、`ActionLab*Tests.cs.meta`、`code/unity/README.md`），**#157 触碰的 6 个文件两侧逐字节一致** ⇒ 本轮读数不建立在"另一份拷贝的在制改动"上 |
| Editor 状态 | `editor_status`：`compiling=false` · `playMode=stopped`（跑测试时 `playing`）· `programPath` 如上 |

> ⚠️ **诚实标注**：`unity` 门禁的读数取自 Windows 拷贝（其 git HEAD 落后），这与 §二·O 未闭合 4 记的是同一件事。补偿手段是上行的**逐字节内容比对**——但它证明的是"内容一致"，**不是**"同一个 git 版本"。完整闭合需要把该拷贝对齐到仓库 HEAD（`fetch` + `reset --mixed`），本轮未做（WSL 沙箱对 `/mnt/c` 只读，且对齐属另一条工作）。

## 三、共同样本与口径怎么落的

| 口径 | 落法 |
|---|---|
| §2.1 样本 | 仓库内 `Assets/Mixamo/Characters/X Bot.fbx`（Humanoid）+ `Assets/Animations/Mixamo/Combat/PhysicalAttack.fbx`；地面为 24×24 平面、表面 y = 0；载体站在原点、无附加旋转 |
| §2.2 取帧 | 41 点均匀采样求 `argmax_t [(右手 − 髋) · 角色 forward]`，再在相邻两采样点之间**逐帧细化**。**投影对整体平移不变**（右手−髋），故取帧不受根位移语义影响。trace 见下方 |
| §2.3 目标 | 右手靶 = 接触帧右手 + 角色局部 `right 0.15 / up 0.10 / forward 0.05`（模长 **187.083 mm**）；左右脚靶 = 该脚足底最低点抬到 `地面 + soleMargin(2.8 mm)`，**只上抬不下压** |
| §2.4 场景 | 地面 · 载体 · 右手靶 · 左右脚靶 · 髋参考（`HipsRef`）· **约束权重可切**（探针 `SetWeights(0/1)` + `RigBuilder.Build()`） |
| §3.1 归属唯一 | lab 载体上**不挂** `FootGroundingIK`（自检与 PlayMode 断言各有一条守它） |
| §五 产物去向 | lab 场景**入库** + 登记 `EditorBuildSettings`（index 1）；派生素材只落在 `Assets/Animations/Derived/` |

**取帧 trace（实测，clip 内留痕）**：

```
clip=mixamo.com  length=2.1333s  frameRate=30  totalFrames=64
coarseProjections=[0.1589,0.1673,0.1734,0.1773,0.1778,0.176,0.1711,0.1537,0.1173,0.0827,0.1021,
 0.2454,0.4582,0.5694,0.5041,0.3589,0.2551,0.2284,0.2349,0.2345,0.2186,0.1978,0.1816,0.1736,0.1706,
 0.1689,0.1737,0.1772,0.1775,0.1731,0.1622,0.1547,0.1576,0.1641,0.165,0.1618,0.1556,0.1507,0.1487,0.1518,0.1589]
coarseBestIndex=13  refineWindowFrames=[19,23]  contactFrame=21  contactTime=0.7  contactProjection=0.5715
```

## 四、M1–M7 读数（约束关 / 开 · **同一帧**）

关 = Rig 与三条约束权重 0（改后调 `RigBuilder.Build()`）；开 = 权重 1 + 同一次 `Build()`；两次都在接触帧（frame 21 / t=0.7 s），姿势由同一条定位路径（`Animator.Play` + `Update(0f)` + 冻结）给出。

| id | 观测量 | 关 | 开 | 判读 |
|---|---|---|---|---|
| **M1** | 右手 ↔ 目标距离 | **187.1199 mm** | **96.4484 mm** | 约束把右手拉近 **90.67 mm**；**未到 0**（见下方"够不到"） |
| **M2** | 足底相对地面（左 / 右） | **−24.0053 / −34.9085 mm** | **+2.8337 / +2.7730 mm** | 关时双脚**陷入地面**；开后停在 `soleMargin`（2.8 mm）**± 0.03 mm** |
| **M3a** | 根水平漂移（对首帧） | 19.3751 mm | 19.3751 mm | **逐位不变** ⇒ 约束不动根 |
| **M3b** | 根朝向偏差（对首帧） | 21.7424° | 21.7424° | **逐位不变** |
| **M4** | 骨长（上臂/前臂/大腿/小腿） | 278.4153 / 283.2883 / 443.7147 / 445.2781 mm | 278.4153 / 283.2884 / 443.7147 / 445.2782 mm | 关开之差 **≤ 0.0001 mm** ⇒ 无缩放 |
| **M5** | 脚滑代理量（tc → tc+1） | 左 **10.6582** / 右 **2.3577** mm | 左 **0.0014** / 右 **0.0016** mm | 开后两脚**几乎完全静止**（脚被钉在靶上） |
| **M6** | 肘 / 膝屈曲量 | 肘 34.4603° · 膝左 39.2047° · 膝右 29.6021° | 肘 **0°** · 膝左 47.9638° · 膝右 42.9664° | 肘被拉直（够不到的表现）；两膝弯曲量增大（腿被拉向脚靶） |
| **M7** | 重开可复现性 | — | — | **逐位一致**：Play 重启 + 脚本重编译（域重载）+ 跑完一轮 PlayMode 测试后再测，M1/M2 与首次**完全相同**（187.1199 / 96.4484 / 2.8337 / 2.7730）。**未做**完整 Editor 重启（见 §十） |

原始位置（判"够没够到"用）：

| 状态 | 右手 | 右手靶 | 左踝 | 左脚趾 | 左脚靶 | 臂残差 | 腿残差（左/右） |
|---|---|---|---|---|---|---|---|
| 关 | `0.28426, 1.36970, 0.48089` | `0.4343, 1.4697, 0.5309` | `0.05582, 0.05477, 0.24382` | `0.13414, −0.02401, 0.32599` | `0.0558, 0.0816, 0.2438` | 187.12 mm | 26.83 / 37.73 mm |
| 开 | `0.38784, 1.44814, 0.44918` | 同上 | `0.0558, 0.0816, 0.2438` | `0.1341, 0.00283, 0.326` | 同上 | 96.45 mm | **0.0008 / 0.0003 mm** |

### M1 为什么不是 0（本条要点）

手臂残差 96.45 mm 的几何解释：约束把右臂**拉直到极限**（肘屈曲量 0°）后仍差 96.45 mm，
即 `肩 → 靶` 距离 ≈ 臂长 561.7 mm + 96.45 mm = **658 mm > 臂长 562 mm**。也就是：**固定目标偏移（187.08 mm）
从这个接触帧出发落在这条两骨链的可达域之外**。腿链在同一 lab 里残差 0.0008 mm，说明"够不到"不是约束没生效。

> 与 §二·O 的 `0.0 mm` 不矛盾：那条读数取自 `ActionLab`（左手、目标按**运行时那一刻的手位**现摆），
> 本条按 §2.3 的**固定偏移**从接触帧布置。两者是不同的问题——**本条的 96.45 mm 正是"固定共同样本目标"下的真实读数**，
> 也正是横向对照要读的东西：Unity 的最小两骨 IK 在肩胛不参与的前提下够不到该靶。

## 五、派生件与独立复现（验收标准 ④）

| 项 | 值 |
|---|---|
| 烘焙路径 | Play 中逐帧抓"约束开"的**人形姿势**（`HumanPoseHandler` 肌肉 95 + 根）→ 落 JSON → Editor 侧写 `.anim`（肌肉曲线绑 `Animator`/`HumanTrait.MuscleName[i]`，根写 `RootT.*` / `RootQ.*`） |
| 产物 | `code/unity/Assets/Animations/Derived/PhysicalAttack_ContactCorrected.anim` · 帧范围 **0–64 帧全段**（65 个采样）· `length=2.1333 s` · **102 条曲线**（95 肌肉 + 7 根）· 2,730,302 B |
| 独立复现（**约束关**，只采派生件，仍为接触帧） | M1 **96.4522 mm** · M2 左 **2.8175 mm** · M2 右 **2.7170 mm** |
| 与"约束开"之差 | **+0.0038 / −0.0162 / −0.0560 mm**（同一容差 1 mm 内**逐项复现**） |
| 源件指纹 | `X Bot.fbx` `cd60e51571bb7c0c…` · `PhysicalAttack.fbx` `ad97581060e5ce37…`——与 [对照实验](../../presentation/动画处理能力对照实验.md) §2.1 登记值**一致**，源 FBX 字节未变 |
| 漂移风险 | 派生件**与载体绑定**（烘焙的是 X Bot 上的姿势）；换载体重跑烘焙。与 `DerivedClipBuilder` 的"纯函数派生件"不同，本条**不是**可重算的纯函数产物，故不纳入 `VerifyDerived()` 的逐曲线自检——已在 `code/unity/README.md` §二·P 写明 |

## 六、成本口径 C1–C9（两线对照要读的代价面）

| id | 项 | 本轮值 |
|---|---|---|
| C1 | 引擎与版本 | Unity **6000.5.2f1**（Windows 11 build 26200） |
| C2 | 工具链与插件 | `com.unity.animation.rigging` 1.4.1（连带 burst 1.8.29 / mathematics 1.4.0，**`dcc0073` 已入库**）· `com.unity.pipeline` 0.6.0-exp.1（直驱）· 本条**未新增包** |
| C3 | 建立耗时 | 从第一条脚本落进工程到"lab 场景可编辑并出读数"：**约 85 分钟**（含 §七 的 **4 轮踩坑**：静默推送失败 ×1、姿势语义 ×1、Play 定位顺序 ×1、目标朝向 ×1）。其中**跑通后的重建**只需一条菜单（`创建 AnimationRiggingLab 场景`），实测 **< 5 s** |
| C4 | 人工步骤 | 一次性 3 步（建场景菜单 → Play 内校准 → 退出后写回场景）；烘培 2 步（Play 内采集 → 退出后烘焙菜单）。**不可数项**：Unity 内部的资产导入/重编译次数未计时 |
| C5 | 自定义代码量 | 新增 **2 文件 1172 行**（`AnimationRiggingProbe.cs` 651 行 · `AnimationRiggingLabBuilder.cs` 521 行）+ 测试**净增 167 行**（317 行里含既有 150 行）；约束控制器 **1 Rig + 3 约束 + 3 目标**；**0 个自定义 Blueprint**（Unity 侧对应物是 0） |
| C6 | 警告与错误 | 编译 **0 error**；**2 条既有弃用警告原文**：`warning CS0618: 'Object.FindFirstObjectByType<T>()' is obsolete: 'FindFirstObjectByType has been deprecated because it relies on instance ID ordering. Use FindAnyObjectByType instead, which does not depend on ordering.'`（`AnimationRiggingProbeTests.cs` / `AnimationRiggingLabBuilder.cs` 各一，非本条引入） |
| C7 | 可撤销性 / 可诊断性 | 撤销栈：lab 场景由 builder **幂等重建**（改错就重跑菜单），派生件是产物（重烘焙）；**报错指名到骨与帧**——实测原文 `[RigLab] RightArmIK 骨链绑定为空 → RightUpperArm（Humanoid 载体换过？FBX 是否开了 Optimize Game Objects？）`、`[RigProbe] measure {"contactFrame":21,…}` 每条读数带帧号 |
| C8 | 资产结果 | 派生件**脱离约束状态可独立采样复现**（§五）· 重开 Play 后可复现 · 导出物 `Assets/Animations/Derived/PhysicalAttack_ContactCorrected.anim`（Unity 文本序列化 `.anim`） |
| C9 | 回滚演练 | 见 §九（`git revert` 实测） |

## 七、踩到的坑（全部已回写 [危险点表](../危险点表.md)）

| # | 症状 | 根因 | 代价 |
|---|---|---|---|
| 1 | **改了代码、重编译也过，行为完全没变** | `uc.sh write_text_file --contents "$(cat 大文件)"` 走命令行参数，38 KB 的 `.cs` 触到 Windows 命令行长度上限 → unity.exe 报 `Invalid argument`，**文件根本没写**（`--confirm true` 也不报） | 时间 + **错误结论**（会误判成"Unity 没重编译"）。处置：新增 `code/tools/unity-cli/push_file.sh`（base64 分片 + Editor 侧拼回） |
| 2 | Play 里读到的目标离手 **762 mm**（应 187 mm） | Play 中 `AnimationClip.SampleAnimation` 的写入被动画播放图覆盖；且**编辑期姿势 ≠ Play 期姿势**（实测同一帧右手 `(-0.041, 1.281, 1.067)` vs `(0.284, 1.370, 0.481)`，差值**不是纯平移**） | 一整轮垃圾读数。处置：取帧与目标布置**只在 Play 内校准一次**，结果写回场景（`_lab_calibration.json` + 菜单"把校准结果写回 lab 场景"） |
| 3 | 请求 `norm=0.7`，状态时间却停在 `22/64`（0.34375） | `Animator.Play(state, layer, normalizedTime)` 的定位：**必须先 `Update(0f)` 才生效**；先 `speed = 0` 再 Play 也不生效 | 整片读数错（M1 恒 762 mm）。处置：`PoseAtFrame()` 统一 Play → `Update(0f)` → 冻结 |
| 4 | 踝明明精确到位（残差 0.0008 mm），脚趾却被抬到 **+220 mm**，M2 报 +81.6 mm | 约束 `maintainTargetRotationOffset = false` ⇒ 把 tip 朝向**设成目标的朝向**；目标是 `new GameObject` 的 identity 朝向 → 脚被硬拧过去 | 假读数。处置：布置目标时**连朝向一起摆**（`target.rotation = 骨.rotation`），校准 JSON 里带上四元数 |
| 5 | 脚滑量在约束开时 ≈ 0 | （不是坑，是要读的事实）脚靶是**静态**物体 ⇒ 约束开时两脚被钉住，M5 从 10.66 mm 降到 0.0014 mm | — |

## 八、门禁与命令（逐条实跑）

| # | 命令 | 退出码 | 读数 |
|---|---|---|---|
| 1 | `python3 code/tools/run_all_checks.py`（docs-integrity） | 0 | **14 validators: 14 passed / 0 failed** |
| 2 | `python3 code/tools/check_clean_checkout.py` | 0 | ✅ 干净检出可完全解析（4 条警告均为既有归档文档的绝对路径） |
| 3 | `python3 code/tools/validate_unity_assets.py` | 0 | 受控 155（`.meta` 72）· A1 0 · A2 0 · **A3 悬空 0**（放行 99：builtin 87 / package 8 / known 4）· A4 0 |
| 4 | `uc.sh recompile` + `recompile_status` | 0 | `status: completed` · **failed: false** · `errors: []` |
| 5 | `uc.sh run_tests --mode playmode --async_tests true` → `test_status` | 0 | **56 项：55 过 / 0 败 / 1 跳过**（跳过的是既有的 `ActionLabGuardVariantTests.GuardVariant_MeetsThreeCriteria`，与本条无关）。本条新增 3 条全绿：`LabScene_HasThreeBoundConstraints_SerializedContactFrame_AndNoFootGroundingIK` · `LabScene_ConstraintOff_vs_On_AtSameFrame_MovesHandAndGroundsFeet` · `BakedClip_ReproducesCorrectedReadings_WithoutConstraints`；既有 2 条判据**未改**且仍绿 |
| 6 | `validate_issues.py --from-github` | 0 | 14 rules：10 passed / 0 failed / 4 warnings |
| 7 | 浅克隆/write 相关（§七 #1） | 非 0 | `unity.exe: Invalid argument`——已固化为 `push_file.sh` |

> `unity` 门禁的可用性：本机 Editor 在 Windows 侧、经 WSL interop 直驱（`gates.json` 的 `unity.available = true`）；
> 基线口径见 §二（Windows 拷贝 HEAD 落后 + 逐字节内容比对）。

## 九、问题差分、回滚演练、工作树

```
new_finding = after − mapped(before) − expected_delta = 空
```

- `before`（base `b7f6b02`）：`code/unity/Assets/Scenes/` 下无接触修正 lab；无派生接触修正件；`AnimationRiggingProbeTests.cs` 只有 2 条（150 行）；PlayMode 全量 **53** 条。
- `expected_delta`（[#157](https://github.com/verystrongdog/game/issues/157) 预期差分）：新增 lab builder / 探针 / lab 场景 / 派生件 / 证据 / README 回填；改测试与 `EditorBuildSettings.asset`。**实际新增了 1 个预期外但必要的文件**：`code/tools/unity-cli/push_file.sh`（§七 #1 的直接产物，属工具面无行为影响）。这条偏离**已在提交信息与本节登记**，不是事后倒填。
- 预期不变项核对：源 `X Bot.fbx` / `PhysicalAttack.fbx` **指纹与登记值一致**（§五）；`ActionLab` 场景的惰性契约（`rig.weight = ik.weight = 0`）由既有的 2 条断言守着、仍绿；动作词表 / `data/action_set.json` 未动；持椅交互暂停线未动（`ChairGrip`/`ChairSeat` 未改）；`Packages/manifest.json` 与锁文件未动。

### 回滚演练（实测）

方式：临时 worktree + `git revert`（不改主干），回滚**本轮 4 个交付提交**。

| 步 | 命令 | 退出码 | 结果 |
|---|---|---|---|
| 1 | `git worktree add --detach /tmp/revert157 HEAD` | 0 | 在 head `cc78dff` 上取得干净检出（回滚前：lab 场景与派生件都在，`EditorBuildSettings` 含 1 条 lab 引用） |
| 2 | `git revert --no-edit fc4e200 62d0490 cc78dff 3b5ee5c` | 0 | 4 条 revert 提交，无冲突 |
| 3 | 核对产物 | — | lab 场景 / 派生件 / 探针 / builder / `push_file.sh` **全部消失**；`EditorBuildSettings.asset` 里 lab 引用 **1 → 0**，`ActionLab.unity` **仍在**（未被误删） |
| 4 | `validate_cross_refs.py`（回滚态） | 0 | 1752 refs / 1751 passed / **0 dead**——与本条开工前的读数逐字同值 |
| 5 | `validate_unity_assets.py`（回滚态） | 0 | ✅ 全部通过（受控 FBX 17 · 非 Humanoid 0 · 非人形豁免 1） |
| 6 | `git worktree remove --force /tmp/revert157` | 0 | 临时工作树清理；主干 `HEAD` 仍为 `cc78dff` |

> 回滚**不**回退 `Packages/manifest.json` 与锁文件（`animation.rigging` 1.4.1 早于本条入库，`ActionLab` 的惰性接入点依赖它）——本轮 4 个提交本就未触碰这两个文件，实测回滚后仍保持一致。

### 工作树

提交后 `git status --short` 应为空；本轮的**过程物**（`_lab_calibration.json`、`_contact_capture.json`、`_push_part_*.txt`）**不入库**（`_` 前缀 + `.gitignore`），且已从 Windows 工程删除。

## 十、未闭合项（不得当作通过）

1. **M1「开」= 96.45 mm ≠ 0**：固定目标偏移超出两骨链可达域（§四）。这**不是**本条的缺陷，但它是横向对照要解释的读数——Blender 线若能把同一偏移做到 0，差异来自"肩胛是否参与 / 是否允许位移根"。
2. **M7 未覆盖完整 Editor 重启**：只验了 Play 重启 + 域重载 + 跑完测试后的复现。完整重启需要动 owner 正在用的 Editor。
3. **M6 的符号口径收窄**：§三 M6 原文是"有符号屈曲角（与源 clip 同号为正）"，本探针只报**屈曲量大小**（三点夹角补角），未定符号（只有三点坐标时符号不唯一）。要坐实需读源 clip 的旋转方向。
4. **Windows 拷贝 git HEAD 落后 53 提交**（内容侧 141/14/0，见 §二）：与本条无关的既有状态，但它是"门禁证据绑不绑得上仓库 HEAD"的老问题。
5. **派生件与载体绑定**：烘焙的是 X Bot 上的姿势，换载体重跑；因此不纳入 `DerivedClipBuilder.VerifyDerived()` 的纯函数自检（已在 README §二·P 写明）。
6. **lab 场景入库是对既有约定的例外**：`code/unity/README.md` §二·H「其余 lab 场景不入库」的显式例外，理由是实测硬约束（约束只认已序列化场景 + 断言按名 `LoadScene`），owner 已在 [对照实验](../../presentation/动画处理能力对照实验.md) §七.3 确认。

---

*创建: 2026-09-14 | 状态: 交付完成，门禁实跑见 §八；`Implementation: NONE → PARTIAL` · `Health: UNKNOWN → PASS`（绑定 commit 见 §二）*
*关联: [动画处理能力对照实验](../../presentation/动画处理能力对照实验.md) · [Unreal 探针证据](unreal-animation-probe-2026-09-14.md) · [阶段证据说明](README.md) · [危险点表](../危险点表.md) · [WORKFLOW.md](../../../WORKFLOW.md)*
