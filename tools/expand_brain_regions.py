#!/usr/bin/env python3
"""
扩展脑区图谱 — 从59区扩展到全脑功能层级模型
=============================================
方案A: 脑干核团使用文献MNI坐标（点节点，不需要独立OBJ）
皮层缺失区使用 DK atlas OBJ 质心
皮下结构使用 subcortical/ OBJ 质心

输入: data/brain_regions.json (现有59区)
输出: data/brain_regions.json (覆盖为完整版)

来源标记:
  - obj_centroid: 从 brain-for-blender OBJ 计算的质心
  - literature_mni: 文献报告的 MNI 坐标
  - literature_approx: 文献近似值（无精确坐标的核团）
"""

import json
import os
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# SECTION 1: MNI ↔ Game 坐标转换
# ═══════════════════════════════════════════════════════════

def mni_to_game(mni_x, mni_y, mni_z):
    """MNI152 (RAS+) → 游戏世界空间"""
    gx = round(mni_x / 90.0, 4)
    gy = round(mni_z / 90.0 + 0.55, 4)
    gz = round(mni_y / 126.0 * 0.85, 4)
    return [gx, gy, gz]

# ═══════════════════════════════════════════════════════════
# SECTION 2: 全部脑区定义（保留原有 + 新增）
# ═══════════════════════════════════════════════════════════

# 功能层级标记 (L0-L5)
# L0=脑干反射, L1=边缘系统, L2=旁边缘, L3=初级感觉,
# L4=高级单模态, L5=跨模态认知（原L6整合并入）

ALL_REGIONS = {}

def add_region(cn_name, std_name, bfb_region, category, lobe, mni, level,
               mni_source="literature_mni", obj_file=None,
               freesurfer_name=None, notes=None):
    """添加一个脑区条目"""
    game_xyz = mni_to_game(*mni)
    entry = {
        "std_name": std_name,
        "bfb_region": bfb_region,
        "category": category,
        "lobe": lobe,
        "level": level,
        "mni_xyz": list(mni),
        "mni_xyz_source": mni_source,
        "game_xyz": game_xyz,
    }
    if obj_file:
        entry["obj_file"] = obj_file
    if freesurfer_name:
        entry["freesurfer_name"] = freesurfer_name
    if notes:
        entry["notes"] = notes
    ALL_REGIONS[cn_name] = entry

# ============================================================
# L0 脑干：生存反射 (~10个新增核团)
# ============================================================
# 文献来源: Hansen et al. (2024) Nature Neuroscience — 58个脑干核团
#           Brainstem Navigator atlas
#           Paxinos & Mai (2004) The Human Nervous System

