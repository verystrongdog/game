#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""author_xbot_chair_grab.py —— 在母版上产出动作 `BendGripChairBack`（弯腰、双手抓住椅背）。

来源：design/presentation/Blender动作制作管线.md §八（动作素材：弯腰抓椅背）

它做什么
--------
1. 按 `ActionLabBuilder` 的**权威椅子常量**在母版里摆一张**参考椅**（`REF_Chair` 集合；
   只在母版里做参考与量测，**不会被导出**——导出是 `object_types={"ARMATURE"}` 的 animation-only）。
2. 用**临时 IK**（脚踩原地 + 双手到靠背顶杆）逐关键帧解姿势，再把解**捕获成控制骨角度**（IK 不落库）。
3. 手指没有控制骨 ⇒ 直接在手指变形骨上打键（导出烘焙会带上）；蜷曲轴由**自测**决定，不靠猜。
4. 逐关键帧复核：**去掉 IK 之后**再用捕获到的角度摆一遍，量手↔顶杆、脚↔静止位的残差。

为什么要"反解"而不是先定椅子位置
--------------------------------
实测（2026-09-14）：站椅子**正面**抓不到靠背顶杆——角色会被坐板挡在离坐面中心 0.522 m 处，
而顶杆还在坐面**另一侧** 0.44 m，只有指尖勉强蹭到。⇒ 站位只能是**椅子后方**（靠背朝角色），
而"椅子放多远"应当由**可达性**推出来（本脚本按任务空间给定弯腰角与骨盆位移，再解手臂）。

用法
----
    blender --background --factory-startup --python-exit-code 1 \\
        --python code/tools/author_xbot_chair_grab.py -- \\
        --template <.blend> [--action BendGripChairBack] [--chair 0.70] [--bend 55] [--force]
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
FINGER_CURL_DEG = {"Index": (60, 55, 40), "Middle": (60, 55, 40), "Ring": (60, 55, 40),
                   "Pinky": (60, 55, 40), "Thumb": (30, 25, 20)}


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

    d = chair_distance
    cube("REF_Seat", (0.0, -d, SEAT_TOP - SEAT_THICKNESS / 2),
         (SEAT_SIZE, SEAT_SIZE, SEAT_THICKNESS), (0.55, 0.36, 0.20))
    cube("REF_Back", (0.0, -d - (SEAT_SIZE / 2 + BACK_THICKNESS / 2), SEAT_TOP + BACK_HEIGHT / 2),
         (SEAT_SIZE, BACK_THICKNESS, BACK_HEIGHT), (0.45, 0.29, 0.16))
    leg_h = SEAT_TOP - SEAT_THICKNESS
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        cube("REF_Leg%d" % i, (sx * LEG_SPREAD, -d + sy * LEG_SPREAD, leg_h / 2),
             (LEG_SIZE, LEG_SIZE, leg_h), (0.42, 0.27, 0.15))


def rail_y(chair_distance):
    """靠背平面（朝角色那一面）的 y。椅子 forward = 坐者朝向 = −Y，故靠背在 +Y 侧。"""
    return -chair_distance + (SEAT_SIZE / 2 + BACK_THICKNESS / 2)


def rail_top_z():
    return SEAT_TOP + BACK_HEIGHT


# ---------------------------------------------------------------- 手指蜷曲轴自测


def detect_curl_axis(arm, side):
    """在 X / Z 两个候选轴里挑出"指尖朝掌心"效果更强的那个（含符号）。**不猜**。"""
    ref_bone = f"{BONE_PREFIX}{side}HandMiddle4"
    palm_bone = f"{BONE_PREFIX}{side}Hand"
    clear_pose(arm)
    base_tip = world_point(arm, ref_bone, "tail").copy()
    toward_palm = (world_point(arm, palm_bone, "head") - base_tip).normalized()
    best = None
    for axis_index, axis_name in ((0, "X"), (2, "Z")):
        for sign in (1, -1):
            clear_pose(arm)
            for finger in FINGERS:
                for k in (1, 2, 3):
                    name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
                    if name not in arm.pose.bones:
                        continue
                    degrees = FINGER_CURL_DEG[finger][k - 1] * sign
                    e = [0.0, 0.0, 0.0]
                    e[axis_index] = math.radians(degrees)
                    pb = arm.pose.bones[name]
                    pb.rotation_mode = "XYZ"
                    pb.rotation_euler = Euler(e, "XYZ")
            update()
            chord = world_point(arm, ref_bone, "tail") - base_tip
            score = chord.dot(toward_palm) * 1000.0
            if best is None or score > best[0]:
                best = (score, axis_name, sign)
    clear_pose(arm)
    return {"axis": best[1], "sign": best[2], "toward_palm_mm": round(best[0], 1)}


