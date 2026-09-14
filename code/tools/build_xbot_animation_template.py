#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_xbot_animation_template.py —— 从仓库 X Bot.fbx 生成 Blender 人体动作母版。

来源：design/presentation/Blender动作制作管线.md §二（母版契约）/§三（自检判据）
      code/unity/Assets/Mixamo/Characters/X Bot.fbx（输入载体，字节不改）

母版是什么
----------
一份 `.blend`：**原封不动的 mixamorig 骨架 + 蒙皮网格**，加一层**非变形控制骨 `CTRL_*`**，
控制骨经 Bone Constraint 驱动对应变形骨。动作在这层控制骨上做，导出时再把控制结果烘到
变形骨上（见 export_xbot_action.py），于是「Blender 里能调」与「Unity 里能复用」是同一套骨。

硬约束（本脚本每次运行都自检，不通过即非 0 退出）
------------------------------------------------
V1 输入 FBX 的 sha256 在运行前后一致（母版只读输入，不改字节）
V2 骨架仍是 65 根骨、单一根 `mixamorig:Hips`、全部名为 `mixamorig:*`
V3 保存并**重新打开** `.blend` 后，父子关系与 V2 逐条相同
V4 保存并重新打开后，Rest Pose（`matrix_local`）逐条相同
V5 所有 `CTRL_*` 骨 `use_deform == False`
V6 每根控制骨都能真实驱动它对应的变形骨（摆控制骨 → 读变形骨世界矩阵变化）
V7 母版携带探针动作 `RigRoundTripProbe`，且 13 根控制骨逐根有键
V8 探针动作**非退化**：Hips/双手/双脚在每个关键帧上的位移都 > V8_MIN_MOTION_MM

用法
----
    blender --background --factory-startup \\
        --python code/tools/build_xbot_animation_template.py -- [选项]

选项
----
    --input PATH    输入 FBX（默认 code/unity/Assets/Mixamo/Characters/X Bot.fbx）
    --out-dir DIR   输出目录（默认 <repo>/.scratch/blender_assets/xbot，被 gitignore）
    --force         允许覆盖已存在的 .blend（默认拒绝覆盖）
    --report PATH   自检报告 JSON 路径（默认 <out-dir>/build_report.json）

版本：本脚本 **Blender 4.5 LTS 与 5.x 双兼容**（差异收在 `blender_action_compat.py`）。
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blender_action_compat as bac          # noqa: E402  4.5 / 5.x 动作 API 取道层
from mathutils import Euler, Quaternion, Vector

# ---------------------------------------------------------------- 常量（皆有来源）

REPO_ROOT = Path(__file__).resolve().parents[2]

# 来源：code/unity/Assets/Mixamo/Characters/X Bot.fbx —— 实测 Import 后骨架根数/骨数
EXPECTED_BONE_COUNT = 65
EXPECTED_ROOT_BONE = "mixamorig:Hips"
BONE_PREFIX = "mixamorig:"

# 来源：既有 15 条 Mixamo 动画 FBX 实测帧率（design/presentation/Blender动作制作管线.md §二）
SCENE_FPS = 30

# GUI 可用性：骨骼集合名与控制骨配色（**只影响显示**，不进 FBX）
CTRL_COLLECTION = "CTRL"
DEFORM_COLLECTION = "MIXAMORIG"
CTRL_BONE_COLOR = "THEME04"

TEMPLATE_NAME = "XBot_AnimationTemplate"
PROBE_ACTION_NAME = "RigRoundTripProbe"

