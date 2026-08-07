#!/usr/bin/env python3
"""
build_tripartite_model.py — 三体神经模型生成器

替代旧 build_link_legitimacy_matrix.py（364 链路 pairwise 有向模型）。
生成三种通信原语：
  1. CSTC 环路 —— 门控决策（GO/NO-GO/STOP），闭环去抑制
  2. 皮层-皮层连接 —— 信息传递，EDR + 层级 + 双向互惠 + 功能标签四层筛选
  3. 脑干广播 —— 全局状态调制，弥漫投射非点对点

数据源:
  - data/brain_regions.json: 69 functional_id (50 dk_name + STN), 含 function_profile
  - data/signal_types.json: 4 大类 × 19 子类信号类型受控词表

输出:
  - data/connectivity/tripartite_model.json

设计依据: Grilling #26 (GitHub #27) — 三体神经模型，16 项决策
  规则/技能树系统/脑功能层级模型.md §二十
"""

import json
import math
import sys
from pathlib import Path
from collections import defaultdict
from itertools import combinations

ROOT = Path(__file__).resolve().parent.parent

# ─── 常量 ───────────────────────────────────────────────────────

# EDR 参数 (Molnár et al. 2024)
EDR_C = 0.85        # 截距——零距离连接概率
EDR_LAMBDA = 0.015  # 衰减率 (mm⁻¹)
EDR_THRESHOLD = 0.10  # 解剖天花板——p≥0.10 即放行 (D11)

# CSTC 环路定义 (D2, D3)
CSTC_LOOPS = ["somatic", "cognitive", "limbic"]
CSTC_STATION_ORDER = ["cortical_input", "striatal_gate", "pallidal_output", "thalamic_relay"]
CSTC_PATHWAYS = {
    ("cortical_input", "striatal_gate"): "go_direct",       # 皮层→纹状体 (D1 GO 通路开始)
    ("striatal_gate", "pallidal_output"): "go_direct",      # 纹状体→苍白球 (GO)
    ("pallidal_output", "thalamic_relay"): "disinhibition", # 苍白球→丘脑 (去抑制释放)
    ("thalamic_relay", "cortical_input"): "thalamocortical",# 丘脑→皮层 (闭合)
}

# 脑干广播目标 (D5, R7)
# DK_TARGETS: LC/中缝/VTA-SNc 投射的 dk_name 目标集
LC_TARGETS = []       # all cortical dk_names (动态填充)
RAPHE_TARGETS = []    # all cortical dk_names (动态填充)
VTA_TARGETS = [       # DA: 纹状体 + 前额叶 (D5)
    "Putamen", "Caudate", "Accumbens-area",
    "rostralmiddlefrontal", "superiorfrontal", "medialorbitofrontal",
    "frontalpole", "caudalmiddlefrontal", "lateralorbitofrontal", "parsopercularis"
]
SNc_TARGETS = [       # 运动 DA: 纹状体为主 (D5)
    "Putamen", "Caudate", "Accumbens-area"
]

# ─── 数据加载 ───────────────────────────────────────────────────

def load_brain_regions():
    """加载 brain_regions.json，返回 regions dict"""
    with open(ROOT / "data/brain_regions.json") as f:
        data = json.load(f)
    return data["regions"]


def load_signal_types():
    """加载 signal_types.json，返回受控词表"""
    with open(ROOT / "data/signal_types.json") as f:
        return json.load(f)


# ─── 图节点构建 ─────────────────────────────────────────────────

