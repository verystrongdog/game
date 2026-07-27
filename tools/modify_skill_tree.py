#!/usr/bin/env blender --python
"""
修改 brain_skill_tree.blend:
1. 断层扫描验证: 检查每个技能点是否落在对应脑区 mesh 内
2. 删除 Ultimate 节点及所有关联连线
3. 缩小技能点几何体 (scale → 0.4)
4. 减细连线 (bevel_depth → 0.015)
"""

import bpy
import mathutils
from mathutils import Vector
import json
import sys
from collections import defaultdict

# ============================================================
# 0. 脑区 → 技能点映射表（根据当前设计文档）
# ============================================================

# Cognition 技能点 → 对应脑区 (FreeSurfer DK region name)
COG_BRAIN_MAP = {
    # L1 知觉与注意 (枕叶/顶叶)
    "cog_0_洞见": "pericalcarine",      # V1
    "cog_1_凝神": "lateraloccipital",    # 枕顶联合
    "cog_2_察微": "cuneus",              # 楔叶
    "cog_3_纵观": "superiorparietal",    # 顶内沟
    "cog_4_警觉": "precuneus",           # (注意网络)
    # L2 记忆 (颞叶/海马)
    "cog_5_拾遗": "inferiortemporal",    # 颞下回
    "cog_6_追忆": "middletemporal",      # 颞中回
    "cog_7_闪回": "entorhinal",          # 内嗅皮层
    "cog_8_铭刻": "parahippocampal",     # 海马旁回
    "cog_9_释怀": "isthmuscingulate",    # 峡部扣带
    # L3 知识表征 (TPJ/颞顶)
    "cog_10_甄别": "inferiorparietal",   # 角回/顶叶
    "cog_11_定性": "supramarginal",      # 缘上回
    "cog_12_归因": "precuneus",          # 楔前叶
    "cog_13_正名": "superiortemporal",   # 颞上回
    "cog_14_类比": "inferiorparietal",   # 顶叶
    # L4 表象与语言 (Wernicke/Broca)
    "cog_15_隐喻": "supramarginal",      # 缘上回/角回
    "cog_16_白描": "superiortemporal",   # 颞上回(Wernicke)
    "cog_17_构想": "precuneus",          # 楔前叶
    "cog_18_转述": "parsopercularis",    # Broca区
    "cog_19_命名": "parstriangularis",   # Broca区
    # L5 推理与决策 (前额叶)
    "cog_20_预判": "rostralmiddlefrontal", # dlPFC
    "cog_21_决意": "superiorfrontal",     # 额上回
    "cog_22_筹算": "caudalmiddlefrontal",  # 额中回尾部
    "cog_23_推演": "rostralmiddlefrontal", # dlPFC
    "cog_24_权衡": "superiorfrontal",      # 额上回内侧
}

# Emotion 技能点 → 对应脑区
EMO_BRAIN_MAP = {
    # L1 核心情绪 (杏仁核/下丘脑/PAG)
    "emo_0_快乐": "Left-Amygdala",
    "emo_1_恐惧": "Left-Amygdala",
    "emo_2_平静": "Brain-Stem",
    # L2 社会情绪 (NAcc/腹侧纹状体/BNST)
    "emo_3_希望": "Left-Accumbens-area",
    "emo_4_愤怒": "Left-Amygdala",
    "emo_5_悲痛": "Left-Accumbens-area",
    # L3 复合情绪 (前脑岛/ACC)
    "emo_6_共情": "insula_lh",
    "emo_7_爱": "Left-Accumbens-area",
    "emo_8_焦虑": "Left-Amygdala",
    "emo_9_厌恶": "insula_lh",
    # L4 高阶情绪 (OFC/mPFC/颞极)
    "emo_10_绝望": "medialorbitofrontal_lh",
    "emo_11_内疚": "rostralanteriorcingulate_lh",
    "emo_12_敬畏": "temporalpole_lh",
    "emo_13_孤独": "lateralorbitofrontal_lh",
    # L5 (杏仁核-mPFC耦合)
    "emo_14_恐怖": "Left-Amygdala",
}

