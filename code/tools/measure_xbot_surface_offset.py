#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 verystrongdog
# SPDX-License-Identifier: GPL-3.0-or-later
"""measure_xbot_surface_offset.py —— 实测「骨 → 蒙皮表面」偏移（口径 §八 的接触档 ε）。

来源：design/presentation/动作描述口径.md §八（容差 ε 口径 = "骨 → 蒙皮表面"实测偏移）
      · §十五 / §15.6（部位侧 ε 与逐部位登记，#168 起：**按骨集合测**，不再手部专用）
      · §6.1（四系）· §6.2（世界轴映射：+X = 左手侧 · −Y = 前）· §15.4（13 根标记骨不许进部位）
      · design/engineering/issue-process.md §4.1.1（参数来源）
      · 先例：`FootGroundingIK.cs` 的 `soleMargin = 0.0028 m`——2026-09-12 bind pose 趾骨 Y 的实测值，
        同属"骨在蒙皮里，蒙皮表面才是几何实体"这一类量
      · 先例：`measure_xbot_control_axes.py`（同类"实测取参数"件；本脚本的姿势应用与它同源）

为什么需要它
------------
"手掌贴合椅背上方"这类需求，判据落在**蒙皮表面**上；而 agent 手上的读数一律是**骨端点**。
两者之差不是一个可以拍的常数——它随骨、随蒙皮、随方向而异。本脚本把它**测出来**，
于是"贴合"可以从"只报读数、由 owner 目视判"升级为"读数 + 有来源的 ε"。

测什么（三层）
--------------
1. **表面剖面**：对每根目标骨，取其**主导组就是该骨**的顶点，在**该骨静止局部系**里量
   6 个方向（±X/±Y/±Z）的**最外沿距离**（骨原点 → 最外顶点）。这就是"往哪个方向有多厚"。
2. **平坦面支撑数**：每个方向上落在极值面 2 mm 内的顶点数——用来**判面朝哪一侧**
   （大平面 ⇒ 支撑数大）。面方向由数据定，不由本脚本猜。
3. **稳定性（本条的假设）**：在若干确定性姿势下，跟踪**静止姿势选出的那批最外顶点**，
   量它们相对该骨的局部偏移变化（mm）。问题就是："ε 是常数吗？"

⚠️ 三条实测教训（都踩过，都已改）
--------------------------------
- **单位**：母版是 Mixamo **厘米制** + Armature 对象 `scale = 0.01`（管线 §二 ⚠️ 块）。
  骨矩阵与网格数据都在**骨架局部单位（= 1 cm）**里，故米制换算 = `× 对象 scale`。
  第一版按"米"直接 `× 1000`，量出"手的外沿 **3–10 米**"——**量级自证**就足以当场否掉这个读数。
- **取样门槛不能是"权重 ≥ 0.999"**：线性混合蒙皮（LBS）下权重 = 1 的顶点相对其骨**恒为常数**，
  用它们做样本，稳定性判据必然 0 mm ——**平凡通过**（本仓记过同类教训：管线 §三 V8 的由来）。
  故成员判据取**主导组（argmax）**，权重只作报告量；表面那层混合权重顶点才是会滑动的那批。
- **换算用的法向必须与读数同一个系**（[#164] 实测：母线骨架对象带 +90° X 旋转，把骨架系法向
  当世界方向用 ⇒ 差 90°、手被推错 32.68 mm）。本脚本每次运行都跑 `frame_check`：
  ① 两条独立算路（3×3 与 4×4 点变换）给出同一个世界方向；
  ② 逐面给出"若漏掉 `arm.matrix_world` 会差多少"的读数（含 #163 那个**不动轴巧合**）。

用法
----
    blender --background --factory-startup --python-exit-code 1 \\
        --python code/tools/measure_xbot_surface_offset.py -- \\
        --template <.blend> [--set hand|headneck] [--bones 额外骨名,…] [--report <.json>]

`--set` 选**部位集**（默认 `hand` = #160 的 42 根 `Hand*` 族，读数与 #160 逐值相同）。
新增部位 = 在 `PART_SETS` 里加一行（骨集合 + 姿势表 + 该集的根骨），**不改测法**
（口径 §15.6「不建空表」：只测实际要用的部位）。

版本：Blender 4.5 / 5.x 均可（本脚本不碰 Action API，故无需 `blender_action_compat`）。
"""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector, Euler

BONE_PREFIX = "mixamorig:"
#: 手部集的根骨：两手 + 每侧 20 根手指骨（骨表里的 `Hand*` 族，共 42 根）
HAND_ROOTS = ("mixamorig:LeftHand", "mixamorig:RightHand")
FINGERS = ("Thumb", "Index", "Middle", "Ring", "Pinky")
FINGER_SEGMENTS = (1, 2, 3, 4)
HAND_BONES = HAND_ROOTS + tuple(
    f"{BONE_PREFIX}{side}Hand{f}{seg}"
    for side in ("Left", "Right") for f in FINGERS for seg in FINGER_SEGMENTS)