L0_REGIONS = {
    # 中脑导水管周围灰质 — 防御行为选择的master integrator
    "PAG": {
        "std_name": "Periaqueductal Gray",
        "bfb_region": None,  # 包含在 Brain-Stem.obj 中
        "category": "brainstem",
        "lobe": "midbrain",
        "mni": [0, -30, -8],
        "notes": "防御行为选择(战/逃/冻). Hansen2024 GREEN社区核心. 柱状组织: dlPAG=主动防御, vlPAG=冻结"
    },
    # 上丘 — 威胁检测、朝向反射
    "上丘": {
        "std_name": "Superior Colliculus",
        "bfb_region": None,
        "category": "brainstem",
        "lobe": "midbrain",
        "mni": [0, -32, -4],
        "notes": "视觉-运动接口, 威胁检测→启动PAG逃逸. 接收视网膜直接输入(Glu)"
    },
    # 中缝背核 — 5-HT源头，感觉门控
    "中缝背核": {
        "std_name": "Dorsal Raphe Nucleus",
        "bfb_region": None,
        "category": "brainstem",
        "lobe": "midbrain",
        "mni": [0, -32, -14],
        "notes": "5-HT源头. Hansen2024 PINK社区, 全脑关键hub. 感觉门控/冲动抑制/攻击调节"
    },
    # 中缝正中核
    "中缝正中核": {
        "std_name": "Median Raphe Nucleus",
        "bfb_region": None,
        "category": "brainstem",
        "lobe": "midbrain",
        "mni": [0, -30, -18],
        "notes": "5-HT. 投射至海马/隔区. Hansen2024 GREEN社区"
    },
    # 蓝斑 — NE源头，全局唤醒
    "蓝斑": {
        "std_name": "Locus Coeruleus",
        "bfb_region": None,
        "category": "brainstem",
        "lobe": "pons",
        "mni": [-8, -34, -22],
        "notes": "NE源头. Hansen2024 PINK社区, 全脑最强hub. 唤醒/警觉/应激. 双侧, 左(-8,-34,-22) 右(+8,-34,-22)"
    },
    # 黑质致密部 — DA源头之一
    "黑质致密部": {
        "std_name": "Substantia Nigra pars compacta",
        "bfb_region": None,
        "category": "brainstem",
        "lobe": "midbrain",
        "mni": [-10, -18, -14],
        "notes": "DA源头. Hansen2024 GREEN社区. 运动启动/奖励学习. 帕金森病关键结构"
    },
    # VTA — DA源头，动机突显
    "VTA": {
        "std_name": "Ventral Tegmental Area",
        "bfb_region": None,
        "category": "brainstem",
        "lobe": "midbrain",
        "mni": [0, -16, -12],
        "notes": "DA源头. Hansen2024 GREEN+BLUE社区. 动机突显(正/负)/目标导向. 投射至NAcc/PFC/杏仁核"
    },
    # 蓝斑(右)
    "蓝斑_R": {
        "std_name": "Locus Coeruleus (Right)",
        "bfb_region": None,
        "category": "brainstem",
        "lobe": "pons",
        "mni": [8, -34, -22],
        "notes": "蓝斑右侧对应. 与左侧共同构成双侧LC"
    },
    # 黑质致密部(右)
    "黑质致密部_R": {
        "std_name": "Substantia Nigra pars compacta (Right)",
        "bfb_region": None,
        "category": "brainstem",
        "lobe": "midbrain",
        "mni": [10, -18, -14],
        "notes": "黑质右侧"
    },
    # 脑桥网状核
    "脑桥网状核": {
        "std_name": "Pontine Reticular Nucleus",
        "bfb_region": None,
        "category": "brainstem",
        "lobe": "pons",
        "mni": [0, -30, -28],
        "notes": "Hansen2024 YELLOW社区. 脑桥网状结构, 运动/自主功能整合"
    },
}

for name, info in L0_REGIONS.items():
    add_region(name, info["std_name"], info["bfb_region"],
               info["category"], info["lobe"], info["mni"],
               level=0, mni_source="literature_mni",
               notes=info.get("notes"))

# ============================================================
# L1 边缘系统 (保留原有 + 新增皮下结构)
# ============================================================

L1_NEW_REGIONS = {
    # 苍白球 — 基底节输出核
    "苍白球": {
        "std_name": "Globus Pallidus",
        "bfb_region": "Pallidum",
        "category": "subcortical",
        "lobe": "basal_ganglia",
        "mni": [-20, -4, -4],
        "obj_file": "技能树系统/blender_assets/all_obj/subcortical/Left-Pallidum.obj",
        "notes": "基底节间接通路输出核. 抑制丘脑→抑制运动. CSTC环路关键节点"
    },
    # 尾状核
    "尾状核": {
        "std_name": "Caudate Nucleus",
        "bfb_region": "Caudate",
        "category": "subcortical",
        "lobe": "basal_ganglia",
        "mni": [-14, 8, 10],
        "obj_file": "技能树系统/blender_assets/all_obj/subcortical/Left-Caudate.obj",
        "notes": "目标导向行为的纹状体区. 联合环路(dmStr)的皮层输入区"
    },
    # 壳核
    "壳核": {
        "std_name": "Putamen",
        "bfb_region": "Putamen",
        "category": "subcortical",
        "lobe": "basal_ganglia",
        "mni": [-26, 0, 4],
        "obj_file": "技能树系统/blender_assets/all_obj/subcortical/Left-Putamen.obj",
        "notes": "感觉运动环路的纹状体区(dlStr). 习惯形成/自动执行"
    },
}

