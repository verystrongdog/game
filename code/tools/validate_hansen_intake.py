#!/usr/bin/env python3
"""validate_hansen_intake.py — `hansen2024/` 只读结构校验（#133，依 #132 裁定 C）

**判据：数据集的结构/坐标文件与项目核团清单能对上，且校验过程一个字节都不写。**

背景：#132 裁定为 **C 部分接入**——接入 `region_info_Schaefer400.csv` / `subcortex_coords.csv`
做结构校验，**连接强度仍用本仓估计**（数值权威 = 本仓估计，Design `ACCEPTED`）。
裁定全文见 `data/connectivity/external-sources.md` §二 缺口 1。
本校验器要消掉的是「登记了却不读」：此前 5 个数据文件的受控代码引用数**全为 0**。

四条断言（全部只读）：

  A 配对完整性  `brainstem_coords.txt` 行数 = `brainstem_coords_labels.txt` 标签数（逐行配对）；
                 同名标签在 `region_info_Schaefer400.csv` 中可查（**`STh_l`/`STh_r` 两个已知不在**，登记不算失败）
  B 覆盖        项目 16 条脑干条目（`BRAINSTEM_COMMUNITY_GAIN_ESTIMATE`，用 `ast` 读源码取键，
                 **不 import 生成器**——那会拖进 numpy）逐条有判定：
                 映射到真实存在的数据集标签，或显式豁免 + 理由；三类集合必须恰好铺满 16 条
  C 坐标一致    ① `brainstem_coords.txt` ↔ `region_info`：**x、y 反号**后一致（约定是实测出来的，
                 不是假设：2026-09-13 实测 67/67）② `subcortex_coords.csv` ↔ `region_info`：
                 **同号**直接一致（实测 14/14）。容差 1e-3，写死在本文件与 mapping JSON 里
  D 只读        运行前后 4 个数据文件的 `(size, mtime_ns)` 必须逐个不变——校验器自己证明自己没写

**为什么不做「`subcortex_coords.csv` ↔ `brainstem_coords.txt` 坐标一致」这条**（#133 验收标准第 4 条的原文）：
实测两文件**没有共同核团**——前者是 14 个皮质下结构（丘脑/尾状核/壳核/…），后者是 69 个脑干标签。
按原文无从比对，故改测**实际存在的两组配对**，并把这件事写进 mapping JSON 的 `_measured_conventions`。

允许清单/对应表: `hansen_intake_mapping.json`（同目录）——`mapped` / `exempt` / `_unverified`
三段；`_unverified` 里的条目（如「subregion1 = 致密部」的编号推定）会在输出里标 ⚠️，
**校验器不为解剖等价性背书**。

来源: data/connectivity/external-sources.md §二 缺口 1（#132 裁定 C）· issue #133
用法: python3 code/tools/validate_hansen_intake.py [--verbose]
退出码: 0 = 四条断言全过, 1 = 有违规
"""

import ast
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

HAN = ROOT / "data/connectivity/hansen2024"
REGION_INFO = HAN / "region_info_Schaefer400.csv"
SUBCORTEX = HAN / "subcortex_coords.csv"
BS_COORDS = HAN / "brainstem_coords.txt"
BS_LABELS = HAN / "brainstem_coords_labels.txt"

MAPPING_FILE = ROOT / "code/tools/hansen_intake_mapping.json"
GENERATOR = ROOT / "code/tools/gen_modulation_ceiling_v2.py"
ESTIMATE_NAME = "BRAINSTEM_COMMUNITY_GAIN_ESTIMATE"

TOL = 1e-3          # 坐标容差：数据文件是定点文本，实测误差为 0；1e-3 给浮点留余量
EXPECTED_BRAINSTEM_ROWS = 58   # 留存文档 §样本参数：Brainstem Navigator 58 个核团


