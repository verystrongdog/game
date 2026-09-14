#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""measure_xbot_control_axes.py —— 实测母版里每根控制骨的**局部轴向语义**。

来源：design/presentation/Blender动作制作管线.md §2.1.1（表）/ §7.4（口径）

为什么需要它
------------
"绕局部 X 转一点"对每根骨意味着什么，**读代码读不出来**：它取决于该骨在静止姿势下的
局部轴朝向，而那套朝向在 Mixamo 骨架上**左右并不统一**（实测：髋/膝/踝左右完全同轴，
肩/肘/腕左右镜像）。凭直觉调会得到"转了但动作不对/左右不镜像"的结果，且很难归因。

本脚本绕每根控制骨的每个局部轴各转 `--deg`（默认 20°），量两处位移：
  · **本骨骨尖**——看这个关节本身动没动；
  · **链末标志点**——腿看趾尖 · 臂看指尖 · 骨盆看头顶与左手。
    ⚠️ 只看本骨会漏掉**扭转**：局部 Y 是沿骨轴的扭转，本骨骨尖在轴上、位移**恒为 0**，
    但不代表这根轴没用（骨盆扭转会带动双臂 278 mm，见 §2.1.1）。

用法
----
    blender --background --factory-startup --python-exit-code 1 \\
        --python code/tools/measure_xbot_control_axes.py -- \\
        --template <.blend> [--deg 20] [--report <json>]

