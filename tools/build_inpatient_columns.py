"""
一层住院部承重柱 — 基于 Desmos 柱网交点自动生成

数据来源: 一层主园区，承重柱交点 (Desmos)
https://www.desmos.com/calculator/pmik7o5ykk

柱网描述: "回"字形建筑，中庭无柱
  - 北侧 (x ≤ -22.5, 0<y<55.2):  两排柱, 6.9m 等距 (x=-39, -32.4, -29.4, -22.5)
  - 南侧 (x ≥ 22.5, 0<y<55.2):   两排柱, 6.9m 等距
  - 东端 (y ≥ 55.2):             2 排, 全宽
  - 西端 (y ≤ 0):                5 排, 全宽
  总计: 145 根承重柱

用法:
  1. 打开 Blender → Scripting 工作区 → 打开此文件 → Run Script
  2. 或命令行:
     blender --background --python build_inpatient_columns.py

生成物:
  - 集合 "一层住院部承重柱" 下按区域分 4 个子集合
  - 所有柱子共享同一个 mesh (0.6×0.6×3.9m)
  - 每个区域有根节点 Empty (PLAIN_AXES) 便于整体移动
"""

import bpy
import bmesh

# ---------------------------------------------------------------------------
# 参数 (可调)
# ---------------------------------------------------------------------------
TOP_COLLECTION_NAME = "一层住院部承重柱"
SHARED_MESH_NAME = "承重柱_共享网格"
COLUMN_PREFIX = "承重柱"

COLUMN_SIZE = 0.6       # 柱截面边长 (m) — 方柱 600×600mm
COLUMN_HEIGHT = 4.2     # 首层层高 (m)
CLEAR_PREVIOUS = True   # 运行前清空已有集合

# ---------------------------------------------------------------------------
# Desmos 读出的线段数据 (单位: 米)
# ---------------------------------------------------------------------------

# 竖向轴线: x -> [(y_lo, y_hi), ...]
VERTICAL_SEGMENTS = {
    # 住院部主楼
    -39:   [(-22.5, 55.2)],
    -32.4: [(-22.5, 58.2)],
    -29.4: [(-22.5, 55.2)],
    -22.5: [(-22.5, 58.2)],
    -15:   [(-22.5, 0), (55.2, 58.2)],
    -7.5:  [(-22.5, 0), (55.2, 58.2)],
    0:     [(-22.5, 0), (55.2, 58.2)],
    7.5:   [(-22.5, 0), (55.2, 58.2)],
    15:    [(-22.5, 0), (55.2, 58.2)],
    22.5:  [(-22.5, 58.2)],
    29.1:  [(-22.5, 55.2)],
    32.1:  [(-22.5, 58.2)],
    39:    [(-22.5, 55.2)],
    # 西侧延伸
    -45:   [(-3, 0)],
    -52:   [(-3, 0)],
    -58:   [(-40.5, 19.5)],
    -65.5: [(-40.5, 19.5)],
    -73:   [(-40.5, 19.5)],
    -80.5: [(-40.5, 19.5)],
    -88:   [(-40.5, 19.5)],
    -95.5: [(-40.5, 19.5)],
    # 东侧延伸
    46.5:  [(-3, 0)],
    54:    [(-3, 0)],
    61.5:  [(-22.5, 0), (48, 64.8)],
    69:    [(-22.5, 0), (48, 64.8)],
    76.5:  [(-22.5, 0), (6.9, 41.4), (48.3, 64.8)],
    84:    [(-22.5, 64.8)],
    90.9:  [(-22.5, 64.8)],
    93.9:  [(-22.5, 64.8)],
    100.8: [(-22.5, 64.8)],
    102.8: [(6.9, 41.4)],
}

# 横向轴线: y -> [(x_lo, x_hi), ...]
HORIZONTAL_SEGMENTS = {
    64.8:  [(61.5, 100.8)],
    58.2:  [(-32.4, 32.1), (61.5, 100.8)],
    55.2:  [(-39, 39), (61.5, 100.8)],
    51.75: [(-39, -32.4), (22.5, 29.1)],
    48.3:  [(-39, -22.5), (22.5, 39), (61.5, 100.8)],
    41.4:  [(-39, -22.5), (22.5, 39), (76.5, 102.8)],
    34.5:  [(-39, -22.5), (22.5, 39), (76.5, 102.8)],
    27.6:  [(-39, -22.5), (22.5, 39), (76.5, 102.8)],
    20.7:  [(-39, -22.5), (22.5, 39), (76.5, 102.8)],
    19.5:  [(-95.5, -58)],
    13.8:  [(-39, -22.5), (22.5, 39), (76.5, 102.8)],
    12:    [(-95.5, -58)],
    6.9:   [(-39, -22.5), (22.5, 39), (76.5, 102.8)],
    4.5:   [(-95.5, -58)],
    3.45:  [(-39, -32.4), (22.5, 29.1)],
    0:     [(-39, 39)],
    -3:    [(-95.5, -39), (-15, 15), (39, 100.8)],
    -7.5:  [(-39, -22.5), (22.5, 39)],
    -9:    [(61.5, 100.8)],
    -10.5: [(-95.5, -58)],
    -12:   [(-15, 15)],
    -15:   [(-39, 39), (61.5, 100.8)],
    -18:   [(-95.5, -58)],
    -22.5: [(-39, 39), (61.5, 100.8)],
    -25.5: [(-95.5, -58)],
    -33:   [(-95.5, -58)],
    -40.5: [(-95.5, -58)],
}


