#!/usr/bin/env python3
"""
精神专科医院 3D 模型自动检查脚本
用法:
  blender --background --python check_model.py -- file.blend
  blender --background --python check_model.py -- file.blend --baseline
  blender --background --python check_model.py -- file.blend --phase 1A
  blender --background --python check_model.py -- file.glb

检查 .blend 和 .glb 文件的几何精度、重叠、缝隙、命名、UV、碰撞体、面数、材质。
--baseline: 所有问题降级为 INFO（摸底模式）
--phase:    按 PHASE_SKIP 跳过当前阶段不适用的检查
"""

import bpy
import sys
import os
import json
import re
import time
from math import radians
from collections import defaultdict
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

# ============================================================
# CONFIG — 所有阈值集中管理，改一个全局生效
# ============================================================

CONFIG = {
    # 几何精度
    "wall_thickness": {"min": 0.15, "max": 0.40},  # m
    "slab_thickness": {"min": 0.15, "max": 0.25},  # m
    "column_grid": 3.6,       # 开间模数 (m)
    "grid_tolerance": 0.05,   # 柱网对齐公差 (m)
    "floor_z_tolerance": 0.05, # 楼板标高公差 (m)

    # 重叠检测
    "overlap_min_volume": 1e-6,  # m³, 最小报告体积
    "overlap_sample_points": 100, # BVH 射线采样点数

    # 缝隙检测
    "gap_max": 0.010,  # m, 最大允许缝隙 (10mm, 建筑公差)
    "gap_search_radius": 1.0,  # m, 缝隙搜索半径

    # UV 检查
    "uv_island_overlap_max": 0.05,  # 5%
    "uv_density_deviation_max": 3.0,  # 3×

    # 面数限制
    "face_count_building_warn": 500000,
    "face_count_room_warn": 5000,

    # 碰撞体
    "collision_deviation_max": 0.05,  # m, 碰撞体与视觉体最大允许偏差

    # 门洞偏移
    "beam_door_overlap_threshold": 0.001,  # m³
    "door_offset_min": 0.3,  # m

    # 楼梯
    "stair_riser": 0.150,   # 踏步高 (m)
    "stair_tread": 0.280,   # 踏步宽 (m)

    # 门斗
    "door_recess_depth": 0.30,  # m

    # 女儿墙
    "parapet_height": 3.5,  # m

    # 标准楼层标高 (m)
    "floor_levels": {
        "B1": -3.90,
        "F1": 0.00,
        "F2": 4.20,
        "F3": 7.80,
        "F4": 11.40,
        "EQ": 15.00,
    },
}

# 各 Phase 跳过的检查（键名为 check 模块函数名中提取的标识）
PHASE_SKIP = {
    "1A": ["window", "door", "ceiling", "uv", "collision", "finish", "material"],
    "1B": ["uv", "finish"],
    "1C": ["uv"],
    "1D": ["uv"],
    "pre_merge": ["uv", "material"],   # 合并前检查
    "post_merge": ["overlap_detect", "gap_detect"],  # 合并后跳过重叠和缝隙
}

# 命名正则模式
NAMING_PATTERNS = {
    "object": re.compile(
        r'^[A-Z][a-z]*_[A-Z]+_[A-Z0-9]+_[A-Za-z0-9]+(_[0-9]{2})?$'
    ),
    "material": re.compile(
        r'^M_[A-Z][a-z]*_[A-Za-z0-9]+$'
    ),
}

# 排除检查的对象名模式（Blender 内部对象、辅助对象等）
EXCLUDE_PATTERNS = [
    re.compile(r'^Camera', re.I),
    re.compile(r'^Light', re.I),
    re.compile(r'^Empty', re.I),
    re.compile(r'^Armature', re.I),
    re.compile(r'^CameraTarget', re.I),
    re.compile(r'^TourCamera', re.I),
]

# ============================================================
# 工具函数
# ============================================================

class Level:
    """严重级别"""
    INFO = 0
    WARNING = 1
    ERROR = 2

    _names = {0: "PASS", 1: "WARN", 2: "FAIL"}

    @classmethod
    def name(cls, level):
        return cls._names.get(level, "????")

class Colors:
    """终端 ANSI 颜色"""
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def color_line(text, color):
    return f"{color}{text}{Colors.RESET}"

