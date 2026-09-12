#!/usr/bin/env python3
"""
楼梯自动建模 — 13 阶直跑楼梯

参数:
  踏步高 (riser):     0.16 m
  踏步深 (tread):     0.28 m
  楼梯宽 (width):     1.425 m
  阶数:               13 阶

用法:
  1. 打开 Blender → Scripting 工作区 → 打开此文件 → Run Script
  2. 或命令行:
     blender --background --python code/tools/build_stairs.py

生成物:
  - 集合 "楼梯" 下 13 阶踏步
  - 所有踏步共用同一个 mesh
  - 总根 Empty (PLAIN_AXES) 便于整体移动
"""

import bpy
import bmesh

# ---------------------------------------------------------------------------
# 参数 (可调)
# ---------------------------------------------------------------------------
TOP_COLLECTION_NAME = "楼梯"
SHARED_MESH_NAME = "踏步_共享网格"
STEP_PREFIX = "踏步"

STEP_RISER = 0.16       # 踏步高 (m)
STEP_TREAD = 0.28       # 踏步深 (m)
STEP_WIDTH = 1.425      # 楼梯宽 (m)
STEP_COUNT = 13         # 阶数

CLEAR_PREVIOUS = True   # 运行前清空已有集合
STAIR_DIRECTION = "X"   # 楼梯上升方向: "X" | "Y" | "-X" | "-Y"

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


def create_shared_step_mesh():
    """创建一块踏步的共享 mesh：原点在底面中心。"""
    mesh = bpy.data.meshes.get(SHARED_MESH_NAME)
    if mesh is not None:
        return mesh

    mesh = bpy.data.meshes.new(SHARED_MESH_NAME)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)

    # 默认立方体 ±0.5，缩放并抬高到 Z≥0
    for vert in bm.verts:
        vert.co.x *= STEP_TREAD
        vert.co.y *= STEP_WIDTH
        vert.co.z *= STEP_RISER
        vert.co.z += STEP_RISER / 2.0   # 原点在底面中心

    bm.to_mesh(mesh)
    bm.free()
    return mesh


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    # 1. 清空已有
    top = get_or_create_collection(TOP_COLLECTION_NAME)

    if CLEAR_PREVIOUS:
        clear_collection_recursive(top)

    remove_existing_shared_mesh()
    mesh = create_shared_step_mesh()

    # 2. 总根 Empty
    master_root = bpy.data.objects.new(f"{TOP_COLLECTION_NAME}_总根", None)
    master_root.empty_display_type = "PLAIN_AXES"
    master_root.location = (0.0, 0.0, 0.0)
    top.objects.link(master_root)

    # 3. 方向 → (dx, dy) 每阶位移量
    direction_map = {
        "X":  (1, 0),
        "-X": (-1, 0),
        "Y":  (0, 1),
        "-Y": (0, -1),
    }
    dx_sign, dy_sign = direction_map.get(STAIR_DIRECTION, (1, 0))

    # 4. 逐阶放置
    for i in range(STEP_COUNT):
        obj = bpy.data.objects.new(f"{STEP_PREFIX}_{i+1:02d}", mesh)
        obj.location = (
            i * STEP_TREAD * dx_sign,
            i * STEP_TREAD * dy_sign,
            i * STEP_RISER,           # 底面 Z
        )
        obj.parent = master_root
        top.objects.link(obj)

    # 5. 打印摘要
    total_rise = STEP_COUNT * STEP_RISER
    total_run = STEP_COUNT * STEP_TREAD

    print(f"\n✅ 已生成 {STEP_COUNT} 阶楼梯 → 集合: {TOP_COLLECTION_NAME}")
    print(f"   踏步: {STEP_TREAD}m 深 × {STEP_WIDTH}m 宽 × {STEP_RISER}m 高")
    print(f"   总高: {total_rise:.2f}m  总深: {total_run:.2f}m")
    print(f"   方向: {STAIR_DIRECTION}")
    print(f"   整体挪动: 选中「{TOP_COLLECTION_NAME}_总根」→ G 拖动")
    print(f"   虚线太多? 3D Viewport 右上 Overlay 下拉 → 取消 Relationship Lines")


if __name__ == "__main__":
    main()
