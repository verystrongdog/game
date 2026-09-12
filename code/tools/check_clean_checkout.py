#!/usr/bin/env python3
"""check_clean_checkout.py — 干净检出可解析性检查

问题：受控文件引用了**未受控**（或被 .gitignore 排除）的路径时，本地因残留
文件而通过，干净检出（CI）必然断链。2026-09-12 CI 首跑就因这一类失败。

本脚本把「干净检出可以复现结果」这条判据（WORKFLOW.md §六）变成可执行检查：
  1. 受控 .md 的链接目标，若磁盘存在但**未被 git 跟踪** → 报错
  2. 受控文件里的绝对路径若指向开发机（/home/<user>、/Users/<user>）→ 报错

用法: python3 code/tools/check_clean_checkout.py
退出码: 0 = 通过, 1 = 有未受控引用
"""
import os
import re
import subprocess
import sys
import urllib.parse

LINK = re.compile(r'\]\(([^)]+)\)')
MACHINE_ABS = re.compile(r'(/home/[A-Za-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/|C:\\\\Users\\\\[^\\\\]+)')

# 归档代码不参与运行 → 其中的机器路径属历史痕迹，不报错
# （reference/deprecated/ 是"保留为参考数据源"的已废弃子系统；
#   design/archive/ 是 grilling 源记录与垃圾箱）
ARCHIVE_PREFIX = ('reference/deprecated/', 'design/archive/')
SKIP_EXT = ('.png', '.jpg', '.pdf', '.fbx', '.blend', '.glb', '.obj', '.npy', '.csv')


def tracked_files():
    out = subprocess.run(['git', '-c', 'core.quotePath=false', 'ls-files'],
                         capture_output=True, text=True).stdout
    return {l for l in out.split('\n') if l}


def main():
    tracked = tracked_files()
    n_link = n_abs = 0
    bad, warns = [], []
    for f in sorted(tracked):
        if not f.endswith(('.md', '.cs', '.py', '.json')):
            continue
        try:
            txt = open(f, encoding='utf-8').read()
        except Exception:
            continue
        # 1) 未受控的链接目标
        if f.endswith('.md'):
            for i, line in enumerate(txt.splitlines(), 1):
                for m in LINK.finditer(line):
                    tg = m.group(1).strip()
                    if tg.startswith(('http', 'mailto', '#', '/')):
                        continue
                    pa = tg.partition('#')[0]
                    if not pa:
                        continue
                    r = os.path.normpath(os.path.join(
                        os.path.dirname(f), urllib.parse.unquote(pa)))
                    if not os.path.isfile(r):
                        continue                     # 不存在 → 由 validate_cross_refs 报
                    if r not in tracked:
                        bad.append((f, i, f'未受控目标: {pa}'))
                        n_link += 1
        # 2) 开发机绝对路径
        #
        # 区分两类（2026-09-12）：
        #   - **代码**（.cs/.py）里的机器绝对路径 = 运行时依赖作者机器 → 错误
        #   - **文档/数据**里的是"出处引用"（某文献来自某下载目录、某结论据某路径核查）
        #     → 提示。它们不参与运行，且记录了真实来源，不应删除
        for i, line in enumerate(txt.splitlines(), 1):
            if not MACHINE_ABS.search(line):
                continue
            if f.endswith(('.cs', '.py')):
                if f.startswith(ARCHIVE_PREFIX):
                    continue          # 归档代码，不参与运行
                bad.append((f, i, f'代码中的开发机绝对路径: {line.strip()[:90]}'))
                n_abs += 1
            else:
                warns.append((f, i, f'文档/数据中的出处引用: {line.strip()[:80]}'))

    print(f"检查 {len(tracked)} 个受控文件")
    print(f"  未受控引用: {n_link} 处")
    print(f"  代码中的开发机绝对路径: {n_abs} 处")
    print(f"  文档/数据中的出处引用（提示，不算失败）: {len(warns)} 处")
    if warns:
        print()
        for f, i, why in warns[:20]:
            print(f"  ⚠️  {f}:{i} — {why}")
    if bad:
        print()
        for f, i, why in bad[:40]:
            print(f"  ❌ {f}:{i} — {why}")
        print(f"\n❌ 干净检出会失败（共 {len(bad)} 处）")
        return 1
    print("\n✅ 干净检出可完全解析")
    return 0


if __name__ == '__main__':
    sys.exit(main())
