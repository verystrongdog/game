#!/usr/bin/env python3
"""
性格标签 → 链路映射 自动生成
基于标签的脑区群 + 行为角色偏好，从 364 条链路中自动匹配
输出: data/connectivity/personality_tag_links.json
"""

import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent.parent

# 6 个性格标签定义 — 基于 NPC AI 行为模型 §4.1
TAG_DEFS = {
    "threat_sensitization": {
        "display_name": "敏化-威胁",
        "core_regions": {"杏仁核", "PAG", "前脑岛", "BNST", "上丘",
                          "杏仁核-PAG", "反射环路·PAG→杏仁核",
                          "反射环路·冻结反应", "反射环路·快速闪避"},
        "preferred_roles": {"flee", "defend", "perceive"},
        "main_offset": 0.4,
        "description": "过度警觉，容易恐惧逃离。杏仁核+前脑岛→PAG/脑干防御回路增强。"
    },
    "reward_sensitization": {
        "display_name": "敏化-奖励",
        "core_regions": {"VTA", "VTA-NAcc", "NAcc壳", "NAcc核", "伏隔核/NAcc",
                          "腹侧纹状体", "OFC", "壳核", "黑质致密部"},
        "preferred_roles": {"approach", "attack_physical"},
        "main_offset": 0.4,
        "description": "冲动趋近，成瘾倾向。VTA→NAcc/壳核奖赏回路增强。"
    },
    "under_inhibition": {
        "display_name": "抑制不足",
        "core_regions": {"dlPFC", "额中回尾部", "额上回", "额极",
                          "前额叶极", "前额叶极·FPN", "前额叶极·SN",
                          "基底节间接通路"},
        "preferred_roles": {"approach", "attack_physical", "attack_mental", "disrupt"},
        "main_offset": 0.4,
        "description": "自控差，无法压制冲动。dlPFC→杏仁核/纹状体抑制链路弱（负向偏移，即这些抑制链路不被选中）。此处选择的是少了抑制后会多出来的行动链路。"
    },
    "over_inhibition": {
        "display_name": "过度抑制",
        "core_regions": {"dlPFC", "额中回尾部", "额上回", "额极",
                          "前额叶极·FPN", "基底节间接通路",
                          "ACC背侧", "岛叶-ACC", "缰核"},
        "preferred_roles": {"defend", "support", "perceive"},
        "main_offset": 0.4,
        "description": "抑制一切——不说话、不动、情感淡漠。dlPFC控制链路全面增强。"
    },
    "rumination": {
        "display_name": "反刍",
        "core_regions": {"后扣带", "vmPFC", "楔前叶", "前额叶极·DMN",
                          "DMN+OFC", "海马体 CA1", "海马体 CA3",
                          "杏仁核-海马", "前额叶-海马", "内嗅皮层",
                          "mPFC", "峡部扣带"},
        "preferred_roles": {"support", "perceive"},
        "main_offset": 0.4,
        "description": "关不掉的内在世界。默认网络（后扣带+vmPFC）髓鞘化过高。"
    },
    "social_blunting": {
        "display_name": "社交钝化",
        # 社交钝化是 m 降低，不是升高。这里选的是"被压低"的链路集合。
        # offset_direction = negative → 这些链路的 m 被减去 0.4
        "core_regions": {"颞极", "mPFC", "颞上沟岸", "TPJ", "vmPFC-TPJ",
                          "岛叶-vmPFC", "Broca区", "Wernicke区",
                          "ACC吻侧"},
        "preferred_roles": {"attack_mental", "disrupt", "perceive"},
        "main_offset": -0.4,  # 负向：社交链路被压低
        "description": "不理解社交线索，不回应。颞极/mPFC/STS社会认知链路髓鞘化过低（负向偏移）。"
    },
}


def score_link_for_tag(link, tag_def):
    """计算链路对标签的相关性得分"""
    regions = set(link["regions_a"]) | set(link["regions_b"])
    roles = set(link["roles"])

    # 核心脑区命中
    core_hits = regions & tag_def["core_regions"]
    core_score = len(core_hits) / max(len(regions), 1) if core_hits else 0

    # 行为角色偏好
    role_hits = roles & tag_def["preferred_roles"]
    role_score = len(role_hits) / max(len(roles), 1) if role_hits else 0

    return round(core_score * 0.7 + role_score * 0.3, 3)


def main():
    with open(ROOT / "data/connectivity/link_behavior_roles.json") as f:
        roles_data = json.load(f)

    output = {
        "_description": "性格标签 → 链路 ID 映射 — 自动生成初稿，人工可覆盖",
        "_source": "code/tools/generate_tag_links.py",
        "_note": "collateral_links 留空待人工审核后补充",
        "tags": {},
    }

    for tag_id, tag_def in TAG_DEFS.items():
        scored = []
        for link in roles_data["links"]:
            s = score_link_for_tag(link, tag_def)
            if s > 0:
                scored.append((link["link_id"], s, link["roles"], link["layers"]))

        # 按得分排序，取 top 15-20 条（≈ 标签覆盖 3-8 条链路 × 2-3x 候选）
        scored.sort(key=lambda x: -x[1])

        # 阈值：得分 > 0.2 且最多 15 条（留有审核余地）
        selected = [(lid, s, r, ly) for lid, s, r, ly in scored if s > 0.2][:15]

        core_links = [lid for lid, s, r, ly in selected]
        print(f"\n{tag_def['display_name']} ({tag_id}):")
        print(f"  offset: {tag_def['main_offset']:+.1f}")
        print(f"  选中 {len(core_links)} 条链路:")
        for lid, s, r, ly in selected:
            print(f"    [{lid:3d}] L{ly[0]}→L{ly[1]} score={s:.2f} roles={r}")

        output["tags"][tag_id] = {
            "display_name": tag_def["display_name"],
            "description": tag_def["description"],
            "main_offset": tag_def["main_offset"],
            "core_links": core_links,
            "collateral_links": {},  # 待人工补充
            "auto_generated": True,
        }

    out_path = ROOT / "data/connectivity/personality_tag_links.json"
    with open(out_path, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n输出: {out_path}")


if __name__ == "__main__":
    main()
