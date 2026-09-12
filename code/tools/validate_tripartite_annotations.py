#!/usr/bin/env python3
"""
validate_tripartite_annotations.py — tripartite_model.json 注释完整性校验（只读，fail-fast）

背景（2026-08-30 Grilling #91 事故）：
  #92 (66d1dd2) 重跑 build_tripartite_model.py 时覆盖了 build_function_labels.py 的
  注释产物（role/function_label/gameplay_labels/description），EdgeRole 枚举默认 Active(0)
  使全部 brainstem 边静默升值 1.0 → b_j 漂移 → 引擎 12 测试失败。
  本脚本是防再犯门禁：最终 tripartite_model.json 必须同时满足
  基础图 schema + 注释字段完整性 + #92 lateralization + 手工 privileged_pathways。

设计依据:
  - 规则/技能树系统/脑功能层级模型.md §二十（三体模型）
  - 规则/技能树系统/偏侧化架构.md §9.2（T8 校验）
  - Grilling #91（2026-08-30）数据回归修复

用法: python3 tools/validate_tripartite_annotations.py [data_dir]
退出码: 0 = PASS；1 = FAIL（fail-fast，第一条错误即退出）
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ─── 校验契约 ───────────────────────────────────────────────────

# 每类边的 role 合法值集合（实测来源：66d1dd2^ 数据 + build_function_labels.py 逻辑）
ALLOWED_ROLES = {
    "brainstem": {"active", "modulating"},       # 脑干广播：active/modulating（99+15 实测）
    "cstc": {"active"},                          # CSTC 环路：结构性 active（47 实测）
    "corticocortical": {"active", "silent"},     # 皮层-皮层：active/silent（368+408 实测）
    "privileged_pathways": {"active", "silent"}, # 特权通路：active/silent（64+48 实测）
}

# 注释步骤（build_function_labels.py）必须产出的边字段
REQUIRED_FIELDS = ["role", "function_label", "gameplay_labels", "description"]

# 镜像节点（偏侧化架构 §五：不写 lateralization 字段）
MIRROR_EXEMPT = {"LocusCoeruleusRight", "SubstantiaNigraParsCompactaRight"}

# 手工维护数据（生成器不产出——重跑生成器会丢失，须从 git 恢复）
MANUAL_KEYS = ["privileged_pathways"]


def load_model(data_dir: Path) -> dict:
    path = data_dir / "connectivity" / "tripartite_model.json"
    if not path.exists():
        raise FileNotFoundError(f"tripartite_model.json 不存在: {path}")
    with open(path) as f:
        return json.load(f)


def check(cond: bool, msg: str) -> None:
    if not cond:
        print(f"❌ FAIL: {msg}")
        sys.exit(1)


def main() -> None:
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data"
    model = load_model(data_dir)
    total_edges = 0

    # 1) 边注释字段完整性（role/function_label/gameplay_labels/description）
    for kind, allowed in ALLOWED_ROLES.items():
        edges = model.get(kind, [])
        total_edges += len(edges)
        for e in edges:
            src = e.get("source", "?")
            tgt = e.get("target", "?")
            for f in REQUIRED_FIELDS:
                check(f in e, f"{kind} 边 {src}→{tgt} 缺字段 {f}（生成器重跑会丢失注释产物——须重跑 build_function_labels.py）")
            check(e.get("role") in allowed,
                  f"{kind} 边 {src}→{tgt} role={e.get('role')!r} ∉ {sorted(allowed)}")

    # 2) #92 lateralization（graph_nodes 非镜像节点必须有，镜像节点必须无）
    nodes = model.get("graph_nodes", {})
    for name, node in nodes.items():
        has = "lateralization" in node
        if name in MIRROR_EXEMPT:
            check(not has, f"镜像节点 {name} 不应有 lateralization（偏侧化架构 §五）")
        else:
            check(has, f"graph_nodes.{name} 缺 lateralization（#92 契约）")
            lat = node.get("lateralization")
            check(lat is not None and -1.0 <= lat <= 1.0,
                  f"graph_nodes.{name} lateralization={lat!r} ∉ [−1, +1]")

    # 3) 手工维护数据存在性（生成器不产出——重跑丢失即此处 FAIL）
    for key in MANUAL_KEYS:
        check(len(model.get(key, [])) > 0,
              f"{key} 为空——该数据为手工维护（curated whitelist，生成器不产出），"
              f"若刚重跑过生成器请从 git 恢复")

    # 4) 注释元字段（build_function_labels.py 写回标记）
    check(model.get("_function_labels_applied") is True,
          "_function_labels_applied 缺失——注释步骤未执行或产物被覆盖")

    print(f"✅ PASS: {len(nodes)} 图节点 / {total_edges} 边 / lateralization 契约 / 注释字段全部通过")


if __name__ == "__main__":
    main()
