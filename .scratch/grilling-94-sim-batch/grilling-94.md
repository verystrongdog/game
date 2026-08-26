# Grilling #94 — 模拟实现批次（v7 落地为可机检 sim）

> Issue: [#94](https://github.com/verystrongdog/game/issues/94) | 维度: 规则（纯学术研讨，不入游戏正典——#40/#93 先例）| 状态: 🔄 进行中 | 前置: v7 定稿 ✅ | 输入: 用户草案 + ChatGPT 分享链接（t_6a8f1aef54f4819180c2c3a424179ef3）

## 批次计划（用户草案，已确认顺序）

| 顺序 | 脚本 | 验证的 v7 定义 |
|---|---|---|
| 1 | `sim_consciousness_v7_components.py` | Reach R1 + E_S^(1) + 𝒞 + Diff(C) 轨迹熵 + Capacity + **四要件局部化** + Replication Invariance |
| 2 | `sim_consciousness_v7_rb_test.py` | R-B 内部因果穿透判别三角 F1/F8′/F9 + AgencyUse（do 干预） |
| 3 | `sim_consciousness_v7_benchmark.py` | B1 十类 paired 系统 + 双轨对照 + S1-S3 sanity |

## 决策记录（Step 3 逐题）

### Q1（2026-08-27）范围：脚本 1 = 完整 CS′_local(C) 版本 ✅ 定案

- **决策 D1**：选 (a) 完整版。脚本 1 实现完整 `CS′_local(C)`（Int_local/SB_local/SM_local/Diff(C) 四要件局部化），以完整分量级 CS′ = ⋁_{C∈𝒞(S)} CS′_local(C) 验证 Replication Invariance；**不允许 Diff-only 代理验收**（否则 Int/SB/SM 局部化在 S⊕S 下漂移会制造假阳性）。
- 依据：v7 §二 CS′(S)=⋁ CS′_local(C)；四要件局部化是脚本 2/3 共同地基，须在脚本 1 冻结语义（来源：issue #94 Q1 讨论 + ChatGPT 分享链接）。
- **验收分层输出**（ChatGPT 分享采纳）：Component decomposition（𝒞(S)/𝒞(S⊕S)/invariant）→ Per-component metrics（Diff/Capacity/Int_local/SB_local/SM_local）→ Local CS′ → System CS′ → Replication Invariance。失败可定位到层。
- **F8′ 构造归脚本 2**（cs4 F8 在 M/A 分配下 I=∅，M→I 恒假——脚本 2 决策点，不阻塞脚本 1）。

### Q2（2026-08-27）随机核精确化 ✅ 定案

- **决策 D2**：采用通用 `exact_kernel(step_fn, n)`——对每个 y∈Ω 枚举全部伯努利出向量 v∈{0,1}^K（K=单步最大 rng 调用数），模式 rng 驱动 step 函数，按**实际消费位串**确定路径事件（相同消费位串合并概率，未消费尾位不重复计数），路径概率 = ∏(p 或 1−p)。**禁止为 F1/F8/F9 手工维护第二套核定义**；P(y′|y) 必须是 step_fn 的唯一派生结果（来源：issue #94 Q2 + ChatGPT 分享 t_6a8f1ba3ce70819183ca289064517b6f）。
- **统一接口冻结**：`System = (name, n, step_fn(state, rng), M_set, A_set)`，三脚本共享；确定性系统同签名（step 忽略 rng，退化为 δ 核）。
- **n≤8 exact 轨范围声明**：脚本 1 不引入采样近似、无 Monte Carlo fallback；超出 exact 轨显式报错。

### Q3（2026-08-27）四要件局部化语义 ✅ 定案

- **决策 D3**：`SM_local(C) = RB_I(C) ∧ RB_A(C)`，v7 SM′ 全量语义 + do 干预原语在脚本 1 冻结；B（v6 SM 占位）否决——会让脚本 1 验证已废弃判据（来源：issue #94 Q3 + ChatGPT 分享 t_6a8f1c74bb58819197b0ed07b617b1d4）。
- 判定链：`CS′_local(C) = Int_local(C)>0 ∧ Diff(C)≥θ_D(3bit) ∧ SB_local(C) ∧ SM_local(C)`；`CS′(S)=⋁_{C∈𝒞(S)} CS′_local(C)`。
- RB_I（SelfRep R-B）= ∃m≠m′, k∈I∩C: `P_F(X′_k|do(M=m)) ≠ P_F(X′_k|do(M=m′))`；RB_A（SelfUse∧AgencyUse 合一）= 同上 k∈A∩C，Δ_A(M)>0 结构性条件。
- **do 干预语义**：单步硬干预 do(M_t=m)；权重 w(y|M=m) = 1/|{y∈Ω: y_M=m}| 条件均匀（不跟随 μ_t，跨基底）。
- **退化条款入原语**：M∩C=∅ → SM_local=0；A∩C=∅ → 仅 RB_I（A=∅ 退化条款，I=V∖M）。
- **局部化合法性**（decomposition invariant 断言）：无跨分量边 ⟹ 核因式分解 P_F(Y′|y)=∏_C P_F(Y′_C|y_C) ⟹ 每分量 C 为动力学封闭马尔可夫子系统；闭包检验可精确断言。
- Int_local(C) = v6 定义 min_{π∈Π₂(C)} E_μ[KL]，μ=稳态分布（幂迭代）；SB_local(C) = 复用 cs4 sel_broadcast 阈值常量，搜索域收窄 I₀,J⊆C。
- **脚本 2 不修改判定器**，只负责 F8′ 新构造 + 判别三角实测。

### Q4（2026-08-27）Diff(C) 的 T 取值 + 数值冻结表 ✅ 定案

- **决策 D4**：固定 T=64，`Diff(C) = (1/65)Σ_{t=0}^{64} H(μ_t^C)`（log2）。(ii) 混合判定否决——ε 成为塞进 Diff 的隐藏时间尺度自由度（撞 S2 精神）；(iii) T=2^n 否决（来源：issue #94 Q4 + ChatGPT 分享 t_6a8f1ce6060c81919afb3b5ade0e1e5e）。
- **诊断输出纳入验收**：H(μ_t^C) 全序列 + 稳态熵 H_C(∞)（幂迭代极限），**只诊断不参与 Diff 定义**（写死防替代）。
- **数值冻结表**（本批次全部实例化值，无新增 [NEW] 参数）：

| 项 | 冻结值 | 来源 |
|---|---|---|
| θ_D | 3 bit | v7 参数速查表 |
| Diff 熵底 | log2（bit）| θ_D 语义单位 |
| SB 阈值 | THETA_TE=0.01, THETA_SRC=0.5, THETA_F=0.5, THETA_C=0.3（cs4 :26-30）；θ_S=1.0, MIN_TARGETS=2, MIN_SOURCE_VALUES=3（v5_check :36-39）| 复用既有常量，从来源读取不复制 |
| Int 的 μ | 稳态分布（幂迭代）| v6 Layer 1 E_μ |
| μ₀ | Unif(Ω) | v7 §五 |
| T | 64 | 本问 D4 |

**脚本 1 参数面冻结。** 待继续追问：F8′ 构造（脚本 2 开工前）、B1 十类 paired 清单（脚本 3 开工前）。

### Q5（2026-08-27）F8′ 构造（升格为脚本 1 前置——Replication Invariance 1→1 半边需要正例）✅ 定案

- **决策 D5**：`F8′ = F8 + (z1,z2)` 内部寄存器，n=6；M={m1,m2}={2,3}、A={y1,y2}={0,1}、I={z1,z2}={4,5}。z′←m 跟随强度 0.9（沿用 F8 概率风格）。**z 不得反向影响 M/A**（新增机制只能是 M→I，禁止 M→I→A）。F8 原有动力学零改动（配对控制）。1 个 z 即足以使 RB_I 成立，2 个维持与 (m1,m2) 一一配对（来源：issue #94 Q5 + ChatGPT 分享 t_6a8f1df3a7348191a211100d4d137334）。
- **实现检查**：RB_I/RB_A 必须由 exact do-kernel 实测（P(z1′|do(m1=0)) vs P(z1′|do(m1=1)) 核计算），不得由构造直接赋值。
- **角色分工**：F8′ 承担 1→1 不稀释半边（CS′(F8′)=1；F8′⊕R 惰性模块=1）；F8 承担 0→0（复制不新增候选）；v5.3 四系统无 M/A → SM 退化条款 CS′=0，承担分量/熵/退化修复展示。
- **n≤8 预算注记**：F8⊕F8 n=8 在轨内；F8′⊕F8′ n=12 超轨 → 1→1 复制半边用 F8′⊕R（n=7，惰性常数模块 R，CS′(R)=0）覆盖等式断言。

### Q6（2026-08-27）实测发现：RB_A 对 XOR 型 M→A 失效（待用户裁决）

- **脚本 1 实测（sim_consciousness_v7_components.py）**：F8′ 的 M→A 为 XOR 型（y1′=y1^m1，来源 cs4 :241-249），v7 §六 AgencyUse 的边际 do 比较在另一输入均匀化后检测不到 XOR 依赖——实测 `P(y1′=1|do(m1=0)) = P(y1′=1|do(m1=1)) = 0.5` → RB_A=False → SM_local=False → CS′(F8′)=0 → Replication Invariance 1→1 半边（不稀释）阻塞。
- **对照原型**：F8′ 若 y1′=m1 直接依赖（0.6）→ `0.8 vs 0.2` → RB_A=True。XOR 失效确认为**定义级现象**（边际 do 比较的固有特性，非实现 bug）。
- **待裁决选项**：(a) F8′ 构造微调——M→A 改直接依赖（不动判定器；F8 保持 XOR 作自然负例）；(b) R-B 定义扩展为条件化 do（∃j 条件变量，引入选择自由度）；(c) 接受 RB_A=False → v7 判别三角 F8′ 行需重写。
- **脚本 1 已通过部分**：0→0 半边 ✅（CS′(F8⊕F8)=CS′(F8)=0，分量 1→2 复制稳定性，张量积核与直和枚举抽查一致）；v5.3 退化修复 ✅（S″ 逐分量 1bit、S‴ 分量 [[0,2],[1],[3]]、S* 1.015bit 全部拒）；闭包/因式分解断言全 ✓；F8′ Diff=5.438/Int=0.0668/SB=True/RB_I=True 全过（仅 RB_A 阻塞）。

### Q6 定案（2026-08-27）RB_A XOR 失效 → 构造微调（D6）✅

- **决策 D6**：只修改 F8′ 的 A 通道构造（XOR → 直接依赖 `ny1=m1 if 0.6`），z1,z2 与其余不动；**v7 §六判定器、RB_A 定义、do 原语全部保持不变**（来源：issue #94 Q6 + ChatGPT 分享 t_6a8f21983e0c819189ccbc71ba519b56）。
- (b) 否决：条件化 do 打开条件变量选择/多条件/条件分布/可比性一整套定义自由度；(c) 否决：F8′ 失去正例功能。
- **F8 保留 XOR 作自然负例**：存在结构上的 M→A XOR 依赖 ≠ 边际 AgencyUse do 检验可见——暴露 v7 RB_A 的检测边界而非缺陷。
- **脚本 1 验收全过（2026-08-27 实测）**：Replication Invariance 双边 ✅（0→0：F8⊕F8=0；1→1：F8′=1、F8′⊕R=1）；v5.3 退化修复 ✅；闭包/因式分解断言全 ✓；张量积核抽查 ✓。F8′ 最终：Diff=5.409/Int=0.0657/SB=True/SM=[RB_I=True,RB_A=True] → CS′=1。

## 下一步（脚本 2 前置）

- F1/F9 的 M/A 分配确认（cs4 :283-287 + v7 §六判别三角语义）
- 判别三角断言对象 = SM′（v7 §六末列 SelfRep=0/0/1），完整 CS′ 作对照

### Q7（2026-08-27）脚本 2 装载确认 ✅ 定案

- **决策 D7**：①F1: V={c0,c1,c2,j1,j2,fb}，M={3,4}，A=Y={0,1,2}（cs4 Y 语义，M→A ✗ 显式检验），I={5}；F9: V={s,m1,m2,a1,a2}，M={1,2}，A={3,4}，I={0}={s}（sensor 入 I）。②判别三角断言对象 = **SM′ = RB_I∧RB_A**（F1=0/F9=0/F8′=1，v7 §六末列；完整 CS′ 作对照输出，复测 v6 边界反例修复）。③脚本 2 复用脚本 1 原语（import，不重复定义）；F1/F9 step 按 cs4 做 bernoulli 语义等价改写。Y∖M→M 表征形成列为诊断（E_S^(1) 边 (i∈A∪I)→(j∈M) 检验），不进 SM′。

### Q8（2026-08-27）脚本 2 实测 ✅ 通过

- **判别三角全部通过（sim_consciousness_v7_rb_test.py）**：F1（Y∖M→M ✓/M→I ✗/M→A ✗，SM′=0，CS′=0）、F9（✓/✗/✓，SM′=0，CS′=0）、F8′（✓/✓/✓，SM′=1，CS′=1）——与 v7 §六表格逐格一致。
- **v6 边界反例修复实测确认**：F1 在 v6 记录 CS′=1（边界反例），v7 下 CS′=0——SM′ 重建的判别力成立；F9（状态估计+反馈控制）同样被排除。

### Q9（2026-08-27）B1 十类 paired 清单 ✅ 定案（D8）

- **决策 D8**：十类 = 负 4（#1 随机/#2 纯前馈/#3 数字电路/#4 通信网络）+ 正 3（#5 生物神经网络/#6 人脑数据/#7 自模型控制器）+ 判别 3（#8 反馈控制器/#9 细胞自动机/#10 RL 智能体）；每类 representative + 预期负控制，paired 只改声明目标机制（来源：issue #94 Q9 + ChatGPT 分享 t_6a8f233da3588191bec560b5eaf9a05d）。
- **「预期负控制」= 实验预期非验收定义**：不得为满足预期修改系统/判定器；意外成立记录为实验反例。
- **#6 synthetic observation 轨**（D9 A1）：报告估计值+不确定度+estimator validity，不触发 exact failure line。
- **#10 RL = 确定性有限系统实例化**：3-state/2-action 微 MDP，Q 表精确迭代，无采样训练。
- **Failure line**：F+ = ∃负类判 1；F− = ∀正类判 0（单个正类 0 不失败）；判别组不触发。
- **paired 分配冻结**：原则上保持 V/M/A/I 不变；目标机制要求改变分配 → 显式记录为结构性变化，不得称纯机制单变量对照（#7/#8 涉 I 尤其注意）。

### Q10（2026-08-27）无自然 M/A 系统的 M/A 实例化规则 ✅ 定案（D10）

- **决策 D10**：①M/A 是 benchmark 的**规范输入**（非从系统推断的事实语义）；三类分治：负类 #1-#4 M=∅/A=∅（SM′=0 是规范选择+退化条款结果，不解释成「证明无自模型结构」）；正类 #5-#7 按构造指南翻译给规范 M/A；判别组 #8-#10 按预先声明的结构规范选 M/A（不声称自然语义）（来源：issue #94 Q10 + ChatGPT 分享 t_6a8f23e1005c81919b662d257de2d8d5）。
- ②CA: M={格0}/A=∅（Rule30/Rule0 相同 M/A）；RL: M={状态}/A={动作}（保留天然状态→动作结构）。
- ③paired M/A 一致 + 预期非验收 = 硬约束；目标机制本身导致 I 变化 = 被测机制的结构变化（非 M/A 漂移）。
- **总原则**：类别标签/representative-control 标签/预期 CS′ 均不参与判定计算；判定器只读 step_fn + 预冻结 M/A。正类单样本 0 = 失败观测（不修改系统/阈值/M/A 救援），全 0 才 F−。

### Q11（2026-08-27）脚本 3 实测 ✅ 通过

- **B1 benchmark（sim_consciousness_v7_benchmark.py）全跑通，失败线未触发**：F+ 未触发（负类 8 系统全 0——高 Diff 系统如 F_fwd Diff_global=5.0 也因 SM 退化被拒）；F− 未触发（B_cpg=1 ✅、F8′=1 ✅；H_loop=0 为 observation 轨失败观测——分量分解显示为两个 2-回环，逐分量 Diff=2bit<θ_D，如实报告不救）。
- **判别组**（无失败线）：F9=0、F9_rep=1（反馈控制器+内部表征=1——画边界结果）；CA_Rule30=0（n=6 环 Diff=0.771bit 不足——规模限制）；CA_Rule0=0；RL_Q=0（微 MDP 收敛低熵 + M/A 占满 V→I=∅→SM 退化）；RL_rand=0。
- **Δ(Int,Diff,SB,SM) 表**：抑制性耦合 ΔSM=−1 ΔCS′=−1、M→I 内部穿透 ΔSM=−1 ΔCS′=−1、内部表征 I ΔSM=+1 ΔCS′=+1——SM′ 对目标机制敏感（v7 核心预测成立）。
- **S1/S2/S3 全 ✅**：S1 复制等式（F8′⊕F8′=1∨1=1）、S2 惰性模块（F8′⊕Z=1=1）、S3 真正耦合（B_cpg↔R 合并单分量+闭包+分解 ✓，CS′ 不预设方向）。
- **RL 编码注记**：2 位状态编码的非法态 s=3（μ₀=Unif 覆盖）重映射到 s=1（非法态行为明确，合法态动力学不变）。

## 约束清单（CLAUDE.md）

- 复用现有 sim 常量/函数（v5_check 四系统 + cs4 entropy/simulate/comp_trace/make_f1/f8/f9），不重复定义
- 数值参数全部标注来源；本批无新增 [NEW] 参数（μ₀=Unif、n≤8、θ_D=3bit 均已定）
- 单文件函数式、中文注释
- n≤8 精确枚举；n>8 采样近似（标注为估计，D 条款）
