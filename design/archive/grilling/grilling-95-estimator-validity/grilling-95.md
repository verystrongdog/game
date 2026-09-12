# Grilling #95 — #6 estimator-validity 完整实验（observation 轨深化）

> Issue: [#95](https://github.com/verystrongdog/game/issues/95) | 维度: 规则（纯学术研讨，不入游戏正典——#40/#93/#94 先例）| 状态: ✅ 设计完成（2026-08-27，脚本 4 实现另开 issue）| 前置: #94 模拟实现批次 ✅ + v7 §七 D9/D10 | 输入: 用户 ChatGPT 分享链接 ×20（t_6a8fc7d8… #94 收尾总结 + t_6a8fca50…~t_6a8fd23e… 逐题裁决）

## 话题

#94 推迟清单首位（决策树 :3206）——把脚本 3 的 observation 轨（#6 人脑数据 H_loop/H_linear）从「exact 轨标注 CS′」深化为**完整 estimator-validity 实验**：`F_known → 𝒞_exact → synthetic trajectory → Ĉ_obs`，测 **Ĉ_obs ≈ 𝒞_exact 的成立域**（样本量/噪声/时间分辨率/观测缺失/隐变量/耦合强度梯度）。v6 开放问题 #5「TE≠因果」落地为可测试问题（v7 §七 D10 H1）；服务 scaled observation 轨（n≫8）前置。

## 决策记录（Step 3 逐题）

### Q1（2026-08-27）系统范围 ✅ 定案

- **决策**：全部十类 20 系统（rep+ctl 全纳入）。
- 理由：estimator-validity 检验的是估计层本身的有效性，不应限定为 #6 的局部性质；20 系统全纳入才能判断 estimator 是否跨系统/跨类别保持有效；与脚本 3 判定层十类表面完整可比；rep/ctl 都纳入以排除对某类结构或控制条件的系统性偏差（来源：issue #95 Q1 + ChatGPT 分享 t_6a8fca50764c8191a8fd97e22dc68b81）。

### Q2（2026-08-27）目标量 ✅ 定案

- **决策**：(a) 目标量 = **结构恢复**（Ĉ_obs ≈ 𝒞_exact）；CS′̂ 作对照输出列，不参与 estimator-validity 主判定。
- 理由：两层误差分离可归因——Ĉ_obs 偏离 → 结构估计层；Ĉ_obs 正确而 CS′̂ 错 → 四要件/判据估计层；避免边估计失败与判据估计失败混成黑箱指标（来源：t_6a8fcb1e7a388191a454e2672bdf8879）。

### Q3（2026-08-27）估计器选型 ✅ 定案

- **决策**：(c) 双估计器——**plug-in 主估计**（估计 E_S^(1) 定义所需条件转移概率 P̂，保留原判定逻辑；统计检验阈值不得改变 E_S^(1) 语义）+ **TE/cTE 对照**（实测 v6 #5「TE≠因果」，尤其 XOR/交互依赖可见性）。
- 边界锁死：plug-in 的置信区间/置换检验属有限样本统计判定机制，不构成第二套结构定义（来源：t_6a8fcb87456c819199a10d231f752b8b）。

### Q4（2026-08-27）有效性判定准则 ✅ 定案

- **决策**：(c) 分层度量——**A_pair ∈ [0,1] 主判定**（变量对同分量关系一致性，连续，无 θ_valid；A_pair=1 严格成立域作报告结果）+ 边级 P/R/F1 诊断（解释 A_pair 升降来源）+ CS′̂ 对照（全链路偏差追踪）。
- 理由：边错≠分量错——边级假阳合并分量、假阴拆分分量，单一度量丢归因（来源：t_6a8fcc0e0d5c8191a2bbe84ad78caf68）。

### Q5（2026-08-27）梯度定义 ✅ 定案

- **取值**：N={64,256,1024,4096,16384}（×4 指数步进，log 轴等距）；p_n={0,0.05,0.10,0.20}；d={1,2,4}；p_m={0,0.20,0.50}；h={0,1}；c={0.6,0.9}。
- **分层**：p_n/d/p_m 作用于观测层（不改 F）；h 作用于观测投影可见性；c 直接改机制层——三类效应可分离。
- **策略**：不执行 720 格全因子；阶段 A = 六条单因素梯度扫描（基线 N=1024, p_n=0, d=1, p_m=0, h=0, c=0.9）；阶段 B = 关键格全因子（来源：t_6a8fcc5b67ec8191a8e1bca567f7f03f）。

### Q6（2026-08-27）统计机制 ✅ 定案（含关键修订）

- **决策**：R=32 独立重复/格；seed=`hash(system, 梯度格, estimator, repeat)` 确定性派生（完全可复现）；A_pair = 32 repeat 均值 ± 95% bootstrap CI（B=1000，**重采样单位 = 32 个独立 repeat，非轨迹内时间点**）；plug-in 差异检验 = **保持时间结构的条件/标签置换检验**；α=0.01 + 按实际执行检验族多重比较校正（Bonferroni 为预注册保守方案，不预写死检验总数）；TE/cTE 沿用既有 THETA_TE 等阈值；不新增 θ_valid。
- **修订**：否决「完全随机时间索引置换」——会同时破坏时间依赖结构，检验的零假设变成比「条件转移概率无差异」更强/不同的命题（来源：t_6a8fccb21b408191a5fcaa0597827a3a）。

### Q7（2026-08-27）CS′̂ 实现语义 ✅ 定案

- **决策**：(b) 结构估计 + 判据精确——CS′̂ = 先在估计分量 Ĉ_obs 上用 **exact 原语**计算四要件并合成裁决（「基于估计结构的 exact-primitive replay」）。
- 锁死：本批**不实现** Diff̂/Int̂/SB̂/SM̂ 全观测估计；**不制造** SM̂ 从纯观测近似恢复 do(M=m)（重蹈 TE≠因果）；全观测估计轨推迟为独立后续实验（来源：t_6a8fcd2044c88191873ed27d1f5f6d01）。

### Q8（2026-08-27）scaled observation 轨关系 ✅ 定案

- **决策**：(a) 不并入本批，保持独立后续实验——本批限定 n≤8 域，优先建立 estimator-validity 成立域；scaled 轨（n≫8 规模效应）与本批混合会破坏分层归因。
- **可复用接口**：plug-in/TE estimator、条件/标签置换检验、R=32、确定性 seed、bootstrap CI、A_pair、P/R/F1、exact-primitive replay、实验格与结果记录格式全部作为 scaled 轨基础设施；**不得因推迟而重设计/复制 estimator stack**。
- **启动前置**：本批完成 n≤8 成立域结论并形成可复现 baseline（成立域是实验结果非 θ_valid）（来源：t_6a8fcd59d7088191a5a0ee16740bf151）。

### Q9（2026-08-27）TE 对照精确形态 ✅ 定案

- **决策**：(a) 仅双变量 TE——复用 cs4 `transfer_entropy(source_past, target_past, target_future)`（plug-in 熵、lag-1、双变量）+ `THETA_TE=0.01`（cs4 :26），边判定 `TE(X_i→X_j) ≥ 0.01`。
- **cTE 不进本批**：cs4 未实现、条件集未冻结（条件化哪些变量 = 新自由度 → 变成另一项方法设计实验）；作后续独立变体推迟。
- **定位**：TE 是 **naive observational estimator baseline**，不赋予因果语义；TE 与 E_S^(1)/𝒞_exact 的一致/不一致均作为实测结果报告（来源：t_6a8fce1917fc8191ba765ba1a9b52b9d）。

### Q10（2026-08-27）trajectory 协议 ✅ 定案

- **决策**：(a) μ₀=Unif(Ω) 起步（v7 §五）+ **无 burn-in**（v7 §四 D4 Reach 含瞬态——丢弃前 B 拍改变观测状态集，违反定义语义）+ **R=32 逐轨迹独立估计**（各自 Ē→Ĉ_obs→A_pair，不跨 repeat 合并——合并使 bootstrap 失去 repeat-level uncertainty 语义）。
- 锁死：无最小状态计数阈值；瞬态状态有限样本高方差作为真实实验结果保留并报告（来源：t_6a8fce5fc3608191b7e2fe4b3a533cdc）。

### Q11（2026-08-27）实现形态 ✅ 定案

- **决策**：(a) 新建 `sim_consciousness_v7_estimator_validity.py`（脚本 4）——import 复用 `make_benchmark_systems()`（20 系统定义）、components 原语（System/evaluate/exact_kernel/edges_e1/weak_components）、cs4 `transfer_entropy/THETA_TE`；**benchmark.py 零改动**（#94 闭合产物，避免「benchmark 一套系统、estimator-validity 另一套」）。
- 新增仅限实验层：synthetic trajectory、观测扰动、plug-in、条件/标签置换检验、多重比较校正、A_pair、P/R/F1、bootstrap CI、exact-primitive replay、阶段 A/B 调度、结果序列化。
- 输出 `data/sim_results/`：每格保留 system/类别/rep-ctl/estimator/六梯度值/repeat/seed/A_pair mean/95% CI/edge P/R/F1/CS′̂/统计检验摘要，可追溯。
- **无失败线**：验收 = 协议完整执行 + 结果完整报告 + seed 可复现；「发现 estimator 不成立」也是有效实验结果（来源：t_6a8fcf64a32081918fe8551655fab268）。

### Q12（2026-08-27）阶段 B 选格规则 ✅ 定案

- **决策**：(a) 预注册四条机械规则（对每系统×每估计器独立判定），禁止事后自由选择关键格：

| 规则 | 操作性定义 |
|---|---|
| R1 下降区 | 相邻梯度档 A_pair 下降 ≥ 0.15 → 该档及 ±1 邻档 |
| R2 分歧区 | \|A_pair_plug−A_pair_TE\| ≥ 0.15 → 该档及 ±1 邻档 |
| R3 边界区 | 按预注册梯度增强方向（由每梯度预注册排序决定），A_pair 首次 1.0→<1.0 的档及 ±1 邻档 |
| R4 异常区 | 仅阶段 A 前冻结清单 {R_corr, N_bcast, F9, B_cpg, H_loop}——**覆盖保证非临时追加** |

- 锁死：0.15 是**阶段 B 选格规则**非 estimator-validity 判定阈值（不改变 Q4 无 θ_valid）；阶段 A 结果不得追加 R4 系统（新发现可在讨论中报告，不改变阶段 B 集合）（来源：t_6a8fcfece3c88191b38df796052aa8a5）。

### Q13（2026-08-27）隐变量 h 选取 + 比较域 ✅ 定案

- **决策**：(a) h=1 每系统预注册**机制相关**变量（阶段 A 前冻结，不可追加/替换/轮转）：F1→j1、F9→s、F8′→z1、B_cpg→x2、H_loop→c1、CA→格0、RL→s0、R_iid/F_fwd/C_comb/N_chain→末位变量。
- **ground truth 同步投影**：h>0 时 A_pair 仅在可观测对 C(|V_obs|,2) 上计算；truth = 完整 𝒞_exact 在 V_obs 上的 **component-connectivity projection**（两可观测变量若在完整 exact 结构中可经包含隐藏变量的路径连通 → 投影 truth 中同分量；隐藏变量本身不入估计变量域但连通作用保留）——非 induced subgraph；h=0 退化为 Q4 全图（来源：t_6a8fd0727a4081919a1c9bf1d5a87b4c）。

### Q14（2026-08-27）边聚合 + 多重比较检验族 ✅ 定案

- **决策**：(a) 逐边检验族 + ∃ 聚合——对候选边 (i,j)，其全部实际检验条件对构成独立族，边内 FWER ≤ α=0.01（α/m_ij），随后按 E_S^(1) 原始 ∃ 语义聚合（族内任一校正后拒绝 H0 → 判边存在）。
- 不做全局族：避免单条边判定额外依赖整个系统候选边数量（N_bcast 高扇出 → 规模/扇出效应与校正效应纠缠）。
- m_ij = 该边**实际进入统计检验**的条件对数量（非预固定 2^(n-1)）；不得事后依据结果选择条件对（来源：t_6a8fd0c529d4819185586a6573048aa7）。

### Q15（2026-08-27）阶段 B 结果后处理与报告 ✅ 定案

- **决策**：(a) 三层报告 + 预注册三组二因素交互——**N×p_n**（样本量×噪声精度权衡）、**d×p_m**（下采样×整拍缺失观测完整性耦合）、**c×h**（机制强度×可见性跨层交互）；预注册对象是问题不是结果，全部报告不以显著性筛选。
- 报告结构：①阶段 A 六条单因素曲线（20 系统×2 估计器）；②阶段 B 三交互的 ΔA_pair 效应量+方向+不确定度（不以显著性决定纳入）；③成立域汇总（每 system×estimator：A_pair=1 严格域、A_pair≥0.9 描述性宽域、plug-in/TE 分歧区）——**0.9 仅汇总切片非 θ_valid，报告中显式标注**（来源：t_6a8fd13c5e34819199e0805ddb804e64）。

### Q16（2026-08-27）网格生成 + 局部全因子定义 ✅ 定案

- **决策**：(a) 阶段 A = 六条单因素扫描共享基线 → 去重后 **14 格/系统/估计器**；±1 邻档越界 clamp、重复去重、按预注册梯度顺序排序；R4 不参与阶段 A 选格。
- 阶段 B 局部全因子：每交互因素用 R1-R3 选档集合（无规则触发 → 全档 fallback，保证预注册交互可计算）；三因素以上不扫。
- 主交互量：`ΔA_pair = [A(H,H)−A(H,L)]−[A(L,H)−A(L,L)]`（H/L = 各自预注册档位集合最高/最低档，**不得事后选择**）；非端点档保留为局部全因子诊断矩阵（来源：t_6a8fd1908db0819199b60446fb4e6657）。

### Q17（2026-08-27）观测扰动算子顺序 + 缺失拍处理 ✅ 定案

- **决策**：(a) 固定顺序 `p_n → d → p_m → h`：p_n 位翻转作用于完整真实轨迹 → d 下采样（选择被观测拍）→ p_m 整拍缺失（观测记录丢失）→ h 变量剔除（观测通道不存在）；算子只改观测层不修改 F。
- **缺失不拼接**：p_m 后 lag-1 条件对仅由**原始时间轴连续 (t,t+1) 且两拍均存在**的观测构成；缺失点两侧不得配对（防 X_t→X_{t+2} 被当成 lag-1）；d>1 时 lag-1 = 下采样后相邻观测记录（不重新解释为原始机制单步转移）；**不得重构/插值/补齐时间序列**（来源：t_6a8fd1d9a8808191a4b98705360eba44）。

### Q18（2026-08-27）plug-in 候选对来源 ✅ 定案

- **决策**：(a) 逐 repeat 观测 `Reacĥ_r` = 该 repeat synthetic observation 中实际出现过的去重状态集；对每个 y 按 E_S^(1) 单坐标翻转生成 y′，仅 y′ ∈ Reacĥ_r 时进入实际统计检验；未观测 y′ → 该对不检验并记录为未检验。
- **锁死**：exact Reach 不得提供给 estimator（隐性真值泄漏）——|Reacĥ|/|Reach| 覆盖率、未检验对清单仅事后诊断；m_ij=0 → 标记 **not testable**，不得当作「无边」；逐 repeat 独立（不跨 repeat 合并候选状态/样本）（来源：t_6a8fd20a19d881918265bf4943397d74）。

### Q19（2026-08-27）not testable 进 P/R/F1 与 A_pair 的规则 ✅ 定案（a′ 语义修订）

- **决策**：(a′) 边状态三值化 `present / absent / not_testable`；P/R/F1 **仅在 tested 边**计算（报告 n_tested/n_candidate 作 coverage 诊断）；A_pair 在**完整可观测对域** C(|V_obs|,2) 上计算，Ĉ_obs 用「已获正边证据的保守估计图」——not_testable 不提供正边证据（分量碎裂 → A_pair 下降 = 观测覆盖/估计不足造成的结构恢复损失，**非「未检=无边」**）；CS′̂ 同保守结构 replay；报告中显式区分 not_testable 与 absent。
- 修订动机：Q19 原 (a) 第 2 条「not testable 按不存在处理」与 Q18「未知≠负例」数学冲突——未检验边已被转换成负边；修订后未知不提供正边证据但保留于三值状态（来源：t_6a8fd23e4f5c8191b257e6d817123d6c）。

## Step 4 写入验证表（2026-08-27）

| 决策 | 摘要 | 写入文件 | 位置 | 状态 |
|---|---|---|---|---|
| Q1-Q19 | estimator-validity 实验设计全量 | design/decisions/ | #95 条目「决策（Q1-Q19）」 | ✅ 已验证 |
| 6 术语 | estimator-validity/Ĉ_obs/A_pair/synthetic observation 轨/not_testable/scaled observation 轨 | data/term_registry.json | terms（220 条） | ✅ 已验证 |
| 衔接注记 | v7 §七 D10 H1 落地 + 参数速查表补充（R/α/选格阈值） | reference/意识结构侧-下一阶段路线-v7.md | 头部 + §参数速查表 | ✅ 已验证 |
| 决策日志 | 本文件 | grilling-95.md | 全文 | ✅ 已验证 |
| memory | 决策摘要 | memory/estimator-validity-grilling-95.md | — | ✅ 已验证 |
| 实现排期 | 脚本 4 另开 issue | GitHub issue | [实现 issue] | ✅ 已创建 |

### 一致性清扫（Step 4 🔥）

- grep `estimator-validity|Ĉ_obs|A_pair|not_testable`：命中 决策树 #95 条目 + v7 注记/参数表 + 本日志 + term_registry —— 均为本批新增，无旧文档残留冲突 ✅
- grep `scaled observation`：决策树 #94 推迟项（→ 见 #95 本条目衔接）+ #95 条目 —— 无路径断裂 ✅
- 本批无废弃概念/废弃数字/垃圾桶移动 ✅
- term_registry 定义变更：无（6 术语为全新条目，未改既有术语定义）✅

## 约束清单（CLAUDE.md）

- 复用现有 sim 常量/函数（cs4 transfer_entropy/THETA_TE、components 原语、benchmark make_benchmark_systems），不重复定义
- 新数值参数标注 [NEW] #95：阶段 B 选格阈值 0.15（来源：A_pair 定义域 [0,1] 结构变化工程判据）；统计层 α=0.01（来源：Q6，Westfall & Young 1993 多重比较惯例）；R=32（Q6 工程/统计折中）
- 单文件函数式、中文注释（脚本 4 实现时遵守）
- 纯学术研讨产物，不入游戏正典