# 控制骨覆盖：骨盆 + 双腿（髋/膝/踝）+ 双臂（肩关节/肘/腕）——来源：#156 验收标准第 2 条
CTRL_PLAN = [
    # (控制骨名, 目标变形骨, 是否也复制位移)
    ("CTRL_Hips", "mixamorig:Hips", True),
    ("CTRL_LeftUpLeg", "mixamorig:LeftUpLeg", False),
    ("CTRL_LeftLeg", "mixamorig:LeftLeg", False),
    ("CTRL_LeftFoot", "mixamorig:LeftFoot", False),
    ("CTRL_RightUpLeg", "mixamorig:RightUpLeg", False),
    ("CTRL_RightLeg", "mixamorig:RightLeg", False),
    ("CTRL_RightFoot", "mixamorig:RightFoot", False),
    ("CTRL_LeftArm", "mixamorig:LeftArm", False),
    ("CTRL_LeftForeArm", "mixamorig:LeftForeArm", False),
    ("CTRL_LeftHand", "mixamorig:LeftHand", False),
    ("CTRL_RightArm", "mixamorig:RightArm", False),
    ("CTRL_RightForeArm", "mixamorig:RightForeArm", False),
    ("CTRL_RightHand", "mixamorig:RightHand", False),
]

# 控制骨之间的父子关系（另起一条平行链，不插进 mixamorig 链）
CTRL_PARENT = {
    "CTRL_Hips": None,
    "CTRL_LeftUpLeg": "CTRL_Hips",
    "CTRL_LeftLeg": "CTRL_LeftUpLeg",
    "CTRL_LeftFoot": "CTRL_LeftLeg",
    "CTRL_RightUpLeg": "CTRL_Hips",
    "CTRL_RightLeg": "CTRL_RightUpLeg",
    "CTRL_RightFoot": "CTRL_RightLeg",
    "CTRL_LeftArm": "CTRL_Hips",
    "CTRL_LeftForeArm": "CTRL_LeftArm",
    "CTRL_LeftHand": "CTRL_LeftForeArm",
    "CTRL_RightArm": "CTRL_Hips",
    "CTRL_RightForeArm": "CTRL_RightArm",
    "CTRL_RightHand": "CTRL_RightForeArm",
}

# 控制骨驱动判据：绕本骨局部 X 轴摆 25° 后，目标变形骨的**骨尖**位移必须超过该阈值
CTRL_DRIVE_TEST_DEG = 25.0
CTRL_DRIVE_MIN_MM = 20.0

# 探针动作关键帧：{帧: {控制骨: (绕局部 XYZ 的角度, 骨架局部单位下的位移)}}
# ⚠️ 位移的单位是**骨架局部单位**，不是米：本骨架是 Mixamo 的厘米制 + Armature 对象 scale=0.01，
#    所以 1 单位 = 1 cm = 10 mm 世界。写成"米"会让骨盆位移小 100 倍（2026-09-14 实测：20 mm 写成
#    0.02 → 实际只动了 0.2 mm，被 V8 拦下）。
# 只求"覆盖骨盆/双腿/双臂且姿势可读"，不求动作审美——来源：#156「明确排除」最后一条
PROBE_FRAMES = (1, 21, 41, 61)
PROBE_KEYS = {
    1: {},
    21: {
        "CTRL_Hips": ((0.0, 0.0, 0.0), (0.0, 2.5, 0.0)),
        "CTRL_LeftUpLeg": ((28.0, 0.0, 0.0), None),
        "CTRL_LeftLeg": ((-22.0, 0.0, 0.0), None),
        "CTRL_LeftFoot": ((10.0, 0.0, 0.0), None),
        "CTRL_RightUpLeg": ((-16.0, 0.0, 0.0), None),
        "CTRL_RightLeg": ((-6.0, 0.0, 0.0), None),
        "CTRL_RightFoot": ((4.0, 0.0, 0.0), None),
        "CTRL_LeftArm": ((26.0, 0.0, 0.0), None),
        "CTRL_LeftForeArm": ((-18.0, 0.0, 0.0), None),
        "CTRL_LeftHand": ((0.0, 0.0, 12.0), None),
        "CTRL_RightArm": ((-32.0, 0.0, 0.0), None),
        "CTRL_RightForeArm": ((-36.0, 0.0, 0.0), None),
        "CTRL_RightHand": ((0.0, 0.0, -14.0), None),
    },
    41: {
        "CTRL_Hips": ((0.0, 0.0, 6.0), (0.0, -1.5, 0.0)),
        "CTRL_LeftUpLeg": ((-16.0, 0.0, 0.0), None),
        "CTRL_LeftLeg": ((-6.0, 0.0, 0.0), None),
        "CTRL_LeftFoot": ((4.0, 0.0, 0.0), None),
        "CTRL_RightUpLeg": ((28.0, 0.0, 0.0), None),
        "CTRL_RightLeg": ((-22.0, 0.0, 0.0), None),
        "CTRL_RightFoot": ((10.0, 0.0, 0.0), None),
        "CTRL_LeftArm": ((-32.0, 0.0, 0.0), None),
        "CTRL_LeftForeArm": ((-36.0, 0.0, 0.0), None),
        "CTRL_LeftHand": ((0.0, 0.0, -14.0), None),
        "CTRL_RightArm": ((26.0, 0.0, 0.0), None),
        "CTRL_RightForeArm": ((-18.0, 0.0, 0.0), None),
        "CTRL_RightHand": ((0.0, 0.0, 12.0), None),
    },
    61: {},
}