def build_graph_nodes(regions):
    """
    以 dk_name 为图节点，functional_id 为通信模式标签。
    同 dk_name 多 functional_id → profile 取并集 (R10)。

    返回:
      nodes: {dk_name: {...}}
      fids_by_dk: {dk_name: [functional_id, ...]}
    """
    # 按 dk_name 分组
    fids_by_dk = defaultdict(list)
    for fid, r in regions.items():
        dk = r.get("dk_name")
        if dk:
            fids_by_dk[dk].append(fid)
        else:
            # 脑干核团无 dk_name，用 functional_id 作为图节点
            fids_by_dk[fid].append(fid)

    nodes = {}
    for dk, fids in fids_by_dk.items():
        profiles = []
        levels = []
        categories = []
        mni_coords = []

        for fid in fids:
            r = regions[fid]
            pf = r.get("function_profile")
            if pf and isinstance(pf, dict) and "mirror_of" not in pf:
                profiles.append(pf)
            elif pf and isinstance(pf, dict) and "mirror_of" in pf:
                # 解析 mirror_of 引用
                target_fid = pf["mirror_of"]
                if target_fid in regions:
                    target_pf = regions[target_fid].get("function_profile")
                    if target_pf and isinstance(target_pf, dict) and "mirror_of" not in target_pf:
                        profiles.append(target_pf)

            lvl = r.get("level")
            if lvl is not None:
                levels.append(lvl)

            cat = r.get("category", "")
            if cat:
                categories.append(cat)

            mni = r.get("mni_xyz")
            if mni and len(mni) == 3:
                mni_coords.append(mni)

        # 取并集 (R10): input_types/output_types/gameplay_domain 取所有 profile 的并集
        union_input = []
        union_output = []
        union_domains = []
        union_cstc_loops = set()
        cstc_roles = set()
        timescales = set()

        for pf in profiles:
            for it in pf.get("input_types", []):
                if it not in union_input:
                    union_input.append(it)
            for ot in pf.get("output_types", []):
                if ot not in union_output:
                    union_output.append(ot)
            gd = pf.get("gameplay_domain", "")
            if gd and gd not in union_domains:
                union_domains.append(gd)
            cl = pf.get("cstc_loop", "none")
            if cl and cl != "none":
                union_cstc_loops.add(cl)
            cr = pf.get("cstc_role", "none")
            if cr and cr != "none":
                cstc_roles.add(cr)
            ts = pf.get("timescale", "")
            if ts:
                timescales.add(ts)

        # 确定代表性 level（取众数）
        rep_level = max(set(levels), key=levels.count) if levels else None
        rep_category = max(set(categories), key=categories.count) if categories else "unknown"
        rep_mni = mni_coords[0] if mni_coords else None

        nodes[dk] = {
            "dk_name": dk,
            "functional_ids": fids,
            "category": rep_category,
            "level": rep_level,
            "mni_xyz": rep_mni,
            "profile_count": len(profiles),
            "profile_missing": len(profiles) == 0,
            # 并集字段
            "input_types": union_input,
            "output_types": union_output,
            "gameplay_domains": union_domains,
            "cstc_loops": sorted(union_cstc_loops),
            "cstc_roles": sorted(cstc_roles),
            "timescales": sorted(timescales),
            # 振荡频段并集
            "oscillatory_bands": sorted(set(
                pf.get("oscillatory_band", "") for pf in profiles if pf.get("oscillatory_band")
            )),
            "neurotransmitters": sorted(set(
                pf.get("neurotransmitter_dominant", "") for pf in profiles if pf.get("neurotransmitter_dominant")
            )),
        }

    return nodes, fids_by_dk, regions


# ─── EDR 距离计算 ───────────────────────────────────────────────

def edr_distance(mni_a, mni_b):
    """计算 MNI 空间欧氏距离 (mm)"""
    if not mni_a or not mni_b:
        return None
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(mni_a, mni_b)))


def edr_probability(distance_mm):
    """EDR 连接概率 (Molnár et al. 2024)"""
    if distance_mm is None:
        return None
    return EDR_C * math.exp(-EDR_LAMBDA * distance_mm)


def edr_passes(distance_mm):
    """EDR 解剖天花板检查 (D11): p ≥ 0.10"""
    p = edr_probability(distance_mm)
    if p is None:
        return False
    return p >= EDR_THRESHOLD


# ─── CSTC 环路生成 ─────────────────────────────────────────────

