# PLAN.md 实现预演 — Dry Run 断层报告

> 2026-08-01 | 按执行检查清单逐项模拟实现。不是读文本找不一致，是对每一项问"这行代码怎么写"。

---

## 方法说明

对 P0.0 → P0.3 逐项模拟实现。每个步骤写伪代码，暴露语义断层。

---

## P0.0 — parse_frontmatter() 升级

```python
import yaml

def parse_frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}
```

**输入**（父类模板 frontmatter）→ `yaml.safe_load()` 产出：
```python
{
    '父类ID': 'reward-system',
    '父类名': '奖赏系统障碍',
    '功能域定性方向': {
        '防御域': None,      # YAML null → Python None
        '奖赏域': '↓',        # Unicode → str
        '唤醒域': None,
        ...
        '整合域': '异常',
    },
    '默认病理类型': '解耦沉默 + 边界崩溃',
    '默认标签': [],
}
```

**输入**（子类 frontmatter）→ 产出：
```python
{
    '父类': '奖赏系统障碍',
    '疾病ID': 'mdd',
    'CGI-S范围': '3-7',
    '文献': 'ENIGMA MDD (Schmaal 2016), Guo et al. 2026',
}
```

✅ 类型兼容。`yaml.safe_load` 天然处理扁平和嵌套。`None` vs 字符串的区分由调用方处理。

✅ 无断层。可写。

---

## P0.1 — validate_pathology_types()

```python
VALID_TYPES = {'跨层短路', '过度耦合', '解耦沉默', '结构异常', '边界崩溃'}

def validate_pathology_types(path_str: str) -> list[str]:
    errors = []
    if not path_str or not path_str.strip():
        errors.append("病理类型为空")
        return errors
    parts = [p.strip() for p in path_str.split('+')]
    for p in parts:
        if '→' in p or ',' in p or '|' in p:
            errors.append(f"含非法分隔符 '{p}' (仅支持 +)")
        elif p not in VALID_TYPES:
            errors.append(f"'{p}' 不是合法病理类型")
    return errors
```

**断层 #1 — 调用位置的数据来源不明确**

此函数需要在 `validate_file()` 中遍历 func_table 的每一行并读取 `病理类型` 列。但 PLAN 没定义：

- 如果某行的"病理类型"列为空 → ERROR 还是 WARNING？
- 如果整个表格没有"病理类型"列（旧格式文件）→ ERROR 还是 WARNING？

**建议**：`病理类型` 列为**必填**，空值或缺失 → ERROR。

---

## P0.2 — validate_drop_pool() 扩展

**断层 #2 — 需要同时返回 ERROR 和 WARNING，破坏现有接口**

当前 `validate_drop_pool()` 返回 `list[str]`，全被当作 WARNING。但 P0.2 的格式错误（非数字、非法分隔符、非法 tier 标签）是 ERROR 级。

现有调用方 `validate_file()` 的接口是：
```python
result["errors"].extend(some_function(...))    # ERROR
result["warnings"].extend(some_other(...))      # WARNING
```

每个校验函数要么返回 errors 要么返回 warnings，不混合。但 P0.2 需要在一个函数内同时产出两类。需要改为 `→ tuple[list[str], list[str]]`，或拆成两个函数。

**断层 #3 — "该疾病实际 tier 数"的计算方法未定义**

PLAN："N = 该疾病 CGI-S 域扩展表中实际出现的 tier 数"。

CGI-S 域扩展表结构：
```
| 严重度 | 核心域 | 关联域 | 边缘域 |
| 轻度   | 奖赏,认知控制 | 0 | 0 |
| 中度   | - | +语言社会,+记忆 | 0 |
| 重度   | - | - | +防御 |
```

问题："实际出现的 tier 数"是：
- (a) 所有严重度行中，该 tier 列至少一次非空 → N=3（轻度有核心、中度有关联、重度有边缘）
- (b) 某严重度行下的 tier 数？如果是重度，核心域="-"，关联域="-"（继承），边缘域="+防御" → 只有 1 个 tier 活跃？

当前域数约束校验（`validate_domain_count_constraints`）已经有从 CGI-S 表推断 `core_domains/assoc_domains/peri_domains` 的逻辑。可以复用——tier "存在"当且仅当该 tier 在任一严重度有至少一个非空域。

