"""
精神专科医院 — 500床院区 3D 模型 (v3.0)
基于《精神专科医院建筑设计方案参考图集》（卫生部，2009.12）
500 床规模综合院区: 多栋功能楼 + 操场 + 绿化庭院

坐标系:
  X → 东, Y → 北, Z → 上
  原点: 院区西南角

院区组成:
  1. 门诊医技综合楼 (4F, 60×25m) — 主入口, 挑空中庭
  2. 住院楼 A (6F, 40×18m) — 护理单元 ×6
  3. 住院楼 B (6F, 40×18m) — 护理单元 ×6
  4. 康复活动楼 (3F, 30×15m) — 工娱疗, 活动室
  5. 行政后勤楼 (2F, 25×15m)
  6. 食堂 (2F, 20×15m)
  7. 操场 (60×40m) — 跑道+球场
  8. 花园庭院 + 连廊系统

运行: blender --background --python build_hospital.py
"""

import bpy
import math
import os

# ============================================================
# 场地参数
# ============================================================
SITE_W = 220.0  # 院区东西宽
SITE_D = 180.0  # 院区南北深

# ============================================================
# 工具函数
# ============================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def box(name, x, y, z, w, d, h):
    """长方体. (x,y,z)=底面西南角"""
    bpy.ops.mesh.primitive_cube_add(size=2)
    obj = bpy.context.active_object
    obj.name = name
    obj.location = (x + w/2, y + d/2, z + h/2)
    obj.scale = (w/2, d/2, h/2)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def wall_x(name, x, y, z, length, height, thick=0.30):
    return box(name, x, y, z, length, thick, height)

def wall_y(name, x, y, z, length, height, thick=0.30):
    return box(name, x, y, z, thick, length, height)

def slab(name, x, y, z, w, d, t=0.20):
    return box(name, x, y, z, w, d, t)

def column(name, x, y, z, h, size=0.5):
    return box(name, x - size/2, y - size/2, z, size, size, h)

def cylinder(name, x, y, z, r, h):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=(x, y, z + h/2))
    obj = bpy.context.active_object
    obj.name = name
    return obj

def sphere(name, x, y, z, r):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, z))
    obj = bpy.context.active_object
    obj.name = name
    return obj

# ============================================================
# 1. 场地基础
# ============================================================

def build_site():
    """地面, 道路, 入口广场"""
    # 主地面 (草地)
    box("Ground_Grass", -5, -5, -0.05, SITE_W + 10, SITE_D + 10, 0.05)

    # 内部道路 (环形主干道)
    road_w = 6.0
    # 南侧主路
    box("Road_S", 0, 15, 0, SITE_W, road_w, 0.02)
    # 北侧路
    box("Road_N", 0, SITE_D - 25, 0, SITE_W, road_w, 0.02)
    # 西侧路
    box("Road_W", 15, 0, 0, road_w, SITE_D, 0.02)
    # 东侧路
    box("Road_E", SITE_W - 25, 0, 0, road_w, SITE_D, 0.02)
    # 中央南北路
    box("Road_Center", SITE_W/2 - road_w/2, 15, 0, road_w, SITE_D - 40, 0.02)

    # 入口广场 (南侧)
    plaza_w, plaza_d = 50.0, 25.0
    box("EntryPlaza", SITE_W/2 - plaza_w/2, 5, 0.01, plaza_w, plaza_d, 0.02)

    # 人行步道
    path_w = 2.0
    # 连接各楼之间
    box("Path_OP_to_IP", SITE_W/2 - path_w/2, 45, 0.01, path_w, 80, 0.02)


# ============================================================
# 2. 建筑通用构建器
# ============================================================

def build_floor_slab(bldg_name, level_idx, x, y, z, w, d):
    """单层楼板"""
    slab(f"Slab_{bldg_name}_L{level_idx}", x, y, z, w, d)