#: 方向：静止局部系的 ±X / ±Y / ±Z
DIRECTIONS = (("+X", (1, 0, 0)), ("-X", (-1, 0, 0)),
              ("+Y", (0, 1, 0)), ("-Y", (0, -1, 0)),
              ("+Z", (0, 0, 1)), ("-Z", (0, 0, -1)))
#: "平坦面"片层厚度（米）——落在极值面这么薄一层里的顶点算作支撑
FLAT_SLAB_M = 0.002
#: 量级自证上限：单根骨沿任一方向的表面外沿不该超过这个值（米）。超过 ⇒ 单位或成员判据出错
#: ⚠️ 沿骨长轴那一格量的是"骨原点到链末表面"（头骨 210 mm / 颈骨 93 mm），故不是骨半径的两倍
PLAUSIBLE_MAX_M = 0.30

#: 手部集的确定性姿势（只动控制骨；控制骨经约束驱动变形骨，读数走 evaluated depsgraph）
HAND_POSES = (
    ("rest", {}),
    ("wrist_bend", {"CTRL_LeftHand": (40.0, 0.0, 0.0), "CTRL_RightHand": (40.0, 0.0, 0.0)}),
    ("elbow+wrist", {"CTRL_LeftForeArm": (0.0, 0.0, 30.0), "CTRL_LeftHand": (0.0, 20.0, 0.0),
                     "CTRL_RightForeArm": (0.0, 0.0, 30.0), "CTRL_RightHand": (0.0, 20.0, 0.0)}),
    ("arms_down", {"CTRL_LeftArm": (35.0, 0.0, 0.0), "CTRL_RightArm": (35.0, 0.0, 0.0)}),
)
#: 颈头集（口径 §15.3 第 15 行分区：`Neck`/`Head`，`HeadTop_End` 排除见 §15.4）
HEADNECK_BONES = (f"{BONE_PREFIX}Neck", f"{BONE_PREFIX}Head")
#: 颈头**无控制骨**（管线 §2.1.5 规矩 2：直接打键）⇒ 姿势直接转变形骨；
#: 幅度与轴沿用管线 §2.1.4 的实测语义（X = 点头 · Y = 转头 · Z = 歪头）
HEADNECK_POSES = (
    ("rest", {}),
    ("neck_nod", {f"{BONE_PREFIX}Neck": (20.0, 0.0, 0.0)}),
    ("head_turn", {f"{BONE_PREFIX}Neck": (0.0, 20.0, 0.0), f"{BONE_PREFIX}Head": (0.0, 15.0, 0.0)}),
    ("head_tilt", {f"{BONE_PREFIX}Head": (0.0, 0.0, 20.0)}),
    ("spine_lean", {f"{BONE_PREFIX}Spine2": (12.0, 0.0, 0.0)}),
)

#: 部位集：骨集合 + 姿势表 + 打印明细的"根骨" + 掌面探针是否适用
#: ⚠️ 默认 `hand` ⇒ 不传 `--set` 时读数/报告与 #160 那两次运行**逐值相同**
PART_SETS = {
    "hand": {"bones": HAND_BONES, "poses": HAND_POSES, "print_roots": HAND_ROOTS,
             "palm_probe": True, "extra_label": "手指骨"},
    "headneck": {"bones": HEADNECK_BONES, "poses": HEADNECK_POSES, "print_roots": HEADNECK_BONES,
                 "palm_probe": False, "extra_label": "非根骨"},
}

#: 具名面的**局部轴分组**——语义来源：管线 §2.1.4 实测轴表（`Neck`/`Head`：局部 X = 点头/抬头
#: ⇒ X 是**左右轴**；局部 Z = 歪头 ⇒ Z 是**前后轴**；局部 Y = 转头 ⇒ Y **沿骨长轴**）。
#: 正负号**不写死**：由实测 `axis_in_world` 与口径 §6.2 的世界轴映射（+X = 左手侧 · −Y = 前）比对后裁定，
#: 并把"测得方向 ↔ 命名世界轴"的夹角一并报出（两条独立来源，非自证）。
PART_FACE_AXIS_GROUPS = {
    f"{BONE_PREFIX}Neck": {"side": ("+X", "-X"), "front_back": ("+Z", "-Z"), "along": ("+Y",)},
    f"{BONE_PREFIX}Head": {"side": ("+X", "-X"), "front_back": ("+Z", "-Z"), "along": ("+Y",)},
}
#: 命名世界轴（口径 §6.2）：世界 +X = 左手侧 · 世界 −Y = 前（角色面朝方向）· 世界 +Z = 上
NAMED_WORLD_AXES = {
    "side_left": ((1.0, 0.0, 0.0), "左侧面（耳侧）"),
    "front": ((0.0, -1.0, 0.0), "前面（额）"),
    "along_bone": ((0.0, 0.0, 1.0), "沿骨长轴（头顶方向）"),
}