def estimate_keys():
    """用 ast 读生成器源码里 BRAINSTEM_COMMUNITY_GAIN_ESTIMATE 的键（不 import，避开 numpy）。"""
    tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == ESTIMATE_NAME for t in node.targets):
            return [k.value for k in node.value.keys]
    raise SystemExit(f"❌ 在 {GENERATOR.name} 中找不到 {ESTIMATE_NAME}")


def read_csv_rows(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def norm_subcortex_name(s):
    """`Right-thalamusproper` → `rthalamusproper`，与 region_info 的 `R-Thalamus-Proper` 同形。"""
    s = s.strip().lower().replace("-", "").replace("_", "")
    for pre, short in (("right", "r"), ("left", "l")):
        if s.startswith(pre):
            return short + s[len(pre):]
    return s


def file_stamp(path):
    st = path.stat()
    return (st.st_size, st.st_mtime_ns)


def main():
    verbose = "--verbose" in sys.argv
    errors, warnings = [], []

    print("=" * 60)
    print("hansen2024 只读结构校验（#133 · 依 #132 裁定 C）")
    print("=" * 60)

    # ---- D 前置：记下 4 个数据文件的指纹，用于运行后自证只读 ----
    data_files = [REGION_INFO, SUBCORTEX, BS_COORDS, BS_LABELS]
    before = {p: file_stamp(p) for p in data_files}

    mapping = json.loads(MAPPING_FILE.read_text(encoding="utf-8"))
    mapped, exempt = mapping["mapped"], mapping["exempt"]

    rows = read_csv_rows(REGION_INFO)
    ri_labels = {r["labels"] for r in rows}
    ri_by_label = {r["labels"]: r for r in rows}
    bs_coords = [l.split() for l in BS_COORDS.read_text(encoding="utf-8").strip().splitlines()]
    bs_labels = BS_LABELS.read_text(encoding="utf-8").split()
    bs_label_set = set(bs_labels)

    # ---- A 配对完整性 ----
    print("\n[A] 配对完整性")
    if len(bs_coords) != len(bs_labels):
        errors.append(f"brainstem_coords.txt 有 {len(bs_coords)} 行，brainstem_coords_labels.txt 有 "
                      f"{len(bs_labels)} 个标签——逐行配对不成立")
    else:
        print(f"  brainstem_coords.txt ↔ labels：{len(bs_labels)}/{len(bs_labels)} 逐行配对 ✅")
    bs_struct_rows = [r for r in rows if r["structure"] == "brainstem"]
    if len(bs_struct_rows) != EXPECTED_BRAINSTEM_ROWS:
        errors.append(f"region_info 的 structure=brainstem 行数 {len(bs_struct_rows)}，"
                      f"留存文档记的是 {EXPECTED_BRAINSTEM_ROWS}")
    else:
        print(f"  region_info 脑干行：{len(bs_struct_rows)}（与留存文档 §样本参数 的 58 一致）✅")
    missing = sorted(l for l in bs_labels if l not in ri_labels)
    if missing == ["STh_l", "STh_r"]:
        print(f"  同名可查：{len(bs_labels) - len(missing)}/{len(bs_labels)}·"
              f"已知不在 region_info 的：{', '.join(missing)}（登记为已知，不算失败）")
    elif missing:
        errors.append(f"brainstem 标签不在 region_info 的：{missing}（期望只有 STh_l/STh_r）")

    # ---- B 覆盖 ----
    print("\n[B] 覆盖：项目条目逐条有判定")
    keys = estimate_keys()
    print(f"  {ESTIMATE_NAME}：{len(keys)} 条（ast 读源码取得）")
    dup = set(mapped) & set(exempt)
    if dup:
        errors.append(f"同一条目同时出现在 mapped 与 exempt：{sorted(dup)}")
    extra = (set(mapped) | set(exempt)) - set(keys)
    if extra:
        errors.append(f"对应表里有估计表之外/已被删除的条目：{sorted(extra)}")
    undecided = [k for k in keys if k not in mapped and k not in exempt]
    if undecided:
        errors.append(f"没有判定的条目（既未映射也未豁免）：{undecided}")
    for name, spec in sorted(mapped.items()):
        labels = spec.get("labels") or []
        if not labels:
            errors.append(f"条目 `{name}` 标为 mapped 但没有 labels")
            continue
        for lab in labels:
            if lab not in ri_labels and lab not in bs_label_set:
                errors.append(f"条目 `{name}` 映射到 `{lab}`，但该标签不在数据集任何标签表里")
    for name, reason in sorted(exempt.items()):
        if not str(reason).strip():
            errors.append(f"条目 `{name}` 豁免但没有理由")
    if not undecided and not extra and not dup:
        print(f"  {len(mapped)} 条映射 + {len(exempt)} 条豁免 = {len(keys)} ✅")
    for item in mapping.get("_unverified", []):
        warnings.append(item)

    # ---- C 坐标一致 ----
    print("\n[C] 坐标一致（容差 1e-3）")
    ok_flip = mismatch = 0
    for lab, c in zip(bs_labels, bs_coords):
        r = ri_by_label.get(lab)
        if not r:
            continue
        c = [float(v) for v in c]
        rc = [float(r["x"]), float(r["y"]), float(r["z"])]
        flipped = [abs(-c[0] - rc[0]), abs(-c[1] - rc[1]), abs(c[2] - rc[2])]
        same = [abs(a - b) for a, b in zip(c, rc)]
        if max(flipped) <= TOL:
            ok_flip += 1
        else:
            mismatch += 1
            errors.append(f"`{lab}` 在 x/y 反号约定下不一致：coords={c} region_info={rc} "
                          f"（同号差 {max(same):.3g}）")
    print(f"  ① brainstem_coords.txt ↔ region_info（x/y 反号约定）：{ok_flip} 行一致 · {mismatch} 行不符")
    sub_rows = read_csv_rows(SUBCORTEX)
    ri_norm = {norm_subcortex_name(r["labels"]): r for r in rows}
    ok_same = sub_mismatch = unmatched = 0
    for r in sub_rows:
        m = ri_norm.get(norm_subcortex_name(r[""]))
        if not m:
            unmatched += 1
            errors.append(f"subcortex_coords.csv 的 `{r['']}` 在 region_info 中找不到同名行")
            continue
        c = [float(r["x"]), float(r["y"]), float(r["z"])]
        rc = [float(m["x"]), float(m["y"]), float(m["z"])]
        if max(abs(a - b) for a, b in zip(c, rc)) <= TOL:
            ok_same += 1
        else:
            sub_mismatch += 1
            errors.append(f"subcortex `{r['']}` 与 region_info `{m['labels']}` 坐标不符：{c} vs {rc}")
    print(f"  ② subcortex_coords.csv ↔ region_info（同号）：{ok_same} 行一致 · {sub_mismatch} 行不符 · "
          f"{unmatched} 行对不上名")
    if verbose:
        print("  约定实测（来自 mapping JSON）：")
        for k, v in mapping["_measured_conventions"].items():
            print(f"    {k}：{v}")

    # ---- D 只读自证 ----
    print("\n[D] 只读自证（运行前后数据文件指纹）")
    wrote = [p for p in data_files if file_stamp(p) != before[p]]
    if wrote:
        errors.append(f"校验器改动了数据文件：{[str(p.relative_to(ROOT)) for p in wrote]}")
    else:
        print(f"  {len(data_files)} 个数据文件的 (size, mtime) 逐个不变 ✅")

    if warnings:
        print()
        for w in warnings:
            print(f"⚠️  {w}")
    if errors:
        print()
        for e in errors:
            print(f"❌ {e}")
        print(f"\n{'=' * 60}\n❌ {len(errors)} 处违规\n{'=' * 60}")
        return 1

    print(f"\n{'=' * 60}\n✅ 全部通过（{len(keys)} 条条目逐条有判定；两组坐标配对一致；只读）\n{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
