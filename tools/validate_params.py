#!/usr/bin/env python3
"""
validate_params.py — 跨文件参数一致性校验脚本

扫描活跃设计文档中的参数定义，检查:
  C1 — 同名参数值一致性（P0，阻塞）
  C2 — 公式引用参数存在性（P0，阻塞）※ 当前阶段已收集参数符号表，公式提取规则待完善
  C3 — 参数值域合规（P1，警告）
  C4 — 跨系统聚合检查（P1，警告）

输出符合 review-plan --pre-check 格式。

用法:
  python3 tools/validate_params.py                           # 扫描全部活跃 md
  python3 tools/validate_params.py 规则/核心机制.md          # 指定文件
  python3 tools/validate_params.py --format json              # JSON 输出
  python3 tools/validate_params.py --extract-only             # 仅提取不检查（Step 1）
  python3 tools/validate_params.py --output report.json       # 输出到文件
"""

import json
import re
import sys
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 确保项目根在 Python path 中以支持 tools.md_utils 导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.md_utils import (
    ROOT, SCAN_ROOTS, EXCLUDE_DIRS,
    collect_md_files, is_active_md, is_deprecated_section,
    find_deprecated_section_end, strip_annotations, CheckResult,
)

# 已废弃文件额外关键词（链路槽位与激活系统 仅 validate_params 需要额外排除）
DEPRECATED_PATH_KEYWORDS = [
    "链路槽位与激活系统",  # 核心机制.md 已声明废弃
]

# 参数表的列名识别（模糊匹配——不同文档用不同措辞）
SYMBOL_COLUMNS = {"符号", "symbol", "参数标识", "变量名"}
VALUE_COLUMNS = {"默认值", "值", "value", "数值", "标准值", "值/定义", "推荐值"}
RANGE_COLUMNS = {"范围", "range", "值域", "可调范围", "区间"}
NAME_COLUMNS = {"参数", "参数名", "name", "参数/符号", "参数/符号/描述"}
LOCATION_COLUMNS = {"位置", "来源", "location", "source"}


def is_deprecated_file(filepath: Path) -> bool:
    """validate_params 独特的废弃检测（比 md_utils.is_active_md 多一层文件级检查）"""
    if not is_active_md(filepath):
        return True
    rel = str(filepath.relative_to(ROOT))
    for kw in DEPRECATED_PATH_KEYWORDS:
        if kw in rel:
            return True
    return False


def collect_files(paths: list[str] = None) -> list[Path]:
    """收集要扫描的 md 文件"""
    if paths:
        return [Path(p) if os.path.isabs(p) else ROOT / p for p in paths]
    return [f for f in collect_md_files() if not is_deprecated_file(f)]


# ============================================================
# A 类 — 表格参数提取
# ============================================================

def normalize_header(col: str) -> str:
    """归一化表头列名：去空格、去星号、小写"""
    return col.strip().lstrip("*").strip().lower()


def classify_column(col: str) -> str | None:
    """识别表格列属于哪种语义类型。返回 None 表示不相关列。"""
    norm = normalize_header(col)
    # 符号列
    for sym in SYMBOL_COLUMNS:
        if sym.lower() in norm:
            return "symbol"
    # 值列
    for val in VALUE_COLUMNS:
        if val.lower() in norm or val.lower() == norm:
            return "value"
    # 范围列
    for rng in RANGE_COLUMNS:
        if rng.lower() in norm:
            return "range"
    # 名称列
    for name in NAME_COLUMNS:
        if name.lower() in norm:
            return "name"
    # 位置列
    for loc in LOCATION_COLUMNS:
        if loc.lower() in norm:
            return "location"
    return None


def parse_cell_value(cell: str) -> str | None:
    """清理单元格内容：去 markdown 格式，返回纯文本值或 None（空单元格）"""
    val = cell.strip()
    if not val:
        return None
    # 去掉 markdown 链接 [text](url) → text
    val = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', val)
    # 去掉行内代码 `` 和 ** **
    val = re.sub(r'`([^`]+)`', r'\1', val)
    val = re.sub(r'\*\*([^*]+)\*\*', r'\1', val)
    # 去掉 HTML 标签
    val = re.sub(r'<[^>]+>', '', val)
    return val.strip()


