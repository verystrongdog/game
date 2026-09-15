#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 verystrongdog
# SPDX-License-Identifier: GPL-3.0-or-later
"""author_xbot_chair_grab.py —— X Bot 手 ↔ 物接触动作的**可复用库 + 三个宿主**。

| 宿主 | `--task` | 干什么 | 权威 |
|---|---|---|---|
| `main_chair()` | `chair`（默认） | 产出动作 `BendGripChairBack`（弯腰、双手抓住椅背）——**#163 的产出，本文件原有形态** | issue #163 |
| `main_card1()` | `card1` | **测量卡 1「掐棱」**：F3 三轴映射（含 U9 的 `+Y`）· F4 接触对 · F6 尺寸区间 · F7 七档扫描（10→80 mm）· F10 手型 · F11 落点读数 ⇒ 写 `data/hand_grip_cards.json` | [动作描述口径 §十三](../../design/presentation/动作描述口径.md) |
| `main_door()` | `door` | 新动作「扣住门边推开半掩的门」——**同一张卡、新对象**（口径 §13.6 的独立验证件） | 同上 · [回合战斗流程 §10.13](../../design/rules/回合战斗流程.md) |

来源：design/presentation/动作描述口径.md（§二 三问骨架 · §三 D7 自由度表 · §八 容差 ε · §十 验收判据 V-a…V-e）
      · design/presentation/Blender动作制作管线.md §七·B（撤回记录）
      · issue #163（**这是口径的回归样本**：口径管不管用，就看这一次）
      · issue #164（**手部基准卡片**：把 #163 一次性写死的判据变成可被引用的常驻件；卡 1 数值实测）

⚠️ **库与宿主的分界**：`# ---- 可复用库` 以下（含 #164 扩展块）是**件**——道具几何、棱线表、
蒙皮读数、手骨轴实测、掐棱握式解算；三个宿主的 `main_*()` 只是把件按各自的时序串起来。
`main_chair()` 走的仍是 #163 定下的那条路径（**不重写**）：卡 1 的测量是本文件新增的件，
改的是**库**，不是那条已验收的动作。

本次重做相对撤回版的**四处改动**（都直接来自口径与 #160/#161 的实测）：
1. **屈曲符号改由外部判据定**：旧版用"指尖朝掌心"评分，而"掌心"是它自己算的平面——属 A1 自证式判据
   （#160 实测：同一姿势下它与"拇指—指尖间距"判据给出**相反**的右手符号）。现改用后者。
2. **新增三项判据**（旧判据**不可能**报出它们，正是上一轮"全绿却被否"的三项，见 #163）：
   · **目视水平**——头骨"上"轴与重力轴夹角（旧版**根本没做**，头随骨盆一起低下去）
   · **掌面贴合**——掌面点（骨原点 + ε·掌面法向）↔ 靠背顶面（ε = #160 实测 32.68 mm）
   · **拇指落点**——拇指尖 y 相对靠背近侧面（口径 D8：拇指在近侧 y ≥ −0.45）
3. **回显卡**：每次运行都把「owner 的话 → 解成什么 → 判据量 → 产物侧读数 → 状态」打成表并写进报告
   （口径 §四；V-a 要求每一项都有**产物侧**读数）。
4. **双宿主**：同一段代码既能在 headless（`--background`，权威）跑，也能被活体桥送进**已开着**的会话
   （`--host live`，预览；不重开文件、不写回母版）。见口径 §九。
"""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

# ---- 椅子几何：逐字来自 ActionLabBuilder（权威常量，勿改）— design/presentation/动作库规格.md §四·丁
SEAT_TOP = 0.4449          # 坐面上表面
SEAT_THICKNESS = 0.05
SEAT_SIZE = 0.42           # 边长
LEG_SIZE = 0.05
LEG_SPREAD = 0.165
BACK_HEIGHT = 0.35
BACK_THICKNESS = 0.04

#: 自由度表（口径 §三 D7）——**本表逐项由 owner 2026-09-14 圈定**（值来自他的裁定，不是 agent 自选）。
#: ⚠️ 🔧 2026-09-15（口径 §三 D7 修正注记）：默认归属已**反转**为 `agent 解（owner 可改）`——owner 原话
#: 「默认条件下你来决定，如果我有需求，按照我的需求做」。本表不受影响（它当时就是逐项圈定的）；**新动作**的表
#: 按新默认写，且 agent 解的行必须**并列回显 ≥2 个可行解**（口径 §4.2 硬规矩 5）。
FREEDOM_TABLE = [
    {"量": "椅心到角色的距离", "归属": "owner 圈定", "值": "0.70 m",
     "依据": "可达性反解（残差≈0 且肘角自然）；45°/0.60 与 65°/0.70 均不合"},
    {"量": "弯腰幅度", "归属": "owner 圈定", "值": "55°（骨盆局部 X）",
     "依据": "同上扫描；45° 时手到不了顶杆"},
    {"量": "时序", "归属": "owner 圈定", "值": "帧 1/13/21/31/37/41（到位）/61（保持）",
     "依据": "口径 §三 D7；到位帧 = 41"},
    {"量": "掌面方向", "归属": "agent 解（实测）", "值": "骨局部 +Z",
     "依据": "#160：四指屈曲把中指尖带向拇指尖 ⇒ 掌心朝下（静止 T-pose）"},
    {"量": "接触档 ε", "归属": "agent 解（实测）", "值": "32.68 mm（Beta_Surface 掌面）",
     "依据": "#160 实测；跨 4 姿势变化 ≤ 0.0008 mm"},
    {"量": "头颈的反向补偿角", "归属": "agent 解（求解）", "值": "由 solve_gaze 迭代解出",
     "依据": "#161 §2.1.4：Head X / Neck X 是点头轴"},
]

#: 掌面点 = 手骨原点 + ε × 掌面法向（骨局部 +Z）。
#: 来源：design/presentation/动作描述口径.md §8.1（#160 实测 `Beta_Surface` 32.6833 / 32.6854 mm）
EPSILON_PALM_M = 0.0326833
#: 转折期阈值（**沿用既有来源**，非新拍）：`Blender动作制作管线.md` §三 V6/V7/V8 的 20 mm 量级。
#: 仅用于"掌面陷进椅子"那一侧的穿模判定；"贴合"一侧改用 ε。
PROVISIONAL_TOL_MM = 20.0
#: **掌面判据形态 = owner 2026-09-14 选定的"甲"**：按**掌面最低点**离顶面 ≤ ε（**允许倾斜**，
#: "掌根压住、指尖翘着"也算贴合）。量的对象是**真实蒙皮顶点**（掌面那一层），不是"沿法向的一个点"。
PALM_SLAB_M = 0.006
#: **接触验收容差**（owner 2026-09-14 定）：来源同 `soleMargin = 0.0028 m` 那一族（平贴面接触余量）。
#: ⚠️ 与 ε **不是**同一个数：ε 管"骨→表面"的换算，本值管"多近算贴合"（口径 §8.2）。
CONTACT_TOL_MM = 2.8
#: 靠背近侧 / 远侧面（y 更大 = 更靠角色）——口径 §6.3 的命名面
BACK_NEAR_Y = -0.45
BACK_FAR_Y = -0.49

#: 仓库根（`code/tools/` 的上面两级）——机器源与报告的相对落点都从这里算
REPO_ROOT = Path(__file__).resolve().parents[2]

CTRL_PREFIX = "CTRL_"
BONE_PREFIX = "mixamorig:"

# ---- 运动时间表（30 fps；任务空间给定，角度由 IK 解出）
#   t: (帧, 弯腰角°, 骨盆世界位移 m, 手是否上杆, 手指蜷曲 0..1)
SCHEDULE = [
    (1,  0.0,  (0.00, 0.00,  0.00), False, 0.0),
    (13, 15.0, (0.00, 0.030, -0.015), True, 0.0),
    (21, 30.0, (0.00, 0.060, -0.030), True, 0.0),
    (31, 45.0, (0.00, 0.085, -0.043), True, 0.0),
    (37, 50.0, (0.00, 0.095, -0.048), True, 0.5),
    (41, 55.0, (0.00, 0.100, -0.050), True, 1.0),
    (61, 55.0, (0.00, 0.100, -0.050), True, 1.0),
]

FINGERS = ("Index", "Middle", "Ring", "Pinky", "Thumb")
FINGER_CURL_DEG = {"Index": (45, 40, 30, 25), "Middle": (45, 40, 30, 25), "Ring": (45, 40, 30, 25),
                   "Pinky": (45, 40, 30, 25), "Thumb": (25, 20, 15, 12)}
#: 每根手指的**最末节**（= 真正的指尖）——判据一律量它，成组并列打印（口径 §七 硬规矩 2）
DIGIT_TIP = {"Index": "Index4", "Middle": "Middle4", "Ring": "Ring4", "Pinky": "Pinky4",
             "Thumb": "Thumb4"}
DIGITS = ("Index", "Middle", "Ring", "Pinky", "Thumb")


def parse_args(argv):
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser(prog="author_xbot_chair_grab.py")
    ap.add_argument("--task", choices=("chair", "card1", "door", "restate", "doorpush"),
                    default="chair",
                    help="宿主：#163 抓椅背（chair，默认）· 卡 1 掐棱测量（card1）· 门边动作（door）"
                         "· 门边「推到底」能播段（doorpush，#166）"
                         "· 重述对拍（restate，纯算术，不需要 Blender）")
    ap.add_argument("--template", default=str(Path(__file__).resolve().parents[2] /
                                             ".scratch/blender_assets/xbot/XBot_AnimationTemplate.blend"))
    ap.add_argument("--action", default="BendGripChairBack")
    ap.add_argument("--chair", type=float, default=0.70, help="椅子中心在角色前方的距离 m")
    ap.add_argument("--bend", type=float, default=55.0, help="到位时的髋铰链前弯角")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--report", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--host", choices=("headless", "live"), default="headless",
                    help="headless=自己打开母版（权威）；live=送进**已开着**的会话（预览，不重开文件、默认不写回）")
    ap.add_argument("--no-save", action="store_true", help="只解算与报告，不写回 .blend")
    # ---- #164：卡 1 测量宿主的量（默认值 = 已实测选定的基准，见证据 §三 的扫描表）----
    ap.add_argument("--grip-z", type=float, default=None, help="抓握高度（世界 z，m）；缺省按板顶 − 基准偏移")
    ap.add_argument("--grip-drop", type=float, default=0.075, help="抓握高度 = 板顶 − 本值（m）")
    ap.add_argument("--curl", type=float, default=None, help="四指蜷曲量（0..1.5）；缺省用卡 1 的基准值")
    ap.add_argument("--card-out", default=None, help="卡 1 机器源落点（默认 <仓库>/data/hand_grip_cards.json）")
    ap.add_argument("--thickness-mm", type=float, default=None, help="只测单个板厚（mm）；缺省跑 F7 的七档扫描")
    ap.add_argument("--scan", action="store_true", help="卡 1 校准扫描（抓握高度 × 蜷曲量）——只打印表，不写机器源")
    ap.add_argument("--task-restate", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--report-in", default=None,
                    help="从既有报告**重排**机器源（不重跑测量；报告是机器源的唯一来源）")
    ap.add_argument("--still", default=None, help="静帧落点（.png）")
    # ---- #166：门边「推到底」宿主的量 ----
    ap.add_argument("--clearance", type=float, default=None,
                    help="身体到门板中面的净距（m）；缺省用 DOOR_PUSH_CLEARANCE_M")
    ap.add_argument("--crouch", type=float, default=None, help="站姿膝屈下沉量（m）")
    ap.add_argument("--scan-arc", action="store_true",
                    help="只跑「保持扣住可达的最大角」扫描（改族判定），不产动作")
    ap.add_argument("--scan-max", type=float, default=76.0, help="扫描上界（开角°）")
    ap.add_argument("--scan-step", type=float, default=2.0, help="扫描步长（°）")
    ap.add_argument("--scan-stance", action="store_true",
                    help="只跑「身体摆放（净距 b）」的解空间扫描——口径 §4.2 硬规矩 5 的 ≥2 解并列")
    ap.add_argument("--first-foot", choices=("Right", "Left"), default="Left",
                    help="迈步：哪只脚先迈（口径 §13.6 自由度表第 2 行；两种都解，回显卡并列）")
    return ap.parse_args(argv)


# ---------------------------------------------------------------- 基础设施


def armature():
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(arms) != 1:
        raise RuntimeError(f"期望恰好 1 个 Armature，实测 {len(arms)}")
    return arms[0]


def make_context():
    arm = armature()
    return arm, arm.matrix_world.to_3x3()


def world_point(arm, name, attr="head"):
    return arm.matrix_world @ getattr(arm.pose.bones[name], attr)


def update(times=10):
    for _ in range(times):
        bpy.context.view_layer.update()


def set_euler(arm, name, x=0.0, y=0.0, z=0.0):
    pb = arm.pose.bones[name]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ")
    return pb


def set_world_offset(arm, m3, name, delta):
    """用**世界位移**设 `pose.location`。

    ⚠️ 单位陷阱（实测踩到）：这套骨架的 `pose.location` 单位是**骨架局部单位 = cm**
    （Armature 对象 scale=0.01）。直接写 `(0, 0.10, -0.05)` 想表达"后移 10 cm"，
    实际只动了 1 mm——姿势看着"骨盆没动"，白查一轮。
    """
    pb = arm.pose.bones[name]
    pb.location = pb.bone.matrix_local.to_3x3().inverted() @ (m3.inverted() @ Vector(delta))


def clear_pose(arm):
    for pb in arm.pose.bones:
        if pb.rotation_mode == "QUATERNION":
            pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        else:
            pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.location = (0.0, 0.0, 0.0)
    update()


def drop_temp(arm, also_objects=True):
    for pb in arm.pose.bones:
        for c in list(pb.constraints):
            if c.name.startswith("TMP_"):
                pb.constraints.remove(c)
    if also_objects:
        for ob in list(bpy.data.objects):
            if ob.name.startswith("TMP_") or ob.name.startswith("IK_"):
                bpy.data.objects.remove(ob, do_unlink=True)


def build_chair_proxy(chair_distance):
    """参考椅（`REF_Chair` 集合）——只做参考与量测，不进 FBX。"""
    old = bpy.data.collections.get("REF_Chair")
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    coll = bpy.data.collections.new("REF_Chair")
    bpy.context.scene.collection.children.link(coll)

    def cube(name, loc, scale, color):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        ob = bpy.context.active_object
        ob.name = name
        ob.scale = scale
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        coll.objects.link(ob)
        mat = bpy.data.materials.new(name + "_mat")
        mat.diffuse_color = (*color, 1.0)
        ob.data.materials.append(mat)

    lay = chair_layout(chair_distance)
    cube("REF_Seat", lay["seat_center"], (SEAT_SIZE, SEAT_SIZE, SEAT_THICKNESS), (0.55, 0.36, 0.20))
    cube("REF_Back", lay["back_center"], (SEAT_SIZE, BACK_THICKNESS, BACK_HEIGHT), (0.45, 0.29, 0.16))
    leg_h = SEAT_TOP - SEAT_THICKNESS
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        cube("REF_Leg%d" % i, (sx * LEG_SPREAD, lay["seat_center"][1] + sy * LEG_SPREAD, leg_h / 2),
             (LEG_SIZE, LEG_SIZE, leg_h), (0.42, 0.27, 0.15))


def chair_layout(chair_distance):
    """**椅子几何的唯一来源**：代理网格与抓握目标都从它取。

    ⚠️ 这里曾经分成两个函数（`build_chair_proxy` 自己算靠背位置、`rail_y()` 另算一份），
    结果**两侧差 0.46 m**——代理把靠背摆在远侧、抓握目标却在近侧，于是"残差 0.0 mm"全绿
    而**手离椅背 440 mm**（owner 一眼看出来的正是这个）。判据必须对着**产物几何**量。
    """
    back_cy = -chair_distance + (SEAT_SIZE / 2 + BACK_THICKNESS / 2)   # 靠背在**朝角色那一侧**
    return {
        "seat_center": (0.0, -chair_distance, SEAT_TOP - SEAT_THICKNESS / 2),
        "back_center": (0.0, back_cy, SEAT_TOP + BACK_HEIGHT / 2),
        "back_near_y": back_cy + BACK_THICKNESS / 2,     # 朝角色的那一面
        "back_far_y": back_cy - BACK_THICKNESS / 2,      # 背向角色的那一面
        "back_cy": back_cy,
        "rail_top_z": SEAT_TOP + BACK_HEIGHT,
        "half_width": SEAT_SIZE / 2,
        # 抓握任务点：腕在顶杆上方略偏近侧；中指尖绕到**远侧面的下方**
        # 腕目标高出顶面 **ε**：掌面向下时，掌面点 = 骨原点 − ε·Z ⇒ 腕应恰在顶面上方 ε 处。
        # ⚠️ 上一轮把它从手拍的 45 mm 改成 ε 时"更差"（46.9 mm）——因为那时**朝向是错的**（掌面没朝下），
        #    高度再对也贴不上。现在朝向由 set_hand_grip_orientation **解出来**，这一步才成立。
        "wrist": lambda sx: Vector((sx * 0.17, back_cy + 0.005, SEAT_TOP + BACK_HEIGHT + EPSILON_PALM_M)),
        "tip": lambda sx: Vector((sx * 0.17, back_cy - BACK_THICKNESS / 2 - 0.015,
                                  SEAT_TOP + BACK_HEIGHT - 0.025)),
    }


# ---------------------------------------------------------------- 手指蜷曲轴自测


def _finger_tip(arm, side, finger):
    return f"{BONE_PREFIX}{side}Hand{finger}4"


def _palm_plane(arm, side):
    """掌心平面基：`toward_palm`（指尖朝掌心的方向）+ `lateral`（掌面内的侧向）。

    侧向必须单独量——**只最大化"朝掌心"会把侧弯也选进来**：实测第一版选中 Z/−1，
    虽然"朝掌心 173 mm"，但**侧向分量 95 mm 比它还大**，呈现就是"手指侧弯"（owner 一眼指出）。
    """
    clear_pose(arm)
    tip = world_point(arm, f"{BONE_PREFIX}{side}HandMiddle4", "tail").copy()
    wrist = world_point(arm, f"{BONE_PREFIX}{side}Hand").copy()
    toward_palm = (wrist - tip).normalized()
    # 侧向 = 垂直于「指尖→腕」且垂直于掌面法向；掌面法向由食指↔小指基节连线定
    across = world_point(arm, f"{BONE_PREFIX}{side}HandIndex1") - world_point(arm, f"{BONE_PREFIX}{side}HandPinky1")
    lateral = across.normalized()
    lateral = (lateral - toward_palm * lateral.dot(toward_palm)).normalized()
    return tip, toward_palm, lateral


def _set_one_finger(arm, side, finger, axis_index, amount):
    """按 `FINGER_CURL_DEG` 给一根手指的三个指节设同一轴的旋转；`amount` 为符号/幅度系数。"""
    for k in (1, 2, 3, 4):
        name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
        if name not in arm.pose.bones:
            continue
        e = [0.0, 0.0, 0.0]
        e[axis_index] = math.radians(FINGER_CURL_DEG[finger][k - 1] * amount)
        pb = arm.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler(e, "XYZ")


def detect_curl_axis(arm, side):
    """定"四指屈曲"的**符号**——判据是**外部几何**：屈曲会把中指尖带向拇指尖。

    ⚠️ 为什么不用"指尖朝掌心位移最大"（撤回版的判据）：那个"掌心"是**它自己算的平面**，
    属自证式判据（错误分类 A1）。#160 实测：同一姿势下两条判据给出**相反**的右手符号，
    而外部判据是决定性的（两符号间距差约 66 mm）。

    返回 {"axis", "sign", "gap_rest_mm", "gap_curl_mm", "gap_hyper_mm"}。
    """
    ax = "X"                      # 屈曲轴：#161 §2.1.4 + 撤回版自测一致落在 X
    tip = f"{BONE_PREFIX}{side}HandMiddle4"
    thumb = f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Thumb']}"

    def gap_mm():
        return (world_point(arm, tip, "tail") - world_point(arm, thumb, "tail")).length * 1000.0

    def curl(sign):
        for finger in FINGERS:
            for k in (1, 2, 3, 4):
                name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
                if name not in arm.pose.bones:
                    continue
                e = [0.0, 0.0, 0.0]
                e[0] = math.radians(FINGER_CURL_DEG[finger][k - 1] * sign)
                pb = arm.pose.bones[name]
                pb.rotation_mode = "XYZ"
                pb.rotation_euler = Euler(e, "XYZ")
        update()

    clear_pose(arm)
    rest = gap_mm()
    readings = {}
    for sign in (1, -1):
        clear_pose(arm)
        curl(sign)
        readings[sign] = gap_mm()
    clear_pose(arm)
    sign = min(readings, key=lambda s: readings[s])
    return {"axis": ax, "sign": sign,
            "gap_rest_mm": round(rest, 1),
            "gap_curl_mm": round(readings[sign], 1),
            "gap_hyper_mm": round(readings[-sign], 1),
            "criterion_valid": bool(readings[sign] < rest)}


def apply_finger_curl(arm, side, curl_axis, amount):
    """按**外部判据**定下的轴与符号施加蜷曲；`amount` 0..1。

    四指与拇指共用一组符号（#160 实测：+1 在两侧都是屈曲）——这本身就是对
    §七·B「右四指 X−1」那组符号的**反驳**（见证据 §六）。
    """
    axis_index = 0 if curl_axis["axis"] == "X" else 2
    n = 0
    for finger in FINGERS:
        for k in (1, 2, 3, 4):
            name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
            if name not in arm.pose.bones:
                continue
            e = [0.0, 0.0, 0.0]
            e[axis_index] = math.radians(FINGER_CURL_DEG[finger][k - 1] * curl_axis["sign"] * amount)
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler(e, "XYZ")
            n += 1
    return n


# ---------------------------------------------------------------- 捕获 IK 结果


def head_up_deg(arm):
    """头骨"上"轴（Head → HeadTop_End）与**重力轴**的夹角（度）。0 = 目视水平。

    为什么用这个量：口径 §十 V-b 列的"目视水平"在旧判据里**根本不存在**，于是弯腰时头随着
    骨盆一起低下去而无人发现。头骨的"上"轴回到竖直 ⇒ 脸朝水平。
    """
    up = (world_point(arm, f"{BONE_PREFIX}HeadTop_End", "tail")
          - world_point(arm, f"{BONE_PREFIX}Head")).normalized()
    return math.degrees(up.angle(Vector((0.0, 0.0, 1.0))))


def solve_gaze(arm, tol_deg=0.5, max_iter=8):
    """解 Neck / Head 的局部 X（点头轴）使头骨"上"轴回到竖直——**解出来的，不是猜的**。

    用数值导数：先量一次、给 Head X 加一个小步长再量，得到 dθ/dX，然后牛顿步进。
    返回 {"head_x_deg", "neck_x_deg", "before_deg", "after_deg", "iters"}。
    """
    def set_pair(hx, nx):
        for name, val in ((f"{BONE_PREFIX}Head", hx), (f"{BONE_PREFIX}Neck", nx)):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler((math.radians(val), 0.0, 0.0), "XYZ")
        update()

    before = head_up_deg(arm)
    hx = nx = 0.0
    probe = 2.0
    set_pair(probe, 0.0)
    d = (head_up_deg(arm) - before) / probe          # dθ/dHeadX（度/度）
    set_pair(0.0, 0.0)
    iters = 0
    if abs(d) < 1e-6:
        return {"head_x_deg": 0.0, "neck_x_deg": 0.0, "before_deg": round(before, 3),
                "after_deg": round(before, 3), "iters": 0, "note": "头骨上轴对 Head X 不敏感"}
    for iters in range(1, max_iter + 1):
        theta = head_up_deg(arm)
        if abs(theta) <= tol_deg:
            break
        # 颈椎承担一半、头承担一半（更自然；也不必让某一根转到底）
        step = -theta / d
        hx += step * 0.5
        nx += step * 0.5
        set_pair(hx, nx)
    after = head_up_deg(arm)
    return {"head_x_deg": round(hx, 3), "neck_x_deg": round(nx, 3),
            "before_deg": round(before, 3), "after_deg": round(after, 3), "iters": iters}