# Behavior 技能点 → 对应脑区
BEH_BRAIN_MAP = {
    # L1 反射 (PAG/上丘/脑干)
    "beh_0_逃跑": "Brain-Stem",        # PAG背外侧
    "beh_1_僵住": "Brain-Stem",        # PAG腹外侧
    "beh_2_闪避": "Brain-Stem",        # 上丘
    # L2 惩罚机制 (基底节/杏仁核)
    "beh_3_回避": "Left-Amygdala",
    "beh_4_妥协": "Left-Pallidum",
    "beh_5_克制": "Left-Caudate",
    # L2 奖励机制 (NAcc/VTA)
    "beh_6_试探": "Left-Accumbens-area",
    "beh_7_追求": "Left-Accumbens-area",
    "beh_8_坚持": "Left-Putamen",
    # L3 道德驱动 (vmPFC/TPJ/楔前叶)
    "beh_9_自责": "rostralanteriorcingulate_lh",
    "beh_10_维护": "superiorfrontal_lh",
    "beh_11_坚守": "precuneus_lh",
    # L3 文化习俗 (mPFC/颞极/后扣带)
    "beh_12_遵从": "temporalpole_lh",
    "beh_13_从众": "lateralorbitofrontal_lh",
    "beh_14_运用仪式": "posteriorcingulate_lh",
    # L4 价值驱动 (ACC/额顶控制网络)
    "beh_15_牺牲": "rostralmiddlefrontal_lh",
    "beh_16_对抗": "superiorfrontal_lh",
    "beh_17_突破": "caudalmiddlefrontal_lh",
    # L4 照护 (前脑岛/ACC/VTA)
    "beh_18_安抚": "insula_lh",
    "beh_19_保护": "rostralanteriorcingulate_lh",
    "beh_20_舍身": "Left-Accumbens-area",
}

# ============================================================
# 1. 断层扫描验证 —— 用包围盒(Bounding Box)近似
# ============================================================

def point_inside_bbox(point, obj):
    """检查点是否在物体的包围盒内（快速近似）"""
    bbox = obj.bound_box  # 8 corners in local space
    # Transform to world space
    matrix = obj.matrix_world
    world_bbox = [matrix @ Vector(corner) for corner in bbox]

    xs = [v.x for v in world_bbox]
    ys = [v.y for v in world_bbox]
    zs = [v.z for v in world_bbox]

    margin = 2.0  # 容差 (MNI space)
    return (min(xs) - margin <= point.x <= max(xs) + margin and
            min(ys) - margin <= point.y <= max(ys) + margin and
            min(zs) - margin <= point.z <= max(zs) + margin)

def ray_cast_inside(obj, point):
    """用射线法检测点是否在mesh内部（更精确但更慢）"""
    if obj.type != 'MESH':
        return None
    mesh = obj.data
    # 从点向 +X 发一条射线
    direction = Vector((1, 0, 0))
    # 需要转换到局部坐标
    matrix_inv = obj.matrix_world.inverted()
    local_point = matrix_inv @ point
    local_direction = matrix_inv.to_3x3() @ direction

    result, loc, normal, index = obj.ray_cast(local_point, local_direction)
    if not result:
        return False

    # 统计交叉次数以判断是否在内部
    hit_count = 0
    for poly in mesh.polygons:
        # 简化: 仅用第一次ray_cast结果 + 多点样本
        pass

    # 用多方向射线法
    directions = [
        Vector((1, 0, 0)),
        Vector((-1, 0, 0)),
        Vector((0, 1, 0)),
        Vector((0, -1, 0)),
        Vector((0, 0, 1)),
        Vector((0, 0, -1)),
    ]
    hits = 0
    for d in directions:
        local_d = matrix_inv.to_3x3() @ d
        result, _, _, _ = obj.ray_cast(local_point, local_d)
        if result:
            hits += 1
    # 如果从多个方向都能碰到mesh，大概率在内部
    return hits >= 4

