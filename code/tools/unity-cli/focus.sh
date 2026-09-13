#!/usr/bin/env bash
# focus.sh — 把 Windows 侧 Unity Editor 窗口切到前台（WSL interop）
#
# 为什么需要它（2026-09-13 实测，代价很大）：**Unity 6 在 Editor 窗口位于后台时会节流主线程**，
# 于是 `unity command ...` 全部报「Main thread operation timed out after 30000ms」，
# 而 `unity status` 仍回 ready（健康检查走后台线程）——看起来像 Editor 卡死，其实是没在前台。
# `editor_focus` 自己也走主线程，所以节流后它同样超时：必须从 Windows 侧把窗口调到前台。
#
# 用法： ./focus.sh          # 取 `unity status` 里的 PID 并置前
#        ./focus.sh <pid>
set -uo pipefail
U="${UNITY_CLI:-/mnt/c/Users/9527/AppData/Local/Unity/bin/unity.exe}"
PS="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"

PID_ARG="${1:-}"
if [ -z "$PID_ARG" ]; then
  PID_ARG=$(timeout 60 "$U" status 2>/dev/null | awk -F'\t' 'NR==2 {print $5}')
fi
if [ -z "${PID_ARG:-}" ]; then
  echo "取不到 Unity PID：先跑 '$U status' 确认 Editor 在线" >&2
  exit 1
fi

TMP=$(mktemp /tmp/dsh-focus-XXXX.ps1)
cat > "$TMP" <<EOF
\$sig = '[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);'
\$t = Add-Type -MemberDefinition \$sig -Name 'WinFocus' -Namespace 'Dsh' -PassThru
\$p = Get-Process -Id $PID_ARG
\$h = \$p.MainWindowHandle
\$t::ShowWindow(\$h, 9) | Out-Null
\$t::BringWindowToTop(\$h) | Out-Null
\$r = \$t::SetForegroundWindow(\$h)
Write-Output ("pid=$PID_ARG handle=" + \$h + " foreground=" + \$r + " title=" + \$p.MainWindowTitle)
EOF

ENC=$(python3 - "$TMP" <<'PY'
import base64, sys
print(base64.b64encode(open(sys.argv[1], encoding='utf-8').read().encode('utf-16-le')).decode())
PY
)
rm -f "$TMP"
"$PS" -NoProfile -EncodedCommand "$ENC" 2>/dev/null | tr -d '\r' | grep -E '^pid='
