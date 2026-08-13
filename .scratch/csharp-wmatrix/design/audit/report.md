# 审计报告: csharp-wmatrix spec v1.0

> 审计日期: 2026-08-13 | 审计方法: workflow 3 专家 agent（数学公式 / 架构契约 / 数据完整性）| spec版本: v1.0

## Trace Table

| # | spec位置 | 检查项 | 输入 | 判定 | 详情 |
|----|---------|--------|------|------|------|
| 1 | §六 AC-11 | 同 dk 内 fid 对计数 == 82 是否可由 graph_nodes 推导 | python 实测 fan-out 分布 {1:39, 2:7, 3:4, 4:1} | ❌ error（3/3 专家） | Σ_dk n(n−1) = **50**（无序对 25×2 方向）；82 = Σn²(活跃) 含 48 个对角单元格，与 AC-11 内「69 对角全 0」重复计数。按 AC 字面写测试必失败 |
| 2 | §六 AC-8 | τ 分布 27/29/11 与 mirror 继承后产物是否一致 | 按 Step 6 算法逐 fid 统计 | ❌ error（2/2 专家） | 原始字段 27/29/11 + mirror 2 属实；**继承后最终 Tau[69] = fast 27 / medium 30 / slow 12**（LC-Right→slow、SNc-Right→medium 各使 slow/medium +1）。AC 作为验收标准作用于最终产物，计数自相矛盾 |
| 3 | §一 B2 | 「Cerebellum-Cortex 参与 W（CC 40 + PP 51）」支撑数字 | 全量边独立实测 | ❌ error（1/3 专家） | 40/51 是 {Amygdala, Hippocampus, Cerebellum-Cortex} **三 dk 并集**的幸存口径（复算一致）；Cerebellum-Cortex 单节点幸存触边 = CC 6 / PP 12（原始 CC 16 / PP 12）。结论（不排除）正确，数字误挂 |
| 4 | §六 AC-7 | 锚点「按 fid 名经 RowFids 查索引」可执行性 | W_sensory rows 键 vs graph_nodes 键比对 | ⚠️ warning（3/3 专家） | 5 个锚点中 4 个是 **dk 名**（caudalanteriorcingulate→3 fids、transversetemporal、entorhinal、Hippocampus→2 fids），不在 RowFids 中，字面执行 KeyNotFound。锚点数值 5 个全部复算正确（relerr ≤ 1.2e-7） |
| 5 | §二 Step 4.3 | 「15 个歧义名……其 dk 恰为单 fid」事实性 | 15 个歧义名逐名核对 | ⚠️ warning（2/3 专家） | Caudate 的 dk 有 2 fids（Caudate + StriatumMatrix）。无副作用结论仍成立（Caudate ∈ CSTC 排除集，排除检查先于解析），但理由句为虚假数据声称 |
| 6 | §一 B1 | 延后修正清单是否覆盖全部同源冲突点 | 逐段 Read 两文档陈旧表述 | ⚠️ warning（1/3 专家） | 遗漏正典文档自身的 4 处：运行时状态模型 §4.1（方程作用域「category=cortical 且不在 CSTC 排除清单中」）、§4.5（「25 个 subcortical/brainstem 节点不参与 WC」）、参数速查表（「CC 节点数（排除后）~34 dk」——实测 35）；皮层动力学 §5.3（「CC 独有 6 节点」含已排除 Pallidum） |
| 7 | 任务issue 数据实测表 | 「CC-only 5 个（cuneus/…/transversetemporal）」口径 | CC/PP 端点差集实测 | ⚠️ warning（1/3 专家） | 全口径（无任何 PP 边）CC-only = 6 个（+Caudate/Pallidum/Putamen）；cuneus 与 transversetemporal **有** PP 边（全部触及排除 dk）。表中口径未声明。spec 未引用此行，不影响 spec 结论 |
| 8 | §二 Step 5 | 归一化公式引用段号 | Read 运行时状态模型原文 | ℹ️ info | 行归一化公式在 §4.3；§4.2 是排除清单（Step 3 引用正确）。公式本身逐字一致 |
| 9 | §六 AC-7 | 容差 1e-5 未声明绝对/相对 | numpy float32 独立重算 | ℹ️ info | float32 最大偏差 1.5e-7，1e-5 绝对容差余量 ~100×，合理；应显式声明绝对容差 + 依据 |
| 10 | §六 AC-4/6/8/11 | 数据漂移哨兵标注不统一 | — | ℹ️ info | 仅 AC-7 声明哨兵语义，建议全部数据依赖 AC 统一标注 |
| 11 | 变更日志 | 「13 条 AC」与 §六 实有 AC 数 | 逐条枚举 | ℹ️ info | 实际 12 条（AC-1…AC-12），多计 1 |
| 12 | §三 | 「Engine/ 目录新建」 | ls 目录 | ℹ️ info | 目录已存在（空），应为「内新建文件」 |

