#!/usr/bin/env python3
"""
validate_cross_refs.py — 跨文件引用完整性校验

扫描所有活跃 .md 文件，检测:
  - [text](path) 死链（目标文件不存在）
  - 段引用可能失效（目标段未找到）
  - 目录引用（建议改为文件引用）
  - Frontmatter 父类引用

输出符合 review-plan --pre-check 格式（对齐 grilling-质量保障体系-v2.md §5.4）。

用法:
  python3 tools/validate_cross_refs.py                  # 扫描全部
  python3 tools/validate_cross_refs.py --format json     # JSON 输出
  python3 tools/validate_cross_refs.py --output report.json
"""

import json
import re
import sys
import urllib.parse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.md_utils import (
    ROOT, collect_md_files, is_deprecated_section,
    find_deprecated_section_end, CheckResult,
)


def extract_links(filepath: Path) -> list[dict]:
    """提取所有交叉引用。跳过代码块内和废弃章节内的链接。"""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    rel_path = str(filepath.relative_to(ROOT))
    links = []
    lines = text.split("\n")
    current_section = ""
    in_code_block = False

    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # 行内代码 `` `[text](path)` `` 跳过
        if re.search(r'`[^`]*\[[^\]]*\]\([^)]*\)[^`]*`', line):
            continue

        # 章节追踪 + 废弃章节跳过
        sec_match = re.match(r'^#{1,6}\s+(.+)$', line)
        if sec_match:
            heading = sec_match.group(1).strip()
            current_section = heading
            if is_deprecated_section(heading):
                # 跳过整个废弃章节
                level = len(re.match(r'^(#+)', line).group(1))
                end = find_deprecated_section_end(lines, i, level)
                # 将废弃章节内的所有行标记为跳过
                for skip_i in range(i, end):
                    continue  # 不处理这些行，直接跳到最后
                # 继续 i 到 end
                continue

        # Markdown 链接 [text](path)
        for m in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', line):
            target = m.group(2)
            label = m.group(1)
            if target.startswith("http://") or target.startswith("https://"):
                continue
            if target.startswith("#"):
                continue
            target = urllib.parse.unquote(target)
            if "#" in target:
                path_part, anchor = target.split("#", 1)
            else:
                path_part, anchor = target, None

            links.append({
                "type": "md_link",
                "target": path_part,
                "anchor": anchor,
                "text": label,
                "source_file": rel_path,
                "source_line": i + 1,
            })

        # Frontmatter 父类引用
        fm_match = re.match(r'^父类:\s*(.+)$', line)
        if fm_match:
            parent_name = fm_match.group(1).strip()
            parent_path = f"实体/疾病目录/_父类/{parent_name}.md"
            links.append({
                "type": "frontmatter_parent",
                "target": parent_path,
                "anchor": None,
                "text": parent_name,
                "source_file": rel_path,
                "source_line": i + 1,
            })

    return links


def resolve_target(target: str, source_file: str) -> tuple[Path | None, bool]:
    """解析相对路径。返回 (Path, is_directory)。"""
    target = urllib.parse.unquote(target)
    source_dir = (ROOT / source_file).parent
    candidates = [source_dir / target, ROOT / target]

    # 处理 ../ 路径
    parts = target.split("/")
    resolved = source_dir
    try:
        for part in parts:
            if part == "..": resolved = resolved.parent
            elif part == ".": continue
            else: resolved = resolved / part
        candidates.append(resolved)
    except ValueError:
        pass

    # 文件名模糊搜索
    filename = Path(target).name
    if filename and not target.endswith("/"):
        search_name = filename if "." in filename else filename + ".md"
        for f in ROOT.rglob(search_name):
            rel = str(f.relative_to(ROOT))
            if not any(kw in rel for kw in ["垃圾桶", ".trash", ".git", "__pycache__"]):
                candidates.append(f)
                break

    for cand in list(candidates):
        if not cand.suffix and not str(cand).endswith("/"):
            candidates.append(cand.with_suffix(".md"))

    for cand in candidates:
        try:
            if cand.is_dir(): return cand, True
            if cand.is_file(): return cand, False
        except (OSError, ValueError):
            continue
    return None, False