def parse_args(argv):
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser(prog="measure_xbot_surface_offset.py")
    ap.add_argument("--template", default=str(Path(__file__).resolve().parents[2] /
                                             ".scratch/blender_assets/xbot/XBot_AnimationTemplate.blend"))
    ap.add_argument("--report", default=None)
    ap.add_argument("--set", dest="sets", default="hand",
                    help="部位集，逗号分隔（可选：%s；默认 hand）" % " / ".join(PART_SETS))
    ap.add_argument("--bones", default=None,
                    help="额外骨名（逗号分隔，附加到所选部位的骨集合上；姿势表仍取 --set）")
    return ap.parse_args(argv)


def selected(ap_args):
    """解析 --set / --bones ⇒ (集合名, 骨名单, 姿势表, 打印根骨, 掌面探针是否需要, 额外骨标签)。"""
    names = [s.strip() for s in ap_args.sets.split(",") if s.strip()]
    if not names:
        raise SystemExit("--set 为空")
    for n in names:
        if n not in PART_SETS:
            raise SystemExit(f"未知部位集：{n}（可选：{', '.join(PART_SETS)}）")
    bones, poses, roots = [], [], []
    for n in names:
        spec = PART_SETS[n]
        bones += [b for b in spec["bones"] if b not in bones]
        poses += [p for p in spec["poses"] if all(p[0] != q[0] for q in poses)]
        roots += [b for b in spec["print_roots"] if b not in roots]
    extra_label = PART_SETS[names[0]]["extra_label"]
    if ap_args.bones:
        for b in [x.strip() for x in ap_args.bones.split(",") if x.strip()]:
            if b not in bones:
                bones.append(b)
    palm = any(PART_SETS[n]["palm_probe"] for n in names)
    return names, tuple(bones), tuple(poses), tuple(roots), palm, extra_label


def armature():
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(arms) != 1:
        raise RuntimeError(f"期望恰好 1 个 Armature，实测 {len(arms)}")
    return arms[0]


def skinned_meshes(arm):
    """只取真正被该骨架蒙皮的网格（母版里的 REF_* 参考代理没有 Armature 修改器）。"""
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        if any(m.type == "ARMATURE" and m.object == arm for m in o.modifiers):
            out.append(o)
    return sorted(out, key=lambda o: o.name)


