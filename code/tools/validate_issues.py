#!/usr/bin/env python3
"""validate_issues.py — issue 契约校验（issue-process.md §5.2 规则 I1–I12）

契约正文（唯一真相源）: `design/engineering/issue-process.md`
  · §4.1 所有类型必填字段（动机/类型/能力增量/依赖/门禁/预期差分/验收标准/明确排除/回滚）
  · §4.2 按类型追加必填（Bug / Experiment / RFC / Slice / Task·Implementation）
  · §4.3 引用格式：契约面允许段引用，定位面禁止行号
  · §5.2 规则表 I1–I12
  · §7.3 本机 gh 2.4.0 限制（无 --blocked-by / --parent）→ 依赖写在正文 `依赖:` 字段
  · §7.4 存量豁免（无 type:* 标签 且 创建日期早于 2026-09-12 的 issue 不追溯）
上游枚举: `WORKFLOW.md` §一（类型用途）/ §二（四轴合法状态）
门禁表:   `design/engineering/gates.json`（I6 的判定依据）

检查项（规则表 RULES = id · 一句话 · 判定函数，单一来源，逐条对应 §5.2）:
  I1  必填章节齐全（§4.1 九个 + §4.2 按类型追加）且内容非空
  I2  `### 类型` ∈ 六种枚举；`--label type:*` 与正文类型一致
  I3  能力增量的轴 ∈ 四轴枚举，且「从 / 到」∈ 该轴合法状态
  I4  `Design` 未 `ACCEPTED` 的能力不得声明 `Implementation` 迁移（读 design/slices/*/slice.md）
  I5  `blocked-by`/`consumed-by`/`requires` 引用的 issue 编号在快照内存在
  I6  门禁行 ∈ gates.json 的 gate id，或引用的仓库脚本真实存在；
      引用 `available: false` 的门禁且标 `state:ready-for-agent` → FAIL，未标 → warning
  I7  `blocked-by` 未全部关闭时，本 issue 不得处于 `state:in-progress`
  I8  正文（反引号内 / 链接目标）的仓库相对路径必须存在（FAIL）；
      段引用 `§N` 文件必须在（FAIL），段号找不到只出 warning
  I9  正文不得出现 `文件.ext:行号` 或「第 N 行」式定位（warning）
  I10 正文不得引用 `design/archive/trash/`（FAIL）；不得使用 term_registry.json 中
      `status: deprecated` 且有替代说明的术语（warning）
  I11 全仓同时 `state:in-progress` 的 issue ≤ 1（仅 --from-github）
  I12 验收标准 2–8 条；能力增量 ≤ 3 行数据；门禁 ≥ 1 条

两种模式:
  python3 code/tools/validate_issues.py --file <草稿.md> [--label type:task --label state:needs-triage]
      —— 创建前门禁（§7.1 通道 B）。`--file -` 从 stdin 读，便于
         `... --file - | gh issue create --body-file -` 式管道。
  python3 code/tools/validate_issues.py --from-github [--repo OWNER/REPO] [--limit N]
      —— CI 快照（§7.1 通道 C），校验真相源本身。本机 gh 为 2.4.0，
         只用 `gh issue list --json` 的既有字段（无原生依赖边字段，见 §7.3）。

本脚本**零副作用**：不写任何状态文件、不调用会写盘的编排器（对比
`run_all_checks.py` 会写 `.checks-state.json`——那是它的已知副作用）。

「未运行不是通过」（WORKFLOW §5.1）:
  · `--file` 模式下 I5/I7/I11 无快照可判 → **显式打印「已跳过（需 --from-github）」**，
    在汇总里单列 skipped 计数，**不计入通过**。
  · 快照内没有非存量 issue 时全部规则同样标 skipped，绝不静默全绿。
  · 拉不到输入（gh 未安装/未认证/网络失败/gates.json 缺失）→ 退出码 2，绝不退 0。

用法:
  python3 code/tools/validate_issues.py --file <草稿.md>
  python3 code/tools/validate_issues.py --file - --label type:task
  python3 code/tools/validate_issues.py --from-github
  python3 code/tools/validate_issues.py --from-github --repo verystrongdog/game --limit 200

退出码: 0 = 全部通过（允许有 warning）；1 = 有 FAIL；2 = 用法错误或输入不可得
"""

import argparse
import json
import re
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

GATES_JSON = ROOT / "design/engineering/gates.json"
TERM_REGISTRY = ROOT / "data/term_registry.json"
SLICES_DIR = ROOT / "design/slices"
DEFAULT_REPO = "verystrongdog/game"

# §7.4 存量豁免的分界（无 type:* 标签 且 创建日期早于本日）
LEGACY_CUTOFF = "2026-09-12"

# §7.3：本机 gh 2.4.0 的 `gh issue list --json` 可用字段（实测：
# assignees author body closed closedAt comments createdAt id labels milestone
# number projectCards reactionGroups state title updatedAt url）——没有原生依赖边字段。
GH_JSON_FIELDS = "number,title,body,labels,createdAt,state,url,blockedBy"

# ── WORKFLOW.md §三 类型枚举 ───────────────────────────────
ISSUE_TYPES = ["Task", "Implementation", "Bug", "Experiment", "RFC", "Slice"]

# ── WORKFLOW.md §二.1 能力四轴与合法状态 ────────────────────
AXIS_STATES = {
    "Design": ["UNRESOLVED", "CANDIDATE", "ACCEPTED", "SUPERSEDED"],
    "Implementation": ["NONE", "FAKE", "PARTIAL", "DONE_FOR_SLICE"],
    "Integration": ["ISOLATED", "CONNECTED", "E2E"],
    "Health": ["UNKNOWN", "PASS", "REGRESSED"],
}

# ── issue-process.md §4.1 所有类型必填 ─────────────────────
BASE_FIELDS = ["动机", "类型", "能力增量", "依赖", "门禁", "预期差分",
               "验收标准", "明确排除", "回滚"]

# ── issue-process.md §4.2 按类型追加必填 ───────────────────
TYPE_FIELDS = {
    "Task": ["交付物", "接入位置"],
    "Implementation": ["交付物", "接入位置"],
    "Bug": ["复现", "期望 vs 实际"],
    "Experiment": ["假设", "判定标准", "原型去向"],
    "RFC": ["选项", "owner 决策"],          # 「回滚」已在 §4.1，不重复要求
    "Slice": ["玩家路径", "must-prove"],
}

# 章节标题的等价写法（GitHub Issue Forms 的 label 渲染有空格/大小写差异；
# 其余章节一律要求 `### 标题` 精确匹配）。键为 §4.1/§4.2 的字段名。
FIELD_ALIASES = {
    "回滚": ["回滚", "回滚方案"],
    "期望 vs 实际": ["期望 vs 实际", "期望vs实际", "期望与实际", "期望/实际", "期望和实际"],
    "owner 决策": ["owner 决策", "owner决策", "决策"],
    "must-prove": ["must-prove", "mustprove", "must prove"],
    "复现": ["复现", "复现步骤"],
    "判定标准": ["判定标准", "判定判据"],
}

# ── §4.1 依赖章节的三个 key ────────────────────────────────
DEP_KEYS = ["blocked-by", "consumed-by", "requires"]

# ── issue-process.md §4.1.1 三个受控取值域 ──────────────────

def check_requires_domain(value: str, gates: dict):
    """校验 `requires:` 的取值域（§4.1.1）。返回问题描述列表。"""
    problems = []
    if value in ("无", ""):
        return problems
    for tok in re.split(r"[、,，;；]+", value):
        tok = tok.strip()
        if not tok:
            continue
        if tok.startswith("gate:"):
            gid = tok[len("gate:"):].strip()
            if gid not in gates:
                problems.append(f"requires: gate:{gid} 不在 gates.json 中")
        elif tok.startswith("PLAYABLE:"):
            rest = tok[len("PLAYABLE:"):].strip()
            if rest != "NO_AUTHORIZED_PLAYABLE" and not rest.startswith("AUTHORIZED_PLAYABLE:"):
                problems.append(f"requires: PLAYABLE:{rest} 不是合法状态"
                                f"（应为 NO_AUTHORIZED_PLAYABLE 或 AUTHORIZED_PLAYABLE: <slice-id>）")
        elif tok.startswith("能力:"):
            m = re.match(r"^能力:(.+?)\s*=\s*(\w+)\s*:\s*(\w+)$", tok)
            if not m:
                problems.append(f"requires: {tok} 不符合 `能力:<能力名>=<轴>:<状态>`")
            else:
                _, axis, state = m.groups()
                if axis not in AXIS_STATES:
                    problems.append(f"requires: {tok} 的轴 {axis} ∉ 四轴")
                elif state not in AXIS_STATES[axis]:
                    problems.append(f"requires: {tok} 的状态 {state} ∉ {axis} 的合法值")
        elif tok.startswith("owner:"):
            if not tok[len("owner:"):].strip():
                problems.append("requires: owner: 后必须写明决策项")
        else:
            problems.append(f"requires: {tok} 不在受控取值域"
                            f"（gate: / PLAYABLE: / 能力: / owner: / 无）")
    return problems


