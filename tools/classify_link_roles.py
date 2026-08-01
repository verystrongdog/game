#!/usr/bin/env python3
"""
364 链路行为角色自动分类
基于脑区/网络/层级规则 → 为每条链路分配 1-2 个行为角色标签
输出: data/connectivity/link_behavior_roles.json
"""

import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent.parent

# 行为角色定义: {角色: {regions, networks, layers, weight}}
ROLE_DEFS = {
    "attack_physical": {
        "regions": {"M1", "旁中央小叶", "壳核", "苍白球", "小脑皮层",
                     "S1", "丘脑", "黑质致密部", "脑桥网状核", "纹状体基质"},
        "networks": {"Motor"},
        "layers": {0, 1, 3},  # L0-L3 motor output
        "weight": 1.0,
    },
    "attack_mental": {
        "regions": {"Broca区", "Wernicke区", "弓状束", "缘上回",
                     "颞上回", "颞中回", "角回"},
        "networks": {"Semantic Memory", "Theory of Mind"},
        "layers": {4, 5},  # L4-L5 language
        "weight": 1.0,
    },
    "defend": {
        "regions": {"PAG", "中缝背核", "中缝正中核", "脑桥网状核",
                     "反射环路·冻结反应", "反射环路·快速闪避",
                     "反射环路·PAG→杏仁核", "杏仁核-PAG", "杏仁核",
                     "缰核", "蓝斑"},
        "networks": {"Emotion Regulation"},
        "layers": {0, 1},
        "weight": 1.2,  # 提高防御权重，避免被disrupt吞掉
    },
    "flee": {
        "regions": {"杏仁核", "杏仁核-PAG", "反射环路·PAG→杏仁核",
                     "上丘", "BNST", "反射环路·快速闪避", "反射环路·冻结反应",
                     "PAG"},
        "networks": {"Emotional Scene and Face Processing"},
        "layers": {0, 1},
        "weight": 1.3,  # 逃跑是特异性最高的反射，提高区分度
    },
    "approach": {
        "regions": {"VTA", "VTA-NAcc", "NAcc壳", "NAcc核", "伏隔核/NAcc",
                     "腹侧纹状体", "OFC", "壳核", "尾状核",
                     "黑质致密部"},
        "networks": {"Reward"},
        "layers": {0, 1, 2},
        "weight": 1.0,
    },
    "perceive": {
        "regions": {"A1", "枕叶 V1", "楔叶", "外侧枕叶", "楔前叶",
                     "纺锤体回", "颞下回", "枕顶联合", "顶内沟", "顶叶",
                     "颞上沟岸", "颞上沟", "S1", "角回", "海马旁回",
                     "内嗅皮层", "前脑岛", "峡部扣带"},
        "networks": {"Emotional Scene and Face Processing",
                      "Vigilant Attention", "Cognitive Attention Control"},
        "layers": {3, 4},  # L3-L4 sensory/perceptual
        "weight": 1.0,
    },
    "support": {
        "regions": {"蓝斑", "中缝背核", "中缝正中核", "vmPFC",
                     "后扣带", "楔前叶", "前额叶极", "前额叶极·DMN",
                     "前额叶极·FPN", "前额叶极·SN", "ACC吻侧",
                     "缰核", "下丘脑", "隔区", "岛叶-vmPFC"},
        "networks": {"Autobiographical Memory", "Extended Socio-Affective Default"},
        "layers": {0, 2, 5, 6},  # L0 broadcast + L5-L6 self-referential
        "weight": 1.0,
    },
    "disrupt": {
        # 收紧: 只包含社会认知压制/操纵相关的脑区，排除通用的认知控制
        "regions": {"TPJ", "颞极", "颞上沟岸", "vmPFC-TPJ",
                     "岛叶-PFC-杏仁核", "岛叶-ACC-VTA",
                     "基底节间接通路",  # 行为抑制
                     "杏仁核-海马"},  # 恐惧记忆激活
        "networks": {"Empathy", "Mirror Neuron System"},
        "layers": {2, 4, 5},
        "weight": 1.0,
    },
}