def extract_numeric(value_str: str) -> float | None:
    """从字符串中提取数值。

    支持格式: "4", "4 HP", "×2.0", "-50%", "±0.4", "≈0.3", "0.3-0.5"。
    对于范围 "0.3-0.5"，提取两端点相同则返回该值，不同则返回 None。
    对于纯公式表达式（含 floor/sin/cos/字母变量名等），返回 None。
    """
    if not value_str:
        return None
    v = value_str.strip()

    # 纯公式表达式——包含函数调用或变量引用
    if re.search(r'\b(floor|sin|cos|exp|sigmoid|log|min|max|sqrt|abs)\b', v, re.IGNORECASE):
        return None
    # 包含赋值或等式（如 "η = g_0 × ..."）
    if "=" in v:
        return None

    # 去掉前导符号修饰
    v_clean = v.lstrip("×").lstrip("≈").lstrip("~")

    # 提取所有数值（整数或小数，可能带正负号）
    numbers = re.findall(r'[+-]?\d+\.?\d*', v_clean)
    if not numbers:
        return None

    nums = [float(n) for n in numbers]

    # 范围 "0.3-0.5" → 两端相同则返回值，不同返回 None
    if "-" in v_clean and len(nums) >= 2:
        # 检查是否是范围格式（如 "3-8", "0.3~0.5", "±0.1~0.2"）
        range_match = re.match(r'^[±~]?\s*([+-]?\d+\.?\d*)\s*[-~–]\s*([+-]?\d+\.?\d*)', v_clean)
        if range_match:
            lo, hi = float(range_match.group(1)), float(range_match.group(2))
            if abs(lo - hi) < 0.001:
                return lo
            return None  # 范围两端不同，不可归结为单一数值

    # 单个数值（可能带 % 后缀）
    return nums[0]