def check_consumed_domain(value: str, gates: dict):
    """校验 `consumed-by:` 的取值域（§4.1.1）。返回 (问题列表, 警告列表)。"""
    problems, warns = [], []
    if value in ("无", ""):
        return problems, warns
    # `待建:<描述>` 与 `终态`（须写明为何）**按定义携带自由文本**，其中的
    # 顿号/逗号属于描述本身，不能当分隔符——否则 `终态（…，由…消费）` 会被
    # 切成两半，把合法写法误报成非法。实测：第一版实现就误报了 #133 与 #135。
    if value.startswith("待建:") or value.startswith("终态"):
        rest = value[len("待建:"):].strip() if value.startswith("待建:") else ""
        if value.startswith("待建:") and not rest:
            problems.append("consumed-by: 待建: 后必须写明下游是什么")
        elif value.startswith("待建:"):
            warns.append(f"consumed-by: {value}（下游尚未创建——A3 的弱化形态，triage 时确认）")
        return problems, warns
    for tok in re.split(r"[、,，;；]+", value):
        tok = tok.strip()
        if not tok or re.match(r"^#\d+$", tok):
            continue                    # 编号存在性由 I5 主体判定
        if tok.startswith("证据:"):
            path = clean_path_token(tok[len("证据:"):].strip())
            if not (ROOT / path).exists():
                problems.append(f"consumed-by: 证据:{path} 指向的证据文件不存在")
        elif tok.startswith("门禁:"):
            gid = tok[len("门禁:"):].strip()
            if gid not in gates:
                problems.append(f"consumed-by: 门禁:{gid} 不在 gates.json 中")
        elif tok.startswith("待建:"):
            if not tok[len("待建:"):].strip():
                problems.append("consumed-by: 待建: 后必须写明下游是什么")
            else:
                warns.append(f"consumed-by: {tok}（下游尚未创建——A3 的弱化形态，triage 时确认）")
        elif tok == "终态":
            continue
        elif (ROOT / "design" / "slices" / tok).is_dir():
            continue                    # 切片 id
        else:
            problems.append(f"consumed-by: {tok} 不在受控取值域"
                            f"（#NN / <切片 id> / 证据:<路径> / 门禁:<gate id> / 待建:<描述> / 终态）")
    return problems, warns


# 四轴表中「无设计面」的写法（I4 按不适用处理，不判轴序边违反）
NOT_APPLICABLE = {"—", "-", "–", "n/a", "N/A", "无", "不适用"}

# `门禁: none` 只对这两类合法（它们的判据是决策/结论，不是机器门禁）——
# issue-process.md §4.1 字段表 + §4.1.1 例外 2。
GATE_NONE_TYPES = {"RFC", "Experiment"}

# I8 豁免的章节：这两节按定义描述**尚未存在**的产物（交付物 / 预期差分），
# 引用未来路径是它们的工作，不是死引用。其余章节里的路径必须已存在。
I8_EXEMPT_FIELDS = ("交付物", "预期差分")

# I8 的降级标记：路径不存在但**同一行**显式标注了它尚不存在 → 警告而非失败
# （issue-process.md §4.1.1 例外 4：命名缺失物是 issue 的主题，不是隐藏依赖）。
MISSING_MARKERS = ("缺失", "不存在", "尚未", "未提交", "待建", "待补", "将新增", "新增",
                   "新建", "为零", "0 个", "未创建", "尚无")

# 状态标签：正规写法是 `state:*`（issue-process.md §5.2）。WORKFLOW.md §一 曾写
# `status:in-progress`，已于 2026-09-12 统一为 `state:in-progress`；两种前缀都认，
# 以免历史 issue 或手写标签被误判。
STATE_PREFIXES = ("state:", "status:")
IN_PROGRESS_LABELS = {"state:in-progress", "status:in-progress"}
READY_LABELS = {"state:ready-for-agent", "status:ready-for-agent", "ready-for-agent"}

# ── 仓库相对路径的顶层前缀（I8 只认这些，避免把 URL/绝对路径当仓库路径） ──
REPO_PATH_PREFIXES = ("design/", "code/", "data/", "reference/", ".github/", ".agents/")
TRASH_PATH = "design/archive/trash"

CN_NUM = {"一": "1", "二": "2", "三": "3", "四": "4", "五": "5", "六": "6",
          "七": "7", "八": "8", "九": "9", "十": "10", "十一": "11", "十二": "12",
          "十三": "13", "十四": "14"}

PASS, FAIL, WARN, SKIP = "pass", "fail", "warn", "skip"
ICON = {PASS: "✅", FAIL: "❌", WARN: "⚠️", SKIP: "⏭️"}

Finding = namedtuple("Finding", ["status", "message"])
Rule = namedtuple("Rule", ["id", "desc", "fn"])
Section = namedtuple("Section", ["heading", "content", "line"])


# ══════════════════════════════════════════════════════════════
# 文本工具
# ══════════════════════════════════════════════════════════════

def deformat(s: str) -> str:
    """去掉 markdown 装饰（反引号/粗体/斜体）与首尾空白。"""
    s = s.replace("**", "").replace("`", "")
    s = s.strip().strip("*").strip()
    return re.sub(r"\s+", " ", s).strip()


def norm_heading(s: str) -> str:
    """章节标题归一化：去装饰、折叠空白、去尾部冒号、ASCII 小写。"""
    s = deformat(s)
    s = s.strip().rstrip("：:")
    return re.sub(r"\s+", " ", s).strip().lower()


def is_empty_content(content: str) -> bool:
    """章节内容是否为空。GitHub Issue Forms 的「未填」会渲染成 `_No response_`。"""
    body = re.sub(r"<!--.*?-->", "", content, flags=re.S)
    body = body.strip()
    if body in ("_No response_", "_No response_", "No response", "_No response_."):
        return True
    return body == ""


def strip_code_fences(body: str):
    """返回 [(行号, 行文本, 是否在 ``` 代码块内)]。"""
    out, in_fence = [], False
    for i, line in enumerate(body.split("\n"), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append((i, line, True))
            continue
        out.append((i, line, in_fence))
    return out


# ══════════════════════════════════════════════════════════════
# 章节解析（`### 标题` 精确匹配 + FIELD_ALIASES 的少量等价写法）
# ══════════════════════════════════════════════════════════════

def canonical_field(heading: str):
    """把归一化后的标题映射回 §4.1/§4.2 的字段名；不认识返回 None。"""
    n = norm_heading(heading)
    for field, aliases in FIELD_ALIASES.items():
        if n in {norm_heading(a) for a in aliases}:
            return field
    for field in list(BASE_FIELDS) + [f for fs in TYPE_FIELDS.values() for f in fs]:
        if n == norm_heading(field):
            return field
    return None


def parse_sections(body: str) -> dict:
    """按 `### 标题` 切分。只认三级标题（§4.3：表单渲染出的锚点即 `### 标题`）。"""
    lines = body.split("\n")
    heads = []
    for i, line in enumerate(lines):
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            heads.append((i, m.group(1)))
    out = {}
    for idx, (i, raw) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
        content = "\n".join(lines[i + 1:end])
        field = canonical_field(raw)
        if field and field not in out:
            out[field] = Section(raw, content, i + 1)
    return out


def md_tables(content: str):
    """把 markdown 正文切成若干张表；每张表是行列表，分隔行（|---|）记为 None。

    一个文件里常有多张表（如 slice.md 的 must-prove 表与四轴表），必须按表分段，
    否则第一张表的表头会被当成整个文件的表头（2026-09-12 实测踩过）。
    """
    tables, cur = [], []
    for line in content.split("\n"):
        s = line.strip()
        if s.startswith("|") and s.endswith("|") and s.count("|") >= 2:
            cells = [c.strip() for c in s.strip("|").split("|")]
            cur.append(None if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c != "")
                       else cells)
        elif cur:
            tables.append(cur)
            cur = []
    if cur:
        tables.append(cur)
    return tables