### 核查通过项（专家独立复算确认，无问题）

- **公式逐字对照全过**：w = edr×m×focus（§5.2）/ 归一化 +ε=0.01（§5.4 + 运行时 §4.3）/ τ 映射四档（§4.4）/ 自连接 0（§5.2）/ 特权通路入 W（§5.5）
- **B3 方向契约裁定正确**：皮层动力学 §5.1-5.2 首下标=源 与 运行时 §4.1 h_j=Σ_k W_jk·a_k（行=接收者）确为互转置；行=接收者使 plan §4.2 WcDynamics 矩阵向量积免转置成立
- **锚点值全部正确**：0.02277450 / 0 / 0.03620595 / 0.02819380 / 0.07386513（三专家独立重算，relerr ≤ 1.2e-7）
- **其余全部数值断言复验通过**：735 幸存对 / 1389 非零元 / 21 排除 fids / 16 dk（STN 双归属）/ 48 活跃行 ∈ (0,1) / edr [0.103,0.759] / 无孤岛 / 唯一非互惠对 / mirror 单层继承无递归 / 行序首键 AccumbensCore 双射
- **契约核对全过**：GameData/WsensoryMatrix/TripartiteModel/BrainRegion/FunctionProfile/Timescale?/MirrorOf/CalibrationConfig.MDefault==0.3f/WMatrix 构造全部存在且语义一致；csproj 无需改动；AC-10 合成 GameData 可行
- **决策固化全过**：D1-D8 各有落点；Q1/Q2 合规；结转 #5 → AC-2 落地；模板合规（一~七 + 变更日志 + footer + 目录 + 参数速查表）

## 缺口汇总

| # | 严重度 | 描述 |
|----|--------|------|
| F1 | ❌ error | AC-11 计数 82 错误，正确值 50（Σ_dk n(n−1)），按字面写测试必失败 |
| F2 | ❌ error | AC-8 计数作用于最终产物应为 27/30/12，29/11 只对 67 个非 mirror 原始字段成立 |
| F3 | ❌ error | B2 支撑数字误挂（并集口径当作单节点口径），「实测」标注失实 |
| F4 | ⚠️ warning | AC-7 锚点名 4/5 是 dk 名，测试方式按字面不可执行 |
| F5 | ⚠️ warning | Step 4.3 歧义名理由句对 Caudate 不成立 |
| F6 | ⚠️ warning | B1 延后修正清单遗漏正典文档 4 处同源陈旧表述 |
| F7 | ⚠️ warning | 任务issue 表「CC-only 5 个」口径未声明、与全口径实测不符 |
| F8-12 | ℹ️ info | 段号 §4.2→§4.3 / 容差声明 / 哨兵标注统一 / 变更日志 AC 数 / Engine 目录表述 |

## 审计结论

- [ ] 通过（无阻塞项）
- [ ] 有条件通过（⚠️ 项需人类确认）
- [x] **退回修改（❌ 项必须修复）**——3 个 error 均为 AC 可执行性与数据声称类缺陷，无公式错误、无设计级错误（方向契约 B3 裁定被三专家确认正确）。修复后升版 v1.1，走 Δ审计（变更章节 + 半径扩张复查）。

## 半径扩张

| 修复点 | 受影响消费者 | 复查状态 |
|--------|------------|---------|
| AC-11 计数 82→50 | §五 C5、§七自检清单数字 | 待 Δ审计 |
| AC-8 分布 27/30/12 | §二 Step 6 实测段 | 待 Δ审计 |
| B2 数字修正 | 任务issue D1/数据实测表（并集口径行保留为并集标注） | 待 Δ审计 |
| AC-7 命名粒度 | 测试实现方式（工作issue） | 待 Δ审计 |
| Step 4.3 理由句 | 任务issue D4 | 待 Δ审计 |
| B1 修正清单补全 | 审计后 L1 文档修正任务 | 待 Δ审计 |
| 任务issue「CC-only」行 | spec §一（「issue 表为本 spec 出处」声明） | 待 Δ审计 |