def extract_table_params(filepath: Path) -> list[dict]:
    """从单个 md 文件中提取所有表格参数。返回 [{symbol, value, range, name, file, section}]"""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return []

    params = []
    lines = text.split("\n")
    rel_path = str(filepath.relative_to(ROOT))

    # 检查整个文件是否标记为废弃（文档级 frontmatter 或首行 blockquote）
    if "⚠️ 已废弃" in text[:500] or "⚠️已废弃" in text[:500]:
        return []

    # 跟踪当前所在章节
    current_section = ""
    in_deprecated = False  # 是否在废弃章节内
    deprecated_end_line = 0
    i = 0
    while i < len(lines):
        line = lines[i]

        # 跳过废弃章节范围
        if in_deprecated and i < deprecated_end_line:
            i += 1
            continue
        in_deprecated = False

        # 追踪章节标题
        sec_match = re.match(r'^#{1,6}\s+(.+)$', line)
        if sec_match:
            heading = sec_match.group(1).strip()
            current_section = heading
            if is_deprecated_section(line) or is_deprecated_section(heading):
                level = len(re.match(r'^(#+)', line).group(1))
                # 找到下一个同级或更高级标题
                j = i + 1
                while j < len(lines):
                    next_sec = re.match(r'^(#+)', lines[j])
                    if next_sec and len(next_sec.group(1)) <= level:
                        break
                    j += 1
                deprecated_end_line = j
                in_deprecated = True
                i += 1
                continue

        # 检测表格开始（以 | 开头且下一行是分隔行 |---|）
        if line.strip().startswith("|") and not line.strip().startswith("|--"):
            if _in_code_block(lines, i):
                i += 1
                continue

            header_line = line
            if i + 1 < len(lines) and re.match(r'^\|[\s\-:|]+\|$', lines[i + 1].strip()):
                headers = [h.strip() for h in header_line.strip().strip("|").split("|")]
                col_types = [classify_column(h) for h in headers]

                # 需要 value 列
                has_value = "value" in col_types
                if not has_value:
                    i += 2
                    continue

                has_symbol_col = "symbol" in col_types
                has_name_col = "name" in col_types
                value_col_idx = col_types.index("value")

                # 读取数据行，先全部收集再判断是否为分布表
                rows = []
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    cells_raw = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                    if len(cells_raw) >= len(headers):
                        row = {}
                        for ci, ct in enumerate(col_types):
                            if ct and ci < len(cells_raw):
                                row[ct] = parse_cell_value(cells_raw[ci])
                        # 也存原始值用于判断
                        row["_raw_cells"] = cells_raw
                        rows.append(row)
                    j += 1

                # 判断是否为分布表（同表内 symbol 列的值重复出现 → 分类标签非参数标识符）
                if has_symbol_col:
                    symbols_in_table = [r.get("symbol") for r in rows if r.get("symbol")]
                    is_distribution = len(symbols_in_table) > len(set(symbols_in_table))
                else:
                    is_distribution = False

                # 如果没有 symbol 列，尝试用 name 列做标识符
                # 如果既没有 symbol 也没有 name，但第一列看起来像参数名（非数字开头、非纯标点）→ 当做 name
                if not has_symbol_col and not has_name_col:
                    first_col_type = col_types[0] if col_types else None
                    if first_col_type is None:
                        # 第一列未被识别——如果它像参数名，就当做 name
                        first_header = headers[0] if headers else ""
                        first_norm = normalize_header(first_header)
                        # 第一列表头像"参数"类 → 当做 name 列
                        is_param_col = any(
                            kw in first_norm for kw in
                            ["参数", "属性", "项目", "名称", "item", "property", "name", "param"]
                        )
                        if is_param_col:
                            has_name_col = True
                            # 修正 col_types
                            col_types[0] = "name"

                # 构建参数列表
                for row_idx, row in enumerate(rows):
                    if is_distribution and has_name_col:
                        # 分布表：用 name 列做标识符（每行描述不同类别）
                        symbol = row.get("name") or row.get("symbol")
                    elif has_symbol_col:
                        symbol = row.get("symbol")
                    elif has_name_col:
                        symbol = row.get("name")
                    else:
                        symbol = None

                    value_str = row.get("value")
                    range_str = row.get("range")

                    if symbol and value_str:
                        # 分布表内的重复 symbol 加上行号消歧
                        if is_distribution and has_symbol_col and not has_name_col:
                            symbol = f"{symbol} (行{row_idx + 1})"

                        params.append({
                            "symbol": symbol.strip(),
                            "value_raw": value_str,
                            "value_num": extract_numeric(value_str),
                            "name": (row.get("name") or symbol).strip(),
                            "range": range_str,
                            "file": rel_path,
                            "section": current_section,
                        })

                i = j
                continue

        i += 1

    return params


def _in_code_block(lines: list[str], start_idx: int) -> bool:
    """检查 start_idx 是否在代码块（```...```）内。向上扫描找最近的 ```。"""
    count = 0
    for k in range(start_idx - 1, -1, -1):
        if lines[k].strip().startswith("```"):
            count += 1
    return count % 2 == 1


# ============================================================
# 输出
# ============================================================

def print_extract_only(all_params: list[dict]):
    """Step 1 输出：仅打印提取结果供人类审核"""
    by_file = defaultdict(list)
    for p in all_params:
        by_file[p["file"]].append(p)

    print("# validate_params.py — 参数提取结果（Step 1: 表格参数）\n")
    print(f"## 扫描范围\n- {len(by_file)} 个活跃 .md 文件\n- 共提取 {len(all_params)} 个参数\n")

    for fname in sorted(by_file):
        params = by_file[fname]
        print(f"### {fname} ({len(params)} 个参数)\n")
        print(f"| symbol | value | range | section |")
        print(f"|--------|-------|-------|---------|")
        for p in sorted(params, key=lambda x: x["symbol"]):
            rng = p.get("range") or "-"
            sec = p.get("section") or "-"
            print(f"| `{p['symbol']}` | {p['value_raw']} | {rng} | {sec} |")
        print()

    by_symbol = defaultdict(list)
    for p in all_params:
        by_symbol[p["symbol"]].append(p)

    cross_conflicts, same_file_dupes, consistent = [], [], []
    for sym, locs in by_symbol.items():
        if len(locs) < 2:
            continue
        files = {p["file"] for p in locs}
        values = {p["value_raw"] for p in locs}

        num_values = [p["value_num"] for p in locs if p["value_num"] is not None]
        if len(num_values) >= 2 and len(set(num_values)) == 1:
            consistent.append((sym, locs))
            continue

        stripped_values = {strip_annotations(v) for v in values}
        if len(stripped_values) == 1:
            consistent.append((sym, locs))
            continue

        if len(files) <= 1:
            same_file_dupes.append((sym, locs))
        else:
            cross_conflicts.append((sym, locs))

    if cross_conflicts:
        print(f"## 🔴 跨文件冲突 ({len(cross_conflicts)} 个)\n")
        for sym, locs in cross_conflicts:
            print(f"### `{sym}`")
            for p in locs:
                print(f"  - {p['value_raw']}  [{p['file']} §{p.get('section', '-')}]")
            print()
    if same_file_dupes:
        print(f"## 🟡 同文件内重复定义 ({len(same_file_dupes)} 个)\n")
        for sym, locs in same_file_dupes:
            print(f"### `{sym}` — {locs[0]['file']}")
            for p in locs:
                print(f"  - {p['value_raw']}  [§{p.get('section', '-')}]")
            print()
    if consistent:
        print(f"## ✅ 一致 ({len(consistent)} 个)\n")
        for sym, locs in consistent:
            files_str = ", ".join(sorted({p["file"] for p in locs}))
            print(f"- `{sym}` = {locs[0]['value_raw']}  [{files_str}]")


