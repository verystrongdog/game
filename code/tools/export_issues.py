#!/usr/bin/env python3
"""export_issues.py — 把 GitHub issue 导出为 markdown 归档

Phase 4.5：grilling 停用后，122 个 issue（106 关闭 / 16 开放）是唯一的
决策过程记录，必须落盘留存，否则 GitHub 上的历史与本仓脱钩。

产出：design/archive/grilling/issues/
  ├── README.md            索引（编号 / 标题 / 状态 / 标签 / 链接）
  └── <NNN>-<slug>.md      每 issue 一份（正文 + 评论）

用法：
    python3 code/tools/export_issues.py [--limit N] [--dry-run]

依赖：gh（已认证）。来源: REFACTOR-PLAN.md §六 Phase 4.5
"""

import argparse
import json
import os
import re
import subprocess
import sys

OUT_DIR = 'design/archive/grilling/issues'
REPO = 'verystrongdog/game'


def slugify(title: str, maxlen: int = 40) -> str:
    """标题 → 文件名片段。保留中文（项目文档为中文），去掉路径不安全字符。"""
    s = re.sub(r'[\\/:*?"<>|\s]+', '-', title.strip())
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s[:maxlen].rstrip('-')


def gh(args: list, timeout: int = 120) -> str:
    r = subprocess.run(['gh'] + args, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:200])
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=500)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    print("拉取 issue 列表…")
    raw = gh(['issue', 'list', '--state', 'all', '--limit', str(args.limit),
              '--json', 'number,title,state,labels,body,createdAt,closedAt,url'])
    issues = json.loads(raw)
    issues.sort(key=lambda x: x['number'])
    print(f"共 {len(issues)} 个 issue")

    if not args.dry_run:
        os.makedirs(OUT_DIR, exist_ok=True)

    index = ['# Grilling Issue 归档',
             '',
             '> 122 个 GitHub issue 的落盘存档（106 关闭 / 16 开放）。'
             'grilling 流程已停用，本目录是决策过程的**只读历史**。',
             '',
             '> **性质**：归档。活跃文档不得把本目录当作设计依据——'
             '要引用结论请引用 `design/` 下的正典，或 `design/decisions/` 对应条目。',
             '',
             '> **来源**：`gh issue list` 导出（2026-09-12）。'
             f'原始 issue 仍在 <https://github.com/{REPO}/issues> 可查。',
             '',
             '---',
             '',
             '| # | 标题 | 状态 | 标签 |',
             '|---|------|------|------|']
    n_ok = n_fail = 0

    for it in issues:
        num, title = it['number'], it['title']
        labels = ', '.join(l['name'] for l in it['labels'])
        state_cn = '开放' if it['state'] == 'OPEN' else '关闭'
        fname = f"{num:03d}-{slugify(title)}.md"
        index.append(f"| [{num}]({fname}) | {title} | {state_cn} | {labels} |")

        if args.dry_run:
            continue
        try:
            detail = json.loads(gh(['issue', 'view', str(num),
                                    '--json', 'comments']))
        except Exception as e:
            print(f"  ⚠️ #{num} 评论拉取失败: {e}")
            detail = {'comments': []}
            n_fail += 1

        body = (it.get('body') or '').strip()
        lines = [f"# #{num} {title}", '',
                 f"> 状态：{state_cn} · 创建 {it['createdAt'][:10]}"
                 + (f" · 关闭 {it['closedAt'][:10]}" if it.get('closedAt') else ''),
                 f"> 标签：{labels or '（无）'}",
                 f"> 原始：{it['url']}",
                 '',
                 '> **归档**：grilling 流程已停用，本文是只读历史记录。',
                 '', '---', '', '## 正文', '', body or '（无正文）', '']
        comments = detail.get('comments', [])
        if comments:
            lines += ['---', '', f'## 评论（{len(comments)} 条）', '']
            for c in comments:
                who = (c.get('author') or {}).get('login', '?')
                when = (c.get('createdAt') or '')[:10]
                cb = (c.get('body') or '').strip()
                lines += [f'### {who} · {when}', '', cb or '（空）', '']
        lines += ['---', '*导出: 2026-09-12 | 来源: GitHub issue*', '']
        with open(os.path.join(OUT_DIR, fname), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        n_ok += 1
        if n_ok % 20 == 0:
            print(f"  已导出 {n_ok}/{len(issues)}")

    index += ['', '---', '*导出: 2026-09-12*', '']
    if not args.dry_run:
        with open(os.path.join(OUT_DIR, 'README.md'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(index))
    print(f"\n完成：导出 {n_ok} · 评论失败 {n_fail}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
