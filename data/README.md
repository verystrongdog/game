# 数据层

> 结构化数据文件（JSON），供 C# 引擎（`code/src/YouAreNotTheFish.Core`）与 Python 工具直接读取。md 文档负责设计推导和"为什么"，JSON 负责"是什么"。🔧 2026-08-14 Grilling #24 C-2：重写索引——旧版只列已废弃的态度/情绪/行为/卡牌文件，未提及引擎实际消费的 5 个数据文件。

---

## 目录

1. [架构原则](#一架构原则)
2. [数据契约清单](#二数据契约清单)
3. [文件索引](#三文件索引)
4. [数据关系图](#四数据关系图)
5. [使用方式](#五使用方式)
6. [维护规则](#六维护规则)

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
- **引擎消费路径**：`GameDataLoader.LoadAll(dataDir)` → `GameData`（5 record 聚合）→ 引擎模块（详见 [引擎数据关系规格](../design/rules/skill-tree/%E5%BC%95%E6%93%8E%E6%95%B0%E6%8D%AE%E5%85%B3%E7%B3%BB%E8%A7%84%E6%A0%BC.md)）
- JSON 可被 Git diff（比 SQL dump 友好）
- 未来 Unity 实装时，JSON → ScriptableObject 有成熟工具链（见引擎数据关系规格 §六）

---

## 二、数据契约清单

> **每个受控数据文件的权威属性见 [`manifest.json`](manifest.json)**——由
> [`code/tools/build_data_manifest.py`](../code/tools/build_data_manifest.py) 从证据生成，
> 含四轴正交属性（origin / lifecycle / role / shipping）+ owner + 生成链 + 消费方。

| 轴 | 取值 | 含义 |
|---|---|---|
| `origin` | authored / generated / external | 手写 / 工具生成 / 外部下载 |
| `lifecycle` | active / deprecated / archived | 任一引用面活跃 / 仅废弃子系统引用 / 三类引用面全空 |
| `role` | runtime / generator-input / reference / evidence | 运行时消费 / 生成链输入 / 参考或校验基准 / 归档 |
| `shipping` | true / false | 是否进入运行时路径（**仅 runtime 为 true**） |

**判据**（owner 方案 §9.3）：

- **`archived` 不等于"零设计文档引用"**——还要看活跃代码与生成链。
  实测教训（2026-09-12）：`enigma_sc_ctx_matrix.npy` 等 5 个文件零设计文档引用，
  但被 [`gen_modulation_ceiling.py`](../code/tools/gen_modulation_ceiling.py) 实际读取；
  按"零文档引用"判定就会把活着的生成链输入标成可清理的孤儿。
  现在 `archived` 的含义是**活跃文档、活跃代码、活跃工具链三条引用面全空**。
- **`origin=generated` 只认写出证据**（`json.dump` / `write_text` / `np.save` 等），
  不认"文件里出现过这个名字"——读入也算出现。
- **`--check` 不重新推导属性**：属性是声明式契约；`refs` 计数会因任意新增 `.md`
  提到该文件名而漂移，若比对推导值，则写任何文档都要重生成 manifest。
  属性更新是人工动作 `--refresh`。

**runtime allowlist**：引擎只允许消费 `role=runtime` 的 8 个文件（由 `GameDataLoader.LoadAll` 实测确定，
双向校验见 [`validate_data_manifest.py`](../code/tools/validate_data_manifest.py)）。

**外部数据来源**：`data/connectivity/` 下的外部数据集（Yeo2011 / Hansen2024 / CAB-NP / ENIGMA / Kroell）
的来源、许可、文件清单与消费方见 [connectivity/external-sources.md](connectivity/external-sources.md)。
该表登记了两项**未闭合缺口**，不得当作通过。

## 三、文件索引

### 引擎消费（8 文件，正典）

> 文件清单以 `GameDataLoader.LoadAll` 为准（spec@v1.1 §三 3.3 + #105 T2/T3/T6）。

| 文件 | 内容 | 规模 | 来源 | 消费方 |
|------|------|------|------|--------|
| `brain_regions.json` | 50 解剖实体 + 19 细分 = **69 functional_id**（44 皮层 + 14 皮下 + 11 脑干；67 剖面 + 2 mirror_of 展开），每区 16 字段含 function_profile；带 dk_name 条目含 lateralization（Grilling #92） | 69 regions | `design/rules/skill-tree/脑功能层级模型.md` | 全部引擎层（行序锚/τ/CSTC CI/坐标） |
| `connectivity/tripartite_model.json` | 三体神经模型：51 图节点 + 4 种边（皮层-皮层 776 / 脑干广播 114 / CSTC 环路 47 / 特权通路 112）；graph_nodes 含 lateralization 字段（Grilling #92） | 51 / 1049 边 | 脑功能层级模型 §二十（Grilling #26） | WMatrixBuilder / CorticalBias / CstcGating |
| `connectivity/W_sensory.json` | 感官模态→解剖节点映射矩阵（8 模态 × 69 节点，二值） | 69×8 | `design/rules/skill-tree/运行时状态模型.md` §4.5（Grilling #34；#108 Q2 扩列嗅觉/热觉） | EventProcessor（s 打包）+ canonical 行序锚 |
| `connectivity/situation_primitives.json` | 27 情境原型（RDoC 剖面 + 评估剖面 + 关键脑区） | 27 archetypes | `design/rules/核心机制.md` §六 | 正式情境系统（demo 未消费） |
| `signal_types.json` | 信号类型受控词表（4 大类 × 18 子类） | 18 subtypes | 脑功能层级模型 §二十.8 | function_label / function_profile membership 校验 |
| `connectivity/alpha_patterns.json` | α 模式表：8 模态 × 事件字典 | 8 模态 / 6+ 事件 | #105 T2 | EventProcessor |
| `connectivity/env_tones.json` | 环境 tone 向量表 | 3 环境（ward/corridor/nurse_station） | #105 T3 | EventProcessor（tone 通道） |
| `connectivity/moonlight_landing.json` | 月光落点语义（s_core 等） | PLACEHOLDER（calibration_version 0） | #105 T6 | MoonlightLanding |

### 支持文件

| 文件 | 内容 | 规模 | 说明 |
|------|------|------|------|
| `connectivity/region_name_map.json` | 69 functional_id 三层 ID 映射（fid → dk_name → zh_name） | 69 条目 | 🔧 2026-08-14 对齐 69（删 2 聚合体 + 补 STN） |
| `connectivity/kroell14_networks.json` | Kroell 14 网络集合 | 14 | 技能生成/上下文判定 |
| `connectivity/link_modulation_ceiling_v2.json` | 链路调制天花板 | — | 参考（旧链路体系） |
| `term_registry.json` | 术语注册表 | 311 条 | 设计期参考，非运行时数据 |

### 参考数据（⚠️ 已废弃系统，保留为参数参考）

| 文件 | 内容 | 说明 |
|------|------|------|
| `emotions.json` / `drives.json` / `attitudes.json` | 旧态度引擎 PAD/驱动/态度 | ⚠️ 态度引擎已废弃（2026-07-26），保留为参考 |
| `emotion_cards.json` / `cognition_cards.json` / `behavior_cards.json` | 旧卡牌系统 | ⚠️ 卡牌体系已废弃（2026-07-11），保留为参数参考 |

### 契约 fixture（`runtime-fixtures/`）

> 8 个 runtime 文件的**合法与非法样例**，供 Python 与 C# **共用**（owner 方案 §9.3）。

| 内容 | 说明 |
|---|---|
| `runtime-fixtures/index.json` | 53 条用例的索引：`file` / `logical_id` / `expect` / `rule` / `mutation` / `depends_on` |
| `runtime-fixtures/<logical_id>/valid.json` | 真实文件的副本——**必须被两侧接受** |
| `runtime-fixtures/<logical_id>/*.json` | **单点变异**样例——**必须被两侧拒绝** |

**为何是单点变异**：每个非法样例与合法版本的差异**恰好一处**，
因此"该被拒绝"的归因是确定的（`rule` 字段），不会出现"它失败了但不知道因为哪条规则"。
手写 JSON 会与真实数据脱节——真实数据加字段，手写样例不知道。

生成与校验：

```bash
python3 code/tools/build_runtime_data_fixtures.py --refresh   # 重建
python3 code/tools/build_runtime_data_fixtures.py --check     # 索引与磁盘一致
python3 code/tools/validate_runtime_fixtures.py               # Python 侧判定
python3 code/tools/compare_fixture_verdicts.py                # 跨语言逐条比对（需 dotnet）
```

---

## 四、数据关系图

```
数据文件 ──GameDataLoader.LoadAll──→ GameData（5 record 聚合）
  │
  ├─ brain_regions.json (69 fid) ──→ τ 查表 / CSTC CI 解析 / game_xyz
  ├─ tripartite_model.json (51节点+1049边) ──→ W 矩阵（皮层-皮层×特权通路） / b_j（脑干广播）
  ├─ W_sensory.json (69×8) ──→ s(t) 打包（W_sensory × α）
  ├─ situation_primitives.json (27) ──→ （正式情境选择，demo 未消费）
  └─ signal_types.json (4×18) ──→ 词表校验

三层因果链（运行时状态模型 §一）：
  tone（脑干 4 标量）→ b_j → a(t)（WC 69 节点）→ c_loop → gate（CSTC 3 环路）→ 战斗结算
```

完整数据流见 [引擎数据关系规格](../design/rules/skill-tree/%E5%BC%95%E6%93%8E%E6%95%B0%E6%8D%AE%E5%85%B3%E7%B3%BB%E8%A7%84%E6%A0%BC.md) §二。

---

## 五、使用方式

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

## 六、维护规则

1. **JSON 是 md 的导出格式**：修改参数时，先改 md 文档中的推导和依据，再同步更新 JSON
2. **JSON 字段只增不删**：加字段可以，删字段需要确认没有脚本/引擎依赖
3. **所有数值参数标注来源**：JSON 中 `_source` 字段指明来源 md 文档
4. **格式规范**：UTF-8 编码，2 空格缩进，`_` 前缀表示元数据字段
5. **日期标注**：`_updated` 字段记录最后修改日期
6. **计数一致性**：functional_id 主键数（69）必须与 `brain_regions.json` / `region_name_map.json` / `W_sensory.json` rows 三方一致——修改任一文件须同步其余（Grilling #24 D-1 确立）

---

*创建: 2026-07-09 | 更新: 2026-08-14（Grilling #24 C-2：索引重写为引擎 5 文件 + 废弃参考分区；D-1：region_name_map 对齐说明）*
*关联: [项目总览](../design/README.md), [核心机制](../design/rules/%E6%A0%B8%E5%BF%83%E6%9C%BA%E5%88%B6.md), [引擎数据关系规格](../design/rules/skill-tree/%E5%BC%95%E6%93%8E%E6%95%B0%E6%8D%AE%E5%85%B3%E7%B3%BB%E8%A7%84%E6%A0%BC.md), [脑功能层级模型](../design/rules/skill-tree/%E8%84%91%E5%8A%9F%E8%83%BD%E5%B1%82%E7%BA%A7%E6%A8%A1%E5%9E%8B.md), [运行时状态模型](../design/rules/skill-tree/%E8%BF%90%E8%A1%8C%E6%97%B6%E7%8A%B6%E6%80%81%E6%A8%A1%E5%9E%8B.md)*