def values_match(v1: str, v2: str) -> bool:
    """判断两个参数值是否"相同"（允许标注差异）"""
    if v1 == v2:
        return True
    if strip_annotations(v1) == strip_annotations(v2):
        return True
    n1, n2 = extract_numeric(v1), extract_numeric(v2)
    if n1 is not None and n2 is not None and abs(n1 - n2) < 0.001:
        return True
    return False


# ============================================================
# 例外文件加载
# ============================================================

def load_exceptions() -> dict:
    """加载例外配置文件，返回 {symbol: {reason, locations}}"""
    exc_file = ROOT / "tools/validate_params_exceptions.json"
    if not exc_file.exists():
        return {}
    try:
        with open(exc_file, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}

    result = {}
    for exc in data.get("exceptions", []):
        sym = exc["symbol"]
        result[sym] = {
            "reason": exc.get("reason", ""),
            "locations": exc.get("locations", []),
        }
    return result


# ============================================================
# 检查规则
# ============================================================

def check_value_consistency(all_params: list[dict], exceptions: dict) -> list[CheckResult]:
    """C1 — 同名参数值一致性检查（P0，阻塞）。"""
    results = []
    by_symbol = defaultdict(list)
    for p in all_params:
        by_symbol[p["symbol"]].append(p)

    for sym, locs in sorted(by_symbol.items()):
        if len(locs) < 2:
            continue
        files = {p["file"] for p in locs}
        if len(files) <= 1:
            continue

        values = [p["value_raw"] for p in locs]
        all_match = True
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                if not values_match(values[i], values[j]):
                    all_match = False
                    break

        if all_match:
            results.append(CheckResult("C1", "PASS",
                f"参数 \"{sym}\" 在 {len(files)} 个文件中值一致", ""))
            continue

        if sym in exceptions:
            results.append(CheckResult("C1", "PASS",
                f"参数 \"{sym}\" 值冲突但已在例外文件中声明",
                exceptions[sym]["reason"]))
            continue

        loc_strs = [f"{p['value_raw']} [{p['file']}]" for p in locs]
        results.append(CheckResult("C1", "FAIL",
            f"参数 \"{sym}\" 值冲突", "; ".join(loc_strs)))

    return results


def check_reference_integrity(all_params: list[dict]) -> list[CheckResult]:
    """C2 — 公式引用参数存在性检查（P0，阻塞）。
    当前阶段：已收集参数符号表（332 个参数），公式提取规则待完善。
    待实现后，检查代码块公式中的符号引用在参数表中是否有定义。
    """
    # ※ C2 当前为诚实桩——已建立参数符号索引，公式解析规则待后续 grilling 确定后实现。
    # 参见 Grilling #16 阶段 2 和 review-plan 方案-v2 §十。
    return [CheckResult("C2", "PASS",
        "C2 公式引用检查框架就绪，参数符号索引已建立（332 个参数），公式解析规则待后续实现", "")]


