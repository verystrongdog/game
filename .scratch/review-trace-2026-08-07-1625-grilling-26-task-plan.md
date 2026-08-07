# Review Trace: grilling-26-task-plan.md

> 审查日期: 2026-08-07 16:25 | 审查范围: `.scratch/grilling-26-task-plan.md`
> 方法: 符号执行 + 限界验证 | 前置检查: run_all_checks.py (5/6 passed, 1 known-expected fail)

## 前置输入
- [x] Layer 1 预检查: 6 validators, 5 passed, 1 failed (S4 is_design_node — #25 有意删除，非本次引入)
- [x] Layer 1.5 抽查: 跳过（本文件为任务计划而非设计规格，H1 引用均为已有文档，无新规则可供抽查）
- [x] 被引用文件自动拉入: [brain_regions.json](../data/brain_regions.json), [脑功能层级模型.md](../规则/技能树系统/脑功能层级模型.md)
- [x] validate_trash_isolation.py: ✅ 全部通过（238 活跃 md 文件无垃圾引用）
- [x] validate_cross_refs.py: 481 total, 480 passed, 0 blocker

## Trace Table

### §一 决策清单 — D1-D12（声明性，不触发 H1-H6）

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| T1 | D1 三体模型 | 旧 364 链路模型 | 引用<旧模型> | 架构替换 | 三体模型规范 | Task 2.1/2.2/3.1 | 旧模型全部迁移至垃圾桶 ✅ | ✅ |
| T2 | D3 CSTC 三通路 | Alexander 1986 文献 | 引用<文献> | 每环路 3 通路（GO/NO-GO/STOP） | 9 CSTC 通道 | Task 2.1 R1 | STN 缺失 → Task 1.1 补齐 | ⚠️ 见缺口 G3 |

### §二 功能剖面草案 — H2（类型定义）+ H6（表格数据）

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| T3 | function_profile JSON schema (Task 1.4) | §二 表格 → brain_regions.json | Dict<字段, 值> | 表格行 → JSON 嵌套对象 | `{primary_function: 文本, input_types: List<文本>, ...}` | build_tripartite_model.py, build_function_labels.py | — | ⚠️ 见缺口 G1 |
| T4 | input_types/output_types 值域 | §二 15 个剖面草案 | List<文本> (无约束) | 源 output_types ∩ 目标 input_types → 连接语义 | 枚举<signal_type> (未定义) | build_function_labels.py 交集计算 | 值域未受控 → 交集运算依赖精确字符串匹配 | ❌ 见缺口 G1 |
| T5 | timescale 字段 | §二 15 剖面 | 枚举<fast\|medium\|slow> | 无变换（属性字段） | 枚举<fast\|medium\|slow> | build_function_labels.py (连接时间粒度) | 3 值完整，无 null 处理声明 | ✅ |
| T6 | neurotransmitter_dominant 字段 | §二 15 剖面 | 枚举 (未定义完整值域) | 无变换 | glutamate(8) / GABA(4) / dopamine(2) / norepinephrine(1) | 文档参考 / 药物系统交互 | 是否允许多值（共释放）？当前均单值 | ⚠️ 见缺口 G4 |
| T7 | cstc_role 字段 | §二 + Task 2.1 R1 | 枚举<cortical_input\|striatal_gate\|pallidal_output\|thalamic_relay\|modulator\|none> | 按角色匹配构建 CSTC 环路 | CSTC 环路连接 | R1: cortex→striatum→pallidum→thalamus→cortex | 6 值完整。但同角色多实体时如何配对？ | ❌ 见缺口 G3 |
| T8 | gameplay_domain 字段 | D9 + §二 15 剖面 | 枚举<12 terms> | 源 domain × 目标 domain → 连接级域 | 连接 game effect 标签 | build_function_labels.py, NPC AI 预烘焙, 战斗结算 | 3/12 domains 在 batch 1 中未使用（预期，非缺口） | ⚠️ 见缺口 G5 |
| T9 | 15 剖面 → functional_id 映射 | brain_regions.json (70 fids) | 任务计划用 dk_name 级描述（如"NAcc"） | dk_name → 该 dk_name 下所有 functional_id | 每个 functional_id 一个 function_profile | 所有消费方 | dk_name 共享多个 functional_id 时，同 profile 还是分 profile？ | ⚠️ 见缺口 G2 |

### §三 任务分解 — H3（数据变换）+ H5（管道衔接）

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| T10 | R1 CSTC 闭合 | brain_regions.json cstc_role | 枚举 (见 T7) | 匹配 cortical_input→striatal_gate→pallidal_output→thalamic_relay→cortical_input | CSTC 连接列表 | tripartite_model.json cstc 段 | 同角色多实体 → 穷举配对？需 loop_id 分组 | ❌ 见缺口 G3 |
| T11 | R5 EDR 公式 | brain_regions.json mni_xyz | List<数值[3]> (MNI mm) | p = 0.85 × e^(−0.015×d); d = 欧氏距离 | 数值[0-0.85] | 阈值二值化 → 皮层-皮层连接 | 阈值未指定。d=0 时 p=0.85（同区自连接）→ 需排除 | ❌ 见缺口 G6 |
| T12 | R6 层级相邻 | brain_regions.json level | 数值[0-5] | 筛选 \|Δlevel\| ≤ 1 的皮层对 | 皮层-皮层候选对 | EDR 过滤前/后？（建议先层级筛再 EDR） | 脑干 level=0，但 R14 排除 → OK。L0 小脑 Cortex？ | ⚠️ 见缺口 G7 |
| T13 | R7 双向互惠 | R6 输出对 | 皮层连接对 (A,B) | 每对生成 A→B 和 B→A 两条 | 双向连接列表 | 合并入 corticocortical 段 | Markov 2013: 所有皮层-皮层连接双向。正确 | ✅ |
| T14 | R8 脑干广播 | brain_regions.json category, dk_name | 枚举<cortical\|subcortical\|brainstem> × 文本(dk_name) | LC→NE: 全皮层+L1 皮层; 中缝→5-HT: 全皮层; VTA/SNc→DA: 纹状体+PFC | 脑干广播连接 | tripartite_model.json brainstem 段 | "纹状体"=Putamen+Caudate+Accumbens-area? "PFC"=哪些 dk_name? | ❌ 见缺口 G8 |
| T15 | R9 STN 超直接 | STN (新实体) + Pallidum | function_profile(cstc_role=pallidal_output) | STN→GPi/SNr 每环路一条 | 9 条 STOP 通道（3 环路 × 3 通路的 STOP 组分） | CSTC 段 STOP 通路 | STN 实体尚不存在（Task 1.1 创建） | ⚠️ 依赖 Task 1.1 |
| T16 | Task 2.1 → 2.2 管道 | tripartite_model.json | Dict{segments, connections} | 2.1 输出 → 2.2 输入 | 含 function_label 的 JSON | Task 4.1 验证 | JSON schema 需在 2.1 中定义，2.2 中读取 | ✅（同文件管线，schema 自洽） |
| T17 | brain_regions.json 共享 dk_name 处理 | brain_regions.json (14 dk_names 有 >1 fids) | Dict<dk_name, List<functional_id>> | 同 dk_name 的 fids 是否共享 function_profile？ | 剖面分配策略 | Task 1.4 写入逻辑 | 任务计划未声明策略 | ❌ 见缺口 G2 |

### §四 文件清单 — H1（跨文件引用）

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| T18 | 垃圾桶迁移 9 文件 | tools/ (7 .py) + data/connectivity/ (2 .json) | 引用<文件路径> | git mv → 垃圾桶/ | 已迁移文件 | 一致性清扫 (Task 3.3) | 迁移后 grep 验证无残留引用 | ✅ |
| T19 | 新建文件依赖 | tripartite_model.json (生成物) | 引用<JSON> | 由 Task 2.1 + 2.2 生成 | 三体模型数据 | NPC AI 预烘焙管线 / 技能树可视化 / 战斗结算 | 暂不阻塞 — 下游消费者是未来任务 | ✅ |

---

## 缺口汇总

| # | 位置 | 严重度 | 描述 |
|----|------|--------|------|
| G1 | §二 + Task 1.4 | ❌ | **signal_type 受控词表缺失**：input_types 和 output_types 在各剖面中使用自由文本字符串（"motor_plan", "sensory_feedback", "thalamic_sensory_relay_VPL" 等），无统一受控词表。build_function_labels.py 依赖 `output_types ∩ input_types` 做交集匹配，自由文本必然导致匹配失败。**需定义受控 signal_type 枚举（预计 20-30 项）并重写所有剖面中的 input/output_types。** |
| G2 | §二 + Task 1.4 | ❌ | **dk_name 共享多 functional_id 时的剖面分配策略未定义**：14 个 dk_name 有 >1 functional_id（如 Accumbens-area=4, Hippocampus=2, superiortemporal=3）。任务计划用 dk_name 级描述"15 实体"，但 brain_regions.json 以 functional_id 为条目主键。需明确：同 dk_name 的多个 functional_id 是共享同一 function_profile 还是各写独立 profile？HippocampusCA1 vs CA3 功能不同（pattern completion vs separation），应分写；AccumbensShell vs Core 功能有差异（shell=emotional, core=motor interface），建议分写。 |
| G3 | §三 R1 + T7 | ❌ | **CSTC 环路路由规则缺失**：cstc_role 字段用 6 值枚举区分角色，但无法确定哪些实体属于同一环路。M1(cortical_input)、Putamen(striatal_gate)、Pallidum(pallidal_output)、Thalamus(thalamic_relay) 都标记了角色，但脚本如何知道 M1+Putamen 组成 somatic 环路而非 Caudate+M1？当前方案需：(a) 增加 loop_id 字段（somatic/cognitive/limbic）或 (b) 从已有 connectivity 数据推导环路成员。 |
| G4 | §二 T6 | ⚠️ | **neurotransmitter_dominant 值域未定义**：当前使用 glutamate/GABA/dopamine/norepinephrine 4 种。但 (a) 允许多值吗（如 VTA 同时释放 DA+GABA）？(b) serotonin 未出现（中缝核在 batch 2），但值域应预留。(c) acetylcholine（基底前脑）在 batch 2 需要。建议值域：glutamate, GABA, dopamine, norepinephrine, serotonin, acetylcholine, histamine, endogenous_opioid。 |
| G5 | §二 + D9 | ⚠️ | **gameplay_domain 使用分布不均**：batch 1 仅覆盖 9/12 domains（social_cognition/interoception/habit_learning 未用）。非缺口——对应实体在 batch 2（Insula=interoception, TPJ/Broca=social_cognition, Putamen habit 子剖面=habit_learning）。但任务计划应标注 batch 2 的 domain 补全路线。 |
| G6 | §三 R5 | ❌ | **EDR 连接阈值未指定**：p(connection) = 0.85 × e^(−0.015×d) 产生概率 0-0.85，需二值化阈值。Molnár et al. 2024 报告 binary connections AUC≥0.8。建议阈值锚定：p≥0.15（文献 EDR 拟合的 binary 分界）或 p≥0.10（宽松），需 grilling 确认。另外：d=0 时 p=0.85 须排除自连接（source==target）。 |
| G7 | §三 R6+R14 | ⚠️ | **CerebellumCortex 的层级归属模糊**：小脑皮层 category=subcortical, dk_name=Cerebellum-Cortex, level=0。R6 说 |Δlevel|≤1，R14 说无 dk_name 不作皮层-皮层。小脑有 dk_name，如果 level=0 则与 L1 皮层的 Δlevel=1，会被 R6 纳入。但小脑-皮层连接走的是小脑-丘脑-皮层通路（非直接皮层-皮层）。需明确排除或给小脑单独处理。 |
| G8 | §三 R8 | ❌ | **脑干广播的目标集需正式定义**："纹状体" = 哪些 dk_name？"PFC" = 哪些 dk_name？当前 brain_regions.json 无 lobe="striatum" 或 category="prefrontal" 字段。可能的实现：(a) 按 dk_name 硬编码列表（Putamen, Caudate, Accumbens-area 为纹状体；rostralmiddlefrontal, superiorfrontal, medialorbitofrontal, frontalpole, caudalmiddlefrontal, lateralorbitofrontal, parsopercularis 为 PFC）或 (b) 利用 function_profile.gameplay_domain 反向推导。方案 (b) 更优雅但依赖 Task 1.4 全部完成。 |

---

## 半径扩张 — 待复查

| 修复点 | 受影响消费者 | 复查状态 |
|--------|------------|---------|
| G1 signal_type 词表 | Task 2.2 build_function_labels.py, §二全部 15 剖面 | 待修复 |
| G2 dk_name→fid 剖面策略 | Task 1.4, brain_regions.json | 待修复 |
| G3 CSTC 环路路由 | Task 2.1 R1, function_profile.cstc_role | 待修复 |
| G6 EDR 阈值 | Task 2.1 R5, 皮层-皮层连接数 | 待修复 |
| G8 脑干广播目标集 | Task 2.1 R8, brainstem 广播连接 | 待修复 |

## 变更追踪
（首次审查，无上次缺口可比较）

## 统计
- 总 trace 行数: 19
- ✅: 5
- ⚠️: 7 (G4/G5/G7 + T2/T9/T15)
- ❌: 5 (G1/G2/G3/G6/G8)
- 待复查: 5

## 建议

1. **G1（signal_type 词表）是最高优先级阻塞项**——不解决则 build_function_labels.py 的交集匹配逻辑无法工作。建议在 grilling 中追加 1 题确定受控词表（预计 20-30 项），然后重写 15 剖面的 input/output_types。

2. **G3（CSTC 环路路由）次高优先级**——建议在 function_profile 增加 `cstc_loop` 字段（枚举<somatic\|cognitive\|limbic\|none>），替代从 cstc_role 推导环路的隐式逻辑。

3. **G2（剖面粒度）**建议策略：以 functional_id 为最小粒度写剖面，同 dk_name 的功能变体各自独立。CA1 vs CA3 功能不同，分开剖面是正确的。

4. **G6（EDR 阈值）**可在 grilling 中快速确认，或先实现再调参。

5. 任务计划整体结构合理，Phase 排序正确（数据→脚本→文档→验证），文件清单完整。