def split_table(table):
    """→ (表头单元 | None, 数据行列表)。markdown 表头后必跟分隔行。"""
    idx = next((i for i, r in enumerate(table) if r is None), None)
    if idx is None:
        return None, [r for r in table if r]
    return table[0], [r for r in table[idx + 1:] if r]


def find_table(content: str, header_pred):
    """取第一张表头满足 header_pred 的表；都不满足则回退到第一张表。"""
    tables = md_tables(content)
    for t in tables:
        header, _ = split_table(t)
        if header and header_pred(header):
            return t
    return tables[0] if tables else []


def list_items(content: str):
    """章节内的列表项（`- [ ]` / `- ` / `* ` / `1. `）——I12 计数用。

    §5.2 I12 明写「`- [ ]` 或 `- ` 列表项」；这里同时接受 `*`/`+` 与有序列表，
    因为 Issue Forms 的 checklist 与草稿手写两种写法都合法（容差，不改变判据）。
    """
    items = []
    for i, line in enumerate(content.split("\n"), 1):
        s = line.strip()
        if re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)", s) and deformat(re.sub(r"^[\s\-*+\d.)]+", "", s)):
            items.append((i, s))
    return items


def nonblank_lines(content: str):
    out = []
    for i, line in enumerate(content.split("\n"), 1):
        s = line.strip()
        if not s or s.startswith("<!--"):
            continue
        out.append((i, s))
    return out


# ══════════════════════════════════════════════════════════════
# 段引用存在性（复用 validate_cross_refs.py §check_section_exists 的思路：
# 扫标题、中文数字与阿拉伯数字互认、段号需有分隔符边界）
# ══════════════════════════════════════════════════════════════

def section_exists(path: Path, anchor: str) -> bool:
    """目标文件中是否存在 `§anchor` 段。接受 `## 4` / `## 4.1` / `## 四、` 三种形式。"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    anchor = anchor.strip().lstrip("§").strip()
    if not anchor:
        return False
    variants = {anchor}
    if anchor in CN_NUM:
        variants.add(CN_NUM[anchor])
    for cn, num in CN_NUM.items():
        if num == anchor:
            variants.add(cn)
    for line in text.split("\n"):
        m = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if not m:
            continue
        heading = deformat(m.group(1))
        # 标题开头的段号：`4 门禁` / `4.1 所有类型必填` / `四、阶段的两次闭合`
        sm = re.match(r"^([0-9]+(?:\.[0-9]+)*|[一二三四五六七八九十]+)\s*(?:[、.．,:：]|\s|$)", heading)
        if not sm:
            continue
        if sm.group(1) in variants:
            return True
    return False


# ══════════════════════════════════════════════════════════════
# 契约数据加载
# ══════════════════════════════════════════════════════════════

def load_gates():
    """读 gates.json。缺失 → 输入不可得（退出码 2）。"""
    if not GATES_JSON.exists():
        raise InputUnavailable(f"{GATES_JSON.relative_to(ROOT)} 不存在——I6 无法判定")
    doc = json.loads(GATES_JSON.read_text(encoding="utf-8"))
    gates = {}
    for g in doc.get("gates", []):
        if g.get("id"):
            gates[g["id"]] = g
    return gates


def load_deprecated_terms():
    """term_registry.json 中 status=deprecated 且有替代说明的术语。"""
    if not TERM_REGISTRY.exists():
        raise InputUnavailable(f"{TERM_REGISTRY.relative_to(ROOT)} 不存在——I10 无法判定")
    doc = json.loads(TERM_REGISTRY.read_text(encoding="utf-8"))
    terms = []
    for name, v in (doc.get("terms") or {}).items():
        if not isinstance(v, dict) or v.get("status") != "deprecated":
            continue
        replacement = (v.get("replaced_by") or v.get("superseded_by")
                       or v.get("deprecation_reason") or v.get("deviation_reason"))
        if not replacement:
            continue        # §I10：只查有 replacement/替代说明的条目
        terms.append((name, str(replacement)))
    return terms


def load_slice_design_states():
    """读 design/slices/*/slice.md 的四轴表 → {能力名: Design 状态原文}。

    表列名就是 `Design`/`Implementation`/`Integration`/`Health`（§4.1 消费时刻：
    关闭时据此更新 slice.md 的四轴表）。
    """
    states = {}
    if not SLICES_DIR.exists():
        return states
    for f in sorted(SLICES_DIR.glob("*/slice.md")):
        for table in md_tables(f.read_text(encoding="utf-8")):
            header, data = split_table(table)
            if not header or not data:
                continue
            cap_i, design_i = 0, None
            for i, h in enumerate(header):
                hn = deformat(h)
                if "能力" in hn:
                    cap_i = i
                if hn.lower() == "design":
                    design_i = i
            if design_i is None:
                continue        # 不是四轴表（如 must-prove 表）
            for r in data:
                if len(r) <= max(cap_i, design_i):
                    continue
                cap = capability_key(r[cap_i])
                if not cap:
                    continue
                states.setdefault(cap, deformat(r[design_i]).upper())
    return states


def capability_key(name: str) -> str:
    """能力名归一化：去装饰、去空白、（…）附注。`Core → Unity 适配层` 与
    `Core->Unity 适配层` 视为同一能力。"""
    s = deformat(name)
    s = re.sub(r"[（(][^）)]*[）)]", "", s).strip()
    s = s.replace("->", "→").replace("—>", "→").replace("–>", "→")
    return re.sub(r"\s+", "", s).lower()


# ══════════════════════════════════════════════════════════════
# 能力增量表解析（I3 / I4 / I12 共用）
# ══════════════════════════════════════════════════════════════

Increment = namedtuple("Increment", ["ability", "axis", "frm", "to", "raw"])


def parse_increments(content: str):
    """解析 `### 能力增量` 的表格：能力 · 轴 · 从 → 到。

    表头可写 `| 能力 | 轴 | 从 → 到 |`，也可拆成 `| 从 | 到 |` 两列；
    表头无法识别时按位置回退（0=能力 1=轴 2=从→到）。
    """
    rows = md_tables(content)
    if not rows:
        return []
    header, data = split_table(find_table(
        content, lambda h: any(("能力" in deformat(c)) or ("轴" in deformat(c)) for c in h)))
    has_header = header is not None

    cap_i, axis_i, from_i, to_i, pair_i = 0, 1, None, None, 2
    if has_header:
        for i, h in enumerate(header):
            hn = deformat(h)
            if "能力" in hn:
                cap_i = i
            elif "轴" in hn:
                axis_i = i
            elif "从" in hn and "到" in hn:
                pair_i = i
            elif hn.startswith("从"):
                from_i = i
            elif hn.startswith("到"):
                to_i = i
        if from_i is not None and to_i is not None:
            pair_i = None

    out = []
    for r in data:
        n = len(r)

        def cell(idx):
            return deformat(r[idx]) if idx is not None and idx < n else ""

        ability, axis = cell(cap_i), cell(axis_i) if axis_i < n else ""
        if from_i is not None and to_i is not None:
            frm, to = cell(from_i), cell(to_i)
        else:
            raw_pair = cell(pair_i) if pair_i is not None and pair_i < n else ""
            parts = re.split(r"→|->|—>|–>", raw_pair, maxsplit=1)
            frm = deformat(parts[0]) if parts else ""
            to = deformat(parts[1]) if len(parts) > 1 else ""
        out.append(Increment(ability, axis, state_token(frm), state_token(to), r))
    return out


def state_token(s: str) -> str:
    """状态单元归一化：去装饰、去（…）附注、大写。保留原样供报错展示。"""
    s = deformat(s)
    s = re.sub(r"[（(][^）)]*[）)]", "", s).strip()
    return s.upper()


def axis_lookup(axis_raw: str):
    """轴名归一化匹配（Design/Implementation/Integration/Health，ASCII 不区分大小写）。"""
    a = deformat(axis_raw).strip().lower()
    for known in AXIS_STATES:
        if a == known.lower():
            return known
    return None


