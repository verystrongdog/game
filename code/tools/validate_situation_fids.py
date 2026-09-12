#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""情境原型 fid 一致性校验器（Grilling #108 Q13 第一层防线，T4）。

断言（验收门槛 = 27 原型 key_brain_regions 去重 37 名 100% 命中）：
1. 名称 ∈ region_name_map.regions（69 键）
2. name == functional_id（键即 functional_id，直接比对）

铁律：
- **不建立 dk→fid 翻译映射表**（#108 Q13：当前 37 个去重名已 100% 是 fid，翻译需求 = 0）
- 失败 → exit 非零（不静默降级；管线门禁）
- 新增原型自动纳入（遍历 situation_primitives.json 全量，无硬编码名单）

用法: python3 code/tools/validate_situation_fids.py [--report]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SP_PATH = ROOT / "data" / "connectivity" / "situation_primitives.json"
RN_PATH = ROOT / "data" / "connectivity" / "region_name_map.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="输出完整命中报告")
    args = ap.parse_args()

    sp = json.loads(SP_PATH.read_text(encoding="utf-8"))
    rn = json.loads(RN_PATH.read_text(encoding="utf-8"))
    regions = rn["regions"]  # dict: functional_id → meta

    archetypes = sp.get("situation_archetypes", [])
    if len(archetypes) != 27:
        print(f"警告: 情境原型数 {len(archetypes)} ≠ 27（数据演进，非校验失败——校验器自动纳入新原型）")

    all_names = set()
    per_archetype = {}
    for a in archetypes:
        kbr = a.get("key_brain_regions", [])
        per_archetype[a["name"]] = kbr
        all_names.update(kbr)

    errors = []
    # ① 名称 ∈ regions
    missing = sorted(n for n in all_names if n not in regions)
    if missing:
        errors.append(f"不在 region_name_map.regions: {missing}")
    # ② name == functional_id
    mismatched = sorted(n for n in all_names if n in regions and regions[n].get("functional_id") != n)
    if mismatched:
        errors.append(f"name != functional_id: {mismatched}")

    hit = len(all_names) - len(missing)
    total = len(all_names)
    pct = 100.0 * hit / total if total else 0.0

    print(f"原型数: {len(archetypes)} | 去重 key_brain_regions 名: {total} | 命中: {hit} ({pct:.1f}%)")
    if args.report:
        print(f"G 组候选（negative_valence ≥ 0.2 ∧ valence=negative）:")
        for a in archetypes:
            nv = a.get("rdoc_profile", {}).get("negative_valence")
            val = a.get("appraisal_profile", {}).get("valence")
            if nv is not None and nv >= 0.2 and val == "negative":
                print(f"  {a['name']} (nv={nv}, {val})")

    if errors:
        print("校验失败:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"校验通过: {total}/{total} 名 ∈ region_name_map.regions 且 name == functional_id（无 dk→fid 映射表）")
    sys.exit(0)


if __name__ == "__main__":
    main()
