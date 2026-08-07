# Review Trace: privileged_pathways — 特权跨层通路白名单机制

> 审查日期: 2026-08-07 22:30 | 审查范围: `规则/技能树系统/脑功能层级模型.md` §20.4 + `data/connectivity/privileged_pathways.json`
> 方法: 符号执行 + 限界验证 | 前置检查: `tools/run_all_checks.py` (3 PASS, 2 FAIL 已忽略)

## 前置输入
- [x] Layer 1 预检查: 5 validators — 3 pass, 2 fail (死链 link_behavior_roles.json 预存 + S4 is_design_node)，均已忽略
- [x] Layer 1 WARN: 4 个（SAN 阈值一致性），不涉及本次追踪目标
- [x] 被引用文件自动拉入: `data/connectivity/privileged_pathways.json`
- [x] H1 深度 1 拉入: `tools/build_tripartite_model.py`（已验证含 privileged 代码）, `tools/build_function_labels.py`（验证缺失）

## Trace Table

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| 1 | `脑功能层级模型.md` §20.4 blockquote — pathway_class 枚举 | 解剖学文献（Witter 1989, Paxinos 2004, etc.） | 枚举<8 classes> = {perforant_path, amygdalofugal, thalamocortical_relay, cerebellothalamic, prefrontal_limbic, dmn_core, ventral_stream_emotion, brainstem_subcortical} | H2: 定义受控词表——8 个 pathway_class 覆盖所有解剖学证实的跨层连接类型。文档列出 8 项 + JSON 中 `pathway_classes` 字段定义完整描述 | 枚举<8 pathway_class> | `privileged_pathways.json` §pathway_classes（自描述）; `build_tripartite_model.py` 读取并作为 `pathway_class` 字段写入每条 privileged 连接 | null → ❌（类为空则连接无分类，但尚无校验）; 不在 8 类中 → 未校验（脚本无枚举受控检查） | ⚠️ 有疑点：文档列了 8 类，JSON 含 8 类描述，但生成脚本未做枚举校验——非法 class 值可无声通过 |
| 2 | 同上 — whitelist 条目结构 | `privileged_pathways.json` §pathways[61] | List<{source: 文本, target: 文本, class: 枚举<8>, basis: 文本, bidirectional: 布尔}> | H6: 61 条 pathway 条目 —— 结构验证通过：全部 source/target 在 51 个 graph_nodes 中存在 ✅；61 个 class 全部在 8 类中 ✅；51 双向 + 10 单向 ✅；EDR p≥0.10 全部通过 ✅ | List<PathwayEntry> | `build_tripartite_model.py` → `generate_privileged_pathways()` 逐条消费 | source/target 不在 graph_nodes → 代码中 `continue` 跳过（静默丢失），无警告输出；bidirectional 字段缺失 → 默认 true（代码 `entry.get("bidirectional", True)`） | ⚠️ 有疑点：source/target 不存在时静默跳过，无错误报告——可能隐藏 JSON 拼写错误。bidirectional 默认 true 合理但未在文档中声明 |
| 3 | 同上 — 白名单绕过层级约束 | graph_nodes{dk_name→level} + whitelist source/target | 输入: Dict<dk_name, level> + List<(source_dk, target_dk)> | H3: 对每个 whitelist pair，跳过 \|Δlevel\|≤1 检查 + 跳过 R9 脑干排除（category==brainstem + dk_name==functional_id），但强制 EDR p≥0.10（Molnár 2024, λ=0.015, c=0.85, threshold=0.10） | List<Connection> = {source, target, type="privileged_pathway", pathway_class, direction, distance_mm, edr_probability, level_diff} | `tripartite_model.json` §privileged_pathways → `build_function_labels.py` 读取并推导 function_label | EDR p<0.10 → 代码中 `continue` 跳过（当前 61 条全部通过 ✅）；MNI 坐标缺失 → 跳过 EDR 检查（dist=None → edr_passes 返回 False）——连接被静默丢弃 ⚠️；source/target 同节点（自环）→ 未做检查 | ⚠️ 有疑点：MNI 坐标缺失导致连接静默丢弃，无警告。当前无此情况，但无防御性编程 |
| 4 | `build_function_labels.py` 处理 privileged_pathways | `tripartite_model.json` §privileged_pathways | List<Connection>（同 #3 输出） | H5: 对每条 privileged 连接，取 source.output_types ∩ target.input_types → 推导 function_label；取 source.gameplay_domains ∪ target.gameplay_domains → gameplay_labels。空交集 → role="silent" | 同上 + {function_label, gameplay_labels, role, description} | `tripartite_model.json`（自更新）; 下游 NPC AI 预烘焙管线（`管线/预烘焙管线脚本设计.md`） | — | ❌ 有缺口：**build_function_labels.py 尚未实现 privileged_pathways 处理逻辑**。当前脚本仅处理 corticocortical/cstc/brainstem 三种 section，privileged_pathways 连接不会被标注 function_label。代码位于 `tools/build_function_labels.py:96-207`，需新增 ~20 行处理循环 |
| 5 | 管道衔接: 生成→标注→消费 | — | — | H5: `build_tripartite_model.py` Step 6/6 → 写入 `tripartite_model.json` → `build_function_labels.py` 读取标注 → 下游消费 | — | — | — | ⚠️ 管道断裂：#4 缺口导致 Step 6 产出未被 Step 7 标注（build_function_labels.py 未读取 privileged_pathways section） |

