#!/usr/bin/env python3
"""
疾病md文件校验器 v2（Grilling #88 重映射后）

解析 实体/疾病目录/*.md，校验：
- 病理边引用表 edge_id ∈ pathology_edges.json（且 disease_id 匹配）
- pathology_edges.json 自身：端点 ∈ tripartite graph_nodes、禁镜像实体、
  三体边命中（非「病理新增」时）、|m| ≤ 0.6、Δ ∈ [−1,+1]、相位键仅限 bipolar-I/II
- 行为覆盖/非线性跳变引用的边 ID 合法性
- 组件掉落池边 ID 覆盖 + 权重格式
- 父类继承（病理类型矛盾）+ 全局父类归属交叉验证

旧版（2026-08-03）查 link_registry.json（⚠️ 已废弃 2026-08-07 #26），已由本版替代。

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
PARENT_DIR = DISEASE_DIR / "_父类"
TRI = ROOT / "data/connectivity/tripartite_model.json"
PE = ROOT / "data/connectivity/pathology_edges.json"

MIRROR_NODES = {"LocusCoeruleusRight", "SubstantiaNigraParsCompactaRight"}
VALID_PATHOLOGY_TYPES = {"跨层短路", "过度耦合", "解耦沉默", "结构异常"}
BIPOLAR_IDS = {"bipolar-I", "bipolar-II"}
M_MAX = 0.6


def load_data():
    """加载 tripartite 模型 + pathology_edges，返回 (nodes, edges, pathology)"""
    with open(TRI, encoding="utf-8") as f:
        tri = json.load(f)
    nodes = set(tri["graph_nodes"].keys())
    tri_edges = set()
    for k in ["cstc", "corticocortical", "brainstem", "privileged_pathways"]:
        for e in tri[k]:
            tri_edges.add((e["source"], e["target"]))
            tri_edges.add((e["target"], e["source"]))

    with open(PE, encoding="utf-8") as f:
        pe = json.load(f)
    path_edges = {e["edge_id"]: e for e in pe["edges"]}
    return nodes, tri_edges, path_edges, pe


def parse_frontmatter(text: str) -> dict:
    """提取 YAML frontmatter (--- ... ---)"""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def parse_md_table(text: str, section_header: str) -> list[dict]:
    """提取指定 ## 标题下的第一个 markdown 表格"""
    pattern = rf"^##\s+{re.escape(section_header)}\s*\n"
    m = re.search(pattern, text, re.MULTILINE)
    if not m:
        return []
    section_start = m.end()
    next_section = re.search(r"^##\s+", text[section_start:], re.MULTILINE)
    section_end = section_start + next_section.start() if next_section else len(text)
    section_text = text[section_start:section_end]

    lines = section_text.split("\n")
    header_idx = None
    sep_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and not line.strip().startswith("|--"):
            if header_idx is None:
                header_idx = i
        if header_idx is not None and sep_idx is None and re.match(r"^\|[\s\-:|]+\|$", line.strip()):
            sep_idx = i
            break

    if header_idx is None or sep_idx is None:
        return []

    headers = [h.strip() for h in lines[header_idx].split("|")[1:-1]]
    rows = []
    for line in lines[sep_idx + 1:]:
        line = line.strip()
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


# ─── pathology_edges.json 自身校验 ───

