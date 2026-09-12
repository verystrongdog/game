#!/usr/bin/env python3
"""
run_all_checks.py — Layer 1 预检查编排器

运行 code/tools/validate_*.py 全部脚本，汇总输出。
检测文件变更，标注需要人类审核的项。

用法:
  python3 code/tools/run_all_checks.py                  # 运行全部校验
  python3 code/tools/run_all_checks.py --format json     # JSON 输出（供 review-plan --pre-check）
  python3 code/tools/run_all_checks.py --changed         # 检测变更文件（不运行校验）
  python3 code/tools/run_all_checks.py --output report.json
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.md_utils import ROOT, collect_md_files

# 校验脚本注册表（单一列表，不再用三个分散列表）
VALIDATOR_REGISTRY = {
    "validate_link_data.py":       {"status": "deprecated", "json": True, "replaced_by": "build_tripartite_model.py + build_function_labels.py"},
    "validate_disease.py":         {"status": "active", "json": False},
    "validate_spatial.py":         {"status": "active", "json": True},
    "validate_trash_isolation.py": {"status": "active", "json": False},
    "validate_params.py":          {"status": "active", "json": True},
    "validate_cross_refs.py":      {"status": "active", "json": True},
    "validate_cards.py":           {"status": "deprecated", "json": False},
}

STATE_FILE = ROOT / ".checks-state.json"   # 运行状态（2026-09-12：原 .scratch/.last_check_state.json，随 .scratch 移出版本控制而迁出）


def get_active_validators() -> list[Path]:
    """获取所有活跃校验脚本的路径"""
    tools_dir = ROOT / "tools"
    return [tools_dir / name for name, info in VALIDATOR_REGISTRY.items()
            if info["status"] == "active" and (tools_dir / name).exists()]


def run_validator(script: Path) -> dict:
    """运行单个校验脚本，返回 {name, exit_code, stdout, stderr}"""
    info = VALIDATOR_REGISTRY.get(script.name, {})
    extra_args = ["--format", "json"] if info.get("json", True) else []
    try:
        result = subprocess.run(
            [sys.executable, str(script)] + extra_args,
            cwd=str(ROOT), capture_output=True, text=True, timeout=60,
        )
        return {
            "name": script.name,
            "exit_code": result.returncode,
            "stdout": result.stdout.strip()[:2000],
            "stderr": result.stderr.strip()[:500],
        }
    except subprocess.TimeoutExpired:
        return {"name": script.name, "exit_code": -1, "stdout": "", "stderr": "TIMEOUT (60s)"}
    except Exception as e:
        return {"name": script.name, "exit_code": -1, "stdout": "", "stderr": str(e)}


def load_last_state() -> dict:
    """加载上次运行的状态"""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"files": {}, "last_run": None}


def save_state(current_files: dict):
    """保存当前运行状态"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({
        "files": current_files,
        "last_run": datetime.now().isoformat(),
    }, indent=2, ensure_ascii=False))


def detect_new_files() -> list[str]:
    """检测自上次运行以来新增/修改的 md 文件。来源: md_utils.collect_md_files"""
    last_state = load_last_state()
    last_files = last_state.get("files", {})

    current_files = {}
    new_or_changed = []

    for md in collect_md_files():
        rel = str(md.relative_to(ROOT))
        mtime = md.stat().st_mtime
        current_files[rel] = mtime
        if rel not in last_files:
            new_or_changed.append(f"[NEW] {rel}")
        elif mtime > last_files[rel]:
            new_or_changed.append(f"[MODIFIED] {rel}")

    save_state(current_files)
    return new_or_changed


def format_output(validator_results: list[dict], new_files: list[str], fmt: str = "text"):
    """以 review-plan --pre-check 格式输出汇总"""
    if fmt == "json":
        summary = {
            "script": "run_all_checks.py",
            "timestamp": datetime.now().isoformat(),
            "validators": [
                {"name": r["name"], "exit_code": r["exit_code"], "output": r["stdout"][:500]}
                for r in validator_results
            ],
            "new_files": new_files,
            "summary": {
                "total": len(validator_results),
                "passed": sum(1 for r in validator_results if r["exit_code"] == 0),
                "failed": sum(1 for r in validator_results if r["exit_code"] not in (0, -1)),
                "errors": sum(1 for r in validator_results if r["exit_code"] == -1),
            },
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    # Text output
    n_pass = sum(1 for r in validator_results if r["exit_code"] == 0)
    n_fail = sum(1 for r in validator_results if r["exit_code"] not in (0, -1))
    n_err = sum(1 for r in validator_results if r["exit_code"] == -1)

    print("# run_all_checks.py — Layer 1 预检查编排器\n")
    print("## 检查范围")
    print(f"- 校验脚本: {len(validator_results)} 个")
    for r in validator_results:
        status = "✅" if r["exit_code"] == 0 else ("❌" if r["exit_code"] > 0 else "💥")
        print(f"  - {status} {r['name']}")
    active_names = [n for n, i in VALIDATOR_REGISTRY.items() if i["status"] == "active"]
    missing = [v for v in active_names if not (ROOT / "tools" / v).exists()]
    if missing:
        print(f"\n- ⚠️ 未实现的校验脚本 ({len(missing)} 个): {', '.join(missing)}")
    deprecated = [n for n, i in VALIDATOR_REGISTRY.items() if i["status"] == "deprecated"]
    if deprecated:
        print(f"- 已废弃（不运行）: {', '.join(deprecated)}")

    print(f"\n## 新文件/修改文件 ({len(new_files)} 个)")
    if new_files:
        for f in new_files[:30]:
            print(f"  - {f}")
        if len(new_files) > 30:
            print(f"  ... 等 {len(new_files) - 30} 个")
    else:
        print("  (无变更)")

    print(f"\n## 各脚本详情")
    for r in validator_results:
        status = "PASS" if r["exit_code"] == 0 else ("FAIL" if r["exit_code"] > 0 else "ERROR")
        print(f"\n### {status}  {r['name']}")
        if r["stdout"]:
            # 提取各脚本的汇总行
            for line in r["stdout"].split("\n"):
                line = line.strip()
                if line and not line.startswith("{") and not line.startswith("#"):
                    print(f"  {line}")
        if r["stderr"]:
            print(f"  [stderr] {r['stderr'][:200]}")

    print(f"\n## 汇总")
    print(f"{len(validator_results)} validators: {n_pass} passed, {n_fail} failed, {n_err} errors")
    if new_files:
        print(f"{len(new_files)} files changed since last run — 建议人工审核")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Layer 1 预检查编排器")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", "-o", help="输出到文件（默认 stdout）")
    parser.add_argument("--changed", action="store_true", help="仅检测变更文件（不运行校验）")
    args = parser.parse_args()

    if args.changed:
        new_files = detect_new_files()
        out = json.dumps(new_files, indent=2, ensure_ascii=False) if args.format == "json" else "\n".join(new_files or ["(无变更)"])
        if args.output: Path(args.output).write_text(out, encoding="utf-8")
        else: print(out)
        return

    new_files = detect_new_files()
    scripts = get_active_validators()
    results = [run_validator(s) for s in scripts]

    # 收集输出
    output_lines = []
    # Text format is handled inside format_output which prints directly
    # For --output support, redirect stdout
    if args.output:
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            format_output(results, new_files, args.format)
            output_text = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        Path(args.output).write_text(output_text, encoding="utf-8")
    else:
        format_output(results, new_files, args.format)

    n_fail = sum(1 for r in results if r["exit_code"] not in (0, -1))
    sys.exit(1 if n_fail > 0 else 0)


if __name__ == "__main__":
    main()