# ---------------------------------------------------------------- 小工具


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def matrix_fingerprint(mat) -> list:
    return [round(v, 6) for row in mat for v in row]


def armature_object() -> bpy.types.Object:
    arms = [ob for ob in bpy.data.objects if ob.type == "ARMATURE"]
    if len(arms) != 1:
        raise RuntimeError(f"期望恰好 1 个 Armature 对象，实测 {len(arms)}：{[o.name for o in arms]}")
    return arms[0]


def rest_fingerprint(arm_obj: bpy.types.Object) -> dict:
    """骨架的「名称 + 父子 + Rest Pose」指纹——V2/V3/V4 的比较对象。"""
    arm = arm_obj.data
    return {
        b.name: {
            "parent": b.parent.name if b.parent else None,
            "head_local": [round(v, 6) for v in b.head_local],
            "tail_local": [round(v, 6) for v in b.tail_local],
            # roll 不是 Bone 的属性，但它完全编码在 matrix_local 里 ⇒ 由 matrix_local 覆盖
            "matrix_local": matrix_fingerprint(b.matrix_local),
            "use_deform": b.use_deform,
        }
        for b in arm.bones
    }


def deform_fingerprint(fp: dict) -> dict:
    """只取 mixamorig 部分的指纹（控制骨是本脚本新增的，比对时要剔掉）。"""
    return {k: v for k, v in fp.items() if k.startswith(BONE_PREFIX)}


def bone_tip_world(arm_obj: bpy.types.Object, bone_name: str) -> Vector:
    """骨尖（tail）在 armature 对象空间的坐标——姿势求值走 evaluated depsgraph。"""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm_obj.evaluated_get(dg)
    pb = ev.pose.bones[bone_name]
    return ev.matrix_world @ pb.tail


def reset_pose(arm_obj: bpy.types.Object) -> None:
    """归零姿势。

    ⚠️ **不得改 `rotation_mode`**：控制骨的探针动作是 `rotation_euler` 通道，模式一旦被打回
    `QUATERNION`，那些关键帧就不再驱动姿势——症状是"母版看着正常、动作却是静止的"
    （2026-09-14 实测踩到：母版与导出物**同时**退化为静止姿势，于是烘焙保真/回导保真两条判据
    都**平凡通过**；由 V8/E0 的非退化判据拦下）。
    """
    for pb in arm_obj.pose.bones:
        if pb.rotation_mode == "QUATERNION":
            pb.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))
        else:
            pb.rotation_euler = Euler((0.0, 0.0, 0.0), pb.rotation_mode)
        pb.location = (0.0, 0.0, 0.0)
        pb.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()


# ---------------------------------------------------------------- 主流程


def parse_args(argv):
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    ap = argparse.ArgumentParser(prog="build_xbot_animation_template.py")
    ap.add_argument("--input", default=str(REPO_ROOT / "code/unity/Assets/Mixamo/Characters/X Bot.fbx"))
    ap.add_argument("--out-dir", default=str(REPO_ROOT / ".scratch/blender_assets/xbot"))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--report", default=None)
    return ap.parse_args(argv)


