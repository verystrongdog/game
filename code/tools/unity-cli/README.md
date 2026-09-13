# Unity CLI 直驱工具

> 在 WSL 侧驱动 Windows 上的 Unity Editor（`com.unity.pipeline`）做编译 / 生成 / 测试 / 截图验证的封装脚本。首次使用见 [Grilling #126 决策记录](../../../design/archive/grilling/grilling-126-rosefield/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md) §本机实测。

## 一、前置

| 项 | 要求 |
|----|------|
| Unity CLI | `C:\Users\<你>\AppData\Local\Unity\bin\unity.exe`（`unity status` 能列出 Editor） |
| Pipeline 包 | 工程 `Packages/manifest.json` 含 `com.unity.pipeline` |
| Editor | 已打开目标工程并处于 `ready`（`unity status` 的 `State` 列） |
| Project root 约束 | `capture_game_view --save_path` 必须落在工程根目录内，否则 400 |

## 二、脚本

| 脚本 | 用途 |
|------|------|
| `uc.sh <命令> [参数...]` | 调 `unity command <命令>` 并打印结构化 JSON 结果 |
| `shot.sh <输出名> [camera\|screen]` | 激活 Unity 窗口后截图到工作区（规避冻结帧） |
| `focus.sh [pid]` | **把 Editor 窗口调到前台**——后台节流时（见 §四 坑 4）唯一能救回命令通道的手段 |

两个脚本里的 `U=` 与 `PS=` 两个路径按本机实际值改。

## 三、常用命令

```bash
./uc.sh status                                     # Editor 端口/工程/版本
./uc.sh recompile && ./uc.sh recompile_status      # 重编译 + 轮询
./uc.sh console --level error --tail 20            # 读控制台
./uc.sh list_tests                                 # 列出测试
./uc.sh run_tests && ./uc.sh test_status           # 跑测试 + 取结果
./uc.sh menu "YANTF/动作演示/创建 ActionLab 场景"      # 执行菜单项（中文路径可）
./uc.sh editor_play ; ./uc.sh editor_stop          # 进出 Play
./uc.sh list_open_scenes                           # 打开的场景 + isDirty
./uc.sh get_scene_hierarchy                        # 场景层级
./shot.sh out.png camera                           # 抓 Game View（实时性见 §四）
```

## 四、⚠️ 五个坑（#126 / #137 / #141 实测踩过，代价很大）

1. **失焦冻结玩家循环**。`Run In Background` 关闭时，编辑器窗口失焦 → 播放循环停止（`Time.frameCount` 不再增长）。场景照常渲染，但 `Update` 不执行 → 一切动态内容消失，极易误判成「代码没生效」。做 Play 态验证前先在 builder/设置里打开 `PlayerSettings.runInBackground`。
2. **Error Pause 同样会冻结循环——且症状与坑 1 逐项相同**（#137 实测，2026-09-12）。Console 出现 `LogError` 时，若 Console 面板的 **Error Pause** 开着，Editor 会**自动暂停** Play：`Time.frameCount` 冻住、`isPlaying` 仍 `True`、`Application.runInBackground` 仍 `True`、`editor_focus` 也救不回来。
   - **一步定位**：读 `UnityEditor.EditorApplication.isPaused`。为 `True` 就是这条，不是失焦。
   - **解**：`unity command editor_pause`（切换暂停态）恢复；并去 Console 面板关掉 Error Pause，或先消除产生 `LogError` 的那次调用。
   - 典型诱发源：`Destroy()` 一个被 `[RequireComponent]` 约束的组件（例：销毁 `CharacterController` 而 `ActionLabDriver` 依赖它）。
3. **即时模式绘制不进抓帧路径**。`Graphics.DrawMesh / DrawMeshInstanced / RenderMeshInstanced` 不出现在 `capture_game_view --source camera` 的帧里；`source=screen` 多出来的颜色经比对是编辑器 UI 而非场景内容。要被抓到就必须用真实 GameObject 渲染。
4. **后台节流：Unity 6 在 Editor 窗口不处于前台时会节流主线程**（#141 实测，2026-09-13）。症状极具误导性——`unity status` 仍回 `ready`（健康检查走后台线程），但**所有 `unity command` 一律报**「Main thread operation timed out after 30000ms」；`unity.exe status` 的 PID/工程都正常、进程 CPU 占用近 0、`Responding=True`，看起来像 Editor 卡死或 pipeline 坏了。
   - **判据**：`Get-Process -Id <pid> | Select CPU` 连测两次，5 s 内增量 ≈ 0 而窗口不在前台 → 就是这条。**`editor_focus` 救不回来**（它自己也走主线程），必须在 Windows 侧调窗口。
   - **解**：`./focus.sh`（Windows 侧 `SetForegroundWindow`，见 §二 脚本表）；此后命令立即恢复。
   - 连带影响：**Play 态测试跑一半被节流会挂住**（测试框架靠帧推进）——跑 `run_tests` 前先 focus，跑完再取结果；挂住时 `cancel_tests` + 重新跑。
5. **截图必须先做帧新鲜度断言**。先改一个必然影响画面的量、连拍两张比 md5；两张相同即冻结帧，此前所有基于截图的结论全部作废。`shot.sh` 已内置「激活窗口 → 再截图」来规避，但不能替代断言。

## 五、比截图更可靠的判据：确定性姿势求值

Play 态验证若只为读「某个动作在某时刻的姿势」，**不必开 Play 循环、不必截图**——`Animator.Play(state, layer, normalizedTime)` + `Animator.Update(0f)` 可在**同一帧内**确定性求值任意 clip 的任意时刻，再用 `GetBoneTransform(HumanBodyBones.*)` 读骨骼几何量（足底最低点、膝角、躯干倾角、髋落点）。优点：不受坑 1 / 坑 2 影响、无 interop 延迟、可写进机械断言。

**两个注意**：

- **IK 不在这一路径上求值**。`OnAnimatorIK` 由玩家循环驱动，且 `Animator.SetIKPosition` **不是持久状态**（Unity 每帧重置）——从 eval 里设一次无效（实测跨真实帧读数逐位不变），必须由真实 `MonoBehaviour` 逐帧设置。要验 IK 就得开 Play 循环逐帧读，且中间姿势需要 `Animator.speed = 0` 冻结。
- **非循环状态的末帧姿势可跨帧稳定**（时间停在末尾），所以末帧可以直接用「Play 到 t=1 → 等几帧 → 读」验，不必冻结。

---
*创建: 2026-09-12 | 更新: 2026-09-13（#141 实测：加"后台节流"坑 + `focus.sh` + 修正 `shot.sh` 的工程路径 `unity/` → `code/unity/`；#137 实测：加 Error Pause 坑 + 新增 §五 确定性姿势求值）*
*关联: [Grilling #126 决策记录](../../../design/archive/grilling/grilling-126-rosefield/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md), [code/unity/README.md](../../unity/README.md)*
