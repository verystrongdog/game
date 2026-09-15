#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 verystrongdog
# SPDX-License-Identifier: GPL-3.0-or-later
"""measure_xbot_surface_offset.py —— 实测手部「骨 → 蒙皮表面」偏移（口径 §八 的接触档 ε）。

来源：design/presentation/动作描述口径.md §八（容差 ε 口径 = "骨 → 蒙皮表面"实测偏移）
      · design/engineering/issue-process.md §4.1.1（参数来源）
      · 先例：`FootGroundingIK.cs` 的 `soleMargin = 0.0028 m`——2026-09-12 bind pose 趾骨 Y 的实测值，
        同属"骨在蒙皮里，蒙皮表面才是几何实体"这一类量

为什么需要它
------------
"手掌贴合椅背上方"这类需求，判据落在**蒙皮表面**上；而 agent 手上的读数一律是**骨端点**。
两者之差不是一个可以拍的常数——它随骨、随蒙皮、随方向而异。本脚本把它**测出来**，
于是"贴合"可以从"只报读数、由 owner 目视判"升级为"读数 + 有来源的 ε"。

测什么（三层）
--------------
1. **表面剖面**：对每根手部/手指骨，取其**主导组就是该骨**的顶点，在**该骨静止局部系**里量
   6 个方向（±X/±Y/±Z）的**最外沿距离**（骨原点 → 最外顶点）。这就是"往哪个方向有多厚"。
2. **平坦面支撑数**：每个方向上落在极值面 2 mm 内的顶点数——用来**判掌面朝哪一侧**
   （大平面 ⇒ 支撑数大）。掌面方向由数据定，不由本脚本猜。
3. **稳定性（本条的假设）**：在若干确定性姿势下，跟踪**静止姿势选出的那批最外顶点**，
   量它们相对该骨的局部偏移变化（mm）。问题就是："ε 是常数吗？"

⚠️ 两条 2026-09-14 实测教训（都踩过，都已改）
--------------------------------------------
- **单位**：母版是 Mixamo **厘米制** + Armature 对象 `scale = 0.01`（管线 §二 ⚠️ 块）。
  骨矩阵与网格数据都在**骨架局部单位（= 1 cm）**里，故米制换算 = `× 对象 scale`。
  第一版按"米"直接 `× 1000`，量出"手的外沿 **3–10 米**"——**量级自证**就足以当场否掉这个读数。
- **取样门槛不能是"权重 ≥ 0.999"**：线性混合蒙皮（LBS）下权重 = 1 的顶点相对其骨**恒为常数**，
  用它们做样本，稳定性判据必然 0 mm ——**平凡通过**（本仓记过同类教训：管线 §三 V8 的由来）。
  故成员判据取**主导组（argmax）**，权重只作报告量；表面那层混合权重顶点才是会滑动的那批。

用法
----
    blender --background --factory-startup --python-exit-code 1 \\
        --python code/tools/measure_xbot_surface_offset.py -- \\
        --template <.blend> [--report <.json>]

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
#: 目标骨：两手 + 每侧 20 根手指骨（骨表里的 `Hand*` 族，共 42 根）
HAND_ROOTS = ("mixamorig:LeftHand", "mixamorig:RightHand")
FINGERS = ("Thumb", "Index", "Middle", "Ring", "Pinky")
FINGER_SEGMENTS = (1, 2, 3, 4)
#: 方向：静止局部系的 ±X / ±Y / ±Z
DIRECTIONS = (("+X", (1, 0, 0)), ("-X", (-1, 0, 0)),
              ("+Y", (0, 1, 0)), ("-Y", (0, -1, 0)),
              ("+Z", (0, 0, 1)), ("-Z", (0, 0, -1)))
#: "平坦面"片层厚度（米）——落在极值面这么薄一层里的顶点算作支撑
FLAT_SLAB_M = 0.002
#: 量级自证上限：单根手部骨的表面外沿不该超过这个值（米）。超过 ⇒ 单位或成员判据出错
PLAUSIBLE_MAX_M = 0.30
#: 确定性姿势表（只动控制骨；控制骨经约束驱动变形骨，读数走 evaluated depsgraph）
POSES = (
    ("rest", {}),
    ("wrist_bend", {"CTRL_LeftHand": (40.0, 0.0, 0.0), "CTRL_RightHand": (40.0, 0.0, 0.0)}),
    ("elbow+wrist", {"CTRL_LeftForeArm": (0.0, 0.0, 30.0), "CTRL_LeftHand": (0.0, 20.0, 0.0),
                     "CTRL_RightForeArm": (0.0, 0.0, 30.0), "CTRL_RightHand": (0.0, 20.0, 0.0)}),
    ("arms_down", {"CTRL_LeftArm": (35.0, 0.0, 0.0), "CTRL_RightArm": (35.0, 0.0, 0.0)}),
)


def parse_args(argv):
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser(prog="measure_xbot_surface_offset.py")
    ap.add_argument("--template", default=str(Path(__file__).resolve().parents[2] /
                                             ".scratch/blender_assets/xbot/XBot_AnimationTemplate.blend"))
    ap.add_argument("--report", default=None)
    return ap.parse_args(argv)


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


def apply_pose(arm, spec):
    reset_pose(arm)
    for name, (rx, ry, rz) in spec.items():
        pb = arm.pose.bones.get(name)
        if pb is None:
            raise RuntimeError(f"控制骨不存在：{name}")
        if pb.rotation_mode == "QUATERNION":
            raise RuntimeError(f"{name} 的 rotation_mode 是 QUATERNION——本脚本不改模式（管线 §2.1 红线 1）")
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




def main() -> int:
    args = parse_args(list(sys.argv))
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

    bones = list(HAND_ROOTS) + [
        f"{BONE_PREFIX}{side}Hand{f}{seg}"
        for side in ("Left", "Right") for f in FINGERS for seg in FINGER_SEGMENTS]

    report = {
        "script": "measure_xbot_surface_offset.py",
        "blender": bpy.app.version_string,
        "template": str(tmpl),
        "armature": arm.name,
        "armature_scale": [round(s, 6) for s in arm_scale],
        "local_units_per_meter": round(1.0 / local_to_m, 6) if local_to_m else None,
        "flat_slab_m": FLAT_SLAB_M,
        "plausible_max_m": PLAUSIBLE_MAX_M,
        "poses": [name for name, _ in POSES],
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
            vg = mesh_obj.vertex_groups.get(bone_name)
            if bone_name not in arm.data.bones or vg is None:
                continue
            pairs = dominant_set(mesh_obj, bone_name)
            if not pairs:
                entry["bones"][bone_name] = {"sampled": 0}
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
        for pose_name, spec in POSES:
            apply_pose(arm, spec)
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

    # ---------- 4. 掌面朝向（屈曲方向）与接触档 ε ----------
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

    # ---------- 打印 ----------
    print("=" * 100)
    print(f"母版 {tmpl}")
    print(f"Blender {report['blender']} · 骨架 scale {report['armature_scale']} "
          f"(1 单位 = {local_to_m * 1000:.4f} mm) · 网格 {list(report['meshes'])}")
    print(f"姿势表 {report['poses']} · 平坦片层 {FLAT_SLAB_M * 1000:.1f} mm")
    print("-" * 100)
    for mesh_name, entry in report["per_mesh"].items():
        print(f"[{mesh_name}] 顶点 {entry['vertices']}")
        print(f"{'骨':<34}{'方向':>4}{'外沿(mm)':>12}{'平坦支撑':>10}  世界指向")
        for bone_name, row in entry["bones"].items():
            if not row.get("sampled"):
                continue
            if bone_name not in HAND_ROOTS:
                continue
            for tag, _ in DIRECTIONS:
                p = row["profile"][tag]
                ax = p["axis_in_world"]
                print(f"{bone_name:<34}{tag:>4}{p['outer_mm']:>12.4f}{p['flat_support_vertices']:>10}"
                      f"  ({ax[0]:+.3f}, {ax[1]:+.3f}, {ax[2]:+.3f})")
            print(f"{'':<34}取样 {row['sampled']} 顶点 · 该骨权重 min/中位/max = "
                  f"{row['own_weight']['min']}/{row['own_weight']['median']}/{row['own_weight']['max']}")
        fingers = [b for b in entry["bones"] if b not in HAND_ROOTS and entry["bones"][b].get("sampled")]
        print(f"  （另有 {len(fingers)} 根手指骨有读数，逐根明细见 JSON）")
    print("-" * 100)
    print("掌面朝向（判据：四指屈曲把中指尖带向拇指尖 ⇒ 该位移方向 = 掌面法向）")
    for side, row in palm.items():
        t = row["trials"]
        print(f"  {side:<6} 静止拇中尖距 {row['rest_thumb_tip_gap_mm']} mm · "
              f"符号+1 → {t['+1']['gap_mm']} mm · 符号−1 → {t['-1']['gap_mm']} mm "
              f"⇒ 取 {row['chosen_sign']}（判据{'成立' if row['criterion_valid'] else '失效'}）")
        print(f"         中指尖位移 {t[row['chosen_sign']]['displacement_mm']} mm "
              f"⇒ 掌面方向 {row['palm_direction_local']}（法向分量 {row['palm_normal_displacement_mm']} mm）")
    print("接触档 ε（骨原点 → 掌面，沿掌面法向）")
    for mesh_name, per_side in contact.items():
        for side, row in per_side.items():
            print(f"  [{mesh_name}] {side}Hand 掌面方向 {row['palm_direction']} ⇒ ε = {row['epsilon_mm']:.4f} mm "
                  f"（世界指向 {row['axis_in_world']}）")
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