def generate_cstc_loops(nodes):
    """
    生成 CSTC 环路连接。

    R1: 按 cstc_loop 分组 → 每环路内按 cstc_role 匹配 4 站。
    cstc_role=pallidal_output 和 thalamic_relay 的节点 cstc_loop=none，
    作为通配匹配所有环路 (D9)。
    STN→Pallidum 超直接 STOP 独立生成 (R8)。
    """
    connections = []

    # 按 cstc_loop 分组节点
    loop_nodes = {loop: defaultdict(list) for loop in CSTC_LOOPS}
    wildcard_pallidal = []  # cstc_loop=none, cstc_role=pallidal_output
    wildcard_thalamic = []  # cstc_loop=none, cstc_role=thalamic_relay
    stn_nodes = []           # STN for hyperdirect STOP

    for dk, node in nodes.items():
        for loop in node.get("cstc_loops", []):
            for role in node.get("cstc_roles", []):
                if role in ["cortical_input", "striatal_gate"]:
                    loop_nodes[loop][role].append(dk)

        # 通配节点 (R1)
        if "pallidal_output" in node.get("cstc_roles", []):
            wildcard_pallidal.append(dk)
        if "thalamic_relay" in node.get("cstc_roles", []):
            wildcard_thalamic.append(dk)

        # STN 超直接 STOP (R8) — 匹配完整 signal_type 格式
        stn_outputs = node.get("output_types", [])
        if "gating/stop_hyperdirect" in stn_outputs:
            stn_nodes.append(dk)

    # 为每个环路生成连接
    for loop in CSTC_LOOPS:
        cortical_inputs = loop_nodes[loop]["cortical_input"]
        striatal_gates = loop_nodes[loop]["striatal_gate"]

        if not cortical_inputs or not striatal_gates:
            continue

        # 1. cortical_input → striatal_gate (D1 GO 通路)
        for ci in cortical_inputs:
            for sg in striatal_gates:
                connections.append({
                    "source": ci,
                    "target": sg,
                    "type": "cstc",
                    "loop": loop,
                    "pathway": "go_direct",
                    "station_from": "cortical_input",
                    "station_to": "striatal_gate",
                    "description": f"{ci}→{sg}: {loop}环路 D1 GO 通路"
                })

        # 2. striatal_gate → pallidal_output (GO/NO-GO)
        for sg in striatal_gates:
            for pal in wildcard_pallidal:
                connections.append({
                    "source": sg,
                    "target": pal,
                    "type": "cstc",
                    "loop": loop,
                    "pathway": "go_direct",
                    "station_from": "striatal_gate",
                    "station_to": "pallidal_output",
                    "description": f"{sg}→{pal}: GO 去抑制 (D1 直接通路)"
                })
                # NO-GO 间接通路 (D2→GPe→STN→GPi，简化建模: striatal→pallidal D2)
                connections.append({
                    "source": sg,
                    "target": pal,
                    "type": "cstc",
                    "loop": loop,
                    "pathway": "nogo_indirect",
                    "station_from": "striatal_gate",
                    "station_to": "pallidal_output",
                    "description": f"{sg}→{pal}: NO-GO 增强抑制 (D2 间接通路)"
                })

        # 3. pallidal_output → thalamic_relay (去抑制释放)
        for pal in wildcard_pallidal:
            for thal in wildcard_thalamic:
                connections.append({
                    "source": pal,
                    "target": thal,
                    "type": "cstc",
                    "loop": loop,
                    "pathway": "disinhibition",
                    "station_from": "pallidal_output",
                    "station_to": "thalamic_relay",
                    "description": f"{pal}→{thal}: 苍白球去抑制→丘脑释放 ({loop})"
                })

        # 4. thalamic_relay → cortical_input (闭合环路)
        for thal in wildcard_thalamic:
            for ci in cortical_inputs:
                connections.append({
                    "source": thal,
                    "target": ci,
                    "type": "cstc",
                    "loop": loop,
                    "pathway": "thalamocortical",
                    "station_from": "thalamic_relay",
                    "station_to": "cortical_input",
                    "description": f"{thal}→{ci}: 丘脑皮层闭合 ({loop}环路)"
                })

    # 5. STN→Pallidum 超直接 STOP (R8, 全局急停，不按环路分组)
    for stn in stn_nodes:
        for pal in wildcard_pallidal:
            connections.append({
                "source": stn,
                "target": pal,
                "type": "cstc",
                "loop": "global",
                "pathway": "stop_hyperdirect",
                "station_from": "stn",
                "station_to": "pallidal_output",
                "description": f"{stn}→{pal}: STOP 超直接急停 (Nambu 2015)"
            })

    return connections