def import_source(fbx_path: Path) -> bpy.types.Object:
    """导入 X Bot.fbx。

    `use_anim=False`：母版不带源动画。理由是控制层用 Constraint 覆盖变形骨，若同时留着源
    action 的位移/缩放通道，同一根骨会有两个写者，读数无法归属（判据 §读数归属）。
    源动画仍可从 X Bot.fbx 取，不在母版里存第二份。
    """
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = SCENE_FPS
    bpy.ops.import_scene.fbx(filepath=str(fbx_path), use_anim=False)
    return armature_object()


def build_control_layer(arm_obj: bpy.types.Object) -> None:
    """新建非变形控制骨（同 head/tail/roll 的平行链）+ 驱动约束。"""
    arm = arm_obj.data
    bpy.context.view_layer.objects.active = arm_obj
    if arm_obj.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")

    # 需要先按拓扑序建骨，父骨必须已存在
    order = []

    def visit(name):
        p = CTRL_PARENT[name]
        if p is not None and p not in order:
            visit(p)
        order.append(name)

    for name, _, _ in CTRL_PLAN:
        visit(name)

    for ctrl_name, deform_name, _ in CTRL_PLAN:
        src = arm.edit_bones[deform_name]
        eb = arm.edit_bones.new(ctrl_name)
        eb.head = src.head.copy()
        eb.tail = src.tail.copy()
        eb.roll = src.roll
        eb.use_deform = False
        eb.use_connect = False
        ctrl_parent = CTRL_PARENT[ctrl_name]
        if ctrl_parent is not None:
            eb.parent = arm.edit_bones[ctrl_parent]

    # ---- GUI 可用性：控制骨与变形骨**完全重合**，不加点标记在视口里根本点不到 ----
    # 只动**显示层**（骨骼集合 / 配色 / 显示模式）：head/tail/roll 一字不改，故约束映射与导出物都不受影响。
    # ⚠️ 必须在 **EDIT 模式**下读 `arm.edit_bones`——在 OBJECT 模式下它是**空的**（实测踩到：变形骨集合 0 根）。
    ctrl_bones = [n for n, _, _ in CTRL_PLAN]
    deform_bones = [b.name for b in arm.edit_bones if b.name.startswith(BONE_PREFIX)]
    for coll in list(arm.collections):
        if coll.name in (CTRL_COLLECTION, DEFORM_COLLECTION):
            arm.collections.remove(coll)
    coll_ctrl = arm.collections.new(CTRL_COLLECTION)
    coll_deform = arm.collections.new(DEFORM_COLLECTION)
    for name in ctrl_bones:
        eb = arm.edit_bones[name]
        coll_ctrl.assign(eb)
        eb.color.palette = CTRL_BONE_COLOR
        if hasattr(eb, "display_type"):
            eb.display_type = "OCTAHEDRAL"
    for name in deform_bones:
        coll_deform.assign(arm.edit_bones[name])
    bpy.ops.object.mode_set(mode="OBJECT")
    # 集合默认可见：不改用户的显示习惯；要"只点控制骨"就把 DEFORM 集合关掉
    coll_ctrl.is_visible, coll_deform.is_visible = True, True

    # 控制骨的旋转模式固定为 XYZ 欧拉——探针动作写的是 rotation_euler 通道（见 reset_pose 的注）
    for ctrl_name, _, _ in CTRL_PLAN:
        arm_obj.pose.bones[ctrl_name].rotation_mode = "XYZ"

    # 约束：变形骨的旋转（骨盆另加位移）由控制骨接管
    for ctrl_name, deform_name, copy_location in CTRL_PLAN:
        pb = arm_obj.pose.bones[deform_name]
        for c in list(pb.constraints):
            pb.constraints.remove(c)
        rot = pb.constraints.new(type="COPY_ROTATION")
        rot.name = f"CTRL {ctrl_name}"
        rot.target = arm_obj
        rot.subtarget = ctrl_name
        rot.target_space = "LOCAL"
        rot.owner_space = "LOCAL"
        rot.mix_mode = "REPLACE"
        if copy_location:
            loc = pb.constraints.new(type="COPY_LOCATION")
            loc.name = f"CTRL {ctrl_name} loc"
            loc.target = arm_obj
            loc.subtarget = ctrl_name
            loc.target_space = "LOCAL"
            loc.owner_space = "LOCAL"


