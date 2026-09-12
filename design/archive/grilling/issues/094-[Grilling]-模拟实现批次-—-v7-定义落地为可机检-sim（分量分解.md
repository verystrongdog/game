# #94 [Grilling] 模拟实现批次 — v7 定义落地为可机检 sim（分量分解/Diff轨迹熵/R-B判别三角/benchmark）

> 状态：关闭 · 创建 2026-08-26 · 关闭 2026-08-26
> 标签：维度:规则, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/94

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题

**模拟实现批次**（#93 推迟清单首位）——把 v7 定稿的数学定义落成可机检 sim 脚本，逐项实测验证。纯学术研讨，不进游戏正典（同 #40/#93 先例）。

## 背景

`参考/意识结构侧-下一阶段路线-v7.md`（Grilling #93 定稿）已给出：分量级判定 CS′(S) = ⋁_{C∈𝒞(S)} CS′_local(C)（Replication Invariance）、Reach R1（§四）、E_S^(1) 一阶结构依赖边（§三）、弱连通分量 𝒞（§三）、Diff(C) 轨迹熵 + Capacity 诊断量（§五）、R-B 内部因果穿透判别三角 F1/F8′/F9（§六）、B1 benchmark 协议（§七）。决策树 :3163 记为「推迟——脚本实现时逐项验证」。

## 六维定位

- **维度**: 规则（纯学术研讨——#40/#93 先例；sim 脚本为验证工具）
- **依赖**: v7 定稿 ✅ + 现有 sim 资产（`sim_consciousness_v5_check.py` 四系统 S*₃/S*/S″/S‴ + `sim_consciousness_cs4_test.py` 的 entropy/simulate/comp_trace/make_f1/f8/f9 + M/Y 分量分配）
- **阻塞**: 无

## 批次计划（3 脚本，按依赖顺序）

| 顺序 | 脚本 | 验证的 v7 定义 | 复用现有资产 |
|---|---|---|---|
| 1 | `sim_consciousness_v7_components.py` | Reach R1（§四）+ E_S^(1) 边（§三）+ 弱连通分量 𝒞 + Diff(C) 轨迹熵（§五）+ Capacity 诊断量 | v5.3 四系统 + cs4 的 entropy/simulate/comp_trace |
| 2 | `sim_consciousness_v7_rb_test.py` | R-B 内部因果穿透（§六）——F1/F8′/F9 判别三角实测 + AgencyUse（do 干预） | cs4 的 make_f1/f8/f9 + M/Y 分量分配 |
| 3 | `sim_consciousness_v7_benchmark.py` | B1 十类 paired 系统（§七）+ 双轨对照（CS′_old vs CS′_new）+ S1-S3 sanity | 各 sim 阈值常量 + 新分量原语 |

## 关键实现决策（待逐题确认）

1. 随机核（rng 驱动 step 函数）如何精确化为 P(y′|y)——n≤8 精确枚举方式
2. CS′_local(C) 的四要件局部化语义（Int/SB/SM 如何在分量内判定）
3. F8′ 构造——cs4 的 F8（V={y1,y2,m1,m2}）在 M/A 分配下 I=∅，M→I 恒假，判别三角正例需新构造
4. do(M=m) 干预在随机核下的精确语义（脚本 2）
5. Diff(C) 的 T 取值与 μ_t 精确迭代（脚本 1）
6. 脚本 3 十类 paired 系统清单（n≤8 约束下 RL/CA 的实现形态）

## 当前状态

批次顺序与验收标准由用户给出草案：① Replication Invariance（CS′(S⊕S)=CS′(S)）② 判别三角 F1=0/F9=0/F8′=1 ③ S1-S3 sanity + Δ(Int,Diff,SB,SM) 随目标机制变化表。待逐题确认后按序实现。

## 工作方式

与 #93 相同——逐题追问（每轮一问），定义基线查询 term_registry（CS′/Int/Diff/SB/SM/Reach/因果分量/Replication Invariance/内部因果穿透/判别组/prior-positive 已入库），数值/公式标注来源。本批无新增 [NEW] 参数（μ₀=Unif、n≤8、θ_D=3bit 均已定）。

---

## 评论（2 条）

### verystrongdog · 2026-08-26

## ✅ Grilling #94 关闭总结（2026-08-27）

**模拟实现批次**——v7 定义落地为可机检 sim，三脚本全部验收通过。

### 决策表（D1-D7 + v7 D8/D9/D10 落地确认）