def build_exterior(bldg_name, x, y, z_base, w, d, n_floors, floor_heights,
                   entrance_side='S', entrance_w=8.0, entrance_h=3.0,
                   has_atrium=None):
    """建筑外墙, 含入口留空

    entrance_side: 'S'(南), 'N'(北), 'W'(西), 'E'(东)
    has_atrium: (atrium_x_rel, atrium_w_rel, atrium_d_rel) 或 None
    """
    total_h = sum(floor_heights[:n_floors])
    EXT = 0.30

    # 入口侧外墙留空
    if entrance_side == 'S':
        # 南墙: 入口左侧 + 入口右侧
        left_w = (w - entrance_w) / 2
        if left_w > 0.1:
            wall_x(f"Ext_{bldg_name}_S_L", x, y, z_base, left_w, total_h, EXT)
            wall_x(f"Ext_{bldg_name}_S_R", x + left_w + entrance_w, y, z_base, left_w, total_h, EXT)
        # 入口大门框
        wall_y(f"Ext_{bldg_name}_Entry_L", x + left_w, y, z_base, entrance_h, EXT, EXT)
        wall_y(f"Ext_{bldg_name}_Entry_R", x + left_w + entrance_w - EXT, y, z_base, entrance_h, EXT, EXT)
        # 门楣
        wall_x(f"Ext_{bldg_name}_Lintel", x + left_w, y, z_base + entrance_h,
               entrance_w, total_h - entrance_h, EXT)
        # 玻璃门
        box(f"Glass_{bldg_name}_Entry", x + left_w + 0.1, y, z_base,
            entrance_w - 0.2, 0.05, entrance_h)

        # 其他三面完整
        wall_x(f"Ext_{bldg_name}_N", x, y + d - EXT, z_base, w, total_h, EXT)
        wall_y(f"Ext_{bldg_name}_W", x, y, z_base, d, total_h, EXT)
        wall_y(f"Ext_{bldg_name}_E", x + w - EXT, y, z_base, d, total_h, EXT)
    else:
        # 四面完整 (简化)
        wall_x(f"Ext_{bldg_name}_S", x, y, z_base, w, total_h, EXT)
        wall_x(f"Ext_{bldg_name}_N", x, y + d - EXT, z_base, w, total_h, EXT)
        wall_y(f"Ext_{bldg_name}_W", x, y, z_base, d, total_h, EXT)
        wall_y(f"Ext_{bldg_name}_E", x + w - EXT, y, z_base, d, total_h, EXT)

    return total_h


def build_corridor_rooms(bldg_name, level_idx, x, y, z, w, d, floor_h,
                          corr_axis='X', corr_pos=0.5,
                          room_depth_a=6.8, room_depth_b=6.0,
                          room_width=3.6):
    """双廊式布局: 走廊 + 房间隔墙

    corr_axis: 'X'=东西向走廊, 'Y'=南北向走廊
    corr_pos: 走廊位置 (0-1, 从近端算)
    """
    INT = 0.20
    CORR_W = 2.4
    h = floor_h - 0.20

    if corr_axis == 'X':
        # 走廊沿 X 轴, 南北两侧房间
        corr_y = y + d * corr_pos - CORR_W / 2

        # 走廊墙
        wall_x(f"Corr_S_{bldg_name}_L{level_idx}", x, corr_y, z, w, h, INT)
        wall_x(f"Corr_N_{bldg_name}_L{level_idx}", x, corr_y + CORR_W, z, w, h, INT)

        # 南侧隔墙
        n_south = max(2, int(w / room_width))
        for i in range(n_south + 1):
            rx = x + i * (w / n_south)
            thick = 0.30 if (i == 0 or i == n_south) else INT
            sd = corr_y - y
            wall_y(f"Div_S_{bldg_name}_L{level_idx}_{i}", rx - thick/2, y, z, sd, h, thick)

        # 北侧隔墙
        n_north = max(2, int(w / room_width))
        north_start = corr_y + CORR_W
        nd = (y + d) - north_start
        for i in range(n_north + 1):
            rx = x + i * (w / n_north)
            thick = 0.30 if (i == 0 or i == n_north) else INT
            wall_y(f"Div_N_{bldg_name}_L{level_idx}_{i}", rx - thick/2, north_start, z, nd, h, thick)

        # 房间体量 (南侧)
        for i in range(n_south):
            rx = x + i * (w / n_south) + 0.01
            rw = (w / n_south) - 0.02
            sd = corr_y - y
            box(f"Room_S_{bldg_name}_L{level_idx}_{i}", rx, y, z, rw, sd, h)

        # 房间体量 (北侧)
        for i in range(n_north):
            rx = x + i * (w / n_north) + 0.01
            rw = (w / n_north) - 0.02
            nd = (y + d) - north_start
            box(f"Room_N_{bldg_name}_L{level_idx}_{i}", rx, north_start, z, rw, nd, h)

    else:  # corr_axis == 'Y', 东西两侧房间
        corr_x = x + w * corr_pos - CORR_W / 2

        wall_y(f"Corr_W_{bldg_name}_L{level_idx}", corr_x, y, z, d, h, INT)
        wall_y(f"Corr_E_{bldg_name}_L{level_idx}", corr_x + CORR_W, y, z, d, h, INT)

        # 西侧隔墙
        n_west = max(2, int(d / room_width))
        for i in range(n_west + 1):
            ry = y + i * (d / n_west)
            thick = 0.30 if (i == 0 or i == n_west) else INT
            wd = corr_x - x
            wall_x(f"Div_W_{bldg_name}_L{level_idx}_{i}", x, ry - thick/2, z, wd, h, thick)

        # 东侧隔墙
        n_east = max(2, int(d / room_width))
        east_start = corr_x + CORR_W
        ed = (x + w) - east_start
        for i in range(n_east + 1):
            ry = y + i * (d / n_east)
            thick = 0.30 if (i == 0 or i == n_east) else INT
            wall_x(f"Div_E_{bldg_name}_L{level_idx}_{i}", east_start, ry - thick/2, z, ed, h, thick)

        # 房间体量
        for i in range(n_west):
            ry = y + i * (d / n_west) + 0.01
            rd = (d / n_west) - 0.02
            wd = corr_x - x
            box(f"Room_W_{bldg_name}_L{level_idx}_{i}", x, ry, z, wd, rd, h)
        for i in range(n_east):
            ry = y + i * (d / n_east) + 0.01
            rd = (d / n_east) - 0.02
            ed = (x + w) - east_start
            box(f"Room_E_{bldg_name}_L{level_idx}_{i}", east_start, ry, z, ed, rd, h)


