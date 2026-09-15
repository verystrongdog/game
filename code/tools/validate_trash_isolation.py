#!/usr/bin/env python3
"""
垃圾桶隔离校验 — 验证"活跃文档不引用垃圾桶内容"规则。

检查项:
  1. 活跃 .md 文件中是否引用了**已移出的垃圾桶内容**（`design/archive/trash/<子路径>` / `.trash/<子路径>`）
  2. 活跃 .md 文件中是否出现了 #20 已废弃的术语（**硬编码表 7 条正则**——本 issue 正文写「6 类」，实为 7 条：`37` 有两种写法；判定与 2026-09-13 版逐条一致）
  3. 活跃 .md 文件中的链接是否指向垃圾桶
  4. **注册表驱动**（#159，2026-09-15）：扫 `design/` + `reference/` 活跃文档，按
     `data/term_registry.json` 各条 `status: deprecated` 的 **`enforcement` 逐术语执法策略**
     （`扫描` / `只登记` / `关闭`，**缺省即 `扫描`**）判废弃术语残留

> **2026-09-15 变更（#159）**：检查 2 的正则表**硬编码**、不读注册表 —— 于是"只标 `status`
> 不加门禁"这一形态在设计文档这侧**无机器可达**（`list_deprecated_terms.py` 读注册表却从不被 CI 执行）。
> 检查 4 补上这条链路。为什么不是"读 `status` 就完事"：23 条 deprecated 里 `AP` 是 `APP`/`API`
> 的子串、`β`/`η`/`κ` 在活跃公式里另有合法用法、`态度` 是日常中文词 ⇒ 盲目动态扫描会产出数百条
> 假阳性（实测 `AP` 143 / `态度` 118 / `β` 77 处，未做豁免时）。故必须有**逐术语**的三档策略。
> **检查 2 的判定结果不因本次变更而变**（文件集、正则、豁免词、豁免前缀均未动）。

**2026-09-13 变更**：原 `design/archive/trash/` 的 26 个文件已**整份移出仓库**，
本地保留在 `.trash/`（见 `.gitignore`）。因此本校验**不再维护"垃圾桶里有哪些文件"的
枚举清单**——那类清单只能守住被枚举过的实例：实测一份**行内代码形式的新子路径引用**
（`design/archive/trash/deprecated-scripts/test_evolved_cog.py`）正是这样空过的
（旧的 `FILES_IN_TRASH` 只有 7 个文件名，且只比对 markdown 链接）。现在只判一件事：
**活跃文档不得指向垃圾桶下的任何内容**，与桶里当时有什么无关。

用法: python code/tools/validate_trash_isolation.py [--verbose]
退出码: 0 = 全部通过, 1 = 有问题
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

# 共享工具（`md_utils`）：注册表驱动的判定面 = design/ + reference/ 活跃文档（SCAN_ROOTS），
# 归档 / 决策树 / reference/deprecated 由它排除。与 run_all_checks.py 同一取道方式。
sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.md_utils import (              # noqa: E402
    collect_md_files,
    find_deprecated_section_end,
    is_deprecated_section,
)

# ── 已移出的垃圾桶（2026-09-13） ──────────────────────────
# 判据 = 「指向垃圾桶下的内容」，与桶里有哪些文件无关：
#   · `design/archive/trash/<子路径>`（原位置，已移出仓库）
#   · `.trash/<子路径>`（新位置，本地保留、gitignore——引用它对别人就是死引用）
#   · `垃圾桶/<子路径>`（历史叫法）
# 只写目录本身（`design/archive/trash/`，用于定义该规则/记载变迁）**不算引用**；
# **占位写法也不算**——`<`/`>` 已从匹配字符类中排除，故 `design/archive/trash/<子路径>`
# 这种"描述规则"的写法不会误报（制定本检查时自己踩到，见下）。
TRASH_REF = re.compile(r"(?:design/archive/trash/|\.trash/|垃圾桶/)[^\s)`\"（），,；;：:<>]{2,}")

# 行内含这些标记 = 该行是在**记载变迁或标注废弃**，不判违规（沿用旧检查的豁免惯例）
DEPRECATION_MARKERS = ("⚠️", "已废弃", "已移出", "迁出", "迁至")

# ── 废弃术语 (#20) ────────────────────────────────────────

DEPRECATED_TERMS = [
    # (正则, 描述, 行内豁免词, 文件豁免前缀)
    (
        r"37\s*个?\s*(操作|技能)(?![项决])",
        "37个操作/技能 (D20 已废弃)",
        ["⚠️", "已废弃", "D20", "#20", "决策树"],
        ["design/decisions/"],
    ),
    # 表格中的裸 37: "37 (L0-L5)" 或 "37(L0-L5)"
    (
        r"\b37\b\s*\(?L\d",
        "37 (L0-L5) 旧技能计数 (D20 已废弃, L6已删除 #25)",
        ["⚠️", "已废弃", "D20", "#20", "决策树"],
        ["design/decisions/", "design/framework/grilling"],
    ),
    (
        r"激活点预算",
        "激活点预算 (玩家侧已改聚焦容量 D4/D7)",
        ["⚠️", "已废弃", "范式修正", "#20"],
        [
            "design/decisions/",
            "design/pipeline/预烘焙管线脚本设计.md",
            "design/rules/skill-tree/NPC AI 行为模型.md",
            ".scratch/",
        ],
    ),
    # 旧激活点模型章节 (在玩家侧文档中)
    (
        r"激活点模型",
        "激活点模型章节 (玩家侧已改聚焦容量)",
        ["⚠️", "已废弃", "#20", "决策树", "NPC AI", "预烘焙"],
        [
            "design/decisions/",
            "design/pipeline/预烘焙管线脚本设计.md",
            "design/rules/skill-tree/NPC AI 行为模型.md",
            ".scratch/",
        ],
    ),
    (
        r"在线手动选择",
        "在线手动选择链路 (D5 全局激活)",
        ["⚠️", "已废弃", "决策树"],
        ["design/decisions/"],
    ),
    (
        r"手动激活.*(链路|脑区)",
        "手动激活链路 (D5 全局激活, NPC情境自动激活除外)",
        ["⚠️", "已废弃", "决策树", "情境自动激活"],
        ["design/decisions/"],
    ),
    # 旧"每回合激活"模型
    (
        r"每回合.*?激活点|激活点.*?每回合",
        "每回合激活点模型 (D4/D7 已废弃)",
        ["⚠️", "已废弃", "#20", "决策树"],
        [
            "design/decisions/",
            "design/pipeline/预烘焙管线脚本设计.md",
            "design/rules/skill-tree/NPC AI 行为模型.md",
            ".scratch/",
        ],
    ),
]

# ── 豁免路径 ──────────────────────────────────────────────

EXEMPT_PREFIX = [
    "design/decisions/",
    ".scratch/",
    "design/archive/trash/",
    ".trash/",
    "reference/deprecated/",
    # grilling 源记录归档——非活跃正典，允许提及已废弃术语（2026-09-12 重构 Phase 2 新建）
    "design/archive/",
    # 仓库重构期的本地安全备份（非项目内容，重构完成后删除）
    ".refactor-backup/",
    # 已标注 ⚠️ 废弃的前置系统 (保留为参考数据源, [项目规约](../../design/conventions/README.md) §六)
    # 2026-09-12 仓库重构：该文件已从 design/archive/trash/ 迁至 design/rules/skill-tree/deprecated/（与 10 个同门文件同处）
    "design/rules/skill-tree/deprecated/链路槽位与激活系统.md",
]

EXEMPT_DIRS = {"trash", "deprecated", "archive", ".trash", ".scratch", ".refactor-backup"}


def is_exempt(rel_path: str) -> bool:
    for p in EXEMPT_PREFIX:
        if rel_path.startswith(p):
            return True
    for d in EXEMPT_DIRS:
        if f"/{d}/" in rel_path:
            return True
    return False


# ── 注册表驱动：逐术语执法策略（#159，2026-09-15） ──────────
#
# `data/term_registry.json` 的 `status` 是术语状态的唯一权威（AGENTS.md §二）。旧检查 2 的
# 正则表是硬编码的 ⇒ 注册表里新标一个 `deprecated`，设计文档侧不会有任何机器反应。
# 本段补上这条链路。**三档执法策略**由注册表的 `enforcement` 字段给出：

TERM_REGISTRY = ROOT / "data" / "term_registry.json"

ENFORCEMENT_SCAN = "扫描"        # 该串除旧模型外无合法用法 ⇒ 出现即判残留（豁免语境除外）
ENFORCEMENT_REGISTER = "只登记"  # 不判：该串在活跃文本里另有合法用法，机器分不出新旧义
ENFORCEMENT_OFF = "关闭"         # 不判（欠账）：本可扫，但活跃文档现存残留未清；现存量每次打印
ENFORCEMENT_TIERS = (ENFORCEMENT_SCAN, ENFORCEMENT_REGISTER, ENFORCEMENT_OFF)
# fail-closed：不写字段或写错值 ⇒ 按 `扫描` 处理（"只标 status 不加门禁"不得靠不写字段成立）
ENFORCEMENT_DEFAULT = ENFORCEMENT_SCAN

# 行内豁免：该行是在**记载作废 / 明文否定 / 说明替代**，不是"把旧模型当现行模型在用"。
# 前五类沿用 check_refs_to_moved_trash 的 DEPRECATION_MARKERS；后几类是明文否定与替代
# ——「不设 AP」这类驳回句必须写得出来，否则门禁会逼人删掉"我们不这么做"的记录。
TERM_MENTION_MARKERS = (
    "⚠️", "已废弃", "已废", "已移出", "迁出", "迁至",
    "已过时", "废止",
    "不设", "不要", "不需要", "无需", "不再", "不引入", "而非", "不是",
    "替代", "取代", "考古",
)

# 引用式豁免：行内代码 / 「」『』 包住的出现 = **提及**，不是使用。
# #159 正文那 4 条 WARN（该 issue 只是在**列举**术语、讨论术语治理）即此形态的复现样本。
REFERENCE_SPAN = re.compile(r"`[^`]*`|「[^」]*」|『[^』]*』")


def mask_references(line: str) -> str:
    """把引用式跨度（行内代码 / 引号）替换为等长占位，使其不参与术语匹配。"""
    return REFERENCE_SPAN.sub(lambda m: "\x00" * len(m.group(0)), line)


def term_regex(term: str):
    """术语匹配：ASCII 词要求词边界（避免 `AP` 命中 `CAPTCHA`），CJK 直接子串。

    语义与 `validate_issues.py` 的同名函数一致。两份实现各自持有是**有意的**：那个模块由
    `test_validate_issues.py` 按路径加载、不 import 兄弟模块，互引会把测试的加载方式弄坏。
    """
    if not term:
        return None
    if re.fullmatch(r"[A-Za-z0-9_()\-.]+", term):
        return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])")
    return re.compile(re.escape(term))


def load_registry_terms(registry_path=None):
    """读 `term_registry.json` 的 deprecated 条目 + enforcement 档位。

    返回 `(terms, hygiene)`:
      terms   = {术语: {"enforcement", "replacement"}}（保持注册表顺序）
      hygiene = {"missing": [未写 enforcement 的术语], "invalid": [(术语, 原值)]}
                —— 两者都按缺省 `扫描` 处理，但必须在输出里露面（不能静默生效）。
    """
    path = Path(registry_path) if registry_path else TERM_REGISTRY
    if not path.exists():
        raise FileNotFoundError(f"{path} 不存在——注册表驱动的废弃术语检查无法判定")

    doc = json.loads(path.read_text(encoding="utf-8"))
    terms, hygiene = {}, {"missing": [], "invalid": []}
    for name, v in (doc.get("terms") or {}).items():
        if not isinstance(v, dict) or v.get("status") != "deprecated":
            continue
        tier = v.get("enforcement")
        if tier is None:
            hygiene["missing"].append(name)
            tier = ENFORCEMENT_DEFAULT
        elif tier not in ENFORCEMENT_TIERS:
            hygiene["invalid"].append((name, str(tier)))
            tier = ENFORCEMENT_DEFAULT
        replacement = (v.get("replaced_by") or v.get("superseded_by")
                       or v.get("deprecation_reason") or v.get("deviation_reason") or "")
        terms[name] = {"enforcement": tier, "replacement": str(replacement)}
    return terms, hygiene


# ── 扫描 ──────────────────────────────────────────────────

def find_md_files():
    files = []
    for md in ROOT.rglob("*.md"):
        rel = str(md.relative_to(ROOT))
        if not is_exempt(rel):
            files.append((rel, md))
    return files


def check_refs_to_moved_trash(md_files):
    """活跃文档不得指向垃圾桶下的任何内容（与桶里当时有什么文件无关）。

    这是 2026-09-13 替换掉 `check_trash_refs` / `check_trash_paths` 的检查：那两道以
    `FILES_IN_TRASH`（7 个硬编码文件名）为判据，垃圾桶移出后它们只会静默通过。
    """
    errors = []
    for rel_path, abs_path in md_files:
        content = abs_path.read_text(encoding="utf-8")
        for i, line in enumerate(content.split("\n"), 1):
            m = TRASH_REF.search(line)
            if not m:
                continue
            if any(mark in line for mark in DEPRECATION_MARKERS):
                continue
            errors.append(
                f"🔴 {rel_path}:{i} — 引用已移出的垃圾桶内容: {m.group(0)[:90]}\n"
                f"   {line.strip()[:130]}"
            )
    return errors


def check_terms(md_files):
    errors = []
    for rel_path, abs_path in md_files:
        content = abs_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for pattern, desc, ok_words, ok_files in DEPRECATED_TERMS:
            if any(rel_path.startswith(f) for f in ok_files):
                continue
            for i, line in enumerate(lines, 1):
                if not re.search(pattern, line):
                    continue
                if any(w in line for w in ok_words):
                    continue
                errors.append(
                    f"🔴 {rel_path}:{i} — {desc}\n"
                    f"   {line.strip()[:130]}"
                )
    return errors


def deprecated_section_lines(lines):
    """返回落在「⚠️ 已废弃」标题下的 0-based 行号集合（整节豁免——项目规约 §六：废弃术语
    只允许出现在决策树历史记录或标注了 ⚠️ 已废弃 的段落里）。复用 md_utils 的两个函数。"""
    skip = set()
    for i, line in enumerate(lines):
        m = re.match(r"^(#+)\s*(.*)$", line)
        if m and is_deprecated_section(m.group(2)):
            skip.update(range(i, find_deprecated_section_end(lines, i, len(m.group(1)))))
    return skip


def scan_registry_terms(md_files, terms):
    """按 `enforcement` 档位扫活跃文档，返回 `(errors, hits)`。

    `hits` = {术语: [(路径, 行号, 行)]} —— **三档都收**：`只登记` / `关闭` 档的现存量不判罚，
    但要打印出来（"只标 status 不加门禁 = 记了一笔没人查的账"，账得在明处）。
    """
    regexes = {t: term_regex(t) for t in terms}
    hits = {t: [] for t in terms}

    for rel_path, abs_path in md_files:
        lines = abs_path.read_text(encoding="utf-8").split("\n")
        skip = deprecated_section_lines(lines)
        for i, line in enumerate(lines):
            if i in skip or any(mark in line for mark in TERM_MENTION_MARKERS):
                continue
            masked = mask_references(line)
            for term, rx in regexes.items():
                if rx is not None and rx.search(masked):
                    hits[term].append((rel_path, i + 1, line.strip()[:130]))

    errors = []
    for term, spec in terms.items():
        if spec["enforcement"] != ENFORCEMENT_SCAN:
            continue
        for rel_path, lineno, text in hits[term]:
            errors.append(
                f"🔴 {rel_path}:{lineno} — 废弃术语残留「{term}」"
                f"（注册表 status: deprecated · enforcement: 扫描）\n"
                f"   替代：{spec['replacement'][:80] or '（注册表未写替代说明）'}\n"
                f"   {text}"
            )
    return errors, hits


def check_links_to_trash(md_files):
    errors = []
    link_re = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    for rel_path, abs_path in md_files:
        content = abs_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for m in link_re.finditer(line):
                target = m.group(2)
                if target.startswith("http") or target.startswith("#"):
                    continue
                t = target.split("#")[0]
                if not t:
                    continue
                try:
                    r = str((abs_path.parent / t).resolve().relative_to(ROOT))
                except ValueError:
                    continue
                for td in ["垃圾桶", ".trash"]:
                    if r.startswith(f"{td}/") or f"/{td}/" in r:
                        errors.append(f"🔴 {rel_path}:{i} — 链接指向垃圾桶: {m.group(0)}")
                        break
    return errors


def print_registry_summary(terms, hits, hygiene, n_files):
    """打印注册表驱动的判定账目——三档各多少条、各命中多少处。

    `只登记` / `关闭` 档**不判罚**，但必须每次都露面：关闭档的现存量就是欠账清单
    （"只标 `status` 不加门禁 = 记了一笔没人查的账" ⇒ 账得在明处），清理完把那条
    `enforcement` 改回 `扫描` 即可。
    """
    by_tier = {t: [n for n, spec in terms.items() if spec["enforcement"] == t]
               for t in ENFORCEMENT_TIERS}
    n_hits = {t: sum(len(hits[n]) for n in names) for t, names in by_tier.items()}

    print(f"ℹ️ 注册表驱动：判定面 design/ + reference/ 活跃文档 {n_files} 个（md_utils.SCAN_ROOTS）；"
          f"deprecated 条目 {len(terms)} 条 = "
          + " · ".join(f"{t} {len(by_tier[t])} 条/命中 {n_hits[t]} 处" for t in ENFORCEMENT_TIERS))

    if by_tier[ENFORCEMENT_OFF]:
        pending = sorted(((n, len(hits[n])) for n in by_tier[ENFORCEMENT_OFF]), key=lambda p: -p[1])
        detail = " · ".join(f"{n} {c} 处" for n, c in pending if c) or "（0 处）"
        print(f"ℹ️ 关闭档现存量（欠账，不判罚；清理后改回 `{ENFORCEMENT_SCAN}`）：{detail}")
    if by_tier[ENFORCEMENT_REGISTER]:
        print(f"ℹ️ 只登记档命中 {n_hits[ENFORCEMENT_REGISTER]} 处"
              f"（该串在活跃文本里另有合法用法 ⇒ 不判罚）")
    if hygiene["missing"]:
        print(f"⚠️ {len(hygiene['missing'])} 条 deprecated 未写 `enforcement` ⇒ 按缺省 "
              f"`{ENFORCEMENT_DEFAULT}` 处理: " + " ".join(hygiene["missing"]))
    if hygiene["invalid"]:
        print(f"⚠️ `enforcement` 取值不在三档内 ⇒ 按缺省 `{ENFORCEMENT_DEFAULT}` 处理: "
              + " ".join(f"{n}=`{v}`" for n, v in hygiene["invalid"]))
    print()


# ── main ──────────────────────────────────────────────────

def main():
    md_files = find_md_files()
    print(f"校验 {len(md_files)} 个活跃 .md 文件...\n")

    all_errors = []
    for name, fn in [
        ("引用已移出的垃圾桶内容", check_refs_to_moved_trash),
        ("废弃术语残留（硬编码表）", check_terms),
        ("链接指向垃圾桶", check_links_to_trash),
    ]:
        errs = fn(md_files)
        if errs:
            print(f"## {name} ({len(errs)} 处)")
            for e in errs:
                print(e)
            print()
        all_errors.extend(errs)

    # ── 检查 4：注册表驱动（判定面 = design/ + reference/ 活跃文档） ──
    registry_terms, hygiene = load_registry_terms()
    reg_md = [(str(p.relative_to(ROOT)), p) for p in collect_md_files()]
    reg_errors, hits = scan_registry_terms(reg_md, registry_terms)
    if reg_errors:
        print(f"## 废弃术语残留（注册表驱动）({len(reg_errors)} 处)")
        for e in reg_errors:
            print(e)
        print()
    all_errors.extend(reg_errors)
    print_registry_summary(registry_terms, hits, hygiene, len(reg_md))

    if all_errors:
        n = len(all_errors)
        print(f"{'='*60}\n❌ {n} 处问题\n{'='*60}")
        sys.exit(1)
    else:
        print("✅ 全部通过")
        sys.exit(0)


if __name__ == "__main__":
    main()
