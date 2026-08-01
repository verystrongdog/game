# 疾病目录全量填充 — 任务规划

> 2026-08-01 | Grilling #15 — 疾病系统独立建模 子任务
> 依赖: 疾病系统独立建模 ✅ / 364链路 ✅ / 13功能域 ✅（定义: `实体/角色与面具.md` §8.3, `docs/决策树.md` :103-116）
> Dry-run: [DRY-RUN.md](DRY-RUN.md) — 11 断层全部修正

---

## 阶段总览

| 阶段 | 内容 | 预估工作量 | 产出 |
|------|------|:---:|------|
| P0 | 校验基础设施（解析器升级 + 脚本扩展） | 5 项 | `tools/validate_disease.py` |
| P1 | 文献搜索 | 11 条目（10 疾病 + 1 补充） | 更新 `参考/文献/疾病-脑区链路映射-文献数据源.md` |
| P2 | 父类模板 + 已有文件迁移 | 6 个父类文件 | `实体/疾病目录/_父类/` |
| P3 | 疾病定量填充 | 18 个新文件（+ 偏执型精分 = 19 总） | `实体/疾病目录/*.md` |
| P4 | 校验 + 角色系统解耦 + 清扫 | validate + 角色文档修改 + 228残留清理 | 关闭 issue #14 |

---

## P0 — 校验基础设施

> 在填充工作开始前，补齐解析能力和校验缺口。P0.3 因架构原因拆分为 per-file（A+B）和 global（C）两个函数。

### P0.0 — 升级 parse_frontmatter() 为 YAML 解析

**当前**：`parse_frontmatter()` 使用扁平 `key.partition(":")` 解析，`validate_file()` :403 调用但返回值从未被消费（死代码）。

**升级**：安装 PyYAML（`pip install pyyaml`；非标准库，当前环境已安装 5.4.1），从 `---` 分隔块中提取内容后 `yaml.safe_load()`。

**返回值类型变更**：`dict[str, str]` → `dict[str, Any]`。嵌套键（如 `功能域定性方向`）解析为 dict。YAML `null` → Python `None`。

```python
import yaml

def parse_frontmatter(text: str) -> dict[str, Any]:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}
```

---

### P0.1 — 病理类型校验

新增函数 `validate_pathology_types(pathology_str: str) -> list[str]`：

- 按 ` + ` split 后逐项检查是否为 5 种合法值之一
- `→` / `,` / `|` 等非 ` + ` 分隔符 → ERROR
- 空值 → ERROR
- 错误级别：ERROR

**调用位置**：在 `validate_file()` 主循环中，遍历 `func_table` 每一行，取 `病理类型` 列（**必填列**——缺失或空值 → ERROR），调用此函数，结果 `extend` 到 `result["errors"]`。

---

### P0.2 — 掉落池权重校验

扩展现有 `validate_drop_pool()`。**返回值变更**：`list[str]` → `tuple[list[str], list[str]]`（errors, warnings），与 `validate_file()` 调用方式一致。

**格式校验（ERROR）**：
- 权重值格式：`N (tier标签)`，正则 `r'^(\d+)\s*\((核心|关联|边缘)\)$'`
- 不匹配 → ERROR（含非数字、非整数、非法 tier 标签、缺少括号等）

**范围校验（WARNING）**：
- 权重值 N 不应超过该疾病 CGI-S 表中"实际出现的最大 tier 索引"
- "实际出现"定义：在 CGI-S 域扩展表的任一严重度行中，该 tier 列（核心域/关联域/边缘域）有至少一个非空域名（不是 "0" / "-" / ""）
- 计算方式：复用 `validate_domain_count_constraints()` 中对 `core_domains / assoc_domains / peri_domains` 的推断逻辑——tier 索引 = 核心域/关联域/边缘域分别对应 tier 1/2/3。一个 tier "存在"当该 tier 的域集合非空
- 例：某疾病只有核心域 + 关联域（边缘域全为 "0"）→ 权重值 > 2 → WARNING

**调用位置**：在 `validate_file()` 中调用，errors → `result["errors"]`，warnings → `result["warnings"]`。

---

### P0.3-A+B — 父类继承校验（per-file）

新增函数 `validate_parent_inheritance(filepath: Path, parent_dir: Path) -> tuple[list[str], list[str]]`：