def check_section_exists(filepath: Path, anchor: str) -> bool:
    """检查目标文件中是否存在指定章节/段落"""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return False
    anchor = urllib.parse.unquote(anchor).lstrip("§")
    CN_NUM = {"一":"1","二":"2","三":"3","四":"4","五":"5","六":"6","七":"7","八":"8","九":"9","十":"10",
              "十一":"11","十二":"12","十三":"13","十四":"14"}
    raw_patterns = [anchor]
    if anchor in CN_NUM: raw_patterns.append(CN_NUM[anchor])
    for cn, num in CN_NUM.items():
        if num == anchor: raw_patterns.append(cn)
    # 扫描所有章节标题，逐标题尝试匹配（支持 GitHub 锚点格式）
    for line in text.split("\n"):
        sec = re.match(r'^#{1,6}\s+(.+)$', line)
        if not sec:
            continue
        heading = sec.group(1).strip()

        # GitHub 锚点风格：小写英文 + 去标点 + 空格变连字符
        githubified = heading.lower()
        githubified = re.sub(r'[^\w\s一-鿿-]', '', githubified)
        githubified = re.sub(r'\s+', '-', githubified)
        githubified = re.sub(r'-{2,}', '-', githubified)  # 合并连续连字符

        for raw in raw_patterns:
            escaped = re.escape(raw)
            for cand in (heading, githubified):
                if raw in cand:
                    return True
                if re.search(rf'(?:^|\s){escaped}(?:[\s、.,:：]|$)', cand):
                    return True
    return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="跨文件引用完整性校验")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", "-o", help="输出到文件（默认 stdout）")
    args = parser.parse_args()

    files = collect_md_files()
    all_links = []
    for fp in files:
        all_links.extend(extract_links(fp))

    # 模板占位符跳过
    PLACEHOLDER = ["相对路径", "xxx.md", "示例", "example"]
    dead_links, dir_links, section_warns = [], [], []
    pass_count = 0

    for link in all_links:
        target = link["target"]
        if not target or any(p in target.lower() for p in PLACEHOLDER):
            continue
        resolved, is_dir = resolve_target(target, link["source_file"])
        if resolved is None:
            dead_links.append(link)
        elif is_dir:
            dir_links.append(link)
        elif link["anchor"] and not check_section_exists(resolved, link["anchor"]):
            section_warns.append(link)
        else:
            pass_count += 1

    # 输出
    if args.format == "json":
        output = {
            "script": "validate_cross_refs.py",
            "timestamp": datetime.now().isoformat(),
            "summary": {"total": len(all_links), "passed": pass_count,
                        "blocker": len(dead_links), "warn": len(dir_links) + len(section_warns), "info": 0},
            "blocker": [{"source_file": l["source_file"], "source_line": l["source_line"],
                         "reason": f"死链: {l['target']}"} for l in dead_links],
            "warn": ([{"source_file": l["source_file"], "source_line": l["source_line"],
                       "reason": f"目录引用: {l['target']}/"} for l in dir_links] +
                     [{"source_file": l["source_file"], "source_line": l["source_line"],
                       "reason": f"段引用可能失效: §{l['anchor']}"} for l in section_warns]),
            "info": [],
        }
        out = json.dumps(output, ensure_ascii=False, indent=2)
    else:
        lines = ["# validate_cross_refs.py — 跨文件引用完整性校验\n",
                 "## 检查范围", f"- 扫描 {len(files)} 个活跃 .md 文件",
                 f"- 提取 {len(all_links)} 个交叉引用\n", "## 结果"]
        if dead_links:
            lines.append(f"\n### 🔴 死链 ({len(dead_links)} 个)\n")
            for l in dead_links:
                lines.append(f"FAIL  cross_ref  [{l['source_file']}:{l['source_line']}] → `{l['target']}` (文件不存在)")
        if dir_links:
            lines.append(f"\n### 🟡 目录引用 ({len(dir_links)} 个)\n")
            for l in dir_links[:15]:
                lines.append(f"WARN  cross_ref  [{l['source_file']}:{l['source_line']}] → `{l['target']}/` (目录引用)")
        if section_warns:
            lines.append(f"\n### 🟡 段引用可能失效 ({len(section_warns)} 个)\n")
            for l in section_warns[:20]:
                lines.append(f"WARN  cross_ref  [{l['source_file']}:{l['source_line']}] → `{l['target']} §{l['anchor']}` (段未找到)")
        lines.append(f"\nPASS  cross_ref  {pass_count} 个引用有效")
        lines.append(f"\n## 汇总")
        lines.append(f"{len(all_links)} refs: {pass_count} passed, {len(dead_links)} dead, {len(dir_links)} dir-refs, {len(section_warns)} section warnings")
        out = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)

    sys.exit(1 if dead_links else 0)


if __name__ == "__main__":
    main()
