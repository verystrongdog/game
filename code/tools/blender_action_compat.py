#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 verystrongdog
# SPDX-License-Identifier: GPL-3.0-or-later
"""blender_action_compat.py —— Blender **4.5 / 5.x 双兼容**的动作 API 取道层。

来源：design/presentation/Blender动作制作管线.md §七（Blender Python 参考）
      危险点表 §四「`Action.fcurves`（Blender 5.x 槽位化动作）」行

为什么需要它
------------
Blender 5.x 把 `Action` 改成 **slotted actions**：`Action.fcurves` **被移除**，曲线改从
`action.layers[0].strips[0].channelbag(slot).fcurves` 取；而且把 action 指派给
`animation_data` 之后**还必须再指 `animation_data.action_slot`**，否则那条 action
**不驱动任何东西**（实测 5.1.2：新建 action 的 `action_slot` 是 `None`）。

症状是"脚本在 4.5 上全绿、在 5.1 上直接崩"（`AttributeError: 'Action' object has no attribute 'fcurves'`），
很容易误判成"脚本坏了 / 母版坏了"。取道层把这件事收在一处，两个脚本都只调这里的函数。

用法
----
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import blender_action_compat as bac
"""

from __future__ import annotations

import bpy

def _type_exposes_fcurves() -> bool:
    """类型级判据。

    ⚠️ **不能用 `hasattr(bpy.types.Action, "fcurves")`**：那个在 **4.5 上也是 `False`**
    （RNA 的集合属性在类型上取不到、只在实例上取得到）⇒ 会把 4.5 误判成槽位化（实测踩到）。
    可靠判据是查 `bl_rna.properties`：**4.5.13 = True，5.1.2 = False**（实测）。
    """
    return any(p.identifier == "fcurves" for p in bpy.types.Action.bl_rna.properties)


#: 4.5 = False（`Action.fcurves` 在）；5.x = True（槽位化）
SLOTTED_ACTIONS = not _type_exposes_fcurves()


def describe() -> dict:
    """把版本与取道方式记进报告，便于事后归因。"""
    return {
        "blender": bpy.app.version_string,
        "slotted_actions": SLOTTED_ACTIONS,
        "fcurve_access": "layers→strips→channelbag" if SLOTTED_ACTIONS else "action.fcurves",
    }


def assign_action(anim_data, action, id_type: str = "OBJECT"):
    """把 `action` 指派给 `anim_data`。

    4.5：只设 `action`。
    5.x：**还要把 slot 指上**——动作一律有 slot；新 action 先建一个再指，
    否则 `keyframe_insert` / 烘焙写进去的东西**不会被求值**（实测：`action_slot is None`）。
    """
    anim_data.action = action
    slot_attr = "action_slot"
    if not hasattr(anim_data, slot_attr):
        return action
    slots = getattr(action, "slots", None)
    if slots is None:
        return action
    if len(slots) > 0:
        anim_data.action_slot = slots[0]
        return action
    try:
        slot = slots.new(id_type=id_type, name=action.name)
    except TypeError:                      # 参数名在个别版本上不同
        slot = slots.new(id_type, action.name)
    if slot is not None:
        anim_data.action_slot = slot
    return action


def select_pose_bones(arm_obj, predicate) -> str:
    """按谓词设置**姿态骨选择位**；返回实际用的是哪个属性（记进报告）。

    ⚠️ 选择位在两个版本上**不在同一个地方**（实测）：
      · Blender **4.5**：`Bone.select` 在、`PoseBone.select` **不在**
      · Blender **5.x**：`PoseBone.select` 在、`Bone.select` **已被移除**
    选错就报 `AttributeError: ... has no attribute 'select'`。`Bone.hide` 两侧都在，不受影响。
    """
    used = "none"
    for pb in arm_obj.pose.bones:
        if hasattr(pb, "select"):
            pb.select = predicate(pb.name)
            used = "PoseBone.select"
        elif hasattr(pb.bone, "select"):
            pb.bone.select = predicate(pb.name)
            used = "Bone.select"
        pb.bone.hide = False
    return used


def action_fcurves(action):
    """取 F-Curve 容器。

    ⚠️ 空 action（还没有任何 slot / 关键帧）在 5.x 下**取不到容器** → 返回 `None`，
    调用方必须处理（而不是当成"0 条曲线"）。
    """
    direct = getattr(action, "fcurves", None)
    if direct is not None:
        return direct
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            channelbag = getattr(strip, "channelbag", None)
            if channelbag is None:
                continue
            for slot in getattr(action, "slots", []):
                bag = channelbag(slot)
                if bag is not None:
                    return bag.fcurves
    return None


def fcurve_count(action) -> int:
    """曲线条数（容器取不到时返回 0）。"""
    curves = action_fcurves(action)
    return 0 if curves is None else len(curves)


def action_frame_range(action):
    """动作的帧范围（取不到返回 `(0.0, 0.0)`）。"""
    for attr in ("frame_range", "curve_frame_range"):
        value = getattr(action, attr, None)
        if value is not None:
            try:
                return (float(value[0]), float(value[1]))
            except (TypeError, IndexError, ValueError):
                continue
    return (0.0, 0.0)


def iter_fcurves(action):
    """遍历曲线；容器取不到时不迭代（不抛）。"""
    curves = action_fcurves(action)
    if curves is None:
        return iter(())
    return iter(curves)


def remove_fcurves_where(action, predicate) -> int:
    """按谓词删曲线（5.x 必须从 channelbag 的容器删，不能在 action 上删）。"""
    curves = action_fcurves(action)
    if curves is None:
        return 0
    doomed = [fc for fc in curves if predicate(fc)]
    for fc in doomed:
        curves.remove(fc)
    return len(doomed)