**查找规则**：子类 frontmatter `父类:` 值 = 父类 `父类名:` 值。父类文件路径 = `parent_dir / f"{父类值}.md"`（parent_dir = `实体/疾病目录/_父类/`）。

#### A. 域方向校验

1. 从子类 frontmatter 读取 `父类:` → 加载父类文件 → 获取 `功能域定性方向:` dict
2. 按域汇总子类每条链路的 m 偏移（轻/中/重三级）
3. 对父类声明的每个非 `null` 域，计算该域的**净 m 方向**（定义见下），与父类方向比对
4. 违反 → ERROR

**净 m 方向计算公式**：

```
对于域 D，取"最高有效严重度"：在 {重, 中, 轻} 中，第一个满足"该域至少有一条链路在此严重度的 m ≠ 0"的级别。
在该严重度下，对该域所有链路的 m 值求和。
净方向 = sign(sum)。sum = 0 → 净方向 = 0（既非正也非负）。
```

**方向语义与校验行为**：

| 父类值 | 校验行为 |
|:---:|------|
| `↓` | 净方向必须 < 0（sum < 0）。若净方向 = 0 → WARNING（域声明为 ↓ 但无负偏移） |
| `↑` | 净方向必须 > 0（sum > 0）。若净方向 = 0 → WARNING |
| `异常` | 该域至少有一条链路在任一严重度满足 \|m\| ≥ 0.1。不满足 → WARNING |
| `None`（YAML null） | 无约束 |

#### B. 病理类型矛盾检查

5. 遍历子类每条链路的病理类型（`validate_pathology_types()` split 后的列表）
6. 与父类 `默认病理类型` 比对：

| 父类格式 | 检查逻辑 |
|---------|---------|
| 单一类型（如 `解耦沉默`） | 子类任一条链路的病理类型不得与该类型矛盾 |
| `X 或 Y` | 父类不限定，无矛盾 |
| `X + Y` | 子类所有链路的病理类型集合中，至少包含 {X, Y} 之一（否则 ERROR） |
| 同时含 `+` 和 `或` | 语法错误 → ERROR（P0.3-B 开头拦截，当前 6 个父类均不触发） |

**矛盾矩阵**（完整 5×5）：

矛盾仅定义在**信号强度轴**上：`解耦沉默`（信号减弱） ↔ `过度耦合`（信号过强）。其他三种（跨层短路、结构异常、边界崩溃）是路径/架构层面的异常，与信号强度异常机制不同，可与任何类型共存。

| a \ b | 跨层短路 | 过度耦合 | 解耦沉默 | 结构异常 | 边界崩溃 |
|-------|:---:|:---:|:---:|:---:|:---:|
| 跨层短路 | — | 不矛盾 | 不矛盾 | 不矛盾 | 不矛盾 |
| 过度耦合 | 不矛盾 | — | **矛盾** | 不矛盾 | 不矛盾 |
| 解耦沉默 | 不矛盾 | **矛盾** | — | 不矛盾 | 不矛盾 |
| 结构异常 | 不矛盾 | 不矛盾 | 不矛盾 | — | 不矛盾 |
| 边界崩溃 | 不矛盾 | 不矛盾 | 不矛盾 | 不矛盾 | — |

**调用位置**：在 `validate_file()` 中调用。如果 filepath 本身是父类文件（位于 parent_dir 内或以 `_` 开头），跳过 P0.3-A+B。

**`validate_file()` 签名变更**：
```python
# Before:
def validate_file(filepath: Path, registry_by_name: dict) -> dict:

# After:
def validate_file(filepath: Path, registry_by_name: dict, parent_dir: Path | None = None) -> dict:
```
`parent_dir` 默认 `ROOT / "实体/疾病目录/_父类"`。`main()` 在单文件模式下显式传入，批量模式下使用默认值。

---

### P0.3-C — 父类归属交叉验证（global）

新增独立函数 `validate_parent_child_consistency(disease_dir: Path, parent_dir: Path) -> tuple[list[str], list[str]]`：