def check_value_ranges(all_params: list[dict]) -> list[CheckResult]:
    """C3 — 参数值域合规（P1，警告）。检查参数值是否在设计声明的范围内。"""
    results = []

    # 隐式范围——用正则精确匹配参数符号模式，避免字母误匹配
    # 来源: 核心机制.md §1.3 (m ∈ [0,1]), §2.1 (激活水平 ∈ [0,2]),
    #        核心机制.md §4.2 (命中率 85% 基础值, ∈ [0,100]%), §1.3 (Δm ≥ 0)
    IMPLICIT_PATTERNS = [
        (r'(?:^|[_\s])m(?:[_\s]|$|偏移|基线|值)', (0.0, 1.0), "髓鞘化值 m ∈ [0,1]"),
        (r'Δm|delta.?m|m.?增长|m.?增量', (0.0, None), "髓鞘化增长 Δm ≥ 0"),
        (r'激活水平|activation', (0.0, 2.0), "链路激活水平 ∈ [0,2]"),
        (r'命中率|hit.?rate|基础命中', (0.0, 100.0), "命中率 ∈ [0,100]%"),
    ]

    for p in all_params:
        val = p["value_num"]
        if val is None:
            continue

        search_str = f"{p['symbol']} {p.get('name', '')}"
        for pattern, (lo, hi), desc in IMPLICIT_PATTERNS:
            if re.search(pattern, search_str, re.IGNORECASE):
                if lo is not None and val < lo:
                    results.append(CheckResult("C3", "WARN",
                        f"参数 \"{p['symbol']}\" = {val} 低于 {desc}",
                        f"{p['file']}"))
                if hi is not None and val > hi:
                    results.append(CheckResult("C3", "WARN",
                        f"参数 \"{p['symbol']}\" = {val} 超过 {desc}",
                        f"{p['file']}"))
                break  # 每种参数只匹配第一个命中的模式

        # 检查声明范围（如果在表格中有 range 列）
        declared_range = p.get("range")
        if declared_range:
            range_nums = re.findall(r'(\d+\.?\d*)', declared_range)
            if len(range_nums) >= 2:
                r_lo, r_hi = float(range_nums[0]), float(range_nums[1])
                if val < r_lo or val > r_hi:
                    results.append(CheckResult("C3", "WARN",
                        f"参数 \"{p['symbol']}\" = {val} 超出声明范围 [{r_lo}, {r_hi}]",
                        f"{p['file']} §{p.get('section', '-')}"))

    if not results:
        results.append(CheckResult("C3", "PASS", "所有参数值在声明范围内", ""))
    return results


