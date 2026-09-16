#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 verystrongdog
# SPDX-License-Identifier: GPL-3.0-or-later
"""lab_multi_instance.py —— 多实例呈现 lab 装配器（口径 §15.8 · [#169] 的交付）。

来源：design/presentation/动作描述口径.md **§15.8**（多实例 lab：三件同屏 · 间距 **5.0 m**（owner
      2026-09-16 圈定，非实测非扫描）· 落 `.scratch/` + `--no-save` · 逐实例可见性收敛 ·
      指派 action **必须走取道层**）· §15.9（三件的顺序 ①→②→③）
      · [危险点表 §四](../engineering/危险点表.md) 的四条坑
      · 先例：宿主 5/6 里的 `door_push_preview_cleanup` / `visible_bone_outliers`

它是什么
--------
把**若干「母版复制体」（实例）**沿**世界 X 轴**等距排开（默认 −5.0 / 0 / +5.0 m），
每个实例 = 一套（Armature + 蒙皮网格 + 一个动作）——用于在**一个 Blender 界面**里同时看
多个候选动作（本批三件：① 恐慌姿态 · ② 下蹲/被推退 · ③ 跪地/顶肘）。

四条硬规矩（口径 §15.8，本脚本只实现、不改）
------------------------------------------
1. **lab 不是导出源**：`export_xbot_action.py` 硬要求「**恰好 1 个 Armature**」；母版自检
   V2/V3/V9 也硬判 ⇒ 本脚本**从不写回**任何文件（`--no-save` 是默认且唯一的形态）。
2. **lab 只做呈现**：解算、判据、导出仍在**单实例**文件里做 ⇒ 实例只需**整体平移**，
   相对关系不变、姿势与接触读数**不需要在 lab 里重算**（本脚本因此**不重算任何判据**）。
3. **指派 action 必须走取道层** `blender_action_compat.assign_action()`：Blender 5.x 侧
   不设 `action_slot` 的话，那条 action **不驱动任何东西**（实测过）。
4. **逐实例收敛**：可见性收敛（只留 `MIXAMORIG`、隐藏 13 根标记骨）**每个实例各跑一次**，
   否则会再出现 owner 指出过三次的"多余骨骼飘在模型外面"。

用法
----
    blender --background --factory-startup --python-exit-code 1 \\
        --python code/tools/lab_multi_instance.py -- \\
        --template <.blend 含动作> \\
        --instances "0:PanicCoverEars,-5:PanicCoverEars,5:PanicCoverEars" \\
        [--report <.json>] [--still <png>] [--spacing 5.0]

`--instances` 的每一项是 `<x 米>:<动作名>`；动作名 `-` 表示该实例只放母版的中立姿势。

版本：Blender 4.5 / 5.x 均可（动作指派走取道层）。
"""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

DEFAULT_SPACING_M = 5.0
#: 可见性收敛后的期望可见骨数：65 变形骨 − 13 根标记骨（口径 §15.4 / 管线 §2.1.5 规矩 1）
EXPECTED_VISIBLE_BONES = 52

#: **本批三件的实例预设**（口径 §15.8：三份实例沿世界 X 轴等距 −5.0 / 0 / +5.0 m）。
#: - `①` 恐慌姿态（[#169](https://github.com/verystrongdog/game/issues/169)）= **0.0 m**：母版原件留在原位
#:   （装配器把 0 号实例当作模板，改动最小）；
#: - `②` 下蹲/被推退（[#170](https://github.com/verystrongdog/game/issues/170)）= **+5.0 m**（本件加的**第 2 个实例**）；
#: - `③` 跪地/顶肘（[#171](https://github.com/verystrongdog/game/issues/171)）= **−5.0 m**，**未落地** ⇒ `None`
#:   （`--batch` 会把它渲染成中立姿势的占位，并在报告里登记"③ 未落"）。
#: ⚠️ 本仓库把"加第 2 个实例"落成**批预设 + 实跑**，而不是改复制逻辑：装配器在 #169 已按
#:   `--instances` 列表泛化（复制 / 平移 / 逐实例收敛 / 指派 action 都在),第 2 件不需要新机制。
#: 末项 = **定格帧**：每件停在自己的判据帧上（① 捂耳到位帧 13 · ② 失衡极值帧 34）。
#: ⚠️ 为什么要有它：#169 那次静帧停在 `scene.frame_start`(=1)，而两条动作的首帧都被
#:   导出侧 E5 硬约定要求为**中立姿势** ⇒ 那样拍出来的"三件同屏"其实是**三个站着不动的人**。
BATCH_SLOTS = ((0.0, "PanicCoverEars", "① 恐慌姿态（#169）", 13, False),
               (5.0, "CrouchPushedBack", "② 下蹲/被推退（#170）", 34, False),
               (-5.0, "KneelElbowBrace", "③ 跪地/顶肘（#171）", 61, True))