```python
def validate_parent_child_consistency(disease_dir, parent_dir):
    errors, warnings = [], []
    
    # 扫描子类: 所有非 _ 前缀的 .md 文件(父类在 _父类/ 子目录中,自然不匹配此 glob)
    child_files = [p for p in disease_dir.glob("*.md") if not p.name.startswith("_")]
    parent_files = list(parent_dir.glob("*.md"))
    
    # 汇总 父类→子类 映射
    parent_to_children = {}
    for child in child_files:
        fm = parse_frontmatter(open(child).read())
        parent = fm.get('父类', '')
        parent_to_children.setdefault(parent, []).append(child.name)
    
    parent_names = {p.stem for p in parent_files}  # 文件名去 .md (= 父类名)
    declared = set(parent_to_children.keys())
    
    # 有父类文件但无子类 → WARNING
    for p in parent_names - declared:
        warnings.append(f"父类 '{p}' 无任何子类引用")
    
    # 有子类声明但父类文件不存在 → ERROR(已在 P0.3-A+B 中报错,此处补充)
    for d in declared - parent_names:
        if d:  # 跳过空声明(已在 P0.3-A+B 中 WARNING)
            errors.append(f"子类引用父类 '{d}' 但父类文件不存在: _父类/{d}.md")
    
    return errors, warnings
```

**调用位置**：在 `main()` 中，所有文件单文件校验（P0.3-A+B）完成后调用一次。

---

### frontmatter 键名规范

| 文件类型 | 键名 | 值格式 | 用途 |
|----------|------|--------|------|
| 父类 | `父类ID:` | 英文 slug（如 `reward-system`） | 程序化索引 |
| 父类 | `父类名:` | 中文名（如 `奖赏系统障碍`） | 子类 `父类:` 匹配 + 父类文件名（`_父类/<父类名>.md`） |
| 子类 | `父类:` | 中文名（如 `奖赏系统障碍`） | P0.3 用此值查找父类文件 |
| 子类 | `疾病ID:` | 英文 slug（如 `mdd`） | 程序化索引 |

**查找规则**：`子类.父类:` 的值 = `父类.父类名:` 的值 = 父类文件名（在 `_父类/` 子目录下，不带 `_` 前缀）。

---

## P1 — 文献搜索

### 已有文献（无需再搜）

| 疾病 | 文献覆盖 | 状态 |
|------|---------|:---:|
| 偏执型精神分裂症 | ENIGMA + Guo ALFF + PANSS | ✅ 已定量填充 |
| 重度抑郁症 MDD | ENIGMA + Guo + RDoC奖赏回路 | ✅ 文献已有 |
| 双相障碍 BD | ENIGMA BD (Hibar 2016) + Guo + RDoC | ✅ 文献已有（I/II 亚型效应量差异待确认） |
| OCD | ENIGMA + Guo + CSTC回路 | ✅ 文献已有 |
| PTSD | Guo + 杏仁核FC meta | ✅ 文献已有 |
| GAD | Guo + RDoC唤醒域 + 杏仁核过度反应 | ✅ 文献已有 |
| ASD | ENIGMA + social brain connectivity + RDoC社会过程 | ✅ 文献已有 |
| 神经性厌食症 AN | insula interoception meta + reward circuit | ✅ 文献已有 |

### 执行前确认

搜索前先 `Read` `参考/文献/疾病-脑区链路映射-文献数据源.md` §七 全部内容，确认现有条目列表。

### 待搜文献（每个疾病至少 1-2 篇关键文献）

#### 奖赏系统障碍组（4 个）

| # | 疾病 | 搜索关键词 | 目标数据 |
|----|------|----------|---------|
| 1 | 未分化型精神分裂症 | PANSS undifferentiated schizophrenia brain imaging | 与偏执型的m偏移差异 |
| 2 | 分裂情感性障碍 | schizoaffective disorder ENIGMA fMRI GMV | 精分+心境混合特征 |
| 3 | 持续性心境障碍/环性心境 | cyclothymia neuroimaging fMRI reward | 与BD的差异 |
| 4 | 物质使用障碍 | substance use disorder ENIGMA dopamine reward fMRI | VTA→NAcc + dlPFC↓ |

#### 焦虑唤醒障碍组（1 个）

| # | 疾病 | 搜索关键词 | 目标数据 |
|----|------|----------|---------|
| 5 | 特定恐惧症 | specific phobia fMRI amygdala PAG fear circuit | 杏仁核→PAG + 回避 |

#### 认知控制障碍组（2 个）

| # | 疾病 | 搜索关键词 | 目标数据 |
|----|------|----------|---------|
| 6 | ADHD | ADHD ENIGMA fMRI dlPFC default mode | dlPFC成熟延迟 + DMN干扰；补充 ENIGMA subcortical volumes（Cohen's d） |
| 7 | 拖延症 | procrastination fMRI dlPFC temporal discounting | 奖赏时间折扣 + dlPFC↓ |