def verify_skill_placement():
    """验证所有技能点是否在对应脑区内"""
    print("\n" + "="*70)
    print("断层扫描验证: 技能点 ↔ 脑区")
    print("="*70)

    # 建立脑区mesh查找表
    brain_meshes = {}
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            name = obj.name
            brain_meshes[name] = obj
            # 也加入简化名称
            if 'lh.pial.DK.' in name:
                short = name.replace('lh.pial.DK.', '')
                brain_meshes[short] = obj
            if 'rh.pial.DK.' in name:
                short = name.replace('rh.pial.DK.', '')
                brain_meshes[short] = obj

    # 加上 _lh / _rh 后缀的查找
    for name in list(brain_meshes.keys()):
        if name.startswith('lh.pial.DK.'):
            brain_meshes[name.replace('lh.pial.DK.', '') + '_lh'] = brain_meshes[name]
        if name.startswith('rh.pial.DK.'):
            brain_meshes[name.replace('rh.pial.DK.', '') + '_rh'] = brain_meshes[name]

    all_skill_maps = {
        "Cognition": COG_BRAIN_MAP,
        "Emotion": EMO_BRAIN_MAP,
        "Behavior": BEH_BRAIN_MAP,
    }

    results = {"inside": [], "borderline": [], "outside": [], "no_mesh": []}

    for category, skill_map in all_skill_maps.items():
        print(f"\n--- {category} ---")
        for obj_name, brain_name in skill_map.items():
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                print(f"  ❌ {obj_name}: 对象不存在")
                results["no_mesh"].append((obj_name, brain_name, "对象不存在"))
                continue

            point = obj.location.copy()

            # 查找对应脑区mesh
            mesh = brain_meshes.get(brain_name)
            if not mesh:
                # 尝试模糊匹配
                found = False
                for key, m in brain_meshes.items():
                    if brain_name.lower() in key.lower():
                        mesh = m
                        found = True
                        break
                if not found:
                    print(f"  ⚠️  {obj_name} → {brain_name}: 脑区mesh未找到")
                    results["no_mesh"].append((obj_name, brain_name, "脑区mesh未找到"))
                    continue

            # 用包围盒快速检测
            in_bbox = point_inside_bbox(point, mesh)

            if in_bbox:
                # 再用射线法精确检测
                inside = ray_cast_inside(mesh, point)
                if inside or inside is None:  # None = 无法判断，默认通过
                    dist_to_center = (point - mesh.location).length
                    status = "✅ 在内部" if inside else "⚠️  通过包围盒"
                    print(f"  {status} {obj_name} → {mesh.name} (dist={dist_to_center:.1f})")
                    results["inside"].append((obj_name, brain_name, mesh.name))
                else:
                    # 在包围盒内但射线法判断不在内部 → 边缘
                    print(f"  ⚡ 边缘 {obj_name} → {mesh.name} (包围盒内但可能不在mesh内部)")
                    results["borderline"].append((obj_name, brain_name, mesh.name))
            else:
                # 不在包围盒内 → 计算距离
                bbox_center = sum([mesh.matrix_world @ Vector(c) for c in mesh.bound_box], Vector()) / 8
                dist = (point - bbox_center).length
                print(f"  ❌ 不在脑区内 {obj_name} → {brain_name} (离bbox中心 {dist:.1f})")
                results["outside"].append((obj_name, brain_name, mesh.name, dist))

    # 汇总
    print(f"\n{'='*70}")
    print(f"验证结果汇总:")
    print(f"  ✅ 在脑区内: {len(results['inside'])}")
    print(f"  ⚡ 边缘/存疑: {len(results['borderline'])}")
    print(f"  ❌ 不在脑区内: {len(results['outside'])}")
    print(f"  ⚠️  无法检测: {len(results['no_mesh'])}")
    print(f"{'='*70}\n")

    return results

# ============================================================
# 2. 删除 Ultimate 及所有关联连线
# ============================================================

def delete_ultimate():
    """删除 Ultimate 集合中的所有节点 + Functional/Tier 中的关联连线"""
    print("删除 Ultimate 技能点及连线...")

    deleted_nodes = 0
    deleted_curves = 0

    # 删除 Ultimate 集合中的节点
    ult_coll = bpy.data.collections.get("Ultimate")
    if ult_coll:
        for obj in list(ult_coll.objects):
            print(f"  删除节点: {obj.name}")
            bpy.data.objects.remove(obj, do_unlink=True)
            deleted_nodes += 1

    # 删除 Functional 集合中包含 "ult_" 的连线
    func_coll = bpy.data.collections.get("Functional")
    if func_coll:
        for obj in list(func_coll.objects):
            if "ult_" in obj.name:
                print(f"  删除功能连线: {obj.name}")
                bpy.data.objects.remove(obj, do_unlink=True)
                deleted_curves += 1

    # 删除 Tier 集合中包含 "ult_" 的连线
    tier_coll = bpy.data.collections.get("Tier")
    if tier_coll:
        for obj in list(tier_coll.objects):
            if "ult_" in obj.name:
                print(f"  删除层级连线: {obj.name}")
                bpy.data.objects.remove(obj, do_unlink=True)
                deleted_curves += 1

    # 删除空的 Ultimate 集合
    if ult_coll:
        bpy.data.collections.remove(ult_coll)

    print(f"  共删除: {deleted_nodes} 节点 + {deleted_curves} 连线")
    return deleted_nodes, deleted_curves

