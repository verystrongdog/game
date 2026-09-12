#!/usr/bin/env python3
"""rewrite_refs.py — 路径迁移后的引用重写

配合 migrate_paths.py 使用。两类改写：

1. **markdown 链接**：在【旧位置】解析目标 → 经新旧路径映射 → 从【新位置】
   重算相对路径。深度变化、目录改名、单文件改名都能正确处理。
2. **裸文本 / 反引号 / 代码注释中的路径**：按前缀表做替换，并施加**词边界守卫**。

### 两个必须避免的坑（本脚本第一版踩过，2026-09-12）

- **过度匹配**：不加词边界会把「Blender管线/HTML原型」「医院建筑参考/Blender场景」
  里的「管线/」「参考/」当成仓库路径，改出 `Blenderdesign/pipeline/HTML原型`。
  修法：`BARE_GUARD` —— 前缀前面紧跟词字符（Python 的 `\\w` 已含中日韩）、`/`、`.` 时不匹配。
- **顺序污染**：裸替换若跑在链接重算之后，会把刚改好的 `code/unity/README.md`
  再吃一遍变成 `code/code/unity/README.md`。
  修法：先把链接目标打桩保护，裸替换只作用于链接之外，最后再还原并重算链接。

用法：
    python3 code/tools/rewrite_refs.py --dry-run
    python3 code/tools/rewrite_refs.py

来源: REFACTOR-PLAN.md §六 Phase 3.2
"""

import argparse
import collections
import os
import re
import subprocess
import sys
import urllib.parse

SKIP_DIRS = {'.git', '.refactor-backup', '.scratch', '.nuget-pkgs',
             'node_modules', '__pycache__', 'obj', 'bin',
             'Library', 'Temp', 'Logs',
             'sim_results',          # data/ 下的模拟生成物（2.6G / 1804 文件），无引用可改
             }
MAX_BYTES = 5 * 1024 * 1024   # 单文件读取上限；超过则跳过（生成物/大 JSON）
EXTS = ('.md', '.json', '.cs', '.py', '.sh', '.js', '.html', '.yml', '.yaml',
        '.asmdef', '.txt')
LINK = re.compile(r'\]\(([^)]+)\)')          # 允许路径含空格
PLACEHOLDERS = {'path', '相对路径', '路径', '', '...', 'url', 'link'}

# 词边界守卫：前缀前面若紧跟词字符（含中日韩）、`/` 或 `.`，则不是路径开头
BARE_GUARD = r'(?<![\w/.])'

# 不参与改写的文件（自身以旧路径为数据，改写会破坏其映射表）
SKIP_FILES = {
    'code/tools/migrate_paths.py',
    'code/tools/rewrite_refs.py',
}

# 不参与改写的目录：外部 vendored 内容有自己的内部路径空间
# （2026-09-12 实测：某本书自带 docs/ 目录，被全局 docs/→design/framework/
#  替换污染了 README 与 CI 配置，已回滚）
SKIP_PREFIX = (
    'reference/books/',      # 外部书籍正文（含自带 docs/ 结构）
    '.agents/',              # 上游 skill 包（示例路径非本仓引用）
)