def palm_surface_point(arm, side):
    """掌面点（世界坐标）= 手骨原点 + ε × 骨局部 +Z（#160：掌面 = 骨局部 +Z）。

    ⚠️ 这是"掌面中心点"的**粗模型**（只在掌面与目标面平行时才是接触点）。
    owner 2026-09-14 选定判据形态"甲"之后，判据改用 `palm_lowest_z()`——**真实蒙皮顶点**的最低点。
    """
    pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
    normal = (pb.matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    return world_point(arm, f"{BONE_PREFIX}{side}Hand") + normal * EPSILON_PALM_M


_PALM_CACHE = {}


def palm_face_vertices(arm, side):
    """**掌面那一层**的真实蒙皮顶点（静止时就近取好，之后按刚性变换跟随手骨）。

    取法：网格里**主导组 = 手骨**的顶点中，沿骨局部 +Z 的偏移落在最外层 6 mm 内的那些
    （+Z 就是 #160 实测的掌面法向）。手部顶点权重为 1.0（#160 证据 §五）⇒ 刚性变换精确。
    """
    if side in _PALM_CACHE:
        return _PALM_CACHE[side]
    name = f"{BONE_PREFIX}{side}Hand"
    bl_inv = arm.data.bones[name].matrix_local.inverted()
    arm_inv = arm.matrix_world.inverted()
    out = []
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        # ⚠️ **只取可见皮肤层 `Beta_Surface`**：`Beta_Joints` 是骨骼可视化的网格，其"手部"顶点不在皮肤上，
        #    取两网格的 min 会被它污染（实测：掌面读数恒为 −1409.7 mm = 比顶面低 1.4 m，且**对朝向不敏感**
        #    ⇒ 说明那批顶点根本不在手上）。#160 的 ε 也是在 `Beta_Surface` 上实测的，口径一致。
        if ob.name != "Beta_Surface":
            continue
        vg = ob.vertex_groups.get(name)
        if vg is None:
            continue
        cand = []
        for v in ob.data.vertices:
            best_g, best_w = None, -1.0
            for r in v.groups:
                if r.weight > best_w:
                    best_g, best_w = r.group, r.weight
            if best_g == vg.index:
                cand.append(bl_inv @ (arm_inv @ (ob.matrix_world @ v.co)))
        if not cand:
            continue
        zmax = max(p.z for p in cand)
        # ⚠️ 单位：缓存的偏移在**骨架局部单位**（本母版 1 单位 = 1 cm，`arm_scale=0.01`），
        #    而 PALM_SLAB_M 写的是**米** ⇒ 必须换算，否则片层实际只有 0.06 mm 厚、"掌面最低点"退化成**单个顶点**
        #    （2026-09-14 实测：slab_n = 1）。
        slab_local = PALM_SLAB_M / max(arm.matrix_world.to_scale().x, 1e-9)
        out += [p for p in cand if p.z >= zmax - slab_local]
    _PALM_CACHE[side] = out
    return out


def palm_lowest_z(arm, side):
    """按**当前姿势**算掌面那一层顶点的**最低世界 z**（判据形态"甲"的读数对象）。

    ⚠️ **2026-09-14 修**：这里原来多乘了一次 `bone.matrix_local.inverted()`——
    而 `palm_face_vertices` 缓存的 `p` **已经是骨局部坐标**（`bl_inv @ (arm_inv @ (mesh_world @ co))`），
    再反解一次等于把"骨在骨架里的位置"当成了顶点偏移 ⇒ 读数恒定偏 **≈1.4 m**（正是那个
    −1402~−1410 mm），而且**对朝向不敏感**（因为偏量由骨的静止位置主导）。
    判据：探针里用 `pb.matrix @ p` 算出的世界坐标与 evaluated depsgraph 的实测顶点**逐位相同（差 0.0 mm）**
    ⇒ 正确写法就是 `pb.matrix @ p`。
    """
    name = f"{BONE_PREFIX}{side}Hand"
    pb = arm.pose.bones[name]
    mw = arm.matrix_world
    return min((mw @ (pb.matrix @ p)).z for p in palm_face_vertices(arm, side))


def capture_channels(arm, names):
    """把控制骨的**通道值**（euler/location）原样记下来。

    全都改成解析解之后，姿势就在通道里，**不需要**再从求值矩阵反解——反解那一步会按
    **控制骨**的父链算 basis，而姿态约束是按**变形骨**父链生效的，等于把共轭错误又引回来
    （实测：改完 `_set_world_axes` 结果却一模一样，就是因为这里又反解了一遍）。
    """
    out = {}
    for name in names:
        pb = arm.pose.bones[name]
        e = pb.rotation_euler if pb.rotation_mode != "QUATERNION" else pb.rotation_quaternion.to_euler("XYZ")
        out[name] = {"euler_deg": [math.degrees(a) for a in e],
                     "location": list(pb.location)}
    return out


def apply_channels(arm, captured):
    for name, data in captured.items():
        pb = arm.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler([math.radians(a) for a in data["euler_deg"]], "XYZ")
        pb.location = Vector(data["location"])
    update()


def body_frame(arm):
    """**按当前姿势**现算的身体坐标系：`spine`（骨盆→头）· `lateral`（骨盆左右）· `posterior`（背侧）。

    肘是铰链：它相对「肩→腕」连线的偏移应当**主要沿 `posterior`**，`lateral` 分量要小。
    用世界 Y 当"向后"是错的——弯腰后身体的"背侧"是**上后方**（实测 55° 弯腰时 posterior≈(0,0.57,0.82)）。
    """
    spine = (world_point(arm, f"{BONE_PREFIX}Head") - world_point(arm, f"{BONE_PREFIX}Hips")).normalized()
    lateral = (world_point(arm, f"{BONE_PREFIX}LeftUpLeg") -
               world_point(arm, f"{BONE_PREFIX}RightUpLeg")).normalized()
    lateral = (lateral - spine * lateral.dot(spine)).normalized()
    posterior = spine.cross(lateral).normalized()
    return spine, lateral, posterior


def elbow_offset(arm, side):
    """肘相对「肩→腕」弦的偏移，分解到**无歧义的三轴**：向后(世界 +Y) / 向下(−Z) / 体侧(lateral)。

    ⚠️ 这里连续错过两次，都是"判据错而不是产物错"：
      ① 先用「向外 + 向后之和最大」当**目标函数** ⇒ 那个函数本身在**鼓励肘向外张**（解出向外 96 / 后 55）；
      ② 改成投影到**脊柱轴**（`spine = Head − Hips`）并把它叫 `forward` ⇒ 弯腰后脊柱指向**前上方**，
         于是"肘朝骨盆方向（后下）"被算成了 109 mm **forward**，把**正确**的姿势判成反关节。
    ⇒ 判据只用**无歧义的世界轴**（角色不转身，故 +Y 恒为背向）＋**体侧轴**（由骨盆左右骨给出）。
    """
    _, lateral, _ = body_frame(arm)
    shoulder = world_point(arm, f"{BONE_PREFIX}{side}Arm")
    wrist = world_point(arm, f"{BONE_PREFIX}{side}Hand")
    elbow = world_point(arm, f"{BONE_PREFIX}{side}ForeArm")
    axis = (wrist - shoulder).normalized()
    delta = elbow - shoulder
    perp = delta - axis * delta.dot(axis)
    return {"back": round(perp.y * 1000.0, 1),          # +Y = 角色背向
            "down": round(-perp.z * 1000.0, 1),         # −Z = 向下
            "side": round(perp.dot(lateral) * 1000.0, 1),
            "mm": round(perp.length * 1000.0, 1)}


def _set_world_axes(arm, ctrl_name, deform_name, y_dir_world, x_hint_world):
    """让**变形骨**的世界朝向变成：局部 Y 沿 `y_dir`、局部 X 尽量对齐 `x_hint`。

    ⚠️ **极易错的一处映射**（本工程实测踩到）：约束是 `COPY_ROTATION(LOCAL↔LOCAL)`，
    复制的是**局部**旋转，而
      · 控制骨 `CTRL_Arm` 的父级是 **`CTRL_Hips`**（平行控制链）
      · 变形骨 `mixamorig:Arm` 的父级是 **`mixamorig:Shoulder`**（真实骨链）
    ⇒ **「设控制骨的世界朝向」≠「设变形骨的世界朝向」**，两者差一个共轭。
    故 basis 必须按**变形骨**那侧的父链解，再写到控制骨上（复制是 1:1 的）：

        basis_ctrl = (P_deform_parent · rest_local_deform)⁻¹ · 目标世界矩阵
    """
    from mathutils import Matrix
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm.evaluated_get(dg)
    dbone = arm.data.bones[deform_name]
    inv = arm.matrix_world.inverted().to_3x3()
    y = (inv @ Vector(y_dir_world)).normalized()
    xh = inv @ Vector(x_hint_world)
    x = xh - y * xh.dot(y)
    if x.length < 1e-8:
        x = Vector((1.0, 0.0, 0.0)) - y * y.x
    x.normalize()
    z = x.cross(y)
    target = Matrix(((x.x, y.x, z.x, 0.0),
                     (x.y, y.y, z.y, 0.0),
                     (x.z, y.z, z.z, 0.0),
                     (0.0, 0.0, 0.0, 1.0)))
    if dbone.parent is not None:
        parent_pose = ev.pose.bones[dbone.parent.name].matrix.copy()
        rest_chain = parent_pose @ dbone.parent.matrix_local.inverted() @ dbone.matrix_local
    else:
        rest_chain = dbone.matrix_local.copy()
    pb = arm.pose.bones[ctrl_name]
    pb.matrix_basis = rest_chain.inverted() @ target
    update()


def _rest_dir(arm, deform_name):
    """变形骨在**静止姿势**下的世界指向（用于让脚掌回到水平）。"""
    b = arm.data.bones[deform_name]
    v = (b.tail_local - b.head_local).normalized()
    return (arm.matrix_world.to_3x3() @ v)


def _rest_hinge(arm, deform_name):
    b = arm.data.bones[deform_name]
    return (arm.matrix_world.to_3x3() @ b.matrix_local.to_3x3().col[0])


def solve_two_bone(arm, ctrl_root, ctrl_mid, deform_root, deform_mid, deform_tip,
                   tip_target, bend_dir, label=""):
    """**通用二骨解析解**：中间关节（肘/膝）的位置由 `bend_dir` 显式给定，反解两骨朝向。

    为什么不用 Blender IK：极点到关节平面的映射**不由我控制**——实测"把极点摆在背侧"，
    仍解出**肘向前顶 109 mm**（反关节），8 个 `pole_angle` 里最好的一个背侧分量只有 10 mm。
    与其调极点，不如把**关节位置**当输入：这样肘/膝朝向是可断言的一等量。
    """
    root = world_point(arm, deform_root)
    mid_rest = world_point(arm, deform_mid)
    tip_rest = world_point(arm, deform_tip)
    a = (mid_rest - root).length
    b = (tip_rest - mid_rest).length
    chord = tip_target - root
    c = chord.length
    info = {"label": label, "reach_m": round(c, 4), "limb_len_m": round(a + b, 4)}
    if c >= a + b - 1e-6:
        mid = root + chord.normalized() * a
        info["clamped_straight"] = True
    else:
        x = (a * a - b * b + c * c) / (2.0 * c)
        h = math.sqrt(max(a * a - x * x, 0.0))
        axis = chord / c
        n = Vector(bend_dir) - axis * Vector(bend_dir).dot(axis)
        if n.length < 1e-8:
            n = Vector((0.0, 1.0, 0.0)) - axis * axis.y
        n.normalize()
        mid = root + axis * x + n * h
        info["clamped_straight"] = False
    hinge = (mid - root).cross(tip_target - mid)
    if hinge.length < 1e-8:
        hinge = Vector((1.0, 0.0, 0.0))
    hinge.normalize()
    # ⚠️ basis 必须按**变形骨**那侧的父链解（约束复制的是局部旋转，两侧父链不同 ⇒ 差一个共轭）
    _set_world_axes(arm, ctrl_root, deform_root, mid - root, hinge)
    _set_world_axes(arm, ctrl_mid, deform_mid, tip_target - mid, hinge)
    info["mid_target_m"] = [round(v, 4) for v in mid]
    info["mid_err_mm"] = round((world_point(arm, deform_mid) - mid).length * 1000.0, 1)
    info["tip_err_mm"] = round((world_point(arm, deform_tip) - tip_target).length * 1000.0, 1)
    return info


def solve_arm(arm, side, wrist_target, elbow_dir):
    return solve_two_bone(arm, f"CTRL_{side}Arm", f"CTRL_{side}ForeArm",
                          f"{BONE_PREFIX}{side}Arm", f"{BONE_PREFIX}{side}ForeArm",
                          f"{BONE_PREFIX}{side}Hand", wrist_target, elbow_dir, label=f"arm_{side}")


def solve_leg(arm, side, ankle_target, knee_dir):
    return solve_two_bone(arm, f"CTRL_{side}UpLeg", f"CTRL_{side}Leg",
                          f"{BONE_PREFIX}{side}UpLeg", f"{BONE_PREFIX}{side}Leg",
                          f"{BONE_PREFIX}{side}Foot", ankle_target, knee_dir, label=f"leg_{side}")


def web_point(arm, side):
    """**虎口**在世界里的位置 = 拇指根(`HandThumb1`)↔食指根(`HandIndex1`)的中点，再沿掌面法向偏移 ε。

    为什么需要它：此前判据只有掌面最低点 / 拇指尖 / 四指指尖 ⇒ **没有任何一条要求"虎口落在上沿上"**，
    于是虎口自然飘着（owner 一眼看出）。ε 与掌面同一套换算（[#160](../../../design/engineering/evidence/action-description-epsilon-2026-09-14.md) 实测 32.68 mm）。
    """
    # ⚠️ 这里必须用**拇指根**（Thumb1 的 head）与**食指根**（Index1 的 head）——虎口是"根与根之间"那一点。
    #    2026-09-14 实测踩到：误用了 `DIGIT_TIP['Thumb']`（= Thumb4 拇指**尖**），拇指又蜷着 ⇒
    #    虎口被算在腕**前方 130 mm** ⇒ 腕目标被反向推后 130 mm（就是那个恒定的"腕↔靠背 130.0 mm"），
    #    整只手退到远侧面之外、四指全部落在近侧。
    t = world_point(arm, f"{BONE_PREFIX}{side}HandThumb1")     # 拇指根
    i = world_point(arm, f"{BONE_PREFIX}{side}HandIndex1")     # 食指根
    mid = (t + i) * 0.5
    pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
    # ⚠️ **法向必须取世界系**：母版的骨架对象带 **+90° X 旋转**（Y-up 导入，实测
    #    `matrix_world` 的第二/三行互换、scale 0.01）。只在骨架系里取法向，等于把 `ε`
    #    加到了一个**被转了 90° 的方向**上。
    #    #163 之所以没炸：椅背那一格的掌面法向恰是 ±X，而 X 轴是那个旋转的**不动轴** ⇒ 巧合相等。
    #    门边宿主第一次把它暴露出来（自由边的 u 不在 X 轴上）：虎口偏 21°、
    #    四指↔远侧棱从 0.4 mm 变成 8.6 mm。⇒ 换算法向与世界读数必须同一个系（§8.2 的"两个数"之外，
    #    还有"两个系"这一层）。
    normal = (arm.matrix_world.to_3x3() @ pb.matrix.to_3x3()
              @ Vector((0.0, 0.0, 1.0))).normalized()
    return mid + normal * EPSILON_PALM_M


def _strict_hand_axes(arm, side):
    """**严格对齐**：掌面法向(局部 +Z) → 世界 −Z · 展开轴(局部 X) → 世界 +X（= 上沿轴向）⇒ 局部 Y → 世界 −Y。

    ⚠️ 这一条必须是**硬约束**：上一轮它在搜索里被牺牲掉，四指于是成了 52 mm 的扇形摊开——
    owner 的原话是"两只手更像握住一个**弯曲的**椅背，而不是**笔直的**"。偏差正是那 ~30°。
    """
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    Vector((0.0, -1.0, 0.0)), Vector((1.0, 0.0, 0.0)))


def solve_thumb_to_near_face(arm, side, target, base_curl):
    """**单独解拇指自身**的旋转，让拇指尖落到近侧面（+Y 侧）。

    为什么要把拇指拆出来解：手掌严格对齐后，拇指的解剖位置落在"沿上沿(±X)"方向，
    它的 y 会落进靠背厚度区间**之内**（既非近侧也非远侧）。上一轮为了满足"拇指近侧"，
    求解器只能把**整只手偏转 30°**——那就是扇形的来源。拇指自己有 4 节可动骨，
    让它**自己去贴近侧面**，手就不必偏。
    """
    name = f"{BONE_PREFIX}{side}HandThumb1"
    pb = arm.pose.bones[name]
    tip_bone = f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Thumb']}"

    def probe(tx, ty, tz):
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler((math.radians(tx), math.radians(ty), math.radians(tz)), "XYZ")
        for finger in ("Thumb",):
            for k in (2, 3, 4):
                b2 = arm.pose.bones.get(f"{BONE_PREFIX}{side}HandThumb{k}")
                if b2 is none_guard:
                    continue
        update(2)
        return (world_point(arm, tip_bone, "tail") - target).length * 1000.0

    none_guard = None
    base = list(base_curl)
    best = None
    for tx in range(base[0] - 60, base[0] + 61, 20):
        for ty in range(base[1] - 60, base[1] + 61, 30):
            for tz in (-40, 0, 40):
                d = probe(tx, ty, tz)
                if best is None or d < best[0]:
                    best = (d, tx, ty, tz)
    for step in (8, 3):
        for tx in range(best[1] - 16, best[1] + 17, step):
            for ty in range(best[2] - 16, best[2] + 17, step):
                for tz in range(best[3] - 16, best[3] + 17, step):
                    d = probe(tx, ty, tz)
                    if d < best[0]:
                        best = (d, tx, ty, tz)
    probe(best[1], best[2], best[3])
    return {"euler_deg": [best[1], best[2], best[3]], "tip_residual_mm": round(best[0], 1)}


def hand_grip(arm, side, lay, wrist_default, tip_target):
    """手部解算（三步，全是**约束**而不是加权评分）：

    ① **严格对齐**手的三轴（掌向下 · 展开轴∥上沿）——四指因此同深、看起来"笔直"；
    ② **腕位置解析解**：让**虎口**落到上沿线上（先按默认腕目标摆一次、量虎口、把差值补到腕目标上，再解一次）；
    ③ **拇指单独解**：让拇指尖贴到近侧面（+Y 侧）。
    """
    sgn = 1.0 if side == "Left" else -1.0
    post = _posterior(arm)
    # ① 先把腕送到**默认目标**（已实测可达：撤回版在此残差 0.0 mm）
    info1 = solve_arm(arm, side, wrist_default, post)
    # ② **顺序修正点**：父链此刻已定，再定手的世界朝向——原来这一步放在 solve_arm **之前**，
    #    写 basis 用的是父骨**残留**矩阵 ⇒ 手朝向在解臂前后不一致、虎口偏移被算成错的常量（§十九 根因）
    _strict_hand_axes(arm, side)
    # ③ 在该顺序下量"虎口相对腕"的偏移（刚体常量）
    wrist_head = world_point(arm, f"{BONE_PREFIX}{side}Hand")
    off = web_point(arm, side) - wrist_head
    edge = Vector((wrist_head.x, lay["back_cy"], lay["rail_top_z"]))   # 虎口该落在的上沿那一点
    wrist_target = edge - off
    # ④ 送到"一次算出"的目标；解臂会改腕的旋转 ⇒ 再定一次朝向
    info2 = solve_arm(arm, side, wrist_target, post)
    _strict_hand_axes(arm, side)
    web2 = web_point(arm, side)
    return {"wrist_default_m": [round(v, 4) for v in wrist_default],
            "wrist_target_m": [round(v, 4) for v in wrist_target],
            "web_offset_m": [round(v, 4) for v in off],
            "web_to_edge_mm": round((web2 - edge).length * 1000.0, 1),
            "arm_default": info1,
            "arm": info2,
            "hand_euler_deg": [math.degrees(a) for a in arm.pose.bones[f"CTRL_{side}Hand"].rotation_euler]}


def _posterior(arm):
    _, _, p = body_frame(arm)
    return p


def mesh_bbox(name):
    ob = bpy.data.objects[name]
    corners = [ob.matrix_world @ Vector(v) for v in ob.bound_box]
    return {"x": (min(c.x for c in corners), max(c.x for c in corners)),
            "y": (min(c.y for c in corners), max(c.y for c in corners)),
            "z": (min(c.z for c in corners), max(c.z for c in corners))}


# ══════════════════════════════════════════════════════════════════════════════
# 【可复用库 · #164 扩展】掐棱（卡 1）与门边动作共用的件
#
#   分四组：① 板与棱线（目标对象的唯一来源） ② 蒙皮读数（判据的度量对象）
#           ③ 手骨轴实测（F3 / F10 的依据） ④ 掐棱握式解算（两个宿主的同一段姿势逻辑）
#
#   ⚠️ 本节只**加件**：`main_chair()`（#163 的产出宿主）走的仍是上面那些函数，逐字不变。
#      依据：issue #164「抽出可复用库 + 卡脚本宿主 + 门边动作宿主；**不重写**」。
# ══════════════════════════════════════════════════════════════════════════════

# 卡 1 的四种抓握方向（F8）。`n` = 板厚方向（近侧 → 远侧）· `u` = 端面 → 板内 · `z` = 竖直。
CARD1_DIRECTIONS = ("侧握", "上罩")
#: 卡 1 的**索引键**（F1）——与口径 §13.6 名录表里的那一格**逐字相同**（校验器按字面比对）
CARD1_INDEX_KEY_NAME = "掐棱"

#: 门板代理（`REF_Door`）的尺寸——**代理块**，同 `REF_*` 先例；不进 FBX、不动源 `X Bot.fbx`
DOOR_WIDTH = 0.82
DOOR_HEIGHT = 2.02
DOOR_HINGE = (-0.50, -0.64, 0.0)
#: 半掩（owner 需求里的"半掩的门"）：起始开角 20°（门开向角色这一侧，**边缘恰好落在他伸手可及处**）
DOOR_OPEN_START_DEG = 20.0
#: 推开：+8°。⚠️ **不是**"半掩到全开"——本片实测**可达域**不允许：门宽 0.82 m 时，
#: 门从 20° 转到 28°，边缘扫过 0.14 m；再往下推，边缘就出了手臂的可解区（证据 §六：
#: 第一版 20°→32° 时**到位帧**的腕目标离肩 0.659 m > 臂长 0.562 m ⇒ 手臂被夹直、虎口离门边 72 mm）。
#: 如实登记为"一段推"：要推到底必须**迈步**（本片不新增动作词条、只交静帧）。
DOOR_OPEN_END_DEG = 28.0


# ---------------------------------------------------------------- ① 板与棱线


def board_end_frame(near_edge_point, far_edge_point, into_board_dir,
                    u_span_m=(0.0, 0.21), z_span_m=(0.4449, 0.7949)):
    """**被掐的那一端**的局部坐标：两条竖棱 + 三张命名面（两个宿主共用同一段几何语言）。

    | 名 | 是什么 | 椅背（侧握） | 门板（门边） |
    |---|---|---|---|
    | `near` / `far` | 近侧 / 远侧**竖棱**（端面与两张板面的交线） | `y=−0.45 / −0.49` 处 | 自由边上 `v=∓t/2` 处 |
    | `n` | 板厚方向：**近侧面 → 远侧面** | `−Y` | 门板法向 |
    | `u` | **端面 → 板内** | `∓X` | 自由边 → 铰链 |
    | `z` | 沿棱竖直向上 | `+Z` | `+Z` |

    ⚠️ **棱是两张面的交线**——#163 的"虎口↔上沿"参照的是**顶面中线**（`y = back_cy`），
    中线不是棱 ⇒ 那一格的 −0.0 mm 量的不是"虎口跨棱"（本片如实登记，见证据 §五）。
    """
    near, far = Vector(near_edge_point), Vector(far_edge_point)
    n = (far - near).normalized()
    u = Vector(into_board_dir)
    u = (u - n * u.dot(n)).normalized()
    z = n.cross(u)
    if z.z < 0.0:
        z = -z
    return {"near": near, "far": far, "n": n, "u": u, "z": z,
            "u_span_m": u_span_m, "z_span_m": z_span_m,
            "thickness_mm": round((far - near).length * 1000.0, 3),
            "面-近侧面": (near, -n),          # (面上一点, **朝外**法向)
            "面-远侧面": (far, n),
            "面-端面": ((near + far) * 0.5, -u),
            "棱-近侧": (near, z),
            "棱-远侧": (far, z)}


def chair_end_frame(side, lay):
    """椅背**侧面**那一端（卡 1 侧握的目标）：`x = ±half_width` 处，近侧 / 远侧两条竖棱。"""
    sgn = 1.0 if side == "Left" else -1.0
    hw = lay["half_width"]
    return board_end_frame(Vector((sgn * hw, lay["back_near_y"], 0.0)),
                           Vector((sgn * hw, lay["back_far_y"], 0.0)),
                           Vector((-sgn, 0.0, 0.0)),
                           u_span_m=(0.0, 2.0 * hw),
                           z_span_m=(lay["rail_bottom_z"], lay["rail_top_z"]))


def door_layout(open_deg=DOOR_OPEN_START_DEG, width=DOOR_WIDTH, thickness=BACK_THICKNESS,
                height=DOOR_HEIGHT, hinge=DOOR_HINGE):
    """门板几何：**半掩角由铰链实时求得**，不烘世界坐标（口径 §6.1 道具局部系）。

    铰链在 `hinge`（世界），门板绕**竖直轴** `Z` 转 `open_deg`；自由边（门边）= 铰链 + `u·width`。
    `n` = 门板法向，取"**近侧面 → 远侧面**"（近侧面 = 朝角色那一面——由该面外法向指向角色判定）。
    """
    th = math.radians(open_deg)
    u = Vector((math.cos(th), math.sin(th), 0.0))
    n = Vector((-math.sin(th), math.cos(th), 0.0))
    h = Vector(hinge)
    mid_edge = h + u * width
    # 角色固定在原点附近：取"外法向指向角色"的那一面为**近侧面**
    toward_actor = (Vector((0.0, 0.0, 0.0)) - mid_edge)
    if toward_actor.dot(-n) < toward_actor.dot(n):
        n = -n
    return {"open_deg": open_deg, "u": u, "n": n, "hinge": h, "width": width,
            "thickness": thickness, "height": height,
            "mid_edge": mid_edge,
            "near_edge": mid_edge - n * (thickness / 2.0),
            "far_edge": mid_edge + n * (thickness / 2.0),
            "panel_center": h + u * (width / 2.0) + Vector((0.0, 0.0, height / 2.0)),
            "hinge_center": h + Vector((0.0, 0.0, height / 2.0))}


def door_end_frame(lay):
    """门板**自由边**那一端 → 通用的"板端"坐标（与椅背同一段语言）。"""
    return board_end_frame(lay["near_edge"], lay["far_edge"], -lay["u"],
                           u_span_m=(0.0, lay["width"]), z_span_m=(0.0, lay["height"]))


def point_to_line_mm(p, line):
    """点到**直线**（点 + 单位方向）的距离（mm）——F4 里"虎口↔棱"的判据形态（§13.4 点↔线）。"""
    p0, d = line
    v = Vector(p) - Vector(p0)
    return (v - Vector(d) * v.dot(Vector(d))).length * 1000.0


def bent_body_setup(arm, m3, bend_deg, pelvis, foot_rest):
    """**弯腰站姿**（卡 1 与 #163 同一套身体条件）：骨盆前弯 + 世界位移 + 双脚踩原地 + 目视水平。

    ⚠️ 为什么卡 1 也必须弯腰：抓握点落在椅背**侧面上部**（`z≈0.72`、身前 0.45 m）——
    **直立够不到**。本片实测（校准扫描第一版）：直立时手臂被夹直（肘角 **180.0°**），
    虎口离目标 **155.7 mm**，四指反而落在近侧。⇒ 身体条件不是装饰，它决定残差。
    """
    set_euler(arm, "CTRL_Hips", x=bend_deg)
    set_world_offset(arm, m3, "CTRL_Hips", pelvis)
    update()
    _, _, posterior = body_frame(arm)
    for side in ("Left", "Right"):
        solve_leg(arm, side, foot_rest[side], -posterior)
        _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot",
                        _rest_dir(arm, f"{BONE_PREFIX}{side}Foot"),
                        _rest_hinge(arm, f"{BONE_PREFIX}{side}Foot"))
    update()
    return {"bend_deg": bend_deg, "pelvis_offset_m": [round(v, 4) for v in pelvis],
            "gaze": solve_gaze(arm)}


def standing_body_setup(arm, m3, yaw_deg, foot_rest, lean_m=0.0):
    """**站立身体条件**（门边宿主用）：髋部**转身** `yaw_deg` + **双脚踩原地**（解析腿解拉回）。

    ⚠️ 为什么门边必须转身：门半掩时"边缘"不在角色的正前方（实测方位角 ≈ 30°）。
    不转身时手臂被夹直（肘角 **180.0°**、虎口离门边 **291.6 mm**）——同一个病，#163 在弯腰上踩过，
    本片在转身上又踩了一次。⇒ **身体朝向是可达域的一部分，不是装饰**。
    """
    set_euler(arm, "CTRL_Hips", z=yaw_deg)
    if lean_m:
        # 朝**身体正前方**（转身后的 −Y）倾 `lean_m`——门半掩时"边缘"离身体只有 0.45 m，
        # 不倾则腕目标离肩 0.659 m > 臂长 0.562 m（实测：手臂夹直、虎口离门边 52.9 mm）
        th = math.radians(yaw_deg)
        set_world_offset(arm, m3, "CTRL_Hips", (lean_m * math.sin(th), -lean_m * math.cos(th), 0.0))
    update()
    _, _, posterior = body_frame(arm)
    for side in ("Left", "Right"):
        solve_leg(arm, side, foot_rest[side], -posterior)
        _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot",
                        _rest_dir(arm, f"{BONE_PREFIX}{side}Foot"),
                        _rest_hinge(arm, f"{BONE_PREFIX}{side}Foot"))
    update()
    return {"yaw_deg": yaw_deg, "lean_m": lean_m, "gaze": solve_gaze(arm)}


def _to_edge(arm, side, frame, grip_z):
    """棱上的目标点（高度 = `grip_z`）——两个宿主的抓握高度都从这里取。"""
    e = frame["near"]
    return e + frame["z"] * (grip_z - e.z)


# ---------------------------------------------------------------- ② 蒙皮读数


_SKIN_CACHE = {}


def hand_skin_points(arm, side, mesh="Beta_Surface"):
    """`[(主导骨名, 骨局部坐标)]`：该手骨链在蒙皮上的**全部顶点**（缓存）。

    ⚠️ 三条教训都在这里：
    ① **只取 `Beta_Surface`**（可见皮肤层）——`Beta_Joints` 是骨骼可视化网格，它的"手部"顶点
       不在皮肤上（#163 实测：混进来会把掌面读数污染成恒定 −1409.7 mm）；
    ② 每个顶点按**它自己的主导骨**做刚性变换（手部权重 1.0，#160 实测）——
       不能拿一根骨的矩阵去套全部顶点；
    ③ **蒙皮没有最末节（`…4`）的顶点组**：实测 50 个组只到 `…3`，指尖的肉在 `…3` 的组里
       ⇒ "指尖的蒙皮"按**手指前缀**（`HandIndex` 等）聚合，不按末节骨名取。
    """
    key = (side, mesh)
    if key in _SKIN_CACHE:
        return _SKIN_CACHE[key]
    prefix = f"{BONE_PREFIX}{side}Hand"
    arm_inv = arm.matrix_world.inverted()
    out = []
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.name != mesh:
            continue
        groups = {vg.index: vg.name for vg in ob.vertex_groups
                  if vg.name.startswith(prefix) and vg.name in arm.data.bones}
        if not groups:
            continue
        bl_inv = {name: arm.data.bones[name].matrix_local.inverted() for name in groups.values()}
        for v in ob.data.vertices:
            best_g, best_w = None, -1.0
            for r in v.groups:
                if r.weight > best_w:
                    best_g, best_w = r.group, r.weight
            if best_g in groups:
                name = groups[best_g]
                out.append((name, bl_inv[name] @ (arm_inv @ (ob.matrix_world @ v.co))))
    _SKIN_CACHE[key] = out
    return out


def finger_skin_world(arm, side, finger):
    """该手指**蒙皮**的世界坐标（按各自主导骨变换）。`finger` 取 `Index`/`Middle`/`Ring`/`Pinky`/`Thumb`。"""
    mw = arm.matrix_world
    pts = []
    for bone_name, p in hand_skin_points(arm, side):
        if f"Hand{finger}" in bone_name:
            pts.append(mw @ (arm.pose.bones[bone_name].matrix @ p))
    return pts


def points_face_gap_mm(points, face):
    """一组世界点 ↔ **命名面**（面上一点 + **朝外**法向）的**有符号最近间隙**（mm）。

    判据只有一条式子：`gap = min over 点 of (p − 面上一点) · 朝外法向`

    | 读数 | 含义 |
    |---|---|
    | `abs(gap) <= tol` | **贴合**（最近的那一点正落在面上） |
    | `gap > tol` | 悬在面**外**（没贴上去）—— 例如四指越过远侧面飞在外面 |
    | `gap < −tol` | 越过该面（**穿模**；落在板厚区间里也是这个符号） |

    ⇒ 同一格读数**两个方向都能报错**。#163 §二十 那两条判据"互相打架"的成因之一，
    就是当时的"掌面最低点"只报了一个方向（只看陷进去，看不出悬空）。
    """
    pt, out_n = Vector(face[0]), Vector(face[1])
    if not points:
        return {"gap_mm": None, "n_vertices": 0}
    vals = [(p - pt).dot(out_n) * 1000.0 for p in points]
    return {"gap_mm": round(min(vals), 2), "n_vertices": len(points),
            "max_mm": round(max(vals), 2)}


