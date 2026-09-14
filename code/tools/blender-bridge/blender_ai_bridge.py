#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""blender_ai_bridge.py —— 把**当前这个 Blender 会话**变成可远程驱动的活体桥。

来源：design/presentation/Blender动作制作管线.md §7.5（用法）/ §7.6（安全与边界）

为什么需要一个"活体桥"
----------------------
`blender --background --python x.py` 已经能让脚本驱动 Blender，但它每次都是**新进程、新会话**：
看不见你手改到一半的东西、也没法让你实时看着它动。活体桥补的正是这一格——
socket 收到代码 → 交给**主线程**执行 → 回传结果，于是"AI 动的是你眼前那个窗口"。

bpy 只能在主线程调用，所以：socket 线程只收活，真正的执行放 queue，
由 `bpy.app.timers` 的回调在主线程取出来跑。

两种用法
--------
1. **会话级**（推荐，免安装）：启动 Blender 时带上本脚本，`.blend` 必须放在它**前面**
   ```powershell
   blender.exe "Z:\\path\\母版.blend" --python "Z:\\path\\blender_ai_bridge.py"
   ```
   ⚠️ 顺序有讲究：`--python` 排在 `.blend` 之前时，脚本在文件加载**之前**就跑了，
   它看到的是默认启动场景（`bpy.data.filepath` 为空）。

2. **装成 addon**：把本文件放进 `<Blender>/scripts/addons/` 并在偏好设置里启用（`register()` 即启动）。

协议
----
一行一条 JSON 请求，回一行 JSON：

    请求 {"id":1, "code":"bpy.data.filepath", "mode":"eval|exec", "token":"...", "timeout":30}
    回   {"ok":true,  "result":"...", "stdout":"..."}
         {"ok":false, "error":"AttributeError: ...", "trace":"..."}

`exec` 模式会**捕获 print 输出**一并回传（省得再写中间文件）。

环境变量
--------
| 变量 | 默认 | 说明 |
|---|---|---|
| `BB_HOST` | `127.0.0.1` | 绑定地址。要从 WSL 连进来必须设成 **WSL 网卡在 Windows 侧的 IP**（`bb-launch.sh` 会自动取） |
| `BB_PORT` | `9878` | 端口 |
| `BB_TOKEN` | 随机生成 | 请求必须带同一个 token；生成值写进状态文件 |
| `BB_STATE` | `%TEMP%/blender-ai-bridge.json` | 状态文件（host/port/token/blender 版本/已加载文件）。**让客户端读它**，不要靠猜 |
"""

import json
import os
import queue
import secrets
import socketserver
import sys
import threading
import traceback

HOST = os.environ.get("BB_HOST", "127.0.0.1")
PORT = int(os.environ.get("BB_PORT", "9878"))
TOKEN = os.environ.get("BB_TOKEN") or secrets.token_hex(8)
STATE = os.environ.get("BB_STATE") or os.path.join(
    os.environ.get("TEMP", os.path.expanduser("~")), "blender-ai-bridge.json")
MAX_RESULT = 20000          # 回传字符串上限，避免把整个场景 repr 出来

_inbox = queue.Queue()
_pending = {}
_lock = threading.Lock()
_server = None
_started = False


def _summarize(value):
    if isinstance(value, (int, float, bool, str, type(None))):
        return value
    text = repr(value)
    return text if len(text) <= MAX_RESULT else text[:MAX_RESULT] + f"...（截断，共 {len(text)} 字符）"


def _run_one(rid, req):
    import bpy
    import contextlib
    import io

    buf = io.StringIO()
    try:
        code = req.get("code", "")
        glb = {"bpy": bpy, "__name__": "__bridge__"}
        with contextlib.redirect_stdout(buf):
            if req.get("mode", "eval") == "exec":
                exec(compile(code, "<bridge>", "exec"), glb)
                value = glb.get("__result__")
            else:
                value = eval(compile(code, "<bridge>", "eval"), glb)
        res = {"ok": True, "result": _summarize(value)}
    except Exception as exc:
        res = {"ok": False, "error": f"{type(exc).__name__}: {exc}",
               "trace": traceback.format_exc(limit=3)}
    captured = buf.getvalue()
    if captured:
        res["stdout"] = captured[-MAX_RESULT:]
    with _lock:
        _pending[rid] = res


def _tick():
    """主线程心跳：把 queue 里的活取出来跑（bpy 只能在主线程调）。"""
    while True:
        try:
            rid, req = _inbox.get_nowait()
        except queue.Empty:
            break
        _run_one(rid, req)
    return 0.05


class _Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            line = self.rfile.readline()
            if not line:
                return
            req = json.loads(line.decode("utf-8"))
        except Exception as exc:
            self.wfile.write((json.dumps({"ok": False, "error": f"bad request: {exc}"}) + "\n").encode())
            return
        if req.get("token") != TOKEN:
            self.wfile.write((json.dumps({"ok": False, "error": "token mismatch"}) + "\n").encode())
            return
        rid = req.get("id", 0)
        _inbox.put((rid, req))
        for _ in range(int(float(req.get("timeout", 30)) * 20)):
            with _lock:
                if rid in _pending:
                    break
            threading.Event().wait(0.05)
        with _lock:
            res = _pending.pop(rid, {"ok": False, "error": "timeout"})
        self.wfile.write((json.dumps(res, ensure_ascii=False) + "\n").encode("utf-8"))


class _Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def start():
    """起服务 + 定时器，并把状态写进 `BB_STATE`（客户端靠它拿 host/port/token）。"""
    global _server, _started
    import bpy
    if _started:
        return
    _server = _Server((HOST, PORT), _Handler)
    threading.Thread(target=_server.serve_forever, daemon=True).start()
    bpy.app.timers.register(_tick, persistent=True)
    _started = True
    state = {"host": HOST, "port": PORT, "token": TOKEN,
             "blender": bpy.app.version_string, "pid": os.getpid(),
             "filepath": bpy.data.filepath,
             "objects": [o.name for o in bpy.data.objects]}
    try:
        with open(STATE, "w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=1)
    except OSError as exc:
        print(f"[bridge] 状态文件写不进去：{exc}", file=sys.stderr)
    print(f"[bridge] {HOST}:{PORT} · state={STATE} · filepath={bpy.data.filepath!r}")


def stop():
    global _server, _started
    if _server is not None:
        _server.shutdown()
        _server.server_close()
        _server = None
    _started = False


# ---- 作为 addon 用时走这里 -------------------------------------------------
bl_info = {
    "name": "AI Bridge (活体桥)",
    "author": "YANTF 项目",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "无界面（启用即监听）",
    "description": "让外部进程远程驱动当前 Blender 会话（token 门禁）",
    "category": "Development",
}


def register():
    start()


def unregister():
    stop()


# ---- 作为 `--python` 脚本用时走这里 ---------------------------------------
if __name__ == "__main__":
    start()