**建议**：采用 (a)，并复用现有的 tier 推断逻辑。

---

## P0.3 — validate_parent_inheritance() 模拟实现

### P0.3 整体架构

```python
def validate_parent_inheritance(child_path: Path, parent_dir: Path) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    
    child_text = open(child_path).read()
    child_fm = parse_frontmatter(child_text)
    parent_name = child_fm.get('父类', '')
    
    if not parent_name:
        warnings.append("未声明父类")
        return errors, warnings
    
    parent_path = parent_dir / f"_{parent_name}.md"
    if not parent_path.exists():
        errors.append(f"父类文件不存在: {parent_path}")
        return errors, warnings
    
    parent_text = open(parent_path).read()
    parent_fm = parse_frontmatter(parent_text)
    
    errors.extend(_check_domain_direction(child_path, child_fm, parent_fm))
    errors.extend(_check_pathology_contradiction(child_path, child_fm, parent_fm))
    
    return errors, warnings
```

### 断层 #4 — 🔴 父类文件路径：P2 与 P0.3 矛盾

| 来源 | 路径 | 
|------|------|
| P2 产出列 | `实体/疾病目录/_父类/_奖赏系统障碍.md` |
| P0.3 step 2 | `实体/疾病目录/_<父类值>.md` |

两个不同路径。API 设计时只能选一个。

**建议**：统一为 `实体/疾病目录/_父类/<父类名>.md`。父类放在独立子目录中，与疾病文件隔离。P0.3 步骤描述和 P2 表格都更新到此路径。

连带修正：P0.3-C 的扫描范围 `实体/疾病目录/` 下非 `_` 前缀的 `.md` 文件 → 改为 `实体/疾病目录/*.md`（疾病文件在根目录），父类文件在 `_父类/` 子目录中，自然不匹配。

---

### P0.3-A — 域方向校验

```python
def _check_domain_direction(child_path, child_fm, parent_fm):
    errors = []
    parent_dirs = parent_fm.get('功能域定性方向', {})
    
    # Parse child's func_table
    child_text = open(child_path).read()
    func_table = parse_md_table(child_text, "功能域配置")
    
    # Group child links by domain
    child_m_by_domain = {}  # {domain_norm: [(link_id, m_mild, m_mod, m_sev), ...]}
    for row in func_table:
        domain = row.get('域', '').strip()
        m_str = row.get('m偏移(轻/中/重)', '').strip()
        if not domain or not m_str:
            continue
        dnorm = _norm_domain(domain)
        parts = [float(p) if p else 0.0 for p in m_str.split('/')[:3]]
        child_m_by_domain.setdefault(dnorm, []).append(parts)
    
    for dnorm, parent_dir_val in parent_dirs.items():
        if parent_dir_val is None:  # YAML null
            continue  # no constraint
        
        child_links = child_m_by_domain.get(dnorm, [])
        if not child_links:
            if parent_dir_val != None:
                # Parent says this domain is abnormal but child has no links in it
                # WARNING or skip? 
                pass  # ← GAP: what to do?
            continue
        
        # 🔴 GAP: compute "net m direction" — formula undefined
        net_dir = ???  # ← THIS IS THE BLOCKER
```

**断层 #5 — 🔴 "净 m 方向"计算公式未定义（最关键的单点阻塞）**

PLAN 定义了四种方向语义的校验行为，但**没定义如何从多条链路的多级 m 偏移计算出一个"净方向"**。

候选公式（均未在 PLAN 中）：

| 方案 | 公式 | 问题 |
|------|------|------|
| A. 符号和 | `sign(Σ all m values)` | 正负抵消可能导致净零 |
| B. 绝对值主导 | `sign(max |m| 的符号)` | 如果一条 +0.6 和一条 -0.4，净方向 = ↑——对等抵消不适用 |
| C. 多数符号 | `sign(count(+) - count(-))` | 小偏移和大偏移权重相同 |
| D. per-severity | 轻中重三级分别判断，任一级违反 → ERROR | 三级可能互相矛盾 |

**建议**（基于 PLAN 意图推断——这是对"净"的最自然解释）：

