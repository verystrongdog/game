# 数据层

> 结构化数据文件（JSON），供 C# 引擎（`src/YouAreNotTheFish.Core`）与 Python 工具直接读取。md 文档负责设计推导和"为什么"，JSON 负责"是什么"。🔧 2026-08-14 Grilling #24 C-2：重写索引——旧版只列已废弃的态度/情绪/行为/卡牌文件，未提及引擎实际消费的 5 个数据文件。

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
md 文档（设计层）          JSON 文件（数据层）          C# 引擎 / Python 工具（消费层）
─────────────────         ─────────────────           ─────────────────
为什么是这个参数           参数的具体数值               GameDataLoader.LoadAll → record
文献出处和推导过程          字段含义和取值范围           数值模拟验证 / 数据驱动管线
讨论和废弃原因             纯数据结构，无语义歧义        Unity ScriptableObject 映射
```

- **md 是 source of truth for design rationale**
- **JSON 是 source of truth for parameter values**
- **引擎消费路径**：`GameDataLoader.LoadAll(dataDir)` → `GameData`（5 record 聚合）→ 引擎模块（详见 [引擎数据关系规格](../规则/技能树系统/引擎数据关系规格.md)）
- JSON 可被 Git diff（比 SQL dump 友好）
- 未来 Unity 实装时，JSON → ScriptableObject 有成熟工具链（见引擎数据关系规格 §六）

---

## 二、文件索引

### 引擎消费（5 文件，正典）

| 文件 | 内容 | 规模 | 来源 | 消费方 |
|------|------|------|------|--------|
| `brain_regions.json` | 50 解剖实体 + 19 细分 = **69 functional_id**（44 皮层 + 14 皮下 + 11 脑干；67 剖面 + 2 mirror_of 展开），每区 16 字段含 function_profile；带 dk_name 条目含 lateralization（Grilling #92） | 69 regions | `规则/技能树系统/脑功能层级模型.md` | 全部引擎层（行序锚/τ/CSTC CI/坐标） |
| `connectivity/tripartite_model.json` | 三体神经模型：51 图节点 + 4 种边（皮层-皮层 776 / 脑干广播 114 / CSTC 环路 47 / 特权通路 112）；graph_nodes 含 lateralization 字段（Grilling #92） | 51 / 1049 边 | 脑功能层级模型 §二十（Grilling #26） | WMatrixBuilder / CorticalBias / CstcGating |
| `connectivity/W_sensory.json` | 感官模态→解剖节点映射矩阵（6 模态 × 69 节点，二值） | 69×6 | `规则/技能树系统/运行时状态模型.md` §4.5（Grilling #34） | EventProcessor（s 打包）+ canonical 行序锚 |
| `connectivity/situation_primitives.json` | 27 情境原型（RDoC 剖面 + 评估剖面 + 关键脑区） | 27 archetypes | `规则/核心机制.md` §六 | 正式情境系统（demo 未消费） |
| `signal_types.json` | 信号类型受控词表（4 大类 × 18 子类） | 18 subtypes | 脑功能层级模型 §二十.8 | function_label / function_profile membership 校验 |

### 支持文件

| 文件 | 内容 | 规模 | 说明 |
|------|------|------|------|
| `connectivity/region_name_map.json` | 69 functional_id 三层 ID 映射（fid → dk_name → zh_name） | 69 条目 | 🔧 2026-08-14 对齐 69（删 2 聚合体 + 补 STN） |
| `connectivity/kroell14_networks.json` | Kroell 14 网络集合 | 14 | 技能生成/上下文判定 |
| `connectivity/link_modulation_ceiling_v2.json` | 链路调制天花板 | — | 参考（旧链路体系） |
| `term_registry.json` | 术语注册表（Grilling §3.0 基线数据源） | 134 条 | 设计期参考，非运行时数据 |

### 参考数据（⚠️ 已废弃系统，保留为参数参考）

| 文件 | 内容 | 说明 |
|------|------|------|
| `emotions.json` / `drives.json` / `attitudes.json` | 旧态度引擎 PAD/驱动/态度 | ⚠️ 态度引擎已废弃（2026-07-26），保留为参考 |
| `emotion_cards.json` / `cognition_cards.json` / `behavior_cards.json` | 旧卡牌系统 | ⚠️ 卡牌体系已废弃（2026-07-11），保留为参数参考 |

---

## 三、数据关系图

```
数据文件 ──GameDataLoader.LoadAll──→ GameData（5 record 聚合）
  │
  ├─ brain_regions.json (69 fid) ──→ τ 查表 / CSTC CI 解析 / game_xyz
  ├─ tripartite_model.json (51节点+1049边) ──→ W 矩阵（皮层-皮层×特权通路） / b_j（脑干广播）
  ├─ W_sensory.json (69×6) ──→ s(t) 打包（W_sensory × α）
  ├─ situation_primitives.json (27) ──→ （正式情境选择，demo 未消费）
  └─ signal_types.json (4×18) ──→ 词表校验

三层因果链（运行时状态模型 §一）：
  tone（脑干 4 标量）→ b_j → a(t)（WC 69 节点）→ c_loop → gate（CSTC 3 环路）→ 战斗结算
```

完整数据流见 [引擎数据关系规格](../规则/技能树系统/引擎数据关系规格.md) §二。

---

## 四、使用方式

### C# 引擎（正典路径）

```csharp
var data = GameDataLoader.LoadAll("data");   // 5 文件一次加载 → GameData
var w = WMatrixBuilder.Build(data);          // W[69,69] + τ[69]
var b = CorticalBias.Compute(tone, data);    // 脑干调制 69 维
```

### Python 工具

```python
import json

with open('data/brain_regions.json') as f:
    regions = json.load(f)['regions']
print(len(regions))  # 69

with open('data/connectivity/tripartite_model.json') as f:
    tri = json.load(f)
print(len(tri['graph_nodes']))  # 51
```

---

## 五、维护规则

1. **JSON 是 md 的导出格式**：修改参数时，先改 md 文档中的推导和依据，再同步更新 JSON
2. **JSON 字段只增不删**：加字段可以，删字段需要确认没有脚本/引擎依赖
3. **所有数值参数标注来源**：JSON 中 `_source` 字段指明来源 md 文档
4. **格式规范**：UTF-8 编码，2 空格缩进，`_` 前缀表示元数据字段
5. **日期标注**：`_updated` 字段记录最后修改日期
6. **计数一致性**：functional_id 主键数（69）必须与 `brain_regions.json` / `region_name_map.json` / `W_sensory.json` rows 三方一致——修改任一文件须同步其余（Grilling #24 D-1 确立）

---

*创建: 2026-07-09 | 更新: 2026-08-14（Grilling #24 C-2：索引重写为引擎 5 文件 + 废弃参考分区；D-1：region_name_map 对齐说明）*
*关联: [项目总览](../项目总览.md), [核心机制](../规则/核心机制.md), [引擎数据关系规格](../规则/技能树系统/引擎数据关系规格.md), [脑功能层级模型](../规则/技能树系统/脑功能层级模型.md), [运行时状态模型](../规则/技能树系统/运行时状态模型.md)*
