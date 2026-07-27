#!/usr/bin/env python3
"""
一层主园区 承重柱 — 自动放置 (Blender 脚本)
=============================================
从 Desmos 平面图线条方程精确计算所有承重柱交点，
直接在 Blender 中创建 294 根承重柱。

数据源: 一层主园区，承重柱交点 _ Desmos.pdf
承重柱: 60cm × 60cm × 4.2m, 原点 = 地面中心 = 给定交点

用法:
  # 仅计算、查看点位（不需要 Blender）
  python3 tools/place_load_columns.py --calc

  # 在 Blender 中运行（放置全部柱子）
  blender --background --python tools/place_load_columns.py
  或: Blender 内 Scripting 工作区 → 打开此文件 → Run Script
"""

import sys

# ═══════════════════════════════════════════════════════════
#  数据: Desmos 线段定义（单位：米）
#  竖线 = (x, [(y_lo, y_hi), ...])  — 每条竖线可有多个不连续 y 段
#  横线 = (y, [(x_lo, x_hi), ...])  — 每条横线可有多个不连续 x 段
# ═══════════════════════════════════════════════════════════

VERTICAL_LINES = [
    # ── 中央主楼 ──
    (0,      [(-22.5, 0), (55.2, 58.2)]),
    (7.5,    [(-22.5, 0), (55.2, 58.2)]),
    (15,     [(-22.5, 0), (55.2, 58.2)]),
    (22.5,   [(-22.5, 58.2)]),
    (29.1,   [(-22.5, 55.2)]),
    (32.1,   [(-22.5, 58.2)]),
    (39,     [(-22.5, 55.2)]),
    (-7.5,   [(-22.5, 0), (55.2, 58.2)]),
    (-15,    [(-22.5, 0), (55.2, 58.2)]),
    (-22.5,  [(-22.5, 58.2)]),
    (-29.4,  [(-22.5, 55.2)]),
    (-32.4,  [(-22.5, 58.2)]),
    (-39,    [(-22.5, 55.2)]),
    # ── 左翼 ──
    (-45,    [(-3, 0)]),
    (-52,    [(-3, 0)]),
    (-58,    [(-40.5, 19.5)]),
    (-65.5,  [(-40.5, 19.5)]),
    (-73,    [(-40.5, 19.5)]),
    (-80.5,  [(-40.5, 19.5)]),
    (-88,    [(-40.5, 19.5)]),
    (-95.5,  [(-40.5, 19.5)]),
    # ── 右翼 ──
    (46.5,   [(-3, 0)]),
    (54,     [(-3, 0)]),
    (61.5,   [(-22.5, 0), (48, 64.8)]),
    (69,     [(-22.5, 0), (48, 64.8)]),
    (76.5,   [(-22.5, 0), (6.9, 41.4), (48.3, 64.8)]),
    (84,     [(-22.5, 64.8)]),
    (90.9,   [(-22.5, 64.8)]),
    (93.9,   [(-22.5, 64.8)]),
    (100.8,  [(-22.5, 64.8)]),
    (102.8,  [(6.9, 41.4)]),
]

HORIZONTAL_LINES = [
    # ── 中央主楼 ──
    (58.2,   [(-32.1, 32.1), (61.5, 100.8)]),
    (64.8,   [(61.5, 100.8)]),
    (55.2,   [(-39, 39), (61.5, 100.8)]),
    (0,      [(-39, 39)]),
    (6.9,    [(-39, -22.5), (22.5, 39), (76.5, 102.8)]),
    (3.45,   [(-39, -32.4), (22.5, 29.1)]),
    (51.75,  [(-39, -32.4), (22.5, 29.1)]),
    (13.8,   [(-39, -22.5), (22.5, 39), (76.5, 102.8)]),
    (20.7,   [(-39, -22.5), (22.5, 39), (76.5, 102.8)]),
    (27.6,   [(-39, -22.5), (22.5, 39), (76.5, 102.8)]),
    (34.5,   [(-39, -22.5), (22.5, 39), (76.5, 102.8)]),
    (41.4,   [(-39, -22.5), (22.5, 39), (76.5, 102.8)]),
    (48.3,   [(-39, -22.5), (22.5, 39), (61.5, 100.8)]),
    (-3,     [(-95.5, -39), (-15, 15), (39, 100.8)]),
    (-7.5,   [(-39, -22.5), (22.5, 39)]),
    (-12,    [(-15, 15)]),
    (-15,    [(-39, 39), (61.5, 100.8)]),
    (-22.5,  [(-39, 39), (61.5, 100.8)]),
    # ── 左翼 ──
    (4.5,    [(-95.5, -58)]),
    (12,     [(-95.5, -58)]),
    (19.5,   [(-95.5, -58)]),
    (-10.5,  [(-95.5, -58)]),
    (-18,    [(-95.5, -58)]),
    (-25.5,  [(-95.5, -58)]),
    (-33,    [(-95.5, -58)]),
    (-40.5,  [(-95.5, -58)]),
    # ── 右翼 ──
    (-9,     [(61.5, 100.8)]),
]

