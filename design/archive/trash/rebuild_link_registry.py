#!/usr/bin/env python3
"""重构 link_registry.json — 显式主键 + functional_id + primary_network (D24/D10/D23/D25)

功能: 从 link_legitimacy_matrix.json 重建 registry:
  - id: link_NNN_L/R 显式主键（D24，同时写入 link_behavior_roles.json）
  - source_region/target_region: functional_id（D25 三层 ID）
  - source_dk_name/target_dk_name: DK 解剖映射
  - hemisphere: L/R + is_single_sided（20 条真实单侧）
  - primary_network = coactivated_networks[0]（D23）
  - display_name_zh 保留中文（显示层）
输入: data/connectivity/link_legitimacy_matrix.json + region_name_map.json
输出: data/connectivity/link_registry.json（重构）
"""
import json
import sys
from collections import defaultdict

def zh_to_fid(region_name, name_map):
    """中文名 → functional_id（含别名处理）"""
    for fid, e in name_map.items():
        if e['zh_name'] == region_name:
            return fid
    return None


def main():
    with open('data/connectivity/link_legitimacy_matrix.json') as f:
        matrix = json.load(f)
    with open('data/connectivity/region_name_map.json') as f:
        name_map = json.load(f)['regions']

    links = matrix['links']
    errors = []
    new_links = []
    id_counter = 0

    # 预处理: 按 dk_pair+direction 分组（判断左右成对/单侧/自连）
    groups = defaultdict(list)
    for idx, l in enumerate(links):
        dp = l.get('dk_pair')
        key = (tuple(dp or []), l.get('direction'))
        groups[key].append(idx)

    # 侧向判定
    def get_sides(l):
        sides = set()
        for e in l.get('enigma_labels') or []:
            if e.startswith('L_'):
                sides.add('L')
            elif e.startswith('R_'):
                sides.add('R')
        return sides

    # 逐条生成新 id
    for idx, l in enumerate(links):
        dp = l.get('dk_pair')
        sides = get_sides(l)
        if not dp:  # 脑干 + manual_curation
            # 无侧向: 检查是否与同组其他链路配对（manual 杏仁核-海马成对出现）
            hemi = None
        else:
            hemi = sorted(sides)[0] if len(sides) == 1 else None

        # 找同组（同 dk_pair 同方向）判断单侧
        key = (tuple(dp or []), l.get('direction'))
        group = groups.get(key, [idx])
        group_sides = set()
        for gi in group:
            group_sides |= get_sides(links[gi])
        is_single = len(group_sides) == 1

        # 分配 id
        if hemi:
            new_id = f"link_{id_counter:03d}_{hemi}"
        elif is_single and group_sides:
            new_id = f"link_{id_counter:03d}_{sorted(group_sides)[0]}"
        elif dp and dp[0] == dp[1]:  # 自连 L↔R
            new_id = f"link_{id_counter:03d}_LR"
        else:
            new_id = f"link_{id_counter:03d}"
        id_counter += 1

        # functional_id 转换
        def map_region(r):
            fid = zh_to_fid(r, name_map)
            if not fid:
                errors.append(f"link[{idx}] 脑区 '{r}' 无 functional_id 映射")
                return None, None
            return fid, name_map[fid].get('dk_name')

        # 源/靶: 优先 regions_a[0]（或脑干 brainstem_nucleus）
        ra = l.get('regions_a') or []
        rb = l.get('regions_b') or []
        src_zh = ra[0] if ra else (l.get('brainstem_nucleus') or '')
        tgt_zh = rb[0] if rb else (l.get('dk_target') or '')
        # dk_target 是英文小写 → 尝试反向映射（dk_name → functional_id）
        src_fid, src_dk = map_region(src_zh)
        tgt_fid, tgt_dk = None, None
        # dk_target 特殊映射（英文小写 → functional_id）
        DK_TARGET_MAP = {
            'accumbens': 'NucleusAccumbens',
            'hypothalamus': 'Hypothalamus',
            'septum': 'SeptalRegion',
            'thalamus': 'Thalamus',
            # dk_name 一对多时选主条目（functional_id 与 zh_name 同义）
            'amygdala': 'Amygdala',
            'caudate': 'Caudate',
            'hippocampus': 'HippocampusCA1',
            'putamen': 'Putamen',
            'caudalanteriorcingulate': 'AnteriorCingulateCortex',
            'medialorbitofrontal': 'MedialOrbitalPrefrontalVMPFC',
            'rostralmiddlefrontal': 'RostralMiddleFrontalDLPFC',
            'superiorfrontal': 'SuperiorFrontalMPFC',
        }
        if tgt_zh:
            if tgt_zh in [e['zh_name'] for e in name_map.values()]:
                tgt_fid, tgt_dk = map_region(tgt_zh)
            elif tgt_zh.lower() in DK_TARGET_MAP:
                fid = DK_TARGET_MAP[tgt_zh.lower()]
                tgt_fid = fid
                tgt_dk = name_map[fid]['dk_name']
            else:
                # 兜底: dk_name 匹配（仅 1:1 时取，一对多取主条目）
                matches = [fid for fid, e in name_map.items()
                           if e['dk_name'] and e['dk_name'].lower() == tgt_zh.lower()]
                if len(matches) == 1:
                    tgt_fid, tgt_dk = matches[0], tgt_zh
                elif matches:
                    # 一对多: 取 zh_name 与 dk_name 同源的（PascalCase 化后相等）
                    pascal = ''.join(w.capitalize() for w in tgt_zh.replace('-', ' ').split())
                    for fid in matches:
                        if name_map[fid]['zh_name'].replace(' ', '') == pascal:
                            tgt_fid, tgt_dk = fid, tgt_zh
                            break
                if not tgt_fid:
                    # 无映射: 保留原样标记 target_is_dk_only
                    tgt_fid = None
                    tgt_dk = tgt_zh

        # primary_network
        nets = l.get('coactivated_networks') or []
        primary_net = nets[0] if nets else None

        entry = {
            'id': new_id,
            'display_name_zh': None,  # 由旧 registry 的 display_name 填充（见下文合并）
            'source_region': src_fid,
            'source_dk_name': src_dk,
            'target_region': tgt_fid,
            'target_dk_name': tgt_dk,
            'target_is_dk_only': tgt_fid is None,
            'hemisphere': hemi,
            'hemisphere_pair': 'L→R' if dp and dp[0] == dp[1] else None,
            'is_single_sided': is_single and len(group_sides) == 1,
            'layers': l.get('layers'),
            'direction': l.get('direction'),
            'primary_network': primary_net,
            'coactivated_networks': nets,
            'data_source': l.get('source') or ('enigma' if dp else 'brainstem'),
            'enigma_strength': l.get('enigma_strength'),
            'fc_strength': l.get('fc_strength'),
            'pathway': l.get('pathway'),
            'ref': l.get('ref'),
            'regions_a_zh': ra,
            'regions_b_zh': rb,
        }
        new_links.append(entry)

    if errors:
        for e in errors[:20]:
            print(f"ERROR: {e}")
        print(f"共 {len(errors)} 个错误")
        sys.exit(1)

    # 合并旧 display_name（中文显示名保留）
    with open('data/connectivity/link_registry.json') as f:
        old_reg = json.load(f)
    old_names = [l.get('display_name') for l in old_reg['links']]
    for i, e in enumerate(new_links):
        if i < len(old_names):
            e['display_name_zh'] = old_names[i]

    out = {
        '_description': '统一链路注册表 — 364 条链路的显式主键和三层 ID (D24/D25/D23)',
        '_generated_from': 'data/connectivity/link_legitimacy_matrix.json + region_name_map.json',
        '_stats': {
            'total': len(new_links),
            'single_sided': sum(1 for l in new_links if l['is_single_sided']),
            'hemisphere_pair': sum(1 for l in new_links if l['hemisphere_pair']),
            'target_is_dk_only': sum(1 for l in new_links if l['target_is_dk_only']),
        },
        'links': new_links,
    }
    with open('data/connectivity/link_registry.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(new_links)} 条 → link_registry.json")
    print(f"   单侧: {out['_stats']['single_sided']}, 自连: {out['_stats']['hemisphere_pair']}, target_is_dk_only: {out['_stats']['target_is_dk_only']}")


if __name__ == '__main__':
    main()
