# #95 [Grilling] #6 estimator-validity 完整实验（observation 轨深化）

> 状态：关闭 · 创建 2026-08-27 · 关闭 2026-08-27
> 标签：维度:规则, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/95

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题
#94 推迟清单首位（决策树 :3206）：把脚本 3 的 observation 轨（#6 人脑数据 H_loop/H_linear）从「exact 轨报告 CS′」深化为完整的 **estimator-validity 实验**——`F_known → 𝒞_exact → synthetic trajectory → Ĉ_obs`，测 `Ĉ_obs ≈ 𝒞_exact` 何时成立。

输入来源：用户分享的 ChatGPT 收尾总结链接（t_6a8fc7d8…，与 #94 记录逐条核对一致，无新决策），其中明确建议「把 #94 当作稳定基线，然后进入推迟项中最靠前的 #6 estimator-validity」。

## 六维定位
- 维度：**规则**（纯学术研讨，不入游戏正典——#40/#93/#94 先例）
- 依赖：v7 §三 D 条款（TE/cTE 降为观测估计器）+ §五（Diff 与 Diff̂ 分离）+ §七 D9/D10（observation 轨协议：报告估计值+不确定度+estimator validity，不触发失败线）+ #94 三脚本（原语复用）
- 阻塞：scaled observation 轨（n≫8 采样估计）——estimator 有效性是 n≫8 轨的前提

## 当前状态
- v7 协议已冻结（D9 A1 / D10 H1），缺的是**实验设计 + 实现**：
  - 现有 benchmark.py 对 H_loop/H_linear 仍走 exact 轨（evaluate() 直接算 CS′），只是标注「observation 轨、不触发失败线」——**synthetic observation 管线尚未实现**
  - v6 开放问题 #5「TE ≠ 因果」已在 v7 §七 H1 重构为可测试问题，本 grilling 即落地该测试
- 待 grill 决策点（预计）：范围（仅 #6 还是全十类）、估计器选择（TE/cTE 阈值）、有效性判定准则（Ĉ_obs≈𝒞 的误差度量：边集/分量划分/CS′ 裁决）、梯度参数（样本量/噪声/时间分辨率/观测缺失/隐变量/耦合强度）取值、报告格式（估计值+不确定度）

## 输出预期
- 决策写入：`docs/决策树.md` 新条目（#95）+ `参考/意识结构侧-下一阶段路线-v7.md` 衔接注记 + 新脚本（或脚本 3 扩展）+ 决策日志 `.scratch/grilling-95-estimator-validity/`

---

## 评论（2 条）

### verystrongdog · 2026-08-27

## ✅ Grilling #95 关闭总结（2026-08-27）

### 决策表（Q1-Q19）

| Q | 决策 |
|---|---|
| Q1 | 全部十类 20 系统（rep+ctl） |
| Q2 | 目标量 = 结构恢复（Ĉ_obs ≈ 𝒞_exact）；CS′̂ 对照列 |
| Q3 | plug-in 主估计 + TE/cTE 对照（实测 v6 #5） |
| Q4 | A_pair 主判 + P/R/F1 诊断 + CS′̂ 对照；无 θ_valid |
| Q5 | 六梯度取值冻结；阶段 A 单因素扫描 + 阶段 B 关键格全因子 |
| Q6 | R=32 + 确定性 seed + repeat 重采样 bootstrap CI + 条件/标签置换检验 α=0.01 |
| Q7 | CS′̂ = Ĉ_obs 上 exact-primitive replay；无 SM̂ 观测近似 |
| Q8 | scaled 轨独立推迟；本批产出可复用 estimator stack |
| Q9 | 仅双变量 TE（cs4 复用 + THETA_TE=0.01）；cTE 推迟 |
| Q10 | μ₀=Unif(Ω) + 无 burn-in + 逐轨迹独立估计 |
| Q11 | 新脚本 4，benchmark.py 零改动；无失败线 |
| Q12 | 预注册 R1-R4 选格；0.15 为选格阈值非有效性阈值 |
| Q13 | h=1 预注册机制相关隐变量 + component-connectivity projection truth |
| Q14 | 逐边检验族 FWER≤0.01 + ∃ 聚合 |
| Q15 | 三层报告 + 预注册三交互（N×p_n / d×p_m / c×h） |
| Q16 | 14 去重格 + clamp/去重 ±1 + 局部全因子 + 2×2 contrast |
| Q17 | p_n→d→p_m→h 顺序 + 缺失不拼接 |
| Q18 | 观测 Reacĥ 逐 repeat 动态候选对；exact Reach 仅评估侧 |
| Q19 | 边三值 present/absent/not_testable；P/R/F1 排除 not-testable；A_pair 保守图 |

### 受影响文件

- `docs/决策树.md` #95 条目
- `参考/意识结构侧-下一阶段路线-v7.md`（衔接注记 + 参数速查表补充）
- `.scratch/grilling-95-estimator-validity/grilling-95.md`（决策日志 + 写入验证表）
- `data/term_registry.json`（6 术语入库：estimator-validity/Ĉ_obs/A_pair/synthetic observation 轨/not_testable/scaled observation 轨）
- memory（`estimator-validity-grilling-95.md`）

### 质量门禁

- 写入验证表：Q1-Q19 逐条对照 ✅（见 grilling-95.md）
- 一致性清扫：grep 新术语/新参数命中均为本批新增，无旧文档冲突、无路径断裂、无垃圾桶移动 ✅
- 新参数标注 [NEW] #95：选格阈值 0.15、统计层 α=0.01、R=32

### 推迟清单

- **脚本 4 实现** → [issue #96](https://github.com/verystrongdog/game/issues/96)（设计冻结，实现待排期）
- scaled observation 轨（n≫8，前置 = 本批成立域结论）
- cTE 变体（条件集未冻结）/ 全观测估计版 CS′̂（撞 TE≠因果）
- SelfRep 充分定义 / E^(k)超图 / 任务化 μ₀ / 连续域 Reach（保留）

### verystrongdog · 2026-08-27

## 🔧 闭合后修正 (2026-08-27)

| 原决策 | 修正后 | 根因 |
|---|---|---|
| Q9：cTE 不进本批（条件集未冻结=新自由度，作后续独立变体推迟）| cTE 变体设计已冻结（[Grilling #97](https://github.com/verystrongdog/game/issues/97) Q1-Q6：全条件 `cTE(X_i→X_j)=I(X_{i,t−1};X_{j,t}|X_{∖{i},t−1})`、置换检验无硬阈值、A_pair 三估计器同格、有向边级 P/R/F1），**实现并入脚本 4（#96，estimator 集合 {plug-in, TE, cTE}）** | ①#97 Q1 已冻结条件集（Z=V∖{X_i} 全条件，由结构决定）——原推迟理由（条件集未冻结=新自由度）已解决；②#95 Q8「不得重设计/复制 estimator stack」支持并入而非另开脚本；③#96 尚未实现，scope 扩展零返工 |

修正不影响 #95 其余 Q1-Q19 决策。决策树 #95 条目已加修正行，v7 文档 §七已加「cTE 变体（Grilling #97）」小节。

---
*导出: 2026-09-12 | 来源: GitHub issue*
