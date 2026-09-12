#!/usr/bin/env python3
"""rename_regions.py — 旧中文名 → functional_id 迁移工具 (批次1第6步)

功能: 扫描 md/yaml 文件中的旧中文脑区名，替换为 functional_id
输入: 目标文件列表 + region_name_map.json
输出: 迁移报告（每个文件改了多少处、未命中清单）

用法: python3 code/tools/rename_regions.py <文件或目录...>
"""
import json
import re
import sys
from pathlib import Path


def load_name_map():
    with open('data/connectivity/region_name_map.json') as f:
        return json.load(f)['regions']


def main():
    name_map = load_name_map()
    # 旧中文名 → functional_id（按长度降序避免子串误替换）
    zh2fid = sorted(
        [(e['zh_name'], fid) for fid, e in name_map.items()],
        key=lambda x: len(x[0]), reverse=True,
    )

    if len(sys.argv) < 2:
        print("用法: python3 code/tools/rename_regions.py <文件或目录...>")
        sys.exit(1)

    total = {'changed': 0, 'files': 0, 'misses': {}}
    for arg in sys.argv[1:]:
        path = Path(arg)
        files = [path] if path.is_file() else list(path.rglob('*.md')) + list(path.rglob('*.yaml')) + list(path.rglob('*.yml'))
        for f in files:
            if '垃圾桶' in str(f) or '.scratch' in str(f):
                continue
            text = f.read_text(encoding='utf-8')
            orig = text
            hits = 0
            for zh, fid in zh2fid:
                # 只替换独立出现（前后非中文/字母），避免破坏 display_name 等含链路的文本
                pattern = re.compile(rf'(?<![A-Za-z一-鿿]){re.escape(zh)}(?![A-Za-z一-鿿])')
                new_text, n = pattern.subn(fid, text)
                if n:
                    hits += n
                    text = new_text
            if hits:
                f.write_text(text, encoding='utf-8')
                total['changed'] += hits
                total['files'] += 1
                print(f"  {f}: {hits} 处替换")
    print(f"\n迁移报告: {total['files']} 文件, {total['changed']} 处替换, 未命中 {total['misses']}")


if __name__ == '__main__':
    main()
