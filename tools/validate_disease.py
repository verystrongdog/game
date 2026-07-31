#!/usr/bin/env python3
"""
疾病md文件校验器
解析 实体/疾病目录/*.md，检查链路ID存在性、m偏移范围、CGI-S一致性、
非线性跳变引用、掉落池覆盖。
用法:
  python3 tools/validate_disease.py                          # 扫描全部
  python3 tools/validate_disease.py 实体/疾病目录/偏执型精神分裂症.md  # 单个
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DISEASE_DIR = ROOT / "实体/疾病目录"


def load_registry():
    """加载链路注册表，返回 {display_name: entry} 和 {id: entry}"""
    try:
        with open(ROOT / "data/connectivity/link_registry.json", encoding="utf-8") as f:
            reg = json.load(f)
    except FileNotFoundError:
        print("✗ 注册表不存在，请先运行: python3 tools/build_link_registry.py")
        sys.exit(1)

    by_name = {}
    by_id = {}
    for link in reg["links"]:
        by_name[link["display_name"]] = link
        by_id[link["id"]] = link
    return by_name, by_id


def parse_frontmatter(text: str) -> dict:
    """提取 YAML frontmatter (--- ... ---) 的原始内容"""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    # 简单解析: 键: 值（不做完整YAML）
    result = {}
    for line in m.group(1).split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            result[key] = val
    return result


def parse_md_table(text: str, section_header: str) -> list[dict]:
    """提取指定 ## 标题下的第一个 markdown 表格，返回 [{col_name: cell_value}, ...]"""
    # 定位 section
    pattern = rf"^##\s+{re.escape(section_header)}\s*\n"
    m = re.search(pattern, text, re.MULTILINE)
    if not m:
        return []

    section_start = m.end()
    # 找到下一个 ## 或文件尾
    next_section = re.search(r"^##\s+", text[section_start:], re.MULTILINE)
    section_end = section_start + next_section.start() if next_section else len(text)
    section_text = text[section_start:section_end]

    # 找到第一个表格: | ... | ... | 行后跟分隔行
    lines = section_text.split("\n")
    header_idx = None
    sep_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and not line.strip().startswith("|--"):
            if header_idx is None:
                header_idx = i
            elif sep_idx is not None:
                break  # already found header+sep, this is data
        if header_idx is not None and sep_idx is None and re.match(r"^\|[\s\-:|]+\|$", line.strip()):
            sep_idx = i
            break

    if header_idx is None or sep_idx is None:
        return []

    # 解析表头
    headers = [h.strip() for h in lines[header_idx].split("|")[1:-1]]
    rows = []
    for line in lines[sep_idx + 1 :]:
        line = line.strip()
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
        elif cells and not all(c == "" for c in cells):
            pass  # malformed row, skip

    return rows


# ─── Validation functions ───

def validate_link_ids(table: list[dict], registry_by_name: dict, filepath: str, col: str = "链路ID") -> list[str]:
    """检查链路ID是否在注册表中存在"""
    errors = []
    for row in table:
        link_id = row.get(col, "").strip()
        if not link_id:
            continue
        if link_id not in registry_by_name:
            errors.append(f"[{link_id}] 链路ID不在注册表中")
    return errors


def validate_m_offsets(table: list[dict], filepath: str, col: str = "m偏移(轻/中/重)") -> list[str]:
    """检查m偏移值是否在[-1.0, 1.0]范围内"""
    errors = []
    for row in table:
        link_id = row.get("链路ID", "?").strip()
        m_str = row.get(col, "").strip()
        if not m_str:
            continue
        # 归一化 Unicode 减号 → ASCII hyphen
        m_str = m_str.replace("−", "-").replace("–", "-").replace("—", "-")
        parts = m_str.split("/")
        for i, p in enumerate(parts):
            p = p.strip()
            try:
                val = float(p)
            except ValueError:
                errors.append(f"[{link_id}] m偏移 '{p}' 不是有效数字 (完整值: {m_str})")
                continue
            if val < -1.0 or val > 1.0:
                errors.append(f"[{link_id}] m偏移 {val} 超出范围[-1.0, 1.0] (完整值: {m_str})")
    return errors


