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
| ⚠️ 别把载体认错 | X Bot 与 Y Bot **不是同一套网格**：X Bot = `Beta_Joints`/`Beta_Surface`（主材质 `#AB3E36`，**砖红偏粉**）；Y Bot = `Alpha_Body`/`Alpha_Joints`（主材质 `#14566A`，**青蓝**）。两者是两套外观近乎相同的 Mixamo 男模，**看颜色比看名字可靠**（实测 2026-09-14） | `Assets/Mixamo/Characters/*.fbx` 的共享材质 |
| 输入指纹 | `sha256 = cd60e51571bb7c0c1988ec58b3be174c91bd193b6372a9064f1ec2553bc8deab` | 实测（运行前后一致，由 V1 每次核） |
| 生成命令 | `blender --background --factory-startup --python-exit-code 1 --python code/tools/build_xbot_animation_template.py -- [--force]` | 本文 §七·1 |
| 默认输出 | `.scratch/blender_assets/xbot/XBot_AnimationTemplate.blend`（被 `.gitignore` 排除） | 过程物不入库；入库的是脚本与探针 FBX |
| 骨架 | 65 根骨 · 单一根 `mixamorig:Hips` · 全部 `mixamorig:*` 前缀 | 实测（V2） |
| 控制层 | **13 根** `CTRL_*`：骨盆 1 · 双腿 6（髋/膝/踝 ×2）· 双臂 6（肩关节/肘/腕 ×2），全部 `use_deform = False` | 本条「覆盖骨盆、双腿和双臂控制」的要求 |
| 控制链 | 控制骨自成一**平行链**（`CTRL_Hips` 为根），**不插进** `mixamorig` 链 | 插进去会改变变形骨的父子关系，破坏 V3 |
| 驱动方式 | 变形骨加 Bone Constraint：`COPY_ROTATION`（`LOCAL`↔`LOCAL`，`REPLACE`）；骨盆另加 `COPY_LOCATION`（同空间口径） | 控制骨因此**真的**驱动身体（V6 逐根实测） |
| 不带源动画 | 导入时 `use_anim=False` | 控制层用约束覆盖变形骨；若同一条骨上同时有源 action 的位移/缩放通道，就有两个写者，读数无法归属。源动画仍可从 X Bot.fbx 取，不存第二份 |
| GUI 可用性 | 13 根控制骨归入骨骼集合 **`CTRL`**（配色 `THEME04`、八面体显示），65 根变形骨归入 **`MIXAMORIG`**；两个集合**默认都可见**。⚠️ 控制骨与目标骨 head/tail/roll **完全重合**，同屏时点不准——**要"只点控制骨"就把 `MIXAMORIG` 集合关掉**。纯显示层：不进 FBX、不改约束映射（已复核导出物等价，§四·4） | V9 自检 |
| 场景帧率 | 30 fps（与既有 15 条 Mixamo FBX 实测一致） | 实测 |
| 母版自带动作 | `RigRoundTripProbe`：4 个关键帧（1 / 21 / 41 / 61），键在**控制骨**上 | 既是控制层的接线自检（V8），也是导出的输入 |
| 探针动作幅度 | 骨盆 ±（+2.5 / −1.5）**骨架局部单位**；四肢 16°–32° | 演示常量，非正典参数 |
| ⚠️ 探针**观感**（实测几何） | 关键帧绕的是**骨的局部 X 轴**，在这套 Mixamo 骨轴上那是**竖直面内的抬摆**而非前后摆：实测左手**相对肩 −0.1824 → +0.4450 m**（摆到过头）；双脚 y 只在 **0.0868–0.1496 m**（**贴地前刮、几乎不抬脚**）；骨盆只做起落。合起来的观感**类似走钢丝**——这是覆盖性探针的必然长相，不是缺陷（审美与脚滑在本条「明确排除」内；owner 2026-09-14 目视确认为「没有发现明显问题」） | Play 内逐帧读数，见本文 §六·3 |

⚠️ **单位口径**（踩过）：本骨架是 Mixamo 的**厘米制** + Armature 对象 `scale = 0.01`，因此
**姿态骨的 `location` 单位是骨架局部单位 = 1 cm = 10 mm 世界**，不是米。把"20 mm"写成 `0.02`
会让骨盆只动 0.2 mm——2026-09-14 实测踩到，被 V8 拦下。

### 2.1 GUI 操作手册（调动作的完整动作序列）

**打开**（命令见 §7.1；⚠️ 必须用 `Z:` 盘符路径 + `Start-Process`，否则会静默回落到默认立方体场景）：

```powershell
net use Z: \\wsl.localhost\Ubuntu-22.04
Start-Process "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -ArgumentList 'Z:\home\dog\game\.scratch\blender_assets\xbot\XBot_AnimationTemplate.blend'
```

然后：