#### 社会认知障碍组（1 个）

| # | 疾病 | 搜索关键词 | 目标数据 |
|----|------|----------|---------|
| 8 | ASPD | antisocial personality disorder fMRI vmPFC amygdala empathic | vmPFC↓ + 杏仁核↓ + 共情缺失 |

#### 解离性障碍组（1 个）

| # | 疾病 | 搜索关键词 | 目标数据 |
|----|------|----------|---------|
| 9 | DID | dissociative identity disorder fMRI neuroimaging brain | 记忆区隔化 + 整合域异常 |

#### 进食障碍组（1 个）

| # | 疾病 | 搜索关键词 | 目标数据 |
|----|------|----------|---------|
| 10 | 神经性贪食症 BN | bulimia nervosa fMRI impulsivity reward binge | 冲动控制 + 奖赏域 |

#### GAD 定量化追加（1 个）

| # | 疾病 | 搜索关键词 | 目标数据 |
|----|------|----------|---------|
| 11 | GAD（定量化） | GAD fMRI default mode worry perseveration | 持续性担忧的DMN-认知控制交互 |

> 注：#11 已有文献覆盖功能层面，仅补充定量效应量。不增加疾病计数。

### P1 产出

追加到 `参考/文献/疾病-脑区链路映射-文献数据源.md` §七，格式参照现有条目。

---

## P2 — 父类模板 + 已有文件迁移

### 父类文件路径

父类文件存放于 `实体/疾病目录/_父类/` 子目录。文件名 = `<父类名>.md`（不带 `_` 前缀，与 P0.3 查找规则一致：`parent_dir / f"{父类值}.md"`）。

### P2.0 — 迁移偏执型精神分裂症

1. blockquote `> 父类: 精神分裂症` → YAML frontmatter：
   ```yaml
   ---
   父类: 奖赏系统障碍
   疾病ID: paranoid-schizophrenia
   CGI-S范围: 3-7
   文献: ENIGMA SZ (Van Erp 2016), Guo et al. 2026, PANSS (Fountoulakis 2019)
   ---
   ```
2. 删除原有 `> 文献: ...` 块（信息已移入 frontmatter）
3. 正文不变
4. 跑 P0.3 确认与新父类无矛盾

### 父类文件（6 个）

| 文件名 | 功能域定性方向 | 默认病理类型 | 默认标签 |
|------|-------------|------------|---------|
| `奖赏系统障碍.md` | 奖赏域↓, 整合域异常, 内感受域异常 | 解耦沉默 + 边界崩溃 | — |
| `焦虑唤醒障碍.md` | 唤醒域↑, 防御域↑, 内感受域↑ | 过度耦合 | 敏化-威胁 |
| `认知控制障碍.md` | 认知控制域异常, 行动门控域异常 | 过度耦合 或 解耦沉默 | — |
| `社会认知障碍.md` | 自我社会域↓, 语言社会域异常 | 结构异常 | 社交钝化 |
| `解离性障碍.md` | 整合域异常, 记忆域区隔化, 自我社会域↓ | 解耦沉默 | — |
| `进食障碍.md` | 内感受域异常, 奖赏域↓, 认知控制域↑ | 解耦沉默 + 过度耦合 | — |

> 文件在 `_父类/` 子目录下，文件名 = 父类名（不带 `_` 前缀）。

### 病理类型用词规范

| 符号 | 含义 |
|:---:|------|
| ` + ` | 混合——同一链路可能有多种类型，或同一疾病不同链路分属不同类型 |
| `或` | 择——不同子类在不同条件下取不同类型，子类在集合内选择 |
| `+` 和 `或` 同时出现 | 非法语法，P0.3-B 拦截为 ERROR |

### 父类模板格式

```markdown
---
父类ID: reward-system
父类名: 奖赏系统障碍
功能域定性方向:
  防御域: null
  奖赏域: ↓
  唤醒域: null
  行动门控域: null
  记忆域: null
  内感受域: 异常
  自我社会域: null
  感觉域: null
  运动域: null
  识别域: null
  认知控制域: null
  语言社会域: null
  整合域: 异常
默认病理类型: 解耦沉默 + 边界崩溃
默认标签: []
---

# 奖赏系统障碍
...
```