版本：Blender 4.5 / 5.x 均可（本脚本不碰 Action API，故无需 `blender_action_compat`）。
"""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

BONE_PREFIX = "mixamorig:"
CTRL_PREFIX = "CTRL_"

#: 每根控制骨的**链末标志点**——"转这根骨，人身上哪个位置动得最明显"
DISTAL_LANDMARKS = {
    "CTRL_Hips": "mixamorig:HeadTop_End",
    "CTRL_LeftUpLeg": "mixamorig:LeftToeBase",
    "CTRL_LeftLeg": "mixamorig:LeftToeBase",
    "CTRL_LeftFoot": "mixamorig:LeftToeBase",
    "CTRL_RightUpLeg": "mixamorig:RightToeBase",
    "CTRL_RightLeg": "mixamorig:RightToeBase",
    "CTRL_RightFoot": "mixamorig:RightToeBase",
    "CTRL_LeftArm": "mixamorig:LeftHand",
    "CTRL_LeftForeArm": "mixamorig:LeftHand",
    "CTRL_LeftHand": "mixamorig:LeftHand",
    "CTRL_RightArm": "mixamorig:RightHand",
    "CTRL_RightForeArm": "mixamorig:RightHand",
    "CTRL_RightHand": "mixamorig:RightHand",
}

#: 偏轴标志点：专治"扭转看不见"（骨盆转身看手、臂扭转看指尖、腿旋看趾尖）
OFF_AXIS_LANDMARKS = {
    "CTRL_Hips": ("mixamorig:LeftHand", "mixamorig:LeftHandMiddle4"),
    "CTRL_LeftUpLeg": ("mixamorig:LeftToe_End",),
    "CTRL_RightUpLeg": ("mixamorig:RightToe_End",),
    "CTRL_LeftArm": ("mixamorig:LeftHandMiddle4",),
    "CTRL_RightArm": ("mixamorig:RightHandMiddle4",),
}


def parse_args(argv):
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser(prog="measure_xbot_control_axes.py")
    ap.add_argument("--template", default=str(Path(__file__).resolve().parents[2] /
                                             ".scratch/blender_assets/xbot/XBot_AnimationTemplate.blend"))
    ap.add_argument("--deg", type=float, default=20.0)
    ap.add_argument("--group", choices=("control", "deform", "both"), default="control",
                    help="control=13 根控制骨（§2.1.1 既有表）· deform=无约束变形骨（§2.1.4 新表）· both=两组都测")
    ap.add_argument("--report", default=None)
    return ap.parse_args(argv)


def armature_object():
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(arms) != 1:
        raise RuntimeError(f"期望恰好 1 个 Armature，实测 {len(arms)}")
    return arms[0]


def world_point(arm_obj, bone_name):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm_obj.evaluated_get(dg)
    return ev.matrix_world @ ev.pose.bones[bone_name].tail


def reset_pose(arm_obj):
    """归零姿势。

    ⚠️ **每量一个轴之前都必须先归零**：否则基准点会叠上"上一个轴/上一根骨"的残留，
    算出来的位移凭空多出一个与骨长同量级的分量（实测踩到：左腿凭空多出 170 mm 侧向位移，
    差点把"左右不镜像"这个**错误**结论写进文档）。
    """
    for pb in arm_obj.pose.bones:
        if pb.rotation_mode == "QUATERNION":
            pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        else:
            pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()


def body_frame(arm_obj):
    """身体坐标系（**解剖定义**，不猜）：左腿方向 / 脚尖方向 / 髋→头。"""
    reset_pose(arm_obj)
    up = (world_point(arm_obj, "mixamorig:Head") - world_point(arm_obj, "mixamorig:Hips")).normalized()
    left = world_point(arm_obj, "mixamorig:LeftUpLeg") - world_point(arm_obj, "mixamorig:RightUpLeg")
    left = (left - up * left.dot(up)).normalized()
    fwd_raw = world_point(arm_obj, "mixamorig:LeftToeBase") - world_point(arm_obj, "mixamorig:LeftFoot")
    fwd = (fwd_raw - up * fwd_raw.dot(up)).normalized()
    return left, fwd, up


def body_frame(arm_obj):
    """身体坐标系（**解剖定义**，不猜）：左腿方向 / 脚尖方向 / 髋→头。"""
    reset_pose(arm_obj)
    up = (world_point(arm_obj, "mixamorig:Head") - world_point(arm_obj, "mixamorig:Hips")).normalized()
    left = world_point(arm_obj, "mixamorig:LeftUpLeg") - world_point(arm_obj, "mixamorig:RightUpLeg")
    left = (left - up * left.dot(up)).normalized()
    fwd_raw = world_point(arm_obj, "mixamorig:LeftToeBase") - world_point(arm_obj, "mixamorig:LeftFoot")
    fwd = (fwd_raw - up * fwd_raw.dot(up)).normalized()
    return left, fwd, up


# ---------------------------------------------------------------- 无约束变形骨（§2.1.4，issue #161）

#: 目标 = 52 根无约束变形骨里**除 40 根手指**之外的全部（3 脊柱 + 3 头颈 + 2 肩 + 4 脚趾 = 12 根）
#: 手指另议：上一轮的屈曲轴是脚本自测的，且其符号存在待裁定分歧（见 #160 证据 §六.2）
DEFORM_TARGETS = (
    "mixamorig:Spine", "mixamorig:Spine1", "mixamorig:Spine2",
    "mixamorig:Neck", "mixamorig:Head", "mixamorig:HeadTop_End",
    "mixamorig:LeftShoulder", "mixamorig:RightShoulder",
    "mixamorig:LeftToeBase", "mixamorig:LeftToe_End",
    "mixamorig:RightToeBase", "mixamorig:RightToe_End",
)

#: 链末标志点 = 该骨最远的下游骨尖（"转这根骨，人身上哪个位置动得最明显"）
DEFORM_DISTAL = {
    "mixamorig:Spine": "mixamorig:HeadTop_End",
    "mixamorig:Spine1": "mixamorig:HeadTop_End",
    "mixamorig:Spine2": "mixamorig:HeadTop_End",
    "mixamorig:Neck": "mixamorig:HeadTop_End",
    "mixamorig:Head": "mixamorig:HeadTop_End",
    "mixamorig:HeadTop_End": None,          # 叶骨：无下游
    "mixamorig:LeftShoulder": "mixamorig:LeftHand",
    "mixamorig:RightShoulder": "mixamorig:RightHand",
    "mixamorig:LeftToeBase": "mixamorig:LeftToe_End",
    "mixamorig:LeftToe_End": None,
    "mixamorig:RightToeBase": "mixamorig:RightToe_End",
    "mixamorig:RightToe_End": None,
}

#: 偏轴标志点 = 专治"扭转看不见"（沿骨轴的扭转对本骨骨尖位移恒为 0，见 §7.4 实测）
DEFORM_OFF_AXIS = {
    "mixamorig:Spine": ("mixamorig:LeftHand", "mixamorig:RightHand"),
    "mixamorig:Spine1": ("mixamorig:LeftHand", "mixamorig:RightHand"),
    "mixamorig:Spine2": ("mixamorig:LeftHand", "mixamorig:RightHand"),
    "mixamorig:Neck": (),                    # 颈的下游只有 Head→HeadTop_End，均在轴上
    "mixamorig:Head": (),                    # 头同理
    "mixamorig:LeftShoulder": ("mixamorig:LeftHand",),
    "mixamorig:RightShoulder": ("mixamorig:RightHand",),
    "mixamorig:LeftToeBase": ("mixamorig:LeftToe_End",),
    "mixamorig:RightToeBase": ("mixamorig:RightToe_End",),
}


def skinned_meshes(arm_obj):
    """被该骨架蒙皮的网格（母版里的 REF_* 参考代理没有 Armature 修改器，排除）。"""
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        if any(m.type == "ARMATURE" and m.object == arm_obj for m in o.modifiers):
            out.append(o)
    return sorted(out, key=lambda o: o.name)


def mesh_positions(meshes):
    """evaluated depsgraph 下每个蒙皮网格的顶点世界坐标。"""
    dg = bpy.context.evaluated_depsgraph_get()
    out = {}
    for o in meshes:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world
        out[o.name] = [mw @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    return out


def measure_deform_group(arm_obj, left, fwd, up, deg):
    """量 12 根无约束变形骨：绕各自**局部轴** +deg 后，四处可观察量各动了多少。

    为什么比 §2.1.1 多一列**蒙皮位移**：头 / 颈 / 趾这类骨的扭转**在任何骨尖上都看不见**
    （下游骨与本骨共线、叶骨干脆没有下游），只有蒙皮会动。只量骨尖会把"这根轴没用"
    这个**错误**结论写进文档——§7.4 已经为控制骨记过一次同类教训。
    """
    def decompose(vec):
        return {"mm": round(vec.length, 1), "侧": round(vec.dot(left), 1),
                "前": round(vec.dot(fwd), 1), "上": round(vec.dot(up), 1)}

    meshes = skinned_meshes(arm_obj)
    original_modes = {pb.name: pb.rotation_mode for pb in arm_obj.pose.bones}

    reset_pose(arm_obj)
    rest_mesh = mesh_positions(meshes)
    # 噪声底：同一姿势再求值一次，最大差即本测量的精度地板（不拍阈值，量出来）
    noise = 0.0
    for name, pts in mesh_positions(meshes).items():
        for a, b in zip(pts, rest_mesh[name]):
            noise = max(noise, (a - b).length)
    noise_mm = noise * 1000.0

    rows = []
    for bone_name in DEFORM_TARGETS:
        bone = arm_obj.data.bones.get(bone_name)
        if bone is None:
            rows.append({"bone": bone_name, "error": "骨不存在"})
            continue
        distal = DEFORM_DISTAL.get(bone_name)
        off_names = DEFORM_OFF_AXIS.get(bone_name, ())
        cells = {}
        for axis_i, axis in enumerate("XYZ"):
            reset_pose(arm_obj)                                    # 基准必须在归零之后取
            pb = arm_obj.pose.bones[bone_name]
            base_tip = world_point(arm_obj, bone_name)
            base_dst = world_point(arm_obj, distal) if distal else None
            base_off = {n: world_point(arm_obj, n) for n in off_names}
            pb.rotation_mode = "XYZ"
            e = [0.0, 0.0, 0.0]
            e[axis_i] = math.radians(deg)
            pb.rotation_euler = Euler(e, "XYZ")
            bpy.context.view_layer.update()

            tip = decompose((world_point(arm_obj, bone_name) - base_tip) * 1000.0)
            dst = decompose((world_point(arm_obj, distal) - base_dst) * 1000.0) if distal else None
            off = {n: round((world_point(arm_obj, n) - base_off[n]).length * 1000.0, 1) for n in off_names}
            posed = mesh_positions(meshes)
            skin = {}
            for mesh_name, pts in posed.items():
                worst, widx, wvec = 0.0, None, Vector((0.0, 0.0, 0.0))   # 蒙皮完全不动时要有个零向量
                for i, p in enumerate(pts):
                    d = (p - rest_mesh[mesh_name][i])
                    if d.length > worst:
                        worst, widx, wvec = d.length, i, d
                skin[mesh_name] = {"max_mm": round(worst * 1000.0, 2), "vertex": widx,
                                   "direction": decompose(wvec * 1000.0)}
            bone_only = max([tip["mm"]] + ([dst["mm"]] if dst else []) + list(off.values()))
            skin_only = max(v["max_mm"] for v in skin.values())
            observable_mm = max(bone_only, skin_only)
            # 可观察性按"动了没动"判——噪声底是**实测**的（本次 0.000000 mm），故不设人为阈值
            visible = observable_mm > 0.0
            cells[axis] = {"tip": tip, "distal": dst, "off_axis": off, "skin": skin,
                           "observable_mm": round(observable_mm, 2),
                           "bone_only_observable": round(bone_only, 2),
                           "skin_max_mm": round(skin_only, 2),
                           "visible": bool(visible),
                           "only_skin_visible": bool(visible and bone_only == 0.0)}
        rows.append({"bone": bone_name, "distal": distal, "off_axis": list(off_names),
                     "children": [c.name for c in bone.children], "axes": cells})

    for pb in arm_obj.pose.bones:                                  # 还原 rotation_mode（虽不入库，保持干净）
        pb.rotation_mode = original_modes[pb.name]
    reset_pose(arm_obj)
    return rows, noise_mm


def main() -> int:
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    out = Path(args.report) if args.report else tmpl.parent / "control_axes.json"
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}\n        先跑 build_xbot_animation_template.py")
        return 2

    bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    arm_obj = armature_object()
    left, fwd, up = body_frame(arm_obj)

    driven = {}
    for pb in arm_obj.pose.bones:
        for c in pb.constraints:
            if c.type == "COPY_ROTATION" and c.subtarget:
                driven[c.subtarget] = pb.name
    ctrls = sorted(n for n in driven if n.startswith(CTRL_PREFIX))
    want_control = args.group in ("control", "both")
    want_deform = args.group in ("deform", "both")
    if want_control and not ctrls:
        print("[ERROR] 母版里没有 CTRL_* 控制骨（母版不对？）")
        return 3

    def decompose(vec):
        return {"mm": round(vec.length, 1), "侧": round(vec.dot(left), 1),
                "前": round(vec.dot(fwd), 1), "上": round(vec.dot(up), 1)}

    rows = []
    for ctrl in (ctrls if want_control else []):
        target = driven[ctrl]
        distal = DISTAL_LANDMARKS.get(ctrl, target)
        cells = {}
        for axis_i, axis in enumerate("XYZ"):
            reset_pose(arm_obj)                                   # 基准必须在归零之后取
            base_tip, base_dst = world_point(arm_obj, target), world_point(arm_obj, distal)
            base_off = {n: world_point(arm_obj, n) for n in OFF_AXIS_LANDMARKS.get(ctrl, ())}
            pb = arm_obj.pose.bones[ctrl]
            pb.rotation_mode = "XYZ"
            e = [0.0, 0.0, 0.0]
            e[axis_i] = math.radians(args.deg)
            pb.rotation_euler = Euler(e, "XYZ")
            bpy.context.view_layer.update()
            cells[axis] = {
                "tip": decompose((world_point(arm_obj, target) - base_tip) * 1000.0),
                "distal": decompose((world_point(arm_obj, distal) - base_dst) * 1000.0),
                "off_axis": {n: round((world_point(arm_obj, n) - base_off[n]).length * 1000.0, 1)
                             for n in base_off},
            }
        rows.append({"ctrl": ctrl, "driven": target, "distal": distal, "axes": cells})
    reset_pose(arm_obj)

    deform_rows, noise_mm = ([], None)
    if want_deform:
        deform_rows, noise_mm = measure_deform_group(arm_obj, left, fwd, up, args.deg)

    report = {"script": "measure_xbot_control_axes.py", "blender": bpy.app.version_string,
              "template": str(tmpl), "deg": args.deg, "group": args.group,
              "body_frame": {"left": [round(v, 4) for v in left],
                             "fwd": [round(v, 4) for v in fwd],
                             "up": [round(v, 4) for v in up]},
              "mesh_noise_floor_mm": (round(noise_mm, 6) if noise_mm is not None else None),
              "rows": rows,
              "deform_rows": deform_rows}
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print("=" * 104)
    print(f"母版: {tmpl}")
    print(f"Blender {bpy.app.version_string} · 每轴 +{args.deg:g}° · group={args.group} · "
          f"控制骨 {len(rows)} 根 · 无约束变形骨 {len(deform_rows)} 根")
    print(f"身体坐标系 left={[round(v,2) for v in left]} fwd={[round(v,2) for v in fwd]} "
          f"up={[round(v,2) for v in up]}")
    if deform_rows:
        print(f"蒙皮求值噪声底 {noise_mm:.6f} mm（同一姿势重求值一次的最大差——不拍阈值，量出来）")
        print("-" * 104)
        print(f"{'骨':<28}{'轴':>3}{'本骨骨尖':>10}{'链末':>9}{'偏轴max':>9}"
              f"{'蒙皮max':>10}{'骨架侧可观察':>13}  判定")
        for row in deform_rows:
            if row.get("error"):
                print(f"{row['bone']:<28} {row['error']}")
                continue
            for axis in "XYZ":
                c = row["axes"][axis]
                dst = f"{c['distal']['mm']:.2f}" if c["distal"] else "-"
                off = f"{max(c['off_axis'].values()):.2f}" if c["off_axis"] else "-"
                if not c["visible"]:
                    verdict = "不可观察（叶骨＋骨尖在轴上）"
                elif c["only_skin_visible"]:
                    verdict = "**仅蒙皮可见**"
                else:
                    verdict = "可观察"
                print(f"{row['bone']:<28}{axis:>3}{c['tip']['mm']:>10.2f}{dst:>9}{off:>9}"
                      f"{c['skin_max_mm']:>10.2f}{c['bone_only_observable']:>13.2f}  {verdict}")
        print("  判定三态：可观察 / **仅蒙皮可见**（骨尖与标志点全不动，只有蒙皮动）/ 不可观察（无任何可观察量动）")
    print(f"报告: {out}")
    print("=" * 104)
    return 0


if __name__ == "__main__":
    sys.exit(main())
