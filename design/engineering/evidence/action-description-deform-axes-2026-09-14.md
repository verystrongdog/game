# 无约束变形骨轴向语义证据（12 根骨 × 3 轴，含"仅蒙皮可见"三态判定）

> [#161](https://github.com/verystrongdog/game/issues/161) 的收口证据。表本身落
> [Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) §2.1.4；
> 必填字段按 [阶段证据说明](README.md) 与 [WORKFLOW.md §五/§六](../../../WORKFLOW.md) 记录。

## 一、结论（先读这一段）

| 项 | 值 |
|---|---|
| 达成 | 能力增量：`动作描述口径（人机协作接口）` · Implementation `NONE/PARTIAL → PARTIAL`（"绕某根骨的轴"这句话，从"agent 手上没有映射"变成**有实测表**） |
| 一句话 | 12 根无约束变形骨 × 3 局部轴 = **36 格全部测完**；**31 格可观察 · 2 格仅蒙皮可见 · 3 格不可观察**；"目视水平"这类需求从此有轴—位移映射 |
| 关键读数 | `Head` X（点头）**157.6 mm** · `Neck` X **191.5 mm** · `Head`/`Neck` 的扭转**只有蒙皮看得见**（骨尖恒 0）· `ToeBase` 的扭转**骨尖与标志点全 0、蒙皮 22.28 mm** |
| 假设判定 | **支持**（见 §五）；新增一条**实现级发现**：为什么必须多量"蒙皮"这一列 |
| 未做的事 | 40 根手指骨未测（另议）· 未加任何控制骨（口径 §三 D6）· 未做整机重启复现 |

## 二、绑定

| 字段 | 值 |
|---|---|
| base SHA | `6b051ab`（#160 切片表回填提交） |
| head SHA | 本回填提交（脚本扩展 + §2.1.4 + 口径 §6.2/§十一 U3 + 证据） |
| 阶段 | [#161](https://github.com/verystrongdog/game/issues/161)（Experiment） |
| 执行者 | DSH agent（本机 WSL → Windows 侧 Blender） |
| 工具版本 | Blender **5.1.2**（`hash ec6e62d40fa9`）· Windows 11 家庭中文版 · Python 3.10.12 |
| 被测对象 | 母版 `.scratch/blender_assets/xbot/XBot_AnimationTemplate.blend`（`5601197` 字节 · mtime 2026-09-14 22:31:58）· 骨架 78 骨 · 蒙皮网格 `Beta_Joints`(10514 v) / `Beta_Surface`(14232 v) |
| 目标骨 | 52 根无约束变形骨中**除 40 根手指**外的 12 根：`Spine`/`Spine1`/`Spine2` · `Neck`/`Head`/`HeadTop_End` · `Left/RightShoulder` · `Left/RightToeBase` · `Left/RightToe_End` |
| 身体坐标系（实测） | `left = (1.000, 0.000, 0.000)` · `fwd = (0.000, −0.996, 0.088)` · `up = (0.000, 0.088, 0.996)`（由髋/头、左右大腿、足→趾尖**解剖定义**，见脚本 `body_frame()`） |

## 三、命令与退出码

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --factory-startup `
  --python-exit-code 1 --python "$env:TEMP\measure_xbot_control_axes.py" -- `
  --group deform --template 'Z:\home\dog\game\.scratch\blender_assets\xbot\XBot_AnimationTemplate.blend' `
  --report 'Z:\home\dog\game\.scratch\deform_axes_run<N>.json'
```

| 命令 | 退出码 |
|---|---|
| 上表（run1 / run2） | **0** / **0** |
| `python3 code/tools/validate_cross_refs.py` | **0** |
| `python3 code/tools/validate_trash_isolation.py` | **0** |
| `python3 code/tools/validate_params.py` | **0**（0 failed / 7 warnings，全在未改动文件上） |

> 脚本是**扩展既有 `measure_xbot_control_axes.py`**（新增 `--group control|deform|both`，默认 `control` **保持既有行为不变**），
> 不新建第二个测量器——#161 的预期差分即如此要求。

## 四、读数

### 4.1 三态分布（36 格）

| 态 | 格数 | 是哪几格 |
|---|---|---|
| **可观察** | **31** | 其余全部 |
| **仅蒙皮可见** | **2** | `LeftToeBase.Y` · `RightToeBase.Y`（骨尖 **0.00** / 标志点 **0.00** / 蒙皮 **22.28 mm**） |
| **不可观察** | **3** | `HeadTop_End.Y` · `LeftToe_End.Y` · `RightToe_End.Y`（叶骨、骨尖在轴上、**无顶点权重**⇒蒙皮 0.00） |

完整 36 行读数见 [管线 §2.1.4](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) 的表与
`.scratch/deform_axes_run{1,2}.json`（过程物、gitignore）。

### 4.2 三条关键读数

1. **"目视水平"现在可落**：`Head` X（点头轴）⇒ 头顶移动 **157.6 mm**（前+147.2 / 上−56.4）、
   `Neck` X ⇒ **191.5 mm**（前+177.9 / 上−70.7）。头颈**都没有控制骨**（口径 §三 D6：不加控制骨，走变形骨直接打键）⇒ 这张表就是那条路的唯一依据。
2. **扭转只能靠蒙皮看**：`Neck` Y 的本骨骨尖 **0.00**、链末（`HeadTop_End`，在轴上）45.0，而**蒙皮 61.3 mm**；
   `Head` Y 同理（骨尖 0，蒙皮 51.4 mm）。
3. **对称性独立复现**：肩 X/Z 的**左右侧符号相反**（左 前+256.8 / 右 前−253.7）、脚趾 Z 的**左右同号**（两侧都是 侧+63.5）
   ——与 §2.1.2 已实测的"**臂镜像 / 腿同轴**"一致，属**独立复现**（不同骨、不同测法）。

### 4.3 重跑一致性

| 项 | 值 |
|---|---|
| 蒙皮求值**噪声底** | **0.000000 mm**（同一姿势重求值，逐值相同） |
| 两次运行可比数值 | **806 个**，不一致 **0 个** |
| 两次打印表 | **逐字相同** |

### 4.4 为什么"蒙皮"这一列不是锦上添花（实现级发现）

脚本**第一次运行就崩了**：`TypeError: unsupported operand type(s) for *: 'NoneType' and 'float'`——
因为某根骨转动后**蒙皮一个顶点都没动**，代码里"最大位移顶点"仍是 `None`。
崩的那一格正是 `HeadTop_End`（叶骨 × 无顶点权重）。

⇒ 这不是代码手滑，而是**测量对象本身的分层**：
**"骨动了"与"看得见"是两件事**。§2.1.1 的 13 根控制骨碰巧都能用骨尖观察到，于是这个分层一直没暴露；
扩到 52 根之后，**36 格里有 5 格**（2 仅蒙皮 + 3 不可观察）用骨尖**根本量不出来**——
若沿用旧口径，会把这些轴写成"没用"，那是**错误结论**（§7.4 已为控制骨记过一次同类教训）。

## 五、判定标准（三种结局的评估）

| 结局 | 是否命中 | 依据 |
|---|---|---|
| **支持** | ✅ | 目标子集每根每轴都给出了可复现读数与方向分解（体侧/前后/上下）；`Head`/`Neck`/`Spine*`/`Shoulder*`/`ToeBase*` 全覆盖 |
| **否定** | ✅ **部分命中（已按预案记账）** | 3 格对**任何**标志点与蒙皮都恒为 0 ⇒ 表中显式标"不可观察"并给几何理由（叶骨 + 骨尖在轴上 + 无顶点权重）。**这正是判定标准里写明的"这同样是结论"** |
| 证据不足 | ✗ | 读数与母版版本一致（基线 Blender 5.1.2），两次独立进程逐值相同 |

## 六、问题差分

`new_finding = after − mapped(before) − expected_delta` = **空**。

| 检查 | 结果 |
|---|---|
| 预期差分内的文件 | `code/tools/measure_xbot_control_axes.py`（改，+`--group`） · `design/presentation/Blender动作制作管线.md`（改，+§2.1.4） · `design/presentation/动作描述口径.md`（改，§6.2 + §十一 U3） · `design/engineering/evidence/action-description-deform-axes-2026-09-14.md`（新增；⚠️ 文件名比 #161 预期差分写的 `action-description-unc-age-axes.md` 更清楚，且遵循 `<阶段>-<日期>.md` 约定） · [阶段证据说明](README.md)（登记本行） · `design/slices/CP-01-ward-1f/slice.md`（🔧 注释一行） |
| 计划外变化 | 无 |
| 预期不变项 | §2.1.1 的 13 根控制骨表**逐字未动** · 默认行为（`--group control`）未变 · 母版未触碰（只读打开） · 40 根手指骨未测 |
| 工作树 | 提交后干净 |
| **回滚演练** | ✅ **已演练**：`git revert --no-commit HEAD` 后三个校验器仍绿，`git reset --mixed HEAD && git checkout -- .` 后工作树干净 ⇒ 回滚恢复上一状态成立（纯新增/追加，无数据迁移） |

**测试报告定位**：`.scratch/deform_axes_run{1,2}.json` 与 `.scratch/deform_table_{1,2}.txt`；复现命令见 §三。

## 七、未闭合（诚实清单）

| # | 项 |
|---|---|
| 1 | **40 根手指骨未测**（上一轮屈曲轴为脚本自测，符号存在待裁定分歧 → [#163](https://github.com/verystrongdog/game/issues/163)） |
| 2 | **+20° 是单一幅度**：`HeadTop_End`/`Toe_End` 的"仅自身骨尖动"未在不同角度下复核 |
| 3 | **未做整机重启复现**（两次运行是两次独立进程，比"同会话重跑"强、比"重启机器"弱） |
| 4 | 母版里**残留撤回动作的 `REF_*` 代理**（同 [#160](https://github.com/verystrongdog/game/issues/160) 证据 §二）未清理 |
| 5 | 本表**尚未被第二个动作消费**——它是否够用，要等 [#163](https://github.com/verystrongdog/game/issues/163) 用"目视水平"真的落一次 |

## 八、来源

| 事实 | 来源 |
|---|---|
| 13 根控制骨 × 3 轴表与"偏轴标志点/基准先归零"口径 | [Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) §2.1.1 · §7.4 |
| 臂镜像 / 腿同轴的符号规则 | 同上 §2.1.2 |
| 头颈不加控制骨、走变形骨直接打键 | [动作描述口径](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) §三 D6 |
| "目视水平"属旧判据不可能报出的三项之一 | 同上 §十 V-b |
| 局部 Y 扭转对本骨骨尖位移恒为 0 | [Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) §7.4 |
| 全部读数 | 本条实测（Blender 5.1.2，2026-09-14），原始 JSON 见 §六 |

---
*创建: 2026-09-14（agent 执行 [#161](https://github.com/verystrongdog/game/issues/161)）*
*状态: 收口证据——假设**支持**、否定分支按预案记账（3 格不可观察）；未闭合 5 项见 §七*
*关联: [#161](https://github.com/verystrongdog/game/issues/161) · [#160](https://github.com/verystrongdog/game/issues/160) · [#163](https://github.com/verystrongdog/game/issues/163) · [Blender动作制作管线](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) §2.1.4 · [阶段证据说明](README.md)*