### 继承冲突解决规则

1. **方向约束**：`↓` → 子类净方向 < 0；`↑` → > 0；`异常` → 至少一条链路 \|m\| ≥ 0.1；`null` → 无约束。净方向 = 最高有效严重度下该域所有链路 m 值之和的符号。
2. **病理类型约束**：仅 `解耦沉默 ↔ 过度耦合` 矛盾（信号强度轴对立）。其他类型可自由组合。
3. **链路覆盖**：子类 m 偏移优先级 > 父类同链路声明。
4. **默认标签**：子类可覆盖。
5. **m 偏移范围**：父类不设数值范围，定量由子类定义。
6. **域扩展**：子类可在 `null` 域中自由添加链路。

### 子类 YAML frontmatter 模板

```markdown
---
父类: 奖赏系统障碍
疾病ID: mdd
CGI-S范围: 3-7
文献: ENIGMA MDD (Schmaal 2016), Guo et al. 2026
创建: 2026-08-01
---
```

---

## P3 — 疾病定量填充

### 全部疾病

| # | 疾病 | 父类 | 档位 | 核心病理类型 | 预估链路数 | 状态 |
|----|------|------|:---:|------------|:---:|:---:|
| 0 | 偏执型精神分裂症 | 奖赏系统障碍 | — | 边界崩溃 + 过度耦合 + 解耦沉默 | 15 | ✅ P2.0 迁移后 |
| 1 | 重度抑郁症 MDD | 奖赏系统障碍 | A | 解耦沉默 | 10-12 | |
| 2 | PTSD | 焦虑唤醒障碍 | A | 跨层短路 | 8-10 | |
| 3 | OCD | 认知控制障碍 | A | 过度耦合 | 10-14 | |
| 4 | ASD | 社会认知障碍 | A | 结构异常 | 10-14 | |
| 5 | 神经性厌食症 AN | 进食障碍 | A | 解耦沉默 + 过度耦合 | 10-12 | |
| 6 | 双相障碍 I型 | 奖赏系统障碍 | B¹ | 过度耦合 + 解耦沉默（交替） | 12-15 | |
| 7 | 双相障碍 II型 | 奖赏系统障碍 | B¹ | 过度耦合 + 解耦沉默（交替） | 10-12 | |
| 8 | 未分化型精神分裂症 | 奖赏系统障碍 | B | 边界崩溃 + 解耦沉默 | 8-12 | |
| 9 | 物质使用障碍 | 奖赏系统障碍 | B | 过度耦合 + 解耦沉默 | 8-10 | |
| 10 | ADHD | 认知控制障碍 | B | 解耦沉默（发育延迟） | 8-12 | |
| 11 | GAD | 焦虑唤醒障碍 | B | 过度耦合 | 8-10 | |
| 12 | 分裂情感性障碍 | 奖赏系统障碍 | C | 边界崩溃 + 解耦沉默 | 10-14 | |
| 13 | 持续性心境障碍 | 奖赏系统障碍 | C | 解耦沉默（轻度） | 6-8 | |
| 14 | 特定恐惧症 | 焦虑唤醒障碍 | C | 过度耦合（刺激特异性） | 4-6 | |
| 15 | ASPD | 社会认知障碍 | C | 解耦沉默 + 结构异常 | 8-10 | |
| 16 | DID | 解离性障碍 | C | 解耦沉默（整合域区隔化） | 6-8 | |
| 17 | 神经性贪食症 BN | 进食障碍 | C | 解耦沉默 + 过度耦合 | 8-12 | |
| 18 | 拖延症 | 认知控制障碍 | C | 解耦沉默（时间折扣偏误） | 4-6 | |

¹ BD I/II：P1 中优先搜索 I/II 亚型效应量差异文献。若充分 → 升入 P3-A；若不充分 → 保持 P3-B。

### 每个疾病文件的模板

1. YAML frontmatter
2. **功能域配置表**（4 列：`域 | 链路ID | 病理类型 | m偏移(轻/中/重)`。`病理类型` 为必填列）
3. **CGI-S域扩展表**（列：`严重度 | 核心域 | 关联域 | 边缘域 | m倍率(参考) | 域数合计`）
4. **默认标签**
5. **行为覆盖**（表格：`条件 | 约束`）
6. **非线性跳变**（表格：`m阈值 | 作用域 | 效果`）
7. **组件掉落池**（表格：`权重 | 链路ID`。权重格式：`N (核心|关联|边缘)`）
8. **思路链**

