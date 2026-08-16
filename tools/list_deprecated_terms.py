#!/usr/bin/env python3
"""
list_deprecated_terms.py — deprecated 术语清单查询脚本（单一正典来源）

从 data/term_registry.json 动态读取所有 status=deprecated 的术语。
供 task-checker / review-plan / 数学语言书写规范 等 AI 检查流程引用，
避免在任何 skill/规范文档中硬编码术语清单（硬编码会随注册表更新而漂移）。

用法:
  python3 tools/list_deprecated_terms.py                 # text：每行一个术语
  python3 tools/list_deprecated_terms.py --format json   # JSON 数组
  python3 tools/list_deprecated_terms.py --format table  # 含 definition 摘要的表格
  python3 tools/list_deprecated_terms.py --check 态度     # 检查单个词是否 deprecated（exit 0=是）
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
REGISTRY = ROOT / "data" / "term_registry.json"


def load_registry() -> dict:
    """加载 term_registry.json，返回 terms 字典。"""
    with open(REGISTRY, encoding="utf-8") as f:
        data = json.load(f)
    return data["terms"]


def deprecated_terms(terms: dict) -> list[dict]:
    """返回 status=deprecated 的术语条目列表（按名称排序）。"""
    out = []
    for name, info in terms.items():
        if info.get("status") == "deprecated":
            out.append({"name": name, **info})
    return sorted(out, key=lambda x: x["name"])


def main():
    parser = argparse.ArgumentParser(description="查询 term_registry 中的 deprecated 术语清单")
    parser.add_argument("--format", choices=["text", "json", "table"], default="text")
    parser.add_argument("--check", metavar="术语名", help="检查单个术语是否 deprecated（exit 0=是 / 1=否）")
    parser.add_argument("--count", action="store_true", help="只输出数量")
    args = parser.parse_args()

    terms = load_registry()
    depr = deprecated_terms(terms)

    if args.check:
        name = args.check
        info = terms.get(name)
        if info and info.get("status") == "deprecated":
            print(f"✅ {name} 是 deprecated 术语")
            sys.exit(0)
        else:
            print(f"❌ {name} 不是 deprecated 术语（不存在或 status!=deprecated）")
            sys.exit(1)

    if args.count:
        print(len(depr))
        return

    if args.format == "json":
        print(json.dumps([d["name"] for d in depr], ensure_ascii=False, indent=2))
    elif args.format == "table":
        print(f"| 术语 | definition 摘要 | 来源 |")
        print(f"|------|----------------|------|")
        for d in depr:
            # definition 摘要：取第一段（按 。/；切分）
            desc = d.get("definition", "").split("。")[0].split("；")[0].strip()
            if len(desc) > 60:
                desc = desc[:57] + "..."
            print(f"| `{d['name']}` | {desc} | {d.get('source','—')} |")
        print(f"\n共 {len(depr)} 个 deprecated 术语（来源: data/term_registry.json）")
    else:  # text
        for d in depr:
            print(d["name"])


if __name__ == "__main__":
    main()
