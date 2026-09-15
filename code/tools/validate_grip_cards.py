#!/usr/bin/env python3
"""validate_grip_cards.py — 手部基准卡片的机械判据（#164）

**判据：卡片的"人类契约（口径 §十三）"与"机器源（`data/hand_grip_cards.json`）"
与"证据（回显卡）"三处不许互相漂移。**

为什么需要它（#164 的动机）：口径 §十三 于 2026-09-15 被 owner 逐题接受，但**数值一格未测**、
机器源不存在 ⇒ 与 Grilling #85 同形（**规范完整、落库、过全部门禁、零效果**）。本校验器把
"卡片还在管用"这件事钉成每次自动发现的判据，而不是留在散文里。

四条规则（每条都指得出**冲突的两个来源**）：

| # | 规则 | 冲突面 |
|---|---|---|
| R1 | 名录（口径 §13.6 表）里存在一行，其**索引键**与 json 的 `F1_索引键` **逐字相同** | md 名录 ↔ json |
| R2 | 该行的**判据形态**列覆盖 json `F5_判据形态与容差档.形态` 里出现的每个形态名，且每个形态名 ∈ §13.4 的**受控枚举 5 种** | md 名录 ↔ json ↔ 枚举 |
| R3 | 该行的**状态**列已回填（json 存在时不得再写"待实测"） | md 名录 ↔ json 存在性 |
| R4 | json 的**接触对清单行数** == 证据文件「回显卡」表的**行数**（口径 §13.2："接触对清单 = 回显卡行清单"） | json ↔ 证据 |
| R5 | `F7_改族阈值与越界落点.改族边` 的每条有向边两端**都能在名录里找到**（无悬挂）；越界落点必须写明归属 | json ↔ md 名录 |

**契约（R4 的解析面，写在这里以免靠猜）**：证据文件里**第一个标题含「回显卡」的段落**之下、
**第一张 markdown 表**的数据行数（不含表头行与 `|---|` 分隔行）= 回显卡行数。
⇒ 证据文件的回显卡必须是"一对接一行"的表，且**由 json 的同一份清单生成**（生成一次、抄一次都不许）。

来源: design/presentation/动作描述口径.md §13.2/§13.4/§13.6 · issue #164
用法: python3 code/tools/validate_grip_cards.py [--format json]
退出码: 0 = 四条规则全过, 1 = 有违规
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CARDS_JSON = ROOT / "data/hand_grip_cards.json"
KOUJING_MD = ROOT / "design/presentation/动作描述口径.md"
EVIDENCE_MD = ROOT / "design/engineering/evidence/hand-grip-cards-2026-09-15.md"

#: 判据形态的**受控枚举**（口径 §13.4，5 种）——json 里出现别的写法即违规
FORM_ENUM = ("点↔面", "点↔线", "平面↔平面", "弧面↔面", "弧面↔弧面")
#: 名录里"本片做"的那张卡的编号（§13.6）
CARD_ROW_RE = re.compile(r"^\|\s*\*{0,2}(卡\s*(\d+))\*{0,2}\s*\|(.+)\|\s*$")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_roster(md_text):
    """口径 §13.6 的**卡片名录**：`卡 N → {索引键, 判据形态, 服务需求, 状态}`。

    只认"卡 N"开头的表行；索引键取第一列括号前的部分并去掉 `**`（如 `**掐棱**（虎口跨一条板棱）` → `掐棱`）。
    """
    out = {}
    for line in md_text.splitlines():
        m = CARD_ROW_RE.match(line)
        if not m:
            continue
        c = cells(line)
        if len(c) < 5:
            continue
        key_raw = c[1]
        key = re.sub(r"[*`]", "", key_raw.split("（")[0].split("(")[0]).strip()
        out[f"卡{m.group(2)}"] = {"索引键": key, "判据形态": c[2], "服务需求": c[3], "状态": c[4],
                                  "行": line.strip()}
    return out


def parse_feedback_card_rows(md_text):
    """证据文件里**第一个标题含「回显卡」的段落**下的第一张表的数据行数（见模块 docstring 的契约）。"""
    lines = md_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith("#") and "回显卡" in line:
            start = i
            break
    if start is None:
        return None, "证据文件里找不到含「回显卡」的标题"
    rows, seen_table = 0, False
    for line in lines[start + 1:]:
        if line.startswith("#"):
            break
        if line.strip().startswith("|"):
            if re.match(r"^\|[\s:\-|]+\|$", line.strip()):
                seen_table = True
                continue
            if seen_table:
                rows += 1
        elif seen_table and line.strip():
            break
    if not seen_table:
        return None, "「回显卡」段落里没有 markdown 表"
    return rows, None


def main():
    ap = argparse.ArgumentParser(description="手部基准卡片校验（#164）")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--output", "-o")
    args = ap.parse_args()

    findings = []          # (level, rule, message)
    checks = 0

    if not CARDS_JSON.is_file():
        findings.append(("FAIL", "R0", f"机器源不存在：{CARDS_JSON.relative_to(ROOT)}——"
                                       f"卡 1 的数值必须由 `code/tools/author_xbot_chair_grab.py --task card1` 产出"))
        data = None
    else:
        data = json.loads(CARDS_JSON.read_text(encoding="utf-8"))

    md = KOUJING_MD.read_text(encoding="utf-8") if KOUJING_MD.is_file() else ""
    roster = parse_roster(md)
    if not roster:
        findings.append(("FAIL", "R1", "口径 §13.6 名录里解析不出任何「卡 N」行"))

    if data:
        meta = data.get("_meta", {})
        cards = data.get("cards", [])
        checks += 1
        if not isinstance(cards, list) or not cards:
            findings.append(("FAIL", "R0", "json 里没有 cards 数组或为空"))
        # --- R1 名录 ↔ json：索引键逐字一致 ---
        for card in cards:
            key = card.get("F1_索引键")
            checks += 1
            hit = [cid for cid, row in roster.items() if row["索引键"] == key]
            if not hit:
                findings.append(("FAIL", "R1", f"json 的索引键 {key!r} 在口径 §13.6 名录里找不到对应行"))
                continue
            cid = hit[0]
            # --- R2 判据形态：名录列须覆盖 json 的每个形态名，且都在受控枚举里 ---
            forms = card.get("F5_判据形态与容差档", {}).get("形态", [])
            checks += 1
            for f in forms:
                token = f.split("（")[0].split("(")[0].strip()
                if token not in FORM_ENUM:
                    findings.append(("FAIL", "R2", f"{cid} 的判据形态 {token!r} 不在 §13.4 的受控枚举 "
                                                f"{list(FORM_ENUM)} 里"))
                if token not in roster[cid]["判据形态"]:
                    findings.append(("FAIL", "R2", f"{cid} 的判据形态 {token!r} 没有出现在名录该行"
                                                f"（名录写的是 {roster[cid]['判据形态']!r}）"))
            # --- R3 名录状态已回填 ---
            checks += 1
            if "待实测" in roster[cid]["状态"]:
                findings.append(("FAIL", "R3", f"{cid} 的机器源已存在，而名录状态仍写「待实测」"
                                              f"（{roster[cid]['状态']!r}）"))
            # --- R5 改族边无悬挂 ---
            edges = card.get("F7_改族阈值与越界落点", {}).get("改族边", []) or []
            for e in edges:
                checks += 1
                tgt = e.get("to", "")
                tgt_key = re.sub(r"^卡\s*", "", tgt)
                tgt_cid = f"卡{tgt_key}"
                if tgt_cid not in roster:
                    findings.append(("FAIL", "R5", f"{cid} 的改族边指向 {tgt!r}，而名录里没有 {tgt_cid}"
                                                  f"（悬挂边）"))
            # 越界落点必须写明归属
            for side_name, landing in (card.get("F7_改族阈值与越界落点", {})
                                       .get("越界落点", {}) or {}).items():
                checks += 1
                if not isinstance(landing, dict) or not landing.get("落点"):
                    findings.append(("FAIL", "R5", f"{cid} 的越界落点「{side_name}」没写明落点"))

        # --- R4 接触对行数 == 回显卡行数 ---
        checks += 1
        if not EVIDENCE_MD.is_file():
            findings.append(("FAIL", "R4", f"证据文件不存在：{EVIDENCE_MD.relative_to(ROOT)}"
                                           f"（回显卡行数的唯一来源）"))
        else:
            ev = EVIDENCE_MD.read_text(encoding="utf-8")
            ev_rows, err = parse_feedback_card_rows(ev)
            pair_rows = sum(len(c.get("F4_分区分工与接触对清单", [])) for c in cards)
            if err:
                findings.append(("FAIL", "R4", err))
            elif ev_rows != pair_rows:
                findings.append(("FAIL", "R4", f"接触对行数 {pair_rows} != 证据回显卡行数 {ev_rows}"
                                               f"（口径 §13.2：接触对清单 = 回显卡行清单）"))

    passed = sum(1 for lvl, _r, _m in findings if lvl == "PASS")
    failed = [f for f in findings if f[0] == "FAIL"]
    warned = [f for f in findings if f[0] == "WARN"]

    if args.format == "json":
        out = json.dumps({
            "script": "validate_grip_cards.py",
            "timestamp": datetime.now().isoformat(),
            "summary": {"total": checks, "passed": checks - len(failed), "blocker": len(failed),
                        "warn": len(warned), "info": 0},
            "blocker": [{"rule": r, "reason": m} for _l, r, m in failed],
            "warn": [{"rule": r, "reason": m} for _l, r, m in warned],
            "info": [], "passed": passed,
        }, ensure_ascii=False, indent=2)
    else:
        lines = ["# validate_grip_cards.py — 手部基准卡片校验（#164）\n", "## 检查范围",
                 f"- 机器源：`{CARDS_JSON.relative_to(ROOT)}`"
                 f"（{'存在' if CARDS_JSON.is_file() else '**不存在**'}）",
                 f"- 人类契约：`{KOUJING_MD.relative_to(ROOT)}` §13.6 名录（解析到 {len(roster)} 张卡）",
                 f"- 证据：`{EVIDENCE_MD.relative_to(ROOT)}`（回显卡行数的唯一来源）\n",
                 "## 结果"]
        for lvl, rule, msg in findings:
            lines.append(f"{lvl}  {rule}  {msg}")
        if not findings:
            lines.append(f"PASS  R1-R5  {checks} 项判据全过")
        lines += ["", "## 汇总",
                  f"{checks} checks: {checks - len(failed)} passed, {len(failed)} failed"]
        out = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
