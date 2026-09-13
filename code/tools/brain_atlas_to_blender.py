#!/usr/bin/env python3
"""
脑图谱数据管线 — 技能树 57 脑区 → MNI坐标 → Blender 节点放置
================================================================
数据来源:
  - brain-for-blender (brainder.org): DK/Destrieux/DKT 脑区 OBJ + 皮层下结构 OBJ
  - MNI 坐标: 部分来自文献, 部分由 OBJ mesh 质心计算
  - BrainPainter (github.com/mrazvan22/brain-coloring): Blender 渲染参考

工作流:
  1. 下载 brain-for-blender OBJ (如本地已有则跳过)
  2. 对每个 OBJ 计算质心 = MNI 坐标
  3. 将我们的 57 脑区名称映射到标准图谱标签
  4. 输出 brain_regions.json → Phase 2 技能坐标映射

用法:
  python code/tools/brain_atlas_to_blender.py          # 只查文献坐标 (无需下载)
  python code/tools/brain_atlas_to_blender.py --download  # 下载 OBJ 并计算质心
  python code/tools/brain_atlas_to_blender.py --blender    # 输出可直接在 Blender 中运行的 bpy 脚本
"""

⚠️ 世代定位（2026-09-13）：本脚本是 **57 脑区那一代**的历史生成器。当前 brain_regions.json
是 69 个 functional_id / 50 解剖实体，登记生成器为 rebuild_brain_regions.py（见 data/manifest.json）。
`--blender` 模式会写出 `code/tools/place_skill_nodes_blender.py`——**该文件从未生成，其职责已由
build_brain_skill_tree_windows.py（当前世代）+ build_brain_skill_tree.py（v1 世代）取代**。
勿重跑覆盖受控契约；资产身份与重建见 design/presentation/visualization-3d/脑模型资产登记.md。

import json
import os
import sys
import math
from pathlib import Path

# ═══════════════════════════════════════════════════════════
#  SECTION 1: 技能树 60 脑区 → 标准神经解剖名称映射
# ═══════════════════════════════════════════════════════════

# 每条目: (技能树中文名, 标准英文名, brain-for-blender 中的匹配名/文件名, 大致MNI坐标)
# MNI 坐标来源: Harvard-Oxford Atlas / AAL3 / 文献
# brain-for-blender 的 DK atlas 用 FreeSurfer 命名规范