> 净方向 = 该域所有链路在 CGI-S 最高严重度下的 m 值加权方向。
> - 取重度 m 值（如重度为 0 则退到中度，再退到轻度）
> - 如该域有一条链路重度 m = +0.5 和一条重度 m = -0.3，则净 = +0.2 → ↑
> - 如该域所有链路 m = 0 → 净 = 0 → 特殊处理

但这需要明确选择并写入 PLAN。

**断层 #6 — `异常` 的校验过弱**

PLAN："父类声明`异常` → 子类该域至少有一条非零 m 链路（方向不限）"。

如果 father 的 `整合域: 异常`，子类在整合域写了一条 `某链路: m偏移 0/+0.01/0` ——轻度和中度都是 0，只有重度有一丁点信号。这在生物学上不合理（一个真正异常的域应该有实质性的偏移），但规则允许。

**建议**：`异常` 增加阈值——该域至少有一条链路的任一严重度 |m| ≥ 0.1。

---

### P0.3-B — 病理类型矛盾检查

```python
CONTRADICTION_MATRIX = {
    ('解耦沉默', '过度耦合'): True,  # signal weakening vs signal too strong
    ('过度耦合', '解耦沉默'): True,
    # 🔴 GAP: other 4×4 pairs are undefined
}

def _check_pathology_contradiction(child_path, child_fm, parent_fm):
    errors = []
    parent_default = parent_fm.get('默认病理类型', '')
    
    # Parse parent semantics
    if '或' in parent_default:
        return errors  # parent says "X 或 Y", no contradiction possible
    
    # Split parent types
    parent_types = set(t.strip() for t in parent_default.replace('或', '+').split('+'))
    
    child_text = open(child_path).read()
    func_table = parse_md_table(child_text, "功能域配置")
    
    for row in func_table:
        path_str = row.get('病理类型', '').strip()
        if not path_str:
            continue
        child_types = set(t.strip() for t in path_str.split('+'))
        
        # Check: does child have any type that contradicts parent?
        for pt in parent_types:
            for ct in child_types:
                if ct not in VALID_TYPES or pt not in VALID_TYPES:
                    continue  # invalid types already caught by P0.1
                if (pt, ct) in CONTRADICTION_MATRIX:
                    errors.append(f"病理类型矛盾: 父类默认 '{pt}', 链路 '{row.get('链路ID','?')}' 声明 '{ct}'")
    
    # Check: if parent has "+" (expects coexistence), child must have at least one
    if '+' in parent_default and '或' not in parent_default:
        # Parent expects "X + Y" → child should have at least one of them
        all_child_types = set()
        for row in func_table:
            for t in row.get('病理类型', '').split('+'):
                t = t.strip()
                if t:
                    all_child_types.add(t)
        if not (parent_types & all_child_types):
            errors.append(f"父类期望至少包含一种病理类型 {parent_types}，但子类未包含任何")  # ← GAP: PLAN says WARNING, not ERROR?
    
    return errors
```

**断层 #7 — 🔴 矛盾矩阵只定义了 1 对，剩余 4×4 对未定义**

| a \ b | 跨层短路 | 过度耦合 | 解耦沉默 | 结构异常 | 边界崩溃 |
|-------|:---:|:---:|:---:|:---:|:---:|
| 跨层短路 | — | ? | ? | ? | ? |
| 过度耦合 | ? | — | ✅矛盾 | ? | ? |
| 解耦沉默 | ? | ✅矛盾 | — | ? | ? |
| 结构异常 | ? | ? | ? | — | ? |
| 边界崩溃 | ? | ? | ? | ? | — |

PLAN 只定义了 `解耦沉默 ↔ 过度耦合` 矛盾（"信号减弱 vs 信号过强"）。其他组合未定义。

**建议**：空白格 = 不矛盾（不同机制可以共存）。在父类模板中加一行或写死一个完整的 5×5 矩阵。

**断层 #8 — `或` 和 `+` 同时出现时解析逻辑有歧义**

父类 `_认知控制障碍.md`：`过度耦合 或 解耦沉默`。没有 `+`。但如果未来有 `解耦沉默 + 边界崩溃 或 过度耦合`，解析器会困惑。

当前不需要处理这个边界情况（全量 6 个父类中不出现），但应在 P0.3-B 开头加一个 check：如果同时包含 `+` 和 `或` → 报错（不支持此语法）。

