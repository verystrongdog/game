#!/usr/bin/env python3
"""
精神专科医院 — OP 门诊医技综合楼 (Phase 1)
基于 01-建模规范与检查机制.md v1.0

运行: blender --background --python build_op.py

坐标系: X→东, Y→北, Z→上, 原点=院区西南角(0,0,0)
OP 位置: SW角 (80, 35), 60×25m, 4F+B1+设备层
"""

import bpy
import os
import json
import math
import sys

# ============================================================
# CONFIG — 主参数
# ============================================================

CONFIG = {
    # 场地
    "site_w": 220.0,
    "site_d": 180.0,

    # OP 建筑
    "op_x": 80.0,          # SW 角 X (院区坐标)
    "op_y": 35.0,          # SW 角 Y
    "op_w": 60.0,          # 面宽 X
    "op_d": 25.0,          # 进深 Y
    "n_floors": 4,         # 地上层数

    # 模数
    "module_3_6": 3.6,     # 半跨 (m)
    "col_spacing": 7.2,    # 柱跨 (m)

    # 层高
    "h_b1": 3.9,
    "h_f1": 4.2,
    "h_standard": 3.6,
    "h_equip": 2.5,

    # 结构
    "ext_wall": 0.30,
    "int_wall": 0.20,
    "slab_t": 0.20,
    "col_size": 0.60,
    "beam_w": 0.30,
    "beam_h": 0.60,
    "parapet_h": 3.5,

    # 走廊
    "corr_w": 2.4,

    # 楼梯
    "stair_well_w": 3.6,
    "stair_well_d": 6.0,
    "stair_run_w": 1.65,
    "stair_riser": 0.150,
    "stair_tread": 0.280,
    "stair_steps_per_floor": 24,
    "stair_steps_per_run": 12,

    # 电梯
    "elev_shaft_w": 2.4,
    "elev_shaft_d": 3.0,
    "elev_car_w": 1.4,
    "elev_car_d": 2.4,
    "elev_pit": 1.8,
    "elev_top": 5.2,

    # 门
    "door_w_ward": 1.1,
    "door_w_std": 0.9,
    "door_h": 2.1,
    "door_recess": 0.30,
    "door_frame_w": 0.10,

    # 窗
    "win_sill": 0.9,
    "win_h_ward": 1.8,
    "win_w_ward": 1.5,

    # 吊顶
    "ceil_drop": 0.5,
    "ceil_h_corr": 2.4,
    "ceil_h_ward": 2.7,

    # 护士站
    "nurse_len": 9.0,
    "nurse_desk_h_high": 1.10,
    "nurse_desk_h_low": 0.75,

    # 变形缝
    "joint_gap": 0.02,
    "joint_x": 30.0,       # OP 中轴线相对位置

    # 柱网 (开间方向, 共16个3.6m)
    "bays_x": [1.2 + i*3.6 for i in range(17)],  # 17条轴线
}

# 推导: 层高列表
CONFIG["floor_heights"] = [CONFIG["h_f1"]] + [CONFIG["h_standard"]] * (CONFIG["n_floors"] - 1)
# B1起止标高
CONFIG["z_b1_top"] = 0.0
CONFIG["z_b1_bot"] = -CONFIG["h_b1"]
# 各层楼板标高 (F1-F4)
CONFIG["z_levels"] = []
z = 0.0
for h in CONFIG["floor_heights"]:
    z += h
    CONFIG["z_levels"].append(z)
# z_levels = [4.2, 7.8, 11.4, 15.0]
CONFIG["z_eq_top"] = CONFIG["z_levels"][-1] + CONFIG["h_equip"]
CONFIG["z_parapet"] = CONFIG["z_eq_top"]

# 进深方向 (Y轴, 7.2m×3=21.6m + 外墙)
#  南→北: 外墙(0.3) + 病房区(6.8) + 走廊(2.4) + 辅助区(6.0) + 医护通道(1.5) + 外墙(0.3)
#  但 OP 不是护理单元，用不同分区:
#  F1: 大厅(12m) + 诊室(5.4m) + 走廊(2.4m) + 辅助(5.2m)
#  F2-F4: 灵活分区

# ============================================================
# 工具函数
# ============================================================

def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

def box(name, x, y, z, w, d, h, col_prefix="Col_"):
    """长方体 + 碰撞体"""
    center = (x + w/2, y + d/2, z + h/2)
    half = (w/2, d/2, h/2)
    # 视觉
    bpy.ops.mesh.primitive_cube_add(size=2)
    obj = bpy.context.active_object
    obj.name = name
    obj.location = center
    obj.scale = half
    bpy.ops.object.transform_apply(scale=True)
    # 碰撞体
    bpy.ops.mesh.primitive_cube_add(size=2)
    col = bpy.context.active_object
    col.name = col_prefix + name
    col.location = center
    col.scale = half
    bpy.ops.object.transform_apply(scale=True)
    col.display_type = 'WIRE'
    return obj

def wall_x(name, x, y, z, length, height, thick=0.20):
    return box(name, x, y, z, length, thick, height)

def wall_y(name, x, y, z, length, height, thick=0.20):
    return box(name, x, y, z, thick, length, height)

def slab_s(name, x, y, z, w, d, t=0.20):
    return box(name, x, y, z, w, d, t)

def column(name, x, y, z, h, size=0.60):
    return box(name, x - size/2, y - size/2, z, size, size, h)

def beam_x(name, x, y, z, length):
    return box(name, x, y, z, length, CONFIG["beam_w"], CONFIG["beam_h"])

def beam_y(name, x, y, z, length):
    return box(name, x, y, z, CONFIG["beam_w"], length, CONFIG["beam_h"])

def cylinder_v(name, x, y, z, r, h):
    """圆柱 + 碰撞体"""
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=(x, y, z + h/2))
    obj = bpy.context.active_object
    obj.name = name
    col = bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=(x, y, z + h/2))
    return obj

def door_opening(name, x, y, z, w, h, facing='N'):
    """门洞: 在墙上挖出矩形洞 + 门斗凹入
    facing: 开门方向 'N'朝北(墙南侧开门) / 'S'朝南
    """
    recess = CONFIG["door_recess"]
    frame_w = CONFIG["door_frame_w"]
    wall_thick = CONFIG["ext_wall"]  # 外墙默认

    # 门斗凹入: 在墙内侧挖 L 形凹槽
    if facing == 'N':
        # 门向走廊(北)开, 凹入在南侧
        box(f"DR_{name}_recess", x - frame_w, y, z, w + frame_w*2, recess, h)
    else:
        box(f"DR_{name}_recess", x - frame_w, y + wall_thick - recess, z, w + frame_w*2, recess, h)

    # 门洞穿过剩余墙体
    remaining = wall_thick - recess
    if remaining > 0.01:
        if facing == 'N':
            box(f"DR_{name}_cut", x - frame_w, y + recess, z, w + frame_w*2, remaining, h)
        else:
            box(f"DR_{name}_cut", x - frame_w, y, z, w + frame_w*2, remaining, h)

    # 门框 (两侧 + 上)
    box(f"DF_{name}_L", x - frame_w/2, y, z, frame_w, wall_thick, h)
    box(f"DF_{name}_R", x + w - frame_w/2, y, z, frame_w, wall_thick, h)
    box(f"DF_{name}_Top", x - frame_w, y, z + h, w + frame_w*2, wall_thick, frame_w)


# ============================================================
# 柱网系统
# ============================================================

def build_column_grid(bldg, x0, y0, w, d, floor_heights, b1=False):
    """生成柱网系统"""
    module = CONFIG["module_3_6"]
    col_spacing = CONFIG["col_spacing"]

    # X 方向轴线 (3.6m 间距, 共 17 条 = 0, 3.6, 7.2, ..., 57.6, 60? 不算端墙就是0-57.6)
    # 实际: 0, 3.6, 7.2, ..., 57.6 (16跨). 两端各1.2m边跨
    n_bays = int(w / module)  # 16
    grid_x = [x0 + i * module for i in range(n_bays + 1)]  # 17 lines

    # Y 方向轴线 (7.2m 间距 + 边跨)
    # d=25m → col_lines: 0, 0.3(外墙内), 7.5, 14.7, 22.0?, ...
    # 简化: 南侧病房6.8m + 中廊2.4m + 北侧6.0m + 医护1.5m = 16.7m + 外墙
    # 柱列: 南外墙内, 病房北, 走廊北, 辅助北, 北外墙内
    n_d_bays = int(d / col_spacing)  # ~3跨
    grid_y = [y0 + i * col_spacing for i in range(n_d_bays + 1)]
    # 补齐边跨
    if grid_y[-1] < y0 + d - col_spacing:
        grid_y.append(y0 + d - module)

    # 生成各层柱
    if b1:
        z_bases = [CONFIG["z_b1_bot"]]
        heights = [CONFIG["h_b1"]]
    else:
        z_bases = []
        heights = []

    z_bases.extend([0.0] + CONFIG["z_levels"][:-1])
    heights.extend(CONFIG["floor_heights"])

    for zi, hi in zip(z_bases, heights):
        for cx in grid_x:
            if cx <= x0 + 0.6 or cx >= x0 + w - 0.6:
                continue  # 跳过端墙内的柱位
            for cy in grid_y:
                if cy <= y0 + 0.6 or cy >= y0 + d - 0.6:
                    continue
                # 跳过中庭区域 (F1-F2 挑空, 中央约18×12m)
                atrium_center_x = x0 + w/2
                atrium_center_y = y0 + 7
                if abs(cx - atrium_center_x) < 9.5 and abs(cy - atrium_center_y) < 6.5:
                    if zi < CONFIG["z_levels"][1]:  # F1-F2 范围内
                        continue
                column(f"Col_{bldg}_{cx:.0f}_{cy:.0f}", cx, cy, zi, hi)


# ============================================================
# OP 建筑生成
# ============================================================

