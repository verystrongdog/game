#!/usr/bin/env python3
"""
疾病md文件校验器
解析 实体/疾病目录/*.md，检查链路ID存在性、m偏移范围、CGI-S一致性、
非线性跳变引用、掉落池覆盖、域数约束（轻度1-2核心/中度+关联/重度+边缘）。
用法:
  python3 tools/validate_disease.py                          # 扫描全部
  python3 tools/validate_disease.py 实体/疾病目录/偏执型精神分裂症.md  # 单个
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("需要 PyYAML: pip install pyyaml")
    sys.exit(1)

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
    """提取 YAML frontmatter (--- ... ---)，返回解析后的 dict。

    返回值类型: dict[str, Any]。嵌套键（如父类的"功能域定性方向"）
    将被解析为嵌套 dict；YAML null → Python None。
    """
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


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

# P0.1: 病理类型合法值
VALID_PATHOLOGY_TYPES = {"跨层短路", "过度耦合", "解耦沉默", "结构异常", "边界崩溃"}


def validate_pathology_types(pathology_str: str, link_id: str = "?") -> list[str]:
    """检查病理类型是否为合法值（支持 + 复合语法）。

    Args:
        pathology_str: 病理类型字符串，如 "解耦沉默 + 过度耦合"
        link_id: 链路ID，用于错误信息
    Returns:
        ERROR 列表（空列表 = 通过）
    """
    errors = []
    raw = pathology_str.strip()
    if not raw:
        errors.append(f"[{link_id}] 病理类型为空")
        return errors

    # 检查非法分隔符
    for ch in ["→", ",", "|"]:
        if ch in raw:
            errors.append(
                f"[{link_id}] 病理类型含非法分隔符 '{ch}'（仅支持 + 分隔）: {raw}"
            )
            return errors

    # 按 + split 逐项检查
    parts = [p.strip() for p in raw.split("+")]
    for p in parts:
        if not p:
            errors.append(f"[{link_id}] 病理类型含空项（连续 + 或首尾 +）: {raw}")
            continue
        if p not in VALID_PATHOLOGY_TYPES:
            errors.append(
                f"[{link_id}] 病理类型 '{p}' 不是合法值"
                f"（合法: {', '.join(sorted(VALID_PATHOLOGY_TYPES))}）: {raw}"
            )
    return errors

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
    cgi_table: list[dict] | None = None,
) -> tuple[list[str], list[str]]:
    """检查组件掉落池：链路覆盖 + 权重格式 + tier 范围。

    Returns:
        (errors, warnings) — errors 为空格式错误，warnings 为链路覆盖/权重范围
    """
    errors: list[str] = []
    warnings: list[str] = []

    func_link_ids = {row.get("链路ID", "").strip() for row in func_table if row.get("链路ID", "").strip()}

    # ── 链路覆盖检查（原有逻辑，WARNING） ──
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

    # ── P0.2: 权重格式校验（ERROR） ──
    weight_re = re.compile(r"^(\d+)\s*\((核心|关联|边缘)\)$")
    max_weight = 0
    for row in drop_table:
        weight_str = row.get("权重", "").strip()
        if not weight_str:
            continue
        m = weight_re.match(weight_str)
        if not m:
            errors.append(f"组件掉落池 权重格式错误: '{weight_str}' — 应为 'N (核心|关联|边缘)'")
            continue
        w = int(m.group(1))
        if w < 1:
            errors.append(f"组件掉落池 权重值 {w} < 1: '{weight_str}'")
        max_weight = max(max_weight, w)

    # ── P0.2: tier 范围校验（WARNING） ──
    if cgi_table and max_weight > 0:
        actual_tiers = _count_actual_tiers(cgi_table)
        if max_weight > actual_tiers:
            warnings.append(
                f"组件掉落池 最大权重 {max_weight} 超过实际 tier 数 {actual_tiers}"
                f"（CGI-S 表中有 {actual_tiers} 个 tier 列非空）"
            )

    return errors, warnings


def _count_actual_tiers(cgi_table: list[dict]) -> int:
    """计算 CGI-S 域扩展表中'实际出现的 tier 数'。

    一个 tier "存在" = 在任一严重度行中该 tier 列至少有一个非空域名。
    tier 列: 核心域 / 关联域 / 边缘域。
    """
    tier_cols = ["核心域", "关联域", "边缘域"]
    active_tiers = 0
    for col in tier_cols:
        for row in cgi_table:
            cell = row.get(col, "").strip()
            if cell and cell not in ("0", "-"):
                active_tiers += 1
                break  # 该 tier 存在，跳到下一个
    return max(active_tiers, 1)  # 至少 1 个 tier


def validate_domain_count_constraints(
    func_table: list[dict],
    cgi_table: list[dict],
    filepath: str,
) -> list[str]:
    """检查域数约束: 轻度1-2核心域 / 中度+关联域 / 重度+边缘域

    从 CGI-S域扩展表 推断每个域的角色（核心/关联/边缘），
    然后检查功能域表中的 m 偏移是否与域角色一致。

    注意：域级角色（核心域 vs 关联域）定义在 CGI-S 域扩展表中，
    不在功能域配置表中。功能域配置表不设"角色"列。

    规则来源: 决策树 [Grilling] 疾病系统独立建模 §域数 (2026-08-01)
    """
    warnings = []

    if not cgi_table:
        return warnings  # 无CGI-S表则跳过

    # ── 从 CGI-S 域扩展表推断域级角色 ──
    def _parse_domains(cell: str) -> set[str]:
        """解析 CGI-S 表中的域列表"""
        if not cell or cell.strip() in ("0", "-", ""):
            return set()
        result = set()
        for d in cell.split(","):
            d = d.strip().lstrip("+")
            dnorm = _norm_domain(d)
            if dnorm:
                result.add(dnorm)
        return result

    core_domains = set()      # 在轻度核心域列出现的域
    assoc_domains = set()     # 在中度关联域列出现（且不在轻度核心域列中）的域
    peri_domains = set()      # 在重度边缘域列出现（且不在前两者中）的域

    for row in cgi_table:
        sev = row.get("严重度", "").strip()
        if sev == "轻度":
            core_domains = _parse_domains(row.get("核心域", ""))
        elif sev == "中度":
            mid_core = _parse_domains(row.get("核心域", ""))
            mid_assoc_raw = _parse_domains(row.get("关联域", ""))
            # 关联域 = 在中度新出现的（不在轻度核心域中）
            assoc_domains = mid_assoc_raw - core_domains
        elif sev == "重度":
            sev_core = _parse_domains(row.get("核心域", ""))
            sev_assoc = _parse_domains(row.get("关联域", ""))
            sev_peri = _parse_domains(row.get("边缘域", ""))
            # 边缘域 = 在重度新出现的（不在核心域+关联域中）
            peri_domains = sev_peri - core_domains - assoc_domains

    # ── 按域汇总 m 偏移 ──
    # 对每个域，收集所有链路的 m 偏移，取最大绝对值作为"该域在该严重度的活跃度"
    domain_m_max = {}  # {dnorm: [m_mild_max, m_moderate_max, m_severe_max]}
    for row in func_table:
        domain = row.get("域", "").strip()
        m_str = row.get("m偏移(轻/中/重)", "").strip()
        if not domain:
            continue
        dnorm = _norm_domain(domain)
        m_str = m_str.replace("−", "-").replace("–", "-").replace("—", "-")
        parts = [p.strip() for p in m_str.split("/")]
        try:
            m_vals = [abs(float(p)) if p else 0.0 for p in parts[:3]]
        except ValueError:
            continue
        if dnorm not in domain_m_max:
            domain_m_max[dnorm] = [0.0, 0.0, 0.0]
        for i in range(3):
            domain_m_max[dnorm][i] = max(domain_m_max[dnorm][i], m_vals[i])

    # ── 检查1: 核心域在轻度应有非零 m ──
    inactive_core = []
    for d in core_domains:
        max_m = domain_m_max.get(d, [0, 0, 0])
        if max_m[0] == 0.0:
            inactive_core.append(d)
    if inactive_core:
        warnings.append(f"[域数约束] 核心域在轻度无任何非零m偏移: {', '.join(inactive_core)}")

    # ── 检查2: 关联域在轻度不应有非零 m ──
    assoc_early = []
    for d in assoc_domains:
        max_m = domain_m_max.get(d, [0, 0, 0])
        if max_m[0] != 0.0:
            assoc_early.append(d)
    if assoc_early:
        warnings.append(f"[域数约束] 关联域在轻度有非零m偏移（应在中度才激活）: {', '.join(assoc_early)}")

    # ── 检查3: 边缘域在轻/中度不应有非零 m ──
    peri_early = []
    for d in peri_domains:
        max_m = domain_m_max.get(d, [0, 0, 0])
        if max_m[0] != 0.0 or max_m[1] != 0.0:
            peri_early.append(d)
    if peri_early:
        warnings.append(f"[域数约束] 边缘域在轻/中度有非零m偏移（应在重度才激活）: {', '.join(peri_early)}")

    # ── 检查4: 核心域数量（轻度）──
    if len(core_domains) < 1:
        warnings.append(f"[域数约束] CGI-S表中轻度无核心域")
    # >2 核心域不报警告（多域疾病如精神分裂症天然需要）

    return warnings


# ═══════════════════════════════════════════════════════════════
# P0.3: 父类继承校验
# ═══════════════════════════════════════════════════════════════

# P0.3-B: 病理类型矛盾矩阵（仅信号强度轴对立）
# 解耦沉默（信号减弱）↔ 过度耦合（信号过强）矛盾。
# 跨层短路/结构异常/边界崩溃 是路径/架构异常，与任何类型共存。
_CONTRADICT = {("解耦沉默", "过度耦合"), ("过度耦合", "解耦沉默")}


def _compute_net_direction(
    domain_links: list[tuple[str, list[float]]],
) -> tuple[int, str]:
    """计算一个域的"净 m 方向"。

    Args:
        domain_links: [(link_id, [m_mild, m_mod, m_sev]), ...]

    Returns:
        (net_sign, severity_used)
        net_sign: 1 (↑), -1 (↓), 0 (无有效偏移)
        severity_used: "重"/"中"/"轻"/"无"
    """
    sev_indices = [2, 1, 0]  # 重, 中, 轻
    sev_names = ["重", "中", "轻"]
    for si, sname in zip(sev_indices, sev_names):
        total_abs = sum(abs(links[si]) for _, links in domain_links)
        if total_abs > 0:
            net = sum(links[si] for _, links in domain_links)
            if net > 0:
                return (1, sname)
            elif net < 0:
                return (-1, sname)
            else:
                return (0, sname)
    return (0, "无")


def validate_parent_inheritance(
    filepath: Path, parent_dir: Path
) -> tuple[list[str], list[str]]:
    """P0.3-A+B: per-file 父类继承校验（域方向 + 病理类型矛盾）。"""
    errors: list[str] = []
    warnings: list[str] = []

    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")

    child_fm = parse_frontmatter(text)
    parent_name = child_fm.get("父类", "")
    if not parent_name:
        warnings.append("未声明父类（frontmatter 中无 '父类:' 字段）")
        return errors, warnings

    parent_path = parent_dir / f"{parent_name}.md"
    if not parent_path.exists():
        errors.append(f"父类文件不存在: {parent_path}")
        return errors, warnings

    with open(parent_path, encoding="utf-8") as f:
        parent_text = f.read()
    parent_text = parent_text.replace("−", "-").replace("–", "-").replace("—", "-")
    parent_fm = parse_frontmatter(parent_text)

    parent_domain_dirs: dict = parent_fm.get("功能域定性方向", {})
    if not parent_domain_dirs:
        warnings.append(f"父类文件 {parent_path.name} 缺少 '功能域定性方向' 字段")
        return errors, warnings

    parent_default_path = parent_fm.get("默认病理类型", "")

    func_table = parse_md_table(text, "功能域配置")

    # ── P0.3-A: 域方向校验 ──
    domain_links: dict[str, list[tuple[str, list[float]]]] = {}
    for row in func_table:
        domain = row.get("域", "").strip()
        link_id = row.get("链路ID", "?").strip()
        m_str = row.get("m偏移(轻/中/重)", "").strip()
        if not domain:
            continue
        dnorm = _norm_domain(domain)
        if not m_str:
            domain_links.setdefault(dnorm, []).append((link_id, [0.0, 0.0, 0.0]))
            continue
        parts = m_str.split("/")
        try:
            m_vals = [float(p.strip()) if p.strip() else 0.0 for p in parts[:3]]
        except ValueError:
            m_vals = [0.0, 0.0, 0.0]
        while len(m_vals) < 3:
            m_vals.append(0.0)
        domain_links.setdefault(dnorm, []).append((link_id, m_vals))

    for dnorm_raw, parent_dir_val in parent_domain_dirs.items():
        dnorm = _norm_domain(dnorm_raw)  # 归一化父类 key（去掉"域"后缀）
        if parent_dir_val is None:  # YAML null → Python None
            continue

        child_links = domain_links.get(dnorm, [])
        net_sign, sev_used = _compute_net_direction(child_links)

        if parent_dir_val == "↓":
            if net_sign > 0:
                errors.append(
                    f"[父类方向矛盾] 域 '{dnorm}' 父类声明 ↓，"
                    f"但子类净方向为 ↑（{sev_used}度 sum>0）"
                )
            elif net_sign == 0 and child_links:
                warnings.append(
                    f"[父类方向] 域 '{dnorm}' 父类声明 ↓，"
                    f"但子类无任何非零 m 偏移"
                )

        elif parent_dir_val == "↑":
            if net_sign < 0:
                errors.append(
                    f"[父类方向矛盾] 域 '{dnorm}' 父类声明 ↑，"
                    f"但子类净方向为 ↓（{sev_used}度 sum<0）"
                )
            elif net_sign == 0 and child_links:
                warnings.append(
                    f"[父类方向] 域 '{dnorm}' 父类声明 ↑，"
                    f"但子类无任何非零 m 偏移"
                )

        elif parent_dir_val == "异常":
            has_abnormal = any(
                any(abs(v) >= 0.1 for v in m_vals) for _, m_vals in child_links
            )
            if not has_abnormal and child_links:
                warnings.append(
                    f"[父类方向] 域 '{dnorm}' 父类声明 异常，"
                    f"但子类无任何 |m|≥0.1 的链路"
                )
            elif not child_links:
                warnings.append(
                    f"[父类方向] 域 '{dnorm}' 父类声明 异常，"
                    f"但子类在该域无任何链路"
                )

    # ── P0.3-B: 病理类型矛盾检查 ──
    if parent_default_path:
        ppt_raw = parent_default_path.strip()
        has_or = "或" in ppt_raw
        has_plus = "+" in ppt_raw

        if has_or and has_plus:
            errors.append(
                f"[父类病理类型] 父类默认病理类型含 '+' 和 '或': {ppt_raw}"
                f"（不支持此组合语法）"
            )
        else:
            parent_types = set(
                t.strip() for t in ppt_raw.replace("或", "+").split("+") if t.strip()
            )

            if has_or:
                pass  # 父类含"或"：不限定
            elif has_plus:
                all_child_types: set[str] = set()
                for row in func_table:
                    pt = row.get("病理类型", "").strip()
                    if pt:
                        for t in pt.split("+"):
                            t = t.strip()
                            if t:
                                all_child_types.add(t)
                if not (parent_types & all_child_types):
                    errors.append(
                        f"[父类病理类型] 父类期望至少包含一种病理类型 "
                        f"{parent_types}，"
                        f"但子类未包含任何: {sorted(all_child_types) or '（无）'}"
                    )
            else:
                parent_type = list(parent_types)[0]
                for row in func_table:
                    link_id = row.get("链路ID", "?").strip()
                    pt_str = row.get("病理类型", "").strip()
                    if not pt_str:
                        continue
                    for ct in pt_str.split("+"):
                        ct = ct.strip()
                        if not ct or ct not in VALID_PATHOLOGY_TYPES:
                            continue
                        if (parent_type, ct) in _CONTRADICT:
                            errors.append(
                                f"[父类病理类型矛盾] 父类默认 '{parent_type}'，"
                                f"链路 '{link_id}' 声明 '{ct}'"
                                f"（信号强度轴对立）"
                            )

    return errors, warnings


def validate_parent_child_consistency(
    disease_dir: Path, parent_dir: Path
) -> tuple[list[str], list[str]]:
    """P0.3-C: global 父类归属交叉验证。"""
    errors: list[str] = []
    warnings: list[str] = []

    if not parent_dir.exists():
        warnings.append(f"父类目录不存在: {parent_dir}")
        return errors, warnings

    child_files = [
        p for p in sorted(disease_dir.glob("*.md")) if not p.name.startswith("_")
    ]
    parent_files = sorted(parent_dir.glob("*.md"))

    parent_to_children: dict[str, list[str]] = {}
    children_no_parent: list[str] = []

    for child in child_files:
        with open(child, encoding="utf-8") as f:
            child_text = f.read()
        fm = parse_frontmatter(child_text)
        parent = fm.get("父类", "")
        if parent:
            parent_to_children.setdefault(parent, []).append(child.name)
        else:
            children_no_parent.append(child.name)

    parent_names = {p.stem for p in parent_files}
    declared = set(parent_to_children.keys())

    for p in sorted(parent_names - declared):
        warnings.append(f"[交叉验证] 父类 '{p}' 无任何子类引用")

    for d in sorted(declared - parent_names):
        errors.append(f"[交叉验证] 子类引用父类 '{d}' 但父类文件不存在: _父类/{d}.md")

    if children_no_parent:
        warnings.append(
            f"[交叉验证] {len(children_no_parent)} 个文件未声明父类: "
            f"{', '.join(children_no_parent)}"
        )

    return errors, warnings


def validate_file(filepath: Path, registry_by_name: dict, parent_dir: Path | None = None) -> dict:
    """校验单个文件，返回结果字典。"""
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

    # ── ERROR checks ──
    result["errors"].extend(validate_link_ids(func_table, registry_by_name, str(filepath)))
    result["errors"].extend(validate_m_offsets(func_table, str(filepath)))
    result["errors"].extend(validate_jump_refs(jump_table, func_table, str(filepath)))

    # P0.1: 病理类型校验（遍历每条链路）
    for row in func_table:
        link_id = row.get("链路ID", "?").strip()
        path_str = row.get("病理类型", "")
        result["errors"].extend(validate_pathology_types(path_str, link_id))

    # ── WARNING checks ──
    result["warnings"].extend(validate_cgi_consistency(func_table, cgi_table, str(filepath)))
    result["warnings"].extend(validate_domain_count_constraints(func_table, cgi_table, str(filepath)))

    # P0.2: 掉落池校验（返回 tuple[errors, warnings]）
    drop_errors, drop_warnings = validate_drop_pool(drop_table, func_table, cgi_table)
    result["errors"].extend(drop_errors)
    result["warnings"].extend(drop_warnings)

    # P0.3-A+B: 父类继承校验（仅子类文件，父类文件自身跳过）
    if parent_dir and parent_dir.exists():
        is_parent_file = (
            filepath.parent == parent_dir or filepath.name.startswith("_")
        )
        if not is_parent_file:
            inh_errors, inh_warnings = validate_parent_inheritance(filepath, parent_dir)
            result["errors"].extend(inh_errors)
            result["warnings"].extend(inh_warnings)

    return result


def main():
    registry_by_name, registry_by_id = load_registry()

    parent_dir = ROOT / "实体/疾病目录/_父类"

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
        result = validate_file(fp, registry_by_name, parent_dir)

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

    # P0.3-C: global 父类归属交叉验证
    if parent_dir.exists():
        print(f"\n{'═' * 60}")
        print("交叉验证: 父类归属")
        cs_errors, cs_warnings = validate_parent_child_consistency(DISEASE_DIR, parent_dir)
        if cs_errors:
            print(f"  🔴 ERROR ({len(cs_errors)}):")
            for e in cs_errors:
                print(f"    ✗ {e}")
        if cs_warnings:
            print(f"  🟡 WARNING ({len(cs_warnings)}):")
            for w in cs_warnings:
                print(f"    ⚠ {w}")
        if not cs_errors and not cs_warnings:
            print(f"  ✅ 通过")
        total_errors += len(cs_errors)
        total_warnings += len(cs_warnings)

    print(f"\n{'═' * 60}")
    print(f"汇总: {len(files)} 文件, {total_errors} ERROR, {total_warnings} WARNING")
    if total_errors > 0:
        sys.exit(1)
    else:
        print("✓ 全部通过")


if __name__ == "__main__":
    main()