# ── 目录前缀映射（来自 migrate_paths.py 的 TOP + NESTED + FILES）──
PREFIX = [
    ("规则/技能树系统/操作层/",              "design/rules/skill-tree/operations/"),
    ("规则/技能树系统/调制参数/",            "design/rules/skill-tree/modulation/"),
    ("规则/技能树系统/已废弃/",              "design/rules/skill-tree/deprecated/"),
    ("规则/技能树系统/参考文献/",            "design/rules/skill-tree/references/"),
    ("规则/技能树系统/",                     "design/rules/skill-tree/"),
    ("规则/",                                "design/rules/"),
    ("实体/疾病目录/_父类/",                 "design/entities/diseases/_parent-classes/"),
    ("实体/疾病目录/",                       "design/entities/diseases/"),
    ("实体/",                                "design/entities/"),
    ("空间/治疗中心建模/references/raw/参考图/",
     "design/space/treatment-center-modeling/references/raw/reference-images/"),
    ("空间/治疗中心建模/",                   "design/space/treatment-center-modeling/"),
    ("空间/",                                "design/space/"),
    ("事件/",                                "design/events/"),
    ("呈现/3D可视化/",                       "design/presentation/visualization-3d/"),
    ("呈现/",                                "design/presentation/"),
    ("管线/",                                "design/pipeline/"),
    ("规格/素材/病种试点/",                  "design/spec/material/disease-pilots/"),
    ("规格/素材/ref/一手叙事/",              "design/spec/material/ref/first-person-narratives/"),
    ("规格/素材/ref/",                       "design/spec/material/ref/"),
    ("规格/素材/drafts/",                    "design/spec/material/drafts/"),
    ("规格/素材/",                           "design/spec/material/"),
    ("规格/引擎/",                           "design/spec/engine/"),
    ("规格/数据源/",                         "design/spec/source-data/"),
    ("规格/",                                "design/spec/"),
    ("设计归档/grilling/方法论/",            "design/archive/grilling/methodology/"),
    ("设计归档/grilling/_根级/",             "design/archive/grilling/_root/"),
    ("设计归档/grilling/grilling-116-disease-gen-evolution/资格核验批次1-性创伤通道/",
     "design/archive/grilling/grilling-116-disease-gen-evolution/eligibility-batch1-sexual-trauma/"),
    ("设计归档/grilling/grilling-116-disease-gen-evolution/资格核验批次2-全量解锁/",
     "design/archive/grilling/grilling-116-disease-gen-evolution/eligibility-batch2-full-unlock/"),
    ("设计归档/grilling/",                   "design/archive/grilling/"),
    ("设计归档/",                            "design/archive/"),
    ("垃圾桶/废弃技能树/",                   "design/archive/trash/deprecated-skill-tree/"),
    ("垃圾桶/废弃脚本/",                     "design/archive/trash/deprecated-scripts/"),
    ("垃圾桶/",                              "design/archive/trash/"),
    ("参考/废弃/卡牌系统/",                  "reference/deprecated/card-system/"),
    ("参考/废弃/态度系统/",                  "reference/deprecated/attitude-system/"),
    ("参考/废弃/情绪系统/",                  "reference/deprecated/emotion-system/"),
    ("参考/废弃/月光场/",                    "reference/deprecated/moonlight-field/"),
    ("参考/废弃/行为系统/",                  "reference/deprecated/behavior-system/"),
    ("参考/废弃/认知系统/",                  "reference/deprecated/cognitive-system/"),
    ("参考/废弃/",                           "reference/deprecated/"),
    ("参考/文献/参考文献/",                  "reference/literature/papers/"),
    ("参考/文献/",                           "reference/literature/"),
    ("参考/书籍/",                           "reference/books/"),
    ("参考/会话存档/",                       "reference/session-archive/"),
    ("参考/",                                "reference/"),
    ("docs/维度/",                           "design/framework/dimensions/"),
    ("docs/决策树/",                         "design/decisions/"),
    ("docs/agents/",                         "design/conventions/agents/"),
    ("docs/设计框架-六维状态.md",            "design/framework/six-dimensions.md"),
    ("docs/写作与引用规范.md",               "design/conventions/writing-and-references.md"),
    ("docs/",                                "design/framework/"),
    ("src/",                                 "code/src/"),
    ("unity/",                               "code/unity/"),
    ("sim/",                                 "code/sim/"),
    ("tools/",                               "code/tools/"),
    ("项目总览.md",                          "design/README.md"),
]
PREFIX.sort(key=lambda kv: -len(kv[0]))       # 最长匹配优先

# 预编译（否则每个文件重复编译 60 次正则，2776 文件下会超时）
PREFIX_RE = [(re.compile(BARE_GUARD + re.escape(o)), n) for o, n in PREFIX]

# 旧路径下的实际文件名 → 新文件名（框架索引与决策树片段改过名）
FILE_RENAME = {
    "docs/维度/规则.md": "design/framework/dimensions/rules.md",
    "docs/维度/实体.md": "design/framework/dimensions/entities.md",
    "docs/维度/空间.md": "design/framework/dimensions/space.md",
    "docs/维度/事件.md": "design/framework/dimensions/events.md",
    "docs/维度/呈现.md": "design/framework/dimensions/presentation.md",
    "docs/维度/管线.md": "design/framework/dimensions/pipeline.md",
    "docs/决策树/01-被否决的方向.md": "design/decisions/01-rejected-directions.md",
    "docs/决策树/02-话题轮次-2026-07至08-01.md": "design/decisions/02-topics-2026-07-to-08-01.md",
    "docs/决策树/03-话题轮次-2026-08-01至08-11.md": "design/decisions/03-topics-2026-08-01-to-08-11.md",
    "docs/决策树/04-编号轮次-意识基础与数据层.md": "design/decisions/04-numbered-consciousness-and-data-layer.md",
    "docs/决策树/05-编号轮次-引擎实施.md": "design/decisions/05-numbered-engine-implementation.md",
    "docs/决策树/06-编号轮次-疾病与呈现.md": "design/decisions/06-numbered-disease-and-presentation.md",
}


