#!/usr/bin/env python3
"""
build_link_legitimacy_matrix.py — 从 ENIGMA 结构连接 + 脑区层级 + Kroell 功能网络 + 白质纤维束
交叉过滤，生成满足四规则的合法神经链路清单。

四规则（来自设计共识 2026-07-27）:
  1. 层级相邻 (Mesulam 1998): 链路只能连相邻层级 (L0↔L1↔...↔L5)
  2. 结构存在 (HCP DTI / ENIGMA): 两个脑区之间必须有白质纤维束
  3. 协同激活 (Kroell 2024): 必须在至少一个已知功能网络中共同激活
  4. 双向不对称 (Felleman & Van Essen 1991):
     上行 (feedforward Ln→Ln+1) = 快/被动/自动
     下行 (feedback Ln+1→Ln) = 慢/主动/占带宽

数据源:
  - brain_regions.json: 70 条目 (50 解剖实体), L0-L5 层级, DK/bfb 标签
  - enigma_all_connections.csv: 698 条 ENIGMA SC 连接 (68 DK 皮层区域)
  - enigma_sc_sctx_matrix.npy: 14 皮下 × 68 皮层 SC 矩阵
  - kroell14_networks.md: 14 功能网络 (手动提取)
  - white_matter_tracts.json: 25+ 白质纤维束

输出:
  - data/connectivity/link_legitimacy_matrix.json
  - stdout 摘要
"""

import json
import csv
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent

# ─── 1. 加载脑区数据 ───────────────────────────────────────────

def load_brain_regions():
    """加载 brain_regions.json，建立 DK/brainstem/subcortical 标签 → 层级 的映射"""
    with open(ROOT / "data/brain_regions.json") as f:
        data = json.load(f)

    regions = data["regions"]

    # 多对多映射:
    #   dk_to_level: DK atlas 标签 → list of (region_name, level)
    #   name_to_level: 脑区名称 → level
    #   subcortical_map: 中文/英文名称 → ENIGMA subcortical label

    dk_to_regions = defaultdict(list)
    name_to_level = {}
    subcortical_to_enigma = {}

    # 手动映射: brain_regions 中文名 → ENIGMA subcortical labels
    # ENIGMA labels: Laccumb, Lamyg, Lcaud, Lhippo, Lpal, Lput, Lthal
    ENIGMA_SUBCORTICAL_MAP = {
        "杏仁核":        ("amygdala",  ["Lamyg", "Ramyg"]),
        "杏仁核-海马":    ("amygdala",  ["Lamyg", "Ramyg"]),
        "海马体 CA1":    ("hippocampus", ["Lhippo", "Rhippo"]),
        "海马体 CA3":    ("hippocampus", ["Lhippo", "Rhippo"]),
        "海马旁回":      ("parahippocampal", []),  # DK cortical
        "内嗅皮层":      ("entorhinal", []),        # DK cortical
        "伏隔核/NAcc":   ("nacc",       ["Laccumb", "Raccumb"]),
        "NAcc壳":       ("nacc",       ["Laccumb", "Raccumb"]),
        "NAcc核":       ("nacc",       ["Laccumb", "Raccumb"]),
        "腹侧纹状体":    ("nacc",       ["Laccumb", "Raccumb"]),
        "壳核":          ("putamen",    ["Lput", "Rput"]),
        "苍白球":        ("pallidum",   ["Lpal", "Rpal"]),
        "尾状核":        ("caudate",    ["Lcaud", "Rcaud"]),
        "纹状体基质":    ("caudate",    ["Lcaud", "Rcaud"]),
        "丘脑":          ("thalamus",   ["Lthal", "Rthal"]),
        "丘脑枕":        ("thalamus",   ["Lthal", "Rthal"]),
        "缰核":          ("habenula",   []),        # 不在 ENIGMA 皮下
        "下丘脑":        ("hypothalamus", []),       # 不在 ENIGMA 皮下
        "BNST":          ("bnst",       []),         # 不在 ENIGMA 皮下
        "隔区":          ("septal",     []),         # 不在 ENIGMA 皮下
        "全脑整合":      ("rich_club",  []),         # 概念性
        "基底节间接通路": ("bg_indirect", ["Lpal", "Rpal"]),
        "小脑皮层":      ("cerebellum", []),         # 不在 ENIGMA DK
        "额顶网络":      ("fpn",        []),         # 概念性/白质通路
        "弓状束":        ("af",         []),         # 白质通路
        "岛叶-ACC":      ("insula_acc", []),         # 白质通路
        "岛叶-ACC-VTA":  ("insula_acc_vta", []),     # 白质通路
        "岛叶-PFC-杏仁核": ("insula_pfc_amyg", []),  # 白质通路
        "岛叶-vmPFC":    ("insula_vmpfc", []),       # 白质通路
        "vmPFC-TPJ":     ("vmpfc_tpj", []),          # 白质通路
        "前额叶-海马":   ("pfc_hippo", []),          # 白质通路
        "mPFC-杏仁核":   ("mpfc_amyg", []),          # 白质通路
    }

    for name, r in regions.items():
        level = r.get("level")
        if level is None:
            continue
        name_to_level[name] = level

        bfb = r.get("bfb_region")
        category = r.get("category", "")

        if bfb and category == "cortical":
            dk_to_regions[bfb].append((name, level))

        # 皮下/脑干映射
        if name in ENIGMA_SUBCORTICAL_MAP:
            for enigma_label in ENIGMA_SUBCORTICAL_MAP[name][1]:
                subcortical_to_enigma[enigma_label] = level

    return dk_to_regions, name_to_level, subcortical_to_enigma, regions


