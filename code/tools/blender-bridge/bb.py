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

import argparse
import json
import os
import socket
import sys
import uuid

DEFAULT_STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blender-ai-bridge.json")
#: 默认超时（秒）。⚠️ 原先是**写死的 60**——真实产姿势的脚本一超 60 s 就被掐断，
#: 而"是不是真超时"从前分不出来（`{"ok": false, "error": "timeout"}` 与脚本自己抛的错长得一样）。
DEFAULT_TIMEOUT = float(os.environ.get("BB_TIMEOUT", "60"))


#: 兜底：`bb-launch.sh` 把状态文件写在**仓库的** `.scratch/` 里，而客户端默认找自己同级目录。
#: 两边不一致时"桥明明活着、客户端却说读不到状态文件"——2026-09-14 实测踩到（issue #162）。
REPO_STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "..", "..", ".scratch", "blender-bridge.json")


def load_state():
    path = os.environ.get("BB_STATE") or DEFAULT_STATE
    if not os.path.isfile(path) and os.path.isfile(REPO_STATE):
        path = REPO_STATE
    if not os.path.isfile(path):
        sys.exit(f"[bb] 读不到状态文件：{path}\n"
                 f"     先跑 bb-launch.sh（或手动启动 Blender 时设 BB_STATE 指向它）。\n"
                 f"     状态文件由 blender_ai_bridge.py 在启动时写。")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh), path


def main():
    ap = argparse.ArgumentParser(prog="bb.py", add_help=True,
                                 description="把一段代码送到那个活着的 Blender 会话里跑")
    ap.add_argument("code", help="代码；以 @ 开头则读文件（按 exec 跑）")
    ap.add_argument("mode", nargs="?", default=None, choices=("eval", "exec"))
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                    help=f"服务端等待上限（秒，默认 {DEFAULT_TIMEOUT:g}；也可用环境变量 BB_TIMEOUT）")
    ap.add_argument("--raw", action="store_true", help="只打印 result/stdout 文本，不打整包 JSON")
    args = ap.parse_args()

    code = args.code
    mode = args.mode
    if code.startswith("@"):
        with open(code[1:], encoding="utf-8") as fh:
            code = fh.read()
        mode = mode or "exec"
    mode = mode or "eval"

    state, path = load_state()
    # ⚠️ rid 必须**每次唯一**：原先写死 `id: 1`，而服务端按 rid 存结果 ⇒ 一次超时留下的
    #    残留结果会被**下一次请求**立即取走——客户端拿到的是**上一次的输出**，还是"成功"的。
    #    这是静默错误（issue #162 实测踩到：探针请求秒回了上一个 67.6 s 任务的结果）。
    req = {"id": uuid.uuid4().hex[:12], "code": code, "mode": mode,
           "token": state["token"], "timeout": args.timeout}
    try:
        # socket 超时必须**明显长于**应用层超时：服务端的回包要在应用层超时之后再飞回来，
        # 贴太近会让"超时"这个明确信号退化成"连不上"（issue #162 实测踩到）。
        with socket.create_connection((state["host"], state["port"]), timeout=args.timeout + 30) as sock:
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
    if args.raw:
        if reply.get("stdout"):
            print(reply["stdout"])
        if reply.get("result") is not None:
            print(reply["result"])
    else:
        print(json.dumps(reply, ensure_ascii=False, indent=1))
    # 超长输出已被服务端落进 outbox —— 按**文件名**在状态文件同级目录里找它（不猜 Windows 路径）
    for key in ("stdout_file_name", "result_file_name"):
        if reply.get(key):
            local = os.path.join(os.path.dirname(os.path.abspath(path)), "bb-outbox", reply[key])
            print(f"[bb] 完整{key.split('_')[0]}（{reply.get(key.split('_')[0] + '_chars', '?')} 字符）→ {local}",
                  file=sys.stderr)
    if reply.get("error") == "timeout":
        print(f"[bb] ⏱ 服务端在 --timeout {args.timeout:g}s 内没跑完（不是脚本报错）。"
              f"加大 --timeout 再试；脚本仍在那个会话里继续跑。", file=sys.stderr)
    return 0 if reply.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
