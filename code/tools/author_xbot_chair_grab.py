#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 verystrongdog
# SPDX-License-Identifier: GPL-3.0-or-later
"""author_xbot_chair_grab.py —— 在母版上产出动作 `BendGripChairBack`（弯腰、双手抓住椅背）。

来源：design/presentation/动作描述口径.md（§二 三问骨架 · §三 D7 自由度表 · §八 容差 ε · §十 验收判据 V-a…V-e）
      · design/presentation/Blender动作制作管线.md §七·B（撤回记录）
      · issue #163（**这是口径的回归样本**：口径管不管用，就看这一次）

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

#: 自由度表（口径 §三 D7）——**owner 2026-09-14 圈定**，不是 agent 自选
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
    normal = (pb.matrix.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
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


def main() -> int:
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


if __name__ == "__main__":
    sys.exit(main())