# ══════════════════════════════════════════════════════════════
# 主体（issue 或草稿）
# ══════════════════════════════════════════════════════════════

class Subject:
    def __init__(self, body, number=None, title="", labels=None, created_at="", state=""):
        self.body = body or ""
        self.number = number
        self.title = title
        self.labels = [l.lower() for l in (labels or [])]
        self.created_at = created_at or ""
        self.state = state
        self.sections = parse_sections(self.body)

    @property
    def tag(self) -> str:
        return f"#{self.number}" if self.number else "草稿"

    def section(self, field):
        return self.sections.get(field)

    def content(self, field) -> str:
        s = self.sections.get(field)
        return s.content if s else ""

    @property
    def issue_type_raw(self) -> str:
        sec = self.sections.get("类型")
        if not sec:
            return ""
        for _, line in nonblank_lines(sec.content):
            return deformat(line).strip()
        return ""

    @property
    def issue_type(self):
        raw = self.issue_type_raw
        for t in ISSUE_TYPES:
            if raw.lower() == t.lower():
                return t
        return None

    def has_label(self, names) -> bool:
        return any(l in names for l in self.labels)

    @property
    def in_progress(self) -> bool:
        return self.has_label(IN_PROGRESS_LABELS)

    @property
    def ready_for_agent(self) -> bool:
        return self.has_label(READY_LABELS)


class InputUnavailable(Exception):
    """输入不可得（退出码 2）。"""


def parse_dependencies(subject: Subject) -> dict:
    """解析 `### 依赖` 的 `key: value`。返回 {key: (值原文, [issue 编号])}。"""
    deps = {}
    for _, line in nonblank_lines(subject.content("依赖")):
        s = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", line).strip()
        m = re.match(r"^`?\s*([A-Za-z][A-Za-z-]*)\s*`?\s*[:：]\s*(.*)$", s)
        if not m:
            continue
        key = m.group(1).strip().lower()
        if key not in DEP_KEYS:
            continue
        value = deformat(m.group(2)).strip()
        deps[key] = (value, [int(n) for n in re.findall(r"#(\d+)", value)])
    return deps


# ══════════════════════════════════════════════════════════════
# 规则实现（I1–I12）
# ══════════════════════════════════════════════════════════════

def rule_i1(subjects, ctx):
    """I1 必填章节齐全（§4.1 九个 + §4.2 按类型追加）且内容非空。"""
    out = []
    for s in subjects:
        missing = [f for f in BASE_FIELDS if f not in s.sections]
        empty = [f for f in BASE_FIELDS if f in s.sections and is_empty_content(s.content(f))]
        if missing:
            out.append(Finding(FAIL, f"{s.tag} 缺必填章节: " + " / ".join(f"### {f}" for f in missing)))
        if empty:
            out.append(Finding(FAIL, f"{s.tag} 必填章节内容为空: " + " / ".join(f"### {f}" for f in empty)))
        t = s.issue_type
        if t is None:
            extra = [f for fs in TYPE_FIELDS.values() for f in fs]
            out.append(Finding(WARN, f"{s.tag} 类型缺失或非法（{s.issue_type_raw or '空'}），"
                                     f"§4.2 追加章节（{'/'.join(sorted(set(extra)))}）无法判定"))
            continue
        appended = TYPE_FIELDS.get(t, [])
        miss = [f for f in appended if f not in s.sections]
        emp = [f for f in appended if f in s.sections and is_empty_content(s.content(f))]
        if miss:
            out.append(Finding(FAIL, f"{s.tag} 类型 {t} 缺 §4.2 追加章节: "
                                     + " / ".join(f"### {f}" for f in miss)))
        if emp:
            out.append(Finding(FAIL, f"{s.tag} 类型 {t} 的追加章节内容为空: "
                                     + " / ".join(f"### {f}" for f in emp)))
    return out


def rule_i2(subjects, ctx):
    """I2 `### 类型` ∈ 六种枚举；标签与正文类型一致。"""
    out = []
    for s in subjects:
        raw = s.issue_type_raw
        if not raw:
            out.append(Finding(FAIL, f"{s.tag} `### 类型` 为空"))
        elif s.issue_type is None:
            out.append(Finding(FAIL, f"{s.tag} 类型 {raw!r} ∉ {{{', '.join(ISSUE_TYPES)}}}"))
        elif raw != s.issue_type:
            out.append(Finding(WARN, f"{s.tag} 类型 {raw!r} 大小写与枚举不一致，应为 {s.issue_type}"))
        if ctx.labels_provided:
            label_sets = [ctx.labels]
        elif s.number is not None:
            label_sets = [s.labels]      # 快照模式：用 issue 自己的标签
        else:
            label_sets = []
        for labels in label_sets:
            type_labels = [l for l in labels if l.lower().startswith("type:")]
            if not type_labels:
                out.append(Finding(WARN, f"{s.tag} 没有 type:* 标签，无法校验「标签 vs 正文类型」"
                                         f"一致性（§7.4 也以 type:* 区分存量）"))
                continue
            for l in type_labels:
                val = l.split(":", 1)[1]
                if s.issue_type and val.lower() != s.issue_type.lower():
                    out.append(Finding(FAIL, f"{s.tag} 标签 {l} 与正文类型 {s.issue_type} 不一致"))
                elif not s.issue_type:
                    out.append(Finding(WARN, f"{s.tag} 标签 {l} 无法与正文类型比对（类型非法）"))
    return out


def rule_i3(subjects, ctx):
    """I3 轴 ∈ 四轴枚举；「从 / 到」∈ 该轴合法状态。"""
    out = []
    for s in subjects:
        sec = s.sections.get("能力增量")
        if not sec:
            continue
        incs = parse_increments(sec.content)
        if not incs:
            out.append(Finding(FAIL, f"{s.tag} `### 能力增量` 未找到表格（能力 · 轴 · 从 → 到）"))
            continue
        for inc in incs:
            if not inc.ability:
                out.append(Finding(FAIL, f"{s.tag} 能力增量行缺「能力」单元格: {inc.raw}"))
            axis = axis_lookup(inc.axis)
            if axis is None:
                out.append(Finding(FAIL, f"{s.tag} 能力「{inc.ability or '?'}」轴 {inc.axis!r} "
                                         f"∉ {{{', '.join(AXIS_STATES)}}}"))
                continue
            legal = AXIS_STATES[axis]
            for label, val in (("从", inc.frm), ("到", inc.to)):
                if not val:
                    out.append(Finding(FAIL, f"{s.tag} 能力「{inc.ability}」轴 {axis} 缺「{label}」值"))
                elif val not in legal:
                    out.append(Finding(FAIL, f"{s.tag} 能力「{inc.ability}」轴 {axis} "
                                             f"「{label}」={val} ∉ {{{', '.join(legal)}}}"))
    return out


def rule_i4(subjects, ctx):
    """I4 `Design` 未 `ACCEPTED` 的能力不得声明 `Implementation` 迁移。"""
    out = []
    states = load_slice_design_states()
    if not states:
        return [Finding(WARN, "design/slices/*/slice.md 无四轴表可查——I4 无法判定")]
    for s in subjects:
        sec = s.sections.get("能力增量")
        if not sec:
            continue
        for inc in parse_increments(sec.content):
            if axis_lookup(inc.axis) != "Implementation":
                continue
            if not inc.frm or not inc.to or inc.frm == inc.to:
                continue        # 不是迁移（I3 已负责取值合法性）
            key = capability_key(inc.ability)
            if key not in states:
                out.append(Finding(WARN, f"{s.tag} 能力「{inc.ability}」未在切片四轴表中登记"
                                         f"（design/slices/*/slice.md）——I4 无法判定"))
                continue
            design = states[key]
            # `—` 表示该能力**没有设计面**（工程侧能力，如「Unity 资产身份」在
            # slice.md 的四轴表里 Design 列就是 `—`）。轴序边只约束"有设计面但
            # 尚未 ACCEPTED"的能力，故不适用不算违反（issue-process.md §4.1.1）。
            if design in NOT_APPLICABLE:
                out.append(Finding(WARN, f"{s.tag} 能力「{inc.ability}」在切片表中 Design="
                                         f"{design}（无设计面）——按不适用处理，不判轴序边违反"))
                continue
            if design != "ACCEPTED":
                out.append(Finding(FAIL, f"{s.tag} 能力「{inc.ability}」声明 Implementation "
                                         f"{inc.frm}→{inc.to}，但切片表 Design={design or '（空）'}"
                                         f"（未到 ACCEPTED，轴序边不成立）"))
    return out


