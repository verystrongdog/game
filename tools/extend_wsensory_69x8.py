#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""W_sensory.json 69×6 → 69×8 扩列迁移脚本（一次性工具，Grilling #108 Q2 执行契约）。

锚点（#108 Q2）：
- olfactory（嗅觉）      = {LateralOrbitofrontal, Amygdala}   （#69 解剖锚「梨状皮层/OFC」→ OFC 主投射 + 杏仁核气味-情绪联结）
- thermoreception（热觉）= {Postcentral, Insula}             （S1 温度区 + 后脑岛内感受）

铁律：
- 原 6 列（visual/auditory/somatosensory/pain/social_cognition/language_cognition）逐位不变
- rows 与 matrix_2d 双源一致性断言（matrix_2d[j][k] == rows[fid][modalities[k]]）
- 元字段同步：modalities / dimensions.modalities / modality_nodes /
  cortical_nodes_with_sensory_input / cortical_nodes_without_sensory_input / metadata

用法: python3 tools/extend_wsensory_69x8.py [--check]  （--check 只断言不写回）
"""
import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "connectivity" / "W_sensory.json"

ORIGINAL_MODALITIES = ["visual", "auditory", "somatosensory", "pain",
                       "social_cognition", "language_cognition"]

# 新模态 → 锚点 fid（#108 Q2）
NEW_MODALITIES = {
    "olfactory": ["LateralOrbitofrontal", "Amygdala"],
    "thermoreception": ["Postcentral", "Insula"],
}


def assert_matrix_rows_consistent(rows, matrix, modalities):
    """双源一致性：matrix_2d[j][k] == rows[RegionIds[j]][modalities[k]]，69×N 全量。"""
    fids = list(rows.keys())
    assert len(fids) == len(matrix), f"rows({len(fids)}) != matrix({len(matrix)})"
    for j, fid in enumerate(fids):
        row = rows[fid]
        for k, mod in enumerate(modalities):
            assert matrix[j][k] == row[mod], (
                f"双源不一致 j={j} fid={fid} k={k} mod={mod}: "
                f"matrix={matrix[j][k]} rows={row[mod]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只断言，不写回")
    args = ap.parse_args()

    data = json.loads(PATH.read_text(encoding="utf-8"))

    # ---- 前置断言：原文件必须仍为 69×6 ----
    assert data["modalities"] == ORIGINAL_MODALITIES, "原 modalities 顺序不符"
    assert len(data["rows"]) == 69, f"rows 应 69，实测 {len(data['rows'])}"
    assert len(data["matrix_2d"]) == 69, f"matrix_2d 应 69，实测 {len(data['matrix_2d'])}"
    assert all(len(r) == 6 for r in data["matrix_2d"]), "matrix_2d 列数应 6"
    assert_matrix_rows_consistent(data["rows"], data["matrix_2d"], ORIGINAL_MODALITIES)

    # ---- 快照原 6 列（逐位断言锚点）----
    orig_rows = copy.deepcopy(data["rows"])
    orig_matrix = copy.deepcopy(data["matrix_2d"])

    new_data = copy.deepcopy(data)
    modalities = ORIGINAL_MODALITIES + list(NEW_MODALITIES.keys())

    # 逐行追加新模态列
    for fid, row in new_data["rows"].items():
        for mod, anchors in NEW_MODALITIES.items():
            row[mod] = 1 if fid in anchors else 0
    new_matrix = []
    for j, fid in enumerate(list(new_data["rows"].keys())):
        new_row = [new_data["rows"][fid][m] for m in modalities]
        new_matrix.append(new_row)
    new_data["matrix_2d"] = new_matrix
    new_data["modalities"] = modalities
    new_data["dimensions"]["modalities"] = 8
    new_data["description"] = (
        "W_sensory — anatomical mapping from 8 sensory modalities to 69 functional_ids")

    # ---- 元字段同步 ----
    # modality_nodes：新模态 → 锚点 fid 列表
    new_data["modality_nodes"].update(NEW_MODALITIES)
    # 非皮层注释更新（Amygdala 现为嗅觉锚点）
    new_data["metadata"]["non_cortical_note"] = (
        "25 nodes (14 subcortical + 11 brainstem) have all-zero W_sensory rows except "
        "Amygdala (olfactory, 2026-09-03 #108 Q2). Per runtime state model §4.1, only "
        "category=cortical nodes participate in WC dynamics and receive s(t); Amygdala "
        "pain/social processing still arrives through corticocortical connections.")
    # 无直接感官输入列表：LateralOrbitofrontal 现为嗅觉锚点 → 移除
    without = new_data["metadata"]["nodes_without_direct_sensory"]
    without = without.replace("LateralOrbitofrontal (reward), ", "")
    new_data["metadata"]["nodes_without_direct_sensory"] = without
    new_data["metadata"]["sources"].append(
        "Grilling #108 Q2 — olfactory {LateralOrbitofrontal, Amygdala} / "
        "thermoreception {Postcentral, Insula} (2026-09-03)")
    # cortical 列表同步
    sensory_now = set(new_data["cortical_nodes_with_sensory_input"]) | {"LateralOrbitofrontal"}
    new_data["cortical_nodes_with_sensory_input"] = sorted(sensory_now)
    new_data["cortical_nodes_without_sensory_input"] = sorted(
        set(new_data["cortical_nodes_without_sensory_input"]) - {"LateralOrbitofrontal"})

    # ---- 后置断言 ----
    assert_matrix_rows_consistent(new_data["rows"], new_data["matrix_2d"], modalities)
    assert len(new_data["matrix_2d"]) == 69 and all(len(r) == 8 for r in new_data["matrix_2d"])
    # 原 6 列逐位不变（rows 双源）
    for fid in orig_rows:
        for mod in ORIGINAL_MODALITIES:
            assert new_data["rows"][fid][mod] == orig_rows[fid][mod], f"原列漂移: {fid}.{mod}"
    # 锚点断言
    for mod, anchors in NEW_MODALITIES.items():
        for fid in new_data["rows"]:
            want = 1 if fid in anchors else 0
            assert new_data["rows"][fid][mod] == want, f"新模态锚点不符: {fid}.{mod}"
    # 模态数上限：Postcentral 变 3 模态（somatosensory+pain+thermoreception，允许）
    print("扩列后模态活跃计数：")
    for mi, mod in enumerate(modalities):
        n = sum(1 for r in new_data["matrix_2d"] if r[mi] == 1)
        print(f"  {mod}: {n}")

    if args.check:
        print("CHECK OK — 未写回")
        return
    PATH.write_text(json.dumps(new_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已写回 {PATH}")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"断言失败: {e}", file=sys.stderr)
        sys.exit(1)