# ─── 皮层-皮层连接生成 ─────────────────────────────────────────

def generate_corticocortical(nodes, regions):
    """
    生成皮层-皮层连接。

    四层渐降筛选 (D4):
      1. EDR 解剖天花板 p≥0.10
      2. 层级相邻 |Δlevel| ≤ 1
      3. 双向互惠 (Markov et al. 2013)
      4. function_label 层（本脚本仅做结构生成，语义匹配交 build_function_labels.py）

    R9: 无 dk_name 的条目不参与皮层-皮层连接
    """
    connections = []

    # 筛选可参与皮层-皮层连接的节点
    # 排除：(a) 脑干核团（无真实 dk_name），(b) 无 MNI 坐标
    eligible = {}
    for dk, node in nodes.items():
        lvl = node.get("level")
        mni = node.get("mni_xyz")
        cat = node.get("category", "")
        fids = node.get("functional_ids", [])

        if lvl is None or mni is None:
            continue

        # 脑干核团：dk_name == functional_id（self-named），无真实皮层 dk_name
        is_brainstem_self_named = (cat == "brainstem" and len(fids) == 1 and dk == fids[0])

        if not is_brainstem_self_named:
            eligible[dk] = node

    dk_list = list(eligible.keys())

    for dk_a, dk_b in combinations(dk_list, 2):
        node_a = eligible[dk_a]
        node_b = eligible[dk_b]

        # 1. EDR 解剖天花板 (D11)
        dist = edr_distance(node_a.get("mni_xyz"), node_b.get("mni_xyz"))
        if not edr_passes(dist):
            continue

        # 2. 层级相邻 (R5)
        lvl_a = node_a.get("level")
        lvl_b = node_b.get("level")
        if lvl_a is None or lvl_b is None:
            continue
        if abs(lvl_a - lvl_b) > 1:
            continue

        # 3. 双向互惠 (R6) — 生成双向连接
        edr_p = edr_probability(dist)

        # A→B
        connections.append({
            "source": dk_a,
            "target": dk_b,
            "type": "corticocortical",
            "direction": "feedforward" if lvl_a < lvl_b else ("feedback" if lvl_a > lvl_b else "lateral"),
            "distance_mm": round(dist, 1),
            "edr_probability": round(edr_p, 4),
            "level_diff": lvl_b - lvl_a,
            "reciprocal_of": f"{dk_b}→{dk_a}",
        })

        # B→A (双向互惠)
        connections.append({
            "source": dk_b,
            "target": dk_a,
            "type": "corticocortical",
            "direction": "feedforward" if lvl_b < lvl_a else ("feedback" if lvl_b > lvl_a else "lateral"),
            "distance_mm": round(dist, 1),
            "edr_probability": round(edr_p, 4),
            "level_diff": lvl_a - lvl_b,
            "reciprocal_of": f"{dk_a}→{dk_b}",
        })

    return connections


# ─── 脑干广播生成 ───────────────────────────────────────────────