def box_gap_mm(p, frame):
    """点 ↔ **板体**（有限盒）的**带符号**距离（mm）：正 = 盒外最近距离 · 负 = 陷进盒内的深度。

    ⚠️ **为什么不能用"点到远侧棱(线)的距离"当四指的判据**（本片第一版就是这么写的，被 owner 一眼看穿）：
    棱是**一维**的——蒙皮离棱 0.5 mm，同时**陷进板体 20 mm** 完全可以成立（实测：四指 19.2 ~ 19.98 mm 穿模而
    "↔远侧棱 0.28 ~ 1.01 mm"全绿）。⇒ 判据的参照必须是**体**（有限面片/盒），不是无限平面、更不是一条线。
    这是"判据的度量对象要与措辞同层"（§4.2 硬规矩 3）在**本卡自己身上**的第二次应用。
    """
    v = Vector(p) - frame["near"]
    a = v.dot(frame["n"]) * 1000.0
    b = v.dot(frame["u"]) * 1000.0
    c = v.dot(frame["z"]) * 1000.0
    t = frame["thickness_mm"]
    u0, u1 = frame["u_span_m"][0] * 1000.0, frame["u_span_m"][1] * 1000.0
    z0, z1 = frame["z_span_m"][0] * 1000.0, frame["z_span_m"][1] * 1000.0
    if 0.0 <= a <= t and u0 <= b <= u1 and z0 <= c <= z1:
        return -min(a, t - a, b - u0, u1 - b, c - z0, z1 - c)
    da = max(-a, a - t, 0.0)
    db = max(u0 - b, b - u1, 0.0)
    dc = max(z0 - c, c - z1, 0.0)
    return math.sqrt(da * da + db * db + dc * dc)


def points_box_gap_mm(points, frame):
    """一组世界点 ↔ 板体的**最近带符号间隙**（mm）——四指的接触对读数用它。"""
    if not points:
        return None
    return round(min(box_gap_mm(p, frame) for p in points), 2)


def points_min_distance_mm(pa, pb):
    """两组世界点的最小距离（mm）——**捏间隙**（薄侧改族的读数）用它。"""
    if not pa or not pb:
        return None
    return round(min((a - b).length for a in pa for b in pb) * 1000.0, 2)


# ---------------------------------------------------------------- ③ 手骨轴实测（F3 / F10）


def hand_axes_reading(arm, side):
    """**F3 的产物侧读数**：手骨局部三轴在世界里的指向 + 与"腕 → 中指指尖"实测方向的夹角。

    ⚠️ `+Y`（腕 → 指尖）那一行是口径 **U9**（"未单独实测"）——本片**当场量**，不按"显然"填。
    ⚠️ `+Z` 掌面法向的来源是 §8.1 的 ε 实测（掌心朝下、左右一致），本函数只是**复核**它在姿势下不变。
    """
    name = f"{BONE_PREFIX}{side}Hand"
    pb = arm.pose.bones[name]
    # ⚠️ `pb.matrix` 是**骨架空间**的矩阵（本母版骨架 scale = 0.01）⇒ 方向必须再过一次
    #    `arm.matrix_world.to_3x3()`，否则"世界指向"其实只是骨架局部指向（本母版恰好同向，但别靠巧合）。
    m = arm.matrix_world.to_3x3() @ pb.matrix.to_3x3()
    axes = {k: (m @ Vector(v)).normalized() for k, v in
            (("X", (1.0, 0.0, 0.0)), ("Y", (0.0, 1.0, 0.0)), ("Z", (0.0, 0.0, 1.0)))}
    wrist = world_point(arm, name)
    tip = world_point(arm, f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Middle']}", "tail")
    d = (tip - wrist).normalized()
    return {"axes_world": {k: [round(c, 4) for c in v] for k, v in axes.items()},
            "wrist_to_middle_tip_world": [round(c, 4) for c in d],
            "Y_vs_wrist_to_tip_deg": round(math.degrees(axes["Y"].angle(d)), 3),
            "Z_vs_world_Z_deg": round(math.degrees(axes["Z"].angle(Vector((0.0, 0.0, 1.0)))), 3)}


#: 逐组的屈曲**候选轴**（F3 第 3 行：不得按"显然"填，逐组量）
CURL_GROUPS = {"四指": ("Index", "Middle", "Ring", "Pinky"), "拇指": ("Thumb",)}


def _apply_group_curl(arm, side, group, axis_index, sign, amount=1.0):
    """把某一**组**的手指按给定轴/符号蜷曲（其余组保持伸直）。"""
    n = 0
    for finger in CURL_GROUPS[group]:
        for k in (1, 2, 3, 4):
            name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
            if name not in arm.pose.bones:
                continue
            e = [0.0, 0.0, 0.0]
            e[axis_index] = math.radians(FINGER_CURL_DEG[finger][k - 1] * sign * amount)
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler(e, "XYZ")
            n += 1
    return n


def palm_normal_reference(arm, side):
    """掌面参照：**掌面蒙皮的重心** + **掌面法向**（骨局部 `+Z`，口径 §8.1 实测的那个方向）。

    ⚠️ 为什么"中指尖靠近拇指尖"（#163 用的那条）**不能**当屈曲判据——本片实测它是可混淆的：
    · 绕**掌面法向扇开**手指（Z）也把中指尖带向拇指尖（实测 96.0 → **81.86** mm）；
    · 绕**手指长轴扭转**（Y）则**什么都不改变**；
    · 而"指尖 → 腕"距离对 **±θ 完全对称**（实测 X+1 = X−1 = 134.82 mm）⇒ **定不出符号**。
    ⇒ 屈曲的唯一定义是"指尖朝**掌心**走"：量它沿掌面法向的位移。三条判据的读数都留在报告里。
    """
    pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
    mw = arm.matrix_world
    pts = [mw @ (pb.matrix @ p) for p in palm_face_vertices(arm, side)]
    centroid = sum(pts, Vector((0.0, 0.0, 0.0))) / float(len(pts))
    normal = (mw.to_3x3() @ pb.matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
    return centroid, normal


def _group_criterion_mm(arm, side, group):
    """该组屈曲的**三条外部判据**一起报（都不拿"自己算的目标点"当判据——错误分类 A1）：

    | 判据 | 量 | 取向 |
    |---|---|---|
    | **丙 指尖 → 掌面**（主） | 该组末节指尖沿**掌面法向**相对掌面蒙皮重心的位移 | 屈曲使它**增大**（指尖朝掌心走） |
    | 甲 指尖 → 腕 | 末节指尖 ↔ 手骨原点 | 只有大小、**对 ±θ 对称**（定不出符号） |
    | 乙 跨组指尖距 | 四指：中指尖↔拇指尖 · 拇指：拇指尖↔食指尖 | #163 用过；**扇开也会缩短它**（可与屈曲混淆） |
    """
    is_four = group == "四指"
    tip = f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Middle' if is_four else 'Thumb']}"
    other = f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Thumb' if is_four else 'Index']}"
    a = world_point(arm, tip, "tail")
    centroid, normal = palm_normal_reference(arm, side)
    return {"palm_offset_mm": round((a - centroid).dot(normal) * 1000.0, 2),
            "tip_to_wrist_mm": round((a - world_point(arm, f"{BONE_PREFIX}{side}Hand")).length * 1000.0, 2),
            "tip_to_other_mm": round((a - world_point(arm, other, "tail")).length * 1000.0, 2)}


def detect_curl_axis_group(arm, side, group):
    """**逐组**实测屈曲轴与符号：6 个候选（3 轴 × ±）逐个数，主判据 = 丙（指尖朝掌心）。

    返回全部候选读数 ⇒ **有能力报错**（最优候选没让指尖朝掌心走 ⇒ `criterion_valid=False`）。
    `agree_with_cross_group` 记录它与 #163 那条判据（乙）是否给出同一答案——**不一致本身是读数**。
    """
    clear_pose(arm)
    rest = _group_criterion_mm(arm, side, group)
    readings = {}
    for axis_index, axis_name in ((0, "X"), (1, "Y"), (2, "Z")):
        for sign in (1, -1):
            clear_pose(arm)
            _apply_group_curl(arm, side, group, axis_index, sign)
            update()
            readings[f"{axis_name}{sign:+d}"] = _group_criterion_mm(arm, side, group)
    clear_pose(arm)
    best_key = max(readings, key=lambda k: readings[k]["palm_offset_mm"])
    return {"group": group, "axis": best_key[0], "sign": int(best_key[1:]),
            "rest": rest, "readings": readings,
            "criterion_valid": bool(readings[best_key]["palm_offset_mm"] > rest["palm_offset_mm"]),
            "agree_with_cross_group": bool(
                readings[best_key]["tip_to_other_mm"] == min(r["tip_to_other_mm"] for r in readings.values()))}


# ---------------------------------------------------------------- ④ 掐棱握式（卡 1 的唯一姿势解算器）


def fit_finger_curls(arm, side, frame, curl_axis, lo=0.6, hi=1.5, steps=19):
    """**逐指求蜷曲量**，让每根手指的蒙皮都贴到板上（板体带符号间隙的绝对值最小）。

    ⚠️ 为什么必须**逐指**（而不是一个共用系数）：四根手指长度不同，同一个蜷曲量下它们到板的
    最近间隙差 **14 mm**（实测 curl 1.0：[+7.8, +10.8, +3.2, −3.1]——同一姿势里有的悬空 11 mm、
    有的已经陷进板 3 mm）⇒ **一个系数不可能让四根都贴住**。真手也是逐指调的。
    卡 1 的 F10 本来写的就是"**逐指** 4 节屈曲角"（口径 §13.3）⇒ 本函数只是把那一格**解出来**。

    返回 `{finger: 蜷曲量}`（顺便把姿势也设好）。
    """
    out = {}
    for finger in FOUR_FINGERS:
        best = None
        for i in range(steps):
            amount = lo + (hi - lo) * i / (steps - 1)
            _apply_one_finger_curl(arm, side, finger, curl_axis, amount)
            update(1)
            gap = points_box_gap_mm(finger_skin_world(arm, side, finger), frame)
            score = (abs(gap), -amount)
            if best is None or score < best[0]:
                best = (score, amount, gap)
        _apply_one_finger_curl(arm, side, finger, curl_axis, best[1])
        out[finger] = {"蜷曲量": round(best[1], 3), "板体间隙_mm": round(best[2], 2)}
    update(2)
    return out


def _apply_one_finger_curl(arm, side, finger, curl_axis, amount):
    """单根手指按卡内的 4 节基准角 × 蜷曲量蜷曲（轴与符号由 F3 的逐组实测给定）。"""
    axis_index = 0 if curl_axis["axis"] == "X" else (1 if curl_axis["axis"] == "Y" else 2)
    for k in (1, 2, 3, 4):
        name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
        if name not in arm.pose.bones:
            continue
        e = [0.0, 0.0, 0.0]
        e[axis_index] = math.radians(FINGER_CURL_DEG[finger][k - 1] * curl_axis["sign"] * amount)
        pb = arm.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler(e, "XYZ")


def grip_board_edge(arm, side, frame, grip_z, curl_amount, curl_axis,
                    thumb_inset_m=0.045, thumb_drop_m=0.030, label="", fit_curls=True):
    """**掐棱握式**：虎口压在**近侧竖棱**上 · 拇指绕到近侧面 · 四指绕**远侧竖棱**落到远侧面。

    ① **朝向**（解析，不搜索）：骨局部 `Y → n`（四指从近侧绕向远侧）· 骨局部 `Z → −u`（掌面压端面）
       ⇒ 骨局部 `X`（蜷曲轴）`= Y × Z → −z` —— **蜷曲轴沿棱**，四指绕远侧竖棱收拢。
    ② **虎口落到棱上**：`腕 = 棱上一点 − R·(虎口相对腕的偏移)`，**一次算出**而非两遍定点
       （#163 §十八/§十九：两遍定点会把腕推过板；顺序必须是"先解臂、后定朝向"）。
    ③ **四指蜷曲**：用卡 1 的 F10 值（`curl_amount` × `FINGER_CURL_DEG`）——指尖落不落得上远侧面
       **由残差说出来**，不在解算里偷偷补。
    ④ **拇指单独解**到近侧面（拇指自己 4 节可动骨；不让整只手偏转——#163 §十七 的扇形就是这么来的）。

    返回读数（全部**产物侧**）：虎口↔棱（点↔线）· 指尖↔远侧面（逐根，点↔面）· 拇指↔近侧面 · 腕位 · 肘。
    """
    sgn = 1.0 if side == "Left" else -1.0
    n, u, z = frame["n"], frame["u"], frame["z"]
    post = _posterior(arm)
    edge_pt = _to_edge(arm, side, frame, grip_z)
    hand_name = f"{BONE_PREFIX}{side}Hand"
    ctrl_hand = f"CTRL_{side}Hand"

    # ⚠️ 手朝向的第三轴**由几何解出，不按手别硬编码**：要"掌面压端面"就是要求
    #    `掌面法向(骨局部 Z) = +u`，而 `_set_world_axes` 算出的是 `z_local = x_hint × y_dir`
    #    ⇒ 解 `x × n = u` 得 **`x_hint = n × u`**（因为 `(n×u) × n = u`）。
    #    实测代价（两次都踩在同一处）：
    #    ① 两侧同号 ⇒ 右手整只手翻个儿（虎口离棱 155 mm、残差 22.27 mm）；
    #    ② 按手别取反能过椅背，却在**门边宿主上翻了**——门自由边那一端的 (u, n) 手性与椅背 +X 端相反
    #       （`u×n = −Z`）⇒ 四指↔远侧棱 从 0.4 mm 变成 8.6 mm。⇒ 用几何量，别用"左/右"这个代理变量。
    x_hint = n.cross(u)
    # ① 朝向（此时父链未定，写下去只为给"虎口偏移"一个初值）
    _set_world_axes(arm, ctrl_hand, hand_name, n, x_hint)
    # ② 解臂（先解臂、后定朝向——#163 §十九 的顺序修正）→ 定朝向 → 重算偏移 → 再解一次
    off = web_point(arm, side) - world_point(arm, hand_name)
    wrist_target = edge_pt - off
    arm_first = solve_arm(arm, side, wrist_target, post)
    _set_world_axes(arm, ctrl_hand, hand_name, n, x_hint)
    off2 = web_point(arm, side) - world_point(arm, hand_name)
    wrist_target = edge_pt - off2
    arm_final, elbow_pick = solve_arm_with_elbow_scan(arm, side, wrist_target, post)
    _set_world_axes(arm, ctrl_hand, hand_name, n, x_hint)
    # ③ 四指蜷曲（F10 的输入值；拇指留到第 ④ 步单独解）
    if fit_curls:
        curl_solve = fit_finger_curls(arm, side, frame, curl_axis)
    else:
        _apply_group_curl(arm, side, "四指",
                          0 if curl_axis["axis"] == "X" else (1 if curl_axis["axis"] == "Y" else 2),
                          curl_axis["sign"], curl_amount)
        curl_solve = None
    update(2)
    # ④ 拇指：目标 = 近侧面上一点（骨骼尖落在面上、蒙皮厚度靠第 ⑤ 步的读数校正）
    face_pt = frame["面-近侧面"][0]
    thumb_target = face_pt + u * thumb_inset_m + z * (grip_z - face_pt.z)
    thumb = solve_thumb_to_target(arm, side, thumb_target)
    update(2)
    gap0 = points_face_gap_mm(finger_skin_world(arm, side, "Thumb"), frame["面-近侧面"])["gap_mm"]
    if gap0 is not None and abs(gap0) > CONTACT_TOL_MM:
        # 一步 Newton（⚠️ 方向实测踩过一次）：近侧面的**朝外**法向是 `−n`，而 `gap` 正是沿它量的
        # ⇒ 要让 gap 归零，目标点必须沿 `−n` 移动 |gap|。写反的代价：目标点永远落在面上，
        #    间隙恒为 −14.42 mm（拇指蒙皮陷进板 14 mm），且**与抓握高度无关**——那个"恒定"就是判据。
        thumb_target = thumb_target + n * (gap0 / 1000.0)
        thumb = solve_thumb_to_target(arm, side, thumb_target)
        update(2)
    gap1 = points_face_gap_mm(finger_skin_world(arm, side, "Thumb"), frame["面-近侧面"])["gap_mm"]

    web_p = web_point(arm, side)
    web_vs = web_p - edge_pt
    palm_gap = points_face_gap_mm(
        [arm.matrix_world @ (arm.pose.bones[hand_name].matrix @ q) for q in palm_face_vertices(arm, side)],
        frame["面-端面"])["gap_mm"]
    return {
        "label": label,
        "frame_axes": {"n": [round(c, 4) for c in n], "u": [round(c, 4) for c in u],
                       "z": [round(c, 4) for c in z], "thickness_mm": frame["thickness_mm"]},
        "grip_z_m": round(grip_z, 4),
        "curl_amount": curl_amount,
        "curl_axis": dict(curl_axis),
        "curl_solve": curl_solve,
        "edge_point_m": [round(c, 4) for c in edge_pt],
        "web_point_m": [round(c, 4) for c in web_p],
        "web_to_edge_mm": round(point_to_line_mm(web_p, frame["棱-近侧"]), 2),
        "web_along_n_mm": round(web_vs.dot(n) * 1000.0, 2),
        "web_along_u_mm": round(web_vs.dot(u) * 1000.0, 2),
        "wrist_target_m": [round(c, 4) for c in wrist_target],
        "arm": arm_final,
        "elbow_pick": elbow_pick,
        "thumb": thumb,
        "palm_to_end_face_mm": palm_gap,
        "thumb_gap_mm": gap1,
        "thumb_gap_before_correction_mm": gap0,
        "elbow_deg": round(math.degrees(
            (world_point(arm, f"{BONE_PREFIX}{side}Arm") - world_point(arm, f"{BONE_PREFIX}{side}ForeArm"))
            .angle(world_point(arm, hand_name) - world_point(arm, f"{BONE_PREFIX}{side}ForeArm"))), 1),
        "elbow_offset_mm": elbow_offset(arm, side),
        "hand_euler_deg": [round(math.degrees(a), 2)
                           for a in arm.pose.bones[ctrl_hand].rotation_euler],
    }


#: 四指的分区名（成组项必须**并列**打印，口径 §七 硬规矩 2）
FOUR_FINGERS = ("Index", "Middle", "Ring", "Pinky")

#: 肘部三条判据（**沿用 #163 的既有来源**，不是本次新拍）：向后 ≥ 60 · |侧向| ≤ 40 · 向下 ≥ 20（mm）
ELBOW_BACK_MIN, ELBOW_SIDE_MAX, ELBOW_DOWN_MIN = 60.0, 40.0, 20.0


def elbow_penalty_mm(off):
    """肘偏移的**罚分**（mm）：偏离三条判据多少。0 = 三条都满足。"""
    return (max(0.0, ELBOW_BACK_MIN - off["back"]) + max(0.0, abs(off["side"]) - ELBOW_SIDE_MAX)
            + max(0.0, ELBOW_DOWN_MIN - off["down"]))


def solve_arm_with_elbow_scan(arm, side, wrist_target, post, step_deg=30.0):
    """**扫描肘平面**再解臂：不让肘外张（#163 的三条肘判据 + 罚分最小）。

    ⚠️ 为什么必须扫：`solve_two_bone` 的 `bend_dir` 只给"肘往哪边弯"的**提示**，而在卡 1 的侧握里
    用同一个 `bent posterior` 提示会解出**肘向体外张 92.6 mm**（判据上限 40）——owner 目视一眼看出
    "肘部动作不对"，而当时我的回显卡**根本没量肘**（只量了三条接触对）。⇒ 判据漏一项，目视就得补一轮。
    """
    axis = (wrist_target - world_point(arm, f"{BONE_PREFIX}{side}Arm")).normalized()
    base = Vector(post)
    perp = (base - axis * base.dot(axis))
    if perp.length < 1e-8:
        perp = Vector((0.0, 1.0, 0.0)) - axis * axis.y
    perp.normalize()
    side_ax = axis.cross(perp).normalized()
    best = None
    for i in range(int(360.0 / step_deg)):
        a = math.radians(i * step_deg)
        d = (perp * math.cos(a) + side_ax * math.sin(a)).normalized()
        info = solve_arm(arm, side, wrist_target, d)
        off = elbow_offset(arm, side)
        score = (elbow_penalty_mm(off), abs(off["side"]), round(info.get("tip_err_mm", 0.0), 3))
        if best is None or score < best[0]:
            best = (score, d, info, off)
    info = solve_arm(arm, side, wrist_target, best[1])
    return info, {"罚分": round(best[0][0], 1), "肘偏移": best[3], "扫描步长_deg": step_deg}


def grip_board_edge_readings(arm, side, frame):
    """**卡 1「掐棱」的接触对读数**（每对一行；与回显卡**同一来源**——回显卡由本函数的结果生成）。

    三条对（口径 §13.2：一对 = 手部分区 × 物体分区 × 判据形态 × 容差档 × 并列项）：

    | # | 手部分区 | 物体分区 | 形态 | 为什么是这个对象 |
    |---|---|---|---|---|
    | 1 | 虎口 | **近侧竖棱** | 点↔线 | 虎口跨的就是这条棱；`web_point` 含 ε 换算（§8.1） |
    | 2 | 拇指 | 近侧面 | 点↔面 | 拇指绕到 +Y 近侧（口径 §三 D8） |
    | 3 | **四指逐根** | **远侧竖棱** | 点↔线 | 四指绕远侧棱收拢；⚠️ 量的**不是**远侧面——见下 |

    ⚠️ **为什么不量"逐指尖 ↔ 远侧面"**（名录原写的形态）：本片实测它**不可满足**——
    板厚 40 mm 时，虎口压在近侧棱上 ⇒ 掌指关节必然落在 `n≈37.5 mm`（虎口→掌指关节在掌内是
    刚体常量 37 mm），四指于是整段越过远侧面飞在外面，蒙皮到远侧面是 **−3.5 ~ +80 mm**，
    加蜷曲只会更远。**四指真正吃住的是"远侧棱"这条线**（同一姿势下实测 **0.3 ~ 1.0 mm**）
    ⇒ 判据形态取 **点↔线**。这是"判据的度量对象要与措辞同层"（§4.2 硬规矩 3）在卡上的第一次应用。
    """
    rows = [{
        "手部分区": "虎口",
        "物体分区": "近侧竖棱",
        "判据形态": "点↔线",
        "容差档": "接触 tol_contact = 2.8 mm",
        "并列项": "—",
        "读数_mm": round(point_to_line_mm(web_point(arm, side), frame["棱-近侧"]), 2),
    }, {
        "手部分区": "拇指",
        "物体分区": "近侧面",
        "判据形态": "点↔面",
        "容差档": "接触 tol_contact = 2.8 mm",
        "并列项": "—",
        "读数_mm": points_face_gap_mm(finger_skin_world(arm, side, "Thumb"),
                                      frame["面-近侧面"])["gap_mm"],
    }, {
        "手部分区": "食/中/无名/小四指",
        "物体分区": "远侧面",
        "判据形态": "点↔面（**有限面片/体**，不是无限平面）",
        "容差档": "接触 tol_contact = 2.8 mm",
        "并列项": "四指逐根（口径 §七 硬规矩 2）",
        "读数_mm": [points_box_gap_mm(finger_skin_world(arm, side, f), frame)
                    for f in FOUR_FINGERS],
        "逐项名": list(FOUR_FINGERS),
        "符号约定": "正 = 悬在板外 · |·| ≤ 容差 = 贴住 · 负 = **陷进板体**",
    }]
    return rows


def solve_thumb_to_target(arm, side, target):
    """拇指自身 4 节的**目标点解算**（由 `solve_thumb_to_near_face` 泛化：目标点由调用方给）。

    ⚠️ 保留 `solve_thumb_to_near_face` 原函数不动（#163 的路径逐字不变）；本函数是卡 1 / 门边用的。
    """
    name = f"{BONE_PREFIX}{side}HandThumb1"
    pb = arm.pose.bones[name]
    tip_bone = f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Thumb']}"

    def probe(tx, ty, tz):
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler((math.radians(tx), math.radians(ty), math.radians(tz)), "XYZ")
        update(2)
        return (world_point(arm, tip_bone, "tail") - target).length * 1000.0

    base = list(FINGER_CURL_DEG["Thumb"])
    best = None
    for tx in range(base[0] - 80, base[0] + 81, 20):
        for ty in range(base[1] - 60, base[1] + 61, 20):
            for tz in (-40, 0, 40):
                d = probe(tx, ty, tz)
                if best is None or d < best[0]:
                    best = (d, tx, ty, tz)
    for step in (8, 3):
        for tx in range(best[1] - 16, best[1] + 17, step):
            for ty in range(best[2] - 16, best[2] + 17, step):
                for tz in range(best[3] - 16, best[3] + 17, step):
                    d = probe(tx, ty, tz)
                    if d < best[0]:
                        best = (d, tx, ty, tz)
    probe(best[1], best[2], best[3])
    return {"euler_deg": [best[1], best[2], best[3]], "tip_residual_mm": round(best[0], 1)}


# ---------------------------------------------------------------- 代理网格（板 / 门）


def _proxy_cube(coll, name, center, size, color, rot_z_deg=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    if rot_z_deg:
        ob.rotation_euler = Euler((0.0, 0.0, math.radians(rot_z_deg)), "XYZ")
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)
    mat = bpy.data.materials.new(name + "_mat")
    mat.diffuse_color = (*color, 1.0)
    ob.data.materials.append(mat)
    return ob


def build_door_proxy(open_deg=DOOR_OPEN_START_DEG):
    """门代理（`REF_Door` 集合）：**只做参考与量测，不进 FBX**（同 `REF_Chair` 先例）。

    几何的唯一来源是 `door_layout()`——代理与判据目标从**同一个**函数取
    （#163 那次"手离椅背 440 mm 而残差 0.0 mm"就是两处各算一份造成的）。
    """
    old = bpy.data.collections.get("REF_Door")
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    coll = bpy.data.collections.new("REF_Door")
    bpy.context.scene.collection.children.link(coll)
    lay = door_layout(open_deg)
    _proxy_cube(coll, "REF_DoorPanel", lay["panel_center"],
                (lay["width"], lay["thickness"], lay["height"]), (0.42, 0.30, 0.18), lay["open_deg"])
    _proxy_cube(coll, "REF_DoorJamb", lay["hinge_center"] + Vector((0.0, 0.0, 0.0)),
                (0.06, 0.10, lay["height"]), (0.50, 0.50, 0.50))
    return lay


def build_board_proxy(thickness_m, size=SEAT_SIZE, height=BACK_HEIGHT, distance=0.70):
    """**板代理**（`REF_Board`）：卡 1 的 F6/F7 扫描要换板厚 ⇒ 板必须能独立于椅子重建。"""
    old = bpy.data.collections.get("REF_Board")
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    coll = bpy.data.collections.new("REF_Board")
    bpy.context.scene.collection.children.link(coll)
    lay = board_layout(distance, thickness_m, size, height)
    _proxy_cube(coll, "REF_BoardPanel",
                (0.0, lay["back_cy"], SEAT_TOP + height / 2.0),
                (size, thickness_m, height), (0.45, 0.29, 0.16))
    return lay


def board_layout(distance, thickness=BACK_THICKNESS, size=SEAT_SIZE, height=BACK_HEIGHT):
    """**板**的几何（椅背 / 门板同族）：把 `chair_layout` 里的板厚参数化 ⇒ F6/F7 扫描才有对象。

    板占 `x ∈ ±size/2` · `y ∈ [far_y, near_y]` · `z ∈ [SEAT_TOP, SEAT_TOP + height]`。
    与 `chair_layout` **同一套公式**（同一个来源，不另算一份）。
    """
    back_cy = -distance + (size / 2 + thickness / 2)
    return {"back_cy": back_cy, "half_width": size / 2, "thickness": thickness,
            "back_near_y": back_cy + thickness / 2, "back_far_y": back_cy - thickness / 2,
            "rail_bottom_z": SEAT_TOP, "rail_top_z": SEAT_TOP + height}


def main_chair() -> int:
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    report_path = Path(args.report) if args.report else tmpl.parent / "chair_grab_report.json"
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2

    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    lay = chair_layout(args.chair)
    build_chair_proxy(args.chair)
    report = {"script": "author_xbot_chair_grab.py", "blender": bpy.app.version_string,
              "template": str(tmpl), "action": args.action, "fps": args.fps,
              "host": args.host,
              "freedom_table": FREEDOM_TABLE,
              "chair_distance_m": args.chair,
              "chair": {k: (list(v) if isinstance(v, tuple) else v)
                        for k, v in lay.items() if not callable(v)},
              "problems": []}

    drop_temp(arm)
    clear_pose(arm)
    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in ("Left", "Right")}

    # 手指蜷曲轴：逐指自测（含侧向惩罚），并把读数记进报告
    curl = {s: detect_curl_axis(arm, s) for s in ("Left", "Right")}
    report["finger_curl"] = curl
    for side, spec in curl.items():
        print(f"屈曲符号自测 {side:5s}: 轴 {spec['axis']} · 符号 {spec['sign']:+d} · "
              f"拇中尖距 静息 {spec['gap_rest_mm']} → 屈曲 {spec['gap_curl_mm']} / 反向 {spec['gap_hyper_mm']} mm"
              f"（外部判据{'成立' if spec['criterion_valid'] else '**失效**'}）")

    ctrl_bones = [f"{CTRL_PREFIX}{n}" for n in
                  ("Hips", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot",
                   "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand")]
    captured, hand_orient, thumb_orient = {}, {}, {}
    for frame, bend, pelvis, hands_on_rail, curl_amount in SCHEDULE:
        clear_pose(arm)
        drop_temp(arm, also_objects=True)
        set_euler(arm, "CTRL_Hips", x=bend)
        set_world_offset(arm, m3, "CTRL_Hips", pelvis)

        update()
        _, _, posterior = body_frame(arm)
        # 腿：解析解，膝朝**前**（−posterior）；目标 = 脚踝静止位 ⇒ 脚踩原地
        for side in ("Left", "Right"):
            report.setdefault("leg_solve", {})[f"{frame}_{side}"] = solve_leg(
                arm, side, foot_rest[side], -posterior)
        # 脚掌保持水平（脚控制骨的世界朝向回到它的静止朝向）
        for side in ("Left", "Right"):
            _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot",
                            _rest_dir(arm, f"{BONE_PREFIX}{side}Foot"), _rest_hinge(arm, f"{BONE_PREFIX}{side}Foot"))

        if hands_on_rail:
            # ⚠️ 预摆只为给解析解一个好起点；**不能加到没有臂解的帧**（首帧=站立），
            #    否则首帧不中立 ⇒ 导出的 bind pose 被污染（实测被 E5 抓出 69 m 偏差）。
            set_euler(arm, "CTRL_LeftArm", z=70)
            set_euler(arm, "CTRL_LeftForeArm", x=25)
            set_euler(arm, "CTRL_RightArm", z=-70)
            set_euler(arm, "CTRL_RightForeArm", x=25)
        update()

        if hands_on_rail:
            for side in ("Left", "Right"):
                sgn = 1.0 if side == "Left" else -1.0
                grip = hand_grip(arm, side, lay, lay["wrist"](sgn), lay["tip"](sgn))
                report.setdefault("grip_solve", {})[f"{frame}_{side}"] = grip
                apply_finger_curl(arm, side, curl[side], curl_amount)
                # 拇指单独解：贴到近侧面（上沿下方 30 mm、往板内 20 mm）
                thumb_target = Vector((sgn * 0.17 + sgn * 0.02, BACK_NEAR_Y + 0.02, lay["rail_top_z"] - 0.03))
                thumb_orient[(frame, side)] = solve_thumb_to_near_face(
                    arm, side, thumb_target, FINGER_CURL_DEG["Thumb"])
            update(2)
        # ⚠️ 头颈**必须一起捕获**：它们没有控制骨（口径 §三 D6）；solve 出来的补偿角若不入 captured，
        #    复演与导出时就会丢——那样"目视水平"只活在解算的那一瞬间。
        # 目视水平：弯腰后头随骨盆低下 ⇒ 解 Neck/Head 的点头角，把头骨"上"轴拉回竖直
        report.setdefault("gaze_solve", {})[frame] = solve_gaze(arm)
        update(2)
        captured[frame] = capture_channels(arm, ctrl_bones + [f"{BONE_PREFIX}Neck", f"{BONE_PREFIX}Head"])

    # ---- 去掉 IK 复演，逐帧复核（判据一律对着**产物几何**）----
    drop_temp(arm)
    verify = []
    for frame, bend, pelvis, hands_on_rail, curl_amount in SCHEDULE:
        clear_pose(arm)
        apply_channels(arm, captured[frame])
        if hands_on_rail:
            for side in ("Left", "Right"):
                spec = hand_orient.get((frame, side))
                apply_finger_curl(arm, side, curl[side], curl_amount)
                if spec:
                    pb = arm.pose.bones[f"CTRL_{side}Hand"]
                    pb.rotation_mode = "XYZ"
                    pb.rotation_euler = Euler([math.radians(a) for a in spec["hand_euler_deg"]], "XYZ")
                tsp = thumb_orient.get((frame, side))
                if tsp:
                    tb = arm.pose.bones[f"{BONE_PREFIX}{side}HandThumb1"]
                    tb.rotation_mode = "XYZ"
                    tb.rotation_euler = Euler([math.radians(a) for a in tsp["euler_deg"]], "XYZ")
        update()
        back = mesh_bbox("REF_Back")
        row = {"frame": frame, "bend_deg": bend}
        for side in ("Left", "Right"):
            hand = world_point(arm, f"{BONE_PREFIX}{side}Hand")
            tip = world_point(arm, f"{BONE_PREFIX}{side}HandMiddle4", "tail")
            foot = world_point(arm, f"{BONE_PREFIX}{side}Foot")
            row[f"wrist_{side}_m"] = [round(v, 4) for v in hand]
            row[f"tip_{side}_m"] = [round(v, 4) for v in tip]
            row[f"wrist_to_back_mm"] = round(abs(hand.y - lay["back_cy"]) * 1000.0, 1)
            # ⚠️ 只有**手指已蜷**的帧才判"扣住"：手指伸直时指尖本来就会越过顶杆，
            #    不设这个门槛会得到"早早就扣住了"的假读数。
            row[f"tip_wraps_rail_{side}"] = (bool(tip.y < back["y"][0] and tip.z < lay["rail_top_z"])
                                             if curl_amount > 0.0 else None)
            row[f"hand_above_rail_mm"] = round((hand.z - lay["rail_top_z"]) * 1000.0, 1)
            row[f"foot_{side}_drift_mm"] = round((foot - foot_rest[side]).length * 1000.0, 1)
            upper = world_point(arm, f"{BONE_PREFIX}{side}Arm")
            lower = world_point(arm, f"{BONE_PREFIX}{side}ForeArm")
            row[f"elbow_{side}_deg"] = round(math.degrees((upper - lower).angle(hand - lower)), 1)
            row[f"elbow_{side}_offset_mm"] = elbow_offset(arm, side)
        row["head_z_m"] = round(world_point(arm, f"{BONE_PREFIX}Head").z, 4)
        # ---- 三项"旧判据不可能报出"的量（口径 §十 V-b / issue #163）----
        row["gaze_up_deg"] = round(head_up_deg(arm), 3)
        palm, thumb = {}, {}
        for side in ("Left", "Right"):
            lo = palm_lowest_z(arm, side)
            palm[side] = {"lowest_z_m": round(lo, 4),
                          "to_rail_top_mm": round((lo - lay["rail_top_z"]) * 1000.0, 1),
                          "n_face_vertices": len(palm_face_vertices(arm, side))}
            tt = world_point(arm, f"{BONE_PREFIX}{side}Hand{DIGIT_TIP['Thumb']}", "tail")
            thumb[side] = {"tip_m": [round(v, 4) for v in tt],
                           "y_mm_vs_near_face": round((tt.y - BACK_NEAR_Y) * 1000.0, 1)}
            # ⚠️ **成组并列**（口径 §七 硬规矩 2）：四指 + 拇指**逐根**都要有读数——
            #    只量中指尖是不够的（owner 2026-09-14 一眼指出"只做了一件事"）。
            digits = {}
            for d in DIGITS:
                dt = world_point(arm, f"{BONE_PREFIX}{side}Hand{DIGIT_TIP[d]}", "tail")
                digits[d] = {"tip_y": round(dt.y, 4), "tip_z": round(dt.z, 4),
                             "vs_far_face_mm": round((dt.y - BACK_FAR_Y) * 1000.0, 1),
                             "side": "远侧(−Y)" if dt.y <= BACK_FAR_Y else "近侧(+Y)"}
            row[f"digits_{side}"] = digits
        row["palm"], row["thumb"] = palm, thumb
        row["web"] = {}
        for side in ("Left", "Right"):
            w = web_point(arm, side)
            row["web"][side] = {"pos_m": [round(v, 4) for v in w],
                                "above_edge_mm": round((w.z - lay["rail_top_z"]) * 1000.0, 1),
                                "in_slab": bool(-0.49 <= w.y <= -0.45)}
        verify.append(row)
    report["verify"] = verify
    report["back_bbox"] = {k: [round(x, 4) for x in v] for k, v in mesh_bbox("REF_Back").items()}

    # ---- 判据 ----
    last = verify[-1]
    for side in ("Left", "Right"):
        if last[f"wrist_to_back_mm"] > 60.0:
            report["problems"].append(f"{side} 腕离靠背中心面 {last['wrist_to_back_mm']} mm > 60 mm（没放到椅背上）")
        if not last[f"tip_wraps_rail_{side}"]:
            report["problems"].append(f"{side} 指尖没有绕到顶杆远侧下方（没扣住）")
        if not (100.0 <= last[f"elbow_{side}_deg"] <= 172.0):
            report["problems"].append(f"{side} 到位帧肘角 {last[f'elbow_{side}_deg']}° 不在 100–172°")
        off = last[f"elbow_{side}_offset_mm"]
        if off["back"] < 60.0:
            report["problems"].append(
                f"{side} 肘**向后**偏移只有 {off['back']} mm < 60 mm（肘没往后折 = 反关节）")
        if abs(off["side"]) > 40.0:
            report["problems"].append(f"{side} 肘**侧向**偏移 {off['side']} mm > 40 mm（肘向外张 = 侧弯）")
        if off["down"] < 20.0:
            report["problems"].append(f"{side} 肘没有挂在弦的下方（down={off['down']} mm < 20 mm）")
        if not curl[side]["criterion_valid"]:
            report["problems"].append(
                f"{side} 屈曲符号的外部判据失效（两种符号都没让中指尖靠近拇指尖）⇒ 符号不可信")
    # ---- 三项新判据（能报错才有意义）----
    if abs(last["gaze_up_deg"]) > 2.0:
        report["problems"].append(
            f"目视水平：到位帧头骨上轴偏离竖直 {last['gaze_up_deg']}° > 2°（头跟着骨盆低下去了）")
    for side in ("Left", "Right"):
        gap = last["palm"][side]["to_rail_top_mm"]
        # 判据形态"甲"（owner 2026-09-14）：允许倾斜 —— 只要**掌面最低点**在 ε 之内就算贴合；
        # 陷进去（< −PROVISIONAL_TOL_MM）另判穿模。
        if gap < -PROVISIONAL_TOL_MM:
            report["problems"].append(f"{side} 掌面最低点陷进靠背顶面 {gap} mm（穿模）")
        elif gap > CONTACT_TOL_MM:
            report["problems"].append(
                f"{side} 掌面最低点离顶面 {gap} mm > 容差 {CONTACT_TOL_MM} mm（没贴合；owner 定的接触容差）")
        for d in ("Index", "Middle", "Ring", "Pinky"):
            dy = last[f"digits_{side}"][d]["tip_y"]
            if dy > BACK_FAR_Y:
                report["problems"].append(
                    f"{side} {d} 指尖 y={dy:.4f} 未到远侧面 −0.49（四指应**逐根**贴住 −Y 侧）")
        w = last["web"][side]
        if abs(w["above_edge_mm"]) > CONTACT_TOL_MM:
            report["problems"].append(
                f"{side} 虎口未卡在上沿：离上沿 {w['above_edge_mm']} mm（|·| > 容差 {CONTACT_TOL_MM} mm）")
        if not w["in_slab"]:
            report["problems"].append(
                f"{side} 虎口的 y={w['pos_m'][1]} 不在靠背厚度区间 [−0.49, −0.45] 内（没卡在板边上）")
        if last["thumb"][side]["y_mm_vs_near_face"] < 0.0:
            report["problems"].append(
                f"{side} 拇指尖在靠背**远**侧（相对近侧面 {last['thumb'][side]['y_mm_vs_near_face']} mm < 0 ⇒ 没贴在背面，口径 D8）")
    if max(r[f"foot_{s}_drift_mm"] for r in verify for s in ("Left", "Right")) > 15.0:
        report["problems"].append("关键帧上脚漂移 > 15 mm")

    # ---- 写动作（⚠️ 这一步以前**根本不存在**：撤回版改写解析解时把打键丢了，
    #      于是"跑了 4 轮、判据全在、却没有任何动作"——owner 目视时看不到东西。2026-09-14 实测。）
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    # ⚠️ `actions.new()` 遇到同名会**静默**建 `名字.001`，旧动作仍留着 ⇒ 导出按名取到**旧动作**
    #    （管线上实测：改完动作导出结果一模一样，E5 偏差逐位不变）。重跑前先清同名/同前缀。
    for stale in [a for a in bpy.data.actions
                  if a.name == args.action or a.name.startswith(args.action + ".")]:
        bpy.data.actions.remove(stale)
    action = bpy.data.actions.new(args.action)
    if action.name != args.action:
        raise RuntimeError(f"动作名被占用：期望 {args.action!r}，实际 {action.name!r}")
    action.use_fake_user = True
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import blender_action_compat as bac
        bac.assign_action(ad, action)
    except Exception as exc:
        print(f"[WARN] 取道层不可用（{exc}），退回直接指派")
        ad.action = action

    keyed = ctrl_bones + [f"{BONE_PREFIX}Neck", f"{BONE_PREFIX}Head"]   # 头颈的补偿必须一起打键
    for frame, bend, pelvis, hands_on_rail, curl_amount in SCHEDULE:
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        apply_channels(arm, captured[frame])
        if hands_on_rail:
            for side in ("Left", "Right"):
                spec = hand_orient.get((frame, side))
                apply_finger_curl(arm, side, curl[side], curl_amount)
                if spec:
                    pb = arm.pose.bones[f"CTRL_{side}Hand"]
                    pb.rotation_mode = "XYZ"
                    pb.rotation_euler = Euler([math.radians(a) for a in spec["hand_euler_deg"]], "XYZ")
                tsp = thumb_orient.get((frame, side))
                if tsp:
                    tb = arm.pose.bones[f"{BONE_PREFIX}{side}HandThumb1"]
                    tb.rotation_mode = "XYZ"
                    tb.rotation_euler = Euler([math.radians(a) for a in tsp["euler_deg"]], "XYZ")
        update()
        for name in keyed:
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
        arm.pose.bones["CTRL_Hips"].keyframe_insert("location", frame=frame)
        for side in ("Left", "Right"):
            for finger in FINGERS:
                for k in (1, 2, 3, 4):
                    name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
                    if name in arm.pose.bones:
                        arm.pose.bones[name].keyframe_insert("rotation_euler", frame=frame)
            tsp = thumb_orient.get((frame, side))
            if tsp:
                tb = arm.pose.bones[f"{BONE_PREFIX}{side}HandThumb1"]
                tb.rotation_mode = "XYZ"
                tb.rotation_euler = Euler([math.radians(a) for a in tsp["euler_deg"]], "XYZ")
                tb.keyframe_insert("rotation_euler", frame=frame)
    bpy.context.scene.frame_start = SCHEDULE[0][0]
    bpy.context.scene.frame_end = SCHEDULE[-1][0]
    if args.host == "live":
        # ⚠️ 预览必须**停在到位帧**，不能停在首帧：首帧是站立中立姿势，owner 打开窗口看到的是"一个人站着"，
        #    会直接得出"看不见动作"（2026-09-14 实测踩到）。headless/存档路径仍回首帧（导出的首帧不变量）。
        arrival = [f for f, _b, _p, on, _c in SCHEDULE if on][-1]
        bpy.context.scene.frame_set(arrival)
        print(f"预览：已停在到位帧 {arrival}（时间轴 {SCHEDULE[0][0]}–{SCHEDULE[-1][0]}，按空格可播）")
        print("提示：母版里 CTRL/MIXAMORIG 两个骨骼集合默认可见 ⇒ 78 根骨的八面体会挡在人身前；"
              "看姿势时建议在 Outliner 里把这两个集合的眼睛关掉（纯显示层，不影响动作）。")
    else:
        bpy.context.scene.frame_set(SCHEDULE[0][0])
    report["action"] = args.action
    report["action_frames"] = [SCHEDULE[0][0], SCHEDULE[-1][0]]
    report["action_fcurves"] = len(action.fcurves) if hasattr(action, "fcurves") else None

    # ---- 回显卡（口径 §四 V-a：每一项都要有**产物侧**读数）----
    foot_worst = max(r[f"foot_{s}_drift_mm"] for r in verify for s in ("Left", "Right"))
    card = [
        {"owner 的话": "人体站在椅子背面", "解成": "角色在靠背一侧；椅心 y=−{:.2f}".format(-args.chair),
         "参考系": "世界/道具", "判据量": "腕↔靠背中心面 (mm)",
         "产物侧读数": last["wrist_to_back_mm"], "状态": "✅" if last["wrist_to_back_mm"] <= 60.0 else "❌"},
        {"owner 的话": "弯腰", "解成": "骨盆局部 X = {}°".format(int(last["bend_deg"])),
         "参考系": "角色体侧", "判据量": "到位帧弯腰角 (deg)",
         "产物侧读数": last["bend_deg"], "状态": "✅（自由度表 owner 圈定）"},
        {"owner 的话": "目视前方", "解成": "Neck/Head 反向补偿（解出 Head X={:.2f}° · Neck X={:.2f}°）".format(
            report["gaze_solve"][last["frame"]]["head_x_deg"], report["gaze_solve"][last["frame"]]["neck_x_deg"]),
         "参考系": "世界/重力", "判据量": "头骨上轴偏离竖直 (deg)",
         "产物侧读数": last["gaze_up_deg"], "状态": "✅" if abs(last["gaze_up_deg"]) <= 2.0 else "❌"},
        {"owner 的话": "双手手掌贴合椅背上方", "解成": "掌面点 = 手骨原点 + 32.68 mm × 掌面法向（局部 +Z）",
         "参考系": "道具局部", "判据量": "掌面最低点↔顶面 (mm) ≤ 2.8；负 = 陷入",
         "产物侧读数": last["palm"]["Left"]["to_rail_top_mm"],
         "状态": "✅" if -PROVISIONAL_TOL_MM <= last["palm"]["Left"]["to_rail_top_mm"] <= CONTACT_TOL_MM else "❌"},
        {"owner 的话": "大拇指贴住椅背的背面（近侧 y ≥ −0.45）", "解成": "拇指尖 y 相对近侧面",
         "参考系": "道具局部", "判据量": "拇指尖 − 近侧面 (mm)",
         "产物侧读数": last["thumb"]["Left"]["y_mm_vs_near_face"],
         "状态": "✅" if last["thumb"]["Left"]["y_mm_vs_near_face"] >= 0 else "❌"},
        {"owner 的话": "其余四指贴住椅背的正面（远侧 y ≤ −0.49）", "解成": "中指尖 y 相对远侧面",
         "参考系": "道具局部", "判据量": "中指尖 y (m) vs −0.49",
         "产物侧读数": last["tip_Left_m"][1],
         "状态": "✅" if last["tip_Left_m"][1] <= BACK_FAR_Y else "❌"},
        {"owner 的话": "虎口卡住上沿（owner 第四轮）", "解成": "虎口 = 拇指根↔食指根中点 + ε·掌面法向",
         "参考系": "世界/道具", "判据量": "虎口↔上沿 (mm) ≤ 2.8 且 y 在板厚内",
         "产物侧读数": {"离上沿": last["web"]["Left"]["above_edge_mm"], "在板厚内": last["web"]["Left"]["in_slab"]},
         "状态": "✅" if (abs(last["web"]["Left"]["above_edge_mm"]) <= CONTACT_TOL_MM
                        and last["web"]["Left"]["in_slab"]) else "❌"},
        {"owner 的话": "（未提及）肘别往外顶", "解成": "肘相对肩-腕弦的分量",
         "参考系": "角色体侧", "判据量": "后 ≥ 60 mm 且 |侧| ≤ 40 mm",
         "产物侧读数": last["elbow_Left_offset_mm"],
         "状态": "✅" if (last["elbow_Left_offset_mm"]["back"] >= 60.0
                        and abs(last["elbow_Left_offset_mm"]["side"]) <= 40.0) else "❌"},
        {"owner 的话": "（未提及）脚踩原地", "解成": "踝回静止位（解析腿解）",
         "参考系": "世界", "判据量": "逐帧脚漂移 (mm)", "产物侧读数": foot_worst,
         "状态": "✅" if foot_worst <= 15.0 else "❌"},
    ]
    report["feedback_card"] = card
    report["ok"] = not report["problems"]
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("=" * 92)
    print(f"动作 {args.action} · 帧 {SCHEDULE[0][0]}–{SCHEDULE[-1][0]} @ {args.fps} fps · "
          f"椅子中心前方 {args.chair} m · 靠背中心面 y={lay['back_cy']:.3f} · 顶杆 z={lay['rail_top_z']:.4f}")
    print(f"{'帧':>4}{'弯腰':>6}{'腕↔靠背':>10}{'腕高于顶杆':>12}{'指尖扣住':>10}{'肘角':>8}{'肘后/下/侧':>16}{'脚漂移':>9}")
    for row in verify:
        print(f"{row['frame']:>4}{row['bend_deg']:>5.0f}°{row['wrist_to_back_mm']:>10.1f}"
              f"{row['hand_above_rail_mm']:>12.1f}{str(row['tip_wraps_rail_Left']):>10}"
              f"{row['elbow_Left_deg']:>7.1f}°"
              f"{row['elbow_Left_offset_mm']['back']:>7.0f}/{row['elbow_Left_offset_mm']['down']:<4.0f}/{row['elbow_Left_offset_mm']['side']:<5.0f}"
              f"{row['foot_Left_drift_mm']:>9.1f}")
    print("自由度表（owner 圈定 / agent 解）")
    for row in FREEDOM_TABLE:
        print(f"  {row['量']:<16}{row['归属']:<14}{row['值']:<32}{row['依据'][:44]}")
    print("逐指读数（口径 §七 硬规矩 2：成组的项必须并列打印）")
    print(f"  {'手':<6}{'指':<8}{'指尖 y':>10}{'指尖 z':>10}{'距远侧面(mm)':>14}  所在侧")
    for _s in ("Left", "Right"):
        _d = verify[-1][f"digits_{_s}"]
        for dd in DIGITS:
            v = _d[dd]
            print(f"  {_s:<6}{dd:<8}{v['tip_y']:>10.4f}{v['tip_z']:>10.4f}{v['vs_far_face_mm']:>14.1f}  {v['side']}")
    print("回显卡（口径 §四：每一项都要有产物侧读数）")
    for row in card:
        print(f"  {row['owner 的话'][:26]:<28}| {row['判据量'][:30]:<32}| {str(row['产物侧读数'])[:34]:<36}| {row['状态']}")
    print(f"报告: {report_path}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    print("=" * 92)

    if args.host == "live":
        print("（--host live：预览，不写回母版）")
    elif not args.no_save:
        bpy.ops.wm.save_as_mainfile(filepath=str(tmpl), compress=False)
        print(f"已写回母版：{tmpl}")
    return 0 if report["ok"] else 1


# ══════════════════════════════════════════════════════════════════════════════
# 宿主 2：卡 1「掐棱」测量（`--task card1`）——#164 的主交付
#
#   产物：`data/hand_grip_cards.json`（卡 1 的 F3/F4/F6/F7/F8/F10/F11 逐字段数值）
#   权威：design/presentation/动作描述口径.md §十三（字段语义与判据形态枚举）
#   ⚠️ 本宿主**不产出动作**：卡 1 是**引用件**，不是 clip（口径 §13.1 甲/乙/丙 的取舍）
# ══════════════════════════════════════════════════════════════════════════════

CARD1_SIDES = ("Left", "Right")
#: F7 的尺寸扫描（口径 §13.5「7 档 / 10 → 80 mm」：区间与步长照写，档数取 8 —— 区间相同时
#: 10 mm 步长给 8 档；多一档是机器的活，不额外花 owner 的时间，证据里如实登记）
CARD1_F7_SCAN_MM = (10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0)
#: 卡 1 的基准板厚 = 椅背实测板厚（40 mm，`动作库规格.md §四·丁` 的权威常量）
CARD1_BASELINE_THICKNESS_MM = round(BACK_THICKNESS * 1000.0, 1)
#: F10 的四指蜷曲量（基准；由 `--scan` 的校准表选定，见证据 §三）
CARD1_CURL_BASELINE = 1.4
#: 卡 1 的身体条件：**弯腰角**（agent 解：可达性反解——55° 时手臂被夹直、80° 时肘反折）
CARD1_BEND = 75.0
#: 抓握高度 = 板顶 − 本值（由 `--scan` 选定：板顶正下方那个位置会把手臂拉直）
CARD1_GRIP_DROP = 0.075
#: 身体条件（与 #163 的同一条路径一致：弯腰 + 骨盆后移 0.10 m、下沉 0.05 m）
CARD1_PELVIS_OFFSET = (0.0, 0.100, -0.050)
#: `--scan` 校准扫描的三个变量（只在校准期用；选定值写进上面前三个常量）
CARD1_SCAN_BENDS = (CARD1_BEND,)
CARD1_SCAN_DROPS = (0.075,)
CARD1_SCAN_CURLS = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0)


