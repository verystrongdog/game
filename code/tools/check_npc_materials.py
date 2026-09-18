#!/usr/bin/env python3
"""check_npc_materials.py — NPC 素材跨字段一致性**报告**（只报不拦 · 非门禁）

## 这是什么
把 2026-09-18 那一轮人肉审计里**机械可判**的那部分固化下来。判据全是
**跨字段一致性**（同一个事实在两个地方必须对得上），不是"参数须落在某区间"
那类需要容差与例外表的判据——**需要例外表才能活的判据，本脚本一律不收**。

## 与 2026-09-17「撤销全部门禁」的关系
那一次撤掉的是 **26 个专用校验器 + 两张人工例外表（validate_*_exceptions.json）
+ gates.json 注册表 + 三个 CI 门禁 job**。本脚本刻意不是它们：
  · 单文件 · 只用 stdlib · 不建任何例外表 · **默认永不失败**（report-only）
  · 进 CI 的形态 = 只产出报告 artifact，红叉都不给（`continue-on-error: true`）
  · `--strict` 只给本地开发用（那时它才是门禁，且只挡你自己）

## 用法
    python3 code/tools/check_npc_materials.py              # 报告，永远 exit 0
    python3 code/tools/check_npc_materials.py --strict     # 有 🔴 时 exit 1（本地）
    python3 code/tools/check_npc_materials.py --json out.json
    python3 code/tools/check_npc_materials.py --only ages,links

## 判据清单（每项都对应一次真实事故）
    json        JSON 可解析（25 份 gen.json + registry + manifest）
    manifest    manifest ↔ 磁盘 ↔ 患者生态索引 机器核对区 三者一致
    ages        出生年 + 年份 = 年龄（带 birth_month 豁免）
    bands       档位 × 阈值 必须同档（周桂芳那次：档位=中度 却挂 [1.0,2.0)）
    lifespan    年份非降序；同 (年,事件) 重复
    crossview   md 与 .gen.json 的关键字段一致（入院年龄/年份/病区）
    city        入院城市白名单（临水/省城）——其余命中按性质分 🔴/🟡
    links       相对链接不死（撤销前最后一次读数：2163 引用 / 0 死链）
    terms       注册表驱动的废弃术语残留（分档：扫描🔴 列明细 / 只登记🟡 只计数 / 关闭ℹ️ 打印存量）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DRAFTS = ROOT / "design" / "spec" / "material" / "drafts"
MANIFEST = ROOT / "design" / "spec" / "material" / "npc-materials-manifest.json"
INDEX = ROOT / "design" / "spec" / "material" / "患者生态索引.md"
# 第二处机器核对区：多样性记账表自称"患者集合与 manifest 机械核对"——
# 既然同一事实有两个登记处，两处都必须对得上（判据同 index，见 check_manifest）
DIVERSITY = ROOT / "design" / "spec" / "material" / "多样性记账表.md"
REGISTRY = ROOT / "data" / "term_registry.json"

# 入院城市白名单：正典见 design/events/世界观与叙事.md §医院与所在城市
CITY_OK = ("临水", "省城")
# 出现这些词的行视为「籍贯 / 自检 / 来历」语境，不算入院地残留
CITY_CONTEXT_WHITELIST = (
    "个体合法性", "出生", "籍贯", "生于", "老家", "大学", "毕业", "打工", "家属",
    "母亲", "父亲", "女儿", "儿子", "妻子", "丈夫", "婆婆", "奶奶", "姥姥",
    "转诊", "转院", "火车", "长途", "南下", "分配到", "招工", "考编",
)
CITY_NAMES = (
    "哈尔滨", "沈阳", "铁西", "长春", "北京", "天津", "上海", "南京", "苏州", "无锡",
    "杭州", "宁波", "合肥", "青岛", "武汉", "长沙", "南昌", "郑州", "广州", "深圳",
    "东莞", "佛山", "海口", "成都", "重庆", "万州", "昆明", "贵阳", "贵州", "西安",
    "兰州", "乌鲁木齐", "太原", "吕梁", "石家庄", "沧州", "呼和浩特",
)

RED, YELLOW, INFO = "🔴", "🟡", "ℹ️"


class Report:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str, str]] = []  # (severity, check, where, msg)

    def add(self, sev: str, check: str, where: str, msg: str) -> None:
        self.rows.append((sev, check, where, msg))

    def count(self, sev: str) -> int:
        return sum(1 for r in self.rows if r[0] == sev)

    def render(self) -> str:
        out: list[str] = []
        order = {RED: 0, YELLOW: 1, INFO: 2}
        for sev in (RED, YELLOW, INFO):
            rows = [r for r in self.rows if r[0] == sev]
            if not rows:
                continue
            out.append(f"\n{'=' * 78}\n{sev}  {len(rows)} 条\n{'=' * 78}")
            for _, check, where, msg in sorted(rows, key=lambda r: (r[1], r[2])):
                out.append(f"[{check}] {where}\n    {msg}")
        head = (
            f"NPC 素材一致性报告 —— 🔴 {self.count(RED)} · 🟡 {self.count(YELLOW)} · "
            f"ℹ️ {self.count(INFO)}\n"
            "（只报不拦：本脚本默认 exit 0；--strict 才在 🔴>0 时失败）"
        )
        return head + "\n".join(out)

    def to_json(self) -> dict:
        return {
            "summary": {"red": self.count(RED), "yellow": self.count(YELLOW), "info": self.count(INFO)},
            "rows": [{"sev": s, "check": c, "where": w, "msg": m} for s, c, w, m in self.rows],
        }


def load_json(path: Path, rep: Report):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — 报告工具，任何解析失败都要报出来而不是崩
        rel = path.relative_to(ROOT)
        rep.add(RED, "json", str(rel), f"JSON 解析失败：{exc}")
        return None


def gen_files() -> list[Path]:
    return sorted(DRAFTS.glob("*.gen.json"))


# ── 各判据 ────────────────────────────────────────────────────────────────


def check_json(rep: Report) -> None:
    files = gen_files() + [MANIFEST, REGISTRY]
    for f in files:
        load_json(f, rep)
    rep.add(INFO, "json", "—", f"已解析 {len(files)} 份 JSON（gen.json {len(gen_files())} 份）")


def check_manifest(rep: Report) -> None:
    man = load_json(MANIFEST, rep)
    if not man:
        return
    mats = man.get("materials", [])
    if len(mats) != man.get("expected_material_count"):
        rep.add(
            RED, "manifest", "npc-materials-manifest.json",
            f"entries={len(mats)} 但 expected_material_count={man.get('expected_material_count')}",
        )
    patients = [m for m in mats if m.get("patient_pool")]
    if len(patients) != man.get("expected_patient_count"):
        rep.add(
            RED, "manifest", "npc-materials-manifest.json",
            f"patient_pool=true 的条目={len(patients)} 但 expected_patient_count={man.get('expected_patient_count')}",
        )
    for m in mats:
        for key in ("json_path", "narrative_path"):
            p = ROOT / (m.get(key) or "")
            if not p.exists():
                rep.add(RED, "manifest", m.get("name", "?"), f"{key} 指向不存在的文件：{m.get(key)}")

    # 与 患者生态索引 的机器核对区对齐
    if INDEX.exists():
        text = INDEX.read_text(encoding="utf-8")

        def region(tag: str) -> list[str]:
            mm = re.search(rf"<!-- {tag}:start -->(.*?)<!-- {tag}:end -->", text, re.S)
            return re.findall(r"^-\s*(\S+)", mm.group(1), re.M) if mm else []

        pool, nonpool = region("npc-patient-pool"), region("npc-non-patient-materials")
        man_pool = [m["name"] for m in patients]
        if set(pool) != set(man_pool):
            rep.add(
                RED, "manifest", "患者生态索引.md ↔ manifest",
                f"患者池不一致：索引 {len(pool)} 位 {sorted(set(pool) ^ set(man_pool)) or ''} vs manifest {len(man_pool)} 位",
            )
        man_non = [m["name"] for m in mats if not m.get("patient_pool")]
        legacy = {"刘建军", "周桂芳", "郑晓敏"}  # 索引里的 #89 三行遗留表，新非患者稿按台账另记
        missing = sorted(set(man_non) - set(nonpool) - legacy)
        if missing:
            rep.add(
                INFO, "manifest", "患者生态索引.md ↔ manifest",
                f"manifest 中不在索引非患者遗留表里的（预期，见台账 §七⑤）：{missing}",
            )

    # 第二处登记处：多样性记账表自称"患者集合与 manifest 机械核对" ⇒ 同一判据
    if DIVERSITY.exists():
        text = DIVERSITY.read_text(encoding="utf-8")
        mm = re.search(r"<!-- npc-patient-pool:start -->(.*?)<!-- npc-patient-pool:end -->", text, re.S)
        if not mm:
            rep.add(YELLOW, "manifest", "多样性记账表.md", "找不到 npc-patient-pool 机器核对区（该表自称与 manifest 核对）")
        else:
            div = re.findall(r"^-\s*(\S+)", mm.group(1), re.M)
            man_pool = [m["name"] for m in patients]
            if set(div) != set(man_pool):
                rep.add(
                    RED, "manifest", "多样性记账表.md ↔ manifest",
                    f"患者池不一致：记账表 {len(div)} 位 {sorted(set(div) ^ set(man_pool)) or ''} vs manifest {len(man_pool)} 位",
                )


def _num(x):
    try:
        return int(str(x)[:4])
    except (TypeError, ValueError):
        return None


def check_ages(rep: Report) -> None:
    for f in gen_files():
        d = load_json(f, rep)
        if not d:
            continue
        rel = f.relative_to(ROOT)
        ident = d.get("identity") or {}
        by, ay, yy = _num(ident.get("birth_year")), _num(ident.get("入院年龄")), _num(ident.get("入院年份"))
        has_month = ident.get("birth_month") is not None  # 有月份 ⇒ 允许「生日未到」的 -1
        if by and yy and ay is not None:
            exp = yy - by
            if ay != exp and not (has_month and ay == exp - 1):
                rep.add(RED, "ages", str(rel), f"入院年龄 {ay} ≠ {yy}-{by}={exp}（且无 birth_month 豁免）")
        for e in d.get("lifespan") or []:
            y, a = _num(e.get("year")), _num(e.get("age"))
            if by and y and a is not None:
                exp = y - by
                if a != exp and not (has_month and a == exp - 1):
                    rep.add(
                        RED, "ages", str(rel),
                        f"lifespan {y} 年写 {a} 岁，应为 {exp} 岁｜{str(e.get('event'))[:36]}",
                    )


def check_bands(rep: Report) -> None:
    band_of = {"[1.0,2.0)": "轻", "[2.0,3.0)": "中度", "[3.0,∞)": "重"}

    def walk(o, rel, path=""):
        if isinstance(o, dict):
            b, t = o.get("档位"), o.get("阈值")
            if isinstance(b, str) and isinstance(t, str) and b != "∅":
                exp = next((v for k, v in band_of.items() if t.startswith(k)), None)
                if exp and b != exp:
                    rep.add(RED, "bands", f"{rel}{path}", f"档位={b} 但阈值={t}（该区间对应 {exp}）")
            for k, v in o.items():
                walk(v, rel, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, rel, f"{path}[{i}]")

    for f in gen_files():
        d = load_json(f, rep)
        if d:
            walk(d, f.relative_to(ROOT))


def check_lifespan(rep: Report) -> None:
    for f in gen_files():
        d = load_json(f, rep)
        if not d:
            continue
        rel = f.relative_to(ROOT)
        nums = []
        for e in d.get("lifespan") or []:
            raw = e.get("year")
            y = raw if isinstance(raw, int) else None  # 「1980s-2010s」这类时期串不参与升序判断
            if y is not None:
                nums.append((raw, y))
        prev = None
        for raw, y in nums:
            if prev is None:
                prev = y
                continue
            if y < prev:
                rep.add(YELLOW, "lifespan", str(rel), f"年份非升序（或时期串）：{prev} → {y}（{raw!r}）")
            prev = y
        seen: dict[tuple, int] = {}
        for e in d.get("lifespan") or []:
            key = (str(e.get("year")), str(e.get("event"))[:24])
            seen[key] = seen.get(key, 0) + 1
        for k, n in seen.items():
            if n > 1:
                rep.add(YELLOW, "lifespan", str(rel), f"重复条目 ×{n}：{k[0]} {k[1]}")


def check_crossview(rep: Report) -> None:
    """md ↔ .gen.json 的关键字段一致（同一事实源的两个视图）。"""
    for f in gen_files():
        d = load_json(f, rep)
        if not d:
            continue
        md = DRAFTS / (f.name[: -len(".gen.json")] + "-叙事视图.md")
        if not md.exists():
            rep.add(RED, "crossview", str(f.relative_to(ROOT)), "找不到同名叙事视图")
            continue
        text, rel = md.read_text(encoding="utf-8"), md.relative_to(ROOT)
        ident = d.get("identity") or {}

        # ① 入院年龄必须与正文自检行一致（有 birth_month 时允许「生日未到」的 ±1）
        ay = ident.get("入院年龄")
        exp_ay = {int(ay)} if ay is not None else set()
        if ay is not None and ident.get("birth_month") is not None:
            exp_ay.add(int(ay) + 1)
        for m in re.finditer(r"(\d+)\s*岁入院", text):
            if exp_ay and int(m.group(1)) not in exp_ay:
                rep.add(RED, "crossview", str(rel), f"正文自检「{m.group(0)}」≠ gen.identity.入院年龄 {ay}")
        # ② 病区与性别一致（B1 男区 / B2 女区）
        ward = re.search(r"B 病区\s*(B[12])\s*(男|女)区", text)
        if ward:
            want = {"B1": "男", "B2": "女"}[ward.group(1)]
            if ward.group(2) != want:
                rep.add(RED, "crossview", str(rel), f"{ward.group(0)} 自身矛盾（{ward.group(1)} 应为{want}区）")
            gender = ident.get("gender")
            if gender and gender != want:
                rep.add(RED, "crossview", str(rel), f"病区写 {ward.group(1)}（{want}区）但 identity.gender={gender}")
        # ③ 诊断名（gen 写了的）应能在正文出现
        sp = d.get("symptoms_presentation") or {}
        diag = sp.get("当前诊断") or (d.get("transformation", {}).get("disease_profile") or {}).get("主病")
        if isinstance(diag, str) and len(diag) >= 3:
            core = re.split(r"[（(，,、]", diag)[0].strip()
            # 正文常直接写缩写（SSD/GAD/DID/MDD），二选一命中即可
            abbr = re.findall(r"[A-Z]{2,5}", diag)
            if core and core not in text and not any(a in text for a in abbr):
                rep.add(YELLOW, "crossview", str(rel), f"gen 诊断「{core}」在正文里找不到对应表述")
        # ④ 同一事实源的「入院方式」若提及城市，必须是临水口径
        way = json.dumps(sp, ensure_ascii=False)
        for c in CITY_NAMES:
            if c in way and "临水" not in way:
                rep.add(RED, "crossview", str(f.relative_to(ROOT)), f"symptoms_presentation 提及 {c} 但无临水口径")


def check_city(rep: Report) -> None:
    """入院地城市白名单：句子含入院/转/送 + 非白名单城市 ⇒ 🔴；其余共现 ⇒ 🟡。"""
    for md in sorted(DRAFTS.glob("*-叙事视图.md")):
        text, rel = md.read_text(encoding="utf-8"), md.relative_to(ROOT)
        for ln, line in enumerate(text.split("\n"), 1):
            if line.startswith(">") or any(w in line for w in CITY_CONTEXT_WHITELIST):
                continue
            for m in re.finditer(r"[^。；\n]{0,50}(?:入院|转入|转到|送进|住院|精神卫生中心)[^。；\n]{0,50}", line):
                seg = m.group(0)
                hit = [c for c in CITY_NAMES if c in seg]
                if not hit:
                    continue
                if any(o in seg for o in CITY_OK):
                    continue
                if re.search(rf"(?:{'|'.join(hit)})\s*(?:某|市|省)?\s*(?:的)?\s*(?:精神卫生中心|医院)", seg):
                    rep.add(RED, "city", f"{rel}:{ln}", f"入院机构带非临水城市：…{seg.strip()[:60]}…")
                else:
                    rep.add(YELLOW, "city", f"{rel}:{ln}", f"入院语境出现 {hit}：…{seg.strip()[:60]}…（请人工确认是否为籍贯/来历）")


# 判定面之外：归档 / 已废弃 / 已冻结（decisions）目录 —— 历史记录里的链接指向当年路径，
# 本就不该要求它们存活（这不是例外表，是"这些文档不是活跃正典"这条既有事实）
OUT_OF_SCOPE_DIRS = ("/archive/", "/deprecated/", "/decisions/")
# 占位符式链接（散文里的格式示例，不是真引用）
PLACEHOLDER_TARGETS = {"path", "url", "link", "路径", "相对路径", "xxx.md", "文件名"}


def check_links(rep: Report) -> None:
    roots = [ROOT / "design", ROOT / "reference"]
    n = 0
    skipped = 0
    for root in roots:
        for md in sorted(root.rglob("*.md")):
            rel_md = "/" + str(md.relative_to(ROOT)).replace("\\", "/")
            if any(d in rel_md for d in OUT_OF_SCOPE_DIRS):
                skipped += 1
                continue
            base = md.parent
            for raw in re.findall(r"\]\(([^)\s]+)\)", md.read_text(encoding="utf-8")):
                if raw.startswith(("http", "#", "mailto:")):
                    continue
                if raw.strip() in PLACEHOLDER_TARGETS or "xxx" in raw:
                    continue
                n += 1
                target = (base / urllib.parse.unquote(raw.split("#")[0])).resolve()
                if not target.exists():
                    rep.add(RED, "links", str(md.relative_to(ROOT)), f"死链 → {raw}")
    rep.add(
        INFO, "links", "—",
        f"检查相对链接 {n} 条（design/ + reference/，已跳过归档/废弃目录 {skipped} 份文档）",
    )


def check_terms(rep: Report) -> None:
    reg = load_json(REGISTRY, rep)
    if not reg:
        return
    terms = reg.get("terms", {})
    dep = {k: v for k, v in terms.items() if v.get("status") == "deprecated"}
    docs = [
        p for p in (ROOT / "design").rglob("*.md")
        if "archive" not in p.parts and "decisions" not in p.parts and "deprecated" not in p.parts
    ] + [ROOT / "reference" / "灵感收件箱.md"]
    # 允许出现在「已标注废弃/旧值」的行里 —— 这是 AGENTS §二 的既有写法约定，不是例外表
    MARKERS = ("已废弃", "废弃", "旧值", "旧参数", "deprecated", "superseded", "DEPRECATED")
    for term, meta in sorted(dep.items()):
        mode = meta.get("enforcement") or "扫描"  # 缺字段 ⇒ fail-closed 按扫描处理
        sev = {"扫描": RED, "只登记": YELLOW, "关闭": INFO}.get(mode, RED)
        hits: list[str] = []
        # ASCII 术语必须整词命中（避免 f_lunar 被当成 lunar）
        pat = (
            re.compile(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])")
            if term.isascii()
            else re.compile(re.escape(term))
        )
        for md in docs:
            if not md.exists():
                continue
            for ln, line in enumerate(md.read_text(encoding="utf-8").split("\n"), 1):
                if pat.search(line) and not any(k in line for k in MARKERS):
                    hits.append(f"{md.relative_to(ROOT)}:{ln}")
        if hits:
            # 三档语义（design/conventions/README.md §五 第 2 条）：
            #   扫描 = 判残留（列明细）；只登记 = 不判、**只计数不列明细**（该串另有合法用法，
            #   逐串匹配分不出新旧义）；关闭 = 不判，但现存量每次打印（欠账在明处）。
            msg = (
                f"{len(hits)} 处命中（`只登记` 档：只计数、不列明细——该串在活跃文本里另有合法用法）"
                if mode == "只登记"
                else f"{len(hits)} 处残留，前几处：{hits[:4]}"
            )
            rep.add(sev, "terms", f"{term}（{mode}）", msg)
    rep.add(INFO, "terms", "—", f"deprecated 术语 {len(dep)} 条已扫（分档：扫描=🔴 / 只登记=🟡 / 关闭=ℹ️）")


CHECKS = {
    "json": check_json,
    "manifest": check_manifest,
    "ages": check_ages,
    "bands": check_bands,
    "lifespan": check_lifespan,
    "crossview": check_crossview,
    "city": check_city,
    "links": check_links,
    "terms": check_terms,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="NPC 素材跨字段一致性报告（只报不拦）")
    ap.add_argument("--strict", action="store_true", help="有 🔴 时 exit 1（本地用；CI 不用）")
    ap.add_argument("--json", dest="json_out", help="把结构化报告写到该路径")
    ap.add_argument("--only", help="只跑这些判据，逗号分隔：" + ",".join(CHECKS))
    args = ap.parse_args()

    rep = Report()
    names = list(CHECKS) if not args.only else [n.strip() for n in args.only.split(",") if n.strip()]
    for n in names:
        if n not in CHECKS:
            print(f"未知判据：{n}（可选：{','.join(CHECKS)}）", file=sys.stderr)
            return 2
        CHECKS[n](rep)

    print(rep.render())
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(rep.to_json(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\n结构化报告 → {args.json_out}")
    return 1 if (args.strict and rep.count(RED)) else 0


if __name__ == "__main__":
    sys.exit(main())