| 步 | 操作 | 为什么 / 注意 |
|---|---|---|
| 1 | 点视口里的**骨架**（或 Outliner 里的 `Armature`）→ `Ctrl+Tab` 或左上角模式下拉 → **Pose Mode** | 编辑模式改的是静止姿势，**会破坏 V3/V4** |
| 2 | Outliner 的骨骼集合里**关掉 `MIXAMORIG`**（眼睛图标） | 控制骨与目标骨 head/tail/roll **完全重合**，13 根变形骨挡在前面时点不准 |
| 3 | 选一根 `CTRL_*`（或在 Outliner 里点名字） | **只动 `CTRL_*`**；直接转 `mixamorig:*` 会被约束覆盖（转了个寂寞） |
| 4 | `R` 起转 → 按 `X`/`Y`/`Z` 锁轴 → 输入角度 → 回车 | 也可以 `N` 打开侧栏，在 `Item → Rotation Euler` 里填数值（更精确） |
| 5 | 满意后**打关键帧**：`I` → 选 `Rotation`（或 Dope Sheet 里右键 → Insert Keyframe） | 只在控制骨上打；变形骨不需要键（导出时自动烘） |
| 6 | `Ctrl+S` 存回原路径 → 退出 GUI → 跑导出脚本（§四） | Blender **独占**文件；GUI 开着时导出脚本读的是磁盘上已存的那版 |

⚠️ **两条会让关键帧"白打"的红线**：

1. **别改控制骨的 `rotation_mode`**：脚本建的控制骨是 **XYZ 欧拉**、探针动作写在 `rotation_euler` 通道上。改成 `Quaternion` 后那些键**不再驱动姿势**（§三 V8 就是为这条设的）。
2. **别用"整套姿势取负号"做镜像**（下面 §2.1.1 是实测依据）。

#### 2.1.1 13 根控制骨 → 它们驱动什么

| 控制骨 | 驱动 | 通俗说法 | 局部 X +20° | 局部 Y +20° | 局部 Z +20° |
|---|---|---|---|---|---|
| `CTRL_Hips` | `mixamorig:Hips` | 骨盆（全身根） | **前倾**（头顶前 337 mm） | **转身**（左手 278 · 中指尖 326 mm；**头顶仅 1 mm**） | **侧倾**（头顶侧 −345 mm） |
| `CTRL_LeftUpLeg` / `CTRL_RightUpLeg` | 同名 | 左/右**髋** | **前摆**（脚 +332 mm） | 整腿**内/外旋**（趾尖 +90 mm） | **外展/内收**（脚 侧 +334 mm） |
| `CTRL_LeftLeg` / `CTRL_RightLeg` | 同名 | 左/右**膝** | **小腿前摆**（脚 +179 mm） | 小腿旋（趾尖 +71 mm） | 侧向（脚 +177 mm） |
| `CTRL_LeftFoot` / `CTRL_RightFoot` | 同名 | 左/右**踝** | **勾/绷脚**（脚 上 +72 mm） | 足旋（趾 +20 mm） | 侧向（脚 +72 mm） |
| `CTRL_LeftArm` / `CTRL_RightArm` | 同名 | 左/右**肩** | **落臂**（手 上 −219 mm） | **沿臂扭转**（直臂时指尖 **0 mm**；弯肘时会大幅摆动下游） | **前后摆**（左手 前 +219 / **右手 前 −219**） |
| `CTRL_LeftForeArm` / `CTRL_RightForeArm` | 同名 | 左/右**肘** | 落（手 −124 mm） | 前臂旋 | 前后（左 +124 / **右 −124**） |
| `CTRL_LeftHand` / `CTRL_RightHand` | 同名 | 左/右**腕** | 落（−28 mm） | 手旋 | 前后（左 +28 / **右 −28**） |

> 表里每个数字都是 2026-09-14 实测：绕该控制骨**局部轴** +20°，量**链末标志点**（腿=趾尖、臂=指尖、骨盆=头顶/左手/指尖）的位移，方向分解为「体侧 / 前后 / 上下」。**可复现**：跑 §7.4 的 `measure_xbot_control_axes.py`，本表即其 `control_axes.json` 的读数。

#### 2.1.2 符号规则：**左右不统一，不能整套取负号**

实测两套骨骼的静止局部轴（`matrix_local`，用 head→tail 交叉核对过）：

| 部位 | 左 | 右 | 结论 |
|---|---|---|---|
| 髋/膝/踝 | X = `(−1,0,0)` | X = `(−1,0,0)` | **完全同轴** ⇒ 同号 = **同向世界位移**（左腿外展 / 右腿内收）；交替迈步要**分别给正负** |
| 肩/肘/腕 | X = `(0,0,−1)` · Z = `(0,−1,0)` | X = `(0,0,+1)` · Z = `(0,−1,0)` | **镜像**（X 反号、Z 同号）⇒ **X 取同号 = 对称**（两臂一起落）；**Z 要镜像必须给相反符号**（双手一起向前 = 左 `Z+` / 右 `Z−`） |

⇒ **做镜像动作或左右对称姿势时，逐骨定符号**；"把一组数值取负"会把腿做成同向、把手臂做成反向。

#### 2.1.3 摆不出来的三个自查

