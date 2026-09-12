#!/usr/bin/env bash
# shot.sh <输出png> [camera|screen] — 激活 Unity 窗口后抓 Game View，规避冻结帧
# ⚠️ 仍建议自己做帧新鲜度断言（连拍两张比 md5），见同目录 README.md §四
set -uo pipefail
U="${UNITY_CLI:-/mnt/c/Users/9527/AppData/Local/Unity/bin/unity.exe}"
PS="${POWERSHELL:-/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe}"
PROJ_WIN="${UNITY_PROJECT_WIN:-C:\\Users\\9527\\game\\unity}"
PROJ_WSL="${UNITY_PROJECT_WSL:-/mnt/c/Users/9527/game/unity}"
OUT="${1:?用法: shot.sh <输出png> [camera|screen]}"
SRC="${2:-camera}"
"$PS" -NoProfile -Command "\$p = Get-Process Unity -ErrorAction SilentlyContinue | Where-Object { \$_.MainWindowTitle -ne '' } | Select-Object -First 1; if (\$p) { (New-Object -ComObject WScript.Shell).AppActivate(\$p.Id) | Out-Null }" >/dev/null 2>&1
sleep 2
timeout 120 "$U" command capture_game_view --save_path 'Assets/_shot.png' --source "$SRC" 2>&1 | grep -o '"savedPath":[^,]*'
sleep 1
cp "$PROJ_WSL/Assets/_shot.png" "$OUT" && md5sum "$OUT"