class Finding:
    """单条检查发现"""
    def __init__(self, module, level, message, detail=None):
        self.module = module
        self.level = level
        self.message = message
        self.detail = detail or ""

    def to_dict(self):
        return {
            "module": self.module,
            "level": Level.name(self.level),
            "message": self.message,
            "detail": self.detail,
        }

class CheckReport:
    """检查报告收集器"""
    def __init__(self):
        self.findings = []
        self.stats = {"total": 0, "pass": 0, "warn": 0, "fail": 0}

    def add(self, module, level, message, detail=None):
        finding = Finding(module, level, message, detail)
        self.findings.append(finding)
        self.stats["total"] += 1
        if level == Level.WARNING:
            self.stats["warn"] += 1
        elif level == Level.ERROR:
            self.stats["fail"] += 1
        else:
            self.stats["pass"] += 1

    def print_terminal(self):
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}  3D Model Check Report{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

        current_module = None
        for f in self.findings:
            if f.module != current_module:
                current_module = f.module
                print(f"\n{Colors.CYAN}[{f.module}]{Colors.RESET}")

            color = Colors.GREEN
            if f.level == Level.WARNING:
                color = Colors.YELLOW
            elif f.level == Level.ERROR:
                color = Colors.RED

            tag = Level.name(f.level)
            print(f"  {color_line(f'[{tag}]', color)} {f.message}")
            if f.detail:
                print(f"       {f.detail}")

        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        s = self.stats
        p = color_line(f"PASS: {s['pass']}", Colors.GREEN)
        w = color_line(f"WARN: {s['warn']}", Colors.YELLOW)
        f_ = color_line(f"FAIL: {s['fail']}", Colors.RED)
        print(f"  Total: {s['total']}  {p}  {w}  {f_}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

    def write_json(self, filepath):
        data = {
            "report_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "file": self.source_file,
            "stats": self.stats,
            "findings": [f.to_dict() for f in self.findings],
        }
        with open(filepath, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, indent=2, ensure_ascii=False)
        print(f"  JSON report: {filepath}")

    def write_errors(self, filepath):
        errors = [f for f in self.findings if f.level == Level.ERROR]
        if not errors:
            return
        with open(filepath, 'w', encoding='utf-8') as fp:
            fp.write(f"ERROR REPORT — {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            fp.write(f"{'='*60}\n\n")
            for f in errors:
                fp.write(f"[{f.module}] {f.message}\n")
                if f.detail:
                    fp.write(f"  {f.detail}\n")
                fp.write("\n")
        print(f"  ERROR details: {filepath} ({len(errors)} issues)")

    def write_warnings(self, filepath):
        warns = [f for f in self.findings if f.level == Level.WARNING]
        if not warns:
            return
        with open(filepath, 'w', encoding='utf-8') as fp:
            fp.write(f"WARNING REPORT — {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            fp.write(f"{'='*60}\n\n")
            for f in warns:
                fp.write(f"[{f.module}] {f.message}\n")
                if f.detail:
                    fp.write(f"  {f.detail}\n")
                fp.write("\n")
        print(f"  WARNING details: {filepath} ({len(warns)} issues)")


# ============================================================
# 辅助函数
# ============================================================

def get_mesh_objects():
    """获取所有需要检查的 mesh 对象（排除内部对象）"""
    meshes = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        excluded = False
        for pat in EXCLUDE_PATTERNS:
            if pat.search(obj.name):
                excluded = True
                break
        if not excluded:
            meshes.append(obj)
    return meshes


def object_aabb(obj):
    """计算对象世界空间的 AABB，返回 (min_vec, max_vec)"""
    if not obj.data.vertices:
        return Vector((0,0,0)), Vector((0,0,0))
    mat = obj.matrix_world
    verts = [mat @ v.co for v in obj.data.vertices]
    min_v = Vector(verts[0])
    max_v = Vector(verts[0])
    for v in verts[1:]:
        min_v.x = min(min_v.x, v.x)
        min_v.y = min(min_v.y, v.y)
        min_v.z = min(min_v.z, v.z)
        max_v.x = max(max_v.x, v.x)
        max_v.y = max(max_v.y, v.y)
        max_v.z = max(max_v.z, v.z)
    return min_v, max_v


def aabb_volume(min_v, max_v):
    """AABB 体积"""
    d = max_v - min_v
    return abs(d.x * d.y * d.z)


def aabb_overlap(min_a, max_a, min_b, max_b):
    """两个 AABB 是否重叠"""
    return (min_a.x < max_b.x and max_a.x > min_b.x and
            min_a.y < max_b.y and max_a.y > min_b.y and
            min_a.z < max_b.z and max_a.z > min_b.z)


def bvh_from_object(obj):
    """为对象创建 BVHTree"""
    if not obj.data.vertices:
        return None
    mat = obj.matrix_world
    verts = [mat @ v.co for v in obj.data.vertices]
    faces = []
    for poly in obj.data.polygons:
        faces.append([poly.vertices[i] for i in range(len(poly.vertices))])
    if not faces:
        return None
    return BVHTree.FromPolygons(verts, faces)


def build_bvh_index(meshes):
    """为所有 mesh 建立 BVHTree 索引"""
    index = {}
    for obj in meshes:
        tree = bvh_from_object(obj)
        if tree is not None:
            index[obj.name] = (obj, tree)
    return index


# ============================================================
# 检查模块 1: 网格完整性
# ============================================================

def check_mesh_integrity(report, meshes, baseline=False):
    """检查 non-manifold 边、零面积面、翻转法线、孤立顶点、退化三角形"""
    module = "1-MeshIntegrity"
    level = Level.INFO if baseline else Level.ERROR

    for obj in meshes:
        mesh = obj.data
        n_verts = len(mesh.vertices)
        n_edges = len(mesh.edges)
        n_faces = len(mesh.polygons)

        if n_faces == 0:
            report.add(module, level,
                       f"Empty mesh: {obj.name}",
                       "Object has no faces")
            continue

        # 零面积面
        zero_area = []
        for poly in mesh.polygons:
            if poly.area < 1e-8:
                zero_area.append(str(poly.index))
        if zero_area:
            report.add(module, level,
                       f"Zero-area faces: {obj.name}",
                       f"{len(zero_area)} faces: indices {', '.join(zero_area[:5])}{'...' if len(zero_area) > 5 else ''}")

        # 退化三角形 (长宽比 > 1000)
        degenerate = []
        for poly in mesh.polygons:
            if len(poly.vertices) == 3:
                v = [mesh.vertices[poly.vertices[i]].co for i in range(3)]
                e = [(v[1]-v[0]).length, (v[2]-v[1]).length, (v[0]-v[2]).length]
                e.sort()
                if e[0] < 1e-6:
                    degenerate.append(str(poly.index))
        if degenerate:
            report.add(module, level,
                       f"Degenerate triangles: {obj.name}",
                       f"{len(degenerate)} faces")

        # 孤立顶点
        connected = set()
        for edge in mesh.edges:
            connected.add(edge.vertices[0])
            connected.add(edge.vertices[1])
        isolated = [i for i in range(n_verts) if i not in connected]
        if isolated:
            report.add(module, level,
                       f"Isolated vertices: {obj.name}",
                       f"{len(isolated)} unconnected vertices")

    if not baseline:
        report.add(module, Level.INFO,
                   f"Mesh integrity check complete: {len(meshes)} objects scanned")


# ============================================================
# 检查模块 2: 几何精度
# ============================================================

def check_geometry_precision(report, meshes, baseline=False):
    """检查墙厚、楼板标高、柱网对齐"""
    module = "2-GeometryPrecision"
    level = Level.INFO if baseline else Level.WARNING

    floor_levels = CONFIG["floor_levels"]
    grid = CONFIG["column_grid"]
    grid_tol = CONFIG["grid_tolerance"]
    slab_z_tol = CONFIG["floor_z_tolerance"]

    for obj in meshes:
        name = obj.name
        min_v, max_v = object_aabb(obj)
        size = max_v - min_v

        # 墙厚检查
        if name.startswith("Wall_"):
            # 墙的AABB三个维度中最薄的是厚度
            dims = sorted([abs(size.x), abs(size.y), abs(size.z)])
            thickness = dims[0]  # 最薄维度
            wc = CONFIG["wall_thickness"]
            if thickness < wc["min"] or thickness > wc["max"]:
                report.add(module, level,
                           f"Wall thickness out of range: {obj.name}",
                           f"Thickness={thickness:.3f}m (range: {wc['min']}-{wc['max']}m)")

        # 楼板标高检查
        if name.startswith("Slab_"):
            z_center = (min_v.z + max_v.z) / 2
            # 检查 Z 值是否接近标准楼层标高
            closest = min(floor_levels.values(), key=lambda fl: abs(z_center - fl))
            if abs(z_center - closest) > slab_z_tol:
                report.add(module, level,
                           f"Slab Z-level off: {obj.name}",
                           f"Slab Z={z_center:.3f}m, nearest standard level={closest:.3f}m, diff={abs(z_center-closest):.3f}m")

        # 柱网对齐检查
        if name.startswith("Col_"):
            cx = (min_v.x + max_v.x) / 2
            cy = (min_v.y + max_v.y) / 2
            # 最近的 3.6m 网格点
            nearest_x = round(cx / grid) * grid
            nearest_y = round(cy / grid) * grid
            dx = abs(cx - nearest_x)
            dy = abs(cy - nearest_y)
            if dx > grid_tol or dy > grid_tol:
                report.add(module, level,
                           f"Column off-grid: {obj.name}",
                           f"Center=({cx:.2f},{cy:.2f}), nearest grid=({nearest_x:.1f},{nearest_y:.1f}), offset=({dx:.3f},{dy:.3f})m")


# ============================================================
# 检查模块 3: 重叠检测
# ============================================================

def check_overlap(report, meshes, baseline=False):
    """BVH + AABB + 三角面精确重叠检测。仅检测同类型+同楼层对象，排除墙-楼板等自然交叉。"""
    module = "3-OverlapDetect"
    level = Level.INFO if baseline else Level.ERROR
    min_vol = CONFIG["overlap_min_volume"]

    # 分组: 同建筑+同楼层的对象才互相检查
    groups = defaultdict(list)
    for obj in meshes:
        name = obj.name
        # 排除碰撞体 (自然与视觉体重叠)
        if name.startswith("Col_"):
            continue
        # 提取 {bldg}_{floor}
        parts = name.split('_')
        if len(parts) >= 3 and parts[0] == 'Merged':
            key = f"Merged_{parts[1]}"  # 合并mesh独立分组, 不与原始对象混合
        elif len(parts) >= 3:
            key = f"{parts[1]}_{parts[2]}"
        else:
            key = "ungrouped"
        groups[key].append(obj)

    # 允许自然交叉的类型对 (不报错)
    NATURAL_CROSS_PAIRS = {
        ('Wall', 'Slab'), ('Slab', 'Wall'),
        ('Wall', 'Col'), ('Col', 'Wall'),
        ('Slab', 'Col'), ('Col', 'Slab'),
        ('Beam', 'Slab'), ('Slab', 'Beam'),
        ('Beam', 'Wall'), ('Wall', 'Beam'),
        ('Beam', 'Col'), ('Col', 'Beam'),
        ('Slab', 'Slab'),
        # 设备基座
        ('AHU', 'Slab'), ('Machine', 'Slab'),
        ('Machine', 'Slab_EQ'),
    }
    # 同类型前缀的对象自然可交叉 (如 Elev_E, Elev_N 都是电梯井的墙)
    SAME_TYPE_OK = {'Elev', 'Elev2', 'Atrium', 'Balc', 'Rail', 'Canopy',
                    'Wall_Stair', 'Wall_Stair',  # 楼梯间墙
                    'Stair', 'Parapet', 'Plat', 'AHU', 'Machine', 'Base',
                    'Step', 'Escalator', 'DR_', 'DF_', 'Glass', 'Nurse',
                    'FireH', 'Plumb', 'Elec', 'ElecW', 'Ceil', 'Win'}
    # 允许不同类型但同属一个组件的交叉
    NATURAL_CROSS_PAIRS.add(('Atrium', 'Balc'))
    NATURAL_CROSS_PAIRS.add(('Balc', 'Atrium'))
    NATURAL_CROSS_PAIRS.add(('Atrium', 'Rail'))
    NATURAL_CROSS_PAIRS.add(('Rail', 'Atrium'))
    NATURAL_CROSS_PAIRS.add(('Balc', 'Rail'))
    NATURAL_CROSS_PAIRS.add(('Rail', 'Balc'))
    NATURAL_CROSS_PAIRS.add(('Atrium', 'Escalator'))
    NATURAL_CROSS_PAIRS.add(('Escalator', 'Atrium'))

    n_checked = 0
    n_overlaps = 0

    for key, group in groups.items():
        if len(group) < 2:
            continue
        # 合并后的 Mesh 组跳过重叠检查
        if key.startswith('Merged'):
            continue
        bvh_index = build_bvh_index(group)
        names = list(bvh_index.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                obj_a, tree_a = bvh_index[names[i]]
                obj_b, tree_b = bvh_index[names[j]]

                # 获取类型前缀 (两段式: Wall_Stair → "Wall_Stair")
                def type_prefix(name):
                    parts = name.split('_')
                    if len(parts) >= 2 and parts[1] in ('Stair', 'Tube', 'Pit', 'Core'):
                        return f"{parts[0]}_{parts[1]}"
                    return parts[0] if parts else name
                type_a = type_prefix(names[i])
                type_b = type_prefix(names[j])
                # 自然交叉豁免
                if (type_a, type_b) in NATURAL_CROSS_PAIRS:
                    continue
                # 同类型结构对象豁免 (如电梯井四面墙、中庭墙)
                if type_a == type_b and type_a in SAME_TYPE_OK:
                    continue

                # AABB 粗筛
                min_a, max_a = object_aabb(obj_a)
                min_b, max_b = object_aabb(obj_b)
                if not aabb_overlap(min_a, max_a, min_b, max_b):
                    continue

                # BVH 重叠检测
                overlap_pairs = tree_a.overlap(tree_b)
                if overlap_pairs:
                    n_overlaps += 1
                    ov_min = Vector((
                        max(min_a.x, min_b.x),
                        max(min_a.y, min_b.y),
                        max(min_a.z, min_b.z)))
                    ov_max = Vector((
                        min(max_a.x, max_b.x),
                        min(max_a.y, max_b.y),
                        min(max_a.z, max_b.z)))
                    ov_vol = aabb_volume(ov_min, ov_max)
                    if ov_vol > min_vol:
                        report.add(module, level,
                                   f"Mesh overlap: {obj_a.name} <-> {obj_b.name}",
                                   f"Overlap volume ~{ov_vol:.6f}m³, {len(overlap_pairs)} overlapping triangle pairs")
                n_checked += 1

    report.add(module, Level.INFO,
               f"Overlap check complete: {n_checked} pairs checked, {n_overlaps} overlaps in {len(groups)} groups")


# ============================================================
# 检查模块 4: 缝隙检测
# ============================================================

def check_gaps(report, meshes, baseline=False):
    """检查相邻墙体/楼板间的缝隙"""
    module = "4-GapDetect"
    level = Level.INFO if baseline else Level.ERROR
    gap_max = CONFIG["gap_max"]
    search_radius = CONFIG["gap_search_radius"]

    # 按类型分组
    walls = [o for o in meshes if o.name.startswith("Wall_")]
    slabs = [o for o in meshes if o.name.startswith("Slab_")]

    # 同建筑同层的墙体间缝隙
    wall_groups = defaultdict(list)
    for w in walls:
        # 提取建筑+楼层标识: Wall_OP_F1_xxx → OP_F1
        parts = w.name.split('_')
        if len(parts) >= 3:
            key = f"{parts[1]}_{parts[2]}"
            wall_groups[key].append(w)

    for key, group in wall_groups.items():
        bvh_index = build_bvh_index(group)
        names = list(bvh_index.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                obj_a, tree_a = bvh_index[names[i]]
                obj_b, tree_b = bvh_index[names[j]]

                min_a, max_a = object_aabb(obj_a)
                min_b, max_b = object_aabb(obj_b)

                # 扩展 AABB 以检测缝隙
                g_min_a = Vector((min_a.x - gap_max, min_a.y - gap_max, min_a.z - gap_max))
                g_max_a = Vector((max_a.x + gap_max, max_a.y + gap_max, max_a.z + gap_max))

                if not aabb_overlap(g_min_a, g_max_a, min_b, max_b):
                    continue

                # 两个 mesh 不重叠但 AABB 几乎接触 → 可能缝隙
                if not aabb_overlap(min_a, max_a, min_b, max_b):
                    # 检查最近距离
                    result = tree_a.find_nearest(
                        [(min_b.x + max_b.x) / 2, (min_b.y + max_b.y) / 2, (min_b.z + max_b.z) / 2]
                    )
                    if result and len(result) >= 2:
                        dist = result[0]
                        if 0 < dist <= search_radius:
                            report.add(module, level,
                                       f"Gap detected: {obj_a.name} <-> {obj_b.name}",
                                       f"Distance={dist*1000:.1f}mm (threshold={gap_max*1000:.0f}mm)")

    # 墙底与楼板之间的缝隙
    for wall in walls:
        w_min, w_max = object_aabb(wall)
        wall_bottom = w_min.z
        # 找最近楼板
        for slab in slabs:
            s_min, s_max = object_aabb(slab)
            slab_top = s_max.z
            gap = abs(wall_bottom - slab_top)
            if gap_max < gap < search_radius:
                report.add(module, level,
                           f"Wall-Floor gap: {wall.name} from {slab.name}",
                           f"Gap={gap*1000:.1f}mm")


# ============================================================
# 检查模块 5: 命名合规
# ============================================================

def check_naming(report, meshes, baseline=False):
    """检查对象名、材质名是否符合命名规范"""
    module = "5-NamingConvention"
    level = Level.INFO if baseline else Level.WARNING

    obj_pat = NAMING_PATTERNS["object"]
    mat_pat = NAMING_PATTERNS["material"]

    # 对象名
    names_seen = set()
    for obj in meshes:
        name = obj.name
        if name in names_seen:
            report.add(module, level,
                       f"Duplicate object name: {name}")
        names_seen.add(name)
        if not obj_pat.match(name):
            # 对不符合模式的名字给出友好建议
            report.add(module, Level.INFO if baseline else Level.WARNING,
                       f"Object name not matching convention: {name}",
                       "Expected: {Type}_{Building}_{Floor}_{Location}_{Index}")

    # 材质名
    all_mats = set()
    for obj in meshes:
        for slot in obj.material_slots:
            if slot.material:
                all_mats.add(slot.material.name)

    for mat_name in all_mats:
        if not mat_pat.match(mat_name):
            report.add(module, Level.INFO if baseline else Level.WARNING,
                       f"Material name not matching convention: {mat_name}",
                       "Expected: M_{Category}_{Variant}")


# ============================================================
# 检查模块 6: UV 检查
# ============================================================

def check_uv(report, meshes, baseline=False):
    """检查 UV Map 存在、岛重叠、密度一致性"""
    module = "6-UVMapping"
    level = Level.INFO if baseline else Level.WARNING

    no_uv = []
    for obj in meshes:
        if not obj.data.uv_layers:
            no_uv.append(obj.name)

    if no_uv:
        for name in no_uv[:10]:
            report.add(module, level,
                       f"No UV map: {name}")
        if len(no_uv) > 10:
            report.add(module, level,
                       f"No UV map: ... and {len(no_uv)-10} more objects")

    # 有 UV 的对象统计密度
    uv_densities = []
    for obj in meshes:
        if not obj.data.uv_layers:
            continue
        uv = obj.data.uv_layers[0]
        mesh = obj.data
        total_area_3d = sum(p.area for p in mesh.polygons)
        if total_area_3d < 1e-6:
            continue
        # 估算 UV 面积
        uv_area = 0
        for poly in mesh.polygons:
            uv_coords = [uv.data[li].uv for li in poly.loop_indices]
            if len(uv_coords) >= 3:
                uv_area += _triangle_area_2d(uv_coords[0], uv_coords[1], uv_coords[2])
        density = uv_area / total_area_3d if total_area_3d > 0 else 0
        uv_densities.append((obj.name, density))

    if uv_densities:
        densities = [d for _, d in uv_densities]
        avg = sum(densities) / len(densities) if densities else 1.0
        max_dev = CONFIG["uv_density_deviation_max"]
        for name, d in uv_densities:
            if avg > 0 and (d / avg > max_dev or avg / d > max_dev):
                report.add(module, level,
                           f"UV density deviation: {name}",
                           f"Density={d:.1f} px⁻¹, average={avg:.1f} px⁻¹, deviation={d/avg:.1f}x")


def _triangle_area_2d(a, b, c):
    """二维三角形面积 (Shoelace)"""
    return 0.5 * abs(a[0]*(b[1]-c[1]) + b[0]*(c[1]-a[1]) + c[0]*(a[1]-b[1]))


# ============================================================
# 检查模块 7: 碰撞体
# ============================================================

def check_collision(report, meshes, baseline=False):
    """检查每个可见 mesh 是否有对应碰撞体，碰撞体尺寸是否匹配"""
    module = "7-CollisionBody"
    level = Level.INFO if baseline else Level.ERROR
    max_dev = CONFIG["collision_deviation_max"]

    visible = []
    collision = []

    for obj in meshes:
        name = obj.name
        if name.startswith("Col_"):
            collision.append(obj)
        elif not name.startswith("Slab_Col"):  # 碰撞体楼板不要误判
            visible.append(obj)

    # 检查可见 mesh 是否有对应碰撞体
    for vis in visible:
        # 合并后的 Mesh 跳过碰撞体检查 (碰撞体在合并前已验证)
        if vis.name.startswith("Merged_"):
            continue
        expected_col_name = vis.name
        if expected_col_name.startswith("Wall_"):
            expected_col_name = "Col_" + expected_col_name[5:]
        elif expected_col_name.startswith("Slab_"):
            expected_col_name = "Col_" + expected_col_name[5:]
        else:
            expected_col_name = "Col_" + expected_col_name

        found = None
        for col in collision:
            # 模糊匹配：碰撞体名包含可见对象名的一部分
            col_key = col.name[4:] if col.name.startswith("Col_") else col.name
            vis_key = vis.name
            if vis_key.startswith("Wall_"):
                vis_key = vis_key[5:]
            elif vis_key.startswith("Slab_"):
                vis_key = vis_key[5:]
            if vis_key in col_key or col_key in vis_key:
                found = col
                break

        if not found:
            report.add(module, level,
                       f"No collision body: {vis.name}",
                       f"Expected name like: {expected_col_name}")

        # 如果有对应碰撞体，检查尺寸
        if found:
            vis_min, vis_max = object_aabb(vis)
            col_min, col_max = object_aabb(found)
            vis_size = vis_max - vis_min
            col_size = col_max - col_min
            for axis, label in [(0,'X'), (1,'Y'), (2,'Z')]:
                if col_size[axis] < vis_size[axis] - max_dev:
                    report.add(module, level,
                               f"Collision too small: {found.name} vs {vis.name}",
                               f"Axis {label}: collision={col_size[axis]:.3f}m < visual={vis_size[axis]:.3f}m (diff > {max_dev:.2f}m)")
                    break
                elif col_size[axis] > vis_size[axis] + max_dev * 2:
                    report.add(module, Level.INFO if baseline else Level.WARNING,
                               f"Collision larger than visual: {found.name} vs {vis.name}",
                               f"Axis {label}: collision={col_size[axis]:.3f}m > visual={vis_size[axis]:.3f}m")


# ============================================================
# 检查模块 8: 面数统计
# ============================================================

def check_face_count(report, meshes, baseline=False):
    """统计面数，超限警告"""
    module = "8-FaceCount"
    level = Level.INFO if baseline else Level.WARNING
    bldg_warn = CONFIG["face_count_building_warn"]
    room_warn = CONFIG["face_count_room_warn"]

    # 按建筑分组统计
    bldg_faces = defaultdict(int)
    room_faces = defaultdict(int)
    total = 0

    for obj in meshes:
        nf = len(obj.data.polygons)
        total += nf
        # 提取建筑代码
        parts = obj.name.split('_')
        if len(parts) >= 2:
            bldg = parts[1] if parts[0] != 'Col' else (parts[1] if len(parts) > 1 else "UNKNOWN")
            bldg_faces[bldg] += nf
        # 提取房间标识
        if len(parts) >= 4 and parts[3].startswith('R'):
            room_faces[parts[3]] += nf

    report.add(module, Level.INFO,
               f"Total faces: {total:,} across {len(meshes)} objects")

    for bldg, nf in sorted(bldg_faces.items()):
        if nf > bldg_warn:
            report.add(module, level,
                       f"Building {bldg}: {nf:,} faces (warn threshold: {bldg_warn:,})")

    for room, nf in sorted(room_faces.items()):
        if nf > room_warn:
            report.add(module, level,
                       f"Room {room}: {nf:,} faces (warn threshold: {room_warn:,})")

    report.add(module, Level.INFO,
               f"Per building: {dict(sorted(bldg_faces.items()))}")


# ============================================================
# 检查模块 9: 材质检查
# ============================================================

def check_materials(report, meshes, baseline=False):
    """检查空材质槽、引用不存在的材质"""
    module = "9-MaterialCheck"
    level = Level.INFO if baseline else Level.ERROR

    existing_mats = set(bpy.data.materials.keys())

    for obj in meshes:
        if not obj.material_slots:
            report.add(module, level,
                       f"No material slots: {obj.name}")
            continue

        for i, slot in enumerate(obj.material_slots):
            if not slot.material:
                report.add(module, level,
                           f"Empty material slot [{i}]: {obj.name}")
            elif slot.material.name not in existing_mats:
                report.add(module, level,
                           f"Referenced material not found: {obj.name}[{i}] -> {slot.material.name}")


# ============================================================
# 主函数
# ============================================================

def parse_args():
    """解析命令行参数"""
    args = {
        "filepath": None,
        "baseline": False,
        "phase": None,
    }

    argv = sys.argv
    # blender --background --python check_model.py -- file.blend --baseline
    try:
        idx = argv.index("--")
        rest = argv[idx + 1:]
    except ValueError:
        # 尝试在 sys.argv 中找 .blend/.glb
        rest = []
        for a in argv:
            if a.endswith('.blend') or a.endswith('.glb'):
                rest = [a]
                break

    i = 0
    while i < len(rest):
        a = rest[i]
        if a == '--baseline':
            args["baseline"] = True
        elif a == '--phase':
            i += 1
            if i < len(rest):
                args["phase"] = rest[i]
        elif a.endswith('.blend') or a.endswith('.glb'):
            args["filepath"] = a
        elif not a.startswith('--'):
            # 可能是文件路径
            if os.path.exists(a) and (a.endswith('.blend') or a.endswith('.glb')):
                args["filepath"] = a
        i += 1

    return args


def should_skip(module_name, phase):
    """根据 phase 决定是否跳过某个模块"""
    if not phase:
        return False
    skip_list = PHASE_SKIP.get(phase, [])
    for keyword in skip_list:
        if keyword.lower() in module_name.lower():
            return True
    return False


def main():
    args = parse_args()

    if not args["filepath"]:
        print(f"{Colors.RED}Usage: blender --background --python check_model.py -- <file.blend|file.glb> [--baseline] [--phase X]{Colors.RESET}")
        sys.exit(1)

    filepath = args["filepath"]
    if not os.path.exists(filepath):
        print(f"{Colors.RED}File not found: {filepath}{Colors.RESET}")
        sys.exit(1)

    is_glb = filepath.endswith('.glb')
    baseline = args["baseline"]
    phase = args["phase"]

    print(f"\n{Colors.BOLD}Loading: {filepath}{Colors.RESET}")
    if baseline:
        print(f"{Colors.YELLOW}BASELINE mode: all issues → INFO{Colors.RESET}")
    if phase:
        print(f"{Colors.CYAN}PHASE: {phase} — skips: {PHASE_SKIP.get(phase, [])}{Colors.RESET}")

    # 加载文件
    if is_glb:
        bpy.ops.import_scene.gltf(filepath=filepath)
    # .blend 文件由 Blender 启动时载入

    # 准备检查
    meshes = get_mesh_objects()
    print(f"  Mesh objects found: {len(meshes)}")

    report = CheckReport()
    report.source_file = filepath

    # 运行所有检查模块
    checks = [
        ("1-MeshIntegrity",     check_mesh_integrity),
        ("2-GeometryPrecision",  check_geometry_precision),
        ("3-OverlapDetect",     check_overlap),
        ("4-GapDetect",         check_gaps),
        ("5-NamingConvention",  check_naming),
        ("6-UVMapping",         check_uv),
        ("7-CollisionBody",     check_collision),
        ("8-FaceCount",         check_face_count),
        ("9-MaterialCheck",     check_materials),
    ]

    for mod_name, check_fn in checks:
        if should_skip(mod_name, phase):
            print(f"  {Colors.CYAN}SKIP {mod_name} (phase: {phase}){Colors.RESET}")
            continue

        if is_glb and mod_name in ("5-NamingConvention", "6-UVMapping", "8-FaceCount"):
            print(f"  {Colors.CYAN}SKIP {mod_name} (GLB simplified mode){Colors.RESET}")
            continue

        print(f"  Running {mod_name}...")
        check_fn(report, meshes, baseline)

    # 输出报告
    report.print_terminal()

    # 写文件报告
    base = os.path.splitext(filepath)[0]
    report.write_json(f"{base}_check_report.json")
    report.write_errors(f"{base}_check_errors.txt")
    report.write_warnings(f"{base}_check_warnings.txt")

    # 返回码
    if report.stats["fail"] > 0 and not baseline:
        print(f"\n{Colors.RED}Check FAILED: {report.stats['fail']} error(s){Colors.RESET}")
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}Check PASSED{Colors.RESET}")
        sys.exit(0)


if __name__ == '__main__':
    main()
