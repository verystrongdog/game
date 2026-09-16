# 恐慌姿态证据（抱头 / 捂耳 · 第四系「目标部位局部系」首件）

> [#169](https://github.com/verystrongdog/game/issues/169) 的收口证据（口径 §15.7 **① 件**）。
> 口径权威 = [动作描述口径](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) §十五 / §15.6.1（部位面登记）· §13.4 / §13.4.1（判据形态与时域）· §15.8（多实例 lab）；
> 部位面 ε 来自 [#168](https://github.com/verystrongdog/game/issues/168)（[证据](body-part-epsilon-2026-09-16.md)）。必填字段按 [阶段证据说明](README.md) 与 [WORKFLOW.md §五/§六](../../../WORKFLOW.md) 记录。

## 一、结论（先读这一段）

| 项 | 值 |
|---|---|
| 达成 | 能力增量：`身体分区与四系（部位索引件）` · Implementation `NONE → PARTIAL` · Integration `ISOLATED → CONNECTED`；`多实例呈现 lab（三件同屏）` · Implementation `NONE → PARTIAL` |
| 一句话 | **第四系第一次被真实动作消费**：`--task panic` 产出一条 **46 帧**的恐慌姿态（捂耳），判据面全部落在**自身头部的具名面**上——**掌面 ↔ 耳侧面 0.80 mm**（到位帧）· 保持期内最坏 **1.97 mm**（容差 2.8）· **非退化对照 622.44 mm**（同一条判据在中立姿势下报红）· 逐指解 5 指全在头外（+0.6 ~ +2.9 mm）· 手/指**蒙皮零穿透**（+0.34 mm）· 时序 **13 == 13** · 接地无支撑帧 **0** |
| **本条最该带走的两条** | ① **ε 可被消费**：脚本每次运行都把 §15.6.1 登记的 ε 与**真实面片**复核——四处**逐值相同**（88.0429 / 88.0429 / 99.72 / 207.4887 mm）⇒ 登记表不是散文。② **判据的度量对象必须与措辞同层**：拿**骨段点**当"手不陷入头"的判据时，皮肤刚贴住就报 **−4.21 mm 假红**（骨的采样点在**肉里**，离皮肤 ≈10 mm；同族：口径 §15.3 脚的 **41 mm 层差**）⇒ 改成**手/指蒙皮**后为 **+0.34 mm** |
| 假设判定 | **支持**（见 §五）：自身部位的具名面**能**由该部位当前 transform 实时求得并承载**能报红**的判据；②③ 可直接复用本条的**部位面件**与 **lab 装配器** |
| 未做的事 | **owner 目视未做**（第 8 条验收，不以机械全绿代替）· 朝向档角度 ε 仍走 §8.3（U2′）· **抱头那一解判不上**（见 §4.4 的如实登记） |

## 二、绑定

| 字段 | 值 |
|---|---|
| base SHA | `d632baa`（#168 收口后的 HEAD） |
| head SHA | 本条**提交组**：`8dcc868`（宿主 6 + lab 装配器）· `6a8eea4`（证据 + 口径/切片回填）· 本行所在提交（回滚演练记录 + head SHA） |
| 阶段 | [#169](https://github.com/verystrongdog/game/issues/169)（Experiment） |
| 执行者 | DSH agent（本机 WSL → Windows 侧 Blender） |
| 工具版本 | Blender **5.1.2**（`hash ec6e62d40fa9`）· Windows 11 家庭中文版 |
| 被测对象 | 母版副本 `.scratch/panic/panic_clip.blend`（由 `.scratch/blender_assets/xbot/XBot_AnimationTemplate.blend` 逐字节拷贝而来，`5601197` 字节）· 骨架 `Armature`（78 骨 = 65 变形 + 13 控制）· 蒙皮网格 `Beta_Joints`(10514 v) / `Beta_Surface`(14232 v) |
| ⚠️ 母版的地位 | 生成物、不可逐字节复现（[管线 §4.4](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md)）⇒ 只作留痕；**原件字节未被触碰**（所有写回都发生在 `.scratch/panic/` 的副本上） |

## 三、命令与退出码

```powershell
# 一条命令产一条 clip（写回的是母版**副本**，不是母版）
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --factory-startup `
  --python-exit-code 1 --python 'Z:\home\dog\game\code\tools\author_xbot_chair_grab.py' -- `
  --task panic --template 'Z:\home\dog\game\.scratch\panic\panic_clip.blend' `
  --report 'Z:\home\dog\game\.scratch\panic\panic_report_6.json'

# 身体条件解空间（口径 §4.2 硬规矩 5）
#   … --task panic --no-save --scan-body
# 多实例 lab（单实例真跑 / 三实例自测；**从不写回**）
#   … --python code/tools/lab_multi_instance.py -- --template <.blend> --instances "0:PanicCoverEars" …
#   … --python code/tools/lab_multi_instance.py -- --template <.blend> "--instances=-5:PanicCoverEars,0:PanicCoverEars,5:PanicCoverEars" …
```

| 命令 | 退出码 |
|---|---|
| `--task panic`（捂耳 clip，run6） | **0**（`problems: []`） |
| `--task panic`（同一条再跑一遍，run7） | **0** |
| `--task panic --pose head`（抱头解，作对照解） | **1** —— `掌面最低点落在面片之外的帧`（**如实判不上**，见 §4.4） |
| `--task panic --no-save --scan-body` | **0** |
| `lab_multi_instance.py`（1 实例） | **0** |
| `lab_multi_instance.py`（3 实例自测） | **0**（间距 5.0 / 5.0 m · 逐实例可见骨 52 / 非例外越界 0） |
| `python3 code/tools/validate_cross_refs.py` | **0**（0 死链 / 0 段引用警告） |
| `python3 code/tools/validate_trash_isolation.py` | **0** |
| `python3 code/tools/validate_params.py` | **0**（0 failed / 7 warnings，与改前逐条相同） |
| `python3 code/tools/validate_grip_cards.py` | **0**（8/8） |
| `python3 code/tools/run_all_checks.py` | **0**（16/16） |
| `dotnet test` | 未跑——本次**未改 `code/src/`**（先例 #165/#167 同记法） |

## 四、读数

### 4.1 部位面自检：**§15.6.1 登记的 ε 与真实面片逐值一致**（"能不能被消费"变成读数）

脚本每次运行都对四个面复核（面片 = 沿该面局部轴最外的 `PANIC_SLAB_M = 8 mm` 一层真实蒙皮顶点）：

| 面 | 骨局部轴 | §15.6.1 登记 ε | **真实面片复核** | 一致 | 面片顶点数 |
|---|---|---|---|---|---|
| 左耳侧面 | `+X` | 88.0429 mm | **88.0429 mm** | ✅ | 62 |
| 右耳侧面 | `−X` | 88.0429 mm | **88.0429 mm** | ✅ | 62 |
| 后脑面 | `−Z` | 99.72 mm | **99.72 mm** | ✅ | 12 |
| 头顶面 | `+Y` | 207.4887 mm | **207.4887 mm** | ✅ | 9 |

⚠️ **锚点的定义改过一次（如实登记）**：第一版把锚点写成"骨原点 + ε·法向"，它在**面内**的位置等于**骨原点**的位置——而后脑的最外点高出骨原点 **48–118 mm** ⇒ 锚点落在面片**下方 80 mm**，"最低点是否落在面片内"的判读整个错位。现改为**沿该轴最外的那个真实蒙皮顶点**（ε 逐值不变——它就是那个顶点的沿轴投影）。

### 4.2 主判据：掌面 ↔ 自身头部具名面（**弧面↔面**，口径 §13.4 甲 · U8 已闭合）

| 阶段 | 读数 | 容差 |
|---|---|---|
| 到位帧（13）| **0.80 mm**（左）· **0.80 mm**（右） | `tol_contact = 2.8 mm`（§8.2） |
| 保持期（13–46，**逐帧**）| 最坏 **1.97 mm**（松一帧即红的规律下**全绿**） | 同上 |
| 非退化对照（**中立姿势**，同一条判据）| **622.44 / 622.43 mm** ⇒ 判据**能报红** | 同上 |
| 面内判读 | 到位帧起**始终落在面片内**（`面内 True`） | #164：**面外不许判贴合** |
| 掌面法向 ↔ 面法向 | **180.00°**（掌面正对头侧） | 朝向档未测 ⇒ **只报读数**（§8.3） |

**面↔面顶点最近距离**（只报读数、**不判红**）：最坏 5.61 mm。⚠️ 它**不是**判据：两个点集的最小**顶点**距离有**网格分辨力下限**（≈ 顶点间距，本件的下限量级 2.7 mm）⇒ 拿它当"贴合"判据就是"用地磅称一封信"（§8.2 的同一道理）。

### 4.3 逐指手型（F10）· 两条解并列（口径 §4.2 硬规矩 5）

**逐指解 vs 四指共用一个系数**（口径 §13.8 前史：那就是 [#164](https://github.com/verystrongdog/game/issues/164) 实测过的错法）——本件把那条教训**复现成读数**：

| 手 | 手型 | Index | Middle | Ring | Pinky | Thumb |
|---|---|---|---|---|---|---|
| 左 | **逐指解** ✅ | +2.4 | +1.5 | +1.4 | +2.2 | +2.1 |
| 左 | 四指共用（对照） | +2.4 | +2.7 | **−1.0** | +0.6 | +2.1 |
| 右 | **逐指解** ✅ | +2.9 | +2.3 | +1.7 | +0.6 | +1.0 |
| 右 | 四指共用（对照） | +2.9 | +2.7 | +1.4 | +0.6 | +1.0 |

（单位 mm，**带符号**：正 = 在头外。⇒ 共用系数让**无名指陷进头里 1.0 mm**，而逐指解五指全在头外。）

**身体条件的解空间**（`--scan-body`，3 下蹲 × 3 抬肘 = 9 行）：**接触读数在 9 行里逐值相同**——因为目标面**跟着身体走**（第四系的锚点由该部位当前 transform 实时求得）⇒ **身体条件的取舍是观感（owner）**，判据面给不出区分；**肘方向的取舍有读数**（肘侧向 **−3.0 / 163.3 / 218.9 mm**，抬肘 −15/0/+15°）。⇒ 两行的性质**不同**，如实登记，不假装"9 解都可行"。

### 4.4 两解并列与抱头那一解的**如实判不上**

| 解 | 面 | 到位帧间隙 | 面内 | 判定 |
|---|---|---|---|---|
| **捂耳**（`PanicCoverEars`，进 clip） | 左/右耳侧面 | **0.80 / 0.80 mm** | ✅ True | **通过** |
| 抱头（`PanicHoldHead`，只报读数） | 后脑面 | 0.80 / 0.80 mm | ❌ **False** | **判不上** |

**抱头为什么判不上**：掌面最低点落在后脑面片之外——面片横向跨度只有 ±35.3 mm（**面片仅 12 个顶点**），而掌面最低点在 **+49.3 mm** 处（掌面是近平面、头是球面 ⇒ 倾斜时最低点落在**掌缘**）。按 §13.4/#164 的"**面外不许判贴合**"⇒ 本条**不判它通过**，也不为它调参（调面片厚度或对齐目标就等于**倒填**）。
⚠️ 这暴露一条**真实缺口**（留给 ②③）：**"具名面的横向范围"目前只用"最外片层的顶点跨度"定义，而它受网格分辨率限制**（后脑 12 顶点 ⇒ 跨度小、容易判"面外"）。⇒ 见 §八 未闭合 2。

### 4.5 其余判据（全部产物侧；`evaluated_get(depsgraph)` 上取）

| 判据 | 读数 | 来源 |
|---|---|---|
| **零穿透**（手/指**蒙皮** ↔ 头部蒙皮面，带符号） | 最坏 **+0.34 mm**（**全段无穿透**） | 动作库规格 §四·戊·5 判据 4；阈值取 §8.2 `tol_contact` 的**对称用法**（同宿主 5 的 `support_penetration`） |
| 同上（**骨段点**，仅读数） | 最坏 **+34.17 mm** | ⚠️ **不能当判据**：第一版拿骨段点判 ⇒ 皮肤刚贴住就报 **−4.21 mm 假红**（骨在**肉里**，离皮肤 ≈10 mm） |
| **时序（V-f，一次性）** | 声明到位帧 **13** == 产物极值帧 **13** ✅ | 判据量 = 两手"掌面最低点 ↔ 部位面"沿法向间隙取大的曲线最低点 |
| **接地（M2，持续）** | 无支撑帧 **0** / 46 帧 · 最坏陷入 **0.01 mm** | `soleMargin = 2.8 mm`（取自已入库件 `xbot_contact_phase.SOLE_MARGIN_MM`） |
| 预览可见性 | **52** 根可见骨 · **非例外越界 0** | 65 变形骨 − 13 标记骨；判据 `visible_bone_outliers`（#166 第 3 轮建） |
| 通道完整 | **58** 个通道（含**手指 40** · **腿脚 6**） | ⚠️ 宿主 3 漏打腿脚的教训（#165）⇒ 逐项列全并打印 |

第一版的**两处假红**（都已改，如实登记）：① 拿 **AABB 盒**当头部代理 ⇒ 脖子整段落在盒里，"手在耳侧"被读成**骨段陷入 −38.94 mm**（35 帧假红）⇒ 改用**蒙皮顶点法向**的带符号参照；② 拿**骨段点**判穿透（见上）。

### 4.6 多实例 lab（口径 §15.8）

| 运行 | 实例 | 结果 |
|---|---|---|
| **真跑**（本条落的第 1 个实例） | `0:PanicCoverEars` | 可见骨 **52** · 非例外越界 **0** · `problems []` · 退出码 **0** |
| **三实例自测** | `−5 / 0 / +5 m`（同一动作三份） | 逐实例可见骨 **52** / 越界 **0** · 间距实测 **5.0 / 5.0 m** · 静态包围盒**无重叠** · 退出码 **0** |

形态与四条硬规矩逐条对上（§15.8）：① lab **不是导出源** ⇒ 脚本**从不写回**任何文件；② lab **只做呈现** ⇒ 实例只整体平移，**不重算任何判据**；③ 指派 action 走**取道层** `assign_action()`（5.x 要设 `action_slot`）；④ **逐实例**跑可见性收敛。
⚠️ **两处实测坑**（都已修，并值得进[危险点表](../%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md) §四）：
① `visible_bone_outliers` 按**名字**取皮肤 ⇒ 复制后实例的网格叫 `Beta_Surface.001`，判据拿到的是**原实例**的皮肤 ⇒ 报出"51 根骨伸出 **5000 mm**"的假红（= 实例间距）。⇒ 函数加 `meshes=` 参数，把**该实例自己的网格**传进去。
② 蒙皮网格的 Armature 修改器**必须改指到新骨架**，否则一套皮肤被两套骨架同时驱动。
③ `--instances "-5:…"` 会被 argparse 当成选项 ⇒ 用 `--instances=…`（本件踩到，已记在脚本用法里）。

### 4.7 重跑一致性与回归

| 比对 | 结果 |
|---|---|
| 同一份母版副本 `--task panic` **两遍独立进程** | 可比数值 **2387** 个，逐值相同 **2381** 个；**6 个差 ≤ 0.01 mm** |
| 那 6 个差异的来源（已定位，不是随机） | ① 逐指蜷曲量的**离散档**在近简并处翻了一档（2.85 ↔ 2.84，步长 0.1 档 ≈ 0.01 mm 间隙）；② 掌面最低点的 `argmin` 在近平面掌面上取到了相邻的**等价顶点**（面内偏移 0.01 mm 抖动）。**判据量（沿法向间隙 / 时序帧 / 穿透 / 接地）逐值相同** |
| 手部三件工具回归 | `measure_xbot_surface_offset.py`（#168）、`xbot_contact_phase.py`、`validate_grip_cards.py` 本次**未改**且全绿 |
| 既有四个宿主 | `chair` / `card1` / `door` / `restate` 的**代码路径未改**（只在同文件里新增宿主 6 与库层件）；`--task` 的 `choices` 与 dispatch 两处同步登记 |

## 五、判定标准（三种结局的评估）

| 结局 | 是否命中 | 依据 |
|---|---|---|
| **支持** | ✅ | ① 件在第四系上有**可报红的「面」判据**（掌面 ↔ 耳侧面 0.80 / 保持期 1.97 mm，对照 622.44 mm）；② **②③ 能直接复用**本条登记的**部位面件**（`head_part_frame` / `head_face_patch_local` / `head_signed_mm`）与 **lab 装配器**（`PART_SETS` 加一行 = 加一个部位；`--instances` 加一项 = 加一个实例），**不重开会话形态** |
| 否定 | ✗ | 第四系**表达力足够**：面朝向在整段里稳定（掌面法向夹角恒 **180.00°**，无逐帧跳变），ε 双侧成立（左 88.0429 / 右 88.0429，逐值相同）。⚠️ **但有一条被否掉的东西**：**"面片的横向范围"用顶点跨度定义**在**后脑**这种低分辨率的面上会**误判面外**（抱头解）⇒ 见 §八 未闭合 2，**不属"第四系表达不了"**（耳侧那两格工作正常） |
| 证据不足 | ✗ | 交的不是静帧：**46 帧逐帧**读数（`F4a` 窗口 13–46 逐帧）+ lab **逐实例收敛**（52 / 0）都做了 |

## 六、owner 目视（**未做——本条的验收第 8 条**）

静帧已就绪（`.scratch/panic/stills/`，过程物不入库）：

| 文件 | 内容 |
|---|---|
| `panic_f01_front34.png` | 帧 1 **中立**（导出侧 Rest Pose 一口清） |
| `panic_f06_front34.png` | 帧 6 起手中段 |
| `panic_f13_{front34,side,back}.png` | 帧 13 **到位**（正前 3/4 · 正侧 · 背后） |
| `panic_f25_front34.png` · `panic_f46_{front34,side,back}.png` | 帧 25 保持中 · 帧 46 保持末 |
| `lab_single.png` · `lab_three.png` | lab：单实例 / 三实例同屏（间距 5.0 m） |

**可直接在 Blender 里看的一条**：`.scratch/panic/panic_clip.blend`（动作 `PanicCoverEars`，帧 1–46）。
⚠️ **我自己看不到图**（本会话的模型不吃图像输入）⇒ 上面的**几何读数**是我能给的替代：肘在肩**外 149 mm / 前 171 mm / 高 71 mm**，两肘间距 **601 mm**，肘角 **119.3°**，头轴与竖直 **25.9°**（缩头）。**"像不像捂着耳朵"这一条只有 owner 能判。**

## 七、问题差分

`new_finding = after − mapped(before) − expected_delta` = **空**。

| 检查 | 结果 |
|---|---|
| 预期差分内的文件 | `code/tools/author_xbot_chair_grab.py`（改：新增**宿主 6** `--task panic` + 库层件：部位面框 / 蒙皮带符号判据 / 逐指解 / 多解并列）· `code/tools/lab_multi_instance.py`（**新增**）· `design/engineering/evidence/panic-posture-2026-09-16.md`（**新增**）· `design/presentation/动作描述口径.md`（§15.6.1 加「① 件消费登记」· §15.7 ① 结账）· `design/slices/CP-01-ward-1f/slice.md`（两行四轴表回填） |
| **连带修改**（逐条登记） | ① [阶段证据说明](README.md) 的「已有证据」表**加一行**；② `author_xbot_chair_grab.py` 的**模块 docstring**（"三个宿主"→ 六个宿主）与 `main()` docstring——**该表已过期两轮**（#166 加 doorpush 时就没跟上），本件顺手更正；③ `visible_bone_outliers()` 加 `meshes=` 可选参数（多实例 lab 必需，见 §4.6 坑 ①）——**旧调用点行为不变**（默认仍是按名字取） |
| 计划外变化 | 无 |
| 工作树 | 提交后干净（`git status --short` 空） |
| **回滚演练** | ✅ **已演练**：临时 worktree 里逐条 `git revert` 两条提交后 **`git diff d632baa HEAD` 为空**（回滚态与 base **逐字节相同**）、宿主表回到既有五个（`panic` 命中 0 处、lab 文件已删）、四条门禁读数逐值回到改前 ⇒ **回滚恢复上一状态成立**。实做记录见 §九 |
| 预期不变项 | `data/action_set.json` **17 词条不增**（本件**不新增词条**）· `data/hand_grip_cards.json` 未触碰 · `code/unity/**` **未触碰**（不接 Unity 侧 lab）· `design/rules/回合战斗流程.md` §10.13 未触碰 · `PLAYABLE.md` 未触碰（仍 `NO_AUTHORIZED_PLAYABLE`）· 母版 `.blend` 与源 `X Bot.fbx` **字节未触碰**（全部写回都落在 `.scratch/panic/` 副本）· 既有四个宿主行为不变 |

**测试报告定位**：`.scratch/panic/panic_report_{6,7}.json`（两遍读数）· `panic_scan_body.json` · `panic_report_head.json`（抱头对照解）· `lab_report_{single,three}.json` · `stills/`——过程物、被 `.gitignore` 排除、磁盘保留。

## 八、未闭合（诚实清单）

| # | 项 |
|---|---|
| 1 | **owner 目视未做**（验收第 8 条）——静帧 11 张 + clip 已就绪 |
| 2 | **"具名面的横向范围"定义不合格**（本件实测暴露）：现用"最外片层的**顶点跨度**"，而**后脑面只有 12 个顶点** ⇒ 跨度小、掌缘容易判"面外"（抱头解由此判不上）。**建议**：改成"以锚点为心的**面域半径**"或"沿面法向的**局部平坦区**"——但**需要一个来源**（不能拍），留给 ②③ 或另开件 |
| 3 | **抱头那一解不通过**（§4.4）——含 #2 的根因；它的五指间隙也偏大（+0.6 ~ +34.0 mm：掌在后脑时手指越过头顶**伸向空中**）⇒ 抱头若要真正可用，手指朝向与落点需要**另解**（不是同一套 `f_dir = 头骨长轴`） |
| 4 | **朝向档（角度版 ε）仍未测**（U2′）：本件的"掌面法向夹角 180.00°"**只作读数**，没有阈值判据 |
| 5 | **身体条件的取舍无判据**（§4.3）：接触读数与身体条件**逐值无关**（目标面跟身体走）⇒ 下蹲/前倾/缩头三项**归观感**（owner）；肘方向有读数但**同样没有阈值**（"肘该多高"没有来源） |
| 6 | **②③ 的实例未落**：lab 目前只有 ① 的实例（三实例那次是**自测**：同一动作三份）⇒ "三件同屏"要等 ②③ |
| 7 | 未做**整机重启复现** · 未做**导出 E0–E6**（本件**不导 FBX**：口径 §15.7 词条位块明写不新增词条、不接 Unity lab） |

## 九、回滚演练实做记录

形态与 [#166](https://github.com/verystrongdog/game/issues/166) §十三 / [#168](https://github.com/verystrongdog/game/issues/168) §十 的先例一致：**临时 worktree + 逐条 `git revert` + 全门禁重跑**（不做 `reset --hard`）。

```bash
git worktree add --detach .scratch/rollback-drill-169 HEAD
cd .scratch/rollback-drill-169
git revert --no-edit 6a8eea4      # 证据 + 口径/切片回填
git revert --no-edit 8dcc868      # 宿主 6 + lab 装配器
```

| 核对项 | 预测（issue 的「回滚」节） | **实测** |
|---|---|---|
| 回落点 | 宿主与 lab 可整体删除、口径与切片可回退；无数据迁移、无资产改动 | ✅ **`git diff d632baa HEAD` 为空**（回滚态与 base **逐字节相同**） |
| **宿主表逐字核对** | 回到既有五个（`chair`/`card1`/`door`/`restate`/`doorpush`） | ✅ `choices=("chair", "card1", "door", "restate", "doorpush")` · 全文件 `panic` 命中 **0** 处 · `lab_multi_instance.py` **已删除** |
| `validate_cross_refs.py` | 0 死链 | ✅ **2020 refs / 2019 passed / 0 dead / 0 section warnings**（= 改前那一组数） |
| `validate_trash_isolation.py` | 全过 | ✅ 全部通过 |
| `validate_params.py` | 0 失败 | ✅ 56 checks / 49 passed / 0 failed / 7 warnings |
| `run_all_checks.py` | 16/16 | ✅ 16 validators / 16 passed / 0 failed |
| 母版与数据 | 零改动 | ✅ 母版 `.blend` 与源 `X Bot.fbx` **字节未触碰**（所有写回都在 `.scratch/panic/` 副本）；`data/` 零改动 |
| 工作树 | 干净 | ✅ `git status --short` 空；演练后 `git worktree remove --force`（`git worktree list` 只剩主树） |

⇒ **回滚恢复上一状态成立**（以最强形式：**逐字节**）。

## 十、来源

| 事实 | 来源 |
|---|---|
| 第四系「目标部位局部系」的定义与"不烘世界坐标" | [动作描述口径](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) §6.1 · §15.5 |
| 部位面 ε（头 5 面）与"两层骨集合不同" | [部位侧 ε 证据](body-part-epsilon-2026-09-16.md) §4.1/§4.2（[#168](https://github.com/verystrongdog/game/issues/168)） |
| 判据形态「弧面↔面」（掌面最低点 ↔ **有限面片**）· 容差两个数 | 同上口径 §13.4（U8 闭合）· §8.1 · §8.2 |
| F4a 判据时域（持续/一次性）· V-f 时序 | 同上 §13.3 F4a · §13.4.1 · §十 V-f |
| 多实例 lab 的四条硬规矩与间距 5.0 m | 同上 §15.8（owner 2026-09-16 圈定） |
| 逐指解（"四指共用一个系数"的实测代价） | [手部基准卡片证据](hand-grip-cards-2026-09-15.md) §八（[#164](https://github.com/verystrongdog/game/issues/164)） |
| 骨段 vs 蒙皮的层差（同类先例 41 mm） | 同上口径 §15.3 子分区「脚」· [#165 证据](xbot-contact-phase-2026-09-15.md) §七 |
| `soleMargin = 2.8 mm` 与 `支撑脚陷入` 的对称用法 | [#166 证据](door-push-2026-09-15.md) §十（宿主 5 的 `support_penetration`） |
| 可见骨判据与预览收敛（52 根 / 0 越界） | 同上 §十五（#166 第 3 轮） |
| 全部读数 | 本条实测（Blender 5.1.2，2026-09-16），原始 JSON 见 §七 |

---

*创建: 2026-09-16（agent 执行 [#169](https://github.com/verystrongdog/game/issues/169)）*
*状态: 收口证据——假设**支持**（耳侧两格）；**owner 目视未做**；未闭合 7 项见 §八*
*关联: [#169](https://github.com/verystrongdog/game/issues/169) · [#168](https://github.com/verystrongdog/game/issues/168) · [#164](https://github.com/verystrongdog/game/issues/164) · [#166](https://github.com/verystrongdog/game/issues/166) · [动作描述口径](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) · [阶段证据说明](README.md)*
