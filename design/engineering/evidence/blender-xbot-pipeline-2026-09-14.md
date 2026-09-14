# Blender X Bot 动画制作与回导调试管线证据

> [#156](https://github.com/verystrongdog/game/issues/156) 的收口证据。口径权威是 [Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md)（Blender 线）与 [动画处理能力对照实验](../../presentation/动画处理能力对照实验.md)（两线共用）；必填字段按 [WORKFLOW.md §五/§六](../../../WORKFLOW.md) 与 [阶段证据说明](README.md) 记录。

## 一、结论（先读这一段）

| 项 | 值 |
|---|---|
| 达成 | 能力增量：`Blender 人形动作制作与回导调试` · Implementation `NONE → DONE_FOR_SLICE` · Health `UNKNOWN → PASS`（判据见 §八） |
| 一句话 | 「X Bot → Blender 控制骨母版 → animation-only FBX → Unity Humanoid → 逐帧回导检查」这条链路**建成并跑通**：母版 8 条自检、导出物 7 条自检全绿，探针 `RigRoundTripProbe.fbx` 在 Unity 里 `humanMotion=true`、无导入告警、逐帧可定位且重复采样逐位一致 |
| ⚠️ 一条要点 | **"两侧比对"型判据会平凡通过**：第一版母版的关键帧因 `rotation_mode` 被打回 `QUATERNION` 而**完全失效**，而"烘焙保真/回导保真"是两侧比对 ⇒ 两侧同样静止 ⇒ **双双通过**。由此新增非退化判据 **V8 / E0**，并修掉 `nla.bake(use_current_action=False)` 摘掉驱动 action 的第二个同类坑 |
| 未做的事 | 未做 Blender **5.1.2 横向对照**；未做**完整 Editor 重启**后的复现；危险点表未登记本条的 4 条坑（不在本条「预期差分」内，进候选队列）。**owner 目视（含"逐帧目视"）已于 2026-09-14 完成并通过** |

## 二、绑定

| 字段 | 值 |
|---|---|
| base SHA | `a38ba15`（#157 的末次提交） |
| head SHA | 本轮 **9 个提交**：`3e72d30`（管线正典）· `2e5dcb0`（母版生成器 + 导出器）· `7a7b860`（探针 FBX 入库）· `cd36cca`（Unity lab + 7 条断言）· `dcdb80c`（README §二·Q）· `2c5f390`（切片四轴回填 + 版本口径）· `42541b9`（证据落库）· **接环与 `_driven` 修复 + 文档同步为第 8–9 个** |
| 阶段 | [#156](https://github.com/verystrongdog/game/issues/156)（Task） |
| 收口 | **[#156](https://github.com/verystrongdog/game/issues/156) 已按 owner 指示关闭**（2026-09-14，reason = completed）——收口评论：<https://github.com/verystrongdog/game/issues/156#issuecomment-5664593878>。授权范围 = 该条收口评论 + `close` 动作；**标签按仓库惯例保留**（参照已关闭的 #149 / #142） |
| 执行者 | DSH agent（本机） |
| 工具版本 | Blender **4.5.13 LTS**（`blender-v4.5-release` · build hash `daeeeca98fb0` · linux-x64 便携包）· Unity **6000.5.2f1** · Python 3.10.12 · WSL2（Ubuntu 22.04） |
| 依赖 | 包**未改**（`com.unity.animation.rigging` 1.4.1 等沿用 `packages-lock.json`） |

### 证据基线（危险点表 §七 要求写明）

| 项 | 值 |
|---|---|
| Editor 打开的工程 | `C:\Users\9527\game\code\unity`（**Windows 拷贝**，非仓库工作树） |
| 该拷贝的 git HEAD | `6ea806a`（落后仓库 base `a38ba15`）· `git status --short` **139** 条 |
| **内容基线**（补偿证据） | 本轮触碰的 3 个 Unity 源文件与探针资产在 **两侧逐字节一致**（探针 FBX 三侧同哈希，见 §三）；`.meta` 由 Editor 生成后原值搬进仓库 |
| Editor 状态 | 生成 lab 与跑测试时 `editor_status` = `ready` · `compiling=false` · `playMode` 按需 `stopped/playing` |

> ⚠️ 与 §二·O / §二·P 记的是同一件事：`unity` 门禁读数取自 Windows 拷贝（git HEAD 落后）。
> 补偿手段是**逐字节内容比对**——它证明"内容一致"，**不是**"同一个 git 版本"。

## 三、母版与导出物读数（Blender 侧）

生成命令与预设全文见 [管线文档](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) §二/§四。

| 项 | 读数 |
|---|---|
| 输入 | `code/unity/Assets/Mixamo/Characters/X Bot.fbx` · `sha256 = cd60e51571bb7c0c1988ec58b3be174c91bd193b6372a9064f1ec2553bc8deab`（**运行前后一致**，V1 每次核） |
| 母版 | `.scratch/blender_assets/xbot/XBot_AnimationTemplate.blend`（过程物，不入库）· 78 骨 = 65 变形 + **13 控制** · 单一根 `mixamorig:Hips` |
| 母版自检 | **V1–V8 全绿**：控制驱动最小位移 **35.6121 mm**（阈值 20）· 探针最大位移 **820.2072 mm**（逐点 Hips 42.05 / 左手 746.38 / 右手 820.21 / 左脚 608.26 / 右脚 601.19） |
| 导出物 | `RigRoundTripProbe.fbx` · **684 044 字节** · `sha256 = b8cb1c96a508df73dd6ec0f168094e51844c37d6abac39014340b1ccf4e50356` · take `Armature\|RigRoundTripProbe` · 导出帧 0–60（61 键 @30 fps = **2.0000 s**） |
| 导出自检 | **E0–E6 全绿**：E0 源动作位移 274.7759 mm · E1 烘焙保真 **0.0011 mm** · E2 65 变形骨 / `CTRL_` **0** / 多余骨 **0** · E3 根 `['mixamorig:Hips']` · E4 网格 **0** · E5 Rest Pose 最大元素差 **9.2e-05** · E6 回导保真 **0.0014 mm**（帧号 offset **0**） |
| 烘焙过程 | 715 条 F-Curve · 剥掉 **42** 条控制通道 · 解除 **14** 条约束 |
| Blender 侧姿势读数（帧 1 / 21 / 41 / 61，髋骨世界 z） | `1.04275 / 1.06775 / 1.02775 / 1.04275`（即 +25.0 / −15.0 mm，量程 **40.0 mm**）· 母版与回导 FBX **逐帧相同** |

### 载体身份核验（2026-09-14，owner 目视后补）

owner 在 Play 画面里把载体读成了 "Y Bot"。实测**不是**——lab 载体是 X Bot，两者只是"同款不同色"：

| 资产 | 网格族 | 主材质 baseColor |
|---|---|---|
| `X Bot.fbx`（**lab 载体**、正典锚定） | `Beta_Joints` / `Beta_Surface` | `#441915` 深棕 + **`#AB3E36` 砖红偏粉** |
| `Y Bot.fbx` | `Alpha_Body` / `Alpha_Joints` | **`#14566A` 青蓝** + `#1F2B2D` 深灰 |

lab 载体的两条 `SkinnedMeshRenderer.sharedMaterials` 与 `X Bot.fbx` **逐项同值**；另有 `avatar = X BotAvatar`、actor 名 `Blender回导调试载体(X Bot)`。
⇒ 判定：**owner 看到的是 X Bot 的砖红材质**，与产物无关；`Y Bot` 是另一套网格族（`Alpha_*`），本条未使用。

### 三处同哈希（资产身份，`code/unity/README.md` §二·H 口径）

| 文件 | 三侧（Blender 输出 / 仓库 / Editor 工程）sha256 |
|---|---|
| `Assets/Animations/Blender/RigRoundTripProbe.fbx` | `b8cb1c96a508df73dd6ec0f168094e51844c37d6abac39014340b1ccf4e50356`（**逐字节一致**） |
| `Blender.meta` | GUID `7dd0a64c67b92a44fb198d534968cc1c`（**Editor 生成**，仓库采用同值） |
| `RigRoundTripProbe.fbx.meta` | GUID `fea37d37d0d6ded459704d6132b4ee9d`（**Editor 生成**，仓库采用同值） |

新源文件的 `.meta` GUID（同样由 Editor 生成）：`BlenderAnimationDebugger.cs` = `efafd0eba27c01c439e9f5ecad4df201` · `BlenderAnimationDebugBuilder.cs` = `4dab62777f9f3a540ad42dfa0ad59e14` · `BlenderAnimationDebugTests.cs` = `c3d80822b761d9040a76443e572e922b`。

## 四、Unity 侧读数（Editor 6000.5.2f1）

| 判据 | 读数 |
|---|---|
| 导入设置 | `animationType = 3`（Human）· `avatarSetup = 1`（CreateFromThisModel）· `animationCompression = 0`（**Off**，见 §六·3） |
| clip | `RigRoundTripProbe` · `humanMotion = True` · `length = 2.0000 s` · `frameRate = 30` · 130 条曲线（57 条随时间变化） |
| avatar | `RigRoundTripProbeAvatar` · `isValid = True` · `isHuman = True` |
| 三条导入告警串 | `animationImportErrors` / `animationImportWarnings` / `animationRetargetingWarnings` **三串皆空**（落 `.fbx.meta`，由 builder 自检每次核） |
| 同一帧重复采样 | 第 20 帧连续三次 `ReadoutLine()` **逐字节相同** |
| 帧间确实在动 | Hips **16.94 mm** · 左手 **677.06 mm** · 左脚 **550.98 mm**（断言下限 10 / 300 / 200 mm） |
| 帧 0 与帧 60 | **逐位相同**（探针首末帧同为静止姿势，符合设计） |

逐帧读数（Hips / LeftHand / LeftFoot）：

| 帧 | Hips | LeftHand | LeftFoot |
|---|---|---|---|
| 0 | `(-0.00253, 1.04270, 0.02702)` | `(-0.71586, 1.44057, -0.04401)` | `(-0.08461, 0.08730, -0.01595)` |
| 20 | `(0.00088, 1.02723, 0.02103)` | `(-0.68156, 1.26361, -0.05000)` | `(-0.08119, 0.12485, 0.23249)` |
| 40 | `(-0.00740, 1.03034, 0.02107)` | `(-0.41410, 1.88560, -0.04990)` | `(-0.18262, 0.14848, -0.30856)` |
| 60 | 与帧 0 逐位相同 | 同左 | 同左 |

### lab 幂等（结构指纹，两次生成逐字节相同）

`scene=BlenderRoundTripDebug` · `rootCount=4` · 各 root 的 transform 数与组件类型集合 · 载体名 ·
controller 名 · clip 名 · `frameCount=60` · avatar 名——连续两次 `CreateScene` 后**逐字节相同**。

> 说明：场景**文件字节不幂等**（Unity 每次重建会换内部 fileID），故判据取**结构指纹**而不是文件哈希。

## 五、门禁

| 门禁 | 命令 | 退出码 | 读数 |
|---|---|---|---|
| `docs-integrity` | `python3 code/tools/run_all_checks.py` | **0** | **14/14 校验器通过**（含 `validate_cross_refs.py`：1780 引用 / 0 死链 / 0 段引用警告） |
| `clean-checkout` | `python3 code/tools/check_clean_checkout.py` | **0** | ✅ 干净检出可完全解析（收尾前唯一 ❌ 是"README 指向尚未提交的管线文档"，提交后转绿） |
| `unity-assets` | `python3 code/tools/validate_unity_assets.py` | **0** | 受控文件 **164**（`.meta` 77）· A1 0 · A2 0 · A3 悬空 0 · A4 **受控 FBX 18**、非 Humanoid 0、非人形豁免 1（`brain_shell.fbx`） |
| `unity` | `run_tests --mode playmode --async_tests true` | — | **64 项：63 过 / 0 败 / 1 跳过**（基线 **56 项 55 过/0 败/1 跳过**；新增 **8** 条全过；跳过的是既有的 `ActionLabGuardVariantTests`） |
| `issues-fixtures`（旁证） | `python3 code/tools/validate_issues.py --from-github` | 0 | 14 规则 10 过 0 败 4 警告（警告全为存量） |

编译：新推 3 个 `.cs` 后 `console --level error` **无新增 error**（期间出现的 3 条 `CS0246` 是漏 `using UnityEngine.TestTools;`，已修并复跑）。

> ⚠️ **两个读数陷阱**（已写进管线文档 §六·2）：① `recompile_status` 报 `up_to_date` **不等于**没有编译错误——编译失败时它仍回 `failed:false`，判据要读 `console --level error`；② Play 态下跑菜单会抛 `InvalidOperationException`（"This cannot be used during play mode"）。

## 六、问题差分与新发现

`new_finding = after − mapped(before) − expected_delta`

### 6.1 预期差分比对（WORKFLOW §5.1）

本轮实际改动**全部落在** #156 登记的「允许变化」集合内，且是其**真子集**：

| 登记的允许变化 | 实际 |
|---|---|
| `design/presentation/Blender动作制作管线.md` | ✅ 新建 |
| `design/presentation/动作库规格.md` | ✅ 改 1 行（统一 Blender 版本口径） |
| `design/slices/CP-01-ward-1f/slice.md` | ✅ 四轴行回填 |
| `code/tools/build_xbot_animation_template.py` | ✅ 新建 |
| `code/tools/export_xbot_action.py` | ✅ 新建 |
| `code/unity/Assets/Animations/Blender.meta` + `Blender/RigRoundTripProbe.fbx{,.meta}` | ✅ 三件新建 |
| `code/unity/Assets/Editor/BlenderAnimationDebugBuilder.cs{,.meta}` | ✅ 新建 |
| `code/unity/Assets/Scripts/BlenderAnimationDebugger.cs{,.meta}` | ✅ 新建 |
| `code/unity/Assets/Tests/PlayMode/BlenderAnimationDebugTests.cs{,.meta}` | ✅ 新建 |
| `code/unity/README.md` | ✅ 加 §二·Q + 目录树 + 尾行 |
| `docs/reference/blender-python.md` | ⛔ **未建**——owner 2026-09-14 裁定「折进管线文档作附节」（仓库根本没有 `docs/` 顶层目录）。**少改不构成 new_finding** |

**预期不变项实测**：

| 项 | 判据 | 结果 |
|---|---|---|
| `X Bot.fbx` | 字节哈希 | **不变**（`cd60e515…`，且由 `BlenderAnimationDebugTests` 每次回归断言） |
| 15 条既有 Mixamo FBX | 逐个存在性 | **一个不少**（同断言） |
| `ActionLab.controller` / `ActionLab.unity` | 存在性 + 本轮 git diff | **未触碰**（`git rebase` 级核对：本轮 13 个路径无一落在其内） |
| `data/action_set.json` · `ActionCatalog.cs` · `ActionIds.cs` | 本轮 git diff | **未触碰** |
| Unity 包与锁文件 | 本轮 git diff | **未触碰** |
| lab 生成物 | 落点 | **只落 `Assets/Temp/`**（`.gitignore` 第 106 行 `code/unity/Assets/Temp/` 命中，未入库） |

### 6.2 新发现（6 条，全部在本条内处置）

| # | 发现 | 处置 |
|---|---|---|
| 1 | **控制骨 `rotation_mode` 被打回 `QUATERNION` ⇒ euler 关键帧失效**，而 E1/E6 两侧比对**平凡通过** | 修 `reset_pose`（模式感知）+ 新增 **V8**（母版）与 **E0**（导出）非退化判据 —— 管线文档 §三 |
| 2 | **`nla.bake(use_current_action=False)` 会摘掉正在驱动骨头的 action** ⇒ 烘出常量曲线（症状：FBX 有时长但 Unity 侧 130 条曲线**全 constant**） | 改 `use_current_action=True` 就地烘焙 + 烘后剥掉控制通道 —— §四·1 |
| 3 | **`EnsureController` 无条件删了重建 ⇒ 换 GUID ⇒ 已存盘 lab 场景的 controller 引用 missing**（症状：场景在、`clip=(none) frameCount=0`、姿势永不动） | 改为"内容已对就复用"（按 clip **名**比对）；`ResolveClip` 补 error 留痕 —— §六·2 |
| 4 | **Unity 默认关键帧压缩把骨盆位移从 61 键降到 3 键**（`RootT.y`），使"探针覆盖骨盆"在 Unity 侧只剩 17 mm | 探针导入设置固定 `animationCompression = Off`，并进 builder 自检 —— §5.4·2 |

| 5 | **`MonoBehaviour.Start` 在下一帧才跑 ⇒ 会静默取消调用方刚开的播放**（`_playOnStart` 兜底把状态冲掉；实测表现：「接环把播放态关掉了」） | 组件加 `_driven` 标记：被外部驱动过就不再兜底；新增接环断言把它钉住 —— §六·2 |
| 6 | **连续播放需要「播放层面接环」**：探针首末帧同为静止姿势，不接环时按 Play 一秒后画面就「没动静」，而 lab 的用途正是逐帧目视 | `BlenderAnimationDebugger` 加 `_loopInPlay`（默认开）+ 1 条断言；**只改播放行为**，FBX 与导入设置不动，样本仍是一次性 —— §六·2 |

**未在本条处置的候选**（[WORKFLOW.md §一](../../../WORKFLOW.md) 非阻塞发现进候选队列）：

- 上面的坑 1–4 **未登记进[危险点表](../../engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md)**——该文件不在本条「预期差分」内。它们已落在管线文档 §六·2/§七·3 与源码注释；**建议下一条动该表的 issue 顺手并入 §三（导入期）/§四（生成期）/§七（编辑器驱动）**。
- Unity 侧骨盆读数与 Blender 侧口径不同（16.94 vs 40.0 mm）——已作为**读数口径**记入管线文档 §5.4，不是缺陷；若要逐值比对，需要另立"人形 body position 语义"的专项。

## 七、回滚演练（临时 worktree）

```
git worktree add --detach .scratch/rollback HEAD      # HEAD = dcdb80c（本轮第 6 个提交）
cd .scratch/rollback
git revert --no-commit a38ba15..HEAD                  # 反做本轮 6 个提交
```

| 判据 | 结果 |
|---|---|
| 回滚后工作树 == base `a38ba15` | `git diff --stat a38ba15` **为空**（逐文件恢复到前态） |
| 回滚涉及的仓库路径 | **13 条**，与 §6.1 的「允许变化」集合**完全一致**（12 删除 + `code/unity/README.md` 1 修改） |
| 回滚后 `docs-integrity` 的前置 | `check_clean_checkout.py` **exit 0**（✅ 干净检出可完全解析） |
| 回滚后资产身份 | `validate_unity_assets.py` **exit 0**：A1 0 · A2 0 · A3 **悬空 0** · A4 受控 FBX **17**（探针随回滚消失，与 base 同） |
| Unity 侧 | 本条**不触碰** `ActionLab.unity` / `ActionLab.controller`，故"打开既有基准场景不产生缺失 GUID 或脚本引用"由 A3（引用可解析 0 悬空）在**回滚后的树**上直接给出；无数据迁移、无不可回滚的资产改名 |

> 演练后已 `git worktree remove`，工作树无残留。

## 八、能力四轴与判据

| 轴 | 从 → 到 | 判据 |
|---|---|---|
| Implementation | `NONE → DONE_FOR_SLICE` | 交付物存在且接入目标位置：两个 Blender 脚本（8 + 7 条自检全绿）、探针 FBX 入库（E2/E3/E4 形状判据）、Unity builder/debugger/断言三件落地；`run_tests` 64 项全绿 |
| Integration | `ISOLATED`（保持） | 探针**未接**正式玩家状态机：`ActionLab` / `ActionRiggingLab` 与其 controller、场景一字未改；lab 是隔离工作面（#156「明确排除」） |
| Health | `UNKNOWN → PASS` | 本轮全量相关回归：`run_tests` 64/63/0/1 · `docs-integrity` 14/14 · `clean-checkout` 0 · `unity-assets` A1–A4 全 0 · 回滚演练通过。⚠️ 范围限定见 §九 |
| Design | `ACCEPTED`（保持） | 设计面是[动作库规格 §四·戊·5](../../presentation/%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md) 的**分工口径**（2026-09-14 owner 定）与[对照实验](../../presentation/动画处理能力对照实验.md)（`Design: ACCEPTED`）；管线内部形态（控制骨母版/导出预设/回导判据）属工程交付物，其正典落 [Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) |

### 验收标准逐条对照

| # | 验收标准 | 结论 | 证据 |
|---|---|---|---|
| 1 | Blender 4.5 LTS 从干净检出的 `X Bot.fbx` 生成 `.blend`；输入哈希不变；`mixamorig:*` 名称/父子/Rest Pose 不变；`CTRL_*` 均 `Deform=false` | ✅ | §三（V1–V5；实测版本 **4.5.13 LTS**） |
| 2 | 导出 `RigRoundTripProbe.fbx`，覆盖骨盆/双腿/双臂控制；animation-only 中无 `CTRL_*`、无新增 Leaf Bone、无额外 Root 骨 | ✅ | §三（V6/V7/V8 + E2/E3/E4） |
| 3 | 探针在 Unity 满足 `animationType=Human`、`avatarSetup=CreateFromThisModel`、`clip.humanMotion=true`，且无 animation import/retarget warning | ✅ | §四 |
| 4 | 独立 lab 由 Editor 菜单**幂等**生成，支持播放/暂停、前后单帧、回首帧，显示当前 clip、帧号及 Hips/双手/双脚读数 | ✅ | §四（幂等结构指纹）+ `BlenderAnimationDebugTests` 3 条控制断言（含「连续播放在末帧接回首帧」——否则探针停在静止末帧，lab 看起来没动静） |
| 5 | 同 clip 同帧重复采样读数逐次一致；逐帧目视确认无比例跳变/骨架翻转/控制骨多余节点，并记录两端截图或日志 | ✅（**owner 目视通过**） | 重复采样逐次一致 ✅。**owner 目视（2026-09-14，Play 态）结论原话：「目视没有发现明显问题」**，并补充描述该动作为「类似走钢丝」——**该描述与读数吻合**：探针关键帧绕骨局部 X 轴 ⇒ 竖直面抬臂（左手相对肩 −0.1824 → +0.4450 m），双脚 y 只在 0.0868–0.1496 m（贴地前刮），骨盆只做起落。数值代理同时成立：骨长量程 ≤ 0.0004 mm · 胸骨 `up.y` 恒 0.9837–0.9891。两端截图：Unity `capture_game_view` 1280×720（连拍两张 md5 不同 = 非冻结帧）、Blender Cycles CPU 420×560。⚠️ 「控制骨多余节点」一项**不是目视覆盖的**（lab 载体是 X Bot，本身不含控制骨），它由机械断言覆盖（导出物 `CTRL_` **0**、骨数 65）|
| 6 | `X Bot.fbx`、15 条 Mixamo FBX、`ActionLab.controller`、`ActionLab.unity` 不变；生成物只落 `Assets/Temp/` 不入库 | ✅ | §6.1 |
| 7 | 三条门禁退出码均为 0，且回滚演练恢复到无 Blender 调试管线的前态 | ✅ | §五 + §七 |

## 九、未闭合（诚实清单）

1. **只验了 Blender 4.5.13 LTS**（linux-x64 便携包）。本机 Windows 侧装的是 **5.1.2**，**未做横向对照**；FBX 版本 7400（Blender 4.5 导出）与既有 Mixamo 的 7700 不同，**未做 Unity 侧兼容性专项验证**，只验了"本机 Unity 6000.5.2f1 能吃"。
2. **未做完整 Editor 重启后的复现**：幂等与确定性读数都在同一 Editor 会话内实测。
3. **Unity 侧骨盆读数低于 Blender 侧**（16.94 vs 40.0 mm）——量的是两个不同的量（Unity 把髋位移重定向进人形 body position 归一化空间后再落到 Hips 节点）；峰值帧与趋势一致，**绝对量不可逐值比对**。本条只主张后者。
4. **逐帧目视：owner 已于 2026-09-14 完成**（Play 态，结论「目视没有发现明显问题」；动作观感"类似走钢丝"且与读数吻合——见 §八 验收标准第 5 行）。残留范围仅两点：① 「控制骨多余节点」一项由**机械断言**（`CTRL_` 0 / 骨数 65）覆盖而非目视；② 截图为过程物（`.scratch/shots/`）、不入库，**未经第二人复核**。
5. **危险点表未登记本条的 4 条坑**（不在「预期差分」内）——已进候选队列，见 §6.2。
6. **基线**：Unity 读数取自 Windows 拷贝（git HEAD `6ea806a`，落后仓库 base）；补偿证据是探针 FBX 与两份 `.meta` **三侧同哈希**。这证明"内容一致"，**不是**"同一个 git 版本"。
7. **只做了 1 条探针动作**（演示幅度，非审美动作）；正式动作的制作与准入属切片 `CP-01-ward-1f`。

---
*创建: 2026-09-14 | 更新: 2026-09-14*
*关联: [#156](https://github.com/verystrongdog/game/issues/156), [Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md), [Unity 动画约束与接触修正证据](unity-animation-rigging-2026-09-14.md), [code/unity/README.md](../../../code/unity/README.md), [危险点表](../../engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md)*