def build_atrium(bldg_name, x, y, z1, z2, w, d, f1_h, f2_h):
    """二层挑空中庭 (门诊大厅)

    中庭位于建筑南侧中央, F1-F2 挑空
    """
    atrium_w = w * 0.55
    atrium_d = d * 0.50
    ax = x + (w - atrium_w) / 2
    ay = y + 2.0  # 距南立面 2m
    total_h = f1_h + f2_h

    # 中庭东西墙 (通高)
    wall_y(f"Atrium_W_{bldg_name}", ax, ay, z1, atrium_d, total_h)
    wall_y(f"Atrium_E_{bldg_name}", ax + atrium_w - 0.30, ay, z1, atrium_d, total_h)

    # 中庭北墙 F1 (通道)
    north_y = ay + atrium_d - 0.30
    passage = 3.6
    side_w = (atrium_w - passage) / 2
    if side_w > 0.2:
        wall_x(f"Atrium_N_L_{bldg_name}", ax, north_y, z1, side_w, f1_h)
        wall_x(f"Atrium_N_R_{bldg_name}", ax + side_w + passage, north_y, z1, side_w, f1_h)

    # F2 回廊
    balcony = 2.0
    f2_z = z2
    slab(f"Balcony_S_{bldg_name}", ax, ay, f2_z, atrium_w, balcony)
    slab(f"Balcony_N_{bldg_name}", ax, ay + atrium_d - balcony, f2_z, atrium_w, balcony)
    slab(f"Balcony_W_{bldg_name}", ax, ay + balcony, f2_z, balcony, atrium_d - 2*balcony)
    slab(f"Balcony_E_{bldg_name}", ax + atrium_w - balcony, ay + balcony, f2_z, balcony, atrium_d - 2*balcony)

    # 栏杆
    rail_h = 1.1
    wall_x(f"Rail_S_{bldg_name}", ax + balcony, ay + balcony, f2_z, atrium_w - 2*balcony, rail_h, 0.15)
    wall_x(f"Rail_N_{bldg_name}", ax + balcony, ay + atrium_d - balcony - 0.15, f2_z, atrium_w - 2*balcony, rail_h, 0.15)
    wall_y(f"Rail_W_{bldg_name}", ax + balcony, ay + balcony, f2_z, atrium_d - 2*balcony, rail_h, 0.15)
    wall_y(f"Rail_E_{bldg_name}", ax + atrium_w - balcony - 0.15, ay + balcony, f2_z, atrium_d - 2*balcony, rail_h, 0.15)

    # 中庭地面
    slab(f"Atrium_Floor_{bldg_name}", ax, ay, z1, atrium_w, atrium_d, 0.10)

    # 镜子平台
    ps = 4.0
    box(f"Mirror_Platform_{bldg_name}", ax + (atrium_w-ps)/2, ay + (atrium_d-ps)/2, z1, ps, ps, 0.05)

    return ax, ay, atrium_w, atrium_d


def build_columns_grid(bldg_name, x, y, z, w, d, h, col_spacing=7.2):
    """结构柱网"""
    cols_x = [x + col_spacing * i for i in range(int(w / col_spacing) + 1)]
    cols_y = [y + col_spacing * i for i in range(int(d / col_spacing) + 1)]

    for cx in cols_x:
        if cx <= x + 0.5 or cx >= x + w - 0.5:
            continue
        for cy in cols_y:
            if cy <= y + 0.5 or cy >= y + d - 0.5:
                continue
            # 跳过中庭区域 (简化为建筑南侧中央 40% 区域)
            atrium_zone = (x + w*0.2 < cx < x + w*0.8 and cy < y + d*0.4)
            if atrium_zone and bldg_name == "OP":
                continue
            column(f"Col_{bldg_name}_{cx:.0f}_{cy:.0f}", cx, cy, z, h)