def rule_i5(subjects, ctx):
    """I5 依赖三 key：取值域合法（§4.1.1，两种模式都判）+ 引用的编号存在（需快照）。"""
    known = ctx.snapshot["numbers"] if ctx.snapshot else None
    out = []
    if known is None:
        out.append(Finding(SKIP, "依赖**引用存在性**需要 issue 快照 —— 已跳过（需 --from-github）；"
                                 "本节其余判据（取值域合法）已执行"))
    for s in subjects:
        if not s.sections.get("依赖"):
            continue
        deps = parse_dependencies(s)
        for key in DEP_KEYS:
            if key not in deps:
                out.append(Finding(FAIL, f"{s.tag} `### 依赖` 缺 key `{key}:`（§4.1 要求三个 key 逐行）"))
        for key, (value, nums) in deps.items():
            if key == "requires":
                for msg in check_requires_domain(value, ctx.gates):
                    out.append(Finding(FAIL, f"{s.tag} {msg}"))
            elif key == "consumed-by":
                problems, warns = check_consumed_domain(value, ctx.gates)
                out += [Finding(FAIL, f"{s.tag} {m}") for m in problems]
                out += [Finding(WARN, f"{s.tag} {m}") for m in warns]
            if known is None:
                continue
            for n in nums:
                if n not in known:
                    out.append(Finding(FAIL, f"{s.tag} {key}: {value} 引用了快照中不存在的 #{n}"))
    return out


def rule_i6(subjects, ctx):
    """I6 门禁行 ∈ gates.json 或真实存在的仓库脚本；不可用门禁 + ready-for-agent → FAIL。"""
    out = []
    for s in subjects:
        sec = s.sections.get("门禁")
        if not sec:
            continue
        for lineno, raw in nonblank_lines(sec.content):
            token = deformat(raw).strip().strip("`").rstrip("。.")
            if token.lower() in ("none", "无（rfc/experiment）", "不适用"):
                if s.issue_type_raw not in GATE_NONE_TYPES:
                    out.append(Finding(FAIL, f"{s.tag} 门禁写 `none`，但类型是 "
                                             f"{s.issue_type_raw or '（空）'}——只有 RFC / Experiment "
                                             f"可以无机器门禁（§4.1.1 例外 2）"))
                continue
            kind, payload = judge_gate_line(raw, ctx.gates)
            if kind == "unknown":
                out.append(Finding(FAIL, f"{s.tag} 门禁行「{raw}」既不是 gates.json 的 gate id，"
                                         f"也不含仓库内真实存在的脚本路径"))
                continue
            if kind == "prose":
                out.append(Finding(WARN, f"{s.tag} 门禁行「{raw}」无法解析为 gate id 或脚本命令"
                                         f"（§4.1 要求一行一条 gate id / 命令）"))
                continue
            if kind == "gate":
                g = ctx.gates[payload]
                if not g.get("available", True):
                    reason = g.get("unavailable_reason", "本环境不可用")
                    if s.ready_for_agent:
                        out.append(Finding(FAIL, f"{s.tag} 引用不可用门禁 `{payload}` 却标 "
                                                 f"state:ready-for-agent —— {reason}"))
                    else:
                        out.append(Finding(WARN, f"{s.tag} 引用不可用门禁 `{payload}`"
                                                 f"（未标 ready-for-agent，仅警告）—— {reason}"))
                continue
            missing = [p for p in payload if not (ROOT / p).exists()]
            if missing:
                out.append(Finding(FAIL, f"{s.tag} 门禁行的脚本路径不存在: " + " / ".join(missing)))
    return out


COMMAND_WORDS = ("python", "python3", "bash", "sh", "dotnet", "node", "npm", "pnpm",
                 "gh", "make", "pwsh", "powershell", "msbuild", "unity")

# 只有这些后缀的路径才算「门禁脚本」。没有这一层时，一行散文里提到的**文档**路径
# 会被当成被检查的脚本——实测 #134 的门禁行因此空过：它括号内的解释文字提到了
# design/engineering/issue-process.md，解析器判 script 并因该文件存在而 PASS，
# 而真正该检查的新门禁名 validate_ceiling_generator 从未被检查。
SCRIPT_SUFFIX = re.compile(r"\.(py|sh|bash|ps1|cmd)$")


def judge_gate_line(raw: str, gates: dict):
    """判定一行门禁：('gate', id) / ('script', [路径]) / ('unknown', None) / ('prose', None)。

    `prose` 是散文行（不含反引号/路径/命令词，也不是 id 形状）——调用方出 warning
    而不是 FAIL，避免把「本机不可用，替代验证方式见 …」这类说明误判成非法门禁。

    **路径须像脚本**（`SCRIPT_SUFFIX`）才判 `script`：一行里抽到的非脚本路径（如文档）
    不构成门禁，会继续下落——含反引号则判 `unknown`（FAIL），否则判 `prose`（warning）。
    """
    cleaned = raw.replace("`", "").strip()
    tokens = cleaned.split()
    first = tokens[0].rstrip("：:，,。;；") if tokens else ""
    if first in gates or cleaned in gates:
        return "gate", (first if first in gates else cleaned)
    paths = re.findall(r"((?:code|design|data|reference|\.github|\.agents)/[^\s`）)，,；;：:]+)",
                       cleaned)
    script_paths = [p for p in paths if SCRIPT_SUFFIX.search(p)]
    if script_paths:
        return "script", script_paths
    for gid, g in gates.items():
        cmd = g.get("command") or ""
        if cmd and cmd in cleaned:
            return "gate", gid
    looks_declaration = ("`" in raw) or first.lower() in COMMAND_WORDS \
        or bool(re.fullmatch(r"[A-Za-z0-9_.\-]+", cleaned))
    return ("unknown" if looks_declaration else "prose"), None


def rule_i7(subjects, ctx):
    """I7 blocked-by 未全部关闭时，本 issue 不得处于 state:in-progress。"""
    if ctx.snapshot is None:
        return [Finding(SKIP, "blocked-by 的关闭状态需要 issue 快照 —— 已跳过（需 --from-github）")]
    out = []
    states = ctx.snapshot["states"]
    for s in subjects:
        if not s.in_progress:
            continue
        deps = parse_dependencies(s)
        for n in deps.get("blocked-by", ("", []))[1]:
            st = states.get(n)
            if st is None:
                continue        # I5 已报引用不存在
            if st != "CLOSED":
                out.append(Finding(FAIL, f"{s.tag} 处于 state:in-progress，但 blocked-by #{n} 仍为 "
                                         f"{st}（未关闭，单线程约束失效）"))
    return out


def rule_i8(subjects, ctx):
    """I8 引用的仓库路径存在；段引用 §N 在目标文件中存在（段号找不到仅警告）。

    `交付物` / `预期差分` 两节豁免路径存在性检查——它们按定义描述尚未存在的
    产物（issue-process.md §4.1.1）。其余章节里的路径必须已存在。
    """
    out = []
    for s in subjects:
        seen = set()
        checked = body_without_sections(s.body, I8_EXEMPT_FIELDS)
        lines = checked.split("\n")
        for lineno, token, where in body_path_tokens(checked):
            if token in seen:
                continue
            seen.add(token)
            if (ROOT / token).exists():
                continue
            line = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
            # §4.1.1 例外 4：正文**显式标注**了该产物尚不存在（缺失/待建/将新增…）
            # 时降为警告——这条路径是 issue 的**主题**，不是隐藏依赖。
            if any(mk in line for mk in MISSING_MARKERS):
                out.append(Finding(WARN, f"{s.tag}:{lineno} {where}命名了尚不存在的产物"
                                         f"（已显式标注）: {token}"))
            else:
                out.append(Finding(FAIL, f"{s.tag}:{lineno} {where}引用仓库路径不存在: {token}"))
        for lineno, path, anchor in section_refs(s.body):
            target = ROOT / path
            if not target.exists():
                out.append(Finding(FAIL, f"{s.tag}:{lineno} 段引用目标文件不存在: {path} §{anchor}"))
            elif not section_exists(target, anchor):
                out.append(Finding(WARN, f"{s.tag}:{lineno} 段引用可能失效: {path} §{anchor}（段未找到）"))
    return out