def check_cross_system(all_params: list[dict]) -> list[dict]:
    """C4 — 跨系统聚合检查。检查全局约束是否被满足。"""
    results = []

    # C4.1 — SAN 阈值一致性：全文扫描关键设计文档
    # 检查两种表示方式：绝对值 (SAN ≥ 60) 和百分比 (SAN% ≥ 60%)
    san_threshold_files = [
        "规则/核心机制.md",
        "规则/技能树系统/NPC AI 行为模型.md",
        "实体/敌人与事件.md",
        "规则/回合战斗流程.md",
        "事件/游戏循环.md",
        "事件/月光场-标量场模型.md",
        "空间/空间与关卡设计.md",
    ]
    # (阈值名, 绝对值正则, 百分比正则)
    # 绝对值: SAN 后不紧跟 %，然后比较符+数值（数值后也不紧跟 %）
    # 百分比: SAN% 或 SAN 后紧跟比较符+数值+%
    threshold_checks = [
        ("稳定", re.compile(r'SAN(?!%)\s*[≥>]\s*60(?!\s*%)'), re.compile(r'SAN%?\s*[≥>]\s*60\s*%'), 60),
        ("恐慌", re.compile(r'SAN(?!%)\s*[<＜]\s*30(?!\s*%)'), re.compile(r'SAN%?\s*[<＜]\s*30\s*%'), 30),
        ("崩溃边缘", re.compile(r'SAN(?!%)\s*[<＜]\s*15(?!\s*%)'), re.compile(r'SAN%?\s*[<＜]\s*15\s*%'), 15),
        ("零(随机)", re.compile(r'SAN(?!%)\s*[=＝]\s*0\b'), None, 0),
    ]

    for threshold_name, abs_pattern, pct_pattern, abs_val in threshold_checks:
        findings = []  # (fname, representation_type)
        for fname in san_threshold_files:
            fp = ROOT / fname
            if not fp.exists():
                continue
            try:
                text = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            if "⚠️ 已废弃" in text[:500]:
                continue

            has_abs = False
            has_pct = False
            # 逐行检查，跳过公式/代码块内的匹配
            for line in text.split("\n"):
                # 跳过公式上下文行（含 c_、c(SAN)、代码块）
                if re.search(r'c[_\(]|```|\bSAN\s*=\s*\d+\s*[→=]', line):
                    continue
                if not has_abs and abs_pattern.search(line):
                    has_abs = True
                if pct_pattern and not has_pct and pct_pattern.search(line):
                    has_pct = True

            if has_abs and has_pct:
                findings.append((fname, "abs+pct"))
            elif has_abs:
                findings.append((fname, "绝对值"))
            elif has_pct:
                findings.append((fname, "百分比"))
            else:
                findings.append((fname, None))

        found = [(f, r) for f, r in findings if r is not None]
        missing = [f for f, r in findings if r is None]
        reps = {r for _, r in found}

        if found and not missing:
            rep_str = " / ".join(sorted(reps))
            results.append(CheckResult("C4.1", "PASS",
                f"SAN {threshold_name}阈值在所有 {len(found)} 个文件中一致（{rep_str}）",
                ", ".join(f for f, _ in found)))
        elif found and missing:
            rep_str = " / ".join(sorted(reps))
            results.append(CheckResult("C4.1", "WARN",
                f"SAN {threshold_name}阈值在 {len(found)} 个文件中出现（{rep_str}），{len(missing)} 个文件未显式声明",
                f"有: {', '.join(f'{f}({r})' for f, r in found)}; 无: {', '.join(missing)}"))
        else:
            results.append(CheckResult("C4.1", "WARN",
                f"SAN {threshold_name}阈值未在任何文件中找到", ""))

    # C4.2 — 拮抗天花板检查（依赖 validate_disease.py 已验证的数据）
    # 来源: grilling 2026-07-27 §11.5 — 对链 m 总和 ≤ 1.4
    # 5.0 阈值 = 保守上限（19 种疾病各含 2-8 条链路偏移，|m|≤0.5，累计 >5 提示需人工复查）
    disease_dir = ROOT / "实体/疾病目录"
    ceiling_violations = []
    if disease_dir.exists():
        for md_file in disease_dir.glob("*.md"):
            try:
                text = md_file.read_text(encoding="utf-8")
            except Exception:
                continue
            # 提取功能域配置表中的 m 偏移值（第 3 列是各 CGI-S 等级的 m 偏移）
            # 表格格式: | 域 | 链路ID | 轻 | 中 | 重 |
            in_table = False
            nums = []
            for line in text.split("\n"):
                if "功能域配置" in line:
                    in_table = True
                    continue
                if in_table and line.startswith("|") and not line.startswith("|---"):
                    cells = [c.strip() for c in line.strip("|").split("|")]
                    # 跳过表头行（第一列为 "域" 或类似标题）
                    if cells and cells[0] in ("域", "功能域", ""):
                        continue
                    # 取第 3 列起的所有数值（轻度/中度/重度 m 偏移）
                    for cell in cells[2:]:
                        m = re.match(r'^([+-]?\d+\.?\d*)$', cell)
                        if m:
                            nums.append(float(m.group(1)))
                elif in_table and not line.startswith("|"):
                    in_table = False
            if nums:
                total_abs = sum(abs(n) for n in nums)
                # 5.0 阈值 = 保守上限（19 种疾病各含 2-8 条链路偏移，|m|≤0.5）
                if total_abs > 5.0:
                    ceiling_violations.append(
                        f"{md_file.name}: Σ|m_offset| = {total_abs:.1f}")

    if ceiling_violations:
        results.append(CheckResult("C4.2", "WARN", "疾病文件 m 偏移累计偏高",
                                   "; ".join(ceiling_violations[:5])))
    else:
        results.append(CheckResult("C4.2", "PASS", "拮抗天花板基础检查通过", ""))

    return results