for name, info in L1_NEW_REGIONS.items():
    add_region(name, info["std_name"], info["bfb_region"],
               info["category"], info["lobe"], info["mni"],
               level=1, mni_source="literature_mni",
               obj_file=info.get("obj_file"),
               notes=info.get("notes"))

# ============================================================
# L3 初级感觉皮层 (新增缺失皮层)
# ============================================================

L3_NEW_REGIONS = {
    # M1 初级运动皮层
    "M1": {
        "std_name": "Primary Motor Cortex (M1, BA4)",
        "bfb_region": "precentral",
        "category": "cortical",
        "lobe": "frontal",
        "mni": [-37, -22, 58],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.precentral.obj",
        "notes": "运动输出的最终皮层端. 控制对侧身体运动. 皮质脊髓束起源"
    },
    # S1 初级体感皮层
    "S1": {
        "std_name": "Primary Somatosensory Cortex (S1, BA3/1/2)",
        "bfb_region": "postcentral",
        "category": "cortical",
        "lobe": "parietal",
        "mni": [-42, -26, 54],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.postcentral.obj",
        "notes": "触觉/本体感觉的初级皮层. 身体图式. 内感受的上游输入"
    },
    # A1 初级听觉皮层
    "A1": {
        "std_name": "Primary Auditory Cortex (A1, BA41, Heschl's Gyrus)",
        "bfb_region": "transversetemporal",
        "category": "cortical",
        "lobe": "temporal",
        "mni": [-42, -24, 10],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.transversetemporal.obj",
        "notes": "听觉输入的第一站皮层. 音调/频率处理. 颞横回(Heschl回)"
    },
    # 旁中央小叶
    "旁中央小叶": {
        "std_name": "Paracentral Lobule",
        "bfb_region": "paracentral",
        "category": "cortical",
        "lobe": "frontal",
        "mni": [-8, -30, 60],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.paracentral.obj",
        "notes": "下肢运动/感觉代表区. 连接M1和S1的内侧延伸"
    },
    # 楔叶 (次级视觉)
    "楔叶": {
        "std_name": "Cuneus (Secondary Visual)",
        "bfb_region": "cuneus",
        "category": "cortical",
        "lobe": "occipital",
        "mni": [-8, -80, 28],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.cuneus.obj",
        "notes": "背侧视觉通路的一部分. 空间视觉/运动检测"
    },
}

for name, info in L3_NEW_REGIONS.items():
    add_region(name, info["std_name"], info["bfb_region"],
               info["category"], info["lobe"], info["mni"],
               level=3, mni_source="literature_mni",
               obj_file=info.get("obj_file"),
               notes=info.get("notes"))

# ============================================================
# L4 高级单模态皮层 (新增)
# ============================================================

L4_NEW_REGIONS = {
    # 纺锤体回 — 面孔/精细识别
    "纺锤体回": {
        "std_name": "Fusiform Gyrus",
        "bfb_region": "fusiform",
        "category": "cortical",
        "lobe": "temporal",
        "mni": [-40, -50, -22],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.fusiform.obj",
        "notes": "面孔识别(FFA)/物体精细分类. 视觉词形区(VWFA)也在附近"
    },
    # 外侧枕叶
    "外侧枕叶": {
        "std_name": "Lateral Occipital Cortex",
        "bfb_region": "lateraloccipital",
        "category": "cortical",
        "lobe": "occipital",
        "mni": [-30, -82, 12],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.lateraloccipital.obj",
        "notes": "物体识别的关键区(LO). 腹侧视觉通路"
    },
    # 舌回
    "舌回": {
        "std_name": "Lingual Gyrus",
        "bfb_region": "lingual",
        "category": "cortical",
        "lobe": "occipital",
        "mni": [-16, -78, -6],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.lingual.obj",
        "notes": "腹侧视觉通路. 颜色/文字处理. 连接V1与纺锤体回"
    },
    # 颞中回
    "颞中回": {
        "std_name": "Middle Temporal Gyrus",
        "bfb_region": "middletemporal",
        "category": "cortical",
        "lobe": "temporal",
        "mni": [-54, -42, -6],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.middletemporal.obj",
        "notes": "运动处理(MT/MST). 语义记忆. 背侧听觉通路"
    },
    # 颞上沟岸
    "颞上沟岸": {
        "std_name": "Bank of Superior Temporal Sulcus",
        "bfb_region": "bankssts",
        "category": "cortical",
        "lobe": "temporal",
        "mni": [-52, -44, 8],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.bankssts.obj",
        "notes": "社会知觉/生物运动检测. 意图感知/心理理论的前体"
    },
}