def build_op():
    """门诊医技综合楼 4F+B1+设备层"""
    bldg = "OP"
    x0 = CONFIG["op_x"]
    y0 = CONFIG["op_y"]
    w = CONFIG["op_w"]   # 60m
    d = CONFIG["op_d"]   # 25m
    module = CONFIG["module_3_6"]
    ext = CONFIG["ext_wall"]
    int_w = CONFIG["int_wall"]
    corr = CONFIG["corr_w"]
    fh = CONFIG["floor_heights"]  # [4.2, 3.6, 3.6, 3.6]
    n_floors = CONFIG["n_floors"]
    z_levels = CONFIG["z_levels"]   # [4.2, 7.8, 11.4, 15.0]

    print(f"\n{'='*60}")
    print(f"  OP 门诊医技综合楼: {w}×{d}m, {n_floors}F+B1+EQ")
    print(f"  SW角: ({x0}, {y0}), NE角: ({x0+w}, {y0+d})")
    print(f"{'='*60}")

    # ---- B1 地下室 ----
    print("\n[1] B1 地下室...")
    b1_z_bot = CONFIG["z_b1_bot"]  # -3.9
    # 外墙
    wall_x(f"Ext_{bldg}_S_B1", x0, y0, b1_z_bot, w, CONFIG["h_b1"], ext)
    wall_x(f"Ext_{bldg}_N_B1", x0, y0 + d - ext, b1_z_bot, w, CONFIG["h_b1"], ext)
    wall_y(f"Ext_{bldg}_W_B1", x0, y0, b1_z_bot, d, CONFIG["h_b1"], ext)
    wall_y(f"Ext_{bldg}_E_B1", x0 + w - ext, y0, b1_z_bot, d, CONFIG["h_b1"], ext)
    # 底板
    slab_s(f"Base_{bldg}_B1", x0, y0, b1_z_bot - 0.20, w, d, 0.30)
    # 顶板(F1楼板)
    slab_s(f"Slab_{bldg}_B1top", x0, y0, 0.0, w, d, CONFIG["slab_t"])

    # B1 内部隔墙
    # 东西向主走廊 (y=走廊中心)
    b1_corr_y = y0 + d * 0.5
    wall_x(f"Wall_{bldg}_B1_CorrS", x0, b1_corr_y - corr/2, b1_z_bot, w, CONFIG["h_b1"], int_w)
    wall_x(f"Wall_{bldg}_B1_CorrN", x0, b1_corr_y + corr/2, b1_z_bot, w, CONFIG["h_b1"], int_w)
    # 南北向隔墙 (划分房间)
    for i, rx in enumerate([x0 + w*0.25, x0 + w*0.5, x0 + w*0.75]):
        wall_y(f"Wall_{bldg}_B1_Div{i}", rx, y0, b1_z_bot, d, CONFIG["h_b1"], int_w)

    build_column_grid(bldg, x0, y0, w, d, [CONFIG["h_b1"]], b1=True)

    # ---- F1 首层 (标高 0.00) ----
    print("\n[2] F1 首层...")
    f1_h = fh[0]  # 4.2m

    # 南侧入口 (主入口 - 留空门洞)
    entry_cx = x0 + w/2
    entry_w = 10.0
    wall_x(f"Ext_{bldg}_S_L", x0, y0, 0, entry_cx - x0 - entry_w/2, f1_h, ext)
    wall_x(f"Ext_{bldg}_S_R", entry_cx + entry_w/2, y0, 0, x0 + w - (entry_cx + entry_w/2), f1_h, ext)
    # 入口门框
    box(f"Glass_{bldg}_Entry", entry_cx - entry_w/2 + 0.1, y0, 0, entry_w - 0.2, 0.05, 3.5)
    # 雨棚
    slab_s(f"Canopy_{bldg}", entry_cx - 6, y0 - 3.5, 3.5, 12, 3.5)
    # 入口台阶
    for i in range(6):
        box(f"Step_{bldg}_{i}", entry_cx - 5, y0 - (i+1)*0.35, -0.2 - (i+1)*0.15, 10, 0.35, 0.15)

    # 其他三面外墙
    wall_x(f"Ext_{bldg}_N", x0, y0 + d - ext, 0, w, f1_h, ext)
    wall_y(f"Ext_{bldg}_W", x0, y0, 0, d, f1_h, ext)
    wall_y(f"Ext_{bldg}_E", x0 + w - ext, y0, 0, d, f1_h, ext)

    # 急诊独立入口 (东立面)
    emerge_cx = x0 + w - ext
    emerge_cy = y0 + 10
    # 留空门洞 6m
    wall_y(f"Ext_{bldg}_E_N", emerge_cx, y0, 0, emerge_cy - 3, f1_h, ext)
    wall_y(f"Ext_{bldg}_E_S", emerge_cx, emerge_cy + 3, 0, (y0 + d) - (emerge_cy + 3), f1_h, ext)
    box(f"Glass_{bldg}_Emerg", emerge_cx - 0.05, emerge_cy - 3, 0, 0.05, 6, 3.5)

    # F1 楼板
    slab_s(f"Slab_{bldg}_F1", x0, y0, 0, w, d, CONFIG["slab_t"])

    # ---- 中庭 (F1-F2 挑空) ----
    print("\n[3] 中庭 (F1-F2 挑空)...")
    atrium_w = 18.0
    atrium_d = 12.0
    atrium_x = entry_cx - atrium_w/2
    atrium_y = y0 + 3.0
    atrium_h_total = fh[0] + fh[1]  # 7.8m

    # 中庭四面墙 (通高)
    wall_y(f"Atrium_W", atrium_x, atrium_y, 0, atrium_d, atrium_h_total, int_w)
    wall_y(f"Atrium_E", atrium_x + atrium_w - int_w, atrium_y, 0, atrium_d, atrium_h_total, int_w)
    # 北墙留通道
    atrium_north = atrium_y + atrium_d - int_w
    wall_x(f"Atrium_N_L", atrium_x, atrium_north, 0, atrium_w*0.35, atrium_h_total, int_w)
    wall_x(f"Atrium_N_R", atrium_x + atrium_w*0.35 + 3.6, atrium_north, 0, atrium_w*0.35, atrium_h_total, int_w)

    # F2 回廊 (标高 fh[0]=4.2m)
    balcony = 2.0
    f2_z = fh[0]
    slab_s(f"Balc_S", atrium_x, atrium_y, f2_z, atrium_w, balcony)
    slab_s(f"Balc_N", atrium_x, atrium_y + atrium_d - balcony, f2_z, atrium_w, balcony)
    slab_s(f"Balc_W", atrium_x, atrium_y + balcony, f2_z, balcony, atrium_d - 2*balcony)
    slab_s(f"Balc_E", atrium_x + atrium_w - balcony, atrium_y + balcony, f2_z, balcony, atrium_d - 2*balcony)
    # 栏杆 (1.1m高)
    wall_x(f"Rail_S", atrium_x + balcony, atrium_y + balcony, f2_z, atrium_w - 2*balcony, 1.1, 0.15)
    wall_x(f"Rail_N", atrium_x + balcony, atrium_y + atrium_d - balcony - 0.15, f2_z, atrium_w - 2*balcony, 1.1, 0.15)
    wall_y(f"Rail_W", atrium_x + balcony, atrium_y + balcony, f2_z, atrium_d - 2*balcony, 1.1, 0.15)
    wall_y(f"Rail_E", atrium_x + atrium_w - balcony - 0.15, atrium_y + balcony, f2_z, atrium_d - 2*balcony, 1.1, 0.15)
    # 中庭地面
    slab_s(f"Atrium_Floor", atrium_x, atrium_y, 0, atrium_w, atrium_d, 0.10)
    # 扶梯 (占位)
    box(f"Escalator", atrium_x + atrium_w*0.4, atrium_y + 2, 0, 1.0, 6.0, 0.5)

    # ---- F1 内部隔墙 ----
    print("\n[4] F1 内部隔墙...")
    f1_corr_center = atrium_y + atrium_d + 2.0  # 中庭北侧走廊
    f1_corr_s = f1_corr_center - corr/2
    f1_corr_n = f1_corr_center + corr/2

    # 东西向走廊墙
    wall_x(f"Wall_{bldg}_F1_CorrS", x0, f1_corr_s, 0, w, f1_h, int_w)
    wall_x(f"Wall_{bldg}_F1_CorrN", x0, f1_corr_n, 0, w, f1_h, int_w)

    # 南北向房间隔墙 (诊室/药房/挂号 — 按3.6m开间)
    n_rooms = 16
    for i in range(n_rooms + 1):
        rx = x0 + i * module
        if rx <= x0 + 0.1 or rx >= x0 + w - 0.1:
            continue
        # 走廊以南 (候诊区/大厅 → 不需要全部隔到南墙)
        south_len = f1_corr_s - y0 - ext
        if south_len > 0:
            wall_y(f"Wall_{bldg}_F1_S_{i}", rx, y0 + ext, 0, south_len, f1_h, int_w)
        # 走廊以北 (诊室/辅助)
        north_len = y0 + d - ext - f1_corr_n
        if north_len > 0:
            wall_y(f"Wall_{bldg}_F1_N_{i}", rx, f1_corr_n, 0, north_len, f1_h, int_w)

    # ---- F2 医技层 (标高 4.20) ----
    print("\n[5] F2 医技层...")
    f2_h = fh[1]
    f2_z = fh[0]
    slab_s(f"Slab_{bldg}_F2", x0, y0, f2_z, w, d, CONFIG["slab_t"])
    # 外墙
    for side in ['S','N','W','E']:
        s_fn = {'S': (x0, y0), 'N': (x0, y0+d-ext), 'W': (x0, y0), 'E': (x0+w-ext, y0)}
        s_len = w if side in ('S','N') else d
        s_axis = 'x' if side in ('S','N') else 'y'
        if s_axis == 'x':
            wall_x(f"Ext_{bldg}_{side}_F2", s_fn[side][0], s_fn[side][1], f2_z, s_len, f2_h, ext)
        else:
            wall_y(f"Ext_{bldg}_{side}_F2", s_fn[side][0], s_fn[side][1], f2_z, s_len, f2_h, ext)

    # F2 内部 (走廊 + 房间 — 同F1布局, 但走廊两侧都是房间)
    f2_corr_center = atrium_y + atrium_d + 2.0
    f2_corr_s = f2_corr_center - corr/2
    f2_corr_n = f2_corr_center + corr/2
    wall_x(f"Wall_{bldg}_F2_CorrS", x0, f2_corr_s, f2_z, w, f2_h, int_w)
    wall_x(f"Wall_{bldg}_F2_CorrN", x0, f2_corr_n, f2_z, w, f2_h, int_w)
    for i in range(n_rooms + 1):
        rx = x0 + i * module
        if rx <= x0 + 0.1 or rx >= x0 + w - 0.1:
            continue
        south_len = f2_corr_s - y0 - ext
        if south_len > 0:
            wall_y(f"Wall_{bldg}_F2_S_{i}", rx, y0 + ext, f2_z, south_len, f2_h, int_w)
        north_len = y0 + d - ext - f2_corr_n
        if north_len > 0:
            wall_y(f"Wall_{bldg}_F2_N_{i}", rx, f2_corr_n, f2_z, north_len, f2_h, int_w)

    # ---- F3-F4 标准层 ----
    for fi in range(2, n_floors):  # fi=2→F3, fi=3→F4
        print(f"\n[6] F{fi+1} 标准层...")
        fz = z_levels[fi-1]
        fh_cur = fh[fi]
        slab_s(f"Slab_{bldg}_F{fi+1}", x0, y0, fz, w, d, CONFIG["slab_t"])
        for side in ['S','N','W','E']:
            s_fn = {'S': (x0, y0), 'N': (x0, y0+d-ext), 'W': (x0, y0), 'E': (x0+w-ext, y0)}
            s_len = w if side in ('S','N') else d
            if side in ('S','N'):
                wall_x(f"Ext_{bldg}_{side}_F{fi+1}", s_fn[side][0], s_fn[side][1], fz, s_len, fh_cur, ext)
            else:
                wall_y(f"Ext_{bldg}_{side}_F{fi+1}", s_fn[side][0], s_fn[side][1], fz, s_len, fh_cur, ext)

        # 内部走廊+隔墙
        corr_center = atrium_y + atrium_d + 2.0
        wall_x(f"Wall_{bldg}_F{fi+1}_CorrS", x0, corr_center - corr/2, fz, w, fh_cur, int_w)
        wall_x(f"Wall_{bldg}_F{fi+1}_CorrN", x0, corr_center + corr/2, fz, w, fh_cur, int_w)
        for i in range(n_rooms + 1):
            rx = x0 + i * module
            if rx <= x0 + 0.1 or rx >= x0 + w - 0.1:
                continue
            s_len_s = corr_center - corr/2 - y0 - ext
            if s_len_s > 0:
                wall_y(f"Wall_{bldg}_F{fi+1}_S_{i}", rx, y0 + ext, fz, s_len_s, fh_cur, int_w)
            s_len_n = y0 + d - ext - (corr_center + corr/2)
            if s_len_n > 0:
                wall_y(f"Wall_{bldg}_F{fi+1}_N_{i}", rx, corr_center + corr/2, fz, s_len_n, fh_cur, int_w)

    # ---- 柱网 (各层) ----
    print("\n[7] 柱网...")
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        n_bays_x = int(w / module)
        n_bays_y = int(d / CONFIG["col_spacing"])
        for ix in range(n_bays_x + 1):
            cx = x0 + ix * module
            if cx <= x0 + 1.0 or cx >= x0 + w - 1.0:
                continue
            for iy in range(n_bays_y + 1):
                cy = y0 + iy * CONFIG["col_spacing"]
                if cy <= y0 + 1.0 or cy >= y0 + d - 1.0:
                    continue
                # 中庭范围跳过
                if abs(cx - atrium_x - atrium_w/2) < atrium_w/2 - 1.5 and \
                   abs(cy - atrium_y - atrium_d/2) < atrium_d/2 - 1.5 and fi < 2:
                    continue
                column(f"Col_{bldg}_{cx:.0f}_{cy:.0f}_F{fi+1}", cx, cy, fz, fh_cur)

    # ---- 楼板梁 ----
    print("\n[8] 楼板梁...")
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        # 开间方向梁 (沿X, 每隔7.2m一根)
        for iy in [y0 + j*CONFIG["col_spacing"] for j in range(int(d/CONFIG["col_spacing"]) + 1)]:
            if y0 + ext < iy < y0 + d - ext:
                beam_x(f"Beam_{bldg}_F{fi+1}_X_{iy:.0f}", x0 + ext, iy - CONFIG["beam_w"]/2, fz + fh_cur - CONFIG["beam_h"], w - 2*ext)
        # 进深方向梁 (沿Y, 每个3.6m开间一根)
        for ix in [x0 + j*module for j in range(n_bays_x + 1)]:
            if x0 + ext < ix < x0 + w - ext:
                beam_y(f"Beam_{bldg}_F{fi+1}_Y_{ix:.0f}", ix - CONFIG["beam_w"]/2, y0 + ext, fz + fh_cur - CONFIG["beam_h"], d - 2*ext)

    # ---- 楼梯 (东西两端) ----
    print("\n[9] 楼梯 + 电梯...")
    stair_w = CONFIG["stair_well_w"]
    stair_d = CONFIG["stair_well_d"]
    elev_w = CONFIG["elev_shaft_w"]
    elev_d = CONFIG["elev_shaft_d"]

    # 东端楼梯+电梯核心 (x0 + w - 5.5 附近)
    east_core_x = x0 + w - stair_w - elev_w - 2.0
    east_core_y = y0 + ext
    # 西端楼梯+电梯核心
    west_core_x = x0 + 2.0
    west_core_y = y0 + ext

    for core_x, core_y, core_label in [(west_core_x, west_core_y, "W"), (east_core_x, east_core_y, "E")]:
        # 楼梯间墙
        wall_x(f"Wall_Stair_{core_label}_S", core_x, core_y, 0, stair_w, fh[0] + fh[1] + fh[2] + fh[3], ext)
        wall_x(f"Wall_Stair_{core_label}_N", core_x, core_y + stair_d - ext, 0, stair_w, fh[0] + fh[1] + fh[2] + fh[3], ext)
        wall_y(f"Wall_Stair_{core_label}_W", core_x, core_y, 0, stair_d, fh[0] + fh[1] + fh[2] + fh[3], ext)
        wall_y(f"Wall_Stair_{core_label}_E", core_x + stair_w - ext, core_y, 0, stair_d, fh[0] + fh[1] + fh[2] + fh[3], ext)
        # 楼梯中间平台墙
        wall_y(f"Wall_Stair_{core_label}_Mid", core_x + stair_w/2 - int_w/2, core_y+0.5, 0, stair_d-1, fh[0] + fh[1] + fh[2] + fh[3], int_w)
        # 楼梯踏步 (每层24级, 占位) — 简化为一组斜面 box
        for fi in range(n_floors):
            fz = 0.0 if fi == 0 else z_levels[fi-1]
            fh_cur = fh[fi]
            # 两个梯段
            box(f"Stair_{core_label}_F{fi+1}_A", core_x + 0.3, core_y + 1.5, fz, stair_w/2 - 0.6, stair_d/2 - 1, fh_cur)
            box(f"Stair_{core_label}_F{fi+1}_B", core_x + stair_w/2 + 0.3, core_y + stair_d/2, fz, stair_w/2 - 0.6, stair_d/2 - 1, fh_cur)
            # 楼梯间楼板开洞占位（不会建模，仅标记）

    # 电梯井 (东侧核心旁)
    elev_x = east_core_x - elev_w - 0.5
    elev_y = y0 + ext + 2.0
    for side, lx, ly, lw, ld in [
        ("S", elev_x, elev_y, elev_w, ext),
        ("N", elev_x, elev_y + elev_d - ext, elev_w, ext),
        ("W", elev_x, elev_y, ext, elev_d),
        ("E", elev_x + elev_w - ext, elev_y, ext, elev_d),
    ]:
        total_h = fh[0] + fh[1] + fh[2] + fh[3] + CONFIG["elev_pit"]
        if side in ('N','S'):
            wall_x(f"Elev_{side}", lx, ly, -CONFIG["elev_pit"], lw, total_h, ext)
        else:
            wall_y(f"Elev_{side}", lx, ly, -CONFIG["elev_pit"], ld, total_h, ext)

    # 第二台电梯 (西侧)
    elev2_x = west_core_x + stair_w + 0.5
    elev2_y = y0 + ext + 2.0
    for side, lx, ly, lw, ld in [
        ("S", elev2_x, elev2_y, elev_w, ext),
        ("N", elev2_x, elev2_y + elev_d - ext, elev_w, ext),
        ("W", elev2_x, elev2_y, ext, elev_d),
        ("E", elev2_x + elev_w - ext, elev2_y, ext, elev_d),
    ]:
        total_h = fh[0] + fh[1] + fh[2] + fh[3] + CONFIG["elev_pit"]
        if side in ('N','S'):
            wall_x(f"Elev2_{side}", lx, ly, -CONFIG["elev_pit"], lw, total_h, ext)
        else:
            wall_y(f"Elev2_{side}", lx, ly, -CONFIG["elev_pit"], ld, total_h, ext)

    # ---- 设备层 ----
    print("\n[10] 设备层 + 女儿墙...")
    eq_z = z_levels[-1]  # 15.0m
    eq_h = CONFIG["h_equip"]
    # 设备层外墙 (通风百叶 - 简化)
    for side in ['S','N','W','E']:
        s_fn = {'S': (x0, y0), 'N': (x0, y0+d-ext), 'W': (x0, y0), 'E': (x0+w-ext, y0)}
        s_len = w if side in ('S','N') else d
        if side in ('S','N'):
            wall_x(f"Ext_EQ_{side}", s_fn[side][0], s_fn[side][1], eq_z, s_len, eq_h, ext)
        else:
            wall_y(f"Ext_EQ_{side}", s_fn[side][0], s_fn[side][1], eq_z, s_len, eq_h, ext)
    # 设备层楼板
    slab_s(f"Slab_EQ", x0, y0, eq_z, w, d, CONFIG["slab_t"])
    # 女儿墙
    z_parapet = eq_z + eq_h
    for side in ['S','N','W','E']:
        s_fn = {'S': (x0, y0), 'N': (x0, y0+d-ext), 'W': (x0, y0), 'E': (x0+w-ext, y0)}
        s_len = w if side in ('S','N') else d
        if side in ('S','N'):
            wall_x(f"Parapet_{side}", s_fn[side][0], s_fn[side][1], z_parapet, s_len, CONFIG["parapet_h"], ext)
        else:
            wall_y(f"Parapet_{side}", s_fn[side][0], s_fn[side][1], z_parapet, s_len, CONFIG["parapet_h"], ext)
    # 电梯机房 (东侧)
    machine_w, machine_d, machine_h = 4.0, 4.0, CONFIG["elev_top"] - eq_h
    box(f"Machine_Elev1", elev_x, elev_y, z_parapet, machine_w, machine_d, machine_h)
    box(f"Machine_Elev2", elev2_x, elev2_y, z_parapet, machine_w, machine_d, machine_h)
    # AHU 设备平台占位
    box(f"AHU_Platform", x0 + w*0.5 - 5, y0 + d*0.5 - 4, eq_z, 10, 8, 1.5)

    # ---- 门 ----
    print("\n[11] 门...")
    # F1 南侧入口门 (铁栅栏 [大玻璃门])
    door_opening(f"Door_{bldg}_F1_Main", entry_cx - entry_w/2, y0, 0, entry_w, 3.5, 'N')
    # F1 急诊入口门
    door_opening(f"Door_{bldg}_F1_Emerg", emerge_cx - ext, emerge_cy - 1.5, 0, 3.0, 2.1, 'E')
    # 各层走廊隔断门 (双开门)
    for fi in range(1, n_floors):
        fz = 0.0 if fi == 1 else z_levels[fi-2]
        fh_cur = fh[fi-1]
        corr_center = atrium_y + atrium_d + 2.0
        rx = x0 + w/2
        door_opening(f"Door_{bldg}_F{fi}_Corr", rx - 0.75, corr_center - corr/2, fz, 1.5, CONFIG["door_h"], 'N')

    # ---- 窗 ----
    print("\n[12] 窗 (material marker)...")
    # 简化: 沿外墙按3.6m间距放置窗洞标记 (材质 cutout)
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        win_z = fz + CONFIG["win_sill"]
        # 南立面窗
        for ix in [x0 + (i+0.5)*module for i in range(n_bays_x)]:
            if abs(ix - entry_cx) < entry_w/2 + 1:
                continue  # 跳过主入口
            if x0 + ext < ix < x0 + w - ext:
                box(f"Win_{bldg}_S_F{fi+1}_{ix:.0f}", ix - CONFIG["win_w_ward"]/2, y0, win_z,
                    CONFIG["win_w_ward"], 0.05, CONFIG["win_h_ward"])

    # ---- 吊顶 ----
    print("\n[13] 吊顶...")
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        ceil_z = fz + fh_cur - CONFIG["ceil_drop"]
        # 走廊吊顶
        corr_center = atrium_y + atrium_d + 2.0
        slab_s(f"Ceil_{bldg}_F{fi+1}_Corr", x0 + ext, corr_center - corr/2, ceil_z, w - 2*ext, corr, 0.02)
        # 房间吊顶 (走廊两侧)
        slab_s(f"Ceil_{bldg}_F{fi+1}_South", x0 + ext, y0 + ext, ceil_z, w - 2*ext, corr_center - corr/2 - y0 - ext, 0.02)
        slab_s(f"Ceil_{bldg}_F{fi+1}_North", x0 + ext, corr_center + corr/2, ceil_z, w - 2*ext, y0 + d - ext - (corr_center + corr/2), 0.02)

    # ---- 湿区标记 ----
    print("\n[14] 湿区 + 管道井...")
    # 每层北侧辅助区东端放置湿区 (卫生间/开水间/污物间 — 垂直对齐)
    wet_y = y0 + d - ext - 3.0  # 北侧辅助区
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        wet_x = x0 + w - 10  # 东端
        # 管道井 (2.0×1.5m)
        box(f"Plumb_{bldg}_F{fi+1}", wet_x, wet_y, fz, 2.0, 1.5, fh_cur)
        # 强弱电井
        box(f"Elec_{bldg}_F{fi+1}", wet_x + 2.5, wet_y, fz, 1.5, 1.0, fh_cur)
        box(f"ElecW_{bldg}_F{fi+1}", wet_x + 4.5, wet_y, fz, 1.5, 1.0, fh_cur)

    # ---- 护士站 (F1 北侧) ----
    print("\n[15] 护士站...")
    nurse_y = y0 + d - ext - 7
    nurse_x = x0 + 15
    # 高台
    box(f"Nurse_{bldg}_High", nurse_x, nurse_y, 0, CONFIG["nurse_len"], 0.30, CONFIG["nurse_desk_h_high"])
    # 低台
    box(f"Nurse_{bldg}_Low", nurse_x, nurse_y + 0.30, 0, CONFIG["nurse_len"], 0.68, CONFIG["nurse_desk_h_low"])

    # ---- 消防栓 ----
    print("\n[16] 消防栓...")
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        flr = f"F{fi+1}"
        for ix in [x0 + 8, x0 + 30, x0 + 50]:
            if x0 + ext < ix < x0 + w - ext:
                corr_center = atrium_y + atrium_d + 2.0
                box(f"FireH_{bldg}_{flr}_{ix:.0f}", ix, corr_center + corr/2 - 0.70, fz + 0.3, 0.70, 0.20, 1.20)

    print(f"\n{'='*60}")
    print(f"  OP 建模完成")
    return x0, y0, w, d