def validate_pe_file(pe: dict) -> list[str]:
    """校验 pathology_edges.json：端点/镜像/三体边命中/|m|/Δ/相位键约束"""
    errors = []
    nodes, tri_edges, _, _ = load_data()
    seen_ids = set()
    for e in pe["edges"]:
        eid = e.get("edge_id", "")
        if eid in seen_ids:
            errors.append(f"[PE] 重复 edge_id: {eid}")
        seen_ids.add(eid)

        # Q0.4 断言：edge_id 前缀必须 == disease_id
        did = e.get("disease_id", "")
        eid_prefix = eid.rsplit("_e", 1)[0] if "_e" in eid else eid
        if eid_prefix != did:
            errors.append(f"[PE:{eid}] edge_id 前缀 '{eid_prefix}' ≠ disease_id '{did}'（Q0.4 全局主键约束）")

        src, tgt = e.get("source"), e.get("target")
        if src not in nodes:
            errors.append(f"[PE:{eid}] 端点 {src} 不在 tripartite graph_nodes")
        if tgt not in nodes:
            errors.append(f"[PE:{eid}] 端点 {tgt} 不在 tripartite graph_nodes")
        if src in MIRROR_NODES or tgt in MIRROR_NODES:
            errors.append(f"[PE:{eid}] 引用镜像实体（{src}/{tgt} 禁引）")

        etype = e.get("edge_type", "")
        if etype != "病理新增" and (src, tgt) not in tri_edges:
            errors.append(f"[PE:{eid}] 声明 {etype} 但三体图无 {src}→{tgt}")

        # m_offset: 数组或相位键
        mo = e.get("m_offset")
        did = e.get("disease_id", "")
        if isinstance(mo, dict):
            if did not in BIPOLAR_IDS:
                errors.append(f"[PE:{eid}] 相位键 m_offset 仅限 bipolar-I/II（当前 {did}）")
            for phase, vals in mo.items():
                if phase not in ("mania", "depression"):
                    errors.append(f"[PE:{eid}] 相位键非法: {phase}")
                for v in vals:
                    if v is not None and abs(v) > M_MAX:
                        errors.append(f"[PE:{eid}] {phase} |m|={v} > {M_MAX}")
        elif isinstance(mo, list):
            for v in mo:
                if v is not None and abs(v) > M_MAX:
                    errors.append(f"[PE:{eid}] |m|={v} > {M_MAX}")
        else:
            errors.append(f"[PE:{eid}] m_offset 格式非法: {mo!r}")

        d = e.get("laterality_delta", 0)
        if d is not None and abs(d) > 1.0:
            errors.append(f"[PE:{eid}] laterality_delta {d} 超出 [−1,+1]")

        pt = e.get("pathology_type", "")
        if pt not in VALID_PATHOLOGY_TYPES and pt != "双向振荡":
            errors.append(f"[PE:{eid}] 病理类型 '{pt}' 非法")
    return errors


# ─── 疾病文件校验 ───

def parse_m_triple(m_str: str):
    """解析 m 三档字符串（含 Unicode −、/ 分隔、— 占位、相位键 +X/−Y）→ [v1,v2,v3] 或相位 dict"""
    m_str = m_str.strip().replace("**", "")
    # 相位键格式: +0.3/−0.3, +0.5/−0.5, +0.6/−0.5（逗号分隔的 "X/Y" 对，且 X 为正、Y 可为负）
    # 严格判据：含逗号且每段含 "/" 且每对的第一值带正号或为纯正数
    pairs = [p.strip() for p in m_str.split(",")]
    if len(pairs) >= 2 and all("/" in p for p in pairs):
        mania, dep = [], []
        ok = True
        for pair in pairs:
            parts = pair.split("/")
            if len(parts) != 2:
                ok = False
                break
            m, d = parts
            try:
                mv = float(m.replace("−", "-"))
                dv = float(d.replace("−", "-"))
            except ValueError:
                ok = False
                break
            mania.append(mv)
            dep.append(dv)
        if ok:
            return {"mania": mania, "depression": dep}
    # 普通三档: +0.2/+0.4/+0.6 或 0/+0.2/—
    vals = []
    for part in m_str.split("/"):
        part = part.strip().replace("−", "-")
        if part in ("—", "-", ""):
            vals.append(None)
        else:
            try:
                vals.append(float(part))
            except ValueError:
                vals.append(None)
    return vals


def validate_disease_edges(table: list[dict], path_edges: dict, disease_id: str) -> list[str]:
    """病理边引用表：edge_id ∈ pathology_edges 且 disease_id 匹配"""
    errors = []
    for row in table:
        eid = row.get("病理边ID", "").strip().replace("**", "")
        if not eid:
            continue
        if eid not in path_edges:
            errors.append(f"[{eid}] 病理边ID不在 pathology_edges.json")
            continue
        if path_edges[eid].get("disease_id") != disease_id:
            errors.append(f"[{eid}] 归属疾病 {path_edges[eid].get('disease_id')} ≠ 本文件 {disease_id}")
        # m 偏移与 JSON 一致性（宽松：文件允许 — 占位）
        m_cell = row.get("m偏移(轻/中/重)", "").strip()
        if m_cell:
            parsed = parse_m_triple(m_cell)
            json_mo = path_edges[eid].get("m_offset")
            if isinstance(parsed, dict) and isinstance(json_mo, dict):
                for ph in ("mania", "depression"):
                    jv = json_mo.get(ph, [])
                    for i, pv in enumerate(parsed.get(ph, [])):
                        if i < len(jv) and pv is not None and jv[i] is not None and abs(pv - jv[i]) > 1e-6:
                            errors.append(f"[{eid}] {ph} 第{i+1}档 m 不一致: 文件 {pv} vs JSON {jv[i]}")
            elif isinstance(parsed, list) and isinstance(json_mo, list):
                for i, pv in enumerate(parsed):
                    if i < len(json_mo) and pv is not None and json_mo[i] is not None and abs(pv - json_mo[i]) > 1e-6:
                        errors.append(f"[{eid}] 第{i+1}档 m 不一致: 文件 {pv} vs JSON {json_mo[i]}")
    return errors