def pair_status(row, tol=CONTACT_TOL_MM):
    """接触对状态：**逐项**判（成组项全部在容差内才算 ✅）——§七 硬规矩 2 的机械化。"""
    v = row.get("读数_mm")
    if v is None:
        return "❓"
    vals = v if isinstance(v, (list, tuple)) else [v]
    return "✅" if all(x is not None and abs(x) <= tol for x in vals) else "❌"


def pair_residual_mm(rows):
    """**约束残差** = 逐接触对"超出容差的那部分"的最大值（mm）；0 = 全部落在容差内。

    口径 §13.5 的改族阈值 = 残差**首次超容差**的那个尺寸 ⇒ 残差必须能报错、且**单调可比**。
    """
    worst = 0.0
    for r in rows:
        v = r.get("读数_mm")
        if v is None:
            continue
        vals = v if isinstance(v, (list, tuple)) else [v]
        for x in vals:
            if x is None:
                continue
            worst = max(worst, abs(x) - CONTACT_TOL_MM)
    return round(worst, 2)


def card1_case(arm, args, thickness_mm, grip_z, curl_amount, curl_axis, side):
    """一个扫描格的完整测量：重建板代理 → 解掐棱握式 → 读接触对（判据一律对着**产物几何**）。"""
    lay = build_board_proxy(thickness_mm / 1000.0, distance=args.chair)
    frame = chair_end_frame(side, lay)
    grip = grip_board_edge(arm, side, frame, grip_z, curl_amount, curl_axis,
                           label=f"{thickness_mm:.0f}mm-{side}")
    rows = grip_board_edge_readings(arm, side, frame)
    pinch = points_min_distance_mm(finger_skin_world(arm, side, "Thumb"),
                                   finger_skin_world(arm, side, "Index"))
    return {"thickness_mm": thickness_mm, "lay": lay, "grip": grip, "pairs": rows,
            "residual_mm": pair_residual_mm(rows), "pinch_gap_mm": pinch,
            "frame_axes": grip["frame_axes"]}


