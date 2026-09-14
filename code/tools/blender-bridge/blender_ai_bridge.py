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
| `BB_OUTBOX` | 状态文件同级的 `bb-outbox/` | 超长输出（> `MAX_RESULT`）的落点。客户端从 `*_file_name` 取文件名、在**状态文件同级目录**找它——不猜 Windows 路径（issue [#162](https://github.com/verystrongdog/game/issues/162)） |
"""

import json
import os
import queue
import secrets
import socketserver
import sys
import threading
import time
import traceback

HOST = os.environ.get("BB_HOST", "127.0.0.1")
PORT = int(os.environ.get("BB_PORT", "9878"))
TOKEN = os.environ.get("BB_TOKEN") or secrets.token_hex(8)
STATE = os.environ.get("BB_STATE") or os.path.join(
    os.environ.get("TEMP", os.path.expanduser("~")), "blender-ai-bridge.json")
MAX_RESULT = 20000          # 回包里的**摘要**上限；超出部分**落文件**（不丢，见 `_spill`）
#: 溢出文件的落点 = 状态文件所在目录下的 `bb-outbox/`——**客户端本来就要读状态文件**，
#: 所以它不必猜任何 Windows 路径就能找到这些文件（issue #162 验收标准 3）
OUTBOX = os.environ.get("BB_OUTBOX") or os.path.join(os.path.dirname(STATE), "bb-outbox")

_inbox = queue.Queue()
_pending = {}
_pending_ts = {}
PENDING_TTL_S = 600.0        # 未被取走的结果保留上限（秒）
_lock = threading.Lock()
_server = None
_started = False


def _spill(text, kind, rid):
    """把超长文本整份写进 outbox，返回 (文件名, 完整路径或错误说明)。"""
    name = f"bb-out-{rid}-{kind}.txt"
    path = os.path.join(OUTBOX, name)
    try:
        os.makedirs(OUTBOX, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    except OSError as exc:
        return None, f"（写不进 outbox：{exc}）"
    return name, path


def _shape(text, kind, rid, res):
    """超长就落文件、回包只回**头**+文件名；不超长就原样回。"""
    if len(text) <= MAX_RESULT:
        return text
    name, path = _spill(text, kind, rid)
    res[f"{kind}_file"] = path
    res[f"{kind}_file_name"] = name
    res[f"{kind}_chars"] = len(text)
    head = text[:MAX_RESULT]
    return head + f"\n…（已截断：完整 {len(text)} 字符见 {kind}_file）"


def _summarize(value, kind, rid, res):
    if isinstance(value, (int, float, bool, str, type(None))):
        return value
    return _shape(repr(value), kind, rid, res)


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
        res = {"ok": True}
        res["result"] = _summarize(value, "result", rid, res)
    except Exception as exc:
        res = {"ok": False, "error": f"{type(exc).__name__}: {exc}",
               "trace": traceback.format_exc(limit=3)}
    captured = buf.getvalue()
    if captured:
        # ⚠️ 原先只留**尾部** 20000 字符（长报告的开头被吃掉）；现在超长整份落文件、回包头 + 文件名
        res["stdout"] = _shape(captured, "stdout", rid, res)
    with _lock:
        _pending[rid] = res
        _pending_ts[rid] = time.monotonic()


def _tick():
    """主线程心跳：把 queue 里的活取出来跑（bpy 只能在主线程调）。"""
    # 客户端超时后没人来取的结果会留在这里——按时效清掉，别让它长成内存里的陈旧账
    with _lock:
        now = time.monotonic()
        for k in [k for k, ts in _pending_ts.items() if now - ts > PENDING_TTL_S]:
            _pending.pop(k, None)
            _pending_ts.pop(k, None)
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
        # ⚠️ 用**单调时钟死线**而不是"轮询次数 × 0.05"：后者会随 GIL 竞争漂移
        #    （主线程在跑 CPU 密集脚本时，实测 400 次轮询耗掉 >24 s 而非 20 s），
        #    于是"服务端的超时回包"可能比客户端的 socket 超时还晚——回包根本到不了客户端。
        #    issue #162 实测踩到。
        deadline = time.monotonic() + max(1.0, float(req.get("timeout", 30)))
        while time.monotonic() < deadline:
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