# ============================================================
# 材质
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

    mats['M_Wall_Ext'] = _m("M_Wall_Ext", 0.92, 0.90, 0.86, 0.7)
    mats['M_Wall_Int'] = _m("M_Wall_Int", 0.95, 0.93, 0.90, 0.8)
    mats['M_Concrete'] = _m("M_Concrete", 0.65, 0.63, 0.60, 0.9)
    mats['M_Slab'] = _m("M_Slab", 0.70, 0.68, 0.65, 0.8)
    mats['M_Glass'] = _m("M_Glass", 0.60, 0.75, 0.85, 0.1, 0.1, 0.35)
    mats['M_Roof'] = _m("M_Roof", 0.35, 0.33, 0.30, 0.9)
    mats['M_Lobby'] = _m("M_Lobby", 0.72, 0.70, 0.68, 0.3, 0.05)
    mats['M_Metal'] = _m("M_Metal", 0.50, 0.50, 0.55, 0.3, 0.8)
    mats['M_Ceil_Ward'] = _m("M_Ceil_Ward", 0.98, 0.97, 0.96, 0.9)
    mats['M_Ceil_Corr'] = _m("M_Ceil_Corr", 0.92, 0.91, 0.90, 0.7, 0.05)
    mats['M_Sign'] = _m("M_Sign", 0.15, 0.30, 0.55, 0.5)
    mats['M_Plaza'] = _m("M_Plaza", 0.55, 0.53, 0.50, 0.5)
    mats['M_Fence'] = _m("M_Fence", 0.40, 0.40, 0.42, 0.7, 0.1)
    return mats


