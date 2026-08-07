# Review Trace: grilling-26-task-plan.md (v2)

> 审查日期: 2026-08-07 16:40 | 审查范围: `.scratch/grilling-26-task-plan.md` (v2)
> 方法: 符号执行 + 限界验证 | 前置检查: run_all_checks.py (5/6 passed, 1 known-expected fail)
> 上次 trace: `review-trace-2026-08-07-1625-grilling-26-task-plan.md`

## 前置输入
- [x] Layer 1 预检查: 6 validators, 5 passed, 1 failed (S4 is_design_node — #25 有意删除，非本次引入)。0 新 blocker。
- [x] Layer 1.5 抽查: 跳过（任务计划，新规则尚未写入源文件）
- [x] 被引用文件: brain_regions.json, signal_types.json（目标新建文件）

## v1→v2 缺口闭合验证

| v1 缺口 | v1 严重度 | v2 处理 | 闭合状态 |
|---------|----------|---------|---------|
| G1 signal_type 词表缺失 | ❌ | 新增 §二 19 子类受控词表 + Task 1.1 signal_types.json | ✅ 闭合 |
| G2 剖面粒度未定义 | ❌ | D8: functional_id 粒度 + mirror_of 共享。§三 剖面拆分至 20+2 条目 | ✅ 闭合 |
| G3 CSTC 环路路由 | ❌ | D9: function_profile 增加 cstc_loop 字段。§三 全部剖面含 cstc_loop | ✅ 闭合（见新缺口 N1） |
| G6 EDR 阈值 | ❌ | D11: p ≥ 0.10 天花板，功能筛选交 function_label 交集 | ✅ 闭合 |
| G8 脑干广播目标集 | ❌ | Task 2.1 R7: dk_name 硬编码列表（Putamen/Caudate/Accumbens-area + 7 prefrontal dk_names） | ✅ 闭合（见新缺口 N4） |
| G4 neurotransmitter 值域 | ⚠️ | 任务计划未改，实现时补（data/signal_types.json 不覆盖 neurotransmitter 词表） | ⚠️ 不变 |
| G5 gameplay_domain 覆盖不均 | ⚠️ | v2 新增 StriatumMatrix(habit_learning) — 3→2 domains 未覆盖 | ⚠️ 改善 |

## Trace Table（v2 新增/变更规则）

### §二 — signal_type 受控词表 (H2 类型定义)

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| T1 | signal_type 19 子类枚举 | 文献 (Albin 1989, Marder 2012, Bear 1994) | 引用<文献> | 4 大类 × N 子类 → 封闭枚举 | 枚举<19 子类> | §三 全部剖面 + build_function_labels.py 交集匹配 | 词表扩展：新增子类时需更新 signal_types.json + 所有剖面 | ✅ |
| T2 | excitation 6 子类 | — | 枚举<6> | 无 | 枚举<excitation/motor_command 等> | 皮层-皮层连接 + CSTC 皮层输入站 | social_intention 在 batch 1 无消费者（TPJ/Broca 在 batch 2）→ 预期 | ✅ |
| T3 | modulation 5 子类 | — | 枚举<5> | 无 | 枚举<modulation/reward_DA 等> | 脑干广播 | — | ✅ |
| T4 | gating 4 子类 | — | 枚举<4> | 无 | 枚举<gating/go_direct 等> | CSTC 环路 | stop_hyperdirect 仅 STN 输出 → 1 消费者，合理 | ✅ |
| T5 | plasticity 3 子类 | — | 枚举<3> | 无 | 枚举<plasticity/ltp_consolidation 等> | Hippocampus→广泛皮层, 学习事件 | context_code 在 CA3 output 和 Amygdala/CA1 input 均出现 → 有效交集 | ✅ |

### §三 — 功能剖面 (H2 类型定义 + H6 表格)

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| T6 | 剖面格式一致性 | §三 20 剖面表格 | 文本（裸名称）vs `category/subtype` (JSON) | 表格 → JSON | 格式不一致：表格用 `sensory_feature`，JSON schema 用 `excitation/motor_command` | Task 1.4 写入 | — | ⚠️ 见 N1 |
| T7 | cstc_loop 字段覆盖 | §三 全部剖面 | 枚举<somatic\|cognitive\|limbic\|none> | 同 loop 匹配角色节点 → CSTC 连接 | CSTC 环路连接 | build_tripartite_model.py R1 | Pallidum/Thalamus cstc_loop=none 但参与环路闭合 | ⚠️ 见 N2 |
| T8 | mirror_of 引用 | §三 LC_R, SNc_R | 引用<functional_id> | 运行时展开为被引用 profile | 共享 function_profile | build_tripartite_model.py（需支持 mirror_of 解析） | 引用目标不存在 → 脚本应报 FATAL | ✅ |
| T9 | STN 剖面 | §三 3.20 | Dict<function_profile> | 新增剖面 | STN profile | build_tripartite_model.py R8 (STN→Pallidum STOP) | STN 的 cstc_loop=none, cstc_role=none — STOP 通路独立于环路分组 | ✅ |
| T10 | StriatumMatrix vs Caudate 区分 | §三 3.15 vs 3.16 | 两个 functional_id 共享 dk_name=Caudate | 图节点 Caudate 挂 2 个 profile → 通信模式取并集 | Caudate 节点同时支持 cognitive_control + habit_learning | build_tripartite_model.py R10（同 dk_name 多 profile → 取并集） | 同 dk_name 多 profile 的正确合并逻辑需在脚本中实现 | ⚠️ 见 N3 |

### §四 — 任务分解 (H3 数据变换 + H5 管道)

| # | 规则 | 输入·来源 | 输入·类型 | 变换 | 输出·类型 | 输出·消费者 | 边界 | 判定 |
|----|------|----------|----------|------|----------|------------|------|------|
| T11 | R1 CSTC 闭合 (v2) | brain_regions.json cstc_loop + cstc_role | 枚举<cstc_loop> × 枚举<cstc_role> | 1. 按 cstc_loop 分组 2. 组内匹配 cortical_input→striatal_gate 3. striatal_gate→pallidal_output(任一) 4. pallidal_output→thalamic_relay(任一) 5. thalamic_relay→cortical_input(同 loop) | CSTC 环路连接列表 | tripartite_model.json cstc 段 | pallidal_output/thalamic_relay 的 cstc_loop=none 需通配匹配 | ⚠️ 见 N2 |
| T12 | R4 EDR (v2) | brain_regions.json mni_xyz | List<数值[3]> | p = 0.85 × e^(−0.015×d); d = MNI 欧氏距离; threshold: p ≥ 0.10 | 数值[0.10-0.85] | 二值化连接 + function_label 交集筛选 + gameplay_domain 筛选 | d=0 排除 | ✅ |
| T13 | R7 脑干广播 (v2) | brain_regions.json dk_name, category | Dict<源, List<目标 dk_name>> | LC→{Cortical∪L1}; 中缝→{Cortical}; VTA/SNc→DK_PFC(7)∪DK_STRIATAL(3) | 脑干广播连接 | tripartite_model.json brainstem 段 | DK_TARGETS 硬编码列表 10 项，新增皮层需手动更新 | ⚠️ 见 N4 |
| T14 | R10 同 dk_name 多 profile 合并 | brain_regions.json 同 dk_name 的多 functional_id | List<Dict<function_profile>> | 取所有 profile 的 input_types/output_types/gameplay_domain 的并集 | 图节点级 profile | build_tripartite_model.py + build_function_labels.py | 合并后的 gameplay_domain 可多值（如 Caudate=cognitive_control+habit_learning） | ⚠️ 见 N3 |
| T15 | Task 2.2 function_label 交集 (v2) | tripartite_model.json connection + signal_types.json | 源.output_types ∩ 目标.input_types (受控词表精确匹配) | 使用 signal_types.json 做精确字符串匹配（category/subtype 格式）→ 交集非空 → function_label; 交集空 → role:silent | function_label + gameplay_labels | tripartite_model.json (追加字段) | 词表外信号 → 匹配失败 → 标记 WARN | ✅ |
| T16 | Phase 1→2 依赖 | Task 1.1 (signal_types.json) + Task 1.4 (profiles 写入) | 引用<JSON> | Task 2.1/2.2 读取 signal_types.json + brain_regions.json (含 profile) | 脚本输入 | build_tripartite_model.py, build_function_labels.py | signal_types.json 缺失 → 脚本应 FATAL | ✅ |

---

## 缺口汇总

| # | 位置 | 严重度 | 描述 |
|----|------|--------|------|
| N1 | §三 剖面表格 vs Task 1.4 JSON schema | ⚠️ | **格式不一致**：剖面表格中 input_types/output_types 用裸名称（`sensory_feature`），Task 1.4 JSON schema 用 `category/subtype` 格式（`excitation/motor_command`）。两者引用同一受控词表，应统一格式。建议：剖面表格也用 `category/subtype` 以消除歧义。非阻塞——写入 JSON 时做映射即可。 |
| N2 | §三 Pallidum/Thalamus + Task 2.1 R1 | ⚠️ | **Pallidum 和 Thalamus 的 cstc_loop=none 但参与环路闭合**。脚本需要通配匹配逻辑：`cstc_role=pallidal_output` 匹配所有环路的 striatal_gate，`cstc_role=thalamic_relay` 关闭所有环路的 cortical_input。当前 R1 描述"按 cstc_loop 同组匹配"在 cstc_loop=none 时不成立。需在 R1 中显式定义通配行为。非阻塞——实现时可处理。 |
| N3 | §三 + Task 2.1 R10 | ⚠️ | **同 dk_name 多 functional_id 的并集逻辑未经 Trace**：Caudate 同时有 Caudate(cognitive_control) 和 StriatumMatrix(habit_learning) 两个 profile。R10 说"取并集"——但并集后的 gameplay_domain 是多值的（[cognitive_control, habit_learning]），这个多值如何影响 function_label 交集计算？非阻塞——实现时取并集后各自保留即可。 |
| N4 | Task 2.1 R7 | ⚠️ | **脑干广播硬编码 DK_TARGETS 列表 10 项**。新增/重命名 dk_name 时需手动更新此列表。建议脚本中加自检：启动时验证硬编码 dk_name 是否全部存在于 brain_regions.json，不存在 → WARN（不 FATAL——部分缺失仍可生成剩余广播）。 |
| N5 | §三 3.5 Amygdala | ⚠️ | **Amygdala 同时是 limbic CSTC 的 cortical_input 和 limbic loop 的调节器**。在原始 grilling D2 中，边缘环路被定义为"调节器，非动作通道"。但 amygdala 标记为 cstc_role=cortical_input + cstc_loop=limbic——这意味着它会参与 limbic CSTC 闭合（Amygdala→NAcc→Pallidum→Thalamus→Amygdala）。与 D2 的"调节器"定位是否一致？可能是正确建模（amygdala 确实通过 NAcc 参与 limbic CSTC，同时它的 subcortical shortcut 是独立调节），但建议在文档中说明。 |

---

## 变更追踪

| 上次缺口 | 本次状态 | 备注 |
|---------|---------|------|
| G1 signal_type | ✅ 闭合 | §二 新增 19 子类受控词表 |
| G2 剖面粒度 | ✅ 闭合 | D7+D8: functional_id 级 + mirror_of |
| G3 CSTC 路由 | ✅ 闭合 | D9: cstc_loop 字段（N2 为衍生 ⚠️ 非阻塞） |
| G4 neurotransmitter 值域 | ⚠️ 不变 | 非阻塞，实现时补 |
| G5 gameplay_domain 覆盖 | ⚠️ 改善 | v2 新增 habit_learning |
| G6 EDR 阈值 | ✅ 闭合 | D11: p ≥ 0.10, 功能筛选交 function_label |
| G7 Cerebellum 层级 | ⚠️ 不变 | 非阻塞，实现时排除 |
| G8 脑干广播目标 | ✅ 闭合 | R7: dk_name 硬编码列表（N4 为衍生 ⚠️） |

## 统计
- 总 trace 行数: 16
- ✅: 9
- ⚠️: 5 (N1/N2/N3/N4/N5)
- ❌: 0
- 待复查: 0

## 建议

v2 无 ❌ 阻塞项。5 个 ⚠️ 均为实现级注意事项，不阻塞编码启动：

1. **N1** — JSON 写入时做 category/subtype 格式转换即可，不影响数据结构设计
2. **N2** — cstc_loop=none 的通配匹配是脚本实现细节，在 build_tripartite_model.py 中用一条 `if` 处理
3. **N3** — 同 dk_name 多 profile 合并后各自保留，不影响 function_label 计算
4. **N4** — 硬编码列表自检属于防御性编程优化建议
5. **N5** — Amygdala 双重角色在文档中说明即可

**可以启动实施。**