def score_link(link, role_def):
    """计算一条链路对某个行为角色的匹配得分 0-1"""
    score = 0.0
    regions = set(link["regions_a"]) | set(link["regions_b"])
    networks = set(link["coactivated_networks"])
    layers = set(link["layers"])

    # 脑区命中
    region_hits = regions & role_def["regions"]
    if region_hits:
        score += 0.5 * (len(region_hits) / max(len(regions), 1))

    # 网络命中
    net_hits = networks & role_def["networks"]
    if net_hits:
        score += 0.3 * (len(net_hits) / max(len(networks), 1))

    # 层级命中
    layer_hits = layers & role_def["layers"]
    if layer_hits:
        score += 0.2

    return score * role_def["weight"]


def classify_links():
    with open(ROOT / "data/connectivity/link_legitimacy_matrix.json") as f:
        data = json.load(f)

    links = data["links"]
    results = []
    role_counts = Counter()

    for i, link in enumerate(links):
        scores = {}
        for role_name, role_def in ROLE_DEFS.items():
            s = score_link(link, role_def)
            if s > 0:
                scores[role_name] = round(s, 3)

        # 排序取 top 1-2
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        primary = ranked[0] if ranked else None
        secondary = ranked[1] if len(ranked) > 1 and ranked[1][1] > 0.25 else None

        roles_assigned = []
        if primary:
            roles_assigned.append(primary[0])
            role_counts[primary[0]] += 1
        if secondary:
            roles_assigned.append(secondary[0])
            role_counts[secondary[0]] += 1

        # 处理两种链路格式: dk_pair版 和 brainstem版
        if "dk_pair" in link:
            pair_label = link["dk_pair"]
        elif "brainstem_nucleus" in link:
            pair_label = [link["brainstem_nucleus"], link.get("dk_target", "")]
            # brainstem 链路的 regions_b 可能为空，从 dk_target 补
            if not link.get("regions_b") and link.get("dk_target"):
                link["regions_b"] = [link["dk_target"]]
        else:
            pair_label = [str(link["regions_a"]), str(link["regions_b"])]

        entry = {
            "link_id": i,
            "dk_pair": pair_label,
            "layers": link["layers"],
            "direction": link["direction"],
            "regions_a": link["regions_a"],
            "regions_b": link["regions_b"],
            "roles": roles_assigned,
            "role_scores": {k: v for k, v in ranked[:3]},
        }
        results.append(entry)

    # 统计
    print("=== 角色分布 ===")
    for role, count in role_counts.most_common():
        print(f"  {role}: {count} links")

    unclassified = [r for r in results if not r["roles"]]
    print(f"\n未分类链路: {len(unclassified)}")

    # 单角色 vs 双角色
    single = [r for r in results if len(r["roles"]) == 1]
    double = [r for r in results if len(r["roles"]) == 2]
    print(f"单角色: {len(single)}, 双角色: {len(double)}")

    # 输出
    output = {
        "_description": "364 条链路的行为角色分类 — 用于预烘焙管线采样校验和配置多样性保障",
        "_note": "数值量化是后续内容填充工作，不在此文件中",
        "role_definitions": {
            "attack_physical": "M1通道物理攻击调制",
            "attack_mental": "Broca通道精神攻击调制",
            "defend": "防御/忍耐调制",
            "flee": "逃离/回避",
            "approach": "趋近/追击",
            "perceive": "感知/读意图（L3-L4）",
            "support": "自我/友方增益（非攻击性调制）",
            "disrupt": "敌方减益/SAN攻击（社会认知压制）",
        },
        "links": results,
    }

    out_path = ROOT / "data/connectivity/link_behavior_roles.json"
    with open(out_path, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n输出: {out_path}")

    # 展示前 10 条作为样例
    print("\n=== 样例 (前10条) ===")
    for r in results[:10]:
        region_str = "→".join(r["regions_a"]) + " → " + "→".join(r["regions_b"])
        print(f"  [{r['link_id']:3d}] L{r['layers'][0]}→L{r['layers'][1]} {region_str:40s} | {r['roles']}")

    return results


if __name__ == "__main__":
    classify_links()
