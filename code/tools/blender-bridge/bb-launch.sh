#!/usr/bin/env bash
# bb-launch.sh [母版.blend] —— 从 WSL 启动 Windows 侧 Blender GUI 并挂上活体桥。
#
# 它替你做掉四件容易踩的事（每一条都对应危险点表 §七 的一行）：
#   1. `net use Z:` 把 WSL 目录映射成盘符——**不要**把 UNC 直接塞进命令行：
#      bash 双引号会把 `\\` 折成 `\`，路径退化成相对路径，Blender 静默回落默认场景。
#   2. 取 **WSL 网卡在 Windows 侧的 IP** 当 BB_HOST——默认 127.0.0.1 时 WSL 连不进来。
#   3. 状态文件写到 **仓库可见** 的路径（BB_STATE），客户端读它拿 host/port/token。
#   4. 把 addon 脚本拷到 Windows 本地再 `--python`（UNC 形式的 `--python` 参数 Blender 吃不到），
#      且 **.blend 必须排在 `--python` 前面**（否则脚本先于加载运行，看到的是默认场景）。
#
# ⚠️ **不再默认杀掉已有的 Blender**（2026-09-14 改，issue #162 验收标准 4）：原先无条件
#    `Stop-Process -Force`，于是"起桥"这个动作本身就会掐掉你正开着的会话——那样"零重开"永远
#    无从谈起。现在默认**保留**已有进程（并打印 `LEAVE_EXISTING=<n>`）；确实要清场时显式给
#    `BB_KILL_EXISTING=1`。
#
# 用法：
#   ./bb-launch.sh                                  # 用默认母版（保留已开的 Blender）
#   ./bb-launch.sh /path/to/别的.blend              # 指定文件
#   BB_KILL_EXISTING=1 ./bb-launch.sh               # 先杀光已有 Blender 再起（回归到旧行为）
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_WSL="$(cd "$HERE/../../.." && pwd)"
REPO_WIN='Z:\home\dog\game'                       # 由 net use Z: 建立
BLENDER_WIN="${BB_BLENDER:-C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe}"
BLEND_WSL="${1:-$REPO_WSL/.scratch/blender_assets/xbot/XBot_AnimationTemplate.blend}"
STATE_WSL="$REPO_WSL/.scratch/blender-bridge.json"
STATE_WIN="$REPO_WIN\\.scratch\\blender-bridge.json"
PORT="${BB_PORT:-9878}"
# ⚠️ **必须在这里（bash 侧）取值**：从 WSL 起 Windows 进程时，bash 的环境变量**不会自动传进
#    PowerShell**（实测：`BB_KILL_EXISTING=1 ./bb-launch.sh` 里 PowerShell 看到的是空串 ⇒ 开关静默失效，
#    2026-09-14 踩到）。要传变量得走 WSLENV，或者像 `$PORT` 这样在这里拼进命令串。
KILL_EXISTING="${BB_KILL_EXISTING:-0}"

case "$BLEND_WSL" in
  "$REPO_WSL"/*) BLEND_WIN="$REPO_WIN${BLEND_WSL#$REPO_WSL}"; BLEND_WIN="${BLEND_WIN//\//\\}" ;;
  *) echo "[bb] 母版必须在仓库内（否则 Z: 映射不到）：$BLEND_WSL" >&2; exit 2 ;;
esac
[ -f "$BLEND_WSL" ] || { echo "[bb] 母版不存在：$BLEND_WSL" >&2; exit 2; }

PS="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
[ -x "$PS" ] || { echo "[bb] 找不到 PowerShell（不是在 WSL 里？）" >&2; exit 2; }

# ⚠️ 端口是**单个**的：既然默认不再杀已有 Blender，就必须先判"是否已有一个**活着的桥**"——
#    否则第二个会话抢同一个端口会绑定失败，而它临死前又把状态文件删了，客户端反而连不上。
#    ⇒ 已有活桥就**复用**（这正是"零重开"想要的行为），不再起新窗口。
if [ "$KILL_EXISTING" != "1" ] && [ -f "$STATE_WSL" ]; then   # 显式清场时不复用
  if BB_STATE="$STATE_WSL" timeout 20 python3 "$HERE/bb.py" --timeout 15 'bpy.data.filepath' >/dev/null 2>&1; then
    echo "[bb] 已有一个活着的桥在跑——**复用它**，不再启动新窗口（要强制重起：BB_KILL_EXISTING=1）"
    python3 -c "import json,sys;d=json.load(open(sys.argv[1],encoding='utf-8'));print('[bb] pid=%s · %s:%s · filepath=%r' % (d['pid'], d['host'], d['port'], d['filepath']))" "$STATE_WSL"
    exit 0
  fi
  echo "[bb] 状态文件在、但桥没响应（stale）——重起"
fi
rm -f "$STATE_WSL"

"$PS" -NoProfile -Command "
  if (-not (Test-Path 'Z:\home\dog\game')) { net use Z: \\\\wsl.localhost\\Ubuntu-22.04 | Out-Null }
  \$ip = (Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
          Where-Object { \$_.InterfaceAlias -like '*WSL*' -and \$_.IPAddress -notlike '169.*' } |
          Select-Object -First 1 -ExpandProperty IPAddress)
  if (-not \$ip) { Write-Output 'NO_WSL_IP'; exit 3 }
  if ('$KILL_EXISTING' -eq '1') {
    Get-Process blender -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Milliseconds 900
    Write-Output 'KILLED_EXISTING'
  } else {
    \$n = @(Get-Process blender -ErrorAction SilentlyContinue).Count
    if (\$n -gt 0) { Write-Output ('LEAVE_EXISTING=' + \$n) }
  }
  Copy-Item 'Z:\home\dog\game\code\tools\blender-bridge\blender_ai_bridge.py' \$env:TEMP\blender_ai_bridge.py -Force
  \$env:BB_HOST = \$ip; \$env:BB_PORT = '$PORT'; \$env:BB_STATE = '$STATE_WIN'
  Start-Process -FilePath '$BLENDER_WIN' -ArgumentList '$BLEND_WIN', '--python', (\$env:TEMP + '\blender_ai_bridge.py')
  Write-Output ('LAUNCHED host=' + \$ip + ' port=' + $PORT)
" 2>&1 | tail -2

for _ in $(seq 1 40); do
  [ -f "$STATE_WSL" ] && break
  sleep 1
done
if [ ! -f "$STATE_WSL" ]; then
  echo "[bb] 桥没起来（等 40 s）。检查：母版路径 / Blender 路径 / 状态文件 $STATE_WSL" >&2
  exit 4
fi
echo "[bb] 状态文件：$STATE_WSL"
python3 -c "import json,sys;d=json.load(open(sys.argv[1],encoding='utf-8'));print('[bb] Blender %s · %s:%s · filepath=%r' % (d['blender'], d['host'], d['port'], d['filepath']))" "$STATE_WSL"
BB_STATE="$STATE_WSL" python3 "$HERE/bb.py" "'bridge ok: ' + str([o.name for o in bpy.data.objects])"
