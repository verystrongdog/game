#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 verystrongdog
# SPDX-License-Identifier: GPL-3.0-or-later
"""xbot_contact_phase.py —— **接触相位识别件**（脚支撑区间）：从一条动作算出「哪只脚在撑着、从哪一帧到哪一帧」。

## 权威来源（本件的定义**逐字**取自这两处，不得自行发挥）

**① 术语定义**（`data/term_registry.json` 的 `接触相位` 条目，2026-09-15 入库，**逐字**——R1 每次门禁核它）：

> 一次动作里「**哪只脚在撑着、从哪一帧到哪一帧**」这一层状态。两个已入库术语的**共同前置**：`重心` 的判据部分要用它构出支撑多边形，`脚滑` 的 M5 取帧范围由它给出。✅ **件已建**（2026-09-15，[#165](https://github.com/verystrongdog/game/issues/165)；本句由 [#167](https://github.com/verystrongdog/game/issues/167) 刷新）：`code/tools/xbot_contact_phase.py`——逐帧从**产物**（约束求值后的骨/蒙皮）读、按 M2 取点口径 + `soleMargin = 0.0028 m` 判接触，给出逐脚支撑区间 / 双支撑 / 无支撑 / 换脚帧；离线判据 R1–R5 已进 `run_all_checks.py` 与 CI。⚠️ **消费方尚未接上**：`重心` 的判据部分与 `脚滑` 的 M5 取帧范围**仍没接它**（现有 M5 读数仍是 lab 里**手选接触帧**算的）；§2.2 已有的定帧规则（41 点采样 + `argmax`）定的是**手**到位那一帧（右拳相对髋最前伸），**不是脚的落地相位**。

🔧 **2026-09-15 第七批（[#167](https://github.com/verystrongdog/game/issues/167)）已刷新**：本件落地后
该条目那句「⚠️ **本仓未建**」不再成立 ⇒ 改为「**✅ 件已建 · ⚠️ 消费方尚未接上**」两分记（**事实句刷新，
语义与边界不变**）。刷新时 **R1 确实报了红**（实测：改注册表、未同步本文件的那一版报
`注册表 \`接触相位\` 定义**未逐字出现**：前 84 字一致，第 85 字起分歧`），同步本行后即绿——
**这条判据的用法就是"改一边必红、两边同改才绿"**（R1 是那次的现场证据，不是事后声明）。

⇒ 本件把它落成**两个逐脚独立的布尔序列**（不是"某一时刻撑着的那只脚"这个单值）：

| 口径问题 | 本件的答案 | 依据 |
|---|---|---|
| **哪只脚** | **逐脚各一条**指示序列（左 / 右彼此独立，允许同时为真） | 条目正文"哪只脚在撑着"是**逐脚**的问法；两条序列同时为真即**双支撑** |
| **从哪一帧到哪一帧** | 该序列的**极大连续真区间**（帧号**闭**区间；**不设最小长度门槛**） | 本仓禁无来源阈值（[项目规约 §二](../../design/conventions/README.md)）⇒ 除容差外不引入第二个数 |
| **双支撑** | = 两条序列的**交集**（同一帧上两脚都在支撑） | ⚠️ **注册表条目没有写这一档**（见下"登记"）——交集是"逐脚区间"唯一的读法，**不新增术语** |

**登记（不修注册表）**：`接触相位` 的 `definition` 只定义了逐脚区间，**未定义双支撑**；本件的双支撑是
**派生量**（交集），并在证据里如实登记这一事实。#165 的「预期差分」明写 `data/term_registry.json`
**不新增或修改任何术语条目** ⇒ 本件不动注册表（若 owner 要把双支撑升为术语，另开一件）。

**② 接触判据的取点与容差**（两处，**都沿用既有来源，本件不新拍任何数**）：

| 项 | 值 | 来源（逐字） |
|---|---|---|
| 足底最低点 | 该脚「**足骨 y**」与「**趾骨 y**」的**较小者** − 地面 y | [动画处理能力对照实验 §三 M2](../../design/presentation/动画处理能力对照实验.md)（"该脚「足骨 y」与「趾骨 y」的**较小者** − 地面 y；负 = 陷入"） |
| 接触容差 | **`soleMargin = 0.0028 m`**（2.8 mm） | `code/unity/Assets/Scripts/FootGroundingIK.cs` 注释："2026-09-12 bind pose 趾骨 Y = +0.0028 实测"；同一常量被 [对照实验 §2.1](../../design/presentation/动画处理能力对照实验.md) 引为共同样本固定项 |
| 地面 | **世界 z = 0** 的过原点水平面 | 对照实验 §2.1"地面基平面，表面 y = 0"（Unity 世界 y ↔ Blender 世界 z：本件实测母版静息左足骨 **87.2949 mm** ↔ 管线 §六·3 记的 Unity 侧帧 0 **87.30 mm**，差 0.005 mm——见证据 §5.2） |

判据：`min(足骨, 趾骨) − 0 ≤ 2.8 mm` ⇒ **接触**（含"陷入"：负值同样算接触，因为脚确实在地上）。
⚠️ 本件**只报读数与相位**，**不判"站得稳不稳"**（那是 `重心` / `支撑多边形` 的判据面，需 owner 目视）。

## 两种跑法

| 模式 | 触发 | 干什么 | 谁用 |
|---|---|---|---|
| **Blender 侧读产物** | `--blend <样本> --action <名>`（须在 Blender 里跑） | 逐帧求值那条动作，读**约束求值后**的骨（与蒙皮对照层），算出相位结构，写报告 + markdown | #165 的三个样本（探针 / 门边 / 抓椅背对照） |
| **离线机械校验** | 无参数 / `--verify`（`--only R4` 只跑一条；纯 Python，不需要 bpy） | 对本仓库的文件跑 R1–R5（见下），进 `run_all_checks.py` 与 CI | 门禁 `docs-integrity` |

### 取帧口径（Blender 侧，**必须照此**，否则读数不可比）

1. **先清空姿势**（`rotation_mode` **不许动**——探针动作写在 `rotation_euler` 通道上，改成四元数会让键**静默失效**，
   见 [危险点表 §四](../../design/engineering/危险点表.md) 与 [管线 §七·3](../../design/presentation/Blender动作制作管线.md)）；
2. 用 `blender_action_compat.assign_action` 指派动作（Blender 5.x 槽位化动作**必须再指 slot**，否则不驱动任何东西）；
3. `scene.frame_set(f)` + `view_layer.update()`，从 **`object.evaluated_get(depsgraph)`** 读骨的世界位置
   ⇒ 这是**产物**（约束/驱动求值之后），不是求解器里那个目标值（中间量）。

### 离线判据 R1–R5

| id | 判据 | 防的是什么 |
|---|---|---|
| **R1** | 注册表 `接触相位.definition` 的全文**逐字**出现在本文件 docstring 里 | 定义漂移（改了注册表不同步本件 ⇒ 本件的相位定义失据） |
| **R2** | `FootGroundingIK.cs` 里的 `soleMargin` 与 `SOLE_MARGIN_M` **逐值相同** | 容差被悄悄改数（本仓禁无来源阈值） |
| **R3** | 对照实验 §三 M2 行仍写着"足骨 y 与趾骨 y 的**较小者**" + §2.1 仍引 `soleMargin = 0.0028 m` | 取点口径被改而本件不知 |
| **R4** | 证据里的**逐帧读数表** → 用本件的纯算法重算 ⇒ 与证据里**声明的**区间 / 换脚帧 / 双支撑**逐值一致** | 文档与算法漂移（表格是入库的真值，必须能重算） |
| **R5** | 三组合成序列（换脚 / 全程双支撑 / 全程无接触）逐项断言 + **markdown 往返**（发射→解析→重算逐值不变） | 算法静默退化（"零相位的绿"） |

⚠️ **R4 覆盖边界**（诚实清单）：它判的是**证据表 ↔ 算法**一致，**判不了**"那条动作的相位本身对不对"——
后者是 owner 目视与下游（#166）的面。R4 也**不重跑 Blender**（CI 上无 Blender 可用）。

来源：issue [#165](https://github.com/verystrongdog/game/issues/165)（`code/tools/` 下原无接触相位识别模块）；
[动作描述口径 §1.1](../../design/presentation/动作描述口径.md) 的**乙-触发器 ②**（同一个量被 ≥3 处要求 ⇒ 以「件」的形态建）；
消费方 = 口径 §13.6 门边「推到底」（[#166](https://github.com/verystrongdog/game/issues/166)）与 `重心` / `脚滑` / `悬空` 的判据面。
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

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------- 常量（全部带来源）

#: 接触容差。来源：`code/unity/Assets/Scripts/FootGroundingIK.cs` 注释
#: "2026-09-12 bind pose 趾骨 Y = +0.0028 实测"；对照实验 §2.1 把它引为共同样本固定项（"足底余量"）。
#: ⚠️ 本件**不新拍**这个数：R2 会在每次门禁里逐值核它。
SOLE_MARGIN_M = 0.0028
SOLE_MARGIN_MM = SOLE_MARGIN_M * 1000.0            # 2.8 mm

#: 地面基准：过原点的水平面。来源：对照实验 §2.1「地面基平面，表面 y = 0」
#: （Unity 世界 y ↔ Blender 世界 z——本件实测锚点见 docstring 的表格）。
GROUND_Z_M = 0.0

#: `mixamorig:` 前缀与两侧的取点骨。来源：对照实验 §三 M2 的"足骨 / 趾骨"。
BONE_PREFIX = "mixamorig:"
SIDES = ("Left", "Right")
SIDE_OF = {"Left": "左", "Right": "右"}
FOOT_BONE = "Foot"
TOE_BONE = "ToeBase"

#: 蒙皮对照层的顶点组前缀——**只取可见皮肤层 `Beta_Surface`**（`Beta_Joints` 是骨骼可视化网格，
#: 混进来会污染读数，见 author_xbot_chair_grab.py 的 hand_skin_points 注①）。
SKIN_MESH = "Beta_Surface"

#: 证据文件（R4 的判定面）与本件在文档里的机器标记
EVIDENCE_PATH = "design/engineering/evidence/xbot-contact-phase-2026-09-15.md"
SAMPLE_BEGIN = "<!-- contact-phase:sample={} -->"
SAMPLE_END = "<!-- /contact-phase:sample -->"

#: 离线判据读的三个既有来源文件
SRC_REGISTRY = "data/term_registry.json"
SRC_FOOT_IK = "code/unity/Assets/Scripts/FootGroundingIK.cs"
SRC_COMPARE = "design/presentation/动画处理能力对照实验.md"

TERM = "接触相位"

# ---------------------------------------------------------------- 纯算法（无 bpy 依赖）

#: 区间在 markdown 里的写法：`[1,3] [50,61]`；空集一律写这个字面量（验收标准要求"显式报告未出现"）
EMPTY_CELL = "未出现"


def lowest_point_mm(foot_z_m: float, toe_z_m: float, ground_z_m: float = GROUND_Z_M) -> float:
    """足底最低点相对地面的高度（mm）。**来源：对照实验 §三 M2**——"足骨 y 与趾骨 y 的较小者 − 地面 y"。

    负 = 陷入地面。
    """
    return (min(foot_z_m, toe_z_m) - ground_z_m) * 1000.0


def is_contact(lowest_mm: float, margin_mm: float = SOLE_MARGIN_MM) -> bool:
    """该帧该脚是否**在支撑**。判据：最低点 ≤ `soleMargin`（**含陷入**——脚确实在地上）。"""
    return lowest_mm <= margin_mm


def intervals_of(flags: list[bool]) -> list[list[int]]:
    """布尔序列 → **极大连续真区间**，帧号从 1 起（闭区间）。

    不设最小长度门槛：1 帧的支撑也是支撑（本仓禁无来源阈值）。
    """
    out: list[list[int]] = []
    start = None
    for i, f in enumerate(flags, start=1):
        if f and start is None:
            start = i
        elif not f and start is not None:
            out.append([start, i - 1])
            start = None
    if start is not None:
        out.append([start, len(flags)])
    return out


def switch_frames(left: list[bool], right: list[bool]) -> list[int]:
    """**换脚帧** = 支撑脚集合发生变化的那一帧（离地 / 落地各计一次）。

    集合形态：`{}` 无支撑 · `{L}` · `{R}` · `{L,R}` 双支撑。
    """
    out = []
    prev = None
    for i, (l, r) in enumerate(zip(left, right), start=1):
        cur = frozenset(s for s, v in (("左", l), ("右", r)) if v)
        if prev is not None and cur != prev:
            out.append(i)
        prev = cur
    return out


def complement(flags: list[bool]) -> list[bool]:
    return [not f for f in flags]


def summarize(frames: list[dict]) -> dict:
    """逐帧读数（含 `左最低_mm` / `右最低_mm`）→ 相位结构。

    `frames` 每项形如 `{"帧": f, "左最低_mm": x, "右最低_mm": y, ...}`（顺序即帧顺序）。
    """
    left = [is_contact(r["左最低_mm"]) for r in frames]
    right = [is_contact(r["右最低_mm"]) for r in frames]
    both = [l and r for l, r in zip(left, right)]
    only_l = [l and not r for l, r in zip(left, right)]
    only_r = [r and not l for l, r in zip(left, right)]
    none = complement([l or r for l, r in zip(left, right)])

    def depth(side_key: str) -> dict:
        vals = [(r["帧"], r[side_key]) for r in frames]
        lo = min(vals, key=lambda t: t[1])
        hi = max(vals, key=lambda t: t[1])
        return {"最低_mm": round(lo[1], 3), "最低帧": lo[0],
                "最高_mm": round(hi[1], 3), "最高帧": hi[0],
                "陷入帧数": sum(1 for _, v in vals if v < 0.0),
                "陷入最深_mm": round(min(0.0, lo[1]), 3)}

    struct = {
        "帧范围": [frames[0]["帧"], frames[-1]["帧"]] if frames else [0, 0],
        "帧数": len(frames),
        "支撑区间": {"左": intervals_of(left), "右": intervals_of(right)},
        "接触帧数": {"左": sum(left), "右": sum(right)},
        "读数极值": {"左": depth("左最低_mm"), "右": depth("右最低_mm")},
        "双支撑区间": intervals_of(both),
        "单支撑区间": {"仅左": intervals_of(only_l), "仅右": intervals_of(only_r)},
        "无支撑区间": intervals_of(none),
        "换脚帧": switch_frames(left, right),
    }
    # 「未出现」必须显式列出（验收标准：不得静默省略）
    absent = []
    for label, iv in (("双支撑", struct["双支撑区间"]),
                      ("仅左单支撑", struct["单支撑区间"]["仅左"]),
                      ("仅右单支撑", struct["单支撑区间"]["仅右"]),
                      ("无支撑", struct["无支撑区间"]),
                      ("换脚帧", struct["换脚帧"]),
                      ("左支撑", struct["支撑区间"]["左"]),
                      ("右支撑", struct["支撑区间"]["右"])):
        if not iv:
            absent.append(label)
    struct["未出现的类别"] = absent
    return struct


# ---------------------------------------------------------------- markdown（发射 + 解析，互为逆）

def _iv_cell(ivs: list) -> str:
    if not ivs:
        return EMPTY_CELL
    return " ".join(f"[{iv[0]},{iv[1]}]" if isinstance(iv, (list, tuple)) else str(iv)
                    for iv in ivs)


def _num_cell(v: float) -> str:
    return f"{v:+.2f}" if v >= 0 else f"{v:.2f}"


def sample_markdown(sample: dict) -> str:
    """一个样本 → markdown 段（`R4` 会把它解析回来重算）。"""
    frames, struct = sample["逐帧"], sample["结构"]
    sid = sample["id"]
    lines = [
        SAMPLE_BEGIN.format(sid),
        f"#### 样本 {sid}：{sample['名称']}",
        "",
        f"- 动作：`{sample['动作']}`（帧 {struct['帧范围'][0]}–{struct['帧范围'][1]}，{sample['fps']} fps）",
        f"- 样本文件：`{sample['样本文件']}`",
        f"- 容差：`soleMargin = {SOLE_MARGIN_MM:.1f} mm`（来源见本件 docstring；地面 = 世界 z 0）",
        "",
        "| 帧 | 左足底最低 (mm) | 左蒙皮最低 (mm) | 左接触 | 右足底最低 (mm) | 右蒙皮最低 (mm) | 右接触 |",
        "|---:|---:|---:|:--:|---:|---:|:--:|",
    ]
    for r in frames:
        def skin(key):
            v = r.get(key)
            return "—" if v is None else _num_cell(v)
        lines.append(f"| {r['帧']} | {_num_cell(r['左最低_mm'])} | {skin('左蒙皮最低_mm')} | "
                     f"{'✅' if is_contact(r['左最低_mm']) else '—'} | "
                     f"{_num_cell(r['右最低_mm'])} | {skin('右蒙皮最低_mm')} | "
                     f"{'✅' if is_contact(r['右最低_mm']) else '—'} |")
    lines += [
        "",
        "| 派生结构 | 左 | 右 |",
        "|---|---|---|",
        f"| 支撑区间 | {_iv_cell(struct['支撑区间']['左'])} | {_iv_cell(struct['支撑区间']['右'])} |",
        f"| 接触帧数 | {struct['接触帧数']['左']} | {struct['接触帧数']['右']} |",
        "",
        "| 派生结构 | 值 |",
        "|---|---|",
        f"| 双支撑区间 | {_iv_cell(struct['双支撑区间'])} |",
        f"| 单支撑区间（仅左） | {_iv_cell(struct['单支撑区间']['仅左'])} |",
        f"| 单支撑区间（仅右） | {_iv_cell(struct['单支撑区间']['仅右'])} |",
        f"| 无支撑区间 | {_iv_cell(struct['无支撑区间'])} |",
        f"| 换脚帧 | {_iv_cell(struct['换脚帧'])} |",
        f"| 未出现的类别 | {' · '.join(struct['未出现的类别']) or '—'} |",
        "",
        SAMPLE_END,
    ]
    return "\n".join(lines)


def _iv_cell_list(cell: str) -> list:
    """`[1,3] [49,61]` → `[[1,3],[49,61]]`（空集 / `未出现` ⇒ `[]`）。"""
    if cell.strip() in ("", "—", "-", EMPTY_CELL):
        return []
    return [[int(a), int(b)] for a, b in re.findall(r"\[(\d+),(\d+)\]", cell)]


def _frames_cell_list(cell: str) -> list:
    """`4, 7, 49, 56` → `[4,7,49,56]`（空集 / `未出现` ⇒ `[]`）。"""
    if cell.strip() in ("", "—", "-", EMPTY_CELL):
        return []
    return [int(x) for x in re.findall(r"\d+", cell)]


def parse_sample_markdown(text: str) -> list[dict]:
    """证据文档里所有 `contact-phase:sample` 段 → 可重算的结构（R4 的输入）。"""
    out = []
    for m in re.finditer(re.escape("<!-- contact-phase:sample=") + r"([^ ]+?) -->(.*?)"
                         + re.escape(SAMPLE_END), text, re.S):
        sid, body = m.group(1), m.group(2)
        rows = {}
        # 逐帧表：七列 —— 帧 · 左骨点 · 左蒙皮 · 左接触 · 右骨点 · 右蒙皮 · 右接触
        # （相位只由**骨点层**算：那是 M2 的取点口径；蒙皮层是对照读数，本件不用它判相位）
        for line in body.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 7 and cells[0].isdigit() and cells[3] in ("✅", "—"):
                rows[int(cells[0])] = {"帧": int(cells[0]),
                                       "左最低_mm": float(cells[1]),
                                       "右最低_mm": float(cells[4]),
                                       "左蒙皮最低_mm": None if cells[2] == "—" else float(cells[2]),
                                       "右蒙皮最低_mm": None if cells[5] == "—" else float(cells[5])}
        frames = [rows[k] for k in sorted(rows)]
        # 派生结构表（键值两列 + 三列那两张）
        declared: dict[str, str] = {}
        for line in body.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 3 and cells[0] in ("支撑区间", "接触帧数"):
                declared["左·" + cells[0]] = cells[1]
                declared["右·" + cells[0]] = cells[2]
            elif len(cells) == 2 and cells[0] in (
                    "双支撑区间", "单支撑区间（仅左）", "单支撑区间（仅右）",
                    "无支撑区间", "换脚帧", "未出现的类别"):
                declared[cells[0]] = cells[1]
        out.append({"id": sid, "逐帧": frames, "声明": declared})
    return out


# ---------------------------------------------------------------- Blender 侧：读产物

def _clear_pose(arm) -> None:
    """清空姿势。⚠️ **不动 `rotation_mode`**——探针动作写在 `rotation_euler` 通道上。"""
    for pb in arm.pose.bones:
        if pb.rotation_mode == "QUATERNION":
            pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        else:
            pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.location = (0.0, 0.0, 0.0)
    for _ in range(3):
        bpy.context.view_layer.update()


def _world_points(arm, bone: str) -> dict:
    """求值后的骨世界位置（**产物**）：head（骨心）与 tail（骨尖），单位 m。"""
    dg = bpy.context.evaluated_depsgraph_get()
    ae = arm.evaluated_get(dg)
    pb = ae.pose.bones[bone]
    return {"head": ae.matrix_world @ pb.head, "tail": ae.matrix_world @ pb.tail}


def _skin_index(arm, side: str) -> list[int]:
    """该脚在 `Beta_Surface` 上的蒙皮顶点下标（按**主导顶点组**落在该侧 Foot / ToeBase 上）。

    ⚠️ 与骨点层**不是同一个量**：蒙皮层是"看得见的皮肤"，骨点层是 M2 的取点口径。
    本件只把蒙皮层当**对照读数**报出（对照容差**没有来源** ⇒ 不用它判相位）。
    """
    names = {f"{BONE_PREFIX}{side}{FOOT_BONE}", f"{BONE_PREFIX}{side}{TOE_BONE}"}
    ob = bpy.data.objects.get(SKIN_MESH)
    if ob is None:
        return []
    gi = {vg.index: vg.name for vg in ob.vertex_groups}
    out = []
    for v in ob.data.vertices:
        best, bw = None, -1.0
        for r in v.groups:
            if r.weight > bw:
                best, bw = r.group, r.weight
        if gi.get(best) in names:
            out.append(v.index)
    return out


def _skin_lowest(arm, idx: list[int]) -> float | None:
    if not idx:
        return None
    dg = bpy.context.evaluated_depsgraph_get()
    ob = bpy.data.objects[SKIN_MESH].evaluated_get(dg)
    me = ob.to_mesh()
    try:
        mw = ob.matrix_world
        return min((mw @ me.vertices[i].co).z for i in idx)
    finally:
        ob.to_mesh_clear()


def read_action(blend: str, action_name: str, fps: int | None = None,
                with_skin: bool = True) -> dict:
    """逐帧求值一条动作 → 报告（Blender 侧入口）。"""
    if not HAS_BPY:
        raise RuntimeError("读产物需要 Blender（bpy 不可用）")
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import blender_action_compat as bac

    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(arms) != 1:
        raise RuntimeError(f"期望恰好 1 个 Armature，实测 {len(arms)}")
    arm = arms[0]
    act = bpy.data.actions.get(action_name)
    if act is None:
        raise RuntimeError(f"样本里没有动作 `{action_name}`；实测："
                           f"{[a.name for a in bpy.data.actions]}")

    if fps:
        bpy.context.scene.render.fps = fps

    # ---- 静息对照（无动作的底）：先解开动作、清空姿势再读，验证"地面 = 世界 z 0"这个参照系
    #      ⚠️ 顺序不能反：先指派动作再读，读数就是"动作在当前帧的值"而不是静息。
    arm.animation_data_clear()
    _clear_pose(arm)
    skin_idx = {s: _skin_index(arm, s) for s in SIDES} if with_skin else {s: [] for s in SIDES}
    rest = {}
    for s in SIDES:
        fp = _world_points(arm, f"{BONE_PREFIX}{s}{FOOT_BONE}")
        tp = _world_points(arm, f"{BONE_PREFIX}{s}{TOE_BONE}")
        sk = _skin_lowest(arm, skin_idx[s]) if skin_idx[s] else None
        rest[s] = {"足骨head_z_mm": fp["head"].z * 1000.0, "足骨tail_z_mm": fp["tail"].z * 1000.0,
                   "趾骨head_z_mm": tp["head"].z * 1000.0, "趾骨tail_z_mm": tp["tail"].z * 1000.0,
                   "最低_mm": lowest_point_mm(fp["head"].z, tp["head"].z),
                   "蒙皮最低_mm": None if sk is None else sk * 1000.0}

    ad = arm.animation_data_create()
    bac.assign_action(ad, act)

    f0, f1 = int(round(act.frame_range[0])), int(round(act.frame_range[1]))
    frames = []
    for f in range(f0, f1 + 1):
        bpy.context.scene.frame_set(f)
        for _ in range(3):
            bpy.context.view_layer.update()
        row = {"帧": f}
        for s in SIDES:
            fp = _world_points(arm, f"{BONE_PREFIX}{s}{FOOT_BONE}")
            tp = _world_points(arm, f"{BONE_PREFIX}{s}{TOE_BONE}")
            row[f"{s}_足骨_z_mm"] = round(fp["head"].z * 1000.0, 4)
            row[f"{SIDE_OF[s]}最低_mm"] = round(lowest_point_mm(fp["head"].z, tp["head"].z), 4)
            if skin_idx[s]:
                sk = _skin_lowest(arm, skin_idx[s])
                row[f"{SIDE_OF[s]}蒙皮最低_mm"] = round(sk * 1000.0, 4) if sk is not None else None
        frames.append(row)

    struct = summarize(frames)
    payload = {"逐帧": frames, "结构": struct}
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                       separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "script": Path(__file__).name,
        "blender": bpy.app.version_string,
        "compat": bac.describe(),
        "样本文件": str(blend),
        "动作": action_name,
        "fps": bpy.context.scene.render.fps,
        "容差_soleMargin_mm": SOLE_MARGIN_MM,
        "地面_z_m": GROUND_Z_M,
        "静息对照": rest,
        "读数指纹_sha256": digest,
        **payload,
    }


# ---------------------------------------------------------------- 离线判据 R1–R5

def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def check_r1() -> tuple[bool, str]:
    """注册表 `接触相位.definition` 全文逐字出现在本件 docstring 里。"""
    reg = json.loads(_read(SRC_REGISTRY))
    entry = None
    for bucket in reg.values():
        if isinstance(bucket, dict) and TERM in bucket and isinstance(bucket[TERM], dict):
            entry = bucket[TERM]
            break
    if entry is None:
        return False, f"注册表里找不到术语 `{TERM}`"
    definition = entry["definition"].strip()
    mine = Path(__file__).read_text(encoding="utf-8")
    if definition in mine:
        return True, f"注册表 `{TERM}` 定义（{len(definition)} 字）逐字出现在本件 docstring"
    # 找出第一处分歧，便于修
    for cut in range(len(definition), 0, -20):
        if definition[:cut] in mine:
            return False, (f"注册表 `{TERM}` 定义**未逐字出现**：前 {cut} 字一致，"
                           f"第 {cut + 1} 字起分歧（注册表：…{definition[cut:cut + 20]!r}）")
    return False, f"注册表 `{TERM}` 定义与本件 docstring 不一致（首 20 字就对不上：{definition[:20]!r}）"


def check_r2() -> tuple[bool, str]:
    """`FootGroundingIK.cs` 的 `soleMargin` 与 `SOLE_MARGIN_M` 逐值相同。"""
    src = _read(SRC_FOOT_IK)
    m = re.search(r"soleMargin\s*=\s*([0-9.]+)", src)
    if not m:
        return False, f"{SRC_FOOT_IK} 里找不到 soleMargin"
    val = float(m.group(1))
    if math.isclose(val, SOLE_MARGIN_M, rel_tol=0, abs_tol=1e-12):
        return True, f"soleMargin = {val} m 与本件常量逐值相同"
    return False, f"soleMargin 被改成 {val} m，本件常量仍是 {SOLE_MARGIN_M} m（本仓禁无来源阈值）"


def check_r3() -> tuple[bool, str]:
    """对照实验 §三 M2 的取点口径与 §2.1 的 soleMargin 引用仍在。"""
    src = _read(SRC_COMPARE)
    problems = []
    if "**较小者**" not in src and "较小者" not in src:
        problems.append("§三 M2 的『较小者』取点口径不见了")
    m = re.search(r"soleMargin\s*=\s*([0-9.]+)", src)
    if not m:
        problems.append("§2.1 不再引 `soleMargin`")
    elif not math.isclose(float(m.group(1)), SOLE_MARGIN_M, rel_tol=0, abs_tol=1e-12):
        problems.append(f"§2.1 的 soleMargin 被改成 {m.group(1)}")
    if "足骨" not in src or "趾骨" not in src:
        problems.append("M2 的『足骨 / 趾骨』取点词不见了")
    return (not problems), ("取点口径与容差引用均在位" if not problems else "；".join(problems))


def check_r5() -> tuple[bool, str]:
    """合成序列：算法不退化。"""
    cases = [
        # (左最低, 右最低, 期望：换脚帧, 双支撑, 无支撑)
        ([0, 0, 5, 20, 5, 0, 0], [0, 0, 0, 20, 20, 2, 0], [3, 4, 6], [[1, 2], [6, 7]], [[4, 5]]),
        ([0, 1, 2, 0], [0, 1, 2, 0], [], [[1, 4]], []),
        ([5, 9, 30], [6, 9, 30], [], [], [[1, 3]]),
    ]
    for i, (l, r, want_sw, want_both, want_none) in enumerate(cases, start=1):
        frames = [{"帧": k + 1, "左最低_mm": a, "右最低_mm": b} for k, (a, b) in enumerate(zip(l, r))]
        st = summarize(frames)
        got = (st["换脚帧"], st["双支撑区间"], st["无支撑区间"])
        want = (want_sw, want_both, want_none)
        if got != want:
            return False, f"合成用例 {i} 不符：期望 {want}，实得 {got}"
        # markdown 往返（R4 的机制本身也要自测）：发射 → 解析 → 重算 ⇒ 逐值不变
        md = sample_markdown({"id": f"合成{i}", "名称": "合成", "动作": "synthetic",
                              "样本文件": "(合成)", "fps": 30, "逐帧": frames, "结构": st})
        back = parse_sample_markdown(md)
        got_frames = [{"帧": r["帧"], "左最低_mm": r["左最低_mm"], "右最低_mm": r["右最低_mm"]}
                      for r in (back[0]["逐帧"] if back else [])]
        if len(back) != 1 or got_frames != frames:
            return False, f"合成用例 {i}：markdown 往返后逐帧表变了（解析到 {len(back)} 段）"
        st2 = summarize(back[0]["逐帧"])
        if st2 != st:
            return False, f"合成用例 {i}：markdown 往返后结构变了：{st2} != {st}"
    return True, f"{len(cases)} 组合成序列逐项相符 + markdown 往返逐值一致"


def check_r4() -> tuple[bool, str]:
    """证据里的逐帧表 → 纯算法重算 ⇒ 与文档里声明的结构逐值一致。"""
    path = REPO_ROOT / EVIDENCE_PATH
    if not path.is_file():
        return False, f"证据文件不存在：{EVIDENCE_PATH}"
    text = path.read_text(encoding="utf-8")
    samples = parse_sample_markdown(text)
    if not samples:
        return False, f"{EVIDENCE_PATH} 里没有解析到任何 `contact-phase:sample` 段"
    problems = []
    for s in samples:
        if not s["逐帧"]:
            problems.append(f"样本 {s['id']}：逐帧表解析为空")
            continue
        st = summarize(s["逐帧"])
        want_iv = {
            "左·支撑区间": st["支撑区间"]["左"],
            "右·支撑区间": st["支撑区间"]["右"],
            "双支撑区间": st["双支撑区间"],
            "单支撑区间（仅左）": st["单支撑区间"]["仅左"],
            "单支撑区间（仅右）": st["单支撑区间"]["仅右"],
            "无支撑区间": st["无支撑区间"],
        }
        want_frames = {
            "左·接触帧数": [st["接触帧数"]["左"]],
            "右·接触帧数": [st["接触帧数"]["右"]],
            "换脚帧": st["换脚帧"],
        }
        for k, v in want_iv.items():
            d = s["声明"].get(k)
            if d is None:
                problems.append(f"样本 {s['id']}：文档缺声明行 `{k}`")
            elif _iv_cell_list(d) != [list(iv) for iv in v]:
                problems.append(f"样本 {s['id']}：`{k}` 文档写 {d.strip()!r}，重算得 {_iv_cell(v)}")
        for k, v in want_frames.items():
            d = s["声明"].get(k)
            if d is None:
                problems.append(f"样本 {s['id']}：文档缺声明行 `{k}`")
            elif _frames_cell_list(d) != v:
                problems.append(f"样本 {s['id']}：`{k}` 文档写 {d.strip()!r}，重算得 {_iv_cell(v)}")
        absent_doc = s["声明"].get("未出现的类别", "").strip()
        absent_calc = " · ".join(st["未出现的类别"]) or "—"
        if absent_doc != absent_calc:
            problems.append(f"样本 {s['id']}：`未出现的类别` 文档写 {absent_doc!r}，重算得 {absent_calc!r}")
    if problems:
        return False, "；".join(problems[:6])
    return True, f"{len(samples)} 个样本的逐帧表重算与文档声明逐值一致"


OFFLINE_CHECKS = (
    ("R1", "注册表 `接触相位` 定义逐字一致", check_r1),
    ("R2", "`soleMargin` 容差沿用既有来源", check_r2),
    ("R3", "M2 取点口径仍在位", check_r3),
    ("R4", "证据逐帧表可重算", check_r4),
    ("R5", "合成序列自测", check_r5),
)


def main_verify(only: str | None = None) -> int:
    print(f"# {Path(__file__).name} —— 离线机械校验（接触相位识别件）\n")
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
    # Blender 会把 `--` 之后的参数留给脚本；裸跑（编排器 / CI）时取 `argv[1:]`。
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    ap = argparse.ArgumentParser(prog="xbot_contact_phase.py")
    ap.add_argument("--blend", default=None, help="样本 .blend（Blender 侧读产物用）")
    ap.add_argument("--action", default=None, help="要读的动作名")
    ap.add_argument("--report", default=None, help="报告 JSON 落点")
    ap.add_argument("--markdown", default=None, help="证据 markdown 段落落点")
    ap.add_argument("--name", default=None, help="样本名（写进 markdown 段）")
    ap.add_argument("--fps", type=int, default=None)
    ap.add_argument("--no-skin", action="store_true", help="不读蒙皮对照层（更快）")
    ap.add_argument("--verify", action="store_true", help="离线机械校验（R1–R5）")
    ap.add_argument("--only", default=None, help="只跑某一条离线判据（如 R4）")
    ap.add_argument("--format", default=None, help="占位：编排器可能传 --format json")
    return ap.parse_args(argv)


def main() -> int:
    args = parse_args(list(sys.argv))
    if args.blend:
        report = read_action(args.blend, args.action, fps=args.fps, with_skin=not args.no_skin)
        if args.name:
            report["样本名"] = args.name
        st = report["结构"]
        print(f"样本：{args.blend} · 动作 `{args.action}` · 帧 {st['帧范围'][0]}–{st['帧范围'][1]} "
              f"（{report['fps']} fps）· Blender {report['blender']}")
        for s in SIDES:
            print(f"  {SIDE_OF[s]}脚 支撑区间 {_iv_cell(st['支撑区间'][SIDE_OF[s]])} · "
                  f"接触帧 {st['接触帧数'][SIDE_OF[s]]}/{st['帧数']} · "
                  f"最低 {st['读数极值'][SIDE_OF[s]]['最低_mm']:+.2f} mm"
                  f"（帧 {st['读数极值'][SIDE_OF[s]]['最低帧']}）")
        print(f"  双支撑 {_iv_cell(st['双支撑区间'])} · 无支撑 {_iv_cell(st['无支撑区间'])} · "
              f"换脚帧 {_iv_cell(st['换脚帧'])} · 未出现：{' · '.join(st['未出现的类别']) or '—'}")
        print(f"  读数指纹 sha256 = {report['读数指纹_sha256']}")
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
            print(f"报告：{args.report}")
        if args.markdown:
            sample = {"id": args.name or Path(args.blend).stem, "名称": args.name or "样本",
                      "动作": args.action, "样本文件": args.blend, "fps": report["fps"],
                      "逐帧": report["逐帧"], "结构": st}
            Path(args.markdown).write_text(sample_markdown(sample), encoding="utf-8")
            print(f"markdown：{args.markdown}")
        return 0
    return main_verify(args.only)


if __name__ == "__main__":
    sys.exit(main())