---

### P0.3-C — 交叉验证

**断层 #9 — 🔴 架构不匹配：per-file validator 无法做全局交叉验证**

PLAN 将 P0.3-C 作为 `validate_parent_inheritance()` 的内部步骤，但交叉验证需要：

```python
# This CANNOT be inside validate_file() or validate_parent_inheritance()
# because it needs ALL files at once

all_child_files = [p for p in disease_dir.glob("*.md") if not p.name.startswith("_")]
all_parent_files = [p for p in parent_dir.glob("*.md")]

child_parent_map = {}
for child in all_child_files:
    fm = parse_frontmatter(open(child).read())
    parent = fm.get('父类', '')
    child_parent_map.setdefault(parent, []).append(child.name)

parent_names = {p.stem.lstrip('_') for p in all_parent_files}
child_declared_parents = set(child_parent_map.keys())

parents_without_children = parent_names - child_declared_parents  # WARNING
children_without_parent = child_declared_parents - parent_names   # ERROR
children_missing_parent_file = [c for c in child_declared_parents if c not in parent_names]  # ERROR
```

这必须是独立函数 `validate_parent_child_consistency(all_files, parent_dir)`，在 `main()` 中**所有文件单文件校验完成后**调用一次。

**建议**：P0.3 拆分为两个函数：
- `validate_parent_inheritance(child_path, parent_dir)` — P0.3-A + P0.3-B（per-file）
- `validate_parent_child_consistency(all_child_paths, parent_dir)` — P0.3-C（global）

---

## P0 集成 — validate_file() 重构

**断层 #10 — 🔴 `validate_file()` 需要参数重构**

当前签名：
```python
def validate_file(filepath: Path, registry_by_name: dict) -> dict:
```

新增 P0.3 调用后，需要 `parent_dir` 参数：
```python
def validate_file(filepath: Path, registry_by_name: dict, parent_dir: Path) -> dict:
```

且 `parent_dir` 只在子类文件校验 P0.3 时需要——如果 filepath 本身就是父类文件（`_` 前缀），应跳过 P0.3。

还有 P0.2 需要 `cgi_table`（已在函数内解析）——不需额外参数。

**断层 #11 — P0.1 调用位置**

在 `validate_file()` 中，func_table 已解析。对每行调用 `validate_pathology_types(row['病理类型'])` 并将结果加入 `result["errors"]`。

但如果某行没有 `病理类型` 键（表头不同），`row.get('病理类型', '')` 返回空字符串 → P0.1 报"病理类型为空"。这是 ERROR。意味着所有疾病文件的 func_table 必须有此列。

✅ 可以接受。

---

## 总结

| # | 严重度 | 断层 | 阻塞 |
|:---:|:---:|------|:---:|
| 5 | 🔴 | "净 m 方向"计算公式未定义 | **P0.3-A 完全无法实现** |
| 4 | 🔴 | 父类文件路径 P2 vs P0.3 矛盾 | P0.3 找不到父类文件 |
| 9 | 🔴 | P0.3-C 架构不匹配 | 交叉验证放不进 per-file 函数 |
| 2 | 🟡 | P0.2 需同时返回 ERROR + WARNING | 需要改接口设计 |
| 3 | 🟡 | "实际 tier 数"计算未定义 | 实现到 P0.2 范围检查时卡住 |
| 7 | 🟡 | 矛盾矩阵只定义 1 对 | P0.3-B 大部分病理类型对比无规则 |
| 6 | 🟡 | `异常` 阈值缺失 | 可以实现但语义偏弱 |
| 1 | 🟢 | 病理类型列可选 vs 必填 | 选必填即可 |
| 10 | 🟢 | validate_file() 需加 parent_dir 参数 | API 变更 |
| 8 | 🟢 | `或`+`+` 同时出现的边界 | 当前不触发 |
| 11 | 🟢 | P0.1 调用位置 | 直接加到 validate_file 主循环 |

**11 个断层，3 个阻塞代码编写（#4, #5, #9），4 个需设计决策（#2, #3, #6, #7），4 个可在编码时自然解决。**

---

*创建: 2026-08-01*
*关联: [PLAN.md](PLAN.md), [validate_disease.py](../../tools/validate_disease.py)*