def map_path(old):
    """把【旧】仓库相对路径映射到【新】路径；无映射返回 None。"""
    if old in FILE_RENAME:
        return FILE_RENAME[old]
    for o, n in PREFIX:
        o_ = o.rstrip('/')
        if old == o_:
            return n.rstrip('/')
        if old.startswith(o):
            return n + old[len(o):]
    return None


def git_renames():
    """从 git 读取本次迁移的 new→old 映射（用于反查文件迁移前的路径）。"""
    out = subprocess.run(['git', '-c', 'core.quotePath=false', 'status',
                          '--porcelain'], capture_output=True, text=True).stdout
    new2old = {}
    for line in out.split('\n'):
        if ' -> ' not in line or not ('R' in line[:2] or 'C' in line[:2]):
            continue
        o, n = line[3:].split(' -> ', 1)
        new2old[n.strip().strip('"')] = o.strip().strip('"')
    return new2old


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    dry = args.dry_run

    new2old = git_renames()
    files = []
    for dp, dn, fn in os.walk('.'):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if f.endswith(EXTS):
                files.append(os.path.relpath(os.path.join(dp, f), '.'))
    print(f"{'[DRY-RUN] ' if dry else ''}扫描 {len(files)} 个文件 · "
          f"文件级 rename {len(new2old)} 条\n")

    n_link = n_bare = 0
    touched = collections.Counter()

    for p in files:
        if p in SKIP_FILES or p.startswith(SKIP_PREFIX):
            continue
        old_self = new2old.get(p, p)
        try:
            if os.path.getsize(p) > MAX_BYTES:
                continue
            txt = open(p, encoding='utf-8').read()
        except Exception:
            continue
        orig = txt
        nd_new = os.path.dirname(p) or '.'
        nd_old = os.path.dirname(old_self) or '.'

        # ── 1. 链接目标打桩保护（避免被裸替换污染）──
        stash = []

        def do_stash(m):
            stash.append(m.group(1))
            return '](§§%d§§)' % (len(stash) - 1)

        txt = LINK.sub(do_stash, txt)

        # ── 2. 裸文本路径替换（带词边界守卫）──
        for pat, n in PREFIX_RE:
            txt, hits = pat.subn(n.replace('\\', '\\\\'), txt)
            n_bare += hits

        # ── 3. 还原链接目标并重算相对路径 ──
        def do_unstash(m):
            nonlocal n_link
            raw = stash[int(m.group(1))].strip()
            if raw.startswith(('http', 'mailto', '#', '/')):
                return '](' + raw + ')'
            path, sep, anchor = raw.partition('#')
            if not path:
                return '](' + raw + ')'
            dec = urllib.parse.unquote(path)
            if dec in PLACEHOLDERS:
                return '](' + raw + ')'
            resolved_old = os.path.normpath(os.path.join(nd_old, dec))
            mapped = map_path(resolved_old)
            if not mapped:
                return '](' + raw + ')'
            newrel = os.path.relpath(mapped, nd_new).replace('\\', '/')
            n_link += 1
            tail = ('#' + anchor if sep else '')
            return '](' + urllib.parse.quote(newrel, safe='/.%') + tail + ')'

        txt = re.sub(r'\]\(§§(\d+)§§\)', do_unstash, txt)

        if txt != orig:
            touched[p] += 1
            if not dry:
                open(p, 'w', encoding='utf-8').write(txt)

    print(f"markdown 链接重算 {n_link} 处 · 裸文本路径替换 {n_bare} 处 · "
          f"涉及 {len(touched)} 个文件")
    for k, _ in touched.most_common(12):
        print(f"  {k}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
