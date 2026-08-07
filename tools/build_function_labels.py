#!/usr/bin/env python3
"""
build_function_labels.py — 从 function_profile 组合推导连接功能语义

读取 tripartite_model.json 中的连接，对每条连接的 source→target，
取 source.output_types ∩ target.input_types（精确字符串匹配，signal_type 受控词表），
推导 function_label 和 gameplay_labels。空交集 → role:silent。

设计依据: Grilling #26 (GitHub #27) D10/D13
  规则/技能树系统/脑功能层级模型.md §二十.8/§二十.9
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent


# ─── 数据加载 ───────────────────────────────────────────────────

def load_model():
    with open(ROOT / "data/connectivity/tripartite_model.json") as f:
        return json.load(f)


def load_signal_types():
    with open(ROOT / "data/signal_types.json") as f:
        return json.load(f)


# ─── 功能标签推导 ──────────────────────────────────────────────

def derive_function_label(source_outputs, target_inputs, signal_types):
    """
    计算 source.output_types ∩ target.input_types。
    返回交集列表。空交集 → role=silent。

    signal_type 受控词表用于查找 subtype 的 human-readable 定义。
    """
    intersection = [sig for sig in source_outputs if sig in target_inputs]

    # 为每个交集信号类型查找定义
    signal_defs = {}
    for cat_name, cat_data in signal_types.get("_categories", {}).items():
        for sub_name, sub_data in cat_data.get("subtypes", {}).items():
            signal_defs[f"{cat_name}/{sub_name}"] = sub_data.get("definition", "")

    labels = []
    for sig in intersection:
        cat, sub = sig.split("/", 1)
        definition = signal_defs.get(sig, "")
        labels.append({
            "signal_type": sig,
            "category": cat,
            "subtype": sub,
            "definition": definition
        })

    return labels


def derive_gameplay_labels(source_domains, target_domains):
    """
    从 source 和 target 的 gameplay_domains 并集中推导连接级 gameplay 标签。
    """
    combined = []
    for d in source_domains:
        if d not in combined:
            combined.append(d)
    for d in target_domains:
        if d not in combined:
            combined.append(d)
    return combined


def describe_connection(source_dk, target_dk, labels, source_domains, target_domains):
    """生成人类可读的连接描述"""
    if not labels:
        return f"{source_dk}→{target_dk}: silent (无功能信号交集)"

    signal_names = [l["subtype"] for l in labels]
    domains = set(source_domains + target_domains)

    # 确定连接方向描述
    description = f"{source_dk}→{target_dk}: 传递 {', '.join(signal_names)}"
    if domains:
        description += f" [{', '.join(sorted(domains))}]"

    return description


# ─── 主处理 ────────────────────────────────────────────────────

def process_connections(model, signal_types):
    """处理所有类型的连接，追加 function_label / gameplay_labels / role"""

    node_profiles = model.get("node_profiles", {})

    # 统计
    stats = {"total": 0, "labeled": 0, "silent": 0, "no_profile": 0}

    # 处理皮层-皮层连接（最需要功能标签的类型）
    for conn in model.get("corticocortical", []):
        stats["total"] += 1
        src = conn["source"]
        tgt = conn["target"]

        src_profile = node_profiles.get(src, {})
        tgt_profile = node_profiles.get(tgt, {})

        src_outputs = src_profile.get("output_types", [])
        tgt_inputs = tgt_profile.get("input_types", [])

        if not src_outputs and not tgt_inputs:
            # 两个节点都没有 profile → 标记
            stats["no_profile"] += 1
            conn["role"] = "unknown"
            conn["function_label"] = []
            conn["gameplay_labels"] = []
            conn["description"] = f"{src}→{tgt}: 缺少功能剖面"
            continue

        labels = derive_function_label(src_outputs, tgt_inputs, signal_types)
        gameplay = derive_gameplay_labels(
            src_profile.get("gameplay_domains", []),
            tgt_profile.get("gameplay_domains", [])
        )

        conn["function_label"] = labels
        conn["gameplay_labels"] = gameplay
        conn["description"] = describe_connection(
            src, tgt, labels,
            src_profile.get("gameplay_domains", []),
            tgt_profile.get("gameplay_domains", [])
        )

        if not labels:
            conn["role"] = "silent"
            stats["silent"] += 1
        else:
            conn["role"] = "active"
            stats["labeled"] += 1

    # 处理 CSTC 连接 — 由环路结构决定语义，但也做信号类型验证
    for conn in model.get("cstc", []):
        stats["total"] += 1
        src = conn["source"]
        tgt = conn["target"]

        src_profile = node_profiles.get(src, {})
        tgt_profile = node_profiles.get(tgt, {})

        src_outputs = src_profile.get("output_types", [])
        tgt_inputs = tgt_profile.get("input_types", [])

        labels = derive_function_label(src_outputs, tgt_inputs, signal_types) if src_outputs else []
        gameplay = derive_gameplay_labels(
            src_profile.get("gameplay_domains", []),
            tgt_profile.get("gameplay_domains", [])
        )

        conn["function_label"] = labels
        conn["gameplay_labels"] = gameplay

        if labels:
            conn["role"] = "active"
            stats["labeled"] += 1
        elif not src_outputs and not tgt_inputs:
            conn["role"] = "unknown"
            stats["no_profile"] += 1
        else:
            # CSTC 连接即使信号交集为空，结构上仍是 active（门控是结构性功能）
            conn["role"] = "active"
            stats["labeled"] += 1

    # 处理脑干广播 — 广播式调制，语义由 neurotransmission 类型决定
    for conn in model.get("brainstem", []):
        stats["total"] += 1
        src = conn["source"]
        tgt = conn["target"]

        src_profile = node_profiles.get(src, {})
        tgt_profile = node_profiles.get(tgt, {})

        src_outputs = src_profile.get("output_types", [])
        tgt_inputs = tgt_profile.get("input_types", [])

        labels = derive_function_label(src_outputs, tgt_inputs, signal_types) if src_outputs else []
        gameplay = derive_gameplay_labels(
            src_profile.get("gameplay_domains", []),
            tgt_profile.get("gameplay_domains", [])
        )

        conn["function_label"] = labels
        conn["gameplay_labels"] = gameplay

        if labels:
            conn["role"] = "active"
            stats["labeled"] += 1
        else:
            # 脑干广播即使信号交集为空也标记为 modulating
            conn["role"] = "modulating"
            stats["labeled"] += 1

    return stats


# ─── 报告 ──────────────────────────────────────────────────────

def report(stats, model):
    """生成标注统计报告"""
    print(f"\n{'=' * 60}")
    print(f"功能标签标注统计")
    print(f"{'=' * 60}")
    total = stats["total"]
    print(f"  总连接:     {total:>5}")
    print(f"  已标注:     {stats['labeled']:>5} ({100*stats['labeled']/total:.0f}%)" if total else "  已标注: 0")
    print(f"  silent:     {stats['silent']:>5}")
    print(f"  无 profile: {stats['no_profile']:>5}")

    # 统计 silent 连接
    silent_cc = [c for c in model.get("corticocortical", []) if c.get("role") == "silent"]
    if silent_cc:
        print(f"\n  Silent 皮层-皮层连接 ({len(silent_cc)}):")
        for c in silent_cc[:5]:
            print(f"    {c['source']} → {c['target']}")
        if len(silent_cc) > 5:
            print(f"    ... +{len(silent_cc)-5} more")

    # 按 gameplay domain 统计
    domain_counts = defaultdict(int)
    for conn_list_name in ["corticocortical", "cstc", "brainstem"]:
        for conn in model.get(conn_list_name, []):
            for d in conn.get("gameplay_labels", []):
                domain_counts[d] += 1

    if domain_counts:
        print(f"\n  Gameplay domain 覆盖:")
        for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
            print(f"    {domain}: {count}")


# ─── 主函数 ─────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("build_function_labels.py — 功能标签推导")
    print("=" * 60)

    # 加载数据
    print("\n[1/3] 加载数据...")
    model = load_model()
    signal_types = load_signal_types()
    print(f"  tripartite_model.json: {len(model.get('graph_nodes', {}))} 节点")
    print(f"  signal_types.json: {len(signal_types['_categories'])} categories")

    # 处理连接
    print("\n[2/3] 推导功能标签...")
    stats = process_connections(model, signal_types)

    # 写入
    print("\n[3/3] 写入...")
    model["_function_labels_applied"] = True
    model["_function_labels_generated_by"] = "tools/build_function_labels.py"
    model["_function_labels_created"] = "2026-08-07"

    output_path = ROOT / "data/connectivity/tripartite_model.json"
    with open(output_path, "w") as f:
        json.dump(model, f, ensure_ascii=False, indent=2)

    print(f"  ✅ 已写入: {output_path}")

    # 报告
    report(stats, model)


if __name__ == "__main__":
    main()