for name, info in L4_NEW_REGIONS.items():
    add_region(name, info["std_name"], info["bfb_region"],
               info["category"], info["lobe"], info["mni"],
               level=4, mni_source="literature_mni",
               obj_file=info.get("obj_file"),
               notes=info.get("notes"))

# ============================================================
# L5 跨模态皮层 (新增)
# ============================================================

L5_NEW_REGIONS = {
    # 额上回
    "额上回": {
        "std_name": "Superior Frontal Gyrus",
        "bfb_region": "superiorfrontal",
        "category": "cortical",
        "lobe": "frontal",
        "mni": [-18, 38, 42],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.superiorfrontal.obj",
        "notes": "高级认知/自我意识/工作记忆. 包含SMA前区(pre-SMA)"
    },
    # 缘上回
    "缘上回": {
        "std_name": "Supramarginal Gyrus",
        "bfb_region": "supramarginal",
        "category": "cortical",
        "lobe": "parietal",
        "mni": [-52, -44, 32],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.supramarginal.obj",
        "notes": "语音处理/工作记忆/模仿. TPJ的组成部分. 与角回一起构成感觉-语言界面"
    },
    # 颞上回
    "颞上回": {
        "std_name": "Superior Temporal Gyrus",
        "bfb_region": "superiortemporal",
        "category": "cortical",
        "lobe": "temporal",
        "mni": [-54, -32, 8],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.superiortemporal.obj",
        "notes": "含Wernicke区后部. 听觉联合皮层. 语言理解"
    },
    # 额中回尾部 — dlPFC的一部分
    "额中回尾部": {
        "std_name": "Caudal Middle Frontal Gyrus",
        "bfb_region": "caudalmiddlefrontal",
        "category": "cortical",
        "lobe": "frontal",
        "mni": [-34, 14, 48],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.caudalmiddlefrontal.obj",
        "notes": "dlPFC后部. 工作记忆/执行控制的运动端"
    },
}

for name, info in L5_NEW_REGIONS.items():
    add_region(name, info["std_name"], info["bfb_region"],
               info["category"], info["lobe"], info["mni"],
               level=5, mni_source="literature_mni",
               obj_file=info.get("obj_file"),
               notes=info.get("notes"))

# ============================================================
# 其他新增 (小脑、丘脑本体等)
# ============================================================

