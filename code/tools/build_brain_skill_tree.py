#!/usr/bin/env python3
"""
玻璃大脑技能树 — Blender 自动化构建脚本（v1 世代，2026-07-11）

⚠️ 世代定位：本脚本产出的是**玻璃外壳那一代**（brain_glass + 线框 + node_* 共享材质）。
当前世代是 build_brain_skill_tree_windows.py（逐脑区半透明着色，无外壳）——两者
产出不同，别混用。本脚本保留作 v1 世代的参照实现，其 API 目标为 Blender ≤3.x
（未回植 Blender 4.2/5.x 兼容：import_scene.obj / Emission 输入名 / shadow_method）。
资产身份与重建口径见 design/presentation/visualization-3d/脑模型资产登记.md。
========================================
导入 brain-for-blender OBJ, 创建玻璃脑材质, 放置 74 技能节点, 创建连线。

用法:
  方式1 (Blender 内):  Scripting 工作区 → 打开此文件 → Run Script
  方式2 (命令行):     blender --background --python code/tools/build_brain_skill_tree.py

前置:
  - blender_assets/all_obj/ 已解压 (brain-for-blender OBJ)
  - data/brain_regions.json 已生成
  - data/skill_coords.json 已生成

输出:
  - design/presentation/visualization-3d/blender_assets/build/brain_skill_tree_v1.blend  (Blender 工作文件)
  - design/presentation/visualization-3d/blender_assets/build/brain_skill_tree_v1.glb    (GLB 导出, 可选)
"""

import bpy
import json
import os
import math
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════
#  CONFIG — 根据你的环境调整
# ═══════════════════════════════════════════════════════════

# 项目根目录 (此脚本在 code/tools/ 下, 项目根是上级目录)
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

# OBJ 目录
OBJ_BASE = PROJECT_DIR / "design" / "presentation" / "visualization-3d" / "blender_assets" / "all_obj"

# 输出 —— ⚠️ 默认落 build/ 子目录，**不指向资产目录**
# 资产目录里是正典源与冻结快照，一次误运行就会覆盖（2026-09-13 事故，见
# design/presentation/visualization-3d/脑模型资产登记.md §九）
OUT_DIR = PROJECT_DIR / "design" / "presentation" / "visualization-3d" / "blender_assets" / "build"
BLEND_OUT = str(OUT_DIR / "brain_skill_tree_v1.blend")
GLB_OUT = str(OUT_DIR / "brain_skill_tree_v1.glb")

# 导入哪些 OBJ
IMPORT_PIAL_DK = True       # DK 皮层表面 (pial, 含脑沟)
IMPORT_SUBCORTICAL = True   # 皮层下结构
IMPORT_PIAL_FULL = True     # 完整半球 (玻璃脑外壳)
MAX_CORTEX_FILES = 0       # 导入皮层文件数上限 (0=全部)
MAX_SUBCORT_FILES = 0       # 导入皮层下文件上限 (0=全部)

# 是否导出
EXPORT_GLB = True           # 导出 GLB
EXPORT_BLEND = True         # 保存 .blend

# ═══════════════════════════════════════════════════════════
#  NODE CONFIG
# ═══════════════════════════════════════════════════════════

NODE_CONFIG = {
    "cognition": {
        "radius": 1.5,
        "color": (0.48, 0.56, 1.0, 1.0),   # 蓝紫
        "emit": (0.48, 0.56, 1.0),
        "geo": "icosphere",
        "description": "认知技能 (蓝紫)",
    },
    "emotion": {
        "radius": 1.7,
        "color": (0.94, 0.63, 0.38, 1.0),   # 暖橙
        "emit": (0.94, 0.63, 0.38),
        "geo": "sphere",
        "description": "情绪技能 (暖橙)",
    },
    "behavior": {
        "radius": 1.5,
        "color": (0.31, 0.76, 0.97, 1.0),   # 青蓝
        "emit": (0.31, 0.76, 0.97),
        "geo": "cube",
        "description": "行为技能 (青蓝)",
    },
    "ultimate": {
        "radius": 2.2,
        "color": (0.91, 0.82, 0.44, 1.0),   # 金色
        "emit": (0.91, 0.82, 0.44),
        "geo": "dodecahedron",
        "description": "终极技能 (金色)",
    },
}