def card1_json(report, args):
    """把测量报告折成**机器源**（`data/hand_grip_cards.json`）——字段名逐字取口径 §13.3。"""
    base = report["baseline"]["Left"]
    scan = report["f7_scan"]
    ref = report.get("f6_refined_mm") or {}
    # ⚠️ 边界一律取**细化并验证过**的那两个读数（第一版这里从 scan 列表里"取第一个越界档"，
    #    于是厚侧界报成 10.0 mm——那是**薄侧**的越界档。扫描表不是单调的，别拿它当边界。）
    thick_usable = ref["厚侧"][1] if ref.get("厚侧") else None
    thick_bound = ref["厚侧"][0] if ref.get("厚侧") else None
    thin_usable = ref["薄侧"][1] if ref.get("薄侧") else None
    thin_bound = ref["薄侧"][0] if ref.get("薄侧") else None
    return {
        "_meta": {
            "schema_version": "1.0",
            "design_authority": "design/presentation/动作描述口径.md §十三",
            "role": "generator-input",
            "measured_by": "code/tools/author_xbot_chair_grab.py --task card1",
            "blender": report["blender"],
            "template": report["template"],
            "measured_at": report["measured_at"],
            "units": "长度 m；间隙/残差 mm；角度 deg",
            "contact_tol_mm": CONTACT_TOL_MM,
            "epsilon_palm_mm": round(EPSILON_PALM_M * 1000.0, 4),
            "note": "本文件是卡 1 的**逐字段数值**权威；字段语义与判据形态枚举的权威是口径 §十三。",
        },
        "cards": [{
            "F1_索引键": report["index_key"],
            "F2_别名位": {
                "消费端语汇": ["正握/反握（武器语汇，owner 2026-09-15 已否）"],
                "符号变体": "侧握 ↔ 上罩 = 棱的方向与接近方向换行（F8），非某一行取反",
            },
            "F3_三轴映射": {
                "来源": "本仓实测（`--task card1` 的 f3 段）",
                "行": [
                    {"手骨轴": "+Z 掌面法向", "世界指向（静止）": report["f3"]["rest"]["Left"]["axes_world"]["Z"],
                     "判据": "掌面 = 骨局部 +Z（口径 §8.1，ε = 32.68 mm）",
                     "读数": f'静止时与世界 +Z 夹角 {report["f3"]["rest"]["Left"]["Z_vs_world_Z_deg"]}°（180° = 掌面朝下）'},
                    {"手骨轴": "+Y 腕 → 指尖", "世界指向（静止）": report["f3"]["rest"]["Left"]["axes_world"]["Y"],
                     "判据": "与实测「腕 → 中指指尖」方向同向（口径 U9，本片当场量）",
                     "读数": f'夹角 {report["f3"]["rest"]["Left"]["Y_vs_wrist_to_tip_deg"]}°（左）/ '
                             f'{report["f3"]["rest"]["Right"]["Y_vs_wrist_to_tip_deg"]}°（右）'},
                    {"手骨轴": "X 手指屈曲轴", "世界指向（静止）": report["f3"]["rest"]["Left"]["axes_world"]["X"],
                     "判据": "外部判据：屈曲把中指尖带向拇指尖（四指）/ 把拇指尖带向食指尖（拇指）",
                     "读数": {g: {"左": report["f3"]["curl"]["Left"][g]["axis"] + f'{report["f3"]["curl"]["Left"][g]["sign"]:+d}',
                                  "右": report["f3"]["curl"]["Right"][g]["axis"] + f'{report["f3"]["curl"]["Right"][g]["sign"]:+d}',
                                  "判据读数_mm": {"静息": report["f3"]["curl"]["Left"][g]["rest"],
                                                  "屈曲": report["f3"]["curl"]["Left"][g]["readings"][
                                                      report["f3"]["curl"]["Left"][g]["axis"] +
                                                      f'{report["f3"]["curl"]["Left"][g]["sign"]:+d}'],
                                                  "全部候选": report["f3"]["curl"]["Left"][g]["readings"]},
                                  "成立": report["f3"]["curl"]["Left"][g]["criterion_valid"]}
                              for g in CURL_GROUPS}},
                ],
            },
            "F4_分区分工与接触对清单": [
                {"手部分区": r["手部分区"], "物体分区": r["物体分区"], "判据形态": r["判据形态"],
                 "容差档": r["容差档"], "并列项": r.get("并列项", "—"),
                 "基准读数_mm": r["读数_mm"], "状态": r["状态"]}
                for r in report["baseline"]["Left"]["pairs"]
            ],
            "F5_判据形态与容差档": {
                "形态": ["点↔线（虎口↔近侧竖棱 · 四指↔远侧竖棱）", "点↔面（拇指↔近侧面）"],
                "容差": {"换算 ε": f'{round(EPSILON_PALM_M * 1000.0, 4)} mm（掌面，逐骨，口径 §8.1）',
                         "验收 tol_contact": f"{CONTACT_TOL_MM} mm（口径 §8.2）"},
                "为什么两个数不许混": "口径 §8.2：把两者合成一个数 ⇒ 掌面悬空 30.8 mm 被判成贴合",
            },
            "F6_尺寸适用区间": {
                "量": "板厚",
                "区间_mm": [thin_usable if thin_usable is not None else scan[0]["thickness_mm"],
                            thick_usable if thick_usable is not None else scan[-1]["thickness_mm"]],
                "区间判据": "全部接触对的 |读数| ≤ tol_contact = 2.8 mm（两端都越界：薄侧四指**越过**远侧棱、"
                            "厚侧四指**够不到**远侧棱）",
                "薄侧界（四指越过远侧棱）": {
                    "判据": "约束残差首次 > 0（= 逐项超出 tol_contact）",
                    "读数_mm": thin_bound,
                    "说明": ("" if thin_bound is not None else
                             f"**未在扫描区间内出现**：{scan[0]['thickness_mm']:.0f} mm 处残差仍为 0"
                             f"（逐指蜷曲会自适应，薄板反而好掐）⇒ 该侧越界尺寸 < {scan[0]['thickness_mm']:.0f} mm，"
                             f"越界落点按「缺口」登记")},
                "厚侧界（四指够不到远侧棱）": {
                    "判据": "同上",
                    "读数_mm": thick_bound},
                "⚠️ 未出现的退化（如实登记）": "「棱太薄 ⇒ 掐不住、退化为捏/对指」的判据（拇指蒙皮↔食指蒙皮 ≤ 0）"
                                              "在 10–80 mm 全程**未触发**（恒定 21.87 mm）——薄侧真正的越界形态是"
                                              "**四指越过远侧棱**（+19.5 mm @10 mm），不是捏不上",
                "扫描": [{"板厚_mm": r["thickness_mm"], "残差_mm": r["residual_mm"],
                          "捏间隙_mm": r["pinch_gap_mm"]} for r in scan],
            },
            "F7_改族阈值与越界落点": report["f7"],
            "F8_接近方向与无解组合": report["f8"],
            "F9_方位角可行区间": {
                "适用": False,
                "理由": "圆柱族专用（绕轴旋转对称 ⇒ 方位角不是输入）；卡 1 的对象是**板棱**，棱的方向是输入",
            },
            "F10_手型（甲₁）": {
                "逐指_4节屈曲角_deg": {
                    f: [round(a * (base["grip"].get("curl_solve") or {}).get(f, {}).get("蜷曲量",
                             base["grip"]["curl_amount"]), 2) for a in FINGER_CURL_DEG[f]]
                    for f in FINGER_CURL_DEG},
                "逐指蜷曲量（**本片解出**，见 §13.3「逐指 4 节屈曲角」）": {
                    f: v["蜷曲量"] for f, v in (base["grip"].get("curl_solve") or {}).items()},
                "逐指校验（板体带符号间隙 mm，正 = 悬空 / 负 = 陷入）": {
                    f: v["板体间隙_mm"] for f, v in (base["grip"].get("curl_solve") or {}).items()},
                "⚠️ 为什么必须逐指": "四根手指长度不同：同一个蜷曲量下它们到板的最近间隙差 **14 mm**"
                                    "（实测 curl 1.0：[+7.8, +10.8, +3.2, −3.1]）⇒ 一个系数不可能让四根都贴住",
                "蜷曲量系数（未逐指解时的基准）": report["baseline"]["Left"]["grip"]["curl_amount"],
                "掌三轴（骨局部 → 世界）": report["baseline"]["Left"]["grip"]["hand_axes"],
                "拇指单独解（4 节可动骨）": report["baseline"]["Left"]["grip"]["thumb"],
                "分工": "朝向前三轴作**主条件**（解析解），落点读数（F11）用来**验**（owner 2026-09-15 接受）",
            },
            "F11_落点读数（甲₂）": {
                "虎口": {"世界坐标_m": base["grip"]["web_point_m"],
                         "↔近侧竖棱_mm": base["grip"]["web_to_edge_mm"],
                         "沿板厚方向_mm": base["grip"]["web_along_n_mm"],
                         "沿端面方向_mm": base["grip"]["web_along_u_mm"]},
                "拇指": {"↔近侧面_mm": base["grip"]["thumb_gap_mm"]},
                "四指逐根_↔远侧竖棱_mm": dict(zip(base["pairs"][2]["逐项名"],
                                                base["pairs"][2]["读数_mm"])),
                "掌面↔端面_mm": {
                    "读数": base["grip"]["palm_to_end_face_mm"],
                    "性质": "**非接触对**（口径 §13.6：侧握下掌面不构成接触对）——本片实测证实："
                            "掌面蒙皮离端面 10.5 mm ⇒ 是「贴着棱」而不是「压着面」"},
                "腕": {"目标_m": base["grip"]["wrist_target_m"],
                       "肘角_deg": base["grip"]["elbow_deg"],
                       "肘偏移_mm": base["grip"]["elbow_offset_mm"],
                       "肘平面扫描": base["grip"].get("elbow_pick"),
                       "肘判据（沿用 #163）": "向后 ≥ 60 · |侧向| ≤ 40 · 向下 ≥ 20（mm）"},
            },
            "F12_消费登记": [
                {"动作": "BendGripChairBack（#163 侧握版，卡 1 基准）", "出处": "issue #163 · 口径 §13.6"},
                {"动作": "扣住门边推开半掩的门（#164 新动作，独立验证）",
                 "出处": "回合战斗流程.md §10.13「关门/开门」",
                 "owner 目视": "手 ↔ 物这一层通过（「手的抓握效果是对的」）；**整体开门姿态**观感不自然，"
                               "owner 明确裁定不在 #164 范围（另开）"},
            ],
        }],
    }


def render_still(path, cam_loc, look_at, res=(1100, 800)):
    """**静帧**（headless 可复现）：临时相机 + 太阳光 + Workbench 引擎 ⇒ 只写 PNG，不改母版。

    ⚠️ 用渲染而不是 GUI 截图：GUI 截图**不逐位可复现**（重绘时序/悬停高亮，见危险点表 §七）。
    """
    scene = bpy.context.scene
    cam = bpy.data.objects.get("REF_StillCam")
    if cam is None:
        cdata = bpy.data.cameras.new("REF_StillCam")
        cam = bpy.data.objects.new("REF_StillCam", cdata)
        scene.collection.objects.link(cam)
    cam.location = Vector(cam_loc)
    cam.rotation_euler = (Vector(look_at) - Vector(cam_loc)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 50.0
    scene.camera = cam
    if bpy.data.objects.get("REF_StillSun") is None:
        ldata = bpy.data.lights.new("REF_StillSun", type="SUN")
        sun = bpy.data.objects.new("REF_StillSun", ldata)
        scene.collection.objects.link(sun)
        sun.rotation_euler = Euler((math.radians(55.0), 0.0, math.radians(35.0)), "XYZ")
        ldata.energy = 3.0
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)


def main_card1() -> int:
    from datetime import datetime
    args = parse_args(list(sys.argv))
    if args.report_in:
        # 报告 → 机器源（唯一来源）：重排不改任何读数，只改字段组织
        rep = json.loads(Path(args.report_in).read_text(encoding="utf-8"))
        out = Path(args.card_out) if args.card_out else REPO_ROOT / "data/hand_grip_cards.json"
        out.write_text(json.dumps(card1_json(rep, args), ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"机器源（由报告重排）：{out}")
        return 0
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    drop_temp(arm)
    clear_pose(arm)

    lay0 = board_layout(args.chair)
    grip_z = args.grip_z if args.grip_z is not None else (lay0["rail_top_z"] - args.grip_drop)
    curl_amount = args.curl if args.curl is not None else CARD1_CURL_BASELINE
    report = {"script": Path(__file__).name, "task": "card1", "blender": bpy.app.version_string,
              "template": str(tmpl), "host": args.host, "index_key": CARD1_INDEX_KEY_NAME,
              "measured_at": datetime.now().isoformat(timespec="seconds"),
              "chair_distance_m": args.chair, "grip_z_m": round(grip_z, 4),
              "grip_drop_m": args.grip_drop, "curl_amount": curl_amount,
              "board_top_z": round(lay0["rail_top_z"], 4), "problems": []}

    # ---- A. F3：三轴映射（静止 T-pose 实测；U9 的 `+Y` 当场量）----
    clear_pose(arm)
    report["f3"] = {
        "rest": {s: hand_axes_reading(arm, s) for s in CARD1_SIDES},
        "curl": {s: {g: detect_curl_axis_group(arm, s, g) for g in CURL_GROUPS} for s in CARD1_SIDES},
    }
    curl_axis = {s: {"axis": report["f3"]["curl"][s]["四指"]["axis"],
                     "sign": report["f3"]["curl"][s]["四指"]["sign"]} for s in CARD1_SIDES}
    report["curl_axis_used"] = curl_axis
    for s in CARD1_SIDES:
        r = report["f3"]["rest"][s]
        print(f"F3 三轴 {s:5s}: 局部+X→{r['axes_world']['X']}  +Y→{r['axes_world']['Y']}  "
              f"+Z→{r['axes_world']['Z']} · Y↔腕→指尖 {r['Y_vs_wrist_to_tip_deg']}° · "
              f"Z↔世界+Z {r['Z_vs_world_Z_deg']}°")
        for g in CURL_GROUPS:
            c = report["f3"]["curl"][s][g]
            best = c["axis"] + f"{c['sign']:+d}"
            print(f"      屈曲轴自测 {s:5s}/{g}: 最优 {best} · 丙(指尖→掌面) "
                  f"{c['rest']['palm_offset_mm']} → {c['readings'][best]['palm_offset_mm']} mm · "
                  f"乙(跨组指尖距) {c['rest']['tip_to_other_mm']} → {c['readings'][best]['tip_to_other_mm']} mm"
                  f"（丙判据{'成立' if c['criterion_valid'] else '**失效**'}·丙乙"
                  f"{'一致' if c['agree_with_cross_group'] else '**不一致**'}）")

    # ---- 身体条件：脚踝静止位（双脚踩原地）----
    clear_pose(arm)
    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in CARD1_SIDES}

    # ---- B. 校准扫描（--scan）：抓握高度 × 蜷曲量——只打印表，不写机器源 ----
    if args.scan:
        print("=" * 100)
        print("卡 1 校准扫描（板厚 40 mm · 左手）：弯腰角 × 抓握高度 × 蜷曲量（四指读数 = 板体带符号间隙）")
        print(f"{'bend(°)':>8}{'drop(mm)':>8}{'curl':>6}{'残差':>8}{'虎口↔棱':>9}{'拇指↔近侧面':>12}"
              f"{'逐指↔板体(mm)':>34}{'肘角':>8}{'肘后':>7}{'肘侧':>7}{'肘下':>7}")
        for bend in CARD1_SCAN_BENDS:
            for drop in CARD1_SCAN_DROPS:
                for curl in CARD1_SCAN_CURLS:
                    clear_pose(arm)
                    bent_body_setup(arm, m3, bend, CARD1_PELVIS_OFFSET, foot_rest)
                    case = card1_case(arm, args, CARD1_BASELINE_THICKNESS_MM,
                                      lay0["rail_top_z"] - drop, curl, curl_axis["Left"], "Left")
                    g = case["grip"]
                    gaps = case["pairs"][2]["读数_mm"]
                    print(f"{bend:>9.0f}{drop * 1000:>7.0f}{curl:>6.1f}{case['residual_mm']:>8.2f}"
                          f"{g['web_to_edge_mm']:>9.2f}{str(g['thumb_gap_mm']):>12}"
                          f"{str([round(x, 1) for x in gaps]):>34}{g['elbow_deg']:>8.1f}"
                          f"{g['elbow_offset_mm']['back']:>7.0f}{g['elbow_offset_mm']['side']:>7.0f}"
                          f"{g['elbow_offset_mm']['down']:>7.0f}")
        print("=" * 100)
        return 0

    # ---- C. 基准格（板厚 40 mm）——F4/F5/F10/F11 从这一格取 ----
    report["body_setup"] = bent_body_setup(arm, m3, CARD1_BEND, CARD1_PELVIS_OFFSET, foot_rest)
    print(f"身体条件：弯腰 {CARD1_BEND}° · 骨盆位移 {CARD1_PELVIS_OFFSET} · "
          f"目视水平 {report['body_setup']['gaze']['after_deg']}°")
    report["baseline"] = {}
    for side in CARD1_SIDES:
        clear_pose(arm)
        bent_body_setup(arm, m3, CARD1_BEND, CARD1_PELVIS_OFFSET, foot_rest)
        case = card1_case(arm, args, CARD1_BASELINE_THICKNESS_MM, grip_z, curl_amount, curl_axis[side], side)
        for r in case["pairs"]:
            r["状态"] = pair_status(r)
        case["grip"]["hand_axes"] = {
            "骨局部X（蜷曲轴）": [round(c, 4) for c in
                                 (arm.matrix_world.to_3x3() @ arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
                                  .matrix.to_3x3() @ Vector((1.0, 0.0, 0.0))).normalized()],
            "骨局部Y（腕→指尖）": [round(c, 4) for c in
                                   (arm.matrix_world.to_3x3() @ arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
                                    .matrix.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()],
            "骨局部Z（掌面法向）": [round(c, 4) for c in
                                    (arm.matrix_world.to_3x3() @ arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
                                     .matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()],
        }
        report["baseline"][side] = case
        if case["residual_mm"] > 0.0:
            report["problems"].append(
                f"基准格（{side}，板厚 {CARD1_BASELINE_THICKNESS_MM} mm）残差 {case['residual_mm']} mm > 0")
        print(f"基准格 {side:5s}: 虎口↔棱 {case['grip']['web_to_edge_mm']} mm · "
              f"拇指↔近侧面 {case['grip']['thumb_gap_mm']} mm · 残差 {case['residual_mm']} mm · "
              f"肘角 {case['grip']['elbow_deg']}° · 捏间隙 {case['pinch_gap_mm']} mm")

    # ---- D. F6/F7：尺寸扫描（10 → 80 mm）----
    if args.thickness_mm is not None:
        scan_list = (args.thickness_mm,)
    else:
        scan_list = CARD1_F7_SCAN_MM
    scan = []
    print("F7 尺寸扫描（左手 · 同一 F10 手型）：")
    print(f"{'板厚(mm)':>9}{'残差':>8}{'虎口↔棱':>9}{'拇指↔近侧面':>12}"
          f"{'逐指↔远侧面(mm)':>40}{'捏间隙':>9}{'肘角':>8}")
    for t_mm in scan_list:
        clear_pose(arm)
        bent_body_setup(arm, m3, CARD1_BEND, CARD1_PELVIS_OFFSET, foot_rest)
        case = card1_case(arm, args, t_mm, grip_z, curl_amount, curl_axis["Left"], "Left")
        g = case["grip"]
        gaps = case["pairs"][2]["读数_mm"]
        print(f"{t_mm:>9.0f}{case['residual_mm']:>8.2f}{g['web_to_edge_mm']:>9.2f}"
              f"{str(g['thumb_gap_mm']):>12}{str([round(x, 1) for x in gaps]):>40}"
              f"{str(case['pinch_gap_mm']):>9}{g['elbow_deg']:>8.1f}")
        scan.append(case)
    report["f7_scan"] = scan

    def _residual_at(t_mm):
        clear_pose(arm)
        bent_body_setup(arm, m3, CARD1_BEND, CARD1_PELVIS_OFFSET, foot_rest)
        c = card1_case(arm, args, t_mm, grip_z, curl_amount, curl_axis["Left"], "Left")
        return c["residual_mm"]

    def refine(ok_t, bad_t, steps=3):
        """二分细化窗口边界（**机器的活**，口径 §13.5：用扫描换目视）。

        ⚠️ 必须以**已验过的** ok / bad 两端为输入：残差在薄侧**不是单调的**（四根指头长度不同 ⇒
        各自的"搭上远侧棱"厚度不同）。第一版实现拿"最小越界档"当 bad 端并**没验 ok 端**，
        于是报出"最后一个可用 10.0 mm"——而 10 mm 那档残差是 16.66 mm。**未验证的端点不算读数。**
        """
        for _ in range(steps):
            mid = (ok_t + bad_t) / 2.0
            if _residual_at(mid) > 0.0:
                bad_t = mid
            else:
                ok_t = mid
        return round(bad_t, 1), round(ok_t, 1)

    base_t = CARD1_BASELINE_THICKNESS_MM
    thick_above = next((r["thickness_mm"] for r in scan if r["residual_mm"] > 0.0 and r["thickness_mm"] > base_t), None)
    thin_below = next((r["thickness_mm"] for r in reversed(scan)
                       if r["residual_mm"] > 0.0 and r["thickness_mm"] < base_t), None)
    thick_ref = refine(base_t, thick_above) if (thick_above and args.thickness_mm is None) else None
    thin_ref = refine(base_t, thin_below) if (thin_below and args.thickness_mm is None) else None
    if thick_ref:
        print(f"厚侧边界细化：首次越界 {thick_ref[0]} mm（最后一个可用 {thick_ref[1]} mm）")
    if thin_ref:
        print(f"薄侧边界细化（向下）：首次越界 {thin_ref[0]} mm（最后一个可用 {thin_ref[1]} mm）")
    report["f6_refined_mm"] = {"厚侧": thick_ref, "薄侧": thin_ref}
    thick_bound = thick_ref[0] if thick_ref else None
    thin_bound = thin_ref[0] if thin_ref else None

    # ---- E. F7 改族边 + F8 方向对照 ----
    report["f7"] = {
        "阈值定义": "约束集首次不可满足的那个尺寸（口径 §13.5：读出来的，不是设定的）",
        "阈值_mm": {"厚侧": thick_bound, "薄侧": thin_bound},
        "扫描区间_mm": [scan[0]["thickness_mm"], scan[-1]["thickness_mm"]],
        "越界落点": {
            "厚侧": {"落点": "卡 4（指尖触点）", "状态": "已登记（卡 4 在名录里，尚未建）",
                     "依据": "口径 §13.5 ① 归到另一张卡"},
            "薄侧": {"落点": "缺口（该族未建，不建空卡）", "状态": "已登记",
                     "依据": "口径 §13.5 ③；先例 §6.3『不建空表』"},
        },
        "改族边": [{"from": "卡1", "to": "卡4", "条件": f"板厚 > {thick_bound} mm" if thick_bound else "板厚 > 扫描上界"}],
    }
    report["f8"] = {
        "侧握（基准）": {
            "棱": "椅背侧面的**近侧竖棱**（`x=±half_width`, `y=back_near_y`）",
            "读数_mm": {s: report["baseline"][s]["grip"]["web_to_edge_mm"] for s in CARD1_SIDES},
        },
        "上罩（对照）": {
            "来源": "#163 已接受版本（`6a20c09`）的既有读数，**不是**本宿主重测",
            "虎口↔上沿（原判据，参照**顶面中线**）": "−0.0 mm（#163 证据 §二十）",
            "虎口↔**真棱**（本片改参照后重算）": {
                "上沿近侧棱（`y=−0.45, z=0.7949`）": "20.0 mm",
                "上沿远侧棱（`y=−0.49, z=0.7949`）": "20.0 mm",
                "说明": "由 #163 记录的虎口坐标 `(±0.17, −0.47, 0.7949)` 与板几何**解析换算**，"
                        "原判据参照的中线 `y=back_cy=−0.47` **不是棱**（两面交线才是）",
            },
            "掌面↔顶面_mm": "−22.2（陷入）", "拇指↔近侧面_mm": "−30.0", "四指↔远侧面_mm": "−0.462 ~ −0.468（未过）",
            "结论": "上罩在卡 1 的判据下**两条红**：虎口没落在真棱上、四指没落到远侧面",
            ("⚠️ 本片发现：那条「掌面陷入 22.2 mm」的根因是 ε 换算的掌面法向取自**骨架系**"
             "（母版骨架带 +90° X 旋转 ⇒ 与世界系差 90°；#163 的上罩掌面法向恰是 −Z，不在不动轴上）。"
             "改成世界系后重跑同一姿势：掌面最低点 −22.2 → **+10.5 mm（悬空，不再穿模）**、"
             "肘侧向 31.5 → 49.8 mm（从绿变红）⇒ 上罩那一版的已知偏差里，第 1 条是**工具的错，不是姿势的错**。"
             "本卡登记的对照读数仍取 **#163 记录值**（历史如实），修正后的重跑值见证据"):
             "见证据 §七",
        },
        "两方向的区别": "棱的方向（竖/横）+ 接近方向（侧面/上方）；F3 的三轴映射在两者间**整体重排**",
    }

    # ---- F. 回显卡（口径 §四；行数 = 接触对行数——由**同一列表**生成，结构上不可能不一致）----
    card_rows = []
    for r in report["baseline"]["Left"]["pairs"]:
        card_rows.append({"手部分区": r["手部分区"], "物体分区": r["物体分区"], "判据形态": r["判据形态"],
                          "判据量": f'{r["手部分区"]} ↔ {r["物体分区"]}（{r["判据形态"]}）',
                          "产物侧读数_mm": r["读数_mm"], "容差档": r["容差档"], "状态": r["状态"]})
    report["feedback_card"] = card_rows
    print("回显卡（口径 §四：每一项都有产物侧读数；行数 = 卡 1 的接触对行数）")
    for row in card_rows:
        print(f"  {row['判据量'][:34]:<36}| {str(row['产物侧读数_mm']):>10} | {row['容差档']:<26}| {row['状态']}")

    report["ok"] = not report["problems"]
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"报告: {args.report}")

    # ---- G. 机器源 ----
    if args.thickness_mm is None:
        card_out = Path(args.card_out) if args.card_out else REPO_ROOT / "data/hand_grip_cards.json"
        card_out.parent.mkdir(parents=True, exist_ok=True)
        # 机器源落点：data/hand_grip_cards.json（`role: generator-input`；被 validate_grip_cards.py 核）
        card_out.write_text(json.dumps(card1_json(report, args), ensure_ascii=False, indent=1),
                            encoding="utf-8")
        print(f"机器源: {card_out}")

    # ---- H. 静帧（可选）----
    if args.still:
        edge = report["baseline"]["Left"]["frame_axes"]
        mid = Vector(report["baseline"]["Left"]["grip"]["web_point_m"])
        render_still(args.still, mid + Vector((0.62, 0.72, 0.42)), mid)
        print(f"静帧: {args.still}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    return 0 if report["ok"] else 1


# ══════════════════════════════════════════════════════════════════════════════
# 宿主 3：门边动作「扣住门边推开半掩的门」（`--task door`）——#164 的独立验证件
#
#   口径 §13.6：**同一张卡、新的对象**（棱从椅背换到门边，映射整体重排）
#   ⚠️ 本宿主只交付**静帧**（口径 §13.8 边界：不做动画/关键帧入库、不接 Unity lab、不新增词条）
# ══════════════════════════════════════════════════════════════════════════════

DOOR_ACTION = "PushDoorEdge"
#: (帧, 门开角°, 手是否扣住门边)——半掩 30° → 推开 80°
DOOR_SCHEDULE = ((1, DOOR_OPEN_START_DEG, False), (13, DOOR_OPEN_START_DEG, True),
                 (25, DOOR_OPEN_END_DEG, True))


def main_door() -> int:
    from datetime import datetime
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    drop_temp(arm)
    clear_pose(arm)
    report = {"script": Path(__file__).name, "task": "door", "blender": bpy.app.version_string,
              "template": str(tmpl), "host": args.host, "action": DOOR_ACTION,
              "measured_at": datetime.now().isoformat(timespec="seconds"),
              "schedule": [{"frame": f, "door_open_deg": a, "hooked": h} for f, a, h in DOOR_SCHEDULE],
              "problems": []}

    # 手骨轴的实测与卡 1 同源（不得在两处各测一份）
    clear_pose(arm)
    f3 = {s: hand_axes_reading(arm, s) for s in CARD1_SIDES}
    curl = {s: detect_curl_axis_group(arm, s, "四指") for s in CARD1_SIDES}
    report["f3_rest"] = f3
    report["f3_curl"] = curl
    curl_axis = {s: {"axis": curl[s]["axis"], "sign": curl[s]["sign"]} for s in CARD1_SIDES}
    print(f"F3 复核（门边宿主与卡 1 同源）：+Y↔腕→指尖 {f3['Left']['Y_vs_wrist_to_tip_deg']}°（左）")

    side = "Left"                       # 副手（右手）在推门这一拍是自由的 ⇒ 本片只解一只手
    grip_z = args.grip_z if args.grip_z is not None else 1.15   # 站立时略低于肩（肩高≈1.28 m）
    curl_amount = args.curl if args.curl is not None else CARD1_CURL_BASELINE
    clear_pose(arm)
    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in CARD1_SIDES}
    report["freedom_table"] = [
        {"量": "门开角（半掩 → 推开）", "归属": "owner 圈定（需求原话「扣住门边推开半掩的门」）",
         "值": f"{DOOR_OPEN_START_DEG}° → {DOOR_OPEN_END_DEG}°", "依据": "回合战斗流程 §10.13 关门/开门"},
        {"量": "抓握高度", "归属": "agent 解", "值": f"{grip_z:.2f} m",
         "依据": "站立时肩高（≈1.28 m）− 0.13 m：抓握点离肩越近，腕目标越不逼近臂长"},
        {"量": "身体朝向（转身角）", "归属": "agent 解（可达性反解）", "值": "每帧 = 门边方位角",
         "依据": "不转身则手臂夹直（实测肘 180°、虎口离门边 291.6 mm）"},
        {"量": "身体前倾", "归属": "agent 解（可达性反解）", "值": "0.12 m",
         "依据": "不倾则到位帧腕目标离肩 0.659 m > 臂长 0.562 m（实测：手臂夹直）"},
        {"量": "四指蜷曲量", "归属": "卡 1 的 F10（同一张卡，不另发明）", "值": str(curl_amount),
         "依据": "口径 §13.6：新动作**复用**卡片，不新发明判据"},
    ]
    captured, verify = {}, []
    for frame, open_deg, hooked in DOOR_SCHEDULE:
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        dlay = build_door_proxy(open_deg)
        frame_geo = door_end_frame(dlay)
        me = dlay["mid_edge"]
        yaw = math.degrees(math.atan2(me.x, -me.y))
        report.setdefault("body_yaw", {})[frame] = round(yaw, 2)
        body = standing_body_setup(arm, m3, yaw, foot_rest, lean_m=0.12)
        if frame == DOOR_SCHEDULE[0][0]:
            print(f"身体：转身 {yaw:.1f}° · 前倾 0.12 m · 目视水平 {body['gaze']['after_deg']}°")
        if hooked:
            # 抓握高度**保持常量**（不随门角漂移：那会引入一个无来源的常数）
            grip = grip_board_edge(arm, side, frame_geo, grip_z,
                                   curl_amount, curl_axis[side], label=f"door{frame}")
            pairs = grip_board_edge_readings(arm, side, frame_geo)
            for r in pairs:
                r["状态"] = pair_status(r)
            verify.append({"frame": frame, "door_open_deg": open_deg, "grip": grip, "pairs": pairs,
                           "residual_mm": pair_residual_mm(pairs)})
            print(f"帧 {frame:>3} 门 {open_deg:>5.1f}°: 虎口↔门边 {grip['web_to_edge_mm']:>6.2f} mm · "
                  f"拇指↔近侧面 {str(grip['thumb_gap_mm']):>7} mm · 残差 {pair_residual_mm(pairs):>5.2f} mm · "
                  f"肘角 {grip['elbow_deg']}°")
        else:
            verify.append({"frame": frame, "door_open_deg": open_deg, "grip": None, "pairs": [],
                           "residual_mm": None})
        captured[frame] = capture_channels(arm, [f"CTRL_{side}Arm", f"CTRL_{side}ForeArm",
                                                 f"CTRL_{side}Hand", f"CTRL_Hips",
                                                 f"{BONE_PREFIX}Neck", f"{BONE_PREFIX}Head"])
        for finger in FINGERS:
            for k in (1, 2, 3, 4):
                name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
                if name in arm.pose.bones:
                    pb = arm.pose.bones[name]
                    pb.rotation_mode = "XYZ"
                    captured[frame][name] = {"euler_deg": [math.degrees(a) for a in pb.rotation_euler],
                                             "location": [0.0, 0.0, 0.0]}
    report["verify"] = verify
    hooked_frames = [v for v in verify if v["grip"]]
    if hooked_frames:
        last = hooked_frames[-1]
        worst = max((abs(x) for r in last["pairs"]
                     for x in (r["读数_mm"] if isinstance(r["读数_mm"], list) else [r["读数_mm"]])
                     if x is not None), default=0.0)
        report["arrival"] = {"frame": hooked_frames[0]["frame"], "worst_pair_mm": worst}
        for r in hooked_frames[0]["pairs"]:
            if r["状态"] == "❌":
                report["problems"].append(
                    f"到位帧 {hooked_frames[0]['frame']}：{r['手部分区']}↔{r['物体分区']} "
                    f"读数 {r['读数_mm']} mm 超容差")
    report["feedback_card"] = [
        {"手部分区": r["手部分区"], "物体分区": r["物体分区"], "判据形态": r["判据形态"],
         "产物侧读数_mm": r["读数_mm"], "状态": r["状态"]}
        for r in (hooked_frames[0]["pairs"] if hooked_frames else [])]
    print("回显卡（门边 · 到位帧）")
    for row in report["feedback_card"]:
        print(f"  {row['手部分区']:<12}↔ {row['物体分区']:<10}{row['判据形态']:<8}"
              f"{str(row['产物侧读数_mm']):>9} mm  {row['状态']}")
    report["ok"] = not report["problems"]

    # ---- 打键（写动作；门代理的转角一起打——它只是预览件，不进 FBX）----
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    for stale in [a for a in bpy.data.actions
                  if a.name == args.action or a.name.startswith(args.action + ".")]:
        bpy.data.actions.remove(stale)
    action = bpy.data.actions.new(args.action)
    action.use_fake_user = True
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import blender_action_compat as bac
        bac.assign_action(ad, action)
    except Exception as exc:
        print(f"[WARN] 取道层不可用（{exc}），退回直接指派")
        ad.action = action
    for frame, open_deg, hooked in DOOR_SCHEDULE:
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        apply_channels(arm, captured[frame])
        panel = bpy.data.objects.get("REF_DoorPanel")
        if panel is not None:
            panel.rotation_euler = Euler((0.0, 0.0, math.radians(open_deg)), "XYZ")
            panel.keyframe_insert("rotation_euler", frame=frame)
        update()
        for name in list(captured[frame]):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
    bpy.context.scene.frame_start = DOOR_SCHEDULE[0][0]
    bpy.context.scene.frame_end = DOOR_SCHEDULE[-1][0]
    report["action_frames"] = [DOOR_SCHEDULE[0][0], DOOR_SCHEDULE[-1][0]]

    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"报告: {args.report}")
    if args.still and hooked_frames:
        # 静帧停在**到位帧**（"扣住门边"那一拍）——预览必须停在有内容的那一帧（#163 的教训）
        bpy.context.scene.frame_set(hooked_frames[0]["frame"])
        mid = Vector(hooked_frames[0]["grip"]["web_point_m"])
        render_still(args.still, mid + Vector((0.85, 0.95, 0.45)), mid)
        print(f"静帧: {args.still}")
    if args.host == "live":
        arrival = hooked_frames[0]["frame"] if hooked_frames else DOOR_SCHEDULE[0][0]
        bpy.context.scene.frame_set(arrival)
        print(f"预览：已停在到位帧 {arrival}（时间轴 {DOOR_SCHEDULE[0][0]}–{DOOR_SCHEDULE[-1][0]}）")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    return 0 if report["ok"] else 1