| 症状 | 先查 |
|---|---|
| 转了骨、画面完全不动 | 转的是 `mixamorig:*`（被约束覆盖）还是 `CTRL_*`？ |
| 关键帧打了但播放时姿势不变 | `rotation_mode` 是不是被改成 `Quaternion` 了？（§2.1 红线 1） |
| 左右腿"镜像"后变成同向 | 腿本来就不同轴——按 §2.1.2 逐侧给符号 |

## 三、母版自检判据（V1–V8）

`build_xbot_animation_template.py` 每次运行都跑这 8 条，任一不过即非 0 退出并写进报告 JSON。

| # | 判据 | 阈值 / 口径 | 实测（2026-09-14，**基线 Blender 5.1.2**；4.5.13 为已验的第二版本） |
|---|---|---|---|
| V1 | 输入 FBX 字节哈希运行前后一致 | 相等 | `cd60e515…8deab` ✓ |
| V2 | 骨数 65 · 单一根 `mixamorig:Hips` · 全 `mixamorig:*` 前缀 | 硬判 | 65 / `['mixamorig:Hips']` / ✓ |
| V3 | 存盘并**重新打开** `.blend` 后，父子关系与 V2 逐条相同 | 硬判 | ✓（共 78 骨 = 65 变形 + 13 控制） |
| V4 | 重新打开后 Rest Pose（`matrix_local`）逐条相同 | 硬判 | ✓ |
| V5 | 所有 `CTRL_*` 的 `use_deform == False` | 硬判 | 13/13 ✓ |
| V6 | 每根控制骨都能真实驱动对应变形骨 | 骨尖位移 ≥ **20 mm**（摆 25°） | 最小 **35.6121 mm** ✓ |
| V7 | 探针动作覆盖 13 根控制骨 | 逐根有键 | 13/13，42 条 F-Curve ✓ |
| V8 | 探针动作**非退化**：每个读数点都在动 | 逐点 ≥ **20 mm** | 最大 **820.21 mm**；逐点 Hips 42.05 / 左手 746.38 / 右手 820.21 / 左脚 608.26 / 右脚 601.19 ✓ |
| V9 | 显示层：骨骼集合 `CTRL`/`MIXAMORIG` 分别是 13 / 65 根 | 硬判 | `{'CTRL': 13, 'MIXAMORIG': 65}` ✓ |

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
| E5 | Rest Pose 与源一致（**骨端点坐标**） | ≤ 0.5 mm | 4.5 侧 **0.092 mm** · 5.1 侧 **0.122 mm** ✓（矩阵元素差仅作噪声读数：9.2e-05 / 1.22e-04） |
| E6 | 回导保真：FBX 重新导入后逐帧姿势 vs 母版 | ≤ 0.5 mm | **0.0014 mm**（帧号 offset 0）✓ |

导出物：`RigRoundTripProbe.fbx` · 684 044 字节 · take `Armature|RigRoundTripProbe` ·
导出帧 0–60（61 键 @30 fps = 2.000 s）· 烘焙 715 条 F-Curve，剥掉 42 条控制通道，解除 14 条约束。

> ⚠️ **E1/E6 只证明"Blender 侧往返无损"**，不证明 Unity 侧的重定向行为——后者见 §五。

### 4.4 ⚠️ 导出物**不可逐字节复现**——判据取「内容等价」

FBX 头部带 `CreationTimeStamp`，且对象 UID 是计数器派生 ⇒ **同一母版连导三次得到三个不同哈希**
（实测 2026-09-14：`1fafa792…` / `f2524de1…` / `f0f55d65…`，三次字节数相同、`diff` 遍布全文）。

⇒ 对**生成物** FBX **不得**用 `sha256` 当"没改动"的判据。可用的判据是**内容等价**：

| 核验方式 | 判据 | 实测 |
|---|---|---|
| 回导到 Blender 逐骨比对 | 65 骨 · Rest Pose 端点差 · 逐帧姿势差 | **0.000000 mm**（GUI 显示层改动前后）· **0.000967 mm**（4.5 产物 vs 5.1 产物） |
| 导出侧自检 | E0–E6 全绿 | 两侧皆绿 |

> 注：**源资产**（`X Bot.fbx` 等入库输入）的 `sha256` 照旧可用——它们是字节冻结的输入，不重生成。

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
| 连续播放 | **在播放层面接成环**（走到末帧自动回首帧）——探针首末帧同为静止姿势，不接环的话按 Play 一秒后画面就"没动静"。接环**只改播放行为**：不动 FBX、不动导入设置，样本本身仍是一次性 |
| 与既有 lab 的关系 | **互不引用、互不修改**：不动 `ActionLab` / `AnimationRiggingLab` 场景、controller 与脚本 |
| 断言 | `Assets/Tests/PlayMode/BlenderAnimationDebugTests.cs`（**8 条**：Rig 3 + 采样 1 + 控制 3 + 资产身份 1） |

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
3. **`MonoBehaviour.Start` 在下一帧才跑，会静默取消调用方刚开的播放**：装配方在同一帧里 `Play()`/`SampleAtFrame()` 之后，`Start` 再按 `_playOnStart` 兜一次就把状态冲掉了（实测表现："接环把播放态关掉了"）。组件用 `_driven` 标记挡住这条。
4. **`recompile_status` 报 `up_to_date` 不等于没有编译错误**：同步过去的新 `.cs` 若编译失败，
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

