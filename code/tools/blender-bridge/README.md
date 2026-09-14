# blender-bridge —— 让外部进程驱动**你正开着**的那个 Blender 会话

> 与 [`../unity-cli`](../unity-cli/README.md) 同一地位：**项目自有的直驱桥**。
> 口径正典：[Blender动作制作管线](../../../design/presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md) §7.5 / §7.6。

## 一、它补的是哪一格

| 方式 | 能做什么 | 缺什么 |
|---|---|---|
| `blender --background --python x.py` | 脚本化生成/导出，完全可复现 | 每次都是**新会话**：看不见你手改到一半的场景，也没法让你实时看着它动 |
| **本工具（活体桥）** | 往**你眼前那个窗口**里送代码并读回结果；你实时看见变化 | 需要 Blender 以本桥启动；窗口关了就没了 |

不是替代关系：**量产走 headless 脚本，调试与"我说你动"走活体桥**。

## 二、三步用起来

```bash
# 1) 起（从 WSL；会自动映射 Z:、取 WSL 网卡 IP、设 BB_STATE、把 .blend 排在 --python 前面）
./code/tools/blender-bridge/bb-launch.sh
#    → LAUNCHED host=172.25.48.1 port=9878
#    → [bb] Blender 5.1.2 · 172.25.48.1:9878 · filepath='Z:\...\XBot_AnimationTemplate.blend'

# 2) 问它一句话
./code/tools/blender-bridge/bb.py 'bpy.data.filepath'

# 3) 多行代码（按 exec 跑，print 会被一并回传）
./code/tools/blender-bridge/bb.py @my_probe.py
```

`bb.py` 的 host/port/token **一律从状态文件读**（由 addon 启动时写），不硬编码、不靠猜：

```json
{"host": "172.25.48.1", "port": 9878, "token": "…", "blender": "5.1.2",
 "pid": 32888, "filepath": "Z:\\…\\XBot_AnimationTemplate.blend", "objects": ["Armature", …]}
```

### 手动启动（不经 `bb-launch.sh`）

```powershell
net use Z: \\wsl.localhost\Ubuntu-22.04
$env:BB_HOST  = (Get-NetIPAddress -AddressFamily IPv4 |
                 Where-Object { $_.InterfaceAlias -like '*WSL*' } | Select -First 1 -ExpandProperty IPAddress)
$env:BB_STATE = 'Z:\home\dog\game\.scratch\blender-bridge.json'
Start-Process "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" `
  -ArgumentList 'Z:\home\dog\game\.scratch\blender_assets\xbot\XBot_AnimationTemplate.blend',
                '--python', "$env:TEMP\blender_ai_bridge.py"
# 然后客户端： BB_STATE=/home/dog/game/.scratch/blender-bridge.json bb.py '…'
```

也可以装成 addon：把 `blender_ai_bridge.py` 放进 `<Blender>/scripts/addons/`，在偏好设置里启用即监听（`register()`）。

## 三、协议

一行一条 JSON 请求，回一行 JSON。

| 字段 | 说明 |
|---|---|
| `code` | 要跑的代码。`mode=eval` 时是**表达式**（返回值即结果）；`mode=exec` 时是多行语句，用 `__result__` 交出返回值 |
| `mode` | `eval`（默认）/ `exec` |
| `token` | 必须与状态文件里的一致，否则回 `token mismatch` |
| `timeout` | 秒；`bb.py` 固定发 60 |

回包：`{"ok":true,"result":…,"stdout":…}` 或 `{"ok":false,"error":…,"trace":…}`。
`exec` 模式会**捕获 print**（省得再写中间文件）；结果字符串封顶 20 000 字符，超了会标"截断"。

## 四、⚠️ 安全与边界（先读再开）

1. **它执行任意 Python**，且**没有任何沙箱**——等于把那个 Blender 进程的全部能力交出去。
2. 门禁只有一道：**token**（启动时随机生成，写进状态文件）。谁读得到状态文件，谁就能驱动。
   ⇒ 状态文件别提交、别放共享盘。
3. **默认只绑 `127.0.0.1`**（WSL 连不进来是有意的）。要从 WSL 连必须显式把 `BB_HOST` 设成
   WSL 网卡在 Windows 侧的 IP —— 那样**同网段的其他机器也能连**（只要有 token）。用完关掉窗口即可。
4. **不是长驻服务**：Blender 一关，桥就没了（这正是"活体"的含义，也别拿它当自动化后端）。

## 五、⚠️ 五条实测坑（都在[危险点表](../../../design/engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md) §七 有行）

| 坑 | 判据 | 规避 |
|---|---|---|
| bash 双引号把 `\\` 折成 `\` ⇒ UNC 退化成相对路径 ⇒ **Blender 静默回落默认立方体场景** | 输出里 `path=C:\Windows\wsl.localhost\...`；画面是默认 Cube | 路径用**单引号**或 `Z:` 盘符（`bb-launch.sh` 已处理） |
| `--python` 排在 `.blend` **之前** ⇒ 脚本先于加载运行 | `bpy.data.filepath` 为**空串**、`objects=['Camera','Cube','Light']` | **`.blend` 放最前**（`bb-launch.sh` 已处理） |
| UNC 形式的 `--python` 参数 Blender **吃不到**（脚本没跑，窗口是"未命名"） | 状态文件不出现 | 先把脚本 `Copy-Item` 到 Windows 本地（`%TEMP%`）再传（`bb-launch.sh` 已处理） |
| `cmd /c start` 起 GUI 会让**调用方等 EOF** 到超时 | 命令卡满超时，而进程其实已独立运行 | 用 `Start-Process`（实测 0.54 s 返回） |
| `bpy.ops.screen.screenshot` 抓到**重绘前**的帧（连拍两张字节相同）；且 GUI 截图**本就不逐位可复现** | 两张 `md5` 相同 | 截图前 `bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP")`；像素判据只比**量级与位置** |

## 六、为什么不用现成的 Blender MCP

Blender 的 MCP 生态是有的（[harveyxiacn/blender-mcp](https://github.com/harveyxiacn/blender-mcp)、
[Blender_mcp](https://github.com/Immunogenic-prismspectroscope589/Blender_mcp)、
[blender-mcp-bridge](https://pypi.org/project/blender-mcp-bridge/)、[blender-agent](https://projects.blender.org/Rich-Siomporas/blender-agent)），
且 DSH 支持 MCP（`@deepseek-ai/dsh-mcp-client`，stdio；工具以 `mcp__<server>__<tool>` 形式出现）。
不选它的理由**具体**，不是偏好：

1. **内核是同一件事**——那类 MCP 的 Blender 侧也是一个监听 socket 的插件，本工具 120 行就覆盖了本工程要用的那一格；
2. **多一层第三方依赖**：要装、要跟版本、要信任其代码；本机还没有 `uv`/`uvx`；
3. **MCP 工具只在新会话里出现**——"现在这个会话里帮我摆个姿势"它答不了；
4. **本工程已有先例**：[`../unity-cli`](../unity-cli/README.md) 就是自建直驱桥，同一套思路、同一套坑表。

> 若将来要接 MCP（例如让别的编辑器客户端也能控 Blender），**本 addon 可以直接当它的后端**，不必重写。

---
*创建: 2026-09-14 | 关联: [Blender动作制作管线](../../../design/presentation/Blender%E5%8A%A8%E4%BD%9C%E5%88%B6%E4%BD%9C%E7%AE%A1%E7%BA%BF.md), [unity-cli](../unity-cli/README.md), [危险点表](../../../design/engineering/%E5%8D%B1%E9%99%A9%E7%82%B9%E8%A1%A8.md)*
