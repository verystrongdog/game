#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 verystrongdog
# SPDX-License-Identifier: GPL-3.0-or-later
"""xbot_balance.py —— **凸包件**（`支撑多边形` + 「`重心` ↔ `支撑多边形`」判据）：从一条动作算出逐帧的支撑域与"投影在不在域内"。

## 权威来源（本件的定义**逐字**取自这两条，不得自行发挥）

**① 术语定义**（`data/term_registry.json`，2026-09-15 入库，**逐字**——B1 每次校验核它）：

> `重心`：本仓的**躯体代表点**，用于判「站得住吗」：取值 = `mixamorig:Hips` 骨**世界位置的水平投影**（x, y）——**不含质量模型**。

> `支撑多边形`：当前**着地足底点的凸包**——判「站得住吗」时的参照域：`重心`（= `mixamorig:Hips` 世界位置水平投影）落在域内即视为稳。

⚠️ **注册表同一段里还有两句话，本件落地后不再成立，但本件不动注册表**（#170 的预期差分里没有 `data/term_registry.json`）：
`重心` 条目结尾写着「判据部分（投影 ↔ 支撑多边形）因**支撑多边形本身仍未建**（缺的是凸包，不再是相位）而按 §8.3 过渡态**只报读数、由 owner 目视判**」，
`支撑多边形` 条目结尾写着「⚠️ **本件（凸包本身）尚无任何实现**」。
⇒ 这两句**在本件落地后即失效**，按 [#167](https://github.com/verystrongdog/game/issues/167) 对 `接触相位` 的先例，
刷新注册表**另开一件**（本件只登记该事实，见证据 §八）。B1 因此核的是**定义核**（上面两段逐字），
**不核**那两句会失效的现状句——否则本件一落地 B1 就红在自己的产物上。

**② 接触判据与容差**：**一律引用** [#165](https://github.com/verystrongdog/game/issues/165) 的件
`code/tools/xbot_contact_phase.py`（`import` 后调用它的 `lowest_point_mm` / `is_contact` / `summarize`），
**不自己另算一份**——[危险点表 §147](../engineering/危险点表.md)「同一几何只允许一个来源」（先例：`chair_layout` 两处各算一份、差 0.46 m）。
容差仍是 `soleMargin = 0.0028 m`，地面仍是世界 z = 0；本件**不新拍任何数、不改阈值**。

## 本件判了什么（以及**不**判什么）

| 口径问题 | 本件的答案 | 依据 |
|---|---|---|
| **支撑域是什么** | 当前**着地足底点**的**凸包**（水平面内的二维凸包，单调链，逆时针） | 注册表 `支撑多边形` 逐字 |
| **重心是什么** | `mixamorig:Hips` 骨**世界位置的水平投影**（x, y）——**零常量代理点**，**不含质量模型** | 注册表 `重心` 逐字 |
| **判据是什么** | **投影在域内 / 域外**这个**布尔**（含边界 ⇒ 余量 ≥ 0 即内）；余量（到域边界的带符号距离）**只报读数** | 注册表 `支撑多边形` 的 `deviation_reason`：「判据落在『投影在不在域内』这个**布尔**上——先不引入角度/余量这类需要来源的阈值」 |
| **域无面积时怎么办** | **报 `退化（域无面积）`**，逐帧显式列出，**不当"内"也不当"外"** | 本仓禁静默省略（#165 的「未出现」先例）；单脚单点的域确实没有面积 |
| **两层口径** | **并列报出**：**骨点层**（M2 取点口径用到的两个骨点 `Foot.head` / `ToeBase.head` 的水平位置）与**蒙皮层**（`Beta_Surface` 上主导顶点组 ∈ {Foot, ToeBase} 且 z ≤ `soleMargin` 的顶点） | [#165](https://github.com/verystrongdog/game/issues/165) 证据 §七 #4 的**未裁项**（实测同帧两口径给出相反答案、**最大层差 41 mm**）⇒ 本件**并列读数 + 给建议**，**裁定归 owner** |

⚠️ 本件**不判"站得稳不稳"这个观感**——它判的是注册表写下的那个布尔；"看着站得住"仍归 owner 目视（注册表 `重心` 的 `deviation_reason` 逐字）。

## 两种跑法

| 模式 | 触发 | 干什么 | 谁用 |
|---|---|---|---|
| **Blender 侧读产物** | `--blend <样本> --action <名>`（须在 Blender 里跑） | 逐帧求值那条动作，从 **`object.evaluated_get(depsgraph)`** 读骨与蒙皮，算凸包 + 判据 + 层选对照，写报告 + markdown | #170 的样本（下蹲/被推退）与其交叉核对 |
| **在会话里读**（同一实现） | `read_current(arm, action)` —— 宿主在**打键之后**直接调用 | 同上，但不打开文件（动作就在当前会话里） | `author_xbot_chair_grab.py --task crouch` |
| **离线机械校验** | 无参数 / `--verify`（`--only B4` 只跑一条；纯 Python，不需要 bpy） | 对本仓库的文件跑 B1–B5（见下）——原由 `run_all_checks.py` 与 CI 编排，⚠️ 2026-09-17 两者已随全部门禁删除，现在须手动跑 | ~~门禁 `docs-integrity`~~（已删） |

### 取帧口径（Blender 侧，**照 #165 的件**，否则读数不可比）

1. 先清空姿势（`rotation_mode` **不许动**——探针动作写在 `rotation_euler` 通道上）；
2. 用 `blender_action_compat.assign_action` 指派动作（5.x 槽位化动作**必须再指 slot**）；
3. `scene.frame_set(f)` + `view_layer.update()`，从 **`evaluated_get(depsgraph)`** 读 ⇒ 那是**产物**。

### 离线判据 B1–B5

| id | 判据 | 防的是什么 |
|---|---|---|
| **B1** | 注册表 `重心` / `支撑多边形` 的**定义核**（本文件 docstring 里逐字引的那两段）**逐字**出现在本文件 docstring 里 | 定义漂移（改了注册表不同步本件 ⇒ 本件的判据失据） |
| **B2** | **单一来源**：本件 `import` 了 `xbot_contact_phase`、**不出现**自定的接触容差字面量（`0.0028`）；且那份件的 `SOLE_MARGIN_M` 与 `FootGroundingIK.cs` 的 `soleMargin` **逐值相同** | 接触判据被抄成第二份（改一处漏一处） |
| **B3** | 合成用例：凸包 / 面积 / 余量 / 判定（内 · 外 · 边界 · 退化）+ **判据能报红**（域外用例必须是"外"）+ markdown 往返逐值一致 | 算法静默退化（"零域外的绿"） |
| **B4** | 证据里的**逐帧凸包与重心表** → 用本件的纯算法重算 ⇒ 与证据里**声明的**面积 / 余量 / 判定 / 域外帧**逐值一致** | 文档与算法漂移（表格是入库的真值，必须能重算） |
| **B5** | 证据里声明的**接触相位结构**（逐脚支撑区间 / 双支撑 / 换脚帧 / 未出现的类别）→ 用 `xbot_contact_phase.summarize()` 从**同表**的左/右最低读数重算 ⇒ **逐值一致** | 两件对"哪些点着地"给出不同答案（先例 [#166](https://github.com/verystrongdog/game/issues/166) §九：两处独立实现给同一个答案） |

⚠️ **B4/B5 的覆盖边界**（诚实清单）：它们判的是**证据表 ↔ 算法**一致，**判不了**"那条动作的支撑域本身对不对"——
后者是 owner 目视的面。两条都**不重跑 Blender**（CI 上无 Blender 可用）。

## 层选（须 owner 裁的那一格）

本件**并列**骨点层与蒙皮层，给出：逐帧两口径的判定、判定不一致的帧、**余量差的最大值**（#165 的 41 mm 是同一族读数）。
**建议**写在证据里（依据读数），**裁定归 owner**——本件不把任何一层写成"判据层"（那是 `口径 §8.3` 过渡态的出口）。

来源：issue [#170](https://github.com/verystrongdog/game/issues/170)（② 件：下蹲 / 被推退 · `C′ 平衡与支撑`）；
规则层需求 = [回合战斗流程 §10.13](../rules/回合战斗流程.md)「推挤（对角色）」；
前置件 = [#165](https://github.com/verystrongdog/game/issues/165)（`接触相位`）；
未裁项来源 = [#165 证据](engineering/evidence/xbot-contact-phase-2026-09-15.md) §七 #4。
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

try:                                    # Blender 侧才有；离线（CI）没有
    import bpy                          # type: ignore
    HAS_BPY = True
except Exception:                       # pragma: no cover - 取决于运行环境
    bpy = None                          # type: ignore
    HAS_BPY = False

sys.path.insert(0, str(Path(__file__).resolve().parent))
import xbot_contact_phase as cp          # noqa: E402  ← **单一来源**：接触判据与容差只此一份（B2 核它）

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------- 常量（全部带来源）

#: 判据用的两条术语。来源：`data/term_registry.json`（B1 逐字核定义核）。
TERMS = ("重心", "支撑多边形")

#: **定义核**——逐字取自注册表两条的 `definition`，且**逐字**出现在本文件 docstring 里（B1）。
#: ⚠️ 只取**语义核**，不取那两句"本件/判据部分仍未建"的**现状句**（本件落地后它们即失效，
#: 刷新注册表另开一件；见 docstring 顶部 ⚠️）。
CORE_DEFINITIONS = {
    "重心": "本仓的**躯体代表点**，用于判「站得住吗」：取值 = `mixamorig:Hips` 骨**世界位置的水平投影**（x, y）——**不含质量模型**。",
    "支撑多边形": "当前**着地足底点的凸包**——判「站得住吗」时的参照域：`重心`（= `mixamorig:Hips` 世界位置水平投影）落在域内即视为稳。",
}

#: 两层口径的名字（**并列报出**，见 docstring 的"两层口径"行）。
LAYER_BONE = "骨点层"
LAYER_SKIN = "蒙皮层"
LAYERS = (LAYER_BONE, LAYER_SKIN)

#: 骨点层的候选点 = **M2 取点口径用到的两个骨点**（`Foot.head` / `ToeBase.head` 的水平位置）。
#: 来源：对照实验 §三 M2「该脚『足骨 y』与『趾骨 y』的较小者 − 地面 y」——同一对点，不引入第二套几何。
#: 先例：宿主 5 的 `重心` 读数用的就是 `[(bone.x, bone.y), (toe.x, toe.y)]`（`author_xbot_chair_grab.py:3537`）。
BONE_POINT_SUFFIXES = ("Foot", "ToeBase")

#: 蒙皮层的顶点集（主导顶点组）——**沿用**接触相位件的取法（同一个 `_skin_index`，不抄第二份）。
#: 层的选择来源：`Beta_Surface` 是**可见皮肤层**（`Beta_Joints` 是骨骼可视化网格，混进来会污染读数）。
SKIN_MESH = cp.SKIN_MESH

#: 判定的三种字面量（**退化必须显式列出**，不得静默并入"内/外"）。
V_IN = "内"
V_OUT = "外"
V_DEGENERATE = "退化（域无面积）"

#: 证据文件（B4/B5 的判定面）与样本段的机器标记
EVIDENCE_PATH = "design/engineering/evidence/balance-support-2026-09-16.md"
SAMPLE_BEGIN = "<!-- balance:sample={} -->"
SAMPLE_END = "<!-- /balance:sample -->"

#: 证据表里坐标与读数的**存储精度**（mm）。0.1 mm 远低于任何有意义的几何差；
#: ⚠️ 证据里**声明的**面积/余量/判定一律**从取整后的点重算**（发射与 B4 用同一条算路 ⇒ 逐值可比）。
COORD_DECIMALS = 1
VALUE_DECIMALS = 3

#: 离线判据读的既有来源文件
SRC_REGISTRY = "data/term_registry.json"
SRC_CONTACT_PHASE = "code/tools/xbot_contact_phase.py"
SRC_FOOT_IK = "code/unity/Assets/Scripts/FootGroundingIK.cs"

# ---------------------------------------------------------------- 纯算法（无 bpy 依赖）


def convex_hull_mm(points: list) -> list:
    """二维凸包（**单调链**，Andrew 1979），逆时针，帧内取点一律 mm。

    - 重复点与**边上的共线点**一律剔除（只留凸包的**极点**）⇒ 顶点数稳定、"退化"判据不受共线点干扰；
    - 点数 < 3 或面积 = 0 时返回的仍是"塌掉的包"（1 / 2 个点或共线段），由 `signed_margin_mm` 判退化。

    ⚠️ 本函数**不做任何阈值判断**（本仓禁无来源阈值）：它只做几何。
    """
    pts = sorted({(round(float(x), 6), round(float(y), 6)) for x, y in points})
    if len(pts) <= 2:
        return [tuple(p) for p in pts]

    def half(seq):
        out: list = []
        for p in seq:
            while len(out) >= 2:
                (ax, ay), (bx, by) = out[-2], out[-1]
                if (bx - ax) * (p[1] - ay) - (by - ay) * (p[0] - ax) > 0.0:
                    break
                out.pop()
            out.append(p)
        return out

    lower = half(pts)
    upper = half(list(reversed(pts)))
    return lower[:-1] + upper[:-1]


def polygon_area_mm2(hull: list) -> float:
    """多边形面积（鞋带公式，mm²），取绝对值。"""
    n = len(hull)
    if n < 3:
        return 0.0
    s = 0.0
    for i in range(n):
        x1, y1 = hull[i]
        x2, y2 = hull[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def signed_margin_mm(hull: list, p) -> float | None:
    """`p` 到凸包边界的**带符号距离**（mm）：**正 = 域内**，负 = 域外，0 = 边界上。

    实现：凸包按逆时针给出 ⇒ 每条边的左侧为内，`cross(edge, p−a) / |edge|` 就是该边的带符号距离；
    取最小者 = 到边界最近的那条边。**退化（点数 < 3 或面积 = 0）返回 `None`**——那种域没有"内外"可言。
    """
    if len(hull) < 3 or polygon_area_mm2(hull) <= 0.0:
        return None
    best = None
    n = len(hull)
    for i in range(n):
        ax, ay = hull[i]
        bx, by = hull[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        el = math.hypot(ex, ey)
        if el == 0.0:
            continue
        d = (ex * (p[1] - ay) - ey * (p[0] - ax)) / el
        best = d if best is None else min(best, d)
    return best


def verdict(hull: list, p) -> str:
    """判定：`内` / `外` / `退化（域无面积）`。**含边界 = 内**（余量 ≥ 0，零阈值）。"""
    m = signed_margin_mm(hull, p)
    if m is None:
        return V_DEGENERATE
    return V_IN if m >= 0.0 else V_OUT


def balance_of_points(points: list, com_xy) -> dict:
    """一组着地足底点 + 一个重心水平投影 ⇒ 该层该帧的读数（凸包 / 面积 / 余量 / 判定）。"""
    hull = convex_hull_mm(points)
    return {"着地足底点数": len(points), "凸包顶点数": len(hull),
            "凸包_mm": [[round(x, 3), round(y, 3)] for x, y in hull],
            "面积_mm2": round(polygon_area_mm2(hull), 6),
            "余量_mm": (None if signed_margin_mm(hull, com_xy) is None
                        else round(signed_margin_mm(hull, com_xy), 6)),
            "判定": verdict(hull, com_xy)}


def summarize_balance(frames: list) -> dict:
    """逐帧读数 → 结构（逐层：域内/域外/退化帧；层选对照；未出现的类别）。

    `frames` 每项形如 `{"帧": f, "重心_xy_mm": [x, y], "骨点层": {...}, "蒙皮层": {...}}`（顺序即帧顺序）。
    """
    out: dict = {"帧范围": [frames[0]["帧"], frames[-1]["帧"]] if frames else [0, 0], "帧数": len(frames)}
    for layer in LAYERS:
        ins, outs, deg = [], [], []
        margins = []
        for r in frames:
            lay = r.get(layer) or {}
            v = lay.get("判定")
            if v == V_IN:
                ins.append(r["帧"])
            elif v == V_OUT:
                outs.append(r["帧"])
            else:
                deg.append(r["帧"])
            if lay.get("余量_mm") is not None:
                margins.append((r["帧"], lay["余量_mm"]))
        lo = min(margins, key=lambda t: t[1]) if margins else None
        hi = max(margins, key=lambda t: t[1]) if margins else None
        out[layer] = {
            "可判帧数": len(ins) + len(outs), "域内帧数": len(ins), "域外帧数": len(outs),
            "域内帧": ins, "域外帧": outs, "退化帧": deg,
            "余量最小_mm": None if lo is None else round(lo[1], 3),
            "余量最小帧": None if lo is None else lo[0],
            "余量最大_mm": None if hi is None else round(hi[1], 3),
            "余量最大帧": None if hi is None else hi[0],
        }
    # ---- 层选对照：两口径的判定什么时候不一致、余量差多大（#165 的 41 mm 同族读数）----
    diff, disagree = [], []
    for r in frames:
        b, s = r.get(LAYER_BONE) or {}, r.get(LAYER_SKIN) or {}
        if b.get("余量_mm") is None or s.get("余量_mm") is None:
            continue
        d = round(b["余量_mm"] - s["余量_mm"], 3)
        diff.append((r["帧"], d))
        if b.get("判定") != s.get("判定"):
            disagree.append({"帧": r["帧"], "骨点层": b.get("判定"), "蒙皮层": s.get("判定"),
                             "骨点层余量_mm": b.get("余量_mm"), "蒙皮层余量_mm": s.get("余量_mm")})
    worst = max(diff, key=lambda t: abs(t[1])) if diff else None
    out["层选对照"] = {"可比帧数": len(diff), "判定不一致帧": disagree,
                      "最大余量差_mm": None if worst is None else abs(worst[1]),
                      "最大余量差帧": None if worst is None else worst[0],
                      "余量差正负号含义": "正 = 骨点层的域比蒙皮层**更宽**（同一投影在骨点层更靠内）"}
    # 「未出现」必须显式列出（#165 的验收标准：不得静默省略）
    absent = []
    for layer in LAYERS:
        if not out[layer]["域外帧"]:
            absent.append(f"{layer}·域外帧")
        if not out[layer]["退化帧"]:
            absent.append(f"{layer}·退化帧")
        if not out[layer]["域内帧"]:
            absent.append(f"{layer}·域内帧")
    if not out["层选对照"]["判定不一致帧"]:
        absent.append("层选·判定不一致帧")
    out["未出现的类别"] = absent
    return out


# ---------------------------------------------------------------- markdown（发射 + 解析，互为逆）


def _pts_cell(pts_mm: list) -> str:
    if not pts_mm:
        return "未出现"
    return " ".join(f"({x:g},{y:g})" for x, y in pts_mm)


def _parse_pts_cell(cell: str) -> list:
    if cell.strip() in ("", "—", "-", "未出现"):
        return []
    return [[float(a), float(b)] for a, b in re.findall(r"\((-?[\d.]+),(-?[\d.]+)\)", cell)]


def _rounded_layer(layer: dict, com_xy) -> dict:
    """把该层的**凸包顶点取整到 0.1 mm**，并从取整后的点重算面积/余量/判定（证据表声明的就是这一套）。"""
    pts = [[round(x, COORD_DECIMALS), round(y, COORD_DECIMALS)] for x, y in layer["凸包_mm"]]
    com = (round(com_xy[0], COORD_DECIMALS), round(com_xy[1], COORD_DECIMALS))
    hull = convex_hull_mm(pts)
    m = signed_margin_mm(hull, com)
    return {"凸包_mm": [[float(x), float(y)] for x, y in hull],
            "面积_mm2": round(polygon_area_mm2(hull), VALUE_DECIMALS),
            "余量_mm": None if m is None else round(m, VALUE_DECIMALS),
            "判定": V_DEGENERATE if m is None else (V_IN if m >= 0 else V_OUT),
            "着地足底点数": layer["着地足底点数"]}


def _num(v, decimals=VALUE_DECIMALS) -> str:
    return "未出现" if v is None else f"{v:.{decimals}f}"


def sample_markdown(sample: dict) -> str:
    """一个样本 → markdown 段（`B4`/`B5` 会把它解析回来重算）。"""
    sid = sample["id"]
    icon = {V_IN: "内", V_OUT: "**外**"}
    lines = [
        SAMPLE_BEGIN.format(sid),
        f"#### 样本 {sid}：{sample['名称']}",
        "",
        f"- 动作：`{sample['动作']}`（帧 {sample['帧范围'][0]}–{sample['帧范围'][1]}，{sample['fps']} fps）",
        f"- 样本文件：`{sample['样本文件']}`",
        f"- 接触判据与容差：`code/tools/xbot_contact_phase.py`（[#165](https://github.com/verystrongdog/game/issues/165)）"
        f"· `soleMargin = {cp.SOLE_MARGIN_MM:.1f} mm` · 地面 = 世界 z {cp.GROUND_Z_M:g}（**本件不另算一份**）",
        f"- 重心 = `mixamorig:Hips` 世界位置水平投影 · 域 = 着地足底点凸包 · 判据 = 投影在内为稳（含边界）",
        "",
    ]
    for layer in LAYERS:
        hint = ("骨点层 = M2 取点口径的两个骨点 `Foot.head` / `ToeBase.head`（水平位置，逐点按同一容差着地过滤）"
                if layer == LAYER_BONE else
                f"蒙皮层 = `{SKIN_MESH}` 上主导顶点组 ∈ {{Foot, ToeBase}} 且 z ≤ `soleMargin` 的顶点")
        lines += [
            f"**{layer}**（{hint}）",
            "",
            "| 帧 | 左最低 (mm) | 右最低 (mm) | 左接触 | 右接触 | 重心 x (mm) | 重心 y (mm) | 着地点数 | 凸包顶点数 | 面积 (mm²) | 带符号余量 (mm) | 判定 | 凸包顶点 (mm) |",
            "|---:|---:|---:|:--:|:--:|---:|---:|---:|---:|---:|---:|:--:|---|",
        ]
        for r in sample["逐帧"]:
            com = r["重心_xy_mm"]
            lay = _rounded_layer(r[layer], com)
            lines.append(
                f"| {r['帧']} | {r['左最低_mm']:.4f} | {r['右最低_mm']:.4f} | "
                f"{'✅' if r['接触']['左'] else '—'} | {'✅' if r['接触']['右'] else '—'} | "
                f"{com[0]:.1f} | {com[1]:.1f} | {lay['着地足底点数']} | {len(lay['凸包_mm'])} | "
                f"{lay['面积_mm2']:.3f} | {_num(lay['余量_mm'])} | "
                f"{icon.get(lay['判定'], lay['判定'])} | {_pts_cell(lay['凸包_mm'])} |")
        lines.append("")
    st = sample["结构"]
    lines += [
        "| 派生结构 | 骨点层 | 蒙皮层 |",
        "|---|---|---|",
        f"| 域内帧数 | {st[LAYER_BONE]['域内帧数']} | {st[LAYER_SKIN]['域内帧数']} |",
        f"| 域外帧数 | {st[LAYER_BONE]['域外帧数']} | {st[LAYER_SKIN]['域外帧数']} |",
        f"| 退化帧数 | {len(st[LAYER_BONE]['退化帧'])} | {len(st[LAYER_SKIN]['退化帧'])} |",
        f"| 余量最小 (mm) | {_num(st[LAYER_BONE]['余量最小_mm'])} | {_num(st[LAYER_SKIN]['余量最小_mm'])} |",
        "",
        "| 派生结构 | 值 |",
        "|---|---|",
        f"| 骨点层域外帧 | {_fr_cell(st[LAYER_BONE]['域外帧'])} |",
        f"| 蒙皮层域外帧 | {_fr_cell(st[LAYER_SKIN]['域外帧'])} |",
        f"| 骨点层退化帧 | {_fr_cell(st[LAYER_BONE]['退化帧'])} |",
        f"| 蒙皮层退化帧 | {_fr_cell(st[LAYER_SKIN]['退化帧'])} |",
        f"| 层选·判定不一致帧 | {_frames_cell(st['层选对照']['判定不一致帧'])} |",
        f"| 层选·最大余量差 (mm) | {_num(st['层选对照']['最大余量差_mm'])} |",
        f"| 未出现的类别 | {' · '.join(st['未出现的类别']) or '—'} |",
        "",
        "| 接触相位（引用 [#165](https://github.com/verystrongdog/game/issues/165) 的件 `summarize()` 算出） | 值 |",
        "|---|---|",
        f"| 左支撑区间 | {_iv(sample['接触相位']['支撑区间']['左'])} |",
        f"| 右支撑区间 | {_iv(sample['接触相位']['支撑区间']['右'])} |",
        f"| 双支撑区间 | {_iv(sample['接触相位']['双支撑区间'])} |",
        f"| 无支撑区间 | {_iv(sample['接触相位']['无支撑区间'])} |",
        f"| 换脚帧 | {_fr_cell(sample['接触相位']['换脚帧'])} |",
        f"| 未出现的类别（接触相位） | {' · '.join(sample['接触相位']['未出现的类别']) or '—'} |",
        "",
        SAMPLE_END,
    ]
    return "\n".join(lines)


def _iv(ivs: list) -> str:
    if not ivs:
        return "未出现"
    return " ".join(f"[{iv[0]},{iv[1]}]" for iv in ivs)


def _iv_list(cell: str) -> list:
    if cell.strip() in ("", "—", "-", "未出现"):
        return []
    return [[int(a), int(b)] for a, b in re.findall(r"\[(\d+),(\d+)\]", cell)]


def _fr_cell(frames: list) -> str:
    """帧号列表（**不是区间**）：`4, 7, 49`；空集一律写 `未出现`。"""
    if not frames:
        return "未出现"
    return ", ".join(str(f) for f in frames)


def _fr_list(cell: str) -> list:
    if cell.strip() in ("", "—", "-", "未出现"):
        return []
    return [int(x) for x in re.findall(r"\d+", cell)]


def _frames_cell(items: list) -> str:
    if not items:
        return "未出现"
    return ", ".join(f"{x['帧']}({x['骨点层']}/{x['蒙皮层']})" for x in items)


def _frames_list(cell: str) -> list:
    if cell.strip() in ("", "—", "-", "未出现"):
        return []
    return [int(x) for x in re.findall(r"(\d+)\(", cell)]


def parse_sample_markdown(text: str) -> list[dict]:
    """证据文档里所有 `balance:sample` 段 → 可重算的结构（B4/B5 的输入）。"""
    #: 声明行的**键前缀**（顺序 = 匹配顺序：更具体的写在前面，避免前缀互相吞掉）
    DECLARED_KEYS = ("未出现的类别（接触相位）", "未出现的类别", "骨点层域外帧", "蒙皮层域外帧",
                     "骨点层退化帧", "蒙皮层退化帧", "层选·判定不一致帧", "层选·最大余量差",
                     "左支撑区间", "右支撑区间", "双支撑区间", "无支撑区间", "换脚帧")
    out = []
    for m in re.finditer(re.escape("<!-- balance:sample=") + r"([^ ]+?) -->(.*?)"
                         + re.escape(SAMPLE_END), text, re.S):
        sid, body = m.group(1), m.group(2)
        frames: dict[int, dict] = {}
        declared: dict[str, str] = {}
        layer = None
        for line in body.splitlines():
            s = line.strip()
            if s.startswith("**骨点层**"):
                layer = LAYER_BONE
                continue
            if s.startswith("**蒙皮层**"):
                layer = LAYER_SKIN
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            # 逐帧行：13 列 —— 帧 · 左最低 · 右最低 · 左接触 · 右接触 · 重心x · 重心y ·
            #   着地点数 · 凸包顶点数 · 面积 · 余量 · 判定 · 凸包顶点
            if len(cells) == 13 and cells[0].isdigit() and cells[3] in ("✅", "—") and layer:
                f = int(cells[0])
                row = frames.setdefault(f, {"帧": f, "重心_xy_mm": [float(cells[5]), float(cells[6])],
                                            "左最低_mm": float(cells[1]), "右最低_mm": float(cells[2]),
                                            "接触": {}})
                if layer == LAYER_BONE:                     # 接触两列只在骨点层那张表里（判据的唯一来源）
                    row["接触"] = {"左": cells[3] == "✅", "右": cells[4] == "✅"}
                row[layer] = {"着地足底点数": int(cells[7]), "凸包_mm": _parse_pts_cell(cells[12]),
                              "面积_mm2": float(cells[9]),
                              "余量_mm": None if cells[10] == "未出现" else float(cells[10]),
                              "判定": ("外" if cells[11].startswith("**外**") else
                                       ("内" if cells[11] == "内" else V_DEGENERATE))}
                continue
            if len(cells) != 2 or not cells[0]:
                continue
            for key in DECLARED_KEYS:
                if cells[0].startswith(key):
                    if key == "层选·最大余量差":
                        declared["层选·最大余量差 (mm)"] = cells[1]
                    else:
                        declared.setdefault(key, cells[1])
                    break
        out.append({"id": sid, "逐帧": [frames[k] for k in sorted(frames)], "声明": declared})
    return out


# ---------------------------------------------------------------- Blender 侧：读产物


def _world_xy_z(arm, bone: str) -> tuple:
    """求值后的骨**世界**位置（head）。⚠️ 走 `evaluated_get(depsgraph)` ⇒ 那是**产物**。"""
    dg = bpy.context.evaluated_depsgraph_get()
    ae = arm.evaluated_get(dg)
    p = ae.matrix_world @ ae.pose.bones[bone].head
    return (p.x, p.y, p.z)


def _skin_ground_points(arm, idx: list, margin_m: float) -> list:
    """该侧蒙皮顶点里**着地**那些的水平坐标：逐顶点 `z − 地面 ≤ soleMargin`（同一个容差，不新拍数）。"""
    if not idx:
        return []
    dg = bpy.context.evaluated_depsgraph_get()
    ob = bpy.data.objects[SKIN_MESH].evaluated_get(dg)
    me = ob.to_mesh()
    try:
        mw = ob.matrix_world
        out = []
        for i in idx:
            p = mw @ me.vertices[i].co
            if p.z - cp.GROUND_Z_M <= margin_m:
                out.append((p.x, p.y))
        return out
    finally:
        ob.to_mesh_clear()


def read_current(arm, action_name: str, fps: int | None = None, with_skin: bool = True) -> dict:
    """**在当前会话里**读一条动作（Blender 侧；`--blend` 那条路也走它）——这是唯一的实现。"""
    if not HAS_BPY:
        raise RuntimeError("读产物需要 Blender（bpy 不可用）")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import blender_action_compat as bac

    act = bpy.data.actions.get(action_name)
    if act is None:
        raise RuntimeError(f"样本里没有动作 `{action_name}`；实测：{[a.name for a in bpy.data.actions]}")
    if fps:
        bpy.context.scene.render.fps = fps

    # ---- 静息对照：先解开动作、清空姿势再读（顺序不能反，否则读的是"动作在当前帧的值"）----
    arm.animation_data_clear()
    cp._clear_pose(arm)
    rest = {"髋_xy_mm": [round(v * 1000.0, 2) for v in _world_xy_z(arm, f"{cp.BONE_PREFIX}Hips")[:2]]}
    skin_idx = {s: cp._skin_index(arm, s) for s in cp.SIDES} if with_skin else {s: [] for s in cp.SIDES}
    rest["蒙皮顶点数"] = {s: len(skin_idx[s]) for s in cp.SIDES}

    ad = arm.animation_data_create()
    bac.assign_action(ad, act)

    f0, f1 = int(round(act.frame_range[0])), int(round(act.frame_range[1]))
    frames, cp_rows, problems = [], [], []
    for f in range(f0, f1 + 1):
        bpy.context.scene.frame_set(f)
        for _ in range(3):
            bpy.context.view_layer.update()
        hx, hy, hz = _world_xy_z(arm, f"{cp.BONE_PREFIX}Hips")
        com = (hx * 1000.0, hy * 1000.0)
        row: dict = {"帧": f, "重心_xy_mm": [round(com[0], 4), round(com[1], 4)],
                     "重心_z_mm": round(hz, 6), "接触": {}}
        lowest = {}
        bone_pts: list = []
        for s in cp.SIDES:
            zh = _world_xy_z(arm, f"{cp.BONE_PREFIX}{s}{cp.FOOT_BONE}")
            zt = _world_xy_z(arm, f"{cp.BONE_PREFIX}{s}{cp.TOE_BONE}")
            low = cp.lowest_point_mm(zh[2], zt[2])
            lowest[s] = low
            # ⚠️ 逐点着地过滤用的是**同一个**判据同一个容差（`cp.is_contact`）⇒ 没有第二份接触判据；
            #    且"脚级接触 = 该脚至少一个候选点着地"是 min 的恒等式（报告里逐帧自核，见 `自核`）。
            for (_x, _y, _z), pt in zip((zh, zt), (zh, zt)):
                if cp.is_contact(pt[2] * 1000.0):
                    bone_pts.append((pt[0] * 1000.0, pt[1] * 1000.0))
            row["接触"][cp.SIDE_OF[s]] = bool(cp.is_contact(low))
            if with_skin:
                row[f"{cp.SIDE_OF[s]}蒙皮着地点数"] = len(
                    _skin_ground_points(arm, skin_idx[s], cp.SOLE_MARGIN_M))
        skin_pts: list = []
        if with_skin:
            for s in cp.SIDES:
                skin_pts += [(x * 1000.0, y * 1000.0)
                             for x, y in _skin_ground_points(arm, skin_idx[s], cp.SOLE_MARGIN_M)]
        row["左最低_mm"] = round(lowest["Left"], 4)
        row["右最低_mm"] = round(lowest["Right"], 4)
        row[LAYER_BONE] = balance_of_points(bone_pts, com)
        row[LAYER_SKIN] = (balance_of_points(skin_pts, com) if with_skin else
                           {"着地足底点数": 0, "凸包顶点数": 0, "凸包_mm": [], "面积_mm2": 0.0,
                            "余量_mm": None, "判定": V_DEGENERATE})
        # ---- 自核（单一来源的现场证据）：脚级接触 == 该脚至少一个候选点着地（min 的恒等式）----
        for s in cp.SIDES:
            any_pt = any(cp.is_contact(_world_xy_z(arm, f"{cp.BONE_PREFIX}{s}{sfx}")[2] * 1000.0)
                         for sfx in BONE_POINT_SUFFIXES)
            if bool(cp.is_contact(lowest[s])) != any_pt:
                problems.append(f"帧 {f} {cp.SIDE_OF[s]}脚：脚级接触 {bool(cp.is_contact(lowest[s]))} "
                                f"≠ 逐点着地 {any_pt}（单一来源自核失败）")
        cp_rows.append({"帧": f, "左最低_mm": row["左最低_mm"], "右最低_mm": row["右最低_mm"]})
        frames.append(row)

    struct = summarize_balance(frames)
    payload = {"逐帧": frames, "结构": struct, "接触相位": cp.summarize(cp_rows)}
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                       separators=(",", ":")).encode("utf-8")).hexdigest()
    return {"script": Path(__file__).name, "blender": bpy.app.version_string,
            "compat": bac.describe(), "动作": action_name, "fps": bpy.context.scene.render.fps,
            "接触件": {"文件名": cp.SRC_REGISTRY and Path(cp.__file__).name,
                       "容差_soleMargin_mm": cp.SOLE_MARGIN_MM, "地面_z_m": cp.GROUND_Z_M},
            "静息对照": rest, "读数指纹_sha256": digest, "problems": problems, **payload}


def read_action(blend: str, action_name: str, fps: int | None = None, with_skin: bool = True) -> dict:
    """打开样本文件后读（Blender 侧入口；实现就是 `read_current`）。"""
    if not HAS_BPY:
        raise RuntimeError("读产物需要 Blender（bpy 不可用）")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(arms) != 1:
        raise RuntimeError(f"期望恰好 1 个 Armature，实测 {len(arms)}")
    rep = read_current(arms[0], action_name, fps=fps, with_skin=with_skin)
    rep["样本文件"] = str(blend)
    return rep


# ---------------------------------------------------------------- 离线判据 B1–B5


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def _registry_entry(term: str) -> dict | None:
    reg = json.loads(_read(SRC_REGISTRY))
    for bucket in reg.values():
        if isinstance(bucket, dict) and term in bucket and isinstance(bucket[term], dict):
            return bucket[term]
    return None


def check_b1() -> tuple[bool, str]:
    """注册表两条的**定义核**逐字出现在本文件 docstring 里。"""
    mine = Path(__file__).read_text(encoding="utf-8")
    problems = []
    for term, core in CORE_DEFINITIONS.items():
        entry = _registry_entry(term)
        if entry is None:
            problems.append(f"注册表里找不到术语 `{term}`")
            continue
        if core not in entry["definition"]:
            problems.append(f"注册表 `{term}` 的定义核已变（本件引的那段不再是它的子串）")
        if core not in mine:
            problems.append(f"本件 docstring 里没有逐字出现 `{term}` 的定义核")
    if problems:
        return False, "；".join(problems)
    return True, f"{len(CORE_DEFINITIONS)} 条术语的定义核在注册表与本件里逐字一致"


def check_b2() -> tuple[bool, str]:
    """**单一来源**：本件引用接触相位件、不自定容差；且那份件的容差与 FootGroundingIK.cs 逐值相同。"""
    mine = Path(__file__).read_text(encoding="utf-8")
    problems = []
    if not re.search(r"^\s*import\s+xbot_contact_phase|^\s*from\s+xbot_contact_phase\s+import",
                     mine, re.M):
        problems.append("本件没有 `import xbot_contact_phase`（接触判据必须走那份件）")
    if not re.search(r"cp\.is_contact\(", mine):
        problems.append("本件没有调用 `cp.is_contact(`（接触判据必须走那份件）")
    # 自定容差：**源码**（抠掉 docstring 与注释）里出现 `0.0028` 一律不允许——容差只许从 cp 取。
    # ⚠️ 扫描前必须把**本判据自己**那段源码抠掉，否则它匹配到自己的字面量（第一版实测踩到：判据判自己）。
    code_only = re.sub(r'"""(?:.|\n)*?"""', "", mine)
    code_only = "\n".join(l.split("#")[0] for l in code_only.splitlines())
    code_only = re.sub(r"def check_b2\(\).*?(?=\ndef |\Z)", "", code_only, flags=re.S)
    if "0.0028" in code_only:
        problems.append("本件源码里出现 `0.0028` 字面量（容差必须从 `xbot_contact_phase` 取）")
    foot = _read(SRC_FOOT_IK)
    m = re.search(r"soleMargin\s*=\s*([0-9.]+)", foot)
    if not m:
        problems.append(f"{SRC_FOOT_IK} 里找不到 soleMargin")
    elif not math.isclose(float(m.group(1)), cp.SOLE_MARGIN_M, rel_tol=0, abs_tol=1e-12):
        problems.append(f"`FootGroundingIK.cs` 的 soleMargin = {m.group(1)} 与 `xbot_contact_phase.py` "
                        f"的 SOLE_MARGIN_M = {cp.SOLE_MARGIN_M} 已不一致（两件对同一容差的引用漂移）")
    if problems:
        return False, "；".join(problems)
    return True, (f"接触判据与容差只此一份（`{SRC_CONTACT_PHASE}`）· "
                  f"soleMargin = {cp.SOLE_MARGIN_M} m 与 FootGroundingIK.cs 逐值相同")
    m = re.search(r"soleMargin\s*=\s*([0-9.]+)", foot)
    if not m:
        problems.append(f"{SRC_FOOT_IK} 里找不到 soleMargin")
    elif not math.isclose(float(m.group(1)), cp.SOLE_MARGIN_M, rel_tol=0, abs_tol=1e-12):
        problems.append(f"`FootGroundingIK.cs` 的 soleMargin = {m.group(1)} 与 `xbot_contact_phase.py` "
                        f"的 SOLE_MARGIN_M = {cp.SOLE_MARGIN_M} 已不一致（两件对同一容差的引用漂移）")
    if problems:
        return False, "；".join(problems)
    return True, (f"接触判据与容差只此一份（`{SRC_CONTACT_PHASE}`）· "
                  f"soleMargin = {cp.SOLE_MARGIN_M} m 与 FootGroundingIK.cs 逐值相同")


def check_b3() -> tuple[bool, str]:
    """合成用例：凸包 / 面积 / 余量 / 判定（含**能报红**）＋ markdown 往返逐值一致。"""
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    cases = [
        # (点集, 重心, 期望面积, 期望余量, 期望判定)
        (square + [(5.0, 5.0), (2.0, 2.0)], (5.0, 5.0), 100.0, 5.0, V_IN),
        (square, (15.0, 5.0), 100.0, -5.0, V_OUT),            # **判据能报红**（域外）
        (square, (10.0, 5.0), 100.0, 0.0, V_IN),              # 边界上 = 内（含边界，零阈值）
        (square, (-0.5, 5.0), 100.0, -0.5, V_OUT),
        ([(0.0, 0.0), (5.0, 0.0), (10.0, 0.0)], (5.0, 0.0), 0.0, None, V_DEGENERATE),   # 共线 ⇒ 退化
        ([], (0.0, 0.0), 0.0, None, V_DEGENERATE),                                       # 空集 ⇒ 退化
        ([(3.0, 4.0)], (3.0, 4.0), 0.0, None, V_DEGENERATE),                             # 单点 ⇒ 退化
    ]
    for i, (pts, com, want_a, want_m, want_v) in enumerate(cases, start=1):
        lay = balance_of_points(pts, com)
        if abs(lay["面积_mm2"] - want_a) > 1e-9:
            return False, f"合成用例 {i}：面积期望 {want_a}，实得 {lay['面积_mm2']}"
        got_m = lay["余量_mm"]
        if (got_m is None) != (want_m is None) or (got_m is not None and abs(got_m - want_m) > 1e-9):
            return False, f"合成用例 {i}：余量期望 {want_m}，实得 {got_m}"
        if lay["判定"] != want_v:
            return False, f"合成用例 {i}：判定期望 {want_v}，实得 {lay['判定']}"
    # 顺时针 / 乱序输入必须给同一个包
    hull_a = convex_hull_mm(square)
    hull_b = convex_hull_mm(list(reversed(square)) + [(5.0, 5.0)])
    if hull_a != hull_b:
        return False, f"凸包与输入顺序有关：{hull_a} vs {hull_b}"
    if not any(v == V_OUT for _p, _c, _a, _m, v in cases):
        return False, "合成用例里没有『域外』——判据不可能报红（退化）"
    # markdown 往返：发射 → 解析 → 重算 ⇒ 逐值不变
    frames = [{"帧": 1 + i, "重心_xy_mm": [c[0], c[1]], "左最低_mm": 0.0, "右最低_mm": 5.0,
               "接触": {"左": True, "右": False},
               LAYER_BONE: balance_of_points(p, c), LAYER_SKIN: balance_of_points(p, c)}
              for i, (p, c) in enumerate([(square, (5.0, 5.0)), (square, (15.0, 5.0))])]
    sample = {"id": "合成", "名称": "合成", "动作": "synthetic", "样本文件": "(合成)", "fps": 30,
              "帧范围": [frames[0]["帧"], frames[-1]["帧"]], "逐帧": frames,
              "结构": summarize_balance(frames),
              "接触相位": cp.summarize([{"帧": r["帧"], "左最低_mm": r["左最低_mm"],
                                        "右最低_mm": r["右最低_mm"]} for r in frames])}
    md = sample_markdown(sample)
    back = parse_sample_markdown(md)
    if len(back) != 1 or len(back[0]["逐帧"]) != len(frames):
        return False, f"markdown 往返后样本段/帧数变了（解析到 {len(back)} 段）"
    for orig, re_read in zip(frames, back[0]["逐帧"]):
        for layer in LAYERS:
            a = _rounded_layer(orig[layer], orig["重心_xy_mm"])
            b = re_read[layer]
            if (a["面积_mm2"], a["余量_mm"], a["判定"]) != (b["面积_mm2"], b["余量_mm"], b["判定"]):
                return False, (f"markdown 往返后 {layer} 帧 {orig['帧']} 变了："
                               f"{a['面积_mm2']}/{a['余量_mm']}/{a['判定']} vs "
                               f"{b['面积_mm2']}/{b['余量_mm']}/{b['判定']}")
            if [[float(x), float(y)] for x, y in a["凸包_mm"]] != [[float(x), float(y)] for x, y in b["凸包_mm"]]:
                return False, f"markdown 往返后 {layer} 帧 {orig['帧']} 的凸包顶点变了"
    return True, f"{len(cases)} 组合成用例逐项相符（含域外=能报红）+ markdown 往返逐值一致"


def check_b4() -> tuple[bool, str]:
    """证据里的逐帧凸包与重心表 → 纯算法重算 ⇒ 与文档声明逐值一致。"""
    path = REPO_ROOT / EVIDENCE_PATH
    if not path.is_file():
        return False, f"证据文件不存在：{EVIDENCE_PATH}"
    samples = parse_sample_markdown(path.read_text(encoding="utf-8"))
    if not samples:
        return False, f"{EVIDENCE_PATH} 里没有解析到任何 `balance:sample` 段"
    problems = []
    for s in samples:
        if not s["逐帧"]:
            problems.append(f"样本 {s['id']}：逐帧表解析为空")
            continue
        for r in s["逐帧"]:
            for layer in LAYERS:
                lay = r.get(layer)
                if lay is None:
                    problems.append(f"样本 {s['id']} 帧 {r['帧']}：缺 {layer} 列")
                    continue
                # ① 存下来的顶点必须**自己就是凸包**（否则表里的点被悄悄改成内点了）
                if convex_hull_mm(lay["凸包_mm"]) != [(float(x), float(y)) for x, y in lay["凸包_mm"]]:
                    problems.append(f"样本 {s['id']} 帧 {r['帧']} {layer}：表里的顶点不是凸包")
                    continue
                a = round(polygon_area_mm2(lay["凸包_mm"]), VALUE_DECIMALS)
                m = signed_margin_mm(lay["凸包_mm"], r["重心_xy_mm"])
                m = None if m is None else round(m, VALUE_DECIMALS)
                if abs(a - lay["面积_mm2"]) > 1e-9:
                    problems.append(f"样本 {s['id']} 帧 {r['帧']} {layer}：面积文档 {lay['面积_mm2']}，"
                                    f"重算 {a}")
                if (m is None) != (lay["余量_mm"] is None) or (m is not None and abs(m - lay["余量_mm"]) > 1e-9):
                    problems.append(f"样本 {s['id']} 帧 {r['帧']} {layer}：余量文档 {lay['余量_mm']}，"
                                    f"重算 {m}")
                want_v = (V_DEGENERATE if m is None else (V_IN if m >= 0 else V_OUT))
                if want_v != lay["判定"]:
                    problems.append(f"样本 {s['id']} 帧 {r['帧']} {layer}：判定文档 {lay['判定']}，"
                                    f"重算 {want_v}")
        # 声明的汇总行
        st = summarize_balance([{**r, "重心_xy_mm": r["重心_xy_mm"]} for r in s["逐帧"]])
        want = {"骨点层域外帧": _fr_list(s["声明"].get("骨点层域外帧", "")),
                "蒙皮层域外帧": _fr_list(s["声明"].get("蒙皮层域外帧", "")),
                "骨点层退化帧": _fr_list(s["声明"].get("骨点层退化帧", "")),
                "蒙皮层退化帧": _fr_list(s["声明"].get("蒙皮层退化帧", ""))}
        got = {"骨点层域外帧": st[LAYER_BONE]["域外帧"], "蒙皮层域外帧": st[LAYER_SKIN]["域外帧"],
               "骨点层退化帧": st[LAYER_BONE]["退化帧"], "蒙皮层退化帧": st[LAYER_SKIN]["退化帧"]}
        for k in want:
            if k not in s["声明"]:
                problems.append(f"样本 {s['id']}：文档缺声明行 `{k}`")
            elif want[k] != got[k]:
                problems.append(f"样本 {s['id']}：`{k}` 文档 {want[k]}，重算 {got[k]}")
        d = s["声明"].get("层选·最大余量差 (mm)")
        calc = st["层选对照"]["最大余量差_mm"]
        if d is None:
            problems.append(f"样本 {s['id']}：文档缺声明行 `层选·最大余量差 (mm)`")
        elif d.strip() == "未出现":
            # 文档写「未出现」= 无可比帧（本件的骨点层全域退化时的形态）⇒ 重算也必须为空
            if calc is not None:
                problems.append(f"样本 {s['id']}：`层选·最大余量差` 文档写「未出现」，重算却是 {calc}")
        elif calc is None or abs(float(d) - calc) > 1e-9:
            problems.append(f"样本 {s['id']}：`层选·最大余量差` 文档 {d}，重算 {calc}")
        dis_doc = _frames_list(s["声明"].get("层选·判定不一致帧", ""))
        dis_calc = [x["帧"] for x in st["层选对照"]["判定不一致帧"]]
        if dis_doc != dis_calc:
            problems.append(f"样本 {s['id']}：`层选·判定不一致帧` 文档 {dis_doc}，重算 {dis_calc}")
    if problems:
        return False, "；".join(problems[:6])
    return True, f"{len(samples)} 个样本的逐帧凸包/重心表重算与文档声明逐值一致"


def check_b5() -> tuple[bool, str]:
    """**两处独立实现给同一个答案**（[#166] §九 的先例）：

    ① 证据里声明的**接触相位结构** → 用 [#165] 的件 `xbot_contact_phase.summarize()` 从同表重算 ⇒ 逐值一致；
    ② 证据里若同时含一份 `contact-phase:sample` 段（那是**独立进程跑 [#165] 的件**产出的表）⇒
       两份表里的逐帧最低读数与派生结构必须**逐值一致**（本件与那份件读的是同一条产物的同一个量）。
    """
    path = REPO_ROOT / EVIDENCE_PATH
    if not path.is_file():
        return False, f"证据文件不存在：{EVIDENCE_PATH}"
    samples = parse_sample_markdown(path.read_text(encoding="utf-8"))
    if not samples:
        return False, f"{EVIDENCE_PATH} 里没有解析到任何 `balance:sample` 段"
    problems = []
    for s in samples:
        rows = [{"帧": r["帧"], "左最低_mm": r["左最低_mm"], "右最低_mm": r["右最低_mm"]}
                for r in s["逐帧"]]
        if not rows:
            continue
        st = cp.summarize(rows)
        want = {"左支撑区间": st["支撑区间"]["左"], "右支撑区间": st["支撑区间"]["右"],
                "双支撑区间": st["双支撑区间"], "无支撑区间": st["无支撑区间"]}
        for k, v in want.items():
            d = s["声明"].get(k)
            if d is None:
                problems.append(f"样本 {s['id']}：文档缺声明行 `{k}`")
            elif _iv_list(d) != [list(iv) for iv in v]:
                problems.append(f"样本 {s['id']}：`{k}` 文档 {d.strip()!r}，"
                                f"用接触相位件重算得 {_iv(v)}")
        d = s["声明"].get("换脚帧")
        if d is None:
            problems.append(f"样本 {s['id']}：文档缺声明行 `换脚帧`")
        elif _fr_list(d) != st["换脚帧"]:
            problems.append(f"样本 {s['id']}：`换脚帧` 文档 {d.strip()!r}，"
                            f"用接触相位件重算得 {st['换脚帧']}")
        absent_doc = s["声明"].get("未出现的类别（接触相位）", "").strip()
        absent_calc = " · ".join(st["未出现的类别"]) or "—"
        if absent_doc != absent_calc:
            problems.append(f"样本 {s['id']}：`未出现的类别（接触相位）` 文档 {absent_doc!r}，"
                            f"重算得 {absent_calc!r}")
    # ---- ② 与**独立进程跑 #165 的件**产出的那份表逐值对照（若证据里有）----
    theirs = cp.parse_sample_markdown(path.read_text(encoding="utf-8"))
    cross = 0
    if theirs:
        for a, b in zip(samples, theirs):
            mine = {r["帧"]: (r["左最低_mm"], r["右最低_mm"]) for r in a["逐帧"]}
            other = {r["帧"]: (r["左最低_mm"], r["右最低_mm"]) for r in b["逐帧"]}
            if not mine or not other:
                continue
            if set(mine) != set(other):
                problems.append(f"样本 {a['id']}：与 #165 件的样本 {b['id']} 帧集合不同"
                                f"（{len(mine)} vs {len(other)}）")
                continue
            # ⚠️ 两份表的**展示精度不同**（本件 4 位小数 · #165 的件 2 位小数）⇒ 比到**两者都打印的
            #    那一位**（2 位小数）；这是"逐值一致"在文档面上的正确读法（阈值 2.8 mm 远不受影响）。
            diff = [f for f in sorted(mine)
                    if (round(mine[f][0], 2), round(mine[f][1], 2))
                    != (round(other[f][0], 2), round(other[f][1], 2))]
            if diff:
                problems.append(f"样本 {a['id']}：与 #165 件的读数在 {len(diff)} 帧上不同："
                                + "; ".join(f"帧 {f} {mine[f]} vs {other[f]}" for f in diff[:3]))
            cross += len(mine) - len(diff)
    if problems:
        return False, "；".join(problems[:6])
    msg = f"{len(samples)} 个样本的接触相位结构与 `xbot_contact_phase.summarize()` 重算逐值一致"
    if cross:
        msg += f" · 与 #165 件独立产出的表 **{cross} 个逐帧读数逐值相同**"
    return True, msg


#: 供**下游宿主**复用的展示件（宿主 7 `--task crouch` 用它打印读数，不复制第二份格式化逻辑）
iv_cell = _iv
frame_list_cell = _fr_cell


OFFLINE_CHECKS = (
    ("B1", "注册表 `重心`/`支撑多边形` 定义核逐字一致", check_b1),
    ("B2", "单一来源：接触判据与容差只此一份", check_b2),
    ("B3", "合成用例（含能报红）+ markdown 往返", check_b3),
    ("B4", "证据逐帧凸包/重心表可重算", check_b4),
    ("B5", "证据接触相位结构与 #165 的件逐值一致", check_b5),
)


def main_verify(only: str | None = None) -> int:
    print(f"# {Path(__file__).name} —— 离线机械校验（凸包件）\n")
    failed = ran = 0
    for cid, title, fn in OFFLINE_CHECKS:
        if only and cid != only:
            continue
        try:
            ok, msg = fn()
        except Exception as exc:                      # 校验器自己坏掉也是失败
            ok, msg = False, f"{type(exc).__name__}: {exc}"
        print(f"{'PASS' if ok else 'FAIL'}  {cid}  {title} —— {msg}")
        ran += 1
        failed += 0 if ok else 1
    print(f"\n## 汇总\n{ran - failed}/{ran} passed, {failed} failed")
    return 1 if failed else 0


# ---------------------------------------------------------------- 入口


def parse_args(argv: list[str]):
    import argparse
    argv = list(argv)
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    ap = argparse.ArgumentParser(prog="xbot_balance.py")
    ap.add_argument("--blend", default=None, help="样本 .blend（Blender 侧读产物用）")
    ap.add_argument("--action", default=None, help="要读的动作名")
    ap.add_argument("--report", default=None, help="报告 JSON 落点")
    ap.add_argument("--markdown", default=None, help="证据 markdown 段落落点")
    ap.add_argument("--name", default=None, help="样本名（写进 markdown 段）")
    ap.add_argument("--fps", type=int, default=None)
    ap.add_argument("--no-skin", action="store_true", help="不读蒙皮对照层（更快）")
    ap.add_argument("--verify", action="store_true", help="离线机械校验（B1–B5）")
    ap.add_argument("--only", default=None, help="只跑某一条离线判据（如 B4）")
    ap.add_argument("--format", default=None, help="占位：编排器可能传 --format json")
    return ap.parse_args(argv)


def main() -> int:
    args = parse_args(list(sys.argv))
    if args.blend:
        report = read_action(args.blend, args.action, fps=args.fps, with_skin=not args.no_skin)
        st = report["结构"]
        print(f"样本：{args.blend} · 动作 `{args.action}` · 帧 {st['帧范围'][0]}–{st['帧范围'][1]} "
              f"（{report['fps']} fps）· Blender {report['blender']}")
        for layer in LAYERS:
            s = st[layer]
            print(f"  {layer}：可判 {s['可判帧数']}/{st['帧数']} 帧 · 域内 {s['域内帧数']} · "
                  f"域外 {s['域外帧数']} {_fr_cell(s['域外帧'])} · 退化 {len(s['退化帧'])} · "
                  f"余量最小 {s['余量最小_mm']} mm（帧 {s['余量最小帧']}）")
        print(f"  层选对照：可比 {st['层选对照']['可比帧数']} 帧 · 判定不一致 "
              f"{len(st['层选对照']['判定不一致帧'])} 帧 · 最大余量差 "
              f"{st['层选对照']['最大余量差_mm']} mm（帧 {st['层选对照']['最大余量差帧']}）")
        cps = report["接触相位"]
        print(f"  接触相位（引用 #165 的件）：左 {_iv(cps['支撑区间']['左'])} · "
              f"右 {_iv(cps['支撑区间']['右'])} · 双支撑 {_iv(cps['双支撑区间'])} · "
              f"无支撑 {_iv(cps['无支撑区间'])} · 换脚帧 {_fr_cell(cps['换脚帧'])}")
        print(f"  未出现：{' · '.join(st['未出现的类别']) or '—'}")
        print(f"  读数指纹 sha256 = {report['读数指纹_sha256']}")
        for p in report["problems"]:
            print(f"  [PROBLEM] {p}")
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
            print(f"报告：{args.report}")
        if args.markdown:
            sample = {"id": args.name or Path(args.blend).stem, "名称": args.name or "样本",
                      "动作": args.action, "样本文件": args.blend, "fps": report["fps"],
                      "帧范围": st["帧范围"], "逐帧": report["逐帧"], "结构": st,
                      "接触相位": report["接触相位"]}
            Path(args.markdown).write_text(sample_markdown(sample), encoding="utf-8")
            print(f"markdown：{args.markdown}")
        return 1 if report["problems"] else 0
    return main_verify(args.only)


if __name__ == "__main__":
    sys.exit(main())
