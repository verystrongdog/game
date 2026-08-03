#!/usr/bin/env python3
"""迁移疾病目录: 功能域配置表 → 链路配置表 (D2/D27)

功能:
  1. 功能域配置表 → 链路配置表（去"域"列）
  2. 链路 ID: 中文链路名 → 新数字主键（link_000_L 格式，D27）
  3. CGI-S 域扩展表 → 链路分组表（保留结构，域→链路分组语义，2026-08-03）
  4. 父类 frontmatter: 去功能域定性方向（保留默认病理类型/默认标签）

输入: 实体/疾病目录/*.md + link_name_lookup.json + link_registry.json
输出: 同文件（就地迁移）
"""
import json
import re
import sys
from pathlib import Path

DISEASE_DIR = Path('实体/疾病目录')


def main():
    with open('data/connectivity/link_name_lookup.json') as f:
        lookup = json.load(f)
    with open('data/connectivity/link_registry.json') as f:
        reg = json.load(f)

    # 中文链路名 → 新主键（无侧向名 → 匹配同前缀的所有新 id）
    name2ids = {}
    for zh, old_id in lookup.items():
        matches = [l['id'] for l in reg['links'] if l['id'].startswith(old_id)]
        name2ids[zh] = matches

    def resolve(link_name):
        """中文链路名 → 新主键（单个或无侧向→全部；有侧向→精确）"""
        name = link_name.strip()
        if name in name2ids:
            ids = name2ids[name]
            return ids[0] if len(ids) == 1 else ','.join(ids)
        # 可能已是新主键
        return name

    files = sorted(DISEASE_DIR.glob('*.md'))
    for f in files:
        if f.name.startswith('_'):
            continue
        text = f.read_text(encoding='utf-8')

        # 1+2. 功能域配置表区域: 表头改名 + 去"域"列 + 链路名 → 主键（仅处理该区域）
        def fix_func_rows(t):
            # 定位 "## 功能域配置" 到下一个 "## " 之间的区域
            def replace_region(m):
                region = m.group(1)
                # 先替换表头
                region = region.replace('| 域 | 链路ID | 病理类型 | m偏移(轻/中/重) |',
                                        '| 链路ID | 病理类型 | m偏移(轻/中/重) |')
                # 再替换数据行（4 列：域 | 链路ID | 病理类型 | m偏移 → 3 列）
                region = re.sub(
                    r'^\| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|\s*$',
                    lambda m: f'| {resolve(m.group(2))} | {m.group(3)} | {m.group(4)} |',
                    region, flags=re.MULTILINE,
                )
                return '## 链路配置' + region
            return re.sub(r'## 功能域配置\n(.*?)(?=\n## |\Z)', replace_region, t, flags=re.DOTALL)

        text = fix_func_rows(text)

        # 3. CGI-S 域扩展表: 表头"核心域/关联域/边缘域" → "核心链路/关联链路/边缘链路"（列名保留，域名暂不迁移——链路段落含域名）
        #   注意: 域扩展表的值是"域名"（防御/记忆...），迁移为链路分组语义需保留域名文本，仅改列名
        text = text.replace('## CGI-S 域扩展', '## CGI-S 链路扩展')
        text = text.replace('| 严重度 | 核心域 | 关联域 | 边缘域 | m倍率(参考) | 域数合计 |',
                            '| 严重度 | 核心链路 | 关联链路 | 边缘链路 | m倍率(参考) | 链路数合计 |')

        f.write_text(text, encoding='utf-8')
        print(f"  {f.name}: 迁移完成")

    # 4. 父类 frontmatter: 去功能域定性方向
    for f in sorted((DISEASE_DIR / '_父类').glob('*.md')):
        text = f.read_text(encoding='utf-8')
        # 去掉 frontmatter 中的功能域定性方向块
        text = re.sub(r'功能域定性方向:\n(?:  [^\n]+\n)*', '', text)
        # 正文标题
        text = text.replace('## 功能域定性方向', '## 神经回路定性方向（链路级）')
        f.write_text(text, encoding='utf-8')
        print(f"  _父类/{f.name}: 迁移完成")


if __name__ == '__main__':
    main()