# 承重柱规格
COLUMN_SIZE = 0.6       # m, 正方形截面边长 (60cm)
COLUMN_HEIGHT = 4.2     # m, 柱高
COLUMN_Z = 0.0          # m, 地面高度


# ═══════════════════════════════════════════════════════════
#  纯 Python 部分: 交点计算（Blender 内外通用）
# ═══════════════════════════════════════════════════════════

def _in_any_segment(segments, val):
    """val 是否落在任一闭区间 [lo, hi] 内"""
    for lo, hi in segments:
        if lo <= val <= hi:
            return True
    return False


def compute_intersections():
    """
    遍历所有竖线×横线，交点有效当且仅当:
      x ∈ 横线的某 x 段  AND  y ∈ 竖线的某 y 段
    返回去重排序后的 (x, y) 列表。
    """
    pts = set()
    for x, y_ranges in VERTICAL_LINES:
        for y, x_ranges in HORIZONTAL_LINES:
            if _in_any_segment(x_ranges, x) and _in_any_segment(y_ranges, y):
                pts.add((x, y))
    return sorted(pts, key=lambda p: (-p[1], p[0]))


# ═══════════════════════════════════════════════════════════
#  --calc 模式: 纯 Python 计算 + 打印（不需要 Blender）
# ═══════════════════════════════════════════════════════════

def _print_calc():
    points = compute_intersections()

    # 按区域分
    central = [(x, y) for x, y in points if -40 < x < 44]
    left    = [(x, y) for x, y in points if x <= -40]
    right   = [(x, y) for x, y in points if x >= 44]
    zones = [("中央主楼", central), ("左翼", left), ("右翼", right)]

    print(f"\n{'='*60}")
    print(f"  一层主园区 承重柱交点")
    print(f"  规格: {COLUMN_SIZE}m×{COLUMN_SIZE}m×{COLUMN_HEIGHT}m  |  原点=地面中心")
    print(f"  总计: {len(points)} 根")
    print(f"{'='*60}")

    for name, pts in zones:
        print(f"\n  ▸ {name} ({len(pts)} 根)")
        print(f"  {'─'*50}")
        for i, (x, y) in enumerate(pts):
            print(f"  {i+1:3d}.  ({x:+7.2f}, {y:+7.2f})")

    print(f"\n{'='*60}")
    print(f"  区域统计:")
    for name, pts in zones:
        if pts:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            print(f"    {name}: {len(pts):3d} 根  |  x∈[{min(xs):+.1f}, {max(xs):+.1f}]  y∈[{min(ys):+.1f}, {max(ys):+.1f}]")
    print(f"    {'─'*45}")
    print(f"    合计: {len(points):3d} 根")
    print(f"{'='*60}\n")


# ═══════════════════════════════════════════════════════════
#  Blender 部分: 在场景中放置承重柱
# ═══════════════════════════════════════════════════════════

def _place_in_blender():
    import bpy

    points = compute_intersections()
    total = len(points)

    # ── 材质 ──
    mat_name = "Concrete_Column"
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.65, 0.63, 0.60, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.85
            bsdf.inputs["Specular IOR Level"].default_value = 0.1

    # ── Collection ──
    col_name = "承重柱_一层主园区"
    col = bpy.data.collections.get(col_name)
    if col is None:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    # ── 确保 Object 模式 ──
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    print(f"\n{'='*60}")
    print(f"  一层主园区 承重柱 — Blender 自动放置")
    print(f"  总计 {total} 根  |  {COLUMN_SIZE}m×{COLUMN_SIZE}m×{COLUMN_HEIGHT}m")
    print(f"  原点 = 地面中心 = 交点坐标")
    print(f"{'='*60}\n")

    half_h = COLUMN_HEIGHT / 2.0  # 几何中心到地面的距离

    for i, (x, y) in enumerate(points):
        # 创建 1m 立方体 → 缩放 → 原点设在底面中心
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(x, y, half_h)  # 底面正好在 z=0
        )
        obj = bpy.context.active_object
        obj.name = f"Column_{i+1:04d}"

        # 缩放到目标尺寸
        obj.scale = (COLUMN_SIZE, COLUMN_SIZE, COLUMN_HEIGHT)
        bpy.ops.object.transform_apply(scale=True)

        # 原点移到地面中心 (x, y, 0) = 给定的交点
        bpy.context.scene.cursor.location = (x, y, 0.0)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        # 材质
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        # 移入目标 Collection
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)

        if (i + 1) % 50 == 0:
            print(f"  已放置 {i+1}/{total} 根...")

    # 恢复 3D 光标到原点
    bpy.context.scene.cursor.location = (0, 0, 0)

    print(f"\n  完成! 共放置 {total} 根承重柱。")
    print(f"  Collection: '{col_name}'  |  材质: '{mat_name}'")
    print(f"{'='*60}\n")


# ═══════════════════════════════════════════════════════════
#  入口
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    if "--calc" in sys.argv:
        _print_calc()
    else:
        _place_in_blender()
