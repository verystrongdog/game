# 活体桥预览回路证据（桥内直跑可行性 · 三处前置改造）

> [#162](https://github.com/verystrongdog/game/issues/162) 的收口证据。口径落法见
> [动作描述口径](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) §九；
> 必填字段按 [阶段证据说明](README.md) 与 [WORKFLOW.md §五/§六](../../../WORKFLOW.md) 记录。

## 一、结论（先读这一段）

| 项 | 值 |
|---|---|
| 达成 | 能力增量：`动作描述口径（人机协作接口）` · Implementation **保持 `PARTIAL`**（本条补的是**预览回路**这一格；该行已在 [#160](https://github.com/verystrongdog/game/issues/160) 由 `NONE → PARTIAL`） |
| 一句话 | **"关掉再打开 Blender"这条回路在技术上去掉了**：真实产姿势的脚本可以在**已开着的会话**里跑完（实测 **66.96 s**）、大输出不丢（48172 字符落文件）、起桥**不再杀已有窗口**、且活体结果与 headless **逐位一致** |
| 判定 | **支持**（6 条验收全过，见 §五） |
| 代价（必须一起读） | 长任务期间 **Blender 主线程被占满 ⇒ GUI 冻结**（实测 67 s）；**超时不取消脚本**；**桥自身升级仍要重起会话**（§六.4） |
| 未做的事 | owner **目视确认**（"当场看到姿势变化"这一半由 agent 侧读数替代，见 §四.1）；未做多动作并行；未接 MCP |

## 二、绑定

| 字段 | 值 |
|---|---|
| base SHA | `4c9dbe8`（#161 收口提交） |
| head SHA | 本回填提交（桥三件改造 + 口径 §九 + README + 证据） |
| 阶段 | [#162](https://github.com/verystrongdog/game/issues/162)（Experiment） |
| 执行者 | DSH agent（本机 WSL → Windows 侧 Blender） |
| 工具版本 | Blender **5.1.2**（`hash ec6e62d40fa9`）· Windows 11 家庭中文版 · Python 3.10.12 · gh 2.100.0 |
| 被测对象 | 母版 `.scratch/blender_assets/xbot/XBot_AnimationTemplate.blend`（`5601197` 字节）· 骨架 `Armature`（78 骨）· 蒙皮网格 `Beta_Joints`/`Beta_Surface` |
| 会话形态 | Windows 侧 GUI（`bb-launch.sh` 起，端口 9878；**测试结束时留着一个桥会话**，owner 可自行关闭） |

## 三、命令与退出码

| 命令 | 退出码 / 结果 |
|---|---|
| `./code/tools/blender-bridge/bb-launch.sh`（默认，已有活桥） | **0** —— 打印"**复用它**，不再启动新窗口"；进程数 **2 → 2**（未动任何窗口） |
| `BB_KILL_EXISTING=1 ./code/tools/blender-bridge/bb-launch.sh`（旧行为，现为显式开关） | **0** —— `KILLED_EXISTING` + `LAUNCHED`；进程数 **2 → 1** |
| `bb.py --timeout 20 @.scratch/live_pose_task.py`（长任务） | **1** —— 客户端 19.7 s 收到应用层 `{"error":"timeout"}` 并给出**明确提示**（不是"连不上"） |
| `bb.py --timeout 240 --raw @.scratch/live_pose_task.py`（同一任务） | **0** —— 任务 **66.96 s** 跑完，`__result__` 与 48172 字符 stdout 都拿到 |
| headless 对照：`blender --background --factory-startup --python-exit-code 1 --python live_pose_task.py` | **0** —— 同一段代码、同一组读数 |
| `python3 code/tools/validate_cross_refs.py` / `validate_trash_isolation.py` / `validate_params.py` | **0 / 0 / 0** |

**测试样本**（过程物、gitignore）：`.scratch/live_pose_task.py`（21 行有效载荷：重置姿势 → 转 `CTRL_LeftArm` Z+40° → 读回左手世界坐标 → 23000 次逐顶点计算 ≈ 67 s → 打印 48172 字符）。

## 四、读数

### 4.1 真实产姿势的脚本在已开会话里跑完（验收 1）

| 项 | 值 |
|---|---|
| 姿势确实变了 | 左手世界坐标 `(0.713332, 0.055485, 1.440612)` → `(0.581918, −0.305571, 1.440612)` ⇒ 位移 **384.2 mm** |
| 独立复现 | [blender-bridge README](../../../code/tools/blender-bridge/README.md) §二 记的"摆 `CTRL_LeftArm` Z+40° → 左手位移 **384.2 mm**"——本次独立量得 **0.38423 m**，一致 |
| 任务时长 | **66.96 s**（`ITERS=23000`，每次 2.78–3.04 ms） |
| ⚠️ owner 目视这一半 | **未做**（agent 不在 owner 的屏幕前）——本表用"骨骼世界坐标变化"替代，属**读数替代，不是目视替代** |

### 4.2 长任务不再被 60 s 掐断（验收 2）

| 档 | 结果 |
|---|---|
| 改前（写死 `timeout: 60` + socket 65） | 67 s 的任务**必被掐**，且客户端只看到"连不上/超时"，与脚本自身报错**分不开** |
| 改后 `--timeout 20` | 19.7 s 返回 `{"error":"timeout"}` + 明确提示"**不是脚本报错**…脚本仍在会话里继续跑" |
| 改后 `--timeout 240` | **66.96 s 完整跑完**，`ok: true` |

### 4.3 大输出不丢（验收 3）

| 项 | 值 |
|---|---|
| 输出长度 | **48172 字符**（> 旧上限 20000） |
| 回包 | `stdout` = **前 20000 字符 + "已截断"标记**；附 `stdout_file_name` / `stdout_file` / `stdout_chars` |
| 落点 | `.scratch/bb-outbox/bb-out-<rid>-stdout.txt`（**状态文件同级目录**——客户端本来就要读状态文件，故不必猜任何 Windows 路径） |
| 客户端 | 打印 WSL 侧完整路径：`/home/dog/game/.scratch/bb-outbox/bb-out-6bb2b8335fc6-stdout.txt` |
| ⚠️ 改前的另一个毛病 | 旧代码 `captured[-MAX_RESULT:]` 只留**尾部** 20000 字符 ⇒ **长报告的开头被吃掉**（比截断更坏：看到的是一份"从中间开始"的报告）。现在改成留**头** + 全文落文件 |

### 4.4 起桥不再杀已有窗口（验收 4）

| 行为 | 命令 | 进程数 |
|---|---|---|
| **新默认** | `./bb-launch.sh` | 有一个活桥时：**复用**（2 → 2，不新开窗口）；无活桥但有别的 Blender 时：`LEAVE_EXISTING=<n>` + 起新会话 |
| **旧行为**（现为显式开关） | `BB_KILL_EXISTING=1 ./bb-launch.sh` | 2 → 1（`KILLED_EXISTING`） |

### 4.5 活体 vs headless 对拍（验收 5）

| 宿主 | `before` | `after` | 一致？ |
|---|---|---|---|
| headless（`--background`，权威侧） | `(0.713332, 0.055485, 1.440612)` | `(0.581918, −0.305571, 1.440612)` | — |
| 活体（桥内，已开会话） | `(0.713332, 0.055485, 1.440612)` | `(0.581918, −0.305571, 1.440612)` | ✅ **逐位相同**（6 位小数全同） |

⇒ 口径 §九 的"预览回路 / 产出回路"在**这段代码**上**没有系统性差异**；差异只出现在耗时（0.61 s vs 0.66 s，计时噪声）。

## 五、判定标准（三种结局的评估）

| 结局 | 是否命中 | 依据 |
|---|---|---|
| **支持** | ✅ | 6 条验收全过；对拍逐位一致；"预览只能定性"的顾虑**未成立**（对该类代码） |
| 否定 | ✗ | 同进程结果与 headless 一致 |
| 证据不足 | ✗ | 两遍运行读数稳定；对拍逐位相同 |

**但"支持"带三条边界**（写进口径 §九 与 §七）：① 长任务冻结 GUI；② 超时不取消；③ 桥自身升级要重起会话。

## 六、六条实测发现（全部当场付了代价）

1. **客户端 `rid` 写死为 1 ⇒ 超时残留结果污染下一次请求**（最严重，属**静默错误**）。
   现象：一次超时后，**下一次**请求**瞬间**返回上一次的输出，且 `ok: true`——探针请求"秒回"了一个 67.6 s 任务的结果。
   根因：服务端按 `rid` 存结果，而客户端每次都用 `id: 1`。**已修**：客户端 `uuid4().hex[:12]`；服务端按 TTL 600 s 清理未取走的结果。
2. **客户端 socket 超时贴太近 ⇒ "超时"退化成"连不上"**。第一版 socket 超时 = 应用超时 + 5 s，而服务端的等待是"轮询次数 × 0.05"、在 CPU 密集脚本下**漂移**（实测 20 s 的档位耗掉 >24 s）⇒ 回包比客户端放弃还晚。
   **已修**：服务端改用**单调时钟死线**；客户端 socket 超时 = 应用超时 **+ 30 s**。
3. **从 WSL 起 Windows 进程时，bash 的环境变量不会自动传进 PowerShell**（实测 `BB_KILL_EXISTING=1 ./bb-launch.sh` 里 PowerShell 看到的是**空串** ⇒ 开关**静默失效**，于是"清场"没发生，进程数 2→3）。
   **已修**：在 **bash 侧**取值再嵌进命令串（同 `$PORT` 的既有写法）。
4. **addon 原地热升级不可靠**：用桥把新版本 `exec` 进 `__main__` 并重启监听**看似成功**（打印 `started=True`），但随后请求 `token mismatch` / 无响应——Windows 的 `SO_REUSEADDR` 允许**旧监听器继续占着端口**，新旧服务端并存。
   ⇒ **升级桥自身仍需重起会话**；但**改母版/摆姿势不需要**（这才是"零重开"的收益所在）。
5. **状态文件路径两边不一致**：`bb-launch.sh` 写**仓库** `.scratch/blender-bridge.json`，而 `bb.py` 默认找**自己同级目录** ⇒ "桥明明活着、客户端却说读不到状态文件"。**已修**：加兜底路径。
6. **服务端不取消在飞脚本**：超时后脚本继续跑（本次实测 66.96 s 的那个在超时后仍跑完并把结果留在 pending 里）。这既是特性（长任务不会白跑）也是陷阱（须靠发现 1 的修复兜住污染）。

## 七、问题差分

`new_finding = after − mapped(before) − expected_delta` = **空**。

| 检查 | 结果 |
|---|---|
| 预期差分内的文件 | `code/tools/blender-bridge/bb.py`（改） · `blender_ai_bridge.py`（改） · `bb-launch.sh`（改） · `README.md`（改，§三/§五） · `design/presentation/动作描述口径.md`（改，§九 + §十一 U5） · `design/engineering/evidence/action-description-live-loop-2026-09-14.md`（新增；⚠️ 文件名比 #162 预期差分写的 `action-description-live-loop.md` 多带日期，遵循 `<阶段>-<日期>.md` 约定） · [阶段证据说明](README.md)（登记） · `design/slices/CP-01-ward-1f/slice.md`（🔧 注释一行） |
| 计划外变化 | 无（桥的 **token 门禁与安全边界**（管线 §7.6）**一个字未动**；headless 脚本未动；母版未动） |
| 预期不变项 | `build_xbot_animation_template.py` / `export_xbot_action.py` 未改 · 母版与源 FBX 字节未变 |
| 工作树 | 提交后干净 |
| **回滚演练** | ✅ 已演练：`git revert --no-commit HEAD` 后三个校验器仍绿，`git reset --mixed HEAD && git checkout -- .` 后工作树干净 ⇒ 回滚恢复上一状态成立 |

**测试报告定位**：`.scratch/live_pose_task.py`（样本）· `.scratch/bb-outbox/*.txt`（48172 字符输出）· `.scratch/blender-bridge.json`（活会话状态）；复现命令见 §三。

## 八、未闭合（诚实清单）

| # | 项 |
|---|---|
| 1 | **长任务冻结 GUI**（实测 67 s）——`bpy` 只能在主线程调（桥的设计前提），故任何>200 ms 的脚本都会让画面卡住。**缓解方向未做**：分片（每片一个请求）或后台线程 + 进度回传 |
| 2 | **超时不取消脚本**（发现 6）：没有取消通道 |
| 3 | **桥自身升级仍需重起会话**（发现 4）：未做"干净换监听"的机制（需要真正释放端口并确认旧监听已死） |
| 4 | **owner 目视未做**：§四.1 的"当场看到姿势变化"只有 agent 侧读数 |
| 5 | 未做**多动作并行 / 长驻服务**（口径 §九 的明确排除） |
| 6 | 母版里**残留撤回动作的 `REF_*` 代理**（同 [#160](https://github.com/verystrongdog/game/issues/160) 证据 §二）未清理 |

## 九、来源

| 事实 | 来源 |
|---|---|
| 双回路（预览 / 产出）与"姿势单一写者" | [动作描述口径](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) §九 |
| 桥的协议、五条坑、安全边界 | [blender-bridge README](../../../code/tools/blender-bridge/README.md) §三/§五 · [管线 §7.5/§7.6](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) |
| "摆 `CTRL_LeftArm` Z+40° → 左手 384.2 mm" 的既有读数 | 同 README §二 |
| `--factory-startup` 是可复现前提 | [管线 §7.1](../../presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) |
| 全部读数与六条发现 | 本条实测（Blender 5.1.2，2026-09-14） |

---
*创建: 2026-09-14（agent 执行 [#162](https://github.com/verystrongdog/game/issues/162)）*
*状态: 收口证据——判定**支持**，三条边界见 §五；未闭合 6 项见 §八*
*关联: [#162](https://github.com/verystrongdog/game/issues/162) · [#160](https://github.com/verystrongdog/game/issues/160) · [#163](https://github.com/verystrongdog/game/issues/163) · [动作描述口径](../../presentation/%E5%8A%A8%E4%BD%9C%E6%8F%8F%E8%BF%B0%E5%8F%A3%E5%BE%84.md) §九 · [blender-bridge README](../../../code/tools/blender-bridge/README.md)*