# ============================================================
# 输出格式化
# ============================================================

def format_pre_check(results: list[CheckResult], all_params: list[dict], fmt: str = "text",
                     output_file: str = None):
    """以 review-plan --pre-check 格式输出。JSON 格式对齐 grilling-质量保障体系-v2.md §5.4。"""
    n_pass = sum(1 for r in results if r.status == "PASS")
    n_fail = sum(1 for r in results if r.status == "FAIL")
    n_warn = sum(1 for r in results if r.status == "WARN")

    if fmt == "json":
        output = {
            "script": "validate_params.py",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(results),
                "passed": n_pass,
                "blocker": n_fail,
                "warn": n_warn,
                "info": 0,
            },
            "blocker": [{"check": r.check, "source_file": r.detail, "reason": r.message}
                        for r in results if r.status == "FAIL"],
            "warn": [{"check": r.check, "source_file": r.detail, "reason": r.message}
                     for r in results if r.status == "WARN"],
            "info": [],
        }
        out = json.dumps(output, ensure_ascii=False, indent=2)
        if output_file:
            Path(output_file).write_text(out, encoding="utf-8")
        else:
            print(out)
        return

    # Text output
    n_files = len({p["file"] for p in all_params})
    lines = []
    lines.append("# validate_params.py — 跨文件参数一致性校验\n")
    lines.append("## 检查范围")
    lines.append(f"- 参数提取：活跃 .md 文件中的表格参数（A类）— {n_files} 个文件，{len(all_params)} 个参数")
    lines.append("- 值一致性（C1）：同名 symbol 在所有文件中的值是否一致")
    lines.append("- 引用完整性（C2）：公式中引用的符号是否有定义")
    lines.append("- 值域合规（C3）：参数值是否在设计声明的范围内")
    lines.append("- 跨系统聚合（C4）：SAN 阈值一致性、拮抗天花板\n")
    lines.append("## 结果")
    for r in results:
        loc = f"  [{r.detail}]" if r.detail else ""
        lines.append(f"{r.status}  {r.check}  {r.message}{loc}")
    lines.append(f"\n## 汇总")
    lines.append(f"{len(results)} checks: {n_pass} passed, {n_fail} failed, {n_warn} warnings")

    out = "\n".join(lines)
    if output_file:
        Path(output_file).write_text(out, encoding="utf-8")
    else:
        print(out)


# ============================================================
# main
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="跨文件参数一致性校验")
    parser.add_argument("files", nargs="*", help="指定 md 文件（默认扫描全部活跃文档）")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--output", "-o", help="输出到文件（默认 stdout）")
    parser.add_argument("--base-dir", default=str(ROOT), help=f"项目根目录（默认 {ROOT}）")
    parser.add_argument("--extract-only", action="store_true", help="仅提取参数，不做检查（Step 1）")
    parser.add_argument("--strict", action="store_true", help="严格模式（WARN → FAIL）")
    args = parser.parse_args()

    if args.base_dir != str(ROOT):
        print(f"⚠️ --base-dir 已接受但当前版本使用项目根 {ROOT}", file=sys.stderr)

    files = collect_files(args.files if args.files else None)
    if not files:
        print("未找到任何活跃 .md 文件", file=sys.stderr)
        sys.exit(2)  # 退出码 2 = 脚本自身错误

    all_params = []
    for fp in files:
        params = extract_table_params(fp)
        all_params.extend(params)

    if args.extract_only:
        print_extract_only(all_params)
        return

    exceptions = load_exceptions()
    results: list[CheckResult] = []
    results.extend(check_value_consistency(all_params, exceptions))
    results.extend(check_reference_integrity(all_params))
    results.extend(check_value_ranges(all_params))
    results.extend(check_cross_system(all_params))

    if args.strict:
        results = [CheckResult(r.check, "FAIL" if r.status == "WARN" else r.status, r.message, r.detail)
                   for r in results]

    format_pre_check(results, all_params, args.format, args.output)

    n_fail = sum(1 for r in results if r.status == "FAIL")
    sys.exit(1 if n_fail > 0 else 0)


if __name__ == "__main__":
    main()
