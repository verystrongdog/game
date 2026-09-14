# Blender 人形动作制作管线

> **X Bot → Blender 控制骨母版 → animation-only FBX → Unity Humanoid → 逐帧回导检查** 这条链路的形态、导出预设与回导判据。本文是 Blender 线的**口径正典**；共同样本与共同读数纪律见 [动画处理能力对照实验](%E5%8A%A8%E7%94%BB%E5%A4%84%E7%90%86%E8%83%BD%E5%8A%9B%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C.md)。

## 目录

1. [一、这是什么（消费时刻）](#一这是什么消费时刻)
2. [二、母版契约](#二母版契约)
3. [三、母版自检判据（V1–V8）](#三母版自检判据v1v8)
4. [四、导出预设与烘焙](#四导出预设与烘焙)
5. [五、回导判据](#五回导判据)
6. [六、Unity 回导 lab](#六unity-回导-lab)
7. [七、附：Blender Python 参考](#七附blender-python-参考)
8. [八、未闭合（诚实清单）](#八未闭合诚实清单)
9. [九、参数速查表](#九参数速查表)
10. [十、来源](#十来源)

---

## 一、这是什么（消费时刻）

**解决的是"Blender 里做的动作，Unity 用不了 / 用错了也不知道"这件事。**

没有这条链路时，Blender 里做出的动作没有统一的骨架与导出预设，容易出四类**假完成**：控制骨泄漏进 FBX、
多出一层 Leaf Bone、Rest Pose 在往返中漂移、Root 结构分叉——四者都能"导出成功"、也都能在 Unity 里
导成 Generic 或干脆不动，而肉眼从连续播放上看不出来。

| 谁在什么时候读它 | 读什么 |
|---|---|
| 要在 Blender 里做/改一条正式动作的人（或 agent） | §二 母版怎么建、§四 导出预设怎么定 |
| 要判定"这条 FBX 真的能回导复用吗"的人 | §三 / §四 / §五 的判据与阈值 |
| 要在 Unity 里逐帧看这条动作的人 | §六 lab 的生成方式与读数位置 |
| 接 Blender 脚本的人 | §七 SDK 参考（运行方式、API 要点、坑） |
| 切片 `CP-01-ward-1f` 回填四轴状态时 | §一 的能力名 + §八 的未闭合清单 |

**不做什么**（与[对照实验](%E5%8A%A8%E7%94%BB%E5%A4%84%E7%90%86%E8%83%BD%E5%8A%9B%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C.md) §六同口径）：
不新增玩家动作词条、不改战斗数值与状态机、不给 X Bot 加导出 Root 骨、不重导既有 Mixamo 动画、
不做脚滑/重心/审美的自动修复——本条只提供**可观察、可逐帧定位**的制作面与判据。

## 二、母版契约

母版是一份 `.blend`：**原封不动的 Mixamo 骨架 + 蒙皮网格**，加一层**非变形控制骨**。
动作在控制骨上做，导出时把控制结果烘到变形骨上——于是"Blender 里能调"与"Unity 里能复用"是同一套骨。

| 项 | 取值 | 依据 |
|---|---|---|
| 输入载体 | `code/unity/Assets/Mixamo/Characters/X Bot.fbx`（**只读**） | [对照实验](%E5%8A%A8%E7%94%BB%E5%A4%84%E7%90%86%E8%83%BD%E5%8A%9B%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C.md) §2.1 |
| 输入指纹 | `sha256 = cd60e51571bb7c0c1988ec58b3be174c91bd193b6372a9064f1ec2553bc8deab` | 实测（运行前后一致，由 V1 每次核） |
| 生成命令 | `blender --background --factory-startup --python-exit-code 1 --python code/tools/build_xbot_animation_template.py -- [--force]` | 本文 §七·1 |
| 默认输出 | `.scratch/blender_assets/xbot/XBot_AnimationTemplate.blend`（被 `.gitignore` 排除） | 过程物不入库；入库的是脚本与探针 FBX |
| 骨架 | 65 根骨 · 单一根 `mixamorig:Hips` · 全部 `mixamorig:*` 前缀 | 实测（V2） |
| 控制层 | **13 根** `CTRL_*`：骨盆 1 · 双腿 6（髋/膝/踝 ×2）· 双臂 6（肩关节/肘/腕 ×2），全部 `use_deform = False` | 本条「覆盖骨盆、双腿和双臂控制」的要求 |
| 控制链 | 控制骨自成一**平行链**（`CTRL_Hips` 为根），**不插进** `mixamorig` 链 | 插进去会改变变形骨的父子关系，破坏 V3 |
| 驱动方式 | 变形骨加 Bone Constraint：`COPY_ROTATION`（`LOCAL`↔`LOCAL`，`REPLACE`）；骨盆另加 `COPY_LOCATION`（同空间口径） | 控制骨因此**真的**驱动身体（V6 逐根实测） |
| 不带源动画 | 导入时 `use_anim=False` | 控制层用约束覆盖变形骨；若同一条骨上同时有源 action 的位移/缩放通道，就有两个写者，读数无法归属。源动画仍可从 X Bot.fbx 取，不存第二份 |
| 场景帧率 | 30 fps（与既有 15 条 Mixamo FBX 实测一致） | 实测 |
| 母版自带动作 | `RigRoundTripProbe`：4 个关键帧（1 / 21 / 41 / 61），键在**控制骨**上 | 既是控制层的接线自检（V8），也是导出的输入 |
| 探针动作幅度 | 骨盆 ±（+2.5 / −1.5）**骨架局部单位**；四肢 16°–32° | 演示常量，非正典参数 |

⚠️ **单位口径**（踩过）：本骨架是 Mixamo 的**厘米制** + Armature 对象 `scale = 0.01`，因此
**姿态骨的 `location` 单位是骨架局部单位 = 1 cm = 10 mm 世界**，不是米。把"20 mm"写成 `0.02`
会让骨盆只动 0.2 mm——2026-09-14 实测踩到，被 V8 拦下。

## 三、母版自检判据（V1–V8）

`build_xbot_animation_template.py` 每次运行都跑这 8 条，任一不过即非 0 退出并写进报告 JSON。

| # | 判据 | 阈值 / 口径 | 实测（2026-09-14，Blender 4.5.13 LTS） |
|---|---|---|---|
| V1 | 输入 FBX 字节哈希运行前后一致 | 相等 | `cd60e515…8deab` ✓ |
| V2 | 骨数 65 · 单一根 `mixamorig:Hips` · 全 `mixamorig:*` 前缀 | 硬判 | 65 / `['mixamorig:Hips']` / ✓ |
| V3 | 存盘并**重新打开** `.blend` 后，父子关系与 V2 逐条相同 | 硬判 | ✓（共 78 骨 = 65 变形 + 13 控制） |
| V4 | 重新打开后 Rest Pose（`matrix_local`）逐条相同 | 硬判 | ✓ |
| V5 | 所有 `CTRL_*` 的 `use_deform == False` | 硬判 | 13/13 ✓ |
| V6 | 每根控制骨都能真实驱动对应变形骨 | 骨尖位移 ≥ **20 mm**（摆 25°） | 最小 **35.6121 mm** ✓ |
| V7 | 探针动作覆盖 13 根控制骨 | 逐根有键 | 13/13，42 条 F-Curve ✓ |
| V8 | 探针动作**非退化**：每个读数点都在动 | 逐点 ≥ **20 mm** | 最大 **820.21 mm**；逐点 Hips 42.05 / 左手 746.38 / 右手 820.21 / 左脚 608.26 / 右脚 601.19 ✓ |

### 为什么单独有 V8（一次真实的假绿）

2026-09-14 实测：第一版母版把控制骨的 `rotation_mode` 在归零时打回了 `QUATERNION`，而探针动作写的是
`rotation_euler` 通道——**关键帧全部失效，身体一动不动**。而下游的"烘焙保真"（E1）与"回导保真"（E6）
都是**两侧比对**：两侧同样静止 ⇒ 差值 0 ⇒ **双双平凡通过**。症状只有到 Unity 侧才现形
（clip 有时长、130 条曲线**全 constant**）。

⇒ 凡是"两侧比对"型判据，都必须配一条**非退化**判据（V8 / E0）：先证明源在动，再谈保真。

## 四、导出预设与烘焙

```bash
blender --background --factory-startup --python-exit-code 1 \
  --python code/tools/export_xbot_action.py -- --action RigRoundTripProbe [--force]
```

### 4.1 烘焙（控制层 → 变形骨）

| 步 | 做法 | 为什么 |
|---|---|---|
| 1 | 只选中 65 根变形骨，`bpy.ops.nla.bake(visual_keying=True, only_selected=True)` | 取"约束求值后"的视觉姿势，而不是骨的自身通道 |
| 2 | **`use_current_action=True`**（就地烘焙） | ⚠️ 用 `False` 会**当场把控制骨 action 摘下来**，逐帧求值时控制骨恒为静止 ⇒ 烘出一条**常量**曲线，而它与"母版静止"逐位相同、E1/E6 平凡通过。2026-09-14 实测踩到 |
| 3 | 烘完把 `CTRL_*` 通道从 action 里剥掉 | 导出物里的姿势**只来自显式关键帧**，不依赖控制层 |
| 4 | 解除 14 条约束 | 同上：导出不再依赖控制层是否健在 |
| 5 | 关键帧整体平移，让动作从**第 0 帧**开始 | FBX 的 take 是 0 基；既有 Mixamo FBX 在 Blender 里都从第 1 帧读入。归零后两端帧号**逐帧对齐**（实测 offset = 0） |
| 6 | 场景改名 = 动作名 | FBX take 名取自 `<Armature>\|<场景名>` ⇒ take 成为 `Armature\|RigRoundTripProbe` |

### 4.2 `export_scene.fbx` 预设（逐项都有理由）

| 选项 | 取值 | 理由 |
|---|---|---|
| `object_types` | `{"ARMATURE"}` | **无网格** ⇒ animation-only（与 15 条 Mixamo 动画 FBX 同形态） |
| `use_armature_deform_only` | `True` | **控制骨不外泄**的唯一开关（E2 实测 0 条） |
| `add_leaf_bones` | `False` | **不新增 Leaf Bone**（E2/E3 实测仍 65 根） |
| `axis_forward` / `axis_up` | `-Z` / `Y` | Unity 约定；与既有 Mixamo FBX 同口径 |
| `global_scale` / `apply_unit_scale` / `apply_scale_options` | `1.0` / `True` / `FBX_SCALE_NONE` | 不做二次缩放：往返后骨长逐条一致（E5） |
| `bake_space_transform` | `False` | 不烘空间变换，保留骨架自身的层级与轴向 |
| `bake_anim_use_nla_strips` / `bake_anim_use_all_actions` | `False` / `False` | 只导当前 action，不把 NLA 里别的动作带出去 |
| `bake_anim_step` / `bake_anim_simplify_factor` | `1.0` / `0.0` | 逐帧、**不做关键帧简化** ⇒ 可复现 |
| `primary_bone_axis` / `secondary_bone_axis` | `Y` / `X` | 与导入侧默认一致，往返不改骨朝向 |
| `use_custom_props` | `False` | FBX 不背第二份真相源（同 [#143](https://github.com/verystrongdog/game/issues/143) 的裁定：自定义属性不入 FBX，映射由运行时读契约——见 [code/unity/README.md](../../code/unity/README.md) §二·K 发现 2） |

### 4.3 导出侧自检判据（E0–E6）

| # | 判据 | 阈值 | 实测 |
|---|---|---|---|
| E0 | 源动作**非退化**（防 E1/E6 平凡通过） | ≥ 20 mm | **274.7759 mm** ✓ |
| E1 | 烘焙保真：烘后 vs 烘焙前（同帧同骨） | ≤ 0.5 mm | **0.0011 mm** ✓ |
| E2 | 骨集：65 变形骨 · `CTRL_` **0** 条 · 无多余骨 | 硬判 | 65 / 0 / 0 ✓ |
| E3 | 单一根骨 `mixamorig:Hips`（无额外 Root 骨 / 无新增 Leaf Bone） | 硬判 | `['mixamorig:Hips']` ✓ |
| E4 | 不含网格（animation-only） | 硬判 | `[]` ✓ |
| E5 | Rest Pose 与源逐元素一致 | ≤ 1e-4 | 最大元素差 **9.2e-05** ✓ |
| E6 | 回导保真：FBX 重新导入后逐帧姿势 vs 母版 | ≤ 0.5 mm | **0.0014 mm**（帧号 offset 0）✓ |

导出物：`RigRoundTripProbe.fbx` · 684 044 字节 · take `Armature|RigRoundTripProbe` ·
导出帧 0–60（61 键 @30 fps = 2.000 s）· 烘焙 715 条 F-Curve，剥掉 42 条控制通道，解除 14 条约束。

> ⚠️ **E1/E6 只证明"Blender 侧往返无损"**，不证明 Unity 侧的重定向行为——后者见 §五。

## 五、回导判据

### 5.1 读数点（两端同一组骨）

`Hips` · `LeftHand` · `RightHand` · `LeftFoot` · `RightFoot`。
Blender 侧是 `export_xbot_action.py` 的 `READOUT_BONES`（`mixamorig:` 名），
Unity 侧是 `BlenderAnimationDebugger.ReadoutBones`（`HumanBodyBones` 枚举）——**同一组人形骨**。

### 5.2 Unity 侧怎么定位到某一帧（确定性路径）

`Animator.Play(state, 0, normalizedTime)` + `Animator.Update(0f)`，顺序固定为
**Play → `Update(0f)` → 再冻结 `speed`**（先冻结 `speed` 再 Play 不生效；不调 `Update(0f)` 定位不生效）。
来源：[unity-cli README](../../code/tools/unity-cli/README.md) §五 与 `AnimationRiggingProbe.PoseAtFrame` 的实测注。

帧号域：`0 .. clip.length × clip.frameRate`（本探针 = `0..60`）。

### 5.3 Unity 侧判据

| 判据 | 口径 | 实测（2026-09-14） |
|---|---|---|
| Humanoid 导入 | `animationType = Human` · `avatarSetup = CreateFromThisModel` | `3` / `1`（与 A4 机械口径一致） |
| 回导样本是"人形运动" | `clip.humanMotion == true` | `True` |
| **无导入告警** | `animationImportErrors` / `animationImportWarnings` / `animationRetargetingWarnings` **三串皆空** | 三串皆空（落 `.fbx.meta`，由 builder 自检每次核） |
| 时长 / 帧率 | 与源一致 | `2.0000 s` / `30` |
| Avatar | 由本模型自建且有效 | `RigRoundTripProbeAvatar` · `isValid=True` · `isHuman=True` |
| **关掉关键帧压缩** | `animationCompression = Off` | 见 §5.4 的坑 |
| 同一 clip 同一帧重复采样 | 读数**逐次一致** | 三次逐字节相同 ✓ |
| 帧间确实在动 | 见 §六 的逐点下限 | Hips 16.94 mm · 左手 677.06 mm · 左脚 550.98 mm ✓ |

### 5.4 ⚠️ 两处口径差异（实测，别当成 bug）

1. **Unity 的 Hips 位移与 Blender 的髋骨世界位移不是同一个量。**
   Blender 侧髋骨世界位移量程 **40.0 mm**（f21 = 静止 +25.0，f41 = 静止 −15.0）；
   Unity 侧 Hips 节点量程 **16.94 mm**，而其 `RootT.y`（人形 body position）曲线峰值出现在**同一帧**
   （`t = 0.6667` ↔ 第 20 帧），量程 41.6 mm。
   ⇒ **趋势与峰值帧一致，绝对量不可逐值比对**：Unity 把源骨架的髋位移重定向进"人形 body position"
   归一化空间后再落到 Hips 节点。要看"骨盆控制有没有被覆盖"，判据是**峰值帧与趋势**，不是毫米数。
2. **Unity 默认的关键帧压缩会把骨盆位移降采样掉。** 默认 `KeyframeReduction` +
   `animationPositionError = 0.5` 把 `RootT.y` 从 **61 键降到 3 键**：峰值还在、低谷被抹平，
   于是骨盆读数只剩 17 mm。探针的用途是逐帧比对，压缩会让"差异"无法归属到回导本身
   ⇒ 探针 FBX 的导入设置固定 `animationCompression = Off`（由 `BlenderAnimationDebugBuilder` 幂等纠正并自检）。

> 本条**不**主张"Unity 姿势应当与 Blender 逐值相同"：那是重定向语义问题，不在本 issue 的验收面内。

## 六、Unity 回导 lab

| 项 | 值 |
|---|---|
| 菜单 | `YANTF → 动作演示 → 创建 Blender 回导调试 lab`（幂等；headless 走 `CreateSceneBatch`） |
| 场景 | `Assets/Temp/BlenderRoundTripDebug.unity`（**生成物，不入库**——`[Tt]emp/` 被 `.gitignore` 排除） |
| controller | `Assets/Temp/BlenderRoundTripDebug.controller`（单状态 = 探针 clip，同属生成物） |
| 载体 | X Bot 实例 + `Animator`（avatar 取自 X Bot）+ `BlenderAnimationDebugger`，站在原点、`applyRootMotion = false` |
| 逐帧控制 | 空格 播放/暂停 · ←/→ 前后单帧 · `R` 回首帧；HUD 显示 `clip / 帧号 / 五个读数点` |
| 与既有 lab 的关系 | **互不引用、互不修改**：不动 `ActionLab` / `AnimationRiggingLab` 场景、controller 与脚本 |
| 断言 | `Assets/Tests/PlayMode/BlenderAnimationDebugTests.cs`（7 条：Rig 2 + 采样 1 + 控制 2 + 形状 1 + 资产身份 1） |

### 6.1 幂等怎么判

lab 的**场景文件字节不是幂等的**（Unity 每次重建都会换内部 fileID），但**结构指纹是**：
实测连续两次生成后，`rootCount` / 每根 root 的 transform 数与组件类型集合 / 载体名 /
controller 名 / clip 名 / frameCount / avatar 名**逐字节相同**。判据取后者。

### 6.2 ⚠️ 三条实测坑

1. **`EnsureController` 不得无条件删了重建**：`DeleteAsset` + `CreateAnimatorControllerAtPath`
   会给资产换一个新 GUID，**已存盘 lab 场景里那条引用随即 missing**。症状极具误导性——
   场景在、Animator 在、`clip=(none) frameCount=0`、姿势永远不动。
   现在的做法是"内容已经对就复用"（按 clip **名**比对，不按引用比对）。
2. **在 Play 态下跑菜单会报 `InvalidOperationException`**（"This cannot be used during play mode"）——
   生成 lab 前先退出 Play。
3. **`recompile_status` 报 `up_to_date` 不等于没有编译错误**：同步过去的新 `.cs` 若编译失败，
   该命令仍回 `failed: false`，但 `list_tests` 里看不到新测试。**判据要读 `console --level error`。**

### 6.3 实测读数（Editor 6000.5.2f1）

| 帧 | Hips | LeftHand | RightHand | LeftFoot | RightFoot |
|---|---|---|---|---|---|
| 0 | `(-0.00253, 1.04270, 0.02702)` | `(-0.71586, 1.44057, -0.04401)` | `(0.71080, 1.44057, -0.04400)` | `(-0.08461, 0.08730, -0.01595)` | `(0.07955, 0.08730, -0.01595)` |
| 20 | `(0.00088, 1.02723, 0.02103)` | `(-0.68156, 1.26361, -0.05000)` | `(0.49423, 1.83570, -0.05107)` | `(-0.08119, 0.12485, 0.23249)` | `(0.08297, 0.13249, -0.30985)` |
| 40 | `(-0.00740, 1.03034, 0.02107)` | `(-0.41410, 1.88560, -0.04990)` | `(0.69580, 1.19352, -0.05010)` | `(-0.18262, 0.14848, -0.30856)` | `(-0.01997, 0.12425, 0.23265)` |
| 60 | 与帧 0 **逐位相同**（探针首末帧同为静止姿势） | 同左 | 同左 | 同左 | 同左 |

- 帧号 → Blender 源帧：`+1`（导出已归零，实测 offset = 0）。
- 同一帧（第 20 帧）重复三次采样：`ReadoutLine()` **逐字节相同**。
- 帧间最大位移：Hips 16.94 mm · 左手 677.06 mm · 左脚 550.98 mm（阈值 10 / 300 / 200 mm）。

## 七、附：Blender Python 参考

> 本节是 Blender 侧脚本的 **SDK 参考**（运行方式、用到的 API、踩过的坑）。落地位置由 owner
> 2026-09-14 裁定：折进本文作附节，不另开 `docs/` 顶层目录、不做第二份真相源。

### 7.1 怎么跑（本机实测口径）

```bash
B=.scratch/blender-lts/blender-4.5.13-linux-x64/blender   # 便携包，落被 gitignore 的 .scratch/
"$B" --background --factory-startup --python-exit-code 1 \
     --python code/tools/<脚本>.py -- <脚本自己的参数>
```

| 开关 | 为什么必须 |
|---|---|
| `--background` | 无头；本机无 GPU 直通，交互式界面不可用 |
| `--factory-startup` | 不吃用户配置与已装插件 ⇒ 可复现 |
| `--python-exit-code 1` | ⚠️ **不加它，脚本抛异常后 Blender 仍退出 0**（实测）⇒ 门禁形同虚设 |
| `--` | 其后才是脚本自己的参数；脚本内用 `sys.argv` 的 `--` 之后切片 |

脚本内的仓库根：`Path(__file__).resolve().parents[2]`（脚本位于 `code/tools/`）。

### 7.2 用到的 API 与要点

| 事项 | 做法 / 要点 |
|---|---|
| 空场景起步 | `bpy.ops.wm.read_factory_settings(use_empty=True)` |
| 导入 FBX | `bpy.ops.import_scene.fbx(filepath=..., use_anim=False)`；`use_anim=False` 不导入动画 |
| 骨架编辑 | `bpy.ops.object.mode_set(mode="EDIT")` → `arm.edit_bones.new(...)`；`EditBone` 有 `use_deform` / `roll`，`Bone` **没有** |
| 取"约束求值后"的姿势 | `dg = bpy.context.evaluated_depsgraph_get()` → `ev = arm.evaluated_get(dg)` → `ev.matrix_world @ ev.pose.bones[b].head/tail`（改姿势后先 `bpy.context.view_layer.update()`） |
| 约束 | `pb.constraints.new("COPY_ROTATION")`，`target_space`/`owner_space` 用 `"LOCAL"`；`COPY_ROTATION` 有 `mix_mode`，**`COPY_LOCATION` 没有** |
| 烘焙 | `bpy.ops.nla.bake(..., visual_keying=True, only_selected=True, use_current_action=True)`；**必须就地烘**（见 §四·1 步 2） |
| 关键帧平移 | 直接改 `kp.co.x` / `kp.handle_left.x` / `kp.handle_right.x`，改完 `fc.update()` |
| 存盘后重新读回校验 | `bpy.ops.wm.save_as_mainfile(...)` → `bpy.ops.wm.open_mainfile(...)` → 重新取指纹比对。⚠️ 旧对象引用会失效（`ReferenceError: StructRNA ... has been removed`），先把要打印的摘要取成局部变量 |
| 姿态骨位移单位 | 骨架局部单位（本骨架 cm；见 §二 的 ⚠️） |
| FBX 版本 | Blender 4.5 导出 **7400**；既有 Mixamo FBX 是 **7700**。Unity 两者都吃 |

### 7.3 三条踩过的坑（本管线实测）

1. **`use_current_action=False` 会摘掉正在驱动骨头的 action** ⇒ 烘出常量曲线（§四·1 步 2）。
2. **`rotation_mode` 被打回 `QUATERNION` 会让 euler 关键帧失效**（§三 的 V8 由来）。
3. **"两侧比对"型判据必须配非退化判据**（V8 / E0），否则源静止时全部平凡通过。

## 八、未闭合（诚实清单）

1. **Unity 侧骨盆读数低于 Blender 侧**（16.94 mm vs 40.0 mm）——量的是两个不同的量（§5.4·1）。
   本条的验收面是"探针覆盖骨盆控制"，已由**母版侧 V8（42.05 mm）** 与 **回导保真 E6（0.0014 mm）**
   成立；Unity 侧只主张"趋势与峰值帧一致"。
2. **只验了 Blender 4.5.13 LTS（linux-x64 便携包）**。本机 Windows 侧装的是 5.1.2，
   **未做 5.1 的横向对照**；FBX 版本差异（7400 vs 既有 7700）也**未做 Unity 侧兼容性专项验证**，
   只验了"本机 Unity 6000.5.2f1 能吃"。
3. **未做完整 Editor 重启后的复现**：幂等与确定性读数是在同一 Editor 会话内实测的。
4. **危险点表未登记本条的三条坑**——`design/engineering/危险点表.md` 不在本条的「预期差分」内，
   按 [WORKFLOW.md §一](../../WORKFLOW.md) 非阻塞发现进候选队列，不在本条顺手改。
5. **基线**：Unity 侧读数取自 Windows 工作拷贝（`C:\Users\9527\game\code\unity`，其 git HEAD 落后
   仓库 HEAD，见[危险点表](../engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md) §七），
   补偿证据是逐字节内容比对（探针 FBX 与 `.meta` 三侧同哈希）。
6. **只做了 1 条探针动作**（骨盆 + 双腿 + 双臂各一次摆动的演示幅度），
   未做"正式动作"的制作验证；正式动作的准入属切片 `CP-01-ward-1f`。

## 九、参数速查表

| 参数 | 符号 | 默认值 | 位置 |
|---|---|---|---|
| 场景帧率 | — | `30` fps | `build_xbot_animation_template.py` `SCENE_FPS` |
| 探针关键帧 | — | `1 / 21 / 41 / 61` | 同上 `PROBE_FRAMES` |
| 控制骨驱动判据阈值 | — | `20` mm（摆 25°） | 同上 `CTRL_DRIVE_MIN_MM` / `CTRL_DRIVE_TEST_DEG` |
| 探针非退化阈值 | — | `20` mm | 同上 `V8_MIN_MOTION_MM` |
| 源动作非退化阈值 | — | `20` mm | `export_xbot_action.py` `E0_MIN_MOTION_MM` |
| 烘焙保真容差 | — | `0.5` mm | 同上 `E1_TOL_MM` |
| Rest Pose 元素容差 | — | `1e-4` | 同上 `E5_TOL` |
| 回导保真容差 | — | `0.5` mm | 同上 `E6_TOL_MM` |
| 逐点帧间位移下限 | — | Hips `10` · 手 `300` · 脚 `200` mm | `BlenderAnimationDebugTests.MotionMinMm` |

## 十、来源

| 事实 | 来源 |
|---|---|
| 载体是 Mixamo X Bot、Humanoid、指纹 `cd60e515…` | [动画处理能力对照实验](%E5%8A%A8%E7%94%BB%E5%A4%84%E7%90%86%E8%83%BD%E5%8A%9B%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C.md) §2.1 |
| 产物去向（Blender 线落 `Assets/Animations/Blender/`） | 同上 §五 |
| 共同禁止事项（不覆盖源文件、不改既有动画） | 同上 §六 |
| 母版与导出物的全部读数（V1–V8 / E0–E6） | `design/engineering/evidence/blender-xbot-pipeline-2026-09-14.md` |
| 确定性姿势求值路径与三个坑 | [unity-cli README](../../code/tools/unity-cli/README.md) §五 |
| 资产身份（`.meta` GUID 由 Editor 定、仓库采用同 GUID；lab 场景入库与否的口径） | [code/unity/README.md](../../code/unity/README.md) §二·H / §二·P |
| X Bot 的 Unity 导入设置口径（`animationType: 3` / `avatarSetup: 1`） | `code/tools/validate_unity_assets.py` A4 规则注释 |

---
*创建: 2026-09-14 | 更新: 2026-09-14*
*状态: 与 [动画处理能力对照实验](%E5%8A%A8%E7%94%BB%E5%A4%84%E7%90%86%E8%83%BD%E5%8A%9B%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C.md) 同为**两条线共用的口径正典**；本文只覆盖 Blender 线。*
*关联: [动画处理能力对照实验](%E5%8A%A8%E7%94%BB%E5%A4%84%E7%90%86%E8%83%BD%E5%8A%9B%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C.md), [动作库规格](%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md), [code/unity/README.md](../../code/unity/README.md), [危险点表](../engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md)*
