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
    if not ctrls:
        print("[ERROR] 母版里没有 CTRL_* 控制骨（母版不对？）")
        return 3

    def decompose(vec):
        return {"mm": round(vec.length, 1), "侧": round(vec.dot(left), 1),
                "前": round(vec.dot(fwd), 1), "上": round(vec.dot(up), 1)}

    rows = []
    for ctrl in ctrls:
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

    report = {"script": "measure_xbot_control_axes.py", "blender": bpy.app.version_string,
              "template": str(tmpl), "deg": args.deg,
              "body_frame": {"left": [round(v, 4) for v in left],
                             "fwd": [round(v, 4) for v in fwd],
                             "up": [round(v, 4) for v in up]},
              "rows": rows}
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print("=" * 78)
    print(f"母版: {tmpl}")
    print(f"Blender {bpy.app.version_string} · 每轴 +{args.deg:g}° · 控制骨 {len(rows)} 根")
    print(f"身体坐标系 left={[round(v,2) for v in left]} fwd={[round(v,2) for v in fwd]} "
          f"up={[round(v,2) for v in up]}")
    print(f"报告: {out}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