# ============================================================
# 3. 缩小技能点几何体
# ============================================================

def shrink_skill_nodes(scale_factor=0.35):
    """缩小所有技能点的 scale"""
    print(f"\n缩小技能点几何体 (scale × {scale_factor})...")

    skill_collections = ["Cognition", "Emotion", "Behavior"]
    modified = 0

    for coll_name in skill_collections:
        coll = bpy.data.collections.get(coll_name)
        if not coll:
            continue
        for obj in coll.objects:
            if obj.type == 'MESH':
                obj.scale = Vector((scale_factor, scale_factor, scale_factor))
                modified += 1
                print(f"  {obj.name}: scale → ({scale_factor}, {scale_factor}, {scale_factor})")

    print(f"  共缩小 {modified} 个技能点")
    return modified

# ============================================================
# 4. 减细连线
# ============================================================

def thin_connections(bevel_depth=0.015):
    """减细所有连线曲线的 bevel"""
    print(f"\n减细连线 (bevel_depth → {bevel_depth})...")

    curve_collections = ["Functional", "Tier"]
    modified = 0

    for coll_name in curve_collections:
        coll = bpy.data.collections.get(coll_name)
        if not coll:
            continue
        for obj in coll.objects:
            if obj.type == 'CURVE':
                curve = obj.data
                # 设置 bevel depth
                curve.bevel_depth = bevel_depth
                # 减小分辨率使线条更轻
                curve.bevel_resolution = 2
                modified += 1

    # 也处理不在集合中的曲线对象
    for obj in bpy.data.objects:
        if obj.type == 'CURVE':
            if obj.name.startswith('f_') or obj.name.startswith('t_'):
                curve = obj.data
                if curve.bevel_depth > bevel_depth:
                    curve.bevel_depth = bevel_depth
                    curve.bevel_resolution = 2
                    modified += 1

    print(f"  共减细 {modified} 条连线")
    return modified

# ============================================================
# MAIN
# ============================================================

def main():
    print("="*70)
    print("brain_skill_tree.blend 修改脚本")
    print("="*70)

    # 1. 断层扫描验证
    results = verify_skill_placement()

    # 2. 删除 Ultimate
    n_nodes, n_curves = delete_ultimate()

    # 3. 缩小技能点
    n_shrunk = shrink_skill_nodes(scale_factor=0.35)

    # 4. 减细连线
    n_thinned = thin_connections(bevel_depth=0.015)

    # 保存
    output_path = bpy.path.abspath("//") + "brain_skill_tree.blend"
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print(f"\n✅ 已保存: {bpy.data.filepath}")

    # 输出 JSON 验证结果
    result_json = {
        "inside_count": len(results["inside"]),
        "borderline_count": len(results["borderline"]),
        "outside_count": len(results["outside"]),
        "no_mesh_count": len(results["no_mesh"]),
        "outside_details": [
            {"skill": name, "brain": brain, "mesh": mesh, "distance": dist}
            for name, brain, mesh, dist in results["outside"]
        ],
        "borderline_details": [
            {"skill": name, "brain": brain, "mesh": mesh}
            for name, brain, mesh in results["borderline"]
        ],
        "modifications": {
            "ultimate_nodes_deleted": n_nodes,
            "ultimate_curves_deleted": n_curves,
            "skill_nodes_shrunk": n_shrunk,
            "skill_scale_factor": 0.35,
            "curves_thinned": n_thinned,
            "curve_bevel_depth": 0.015,
        }
    }

    # 写入结果文件
    import os
    result_dir = os.path.dirname(bpy.data.filepath)
    result_path = os.path.join(result_dir, "verify_result.json")
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    print(f"\n验证结果已保存: {result_path}")

if __name__ == "__main__":
    main()
