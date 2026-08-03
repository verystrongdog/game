# 数据层

> 结构化数据文件（JSON），供 Python 模拟脚本直接读取。md 文档负责设计推导和"为什么"，JSON 负责"是什么"。

---

## 目录

1. [架构原则](#一架构原则)
2. [文件索引](#二文件索引)
3. [数据关系图](#三数据关系图)
4. [使用方式](#四使用方式)
5. [维护规则](#五维护规则)

---

## 一、架构原则

```
md 文档（设计层）          JSON 文件（数据层）          Python 脚本（验证层）
─────────────────         ─────────────────           ─────────────────
为什么是这个参数           参数的具体数值               import json 直接读
文献出处和推导过程          字段含义和取值范围           数值模拟验证
讨论和废弃原因             纯数据结构，无语义歧义        蒙特卡洛/CTRNN
```

- **md 是 source of truth for design rationale**
- **JSON 是 source of truth for parameter values**
- 两者冲突时，以 md 为准（JSON 是导出格式，md 是原始设计文档）
- JSON 可被 Git diff（比 SQL dump 友好）
- 未来 Unity 实装时，JSON → ScriptableObject 有成熟工具链

---

## 二、文件索引

| 文件 | 内容 | 规模 | 来源 |
|------|------|------|------|
| `emotions.json` | 15 情绪锚点 PAD 坐标 + 行为推力 + 激活驱动 | 15 条 | `情绪系统/PAD-情绪参考表.md` |
| `drives.json` | 7 行为驱动完整参数（激活函数/θ/β/γ/φ/τ/病情扭曲） | 7 条 + 配置 | `行为系统/行为系统.md`, `态度系统/态度系统.md` |
| `attitudes.json` | 90 种态度（情绪×驱动）的生成算法 + 行为输出 + 状态矩阵 | 90 条 | `态度系统/态度模型可视化.html` |
| `emotion_cards.json` | 15 张情绪卡完整数据（打出效果/手牌压力/残留/获得条件/联动） | 15 条 | `卡牌系统/情绪卡模板.md`, `data/emotions.json` |
| `cognition_cards.json` | 25 张认知卡完整数据（C⁵ 参数/CPM/效果类型/情绪扭曲/门控） | 25 条 | `卡牌系统/认知卡模板.md`, `data/drives.json` |
| `behavior_cards.json` | 21 张行为卡完整数据（驱动归属/valence/AP/效果/悬停文案/联动） | 21 条 | `卡牌系统/行为卡模板.md`, `data/drives.json` |

---

## 三、数据关系图

```
emotions.json (15)
    │
    ├── PAD (V, A, D) ──→ drives.json (7) 激活函数 g_i(PAD)
    │                            │
    │                            ├── θ_play, β, γ, φ, τ
    │                            ├── drive_pole (RST)
    │                            │
    │                            ▼
    └── B_raw ──────────→ attitudes.json (90)
                             │
                             ├── state: natural | forced | situational
                             ├── behavior_output: (valence, intensity, autonomy)
                             └── summary_matrix: 15×7 状态矩阵
```

**核心计算链：**
```
情绪 PAD → sigmoid → g_i (驱动激活) → 与 θ_play 比较 → 行为卡可用性/成本
         ↘
          B_raw = (V, |A|, D) → 与 drive_pole 混合 → 态度行为输出 B(t)
```

---

## 四、使用方式

### Python 模拟脚本

```python
import json

# 加载数据
with open('data/emotions.json') as f:
    emotions = json.load(f)

with open('data/drives.json') as f:
    drives = json.load(f)

with open('data/attitudes.json') as f:
    attitudes = json.load(f)

# 查某情绪 PAD
fear = [e for e in emotions['emotions'] if e['id'] == 'fear'][0]
print(fear['pad'])  # {'V': -0.854, 'A': 0.680, 'D': -0.414}

# 查驱动激活公式
reflex = [d for d in drives['drives'] if d['id'] == 'reflex'][0]
print(reflex['activation']['sigmoid'])  # σ(2.0·max(0,A-0.3) + 1.5·max(0,0.5-D) - 0.5)

# 遍历所有态度
for a in attitudes['attitudes']:
    if a['state'] == 'forced':  # 筛选硬解锁态度
        print(f"{a['id']}: {a['behavior_output']}")
```

### 现有模拟脚本复用

旧模拟脚本（sim_battle.py/sim_cog_evo.py 等）已废弃进垃圾桶（2026-08-03 #20）。新工具（tools/build_*/validate_*）从 `data/` 目录加载数据。

---

## 五、维护规则

1. **JSON 是 md 的导出格式**：修改参数时，先改 md 文档中的推导和依据，再同步更新 JSON
2. **JSON 字段只增不删**：加字段可以，删字段需要确认没有脚本依赖
3. **所有数值参数标注来源**：JSON 中 `_source` 字段指明来源 md 文档
4. **格式规范**：UTF-8 编码，2 空格缩进，`_` 前缀表示元数据字段
5. **日期标注**：`_updated` 字段记录最后修改日期

---

*创建: 2026-07-09*
*关联: [00-项目总览](../项目总览.md), [01-核心机制](../规则/核心机制.md), [态度系统](../态度系统/态度系统.md), [情绪系统](../情绪系统/PAD-情绪参考表.md), [行为系统](../行为系统/行为系统.md)*