def reset_pose(arm):
    """归零（§7.4 硬规矩：量任何东西之前先归零）。

    ⚠️ 不得改 `rotation_mode`——控制骨的轴向语义与既有脚本都依赖它（管线 §2.1 红线 1）。
    """
    for pb in arm.pose.bones:
        if pb.rotation_mode == "QUATERNION":
            pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        else:
            pb.rotation_euler = Euler((0.0, 0.0, 0.0), pb.rotation_mode)
        pb.location = (0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()


def apply_pose(arm, spec, overrides):
    """摆一个确定性姿势。⚠️ 不动姿势的 `rotation_mode`（除下方这一处**临时**改动）。

    母版里 35 根骨是 `QUATERNION`（变形骨）、43 根是 `XYZ`（控制骨）——颈头/脊柱**没有控制骨**
    （管线 §2.1.5 规矩 2：直接打键），要对它们施 `rotation_euler` 就得先切模式。
    本脚本**只读不存**（从不 `save_as_mainfile`），故改动不落盘；每处改动都记进报告。
    """
    reset_pose(arm)
    for name, (rx, ry, rz) in spec.items():
        pb = arm.pose.bones.get(name)
        if pb is None:
            raise RuntimeError(f"控制骨/变形骨不存在：{name}")
        if pb.rotation_mode == "QUATERNION":
            pb.rotation_mode = "XYZ"
            overrides[name] = "QUATERNION → XYZ（临时；本脚本不存盘）"
        pb.rotation_euler = Euler((math.radians(rx), math.radians(ry), math.radians(rz)), pb.rotation_mode)
    for _ in range(10):
        bpy.context.view_layer.update()


def dominant_set(mesh_obj, bone_name):
    """主导组（argmax 权重）== bone_name 的顶点 → [(顶点序号, 该骨权重), ...]。"""
    gi = mesh_obj.vertex_groups[bone_name].index
    out = []
    for v in mesh_obj.data.vertices:
        best_g, best_w, own = None, -1.0, 0.0
        for ref in v.groups:
            if ref.weight > best_w:
                best_g, best_w = ref.group, ref.weight
            if ref.group == gi:
                own = ref.weight
        if best_g == gi:
            out.append((v.index, own))
    return out


def weight_stats(pairs):
    if not pairs:
        return None
    ws = sorted(w for _, w in pairs)
    n = len(ws)
    return {"min": round(ws[0], 4), "median": round(ws[n // 2], 4), "max": round(ws[-1], 4)}


def deformed_world(mesh_obj):
    """evaluated depsgraph 下的顶点世界坐标（约束求值后的姿势）。"""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    me = ev.to_mesh()
    mw = ev.matrix_world
    out = [mw @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    return out


#: 四指屈曲候选符号——**两种都试**，取"指尖靠近拇指"的那一个
#: ⚠️ 不得直接套用别处实测的符号：§七·B 记的 `左 X+1 / 右 X−1` 是**抓椅背那个姿势**下自测的结果，
#: 本脚本在静止 T-pose 下照抄，右手解出了**超伸展**（指尖朝 +Y 反向）——2026-09-14 实测踩到。
CURL_SIGNS = (1.0, -1.0)
CURL_BONES = ("Index1", "Middle1", "Ring1", "Pinky1")
CURL_DEG = 40.0
#: 用哪根指尖与拇指尖的间距作判据（屈曲 = 该间距变小）
CURL_TIP = "Middle4"
THUMB_TIP = "Thumb3"


def palm_direction_probe(arm, local_to_m):
    """掌面朝向 = **手指屈曲时指尖的移动方向**（屈曲永远朝掌心）。

    为什么要测而不是猜："手掌贴合 X" 的 ε 必须取**掌面那一侧**的读数，而 ±Z / ±X 里哪一侧是掌面
    靠看数字看不出来。判据用**对指几何**：四指屈曲会把中指尖带向**拇指尖**（拇指在掌面一侧的边上），
    故两种符号各试一次、取使 |中指尖 − 拇指尖| **变小**的那个 —— 这个判据不预设左右符号，也不需要
    先知道掌面朝哪边。
    """
    out = {}
    for side in ("Left", "Right"):
        hand = f"{BONE_PREFIX}{side}Hand"
        tip = f"{BONE_PREFIX}{side}Hand{CURL_TIP}"
        thumb = f"{BONE_PREFIX}{side}Hand{THUMB_TIP}"
        bl = arm.data.bones[hand].matrix_local
        bl_inv = bl.inverted()

        def thumb_gap_mm():
            a = arm.pose.bones[tip].tail
            b = arm.pose.bones[thumb].tail
            return (a - b).length * local_to_m * 1000.0

        reset_pose(arm)
        gap0 = thumb_gap_mm()
        p0 = bl_inv @ arm.pose.bones[tip].tail.copy()
        trials = {}
        for sign in CURL_SIGNS:
            reset_pose(arm)
            for f in CURL_BONES:
                pb = arm.pose.bones[f"{BONE_PREFIX}{side}Hand{f}"]
                if pb.rotation_mode == "QUATERNION":
                    raise RuntimeError(f"{pb.name} 是 QUATERNION——本脚本不改模式")
                e = list(pb.rotation_euler)
                e[0] = math.radians(CURL_DEG * sign)
                pb.rotation_euler = Euler(e, pb.rotation_mode)
            for _ in range(10):
                bpy.context.view_layer.update()
            d = (bl_inv @ arm.pose.bones[tip].tail.copy()) - p0
            trials[sign] = {"gap_mm": round(thumb_gap_mm(), 3),
                            "displacement_local": [round(c, 6) for c in d],
                            "displacement_mm": [round(c * local_to_m * 1000.0, 3) for c in d]}
        reset_pose(arm)

        # 判据：屈曲 = 指尖靠近拇指尖（间距变小）；两个符号间距都比静止大 ⇒ 判据失效
        best = min(trials, key=lambda s: trials[s]["gap_mm"])
        valid = trials[best]["gap_mm"] < gap0
        d = Vector(trials[best]["displacement_local"]) if valid else Vector((0, 0, 0))
        axes = {"X": d.x, "Y": d.y, "Z": d.z}
        axis = max(axes, key=lambda k: abs(axes[k]))
        signed = ("+" if axes[axis] >= 0 else "-") + axis
        out[side] = {
            "rest_thumb_tip_gap_mm": round(gap0, 3),
            "trials": {("+1" if s > 0 else "-1"): t for s, t in trials.items()},
            "chosen_sign": ("+1" if best > 0 else "-1"),
            "criterion_valid": bool(valid),
            "palm_direction_local": signed,
            "palm_normal_displacement_mm": round(axes[axis] * local_to_m * 1000.0, 3),
        }
        if not valid:
            out[side]["note"] = "两个符号都没让指尖靠近拇指尖 ⇒ 屈曲判据在本骨架上失效，掌面方向未定"
    return out


def frame_check(arm, mesh_entry, bone_name):
    """换算系检查：**换算用的法向与读数的系一致**（#164 的代价 = 差 90°、手被推错 32.68 mm）。

    三个量：
    ① `axis_world_with_arm` —— 正确算路：`arm.matrix_world` 参与（本脚本报告与消费者都该用这个）；
    ② `axis_world_without_arm` —— #164 那种形态：法向取自**骨架系**却当世界方向用；
    ③ `route_identity_deg` —— 另一条**独立算路**（4×4 点变换 `arm.matrix_world @ bone.matrix_local`
       对轴端点求差）与 ① 的夹角 ⇒ 证明 `matrix_world` 恰好参与一次、没有丢旋转。
    再给两个"差多少"的读数：位移向量差 `ε·|n_c − n_w|`、沿正确法向的分量差 `ε·(1 − n_c·n_w)`。
    """
    bl = arm.data.bones[bone_name].matrix_local
    out = {"axis_world_with_arm": {}, "per_direction": {}}
    for tag, d in DIRECTIONS:
        dv = Vector(d)
        n_c = (arm.matrix_world.to_3x3() @ (bl.to_3x3() @ dv)).normalized()
        n_w = (bl.to_3x3() @ dv).normalized()
        p0 = arm.matrix_world @ (bl @ Vector((0.0, 0.0, 0.0)))
        p1 = arm.matrix_world @ (bl @ dv.copy())
        n_route_b = (p1 - p0).normalized()
        eps_mm = mesh_entry["bones"][bone_name]["profile"][tag]["outer_mm"]
        cos = max(-1.0, min(1.0, n_c.dot(n_w)))
        out["axis_world_with_arm"][tag] = [round(c, 4) for c in n_c]
        out["per_direction"][tag] = {
            "axis_world_without_arm": [round(c, 4) for c in n_w],
            "angle_between_frames_deg": round(math.degrees(math.acos(cos)), 4),
            "route_identity_deg": round(math.degrees(n_c.angle(n_route_b)), 8),
            "epsilon_mm": eps_mm,
            "misplacement_vector_mm": round(eps_mm * (n_c - n_w).length, 4),
            "misplacement_along_correct_mm": round(eps_mm * (1.0 - cos), 4),
            "on_rotation_invariant_axis": bool(math.degrees(math.acos(cos)) < 1e-6),
        }
    return out


def named_faces(mesh_entry, bone_name, frame):
    """把 6 方向剖面折成**具名面**（语义 = 管线 §2.1.4 轴表；正负号 = 实测世界指向 vs 口径 §6.2）。"""
    groups = PART_FACE_AXIS_GROUPS.get(bone_name)
    row = mesh_entry["bones"].get(bone_name, {})
    if not groups or not row.get("sampled"):
        return {}
    prof = row["profile"]
    per_direction = (frame or {}).get("per_direction", {})

    def axis_world(tag):
        return Vector(prof[tag]["axis_in_world"])

    def face(tag, key, world_axis, label):
        out = {
            "label": label,
            "local_axis": tag,
            "epsilon_mm": prof[tag]["outer_mm"],
            "epsilon_m": prof[tag]["outer_m"],
            "flat_support_vertices": prof[tag]["flat_support_vertices"],
            "axis_in_world": prof[tag]["axis_in_world"],
            "angle_to_named_world_axis_deg": round(
                math.degrees(axis_world(tag).angle(Vector(world_axis))), 4),
        }
        if tag in per_direction:
            out["frame_check"] = per_direction[tag]
        return key, out

    faces = {}
    side_sorted = sorted(groups["side"], key=lambda t: -axis_world(t).dot(Vector((1.0, 0.0, 0.0))))
    fwd_sorted = sorted(groups["front_back"],
                        key=lambda t: -axis_world(t).dot(Vector((0.0, -1.0, 0.0))))
    k, v = face(side_sorted[0], "side_left", *NAMED_WORLD_AXES["side_left"])
    faces[k] = v
    k, v = face(side_sorted[1], "side_right", (-1.0, 0.0, 0.0), "右侧面（耳侧）")
    faces[k] = v
    k, v = face(fwd_sorted[0], "front", *NAMED_WORLD_AXES["front"])
    faces[k] = v
    k, v = face(fwd_sorted[1], "back", (0.0, 1.0, 0.0), "后面（后脑）")
    faces[k] = v
    for tag in groups.get("along", ()):
        k, v = face(tag, "along_bone", *NAMED_WORLD_AXES["along_bone"])
        faces[k] = v
    return faces


def main() -> int:
    args = parse_args(list(sys.argv))
    set_names, bones, poses, print_roots, need_palm, extra_label = selected(args)
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2
    report_path = Path(args.report) if args.report else tmpl.parent / "surface_offset_report.json"

    bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    arm = armature()
    meshes = skinned_meshes(arm)
    arm_inv = arm.matrix_world.inverted()
    # 骨架局部单位 → 米：母版骨架对象 scale = 0.01（管线 §二 ⚠️ 单位口径块）
    arm_scale = arm.matrix_world.to_scale()
    local_to_m = arm_scale.x
    slab_local = FLAT_SLAB_M / local_to_m if local_to_m else FLAT_SLAB_M

    report = {
        "script": "measure_xbot_surface_offset.py",
        "blender": bpy.app.version_string,
        "template": str(tmpl),
        "sets": list(set_names),
        "bones": list(bones),
        "armature": arm.name,
        "armature_scale": [round(s, 6) for s in arm_scale],
        "local_units_per_meter": round(1.0 / local_to_m, 6) if local_to_m else None,
        "flat_slab_m": FLAT_SLAB_M,
        "plausible_max_m": PLAUSIBLE_MAX_M,
        "poses": [name for name, _ in poses],
        "rotation_mode_overrides": {},
        "meshes": {m.name: {"vertices": len(m.data.vertices),
                            "scale": [round(s, 6) for s in m.matrix_world.to_scale()]} for m in meshes},
        "problems": [],
        "per_mesh": {},
    }

    reset_pose(arm)

    # ---------- 1+2. 剖面与平坦面支撑 ----------
    for mesh_obj in meshes:
        entry = {"bones": {}, "vertices": len(mesh_obj.data.vertices)}
        rest_world = [mesh_obj.matrix_world @ v.co for v in mesh_obj.data.vertices]
        for bone_name in bones:
            if bone_name not in arm.data.bones:
                entry["bones"][bone_name] = {"sampled": 0, "absent": "该骨不在骨架上"}
                continue
            vg = mesh_obj.vertex_groups.get(bone_name)
            if vg is None:
                # ⚠️ 这一格本身就是读数（#168：头/颈在两个蒙皮层上**骨集合不同**，见证据）
                entry["bones"][bone_name] = {"sampled": 0, "absent": "该层无此顶点组（无任何权重）"}
                continue
            pairs = dominant_set(mesh_obj, bone_name)
            if not pairs:
                entry["bones"][bone_name] = {"sampled": 0, "absent": "有顶点组但无主导顶点"}
                continue
            bl_inv = arm.data.bones[bone_name].matrix_local.inverted()
            bl = arm.data.bones[bone_name].matrix_local
            local = {vi: bl_inv @ (arm_inv @ rest_world[vi]) for vi, _ in pairs}
            prof = {}
            for tag, d in DIRECTIONS:
                dv = Vector(d)
                ext = max(local[vi].dot(dv) for vi, _ in pairs)
                support = sum(1 for vi, _ in pairs if local[vi].dot(dv) >= ext - slab_local)
                world_axis = (arm.matrix_world.to_3x3() @ (bl.to_3x3() @ dv)).normalized()
                prof[tag] = {
                    "outer_m": round(ext * local_to_m, 6),
                    "outer_mm": round(ext * local_to_m * 1000.0, 4),
                    "flat_support_vertices": support,
                    "axis_in_world": [round(c, 4) for c in world_axis],
                }
            entry["bones"][bone_name] = {
                "sampled": len(pairs),
                "own_weight": weight_stats(pairs),
                "profile": prof,
                "sample_ids": [vi for vi, _ in pairs],
            }
            for tag, row in prof.items():
                if row["outer_m"] > PLAUSIBLE_MAX_M:
                    report["problems"].append(
                        f"{mesh_obj.name}/{bone_name}{tag} 外沿 {row['outer_m']:.3f} m 超出量级自证上限"
                        f" {PLAUSIBLE_MAX_M} m —— 单位或成员判据可疑")
        report["per_mesh"][mesh_obj.name] = entry

    # ---------- 3. 稳定性：跨姿势跟踪"静止时选出的最外顶点集合" ----------
    stab = {}
    for mesh_obj in meshes:
        entry = report["per_mesh"][mesh_obj.name]
        rest_world = [mesh_obj.matrix_world @ v.co for v in mesh_obj.data.vertices]
        base = {}
        for bone_name, row in entry["bones"].items():
            if not row.get("sample_ids"):
                continue
            bl_inv = arm.data.bones[bone_name].matrix_local.inverted()
            local = {vi: bl_inv @ (arm_inv @ rest_world[vi]) for vi in row["sample_ids"]}
            outer = {}
            for tag, d in DIRECTIONS:
                dv = Vector(d)
                ext = max(local[vi].dot(dv) for vi in row["sample_ids"])
                outer[tag] = [vi for vi in row["sample_ids"] if local[vi].dot(dv) >= ext - slab_local]
            base[bone_name] = {"outer": outer, "local": local}

        per_pose = {}
        for pose_name, spec in poses:
            apply_pose(arm, spec, report["rotation_mode_overrides"])
            dw = deformed_world(mesh_obj)
            row_out = {}
            for bone_name, data in base.items():
                pm_inv = arm.pose.bones[bone_name].matrix.inverted()
                worst, worst_tag = 0.0, None
                for tag, ids in data["outer"].items():
                    for vi in ids:
                        cur = pm_inv @ (arm_inv @ dw[vi])
                        delta = (cur - data["local"][vi]).length * local_to_m * 1000.0
                        if delta > worst:
                            worst, worst_tag = delta, tag
                row_out[bone_name] = {"max_delta_mm": round(worst, 6), "worst_direction": worst_tag}
            per_pose[pose_name] = row_out
        reset_pose(arm)
        stab[mesh_obj.name] = {"per_pose": per_pose}
    report["stability"] = stab

    # ---------- 4a. 手部：掌面朝向（屈曲方向）与接触档 ε ----------
    if need_palm:
        palm = palm_direction_probe(arm, local_to_m)
        report["palm_direction"] = palm
        contact = {}
        for mesh_name, entry in report["per_mesh"].items():
            contact[mesh_name] = {}
            for side in ("Left", "Right"):
                bone_name = f"{BONE_PREFIX}{side}Hand"
                row = entry["bones"].get(bone_name, {})
                tag = palm[side]["palm_direction_local"]
                if row.get("sampled") and tag in row.get("profile", {}):
                    contact[mesh_name][side] = {
                        "palm_direction": tag,
                        "epsilon_mm": row["profile"][tag]["outer_mm"],
                        "axis_in_world": row["profile"][tag]["axis_in_world"],
                    }
        report["contact_epsilon"] = contact

    # ---------- 4b. 换算系检查（#164：漏掉 arm.matrix_world 会差多少） ----------
    ident = []
    for entry in report["per_mesh"].values():
        for bone_name, row in entry["bones"].items():
            if not row.get("sampled"):
                continue
            bl = arm.data.bones[bone_name].matrix_local
            for tag, d in DIRECTIONS:
                n_c = (arm.matrix_world.to_3x3() @ (bl.to_3x3() @ Vector(d))).normalized()
                p0 = arm.matrix_world @ (bl @ Vector((0.0, 0.0, 0.0)))
                p1 = arm.matrix_world @ (bl @ Vector(d))
                ident.append(math.degrees(n_c.angle((p1 - p0).normalized())))
    present = [b for b in bones if b in arm.data.bones]
    rest_identity = max(
        (abs(x - y) for b in present
         for r1, r2 in zip(arm.pose.bones[b].matrix, arm.data.bones[b].matrix_local)
         for x, y in zip(r1, r2)), default=None)
    report["frame_check"] = {
        "armature_matrix_world": [[round(c, 8) for c in r] for r in arm.matrix_world],
        "armature_rotation_euler_deg": [round(math.degrees(a), 6) for a in arm.rotation_euler],
        "armature_scale": [round(s, 8) for s in arm_scale],
        "why": "#164 实测：母版骨架对象带 +90° X 旋转（Y-up 导入）⇒ 骨架系法向当世界方向用会差 90°",
        "route_identity_max_deg": round(max(ident), 10) if ident else None,
        "rest_pose_matrix_identity_max_abs": round(rest_identity, 12) if rest_identity is not None else None,
        "per_mesh": {},
    }
    for mesh_name, entry in report["per_mesh"].items():
        report["frame_check"]["per_mesh"][mesh_name] = {}
        for bone_name, row in entry["bones"].items():
            if row.get("sampled"):
                report["frame_check"]["per_mesh"][mesh_name][bone_name] = frame_check(arm, entry, bone_name)

    # ---------- 4c. 部位面：具名面 ε（语义取自轴表，正负号取自实测世界指向） ----------
    faces_by_mesh = {}
    for mesh_name, entry in report["per_mesh"].items():
        faces_by_mesh[mesh_name] = {}
        for bone_name in bones:
            frame = report["frame_check"]["per_mesh"][mesh_name].get(bone_name)
            faces = named_faces(entry, bone_name, frame)
            if faces:
                faces_by_mesh[mesh_name][bone_name] = faces
    report["part_faces"] = faces_by_mesh

    # ---------- 5. 覆盖：哪一层有哪根骨（#168：头/颈两层的骨集合不同） ----------
    report["bone_coverage"] = {
        mesh_name: {
            "sampled": {b: r["sampled"] for b, r in entry["bones"].items() if r.get("sampled")},
            "absent": {b: r.get("absent") for b, r in entry["bones"].items() if not r.get("sampled")},
        } for mesh_name, entry in report["per_mesh"].items()}

    # ---------- 打印 ----------
    print("=" * 100)
    print(f"母版 {tmpl}")
    print(f"Blender {report['blender']} · 骨架 scale {report['armature_scale']} "
          f"(1 单位 = {local_to_m * 1000:.4f} mm) · 网格 {list(report['meshes'])}")
    print(f"部位集 {report['sets']} · 目标骨 {len(bones)} 根 · 姿势表 {report['poses']} · "
          f"平坦片层 {FLAT_SLAB_M * 1000:.1f} mm")
    print("-" * 100)
    for mesh_name, entry in report["per_mesh"].items():
        print(f"[{mesh_name}] 顶点 {entry['vertices']}")
        print(f"{'骨':<34}{'方向':>4}{'外沿(mm)':>12}{'平坦支撑':>10}  世界指向")
        for bone_name, row in entry["bones"].items():
            if not row.get("sampled"):
                if bone_name in bones:
                    print(f"{bone_name:<34}  —— {row.get('absent')}")
                continue
            if bone_name not in print_roots:
                continue
            for tag, _ in DIRECTIONS:
                p = row["profile"][tag]
                ax = p["axis_in_world"]
                print(f"{bone_name:<34}{tag:>4}{p['outer_mm']:>12.4f}{p['flat_support_vertices']:>10}"
                      f"  ({ax[0]:+.3f}, {ax[1]:+.3f}, {ax[2]:+.3f})")
            print(f"{'':<34}取样 {row['sampled']} 顶点 · 该骨权重 min/中位/max = "
                  f"{row['own_weight']['min']}/{row['own_weight']['median']}/{row['own_weight']['max']}")
        others = [b for b in bones if b not in print_roots and entry["bones"].get(b, {}).get("sampled")]
        if others:
            print(f"  （另有 {len(others)} 根{extra_label}有读数，逐根明细见 JSON）")
    print("-" * 100)
    if "palm_direction" in report:
        print("掌面朝向（判据：四指屈曲把中指尖带向拇指尖 ⇒ 该位移方向 = 掌面法向）")
        for side, row in report["palm_direction"].items():
            t = row["trials"]
            print(f"  {side:<6} 静止拇中尖距 {row['rest_thumb_tip_gap_mm']} mm · "
                  f"符号+1 → {t['+1']['gap_mm']} mm · 符号−1 → {t['-1']['gap_mm']} mm "
                  f"⇒ 取 {row['chosen_sign']}（判据{'成立' if row['criterion_valid'] else '失效'}）")
            print(f"         中指尖位移 {t[row['chosen_sign']]['displacement_mm']} mm "
                  f"⇒ 掌面方向 {row['palm_direction_local']}（法向分量 {row['palm_normal_displacement_mm']} mm）")
        print("接触档 ε（骨原点 → 掌面，沿掌面法向）")
        for mesh_name, per_side in report["contact_epsilon"].items():
            for side, row in per_side.items():
                print(f"  [{mesh_name}] {side}Hand 掌面方向 {row['palm_direction']} ⇒ "
                      f"ε = {row['epsilon_mm']:.4f} mm （世界指向 {row['axis_in_world']}）")
    if any(report["part_faces"].values()):
        print("-" * 100)
        print("部位面 ε（语义 = 管线 §2.1.4 轴表 · 正负号 = 实测世界指向 vs 口径 §6.2）")
        for mesh_name, per_bone in report["part_faces"].items():
            for bone_name, faces in per_bone.items():
                for key, f in faces.items():
                    print(f"  [{mesh_name}] {bone_name:<24}{key:<12}{f['local_axis']:>4}"
                          f"  ε = {f['epsilon_mm']:>9.4f} mm  平坦支撑 {f['flat_support_vertices']:>4}"
                          f"  世界 {f['axis_in_world']}（与命名轴差 {f['angle_to_named_world_axis_deg']}°）")
    print("-" * 100)
    print("换算系检查（#164：法向必须与读数同系；后两列 = 「漏掉 arm.matrix_world」的代价）")
    print(f"  骨架 matrix_world 旋转 {report['frame_check']['armature_rotation_euler_deg']}° · "
          f"scale {report['frame_check']['armature_scale']} · "
          f"两条独立算路最大差 {report['frame_check']['route_identity_max_deg']}° · "
          f"rest 姿势下 pose.matrix == bone.matrix_local 最大差 "
          f"{report['frame_check']['rest_pose_matrix_identity_max_abs']}")
    for mesh_name, per_bone in report["frame_check"]["per_mesh"].items():
        for bone_name, fc in per_bone.items():
            for tag, row in fc["per_direction"].items():
                print(f"  [{mesh_name}] {bone_name:<24}{tag:>4}  两系夹角 {row['angle_between_frames_deg']:>7.4f}°"
                      f" · 位移差 {row['misplacement_vector_mm']:>9.4f} mm"
                      f" · 沿正确法向差 {row['misplacement_along_correct_mm']:>9.4f} mm"
                      f"{'  ← 不动轴（#163 的巧合）' if row['on_rotation_invariant_axis'] else ''}")
    print("-" * 100)
    print("稳定性（跨姿势跟踪静止时选出的最外顶点，相对本骨的局部偏移变化）")
    for mesh_name, s in stab.items():
        print(f"[{mesh_name}]")
        for pose_name, rows in s["per_pose"].items():
            if not rows:
                continue
            worst = max(rows.items(), key=lambda kv: kv[1]["max_delta_mm"])
            print(f"  {pose_name:<14} 全骨最大变化 {worst[1]['max_delta_mm']:>9.6f} mm"
                  f"  @ {worst[0]} ({worst[1]['worst_direction']})")
    print("=" * 100)

    report["ok"] = not report["problems"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print(f"报告：{report_path}")
    if report["problems"]:
        for p in report["problems"][:5]:
            print("  ⚠️ " + p)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