# ============================================================
# 3. 各建筑定义
# ============================================================

def build_outpatient():
    """门诊医技综合楼 (4F, 60×25m)
    院区南侧中央, 主入口
    F1: 门诊大厅(挑空) + 急诊 + 药房 + 挂号
    F2: 检验科 + 放射科 + B超/心电图/脑电图
    F3: 心理测查 + 心理治疗 + 脑功能治疗
    F4: 行政办公 + 会议室
    """
    bldg = "OP"
    w, d = 60.0, 25.0
    x = SITE_W/2 - w/2
    y = 30.0
    floor_heights = [4.2, 3.6, 3.6, 3.6]  # F1-F4

    print(f"  门诊医技综合楼: {w}×{d}m, 4F @ ({x:.0f},{y:.0f})")

    # 各层楼板
    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_floor_slab(bldg, i, x, y, cum_z, w, d)
        cum_z += fh

    # 外墙 (南侧入口留空)
    build_exterior(bldg, x, y, 0, w, d, 4, floor_heights,
                   entrance_side='S', entrance_w=10.0, entrance_h=3.5)

    # 中庭 (F1-F2)
    build_atrium(bldg, x, y, 0, floor_heights[0], w, d,
                 floor_heights[0], floor_heights[1])

    # 各层房间
    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_corridor_rooms(bldg, i, x, y, cum_z, w, d, fh,
                             corr_axis='X', corr_pos=0.55)
        cum_z += fh

    # 柱网
    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_columns_grid(bldg, x, y, cum_z, w, d, fh)
        cum_z += fh

    # 入口台阶
    entry_cx = x + w/2
    for i in range(5):
        sy = y - (i+1) * 0.35
        sz = -0.05 - (i+1) * 0.15
        box(f"Step_OP_{i}", entry_cx - 5, sy, sz, 10, 0.35, 0.15)

    # 雨棚
    canopy_z = floor_heights[0] - 2.5
    slab("Canopy_OP", entry_cx - 6, y - 3.5, canopy_z, 12, 3.5)

    return x, y, w, d, sum(floor_heights)


def build_inpatient(bldg_name, x, y):
    """住院楼 (6F, 40×18m)
    标准护理单元 ×6
    双廊式: 南侧病房(6.8m), 北侧辅助(6.0m), 中廊2.4m
    """
    w, d = 40.0, 18.0
    n_floors = 6
    floor_heights = [3.6] * n_floors

    print(f"  {bldg_name}: {w}×{d}m, 6F @ ({x:.0f},{y:.0f})")

    # 楼板
    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_floor_slab(bldg_name, i, x, y, cum_z, w, d)
        cum_z += fh

    # 外墙
    build_exterior(bldg_name, x, y, 0, w, d, n_floors, floor_heights,
                   entrance_side='S', entrance_w=6.0, entrance_h=2.8)

    # 各层护理单元
    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_corridor_rooms(bldg_name, i, x, y, cum_z, w, d, fh,
                             corr_axis='X', corr_pos=0.45,
                             room_depth_a=6.8, room_depth_b=6.0,
                             room_width=3.6)
        cum_z += fh

    # 柱网
    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_columns_grid(bldg_name, x, y, cum_z, w, d, fh)
        cum_z += fh

    return x, y, w, d, sum(floor_heights)


def build_rehabilitation(x, y):
    """康复活动楼 (3F, 30×15m)
    F1: 工疗室, 手工/陶艺
    F2: 娱疗室, 音乐/绘画/舞蹈治疗
    F3: 活动室, 病人餐厅
    """
    bldg = "REHAB"
    w, d = 30.0, 15.0
    n_floors = 3
    floor_heights = [4.0, 3.6, 3.6]

    print(f"  康复活动楼: {w}×{d}m, 3F @ ({x:.0f},{y:.0f})")

    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_floor_slab(bldg, i, x, y, cum_z, w, d)
        cum_z += fh

    build_exterior(bldg, x, y, 0, w, d, n_floors, floor_heights,
                   entrance_side='S', entrance_w=8.0, entrance_h=3.0)

    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_corridor_rooms(bldg, i, x, y, cum_z, w, d, fh,
                             corr_axis='Y', corr_pos=0.5,
                             room_depth_a=6.0, room_depth_b=5.0,
                             room_width=5.0)  # 更大的活动室
        cum_z += fh

    return x, y, w, d, sum(floor_heights)