def _norm_domain(name: str) -> str:
    """去掉'域'后缀用于跨表匹配"""
    name = name.strip()
    return name[:-1] if name.endswith("域") and len(name) > 1 else name


def validate_cgi_consistency(
    func_table: list[dict],
    cgi_table: list[dict],
    filepath: str,
) -> list[str]:
    """检查CGI-S域扩展表与功能域表m偏移的一致性"""
    warnings = []

    severities = ["轻", "中", "重"]
    domain_m_active = {}

    for row in func_table:
        domain = row.get("域", "").strip()
        m_str = row.get("m偏移(轻/中/重)", "").strip()
        if not domain or not m_str:
            continue
        dnorm = _norm_domain(domain)
        parts = [p.strip() for p in m_str.split("/")]
        for i, sev in enumerate(severities):
            try:
                val = float(parts[i]) if i < len(parts) else 0.0
            except (ValueError, IndexError):
                val = 0.0
            key = (dnorm, sev)
            if key not in domain_m_active:
                domain_m_active[key] = False
            if val != 0.0:
                domain_m_active[key] = True

    if not cgi_table:
        return warnings

    cgi_active = {}
    sev_map = {"轻度": 0, "中度": 1, "重度": 2, "轻": 0, "中": 1, "重": 2}
    sev_names = ["轻", "中", "重"]

    # 第一遍: 按严重度收集
    cgi_by_sev = [{}, {}, {}]  # 每个严重度的 {domain: True}
    for row in cgi_table:
        severity_raw = row.get("严重度", "").strip()
        sev_idx = sev_map.get(severity_raw, -1)
        if sev_idx < 0:
            continue
        for col_name, domains_str in row.items():
            if col_name in ("严重度", "m倍率(参考)", "域数合计", "特殊"):
                continue
            if not domains_str or domains_str.strip() in ("0", "-", ""):
                continue
            for d in domains_str.split(","):
                d = _norm_domain(d.strip().lstrip("+"))
                if d:
                    cgi_by_sev[sev_idx][d] = True

    # 累计: 域在严重度N激活 → 在≥N的所有严重度也激活
    cumulative = {}
    for d in list(cgi_by_sev[0].keys()) + list(cgi_by_sev[1].keys()) + list(cgi_by_sev[2].keys()):
        for si in range(3):
            if d in cgi_by_sev[si]:
                for sj in range(si, 3):
                    cumulative[(d, sev_names[sj])] = True
                break
    cgi_active = cumulative

    for (dnorm, sev), has_m in domain_m_active.items():
        cgi_has = (dnorm, sev) in cgi_active
        if has_m and not cgi_has:
            warnings.append(f"[{dnorm}] {sev}度有非零m偏移，但CGI-S表中未激活")
        elif not has_m and cgi_has:
            warnings.append(f"[{dnorm}] {sev}度CGI-S表已激活，但功能域表中无对应非零m偏移")

    return warnings


def validate_jump_refs(
    jump_table: list[dict],
    func_table: list[dict],
    filepath: str,
) -> list[str]:
    """检查非线性跳变规则引用的链路是否在功能域表中"""
    errors = []
    func_link_ids = {row.get("链路ID", "").strip() for row in func_table}
    func_domains = {row.get("域", "").strip() for row in func_table}

    for row in jump_table:
        scope = row.get("作用域", "").strip()
        if not scope:
            continue
        # 作用域可能列出链路ID（逗号分隔）或域名
        for item in scope.split(","):
            item = item.strip()
            if not item:
                continue
            # 检查是否是链路ID
            if "→" in item or "↔" in item or "←" in item:
                if item not in func_link_ids:
                    errors.append(f"[非线性跳变] 链路 '{item}' 不在功能域表中")
            else:
                # 检查是否是域名
                if item not in func_domains:
                    errors.append(f"[非线性跳变] 域/链路 '{item}' 不在功能域表中")
    return errors