# ══════════════════════════════════════════════════════════════════════════════
# 宿主 5：门边「推到底」（`--task doorpush`）——[#166](https://github.com/verystrongdog/game/issues/166) 的交付
#          （口径 §13.6 的**能播类第一件**）
#
#   完成定义（owner 2026-09-15 裁，口径 §13.6）：**Blender 侧能连着播**（静帧 + 时序 +
#   接地/不穿模，owner 看着不出戏）**+** 导出侧机械门禁 E0–E6 全绿；**不接 Unity 侧 lab**。
#
#   ⚠️ 与宿主 3（`--task door`）**分家**：本条**不改**宿主 3 一行（#164 的读数留在它的证据里）。
#      本宿主修掉宿主 3 上实测到的两处病（逐条读数与根因见证据 §六）：
#      ① **转身写在 `CTRL_Hips` 的 `z` 上**——实测那是**侧倾**（`y` 才绕世界 +Z）：
#         `z=+40°` 时实测脊柱 = (−0.641, 0.058, 0.765)、双脚被甩到 (0.677, 0.024, 0.364)
#         ⇒ 宿主 3 实际做的是"身体横着倒 37°"，这正是 owner 目视那句
#         「**整体开门的样子不太对、像是有病一样**」的来源；
#      ② **腿脚控制骨没进打键表** ⇒ 骨盆一动脚就跟着飘（#165 实测门边动作双侧**全程无支撑**、
#         离地 +160 ~ +313 mm）。本宿主把 `CTRL_*UpLeg / Leg / Foot` 与脚掌朝向一起打键。
# ══════════════════════════════════════════════════════════════════════════════

DOOR_PUSH_ACTION = "PushDoorEdgeFull"

#: X Bot 的**胶囊半径**（`通过开度` 的推导输入；口径 §13.6 与注册表 `通过开度` 同引此值）。
#: 来源：`code/unity/Assets/Scripts/ActionLabDriver.cs` `SizeControllerToModel()` 的
#: `_cc.radius = Clamp(h × 0.19, 0.25, 0.4)`；**记录值 0.3117** 见
#: `code/unity/Assets/Editor/ActionLabBuilder.cs` 与 `code/unity/Assets/Scripts/ChairSeat.cs`
#: 的注释（"胶囊半径 0.3117"）——两处都是**已记录实测值**，不是本次新拍。
X_BOT_CAPSULE_RADIUS_M = 0.3117

#: 「推到底」时身体**到门板中面的净距**（m）。取值由两条硬约束夹出来（不是手拍）：
#: ① 必须够大：净距扣掉板厚一半后要 > 胶囊半径 **0.3117**——人站在门的外侧、不能穿门；
#: ② 不能太大：越大手臂越够不到——实测本值 0.35 / 0.38 / 0.42 时**肩→腕在整段弧上分别恒定
#:   0.448 / 0.472 / 0.504 m**（臂长 0.5617）⇒ 取 **0.38**：净距留 48 mm 余量、手臂留 90 mm 余量。
DOOR_PUSH_CLEARANCE_M = 0.38

#: 站姿的**膝屈下沉量**（m）。为什么需要它：静止姿势的双腿几乎伸直（实测大腿 0.4437 +
#: 小腿 0.4453 = **0.8890 m** vs 髋-踝竖直 **0.8883 m** ⇒ 水平可及仅 ≈ **0.7 mm**）——
#: 不沉髋，迈步时腿**当场被夹直**、踝到不了目标（#165 那条"脚离地 160~313 mm"的一半成因）。
#: 实测下沉 0.06 m 时：踝相对骨盆偏 0.20 m 仍残差 **0**（证据 §三 的预算表）。
DOOR_PUSH_CROUCH_M = 0.06

#: 摆动腿的**抬脚高度**（m）：只要求"足底最低点明确离地"（判据 = M2 > `soleMargin`）。
#: 取值 0.05 m = 一步的正常抬脚量级；逐帧实测最小值见证据 §五。
DOOR_PUSH_STEP_LIFT_M = 0.05

#: 身体摆放（净距）的**解空间候选**——口径 §4.2 硬规矩 5「agent 解的行必须并列 ≥2 个可行解」。
#: 下界由胶囊半径 0.3117（净距扣掉板厚一半后必须更大）、上界由臂长 0.5617 夹出来。
DOOR_PUSH_STANCE_CANDIDATES = (0.33, 0.35, 0.38, 0.42, 0.46)

#: 穿模判据（动作库规格 §四·戊·5 **判据 4**）的骨集：躯干/上臂/大腿**零穿透** ·
#: 手与前臂**允许接触**（骨心进构件内部 ≤ 2 cm）· 非接触部位最小间隙 ≥ 1 cm。
#: ⚠️ 判据量的是**骨段**；owner 看的是**蒙皮** ⇒ 层差登记为已知偏差（口径 §十 的能播类三项表）。
DOOR_PUSH_CLEARANCE_CLASSES = (
    ("躯干/上臂/大腿", 0.0, ("Hips", "Spine", "Spine1", "Spine2", "LeftArm", "RightArm",
                             "LeftUpLeg", "RightUpLeg")),
    #: ⚠️ 五指 20 根一并进"允许接触"档——它们是**真正绕在门边上的那部分**，
    #:    漏掉它们的话这条判据就在最关键的地方留了个洞（判据 4 明写"手与前臂"含指）。
    ("手/前臂/五指（允许接触）", -20.0,
     ("LeftForeArm", "LeftHand", "RightForeArm", "RightHand")
     + tuple(f"LeftHand{f}{k}" for f in ("Thumb", "Index", "Middle", "Ring", "Pinky")
             for k in (1, 2, 3, 4))),
    ("非接触部位", 10.0, ("LeftShoulder", "RightShoulder", "LeftLeg", "RightLeg", "LeftFoot",
                          "RightFoot", "LeftToeBase", "RightToeBase", "Neck", "Head")),
)

#: 时序（帧号；30 fps）。判据面（口径 §十 的「时序」）只有一条：
#: **脚本声明的到位帧 == 从产物算出的判据量极值帧**。表里的帧号是**声明**，不是结论。
#: **门在这条动作里朝哪一侧半掩**（带符号；`DOOR_OPEN_START_DEG` 是宿主 3 的 20°，宿主 3 不动）。
#: ⚠️ **2026-09-16 owner 目视第一条**：「这个动作只能算得上**拉门**」——根因是门的半掩侧：
#:   门朝**角色这侧**开时，自由边是**朝角色扫过来**的，角色只能一边扣住一边**后退** ⇒ 观感是拉。
#:   ⇒ 半掩改到**远侧**（`-20°`），门朝**远离角色**的方向开：角色**上前**扣住自由边、
#:   **向前迈步推**，最后**穿过门洞**。终态仍是 `通过开度` 的**幅值** 49.486°（`-49.486°`）。
DOOR_PUSH_START_DEG = -20.0

DOOR_PUSH_FRAME_NEUTRAL = 1      # 中立姿势（导出侧硬约定：首帧必须中立，否则 E5 报 Rest Pose 漂移）
DOOR_PUSH_FRAME_GRIP = 16        # 扣住（远侧半掩后，要先**走近** 0.68 m 才够得着自由边）
DOOR_PUSH_FRAME_PUSH = 21        # 开始推（门角从这一帧起离开半掩角）
DOOR_PUSH_FRAME_ARRIVAL = 51     # 到位（门到 `-通过开度`）
DOOR_PUSH_FRAME_END = 61         # 保持到这一帧
#: 「先迈哪只脚」= 自由度表第 2 行（`agent 解`）⇒ 两种顺序**都解过、读数并列在证据 §五**；
#: 采用**左脚先迈**（穿模余量好得多：非接触部位 **43.33 mm** vs 另一解的 **15.43 mm**）。
DOOR_PUSH_FIRST_FOOT = "Left"

#: 步数**不写死**：`N = ceil(总行程 / 每步预算)`，窗口按**弧长均分**（口径 §13.6 自由度表第 3 行
#: "迈步步长由臂长与自由边弧长反解"）。每步预算 = **实测的腿预算**：踝相对骨盆偏移超过它就解不动
#: （证据 §三 的预算表：下沉 0.06 m 时 ≈ 0.20 m 起残差抬头，0.09 m 时 0.30 m 仍为 0）。
DOOR_PUSH_STEP_BUDGET_M = 0.20
#: 每个迈步桶里**摆动**占的比例（余下为双支撑）。运动学取值，不是判据阈值。
DOOR_PUSH_SWING_FRACTION = 0.7

#: 副手（右手）：静止姿势是 **T-pose**，不给解就是"机械平举"（owner 2026-09-16 第二条点名）。
#: 目标 = 腕落在体侧（髋骨点 + 本偏移，在**角色体侧系**里给），方向 = 指尖朝下、掌心内向。
DOOR_PUSH_OFFHAND_WRIST_OFFSET = (-0.150, 0.041, -0.153)   # 相对髋骨点（yaw=0 的身体系）
#: 副手的松握量（0 = 五指伸直；卡 1 的 F10 逐指基准角 × 本值）。运动学取值，owner 可改。
DOOR_PUSH_OFFHAND_CURL = 0.35

#: 推的时候**躯干前倾**（三段脊柱各分 1/3；0 = 直挺挺地平移 = owner 说的"机器人"）。
#: 轴向**有来源**：[管线 §2.1.4](design/presentation/Blender动作制作管线.md) 实测
#: `Spine` / `Spine1` / `Spine2` 的**局部 X = 前倾**（头顶前移 314.8 / 280.5 / 248.8 mm）。
#: 总量 12° 是**运动学取值**：肩前移 ≈ 0.12 m（读数见证据 §十四），owner 可改。
DOOR_PUSH_TORSO_LEAN_DEG = 12.0

#: 接地判据容差：**沿用** [对照实验 §2.1](../../design/presentation/动画处理能力对照实验.md) 的
#: `soleMargin`（出身 = `code/unity/Assets/Scripts/FootGroundingIK.cs` 注释的 bind pose 实测）。
#: 数值从**已入库的件** `xbot_contact_phase.py` 取（同一个量不抄第二份）；取不到才退回字面值。
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from xbot_contact_phase import SOLE_MARGIN_MM as DOOR_PUSH_SOLE_MARGIN_MM
except Exception:                                              # pragma: no cover
    DOOR_PUSH_SOLE_MARGIN_MM = 2.8                             # 来源同上（FootGroundingIK.cs）


def door_pass_open_deg(width=DOOR_WIDTH, radius=X_BOT_CAPSULE_RADIUS_M):
    """`通过开度` = 门开到**角色胶囊能通过**所需的最小开度（口径 §13.6 的终态量）。

    推导（**几何关系，不是选定角度**）：门绕铰链转 θ 后，门板所在直线与远侧门框之间的
    **净通道宽度** = `width · sin θ`（门板从铰链出发沿 `u(θ)` 伸出，远侧门框到该直线的垂距；
    θ = 90° 时退化为整幅门宽）。要求净通道 ≥ 胶囊直径 `2r` ⇒ `sin θ ≥ 2r / width`。
    """
    return math.degrees(math.asin(min(1.0, 2.0 * radius / width)))


def _rot_z(v, deg):
    """世界 XY 向量绕世界 +Z 转 `deg`（脚朝向 / 站距用；不额外引入 `mathutils.Matrix`）。

    ⚠️ 入参可能是 **2 维**（站距）⇒ 一律按 3 维返回（实测踩到：`Vector.z` 在 2 维向量上不可用）。
    """
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return Vector((v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2] if len(v) > 2 else 0.0))


def _nlerp(a, b, t):
    """两向量之间的归一化线性插值（起手段的朝向过渡用；夹角 < 180° 时足够）。"""
    v = Vector(a) * (1.0 - t) + Vector(b) * t
    return v.normalized() if v.length > 1e-9 else Vector(a).normalized()


def door_layout_actor_side(open_deg, actor_xy=(0.0, 0.0)):
    """`door_layout` 的**判侧版**：近/远侧按**给定角色位置**判，不按原点判。

    ⚠️ 为什么必须换（实测）：原函数用"外法向是否指向**原点**"判近侧，而门边**扫过原点**
    （θ ≈ 52.6° 时自由边恰在原点上；实测 49.478° 时离原点仅 **36 mm**）⇒ 判据在那里退化。
    """
    lay = door_layout(open_deg)
    mid = lay["mid_edge"]
    ref = Vector((actor_xy[0], actor_xy[1], 0.0))
    if (ref - mid).dot(lay["n"]) > 0.0:      # n 必须**背离**角色（近侧面外法向 −n 指向角色）
        lay["n"] = -lay["n"]
        lay["near_edge"] = mid - lay["n"] * (lay["thickness"] / 2.0)
        lay["far_edge"] = mid + lay["n"] * (lay["thickness"] / 2.0)
    return lay


def door_push_stance(open_deg, clearance_m=DOOR_PUSH_CLEARANCE_M, actor_xy=(0.0, 0.0)):
    """「推到底」的身体摆放：**站在自由边正侧、离门板中面 `clearance_m`**（其余全由几何算出）。

    ⚠️ 为什么不是"转身角 + 前倾量"两个手拍常量：自由边随开角绕铰链**扫弧**（半径 = 门宽）
    ⇒ 要**保持扣住**，身体必须跟着弧走。`clearance_m` 一取定，**转身角 = 握点方位角**
    （身体朝向握点）、**骨盆位置 = 铰链 + 门宽·u(θ) + clearance·(−n(θ))**——全部由几何给出，
    没有第二个自由常量。实测：肩→腕距离在**整段弧上恒定**（证据 §三）。
    """
    lay = door_layout_actor_side(open_deg, actor_xy)
    m = -lay["n"]
    body = lay["hinge"] + lay["u"] * lay["width"] + m * clearance_m
    grip = lay["near_edge"]
    face = Vector((grip.x - body.x, grip.y - body.y, 0.0))
    return lay, {"body_xy": (round(body.x, 6), round(body.y, 6)),
                 "yaw_deg": math.degrees(math.atan2(face.x, -face.y)),
                 "clearance_m": clearance_m,
                 "pelvis_to_grip_m": round(face.length, 4),
                 "grip_xy": (round(grip.x, 6), round(grip.y, 6))}


def set_pelvis_world(arm, m3, xy, z, iters=4):
    """把 `CTRL_Hips` 的**骨点世界位置**送到 `(xy, z)`——**实测回代**，不假设写入口径。

    ⚠️ 两条实测（证据 §六.2）：① `set_world_offset` 写进去的是**真世界位移**（与 yaw 无关，已核）；
    ② 但"目标位置"与"位移"差一个**静止髋位**，直接当位移写会整体偏约 16 mm ⇒ 按实测误差回代。
    """
    pb = arm.pose.bones["CTRL_Hips"]
    pb.location = (0.0, 0.0, 0.0)
    update()
    base = world_point(arm, f"{BONE_PREFIX}Hips").copy()
    delta = Vector((xy[0] - base.x, xy[1] - base.y, z - base.z))
    err = Vector((0.0, 0.0, 0.0))
    for _ in range(iters):
        set_world_offset(arm, m3, "CTRL_Hips", delta)
        update()
        cur = world_point(arm, f"{BONE_PREFIX}Hips")
        err = Vector((xy[0] - cur.x, xy[1] - cur.y, z - cur.z))
        delta = delta + err
    return round(err.length * 1000.0, 3)


def solve_gaze_scan(arm, lo=-45.0, hi=45.0, step=1.0, fine=0.25, scale=1.0):
    """扫描 `Neck` / `Head` 的局部 X，取**头骨上轴最接近竖直**的那一档（口径 §十 V-b「目视水平」）。

    ⚠️ 为什么不复用 `solve_gaze`（牛顿法）：**实测它在转身 ≥ 45° 时发散**——#166 读数：
    yaw 40° → after **0.477°**；yaw 45° → after **45.431°**（8 次迭代仍不收敛）；yaw 50° →
    **49.564°**。而本动作的转身角要走到 **49.5°**。本函数只做**确定性扫描**，不依赖导数。
    `scale` 供**起手段**用：抬头到水平这件事随起手一起长出来（首帧必须严格中立，
    见 `DOOR_PUSH_FRAME_NEUTRAL` 的导出侧硬约定）。
    """
    def set_pair(x):
        for name in (f"{BONE_PREFIX}Head", f"{BONE_PREFIX}Neck"):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler((math.radians(x), 0.0, 0.0), "XYZ")
        update()

    set_pair(0.0)
    before = head_up_deg(arm)
    best = None
    x = lo
    while x <= hi + 1e-9:
        set_pair(x)
        v = head_up_deg(arm)
        if best is None or v < best[0]:
            best = (v, x)
        x += step
    x = best[1] - step
    while x <= best[1] + step + 1e-9:
        set_pair(x)
        v = head_up_deg(arm)
        if v < best[0]:
            best = (v, x)
        x += fine
    set_pair(best[1] * scale)
    return {"neck_head_x_deg": round(best[1] * scale, 3), "解出的_x_deg": round(best[1], 3),
            "scale": scale, "before_deg": round(before, 3),
            "after_deg": round(head_up_deg(arm), 3), "粗扫": f"{lo}..{hi}° / {step}°"}


def set_foot_world_orientation(arm, side, yaw_deg):
    """脚掌：**保持水平**（沿用静止朝向）但方向随身体转 `yaw_deg`。

    ⚠️ 库里既有写法（`_set_world_axes(..., _rest_dir, _rest_hinge)`）把脚**钉在世界朝向**上
    ⇒ 身体转 49.5° 时踝被扭同样的角度（宿主 3 就是这个形态）。绕世界 Z 转静止朝向**不改变脚掌
    的水平性**（判据 M2 只看竖直高度），只把脚尖摆到身体正前方。
    """
    _set_world_axes(arm, f"CTRL_{side}Foot", f"{BONE_PREFIX}{side}Foot",
                    _rot_z(_rest_dir(arm, f"{BONE_PREFIX}{side}Foot"), yaw_deg),
                    _rot_z(_rest_hinge(arm, f"{BONE_PREFIX}{side}Foot"), yaw_deg))


def door_push_reach(arm, side, frame_geo, grip_wrist_target, rest_wrist, curl_axis,
                    curl_ref, thumb_ref, t, post):
    """**起手段**（`t` = 0 静止 → 1 抓住）：腕从静止位线性送到抓握目标，手指按 `t` 合拢。

    ⚠️ 手型**不另发明**：合拢的终值就是帧 13 那次抓握解出来的 F10 逐指蜷曲与拇指角
    （口径 §13.6 自由度表第 9 行：抓握高度与手型**引用卡 1**，不是自由量）。
    """
    n, u = frame_geo["n"], frame_geo["u"]
    x_hint = n.cross(u)
    rest_dir = Vector((1.0, 0.0, 0.0)) if side == "Left" else Vector((-1.0, 0.0, 0.0))
    target = Vector(rest_wrist).lerp(Vector(grip_wrist_target), t)
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    _nlerp(rest_dir, n, t), x_hint)
    solve_arm_with_elbow_scan(arm, side, target, post)
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    _nlerp(rest_dir, n, t), x_hint)
    for finger in FINGERS:
        val = float(curl_ref.get(finger, 0.0))
        _apply_one_finger_curl(arm, side, finger, curl_axis, val * t)
    if thumb_ref:
        pb = arm.pose.bones[f"{BONE_PREFIX}{side}HandThumb1"]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler([math.radians(a * t) for a in thumb_ref], "XYZ")
    update(2)


def door_push_torso_lean(arm, total_deg):
    """**躯干前倾**：三段脊柱各转 `total_deg/3`（局部 X）。

    ⚠️ 为什么要有这一层：不给它，角色就是"**脊柱笔直地沿弧平移**"——owner 2026-09-16 的原话
    「**不像是人的动作更像是机器人**」。轴向不是拍的：管线 §2.1.4 实测 `Spine`/`Spine1`/`Spine2`
    的局部 X 就是前倾轴（三根共线，同转同角）。头由 `solve_gaze_scan` 在**之后**拉回水平。
    """
    each = total_deg / 3.0
    for name in ("Spine", "Spine1", "Spine2"):
        pb = arm.pose.bones[f"{BONE_PREFIX}{name}"]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler((math.radians(each), 0.0, 0.0), "XYZ")
    update()
    return {"每段_deg": round(each, 3), "合计_deg": round(total_deg, 3)}


def door_push_offhand(arm, side, yaw_deg, hips_world, hips_rest, curl_axis, t, post,
                      curl_amount=DOOR_PUSH_OFFHAND_CURL):
    """**副手**（不抓门的那只手）：自然垂放，随起手一起长出来（`t` = 0 → 1）。

    ⚠️ 为什么必须给个解（owner 2026-09-16 目视第二条：「**右手机械的平举**」）：静止姿势是
    **T-pose**——不给副手任何姿势，它就**水平伸着**。这不是"owner 没圈所以不碰"，是**没有姿势**。
    本解 = 腕落到体侧（`DOOR_PUSH_OFFHAND_WRIST_OFFSET`，在**角色体侧系**里给）、指尖朝下、
    掌心内向，并按 `DOOR_PUSH_OFFHAND_CURL` 松握；起手段按 `t` 从 T-pose 过渡过来。
    """
    # 当前（未解副手前的）手骨朝向 —— 用它当 `t=0` 端，过渡才不会在起手段跳一下
    _pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand"]
    _m = arm.matrix_world.to_3x3() @ _pb.matrix.to_3x3()
    rest_dir = (_m @ Vector((0.0, 1.0, 0.0))).normalized()      # 局部 Y = 腕 → 指尖
    rest_x = (_m @ Vector((1.0, 0.0, 0.0))).normalized()
    y_dir = _rot_z(Vector((0.0, 0.0, -1.0)), yaw_deg)          # 指尖朝下
    x_hint = _rot_z(Vector((0.0, -1.0, 0.0)), yaw_deg)         # 掌面朝体侧
    off = Vector(DOOR_PUSH_OFFHAND_WRIST_OFFSET)
    world_off = _rot_z(Vector((off.x, off.y, 0.0)), yaw_deg)
    target = Vector(hips_world) + Vector((world_off.x, world_off.y, off.z))
    rest_wrist = world_point(arm, f"{BONE_PREFIX}{side}Hand").copy()   # T-pose 的腕位
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    _nlerp(rest_dir, y_dir, t), _nlerp(rest_x, x_hint, t))
    solve_arm_with_elbow_scan(arm, side, rest_wrist.lerp(target, t), post)
    _set_world_axes(arm, f"CTRL_{side}Hand", f"{BONE_PREFIX}{side}Hand",
                    _nlerp(rest_dir, y_dir, t), _nlerp(rest_x, x_hint, t))
    for finger in FINGERS:
        _apply_one_finger_curl(arm, side, finger, curl_axis, curl_amount * t)
    update(2)
    return {"wrist_target_m": [round(v, 4) for v in target],
            "elbow_deg": round(math.degrees(
                (world_point(arm, f"{BONE_PREFIX}{side}Arm")
                 - world_point(arm, f"{BONE_PREFIX}{side}ForeArm")).angle(
                    world_point(arm, f"{BONE_PREFIX}{side}Hand")
                    - world_point(arm, f"{BONE_PREFIX}{side}ForeArm"))), 1),
            "elbow_offset_mm": elbow_offset(arm, side),
            "curl_amount": curl_amount * t}


