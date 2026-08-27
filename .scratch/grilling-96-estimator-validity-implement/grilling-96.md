# Grilling #96 — 脚本 4 实现规划（sim_consciousness_v7_estimator_validity.py）

> Issue: [#98](https://github.com/verystrongdog/game/issues/98)（grilling）→ 前置 [实现 issue #96](https://github.com/verystrongdog/game/issues/96) | 维度: 管线（怎么造出来、怎么验证）| 状态: 🔄 追问中 | 前置: #95 estimator-validity 设计冻结（Q1-Q19）+ #97 cTE 变体冻结（Q1-Q6）| 输入: 用户逐题裁决 + ChatGPT 分享（t_6a9015fb…、t_6a9016db…）

## 话题

Grilling #96（实现 issue）的实现规划——把冻结设计（#95 Q1-Q19 + #97 Q1-Q6，estimator 集合 {plug-in, TE, cTE}）落成可运行的 `sim_consciousness_v7_estimator_validity.py`（脚本 4）。**implementation grilling，不重审 #95/#97 科学设计**；发现需重议科学定义处 → 标记设计越界。

## 铁律（#98 定案，Q0）

1. `sim_consciousness_v7_benchmark.py` 零改动（只读 import `make_benchmark_systems()`）
2. 复用既有 estimator stack / 原语，不借实现之名重新设计 estimator
3. 需重议 cTE 统计定义 → 标记设计越界，不在 #96 偷改

## 决策记录（Step 3 逐题）

### Q0（2026-08-28）话题边界 ✅ 定案

- **决策**：边界 = 管线维度 × 脚本 4 实现规划；implementation grilling（不重审 #95/#97 科学设计）；流程按 Q1-Q14 顺序（先锁数据与语义，再锁计算与工程）；收尾 = 决策树条目 → grilling 日志 → #96 issue body → ready-for-agent。
- 输入：ChatGPT 分享 t_6a9015fb…（Q0 确认 + Q1-Q14 顺序建议）；用户转发分享 = 采纳。

### Q1（2026-08-28）脚本职责与输入/输出边界 ✅ 定案（按 ChatGPT 分享修订）

- **决策**：脚本拥有（9 项）：
  1. 按冻结 benchmark system 与冻结参数（μ₀=Unif(Ω)、轨迹长度=N、无 burn-in）生成 synthetic trajectory——不重新定义动力学
  2. 观测扰动算子（固定序 `p_n→d→p_m→h`、缺失不拼接、不插值补齐）；**接口边界：扰动后观测轨迹是 estimator 的唯一输入，不得回读 full trajectory 或 exact Reach**
  3. 逐 repeat 观测 `Reacĥ_r` 动态候选对（候选全集不得由 exact Reach/full-state graph 预先提供）；|Reacĥ|/|Reach| 覆盖率日志；y′ 未观测→not tested；m_ij=0→not testable（不进 P/R/F1 负例分母）
  4. 三估计器 = 实验 estimator adapter（plug-in 调冻结原语+检验机制；TE 调 cs4 `transfer_entropy`；cTE 实现 #97 冻结计算/置换机制）——内部算法拆分归 Q5
  5. per-repeat estimator-vs-ground-truth evaluation
  6. 统计汇总与诊断：A_pair、边级 P/R/F1、bootstrap CI、置换检验/Bonferroni
  7. Stage A / Stage B 实验调度
  8. **evaluation-only ground-truth assembly**（含 h>0 的 component-connectivity projection）——红线：结果只流向 evaluation/statistics/reporting，不得流向 estimator
  9. 可追溯结果序列化与报告（细则归 Q12）
- 脚本不拥有：benchmark 定义及修改；Layer 0-3 理论定义；E_S^(1)/Diff/Int/SB/SM 原语重定义；新「观测版 CS′」理论；exact Reach 向 estimator 的任何输入通道；SM̂ 观测 do 近似；新 threshold/validity 参数；对已有 estimator 科学定义的修改。
- **架构不变量（#98 实现铁律）**：Estimator branch 只能消费 observation branch 的数据；ground-truth branch 只能用于 evaluation；二者不得在 estimator 计算阶段汇合。
- **文件结构**：单文件函数式（不拆第二模块），内部 12 分区：[1] frozen config [2] benchmark loading [3] trajectory generation [4] observation operator [5] exact ground-truth assembly [6] Reacĥ/candidate construction [7] estimator adapters [8] per-repeat evaluation [9] Stage A/B scheduler [10] statistics [11] serialization/reporting [12] CLI/checkpoint。
- CLI 参数/断点归 Q11-Q14；三层报告+序列化细节归 Q12。
- **⚠️ 事实修正 1（AI 核对，引用即读取铁律）**：ChatGPT 分享称「μ₀、T=64、无 burn-in 等参数由冻结设计决定」——**T=64 是 components 的 Diff 观察窗口（T_DIFF，sim_consciousness_v7_components.py :45），非轨迹长度**；脚本 4 轨迹长度 = N（梯度样本量 N∈{64,…,16384}，决策树 :3229 Q5）。
- **⚠️ 缺口标注（设计未操作化，非越界）**：c 梯度（{0.6,0.9}，机制层）冻结设计只有值+层属性，无实例化语义 → 实现需定义 c 变体系统构造方式，归 Q2 裁决。

### Q2（2026-08-28）单实验单元数据生命周期 ✅ 定案（按 ChatGPT 分享修订）

- **决策**：单单元 `(system, 梯度格, estimator, repeat)` 生命周期 8 步：
  1. seed = `hash(system, 梯度格, estimator, repeat)`（Q6）；rng = `Random(seed)`
  2. c 实例化（见 Q2a——存在冻结映射才构造变体，否则记录未实例化）
  3. ground-truth 侧（评估用）：`exact_kernel → edges_e1 → weak_components` → 𝒞_exact；h>0 → V_obs component-connectivity projection → truth
  4. 观测侧：full trajectory（μ₀=Unif、无 burn-in、长度=N）→ 扰动算子 `p_n→d→p_m→h` → 观测轨迹
  5. 逐 repeat：`Reacĥ_r` → 动态候选对（y′∉Reacĥ_r → not tested；m_ij=0 → not testable）
  6. estimator adapter（plug-in/TE/cTE）→ 边判定三值化 → Ĉ_obs 保守图 → 分量划分
  7. per-repeat 评估：A_pair + 边级 P/R/F1 + CS′̂（exact-primitive replay）
  8. 跨 repeat 汇总：A_pair 均值 ± bootstrap CI、成立域
- **不变量**：步 3 与步 4-6 严格分叉，永不汇合（Q1 铁律）。
- **⚠️ 实现事实记录（seed 含 estimator）**：不同 estimator 在同一 (system, grid, repeat) 下**不共享随机轨迹**；三估计器比较按冻结实验设计解释，**禁止在实现阶段改成 common-random-number pairing 减方差**（来源：决策树 :3230 Q6，seed=hash(...,estimator,repeat)）。

### Q2a（2026-08-28）c 梯度机制层实例化 ✅ 定案（按 ChatGPT 分享裁决）

- **决策**：
  | 方案 | 裁决 |
  |---|---|
  | ScaleRNG 插值 `0.5+(p−0.5)·c/0.9` | ❌ 不批准（无语义依据——无法区分耦合/噪声/初始化随机；#96 不得发明机制语义）|
  | 比例式 `p·c/0.9` | ❌ 不批准（向 0 收缩非向噪声收缩，机制语义不同）|
  | 逐系统 coupling mapping | ✅ 语义方向正确，但须已有冻结依据（不得在 #96 重审 20 个 step_fn）|
  | 无明确 mapping | ✅ 标记 `c not instantiated / blocked`，不自行补定义 |
- **新不变量（#98 铁律）**：**#96 不得通过 RNG 全局拦截、概率缩放或其他代理技巧为 c 创造新的机制语义。c 只能作用于已有明确机制层语义的参数；没有该语义就不实例化。**
- **确定性系统**：c 无作用 → 如实记录 **c-invariant / 平坦曲线**（实验事实非 bug）。
- **⚠️ 后果确认（AI 核对后标注，需用户显式认可）**：全项目 grep 确认**任何系统均无冻结的 coupling_parameter(system)→parameter(s) 映射**（决策树 :3229 只有值+层属性）→ **所有 c=0.6 格 blocked** → 阶段 A c 曲线 = 仅基线点（c=0.9）、阶段 B c×h 交互不可计算。c 梯度的机制层定义需另开设计（非 #96）。
- Step 2 命名修正：存在冻结映射 → 构造 c 变体；否则记录未实例化。

### Q3（2026-08-28）原语映射 ✅ 定案（按 ChatGPT 分享修订）

- **决策**：
  - 映射表（#96 行为）：benchmark systems → `make_benchmark_systems()` 只读 import；exact kernel/E_S^(1)/𝒞 → components 原语 import；exact Reach → **仅 coverage diagnostic**（唯一合法数据流：exact Reach → coverage diagnostic → report；禁止流向 candidate construction / estimator input / estimator-side decision）；trajectory/observation operator/Reacĥ/candidates/plug-in/cTE/CS′̂ replay/statistics/scheduling/serialization → #96 新写；TE → cs4 `transfer_entropy` 薄 adapter；**`components.py` 不修改；`benchmark.py` 不修改**。
  - **Q3a**：选 (b)——脚本 4 内联 projection kernel（CS′̂ replay 用），**不扩展 components.py**。约束：①只用于 CS′̂ exact-primitive replay ②与 evaluate() 的 projection/闭包语义逐项一致 ③注释标注对应既有逻辑 ④不改 components.py ⑤不包装成新全局 primitive ⑥不改变 evaluate() 行为。
  - **Q3b**：纯 Python（stdlib + 现有原语）；numpy 是否引入留 Q11，以实测瓶颈为依据——**先有正确 reference implementation，再做 acceleration**。
  - **Q3c**：`evaluate()` 整体不复用（component source 不同：exact edges vs Ĉ_obs 分量；复用会把结果错解释成 CS′̂）。
  - **新铁律（Q3）**：**基础原语库只读；#96 可以组合原语，但不得为了 #96 新增基础 API。**「复用铁律是优先复用既有语义和原语，不是为了消灭代码重复而扩大基础库 API」。
  - exact Reach 数据流与 Q1 branch invariant 一起列为代码 review 重点。

### Q4（2026-08-28）plug-in estimator 精确实现契约 ✅ 定案（按 ChatGPT 分享）

- **决策**：plug-in 判定状态机（逐有向边 (i,j)，逐 repeat）：
  - 候选边域 = 理论域全部有向对 (i,j), i≠j；**实际检验域服从 Q18**（从 Reacĥ_r 取条件对 {y, flip_i(y)}，仅排除定义域为空的情形）→ m_ij
  - 逐条件对：统计量 `D_obs = |P̂(X′_j=1|y) − P̂(X′_j=1|y′)|`（**是检验统计量，非边存在阈值**；不引入 log-odds/θ_valid）；检验 = 保持时间结构的标签置换，B_perm=999 固定 Monte Carlo（**不按样本量切换精确枚举**），`p = (1+#{D_b≥D_obs})/1000`（最小可报告 p=0.001，与 α=0.01 兼容）
  - 校正：α_ij = 0.01/m_ij（Bonferroni 边内族）；p ≤ α_ij → 条件对拒绝 H0
  - ∃ 聚合：族内任一拒绝 → directed edge **PRESENT**；否则 **ABSENT**；m_ij=0 → **NOT_TESTABLE**
  - **RNG 层级（修正）**：cell_seed → repeat_seed → estimator_seed → edge_seed → condition_pair_seed（层级派生，**不用全局 RNG、不按条件对索引独立重派生**）——可复现、无跨单元状态污染、可并行
  - **Q4c**：条件对进入检验需两组各 ≥1 outcome（0 outcome = 条件概率未定义 ≠ 少量 outcome = 高方差）；排除 → 不计入 m_ij
  - **Q4d**：plug-in 保留有向边 (i,j)；Ĉ_obs = present 有向边无向投影 → weak components；plug-in 有向边级 P/R/F1 仅**诊断**（cTE 承担主判，#97 Q6）
  - 术语统一：condition pair **被排除**（非「失败」）
  - **新铁律（Q4）**：**不得以样本量、方差、稀疏度或任何未冻结阈值过滤已定义的 condition pair；唯一允许排除的原因是条件概率定义域为空**（禁止 `if count < 5: continue` 类逻辑）。

### Q5（2026-08-28）TE/cTE adapter 接口与三值化 ✅ 定案（按 ChatGPT 分享）

- **决策**：
  - **Q5a**：cTE 每条有向边 (i,j) **一个**条件独立性检验 H0(i,j): cTE(i→j)=null；FWER family size=1 → α_edge=0.01；**不按 conditioning variables / condition pairs 再拆族**（拆族会改变 #97 设计）；cTE 与 plug-in **不得共用同一 correction 函数**
  - **Q5b**：cTE 用 log2（对齐 components entropy 惯例；无硬阈值 → 基只做正比例缩放，不影响置换排序与判定）；TE 保持 cs4 自然对数（THETA_TE=0.01 语义绑定）——**不为三估计器统一 entropy base**
  - **Q5c**：三判定函数**完全独立**（`plugin_edge_test` / `te_edge_test` / `cte_edge_test`），输出统一 `EdgeResult`；`m_ij`（family_size）**仅 plug-in 有定义，TE/cTE = null**（不得填 1 冒充）；**禁止 `generic_edge_test(statistic, threshold, correction, ...)` 参数化同构**
  - **not_testable 语义修正**：统一原则 = **仅当 estimator 所需数据对象为空/定义域不存在才产生 not_testable**（实现检查 `n_transition == 0`，不用 `N<64` 之类逻辑保证——观测算子 d/p_m/h 会降低实际可用 transition 数）；**不得因样本少/估计不稳定人为制造 not_testable**（与 Q4c 铁律一致）
  - **新铁律（Q5）**：**统一的是结果接口，不是统计判定语义。任何 estimator 不得通过通用 correction/threshold 函数被强行同构。**

### Q6（2026-08-28）EdgeResult / repeat-level schema ✅ 定案（按 ChatGPT 分享修订）

- **决策**：
  - **Q6a**：完整落盘每个 `system×grid×estimator×repeat` 的全部 EdgeResult（#95 可追溯铁律）；**不落 999 次 permutation 原始序列**（detail 存条件对数量/各对 D_obs/p 值/rejected/必要计数；permutation 原始值仅 debug 模式）
  - **Q6b**：c=0.6 blocked → **cell-level 元记录** `{system, grid, estimator, status:"blocked", block_reason:"no_frozen_coupling_mapping"}`，不生成 repeat、不进统计分母；**blocked ≠ failed ≠ not_testable**（设计不可实例化 ≠ 运行失败 ≠ 未检验）
  - **Q6c**：EdgeResult 保留 `estimator` 字段（可追溯性 > schema 最小化）
  - **schema 修订**：
    1. `statistic` + `statistic_name`（abs_delta_p / TE / cTE）——避免三估计器数值语义混淆
    2. `family_size`：plug-in=m_ij、cTE=1（逐边单检验 family）、TE=1（描述性 metadata，**不参与 TE 硬阈值计算**）；若坚持 Q5 的 m_ij=null 语义则用 `correction:"none"` 另标
    3. `n_outcomes` → `sample_info` 按 estimator 语义组织（plug-in: {n_condition_pairs, n_valid_condition_pairs} + detail 内逐对 {y, y_prime, d_obs, p_value, rejected}；TE/cTE: {n_transition}）——禁止 y/y′ 空字段对齐
    4. truth 存**实际边集**（`exact_directed_edges` 列表）不只数量；`n_obs_pairs` 明确区分 observed_state_pairs vs observed_transition_pairs
    5. replay 存 `present_directed_edges`——审计链 EdgeResult → present edges → 无向投影 → Ĉ_obs → components_hat → CS_hat 可定位
  - **状态字段**：`status ∈ {completed, blocked, failed}`，三者语义严格分离

### Q7（2026-08-28）A_pair 精确定义与 h 投影域 ✅ 定案（按 ChatGPT 分享）

- **决策**：
  - **Q7a**：无向化 = 任方向 present 即正边：`{a,b} present ⟺ (a→b) present ∨ (b→a) present`；真值表：present+absent→边、present+not_testable→边、absent+not_testable→无边、not_testable+not_testable→无边；not_testable 永不产生正边
  - **Q7b**：truth_same(a,b) = 完整 G_exact（含隐变量节点）弱连通（component-connectivity projection）；h=1 允许路径经隐变量但隐变量不作端点；D_h = C(|V_obs(h)|,2)；**禁止实现为「删隐变量→重算分量」**（那是仅可观测连通，非冻结语义）；**实现不变量：h 改变 A_pair 端点域，不改变 truth 图本身连通关系**
  - **Q7c**：A_pair_r 全量落盘；A_pair = (1/R)Σ A_pair_r；bootstrap B=1000、重采样单位=repeat、95% CI；**A_pair 无判定阈值**（0.9 仅 Stage B 报告 grid slice，非 validity criterion）
  - **数据一致性检查**：A_pair 的 evaluation domain D 由 `(system, h)` 固定决定，**与 Reacĥ_r/candidate pairs/not_testable 无关**；同 (system,grid,h) 下 32 个 repeat 的 D 必须相同（Reacĥ 决定 estimator 检验域，D 决定评估域，二者不得混——否则观测少→分母小→虚高）
  - **not_testable 与 A_pair**：即使边 not_testable，pair 仍在固定 D 中有 hat_same（由 present-edges-only 的 Ĉ_obs 分量成员决定）；**不得从 A_pair 分母删除**（与 edge-level P/R/F1 规则明确区分）
  - **新铁律（Q7）**：**A_pair 的 evaluation domain D 由 (system, h) 的可观测变量集合固定决定，与 Reacĥ_r、candidate pairs、not_testable 状态无关；任何 repeat 不得改变 A_pair 分母。**

### Q8（2026-08-28）P/R/F1 truth domain 与三值无向化 ✅ 定案（按 ChatGPT 分享修正）

- **决策**：
  - **Q8a**：h>0 有向 truth = `E_S^(1) ∩ (V_obs × V_obs)`（直接依赖边；经隐变量路径**不**产生有向边 truth）；与 A_pair 的 component-connectivity truth（含隐路径）两套语义在代码与报告中显式分离
  - **Q8b（修正，原推荐否决）**：无向化为**三值逻辑**——`present ⟺ 任一方向 present`；`absent ⟺ 两方向均 absent`；`not_testable ⟺ 其余情况`（absent+not_testable → not_testable，不得转 absent）；**无向 P/R/F1 tested 域 = 最终状态为 present 或 absent 的 pair**（not_testable 完全排除）；「正证据 OR、负证据必须双向 absent 共同证明」
  - **Q8c**：per-repeat 落盘——无向套 `metrics.undirected.{P,R,F1,n_candidate,n_tested,n_not_testable}`（**不用裸 metrics.P/R/F1**）；有向套 `directed_diag.{plugin,te,cte}`，cTE 有向 P/R/F1 标 `is_primary: true`（#97 Q6 主判），plug-in/TE 仅 diagnostic
  - **新铁律（Q8）**：**无向化是三值逻辑，不是简单的 tested-OR。正证据可以 OR，负证据必须由双向 absent 共同证明；任何 not_testable 都不得转化为 absent。**
  - 记录性质：Q8b 原草案**不写入决策树**，作为 grilling 中发现并纠正的实现风险记录。

### Q9（2026-08-28）Stage A 网格调度 ✅ 定案（按 ChatGPT 分享）

- **决策**：
  - **Q9a**：14 格 = **完整审计 grid cell**（n_executable + n_blocked = 14）；c=0.6 格留 blocked 元记录、不产生 repeat；**N_repeat = n_executable × 20 × 3 × 32**（非机械 20×3×14×32）；顺序 N→p_n→d→p_m→h→c，system×grid×estimator×repeat 固定遍历
  - **Q9b**：h=1 隐变量表 = **代码内预注册冻结常量**（Q13 来源注释；不可 CLI 覆盖/运行时修改/动态推断；不随 Reacĥ 变；**不随 estimator 变**——h 是 grid/system 条件，三估计器共用同一 V_obs）
  - **Q9c**：扰动 `p_n→d→p_m→h` 作用于**完整系统轨迹**（V_all 运行、μ₀=Unif(Ω) 不变、动力学不被 h 改变）；h 仅最后一步投影 V_obs → Reacĥ/候选对/estimator
  - **新铁律（Q9）**：**`d` 是观测 delay 语义，不是 burn-in；不得通过丢弃轨迹前缀实现（禁 `trajectory[d:]` 类写法）；无 burn-in，瞬态保留。**
  - **新铁律（Q9 调度）**：**实验结果只由 (system, grid, estimator, repeat) 的确定性 seed 决定，不依赖循环执行顺序或共享 RNG 状态；blocked cell 不消耗 RNG。**

### Q10（2026-08-28）Stage B 选格与局部全因子 ✅ 定案（按 ChatGPT 分享）

- **决策**：
  - **Q10a**：`select_stage_B(stageA_results) → selected_grids + trigger_log` 为**确定性纯函数**（输入固定→输出固定；不读人工配置/RNG/Stage B 结果；禁止 agent 手动加格）；trigger_log 落盘 `{rule, system, estimator, factor, trigger_level, selected_levels}`；多规则选中同一格 → union，不重复执行
  - **Q10b**：R2 仅 plug-in vs TE（冻结语义）；plugin↔cTE / TE↔cTE 分歧**不触发 R2**；cTE 在 R2 选中格上**同格执行**——「选格依据：plugin vs TE；执行 estimator：plugin+TE+cTE」分离（#97 cTE 扩展不得修改 #95 冻结的 Stage-B selection semantics）
  - **Q10c**：c×h → `status=not_computable, reason=c=0.6 blocked`；**禁止把 blocked 当缺失硬算交互 / 禁止 c=0.9 替代**；合法实验边界结果非失败
  - **Q10d**：H/L = 预注册档位集合机械端点（N:64/16384、p_n:0/0.20、d:1/4、p_m:0/0.50、h:0/1）；**不得因 Stage A 非线性 post-hoc 改端点**
  - **ΔA_pair 逐 estimator**：ΔA_plugin / ΔA_TE / ΔA_cTE 并列报告（不先平均三估计器）；**CI 仍以 repeat 为重采样单位**（不得把四端点 cell 均值当独立样本做误差传播）
  - **局部全因子**：R1-R3 选中档位**取并集** → 对应交互上做**全因子**（如 N 选中 [64,256,1024] × p_n 选中 [0,.05,.20] → 3×3=9 组合，非仅 diagonal）；baseline 与 Stage A 已有结果**复用不重跑**
  - **新铁律（Q10）**：**Stage B selection 是 Stage-A-only、deterministic、post-hoc-but-pre-registered 的纯函数；Stage B 结果不得反馈选格，blocked 不得被替代或插值。每个 estimator 独立计算自己的 ΔA_pair；cTE 同格执行但不改变 R1-R4 的 selection semantics。**

### Q11（2026-08-28）计算预算与执行策略 ✅ 定案（按 ChatGPT 分享）

- **决策**：
  - **Q11a**：per-cell 独立执行 + **即时落盘**（核心执行单位 = (system, grid, estimator) → repeat 0..31 → cell result 立即写盘，不累计内存）；CLI 子集（`--stage/--systems/--estimators/--repeat-range`）**只选择 job，不改变 job 的 seed/统计语义**（分片运行与整跑逐 repeat 完全一致）
  - **Q11b（有条件）**：numpy **先 micro-benchmark 再触发**（不做预先全面改写）——新增 benchmark-only 路径对比 Python reference kernel vs NumPy kernel（数值/p-value/判定一致性 + runtime + 内存）；收益明确后**仅向量化 cTE permutation 统计内层**，实验层（调度/seed/轨迹/扰动/Reacĥ/候选对/EdgeResult/metrics/序列化）保持纯 Python；**保留极小纯 Python `cte_reference(...)` 作 regression test**（小 N 少量置换下 NumPy 与 Python 的统计量+置换 p 值必须一致）
  - **Q11c**：multiprocessing，**job 粒度 = (system, grid, estimator, repeat-range)**（可控 worker 内存/细粒度断点恢复/大 N cTE 不长期霸占 worker）；worker 不共享 RNG/状态/执行顺序；**防 numpy 线程嵌套**（记录 n_workers + numpy_threads，优先 1 numpy thread/worker）
  - **Q11d**：**目标 = 当前单机完整合法 Stage A + Stage B ≤ 24h**；24h 是 reference target 非统计设计约束——超限时**报告预算超限，禁止改冻结参数**（B_perm 999→99、减 R/grid/候选域等一律禁止）
  - **可恢复执行（硬要求）**：cell 完成 → 原子写入 + `status=completed`；重启 skip completed、skip blocked、failed 允许 retry——与 Q6 的 completed/blocked/failed 闭环
  - **新铁律（Q11）**：①**性能优化不得改变冻结统计语义；禁止通过减少 R、B_perm、grid、candidate domain 或改变检验规则解决性能问题** ②**NumPy kernel 必须与纯 Python reference kernel 做数值/判定回归验证；NumPy 只进入统计内层** ③**实验 runner 必须可中断、可恢复；completed/blocked/failed 可区分，重复启动不得重跑已完成 cell。**

### Q12（2026-08-28）序列化 / data/sim_results/ ✅ 定案（按 ChatGPT 分享）

- **决策**：
  - **Q12a**：每 cell 一个 JSON + **可读确定性 `cell_id`**（如 `R_corr__N1024_pn0_d1_pm0_h0_c09__plugin.json`，非 hash 主文件名）；**完整规范化 grid 对象存 meta**（cell_id 是导航标识不是数据真相）；c=0.6 blocked 在对应位置生成 `{status:"blocked", reason:"no_frozen_coupling_mapping"}` cell 文件——14 审计格全部可枚举
  - **Q12b（细化，非二选一）**：**RepeatRecord = 唯一事实源；aggregation = 可重算缓存；summary = 可重建产物**——cell 完成时内联计算聚合（A_pair mean/bootstrap CI/无向有向 P/R/F1/CS′̂ 摘要）写入 cell，但 `--aggregate` 必须能从 repeat_records 无损重算（聚合 v1/v2/v3 可迭代）；bootstrap 不得把聚合当原始样本——存 `{n_repeats, mean, bootstrap:{B, ci_level, resampling_unit, ci}}`（禁只存 {A_pair: 0.8333}）
  - **Q12c**：三层数据链 runner → cell JSON → aggregation pass → summary JSON；summary pass = **只读消费者**（Stage B 依赖链 Stage A → R1-R4 → selection_log → Stage B）
  - **目录**：`MANIFEST.json / run_log.json / selection_log.json / stageA/<system>/<estimator>/<cell_id>.json / stageB/… / summary/{stageA_curves, stageB_interactions, validity_regions}.json`；cell JSON = `{schema_version, meta, status, repeat_records[], aggregation}`
  - **版本追踪**：`MANIFEST` = 实验定义版本（git_commit/script_version/parameter_registry_version/grid_definition_version/selection_rule_version/h_table_version/B/B_perm/R/alpha/numpy_enabled/numpy_kernel_version）；`schema_version` = JSON 数据结构版本（cell 内也带，非仅 MANIFEST）——二者语义分开
  - **新铁律（Q12）**：①**RepeatRecord 是实验事实源；aggregation 是可重算缓存；summary 是可重建产物。任何聚合或报告代码变更，不得要求重新运行昂贵的轨迹/置换实验。** ②**MANIFEST 追踪实验定义版本，schema_version 追踪数据结构版本，二者不得混为一谈。**

### Q13（2026-08-28）dry-run / 单元验收 / 完整验收 ✅ 定案（按 ChatGPT 分享）

- **决策**：
  - **Q13a**：脚本内 `--self-test`（不新增测试文件），分两类：①纯逻辑断言（三值化真值表/not_testable≠absent/无向化规则/h 投影/candidate pair 构造/m_ij=0/A_pair 分母/seed 派生）②数值统计回归（小数据 plug-in/TE/cTE reference/NumPy cTE、同 seed 同结果）
  - **Q13b（dry-run 两档）**：**D0 最小 smoke** = 1 系统 × 基线格 × 3 估计器 × 2 repeat × N=64（「能不能跑通」）；**D1 协议边界覆盖** = 少量预注册格覆盖 N=64、p_n>0、d>1、p_m>0、h=1、c=0.6 blocked（c=0.6 不执行 repeat，检查 status=blocked + reason）；D1 无需完整 Stage A——「D0 证明能跑，D1 证明关键协议分支跑对」
  - **Q13c（完整验收，5 组）**：①全审计格状态完整 ②**failed==0**（blocked≥0、not_testable≥0 为合法状态，**不得要求 not_testable==0、不得混入 failed**）③三层 summary 完整 ④seed 复现 + **repeat-range 拆分/合并逐字节一致**（0..31 一次 vs 0..7/8..15/16..23/24..31 四段合并——验证执行顺序无关，Q9 铁律）⑤**依赖文件零修改验收**：benchmark.py + components.py + cs4_test.py 运行前后 hash 不变（benchmark 硬要求；components/cs4 按 Q3a/Q3 只读冻结）；另含 n_tested/n_candidate 完整、not_testable≠absent、A_pair 分母固定
  - **新验收铁律（Q13）**：①**D0 证明「能跑」，D1 证明「关键协议分支跑对」** ②**完整实验中 failed==0；blocked 与 not_testable 均为合法状态，不得混入 failed** ③**#96 完成后 benchmark.py、components.py、cs4_test.py 必须保持零修改。**

### Q14（2026-08-28）异常、断点与重复运行行为 ✅ 定案（按 ChatGPT 分享）

- **决策**：
  - **Q14a**：cell 级异常——任一 repeat 失败 → 整 cell `failed`（存 `{status:"failed", error:{type,message,traceback,repeat}}` 诊断）；**completed cell 必须恰有 32 个 RepeatRecord + aggregation + status=completed**（不得以缺失 repeat 冒充事实源）；failed 整 cell retry
  - **Q14b**：partial **不续跑**、整 cell 重跑（seed 确定性保证重跑逐字节一致，无成本损失）；`running/partial/interrupted` 均非最终状态，恢复时统一按未完成 cell 重执行；**最终状态仅 `completed / blocked / failed`**
  - **Q14c**：收尾顺序 ①决策树条目 → ②grilling 日志（本文件）→ ③#96 issue body（实现合同，needs-triage → ready-for-agent）→ ④关闭 #98 + 总结评论 → ⑤同步检查（term_registry/memory/决策树；**不因同步制造新理论定义**——实现细节留在决策树+日志）
  - **新铁律（Q14）**：①**completed cell 必须包含完整 32 个 RepeatRecord；不得以缺失 repeat 的 partial cell 冒充事实源** ②**running/partial 不是最终结果状态；恢复时统一按未完成 cell 处理。最终状态仅 completed / blocked / failed** ③**恢复、重试、拆分执行均不得改变实验结果；结果只由冻结参数 + deterministic seed 决定。**

### 封板（2026-08-28，ChatGPT 分享 t_6a901cbc… 宣布 Q0-Q14 完成）

12 个越界点全堵死：不修改 benchmark/components/cs4；不创造 c=0.6 机制语义；exact truth 与 estimator 严格分叉；exact Reach 不泄漏给 estimator；not_testable ≠ absent；A_pair 分母固定；三 estimator 不共用统计判定逻辑；d ≠ burn-in；不因样本量/稀疏度过滤已定义 condition pair；Stage B 不用显著性筛选；参数超预算不偷改协议；seed 决定结果不由执行顺序决定。

## Step 4 写入验证表（2026-08-28）

| 决策 | 摘要 | 写入文件 | 位置 | 状态 |
|---|---|---|---|---|
| Q0-Q14 | 脚本 4 实现合同全量 | docs/决策树.md | #98 条目「决策（Q0-Q14）」 | ✅ 已验证 |
| Q0-Q14 | 决策日志 + 验证表 | .scratch/grilling-96-estimator-validity-implement/grilling-96.md | 全文 | ✅ 已验证 |
| 实现合同 | #96 issue body 更新 + 标签转换 | GitHub issue #96 | body + needs-triage→ready-for-agent | ✅ 已验证 |
| 关闭 | #98 关闭 + 总结评论 | GitHub issue #98 | 评论 + close | ✅ 已验证 |
| memory | 决策摘要 | memory/script4-estimator-validity-implementation-grilling-96.md | — | ✅ 已验证 |
| term_registry | 无新增（实现规划，关键术语已入库 #95/#97；D0/D1 等实现档位标签不入库） | data/term_registry.json | — | ✅ 已验证（无改动）|

### 一致性清扫（Step 4 🔥）

- grep `estimator-validity|脚本 4|sim_consciousness_v7_estimator_validity`：命中 决策树 #95/#97/#98 + 本日志 + v7 注记 —— 无旧文档冲突 ✅
- grep `c=0.6|c 机制层|blocked`：本批新增 blocked 语义仅出现在本日志/决策树新条目/issue —— 无活跃文档误用 ✅
- 本批无废弃概念/废弃数字/垃圾桶移动 ✅
- term_registry 定义变更：无（D0/D1/cell_id/EdgeResult 等实现层标识符按 Q14c 原则不入库）✅
- #95/#97 推迟项「脚本 4 实现 → #96」需加「→ 见 #98」标注 ✅（决策树写入时一并更新）

## 约束清单（CLAUDE.md）

- 复用现有 sim 常量/函数（cs4 transfer_entropy/THETA_TE、components 原语、benchmark make_benchmark_systems），不重复定义
- 新数值参数标注 [NEW]（如有）
- 单文件函数式、中文注释
- 纯学术研讨产物，不入游戏正典（#40/#93/#94/#95/#97 先例，六维状态不更新）
