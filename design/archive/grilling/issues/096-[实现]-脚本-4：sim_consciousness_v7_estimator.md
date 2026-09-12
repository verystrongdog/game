# #96 [实现] 脚本 4：sim_consciousness_v7_estimator_validity.py（estimator-validity 实验）

> 状态：开放 · 创建 2026-08-27
> 标签：ready-for-agent
> 原始：https://github.com/verystrongdog/game/issues/96

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 任务
实现 Grilling [#95](https://github.com/verystrongdog/game/issues/95)（Q1-Q19 已冻结）的 estimator-validity 实验脚本 4：`sim_consciousness_v7_estimator_validity.py`。

## 设计依据（决策树 #95 条目 + .scratch/grilling-95-estimator-validity/grilling-95.md）

- **范围（Q1）**：全部十类 20 系统（rep+ctl），import `make_benchmark_systems()`（benchmark.py 零改动）
- **目标量（Q2/Q4）**：结构恢复 A_pair 主判 + 边级 P/R/F1 诊断 + CS′̂ 对照（exact-primitive replay）
- **估计器（Q3/Q9）**：plug-in 主（估计 P̂ 套用原 E_S^(1) 判定，逐边族 FWER≤0.01 + ∃ 聚合）+ 双变量 TE 对照（cs4 `transfer_entropy` + THETA_TE=0.01）
- **梯度（Q5）**：N={64,256,1024,4096,16384}、p_n={0,0.05,0.10,0.20}、d={1,2,4}、p_m={0,0.20,0.50}、h={0,1}、c={0.6,0.9}；阶段 A 六条单因素扫描（基线 N=1024,p_n=0,d=1,p_m=0,h=0,c=0.9，14 去重格）+ 阶段 B 预注册 R1-R4 选格局部全因子
- **统计（Q6/Q14/Q19）**：R=32、seed=hash(system,格,estimator,repeat)、bootstrap CI（repeat 重采样 B=1000）、条件/标签置换检验 α=0.01、边三值 present/absent/not_testable
- **轨迹（Q10/Q17/Q18）**：μ₀=Unif(Ω)、无 burn-in、逐轨迹独立、p_n→d→p_m→h、缺失不拼接、观测 Reacĥ 动态候选对（exact Reach 仅评估侧）
- **报告（Q15/Q16）**：三层报告、ΔA_pair 2×2 contrast、成立域汇总；输出 `data/sim_results/` 可追溯 JSON

## 验收（Q11，无失败线）

- 协议完整执行 + 结果完整报告 + seed 可复现
- 不引入 θ_valid；「发现 estimator 不成立」是有效结果
- 数值参数全部标注来源；复用铁律（不重复定义 cs4/components/benchmark 原语）
- 单文件函数式、中文注释（沿用 sim_consciousness_v7_* 惯例）

---

## 评论（2 条）

### verystrongdog · 2026-08-27

## 📌 scope 扩展（2026-08-27，Grilling #97）

**estimator 集合由 {plug-in, TE} 扩展为 {plug-in, TE, cTE}**——cTE 变体设计已冻结（[Grilling #97](https://github.com/verystrongdog/game/issues/97) Q1-Q6）：

- **cTE**（条件转移熵，全条件）：`cTE(X_i→X_j) = I(X_{i,t−1}; X_{j,t} | X_{∖{i},t−1})`，Z = 除 X_i 外全部变量 lag-1 过去，对齐 E_S^(1) 全状态条件语义
- **判定**：与 plug-in 同机制——保持时间结构的置换检验 + α=0.01 逐边族 FWER；**无硬阈值**；边状态三值化（present/absent/not_testable）
- **主目标**：A_pair 三估计器同格对比（全网格 20 系统 × 阶段 A/B）+ cTE 有向边 vs E_S^(1) 有向边方向一致性诊断（有向边级 P/R/F1，Q19 三值框架扩展方向维度）
- 协议全复用：#95 Q10/Q13/Q15/Q17/Q18 机械扩展，不新增阈值参数

其余 scope（#95 Q1-Q19）不变。实现时遵守 #95 Q11 约束：benchmark.py 零改动、import 复用 components 原语与 cs4 transfer_entropy、输出 data/sim_results/ 可追溯。

### verystrongdog · 2026-08-27

## ✅ 实现合同已冻结（Grilling #98，2026-08-28）

实现规划 Q0-Q14 全部定案（决策树 #98 条目 + [.scratch/grilling-96-estimator-validity-implement/grilling-96.md](https://github.com/verystrongdog/game/tree/main/.scratch/grilling-96-estimator-validity-implement/grilling-96.md)），本 issue 从 needs-triage 转 **ready-for-agent**。

### 实现合同要点（agent 必须遵守）

**铁律**：benchmark.py / components.py / cs4_test.py **零修改**；复用 estimator stack；三 estimator 判定函数完全独立；implementation 不重审 #95/#97 科学设计。

**范围**：单文件函数式中文注释 `sim_consciousness_v7_estimator_validity.py`，12 分区；estimator 集合 {plug-in, TE, cTE}。

**关键语义**：
- seed=hash(system, grid, estimator, repeat) 冻结（三估计器不共享轨迹，禁 common-random-number）
- c=0.6 格**全 blocked**（无冻结 coupling mapping）→ 阶段 A 13 executable 格 + 1 blocked、阶段 B 仅 N×p_n 与 d×p_m、c×h=not_computable
- exact truth 与 estimator 严格分叉；exact Reach 仅 coverage diagnostic
- A_pair 分母由 (system,h) 固定（与 Reacĥ_r 无关）；无 A_pair 阈值
- not_testable ≠ absent；无向三值化（present=任方向正证据/absent=双向 absent/其余=not_testable）
- d 是观测 delay 非 burn-in（禁 trajectory[d:]）
- plug-in: |ΔP̂| + B_perm=999 MC + α/m_ij 边内族 + ∃ 聚合 + 层级 RNG
- TE: cs4 transfer_entropy + THETA_TE=0.01；cTE: 全条件 log2 + 逐边单检验 α=0.01 无硬阈值
- 数据链：RepeatRecord=事实源 / aggregation=可重算缓存 / summary=可重建产物；MANIFEST=实验定义版本、schema_version=数据结构版本
- 执行：per-cell 独立即时落盘、可中断可恢复（终态仅 completed/blocked/failed）、job=(system,grid,estimator,repeat-range)、目标单机 ≤24h（超预算报告不偷改参数）、numpy 仅 cTE 统计内层（micro-benchmark 驱动 + cte_reference 回归锚）
- 验收：--self-test + dry-run D0/D1 + 完整验收（failed==0、repeat-range 拆分合并逐字节一致、依赖文件零修改）；**无失败线**（#95 Q11：协议完整+报告完整+seed 可复现）

**输出**：`data/sim_results/`（MANIFEST/run_log/selection_log/stageA/stageB/summary 三层报告：stageA_curves / stageB_interactions / validity_regions）。

---
*导出: 2026-09-12 | 来源: GitHub issue*
