# Unreal 动画制作与修正能力探针证据（X Bot Control Rig / FBIK 小样）

> [#158](https://github.com/verystrongdog/game/issues/158) 的**收口证据**。必填字段按 [WORKFLOW.md §五/§六](../../../WORKFLOW.md) 与 [阶段证据说明](README.md) 记录；共同样本与观测口径的权威是 [动画处理能力对照实验](../../presentation/动画处理能力对照实验.md) §二/§三/§四——**本轮没有产生其中任何一项读数**。

## 一、结论

**证据不足。**

| 项 | 值 |
|---|---|
| 结论 | **证据不足**（既不是"支持假设"，也不是"否定假设"） |
| 原型去向 | **未创建**——没有 `.uproject`、`.uasset`、DerivedDataCache、Intermediate、Saved，也没有引擎二进制；「删除」无对象可执行 |
| 能力增量 | `Unreal 动画工具对照证据` · Design `UNRESOLVED → CANDIDATE`：**未达成**，仍在 `UNRESOLVED` |
| 迁移授权 | **无**。本文件是"不可用"的记录，不构成引擎迁移或路线选择的授权 |

判据映射（[#158](https://github.com/verystrongdog/game/issues/158) 正文「判定标准」的「证据不足」分支）：

- 该分支第一条理由「**实际 Unreal 版本/插件不可用**」**成立**——本机从未安装过 Unreal Engine，实测见 §二。
- 该分支第三条理由「**Unity 对照尚未产出**，只能证明绝对可行而不能完成相对比较」**同向成立**——[#157](https://github.com/verystrongdog/game/issues/157) 仍在 `ready-for-agent`，`code/unity/Assets/Scenes/` 下只有 `ActionLab` 与 `BrainViewLab`，接触修正 lab 尚未产出。
- 「支持」与「否定」两支都**没有可判对象**：从未进入 Sequencer / Control Rig，没有任何一条共同观测读数。

## 二、环境探针（只读，逐条实测）

原始输出留痕：`artifacts/probe-158-raw.txt`（快段另存 `artifacts/probe-158-fast.txt`；`artifacts/` 被 `.gitignore` 排除）。探针脚本：`artifacts/probe158.sh`、`artifacts/probe158-fast.sh`。

### 2.1 引擎是否存在——六项独立检查，全部为否

| # | 检查 | 命令 | 实测结果 |
|---|---|---|---|
| 1 | WSL 全盘引擎/工程文件 | `find / -xdev \( -iname "UnrealEditor*" -o -iname "*.uproject" \)` | 扫描完成，**0 命中** |
| 2 | Windows 侧引擎二进制 | `find /mnt/c -maxdepth 7 -iname "UnrealEditor.exe"` | 扫描完成（未超时），**0 命中** |
| 3 | Epic 安装目录 | `ls -d "/mnt/c/Program Files/Epic Games"` | `No such file or directory` |
| 4 | Epic 数据目录 | `ls -d /mnt/c/ProgramData/Epic` | `No such file or directory` |
| 5 | 注册表安装登记 | `reg.exe query "HKLM\SOFTWARE\EpicGames" /s` | `exit=1`，系统找不到指定的注册表项 |
| 6 | UE 配置残留 | `find /mnt/c/Users/9527/AppData/Local/UnrealEngine -maxdepth 1` | 只有 `4.17` / `4.18` / `4.25` / `4.27`，且各仅 `Saved/Config`——是**别人发布版游戏**的运行时残留，不含编辑器 |

唯一相关实体是**安装器本身**：`C:\Users\9527\Downloads\EpicInstaller-20.1.4-unrealEngine-7182618afca04550acfa86c1dbdfe445.exe`（87,356,416 B，2026-09-14 11:43 下载）——**已下载、未运行**。故本机从未装过 Unreal Engine，也无 Launcher 可供后续安装。

### 2.2 源码可达性——**通的**（不是权限问题）

| 项 | 实测 |
|---|---|
| 仓库 | `gh api repos/EpicGames/UnrealEngine` → `EpicGames/UnrealEngine`，`private: true`（owner 的 GitHub 账号已关联 Epic，源码可读） |
| 仓库体积 | `size: 38916059` KB ≈ **37.1 GiB**（含全部历史的服务器侧口径） |
| 最新稳定 tag | `5.8.2-release`（另有 `5.7.0`–`5.7.4`、`5.8.0`–`5.8.1` 等） |

### 2.3 拿到源码也装不起来——三项硬约束

| 约束 | 实测读数 | UE 侧需求（估算，未实测） |
|---|---|---|
| **磁盘** | `C:` 是**唯一卷**：475.7 GB，**空 51.4 GB**（`Get-Volume` 实测）。WSL 里 `df` 显示的 934 GB "空余"是假象——那是 `C:\Users\9527\AppData\Local\wsl\{c1eb1fb7-…}\ext4.vhdx`（**实体 50.8 GB**，内部仅用 23 GB）的上限，写进去的每个字节都从 C: 里扣 | 源码路线：浅克隆 ≈ 10–20 GB + `Setup.sh` 依赖 ≈ 20–30 GB + 构建产物 ≈ 60–120 GB ⇒ **≈ 110–185 GB**；Launcher 版 ≈ 50–60 GB |
| **内存** | WSL 上限 **7 GB**（宿主 `TotalPhysicalMemory = 16,505,966,592` B ≈ 15.4 GiB；**无** `.wslconfig`，故取默认上限） | UE5 编辑器标称最低 8 GB；源码构建的链接步骤常 >10 GB |
| **GPU** | `/dev/dxg` 不存在；`nvidia-smi -L` → `Failed to initialize NVML: GPU access blocked by the operating system` | WSLg 只剩软件渲染，编辑器 GUI 不具备可用性 |

> 另记一条**操作事实**：本轮曾尝试把源码浅克隆到工作区外（`/home/dog/ue`），被文件沙箱以 `Read-only file system`（`workspace-write` 模式）拒绝，克隆**未开始**、未产生任何下载。源码路线若日后重启，克隆必须落在工作区内或先放开该路径权限。

## 三、共同观测口径（M1–M7）——七项全部未取

| id | 观测量 | 本轮读数 | 原因 |
|---|---|---|---|
| M1 | 右手 ↔ 目标距离（约束关/开） | 未取 | 无引擎，未建立场景 |
| M2 | 足底相对地面高度（左/右） | 未取 | 同上 |
| M3a / M3b | 根水平漂移 / 根朝向偏差 | 未取 | 同上 |
| M4 | 骨长不变量 | 未取 | 同上 |
| M5 | 脚滑代理量 | 未取 | 同上 |
| M6 | 肘 / 膝屈曲角 | 未取 | 同上 |
| M7 | 重开可复现性 | 未取 | 无编辑器状态可重开 |

## 四、成本口径（C1–C9）——能填的部分

| id | 项 | 本轮值 |
|---|---|---|
| C1 | 引擎与版本 | **无**（未安装任何版本） |
| C2 | 工具链与插件 | **无**（Control Rig / FBIK / Motion Warping 的启用状态无从记录） |
| C3 | 建立耗时 | **未开始**（下载未执行） |
| C4 | 人工步骤 | **不可数**（未进入编辑器） |
| C5 | 自定义代码量 | **0**（未新增任何 Unreal 侧文件） |
| C6 | 警告与错误 | **无编辑器，无警告原文可录** |
| C7 | 可撤销性 / 可诊断性 | **N/A**（无操作可撤销） |
| C8 | 资产结果 | **无**（无 Animation Sequence 产出，无关键截图） |
| C9 | 回滚演练 | 见 §六——撤销对象是**本证据提交**，不是原型 |

## 五、owner 裁定（2026-09-14）

| # | 裁定 | 落点 |
|---|---|---|
| 6 | **Unreal 线不建**：[#158](https://github.com/verystrongdog/game/issues/158) 不再以"补齐 Unreal 环境后重跑"为路径，三线对照收窄为**两线**（Unity [#157](https://github.com/verystrongdog/game/issues/157) / Blender [#156](https://github.com/verystrongdog/game/issues/156)） | [动画处理能力对照实验](../../presentation/动画处理能力对照实验.md) §七 裁定表第 6 行 + 同文 §一 / §二·2.2 / §三 / §四 / §五 / §六 与页脚的线数同步 |

## 六、逐条验收标准对照（[#158](https://github.com/verystrongdog/game/issues/158) 正文）——六条全部未达成

| # | 验收标准（摘要） | 状态 | 原因 |
|---|---|---|---|
| 1 | 记录实际 Unreal 完整版本、OS、Control Rig/FBIK/Motion Warping 插件状态及 X Bot 导入的 Skeleton、参考姿势、根结构与全部警告 | **未达成** | 引擎不存在，§二.1 六项检查全否 |
| 2 | 用仓库内 X Bot + `PhysicalAttack.fbx` 在 Sequencer/Control Rig 中逐帧修正命中帧的右手、双脚、骨盆 | **未达成** | 无编辑器；且从未建立 IK Rig/Retargeter，无理由与映射可录 |
| 3 | 记录修正前后的右手目标距离、双脚相对地面高度、关节异常、Motion Warping 窗口前后根位置/朝向偏差与脚滑 | **未达成** | 对应 §三 的 M1–M6，七项全未取 |
| 4 | 修正结果烘焙/保存为独立 Animation Sequence，重开项目后仍可独立播放 | **未达成** | 无产出物，无帧范围、根运动、接触结果与警告可录 |
| 5 | 按共同口径记录导入到首次可编辑的耗时、人工步骤、控制器/节点数量、自定义 Blueprint/C++ 数量、可撤销性、可诊断性、稳定性 | **未达成** | §四 的 C3–C8 无一有实数 |
| 6 | 证据明确写出「支持假设 / 否定假设 / 证据不足」之一、逐项依据、原型删除确认，且结论不得被解释为引擎迁移授权 | **达成** | 本文件 §一（结论与判据映射）· §六（逐项依据）· §一「原型去向：未创建」与「迁移授权：无」 |

> 第 6 条是本轮唯一可交付的一条——它是**证据文件的形态要求**，不是实测要求。

## 七、执行的命令与退出码

| # | 命令 | 退出码 | 结论 |
|---|---|---|---|
| 1 | `bash artifacts/probe158.sh`（§二.1 的第 1/2 项 + 全部快段） | 0 | 引擎不存在；读数见 §二 |
| 2 | `gh api repos/EpicGames/UnrealEngine --jq '.full_name,.default_branch,.size,.private'` | 0 | 源码可读（`private: true`，≈37.1 GiB） |
| 3 | `reg.exe query "HKLM\SOFTWARE\EpicGames" /s` | 1 | 无安装登记（**期望的"不存在"**） |
| 4 | `python3 code/tools/validate_cross_refs.py` | 0 | 1738 passed / 0 dead / 0 section warnings |
| 5 | `python3 code/tools/validate_trash_isolation.py` | 0 | 290 个活跃 `.md` 全部通过 |
| 6 | `python3 code/tools/validate_params.py` | 0 | 49 passed / 0 failed / 7 warnings（均为改动前既有） |
| 7 | `python3 code/tools/validate_issues.py --from-github` | 0 | 10 passed / 0 failed / 4 warnings（均为改动前既有） |
| 8 | 浅克隆到 `/home/dog/ue`（工作区外） | **非 0** | 沙箱拒绝写入（`Read-only file system`），**未产生下载**——记为操作事实，非代码缺陷 |

第 4–7 项是**改动前基线**；改动后重跑结果见 §九。

## 八、问题差分

```
new_finding = after − mapped(before) − expected_delta = 空
```

- `before`（base `eae5fd0`）：`design/engineering/evidence/` 下无 Unreal 相关证据；本机无 Unreal 环境（§二 的六项检查在改动前后同值）。
- `expected_delta`（开工前登记，见 [#158](https://github.com/verystrongdog/game/issues/158) 预期差分）：新增 `design/engineering/evidence/unreal-animation-probe-2026-09-14.md`、`design/engineering/evidence/unreal-animation-probe-2026-09-14/`（关键截图）与 [动画处理能力对照实验](../../presentation/动画处理能力对照实验.md) 的线数同步。**截图目录未创建**（未进入编辑器，无截图可留）——这是对预期差分的**如实收窄**，不是未登记的偏离。
- 非预期 diff：无。Unity 工程、Core、动作词表、源 X Bot / `PhysicalAttack.fbx` 字节、CP-01 must-prove、持椅交互暂停状态均未改动；未向 git 提交任何 Unreal 二进制或缓存。

**本轮唯一值得记的认知修正**（不是仓库缺陷）：WSL 里 `df` 报出的"934 GB 空余"是 `ext4.vhdx` 的**上限**，而该文件实体只占 `C:` 的 50.8 GB、宿主整卷仅剩 51.4 GB——把 WSL 的 `df` 当作可用空间会系统性高估本机的存储余量。这条已写进 §二.3 的表格。

## 九、回滚演练、工作树与门禁复跑

（本节在提交后填实测结论。）

---

*创建: 2026-09-14 | 状态: `证据不足`（[#158](https://github.com/verystrongdog/game/issues/158) 收口证据；能力增量未达成，不构成迁移授权）*
*关联: [动画处理能力对照实验](../../presentation/动画处理能力对照实验.md) · [阶段证据说明](README.md) · [WORKFLOW.md](../../../WORKFLOW.md) · [#157](https://github.com/verystrongdog/game/issues/157) · [#156](https://github.com/verystrongdog/game/issues/156)*
