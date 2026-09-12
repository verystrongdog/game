# 设计决策树 — 编号轮次 — 引擎实施

> 按编号记录的引擎实施批次：#91 console / #100-#104 模拟与接口 / #106-#111 fail-fast 与插件化。
>
> **本文是历史档案**：只追加、不改旧条目。设计文档 = 当前状态；这里 = 怎么走到这里的。
> 总索引见 [README](README.md)。

---

## [Grilling] #6 estimator-validity 完整实验 — observation 轨深化（结构恢复成立域）(2026-08-27，Q1-Q19)

> Issue: [#95](https://github.com/verystrongdog/game/issues/95) | 维度: 规则（纯学术研讨，不入游戏正典——#40/#93/#94 先例）| 状态: ✅ 执行完成（2026-08-27）| 前置: #94 模拟实现批次 ✅ + v7 §七 D9/D10 | 输入: 用户 ChatGPT 分享链接 ×20（t_6a8fc7d8… #94 收尾总结 + t_6a8fca50…~t_6a8fd23e… 逐题裁决）

### 话题

决策树 :3206 #94 推迟清单首位的「脚本 3 observation 轨深化」——把 H_loop/H_linear 的 exact 轨标注（`evaluate()` 直接算 CS′）深化为**完整 estimator-validity 实验**：`F_known → 𝒞_exact → synthetic trajectory → Ĉ_obs`，测 **Ĉ_obs ≈ 𝒞_exact 的成立域**。v6 开放问题 #5「TE≠因果」由此从论断落地为可测试问题（v7 §七 D10 H1），并直接服务 v7 §五「Diff̂ 属统计层」接口。

### 决策（Q1-Q19，逐条对照写入）

- **Q1 范围**：全部十类 20 系统（rep+ctl 全纳入）。有效性是估计层性质而非 #6 局部性质；与脚本 3 判定层十类表面可比；rep/ctl 都测排除系统性偏差
- **Q2 目标量**：结构恢复（Ĉ_obs ≈ 𝒞_exact）为主目标；CS′̂ 作对照输出列——两层误差分离可归因（A_pair 错→结构层；A_pair 对而 CS′̂ 错→判据层）
- **Q3 估计器**：plug-in 主（估计 P̂ 后套用原 E_S^(1) 判定逻辑，非第二套定义）+ TE/cTE 对照（实测 v6 #5）
- **Q4 判定量**：A_pair ∈ [0,1] 主判（变量对同分量一致性，连续无 θ_valid）+ 边级 P/R/F1 诊断 + CS′̂ 对照；A_pair=1 严格域作报告结果
- **Q5 梯度**：N={64,256,1024,4096,16384}、p_n={0,0.05,0.10,0.20}、d={1,2,4}、p_m={0,0.20,0.50}、h={0,1}、c={0.6,0.9}；p_n/d/p_m 观测层、h 可见性、c 机制层；实验策略 = 阶段 A 六条单因素扫描（基线 N=1024,p_n=0,d=1,p_m=0,h=0,c=0.9）+ 阶段 B 关键格全因子
- **Q6 统计机制**：R=32 独立重复/格；seed=`hash(system, 梯度格, estimator, repeat)` 确定性派生；A_pair = 32 repeat 均值 ± 95% bootstrap CI（B=1000，重采样单位=repeat 非时间点）；plug-in 差异检验 = **保持时间结构的条件/标签置换**（否决完全随机时间置换），α=0.01 + 按实际检验族多重比较校正；α 属统计层参数不改 E_S^(1)
- **Q7 CS′̂ 语义**：(b) 结构估计 + 判据精确——CS′̂ = 在 Ĉ_obs 上用 exact 原语重放四要件（「基于估计结构的 exact-primitive replay」）；不实现 Diff̂/Int̂/SB̂/SM̂ 全观测估计、不制造 SM̂ 观测 do 近似（避免重蹈 TE≠因果）；全观测估计轨推迟
- **Q8 scaled 轨**：不并入本批（规模效应与估计器失效混淆破坏归因）；本批产出 estimator stack 为 scaled 轨可复用基础设施；启动前置 = 本批完成 n≤8 成立域结论（成立域是实验结果非 θ_valid）
- **Q9 TE 精确形态**：仅双变量 TE——复用 cs4 `transfer_entropy`（plug-in 熵、lag-1）+ `THETA_TE=0.01`，边判定 `TE(X_i→X_j)≥0.01`；cTE 不进本批（条件集未冻结=新自由度，作后续独立变体）；TE 定位 = naive observational estimator baseline，不赋予因果语义
  **🔧 修正 (2026-08-27, 104624b):** Q9「cTE 不进本批」被 Grilling #97 闭合后修正——cTE 变体设计冻结（#97 Q1-Q6：全条件 `cTE(X_i→X_j)=I(X_{i,t−1};X_{j,t}|X_{∖{i},t−1})`、置换检验无硬阈值（α=0.01 逐边族 FWER）、A_pair 三估计器同格（plug-in/TE/cTE）、有向边级 P/R/F1 方向诊断），实现并入脚本 4（#96，estimator 集合 {plug-in, TE, cTE}）。根因：#95 Q9 推迟理由（条件集未冻结=新自由度）已被 #97 Q1 全条件冻结解决（条件集由结构决定 V∖{X_i}，对齐 E_S^(1) 全状态条件语义）；#95 Q8「不得重设计/复制 estimator stack」支持并入而非另开脚本
- **Q10 trajectory 协议**：μ₀=Unif(Ω) 起步（v7 §五）；**无 burn-in**（v7 §四 D4 Reach 含瞬态）；R=32 逐轨迹独立估计（Ē→Ĉ_obs→A_pair 各自独立，不跨 repeat 合并）；无最小状态计数阈值（瞬态高方差如实上曲线）
- **Q11 实现形态**：新建 `sim_consciousness_v7_estimator_validity.py`（脚本 4），import 复用 `make_benchmark_systems()`/components 原语/cs4 `transfer_entropy`；**benchmark.py 零改动**（#94 闭合产物）；输出 `data/sim_results/` 可追溯 system/estimator/梯度格/repeat/seed；**无失败线**（验收=协议完整+报告完整+可复现）
- **Q12 阶段 B 选格**：预注册四条机械规则（防 post-hoc 选择）——R1 相邻档 A_pair 下降≥0.15、R2 |A_pair_plug−A_pair_TE|≥0.15、R3 按预注册梯度增强方向首次 1.0→<1.0、R4 仅预注册系统清单 {R_corr, N_bcast, F9, B_cpg, H_loop}（阶段 A 结果不得追加）；0.15 是选格规则非有效性阈值
- **Q13 隐变量 h**：h=1 每系统预注册机制相关变量（F1→j1、F9→s、F8′→z1、B_cpg→x2、H_loop→c1、CA→格0、RL→s0、其余→末位）；ground truth = 完整 𝒞_exact 在 V_obs 上的 **component-connectivity projection**（可经隐变量路径连通保留，非 induced subgraph）；A_pair 仅在 C(|V_obs|,2) 可观测对上计算；h=0 退化为 Q4 全图
- **Q14 边聚合 + 多重比较**：逐边检验族（候选边 (i,j) 的全部实际检验条件对构成独立族，边内 FWER≤α=0.01 即 α/m_ij）+ ∃ 聚合（族内任一校正后拒绝 H0 → 判边存在）；不做全局族（规模/扇出效应与校正效应纠缠）；m_ij = 实际检验条件对数，不得事后筛选
- **Q15 报告结构**：三层——阶段 A 六条单因素曲线（20 系统×2 估计器）；阶段 B 预注册三交互 N×p_n / d×p_m / c×h 的 ΔA_pair 效应量+方向+不确定度（预注册对象是问题不是结果，不以显著性筛选）；成立域汇总（A_pair=1 严格域、A_pair≥0.9 描述性宽域、plug-in/TE 分歧区）——0.9 仅汇总切片非 θ_valid
- **Q16 网格生成**：阶段 A = 六曲线共享基线去重后 **14 格/系统/估计器**；±1 邻档越界 clamp、重复去重、按预注册梯度顺序排列；阶段 B 局部全因子 = 各因素 R1-R3 选档集合两两组合（无规则触发因素用全档），三因素以上不扫；主交互量 `ΔA_pair = [A(H,H)−A(H,L)]−[A(L,H)−A(L,L)]`（H/L=预注册档位集合端点，不得事后选择）；非端点档保留为诊断矩阵
- **Q17 观测扰动序**：固定 `p_n → d → p_m → h`（p_n 位翻转作用于完整真实轨迹 → d 下采样 → p_m 整拍缺失 → h 变量剔除）；**缺失不拼接**——lag-1 条件对仅由原始时间轴连续且两拍均存在的 (t,t+1) 构成；d>1 时 lag-1 = 下采样后相邻观测记录（非原始单步转移）；**不得重构/插值/补齐时间序列**
- **Q18 候选对来源**：逐 repeat 观测 `Reacĥ_r`（该 repeat 实际出现过的去重状态集）构造动态候选对；y′ 未观测 → 该对不检验并记为未检验；m_ij=0 → **not testable ≠ 负例**；exact Reach 仅进评估/诊断侧，**不得提供给 estimator**（防真值泄漏）；|Reacĥ|/|Reach| 覆盖率入日志
- **Q19 边状态三值化**：`present / absent / not_testable`；P/R/F1 仅在 tested 边计算（报告 n_tested/n_candidate）；A_pair 在完整可观测对域上计算，Ĉ_obs 用「已获正边证据的保守估计图」（not_testable 不提供正边证据 → 分量碎裂 → A_pair 下降 = 观测覆盖损失，非「未检=无边」）；CS′̂ 同保守结构 replay；报告中显式区分 not_testable 与 absent

### 受影响文件

- `data/term_registry.json`（6 术语入库：estimator-validity/Ĉ_obs/A_pair/synthetic observation 轨/not_testable/scaled observation 轨）
- `design/decisions/`（本文）
- `reference/意识结构侧-下一阶段路线-v7.md`（衔接注记 + 参数速查表补充：选格阈值 0.15、α=0.01、R=32）
- `../设计归档/grilling/grilling-95-estimator-validity/grilling-95.md`（决策日志 + 写入验证表）
- memory（`estimator-validity-grilling-95.md`）

### 相关决策树条目对接

- :3206 #94 推迟项「脚本 3 observation 轨深化」→ 本条目完成（Q1-Q19）
- :3141 v7 D10 H1（synthetic observation / estimator-validity benchmark）→ 本条目落地
- :3140 v7 D9 A1（observation 轨报告估计值+不确定度+estimator validity，不触发失败线）→ Q4/Q11 落地
- :3181 #94 D2（exact_kernel 唯一派生，n≤8 exact 轨）→ 本批 ground truth 侧（𝒞_exact），估计侧不访问
- :3182 #94 D3（do 干预原语、退化条款）→ Q7（exact-primitive replay 用 exact do-kernel）

### 推迟

- **脚本 4 实现**（`sim_consciousness_v7_estimator_validity.py`）→ 已开实现 issue（设计冻结，实现待排期）→ **见 [#97](https://github.com/verystrongdog/game/issues/97)（实现并入 cTE，estimator 集合 {plug-in, TE, cTE}，[#96](https://github.com/verystrongdog/game/issues/96) scope 扩展）→ 实现规划完成，见 [#98](https://github.com/verystrongdog/game/issues/98)（2026-08-28，实现合同冻结，#96 转 ready-for-agent）**
- scaled observation 轨（n≫8 采样估计，D 条款；启动前置 = 本批成立域结论）→ **见 #97 分拣（维持阻塞）**
- cTE 变体（条件集未冻结，独立方法变体）→ **已完成设计，见 [#97](https://github.com/verystrongdog/game/issues/97)（Q1-Q6 冻结）**
- 全观测估计版 CS′̂（Diff̂/Int̂/SB̂/SM̂ + SM̂ 观测 do 近似——撞 TE≠因果，独立后续轨）→ **见 #97 分拣（维持独立后续轨）**
- SelfRep 充分定义（R-B 仅为必要条件，v7 §六，保留）→ **见 #97 分拣（维持，另开 grilling）**
- 高阶依赖 E^(k)/超图（anomaly-triggered，保留）/ 任务化 μ₀（保留）/ 连续状态空间 Reach（定义域外，保留）→ **见 #97 分拣（维持原状态）**

---

## [Grilling] 意识结构侧推迟清单分拣 + cTE 变体设计 (2026-08-27，Q1-Q8)

> Issue: [#97](https://github.com/verystrongdog/game/issues/97) | 维度: 规则（纯学术研讨，不入游戏正典——#40/#93/#94/#95 先例）| 状态: ✅ 执行完成（2026-08-27，cTE 实现并入 #96）| 前置: #95 estimator-validity 设计冻结（Q1-Q19）+ v7 §七 D9/D10 | 输入: 用户逐题裁决（Q1-Q8）

### 话题

处理 #95 推迟清单（8 项）——逐项分拣裁决状态；随后完整设计首个可开题项 **cTE 变体**（#95 Q9 明示"条件集未冻结 = 新自由度，作后续独立变体"）。

### 分拣裁决（Q7，8 项）

- **脚本 4 实现** → 排期 #96，本次并入 cTE（estimator 集合 {plug-in, TE, cTE}）
- **scaled observation 轨**（n≫8）→ 维持阻塞（启动前置 = 脚本 4 成立域结论，#95 Q8 锁死）
- **cTE 变体** → 本次开题设计（Q1-Q6 冻结，见下）
- **全观测估计版 CS′̂**（Diff̂/Int̂/SB̂/SM̂）→ 维持独立后续轨（SM̂ 观测 do 近似撞 TE≠因果，#95 Q7）
- **SelfRep 充分定义** → 维持，另开 grilling（R-B 仅为必要条件，v7 §六）
- **高阶依赖 E^(k)/超图** → 维持 anomaly-triggered（v7 §八 B）
- **任务化 μ₀ 实验轨** → 维持（v7 §五）
- **连续状态空间 Reach** → 维持定义域外（v7 §四）

### 决策（Q1-Q6，cTE 变体设计）

- **Q1 条件集（D1）**：全条件 `cTE(X_i→X_j) = I(X_{i,t−1}; X_{j,t} | X_{∖{i},t−1})`——Z = 除 X_i 外的全部变量 lag-1 过去（含 X_j 自身过去），条件集由结构决定（V∖{X_i}）。对齐 E_S^(1) 全状态条件语义（P_F(X′_j|y)）；一阶 Markov 下"当前全状态 y"与"lag-1 全状态 X_{t−1}"为同一条件事件，条件集全为过去变量不引入碰撞器问题。否决：父集选择（新自由度）、空条件（=双变量 TE 重复）、敏感性双轨
- **Q2 判定机制（D2）**：与 plug-in 同机制——保持时间结构的置换检验（置换 X_{i,t−1} 时间序列、保留其余结构）+ α=0.01 逐边族 FWER（#95 Q6/Q14 复用）；**无硬阈值**（THETA_TE=0.01 是双变量语义，条件化压低熵值后直接复用无语义依据）；边状态三值化（#95 Q19）；cTE 原始值仅诊断列。否决：硬阈值、双轨
- **Q3 主目标（D3）**：A_pair 主判（#95 Q2/Q4 框架不动），plug-in/TE/cTE **三估计器同格对比**（科学问题 =「条件化是否改善结构恢复」）+ 附加诊断 = cTE 有向边 vs E_S^(1) 有向边方向一致性（E_S^(1) 边 (i,j) 有向；v6 #5「TE≠因果」深入验证自然发生）。否决：v6 #5 实证专线、有向边 P/R/F1 并列主判
- **Q4 网格（D4）**：全网格 20 系统 × 阶段 A 14 格 × 阶段 B 局部全因子（#95 Q5/Q12/Q16 机械规则对每 system×estimator 独立判定，cTE 同格）；计算预算锚定：n≤8 全条件直方图桶数 2^(n+1) ≤ 512 可承受。否决：仅阶段 A、子集系统
- **Q5 实现形态（D5）**：并入 #96——闭合后修正 #95 Q9（Step 6：issue #95 评论 + 本条目修正行）+ #96 scope 扩展一次实现。依据 #95 Q8「不得重设计/复制 estimator stack」；#96 尚未实现零返工。否决：另开实现 issue（脚本 5）、设计入档实现暂缓
- **Q6 方向诊断（D6）**：有向边级 P/R/F1——#95 Q19 三值框架扩展方向维度，每条有向候选边 (i,j) 独立判定（exact 侧 truth = (i,j)∈E_S^(1)；估计侧 = cTE 置换检验拒绝 H0）；无向对但方向错 = (i,j) FN + (j,i) FP，无需额外定义。否决：方向条件概率 P(方向对|边在)、仅内部核对
- **协议复用声明（非决策）**：#95 Q10（trajectory 协议）/Q13（h 投影）/Q15（阶段 B 报告）/Q17（扰动序）/Q18（候选对来源）机械扩展，cTE 同格适用

### 受影响文件

- `design/decisions/`（本文：#97 条目 + #95 Q9 修正行（Step 6）+ #93/#94/#95 推迟项「→ 见 #97」标注）
- `data/term_registry.json`（4 术语入库：TE/cTE/plug-in/E_S^(1)，224 条）
- `reference/意识结构侧-下一阶段路线-v7.md`（头部衔接注记 + §七「cTE 变体（Grilling #97）」小节 + 参数速查表补充 3 行）
- `../设计归档/grilling/grilling-97-cte-variant/grilling-97.md`（决策日志 + 写入验证表）
- memory（`意识结构侧推迟清单与cTE变体-grilling-97.md`）
- GitHub：#95 闭合后修正评论（Step 6）+ #96 scope 扩展评论

### 相关决策树条目对接

- :3261-3268 #95 推迟清单 → 本条目分拣完成（各项加注「→ 见 #97」）
- :3233 #95 Q9「cTE 不进本批」→ 本条目闭合后修正（Q1-Q6 冻结，实现并入 #96）
- :3232 #95 Q8（scaled 轨不并入 + estimator stack 复用铁律）→ Q5 实现形态依据
- :3137 v7 D4 S1（一阶边边界）→ Q1/Q6 对齐 E_S^(1) 全状态条件语义

### 推迟

- **脚本 4 实现**（`sim_consciousness_v7_estimator_validity.py`）→ [#96](https://github.com/verystrongdog/game/issues/96) 实现排期（本批设计已冻结，含 cTE 扩展）→ **实现规划完成，见 [#98](https://github.com/verystrongdog/game/issues/98)（2026-08-28，实现合同冻结，#96 转 ready-for-agent）**
- scaled observation 轨（n≫8）→ 维持阻塞（前置 = 脚本 4 成立域结论）
- 全观测估计版 CS′̂（Diff̂/Int̂/SB̂/SM̂）→ 维持独立后续轨（撞 TE≠因果；cTE 全条件为 SB̂ 条件化基础设施候选）
- SelfRep 充分定义 → 维持，另开 grilling（纯理论题）
- 高阶依赖 E^(k)/超图 → 维持 anomaly-triggered（仅系统性异常触发）
- 任务化 μ₀ 实验轨 → 维持
- 连续状态空间 Reach → 维持定义域外

---

## [Grilling] 脚本 4 实现规划 — sim_consciousness_v7_estimator_validity.py（#96 前置）(2026-08-28，Q0-Q14)

> Issue: [#98](https://github.com/verystrongdog/game/issues/98) | 维度: 管线（怎么造出来、怎么验证）| 状态: ✅ 执行完成（2026-08-28，实现合同冻结，#96 转 ready-for-agent）| 前置: #95 estimator-validity 设计冻结（Q1-Q19）+ #97 cTE 变体冻结（Q1-Q6）| 输入: 用户逐题裁决 + ChatGPT 分享 ×15（t_6a9015fb…~t_6a901cbc…）

### 话题

Grilling #96（实现 issue）的实现规划——把冻结设计落成可运行的脚本 4（单文件函数式、中文注释）。**implementation grilling，不重审 #95/#97 科学设计**；需重议科学定义处标记设计越界。

### 决策（Q0-Q14 实现合同要点）

- **Q0 边界**：implementation grilling；流程 Q1-Q14（先锁数据与语义，再锁计算与工程）；收尾 = 决策树条目 → grilling 日志 → #96 issue body → ready-for-agent。铁律：benchmark.py 零改动；复用 estimator stack；cTE 统计定义需重议 → 标记设计越界
- **Q1 职责边界**：脚本拥有 9 项（synthetic trajectory 生成/观测扰动算子/Reacĥ_r 动态候选对/三 estimator adapter/per-repeat 评估/统计汇总/Stage A-B 调度/evaluation-only ground-truth assembly/序列化报告）；不拥有 8 项（benchmark 定义、Layer 0-3 理论、原语重定义、观测版 CS′ 理论、exact Reach→estimator 通道、SM̂ 观测 do 近似、新阈值、estimator 科学定义修改）。**架构不变量：estimator branch 只消费 observation branch；ground-truth 只用于 evaluation，二者不得在 estimator 计算阶段汇合**；12 分区单文件（不拆第二模块）
- **Q2 数据生命周期**：单单元 8 步（seed→c 实例化→ground-truth→轨迹+扰动→Reacĥ/候选对→estimator→per-repeat 评估→跨 repeat 汇总）；seed=hash(system,grid,estimator,repeat) 冻结 → **三估计器不共享随机轨迹（禁 common-random-number 配对减方差）**
- **Q2a c 实例化**：ScaleRNG 插值/比例式均否决（#96 不得发明机制语义）；无冻结 coupling mapping → **所有 c=0.6 格 blocked**（阶段 A c 曲线退出、阶段 B c×h 不可计算，`not_computable` 合法边界结果）；c 机制层定义另开设计轮；确定性系统 c-invariant 如实记录
- **Q3 原语映射**：components/cs4/benchmark 全只读 import；CS′̂ projection 内联（不扩展 components.py，6 条约束）；纯 Python + numpy 留 Q11 实测触发；`evaluate()` 整体不复用；exact Reach 仅 coverage diagnostic（禁流向候选构造/estimator）
- **Q4 plug-in 契约**：`|ΔP̂|` 为检验统计量（非边阈值）；B_perm=999 固定 MC + p+1 校正；α/m_ij 边内族 + ∃ 聚合；**层级 RNG**（cell→repeat→estimator→edge→condition-pair，无全局 RNG）；条件对两组各 ≥1 outcome 才入检验（0 计数=定义域空≠高方差）；plug-in 保留有向边、无向投影成 Ĉ_obs；**禁以样本量/方差/稀疏度过滤已定义 condition pair**
- **Q5 TE/cTE**：TE=cs4 transfer_entropy + THETA_TE=0.01 硬阈值（ln 语义原样）；cTE=全条件直方图 log2、**逐边单检验 family=1、α=0.01、无硬阈值**；三判定函数完全独立（禁 generic 参数化同构）；统一 EdgeResult（m_ij/family_size 仅 plug-in 有定义，TE/cTE 置 null 或按 Q6 修订）；not_testable 仅当数据对象为空（实检 n_transition==0）
- **Q6 schema**：EdgeResult{edge,estimator,state,statistic,statistic_name,p_value,family_size,sample_info,detail}；RepeatRecord{meta,observation,edges,truth,replay,metrics}；完整落盘（不落 999 置换原始序列）；blocked 元记录（status 三分：completed/blocked/failed）；truth 存实际边集；replay 存 present_directed_edges 审计链
- **Q7 A_pair**：任方向 present 即无向正边（真值表含 not_testable 组合）；truth_same = 完整 G_exact 弱连通（component-connectivity projection，h=1 允许经隐变量路径）；**A_pair 分母 D 由 (system,h) 固定、与 Reacĥ_r 无关**；无 A_pair 判定阈值（0.9 仅汇总切片）
- **Q8 P/R/F1**：h>0 有向 truth = E_S^(1)∩(V_obs×V_obs)（与 A_pair 含隐路径 truth 分离）；**无向三值化：present=任一方向 present / absent=双向均 absent / 其余=not_testable**（not_testable 不得转 absent）；cTE 有向边级 P/R/F1 主判（is_primary），plug-in/TE 仅诊断
- **Q9 Stage A**：14 审计格（13 executable + 1 blocked）；N_repeat = n_executable×20×3×32；h 隐变量表 = 预注册冻结常量（三估计器共用 V_obs）；**d 是观测 delay 非 burn-in（禁 trajectory[d:]）**；结果只由确定性 seed 决定、不依赖执行顺序/共享 RNG
- **Q10 Stage B**：select_stage_B = 确定性纯函数 + trigger_log 落盘；R2 仅 plug vs TE（cTE 同格执行不参与选格）；c×h=not_computable（禁 blocked 替代/插值）；H/L 机械取预注册端点；ΔA_pair 逐 estimator 并列报告；局部全因子 = 选中档位并集；Stage A 结果复用不重跑
- **Q11 计算与执行**：per-cell 独立 + 即时落盘；numpy **micro-benchmark 驱动**（仅 cTE 统计内层向量化 + 纯 Python cte_reference 回归锚）；job 粒度=(system,grid,estimator,repeat-range)；防 numpy 线程嵌套（1 thread/worker）；**目标单机完整合法实验 ≤24h**；可中断可恢复（completed skip/blocked skip/failed retry）；超预算报告而非偷改冻结参数
- **Q12 序列化**：data/sim_results/ 目录（MANIFEST/run_log/selection_log/stageA/stageB/summary）；**RepeatRecord=事实源、aggregation=可重算缓存（--aggregate 无损重算）、summary=可重建产物**；MANIFEST=实验定义版本、schema_version=数据结构版本（分离）
- **Q13 验收**：--self-test 两类（逻辑断言+数值回归）；dry-run 两档（D0 最小 smoke、D1 协议边界覆盖含 c=0.6 blocked）；完整验收（全格状态、**failed==0**、blocked/not_testable 合法、三层 summary、seed 复现 + **repeat-range 拆分合并逐字节一致**、**依赖文件零修改 benchmark/components/cs4**）；无失败线（#95 Q11）
- **Q14 异常/恢复**：cell 级异常（任一 repeat 失败 → 整 cell failed + 诊断）；**partial 不续跑、整 cell 重跑**；running/partial 非最终状态，终态仅 completed/blocked/failed；恢复/重试/拆分不改变结果
- **封板**：12 个越界点全堵死（不修改 benchmark/components/cs4；不创造 c=0.6 机制语义；exact truth 与 estimator 严格分叉；exact Reach 不泄漏；not_testable≠absent；A_pair 分母固定；三 estimator 不共用统计判定；d≠burn-in；不因样本量过滤 condition pair；Stage B 不显著性筛选；超预算不偷改协议；seed 决定结果）

### 受影响文件

- `design/decisions/`（本文：#98 条目 + #95/#97 推迟项「→ 见 #98」标注）
- `../设计归档/grilling/grilling-96-estimator-validity-implement/grilling-96.md`（决策日志 + 写入验证表）
- GitHub：#96 issue body（实现合同，needs-triage → ready-for-agent）+ #98 关闭 + 总结评论
- memory（`script4-estimator-validity-implementation-grilling-96.md`）
- `data/term_registry.json`：**无新增**（本轮为实现规划；关键术语已入库 #95/#97；D0/D1/cell_id/EdgeResult 等实现层标识符按 Q14c 原则不入库）

### 相关决策树条目对接

- :3264 / :3320 #95/#97 推迟项「脚本 4 实现 → #96」→ 本条目完成（实现合同冻结，#96 ready-for-agent）
- :3233 #95 Q9 修正行（cTE 并入 #96）→ 本条目 estimator 集合 {plug-in, TE, cTE} 落地
- :3230 #95 Q6（seed=hash(...,estimator,repeat)）→ Q2 实现事实记录（三估计器不共享轨迹）
- :3229 #95 Q5（c 机制层梯度）→ Q2a 缺口处理（无冻结映射 → 全 blocked，另开设计轮）

### 推迟

- **脚本 4 实现执行**（编写 `sim_consciousness_v7_estimator_validity.py`）→ [#96](https://github.com/verystrongdog/game/issues/96) ready-for-agent（按本条目实现合同执行）
- **c 梯度机制层定义**（coupling_parameter(system)→parameter(s) 冻结映射，解锁 c=0.6 格与 c×h 交互）→ 另开设计轮（阻塞项：#96 的 c 曲线/交互）
- scaled observation 轨（n≫8）→ 维持阻塞（前置 = 脚本 4 成立域结论）
- 全观测估计版 CS′̂（Diff̂/Int̂/SB̂/SM̂）→ 维持独立后续轨（撞 TE≠因果）
- SelfRep 充分定义 → 维持，另开 grilling（纯理论题）
- 高阶依赖 E^(k)/超图 → 维持 anomaly-triggered
- 任务化 μ₀ 实验轨 → 维持
- 连续状态空间 Reach → 维持定义域外

---

## 意识结构侧暂停注记（2026-08-28，非 grilling）

> 决策：工作中心转移游戏侧；**意识结构侧整体暂停（搁置非废弃）**。学术轨与游戏正典隔离是设计好的（#40/#93/#94/#95/#97 先例「纯学术研讨，不入游戏正典」），暂停不影响游戏设计推进。
> 状态基线：v7 定义（#93）+ 模拟实现批次（#94）+ estimator-validity 设计（#95/#97）+ 实现合同（#98）+ 脚本 4 完整跑通（1740 completed + 60 blocked、failed=0、`data/sim_results/` 1800 cell 可追溯数据）——全部保留为恢复基线。
> 恢复接续点：memory `意识结构侧暂停-搁置非废弃-2026-08-28.md`（plug-in 统计参数重审 #98 Q4b/Q14、c 梯度冻结映射、CA_Rule30 长轨迹崩溃机制、scaled 轨、全观测估计 CS′̂、SelfRep 充分定义）。

---

## Grilling #100 — E1 壳态保持性模拟实验协议（2026-08-29 闭合）

> Issue: [#100](https://github.com/verystrongdog/game/issues/100)（2026-08-29 开题/闭合）| 维度: 规则+管线 | 形态: 承接 #38 Q7 实验轨 P0 先行项——把「E1 壳态保持性」从自然语言落成可执行的预注册数值协议并实现跑通。来源：用户 2026-08-29 ChatGPT 分享页 ×7（t_6a92d503…~t_6a92f088…）裁决链 + 运行期数值诊断。**E1 结果：PASS**（B 族+A1 壳态保持成立，占位参数域内）。

### 背景

#38 闭合后 Q7 定义实验轨 E1→E2→E3→E4→E6→E5→E7，E1 为 P0 先行（壳态保持性，失败回退 Q3.2 查 B 族+A1）。本 grilling 将 E1 的验证命题、验收判据、数值协议、失败二分类全部量化并实现 `sim_moonlight_e1.py`；同时裁决执行时序（#35 scope 并入 E1-E7、R_i 开题 #101 并行）。

### 决策（Q1-Q8）

- **Q1 验证命题 P**：F=0、B 族+A1 初始壳态 ⇒ r(t)=E/E_c≈1 长期保持。(1) 保持性 [T_min,T_max] |r−1|≤δ_r；(2) 吸引性 p₀=±10% 首次进入并持续停留（t*≤T_settle）；(3) 安全边界 min_t(E−E_th)>0 且扰动集 E(0)=E_c(1±p₀)>E_th；(4) 数值守恒 ε_num 基准实测。冻结月相（λ 调制属 E2）。
- **Q1 待定量**：τ_char=2π/√λ_min⁺(S)（图 Laplacian λ₀=0，普通 λ_min 发散）；T_max=1000τ_char、T_min=5τ_char、T_settle=100τ_char（协议参数非理论常数）；δ_r=0.05（预注册协议参数，δ_r≥10ε_num 必要条件）；ε_num 由 d≡0 基准实测（不预锁）。
- **Q2 h 显式形式**：h_E1(x)=tanh(x)·tanh(x−x_th)，x=(E_c−E)/ε，x_th=(E_c−E_th)/ε——双横截零点、|h|<1（保 d_max=最大阻尼/增益幅度语义）、零新增参数；标注「E1 实现选择，非理论新增公理」（#38 Q6）。否决多项式 A/B（无界幅度）与 C（人为分母）。伴随记号修正：h'(E_th)→h'(x_th)（§四 已写入，导数对门控变量 x）。
- **Q3 数值协议**：标准 RK4 固定步长（**d 在各级中间态求值**，见修正 6）；dt₀=π/(100√λ_max)（最快模态每周期 200 步）预注册初值；收敛序列 dt₀/dt₀/2/dt₀/4；ε_num≤0.005 协议门槛 + dt₀→dt₀/4 唯一合法细化；no-tuning 分裂（数值参数调整 ≠ 模型参数调整）；初始条件单模态壳上旋转 φ(0)=√(E_c/λ_k)v_k、φ̇(0)=i√E_c·v_k（‖v_k‖₂=1）。
- **Q4 扰动分级**：主验收仅 ±10%（±1/5% 在 δ_r 带内可 t*=0 平凡通过 → 降为敏感性诊断）；regime 探针 E(0)=0.9E_th（→0）与 1.1E_th（→E_c）验证分离面两侧符号；双模态诊断 u=v_k+0.1v_j 能量精确归一化（检验全局 d 无模式耦合）；解析 ODE 对照降为渐近诊断（见修正 1）。
- **Q5 G_test=P₄**：N=4 单层连通路径图，w=1，谱 {0, 2−√2, 2, 2+√2}，κ_λ=5.828/κ_ω=2.414；测试图声明写入脚本头（不宣称最终医院拓扑，G_H 待 #1 闭合后替换；K(t)=K₀ 固定 C8）。
- **Q6 最终协议**：Phase 0 预注册冻结 → Phase 1 数值基准（状态误差四阶比 ρ∈[14.4,17.6] + ε_num≤0.005）→ Phase 2 主验收（±10% 三判据 + 实现三校验：能量壳引理/状态四阶比/独立求解器绝对一致）→ Phase 3 诊断（不入 PASS）；**E1 PASS ⇔ Phase 1 ∧ Phase 2**；失败三层分类（实现层/协议层/结构层——结构层先做占位参数敏感性诊断，不写「证伪」）。
- **Q7 时序裁决**：E1-E7 校准轨**并入 #35**（scope 扩展）；R_i 神经落点**开题 #101 并行**（不依赖 E1 数值结果）；「相信被打败」胜利路径暂缓（E1 结果后再定）。
- **Q8 实现**：`sim_moonlight_e1.py`（仓库根，单文件函数式，协议声明入头部）。

### 运行期协议修正 6 项（全部闭环于本 grilling）

| # | 原方案（ChatGPT 裁决链） | 修正后 | 根因（实测） |
|---|------------------------|--------|-------------|
| 1 | 解析 ODE 对照：全动力学对标量 ODE Ė=−d(E)·E 的四阶收敛 | 降为壳区渐近诊断；实现校验改用能量壳引理 + 独立求解器 | K=E 仅纯旋转态；非绝热瞬态（d_max=1≈ω_k=0.765）max\|K/E−1\|≈0.10 |
| 2 | Phase 1 阶检验用能量观测量（带 [14.4,17.6]） | 改用状态误差（‖z‖ 四阶比） | 能量观测量在保守振子上 6 阶（ε_num∝dt⁵，实测比 32/64） |
| 3 | 各 dt 档 n_steps/SAMPLE_EVERY 固定 | 时域对齐（每档 n=T/dt）+ 采样间隔恒 Δt_s=100·dt0 | dt/2、dt/4 只跑 T_max/2、T_max/4 且网格错位 |
| 4 | 引理核对（逐点/梯形求积、全时域） | 与实现的 d 语义一致的求积 + 瞬态窗 [0,T_settle] | 壳区 d≈10·ΔE/ε 放大数值漂移污染全时域；求积须匹配步进语义 |
| 5 | 求解器对照用收敛比（≈16） | 状态自参考比（四阶）+ 求解器绝对一致（≤1e-6） | E 误差 ~1e-7 已达 solve_ivp(rtol=1e-10) 精度地板，比退化 ~1.5 |
| 6 | RK4 冻结-d 步进（d=d(E_prev) 整步常数） | 标准 RK4：d 在 k2/k3/k4 中间态求值 | 冻结-d 对变 d 动力学仅一阶（全动力学状态误差比 ≈2）；stage-d 恢复四阶（ρ_state=16.37） |

### 结果（sim_moonlight_e1.py，2026-08-29 运行）

- **Phase 1 PASS**：ρ_RK4(状态)=15.852 ∈ [14.4,17.6]；ε_num(d≡0)=1.1e-7 ≪ 0.005。
- **Phase 2 PASS**：p₀=±10% 吸引性（t*=0.085-0.102τ 内进入并持续停留至 T_max）、保持性、安全边界（min(E−E_th)=+0.4~0.5）全过；引理残差 8.0e-3≤2e-2；ρ_state(全动力学)=16.37；求解器一致 1.3e-7≤1e-6；壳区渐近偏差 0.0000。
- **Phase 3 诊断**：±1/5% 敏感性正常；regime 探针符号正确（E(0)=0.45→E→0、E(0)=0.55→E→E_c，验证 E_th 分离面两侧 d 符号）；双模态份额漂移 4.0e-8、分解恒等误差 7e-16（全局 d 无模式耦合）。
- **E1 结论：PASS** —— B 族+A1 壳态保持成立（占位参数域内：E_c=1/E_th=0.5/ε=0.1/d_max=1/w=1，P₄ 图）。E2 可开题。

### 受影响文件

- `sim_moonlight_e1.py`（新，E1 协议实现）
- `design/rules/时空结构数学框架.md`（§四 记号修正 h'(x_th)；§11.6 E1 协议块）
- `design/decisions/`（本文）
- `design/framework/six-dimensions.md`（管线 +1；5.1 更新）
- `design/README.md`（5.1 行更新）
- `data/term_registry.json`（候选入库：壳态/B 族/A1 + §十一 短标识符核查——待用户确认）
- GitHub：#35 scope 扩展、#101 开题、#100 关闭
- memory（`E1壳态保持性-grilling-100.md`）

### 推迟

- R_i 神经落点 → #101（并行）
- 「相信被打败」胜利路径 → 暂缓（待独立设计）
- 最终医院图 G_H 拓扑 → #1
- E2-E7 → #35（E1 PASS，按序执行：E2 月相调制标定）→ **见 [Grilling #102](#grilling-102--e2-月相调制标定移动壳慢调制协议2026-08-30-开题协议锁定)（2026-08-30，E2 协议锁定）**

---

## Grilling #102 — E2 月相调制标定（移动壳/慢调制协议）（2026-08-30 开题，协议锁定）

> Issue: [#102](https://github.com/verystrongdog/game/issues/102)（2026-08-30 开题）| 维度: 规则+管线 | 形态: 承接 #38 Q7 实验轨 E1 之后的 P0 项 + #100 结论「E2 可开题」——把「E2 移动壳问题」从自然语言落成可执行的预注册数值协议。来源：用户 2026-08-30 ChatGPT 分享页（t_6a93125600bc81918b48d4848de68de0「裁决随机性供给」高亮消息，E1→E2 总结）裁决链 + 数学框架 §11.6 正典定义。**协议 9 问全部经用户确认**。生命周期循 #100 先例：协议 → 实现 sim_moonlight_e2.py → 运行 → 写入 → 关闭。

### 背景

E1（#100）PASS 后，E2 验证移动壳问题：λ(t) → E_c(λ(t)), E_th(λ(t)) → E(t), q_i(t), q̂_i(t)。E2 与 E1 的本质区别：E1 验证固定月相下的壳动力学；E2 中 E_c 本身随 λ(t) 运动。分享页给出 E2 开题三钉死项（时间尺度/跟踪判据/职责分离），本 grilling 全部量化为协议。

### 决策（Q1-Q9）

- **Q1 λ(t) 波形**：λ(t) = (1−cos Ωt)/2，λ∈[0,1]，Ω=2π/T_moon，T_moon=29.5d（拍频周期）；λ=0↔新月、λ=1↔满月；确定性（C7）。否决：相位角 θ∈[0,2π) 原始形式（不归一化）；三档离散表（v2 已废）。
- **Q2 慢调制协议**：ε_adiab ≡ τ_char/T_mod，T_mod=T_moon/2π；「慢调制」⇔ ε_adiab≪1。扫描 T_moon/τ_char ∈ {10,10²,10³,10⁴}（ε_adiab ∈ {0.63,6.3e-2,6.3e-3,6.3e-4}）。游戏日↔模拟单位映射推迟接口层（E2 只产约束 ε_adiab*）。否决：钉死单值。
- **Q3 跟踪判据**：r(t)=E(t)/E_c(λ(t))（§11.4 已结构锁定，仅确认）。四硬门禁：P1 不脱壳（min_t[E−E_th(λ)]>0）/ P2a 深绝热回退（最深档 max|r−1|≤δ_r=0.05 继承 E1）/ P3 吸引性（p₀=±10% 于 λ(0)=0.5 施加）/ P4 数值分离（ε_num≤0.1×max|r−1|_moving）。两诊断：P2b 收敛标度（实测幂指数 α）/ 滞后 Δφ=argmax_tE−argmax_tE_c(λ)。时间窗：T_settle=1·T_moon，分析窗第 2~3 周期，周期锁定检查。
- **Q4 职责分离**：E2 标定对象仅 f_c/f_th；q^base(λ) 占位=E_c(λ)/N（均匀壳态每节点能量，Σq̂=r 语义自洽），形状留 E6；范围钉死：g→E7、R_i→#101、w_ij→E5、F→E3/E4、初始条件→A1。否决：E2 吞并 E6（违背 Q7 实验轨顺序）；完全剥离 q^base（违背 §11.6 正典定义）。
- **Q5 形状族**：线性端点族 E_c(λ)=E_c,min+ΔE_c·λ（ΔE_c>0）、E_th(λ)=E_th,min+ΔE_th·λ（ΔE_th∈{−0.25,0,+0.25} 三方向——「满月易激活」假设兼容方向由扫描检验）；相对 gap 约束 gap(λ)≥0.1·E_c(λ) ∀λ（P3 ±10% 扰动可行性）；网格 ρ_c=E_c,max/E_c,min∈{4/3,1.5,2.0}（4/3=旧参考 0.675→0.900 幅度比对照点）、基线 E_c,min=1.0/E_th,min=0.5（继承 E1 占位）→ 3×3×4=36 moving runs；对照偏差表诊断不入 PASS。
- **Q6 数值协议**：RK4 + stage 求值扩展至 λ（d 与 λ 均在 k2/k3/k4 中间态求值——冻结-λ 降阶同理 E1 修正 6）；dt₀=π/(100√λ_max)；每案例双跑（moving + λ 冻结控制组 λ≡λ(0)，代码复用 E1），绝热偏差=moving−frozen；G_test 沿用 P₄（对照干净；G_H 待 #1）；初始条件沿用 single_mode_ic，E0=E_c(λ(0))，λ(0)=0.5（新月/满月端点相位入敏感性诊断）；占位参数 ε=0.1/d_max=1/w=1 沿用。
- **Q7 验收合成**：E2 PASS ⇔ ① 深绝热区 {10³,10⁴} P1∧P2a∧P3∧P4 全过 ∧ ② 过渡区 {10²} P1 过 ∧ ③ P4 最深档成立 ∧ ④ 破坏点定位入诊断。输出成立区间下界 ε_adiab*（=P1 首次失败档前一档）——接口层「1 游戏日」映射硬约束。失败三层分类（实现层/协议层——含形状族假设/结构层——B 族+A1 移动壳不成立回 §11.2，不写证伪）。
- **Q8 时序**：#102 完整生命周期（协议→实现→运行→写入→关闭）；不开 Q1–Q6、sim_moonlight_e1.py 冻结不改；#101 并行维持；「相信被打败」暂缓维持。
- **Q9 注册表**：六项候选全部确认入库（λ(t) 月相驱动波形/T_mod/ε_adiab/ρ_c/移动壳跟踪判据/成立区间下界 ε_adiab*）。

### 结果（sim_moonlight_e2.py，2026-08-30 运行，580.8s）

- **E2 结论：PASS** —— 线性族+ΔE_th 方向族在深绝热区 {10³,10⁴} 绝热跟随成立；过渡区 {10²} P1 全过；P4 数值分离成立。36/36 案例通过（快档 {10} 为诊断）。
- **标度律 P2b：α ≈ 1.0 精确**——max|r−1| 每档 10×（L10 9.8e-4 → L100 9.8e-5 → L1000 9.9e-6 → L10000 9.9e-7，ρ_c=4/3 案例），无 O(1) 地板。
- **P2a 深绝热回退**：L10000 max|r−1| = 0.99~2.30e-6 ≪ δ_r=0.05（E1 冻结壳行为复现）。
- **P3 吸引性**：±10% 扰动 t* = 1.70（单位）≪ T_settle=T_moon（阻尼时间尺度 ~1/d_max）。
- **P1 不脱壳全过、破坏点未达**：min gap = 0.5000（新月 λ=0 处，风险相位证实）但远未触阈；**「快档脱壳」未在扫描域内出现**——根因：AGC 能量弛豫率 ≈ d_max·tanh(x_th)·E/ε ≈ 10/单位 ≫ 调制速率 Ω（即使 ε_adiab=0.63）。ε_adiab* ≤ 0.63（下界未解析）——接口层日长映射约束极宽松（T_moon/τ_char ≥ 10 即可）。
- **ΔE_th 方向族对跟随偏差无影响**（三方向 max_dev 四位有效数字内相同）——偏差由 ρ_c 主导（L10000: 9.9e-7 → 1.3e-6 → 2.3e-6）。
- **Δφ ≈ 0**（同相跟随，采样分辨率内无滞后）；**周期锁定** 6.1e-6→5.2e-12 随 ε_adiab 收敛（响应 T_moon 周期性确认）。
- **q̂ 占位连通性**（Q4，参考案例 L10000）：Σq̂ = r ≈ 1 ✓，但每节点 q̂ 非均匀——边界节点 0/3 ≈ 1.104、内部节点 1/2 ≈ 0.896（图 Laplacian 结构依赖，窗内恒定）——**占位基线 E_c(λ)/N 只保证 Σ 语义，节点依赖形状正是 E6 标定对象**。
- **运行期协议修正 1 项**：最深档（ε_adiab=6.3e-4）物理偏差 O(ε_adiab) 趋近 dt₀ 数值地板（ε_num=1.52e-7），P4 门禁 0.1× 需 dt₀→dt₀/2 细化（预注册序列，E1 修正同款；细化后 max_dev 修正 1.12e-6→9.85e-7）。**教训（防重蹈）**：深绝热档验收必须配 dt 细化，否则数值地板污染物理偏差。

### 受影响文件

- `design/rules/时空结构数学框架.md`（§11.6 E2 协议块 + 参数速查表扩展 + §11.6 E2 定义加注）
- `design/decisions/`（本文 + :3517/#38 Q7 加注）
- `design/framework/six-dimensions.md`（5.1 状态更新）
- `design/README.md`（5.1 行更新）
- `data/term_registry.json`（六项候选入库，见 Q9）
- `sim_moonlight_e2.py`（实现并跑通，PASS；含 numba JIT 热路径 + 纯 Python 回退）
- memory（`E2月相调制标定-grilling-102.md`）
- GitHub：#102（协议锁定 + 结果评论，已关闭）

### 推迟

- 游戏日↔模拟单位映射 → 接口层 grilling（消费 ε_adiab* ≤ 0.63 约束，极宽松）
- E3-E7 → #35（E2 PASS 后按序执行：E3 局部注入响应）

---

## Grilling #103 — 游戏日 ↔ 模拟时间接口层（P0 接口契约）（2026-08-30 开题，闭合）

> Issue: [#103](https://github.com/verystrongdog/game/issues/103)（2026-08-30 开题）| 维度: 规则+事件 | 形态: #102 推迟项「游戏日↔模拟单位映射 → 接口层 grilling」正式落成——把游戏侧时间轴（时段/游戏日/月相）与 CGL+AGC 模拟时间轴之间的映射规则、运行时消费契约、校准安全与职责边界全部锁定。来源：用户 2026-08-30 ChatGPT 分享页（t_6a938120c58c819198eea3abb6029aa0「裁决随机性供给」E2→接口层总结；t_6a938303adf48191abe6dbccf2aa4980 Step 0 边界确认 + 8 问）。**Q1-Q8 全部经用户确认（逐轮分享页裁决）**。

### 背景

E2（#102）PASS 产出成立区间下界 ε_adiab* ≤ 0.63（下界未解析，约束极宽松）；#102 Q2 明示「游戏日↔模拟单位映射推迟接口层」。本 grilling 消费该约束，锁定游戏日↔模拟时间的完整接口契约。边界（Step 0 确认）：P0 只定义接口契约，不替 E3 做实验设计；附带小项 = ΔE_th 解读防护 + E1→E2→E3 时序裁决；E3 本身不单开。

### 决策（Q1-Q8 + 小项 2 项）

- **Q1 游戏日定义**：1 游戏日 = 3 时段（上午/下午/夜晚），休息推进 1 时段；夜晚第 3 次休息完成瞬间 → D+1 上午 + 游戏日推进。游戏日 = 月相 λ 推进的原子步长；时段仅属事件/呈现层（NPC 调度/可访问性/风险/月光表观），不作为场动力学时间粒度。否决：引入现实小时/分钟或第四种时间粒度。
- **Q2 时间分层**：模拟时间 = 理论分析时间坐标，以 τ_char 为归一化基准，**不是游戏运行时独立时间变量**；游戏日与模拟时间不建立需要运行时消费的绝对数值映射。运行时以 D 直接计算 λ(D)；τ_char 仅用于绝热性验证——T_moon/τ_char = 29.5 ⇒ ε_adiab = 2π/29.5 ≈ 0.213 ∈ 已验证域。**否决**：1 游戏日 = 1/10/α·τ_char 作为运行时契约（游戏日历耦合 G_H 谱特征）。补充：运行时协议 = 分段冻结（日内冻结 + 日界 λ 跳变 Δλ_max = π/29.5 ≈ 0.106 rad，对应 max|r−1| ≈ 3×10⁻⁴ ≪ δ_r）；ε_adiab* ≤ 0.63 是「扫描过的最大 ε_adiab」，0.213 < 0.63 是落入已验证域的证据，不写成「绝热性已在所有条件下证明」。
- **Q3 刷新分工**：游戏日边界 = 唯一 λ/场参数动力学刷新点；空间切换 = 按当前位置 x_i 重采样（不推进 λ）；时段边界 = 仅事件/呈现层刷新（不进场动力学）。禁止事项：时段月光基线不得解释为 E_c/E_th/q̂ 时段函数；夜晚危险性等真实机制权重归事件/空间状态层（空间维度 grilling 队列项）。
- **Q4 相位锚定与计数**：D=0 ↔ 新月（λ(0)=0，消除开局相位自由参数）；D ∈ ℕ₀ = 自开局已完成的游戏日边界数；λ(D) = (1−cos(2πD/29.5))/2 解析计算（非逐日累加 ⇒ 无累积相位漂移；连续周期 29.5 游戏日、运行时整数 D 离散采样；**满月连续峰值 D=14.75**，D=15 为离散近满月）。λ=f(D) 不变量：战斗/死亡/空间切换/时段切换均不推进 D；仅夜晚第 3 次休息推进 D。存档仅持久化 D，λ 不独立存档（读档 = 恢复历史存档状态，非时间回卷）。
- **Q5 消费 API**：六类消费者（m_field_vec / 空间遭遇·敌人强度 / 剧情绑定 T=时段·月相 / 情境基线 / 呈现层 / 空间状态变化预留）。`moonState(D)` = 纯函数只读无副作用；`MOON_PHASE_CHANGED` 广播 = 失效/刷新通知（非第二状态源）。API 禁止事项：不提供通用 `moonlightIntensity`/`dangerMultiplier` 聚合标量；消费者可解释不得反向修改。
- **Q6 校准安全**：moonState 返回 {λ, E_c, E_th, qhat_baseline ∈ ℝ^N, calibration_status ∈ {PLACEHOLDER, CALIBRATED}, version} = **基线壳态**；E3/E4 扰动量（F_local/F_collective 偏移、q̂ 增强）不进 moonState。PLACEHOLDER 消费分级：只读 λ/剧情谓词/视觉/原型测试（显式标记）✅；正式遭遇/敌人/情境基线/SAN×月光权重 ❌（接口契约级禁止）。校准缺失/版本不匹配 → 启动 fail-fast，禁止静默回退 E2 占位；运行时越界走防御错误路径。
- **Q7 schema 契约**：接口层定义 moonState 契约 + calibration artifact schema（#35 是数值生产者，不拥有 schema）；`major.minor`（major=破坏兼容）；schema_version 与 calibration_version 分离。**硬校验 6 项**：schema major 匹配 / λ∈[0,1] 覆盖含端点 / **graph identity + node-order 匹配且 qhat 维度=N** / gap(λ) ≥ 0.1·E_c(λ) / E_c>0 且 0<E_th<E_c / 数值 finite 无 NaN·Inf；连续性/单调性 = DIAGNOSTIC（模型预注册要求时可升级）。
- **Q8 职责边界**：#103 拥有时间轴/moonState/消费规则/绝热性声明；不拥有校准数值与 E3/E4 动力学（#35）、R_i（#101）、g(SAN,state)（E7/#35）、空间月光分布与夜晚危险性（空间维度）、难度权重（#35）、时段月光表观数值（呈现层）、w_ij（E5）、G_H/graph_identity 定义（#1/#70）。暂停/存档/读档/战斗/死亡不推进 D；绕过休息直接改 D 的时间加速机制违反 λ=f(D) 不变量（未来需要另行 grilling）。
- **小项 1 ΔE_th 解读防护**：E2「ΔE_th 三方向对跟随偏差无影响」仅为本实验参数敏感性结论（偏差由 ρ_c 主导），**不升级为「E_th 理论可删」**；E_th(λ) 月相机制作用（E4 事件激活通道、B 族阈值语义）仍成立，留待 E4 检验。
- **小项 2 时序裁决**：#103 = E2 工程闭环；不重开 E1/E2（冻结脚本不改）；E3 局部注入响应 = 下一实验按 #35 校准轨推进；#101 R_i 并行维持；「相信被打败」暂缓维持（#102 Q8 延续）。

### 受影响文件

- `design/rules/时空结构数学框架.md`（§11.6 接口层协议块 Q1-Q8 + 参数速查表 7 项扩展）
- `design/events/游戏循环.md`（§2.1 时段基线=呈现层表观 / §2.2 游戏日推进锚点 / §4.3 λ(D) 月相推进）
- `design/decisions/`（本文）
- `design/framework/six-dimensions.md`（5.1 接口层闭合 + design/rules/事件状态更新）
- `design/README.md`（5.1 行更新）
- `data/term_registry.json`（游戏日/模拟时间/时段/moonState(D)/λ(D)/MOON_PHASE_CHANGED/calibration_status 等入库）
- memory（`游戏日模拟时间接口层-grilling-103.md`）
- GitHub：#103（总结评论 + 关闭）

### 推迟

- 实现侧验收：校验脚本实现（6 项硬校验，validate_calibration.py）→ 管线维度排期（可并入 #71 数值平衡工具或独立）
- graph_identity 定义 → #1/#70 管线（最终图 G_H 闭合后）
- E_c/E_th/q̂ 具体数值 → #35 校准轨
- 夜晚危险性真实机制权重 → 空间维度 grilling 队列

---

## Grilling #101 — R_i 神经落点（functional_id 映射）（2026-09-02 开题，闭合）

> Issue: [#101](https://github.com/verystrongdog/game/issues/101)（2026-08-29 开题，2026-09-02 闭合）| 维度: 规则+管线 | 形态: #38 Q5 接口锁定后留空的最后缺口——填充 m_field 游戏接口的神经落点向量 R_i ∈ ℝ^69。来源：用户 2026-09-02 ChatGPT 分享页 ×9（t_6a939c41…~t_6a93b6be…「确认接口层边界」系列：Step 0 边界确认 + 8 轮裁决 + 外部 AI 评审 ×5）裁决链 + 时空结构数学框架 §11.5 正典。**Q1-Q7 全部经用户确认（含外部 AI 建议核查后采纳）**。阻塞：#70 P2 情境系统 m_field_vec[69] 占位全 0。

### 背景

#38 Q5 锁定接口形态 `m_field_vec⁽ⁱ⁾ = q̂·g·R_i`，R_i ∈ ℝ^69 只定接口存在、未填=0；#69 D6 确立 m_field 独立第三通道（非感官模态，不进 W_sensory）；#75 P2 将 m_field 接入 s_total 占位全 0。本 grilling 填充 R_i 的落点结构/权重语义/数学约束，数值归 #35 校准轨。

### 决策（Step 0 + Q1-Q7）

- **Step 0 边界**：#101 只定义 R_i 的结构与语义（落点 fid 集合、权重结构、数学约束）；具体权重数值与最终效应大小归 #35。关键措辞边界（写死）：「怎么加权」的形式/约束由 #101 定，「权重数值」（w_k = ?）由 #35 定。#101 不重新定义 m_field 接口、不修改 q̂/g 职责、不承担 E_c/E_th 数值校准。69 fid 正典来源 = `data/brain_regions.json` + 脑功能层级模型.md（不重新创造 fid 编号）。
- **Q1 落点集合**：S_core = {fid : level(fid) ∈ {L1,L2} ∧ fid ∈ W活跃节点} = **12 节点**（L1 4：Amygdala/HippocampusCA1/HippocampusCA3/Parahippocampal；L2 8：ACC×3/Insula/OFC/PosteriorCingulate/IsthmusCingulate/TemporalPole）。排除 L0（脑干广播职责重叠）/L3（W_sensory 职责重叠）/W排除节点（无网络传播语义）。S_ext（L4/L5 知觉-信念子集）**暂不纳入**（扩展性不变量保证未来低成本）。**硬约束：落点 ⊆ W活跃节点（48）**。
- **Q2 结构 + 扩展性**：`R_i = Σ_s α_s · v_s^norm`。① 互斥分区 supp(v_s)∩supp(v_s')=∅（硬约束）② 语义内归一化 Σv_s^norm=1 ③ 独立缩放 α_s（每语义一个）④ 禁止重叠（A 方案；B 未来预留不实现，重叠需求另开 grilling）⑤ **扩展性不变量**：新增语义只能增加未占用 fid 的 R_i 分量，不得改变已有语义分量 ⇒ **不触发已有语义重新校准**；新语义 α_s 正式数值仍归 #35 ⑥ 未校准 α_s 占位值必须标记 PLACEHOLDER，不得进入正式数值消费路径（原型/测试显式启用须保留标记，对齐 #103 calibration_status）。
- **Q3 通道语义**：m_field = 独立第三输入源，非 s_env 乘性增益因子。三通道在 WC 输入层逐节点加法共存：`s_total_j = s_事件_j + s_env_j + m_field_j`；**不引入 s_env×m_field 交互项**。「月光放大情境情绪维度」降级为**系统响应层/游戏语义层描述**（不作为输入层数学关系），增强效应是否/何时发生由 #35/E3 实验验证。#101 禁引入乘性调制或额外交互项，不修改三通道组合接口。**两层解耦**：Q2 互斥分区（防语义间耦合）+ Q3 通道边界（防落点设计侵入事件/环境定义）。
- **Q4 权重语义（主辅两档参数化）**：语义 s 当前 12 落点，主档 4（L1）+ 辅档 8（L2），档内等分。定义 r = m/a > 0，满足 4m+8a=1：`v_s^norm(j) = r/(4r+8) [j∈主] 或 1/(4r+8) [j∈辅] 或 0`。**r 正式数值归 #35**；α_s 正式数值归 #35。v_s^norm 单位归一化 ⇒ α_s 表示语义总注入强度，r 仅决定强度在主/辅节点间的分配。**r=1 仅作 PLACEHOLDER 均匀分配，不代表神经生理事实**；校准得 r≈1 不构成「主辅结构不存在」证据（仅「数据未支持两档差异」）。锁定范围 = 结构（4+8 分档/档内等分/r 参数化/单位归一化）由 #101 定；不锁定 r 具体值；不宣称 L1/L2 主辅关系为已验证生理权重。
- **Q5 全局固定**：R_i ≡ R ∀ i（i 仅表示「谁在接收」，不表示落点结构不同）。R 不随空间位置 x_i、SAN、运行时 state、时段/月相变化。**职责正交化**：空间差异 → q̂_{x_i}；SAN/state 差异 → g(SAN_i,state_i) 及 tone/CSTC；月相变化 → q̂ 基线/壳态（#103 moonState）；神经落点结构 → R；语义扩展 → R 的新增互斥分区（Q2）。当前模型**不通过 R 表示个体差异**；未来需个体特异性落点必须另开接口裁决，不得使现有 R 随个体动态变化。
- **Q6 符号与稀疏**：R[j] ≥ 0（**非负 = 输入层性质**——m_field 不通过 R 对任何 fid 施加直接负向输入；网络层抑制/竞争由既有 WC/CSTC 动力学承担，「增强」是系统响应层结果不由 R 直接保证）。**当前版本** supp(R) = S_core（12 节点），非落点恒 0。**长期结构不变量** supp(R) ⊆ W_active + 语义分区互斥——12 是当前版本结构容量，**不作为永久 N_max 上限**；未来语义扩展只能使用未占用 W-active fid。
- **Q7 与情境系统独立**：R 落点注入与情境系统**无运行时协调接口**（两通道各自注入 s_total，由 WC 自然合成）。**情境选择（SituationSelector）不读 m_field**（防间接环：月光不通过「换情境→再注入」绕圈影响神经）。呈现层月光显示走 moonState(D)（#103）。情境扩展（27 原型组合/新增，composition_rules 已内置 layering/chaining/merging）走情境系统侧，与 R 语义扩展（Q2 互斥分区）**两个独立机制**。
- **Q8 撤回**：消费端/数据形态/校验归属非设计决策——R 只经 m_field_vec → s_total 进入消费端（§11.5 演进链既定事实）；数据文件与校验实现归 #70/#71 管线任务；校验进 #70 已在 Q2 锁定。不入决策。

### 受影响文件

- `design/rules/时空结构数学框架.md`（§11.5 R_i 从「待独立 grilling」更新为已锁定结构 + 参数速查表）
- `design/rules/skill-tree/运行时状态模型.md`（§4.5 m_field 接口注更新）
- `design/rules/核心机制.md`（§6.3 措辞修正：「放大」降级系统响应层描述）
- `design/decisions/`（本文）；旧延迟项加注「→ 见 #101」：:2249（#38 推迟）、:2374（#69 延迟）、:2424（#70 推迟）
- `design/framework/six-dimensions.md`（规则维度 5.1 状态更新）
- `data/term_registry.json`（s_env 措辞修正「真实物理存在」→「空间内容呈现」；R_i/神经落点 入库）
- memory（`月光落点-R_i-grilling-101.md`）
- GitHub：#101（Step 0 评论 + 总结评论 + 关闭）

### 推迟

- R 数据文件（moonlight_landing.json）与引擎实现 → #70/#71 管线任务（含 supp 互斥/归一化/supp⊆W_active/非负/扩展性不变量回归校验）→ **已承接 [#104](https://github.com/verystrongdog/game/issues/104) Q4（P2 实施含 moonlight_landing.json + moonState(D) 契约骨架，实施 issue [#105](https://github.com/verystrongdog/game/issues/105)）**
- r 与 α_s 正式数值 → #35 校准轨（PLACEHOLDER 消费分级对齐 #103）
- 「相信被打败」胜利路径 → 维持暂缓（#102 Q8/#103 小项 2 延续）
- 个体特异性落点（若未来需求）→ 另开接口裁决

---

## Grilling #104 — P2 情境系统实施启动（2026-09-02 开题）

> Issue: [#104](https://github.com/verystrongdog/game/issues/104) | 维度: 管线+规则 | 形态: #70 路线图 P2 批次实施启动——#75 方案已定（2026-08-16）但未实施；**m_field_vec[69] 占位全 0 阻塞已由 #101（2026-09-02）解除**，可进入实施。来源：用户 2026-09-02 请求 + ChatGPT 分享页 ×3（t_6a93bff2…「确认m_field实施方案」Q2 排期审查、t_6a93c185… Q4 边界审查、t_6a93c49c… Q6 修正审查）外部 AI 评审核查后采纳。承接: #70 路线图 P2；阻塞: P3 NPC Affordance 全量。

### 背景

#75 方案（design/events/持续场分离 + 27 原型选择器 + 三通道 + 只读接口）含 m_field「占位全 0」段落，写于 #101/#103 之前；#101 闭合 R 落点结构、#103 定 moonState(D) 契约与 calibration_status 分级 → #75 task-plan 需对齐更新，P2 方可实施。

### 决策（Q1-Q4+Q6）

- **Q1（m_field 实现深度）**：**结构实现 + PLACEHOLDER 分级 + 门禁**（非占位全 0）——三层：①数据层 `moonlight_landing.json`（12 落点 fid + 主辅两档结构 + r/α_s 显式 PLACEHOLDER，文件存在 ≠ 已校准）；②引擎层 m_field 合成（q̂×g×R → s_total 加法，三通道 s_total = s_事件+s_env+m_field）；③门禁层（calibration_status=PLACEHOLDER 时正式情境基线/SAN×月光消费 fail-fast，#103 Q6；demo 走显式标记的原型测试路径）。
- **Q2（排期）**：**独立开实施 issue + 串行惯例 + 无冲突协调机制**——依赖图 P2 无入边（P3 才依赖 P1c+P2），不等待 P1 实施完成；但项目实际工作流是 strict 串行（git 单线无 merge + implementation issue 时间线逐关后开），共享文件（CombatState/CalibrationConfig/Console/Tests）为常态串行增量，**不需要**并行冲突协调机制。修正：前一版 Q2-A「并行推进 + 冲突协调」被推翻（ChatGPT 外审确认「依赖关系独立 ≠ 开发过程并行」）。
- **Q3（开启时机）**：P2 实施 issue **现在创建并排队**（#105），待 #91（csharp-console 实现，OPEN）关闭后实施；开始前基于当时最新 HEAD 增量。
- **Q4（实施边界）**：P2 含 ①`moonlight_landing.json`（#101 四项校验：supp 互斥/归一化/supp⊆W_active/非负）②`moonState(D)` 契约骨架（λ(D)=(1−cos(2πD/29.5))/2 解析 + calibration_status/version 消费，#103 Q4-Q6）③m_field PLACEHOLDER 消费路径 ④正式消费门禁 fail-fast ⑤显式标记 demo 例外。**不包含**：正式 q̂/E_c/E_th 数值生产（#35）、#103 artifact 6 项硬校验（validate_calibration.py → #71）。**边界写死：R 落点校验（P2）≠ artifact 硬校验（#71）**。
- **Q6（env_tones + key_brain_regions）**：env_tones demo = **病房/走廊/护士站 3 环境示例集**（非固定上限，扩展 = 加键，零 schema 变更，完整表值归空间内容填充）；key_brain_regions **fid 直用 + 27 原型全量校验器**（实测 37 去重名 100% 已是 functional_id，翻译需求 = 0 → **不建立 dk→fid 映射表**；校验断言名称 ∈ region_name_map.regions 且 name == functional_id；100% 命中为验收门槛；未来新增原型自动防回归；失败不静默降级）。T4 任务性质从「构建映射工具」改为「建立/运行 fid 一致性校验器」。

### 事实核查（引用即读取）

- 引擎 `code/src/YouAreNotTheFish.Core/` 无 moonState/calibration_status/MFieldStrength/R 落点代码（grep 0 匹配）→ moonState(D) 契约骨架引擎实现归属 P2（#103 未指定实现批次）
- `situation_primitives.json` 27 原型 key_brain_regions 共 201 条、去重 37 名；37/37 ∈ region_name_map.regions 且 name == functional_id（python3 实测）
- git 单线历史（--graph 无 merge）+ implementation issue 串行时间线（43→46→51→53→55→57→61→63 逐关后开）→ 项目串行惯例实证
- #91（csharp-console 实现）OPEN，console 代码已在 HEAD（1f86b67）

### 受影响文件

- `design/decisions/`（本文）；#75 条目加注、#101 推迟项加注「→ 见 #104」
- `../设计归档/grilling/grilling-75-p2-situation/task-plan.md`（更新：m_field 段落 #101/#103 对齐 + T4 fid 校验器 + demo 3 环境集 + 推迟清单 m_field 项解除）
- `design/framework/six-dimensions.md`（管线队列 P2 状态更新）
- GitHub：#105（P2 实施 issue，排队中）+ #104（本文）
- memory（`情境系统引擎-grilling-104.md`）

### 推迟

- 实施执行 → #105（待 #91 关闭后开始）→ **见 [Grilling #91](#grilling-91--csharp-console-实现关闭审查--数据回归事故修复2026-08-30-闭合)（2026-08-30 关闭，阻塞解除）**；正式校准数值（r/α_s/q̂/E_c/E_th）→ #35；#103 artifact 6 项硬校验 → #71；env_tones 全环境表值 → 空间内容填充

---

## Grilling #91 — csharp-console 实现关闭审查 + 数据回归事故修复（2026-08-30 闭合）

> Issue: [#91](https://github.com/verystrongdog/game/issues/91)（工作issue 01，2026-08-14 开题，2026-08-30 闭合）| 维度: 管线 | 形态: csharp-engine plan §十一 step 11 实现 issue 的关闭审查——spec v1.2 已审计通过（三轮审计 31+21 CONFIRMED + 终审 PASS + sign-off ✅），实现已交付（commit 1f86b67，284/284 绿）但 issue OPEN，阻塞 #105（P2 情境系统实施）。关闭审查发现 12 个引擎测试失败，根因非 #91 实现本身而是 #92 数据漂移。

### 背景

#104 Q3 将 #105 排队在 #91 关闭之后。关闭审查（AC-1~13 逐项对照 + 门禁复跑）发现：当前 HEAD 309 用例 / 12 失败——issue body 的「284/284 绿」为 2026-08-14 历史真相，此后数据漂移导致锚点失效。

### 事故根因（数据回归，非契约演进）

- **#92（66d1dd2，2026-08-20）重跑 build_tripartite_model.py 覆盖了两步管线的注释产物**：role/function_label/gameplay_labels/description 从全部 4 类边（brainstem 114/cstc 47/corticocortical 776/privileged 112）丢失。
- **EdgeRole 枚举默认值 = Active(0)**（BrainEnums.cs:61）→ 99 条 modulating(0.5) 边静默升值 1.0 → CorticalBias b_j 膨胀（mOFC 锚点 1.05→1.2）→ WC 静息不动点漂移（0.535~0.771 → 0.558~0.814）。
- 后果：9 失败（M1 锚点 ×5 含 console AC-10 + CorticalBias ×4）+ 3 镜像契约失败（#92 D6 合法演进——镜像从 stub 展开为完整剖面，测试未同步）。
- 次生发现：privileged_pathways（112 条 curated whitelist）为手工维护数据，生成器不产出——重跑生成器还会丢它。

### 决策（Q1-Q5）

- **Q1（边界）**：12 个失败纳入 #91 一并处理（#105 排队依赖 + 同根因闭环最经济；#92 数据落地遗留的引擎侧缺口作闭合后修正）。
- **Q2（M1 锚点策略）**：**保持 HARD，不降级**。数据恢复后实测静息不动点回到原窗口（0.535~0.771），5 个锚点测试未改断言全部通过。外部建议的 C 混合策略（精确窗口 DIAGNOSTIC）**未采纳落地**——降级会掩盖可恢复的数据回归；仅记录为「未来图数据合法变更时的锚点政策」（对齐 #103 hard-validate/DIAGNOSTIC 分层）。
- **Q3（恢复手段）**：**重跑 build_function_labels.py**（两步管线第二步），非 git checkout 旧数据（旧数据无 #92 lateralization，回滚会破坏 #92 产物）。验证：4 字段全量序列化集合与 66d1dd2^ 逐边 0 差异；lateralization 保留（49 节点 = 0.0，镜像 2 节点无）；node_profiles 不变。
- **Q4（镜像契约）**：3 个失败拆 2 类——`LoadTripartiteModel_EnumFieldsAreParsed` 是 role 恢复的消费方（自动转绿）；2 个 brain_regions 镜像测试更新为 #92 D6 语义（镜像 = 主变体完整剖面 + mirror_of 溯源，断言不依赖具体枚举值）。
- **Q5（门禁）**：**① 校验脚本 `code/tools/validate_tripartite_annotations.py`（只读 fail-fast：4 类边 role 合法值/注释字段存在性/lateralization 契约/privileged 非空/注释元字段）+ ② 生成器头部防再犯警告**。原子化重跑方案**否决**：临时管线验证证明生成器输出 privileged=0（手工数据会丢失）。③ 引擎 fail-fast（EdgeRole 缺失默认 Active 的静默失败）**后置**为独立决策，不进 #91 关闭条件。

### 结果

- 309/309 全绿（Failed: 0, Passed: 309, Skipped: 0）；12 失败归零（9 数据恢复 + 1 role 消费 + 2 契约更新）。
- Console AC-1~13 逐条 ✅（实现本身无回归）；结转清单 5 项 ✅。

### 受影响文件

- `data/connectivity/tripartite_model.json`（重跑注释脚本恢复 4 字段——commit 30108af）
- `code/src/YouAreNotTheFish.Core.Tests/Data/GameDataLoaderTests.cs` + `code/src/YouAreNotTheFish.Core/Data/FunctionProfile.cs`（镜像契约测试更新 + 注释同步——commit d2c76db）
- `code/tools/validate_tripartite_annotations.py`（新增）+ `code/tools/build_tripartite_model.py`（防再犯警告——commit 373c2a0）
- `design/decisions/`（本文）、`design/framework/six-dimensions.md`（管线 P2 状态）
- `../设计归档/grilling/csharp-console/impl/issues/01-console-implementation.md`（关闭记录）
- GitHub：#91（总结评论 + 关闭，解锁 #105）
- memory（`console实现-grilling-91.md`）⚠️ 因环境只读未写入，完整记录在本条目

### 推迟

- 引擎 fail-fast（EdgeRole 缺失默认 Active 的静默失败）→ **见 [Grilling #106](#grilling-106--引擎-fail-fastedge-role-缺失默认-active0-静默失败2026-09-02-闭合)（2026-09-02 闭合，独立决策 Q1-Q7）**
- #105（P2 情境系统实施）→ 解锁，可启动
- M1 锚点政策（C 混合策略）→ 仅政策记录，未来图数据合法变更时生效

---

## Grilling #106 — 引擎 fail-fast（EdgeRole 缺失默认 Active(0) 静默失败）（2026-09-02 闭合）

> Issue: [#106](https://github.com/verystrongdog/game/issues/106)（2026-09-02 开题，2026-09-02 闭合）| 维度: 管线 | 形态: #91 Q5 后置项 ③ 的独立决策——EdgeRole 缺失时 C# 反序列化静默回退 `Active(0)` 的引擎层防御。校验脚本 `code/tools/validate_tripartite_annotations.py`（管线侧只读 fail-fast）已实现（#91 Q5 ①/②），本 grilling 补齐引擎侧防御（③）。

### 背景

#91 事故（#92 数据漂移）根因之一：`EdgeRole` 枚举默认值 = Active(0)（BrainEnums.cs:61），4 类边 record 的 `Role` 属性非可空（TripartiteEdges.cs），JSON 缺失 `role` 字段时 System.Text.Json 静默保持默认值 → brainstem 边 modulating(0.5) 静默升值 1.0 → CorticalBias b_j 膨胀 → WC 静息不动点漂移。反序列化完成后无法区分「JSON 缺失」与「显式 active」，消费者层检查（CorticalBias 已查 Silent）永远无法发现此缺陷，必须在反序列化边界拦截。

### 决策（Q1-Q7）

- **Q1（机制）**：`[JsonRequired]`（net8.0 原生 `System.Text.Json.Serialization.JsonRequiredAttribute`）——4 类边 record 的 `Role` 属性声明 `[JsonRequired]`，JSON 缺失 `role` → 反序列化边界直接抛 `JsonException`；保持 `EdgeRole` 非可空及 `Active(0)` 既有语义，不增加消费者层兜底。实测确认（临时实验项目，net8.0 语义）：缺失 → `JsonException: missing required properties including: 'role'`；`"role":null` → converter 兜底抛 JsonException（`SnakeCaseEnumConverter` 的 `reader.GetString()` 返回 null → 比较失败）——注意此路径**不是** JsonRequired 抛的，需测试锁定；显式 `active/silent/modulating` → 正常；`PropertyNameCaseInsensitive=true` 下大小写不敏感兼容；数组元素级逐元素生效。
- **Q2（范围）**：仅 `Role`。真实类名：`BrainstemProjection.Role` / `CstcEdge.Role` / `CorticocorticalEdge.Role` / `PrivilegedPathway.Role`（TripartiteEdges.cs，注意不是 `CstcProjection`/`Corticocortical`/`Privileged`）。其余字段（System/Direction/Loop/Pathway/StationFrom/StationTo/Neurotransmitter/Projection）**不加**，维持现状。拒绝 B（全局 required——spec 有合法 nullable/异构字段如 RdocProfile 6 域/SignalSubtype，会混淆「合法省略」与「错误缺失」）；拒绝 C（只保护 brainstem——#92 事故四类边 role 全部丢失，只保护一类留下不一致契约）。
- **Q3（测试）**：四类边各缺 role 回归测试（复用 `Loader_BadJsonThrowsJsonException` 临时文件模式：写临时坏 JSON → `Assert.Throws<JsonException>`）+ `"role":null` 失败断言 + `"role":"active"` 成功正例。验收语义锁死：**缺失 role → JsonException；显式 `"role":"active"` → 正常通过**（不能写成「所有最终得到 Active 的情况都失败」）。
- **Q4（归属）**：独立 implementation issue（#107），进入串行实施队列；不并入 #105（无数据依赖、范围已锁死）、不回写 #91（已闭合，③ 本就是独立后置决策）。
- **Q5（Console 契约）**：`Program.cs` 增加 `catch (JsonException ex)` → stderr「数据校验失败: {ex.Message}」+ 退出码 1；同步 Console spec AC-12；新增 Console 级缺 role 回归测试（复用 `InvalidArgs_Exit1` 进程测试模式，**锁 stderr 内容而非仅 exit code**——未处理异常在部分环境也可能碰巧非零退出）。分层：Data/Engine 层发现错误 → JsonException；Console 层转化 → stderr + exit 1；不在 `GameDataLoader` 吞异常或改写异常类型。
- **Q6（延迟项）**：其余非可空枚举字段「缺失 → 枚举默认 0」风险（如 `BrainstemProjection.System` 缺失 → `LcNe(0)`，`CorticalBias.ToneOf` 直接消费注入错误 tone）列为延迟项，不纳入 #106 范围。**触发标准（三项同时满足 → 独立评估是否补 `[JsonRequired]`）**：①存在引擎数值消费者；②缺失产生静默错误语义；③现有管线校验未覆盖该风险。
- **Q7（收尾）**：进入 Step 4 落盘（本条目 + 六维状态 + spec 同步 + memory + #106 关闭）。

### 结果

- Q1-Q7 全部闭环；共享对话外部审查 5 轮（Q1-Q6 每轮确认方案 + 修正 Q2 类名错误 + Q5 强化 stderr 验收）。
- 引擎层防御落地 → #107（implementation issue，排队中）；管线侧门禁已就位（#91 Q5 ①/②）。
- 注册表：无新术语入库（`EdgeRole` 为代码级枚举 8 字符不触发 ≤4 短标识符规则；fail-fast/静默回退语义已由 `calibration_status` 条目覆盖）。

### 受影响文件

- `code/src/YouAreNotTheFish.Core/Data/TripartiteEdges.cs`（4 类边 Role 加 `[JsonRequired]`——#107 实施）
- `code/src/YouAreNotTheFish.Core.Tests/Data/GameDataLoaderTests.cs`（四类缺 role/null/active 测试——#107）
- `code/src/YouAreNotTheFish.Console/Program.cs`（catch JsonException → exit 1——#107）
- `code/src/YouAreNotTheFish.Core.Tests/ConsoleApp/ConsoleAppTests.cs`（缺 role 进程测试——#107）
- `../规格/引擎/csharp-data-layer.md`（§四 EdgeRole 行注明 JsonRequired——#107）
- `../规格/引擎/csharp-console.md`（AC-12 增 JsonException → exit 1——#107）
- `design/decisions/`（本文）、`design/framework/six-dimensions.md`（管线维度）
- GitHub：#106（本 grilling）+ #107（implementation）
- memory（`引擎fail-fast-grilling-106.md`）

### 推迟

- 其余枚举字段静默默认风险（System/Direction/Loop/Pathway 等）→ 触发标准 ①+②+③ 同时满足时独立评估
- 引擎层防御实施 → #107（串行队列，待排期）→ 见 [Grilling #110](#grilling-110--107-实施执行层引擎-fail-fast2026-09-03-闭合)（✅ 已实施，2026-09-03）

---

## Grilling #108 — P2 情境系统实施 #105 实施前审查（Q1-Q15 执行契约）（2026-09-02 闭合）

> Issue: [#108](https://github.com/verystrongdog/game/issues/108) | 维度: 管线 | 形态: 工作issue 02 [#105](https://github.com/verystrongdog/game/issues/105)（P2 情境系统实现）实施前审查——在 #75 方案（D1-D4）+ #104 实施决策（Q1-Q4+Q6）已锁定约束下，把 15 个实施层开放点（B1 数据层 / B2 SituationSelector / B3 m_field 通道 / B4 fid 校验器 / B5 Console+测试）逐分支定案为**执行契约**——开发者拿到 task-plan 后无需再问设计问题即可实施 #105。来源：用户逐题外部 AI 评审分享页 ×14（「确定JsonRequired方案」会话分支链，t_6a943190…~t_6a945571…），每 Q 定案经外部评审核查后采纳。承接: #104（P2 实施启动）；阻塞: 无（#105 已解锁）。

### 背景

#104 Q3 将 #105 排队于 #91 之后；#91 关闭（2026-08-30）解锁 #105。实施边界与顶层结构已由 #75/#104 锁定，但 15 个实施层细节（数据 schema/API 契约/边界/测试/demo）未定——不锁死会产生隐性设计分叉。本 grilling 逐分支审查，达成「实施时不能再自由解释的接口/行为契约」。

### 决策（Q1-Q15）

- **Q1（B1-① alpha_patterns 契约）**：`row_id → pattern[8]` 数据契约；行 id ↔ 派生分支绑定留代码（Emit 调用点持有 A1/A2/A4/A5/B1/B2/B4/C1/D1/D2）；`m_alpha` 二态编码 = 有限数字 [0,1]（常量，A 类 1.0）∪ `"m_delta"`（B/C/D 类，调分支算法算 m）；**5 类加载错误 fail-fast 抛 `JsonException`**（消费行缺失 / pattern 长度≠8 / 类型非法 / 数值越界 / 非 `"m_delta"` 字符串）；14 行完整保留、引擎仅映射消费 10 行（A3/A6/A7 保留不消费）；**数据表不是可选配置**——不静默补零/截断/自动修复（对齐 #106 反序列化边界拦截）。
- **Q2（B1-② W_sensory 69×8 锚点）**：嗅觉 = {LateralOrbitofrontal, Amygdala}（#69 解剖锚「梨状皮层/OFC」——梨状皮层不在 69 fid 集，映射到 OFC 主投射 + 杏仁核气味-情绪联结）；热觉 = {Postcentral, Insula}（S1 温度区 + 后脑岛内感受）；**允许节点模态数 > 2**（Postcentral 变 3 模态，生理成立）；原 6 列逐位不变；元字段同步。
- **Q3（B1-③ env_tones 环境 id 形态）**：环境键 = **英文 slug id + 中文 `display_name`**（数据键承担机器接口、显示名承担人类可读语义）；demo = ward/corridor/nurse_station；`alpha_env` 恰好 8 值 ∈ [0,1]，长度/范围违规及**运行时缺失环境键 → fail-fast**；`CombatState.CurrentEnvironment` = string；Console `--env <id>` 注入；`typical_game_scenario` 自由叙事文本与 env id 不建立自动耦合（env_map 人工建表）。
- **Q4（B2-④ 情境粒度）**：**全局单一情境**（战斗/遭遇级）——SituationState 单一挂 CombatState；s_env（含原型注入）空间级、所有参与者同值注入；SAN 调制 = **存在性条件**（任意参与者 SAN<30%，含敌方，敌我同构+恐慌传染叙事）；刷新 = 空间切换 ∪ 任意 C1。
- **Q5（B2-⑤ env_map 来源）**：env_map **折叠进 env_tones.json**（每环境键含 `situation.primary` 引用原型 `name`，不复制内容）；**删除 alternates 字段**（无锁定消费者语义，不建第二套候选池——恐慌偏移统一走全局 G 组）；加新环境 = 加一个键，零 schema 变更（#104 Q6 契合）。
- **Q6（B2-⑥ 诡异/负面分组 + p_panic 语义）**：G = {原型 : `rdoc_profile.negative_valence ≥ t_neg(=0.2)` ∧ `appraisal_profile.valence = negative`}，构造期计算（实测 **G = 17 成员**）；t_neg 是规则参数非 27 条硬编码名单；**G 与 primary 不互斥**（primary ∈ G 合法，两概率路径可同结果，不加排除逻辑）；p_panic=0.5 语义：恐慌真 → P(G 均匀随机)=0.5 / P(primary)=0.5，假 → 确定性 primary；组内均匀随机、注入 RNG（同 seed 同选择）。
- **Q7（B2-⑦ 强度函数）**：双档阶梯——恐慌假 `strength=1.0` / 恐慌真 `strength=s_neg ∈ [1,1.5]`（数值 [NEW] 归 #35，**锁形式不锁数值**）；只作用于原型 fid 注入、**与 α_env 正交**（不缩放环境基调，防两通道混淆）；重选时定值、情境生命周期内恒定。
- **Q8（B2-⑧ 刷新时机挂钩点）**：C1 重选 = **事件流驱动**（TurnManager 事件窗口检测 `StatusChangeEvent(Panic, Entered=true)` → `Select(env, panic, rng)`），**下一回合 Phase 1 生效**（本回合按旧情境结算，不窗口内换情境）；恐慌消退（Entered=false）不重选（C1 只有进入行，情境保持至空间切换/下次 C1）；初始情境在 `CombatState.Create` 确定；SituationSelector 无状态纯函数、触发机制放 TurnManager。
- **Q9（B3-⑨ moonlight_landing.json schema）**：**参数形式 schema**——顶层 `schema`/`version`/`calibration_status`/`calibration_version` + `semantics[]`（id/primary[4]/secondary[8]/r/alpha_s）；r/α_s = 字符串 `"PLACEHOLDER"`（r=PLACEHOLDER → 按 r=1 由 #101 Q4 公式算均匀 12 落点权重）；**字段缺失 ≠ PLACEHOLDER（schema/load error，禁止静默补占位）**；预计算 v^norm 不作第二数据源（防双源漂移）；四项校验引擎加载期 fail-fast：supp 互斥 / 公式重算归一化 / **supp ⊆ W_active（fid→dk 映射后 ∈ 48 dk 级端点集）** / 非负 + r>0。
- **Q10（B3-⑩ moonState(D) C# 骨架）**：`static class MoonState` + `Query(int day)` 纯函数 → `MoonStateResult(Phase=λ(D), Shell={E_c(λ),E_th(λ)}, QhatBaseline[69], CalibrationStatus, Version)`；E_c/E_th 按 #102 E2 锁定形式结构实现（常量挂 CalibrationConfig 为 PLACEHOLDER）；**QhatBaseline N=69 是占位契约**（≠「graph identity 已证明 N=69」，闭合后升级 + 硬维度校验）；D 推进机制与 MOON_PHASE_CHANGED 广播**不实现**（demo 固定 D；无 P2 消费者）。
- **Q11（B3-⑪ 门禁机制）**：`CalibrationGate.EnsureCalibrated(status, version)` 挂载于 **m_field 合成注入点**（PLACEHOLDER/版本不匹配 → fail-fast，Data/Engine 层抛 → Console 转 stderr+exit 1，接 #106 Q5 分层）；**门禁范围 = moonlight→m_field 正式消费链路，s_env/α_env/情境原型注入不挂**（不消费 moonlight calibration artifact，#101 Q3 三通道正交）；demo 例外 = `CalibrationConfig.AllowPlaceholderDemo`（默认 false）+ Console `--mfield-demo` + 每回合醒目警告；三数据文件（alpha_patterns/env_tones/moonlight_landing）schema major 加载期统一校验（major 不匹配 fail-fast，minor 兼容演进）；MoonState.Query 运行时防御断言（0≤λ≤1 / E_c>0 / 0<E_th<E_c / 有限性）。
- **Q12（B3-⑫ s_total 合成时序）**：三通道 **Phase 1 注入点合成**——`s_total_i = SPending_i + s_env + m_field_i`；SPending 保持事件累加语义不变（现有 accumulate-then-inject-then-clear 零改动）；`s_env[69]` 存 CombatState（情境刷新重算，Q8 下一回合生效）；`m_field_i[j] = QhatBaseline[j] × g(SAN_i) × R[j]`，**g ≡ 1.0 占位**（E7/#35 定正式形式，不动架构）、q̂ 取 QhatBaseline 无空间差异（延迟）；默认（无 `--mfield-demo`）PLACEHOLDER 下 m_field 消费 fail-fast、`s_total = s_事件+s_env` 正常运行；**WcDynamics.Step 签名零改动**。
- **Q13（B4-⑬ fid 校验器）**：两层防线——① `code/tools/validate_situation_fids.py` 管线侧只读校验器（名称 ∈ region_name_map.regions 且 name == functional_id；27 原型 37 去重名 100% 命中报告；失败 exit 非零；新增原型自动纳入；**不建立 dk→fid 翻译映射表**——翻译需求=0）② SituationSelector 构造时引擎侧全量断言 fid ∈ 已知集（未知 → 加载期异常，防绕过管线校验器直接换数据文件）；**情境 fid 不要求 ⊆ W_sensory/W_active**（心理情境非感官，与 moonlight 落点约束不混用）；与 moonlight_landing 校验分文件。
- **Q14（B5-⑭ Console demo 形态）**：新增 **`--demo-situation` 非交互 trace 模式**（`--env`/`--day`/`--rounds`/`--seed`/`--mfield-demo`）——对齐 #105 验收（情境/λ(D)/s 注入/a(t) 变化一次确定性运行可见），不污染 RunBattle，与 RunResting trace 惯例一致；输出 = 初始环境/情境/strength + 每回合 λ(D) + WC a(t) 摘要 + 首回合 s_env 注入前后对比 + mfield-demo 时 PLACEHOLDER 警告；`CombatState.Create(environment)` 默认 ward，非法 id → CliUsageException → exit 1；同 seed 同输出。
- **Q15（B5-⑮ 测试矩阵）**：G1-G9 矩阵（G1 数据契约 fail-fast / G2 迁移回归（309 全绿=门槛） / G3 EventProcessor 数据驱动 / G4 SituationSelector / G5 MoonState / G6 门禁 / G7 三通道合成 / G8 fid 校验 / G9 Console 进程级）；**p_panic 契约断言不做频率统计**——恐慌假 → 必 primary；恐慌真 → 必 ∈ {G ∪ primary}；同 seed 同选择（无预注册样本量，不制造「跑 n 次接近 50%」验收）。

### 事实核查（引用即读取）

- `situation_primitives.json` 27 原型 key_brain_regions 共 201 条、去重 37 名；37/37 ∈ region_name_map.regions（69 键）且 name == functional_id 且 ∈ brain_regions 69（python3 实测）
- G 组按 Q6 规则实测 = 17 成员（negative_valence ≥ 0.2 ∧ valence=negative；排除 unexplained_phenomenon（valence=ambiguous）与 stealth_avoidance/deception_unraveling（阈值下））
- 「W活跃节点（48）」= 三体模型 1049 边去重端点集（graph_nodes 51 − 3 无边节点 LocusCoeruleusRight/PontineReticularNucleus/SubstantiaNigraParsCompactaRight = 48）；12 落点 fid→dk 映射 12/12 ∈ 48（HippocampusCA1/CA3 同 dk `Hippocampus`；AnteriorCingulateCortex/Dorsal 同 dk `caudalanteriorcingulate`）——校验必须走 fid→dk，不可直接比字符串
- `EventProcessor.cs` 硬编码 α pattern 位置 :123/:230（`for k < 6`）；`WsensoryMatrix.cs` 动态读列零改动；`GameDataLoader` 异常语义 = FileNotFound/JsonException/InvalidOperationException
- `Program.cs` 现有 `--seed`/`--trace-resting` 两模式；`CombatState.SPending` 每回合累加→注入后清零

### 受影响文件

- `../设计归档/grilling/grilling-75-p2-situation/task-plan.md`（Q1-Q15 执行契约注入——§二 决策清单 + §三 数据文件 + §四 选择器 + §五 三通道 + §七 任务 + §九/§十 校验与验收）
- `../设计归档/grilling/grilling-108-p2-impl-review`（14 份外部评审存档）
- `design/decisions/`（本文）
- `design/framework/six-dimensions.md`（管线维度 P2 状态更新）
- `design/README.md`（5.0 P2 行更新）
- `data/term_registry.json`（G/t_neg/s_neg/p_panic/m_delta/环境 id 入库）
- memory（`情境系统引擎-grilling-108.md`）
- GitHub：#108（总结评论 + 关闭）；#105（实施 issue，可启动）

### 推迟

- 实施执行 → #105（串行队列，可启动）；正式校准数值（r/α_s/q̂/E_c/E_th/g(SAN)/s_neg）→ #35；#103 artifact 6 项硬校验 → #71；env_tones 全环境表值 + situation.primary 全表 + G 组精化 → 空间内容填充；q̂ 空间差异 → graph/spatial 校准；D 推进 + MOON_PHASE_CHANGED 广播 → 游戏循环实施；#107（引擎 fail-fast）仍串行队列中，与 #105 顺序实施

## Grilling #109 — #105 实施执行层（2026-09-03 闭合）

> Issue: [#109](https://github.com/verystrongdog/game/issues/109) | 维度: 管线 | 形态: 工作issue 02 [#105](https://github.com/verystrongdog/game/issues/105) 实施执行层定案——在 #108 Q1-Q15 执行契约（已锁定）之上，定案 6 项执行决策并本会话完成实施。承接: #108（实施前审查闭合）；阻塞: 无（#105 已解锁、回归门槛 309/309 绿实测）。

### 背景

#108 把设计层开放点全部锁为执行契约（Q1-Q15），开发者拿到 task-plan 无需再问设计问题；但 git 形态/分批/门禁执行/问题处置/验收流程等执行层决策未定。本 grilling 逐项定案，达成后立即实施。

### 决策（Q1-Q6）

- **Q1（分支策略）**：开 `feat/p2-situation` 分支（实施完成后合回 main）。用户选保守方案——与近期 #91/#106 的 main 直改惯例不同，本次改动面大（4 数据 + 8 代码 + 测试 + 校验器）走分支隔离。
- **Q2（提交分批）**：按 T1-T7 分批，每批「数据+代码+该批测试」自包含、测试全绿后提交；G1-G9 测试矩阵就近落位，G2 回归门槛（309 绿）全程保持。
- **Q3（问题处置）**：沿用 #96「实现说明」先例——冻结设计未明示处机械实现自主决策并记录；数值不匹配如实呈现不偷改；设计越界标记另开轮。产出 `../设计归档/grilling/grilling-105-p2-impl/实现说明.md`。
- **Q4（数据生成）**：W_sensory 扩列用一次性 Python 脚本生成 + 逐位断言（防 69×8 手改错位，脚本进 code/tools/ 留存）；其余 3 个新 JSON 按契约手写 + 引擎测试断言。
- **Q5（验收关闭）**：逐项核验 8 项验收标准（G1-G9 全绿 + 309 回归 + fid 校验 37/37 + Console demo 输出存档）+ 验收记录后关闭 #105 + 总结评论；不做外部 AI 评审（#108 已做过实施前审查，本批纯执行）。
- **Q6（执行形态）**：共识后本会话直接实施（Q1-Q5 决策 + Q1-Q15 契约足够，不另开会话）。

### 实施结果（T1-T7，6 commit）

| 批次 | 内容 | commit |
|------|------|--------|
| T1 | W_sensory 69×8（Q2 锚点）+ 迁移脚本 | b7153eb |
| T2 | alpha_patterns.json + EventProcessor 去硬编码（Q1） | bf9337c |
| T3+T4 | env_tones.json（Q3/Q5）+ fid 校验器（Q13 第一层） | fbd7412 |
| T5+T6 | SituationSelector + 三通道 + MoonState + 门禁 + moonlight_landing（Q4-Q12） | 0548b32 |
| T7 | Console --demo-situation + G1-G9 矩阵（Q14/Q15） | 98d5b27 |
| 文档 | 实现说明.md（Q3 处置机制） | dfa9d20 |

- **测试**：346/346 全绿（309 回归 + 37 新增）；fid 校验器 37/37（无 dk→fid 映射表）；cross_refs 701 有效（2 dead/2 warning 均为既有问题，与 #105 无关）
- **验收 8 项全过**：W_sensory 69×8 原 6 列逐位不变（git 历史比对 True）；alpha_patterns 14 事件前 6 位 ALL MATCH；env_tones 3 环境 + SituationSelector 空间映射/SAN 调制/刷新生效；fid 校验两层防线；moonlight_landing 12 落点四项校验；moonState(D) 骨架 + 门禁 fail-fast；s_total 三通道 + SituationState 只读；Console demo 输出存档（含 --mfield-demo PLACEHOLDER 警告 + 非法 env exit 1）
- **机械实现 6 项**（实现说明.md）：TNeg float→double（边界精度）；静息 trace environment=null（AC-15 语义保持）；m_field 通道默认关闭（Q12）；λ(D=14)=0.9936 断言修正；W_active 校验走 fid→dk；CombatState.Create 可选 environment 参数
- **契约一致**：G 组 17/17、37 名 100% 命中、12/12 落点、消费行前 6 位一致、回归 309→346——全部与 #108 事实核查一致，无偏差

### 受影响文件

- `../设计归档/grilling/grilling-105-p2-impl/实现说明.md`（新建）
- `data/connectivity/`：W_sensory.json（改写）/ alpha_patterns.json / env_tones.json / moonlight_landing.json（新建）
- `code/src/YouAreNotTheFish.Core/`：Data（AlphaPatterns/EnvTones/MoonlightLanding/GameDataLoader/GameData）、Engine（EventProcessor/SituationSelector/SituationEnv/MoonState/CalibrationGate/MFieldComposer）、Entity/CombatState、Flow/TurnManager、Types（CalibrationConfig/SituationState）
- `code/src/YouAreNotTheFish.Console/`（CliArgs/Program）
- `code/tools/extend_wsensory_69x8.py`、`code/tools/validate_situation_fids.py`（新建）
- `code/src/YouAreNotTheFish.Core.Tests/`（+37 测试：SituationSelectorTests/MoonStateTests/NewDataContractTests/DemoSituationTests + 既有测试同步）
- `design/decisions/`（本文）、`design/framework/six-dimensions.md`（管线 P2）、`design/README.md`（5.0 P2）
- GitHub：#109（本条目 + 关闭）；#105（实施 issue 关闭）

### 推迟

- 合回 main（feat/p2-situation → main，用户确认后执行）；正式校准数值（r/α_s/q̂/E_c/E_th/g(SAN)/s_neg）→ #35；#103 artifact 6 项硬校验 → #71；env_tones 全环境表值 + situation.primary 全表 + G 组精化 → 空间内容填充；q̂ 空间差异 → graph/spatial 校准；D 推进 + MOON_PHASE_CHANGED 广播 → 游戏循环实施；#107（引擎 fail-fast）仍串行队列中，与 #105 顺序实施

## Grilling #110 — #107 实施执行层（引擎 fail-fast）（2026-09-03 闭合）

> Issue: [#110](https://github.com/verystrongdog/game/issues/110) | 维度: 管线 | 形态: 工作issue 03 [#107](https://github.com/verystrongdog/game/issues/107) 实施执行层定案 + 本会话完成实施。承接: [#106](https://github.com/verystrongdog/game/issues/106)（Q1-Q7 设计决策即 #107 规格，无设计层开放点）；阻塞: 无（串行队列中 #105 已完成并合回 main，轮到 #107）。来源：用户逐题外部 AI 评审分享页 ×3（Q2 定案 t_6a9508b77b948191876d5d95bacc1437；Q4 两轮 t_6a950b6597d48191a0ab54d5abf3e0af / t_6a950e055ad48191af18928a592bacb5），每 Q 定案经外部评审核查后采纳。

### 背景

#106 把引擎层 fail-fast 的机制/范围/测试/归属/Console 契约/延迟项全部锁死（Q1-Q7），实施归属 #107 排队。本 grilling 只定执行层决策（git 形态/分批/测试注入机制/问题处置/验收），无设计层内容可 grill。

### 决策（Q1-Q6）

- **Q1（执行形态）**：方案 A——执行层决策 + 本会话直接实施并关闭 #107（#109 Q6 先例）。用户采纳推荐。
- **Q2（分支策略）**：**main 直改**——改动面 1 源文件 + 2 测试文件 + 关闭文档，边界封闭（无数据/schema/跨模块变更），346 基线 + 新增一步回归；#91/#106 同量级惯例；`feat/107-fail-fast` 无实质风险隔离。经外审（t_6a9508b77…）采纳。
- **Q3（提交分批）**：两 commit——① `feat:` TripartiteEdges.cs + 全部新测试（引擎 6 + Console 1，就近落位）；② `docs:` 关闭文档（决策树 #106 注记 + #110 条目 + 六维状态 + 项目总览 + 实现说明 + 外审存档）。用户采纳推荐。
- **Q4（Console 测试数据注入机制）**：**`YANTF_DATA_DIR` 环境变量**——`FindDataDir` 首查（`is { Length: > 0 }`），已设置用之、未设置完全走既有发现策略（生产行为零变化）；不改 CLI / 不扩公开 spec / 不增加用户可见参数。Console 夹具 = 真实 `brain_regions.json` + 缺 role 的 `tripartite_model.json`（仅两文件；`LoadAll` 中 tripartite 第 2 个加载，JsonException 先于后续 FileNotFound）。**防假阳性断言**（外审新增价值，采纳）：exit 1 + stderr 含「数据校验失败」**且不含**「数据目录缺失」——夹具缺后续文件走 FileNotFound（错误路径）时断言失败；另断言无未处理异常堆栈。夹具输入用**缺 role**（非 `role:null`）——还原 #92 事故原貌，端到端验证 `[JsonRequired]` 路径；`null` 路径由引擎级测试 + #106 Q1 实测覆盖。三层职责：#106 Q1 `role:null` → converter 兜底路径；#106 Q3 → 引擎级非法输入；#107 Console 缺 role → `[JsonRequired]` → fail-fast 端到端链路。
- **Q5（问题处置）**：产出 `../设计归档/grilling/grilling-107-fail-fast-impl/实现说明.md`（#96/#109 同构）——机械实现自主决策记录（临时 JSON 最小结构 / active 正例单条 / env 覆盖实现位置 / 新增测试 346→353）。用户选产出。
- **Q6（验收关闭）**：按 #107 验收 6 项逐项核验 + 门禁复核（`validate_tripartite_annotations.py`）+ 双 issue 关闭评论（决策表 + 受影响文件 + 写入验证表）；实施本身不做外部 AI 评审（Q2/Q4 已外审）。用户确认后执行。

### 实施结果

- **commit 1（feat）**：`4ecdf63`——TripartiteEdges.cs 4 处 `[JsonRequired]` + Program.cs `YANTF_DATA_DIR` + 引擎 6 测试 + Console 1 测试
- **commit 2（docs）**：本文 + #106 注记 + 六维状态 + 项目总览 + 实现说明 + 外审存档
- **测试**：353/353 全绿（346 回归 + 7 新增，一次通过无调试迭代）；`validate_tripartite_annotations.py` PASS（1049 边全含 role，无回归）
- **环境注记**：沙箱内 build 链 = `NUGET_PACKAGES=/home/dog/game/.nuget-pkgs`（工作区内可写缓存副本）+ `DOTNET_ROLL_FORWARD=LatestMajor`（本机仅 .NET 10 运行时，net8.0 二进制需 roll-forward）；`.gitignore` 已补 `.nuget-pkgs/`。NuGet 客户端直连 api.nuget.org 的 repository-signatures 端点 SSL 失败（curl 通），离线缓存规避。

### 受影响文件

- `code/src/YouAreNotTheFish.Core/Data/TripartiteEdges.cs`（4 类边 Role 加 `[JsonRequired]`）
- `code/src/YouAreNotTheFish.Console/Program.cs`（FindDataDir 首查 `YANTF_DATA_DIR`）
- `code/src/YouAreNotTheFish.Core.Tests/Data/GameDataLoaderTests.cs`（+6 引擎测试）
- `code/src/YouAreNotTheFish.Core.Tests/ConsoleApp/ConsoleAppTests.cs`（+1 Console 进程测试）
- `../设计归档/grilling/grilling-107-fail-fast-impl/实现说明.md`（新建）+ `../设计归档/grilling/grilling-110-issue107-impl`（3 份外审存档）
- `design/decisions/`（本文 + #106 注记）、`design/framework/six-dimensions.md`（管线）、`design/README.md`（5.0）
- GitHub：#110（本 grilling，关闭）+ #107（implementation，关闭）

### 推迟

- 其余非可空枚举字段「缺失 → 默认 0」风险（System/Direction/Loop/Pathway 等）→ #106 Q6 触发标准 ①引擎数值消费者 + ②静默错误语义 + ③管线校验未覆盖 三项同时满足 → 独立评估（当前未触发，复核无遗漏）
- `FindDataDir` 硬编码 `/home/dog/game/data` 绝对路径兜底 → 延迟项（触发标准：移植/打包场景出现）；`YANTF_DATA_DIR` 已为将来去硬编码留注入点
- 正式校准数值（r/α_s/q̂/E_c/E_th/g(SAN)/s_neg）→ #35；#103 artifact 6 项硬校验 → #71；env_tones 全环境表值 + situation.primary 全表 + G 组精化 → 空间内容填充；q̂ 空间差异 → graph/spatial 校准；D 推进 + MOON_PHASE_CHANGED 广播 → 游戏循环实施

## Grilling #111 — 项目总体插件化（静态契约式模块化架构 + 数据版本化 + 降级协议裁决）（2026-09-03 开题，闭合）

> Issue: [#111](https://github.com/verystrongdog/game/issues/111)（2026-08-31 开题，2026-09-03 闭合）| 维度: 管线+规则 | 形态: 架构方向 grilling——把 DSH harness「一切都是插件」哲学应用于项目引擎/知识架构：引擎模块隔离（某部分出错不影响其它）+ 数据版本化与可换实现（过时设计数据不阻塞进度）。来源：用户逐题外部 AI 评审分享页 ×10（t_6a957877bf8481918b7738506d17c540 ~ t_6a95834c1c7c8191b38f4583911735e7），每 Q 定案经外部评审核查 + DSH 源码核查后采纳。

### 背景

issue #111 两个触发点：①#35 启动时发现跨 14 个 grilling 推迟聚合的待校准参数清单引用链大量过时（公式被替换悬空/快照引用过期/术语漂移/引用链内部矛盾），根因 = 同一事实被复制到最多 5 个存储点靠人工同步（多源复制是结构，漂移是必然）；②用户联想 DSH harness 插件特性（隔离性 + 版本化依赖 + 可换实现）对应「引擎某部分出错不影响其它功能」「过时设计数据不干扰进度」两个诉求。两个方向：方向 1 = 单一事实源 + 生成视图 + 历史/现状分层（知识新鲜度治本）；方向 2 = 插件化 = 隔离层（与方向 1 正交互补）。

**DSH 源码核查（引用即读取，/home/dog/deepseek-harness）**：DSH 插件化真实实现 = ①静态装配插件树（cordis.yml 声明 Entry，Loader 导入，`vendor/loader/`）②服务 seam 换实现（`ctx.<name>` 抽象 + 多后端，装配时选一，如 `ctx.fs` 三实现 / `ctx.llm` 三后端含 llm-replay mock）③Symbol realm 隔离（`isolate.ts`，命名空间隔离非故障隔离）④启动 fail-loud 审计（`assertEntriesActivated`：任一 enabled 条目未激活 → 整树抛错 exit(1)）⑤HMR 开发期热换 + 失败回滚（`vendor/hmr/`）。**DSH 无**：运行时 Degraded 状态机、`SupportedDataVersion` loader 协商（版本 = pnpm semver 编译期锁定 + 数据契约字段如 `FsVersion`）、故障隔离（崩溃照样 fail-loud）。

### 决策（Q1-Q9）

- **Q1（方向采纳）**：**A′ 静态契约式模块化架构**——统一原则：①能力/Service seam ②明确接口边界 ③版本/契约信息 ④装配期有效性检查 ⑤正式装配失败 → fail-fast ⑥实现替换在装配层 ⑦开发期迭代机制与生产运行机制分离。**不采纳**：运行时 Ready/Degraded/Unavailable 通用三态、运行时热插拔、HMR 生产装配、loader 层运行时版本协商、Symbol isolate 解释为故障隔离。否决 B（限定数据层——引擎内部模块不只数据层）、否决 C（维持局部缝合）。
- **Q2（降级语义）**：**否决通用运行时三态**——DSH 双目标（正式消费不撒谎 + 开发进度不阻塞）靠「编译期 fail-fast + 开发期 HMR/回滚」两个正交机制达成，不引入运行时 Degraded 中间态。**明确保留** `calibration_status ∈ {PLACEHOLDER, CALIBRATED}`（#103 Q6）为**数据产物契约字段 + 消费门禁**（装配/消费前有效性检查），非引擎运行时状态机——**模块状态 ≠ 数据产物状态**（外审关键一刀）。
- **Q3（Module 资格）**：三步 = **资格审查流程**，非 `A∧B∧C` 机械充分必要——①本体判据（核心资格）= 独立能力边界（可独立装配/替换）②契约审查 = 有契约敏感性才声明版本/有效性 ③失败影响审查 = 有污染风险才接 fail-fast 门禁。纯计算函数（DamageCalculator/MoonState/SpeedScoreCalculator）第一关即排除，注入参数 + 防御断言即可。反强包装约束：「不能因为需要 Module 验证架构就先制造 Module」。
- **Q4（试点对象）**：**`IActionProvider`**——既有真实 seam（实现者 4：NpcActionProvider/PlayerActionProvider/CompositeActionProvider/WaitProvider，`Flow/IActionProvider.cs` + Console `Providers.cs`），消费者 `TurnManager.cs:17` 仅依赖接口。否决外审点名 `IResponseResolver`（仅单一 Noop stub，#70 F-4，试点会混入 P4c 功能实施）。
- **Q5（SchemaVersion + 最小契约）**：**SchemaVersion 不进入 IActionProvider**——消费内存 record（编译期类型约束）无数据版本敏感，加版本字段 = 凑字段反模式；版本契约留待数据消费型试点（如 m_field 链）。**最小 Module 契约 = 能力边界 + 构造器注入 + 装配期有效性检查（null → ArgumentNullException）**，不加 SchemaVersion/ModuleStatus/wrapper/registry/动态加载。
- **Q6（试点方式 + 验收）**：**纯审查验证，零源码改造**——既有 seam 已满足最低契约时，最强验证恰恰是「不改它」。不加 `[Module]` 标记（无机器可验证语义，对比 #106 `[JsonRequired]`）。**六维机械验收表**：①独立能力边界 PASS ②多实现同一契约 PASS ③消费者依赖接口 PASS ④版本敏感性 **N/A**（非 FAIL——无版本需求不代表 Module 不合格）⑤装配失败前置 PASS（既有测试 `TurnManagerTests.cs:328`）⑥无多余抽象 PASS（diff=0）。
- **Q7（落盘边界）**：「插件化」入库绑定项目内定义（排除 4 个旧模型）；「降级协议」不登记为已采纳能力（有术语≠采用机制）；「单一事实源」不因本轮与 Module 混层。方向 1 **推迟**（本轮不裁决/不实施/不宣称完成）。
- **Q8（registry 机制）**：`插件化`/`静态契约式模块化架构` 入主表 active；`降级协议`/`单一事实源` 走 **`_pending_candidates`** 通道（**补齐 `data/term_registry_candidates.md` 悬空引用**——`term_registry.json:7` 已引用但文件缺失）；**不新增 status 第三值**（现状 = {active, deprecated}）；`plug-in`（学术轨估计器，#95）保留不混用（架构轨用中文「插件化」区分）。
- **Q9（收尾 + 确定性措辞修正）**：issue 8 问全处置（1-6 裁决、7-8 推迟）。**问题 6 措辞修正**：「同 seed 同输出」只表述为「本轮不引入新的降级路径，因此不产生新的降级路径确定性要求」；**不把 DeterministicRng 等既有机制扩大解释成已证明全引擎行为全局确定性**（#71 只保证 RNG 注入层，非结算链全链确定性证明）。

### 试点结果

- 六维机械验收：**PASS / PASS / PASS / N/A / PASS / PASS**——既有 seam `IActionProvider` 已满足 Module 最小契约，零源码改动。
- 验收产物：[../设计归档/grilling/grilling-111-plugin/试点审查报告.md](../archive/grilling/grilling-111-plugin/%E8%AF%95%E7%82%B9%E5%AE%A1%E6%9F%A5%E6%8A%A5%E5%91%8A.md)（证据位置逐条 + 外审存档 10 份）。

### 受影响文件

- `design/decisions/`（本文）
- `design/framework/six-dimensions.md`（管线维度）
- `data/term_registry.json`（+2 术语：插件化/静态契约式模块化架构；calibration_status 注记；_pending_candidates 更新）
- `data/term_registry_candidates.md`（新建——补齐悬空引用，登记降级协议/单一事实源等推迟项）
- `../设计归档/grilling/grilling-111-plugin/试点审查报告.md`（新建）
- memory（`静态契约模块化-grilling-111.md`）
- GitHub：#111（本 grilling，关闭）

### 推迟

- **方向 1（单一事实源）**：CalibrationConfig.cs 手写常量 / term_registry numerical_locations / 生成视图 / #35 触发点 1 治本方案——**零实施性变更**，独立议题裁决
- **issue 问题 7（#70 路线图）**：P0-P6 批次**不因 #111 重构**；模块化按「新子系统建 Module、既有 seam 纯审查」渐进融入
- **issue 问题 8（语义层兜底）**：非结构化知识防过时（引用即读取 + 一致性清扫现状维持）→ 纳入方向 1 后续议题
- **版本契约验证**：数据消费型试点（如 m_field 链）验证 SchemaVersion 实际需求

---

## [Grilling] 病因生成模型世界观裁决 — 创伤=唯一触发 + β 个体易感性接口 + g 环境塑造 (2026-09-01，D1-D3)

> 来源: #87 恢复讨论 + 外部评审核查（ChatGPT 分享 t_6a960da7e254819198438cb6185052d7「判断模型正确性」）| 维度: 规则 | 前置: #88 转化接口 ✅ + #87 创伤记忆语义 ✅ + #90 记忆内容层 ✅ | 状态: ✅ 已落盘（结构锁定，β 数值 [NEW 初值可调]）

### 话题

外部 AI 评审质疑「创伤记忆累积→达阈值→病理化」被写成唯一总路径，建议拆多路径框架（P_trauma ∪ P_development ∪ P_organic ∪ P_susceptibility-stress）。逐条核查后：评审三点具体批评（单次创伤/高成熟创伤/非一一对应）均落空（正典双阈值 I_max 通道与 M:N 候选集已覆盖），但**命中真实张力**——决策树 :3139 D1「无创伤+无器质+非发育 = 健康」与 :3173 D9「无创伤 NPC 走素质-应激兜底」并存未消解。经收养研究事实核查（Tienari 2004 芬兰收养研究：基因×环境交互，健康家庭显著降低高遗传风险儿童患病率）后逐题裁定。

### 决策

- **D1（创伤 = 唯一触发路径）**：没有创伤记忆就不发病。病房里不存在"无创伤来源"患者——**创伤来源 = 各类固定生活环境（家庭/学校/职场/部队/社区等），事件类型层环境无关**（§3.2.1：校园霸凌=社会伤害、职场羞辱=公开羞辱/控制剥夺、长期压力=慢性冲突/高压）；家族聚集现象的解释层立场（模型假说非事实等式）：跨代环境传递（凯博文：社会根源 = 社会结构 × 人际网络）为候选解释。**原"应激触发型"语义废除**：双相/SZ 谱等遗传度高的病，其患者创伤来源可为家庭环境（出生在患者家庭本身 = 目睹发病/照料者不稳定/被忽视 = 忽视/遗弃事件类型），但不排除其他固定生活环境来源。
- **D2（β = 个体易感性接口 → β(t) 最小化版）**：**β_i(t) = F(β₀,i, D_i(t))——基线易感性 β₀ × 发育阶段调制，慢变量；既往经历和当前环境不直接修改 β**（可塑变化走 g/k/L，防 β/g/k/L 概念堆积——模型职责分离，非经验事实断言）。β₀ 来源开放 ∈ {遗传、早期发育、其他稳定个体差异}，不预先裁决权重；家族聚集的遗传/环境归因**不在 β 定义层裁决**（三层分离：经验层 = 现象 / 解释层 = 项目立场「跨代环境传递为候选解释」模型假说 / 参数层 = β 接口）。**防自激反馈环**：β(t) 时变 ≠ 每次受创伤后 β 自动改变——事件即时负荷进 L，不反向改 β。依据：Tienari 2004（Br J Psychiatry 184:216-22）——环境可调节易感性表达。原「遗传 = 阈值调制」命名废弃（偷渡 β≡遗传 因果判断，2026-09-01 修正）。**D9 立场 B「遗传素质」成分废弃**，素质-应激兜底不再需要；原「不引入素质/遗传维度」（:3139）绝对表述修正。
- **D3（g = 环境塑造）**：不成熟度由童年环境决定（依恋质量/教养方式/早年经历），非天赋。模型闭合：环境（g 塑造 + 创伤事件）× 先天（β 阈值）——无"无来源"自由度。职责分离：g 放大累积负荷（L=ΣΔI×g）、β 降低门槛（A_trauma）、创伤事件唯一触发。

### 对 #87 的影响

- **Q1 人际层**：从"可选土壤"升级为**必需土壤**——**环境资格判定概念族废弃（2026-09-01 第九/十/十一份评审）**：环境 = 人生叙事中建模为持续性生活场域的结构性经历（Event Generator 结构输出，非分类器结果）；T_min/环境资格/is_fixed_environment() 不存在；三维度分离（存在性≠暴露量T≠塑造结果）；环境内容维度（家庭结构/亲密关系/代际冲突/关系损伤 + 家庭外场域）保留为关系结构内容
- **Q3 因果链强度**：定位明确——创伤 = 必要触发，遗传 = 调制，非独立路径
- **Q2 参数选择规则（2026-09-01）**：宏观确定锚定 + 微观随机采样分层——宏观社会事件由出生年×地域确定性投影（矩阵），微观人际事件从「事件类型×场所」池随机采样（M5 多样性）；落点 Event Generator；确定性复用 #71 DeterministicRng。详见 [grilling-87.md](../archive/grilling/grilling-87-npc-life-generation/grilling-87.md) Q2 决策
- **Q4 模板化边界（2026-09-01）**：类型学与生成规则允许复用；具体人生实例必须独立生成（M5 澄清）；"同构≠模板复制"防回归；素材池=生成参考非人生模板。详见 [grilling-87.md](../archive/grilling/grilling-87-npc-life-generation/grilling-87.md) Q4 决策
- **Q5 审阅流程（2026-09-01）**：交付 C（结构化骨架+简版叙事，同一事实源两视图）+ 锚点依赖传播局部迭代 + 用户修改优先于 AI 生成规则 + 定稿入 M2 双轨；M2 澄清（AI 起草阶段可为作者，定稿后不改写）。详见 [grilling-87.md](../archive/grilling/grilling-87-npc-life-generation/grilling-87.md) Q5 决策
- **Q6 生成质量校验（2026-09-01，终题）**：三层门禁——①个体合法性硬校验（矩阵/年龄/地域，违反→FAIL）②批次多样性诊断（防异常集中/塌缩，不要求服从预设分布）③素材形态软对照（五本病案=参考非规范，偏离→WARNING）。质量校验=生成后诊断系统非分类器；质量阈值允许但第一版不拍数值（待批次可观测后标定）。**#87 六问（Q1-Q6）全部闭合**。详见 [grilling-87.md](../archive/grilling/grilling-87-npc-life-generation/grilling-87.md) Q6 决策
- **生成器架构（2026-09-01 第八份评审）**：A′-Generator 静态模块契约架构——5 阶段职责隔离/静态 seam/失败语义三层/fallback=生成策略非模块状态/错误在最近契约边界识别。详见 [grilling-87.md](../archive/grilling/grilling-87-npc-life-generation/grilling-87.md) 架构决策段
- 原推迟项「素质-应激兜底规则 → #87 生成功能」（:3187）**废弃**

### 受影响文件

- `design/rules/skill-tree/创伤记忆转化接口.md`（§一 世界观裁决 / §二 β 参数 / §3.1 双阈值个体化 / §3.2.1 立场 B 修正 / §四 参数表 / §六 结构清单）
- `design/decisions/`（本文；:3173 D9 与 :3187 推迟项经本文修正，历史记录保留）
- `data/term_registry.json`（新术语：β 个体易感性接口 / 代际创伤链；创伤记忆条目数值位置同步）
- `../设计归档/grilling/grilling-87-npc-life-generation/grilling-87.md`（恢复记录）

### 推迟

- β 数值 / g 环境映射规则（童年环境 → g 的量化）→ #87 生成功能设计（Q1 人际层结构落地时）
- 24 经历型疾病文件中「遗传度」类引用的清扫标注 → 一致性清扫批次
- 收养研究详细证据入库（Tienari/Kety/GWAS 综述）→ reference/文献 批次

**🔧 修正 (2026-09-01):** D1 原表述「家庭环境是创伤事件核心来源」过窄——创伤来源 = 各类固定生活环境（家庭/学校/职场/部队/社区等），事件类型层环境无关（§3.2.1 十类事件本就覆盖：社会伤害/公开羞辱/控制剥夺/慢性冲突等）。家庭环境的特殊地位仅限解释"遗传度"家族聚集（代际创伤链）。同步修正：转化接口.md §一/:113、本条目 D1、Q1 影响段（"必需土壤"扩展为固定生活环境层）、grilling-87.md 恢复记录。commit 见 `c6e5515` 后续修正提交。

**🔧 修正 (2026-09-01):** β 语义修正（来源：第五份外部评审 t_6a961e5824a48191a35d97c03d6edc04）——原「遗传 = 阈值调制 β」命名废弃（偷渡 β≡遗传 的未裁决因果判断），改为 **β = 个体易感性接口**：来源开放 ∈ {遗传、发育、既往经历、环境塑造、其他个体差异}，不裁决权重。「遗传度现象 = 家庭环境误读」→ 家族聚集 = 经验层现象，解释层立场 = 跨代环境传递（模型假说非事实等式），参数层 = β 接口（三层分离）。同步修正：转化接口.md §一/:51/:84/:113/:203、本条目 D1/D2/标题、term_registry（β 条目）、grilling-87.md R2。

**🔧 修正 (2026-09-01):** β(t) 化 + 韧性双机制（来源：第六/七份外部评审 t_6a96202214288191b46c878771b5d76a / t_6a9621ee23488191aa80e71f91ac5a5e）——① **β_i(t) = F(β₀,i, D_i(t))**：基线 × 发育调制，慢变量，经历不直接改 β（防 β/g/k/L 概念堆积 + 防自激反馈环）；② **四变量职责表**：β=基底易感性（事件不改）/ g=负荷放大 / k=应对缓冲 / L=累积；③ **k = 应对/缓冲系数**：保护因素（社会支持）作为 k 输入而非等价 k（防概念坍缩）；④ **韧性双机制**：累积期抵抗 = k（ΔI 缩放），恢复期 = #90 降档（ΔI_int < 0），不统一成单一韧性参数；⑤ **恢复 ≠ 遗忘**：ΔL_recovery 仅由 #90 治疗性改写提供，P_acc 衰减不降档。同步：转化接口.md（§一/§二/§3.1/§五/§六）、term_registry（β₀ 新增、β 条目更新）、grilling-87.md R2、六维状态条目。

---

---
*创建: 2026-09-12（由 design/decisions/ 拆分）| 更新: 2026-09-12*
*关联: [决策树总索引](README.md), [设计框架-六维状态](../framework/six-dimensions.md)*
