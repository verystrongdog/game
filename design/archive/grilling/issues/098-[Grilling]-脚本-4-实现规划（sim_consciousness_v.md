# #98 [Grilling] 脚本 4 实现规划（sim_consciousness_v7_estimator_validity.py，前置 #96）

> 状态：关闭 · 创建 2026-08-27 · 关闭 2026-08-27
> 标签：维度:管线, needs-triage, grilling
> 原始：https://github.com/verystrongdog/game/issues/98

> **归档**：grilling 流程已停用，本文是只读历史记录。

---

## 正文

## 话题
Grilling #96（实现 issue）的实现规划——把冻结设计（#95 Q1-Q19 estimator-validity + #97 Q1-Q6 cTE 扩展，estimator 集合 {plug-in, TE, cTE}）落成可运行的 `sim_consciousness_v7_estimator_validity.py`（脚本 4）。implementation grilling，不重审科学设计。

## 六维定位
维度：管线（怎么造出来、怎么验证）。纯学术研讨产物，不入游戏正典（#40/#93/#94/#95/#97 先例，六维状态不更新）。

## 当前状态
- #95（✅ 2026-08-27）：estimator-validity 设计冻结 Q1-Q19（A_pair 主判、plug-in 主估计、六梯度阶段 A/B、R=32、置换检验、exact-primitive replay、not_testable 三值化）
- #97（✅ 2026-08-27）：cTE 变体冻结 Q1-Q6（全条件、无硬阈值、有向边 P/R/F1），实现并入 #96
- #96（OPEN，needs-triage）：实现 issue，设计已冻结，待实现排期
- 复用原语：sim_consciousness_v7_components.py（System/evaluate/exact_kernel/edges_e1/weak_components/do_dist 等）、sim_consciousness_v7_benchmark.py（make_benchmark_systems，**零改动**）、cs4 transfer_entropy/THETA_TE

## 铁律
1. `sim_consciousness_v7_benchmark.py` 零改动
2. 复用既有 estimator stack，不借实现之名重新设计 estimator
3. 发现需要重议 cTE 统计定义 → 标记设计越界，不在 #96 偷改

## 流程（Q0-Q14，逐题追问）
Q0 边界定案（2026-08-28，输入 ChatGPT 分享 t_6a9015fb…）→ Q1 职责边界 → Q2 数据流 → Q3 原语映射 → Q4 观测/exact 数据结构 → Q5 estimator stack → Q6 单 repeat schema → Q7 R=32/seed → Q8 阶段 A → Q9 阶段 B → Q10 统计汇总 → Q11 计算预算 → Q12 序列化 → Q13 验收 → Q14 异常/断点 → 决策树条目 + grilling 日志 + #96 issue body + ready-for-agent

---

## 评论（1 条）

### verystrongdog · 2026-08-27

## ✅ Grilling #96 实现规划完成（Q0-Q14 冻结，2026-08-28）

### 决策表（Q0-Q14 要点）

| 题 | 裁决 |
|---|---|
| Q0 边界 | implementation grilling（不重审 #95/#97 科学设计）；Q1-Q14 先锁数据语义再锁计算工程 |
| Q1 职责 | 拥有 9 项 / 不拥有 8 项；estimator branch 与 ground-truth branch 严格分叉；12 分区单文件 |
| Q2 生命周期 | 单单元 8 步；seed 含 estimator → 三估计器不共享轨迹（禁 common-random-number）|
| Q2a c 实例化 | ScaleRNG/比例式否决；**c=0.6 全 blocked**（无冻结 mapping）；c 机制层另开设计轮 |
| Q3 原语映射 | 依赖文件全只读；CS′̂ projection 内联；numpy 留 Q11；evaluate() 不复用 |
| Q4 plug-in | |ΔP̂| + B_perm=999 + α/m_ij 边内族 + ∃ 聚合 + 层级 RNG；禁过滤已定义 condition pair |
| Q5 TE/cTE | TE=硬阈值 0.01；cTE=全条件 log2 逐边单检验 α=0.01；三判定函数完全独立 |
| Q6 schema | EdgeResult/RepeatRecord；完整落盘；blocked 元记录；truth 存边集 |
| Q7 A_pair | 任方向正证据；truth=全图弱连通；**分母由 (system,h) 固定**；无阈值 |
| Q8 P/R/F1 | 有向 truth=E_S^(1)∩(V_obs²)；无向三值化；cTE 有向主判 |
| Q9 Stage A | 14 审计格（13 executable+1 blocked）；h 表预注册冻结；d=delay 非 burn-in |
| Q10 Stage B | 确定性纯函数选格+trigger_log；R2 仅 plug vs TE；c×h=not_computable；H/L 机械端点 |
| Q11 计算 | per-cell 即时落盘；numpy 仅 cTE 内层（benchmark 驱动）；目标 ≤24h；可恢复 |
| Q12 序列化 | RepeatRecord=事实源/aggregation=缓存/summary=产物；MANIFEST vs schema_version 分离 |
| Q13 验收 | --self-test + D0/D1 + 完整验收（failed==0、拆分合并一致、依赖零修改）；无失败线 |
| Q14 异常 | cell 级异常整 cell failed；partial 不续跑；终态仅 completed/blocked/failed |

### 受影响文件

- `docs/决策树.md`：#98 条目 + #95/#97 推迟项「→ 见 #98」标注
- `.scratch/grilling-96-estimator-validity-implement/grilling-96.md`：决策日志 + 写入验证表
- GitHub #96：issue body 附实现合同，needs-triage → ready-for-agent
- memory：`script4-estimator-validity-implementation-grilling-96.md`
- term_registry：无新增（实现规划；D0/D1/cell_id 等实现层标识符不入库）

### 写入验证（质量门禁）

- 决策树条目 ✅ / 日志+验证表 ✅ / #96 合同+标签 ✅ / memory ✅ / registry 检查 ✅
- 一致性清扫：grep `estimator-validity|脚本 4|blocked` 无旧文档冲突；无垃圾桶移动；term_registry 无定义变更 ✅
- 封板：12 个越界点全堵死（详见日志）

### 推迟

- 脚本 4 实现执行 → #96 ready-for-agent
- c 梯度机制层冻结映射 → 另开设计轮
- scaled observation 轨 → 维持阻塞（前置 = 脚本 4 成立域结论）

---
*导出: 2026-09-12 | 来源: GitHub issue*