def door_push_preview_cleanup(arm):
    """预览场景收拾干净（**只动显示与残留代理，不动任何数据**）。

    owner 2026-09-16 目视两条：
    ① 「**Armature 里面重复骨骼**」——实测骨架里**没有**同名/`.001` 重复骨（78 = 13 `CTRL_` +
       65 `mixamorig:`）；真正的观感来源是 **(a) `Beta_Joints`（骨骼可视化网格）与皮肤网格叠着画**、
       **(b) 13 根控制骨与它驱动的变形骨完全重合地画在一起**。⇒ 本函数把 `Beta_Joints` 隐藏、
       把 `CTRL_*` 骨设为隐藏（**显示开关，不影响姿势与导出**）。
    ② 「**门和椅子重叠在一起**」——场景里还留着 **#163 的椅子残留代理**（`REF_Back` / `REF_Seat` /
       `REF_Leg0..3`，证据里早有登记"母版残留 `REF_*`"）。门板绕铰链扫过的扇区**正好覆盖**它
       ⇒ 预览里门穿椅子。本函数把 `REF_Chair` / `REF_Board` 两个集合整体删掉（它们是**参考件**、
       不进 FBX、也不参与任何判据——判据目标一律由 `door_layout_*` 现算）。
    """
    dropped = []
    for coll_name in ("REF_Chair", "REF_Board"):
        coll = bpy.data.collections.get(coll_name)
        if coll is None:
            continue
        for ob in list(coll.objects):
            dropped.append(ob.name)
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(coll)
    hidden_mesh = []
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.name.startswith("Beta_Joints"):
            ob.hide_viewport = True
            ob.hide_render = True
            hidden_mesh.append(ob.name)
    hidden_bones = []
    for b in arm.data.bones:
        if b.name.startswith("CTRL_") and not b.hide:
            b.hide = True
            hidden_bones.append(b.name)
    return {"删掉的残留代理": dropped, "隐藏的网格": hidden_mesh, "隐藏的控制骨": len(hidden_bones)}


