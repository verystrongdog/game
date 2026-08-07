#!/usr/bin/env python3
"""
垃圾桶隔离校验 — 验证"活跃文档不引用垃圾桶内容"规则。

检查项:
  1. 活跃 .md 文件中是否引用了垃圾桶中的文件
  2. 活跃 .md 文件中是否出现了 #20 已废弃的术语
  3. 活跃 .md 文件中的链接是否指向垃圾桶

用法: python tools/validate_trash_isolation.py [--verbose]
退出码: 0 = 全部通过, 1 = 有问题
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ── 垃圾桶中的文件 (#20 批次2移动) ────────────────────────

FILES_IN_TRASH = [
    "规则/技能树系统/操作层/L0-脑干技能设计.md",
    "规则/技能树系统/操作层/L1-边缘系统技能设计.md",
    "规则/技能树系统/操作层/L2-旁边缘技能设计.md",
    "规则/技能树系统/操作层/L3-初级感觉技能设计.md",
    "规则/技能树系统/操作层/L4-高级单模态技能设计.md",
    "规则/技能树系统/操作层/L5-跨模态认知技能设计.md",
    "规则/技能树系统/操作层/L6-跨模态整合技能设计.md",
]

# 路径片段形式的垃圾桶引用
TRASH_PATH_FRAGMENTS = [f.replace(".md", "") for f in FILES_IN_TRASH]

# ── 废弃术语 (#20) ────────────────────────────────────────

DEPRECATED_TERMS = [
    # (正则, 描述, 行内豁免词, 文件豁免前缀)
    (
        r"37\s*个?\s*(操作|技能)(?![项决])",
        "37个操作/技能 (D20 已废弃)",
        ["⚠️", "已废弃", "D20", "#20", "决策树"],
        ["docs/决策树.md"],
    ),
    # 表格中的裸 37: "37 (L0-L5)" 或 "37(L0-L5)"
    (
        r"\b37\b\s*\(?L\d",
        "37 (L0-L5) 旧技能计数 (D20 已废弃, L6已删除 #25)",
        ["⚠️", "已废弃", "D20", "#20", "决策树"],
        ["docs/决策树.md", "docs/grilling"],
    ),
    (
        r"激活点预算",
        "激活点预算 (玩家侧已改聚焦容量 D4/D7)",
        ["⚠️", "已废弃", "范式修正", "#20"],
        [
            "docs/决策树.md",
            "管线/预烘焙管线脚本设计.md",
            "规则/技能树系统/NPC AI 行为模型.md",
            ".scratch/",
        ],
    ),
    # 旧激活点模型章节 (在玩家侧文档中)
    (
        r"激活点模型",
        "激活点模型章节 (玩家侧已改聚焦容量)",
        ["⚠️", "已废弃", "#20", "决策树", "NPC AI", "预烘焙"],
        [
            "docs/决策树.md",
            "管线/预烘焙管线脚本设计.md",
            "规则/技能树系统/NPC AI 行为模型.md",
            ".scratch/",
        ],
    ),
    (
        r"在线手动选择",
        "在线手动选择链路 (D5 全局激活)",
        ["⚠️", "已废弃", "决策树"],
        ["docs/决策树.md"],
    ),
    (
        r"手动激活.*(链路|脑区)",
        "手动激活链路 (D5 全局激活, NPC情境自动激活除外)",
        ["⚠️", "已废弃", "决策树", "情境自动激活"],
        ["docs/决策树.md"],
    ),
    # 旧"每回合激活"模型
    (
        r"每回合.*?激活点|激活点.*?每回合",
        "每回合激活点模型 (D4/D7 已废弃)",
        ["⚠️", "已废弃", "#20", "决策树"],
        [
            "docs/决策树.md",
            "管线/预烘焙管线脚本设计.md",
            "规则/技能树系统/NPC AI 行为模型.md",
            ".scratch/",
        ],
    ),
]

# ── 豁免路径 ──────────────────────────────────────────────

EXEMPT_PREFIX = [
    "docs/决策树.md",
    ".scratch/",
    "垃圾桶/",
    ".trash/",
    "参考/废弃/",
    # 已标注 ⚠️ 废弃的前置系统 (保留为参考数据源, CLAUDE.md §文档层面)
    "规则/技能树系统/激活系统/链路槽位与激活系统.md",
]

EXEMPT_DIRS = {"垃圾桶", ".trash", "已废弃", ".scratch"}


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


def check_trash_refs(md_files):
    errors = []
    for rel_path, abs_path in md_files:
        content = abs_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for trash_file in FILES_IN_TRASH:
            fragment = Path(trash_file).name.replace(".md", "")
            if fragment not in content:
                continue
            for i, line in enumerate(lines, 1):
                if fragment in line and "⚠️" not in line and "废弃" not in line:
                    errors.append(f"🔴 {rel_path}:{i} — 引用垃圾桶文件: {fragment}")
    return errors


def check_trash_paths(md_files):
    errors = []
    for rel_path, abs_path in md_files:
        content = abs_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for fragment in TRASH_PATH_FRAGMENTS:
            short = fragment.split("/")[-1]
            for i, line in enumerate(lines, 1):
                if fragment in line and "⚠️" not in line and "废弃" not in line:
                    errors.append(
                        f"🔴 {rel_path}:{i} — 垃圾桶路径片段: ...{fragment[-40:]}\n"
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
        ("垃圾桶文件引用", check_trash_refs),
        ("垃圾桶路径片段", check_trash_paths),
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