def apply_materials(mats):
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        name = obj.name.lower()
        mat = mats['M_Wall_Ext']
        if 'ceil_' in name and 'corr' in name:
            mat = mats['M_Ceil_Corr']
        elif 'ceil_' in name:
            mat = mats['M_Ceil_Ward']
        elif 'glass' in name:
            mat = mats['M_Glass']
        elif 'atrium' in name and 'floor' in name:
            mat = mats['M_Lobby']
        elif 'col_' in name:
            mat = mats['M_Concrete']
        elif 'slab' in name or 'balc' in name:
            mat = mats['M_Slab']
        elif 'roof' in name or 'parapet' in name:
            mat = mats['M_Roof']
        elif 'sign' in name or 'fireh' in name:
            mat = mats['M_Sign']
        elif 'ext_' in name or name.startswith('wall_stair'):
            mat = mats['M_Wall_Ext']
        elif 'wall_' in name:
            mat = mats['M_Wall_Int']
        elif 'fence' in name or 'gate' in name:
            mat = mats['M_Fence']
        elif 'plaza' in name or 'path' in name:
            mat = mats['M_Plaza']
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat


# ============================================================
# IPA/IPB 住院楼
# ============================================================

def build_ip(bldg, x0, y0):
    """住院楼 4F, 40×18m, 双护理单元, 双楼梯, 铁栅栏门"""
    w = 40.0
    d = 18.0
    n_floors = CONFIG["n_floors"]
    module = CONFIG["module_3_6"]
    ext = CONFIG["ext_wall"]
    int_w = CONFIG["int_wall"]
    corr = CONFIG["corr_w"]
    fh = CONFIG["floor_heights"]
    z_levels = CONFIG["z_levels"]
    n_bays_x = int((w - 2*1.2) / module)  # ~10 跨 (如果没有大的边跨)

    print(f"\n  {bldg}: {w}×{d}m, {n_floors}F @ ({x0:.0f},{y0:.0f})")

    # 进深分区 (从南到北, 相对 y0)
    ward_depth = 6.8
    aux_depth = 6.0
    staff_corr_w = 1.5
    # Y坐标关键线
    y_south_inner = y0 + ext           # 南外墙内缘
    y_ward_north = y_south_inner + ward_depth  # 病房北 = 走廊南墙
    y_corr_south = y_ward_north + int_w        # 走廊南缘
    y_corr_north = y_corr_south + corr          # 走廊北缘
    y_aux_north = y_corr_north + int_w + aux_depth  # 辅助北墙
    y_staff_south = y_aux_north + int_w           # 医护通道南缘
    y_staff_north = y_staff_south + staff_corr_w   # 医护通道北缘
    y_north_inner = y0 + d - ext                   # 北外墙内缘

    # ---- 各层生成 ----
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        flr = f"F{fi+1}"

        # 楼板
        slab_s(f"Slab_{bldg}_{flr}", x0, y0, fz, w, d, CONFIG["slab_t"])

        # 外墙
        wall_x(f"Ext_{bldg}_S_{flr}", x0, y0, fz, w, fh_cur, ext)
        wall_x(f"Ext_{bldg}_N_{flr}", x0, y_north_inner, fz, w, fh_cur, ext)
        wall_y(f"Ext_{bldg}_W_{flr}", x0, y0, fz, d, fh_cur, ext)
        wall_y(f"Ext_{bldg}_E_{flr}", x0 + w - ext, y0, fz, d, fh_cur, ext)

        # 走廊墙 (东西贯穿)
        wall_x(f"Wall_{bldg}_{flr}_CorrS", x0, y_ward_north, fz, w, fh_cur, int_w)
        wall_x(f"Wall_{bldg}_{flr}_CorrN", x0, y_corr_north, fz, w, fh_cur, int_w)

        # 病房隔墙 (3.6m 开间, 南侧)
        for i in range(11 + 1):  # 11跨 = 12条轴线
            rx = x0 + i * module
            if rx <= x0 + 0.15 or rx >= x0 + w - 0.15:
                continue
            wall_y(f"Wall_{bldg}_{flr}_Ward{i}", rx, y_south_inner, fz, ward_depth, fh_cur, int_w)

        # 辅助区隔墙 (北侧)
        for i in range(11 + 1):
            rx = x0 + i * module
            if rx <= x0 + 0.15 or rx >= x0 + w - 0.15:
                continue
            wall_y(f"Wall_{bldg}_{flr}_Aux{i}", rx, y_corr_north + int_w, fz, aux_depth, fh_cur, int_w)

        # 医护通道北墙
        wall_x(f"Wall_{bldg}_{flr}_StaffN", x0, y_staff_north, fz, w - 6, fh_cur, int_w)  # 留两端楼梯入口

        # 护士站 (每层, 中间位置)
        nurse_x = x0 + w/2 - 4.5
        nurse_y = y_corr_north + int_w + 0.5
        box(f"Nurse_{bldg}_{flr}_High", nurse_x, nurse_y, fz, 9.0, 0.30, CONFIG["nurse_desk_h_high"])
        box(f"Nurse_{bldg}_{flr}_Low", nurse_x, nurse_y + 0.30, fz, 9.0, 0.68, CONFIG["nurse_desk_h_low"])

        # 湿区: 每层东端 (卫生间+开水间+污物间)
        wet_x = x0 + w - 12
        box(f"Plumb_{bldg}_{flr}_Pipe", wet_x, y_staff_south, fz, 2.0, 1.5, fh_cur)
        box(f"Elec_{bldg}_{flr}_Strong", wet_x + 2.5, y_staff_south, fz, 1.5, 1.0, fh_cur)
        box(f"ElecW_{bldg}_{flr}_Weak", wet_x + 4.5, y_staff_south, fz, 1.5, 1.0, fh_cur)

        # 消防栓 (走廊每20m)
        for hx in [x0 + 8, x0 + w/2, x0 + w - 10]:
            box(f"FireH_{bldg}_{flr}_{hx:.0f}", hx, y_corr_north - 0.70, fz + 0.3, 0.70, 0.20, 1.20)

        # 门 — 病房铁栅栏门 (每间一个)
        for i in range(11):
            rx = x0 + i * module + 0.2
            door_y = y_ward_north  # 门在走廊南墙上
            if rx + CONFIG["door_w_ward"] < x0 + w - 0.5:
                door_opening(f"Door_{bldg}_{flr}_Ward{i}", rx, door_y - int_w/2, fz, CONFIG["door_w_ward"], CONFIG["door_h"], 'N')

        # 安全门禁 (双开实心门, 护理单元入口 — 中间位置)
        sec_x = x0 + w/2
        door_opening(f"Door_{bldg}_{flr}_Secure", sec_x - 0.75, y_corr_north, fz, 1.5, CONFIG["door_h"], 'N')

        # 窗 (病房南侧, 每间一个)
        win_z = fz + CONFIG["win_sill"]
        for i in range(11):
            wx = x0 + i * module + 1.0
            if wx + CONFIG["win_w_ward"] < x0 + w - ext:
                box(f"Win_{bldg}_{flr}_S{i}", wx, y0, win_z, CONFIG["win_w_ward"], 0.05, CONFIG["win_h_ward"])

        # 吊顶
        ceil_z = fz + fh_cur - CONFIG["ceil_drop"]
        slab_s(f"Ceil_{bldg}_{flr}_Corr", x0 + ext, y_corr_south, ceil_z, w - 2*ext, corr, 0.02)
        slab_s(f"Ceil_{bldg}_{flr}_Ward", x0 + ext, y_south_inner, ceil_z, w - 2*ext, ward_depth, 0.02)
        slab_s(f"Ceil_{bldg}_{flr}_Aux", x0 + ext, y_corr_north + int_w, ceil_z, w - 2*ext, aux_depth, 0.02)

    # ---- 楼梯 (东西两端) ----
    stair_w = CONFIG["stair_well_w"]  # 3.6m
    stair_d = CONFIG["stair_well_d"]  # 6.0m
    for side, sx in [("W", x0 + ext), ("E", x0 + w - ext - stair_w)]:
        sy = y_staff_north  # 楼梯在北侧医护通道端
        total_h_stair = sum(fh) + CONFIG["h_b1"]
        # 楼梯间外墙
        for s_side, lx, ly, lw, ld in [
            ("S", sx, sy, stair_w, ext),
            ("N", sx, sy + stair_d - ext, stair_w, ext),
            ("W", sx, sy, ext, stair_d),
            ("E", sx + stair_w - ext, sy, ext, stair_d),
        ]:
            if s_side in ('N','S'):
                wall_x(f"Wall_Stair_{bldg}_{side}_{s_side}", lx, ly, 0, lw, total_h_stair, ext)
            else:
                wall_y(f"Wall_Stair_{bldg}_{side}_{s_side}", lx, ly, 0, ld, total_h_stair, ext)
        # 楼梯踏步占位 (每层)
        for fi in range(n_floors):
            fz = 0.0 if fi == 0 else z_levels[fi-1]
            fh_cur = fh[fi]
            box(f"Stair_{bldg}_{side}_F{fi+1}_A", sx + 0.3, sy + 1.5, fz, stair_w/2 - 0.6, stair_d/2 - 1, fh_cur)
            box(f"Stair_{bldg}_{side}_F{fi+1}_B", sx + stair_w/2 + 0.3, sy + stair_d/2, fz, stair_w/2 - 0.6, stair_d/2 - 1, fh_cur)

    # ---- 电梯 ----
    elev_w = CONFIG["elev_shaft_w"]
    elev_d = CONFIG["elev_shaft_d"]
    for ei, elev_x in enumerate([x0 + stair_w + 5, x0 + w - 2*stair_w - elev_w - 3]):
        elev_y = y_staff_north
        total_h_elev = sum(fh) + CONFIG["elev_pit"]
        for side, lx, ly, lw, ld in [
            ("S", elev_x, elev_y, elev_w, ext),
            ("N", elev_x, elev_y + elev_d - ext, elev_w, ext),
            ("W", elev_x, elev_y, ext, elev_d),
            ("E", elev_x + elev_w - ext, elev_y, ext, elev_d),
        ]:
            if side in ('N','S'):
                wall_x(f"Elev{bldg}{ei}_{side}", lx, ly, -CONFIG["elev_pit"], lw, total_h_elev, ext)
            else:
                wall_y(f"Elev{bldg}{ei}_{side}", lx, ly, -CONFIG["elev_pit"], ld, total_h_elev, ext)

    # ---- 柱网 ----
    col_spacing = CONFIG["col_spacing"]
    n_bays_y = int(d / col_spacing)
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        for ix in [x0 + j * module for j in range(int(w/module) + 1)]:
            if ix <= x0 + 1.0 or ix >= x0 + w - 1.0:
                continue
            for iy in [y0 + j * col_spacing for j in range(n_bays_y + 1)]:
                if iy <= y0 + 1.0 or iy >= y0 + d - 1.0:
                    continue
                column(f"Col_{bldg}_{ix:.0f}_{iy:.0f}_F{fi+1}", ix, iy, fz, fh_cur)

    # ---- 楼板梁 ----
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        beam_z = fz + fh_cur - CONFIG["beam_h"]
        for iy in [y0 + j * col_spacing for j in range(n_bays_y + 1)]:
            if y0 + ext < iy < y0 + d - ext:
                beam_x(f"Beam_{bldg}_F{fi+1}_Y{iy:.0f}", x0 + ext, iy - CONFIG["beam_w"]/2, beam_z, w - 2*ext)
        for ix in [x0 + j * module for j in range(int(w/module) + 1)]:
            if x0 + ext < ix < x0 + w - ext:
                beam_y(f"Beam_{bldg}_F{fi+1}_X{ix:.0f}", ix - CONFIG["beam_w"]/2, y0 + ext, beam_z, d - 2*ext)

    # ---- 设备层 (屋顶) + 女儿墙 ----
    eq_z = z_levels[-1]
    eq_h = CONFIG["h_equip"]
    for s_side, lx, ly, lw, ld in [
        ("S", x0, y0, w, ext), ("N", x0, y_north_inner, w, ext),
        ("W", x0, y0, ext, d), ("E", x0 + w - ext, y0, ext, d),
    ]:
        if s_side in ('N','S'):
            wall_x(f"Ext_EQ_{bldg}_{s_side}", lx, ly, eq_z, lw, eq_h, ext)
        else:
            wall_y(f"Ext_EQ_{bldg}_{s_side}", lx, ly, eq_z, ld, eq_h, ext)
    slab_s(f"Slab_EQ_{bldg}", x0, y0, eq_z, w, d, CONFIG["slab_t"])
    z_parapet = eq_z + eq_h
    for s in ['S','N','W','E']:
        fn = {'S': (x0, y0), 'N': (x0, y_north_inner), 'W': (x0, y0), 'E': (x0+w-ext, y0)}
        slen = w if s in ('S','N') else d
        if s in ('S','N'):
            wall_x(f"Parapet_{bldg}_{s}", fn[s][0], fn[s][1], z_parapet, slen, CONFIG["parapet_h"], ext)
        else:
            wall_y(f"Parapet_{bldg}_{s}", fn[s][0], fn[s][1], z_parapet, slen, CONFIG["parapet_h"], ext)

    print(f"  {bldg} 完成")
    return x0, y0, w, d


