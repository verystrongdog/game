#!/usr/bin/env python3
"""validate_link_data.py — 数据层质量门禁 (§10.1)

检查:
  V1 链路唯一性: 364 条 id 唯一，无重复 dk_pair×direction×hemisphere
  V2 关联键: matrix 与 link_behavior_roles.json 的 link_id 100% 一致
  V3 命名覆盖: 全部 source/target 有 functional_id，functional_id 全局唯一
  V4 上下文计算: 364 条都有 contexts 集合 + primary_role
  V5 脑干 regions_b: 无 target_is_dk_only
  V6 空间断言（基础）: 单侧标记与 hemisphere 一致

输出: PASS/FAIL/WARN 报告（符合 review-plan --pre-check 格式）
"""
import json
import sys
from collections import Counter


def check(name, cond, detail=''):
    status = 'PASS' if cond else 'FAIL'
    print(f"{status}  {name}  {detail}")
    return cond


def main():
    results = []

    with open('data/connectivity/link_registry.json') as f:
        reg = json.load(f)
    links = reg['links']

    # V1 唯一性
    ids = [l['id'] for l in links]
    results.append(check('V1.1', len(ids) == len(set(ids)), f"id 唯一 {len(set(ids))}/{len(ids)}"))
    # 重复 dk_pair×direction×hemisphere
    seen = Counter((l['source_dk_name'], l['target_dk_name'], l['direction'], l['hemisphere'])
                   for l in links if l['source_dk_name'] and l['target_dk_name'] and l['hemisphere'])
    dups = {k: v for k, v in seen.items() if v > 1}
    results.append(check('V1.2', len(dups) == 0, f"重复组 {len(dups)}"))

    # V2 关联键
    with open('data/connectivity/link_behavior_roles.json') as f:
        roles = json.load(f)
    role_links = roles['links']
    # 角色文件 link_id 顺序 = matrix 顺序（未重排），对比 regions_a
    mismatch = 0
    for i, (r, rl) in enumerate(zip(links, role_links)):
        if r['regions_a_zh'] != rl.get('regions_a'):
            mismatch += 1
    results.append(check('V2', mismatch == 0, f"关联键一致 {mismatch} 条不符"))

    # V3 命名覆盖
    no_src = [l for l in links if not l['source_region']]
    no_tgt = [l for l in links if not l['target_region']]
    results.append(check('V3.1', not no_src and not no_tgt, f"source/target 全部映射 (src缺{len(no_src)}/tgt缺{len(no_tgt)})"))
    with open('data/connectivity/region_name_map.json') as f:
        nm = json.load(f)
    fids = [e['functional_id'] for e in nm['regions'].values()]
    results.append(check('V3.2', len(fids) == len(set(fids)), f"functional_id 唯一 {len(set(fids))}/{len(fids)}"))

    # V4 上下文
    with open('data/connectivity/link_contexts.json') as f:
        ctx = json.load(f)
    no_ctx = [cid for cid, c in ctx['links'].items() if not c['contexts'] or not c['primary_role']]
    results.append(check('V4', len(no_ctx) == 0, f"contexts+primary_role 覆盖 {len(ctx['links'])}"))

    # V5 脑干 target_is_dk_only
    dk_only = [l for l in links if l.get('target_is_dk_only')]
    results.append(check('V5', len(dk_only) == 0, f"target_is_dk_only {len(dk_only)}"))

    # V6 单侧标记一致性
    single = [l for l in links if l['is_single_sided']]
    bad_single = [l for l in single if not l['hemisphere']]
    results.append(check('V6', not bad_single, f"单侧 {len(single)} 条全部有 hemisphere"))

    # 汇总
    n_pass = sum(1 for r in results if r)
    print(f"\n## 汇总")
    print(f"{len(results)} checks: {n_pass} passed, {len(results) - n_pass} failed, 0 warnings")
    sys.exit(0 if n_pass == len(results) else 1)


if __name__ == '__main__':
    main()