def apply_finger_curl(arm, side, curl_axis, amount):
    """`amount` 0..1 的蜷曲度；返回实际设定的骨骼数。"""
    n = 0
    for finger in FINGERS:
        for k in (1, 2, 3):
            name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
            if name not in arm.pose.bones:
                continue
            degrees = FINGER_CURL_DEG[finger][k - 1] * curl_axis["sign"] * amount
            e = [0.0, 0.0, 0.0]
            e[0 if curl_axis["axis"] == "X" else 2] = math.radians(degrees)
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler(e, "XYZ")
            n += 1
    return n


# ---------------------------------------------------------------- 捕获 IK 结果


def capture_basis(arm, names):
    """把**求值后**的姿势写回骨骼自身的通道（IK → FK 的捕获）。

    `pose_matrix = parent_pose @ parent_rest⁻¹ @ bone_rest @ basis` ⇒ `basis = (…)⁻¹ @ pose_matrix`
    （根骨没有父骨时退化为 `bone_rest⁻¹ @ pose_matrix`）。
    """
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm.evaluated_get(dg)
    out = {}
    for name in names:
        bone = arm.data.bones[name]
        pose_matrix = ev.pose.bones[name].matrix.copy()
        if bone.parent is not None:
            parent_pose = ev.pose.bones[bone.parent.name].matrix.copy()
            rest_chain = parent_pose @ bone.parent.matrix_local.inverted() @ bone.matrix_local
        else:
            rest_chain = bone.matrix_local.copy()
        basis = rest_chain.inverted() @ pose_matrix
        out[name] = {"euler_deg": [math.degrees(a) for a in basis.to_euler("XYZ")],
                     "location": list(basis.to_translation())}
    return out


def apply_captured(arm, captured, with_location=("CTRL_Hips",)):
    for name, data in captured.items():
        pb = arm.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler([math.radians(a) for a in data["euler_deg"]], "XYZ")
        pb.location = Vector(data["location"]) if name in with_location else Vector((0.0, 0.0, 0.0))
    update()


# ---------------------------------------------------------------- 主流程