def body_without_sections(body: str, fields) -> str:
    """删掉指定的 `### 标题` 章节（保持行数不变，行号仍可对上原文）。"""
    lines = body.split("\n")
    drop, current = False, False
    for i, line in enumerate(lines):
        m = re.match(r"^#{1,6}\s+(.*)$", line.strip())
        if m:
            current = norm_heading(m.group(1)) in {norm_heading(f) for f in fields}
            drop = current
        if drop:
            lines[i] = ""
    return "\n".join(lines)


def body_path_tokens(body: str):
    """正文里的仓库相对路径候选 → (行号, 路径, 位置说明)。

    只取**反引号内**与 **markdown 链接目标**（§I8 的判据面），避免把散文中的
    URL、绝对路径或含空格的自然语言当路径；含 `...`/通配符的省略写法跳过；
    ``` 代码块内的内容跳过（那是粘贴的证据，不是引用）。
    """
    out = []
    for i, line, in_fence in strip_code_fences(body):
        if in_fence:
            continue
        for span in re.findall(r"`([^`]+)`", line):
            for tok in re.split(r"[\s、,，;；]+", span):
                tok = clean_path_token(tok.split("§")[0])
                if is_repo_path(tok):
                    out.append((i, tok, "反引号内"))
        for m in re.finditer(r"\]\(([^)\s]+)\)", line):
            tok = clean_path_token(m.group(1).split("#")[0])
            if is_repo_path(tok):
                out.append((i, tok, "链接目标"))
    return out


def clean_path_token(tok: str) -> str:
    """剥掉行号后缀（`:42` / `:42:7` / `#L42`）与首尾标点——行号归 I9 管，不归 I8。

    否则 `X.cs:42` 会被 I8 当成"路径不存在"误报 FAIL（2026-09-12 实测）。
    """
    tok = re.sub(r"#L\d+(?:-L?\d+)?$", "", tok.strip())
    tok = re.sub(r":\d+(?::\d+)?$", "", tok)
    return tok.rstrip(".,;:、。，）)]}").strip()


def is_repo_path(tok: str) -> bool:
    """是否为仓库相对路径候选。

    带顶层前缀的（design/ code/ data/ reference/ .github/ .agents/）一律判；
    无前缀的根级文件（`WORKFLOW.md`）只有在确实存在时才判——否则散文里
    随手写的 `slice.md` 会变成误报 FAIL。
    """
    if not tok or any(c in tok for c in "*?<>{}|$") or "..." in tok:
        return False
    if tok.startswith(("http:", "https:", "mailto:", "/", "~/", "#", "../", "./")):
        return False
    if tok.startswith(REPO_PATH_PREFIXES):
        return True
    if re.fullmatch(r"[A-Za-z0-9_\-.]+\.(?:md|json|ya?ml|csproj|sln)", tok):
        return (ROOT / tok).exists()      # 根级文件：只认真实存在的
    return False


def section_refs(body: str):
    """段引用 `路径.md §N` → (行号, 路径, 段号)。"""
    out = []
    for i, line, _ in strip_code_fences(body):
        for m in re.finditer(
                r"`?([A-Za-z0-9_./\u4e00-\u9fff-]+\.md)`?\s*[§#]{1,2}\s*"
                r"([0-9]+(?:\.[0-9]+)*|[一二三四五六七八九十]+)", line):
            path = m.group(1)
            if is_repo_path(path):
                out.append((i, path, m.group(2)))
    return out


def rule_i9(subjects, ctx):
    """I9 正文不得出现 `文件.ext:行号` 或「第 N 行」式脆弱引用（警告）。"""
    out = []
    line_re = re.compile(r"[A-Za-z0-9_\-./\\]+\.(?:cs|py|md|json|ya?ml|csproj|sln|ts|tsx|js|jsx|"
                         r"html|css|sh|ps1|txt|toml|cfg|ini|unity|asset|meta|xml):\d+")
    cn_re = re.compile(r"第\s*\d+\s*(?:[-–~]\s*\d+\s*)?行")
    for s in subjects:
        for i, line, in_fence in strip_code_fences(s.body):
            for rx, label in ((line_re, "文件:行号"), (cn_re, "第 N 行")):
                m = rx.search(line)
                if m:
                    where = "（代码块内）" if in_fence else ""
                    out.append(Finding(WARN, f"{s.tag}:{i} {label}式脆弱引用{where}: {m.group(0)}"
                                             f"  ← §4.3 定位面禁止行号"))
    return out


def rule_i10(subjects, ctx):
    """I10 不得引用 design/archive/trash/（FAIL）；不得使用已废弃术语（警告）。"""
    out = []
    for s in subjects:
        for i, line, _ in strip_code_fences(s.body):
            if TRASH_PATH in line:
                out.append(Finding(FAIL, f"{s.tag}:{i} 引用垃圾桶路径 {TRASH_PATH}/ "
                                         f"（归档隔离，见 AGENTS.md §二）"))
        for term, replacement in ctx.deprecated_terms:
            rx = term_regex(term)
            if rx is None:
                continue
            for i, line, _ in strip_code_fences(s.body):
                if rx.search(line):
                    out.append(Finding(WARN, f"{s.tag}:{i} 使用已废弃术语「{term}」"
                                             f"（替代：{replacement[:80]}）"))
                    break       # 同一术语每个 issue 只报一次
    return out


def term_regex(term: str):
    """术语匹配：ASCII 词要求词边界（避免 AP 命中 CAPTCHA），CJK 直接子串。"""
    if not term:
        return None
    if re.fullmatch(r"[A-Za-z0-9_()\-.]+", term):
        return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])")
    return re.compile(re.escape(term))


def rule_i11(subjects, ctx):
    """I11 全仓同时 state:in-progress 的 issue ≤ 1。"""
    if ctx.snapshot is None:
        return [Finding(SKIP, "全仓 in-progress 统计需要 issue 快照 —— 已跳过（需 --from-github）")]
    running = [s for s in subjects if s.in_progress]
    if len(running) > 1:
        return [Finding(FAIL, "同时处于 state:in-progress 的 issue 有 "
                              f"{len(running)} 个（> 1，违反单线程约束）: "
                              + " ".join(s.tag for s in running))]
    if not running:
        return [Finding(WARN, "快照内没有 state:in-progress 的 issue（单线程约束空跑——"
                              "确认是否漏标标签）")]
    return []


def rule_i12(subjects, ctx):
    """I12 验收标准 2–8 条；能力增量 ≤ 3 行数据；门禁 ≥ 1 条。"""
    out = []
    for s in subjects:
        if "验收标准" in s.sections:
            items = list_items(s.content("验收标准"))
            if not (2 <= len(items) <= 8):
                out.append(Finding(FAIL, f"{s.tag} 验收标准 {len(items)} 条 ∉ [2, 8]"))
        sec = s.sections.get("能力增量")
        if sec:
            _, data = split_table(find_table(
                sec.content, lambda h: any(("能力" in deformat(c)) or ("轴" in deformat(c))
                                           for c in h)))
            if len(data) > 3:
                out.append(Finding(FAIL, f"{s.tag} 能力增量 {len(data)} 行 > 3（A1 单能力判据）"))
        if "门禁" in s.sections:
            n = len(nonblank_lines(s.content("门禁")))
            if n < 1:
                out.append(Finding(FAIL, f"{s.tag} 门禁 0 条（< 1）"))
    return out


def rule_i13(subjects, ctx):
    """I13 并行就绪的多条 issue，其「预期差分」声明的文件集合不得相交。

    语义独立 ≠ 可以并行：两条就绪 issue 改同一个文件时，谁先落地都会让另一条
    的 diff 变成冲突，故必须串行（issue-process.md §三 Step 4）。
    「就绪」= blocked-by 为空或全部已关闭（无快照时按"无 blocked-by"近似）。
    """
    if ctx.snapshot is None:
        return [Finding(SKIP, "并行就绪判定需要 issue 快照 —— 已跳过（需 --from-github）")]
    global BASENAME_INDEX
    if BASENAME_INDEX is None:
        BASENAME_INDEX = build_basename_index()
    ready = []
    blocked_labels = {"state:blocked", "status:blocked"}
    for s in subjects:
        if s.number in ctx.snapshot.get("closed_numbers", set()):
            continue
        if blocked_labels & set(s.labels):
            continue        # 自身已标 blocked（如被环境阻塞）→ 不进并行就绪集合
        deps = parse_dependencies(s)
        blockers = deps.get("blocked-by", (None, []))[1]
        if all(n in ctx.snapshot.get("closed_numbers", set()) for n in blockers):
            ready.append(s)
    if len(ready) < 2:
        return []
    owners = {}
    for s in ready:
        for path in expected_delta_paths(s.content("预期差分")):
            owners.setdefault(path, []).append(s.tag)
    out = []
    for path, tags in sorted(owners.items()):
        if len(tags) > 1:
            out.append(Finding(WARN, f"{path} 被多条并行就绪 issue 同时声明改动: "
                                     f"{' '.join(tags)}——须串行（I13）"))
    return out


