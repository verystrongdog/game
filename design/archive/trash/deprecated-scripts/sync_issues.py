#!/usr/bin/env python3
"""
同步 .scratch/ 本地 issue 文件 ↔ GitHub issues（通过 gh CLI）。

约定（见 design/conventions/agents/issue-tracker.md §GitHub 镜像同步）：
- 本地 issue 头部元数据行: > Status: claimed | Type: task | 维度: 管线 | GitHub: #42
- H1 标题 = GitHub issue 标题；元数据行之后的内容 = GitHub issue body
- 无 GitHub ref → gh issue create，并把 ref 写回文件元数据行
- 有 GitHub ref → gh issue edit 更新 body（本地为真相源）
- Status: resolved / closed → gh issue close
- 幂等：可随时重复运行

用法: python3 code/tools/sync_issues.py [--dry-run]
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "verystrongdog/game"
ROOT = Path(__file__).resolve().parent.parent.parent

# Type → GitHub labels 映射（与 design/conventions/agents/triage-labels.md 词表一致）
TYPE_LABELS = {
    "task": ["ready-for-agent"],
    "implementation": ["implementation"],
    "hotfix": ["hotfix"],
    "grilling": ["grilling", "needs-triage"],
    "research": [],
    "prototype": [],
}


def gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def find_local_issues() -> list[Path]:
    """扫描 .scratch/*/design/issues/ 和 .scratch/*/impl/issues/ 下的 md 文件。"""
    issues = []
    scratch = ROOT / ".scratch"
    if not scratch.exists():
        return issues
    for layer in ("design", "impl"):
        for p in sorted(scratch.glob(f"*/{layer}/issues/*.md")):
            issues.append(p)
    return issues


def parse_issue(path: Path) -> tuple[str | None, dict, list[str]]:
    """解析本地 issue 文件 → (标题, 元数据dict, body行列表)。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    title = None
    meta: dict = {}
    body_lines: list[str] = []
    for line in lines:
        if title is None and line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("> ") and "Status:" in line:
            m = re.search(r"Status:\s*(\w+)", line)
            if m:
                meta["status"] = m.group(1)
            m = re.search(r"Type:\s*(\w+)", line)
            if m:
                meta["type"] = m.group(1)
            m = re.search(r"维度:\s*([^|>]+)", line)
            if m:
                meta["dimension"] = m.group(1).strip()
            m = re.search(r"GitHub:\s*(?:\[#|#)?(\d+)", line)
            if m:
                meta["github"] = m.group(1)
            continue
        body_lines.append(line)
    # 去掉开头的空行
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    return title, meta, body_lines


def build_body(path: Path, body_lines: list[str]) -> str:
    rel = path.relative_to(ROOT)
    header = f"本地: {rel}\n\n"
    return header + "\n".join(body_lines).strip() + "\n"


def labels_for(meta: dict) -> list[str]:
    labels = TYPE_LABELS.get(meta.get("type", ""), [])
    if meta.get("dimension"):
        labels.append(f"维度:{meta['dimension']}")
    return labels


def issue_exists(num: str) -> bool:
    return gh("issue", "view", num, "--repo", REPO, "--json", "number").returncode == 0


def write_github_ref(path: Path, num: str) -> None:
    """把 GitHub ref 写回本地文件元数据行。"""
    text = path.read_text(encoding="utf-8")
    link = f"https://github.com/{REPO}/issues/{num}"
    if re.search(r"GitHub:", text):
        text = re.sub(r"GitHub:\s*(?:\[#|#)?\d+(?:\][^|\n>]*)?", f"GitHub: [#{num}](%7Blink%7D)", text)
    else:
        text = re.sub(r"(> Status:.*)", rf"\1 | GitHub: [#{num}](%7Blink%7D)", text)
    path.write_text(text, encoding="utf-8")


def sync_issue(path: Path, dry_run: bool) -> None:
    title, meta, body_lines = parse_issue(path)
    if not title:
        print(f"⚠️  跳过（无 H1 标题）: {path}")
        return
    body = build_body(path, body_lines)
    gh_num = meta.get("github")

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(body)
        tmp = f.name

    try:
        if gh_num and issue_exists(gh_num):
            if dry_run:
                print(f"[dry-run] 更新 #{gh_num}: {title}")
                return
            r = gh("issue", "edit", gh_num, "--repo", REPO, "--body-file", tmp)
            if r.returncode == 0:
                print(f"✅ 更新 #{gh_num}: {title}")
            else:
                print(f"❌ 更新 #{gh_num} 失败: {r.stderr.strip()}")
        else:
            # 创建新 issue
            if dry_run:
                print(f"[dry-run] 创建: {title} (labels: {labels_for(meta)})")
                return
            args = ["issue", "create", "--repo", REPO, "--title", title, "--body-file", tmp]
            labels = labels_for(meta)
            if labels:
                args += ["--label", ",".join(labels)]
            r = gh(*args)
            m = re.search(r"issues/(\d+)", r.stdout)
            if r.returncode == 0 and m:
                num = m.group(1)
                if gh_num:
                    print(f"⚠️  本地 ref #{gh_num} 已不存在，重建为 #{num}: {title}")
                else:
                    print(f"✅ 创建 #{num}: {title}")
                write_github_ref(path, num)
            else:
                print(f"❌ 创建失败: {title}\n{r.stderr.strip()}")

        # 关闭已解决/已关闭的 issue
        if gh_num and meta.get("status") in ("resolved", "closed"):
            if dry_run:
                print(f"[dry-run] 关闭 #{gh_num}: {title}")
                return
            r = gh("issue", "close", gh_num, "--repo", REPO)
            if r.returncode == 0:
                print(f"🔒 关闭 #{gh_num}: {title}")
    finally:
        Path(tmp).unlink(missing_ok=True)


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    issues = find_local_issues()
    if not issues:
        print("无本地 issue 文件（.scratch/*/{design,impl}/issues/*.md）")
        return
    for path in issues:
        sync_issue(path, dry_run)


if __name__ == "__main__":
    main()