OTHER_NEW = {
    # 小脑皮层
    "小脑皮层": {
        "std_name": "Cerebellar Cortex",
        "bfb_region": "Cerebellum-Cortex",
        "category": "subcortical",
        "lobe": "cerebellum",
        "mni": [-32, -58, -28],
        "obj_file": "技能树系统/blender_assets/all_obj/subcortical/Left-Cerebellum-Cortex.obj",
        "level": 0,  # 进化上古老，但在技能熟练化中是关键
        "notes": "预测/时序/自动化. 内部模型. 技能熟练化→习惯形成的关键结构"
    },
    # 丘脑本体（区别于已有的丘脑枕）
    "丘脑": {
        "std_name": "Thalamus Proper",
        "bfb_region": "Thalamus-Proper",
        "category": "subcortical",
        "lobe": "diencephalon",
        "mni": [-12, -18, 6],
        "obj_file": "技能树系统/blender_assets/all_obj/subcortical/Left-Thalamus-Proper.obj",
        "level": 1,  # 感觉中继站，连接皮层的关键枢纽
        "notes": "感觉中继/皮层间通信/CSTC环路中继. MD核=前额叶中继, 前核=海马中继"
    },
    # 海马旁回
    "海马旁回": {
        "std_name": "Parahippocampal Cortex",
        "bfb_region": "parahippocampal",
        "category": "cortical",
        "lobe": "temporal",
        "mni": [-28, -36, -18],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.parahippocampal.obj",
        "level": 1,  # 旁海马皮层，空间/情景记忆
        "notes": "空间导航/场景识别(PPA). 海马体的主要皮层输入. 内嗅皮层-海马的中继"
    },
    # 峡部扣带 (retrosplenial)
    "峡部扣带": {
        "std_name": "Isthmus Cingulate (Retrosplenial Cortex)",
        "bfb_region": "isthmuscingulate",
        "category": "cortical",
        "lobe": "cingulate",
        "mni": [-8, -46, 10],
        "obj_file": "技能树系统/blender_assets/all_obj/pial_DK/lh.pial.DK.isthmuscingulate.obj",
        "level": 2,  # 旁边缘, 记忆与空间的桥梁
        "notes": "海马-默认网络接口. 空间记忆/场景构建. Alzheimer早期萎缩区"
    },
}

for name, info in OTHER_NEW.items():
    add_region(name, info["std_name"], info["bfb_region"],
               info["category"], info["lobe"], info["mni"],
               level=info["level"], mni_source="literature_mni",
               obj_file=info.get("obj_file"),
               notes=info.get("notes"))

# ═══════════════════════════════════════════════════════════
# SECTION 3: 合并原有脑区 + 去重
# ═══════════════════════════════════════════════════════════

def merge_existing_regions(existing_path):
    """加载原有脑区并合并到 ALL_REGIONS"""
    with open(existing_path, "r", encoding="utf-8") as f:
        existing = json.load(f)

    kept = 0
    skipped_dup = 0
    existing_regions = existing.get("regions", {})

    # 去重: BNST和终纹床核是同一个结构
    # 保留 BNST, 删除 终纹床核
    if "终纹床核" in existing_regions and "BNST" in existing_regions:
        del existing_regions["终纹床核"]
        skipped_dup += 1

    # 伏隔核/NAcc 与 NAcc壳/NAcc核 — 保留3个但标记子区域关系
    # 腹侧纹状体 与 NAcc 重叠 — 保留腹侧纹状体, 标记为上级结构

    for name, info in existing_regions.items():
        if name in ALL_REGIONS:
            # 已在新定义中存在，跳过（新定义覆盖）
            skipped_dup += 1
            continue

        # 添加层级信息到原有脑区
        # 按类别推断层级
        cat = info.get("category", "")
        if cat == "brainstem":
            level = 0
        elif cat == "subcortical":
            level = 1
        elif cat == "cortical":
            lobe = info.get("lobe", "")
            if lobe in ("occipital",):
                level = 3
            elif lobe in ("parietal", "temporal"):
                level = 4
            elif lobe in ("frontal", "cingulate", "insula", "temporo-parietal"):
                level = 5
            elif lobe in ("parieto-occipital",):
                level = 3
            else:
                level = 4
        elif cat == "white_matter":
            level = 5  # 白质通路连接高级区
        else:
            level = 3

        info["level"] = level
        ALL_REGIONS[name] = info
        kept += 1

    print(f"  原有脑区: 保留 {kept} 个, 跳过(重复/去重) {skipped_dup} 个")
    return kept, skipped_dup

# ═══════════════════════════════════════════════════════════
# SECTION 4: 输出
# ═══════════════════════════════════════════════════════════