def build_admin(x, y):
    """行政后勤楼 (2F, 25×15m)"""
    bldg = "ADMIN"
    w, d = 25.0, 15.0
    n_floors = 2
    floor_heights = [3.6, 3.6]

    print(f"  行政后勤楼: {w}×{d}m, 2F @ ({x:.0f},{y:.0f})")

    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_floor_slab(bldg, i, x, y, cum_z, w, d)
        cum_z += fh

    build_exterior(bldg, x, y, 0, w, d, n_floors, floor_heights,
                   entrance_side='S', entrance_w=5.0, entrance_h=2.8)

    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_corridor_rooms(bldg, i, x, y, cum_z, w, d, fh,
                             corr_axis='X', corr_pos=0.5)
        cum_z += fh

    return x, y, w, d, sum(floor_heights)


def build_cafeteria(x, y):
    """食堂 (2F, 20×15m)
    F1: 病人餐厅
    F2: 职工餐厅 + 厨房
    """
    bldg = "CAFE"
    w, d = 20.0, 15.0
    n_floors = 2
    floor_heights = [4.5, 4.0]  # 较高层高

    print(f"  食堂: {w}×{d}m, 2F @ ({x:.0f},{y:.0f})")

    cum_z = 0.0
    for i, fh in enumerate(floor_heights):
        build_floor_slab(bldg, i, x, y, cum_z, w, d)
        cum_z += fh

    build_exterior(bldg, x, y, 0, w, d, n_floors, floor_heights,
                   entrance_side='S', entrance_w=6.0, entrance_h=3.0)

    # 食堂内部开放空间 (大厅+厨房)
    # F1 大餐厅 (无太多隔墙, 开放空间)
    box(f"Hall_{bldg}_L0", x + 0.2, y + 0.2, 0, w*0.7 - 0.4, d - 0.4, floor_heights[0] - 0.2)
    # 厨房
    box(f"Kitchen_{bldg}_L0", x + w*0.7, y + 0.2, 0, w*0.3 - 0.4, d - 0.4, floor_heights[0] - 0.2)

    return x, y, w, d, sum(floor_heights)


