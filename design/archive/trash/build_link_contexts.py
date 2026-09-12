#!/usr/bin/env python3
"""生成 link_contexts.json — 链路 → 上下文集合映射 (D17/D18/D23)

功能: 联合上下文 = 网络集合归属 × 主导角色
  networks(link)   = coactivated_networks（集合归属，多网络链路属多个上下文）
  primary_role     = role_scores 中得分最高的角色
  contexts(link)   = {(network, primary_role) for network in networks(link)}
  primary_network  = coactivated_networks[0]（染色主色/候选池标签）
输入: link_registry.json（新）+ link_behavior_roles.json
输出: data/connectivity/link_contexts.json
"""
import json
import sys


def main():
    with open('data/connectivity/link_registry.json') as f:
        reg = json.load(f)
    with open('data/connectivity/link_behavior_roles.json') as f:
        roles_data = json.load(f)

    # 角色文件按数组顺序与 matrix 对应——但 link_id 已重建，需按 enigma_labels 匹配
    # 先看角色文件的 link_id 与 matrix 的隐式对应是否仍在（矩阵未改顺序）
    reg_links = reg['links']
    role_links = roles_data['links']
    print(f"registry: {len(reg_links)}, roles: {len(role_links)}")

    # 匹配策略: 角色文件 link_id 是 0-363 数组顺序 = 原 matrix 顺序 = 新 registry 顺序（未重排）
    # 验证: 对比 regions_a 前 5 条
    for i in range(5):
        r = reg_links[i]
        rl = role_links[i]
        match = r['regions_a_zh'] == rl.get('regions_a')
        print(f"  [{i}] registry={r['regions_a_zh']} roles={rl.get('regions_a')} → {'✅' if match else '❌'}")

    # 构建: link_id (新主键) → contexts
    contexts = {}
    errors = 0
    for i, (r, rl) in enumerate(zip(reg_links, role_links)):
        if r['regions_a_zh'] != rl.get('regions_a'):
            errors += 1
            continue
        nets = r.get('coactivated_networks') or []
        scores = rl.get('role_scores') or {}
        primary_role = max(scores, key=scores.get) if scores else None
        ctx_set = {(n, primary_role) for n in nets if primary_role}
        contexts[r['id']] = {
            'networks': nets,
            'primary_role': primary_role,
            'primary_network': r.get('primary_network'),
            'contexts': sorted([list(c) for c in ctx_set]),
        }

    if errors:
        print(f"ERROR: {errors} 条对应不一致")
        sys.exit(1)

    out = {
        '_description': '链路 → 上下文集合映射 (D17/D23) — 集合归属 × 主导角色',
        '_rules': [
            'contexts = {(network, primary_role) for network in coactivated_networks}',
            'primary_network = coactivated_networks[0]（仅染色主色/候选池标签）',
            'primary_role = role_scores 最高分角色',
        ],
        'links': contexts,
    }
    with open('data/connectivity/link_contexts.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(contexts)} 条 → link_contexts.json")

    # 统计候选技能池规模
    from collections import Counter
    pool = Counter()
    for cid, c in contexts.items():
        for ctx in c['contexts']:
            pool[tuple(ctx)] += 1
    valid = {k: v for k, v in pool.items() if v >= 2}
    print(f"上下文组合: {len(pool)} | ≥2 链路（候选技能）: {len(valid)}")
    print(f"样例: {list(valid.items())[:8]}")


if __name__ == '__main__':
    main()
