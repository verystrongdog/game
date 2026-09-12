#!/usr/bin/env python3
"""修复疾病文件结算表中的中文链路名 → 新主键 (D27)

功能: 非线性跳变表/行为覆盖表/组件掉落池表中的链路引用
      从中文链路名转换为新数字主键
输入: design/entities/diseases/*.md + link_name_lookup.json + link_registry.json
输出: 同文件（就地迁移）
"""
import json
import re
from pathlib import Path

DISEASE_DIR = Path('design/entities/疾病目录')


def main():
    with open('data/connectivity/link_name_lookup.json') as f:
        lookup = json.load(f)
    with open('data/connectivity/link_registry.json') as f:
        reg = json.load(f)

    # 中文链路名 → 新主键（精确）
    name2id = {}
    for zh, old_id in lookup.items():
        matches = [l['id'] for l in reg['links'] if l['id'].startswith(old_id)]
        if matches:
            name2id[zh] = matches[0]

    # 按名称长度降序（长名先替换避免子串）
    names = sorted(name2id.keys(), key=len, reverse=True)

    files = sorted(DISEASE_DIR.glob('*.md'))
    total = 0
    for f in files:
        if f.name.startswith('_'):
            continue
        text = f.read_text(encoding='utf-8')

        # 只处理结算表区域: 非线性跳变 / 行为覆盖 / 组件掉落池 之后的表格行
        # 这些表格行特征是: 行内包含中文链路名且不在叙述段落
        # 策略: 在表格行(以 | 开头)中替换, 叙述段(不以 | 开头)不动
        def replace_in_table_rows(t):
            def fix_line(line):
                if not line.startswith('|'):
                    return line
                for zh in names:
                    if zh in line:
                        line = line.replace(zh, name2id[zh])
                return line
            return '\n'.join(fix_line(l) for l in t.split('\n'))

        new_text = replace_in_table_rows(text)
        if new_text != text:
            f.write_text(new_text, encoding='utf-8')
            total += 1
            print(f"  {f.name}: 表格行链路名转换")

    print(f"\n完成: {total} 文件表格行转换")


if __name__ == '__main__':
    main()