def main() -> int:
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template)
    report_path = Path(args.report) if args.report else tmpl.parent / "chair_grab_report.json"
    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}")
        return 2

    bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    bpy.context.scene.render.fps = args.fps
    arm, m3 = make_context()
    build_chair_proxy(args.chair)
    ry, rz = rail_y(args.chair), rail_top_z()
    grip = {"Left": Vector((0.17, ry, rz + 0.045)), "Right": Vector((-0.17, ry, rz + 0.045))}
    report = {"script": "author_xbot_chair_grab.py", "blender": bpy.app.version_string,
              "template": str(tmpl), "action": args.action, "fps": args.fps,
              "chair_distance_m": args.chair, "rail_y": round(ry, 4), "rail_top_z": round(rz, 4),
              "problems": []}

    drop_temp(arm)
    clear_pose(arm)
    foot_rest = {s: world_point(arm, f"{BONE_PREFIX}{s}Foot").copy() for s in ("Left", "Right")}

    curl = {s: detect_curl_axis(arm, s) for s in ("Left", "Right")}
    report["finger_curl_axis"] = curl
    print(f"手指蜷曲轴自测：{curl}")

    # ---- 逐关键帧解算 ----
    ctrl_bones = [f"{CTRL_PREFIX}{n}" for n in
                  ("Hips", "LeftUpLeg", "LeftLeg", "LeftFoot", "RightUpLeg", "RightLeg", "RightFoot",
                   "LeftArm", "LeftForeArm", "LeftHand", "RightArm", "RightForeArm", "RightHand")]
    captured = {}
    for frame, bend, pelvis, hands_on_rail, curl_amount in SCHEDULE:
        clear_pose(arm)
        drop_temp(arm, also_objects=True)
        set_euler(arm, "CTRL_Hips", x=bend)
        set_world_offset(arm, m3, "CTRL_Hips", pelvis)
        if hands_on_rail:
            # ⚠️ 这两行只是**给手臂 IK 一个好起点**。**不能无条件加**——不加臂 IK 的帧
            #    （首帧 = 站立）会把预摆角度原样留在姿势里，于是"首帧不中立"，
            #    连带把导出的 bind pose 污染掉（实测：E5 报 69 m 偏差才发现）。
            for side, sgn in (("Left", 1), ("Right", -1)):
                set_euler(arm, f"CTRL_{side}Arm", z=sgn * 70)
                set_euler(arm, f"CTRL_{side}ForeArm", x=25)
        update()
        # 临时 IK：脚回静止位 + （到位前）手到顶杆
        foot_targets, hand_targets = {}, {}
        for side in ("Left", "Right"):
            ft = bpy.data.objects.new("TMP_Foot" + side, None)
            ft.location = foot_rest[side]
            bpy.context.scene.collection.objects.link(ft)
            foot_targets[side] = ft
            ik = arm.pose.bones[f"CTRL_{side}Leg"].constraints.new("IK")
            ik.name = "TMP_IK_leg"
            ik.target = ft
            ik.chain_count = 2
            if hands_on_rail:
                ht = bpy.data.objects.new("TMP_Hand" + side, None)
                ht.location = grip[side]
                bpy.context.scene.collection.objects.link(ht)
                hand_targets[side] = ht
                ik = arm.pose.bones[f"CTRL_{side}ForeArm"].constraints.new("IK")
                ik.name = "TMP_IK_arm"
                ik.target = ht
                ik.chain_count = 2
        update(12)
        if hands_on_rail:
            apply_finger_curl(arm, "Left", curl["Left"], curl_amount)
            apply_finger_curl(arm, "Right", curl["Right"], curl_amount)
            update()
        captured[frame] = capture_basis(arm, ctrl_bones)

    # ---- 去掉 IK，用捕获到的角度复演，逐帧复核 ----
    drop_temp(arm)
    verify = []
    for frame, bend, pelvis, hands_on_rail, curl_amount in SCHEDULE:
        clear_pose(arm)
        apply_captured(arm, captured[frame])
        if hands_on_rail:
            apply_finger_curl(arm, "Left", curl["Left"], curl_amount)
            apply_finger_curl(arm, "Right", curl["Right"], curl_amount)
        update()
        row = {"frame": frame, "bend_deg": bend}
        for side in ("Left", "Right"):
            hand = world_point(arm, f"{BONE_PREFIX}{side}Hand")
            tip = world_point(arm, f"{BONE_PREFIX}{side}HandMiddle4", "tail")
            row[f"hand_{side}_residual_mm"] = round((hand - grip[side]).length * 1000.0, 1) if hands_on_rail else None
            row[f"hand_{side}_m"] = [round(v, 4) for v in hand]
            row[f"fingertip_{side}_m"] = [round(v, 4) for v in tip]
            foot = world_point(arm, f"{BONE_PREFIX}{side}Foot")
            row[f"foot_{side}_drift_mm"] = round((foot - foot_rest[side]).length * 1000.0, 1)
            upper = world_point(arm, f"{BONE_PREFIX}{side}Arm")
            lower = world_point(arm, f"{BONE_PREFIX}{side}ForeArm")
            row[f"elbow_{side}_deg"] = round(math.degrees((upper - lower).angle(hand - lower)), 1)
        row["head_z_m"] = round(world_point(arm, f"{BONE_PREFIX}Head").z, 4)
        row["hips_z_m"] = round(world_point(arm, f"{BONE_PREFIX}Hips").z, 4)
        verify.append(row)
    report["verify"] = verify

    last = verify[-1]
    if last["hand_Left_residual_mm"] is None or max(last["hand_Left_residual_mm"],
                                                    last["hand_Right_residual_mm"]) > 15.0:
        report["problems"].append(
            f"到位帧手↔顶杆残差 {last['hand_Left_residual_mm']} / {last['hand_Right_residual_mm']} mm > 15 mm")
    if max(row["foot_Left_drift_mm"] for row in verify) > 15.0 or \
       max(row["foot_Right_drift_mm"] for row in verify) > 15.0:
        report["problems"].append("关键帧上脚相对静止位漂移 > 15 mm（脚没踩住）")
    if not (120.0 <= last["elbow_Left_deg"] <= 170.0):
        report["problems"].append(f"到位帧肘角 {last['elbow_Left_deg']}° 不在自然区间 120–170°")

    # ---- 写动作 ----
    arm.animation_data_clear()
    ad = arm.animation_data_create()
    # ⚠️ `bpy.data.actions.new()` 遇到**同名**会**静默**建 `名字.001`，而旧动作仍留在文件里
    #    ⇒ 导出脚本按名字取到的是**旧动作**（实测：改完动作、导出结果却一模一样，E5 偏差逐位不变，
    #    才回头发现文件里有 `X` 与 `X.001` 两份）。重跑前先把同名/同前缀的旧动作清掉。
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

    for frame, bend, pelvis, hands_on_rail, curl_amount in SCHEDULE:
        bpy.context.scene.frame_set(frame)
        clear_pose(arm)
        apply_captured(arm, captured[frame])
        if hands_on_rail:
            apply_finger_curl(arm, "Left", curl["Left"], curl_amount)
            apply_finger_curl(arm, "Right", curl["Right"], curl_amount)
        update()
        for name in ctrl_bones:
            pb = arm.pose.bones[name]
            pb.rotation_mode = "XYZ"
            pb.keyframe_insert("rotation_euler", frame=frame)
        arm.pose.bones["CTRL_Hips"].keyframe_insert("location", frame=frame)
        for side in ("Left", "Right"):
            for finger in FINGERS:
                for k in (1, 2, 3):
                    name = f"{BONE_PREFIX}{side}Hand{finger}{k}"
                    if name in arm.pose.bones:
                        arm.pose.bones[name].keyframe_insert("rotation_euler", frame=frame)
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = SCHEDULE[0][0], SCHEDULE[-1][0]
    bpy.context.scene.frame_set(SCHEDULE[0][0])
    report["action_frames"] = [SCHEDULE[0][0], SCHEDULE[-1][0]]
    report["ok"] = not report["problems"]
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print("=" * 78)
    print(f"动作 {args.action} · 帧 {SCHEDULE[0][0]}–{SCHEDULE[-1][0]} @ {args.fps} fps")
    print(f"椅子：中心前方 {args.chair} m · 靠背顶杆 y={ry:.4f} z={rz:.4f}")
    print(f"{'帧':>4}{'弯腰':>7}{'手残差L/R(mm)':>20}{'脚漂移L/R(mm)':>20}{'肘角L':>8}{'头高':>8}")
    for row in verify:
        hl = "—" if row["hand_Left_residual_mm"] is None else f"{row['hand_Left_residual_mm']:.1f}/{row['hand_Right_residual_mm']:.1f}"
        print(f"{row['frame']:>4}{row['bend_deg']:>6.0f}°{hl:>20}"
              f"{row['foot_Left_drift_mm']:>10.1f}/{row['foot_Right_drift_mm']:<9.1f}"
              f"{row['elbow_Left_deg']:>7.1f}°{row['head_z_m']:>8.3f}")
    print(f"报告: {report_path}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    print("=" * 78)

    if not args.no_save:
        if not args.force and bpy.data.filepath and Path(bpy.data.filepath) == tmpl:
            pass          # 就地写入母版：动作与参考椅都归母版（再生母版会清掉，见管线文档 §八）
        bpy.ops.wm.save_as_mainfile(filepath=str(tmpl), compress=False)
        print(f"已写回母版：{tmpl}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