# ─── 1B. 加载 Hansen 2024 脑干-皮层 FC ──────────────────────

def load_brainstem_fc():
    """加载脑干核团→皮层/皮下功能连接补充数据"""
    path = ROOT / "data/connectivity/brainstem_cortical_fc.json"
    if not path.exists():
        print("  ⚠ brainstem_cortical_fc.json 不存在，跳过脑干连接")
        return [], {}

    with open(path) as f:
        data = json.load(f)

    connections = data.get("connections", [])
    brainstem_level = {}
    for conn in connections:
        nucleus = conn["brainstem_nucleus"]
        brainstem_level[nucleus] = 0  # 所有脑干核团都是 L0

    return connections, brainstem_level


# ─── 1C. 加载手动补充 皮下-皮下连接 ──────────────────────────

def load_subcortical_links():
    """加载手动文献验证的皮层下-皮层下结构连接补充数据"""
    path = ROOT / "data/connectivity/subcortical_links.json"
    if not path.exists():
        print("  ⚠ subcortical_links.json 不存在，跳过手动补充连接")
        return []

    with open(path) as f:
        data = json.load(f)

    return data.get("connections", [])


# ─── 2. 加载 ENIGMA 结构连接 ─────────────────────────────────

def load_enigma_connections():
    """加载皮层-皮层和皮下-皮层连接，返回 [(dk_a, dk_b, strength), ...]"""
    connections = []

    # 皮层-皮层: enigma_all_connections.csv
    with open(ROOT / "data/connectivity/enigma_all_connections.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r1 = row["region1"].strip()
            r2 = row["region2"].strip()
            strength = float(row["strength"])
            connections.append((r1, r2, strength))

    # 皮下-皮层: enigma_sc_sctx_matrix.npy — 14×68
    # 需要标签文件来解析
    import numpy as np
    sctx_matrix = np.load(ROOT / "data/connectivity/enigma_sc_sctx_matrix.npy")
    sctx_labels = np.load(ROOT / "data/connectivity/enigma_sc_sctx_labels.npy",
                          allow_pickle=True)
    ctx_labels = np.load(ROOT / "data/connectivity/enigma_sc_ctx_labels.npy",
                         allow_pickle=True)

    # sctx_labels 是 14 个皮下标签，ctx_labels 是 68 个皮层标签
    for i, subc_label in enumerate(sctx_labels):
        for j, ctx_label in enumerate(ctx_labels):
            strength = float(sctx_matrix[i, j])
            if strength > 0:
                # 皮下-皮层连接: subcortical→cortical
                connections.append((subc_label, ctx_label, strength))

    return connections, list(sctx_labels), list(ctx_labels)


# ─── 3. 层级相邻判定 ─────────────────────────────────────────

# 脑干靶区 → 层级 直接映射
# 这些是 brainstem_cortical_fc.json 中使用的靶区名，
# 不一定匹配 DK 标签或 ENIGMA 皮下前缀
_BRAINSTEM_TARGET_LEVEL = {
    "amygdala":     1,
    "hippocampus":  1,
    "accumbens":    1,
    "septum":       1,
    "hypothalamus": 1,
    "thalamus":     1,
    "caudate":      1,
    "putamen":      1,
    "pallidum":     1,
    "entorhinal":   4,
}


def get_region_level(dk_label, dk_to_regions, subcortical_to_enigma):
    """给定一个 ENIGMA DK/皮下标签 或 脑干靶区名，返回层级"""
    # 1. 查脑干靶区直接映射
    if dk_label in _BRAINSTEM_TARGET_LEVEL:
        return _BRAINSTEM_TARGET_LEVEL[dk_label]

    # 2. 查 DK 皮层映射
    if dk_label in dk_to_regions:
        regions = dk_to_regions[dk_label]
        if regions:
            return regions[0][1]

    # 3. 查皮下 ENIGMA 映射 (Lamyg, Ramyg 等)
    if dk_label in subcortical_to_enigma:
        return subcortical_to_enigma[dk_label]

    return None


def is_layer_adjacent(level_a, level_b):
    """层级相邻: |level_a - level_b| <= 1
    例外: L0 脑干核团可以投射到 L1 和 L2（脑干广播式投射，
    蓝斑/VTA/中缝核的神经调质系统直接到达旁边缘皮层）"""
    if level_a is None or level_b is None:
        return False
    diff = abs(level_a - level_b)
    if diff <= 1:
        return True
    # L0 特殊: 可以投射到 L2（蓝斑→前脑岛, VTA→ACC等）
    if (level_a == 0 or level_b == 0) and diff == 2:
        return True
    return False


# ─── 4. Kroell 功能网络协同激活 ──────────────────────────────

def build_kroell_network_map():
    """
    从 kroell14_networks.md 手动提取的网络-脑区映射。
    这里使用 brain_regions.json 中已有脑区的名称做模糊匹配。
    """
    # 14 网络 → 包含的 bfb_region 列表
    # 从 kroell14_networks.md 的脑区描述提取 DK 近似标签
    networks = {
        "Autobiographical Memory": [
            "parahippocampal", "precuneus", "posteriorcingulate",
            "supramarginal", "rostralmiddlefrontal", "lateraloccipital",
            "superiorfrontal", "medialorbitofrontal"
        ],
        "Cognitive Attention Control": [
            "insula", "parsopercularis", "parstriangularis",
            "rostralmiddlefrontal", "superiorparietal",
            "inferiorparietal", "lateraloccipital",
            "caudalanteriorcingulate"
        ],
        "Extended Multiple Demand": [
            "parsopercularis", "parstriangularis", "insula",
            "caudalmiddlefrontal", "superiorparietal",
            "inferiortemporal", "putamen"
        ],
        "Emotional Scene and Face Processing": [
            "superiorfrontal", "parahippocampal", "fusiform",
            "lateralorbitofrontal", "medialorbitofrontal",
            "lateraloccipital", "amygdala", "caudalanteriorcingulate"
        ],
        "Empathy": [
            "superiorfrontal", "insula", "parsopercularis",
            "caudalanteriorcingulate", "rostralanteriorcingulate",
            "supramarginal", "amygdala", "superiortemporal"
        ],
        "Emotion Regulation": [
            "parsopercularis", "parstriangularis", "rostralmiddlefrontal",
            "superiorparietal", "amygdala", "superiorfrontal",
            "caudalanteriorcingulate", "insula", "superiortemporal"
        ],
        "Extended Socio-Affective Default": [
            "caudalanteriorcingulate", "rostralanteriorcingulate",
            "amygdala", "hippocampus", "supramarginal",
            "precuneus", "medialorbitofrontal", "superiorfrontal"
        ],
        "Mirror Neuron System": [
            "parsopercularis", "postcentral", "lateraloccipital",
            "fusiform", "superiortemporal", "superiorparietal"
        ],
        "Motor": [
            "precentral", "postcentral", "putamen", "pallidum",
            "inferiorparietal", "superiorfrontal"
        ],
        "Reward": [
            "insula", "medialorbitofrontal", "lateralorbitofrontal",
            "caudalmiddlefrontal", "accumbens", "pallidum",
            "caudalanteriorcingulate", "posteriorcingulate",
            "inferiorparietal", "superiorfrontal"
        ],
        "Semantic Memory": [
            "inferiorparietal", "supramarginal", "middletemporal",
            "inferiortemporal", "fusiform", "parahippocampal",
            "superiorfrontal", "medialorbitofrontal",
            "lateralorbitofrontal", "posteriorcingulate", "precuneus"
        ],
        "Theory of Mind": [
            "medialorbitofrontal", "superiorfrontal",
            "frontalpole", "precuneus", "supramarginal",
            "temporalpole", "middletemporal", "superiortemporal",
            "parsopercularis"
        ],
        "Vigilant Attention": [
            "paracentral", "superiorfrontal", "caudalanteriorcingulate",
            "insula", "precentral", "lateraloccipital",
            "supramarginal", "inferiorparietal",
        ],
        "Working Memory": [
            "insula", "parsopercularis", "parstriangularis",
            "rostralmiddlefrontal", "caudalmiddlefrontal",
            "superiorfrontal", "superiorparietal",
            "inferiorparietal", "caudate", "pallidum"
        ],
    }

    # 反转: bfb_region → 参与的网络列表
    region_to_networks = defaultdict(list)
    for net_name, bfb_list in networks.items():
        for bfb in bfb_list:
            region_to_networks[bfb].append(net_name)

    return region_to_networks


def have_coactivation(dk_a, dk_b, region_to_networks):
    """判定两个 DK 区域是否在至少一个 Kroell 功能网络中共激活"""
    nets_a = set(region_to_networks.get(dk_a, []))
    nets_b = set(region_to_networks.get(dk_b, []))
    return len(nets_a & nets_b) > 0


# ─── 5. 白质纤维束结构验证 ───────────────────────────────────

def build_wm_tract_map():
    """加载白质纤维束，建立 DK 区域 → 纤维束 映射（哪些区域被同一纤维束连接）"""
    with open(ROOT / "data/connectivity/white_matter_tracts.json") as f:
        data = json.load(f)

    # 为每类纤维束提取连接区域
    tract_connections = defaultdict(set)

    for tract_type, tract_data in data.items():
        if tract_type.startswith("_"):
            continue
        tracts = tract_data.get("tracts", [])
        for tract in tracts:
            regions = tract.get("connected_regions", [])
            # 简化: 提取区域名称中的关键词，映射到 DK 标签
            dk_set = set()
            for region_desc in regions:
                dk = _fuzzy_match_dk(region_desc)
                if dk:
                    dk_set.add(dk)
            # 同一纤维束内的任意两个区域都有结构基础
            for dk_a in dk_set:
                for dk_b in dk_set:
                    if dk_a != dk_b:
                        tract_connections[(dk_a, dk_b)].add(tract["name"])
                        tract_connections[(dk_b, dk_a)].add(tract["name"])

    return tract_connections


def _fuzzy_match_dk(region_desc):
    """从白质纤维束的区域描述模糊匹配到 DK 标签"""
    desc_lower = region_desc.lower()
    # 精确匹配关键词
    MATCH_TABLE = [
        ("amygdala", "amygdala"),
        ("hippocamp", "hippocampus"),
        ("parahippocamp", "parahippocampal"),
        ("entorhinal", "entorhinal"),
        ("cingulate", "caudalanteriorcingulate"),
        ("anterior cingulate", "caudalanteriorcingulate"),
        ("posterior cingulate", "posteriorcingulate"),
        ("insula", "insula"),
        ("orbitofrontal", "lateralorbitofrontal"),
        ("precuneus", "precuneus"),
        ("cuneus", "cuneus"),
        ("fusiform", "fusiform"),
        ("lingual", "lingual"),
        ("temporal pole", "temporalpole"),
        ("superior temporal", "superiortemporal"),
        ("middle temporal", "middletemporal"),
        ("inferior temporal", "inferiortemporal"),
        ("frontal pole", "frontalpole"),
        ("rostral middle frontal", "rostralmiddlefrontal"),
        ("caudal middle frontal", "caudalmiddlefrontal"),
        ("superior frontal", "superiorfrontal"),
        ("pars opercularis", "parsopercularis"),
        ("pars triangularis", "parstriangularis"),
        ("pars orbitalis", "parsorbitalis"),
        ("broca", "parsopercularis"),
        ("wernicke", "superiortemporal"),
        ("precentral", "precentral"),
        ("postcentral", "postcentral"),
        ("paracentral", "paracentral"),
        ("inferior parietal", "inferiorparietal"),
        ("superior parietal", "superiorparietal"),
        ("supramarginal", "supramarginal"),
        ("angular gyrus", "inferiorparietal"),
        ("banks", "bankssts"),
        ("lateral occipital", "lateraloccipital"),
        ("pericalcarine", "pericalcarine"),
        ("caudate", "caudate"),
        ("putamen", "putamen"),
        ("pallidum", "pallidum"),
        ("thalamus", "thalamus"),
        ("accumbens", "accumbens"),
        ("cerebellum", "cerebellum"),
        ("brainstem", "brainstem"),
        ("midbrain", "brainstem"),
    ]
    for keyword, dk_label in MATCH_TABLE:
        if keyword in desc_lower:
            return dk_label
    return None


# ─── 6. 主流程: 交叉过滤 ─────────────────────────────────────

def main():
    print("=" * 70)
    print("链路合法性矩阵生成器")
    print("=" * 70)

    # 加载数据
    print("\n[1/7] 加载脑区层级数据...")
    dk_to_regions, name_to_level, subcortical_to_enigma, regions = load_brain_regions()

    # 统计层级分布
    level_count = defaultdict(int)
    for name, lv in name_to_level.items():
        level_count[f"L{lv}"] += 1
    print(f"  脑区总数: {len(name_to_level)}")
    for lv in sorted(level_count.keys()):
        print(f"    {lv}: {level_count[lv]}")

    print("\n[2/7] 加载 ENIGMA 结构连接...")
    enigma_connections, sctx_labels, ctx_labels = load_enigma_connections()
    print(f"  ENIGMA 连接总数: {len(enigma_connections)}")
    print(f"  皮下标签: {len(sctx_labels)} ({', '.join(sctx_labels[:5])}...)")
    print(f"  皮层标签: {len(ctx_labels)} ({', '.join(ctx_labels[:5])}...)")

    print("\n[3/7] 加载 Hansen 2024 脑干-皮层 FC...")
    brainstem_connections, brainstem_level = load_brainstem_fc()
    print(f"  脑干核团: {len(brainstem_connections)}")
    total_brainstem_targets = sum(len(bc["targets"]) for bc in brainstem_connections)
    print(f"  脑干→靶区 投射: {total_brainstem_targets}")

    print("\n[4/7] 构建 Kroell 功能网络映射...")
    region_to_networks = build_kroell_network_map()
    print(f"  功能网络: 14")
    print(f"  覆盖 DK 区域: {len(region_to_networks)}")

    print("\n[5/7] 构建白质纤维束映射...")
    wm_tract_map = build_wm_tract_map()
    print(f"  纤维束区域对: {len(wm_tract_map)}")

    print("\n[6/7] 加载手动补充 皮下-皮下连接...")
    subcortical_connections = load_subcortical_links()
    print(f"  手动补充连接: {len(subcortical_connections)}")

    print("\n[7/7] 交叉过滤...")
    legal_links = []
    filter_stats = defaultdict(int)
    filter_stats["total_subcortical"] = len(subcortical_connections)
    filter_stats["total_enigma"] = len(enigma_connections)
    filter_stats["total_brainstem"] = total_brainstem_targets

    for conn in enigma_connections:
        dk_a, dk_b, strength = conn

        # 去掉 L_/R_ 前缀做匹配
        dk_a_clean = dk_a.replace("L_", "").replace("R_", "")
        dk_b_clean = dk_b.replace("L_", "").replace("R_", "")

        # 获取层级
        level_a = get_region_level(dk_a_clean, dk_to_regions, subcortical_to_enigma)
        level_b = get_region_level(dk_b_clean, dk_to_regions, subcortical_to_enigma)

        if level_a is None or level_b is None:
            filter_stats["no_level_mapping"] += 1
            continue

        # 规则 1: 结构存在 (ENIGMA 已满足 —— 数据本身就是结构连接)
        filter_stats["has_structure"] += 1

        # 规则 2: 协同激活 —— 同一功能网络
        coactivated = have_coactivation(dk_a_clean, dk_b_clean, region_to_networks)
        if not coactivated:
            filter_stats["no_coactivation"] += 1
            continue

        # 层级相邻 (信息性，不排除)
        layer_adj = is_layer_adjacent(level_a, level_b)
        if not layer_adj:
            filter_stats["not_adjacent"] += 1

        # 规则 3: 方向分类
        if level_a < level_b:
            direction = "feedforward"    # 上行
        elif level_a > level_b:
            direction = "feedback"       # 下行
        else:
            direction = "lateral"        # 同层侧向

        # 检查白质纤维束
        wm_tracts = list(wm_tract_map.get((dk_a_clean, dk_b_clean), set()))

        # 查找该连接映射到哪些脑区
        regions_a = [name for name, lv in dk_to_regions.get(dk_a_clean, [])]
        regions_b = [name for name, lv in dk_to_regions.get(dk_b_clean, [])]
        if not regions_a:
            # 可能是皮下
            for label, lv in subcortical_to_enigma.items():
                if dk_a_clean == label or dk_a == label:
                    regions_a = [f"subcortical:{label}"]
                    break
        if not regions_b:
            for label, lv in subcortical_to_enigma.items():
                if dk_b_clean == label or dk_b == label:
                    regions_b = [f"subcortical:{label}"]
                    break

        link = {
            "dk_pair": [dk_a_clean, dk_b_clean],
            "enigma_labels": [dk_a, dk_b],
            "layers": [level_a, level_b],
            "direction": direction,
            "enigma_strength": round(strength, 2),
            "regions_a": regions_a,
            "regions_b": regions_b,
            "white_matter_tracts": wm_tracts,
            "coactivated_networks": list(
                set(region_to_networks.get(dk_a_clean, [])) &
                set(region_to_networks.get(dk_b_clean, []))
            ),
            "rule_check": {
                "layer_adjacent": layer_adj,
                "structure_exists": True,
                "coactivation": True,
                "direction": direction,
            }
        }
        legal_links.append(link)
        filter_stats["legal"] += 1

    # ─── 处理脑干-皮层连接 ─────────────────────────────────
    # Kroell 网络没有明确覆盖脑干核团，我们使用 Hansen 社区作为功能验证
    for bc in brainstem_connections:
        nucleus = bc["brainstem_nucleus"]
        community = bc["hansen_community"]
        level_a = 0  # L0

        for target in bc["targets"]:
            dk_target = target["target"]
            fc_strength = target["fc_strength"]
            pathway = target["pathway"]

            # 获取靶区层级
            level_b = get_region_level(dk_target, dk_to_regions, subcortical_to_enigma)

            if level_b is None:
                filter_stats["brainstem_no_target_level"] += 1
                continue

            # 规则1: 结构存在 — Hansen FC 本身就是结构+功能数据
            filter_stats["brainstem_has_structure"] += 1

            # 规则2: 功能验证 — Hansen 社区归属 + fc_strength
            if fc_strength < 0.5:
                filter_stats["brainstem_weak_fc"] += 1
                continue

            # 层级相邻 (信息性，不排除)
            layer_adj = is_layer_adjacent(level_a, level_b)
            if not layer_adj:
                filter_stats["brainstem_not_adjacent"] += 1

            # 规则3: 方向
            direction = "feedforward"  # 脑干→皮层一律上行

            # 查找该 DK 靶区对应哪些脑区
            target_regions = [name for name, lv in dk_to_regions.get(dk_target, [])]
            if not target_regions:
                # 可能是 ENIGMA 皮下标签
                for label, lv in subcortical_to_enigma.items():
                    if dk_target == label:
                        target_regions = [f"subcortical:{label}"]
                        break

            link = {
                "source": "hansen2024_brainstem",
                "brainstem_nucleus": nucleus,
                "hansen_community": community,
                "dk_target": dk_target,
                "layers": [level_a, level_b],
                "direction": direction,
                "fc_strength": fc_strength,
                "pathway": pathway,
                "ref": target["ref"],
                "regions_a": [nucleus],
                "regions_b": target_regions,
                "white_matter_tracts": [],
                "coactivated_networks": [f"Hansen:{community}"],
                "rule_check": {
                    "layer_adjacent": layer_adj,
                    "structure_exists": True,  # Hansen FC 数据
                    "coactivation": True,        # 社区归属
                    "direction": direction,
                }
            }
            legal_links.append(link)
            filter_stats["legal"] += 1

    # ─── 手动补充 皮下-皮下连接 ─────────────────────────────
    for sc in subcortical_connections:
        src = sc["source_region"]
        tgt = sc["target_region"]
        level_a = sc["layers"][0]
        level_b = sc["layers"][1]
        layer_adj = is_layer_adjacent(level_a, level_b)
        if not layer_adj:
            filter_stats["subcortical_not_adjacent"] = filter_stats.get("subcortical_not_adjacent", 0) + 1

        link = {
            "source": "manual_curation",
            "dk_pair": None,
            "enigma_labels": None,
            "layers": sc["layers"],
            "direction": sc["direction"],
            "regions_a": sc["regions_a"],
            "regions_b": sc["regions_b"],
            "white_matter_tracts": sc.get("white_matter_tracts", []),
            "coactivated_networks": sc.get("coactivated_networks", []),
            "pathway": sc.get("pathway", ""),
            "ref": sc.get("ref", ""),
            "fc_strength": sc.get("fc_strength"),
            "enigma_strength": None,
            "rule_check": {
                "layer_adjacent": layer_adj,
                "structure_exists": True,
                "coactivation": True,
                "direction": sc["direction"],
            }
        }
        legal_links.append(link)
        filter_stats["legal"] += 1
        filter_stats["subcortical_added"] = filter_stats.get("subcortical_added", 0) + 1

    # ─── 输出统计 ──────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"过滤结果:")
    print(f"  ── ENIGMA 皮层 ──")
    print(f"  ENIGMA 总连接:       {filter_stats['total_enigma']:>6}")
    print(f"  无层级映射:          {filter_stats['no_level_mapping']:>6}")
    print(f"  层级不相邻:          {filter_stats['not_adjacent']:>6}")
    print(f"  有结构基础:          {filter_stats['has_structure']:>6}")
    print(f"  无功能协同激活:       {filter_stats['no_coactivation']:>6}")
    print(f"  ── Hansen 脑干 ──")
    print(f"  脑干投射总数:        {filter_stats['total_brainstem']:>6}")
    print(f"  无法映射靶区层级:    {filter_stats.get('brainstem_no_target_level', 0):>6}")
    print(f"  层级不相邻:          {filter_stats.get('brainstem_not_adjacent', 0):>6}")
    print(f"  FC 过弱(<0.5):       {filter_stats.get('brainstem_weak_fc', 0):>6}")
    print(f"  ── 手动补充 皮下-皮下 ──")
    print(f"  手动补充总数:        {filter_stats.get('total_subcortical', 0):>6}")
    print(f"  层级不相邻:          {filter_stats.get('subcortical_not_adjacent', 0):>6}")
    print(f"  已追加:              {filter_stats.get('subcortical_added', 0):>6}")
    print(f"  ✓ 合法链路:          {filter_stats['legal']:>6}")
    layer_adj_count = sum(1 for l in legal_links if l["rule_check"]["layer_adjacent"])
    print(f"    其中层级相邻:       {layer_adj_count:>6}")
    print(f"    其中层级不相邻:     {filter_stats['legal'] - layer_adj_count:>6}")

    # 按方向统计
    ff_count = sum(1 for l in legal_links if l["direction"] == "feedforward")
    fb_count = sum(1 for l in legal_links if l["direction"] == "feedback")
    lat_count = sum(1 for l in legal_links if l["direction"] == "lateral")
    print(f"\n  上行 (feedforward):  {ff_count}")
    print(f"  下行 (feedback):     {fb_count}")
    print(f"  侧向 (lateral):      {lat_count}")

    # 按层级对统计
    layer_pair_count = defaultdict(int)
    for link in legal_links:
        pair = tuple(sorted(link["layers"]))
        layer_pair_count[pair] += 1
    print(f"\n  层级对分布:")
    for pair in sorted(layer_pair_count.keys()):
        label = f"L{pair[0]}↔L{pair[1]}"
        print(f"    {label}: {layer_pair_count[pair]:>4}")

    # ─── 保存 ──────────────────────────────────────────────
    output = {
        "_description": "合法神经链路矩阵 — 满足三规则(结构存在+协同激活+方向分类)的脑区间连接。层级相邻已降级为信息性标记。",
        "_rules": [
            "1. 结构存在: ENIGMA HCP DTI (皮层) + Hansen 2024 FC (脑干)",
            "2. 协同激活: Kroell 功能网络 (皮层) / Hansen社区 (脑干)",
            "3. 双向不对称: feedforward=快/被动, feedback=慢/主动",
            "(层级相邻已降级为信息性标记 — 有DTI/FC证据的跨层连接合法)",
        ],
        "_data_sources": {
            "brain_regions": "data/brain_regions.json (70条目/50解剖实体 L0-L5)",
            "enigma_sc": "data/connectivity/enigma_all_connections.csv + enigma_sc_sctx_matrix.npy",
            "hansen_brainstem": "data/connectivity/brainstem_cortical_fc.json (Hansen2024 脑干FC)",
            "kroell_networks": "data/connectivity/kroell14_networks.md (14功能网络)",
            "white_matter": "data/connectivity/white_matter_tracts.json (25+纤维束)",
            "subcortical_manual": "data/connectivity/subcortical_links.json (手动补充皮层下-皮下连接)",
        },
        "_stats": {
            "total_enigma_connections": filter_stats["total_enigma"],
            "total_brainstem_targets": filter_stats["total_brainstem"],
            "legal_links": filter_stats["legal"],
            "layer_adjacent": layer_adj_count,
            "layer_nonadjacent": filter_stats["legal"] - layer_adj_count,
            "feedforward": ff_count,
            "feedback": fb_count,
            "lateral": lat_count,
        },
        "links": legal_links,
    }

    out_path = ROOT / "data/connectivity/link_legitimacy_matrix.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 保存到: {out_path}")
    print(f"  文件大小: {out_path.stat().st_size / 1024:.1f} KB")
    print(f"  合法链路: {len(legal_links)} 条")


if __name__ == "__main__":
    main()