def generate(output_path):
    """生成完整的 brain_regions.json"""

    # 统计
    from collections import Counter
    level_count = Counter(r["level"] for r in ALL_REGIONS.values())
    cat_count = Counter(r["category"] for r in ALL_REGIONS.values())

    output = {
        "_description": "完整脑功能层级图谱 — L0脑干反射→L5跨模态认知",
        "_source": "brain-for-blender (brainder.org, CC BY-SA 3.0), Hansen et al. (2024) Nat Neurosci, MNI152, Harvard-Oxford, AAL3, literature",
        "_created": "2026-07-11",
        "_updated": "2026-07-12 — 扩展: 脑干核团(方案A文献坐标) + 皮下全结构 + DK皮层补全",
        "_methodology": {
            "brainstem_nuclei": "方案A: 文献MNI坐标 (Hansen2024, Paxinos&Mai2004). 无独立OBJ, 坐标点落在Brain-Stem.obj体积内",
            "cortical_regions": "FreeSurfer Desikan-Killiany atlas OBJ质心",
            "subcortical": "brain-for-blender subcortical/ OBJ质心",
        },
        "_coordinate_system": {
            "mni": "MNI152 (mm, RAS+): X=右, Y=前, Z=上",
            "game": "游戏世界空间: X=右, Y=上, Z=前",
            "bounds": "X∈[-1.1,+1.1], Y∈[0,1.1], Z∈[-0.8,+0.9]",
            "transform": "game_X=mni_X/90; game_Y=mni_Z/90+0.55; game_Z=mni_Y/126*0.85",
        },
        "_functional_levels": {
            "L0": "脑干反射 — 生存原子操作, ~10-30ms, 最强制/不可抑制",
            "L1": "边缘系统 — 核心情绪与记忆, ~20-80ms, 经验依赖调制L0",
            "L2": "旁边缘 — 内感受与突显, ~50-120ms, 决定'什么值得关注'",
            "L3": "初级感觉皮层 — 原始外部输入, ~30-80ms, 被动接收",
            "L4": "高级单模态 — 模式识别与分类, ~80-150ms, 给世界贴标签",
            "L5": "跨模态皮层 — 认知与语言, ~150-300ms, 多模态整合与推理；原L6整合层（自我叙事/全脑协调/裁决）并入（2026-08-07 Grilling #25）",
        },
        "_stats": {
            "total_regions": len(ALL_REGIONS),
            "by_level": {f"L{k}": v for k, v in sorted(level_count.items())},
            "by_category": dict(cat_count),
        },
        "regions": dict(sorted(ALL_REGIONS.items())),
    }

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # 备份旧文件
    if os.path.exists(output_path):
        backup = output_path.replace(".json", f"_backup_{output['_updated'].replace('-','').replace(' ','_')[:10]}.json")
        import shutil
        shutil.copy2(output_path, backup)
        print(f"  已备份旧文件 → {backup}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 已生成 {output_path}")
    print(f"   总脑区: {len(ALL_REGIONS)}")
    print(f"   按层级: {dict(sorted(level_count.items()))}")
    print(f"   按类别: {dict(cat_count)}")

    return output

# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    existing_path = "data/brain_regions.json"
    output_path = "data/brain_regions.json"

    print("=" * 60)
    print("🧠 扩展脑区图谱: 59区 → 全脑功能层级模型")
    print("=" * 60)

    # 统计新定义的区域
    new_count = len(ALL_REGIONS)
    print(f"\n新增区域: {new_count}")
    for name in sorted(ALL_REGIONS.keys()):
        info = ALL_REGIONS[name]
        print(f"  [{info['level']}] {name:15s} | {info['category']:12s} | {info['lobe']:15s} | {info['mni_xyz']}")

    # 合并原有
    print(f"\n合并原有脑区...")
    kept, skipped = merge_existing_regions(existing_path)

    # 输出
    generate(output_path)
    print(f"\n下一步: 用 tools/map_skills_to_regions.py 重新映射技能坐标")