REGION_MAP = {
    # === 皮层 — 认知分支 ===
    "枕叶 V1": {
        "std_name": "V1 (Primary Visual Cortex)",
        "bfb_region": "pericalcarine",     # DK atlas: pericalcarine ≈ V1
        "mni": [-12, -85, 2],
        "category": "cortical",
        "lobe": "occipital",
    },
    "顶内沟": {
        "std_name": "Intraparietal Sulcus",
        "bfb_region": "superiorparietal",  # closest DK region
        "mni": [-30, -55, 45],
        "category": "cortical",
        "lobe": "parietal",
    },
    "顶叶": {
        "std_name": "Parietal Lobe",
        "bfb_region": "inferiorparietal",
        "mni": [-35, -60, 40],
        "category": "cortical",
        "lobe": "parietal",
    },
    "枕顶联合": {
        "std_name": "Parieto-Occipital Junction",
        "bfb_region": "lateraloccipital",
        "mni": [-20, -75, 30],
        "category": "cortical",
        "lobe": "parieto-occipital",
    },
    "丘脑枕": {
        "std_name": "Pulvinar (Thalamus)",
        "bfb_region": "Thalamus-Proper",   # subcortical
        "mni": [-15, -28, 5],
        "category": "subcortical",
        "lobe": "diencephalon",
    },

    # L2 记忆 — 颞叶/海马体
    "海马体 CA1": {
        "std_name": "Hippocampus CA1",
        "bfb_region": "Hippocampus",        # subcortical
        "mni": [-26, -18, -18],
        "category": "subcortical",
        "lobe": "temporal",
    },
    "内嗅皮层": {
        "std_name": "Entorhinal Cortex",
        "bfb_region": "entorhinal",         # DK atlas
        "mni": [-24, -10, -30],
        "category": "cortical",
        "lobe": "temporal",
    },
    "杏仁核-海马": {
        "std_name": "Amygdala-Hippocampal Junction",
        "bfb_region": "Amygdala",           # subcortical
        "mni": [-22, -8, -22],
        "category": "subcortical",
        "lobe": "temporal",
    },
    "海马体 CA3": {
        "std_name": "Hippocampus CA3",
        "bfb_region": "Hippocampus",        # subcortical
        "mni": [-28, -22, -16],
        "category": "subcortical",
        "lobe": "temporal",
    },
    "前额叶-海马": {
        "std_name": "Prefrontal-Hippocampal Pathway",
        "bfb_region": None,                 # white matter tract, not a region
        "mni": [-18, 20, -12],             # approximate: anterior hippocampus → mPFC
        "category": "white_matter",
        "lobe": "frontal-temporal",
    },

    # L3 知识表征 — TPJ/颞下回/楔前叶
    "TPJ": {  # Temporo-Parietal Junction
        "std_name": "Temporo-Parietal Junction",
        "bfb_region": "supramarginal",      # DK: supramarginal ≈ TPJ component
        "mni": [-52, -50, 28],
        "category": "cortical",
        "lobe": "temporo-parietal",
    },
    "颞下回": {
        "std_name": "Inferior Temporal Gyrus",
        "bfb_region": "inferiortemporal",
        "mni": [-48, -50, -18],
        "category": "cortical",
        "lobe": "temporal",
    },
    "楔前叶": {
        "std_name": "Precuneus",
        "bfb_region": "precuneus",
        "mni": [-8, -60, 40],
        "category": "cortical",
        "lobe": "parietal",
    },
    "角回": {
        "std_name": "Angular Gyrus",
        "bfb_region": "inferiorparietal",   # DK: angular gyrus ≈ inferior parietal
        "mni": [-44, -62, 36],
        "category": "cortical",
        "lobe": "parietal",
    },
    "颞上沟": {
        "std_name": "Superior Temporal Sulcus",
        "bfb_region": "superiortemporal",
        "mni": [-54, -38, 4],
        "category": "cortical",
        "lobe": "temporal",
    },

    # L4 表象与语言
    "Broca区": {
        "std_name": "Broca's Area (BA44/45)",
        "bfb_region": "parsopercularis",    # DK: pars opercularis ≈ Broca
        "mni": [-48, 14, 18],
        "category": "cortical",
        "lobe": "frontal",
    },
    "Wernicke区": {
        "std_name": "Wernicke's Area (BA22)",
        "bfb_region": "superiortemporal",   # posterior STG
        "mni": [-56, -42, 8],
        "category": "cortical",
        "lobe": "temporal",
    },
    "弓状束": {
        "std_name": "Arcuate Fasciculus",
        "bfb_region": None,                 # white matter tract
        "mni": [-40, -10, 24],             # midpoint of arcuate
        "category": "white_matter",
        "lobe": "frontal-temporal",
    },
    "前额叶极": {
        "std_name": "Frontal Pole (BA10)",
        "bfb_region": "rostralmiddlefrontal",  # or frontalpole in Destrieux
        "mni": [-10, 58, 8],
        "category": "cortical",
        "lobe": "frontal",
    },

    # L5 推理与决策
    "dlPFC": {
        "std_name": "Dorsolateral Prefrontal Cortex",
        "bfb_region": "rostralmiddlefrontal",  # + caudalmiddlefrontal
        "mni": [-38, 32, 34],
        "category": "cortical",
        "lobe": "frontal",
    },
    "vmPFC": {
        "std_name": "Ventromedial Prefrontal Cortex",
        "bfb_region": "medialorbitofrontal",
        "mni": [-4, 42, -14],
        "category": "cortical",
        "lobe": "frontal",
    },
    "额极": {
        "std_name": "Frontal Pole",
        "bfb_region": "frontalpole",         # Destrieux atlas
        "mni": [-8, 60, 4],
        "category": "cortical",
        "lobe": "frontal",
    },
    "OFC": {
        "std_name": "Orbitofrontal Cortex",
        "bfb_region": "lateralorbitofrontal",
        "mni": [-22, 34, -16],
        "category": "cortical",
        "lobe": "frontal",
    },

    # === 皮层下/边缘系统 — 情绪分支 ===
    "伏隔核/NAcc": {
        "std_name": "Nucleus Accumbens",
        "bfb_region": "Accumbens-area",      # subcortical
        "mni": [-10, 10, -8],
        "category": "subcortical",
        "lobe": "basal_ganglia",
    },
    "杏仁核": {
        "std_name": "Amygdala",
        "bfb_region": "Amygdala",            # subcortical
        "mni": [-22, -4, -18],
        "category": "subcortical",
        "lobe": "temporal",
    },
    "下丘脑": {
        "std_name": "Hypothalamus",
        "bfb_region": None,                  # not always segmented in DK
        "mni": [0, -4, -8],
        "category": "subcortical",
        "lobe": "diencephalon",
    },
    "腹侧纹状体": {
        "std_name": "Ventral Striatum",
        "bfb_region": "Accumbens-area",      # + Caudate (ventral)
        "mni": [-12, 12, -6],
        "category": "subcortical",
        "lobe": "basal_ganglia",
    },
    "BNST": {
        "std_name": "Bed Nucleus of Stria Terminalis",
        "bfb_region": None,                  # too small for standard atlases
        "mni": [-6, 2, 0],                  # approximate, near anterior commissure
        "category": "subcortical",
        "lobe": "basal_ganglia",
    },
    "隔区": {
        "std_name": "Septal Region",
        "bfb_region": None,
        "mni": [0, 4, -2],
        "category": "subcortical",
        "lobe": "basal_ganglia",
    },
    "前脑岛": {
        "std_name": "Anterior Insula",
        "bfb_region": "insula",
        "mni": [-34, 16, 6],
        "category": "cortical",
        "lobe": "insula",
    },
    "ACC吻侧": {
        "std_name": "Rostral Anterior Cingulate Cortex",
        "bfb_region": "rostralanteriorcingulate",
        "mni": [-6, 36, 14],
        "category": "cortical",
        "lobe": "cingulate",
    },
    "ACC背侧": {
        "std_name": "Dorsal Anterior Cingulate Cortex",
        "bfb_region": "caudalanteriorcingulate",
        "mni": [-6, 16, 32],
        "category": "cortical",
        "lobe": "cingulate",
    },
    "ACC": {
        "std_name": "Anterior Cingulate Cortex",
        "bfb_region": "caudalanteriorcingulate",
        "mni": [-5, 22, 28],
        "category": "cortical",
        "lobe": "cingulate",
    },
    "终纹床核": {
        "std_name": "Bed Nucleus of Stria Terminalis",
        "bfb_region": None,
        "mni": [-6, 2, 0],
        "category": "subcortical",
        "lobe": "basal_ganglia",
    },
    "mPFC": {
        "std_name": "Medial Prefrontal Cortex",
        "bfb_region": "superiorfrontal",      # medial aspect
        "mni": [-4, 48, 10],
        "category": "cortical",
        "lobe": "frontal",
    },
    "mPFC-杏仁核": {
        "std_name": "mPFC-Amygdala Circuit",
        "bfb_region": None,
        "mni": [-10, 20, -10],              # midpoint of mPFC→amygdala
        "category": "white_matter",
        "lobe": "frontal-temporal",
    },
    "颞极": {
        "std_name": "Temporal Pole",
        "bfb_region": "temporalpole",
        "mni": [-36, 10, -34],
        "category": "cortical",
        "lobe": "temporal",
    },

    # === 脑干/基底节 — 行为分支 ===
    "反射环路·PAG→杏仁核": {
        "std_name": "PAG-Amygdala Pathway",
        "bfb_region": None,                  # brainstem + tract
        "mni": [-4, -28, -8],              # PAG location
        "category": "brainstem",
        "lobe": "brainstem",
    },
    "反射环路·冻结反应": {
        "std_name": "Freezing Circuit (PAG→Amygdala)",
        "bfb_region": None,
        "mni": [-2, -30, -6],
        "category": "brainstem",
        "lobe": "brainstem",
    },
    "反射环路·快速闪避": {
        "std_name": "Escape Circuit (PAG→Motor)",
        "bfb_region": None,
        "mni": [2, -29, -10],
        "category": "brainstem",
        "lobe": "brainstem",
    },
    "基底节间接通路": {
        "std_name": "Basal Ganglia Indirect Pathway",
        "bfb_region": "Putamen",             # subcortical
        "mni": [-26, 0, 4],
        "category": "subcortical",
        "lobe": "basal_ganglia",
    },
    "缰核": {
        "std_name": "Habenula",
        "bfb_region": None,                  # very small
        "mni": [-4, -24, 2],
        "category": "subcortical",
        "lobe": "diencephalon",
    },
    "纹状体基质": {
        "std_name": "Striatum (Matrix)",
        "bfb_region": "Caudate",             # subcortical
        "mni": [-14, 8, 10],
        "category": "subcortical",
        "lobe": "basal_ganglia",
    },
    "NAcc壳": {
        "std_name": "NAcc Shell",
        "bfb_region": "Accumbens-area",
        "mni": [-8, 12, -8],
        "category": "subcortical",
        "lobe": "basal_ganglia",
    },
    "NAcc核": {
        "std_name": "NAcc Core",
        "bfb_region": "Accumbens-area",
        "mni": [-11, 10, -6],
        "category": "subcortical",
        "lobe": "basal_ganglia",
    },
    "VTA-NAcc": {
        "std_name": "VTA-NAcc Dopamine Pathway",
        "bfb_region": None,                  # midbrain + tract
        "mni": [-4, -16, -12],             # VTA location
        "category": "brainstem",
        "lobe": "midbrain",
    },
    "vmPFC-TPJ": {
        "std_name": "vmPFC-TPJ Connectivity",
        "bfb_region": None,
        "mni": [-20, 8, 48],               # approximate midpoint
        "category": "white_matter",
        "lobe": "frontal-parietal",
    },
    "后扣带": {
        "std_name": "Posterior Cingulate Cortex",
        "bfb_region": "posteriorcingulate",
        "mni": [-4, -44, 28],
        "category": "cortical",
        "lobe": "cingulate",
    },
    "岛叶-ACC": {
        "std_name": "Insula-ACC Salience Network",
        "bfb_region": None,
        "mni": [-20, 20, 14],              # midpoint insula→ACC
        "category": "white_matter",
        "lobe": "cingulate-insula",
    },
    "岛叶-ACC-VTA": {
        "std_name": "Insula-ACC-VTA Circuit",
        "bfb_region": None,
        "mni": [-14, 4, 6],
        "category": "white_matter",
        "lobe": "limbic",
    },
    "岛叶-PFC-杏仁核": {
        "std_name": "Insula-PFC-Amygdala Circuit",
        "bfb_region": None,
        "mni": [-28, 12, -6],
        "category": "white_matter",
        "lobe": "frontal-temporal",
    },
    "岛叶-vmPFC": {
        "std_name": "Insula-vmPFC Connectivity",
        "bfb_region": None,
        "mni": [-20, 28, -4],
        "category": "white_matter",
        "lobe": "frontal-insula",
    },
    "额顶网络": {
        "std_name": "Frontoparietal Control Network",
        "bfb_region": None,
        "mni": [-34, 42, 36],              # dlPFC node of FPN
        "category": "cortical",
        "lobe": "frontal-parietal",
    },

    # === 网络级 — 终极技能 ===
    "前额叶极·DMN": {
        "std_name": "Prefrontal Pole (DMN hub)",
        "bfb_region": "medialorbitofrontal",
        "mni": [-4, 50, -8],
        "category": "cortical",
        "lobe": "frontal",
    },
    "前额叶极·FPN": {
        "std_name": "Prefrontal Pole (FPN hub)",
        "bfb_region": "rostralmiddlefrontal",
        "mni": [-36, 46, 28],
        "category": "cortical",
        "lobe": "frontal",
    },
    "前额叶极·SN": {
        "std_name": "Prefrontal Pole (Salience Network)",
        "bfb_region": "caudalanteriorcingulate",
        "mni": [-6, 28, 28],
        "category": "cortical",
        "lobe": "cingulate",
    },
    "DMN+OFC": {
        "std_name": "DMN-OFC Convergence",
        "bfb_region": "medialorbitofrontal",
        "mni": [-4, 44, -12],
        "category": "cortical",
        "lobe": "frontal",
    },
    "杏仁核-PAG": {
        "std_name": "Amygdala-PAG Pathway",
        "bfb_region": None,
        "mni": [-12, -16, -14],
        "category": "brainstem",
        "lobe": "midbrain-temporal",
    },
    "全脑整合": {
        "std_name": "Whole-Brain Integration (Rich Club)",
        "bfb_region": None,
        "mni": [0, -10, -2],               # thalamus ≈ central hub
        "category": "subcortical",
        "lobe": "diencephalon",
    },
}