# 连线配置
TRACT_CONFIG = {
    "unlocked": {"depth": 0.15, "color": (0.5, 0.5, 0.7, 0.6)},
    "locked": {"depth": 0.08, "color": (0.2, 0.2, 0.3, 0.2)},
}

# ═══════════════════════════════════════════════════════════
#  UTILITIES
# ═══════════════════════════════════════════════════════════

def log(msg):
    print(f"[BrainSkillTree] {msg}")


def clear_scene():
    """清空场景 (保留相机和灯光)"""
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH' or obj.type == 'EMPTY' or obj.type == 'CURVE':
            bpy.data.objects.remove(obj, do_unlink=True)
    # 清理孤立数据
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        if mat.users == 0 and not mat.name.startswith("brain_"):
            bpy.data.materials.remove(mat)


def get_collection(name, parent=None):
    """获取或创建 Collection"""
    coll = bpy.data.collections.get(name)
    if not coll:
        coll = bpy.data.collections.new(name)
        if parent:
            parent.children.link(coll)
        else:
            bpy.context.scene.collection.children.link(coll)
    return coll


def make_material(name, base_color, emission_color, alpha=1.0, transmission=0.0, roughness=0.3):
    """创建 Principled BSDF 材质"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Transmission'].default_value = transmission
    if alpha < 1.0:
        bsdf.inputs['Alpha'].default_value = alpha
        mat.blend_method = 'BLEND'
        mat.shadow_method = 'NONE'
    if emission_color:
        bsdf.inputs['Emission'].default_value = (*emission_color, 0.3)

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


# ═══════════════════════════════════════════════════════════
#  SECTION 1: IMPORT BRAIN MESH
# ═══════════════════════════════════════════════════════════

def import_brain_objs():
    """导入 brain-for-blender OBJ 文件"""
    log("=" * 50)
    log("Section 1: Import Brain Mesh OBJs")
    log("=" * 50)

    brain_coll = get_collection("BrainMesh")
    cortex_coll = get_collection("Cortex", brain_coll)
    subcort_coll = get_collection("Subcortical", brain_coll)
    full_coll = get_collection("FullHemisphere", brain_coll)

    imported = 0

    # --- Pial DK (皮层表面) ---
    if IMPORT_PIAL_DK:
        dk_dir = OBJ_BASE / "pial_DK"
        if dk_dir.is_dir():
            files = sorted([f for f in os.listdir(dk_dir) if f.endswith('.obj')])
            if MAX_CORTEX_FILES > 0:
                files = files[:MAX_CORTEX_FILES]
            log(f"Importing {len(files)} DK cortex OBJs...")
            for i, fname in enumerate(files):
                obj_path = str(dk_dir / fname)
                try:
                    bpy.ops.import_scene.obj(filepath=obj_path)
                    imported += 1
                    # 将导入的对象移到皮层 Collection
                    for obj in bpy.context.selected_objects:
                        for col in obj.users_collection:
                            col.objects.unlink(obj)
                        cortex_coll.objects.link(obj)
                except Exception as e:
                    log(f"  ⚠ {fname}: {e}")
                if i % 20 == 19:
                    log(f"  ... {i+1}/{len(files)}")

    # --- Subcortical ---
    if IMPORT_SUBCORTICAL:
        sub_dir = OBJ_BASE / "subcortical"
        if sub_dir.is_dir():
            files = sorted([f for f in os.listdir(sub_dir) if f.endswith('.obj')])
            if MAX_SUBCORT_FILES > 0:
                files = files[:MAX_SUBCORT_FILES]
            log(f"Importing {len(files)} subcortical OBJs...")
            for i, fname in enumerate(files):
                obj_path = str(sub_dir / fname)
                try:
                    bpy.ops.import_scene.obj(filepath=obj_path)
                    imported += 1
                    for obj in bpy.context.selected_objects:
                        for col in obj.users_collection:
                            col.objects.unlink(obj)
                        subcort_coll.objects.link(obj)
                except Exception as e:
                    log(f"  ⚠ {fname}: {e}")
                if i % 20 == 19:
                    log(f"  ... {i+1}/{len(files)}")

    # --- Full Hemisphere (玻璃壳) ---
    if IMPORT_PIAL_FULL:
        full_dir = OBJ_BASE / "pial_Full"
        if full_dir.is_dir():
            files = sorted([f for f in os.listdir(full_dir) if f.endswith('.obj')])
            log(f"Importing {len(files)} full hemisphere OBJs...")
            for fname in files:
                obj_path = str(full_dir / fname)
                try:
                    bpy.ops.import_scene.obj(filepath=obj_path)
                    imported += 1
                    for obj in bpy.context.selected_objects:
                        for col in obj.users_collection:
                            col.objects.unlink(obj)
                        full_coll.objects.link(obj)
                except Exception as e:
                    log(f"  ⚠ {fname}: {e}")

    log(f"Total OBJs imported: {imported}")
    return brain_coll, full_coll


# ═══════════════════════════════════════════════════════════
#  SECTION 2: GLASS BRAIN MATERIAL
# ═══════════════════════════════════════════════════════════

def apply_glass_material(brain_coll, full_coll):
    """给脑 mesh 应用玻璃材质"""
    log("=" * 50)
    log("Section 2: Glass Brain Material")
    log("=" * 50)

    # 玻璃主体材质
    glass_mat = make_material(
        "brain_glass",
        base_color=(0.53, 0.60, 0.73, 0.15),   # 冷灰蓝半透明
        emission_color=(0.07, 0.09, 0.13),
        alpha=0.15,
        transmission=0.85,
        roughness=0.3,
    )

    # 线框材质 (叠加用)
    wire_mat = make_material(
        "brain_wireframe",
        base_color=(0.20, 0.27, 0.40, 0.06),
        emission_color=(0.13, 0.20, 0.27),
        alpha=0.06,
        roughness=1.0,
    )

    count = 0
    for coll in [brain_coll, full_coll]:
        if not coll:
            continue
        for obj in coll.all_objects:
            if obj.type == 'MESH':
                # 应用玻璃材质
                if obj.data.materials:
                    obj.data.materials[0] = glass_mat
                else:
                    obj.data.materials.append(glass_mat)
                count += 1

    log(f"Applied glass material to {count} objects")

    # 为完整半球添加线框修改器
    if full_coll:
        for obj in full_coll.all_objects:
            if obj.type == 'MESH':
                mod = obj.modifiers.new(name="Wireframe", type='WIREFRAME')
                mod.thickness = 0.3
                mod.use_replace = False
                # 线框材质在第二个槽
                obj.data.materials.append(wire_mat)

    return glass_mat


# ═══════════════════════════════════════════════════════════
#  SECTION 3: PLACE SKILL NODES
# ═══════════════════════════════════════════════════════════

def create_node_geometry(name, position, branch, collection):
    """在指定位置创建技能节点几何体"""
    cfg = NODE_CONFIG.get(branch, NODE_CONFIG["cognition"])
    x, y, z = position

    if cfg["geo"] == "icosphere":
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1, radius=cfg["radius"], location=(x, y, z))
    elif cfg["geo"] == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=cfg["radius"], location=(x, y, z))
    elif cfg["geo"] == "cube":
        bpy.ops.mesh.primitive_cube_add(
            size=cfg["radius"] * 2.5, location=(x, y, z))
    elif cfg["geo"] == "dodecahedron":
        # Blender 没有原生 dodecahedron, 用低面数 icosphere 代替
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1, radius=cfg["radius"], location=(x, y, z))

    obj = bpy.context.active_object
    obj.name = name
    obj["skill_id"] = name
    obj["branch"] = branch

    # 材质
    mat_name = f"node_{branch}"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = make_material(mat_name, cfg["color"], cfg["emit"], alpha=0.9)
    obj.data.materials.append(mat)

    # 移到 Collection
    for col in obj.users_collection:
        col.objects.unlink(obj)
    collection.objects.link(obj)

    return obj


def place_skill_nodes():
    """从 skill_coords.json 放置所有 74 技能节点"""
    log("=" * 50)
    log("Section 3: Place Skill Nodes")
    log("=" * 50)

    # 加载数据
    regions_path = PROJECT_DIR / "data" / "brain_regions.json"
    skills_path = PROJECT_DIR / "data" / "skill_coords.json"

    if not skills_path.exists():
        log(f"⚠ skill_coords.json not found at {skills_path}")
        log("  Run: python code/tools/map_skills_to_regions.py")
        return

    with open(skills_path, "r", encoding="utf-8") as f:
        skills_data = json.load(f)

    with open(regions_path, "r", encoding="utf-8") as f:
        regions_data = json.load(f)

    # 创建 Collection 层级
    nodes_root = get_collection("SkillNodes")
    branch_collections = {}
    for branch in ["cognition", "emotion", "behavior", "ultimate"]:
        branch_collections[branch] = get_collection(branch.capitalize(), nodes_root)

    # 放置节点
    placed = 0
    node_objects = {}  # id → Blender object

    for skill in skills_data["skills"]:
        sid = skill["id"]
        name = skill["name"]
        branch = skill["branch"]

        # 获取坐标 (优先 FreeSurfer, 回退到 game_xyz)
        region_key = skill.get("region_matched")
        coords = None

        if region_key and region_key in regions_data["regions"]:
            region = regions_data["regions"][region_key]
            fs_coords = region.get("fs_xyz")
            if fs_coords:
                # 应用半球镜像
                pad_x = skill["pad_xyz"][0]
                fs_x, fs_y, fs_z = fs_coords
                if pad_x > 0.05:
                    coords = (abs(fs_x), fs_y, fs_z)
                elif pad_x < -0.05:
                    coords = (-abs(fs_x), fs_y, fs_z)
                else:
                    coords = (0, fs_y, fs_z)

        if not coords:
            # 回退: 使用 game_xyz 按比例放大到 FreeSurfer 空间
            gx, gy, gz = skill["game_xyz_new"]
            coords = (gx * 70.0, gz * 120.0 / 0.85, (gy - 0.55) * 75.0)

        # 创建节点
        obj = create_node_geometry(sid, coords, branch, branch_collections[branch])
        obj.name = f"{sid}_{name}"
        obj["skill_name"] = name
        obj["skill_id"] = sid
        obj["branch"] = branch
        obj["tier"] = str(skill.get("tier", ""))
        obj["region"] = skill.get("region", "")
        # 存储坐标
        obj["fs_xyz"] = coords
        obj["game_xyz"] = skill["game_xyz_new"]

        node_objects[sid] = obj
        placed += 1

    log(f"Placed {placed} skill nodes")
    log(f"  cognition: {sum(1 for s in skills_data['skills'] if s['branch']=='cognition')}")
    log(f"  emotion:   {sum(1 for s in skills_data['skills'] if s['branch']=='emotion')}")
    log(f"  behavior:  {sum(1 for s in skills_data['skills'] if s['branch']=='behavior')}")
    log(f"  ultimate:  {sum(1 for s in skills_data['skills'] if s['branch']=='ultimate')}")

    return node_objects


# ═══════════════════════════════════════════════════════════
#  SECTION 4: WHITE MATTER TRACTS (CONNECTIONS)
# ═══════════════════════════════════════════════════════════

def create_tract_connections(node_objects):
    """创建技能节点之间的 Bezier 连线 (DTI tractography 风格)"""
    log("=" * 50)
    log("Section 4: White Matter Tracts")
    log("=" * 50)

    # 前置关系 — 从 skill_coords.json 的 prereqs 字段读取
    # (如果 JSON 中没有, 则从 HTML 提取或手动指定)
    skills_path = PROJECT_DIR / "data" / "skill_coords.json"
    with open(skills_path, "r", encoding="utf-8") as f:
        skills_data = json.load(f)

    prereqs = skills_data.get("prereqs", [])
    if not prereqs:
        log("No prereqs found in skill_coords.json — extracting from HTML...")
        prereqs = extract_prereqs_from_html()
        # 回存
        skills_data["prereqs"] = prereqs
        with open(skills_path, "w", encoding="utf-8") as f:
            json.dump(skills_data, f, ensure_ascii=False, indent=2)

    tract_coll = get_collection("Tracts")
    created = 0

    for pre in prereqs:
        if len(pre) >= 2:
            child_id, parent_id = pre[0], pre[1]
            if child_id in node_objects and parent_id in node_objects:
                child_obj = node_objects[child_id]
                parent_obj = node_objects[parent_id]
                create_single_tract(child_obj, parent_obj, tract_coll)
                created += 1

    log(f"Created {created} tract connections")


def extract_prereqs_from_html():
    """从 HTML 提取前置关系"""
    import re
    html_path = PROJECT_DIR / "design" / "presentation" / "visualization-3d" / "大脑技能树3D.html"
    if not html_path.exists():
        return []

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 匹配 prereqs 数组: [['id1','id2'], ['id3','id4'], ...]
    match = re.search(r"prereqs\s*=\s*(\[.*?\]);", content, re.DOTALL)
    if not match:
        # 尝试匹配 var prereqs = [...]
        match = re.search(r"var\s+prereqs\s*=\s*(\[.*?\]);", content, re.DOTALL)

    if match:
        prereqs_str = match.group(1)
        # 提取所有 ['xxx','yyy'] 对
        pairs = re.findall(r"\['([^']+)'\s*,\s*'([^']+)'\]", prereqs_str)
        return [[a, b] for a, b in pairs]

    return []


def create_single_tract(from_obj, to_obj, collection):
    """在两个节点之间创建 Bezier 曲线连线"""
    from_pos = from_obj.location
    to_pos = to_obj.location

    # 中点 + 垂直偏移 (模仿纤维束弧线)
    mid_x = (from_pos.x + to_pos.x) / 2
    mid_y = (from_pos.y + to_pos.y) / 2
    mid_z = (from_pos.z + to_pos.z) / 2 + 3.0  # 向上偏移

    # 创建 Bezier 曲线
    curve_data = bpy.data.curves.new(name=f"tract_{from_obj.name}_{to_obj.name}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.15  # 管道粗细

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(2)  # 3 个控制点

    # 起点
    spline.bezier_points[0].co = from_pos
    spline.bezier_points[0].handle_right_type = 'AUTO'
    # 中点 (弯曲)
    spline.bezier_points[1].co = (mid_x, mid_y, mid_z)
    spline.bezier_points[1].handle_left_type = 'AUTO'
    spline.bezier_points[1].handle_right_type = 'AUTO'
    # 终点
    spline.bezier_points[2].co = to_pos
    spline.bezier_points[2].handle_left_type = 'AUTO'

    curve_obj = bpy.data.objects.new(f"tract_{from_obj.name}_{to_obj.name}", curve_data)
    collection.objects.link(curve_obj)

    # 材质
    mat_name = "tract_unlocked"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = make_material(mat_name,
            base_color=(0.4, 0.5, 0.7, 0.5),
            emission_color=(0.3, 0.4, 0.6),
            alpha=0.5, roughness=0.5)
    curve_obj.data.materials.append(mat)

    return curve_obj


# ═══════════════════════════════════════════════════════════
#  SECTION 5: LIGHTING & CAMERA
# ═══════════════════════════════════════════════════════════

def setup_lighting_and_camera():
    """设置光照和相机"""
    log("=" * 50)
    log("Section 5: Lighting & Camera")
    log("=" * 50)

    # 删除默认灯光
    for obj in list(bpy.data.objects):
        if obj.type == 'LIGHT' and obj.name in ['Light', 'Point', 'Sun', 'Spot']:
            bpy.data.objects.remove(obj, do_unlink=True)

    # 主光 (右上方)
    bpy.ops.object.light_add(type='AREA', location=(80, -40, 80))
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 300
    key.data.color = (1.0, 0.95, 0.85)

    # 补光 (左下方)
    bpy.ops.object.light_add(type='AREA', location=(-60, 30, -40))
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 150
    fill.data.color = (0.5, 0.6, 0.8)

    # 底部柔光
    bpy.ops.object.light_add(type='AREA', location=(0, 0, -80))
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 80
    rim.data.color = (0.2, 0.25, 0.35)

    # 环境光
    bpy.context.scene.world.use_nodes = True
    bg = bpy.context.scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.04, 0.04, 0.08, 1.0)
        bg.inputs["Strength"].default_value = 0.3

    # 相机
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
        cam.location = (0, -200, 40)
        cam.rotation_euler = (math.radians(80), 0, 0)
        cam.data.lens = 50

    log("Lighting setup complete")


# ═══════════════════════════════════════════════════════════
#  SECTION 6: RENDER SETTINGS
# ═══════════════════════════════════════════════════════════

def setup_render():
    """配置渲染设置 (Blender 3.0 兼容)"""
    log("=" * 50)
    log("Section 6: Render Settings")
    log("=" * 50)

    scene = bpy.context.scene

    # EEVEE 设置
    scene.render.engine = 'BLENDER_EEVEE'
    try:
        scene.eevee.use_bloom = True
        scene.eevee.bloom_threshold = 0.8
        scene.eevee.bloom_intensity = 0.3
        scene.eevee.bloom_radius = 6.0
    except Exception:
        log("  Bloom not available (may need Blender >= 3.2)")

    # 屏幕空间反射
    try:
        scene.eevee.use_ssr = True
        scene.eevee.ssr_quality = 0.5
    except Exception:
        log("  SSR not available")

    # 分辨率
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    log("EEVEE render settings applied")


# ═══════════════════════════════════════════════════════════
#  SECTION 7: EXPORT
# ═══════════════════════════════════════════════════════════

def export():
    """导出 .blend 和 .glb"""
    os.makedirs(OUT_DIR, exist_ok=True)
    if EXPORT_BLEND:
        log(f"Saving .blend → {BLEND_OUT}")
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)

    if EXPORT_GLB:
        log(f"Exporting .glb → {GLB_OUT}")
        bpy.ops.object.select_all(action='DESELECT')
        for coll_name in ["BrainMesh", "SkillNodes", "Tracts"]:
            coll = bpy.data.collections.get(coll_name)
            if coll:
                for obj in coll.all_objects:
                    obj.select_set(True)

        try:
            bpy.ops.export_scene.gltf(
                filepath=GLB_OUT,
                use_selection=True,
                export_format='GLB',
            )
            log("GLB export complete")
        except Exception as e:
            log(f"GLB export failed: {e}")
            # 尝试没有 use_selection
            try:
                bpy.ops.export_scene.gltf(
                    filepath=GLB_OUT,
                    export_format='GLB',
                )
                log("GLB export complete (all objects)")
            except Exception as e2:
                log(f"GLB export also failed: {e2}")


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

def main():
    log("╔══════════════════════════════════════════════╗")
    log("║  🧠 玻璃大脑技能树 — Blender 自动化构建      ║")
    log("╚══════════════════════════════════════════════╝")

    # 0. 清空场景
    log("\n>>> Clearing scene...")
    clear_scene()

    # 1. 导入脑 OBJ
    brain_coll, full_coll = import_brain_objs()

    # 2. 玻璃材质
    apply_glass_material(brain_coll, full_coll)

    # 3. 放置技能节点
    node_objects = place_skill_nodes()

    # 4. 连线
    create_tract_connections(node_objects)

    # 5. 灯光
    setup_lighting_and_camera()

    # 6. 渲染设置
    setup_render()

    # 7. 导出
    export()

    log("\n╔══════════════════════════════════════════════╗")
    log("║  ✅ 构建完成!                                 ║")
    if EXPORT_BLEND:
        log(f"║  .blend: {BLEND_OUT}")
    if EXPORT_GLB:
        log(f"║  .glb:   {GLB_OUT}")
    log("║  在 Blender 中打开 .blend 查看和微调           ║")
    log("╚══════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