# ---------------------------------------------------------------------------
# 交点计算
# ---------------------------------------------------------------------------

def _in_intervals(val, segments):
    """val 是否落在 segments 的任一区间内 (闭区间)."""
    return any(lo <= val <= hi for lo, hi in segments)


def compute_all_intersections():
    """计算所有竖线 × 横线的交点 (柱位)."""
    points = []
    for x, vy_segs in VERTICAL_SEGMENTS.items():
        for y, hx_segs in HORIZONTAL_SEGMENTS.items():
            if _in_intervals(y, vy_segs) and _in_intervals(x, hx_segs):
                points.append((x, y))
    return points



# ---------------------------------------------------------------------------
# Blender 工具函数
# ---------------------------------------------------------------------------

def get_or_create_collection(name, parent=None):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
    if parent is None:
        if collection.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(collection)
    else:
        if collection.name not in parent.children:
            parent.children.link(collection)
    return collection


def ensure_collection_linked(collection, parent):
    if collection.name not in parent.children:
        parent.children.link(collection)


def clear_collection_recursive(collection):
    for child in list(collection.children):
        clear_collection_recursive(child)
        collection.children.unlink(child)
        if child.users == 0:
            bpy.data.collections.remove(child)
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def remove_existing_shared_mesh():
    mesh = bpy.data.meshes.get(SHARED_MESH_NAME)
    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)


def create_shared_column_mesh():
    mesh = bpy.data.meshes.get(SHARED_MESH_NAME)
    if mesh is not None:
        return mesh

    mesh = bpy.data.meshes.new(SHARED_MESH_NAME)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    for vert in bm.verts:
        vert.co.x *= COLUMN_SIZE
        vert.co.y *= COLUMN_SIZE
        vert.co.z *= COLUMN_HEIGHT
        vert.co.z += COLUMN_HEIGHT / 2.0   # 原点在底面中心

    bm.to_mesh(mesh)
    bm.free()
    return mesh


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    # 1. 计算所有交点
    all_points = compute_all_intersections()
    if not all_points:
        print("❌ 未计算出任何柱位，请检查线段数据")
        return

    print(f"柱位计算完成，共 {len(all_points)} 根")

    # 3. 创建 Blender 对象
    top = get_or_create_collection(TOP_COLLECTION_NAME)

    if CLEAR_PREVIOUS:
        clear_collection_recursive(top)

    remove_existing_shared_mesh()
    mesh = create_shared_column_mesh()

    # 总根 Empty — 选它就能整体移动
    master_root = bpy.data.objects.new(f"{TOP_COLLECTION_NAME}_总根", None)
    master_root.empty_display_type = "PLAIN_AXES"
    master_root.location = (0.0, 0.0, 0.0)
    top.objects.link(master_root)

    sorted_points = sorted(all_points, key=lambda p: (p[1], p[0]))

    for index, (x, y) in enumerate(sorted_points, start=1):
        obj = bpy.data.objects.new(
            f"{COLUMN_PREFIX}_{index:03d}", mesh
        )
        obj.location = (x, y, 0)       # 原点 = 交点底面中心
        obj.parent = master_root
        top.objects.link(obj)

    print(f"\n✅ 已生成 {len(all_points)} 根承重柱（共用 1 个 mesh）→ 集合: {TOP_COLLECTION_NAME}")
    print(f"   柱截面: {COLUMN_SIZE}×{COLUMN_SIZE}m  柱高: {COLUMN_HEIGHT}m")
    print(f"   整体挪动: 选中「{TOP_COLLECTION_NAME}_总根」→ G 拖动")
    print(f"   虚线太多? 3D Viewport 右上 Overlay 下拉 → 取消 Relationship Lines")


if __name__ == "__main__":
    main()