def generate_brainstem_broadcasts(nodes, regions):
    """
    生成脑干广播连接 (D5)。

    3 系统:
      LC→NE: 全皮层 (Foote & Morrison 1987)
      中缝→5-HT: 全皮层
      VTA→DA: 纹状体 + 前额叶
      SNc→DA: 纹状体 (运动)

    R7: DK_TARGETS 硬编码 dk_name 列表。脚本启动时自检。
    """
    connections = []

    # 收集皮层节点 dk_name 列表
    cortical_dks = [
        dk for dk, node in nodes.items()
        if node.get("category") == "cortical" and node.get("level") is not None
    ]

    # 自检硬编码目标 (R7)
    all_dk_names = set(nodes.keys())
    for target_list, source_name in [
        (VTA_TARGETS, "VTA"),
        (SNc_TARGETS, "SNc"),
    ]:
        missing = [t for t in target_list if t not in all_dk_names]
        if missing:
            print(f"  ⚠ WARN: {source_name} targets not in graph nodes: {missing}")

    # 找到脑干广播源节点
    lc_sources = [dk for dk in nodes if "LocusCoeruleus" in dk and "Right" not in dk]
    raphe_sources = [dk for dk in nodes if "Raphe" in dk]
    vta_sources = [dk for dk in nodes if "VentralTegmental" in dk]
    snc_sources = [dk for dk in nodes if "SubstantiaNigra" in dk and "Right" not in dk]

    # LC→NE: 全皮层广播
    for lc in lc_sources:
        for ctx in cortical_dks:
            connections.append({
                "source": lc,
                "target": ctx,
                "type": "brainstem_broadcast",
                "system": "LC_NE",
                "neurotransmitter": "norepinephrine",
                "projection": "diffuse_broadcast",
                "description": f"{lc}→{ctx}: NE 全皮层唤醒广播"
            })

    # 中缝→5-HT: 全皮层广播
    for rap in raphe_sources:
        for ctx in cortical_dks:
            connections.append({
                "source": rap,
                "target": ctx,
                "type": "brainstem_broadcast",
                "system": "Raphe_5HT",
                "neurotransmitter": "serotonin",
                "projection": "diffuse_broadcast",
                "description": f"{rap}→{ctx}: 5-HT 全皮层情绪调制广播"
            })

    # VTA→DA: 纹状体 + 前额叶
    for vta in vta_sources:
        for dk in VTA_TARGETS:
            if dk in nodes:
                connections.append({
                    "source": vta,
                    "target": dk,
                    "type": "brainstem_broadcast",
                    "system": "VTA_DA",
                    "neurotransmitter": "dopamine",
                    "projection": "targeted_broadcast",
                    "description": f"{vta}→{dk}: DA 奖赏预测误差"
                })

    # SNc→DA: 纹状体 (运动)
    for snc in snc_sources:
        for dk in SNc_TARGETS:
            if dk in nodes:
                connections.append({
                    "source": snc,
                    "target": dk,
                    "type": "brainstem_broadcast",
                    "system": "SNc_DA",
                    "neurotransmitter": "dopamine",
                    "projection": "targeted_broadcast",
                    "description": f"{snc}→{dk}: DA 运动启动/活力"
                })

    return connections


# ─── 验证 ───────────────────────────────────────────────────────

def validate_model(model, nodes, signal_types):
    """自检模型合法性"""
    errors = []
    warnings = []

    # 获取合法 signal_type 列表
    valid_subtypes = set()
    for cat_name, cat_data in signal_types.get("_categories", {}).items():
        for sub_name in cat_data.get("subtypes", {}):
            valid_subtypes.add(f"{cat_name}/{sub_name}")

    # 检查所有连接的 source/target 是否在图节点中
    all_dks = set(nodes.keys())
    all_connections = (model["cstc"] + model["corticocortical"] +
                       model["brainstem"] + model.get("stn_hyperdirect", []))

    for conn in all_connections:
        src = conn["source"]
        tgt = conn["target"]
        if src not in all_dks:
            errors.append(f"Source not in graph: {src}")
        if tgt not in all_dks:
            errors.append(f"Target not in graph: {tgt}")

    # 检查节点 profile 的 signal types 合法性
    for dk, node in nodes.items():
        for sig in node.get("input_types", []) + node.get("output_types", []):
            if sig not in valid_subtypes:
                warnings.append(f"Node {dk}: unknown signal type '{sig}'")

    return errors, warnings