# ============================================================
# 通用建筑 (REHAB/ADMIN/CAFE/DORM)
# ============================================================

def build_generic(bldg, x0, y0, w, d, n_floors, room_s_depth, room_n_depth):
    """通用双廊式建筑: 走廊 + 南北两侧房间 + 单楼梯 + 单电梯"""
    module = CONFIG["module_3_6"]
    ext = CONFIG["ext_wall"]
    int_w = CONFIG["int_wall"]
    corr = CONFIG["corr_w"]
    fh = CONFIG["floor_heights"]
    z_levels = CONFIG["z_levels"]
    n_bays_x = int(w / module)

    print(f"  {bldg}: {w}×{d}m, {n_floors}F @ ({x0:.0f},{y0:.0f})")

    # 走廊中心 Y
    corr_center = y0 + room_s_depth + ext + int_w + corr/2
    corr_s = corr_center - corr/2
    corr_n = corr_center + corr/2

    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        flr = f"F{fi+1}"

        slab_s(f"Slab_{bldg}_{flr}", x0, y0, fz, w, d, CONFIG["slab_t"])

        # 外墙
        for side, lx, ly, sl, is_x in [
            ("S", x0, y0, w, True), ("N", x0, y0+d-ext, w, True),
            ("W", x0, y0, d, False), ("E", x0+w-ext, y0, d, False),
        ]:
            if is_x:
                wall_x(f"Ext_{bldg}_{side}_{flr}", lx, ly, fz, sl, fh_cur, ext)
            else:
                wall_y(f"Ext_{bldg}_{side}_{flr}", lx, ly, fz, sl, fh_cur, ext)

        # 走廊墙
        wall_x(f"Wall_{bldg}_{flr}_CorrS", x0, corr_s, fz, w, fh_cur, int_w)
        wall_x(f"Wall_{bldg}_{flr}_CorrN", x0, corr_n, fz, w, fh_cur, int_w)

        # 南北房间隔墙
        for i in range(n_bays_x + 1):
            rx = x0 + i * module
            if rx <= x0 + 0.15 or rx >= x0 + w - 0.15:
                continue
            s_len = corr_s - y0 - ext
            if s_len > 0:
                wall_y(f"Wall_{bldg}_{flr}_S{i}", rx, y0 + ext, fz, s_len, fh_cur, int_w)
            n_len = y0 + d - ext - corr_n
            if n_len > 0:
                wall_y(f"Wall_{bldg}_{flr}_N{i}", rx, corr_n, fz, n_len, fh_cur, int_w)

        # 门 (南侧房间)
        for i in range(n_bays_x):
            rx = x0 + i * module + 0.2
            if rx + CONFIG["door_w_std"] < x0 + w - 0.5:
                door_opening(f"Door_{bldg}_{flr}_S{i}", rx, corr_s - int_w/2, fz, CONFIG["door_w_std"], CONFIG["door_h"], 'N')
        # 门 (北侧房间)
        for i in range(n_bays_x):
            rx = x0 + i * module + 0.2
            if rx + CONFIG["door_w_std"] < x0 + w - 0.5:
                door_opening(f"Door_{bldg}_{flr}_N{i}", rx, corr_n - int_w/2, fz, CONFIG["door_w_std"], CONFIG["door_h"], 'N')

        # 窗
        win_z = fz + CONFIG["win_sill"]
        for i in range(n_bays_x):
            wx = x0 + i * module + 1.0
            if wx + CONFIG["win_w_ward"] < x0 + w - ext - 0.5:
                box(f"Win_{bldg}_{flr}_S{i}", wx, y0, win_z, CONFIG["win_w_ward"], 0.05, CONFIG["win_h_ward"])
                box(f"Win_{bldg}_{flr}_N{i}", wx, y0+d-ext-0.05, win_z, CONFIG["win_w_ward"], 0.05, CONFIG["win_h_ward"])

        # 吊顶
        ceil_z = fz + fh_cur - CONFIG["ceil_drop"]
        slab_s(f"Ceil_{bldg}_{flr}_Corr", x0+ext, corr_s, ceil_z, w-2*ext, corr, 0.02)
        slab_s(f"Ceil_{bldg}_{flr}_S", x0+ext, y0+ext, ceil_z, w-2*ext, corr_s-y0-ext, 0.02)
        slab_s(f"Ceil_{bldg}_{flr}_N", x0+ext, corr_n, ceil_z, w-2*ext, y0+d-ext-corr_n, 0.02)

        # 管道井 + 强弱电 (北侧东端)
        shaft_x = x0 + w - 8
        shaft_y = y0 + d - ext - 4
        box(f"Plumb_{bldg}_{flr}", shaft_x, shaft_y, fz, 2.0, 1.5, fh_cur)
        box(f"Elec_{bldg}_{flr}_S", shaft_x+2.5, shaft_y, fz, 1.5, 1.0, fh_cur)
        box(f"ElecW_{bldg}_{flr}_W", shaft_x+4.5, shaft_y, fz, 1.5, 1.0, fh_cur)

    # ---- 楼梯 (西端) ----
    stair_w = CONFIG["stair_well_w"]
    stair_d = CONFIG["stair_well_d"]
    sx = x0 + ext
    sy = y0 + d - stair_d
    total_h = sum(fh)
    for s_side, lx, ly, lw, ld in [
        ("S", sx, sy, stair_w, ext), ("N", sx, sy+stair_d-ext, stair_w, ext),
        ("W", sx, sy, ext, stair_d), ("E", sx+stair_w-ext, sy, ext, stair_d),
    ]:
        if s_side in ('N','S'):
            wall_x(f"Wall_Stair_{bldg}_{s_side}", lx, ly, 0, lw, total_h, ext)
        else:
            wall_y(f"Wall_Stair_{bldg}_{s_side}", lx, ly, 0, ld, total_h, ext)
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        box(f"Stair_{bldg}_F{fi+1}_A", sx+0.3, sy+1.5, fz, stair_w/2-0.6, stair_d/2-1, fh_cur)
        box(f"Stair_{bldg}_F{fi+1}_B", sx+stair_w/2+0.3, sy+stair_d/2, fz, stair_w/2-0.6, stair_d/2-1, fh_cur)

    # ---- 电梯 ----
    elev_w = CONFIG["elev_shaft_w"]
    elev_d = CONFIG["elev_shaft_d"]
    elev_x = sx + stair_w + 1.5
    elev_y = y0 + d - elev_d
    total_h = sum(fh) + CONFIG["elev_pit"]
    for side, lx, ly, lw, ld in [
        ("S", elev_x, elev_y, elev_w, ext), ("N", elev_x, elev_y+elev_d-ext, elev_w, ext),
        ("W", elev_x, elev_y, ext, elev_d), ("E", elev_x+elev_w-ext, elev_y, ext, elev_d),
    ]:
        if side in ('N','S'):
            wall_x(f"Elev{bldg}_{side}", lx, ly, -CONFIG["elev_pit"], lw, total_h, ext)
        else:
            wall_y(f"Elev{bldg}_{side}", lx, ly, -CONFIG["elev_pit"], ld, total_h, ext)

    # ---- 柱网 ----
    col_spacing = CONFIG["col_spacing"]
    n_bays_y = int(d / col_spacing)
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        for ix in [x0 + j*module for j in range(n_bays_x+1)]:
            if ix <= x0+1.0 or ix >= x0+w-1.0:
                continue
            for iy in [y0 + j*col_spacing for j in range(n_bays_y+1)]:
                if iy <= y0+1.0 or iy >= y0+d-1.0:
                    continue
                column(f"Col_{bldg}_{ix:.0f}_{iy:.0f}_F{fi+1}", ix, iy, fz, fh_cur)

    # ---- 楼板梁 ----
    for fi in range(n_floors):
        fz = 0.0 if fi == 0 else z_levels[fi-1]
        fh_cur = fh[fi]
        beam_z = fz + fh_cur - CONFIG["beam_h"]
        for iy in [y0 + j*col_spacing for j in range(n_bays_y+1)]:
            if y0+ext < iy < y0+d-ext:
                beam_x(f"Beam_{bldg}_F{fi+1}_Y{iy:.0f}", x0+ext, iy-CONFIG["beam_w"]/2, beam_z, w-2*ext)
        for ix in [x0 + j*module for j in range(n_bays_x+1)]:
            if x0+ext < ix < x0+w-ext:
                beam_y(f"Beam_{bldg}_F{fi+1}_X{ix:.0f}", ix-CONFIG["beam_w"]/2, y0+ext, beam_z, d-2*ext)

    # ---- 设备层 + 女儿墙 ----
    eq_z = z_levels[-1]
    eq_h = CONFIG["h_equip"]
    for s_side, lx, ly, sl, is_x in [
        ("S", x0, y0, w, True), ("N", x0, y0+d-ext, w, True),
        ("W", x0, y0, d, False), ("E", x0+w-ext, y0, d, False),
    ]:
        if is_x:
            wall_x(f"Ext_EQ_{bldg}_{s_side}", lx, ly, eq_z, sl, eq_h, ext)
        else:
            wall_y(f"Ext_EQ_{bldg}_{s_side}", lx, ly, eq_z, sl, eq_h, ext)
    slab_s(f"Slab_EQ_{bldg}", x0, y0, eq_z, w, d, CONFIG["slab_t"])
    z_parapet = eq_z + eq_h
    for s in ['S','N','W','E']:
        fn = {'S':(x0,y0), 'N':(x0,y0+d-ext), 'W':(x0,y0), 'E':(x0+w-ext,y0)}
        sl = w if s in ('S','N') else d
        if s in ('S','N'):
            wall_x(f"Parapet_{bldg}_{s}", fn[s][0], fn[s][1], z_parapet, sl, CONFIG["parapet_h"], ext)
        else:
            wall_y(f"Parapet_{bldg}_{s}", fn[s][0], fn[s][1], z_parapet, sl, CONFIG["parapet_h"], ext)

    print(f"  {bldg} 完成")
    return x0, y0, w, d


