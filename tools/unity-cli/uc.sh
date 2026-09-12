#!/usr/bin/env bash
# uc.sh <unity command> [args...] — 调 Unity CLI 并打印结构化 JSON 结果
# 前置与坑见同目录 README.md
set -uo pipefail
U="${UNITY_CLI:-/mnt/c/Users/9527/AppData/Local/Unity/bin/unity.exe}"
timeout "${UCMD_TIMEOUT:-180}" "$U" command "$@" 2>&1 | python3 -c '
import sys, json
raw = sys.stdin.read()
i = raw.find("{")
if i < 0:
    print(raw[:3000]); sys.exit(0)
try:
    obj, _ = json.JSONDecoder().raw_decode(raw[i:])
except Exception as e:
    print("PARSE-FAIL:", e); print(raw[:3000]); sys.exit(0)
print(json.dumps(obj, ensure_ascii=False, indent=1))
'
