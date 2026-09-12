#!/usr/bin/env python3
"""重构 brain_regions.json — functional_id 主键 + zh_name + is_design_node (D13/D25)

功能: 将 brain_regions.json 的 key 从中文名改为 functional_id（英文唯一主键），
     中文名降为 zh_name 字段，补充 is_design_node 标记
输入: data/brain_regions.json + data/connectivity/region_name_map.json
输出: data/brain_regions.json（重构，key = functional_id）
"""
import json
import sys


def main():
    with open('data/brain_regions.json') as f:
        data = json.load(f)
    with open('data/connectivity/region_name_map.json') as f:
        name_map = json.load(f)['regions']

    old_regions = data['regions']
    new_regions = {}

    for zh, r in old_regions.items():
        # 找 functional_id
        fid = None
        for e in name_map.values():
            if e['zh_name'] == zh:
                fid = e['functional_id']
                break
        if not fid:
            print(f"ERROR: {zh} 无 functional_id")
            sys.exit(1)

        entry = {
            'zh_name': zh,  # 中文显示名（降为字段）
            'functional_id': fid,
            'std_name': r.get('std_name'),
            'dk_name': r.get('bfb_region'),  # bfb_region → dk_name
            'category': r.get('category'),
            'lobe': r.get('lobe'),
            'level': r.get('level'),
            'is_design_node': zh in [e['zh_name'] for e in name_map.values() if e['is_design_node']],
            'mni_xyz': r.get('mni_xyz'),
            'mni_xyz_source': r.get('mni_xyz_source'),
            'game_xyz': r.get('game_xyz'),
            'fs_xyz': r.get('fs_xyz'),
            'obj_file': r.get('obj_file'),
            'notes': r.get('notes'),
        }
        # 左右脑干（蓝斑_R）标记 hemisphere
        if zh.endswith('_R'):
            entry['hemisphere'] = 'R'
        new_regions[fid] = entry

    out = {
        '_description': '50 解剖实体（70 条目）— functional_id 主键 (D25/D13)',
        '_coordinate_system': data.get('_coordinate_system'),
        'regions': new_regions,
    }
    with open('data/brain_regions.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(new_regions)} 脑区 → brain_regions.json（key=functional_id）")
    print(f"   is_design_node: {sum(1 for r in new_regions.values() if r['is_design_node'])}")


if __name__ == '__main__':
    main()