#: 第 5 列 = 该实例**带道具代理**（本批只有 ③ 有：`REF_Door*`）。
#: ⚠️ 道具**只平移一份**到它那一件的位置，不逐实例复制——逐实例复制会变成"三扇门"。


def batch_instances(include_unlanded=True):
    """本批三件的 `--instances` 串（`<x>:<动作>:<定格帧>`）。"""
    out = []
    for x, action, _label, frame, _prop in BATCH_SLOTS:
        if action is None and not include_unlanded:
            continue
        item = f"{x:g}:{action or '-'}"
        if frame is not None:
            item += f":{frame}"
        out.append(item)
    return ",".join(out)


def parse_args(argv):
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser(prog="lab_multi_instance.py")
    ap.add_argument("--template", default=str(Path(__file__).resolve().parents[2] /
                                             ".scratch/panic/panic_clip.blend"))
    ap.add_argument("--batch", action="store_true",
                    help="用**本批三件的槽位预设**（0 / +5 / −5 m；③ 未落地 ⇒ 中立姿势占位）"
                         "覆盖 --instances（口径 §15.8）")
    ap.add_argument("--instances", default="0:PanicCoverEars",
                    help="逗号分隔的 `<x 米>:<动作名>`；动作名 `-` = 中立姿势")
    ap.add_argument("--spacing", type=float, default=DEFAULT_SPACING_M,
                    help="等距排列的名义间距（m）——口径 §15.8 = 5.0（owner 圈定）")
    ap.add_argument("--report", default=None)
    ap.add_argument("--still", default=None)
    return ap.parse_args(argv)


