#!/usr/bin/env python3
"""
链路注册表生成器
从 link_legitimacy_matrix.json 提取全部 364 条链路（323 ENIGMA + 41 brainstem），
分配唯一 ID，生成统一 display_name，输出 link_registry.json。
每次链路矩阵更新后重新运行。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent

DIRECTION_SYMBOLS = {
    "feedforward": "→",
    "feedback": "←",
    "lateral": "↔",
}


def hemisphere(label: str) -> str:
    """从 ENIGMA label 提取半球: L_xxx → L, R_xxx → R, 否则空"""
    if label.startswith("L_"):
        return "L"
    if label.startswith("R_"):
        return "R"
    return ""


def build_display_name_enigma(link: dict) -> str:
    """ENIGMA链路: regions_a主名 + 方向 + regions_b主名"""
    a_main = link["regions_a"][0]
    b_main = link["regions_b"][0]
    arrow = DIRECTION_SYMBOLS.get(link["direction"], "—")
    # 加半球标注避免左右半球重名
    enigma_labels = link.get("enigma_labels", [])
    if enigma_labels and len(enigma_labels) >= 2:
        hemi_a = hemisphere(enigma_labels[0])
        hemi_b = hemisphere(enigma_labels[1])
        hemi = ""
        if hemi_a == hemi_b and hemi_a:
            hemi = f"({hemi_a})"
        elif hemi_a and hemi_b:
            hemi = f"({hemi_a}→{hemi_b})"
        elif hemi_a:
            hemi = f"({hemi_a})"
        if hemi:
            return f"{a_main} {arrow} {b_main} {hemi}"
    return f"{a_main} {arrow} {b_main}"


def build_display_name_brainstem(link: dict) -> str:
    """脑干链路: 从pathway字段简化，去掉括号备注"""
    pathway = link.get("pathway", "")
    cleaned = re.sub(r"\([^)]*\)", "", pathway).strip()
    return cleaned


def build_registry():
    with open(ROOT / "data/connectivity/link_legitimacy_matrix.json", encoding="utf-8") as f:
        matrix = json.load(f)

    registry = {
        "_description": "统一链路注册表 — 364 条合法链路的唯一 ID 和显示名",
        "_generated_from": "data/connectivity/link_legitimacy_matrix.json",
        "_total": len(matrix["links"]),
        "_enigma_count": 0,
        "_brainstem_count": 0,
        "links": [],
    }

    enigma_count = 0
    brainstem_count = 0

    for i, link in enumerate(matrix["links"]):
        link_id = f"link_{i:03d}"

        if "brainstem_nucleus" in link:
            display_name = build_display_name_brainstem(link)
            data_source = "brainstem"
            source_region = link["brainstem_nucleus"]
            target_region = link.get("dk_target", "")
            brainstem_count += 1
            entry = {
                "id": link_id,
                "display_name": display_name,
                "source_region": source_region,
                "target_region": target_region,
                "layers": link["layers"],
                "direction": link["direction"],
                "data_source": data_source,
                "brainstem_nucleus": link["brainstem_nucleus"],
                "dk_target": link["dk_target"],
                "fc_strength": link.get("fc_strength"),
                "pathway": link["pathway"],
                "ref": link.get("ref", ""),
                "regions_a": link.get("regions_a", [source_region]),
                "regions_b": link.get("regions_b", []),
                "coactivated_networks": link.get("coactivated_networks", []),
            }
        else:
            display_name = build_display_name_enigma(link)
            data_source = "enigma"
            source_region = link["regions_a"][0]
            target_region = link["regions_b"][0]
            enigma_count += 1
            entry = {
                "id": link_id,
                "display_name": display_name,
                "source_region": source_region,
                "target_region": target_region,
                "layers": link["layers"],
                "direction": link["direction"],
                "data_source": data_source,
                "brainstem_nucleus": None,
                "dk_target": None,
                "fc_strength": None,
                "pathway": None,
                "ref": "",
                "regions_a": link["regions_a"],
                "regions_b": link["regions_b"],
                "coactivated_networks": link.get("coactivated_networks", []),
                "dk_pair": link.get("dk_pair"),
                "enigma_strength": link.get("enigma_strength"),
            }

        registry["links"].append(entry)

    registry["_enigma_count"] = enigma_count
    registry["_brainstem_count"] = brainstem_count

    return registry


def deduplicate(registry: dict):
    """检测重名并追加唯一后缀"""
    name_counts = {}
    for link in registry["links"]:
        name = link["display_name"]
        name_counts[name] = name_counts.get(name, 0) + 1

    # 对出现次数 >1 的名称，追加序号
    name_seen = {}
    for link in registry["links"]:
        name = link["display_name"]
        if name_counts[name] > 1:
            name_seen[name] = name_seen.get(name, 0) + 1
            link["display_name"] = f"{name} #{name_seen[name]}"

    duplicate_groups = {k: v for k, v in name_counts.items() if v > 1}
    return duplicate_groups


def main():
    registry = build_registry()
    duplicates_before = deduplicate(registry)

    # Re-count after deduplication
    all_names = [l["display_name"] for l in registry["links"]]
    dupes_after = len(all_names) - len(set(all_names))

    print(f"ENIGMA links:     {registry['_enigma_count']}")
    print(f"Brainstem links:  {registry['_brainstem_count']}")
    print(f"Total:            {registry['_total']}")
    print(f"重名组(去重前):   {len(duplicates_before)}")
    print(f"重名(去重后):     {dupes_after}")

    if dupes_after > 0:
        print(f"⚠️  去重后仍有 {dupes_after} 个重名!")
        return

    # Write registry
    out_path = ROOT / "data/connectivity/link_registry.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    # Write compact name→id lookup for scripts
    lookup = {l["display_name"]: l["id"] for l in registry["links"]}
    lookup_path = ROOT / "data/connectivity/link_name_lookup.json"
    with open(lookup_path, "w", encoding="utf-8") as f:
        json.dump(lookup, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 输出: {out_path}")
    print(f"✓ 输出: {lookup_path}  ({len(lookup)} 条目)")


if __name__ == "__main__":
    main()