def expected_delta_paths(content: str):
    """从「预期差分」抽出**允许变化**部分的文件路径集合（I13 的判定输入）。

    三条约束，都是被真实 issue 逼出来的：
    1. 只看「允许变化」那一半——「预期不变」里出现的路径恰恰是**不许改**的，
       把它算进来会造出假相交（第一版实现就踩了这个坑）
    2. 只认文件（带扩展名或真实存在于磁盘），不认目录——`code/` / `data/`
       这类指代太粗，会把任何两条 issue 都判成相交
    3. 裸文件名（如 `build-and-test.md`）按唯一基名解析到仓库路径；不唯一则忽略
    """
    changed = re.split(r"预期不变", content)[0]
    out = set()
    for _, line, in_fence in strip_code_fences(changed):
        if in_fence:
            continue
        spans = re.findall(r"`([^`]+)`", line) + re.findall(
            r"((?:design|code|data|reference|\.github)/[^\s`)，,；;：:、]+)", line)
        for span in spans:
            tok = clean_path_token(span.split("§")[0])
            if is_repo_path(tok):
                full = tok.rstrip("/")
                if (ROOT / full).is_file():
                    out.add(full)
                continue
            if re.fullmatch(r"[A-Za-z0-9_./-]+\.[A-Za-z0-9]+", tok):
                matches = BASENAME_INDEX.get(Path(tok).name) or []
                if len(matches) == 1:
                    out.add(matches[0])
    return out


def build_basename_index():
    """仓库受控文件按基名建索引（供裸文件名解析）。只扫已知顶层目录，避免全盘遍历。"""
    index = {}
    for top in ("design", "code", "data", "reference"):
        base = ROOT / top
        if not base.is_dir():
            continue
        for f in base.rglob("*"):
            if f.is_file() and ".git" not in f.parts:
                index.setdefault(f.name, []).append(str(f.relative_to(ROOT)))
    return index


BASENAME_INDEX = None   # 惰性构建


def rule_i14(subjects, ctx):
    """I14 正文 `blocked-by` 与 GitHub 原生依赖边（`blockedBy`）必须一致。

    权威是**正文**：创建前门禁（--file）在 issue 还不存在时就要判，且
    `requires:`（gate/PLAYABLE/能力/owner）没有原生对应物。原生边是**投影**，
    价值在于 GitHub UI 上的阻塞图标与反向可见性。两者不一致 → 警告。
    """
    if ctx.snapshot is None:
        return [Finding(SKIP, "原生依赖边比对需要 issue 快照 —— 已跳过（需 --from-github）")]
    native = ctx.snapshot.get("native_blocked_by")
    if native is None:
        return [Finding(SKIP, "快照未包含 blockedBy 字段（gh 版本过旧？）——已跳过")]
    out = []
    for s in subjects:
        if s.number is None:
            continue
        declared = set(parse_dependencies(s).get("blocked-by", (None, []))[1])
        actual = set(native.get(s.number) or set())
        for n in sorted(declared - actual):
            out.append(Finding(WARN, f"{s.tag} 正文声明 blocked-by: #{n}，但没有对应的原生依赖边"
                                     f"（UI 上看不到阻塞；可 `gh issue edit {s.number} --add-blocked-by {n}`）"))
        for n in sorted(actual - declared):
            out.append(Finding(WARN, f"{s.tag} 有原生依赖边 blocked-by #{n}，但正文 `依赖:` 未声明"
                                     f"——正文是权威，投影无声明即为不一致"))
    return out


# 单一规则表——照 issue-process.md §5.2 的 I1–I14 逐条对应，不增删含义。
RULES = [
    Rule("I1", "必填章节齐全（§4.1 九个 + §4.2 按类型追加）且非空", rule_i1),
    Rule("I2", "类型 ∈ 六种枚举；标签与正文类型一致", rule_i2),
    Rule("I3", "能力增量的轴 ∈ 四轴；从/到 ∈ 该轴合法状态", rule_i3),
    Rule("I4", "Design 未 ACCEPTED 的能力不得声明 Implementation 迁移", rule_i4),
    Rule("I5", "blocked-by / consumed-by / requires 引用的编号存在", rule_i5),
    Rule("I6", "门禁 ∈ gates.json 或真实存在的仓库脚本；不可用门禁 + ready → FAIL", rule_i6),
    Rule("I7", "blocked-by 未全关闭时不得 in-progress", rule_i7),
    Rule("I8", "引用的仓库路径存在；段引用 §N 存在", rule_i8),
    Rule("I9", "禁止 `文件:行号` / 「第 N 行」式脆弱引用（警告）", rule_i9),
    Rule("I10", "禁止引用 design/archive/trash/；禁止已废弃术语", rule_i10),
    Rule("I11", "全仓同时 in-progress 的 issue ≤ 1", rule_i11),
    Rule("I12", "验收标准 2–8 条；能力增量 ≤ 3 行；门禁 ≥ 1 条", rule_i12),
    Rule("I13", "并行就绪的 issue 预期差分文件集合不得相交（警告）", rule_i13),
    Rule("I14", "正文 blocked-by 与原生依赖边一致（警告）", rule_i14),
]


# ══════════════════════════════════════════════════════════════
# 快照（--from-github）
# ══════════════════════════════════════════════════════════════

def fetch_snapshot(repo, limit):
    """用 `gh issue list --json` 拉全量（open+closed）。

    gh 2.4.0 没有原生依赖边字段（§7.3），依赖只能读正文 `依赖:`；
    但 I7 需要被引用 issue 的关闭状态，故取 `--state all`（I5 的编号集合是它的子集）。
    任何失败 → InputUnavailable（退出码 2，绝不退 0）。
    """
    cmd = ["gh", "issue", "list", "--state", "all", "--limit", str(limit),
           "--json", GH_JSON_FIELDS]
    if repo:
        cmd += ["-R", repo]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    except FileNotFoundError:
        raise InputUnavailable("未找到 `gh` 命令——--from-github 模式不可用（退出码 2，不是通过）")
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip()
        hint = ""
        if re.search(r"auth|token|401|403|credential", err, re.I):
            hint = "\n  提示: 先 `gh auth login`，或在 CI 里设 GH_TOKEN/GITHUB_TOKEN（需 issues:read）"
        raise InputUnavailable(f"`gh issue list` 失败（退出码 {r.returncode}）:\n  {err[:600]}{hint}")
    try:
        items = json.loads(r.stdout or "[]")
    except json.JSONDecodeError as e:
        raise InputUnavailable(f"`gh issue list` 输出不是 JSON: {e}")

    truncated = len(items) >= limit
    numbers, states, open_items, native_blocked = set(), {}, [], {}
    for it in items:
        n = it.get("number")
        if n is None:
            continue
        numbers.add(n)
        states[n] = (it.get("state") or "").upper()
        nodes = ((it.get("blockedBy") or {}).get("nodes")) or []
        native_blocked[n] = {x.get("number") for x in nodes if x.get("number")}
        if states[n] == "OPEN":
            open_items.append(it)
    return {"numbers": numbers, "states": states, "open": open_items,
            "native_blocked_by": native_blocked,
            "total": len(items), "truncated": truncated}


def is_legacy(it: dict) -> bool:
    """§7.4 存量：**没有 type:* 标签** 且 **创建日期早于 2026-09-12**。"""
    labels = [l.get("name", "") for l in (it.get("labels") or [])]
    if any(l.lower().startswith("type:") for l in labels):
        return False
    created = (it.get("createdAt") or "")[:10]
    return bool(created) and created < LEGACY_CUTOFF


# ══════════════════════════════════════════════════════════════
# 运行
# ══════════════════════════════════════════════════════════════

