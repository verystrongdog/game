#!/usr/bin/env python3
"""md_utils.py — 校验脚本共享工具

提取 validate_*.py 和 run_all_checks.py 中重复的常量和函数，
作为 Layer 1 管线共享模块。CLAUDE.md §代码层面 要求复用已有代码。

来源: validate_params.py + validate_cross_refs.py + run_all_checks.py 原有重复逻辑。
"""

import re
from pathlib import Path
from collections import namedtuple

ROOT = Path(__file__).parent.parent

# ============================================================
# 扫描范围常量 — 单一定义（不再在三个脚本中各自复制）
# ============================================================

# 活跃文档根目录
SCAN_ROOTS = ["规则", "实体", "空间", "事件", "呈现", "管线", "docs", "参考"]

# 排除目录
EXCLUDE_DIRS = {
    "垃圾桶", ".trash", "参考/废弃", "参考/书籍",
    ".git", ".claude", ".scratch", "__pycache__",
    "data", "tools",
}

# 排除文件名关键词
EXCLUDE_FILE_KEYWORDS = ["已废弃", ".gitkeep", "决策树.md"]


def is_active_md(filepath: Path) -> bool:
    """判断是否为活跃设计文档"""
    try:
        rel = str(filepath.relative_to(ROOT))
    except ValueError:
        return False
    for d in EXCLUDE_DIRS:
        if rel.startswith(d) or ("/" + d) in rel:
            return False
    for kw in EXCLUDE_FILE_KEYWORDS:
        if kw in rel:
            return False
    return filepath.suffix == ".md"


def collect_md_files(roots: list[str] = None) -> list[Path]:
    """收集所有活跃 .md 文件。来源: validate_params.py §collect_files, validate_cross_refs.py §collect_md_files"""
    if roots is None:
        roots = SCAN_ROOTS
    files = []
    for root_dir in roots:
        dir_path = ROOT / root_dir
        if not dir_path.exists():
            continue
        for md in dir_path.rglob("*.md"):
            if is_active_md(md):
                files.append(md)
    return sorted(files)


def is_deprecated_section(heading: str) -> bool:
    """判断章节是否已废弃。来源: validate_params.py §is_deprecated_section"""
    return "⚠️ 已废弃" in heading or "⚠️已废弃" in heading


def find_deprecated_section_end(lines: list[str], start_idx: int, level: int) -> int:
    """找到废弃章节的结束行号。来源: validate_params.py §extract_table_params"""
    j = start_idx + 1
    while j < len(lines):
        next_sec = re.match(r'^(#+)', lines[j])
        if next_sec and len(next_sec.group(1)) <= level:
            break
        j += 1
    return j


def strip_annotations(s: str) -> str:
    """去掉注释性内容：[NEW ...] / (...) / （...）。来源: validate_params.py §strip_annotations"""
    s = re.sub(r'\[NEW[^\]]*\]', '', s)
    s = re.sub(r'\([^)]*\)', '', s)
    s = re.sub(r'（[^）]*）', '', s)
    return s.strip()


# ============================================================
# 共享类型
# ============================================================

# 校验结果——替代裸 4 元组 (check_id, status, message, detail)
CheckResult = namedtuple("CheckResult", ["check", "status", "message", "detail"])
