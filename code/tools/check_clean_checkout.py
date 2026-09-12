#!/usr/bin/env python3
"""check_clean_checkout.py — 干净检出可解析性检查

问题：受控文件引用了**未受控**（或被 .gitignore 排除）的路径时，本地因残留
文件而通过，干净检出（CI）必然断链。2026-09-12 CI 首跑就因这一类失败。

本脚本把「干净检出可以复现结果」这条判据（WORKFLOW.md §六）变成可执行检查：
  1. 受控 .md 的链接目标，若磁盘存在但**未被 git 跟踪** → 报错
  2. 受控文件里的绝对路径若指向开发机（/home/<user>、/Users/<user>）→ 报错
  3. **悬空 gitlink**（索引里的 160000 条目没有 .gitmodules 登记）→ 报错

第 3 条是 2026-09-12 从 CI 日志里发现后补的（见下）。

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


def dangling_gitlinks():
    """索引里的 gitlink（mode 160000）中，**没有 .gitmodules 登记**的那些。

    ## 为什么要查这个（2026-09-12 实测发现）

    `reference/books/a-philosophy-of-software-design-zh` 自 `b74ff98` 起以 gitlink
    入库（160000 → `ca89b238…`），但**本仓从未有过 `.gitmodules`**
    （`git log --all --diff-filter=AD -- .gitmodules` 为空）。

    后果不是"本地坏了"，而是**本地永远看不出问题**：
      - 干净检出/CI：该路径**不进任何内容**（checkout 只创建 gitlink，不 clone 内容），
        且 `git submodule foreach` 因缺 URL 报 `fatal: No url found for submodule path`
        → exit 128。该报错出现在 checkout 的 post 步骤，**不影响 job 结论**，
        所以只在 annotation 里以 warning 形式出现——极易被当噪声略过
      - 作者本机：嵌套仓库 `.git` 还在，目录非空 → 一切正常

    这正是「干净检出可以复现结果」要防的那类缺陷：**本地有、远端没有、且不报错**。
    故补为一条硬检查，而不是只修那一处。
    """
    out = subprocess.run(['git', 'ls-files', '-s'], capture_output=True, text=True).stdout
    gitlinks = [l.split('\t', 1)[1] for l in out.split('\n')
                if l.startswith('160000') and '\t' in l]
    if not gitlinks:
        return []
    mod = ''
    if os.path.exists('.gitmodules'):
        mod = open('.gitmodules', encoding='utf-8').read()
    return [g for g in gitlinks if f'path = {g}' not in mod and f'"{g}"' not in mod]


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

    # 3) 悬空 gitlink
    dangling = dangling_gitlinks()

    print(f"检查 {len(tracked)} 个受控文件")
    print(f"  未受控引用: {n_link} 处")
    print(f"  代码中的开发机绝对路径: {n_abs} 处")
    print(f"  悬空 gitlink（无 .gitmodules 登记）: {len(dangling)} 处")
    print(f"  文档/数据中的出处引用（提示，不算失败）: {len(warns)} 处")
    if warns:
        print()
        for f, i, why in warns[:20]:
            print(f"  ⚠️  {f}:{i} — {why}")
    if dangling:
        print()
        for g in dangling:
            print(f"  ❌ 悬空 gitlink: {g} — 干净检出该路径为空，"
                  f"且 git submodule 操作会报 'No url found'")
        print("     修法：要么登记 .gitmodules（真子模块），"
              "要么 `git rm --cached <path>` 改为普通文件或忽略")
    if bad or dangling:
        print()
        for f, i, why in bad[:40]:
            print(f"  ❌ {f}:{i} — {why}")
        print(f"\n❌ 干净检出会失败（未受控引用 {len(bad)} 处 · 悬空 gitlink {len(dangling)} 处）")
        return 1
    print("\n✅ 干净检出可完全解析")
    return 0


if __name__ == '__main__':
    sys.exit(main())
