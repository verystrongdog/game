#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_xbot_action.py —— 把母版上的一条控制骨动作烘焙成 animation-only Unity FBX。

来源：design/presentation/Blender动作制作管线.md §四（导出预设）/§五（回导判据）
      母版由 build_xbot_animation_template.py 生成（同目录）

做三件事
--------
1. **烘焙**：把控制骨（`CTRL_*`）经 Constraint 驱动的姿势，逐帧烘到变形骨（`mixamorig:*`）上，
   得到一条只含变形骨通道的 action。烘完解除约束——此后 FBX 里的姿势完全来自显式关键帧。
2. **导出**：`use_armature_deform_only=True` + `add_leaf_bones=False` + `object_types={'ARMATURE'}`，
   即 animation-only（无网格、无控制骨、无新增 Leaf Bone、无额外 Root 骨）。
3. **回读校验**：把刚导出的 FBX 重新导入到空场景，逐条核验，并把两端逐帧姿势读数比对。

自检判据（不通过即非 0 退出）
----------------------------
E1 烘焙保真：烘焙后与烘焙前的变形骨世界姿势逐帧一致（≤ E1_TOL_MM）
E2 导出物骨集 == 源 65 根，且**零** `CTRL_` 名
E3 导出物单一根骨 `mixamorig:Hips`（无额外 Root 骨），且无新增 Leaf Bone
E4 导出物不含网格（animation-only）
E5 导出物 Rest Pose 与源逐条一致（端点坐标 ≤ E5_TOL_MM）
E6 导出物在探针各帧的姿势 == 母版（回导保真，≤ E6_TOL_MM）

用法
----
    blender --background --factory-startup --python-exit-code 1 \\
        --python code/tools/export_xbot_action.py -- \\
        [--template <.blend>] [--action RigRoundTripProbe] [--output <.fbx>] [--force]

