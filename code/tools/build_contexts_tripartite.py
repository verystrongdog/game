#!/usr/bin/env python3
"""
build_contexts_tripartite.py — 三体连接 → 上下文集合映射（P1a 重建）

Grilling #72 (P1a) D2/D3/D5 落地。替代旧 link_contexts.json（基于已废弃 364 链路）。

算法（task-plan §三 _rules，逐条对应）：
  1. edge_set = corticocortical ∪ privileged_pathways (888 信息传递边)
  2. networks(edge) = {n : n.gameplay_domains ∩ edge.gameplay_labels ≠ ∅} (kroell14, 14 网络)
  3. role_scores(edge)[r] = Σ_domain w(domain, r) × [domain ∈ edge.gameplay_labels]
       —— domain_role_map.json（12 domain → 8 role 权重表）
  4. primary_role = argmax_r role_scores；secondary_role = 次高分 r（score > 0.25）
  5. contexts(edge) = {(network, primary_role) for network in networks(edge)}
  6. 候选技能 context = 组内 edge_count ≥ 2

契约（Grilling #112 Q1/Q2 定案）：
  - edge_contexts.source/target 用 dk_name（与 tripartite graph_nodes.dk_name 对齐），
    不转 functional_id —— fid 反查归 P1c SkillCatalog
  - 输出含 schema/version 契约字段（非 Module 的强契约数据产物）：
    消费方加载时 version 不匹配 → fail-fast（对标 alpha_patterns/env_tones 先例）
  - 纯函数：同输入同输出（确定性）

输入:
  - data/connectivity/tripartite_model.json（corticocortical + privileged_pathways）
  - data/connectivity/kroell14_networks.json（networks[].name / gameplay_domains）
  - data/connectivity/domain_role_map.json（12 domain → 8 role 权重）

输出:
  - data/connectivity/link_contexts_tripartite.json（双视图 + stats）

设计依据:
  - ../设计归档/grilling/grilling-72-p1a-skill-context/task-plan.md §三/§四/§六
  - docs/决策树/ [Grilling] P1a 技能上下文三体重建（数据层）(2026-08-16)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent

# ─── 契约常量 ───────────────────────────────────────────────────
SCHEMA = "link_contexts_tripartite"
VERSION = 1
SECONDARY_ROLE_MIN = 0.25  # task-plan §三 _rules：次高分需 > 0.25
CANDIDATE_MIN_EDGES = 2    # 候选技能 context 过滤阈值（技能生成机制 §二）


def load_json(rel: str):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def build_networks(edge_labels, networks):
    """D2：networks(edge) = {n : n.gameplay_domains ∩ edge.gameplay_labels ≠ ∅}。"""
    edge_set = set(edge_labels)
    return [n["name"] for n in networks if edge_set & set(n.get("gameplay_domains", []))]


def role_scores_for(edge_labels, domain_map):
    """D3：role_scores(edge)[r] = Σ_domain w(domain, r) × [domain ∈ labels]。"""
    scores = defaultdict(float)
    for domain in edge_labels:
        weights = domain_map.get(domain, {})
        for role, w in weights.items():
            scores[role] += w
    return dict(scores)


def pick_roles(scores, roles_order):
    """D3：primary = argmax；secondary = 次高分 > 0.25。"""
    scored = [(r, scores.get(r, 0.0)) for r in roles_order]
    scored.sort(key=lambda kv: (-kv[1], roles_order.index(kv[0])))
    primary = scored[0][0]
    secondary = None
    for r, s in scored[1:]:
        if s > SECONDARY_ROLE_MIN:
            secondary = r
            break
    return primary, secondary


def main():
    tripartite = load_json("data/connectivity/tripartite_model.json")
    kroell14 = load_json("data/connectivity/kroell14_networks.json")
    domain_map_data = load_json("data/connectivity/domain_role_map.json")

    networks = kroell14["networks"]
    domain_map = domain_map_data["domains"]
    roles_order = domain_map_data["roles"]

    cc_edges = tripartite["corticocortical"]
    pp_edges = tripartite["privileged_pathways"]

    # ── 1. 边键（cc:NNN / pp:NNN = 数组索引，0-based，与 tripartite 顺序绑定）──
    edge_keys = [f"cc:{i}" for i in range(len(cc_edges))] + \
                [f"pp:{i}" for i in range(len(pp_edges))]
    all_edges = cc_edges + pp_edges

    # ── 2/3/4/5. 逐边计算 ──
    contexts: dict[str, dict] = {}        # context_key -> {network, role, edges, edge_count}
    edge_contexts: dict[str, dict] = {}   # edge_key -> 反视图

    for key, edge in zip(edge_keys, all_edges):
        labels = edge.get("gameplay_labels", [])
        nets = build_networks(labels, networks)
        scores = role_scores_for(labels, domain_map)
        primary, secondary = pick_roles(scores, roles_order)

        edge_ctx_list = [[n, primary] for n in nets]
        edge_contexts[key] = {
            "source": edge["source"],     # dk_name（Q1 契约：与 graph_nodes.dk_name 对齐）
            "target": edge["target"],
            "networks": nets,
            "role_scores": {r: round(s, 4) for r, s in sorted(scores.items())},
            "primary_role": primary,
            "secondary_role": secondary,
            "contexts": edge_ctx_list,
        }
        for n, r in edge_ctx_list:
            ck = f"{n}/{r}"
            entry = contexts.setdefault(ck, {"network": n, "role": r, "edges": [], "edge_count": 0})
            entry["edges"].append(key)
            entry["edge_count"] += 1

    # ── stats ──
    uncovered = [k for k, e in edge_contexts.items() if not e["networks"]]
    candidate_skills = {k: v for k, v in contexts.items() if v["edge_count"] >= CANDIDATE_MIN_EDGES}
    role_dist = defaultdict(int)
    for v in edge_contexts.values():
        role_dist[v["primary_role"]] += 1

    # 角色健康性诊断（Grilling #112 Q3.6 外审定案：零主角色 = KNOWN DESIGN LIMITATION，
    # 归因既定权重参数（task-plan §四 初始值），非重建实现错误；权重修正归 #35，本轮禁改）
    zero_roles = [r for r in roles_order if role_dist.get(r, 0) == 0]
    role_health = {
        "zero_primary_roles": zero_roles,
        "status": "KNOWN DESIGN LIMITATION" if zero_roles else "PASS",
        "note": "零主角色 ≠ 无该角色上下文——是当前初始权重下该角色无法成为 argmax（同域高权重支配）。"
                "权重修正属 #35 校准轨，P1a 重建不得修改权重规避。校准后重新验证。",
    } if zero_roles else {
        "zero_primary_roles": [],
        "status": "PASS",
    }

    stats = {
        "total_edges": len(edge_keys),
        "network_assigned": len(edge_keys) - len(uncovered),
        "uncovered_edges": len(uncovered),
        "uncovered_reason": "仅含 thalamic_relay 独标签边（kroell14 无此域）" if uncovered else "无",
        "role_assigned": len(edge_keys),
        "contexts": len(contexts),
        "candidate_skills": len(candidate_skills),
        "role_distribution": {r: role_dist.get(r, 0) for r in roles_order},
        "role_health": role_health,
    }

    output = {
        "schema": SCHEMA,
        "version": VERSION,
        "_description": "三体连接 → 上下文集合映射 (Grilling #72 P1a)，替代旧 link_contexts.json（基于已废弃 364 链路）",
        "_rules": [
            "edge_set = corticocortical ∪ privileged_pathways (888)",
            "networks(edge) = {n : n.gameplay_domains ∩ edge.gameplay_labels ≠ ∅} (kroell14, 14 网络)",
            "role_scores(edge)[r] = Σ_domain w(domain, r) × [domain ∈ edge.gameplay_labels] (domain_role_map.json)",
            "primary_role = argmax_r role_scores; secondary = 次高分 r (score > 0.25)",
            "contexts(edge) = {(network, primary_role) for network in networks(edge)}",
            "候选技能 context = 组内 edge_count ≥ 2",
            "edge_contexts.source/target = dk_name（fid 反查归 P1c SkillCatalog）",
        ],
        "contexts": dict(sorted(contexts.items())),
        "edge_contexts": edge_contexts,
        "stats": stats,
    }

    out_path = ROOT / "data/connectivity/link_contexts_tripartite.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # ── 断言（task-plan §六 验证方案）──
    assert len(edge_keys) == 888, f"边数 ≠ 888: {len(edge_keys)}"
    assert len(edge_contexts) == 888, "反视图缺边"
    assert set(edge_contexts.keys()) == set(edge_keys), "边键双射失败"
    # 双视图互为转置：contexts[ck].edges 与 edge_contexts[key].contexts 一一对应
    # 注意：contexts 值为 [network, role] 列表对（task-plan §三 schema），需拆 key 比较
    for ck, c in contexts.items():
        network, role = ck.rsplit("/", 1)
        for e in c["edges"]:
            assert [network, role] in edge_contexts[e]["contexts"], f"转置失败: {ck} ↔ {e}"
    for k, e in edge_contexts.items():
        for n, r in e["contexts"]:
            ck = f"{n}/{r}"
            assert k in contexts[ck]["edges"], f"转置失败: {k} ↔ {ck}"
    assert all(v["role"] in roles_order for v in contexts.values())
    print(f"OK: 888 边 / {len(contexts)} contexts / {stats['candidate_skills']} 候选技能 / "
          f"uncovered {stats['uncovered_edges']}")
    print(f"角色分布: {stats['role_distribution']}")
    print(f"写出: data/connectivity/link_contexts_tripartite.json")


if __name__ == "__main__":
    main()