def extract_edge_ids_from_text(text: str) -> set[str]:
    """从全文提取所有 <disease>_eNN 形式的边 ID"""
    return set(re.findall(r"[a-z0-9\-]+_e\d{2}", text))


def validate_hook_refs(text: str, path_edges: dict) -> list[str]:
    """行为覆盖/非线性跳变/掉落池引用的边 ID 必须存在于 pathology_edges"""
    errors = []
    for eid in sorted(extract_edge_ids_from_text(text)):
        if eid not in path_edges:
            errors.append(f"[{eid}] 正文引用边 ID 不在 pathology_edges.json")
    return errors


def validate_drop_pool(drop_table: list[dict], path_edges: dict, disease_id: str) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    drop_ids: set[str] = set()
    weight_re = re.compile(r"^(\d+)\s*[（(](核心|关联|边缘)[)）]$")
    max_w = 0
    for row in drop_table:
        ids_str = row.get("病理边ID", "").strip()
        if ids_str:
            # 去除 （+ ...） 注释段
            ids_str = re.sub(r"[（(][+]?.*?[)）]", "", ids_str)
            for item in re.split(r"[,\s]+", ids_str):
                item = item.strip()
                if not item:
                    continue
                # 短名 eNN 补齐疾病前缀
                if re.match(r"^e\d{2}$", item):
                    item = f"{disease_id}_{item}"
                elif item.startswith(f"{disease_id}_"):
                    pass
                else:
                    errors.append(f"[掉落池] 边 ID 格式非法: '{item}'")
                    continue
                drop_ids.add(item)
        w_str = row.get("权重", "").strip()
        if w_str:
            m = weight_re.match(w_str)
            if not m:
                errors.append(f"组件掉落池 权重格式错误: '{w_str}' — 应为 'N(核心|关联|边缘)'")
            else:
                max_w = max(max_w, int(m.group(1)))
    if max_w > 3:
        warnings.append(f"组件掉落池 最大权重 {max_w} 超过 3 档上限")
    for eid in sorted(drop_ids):
        if eid not in path_edges:
            errors.append(f"[掉落池] 边 {eid} 不在 pathology_edges.json")
    return errors, warnings


# ─── 父类校验（沿用 v1 逻辑，适配 病理类型 无 边界崩溃） ───

_CONTRADICT = {("解耦沉默", "过度耦合"), ("过度耦合", "解耦沉默")}


def validate_parent_inheritance(filepath: Path) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    child_fm = parse_frontmatter(text)
    parent_name = child_fm.get("父类", "")
    if not parent_name:
        warnings.append("未声明父类")
        return errors, warnings

    parent_path = PARENT_DIR / f"{parent_name}.md"
    if not parent_path.exists():
        # 兼容：父类名可能与文件名不同（如 躯体症状障碍 → 躯体症状.md）
        candidates = list(PARENT_DIR.glob("*.md"))
        match = None
        for c in candidates:
            with open(c, encoding="utf-8") as f:
                fm = parse_frontmatter(f.read())
            if fm.get("父类名") == parent_name or c.stem == parent_name:
                match = c
                break
        if match:
            parent_path = match
        else:
            errors.append(f"父类文件不存在: {parent_name}")
            return errors, warnings

    with open(parent_path, encoding="utf-8") as f:
        parent_fm = parse_frontmatter(f.read())

    parent_default = parent_fm.get("默认病理类型", "")
    func_table = parse_md_table(text, "病理边引用")
    if parent_default and "或" not in parent_default and "+" not in parent_default:
        parent_type = parent_default.strip().replace("（ASPD/BPD 主）", "").strip()
        if parent_type in VALID_PATHOLOGY_TYPES:
            # 统计子类各类型数量，父类默认类型 = 主导类型（非全边同类型约束）
            type_count = {}
            for row in func_table:
                pt = row.get("病理类型", "").strip().replace("**", "")
                base = re.sub(r"（.*?）", "", pt).strip()
                if base in VALID_PATHOLOGY_TYPES or base == "双向振荡":
                    type_count[base] = type_count.get(base, 0) + 1
            if type_count:
                dominant = max(type_count, key=type_count.get)
                if (parent_type, dominant) in _CONTRADICT:
                    warnings.append(
                        f"[父类主导类型] 父类默认 '{parent_type}' 与子类主导类型 '{dominant}' 对立"
                        f"（{type_count}）——父类默认为主导类型，非全边约束；若属设计意图可忽略"
                    )
    return errors, warnings