class Ctx:
    def __init__(self, mode, labels=None, snapshot=None, gates=None,
                 deprecated_terms=None):
        self.mode = mode
        self.labels = labels or []
        self.labels_provided = bool(self.labels)
        self.snapshot = snapshot
        self.gates = gates or {}
        self.deprecated_terms = deprecated_terms or []


def run_rules(subjects, ctx):
    results = []
    for rule in RULES:
        try:
            findings = rule.fn(subjects, ctx) or []
        except InputUnavailable:
            raise
        except Exception as e:                      # 规则自身异常不得淡化成通过
            findings = [Finding(FAIL, f"规则执行异常: {type(e).__name__}: {e}")]
        statuses = {f.status for f in findings}
        if FAIL in statuses:
            status = FAIL
        elif WARN in statuses:
            status = WARN
        elif SKIP in statuses:
            status = SKIP
        else:
            status = PASS
        results.append((rule, status, findings))
    return results


def print_results(results, max_details=30):
    """逐条规则打印；同一段说明在多条规则上重复时只打印一次（如全量存量豁免）。"""
    print("\n## 规则结果")
    seen = set()
    for rule, status, findings in results:
        print(f"{ICON[status]}  [{rule.id}] {rule.desc}")
        shown = [f for f in findings if status != PASS]
        for f in shown[:max_details]:
            if f.message in seen and len(shown) == 1:
                continue        # 同因重复：只印一次，规则行本身仍在
            seen.add(f.message)
            mark = {FAIL: "FAIL", WARN: "WARN", SKIP: "SKIP", PASS: "PASS"}[f.status]
            print(f"      {mark}  {f.message}")
        if len(shown) > max_details:
            print(f"      … 另有 {len(shown) - max_details} 条同类问题（已截断）")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="validate_issues.py",
        description="issue 契约校验（issue-process.md §5.2 的 I1–I12）")
    parser.add_argument("--file", metavar="草稿.md",
                        help="校验一份临时草稿（issue 正文）；`-` 表示从 stdin 读")
    parser.add_argument("--label", dest="labels", action="append", default=[], metavar="NAME",
                        help="草稿将施加的标签，可重复（用于「标签 vs 正文类型」一致性）")
    parser.add_argument("--from-github", action="store_true",
                        help="拉取开放 issue 逐个校验（含跨 issue 的 I5/I7/I11）")
    parser.add_argument("--repo", metavar="OWNER/REPO", default=None,
                        help=f"--from-github 的仓库（默认 {DEFAULT_REPO}）")
    parser.add_argument("--limit", type=int, default=200,
                        help="--from-github 每个状态最多拉取条数（默认 200）")
    args = parser.parse_args(argv)

    if args.from_github and args.file:
        print("❌ 用法错误: --file 与 --from-github 互斥", file=sys.stderr)
        return 2
    if not args.from_github and not args.file:
        print("❌ 用法错误: 需要 --file <草稿.md>（或 `-`）或 --from-github", file=sys.stderr)
        return 2
    if args.limit < 1:
        print("❌ 用法错误: --limit 必须 ≥ 1", file=sys.stderr)
        return 2

    repo = args.repo or DEFAULT_REPO
    print("# validate_issues.py — issue 契约校验（I1–I12）")
    print("# 契约: design/engineering/issue-process.md §4/§5.2 · 门禁表: design/engineering/gates.json")

    try:
        gates = load_gates()
        deprecated_terms = load_deprecated_terms()
    except InputUnavailable as e:
        print(f"❌ 输入不可得: {e}", file=sys.stderr)
        return 2

    legacy, ctx = [], None

    if args.from_github:
        try:
            snap = fetch_snapshot(repo, args.limit)
        except InputUnavailable as e:
            print(f"❌ 输入不可得: {e}", file=sys.stderr)
            return 2

        print("\n## 范围")
        print(f"- 模式: --from-github（repo {repo}）")
        print(f"- 拉取 issue: {snap['total']}（open {len(snap['open'])} / 全量编号 {len(snap['numbers'])}）"
              f" · gh {gh_version()}")
        if snap["truncated"]:
            print(f"- ⚠️ 拉取条数达到 --limit {args.limit}，快照可能被截断"
                  f"（I5/I11 结论不完整——请提高 --limit）")

        subjects = []
        for it in snap["open"]:
            if is_legacy(it):
                legacy.append(it)
                continue
            subjects.append(Subject(
                body=it.get("body") or "",
                number=it.get("number"),
                title=it.get("title") or "",
                labels=[l.get("name", "") for l in (it.get("labels") or [])],
                created_at=it.get("createdAt") or "",
                state=(it.get("state") or "").upper(),
            ))
        print(f"- 受校验 issue: {len(subjects)}"
              + (f"（{' '.join(s.tag for s in subjects)}）" if subjects else ""))
        print(f"- 存量豁免（§7.4）: {len(legacy)}")
        ctx = Ctx("github", labels=args.labels, snapshot=snap,
                  gates=gates, deprecated_terms=deprecated_terms)
    else:
        if args.file == "-":
            body = sys.stdin.read()
            if not body.strip():
                print("❌ 输入不可得: stdin 为空（草稿必须从管道提供）", file=sys.stderr)
                return 2
            source = "<stdin>"
        else:
            p = Path(args.file)
            if not p.exists():
                print(f"❌ 输入不可得: 草稿 {args.file} 不存在", file=sys.stderr)
                return 2
            try:
                body = p.read_text(encoding="utf-8")
            except OSError as e:
                print(f"❌ 输入不可得: 无法读取 {args.file}: {e}", file=sys.stderr)
                return 2
            source = str(p)
        if not body.strip():
            print(f"❌ 输入不可得: 草稿 {source} 为空", file=sys.stderr)
            return 2
        print("\n## 范围")
        print(f"- 模式: --file {source}")
        print(f"- 标签: {' '.join(args.labels) if args.labels else '（未提供，跳过标签一致性比对）'}")
        print(f"- 识别章节: {len(parse_sections(body))} 个（按 `### 标题`）")
        print("- 跨 issue 规则（I5/I7/I11）在 --file 模式下无快照可判 → 将显式跳过")
        subjects = [Subject(body=body, labels=args.labels)]
        ctx = Ctx("file", labels=args.labels, snapshot=None,
                  gates=gates, deprecated_terms=deprecated_terms)

    # 快照内没有非存量 issue 时：全部规则显式跳过，绝不静默全绿
    if args.from_github and not subjects:
        results = [(rule, SKIP, [Finding(SKIP, "快照内无受校验 issue（全部为 §7.4 存量豁免）"
                                               "——未运行不是通过，本规则不计入 passed")])
                   for rule in RULES]
    else:
        results = run_rules(subjects, ctx)

    print_results(results)

    if legacy:
        nums = " ".join(f"#{it.get('number')}" for it in sorted(legacy, key=lambda x: x.get("number", 0)))
        print("\n## 存量豁免（issue-process.md §7.4）")
        print(f"跳过存量 issue {len(legacy)} 个（无 type:* 标签 且 创建日期 < {LEGACY_CUTOFF}）: {nums}")
        print("  —— 这些 issue 不追溯、不计入 passed，也不按 I1–I12 判罚。")

    n_pass = sum(1 for _, s, _ in results if s == PASS)
    n_fail = sum(1 for _, s, _ in results if s == FAIL)
    n_warn = sum(1 for _, s, _ in results if s == WARN)
    n_skip = sum(1 for _, s, _ in results if s == SKIP)

    print()
    if n_fail:
        failed = " ".join(r.id for r, s, _ in results if s == FAIL)
        print(f"❌ 未通过: {failed}")
    if n_skip:
        skipped = " ".join(r.id for r, s, _ in results if s == SKIP)
        print(f"⏭️ 已跳过（不计入通过）: {skipped}")
    if legacy:
        print(f"⏭️ 存量豁免 {len(legacy)} 个 issue（§7.4，不计入通过；清单见上）")
    print(f"{len(results)} rules: {n_pass} passed, {n_fail} failed, {n_warn} warnings, {n_skip} skipped")

    return 1 if n_fail else 0


def gh_version() -> str:
    try:
        r = subprocess.run(["gh", "--version"], capture_output=True, text=True)
        first = (r.stdout or "").split("\n")[0].split("(")[0].strip()
        return re.sub(r"^gh version\s+", "", first) or "?"
    except OSError:
        return "?"


if __name__ == "__main__":
    sys.exit(main())