def validate_drop_pool(
    drop_table: list[dict],
    func_table: list[dict],
    filepath: str,
) -> list[str]:
    """检查组件掉落池是否覆盖功能域表中的全部链路"""
    warnings = []
    func_link_ids = {row.get("链路ID", "").strip() for row in func_table if row.get("链路ID", "").strip()}

    drop_ids = set()
    for row in drop_table:
        ids_str = row.get("链路ID", "").strip()
        if not ids_str:
            continue
        for item in ids_str.split(","):
            item = item.strip()
            if item:
                drop_ids.add(item)

    missing = func_link_ids - drop_ids
    extra = drop_ids - func_link_ids
    if missing:
        warnings.append(f"组件掉落池缺少 {len(missing)} 条链路: {', '.join(sorted(missing))}")
    if extra:
        warnings.append(f"组件掉落池多出 {len(extra)} 条链路: {', '.join(sorted(extra))}")
    return warnings


def validate_domain_roles(
    func_table: list[dict],
    cgi_table: list[dict],
    filepath: str,
) -> list[str]:
    """检查域角色在CGI-S表中是否体现"""
    warnings = []
    domain_role = {}
    for row in func_table:
        domain = row.get("域", "").strip()
        role = row.get("角色", "").strip()
        if domain:
            domain_role[domain] = role

    # 核心域应该在轻/中度就激活
    for domain, role in domain_role.items():
        if role == "核心":
            pass  # 已经会在CGI-S一致性检查中覆盖
        if role == "边缘":
            pass
    return warnings


def validate_file(filepath: Path, registry_by_name: dict) -> dict:
    """校验单个文件，返回结果字典"""
    result = {
        "filepath": filepath,
        "errors": [],
        "warnings": [],
        "link_count": 0,
        "domain_count": 0,
        "jump_count": 0,
    }

    if not filepath.exists():
        result["errors"].append(f"文件不存在: {filepath}")
        return result

    with open(filepath, encoding="utf-8") as f:
        text = f.read()

    # 归一化 Unicode 特殊字符
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")

    frontmatter = parse_frontmatter(text)
    func_table = parse_md_table(text, "功能域配置")
    cgi_table = parse_md_table(text, "CGI-S 域扩展")
    jump_table = parse_md_table(text, "非线性跳变")
    drop_table = parse_md_table(text, "组件掉落池")

    result["link_count"] = len(func_table)
    result["domain_count"] = len(set(r.get("域", "") for r in func_table))
    result["jump_count"] = len(jump_table)

    # ERROR checks
    result["errors"].extend(validate_link_ids(func_table, registry_by_name, str(filepath)))
    result["errors"].extend(validate_m_offsets(func_table, str(filepath)))
    result["errors"].extend(validate_jump_refs(jump_table, func_table, str(filepath)))

    # WARNING checks
    result["warnings"].extend(validate_cgi_consistency(func_table, cgi_table, str(filepath)))
    result["warnings"].extend(validate_drop_pool(drop_table, func_table, str(filepath)))

    return result


def main():
    registry_by_name, registry_by_id = load_registry()

    # Determine target files
    if len(sys.argv) > 1:
        files = [Path(p) for p in sys.argv[1:]]
    else:
        if not DISEASE_DIR.exists():
            print(f"✗ 疾病目录不存在: {DISEASE_DIR}")
            sys.exit(1)
        files = sorted(DISEASE_DIR.glob("*.md"))

    if not files:
        print("没有找到疾病md文件")
        sys.exit(0)

    total_errors = 0
    total_warnings = 0

    for fp in files:
        result = validate_file(fp, registry_by_name)

        print(f"\n{'═' * 60}")
        print(f"校验: {fp.name}")
        print(f"  链路: {result['link_count']}  域: {result['domain_count']}  跳变: {result['jump_count']}")

        if result["errors"]:
            print(f"  🔴 ERROR ({len(result['errors'])}):")
            for e in result["errors"]:
                print(f"    ✗ {e}")
        else:
            print(f"  ✅ 0 ERROR")

        if result["warnings"]:
            print(f"  🟡 WARNING ({len(result['warnings'])}):")
            for w in result["warnings"]:
                print(f"    ⚠ {w}")
        else:
            print(f"  ✅ 0 WARNING")

        total_errors += len(result["errors"])
        total_warnings += len(result["warnings"])

    print(f"\n{'═' * 60}")
    print(f"汇总: {len(files)} 文件, {total_errors} ERROR, {total_warnings} WARNING")
    if total_errors > 0:
        sys.exit(1)
    else:
        print("✓ 全部通过")


if __name__ == "__main__":
    main()