def host_module():
    """取宿主脚本里的**已入库件**（可见性收敛 / 越界骨判据 / 静帧）——不复制第二份实现。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import author_xbot_chair_grab as host
    return host


def instances_from_spec(spec):
    """`<x 米>:<动作名>[:<定格帧>]` → 实例表。动作名 `-` = 中立姿势；定格帧缺省 = 场景起帧。

    ⚠️ 定格帧是**呈现用**的：lab **不重算任何判据**（口径 §15.8 硬规矩 2），它只是把该实例
    停在自己的判据帧上，好让 owner 在一屏里看见"每件最该看的那一帧"。
    """
    out = []
    for item in [x.strip() for x in spec.split(",") if x.strip()]:
        parts = item.split(":")
        x_str = parts[0]
        action = (parts[1].strip() or "-") if len(parts) > 1 else "-"
        frame = int(parts[2]) if len(parts) > 2 and parts[2].strip() else None
        out.append({"x_m": float(x_str), "action": action, "freeze_frame": frame})
    return out


def duplicate_instance(arm, x_m):
    """复制一套（Armature + 蒙皮网格）并整体平移 `x_m`（只平移，不改相对关系）。

    ⚠️ 蒙皮网格的 Armature 修改器**必须改指到新骨架**，否则它会被两套骨架同时驱动
    （实测症状：实例的皮肤不跟自己的姿势走）。
    """
    arm2 = arm.copy()                      # 共享 armature data（姿势在**对象**层 ⇒ 各实例独立）
    bpy.context.scene.collection.objects.link(arm2)
    arm2.location = arm.location + Vector((x_m, 0.0, 0.0))
    meshes = []
    for ob in [o for o in bpy.data.objects
               if o.type == "MESH" and any(m.type == "ARMATURE" and m.object == arm
                                           for m in o.modifiers)]:
        ob2 = ob.copy()
        bpy.context.scene.collection.objects.link(ob2)
        for mod in ob2.modifiers:
            if mod.type == "ARMATURE" and mod.object == arm:
                mod.object = arm2
        if ob2.parent == arm:
            ob2.parent = arm2
        else:                              # 没挂父级 ⇒ 按世界位移补齐
            ob2.location = ob.location + Vector((x_m, 0.0, 0.0))
        meshes.append(ob2)
    bpy.context.view_layer.update()
    return arm2, meshes


def instance_bbox(arm_obj, meshes):
    """该实例的**世界包围盒**（取蒙皮网格，不取骨架）——静态校核用。"""
    pts = []
    for ob in meshes:
        for corner in ob.bound_box:
            pts.append(ob.matrix_world @ Vector(corner))
    if not pts:
        return None
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return {"min": [round(c, 4) for c in lo], "max": [round(c, 4) for c in hi],
            "尺寸_m": [round(hi[i] - lo[i], 4) for i in range(3)]}


def main() -> int:
    from datetime import datetime
    args = parse_args(list(sys.argv))
    host = host_module()
    host_mod_name = host.__name__
    tmpl = Path(args.template)
    if not tmpl.is_file():
        print(f"[ERROR] 母版/剪辑不存在：{tmpl}")
        return 2
    spec = instances_from_spec(batch_instances() if args.batch else args.instances)
    if not spec:
        print("[ERROR] --instances 为空")
        return 2

    bpy.ops.wm.open_mainfile(filepath=str(tmpl))
    arm = host.armature()
    host.drop_temp(arm)
    base_action = arm.animation_data.action.name if arm.animation_data and arm.animation_data.action else None
    host.clear_pose(arm)
    # 原实例留在原位（它是 `--instances` 里的 0 号，也可能只用作模板）——先记下它的网格
    base_meshes = [o for o in bpy.data.objects
                   if o.type == "MESH" and any(m.type == "ARMATURE" and m.object == arm
                                               for m in o.modifiers)]
    print(f"母版 {tmpl.name} · 骨架 {arm.name} · 蒙皮网格 {[o.name for o in base_meshes]} · "
          f"当前动作 {base_action}")

    report = {"script": Path(__file__).name, "blender": bpy.app.version_string,
              "template": str(tmpl), "measured_at": datetime.now().isoformat(timespec="seconds"),
              "spacing_m": args.spacing, "instances": [], "problems": [],
              "batch": bool(args.batch),
              "batch_slots": ([{"x_m": x, "动作": a, "标签": lb, "定格帧": fr, "带道具": pr}
                               for x, a, lb, fr, pr in BATCH_SLOTS] if args.batch else None)}
    rows = []
    frozen_store = []
    for idx, item in enumerate(spec):
        if idx == 0:
            arm_i, meshes_i = arm, base_meshes
            if item["x_m"] != 0.0:
                arm_i.location = Vector((item["x_m"], 0.0, 0.0))
                bpy.context.view_layer.update()
        else:
            arm_i, meshes_i = duplicate_instance(arm, item["x_m"] - arm.location.x)
        # 逐实例指派动作（走取道层；5.x 不设 action_slot ⇒ 动作不驱动任何东西）
        action_name = item["action"]
        if action_name == "-":
            # 中立姿势：`-` 的实例是**复制出来的**，它会继承复制那一刻来源骨架的**姿势与动画数据**
            # （实测 #170：来源那时挂着 `PanicCoverEars` ⇒ 占位实例在 x=−5 处**演着别人的动作**，
            #  而报告里写的是「动作 `-`」——**报告看不出来**，是 owner 目视那一层才会发现的错。
            #  ⇒ 必须**两件都清**：解开 animation_data（否则 action 会在换帧时把姿势覆盖回来）+ 清姿势）
            if arm_i.animation_data:
                arm_i.animation_data_clear()
            host.clear_pose(arm_i)
        if action_name != "-":
            act = bpy.data.actions.get(action_name)
            if act is None:
                report["problems"].append(f"实例 {idx}（x={item['x_m']}）找不到动作 {action_name}")
                continue
            ad = arm_i.animation_data if arm_i.animation_data else arm_i.animation_data_create()
            try:
                sys.path.insert(0, str(Path(__file__).resolve().parent))
                import blender_action_compat as bac
                bac.assign_action(ad, act)
            except Exception as exc:
                report["problems"].append(f"取道层不可用（{exc}）⇒ 实例 {idx} 动作未指派")
                ad.action = act
        # 逐实例可见性收敛（口径 §15.8 硬规矩 4）
        cleanup = host.door_push_preview_cleanup(arm_i)
        # ⚠️ 必须把**该实例自己的网格**传进去：按名字取会取到原实例的皮肤（实测假红 51 根 × 5000 mm）
        outliers = host.visible_bone_outliers(arm_i, meshes=meshes_i)
        freeze = item.get("freeze_frame")
        frozen = None
        if freeze is not None:
            bpy.context.scene.frame_set(freeze)
            host.update()
            frozen = host.capture_channels(arm_i, [pb.name for pb in arm_i.pose.bones])
        hip = None
        if frozen:
            # 定格的**读数**（不是判据）：髋骨世界位置——用来证明"停的不是中立姿势"（中立姿势的
            # 髋 z 是 1.0427 m，两条动作的判据帧分别是 1.0127 / 0.8827 m，本件实测值见证据）
            bp = arm_i.pose.bones.get("mixamorig:Hips")
            if bp is not None:
                wp = arm_i.matrix_world @ bp.head
                hip = [round(wp.x, 4), round(wp.y, 4), round(wp.z, 4)]
        actual_action = (arm_i.animation_data.action.name
                         if arm_i.animation_data and arm_i.animation_data.action else None)
        expected_action = None if action_name == "-" else action_name
        row = {"序": idx, "x_m": item["x_m"], "动作": action_name, "实际动作": actual_action,
               "定格帧": freeze, "定格通道数": (len(frozen) if frozen else 0),
               "定格_髋世界_m": hip,
               "x_实测_m": round(arm_i.location.x, 4),
               "隐藏的骨集合": cleanup["隐藏的骨集合"], "藏起来的标记骨": cleanup["藏起来的标记骨"],
               "可见骨数": outliers["可见骨数"], "非例外的越界骨": outliers["非例外的越界骨"],
               "包围盒": instance_bbox(arm_i, meshes_i)}
        rows.append(row)
        if frozen:
            frozen_store.append((arm_i, frozen))
        print(f"  实例 {idx} · x={item['x_m']:+.1f} m（实测 {row['x_实测_m']:+.4f}）· 动作 {action_name} · "
              f"可见骨 {row['可见骨数']} · 非例外越界 {len(outliers['非例外的越界骨'])}"
              + (f" · **定格在帧 {freeze}**（{len(frozen)} 个通道 · 髋世界 "
                 f"({hip[0]:+.4f}, {hip[1]:+.4f}, {hip[2]:+.4f}) m）" if frozen else ""))
        if row["可见骨数"] != EXPECTED_VISIBLE_BONES:
            report["problems"].append(
                f"实例 {idx} 可见骨 {row['可见骨数']} ≠ 期望 {EXPECTED_VISIBLE_BONES}"
                f"（65 变形骨 − 13 标记骨）")
        if actual_action != expected_action:
            # 判据：报告写的动作必须就是骨架上挂着的那个（复制实例会**带走来源的动作**——本件实测踩到）
            report["problems"].append(
                f"实例 {idx} 的实际动作 {actual_action!r} ≠ 期望 {expected_action!r}"
                f"（`copy()` 会把来源的 animation_data 一起复制过去）")
        if outliers["非例外的越界骨"]:
            report["problems"].append(
                f"实例 {idx} 有可见骨伸出皮肤包围盒："
                + "; ".join(f"{x['骨']}({x['伸出量_mm']:.1f} mm)" for x in outliers["非例外的越界骨"][:6]))

    # 道具代理：**只平移一份**到"带道具"那一件的位置（口径 §15.8 硬规矩 1/2：lab 是生成物、从不写回）
    prop_slot = next((x for x, a, _l, _f, pr in BATCH_SLOTS if pr and a is not None), None)
    props = [o for o in bpy.data.objects
             if o.name.startswith("REF_") and o.type == "MESH"
             and not any(m.type == "ARMATURE" for m in o.modifiers)]   # 只搬**网格**代理
    if props and prop_slot is not None:
        for ob in props:
            ob.location = ob.location + Vector((prop_slot, 0.0, 0.0))
        bpy.context.view_layer.update()
    report["props"] = {"对象": [o.name for o in props], "平移到_x_m": prop_slot}
    if props:
        print(f"道具代理 {len(props)} 件（{', '.join(o.name for o in props)}）"
              f"平移到 x={prop_slot:+.1f} m 那一件（只平移一份，不逐实例复制）")

    # 静态校核：**一次**（口径 §15.8：不做逐帧判据）+ 间距核对
    # ⚠️ 相邻对必须按**实测 x 升序**取（原实现按 `--instances` 的**参数顺序**取 ⇒ 参数写成
    #    `0:…,5:…,-5:…` 时会把两端当成相邻、误报"包围盒重叠"——#170 实测踩到）。
    boxes = sorted([(r["序"], r["包围盒"], r["x_实测_m"]) for r in rows if r["包围盒"]],
                   key=lambda t: t[2])
    boxes = [(i, b) for i, b, _x in boxes]
    gaps = []
    for (i, a), (j, b) in zip(boxes, boxes[1:]):
        gaps.append({"对": [i, j], "x 间隙_m": round(b["min"][0] - a["max"][0], 4),
                     "重叠": bool(b["min"][0] < a["max"][0])})
    xs = sorted(r["x_实测_m"] for r in rows)
    spacing_ok = all(abs((xs[i + 1] - xs[i]) - args.spacing) < 1e-6 for i in range(len(xs) - 1))
    duplicated = len(xs) != len(set(xs))
    report["instances"] = rows
    report["static_check"] = {"实例 x 排序_m": xs, "重复位置": bool(duplicated),
                              "包围盒两两 x 间隙_m": gaps,
                              "任意重叠": any(g["重叠"] for g in gaps),
                              "实际间距_m": [round(xs[i + 1] - xs[i], 6) for i in range(len(xs) - 1)],
                              "间距符合名义值": bool(spacing_ok),
                              "说明": "口径 §15.8：互相干扰与否**不做逐帧判据**，只在装配后做一次静态包围盒校核"}
    if report["static_check"]["任意重叠"]:
        report["problems"].append("实例包围盒在 x 上重叠")
    if not spacing_ok:
        report["problems"].append(f"实测间距（排序后）与名义 {args.spacing} m 不符：{xs}")
    if duplicated:
        report["problems"].append(f"有两个实例落在同一 x：{xs}")
    print(f"静态校核：间距 {report['static_check']['实际间距_m']} m（名义 {args.spacing}）· "
          f"包围盒重叠 {report['static_check']['任意重叠']}")
    report["ok"] = not report["problems"]

    # 逐实例定格：解开动画后把捕获的通道写回去（顺序：全部捕获完再统一应用，避免相互影响）
    for arm_i, channels in frozen_store:
        if arm_i.animation_data:
            arm_i.animation_data.action = None
        host.apply_channels(arm_i, channels)
    if frozen_store:
        report["frozen"] = [{"序": r["序"], "定格帧": r["定格帧"]} for r in rows if r.get("定格帧")]
        print(f"逐实例定格：{len(frozen_store)} 个实例停在自己的判据帧上（lab **不重算判据**，只呈现）")
    bpy.context.scene.frame_set(bpy.context.scene.frame_start
                               if bpy.context.scene.frame_start else 1)
    if args.still and xs:
        mid = Vector((sum(xs) / len(xs), 0.0, 1.2))
        host.render_still(args.still, mid + Vector((0.0, -4.2, 0.6)), mid, res=(1600, 700))
        print(f"静帧：{args.still}")
    if args.still and not xs:
        print("[WARN] 没有可用实例 ⇒ 不渲染静帧")
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
        print(f"报告：{args.report}")
    print(f"结论: {'OK' if report['ok'] else 'FAIL'} —— problems {report['problems']}")
    print("⚠️ lab **从不写回文件**（口径 §15.8 硬规矩 1/2：lab 是生成物、导出器硬要求恰好 1 个 Armature）")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
