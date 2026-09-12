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

两个脚本里的 `U=` 与 `PS=` 两个路径按本机实际值改。

## 三、常用命令

```bash
./uc.sh status                                     # Editor 端口/工程/版本
./uc.sh recompile && ./uc.sh recompile_status      # 重编译 + 轮询
./uc.sh console --level error --tail 20            # 读控制台
./uc.sh list_tests                                 # 列出测试
./uc.sh run_tests && ./uc.sh test_status           # 跑测试 + 取结果
./uc.sh menu "YANTF/玫瑰实验/创建玫瑰花海场景"        # 执行菜单项（中文路径可）
./uc.sh editor_play ; ./uc.sh editor_stop          # 进出 Play
./uc.sh list_open_scenes                           # 打开的场景 + isDirty
./uc.sh get_scene_hierarchy                        # 场景层级
./shot.sh out.png camera                           # 抓 Game View（实时性见 §四）
```

## 四、⚠️ 三个坑（#126 实测踩过，代价很大）

1. **失焦冻结玩家循环**。`Run In Background` 关闭时，编辑器窗口失焦 → 播放循环停止（`Time.frameCount` 不再增长）。场景照常渲染，但 `Update` 不执行 → 一切动态内容消失，极易误判成「代码没生效」。做 Play 态验证前先在 builder/设置里打开 `PlayerSettings.runInBackground`。
2. **即时模式绘制不进抓帧路径**。`Graphics.DrawMesh / DrawMeshInstanced / RenderMeshInstanced` 不出现在 `capture_game_view --source camera` 的帧里；`source=screen` 多出来的颜色经比对是编辑器 UI 而非场景内容。要被抓到就必须用真实 GameObject 渲染。
3. **截图必须先做帧新鲜度断言**。先改一个必然影响画面的量、连拍两张比 md5；两张相同即冻结帧，此前所有基于截图的结论全部作废。`shot.sh` 已内置「激活窗口 → 再截图」来规避，但不能替代断言。

---
*创建: 2026-09-12 | 更新: 2026-09-12*
*关联: [Grilling #126 决策记录](../../../design/archive/grilling/grilling-126-rosefield/%E5%86%B3%E7%AD%96%E8%AE%B0%E5%BD%95.md), [code/unity/README.md](../../unity/README.md)*
