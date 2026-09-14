# 动作描述口径 ε 实测证据（手部「骨 → 蒙皮表面」偏移）

> [#160](https://github.com/verystrongdog/game/issues/160) 的收口证据。口径权威 = [动作描述口径](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) §八（容差 ε）；
> 必填字段按 [阶段证据说明](README.md) 与 [WORKFLOW.md §五/§六](../../../WORKFLOW.md) 记录。

## 一、结论（先读这一段）

| 项 | 值 |
|---|---|
| 达成 | 能力增量：`动作描述口径（人机协作接口）` · Implementation `NONE → PARTIAL`（接触档 ε 由"只报读数、人目视判"升级为"有来源的判据"） |
| 一句话 | 手部「骨原点 → 蒙皮表面」的 6 方向剖面已实测；**掌面方向 = 骨局部 `+Z`**（静止 T-pose 下朝世界 −Z，即掌心朝下，两侧一致）；**接触档 ε = 32.68 mm**（可见皮肤层 `Beta_Surface`），跨 4 个姿势**变化 ≤ 0.0008 mm** |
| 关键读数 | `Beta_Surface`：`LeftHand +Z = 32.6833 mm` · `RightHand +Z = 32.6854 mm`（对照 `Beta_Joints`：30.55 mm） |
| 假设判定 | **支持**（见 §五）：偏移在该骨局部系里是稳定常数——且结构原因已查清（手部区域权重为 **1.0 刚性**，无混合顶点） |
| 未做的事 | 朝向档（角度版 ε）与到位档**未测**；手部以外的骨**未测**；未做完整 Editor/进程重启后的复现 |

## 二、绑定

| 字段 | 值 |
|---|---|
| base SHA | `357a420`（切片表补能力行那次提交） |
| head SHA | 本回填提交（脚本 + 证据 + 口径 §八 回填） |
| 阶段 | [#160](https://github.com/verystrongdog/game/issues/160)（Experiment） |
| 执行者 | DSH agent（本机 WSL → Windows 侧 Blender） |
| 工具版本 | Blender **5.1.2**（`hash ec6e62d40fa9`，built 2026-05-19 01:37:34）· Windows 11 家庭中文版 · Python 3.10.12 |
| 被测对象 | 母版 `.scratch/blender_assets/xbot/XBot_AnimationTemplate.blend`（`5601197` 字节 · mtime 2026-09-14 22:31:58）· 骨架 `Armature`（78 骨 = 65 变形 + 13 控制） · 蒙皮网格 `Beta_Joints`(10514 v) / `Beta_Surface`(14232 v) |
| ⚠️ 母版的地位 | 它是**生成物**（`.scratch`、被 `.gitignore` 排除、**不可逐字节复现**，见[管线 §4.4](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md)）⇒ 上表只作**留痕**，不当"没变过"的判据；复现靠下方命令重建母版后再跑 |
| ⚠️ 母版里有一条既有污染 | **撤回动作的椅子代理仍在**：`REF_Back` / `REF_Seat` / `REF_Leg0-3`（6 个 8 顶点网格，无 Armature 修改器）。本脚本按"是否被该骨架蒙皮"筛网格，故不受影响；但**母版不是干净母版**这件事本身该记一笔（不属本条范围，未处理） |

## 三、命令与退出码

```powershell
# 一次（跑两遍取一致性）
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --factory-startup `
  --python-exit-code 1 --python "$env:TEMP\measure_xbot_surface_offset.py" -- `
  --template 'Z:\home\dog\game\.scratch\blender_assets\xbot\XBot_AnimationTemplate.blend' `
  --report 'Z:\home\dog\game\.scratch\surface_offset_run<N>.json'
```

| 命令 | 退出码 |
|---|---|
| 上表（run3） | **0**（`problems: []`，量级自证全过） |
| 上表（run4） | **0** |
| `python3 code/tools/validate_cross_refs.py` | **0** |
| `python3 code/tools/validate_trash_isolation.py` | **0** |
| `python3 code/tools/validate_params.py` | **0**（0 failed / 7 warnings，全在未改动文件上） |

> 复现要点：脚本位于 `code/tools/measure_xbot_surface_offset.py`；`--python` 传 Windows 本地副本（UNC 形式 Blender 吃不到，见管线 §7.1 坑 3）；`.blend` 走 `Z:` 盘符（bash 双引号会把 `\\` 折成 `\`，见 §7.1 坑 1）。

## 四、读数

### 4.1 接触档 ε（骨原点 → 掌面，沿掌面法向）

| 网格 | 手 | 掌面方向（骨局部） | **ε** | 静止时世界指向 |
|---|---|---|---|---|
| **`Beta_Surface`**（可见皮肤层） | Left | `+Z` | **32.6833 mm** | `(0, 0, −1)` = 下 |
| **`Beta_Surface`** | Right | `+Z` | **32.6854 mm** | `(0, 0, −1)` = 下 |
| `Beta_Joints`（对照） | Left | `+Z` | 30.5477 mm | `(0, 0, −1)` = 下 |
| `Beta_Joints`（对照） | Right | `+Z` | 30.5481 mm | `(0, 0, −1)` = 下 |

**取哪一层当 ε**：取 `Beta_Surface`。判据（实测，非印象）：两者都可见、都带 Armature 修改器；`Beta_Surface` 顶点更多（14232 vs 10514）、材质为 `Beta_HighLimbsGeoSG3`（基色 `0.837/0.302/0.264`，砖红），`Beta_Joints` 的 `Beta_Joints_MAT1` 为 `0.333/0.125/0.101`（暗红）——与[管线 §二](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md)"X Bot 主材质砖红偏粉"的描述方向一致。**换蒙皮层要重测**（两层的 ε 差 2.1 mm，占 ε 的 6.5%）。

### 4.2 六方向剖面（骨原点 → 最外顶点，mm）

| 骨（`Beta_Surface`） | `+X` | `−X` | `+Y` | `−Y` | `+Z` | `−Z` |
|---|---|---|---|---|---|---|
| `mixamorig:LeftHand` | 53.39 | 45.37 | **91.91** | 6.73 | **32.68** | 33.31 |
| `mixamorig:RightHand` | 45.37 | 53.40 | **91.91** | 6.74 | **32.69** | 33.30 |

读法：`+Y` = 沿骨长（腕→指方向，91.91 mm ≈ 手长）；`−Y` = 腕侧（6.73 mm）；`±Z` = 掌/背两侧（≈33 mm 各半）；`±X` = 拇指侧与尺侧。世界指向：`+Y → 世界 +X`（左臂展方向）· `+Z → 世界 −Z`（下）。取样各 294 顶点（`Beta_Joints` 各 918）。

### 4.3 稳定性（跨姿势跟踪"静止时选出的最外顶点"）

| 姿势 | `Beta_Surface` 全骨最大变化 | `Beta_Joints` |
|---|---|---|
| `wrist_bend`（双手腕局部 X +40°） | **0.000798 mm** | 0.000817 mm |
| `elbow+wrist`（肘 Z+30° + 腕 Y+20°） | 0.000595 mm | 0.000602 mm |
| `arms_down`（双肩局部 X +35°） | 0.000473 mm | 0.000435 mm |

（"rest" 姿亦报 0.000496 mm —— 那是 `to_mesh()` 往返的浮点噪声底，即**本测量的精度地板 ≈ 5e-4 mm**。）

### 4.4 掌面方向怎么判出来的（不靠猜）

判据 = **四指屈曲会把中指尖带向拇指尖**（拇指在掌面一侧的边上），两种符号各试一次、取使「中指尖 ↔ 拇指尖」距离**变小**的那个：

| 手 | 静止间距 | 符号 `+1` | 符号 `−1` | 取 | 掌面方向 | 法向分量 |
|---|---|---|---|---|---|---|
| Left | 150.793 mm | **115.446 mm** | 181.991 mm | `+1` | `+Z` | 80.707 mm |
| Right | 150.721 mm | **115.427 mm** | 181.886 mm | `+1` | `+Z` | 80.627 mm |

判据决定性成立（两符号差 ≈ 66 mm，方向明确），且与 4.2 的轴向映射自洽（`+Z` = 世界 −Z = 掌心朝下，Mixamo T-pose 的标准朝相）。

### 4.5 重跑一致性

| 项 | 值 |
|---|---|
| 两次运行的**可比数值** | **13037 个** |
| 不一致的数值 | **0 个**（逐值相同） |
| 结论 | `--report` 两份 JSON 除模板路径外**无任何差异** ⇒ "该工具显示精度内一致"以最强形式成立 |

## 五、判定标准（三种结局的评估）

| 结局 | 是否命中 | 依据 |
|---|---|---|
| **支持** | ✅ | 同一骨在 4 个姿势下偏移之差 ≤ 0.0008 mm（远小于 4.1 的 32.68 mm），且数值落 §八 后"贴合"成为可判 |
| 否定 | ✗ | 偏移未随姿势显著变化 |
| 证据不足 | ✗ | 测法与 `soleMargin` 同源（都由"骨在蒙皮里、表面才是实体"推出），且取值稳定 |

**为什么"稳定"这件事是结构性的、已被解释清（重要）**：手部区域的顶点**权重全为 1.0**（取样集 min/中位/max = `1.0/1.0/1.0`）。线性混合蒙皮下，权重 = 1 的顶点相对其骨**恒为常数**——所以本次稳定性是**由绑定方式保证**的，不是巧合。全网格确实存在混合权重顶点（`Beta_Surface` 853 个 / `Beta_Joints` 764 个），但**都不在手部**（在肘/膝/肩这类关节处）。⇒ 换到带混合权重的区域测量时，稳定性结论**不自动继承**，须重测。

## 六、两条实测教训（都踩过、都已改）

1. **单位**：母版是 Mixamo **厘米制** + Armature 对象 `scale = 0.01`（[管线 §二](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) ⚠️ 块）。骨矩阵与网格数据都在**骨架局部单位（= 1 cm）**里 ⇒ 米制换算 = `× 对象 scale`。第一版按"米"直接 `× 1000`，量出"手的外沿 **3–10 米**"——**量级自证当场否掉了这个读数**（本脚本已内建 `PLAUSIBLE_MAX_M = 0.30`，超限即把问题写进报告并不返回 0）。
2. **屈曲符号不能从别处套用**：本脚本第一版直接取了 [管线 §七·B](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) 记的 `左 X+1 / 右 X−1`，结果右手解出**超伸展**（指尖朝反方向）。改用"两符号都试、取指尖靠近拇指"的判据后，**两侧都是 `+1`**。
   ⚠️ **与 §七·B 的读数不一致**（那处记的是右四指 `X−1`）。两条判据量的不是同一件事的可能性存在（§七·B 的"朝掌心"用的是它自己算的掌面平面——正是[错误分类](../../engineering/blender%E9%94%99%E8%AF%AF%E5%88%86%E7%B1%BB.md) A1「自证式判据」的形态）。**本条不裁定谁对**，留给 [#163](https://github.com/verystrongdog/game/issues/163) 在同一姿势下用两条判据并列复核——已登记为未闭合项。

## 七、问题差分

`new_finding = after − mapped(before) − expected_delta` = **空**。

| 检查 | 结果 |
|---|---|
| 预期差分内的文件 | `code/tools/measure_xbot_surface_offset.py`（新增） · `design/engineering/evidence/action-description-epsilon-2026-09-14.md`（新增，⚠️ 文件名比 #160 预期差分里写的 `action-description-epsilon.md` 多带日期——遵循[阶段证据说明](README.md) 的 `<阶段>-<日期>.md` 约定） · `design/presentation/动作描述口径.md`（§八 填值 + §十一 U2 闭合） · [阶段证据说明](README.md)（登记本行） |
| 计划外变化 | 无 |
| 工作树 | 提交后干净（`git status --short` 空） |
| **回滚演练** | ✅ **已演练**（2026-09-14）：`git revert --no-commit HEAD` 后三个校验器仍绿（`cross_refs` 回到 **1860 refs / 0 死链**、`trash_isolation` 全过、`params` 0 failed），再 `git reset --mixed HEAD && git checkout -- .` 后工作树干净 ⇒ **回滚恢复上一状态成立**（本条是纯新增：1 脚本 + 1 证据 + 1 文档段落 + 1 登记行，无数据迁移） |
| 预期不变项 | 母版字节**未触碰**（脚本只读打开）· 源 `X Bot.fbx` 未触碰 · `soleMargin` 未改 · §八 的朝向档/到位档未改 |

**测试报告定位**：`--report` 两份 JSON 落 `.scratch/surface_offset_run{3,4}.json`（过程物、被 `.gitignore` 排除、磁盘保留）；复现命令见 §三。

## 八、未闭合（诚实清单）

| # | 项 |
|---|---|
| 1 | **朝向档（角度版 ε）与到位档未测**——§八 三档只填了接触档 |
| 2 | **手部以外的骨未测**（本条只测 42 根 `Hand*` 族；脊柱/膝/肘等已知带混合权重） |
| 3 | **混合权重区域的稳定性不自动继承**（§五 已给理由），未测 |
| 4 | **未做完整进程重启后的复现**（两次运行在同一台机、同一 Blender 版本，但**是两次独立进程**——比"同会话重跑"强，比"重启机器"弱） |
| 5 | **与 §七·B 的屈曲符号不一致**未裁定（§六.2），转 [#163](https://github.com/verystrongdog/game/issues/163) |
| 6 | 母版里**残留撤回动作的 `REF_*` 代理**（§二），未清理 |

## 九、来源

| 事实 | 来源 |
|---|---|
| 容差 ε 的口径（"骨 → 蒙皮表面"实测偏移，三档分立） | [动作描述口径](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) §八 |
| `soleMargin = 0.0028 m` 的同源来历（bind pose 趾骨 Y 实测） | [动画处理能力对照实验](../../presentation/%E5%8A%A8%E7%94%BB%E5%A4%84%E7%90%86%E8%83%BD%E5%8A%9B%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C.md) §2.1 |
| 骨架局部单位 = 1 cm（对象 `scale = 0.01`） | [Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) §二 ⚠️ 单位口径块 |
| 局部 Y 扭转对本骨骨尖位移恒为 0 ⇒ 必须补偏轴标志点 | 同上 §7.4 |
| 自证式判据（判据与需求不同层 ⇒ 全绿而被否） | [Blender 侧错误分类](../../engineering/blender%E9%94%99%E8%AF%AF%E5%88%86%E7%B1%BB.md) §二 A1 · [危险点表](../../engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md) :147 |
| §七·B 记的四指屈曲符号（左 `X+1` / 右 `X−1`） | [Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) §七·B |
| 全部读数 | 本条实测（Blender 5.1.2，2026-09-14），原始 JSON 见 §七 |

---
*创建: 2026-09-14（agent 执行 [#160](https://github.com/verystrongdog/game/issues/160)）*
*状态: 收口证据——假设**支持**；未闭合 6 项见 §八*
*关联: [#160](https://github.com/verystrongdog/game/issues/160) · [#163](https://github.com/verystrongdog/game/issues/163) · [动作描述口径](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) · [阶段证据说明](README.md)*