def verify_control_drive(arm_obj: bpy.types.Object) -> list:
    """V6：逐根控制骨摆 CTRL_DRIVE_TEST_DEG，量目标变形骨骨尖位移（mm）。"""
    rows = []
    reset_pose(arm_obj)
    base = {d: bone_tip_world(arm_obj, d) for _, d, _ in CTRL_PLAN}
    for ctrl_name, deform_name, _ in CTRL_PLAN:
        reset_pose(arm_obj)
        pb = arm_obj.pose.bones[ctrl_name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler((math.radians(CTRL_DRIVE_TEST_DEG), 0.0, 0.0), "XYZ")
        bpy.context.view_layer.update()
        moved = (bone_tip_world(arm_obj, deform_name) - base[deform_name]).length * 1000.0
        rows.append({"ctrl": ctrl_name, "deform": deform_name, "tip_delta_mm": round(moved, 4),
                     "ok": moved >= CTRL_DRIVE_MIN_MM})
    reset_pose(arm_obj)
    return rows


def author_probe_action(arm_obj: bpy.types.Object) -> None:
    """在控制骨上打关键帧，得到探针动作。"""
    arm_obj.animation_data_clear()
    ad = arm_obj.animation_data_create()
    act = bpy.data.actions.new(PROBE_ACTION_NAME)
    act.use_fake_user = True
    bac.assign_action(ad, act)

    for ctrl_name, _, _ in CTRL_PLAN:
        arm_obj.pose.bones[ctrl_name].rotation_mode = "XYZ"

    for frame in PROBE_FRAMES:
        bpy.context.scene.frame_set(frame)
        keys = PROBE_KEYS.get(frame, {})
        for ctrl_name, _, copy_location in CTRL_PLAN:
            pb = arm_obj.pose.bones[ctrl_name]
            rot, loc = keys.get(ctrl_name, ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
            pb.rotation_euler = Euler((math.radians(rot[0]), math.radians(rot[1]), math.radians(rot[2])), "XYZ")
            pb.keyframe_insert("rotation_euler", frame=frame)
            if copy_location:
                pb.location = Vector(loc or (0.0, 0.0, 0.0))
                pb.keyframe_insert("location", frame=frame)

    for fc in bac.iter_fcurves(act):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
    bpy.context.scene.frame_start = PROBE_FRAMES[0]
    bpy.context.scene.frame_end = PROBE_FRAMES[-1]
    bpy.context.scene.frame_set(PROBE_FRAMES[0])
    reset_pose(arm_obj)


READOUT_BONES = ("mixamorig:Hips", "mixamorig:LeftHand", "mixamorig:RightHand",
                 "mixamorig:LeftFoot", "mixamorig:RightFoot")
V8_MIN_MOTION_MM = 20.0


def verify_probe_motion(arm_obj: bpy.types.Object) -> dict:
    """V8：探针动作必须让读数点**真的动**。

    这条是防"平凡通过"的：如果姿势恒定，烘焙保真（E1）与回导保真（E6）会因为**两侧同样静止**
    而无条件通过——2026-09-14 实测就是这样漏过了一版"关键帧根本不生效"的母版。
    """
    pts = {}
    for frame in PROBE_FRAMES:
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        pts[frame] = {b: [round(v, 6) for v in bone_tip_world(arm_obj, b)] for b in READOUT_BONES}
    worst = 0.0
    detail = {}
    for b in READOUT_BONES:
        best = 0.0
        for f1 in PROBE_FRAMES:
            for f2 in PROBE_FRAMES:
                if f2 <= f1:
                    continue
                d = (Vector(pts[f1][b]) - Vector(pts[f2][b])).length * 1000.0
                best = max(best, d)
        detail[b] = round(best, 4)
        worst = max(worst, best)
    return {"max_motion_mm": round(worst, 4), "per_bone_max_mm": detail,
            "threshold_mm": V8_MIN_MOTION_MM,
            "frames": list(PROBE_FRAMES),
            "samples": pts}


def probe_action_coverage(act) -> dict:
    keyed = {}
    for fc in bac.iter_fcurves(act):
        if '"' not in fc.data_path:
            continue
        keyed.setdefault(fc.data_path.split('"')[1], set()).add(fc.data_path.rsplit(".", 1)[-1])
    return {name: sorted(chans) for name, chans in sorted(keyed.items())}


def main() -> int:
    args = parse_args(list(sys.argv))
    in_path = Path(args.input).resolve()
    out_dir = Path(args.out_dir).resolve()
    blend_path = out_dir / f"{TEMPLATE_NAME}.blend"
    report_path = Path(args.report).resolve() if args.report else out_dir / "build_report.json"

    report = {
        "script": "build_xbot_animation_template.py",
        **bac.describe(),
        "input_fbx": str(in_path),
        "output_blend": str(blend_path),
        "checks": {},
        "problems": [],
    }

    def fail(msg):
        report["problems"].append(msg)
        print(f"[V-FAIL] {msg}")

    if not in_path.is_file():
        print(f"[ERROR] 输入 FBX 不存在：{in_path}")
        return 2

    if blend_path.exists() and not args.force:
        print(f"[ERROR] 输出已存在，拒绝覆盖：{blend_path}\n        要覆盖请加 --force")
        return 3

    out_dir.mkdir(parents=True, exist_ok=True)

    # V1（前）：记输入哈希
    hash_before = sha256_of(in_path)
    report["input_sha256_before"] = hash_before

    arm_obj = import_source(in_path)
    fp_before = rest_fingerprint(arm_obj)
    deform_before = deform_fingerprint(fp_before)
    report["checks"]["V2_source_rig"] = {
        "armature_object": arm_obj.name,
        "bones": len(arm_obj.data.bones),
        "roots": [b.name for b in arm_obj.data.bones if b.parent is None],
        "all_prefixed": all(b.name.startswith(BONE_PREFIX) for b in arm_obj.data.bones),
        "mesh_objects": [o.name for o in bpy.data.objects if o.type == "MESH"],
        "expected_bones": EXPECTED_BONE_COUNT,
        "expected_root": EXPECTED_ROOT_BONE,
    }
    c = report["checks"]["V2_source_rig"]
    if c["bones"] != EXPECTED_BONE_COUNT:
        fail(f"V2 骨数 {c['bones']} ≠ {EXPECTED_BONE_COUNT}")
    if c["roots"] != [EXPECTED_ROOT_BONE]:
        fail(f"V2 根骨 {c['roots']} ≠ [{EXPECTED_ROOT_BONE}]")
    if not c["all_prefixed"]:
        fail("V2 存在非 mixamorig: 前缀的骨")

    # V1（后）：导入后再核一次输入字节
    hash_after_import = sha256_of(in_path)
    if hash_after_import != hash_before:
        fail(f"V1 输入 FBX 在导入后被改写：{hash_before} → {hash_after_import}")

    build_control_layer(arm_obj)

    drive = verify_control_drive(arm_obj)
    report["checks"]["V6_control_drive"] = drive
    bad = [r for r in drive if not r["ok"]]
    if bad:
        fail(f"V6 有 {len(bad)} 根控制骨未驱动目标骨（阈值 {CTRL_DRIVE_MIN_MM} mm）："
             + ", ".join(f"{r['ctrl']}={r['tip_delta_mm']}mm" for r in bad))

    author_probe_action(arm_obj)
    act = bpy.data.actions[PROBE_ACTION_NAME]
    coverage = probe_action_coverage(act)
    report["checks"]["V7_probe_action"] = {
        "action": act.name,
        "fcurves": bac.fcurve_count(act),
        "frame_range": list(act.frame_range),
        "fps": SCENE_FPS,
        "keyed_bones": coverage,
    }
    missing = [n for n, _, _ in CTRL_PLAN if n not in coverage]
    if missing:
        fail(f"V7 探针动作缺少控制骨关键帧：{missing}")
    # 重新打开 .blend 会让 action 引用失效，先取好摘要
    probe_summary = {"name": act.name, "range": list(bac.action_frame_range(act))}

    motion = verify_probe_motion(arm_obj)
    report["checks"]["V8_probe_motion"] = motion
    if motion["max_motion_mm"] < V8_MIN_MOTION_MM:
        fail(f"V8 探针动作是退化的：读数点最大位移仅 {motion['max_motion_mm']} mm"
             f"（阈值 {V8_MIN_MOTION_MM} mm）——关键帧没驱动到骨？")
    for bone, d in motion["per_bone_max_mm"].items():
        if d < V8_MIN_MOTION_MM:
            fail(f"V8 读数点 {bone} 位移 {d} mm < {V8_MIN_MOTION_MM} mm（该骨在探针里等于没动）")

    # V5：控制骨 deform 标志
    ctrl_deform = {n: arm_obj.data.bones[n].use_deform for n, _, _ in CTRL_PLAN}
    report["checks"]["V5_ctrl_deform"] = ctrl_deform
    if any(ctrl_deform.values()):
        fail(f"V5 有控制骨 use_deform=True：{[n for n, v in ctrl_deform.items() if v]}")

    # V9：显示层（骨骼集合 / 配色）已落——GUI 里能一键区分控制骨与变形骨
    colls = {c.name: len(c.bones) for c in arm_obj.data.collections}
    report["checks"]["V9_display"] = {"collections": colls,
                                      "expected": {CTRL_COLLECTION: len(CTRL_PLAN),
                                                   DEFORM_COLLECTION: EXPECTED_BONE_COUNT}}
    if colls.get(CTRL_COLLECTION) != len(CTRL_PLAN) or colls.get(DEFORM_COLLECTION) != EXPECTED_BONE_COUNT:
        fail(f"V9 骨骼集合不对：{colls}")

    # 保存
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), compress=False)
    hash_after_save = sha256_of(in_path)
    report["input_sha256_after"] = hash_after_save

    # V3/V4：重新打开刚保存的 .blend，逐条比对
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    arm_re = armature_object()
    fp_after = rest_fingerprint(arm_re)
    deform_after = deform_fingerprint(fp_after)
    report["checks"]["V3V4_reload"] = {
        "bones_after_reload": len(arm_re.data.bones),
        "deform_bones_match": deform_after == deform_before,
        "parent_match": {k: v["parent"] for k, v in deform_after.items()}
        == {k: v["parent"] for k, v in deform_before.items()},
        "rest_pose_match": {k: v["matrix_local"] for k, v in deform_after.items()}
        == {k: v["matrix_local"] for k, v in deform_before.items()},
    }
    rl = report["checks"]["V3V4_reload"]
    if not rl["parent_match"]:
        fail("V3 重新打开后 mixamorig 父子关系与源不一致")
    if not rl["rest_pose_match"]:
        fail("V4 重新打开后 mixamorig Rest Pose 与源不一致")

    # V1（终）
    if hash_after_save != hash_before:
        fail(f"V1 输入 FBX 在运行结束后被改写：{hash_before} → {hash_after_save}")
    report["checks"]["V1_input_unchanged"] = hash_after_save == hash_before

    report["ok"] = not report["problems"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print("=" * 72)
    print(f"母版: {blend_path}")
    print(f"Blender {bac.describe()['blender']} · 动作取道 {bac.describe()['fcurve_access']} · "
          f"骨骼集合 {report['checks']['V9_display']['collections']}")
    print(f"输入 sha256: {hash_before}（运行前后一致={report['checks']['V1_input_unchanged']}）")
    print(f"骨数 {report['checks']['V2_source_rig']['bones']} · 控制骨 {len(CTRL_PLAN)} 根 · "
          f"探针动作 {probe_summary['name']} {probe_summary['range']} @ {SCENE_FPS}fps")
    print(f"控制驱动最小位移: {min(r['tip_delta_mm'] for r in drive):.3f} mm "
          f"（阈值 {CTRL_DRIVE_MIN_MM} mm）")
    print(f"探针动作最大位移: {motion['max_motion_mm']:.3f} mm "
          f"（阈值 {V8_MIN_MOTION_MM} mm）· 逐点 "
          + ", ".join(f"{k.split(':')[-1]}={v:.1f}" for k, v in motion["per_bone_max_mm"].items()))
    print(f"报告: {report_path}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    print("=" * 72)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
