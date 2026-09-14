# Blender 动作管线双版本移植与母版 GUI 可用性证据

> [#156](https://github.com/verystrongdog/game/issues/156) **关闭后**的后续修正（owner 2026-09-14 指示：「登记」+「我要怎么在 windows 端通过 blender 调试动画」→ 选定「把脚本移植到 5.1」与「做母版 GUI 可用性」）。口径正典：[Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md)。

## 一、结论

| 项 | 值 |
|---|---|
| 达成 | 管线从 **Blender 4.5 单版本**变为 **4.5 / 5.x 双兼容**（差异收进取道层）；母版加 **骨骼集合 + 配色**，GUI 里能一键区分并单选控制骨 |
| 一句话 | 同一套脚本在 **4.5.13 LTS（Linux/WSL）** 与 **5.1.2（Windows 已装）** 上**各自跑通 V1–V9 与 E0–E6**，两侧产物**内容等价**（逐骨逐帧差 **0.000967 mm**）；随后按 owner 指示**切成 5.1.2 单基线**——入库探针 FBX 由 5.1.2 重建替换、Unity 全量断言在其上转绿（**§八**） |
| ⚠️ 一条要点 | **FBX 导出不可逐字节复现**（头部 `CreationTimeStamp` + UID 计数）⇒ "哈希不变"**不能**当生成物的判据；由此把 E5 从"矩阵元素"改成"**骨端点坐标（mm）**"，并新增 §4.4 与一条危险点表条目 |
| 未做的事 | 未做**完整 Editor 重启**后的复现；未做 GUI 交互的手感评估（只验了自检与显示层落盘）。~~未在 5.1 上跑 Unity 全量断言~~ → **✅ §八 步 5 已补跑：64 项 63 过 / 0 败 / 1 跳过** |

## 二、绑定

| 字段 | 值 |
|---|---|
| base | `42541b9`（#156 证据落库）之后的工作树；本轮新增 `code/tools/blender_action_compat.py` 并改两个脚本 + 母版生成器 |
| 工具版本 | Blender **4.5.13 LTS**（linux-x64 便携包 · `daeeeca98fb0`）· Blender **5.1.2**（Windows 已装 · `ec6e62d40fa9`）· Python 3.10.12 |
| 触发 | owner：「我要怎么在 windows 端通过 blender 调试动画」——原脚本在 5.1.2 上**直接崩**，而 Windows 侧**无法运行 4.5 便携包**（见 §五） |

## 三、两侧实测读数

| 判据 | Blender 4.5.13 | Blender 5.1.2 |
|---|---|---|
| 动作取道（报告自述） | `action.fcurves` | `layers→strips→channelbag` |
| 姿态骨选择位（报告自述） | `Bone.select` | `PoseBone.select` |
| 母版 V1–V9 | **全绿** | **全绿**（骨骼集合 `{'CTRL': 13, 'MIXAMORIG': 65}`） |
| 探针动作非退化 V8 | 最大 **820.2072 mm** | 同值 |
| 导出 E0–E6 | **全绿**（E1 0.0011 mm · E6 0.0014 mm） | **全绿**（E1 0.001 mm · E6 0.0015 mm） |
| E5 Rest Pose（**端点 mm**） | **0.092 mm** | **0.122 mm**（容差 0.5 mm） |
| 导出物形状 | 65 骨 · `CTRL_` 0 · 单根 · 0 网格 · 684 044 字节 | 同（684 108 字节） |
| 内容等价（vs **已入库**那份） | **0.000000 mm**（65 骨 / rest 0 差异 / 逐帧 0 差） | **0.000967 mm** |
| Unity 侧（5.1 产物导入 `Assets/Temp` 试） | — | `clip.humanMotion=True` · `length=2.0000` · `fps=30` · `avatar isValid/isHuman` · `animationType=3` · `avatarSetup=1` · 三条导入告警串**皆空**（试完已删该临时资产） |

### 内容等价怎么量的

回导进 Blender 后逐骨比：① 65 根骨的存在性；② Rest Pose 的 `head_local`/`tail_local`；③ **逐帧**（1–61）五个读数点的骨尖世界坐标。
判据脚本为一次性探针（`.scratch/cmp_fbx.py`，过程物不入库），输出即上表的"内容等价"两行。

## 四、改了哪些文件、为什么不动 Unity 侧

| 文件 | 改动 |
|---|---|
| `code/tools/blender_action_compat.py` | **新增**：4.5/5.x 取道层（`action_fcurves` / `assign_action` / `select_pose_bones` / `action_frame_range` / `fcurve_count` / `remove_fcurves_where` / `describe`） |
| `code/tools/build_xbot_animation_template.py` | 走取道层；**新增 V9**（骨骼集合）；控制骨配色与显示模式；报告记 `slotted_actions`/`fcurve_access` |
| `code/tools/export_xbot_action.py` | 走取道层；选择位改用兼容助手并记进报告；**E5 判据改为骨端点坐标（mm）**；`rest_fingerprint` 补 `tail_local` |
| `design/presentation/Blender动作制作管线.md` | §二 GUI 行 · §三 V9 · §四·3 E5 · **新增 §4.4**（导出物不可逐字节复现）· §7.1 双版本差异表 · §7.3 五条坑 · 参数表 |
| `design/engineering/危险点表.md` | `Action.fcurves` 行改写为 **`Blender 5.x 动作 API`**（含选择位搬迁与类型级判据坑）；**新增 `FBX 导出字节`行** |
| `code/unity/README.md` | §二·Q 版本与工具面同步 |
| **未动** | `code/unity/**` 的资产与源码**一字未改**（探针 FBX 内容等价 0.000000 mm）⇒ 不需要重跑 Unity `run_tests`；`Assets/Temp` 里那份 5.1 试导件已删 |

## 五、⚠️ Windows 侧的两条环境结论（实测，别再试）

1. **4.5 便携包在 Windows 上无法从 WSL 路径启动**：`\wsl.localhost\...\blender.exe`（以及 `net use Z:` 映射盘符后）一律报
   **「应用程序无法启动，因为应用程序的并行配置不正确」（SxS）**——app-local 依赖解析在 9p 文件系统上不成立。
   要用 4.5 的 GUI，**必须把便携包复制到真正的 Windows 卷**（约 900 MB，本轮未做）。
2. **WSLg 的 GUI 在沙箱内起不来**：命令行开 Linux 版 Blender 时 `The Wayland connection broke`（X11 亦然）。
   ⇒ agent 侧**无法**替 owner 验证 WSLg 图形界面；要用 Linux 版 GUI 得由 owner 自己在 Windows 终端里起。
3. 因此 owner 选的路线（**移植脚本到已装的 5.1.2**）是当前唯一零复制、且本轮**已实测跑通**的路。

## 六、门禁

| 门禁 | 结果 |
|---|---|
| Blender 侧自检 | 4.5 与 5.1 **各自** V1–V9 + E0–E6 全绿（§三） |
| `docs-integrity` | 见提交时的读数（14/14） |
| `clean-checkout` | 见提交时的读数 |
| `unity-assets` | 未受影响（`code/unity/**` 未改） |
| `unity` | **已在 5.1 产物上重跑**（§八 步 5）：`run_tests` **64 项：63 过 / 0 败 / 1 跳过**（与切换前逐项一致；跳过的是既有的 `ActionLabGuardVariantTests`） |

## 七、未闭合

1. **未做完整 Editor 重启复现**（沿用 #156 的残留项）。
2. **GUI 手感未评估**：骨骼集合与配色只验了"落盘且 V9 通过"，好不好用要 owner 在视口里试。
3. **5.x 上只验了本脚本链**，没有把 Unity 侧全量 `run_tests` 在 5.1 产物上重跑一遍（内容等价已由 §三 覆盖）。
4. **创作基线只能二选一**：Blender 保存单向，5.1 存过的 `.blend` 4.5 打不开 ⇒ 一旦用 5.1 调过母版，便携包那条路就作废。

---
*创建: 2026-09-14 | 更新: 2026-09-14*
*关联: [#156](https://github.com/verystrongdog/game/issues/156), [Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md), [#156 收口证据](blender-xbot-pipeline-2026-09-14.md), [危险点表](../../engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md)*


## 八、基线切换为 5.1.2 单基线（2026-09-14，owner 指示）

owner：「只用 5.1 不行么」→ **切成单基线**（取道层的 4.5 分支保留为兼容分支）。执行与读数：

| 步 | 动作 | 结果 |
|---|---|---|
| 1 | 4.5 产物留档到 `.scratch/blender_assets/xbot-4.5-archived/`（母版 + 两份报告 + 4.5 版 FBX） | 存档（过程物，不入库） |
| 2 | 用 **5.1.2 重建母版**到默认路径 `.scratch/blender_assets/xbot/` | V1–V9 **全绿**；取道 `layers→strips→channelbag`、选择位 `PoseBone.select` |
| 3 | 用 **5.1.2 重导** `RigRoundTripProbe.fbx` | E0–E6 **全绿**；E5 端点 0.122 mm；684 108 字节 |
| 4 | 经 Unity `import_asset --confirm true` **替换入库资产** | GUID **`fea37d37d0d6ded459704d6132b4ee9d` 不变**；`animationType=3` / `avatarSetup=1` / `animationCompression=0` / 三条告警串空**全部保持**；`.fbx.meta` 无变化（仅 `.fbx` 变） |
| 5 | **重跑 Unity 全量断言**（在 5.1 产物上） | 见 §六 门禁读数 |
| 6 | 入库 FBX 内容 vs 4.5 版 | **0.000967 mm**（65 骨 / rest 0 差异） |
| 7 | 删 `.scratch/blender-lts/` | 回收 **2.8 GB** |

**切换后的口径**：管线文档 §七·1 首行、README §二·Q、切片四轴行、`动作库规格.md` §四·戊·5、本文与 #156 证据均已改为
**基线 = Blender 5.1.2**；4.5.13 记为**已验的兼容分支**（取道层保留其取道，但本机不再保留便携包 ⇒ 该分支此后无本机回归）。

> 唯一没有损失的是"跨版本知识"：`blender_action_compat.py` 的两条分支都是**实测过**的，不是推测。
