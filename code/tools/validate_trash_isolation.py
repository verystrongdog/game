#!/usr/bin/env python3
"""
垃圾桶隔离校验 — 验证"活跃文档不引用垃圾桶内容"规则。

检查项:
  1. 活跃 .md 文件中是否引用了**已移出的垃圾桶内容**（`design/archive/trash/<子路径>` / `.trash/<子路径>`）
  2. 活跃 .md 文件中是否出现了 #20 已废弃的术语
  3. 活跃 .md 文件中的链接是否指向垃圾桶

**2026-09-13 变更**：原 `design/archive/trash/` 的 26 个文件已**整份移出仓库**，
本地保留在 `.trash/`（见 `.gitignore`）。因此本校验**不再维护"垃圾桶里有哪些文件"的
枚举清单**——那类清单只能守住被枚举过的实例：实测一份**行内代码形式的新子路径引用**
（`design/archive/trash/deprecated-scripts/test_evolved_cog.py`）正是这样空过的
（旧的 `FILES_IN_TRASH` 只有 7 个文件名，且只比对 markdown 链接）。现在只判一件事：
**活跃文档不得指向垃圾桶下的任何内容**，与桶里当时有什么无关。

用法: python code/tools/validate_trash_isolation.py [--verbose]
退出码: 0 = 全部通过, 1 = 有问题
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

# ── 已移出的垃圾桶（2026-09-13） ──────────────────────────
# 判据 = 「指向垃圾桶下的内容」，与桶里有哪些文件无关：
#   · `design/archive/trash/<子路径>`（原位置，已移出仓库）
#   · `.trash/<子路径>`（新位置，本地保留、gitignore——引用它对别人就是死引用）
#   · `垃圾桶/<子路径>`（历史叫法）
# 只写目录本身（`design/archive/trash/`，用于定义该规则/记载变迁）**不算引用**；
# **占位写法也不算**——`<`/`>` 已从匹配字符类中排除，故 `design/archive/trash/<子路径>`
# 这种"描述规则"的写法不会误报（制定本检查时自己踩到，见下）。
TRASH_REF = re.compile(r"(?:design/archive/trash/|\.trash/|垃圾桶/)[^\s)`\"（），,；;：:<>]{2,}")

# 行内含这些标记 = 该行是在**记载变迁或标注废弃**，不判违规（沿用旧检查的豁免惯例）
DEPRECATION_MARKERS = ("⚠️", "已废弃", "已移出", "迁出", "迁至")

# ── 废弃术语 (#20) ────────────────────────────────────────

DEPRECATED_TERMS = [
    # (正则, 描述, 行内豁免词, 文件豁免前缀)
    (
        r"37\s*个?\s*(操作|技能)(?![项决])",
        "37个操作/技能 (D20 已废弃)",
        ["⚠️", "已废弃", "D20", "#20", "决策树"],
        ["design/decisions/"],
    ),
    # 表格中的裸 37: "37 (L0-L5)" 或 "37(L0-L5)"
    (
        r"\b37\b\s*\(?L\d",
        "37 (L0-L5) 旧技能计数 (D20 已废弃, L6已删除 #25)",
        ["⚠️", "已废弃", "D20", "#20", "决策树"],
        ["design/decisions/", "design/framework/grilling"],
    ),
    (
        r"激活点预算",
        "激活点预算 (玩家侧已改聚焦容量 D4/D7)",
        ["⚠️", "已废弃", "范式修正", "#20"],
        [
            "design/decisions/",
            "design/pipeline/预烘焙管线脚本设计.md",
            "design/rules/skill-tree/NPC AI 行为模型.md",
            ".scratch/",
        ],
    ),
    # 旧激活点模型章节 (在玩家侧文档中)
    (
        r"激活点模型",
        "激活点模型章节 (玩家侧已改聚焦容量)",
        ["⚠️", "已废弃", "#20", "决策树", "NPC AI", "预烘焙"],
        [
            "design/decisions/",
            "design/pipeline/预烘焙管线脚本设计.md",
            "design/rules/skill-tree/NPC AI 行为模型.md",
            ".scratch/",
        ],
    ),
    (
        r"在线手动选择",
        "在线手动选择链路 (D5 全局激活)",
        ["⚠️", "已废弃", "决策树"],
        ["design/decisions/"],
    ),
    (
        r"手动激活.*(链路|脑区)",
        "手动激活链路 (D5 全局激活, NPC情境自动激活除外)",
        ["⚠️", "已废弃", "决策树", "情境自动激活"],
        ["design/decisions/"],
    ),
    # 旧"每回合激活"模型
    (
        r"每回合.*?激活点|激活点.*?每回合",
        "每回合激活点模型 (D4/D7 已废弃)",
        ["⚠️", "已废弃", "#20", "决策树"],
        [
            "design/decisions/",
            "design/pipeline/预烘焙管线脚本设计.md",
            "design/rules/skill-tree/NPC AI 行为模型.md",
            ".scratch/",
        ],
    ),
]

# ── 豁免路径 ──────────────────────────────────────────────

EXEMPT_PREFIX = [
    "design/decisions/",
    ".scratch/",
    "design/archive/trash/",
    ".trash/",
    "reference/deprecated/",
    # grilling 源记录归档——非活跃正典，允许提及已废弃术语（2026-09-12 重构 Phase 2 新建）
    "design/archive/",
    # 仓库重构期的本地安全备份（非项目内容，重构完成后删除）
    ".refactor-backup/",
    # 已标注 ⚠️ 废弃的前置系统 (保留为参考数据源, [项目规约](../../design/conventions/README.md) §六)
    # 2026-09-12 仓库重构：该文件已从 design/archive/trash/ 迁至 design/rules/skill-tree/deprecated/（与 10 个同门文件同处）
    "design/rules/skill-tree/deprecated/链路槽位与激活系统.md",
]

EXEMPT_DIRS = {"trash", "deprecated", "archive", ".trash", ".scratch", ".refactor-backup"}


def is_exempt(rel_path: str) -> bool:
    for p in EXEMPT_PREFIX:
        if rel_path.startswith(p):
            return True
    for d in EXEMPT_DIRS:
        if f"/{d}/" in rel_path:
            return True
    return False


# ── 扫描 ──────────────────────────────────────────────────

def find_md_files():
    files = []
    for md in ROOT.rglob("*.md"):
        rel = str(md.relative_to(ROOT))
        if not is_exempt(rel):
            files.append((rel, md))
    return files


def check_refs_to_moved_trash(md_files):
    """活跃文档不得指向垃圾桶下的任何内容（与桶里当时有什么文件无关）。

    这是 2026-09-13 替换掉 `check_trash_refs` / `check_trash_paths` 的检查：那两道以
    `FILES_IN_TRASH`（7 个硬编码文件名）为判据，垃圾桶移出后它们只会静默通过。
    """
    errors = []
    for rel_path, abs_path in md_files:
        content = abs_path.read_text(encoding="utf-8")
        for i, line in enumerate(content.split("\n"), 1):
            m = TRASH_REF.search(line)
            if not m:
                continue
            if any(mark in line for mark in DEPRECATION_MARKERS):
                continue
            errors.append(
                f"🔴 {rel_path}:{i} — 引用已移出的垃圾桶内容: {m.group(0)[:90]}\n"
                f"   {line.strip()[:130]}"
            )
    return errors


def check_terms(md_files):
    errors = []
    for rel_path, abs_path in md_files:
        content = abs_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for pattern, desc, ok_words, ok_files in DEPRECATED_TERMS:
            if any(rel_path.startswith(f) for f in ok_files):
                continue
            for i, line in enumerate(lines, 1):
                if not re.search(pattern, line):
                    continue
                if any(w in line for w in ok_words):
                    continue
                errors.append(
                    f"🔴 {rel_path}:{i} — {desc}\n"
                    f"   {line.strip()[:130]}"
                )
    return errors


def check_links_to_trash(md_files):
    errors = []
    link_re = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    for rel_path, abs_path in md_files:
        content = abs_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for m in link_re.finditer(line):
                target = m.group(2)
                if target.startswith("http") or target.startswith("#"):
                    continue
                t = target.split("#")[0]
                if not t:
                    continue
                try:
                    r = str((abs_path.parent / t).resolve().relative_to(ROOT))
                except ValueError:
                    continue
                for td in ["垃圾桶", ".trash"]:
                    if r.startswith(f"{td}/") or f"/{td}/" in r:
                        errors.append(f"🔴 {rel_path}:{i} — 链接指向垃圾桶: {m.group(0)}")
                        break
    return errors


# ── main ──────────────────────────────────────────────────

def main():
    md_files = find_md_files()
    print(f"校验 {len(md_files)} 个活跃 .md 文件...\n")

    all_errors = []
    for name, fn in [
        ("引用已移出的垃圾桶内容", check_refs_to_moved_trash),
        ("废弃术语残留", check_terms),
        ("链接指向垃圾桶", check_links_to_trash),
    ]:
        errs = fn(md_files)
        if errs:
            print(f"## {name} ({len(errs)} 处)")
            for e in errs:
                print(e)
            print()
        all_errors.extend(errs)

    if all_errors:
        n = len(all_errors)
        print(f"{'='*60}\n❌ {n} 处问题\n{'='*60}")
        sys.exit(1)
    else:
        print("✅ 全部通过")
        sys.exit(0)


if __name__ == "__main__":
    main()