def build_playground(x, y):
    """操场/活动场地 (60×40m)
    200m 跑道 + 篮球场 + 健身器材区
    """
    w, d = 60.0, 40.0

    print(f"  操场: {w}×{d}m @ ({x:.0f},{y:.0f})")

    # 跑道基底
    box("Field_Base", x, y, 0.005, w, d, 0.01)

    # 环形跑道 (简化: 矩形框)
    track_w = 1.5  # 跑道宽
    # 外圈
    box("Track_N", x, y + d - track_w, 0.01, w, track_w, 0.01)
    box("Track_S", x, y, 0.01, w, track_w, 0.01)
    box("Track_W", x, y, 0.01, track_w, d, 0.01)
    box("Track_E", x + w - track_w, y, 0.01, track_w, d, 0.01)

    # 篮球场 (中央偏北)
    court_w, court_d = 28.0, 15.0
    cx = x + (w - court_w) / 2
    cy = y + (d - court_d) / 2
    box("Basketball_Court", cx, cy, 0.01, court_w, court_d, 0.01)

    # 中场线
    wall_x("Court_Mid", cx, cy, 0.015, court_w, 0.05, 0.02)
    # 三分线简化 - 两侧半圆
    for side, cy_offset in [("N", cy + court_d), ("S", cy)]:
        cylinder(f"Court_3pt_{side}", cx + court_w/2, cy_offset, 0.015, 6.0, 0.01)

    # 健身器材区 (东侧)
    equip_x = x + w - 10
    equip_y = y + 2
    for i in range(4):
        box(f"Fitness_{i}", equip_x + (i%2)*4, equip_y + (i//2)*8, 0.02, 1.5, 0.5, 1.5)

    # 看台/休息区 (南侧)
    for i in range(3):
        box(f"Bleacher_{i}", x + 5 + i*3, y - 2, 0.15*i, 20, 2, 0.4)

    return x, y, w, d


def build_gardens():
    """绿化庭院 + 连廊系统"""
    # 中央花园 (门诊楼和住院楼之间)
    garden_x = SITE_W/2 - 20
    garden_y = 65
    garden_w, garden_d = 40, 20
    box("Garden_Central", garden_x, garden_y, 0.005, garden_w, garden_d, 0.01)

    # 花坛
    for i in range(3):
        for j in range(2):
            bx = garden_x + 3 + i * 12
            by = garden_y + 3 + j * 10
            box(f"FlowerBed_{i}_{j}", bx, by, 0.015, 8, 4, 0.3)

    # 连廊 (门诊楼 → 住院楼 → 康复楼)
    corridor_w = 3.0
    corridor_h = 3.0

    # 门诊 → 住院 A
    op_x = SITE_W/2 - 30
    op_y = 30 + 25  # 门诊北侧
    ip_a_x = SITE_W/2 - 40 - 2
    ip_a_y = 85

    # 水平连廊
    box("Corridor_OP_to_IPA", op_x + 15, op_y, 3.0, corridor_w, 20, corridor_h)
    # 连廊柱子
    for i in range(5):
        column(f"Col_Bridge1_{i}", op_x + 15 + corridor_w/2, op_y + 4 + i*4, 0, 3.0)

    # 门诊 → 康复楼 (经过中央花园)
    rehab_x = SITE_W/2 - 15
    rehab_y = 100
    box("Corridor_OP_to_REHAB", SITE_W/2 - corridor_w/2, op_y, 3.0, corridor_w,
        rehab_y - op_y, corridor_h)

    # 康复楼 → 住院 B
    ip_b_x = SITE_W/2 + 42
    ip_b_y = 85
    box("Corridor_REHAB_to_IPB", rehab_x + 30, rehab_y + 5, 3.0, 15, corridor_w, corridor_h)

    # 凉亭
    pavilion_x = garden_x + garden_w/2
    pavilion_y = garden_y + garden_d/2
    # 四根柱
    for dx, dy in [(-3,-3), (3,-3), (-3,3), (3,3)]:
        column(f"Pavilion_Col_{dx}_{dy}", pavilion_x + dx, pavilion_y + dy, 0, 3.5, 0.3)
    # 屋顶
    box("Pavilion_Roof", pavilion_x - 4, pavilion_y - 4, 3.5, 8, 8, 0.15)

    # 围墙 (院区边界)
    wall_thick = 0.20
    wall_h = 2.5
    # 南侧围墙 (留出入口)
    gate_w = 15.0
    gate_x = SITE_W/2 - gate_w/2
    wall_x("Fence_S_L", 0, 0, 0, gate_x, wall_h, wall_thick)
    wall_x("Fence_S_R", gate_x + gate_w, 0, 0, SITE_W - (gate_x + gate_w), wall_h, wall_thick)
    # 大门柱
    column("Gate_Post_L", gate_x, 0, 0, 3.5, 0.8)
    column("Gate_Post_R", gate_x + gate_w, 0, 0, 3.5, 0.8)
    # 门楣
    wall_x("Gate_Beam", gate_x, 0, 3.5, gate_w, wall_h, wall_thick)


# ============================================================
# 4. 观察员 (可移动视角)
# ============================================================

def build_observer():
    """创建可移动观察员 (1.7m 高, 胶囊体+头部+摄像机)

    位置: 院区主入口
    可作为 Godot 中的第一人称视角起点
    """
    ox = SITE_W/2
    oy = 10.0  # 入口广场
    eye_z = 1.65  # 眼睛高度

    # 身体 (胶囊体简化: 圆柱+半球)
    body_h = 1.2
    body_r = 0.25
    body_z = 0.3  # 身体底部离地

    # 躯干
    cylinder("Observer_Body", ox, oy, body_z, body_r, body_h)

    # 头部
    sphere("Observer_Head", ox, oy, body_z + body_h + 0.12, 0.14)

    # 眼睛标记 (两个小球)
    sphere("Observer_Eye_L", ox - 0.05, oy + 0.11, body_z + body_h + 0.14, 0.03)
    sphere("Observer_Eye_R", ox + 0.05, oy + 0.11, body_z + body_h + 0.14, 0.03)

    print(f"  观察员: @ ({ox:.0f}, {oy:.0f}), 眼高 {eye_z}m")
    print(f"  → Godot 中以 Observer_Body 为角色根节点, 摄像机置于 Y=1.65")

    return ox, oy, eye_z


def build_camera_rig():
    """创建摄像机装置 — Blender 内可播放的建筑漫游动画

    路径: 入口广场 → 门诊大厅 → 中庭 → 走廊 → 住院楼 → 操场
    """
    # 创建摄像机
    bpy.ops.object.camera_add(location=(SITE_W/2, 10, 1.7))
    cam = bpy.context.active_object
    cam.name = "TourCamera"
    bpy.context.scene.camera = cam

    # 创建动画关键帧路径
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 600

    # 关键帧位置 (时间, X, Y, Z)
    keyframes = [
        (1, SITE_W/2, 5, 15.0),          # 鸟瞰全景
        (60, SITE_W/2, 25, 1.7),          # 入口广场
        (120, SITE_W/2, 37, 1.7),         # 门诊大厅入口
        (180, SITE_W/2, 45, 1.7),         # 中庭内部
        (240, SITE_W/2 + 5, 50, 1.7),     # 走廊
        (300, SITE_W/2 - 20, 88, 4.5),    # 住院楼 A 入口 (F3 高度)
        (360, SITE_W/2 - 20, 90, 1.7),    # 住院楼内部
        (420, SITE_W/2 + 10, 105, 1.7),   # 康复楼
        (480, SITE_W/2 + 55, 130, 1.7),   # 操场
        (540, SITE_W/2 + 30, 140, 1.7),   # 食堂
        (600, SITE_W/2, 5, 15.0),         # 回到鸟瞰
    ]

    for frame, px, py, pz in keyframes:
        cam.location = (px, py, pz)
        cam.keyframe_insert(data_path="location", frame=frame)

    # 让摄像机始终看向院区中心
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(SITE_W/2, SITE_D/2, 5))
    target = bpy.context.active_object
    target.name = "CameraTarget"

    # 添加 Track To 约束
    constraint = cam.constraints.new(type='TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    print(f"  摄像机动画: 600帧漫游路径已创建")

    return cam


# ============================================================
# 5. 材质
# ============================================================

def create_materials():
    mats = {}

    def _m(name, r, g, b, roughness=0.5, metallic=0.0, alpha=1.0):
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = (r, g, b, alpha)
        mat.roughness = roughness
        mat.metallic = metallic
        if alpha < 1.0:
            mat.blend_method = 'BLEND'
        return mat

    mats['grass'] = _m("Grass", 0.35, 0.55, 0.28, 0.9)
    mats['road'] = _m("Road", 0.25, 0.25, 0.27, 0.8)
    mats['plaza'] = _m("Plaza", 0.55, 0.53, 0.50, 0.5)
    mats['path'] = _m("Path", 0.60, 0.55, 0.48, 0.6)
    mats['exterior'] = _m("ExteriorWall", 0.92, 0.90, 0.86, 0.7)
    mats['interior'] = _m("InteriorWall", 0.95, 0.93, 0.90, 0.8)
    mats['concrete'] = _m("Concrete", 0.65, 0.63, 0.60, 0.9)
    mats['slab'] = _m("FloorSlab", 0.70, 0.68, 0.65, 0.8)
    mats['glass'] = _m("Glass", 0.6, 0.75, 0.85, 0.1, 0.1, 0.35)
    mats['roof'] = _m("Roof", 0.35, 0.33, 0.30, 0.9)
    mats['lobby'] = _m("LobbyFloor", 0.72, 0.70, 0.68, 0.3, 0.05)
    mats['mirror'] = _m("Mirror", 0.3, 0.3, 0.35, 0.02, 0.95)
    mats['track'] = _m("Track", 0.75, 0.30, 0.25, 0.7)  # 红色跑道
    mats['court'] = _m("Court", 0.30, 0.55, 0.35, 0.6)  # 绿色球场
    mats['wood'] = _m("Wood", 0.55, 0.40, 0.25, 0.7)
    mats['skin'] = _m("Skin", 0.85, 0.75, 0.65, 0.8)  # 观察员皮肤
    mats['metal'] = _m("Metal", 0.5, 0.5, 0.55, 0.3, 0.8)  # 金属
    mats['fence'] = _m("Fence", 0.4, 0.4, 0.42, 0.7, 0.1)
    return mats


def apply_materials(mats):
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        name = obj.name.lower()
        mat = mats['exterior']

        if 'ground' in name or 'grass' in name:
            mat = mats['grass']
        elif 'road' in name:
            mat = mats['road']
        elif 'plaza' in name or 'entry' in name:
            mat = mats['plaza']
        elif 'path' in name or 'corridor_' in name and 'op' not in name and 'rehab' not in name:
            mat = mats['path']
        elif 'slab' in name:
            if 'balcony' in name or 'atrium' in name:
                mat = mats['lobby']
            elif 'roof' in name:
                mat = mats['roof']
            else:
                mat = mats['slab']
        elif 'track' in name:
            mat = mats['track']
        elif 'court' in name:
            mat = mats['court']
        elif 'ext_' in name:
            mat = mats['exterior']
        elif 'corr_' in name or 'div_' in name or 'rail' in name:
            mat = mats['interior']
        elif 'col_' in name:
            mat = mats['concrete']
        elif 'glass' in name:
            mat = mats['glass']
        elif 'mirror' in name:
            mat = mats['mirror']
        elif 'field' in name or 'bleacher' in name:
            mat = mats['court']
        elif 'flower' in name or 'garden' in name:
            mat = mats['grass']
        elif 'observer' in name:
            if 'eye' in name:
                mat = mats['metal']
            elif 'head' in name:
                mat = mats['skin']
            elif 'body' in name:
                mat = mats['skin']
        elif 'pavilion' in name and 'roof' in name:
            mat = mats['wood']
        elif 'fence' in name or 'gate' in name:
            mat = mats['fence']
        elif 'kitchen' in name:
            mat = mats['interior']
        elif 'hall_' in name:
            mat = mats['lobby']
        elif 'fitness' in name:
            mat = mats['metal']
        elif 'canopy' in name or 'step' in name:
            mat = mats['concrete']
        elif 'room_' in name or 'ward_' in name:
            mat = mats['interior']

        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat


# ============================================================
# 6. 导出
# ============================================================

def export_model(out_dir):
    os.makedirs(out_dir, exist_ok=True)

    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.select_set(True)

    fbx = os.path.join(out_dir, 'hospital.fbx')
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={'MESH'})
    print(f"  ✓ FBX: {fbx}")

    glb = os.path.join(out_dir, 'hospital.glb')
    bpy.ops.export_scene.gltf(filepath=glb, use_selection=True, export_format='GLB')
    print(f"  ✓ GLB: {glb}")

    blend = os.path.join(out_dir, 'hospital.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print(f"  ✓ Blend: {blend}")


# ============================================================
# 主流程
# ============================================================

def main():
    print("=" * 60)
    print("精神专科医院 500床院区 3D 模型 (v3.0)")
    print("综合院区: 多栋功能楼 + 操场 + 庭院 + 观察员")
    print(f"场地: {SITE_W}×{SITE_D}m")
    print("=" * 60)

    clear_scene()

    # 1. 场地
    print("\n[1] 场地基础...")
    build_site()

    # 2. 各建筑
    print("\n[2] 建筑群...")
    buildings = {}

    # 门诊医技综合楼 (南侧中央)
    bx, by, bw, bd, bh = build_outpatient()
    buildings['OP'] = (bx, by, bw, bd, bh)

    # 住院楼 A (门诊北侧偏西)
    ipa_x = SITE_W/2 - 42
    ipa_y = 85
    bx, by, bw, bd, bh = build_inpatient("IPA", ipa_x, ipa_y)
    buildings['IPA'] = (bx, by, bw, bd, bh)

    # 住院楼 B (门诊北侧偏东)
    ipb_x = SITE_W/2 + 2
    ipb_y = 85
    bx, by, bw, bd, bh = build_inpatient("IPB", ipb_x, ipb_y)
    buildings['IPB'] = (bx, by, bw, bd, bh)

    # 康复活动楼 (住院楼之间北侧)
    rehab_x = SITE_W/2 - 15
    rehab_y = 120
    bx, by, bw, bd, bh = build_rehabilitation(rehab_x, rehab_y)
    buildings['REHAB'] = (bx, by, bw, bd, bh)

    # 行政楼 (入口广场西侧)
    admin_x = SITE_W/2 - 55
    admin_y = 45
    bx, by, bw, bd, bh = build_admin(admin_x, admin_y)
    buildings['ADMIN'] = (bx, by, bw, bd, bh)

    # 食堂 (院区东南)
    cafe_x = SITE_W - 55
    cafe_y = 140
    bx, by, bw, bd, bh = build_cafeteria(cafe_x, cafe_y)
    buildings['CAFE'] = (bx, by, bw, bd, bh)

    # 3. 操场 (院区西南)
    print("\n[3] 操场...")
    field_x = 10
    field_y = 60
    build_playground(field_x, field_y)

    # 4. 绿化 + 连廊
    print("\n[4] 绿化庭院 + 连廊...")
    build_gardens()

    # 5. 观察员
    print("\n[5] 观察员 + 摄像机...")
    build_observer()
    build_camera_rig()

    # 6. 材质 + 导出
    print("\n[6] 材质 + 导出...")
    mats = create_materials()
    apply_materials(mats)
    export_model('/home/dog/game/治疗中心建模/')

    # 统计
    mesh_count = sum(1 for o in bpy.data.objects if o.type == 'MESH')
    print(f"\n{'='*60}")
    print(f"500床院区建模完成!")
    print(f"网格对象: {mesh_count}")
    print(f"建筑: 门诊楼 + 住院A + 住院B + 康复楼 + 行政楼 + 食堂")
    print(f"室外: 操场 + 花园 + 连廊 + 围墙")
    print(f"观察: 观察员模型 + 600帧漫游动画")
    print(f"输出: /home/dog/game/治疗中心建模/hospital.{{blend,fbx,glb}}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
