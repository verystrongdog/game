#!/usr/bin/env python3
"""
区域名规范化脚本 — 试运行
从 situation_primitives.json 提取所有脑区名，
尝试自动映射到 brain_regions.json 的规范 key，
输出命中/未命中/歧义报告。
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

def load_canonical():
    """加载 brain_regions.json 的89个规范key"""
    with open(ROOT / "data/brain_regions.json") as f:
        br = json.load(f)
    keys = list(br["regions"].keys())
    # 构建 lower → [key, ...] 索引 (可能有大小写冲突)
    lower_index = {}
    for k in keys:
        lk = k.lower()
        lower_index.setdefault(lk, []).append(k)
    return keys, lower_index

def extract_situation_regions():
    """递归提取 situation_primitives.json 中所有 key_brain_regions 的名称"""
    with open(ROOT / "data/connectivity/situation_primitives.json") as f:
        sp = json.load(f)

    raw_names = set()
    name_sources = {}  # name → [context_path, ...]

    def walk(obj, path=""):
        if isinstance(obj, dict):
            if "key_brain_regions" in obj:
                for r in obj["key_brain_regions"]:
                    raw_names.add(r)
                    name_sources.setdefault(r, []).append(path)
            for k, v in obj.items():
                walk(v, f"{path}/{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{path}[{i}]")

    walk(sp)
    return sorted(raw_names), name_sources

def try_resolve(name, canonical_keys, lower_index):
    """
    尝试将 name 解析为规范 key(s)。
    返回 (status, result)，其中:
      status: "exact" | "casefold" | "substring" | "split" | "unresolved"
      result: str | [str, ...]  (单个规范key 或 列表)
    """
    # 1. 精确匹配
    if name in canonical_keys:
        return ("exact", name)

    # 2. 大小写归一化
    ln = name.lower()
    if ln in lower_index:
        matches = lower_index[ln]
        if len(matches) == 1:
            return ("casefold", matches[0])
        else:
            return ("ambiguous_case", matches)

    # 3. 子串匹配 (name包含key 或 key包含name)
    substr_hits = []
    for ck in canonical_keys:
        if ck in name or name in ck:
            substr_hits.append(ck)
    if len(substr_hits) == 1:
        return ("substring", substr_hits[0])
    elif len(substr_hits) > 1:
        return ("ambiguous_substr", substr_hits)

    # 4. 分隔符拆分
    parts = re.split(r'[-·/—]', name)
    if len(parts) > 1:
        resolved_parts = []
        all_ok = True
        for p in parts:
            p = p.strip()
            if not p:
                continue
            status, result = try_resolve(p, canonical_keys, lower_index)
            if status == "unresolved":
                all_ok = False
            if isinstance(result, list):
                resolved_parts.extend(result)
            else:
                resolved_parts.append(result)
        if all_ok and resolved_parts:
            return ("split", resolved_parts)
        elif resolved_parts:
            return ("split_partial", resolved_parts)

    return ("unresolved", None)

def main():
    canonical_keys, lower_index = load_canonical()
    raw_names, sources = extract_situation_regions()

    print(f"规范脑区数: {len(canonical_keys)}")
    print(f"situation_primitives 中独特区域名: {len(raw_names)}")
    print()

    results = {
        "exact": [],
        "casefold": [],
        "substring": [],
        "split": [],
        "split_partial": [],
        "ambiguous_case": [],
        "ambiguous_substr": [],
        "unresolved": [],
    }

    for name in raw_names:
        status, result = try_resolve(name, set(canonical_keys), lower_index)
        results[status].append((name, result, sources.get(name, [])))

    for status in ["exact", "casefold", "substring", "split", "split_partial",
                    "ambiguous_case", "ambiguous_substr", "unresolved"]:
        items = results[status]
        if not items:
            continue
        print(f"--- {status} ({len(items)}个) ---")
        for name, result, ctx in items:
            ctx_preview = ctx[0] if ctx else "?"
            if isinstance(result, list):
                print(f"  {name:30s} → {result}")
            elif result:
                print(f"  {name:30s} → {result}")
            else:
                print(f"  {name:30s} → ⚠️ 未解析")
        print()

    total = len(raw_names)
    resolved = total - len(results["unresolved"]) - len(results["ambiguous_case"]) - len(results["ambiguous_substr"])
    print(f"解析率: {resolved}/{total} ({100*resolved//total}%)")
    print(f"  unambiguous: {len(results['exact']) + len(results['casefold']) + len(results['substring']) + len(results['split'])}")
    print(f"  partially split: {len(results['split_partial'])}")
    print(f"  ambiguous: {len(results['ambiguous_case']) + len(results['ambiguous_substr'])}")
    print(f"  unresolved: {len(results['unresolved'])}")

if __name__ == "__main__":
    main()