def validate_parent_child_consistency() -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    child_files = [p for p in sorted(DISEASE_DIR.glob("*.md")) if not p.name.startswith("_")]
    parent_files = sorted(PARENT_DIR.glob("*.md"))
    parent_to_children: dict[str, list[str]] = {}
    for child in child_files:
        with open(child, encoding="utf-8") as f:
            fm = parse_frontmatter(f.read())
        parent = fm.get("父类", "")
        if parent:
            parent_to_children.setdefault(parent, []).append(child.name)

    # 父类名集合 = 文件名 stem ∪ frontmatter 父类名（兼容 躯体症状.md vs 声明"躯体症状障碍"）
    parent_names = set()
    for p in parent_files:
        parent_names.add(p.stem)
        with open(p, encoding="utf-8") as f:
            fm = parse_frontmatter(f.read())
        if fm.get("父类名"):
            parent_names.add(fm["父类名"])
    declared = set(parent_to_children.keys())
    for p in sorted(parent_names - declared):
        # 该文件若存在同名父类名被引用（如 躯体症状.md 被声明为"躯体症状障碍"），不算无子类
        covered = False
        for pf in parent_files:
            with open(pf, encoding="utf-8") as f:
                fm = parse_frontmatter(f.read())
            if fm.get("父类名") in declared and pf.stem == p:
                covered = True
                break
        if not covered:
            warnings.append(f"[交叉验证] 父类文件 '{p}' 无任何子类声明")
    for d in sorted(declared - parent_names):
        # 检查父类名匹配
        found = False
        for p in parent_files:
            with open(p, encoding="utf-8") as f:
                fm = parse_frontmatter(f.read())
            if fm.get("父类名") == d:
                found = True
                break
        if not found:
            errors.append(f"[交叉验证] 子类引用父类 '{d}' 但无对应父类文件")
    return errors, warnings


def validate_file(filepath: Path, nodes, tri_edges, path_edges) -> dict:
    result = {"filepath": filepath, "errors": [], "warnings": [], "edge_count": 0}
    with open(filepath, encoding="utf-8") as f:
        text = f.read()
    fm = parse_frontmatter(text)
    disease_id = fm.get("疾病ID", "")

    edge_table = parse_md_table(text, "病理边引用")
    jump_table = parse_md_table(text, "非线性跳变")
    drop_table = parse_md_table(text, "组件掉落池")
    result["edge_count"] = len(edge_table)

    result["errors"].extend(validate_disease_edges(edge_table, path_edges, disease_id))
    result["errors"].extend(validate_hook_refs(text, path_edges))
    d_errors, d_warnings = validate_drop_pool(drop_table, path_edges, disease_id)
    result["errors"].extend(d_errors)
    result["warnings"].extend(d_warnings)

    # 父类继承（仅子类）
    if filepath.parent != PARENT_DIR:
        inh_errors, inh_warnings = validate_parent_inheritance(filepath)
        result["errors"].extend(inh_errors)
        result["warnings"].extend(inh_warnings)

    return result


def main():
    nodes, tri_edges, path_edges, pe = load_data()

    # 1) pathology_edges.json 自身校验
    pe_errors = validate_pe_file(pe)
    print(f"{'═' * 60}")
    print(f"校验: data/connectivity/pathology_edges.json ({len(pe['edges'])} 条边)")
    if pe_errors:
        print(f"  🔴 ERROR ({len(pe_errors)}):")
        for e in pe_errors:
            print(f"    ✗ {e}")
    else:
        print(f"  ✅ 0 ERROR")
    total_errors = len(pe_errors)
    total_warnings = 0

    # 2) 疾病文件校验
    if len(sys.argv) > 1:
        files = [Path(p) for p in sys.argv[1:]]
    else:
        files = sorted(DISEASE_DIR.glob("*.md"))

    for fp in files:
        if fp.name.startswith("_"):
            continue
        result = validate_file(fp, nodes, tri_edges, path_edges)
        print(f"\n{'═' * 60}")
        print(f"校验: {fp.name}（{result['edge_count']} 条病理边）")
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
        total_errors += len(result["errors"])
        total_warnings += len(result["warnings"])

    # 3) 父类归属交叉验证
    cs_errors, cs_warnings = validate_parent_child_consistency()
    print(f"\n{'═' * 60}")
    print("交叉验证: 父类归属")
    if cs_errors:
        for e in cs_errors:
            print(f"  🔴 ERROR: {e}")
    if cs_warnings:
        for w in cs_warnings:
            print(f"  🟡 WARNING: {w}")
    if not cs_errors and not cs_warnings:
        print("  ✅ 通过")
    total_errors += len(cs_errors)
    total_warnings += len(cs_warnings)

    print(f"\n{'═' * 60}")
    print(f"汇总: {len(pe['edges'])} 条病理边 + {len([f for f in files if not f.name.startswith('_')])} 疾病文件, {total_errors} ERROR, {total_warnings} WARNING")
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()