### 7.1 怎么跑（本机实测口径）· **4.5 与 5.x 双兼容**

**基线 = Blender 5.1.2**（本机 Windows 已装的那个）；脚本经 UNC 读、产物写回 WSL 侧：

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --factory-startup --python-exit-code 1 `
  --python '\\wsl.localhost\Ubuntu-22.04\home\dog\game\code\tools\<脚本>.py' -- <参数>
```

**打开 GUI 调动作**（实测 2026-09-14：从 WSL 侧就能把 Windows 的 Blender 窗口开起来，文件经 UNC 直接读写，
窗口标题回读为 `XBot_AnimationTemplate [...\xbot\XBot_AnimationTemplate.blend] - Blender 5.1.2`）：

```powershell
# 1) 先把 WSL 目录映射成盘符（一次即可，实测可映射成功）
net use Z: \\wsl.localhost\Ubuntu-22.04
# 2) 用盘符路径打开母版——**不要**在这条命令里直接写 UNC（见下方三条坑）
Start-Process -FilePath "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -ArgumentList 'Z:\home\dog\game\.scratch\blender_assets\xbot\XBot_AnimationTemplate.blend'
```

⚠️ **三条实测坑**（2026-09-14，代价：一扇"标题写着母版、画面却是默认立方体"的窗口）：

1. **bash 双引号会把 `\\` 折成单个 `\`**：从 WSL 传 UNC 给 `cmd`/PowerShell 时若用双引号，路径退化成
   **相对路径**，再按调用方的兜底工作目录（cmd 遇到 UNC 会把 cwd 设成 `C:\Windows`）解析 ⇒ 找不到文件。
   ⇒ 传路径一律用**单引号**，或干脆走 `Z:` 盘符（推荐）。
2. **Blender 打不开文件时是「静默回落默认启动场景」，而窗口标题仍显示它尝试打开的路径**——
   于是"标题对了"完全不能证明"画面对了"（实测：标题 `XBot_AnimationTemplate [C:\Windows\wsl.localhost\...]`，
   画面是默认立方体）。**判据要么看图，要么让窗口自证**：启动脚本里读 `bpy.data.filepath` / `bpy.data.objects` 写进文件。
3. **`--python` 也不吃 `//wsl.localhost/...` 形式的路径**（实测：脚本根本没跑，窗口是 `(未命名)` 默认场景）。
   ⇒ 启动脚本先 `Copy-Item` 到 Windows 本地（如 `$env:TEMP`）再传给 `--python`。

> ⚠️ **两条补充实测**（2026-09-14，代价：一轮"改了没生效"的误判）：
> ① **母版路径必须放在 `--python` 之前**——`--python` 排在 `.blend` 前面时，脚本在**文件加载之前**就跑了，
> 它看到的 `bpy.data.filepath` 是空串、`bpy.data.objects` 是默认的 `Camera/Cube/Light`。
> 判据就是读这两个值（§7.5 的桥自证也会打印它们）。
> ② **截图要强制重绘**：`bpy.ops.screen.screenshot` 抓到的是**重绘前**的帧，摆完姿势立刻连拍会得到**两张字节相同**的图；
> 截图前调 `bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP")`。另外 **GUI 截图本来就不逐位可复现**——
> 把物体隐藏再恢复，像素也不会与初次逐位相同，所以像素判据只能比**差异量的量级与位置**。

> 另两条：**必须用 `Start-Process`**（GUI 进程继承调用方 stdout/stderr 句柄，直接前台跑或 `cmd /c start` 不重定向
> 会让调用方**一直等 EOF**——实测卡满 5 分钟超时，而进程早已独立运行，`Start-Process` 实测 **0.54 s** 返回）；
> **Linux 版（WSLg）的 GUI 起不来**（`The Wayland connection broke`），GUI 一律走 Windows 侧已装版。

> **窗口自证脚本**（本机用 `.scratch/open_template_gui.py`，过程物不入库）：打开母版后把
> `blender / filepath / objects / actions / bone_collections` 写进 `.scratch/gui-open-proof.txt`。
> 实测输出：`objects=[('Armature','ARMATURE'), ('Beta_Joints','MESH'), ('Beta_Surface','MESH')]` ·
> `bone_collections=[('CTRL', 13), ('MIXAMORIG', 65)]`——**这才是"窗口里有人体"的判据**。

**兼容分支 = Blender 4.5.13 LTS**（取道层仍支持；本机**不再保留**便携包，要用得自行下载解压到 Windows 本地卷）：

```bash
B=<解压目录>/blender-4.5.13-linux-x64/blender
"$B" --background --factory-startup --python-exit-code 1 \
     --python code/tools/<脚本>.py -- <脚本自己的参数>
```

**版本差异全部收在 `code/tools/blender_action_compat.py`**（两个脚本都只调它）。两侧实测（2026-09-14）：