| # | 决策 | 要点 |
|---|---|---|
| D1 | 完整 CS′_local(C) | Replication Invariance 用完整判据断言（禁 Diff-only 代理）；验收分层输出 |
| D2 | exact_kernel 唯一派生核 | 逐位扩展枚举+消费位串去重；禁第二套手工核；System 统一接口；n≤8 exact 轨 |
| D3 | 四要件局部化 | CS′_local=Int>0∧Diff≥θ_D∧SB∧SM′；SM′=RB_I∧RB_A（do 条件均匀权重）；退化条款入原语；cut 核=块输入截断 |
| D4 | Diff 参数 | T=64 固定、log2；数值冻结表（θ_D=3bit、SB 阈值复用 cs4/v5_check、μ=稳态、μ₀=Unif） |
| D5 | F8′ 构造 | F8+(z1,z2) 内部寄存器；M→I 0.9；z 不反向影响 M/A；RB 必须 do-kernel 实测 |
| D6 | 🔧 闭合后修正 | F8′ A 通道 XOR→直接依赖（边际 do 对 XOR 型 M→A 数学上不可见，实测 0.5vs0.5）；判定器零改动；F8 保留 XOR 作自然负例 |
| D7 | 脚本 2 装载 | F1/F9 的 M/A 分配；判别三角断言对象=SM′ |
| v7 D8′ | 十类 3/4/3 | paired 机制对照；预期非验收；paired M/A 一致 |
| v7 D9 | 失败线 | F+=∃负类1、F−=∀sim 正类0；#6 observation 轨不触发 |
| v7 D10′ | M/A 规范输入 | 负类 M=∅；正类构造指南翻译；判别组结构规范；类别/预期不参与判定 |

### 实测结论（三脚本全过）

- **脚本 1** `sim_consciousness_v7_components.py`：Replication Invariance 双边 ✅（0→0：F8⊕F8=0 分量 1→2；1→1：F8′=1、F8′⊕R=1）；v5.3 full_reachable=Ω 退化修复 ✅；闭包/因式分解断言全 ✓
- **脚本 2** `sim_consciousness_v7_rb_test.py`：判别三角 F1=0/F9=0/F8′=1 全过——v6 边界反例（F1 旧判 1）被 SM′ 排除
- **脚本 3** `sim_consciousness_v7_benchmark.py`：失败线未触发；S1/S2/S3 全过；Δ 表显示 SM′ 对目标机制敏感（抑制性耦合/M→I ΔCS′=−1、内部表征 ΔCS′=+1）

### 受影响文件

- `sim_consciousness_v7_components.py` / `sim_consciousness_v7_rb_test.py` / `sim_consciousness_v7_benchmark.py`（新建）
- `docs/决策树.md`（#94 条目 + #93 推迟项标注「→ 见 #94」）
- `参考/意识结构侧-下一阶段路线-v7.md`（实现完成衔接注记）
- `.scratch/grilling-94-sim-batch/grilling-94.md`（决策日志 D1-D7 + D8′/D10′ + 验证表）
- memory：`意识结构侧模拟实现批次-grilling-94.md`

### 推迟清单

- #6 estimator-validity 完整实验（样本量/噪声/时间分辨率梯度）
- scaled observation 轨（n≫8 采样估计）
- SelfRep 充分定义 / E^(k) 超图（anomaly-triggered）/ 任务化 μ₀ / 连续域 Reach（v7 保留项）

### 质量门禁

- cross-ref grep：`y1^m1|XOR` 仅命中决策树新条目；`F8′` 活跃文档引用无断裂 ✅
- 产物完整性：三脚本 + 决策树 + 验证表 + memory + v7 衔接 ✓

### verystrongdog · 2026-08-27

## 📌 推迟项完成通知（2026-08-27）

本 issue 推迟清单首项「脚本 3 observation 轨深化（#6 estimator-validity 完整实验：样本量/噪声/时间分辨率/观测缺失梯度）」已由 [Grilling #95](https://github.com/verystrongdog/game/issues/95) 完成设计（Q1-Q19，2026-08-27）：

- estimator-validity 实验设计冻结：20 系统全覆盖、plug-in 主 + 双变量 TE 对照、A_pair 主判定（无 θ_valid）、六梯度分梯度扫描 + 预注册关键格全因子、R=32 + 逐边族条件置换检验、CS′̂ = Ĉ_obs 上 exact-primitive replay、scaled observation 轨独立推迟（前置 = 本批成立域结论）。
- 脚本 4 实现（`sim_consciousness_v7_estimator_validity.py`）另开 [issue #96](https://github.com/verystrongdog/game/issues/96)，benchmark.py 零改动。
- 决策树 #94 条目「推迟」项已加注 → 见 #95。

---
*导出: 2026-09-12 | 来源: GitHub issue*