# ═══════════════════════════════════════════════════════════
#  SECTION 2: MNI → 游戏空间坐标转换
# ═══════════════════════════════════════════════════════════

def mni_to_game_space(mni_x, mni_y, mni_z):
    """
    将 MNI152 坐标 (mm, RAS+) 转换为游戏世界空间.

    MNI:  X=右(+), Y=前(+), Z=上(+)
         范围: X∈[-90,90], Y∈[-126,90], Z∈[-72,108]

    Game: X=右(V), Y=上(|A|), Z=前(D)
         范围: X∈[-1.1,+1.1], Y∈[0,1.1], Z∈[-0.8,+0.9]

    转换: game_X = mni_X / 90 * 1.0
          game_Y = mni_Z / 90 * 1.0 + 0.55
          game_Z = mni_Y / 126 * 0.85
    """
    game_x = (mni_x / 90.0) * 1.0
    game_y = (mni_z / 90.0) * 1.0 + 0.55
    game_z = (mni_y / 126.0) * 0.85
    return (round(game_x, 4), round(game_y, 4), round(game_z, 4))


# ═══════════════════════════════════════════════════════════
#  SECTION 3: 输出 brain_regions.json
# ═══════════════════════════════════════════════════════════

def generate_brain_regions_json(output_path="data/brain_regions.json"):
    """生成脑区坐标数据文件"""

    regions = {}
    for name_cn, info in REGION_MAP.items():
        mni = info["mni"]
        game_xyz = mni_to_game_space(*mni)

        regions[name_cn] = {
            "std_name": info["std_name"],
            "bfb_region": info["bfb_region"],
            "category": info["category"],
            "lobe": info["lobe"],
            "mni_xyz": list(mni),
            "game_xyz": list(game_xyz),
        }

    output = {
        "_description": "技能树57脑区的标准MNI解剖坐标与游戏空间坐标映射",
        "_source": "brain-for-blender (brainder.org, CC BY-SA 3.0), MNI152, Harvard-Oxford Atlas, literature values",
        "_created": "2026-07-11",
        "_note": "白质束/功能网络节点 (category=white_matter) 的坐标是近似中点值，精度低于解剖ROI",
        "_coordinate_system": {
            "mni": "MNI152 (mm, RAS+): X=右, Y=前, Z=上",
            "game": "游戏世界空间: X=右, Y=上, Z=前; 范围见包围盒",
            "transform": "game_X = mni_X/90*1.0; game_Y = mni_Z/90*1.0+0.55; game_Z = mni_Y/126*0.85",
        },
        "_stats": {
            "total_regions": len(regions),
            "cortical": sum(1 for r in regions.values() if r["category"] == "cortical"),
            "subcortical": sum(1 for r in regions.values() if r["category"] == "subcortical"),
            "brainstem": sum(1 for r in regions.values() if r["category"] == "brainstem"),
            "white_matter": sum(1 for r in regions.values() if r["category"] == "white_matter"),
        },
        "regions": regions,
    }

    os.makedirs(os.path.dirname(output_path) or "data", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ 已生成 {output_path}")
    print(f"   共 {len(regions)} 个脑区")
    print(f"   皮层: {output['_stats']['cortical']}, "
          f"皮层下: {output['_stats']['subcortical']}, "
          f"脑干: {output['_stats']['brainstem']}, "
          f"白质/网络: {output['_stats']['white_matter']}")

    return output


# ═══════════════════════════════════════════════════════════
#  SECTION 4: 从 brain-for-blender OBJ 计算质心 (可选)
# ═══════════════════════════════════════════════════════════

def compute_centroid_from_obj(obj_path):
    """从 OBJ 文件计算 mesh 质心"""
    try:
        import trimesh
        mesh = trimesh.load(obj_path)
        if mesh is None:
            return None
        centroid = mesh.centroid
        return [round(centroid[0], 2), round(centroid[1], 2), round(centroid[2], 2)]
    except Exception as e:
        print(f"  ⚠ 无法加载 {obj_path}: {e}")
        return None


def update_coords_from_objs(obj_dir, output_path="data/brain_regions.json"):
    """
    从 brain-for-blender 的 OBJ 文件更新坐标.
    匹配逻辑: REGION_MAP 中的 bfb_region 名称 → OBJ 文件名.
    """
    import glob

    # 加载已有 JSON
    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    obj_files = glob.glob(os.path.join(obj_dir, "**/*.obj"), recursive=True)
    print(f"找到 {len(obj_files)} 个 OBJ 文件")

    updated = 0
    for name_cn, info in data["regions"].items():
        bfb_name = info.get("bfb_region")
        if not bfb_name:
            continue

        # 尝试匹配 OBJ 文件名
        matched = None
        for obj_path in obj_files:
            fname = os.path.basename(obj_path).lower().replace(".obj", "")
            if bfb_name.lower() in fname or fname in bfb_name.lower():
                matched = obj_path
                break

        if matched:
            centroid = compute_centroid_from_obj(matched)
            if centroid:
                old_mni = info["mni_xyz"]
                info["mni_xyz"] = centroid
                info["mni_xyz_source"] = "obj_centroid"
                info["mni_xyz_old"] = old_mni
                info["game_xyz"] = list(mni_to_game_space(*centroid))
                updated += 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 已从 OBJ 更新 {updated} 个脑区坐标 → {output_path}")
    return data


# ═══════════════════════════════════════════════════════════
#  SECTION 5: 生成 Blender Python 节点放置脚本 (可选)
# ═══════════════════════════════════════════════════════════

def generate_blender_script(brain_regions_json, skill_coords_json=None,
                            output_path="code/tools/place_skill_nodes_blender.py"):
    """
    生成可在 Blender 中运行的 Python 脚本，批量创建技能节点.

    用法 (在 Blender Scripting 面板):
      import sys; sys.path.append('/path/to/game/tools')
      exec(open('code/tools/place_skill_nodes_blender.py').read())

    或命令行:
      blender --background --python code/tools/place_skill_nodes_blender.py
    """

    with open(brain_regions_json, "r", encoding="utf-8") as f:
        regions = json.load(f)

    script = '''"""Blender 技能节点批量放置脚本
用法: 在 Blender Scripting 面板中运行, 或 blender --background --python 此文件
依赖: brain_regions.json (脑区坐标), 技能→脑区映射表
"""
import bpy
import json
import os

# 加载脑区坐标
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

with open(os.path.join(PROJECT_DIR, "data", "brain_regions.json"), "r", encoding="utf-8") as f:
    brain_data = json.load(f)

# 节点配置
NODE_CONFIG = {
    "cognition": {"radius": 0.04, "color": (0.48, 0.56, 1.0), "shape": "icosahedron"},
    "emotion":    {"radius": 0.045, "color": (0.94, 0.63, 0.38), "shape": "sphere"},
    "behavior":   {"radius": 0.04, "color": (0.31, 0.76, 0.97), "shape": "cube"},
    "ultimate":   {"radius": 0.06, "color": (0.91, 0.82, 0.44), "shape": "dodecahedron"},
}

def create_node(name, game_xyz, branch, collection_name="SkillNodes"):
    """在 Blender 中创建一个技能节点"""
    cfg = NODE_CONFIG.get(branch, NODE_CONFIG["cognition"])
    x, y, z = game_xyz

    # 创建几何体
    if cfg["shape"] == "icosahedron":
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=cfg["radius"], location=(x, y, z))
    elif cfg["shape"] == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=cfg["radius"], location=(x, y, z))
    elif cfg["shape"] == "cube":
        bpy.ops.mesh.primitive_cube_add(size=cfg["radius"]*2, location=(x, y, z))
    elif cfg["shape"] == "dodecahedron":
        # 用低poly icosphere 近似
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=cfg["radius"], location=(x, y, z))

    obj = bpy.context.active_object
    obj.name = name

    # 创建材质
    mat = bpy.data.materials.new(name=f"mat_{name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*cfg["color"], 1.0)
        bsdf.inputs["Emission"].default_value = (*cfg["color"], 0.5)
    obj.data.materials.append(mat)

    # 加入集合
    coll = bpy.data.collections.get(collection_name)
    if not coll:
        coll = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(coll)
    coll.objects.link(obj)

    return obj

# ═══════════════ 从技能→脑区映射创建节点 ═══════════════
# 这里需要 skill_coords.json (Phase 2 产出), 目前用脑区坐标演示

print("=== 从 brain_regions.json 创建脑区参考节点 ===")
for region_name, info in brain_data["regions"].items():
    gxyz = info["game_xyz"]
    create_node(region_name, gxyz, "cognition", "BrainRegions")

print(f"完成! 共创建 {len(brain_data['regions'])} 个节点")
'''

    # 检查是否需要合并技能坐标
    if skill_coords_json and os.path.exists(skill_coords_json):
        # 生成含技能映射的完整版脚本
        skill_note = f"""
# 从 {skill_coords_json} 加载技能→脑区映射
with open(os.path.join(PROJECT_DIR, "{skill_coords_json}"), "r", encoding="utf-8") as f:
    skill_map = json.load(f)

print("=== 创建技能节点 (按分支分类) ===")
for skill in skill_map.get("skills", []):
    region_name = skill.get("region")
    if region_name and region_name in brain_data["regions"]:
        gxyz = brain_data["regions"][region_name]["game_xyz"]
        branch = skill.get("branch", "cognition")
        create_node(skill["name"], gxyz, branch, "SkillNodes")
    else:
        print(f"  ⚠ 技能 '{skill.get('name')}' 的脑区 '{region_name}' 不在图谱中")

print(f"完成! 共创建技能节点")
"""
        script += skill_note

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(script)

    print(f"✅ 已生成 Blender 脚本 → {output_path}")
    print(f"   在 Blender 中: 打开 Scripting 工作区, 加载并运行此脚本")
    print(f"   或命令行: blender --background --python {output_path}")


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="脑图谱数据管线")
    parser.add_argument("--download", action="store_true", help="下载 brain-for-blender OBJ 文件")
    parser.add_argument("--obj-dir", type=str, default=None, help="brain-for-blender OBJ 目录")
    parser.add_argument("--blender", action="store_true", help="生成 Blender 放置脚本")
    parser.add_argument("--skill-coords", type=str, default=None, help="技能坐标 JSON (Phase 2产出)")
    args = parser.parse_args()

    print("=" * 60)
    print("🧠 脑图谱数据管线 — 技能树 → MNI → Blender")
    print("=" * 60)

    # Step 1: 生成脑区坐标 JSON (始终执行)
    data = generate_brain_regions_json("data/brain_regions.json")

    # Step 2: 如果指定了 OBJ 目录, 从 mesh 质心更新坐标
    if args.obj_dir:
        print(f"\n📦 从 OBJ 文件更新坐标: {args.obj_dir}")
        data = update_coords_from_objs(args.obj_dir, "data/brain_regions.json")

    # Step 3: 如果需要, 生成 Blender 脚本
    if args.blender:
        print("\n🎨 生成 Blender 节点放置脚本...")
        generate_blender_script("data/brain_regions.json", args.skill_coords)

    print("\n✅ 管线完成")
    print(f"   下一步: Phase 2 — 建立技能→脑区映射表 (code/tools/map_skills_to_regions.py)")
