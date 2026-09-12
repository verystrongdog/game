#!/usr/bin/env python3
"""迁移: situation_primitives.json + personality_tag_links.json 英文化 (A1/D24)

功能:
  1. situation_primitives.json: key_brain_regions 中文名 → functional_id
  2. personality_tag_links.json: core_links 旧数字索引 → 新 link_id 主键
输入: 旧 JSON + region_name_map.json + link_registry.json（新）
输出: 同文件（就地迁移）
"""
import json
import sys


def main():
    with open('data/connectivity/region_name_map.json') as f:
        name_map = json.load(f)['regions']
    with open('data/connectivity/link_registry.json') as f:
        reg = json.load(f)

    # zh → functional_id
    zh2fid = {e['zh_name']: fid for fid, e in name_map.items()}

    # 1. situation_primitives.json
    with open('data/connectivity/situation_primitives.json') as f:
        sit = json.load(f)
    errors = []
    converted = 0
    for s in sit['situation_archetypes']:
        kbr = s.get('key_brain_regions') or []
        new_kbr = []
        for r in kbr:
            fid = zh2fid.get(r)
            if not fid:
                errors.append(f"情境 {s.get('name')}: 脑区 '{r}' 无 functional_id")
                new_kbr.append(r)
            else:
                new_kbr.append(fid)
                converted += 1
        s['key_brain_regions'] = new_kbr
    # auto_activated_links 可能也有旧索引
    for s in sit['situation_archetypes']:
        aal = s.get('auto_activated_links')
        if isinstance(aal, list) and aal and isinstance(aal[0], int):
            # 旧数字索引 → 新主键（顺序对应）
            s['auto_activated_links'] = [reg['links'][i]['id'] if i < len(reg['links']) else f"link_{i}"
                                          for i in aal]
    with open('data/connectivity/situation_primitives.json', 'w') as f:
        json.dump(sit, f, ensure_ascii=False, indent=2)
    print(f"situation_primitives: {converted} 个脑区名转换, 错误 {len(errors)}")

    # 2. personality_tag_links.json
    with open('data/connectivity/personality_tag_links.json') as f:
        ptl = json.load(f)
    # 旧 link_id 索引 = 新 registry 顺序（未重排）
    old2new = {i: l['id'] for i, l in enumerate(reg['links'])}
    tag_errors = []
    for tag, t in ptl['tags'].items():
        core = t.get('core_links') or []
        new_core = []
        for c in core:
            if isinstance(c, int):
                new_core.append(old2new.get(c, f"link_{c}"))
            else:
                new_core.append(c)
        t['core_links'] = new_core
        # collateral_links 类似
        col = t.get('collateral_links') or {}
        if col:
            new_col = {}
            for k, v in col.items():
                if isinstance(k, int):
                    new_col[old2new.get(k, f"link_{k}")] = v
                else:
                    new_col[k] = v
            t['collateral_links'] = new_col
    with open('data/connectivity/personality_tag_links.json', 'w') as f:
        json.dump(ptl, f, ensure_ascii=False, indent=2)
    print(f"personality_tag_links: 6 标签 core_links 迁移完成")

    if errors:
        print(f"\nERROR: {errors}")
        sys.exit(1)


if __name__ == '__main__':
    main()