| 差异点 | Blender 4.5.13（兼容分支） | Blender 5.1.2（**基线**） | 取道层怎么办 |
|---|---|---|---|
| 曲线容器 | `Action.fcurves` | **已移除** → `action.layers[0].strips[0].channelbag(slot).fcurves`（slotted actions） | `action_fcurves()` 按实例探测，取不到返回 `None`（**不当成「0 条曲线」**） |
| 指派后的 slot | 无此概念 | 必须再设 `animation_data.action_slot`，否则**不驱动任何东西** | `assign_action()`：有 slot 指第一个，没 slot 先建一个 |
| 姿态骨选择位 | `Bone.select` | `Bone.select` **已移除** → `PoseBone.select` | `select_pose_bones()` 按属性存在性二选一，并把实际用的属性记进报告 |
| 类型级探测 | `hasattr(bpy.types.Action, "fcurves")` **在 4.5 上也是 False** | 同左 | 判据改查 `bl_rna.properties`（**4.5 = 有 / 5.1 = 无**） |

⚠️ **创作基线可以自选，但不能降级**：Blender 保存是单向的——用 5.1 存过的 `.blend`，4.5 **打不开**。
所以「用哪个版本的 GUI 调动作」要固定下来；两侧脚本都能跑，故换版本只需**重建一次母版**。

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
| FBX 版本 | 4.5 与 5.1 **导出都是 7400**；既有 Mixamo FBX 是 **7700**。Unity 两者都吃（5.1 的产物已实测导入 Unity 无告警，见证据 §三） |

### 7.3 五条踩过的坑（本管线实测）

1. **`use_current_action=False` 会摘掉正在驱动骨头的 action** ⇒ 烘出常量曲线（§四·1 步 2）。
2. **`rotation_mode` 被打回 `QUATERNION` 会让 euler 关键帧失效**（§三 的 V8 由来）。
3. **「两侧比对」型判据必须配非退化判据**（V8 / E0），否则源静止时全部平凡通过。
4. **`arm.edit_bones` 在 OBJECT 模式下是空的** ⇒ 在 OBJECT 模式里按 `edit_bones` 建骨骼集合并赋值，会得到一个
   **0 根骨**的集合而**不报错**（实测：`MIXAMORIG` 集合 0 根，被 V9 拦下）。
5. **`matrix_local` 的逐元素比对不是「Rest Pose 不变」的判据**：它是浮点噪声敏感量，同一份骨架跨版本
   （4.5 → 5.1）就从 9.2e-05 变到 1.22e-04、**越过 1e-4 阈值却什么都没变**。判据要取**骨端点坐标（mm）**。

### 7.4 轴向语义怎么测（§2.1.1 那张表的来源）

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --factory-startup --python-exit-code 1 `
  --python '\\wsl.localhost\Ubuntu-22.04\home\dog\game\code\tools\measure_xbot_control_axes.py' `
  -- --report '\\wsl.localhost\Ubuntu-22.04\home\dog\game\.scratch\control_axes.json'
