#!/usr/bin/env python3
"""
从 brain-for-blender OBJ 文件精炼脑区坐标
=========================================
遍历解压后的 OBJ 文件, 计算每个脑区 mesh 的质心,
更新 data/brain_regions.json 中的坐标。

用法:
  python tools/refine_coords_from_objs.py
"""

import json
import os
import glob
import math

OBJ_BASE = "技能树系统/blender_assets/all_obj"

# bfb_region 名称 → OBJ 文件路径模式
# DK atlas: lh.pial.DK.<region>.obj
# Subcortical: <name>.obj (带 Left-/Right- 前缀)

def find_obj_for_region(bfb_name, obj_base):
    """在 OBJ 目录中查找匹配给定 bfb_region 名称的文件。
    优先左半球 (lh.*), 皮层下结构找 Left-* 版本."""
    if not bfb_name:
        return None

    candidates = []

    # pial_DK (皮层)
    dk_dir = os.path.join(obj_base, "pial_DK")
    if os.path.isdir(dk_dir):
        for f in os.listdir(dk_dir):
            if f.endswith(".obj") and bfb_name.lower() in f.lower():
                # 优先左半球
                if f.startswith("lh."):
                    return os.path.join(dk_dir, f)
                candidates.append(os.path.join(dk_dir, f))

    # subcortical (皮层下)
    subcort_dir = os.path.join(obj_base, "subcortical")
    if os.path.isdir(subcort_dir):
        for f in os.listdir(subcort_dir):
            if f.endswith(".obj") and bfb_name.lower() in f.lower():
                # 优先 Left- 版本
                if f.startswith("Left-"):
                    return os.path.join(subcort_dir, f)
                candidates.append(os.path.join(subcort_dir, f))

    # 返回第一个候选
    if candidates:
        return candidates[0]

    return None


def compute_centroid(obj_path):
    """从 OBJ 文件计算 mesh 质心 (所有顶点均值)"""
    verts = []
    try:
        with open(obj_path, "r") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.split()
                    verts.append([float(parts[1]), float(parts[2]), float(parts[3])])
    except Exception as e:
        print(f"  ⚠ 读取失败 {obj_path}: {e}")
        return None

    if not verts:
        return None

    n = len(verts)
    cx = sum(v[0] for v in verts) / n
    cy = sum(v[1] for v in verts) / n
    cz = sum(v[2] for v in verts) / n
    return [round(cx, 3), round(cy, 3), round(cz, 3)]


def freesurfer_to_game(fs_xyz):
    """
    FreeSurfer RAS (mm, origin at AC) → 游戏世界空间.

    FreeSurfer RAS 范围 (实测 brain-for-blender DK atlas):
      X: [-70, 70]   (左→右)
      Y: [-130, 90]  (后→前)
      Z: [-70, 80]   (下→上)

    游戏空间:
      X: [-1.1, +1.1]  (左→右 = Valence)
      Y: [0, 1.1]      (下→上 = Intensity)
      Z: [-0.8, +0.9]  (后→前 = Autonomy)

    转换: game_X = fs_X / 70 * 1.0
          game_Y = fs_Z / 75 * 1.0 + 0.55
          game_Z = fs_Y / 120 * 0.85
    """
    fs_x, fs_y, fs_z = fs_xyz
    game_x = (fs_x / 70.0) * 1.0
    game_y = (fs_z / 75.0) * 1.0 + 0.55
    game_z = (fs_y / 120.0) * 0.85
    return [round(game_x, 4), round(game_y, 4), round(game_z, 4)]


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    obj_base = os.path.join(base_dir, OBJ_BASE)
    regions_path = os.path.join(base_dir, "data", "brain_regions.json")

    with open(regions_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 统计 OBJ 文件
    obj_count = len(glob.glob(os.path.join(obj_base, "**/*.obj"), recursive=True))
    print(f"📦 OBJ 目录: {obj_base}")
    print(f"   共 {obj_count} 个 OBJ 文件")

    # 为每个脑区查找 OBJ 并计算质心
    updated = 0
    not_found = []

    for name_cn, info in data["regions"].items():
        bfb_name = info.get("bfb_region")
        obj_path = find_obj_for_region(bfb_name, obj_base)

        if obj_path:
            centroid = compute_centroid(obj_path)
            if centroid:
                old_mni = info.get("mni_xyz", [])
                info["fs_xyz"] = centroid  # FreeSurfer RAS coordinate
                info["coord_source"] = "obj_centroid_fs"
                info["mni_literature"] = old_mni
                info["game_xyz"] = freesurfer_to_game(centroid)
                info["obj_file"] = os.path.relpath(obj_path, base_dir)
                updated += 1
        else:
            not_found.append((name_cn, bfb_name))

    # 保存更新
    data["_updated"] = "2026-07-11: OBJ质心精炼"
    with open(regions_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 已从 OBJ 精炼 {updated} 个脑区坐标")
    if not_found:
        print(f"⚠ 未找到 OBJ 的脑区 ({len(not_found)}):")
        for name, bfb in not_found:
            print(f"   {name} (bfb: {bfb})")

    # 同时更新 skill_coords.json
    skills_path = os.path.join(base_dir, "data", "skill_coords.json")
    if os.path.exists(skills_path):
        with open(skills_path, "r", encoding="utf-8") as f:
            skills_data = json.load(f)

        skill_updated = 0
        for skill in skills_data["skills"]:
            region_key = skill.get("region_matched")
            if region_key and region_key in data["regions"]:
                region_info = data["regions"][region_key]
                if region_info.get("coord_source") == "obj_centroid_fs":
                    # 应用半球
                    fs = region_info["fs_xyz"]
                    pad_x = skill["pad_xyz"][0]
                    if pad_x > 0.05:
                        fs_hemi = (abs(fs[0]), fs[1], fs[2])
                    elif pad_x < -0.05:
                        fs_hemi = (-abs(fs[0]), fs[1], fs[2])
                    else:
                        fs_hemi = (0, fs[1], fs[2])

                    skill["fs_xyz"] = list(fs_hemi)
                    skill["game_xyz_new"] = freesurfer_to_game(fs_hemi)
                    skill["coord_source"] = "obj_centroid_fs"
                    skill_updated += 1

        with open(skills_path, "w", encoding="utf-8") as f:
            json.dump(skills_data, f, ensure_ascii=False, indent=2)
        print(f"   同步更新 {skill_updated} 个技能坐标")

    # 打印几个关键变化
    print("\n📊 精炼后坐标示例 (FreeSurfer RAS → Game):")
    for name in ["杏仁核", "海马体 CA1", "dlPFC", "前额叶极"]:
        if name in data["regions"]:
            r = data["regions"][name]
            old = r.get("mni_literature", [])
            new = r.get("fs_xyz", r.get("mni_xyz", []))
            game = r["game_xyz"]
            src = r.get("coord_source", "literature")
            print(f"  {name}: FS{new} → Game{game}  [{src}]")


if __name__ == "__main__":
    main()