# ─── 主函数 ─────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("build_tripartite_model.py — 三体神经模型生成器")
    print("=" * 60)

    # 加载数据
    print("\n[1/5] 加载数据...")
    regions = load_brain_regions()
    signal_types = load_signal_types()
    print(f"  brain_regions.json: {len(regions)} functional_ids")
    print(f"  signal_types.json: {len(signal_types['_categories'])} categories")

    # 构建图节点
    print("\n[2/5] 构建图节点 (dk_name 主键)...")
    nodes, fids_by_dk, all_regions = build_graph_nodes(regions)

    profiled = sum(1 for n in nodes.values() if not n["profile_missing"])
    print(f"  图节点: {len(nodes)} ({len(fids_by_dk)} dk_name groups)")
    print(f"  含 profile: {profiled}/{len(nodes)}")

    # 生成 CSTC 环路
    print("\n[3/5] 生成 CSTC 环路...")
    cstc = generate_cstc_loops(nodes)
    print(f"  CSTC 连接: {len(cstc)}")
    # 统计
    by_loop = defaultdict(int)
    by_pathway = defaultdict(int)
    for c in cstc:
        by_loop[c["loop"]] += 1
        by_pathway[c["pathway"]] += 1
    for loop in sorted(by_loop):
        print(f"    {loop}: {by_loop[loop]}")
    for pw in sorted(by_pathway):
        print(f"    {pw}: {by_pathway[pw]}")

    # 生成皮层-皮层连接
    print("\n[4/5] 生成皮层-皮层连接...")
    corticocortical = generate_corticocortical(nodes, regions)
    print(f"  皮层-皮层连接: {len(corticocortical)} (双向)")
    # 统计 EDR
    if corticocortical:
        dists = [c["distance_mm"] for c in corticocortical]
        print(f"    距离范围: {min(dists):.1f} - {max(dists):.1f} mm")
        ff = sum(1 for c in corticocortical if c["direction"] == "feedforward")
        fb = sum(1 for c in corticocortical if c["direction"] == "feedback")
        lat = sum(1 for c in corticocortical if c["direction"] == "lateral")
        print(f"    前馈: {ff}, 反馈: {fb}, 同层: {lat}")

    # 生成脑干广播
    print("\n[5/5] 生成脑干广播...")
    brainstem = generate_brainstem_broadcasts(nodes, regions)
    print(f"  脑干广播: {len(brainstem)}")
    by_system = defaultdict(int)
    for c in brainstem:
        by_system[c["system"]] += 1
    for sys in sorted(by_system):
        print(f"    {sys}: {by_system[sys]}")

    # 组装模型
    model = {
        "_description": "三体神经模型 — 三种通信原语替代旧 364 链路 pairwise 有向模型。Grilling #26 (2026-08-07)。",
        "_design_doc": "规则/技能树系统/脑功能层级模型.md §二十",
        "_generated_by": "tools/build_tripartite_model.py",
        "_created": "2026-08-07",
        "graph_nodes": {
            dk: {
                k: v for k, v in node.items()
                if k not in ("input_types", "output_types")  # 完整 profile 在 function_labels 层处理
            }
            for dk, node in nodes.items()
        },
        "node_profiles": {
            dk: {
                "input_types": node["input_types"],
                "output_types": node["output_types"],
                "gameplay_domains": node["gameplay_domains"],
                "cstc_loops": node["cstc_loops"],
                "cstc_roles": node["cstc_roles"],
                "oscillatory_bands": node["oscillatory_bands"],
                "neurotransmitters": node["neurotransmitters"],
            }
            for dk, node in nodes.items()
        },
        "cstc": cstc,
        "corticocortical": corticocortical,
        "brainstem": brainstem,
    }

    # 验证
    errors, warnings = validate_model(model, nodes, signal_types)
    if errors:
        print(f"\n❌ 验证错误 ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    if warnings:
        print(f"\n⚠️ 验证警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")

    # 写入
    output_path = ROOT / "data/connectivity/tripartite_model.json"
    with open(output_path, "w") as f:
        json.dump(model, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 三体神经模型已写入: {output_path}")

    # 摘要
    total = len(cstc) + len(corticocortical) + len(brainstem)
    print(f"\n{'=' * 60}")
    print(f"摘要: {len(nodes)} 图节点, {total} 连接")
    print(f"  CSTC 环路:       {len(cstc):>5}")
    print(f"  皮层-皮层:       {len(corticocortical):>5}")
    print(f"  脑干广播:        {len(brainstem):>5}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