## 缺口汇总

| # | 位置 | 严重度 | 描述 |
|----|------|--------|------|
| 1 | `tools/build_function_labels.py:96-207` | ❌ BLOCKER | 未实现 privileged_pathways 处理循环。设计文档声明"功能标签由 build_function_labels.py 统一推导"，但代码仅处理 corticocortical/cstc/brainstem，privileged_pathways section 被忽略 |
| 2 | `脑功能层级模型.md` §20.4 blockquote | ⚠️ WARN | pathway_class 枚举值域已列出但生成脚本无受控校验——非法 class 值可无声通过 |
| 3 | `tools/build_tripartite_model.py:generate_privileged_pathways()` | ⚠️ WARN | source/target 不在 graph_nodes 或 MNI 坐标缺失 → 静默跳过，无 warning 输出。可能隐藏数据拼写错误 |
| 4 | 同上 | ⚠️ WARN | bidirectional 字段默认 true 但未在文档中声明——消费者需检查代码才能确认默认行为 |
| 5 | `规则/技能树系统/脑功能层级模型.md` §20.2 表格 | ⚠️ INFO | 生成规则列表仍只列三种原语（CSTC/皮层-皮层/脑干广播），未体现第 4 种（特权跨层通路）在生成流程中的位置。建议在表格下方加注或在 §20.4 末尾标注 |

## 半径扩张 — 待复查

| 修复点 | 受影响消费者 | 复查状态 |
|--------|------------|---------|
| #1: build_function_labels.py 加 privileged 处理 | `tripartite_model.json`（function_label 字段）; NPC AI 预烘焙管线; 疾病链路缺口复查 | ⏳ 待修复 |
| #2: build_tripartite_model.py 加 pathway_class 枚举校验 | tripartite_model.json（pathway_class 字段正确性） | ⏳ 待修复 |
| #3: generate_privileged_pathways() 加 warning 输出 | 开发者排查数据错误时 | ⏳ 待修复 |

## 变更追踪

本次为首次 trace，无上次对比。

## 统计
- 总 trace 行数: 5
- ✅ 完整: 0
- ⚠️ 有疑点: 4
- ❌ 有缺口: 1
- 待复查: 3

## 附加验证

### 结构一致性检查 ✅
- 61 条 pathway 全部 source/target 在 51 个 graph_nodes 中存在
- 8 个 pathway_class 在 doc/JSON/实际使用中完全一致
- EDR p≥0.10: 全部通过（61/61）
- 文档描述与 JSON _usage 字段一致

### 待实施项
- [ ] **BLOCKER**: `build_function_labels.py` — 新增 privileged_pathways 处理循环
- [ ] **WARN**: `build_tripartite_model.py` — 加 pathway_class 枚举校验 + 缺失节点/坐标 warning
- [ ] **INFO**: `脑功能层级模型.md` §20.2 — 生成规则表注明第 4 种通路
