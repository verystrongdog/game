#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bb.py —— blender-bridge 的**客户端**：把一段代码送到那个活着的 Blender 会话里跑。

用法
----
    python3 code/tools/blender-bridge/bb.py 'bpy.data.filepath'
    python3 code/tools/blender-bridge/bb.py @some_script.py          # 多行代码，按 exec 跑
    python3 code/tools/blender-bridge/bb.py 'print("hi"); __result__ = 42'
    BB_STATE=/别的/状态文件.json python3 .../bb.py '...'

host / port / token **一律从状态文件读**（由 addon 在启动时写），不靠猜、不硬编码。
"""

import json
import os
import socket
import sys

DEFAULT_STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blender-ai-bridge.json")


def load_state():
    path = os.environ.get("BB_STATE") or DEFAULT_STATE
    if not os.path.isfile(path):
        sys.exit(f"[bb] 读不到状态文件：{path}\n"
                 f"     先跑 bb-launch.sh（或手动启动 Blender 时设 BB_STATE 指向它）。\n"
                 f"     状态文件由 blender_ai_bridge.py 在启动时写。")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh), path


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    code = sys.argv[1]
    mode = "eval"
    if code.startswith("@"):
        with open(code[1:], encoding="utf-8") as fh:
            code = fh.read()
        mode = "exec"
    if len(sys.argv) > 2:
        mode = sys.argv[2]

    state, path = load_state()
    req = {"id": 1, "code": code, "mode": mode, "token": state["token"], "timeout": 60}
    try:
        with socket.create_connection((state["host"], state["port"]), timeout=65) as sock:
            sock.sendall((json.dumps(req) + "\n").encode("utf-8"))
            buf = b""
            while not buf.endswith(b"\n"):
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buf += chunk
    except OSError as exc:
        sys.exit(f"[bb] 连不上 {state['host']}:{state['port']}（{exc}）\n"
                 f"     状态文件：{path}\n"
                 f"     Blender 还开着吗？端口/网卡变过吗？重跑 bb-launch.sh。")
    reply = json.loads(buf.decode("utf-8"))
    print(json.dumps(reply, ensure_ascii=False, indent=1))
    return 0 if reply.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
