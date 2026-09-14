#!/usr/bin/env bash
# push_file.sh <工程内相对路径> <本地文件路径>
#   把本地文件推进 Windows 侧 Unity 工程（`C:\Users\9527\game\code\unity`）。
#
# 为什么需要它（2026-09-14 实测，代价：两次静默失败）：
#   `uc.sh write_text_file --contents "$(cat 大文件)"` 走的是**命令行参数**，超过 Windows 的
#   命令行长度上限时 unity.exe 直接报 `Invalid argument`（**文件不会被写入**，而 `--confirm true`
#   也不会有别的提示）。实测 38 KB 的 `.cs` 就推不动了（约 20 KB 时还正常）。
#   症状是"改了代码、重编译也过了，行为却完全没变"——极易误判成"Unity 没重编译"。
#
# 做法：本地 base64 → 按 8000 字符切成若干 ASCII 分片 → 逐片 `write_text_file` 成临时 `.txt`
#   → 一条小 `eval` 在 Editor 进程里拼回、base64 解码、写目标文件（Unity 进程有写盘权限；
#   WSL 沙箱对 `/mnt/c` 是只读），最后 `AssetDatabase.Refresh()` 让 Unity 生成 `.meta`。
set -euo pipefail

if [ $# -ne 2 ]; then
  echo "用法: $0 <工程内相对路径> <本地文件路径>" >&2
  exit 2
fi
ASSET_PATH="$1"          # 例: Assets/Scripts/AnimationRiggingProbe.cs
LOCAL_PATH="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"
UC="$HERE/uc.sh"
TMP_DIR="Assets/Animations/Derived/_push"   # 过程物，落在被 gitignore 的 `_` 前缀目录里

B64="$(base64 -w0 "$LOCAL_PATH")"
CHUNK=8000
N=0
while [ -n "$B64" ]; do
  PART="${B64:0:$CHUNK}"
  B64="${B64:$CHUNK}"
  N=$((N + 1))
  "$UC" write_text_file --path "${TMP_DIR}_part_${N}.txt" --contents "$PART" --confirm true >/dev/null
done

"$UC" eval "var sb = new System.Text.StringBuilder(); for (int k = 1; k <= ${N}; k++) sb.Append(System.IO.File.ReadAllText(\"${TMP_DIR}_part_\" + k + \".txt\")); var bytes = System.Convert.FromBase64String(sb.ToString()); System.IO.File.WriteAllText(\"${ASSET_PATH}\", System.Text.Encoding.UTF8.GetString(bytes), new System.Text.UTF8Encoding(false)); UnityEditor.AssetDatabase.Refresh(); return \"pushed ${ASSET_PATH} \" + bytes.Length + \" bytes (\" + ${N} + \" chunks)\";"

# 清理分片
"$UC" eval "for (int k = 1; k <= ${N}; k++) { var p = \"${TMP_DIR}_part_\" + k + \".txt\"; if (System.IO.File.Exists(p)) System.IO.File.Delete(p); if (System.IO.File.Exists(p + \".meta\")) System.IO.File.Delete(p + \".meta\"); } UnityEditor.AssetDatabase.Refresh(); return \"cleaned\";"