# ============================================================
# 室外空间 + 独立建筑 + Props
# ============================================================

def build_outdoor():
    """操场, 花园, 庭院, 连廊, 围墙, 门卫, 停车场, 马路, 消防车道"""
    print("\n[室外] 院区室外空间...")

    site_w = CONFIG["site_w"]
    site_d = CONFIG["site_d"]
    ext = CONFIG["ext_wall"]

    # 地面
    box("Ground_Grass", -5, -5, -0.05, site_w+10, site_d+10, 0.05)

    # 入口广场 (OP 南侧)
    plaza_w, plaza_d = 50.0, 25.0
    box("EntryPlaza", site_w/2 - plaza_w/2, 5, 0.01, plaza_w, plaza_d, 0.02)

    # 环绕马路 (宽6m, 院区边界)
    road_w = 6.0
    box("Road_South", 0, 0, 0.01, site_w, road_w, 0.02)
    box("Road_North", 0, site_d - road_w, 0.01, site_w, road_w, 0.02)
    box("Road_West", 0, 0, 0.01, road_w, site_d, 0.02)
    box("Road_East", site_w - road_w, 0, 0.01, road_w, site_d, 0.02)
    # 马路外侧地面 (20m)
    box("Road_Outer_S", -20, -20, -0.03, site_w+40, 20, 0.02)
    box("Road_Outer_N", -20, site_d, -0.03, site_w+40, 20, 0.02)
    box("Road_Outer_W", -20, -20, -0.03, 20, site_d+40, 0.02)
    box("Road_Outer_E", site_w, -20, -0.03, 20, site_d+40, 0.02)

    # 消防车道 (环形, 宽4m)
    fire_w = 4.0
    box("FireLane_S", 15, 35, 0.02, site_w-30, fire_w, 0.02)
    box("FireLane_N", 15, site_d-45, 0.02, site_w-30, fire_w, 0.02)
    box("FireLane_W", 15, 35, 0.02, fire_w, site_d-80, 0.02)
    box("FireLane_E", site_w-20, 35, 0.02, fire_w, site_d-80, 0.02)

    # 操场 (60×40m, 西南)
    field_x, field_y = 10.0, 60.0
    box("Field_Base", field_x, field_y, 0.005, 60, 40, 0.01)
    track_w = 1.5
    box("Track_N", field_x, field_y+40-track_w, 0.01, 60, track_w, 0.01)
    box("Track_S", field_x, field_y, 0.01, 60, track_w, 0.01)
    box("Track_W", field_x, field_y, 0.01, track_w, 40, 0.01)
    box("Track_E", field_x+60-track_w, field_y, 0.01, track_w, 40, 0.01)
    box("Basketball_Court", field_x+16, field_y+12, 0.01, 28, 15, 0.01)
    # 健身器材占位
    for i in range(4):
        box(f"Fitness_{i}", field_x+50+(i%2)*4, field_y+2+(i//2)*10, 0.02, 1.5, 0.5, 1.5)

    # 中央花园 (40×20m)
    garden_x, garden_y = 90.0, 75.0
    box("Garden_Central", garden_x, garden_y, 0.005, 40, 20, 0.01)
    for i in range(2):
        for j in range(2):
            box(f"FlowerBed_{i}_{j}", garden_x+3+i*17, garden_y+3+j*10, 0.015, 14, 4, 0.3)
    # 凉亭
    px, py = garden_x+20, garden_y+10
    for dx, dy in [(-3,-3),(3,-3),(-3,3),(3,3)]:
        column(f"Pavilion_Col_{dx}_{dy}", px+dx, py+dy, 0, 3.5, 0.3)
    box("Pavilion_Roof", px-4, py-4, 3.5, 8, 8, 0.15)

    # 封闭治疗庭院 (IPA/IPB 之间)
    courtyard_x, courtyard_y = 95.0, 100.0
    box("Courtyard_Base", courtyard_x, courtyard_y, 0.005, 25, 15, 0.01)
    wall_x("Courtyard_Wall_N", courtyard_x, courtyard_y+15-ext, 0, 25, 3.0, ext)
    wall_x("Courtyard_Wall_S", courtyard_x, courtyard_y, 0, 25, 3.0, ext)
    wall_y("Courtyard_Wall_W", courtyard_x, courtyard_y, 0, 15, 3.0, ext)
    wall_y("Courtyard_Wall_E", courtyard_x+25-ext, courtyard_y, 0, 15, 3.0, ext)

    # 连廊 (宽3m, 连接 OP→IPA→REHAB→IPB)
    corr_w = 3.0
    box("Corridor_OP_IPA", 95, 58, 3.0, corr_w, 39, 3.0)
    box("Corridor_IPA_REHAB", 65, 110, 3.0, 55, corr_w, 3.0)
    box("Corridor_REHAB_IPB", 113, 125, 3.0, 15, corr_w, 3.0)
    # 连廊柱
    for i in range(8):
        column(f"Col_Bridge_{i}", 96.5, 63+i*5, 0, 3.0, 0.3)

    # 围墙 (院区周界, 高2.5m)
    gate_w = 15.0
    gate_x = site_w/2 - gate_w/2
    wall_x("Fence_S_L", 0, 0, 0, gate_x, 2.5, 0.20)
    wall_x("Fence_S_R", gate_x+gate_w, 0, 0, site_w-(gate_x+gate_w), 2.5, 0.20)
    wall_x("Fence_N", 0, site_d-0.20, 0, site_w, 2.5, 0.20)
    wall_y("Fence_W", 0, 0, 0, site_d, 2.5, 0.20)
    wall_y("Fence_E", site_w-0.20, 0, 0, site_d, 2.5, 0.20)
    # 大门柱
    column("Gate_Post_L", gate_x, 0, 0, 3.5, 0.8)
    column("Gate_Post_R", gate_x+gate_w, 0, 0, 3.5, 0.8)

    # 地上停车场 (入口广场两侧)
    for side, px in [("L", 30), ("R", 145)]:
        box(f"Parking_{side}", px, 10, 0.01, 30, 15, 0.02)

    # 救护车通道+回车场 (OP 急诊入口前)
    box("Ambulance_Lane", 130, 35, 0.01, 6, 35, 0.02)
    box("Ambulance_Turn", 120, 60, 0.01, 20, 12, 0.02)

    print("  室外完成")


def build_independent():
    """锅炉房, 氧气站, 废物间, 门卫室"""
    print("\n[独立建筑] 辅助建筑...")

    # 锅炉房 (10×8m, 院区北侧)
    bx, by = 130.0, 158.0
    box("Boiler_Floor", bx, by, 0, 10, 8, 0.20)
    wall_x("Boiler_Wall_S", bx, by, 0, 10, 5.0, 0.30)
    wall_x("Boiler_Wall_N", bx, by+7.7, 0, 10, 5.0, 0.30)
    wall_y("Boiler_Wall_W", bx, by, 0, 8, 5.0, 0.30)
    wall_y("Boiler_Wall_E", bx+9.7, by, 0, 8, 5.0, 0.30)
    box("Boiler_Roof", bx, by, 5.0, 10, 8, 0.15)
    box("Boiler_Stack", bx+4.5, by+3.5, 5.0, 1.0, 1.0, 8.0)

    # 氧气站 (8×5m, 距主楼≥25m)
    ox, oy = 150.0, 160.0
    box("O2_Floor", ox, oy, 0, 8, 5, 0.20)
    wall_x("O2_Wall_S", ox, oy, 0, 8, 4.0, 0.30)
    wall_x("O2_Wall_N", ox, oy+4.7, 0, 8, 4.0, 0.30)
    wall_y("O2_Wall_W", ox, oy, 0, 5, 4.0, 0.30)
    wall_y("O2_Wall_E", ox+7.7, oy, 0, 5, 4.0, 0.30)
    box("O2_Roof", ox, oy, 4.0, 8, 5, 0.15)

    # 医疗废物暂存间 (6×4m)
    wx, wy = 160.0, 158.0
    box("Waste_Floor", wx, wy, 0, 6, 4, 0.20)
    for s, lx, ly, lw, is_x in [("S",wx,wy,6,True),("N",wx,wy+3.7,6,True),("W",wx,wy,4,False),("E",wx+5.7,wy,4,False)]:
        if is_x:
            wall_x(f"Waste_Wall_{s}", lx, ly, 0, lw, 3.5, 0.30)
        else:
            wall_y(f"Waste_Wall_{s}", lx, ly, 0, lw, 3.5, 0.30)
    box("Waste_Roof", wx, wy, 3.5, 6, 4, 0.15)

    # 门卫室 ×2 (主入口南 + 后勤入口北, 4×3m)
    for label, gx, gy in [("S", 108, 1), ("N", 108, 177)]:
        box(f"Gate_{label}_Floor", gx, gy, 0, 4, 3, 0.20)
        for s, lx, ly, lw, is_x in [("S",gx,gy,4,True),("N",gx,gy+2.7,4,True),("W",gx,gy,3,False),("E",gx+3.7,gy,3,False)]:
            if is_x:
                wall_x(f"Gate_{label}_Wall_{s}", lx, ly, 0, lw, 3.0, 0.30)
            else:
                wall_y(f"Gate_{label}_Wall_{s}", lx, ly, 0, lw, 3.0, 0.30)
        box(f"Gate_{label}_Roof", gx, gy, 3.0, 4, 3, 0.15)

    print("  独立建筑完成")


def build_props():
    """Props 方块占位体 — 医疗器械 + 家具 + 门"""
    print("\n[Props] 占位体...")

    props_dir = '/home/dog/game/治疗中心建模/props_placeholders'

    props = [
        # 医疗器械
        ("CT_Scanner", 1.9, 1.9, 2.6),
        ("XR_Machine", 1.5, 0.8, 1.8),
        ("Ultrasound", 0.6, 0.7, 1.3),
        ("ECG_Machine", 0.4, 0.5, 0.8),
        ("EEG_Machine", 0.6, 0.7, 1.5),
        ("ECT_Device", 2.0, 0.9, 1.2),
        ("Surgical_Light", 0.6, 0.6, 0.3),
        ("Lab_Bench", 1.5, 0.75, 0.85),
        ("Cabinet", 1.2, 0.5, 2.0),
        ("Sterilizer", 1.5, 1.0, 1.8),
        # 家具
        ("Bed_Ward", 2.0, 0.9, 0.2),
        ("Nightstand", 0.45, 0.45, 0.7),
        ("Wardrobe", 0.6, 0.55, 2.0),
        ("Restraint_Chair", 0.7, 0.8, 1.2),
        ("Nurse_Counter", 3.0, 0.68, 1.10),
        ("Record_Cabinet", 0.35, 0.6, 1.8),
        ("Fire_Hydrant", 0.70, 0.20, 1.20),
        # 标识
        ("Sign_Direction", 0.80, 0.05, 0.30),
        ("Sign_Room", 0.25, 0.03, 0.15),
        ("Light_Ceiling", 0.60, 0.60, 0.05),
        # 门模型 (5种)
        ("Door_Ward_Iron", 1.1, 0.05, 2.1),
        ("Door_Staff_Solid", 0.9, 0.05, 2.1),
        ("Door_Double_Solid", 1.5, 0.05, 2.1),
    ]

    for i, (name, pw, pd, ph) in enumerate(props):
        # 分散放置避免重叠 (排列在院区外)
        row = i // 8
        col = i % 8
        px = -30 + col * 4.0
        py = 200 + row * 4.0
        box(f"Prop_{name}", px, py, 0, pw, pd, ph)
        print(f"    {name}: {pw}×{pd}×{ph}m")

    print(f"  {len(props)} Props 占位体完成")


def _cut_door_openings():
    """遍历所有门洞(DF_ Door frame对象), 在碰撞墙上切出门洞"""
    from mathutils import Vector

    # 收集所有门的位置和尺寸 (从 DF_ 门框对象)
    doors = []
    for obj in bpy.data.objects:
        if not obj.name.startswith("DF_"):
            continue
        min_v, max_v = _obj_bbox_world(obj)
        if min_v is None:
            continue
        # 门的位置和尺寸 (AABB)
        dx, dy, dz = (min_v.x + max_v.x) / 2, (min_v.y + max_v.y) / 2, (min_v.z + max_v.z) / 2
        dw = max_v.x - min_v.x + 0.3  # 稍宽一点确保碰撞不挡
        dd = max_v.y - min_v.y + 0.3
        doors.append((dx, dy, dz, dw, dd))

    if not doors:
        print("  No doors found for collision cutting")
        return

    print(f"  Cutting {len(doors)} door openings in collision walls...")

    # 对每个 Col_Wall 或 Col_Ext 碰撞墙，检查是否被门洞穿过
    wall_cols = [o for o in bpy.data.objects
                 if o.type == 'MESH' and o.name.startswith("Col_")
                 and ('Col_Wall_' in o.name or 'Col_Ext_' in o.name or 'Col_Stair' in o.name)]

    cut_count = 0
    for wall in wall_cols:
        w_min, w_max = _obj_bbox_world(wall)
        if w_min is None:
            continue

        # 找穿过这面墙的所有门
        touching_doors = []
        for dx, dy, dz, dw, dd in doors:
            # 门在墙范围内?
            if (w_min.x - 0.5 < dx < w_max.x + 0.5 and
                w_min.y - 0.5 < dy < w_max.y + 0.5 and
                w_min.z < dz < w_max.z):
                touching_doors.append((dx, dy, dw, dd))

        if not touching_doors:
            continue

        # 判断墙的方向 (X墙: 宽度 >> 厚度, Y墙: 深度 >> 厚度)
        wsx, wsy, wsz = w_max.x - w_min.x, w_max.y - w_min.y, w_max.z - w_min.z
        is_x_wall = wsx > wsy * 2  # X方向更长 = X墙

        # 重新生成碰撞墙为多个分段，跳过门洞位置
        mesh = wall.data
        mat_world = wall.matrix_world

        if is_x_wall:
            # X轴墙: 沿X分段
            cuts = sorted([(d[0] - d[2]/2, d[0] + d[2]/2) for d in touching_doors], key=lambda x: x[0])
            segments = []
            seg_start = w_min.x
            for cut_start, cut_end in cuts:
                if seg_start < cut_start - 0.01:
                    segments.append((seg_start, w_min.y, w_min.z, cut_start - seg_start, wsy, wsz))
                seg_start = max(seg_start, cut_end)
            if seg_start < w_max.x - 0.01:
                segments.append((seg_start, w_min.y, w_min.z, w_max.x - seg_start, wsy, wsz))
        else:
            # Y轴墙: 沿Y分段
            cuts = sorted([(d[1] - d[3]/2, d[1] + d[3]/2) for d in touching_doors], key=lambda x: x[0])
            segments = []
            seg_start = w_min.y
            for cut_start, cut_end in cuts:
                if seg_start < cut_start - 0.01:
                    segments.append((w_min.x, seg_start, w_min.z, wsx, cut_start - seg_start, wsz))
                seg_start = max(seg_start, cut_end)
            if seg_start < w_max.y - 0.01:
                segments.append((w_min.x, seg_start, w_min.z, wsx, w_max.y - seg_start, wsz))

        # 重建碰撞墙为多个分段
        if len(segments) > 1:
            for si, (sx, sy, sz, sw, sd, sh) in enumerate(segments):
                bpy.ops.mesh.primitive_cube_add(size=2)
                seg = bpy.context.active_object
                seg.name = f"{wall.name}_D{si}"
                seg.location = (sx + sw/2, sy + sd/2, sz + sh/2)
                seg.scale = (sw/2, sd/2, sh/2)
                bpy.ops.object.transform_apply(scale=True)
            # 删除原始碰撞墙
            bpy.data.objects.remove(wall, do_unlink=True)
            cut_count += 1

    print(f"  Done: {cut_count} collision walls split for doors")


def _obj_bbox_world(obj):
    """对象世界空间AABB"""
    from mathutils import Vector
    if not obj.data or not obj.data.vertices:
        return None, None
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    xs = [v.x for v in verts]
    ys = [v.y for v in verts]
    zs = [v.z for v in verts]
    return (Vector((min(xs), min(ys), min(zs))),
            Vector((max(xs), max(ys), max(zs))))


# ============================================================
# 合并与导出
# ============================================================

def merge_and_export(out_dir):
    """合并每层墙体 + 导出 + 写 merge_map (for all buildings)"""
    merge_map = {}
    os.makedirs(out_dir, exist_ok=True)

    # 按建筑+楼层分组
    groups = defaultdict(list)
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        name = obj.name
        if name.startswith("Col_"):
            continue
        parts = name.split('_')
        if len(parts) >= 2:
            if parts[0] == 'Col':
                bldg = parts[1] if len(parts) > 1 else "UNK"
                flr = parts[2] if len(parts) > 2 else "UNK"
            else:
                bldg = parts[1] if len(parts) > 1 else "UNK"
                flr = parts[2] if len(parts) > 2 else "UNK"
            # 仅处理已知建筑
            if bldg in ("OP", "IPA", "IPB", "REHAB", "ADMIN", "CAFE", "DORM",
                          "Boiler", "O2", "Waste", "Gate", "Fence", "Ground",
                          "Entry", "Road", "Fire", "Field", "Track", "Basketball",
                          "Garden", "Courtyard", "Corridor", "Parking", "Ambulance",
                          "Prop", "Pavilion", "Flower", "Fitness"):
                key = f"{bldg}_{flr}"
                groups[key].append(obj)

    # 合并每组
    for key, objs in groups.items():
        if len(objs) < 2:
            continue
        # 选择对象
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        # 复制+合并
        bpy.ops.object.duplicate()
        bpy.ops.object.join()
        merged = bpy.context.active_object
        merged.name = f"Merged_{key}"
        # 记录映射
        merge_map[merged.name] = {
            "source_objects": [o.name for o in objs],
            "face_count": len(merged.data.polygons),
        }
        # 删除原始对象 (保留合并后)
        for o in objs:
            bpy.data.objects.remove(o, do_unlink=True)
        print(f"  Merged {key}: {len(objs)} objects → {merged.name} ({len(merged.data.polygons)} faces)")

    # 写 merge_map
    map_path = os.path.join(out_dir, 'merge_map.json')
    with open(map_path, 'w') as f:
        json.dump(merge_map, f, indent=2)
    print(f"  merge_map.json written: {len(merge_map)} groups")

    # 导出视觉 GLB (排除碰撞体)
    bpy.ops.object.select_all(action='DESELECT')
    vis_count = 0
    col_count = 0
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if obj.name.startswith("Col_"):
                obj.select_set(False)
                col_count += 1
            else:
                obj.select_set(True)
                vis_count += 1
    print(f"  Exporting {vis_count} visual meshes (excluding {col_count} collision bodies)")

    glb_path = os.path.join(out_dir, 'hospital_phase2.glb')
    bpy.ops.export_scene.gltf(filepath=glb_path, use_selection=True, export_format='GLB')
    print(f"  GLB exported: {glb_path}")

    # 导出碰撞体 GLB — 只保留建筑结构碰撞
    # 排除: 道具(Prop), 马路外延(Road_Outer), 门框(DF), 门斗(DR),
    #        窗(Win), 天花板(Ceil), 双重前缀(Col_Col), 标识(Sign),
    #        灯具(Light), 护士站(Nurse_OP等), 消防栓(FireH),
    #        栏杆(Rail), 雨棚(Canopy), 台阶(Step), 扶梯(Escalator)
    # 门洞切割: 找到每个门洞位置，把对应的碰撞墙切开
    _cut_door_openings()

    COLLISION_SKIP = (
        "Col_Prop_", "Col_Road_Outer",
        "Col_DF_", "Col_DR_", "Col_Win_", "Col_Ceil_",
        "Col_Col_", "Col_Sign_", "Col_Light_",
        "Col_Nurse_", "Col_FireH_",
        "Col_Rail_", "Col_Canopy_", "Col_Step_", "Col_Escalator",
    )
    bpy.ops.object.select_all(action='DESELECT')
    keep_count = 0
    skip_count = 0
    for obj in bpy.data.objects:
        if obj.type != 'MESH' or not obj.name.startswith("Col_"):
            continue
        skip = False
        for prefix in COLLISION_SKIP:
            if obj.name.startswith(prefix):
                skip = True
                break
        if skip:
            obj.select_set(False)
            skip_count += 1
        else:
            obj.select_set(True)
            keep_count += 1

    col_glb_path = os.path.join(out_dir, 'hospital_phase2_collision.glb')
    bpy.ops.export_scene.gltf(filepath=col_glb_path, use_selection=True, export_format='GLB')
    print(f"  Collision GLB: {keep_count} kept, {skip_count} skipped → {col_glb_path}")

    # 保存 .blend (含全部对象)
    blend_path = os.path.join(out_dir, 'hospital_phase2.blend')
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  Blend saved: {blend_path}")


# ============================================================
# 主流程
# ============================================================

def main():
    print("="*60)
    print("精神专科医院 — Phase 4 (全建筑+室外+Props)")
    print("3.6m模数, 4F+B1(OP)+设备层")
    print("="*60)

    clear_scene()

    # OP
    print(f"\n{'='*40}")
    print("  [1/7] OP 门诊医技综合楼")
    print(f"{'='*40}")
    build_op()

    # IPA
    print(f"\n{'='*40}")
    print("  [2/7] IPA 住院楼A")
    print(f"{'='*40}")
    build_ip("IPA", 55.0, 95.0)

    # IPB
    print(f"\n{'='*40}")
    print("  [3/7] IPB 住院楼B")
    print(f"{'='*40}")
    build_ip("IPB", 125.0, 95.0)

    # REHAB - 康复活动楼 (30×15m, 工疗+娱疗+活动+体疗)
    print(f"\n{'='*40}")
    print("  [4/7] REHAB 康复活动楼")
    print(f"{'='*40}")
    build_generic("REHAB", 85.0, 120.0, 30.0, 15.0, 4, 6.0, 5.0)

    # ADMIN - 行政后勤楼 (25×15m, 办公+档案+会议)
    print(f"\n{'='*40}")
    print("  [5/7] ADMIN 行政后勤楼")
    print(f"{'='*40}")
    build_generic("ADMIN", 30.0, 60.0, 25.0, 15.0, 4, 6.0, 5.0)

    # CAFE - 食堂 (20×15m, 餐厅+厨房+活动)
    print(f"\n{'='*40}")
    print("  [6/7] CAFE 食堂")
    print(f"{'='*40}")
    build_generic("CAFE", 155.0, 140.0, 20.0, 15.0, 4, 8.0, 3.0)

    # DORM - 职工值班宿舍 (20×15m)
    print(f"\n{'='*40}")
    print("  [7/7] DORM 职工值班宿舍")
    print(f"{'='*40}")
    build_generic("DORM", 25.0, 130.0, 20.0, 15.0, 4, 6.0, 5.0)

    # 室外
    print(f"\n{'='*40}")
    print("  [8/9] 室外空间 + 独立建筑")
    print(f"{'='*40}")
    build_outdoor()
    build_independent()

    # Props
    print(f"\n{'='*40}")
    print("  [9/9] Props 占位体")
    print(f"{'='*40}")
    build_props()
    mats = create_materials()
    apply_materials(mats)

    mesh_count = sum(1 for o in bpy.data.objects if o.type == 'MESH')
    col_count = sum(1 for o in bpy.data.objects if o.name.startswith('Col_'))
    print(f"\n  网格对象: {mesh_count} (含 {col_count} 碰撞体)")

    merge_and_export('/home/dog/game/治疗中心建模/')

    print(f"\n{'='*60}")
    print("Phase 4 完成!")
    print(f"{'='*60}")


if __name__ == '__main__':
    from collections import defaultdict
    main()