```

| 口径 | 做法 | 为什么 |
|---|---|---|
| 绕**局部轴**转 | `pb.rotation_euler` 置 ±N°（默认 20°），只动一根控制骨 | 与"在 GUI 里按 X/Y/Z 锁轴旋转"同一件事 |
| **基准必须先归零** | 每量一个轴前 `reset_pose()`，**再**取基准点 | ⚠️ 否则基准会叠上一轴/上一根骨的残留——实测让左腿凭空多出 **170 mm** 侧向位移，差点把"左右不镜像"这个**错误**结论写进文档 |
| 量两处 | ① 本骨骨尖 ② **链末标志点**（腿=趾尖 · 臂=指尖 · 骨盆=头顶） | 只看本骨会漏掉**扭转**：局部 Y 是沿骨轴扭转，本骨骨尖在轴上、位移恒为 0 |
| 补**偏轴**标志点 | 骨盆看左手/中指尖 · 臂看中指尖 · 腿看趾尖 | 专治扭转不可见（骨盆扭转：头顶 1 mm，**中指尖 326 mm**） |
| 分解到身体坐标系 | 左腿方向 / 脚尖方向 / 髋→头 | 解剖定义，不猜世界轴 |

> ⚠️ **扭转的效果取决于下游是否偏轴**：直臂时上臂扭转对指尖位移为 **0**，但**肘一弯**，同样的扭转会把小臂大幅摆出去。表里的 "0 mm" 是**静止 T-pose 下**的读数，不是"这根轴没用"。

### 7.5 活体桥：让外部进程驱动**你正开着**那个会话

`code/tools/blender-bridge/`（与 [`unity-cli`](../../code/tools/unity-cli/README.md) 同一地位的项目自有直驱桥）。

| 方式 | 能做什么 | 缺什么 |
|---|---|---|
| `--background --python x.py` | 脚本化生成/导出，完全可复现 | 每次都是**新会话**：看不见你手改到一半的场景 |
| **活体桥** | 往**你眼前那个窗口**送代码并读回结果，你实时看见变化 | 需要 Blender 以本桥启动；窗口关了就没 |

```bash
./code/tools/blender-bridge/bb-launch.sh          # 起（自动处理 Z: / WSL IP / BB_STATE / 参数顺序）
./code/tools/blender-bridge/bb.py 'bpy.data.filepath'
./code/tools/blender-bridge/bb.py @my_probe.py    # 多行 exec，print 一并回传
```

**为什么 `bb-launch.sh` 不是可有可无的包装**：它替你做掉四件每一步都能踩空的事——
`net use Z:`（UNC 过 bash 双引号会被折掉 ⇒ Blender 静默回落默认场景）· 取 **WSL 网卡在 Windows 侧的 IP**
（默认 `127.0.0.1` 时 WSL 连不进来）· 状态文件写到仓库可见处（客户端靠它拿 host/port/token，不靠猜）·
把 addon 拷到 Windows 本地再 `--python`、且 **`.blend` 排在 `--python` 前面**。

### 7.6 边界与安全（活体桥）

1. **它执行任意 Python、无沙箱**——等于交出那个 Blender 进程的全部能力。门禁只有 **token**（启动时随机生成、写进状态文件）⇒ 状态文件别提交、别放共享盘（`.gitignore` 已排除）。
2. **默认只绑 `127.0.0.1`**；要从 WSL 连必须显式把 `BB_HOST` 设成 WSL 网卡 IP，**那之后同网段其他机器也能连**（有 token 就行）。用完关窗口。
3. **不是常驻服务**：Blender 一关桥就没了——这正是「活体」的含义，别拿它当自动化后端。
4. **为什么不用现成的 Blender MCP**：MCP 生态确实有（[harveyxiacn/blender-mcp](https://github.com/harveyxiacn/blender-mcp) · [Blender_mcp](https://github.com/Immunogenic-prismspectroscope589/Blender_mcp) · [blender-mcp-bridge](https://pypi.org/project/blender-mcp-bridge/) · [blender-agent](https://projects.blender.org/Rich-Siomporas/blender-agent)），DSH 也支持 MCP（`@deepseek-ai/dsh-mcp-client`，工具以 `mcp__<server>__<tool>` 出现）。不选它的理由具体：① 那类 MCP 的 Blender 侧内核也是监听 socket 的插件，本桥 120 行就覆盖了本工程要用的那一格；② 多一层第三方依赖（要装、跟版本、信任其代码；本机还没有 `uv`/`uvx`）；③ **MCP 工具只在新会话里出现**，「现在这个会话里帮我摆个姿势」它答不了；④ 本工程已有 [`unity-cli`](../../code/tools/unity-cli/README.md) 这个自建直驱先例。**若将来要接 MCP，本 addon 可直接当它的后端。**

## 七·B、动作素材：`BendGripChairBack`（弯腰、双手抓住椅背）

> 由 `code/tools/author_xbot_chair_grab.py` 产出（**脚本化、可复现**；母版里手改会在重建母版时丢失）。
> **2026-09-14 owner 目视三轮返工**：站位侧 → 肘朝向 → 手指侧弯 → 手没放在椅背上。
> 错误分类与硬规矩见 [Blender 侧错误分类](../engineering/blender%E9%94%99%E8%AF%AF%E5%88%86%E7%B1%BB.md)。
>
> ⚠️ **这一节只写 Blender 侧**。Unity 侧（导入 / Avatar / lab）按 owner 指示**暂缓**，等姿势目视通过再推。

### 结论与可达性（先读这段）

**站椅子正面抓不到靠背顶杆**——这不是手感问题，是几何：角色被坐板挡在离坐面中心 **0.522 m**
（胶囊半径 0.3117 + 坐面半深 0.21），而顶杆还在坐面**另一侧** 0.44 m，远超
**肩→手骨原点 0.562 m** 的可达域。⇒ 站位只能是**椅子后方**（靠背朝角色），
而"椅子放多远"由**可达性反解**得出（扫描：残差 ≈ 0 且肘角自然）：

| 弯腰 | 椅子中心距离 | 手残差 | 肘角 |
|---|---|---|---|
| 45° | 0.60 m | 0.0 mm | 143.7° |
| 45° | 0.66 m | 0.0 mm | 176.8°（几乎伸直） |
| **55°** | **0.70 m** | **0.0 mm** | **133.2°**（自然屈曲）← 采用 |
| 65° | 0.70 m | 0.0 mm | 105.2°（过屈） |

### 实测读数（2026-09-14，Blender 5.1.2 · **判据一律对着产物几何**）

椅子几何由 **一个** 布局函数同时产出代理与抓握目标（`chair_layout()`）：
坐面中心 `y=-0.70` · **靠背中心面 `y=-0.47`（朝角色那一侧）** · 靠背包围盒 `y∈[-0.49,-0.45]` · 顶杆 `z=0.7949`。

| 帧 | 弯腰 | 腕↔靠背面 | 腕高于顶杆 | 指尖扣住 | 肘角 | 肘 后/下/侧 (mm) | 脚漂移 |
|---|---|---|---|---|---|---|---|
| 1 | 0° | 525.5 mm | 645.7 mm | —（未蜷） | 180.0° | 0 / 0 / 0 | 0.0 mm |
| 21 | 30° | 63.6 mm | 132.1 mm | —（未蜷） | 180.0° | 0 / 0 / 0 | 0.0 mm |
| 31 | 45° | 13.4 mm | 58.7 mm | —（未蜷） | 180.0° | 0 / 0 / 0 | 0.0 mm |
| 37 | 50° | 5.0 mm | 45.0 mm | **True** | 152.7° | **56 / 34 / 11** | 0.0 mm |
| **41** | **55°** | **5.0 mm** | 45.0 mm | **True** | **131.9°** | **95 / 56 / 32** | **0.0 mm** |
| 61 | 55° | 5.0 mm | 45.0 mm | **True** | 131.9° | 95 / 56 / 32 | 0.0 mm |

到位帧（41）几何：左腕 `(0.170, -0.465, 0.840)` · **左中指尖 `(0.173, -0.511, 0.755)`**
⇒ `y=-0.511` **越过靠背远侧面（-0.49）**、`z=0.755` **低于顶面（0.7949）** ⇒ **手指绕过顶杆扣住**。
**肘向后 95 mm / 向下 56 mm / 体侧仅 32 mm** ⇒ 肘往**后**折（不是往外顶）。

- **指尖扣住** 只在**手指已蜷**的帧上判（手指伸直时指尖本来就越过顶杆 ⇒ 不设门槛会给假读数）。
- **肘判据只用无歧义轴**：世界 +Y（角色不转身 ⇒ 恒为背向）与**由骨盆骨定义的体侧轴**；
  ⚠️ 不要用脊柱轴当"前后轴"——弯腰后脊柱指**前上方**，会把正确的后折判成"反关节"（本轮踩过，见错误分类 A3）。

### 手臂/腿：**解析二骨解**，不是 Blender IK

`CTRL_*ForeArm` / `CTRL_*Leg` 上**不挂 IK**。原因：极点到关节平面的映射**不由我控制**——
实测"把极点摆在背侧"仍解出**肘向前顶 109 mm**（反关节），8 个 `pole_angle` 里最好的一个背侧分量只有 10 mm。
⇒ 改为**把中间关节的位置当输入**（肘沿身体背侧、膝朝前），解析反解两骨朝向；关节落点当场核对
（`mid_err_mm` / `tip_err_mm`，实测 **0.0 mm**）。

⚠️ 写朝向时 basis 必须按**变形骨**那侧父链解、再写到控制骨上：
`COPY_ROTATION(LOCAL↔LOCAL)` 复制的是**局部**旋转，而 `CTRL_Arm` 的父级是 `CTRL_Hips`、
`mixamorig:Arm` 的父级是 `mixamorig:Shoulder` ⇒ 两侧差一个**共轭**（本轮踩过，见错误分类 D2）。

### 手指怎么扣的（母版没有手指控制骨）

13 根控制骨里没有手指 ⇒ **直接在手指变形骨上打键**（导出烘焙覆盖全部变形骨，故能带出去）。
蜷曲轴由脚本自测，**整只手只选一次**（取中指），拇指单列；评分带**侧向惩罚**：

| 手 | 四指 | 朝掌心 | 侧向 | 拇指 |
|---|---|---|---|---|
| 左 | X+1 | 625.3 mm（四指合计） | **1.4 mm** | X+1（94.6 / 26.2 mm） |
| 右 | X−1 | 624.7 mm | **1.4 mm** | X+1（94.4 / 26.3 mm） |

⚠️ 两处坑：① 只用"朝掌心最大"挑轴 ⇒ 会选到**侧弯**（实测朝掌心 58 mm 而**侧向 95 mm**）；
② **逐指各自选轴** ⇒ 同一只手选出**相反符号**（Index/Middle/Ring 取 X−1 而 Pinky 取 X+1）。
（错误分类 A4 / B2）

### ⚠️ 本轮错误清单（12 处，全部有实测读数）

**判据类 5**：A1 自证式判据（残差 0 而手离椅背 440 mm）· A2 目标函数方向反（"向外+向后之和"鼓励肘外张）·
A3 轴名错配（脊柱轴当前后轴 ⇒ 正确姿势被判反关节）· A4 单目标漏惩罚（指纹选到侧弯）· A5 门槛缺失（未蜷也判"扣住"）；
**污染类 2**：B1 基准未归零（左腿凭空 170 mm）· B2 逐指独立自测（同手反号）；
**静默失败 2**：C1 打不开文件回落默认场景 · C2 `actions.new()` 重名建 `.001`（导出结果逐位不变）；
**约定 2**：D1 `pose.location` 单位是 cm · D2 `COPY_ROTATION` 两侧父链不同 ⇒ 差共轭；
**导出语义 2**：E1 bind pose 取当前帧姿势（E5 报 86 m）· E2 生成物不可逐字节复现；
**补丁纪律 3**：F1 切片误删函数 · F2 补丁后不跑就宣布完成 · F3 断言写错。

## 八、未闭合（诚实清单）

1. **Unity 侧骨盆读数低于 Blender 侧**（16.94 mm vs 40.0 mm）——量的是两个不同的量（§5.4·1）。
   本条的验收面是"探针覆盖骨盆控制"，已由**母版侧 V8（42.05 mm）** 与 **回导保真 E6（0.0014 mm）**
   成立；Unity 侧只主张"趋势与峰值帧一致"。
2. **基线是 Blender 5.1.2**（2026-09-14 由 4.5.13 切换，见[双版本证据](../engineering/evidence/blender-pipeline-dual-version-2026-09-14.md) §八）；
   4.5.13 作为**兼容分支**曾全链验过（V1–V9 + E0–E6 全绿、产物内容等价 0.000967 mm），但本机**不再保留其便携包**，
   故 4.5 分支此后**不再有本机回归**。FBX 版本差异（导出 7400 vs 既有 Mixamo 7700）**未做 Unity 侧兼容性专项验证**，
   只验了"本机 Unity 6000.5.2f1 能吃"。
3. **未做完整 Editor 重启后的复现**：幂等与确定性读数是在同一 Editor 会话内实测的。
   ⚠️ 另：**GUI 已能自动打开**（§7.1），但"骨骼集合好不好用、控制骨点得到点不到"这一层**只能目视**——
   agent 无图像输入，故 §二 的 GUI 行只主张"显示层已落盘（V9）"，不主张手感。
4. ~~危险点表未登记本条的三条坑~~ → **✅ 2026-09-14 已登记**（#156 关闭后按 owner 指示补：§三 1 行 / §四 3 行 / §七 2 行 + 扩写 1 行）。
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
| Rest Pose **端点坐标**容差 | — | `0.5` mm | 同上 `E5_TOL_MM` |
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
*创建: 2026-09-14 | 更新: 2026-09-14（🔧 第六次：**新增 §7·B 动作素材 `BendGripChairBack`**（弯腰双手抓椅背）——脚本化产出 `code/tools/author_xbot_chair_grab.py`（临时 IK 解 + 捕获成控制骨角度），实测抓点残差 **0.0 mm**、肘 133°、逐帧脚漂移 **0.0 mm**、手指自测蜷曲轴 Z/−1；导出与 Unity 导入全绿。**并挖出三个真 bug**：FBX 导出的 bind pose 取当前帧姿势（E5 报 86 m，探针一直裸奔侥幸过）· `pose_position=REST` 是错误修法（压成常量）· `actions.new()` 重名静默建 `.001`。⚠️ 本动作**未登记动作词条**（词表受控，属设计裁定）。🔧 第五次：**新增 §7.5 活体桥 + §7.6 边界与安全**——落库 `code/tools/blender-bridge/`（`blender_ai_bridge.py` + `bb.py` + `bb-launch.sh` + README），实测驱动已开着的窗口：摆 `CTRL_LeftArm` Z+40° → 左手位移 **384.2 mm**，并读回 13 根控制骨与两组集合；含「为什么不用现成 Blender MCP」的四条具体理由。🔧 第四次：**新增 §2.1 GUI 操作手册**（打开方式 · 六步动作序列 · 两条红线）+ **§2.1.1 逐根控制骨的实测轴向语义表**（13 根 × 3 轴，链末标志点位移）+ **§2.1.2 符号规则**（实测：腿左右同轴、臂左右镜像 ⇒ 不能整套取负号）+ §2.1.3 三个自查。测量脚本口径见 §7.4。🔧 第三次：**验证基线由 4.5.13 LTS 切换为 Blender 5.1.2**——入库探针 FBX 由 5.1.2 重建（与 4.5 产物内容等价 **0.000967 mm**）、Unity 侧重跑全量断言转绿；4.5 分支保留在取道层但本机不再保留便携包。🔧 第二次：**移植为 Blender 4.5 / 5.x 双兼容**（新增取道层 `code/tools/blender_action_compat.py`：slotted actions 曲线取道 · `action_slot` 指派 · 姿态骨选择位）+ **母版 GUI 可用性**（骨骼集合 `CTRL`/`MIXAMORIG` + 配色，V9 自检；已复核导出物内容等价 **0.000000 mm**）+ 新增 §4.4「导出物不可逐字节复现」与 §7.1 双版本差异表；E5 判据由矩阵元素改为骨端点坐标）*
*状态: 与 [动画处理能力对照实验](%E5%8A%A8%E7%94%BB%E5%A4%84%E7%90%86%E8%83%BD%E5%8A%9B%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C.md) 同为**两条线共用的口径正典**；本文只覆盖 Blender 线。*
*关联: [动画处理能力对照实验](%E5%8A%A8%E7%94%BB%E5%A4%84%E7%90%86%E8%83%BD%E5%8A%9B%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C.md), [动作库规格](%E5%8A%A8%E4%BD%9C%E5%BA%93%E8%A7%84%E6%A0%BC.md), [code/unity/README.md](../../code/unity/README.md), [危险点表](../engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md)*