版本：本脚本 **Blender 4.5 LTS 与 5.x 双兼容**（差异收在 `blender_action_compat.py`）。
"""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blender_action_compat as bac          # noqa: E402  4.5 / 5.x 动作 API 取道层
from mathutils import Vector

REPO_ROOT = Path(__file__).resolve().parents[2]

BONE_PREFIX = "mixamorig:"
CTRL_PREFIX = "CTRL_"
EXPECTED_BONE_COUNT = 65
EXPECTED_ROOT_BONE = "mixamorig:Hips"

# 回导读数点：与 Unity 侧 BlenderAnimationDebugger 读的是同一组人形骨
# 来源：design/presentation/Blender动作制作管线.md §五·2
READOUT_BONES = ("mixamorig:Hips", "mixamorig:LeftHand", "mixamorig:RightHand",
                 "mixamorig:LeftFoot", "mixamorig:RightFoot")

E0_MIN_MOTION_MM = 20.0   # 源动作非退化阈值（防"两侧同样静止"式的平凡通过）
E1_TOL_MM = 0.5       # 烘焙保真容差（实测中段插值帧残差 0.1 mm 量级，见报告）
E5_TOL_MM = 0.5       # Rest Pose 端点坐标容差（mm）——实测 4.5 侧 ~0.005、5.1 侧 0.122，都远小于"结构漂移"量级
E5_MATRIX_TOL = 5e-4  # 矩阵元素容差（仅供参考的噪声读数）
E6_TOL_MM = 0.5       # 回导保真容差（跨 FBX 往返，允许更大）
SCENE_FPS = 30


# ---------------------------------------------------------------- 小工具


def parse_args(argv):
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser(prog="export_xbot_action.py")
    ap.add_argument("--template", default=str(REPO_ROOT / ".scratch/blender_assets/xbot/XBot_AnimationTemplate.blend"))
    ap.add_argument("--action", default="RigRoundTripProbe")
    ap.add_argument("--output", default=None)
    ap.add_argument("--report", default=None)
    ap.add_argument("--force", action="store_true")
    return ap.parse_args(argv)


def armature_object():
    arms = [ob for ob in bpy.data.objects if ob.type == "ARMATURE"]
    if len(arms) != 1:
        raise RuntimeError(f"期望恰好 1 个 Armature，实测 {len(arms)}")
    return arms[0]


def rest_fingerprint(arm_obj):
    return {
        b.name: {
            "parent": b.parent.name if b.parent else None,
            "head_local": [round(v, 6) for v in b.head_local],
            "tail_local": [round(v, 6) for v in b.tail_local],
            "matrix_local": [round(v, 6) for row in b.matrix_local for v in row],
        }
        for b in arm_obj.data.bones
    }


def sample_world(arm_obj, frames, bones):
    """逐帧采骨头的世界坐标（head 与 tail），作为两端比对的共同读数。"""
    out = {}
    for f in frames:
        bpy.context.scene.frame_set(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        ev = arm_obj.evaluated_get(dg)
        row = {}
        for b in bones:
            pb = ev.pose.bones[b]
            row[b] = {
                "head": [round(v, 6) for v in (ev.matrix_world @ pb.head)],
                "tail": [round(v, 6) for v in (ev.matrix_world @ pb.tail)],
            }
        out[f] = row
    return out


def shift_action_to_zero(action) -> int:
    """把 action 的关键帧整体前移到从第 0 帧开始。

    FBX 的 take 时间轴是 0 基的：既有 15 条 Mixamo FBX 在 Blender 里都从第 1 帧读入
    （= 源文件第 0 帧）。母版里动作从第 1 帧起，直接导出会让 take 从 1/30 s 起，
    回导后整体后移一帧。归零后两端帧号逐帧对齐（来源：管线文档 §四·3）。
    """
    shift = -int(round(min(fc.keyframe_points[0].co.x for fc in bac.iter_fcurves(action))))
    if shift == 0:
        return 0
    for fc in bac.iter_fcurves(action):
        for kp in fc.keyframe_points:
            kp.co.x += shift
            kp.handle_left.x += shift
            kp.handle_right.x += shift
        fc.update()
    return shift


def diff_mm(a, b):
    worst = 0.0
    where = None
    for f, row in a.items():
        for bone, pts in row.items():
            for key in ("head", "tail"):
                d = (Vector(pts[key]) - Vector(b[f][bone][key])).length * 1000.0
                if d > worst:
                    worst, where = d, f"{bone}.{key}@f{f}"
    return round(worst, 4), where


# ---------------------------------------------------------------- 主流程


def main() -> int:
    args = parse_args(list(sys.argv))
    tmpl = Path(args.template).resolve()
    out_fbx = Path(args.output).resolve() if args.output else tmpl.parent / f"{args.action}.fbx"
    report_path = Path(args.report).resolve() if args.report else tmpl.parent / "export_report.json"

    report = {"script": "export_xbot_action.py", **bac.describe(),
              "template": str(tmpl), "action": args.action, "output_fbx": str(out_fbx),
              "checks": {}, "problems": []}

    def fail(msg):
        report["problems"].append(msg)
        print(f"[E-FAIL] {msg}")

    if not tmpl.is_file():
        print(f"[ERROR] 母版不存在：{tmpl}\n        先跑 build_xbot_animation_template.py")
        return 2
    if out_fbx.exists() and not args.force:
        print(f"[ERROR] 输出已存在，拒绝覆盖：{out_fbx}\n        要覆盖请加 --force")
        return 3

    bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    bpy.context.scene.render.fps = SCENE_FPS
    arm = armature_object()
    src_fp = rest_fingerprint(arm)
    src_bones = sorted(src_fp)

    if args.action not in bpy.data.actions:
        print(f"[ERROR] 母版里没有 action {args.action!r}；现有：{[a.name for a in bpy.data.actions]}")
        return 4
    act = bpy.data.actions[args.action]
    arm.animation_data_create()
    bac.assign_action(arm.animation_data, act)
    f0, f1 = (int(round(v)) for v in bac.action_frame_range(act))
    frames = [f0, (f0 + f1) // 2, f1]
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = f0, f1

    # 烘焙前：控制骨驱动下的读数（作为 E1 的基准）
    before = sample_world(arm, frames, READOUT_BONES)

    # ---- 0) E0：源动作非退化（否则下面的保真判据全部平凡通过）
    spans = {}
    for bone in READOUT_BONES:
        best = 0.0
        for f1 in frames:
            for f2 in frames:
                if f2 <= f1:
                    continue
                d = (Vector(before[f1][bone]["tail"]) - Vector(before[f2][bone]["tail"])).length * 1000.0
                best = max(best, d)
        spans[bone] = round(best, 4)
    e0 = max(spans.values())
    report["checks"]["E0_source_motion"] = {"max_motion_mm": e0, "per_bone_mm": spans,
                                            "threshold_mm": E0_MIN_MOTION_MM, "frames": frames}
    if e0 < E0_MIN_MOTION_MM:
        fail(f"E0 源动作退化：读数点最大位移仅 {e0} mm（阈值 {E0_MIN_MOTION_MM} mm）"
             f"——母版里那条 action 根本没驱动骨架，后续保真判据无意义")

    # ---- 1) 烘焙：只选变形骨，visual keying 取约束求值后的姿势
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="POSE")
    select_attr = bac.select_pose_bones(arm, lambda n: n.startswith(BONE_PREFIX))
    # ⚠️ `use_current_action=True` 是必须的（2026-09-14 实测，代价一整轮假绿）：
    #    `use_current_action=False` 会**当场把控制骨 action 摘下来**，于是烘焙逐帧求值时控制骨恒为
    #    静止姿势 → 烘出来的是一条**常量**曲线。而它与"母版静止"逐位相同，E1/E6 会**平凡通过**
    #    （症状：FBX 有 2.0 s 时长、Unity 侧 130 条曲线全部 constant）。改为就地烘焙后控制骨
    #    在整个烘焙过程中照常驱动；烘完再把控制骨通道从 action 里剥掉。
    bpy.ops.nla.bake(frame_start=f0, frame_end=f1, step=1,
                     only_selected=True, visual_keying=True,
                     clear_constraints=False, clear_parents=False,
                     use_current_action=True, bake_types={"POSE"})
    baked = arm.animation_data.action
    baked.name = f"{args.action}_Baked"
    bpy.ops.object.mode_set(mode="OBJECT")

    stripped = bac.remove_fcurves_where(baked, lambda fc: f'"{CTRL_PREFIX}' in fc.data_path)

    # 烘完解除约束：此后姿势只来自显式关键帧，导出物不依赖控制层
    dropped = 0
    for pbone in arm.pose.bones:
        for c in list(pbone.constraints):
            pbone.constraints.remove(c)
            dropped += 1

    after = sample_world(arm, frames, READOUT_BONES)
    e1, e1_where = diff_mm(before, after)
    report["checks"]["E1_bake_fidelity"] = {
        "baked_action": baked.name, "fcurves": bac.fcurve_count(baked),
        "ctrl_curves_stripped": stripped, "constraints_removed": dropped,
        "max_delta_mm": e1, "worst_at": e1_where, "tolerance_mm": E1_TOL_MM,
    }
    if e1 > E1_TOL_MM:
        fail(f"E1 烘焙不保真：最大偏差 {e1} mm @ {e1_where}（容差 {E1_TOL_MM} mm）")

    # 归零到 0 基，让 FBX take 与既有 Mixamo 同口径（回导后帧号逐帧对齐）
    shifted = shift_action_to_zero(baked)
    bpy.context.scene.frame_start = f0 + shifted
    bpy.context.scene.frame_end = f1 + shifted
    bpy.context.scene.name = args.action   # FBX take 名 = <Armature>|<Scene>
    baked_name = baked.name
    report["checks"]["bake_step"] = {
        "frames": [f0, f1], "shifted_to_zero": shifted, "bone_select_attr": select_attr,
        "exported_frame_range": [f0 + shifted, f1 + shifted],
        "constraints_removed": dropped,
        "ctrl_bones_still_present": [n for n in src_bones if n.startswith(CTRL_PREFIX)],
    }

    # ---- 2) 导出：animation-only
    out_fbx.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=str(out_fbx),
        use_selection=False,
        object_types={"ARMATURE"},          # 无网格 ⇒ animation-only
        axis_forward="-Z", axis_up="Y",     # Unity 约定（既有 15 条 Mixamo FBX 同口径）
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_NONE",
        bake_space_transform=False,
        add_leaf_bones=False,               # 不新增 Leaf Bone
        use_armature_deform_only=True,      # 控制骨不外泄
        primary_bone_axis="Y", secondary_bone_axis="X",
        armature_nodetype="NULL",
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0,      # 不做关键帧简化 ⇒ 可复现
        use_custom_props=False,
        path_mode="AUTO",
        embed_textures=False,
    )
    report["checks"]["E_export_bytes"] = {"size": out_fbx.stat().st_size}

    # ---- 3) 回读校验
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = SCENE_FPS
    bpy.ops.import_scene.fbx(filepath=str(out_fbx))
    arm2 = armature_object()
    rt_fp = rest_fingerprint(arm2)
    rt_bones = sorted(rt_fp)
    rt_deform = [n for n in rt_bones if n.startswith(BONE_PREFIX)]
    rt_ctrl = [n for n in rt_bones if n.startswith(CTRL_PREFIX)]
    roots = sorted(b.name for b in arm2.data.bones if b.parent is None)
    meshes = [ob.name for ob in bpy.data.objects if ob.type == "MESH"]
    extra_bones = sorted(set(rt_bones) - set(src_bones))

    report["checks"]["E2_bone_set"] = {
        "bones_total": len(rt_bones), "deform_bones": len(rt_deform),
        "ctrl_leaked": rt_ctrl, "unexpected_bones": extra_bones,
        "expected_deform": EXPECTED_BONE_COUNT,
    }
    if rt_ctrl:
        fail(f"E2 控制骨外泄到导出物：{rt_ctrl}")
    if len(rt_deform) != EXPECTED_BONE_COUNT or extra_bones:
        fail(f"E2 变形骨集不符：{len(rt_deform)} ≠ {EXPECTED_BONE_COUNT}，多余 {extra_bones}")
    if len(rt_bones) != EXPECTED_BONE_COUNT:
        fail(f"E3 导出物骨数 {len(rt_bones)} ≠ {EXPECTED_BONE_COUNT}（疑似新增 Leaf Bone）")

    report["checks"]["E3_root"] = {"roots": roots, "expected": [EXPECTED_ROOT_BONE]}
    if roots != [EXPECTED_ROOT_BONE]:
        fail(f"E3 根骨不唯一/不符：{roots}")

    report["checks"]["E4_animation_only"] = {"meshes": meshes}
    if meshes:
        fail(f"E4 导出物含网格：{meshes}")

    src_deform_fp = {k: v for k, v in src_fp.items() if k.startswith(BONE_PREFIX)}
    # ⚠️ 判据取**骨端点坐标**（mm），不取矩阵元素：矩阵元素是浮点噪声敏感量——实测 4.5 侧
    #    9.2e-05、5.1 侧 1.22e-04，同一份骨架跨版本就能越过 1e-4 的阈值，而那与"Rest Pose 变了没"
    #    无关。端点坐标才是"Rest Pose 不变"的语义量。
    rest_worst_mm = 0.0
    matrix_worst = 0.0
    for n in src_deform_fp:
        for key in ("head_local", "tail_local"):
            a, b = src_deform_fp[n][key], rt_fp[n][key]
            rest_worst_mm = max(rest_worst_mm, max(abs(x - y) for x, y in zip(a, b)) * 1000.0)
        ma, mb = src_deform_fp[n]["matrix_local"], rt_fp[n]["matrix_local"]
        matrix_worst = max(matrix_worst, max(abs(x - y) for x, y in zip(ma, mb)))
    rest_match = rest_worst_mm <= E5_TOL_MM
    report["checks"]["E5_rest_pose"] = {
        "match": rest_match, "compared": len(src_deform_fp),
        "max_endpoint_delta_mm": round(rest_worst_mm, 6), "tolerance_mm": E5_TOL_MM,
        "max_matrix_element_delta": round(matrix_worst, 8), "matrix_tolerance_info": E5_MATRIX_TOL,
    }
    if not rest_match:
        fail(f"E5 导出物 Rest Pose 与源不一致：端点最大差 {rest_worst_mm:.6f} mm"
             f"（容差 {E5_TOL_MM} mm）")

    # E6：回导后的逐帧姿势 vs 母版
    rt_actions = [a for a in bpy.data.actions]
    if not rt_actions:
        fail("E6 导出物没有动画")
    else:
        arm2.animation_data_create()
        bac.assign_action(arm2.animation_data, rt_actions[0])
        af0, af1 = (int(round(v)) for v in bac.action_frame_range(rt_actions[0]))
        report["checks"]["E_roundtrip_action"] = {
            "action": rt_actions[0].name, "fcurves": bac.fcurve_count(rt_actions[0]),
            "frame_range": [af0, af1],
        }
        probe_frames = [af0, (af0 + af1) // 2, af1]
        rt_pose = sample_world(arm2, probe_frames, READOUT_BONES)
        frame_map = {f: f + (af0 - frames[0]) for f in frames}   # 母版帧 → 回导帧
        remapped = {f: rt_pose[g] for f, g in frame_map.items() if g in rt_pose}
        e6, e6_where = diff_mm({f: v for f, v in after.items() if f in remapped}, remapped)
        report["checks"]["E6_roundtrip_fidelity"] = {
            "max_delta_mm": e6, "worst_at": e6_where, "tolerance_mm": E6_TOL_MM,
            "template_frames": frames, "roundtrip_frames": probe_frames,
            "frame_offset": af0 - frames[0], "frame_map": frame_map,
        }
        if e6 > E6_TOL_MM:
            fail(f"E6 回导姿势与母版不符：最大偏差 {e6} mm @ {e6_where}")

    report["checks"]["readout"] = {"frames": frames, "bones": list(READOUT_BONES)}
    report["ok"] = not report["problems"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print("=" * 72)
    print(f"导出: {out_fbx}（{out_fbx.stat().st_size} 字节）")
    print(f"源动作位移: {e0:.3f} mm（阈值 {E0_MIN_MOTION_MM}）· 烘焙: {baked_name} · "
          f"帧 {f0}–{f1} → 导出帧 {f0 + shifted}–{f1 + shifted} @ {SCENE_FPS}fps · 保真差 {e1} mm")
    print(f"回读: 骨 {len(rt_bones)}（变形 {len(rt_deform)} / 控制外泄 {len(rt_ctrl)}）· "
          f"根 {roots} · 网格 {len(meshes)} · 回导差 "
          f"{report['checks'].get('E6_roundtrip_fidelity', {}).get('max_delta_mm', 'n/a')} mm")
    print(f"报告: {report_path}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL —— ' + '; '.join(report['problems'])}")
    print("=" * 72)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