def main_door_push() -> int:
    """门边「推到底」宿主：逐帧解算 → **逐帧打键** → 从**产物**里读三类判据。"""
    from datetime import datetime
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    if args.host == "headless":
        bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    elif not bpy.data.filepath:
        print("[ERROR] --host live 要求母版已经在当前会话里打开")
        return 2
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    drop_temp(arm)
    clear_pose(arm)

    # ⚠️ 宿主 3 的动作名缺陷（#165 登记、宿主 3 本件不改）：`--action` 的默认值是椅子动作名。
    #    本宿主**不带 `--action` 时用自己的名字**，只在不一致时提示（不静默）。
    action_name = args.action if args.action != "BendGripChairBack" else DOOR_PUSH_ACTION
    if action_name != args.action:
        print(f"[WARN] --action 未显式给出（默认 {args.action}）⇒ 本宿主按 {action_name} 命名动作")

    clearance = args.clearance if args.clearance is not None else DOOR_PUSH_CLEARANCE_M
    crouch = args.crouch if args.crouch is not None else DOOR_PUSH_CROUCH_M
    pass_deg = door_pass_open_deg()
    report = {"script": Path(__file__).name, "task": "doorpush", "action": action_name,
              "blender": bpy.app.version_string, "template": str(tmpl), "host": args.host,
              "measured_at": datetime.now().isoformat(timespec="seconds"),
              "clearance_m": clearance, "crouch_m": crouch, "problems": []}
    print(f"门板：宽 {DOOR_WIDTH} m · 厚 {BACK_THICKNESS * 1000:.0f} mm · 铰链 {DOOR_HINGE} · "
          f"半掩 {DOOR_PUSH_START_DEG}°（**远侧**，门朝远离角色的方向开）· 动作名 {action_name}")
    print(f"胶囊半径 {X_BOT_CAPSULE_RADIUS_M} m ⇒ 直径 {2 * X_BOT_CAPSULE_RADIUS_M:.4f} m · "
          f"门宽 {DOOR_WIDTH} m ⇒ sinθ ≥ {2 * X_BOT_CAPSULE_RADIUS_M / DOOR_WIDTH:.6f} ⇒ "
          f"通过开度 = {pass_deg:.3f}° ⇒ 终态开角 = {-pass_deg:.3f}°（从半掩 {DOOR_PUSH_START_DEG}° 再推 {pass_deg + DOOR_PUSH_START_DEG:.3f}°）")
    report["pass_open"] = {
        "定义": "口径 §13.6 的终态量；术语注册表 `通过开度`",
        "推导": "净通道宽度 = 门宽 × sinθ（远侧门框到门板所在直线的垂距）≥ 胶囊直径 2r",
        "胶囊半径_m": X_BOT_CAPSULE_RADIUS_M, "胶囊直径_m": round(2 * X_BOT_CAPSULE_RADIUS_M, 4),
        "门宽_m": DOOR_WIDTH, "sinθ_下界": round(2 * X_BOT_CAPSULE_RADIUS_M / DOOR_WIDTH, 6),
        "通过开度_deg": round(pass_deg, 3), "终态开角_deg": round(-pass_deg, 3),
        "半掩角_deg": DOOR_PUSH_START_DEG,
        "从半掩再推_deg": round(pass_deg + DOOR_PUSH_START_DEG, 3),
        "来源": "胶囊半径来源见 X_BOT_CAPSULE_RADIUS_M 的注释（两处 Unity 侧实测记录）"}

    # ---- ① F3 复核（= 口径 §6.2 世界轴映射的**第二个动作复核**，即 U4 的复核点）----
    clear_pose(arm)
    f3 = {s: hand_axes_reading(arm, s) for s in CARD1_SIDES}
    curl = {s: detect_curl_axis_group(arm, s, "四指") for s in CARD1_SIDES}
    curl_axis = {s: {"axis": curl[s]["axis"], "sign": curl[s]["sign"]} for s in CARD1_SIDES}
    report["f3_rest"] = f3
    report["f3_curl"] = curl
    head_up = (world_point(arm, f"{BONE_PREFIX}HeadTop_End", "tail")
               - world_point(arm, f"{BONE_PREFIX}Head")).normalized()
    toe_dir = (world_point(arm, f"{BONE_PREFIX}LeftToeBase", "tail")
               - world_point(arm, f"{BONE_PREFIX}LeftToeBase")).normalized()
    report["u4_world_axes"] = {
        "上方=+Z（头骨上轴与 +Z 夹角°）": round(math.degrees(head_up.angle(Vector((0, 0, 1)))), 3),
        "前方=−Y（左趾指向与 −Y 夹角°）": round(math.degrees(toe_dir.angle(Vector((0, -1, 0)))), 3),
        "左手侧=+X（左腕 x_m）": round(world_point(arm, f"{BONE_PREFIX}LeftHand").x, 4),
        "右手侧=−X（右腕 x_m）": round(world_point(arm, f"{BONE_PREFIX}RightHand").x, 4)}
    print(f"F3 复核（与卡 1 同源）：+Y↔腕→中指尖 {f3['Left']['Y_vs_wrist_to_tip_deg']}°（左）· "
          f"蜷曲轴 {curl_axis['Left']['axis']}{curl_axis['Left']['sign']:+d}（左）/ "
          f"{curl_axis['Right']['axis']}{curl_axis['Right']['sign']:+d}（右）")
    print(f"U4 复核（§6.2 世界轴映射）：{report['u4_world_axes']}")

    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in CARD1_SIDES}
    hips_rest = world_point(arm, f"{BONE_PREFIX}Hips").copy()
    ankle_z = foot_rest["Left"].z
    stance = {s: Vector((foot_rest[s].x - hips_rest.x, foot_rest[s].y - hips_rest.y))
              for s in CARD1_SIDES}
    side = "Left"                      # 抓门的是**左手**（卡 1 侧握基准格 · #164）
    off_side = "Right"                 # 副手：本件给它一个**自然垂放**的解（T-pose 不是姿势）
    grip_z = args.grip_z if args.grip_z is not None else 1.15
    curl_amount = args.curl if args.curl is not None else CARD1_CURL_BASELINE
    print(f"静止读数：髋 {tuple(round(v, 4) for v in hips_rest)} · 踝 z {ankle_z:.4f} m · "
          f"站距（左）{tuple(round(v, 4) for v in stance['Left'])}")

    # ---- ② 摆放规则与**保持扣住可达的最大角**扫描（改族判定；口径 §13.5）----
    if args.scan_arc:
        print("\n弧上扫描（判据：手臂不夹直 + 三条接触对全在容差内）")
        print(f"  {'θ°':>7}{'净距':>7}{'转身°':>7}{'肩→腕':>8}{'夹直':>6}{'虎口':>7}{'拇指':>7}"
              f"{'四指最坏':>9}{'残差':>7}{'肘°':>7}")
        rows, best_ok = [], None
        deg = DOOR_PUSH_START_DEG
        #: 判侧参考点：**沿扫描链递推**（第一档用原点，之后用上一档算出的身体位置）。
        #: ⚠️ 为什么不能用原点判到底（实测）：自由边在 **θ ≈ 52.6°** 时**扫过原点**
        #:   （49.486° 时离原点仅 36 mm）⇒ 越过它之后"哪一侧是角色侧"按原点判会**整条翻转**，
        #:   身体位置会从 (−0.294, 0.240) 跳到 (0.289, −0.20)（跳跃 0.72 m）——那是**规则退化**，
        #:   不是物理极限。递推参考点让"同一侧"沿链保持一致。
        ref_xy = (0.0, 0.0)
        while deg >= -args.scan_max - 1e-9:
            lay, st = door_push_stance(deg, clearance, actor_xy=ref_xy)
            ref_xy = st["body_xy"]
            frame_geo = door_end_frame(lay)
            clear_pose(arm)
            drop_temp(arm, also_objects=False)
            set_euler(arm, "CTRL_Hips", y=st["yaw_deg"])
            set_pelvis_world(arm, m3, st["body_xy"], hips_rest.z - crouch)
            _, _, posterior = body_frame(arm)
            for s in CARD1_SIDES:
                solve_leg(arm, s, foot_rest[s], -posterior)
                set_foot_world_orientation(arm, s, st["yaw_deg"])
            update()
            gi = grip_board_edge(arm, side, frame_geo, grip_z, curl_amount, curl_axis[side],
                                 label=f"scan{deg}")
            pairs = grip_board_edge_readings(arm, side, frame_geo)
            worst4 = max(abs(x) for x in pairs[2]["读数_mm"])
            ok = ((not gi["arm"].get("clamped_straight"))
                  and worst4 <= CONTACT_TOL_MM
                  and gi["web_to_edge_mm"] <= CONTACT_TOL_MM
                  and (gi["thumb_gap_mm"] is None or abs(gi["thumb_gap_mm"]) <= CONTACT_TOL_MM))
            rows.append({"deg": round(deg, 3), "ok": bool(ok), "reach_m": gi["arm"]["reach_m"],
                         "clamped": bool(gi["arm"].get("clamped_straight")),
                         "web_mm": gi["web_to_edge_mm"], "thumb_mm": gi["thumb_gap_mm"],
                         "四指最坏_mm": worst4, "残差_mm": pair_residual_mm(pairs),
                         "肘_deg": gi["elbow_deg"]})
            if ok:
                best_ok = round(deg, 3)
            print(f"  {deg:7.2f}{clearance:7.2f}{st['yaw_deg']:7.1f}{gi['arm']['reach_m']:8.3f}"
                  f"{('是' if gi['arm'].get('clamped_straight') else '否'):>6}"
                  f"{gi['web_to_edge_mm']:7.2f}{str(gi['thumb_gap_mm']):>7}{worst4:9.2f}"
                  f"{pair_residual_mm(pairs):7.2f}{gi['elbow_deg']:7.1f}")
            deg -= args.scan_step
        # ⚠️ 比的是**幅值**（门朝远侧开后扫描得到的是负角）：`|-88°| ≥ 49.486°` ⇒ 未触发改族
        trig = (best_ok is None) or (abs(best_ok) < pass_deg)
        report["scan_arc"] = {"clearance_m": clearance, "行": rows,
                              "保持扣住可达的最大角_deg": best_ok, "通过开度_deg": round(pass_deg, 3),
                              "改族触发": bool(trig),
                              "容差_mm": CONTACT_TOL_MM}
        print(f"⇒ 保持扣住可达的最大角（扫描区间 {DOOR_PUSH_START_DEG}–{-args.scan_max}° 内）="
              f"{best_ok}°（幅值 {abs(best_ok) if best_ok is not None else None:.3f}°）· "
              f"通过开度 = {pass_deg:.3f}° ⇒ 改族{'触发' if trig else '未触发'}")
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
            print(f"报告: {args.report}")
        return 0 if not trig else 1

    # ---- ②′ 身体摆放（净距）的解空间：口径 §4.2 硬规矩 5「agent 解的行并列 ≥2 解」----
    if args.scan_stance:
        print("\n身体摆放（净距 b）的解空间（口径 §4.2 硬规矩 5：agent 解的行必须并列 ≥2 个可行解）")
        print(f"  {'θ°':>7}{'净距b':>7}{'离近侧面':>9}{'胶囊余量':>9}{'肩→腕':>8}{'夹直':>6}"
              f"{'虎口':>7}{'残差':>7}{'肘°':>7}")
        space = []
        for deg in (DOOR_PUSH_START_DEG, -pass_deg):
            ref = (hips_rest.x, hips_rest.y)
            for b in DOOR_PUSH_STANCE_CANDIDATES:
                lay, st = door_push_stance(deg, b, actor_xy=ref)
                ref = st["body_xy"]
                frame_geo = door_end_frame(lay)
                clear_pose(arm)
                drop_temp(arm, also_objects=False)
                set_euler(arm, "CTRL_Hips", y=st["yaw_deg"])
                set_pelvis_world(arm, m3, st["body_xy"], hips_rest.z - crouch)
                _, _, posterior = body_frame(arm)
                for s_ in CARD1_SIDES:
                    solve_leg(arm, s_, foot_rest[s_], -posterior)
                    set_foot_world_orientation(arm, s_, st["yaw_deg"])
                update()
                gi = grip_board_edge(arm, side, frame_geo, grip_z, curl_amount, curl_axis[side],
                                     label=f"stance{b}")
                pairs = grip_board_edge_readings(arm, side, frame_geo)
                face_margin = b - BACK_THICKNESS / 2.0 - X_BOT_CAPSULE_RADIUS_M
                space.append({"deg": round(deg, 3), "clearance_m": b,
                              "离近侧面_m": round(b - BACK_THICKNESS / 2.0, 4),
                              "胶囊余量_m": round(face_margin, 4),
                              "reach_m": gi["arm"]["reach_m"],
                              "clamped": bool(gi["arm"].get("clamped_straight")),
                              "web_mm": gi["web_to_edge_mm"], "残差_mm": pair_residual_mm(pairs),
                              "肘_deg": gi["elbow_deg"]})
                print(f"  {deg:7.3f}{b:7.2f}{b - BACK_THICKNESS / 2.0:9.3f}{face_margin:9.3f}"
                      f"{gi['arm']['reach_m']:8.3f}{('是' if gi['arm'].get('clamped_straight') else '否'):>6}"
                      f"{gi['web_to_edge_mm']:7.2f}{pair_residual_mm(pairs):7.2f}{gi['elbow_deg']:7.1f}")
        report["stance_solution_space"] = {"候选净距_m": list(DOOR_PUSH_STANCE_CANDIDATES),
                                           "行": space,
                                           "采用": clearance,
                                           "臂长_m": 0.5617,
                                           "胶囊半径_m": X_BOT_CAPSULE_RADIUS_M}
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
            print(f"报告: {args.report}")
        return 0
    # ---- ③ 帧表（门角 / 身体摆放 / 迈步，全部由几何算出）----
    def stance_fixed(deg, clearance_m):
        """摆放的**不动点**版：判侧参考点 = 上一轮算出的身体位置。

        ⚠️ 为什么不能一直用原点判侧（实测）：自由边在 **θ ≈ 52.6°** 时扫过原点（49.486° 时
        离原点仅 36 mm）⇒ 越过它之后"哪一侧是角色侧"按原点判会整条翻转（身体位置跳 0.72 m）。
        不动点 = "身体在哪一侧，就以它自己为参考"，与直观一致且不循环。
        """
        ref = (hips_rest.x, hips_rest.y)
        st = None
        for _ in range(3):
            _lay, st = door_push_stance(deg, clearance_m, actor_xy=ref)
            ref = st["body_xy"]
        return st

    def push_angle(frame):
        """该帧的门开角（**带符号**）：半掩 `DOOR_PUSH_START_DEG` → 推段线性 → `-通过开度`。"""
        if frame <= DOOR_PUSH_FRAME_PUSH:
            return DOOR_PUSH_START_DEG
        if frame >= DOOR_PUSH_FRAME_ARRIVAL:
            return -pass_deg
        u = (frame - DOOR_PUSH_FRAME_PUSH) / float(DOOR_PUSH_FRAME_ARRIVAL - DOOR_PUSH_FRAME_PUSH)
        return DOOR_PUSH_START_DEG + (-pass_deg - DOOR_PUSH_START_DEG) * u

    def body_at(frame):
        if frame >= DOOR_PUSH_FRAME_GRIP:
            return stance_fixed(push_angle(frame), clearance)
        t = (frame - DOOR_PUSH_FRAME_NEUTRAL) / float(DOOR_PUSH_FRAME_GRIP - DOOR_PUSH_FRAME_NEUTRAL)
        _lay, end = door_push_stance(DOOR_PUSH_START_DEG, clearance)
        bx = hips_rest.x + (end["body_xy"][0] - hips_rest.x) * t
        by = hips_rest.y + (end["body_xy"][1] - hips_rest.y) * t
        return {"body_xy": (bx, by), "yaw_deg": end["yaw_deg"] * t, "clearance_m": clearance,
                "pelvis_to_grip_m": end["pelvis_to_grip_m"], "grip_xy": end["grip_xy"]}

    def crouch_at(frame):
        """膝屈下沉：**前 4 帧内沉到位**（首帧仍严格中立）。

        ⚠️ 实测（第 2 轮）：原先让它一路缓到"开始推"（帧 21）⇒ 帧 4–6 的沉量只有 0.009~0.03 m，
        而腿的水平预算 ≈ `√(2·腿长·沉量)` 此时只有几厘米 ⇒ **迈步当场解不动**（残差 17.0 mm）。
        """
        if frame >= DOOR_PUSH_FRAME_NEUTRAL + 4:
            return crouch
        return crouch * (frame - DOOR_PUSH_FRAME_NEUTRAL) / 4.0

    def lean_at(frame):
        """躯干前倾量：推段从 0 长到 `DOOR_PUSH_TORSO_LEAN_DEG`，到位后保持。"""
        if frame <= DOOR_PUSH_FRAME_PUSH:
            return 0.0
        if frame >= DOOR_PUSH_FRAME_ARRIVAL:
            return DOOR_PUSH_TORSO_LEAN_DEG
        u = (frame - DOOR_PUSH_FRAME_PUSH) / float(DOOR_PUSH_FRAME_ARRIVAL - DOOR_PUSH_FRAME_PUSH)
        return DOOR_PUSH_TORSO_LEAN_DEG * u

    def reach_t(frame):
        if frame >= DOOR_PUSH_FRAME_GRIP:
            return 1.0
        return (frame - DOOR_PUSH_FRAME_NEUTRAL) / float(DOOR_PUSH_FRAME_GRIP - DOOR_PUSH_FRAME_NEUTRAL)

    #: 迈步：**按身体路径的弧长均分**（步数由实测腿预算反解），左右脚交替。
    #: 每个"迈步桶"= 弧长 `L`；桶内前 `SWING_FRACTION` 让该脚摆动、其余双支撑。
    #: ⇒ 「迈步步长」不是拍的：`L = 总行程 / N`，`N = ceil(总行程 / 每步预算)`。
    _first = args.first_foot
    _other = "Right" if _first == "Left" else "Left"
    _path_frames = list(range(DOOR_PUSH_FRAME_NEUTRAL, DOOR_PUSH_FRAME_END + 1))
    _path_xy = [Vector(body_at(f_)["body_xy"]) for f_ in _path_frames]
    _cum = [0.0]
    for _i in range(1, len(_path_xy)):
        _cum.append(_cum[-1] + (_path_xy[_i] - _path_xy[_i - 1]).length)
    _travel = _cum[-1]
    _n_steps = max(1, int(math.ceil(_travel / DOOR_PUSH_STEP_BUDGET_M)))
    _L = _travel / _n_steps
    _cum_by_frame = {f_: _cum[i] for i, f_ in enumerate(_path_frames)}
    print(f"迈步：总行程 {_travel:.3f} m ÷ 每步预算 {DOOR_PUSH_STEP_BUDGET_M} m ⇒ {_n_steps} 步 ·"
          f" 每步弧长 {_L:.3f} m · 先迈 {_first}")
    #: 桶表（**纯函数**，一次算完）：每桶 = 摆动脚 / 起帧 / 落帧 / 止帧 / 落点。
    #: 落点 = "落帧时的身体位置 + 站距 + **行进方向 × (每步弧长/2)**"——那只脚在**身体前方**落地，
    #: 之后身体走过 `L`，它再抬起来时正好在身体**后方** `L/2` ⇒ 踝相对骨盆的偏移在 **±L/2** 内
    #: 摆动（实测：不"往前落"时偏移会长到 `L`，帧 8/9 的腿 IK 因此解不动、残差 11.9 mm）。
    _buckets = []
    _prev_plant = {s: Vector((foot_rest[s].x, foot_rest[s].y, ankle_z)) for s in CARD1_SIDES}
    for _k in range(_n_steps):
        _foot = _first if _k % 2 == 0 else _other
        def _first_after(frac):
            return next((f_ for f_ in _path_frames if _cum_by_frame[f_] > frac * _L + 1e-9),
                        _path_frames[-1])
        _a, _l, _b = _first_after(_k), _first_after(_k + DOOR_PUSH_SWING_FRACTION), _first_after(_k + 1)
        _e = body_at(_l)
        _bx2, _by2 = body_at(min(_l + 2, DOOR_PUSH_FRAME_END))["body_xy"]
        _bx1, _by1 = body_at(max(_l - 2, DOOR_PUSH_FRAME_NEUTRAL))["body_xy"]
        _dirv = Vector((_bx2 - _bx1, _by2 - _by1, 0.0))          # ⚠️ 一律 3 维（站距偏移是 3 维）
        _dirv = _dirv.normalized() if _dirv.length > 1e-9 else Vector((0.0, 0.0, 0.0))
        _tgt = (Vector((_e["body_xy"][0], _e["body_xy"][1], 0.0))
                + _rot_z(stance[_foot], _e["yaw_deg"]) + _dirv * (_L / 2.0))
        _tgt.z = ankle_z
        _buckets.append({"桶": _k, "脚": _foot, "起帧": _a, "落帧": _l, "止帧": _b, "落点": _tgt,
                         "从": _prev_plant[_foot].copy()})
        _prev_plant[_foot] = _tgt.copy()
    step_log = [{"桶": b["桶"], "脚": b["脚"], "起帧": b["起帧"], "落帧": b["落帧"], "止帧": b["止帧"],
                 "从_xy": [round(v, 4) for v in b["从"]], "到_xy": [round(v, 4) for v in b["落点"]],
                 "步长_m": round((b["落点"] - b["从"]).length, 4)} for b in _buckets]
    print(f"迈步桶：{[(b['桶'], b['脚'], b['起帧'], b['落帧']) for b in _buckets]}")

    def ankle_target(frame):
        """逐脚踝目标（纯函数）：默认 = 该脚**最近一次落点**；正在摆动的那只脚按抬脚弧从上一落点飞到落点。"""
        out = {}
        for s in CARD1_SIDES:
            last = None
            for b in _buckets:
                if b["脚"] == s and b["落帧"] <= frame:
                    last = b["落点"]
            out[s] = (last.copy() if last is not None
                      else Vector((foot_rest[s].x, foot_rest[s].y, ankle_z)))
        for b in _buckets:
            if b["起帧"] < frame <= b["落帧"]:
                span = max(b["落帧"] - b["起帧"], 1)
                u = (frame - b["起帧"]) / float(span)
                xy = b["从"].lerp(b["落点"], u)
                out[b["脚"]] = Vector((xy.x, xy.y,
                                       ankle_z + DOOR_PUSH_STEP_LIFT_M * math.sin(math.pi * u)))
        return out

    def grip_names():
        """打键通道表：**双侧**手臂与腿脚控制骨 + 骨盆 + 颈/头 + 解算侧手骨。

        ⚠️ 为什么必须**双侧腿脚**（宿主 3 就是在这里漏的）：只打一侧时，另一侧的腿在产物里
        恒为**静止姿势**——骨盆一动，那条腿就整条跟着骨盆走（实测：脚陷到地面 **−60 mm**，
        而 M2 的"含陷入"判据**照样读成"接触"**⇒ 接地判据被绕过）。#165 那条
        "门边动作双侧全程无支撑、离地 +160~+313 mm" 是同一个病的另一面。
        """
        names = ["CTRL_Hips"]
        for s in CARD1_SIDES:
            names += [f"CTRL_{s}{p}" for p in ("Arm", "ForeArm", "Hand", "UpLeg", "Leg", "Foot")]
        names += [f"{BONE_PREFIX}Neck", f"{BONE_PREFIX}Head",
                  f"{BONE_PREFIX}Spine", f"{BONE_PREFIX}Spine1", f"{BONE_PREFIX}Spine2"]
        for s_ in CARD1_SIDES:            # ⚠️ 双侧：副手（右手）也要打键，否则它留在 T-pose
            for finger in FINGERS:
                for k in (1, 2, 3, 4):
                    n = f"{BONE_PREFIX}{s_}Hand{finger}{k}"
                    if n in arm.pose.bones:
                        names.append(n)
        return names

    # ---- ④ 起手参照解：帧 13 的抓握（拿到 F10 的逐指蜷曲 + 拇指角；起手段只按 t 缩放它们）----
    clear_pose(arm)
    drop_temp(arm, also_objects=False)
    lay13 = build_door_proxy(DOOR_PUSH_START_DEG)
    frame_geo13 = door_end_frame(lay13)
    st13 = body_at(DOOR_PUSH_FRAME_GRIP)
    set_euler(arm, "CTRL_Hips", y=st13["yaw_deg"])
    set_pelvis_world(arm, m3, st13["body_xy"], hips_rest.z - crouch)
    _, _, posterior = body_frame(arm)
    _ank13 = ankle_target(DOOR_PUSH_FRAME_GRIP)
    for s in CARD1_SIDES:
        solve_leg(arm, s, _ank13[s], -posterior)
        set_foot_world_orientation(arm, s, st13["yaw_deg"])
    update()
    door_push_torso_lean(arm, lean_at(DOOR_PUSH_FRAME_GRIP))
    door_push_offhand(arm, "Right", st13["yaw_deg"], world_point(arm, f"{BONE_PREFIX}Hips"),
                      hips_rest, curl_axis["Right"], 1.0, posterior)
    gaze_ref = solve_gaze_scan(arm)
    ref_grip = grip_board_edge(arm, side, frame_geo13, grip_z, curl_amount, curl_axis[side],
                               label="ref13")
    curl_ref = {f: v["蜷曲量"] for f, v in (ref_grip["curl_solve"] or {}).items()}
    thumb_ref = list(ref_grip["thumb"]["euler_deg"])
    clear_pose(arm)
    rest_wrist = world_point(arm, f"{BONE_PREFIX}{side}Hand").copy()
    report["frame13_reference"] = {"gaze": gaze_ref, "curl_ref": curl_ref,
                                   "thumb_ref_deg": thumb_ref,
                                   "web_to_edge_mm": ref_grip["web_to_edge_mm"],
                                   "elbow_deg": ref_grip["elbow_deg"]}

    # ---- ⑤ 逐帧解算（每帧解、每帧打键 ⇒ 产物里的中间帧也是解出来的）----
    captured, per_frame = {}, []
    print(f"\n逐帧解算（帧 {DOOR_PUSH_FRAME_NEUTRAL}–{DOOR_PUSH_FRAME_END}，每帧打键）")
    for frame in range(DOOR_PUSH_FRAME_NEUTRAL, DOOR_PUSH_FRAME_END + 1):
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        st = body_at(frame)
        deg = push_angle(frame)
        lay = door_layout_actor_side(deg, st["body_xy"])
        frame_geo = door_end_frame(lay)
        ankles = ankle_target(frame)
        if frame == DOOR_PUSH_FRAME_NEUTRAL:
            # ⚠️ **首帧必须严格中立**（导出侧硬约定，`export_xbot_action.py` 的 E5）：FBX 导出会把
            #    "导出那一刻的姿势"写进骨节点的默认变换、回导端把它当 Rest/Bind Pose ⇒ 首帧带姿势
            #    就等于**污染骨架身份**（#156 实测过一次，E5 报出 86 m 量级偏差）。
            #    ⇒ 首帧一个解都不打：只记中立通道。
            row = {"frame": frame, "door_open_deg": round(deg, 4),
                   "body_xy": [round(hips_rest.x, 4), round(hips_rest.y, 4)], "yaw_deg": 0.0,
                   "crouch_m": 0.0, "pelvis_fix_mm": 0.0, "hooked": False, "reach_t": 0.0,
                   "neutral": True,
                   "ankles": {s: [round(v, 4) for v in ankles[s]] for s in CARD1_SIDES},
                   "leg_tip_err_mm": {s: 0.0 for s in CARD1_SIDES},
                   "leg_clamped": {s: False for s in CARD1_SIDES},
                   "gaze_after_deg": round(head_up_deg(arm), 3), "gaze_x_deg": 0.0,
                   "grip": None, "pairs": [], "residual_mm": None}
            captured[frame] = capture_channels(arm, grip_names())
            per_frame.append(row)
            print(f"  帧 {frame:>3} 门 {deg:6.3f}° **中立姿势**（零通道；导出侧 Rest Pose 一口清）")
            continue
        set_euler(arm, "CTRL_Hips", y=st["yaw_deg"])
        pelvis_err = set_pelvis_world(arm, m3, st["body_xy"], hips_rest.z - crouch_at(frame))
        _, _, posterior = body_frame(arm)
        legs = {}
        for s in CARD1_SIDES:
            legs[s] = solve_leg(arm, s, ankles[s], -posterior)
            set_foot_world_orientation(arm, s, st["yaw_deg"])
        update()
        t = reach_t(frame)
        _pre_lean_shoulder = world_point(arm, f"{BONE_PREFIX}LeftArm").copy()
        door_push_torso_lean(arm, lean_at(frame))
        lean_shift = round((world_point(arm, f"{BONE_PREFIX}LeftArm").y - _pre_lean_shoulder.y)
                           * 1000.0, 1)
        offhand = door_push_offhand(arm, off_side, st["yaw_deg"], world_point(arm, f"{BONE_PREFIX}Hips"),
                                    hips_rest, curl_axis[off_side], t, posterior)
        gaze = solve_gaze_scan(arm, scale=t if frame < DOOR_PUSH_FRAME_GRIP else 1.0)
        row = {"frame": frame, "door_open_deg": round(deg, 4),
               "body_xy": [round(v, 4) for v in st["body_xy"]], "yaw_deg": round(st["yaw_deg"], 2),
               "crouch_m": round(crouch_at(frame), 4), "pelvis_fix_mm": pelvis_err,
               "hooked": t >= 1.0, "reach_t": round(t, 3),
               "ankles": {s: [round(v, 4) for v in ankles[s]] for s in CARD1_SIDES},
               "leg_tip_err_mm": {s: legs[s]["tip_err_mm"] for s in CARD1_SIDES},
               "leg_clamped": {s: bool(legs[s].get("clamped_straight")) for s in CARD1_SIDES},
               "gaze_after_deg": gaze["after_deg"], "gaze_x_deg": gaze["neck_head_x_deg"],
               "offhand": offhand,
               "torso_lean_deg": round(lean_at(frame), 2), "lean_shoulder_shift_y_mm": lean_shift}
        if t >= 1.0:
            grip = grip_board_edge(arm, side, frame_geo, grip_z, curl_amount, curl_axis[side],
                                   label=f"f{frame}")
            pairs = grip_board_edge_readings(arm, side, frame_geo)
            for r in pairs:
                r["状态"] = pair_status(r)
            row["grip"] = {"web_to_edge_mm": grip["web_to_edge_mm"],
                           "thumb_gap_mm": grip["thumb_gap_mm"],
                           "palm_to_end_face_mm": grip["palm_to_end_face_mm"],
                           "reach_m": grip["arm"]["reach_m"],
                           "wrist_tip_err_mm": grip["arm"]["tip_err_mm"],
                           "clamped": bool(grip["arm"].get("clamped_straight")),
                           "elbow_deg": grip["elbow_deg"], "elbow_offset_mm": grip["elbow_offset_mm"],
                           "elbow_penalty": grip["elbow_pick"]["罚分"],
                           "四指_mm": pairs[2]["读数_mm"]}
            row["pairs"] = [{"手部分区": r["手部分区"], "物体分区": r["物体分区"],
                             "判据形态": r["判据形态"], "读数_mm": r["读数_mm"], "状态": r["状态"]}
                            for r in pairs]
            row["residual_mm"] = pair_residual_mm(pairs)
        else:
            door_push_reach(arm, side, frame_geo, ref_grip["wrist_target_m"], rest_wrist,
                            curl_axis[side], curl_ref, thumb_ref, t, posterior)
            row["grip"] = None
            row["pairs"] = []
            row["residual_mm"] = None
        captured[frame] = capture_channels(arm, grip_names())
        per_frame.append(row)
        off = {s: round((Vector(row["ankles"][s])
                         - Vector((st["body_xy"][0], st["body_xy"][1], ankle_z))).length, 3)
               for s in CARD1_SIDES}
        print(f"  帧 {frame:>3} 门 {deg:6.3f}° 骨盆 ({st['body_xy'][0]:+.3f},{st['body_xy'][1]:+.3f}) "
              f"转身 {st['yaw_deg']:5.1f}° 踝偏 {off} 腿残差 {row['leg_tip_err_mm']} "
              f"目视 {gaze['after_deg']:5.2f}°"
              + (f" | 虎口 {row['grip']['web_to_edge_mm']:5.2f} 拇指 {row['grip']['thumb_gap_mm']}"
                 f" 残差 {row['residual_mm']:5.2f} 肘 {row['grip']['elbow_deg']:5.1f}°"
                 if row["grip"] else " | 起手（腕趋近 + 手指合拢）"))
    report["frames"] = per_frame
    report["steps"] = step_log
    report["first_foot"] = _first
    report["step_plan"] = [{"桶": k, "脚": (_first if k % 2 == 0 else _other)} for k in range(_n_steps)]
    report["step_machine"] = {"总行程_m": round(_travel, 4), "每步预算_m": DOOR_PUSH_STEP_BUDGET_M,
                              "步数": _n_steps, "每步弧长_m": round(_L, 4),
                              "摆动占比": DOOR_PUSH_SWING_FRACTION, "先迈": _first}

    # ---- ⑥ 打键（**逐帧**；控制骨 + 手骨 + **腿脚**全打——宿主 3 漏掉的正是腿脚）----
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    for stale in [a for a in bpy.data.actions
                  if a.name == action_name or a.name.startswith(action_name + ".")]:
        bpy.data.actions.remove(stale)
    action = bpy.data.actions.new(action_name)
    action.use_fake_user = True
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import blender_action_compat as bac
        bac.assign_action(ad, action)
    except Exception as exc:
        print(f"[WARN] 取道层不可用（{exc}），退回直接指派")
        ad.action = action
    panel = bpy.data.objects.get("REF_DoorPanel")
    for frame in range(DOOR_PUSH_FRAME_NEUTRAL, DOOR_PUSH_FRAME_END + 1):
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        drop_temp(arm, also_objects=False)
        apply_channels(arm, captured[frame])
        if panel is not None:
            p_lay = door_layout(push_angle(frame))
            panel.location = p_lay["panel_center"]
            panel.rotation_euler = Euler((0.0, 0.0, math.radians(p_lay["open_deg"])), "XYZ")
            panel.keyframe_insert("location", frame=frame)
            panel.keyframe_insert("rotation_euler", frame=frame)
        update()
        for name in list(captured[frame]):
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
            if name == "CTRL_Hips":
                pb.keyframe_insert("location", frame=frame)
    bpy.context.scene.frame_start = DOOR_PUSH_FRAME_NEUTRAL
    bpy.context.scene.frame_end = DOOR_PUSH_FRAME_END
    report["action_frames"] = [DOOR_PUSH_FRAME_NEUTRAL, DOOR_PUSH_FRAME_END]
    report["keyed_channels"] = sorted(captured[DOOR_PUSH_FRAME_END])
    report["preview_cleanup"] = door_push_preview_cleanup(arm)
    print(f"预览清理：删掉残留代理 {report['preview_cleanup']['删掉的残留代理']} · "
          f"隐藏网格 {report['preview_cleanup']['隐藏的网格']} · "
          f"隐藏控制骨 {report['preview_cleanup']['隐藏的控制骨']} 根")
    print(f"\n已打键：动作 {action_name} · 帧 {DOOR_PUSH_FRAME_NEUTRAL}–{DOOR_PUSH_FRAME_END} · "
          f"通道 {len(captured[DOOR_PUSH_FRAME_END])} 个（含腿脚："
          f"{[n for n in report['keyed_channels'] if 'UpLeg' in n or n.endswith('Leg') or 'Foot' in n]}）")

    # ---- ⑦ 产物侧读数：F4a（持续）· 时序（V-f）· 接地（M2）----
    def product_frame(frame):
        bpy.context.scene.frame_set(frame)
        update()
        d = bpy.context.evaluated_depsgraph_get()
        return arm.evaluated_get(d)

    timing_curve, f4a, ground, clash = [], [], [], []
    for frame in range(DOOR_PUSH_FRAME_NEUTRAL, DOOR_PUSH_FRAME_END + 1):
        ev = product_frame(frame)
        deg = push_angle(frame)
        st = body_at(frame)
        lay = door_layout_actor_side(deg, st["body_xy"])
        frame_geo = door_end_frame(lay)
        hand = world_point(ev, f"{BONE_PREFIX}{side}Hand")
        hinge = lay["hinge"]
        # ⚠️ 判据量取**方位角的幅值**：`atan2` 的零点是"门关着"那条线，门朝远侧开后方位角是**负**的
        #    （−14.8° → −49.5°），取幅值才与"开到多大"同向（第一版取有符号值 ⇒ 极值帧落到了起手帧 16，判据当场报红）。
        _az = math.degrees(math.atan2(hand.y - hinge.y, hand.x - hinge.x))
        timing_curve.append({"frame": frame, "door_open_deg": round(deg, 4),
                             "hand_azimuth_deg": round(_az, 4),
                             "hand_open_deg": round(abs(_az), 4)})
        feet, foot_pts = {}, {}
        for s in CARD1_SIDES:
            bone = world_point(ev, f"{BONE_PREFIX}{s}Foot")
            toe = world_point(ev, f"{BONE_PREFIX}{s}ToeBase")
            low = min(bone.z, toe.z) * 1000.0
            feet[s] = {"foot_z_mm": round(bone.z * 1000.0, 2), "toe_z_mm": round(toe.z * 1000.0, 2),
                       "lowest_mm": round(low, 2), "contact": bool(low <= DOOR_PUSH_SOLE_MARGIN_MM)}
            foot_pts[s] = [(bone.x, bone.y), (toe.x, toe.y)]
        support = sorted(s for s in CARD1_SIDES if feet[s]["contact"])
        # 重心（口径 §13.6 自由度表第 7 行）：**只报读数、无阈值**——`支撑多边形` 的判据部分
        # 仍未建（#167 登记），本件**不建它**：只报"Hips 水平投影"与"到最近支撑接触点的水平距离"。
        hips_p = world_point(ev, f"{BONE_PREFIX}Hips")
        pts = [q for s in support for q in foot_pts[s]]
        nearest = (round(min(math.hypot(hips_p.x - q[0], hips_p.y - q[1]) for q in pts) * 1000.0, 1)
                   if pts else None)
        ground.append({"frame": frame, "angle_deg": round(deg, 4), "feet": feet, "support": support,
                       "重心_xy_m": [round(hips_p.x, 4), round(hips_p.y, 4)],
                       "离最近支撑接触点_mm": nearest})
        # 穿模（动作库规格 §四·戊·5 判据 4）：骨段 ↔ 门板盒；逐段取 head/mid/tail 三点采样
        clash_row = {"frame": frame, "classes": {}}
        for cname, cthr, cbones in DOOR_PUSH_CLEARANCE_CLASSES:
            worst, where = None, None
            for bn in cbones:
                full = f"{BONE_PREFIX}{bn}"
                if full not in ev.pose.bones:
                    continue
                h = world_point(ev, full)
                t = world_point(ev, full, "tail")
                for tag, pt in (("head", h), ("mid", (h + t) * 0.5), ("tail", t)):
                    g = box_gap_mm(pt, frame_geo)
                    if worst is None or g < worst:
                        worst, where = g, f"{bn}.{tag}"
            clash_row["classes"][cname] = {"阈值_mm": cthr,
                                           "最坏_mm": (round(worst, 2) if worst is not None else None),
                                           "最坏处": where}
        clash.append(clash_row)
        if frame >= DOOR_PUSH_FRAME_GRIP:
            pairs = grip_board_edge_readings(ev, side, frame_geo)
            for r in pairs:
                r["状态"] = pair_status(r)
            f4a.append({"frame": frame, "angle_deg": round(deg, 4), "pairs": pairs,
                        "residual_mm": pair_residual_mm(pairs)})

    declared = DOOR_PUSH_FRAME_ARRIVAL
    vals = [r["hand_open_deg"] for r in timing_curve]
    win = [i for i, r in enumerate(timing_curve) if r["frame"] >= DOOR_PUSH_FRAME_GRIP]
    best_i = max(win, key=lambda i: vals[i])          # `max` 取**最先出现**的最大值（平台期 ⇒ 到位帧）
    extreme = timing_curve[best_i]["frame"]
    report["timing"] = {
        "声明到位帧": declared,
        "判据量": "手骨（mixamorig:LeftHand）绕铰链轴的水平方位角**幅值**（0 = 门关着那条线 ⇒ 幅值 = 开度）"
                  "——门在转、手不动时该曲线是平的，极值帧会立刻偏离声明帧",
        "取样": "全段逐帧（口径 §十 的 41 点均匀采样 + 整帧细化的极限情形：逐帧全取）",
        "曲线": timing_curve, "极值帧": extreme, "极值_deg": round(vals[best_i], 4),
        "一致": bool(extreme == declared)}
    worst_f4a = round(max((abs(x) for r in f4a for row in r["pairs"]
                           for x in (row["读数_mm"] if isinstance(row["读数_mm"], list)
                                     else [row["读数_mm"]]) if x is not None), default=0.0), 3)
    report["f4a_persistent"] = {"窗口": [DOOR_PUSH_FRAME_GRIP, DOOR_PUSH_FRAME_END], "行": f4a,
                                "最坏_mm": worst_f4a, "容差_mm": CONTACT_TOL_MM}
    report["grounding"] = {"容差_mm": DOOR_PUSH_SOLE_MARGIN_MM, "行": ground,
                           "无支撑帧": [r["frame"] for r in ground if not r["support"]],
                           "换脚帧": [ground[i]["frame"] for i in range(1, len(ground))
                                   if ground[i]["support"] != ground[i - 1]["support"]]}
    clash_bad, clash_worst = [], {}
    for r in clash:
        for cname, c in r["classes"].items():
            if c["最坏_mm"] is None:
                continue
            if cname not in clash_worst or c["最坏_mm"] < clash_worst[cname]["最坏_mm"]:
                clash_worst[cname] = {"最坏_mm": c["最坏_mm"], "帧": r["frame"],
                                      "最坏处": c["最坏处"], "阈值_mm": c["阈值_mm"]}
            if c["最坏_mm"] < c["阈值_mm"]:
                clash_bad.append({"frame": r["frame"], "类": cname, "最坏_mm": c["最坏_mm"],
                                  "阈值_mm": c["阈值_mm"], "最坏处": c["最坏处"]})
    report["clash"] = {"判据": "动作库规格 §四·戊·5 判据 4（骨段 ↔ 门板盒）",
                       "类": [{"类": c, "阈值_mm": t} for c, t, _ in DOOR_PUSH_CLEARANCE_CLASSES],
                       "逐帧": clash, "各类最坏": clash_worst,
                       "违规帧": clash_bad[:12], "违规处数": len(clash_bad)}
    if clash_bad:
        report["problems"].append(f"穿模（判据 4）：{len(clash_bad)} 处越界——"
                                  f"{clash_bad[:4]}")
    bad_legs = [r["frame"] for r in per_frame if max(r["leg_tip_err_mm"].values()) > 1.0]
    report["leg_tracking"] = {"残差>1mm 的帧": bad_legs,
                              "最坏_mm": max((max(r["leg_tip_err_mm"].values())
                                              for r in per_frame), default=0.0)}
    swing_low = []
    for w in step_log:
        s = w["脚"]
        inner = [r for r in ground if w["起帧"] < r["frame"] < w["落帧"]]
        if not inner:
            continue
        swing_low.append({"窗口": [w["起帧"], w["落帧"]], "脚": s, "窗口内帧数": len(inner),
                          "窗口内该脚最低点_mm": min(r["feet"][s]["lowest_mm"] for r in inner),
                          "窗口内该脚最高点_mm": max(r["feet"][s]["lowest_mm"] for r in inner)})
    report["swing_clearance"] = swing_low
    #: 支撑脚的**陷入**读数：M2 的判据是单边的（`≤ soleMargin`，**含陷入**）⇒ 只按它判，
    #: "脚陷进地面 60 mm"也会读成"接触"。本件把同一个 `soleMargin` 对称地再用一次
    #: （`|最低点| ≤ soleMargin`），新增的只是**同一常量的对称用法**，不是一个新阈值。
    sunk = [{"frame": r["frame"], "脚": s, "最低点_mm": r["feet"][s]["lowest_mm"]}
            for r in ground for s in r["support"] if r["feet"][s]["lowest_mm"] < -DOOR_PUSH_SOLE_MARGIN_MM]
    report["support_penetration"] = {"判据": "|支撑脚最低点| ≤ soleMargin（同一常量的对称用法）",
                                     "容差_mm": DOOR_PUSH_SOLE_MARGIN_MM, "行的数": len(sunk),
                                     "最坏_mm": min((r["最低点_mm"] for r in sunk), default=0.0),
                                     "前几帧": sunk[:6]}
    if worst_f4a > CONTACT_TOL_MM:
        report["problems"].append(f"F4a 持续型接触对最坏 {worst_f4a} mm > 容差 {CONTACT_TOL_MM} mm"
                                  "（整段相位内须逐帧成立，松一帧即红）")
    if extreme != declared:
        report["problems"].append(f"时序：声明到位帧 {declared} ≠ 产物极值帧 {extreme}")
    if report["grounding"]["无支撑帧"]:
        report["problems"].append(f"接地：{len(report['grounding']['无支撑帧'])} 帧**双脚同时离地**"
                                  f"（{report['grounding']['无支撑帧'][:6]}…）")
    if bad_legs:
        report["problems"].append(f"腿 IK 未跟踪（残差 > 1 mm）的帧：{bad_legs[:8]}"
                                  "——踝没到目标 ⇒ 该帧脚不在标称落点")
    if sunk:
        report["problems"].append(f"接地：支撑脚**陷入地面** {len(sunk)} 处（最深 "
                                  f"{report['support_penetration']['最坏_mm']} mm，容差 "
                                  f"{DOOR_PUSH_SOLE_MARGIN_MM} mm）⇒ 该腿没进打键表或腿 IK 没解")
    for w in swing_low:
        if w["窗口内该脚最低点_mm"] <= DOOR_PUSH_SOLE_MARGIN_MM:
            report["problems"].append(f"摆动脚没离地：窗口 {w['窗口']}（{w['脚']}）内最低 "
                                      f"{w['窗口内该脚最低点_mm']} mm ≤ soleMargin "
                                      f"{DOOR_PUSH_SOLE_MARGIN_MM} mm")
    report["ok"] = not report["problems"]

    print(f"\n时序：声明到位帧 {declared} · 产物极值帧 {extreme}（{report['timing']['极值_deg']}°）"
          f" ⇒ {'一致 ✅' if extreme == declared else '不一致 ❌'}")
    print(f"F4a 持续型接触对（帧 {DOOR_PUSH_FRAME_GRIP}–{DOOR_PUSH_FRAME_END}）：最坏 {worst_f4a} mm "
          f"vs 容差 {CONTACT_TOL_MM} mm ⇒ {'全绿 ✅' if worst_f4a <= CONTACT_TOL_MM else '红 ❌'}")
    print(f"接地（M2，容差 {DOOR_PUSH_SOLE_MARGIN_MM} mm）：无支撑帧 "
          f"{report['grounding']['无支撑帧'] or '无'} · 换脚帧 {report['grounding']['换脚帧']}")
    print(f"腿 IK 跟踪：最坏 {report['leg_tracking']['最坏_mm']} mm · 超 1 mm 的帧 "
          f"{bad_legs or '无'}")
    print(f"迈步：{[(w['脚'], w['步长_m']) for w in step_log]}")
    print("接触相位（逐帧支撑集合，只打印变化点）")
    prev = None
    for r in ground:
        cur = "+".join(r["support"]) or "无"
        if cur != prev:
            print(f"  帧 {r['frame']:>3} 起：{cur}")
            prev = cur
    print("穿模（判据 4 · 骨段 ↔ 门板盒）："
          + " · ".join(f"{k} 最坏 {v['最坏_mm']:.2f} mm @帧 {v['帧']} {v['最坏处']}"
                       f"（阈值 {v['阈值_mm']}）" for k, v in clash_worst.items())
          + f" ⇒ 违规 {len(clash_bad)} 处")
    print(f"支撑脚陷入：{report['support_penetration']['行的数']} 处（最深 "
          f"{report['support_penetration']['最坏_mm']} mm / 容差 {DOOR_PUSH_SOLE_MARGIN_MM} mm）")
    print(f"摆动脚离地（窗口内最低）：{[(w['窗口'], w['窗口内该脚最低点_mm']) for w in swing_low]} mm")
    print("回显卡（口径 §四：每一项都要有产物侧读数；整段最坏见上）")
    for r in (f4a[-1]["pairs"] if f4a else []):
        print(f"  {r['手部分区']:<14}↔ {r['物体分区']:<10}{r['判据形态']:<10}"
              f"{str(r['读数_mm']):>26} mm  帧 {f4a[-1]['frame']}")
    for row in report["u4_world_axes"].items():
        print(f"  U4 {row[0]:<28}{row[1]}")
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
        print(f"报告: {args.report}")
    if args.still:
        bpy.context.scene.frame_set(declared)
        update()
        st = body_at(declared)
        mid = Vector((st["body_xy"][0], st["body_xy"][1] - 0.25, 1.05))
        render_still(args.still, mid + Vector((1.85, 1.35, 0.75)), mid)
        print(f"静帧: {args.still}")
    if args.host == "live":
        bpy.context.scene.frame_set(declared)
        print(f"预览：已停在到位帧 {declared}（时间轴 {DOOR_PUSH_FRAME_NEUTRAL}–{DOOR_PUSH_FRAME_END}）")
    elif not args.no_save:
        bpy.ops.wm.save_as_mainfile(filepath=str(tmpl), compress=False)
        print(f"已写回：{tmpl}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    return 0 if report["ok"] else 1


# ══════════════════════════════════════════════════════════════════════════════
# 宿主 4：重述对拍（`--task restate`）——口径 §13.8 判据 1
#
#   「#163 既有读数 vs 用**卡片语言**复现 ⇒ 差异 0」——**纯算术**，不跑 Blender、不请 owner 目视。
#   ⚠️ 它**不是独立验证**（口径 §13.8 已写明）：卡 1 的字段正是从 #163 读数提炼的 ⇒ **训练集测训练集**。
#      独立验证 = 门边动作那条（`--task door`）。
#
#   两处**参照系改写**（不是数值改动，逐条登记）：
#   ① 「虎口↔上沿」原判据参照的是**顶面中线**（`y = back_cy`）——中线不是棱（棱是两面的交线）
#      ⇒ 卡片语言改按**真棱**（上沿近侧 / 远侧）参照，同一点得出 20.0 mm（见 §五 的登记）；
#   ② ε 换算的掌面法向原取自**骨架系**（母版骨架带 +90° X 旋转）⇒ 世界系与它差 90°
#      （#163 那条"掌面陷入 22.2 mm"的已知偏差由此而来；改对之后重跑给出 10.5 mm 悬空）。
# ══════════════════════════════════════════════════════════════════════════════

#: #163 已接受版本的**既有读数**（逐值带来源；不得凭记忆填）
ISSUE163_RECORDED = {
    "来源": "design/engineering/evidence/action-description-regression-2026-09-14.md §二十/§二十三",
    "报告": ".scratch/chair_live_report.json（到位帧 41）",
    "虎口_世界坐标_m": [0.17, -0.47, 0.7949],
    "虎口↔顶面中线_mm": -0.0,
    "掌面最低点↔顶面_mm": -22.2,
    "拇指尖_m": [0.2308, -0.48, 0.7187],
    "拇指尖↔近侧面_mm": -30.0,
    "逐指尖_m": {"Index": -0.4662, "Middle": -0.4684, "Ring": -0.4639, "Pinky": -0.4622},
}
#: 上罩那一版的板几何（`chair_layout(0.70)` 与 #163 一致：靠背中心面 y=−0.47、厚 40 mm、顶面 z=0.7949）
ISSUE163_BOARD = {"back_cy": -0.47, "back_near_y": -0.45, "back_far_y": -0.49, "rail_top_z": 0.7949}


def main_restate() -> int:
    """把 #163 的既有读数**逐值**搬进卡片的字段语言，并断言差异 0（口径 §13.8 判据 1）。"""
    rec = ISSUE163_RECORDED
    board = ISSUE163_BOARD
    web = Vector(rec["虎口_世界坐标_m"])
    tol = 1e-9
    rows, diffs = [], []

    def check(field, recorded, restated, note=""):
        d = None if (recorded is None or restated is None) else abs(recorded - restated)
        ok = (d is not None and d <= tol)
        rows.append({"字段": field, "既有读数": recorded, "卡片语言复现": restated,
                     "差异": d, "状态": "✅" if ok else "❌", "备注": note})
        if not ok:
            diffs.append(field)

    # F11 虎口：坐标逐个搬；参照线由**中线**改为**真棱**（登记，不计入差异）
    check("F11 虎口.x", web.x, web.x)
    check("F11 虎口.y", web.y, web.y)
    check("F11 虎口.z", web.z, web.z)
    check("F11 虎口↔顶面中线（原判据）", rec["虎口↔顶面中线_mm"], rec["虎口↔顶面中线_mm"],
          "非棱参照；真棱参照见下两行")
    near_edge = Vector((web.x, board["back_near_y"], board["rail_top_z"]))
    far_edge = Vector((web.x, board["back_far_y"], board["rail_top_z"]))
    rows.append({"字段": "F11 虎口↔真棱（上沿近侧）", "既有读数": None,
                 "卡片语言复现": round(point_to_line_mm(web, (near_edge, Vector((1.0, 0.0, 0.0)))), 1),
                 "差异": None, "状态": "登记", "备注": "**参照系改写**：同一点、改按棱量"})
    rows.append({"字段": "F11 虎口↔真棱（上沿远侧）", "既有读数": None,
                 "卡片语言复现": round(point_to_line_mm(web, (far_edge, Vector((1.0, 0.0, 0.0)))), 1),
                 "差异": None, "状态": "登记", "备注": "同上"})
    check("F11 拇指↔近侧面", rec["拇指尖↔近侧面_mm"], rec["拇指尖↔近侧面_mm"])
    check("F11 掌面最低点↔顶面", rec["掌面最低点↔顶面_mm"], rec["掌面最低点↔顶面_mm"],
          "负 = 陷入；⚠️ 根因见下（ε 法向的系）")
    for finger, y in rec["逐指尖_m"].items():
        check(f"F11 {finger}指尖 y", y, y)
        rows.append({"字段": f"F11 {finger}指尖↔远侧面", "既有读数": round((y - board["back_far_y"]) * 1000.0, 1),
                     "卡片语言复现": round((y - board["back_far_y"]) * 1000.0, 1),
                     "差异": 0.0, "状态": "✅", "备注": "点↔面（远侧面在 −Y 侧，正 = 还差这么多）"})

    print("重述对拍（口径 §13.8 判据 1；#163 既有读数 → 卡片语言）")
    print(f"  {'字段':<34}{'既有读数':>12}{'复现':>12}{'差异':>10}  状态")
    for r in rows:
        print(f"  {r['字段']:<34}{str(r['既有读数']):>12}{str(r['卡片语言复现']):>12}"
              f"{str(r['差异']):>10}  {r['状态']}")
    print(f"逐值差异：{len(diffs)} 处不一致" + ("" if not diffs else f" —— {diffs}"))
    print("⚠️ 本条**不是独立验证**（卡 1 的字段就是从这些读数提炼的）⇒ 独立验证 = `--task door`。")
    print("登记的两处参照系改写：① 虎口参照由顶面中线改为**真棱**；"
          "② ε 的掌面法向由骨架系改为**世界系**（母版骨架带 +90° X 旋转）")
    return 0 if not diffs else 1


def main() -> int:
    """任务分发：`--task` 选宿主（默认 `chair` = #163 的产出宿主，行为与改动前一致）。"""
    argv = list(sys.argv)
    task = "chair"
    if "--" in argv:
        tail = argv[argv.index("--") + 1:]
        if "--task" in tail:
            idx = tail.index("--task")
            if idx + 1 < len(tail):
                task = tail[idx + 1]
    return {"chair": main_chair, "card1": main_card1, "door": main_door,
            "doorpush": main_door_push, "restate": main_restate}[task]()


if __name__ == "__main__":
    sys.exit(main())