### P3 执行顺序

**前置**：P1 中优先完成 BD I/II 亚型效应量搜索 → 决定升档。
P3-A（5 个 ± BD）→ P3-B（6 个 ∓ BD）→ P3-C（7 个）。每档完成后跑 validate，修完再进下一档。

---

## P4 — 校验 + 角色系统解耦 + 清扫

### P4.1 自动化校验

```bash
python tools/validate_disease.py  # 全量检查
```

检查项（由 P0 实现，含 per-file 和 global）：
- 链路ID在 `link_registry.json` 中存在
- 病理类型为合法值（复合用 `+` split）（P0.1）
- 域数约束（轻度1-2核心/中度+关联/重度+边缘）
- m偏移方向与父类定性方向不矛盾（P0.3-A，净方向公式）
- 病理类型与父类不矛盾（P0.3-B，完整 5×5 矛盾矩阵）
- 父类归属交叉验证（P0.3-C，global，`main()` 中调用）
- 组件掉落池权重格式 + tier 标签 + 范围（P0.2，返回 tuple）

### P4.2 角色→疾病引用改造

1. `Read` `实体/角色与面具.md`，确认 14 角色疾病信息当前格式
2. 为每个角色新增结构化疾病引用字段（`疾病: [疾病名](../疾病目录/<疾病名>.md)`）
3. 校验：grep 所有引用路径 → 确认每个目标文件存在

### P4.3 一致性清扫

**1. 228→364 残留清理**（6 个文件，8+ 处）：

| 文件 | 行 | 操作 |
|------|:--:|------|
| `呈现/战斗界面布局.md` | 31 | `s/228/364/` |
| `管线/预烘焙管线脚本设计.md` | 29, 58, 207, 253 | `s/228/364/g` |
| `参考/文献/疾病-脑区链路映射-文献数据源.md` | 252, 265 | `s/228/364/` |
| `data/connectivity/subcortical_links_AUDIT.md` | 29 | `s/228/364/` |

决策树中的 228 为历史记录，保留。

**2. 旧父类名残留 + 更新六维状态 + 决策树追加**

---

## 执行检查清单

- [ ] P0.0: 升级 `parse_frontmatter()`（PyYAML；`dict[str,Any]`；`or {}` 空 fallback）
- [ ] P0.1: 新增 `validate_pathology_types()` → `list[str]`（在 `validate_file()` 主循环中调用，`病理类型` 必填）
- [ ] P0.2: 扩展 `validate_drop_pool()` → `tuple[list[str], list[str]]`（格式 ERROR + 范围 WARNING，N = CGI-S 表实际 tier 数）
- [ ] P0.3-A+B: 新增 `validate_parent_inheritance()` → `tuple[list[str], list[str]]`（净方向公式 + 完整矛盾矩阵 + `+`/`或` 并发 → ERROR）
- [ ] P0.3-C: 新增 `validate_parent_child_consistency()` → `tuple[list[str], list[str]]`（global，`main()` 中调用）
- [ ] `validate_file()` 签名变更：增加 `parent_dir` 参数；父类文件自身跳过 P0.3-A+B
- [ ] P1: 11 条目文献搜索（含 BD I/II 亚型优先搜索）
- [ ] P2.0: 偏执型精分格式迁移
- [ ] P2: 6 个父类文件 → `_父类/` 子目录
- [ ] P3-A: A 档疾病填充 → validate → 修完
- [ ] P3-B: B 档疾病填充 → validate → 修完
- [ ] P3-C: C 档疾病填充 → validate → 修完
- [ ] P4.1: `validate_disease.py` 全通过（19 文件无 ERROR）
- [ ] P4.2: 角色→疾病引用改造 + 完整性校验
- [ ] P4.3: 228→364 残留清理 + 旧父类名 grep + 六维状态 + 决策树
- [ ] 关闭 issue #14

---

*创建: 2026-08-01 | 更新: 2026-08-01（DRY-RUN.md 11 断层全部修正）*
*关联: [DRY-RUN.md](DRY-RUN.md), [PLAN-REVIEW-v4.md](PLAN-REVIEW-v4.md), [validate_disease.py](../../tools/validate_disease.py), [偏执型精神分裂症.md](../../实体/疾病目录/偏执型精神分裂症.md)*
